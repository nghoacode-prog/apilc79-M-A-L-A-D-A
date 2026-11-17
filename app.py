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
LEARN_WIN      = 50     # CỬA SỔ HỌC: 50 phiên — đủ dữ liệu, không overfit ngắn
HALF_LIFE      = 18     # decay chậm hơn → phiên cũ vẫn có trọng số tốt
PRIOR_STRENGTH = 2.0    # prior xúc xắc đều, nhẹ hơn để dữ liệu học chi phối hơn

ICON       = {"win": "✅", "lose": "❌", "cho": "⏳"}
VN         = timezone(timedelta(hours=7))
STATE_FILE = os.getenv("STATE_FILE", "/tmp/paw_tx_toggles.json")
CFG_FILE   = os.getenv("CFG_FILE",   "/tmp/paw_tx_cfg.json")
HISTORY_FILE = os.getenv("HISTORY_FILE", "/tmp/paw_tx_history.json")
_history_lock = threading.Lock()

# ── API Access Protection ──────────────────────────────────────────────────────
# Trạng thái bảo vệ — load từ file để bền vững qua restart
_aprot = {"enabled": False, "code": ""}   # mutable dict, bảo vệ bởi _aprot_lock
_aprot_lock = threading.Lock()

# Rate limit: IP → [timestamps] cho truy cập sai mã
_code_fails: dict = {}   # ip → list[float]
_code_blocked_until: dict = {}
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
    if _code_blocked_until.get(ip, 0) > now:
        return False
    times = [t for t in _code_fails.get(ip, []) if now - t < _CODE_WINDOW]
    _code_fails[ip] = times
    if len(times) >= _CODE_MAX_TRIES:
        _code_blocked_until[ip] = now + _CODE_BACKOFF
        return False
    return True

def _record_code_fail(ip: str):
    now = time.time()
    times = [t for t in _code_fails.get(ip, []) if now - t < _CODE_WINDOW]
    times.append(now)
    _code_fails[ip] = times
    if len(times) >= _CODE_MAX_TRIES:
        _code_blocked_until[ip] = now + _CODE_BACKOFF

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
    """Học tổng điểm có decay; chỉ nhận phiên đã qua kiểm tra dữ liệu."""

    def __init__(self):
        self.decay = 0.5 ** (1.0 / HALF_LIFE)
        self.hist = {s: 0.0 for s in range(3, 19)}
        self.cond = {b: {s: 0.0 for s in range(3, 19)} for b in "LMH"}
        self.cond_n = {b: 0.0 for b in "LMH"}
        self.trans = {b: [0.0, 0.0] for b in "LMH"}
        self.run = {}
        self.hist_n = 0.0
        self.prev_pt = None
        self.last_side = None
        self.run_len = 0
        self.n = 0

    @staticmethod
    def _valid_dices(dices, point):
        if dices is None:
            return True
        if not isinstance(dices, (list, tuple)) or len(dices) != 3:
            return False
        try:
            ds = [int(x) for x in dices]
        except (TypeError, ValueError):
            return False
        return all(1 <= x <= 6 for x in ds) and sum(ds) == point

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
        for cell in self.run.values():
            cell[0] *= d
            cell[1] *= d
        self.hist_n *= d

    def observe(self, point, side, dices=None):
        """Ghi nhận một phiên; bỏ qua nếu point/dices không nhất quán."""
        try:
            point = int(point)
        except (TypeError, ValueError):
            return False
        if point < 3 or point > 18 or side not in ("TAI", "XIU"):
            return False
        if not self._valid_dices(dices, point):
            return False

        self._decay_all()
        self.hist[point] += 1.0
        self.hist_n += 1.0

        if self.prev_pt is not None:
            bucket = _pt_bucket(self.prev_pt)
            self.cond[bucket][point] += 1.0
            self.cond_n[bucket] += 1.0
            self.trans[bucket][0 if side == "TAI" else 1] += 1.0

        run_key = min(self.run_len, 6)
        cell = self.run.setdefault(run_key, [0.0, 0.0])
        cell[0 if side == "TAI" else 1] += 1.0

        self.run_len = self.run_len + 1 if self.last_side == side else 1
        self.last_side = side
        self.prev_pt = point
        self.n += 1
        return True

    def _post(self, counts, prior_scale):
        total = tai = 0.0
        for score in range(3, 19):
            value = counts[score] + prior_scale * _PT_PRIOR[score]
            total += value
            if score >= 11:
                tai += value
        return tai / total if total > 0 else _PT_BASE

    def experts(self):
        out = {"pt_hist": 0.5, "pt_cond": 0.5, "pt_trans": 0.5, "pt_run": 0.5}
        if self.n < 3:
            return out
        density = min(1.0, self.hist_n / float(LEARN_WIN)) ** 0.6
        out["pt_hist"] = _shrink(self._post(self.hist, PRIOR_STRENGTH), density)

        bucket = _pt_bucket(self.prev_pt)
        if bucket is not None:
            kc = density * min(1.0, self.cond_n[bucket] / 8.0)
            out["pt_cond"] = _shrink(
                self._post(self.cond[bucket], PRIOR_STRENGTH * 0.5), kc
            )
            tai_count, xiu_count = self.trans[bucket]
            count = tai_count + xiu_count
            kt = density * min(1.0, count / 6.0)
            p_transition = (tai_count + 3.0 * _PT_BASE) / (count + 3.0)
            out["pt_trans"] = _shrink(p_transition, kt)

        if self.last_side is not None:
            run_key = min(self.run_len, 6)
            tai_count, xiu_count = self.run.get(run_key, [0.0, 0.0])
            count = tai_count + xiu_count
            kr = density * min(1.0, count / 4.0)
            p_run = (tai_count + 1.0) / (count + 2.0)
            out["pt_run"] = _shrink(p_run, kr)
        return out

    def summary(self):
        bucket = _pt_bucket(self.prev_pt)
        return {
            "so_phien": round(self.hist_n, 1),
            "tong_truoc": self.prev_pt,
            "nhom": bucket,
            "bệt": self.run_len,
            "p_tai_diem": round(self._post(self.hist, PRIOR_STRENGTH), 3),
            "p_tai_nhom": round(
                self._post(self.cond[bucket], PRIOR_STRENGTH * 0.5), 3
            ) if bucket else None,
        }


class Brain:
    """Ensemble TX; có inverse mode, hard reset và kiểm tra dữ liệu đầu vào."""

    NAMES = (
        "statistical", "markov_1", "markov_2", "streak",
        "alternation", "contrarian",
        "pt_hist", "pt_cond", "pt_trans", "pt_run",
    )
    LEARNED = NAMES
    N = len(NAMES)
    DECAY = 0.5 ** (1.0 / HALF_LIFE)
    GROUPS = {
        "statistical": "Thống kê", "markov_1": "Chuỗi",
        "markov_2": "Chuỗi", "streak": "Chuỗi",
        "alternation": "Chuỗi", "contrarian": "Đảo chiều",
        "pt_hist": "Tổng điểm", "pt_cond": "Tổng điểm",
        "pt_trans": "Tổng điểm", "pt_run": "Tổng điểm",
    }

    def __init__(self):
        self.r = deque(maxlen=LEARN_WIN)
        self.pt = deque(maxlen=LEARN_WIN)
        self.pl = PointLearner()
        self.loss_sum = {k: 0.0 for k in self.NAMES}
        self.loss_mass = {k: 0.0 for k in self.NAMES}
        self.w = {k: 1.0 / self.N for k in self.NAMES}
        self.hit = deque(maxlen=30)
        self.baseline_hit = deque(maxlen=30)
        self.pred_sides = deque(maxlen=30)
        self.brier_hist = deque(maxlen=30)
        self.logloss_hist = deque(maxlen=30)
        self.t = 0
        self.temp = 1.0
        self.cap = 0.0
        self.loss_streak = 0
        self.inverse_mode = False
        self.inverse_win_streak = 0
        self.last_reset = False
        self.hard_reset = False
        # Lưu bản ghi hợp lệ để tái dựng mô hình sau hard reset.
        self.raw_history = deque(maxlen=30)

    @staticmethod
    def _clip(p):
        return max(0.03, min(0.97, float(p)))

    @staticmethod
    def _logloss(p, y):
        p = max(0.02, min(0.98, float(p)))
        return -math.log(p if y else 1.0 - p)

    @staticmethod
    def _rate(weighted_yes, weighted_total, prior=0.5, strength=4.0):
        den = weighted_total + strength
        return (weighted_yes + strength * prior) / den if den else prior

    @staticmethod
    def _run_before(seq, i):
        if i <= 0:
            return 0
        side = seq[i - 1]
        run = 1
        j = i - 2
        while j >= 0 and seq[j] == side:
            run += 1
            j -= 1
        return run

    def _weighted_transitions(self, predicate):
        seq = list(self.r)
        yes = total = 0.0
        for i in range(1, len(seq)):
            if predicate(seq, i):
                wt = self.DECAY ** (len(seq) - 1 - i)
                total += wt
                yes += wt * seq[i]
        return yes, total

    def _weighted_same_after_streak(self):
        seq = list(self.r)
        same = total = 0.0
        for i in range(1, len(seq)):
            if self._run_before(seq, i) >= 2:
                wt = self.DECAY ** (len(seq) - 1 - i)
                total += wt
                if seq[i] == seq[i - 1]:
                    same += wt
        return same, total

    def _seq_experts(self):
        seq = list(self.r)
        keys = ("statistical", "markov_1", "markov_2",
                "streak", "alternation", "contrarian")
        out = {k: 0.5 for k in keys}
        if len(seq) < 2:
            return out

        yes = total = 0.0
        for age, value in enumerate(reversed(seq)):
            wt = self.DECAY ** age
            total += wt
            yes += wt * value
        out["statistical"] = self._rate(yes, total, 0.5, 8.0)

        last = seq[-1]
        y, n = self._weighted_transitions(lambda a, i: a[i - 1] == last)
        out["markov_1"] = self._rate(y, n, 0.5, 5.0)

        pair = tuple(seq[-2:])
        y, n = self._weighted_transitions(
            lambda a, i: i >= 2 and tuple(a[i - 2:i]) == pair
        )
        out["markov_2"] = self._rate(y, n, 0.5, 5.0)
        if pair[0] != pair[1]:
            y, n = self._weighted_transitions(
                lambda a, i: i >= 2 and a[i - 2] != a[i - 1]
            )
            out["alternation"] = self._rate(y, n, 0.5, 5.0)

        run = 1
        for j in range(len(seq) - 2, -1, -1):
            if seq[j] == last:
                run += 1
            else:
                break
        y, n = self._weighted_transitions(
            lambda a, i: self._run_before(a, i) == run
        )
        out["streak"] = self._rate(y, n, 0.5, 4.0)
        same, n = self._weighted_same_after_streak()
        out["contrarian"] = 1.0 - self._rate(same, n, 0.5, 5.0)
        return out

    def _all_experts(self):
        combined = {**self._seq_experts(), **self.pl.experts()}
        return {k: self._clip(combined.get(k, 0.5)) for k in self.NAMES}

    def _update_weights(self):
        """
        Online exponential weighting with a neutral log-loss prior.
        Experts with little evidence are shrunk toward random (log-loss ln(2));
        an untrained expert can no longer receive an artificial advantage.
        """
        neutral = math.log(2.0)
        eta = 1.5
        scores = {}
        for key in self.NAMES:
            mass = self.loss_mass[key]
            observed = self.loss_sum[key] / mass if mass > 1e-9 else neutral
            # Regularize early estimates: 8 pseudo-observations at the neutral score.
            reliability = mass / (mass + 8.0)
            scores[key] = neutral + (observed - neutral) * reliability

        raw = {
            key: math.exp(max(-2.0, min(2.0, -eta * (scores[key] - neutral))))
            for key in self.NAMES
        }
        total = sum(raw.values()) or 1.0
        floor = 0.02
        self.w = {
            key: (1.0 - floor) * raw[key] / total + floor / self.N
            for key in self.NAMES
        }

    def _reset_weights(self):
        self.loss_sum = {k: 0.0 for k in self.NAMES}
        self.loss_mass = {k: 0.0 for k in self.NAMES}
        self.w = {k: 1.0 / self.N for k in self.NAMES}
        self.hit.clear()
        self.baseline_hit.clear()
        self.pred_sides.clear()
        self.brier_hist.clear()
        self.logloss_hist.clear()
        self.temp = 1.0

    def _hard_reset(self):
        """Reset trọng số và dựng lại phần học từ tối đa 30 bản ghi hợp lệ."""
        recent = list(self.raw_history)[-30:]
        self._reset_weights()
        self.r.clear()
        self.pt.clear()
        self.pl = PointLearner()
        for row in recent:
            self._observe_validated(row, keep_raw=False)
        self.loss_streak = 0
        self.inverse_mode = False
        self.inverse_win_streak = 0
        self.last_reset = True
        self.hard_reset = True

    @staticmethod
    def _validated_row(row):
        if not isinstance(row, dict):
            return None
        try:
            point = int(row.get("point"))
        except (TypeError, ValueError):
            return None
        if not 3 <= point <= 18:
            return None

        dices = row.get("dices")
        if dices is not None:
            if not isinstance(dices, (list, tuple)) or len(dices) != 3:
                return None
            try:
                ds = [int(x) for x in dices]
            except (TypeError, ValueError):
                return None
            if not all(1 <= x <= 6 for x in ds) or sum(ds) != point:
                return None

        result = row.get("result")
        if result not in ("TAI", "XIU"):
            result = "TAI" if point >= 11 else "XIU"
        # Tránh học nhãn kết quả mâu thuẫn với tổng điểm.
        expected = "TAI" if point >= 11 else "XIU"
        if result != expected:
            return None
        return {
            "id": row.get("id"),
            "point": point,
            "dices": list(dices) if dices is not None else [],
            "result": result,
        }

    def _observe_validated(self, row, keep_raw=True):
        point, result = row["point"], row["result"]
        self.r.append(1 if result == "TAI" else 0)
        self.pt.append(point)
        self.pl.observe(point, result, row.get("dices") or None)
        if keep_raw:
            self.raw_history.append(dict(row))

    def observe(self, row):
        clean = self._validated_row(row)
        if clean is None:
            return False
        self._observe_validated(clean)
        return True

    def predict(self):
        votes = self._all_experts()
        z_raw = sum(
            self.w[k] * math.log(votes[k] / (1.0 - votes[k]))
            for k in self.NAMES
        )
        p_raw = 1.0 / (1.0 + math.exp(-max(-8.0, min(8.0, z_raw))))
        # Không dùng chế độ đảo chiều tự động: nó thường overfit chuỗi thua ngắn.
        self.inverse_mode = False
        p = p_raw
        z = z_raw
        side = "TAI" if p >= 0.5 else "XIU"

        # Baseline đơn giản: tỷ lệ Tài/Xỉu trong quá khứ, có prior cân bằng.
        seq_for_baseline = list(self.r)
        baseline_p = (sum(seq_for_baseline) + 4.0 * 0.5) / (len(seq_for_baseline) + 4.0)
        baseline_side = "TAI" if baseline_p >= 0.5 else "XIU"

        seq = list(self.r)
        run = 0
        if seq:
            last = seq[-1]
            run = 1
            for value in reversed(seq[:-1]):
                if value == last:
                    run += 1
                else:
                    break

        pl_sum = self.pl.summary()
        conf = round(max(p, 1.0 - p) * 100)
        acc = sum(self.hit) / len(self.hit) if self.hit else None
        baseline_acc = (sum(self.baseline_hit) / len(self.baseline_hit)
                        if self.baseline_hit else None)
        tai_predictions = sum(1 for x in self.pred_sides if x == "TAI")
        xiu_predictions = len(self.pred_sides) - tai_predictions
        prediction_bias = (
            max(tai_predictions, xiu_predictions) / len(self.pred_sides)
            if self.pred_sides else None
        )
        brier = sum(self.brier_hist) / len(self.brier_hist) if self.brier_hist else None
        rolling_logloss = (
            sum(self.logloss_hist) / len(self.logloss_hist)
            if self.logloss_hist else None
        )
        losses = [
            self.loss_sum[k] / self.loss_mass[k]
            for k in self.NAMES if self.loss_mass[k] > 1e-9
        ]
        mean_loss = round(sum(losses) / len(losses), 3) if losses else None
        did_reset = self.last_reset or self.hard_reset
        pt_signal = pl_sum.get("p_tai_diem", 0.5)
        reason = (
            f"Bệt {run} phiên "
            f"{'Tài' if (seq and seq[-1]) else 'Xỉu' if seq else '—'}; "
            f"p(Tài) gốc={p_raw:.1%}, p(Tài) hiệu lực={p:.1%}; "
            f"baseline={baseline_side}; "
            f"chế độ đảo chiều=TẮT; "
            f"hard_reset={'CÓ' if self.hard_reset else 'KHÔNG'}; "
            f"tổng gần nhất={pl_sum.get('tong_truoc')}; "
            f"tín hiệu tổng điểm={pt_signal:.1%}; "
            f"loss streak={self.loss_streak}; chọn {side}."
        )
        result = {
            "side": side, "confidence": conf, "p_tai": round(p, 6),
            "reasoning": reason,
            "experts": {k: round(self.w[k], 4) for k in self.NAMES},
            "expert_votes": votes, "groups": dict(self.GROUPS),
            "forced_skip": False,
            "p": p, "z": z, "ze": z, "conf": conf, "skip": False,
            "ex": votes, "ex_short": dict(votes), "ex_long": dict(votes),
            "p_short": p, "p_long": p,
            "w": dict(self.w), "w_short": dict(self.w), "w_long": dict(self.w),
            "meta_w": {"ensemble": 1.0}, "temp": round(self.temp, 3),
            "ramp": 1.0, "governor": 1.0, "entropy": None,
            "acc30": round(acc, 3) if acc is not None else None,
            "evaluation": {
                "n": len(self.hit),
                "accuracy_30": round(acc, 4) if acc is not None else None,
                "baseline_accuracy_30": round(baseline_acc, 4) if baseline_acc is not None else None,
                "edge_vs_baseline": (
                    round(acc - baseline_acc, 4)
                    if acc is not None and baseline_acc is not None else None
                ),
                "brier_30": round(brier, 4) if brier is not None else None,
                "logloss_30": round(rolling_logloss, 4) if rolling_logloss is not None else None,
                "pred_tai_30": tai_predictions,
                "pred_xiu_30": xiu_predictions,
                "prediction_bias_30": round(prediction_bias, 4) if prediction_bias is not None else None,
                "random_baseline": 0.5,
                "has_evidence": len(self.hit) >= 20,
                "warning": (
                    "Mẫu dự đoán đang lệch mạnh về một phía"
                    if len(self.pred_sides) >= 10 and prediction_bias >= 0.9 else None
                ),
            },
            "baseline_side": baseline_side,
            "baseline_p_tai": round(baseline_p, 6),
            "pl": pl_sum,
            "loss_streak": self.loss_streak, "run_len": run,
            "inverse_mode": self.inverse_mode,
            "hard_reset": self.hard_reset,
            "nhom": {
                "loss_streak": self.loss_streak,
                "hard_reset": did_reset,
                "inverse_mode": self.inverse_mode,
                "loss_tu_hoc": mean_loss,
                "loss_thuat_toan": None,
                "tran": self.cap,
            },
        }
        # Cờ reset chỉ hiển thị ở prediction kế tiếp sau khi reset.
        self.last_reset = False
        self.hard_reset = False
        return result

    def learn(self, pk, y: bool):
        if not isinstance(pk, dict) or pk.get("side") not in ("TAI", "XIU"):
            return
        y = bool(y)
        votes = pk.get("expert_votes") or pk.get("ex") or {}
        for key in self.NAMES:
            self.loss_sum[key] *= self.DECAY
            self.loss_mass[key] *= self.DECAY
            self.loss_sum[key] += self._logloss(votes.get(key, 0.5), y)
            self.loss_mass[key] += 1.0
        self._update_weights()

        won = (pk["side"] == "TAI") == y
        self.hit.append(1 if won else 0)
        self.pred_sides.append(pk["side"])

        baseline_side = pk.get("baseline_side")
        if baseline_side in ("TAI", "XIU"):
            self.baseline_hit.append(1 if ((baseline_side == "TAI") == y) else 0)

        p_tai = self._clip(pk.get("p_tai", 0.5))
        self.brier_hist.append((p_tai - (1.0 if y else 0.0)) ** 2)
        self.logloss_hist.append(self._logloss(p_tai, y))

        if won:
            self.loss_streak = 0
        else:
            self.loss_streak += 1

        # Không tự đảo chiều hoặc reset sau chuỗi thua:
        # đó là phản ứng quá khớp với nhiễu, không phải bằng chứng mô hình tốt hơn.
        self.inverse_mode = False
        self.inverse_win_streak = 0
        self.t += 1



def replay(rows, newest_first=False):
    """
    Prequential walk-forward:
    - sort/validate observations first;
    - at time t predict using only rows < t;
    - score that prediction against row t;
    - only then learn from row t.
    Không dùng validation để chọn đảo chiều trên chính tập đã chấm.
    """
    rows = list(rows or [])
    if newest_first:
        rows.reverse()

    validator = Brain()
    clean_rows = []
    seen_ids = set()
    for row in rows:
        clean = validator._validated_row(row)
        if clean is None:
            continue
        sid = clean.get("id")
        # Bỏ ID trùng để không học lặp cùng một phiên.
        if sid is not None:
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
        clean_rows.append(clean)

    # API có thể trả dữ liệu lộn thứ tự; sắp theo ID phiên khi ID có thể so sánh.
    if clean_rows and all(row.get("id") is not None for row in clean_rows):
        try:
            clean_rows.sort(key=lambda row: int(row["id"]))
        except (TypeError, ValueError):
            pass
    clean_rows = clean_rows[-LEARN_WIN:]

    brain = Brain()
    history = deque(maxlen=HIST_MAX)
    if not clean_rows:
        return brain, history

    # Phiên đầu chỉ dùng làm mốc lịch sử; không có dự đoán trước đó để chấm.
    brain.observe(clean_rows[0])
    for row in clean_rows[1:]:
        prediction = brain.predict()
        won = prediction["side"] == row["result"]
        brain.learn(prediction, row["result"] == "TAI")
        history.append(entry(row, prediction, won, False))
        brain.observe(row)

    return brain, history


def entry(row, prediction, won, live):
    """Chuẩn hóa một phiên đã có kết quả để lưu vào lịch sử."""
    status = "win" if won else "lose"
    return {
        "phien": row.get("id"),
        "du_doan": prediction.get("side"),
        "ket_qua": row.get("result"),
        "xuc_xac": list(row.get("dices") or []),
        "tong": row.get("point"),
        "trang_thai": status,
        "icon": ICON.get(status, ""),
        "live": bool(live),
    }


# ── Trạng thái từng bàn ────────────────────────────────────────────────────────
class Table:
    def __init__(self, code):
        self.code = code; self.name = NAMES[code]; self.url = URLS[code]
        self.enabled = True; self.lock = threading.Lock(); self.reset()
        self.load_history()

    def reset(self):
        self.ready = False; self.brain = None
        self.hist  = deque(maxlen=HIST_MAX); self.last = None; self.pending = None
        self.last_id = 0; self.fetch_ts = 0.0; self.ok_ts = 0.0
        self.err = ""; self.ms = 0; self.n_fetch = 0

    def load_history(self):
        """Chỉ khôi phục lịch sử dự đoán live đã được chấm và lưu JSON."""
        try:
            with _history_lock:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    store = json.load(f)
            rows = store.get(self.code, []) if isinstance(store, dict) else []
            if isinstance(rows, list):
                self.hist = deque([x for x in rows if isinstance(x, dict)][-HIST_MAX:], maxlen=HIST_MAX)
        except (OSError, ValueError, TypeError):
            self.hist = deque(maxlen=HIST_MAX)

    def save_history(self):
        """Ghi atomically lịch sử live sau khi phiên dự đoán có kết quả."""
        try:
            with _history_lock:
                try:
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                        store = json.load(f)
                    if not isinstance(store, dict): store = {}
                except (OSError, ValueError, TypeError):
                    store = {}
                store[self.code] = list(self.hist)[-HIST_MAX:]
                tmp = HISTORY_FILE + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(store, f, ensure_ascii=False, separators=(",", ":"))
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp, HISTORY_FILE)
        except OSError as e:
            self.err = "Không lưu được lịch sử JSON: %s" % str(e)[:100]

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
        rows = sorted(
            (r for r in (rows or []) if isinstance(r, dict) and "id" in r),
            key=lambda r: int(r["id"])
        )
        if not rows:
            self.err = "Nguồn dữ liệu không có phiên hợp lệ"
            return
        newest = rows[-1]["id"]
        if rebuild or not self.ready or newest < self.last_id or rows[0]["id"] > self.last_id + 1:
            self.brain, _replay_history = replay(rows)
            # Không biến dữ liệu API cũ thành lịch sử dự đoán. Chỉ giữ JSON live
            # được ghi từ lúc hệ thống thực sự chạy và đã có kết quả xác minh.
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
            if is_live:
                self.hist.append(entry(row, pk, win, True))
                self.save_history()  # chỉ lưu sau khi phiên dự đoán đã có kết quả thật
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
            "phien":      self.last_id + 1,
            "du_doan":    pk["side"],
            "do_tin_cay": pk["confidence"],
            "conf":       pk["confidence"],
            "p_tai":      round(pk["p_tai"], 3),
            "reasoning":  pk.get("reasoning", ""),
            "loss_streak": pk.get("loss_streak", 0),
            "run_len":    pk.get("run_len", 0),
            "acc30":      pk.get("acc30"),
            "pk":         pk,
        }

TABLES = {c: Table(c) for c in URLS}

# ── Helpers thống kê ───────────────────────────────────────────────────────────
def stats(items):
    w  = sum(1 for h in items if h["trang_thai"] == "win")
    l  = sum(1 for h in items if h["trang_thai"] == "lose")
    total = w + l
    return {"win": w, "lose": l, "skip": 0,
            "ty_le": round(w * 100.0 / total, 1) if total else 0.0}

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
            "evaluation":      pkd.get("evaluation"),
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
    live = [h for h in hist if h.get("live")]
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
            "phien":       pd["phien"],
            "du_doan":     pd["du_doan"],
            "conf":        pd["do_tin_cay"],
            "p_tai":       pd["p_tai"],
            "evaluation":  pk.get("evaluation"),
            "baseline_side": pk.get("baseline_side"),
            "temp":        pk.get("temp", 1.0),
            "reasoning":   pk.get("reasoning", ""),
            "loss_streak": pk.get("loss_streak", 0),
            "run_len":     pk.get("run_len", 0),
            "acc30":       pk.get("acc30"),
            "hard_reset":  pk.get("nhom", {}).get("hard_reset", False),
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

# ── Admin SPA — WHITE LIGHT MODE v2 ───────────────────────────────────────────
PAGE = r"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#ffffff"><title>PAW TX · Neural Control</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════
   PAW TX ADMIN — NỀN TRẮNG TO RÕ NỔI BẬT v2
   ═══════════════════════════════════════════════════ */
*{box-sizing:border-box;margin:0;padding:0}
:root{
  color-scheme:light;
  --bg:#f0f4f9;--surf:#fff;--surf2:#f7f9fc;--surf3:#eef2f7;
  --bd:#dde4ee;--bd2:#c8d4e3;
  --txt:#0f1b2d;--txt2:#2d3f56;--txt3:#5a7090;--txt4:#8fa3b8;
  --blue:#1d6bf3;--blue-s:#e8f0fe;--blue2:#1558d4;
  --cyan:#0891b2;--cyan-s:#e0f7fa;
  --green:#0f7f56;--green-s:#e6f9f1;--green-b:#22c55e;
  --red:#c8203b;--red-s:#fef0f2;--red-b:#ef4444;
  --amber:#a05d10;--amber-s:#fef9ec;
  --purple:#6c3cbf;--purple-s:#f4f0fb;
  --shadow:0 1px 3px rgba(0,0,0,.08),0 1px 2px rgba(0,0,0,.05);
  --shadow-md:0 4px 16px rgba(0,0,0,.09),0 2px 4px rgba(0,0,0,.05);
  --shadow-lg:0 12px 40px rgba(0,0,0,.12),0 4px 10px rgba(0,0,0,.06);
}
html{background:var(--bg);-webkit-font-smoothing:antialiased}
body{background:var(--bg);color:var(--txt);font-family:'Inter',system-ui,sans-serif;font-size:14px;line-height:1.6;min-height:100vh}
button{font:inherit;cursor:pointer}a{color:inherit;text-decoration:none}
.mono{font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}
.hide{display:none!important}

/* ── TOPBAR ── */
.top{position:sticky;top:0;z-index:50;height:64px;
  display:flex;align-items:center;justify-content:space-between;gap:14px;
  padding:0 max(20px,calc((100vw - 1500px)/2));
  background:rgba(255,255,255,.95);backdrop-filter:blur(16px);
  border-bottom:1px solid var(--bd);box-shadow:0 1px 0 var(--bd)}
.brand{display:flex;align-items:center;gap:13px}
.logo{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;
  background:linear-gradient(135deg,#1d6bf3,#7c3aed);box-shadow:0 4px 14px rgba(79,70,229,.28)}
.logo svg{width:24px;height:24px}
.brand-name{font-size:16px;font-weight:900;letter-spacing:-.04em;color:var(--txt)}
.brand-name small{display:block;font-size:9px;font-family:'JetBrains Mono',monospace;
  color:var(--txt3);letter-spacing:.18em;font-weight:600;margin-top:-1px}
.right{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.status-pill{display:flex;align-items:center;gap:7px;padding:6px 12px;
  border:1px solid var(--bd);border-radius:99px;font-size:12px;font-weight:700;
  color:var(--txt3);background:var(--surf2)}
.ldot{width:8px;height:8px;border-radius:50%;background:var(--green-b);
  box-shadow:0 0 0 3px rgba(34,197,94,.15);animation:pulse 2.5s infinite}
.ldot.bad{background:var(--red-b);box-shadow:0 0 0 3px rgba(239,68,68,.15)}
#countdown{font-family:'JetBrains Mono',monospace;font-weight:800;color:var(--blue)}

/* ── BTN ── */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;
  padding:9px 16px;border-radius:10px;font-size:13px;font-weight:700;
  border:1px solid var(--bd2);background:var(--surf);color:var(--txt2);
  transition:all .15s;white-space:nowrap;box-shadow:var(--shadow)}
.btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-s);transform:translateY(-1px);box-shadow:var(--shadow-md)}
.btn:active{transform:scale(.98)}
.btn.primary{background:var(--blue);color:#fff;border-color:var(--blue2);box-shadow:0 2px 8px rgba(29,107,243,.28)}
.btn.primary:hover{background:var(--blue2);border-color:var(--blue2);color:#fff;box-shadow:0 4px 16px rgba(29,107,243,.36)}
.btn.danger{color:var(--red);border-color:#fca5a5;background:var(--red-s)}
.btn.danger:hover{background:#fee2e2;border-color:var(--red)}
.btn-sm{padding:7px 12px;font-size:12px;border-radius:8px}

/* ── NAV TABS ── */
.nav-tabs{display:flex;gap:4px;padding:0 max(20px,calc((100vw - 1500px)/2));
  border-bottom:1px solid var(--bd);background:var(--surf);overflow-x:auto}
.tab{padding:14px 18px;font-size:13px;font-weight:700;color:var(--txt3);
  border:none;background:none;border-bottom:2.5px solid transparent;
  cursor:pointer;white-space:nowrap;transition:color .15s,border-color .15s}
.tab.active{color:var(--blue);border-bottom-color:var(--blue)}
.tab:hover:not(.active){color:var(--txt2)}

/* ── WRAP ── */
.wrap{max-width:1500px;margin:0 auto;padding:24px 20px 72px}

/* ── GRID ── */
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}

/* ── CARD ── */
.card{background:var(--surf);border:1px solid var(--bd);border-radius:16px;
  padding:22px;box-shadow:var(--shadow);min-width:0;
  transition:border-color .15s,box-shadow .15s,transform .15s;
  animation:fadeUp .32s ease both}
.card:hover{border-color:var(--bd2);box-shadow:var(--shadow-md);transform:translateY(-1px)}
.cardhead{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:18px}
.cardhead b{font-size:16px;font-weight:800;color:var(--txt);letter-spacing:-.02em}

/* ── HERO (prediction banner) ── */
.hero{border-radius:14px;padding:22px 24px;position:relative;overflow:hidden;
  background:linear-gradient(130deg,#1a3056 0%,#1a1640 55%,#2b1d50 100%);
  border:1px solid #2e4a7a}
.hero-label{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;
  letter-spacing:.18em;color:#7eb8e8;text-transform:uppercase;margin-bottom:10px}
/* BIG PREDICTION TEXT */
.side{font-size:clamp(52px,8vw,88px);font-weight:900;letter-spacing:-.06em;
  line-height:1;margin:6px 0 12px}
.side.TAI{color:#ff8fa0;text-shadow:0 0 32px rgba(255,80,100,.6)}
.side.XIU{color:#38e8ff;text-shadow:0 0 32px rgba(56,232,255,.6)}
/* BIG CONFIDENCE */
.conf-row{display:flex;align-items:baseline;gap:14px;margin-bottom:12px}
.conf-pct{font-size:clamp(28px,5vw,42px);font-weight:900;letter-spacing:-.05em;
  color:#fbbf24;font-family:'JetBrains Mono',monospace}
.conf-label{font-size:14px;color:#94a3b8;font-weight:600}
.p-tai-row{font-size:13px;color:#9eb8d8;margin-bottom:14px;font-family:'JetBrains Mono',monospace}
/* METER */
.meter{height:10px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden;margin:0 0 16px}
.meter i{display:block;height:100%;border-radius:99px;
  background:linear-gradient(90deg,#3b82f6,#06b6d4);
  box-shadow:0 0 14px rgba(56,232,255,.5);transition:width .4s ease}
/* REASON BOX */
.reason{padding:13px 15px;border:1px solid #2e4a6a;border-left:3px solid #818cf8;
  border-radius:10px;background:rgba(10,20,40,.5);color:#b0c8e8;font-size:13px;line-height:1.6}
.reason strong{display:block;font-family:'JetBrains Mono',monospace;font-size:9px;
  letter-spacing:.15em;color:#a5b4fc;margin-bottom:6px;text-transform:uppercase}
/* STAT CHIPS */
.chips{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.chip{flex:1;min-width:85px;padding:12px 14px;background:rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.1);border-radius:11px}
.chip b{display:block;font-family:'JetBrains Mono',monospace;font-size:20px;
  font-weight:800;color:#e2eeff;line-height:1.1;margin-bottom:4px}
.chip small{font-size:10px;color:#7f98b8;text-transform:uppercase;letter-spacing:.08em;font-weight:700}

/* ── STAT OVERVIEW CARDS ── */
.stat-card{background:var(--surf);border:1px solid var(--bd);border-radius:14px;
  padding:18px 20px;position:relative;overflow:hidden;box-shadow:var(--shadow);
  transition:transform .15s,box-shadow .15s;animation:fadeUp .32s ease both}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--sa,var(--blue));border-radius:14px 14px 0 0}
.stat-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-md)}
.stat-label{font-size:11px;text-transform:uppercase;letter-spacing:.09em;
  color:var(--txt4);font-weight:800;margin-bottom:9px}
.stat-val{font-size:30px;font-weight:900;letter-spacing:-.05em;color:var(--txt);
  font-variant-numeric:tabular-nums;line-height:1.1}
.stat-note{font-size:11px;color:var(--txt4);margin-top:7px}

/* ── EXPERTS PANEL ── */
.experts{display:grid;gap:11px;margin-top:4px}
.expert-row{display:grid;grid-template-columns:140px 1fr 100px;align-items:center;gap:10px}
.expert-name{font-size:12px;font-weight:700;color:var(--txt2)}
.track{height:7px;background:var(--surf3);border-radius:99px;overflow:hidden}
.track i{display:block;height:100%;border-radius:99px;
  background:linear-gradient(90deg,var(--blue),var(--cyan));transition:width .3s}
.expert-meta{text-align:right;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--txt3)}
.group-tag{font-size:9px;font-family:'JetBrains Mono',monospace;color:var(--purple);
  text-transform:uppercase;letter-spacing:.1em}

/* ── TABLE ── */
.tablewrap{overflow:auto;border:1px solid var(--bd);border-radius:12px;background:var(--surf)}
table{border-collapse:separate;border-spacing:0;width:100%;min-width:600px}
thead{position:sticky;top:0;z-index:2;background:var(--surf2)}
th{padding:12px 14px;font-size:10px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--txt4);text-align:left;border-bottom:1px solid var(--bd);font-weight:800}
td{padding:13px 14px;font-size:13px;color:var(--txt2);border-bottom:1px solid var(--surf3)}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover td{background:#fafcff}
tr.win td{background:#f0fdf6}tr.win td:first-child{box-shadow:inset 3px 0 0 var(--green-b)}
tr.lose td{background:#fff4f5}tr.lose td:first-child{box-shadow:inset 3px 0 0 var(--red-b)}
/* PILL BADGES */
.pill{display:inline-flex;align-items:center;padding:4px 11px;border-radius:99px;
  font-size:11px;font-weight:800;border:1px solid;white-space:nowrap;letter-spacing:.03em}
.pill.TAI{background:var(--red-s);color:var(--red);border-color:#fca5a5}
.pill.XIU{background:var(--cyan-s);color:var(--cyan);border-color:#a5f3fc}
.pill.win{background:var(--green-s);color:var(--green);border-color:#86efac}
.pill.lose{background:var(--red-s);color:var(--red);border-color:#fca5a5}
/* LIVE BADGE */
.live-badge{display:inline-flex;align-items:center;gap:5px;font-size:10px;font-weight:800;
  padding:3px 9px;border-radius:99px;background:var(--red-s);border:1px solid #fca5a5;color:var(--red)}
.live-dot{width:5px;height:5px;border-radius:50%;background:var(--red-b);animation:pulse 1.4s infinite}

/* ── PROTECTION SECTION ── */
.protect{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.prot-status{display:inline-flex;align-items:center;gap:8px;padding:7px 14px;
  border-radius:99px;font-size:12px;font-weight:800;border:1.5px solid;margin-bottom:16px}
.prot-status.on{background:var(--green-s);color:var(--green);border-color:#86efac}
.prot-status.off{background:var(--surf3);color:var(--txt3);border-color:var(--bd2)}
.code-box{display:flex;align-items:center;gap:12px;padding:14px 18px;
  background:var(--surf2);border:1.5px solid var(--bd2);border-radius:12px;margin:14px 0}
.code-val{font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:800;
  letter-spacing:.22em;color:var(--blue);flex:1}
.prot-url{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--txt3);
  word-break:break-all;padding:10px 14px;background:var(--surf2);border-radius:10px;
  border:1px solid var(--bd);margin-top:10px}
.prot-url b{color:var(--blue)}
.prot-actions{display:flex;gap:8px;flex-wrap:wrap}

/* ── MISC ── */
.empty{color:var(--txt4);text-align:center;padding:28px;font-size:13px}
.section-title{font-size:17px;font-weight:800;color:var(--txt);letter-spacing:-.03em;margin-bottom:4px}
.section-sub{font-size:12px;color:var(--txt3);margin-bottom:16px}
.sep{height:1px;background:linear-gradient(90deg,transparent,var(--bd),transparent);margin:24px 0}
.actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.muted{color:var(--txt3)}
.tablebox{display:grid;gap:20px}
.toast{position:fixed;bottom:20px;right:20px;z-index:200;
  background:var(--surf);border:1px solid var(--bd);border-left:3px solid var(--green-b);
  padding:13px 18px;border-radius:12px;display:none;
  box-shadow:var(--shadow-lg);font-size:13px;font-weight:700;color:var(--txt);
  animation:fadeUp .2s ease}
.foot{color:var(--txt4);text-align:center;font-family:'JetBrains Mono',monospace;
  font-size:9px;margin-top:28px;letter-spacing:.1em}
.heading{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin:10px 0 20px}
.eyebrow{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--cyan);
  letter-spacing:.18em;font-weight:700;margin-bottom:5px}
h1{font-size:clamp(22px,4vw,32px);font-weight:900;letter-spacing:-.05em;color:var(--txt)}
.hdot{width:9px;height:9px;border-radius:50%;display:inline-block;flex-shrink:0}
.hdot.ok{background:var(--green-b);box-shadow:0 0 0 3px rgba(34,197,94,.15);animation:pulse 2.5s infinite}
.hdot.warn{background:#f59e0b}.hdot.bad{background:var(--red-b)}

@keyframes pulse{50%{box-shadow:0 0 0 7px transparent}}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:950px){.grid,.protect{grid-template-columns:1fr}.grid3{grid-template-columns:repeat(2,1fr)}}
@media(max-width:620px){.wrap{padding:16px 12px 48px}.grid4{grid-template-columns:1fr 1fr}
  .expert-row{grid-template-columns:100px 1fr 80px}.side{font-size:56px}.heading{flex-direction:column;align-items:start}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
</style></head>
<body>

<!-- TOPBAR -->
<header class="top">
  <div class="brand">
    <div class="logo">
      <svg viewBox="0 0 28 28" fill="none">
        <path d="M14 2.5S22.5 12 22.5 17.5a8.5 8.5 0 1 1-17 0C5.5 12 14 2.5 14 2.5Z" fill="white"/>
        <path d="M10 15.5c.8-2.2 2-4.2 3.3-5.8" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </div>
    <div class="brand-name">PAW NEURAL<small>TX // AI CONTROL CENTER</small></div>
  </div>
  <div class="right">
    <div class="status-pill"><span class="ldot" id="apiDot"></span><span id="apiStatus">CONNECTING</span></div>
    <div class="status-pill">SYNC <span id="countdown">4</span>s</div>
    <button class="btn btn-sm" onclick="load()">↻ Làm mới</button>
    <a class="btn btn-sm" href="/admin/logout">Thoát →</a>
  </div>
</header>

<!-- NAV TABS -->
<nav class="nav-tabs">
  <button class="tab active" onclick="switchTab('all',this)">Tổng quan</button>
  <button class="tab" onclick="switchTab('history',this)">Lịch sử dự đoán</button>
  <button class="tab" onclick="switchTab('protection',this)">Bảo vệ API</button>
</nav>

<main class="wrap">
  <!-- ════ TAB ALL ════ -->
  <section id="view-all">
    <div class="heading">
      <div>
        <div class="eyebrow">NEURAL NETWORK / LIVE MONITOR</div>
        <h1>Bộ não dự đoán Tài / Xỉu</h1>
      </div>
      <div class="muted mono" id="updated" style="font-size:12px">Đang khởi tạo…</div>
    </div>
    <!-- Summary stat row -->
    <div class="grid4" id="statRow" style="margin-bottom:20px"></div>
    <!-- Predict boards -->
    <div class="grid" id="boards"></div>
  </section>

  <!-- ════ TAB HISTORY ════ -->
  <section id="view-history" class="hide">
    <div class="heading" style="margin-top:4px">
      <div><div class="eyebrow">WALK-FORWARD LEARNING</div><h1>Lịch sử dự đoán live</h1></div>
    </div>
    <div class="tablebox" id="historyBoards"></div>
  </section>

  <!-- ════ TAB PROTECTION ════ -->
  <section id="view-protection" class="hide">
    <div class="heading" style="margin-top:4px">
      <div><div class="eyebrow">SECURITY</div><h1>Bảo vệ API Access</h1></div>
    </div>
    <div class="protect">
      <div class="card">
        <div class="cardhead"><b>API ACCESS GUARD</b><span class="prot-status off" id="protState">TẮT</span></div>
        <p class="muted" style="font-size:13px;margin-bottom:14px">Thêm mã 6 ký tự vào đường dẫn API để chống chia sẻ trái phép.</p>
        <div class="code-box">
          <div class="code-val" id="codeDisplay">••••••</div>
          <button class="btn btn-sm" onclick="copyCode()">Copy</button>
        </div>
        <div class="prot-url" id="urlPreview">Tạo mã để xem URL bảo vệ</div>
        <div class="prot-actions" style="margin-top:14px">
          <button class="btn primary" onclick="genCode()">Tạo mã mới</button>
          <button class="btn" onclick="setProt('enable')" style="color:var(--green);border-color:#86efac;background:var(--green-s)">Bật bảo vệ</button>
          <button class="btn danger" onclick="setProt('disable')">Tắt bảo vệ</button>
          <button class="btn" onclick="revokeCode()" style="color:var(--amber)">Thu hồi</button>
        </div>
      </div>
      <div class="card">
        <div class="cardhead"><b>Hướng dẫn</b></div>
        <div style="font-size:13px;color:var(--txt2);line-height:1.75">
          <p><b>Khi BẬT:</b> API chỉ nhận URL có mã đúng.</p>
          <div class="prot-url" style="margin:10px 0"><b>https://api…onrender.com/[MÃ6KÝ]/tx/hu</b></div>
          <p><b>Khi TẮT:</b> <code>/tx/hu</code> hoạt động bình thường.</p>
          <p style="margin-top:8px"><b>Rate limit:</b> Sai mã >8 lần/5 phút → block 10 phút.</p>
          <p style="margin-top:8px;color:var(--txt3)">Mã 6 ký tự là lớp bảo vệ đường dẫn, không thay thế HTTPS.</p>
        </div>
        <div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--bd)">
          <div style="font-size:12px;font-weight:800;color:var(--txt3);margin-bottom:8px">TRẠNG THÁI</div>
          <p class="muted" id="protInfo" style="font-size:13px">Đang tải…</p>
        </div>
      </div>
    </div>
  </section>

  <div class="foot">PAW TX · LEARN_WIN=50 · WALK-FORWARD · 10 EXPERTS · NO SKIP · NO GUARANTEED EDGE</div>
</main>
<div class="toast" id="toast"></div>

<script>
const CSRF="__CSRF__";
let DATA=[],_tab='all',timer=4,prot={enabled:false,has_code:false,code:''};
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function toast(s,ok=true){const el=$('toast');el.textContent=s;el.style.borderLeftColor=ok?'var(--green-b)':'var(--red-b)';el.style.display='block';clearTimeout(window._t);window._t=setTimeout(()=>el.style.display='none',2800)}

function switchTab(name,btn){
  _tab=name;
  ['all','history','protection'].forEach(x=>$('view-'+x).classList.toggle('hide',x!==name));
  document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===btn));
  if(name==='protection') loadProt();
}

/* ── SIDE PILL ── */
function side(s){return s?`<span class="pill ${s}">${s==='TAI'?'TÀI':'XỈU'}</span>`:'<span class="pill" style="color:var(--txt4)">—</span>'}

/* ── BOARD CARD (Tổng quan) ── */
function board(t){
  const p=t.pending||{}, ex=t.experts||[];
  const s=p.du_doan, conf=p.conf??0;
  const ev=p.evaluation||{};
  const online=t.ready;
  const accLive=(t.st_live?.win||0)+(t.st_live?.lose||0)>0?t.st_live?.ty_le??0:0;
  return `<article class="card" style="animation-delay:${t.code==='md5'?'.08s':'0s'}">
    <!-- Header -->
    <div class="cardhead">
      <div style="display:flex;align-items:center;gap:10px">
        <span class="hdot ${online?'ok':'bad'}"></span>
        <div>
          <div style="font-size:16px;font-weight:900;letter-spacing:-.03em">Bàn ${esc(t.name)}</div>
          <div class="mono muted" style="font-size:11px">${online?'API ONLINE':'WAITING'} · ${t.ms||0}ms · ${t.age??'—'}s trước</div>
        </div>
      </div>
      <div class="actions">
        <button class="btn btn-sm" onclick="act('${t.code}','refresh')">↻</button>
        <button class="btn btn-sm" onclick="act('${t.code}','relearn')">🧠 Học lại</button>
        <button class="btn btn-sm ${t.enabled?'danger':''}" onclick="act('${t.code}','${t.enabled?'off':'on'}')">${t.enabled?'Tắt':'Bật'}</button>
      </div>
    </div>

    <!-- Hero predict -->
    <div class="hero">
      <div class="hero-label">DỰ ĐOÁN PHIÊN TIẾP THEO · #${p.phien??'—'}</div>
      <div class="side ${s||''}">${s==='TAI'?'TÀI':s==='XIU'?'XỈU':'—'}</div>
      <div class="conf-row">
        <div class="conf-pct">${conf}%</div>
        <div class="conf-label">độ tự tin</div>
        <div class="mono" style="font-size:13px;color:#9eb8d8;margin-left:4px">p(Tài)=${((p.p_tai??.5)*100).toFixed(2)}%</div>
      </div>
      <div class="meter"><i style="width:${Math.min(100,conf)}%"></i></div>
      <div class="reason"><strong>AI SUY NGHĨ</strong>${esc(p.reasoning||'Đang chờ đủ dữ liệu…')}</div>
      <div class="chips">
        <div class="chip"><b>${p.loss_streak??0}</b><small>Thua liên tiếp</small></div>
        <div class="chip"><b>${p.run_len??0}</b><small>Bệt hiện tại</small></div>
        <div class="chip"><b>${t.st_30?.ty_le??0}%</b><small>Accuracy 30</small></div>
        <div class="chip"><b>${t.st_live?.ty_le??0}%</b><small>Accuracy live</small></div>
        <div class="chip"><b>${t.st_30?.win??0}/${t.st_30?.lose??0}</b><small>W/L live 30</small></div>
        <div class="chip"><b>${ev.accuracy_30==null?'—':(ev.accuracy_30*100).toFixed(1)+'%'}</b><small>Walk-forward 30</small></div>
        <div class="chip"><b>${ev.baseline_accuracy_30==null?'—':(ev.baseline_accuracy_30*100).toFixed(1)+'%'}</b><small>Baseline 30</small></div>
        <div class="chip"><b>${ev.pred_tai_30??0}/${ev.pred_xiu_30??0}</b><small>Dự đoán Tài/Xỉu</small></div>
      </div>
      ${ev.warning?`<div style="margin-top:10px;padding:9px 12px;border:1px solid var(--red-b);border-radius:9px;background:var(--red-s);color:var(--red);font-size:12px">⚠ ${esc(ev.warning)}</div>`:''}
    </div>

    <!-- Last session -->
    ${t.last?`<div style="display:flex;align-items:center;justify-content:space-between;margin-top:16px;padding:12px 14px;background:var(--surf2);border:1px solid var(--bd);border-radius:10px;gap:14px;flex-wrap:wrap">
      <div>
        <div class="muted" style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px">Phiên trước · #${t.last.phien}</div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
          ${side(t.last.ket_qua)}
          <span class="mono" style="font-size:13px;color:var(--txt3)">${esc((t.last.xuc_xac||[]).join('-'))} = ${t.last.tong??'—'}</span>
        </div>
      </div>
      <div style="text-align:right">
        <div class="muted" style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px">AI đã đoán</div>
        <div style="display:flex;align-items:center;gap:8px;justify-content:flex-end">
          ${side(t.last.du_doan)}
          <span style="font-size:18px">${t.last.trang_thai==='win'?'✅':t.last.trang_thai==='lose'?'❌':'—'}</span>
        </div>
      </div>
    </div>`:''}

    <!-- Experts -->
    <details style="margin-top:16px">
      <summary style="font-size:12px;font-weight:800;color:var(--txt3);cursor:pointer;letter-spacing:.06em;text-transform:uppercase;padding:8px 0;border-top:1px solid var(--bd)">
        10 Experts Panel · P(TÀI) / Trọng số
      </summary>
      <div class="experts" style="margin-top:12px">
        ${ex.map(x=>`<div>
          <div class="expert-row">
            <span class="expert-name">${esc(x.name.replaceAll('_',' '))}</span>
            <div class="track"><i style="width:${Math.min(100,Math.max(0,x.w*100))}%"></i></div>
            <span class="expert-meta">${(x.w*100).toFixed(1)}% · ${(x.p*100).toFixed(1)}%</span>
          </div>
          <div class="group-tag" style="margin-left:0;padding-left:0">${esc(x.group)} · vote ${(x.p*100).toFixed(1)}% Tài</div>
        </div>`).join('')}
      </div>
    </details>

    ${t.err?`<div style="margin-top:12px;padding:10px 13px;background:var(--red-s);border:1px solid #fca5a5;border-radius:9px;color:var(--red);font-size:12px">⚠ ${esc(t.err)}</div>`:''}
  </article>`;
}

/* ── STAT ROW ── */
function drawStatRow(){
  if(!DATA.length) return;
  const all=DATA.flatMap(t=>t.hist||[]);
  const w=all.filter(h=>h.trang_thai==='win').length;
  const l=all.filter(h=>h.trang_thai==='lose').length;
  const acc=w+l>0?Math.round(w*100/(w+l)):0;
  const live=DATA.flatMap(t=>(t.hist||[]).filter(h=>h.live));
  const lw=live.filter(h=>h.trang_thai==='win').length;
  const ll=live.filter(h=>h.trang_thai==='lose').length;
  const lacc=lw+ll>0?Math.round(lw*100/(lw+ll)):0;
  $('statRow').innerHTML=[
    {label:'Tổng phiên',val:all.length,note:'Đã ghi nhận',sa:'var(--blue)'},
    {label:'Live accuracy',val:lacc+'%',note:lw+'W / '+ll+'L live',sa:'var(--green-b)'},
    {label:'Tổng accuracy',val:acc+'%',note:w+'W / '+l+'L tổng',sa:'var(--purple)'},
    {label:'Response time',val:(Math.round(DATA.reduce((s,t)=>s+t.ms,0)/DATA.length)||0)+'ms',note:'API upstream',sa:'var(--cyan)'},
  ].map((s,i)=>`<div class="stat-card" style="--sa:${s.sa};animation-delay:${i*.06}s">
    <div class="stat-label">${esc(s.label)}</div>
    <div class="stat-val">${esc(s.val)}</div>
    <div class="stat-note">${esc(s.note)}</div>
  </div>`).join('');
}

/* ── HISTORY TABLE ── */
function histTable(t){
  const rows=t.hist||[];
  return `<section class="card">
    <div class="cardhead"><b>Lịch sử dự đoán live · Bàn ${esc(t.name)}</b>
      <span class="muted mono" style="font-size:12px">${rows.filter(h=>h.live).length} live · ${rows.length} tổng</span>
    </div>
    <div class="tablewrap"><table>
      <thead><tr><th>Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>AI dự đoán</th><th>Trạng thái</th><th>Nguồn</th></tr></thead>
      <tbody>${rows.length?rows.map(h=>`<tr class="${h.trang_thai}">
        <td class="mono">#${h.phien}</td>
        <td class="mono">${esc((h.xuc_xac||[]).join('-'))} / ${h.tong??'—'}</td>
        <td>${side(h.ket_qua)}</td>
        <td>${side(h.du_doan)}</td>
        <td><span class="pill ${h.trang_thai}">${h.trang_thai==='win'?'THẮNG':'THUA'}</span></td>
        <td>${h.live?'<span class="live-badge"><span class="live-dot"></span>live</span>':'<span class="muted" style="font-size:11px">📂 nạp</span>'}</td>
      </tr>`).join(''):'<tr><td colspan="6" class="empty">Chưa có lịch sử dự đoán live</td></tr>'}</tbody>
    </table></div>
  </section>`;
}

/* ── DRAW ALL ── */
function draw(){
  $('boards').innerHTML=DATA.map(board).join('');
  $('historyBoards').innerHTML=DATA.map(histTable).join('');
  drawStatRow();
  const online=DATA.every(x=>x.ready);
  $('apiStatus').textContent=online?'API ONLINE':'DEGRADED';
  $('apiDot').className='ldot'+(online?'':' bad');
  $('updated').textContent='Cập nhật '+new Date().toLocaleTimeString('vi-VN');
}

/* ── LOAD ── */
async function load(){
  try{
    const r=await fetch('/admin/data',{cache:'no-store'});
    if(r.status===401){location.href='/admin';return}
    const j=await r.json();
    if(!j.ok) throw Error(j.loi||'API error');
    DATA=j.tables||[];draw();timer=4;
  }catch(e){
    $('apiStatus').textContent='ERROR';
    $('apiDot').className='ldot bad';
    $('updated').textContent='Lỗi: '+e.message;
  }
}

/* ── ACT ── */
async function act(c,a){
  try{
    const r=await fetch(`/admin/act/${c}/${a}`,{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();
    toast(j.ok?'Đã thực hiện: '+a:'Lỗi: '+(j.loi||''), j.ok);
    load();
  }catch(e){toast('Lỗi mạng',false)}
}

/* ── PROTECTION ── */
async function loadProt(){
  try{
    const r=await fetch('/admin/aprot/status',{headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();
    prot={...prot,enabled:j.enabled,has_code:j.has_code};
    const st=$('protState');
    if(j.enabled){st.textContent='BẬT';st.className='prot-status on';}
    else{st.textContent='TẮT';st.className='prot-status off';}
    $('protInfo').textContent=`Bảo vệ: ${j.enabled?'BẬT':'TẮT'} · ${j.has_code?'Đã có mã':'Chưa có mã'}`;
    if(!prot.code && j.has_code) $('codeDisplay').textContent='••••••';
  }catch(e){$('protInfo').textContent='Lỗi tải trạng thái'}
}
async function genCode(){
  try{
    const r=await fetch('/admin/aprot/gen',{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();
    if(!j.ok) throw Error(j.loi);
    prot.code=j.code;prot.has_code=true;
    $('codeDisplay').textContent=j.code;
    $('urlPreview').innerHTML=`<b>${location.origin}/<span style="color:var(--blue)">${esc(j.code)}</span>/tx/hu</b>`;
    toast('Đã tạo mã mới: '+j.code);loadProt();
  }catch(e){toast('Tạo mã thất bại',false)}
}
async function setProt(action){
  if(action==='enable'&&!prot.has_code){toast('Hãy tạo mã trước',false);return}
  try{
    const fd=new FormData();fd.append('action',action);
    const r=await fetch('/admin/aprot/set',{method:'POST',headers:{'X-CSRF-Token':CSRF},body:fd});
    const j=await r.json();
    if(!j.ok) throw Error(j.loi);
    toast(action==='enable'?'✅ Đã bật bảo vệ API':'Đã tắt bảo vệ API');loadProt();
  }catch(e){toast('Không cập nhật được',false)}
}
async function revokeCode(){
  if(!confirm('Thu hồi mã sẽ TẮT bảo vệ ngay. Tiếp tục?')) return;
  try{
    const r=await fetch('/admin/aprot/revoke',{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();
    if(!j.ok) throw Error(j.loi);
    prot={enabled:false,has_code:false,code:''};
    $('codeDisplay').textContent='••••••';
    $('urlPreview').textContent='Tạo mã để xem URL bảo vệ';
    toast('Đã thu hồi mã');loadProt();
  }catch(e){toast('Thu hồi thất bại',false)}
}
function copyCode(){
  if(!prot.code){toast('Chưa có mã để copy',false);return}
  navigator.clipboard?.writeText(prot.code)
    .then(()=>toast('Đã copy mã: '+prot.code))
    .catch(()=>toast('Clipboard không khả dụng',false))
}

/* ── COUNTDOWN & AUTO LOAD ── */
setInterval(()=>{timer=Math.max(0,timer-1);$('countdown').textContent=timer;if(timer===0){load();timer=4}},1000);
load();
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
