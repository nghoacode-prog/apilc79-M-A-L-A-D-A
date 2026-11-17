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
CFG_FILE   = os.getenv("CFG_FILE",   "/tmp/paw_tx_cfg.json")

# ── API Access Protection ──────────────────────────────────────────────────────
# Trạng thái bảo vệ — load từ file để bền vững qua restart
_aprot = {"enabled": False, "code": ""}   # mutable dict, bảo vệ bởi _aprot_lock
_aprot_lock = threading.Lock()

# Rate limit: IP → [timestamps] cho truy cập sai mã
_code_fails: dict = {}   # ip → list[float]
_CODE_MAX_TRIES = 8      # thử tối đa 8 lần
_CODE_WINDOW    = 300    # trong 5 phút
_CODE_BACKOFF   = 600    # block 10 phút sau khi vượt ngưỡng

def _load_cfg():
    try:
        d = json.load(open(CFG_FILE))
        with _aprot_lock:
            _aprot["enabled"] = bool(d.get("enabled", False))
            _aprot["code"]    = str(d.get("code", ""))
    except Exception:
        pass

def _save_cfg():
    try:
        with _aprot_lock:
            snap = dict(_aprot)
        json.dump(snap, open(CFG_FILE, "w"))
    except Exception:
        pass

_load_cfg()

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
    # Không để Referrer rò rỉ mã trong URL
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp

def _check_code_ratelimit(ip: str) -> bool:
    """True = cho phép tiếp tục kiểm tra; False = đang bị block."""
    now = time.time()
    times = [t for t in _code_fails.get(ip, []) if now - t < _CODE_WINDOW]
    if len(times) >= _CODE_MAX_TRIES:
        return False
    return True

def _record_code_fail(ip: str):
    now = time.time()
    times = [t for t in _code_fails.get(ip, []) if now - t < _CODE_WINDOW]
    times.append(now)
    _code_fails[ip] = times

def _check_api_code(prefix_code: str) -> bool:
    """So sánh mã trong URL với mã được lưu (constant-time)."""
    with _aprot_lock:
        stored = _aprot["code"]
    if not stored:
        return False
    return hmac.compare_digest(prefix_code, stored)

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

# ── API có mã bảo vệ: /<code>/tx/<table> và /<code>/history/tx/<table> ───────
def _protected_gate(prefix_code: str):
    """Kiểm tra mã và rate limit. Trả None nếu pass, trả Response nếu fail."""
    with _aprot_lock:
        prot_on = _aprot["enabled"]
    if not prot_on:
        # Bảo vệ tắt → không xử lý route này (tool cũ dùng /tx/... không cần)
        return out({"ok": False, "loi": "not_found", "thong_bao": "Không tìm thấy"}, 404)
    ip = request.remote_addr or "0.0.0.0"
    if not _check_code_ratelimit(ip):
        return out({"ok": False, "loi": "rate_limited",
                    "thong_bao": "Quá nhiều lần thử sai, vui lòng chờ"}, 429)
    if not _check_api_code(prefix_code):
        _record_code_fail(ip)
        # Trả 404 thay vì 403 để không tiết lộ endpoint tồn tại
        return out({"ok": False, "loi": "not_found", "thong_bao": "Không tìm thấy"}, 404)
    return None   # pass

@app.get("/<prefix_code>/tx/<code>")
def api_main_protected(prefix_code, code):
    err = _protected_gate(prefix_code)
    if err: return err
    t, e = table_or_error(code); return e or out(view_main(t))

@app.get("/<prefix_code>/history/tx/<code>")
def api_history_protected(prefix_code, code):
    err = _protected_gate(prefix_code)
    if err: return err
    t, e = table_or_error(code)
    if e: return e
    try:    limit = max(1, min(HIST_MAX, int(request.args.get("limit", HIST_MAX))))
    except: limit = HIST_MAX
    return out(view_history(t, limit))

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

# ── API Protection admin endpoints ────────────────────────────────────────────
@app.post("/admin/aprot/gen")
def aprot_gen():
    """Tạo mã mới 6 ký tự an toàn (secrets.token_urlsafe)."""
    g = guard();
    if g: return g
    # 6 ký tự URL-safe (alphanum + - _), dùng secrets
    code = secrets.token_urlsafe(9)[:6].upper()
    # Đảm bảo đủ entropy: alphanum only
    import re as _re
    code = _re.sub(r'[^A-Z0-9]', lambda m: secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789'), code)
    with _aprot_lock:
        _aprot["code"] = code
    _save_cfg()
    return out({"ok": True, "code": code})

@app.post("/admin/aprot/set")
def aprot_set():
    """Bật/tắt bảo vệ API."""
    g = guard();
    if g: return g
    action = request.form.get("action") or (request.json or {}).get("action", "")
    if action not in ("enable", "disable"):
        return out({"ok": False, "loi": "bad_request"}, 400)
    with _aprot_lock:
        _aprot["enabled"] = (action == "enable")
        cur_code = _aprot["code"]
    _save_cfg()
    return out({"ok": True, "enabled": _aprot["enabled"], "code_set": bool(cur_code)})

@app.post("/admin/aprot/revoke")
def aprot_revoke():
    """Thu hồi mã hiện tại (xóa, bảo vệ tắt tự động)."""
    g = guard();
    if g: return g
    with _aprot_lock:
        _aprot["code"]    = ""
        _aprot["enabled"] = False
    _save_cfg()
    return out({"ok": True, "revoked": True})

@app.get("/admin/aprot/status")
def aprot_status():
    g = guard();
    if g: return g
    with _aprot_lock:
        snap = dict(_aprot)
    # KHÔNG trả mã về trong response — admin phải xem ở UI sau khi gen
    return out({"ok": True, "enabled": snap["enabled"], "has_code": bool(snap["code"])})

# ── Login page ─────────────────────────────────────────────────────────────────
LOGIN = """<!doctype html>
<html lang=vi><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name=theme-color content="#080d1b"><title>PAW TX · Secure Login</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}body{min-height:100vh;display:grid;place-items:center;padding:20px;background:radial-gradient(ellipse at 15% 0%,rgba(37,99,235,.24),transparent 40%),radial-gradient(ellipse at 90% 90%,rgba(124,58,237,.2),transparent 38%),#080d1b;color:#edf3ff;font:13px/1.6 Inter,system-ui,sans-serif}.login{width:min(420px,100%);padding:34px;border:1px solid rgba(148,163,184,.18);border-radius:22px;background:linear-gradient(145deg,rgba(20,32,55,.97),rgba(10,17,32,.98));box-shadow:0 28px 90px rgba(0,0,0,.45);position:relative;overflow:hidden}.login:before{content:'';position:absolute;inset:0 0 auto;height:2px;background:linear-gradient(90deg,#2563eb,#22d3ee,#8b5cf6)}.mark{width:58px;height:58px;margin:0 auto 20px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(145deg,#2563eb,#7c3aed);box-shadow:0 12px 32px rgba(79,70,229,.35);animation:float 3s ease-in-out infinite}.mark svg{width:34px;height:34px}.eyebrow{text-align:center;color:#67e8f9;font-size:9px;font-weight:800;letter-spacing:.2em;margin-bottom:8px}h1{text-align:center;font-size:25px;letter-spacing:-.05em;font-weight:900}.sub{text-align:center;color:#91a1bd;font-size:11px;margin:7px 0 26px}label{display:block;color:#a8b6cc;font-size:9px;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin:0 0 7px}input{width:100%;height:46px;margin:0 0 17px;padding:0 13px;border:1px solid rgba(148,163,184,.2);border-radius:11px;background:#0b1426;color:#edf3ff;font:13px Inter;outline:none;transition:.18s}input:focus{border-color:#60a5fa;box-shadow:0 0 0 3px rgba(59,130,246,.15)}button{width:100%;height:46px;border:0;border-radius:11px;background:linear-gradient(105deg,#2563eb,#5b4be8);color:#fff;font:800 12px Inter;cursor:pointer;box-shadow:0 8px 24px rgba(37,99,235,.24);transition:.18s}button:hover{filter:brightness(1.12);transform:translateY(-1px)}button:active{transform:scale(.99)}.err{margin:0 0 16px;padding:10px 12px;border-radius:10px;border:1px solid rgba(251,113,133,.25);background:rgba(251,113,133,.1);color:#fda4af;font-size:11px}.foot{margin-top:20px;text-align:center;color:#64748b;font-size:10px}.foot span{color:#91a1bd}@keyframes float{50%{transform:translateY(-5px)}}@media(max-width:480px){.login{padding:27px 22px;border-radius:18px}}
</style></head><body><main class=login><div class=mark><svg viewBox="0 0 40 40" fill=none><path d="M20 3S32 16 32 24a12 12 0 1 1-24 0C8 16 20 3 20 3Z" fill=white/><path d="M14 22c1.2-3.2 2.8-5.8 4.7-8" stroke="#93c5fd" stroke-width=2.5 stroke-linecap=round/></svg></div><div class=eyebrow>SECURE ADMIN ACCESS</div><h1>PAW TX Admin</h1><div class=sub>Đăng nhập để truy cập Control Center</div>__ERR__<form method=post action=/admin/login><label for=username>Tài khoản quản trị</label><input id=username name=username value=admin autocomplete=username required><label for=password>Mật khẩu</label><input id=password type=password name=password autocomplete=current-password autofocus required><button type=submit>ĐĂNG NHẬP HỆ THỐNG&nbsp; →</button></form><div class=foot><span>Phiên bảo mật 8 giờ</span> · PAW TX CONTROL CENTER</div></main></body></html>"""

# ── Admin SPA — WHITE LIGHT MODE ──────────────────────────────────────────────
PAGE = r"""<!doctype html>
<html lang=vi>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name=theme-color content="#f8fafc">
<title>PAW TX · Control Center</title>
<link rel=preconnect href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap" rel=stylesheet>
<style>
:root{
  --bg:#f5f7fa;--surface:#fff;--surface2:#f8fafc;--surface3:#eef2f7;
  --bd:#e4e9f0;--bd2:#d0d9e6;
  --txt:#0f1923;--txt2:#2d3a4f;--txt3:#64748b;--txt4:#94a3b8;
  --blue:#2563eb;--blue-s:#eff4ff;--blue-m:#dbeafe;--blue2:#1d4ed8;
  --cyan:#0ea5e9;--green:#16a34a;--green-s:#f0fdf4;
  --red:#dc2626;--red-s:#fff1f2;
  --amber:#ca8a04;--amber-s:#fefce8;
  --purple:#7c3aed;--purple-s:#f5f3ff;
  --indigo:#4f46e5;
  --r:14px;--r-sm:10px;--r-xs:8px;
  --shadow:0 1px 3px rgba(0,0,0,.07),0 1px 2px rgba(0,0,0,.04);
  --shadow-md:0 4px 12px rgba(0,0,0,.07),0 1px 3px rgba(0,0,0,.05);
  --shadow-lg:0 20px 50px rgba(0,0,0,.12),0 4px 12px rgba(0,0,0,.06);
  --topbar:62px;--sidebar:260px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg);font-size:14px;scroll-behavior:smooth}
body{background:var(--bg);color:var(--txt);font-family:'Inter',system-ui,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}button,input,select{font:inherit;cursor:pointer}
svg{vertical-align:middle;flex-shrink:0}
.mono{font-family:'JetBrains Mono',monospace;font-size:11px;font-variant-numeric:tabular-nums}

/* ═══ TOPBAR ═══ */
.topbar{height:var(--topbar);position:sticky;top:0;z-index:50;
  background:rgba(255,255,255,.92);backdrop-filter:blur(16px) saturate(160%);
  border-bottom:1px solid var(--bd);display:flex;align-items:center;
  justify-content:space-between;padding:0 24px;gap:16px}
.brand{display:flex;align-items:center;gap:11px;user-select:none}
.brand-mark{width:36px;height:36px;border-radius:11px;background:linear-gradient(145deg,#2563eb,#7c3aed);
  display:grid;place-items:center;box-shadow:0 4px 12px rgba(79,70,229,.28)}
.brand-mark svg{width:22px;height:22px}
.brand-name{font-size:14px;font-weight:900;letter-spacing:-.04em;color:var(--txt)}
.brand-name small{display:block;font-size:9px;color:var(--txt3);letter-spacing:.12em;font-weight:700}
.tbright{display:flex;align-items:center;gap:10px}
.sync-pill{display:flex;align-items:center;gap:7px;padding:6px 11px;border:1px solid var(--bd);
  border-radius:99px;font-size:11px;color:var(--txt3);background:var(--surface2)}
.sync-pill .ldot{width:7px;height:7px;border-radius:50%;background:var(--green);
  box-shadow:0 0 0 3px rgba(22,163,74,.12);animation:pulse 2.5s infinite}
#countdown{font-family:'JetBrains Mono',monospace;font-weight:800;color:var(--blue)}

/* ═══ NAV TABS ═══ */
.nav-tabs{display:flex;gap:2px;padding:0 24px;border-bottom:1px solid var(--bd);
  background:var(--surface);position:sticky;top:var(--topbar);z-index:40;overflow-x:auto}
.nav-tab{padding:14px 16px;font-size:12px;font-weight:700;color:var(--txt3);
  border-bottom:2px solid transparent;white-space:nowrap;cursor:pointer;
  transition:color .15s,border-color .15s;background:none;border-top:none;border-left:none;border-right:none}
.nav-tab.active{color:var(--blue);border-bottom-color:var(--blue)}
.nav-tab:hover{color:var(--txt2)}

/* ═══ WRAP ═══ */
.wrap{max-width:1400px;margin:0 auto;padding:24px 24px 60px}

/* ═══ BTN ═══ */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;
  padding:8px 14px;border-radius:var(--r-sm);font-size:12px;font-weight:700;
  border:1px solid transparent;white-space:nowrap;
  transition:background .15s,border-color .15s,transform .15s,box-shadow .15s}
.btn:active{transform:scale(.98)}
.btn-primary{background:var(--blue);color:#fff;border-color:var(--blue2);
  box-shadow:0 2px 8px rgba(37,99,235,.22)}
.btn-primary:hover{background:var(--blue2);box-shadow:0 4px 14px rgba(37,99,235,.3);transform:translateY(-1px)}
.btn-sec{background:var(--surface);border-color:var(--bd2);color:var(--txt2)}
.btn-sec:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-s)}
.btn-danger{background:var(--red-s);border-color:#fecdd3;color:var(--red)}
.btn-danger:hover{background:#ffe4e6}
.btn-success{background:var(--green-s);border-color:#bbf7d0;color:var(--green)}
.btn-amber{background:var(--amber-s);border-color:#fde68a;color:var(--amber)}
.btn-sm{padding:6px 10px;font-size:11px;border-radius:var(--r-xs)}
.btn-xs{padding:4px 8px;font-size:10px;border-radius:6px}
.btn-quiet{background:transparent;border-color:transparent;color:var(--txt3);padding:7px 9px}
.btn-quiet:hover{background:var(--surface2);color:var(--txt)}

/* ═══ BADGE ═══ */
.badge{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:99px;
  font-size:10px;font-weight:800;letter-spacing:.03em;border:1px solid;white-space:nowrap}
.badge.win{background:var(--green-s);color:var(--green);border-color:#bbf7d0}
.badge.lose{background:var(--red-s);color:var(--red);border-color:#fecdd3}
.badge.neutral{background:var(--surface3);color:var(--txt3);border-color:var(--bd2)}
.badge.info{background:var(--blue-s);color:var(--blue);border-color:var(--blue-m)}
.badge.amber{background:var(--amber-s);color:var(--amber);border-color:#fde68a}
.badge.TAI{background:#fff1f2;color:var(--red);border-color:#fecdd3}
.badge.XIU{background:#eff9ff;color:#0369a1;border-color:#bae6fd}

/* ═══ DOT ═══ */
.hdot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0}
.hdot.ok{background:var(--green);box-shadow:0 0 0 3px rgba(22,163,74,.12);animation:pulse 2.5s infinite}
.hdot.warn{background:var(--amber)}
.hdot.bad{background:var(--red);box-shadow:0 0 0 3px rgba(220,38,38,.1)}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--red);animation:pulse 1.4s infinite}

/* ═══ CARD ═══ */
.card{background:var(--surface);border:1px solid var(--bd);border-radius:var(--r);
  padding:20px;box-shadow:var(--shadow);transition:border-color .15s,box-shadow .15s,transform .15s;
  animation:fadeUp .35s ease both}
.card:hover{border-color:var(--bd2);box-shadow:var(--shadow-md);transform:translateY(-1px)}
.card-title{font-size:14px;font-weight:800;color:var(--txt);letter-spacing:-.02em;margin-bottom:16px;
  display:flex;align-items:center;gap:8px}

/* ═══ STAT CARD ═══ */
.stat-card{background:var(--surface);border:1px solid var(--bd);border-radius:var(--r);
  padding:18px 20px;box-shadow:var(--shadow);transition:border-color .15s,box-shadow .15s,transform .15s;
  position:relative;overflow:hidden;animation:fadeUp .35s ease both}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--sa,var(--blue));border-radius:var(--r) var(--r) 0 0}
.stat-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-md)}
.stat-label{font-size:10px;text-transform:uppercase;letter-spacing:.09em;color:var(--txt4);font-weight:800;margin-bottom:9px}
.stat-val{font-size:28px;font-weight:900;letter-spacing:-.05em;color:var(--txt);font-variant-numeric:tabular-nums;line-height:1.1}
.stat-note{font-size:11px;color:var(--txt4);margin-top:7px;display:flex;align-items:center;gap:5px}
.stat-icon{position:absolute;right:16px;top:14px;width:34px;height:34px;border-radius:9px;
  display:grid;place-items:center;background:var(--si,var(--blue-s));color:var(--sa,var(--blue))}

/* ═══ GRIDS ═══ */
.g2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.g3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.g4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.g6{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:14px}

/* ═══ ROW FLEX ═══ */
.row{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.flex{display:flex;align-items:center;gap:8px;min-width:0}

/* ═══ PROGRESS BAR ═══ */
.prog-bar{height:6px;background:var(--surface3);border-radius:99px;overflow:hidden}
.prog-bar span{display:block;height:100%;border-radius:99px;transition:width .4s ease}
.prog-inline{display:inline-block;width:68px;height:5px;vertical-align:middle;margin-right:5px;
  background:var(--surface3);border-radius:99px;overflow:hidden}
.prog-inline span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--blue),var(--cyan))}

/* ═══ PREDICT BANNER ═══ */
.pred-banner{margin-top:14px;border-radius:var(--r-sm);padding:18px 20px;position:relative;overflow:hidden;
  background:linear-gradient(135deg,#1e3a8a 0%,#1e1b4b 55%,#312e81 100%);
  border:1px solid #3b4fd8}
.pb-label{font-size:9px;font-weight:800;letter-spacing:.15em;color:#93c5fd;text-transform:uppercase;margin-bottom:7px}
.pb-side{font-size:clamp(28px,4vw,40px);font-weight:900;letter-spacing:-.06em;line-height:1;color:#fff}
.pb-side.TAI{color:#fca5a5;text-shadow:0 2px 16px rgba(239,68,68,.5)}
.pb-side.XIU{color:#67e8f9;text-shadow:0 2px 16px rgba(6,182,212,.5)}
.pb-conf{font-size:12px;font-weight:700;color:#e0eaff;margin-top:7px}
.pb-conf b{color:#fbbf24;font-size:16px}
.pb-meta{font:10px 'JetBrains Mono',monospace;color:#94a3b8;margin-top:4px}
.pb-right{text-align:right;min-width:135px}
.pb-prev-label{font-size:9px;font-weight:800;letter-spacing:.12em;color:#93c5fd;text-transform:uppercase;margin-bottom:6px}

/* ═══ CHIPS (3 stat) ═══ */
.chips3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:12px}
.chip{padding:11px;border:1px solid var(--bd);border-radius:var(--r-sm);background:var(--surface2)}
.chip-val{font-size:20px;font-weight:900;letter-spacing:-.05em;line-height:1.2;margin-bottom:3px;
  font-variant-numeric:tabular-nums}
.chip-val.green{color:var(--green)}.chip-val.red{color:var(--red)}.chip-val.blue{color:var(--blue)}
.chip-lbl{font-size:9px;color:var(--txt4);font-weight:800;letter-spacing:.1em;text-transform:uppercase}

/* ═══ EXPERT ROW ═══ */
.ex-row{display:grid;grid-template-columns:110px 1fr 60px;align-items:center;gap:8px;padding:5px 0}
.ex-name{font-size:10px;font-weight:700;color:var(--txt3);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.prog{height:5px;background:var(--surface3);border-radius:99px;overflow:hidden}
.prog i{display:block;height:100%;border-radius:99px;transition:width .3s}

/* ═══ TOGGLE SWITCH ═══ */
.sw{width:40px;height:22px;border-radius:99px;background:var(--bd2);position:relative;
  cursor:pointer;border:none;flex-shrink:0;transition:.2s}
.sw::after{content:'';position:absolute;top:3px;left:3px;width:16px;height:16px;border-radius:50%;
  background:#fff;transition:.2s;box-shadow:var(--shadow)}
.sw.on{background:var(--green)}.sw.on::after{left:21px}

/* ═══ TABLE ═══ */
.tbl-scroll{overflow:auto;border:1px solid var(--bd);border-radius:var(--r-sm);background:var(--surface)}
table{width:100%;border-collapse:separate;border-spacing:0;white-space:nowrap}
thead{position:sticky;top:0;z-index:2;background:var(--surface2)}
th{padding:11px 14px;font-size:9px;letter-spacing:.09em;text-transform:uppercase;color:var(--txt4);
  text-align:left;border-bottom:1px solid var(--bd);font-weight:800}
td{padding:11px 14px;font-size:12px;color:var(--txt2);border-bottom:1px solid var(--surface3)}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover td{background:#fafcff}
.live-badge{display:inline-flex;align-items:center;gap:5px;font-size:9px;font-weight:800;
  padding:3px 7px;border-radius:99px;background:#fff1f2;border:1px solid #fecdd3;color:var(--red)}

/* ═══ PROTECTION BOX ═══ */
.prot-box{background:linear-gradient(135deg,#eff6ff,#f5f3ff);border:1px solid #c7d2fe;
  border-radius:var(--r);padding:22px;margin-bottom:16px}
.prot-title{font-size:15px;font-weight:800;color:var(--txt);margin-bottom:5px;
  display:flex;align-items:center;gap:9px}
.prot-sub{font-size:12px;color:var(--txt3);margin-bottom:16px}
.prot-status{display:inline-flex;align-items:center;gap:7px;padding:7px 14px;border-radius:99px;
  font-size:11px;font-weight:800;border:1.5px solid;margin-bottom:16px}
.prot-status.on{background:var(--green-s);color:var(--green);border-color:#86efac}
.prot-status.off{background:var(--surface3);color:var(--txt3);border-color:var(--bd2)}
.code-box{display:flex;align-items:center;gap:10px;padding:12px 16px;
  background:var(--surface);border:1px solid var(--bd2);border-radius:var(--r-sm);margin-bottom:14px}
.code-val{font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:700;
  letter-spacing:.22em;color:var(--blue);flex:1}
.prot-url{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--txt3);
  word-break:break-all;padding:9px 12px;background:var(--surface2);border-radius:var(--r-xs);
  border:1px solid var(--bd);margin-top:10px}
.prot-url b{color:var(--blue)}

/* ═══ ERR BOX ═══ */
.err-box{margin-top:12px;padding:10px 13px;border-radius:var(--r-xs);
  background:var(--red-s);border:1px solid #fecdd3;color:var(--red);font-size:11px}

/* ═══ SECTION ═══ */
.section{padding-top:28px;scroll-margin-top:calc(var(--topbar) + 52px)}
.sec-head{display:flex;align-items:flex-end;justify-content:space-between;gap:14px;
  flex-wrap:wrap;margin-bottom:14px}
.sec-title{font-size:15px;font-weight:800;letter-spacing:-.03em;color:var(--txt)}
.sec-sub{font-size:11px;color:var(--txt4);margin-top:3px}
.sep{height:1px;background:linear-gradient(90deg,transparent,var(--bd),transparent);margin:24px 0}

/* ═══ TOAST ═══ */
#toast{position:fixed;right:20px;bottom:20px;z-index:9999;display:none;min-width:230px;
  max-width:calc(100vw - 32px);padding:12px 16px;border:1px solid var(--bd);
  border-left:3px solid var(--green);border-radius:var(--r-sm);background:var(--surface);
  color:var(--txt);box-shadow:var(--shadow-lg);font-size:12px;animation:fadeUp .2s ease}

/* ═══ HERO SECTION ═══ */
.hero{background:linear-gradient(135deg,#eff6ff 0%,#f0f7ff 50%,#f5f3ff 100%);
  border:1px solid var(--bd);border-radius:16px;padding:26px 30px;margin-bottom:22px;
  position:relative;overflow:hidden;animation:fadeUp .4s ease both}
.hero::before{content:'';position:absolute;right:-40px;top:-40px;width:200px;height:200px;
  border-radius:50%;background:radial-gradient(circle,rgba(37,99,235,.07),transparent 65%);pointer-events:none}
.hero-title{font-size:20px;font-weight:900;letter-spacing:-.04em;color:var(--txt);margin-bottom:5px}
.hero-sub{font-size:13px;color:var(--txt3);max-width:420px}
.hero-stats{display:flex;gap:22px;margin-top:16px;flex-wrap:wrap}
.hero-stat b{display:block;font-size:20px;font-weight:900;letter-spacing:-.04em;color:var(--txt);margin-bottom:1px}
.hero-stat span{font-size:11px;color:var(--txt3)}

/* ═══ ANIM ═══ */
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{50%{box-shadow:0 0 0 6px transparent}}

/* ═══ RESPONSIVE ═══ */
@media(max-width:1000px){.g6{grid-template-columns:repeat(3,minmax(0,1fr))}.g4{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px){.wrap{padding:16px 14px 48px}.g2,.g3{grid-template-columns:1fr}.g6{grid-template-columns:repeat(2,minmax(0,1fr))}.g4{grid-template-columns:1fr 1fr}}
@media(max-width:480px){.g6{grid-template-columns:1fr 1fr}.topbar{padding:0 14px}.hero{padding:18px 16px}.hero-stats{gap:14px}.chips3{gap:6px}.pred-banner{padding:14px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style>
</head>
<body>

<!-- TOPBAR -->
<header class=topbar>
  <div class=brand>
    <div class=brand-mark>
      <svg viewBox="0 0 28 28" fill=none>
        <path d="M14 2.5S22.5 12 22.5 17.5a8.5 8.5 0 1 1-17 0C5.5 12 14 2.5 14 2.5Z" fill="white"/>
        <path d="M10 15.5c.8-2.2 2-4.2 3.3-5.8" stroke="#93c5fd" stroke-width=2 stroke-linecap=round/>
      </svg>
    </div>
    <div class=brand-name>PAW TX<small>ADMIN CONTROL CENTER</small></div>
  </div>
  <div class=tbright>
    <div class=sync-pill><span class=ldot></span><span>Đồng bộ <span id=countdown>4</span>s</span></div>
    <span id=tickLbl style="font-size:11px;color:var(--txt3)">Đang kết nối…</span>
    <a class="btn btn-sec btn-sm" href=/admin/logout>Đăng xuất →</a>
  </div>
</header>

<!-- NAV TABS -->
<nav class=nav-tabs>
  <button class="nav-tab active" onclick="switchTab('dashboard',this)">📊 Tổng quan</button>
  <button class=nav-tab onclick="switchTab('tables',this)">🎯 Bàn dự đoán</button>
  <button class=nav-tab onclick="switchTab('history',this)">📋 Lịch sử</button>
  <button class=nav-tab onclick="switchTab('protection',this)">🔐 Bảo vệ API</button>
</nav>

<!-- CONTENT -->
<main class=wrap>

<!-- ═══ TAB: DASHBOARD ═══ -->
<div id=tab-dashboard>
  <!-- Hero -->
  <div class=hero>
    <div class=hero-title>Bảng điều khiển PAW TX</div>
    <div class=hero-sub>Quản lý và giám sát hệ thống dự đoán LC79 · Hũ & MD5 · AI tự học</div>
    <div class=hero-stats>
      <div class=hero-stat><b id=hs-total>—</b><span>Tổng phiên</span></div>
      <div class=hero-stat><b id=hs-live>—</b><span>Dự đoán live</span></div>
      <div class=hero-stat><b id=hs-acc>—%</b><span>Accuracy TB</span></div>
      <div class=hero-stat><b id=hs-ms>—ms</b><span>Thời gian phản hồi</span></div>
    </div>
  </div>

  <!-- Stat cards -->
  <div class=g6 style="margin-bottom:20px" id=statCards></div>

  <!-- State cards (2 bàn) -->
  <div class=g2 id=quickCards></div>
</div>

<!-- ═══ TAB: TABLES (Predict cards) ═══ -->
<div id=tab-tables style="display:none">
  <div class=g2 id=predCards></div>
</div>

<!-- ═══ TAB: HISTORY ═══ -->
<div id=tab-history style="display:none">
  <section class=section id=secHu>
    <div class=sec-head>
      <div>
        <div class=sec-title>Lịch sử · Bàn Hũ</div>
        <div class=sec-sub id=subHu>50 phiên gần nhất</div>
      </div>
      <div class=flex id=statHu></div>
    </div>
    <div class=tbl-scroll><table>
      <thead><tr><th>#Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>Dự đoán</th><th>Trạng thái</th><th>Nguồn</th></tr></thead>
      <tbody id=rowsHu></tbody>
    </table></div>
  </section>
  <div class=sep></div>
  <section class=section id=secMd5>
    <div class=sec-head>
      <div>
        <div class=sec-title>Lịch sử · Bàn MD5</div>
        <div class=sec-sub id=subMd5>50 phiên gần nhất</div>
      </div>
      <div class=flex id=statMd5></div>
    </div>
    <div class=tbl-scroll><table>
      <thead><tr><th>#Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>Dự đoán</th><th>Trạng thái</th><th>Nguồn</th></tr></thead>
      <tbody id=rowsMd5></tbody>
    </table></div>
  </section>
</div>

<!-- ═══ TAB: PROTECTION ═══ -->
<div id=tab-protection style="display:none">
  <div class=g2>
    <!-- Left: Control -->
    <div>
      <div class=prot-box>
        <div class=prot-title>
          <svg width=18 height=18 viewBox="0 0 24 24" fill=none stroke="currentColor" stroke-width=2 stroke-linecap=round><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          API ACCESS PROTECTION
        </div>
        <div class=prot-sub>Thêm mã 6 ký tự vào đường dẫn API để chống chia sẻ trái phép. Kết hợp rate limit tự động.</div>

        <!-- Status badge -->
        <div class="prot-status off" id=protStatus>
          <span>⚪</span><span id=protStatusTxt>Đang tắt</span>
        </div>

        <!-- Code display -->
        <div class=code-box>
          <div class=code-val id=codeDisplay>••••••</div>
          <button class="btn btn-sec btn-sm" id=btnCopy onclick=copyCode()>
            <svg width=13 height=13 viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=2><rect x=9 y=9 width=13 height=13 rx=2/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            Sao chép
          </button>
        </div>

        <!-- URL preview -->
        <div class=prot-url id=urlPreview>Tạo mã để xem URL bảo vệ</div>

        <!-- Actions -->
        <div class=flex style="flex-wrap:wrap;gap:8px;margin-top:14px">
          <button class="btn btn-primary" onclick=genCode()>
            <svg width=13 height=13 viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=2.5><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            Tạo mã mới
          </button>
          <button class="btn btn-success" id=btnEnable onclick=setProt('enable')>
            <svg width=13 height=13 viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=2.5><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Bật bảo vệ
          </button>
          <button class="btn btn-danger" id=btnDisable onclick=setProt('disable')>
            <svg width=13 height=13 viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=2><circle cx=12 cy=12 r=10/><line x1=4.93 y1=4.93 x2=19.07 y2=19.07/></svg>
            Tắt bảo vệ
          </button>
          <button class="btn btn-amber" onclick=revokeCode()>
            <svg width=13 height=13 viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=2><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/></svg>
            Thu hồi mã
          </button>
        </div>
      </div>
    </div>

    <!-- Right: Info -->
    <div class=card style="animation-delay:.1s">
      <div class=card-title>
        <svg width=16 height=16 viewBox="0 0 24 24" fill=none stroke=currentColor stroke-width=2><circle cx=12 cy=12 r=10/><line x1=12 y1=8 x2=12 y2=12/><line x1=12 y1=16 x2=12.01 y2=16/></svg>
        Hướng dẫn sử dụng
      </div>
      <div style="font-size:12.5px;color:var(--txt2);line-height:1.75">
        <p style="margin-bottom:10px"><b>Khi bảo vệ BẬT:</b> API chỉ chấp nhận URL có mã đúng.</p>
        <p style="margin-bottom:10px"><b>Ví dụ URL sau khi bật:</b></p>
        <div class=prot-url style="margin-bottom:12px">
          <b>https://apilc79…onrender.com/[MÃ6KÝ]/tx/hu</b>
        </div>
        <p style="margin-bottom:10px"><b>Khi bảo vệ TẮT:</b> Các endpoint cũ <code style="font-family:monospace;background:var(--surface2);padding:1px 4px;border-radius:4px">/tx/hu</code> hoạt động bình thường.</p>
        <p style="margin-bottom:10px"><b>Khi đổi mã:</b> Mã cũ mất hiệu lực ngay lập tức.</p>
        <p style="margin-bottom:10px"><b>Rate limit:</b> IP sai mã >8 lần / 5 phút → bị block 10 phút.</p>
        <p style="margin-bottom:10px"><b>Lưu ý:</b> Mã 6 ký tự là lớp bảo vệ đường dẫn, không thay thế HTTPS. Dùng kết hợp để hiệu quả nhất.</p>
      </div>

      <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--bd)">
        <div class=card-title style="font-size:12px;margin-bottom:12px">Rate Limit Monitor</div>
        <div id=rateLimitInfo style="font-size:12px;color:var(--txt3)">Đang tải…</div>
      </div>
    </div>
  </div>
</div>

</main>
<div id=toast></div>
<script>
const CSRF="__CSRF__";
let D=[], _cdInt=null, _cdVal=4, _curTab='dashboard';
let _protState={enabled:false, has_code:false, code:''};
const $=id=>document.getElementById(id);
const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* ═══ TAB SWITCH ═══ */
function switchTab(name, btn){
  _curTab=name;
  ['dashboard','tables','history','protection'].forEach(t=>{
    const el=$('tab-'+t); if(el) el.style.display=t===name?'':'none';
  });
  document.querySelectorAll('.nav-tab').forEach(b=>b.classList.toggle('active',b===btn));
  if(name==='history') drawHistory();
  if(name==='protection') loadProt();
}

/* ═══ TOAST ═══ */
function toast(m, ok=true){
  const el=$('toast');
  el.innerHTML=`<span style="font-weight:800;font-size:14px;color:${ok?'var(--green)':'var(--red)'}">${ok?'✓':'✕'}</span> ${E(m)}`;
  el.style.borderLeftColor=ok?'var(--green)':'var(--red)';
  el.style.display='block';
  clearTimeout(el._t); el._t=setTimeout(()=>el.style.display='none', 3000);
}

/* ═══ ACT ═══ */
async function act(c,a){
  try{
    const r=await fetch('/admin/act/'+c+'/'+a,{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json(); toast(j.ok?'Đã thực hiện: '+a:'Lỗi: '+(j.loi||'?'), j.ok); load();
  }catch(e){toast('Lỗi mạng',false)}
}

/* ═══ SIDE HELPER ═══ */
const side=s=>s?`<span class="badge ${s}">${s==='TAI'?'TÀI':'XỈU'}</span>`:'—';

/* ═══ STAT BADGES ═══ */
function statBadges(st){
  return `<span class="badge win">✅ ${st.win} thắng</span>
          <span class="badge lose">❌ ${st.lose} thua</span>
          <span class="badge info">📈 ${st.ty_le}%</span>`;
}

/* ═══ TABLE ROWS ═══ */
function tableRows(hist){
  if(!hist||!hist.length) return '<tr><td colspan=6 style="text-align:center;padding:28px;color:var(--txt4)">Chưa có dữ liệu</td></tr>';
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
      ?'<span class="live-badge"><span class=live-dot></span> live</span>'
      :'<span style="font-size:10px;color:var(--txt4)">📂 nạp</span>'}</td>
  </tr>`).join('');
}

/* ═══ DRAW DASHBOARD ═══ */
function drawDashboard(){
  if(!D.length) return;
  // Hero stats
  const totalSessions=D.reduce((s,t)=>s+(t.hist||[]).length,0);
  const liveCount=D.reduce((s,t)=>s+((t.hist||[]).filter(h=>h.live).length),0);
  const allWin=D.reduce((s,t)=>s+t.st_all.win,0);
  const allTotal=D.reduce((s,t)=>s+t.st_all.win+t.st_all.lose,0);
  const avgAcc=allTotal>0?Math.round(allWin*100/allTotal):0;
  const avgMs=Math.round(D.reduce((s,t)=>s+t.ms,0)/D.length)||0;
  $('hs-total').textContent=totalSessions;
  $('hs-live').textContent=liveCount;
  $('hs-acc').textContent=avgAcc+'%';
  $('hs-ms').textContent=avgMs+'ms';

  // Stat cards
  const sc=[
    {label:'Bàn Hũ · API',val:D.find(x=>x.code==='hu')?.ready?'Online':'Offline',note:'Trạng thái kết nối',sa:'var(--blue)',si:'var(--blue-s)',icon:'🎲'},
    {label:'Bàn MD5 · API',val:D.find(x=>x.code==='md5')?.ready?'Online':'Offline',note:'Trạng thái kết nối',sa:'var(--cyan)',si:'#f0f9ff',icon:'🎯'},
    ...D.map(t=>({label:'Accuracy · '+t.name,val:t.st_30.ty_le+'%',note:t.st_30.win+'W / '+t.st_30.lose+'L (30 phiên)',sa:'var(--purple)',si:'var(--purple-s)',icon:'🧠'})),
    ...D.map(t=>({label:'Live · '+t.name,val:t.st_live.ty_le+'%',note:t.st_live.win+'W / '+t.st_live.lose+'L',sa:'var(--green)',si:'var(--green-s)',icon:'📡'})),
  ];
  $('statCards').innerHTML=sc.slice(0,6).map((s,i)=>`
    <div class=stat-card style="--sa:${s.sa};--si:${s.si};animation-delay:${i*.05}s">
      <div class=stat-label>${E(s.label)}</div>
      <div class=stat-val>${E(s.val)}</div>
      <div class=stat-note>${E(s.note)}</div>
    </div>`).join('');

  // Quick table cards
  $('quickCards').innerHTML=D.map(t=>{
    const pd=t.pending, en=t.enabled, rd=t.ready;
    if(!rd||!pd) return `<div class=card>
      <div class=card-title><span class="hdot ${en?'warn':'bad'}"></span>Bàn ${E(t.name)}</div>
      <div style="color:var(--txt3);font-size:13px">${en?'Đang nạp…':'Bàn tắt'}</div>
    </div>`;
    const isTai=pd.du_doan==='TAI';
    return `<div class=card>
      <div class=row style="margin-bottom:14px">
        <div class=flex>
          <span class="hdot ${rd?'ok':'bad'}"></span>
          <span style="font-size:15px;font-weight:800">Bàn ${E(t.name)}</span>
          <span class="badge ${rd?'info':'neutral'}">${rd?'Online':'Offline'}</span>
        </div>
        <div class=flex>
          <span style="font-size:11px;color:var(--txt4)">${t.age!=null?t.age+'s trước':'–'} · ${t.ms}ms</span>
          <button class="sw ${en?'on':''}" onclick="act('${t.code}','${en?'off':'on'}')"></button>
        </div>
      </div>
      <div class=pred-banner>
        <div class=row>
          <div>
            <div class=pb-label>DỰ ĐOÁN PHIÊN #${pd.phien}</div>
            <div class="pb-side ${isTai?'TAI':'XIU'}">${isTai?'TÀI ☀️':'XỈU 🌙'}</div>
            <div class=pb-conf>Độ tin cậy: <b>${pd.conf}%</b></div>
          </div>
          <div class=pb-right>
            ${t.last?`<div class=pb-prev-label>Phiên trước #${t.last.phien}</div>
            <div class=flex style="justify-content:flex-end;gap:8px;margin:4px 0">
              ${side(t.last.ket_qua)}
              <span class=mono style="color:#93c5fd">${(t.last.xuc_xac||[]).join('-')} = ${t.last.tong}</span>
            </div>
            <div class=flex style="justify-content:flex-end;gap:6px">
              ${side(t.last.du_doan)}
              <span style="font-size:16px">${t.last.trang_thai==='win'?'✅':t.last.trang_thai==='lose'?'❌':'—'}</span>
            </div>`:''}
          </div>
        </div>
      </div>
      <div class=chips3>
        <div class=chip>
          <div class="chip-val ${t.st_live.ty_le>=50?'green':'red'}">${t.st_live.ty_le}%</div>
          <div class=chip-lbl>Live</div>
        </div>
        <div class=chip>
          <div class="chip-val blue">${t.st_30.ty_le}%</div>
          <div class=chip-lbl>30 phiên</div>
        </div>
        <div class=chip>
          <div class="chip-val ${t.st_all.ty_le>=50?'green':'red'}">${t.st_all.ty_le}%</div>
          <div class=chip-lbl>${t.st_all.win}W / ${t.st_all.lose}L</div>
        </div>
      </div>
    </div>`;
  }).join('');
}

/* ═══ DRAW PREDICT CARDS (tab bàn) ═══ */
function drawPred(){
  $('predCards').innerHTML=D.map(t=>{
    const l=t.last, p=t.pending, en=t.enabled, rd=t.ready;
    if(!rd||!l||!p) return `<div class=card>
      <div class="row" style="margin-bottom:12px">
        <span style="font-size:16px;font-weight:800">Bàn ${E(t.name)}</span>
        <button class="sw ${en?'on':''}" onclick="act('${t.code}','${en?'off':'on'}')"></button>
      </div>
      <div style="color:var(--txt3)">${en?'Đang nạp dữ liệu…':'Bàn đang tắt'}</div>
    </div>`;
    const isTai=p.du_doan==='TAI';
    return `<div class=card>
      <div class=row style="padding-bottom:14px;border-bottom:1px solid var(--bd);margin-bottom:14px">
        <div class=flex>
          <span class="hdot ${rd?'ok':'bad'}"></span>
          <span style="font-size:16px;font-weight:800;letter-spacing:-.03em">Bàn ${E(t.name)}</span>
          <span class="badge ${rd?'info':'neutral'}">${rd?'Online':'Offline'}</span>
        </div>
        <div class=flex>
          <span style="font-size:11px;color:var(--txt4)">${t.age!=null?t.age+'s':'–'} · ${t.ms}ms</span>
          <button class="sw ${en?'on':''}" onclick="act('${t.code}','${en?'off':'on'}')" title="${en?'Tắt':'Bật'}"></button>
        </div>
      </div>
      <div class=pred-banner>
        <div class="flex" style="justify-content:space-between;gap:16px">
          <div>
            <div class=pb-label>DỰ ĐOÁN PHIÊN #${p.phien}</div>
            <div class="pb-side ${isTai?'TAI':'XIU'}">${isTai?'TÀI ☀️':'XỈU 🌙'}</div>
            <div class=pb-conf>Độ tin cậy: <b>${p.conf}%</b></div>
            <div class=pb-meta>p(TÀI) = ${p.p_tai} · temp = ${p.temp}</div>
          </div>
          <div class=pb-right>
            <div class=pb-prev-label>Phiên trước #${l.phien}</div>
            <div class=flex style="justify-content:flex-end;gap:8px;margin:4px 0">
              ${side(l.ket_qua)}
              <span class=mono style="color:#93c5fd">${(l.xuc_xac||[]).join('-')} = ${l.tong}</span>
            </div>
            <div class=flex style="justify-content:flex-end;gap:7px">
              <span style="font-size:11px;color:#94a3b8">Dự đoán: ${side(l.du_doan)}</span>
              <span style="font-size:16px">${l.trang_thai==='win'?'✅':l.trang_thai==='lose'?'❌':'—'}</span>
            </div>
          </div>
        </div>
      </div>
      <div class=chips3>
        <div class=chip>
          <div class="chip-val ${t.st_live.ty_le>=50?'green':'red'}">${t.st_live.ty_le}%</div>
          <div class=chip-lbl>Live (${t.st_live.win+t.st_live.lose})</div>
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
      <div style="margin-top:16px;border-top:1px solid var(--bd);padding-top:14px">
        <div style="font-size:10px;font-weight:800;color:var(--txt4);letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px">
          MÔ-ĐUN HỌC ĐIỂM · p(TÀI) / trọng số
        </div>
        ${t.experts.map(x=>{
          const pp=Math.round(x.p*100), ww=Math.round(x.w*100);
          const col=pp>55?'var(--blue)':pp<45?'var(--indigo)':'var(--txt4)';
          return `<div class=ex-row>
            <span class=ex-name>${x.name.replace(/_/g,' ')}</span>
            <div class=prog><i style="width:${pp*2}%;background:${col}"></i></div>
            <span class=mono style="font-size:10px;color:var(--txt4);text-align:right">${pp}%·${ww}%</span>
          </div>`;
        }).join('')}
      </div>
      <div class=row style="margin-top:14px;padding-top:12px;border-top:1px solid var(--bd)">
        <div class=flex>
          <button class="btn btn-primary btn-sm" onclick="act('${t.code}','refresh')">↻ Làm mới</button>
          <button class="btn btn-sec btn-sm" onclick="act('${t.code}','relearn')">🧠 Học lại</button>
        </div>
        <div class=flex>
          <a class="btn btn-sec btn-sm" href="/tx/${t.code}?pretty=1" target=_blank>/tx</a>
          <a class="btn btn-sec btn-sm" href="/history/tx/${t.code}?pretty=1" target=_blank>/history</a>
        </div>
      </div>
      ${t.err?`<div class=err-box>⚠ ${E(t.err)}</div>`:''}
    </div>`;
  }).join('');
}

/* ═══ DRAW HISTORY ═══ */
function drawHistory(){
  const hu=D.find(x=>x.code==='hu'), md5=D.find(x=>x.code==='md5');
  if(hu){$('rowsHu').innerHTML=tableRows(hu.hist);$('statHu').innerHTML=statBadges(hu.st_all);$('subHu').textContent=`${hu.hist.length} phiên · ${hu.age!=null?hu.age+'s trước':'–'}`;}
  if(md5){$('rowsMd5').innerHTML=tableRows(md5.hist);$('statMd5').innerHTML=statBadges(md5.st_all);$('subMd5').textContent=`${md5.hist.length} phiên · ${md5.age!=null?md5.age+'s trước':'–'}`;}
}

/* ═══ PROTECTION ═══ */
async function loadProt(){
  try{
    const r=await fetch('/admin/aprot/status',{headers:{'X-CSRF-Token':CSRF}});
    if(r.status===401){location.href='/admin';return}
    const j=await r.json();
    _protState={enabled:j.enabled, has_code:j.has_code, code:_protState.code};
    renderProtUI();
  }catch(e){$('rateLimitInfo').textContent='Lỗi kết nối'}
}

function renderProtUI(){
  const st=$('protStatus'), stTxt=$('protStatusTxt');
  if(_protState.enabled){
    st.className='prot-status on'; stTxt.textContent='Đang BẬT';
  } else {
    st.className='prot-status off'; stTxt.textContent='Đang tắt';
  }
  if(_protState.code){
    $('codeDisplay').textContent=_protState.code;
    $('urlPreview').innerHTML=`<b>https://apilc79-m-a-l-a-d-a.onrender.com/<span style="color:var(--blue)">${E(_protState.code)}</span>/tx/hu</b>`;
  } else if(_protState.has_code){
    $('codeDisplay').textContent='••••••';
    $('urlPreview').textContent='Mã đã tồn tại. Tạo mã mới để xem.';
  }
  $('rateLimitInfo').textContent=`Bảo vệ: ${_protState.enabled?'BẬT':'TẮT'} · Mã: ${_protState.has_code?'Có mã':'Chưa có mã'}`;
}

async function genCode(){
  try{
    const r=await fetch('/admin/aprot/gen',{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();
    if(j.ok){_protState.code=j.code;_protState.has_code=true;renderProtUI();toast('Đã tạo mã mới: '+j.code);}
    else toast('Lỗi tạo mã: '+(j.loi||'?'),false);
  }catch(e){toast('Lỗi mạng',false)}
}

async function setProt(action){
  if(action==='enable'&&!_protState.has_code){toast('Hãy tạo mã trước khi bật bảo vệ',false);return;}
  try{
    const fd=new FormData(); fd.append('action',action);
    const r=await fetch('/admin/aprot/set',{method:'POST',headers:{'X-CSRF-Token':CSRF},body:fd});
    const j=await r.json();
    if(j.ok){_protState.enabled=j.enabled;renderProtUI();toast(action==='enable'?'Bảo vệ API đã BẬT ✅':'Bảo vệ API đã TẮT');}
    else toast('Lỗi: '+(j.loi||'?'),false);
  }catch(e){toast('Lỗi mạng',false)}
}

async function revokeCode(){
  if(!confirm('Thu hồi mã sẽ TẮT bảo vệ ngay lập tức. Tiếp tục?')) return;
  try{
    const r=await fetch('/admin/aprot/revoke',{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();
    if(j.ok){_protState={enabled:false,has_code:false,code:''};$('codeDisplay').textContent='••••••';$('urlPreview').textContent='Tạo mã để xem URL bảo vệ';renderProtUI();toast('Đã thu hồi mã thành công');}
    else toast('Lỗi: '+(j.loi||'?'),false);
  }catch(e){toast('Lỗi mạng',false)}
}

function copyCode(){
  const code=_protState.code;
  if(!code||code==='••••••'){toast('Chưa có mã để sao chép',false);return;}
  navigator.clipboard?.writeText(code).then(()=>toast('Đã sao chép mã: '+code));
}

/* ═══ COUNTDOWN ═══ */
function startCountdown(){
  clearInterval(_cdInt); _cdVal=4;
  $('countdown').textContent=_cdVal;
  _cdInt=setInterval(()=>{_cdVal=Math.max(0,_cdVal-1);$('countdown').textContent=_cdVal;},1000);
}

/* ═══ LOAD ═══ */
async function load(){
  try{
    const r=await fetch('/admin/data');
    if(r.status===401){location.href='/admin';return}
    D=(await r.json()).tables;
    $('tickLbl').textContent='Đã đồng bộ';
    drawDashboard(); drawPred();
    if(_curTab==='history') drawHistory();
    startCountdown();
  }catch(e){
    $('tickLbl').textContent='Lỗi kết nối';
    toast('Mất kết nối…',false);
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
