# -*- coding: utf-8 -*-
"""PAW TX API v4 — Real-World Stable Engine + Auto-Healing."""
import hmac, json, logging, math, os, secrets, threading, time
from collections import deque, Counter, defaultdict
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import requests
from flask import Flask, jsonify, make_response, redirect, request, session
from werkzeug.exceptions import HTTPException

log = logging.getLogger("paw_tx")

# ── Cấu hình ──────────────────────────────────────────────────────────────────
URLS  = {"hu":  os.getenv("API_URL_HU",  "https://wtx.tele68.com/v1/tx/sessions"),
         "md5": os.getenv("API_URL_MD5", "https://wtxmd52.tele68.com/v1/txmd5/sessions")}
NAMES = {"hu": "Hũ", "md5": "MD5"}

HIST_MAX  = 50
POLL_SEC  = 4
MIN_GAP   = 3
STALE_SEC = 8

ICON       = {"win": "✅", "lose": "❌", "cho": "⏳", "skip": "⏸️"}
VN         = timezone(timedelta(hours=7))
STATE_FILE = os.getenv("STATE_FILE", "/tmp/paw_tx_toggles.json")
CFG_FILE   = os.getenv("CFG_FILE",   "/tmp/paw_tx_cfg.json")
HISTORY_FILE = os.getenv("HISTORY_FILE", "/tmp/paw_tx_history.json")
_history_lock = threading.Lock()

# ── API Access Protection ──────────────────────────────────────────────────────
_aprot = {"enabled": False, "code": ""}
_aprot_lock = threading.Lock()
_code_fails: dict = {}
_code_blocked_until: dict = {}
_CODE_MAX_TRIES = 8
_CODE_WINDOW    = 300
_CODE_BACKOFF   = 600

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

@app.after_request
def add_cors(resp):
    if not request.path.startswith("/admin"):
        resp.headers["Access-Control-Allow-Origin"]  = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-Requested-With"
        resp.headers["Access-Control-Max-Age"]        = "86400"
    if not request.path.startswith("/admin"):
        resp.headers["Cache-Control"] = "no-store"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp

def _check_code_ratelimit(ip: str) -> bool:
    now = time.time()
    if _code_blocked_until.get(ip, 0) > now: return False
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
    with _aprot_lock:
        stored = _aprot["code"]
    if not stored: return False
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

_http = requests.Session()
_http.headers.update({"User-Agent": "Mozilla/5.0 (PAW-TX/4)", "Accept": "application/json"})

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
                point = sum(dices)
                if "point" in it and int(it["point"]) != point:
                    log.warning("Bỏ phiên id=%s: point không khớp dices", sid)
                    continue
            else:
                if "point" not in it: continue
                point = int(it["point"])
                if not 3 <= point <= 18: continue
                dices = []
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
#  BỘ NÃO THỰC CHIẾN (REAL-WORLD ENGINE) - Tự phục hồi & Tự hạ tỉ lệ
# ══════════════════════════════════════════════════════════════════════════════
def _dice_sum_prior():
    c = Counter()
    for a in range(1, 7):
        for b in range(1, 7):
            for d in range(1, 7):
                c[a + b + d] += 1
    return {s: c[s] / 216.0 for s in range(3, 19)}

_PT_PRIOR = _dice_sum_prior()
_PT_BASE = sum(v for s, v in _PT_PRIOR.items() if s >= 11)  # ~48.61%

# RealBrain V8 được nhúng trực tiếp từ ttoantaixiu.py; mỗi Table sở hữu một instance riêng.
# -*- coding: utf-8 -*-
"""
PAW TX · ENGINE 62 — 22 Model Lớn + 40 Model Phụ Trợ
Không dùng AI thật, toàn bộ là code thuật toán thuần túy.
"""
import math, random
from collections import deque, Counter, defaultdict
from typing import List, Optional, Tuple, Dict

# ══════════════════════════════════════════════════════════════════════════
#  HELPERS DÙNG CHUNG
# ══════════════════════════════════════════════════════════════════════════
def _run_lengths(seq: list) -> list:
    """[T,T,X,T,T,T,X] → [2,1,3,1]"""
    if not seq: return []
    runs, cur, cnt = [], seq[0], 1
    for v in seq[1:]:
        if v == cur: cnt += 1
        else: runs.append(cnt); cur, cnt = v, 1
    runs.append(cnt); return runs

def _last_run(seq: list) -> Tuple[str, int]:
    """Trả (ký_tự, độ_dài) của nhịp cuối cùng"""
    if not seq: return ("", 0)
    cur, cnt = seq[-1], 1
    for v in reversed(seq[:-1]):
        if v == cur: cnt += 1
        else: break
    return (cur, cnt)

def _opp(side: str) -> str:
    return "XIU" if side == "TAI" else "TAI"

def _clamp(v, lo=0.50, hi=0.95):
    return max(lo, min(hi, v))

def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

# ══════════════════════════════════════════════════════════════════════════
#  22 MODEL PHỤ TRỢ NHỎ (sub-functions dùng bởi model lớn)
# ══════════════════════════════════════════════════════════════════════════

def sub_entropy(seq: list, window=10) -> float:
    """S1: Shannon entropy của window cuối → đo độ hỗn loạn"""
    w = seq[-window:] if len(seq) >= window else seq
    if not w: return 1.0
    t, x = w.count("TAI"), w.count("XIU")
    n = t + x
    if n == 0 or t == 0 or x == 0: return 0.0
    return -(t/n*math.log2(t/n) + x/n*math.log2(x/n))

def sub_autocorr(seq: list, lag=1) -> float:
    """S2: Tương quan tự động lag k — dương=xu hướng, âm=đảo chiều"""
    s = [1 if v == "TAI" else 0 for v in seq]
    n = len(s)
    if n <= lag: return 0.0
    mu = sum(s)/n
    num = sum((s[i]-mu)*(s[i-lag]-mu) for i in range(lag, n))
    den = sum((v-mu)**2 for v in s)
    return num/den if den > 1e-9 else 0.0

def sub_runs_test(seq: list) -> float:
    """S3: Kiểm tra chuỗi ngẫu nhiên (Wald-Wolfowitz simplified) → p_value"""
    if len(seq) < 10: return 0.5
    s = [1 if v == "TAI" else 0 for v in seq]
    runs, cur = 1, s[0]
    for v in s[1:]:
        if v != cur: runs += 1; cur = v
    n1, n2 = s.count(1), s.count(0)
    if n1 == 0 or n2 == 0: return 0.5
    mu = 2*n1*n2/(n1+n2)+1
    sig2 = (mu-1)*(mu-2)/((n1+n2-1)+1e-9)
    if sig2 <= 0: return 0.5
    z = (runs - mu)/math.sqrt(sig2)
    return _sigmoid(-abs(z)*0.8)

def sub_momentum(seq: list, short=5, long=15) -> float:
    """S4: Momentum — tỉ lệ TAI ngắn hạn vs dài hạn"""
    if len(seq) < long: return 0.5
    s_rate = seq[-short:].count("TAI")/short
    l_rate = seq[-long:].count("TAI")/long
    return 0.5 + (s_rate - l_rate)

def sub_volatility_index(seq: list, window=10) -> float:
    """S5: Chỉ số biến động — tỉ lệ đổi chiều trong window"""
    w = seq[-window:]
    if len(w) < 2: return 0.5
    chg = sum(1 for i in range(1, len(w)) if w[i] != w[i-1])
    return chg/(len(w)-1)

def sub_zscore_tai(seq: list, window=20) -> float:
    """S6: Z-score của tỉ lệ TAI so với kỳ vọng 0.5"""
    w = seq[-window:] if len(seq) >= window else seq
    if len(w) < 5: return 0.0
    t = w.count("TAI"); n = len(w)
    mu, sigma = 0.5, math.sqrt(0.25/n)
    return (t/n - mu)/sigma if sigma > 0 else 0.0

def sub_cau_type(seq: list, n=12) -> str:
    """S7: Nhận dạng loại cầu (1-1, 2-2, bệt, lệch,...)"""
    runs = _run_lengths(seq[-n:]) if seq else []
    if not runs: return "UNKNOWN"
    avg = sum(runs)/len(runs)
    mx = max(runs)
    if mx >= 5: return "BET_DAI"       # cầu bệt dài
    if avg <= 1.3: return "1_1"        # cầu 1-1 xen kẽ
    if avg <= 2.5 and len(runs) >= 3: return "2_2"
    if mx >= 3 and avg <= 2.0: return "MIX_SHORT"
    if len(runs) == 1: return "BET_NGAN"
    return "COMPLEX"

def sub_break_prob_historical(seq: list, run_len: int) -> float:
    """S8: Xác suất gãy khi streak đang ở độ dài run_len.
    FIX BUG CŨ: bản V5.1 đếm 'streak kết thúc tại run_len' là gãy mà không đếm
    'streak tiếp tục sang run_len+1' → p_brk luôn ~1.0 → auto bẻ vô điều kiện.
    Bản này quét từng vị trí khi streak đạt run_len và xem phiên kế tiếp gãy hay tiếp.
    """
    if len(seq) < 20: return 0.5
    run_at = [1] * len(seq)
    for i in range(1, len(seq)):
        run_at[i] = run_at[i-1] + 1 if seq[i] == seq[i-1] else 1
    brk_cnt = cont_cnt = 0
    for i in range(len(seq) - 1):
        if run_at[i] == run_len:
            if seq[i+1] != seq[i]: brk_cnt += 1
            else: cont_cnt += 1
    total = brk_cnt + cont_cnt
    if total < 4: return 0.5 + min(0.08, run_len * 0.016)  # ít mẫu → hơi nghiêng bẻ theo run dài
    return (brk_cnt + 1.0) / (total + 2.0)  # Laplace smoothing

def sub_overall_break_rate(seq: list, min_run: int = 2) -> float:
    """S8b: Tỉ lệ gãy TỔNG QUÁT — pool mọi streak >= min_run. Prior khi thiếu mẫu."""
    if len(seq) < 15: return 0.5
    run_at = [1] * len(seq)
    for i in range(1, len(seq)):
        run_at[i] = run_at[i-1] + 1 if seq[i] == seq[i-1] else 1
    brk = cont = 0
    for i in range(len(seq) - 1):
        if run_at[i] >= min_run:
            if seq[i+1] != seq[i]: brk += 1
            else: cont += 1
    total = brk + cont
    if total < 5: return 0.5
    return (brk + 1.0) / (total + 2.0)

def sub_run_pattern_equal(seq: list, last_k: int = 3) -> Optional[int]:
    """S8d: Nếu k nhịp gần nhất (trừ nhịp đang chạy) đều cùng độ dài VÀ nhịp hiện
    tại đang ở độ dài đó → đây là 'cầu đều' (2-2-2, 3-3-3, 1-1-1).
    Trả về độ dài nhịp của cầu đều, hoặc None."""
    runs = _run_lengths(seq)
    if len(runs) < last_k + 1: return None
    finished = runs[:-1][-last_k:]
    if all(r == finished[0] for r in finished):
        return finished[0]
    return None

def sub_dice_sum_zone(point: int) -> str:
    """S9: Phân vùng điểm xúc xắc"""
    if point <= 7:   return "LOW"
    if point <= 10:  return "MID_LOW"
    if point <= 13:  return "MID_HIGH"
    return "HIGH"

def sub_dice_variance(dices: list) -> float:
    """S10: Phương sai của 3 xúc xắc — đo độ phân tán"""
    if len(dices) < 3: return 0.0
    mu = sum(dices)/3
    return sum((d-mu)**2 for d in dices)/3

def sub_sum_trend(sums: list, window=8) -> float:
    """S11: Xu hướng tổng điểm — hồi quy tuyến tính đơn giản"""
    w = list(sums[-window:]) if sums else []
    n = len(w)
    if n < 3: return 0.0
    xs = list(range(n)); mu_x = (n-1)/2; mu_y = sum(w)/n
    num = sum((xs[i]-mu_x)*(w[i]-mu_y) for i in range(n))
    den = sum((xs[i]-mu_x)**2 for i in range(n))
    return num/den if den > 1e-9 else 0.0

def sub_pair_freq(seq: list, pair: Tuple) -> float:
    """S12: Tần suất xuất hiện cặp (a,b) → xác suất"""
    if len(seq) < 10: return 0.5
    cnt = total = 0
    for i in range(len(seq)-1):
        if seq[i] == pair[0]:
            total += 1
            if seq[i+1] == pair[1]: cnt += 1
    return cnt/total if total > 0 else 0.5

def sub_triple_freq(seq: list, triple: Tuple) -> float:
    """S13: Tần suất bộ ba"""
    if len(seq) < 15: return 0.5
    cnt = total = 0
    for i in range(len(seq)-2):
        if (seq[i], seq[i+1]) == triple[:2]:
            total += 1
            if seq[i+2] == triple[2]: cnt += 1
    return cnt/total if total > 0 else 0.5

def sub_balance_ratio(seq: list, window=20) -> float:
    """S14: Tỉ lệ cân bằng TAI/XIU"""
    w = seq[-window:] if len(seq) >= window else seq
    if not w: return 0.5
    return w.count("TAI")/len(w)

def sub_recent_accuracy(predictions: list, results: list, window=10) -> float:
    """S15: Độ chính xác gần nhất của model"""
    n = min(window, len(predictions), len(results))
    if n == 0: return 0.5
    hits = sum(1 for i in range(-n, 0) if predictions[i] == results[i])
    return hits/n

def sub_loss_penalty(loss_streak: int) -> float:
    """S16: Hệ số phạt khi thua liên tiếp"""
    return max(0.3, 1.0 - loss_streak * 0.08)

def sub_win_boost(win_streak: int) -> float:
    """S17: Hệ số thưởng khi thắng liên tiếp"""
    return min(1.3, 1.0 + win_streak * 0.05)

def sub_cau_xau_detector(seq: list, window=10) -> bool:
    """S18: Phát hiện cầu xấu — không có pattern rõ"""
    if len(seq) < window: return False
    w = seq[-window:]
    # Cầu xấu: entropy cao + autocorr gần 0 + không có run >= 2
    ent = sub_entropy(w, window)
    ac  = abs(sub_autocorr(w))
    runs = _run_lengths(w)
    max_run = max(runs) if runs else 1
    return ent > 0.92 and ac < 0.08 and max_run <= 2

def sub_nhacai_pattern(dices_history: list, window=20) -> Dict:
    """S19: Nhận diện pattern xúc xắc của nhà cái"""
    recent = list(dices_history[-window:]) if dices_history else []
    result = {"dominant_zone": "MID", "repeat_pattern": False, "avg_sum": 10.5}
    if not recent: return result
    sums = [sum(d) if isinstance(d, list) and len(d)==3 else 10 for d in recent]
    result["avg_sum"] = sum(sums)/len(sums)
    zones = [sub_dice_sum_zone(s) for s in sums]
    zone_count = Counter(zones)
    result["dominant_zone"] = zone_count.most_common(1)[0][0]
    # Phát hiện lặp pattern tổng
    if len(sums) >= 6:
        last3 = tuple(sums[-3:])
        for i in range(len(sums)-6, len(sums)-3):
            if tuple(sums[i:i+3]) == last3:
                result["repeat_pattern"] = True; break
    return result

def sub_weight_normalize(weights: Dict) -> Dict:
    """S20: Chuẩn hóa trọng số về tổng = 1"""
    total = sum(weights.values())
    if total <= 0: return {k: 1/len(weights) for k in weights}
    return {k: v/total for k, v in weights.items()}

def sub_confidence_gate(conf: float, min_gap: float, tai_w: float, xiu_w: float) -> bool:
    """S21: Kiểm tra ngưỡng confidence — đủ mạnh để xuất tín hiệu"""
    gap = abs(tai_w - xiu_w)
    return conf >= 0.52 and gap >= min_gap

def sub_trend_direction(seq: list, short=5, long=10) -> str:
    """S22: Hướng xu hướng ngắn-dài"""
    if len(seq) < long: return "NEUTRAL"
    s_tai = seq[-short:].count("TAI")/short
    l_tai = seq[-long:].count("TAI")/long
    diff = s_tai - l_tai
    if diff > 0.15: return "UP"      # TÀI đang tăng
    if diff < -0.15: return "DOWN"   # XIU đang tăng
    return "NEUTRAL"

# ══════════════════════════════════════════════════════════════════════════
#  22 MODEL LỚN + 22 MODEL MINI (hàm hỗ trợ riêng)
# ══════════════════════════════════════════════════════════════════════════

class M01_CauNhanBiet:
    """Model 1: Nhận biết các loại cầu cơ bản và dự đoán theo pattern"""
    name = "M01_CAU_NHAN_BIET"; group = "Pattern"
    def __init__(self): self.w = 1.0; self.hist = deque(maxlen=30)

    # Mini: đếm pattern cụ thể trong lịch sử
    def _mini_count_pattern(self, seq, pat):
        cnt = 0
        for i in range(len(seq)-len(pat)):
            if seq[i:i+len(pat)] == list(pat): cnt += 1
        return cnt

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 6:
            return {"side": None, "conf": 0.5, "reason": "M01: Chưa đủ dữ liệu"}
        cau = sub_cau_type(seq)
        last, rlen = _last_run(seq)
        # 1-1: theo đảo
        if cau == "1_1":
            pred = _opp(last)
            conf = _clamp(0.68 + min(0.08, len(seq)*0.001))
            return {"side": pred, "conf": conf, "reason": f"M01: Cầu 1-1 → bẻ {last}→{pred}"}
        # 2-2: theo đảo sau 2
        if cau == "2_2":
            pred = _opp(last) if rlen >= 2 else last
            conf = 0.65
            return {"side": pred, "conf": conf, "reason": f"M01: Cầu 2-2 run={rlen}"}
        # Bệt dài: hỏi dữ liệu THẬT (p_brk đã fix bug) — lệch rõ mới quyết
        if cau == "BET_DAI":
            brk = sub_break_prob_historical(seq, rlen)
            equal_len = sub_run_pattern_equal(seq, 3)
            if equal_len and rlen == equal_len and equal_len <= 3:
                # Cầu đều 2-2-2 / 3-3-3 → đang đúng nhịp quen, theo nhịp
                return {"side": last, "conf": 0.60,
                        "reason": f"M01: Bệt {rlen} nhưng là cầu đều-{equal_len} → theo nhịp"}
            if brk > 0.55:
                base = 0.55 + min(0.20, (rlen - 4) * 0.05)
                conf = _clamp(base + (brk-0.5)*0.5)
                return {"side": _opp(last), "conf": conf, "reason": f"M01: Bệt {rlen} p_brk={brk:.2f} → bẻ"}
            if brk < 0.45:
                return {"side": last, "conf": _clamp(0.55+(0.5-brk)*0.5),
                        "reason": f"M01: Bệt {rlen} hay tiếp (p_cont={1-brk:.2f}) → theo"}
            return {"side": last, "conf": 0.53, "reason": f"M01: Bệt {rlen} p_brk={brk:.2f} trung tính → theo nhẹ"}
        # Bệt ngắn: theo
        if cau == "BET_NGAN":
            pred = last
            cnt = self._mini_count_pattern(seq, [last, last, last])
            conf = _clamp(0.55 + min(0.1, cnt*0.02))
            return {"side": pred, "conf": conf, "reason": f"M01: Bệt ngắn theo {last}"}
        # Mix ngắn
        if cau == "MIX_SHORT":
            pred = _opp(last) if rlen >= 2 else last
            return {"side": pred, "conf": 0.57, "reason": f"M01: Mix ngắn"}
        return {"side": None, "conf": 0.5, "reason": f"M01: Cầu phức tạp {cau}"}


class M02_TrendShortLong:
    """Model 2: Bắt xu hướng ngắn hạn và dài hạn"""
    name = "M02_TREND"; group = "Trend"
    def __init__(self): self.w = 1.0

    # Mini: tính slope EMA
    def _mini_ema(self, seq, n):
        if len(seq) < n: return 0.5
        alpha = 2/(n+1); ema = seq[-n]
        for v in seq[-n+1:]: ema = alpha*v + (1-alpha)*ema
        return ema

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 10:
            return {"side": None, "conf": 0.5, "reason": "M02: Thiếu dữ liệu"}
        binary = [1 if v=="TAI" else 0 for v in seq]
        ema5  = self._mini_ema(binary, 5)
        ema15 = self._mini_ema(binary, min(15, len(binary)))
        mom   = sub_momentum(seq, 5, min(15, len(seq)))
        trend = sub_trend_direction(seq)

        if trend == "UP" and ema5 > ema15:
            conf = _clamp(0.55 + abs(mom)*0.6)
            return {"side": "TAI", "conf": conf, "reason": f"M02: Trend UP, ema5={ema5:.2f}>ema15={ema15:.2f}"}
        if trend == "DOWN" and ema5 < ema15:
            conf = _clamp(0.55 + abs(mom)*0.6)
            return {"side": "XIU", "conf": conf, "reason": f"M02: Trend DOWN, ema5={ema5:.2f}<ema15={ema15:.2f}"}
        # Trung tính
        last, _ = _last_run(seq)
        return {"side": _opp(last), "conf": 0.52, "reason": f"M02: Trend NEUTRAL, bẻ {last}"}


class M03_Balance12:
    """Model 3: Kiểm tra chênh lệch 12 phiên gần nhất"""
    name = "M03_BALANCE12"; group = "Balance"
    def __init__(self): self.w = 1.0

    # Mini: tính chênh lệch chuẩn hoá
    def _mini_imbalance(self, seq, n=12):
        w = seq[-n:] if len(seq)>=n else seq
        t, x = w.count("TAI"), w.count("XIU")
        return (t-x)/(t+x) if (t+x)>0 else 0.0

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 6:
            return {"side": None, "conf": 0.5, "reason": "M03: Thiếu"}
        imb = self._mini_imbalance(seq, 12)
        # Chênh lệch cao → dự đoán phía thiểu số
        if imb > 0.35:
            conf = _clamp(0.55 + imb*0.3)
            return {"side": "XIU", "conf": conf, "reason": f"M03: 12p TÀI nhiều (imb={imb:.2f})→XIU"}
        if imb < -0.35:
            conf = _clamp(0.55 + abs(imb)*0.3)
            return {"side": "TAI", "conf": conf, "reason": f"M03: 12p XIU nhiều (imb={imb:.2f})→TAI"}
        return {"side": None, "conf": 0.5, "reason": f"M03: Cân bằng imb={imb:.2f}"}


class M04_CauNganHan:
    """Model 4: Bắt cầu ngắn hạn 3-5 phiên"""
    name = "M04_CAU_NGAN"; group = "Pattern"
    def __init__(self): self.w = 1.0

    # Mini: nhận dạng cầu 2 phiên cuối
    def _mini_last2(self, seq):
        if len(seq) < 2: return None
        a, b = seq[-2], seq[-1]
        if a == b: return ("THEO", b)
        return ("DAO", _opp(b))

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 5:
            return {"side": None, "conf": 0.5, "reason": "M04: Thiếu"}
        last3 = seq[-3:]; last2 = self._mini_last2(seq)
        last, rlen = _last_run(seq)
        # Pattern: T-X-T → T (nếu hay lặp lại)
        p2 = sub_pair_freq(seq, (seq[-1], seq[-1]))
        p3 = sub_triple_freq(seq, tuple(last3))
        if p3 >= 0.6:
            pred = last3[-1]
            return {"side": pred, "conf": _clamp(0.55+p3*0.2), "reason": f"M04: Triple {last3[-3:]} p={p3:.2f}"}
        if p2 >= 0.6 and rlen == 1:
            pred = last
            return {"side": pred, "conf": _clamp(0.54+p2*0.15), "reason": f"M04: Pair p={p2:.2f}"}
        if last2:
            typ, pred = last2
            conf = 0.57 if typ == "THEO" else 0.55
            return {"side": pred, "conf": conf, "reason": f"M04: {typ} {pred}"}
        return {"side": None, "conf": 0.5, "reason": "M04: Không rõ"}


class M05_WeightBalance:
    """Model 5: Cân bằng trọng số TAI/XIU khi chênh lệch cao"""
    name = "M05_WEIGHT_BAL"; group = "Balance"
    def __init__(self): self.w = 1.0; self.tai_w = 0.5; self.xiu_w = 0.5

    # Mini: điều chỉnh trọng số từng bước
    def _mini_adjust(self, tai_ratio):
        gap = tai_ratio - 0.5
        if gap > 0.2:   return "XIU", _clamp(0.52 + gap*0.4)
        if gap < -0.2:  return "TAI", _clamp(0.52 + abs(gap)*0.4)
        return None, 0.5

    def predict(self, seq, ensemble_votes=None, **kw) -> Dict:
        if len(seq) < 10:
            return {"side": None, "conf": 0.5, "reason": "M05: Chưa đủ"}
        # Kiểm tra ensemble bias nếu có
        if ensemble_votes:
            tai_v = sum(1 for v in ensemble_votes if v == "TAI")
            total_v = len(ensemble_votes)
            tai_ratio = tai_v/total_v if total_v else 0.5
        else:
            tai_ratio = sub_balance_ratio(seq, 20)
        pred, conf = self._mini_adjust(tai_ratio)
        if pred:
            return {"side": pred, "conf": conf, "reason": f"M05: Cân bằng tai_ratio={tai_ratio:.2f}→{pred}"}
        return {"side": None, "conf": 0.5, "reason": f"M05: Đã cân bằng {tai_ratio:.2f}"}


class M06_BeCau:
    """Model 6: Quyết định bắt theo cầu hay bẻ cầu thông minh"""
    name = "M06_BE_CAU"; group = "Strategy"
    def __init__(self): self.w = 1.0

    # Mini: tính điểm theo vs bẻ
    def _mini_score(self, seq, run_len):
        brk  = sub_break_prob_historical(seq, run_len)
        theo = 1.0 - brk
        return theo, brk

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 15:
            return {"side": None, "conf": 0.5, "reason": "M06: Thiếu"}
        last, rlen = _last_run(seq)
        theo_p, brk_p = self._mini_score(seq, rlen)
        vol = sub_volatility_index(seq)
        ent = sub_entropy(seq)
        # Cầu đang biến động cao → bẻ
        if vol > 0.6:
            pred = _opp(last); conf = _clamp(0.56 + vol*0.15)
            return {"side": pred, "conf": conf, "reason": f"M06: Volatility cao={vol:.2f} → bẻ"}
        # Cầu dài >= 5 → bẻ
        if rlen >= 5:
            pred = _opp(last); conf = _clamp(0.52 + rlen*0.025 + (brk_p-0.5)*0.4)
            return {"side": pred, "conf": conf, "reason": f"M06: Run={rlen}≥5, p_brk={brk_p:.2f}"}
        # Cầu ổn định entropy thấp + run ngắn → theo
        if ent < 0.5 and rlen <= 3:
            pred = last; conf = _clamp(0.54 + theo_p*0.2)
            return {"side": pred, "conf": conf, "reason": f"M06: Ổn định, theo {last}"}
        # Markov quyết định
        if brk_p > 0.55:
            pred = _opp(last)
            return {"side": pred, "conf": _clamp(0.52+brk_p*0.2), "reason": f"M06: p_brk={brk_p:.2f}>0.55→bẻ"}
        pred = last
        return {"side": pred, "conf": _clamp(0.52+theo_p*0.2), "reason": f"M06: p_theo={theo_p:.2f}→theo"}


class M07_WeightEqualize:
    """Model 7: Cân bằng trọng số từng model khi chênh lệch quá cao"""
    name = "M07_WEIGHT_EQ"; group = "Meta"
    def __init__(self): self.w = 1.0; self.model_scores: Dict[str,float] = {}

    # Mini: tính độ lệch chuẩn trọng số
    def _mini_std(self, weights):
        vals = list(weights.values())
        if not vals: return 0.0
        mu = sum(vals)/len(vals)
        return math.sqrt(sum((v-mu)**2 for v in vals)/len(vals))

    def equalize(self, weights: Dict[str, float]) -> Dict[str, float]:
        if not weights: return {}
        std = self._mini_std(weights)
        if std > 0.3:  # chênh lệch cao → kéo về gần trung bình
            mu = sum(weights.values())/len(weights)
            new = {k: mu + (v-mu)*0.5 for k,v in weights.items()}
            return sub_weight_normalize(new)
        return sub_weight_normalize(weights)

    def predict(self, seq, **kw) -> Dict:
        return {"side": None, "conf": 0.5, "reason": "M07: Meta-weight equalizer"}


class M08_CauXau:
    """Model 8: Nhận biết cầu xấu và giảm trọng số"""
    name = "M08_CAU_XAU"; group = "Quality"
    def __init__(self): self.w = 1.0; self.is_bad = False

    # Mini: điểm chất lượng cầu
    def _mini_quality_score(self, seq):
        ent = sub_entropy(seq, 10)
        ac  = abs(sub_autocorr(seq))
        runs = _run_lengths(seq[-10:]) if len(seq) >= 10 else [1]
        max_run = max(runs); avg_run = sum(runs)/len(runs)
        # Chất lượng cao: ent vừa, ac rõ, có run >= 2
        score = (1 - ent*0.4) + ac*0.3 + min(1, max_run/4)*0.3
        return score

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 10:
            return {"side": None, "conf": 0.5, "reason": "M08: Thiếu", "bad_cau": False}
        bad = sub_cau_xau_detector(seq)
        self.is_bad = bad
        q = self._mini_quality_score(seq)
        if bad:
            last, _ = _last_run(seq)
            return {"side": _opp(last), "conf": 0.51, "reason": f"M08: Cầu xấu q={q:.2f}→thận trọng", "bad_cau": True}
        return {"side": None, "conf": q*0.6, "reason": f"M08: Cầu tốt q={q:.2f}", "bad_cau": False}


class M09_CauCoban:
    """Model 9: Nhận biết cầu cơ bản mở rộng (1-2-1, 2-1-2, 3-1, 1-3,...)"""
    name = "M09_CAU_COBAN"; group = "Pattern"
    def __init__(self): self.w = 1.0

    # Mini: nhận dạng chuỗi run length
    def _mini_recognize(self, runs):
        s = "-".join(str(r) for r in runs[-4:]) if runs else ""
        patterns = {
            "1-2-1": ("COMPLEX", "bẻ"),  "2-1-2": ("COMPLEX", "theo"),
            "3-1": ("3-1", "bẻ"),         "1-3": ("1-3", "theo"),
            "1-1-1": ("ALTERNATING", "bẻ"), "2-2": ("2-2", "bẻ"),
            "3-3": ("3-3", "bẻ"),          "1-1": ("1-1", "bẻ"),
        }
        for pat, (name, action) in patterns.items():
            if s.endswith(pat): return name, action
        return "UNKNOWN", "neutral"

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 8:
            return {"side": None, "conf": 0.5, "reason": "M09: Thiếu"}
        runs = _run_lengths(seq)
        last, rlen = _last_run(seq)
        name, action = self._mini_recognize(runs)
        if action == "bẻ":
            pred = _opp(last)
            return {"side": pred, "conf": 0.64, "reason": f"M09: {name}→bẻ→{pred}"}
        if action == "theo":
            return {"side": last, "conf": 0.62, "reason": f"M09: {name}→theo→{last}"}
        return {"side": None, "conf": 0.5, "reason": f"M09: {name} không rõ"}


class M10_XacSuatBe:
    """Model 10: Tính xác suất bẻ cầu tổng hợp"""
    name = "M10_XS_BE"; group = "Probability"
    def __init__(self): self.w = 1.0

    # Mini: Bayesian update bẻ cầu
    def _mini_bayes_break(self, prior, run_len, total_obs):
        # Prior từ lịch sử + điều chỉnh theo run_len
        likelihood = min(0.9, 0.5 + run_len * 0.05)
        posterior = (likelihood * prior) / (likelihood * prior + (1-likelihood)*(1-prior))
        # Smooth với total_obs
        alpha = min(1.0, total_obs / 50)
        return prior * (1-alpha) + posterior * alpha

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 10:
            return {"side": None, "conf": 0.5, "reason": "M10: Thiếu"}
        last, rlen = _last_run(seq)
        hist_brk = sub_break_prob_historical(seq, rlen)
        bayes_brk = self._mini_bayes_break(0.5, rlen, len(seq))
        combined = hist_brk * 0.6 + bayes_brk * 0.4
        if combined > 0.55:
            conf = _clamp(0.52 + (combined-0.5)*0.6)
            return {"side": _opp(last), "conf": conf, "reason": f"M10: p_be={combined:.2f}→bẻ {last}"}
        elif combined < 0.45:
            conf = _clamp(0.52 + (0.5-combined)*0.6)
            return {"side": last, "conf": conf, "reason": f"M10: p_theo={1-combined:.2f}→theo {last}"}
        return {"side": None, "conf": 0.5, "reason": f"M10: Không rõ p_be={combined:.2f}"}


class M11_DiceBienDong:
    """Model 11: Nhận diện biến động xúc xắc theo lịch sử"""
    name = "M11_DICE_VARI"; group = "Dice"
    def __init__(self): self.w = 1.0

    # Mini: phân tích zone transition
    def _mini_zone_transition(self, zones):
        if len(zones) < 4: return "STABLE"
        transitions = sum(1 for i in range(1,len(zones)) if zones[i] != zones[i-1])
        rate = transitions / (len(zones)-1)
        if rate > 0.7: return "VOLATILE"
        if rate < 0.3: return "STABLE"
        return "NORMAL"

    def predict(self, seq, dices_history=None, sums_history=None, **kw) -> Dict:
        if not dices_history or len(dices_history) < 8:
            return {"side": None, "conf": 0.5, "reason": "M11: Thiếu dice"}
        recent_dices = list(dices_history[-15:])
        sums = [sum(d) if isinstance(d, list) and len(d)==3 else 10 for d in recent_dices]
        zones = [sub_dice_sum_zone(s) for s in sums]
        state = self._mini_zone_transition(zones)
        trend_slope = sub_sum_trend(sums, 8)
        nhacai = sub_nhacai_pattern(dices_history, 20)

        last_sum = sums[-1] if sums else 10
        last, _ = _last_run(seq)

        if nhacai["repeat_pattern"]:
            # Nhà cái lặp pattern → theo pattern
            pred = "TAI" if last_sum >= 11 else "XIU"
            return {"side": pred, "conf": 0.65, "reason": f"M11: NhaCai lặp pattern, sum={last_sum}"}

        if state == "VOLATILE":
            # Biến động mạnh → bẻ
            pred = _opp(last)
            return {"side": pred, "conf": 0.60, "reason": f"M11: Dice volatile → bẻ"}

        if trend_slope > 0.5:
            # Tổng đang tăng → TÀI
            return {"side": "TAI", "conf": _clamp(0.54+trend_slope*0.1), "reason": f"M11: Sum tăng slope={trend_slope:.2f}"}
        if trend_slope < -0.5:
            return {"side": "XIU", "conf": _clamp(0.54+abs(trend_slope)*0.1), "reason": f"M11: Sum giảm slope={trend_slope:.2f}"}

        pred = "TAI" if last_sum >= 11 else "XIU"
        return {"side": pred, "conf": 0.54, "reason": f"M11: Sum={last_sum}→{pred}"}


class M12_MultiPattern:
    """Model 12: Nhận diện nhiều mẫu cầu ngắn hơn"""
    name = "M12_MULTI_PAT"; group = "Pattern"
    def __init__(self): self.w = 1.0; self.pat_cache: Dict = {}

    # Mini: xây bảng pattern 2-6
    def _mini_build_table(self, seq, maxlen=5):
        tbl = {}
        n = len(seq)
        for plen in range(2, maxlen+1):
            for i in range(plen, n):
                pat = tuple(seq[i-plen:i])
                nxt = seq[i]
                if pat not in tbl: tbl[pat] = Counter()
                tbl[pat][nxt] += 1
        return tbl

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 12:
            return {"side": None, "conf": 0.5, "reason": "M12: Thiếu"}
        tbl = self._mini_build_table(seq, 5)
        best = None; best_conf = 0.52
        for plen in range(5, 1, -1):
            if len(seq) < plen: continue
            pat = tuple(seq[-plen:])
            if pat in tbl:
                cnt = tbl[pat]; total = sum(cnt.values())
                if total < 3: continue
                for side in ("TAI", "XIU"):
                    rate = cnt.get(side, 0)/total
                    if rate >= 0.58:
                        conf = _clamp(0.52 + (rate-0.5)*0.7)
                        if conf > best_conf:
                            best = (side, conf, f"M12: pat-{plen} {side} rate={rate:.2f}")
                            best_conf = conf
        if best:
            return {"side": best[0], "conf": best[1], "reason": best[2]}
        return {"side": None, "conf": 0.5, "reason": "M12: Không tìm thấy pattern đủ mạnh"}


class M13_Performance:
    """Model 13: Đánh giá hiệu suất và điều chỉnh trọng số"""
    name = "M13_PERF"; group = "Meta"
    def __init__(self):
        self.w = 1.0
        self.model_perf: Dict[str, deque] = {}  # {model_name: deque[0/1]}

    # Mini: tính moving accuracy
    def _mini_ma(self, hits: deque, n=20) -> float:
        recent = list(hits)[-n:]
        return sum(recent)/len(recent) if recent else 0.5

    def update_perf(self, model_name: str, hit: bool):
        if model_name not in self.model_perf:
            self.model_perf[model_name] = deque(maxlen=50)
        self.model_perf[model_name].append(1 if hit else 0)

    def get_weights(self) -> Dict[str, float]:
        weights = {}
        for name, hits in self.model_perf.items():
            acc = self._mini_ma(hits, 20)
            # Trọng số theo accuracy, baseline 0.5
            weights[name] = max(0.1, (acc - 0.3) * 2.5)
        return sub_weight_normalize(weights) if weights else {}

    def predict(self, seq, **kw) -> Dict:
        ws = self.get_weights()
        if ws:
            best = max(ws, key=ws.get)
            top_w = ws[best]
            return {"side": None, "conf": 0.5, "reason": f"M13: Best={best}({top_w:.2f})", "weights": ws}
        return {"side": None, "conf": 0.5, "reason": "M13: Chưa có dữ liệu hiệu suất"}


class M14_XsBeCauTrend:
    """Model 14: Tính xác suất bẻ cầu xu hướng"""
    name = "M14_XS_BE_TREND"; group = "Probability"
    def __init__(self): self.w = 1.0

    # Mini: tỉ lệ bẻ sau chuỗi xu hướng mạnh
    def _mini_trend_break_rate(self, seq, trend_dir, window=5):
        if len(seq) < window*2: return 0.5
        breaks = total = 0
        for i in range(window, len(seq)):
            w = seq[i-window:i]
            t = w.count("TAI"); x = w.count("XIU")
            dominant = "TAI" if t > x else "XIU"
            if dominant == trend_dir:
                total += 1
                if seq[i] != dominant: breaks += 1
        return breaks/total if total > 0 else 0.5

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 20:
            return {"side": None, "conf": 0.5, "reason": "M14: Thiếu"}
        trend = sub_trend_direction(seq)
        if trend == "NEUTRAL":
            return {"side": None, "conf": 0.5, "reason": "M14: Trend neutral"}
        trend_side = "TAI" if trend == "UP" else "XIU"
        brk_rate = self._mini_trend_break_rate(seq, trend_side, 5)
        if brk_rate > 0.6:
            pred = _opp(trend_side)
            return {"side": pred, "conf": _clamp(0.52+brk_rate*0.3), "reason": f"M14: Trend {trend} break_rate={brk_rate:.2f}→{pred}"}
        return {"side": trend_side, "conf": _clamp(0.52+(1-brk_rate)*0.2), "reason": f"M14: Theo trend {trend}"}


class M15_ShouldFollow:
    """Model 15: Suy nghĩ có nên bắt theo xu hướng không"""
    name = "M15_FOLLOW"; group = "Strategy"
    def __init__(self): self.w = 1.0

    # Mini: điểm quyết định follow
    def _mini_follow_score(self, trend, vol, ent, run_len):
        score = 0.0
        if trend != "NEUTRAL": score += 0.3
        if vol < 0.4: score += 0.2       # ít biến động → nên follow
        if ent < 0.7: score += 0.2       # ít hỗn loạn → nên follow
        if run_len <= 3: score += 0.15    # run chưa quá dài → nên theo
        return score

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 10:
            return {"side": None, "conf": 0.5, "reason": "M15: Thiếu"}
        trend = sub_trend_direction(seq)
        vol   = sub_volatility_index(seq)
        ent   = sub_entropy(seq)
        last, rlen = _last_run(seq)
        score = self._mini_follow_score(trend, vol, ent, rlen)
        if score >= 0.5:
            trend_side = "TAI" if trend == "UP" else ("XIU" if trend == "DOWN" else last)
            return {"side": trend_side, "conf": _clamp(0.52+score*0.3), "reason": f"M15: Nên follow score={score:.2f}"}
        return {"side": _opp(last), "conf": 0.54, "reason": f"M15: Không nên follow score={score:.2f}→bẻ"}


class M16_XsSuatBe:
    """Model 16: Tính xác suất bẻ cầu tổng hợp đa nguồn"""
    name = "M16_XS_BE2"; group = "Probability"
    def __init__(self): self.w = 1.0

    # Mini: hàm tổng hợp nhiều xác suất bẻ
    def _mini_combine_break(self, p_list):
        if not p_list: return 0.5
        # Geometric mean
        log_sum = sum(math.log(max(0.01, p)) for p in p_list)
        return math.exp(log_sum/len(p_list))

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 15:
            return {"side": None, "conf": 0.5, "reason": "M16: Thiếu"}
        last, rlen = _last_run(seq)
        p1 = sub_break_prob_historical(seq, rlen)
        p2 = 0.5 + (rlen - 2) * 0.04
        p3 = 1 - sub_autocorr(seq, 1) * 0.5
        vol = sub_volatility_index(seq)
        p4 = 0.5 + (vol - 0.5) * 0.3
        combined = self._mini_combine_break([p1, _clamp(p2,0.4,0.9), _clamp(p3,0.4,0.9), _clamp(p4,0.4,0.9)])
        if combined > 0.57:
            return {"side": _opp(last), "conf": _clamp(0.52+combined*0.2), "reason": f"M16: p_be_combined={combined:.2f}→bẻ"}
        elif combined < 0.43:
            return {"side": last, "conf": _clamp(0.52+(1-combined)*0.2), "reason": f"M16: p_theo={1-combined:.2f}→theo"}
        return {"side": None, "conf": 0.5, "reason": f"M16: Không rõ p={combined:.2f}"}


class M17_WeightBalance:
    """Model 17: Cân bằng trọng số toàn bộ hệ thống"""
    name = "M17_BAL"; group = "Meta"
    def __init__(self): self.w = 1.0

    # Mini: phát hiện model nào đang quá dominant
    def _mini_dominant(self, weights):
        if not weights: return None
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}

    def balance(self, weights: Dict[str, float], perf: Dict[str, float]) -> Dict[str, float]:
        if not weights: return {}
        normed = self._mini_dominant(weights)
        # Kết hợp trọng số hiện tại và hiệu suất
        balanced = {}
        for k in normed:
            w_cur = normed.get(k, 1/len(normed))
            w_perf = perf.get(k, 0.5)
            balanced[k] = w_cur * 0.5 + w_perf * 0.5
        return sub_weight_normalize(balanced)

    def predict(self, seq, **kw) -> Dict:
        return {"side": None, "conf": 0.5, "reason": "M17: Meta-balancer"}


class M18_TrendNganHan:
    """Model 18: Nhận biết xu hướng cầu và đoán theo xu hướng ngắn hạn"""
    name = "M18_TREND_SHORT"; group = "Trend"
    def __init__(self): self.w = 1.0

    # Mini: phát hiện micro-trend 3 phiên
    def _mini_micro_trend(self, seq, n=3):
        if len(seq) < n: return None
        w = seq[-n:]
        t = w.count("TAI"); x = w.count("XIU")
        if t == n: return "TAI_STREAK"
        if x == n: return "XIU_STREAK"
        if w[-2] == w[-1]: return f"MINI_{w[-1]}"
        return None

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 6:
            return {"side": None, "conf": 0.5, "reason": "M18: Thiếu"}
        micro = self._mini_micro_trend(seq, 3)
        last, rlen = _last_run(seq)
        ac = sub_autocorr(seq, 1)
        if micro == "TAI_STREAK":
            # 3 TÀI liên tiếp → xét bẻ
            if rlen >= 4:
                return {"side": "XIU", "conf": 0.65, "reason": "M18: TÀI streak≥4→bẻ XIU"}
            return {"side": "TAI", "conf": 0.60, "reason": "M18: TÀI streak ngắn→theo"}
        if micro == "XIU_STREAK":
            if rlen >= 4:
                return {"side": "TAI", "conf": 0.65, "reason": "M18: XIU streak≥4→bẻ TAI"}
            return {"side": "XIU", "conf": 0.60, "reason": "M18: XIU streak ngắn→theo"}
        if micro and micro.startswith("MINI_"):
            side = micro.split("_")[1]
            return {"side": side, "conf": 0.57, "reason": f"M18: Micro trend {side}"}
        # Dùng autocorr
        if ac > 0.15:
            return {"side": last, "conf": _clamp(0.52+ac*0.3), "reason": f"M18: AC={ac:.2f}→theo {last}"}
        if ac < -0.15:
            return {"side": _opp(last), "conf": _clamp(0.52+abs(ac)*0.3), "reason": f"M18: AC={ac:.2f}→bẻ {last}"}
        return {"side": None, "conf": 0.5, "reason": f"M18: AC neutral={ac:.2f}"}


class M19_PopularTrend:
    """Model 19: Các xu hướng phổ biến (Martingale pattern, clustering,...)"""
    name = "M19_POPULAR"; group = "Pattern"
    def __init__(self): self.w = 1.0

    # Mini: phát hiện clustering pattern
    def _mini_cluster(self, seq, n=8):
        if len(seq) < n: return None
        w = seq[-n:]
        # Clustering: >60% cùng chiều
        t = w.count("TAI"); x = w.count("XIU")
        if t/n >= 0.65: return "CLUSTER_TAI"
        if x/n >= 0.65: return "CLUSTER_XIU"
        # Zigzag
        zz = sum(1 for i in range(1,len(w)) if w[i]!=w[i-1])
        if zz >= n*0.75: return "ZIGZAG"
        return None

    def predict(self, seq, **kw) -> Dict:
        if len(seq) < 10:
            return {"side": None, "conf": 0.5, "reason": "M19: Thiếu"}
        cluster = self._mini_cluster(seq, 8)
        last, _ = _last_run(seq)
        if cluster == "CLUSTER_TAI":
            # Tập trung TÀI → chú ý cân bằng
            return {"side": "XIU", "conf": 0.62, "reason": "M19: Cluster TÀI→cân bằng XIU"}
        if cluster == "CLUSTER_XIU":
            return {"side": "TAI", "conf": 0.62, "reason": "M19: Cluster XIU→cân bằng TAI"}
        if cluster == "ZIGZAG":
            return {"side": _opp(last), "conf": 0.67, "reason": "M19: Zigzag→bẻ"}
        # Markov 2nd order
        if len(seq) >= 15:
            last2 = tuple(seq[-2:])
            p = sub_triple_freq(seq, (last2[0], last2[1], "TAI"))
            if p > 0.6: return {"side": "TAI", "conf": _clamp(0.52+p*0.2), "reason": f"M19: Markov2 p_TAI={p:.2f}"}
            if p < 0.4: return {"side": "XIU", "conf": _clamp(0.52+(1-p)*0.2), "reason": f"M19: Markov2 p_TAI={p:.2f}→XIU"}
        return {"side": None, "conf": 0.5, "reason": "M19: Không có pattern rõ"}


class M20_MaxPerformance:
    """Model 20: Max Performance — kết hợp tất cả signals mạnh nhất"""
    name = "M20_MAX_PERF"; group = "Ensemble"
    def __init__(self): self.w = 1.5  # trọng số cao hơn

    # Mini: lấy tín hiệu mạnh nhất
    def _mini_top_signals(self, signals, n=5):
        return sorted(signals, key=lambda s: s.get("conf", 0), reverse=True)[:n]

    def predict(self, seq, all_signals=None, **kw) -> Dict:
        if not all_signals or len(seq) < 10:
            last, _ = _last_run(seq)
            return {"side": _opp(last) if seq else "TAI", "conf": 0.52, "reason": "M20: Fallback"}
        top = self._mini_top_signals(all_signals, 5)
        tai_score = sum(s["conf"] for s in top if s.get("side")=="TAI")
        xiu_score = sum(s["conf"] for s in top if s.get("side")=="XIU")
        total = tai_score + xiu_score
        if total == 0: return {"side": None, "conf": 0.5, "reason": "M20: Không có tín hiệu"}
        if tai_score > xiu_score:
            conf = _clamp(tai_score/total + 0.08)
            return {"side": "TAI", "conf": conf, "reason": f"M20: MaxPerf TAI={tai_score:.2f}>XIU={xiu_score:.2f}"}
        conf = _clamp(xiu_score/total + 0.08)
        return {"side": "XIU", "conf": conf, "reason": f"M20: MaxPerf XIU={xiu_score:.2f}>TAI={tai_score:.2f}"}


class M21_GlobalBalance:
    """Model 21: Cân bằng tất cả khi thấy chênh lệch cao"""
    name = "M21_GLOBAL_BAL"; group = "Meta"
    def __init__(self): self.w = 1.0

    # Mini: phát hiện extreme imbalance
    def _mini_extreme(self, votes):
        if not votes: return None, 0.5
        tai = votes.count("TAI"); xiu = votes.count("XIU"); total = len(votes)
        if total == 0: return None, 0.5
        tai_r = tai/total
        if tai_r > 0.80: return "XIU", _clamp(0.52+(tai_r-0.5)*0.4)
        if tai_r < 0.20: return "TAI", _clamp(0.52+(0.5-tai_r)*0.4)
        return None, 0.5

    def predict(self, seq, ensemble_votes=None, **kw) -> Dict:
        if not ensemble_votes:
            return {"side": None, "conf": 0.5, "reason": "M21: Chờ ensemble"}
        pred, conf = self._mini_extreme(ensemble_votes)
        if pred:
            return {"side": pred, "conf": conf, "reason": f"M21: Extreme imbalance→{pred}"}
        return {"side": None, "conf": 0.5, "reason": "M21: Ensemble cân bằng"}


class M22_NhaCai:
    """Model 22: Nhận biết cầu gãy, hiểu ý định nhà cái, đọc xúc xắc"""
    name = "M22_NHACAI"; group = "Intelligence"
    def __init__(self):
        self.w = 1.2  # trọng số cao hơn vì đây là model đặc biệt
        self.gai_history = deque(maxlen=20)

    # Mini: phát hiện cầu gãy
    def _mini_detect_gai(self, seq, expected_run=None):
        """Cầu gãy: run kết thúc sớm hơn expected"""
        if len(seq) < 6: return False
        last, rlen = _last_run(seq)
        # Nếu đang trong cầu bệt mà đột ngột gãy
        if expected_run and rlen < expected_run*0.5:
            return True
        # Phát hiện gãy từ lịch sử run
        runs = _run_lengths(seq)
        if len(runs) >= 4:
            avg_run = sum(runs[:-1]) / len(runs[:-1])
            if runs[-1] < avg_run * 0.4:
                return True
        return False

    def predict(self, seq, dices_history=None, **kw) -> Dict:
        if len(seq) < 10:
            return {"side": None, "conf": 0.5, "reason": "M22: Thiếu"}
        last, rlen = _last_run(seq)
        gai = self._mini_detect_gai(seq)
        # Phân tích xúc xắc nếu có
        dice_signal = None
        if dices_history and len(dices_history) >= 5:
            nhacai = sub_nhacai_pattern(dices_history, 10)
            dom = nhacai["dominant_zone"]
            avg_sum = nhacai["avg_sum"]
            if nhacai["repeat_pattern"]:
                # Nhà cái đang lặp → theo
                dice_signal = ("TAI" if avg_sum >= 11 else "XIU", 0.68, f"NhaCai lặp zone={dom}")
            elif dom == "HIGH":
                dice_signal = ("TAI", 0.62, "NhaCai zone=HIGH")
            elif dom == "LOW":
                dice_signal = ("XIU", 0.62, "NhaCai zone=LOW")

        if gai:
            self.gai_history.append(1)
            # Cầu gãy → nhà cái đang điều chỉnh → bẻ hoặc cẩn thận
            pred = _opp(last)
            conf = 0.63
            reason = f"M22: Cầu gãy phát hiện run={rlen}→{pred}"
            if dice_signal:
                pred2, c2, r2 = dice_signal
                # Ưu tiên dice nếu mạnh hơn
                if c2 > conf:
                    return {"side": pred2, "conf": c2, "reason": f"M22: {r2} (gãy+dice)"}
            return {"side": pred, "conf": conf, "reason": reason}
        self.gai_history.append(0)
        if dice_signal:
            pred2, c2, r2 = dice_signal
            return {"side": pred2, "conf": c2, "reason": f"M22: {r2}"}
        # Không gãy, không dice signal rõ → phân tích thống kê nhà cái
        # Nhà cái thường cân bằng dài hạn
        bal = sub_balance_ratio(seq, min(30, len(seq)))
        if bal > 0.65:
            return {"side": "XIU", "conf": 0.60, "reason": f"M22: NhaCai cân bằng lại (TAI={bal:.2f})"}
        if bal < 0.35:
            return {"side": "TAI", "conf": 0.60, "reason": f"M22: NhaCai cân bằng lại (XIU={1-bal:.2f})"}
        return {"side": None, "conf": 0.5, "reason": f"M22: NhaCai cân bằng {bal:.2f}"}


# ══════════════════════════════════════════════════════════════════════════
#  40 MODEL PHỤ TRỢ THÊM (hàm nhỏ, dùng trong ensemble)
# ══════════════════════════════════════════════════════════════════════════
# Mỗi class dưới = 1 model phụ trợ nhỏ

class PA01_Markov1:
    name = "PA01_MK1"; group = "Markov"
    def __init__(self): self.w = 0.8
    def predict(self, seq, **kw):
        if len(seq) < 10: return {"side": None, "conf": 0.5, "reason": "PA01"}
        last = seq[-1]
        p = sub_pair_freq(seq, (last, "TAI"))
        if p > 0.55: return {"side": "TAI", "conf": _clamp(0.52+p*0.2), "reason": f"PA01: MK1 p_TAI={p:.2f}"}
        if p < 0.45: return {"side": "XIU", "conf": _clamp(0.52+(1-p)*0.2), "reason": f"PA01: MK1 p_XIU={1-p:.2f}"}
        return {"side": None, "conf": 0.5, "reason": f"PA01: MK1 neutral p={p:.2f}"}

class PA02_Markov2:
    name = "PA02_MK2"; group = "Markov"
    def __init__(self): self.w = 0.9
    def predict(self, seq, **kw):
        if len(seq) < 15: return {"side": None, "conf": 0.5, "reason": "PA02"}
        last2 = tuple(seq[-2:])
        p = sub_triple_freq(seq, (last2[0], last2[1], "TAI"))
        if p > 0.58: return {"side": "TAI", "conf": _clamp(0.52+p*0.25), "reason": f"PA02: MK2 p={p:.2f}"}
        if p < 0.42: return {"side": "XIU", "conf": _clamp(0.52+(1-p)*0.25), "reason": f"PA02: MK2 p={p:.2f}"}
        return {"side": None, "conf": 0.5, "reason": f"PA02: MK2 p={p:.2f}"}

class PA03_EMA_Cross:
    name = "PA03_EMA"; group = "Trend"
    def __init__(self): self.w = 0.8
    def predict(self, seq, **kw):
        if len(seq) < 15: return {"side": None, "conf": 0.5, "reason": "PA03"}
        binary = [1 if v=="TAI" else 0 for v in seq]
        def ema(s, n):
            a = 2/(n+1); e = s[-n]
            for v in s[-n+1:]: e = a*v+(1-a)*e
            return e
        e3 = ema(binary, 3); e8 = ema(binary, min(8,len(binary)))
        if e3 > e8+0.08: return {"side": "TAI", "conf": 0.60, "reason": f"PA03: EMA3>{e3:.2f}>EMA8={e8:.2f}"}
        if e3 < e8-0.08: return {"side": "XIU", "conf": 0.60, "reason": f"PA03: EMA3={e3:.2f}<EMA8={e8:.2f}"}
        return {"side": None, "conf": 0.5, "reason": "PA03: EMA cross neutral"}

class PA04_RSI:
    name = "PA04_RSI"; group = "Oscillator"
    def __init__(self): self.w = 0.7
    def predict(self, seq, **kw):
        if len(seq) < 14: return {"side": None, "conf": 0.5, "reason": "PA04"}
        binary = [1 if v=="TAI" else 0 for v in seq[-14:]]
        gains = [max(0, binary[i]-binary[i-1]) for i in range(1,14)]
        losses = [max(0, binary[i-1]-binary[i]) for i in range(1,14)]
        avg_g = sum(gains)/13; avg_l = sum(losses)/13
        rsi = 100 - 100/(1+avg_g/avg_l) if avg_l > 0 else 100
        if rsi > 70: return {"side": "XIU", "conf": 0.62, "reason": f"PA04: RSI={rsi:.0f}>70→XIU"}
        if rsi < 30: return {"side": "TAI", "conf": 0.62, "reason": f"PA04: RSI={rsi:.0f}<30→TAI"}
        return {"side": None, "conf": 0.5, "reason": f"PA04: RSI={rsi:.0f} neutral"}

class PA05_Entropy:
    name = "PA05_ENT"; group = "Information"
    def __init__(self): self.w = 0.6
    def predict(self, seq, **kw):
        if len(seq) < 10: return {"side": None, "conf": 0.5, "reason": "PA05"}
        ent = sub_entropy(seq, 10); last, _ = _last_run(seq)
        if ent > 0.95: return {"side": _opp(last), "conf": 0.54, "reason": f"PA05: High entropy={ent:.2f}→bẻ"}
        if ent < 0.5:  return {"side": last, "conf": 0.57, "reason": f"PA05: Low entropy={ent:.2f}→theo"}
        return {"side": None, "conf": 0.5, "reason": f"PA05: Entropy={ent:.2f}"}

class PA06_ZScore:
    name = "PA06_ZSCORE"; group = "Statistical"
    def __init__(self): self.w = 0.7
    def predict(self, seq, **kw):
        if len(seq) < 20: return {"side": None, "conf": 0.5, "reason": "PA06"}
        z = sub_zscore_tai(seq, 20)
        if z > 1.5: return {"side": "XIU", "conf": _clamp(0.52+min(0.15,abs(z)*0.05)), "reason": f"PA06: Z={z:.2f}>1.5→XIU"}
        if z < -1.5: return {"side": "TAI", "conf": _clamp(0.52+min(0.15,abs(z)*0.05)), "reason": f"PA06: Z={z:.2f}<-1.5→TAI"}
        return {"side": None, "conf": 0.5, "reason": f"PA06: Z={z:.2f}"}

class PA07_RunTest:
    name = "PA07_RUNT"; group = "Statistical"
    def __init__(self): self.w = 0.6
    def predict(self, seq, **kw):
        if len(seq) < 15: return {"side": None, "conf": 0.5, "reason": "PA07"}
        p = sub_runs_test(seq)  # p_value nhỏ = có cấu trúc
        last, _ = _last_run(seq)
        ac = sub_autocorr(seq, 1)
        if p < 0.2 and ac > 0.1: return {"side": last, "conf": 0.57, "reason": f"PA07: Structure p={p:.2f}→theo"}
        if p < 0.2 and ac < -0.1: return {"side": _opp(last), "conf": 0.57, "reason": f"PA07: Structure p={p:.2f}→bẻ"}
        return {"side": None, "conf": 0.5, "reason": f"PA07: Random p={p:.2f}"}

class PA08_MomentumShort:
    name = "PA08_MOM3"; group = "Momentum"
    def __init__(self): self.w = 0.8
    def predict(self, seq, **kw):
        if len(seq) < 8: return {"side": None, "conf": 0.5, "reason": "PA08"}
        mom = sub_momentum(seq, 3, 8)
        if mom > 0.1: return {"side": "TAI", "conf": _clamp(0.52+abs(mom)*0.5), "reason": f"PA08: Mom3={mom:.2f}→TAI"}
        if mom < -0.1: return {"side": "XIU", "conf": _clamp(0.52+abs(mom)*0.5), "reason": f"PA08: Mom3={mom:.2f}→XIU"}
        return {"side": None, "conf": 0.5, "reason": f"PA08: Mom={mom:.2f}"}

class PA09_Reversion:
    name = "PA09_REV"; group = "Mean Reversion"
    def __init__(self): self.w = 0.7
    def predict(self, seq, **kw):
        if len(seq) < 20: return {"side": None, "conf": 0.5, "reason": "PA09"}
        bal = sub_balance_ratio(seq, 20)
        if bal > 0.70: return {"side": "XIU", "conf": _clamp(0.53+(bal-0.5)*0.4), "reason": f"PA09: Rev bal={bal:.2f}→XIU"}
        if bal < 0.30: return {"side": "TAI", "conf": _clamp(0.53+(0.5-bal)*0.4), "reason": f"PA09: Rev bal={bal:.2f}→TAI"}
        return {"side": None, "conf": 0.5, "reason": f"PA09: Balanced bal={bal:.2f}"}

class PA10_Cluster:
    name = "PA10_CLUSTER"; group = "Pattern"
    def __init__(self): self.w = 0.7
    def predict(self, seq, **kw):
        if len(seq) < 12: return {"side": None, "conf": 0.5, "reason": "PA10"}
        # Phát hiện cluster 3 phiên
        last3 = seq[-3:]
        t3, x3 = last3.count("TAI"), last3.count("XIU")
        last, _ = _last_run(seq)
        if t3 == 3: # 3 TÀI liên tiếp
            brk = sub_break_prob_historical(seq, 3)
            pred = _opp(last) if brk > 0.5 else last
            return {"side": pred, "conf": _clamp(0.55+abs(brk-0.5)*0.3), "reason": f"PA10: 3TAI brk={brk:.2f}"}
        if x3 == 3:
            brk = sub_break_prob_historical(seq, 3)
            pred = _opp(last) if brk > 0.5 else last
            return {"side": pred, "conf": _clamp(0.55+abs(brk-0.5)*0.3), "reason": f"PA10: 3XIU brk={brk:.2f}"}
        return {"side": None, "conf": 0.5, "reason": "PA10: Không cluster"}

# PA11-PA40: Các model phụ trợ nhỏ tiếp theo
class PA11_SumBand:
    name="PA11_SBAND";group="Dice"
    def __init__(self):self.w=0.7
    def predict(self,seq,sums_history=None,**kw):
        if not sums_history or len(sums_history)<5: return {"side":None,"conf":0.5,"reason":"PA11"}
        last_sum=list(sums_history)[-1]; trend=sub_sum_trend(list(sums_history),5)
        pred="TAI" if last_sum>=11 else "XIU"
        if trend>0.5: pred="TAI"
        elif trend<-0.5: pred="XIU"
        return {"side":pred,"conf":_clamp(0.53+abs(trend)*0.1),"reason":f"PA11: sum={last_sum} slope={trend:.2f}"}

class PA12_DiceVar:
    name="PA12_DVAR";group="Dice"
    def __init__(self):self.w=0.6
    def predict(self,seq,dices_history=None,**kw):
        if not dices_history or len(dices_history)<3: return {"side":None,"conf":0.5,"reason":"PA12"}
        d=list(dices_history)[-1]
        if not isinstance(d,list) or len(d)<3: return {"side":None,"conf":0.5,"reason":"PA12"}
        var=sub_dice_variance(d); s=sum(d)
        pred="TAI" if s>=11 else "XIU"
        conf=0.57 if var<2 else 0.53  # phân tán thấp → đáng tin hơn
        return {"side":pred,"conf":conf,"reason":f"PA12: sum={s} var={var:.2f}"}

class PA13_AntiStreak:
    name="PA13_ANTI";group="Strategy"
    def __init__(self):self.w=1.0  # nâng weight
    def predict(self,seq,**kw):
        if len(seq)<8: return {"side":None,"conf":0.5,"reason":"PA13"}
        last,rlen=_last_run(seq)
        # Giảm ngưỡng: run>=3 bắt đầu xem xét bẻ
        if rlen>=3:
            brk=sub_break_prob_historical(seq,rlen)
            # run=3: chỉ bẻ nếu lịch sử gãy >50%, run>=5: luôn bẻ
            if rlen>=5 or brk>0.50:
                return {"side":_opp(last),"conf":_clamp(0.56+rlen*0.025+(brk-0.5)*0.3),"reason":f"PA13: AntiStreak run={rlen} brk={brk:.2f}"}
        return {"side":None,"conf":0.5,"reason":f"PA13: run={rlen}<3 hoặc brk thấp"}

class PA14_MiniCau11:
    name="PA14_11";group="Pattern"
    def __init__(self):self.w=0.9
    def predict(self,seq,**kw):
        if len(seq)<6: return {"side":None,"conf":0.5,"reason":"PA14"}
        last5=seq[-5:]
        alt=sum(1 for i in range(1,len(last5)) if last5[i]!=last5[i-1])
        last,_=_last_run(seq)
        if alt>=3: return {"side":_opp(last),"conf":_clamp(0.57+alt*0.03),"reason":f"PA14: Alt={alt}/4→bẻ"}
        return {"side":None,"conf":0.5,"reason":f"PA14: alt={alt}"}

class PA15_SumZone:
    name="PA15_ZONE";group="Dice"
    def __init__(self):self.w=0.6
    def predict(self,seq,sums_history=None,**kw):
        if not sums_history or len(sums_history)<5: return {"side":None,"conf":0.5,"reason":"PA15"}
        last5=[s for s in list(sums_history)[-5:]]
        zones=[sub_dice_sum_zone(s) for s in last5]
        from collections import Counter; zc=Counter(zones)
        dom=zc.most_common(1)[0][0]
        pred="TAI" if dom in("HIGH","MID_HIGH") else "XIU"
        return {"side":pred,"conf":0.56,"reason":f"PA15: DomZone={dom}"}

class PA16_MiniMarkov3:
    name="PA16_MK3";group="Markov"
    def __init__(self):self.w=0.85
    def predict(self,seq,**kw):
        if len(seq)<20: return {"side":None,"conf":0.5,"reason":"PA16"}
        if len(seq)<3: return {"side":None,"conf":0.5,"reason":"PA16"}
        t3=tuple(seq[-3:])
        cnt={"TAI":0,"XIU":0}
        for i in range(3,len(seq)):
            if tuple(seq[i-3:i])==t3: cnt[seq[i]]+=1
        total=cnt["TAI"]+cnt["XIU"]
        if total<3: return {"side":None,"conf":0.5,"reason":"PA16: Ít data"}
        p=cnt["TAI"]/total
        if p>0.60: return {"side":"TAI","conf":_clamp(0.52+p*0.2),"reason":f"PA16: MK3 p={p:.2f}"}
        if p<0.40: return {"side":"XIU","conf":_clamp(0.52+(1-p)*0.2),"reason":f"PA16: MK3 p={p:.2f}"}
        return {"side":None,"conf":0.5,"reason":f"PA16: MK3 neutral p={p:.2f}"}

class PA17_RecentBias:
    name="PA17_RBIAS";group="Balance"
    def __init__(self):self.w=0.7
    def predict(self,seq,**kw):
        if len(seq)<8: return {"side":None,"conf":0.5,"reason":"PA17"}
        bal=sub_balance_ratio(seq,8)
        if bal>0.75: return {"side":"XIU","conf":_clamp(0.54+(bal-0.5)*0.4),"reason":f"PA17: 8p TAI heavy={bal:.2f}"}
        if bal<0.25: return {"side":"TAI","conf":_clamp(0.54+(0.5-bal)*0.4),"reason":f"PA17: 8p XIU heavy={bal:.2f}"}
        return {"side":None,"conf":0.5,"reason":f"PA17: bal={bal:.2f}"}

class PA18_StreakPenalty:
    name="PA18_STRPN";group="Strategy"
    def __init__(self):self.w=0.7
    def predict(self,seq,**kw):
        if len(seq)<5: return {"side":None,"conf":0.5,"reason":"PA18"}
        last,rlen=_last_run(seq)
        if rlen==1: return {"side":None,"conf":0.5,"reason":"PA18: run=1"}
        pen=sub_loss_penalty(rlen-1) if rlen>1 else 1.0
        pred=_opp(last) if rlen>=3 else last
        return {"side":pred,"conf":_clamp(0.52+pen*0.1),"reason":f"PA18: pen={pen:.2f} run={rlen}"}

class PA19_SumParity:
    name="PA19_PARITY";group="Dice"
    def __init__(self):self.w=0.5
    def predict(self,seq,sums_history=None,**kw):
        if not sums_history or len(sums_history)<4: return {"side":None,"conf":0.5,"reason":"PA19"}
        parity=[s%2 for s in list(sums_history)[-4:]]
        last,_=_last_run(seq)
        same=sum(1 for p in parity if p==parity[-1])
        if same==4: return {"side":_opp(last),"conf":0.56,"reason":"PA19: 4 parity same→bẻ"}
        return {"side":None,"conf":0.5,"reason":"PA19: parity mixed"}

class PA20_MediumBalance:
    name="PA20_MBAL";group="Balance"
    def __init__(self):self.w=0.7
    def predict(self,seq,**kw):
        if len(seq)<15: return {"side":None,"conf":0.5,"reason":"PA20"}
        bal=sub_balance_ratio(seq,15)
        if bal>0.67: return {"side":"XIU","conf":_clamp(0.52+(bal-0.5)*0.35),"reason":f"PA20: 15p TAI={bal:.2f}→XIU"}
        if bal<0.33: return {"side":"TAI","conf":_clamp(0.52+(0.5-bal)*0.35),"reason":f"PA20: 15p XIU={1-bal:.2f}→TAI"}
        return {"side":None,"conf":0.5,"reason":f"PA20: bal={bal:.2f}"}

class PA21_VolFilter:
    name="PA21_VOL";group="Filter"
    def __init__(self):self.w=0.6
    def predict(self,seq,**kw):
        if len(seq)<10: return {"side":None,"conf":0.5,"reason":"PA21"}
        vol=sub_volatility_index(seq,10); last,_=_last_run(seq)
        if vol>0.7: return {"side":_opp(last),"conf":_clamp(0.52+vol*0.1),"reason":f"PA21: HighVol={vol:.2f}"}
        if vol<0.3: return {"side":last,"conf":_clamp(0.52+(0.5-vol)*0.2),"reason":f"PA21: LowVol={vol:.2f}"}
        return {"side":None,"conf":0.5,"reason":f"PA21: NormVol={vol:.2f}"}

class PA22_ConsecLoss:
    name="PA22_CLOSS";group="Adaptive"
    def __init__(self):self.w=0.7; self.loss_streak=0
    def predict(self,seq,loss_streak=0,**kw):
        self.loss_streak=loss_streak
        if loss_streak>=4:
            last,_=_last_run(seq)
            return {"side":_opp(last),"conf":0.58,"reason":f"PA22: LossStreak={loss_streak}→đảo chiều"}
        return {"side":None,"conf":0.5,"reason":f"PA22: loss_streak={loss_streak}"}

class PA23_RunPat:
    name="PA23_RPAT";group="Pattern"
    def __init__(self):self.w=0.75
    def predict(self,seq,**kw):
        if len(seq)<12: return {"side":None,"conf":0.5,"reason":"PA23"}
        runs=_run_lengths(seq)
        if len(runs)<3: return {"side":None,"conf":0.5,"reason":"PA23: Ít runs"}
        last,rlen=_last_run(seq)
        avg=sum(runs[:-1])/max(1,len(runs)-1)
        # Nếu run hiện tại > avg → khả năng bẻ cao
        if rlen > avg*1.5:
            return {"side":_opp(last),"conf":_clamp(0.56+(rlen-avg)*0.05),"reason":f"PA23: run={rlen}>avg={avg:.1f}→bẻ"}
        if rlen < avg*0.5:
            return {"side":last,"conf":0.56,"reason":f"PA23: run={rlen}<avg={avg:.1f}→theo"}
        return {"side":None,"conf":0.5,"reason":f"PA23: run={rlen}≈avg={avg:.1f}"}

class PA24_Autocorr2:
    name="PA24_AC2";group="Statistical"
    def __init__(self):self.w=0.7
    def predict(self,seq,**kw):
        if len(seq)<15: return {"side":None,"conf":0.5,"reason":"PA24"}
        ac2=sub_autocorr(seq,2); last,_=_last_run(seq)
        if ac2>0.15: return {"side":last,"conf":_clamp(0.52+abs(ac2)*0.3),"reason":f"PA24: AC2={ac2:.2f}→theo"}
        if ac2<-0.15: return {"side":_opp(last),"conf":_clamp(0.52+abs(ac2)*0.3),"reason":f"PA24: AC2={ac2:.2f}→bẻ"}
        return {"side":None,"conf":0.5,"reason":f"PA24: AC2={ac2:.2f}"}

class PA25_Freq5:
    name="PA25_FREQ5";group="Pattern"
    def __init__(self):self.w=0.7
    def predict(self,seq,**kw):
        if len(seq)<20: return {"side":None,"conf":0.5,"reason":"PA25"}
        if len(seq)<5: return {"side":None,"conf":0.5,"reason":"PA25"}
        pat=tuple(seq[-5:])
        cnt={"TAI":0,"XIU":0}
        for i in range(5,len(seq)):
            if tuple(seq[i-5:i])==pat: cnt[seq[i]]+=1
        t=cnt["TAI"]+cnt["XIU"]
        if t<2: return {"side":None,"conf":0.5,"reason":"PA25: Ít data"}
        p=cnt["TAI"]/t
        if p>0.65: return {"side":"TAI","conf":_clamp(0.52+p*0.2),"reason":f"PA25: pat5 p={p:.2f}"}
        if p<0.35: return {"side":"XIU","conf":_clamp(0.52+(1-p)*0.2),"reason":f"PA25: pat5 p={p:.2f}"}
        return {"side":None,"conf":0.5,"reason":f"PA25: p={p:.2f}"}

class PA26_AlterPattern:
    name="PA26_ALTER";group="Pattern"
    def __init__(self):self.w=0.85
    def predict(self,seq,**kw):
        if len(seq)<8: return {"side":None,"conf":0.5,"reason":"PA26"}
        last6=seq[-6:]; alt=sum(1 for i in range(1,len(last6)) if last6[i]!=last6[i-1])
        last,_=_last_run(seq)
        if alt==5: return {"side":_opp(last),"conf":0.70,"reason":f"PA26: Perfect alter→bẻ"}
        if alt>=4: return {"side":_opp(last),"conf":0.63,"reason":f"PA26: Alt={alt}/5→bẻ"}
        return {"side":None,"conf":0.5,"reason":f"PA26: alt={alt}"}

class PA27_SumMean:
    name="PA27_SMEAN";group="Dice"
    def __init__(self):self.w=0.6
    def predict(self,seq,sums_history=None,**kw):
        if not sums_history or len(sums_history)<10: return {"side":None,"conf":0.5,"reason":"PA27"}
        sums=list(sums_history); mu=sum(sums)/len(sums)
        last_s=sums[-1]
        if mu>11.5: return {"side":"TAI","conf":0.56,"reason":f"PA27: mean={mu:.1f}>11.5"}
        if mu<10.5: return {"side":"XIU","conf":0.56,"reason":f"PA27: mean={mu:.1f}<10.5"}
        return {"side":None,"conf":0.5,"reason":f"PA27: mean={mu:.1f}"}

class PA28_GapDetect:
    name="PA28_GAP";group="Pattern"
    def __init__(self):self.w=0.65
    def predict(self,seq,**kw):
        if len(seq)<12: return {"side":None,"conf":0.5,"reason":"PA28"}
        # Phát hiện khoảng cách xuất hiện TAI
        positions=[i for i,v in enumerate(seq[-12:]) if v=="TAI"]
        if len(positions)<2: return {"side":None,"conf":0.5,"reason":"PA28"}
        gaps=[positions[i]-positions[i-1] for i in range(1,len(positions))]
        avg_gap=sum(gaps)/len(gaps)
        last_tai_pos=positions[-1]; dist_since=11-last_tai_pos
        if dist_since >= avg_gap*1.5:
            return {"side":"TAI","conf":0.59,"reason":f"PA28: Lâu chưa TAI dist={dist_since:.0f}avg={avg_gap:.1f}"}
        return {"side":None,"conf":0.5,"reason":f"PA28: dist={dist_since:.0f}avg={avg_gap:.1f}"}

class PA29_InverseGap:
    name="PA29_IGAP";group="Pattern"
    def __init__(self):self.w=0.65
    def predict(self,seq,**kw):
        if len(seq)<12: return {"side":None,"conf":0.5,"reason":"PA29"}
        positions=[i for i,v in enumerate(seq[-12:]) if v=="XIU"]
        if len(positions)<2: return {"side":None,"conf":0.5,"reason":"PA29"}
        gaps=[positions[i]-positions[i-1] for i in range(1,len(positions))]
        avg_gap=sum(gaps)/len(gaps); dist_since=11-positions[-1]
        if dist_since>=avg_gap*1.5:
            return {"side":"XIU","conf":0.59,"reason":f"PA29: Lâu chưa XIU dist={dist_since:.0f}avg={avg_gap:.1f}"}
        return {"side":None,"conf":0.5,"reason":f"PA29: dist={dist_since:.0f}avg={avg_gap:.1f}"}

class PA30_HalfHalf:
    name="PA30_HALF";group="Balance"
    def __init__(self):self.w=0.6
    def predict(self,seq,**kw):
        if len(seq)<10: return {"side":None,"conf":0.5,"reason":"PA30"}
        last10=seq[-10:]
        t=last10.count("TAI"); x=last10.count("XIU")
        last,_=_last_run(seq)
        if abs(t-x)<=1:  # Rất cân bằng → bẻ
            return {"side":_opp(last),"conf":0.57,"reason":f"PA30: 10p balanced T={t}X={x}→bẻ"}
        return {"side":None,"conf":0.5,"reason":f"PA30: T={t}X={x}"}

class PA31_QuadPattern:
    name="PA31_QUAD";group="Pattern"
    def __init__(self):self.w=0.75
    def predict(self,seq,**kw):
        if len(seq)<16: return {"side":None,"conf":0.5,"reason":"PA31"}
        if len(seq)<4: return {"side":None,"conf":0.5,"reason":"PA31"}
        pat4=tuple(seq[-4:])
        cnt={"TAI":0,"XIU":0}
        for i in range(4,len(seq)):
            if tuple(seq[i-4:i])==pat4: cnt[seq[i]]+=1
        t=cnt["TAI"]+cnt["XIU"]
        if t<3: return {"side":None,"conf":0.5,"reason":"PA31: Ít data"}
        p=cnt["TAI"]/t
        if p>0.65: return {"side":"TAI","conf":_clamp(0.53+p*0.2),"reason":f"PA31: quad p={p:.2f}→TAI"}
        if p<0.35: return {"side":"XIU","conf":_clamp(0.53+(1-p)*0.2),"reason":f"PA31: quad p={p:.2f}→XIU"}
        return {"side":None,"conf":0.5,"reason":f"PA31: quad p={p:.2f}"}

class PA32_SumDeviation:
    name="PA32_SDEV";group="Dice"
    def __init__(self):self.w=0.6
    def predict(self,seq,sums_history=None,**kw):
        if not sums_history or len(sums_history)<8: return {"side":None,"conf":0.5,"reason":"PA32"}
        sums=list(sums_history[-8:]); mu=sum(sums)/len(sums)
        dev=math.sqrt(sum((s-mu)**2 for s in sums)/len(sums))
        last_s=sums[-1]
        if last_s > mu+dev*1.5:
            return {"side":"XIU","conf":0.59,"reason":f"PA32: sum={last_s:.0f} high_dev→XIU"}
        if last_s < mu-dev*1.5:
            return {"side":"TAI","conf":0.59,"reason":f"PA32: sum={last_s:.0f} low_dev→TAI"}
        return {"side":None,"conf":0.5,"reason":f"PA32: sum={last_s:.0f} normal dev={dev:.2f}"}

class PA33_EvenOdd:
    name="PA33_EODD";group="Dice"
    def __init__(self):self.w=0.5
    def predict(self,seq,sums_history=None,**kw):
        if not sums_history or len(sums_history)<6: return {"side":None,"conf":0.5,"reason":"PA33"}
        last6=[s%2 for s in list(sums_history)[-6:]]
        even=last6.count(0); odd=last6.count(1)
        last,_=_last_run(seq)
        if even>=5: return {"side":_opp(last),"conf":0.56,"reason":f"PA33: 5+even→bẻ"}
        if odd>=5: return {"side":_opp(last),"conf":0.56,"reason":f"PA33: 5+odd→bẻ"}
        return {"side":None,"conf":0.5,"reason":f"PA33: even={even}odd={odd}"}

class PA34_ConsecSame:
    name="PA34_CSAME";group="Pattern"
    def __init__(self):self.w=0.8
    def predict(self,seq,**kw):
        if len(seq)<5: return {"side":None,"conf":0.5,"reason":"PA34"}
        last,rlen=_last_run(seq)
        if rlen==2:
            brk=sub_break_prob_historical(seq,2)
            pred=_opp(last) if brk>0.52 else last
            return {"side":pred,"conf":_clamp(0.53+abs(brk-0.5)*0.4),"reason":f"PA34: run=2 brk={brk:.2f}"}
        if rlen==3:
            brk=sub_break_prob_historical(seq,3)
            pred=_opp(last) if brk>0.50 else last
            return {"side":pred,"conf":_clamp(0.56+abs(brk-0.5)*0.4),"reason":f"PA34: run=3 brk={brk:.2f}"}
        return {"side":None,"conf":0.5,"reason":f"PA34: run={rlen}"}

class PA35_PhiKy:
    name="PA35_PHI";group="Information"
    def __init__(self):self.w=0.5
    def predict(self,seq,**kw):
        # Phi coefficient giữa phiên i và i+1
        if len(seq)<20: return {"side":None,"conf":0.5,"reason":"PA35"}
        phi=sub_autocorr(seq,1)
        last,_=_last_run(seq)
        if phi>0.2: return {"side":last,"conf":_clamp(0.52+phi*0.3),"reason":f"PA35: Phi={phi:.2f}→theo"}
        if phi<-0.2: return {"side":_opp(last),"conf":_clamp(0.52+abs(phi)*0.3),"reason":f"PA35: Phi={phi:.2f}→bẻ"}
        return {"side":None,"conf":0.5,"reason":f"PA35: Phi={phi:.2f}"}

class PA36_TripleSame:
    name="PA36_TRIP";group="Pattern"
    def __init__(self):self.w=0.85
    def predict(self,seq,**kw):
        if len(seq)<8: return {"side":None,"conf":0.5,"reason":"PA36"}
        last,rlen=_last_run(seq)
        if rlen>=3:
            brk=sub_break_prob_historical(seq,rlen)
            if brk>0.52:
                return {"side":_opp(last),"conf":_clamp(0.57+brk*0.1),"reason":f"PA36: run={rlen} brk={brk:.2f}→bẻ"}
            return {"side":last,"conf":_clamp(0.53+(1-brk)*0.1),"reason":f"PA36: run={rlen} theo={1-brk:.2f}"}
        return {"side":None,"conf":0.5,"reason":f"PA36: run={rlen}<3"}

class PA37_SmartFallback:
    name="PA37_FALL";group="Fallback"
    def __init__(self):self.w=0.5
    def predict(self,seq,**kw):
        if not seq: return {"side":"TAI","conf":0.50,"reason":"PA37: Empty→TAI"}
        last,rlen=_last_run(seq)
        # Luôn có fallback thông minh
        bal=sub_balance_ratio(seq,min(20,len(seq)))
        pred="XIU" if bal>0.5 else "TAI"
        return {"side":pred,"conf":0.51,"reason":f"PA37: Fallback bal={bal:.2f}→{pred}"}

class PA38_AntiHerd:
    name="PA38_AHERD";group="Contrarian"
    def __init__(self):self.w=0.6
    def predict(self,seq,ensemble_votes=None,**kw):
        if not ensemble_votes or len(ensemble_votes)<5:
            return {"side":None,"conf":0.5,"reason":"PA38"}
        tai=ensemble_votes.count("TAI"); xiu=ensemble_votes.count("XIU")
        total=tai+xiu
        if total==0: return {"side":None,"conf":0.5,"reason":"PA38"}
        tai_r=tai/total
        # Khi quá nhiều model đồng thuận → đây có thể là bẫy
        if tai_r>0.85: return {"side":"XIU","conf":0.57,"reason":f"PA38: Herd TAI={tai_r:.2f}→contrarian XIU"}
        if tai_r<0.15: return {"side":"TAI","conf":0.57,"reason":f"PA38: Herd XIU={1-tai_r:.2f}→contrarian TAI"}
        return {"side":None,"conf":0.5,"reason":f"PA38: No herd tai={tai_r:.2f}"}

class PA39_PeriodDetect:
    name="PA39_PERIOD";group="Pattern"
    def __init__(self):self.w=0.7
    def predict(self,seq,**kw):
        if len(seq)<20: return {"side":None,"conf":0.5,"reason":"PA39"}
        # Phát hiện chu kỳ 2,3,4,5
        binary=[1 if v=="TAI" else 0 for v in seq]
        best_p=None; best_score=0
        for period in [2,3,4,5]:
            matches=sum(1 for i in range(period,len(binary)) if binary[i]==binary[i-period])
            rate=matches/(len(binary)-period)
            if rate>0.65 and rate>best_score:
                best_score=rate; best_p=period
        if best_p:
            pred="TAI" if binary[-best_p]==1 else "XIU"
            return {"side":pred,"conf":_clamp(0.54+best_score*0.2),"reason":f"PA39: Period={best_p} rate={best_score:.2f}"}
        return {"side":None,"conf":0.5,"reason":"PA39: No period"}

class PA40_FinalJudge:
    name="PA40_JUDGE";group="Final"
    def __init__(self):self.w=1.0
    def predict(self,seq,tai_total=0,xiu_total=0,**kw):
        # Model cuối cùng: tổng hợp điểm thô TAI vs XIU
        if tai_total==0 and xiu_total==0: 
            last,_=_last_run(seq) if seq else ("TAI",0)
            return {"side":_opp(last),"conf":0.51,"reason":"PA40: Fallback"}
        total=tai_total+xiu_total
        tai_r=tai_total/total
        pred="TAI" if tai_r>=0.5 else "XIU"
        gap=abs(tai_r-0.5)
        conf=_clamp(0.52+gap*0.5)
        return {"side":pred,"conf":conf,"reason":f"PA40: Judge TAI={tai_r:.2f}→{pred} gap={gap:.2f}"}


# ══════════════════════════════════════════════════════════════════════════
#  ENGINE 62 — ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════
def _bet_hier(seq, rlen, K=4.0):
    """Ước lượng p(GÃY) sau nhịp bệt dài `rlen` theo 3 tầng, mỗi tầng CO về tầng cha khi thiếu mẫu
    (thay cho việc bỏ qua khi n<5):
        tầng 0: TỔNG QUÁT mọi nhịp bệt >=2           (cha = 0.5, Laplace)
        tầng 1: nhóm độ dài  (2-3 | 4+)              (co về tầng 0)
        tầng 2: ĐÚNG độ dài rlen                      (co về tầng 1)
    Mẫu ít → p tự trôi về xác suất chung của bệt; mẫu nhiều → theo đúng rlen.
    Trả (p_brk, n_exact, n_group, n_all)."""
    n = len(seq); cap = 10
    rc = min(rlen, cap)
    grp = lambda r: 0 if r <= 3 else 1
    b_e = c_e = b_g = c_g = b_a = c_a = 0
    run = 1
    for i in range(n - 1):
        if i > 0: run = run + 1 if seq[i] == seq[i - 1] else 1
        if run < 2: continue
        r = min(run, cap); brk = seq[i + 1] != seq[i]
        if brk: b_a += 1
        else:   c_a += 1
        if grp(r) == grp(rc):
            if brk: b_g += 1
            else:   c_g += 1
        if r == rc:
            if brk: b_e += 1
            else:   c_e += 1
    n_a, n_g, n_e = b_a + c_a, b_g + c_g, b_e + c_e
    p_all = (b_a + 1.0) / (n_a + 2.0)
    p_grp = (b_g + K * p_all) / (n_g + K)
    p_ex  = (b_e + K * p_grp) / (n_e + K)
    return p_ex, n_e, n_g, n_a


class Engine84:
    """Điều phối 62 model thực tế (22 lớn + 40 phụ trợ)."""

    # Khởi tạo tất cả models
    _M_LARGE = [M01_CauNhanBiet, M02_TrendShortLong, M03_Balance12,
                M04_CauNganHan, M05_WeightBalance, M06_BeCau,
                M07_WeightEqualize, M08_CauXau, M09_CauCoban,
                M10_XacSuatBe, M11_DiceBienDong, M12_MultiPattern,
                M13_Performance, M14_XsBeCauTrend, M15_ShouldFollow,
                M16_XsSuatBe, M17_WeightBalance, M18_TrendNganHan,
                M19_PopularTrend, M20_MaxPerformance, M21_GlobalBalance,
                M22_NhaCai]

    _M_SUPPORT = [PA01_Markov1, PA02_Markov2, PA03_EMA_Cross, PA04_RSI,
                  PA05_Entropy, PA06_ZScore, PA07_RunTest, PA08_MomentumShort,
                  PA09_Reversion, PA10_Cluster, PA11_SumBand, PA12_DiceVar,
                  PA13_AntiStreak, PA14_MiniCau11, PA15_SumZone, PA16_MiniMarkov3,
                  PA17_RecentBias, PA18_StreakPenalty, PA19_SumParity, PA20_MediumBalance,
                  PA21_VolFilter, PA22_ConsecLoss, PA23_RunPat, PA24_Autocorr2,
                  PA25_Freq5, PA26_AlterPattern, PA27_SumMean, PA28_GapDetect,
                  PA29_InverseGap, PA30_HalfHalf, PA31_QuadPattern, PA32_SumDeviation,
                  PA33_EvenOdd, PA34_ConsecSame, PA35_PhiKy, PA36_TripleSame,
                  PA37_SmartFallback, PA38_AntiHerd, PA39_PeriodDetect, PA40_FinalJudge]

    def __init__(self):
        self.large  = [cls() for cls in self._M_LARGE]
        self.support = [cls() for cls in self._M_SUPPORT]
        self.perf_m = M13_Performance()
        self.weight_eq = M07_WeightEqualize()
        self.bal_m  = M17_WeightBalance()
        self.seq    = deque(maxlen=500)
        self.sums   = deque(maxlen=500)
        self.dices  = deque(maxlen=200)
        self.pred_hist = deque(maxlen=100)
        self.result_hist = deque(maxlen=100)
        self.loss_streak = 0; self.win_streak = 0
        self.total_w = 0; self.total_l = 0
        self._last_pred = None
        self._last_model_signals = {}
        self.bet_dec = deque(maxlen=20)      # lịch sử quyết định lúc bệt: 1=theo, 0=bẻ
        self._last_bet_follow = None

    def push(self, rows: list):
        for r in rows:
            if isinstance(r, dict):
                res = r.get("result", "")
                if res in ("TAI", "XIU"):
                    self.seq.append(res)
                    p = r.get("point") or r.get("total")
                    if p: self.sums.append(int(p))
                    d = r.get("dices", [])
                    if d and len(d) == 3: self.dices.append([int(x) for x in d])

    def learn(self, predicted: str, actual: str):
        if not predicted or not actual: return
        hit = predicted == actual
        self.pred_hist.append(predicted); self.result_hist.append(actual)
        if self._last_bet_follow is not None:
            self.bet_dec.append(self._last_bet_follow); self._last_bet_follow = None
        if hit:
            self.win_streak += 1; self.loss_streak = 0; self.total_w += 1
        else:
            self.loss_streak += 1; self.win_streak = 0; self.total_l += 1
        # Cập nhật hiệu suất theo tín hiệu thật của từng model.
        # Không được ghi kết quả ensemble cho mọi model, vì như vậy toàn bộ
        # trọng số sẽ giống nhau và cơ chế tự học bị sai.
        signals = self._last_model_signals or {}
        for name, side in signals.items():
            self.perf_m.update_perf(name, side == actual)

    def predict(self) -> Dict:
        seq = list(self.seq)
        sums_h = list(self.sums)
        dices_h = list(self.dices)

        if len(seq) < 5:
            return {"side": "TAI", "confidence": 52,
                    "p_tai": 0.52, "reasoning": "Khởi tạo — Chưa đủ dữ liệu",
                    "models": [], "loss_streak": self.loss_streak, "run_len": 0, "acc30": None}

        last_v, rlen = _last_run(seq)

        # --- Thu thập tín hiệu từ tất cả model lớn ---
        all_signals = []
        all_votes = []
        ctx = dict(seq=seq, sums_history=sums_h, dices_history=dices_h,
                   loss_streak=self.loss_streak)

        # M20/M21 cần context của ensemble nên phải chạy sau các model cơ sở.
        deferred = (M20_MaxPerformance, M21_GlobalBalance)
        for m in self.large:
            if isinstance(m, deferred):
                continue
            try:
                sig = m.predict(**ctx)
                if isinstance(sig, dict) and sig.get("side") in ("TAI", "XIU"):
                    sig["model"] = m.name; sig["weight"] = m.w
                    all_signals.append(sig); all_votes.append(sig["side"])
            except Exception:
                log.exception("Model lỗi: %s", m.name)

        for m in (x for x in self.large if isinstance(x, deferred)):
            try:
                extra_ctx = {**ctx, "all_signals": list(all_signals),
                             "ensemble_votes": list(all_votes),
                             "tai_total": all_votes.count("TAI"),
                             "xiu_total": all_votes.count("XIU")}
                sig = m.predict(**extra_ctx)
                if isinstance(sig, dict) and sig.get("side") in ("TAI", "XIU"):
                    sig["model"] = m.name; sig["weight"] = m.w
                    all_signals.append(sig); all_votes.append(sig["side"])
            except Exception:
                log.exception("Model lỗi: %s", m.name)

        # --- Thu thập tín hiệu từ model hỗ trợ ---
        for m in self.support:
            try:
                extra_ctx = {**ctx, "ensemble_votes": all_votes,
                             "tai_total": all_votes.count("TAI"),
                             "xiu_total": all_votes.count("XIU")}
                sig = m.predict(**extra_ctx)
                if isinstance(sig, dict) and sig.get("side") in ("TAI", "XIU"):
                    sig["model"] = m.name; sig["weight"] = m.w * 0.7
                    all_signals.append(sig); all_votes.append(sig["side"])
            except Exception:
                log.exception("Model lỗi: %s", m.name)

        # --- Lấy trọng số hiệu suất ---
        perf_ws = self.perf_m.get_weights()

        # --- Tổng hợp điểm có trọng số ---
        score_tai = score_xiu = total_w = 0.0
        reason_top = []
        for sig in all_signals:
            name = sig.get("model", "?")
            w_base = sig.get("weight", 1.0)
            w_perf = perf_ws.get(name, 0.5)
            w = w_base * (0.5 + w_perf * 0.5)
            conf = float(sig.get("conf", 0.5))
            effective = w * conf
            if sig["side"] == "TAI": score_tai += effective
            else: score_xiu += effective
            total_w += effective
            reason_top.append((sig["side"], conf, name, sig.get("reason", ""), w))

        # --- Cân bằng (M07, M21) ---
        if total_w > 0:
            tai_r = score_tai/total_w
            if tai_r > 0.80 or tai_r < 0.20:
                # Extreme → M21 override
                try:
                    m21 = M21_GlobalBalance()
                    s21 = m21.predict(seq, ensemble_votes=all_votes)
                    if s21.get("side"):
                        adj = 0.15 if tai_r > 0.80 else -0.15
                        score_tai += adj * total_w
                        score_xiu -= adj * total_w

                except Exception:
                    log.exception("M21 lỗi khi cân bằng ensemble")

        # ══════════════════════════════════════════════════════════════
        # BỆT ADJUSTER v7 — data-driven, không hardcode bẻ theo rlen
        # Nguyên tắc:
        #   1. Tính run_at[i] cho từng vị trí (đúng kỹ thuật)
        #   2. Đếm: vị trí i có run_at[i]==rlen → phiên i+1 gãy hay tiếp?
        #   3. Chỉ nudge khi n >= 5 mẫu VÀ lệch >= 8%
        #   4. KHÔNG bao giờ FORCE_BREAK hay LOSS_FLIP — những thứ đó làm
        #      engine auto bẻ bất kể dữ liệu nói gì
        # ══════════════════════════════════════════════════════════════
        bet_override_reason = ""
        if rlen >= 2 and total_w > 0 and len(seq) >= 25:
            # Tính run_at chính xác
            _run_at = [1] * len(seq)
            for _i in range(1, len(seq)):
                _run_at[_i] = _run_at[_i-1] + 1 if seq[_i] == seq[_i-1] else 1
            # Đếm mẫu: vị trí i có run_at[i]==rlen, xem i+1
            # v8: fallback phân tầng — KHÔNG còn bỏ qua khi thiếu mẫu đúng-rlen
            _p_brk, _n, _n_g, _n_all = _bet_hier(seq, rlen)

            if _n_all >= 5:
                # độ tin cậy theo lượng mẫu thực có (đúng rlen + nhóm + tổng quát)
                _rel = min(1.0, (_n + _n_g / 3.0 + _n_all / 10.0) / 6.0)
                _dev = abs(_p_brk - 0.5)
                _lv = "EXACT" if _n >= 5 else "GROUP" if _n_g >= 5 else "ALL"
                if _dev >= 0.08:
                    # Có bằng chứng thống kê → nudge nhẹ theo chiều dữ liệu
                    _adj = min(0.20, _dev * 1.0) * _rel * total_w
                    if _p_brk > 0.5:
                        # Lịch sử hay gãy → nudge bẻ
                        if _opp(last_v) == "TAI":
                            score_tai += _adj; score_xiu -= _adj * 0.3
                        else:
                            score_xiu += _adj; score_tai -= _adj * 0.3
                        bet_override_reason = (f"DATA_BRK[{_lv}] run={rlen} "
                            f"p_brk={_p_brk:.2f} n={_n}/{_n_g}/{_n_all} nudge={_adj/total_w:.2f}")
                    else:
                        # Lịch sử hay tiếp → nudge theo
                        if last_v == "TAI":
                            score_tai += _adj; score_xiu -= _adj * 0.3
                        else:
                            score_xiu += _adj; score_tai -= _adj * 0.3
                        bet_override_reason = (f"DATA_CONT[{_lv}] run={rlen} "
                            f"p_cont={1-_p_brk:.2f} n={_n}/{_n_g}/{_n_all} nudge={_adj/total_w:.2f}")
                else:
                    bet_override_reason = f"NEUTRAL[{_lv}] run={rlen} p_brk={_p_brk:.2f} n={_n}/{_n_g}/{_n_all}"
            else:
                bet_override_reason = f"WAIT run={rlen} chưa có >=5 mẫu bệt nào"

            # Nhận biết cầu đều (1-1, 2-2, 3-3): nudge nhẹ theo nhịp
            equal_len = sub_run_pattern_equal(seq, 3)
            if equal_len and rlen == equal_len and equal_len <= 3:
                theo_amt = 0.06 * total_w
                if last_v == "TAI":
                    score_tai += theo_amt; score_xiu -= theo_amt * 0.3
                else:
                    score_xiu += theo_amt; score_tai -= theo_amt * 0.3
                bet_override_reason += f" | CAU_DEU-{equal_len} theo nhịp"

        # Thua liên tiếp → chỉ shrink confidence, không đảo chiều
        if self.loss_streak >= 3 and total_w > 0:
            _shrink = min(0.15, (self.loss_streak - 2) * 0.03)
            _mid = (score_tai + score_xiu) / 2
            score_tai = score_tai * (1 - _shrink) + _mid * _shrink
            score_xiu = score_xiu * (1 - _shrink) + _mid * _shrink
            bet_override_reason += f" | SHRINK={_shrink:.2f}"

        # --- Chuẩn hóa score sau toàn bộ override ---
        # Override heuristic có thể kéo một phía xuống âm; score âm không
        # được phép đi vào p_tai/confidence.
        score_tai = max(0.0, score_tai)
        score_xiu = max(0.0, score_xiu)
        score_total = score_tai + score_xiu
        if score_total > 0:
            total_w = score_total

        # --- Quyết định ---
        if total_w <= 0:
            pred = _opp(last_v); conf_pct = 52
            reasoning = f"Fallback — đảo {last_v}"
        else:
            tai_r = score_tai/total_w
            xiu_r = score_xiu/total_w
            # Penalty khi thua liên tiếp (ngoài bệt)
            if self.loss_streak >= 3 and rlen < 2:
                pen = sub_loss_penalty(self.loss_streak)
                tai_r = 0.5 + (tai_r-0.5)*pen
                xiu_r = 0.5 + (xiu_r-0.5)*pen

            pred = "TAI" if tai_r >= xiu_r else "XIU"
            gap = abs(tai_r - xiu_r)
            conf_pct = max(60, min(72, int(50 + gap*45 + 2)))

            # ── BET MIX: lúc đang bệt, tỉ lệ THEO/BẺ bám xác suất dữ liệu nhưng kẹp 30–70%,
            #    KHÔNG bao giờ 100/0. Quyết định tự nhiên của ensemble được giữ; chỉ khi chuỗi
            #    quyết định gần đây lệch quá hạn mức (>±5%) mới đổi chiều 1 lần để giữ đúng tỉ lệ.
            self._last_bet_follow = None
            if rlen >= 3 and len(seq) >= 25:
                _pb, _ne, _ng, _na = _bet_hier(seq, rlen)
                _tgt = 0.5 if _na < 5 else min(0.70, max(0.30, 1.0 - _pb))   # P(theo) mục tiêu
                _rec = list(self.bet_dec)[-20:]
                _flip = False
                if len(_rec) >= 6:
                    _share = sum(_rec) / len(_rec)
                    _nat = (pred == last_v)
                    # lệch nhẹ (>5%) → chỉ đổi chiều ở phiên ensemble ÍT chắc (gap nhỏ); lệch nặng (>15%) → đổi bắt buộc
                    _over = (_share - _tgt) if _nat else (_tgt - _share)
                    if _over > 0.15: _flip = True
                    elif _over > 0.05 and gap < 0.30: _flip = True
                if _flip:
                    pred = _opp(pred); conf_pct = min(conf_pct, 58)
                self._last_bet_follow = 1 if pred == last_v else 0
                bet_override_reason += f" | MIX theo={_tgt:.0%}/bẻ={1-_tgt:.0%}{' ↺' if _flip else ''}"

            # Xây lý do từ top signals
            top5 = sorted(reason_top, key=lambda x: x[1]*x[4], reverse=True)[:5]
            detail_parts = "; ".join(f"[{r[2]}] {r[3]} ({r[1]:.0%})" for r in top5)
            bet_note = f" ⚡{bet_override_reason}" if bet_override_reason else ""
            reasoning = f"{pred} {conf_pct}% | TAI_score={score_tai:.2f} XIU_score={score_xiu:.2f}{bet_note} | {detail_parts}"

        p_tai = round(0.5 + (conf_pct-50)/100 if pred=="TAI" else 0.5 - (conf_pct-50)/100, 4)

        # Tổng hiệu suất
        total = self.total_w + self.total_l
        acc30 = None
        if len(self.pred_hist) >= 5:
            n = min(30, len(self.pred_hist))
            hits = sum(1 for i in range(-n,0) if self.pred_hist[i]==self.result_hist[i])
            acc30 = round(hits/n, 3)

        # Expert votes summary (22 model lớn)
        expert_votes = {m.name: 0.0 for m in self.large}
        experts = {m.name: m.w for m in self.large}
        for sig in all_signals:
            name = sig.get("model","")
            if name in expert_votes:
                expert_votes[name] = float(sig.get("conf", 0.5)) if sig["side"]=="TAI" else 1-float(sig.get("conf",0.5))

        self._last_model_signals = {
            sig["model"]: sig["side"] for sig in all_signals
            if sig.get("model") and sig.get("side") in ("TAI", "XIU")
        }
        return {
            "side": pred,
            "confidence": conf_pct,
            "p_tai": p_tai,
            "reasoning": reasoning,
            "experts": experts,
            "expert_votes": expert_votes,
            "loss_streak": self.loss_streak,
            "run_len": rlen,
            "acc30": acc30,
            "total_signals": len(all_signals),
            "models_voted_tai": all_votes.count("TAI"),
            "models_voted_xiu": all_votes.count("XIU"),
            "model_signals": dict(self._last_model_signals),
        }

    def update(self, pred_side: str, actual_side: str, model_signals=None):
        if model_signals is not None:
            self._last_model_signals = dict(model_signals)
        self.learn(pred_side, actual_side)


# ══════════════════════════════════════════════════════════════════════════
#  BRAIN ADAPTER — dùng Engine84 làm core
# ══════════════════════════════════════════════════════════════════════════
class Brain:
    """Adapter giữ nguyên hợp đồng app cũ, Engine62 làm engine dự đoán."""
    def __init__(self):
        self.engine = Engine84()
        self.history = deque(maxlen=500)
        self.points  = deque(maxlen=500)
        self._seen_ids = set()
        self._seen_order = deque(maxlen=1000)
        self._last_prediction = None
        self.loss_streak  = 0
        self.win_streak   = 0
        self.hit   = deque(maxlen=30)
        self.pred_sides = deque(maxlen=30)

    def observe(self, row):
        if not isinstance(row, dict): return False
        try:
            sid = int(row.get("id")); point = int(row.get("point"))
            result = str(row.get("result","")).upper()
        except (TypeError, ValueError): return False
        if sid in self._seen_ids or not 3 <= point <= 18 or result not in ("TAI","XIU"):
            return False
        self._seen_ids.add(sid)
        if len(self._seen_order) >= self._seen_order.maxlen:
            self._seen_ids.discard(self._seen_order.popleft())
        self._seen_order.append(sid)
        self.history.append(1 if result=="TAI" else 0)
        self.points.append(point)
        self.engine.push([{"result": result, "point": point,
                           "dices": row.get("dices", [])}])
        return True

    def predict(self):
        raw = self.engine.predict()
        side       = raw.get("side","TAI")
        confidence = int(raw.get("confidence", 52))
        p_tai      = float(raw.get("p_tai", 0.52))
        reason     = str(raw.get("reasoning",""))
        # expert votes từ 22 model lớn
        ev = raw.get("expert_votes", {})
        ex = raw.get("experts", {})
        perf = list(self.hit)
        acc  = sum(perf)/len(perf) if perf else None
        result = {
            "side": side,
            "confidence": max(50, min(89, confidence)),
            "p_tai": round(p_tai, 6),
            "reasoning": reason,
            "experts": ex,
            "expert_votes": ev,
            "forced_skip": False,
            "loss_streak": self.engine.loss_streak,
            "run_len": raw.get("run_len", 0),
            "acc30": raw.get("acc30"),
            "total_signals": raw.get("total_signals", 0),
            "evaluation": {
                "n": len(perf),
                "accuracy_30": round(acc,4) if acc is not None else None,
                "random_baseline": 0.5,
                "has_evidence": len(perf) >= 20,
                "warning": "Chưa đủ dữ liệu" if len(perf) < 20 else None,
            },
            "baseline_side": None, "baseline_p_tai": None,
            "pl": {
                "so_phien": len(self.engine.seq),
                "tong_truoc": self.points[-1] if self.points else None,
                "nhom": "L" if self.points and self.points[-1]<=9
                         else "M" if self.points and self.points[-1]<=11 else "H",
                "bệt": raw.get("run_len",0),
                "p_tai_diem": None, "p_tai_nhom": None
            },
            "nhom": {
                "loss_streak": self.engine.loss_streak,
                "hard_reset": False,
                "loss_tu_hoc": round(1-acc,4) if acc is not None else None,
                "loss_thuat_toan": None,
            },
            "hard_reset": False, "inverse_mode": False,
            "models_voted_tai": raw.get("models_voted_tai", 0),
            "models_voted_xiu": raw.get("models_voted_xiu", 0),
            "model_signals": raw.get("model_signals", {}),
        }
        self._last_prediction = result
        return result

    def learn(self, pk, y: bool):
        if not isinstance(pk, dict) or pk.get("side") not in ("TAI","XIU"): return
        actual = "TAI" if y else "XIU"
        won = pk["side"] == actual
        self.engine.update(pk["side"], actual, pk.get("model_signals"))
        self.hit.append(1 if won else 0)
        self.pred_sides.append(pk["side"])

    def _run_len(self):
        seq = list(self.engine.seq)
        if not seq: return 0
        last = seq[-1]; n = 0
        for v in reversed(seq):
            if v != last: break
            n += 1
        return n

# ── Hai hàm Table.apply() cần nhưng trước đây KHÔNG tồn tại (gây NameError) ────
def entry(row, pk, win, live=False):
    """Một dòng lịch sử: phiên đã ra + dự đoán đã đưa ra cho phiên đó."""
    du = pk.get("side") if isinstance(pk, dict) else None
    if du not in ("TAI", "XIU"): status = "skip"
    else: status = "win" if win else "lose"
    return {"phien": row["id"], "du_doan": du, "ket_qua": row["result"],
            "xuc_xac": list(row.get("dices") or []), "tong": row["point"],
            "trang_thai": status, "icon": ICON.get(status, ""), "live": bool(live),
            "conf": pk.get("confidence") if isinstance(pk, dict) else None}

REPLAY_WARMUP = 12   # số phiên tối thiểu trước khi bắt đầu chấm điểm lại

def replay(rows):
    """Dựng lại Brain từ danh sách phiên cũ: dự đoán TRƯỚC, học SAU (giống lúc chạy thật).
    Trả về (brain, danh sách entry không-live)."""
    brain = Brain(); entries = []
    for row in rows:
        if len(brain.history) >= REPLAY_WARMUP:
            try: pk = brain.predict()
            except Exception: pk = None
            if isinstance(pk, dict) and pk.get("side") in ("TAI", "XIU"):
                win = pk["side"] == row["result"]
                brain.learn(pk, row["result"] == "TAI")
                entries.append(entry(row, pk, win, False))
        brain.observe(row)
    return brain, entries

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

    def _hist_path(self):
        """Mỗi bàn một file lịch sử riêng: paw_tx_history_hu.json, _md5.json"""
        if HISTORY_FILE.endswith(".json"):
            return HISTORY_FILE[:-5] + "_%s.json" % self.code
        return HISTORY_FILE + "_" + self.code

    def load_history(self):
        # 1) Ưu tiên file riêng của bàn
        try:
            with open(self._hist_path(), "r", encoding="utf-8") as f:
                rows = json.load(f)
            if isinstance(rows, list):
                self.hist = deque([x for x in rows if isinstance(x, dict)][-HIST_MAX:], maxlen=HIST_MAX)
                return
        except (OSError, ValueError, TypeError) as e:
            log.warning("Không đọc được history của bảng %s: %s", self.code, e)
        # 2) Fallback: file gộp cũ → tự migrate sang file riêng
        try:
            with _history_lock:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f: store = json.load(f)
            rows = store.get(self.code, []) if isinstance(store, dict) else []
            if isinstance(rows, list) and rows:
                self.hist = deque([x for x in rows if isinstance(x, dict)][-HIST_MAX:], maxlen=HIST_MAX)
                self.save_history()
        except (OSError, ValueError, TypeError): self.hist = deque(maxlen=HIST_MAX)

    def save_history(self):
        try:
            tmp = self._hist_path() + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(list(self.hist)[-HIST_MAX:], f, ensure_ascii=False, separators=(",", ":"))
                f.flush(); os.fsync(f.fileno())
            os.replace(tmp, self._hist_path())
        except OSError as e: self.err = "Lỗi lưu JSON: %s" % str(e)[:100]

    def refresh(self, force=False, block=True, rebuild=False):
        if not self.lock.acquire(blocking=block): return
        try:
            if not force and self.ready and time.time() - self.fetch_ts < MIN_GAP: return
            self.fetch_ts = time.time(); t0 = time.time()
            try: rows = FETCH(self.url)
            except Exception as e:
                self.err = "%s: %s" % (type(e).__name__, str(e)[:120]); return
            if not rows: self.err = "Upstream trả danh sách rỗng"; return
            self.ms = int((time.time() - t0) * 1000); self.err = ""
            self.ok_ts = time.time(); self.n_fetch += 1
            try: self.apply(rows, rebuild)
            except Exception as e:
                log.exception("Lỗi apply bảng %s", self.code)
                self.err = "apply %s: %s" % (type(e).__name__, str(e)[:120])
        finally: self.lock.release()

    def apply(self, rows, rebuild=False):
        rows = sorted((r for r in (rows or []) if isinstance(r, dict) and "id" in r), key=lambda r: int(r["id"]))
        if not rows: self.err = "Nguồn dữ liệu không có phiên hợp lệ"; return
        newest = rows[-1]["id"]
        if rebuild or not self.ready or newest < self.last_id or rows[0]["id"] > self.last_id + 1:
            self.brain, _ = replay(rows)
            self.last = {"phien": newest, "xuc_xac": rows[-1]["dices"], "tong": rows[-1]["point"], "ket_qua": rows[-1]["result"], "du_doan": None, "trang_thai": "khong"}
            self.last_id = newest; self.ready = True; self._pend(); return

        for row in (r for r in rows if int(r["id"]) > self.last_id):
            row_id = int(row["id"])
            pd = self.pending
            expected_id = self.last_id + 1
            gap = row_id > expected_id
            if gap:
                # Không được chấm pending của phiên đã bị upstream bỏ mất.
                # Bỏ qua việc learn cho row hiện tại và bắt đầu prediction mới.
                self.err = "Upstream thiếu phiên %s-%s" % (expected_id, row_id - 1)
                self.pending = None
            is_live = bool(not gap and pd and pd["phien"] == row_id)
            pk = pd["pk"] if is_live else self.brain.predict()
            du = pk.get("side") if isinstance(pk, dict) else None
            valid_prediction = du in ("TAI", "XIU")
            win = (du == row["result"]) if valid_prediction else None
            if valid_prediction and is_live:
                self.brain.learn(pk, row["result"] == "TAI")
            if is_live:
                self.hist.append(entry(row, pk, win, True)); self.save_history()
            self.brain.observe(row)
            status = "skip" if not valid_prediction else ("win" if win else "lose")
            self.last = {"phien": row["id"], "xuc_xac": row["dices"], "tong": row["point"], "ket_qua": row["result"], "du_doan": du, "trang_thai": status}
            self.last_id = row["id"]; self.pending = None
        self._pend()

    def _pend(self):
        pk = self.brain.predict()
        self.pending = {"phien": self.last_id + 1, "du_doan": pk["side"], "do_tin_cay": pk["confidence"], "conf": pk["confidence"], "p_tai": pk["p_tai"], "reasoning": pk.get("reasoning", ""), "loss_streak": pk.get("loss_streak", 0), "run_len": pk.get("run_len", 0), "acc30": pk.get("acc30"), "pk": pk}

TABLES = {c: Table(c) for c in URLS}

def stats(items):
    w = sum(1 for h in items if h.get("trang_thai") == "win")
    l = sum(1 for h in items if h.get("trang_thai") == "lose")
    skipped = sum(1 for h in items if h.get("trang_thai") == "skip")
    total = w + l
    return {"win": w, "lose": l, "skip": skipped,
            "ty_le": round(w * 100.0 / total, 1) if total else 0.0}

def now_iso(): return datetime.now(VN).replace(microsecond=0).isoformat()

def _cau_number_sequence(brain, limit=12):
    """Chuỗi số độ dài các nhịp liên tiếp, chỉ trả số, ví dụ 1-2-1."""
    values = list(getattr(brain, "history", []))[-limit:]
    if not values:
        return "—"
    runs = []
    current = values[0]
    count = 1
    for value in values[1:]:
        if value == current:
            count += 1
        else:
            runs.append(count)
            current, count = value, 1
    runs.append(count)
    return "-".join(str(n) for n in runs)

def view_main(t):
    last = t.last; pd = t.pending
    items = list(t.hist)
    if items and last and items[-1]["phien"] == last["phien"]: items = items[:-1]
    phien_truoc = {"phien": last["phien"], "xuc_xac": last["xuc_xac"], "tong": last["tong"], "ket_qua": last["ket_qua"], "du_doan": last["du_doan"], "trang_thai": last["trang_thai"], "icon": ICON.get(last["trang_thai"], "")}
    prediction_side = pd.get("du_doan")
    phien_hien_tai = {
        "phien": pd.get("phien"),
        "du_doan": prediction_side,
        "do_tin_cay": pd.get("do_tin_cay"),
        "cau": _cau_number_sequence(t.brain),
        "ket_qua": None,
        "icon": "🔴" if prediction_side == "TAI" else "🔵" if prediction_side == "XIU" else "—",
        "cap_nhat": now_iso(),
    }
    lich_su = [{"phien": h["phien"], "du_doan": h["du_doan"], "ket_qua": h["ket_qua"], "trang_thai": h["trang_thai"], "icon": h["icon"]} for h in items[-5:][::-1]]
    res = {"ok": True, "ban": t.name, "phien_truoc": phien_truoc, "phien_hien_tai": phien_hien_tai, "lich_su": lich_su, "thong_ke": stats(list(t.hist)), "cap_nhat": now_iso()}
    if t.err: res["canh_bao"] = "Nguồn dữ liệu lỗi, đang dùng dữ liệu gần nhất"
    if pd and pd.get("pk"):
        pkd = pd["pk"]; pl = pkd.get("pl") or {}; nh = pkd.get("nhom") or {}
        res["tu_hoc"] = {"cua_so": 50, "so_phien": pl.get("so_phien"), "tong_truoc": pl.get("tong_truoc"), "nhom_tong": pl.get("nhom"), "bet": pl.get("bệt"), "p_tai_tu_diem": pl.get("p_tai_diem"), "p_tai_theo_nhom": pl.get("p_tai_nhom"), "acc30": pkd.get("acc30"), "loss_tu_hoc": nh.get("loss_tu_hoc"), "loss_thuat_toan": nh.get("loss_thuat_toan"), "trong_so_tu_hoc": 1.0, "governor": pkd.get("governor"), "evaluation": pkd.get("evaluation")}
    return res

def view_history(t, limit):
    items = list(t.hist)[::-1][:limit]
    return {"ok": True, "ban": t.name, "tong": len(items), "thong_ke": stats(list(t.hist)), "cap_nhat": now_iso(), "lich_su": [{"phien": h["phien"], "du_doan": h["du_doan"], "ket_qua": h["ket_qua"], "xuc_xac": h["xuc_xac"], "tong": h["tong"], "trang_thai": h["trang_thai"], "icon": h["icon"], "live": h["live"]} for h in items]}

# ── Background Poller ──────────────────────────────────────────────────────────
def load_toggles():
    off = {x.strip() for x in os.getenv("DISABLED_TABLES", "").split(",") if x.strip()}
    try: saved = json.load(open(STATE_FILE))
    except (OSError, ValueError, TypeError) as e:
        log.warning("Không đọc được STATE_FILE: %s", e); saved = {}
    for c, t in TABLES.items(): t.enabled = bool(saved.get(c, c not in off))

def save_toggles():
    try: json.dump({c: t.enabled for c, t in TABLES.items()}, open(STATE_FILE, "w"))
    except OSError as e: log.warning("Không lưu được STATE_FILE: %s", e)

load_toggles()
_poller = {"on": False}; _plock = threading.Lock()

def _loop():
    while True:
        for t in TABLES.values():
            if t.enabled:
                try: t.refresh()
                except Exception: log.exception("Poller lỗi tại bảng %s", t.code)
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
    if not t: return None, out({"ok": False, "loi": "not_found", "thong_bao": "Dùng hu hoặc md5"}, 404)
    if not t.enabled: return None, out({"ok": False, "loi": "table_off", "thong_bao": "Bàn %s đang tắt" % t.name}, 503)
    if not t.ready: t.refresh()
    elif time.time() - t.fetch_ts > STALE_SEC: threading.Thread(target=t.refresh, kwargs={"block": False}, daemon=True).start()
    if not t.ready: return None, out({"ok": False, "loi": "upstream_error", "thong_bao": "Chưa lấy được dữ liệu", "chi_tiet": t.err}, 503)
    return t, None

# ── API Endpoints ──────────────────────────────────────────────────────────────
def _legacy_api_gate():
    with _aprot_lock: protected = _aprot["enabled"]
    if protected: return out({"ok": False, "loi": "not_found", "thong_bao": "Không tìm thấy"}, 404)
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
    try: limit = max(1, min(HIST_MAX, int(request.args.get("limit", HIST_MAX))))
    except: limit = HIST_MAX
    return out(view_history(t, limit))

@app.get("/ping")
def ping(): return out({"ok": True, "t": now_iso()})

@app.get("/")
def index(): return out({"ok": True, "api": "PAW TX v6 + Engine62", "endpoints": ["/tx/hu", "/tx/md5", "/history/tx/hu", "/history/tx/md5", "/admin", "/ping"]})

def _protected_gate(prefix_code: str):
    with _aprot_lock: prot_on = _aprot["enabled"]
    if not prot_on: return out({"ok": False, "loi": "not_found", "thong_bao": "Không tìm thấy"}, 404)
    ip = request.remote_addr or "0.0.0.0"
    if not _check_code_ratelimit(ip): return out({"ok": False, "loi": "rate_limited", "thong_bao": "Quá nhiều lần thử sai"}, 429)
    if not _check_api_code(prefix_code):
        _record_code_fail(ip)
        return out({"ok": False, "loi": "not_found", "thong_bao": "Không tìm thấy"}, 404)
    return None

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
    try: limit = max(1, min(HIST_MAX, int(request.args.get("limit", HIST_MAX))))
    except: limit = HIST_MAX
    return out(view_history(t, limit))

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN UI
# ══════════════════════════════════════════════════════════════════════════════
_fails: dict = {}

def authed(): return bool(session.get("adm")) and session.get("adm_until", 0) > time.time()

def guard():
    if not authed(): return out({"ok": False, "loi": "unauthorized"}, 401)
    if request.method == "POST" and not hmac.compare_digest(request.headers.get("X-CSRF-Token", ""), session.get("csrf", "x")): return out({"ok": False, "loi": "csrf"}, 403)

def table_dump(t):
    pd = t.pending; hist = list(t.hist); live = [h for h in hist if h.get("live")]; l30 = hist[-30:]
    pk = pd["pk"] if pd else {}
    ex = [{"name": k, "p": round(pk.get("expert_votes", {}).get(k, 0.5), 4), "w": round(pk.get("experts", {}).get(k, 0.33), 4), "group": "Thực chiến"} for k in pk.get("expert_votes", {}).keys()] if pd else []
    return {"code": t.code, "name": t.name, "enabled": t.enabled, "ready": t.ready, "err": t.err, "ms": t.ms, "n_fetch": t.n_fetch, "age": round(time.time() - t.ok_ts) if t.ok_ts else None, "last": t.last, "pending": {"phien": pd["phien"], "du_doan": pd["du_doan"], "conf": pd["do_tin_cay"], "p_tai": pd["p_tai"], "evaluation": pk.get("evaluation"), "baseline_side": pk.get("baseline_side"), "temp": pk.get("temp", 1.0), "reasoning": pk.get("reasoning", ""), "loss_streak": pk.get("loss_streak", 0), "run_len": pk.get("run_len", 0), "cau": _cau_number_sequence(t.brain), "acc30": pk.get("acc30"), "hard_reset": pk.get("nhom", {}).get("hard_reset", False)} if pd else None, "experts": ex, "st_all": stats(hist), "st_live": stats(live), "st_30": stats(l30), "hist": hist[::-1]}

@app.get("/admin/data")
def admin_data():
    g = guard(); return g or out({"ok": True, "tables": [table_dump(t) for t in TABLES.values()]})

@app.post("/admin/act/<code>/<act>")
def admin_act(code, act):
    g = guard()
    if g: return g
    t = TABLES.get(code)
    if not t or act not in ("on", "off", "refresh", "relearn"): return out({"ok": False, "loi": "bad_request"}, 400)
    if act in ("on", "off"): t.enabled = act == "on"; save_toggles()
    elif act == "refresh": t.refresh(force=True)
    else: t.refresh(force=True, rebuild=True)
    return out({"ok": True, "enabled": t.enabled, "err": t.err})

@app.post("/admin/aprot/gen")
def aprot_gen():
    g = guard()
    if g: return g
    code = secrets.token_urlsafe(9)[:6].upper()
    import re as _re
    code = _re.sub(r'[^A-Z0-9]', lambda m: secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789'), code)
    with _aprot_lock: _aprot["code"] = code
    _save_cfg()
    return out({"ok": True, "code": code})

@app.post("/admin/aprot/set")
def aprot_set():
    g = guard()
    if g: return g
    action = request.form.get("action", "")
    if not action:
        try:
            body = request.get_json(silent=True) or {}; action = body.get("action", "") if isinstance(body, dict) else ""
        except Exception: action = ""
    if action not in ("enable", "disable"): return out({"ok": False, "loi": "bad_request"}, 400)
    with _aprot_lock:
        cur_code = _aprot["code"]
        if action == "enable" and not cur_code: return out({"ok": False, "loi": "code_required"}, 400)
        _aprot["enabled"] = (action == "enable")
    _save_cfg()
    return out({"ok": True, "enabled": _aprot["enabled"], "code_set": bool(cur_code)})

@app.post("/admin/aprot/revoke")
def aprot_revoke():
    g = guard()
    if g: return g
    with _aprot_lock: _aprot["code"] = ""; _aprot["enabled"] = False
    _save_cfg()
    return out({"ok": True, "revoked": True})

@app.get("/admin/aprot/status")
def aprot_status():
    g = guard()
    if g: return g
    with _aprot_lock: snap = dict(_aprot)
    return out({"ok": True, "enabled": snap["enabled"], "has_code": bool(snap["code"])})

LOGIN = """<!doctype html><html lang=vi><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><title>PAW TX · Login</title><style>*{box-sizing:border-box;margin:0;padding:0}body{min-height:100vh;display:grid;place-items:center;padding:20px;background:radial-gradient(ellipse at 15% 0%,rgba(37,99,235,.24),transparent 40%),#080d1b;color:#edf3ff;font:13px/1.6 Inter,system-ui,sans-serif}.login{width:min(420px,100%);padding:34px;border:1px solid rgba(148,163,184,.18);border-radius:22px;background:linear-gradient(145deg,rgba(20,32,55,.97),rgba(10,17,32,.98));box-shadow:0 28px 90px rgba(0,0,0,.45);position:relative;overflow:hidden}.mark{width:58px;height:58px;margin:0 auto 20px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(145deg,#2563eb,#7c3aed);box-shadow:0 12px 32px rgba(79,70,229,.35)}.mark svg{width:34px;height:34px}.eyebrow{text-align:center;color:#67e8f9;font-size:9px;font-weight:800;letter-spacing:.2em;margin-bottom:8px}h1{text-align:center;font-size:25px;letter-spacing:-.05em;font-weight:900}.sub{text-align:center;color:#91a1bd;font-size:11px;margin:7px 0 26px}label{display:block;color:#a8b6cc;font-size:9px;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin:0 0 7px}input{width:100%;height:46px;margin:0 0 17px;padding:0 13px;border:1px solid rgba(148,163,184,.2);border-radius:11px;background:#0b1426;color:#edf3ff;font:13px Inter;outline:none;transition:.18s}input:focus{border-color:#60a5fa;box-shadow:0 0 0 3px rgba(59,130,246,.15)}button{width:100%;height:46px;border:0;border-radius:11px;background:linear-gradient(105deg,#2563eb,#5b4be8);color:#fff;font:800 12px Inter;cursor:pointer}.err{margin:0 0 16px;padding:10px 12px;border-radius:10px;border:1px solid rgba(251,113,133,.25);background:rgba(251,113,133,.1);color:#fda4af;font-size:11px}.foot{margin-top:20px;text-align:center;color:#64748b;font-size:10px}
/* PAW ADMIN WHITE CREATIVE OVERRIDES */
html,body{background:#fff!important;color:#142033}
:root{--bg:#fff;--surf:#fff;--surf2:#f8fbff;--surf3:#f1f6fc;
 --bd:#e4eaf2;--bd2:#d3deeb;--txt:#142033;--txt2:#34445b;
 --txt3:#64758d;--txt4:#91a0b4;--shadow:0 2px 12px rgba(24,49,82,.055);
 --shadow-md:0 12px 28px rgba(24,49,82,.09);--shadow-lg:0 18px 44px rgba(24,49,82,.12)}
.top{background:rgba(255,255,255,.97);border-bottom:1px solid #e7edf5}
.nav-tabs{background:#fff;border-bottom:1px solid #e7edf5}
.wrap{max-width:1480px;padding-top:30px}
.heading{display:flex;align-items:end;justify-content:space-between;gap:18px;margin:8px 0 22px}
.card,.stat-card{background:#fff;border:1px solid #e5ebf3;box-shadow:0 4px 18px rgba(27,53,87,.055)}
.card{border-radius:18px;padding:20px}
.card:hover{border-color:#cbdcf2;box-shadow:0 12px 30px rgba(27,53,87,.09)}
.stat-card{border-radius:16px;padding:18px 20px}
.stat-card::before{height:4px}
.hero.prediction-json{background:linear-gradient(145deg,#fff 0%,#fbfdff 100%);border:1px solid #e2eaf5;border-radius:16px;padding:16px;box-shadow:inset 0 1px 0 #fff}
.prediction-topline{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.prediction-json .hero-label{color:#7890ad;margin:0 0 3px;letter-spacing:.15em}
.prediction-caption{font-size:12px;font-weight:700;color:#34445b}
.prediction-live{display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:99px;background:#effaf4;color:#168253;font-size:10px;font-weight:900;letter-spacing:.1em}
.prediction-live i{width:7px;height:7px;border-radius:50%;background:#20b875;box-shadow:0 0 0 3px #d8f5e6}
.json-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.json-cell{min-height:72px;padding:11px 12px;border:1px solid #e7edf5;border-radius:12px;background:#fff;display:flex;flex-direction:column;justify-content:space-between;gap:7px}
.json-cell>span{font:700 9px 'JetBrains Mono',monospace;letter-spacing:.15em;color:#8a9bb0}
.json-cell>b{font-size:17px;color:#17263b;line-height:1.2}
.json-cell .json-side{font-size:25px;font-weight:950;letter-spacing:-.04em}
.json-side.TAI{color:#e34f68}.json-side.XIU{color:#0898b5}
.json-cell .json-icon{font-size:22px}
.prediction-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.prediction-meta span{padding:7px 9px;border-radius:9px;background:#f4f8fd;color:#77879d;font-size:9px;font-weight:800;letter-spacing:.04em}
.prediction-meta b{color:#263b57;margin-left:4px;font:800 11px 'JetBrains Mono',monospace}
.prediction-reason{margin-top:10px;padding:10px 12px;border-radius:10px;background:#f8faff;border:1px solid #e8eef7;color:#61728a;font-size:11px;line-height:1.55}
.side{font-size:clamp(40px,6vw,68px)}
.tablewrap{border:1px solid #e7edf5;border-radius:13px}
table{background:#fff}
th{background:#f7faff;color:#8293a9}
tr:hover td{background:#f8fbff}
.foot{color:#a0aec0}
@media(max-width:620px){.wrap{padding:16px 12px 48px}.card{padding:14px}.json-grid{gap:7px}.json-cell{min-height:66px;padding:9px}.json-cell>b{font-size:15px}.prediction-meta{gap:5px}}

</style></head><body><main class=login><div class=mark><svg viewBox="0 0 40 40" fill=none><path d="M20 3S32 16 32 24a12 12 0 1 1-24 0C8 16 20 3 20 3Z" fill=white/></svg></div><div class=eyebrow>SECURE ADMIN ACCESS</div><h1>PAW TX Admin</h1><div class=sub>Đăng nhập để truy cập Control Center</div>__ERR__<form method=post action=/admin/login><label>Tài khoản</label><input name=username value=admin required><label>Mật khẩu</label><input type=password name=password required><button type=submit>ĐĂNG NHẬP HỆ THỐNG →</button></form><div class=foot>PAW TX CONTROL CENTER</div></main></body></html>"""

PAGE = r"""<!doctype html>
<html lang="vi"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#f4f7fb">
<title>PAW TX · Neural Control Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════
   PAW TX ADMIN — NỀN TRẮNG · ENGINE 62 MODEL
   ═══════════════════════════════════════════════════ */
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f4f7fb;--surf:#fff;--surf2:#f8fbff;--surf3:#eef3fa;
  --bd:#dde6f0;--bd2:#c5d4e8;
  --txt:#0d1c2e;--txt2:#2a3c54;--txt3:#5570a0;--txt4:#8ba2c0;
  --blue:#1a6bf0;--blue-s:#e8f0fe;--blue2:#1456d0;
  --cyan:#0881ae;--cyan-s:#e0f4fa;
  --green:#0a7a50;--green-s:#e4f8f0;--green-b:#1ab870;
  --red:#c01c38;--red-s:#fef0f2;--red-b:#e83348;
  --amber:#a05510;--amber-s:#fef9ea;
  --purple:#6030c0;--purple-s:#f4f0fb;
  --shadow:0 2px 8px rgba(10,30,70,.07);
  --shadow-md:0 6px 20px rgba(10,30,70,.10);
  --shadow-lg:0 14px 44px rgba(10,30,70,.13);
  --radius:16px;
}
html{background:var(--bg);-webkit-font-smoothing:antialiased}
body{background:var(--bg);color:var(--txt);font-family:'Inter',system-ui,sans-serif;font-size:14px;line-height:1.6;min-height:100vh}
button{font:inherit;cursor:pointer;border:none}
a{color:inherit;text-decoration:none}
.mono{font-family:'JetBrains Mono',monospace;font-variant-numeric:tabular-nums}
.hide{display:none!important}
.muted{color:var(--txt4)}
.empty{text-align:center;color:var(--txt4);padding:28px!important;font-size:12px}

/* ── TOPBAR ── */
.top{
  position:sticky;top:0;z-index:50;height:60px;
  display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:0 max(16px,calc((100vw - 1500px)/2));
  background:rgba(255,255,255,.97);backdrop-filter:blur(16px);
  border-bottom:1.5px solid var(--bd);box-shadow:var(--shadow);
}
.brand{display:flex;align-items:center;gap:11px}
.logo{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;
  background:linear-gradient(135deg,#1a6bf0,#7030e0);box-shadow:0 4px 14px rgba(79,70,229,.25)}
.logo svg{width:22px;height:22px}
.brand-name{font-size:15px;font-weight:900;letter-spacing:-.03em;color:var(--txt)}
.brand-name small{display:block;font-size:9px;font-family:'JetBrains Mono',monospace;
  color:var(--txt3);letter-spacing:.18em;font-weight:600;margin-top:-2px}
.right{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.status-pill{display:flex;align-items:center;gap:6px;padding:5px 11px;
  border:1.5px solid var(--bd);border-radius:99px;font-size:11px;font-weight:700;
  color:var(--txt3);background:var(--surf2);letter-spacing:.04em}
.ldot{width:7px;height:7px;border-radius:50%;background:var(--green-b);
  box-shadow:0 0 0 2px rgba(26,184,112,.2);animation:pulse 2.4s infinite}
.ldot.bad{background:var(--red-b);box-shadow:0 0 0 2px rgba(232,51,72,.2)}
#countdown{font-family:'JetBrains Mono',monospace;font-weight:800;color:var(--blue)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}

/* ── BTN ── */
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:5px;
  padding:8px 15px;border-radius:10px;font-size:12px;font-weight:800;
  border:1.5px solid var(--bd2);background:var(--surf);color:var(--txt2);
  transition:all .15s;white-space:nowrap;box-shadow:var(--shadow);letter-spacing:.02em;
}
.btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-s);transform:translateY(-1px)}
.btn:active{transform:scale(.97)}
.btn.primary{background:var(--blue);color:#fff;border-color:var(--blue2);box-shadow:0 2px 8px rgba(26,107,240,.25)}
.btn.primary:hover{background:var(--blue2);border-color:var(--blue2)}
.btn.danger{color:var(--red);border-color:#fca5a5;background:var(--red-s)}
.btn-sm{padding:6px 11px;font-size:11px;border-radius:8px}

/* ── NAV TABS ── */
.nav-tabs{
  display:flex;gap:2px;
  padding:0 max(16px,calc((100vw - 1500px)/2));
  border-bottom:1.5px solid var(--bd);background:var(--surf);overflow-x:auto;
  scrollbar-width:none;
}
.nav-tabs::-webkit-scrollbar{display:none}
.tab{
  padding:12px 16px;font-size:12px;font-weight:800;color:var(--txt3);
  border:none;background:none;border-bottom:2.5px solid transparent;
  cursor:pointer;white-space:nowrap;transition:color .15s,border-color .15s;
  letter-spacing:.04em;text-transform:uppercase;
}
.tab.active{color:var(--blue);border-bottom-color:var(--blue)}
.tab:hover:not(.active){color:var(--txt2)}

/* ── WRAP ── */
.wrap{max-width:1500px;margin:0 auto;padding:22px 16px 72px}
.pane{display:none}.pane.active{display:block}

/* ── GRID ── */
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(500px,1fr));gap:18px}
.grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
@media(max-width:900px){.grid{grid-template-columns:1fr}.grid4{grid-template-columns:repeat(2,1fr)}}
@media(max-width:500px){.grid4{grid-template-columns:1fr}}

/* ── CARD ── */
.card{
  background:var(--surf);border:1.5px solid var(--bd);border-radius:var(--radius);
  padding:20px;box-shadow:var(--shadow);min-width:0;
  animation:fadeUp .3s ease both;
}
.card:hover{border-color:var(--bd2);box-shadow:var(--shadow-md)}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.cardhead{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:16px}
.cardhead b{font-size:15px;font-weight:900;color:var(--txt);letter-spacing:-.02em}

/* ── STAT CARDS ── */
.stat-card{
  background:var(--surf);border:1.5px solid var(--bd);border-radius:14px;
  padding:16px 18px;position:relative;overflow:hidden;
  box-shadow:var(--shadow);animation:fadeUp .3s ease both;
  transition:box-shadow .15s,transform .15s;
}
.stat-card:hover{box-shadow:var(--shadow-md);transform:translateY(-1px)}
.stat-card::before{
  content:"";position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--sa,var(--blue));border-radius:14px 14px 0 0;
}
.stat-label{font-size:10px;font-weight:800;color:var(--txt3);letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px}
.stat-val{font-size:clamp(22px,3vw,30px);font-weight:900;color:var(--txt);letter-spacing:-.04em;line-height:1.1;font-family:'JetBrains Mono',monospace}
.stat-note{font-size:11px;color:var(--txt4);margin-top:4px}

/* ── PREDICTION HERO ── */
.pred-hero{
  background:linear-gradient(130deg,#0f1f38 0%,#162040 55%,#231550 100%);
  border:1.5px solid #2c4278;border-radius:var(--radius);padding:20px 22px;
  position:relative;overflow:hidden;margin-bottom:16px;
}
.pred-hero::after{
  content:"";position:absolute;top:-30px;right:-30px;
  width:120px;height:120px;border-radius:50%;
  background:radial-gradient(circle,rgba(99,70,255,.18),transparent 70%);
}
.pred-hero-label{font-size:9px;font-weight:900;letter-spacing:.22em;color:#7090c8;text-transform:uppercase;margin-bottom:8px}
/* BIG side */
.big-side{font-size:clamp(52px,8vw,88px);font-weight:900;letter-spacing:-.06em;line-height:1;margin:4px 0 10px;display:block}
.big-side.TAI{color:#ff6a85;text-shadow:0 0 32px rgba(255,80,100,.55)}
.big-side.XIU{color:#30d8f8;text-shadow:0 0 32px rgba(48,216,248,.55)}
/* BIG % */
.big-pct{font-size:clamp(32px,5vw,52px);font-weight:900;color:#fbbf24;
  font-family:'JetBrains Mono',monospace;letter-spacing:-.05em;display:inline-block}
.pct-label{font-size:12px;color:#90a8c8;font-weight:600;margin-left:8px;vertical-align:middle}
/* P_TAI */
.ptai-row{font-size:12px;color:#8099c0;margin-bottom:12px;font-family:'JetBrains Mono',monospace}
/* Meter */
.meter{height:8px;border-radius:99px;background:rgba(255,255,255,.1);overflow:hidden;margin:0 0 14px}
.meter i{display:block;height:100%;border-radius:99px;
  background:linear-gradient(90deg,#3060d8,#06b8d8);
  box-shadow:0 0 10px rgba(48,210,248,.4);transition:width .4s}
/* Reason */
.reason-box{
  padding:10px 13px;border:1px solid #2a4068;border-left:3px solid #7060c8;
  border-radius:9px;background:rgba(8,18,38,.55);color:#98b8d8;font-size:11px;line-height:1.6;
}
.reason-box strong{display:block;font-family:'JetBrains Mono',monospace;font-size:8px;
  letter-spacing:.16em;color:#8880d8;margin-bottom:5px;text-transform:uppercase}
/* Chips */
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
.chip{flex:1;min-width:80px;padding:10px 12px;background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.09);border-radius:10px}
.chip b{display:block;font-family:'JetBrains Mono',monospace;font-size:18px;
  font-weight:900;color:#d8e8ff;line-height:1;margin-bottom:3px}
.chip small{font-size:9px;color:#6080a8;text-transform:uppercase;letter-spacing:.08em;font-weight:700}
/* Model votes */
.votes-row{display:flex;gap:6px;margin-top:12px;align-items:center;flex-wrap:wrap}
.vote-pill{display:inline-flex;align-items:center;gap:4px;padding:4px 9px;border-radius:7px;font-size:10px;font-weight:800}
.vote-pill.tai{background:rgba(255,100,130,.12);color:#ff7a9a;border:1px solid rgba(255,100,130,.2)}
.vote-pill.xiu{background:rgba(40,210,250,.10);color:#30d0f0;border:1px solid rgba(40,210,250,.18)}

/* ── PREV SESSION ── */
.prev-box{
  display:flex;align-items:center;justify-content:space-between;gap:10px;
  padding:12px 16px;border:1.5px solid var(--bd);border-radius:12px;
  background:var(--surf2);margin-bottom:14px;
}
.prev-side{font-size:clamp(24px,4vw,38px);font-weight:900;letter-spacing:-.04em}
.prev-side.TAI{color:var(--red-b)}.prev-side.XIU{color:var(--cyan)}
.prev-label{font-size:9px;font-weight:800;color:var(--txt3);letter-spacing:.12em;text-transform:uppercase}
.prev-info{flex:1;text-align:center}
.icon-big{font-size:28px;line-height:1}

/* ── EXPERTS ── */
.expert-row{display:flex;align-items:center;gap:8px;margin:3px 0}
.expert-name{font-size:10px;font-weight:700;color:var(--txt2);min-width:130px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.track{flex:1;height:5px;background:var(--bd);border-radius:4px;overflow:hidden}
.track i{display:block;height:100%;border-radius:4px;background:var(--blue);transition:width .3s}
.expert-meta{font-size:9px;color:var(--txt4);font-family:'JetBrains Mono',monospace;min-width:80px;text-align:right}
.group-tag{display:inline-block;font-size:8px;font-weight:800;letter-spacing:.08em;color:var(--txt4);text-transform:uppercase;margin-left:130px;padding:1px 0}

/* ── TABLE ── */
.tablewrap{border:1.5px solid var(--bd);border-radius:12px;overflow:hidden}
table{width:100%;border-collapse:collapse;background:var(--surf)}
th{background:var(--surf2);padding:9px 12px;text-align:left;font-size:10px;font-weight:900;
  color:var(--txt3);letter-spacing:.1em;text-transform:uppercase;border-bottom:1.5px solid var(--bd)}
td{padding:9px 12px;border-bottom:1px solid var(--bd);font-size:12px;vertical-align:middle}
tr:last-child td{border-bottom:none}
tr.win{background:linear-gradient(90deg,rgba(26,184,112,.04),transparent)}
tr.lose{background:linear-gradient(90deg,rgba(232,51,72,.04),transparent)}
tr:hover td{background:var(--surf2)}

/* ── PILL ── */
.pill{display:inline-block;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:900;letter-spacing:.06em}
.pill.win{background:var(--green-s);color:var(--green)}
.pill.lose{background:var(--red-s);color:var(--red)}
.pill.cho{background:var(--amber-s);color:var(--amber)}
.live-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 8px;border-radius:6px;
  background:#e6faf3;color:#0a7a50;font-size:10px;font-weight:800}
.live-dot{width:5px;height:5px;border-radius:50%;background:#1ab870;animation:pulse 2s infinite}
/* Side pills */
.side-t{color:#c01c38;font-weight:900;font-size:12px}
.side-x{color:#0881ae;font-weight:900;font-size:12px}

/* ── PROTECTION TAB ── */
.prot-status{display:inline-block;padding:3px 10px;border-radius:7px;font-size:11px;font-weight:900;letter-spacing:.06em}
.prot-status.on{background:var(--green-s);color:var(--green)}
.prot-status.off{background:var(--red-s);color:var(--red)}
.code-box{background:#1a1f2e;border-radius:10px;padding:12px 16px;font-family:'JetBrains Mono',monospace;
  font-size:18px;font-weight:700;color:#e8d060;letter-spacing:.12em;text-align:center}
.url-preview{padding:10px 12px;background:var(--surf2);border:1.5px solid var(--bd);border-radius:9px;
  font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--txt3);word-break:break-all;line-height:1.5}

/* ── TOAST ── */
#toast{
  position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);
  padding:11px 20px;border-radius:12px;font-size:13px;font-weight:700;
  background:var(--txt);color:#fff;box-shadow:var(--shadow-lg);
  transition:transform .28s cubic-bezier(.34,1.56,.64,1),opacity .2s;
  opacity:0;pointer-events:none;z-index:999;white-space:nowrap;
}
#toast.show{transform:translateX(-50%) translateY(0);opacity:1}
#toast.ok{background:#0a7a50}
#toast.err{background:var(--red)}

@media(max-width:620px){
  .wrap{padding:14px 10px 60px}
  .card{padding:14px}
  .pred-hero{padding:14px 16px}
  .topbar .right .status-pill{display:none}
}
</style></head>

<body>
<!-- ── TOPBAR ── -->
<nav class="top">
  <div class="brand">
    <div class="logo">
      <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round">
        <path d="M12 2L4 7v5c0 5 4 9 8 10 4-1 8-5 8-10V7z"/>
        <path d="M9 12l2 2 4-4"/>
      </svg>
    </div>
    <div>
      <div class="brand-name">PAW NEURAL<small>TX // AI CONTROL CENTER</small></div>
    </div>
  </div>
  <div class="right">
    <div class="status-pill"><div class="ldot" id="apiDot"></div><span id="apiStatus">Đang tải…</span></div>
    <div class="status-pill">SYNC <span id="countdown" class="mono">4</span> s</div>
    <button class="btn btn-sm" onclick="load()">↻ Làm mới</button>
    <a href="/admin/logout" class="btn btn-sm danger">Thoát →</a>
  </div>
</nav>

<!-- ── TABS ── -->
<div class="nav-tabs" role="tablist">
  <button class="tab active" onclick="showTab('tab-overview',this)">Tổng quan</button>
  <button class="tab" onclick="showTab('tab-history',this)">Lịch sử dự đoán</button>
  <button class="tab" onclick="showTab('tab-models',this)">62 Models</button>
  <button class="tab" onclick="showTab('tab-prot',this)">Bảo vệ API</button>
</div>

<main class="wrap">
  <div id="toast"></div>

  <!-- ── TAB OVERVIEW ── -->
  <div class="pane active" id="tab-overview">
    <!-- Stat row -->
    <div class="grid4" id="statRow" style="margin-bottom:20px"></div>
    <!-- Boards -->
    <div class="grid" id="boards"></div>
  </div>

  <!-- ── TAB HISTORY ── -->
  <div class="pane" id="tab-history">
    <div style="margin-bottom:14px">
      <span style="font-size:11px;font-weight:800;color:var(--txt3);letter-spacing:.12em;text-transform:uppercase">WALK-FORWARD LEARNING</span>
      <h2 style="font-size:clamp(20px,4vw,28px);font-weight:900;color:var(--txt);letter-spacing:-.03em;margin:4px 0 0">Lịch sử dự đoán live</h2>
    </div>
    <div id="historyBoards"></div>
  </div>

  <!-- ── TAB 62 MODELS ── -->
  <div class="pane" id="tab-models">
    <div style="margin-bottom:16px">
      <span style="font-size:11px;font-weight:800;color:var(--txt3);letter-spacing:.12em;text-transform:uppercase">ENGINE OVERVIEW</span>
      <h2 style="font-size:clamp(18px,4vw,26px);font-weight:900;color:var(--txt);letter-spacing:-.03em;margin:4px 0 6px">62 Model Engine</h2>
      <p style="font-size:12px;color:var(--txt3);max-width:700px;line-height:1.6">22 model lớn + 40 model phụ trợ. Trọng số được cập nhật theo tín hiệu riêng của từng model; lỗi model sẽ được ghi nhận thay vì bỏ qua im lặng. Không dùng AI thật — 100% code thuật toán.</p>
    </div>
    <div id="modelsGrid"></div>
  </div>

  <!-- ── TAB BẢO VỆ API ── -->
  <div class="pane" id="tab-prot">
    <div class="card" style="max-width:580px">
      <div class="cardhead">
        <b>🔐 Bảo vệ API bằng mã tiền tố</b>
        <span class="prot-status off" id="protState">TẮT</span>
      </div>
      <p style="font-size:12px;color:var(--txt3);margin-bottom:16px;line-height:1.6">
        Khi bật, URL API đổi thành <code style="background:var(--surf2);padding:1px 5px;border-radius:4px;font-size:11px">/<b>MÃ</b>/tx/hu</code> và <code style="background:var(--surf2);padding:1px 5px;border-radius:4px;font-size:11px">/<b>MÃ</b>/tx/md5</code>. URL cũ trả 404.
      </p>
      <div style="margin-bottom:14px;padding:12px 14px;background:var(--surf2);border:1.5px solid var(--bd);border-radius:11px">
        <div style="font-size:9px;font-weight:900;color:var(--txt3);letter-spacing:.14em;margin-bottom:8px">MÃ TRUY CẬP API</div>
        <div class="code-box" id="codeDisplay">••••••</div>
        <div class="url-preview" id="urlPreview" style="margin-top:10px">Tạo mã để xem URL bảo vệ</div>
      </div>
      <div style="font-size:11px;color:var(--txt3);margin-bottom:14px" id="protInfo">Đang tải trạng thái…</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button class="btn primary" onclick="genCode()">🔑 Tạo mã mới</button>
        <button class="btn" onclick="copyCode()">📋 Copy mã</button>
        <button class="btn primary" onclick="setProt('enable')">✅ Bật bảo vệ</button>
        <button class="btn" onclick="setProt('disable')">⏸ Tắt</button>
        <button class="btn danger" onclick="revokeCode()">🗑 Thu hồi</button>
      </div>
    </div>
  </div>
</main>

<script>
const CSRF='__CSRF__';
let DATA=[],timer=4,prot={enabled:false,has_code:false,code:''};
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

/* ── TOAST ── */
function toast(msg,ok=true){
  const el=$('toast');el.textContent=msg;
  el.className='show '+(ok?'ok':'err');
  clearTimeout(el._t);el._t=setTimeout(()=>el.className='',3000);
}

/* ── TAB ── */
function showTab(id,btn){
  document.querySelectorAll('.pane').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  $(id).classList.add('active');btn.classList.add('active');
  if(id==='tab-models')drawModels();
}

/* ── SIDE PILL ── */
function side(s){
  if(!s||s==='—') return '<span class="muted">—</span>';
  const cls=s==='TAI'||s==='TÀI'?'side-t':'side-x';
  const lbl=s==='TAI'?'TÀI':s==='XIU'?'XỈU':esc(s);
  return `<span class="${cls}">${lbl}</span>`;
}

/* ── BOARD CARD ── */
function board(t){
  const pd=t.pending; const ex=t.experts||[];
  const st=t.st_live||{}; const s30=t.st_30||{};
  const acc30=s30.win+s30.lose>0?Math.round(s30.win*100/(s30.win+s30.lose)):0;
  const accAll=t.st_all?.win+t.st_all?.lose>0?Math.round(t.st_all.win*100/(t.st_all.win+t.st_all.lose)):0;
  const color=t.code==='hu'?'#9030e0':'#1a6bf0';

  return `<article class="card" style="--accent:${color}">
    <div class="cardhead">
      <b style="color:var(--txt)">Bàn ${esc(t.name)}</b>
      <div style="display:flex;gap:6px;align-items:center">
        ${t.enabled
          ?`<button class="btn btn-sm danger" onclick="act('${t.code}','off')">⏸ Tắt</button>
            <button class="btn btn-sm" onclick="act('${t.code}','refresh')">↻</button>
            <button class="btn btn-sm" onclick="act('${t.code}','relearn')">🔄 Học lại</button>`
          :`<button class="btn btn-sm primary" onclick="act('${t.code}','on')">▶ Bật</button>`}
      </div>
    </div>

    ${pd?`<!-- PREDICTION HERO -->
    <div class="pred-hero">
      <div class="pred-hero-label">Dự đoán phiên tiếp theo · #${pd.phien}</div>
      <div>
        <span class="big-side ${pd.du_doan}">${pd.du_doan==='TAI'?'TÀI':'XỈU'}</span>
      </div>
      <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:8px">
        <span class="big-pct">${pd.conf??'—'}%</span>
        <span class="pct-label">Độ tin cậy</span>
      </div>
      <div class="meter"><i style="width:${Math.min(100,pd.conf??50)}%"></i></div>
      ${pd.p_tai!=null?`<div class="ptai-row">P(TÀI) = ${(pd.p_tai*100).toFixed(1)}%  ·  P(XỈU) = ${((1-pd.p_tai)*100).toFixed(1)}%</div>`:''}
      ${pd.reasoning?`<div class="reason-box"><strong>Lý do phân tích</strong>${esc(pd.reasoning)}</div>`:''}
      <div class="votes-row">
        <span style="font-size:9px;color:#6080a8;font-weight:800;letter-spacing:.1em">VOTES:</span>
        ${pd.models_voted_tai!=null?`<span class="vote-pill tai">TÀI ${pd.models_voted_tai}</span>`:''}
        ${pd.models_voted_xiu!=null?`<span class="vote-pill xiu">XỈU ${pd.models_voted_xiu}</span>`:''}
        ${pd.total_signals!=null?`<span style="font-size:9px;color:#6080a8">/ ${pd.total_signals} signals</span>`:''}
      </div>
      <div class="chips">
        <div class="chip"><b>${pd.loss_streak??0}</b><small>Loss Streak</small></div>
        <div class="chip"><b>${pd.run_len??0}</b><small>Run len</small></div>
        <div class="chip"><b>${acc30}%</b><small>Acc 30</small></div>
        <div class="chip"><b>${accAll}%</b><small>Acc All</small></div>
      </div>
    </div>`:'<div style="padding:20px;text-align:center;color:var(--txt4)">Đang tải dự đoán…</div>'}

    ${t.last?`<!-- PREV SESSION -->
    <div class="prev-box">
      <div>
        <div class="prev-label">Phiên trước · #${t.last.phien}</div>
        <span class="prev-side ${t.last.ket_qua}">${t.last.ket_qua==='TAI'?'TÀI':'XỈU'}</span>
      </div>
      <div class="prev-info">
        <div style="font-size:11px;color:var(--txt3)">Điểm ${t.last.tong??'—'}</div>
        <div style="font-size:11px;color:var(--txt3)">${(t.last.xuc_xac||[]).join('-')||'—'}</div>
      </div>
      <div>
        <div class="prev-label">AI dự đoán</div>
        <div>${side(t.last.du_doan)}</div>
      </div>
      <div class="icon-big">${t.last.trang_thai==='win'?'✅':t.last.trang_thai==='lose'?'❌':'—'}</div>
    </div>`:''}

    ${t.err?`<div style="padding:9px 12px;background:var(--red-s);border:1.5px solid #fca5a5;border-radius:9px;color:var(--red);font-size:11px;margin-bottom:12px">⚠ ${esc(t.err)}</div>`:''}

    <!-- Expert votes chi tiết -->
    <details style="margin-top:14px">
      <summary style="font-size:11px;font-weight:800;color:var(--txt3);cursor:pointer;letter-spacing:.06em;text-transform:uppercase;padding:7px 0;border-top:1.5px solid var(--bd)">
        22 Model Lớn · P(TÀI) / Trọng số
      </summary>
      <div style="margin-top:10px">
        ${ex.map(x=>`<div style="margin-bottom:4px">
          <div class="expert-row">
            <span class="expert-name">${esc(x.name.replaceAll('_',' '))}</span>
            <div class="track"><i style="width:${Math.min(100,Math.max(0,x.w*100))}%"></i></div>
            <span class="expert-meta">${(x.w*100).toFixed(1)}% · ${(x.p*100).toFixed(1)}%</span>
          </div>
          <div class="group-tag">${esc(x.group)}</div>
        </div>`).join('')}
      </div>
    </details>
  </article>`;
}

/* ── STAT ROW ── */
function drawStatRow(){
  if(!DATA.length)return;
  // TÍNH RIÊNG TỪNG BÀN — không gộp lịch sử 2 bàn với nhau
  const cards=[];
  DATA.forEach(t=>{
    const rows=t.hist||[];
    const w=rows.filter(h=>h.trang_thai==='win').length;
    const l=rows.filter(h=>h.trang_thai==='lose').length;
    const acc=w+l>0?Math.round(w*100/(w+l)):0;
    const live=rows.filter(h=>h.live);
    const lw=live.filter(h=>h.trang_thai==='win').length;
    const ll=live.filter(h=>h.trang_thai==='lose').length;
    const lacc=lw+ll>0?Math.round(lw*100/(lw+ll)):0;
    const nm=esc(t.name);
    const color=t.code==='hu'?'var(--purple)':'var(--blue)';
    cards.push(
      {label:'Tổng phiên · '+nm,val:rows.length,note:w+'W / '+l+'L',sa:color},
      {label:'Live acc · '+nm,val:lacc+'%',note:lw+'W / '+ll+'L (live)',sa:'var(--green-b)'},
      {label:'Tổng acc · '+nm,val:acc+'%',note:w+'W / '+l+'L',sa:'var(--cyan)'},
      {label:'Upstream · '+nm,val:(t.ms||0)+'ms',note:t.err?('⚠ '+esc(t.err).slice(0,40)):'OK',sa:'var(--amber)'}
    );
  });
  $('statRow').innerHTML=cards.map((s,i)=>`<div class="stat-card" style="--sa:${s.sa};animation-delay:${i*.04}s">
    <div class="stat-label">${esc(s.label)}</div>
    <div class="stat-val">${esc(s.val)}</div>
    <div class="stat-note">${esc(s.note)}</div>
  </div>`).join('');
}

/* ── HISTORY FEED — style như ảnh ── */
function histTable(t){
  const rows = t.hist || [];
  const st   = t.st_all || {};
  const w = st.win??0, l = st.lose??0;
  const acc = w+l>0 ? Math.round(w*100/(w+l)) : 0;
  const pd  = t.pending;
  const acColor = acc>=65?'#22c55e':acc>=55?'#3b82f6':'#ef4444';

  /* pill TAI / XIU — bo tròn, màu nền nhẹ */
  function sPill(s){
    if(!s) return '<span style="color:#9ca3af;font-size:13px">—</span>';
    const tai = s==='TAI';
    return `<span style="
      display:inline-block;padding:5px 18px;border-radius:999px;
      font-size:13px;font-weight:800;letter-spacing:.02em;
      background:${tai?'#fce7ea':'#e0f2fe'};
      color:${tai?'#e11d48':'#0369a1'};
    ">${tai?'Tài':'Xiu'}</span>`;
  }

  /* badge kết luận — bo tròn */
  function bBadge(ts){
    if(ts==='win') return `<span style="
      display:inline-flex;align-items:center;gap:5px;
      padding:5px 14px;border-radius:999px;font-size:12px;font-weight:800;
      background:#dcfce7;color:#15803d;">✓ Đúng</span>`;
    if(ts==='lose') return `<span style="
      display:inline-flex;align-items:center;gap:5px;
      padding:5px 14px;border-radius:999px;font-size:12px;font-weight:800;
      background:#fee2e2;color:#dc2626;">✗ Sai</span>`;
    return `<span style="
      display:inline-flex;align-items:center;gap:5px;
      padding:5px 14px;border-radius:999px;font-size:12px;font-weight:700;
      background:#fef9c3;color:#a16207;">⏳</span>`;
  }

  /* Header stat: W · L · % · #phien — y hệt ảnh */
  const hdr = `<div style="padding:14px 18px 10px;border-bottom:1px solid #f1f5f9">
    <div style="font-size:11px;font-weight:800;color:#94a3b8;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px">
      ${t.code==='hu'?'● HŨ':'● MD5'}
      <span style="margin-left:6px;font-weight:600;color:#cbd5e1">TX</span>
    </div>
    <div style="display:flex;align-items:baseline;gap:20px;flex-wrap:wrap">
      <div style="display:flex;align-items:baseline;gap:5px">
        <span style="font-size:28px;font-weight:900;color:#22c55e;font-family:'JetBrains Mono',monospace">${w}</span>
        <span style="font-size:11px;font-weight:800;color:#86efac;text-transform:uppercase">Thắng</span>
      </div>
      <div style="display:flex;align-items:baseline;gap:5px">
        <span style="font-size:28px;font-weight:900;color:#ef4444;font-family:'JetBrains Mono',monospace">${l}</span>
        <span style="font-size:11px;font-weight:800;color:#fca5a5;text-transform:uppercase">Thua</span>
      </div>
      <div style="display:flex;align-items:baseline;gap:5px">
        <span style="font-size:28px;font-weight:900;color:${acColor};font-family:'JetBrains Mono',monospace">${acc}.0%</span>
        <span style="font-size:11px;font-weight:800;color:#94a3b8;text-transform:uppercase">Tỉ lệ</span>
      </div>
      <div style="display:flex;align-items:baseline;gap:5px;margin-left:auto">
        <span style="font-size:22px;font-weight:900;color:#1e293b;font-family:'JetBrains Mono',monospace">#${rows[0]?.phien??'—'}</span>
        <span style="font-size:10px;font-weight:800;color:#94a3b8;text-transform:uppercase">Phiên</span>
      </div>
    </div>
  </div>`;

  /* Col header */
  const colH = `<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;
    padding:7px 18px;background:#f8fafc;border-bottom:1px solid #f1f5f9">
    <div style="font-size:10px;font-weight:800;color:#94a3b8;letter-spacing:.1em;text-transform:uppercase">THỜI GIAN</div>
    <div style="font-size:10px;font-weight:800;color:#94a3b8;letter-spacing:.1em;text-transform:uppercase;text-align:center">DỰ ĐOÁN</div>
    <div style="font-size:10px;font-weight:800;color:#94a3b8;letter-spacing:.1em;text-transform:uppercase;text-align:center">KẾT QUẢ</div>
    <div style="font-size:10px;font-weight:800;color:#94a3b8;letter-spacing:.1em;text-transform:uppercase;text-align:right">XÁC MINH</div>
  </div>`;

  /* Phiên đang chạy */
  const runRow = pd ? `<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;
    align-items:center;padding:14px 18px;
    background:linear-gradient(90deg,#f0fdf4,#fff);
    border-bottom:1px solid #f1f5f9">
    <div>
      <span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:800;color:#22c55e">
        <span style="width:7px;height:7px;border-radius:50%;background:#22c55e;animation:pulse 1.2s infinite"></span>
        running...
      </span>
    </div>
    <div style="text-align:center">${sPill(pd.du_doan)}</div>
    <div style="text-align:center;color:#94a3b8;font-size:13px">Chờ...</div>
    <div style="text-align:right">${bBadge('cho')}</div>
  </div>` : '';

  /* Các dòng lịch sử */
  const bodyRows = rows.length ? rows.map(h => {
    const isW = h.trang_thai==='win', isL = h.trang_thai==='lose';
    const bg = isW?'#f0fdf4':isL?'#fff5f5':'#fff';
    const dices = (h.xuc_xac||[]).join('-');
    const sub = dices ? `${dices}/${h.tong??''}` : '';
    return `<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;
      align-items:center;padding:13px 18px;
      background:${bg};border-bottom:1px solid #f8fafc;
      transition:background .12s"
      onmouseover="this.style.background='#f8fafc'"
      onmouseout="this.style.background='${bg}'">
      <div>
        <div style="font-size:13px;font-weight:700;color:#374151">#${h.phien}</div>
        ${sub?`<div style="font-size:11px;color:#9ca3af;margin-top:1px;font-family:'JetBrains Mono',monospace">${sub}</div>`:''}
      </div>
      <div style="text-align:center">${sPill(h.du_doan)}</div>
      <div style="text-align:center">${sPill(h.ket_qua)}</div>
      <div style="text-align:right">${bBadge(h.trang_thai)}</div>
    </div>`;
  }).join('') : `<div style="padding:48px;text-align:center;color:#94a3b8;font-size:13px">Chưa có dữ liệu</div>`;

  return `<section style="
    margin-bottom:20px;border-radius:16px;overflow:hidden;
    background:#fff;border:1px solid #e2e8f0;
    box-shadow:0 1px 3px rgba(0,0,0,.06),0 4px 16px rgba(0,0,0,.04)">
    ${hdr}${colH}${runRow}<div>${bodyRows}</div>
  </section>`;
}

/* ── 62 MODELS DISPLAY ── */
const MODEL_INFO=[
  {name:"M01 Cầu Nhận Biết",group:"Pattern",desc:"Nhận biết 1-1, 2-2, bệt, mix rồi dự đoán theo pattern"},
  {name:"M02 Trend Ngắn/Dài",group:"Trend",desc:"Bắt xu hướng bằng EMA5 vs EMA15, momentum"},
  {name:"M03 Balance 12",group:"Balance",desc:"Kiểm tra chênh lệch 12 phiên → dự đoán phía thiểu số"},
  {name:"M04 Cầu Ngắn Hạn",group:"Pattern",desc:"Bắt cầu 3-5 phiên, pair freq, triple freq"},
  {name:"M05 Weight Balance",group:"Balance",desc:"Cân bằng TAI/XIU khi bias > 20%"},
  {name:"M06 Bẻ Cầu",group:"Strategy",desc:"Quyết định bắt theo hay bẻ dựa trên volatility + run length"},
  {name:"M07 Weight Equalize",group:"Meta",desc:"Kéo trọng số về trung bình khi std > 0.3"},
  {name:"M08 Cầu Xấu",group:"Quality",desc:"Phát hiện cầu không có pattern, giảm confidence"},
  {name:"M09 Cầu Cơ Bản",group:"Pattern",desc:"Nhận dạng 1-2-1, 2-1-2, 3-1, 1-3 rồi hành động"},
  {name:"M10 Xác Suất Bẻ",group:"Probability",desc:"Bayesian update xác suất bẻ cầu"},
  {name:"M11 Dice Biến Động",group:"Dice",desc:"Phân tích zone xúc xắc, nhận dạng pattern nhà cái"},
  {name:"M12 Multi Pattern",group:"Pattern",desc:"Bảng lookup pattern 2-5 phiên từ lịch sử"},
  {name:"M13 Performance",group:"Meta",desc:"Đánh giá hiệu suất 50 phiên, điều chỉnh trọng số"},
  {name:"M14 Bẻ Trend",group:"Probability",desc:"Tính xác suất bẻ sau xu hướng mạnh"},
  {name:"M15 Follow?",group:"Strategy",desc:"Suy nghĩ có nên follow trend dựa 4 chỉ số"},
  {name:"M16 XS Bẻ 2",group:"Probability",desc:"Geometric mean 4 nguồn xác suất bẻ"},
  {name:"M17 Global Balance",group:"Meta",desc:"Cân bằng trọng số thực chiến + hiệu suất"},
  {name:"M18 Trend Ngắn",group:"Trend",desc:"Micro-trend 3 phiên + autocorrelation"},
  {name:"M19 Popular Trend",group:"Pattern",desc:"Cluster, zigzag, Markov bậc 2"},
  {name:"M20 Max Performance",group:"Ensemble",desc:"Lấy top 5 signals mạnh nhất (trọng số 1.5×)"},
  {name:"M21 Global Balance",group:"Meta",desc:"Override khi ensemble bias > 80%"},
  {name:"M22 Nhà Cái",group:"Intelligence",desc:"Phát hiện cầu gãy, đọc pattern nhà cái (trọng số 1.2×)"},
];
const PA_INFO=[
  {name:"PA01 Markov-1",g:"Markov"},{name:"PA02 Markov-2",g:"Markov"},{name:"PA03 EMA Cross",g:"Trend"},
  {name:"PA04 RSI",g:"Oscillator"},{name:"PA05 Entropy",g:"Info"},{name:"PA06 Z-Score",g:"Stat"},
  {name:"PA07 Runs Test",g:"Stat"},{name:"PA08 Momentum 3",g:"Mom"},{name:"PA09 Reversion",g:"Balance"},
  {name:"PA10 Cluster",g:"Pattern"},{name:"PA11 Sum Band",g:"Dice"},{name:"PA12 Dice Var",g:"Dice"},
  {name:"PA13 Anti Streak",g:"Strategy"},{name:"PA14 1-1 Mini",g:"Pattern"},{name:"PA15 Sum Zone",g:"Dice"},
  {name:"PA16 Markov-3",g:"Markov"},{name:"PA17 Recent Bias",g:"Balance"},{name:"PA18 Streak Penalty",g:"Strategy"},
  {name:"PA19 Sum Parity",g:"Dice"},{name:"PA20 Med Balance",g:"Balance"},{name:"PA21 Vol Filter",g:"Filter"},
  {name:"PA22 Consec Loss",g:"Adaptive"},{name:"PA23 Run Pattern",g:"Pattern"},{name:"PA24 Autocorr-2",g:"Stat"},
  {name:"PA25 Freq-5",g:"Pattern"},{name:"PA26 Alter",g:"Pattern"},{name:"PA27 Sum Mean",g:"Dice"},
  {name:"PA28 Gap Detect",g:"Pattern"},{name:"PA29 Inv Gap",g:"Pattern"},{name:"PA30 Half-Half",g:"Balance"},
  {name:"PA31 Quad Pat",g:"Pattern"},{name:"PA32 Sum Dev",g:"Dice"},{name:"PA33 Even/Odd",g:"Dice"},
  {name:"PA34 Consec Same",g:"Pattern"},{name:"PA35 Phi Coeff",g:"Info"},{name:"PA36 Triple Same",g:"Pattern"},
  {name:"PA37 Smart Fall",g:"Fallback"},{name:"PA38 Anti Herd",g:"Contrarian"},{name:"PA39 Period",g:"Pattern"},
  {name:"PA40 Final Judge",g:"Final"},
];
const GROUP_COLOR={Pattern:'var(--blue)',Trend:'var(--cyan)',Balance:'var(--green)',Meta:'var(--purple)',Strategy:'#d08020',Probability:'#b040a0',Dice:'#20a070',Ensemble:'var(--red)',Quality:'#a08020',Intelligence:'#c04040',Markov:'#6060d0',Oscillator:'#20c060',Stat:'#8060d0',Info:'#30b080',Mom:'#d06040',Filter:'#60a040',Adaptive:'#c05020',Contrarian:'#4080d0',Fallback:'#808080',Final:'var(--red)'};

function drawModels(){
  const mg=$('modelsGrid'); if(!mg)return;
  let html=`<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;margin-bottom:20px">`;
  MODEL_INFO.forEach((m,i)=>{
    const c=GROUP_COLOR[m.group]||'var(--blue)';
    html+=`<div class="card" style="padding:14px;border-left:3px solid ${c};animation-delay:${i*.03}s">
      <div style="font-size:9px;font-weight:900;letter-spacing:.12em;color:${c};text-transform:uppercase;margin-bottom:5px">${m.group}</div>
      <div style="font-size:13px;font-weight:800;color:var(--txt);margin-bottom:5px">${m.name}</div>
      <div style="font-size:11px;color:var(--txt3);line-height:1.5">${m.desc}</div>
    </div>`;
  });
  html+='</div>';
  html+=`<div style="margin:0 0 10px;font-size:11px;font-weight:800;color:var(--txt3);letter-spacing:.12em;text-transform:uppercase">40 Model Phụ Trợ (PA01–PA40)</div>`;
  html+=`<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:8px">`;
  PA_INFO.forEach(p=>{
    const c=GROUP_COLOR[p.g]||'var(--txt4)';
    html+=`<div style="padding:9px 12px;background:var(--surf);border:1.5px solid var(--bd);border-radius:10px;border-left:3px solid ${c}">
      <div style="font-size:8px;font-weight:900;color:${c};letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px">${p.g}</div>
      <div style="font-size:11px;font-weight:800;color:var(--txt)">${p.name}</div>
    </div>`;
  });
  html+='</div>';
  mg.innerHTML=html;
}

/* ── DRAW ALL ── */
function draw(){
  $('boards').innerHTML=DATA.map(board).join('');
  $('historyBoards').innerHTML=DATA.map(histTable).join('');
  drawStatRow();
  const online=DATA.every(x=>x.ready);
  $('apiStatus').textContent=online?'API ONLINE':'DEGRADED';
  $('apiDot').className='ldot'+(online?'':' bad');
}

/* ── LOAD ── */
async function load(){
  try{
    const r=await fetch('/admin/data',{cache:'no-store'});
    if(r.status===401){location.href='/admin';return}
    const j=await r.json();
    if(!j.ok)throw Error(j.loi||'API error');
    DATA=j.tables||[];draw();timer=4;
  }catch(e){
    $('apiStatus').textContent='ERROR';
    $('apiDot').className='ldot bad';
    toast('Lỗi: '+e.message,false);
  }
}

/* ── ACT ── */
async function act(c,a){
  try{
    const r=await fetch(`/admin/act/${c}/${a}`,{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();
    toast(j.ok?'Đã thực hiện: '+a:'Lỗi: '+(j.loi||''),j.ok);load();
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
    if(!prot.code&&j.has_code)$('codeDisplay').textContent='••••••';
  }catch(e){$('protInfo').textContent='Lỗi tải trạng thái'}
}
async function genCode(){
  try{
    const r=await fetch('/admin/aprot/gen',{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();if(!j.ok)throw Error(j.loi);
    prot.code=j.code;prot.has_code=true;
    $('codeDisplay').textContent=j.code;
    $('urlPreview').innerHTML=`<b>${location.origin}/<span style="color:var(--blue)">${esc(j.code)}</span>/tx/hu</b>`;
    toast('Đã tạo mã: '+j.code);loadProt();
  }catch(e){toast('Tạo mã thất bại',false)}
}
async function setProt(action){
  if(action==='enable'&&!prot.has_code){toast('Hãy tạo mã trước',false);return}
  try{
    const fd=new FormData();fd.append('action',action);
    const r=await fetch('/admin/aprot/set',{method:'POST',headers:{'X-CSRF-Token':CSRF},body:fd});
    const j=await r.json();if(!j.ok)throw Error(j.loi);
    toast(action==='enable'?'✅ Đã bật bảo vệ':'Đã tắt bảo vệ');loadProt();
  }catch(e){toast('Không cập nhật được',false)}
}
async function revokeCode(){
  if(!confirm('Thu hồi mã sẽ TẮT bảo vệ. Tiếp tục?'))return;
  try{
    const r=await fetch('/admin/aprot/revoke',{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json();if(!j.ok)throw Error(j.loi);
    prot={enabled:false,has_code:false,code:''};
    $('codeDisplay').textContent='••••••';$('urlPreview').textContent='Tạo mã để xem URL';
    toast('Đã thu hồi mã');loadProt();
  }catch(e){toast('Thu hồi thất bại',false)}
}
function copyCode(){
  if(!prot.code){toast('Chưa có mã',false);return}
  navigator.clipboard?.writeText(prot.code)
    .then(()=>toast('Đã copy: '+prot.code))
    .catch(()=>toast('Clipboard lỗi',false))
}

/* ── COUNTDOWN ── */
setInterval(()=>{timer=Math.max(0,timer-1);$('countdown').textContent=timer;if(timer===0){load();timer=4}},1000);
load();loadProt();
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
