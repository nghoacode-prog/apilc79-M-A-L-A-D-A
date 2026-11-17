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
    """Ensemble TX có decay, kiểm chứng walk-forward và chống kẹt.

    Lưu ý: kết quả xúc xắc độc lập nên streak/alternation chỉ là tín hiệu
    thống kê thực nghiệm, không phải quy luật làm xác suất đổi chiều.
    """
    NAMES = ("statistical", "markov_1", "markov_2", "streak", "alternation", "contrarian")
    LEARNED = NAMES
    N = len(NAMES)
    HALF_LIFE = 10
    DECAY = 0.5 ** (1.0 / HALF_LIFE)
    SKIP_BAND = (0.46, 0.54)
    GROUPS = {
        "statistical": "Statistical", "markov_1": "Pattern",
        "markov_2": "Pattern", "streak": "Pattern",
        "alternation": "Pattern", "contrarian": "Contrarian"
    }

    def __init__(self):
        self.r = deque(maxlen=LEARN_WIN)  # 1 = Tài, 0 = Xỉu; chỉ giữ 30 phiên gần nhất
        self.pt = deque(maxlen=LEARN_WIN)
        # Giữ PointLearner để tương thích trường tu_hoc của API cũ.
        self.pl = PointLearner()
        self.loss_streak = 0
        self.skip_due = False           # chỉ bật sau 3 lệnh thua liên tiếp
        self.skip_triggered = False     # mỗi chuỗi thua chỉ ép SKIP một lần
        self.loss_sum = {k: 0.0 for k in self.NAMES}
        self.loss_mass = {k: 0.0 for k in self.NAMES}
        self.w = {k: 1.0 / self.N for k in self.NAMES}
        self.hit = deque(maxlen=30)
        self.t = 0
        self.temp = 1.0
        self.cap = 0.0
        self.last_reset = False

    @staticmethod
    def _clip(p):
        return max(0.02, min(0.98, float(p)))

    @staticmethod
    def _logloss(p, y):
        p = max(0.02, min(0.98, float(p)))
        return -math.log(p if y else 1.0 - p)

    @staticmethod
    def _rate(weighted_yes, weighted_total, prior=0.5, strength=4.0):
        # Bayesian smoothing: dữ liệu ít thì gần 50%, không phóng đại mẫu nhỏ.
        den = weighted_total + strength
        return (weighted_yes + strength * prior) / den if den else prior

    def _weighted_transitions(self, predicate):
        seq = list(self.r)
        yes = total = 0.0
        # Mỗi cặp (context -> kết quả kế tiếp) được decay theo độ mới của target.
        for i in range(1, len(seq)):
            if predicate(seq, i):
                age = len(seq) - 1 - i
                wt = self.DECAY ** age
                total += wt
                yes += wt * seq[i]
        return yes, total

    def _weighted_same_after_streak(self):
        """P(kết quả kế tiếp cùng phía với bệt trước đó | bệt >= 2)."""
        seq = list(self.r)
        same = total = 0.0
        for i in range(1, len(seq)):
            run_before = self._run_before(seq, i)
            if run_before >= 2:
                wt = self.DECAY ** (len(seq) - 1 - i)
                total += wt
                if seq[i] == seq[i-1]:
                    same += wt
        return same, total

    def _experts(self):
        seq = list(self.r)
        base = {k: 0.5 for k in self.NAMES}
        if len(seq) < 2:
            return base

        # Statistical: tỷ lệ Tài/Xỉu có decay; prior lý thuyết 3 xúc xắc là 50/50.
        yes = total = 0.0
        for age, value in enumerate(reversed(seq)):
            wt = self.DECAY ** age
            total += wt
            yes += wt * value
        base["statistical"] = self._rate(yes, total, 0.5, 8.0)

        last = seq[-1]
        y, n = self._weighted_transitions(lambda a, i: a[i-1] == last)
        base["markov_1"] = self._rate(y, n, 0.5, 5.0)

        if len(seq) >= 2:
            pair = tuple(seq[-2:])
            y, n = self._weighted_transitions(lambda a, i: i >= 2 and tuple(a[i-2:i]) == pair)
            base["markov_2"] = self._rate(y, n, 0.5, 5.0)

            if pair[0] != pair[1]:
                y, n = self._weighted_transitions(lambda a, i: i >= 2 and a[i-2] != a[i-1])
                base["alternation"] = self._rate(y, n, 0.5, 5.0)
            else:
                base["alternation"] = 0.5

        run = 1
        for j in range(len(seq)-2, -1, -1):
            if seq[j] == last: run += 1
            else: break
        y, n = self._weighted_transitions(lambda a, i: self._run_before(a, i) == run)
        base["streak"] = self._rate(y, n, 0.5, 4.0)

        # Contrarian: xác suất thực nghiệm đi ngược sau bệt >= 2; không mặc định bệt phải gãy.
        same, n = self._weighted_same_after_streak()
        p_same = self._rate(same, n, 0.5, 5.0)
        p_opposite = 1.0 - p_same
        base["contrarian"] = p_opposite
        return {k: self._clip(v) for k, v in base.items()}

    @staticmethod
    def _run_before(seq, i):
        if i <= 0: return 0
        side = seq[i-1]; run = 1
        j = i - 2
        while j >= 0 and seq[j] == side:
            run += 1; j -= 1
        return run

    def _update_weights(self):
        scores = {}
        for k in self.NAMES:
            scores[k] = self.loss_sum[k] / self.loss_mass[k] if self.loss_mass[k] > 1e-9 else 0.0
        trained = [scores[k] for k in self.NAMES if self.loss_mass[k] > 0.05]
        baseline = min(trained) if trained else 0.0
        raw = {k: math.exp(max(-5.0, min(0.0, -(scores[k] - baseline) * 1.4))) for k in self.NAMES}
        total = sum(raw.values()) or 1.0
        floor = 0.06
        self.w = {k: (1-floor) * raw[k] / total + floor / self.N for k in self.NAMES}

    def _reset_learning(self):
        # Chỉ reset bộ chấm điểm expert; giữ chuỗi quan sát để không quên dữ liệu thật.
        self.loss_sum = {k: 0.0 for k in self.NAMES}
        self.loss_mass = {k: 0.0 for k in self.NAMES}
        self.w = {k: 1.0 / self.N for k in self.NAMES}
        self.hit.clear()
        self.loss_streak = 0
        self.skip_due = False
        self.skip_triggered = False
        self.temp = 1.0
        self.last_reset = True

    def predict(self):
        votes = self._experts()
        # Trung bình log-odds giúp xác suất không bị expert cực đoan kéo về 0/1.
        z = sum(self.w[k] * math.log(votes[k] / (1.0-votes[k])) for k in self.NAMES)
        p = 1.0 / (1.0 + math.exp(-max(-8.0, min(8.0, z))))
        run = 0
        seq = list(self.r)
        if seq:
            last = seq[-1]; run = 1
            for v in reversed(seq[:-1]):
                if v == last: run += 1
                else: break
        forced_skip = self.skip_due
        if forced_skip:
            side = None
            reason = "AI đã thua liên tiếp 3 lần: tạm SKIP đúng một phiên để ngắt chu kỳ quyết định."
        elif self.SKIP_BAND[0] <= p <= self.SKIP_BAND[1]:
            side = None
            reason = "Xác suất tổng hợp nằm trong vùng 46–54%: tín hiệu quá cân bằng, không vào lệnh."
        else:
            side = "TAI" if p > 0.5 else "XIU"
            reason = (f"Bệt hiện tại {run} phiên {'Tài' if seq and seq[-1] else 'Xỉu' if seq else 'chưa đủ dữ liệu'}; "
                      f"p(Tài)={p:.1%}. Ensemble chọn {side}; streak/đảo chiều chỉ được tin theo dữ liệu đã kiểm chứng.")
        conf = round(max(p, 1-p) * 100)
        acc = sum(self.hit)/len(self.hit) if self.hit else None
        trained_losses = [self.loss_sum[k] / self.loss_mass[k]
                          for k in self.NAMES if self.loss_mass[k] > 1e-9]
        mean_loss = (round(sum(trained_losses) / len(trained_losses), 3)
                     if trained_losses else None)
        experts = {k: round(self.w[k], 4) for k in self.NAMES}
        did_reset = self.last_reset
        self.last_reset = False
        return {
            # Trường mới theo yêu cầu
            "side": side, "confidence": conf, "p_tai": round(p, 6),
            "reasoning": reason, "experts": experts,
            "expert_votes": votes, "groups": dict(self.GROUPS),
            "forced_skip": forced_skip,
            # Giữ đầy đủ các khóa mà app/API phiên bản cũ từng xuất ra.
            "p": p, "z": z, "ze": z, "conf": conf, "skip": side is None,
            "ex": votes, "ex_short": dict(votes), "ex_long": dict(votes),
            "p_short": p, "p_long": p,
            "w": dict(self.w), "w_short": dict(self.w), "w_long": dict(self.w),
            "meta_w": {"ensemble": 1.0}, "temp": round(self.temp, 3),
            "ramp": 1.0, "governor": 1.0, "entropy": None,
            "acc30": round(acc, 3) if acc is not None else None,
            "pl": self.pl.summary(),
            "loss_streak": self.loss_streak, "run_len": run,
            "nhom": {"loss_streak": self.loss_streak, "hard_reset": did_reset,
                     "loss_tu_hoc": mean_loss, "loss_thuat_toan": None, "tran": self.cap},
        }

    def learn(self, pk, y: bool):
        """Chấm dự đoán phiên vừa đóng; gọi trước observe(row)."""
        if not isinstance(pk, dict): return
        side = pk.get("side")
        if side not in ("TAI", "XIU"):
            # SKIP trung tính không ảnh hưởng chuỗi thua; SKIP bắt buộc chỉ
            # đóng cooldown đã kích hoạt sau đúng 3 lệnh thua.
            if pk.get("forced_skip"):
                self.skip_due = False
                self.skip_triggered = True
            return
        y = bool(y)
        votes = pk.get("expert_votes") or pk.get("ex") or {}
        for k in self.NAMES:
            self.loss_sum[k] *= self.DECAY
            self.loss_mass[k] *= self.DECAY
            self.loss_sum[k] += self._logloss(votes.get(k, 0.5), y)
            self.loss_mass[k] += 1.0
        self._update_weights()
        won = (side == "TAI") == y
        self.hit.append(1 if won else 0)
        if won:
            self.loss_streak = 0
            self.skip_due = False
            self.skip_triggered = False
        else:
            self.loss_streak += 1
            if self.loss_streak >= 3 and not self.skip_triggered:
                self.skip_due = True
        self.t += 1
        if self.loss_streak >= 5:
            self._reset_learning()

    def observe(self, row):
        if not isinstance(row, dict): return
        res = row.get("result")
        point = row.get("point")
        try: point = int(point)
        except (TypeError, ValueError): point = None
        if point is not None and not 3 <= point <= 18: point = None
        if res not in ("TAI", "XIU"):
            if point is None: return
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
        "trang_thai": ("skip" if pk.get("side") is None else ("win" if win else "lose")),
        "icon":      ("⏭️" if pk.get("side") is None else ICON["win" if win else "lose"]),
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
        win = pk["side"] == row.get("result") if pk.get("side") else False
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
            win = (du == row["result"]) if du else False
            self.brain.learn(pk, row["result"] == "TAI")
            self.hist.append(entry(row, pk, win, is_live))
            self.brain.observe(row)  # cập nhật điểm sau khi chấm dự đoán
            self.last = {
                "phien": row["id"], "xuc_xac": row["dices"],
                "tong": row["point"], "ket_qua": row["result"],
                "du_doan": du, "trang_thai": ("skip" if du is None else ("win" if win else "lose")),
            }
            self.last_id = row["id"]; self.pending = None
        self._pend()

    def _pend(self):
        pk = self.brain.predict()
        self.pending = {
            "phien":    self.last_id + 1,
            "du_doan":  pk["side"],
            "do_tin_cay": pk["confidence"],
            "p_tai":    round(pk["p_tai"], 3),
            "pk":       pk,
        }

TABLES = {c: Table(c) for c in URLS}

# ── Helpers thống kê ───────────────────────────────────────────────────────────
def stats(items):
    w = sum(1 for h in items if h["trang_thai"] == "win")
    l = sum(1 for h in items if h["trang_thai"] == "lose")
    sk = sum(1 for h in items if h["trang_thai"] == "skip")
    decided = w + l
    return {"win": w, "lose": l, "skip": sk, "ty_le": round(w * 100.0 / decided, 1) if decided else 0.0}

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
def _legacy_api_gate():
    """Khi bật mã bảo vệ, khóa đường dẫn cũ để không thể bypass bằng /tx/..."""
    with _aprot_lock:
        protected = _aprot["enabled"]
    if protected:
        return out({"ok": False, "loi": "not_found", "thong_bao": "Không tìm thấy"}, 404)
    return None

@app.get("/tx/<code>")
def api_main(code):
    blocked = _legacy_api_gate()
    if blocked: return blocked
    t, err = table_or_error(code); return err or out(view_main(t))

@app.get("/history/tx/<code>")
def api_history(code):
    blocked = _legacy_api_gate()
    if blocked: return blocked
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
    pd = t.pending
    hist = list(t.hist)
    live_real = [h for h in hist if h.get("live")]
    live = live_real if live_real else hist[-5:]
    l30 = hist[-30:]
    pk = pd["pk"] if pd else {}
    ex = [{"name": k, "p": round(pk.get("expert_votes", {}).get(k, 0.5), 4),
           "w": round(pk.get("experts", {}).get(k, 1.0/Brain.N), 4),
           "group": pk.get("groups", {}).get(k, "Expert")}
          for k in Brain.NAMES] if pd else []
    return {
        "code": t.code, "name": t.name, "enabled": t.enabled, "ready": t.ready,
        "err": t.err, "ms": t.ms, "n_fetch": t.n_fetch,
        "age": round(time.time() - t.ok_ts) if t.ok_ts else None,
        "last": t.last,
        "pending": {
            "phien": pd["phien"], "du_doan": pd["du_doan"],
            "conf": pd["do_tin_cay"], "p_tai": pd["p_tai"],
            "temp": pk.get("temp", 1.0), "reasoning": pk.get("reasoning", ""),
            "loss_streak": pk.get("loss_streak", 0),
            "run_len": pk.get("run_len", 0), "skip": pk.get("skip", False),
            "hard_reset": pk.get("nhom", {}).get("hard_reset", False),
        } if pd else None,
        "experts": ex, "st_all": stats(hist), "st_live": stats(live),
        "st_30": stats(l30), "hist": hist[::-1],
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
    action = request.form.get("action", "")
    if not action:
        try:
            body = request.get_json(silent=True) or {}
            action = body.get("action", "") if isinstance(body, dict) else ""
        except Exception:
            action = ""
    if action not in ("enable", "disable"):
        return out({"ok": False, "loi": "bad_request"}, 400)
    with _aprot_lock:
        cur_code = _aprot["code"]
        if action == "enable" and not cur_code:
            return out({"ok": False, "loi": "code_required"}, 400)
        _aprot["enabled"] = (action == "enable")
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
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#070b14"><title>PAW TX // NEURAL CONTROL</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{color-scheme:dark;--bg:#070b14;--panel:#0d1422;--panel2:#111c2e;--line:#203047;--txt:#e5f0ff;--muted:#7f93ad;--cyan:#38e8ff;--blue:#538cff;--green:#37e6a0;--red:#ff5578;--amber:#ffc66d;--purple:#b28aff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 12% -5%,#10264a 0,transparent 36%),radial-gradient(ellipse at 90% 20%,#21133c 0,transparent 30%),var(--bg);color:var(--txt);font:13px/1.55 Inter,system-ui,sans-serif;min-height:100vh}button{font:inherit;cursor:pointer}.mono{font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}.top{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px max(18px,calc((100vw - 1440px)/2));background:#080e1beF;border-bottom:1px solid var(--line);backdrop-filter:blur(18px)}.brand{display:flex;align-items:center;gap:12px;font-weight:900;letter-spacing:.08em}.logo{width:38px;height:38px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(135deg,#1678ff,#a044ff);box-shadow:0 0 24px #397aff55;font-size:19px}.sub{font:9px 'JetBrains Mono';color:var(--cyan);letter-spacing:.18em}.right,.actions,.chips{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.status{display:flex;align-items:center;gap:7px;color:var(--muted);font:10px 'JetBrains Mono'}.dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 12px var(--green)}.btn{border:1px solid var(--line);border-radius:9px;padding:8px 12px;color:var(--txt);background:#111d30}.btn:hover{border-color:var(--cyan);box-shadow:0 0 14px #38e8ff22}.btn.primary{background:#123b59;border-color:#1e8ba8;color:#9cf5ff}.btn.danger{color:#ff9db0}.wrap{max-width:1440px;margin:auto;padding:22px 18px 60px}.heading{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:8px 0 18px}.eyebrow{color:var(--cyan);font:10px 'JetBrains Mono';letter-spacing:.18em}.heading h1{font-size:clamp(21px,4vw,32px);margin:5px 0 0;letter-spacing:-.05em}.tabs{display:flex;gap:7px;margin:0 0 18px;overflow:auto}.tab{border:1px solid var(--line);background:#0b1320;color:var(--muted);padding:9px 13px;border-radius:9px;white-space:nowrap}.tab.active{color:var(--cyan);border-color:#267c98;background:#102637}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.card{background:linear-gradient(145deg,#101a2aee,#0b1220f5);border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 15px 45px #0005;min-width:0}.cardhead{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:14px}.cardhead b{font-size:15px}.muted{color:var(--muted)}.hero{position:relative;overflow:hidden;border:1px solid #284767;border-radius:14px;padding:20px;background:radial-gradient(circle at 85% 10%,#173c5c,transparent 45%),linear-gradient(125deg,#111f35,#111327)}.hero:after{content:'';position:absolute;inset:auto -10% -70% 30%;height:130px;background:#28cfff12;filter:blur(35px);pointer-events:none}.hero-label{color:#86a9c9;font:10px 'JetBrains Mono';letter-spacing:.16em}.side{font-size:clamp(35px,6vw,58px);font-weight:900;letter-spacing:-.07em;line-height:1.2;margin:8px 0}.side.TAI{color:var(--red);text-shadow:0 0 25px #ff557866}.side.XIU{color:var(--cyan);text-shadow:0 0 25px #38e8ff66}.side.SKIP{color:var(--amber);text-shadow:0 0 20px #ffc66d55}.meter{height:8px;border-radius:99px;background:#1b2a3d;overflow:hidden;margin:10px 0}.meter i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--blue),var(--cyan));box-shadow:0 0 12px #38e8ff88}.reason{margin-top:14px;padding:12px 14px;border:1px solid #263c55;border-left:3px solid var(--purple);border-radius:10px;background:#0a1423;color:#b8cce3;font-size:12px}.reason strong{display:block;color:var(--purple);font:10px 'JetBrains Mono';letter-spacing:.12em;margin-bottom:5px}.chips{margin-top:13px}.chip{background:#0b1422;border:1px solid var(--line);border-radius:9px;padding:9px 12px;min-width:95px}.chip b{display:block;font:700 17px 'JetBrains Mono'}.chip small{color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.1em}.experts{display:grid;gap:12px}.expert{display:grid;grid-template-columns:minmax(90px,130px) 1fr 72px;align-items:center;gap:10px}.expert-name{font-size:11px;color:#b8c9dd}.track{height:7px;background:#1b2a3d;border-radius:99px;overflow:hidden}.track i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#526fff,#38e8ff)}.expert-meta{text-align:right;font:10px 'JetBrains Mono';color:var(--muted)}.group{font:9px 'JetBrains Mono';color:var(--purple);text-transform:uppercase;letter-spacing:.1em}.tablewrap{overflow:auto;border:1px solid var(--line);border-radius:12px}table{border-collapse:collapse;width:100%;min-width:650px}th,td{padding:11px 12px;text-align:left;border-bottom:1px solid #1b293b;font-size:11px}th{font:9px 'JetBrains Mono';color:var(--muted);letter-spacing:.12em;background:#0a1320;position:sticky;top:0}tr:last-child td{border:0}tr.win{background:#10312655}tr.lose{background:#39172555}tr.skip{background:#3b2c1655}.pill{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:3px 8px;font:9px 'JetBrains Mono'}.pill.TAI{color:var(--red);border-color:#713044}.pill.XIU{color:var(--cyan);border-color:#1b6270}.pill.win{color:var(--green)}.pill.lose{color:var(--red)}.pill.skip{color:var(--amber)}.tablebox{display:grid;gap:16px}.hide{display:none!important}.empty{color:var(--muted);text-align:center;padding:25px}.protect{display:grid;grid-template-columns:1fr 1fr;gap:16px}.code{font:700 25px 'JetBrains Mono';letter-spacing:.2em;color:var(--cyan);margin:15px 0;word-break:break-all}.toast{position:fixed;bottom:20px;right:20px;background:#14243a;border:1px solid #34506f;padding:12px 16px;border-radius:10px;display:none;z-index:20;box-shadow:0 10px 35px #0009}.foot{color:#52677f;text-align:center;font:9px 'JetBrains Mono';margin-top:25px;letter-spacing:.1em}
@media(max-width:850px){.grid,.protect{grid-template-columns:1fr}.top{padding:12px 14px}.wrap{padding:16px 12px 40px}.expert{grid-template-columns:95px 1fr 66px}.heading{align-items:start;flex-direction:column}}@media(max-width:480px){.brand{font-size:12px}.right .status{display:none}.card{padding:14px}.hero{padding:16px}.side{font-size:42px}.btn{padding:7px 9px;font-size:11px}}
</style></head><body>
<header class="top"><div class="brand"><div class="logo">⌁</div><div>PAW NEURAL <div class="sub">TX // AI CONTROL CENTER</div></div></div><div class="right"><span class="status"><i class="dot" id="apiDot"></i><span id="apiStatus">CONNECTING</span></span><span class="status">SYNC <b id="countdown">4</b>s</span><button class="btn" onclick="load()">↻ Làm mới</button><a class="btn" href="/admin/logout">Thoát</a></div></header>
<main class="wrap"><div class="heading"><div><div class="eyebrow">NEURAL NETWORK / LIVE MONITOR</div><h1>Bộ não dự đoán Tài / Xỉu</h1></div><div class="muted mono" id="updated">Đang khởi tạo dữ liệu…</div></div>
<nav class="tabs"><button class="tab active" onclick="tab('all',this)">Tổng quan</button><button class="tab" onclick="tab('history',this)">Lịch sử 50 phiên</button><button class="tab" onclick="tab('protection',this)">Bảo vệ API</button></nav>
<section id="view-all"><div class="grid" id="boards"></div></section>
<section id="view-history" class="hide"><div class="tablebox" id="historyBoards"></div></section>
<section id="view-protection" class="hide"><div class="protect"><div class="card"><div class="cardhead"><b>API ACCESS GUARD</b><span class="pill" id="protState">UNKNOWN</span></div><p class="muted">Tạo mã đường dẫn 6 ký tự và bật/tắt bảo vệ endpoint.</p><div class="code" id="codeDisplay">••••••</div><div class="actions"><button class="btn primary" onclick="genCode()">Tạo mã mới</button><button class="btn" onclick="copyCode()">Copy mã</button></div><div class="actions" style="margin-top:10px"><button class="btn primary" onclick="setProt('enable')">Bật bảo vệ</button><button class="btn danger" onclick="setProt('disable')">Tắt bảo vệ</button><button class="btn" onclick="revokeCode()">Thu hồi</button></div><p class="muted mono" id="urlPreview" style="margin-top:14px;word-break:break-all"></p></div><div class="card"><b>Trạng thái bảo vệ</b><p class="muted" id="protInfo" style="margin-top:12px">Đang tải…</p><p class="muted" style="margin-top:12px">Mã 6 ký tự là lớp bảo vệ đường dẫn, không thay thế HTTPS hoặc xác thực mạnh. Không chia sẻ URL có mã công khai.</p></div></div></section>
<div class="foot">PAW TX // DECAY HALF-LIFE 10 // WALK-FORWARD LEARNING // NO GUARANTEED EDGE</div></main><div class="toast" id="toast"></div>
<script>
const CSRF="__CSRF__";let DATA=[],activeTab='all',timer=4,prot={enabled:false,has_code:false,code:''};const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function toast(s){$('toast').textContent=s;$('toast').style.display='block';clearTimeout(window._toast);window._toast=setTimeout(()=>$('toast').style.display='none',2600)}
function tab(name,btn){activeTab=name;['all','history','protection'].forEach(x=>$('view-'+x).classList.toggle('hide',x!==name));document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===btn));if(name==='protection')loadProt()}
function side(s){return s?`<span class="pill ${s}">${s==='TAI'?'TÀI':'XỈU'}</span>`:'<span class="pill skip">SKIP</span>'}
function board(t){const p=t.pending||{},s=p.du_doan,cls=s||'SKIP';const experts=t.experts||[];return `<article class="card"><div class="cardhead"><div><b>${esc(t.name)} // ${esc(t.code).toUpperCase()}</b><div class="muted mono">${t.ready?'UPSTREAM ONLINE':'WAITING'} · ${t.ms||0}ms · ${t.age??'—'}s</div></div><div class="actions"><button class="btn" onclick="act('${t.code}','refresh')">↻</button><button class="btn" onclick="act('${t.code}','relearn')">🧠 Học lại</button><button class="btn ${t.enabled?'danger':'primary'}" onclick="act('${t.code}','${t.enabled?'off':'on'}')">${t.enabled?'Tắt':'Bật'}</button></div></div><div class="hero"><div class="hero-label">NEXT SESSION // #${p.phien??'—'}</div><div class="side ${cls}">${s==='TAI'?'TÀI':s==='XIU'?'XỈU':'NO BET / SKIP'}</div><div class="muted">Độ tự tin <b>${p.conf??0}%</b> · P(Tài) <b>${((p.p_tai??.5)*100).toFixed(2)}%</b></div><div class="meter"><i style="width:${Math.max(0,Math.min(100,p.conf??0))}%"></i></div><div class="reason"><strong>AI REASONING / SUY NGHĨ CỦA AI</strong>${esc(p.reasoning||'Đang chờ đủ dữ liệu để phân tích.')}</div><div class="chips"><div class="chip"><b>${p.loss_streak??0}</b><small>Loss streak</small></div><div class="chip"><b>${p.run_len??0}</b><small>Chuỗi hiện tại</small></div><div class="chip"><b>${t.st_30?.ty_le??0}%</b><small>Accuracy 30</small></div><div class="chip"><b>${t.st_30?.win??0}/${t.st_30?.lose??0}</b><small>Win / Loss</small></div></div></div><div style="margin-top:17px"><div class="cardhead"><b>EXPERTS PANEL</b><span class="group">WEIGHT / VOTE P(TÀI)</span></div><div class="experts">${experts.map(x=>`<div><div class="expert"><span class="expert-name">${esc(x.name.replaceAll('_',' '))}</span><div class="track"><i style="width:${Math.max(0,Math.min(100,x.w*100))}%"></i></div><span class="expert-meta">${(x.w*100).toFixed(1)}%</span></div><div class="group">${esc(x.group)} · vote ${(x.p*100).toFixed(1)}% Tài</div></div>`).join('')}</div></div><div class="actions" style="margin-top:16px"><span class="muted mono">LAST: #${t.last?.phien??'—'} ${side(t.last?.ket_qua)}</span><span class="muted mono">${esc((t.last?.xuc_xac||[]).join('-'))} = ${t.last?.tong??'—'}</span></div>${t.err?`<p class="muted" style="color:var(--red);margin-top:10px">${esc(t.err)}</p>`:''}</article>`}
function histTable(t){const rows=t.hist||[];return `<section class="card"><div class="cardhead"><b>LỊCH SỬ // ${esc(t.name)}</b><span class="muted mono">${rows.length} phiên gần nhất</span></div><div class="tablewrap"><table><thead><tr><th>Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>AI dự đoán</th><th>Trạng thái</th></tr></thead><tbody>${rows.length?rows.map(h=>`<tr class="${h.trang_thai}"><td class="mono">#${h.phien}</td><td class="mono">${esc((h.xuc_xac||[]).join('-'))} / ${h.tong??'—'}</td><td>${side(h.ket_qua)}</td><td>${side(h.du_doan)}</td><td><span class="pill ${h.trang_thai}">${h.trang_thai==='win'?'THẮNG':h.trang_thai==='lose'?'THUA':'SKIP'}</span></td></tr>`).join(''):'<tr><td colspan="5" class="empty">Chưa có lịch sử</td></tr>'}</tbody></table></div></section>`}
function draw(){ $('boards').innerHTML=DATA.map(board).join('');$('historyBoards').innerHTML=DATA.map(histTable).join('');$('apiStatus').textContent=DATA.every(x=>x.ready)?'API ONLINE':'API DEGRADED';$('apiDot').style.background=DATA.every(x=>x.ready)?'var(--green)':'var(--amber)';$('updated').textContent='UPDATED '+new Date().toLocaleTimeString('vi-VN'); }
async function load(){try{const r=await fetch('/admin/data',{cache:'no-store'});if(r.status===401){location.href='/admin';return}const j=await r.json();if(!j.ok)throw Error(j.loi||'API error');DATA=j.tables||[];draw();timer=4}catch(e){$('apiStatus').textContent='API ERROR';$('apiDot').style.background='var(--red)';$('updated').textContent='FETCH ERROR: '+e.message}}
async function act(c,a){try{const r=await fetch(`/admin/act/${c}/${a}`,{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();toast(j.ok?'Đã thực hiện '+a:'Lỗi '+(j.loi||''));load()}catch(e){toast('Không thể kết nối máy chủ')}}
async function loadProt(){try{const r=await fetch('/admin/aprot/status');const j=await r.json();prot={...prot,enabled:j.enabled,has_code:j.has_code};$('protState').textContent=prot.enabled?'PROTECTED':'UNPROTECTED';$('protInfo').textContent=`Bảo vệ: ${prot.enabled?'BẬT':'TẮT'} · ${prot.has_code?'Đã có mã':'Chưa có mã'}`;$('codeDisplay').textContent=prot.code|| (prot.has_code?'••••••':'Chưa tạo');}catch(e){$('protInfo').textContent='Lỗi tải trạng thái'}}
async function genCode(){try{const r=await fetch('/admin/aprot/gen',{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();if(!j.ok)throw Error(j.loi);prot.code=j.code;prot.has_code=true;$('codeDisplay').textContent=j.code;$('urlPreview').textContent=location.origin+'/'+j.code+'/tx/hu';toast('Đã tạo mã mới');loadProt()}catch(e){toast('Tạo mã thất bại')}}
async function setProt(action){if(action==='enable'&&!prot.has_code){toast('Tạo mã trước');return}try{const fd=new FormData();fd.append('action',action);const r=await fetch('/admin/aprot/set',{method:'POST',headers:{'X-CSRF-Token':CSRF},body:fd});const j=await r.json();if(!j.ok)throw Error(j.loi);toast(action==='enable'?'Đã bật bảo vệ':'Đã tắt bảo vệ');loadProt()}catch(e){toast('Không cập nhật được')}}
async function revokeCode(){if(!confirm('Thu hồi mã và tắt bảo vệ?'))return;try{const r=await fetch('/admin/aprot/revoke',{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();if(!j.ok)throw Error(j.loi);prot={enabled:false,has_code:false,code:''};$('urlPreview').textContent='';toast('Đã thu hồi mã');loadProt()}catch(e){toast('Thu hồi thất bại')}}
function copyCode(){if(!prot.code)return toast('Chưa có mã');navigator.clipboard.writeText(prot.code).then(()=>toast('Đã copy mã')).catch(()=>toast('Clipboard không khả dụng'))}
setInterval(()=>{timer=Math.max(0,timer-1);$('countdown').textContent=timer;if(timer===0){load();timer=4}},1000);load();
</script></body></html>"""

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
