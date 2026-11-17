# -*- coding: utf-8 -*-
"""PAW TX API v3 — AI nâng cấp + JSON gọn.
Endpoints: /tx/hu  /tx/md5  /history/tx/hu  /history/tx/md5  /ping  /admin
Env: ADMIN_PASS (bắt buộc), ADMIN_USER (mặc định: admin), SECRET_KEY,
     API_URL_HU, API_URL_MD5, STATE_FILE, DISABLED_TABLES
Start: gunicorn app:app --workers 1 --threads 4 --timeout 30
"""
import hmac, json, math, os, secrets, threading, time
from collections import deque, Counter
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import requests
from flask import Flask, jsonify, make_response, redirect, request, session
from werkzeug.exceptions import HTTPException

# ── Cấu hình ──────────────────────────────────────────────────────────────────
URLS  = {"hu":  os.getenv("API_URL_HU",  "https://wtx.tele68.com/v1/tx/sessions"),
         "md5": os.getenv("API_URL_MD5", "https://wtxmd52.tele68.com/v1/txmd5/sessions")}
NAMES = {"hu": "Hũ", "md5": "MD5"}

WINDOW    = 50    # cửa sổ lịch sử
HIST_MAX  = 50
POLL_SEC  = 4
MIN_GAP   = 3
STALE_SEC = 8

# ── Học ───────────────────────────────────────────────────────────────────────
LEARN_WIN      = 30     # CỬA SỔ HỌC TỐI ĐA: chỉ 30 phiên gần nhất quyết định
HALF_LIFE      = 12     # phiên cũ hơn 12 → trọng số còn 50% (phiên 30 ≈ 18%)
PRIOR_STRENGTH = 2.5    # prior xúc xắc đều, tính bằng "phiên tương đương"

ICON       = {"win": "✅", "lose": "❌", "cho": "⏳"}
VN         = timezone(timedelta(hours=7))
STATE_FILE = os.getenv("STATE_FILE", "/tmp/paw_tx_toggles.json")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8)
)
app.json.ensure_ascii = False
app.json.sort_keys    = False

# ── CORS + lỗi JSON ────────────────────────────────────────────────────────────
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-Requested-With"
    resp.headers["Access-Control-Max-Age"]        = "86400"
    if not request.path.startswith("/admin"):
        resp.headers["Cache-Control"] = "no-store"
    return resp

@app.errorhandler(Exception)
def on_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    msg  = e.description if isinstance(e, HTTPException) else "Lỗi máy chủ"
    return jsonify({"ok": False, "loi": "http_%d" % code, "thong_bao": msg}), code

def out(payload, status=200):
    if request.args.get("pretty"):
        r = make_response(json.dumps(payload, ensure_ascii=False, indent=2), status)
        r.headers["Content-Type"] = "application/json; charset=utf-8"
        return r
    return jsonify(payload), status

# ── HTTP client ────────────────────────────────────────────────────────────────
_http = requests.Session()
_http.headers.update({"User-Agent": "Mozilla/5.0 (PAW-TX/3)", "Accept": "application/json"})

def parse_sessions(data):
    rows = data.get("list") if isinstance(data, dict) else data
    got  = {}
    for it in rows or []:
        try:
            sid = int(it["id"])
            raw_dices = it.get("dices") or []
            dices = [int(x) for x in raw_dices[:3]] if isinstance(raw_dices, (list, tuple)) else []
            dice_ok = len(dices) == 3 and all(1 <= x <= 6 for x in dices)
            if dice_ok:
                # Tổng 3 viên là nguồn chuẩn; không để trường point sai lệch dữ liệu học.
                point = sum(dices)
            else:
                if "point" not in it:
                    continue
                point = int(it["point"])
                if not 3 <= point <= 18:
                    continue
                dices = []
            # Chuẩn hóa đúng luật người dùng: tổng >= 11 là TÀI, còn lại XỈU.
            res = "TAI" if point >= 11 else "XIU"
            got[sid] = {"id": sid, "dices": dices, "point": point, "result": res}
        except (KeyError, TypeError, ValueError):
            continue
    return [got[k] for k in sorted(got)]

def fetch_sessions(url):
    r = _http.get(url, timeout=(3, 7)); r.raise_for_status()
    return parse_sessions(r.json())

FETCH = fetch_sessions

# ══════════════════════════════════════════════════════════════════════════════
#  BỘ HỌC TỔNG ĐIỂM — dùng dữ liệu 30 phiên gần nhất
#  Không dùng các expert dựa trên chuỗi TÀI/XỈU cũ.
# ══════════════════════════════════════════════════════════════════════════════
def _logit(p):
    p = min(0.9499, max(0.0501, p))
    return math.log(p / (1 - p))

def _sig(z):
    return 1.0 / (1.0 + math.exp(-max(-15, min(15, z))))

def _shrink(p, k):
    """Kéo p về 0.5 theo độ dày dữ liệu k∈[0,1]."""
    k = max(0.0, min(1.0, k))
    return 0.5 + (p - 0.5) * k

def _dice_sum_prior():
    """Phân phối lý thuyết tổng 3 xúc xắc đều (3..18) — prior, không phải kết luận."""
    c = Counter()
    for a in range(1, 7):
        for b in range(1, 7):
            for d in range(1, 7):
                c[a + b + d] += 1
    return {s: c[s] / 216.0 for s in range(3, 19)}

_PT_PRIOR = _dice_sum_prior()
_PT_BASE  = sum(v for s, v in _PT_PRIOR.items() if s >= 11)   # ≈ 0.4861

def _pt_bucket(p):
    if p is None:
        return None
    if p <= 9:
        return "L"      # 3..9  — thiên Xỉu
    if p <= 11:
        return "M"      # 10..11 — vùng biên
    return "H"          # 12..18 — thiên Tài


class PointLearner:
    """Học từ chuỗi TỔNG ĐIỂM 3 viên. Cửa sổ tối đa LEARN_WIN phiên (decay)."""

    def __init__(self):
        self.decay   = 0.5 ** (1.0 / HALF_LIFE)
        self.hist    = {s: 0.0 for s in range(3, 19)}          # tổng -> trọng số
        self.cond    = {b: {s: 0.0 for s in range(3, 19)} for b in "LMH"}  # tổng kế tiếp | nhóm tổng trước
        self.cond_n  = {b: 0.0 for b in "LMH"}
        self.trans   = {b: [0.0, 0.0] for b in "LMH"}          # [tai, xiu] kế tiếp | nhóm tổng trước
        self.run     = {}                                      # độ dài bệt -> [tai, xiu]
        self.hist_n  = 0.0
        self.prev_pt = None
        self.last_side = None
        self.run_len = 0
        self.n = 0

    def _decay_all(self):
        d = self.decay
        for s in self.hist:
            self.hist[s] *= d
        for b in "LMH":
            for s in self.cond[b]:
                self.cond[b][s] *= d
            self.cond_n[b] *= d
            self.trans[b][0] *= d
            self.trans[b][1] *= d
        for k in list(self.run):
            self.run[k][0] *= d
            self.run[k][1] *= d
        self.hist_n *= d

    def observe(self, point, side):
        """side = 'TAI'/'XIU' của chính phiên có tổng `point` này."""
        try:
            point = int(point)
        except (TypeError, ValueError):
            return
        if point < 3 or point > 18:
            return
        self._decay_all()

        self.hist[point] += 1.0
        self.hist_n += 1.0

        # tổng kế tiếp phụ thuộc nhóm tổng trước
        if self.prev_pt is not None:
            b = _pt_bucket(self.prev_pt)
            self.cond[b][point] += 1.0
            self.cond_n[b] += 1.0
            self.trans[b][0 if side == "TAI" else 1] += 1.0

        # bệt: kết quả kế tiếp phụ thuộc độ dài bệt hiện tại
        rl = min(self.run_len, 6)
        cell = self.run.setdefault(rl, [0.0, 0.0])
        cell[0 if side == "TAI" else 1] += 1.0

        if self.last_side is None or side != self.last_side:
            self.run_len = 1
        else:
            self.run_len += 1
        self.last_side = side
        self.prev_pt = point
        self.n += 1

    # ── xuất tín hiệu ────────────────────────────────────────────────────────
    def _post(self, counts, prior_scale):
        tot = tai = 0.0
        for s in range(3, 19):
            v = counts[s] + prior_scale * _PT_PRIOR[s]
            tot += v
            if s >= 11:
                tai += v
        return (tai / tot) if tot > 0 else _PT_BASE

    def experts(self):
        """4 module tự học — đều trả P(TAI). Dữ liệu mỏng → kéo mạnh về 0.5."""
        out = {"pt_hist": 0.5, "pt_cond": 0.5, "pt_trans": 0.5, "pt_run": 0.5}
        if self.n < 3:
            return out
        # độ dày: 3 phiên → gần như im, 30 phiên → nói hết
        k = min(1.0, self.hist_n / float(LEARN_WIN)) ** 0.6

        out["pt_hist"] = _shrink(self._post(self.hist, PRIOR_STRENGTH), k)

        b = _pt_bucket(self.prev_pt)
        if b is not None:
            # điều kiện theo nhóm tổng trước — cần đủ mẫu trong ô mới dám nói
            kc = k * min(1.0, self.cond_n[b] / 8.0)
            out["pt_cond"] = _shrink(self._post(self.cond[b], PRIOR_STRENGTH * 0.5), kc)

            t = self.trans[b]; tc = t[0] + t[1]
            kt = k * min(1.0, tc / 6.0)
            p_t = (t[0] + 3.0 * _PT_BASE) / (tc + 3.0)
            out["pt_trans"] = _shrink(p_t, kt)

        if self.last_side is not None:
            rl = min(self.run_len, 6)
            cell = self.run.get(rl, [0.0, 0.0]); c = cell[0] + cell[1]
            kr = k * min(1.0, c / 4.0)
            p_r = (cell[0] + 2.0 * 0.5) / (c + 2.0)
            out["pt_run"] = _shrink(p_r, kr)
        return out

    def summary(self):
        b = _pt_bucket(self.prev_pt)
        return {
            "so_phien":     round(self.hist_n, 1),
            "tong_truoc":   self.prev_pt,
            "nhom":         b,
            "bệt":          self.run_len,
            "p_tai_diem":   round(self._post(self.hist, PRIOR_STRENGTH), 3),
            "p_tai_nhom":   round(self._post(self.cond[b], PRIOR_STRENGTH * 0.5), 3) if b else None,
        }


class Brain:
    """AI học trực tiếp từ tối đa 30 phiên gần nhất và tổng điểm 3 viên.

    Không dùng bộ dự đoán Markov/Trend/Run cũ. Bốn tín hiệu đều lấy từ
    PointLearner: phân bố tổng điểm, tổng điểm có điều kiện, chuyển tiếp
    theo nhóm tổng trước và kết quả theo độ dài bệt. Trọng số được học
    walk-forward bằng log-loss trên kết quả thực tế.
    """
    NAMES = ("pt_hist", "pt_cond", "pt_trans", "pt_run")
    LEARNED = NAMES
    N = len(NAMES)

    def __init__(self):
        self.r = deque(maxlen=LEARN_WIN)
        self.pt = deque(maxlen=LEARN_WIN)
        self.pl = PointLearner()
        self.losses = {k: deque(maxlen=LEARN_WIN) for k in self.NAMES}
        self.w = {k: 1.0 / self.N for k in self.NAMES}
        self.hit = deque(maxlen=LEARN_WIN)
        self.t = 0
        self.temp = 1.0
        self.cap = 0.0

    @staticmethod
    def _clip(p):
        return min(0.95, max(0.05, float(p)))

    @staticmethod
    def _loss(p, y):
        p = min(0.98, max(0.02, float(p)))
        return -math.log(p if y else 1.0 - p)

    def _update_weights(self):
        # Chỉ dựa trên sai số thực tế của 30 phiên đã được xác nhận.
        scores = {}
        for k in self.NAMES:
            vals = list(self.losses[k])
            scores[k] = (sum(vals) / len(vals)) if vals else 0.0
        base = min(scores.values())
        raw = {k: math.exp(max(-12.0, -(scores[k] - base) * 1.25)) for k in self.NAMES}
        total = sum(raw.values()) or 1.0
        # Floor nhỏ để AI luôn tiếp tục kiểm tra lại các tín hiệu khác.
        floor = 0.08
        self.w = {k: (1.0 - floor) * raw[k] / total + floor / self.N for k in self.NAMES}

    def _reset_learning(self):
        # Giữ nguyên lịch sử 30 phiên; chỉ xóa đánh giá trọng số đã học.
        self.losses = {k: deque(maxlen=LEARN_WIN) for k in self.NAMES}
        self.w = {k: 1.0 / self.N for k in self.NAMES}
        self.hit.clear()
        self.temp = 1.0

    def predict(self):
        ex = self.pl.experts()
        # Kết hợp xác suất của các mô-đun học từ tổng điểm, không thêm
        # một cửa dự đoán mặc định hoặc expert dựa trên chuỗi nhị phân cũ.
        z = sum(self.w[k] * _logit(self._clip(ex[k])) for k in self.NAMES)
        p = _sig(z)
        side = "TAI" if p >= 0.5 else "XIU"
        conf = round(max(p, 1.0 - p) * 100)
        acc30 = (sum(self.hit) / len(self.hit)) if self.hit else None
        pl = self.pl.summary()
        return {
            "p": p, "z": z, "ze": z, "ex": dict(ex),
            "ex_short": dict(ex), "ex_long": dict(ex),
            "p_short": p, "p_long": p,
            "side": side, "conf": conf, "skip": False,
            "w": dict(self.w), "w_short": dict(self.w),
            "w_long": dict(self.w), "meta_w": {"point_learning": 1.0},
            "temp": round(self.temp, 3), "ramp": 1.0,
            "governor": 1.0, "entropy": None,
            "acc30": round(acc30, 3) if acc30 is not None else None,
            "nhom": {
                "loss_tu_hoc": round(sum((sum(v) / len(v)) for v in self.losses.values() if v) / max(1, sum(1 for v in self.losses.values() if v)), 3) if any(self.losses.values()) else None,
                "loss_thuat_toan": None,
                "tran": self.cap,
            },
            "pl": pl,
        }

    def learn(self, pk, y: bool):
        """Học trọng số từ dự đoán đã chốt; gọi trước observe()."""
        y = bool(y)
        ex = pk.get("ex") or {}
        for k in self.NAMES:
            self.losses[k].append(self._loss(ex.get(k, 0.5), y))
        self._update_weights()
        hit = 1 if ((pk.get("side") == "TAI") == y) else 0
        self.hit.append(hit)
        self.t += 1

    def observe(self, row):
        """Đưa kết quả và tổng điểm 3 viên đã xác nhận vào bộ nhớ 30 phiên."""
        if not isinstance(row, dict):
            return
        res = row.get("result")
        point = row.get("point")
        try:
            point = int(point)
        except (TypeError, ValueError):
            point = None
        if point is not None and not 3 <= point <= 18:
            point = None
        if res not in ("TAI", "XIU"):
            if point is None:
                return
            res = "TAI" if point >= 11 else "XIU"
        self.r.append(1 if res == "TAI" else 0)
        if point is not None:
            self.pt.append(point)
        self.pl.observe(point, res)

# ── Replay & entry ─────────────────────────────────────────────────────────────
def entry(row, pk, win, live):
    return {
        "phien":     row["id"],
        "du_doan":   pk["side"],
        "ket_qua":   row["result"],
        "xuc_xac":   row["dices"],
        "tong":      row["point"],
        "trang_thai": "win" if win else "lose",
        "icon":      ICON["win" if win else "lose"],
        "live":      live,
    }

def replay(rows, newest_first=False):
    """Nạp tối đa 30 phiên mới nhất, học walk-forward và khôi phục lịch sử."""
    rows = list(rows or [])
    if newest_first:
        rows.reverse()
    rows = rows[-LEARN_WIN:]
    b = Brain()
    hist = deque(maxlen=HIST_MAX)
    # Phiên đầu chỉ tạo dữ liệu nền; các phiên sau được dự đoán bằng
    # trạng thái AI trước khi biết kết quả, tránh rò rỉ dữ liệu tương lai.
    if rows:
        b.observe(rows[0])
    for row in rows[1:]:
        pk = b.predict()
        actual = row.get("result") == "TAI"
        win = pk["side"] == row.get("result")
        b.learn(pk, actual)
        hist.append(entry(row, pk, win, False))
        b.observe(row)
    return b, hist

# ── Trạng thái từng bàn ────────────────────────────────────────────────────────
class Table:
    def __init__(self, code):
        self.code = code; self.name = NAMES[code]; self.url = URLS[code]
        self.enabled = True; self.lock = threading.Lock(); self.reset()

    def reset(self):
        self.ready = False; self.brain = None
        self.hist  = deque(maxlen=HIST_MAX); self.last = None; self.pending = None
        self.last_id = 0; self.fetch_ts = 0.0; self.ok_ts = 0.0
        self.err = ""; self.ms = 0; self.n_fetch = 0

    def refresh(self, force=False, block=True, rebuild=False):
        if not self.lock.acquire(blocking=block): return
        try:
            if not force and self.ready and time.time() - self.fetch_ts < MIN_GAP: return
            self.fetch_ts = time.time(); t0 = time.time()
            try:    rows = FETCH(self.url)
            except Exception as e:
                self.err = "%s: %s" % (type(e).__name__, str(e)[:120]); return
            if not rows: self.err = "Upstream trả danh sách rỗng"; return
            self.ms = int((time.time() - t0) * 1000); self.err = ""
            self.ok_ts = time.time(); self.n_fetch += 1
            self.apply(rows, rebuild)
        finally:
            self.lock.release()

    def apply(self, rows, rebuild=False):
        newest = rows[-1]["id"]
        if rebuild or not self.ready or newest < self.last_id or rows[0]["id"] > self.last_id + 1:
            self.brain, self.hist = replay(rows)
            # last = thông tin phiên mới nhất từ raw data (chưa có dự đoán live)
            self.last = {
                "phien": newest, "xuc_xac": rows[-1]["dices"],
                "tong": rows[-1]["point"], "ket_qua": rows[-1]["result"],
                "du_doan": None, "trang_thai": "khong",
            }
            self.last_id = newest; self.ready = True; self._pend(); return

        for row in (r for r in rows if r["id"] > self.last_id):
            pd = self.pending
            # Nếu poll bị trễ và API trả về nhiều phiên cùng lúc, vẫn phải
            # chấm/học từng phiên theo thứ tự, không bỏ qua các phiên ở giữa.
            is_live = bool(pd and pd["phien"] == row["id"])
            pk = pd["pk"] if is_live else self.brain.predict()
            du = pk["side"]
            win = du == row["result"]
            self.brain.learn(pk, row["result"] == "TAI")
            self.hist.append(entry(row, pk, win, is_live))
            self.brain.observe(row)  # cập nhật điểm sau khi chấm dự đoán
            self.last = {
                "phien": row["id"], "xuc_xac": row["dices"],
                "tong": row["point"], "ket_qua": row["result"],
                "du_doan": du, "trang_thai": "win" if win else "lose",
            }
            self.last_id = row["id"]; self.pending = None
        self._pend()

    def _pend(self):
        pk = self.brain.predict()
        self.pending = {
            "phien":    self.last_id + 1,
            "du_doan":  pk["side"],
            "do_tin_cay": pk["conf"],
            "p_tai":    round(pk["p"], 3),
            "pk":       pk,
        }

TABLES = {c: Table(c) for c in URLS}

# ── Helpers thống kê ───────────────────────────────────────────────────────────
def stats(items):
    w = sum(1 for h in items if h["trang_thai"] == "win")
    l = len(items) - w
    return {"win": w, "lose": l, "ty_le": round(w * 100.0 / len(items), 1) if items else 0.0}

def now_iso():
    return datetime.now(VN).replace(microsecond=0).isoformat()

# ── View JSON ─────────────────────────────────────────────────────────────────
def view_main(t):
    last = t.last; pd = t.pending
    items = list(t.hist)
    if items and last and items[-1]["phien"] == last["phien"]:
        items = items[:-1]

    phien_truoc = {
        "phien":      last["phien"],
        "xuc_xac":    last["xuc_xac"],
        "tong":       last["tong"],
        "ket_qua":    last["ket_qua"],
        "du_doan":    last["du_doan"],
        "trang_thai": last["trang_thai"],
        "icon":       ICON.get(last["trang_thai"], ""),
    }
    phien_hien_tai = {
        "phien":      pd["phien"],
        "du_doan":    pd["du_doan"],
        "do_tin_cay": pd["do_tin_cay"],
        "icon":       ICON["cho"],
    }
    lich_su = [
        {
            "phien":      h["phien"],
            "du_doan":    h["du_doan"],
            "ket_qua":    h["ket_qua"],
            "trang_thai": h["trang_thai"],
            "icon":       h["icon"],
        }
        for h in items[-5:][::-1]
    ]

    res = {
        "ok":           True,
        "ban":          t.name,
        "phien_truoc":  phien_truoc,
        "phien_hien_tai": phien_hien_tai,
        "lich_su":      lich_su,
        "thong_ke":     stats(list(t.hist)),
        "cap_nhat":     now_iso(),
    }
    if t.err: res["canh_bao"] = "Nguồn dữ liệu lỗi, đang dùng dữ liệu gần nhất"

    # ── Bộ não đang học được gì (chỉ đọc, không đổi logic cũ) ─────────────────
    if pd and pd.get("pk"):
        pkd = pd["pk"]; pl = pkd.get("pl") or {}; nh = pkd.get("nhom") or {}
        res["tu_hoc"] = {
            "cua_so":          LEARN_WIN,
            "so_phien":        pl.get("so_phien"),
            "tong_truoc":      pl.get("tong_truoc"),
            "nhom_tong":       pl.get("nhom"),
            "bet":             pl.get("bệt"),
            "p_tai_tu_diem":   pl.get("p_tai_diem"),
            "p_tai_theo_nhom": pl.get("p_tai_nhom"),
            "acc30":           pkd.get("acc30"),
            "loss_tu_hoc":     nh.get("loss_tu_hoc"),
            "loss_thuat_toan": nh.get("loss_thuat_toan"),
            "trong_so_tu_hoc": round(sum(v for k, v in (pkd.get("w") or {}).items()
                                        if k in Brain.LEARNED), 3),
            "governor":        pkd.get("governor"),
        }
    return res

def view_history(t, limit):
    items = list(t.hist)[::-1][:limit]
    return {
        "ok":       True,
        "ban":      t.name,
        "tong":     len(items),
        "thong_ke": stats(list(t.hist)),
        "cap_nhat": now_iso(),
        "lich_su":  [
            {
                "phien":      h["phien"],
                "du_doan":    h["du_doan"],
                "ket_qua":    h["ket_qua"],
                "xuc_xac":    h["xuc_xac"],
                "tong":       h["tong"],
                "trang_thai": h["trang_thai"],
                "icon":       h["icon"],
                "live":       h["live"],
            }
            for h in items
        ],
    }

# ── Background poller ──────────────────────────────────────────────────────────
def load_toggles():
    off = {x.strip() for x in os.getenv("DISABLED_TABLES", "").split(",") if x.strip()}
    try:    saved = json.load(open(STATE_FILE))
    except: saved = {}
    for c, t in TABLES.items(): t.enabled = bool(saved.get(c, c not in off))

def save_toggles():
    try: json.dump({c: t.enabled for c, t in TABLES.items()}, open(STATE_FILE, "w"))
    except: pass

load_toggles()
_poller = {"on": False}; _plock = threading.Lock()

def _loop():
    while True:
        for t in TABLES.values():
            if t.enabled:
                try: t.refresh()
                except: pass
        time.sleep(POLL_SEC)

@app.before_request
def start_poller():
    if not _poller["on"]:
        with _plock:
            if not _poller["on"]:
                _poller["on"] = True
                threading.Thread(target=_loop, daemon=True).start()

def table_or_error(code):
    t = TABLES.get(code)
    if not t:
        return None, out({"ok": False, "loi": "not_found", "thong_bao": "Dùng hu hoặc md5"}, 404)
    if not t.enabled:
        return None, out({"ok": False, "loi": "table_off",  "thong_bao": "Bàn %s đang tắt" % t.name}, 503)
    if not t.ready: t.refresh()
    elif time.time() - t.fetch_ts > STALE_SEC:
        threading.Thread(target=t.refresh, kwargs={"block": False}, daemon=True).start()
    if not t.ready:
        return None, out({"ok": False, "loi": "upstream_error",
                          "thong_bao": "Chưa lấy được dữ liệu, thử lại sau vài giây",
                          "chi_tiet": t.err}, 503)
    return t, None

# ── API endpoints ──────────────────────────────────────────────────────────────
@app.get("/tx/<code>")
def api_main(code):
    t, err = table_or_error(code); return err or out(view_main(t))

@app.get("/history/tx/<code>")
def api_history(code):
    t, err = table_or_error(code)
    if err: return err
    try:    limit = max(1, min(HIST_MAX, int(request.args.get("limit", HIST_MAX))))
    except: limit = HIST_MAX
    return out(view_history(t, limit))

@app.get("/ping")
def ping(): return out({"ok": True, "t": now_iso()})

@app.get("/")
def index():
    return out({"ok": True, "api": "PAW TX v3",
                "endpoints": ["/tx/hu", "/tx/md5", "/history/tx/hu", "/history/tx/md5", "/admin", "/ping"]})

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN — UI hiện đại, light/dark, thống kê đầy đủ
# ══════════════════════════════════════════════════════════════════════════════
_fails: dict = {}

def authed():
    return bool(session.get("adm")) and session.get("adm_until", 0) > time.time()

def guard():
    if not authed(): return out({"ok": False, "loi": "unauthorized"}, 401)
    if request.method == "POST" and not hmac.compare_digest(
            request.headers.get("X-CSRF-Token", ""), session.get("csrf", "x")):
        return out({"ok": False, "loi": "csrf"}, 403)

def table_dump(t):
    pd   = t.pending; hist = list(t.hist)
    # live = phiên có flag live=True; nếu không có thì lấy 5 phiên gần nhất làm live proxy
    live_real = [h for h in hist if h.get("live")]
    live = live_real if live_real else hist[-5:]
    l30 = hist[-30:]
    ex   = [{"name": k, "p": round(pd["pk"]["ex"][k], 3), "w": round(pd["pk"]["w"][k], 3)}
            for k in Brain.NAMES] if pd else []
    return {
        "code": t.code, "name": t.name, "enabled": t.enabled, "ready": t.ready,
        "err": t.err, "ms": t.ms, "n_fetch": t.n_fetch,
        "age":  round(time.time() - t.ok_ts) if t.ok_ts else None,
        "last": t.last,
        "pending": {
            "phien":   pd["phien"],   "du_doan": pd["du_doan"],
            "conf":    pd["do_tin_cay"], "p_tai": pd["p_tai"],
            "temp":    pd["pk"]["temp"],
        } if pd else None,
        "experts":  ex,
        "st_all":   stats(hist),
        "st_live":  stats(live),
        "st_30":    stats(l30),
        "hist":     hist[::-1],
    }

@app.get("/admin/data")
def admin_data():
    g = guard(); return g or out({"ok": True, "tables": [table_dump(t) for t in TABLES.values()]})

@app.post("/admin/act/<code>/<act>")
def admin_act(code, act):
    g = guard()
    if g: return g
    t = TABLES.get(code)
    if not t or act not in ("on", "off", "refresh", "relearn"):
        return out({"ok": False, "loi": "bad_request"}, 400)
    if act in ("on", "off"):
        t.enabled = act == "on"; save_toggles()
    elif act == "refresh": t.refresh(force=True)
    else:                  t.refresh(force=True, rebuild=True)
    return out({"ok": True, "enabled": t.enabled, "err": t.err})

# ── Login page ─────────────────────────────────────────────────────────────────
LOGIN = """<!doctype html>
<html lang=vi><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name=theme-color content="#080d1b"><title>PAW TX · Secure Login</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}body{min-height:100vh;display:grid;place-items:center;padding:20px;background:radial-gradient(ellipse at 15% 0%,rgba(37,99,235,.24),transparent 40%),radial-gradient(ellipse at 90% 90%,rgba(124,58,237,.2),transparent 38%),#080d1b;color:#edf3ff;font:13px/1.6 Inter,system-ui,sans-serif}.login{width:min(420px,100%);padding:34px;border:1px solid rgba(148,163,184,.18);border-radius:22px;background:linear-gradient(145deg,rgba(20,32,55,.97),rgba(10,17,32,.98));box-shadow:0 28px 90px rgba(0,0,0,.45);position:relative;overflow:hidden}.login:before{content:'';position:absolute;inset:0 0 auto;height:2px;background:linear-gradient(90deg,#2563eb,#22d3ee,#8b5cf6)}.mark{width:58px;height:58px;margin:0 auto 20px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(145deg,#2563eb,#7c3aed);box-shadow:0 12px 32px rgba(79,70,229,.35);animation:float 3s ease-in-out infinite}.mark svg{width:34px;height:34px}.eyebrow{text-align:center;color:#67e8f9;font-size:9px;font-weight:800;letter-spacing:.2em;margin-bottom:8px}h1{text-align:center;font-size:25px;letter-spacing:-.05em;font-weight:900}.sub{text-align:center;color:#91a1bd;font-size:11px;margin:7px 0 26px}label{display:block;color:#a8b6cc;font-size:9px;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin:0 0 7px}input{width:100%;height:46px;margin:0 0 17px;padding:0 13px;border:1px solid rgba(148,163,184,.2);border-radius:11px;background:#0b1426;color:#edf3ff;font:13px Inter;outline:none;transition:.18s}input:focus{border-color:#60a5fa;box-shadow:0 0 0 3px rgba(59,130,246,.15)}button{width:100%;height:46px;border:0;border-radius:11px;background:linear-gradient(105deg,#2563eb,#5b4be8);color:#fff;font:800 12px Inter;cursor:pointer;box-shadow:0 8px 24px rgba(37,99,235,.24);transition:.18s}button:hover{filter:brightness(1.12);transform:translateY(-1px)}button:active{transform:scale(.99)}.err{margin:0 0 16px;padding:10px 12px;border-radius:10px;border:1px solid rgba(251,113,133,.25);background:rgba(251,113,133,.1);color:#fda4af;font-size:11px}.foot{margin-top:20px;text-align:center;color:#64748b;font-size:10px}.foot span{color:#91a1bd}@keyframes float{50%{transform:translateY(-5px)}}@media(max-width:480px){.login{padding:27px 22px;border-radius:18px}}
</style></head><body><main class=login><div class=mark><svg viewBox="0 0 40 40" fill=none><path d="M20 3S32 16 32 24a12 12 0 1 1-24 0C8 16 20 3 20 3Z" fill=white/><path d="M14 22c1.2-3.2 2.8-5.8 4.7-8" stroke="#93c5fd" stroke-width=2.5 stroke-linecap=round/></svg></div><div class=eyebrow>SECURE ADMIN ACCESS</div><h1>PAW TX Admin</h1><div class=sub>Đăng nhập để truy cập Control Center</div>__ERR__<form method=post action=/admin/login><label for=username>Tài khoản quản trị</label><input id=username name=username value=admin autocomplete=username required><label for=password>Mật khẩu</label><input id=password type=password name=password autocomplete=current-password autofocus required><button type=submit>ĐĂNG NHẬP HỆ THỐNG&nbsp; →</button></form><div class=foot><span>Phiên bảo mật 8 giờ</span> · PAW TX CONTROL CENTER</div></main></body></html>"""

# ── Admin SPA ──────────────────────────────────────────────────────────────────
PAGE = r"""<!doctype html>
<html lang=vi>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name=theme-color content="#080d1b">
<title>PAW TX · Control Center</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
:root{color-scheme:dark;--bg:#080d1b;--bg2:#0d1426;--panel:#111b30;--panel2:#15213a;--line:rgba(148,163,184,.15);--line2:rgba(99,102,241,.35);--txt:#edf3ff;--muted:#91a1bd;--dim:#64748b;--blue:#60a5fa;--cyan:#22d3ee;--violet:#8b5cf6;--green:#34d399;--red:#fb7185;--amber:#fbbf24;--shadow:0 18px 50px rgba(0,0,0,.25)}
*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth;background:var(--bg)}body{min-height:100vh;color:var(--txt);font:13px/1.6 Inter,system-ui,sans-serif;background:radial-gradient(ellipse at 12% -10%,rgba(37,99,235,.18),transparent 35%),radial-gradient(ellipse at 95% 12%,rgba(124,58,237,.13),transparent 28%),var(--bg);-webkit-font-smoothing:antialiased}a{color:inherit;text-decoration:none}button{font:inherit}.mono{font-family:'JetBrains Mono',monospace;font-size:11px;font-variant-numeric:tabular-nums}
.wrap{max-width:1480px;margin:auto;padding:0 28px}.topbar{height:72px;position:sticky;top:0;z-index:50;background:rgba(8,13,27,.82);backdrop-filter:blur(20px);border-bottom:1px solid var(--line)}.tinner{height:100%;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{display:flex;align-items:center;gap:12px;font-size:15px;font-weight:900;letter-spacing:-.04em}.brand-mark{width:38px;height:38px;border-radius:13px;display:grid;place-items:center;background:linear-gradient(145deg,#2563eb,#7c3aed);box-shadow:0 8px 24px rgba(79,70,229,.35)}.brand-mark svg{width:23px;height:23px}.brand small{display:block;color:var(--muted);font-size:9px;letter-spacing:.17em;font-weight:700;margin-top:-2px}.tbright{display:flex;align-items:center;gap:14px}.tick,.count-wrap{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:11px}.tick-dot,.live-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 0 4px rgba(52,211,153,.12);animation:pulse 2s infinite}.count-wrap{padding:7px 10px;border:1px solid var(--line);border-radius:9px;background:rgba(255,255,255,.025)}#countdown{font-family:'JetBrains Mono',monospace;color:var(--cyan);font-weight:700}.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:9px 13px;border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.04);color:#c7d4eb;font:700 11px Inter;white-space:nowrap;cursor:pointer;transition:.18s}.btn:hover{border-color:rgba(96,165,250,.6);background:rgba(59,130,246,.12);color:#fff;transform:translateY(-1px)}.btn:active{transform:scale(.97)}.btn-blue{background:linear-gradient(110deg,#2563eb,#4f46e5);border-color:transparent;color:white;box-shadow:0 6px 18px rgba(37,99,235,.2)}.btn-blue:hover{background:linear-gradient(110deg,#3b82f6,#6366f1);color:white}.btn-sm{padding:7px 10px;font-size:10px;border-radius:8px}
main{padding:30px 0 52px}.page-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:22px}.eyebrow{display:flex;align-items:center;gap:8px;color:var(--cyan);font-size:9px;font-weight:800;letter-spacing:.19em;text-transform:uppercase;margin-bottom:8px}.eyebrow:before{content:'';width:18px;height:1px;background:var(--cyan)}h1{font-size:clamp(23px,3vw,32px);font-weight:900;letter-spacing:-.055em;line-height:1.12}.page-desc{color:var(--muted);font-size:12px;margin-top:8px}.head-tag{display:flex;align-items:center;gap:8px;padding:9px 12px;border:1px solid var(--line);border-radius:12px;background:rgba(17,27,48,.7);color:var(--muted);font-size:10px}.head-tag strong{color:var(--txt)}.navstrip{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}.navstrip a{padding:8px 12px;border:1px solid var(--line);border-radius:9px;color:var(--muted);font-size:10px;font-weight:700;background:rgba(255,255,255,.025);transition:.18s}.navstrip a:hover{color:#fff;border-color:var(--line2);background:rgba(99,102,241,.1)}
.g2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.card{min-width:0;padding:20px;border:1px solid var(--line);border-radius:17px;background:linear-gradient(145deg,rgba(20,32,55,.96),rgba(13,21,39,.96));box-shadow:var(--shadow);position:relative;overflow:hidden;transition:border-color .2s,transform .2s}.card:hover{border-color:rgba(96,165,250,.32);transform:translateY(-2px)}.card:before{content:'';position:absolute;inset:0 0 auto;height:1px;background:linear-gradient(90deg,transparent,rgba(96,165,250,.45),transparent);pointer-events:none}.row{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:7px 0}.row+.row{border-top:1px solid var(--line)}.flex{display:flex;align-items:center;gap:8px;min-width:0}.muted{color:var(--muted)}.small{font-size:10px}.hdot{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}.hdot.ok{background:var(--green);box-shadow:0 0 0 4px rgba(52,211,153,.12);animation:pulse 2s infinite}.hdot.warn{background:var(--amber)}.hdot.bad{background:var(--red);box-shadow:0 0 0 4px rgba(251,113,133,.12)}.sw{width:42px;height:24px;border-radius:20px;background:#334155;position:relative;cursor:pointer;border:1px solid rgba(255,255,255,.08);flex-shrink:0;transition:.2s}.sw:after{content:'';position:absolute;top:3px;left:3px;width:16px;height:16px;border-radius:50%;background:#e2e8f0;transition:.2s}.sw.on{background:#059669}.sw.on:after{left:21px;background:white}
.pred-banner{margin-top:13px;border:1px solid rgba(129,140,248,.25);border-radius:14px;padding:20px;background:radial-gradient(ellipse at 90% 0%,rgba(124,58,237,.22),transparent 45%),linear-gradient(120deg,#142b54,#1b2450 60%,#25204b);position:relative;overflow:hidden}.pred-banner:after{content:'';position:absolute;width:180px;height:180px;border:1px solid rgba(255,255,255,.06);border-radius:50%;right:-55px;top:-80px;box-shadow:0 0 0 22px rgba(255,255,255,.018),0 0 0 46px rgba(255,255,255,.014)}.pbinner{position:relative;z-index:1}.pb-label,.pb-prev-label{font-size:9px;font-weight:800;letter-spacing:.15em;color:#9eb6df;text-transform:uppercase;margin-bottom:7px}.pb-side{font-size:clamp(30px,4vw,42px);font-weight:900;letter-spacing:-.06em;line-height:1}.pb-conf{font-size:12px;font-weight:700;color:#e0eaff;margin-top:7px}.pb-meta{font:10px 'JetBrains Mono',monospace;color:#9fb1d0;margin-top:5px}.pb-right{text-align:right;min-width:145px}.chips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:13px}.chip{padding:12px 10px;border:1px solid var(--line);border-radius:12px;background:rgba(5,10,22,.25);text-align:left}.chip-val{font-size:21px;font-weight:900;letter-spacing:-.05em;line-height:1.15;margin-bottom:4px;font-variant-numeric:tabular-nums}.chip-lbl{font-size:9px;color:var(--muted);font-weight:800;letter-spacing:.1em;text-transform:uppercase}.chip-val.green{color:var(--green)}.chip-val.red{color:var(--red)}.chip-val.blue{color:var(--cyan)}.badge{display:inline-flex;align-items:center;padding:4px 9px;border-radius:7px;font-size:9px;font-weight:900;border:1px solid;white-space:nowrap;letter-spacing:.04em}.TAI{background:rgba(251,113,133,.12);color:#fda4af;border-color:rgba(251,113,133,.28)}.XIU{background:rgba(34,211,238,.1);color:#67e8f9;border-color:rgba(34,211,238,.25)}.win{background:rgba(52,211,153,.1);color:#6ee7b7;border-color:rgba(52,211,153,.22)}.lose{background:rgba(251,113,133,.1);color:#fda4af;border-color:rgba(251,113,133,.22)}.neutral{background:rgba(148,163,184,.1);color:#cbd5e1;border-color:var(--line)}.ex-row{display:grid;grid-template-columns:110px minmax(40px,1fr) 64px;align-items:center;gap:9px;padding:5px 0}.ex-name{font-size:10px;font-weight:700;color:#b7c5dc;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.prog{height:5px;background:rgba(148,163,184,.14);border-radius:8px;overflow:hidden;min-width:0}.prog i{display:block;height:100%;border-radius:8px;transition:width .3s}.section{padding-top:28px;scroll-margin-top:88px}.sec-head{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;flex-wrap:wrap;margin-bottom:13px}.sec-title{font-size:15px;font-weight:850;letter-spacing:-.035em}.sec-sub{font-size:10px;color:var(--muted);margin-top:4px}.tbl-scroll{overflow:auto;border:1px solid var(--line);border-radius:13px;background:rgba(17,27,48,.65)}table{width:100%;border-collapse:separate;border-spacing:0;white-space:nowrap}thead{position:sticky;top:0;z-index:2}th{padding:11px 14px;background:#17243b;color:#8395b3;border-bottom:1px solid var(--line);text-align:left;font-size:9px;font-weight:800;letter-spacing:.13em;text-transform:uppercase}td{padding:11px 14px;color:#bdc9dc;font-size:11px;border-bottom:1px solid rgba(148,163,184,.08);background:rgba(14,23,41,.7)}tbody tr:hover td{background:rgba(59,130,246,.08)}tbody tr:last-child td{border-bottom:0}.live-badge{display:inline-flex;align-items:center;gap:6px;font-size:9px;font-weight:800;padding:4px 8px;border-radius:20px;background:rgba(251,113,133,.1);border:1px solid rgba(251,113,133,.2);color:#fda4af}.live-dot{width:5px;height:5px;background:var(--red);box-shadow:none}.err-box{margin-top:12px;padding:10px 12px;border-radius:10px;background:rgba(251,113,133,.1);border:1px solid rgba(251,113,133,.22);color:#fda4af;font-size:11px}.sep{height:1px;background:linear-gradient(90deg,transparent,var(--line),transparent);margin-top:26px}#toast{position:fixed;right:22px;bottom:22px;z-index:9999;display:none;min-width:240px;max-width:calc(100vw - 32px);padding:13px 16px;border:1px solid var(--line);border-left:3px solid var(--green);border-radius:12px;background:#15213a;color:#eaf2ff;box-shadow:var(--shadow);font-size:12px;animation:rise .2s ease}.footnote{color:var(--dim);font-size:9px;text-align:center;padding:24px 0 0;letter-spacing:.08em;text-transform:uppercase}
@keyframes pulse{50%{box-shadow:0 0 0 7px transparent}}@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:900px){.wrap{padding:0 18px}.g2{grid-template-columns:1fr}.page-head{align-items:flex-start}.head-tag{display:none}}
@media(max-width:560px){.wrap{padding:0 12px}.topbar{height:60px}.brand{font-size:13px}.brand-mark{width:34px;height:34px}.tbright{gap:7px}.tick{font-size:0}.tick-dot{width:8px;height:8px}.count-wrap{font-size:9px;padding:6px 7px}.tbright>.btn{padding:8px;font-size:0}.tbright>.btn:after{content:'Thoát';font-size:10px}.page-head{margin-bottom:16px}main{padding-top:22px}.card{padding:15px;border-radius:14px}.pred-banner{padding:16px}.pbinner{flex-direction:column;align-items:flex-start}.pb-right{text-align:left;width:100%;min-width:0;border-top:1px solid rgba(255,255,255,.1);padding-top:11px}.pb-right>div{justify-content:flex-start!important}.chips{gap:6px}.chip{padding:10px 8px}.chip-val{font-size:18px}.chip-lbl{font-size:8px}.ex-row{grid-template-columns:88px minmax(30px,1fr) 55px;gap:6px}.ex-name{font-size:9px}.sec-head{align-items:flex-start}.sec-head>.flex{flex-wrap:wrap}.tbl-scroll{margin:0 -2px}th,td{padding:10px 11px}.section{padding-top:22px}#toast{right:12px;bottom:12px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.01ms!important;animation-iteration-count:1!important;scroll-behavior:auto!important;transition-duration:.01ms!important}}
</style>
</head>
<body>
<header class=topbar><div class="wrap tinner">
  <div class=brand><span class=brand-mark><svg viewBox="0 0 28 28" fill=none><path d="M14 2.5S22.5 12 22.5 17.5a8.5 8.5 0 1 1-17 0C5.5 12 14 2.5 14 2.5Z" fill="white"/><path d="M10 15.5c.8-2.2 2-4.2 3.3-5.8" stroke="#93c5fd" stroke-width=2 stroke-linecap=round/></svg></span><span>PAW TX<small>ADMIN CONTROL CENTER</small></span></div>
  <div class=tbright><div class=tick><span class=tick-dot></span><span id=tickLbl>Đang kết nối…</span></div><div class=count-wrap>Đồng bộ <span id=countdown>4</span>s</div><a class=btn href=/admin/logout>↗ Đăng xuất</a></div>
</div></header>
<main class=wrap>
  <div class=page-head><div><div class=eyebrow>HỆ THỐNG GIÁM SÁT · LIVE</div><h1>Control Center</h1><p class=page-desc>Quản lý bàn dự đoán, theo dõi hiệu suất và lịch sử học của PAW TX.</p></div><div class=head-tag><span class=tick-dot></span><span><strong>LIVE MONITORING</strong><br>Đồng bộ dữ liệu tự động</span></div></div>
  <nav class=navstrip><a href=#predCards>◈ Tổng quan bàn</a><a href=#secHu>◷ Lịch sử Hũ</a><a href=#secMd5>◷ Lịch sử MD5</a></nav>
  <div class=g2 id=predCards></div>
  <section class=section id=secHu><div class=sec-head><div><div class=eyebrow>LỊCH SỬ · TABLE 01</div><div class=sec-title>📊 Bàn Hũ</div><div class=sec-sub id=subHu>50 phiên gần nhất</div></div><div class=flex id=statHu></div></div><div class=tbl-scroll><table><thead><tr><th>#Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>Dự đoán</th><th>Trạng thái</th><th>Nguồn</th></tr></thead><tbody id=rowsHu></tbody></table></div></section>
  <div class=sep></div>
  <section class=section id=secMd5><div class=sec-head><div><div class=eyebrow>LỊCH SỬ · TABLE 02</div><div class=sec-title>📊 Bàn MD5</div><div class=sec-sub id=subMd5>50 phiên gần nhất</div></div><div class=flex id=statMd5></div></div><div class=tbl-scroll><table><thead><tr><th>#Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>Dự đoán</th><th>Trạng thái</th><th>Nguồn</th></tr></thead><tbody id=rowsMd5></tbody></table></div></section>
  <div class=footnote>PAW TX · SECURE ADMIN · AUTO REFRESH</div>
</main><div id=toast></div>
<script>
const CSRF="__CSRF__";
let D=[], _cdInt=null, _cdVal=4;
const $=id=>document.getElementById(id);
const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* ── Toast ── */
function toast(m, ok=true){
  const el=$('toast');
  el.innerHTML=`<span style="font-weight:800;font-size:14px">${ok?'✓':'✕'}</span> ${E(m)}`;
  el.style.borderLeftColor=ok?'#22c55e':'#ef4444';
  el.style.display='block';
  clearTimeout(el._t); el._t=setTimeout(()=>el.style.display='none', 3000);
}

/* ── Action ── */
async function act(c,a){
  try{
    const r=await fetch('/admin/act/'+c+'/'+a,{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json(); toast(j.ok?'Đã thực hiện: '+a:'Lỗi: '+(j.loi||'?'), j.ok); load();
  }catch(e){toast('Lỗi mạng',false)}
}

/* ── Helpers ── */
const side=s=>s?`<span class="badge ${s}">${s==='TAI'?'TÀI':'XỈU'}</span>`:'—';

function statBadges(st){
  return `<span class="badge win" style="font-size:12px;padding:4px 11px">✅ ${st.win} thắng</span>
          <span class="badge lose" style="font-size:12px;padding:4px 11px">❌ ${st.lose} thua</span>
          <span class="badge neutral" style="font-size:12px;padding:4px 11px">📈 ${st.ty_le}%</span>`;
}

function tableRows(hist){
  if(!hist||!hist.length) return '<tr><td colspan=6 style="text-align:center;padding:28px;color:#94a3b8">Chưa có dữ liệu</td></tr>';
  return hist.map(h=>`<tr>
    <td class=mono>#${h.phien}</td>
    <td class=mono>${(h.xuc_xac||[]).join('-')} = ${h.tong}</td>
    <td>${side(h.ket_qua)}</td>
    <td>${side(h.du_doan)}</td>
    <td>${h.trang_thai==='win'
      ?'<span class="badge win">✅ Thắng</span>'
      :h.trang_thai==='lose'
        ?'<span class="badge lose">❌ Thua</span>'
        :'<span class="badge neutral">—</span>'}</td>
    <td>${h.live
      ?'<span class="live-badge"><span class=live-dot></span>live</span>'
      :'<span class="muted small">📂 nạp</span>'}</td>
  </tr>`).join('');
}

/* ── Draw predict cards ── */
function drawPred(){
  $('predCards').innerHTML = D.map(t=>{
    const l=t.last, p=t.pending, en=t.enabled, rd=t.ready;
    const hdot=`<span class="hdot ${!en?'warn':t.err?'bad':'ok'}"></span>`;
    const ageStr=t.age==null?'–':(t.age<60?t.age+'s':Math.floor(t.age/60)+'m')+' trước';

    if(!rd||!l||!p){
      return `<div class=card>
        <div class=row><b style="font-size:16px;font-weight:800">${E(t.name)}</b>
          <button class="sw ${en?'on':''}" onclick="act('${t.code}','${en?'off':'on'}')"></button>
        </div>
        <div class="muted small" style="padding:16px 0">${en?'Đang nạp dữ liệu…':'Bàn đang tắt'}</div>
      </div>`;
    }

    const prevOk=l.trang_thai==='win';
    const prevIcon=l.trang_thai==='win'?'✅':l.trang_thai==='lose'?'❌':'—';

    const isTai = p.du_doan==='TAI';
    const pbSideColor = isTai ? '#fca5a5' : '#67e8f9';
    const pbSideShadow = isTai ? 'rgba(220,38,38,.4)' : 'rgba(8,145,178,.4)';
    return `<div class=card>
      <!-- header -->
      <div class=row style="padding-bottom:14px;border-bottom:1px solid var(--bd);margin-bottom:14px">
        <span class=flex style="gap:10px">
          ${hdot}
          <span style="font-size:16px;font-weight:850;letter-spacing:-.03em">Bàn ${E(t.name)}</span>
          <span class="badge ${rd?'win':'lose'}" style="font-size:10px">${rd?'Online':'Offline'}</span>
        </span>
        <span class=flex>
          <span class="muted small">${ageStr} · ${t.ms}ms</span>
          <button class="sw ${en?'on':''}" onclick="act('${t.code}','${en?'off':'on'}')" title="${en?'Tắt':'Bật'}"></button>
        </span>
      </div>

      <!-- predict banner -->
      <div class=pred-banner>
        <div class="flex pbinner" style="justify-content:space-between;gap:16px;position:relative;z-index:1">
          <div>
            <div class=pb-label>DỰ ĐOÁN PHIÊN #${p.phien}</div>
            <div class=pb-side style="color:${pbSideColor};text-shadow:0 2px 16px ${pbSideShadow}">${isTai?'TÀI ☀️':'XỈU 🌙'}</div>
            <div class=pb-conf>Độ tin cậy: <b>${p.conf}%</b></div>
            <div class=pb-meta>p(TÀI) = ${p.p_tai} · temp = ${p.temp}</div>
          </div>
          <div class=pb-right>
            <div class=pb-prev-label>Phiên trước #${l.phien}</div>
            <div style="display:flex;align-items:center;gap:8px;justify-content:flex-end;margin:4px 0">
              ${side(l.ket_qua)}
              <span style="font-size:11.5px;opacity:.8;font-family:'JetBrains Mono',monospace">
                ${(l.xuc_xac||[]).join('-')} = ${l.tong}
              </span>
            </div>
            <div style="display:flex;align-items:center;gap:7px;justify-content:flex-end">
              <span style="font-size:11.5px;opacity:.75">Dự đoán: ${side(l.du_doan)}</span>
              <span style="font-size:16px">${prevIcon}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- stats chips -->
      <div class=chips>
        <div class=chip>
          <div class="chip-val ${t.st_live.ty_le>=50?'green':'red'}">${t.st_live.ty_le}%</div>
          <div class=chip-lbl>${(t.st_live.win+t.st_live.lose)>0&&t.st_live.win+t.st_live.lose<=5?'5 gần nhất':'Live ('+( t.st_live.win+t.st_live.lose)+')'}</div>
        </div>
        <div class=chip>
          <div class="chip-val blue">${t.st_30.ty_le}%</div>
          <div class=chip-lbl>30 gần nhất</div>
        </div>
        <div class=chip>
          <div class="chip-val ${t.st_all.ty_le>=50?'green':'red'}">${t.st_all.ty_le}%</div>
          <div class=chip-lbl>${t.st_all.win}W / ${t.st_all.lose}L</div>
        </div>
      </div>

      <!-- experts -->
      <div style="margin-top:16px;border-top:1px solid var(--bd);padding-top:14px">
        <div style="font-size:11px;font-weight:800;color:var(--t3);letter-spacing:.07em;text-transform:uppercase;margin-bottom:10px">
          MÔ-ĐUN HỌC ĐIỂM · p(TÀI) / trọng số
        </div>
        ${t.experts.map(x=>{
          const pp=Math.round(x.p*100), ww=Math.round(x.w*100);
          const col=pp>55?'var(--blue)':pp<45?'var(--indigo)':'var(--t3)';
          return `<div class=ex-row>
            <span class=ex-name>${x.name.replace(/_/g,' ')}</span>
            <div class=prog><i style="width:${pp*2}%;background:${col}"></i></div>
            <span class="mono" style="font-size:10.5px;color:var(--t3);text-align:right">${pp}%·${ww}%</span>
          </div>`;
        }).join('')}
      </div>

      <!-- actions -->
      <div class=row style="margin-top:14px;padding-top:12px;border-top:1px solid var(--bd)">
        <span class=flex>
          <button class="btn btn-blue btn-sm" onclick="act('${t.code}','refresh')">↻ Làm mới</button>
          <button class="btn btn-sm" onclick="act('${t.code}','relearn')">🧠 Học lại</button>
        </span>
        <span class=flex>
          <a class="btn btn-sm" href="/tx/${t.code}?pretty=1" target=_blank>/tx</a>
          <a class="btn btn-sm" href="/history/tx/${t.code}?pretty=1" target=_blank>/history</a>
        </span>
      </div>

      ${t.err?`<div class=err-box>⚠ ${E(t.err)}</div>`:''}
    </div>`;
  }).join('');
}

/* ── Draw history tables ── */
function drawHistory(){
  const hu  = D.find(x=>x.code==='hu');
  const md5 = D.find(x=>x.code==='md5');

  if(hu){
    $('rowsHu').innerHTML = tableRows(hu.hist);
    $('statHu').innerHTML = statBadges(hu.st_all);
    $('subHu').textContent = `${hu.hist.length} phiên · cập nhật ${hu.age!=null?hu.age+'s trước':'–'}`;
  }
  if(md5){
    $('rowsMd5').innerHTML = tableRows(md5.hist);
    $('statMd5').innerHTML = statBadges(md5.st_all);
    $('subMd5').textContent = `${md5.hist.length} phiên · cập nhật ${md5.age!=null?md5.age+'s trước':'–'}`;
  }
}

/* ── Countdown ── */
function startCountdown(){
  clearInterval(_cdInt); _cdVal=4;
  $('countdown').textContent=_cdVal;
  _cdInt=setInterval(()=>{
    _cdVal=Math.max(0,_cdVal-1);
    $('countdown').textContent=_cdVal;
  },1000);
}

/* ── Load ── */
async function load(){
  try{
    const r=await fetch('/admin/data');
    if(r.status===401){location.href='/admin';return}
    D=(await r.json()).tables;
    $('tickLbl').textContent='Tự động cập nhật';
    drawPred(); drawHistory(); startCountdown();
  }catch(e){
    $('tickLbl').textContent='Lỗi kết nối';
    toast('Mất kết nối, thử lại…',false);
  }
}

load(); setInterval(load,4000);
</script>
</body></html>"""

@app.route("/admin/login", methods=["POST"])
def admin_login():
    ip = request.remote_addr or "?"; now = time.time()
    tries = [x for x in _fails.get(ip, []) if now - x < 300]
    if len(tries) >= 6: return redirect("/admin?e=Thử quá nhiều lần, chờ 5 phút")
    pw = os.getenv("ADMIN_PASS", "")
    ok = (bool(pw)
          and hmac.compare_digest(request.form.get("password", ""), pw)
          and hmac.compare_digest(request.form.get("username", ""),
                                  os.getenv("ADMIN_USER", "admin")))
    if not ok:
        _fails[ip] = tries + [now]; return redirect("/admin?e=Sai tài khoản hoặc mật khẩu")
    session.clear()
    session.update(adm=True, adm_until=now + 8 * 3600,
                   csrf=secrets.token_urlsafe(24))
    session.permanent = True
    return redirect("/admin")

@app.get("/admin/logout")
def admin_logout():
    session.clear(); return redirect("/admin")

@app.get("/admin")
def admin_page():
    if not authed():
        e = request.args.get("e", "")
        if not os.getenv("ADMIN_PASS"):
            e = "Chưa đặt biến môi trường ADMIN_PASS trên Render"
        err_html = f'<div class=err>{e.replace("<","&lt;")}</div>' if e else ""
        html = LOGIN.replace("__ERR__", err_html)
        r = make_response(html); r.headers["Content-Type"] = "text/html; charset=utf-8"; return r
    r = make_response(PAGE.replace("__CSRF__", session.get("csrf", "")))
    r.headers["Content-Type"] = "text/html; charset=utf-8"; return r

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
