# -*- coding: utf-8 -*-
"""PAW TX API v12 — Engine88 mặc định (PAW_ENGINE=89 → Engine89) (Engine87 + module bệt nhẹ thích nghi, tối ưu cho nguồn ~105 phiên + tích lũy dữ liệu thô)."""
import hmac, json, math, os, secrets, threading, time
from collections import deque, Counter, defaultdict
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import requests
from flask import Flask, jsonify, make_response, redirect, request, session
from werkzeug.exceptions import HTTPException

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
# Khóa phiên ổn định: nếu không đặt SECRET_KEY thì suy ra từ ADMIN_PASS (tránh mất đăng nhập khi restart / nhiều worker)
import hashlib as _hl
app.secret_key = os.getenv("SECRET_KEY") or (
    _hl.sha256(("paw-session:" + os.getenv("ADMIN_PASS", "")).encode()).hexdigest()
    if os.getenv("ADMIN_PASS") else secrets.token_hex(32))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8)
)
app.json.ensure_ascii = False
app.json.sort_keys    = False

@app.after_request
def add_cors(resp):
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
            if dice_ok: point = sum(dices)
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

# ── Tích lũy dữ liệu thô: nguồn chỉ trả ~105 phiên, nên gom thêm qua các lần gọi + lưu file ──
RAW_FILE = os.getenv("RAW_FILE", "/tmp/paw_tx_raw.json")
RAW_MAX  = int(os.getenv("RAW_MAX", "300"))
_raw_lock = threading.Lock()

def merge_rows(saved, fetched):
    """Gộp dữ liệu đã lưu + vừa lấy. Giữ TOÀN BỘ phiên vừa lấy; phần cũ đã lưu chỉ giữ nếu liền mạch
    (không có lỗ phiên) để không học trên chuỗi bị ghép sai."""
    fetched = sorted((r for r in fetched if isinstance(r, dict) and "id" in r), key=lambda r: int(r["id"]))
    if not fetched: return []
    first = int(fetched[0]["id"]); older = []; need = first - 1
    for r in sorted((r for r in saved if isinstance(r, dict) and "id" in r and int(r["id"]) < first),
                    key=lambda r: int(r["id"]), reverse=True):
        if int(r["id"]) != need: break
        older.append(r); need -= 1
    return (older[::-1] + fetched)[-RAW_MAX:]

def raw_load(code):
    try:
        with _raw_lock, open(RAW_FILE, "r", encoding="utf-8") as f: d = json.load(f)
        v = d.get(code, []) if isinstance(d, dict) else []
        return v if isinstance(v, list) else []
    except (OSError, ValueError, TypeError): return []

def raw_save(code, rows):
    try:
        with _raw_lock:
            try:
                with open(RAW_FILE, "r", encoding="utf-8") as f: d = json.load(f)
                if not isinstance(d, dict): d = {}
            except (OSError, ValueError, TypeError): d = {}
            d[code] = rows
            tmp = RAW_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False)
            os.replace(tmp, RAW_FILE)
    except OSError: pass

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
PAW TX · ENGINE 84 — 22 Model Lớn + 22 Model Mini + 40 Model Phụ Trợ
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
    """S8: Xác suất bẻ cầu dựa trên lịch sử của độ dài run đó"""
    if len(seq) < 20: return 0.5
    breaks, total = 0, 0
    cur, cnt = seq[0], 1
    for i in range(1, len(seq)):
        if seq[i] == cur:
            cnt += 1
        else:
            if cnt == run_len:
                total += 1  # đây là lần run_len kết thúc
                breaks += 1
            cur, cnt = seq[i], 1
    if total == 0: return 0.5 + min(0.1, run_len * 0.02)
    return breaks/total

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
        # Bệt dài: bẻ — tăng conf theo run_len
        if cau == "BET_DAI":
            pred = _opp(last)
            brk = sub_break_prob_historical(seq, rlen)
            # run=5→0.65, run=6→0.70, run=7+→0.75+
            base = 0.55 + min(0.20, (rlen - 4) * 0.05)
            conf = _clamp(base + (brk-0.5)*0.5)
            return {"side": pred, "conf": conf, "reason": f"M01: Bệt {rlen} → bẻ mạnh, p_brk={brk:.2f}"}
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
#  ENGINE 84 — ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════
class Engine84:
    """Điều phối 84 model (22 lớn + 22 mini + 40 phụ trợ)"""

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
        if hit:
            self.win_streak += 1; self.loss_streak = 0; self.total_w += 1
        else:
            self.loss_streak += 1; self.win_streak = 0; self.total_l += 1
        # Cập nhật hiệu suất từng model
        for m in self.large + self.support:
            if hasattr(m, 'name'):
                self.perf_m.update_perf(m.name, hit)

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

        for m in self.large:
            try:
                sig = m.predict(**ctx)
                if isinstance(sig, dict) and sig.get("side") in ("TAI", "XIU"):
                    sig["model"] = m.name; sig["weight"] = m.w
                    all_signals.append(sig); all_votes.append(sig["side"])
            except Exception: pass

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
            except Exception: pass

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

                except Exception: pass

        # ══════════════════════════════════════════════════════════════
        # --- BỆT DETECTOR: Override ensemble khi phát hiện bệt ---
        # Logic: khi run_len >= 2 mà các model đang vote "theo bệt"
        # nhưng lịch sử cho thấy bệt hay gãy → ép bẻ mạnh hơn
        # ══════════════════════════════════════════════════════════════
        bet_override_reason = ""
        if rlen >= 2 and total_w > 0:
            # Tính % model đang vote "theo bệt" (vote cùng chiều last_v)
            theo_votes = sum(1 for s in all_signals if s.get("side") == last_v)
            be_votes   = sum(1 for s in all_signals if s.get("side") != last_v)
            total_votes = theo_votes + be_votes

            # Xác suất gãy lịch sử
            p_break_hist = sub_break_prob_historical(seq, rlen)

            # Hệ số áp lực bẻ: tăng dần theo run_len
            # run=2 → 0.0, run=3 → 0.15, run=4 → 0.30, run=5+ → 0.45+
            bet_pressure = min(0.55, max(0.0, (rlen - 2) * 0.15))

            # Nếu lịch sử gãy cao (>52%) VÀ run đủ dài → thêm áp lực bẻ
            if p_break_hist > 0.52 and rlen >= 3:
                # Điều chỉnh score ngược chiều bệt
                be_side    = _opp(last_v)
                adj_factor = bet_pressure * (p_break_hist - 0.5) * 2.0  # 0..0.55
                adj_amount = adj_factor * total_w
                if be_side == "TAI":
                    score_tai += adj_amount
                    score_xiu -= adj_amount * 0.5
                else:
                    score_xiu += adj_amount
                    score_tai -= adj_amount * 0.5
                bet_override_reason = f"BET_BREAK run={rlen} p_brk={p_break_hist:.2f} adj={adj_factor:.2f}"

            # Nếu ensemble quá đồng thuận theo bệt (>72%) → kéo về 50/50
            if total_votes > 0 and theo_votes / total_votes > 0.72 and rlen >= 3:
                # Cân bằng lại — không để ensemble bị "bẫy bệt"
                mid = (score_tai + score_xiu) / 2
                pull_strength = min(0.4, (theo_votes/total_votes - 0.72) * 1.5)
                score_tai = score_tai * (1 - pull_strength) + mid * pull_strength
                score_xiu = score_xiu * (1 - pull_strength) + mid * pull_strength
                bet_override_reason += f" | HERD_PULL theo={theo_votes}/{total_votes} pull={pull_strength:.2f}"

            # Cầu bệt rất dài (>=6): luôn bẻ mạnh, bất kể ensemble
            if rlen >= 6:
                be_side = _opp(last_v)
                force_adj = 0.35 * total_w
                if be_side == "TAI":
                    score_tai += force_adj; score_xiu -= force_adj
                else:
                    score_xiu += force_adj; score_tai -= force_adj
                bet_override_reason = f"FORCE_BREAK run={rlen}>=6"

        # ══════════════════════════════════════════════════════════════
        # --- LOSS STREAK BET DETECTOR ---
        # Thua liên tiếp trong cầu bệt → tăng mạnh xác suất bẻ
        # ══════════════════════════════════════════════════════════════
        if self.loss_streak >= 2 and rlen >= 2 and total_w > 0:
            # Đang bệt mà thua >=2 lần → khả năng cao engine đang theo sai
            # Đảo ngược bias hiện tại
            current_bias = last_v  # engine đang "theo" bệt this side
            flip_strength = min(0.45, self.loss_streak * 0.08)  # 2→0.16, 3→0.24, 4→0.32, 5→0.40
            flip_amount = flip_strength * total_w
            if _opp(current_bias) == "TAI":
                score_tai += flip_amount; score_xiu -= flip_amount * 0.3
            else:
                score_xiu += flip_amount; score_tai -= flip_amount * 0.3
            if bet_override_reason:
                bet_override_reason += f" | LOSS_FLIP streak={self.loss_streak} flip={flip_strength:.2f}"
            else:
                bet_override_reason = f"LOSS_FLIP_BET streak={self.loss_streak} run={rlen}"

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
            conf_pct = max(50, min(89, int(50 + gap*45 + 2)))

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
        }

    def update(self, pred_side: str, actual_side: str):
        self.learn(pred_side, actual_side)


# ══════════════════════════════════════════════════════════════════════════
#  ENGINE 85 — Ensemble cân bằng, tự đo hiệu suất từng module, bắt bệt bằng dữ liệu
#  Sửa các lỗi của Engine84:
#   1) learn() chấm điểm MỌI module bằng kết quả chung -> trọng số hiệu suất vô nghĩa.
#      Nay mỗi module được chấm bằng đúng dự đoán CỦA NÓ.
#   2) M05/M20/M21 (meta) không nhận ensemble_votes/all_signals -> M20 luôn "ngược phiên trước"
#      với trọng số 1.5. Nay meta chạy lượt 2 với tín hiệu thật, trọng số thấp.
#   3) Luật FORCE_BREAK/BET_PRESSURE cố định (ép bẻ bệt) -> thay bằng M23/M24 học từ dữ liệu.
#   4) Không module nào được quá CAP_SHARE tổng phiếu; có bù lệch khi dự đoán nghiêng 1 phía
#      so với kết quả thực.
#   5) Độ tin cậy lấy từ hiệu suất đo thực tế (cận dưới), không còn 50 + gap*45.
# ══════════════════════════════════════════════════════════════════════════
class M23_StreakRegime:
    """Học xác suất 'bệt tiếp' theo độ dài bệt hiện tại từ chính chuỗi quan sát (có decay + shrink).
    Chỉ ra tín hiệu khi lệch khỏi 50% có ý nghĩa; nếu không thì bỏ phiếu trắng."""
    name = "M23_STREAK_REGIME"; group = "Regime"
    def __init__(self): self.w = 1.0

    def predict(self, seq, **kw) -> Dict:
        n = len(seq)
        if n < 30:
            return {"side": None, "conf": 0.5, "reason": "M23: chưa đủ dữ liệu"}
        last, r = _last_run(seq)
        b = min(r, 6)
        run = 1; cont = brk = 0.0; decay = 0.985
        for i in range(n - 1):
            if i > 0:
                run = run + 1 if seq[i] == seq[i - 1] else 1
            if min(run, 6) == b:
                wgt = decay ** (n - 2 - i)
                if seq[i + 1] == seq[i]: cont += wgt
                else: brk += wgt
        neff = cont + brk
        p = (cont + 5.0) / (neff + 10.0)
        z = (p - 0.5) / math.sqrt(0.25 / (neff + 10.0))
        if abs(z) < 1.0:
            return {"side": None, "conf": 0.5, "reason": f"M23: bệt {r} p_tiếp={p:.2f} chưa lệch rõ"}
        side = last if p > 0.5 else _opp(last)
        conf = 0.5 + min(0.08, abs(p - 0.5))
        return {"side": side, "conf": conf,
                "reason": f"M23: bệt {r} p_tiếp={p:.2f} z={z:.1f} → {'theo' if p > 0.5 else 'bẻ'}"}


class M24_MarkovDecay:
    """Markov bậc 3 có decay + shrink: P(TAI | 3 kết quả gần nhất)."""
    name = "M24_MARKOV_DECAY"; group = "Regime"
    def __init__(self): self.w = 1.0

    def predict(self, seq, **kw) -> Dict:
        n = len(seq)
        if n < 40:
            return {"side": None, "conf": 0.5, "reason": "M24: chưa đủ dữ liệu"}
        ctx = tuple(seq[-3:]); t = x = 0.0; decay = 0.99
        for i in range(n - 3):
            if tuple(seq[i:i + 3]) == ctx:
                wgt = decay ** (n - 4 - i)
                if seq[i + 3] == "TAI": t += wgt
                else: x += wgt
        neff = t + x
        p = (t + 4.0) / (neff + 8.0)
        z = (p - 0.5) / math.sqrt(0.25 / (neff + 8.0))
        if abs(z) < 1.0:
            return {"side": None, "conf": 0.5, "reason": "M24: ngữ cảnh chưa lệch rõ"}
        return {"side": "TAI" if p > 0.5 else "XIU", "conf": 0.5 + min(0.08, abs(p - 0.5)),
                "reason": f"M24: ctx={''.join(c[0] for c in ctx)} p_tai={p:.2f} z={z:.1f}"}


class Engine85(Engine84):
    SHRINK_N  = 30      # độ mạnh prior kéo hiệu suất module về 50%
    CAP_SHARE = 0.07    # 1 module tối đa 7% tổng phiếu
    CONF_CAP  = 0.62    # trần độ tin cậy mà 1 module được phép đóng góp
    META = ("M05_WEIGHT_BAL", "M20_MAX_PERF", "M21_GLOBAL_BAL")

    def __init__(self):
        super().__init__()
        self.large.append(M23_StreakRegime()); self.large.append(M24_MarkovDecay())
        self.own = defaultdict(lambda: deque(maxlen=60))   # tên module -> deque(1/0) theo DỰ ĐOÁN CỦA CHÍNH NÓ
        self._last_sig = {}
        self.ens_hits = deque(maxlen=200)
        self.pred_sides = deque(maxlen=30)
        self.last_info = {}

    # --- học: chấm điểm đúng từng module ---
    def learn(self, predicted, actual):
        if not predicted or not actual: return
        hit = predicted == actual
        self.pred_hist.append(predicted); self.result_hist.append(actual)
        if hit: self.win_streak += 1; self.loss_streak = 0; self.total_w += 1
        else:   self.loss_streak += 1; self.win_streak = 0; self.total_l += 1
        for name, side in self._last_sig.items():
            self.own[name].append(1 if side == actual else 0)
        self.ens_hits.append(1 if hit else 0)
        self.pred_sides.append(predicted)

    def _w_perf(self, name):
        h = self.own.get(name); n = len(h) if h else 0
        post = (sum(h) + 0.5 * self.SHRINK_N) / (n + self.SHRINK_N) if n else 0.5
        return min(1.5, max(0.2, 1.0 + (post - 0.5) * 8.0))

    def _edge(self):
        n = len(self.ens_hits)
        if n < 20: return 0.0, None, n
        acc = sum(self.ens_hits) / n
        lb = acc - 1.64 * math.sqrt(0.25 / n)
        return max(0.0, lb - 0.5), acc, n

    def predict(self) -> Dict:
        seq = list(self.seq); sums_h = list(self.sums); dices_h = list(self.dices)
        if len(seq) < 5:
            side = seq[-1] if seq else "TAI"
            return {"side": side, "confidence": 50, "p_tai": 0.5, "reasoning": "Khởi tạo — chưa đủ dữ liệu",
                    "models": [], "loss_streak": self.loss_streak, "run_len": len(seq), "acc30": None}
        last_v, rlen = _last_run(seq)
        ctx = dict(seq=seq, sums_history=sums_h, dices_history=dices_h, loss_streak=self.loss_streak)

        # Lượt 1: module thường
        sigs = {}
        for m in self.large + self.support:
            if m.name in self.META: continue
            try:
                kw = dict(ctx)
                if m in self.support: kw["ensemble_votes"] = []
                s = m.predict(**kw)
                if isinstance(s, dict) and s.get("side") in ("TAI", "XIU"):
                    s["model"] = m.name
                    s["base"] = (m.w * 0.7) if m in self.support else m.w
                    sigs[m.name] = s
            except Exception:
                pass
        # Lượt 2: meta với tín hiệu thật
        votes1 = [s["side"] for s in sigs.values()]
        for m in self.large:
            if m.name not in self.META: continue
            try:
                s = m.predict(seq=seq, ensemble_votes=votes1, all_signals=list(sigs.values()),
                              sums_history=sums_h, dices_history=dices_h)
                if isinstance(s, dict) and s.get("side") in ("TAI", "XIU"):
                    s["model"] = m.name; s["base"] = 0.5   # meta: trọng số thấp, tránh đếm trùng
                    sigs[m.name] = s
            except Exception:
                pass
        self._last_sig = {k: v["side"] for k, v in sigs.items()}

        # Phiếu có hiệu chỉnh: (conf-0.5) bị chặn trần, nhân trọng số đo thực tế
        votes = {}
        for name, s in sigs.items():
            c = min(float(s.get("conf", 0.5)), self.CONF_CAP)
            base = min(1.2, max(0.5, float(s.get("base", 1.0))))
            v = (c - 0.5) * base * self._w_perf(name)
            votes[name] = v if s["side"] == "TAI" else -v
        for _ in range(2):  # chặn mỗi module tối đa CAP_SHARE tổng phiếu
            tot = sum(abs(v) for v in votes.values())
            if tot <= 0: break
            cap = self.CAP_SHARE * tot
            votes = {k: max(-cap, min(cap, v)) for k, v in votes.items()}
        tot = sum(abs(v) for v in votes.values())
        S = sum(votes.values())

        # Bù lệch: dự đoán đang nghiêng 1 phía hơn hẳn thực tế & tín hiệu yếu
        note = ""
        if tot > 0 and len(self.pred_sides) >= 12 and len(seq) >= 20:
            ps = list(self.pred_sides)[-20:]
            pred_tai = ps.count("TAI") / len(ps)
            act_tai = seq[-30:].count("TAI") / len(seq[-30:])
            m0 = abs(S) / tot
            if m0 < 0.12:
                if pred_tai - act_tai > 0.30:
                    S -= 0.15 * tot; note = " | bù lệch→XIU"
                elif act_tai - pred_tai > 0.30:
                    S += 0.15 * tot; note = " | bù lệch→TAI"

        # Quyết định + chống hòa
        if tot <= 0 or abs(S) < 1e-9:
            r = sigs.get("M23_STREAK_REGIME")
            if r: pred = r["side"]
            else:
                ps = list(self.pred_sides)[-10:]
                pred = "XIU" if ps.count("TAI") > ps.count("XIU") else "TAI" if ps.count("XIU") > ps.count("TAI") else last_v
            margin = 0.0
        else:
            pred = "TAI" if S > 0 else "XIU"; margin = abs(S) / tot

        edge, acc, n = self._edge()
        conf_pct = max(50, min(60, 50 + int(round(edge * 100)) + (1 if margin > 0.25 else 0)))
        p_tai = round(0.5 + (conf_pct - 50) / 100 if pred == "TAI" else 0.5 - (conf_pct - 50) / 100, 4)

        top = sorted(votes.items(), key=lambda kv: abs(kv[1]), reverse=True)[:4]
        det = "; ".join(f"[{k}] {sigs[k].get('reason','')}" for k, _ in top)
        reasoning = (f"{pred} {conf_pct}% | TAI={sum(v for v in votes.values() if v>0):.3f} "
                     f"XIU={-sum(v for v in votes.values() if v<0):.3f}{note} | {det}")

        acc30 = None
        if len(self.pred_hist) >= 5:
            k = min(30, len(self.pred_hist))
            acc30 = round(sum(1 for i in range(-k, 0) if self.pred_hist[i] == self.result_hist[i]) / k, 3)
        names = [m.name for m in self.large]
        expert_votes = {nm: 0.0 for nm in names}
        for nm, s in sigs.items():
            if nm in expert_votes:
                c = float(s.get("conf", 0.5))
                expert_votes[nm] = c if s["side"] == "TAI" else 1 - c
        self.last_info = {"has_edge": bool(n >= 50 and edge > 0), "ensemble_acc": acc, "n": n}
        return {"side": pred, "confidence": conf_pct, "p_tai": p_tai, "reasoning": reasoning,
                "experts": {m.name: round(self._w_perf(m.name), 3) for m in self.large},
                "expert_votes": expert_votes, "loss_streak": self.loss_streak, "run_len": rlen,
                "acc30": acc30, "total_signals": len(sigs),
                "models_voted_tai": sum(1 for s in sigs.values() if s["side"] == "TAI"),
                "models_voted_xiu": sum(1 for s in sigs.values() if s["side"] == "XIU"),
                "has_edge": self.last_info["has_edge"]}


# ══════════════════════════════════════════════════════════════════════════
#  ENGINE 87 — Dân chủ thật: mọi module bằng trọng số, boost theo regime chỉ là hệ số tạm thời
#   • KHÔNG dùng m.w. Nhóm lớn chia đều 50% phiếu, nhóm phụ chia đều 50% (base = 0.50/N).
#   • Regime: INSUFFICIENT | RANDOM | 1_1 | 2_2 | 3_3 | ZIGZAG | BET | LONG_BET.
#   • Hiệu suất chấm RIÊNG từng regime (regime_perf), shrink Bayesian, hệ số PERF 0.85–1.15.
#   • Hệ số ngữ cảnh (context) tính lại mỗi predict(), không lưu state.
#   • Confidence = cận dưới Wilson của hiệu suất ensemble đo thực, trần 68%.
#   • Predict 3 lượt: (1) large thường → (2) support thấy vote lượt 1 → (3) meta thấy cả hai.
# ══════════════════════════════════════════════════════════════════════════
def _wilson_lb(hits, n, z=1.64):
    """Cận dưới Wilson của tỉ lệ thắng."""
    if n <= 0: return 0.0
    p = hits / n; z2 = z * z
    den = 1 + z2 / n
    cen = p + z2 / (2 * n)
    mar = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return max(0.0, (cen - mar) / den)


def _dice_for_point(rnd, point):
    """Sinh 3 xúc xắc có tổng = point (dùng cho probe phân nhóm module)."""
    while True:
        a, b = rnd.randint(1, 6), rnd.randint(1, 6)
        c = point - a - b
        if 1 <= c <= 6: return [a, b, c]



def _cont_dir(seq):
    """Hướng bệt đo từ dữ liệu: +1 nếu 'bệt tiếp' lệch >50% có ý nghĩa, -1 nếu 'bẻ' lệch có ý nghĩa, 0 nếu chưa rõ."""
    n = len(seq)
    if n < 30: return 0
    last, r = _last_run(seq); b = min(r, 6)
    run = 1; cont = brk = 0.0
    for i in range(n - 1):
        if i > 0: run = run + 1 if seq[i] == seq[i - 1] else 1
        if min(run, 6) == b:
            w = 0.985 ** (n - 2 - i)
            if seq[i + 1] == seq[i]: cont += w
            else: brk += w
    neff = cont + brk; p = (cont + 5.0) / (neff + 10.0)
    z = (p - 0.5) / math.sqrt(0.25 / (neff + 10.0))
    return 0 if abs(z) < 1.0 else (1 if p > 0.5 else -1)


def _bet_stat(seq, win=240, decay=0.985, prior=4.0):
    """Đo thực tế xác suất 'bệt tiếp' tại các nhịp bệt >=3 trong `win` phiên gần nhất (có decay).
    Trả (p_tiếp, z, n_eff). z nhỏ (<1) = chưa có bằng chứng → module bệt IM, không ép theo/bẻ."""
    W = list(seq)[-win:]; m = len(W)
    if m < 40: return 0.5, 0.0, 0.0
    run = 1; cont = brk = 0.0
    for i in range(m - 1):
        if i > 0: run = run + 1 if W[i] == W[i - 1] else 1
        if run >= 3:
            w = decay ** (m - 2 - i)
            if W[i + 1] == W[i]: cont += w
            else: brk += w
    ne = cont + brk
    p = (cont + prior) / (ne + 2 * prior)
    z = (p - 0.5) / math.sqrt(0.25 / (ne + 2 * prior))
    return p, z, ne


_META87 = ("M05_WEIGHT_BAL", "M07_WEIGHT_EQ", "M13_PERF", "M17_WEIGHT_BAL", "M20_MAX_PERF", "M21_GLOBAL_BAL")
_GROUP_CACHE = {}
_GROUP_LOCK = threading.Lock()


def _classify_modules(model_classes):
    """Phân nhóm module theo HÀNH VI THỰC TẾ trên bộ probe cố định (seed cố định, tính 1 lần, không đổi):
      bet_group[name] ∈ {BREAK, FOLLOW, NEUTRAL}  — khi đang bệt 4–6 phiên (module bẻ hay theo)
      alt_group[name] ∈ {REVERSE, FOLLOW, NEUTRAL} — khi chuỗi xen kẽ 1-1 (module đảo chiều hay theo)
    Đây là thuộc tính tĩnh của module (không phải state của engine)."""
    key = tuple(c.__name__ for c in model_classes)
    with _GROUP_LOCK:
        if key in _GROUP_CACHE: return _GROUP_CACHE[key]
        rnd = random.Random(87_2026)
        sides = ("TAI", "XIU")

        def build(tail):
            pre = [rnd.choice(sides) for _ in range(46)]
            while pre[-1] == tail[0]: pre[-1] = rnd.choice(sides)
            return pre + tail

        bet_probes, alt_probes = [], []
        for _ in range(40):
            s = rnd.choice(sides); bet_probes.append(build([s] * rnd.choice((4, 5, 6))))
            s = rnd.choice(sides); alt = [s if i % 2 == 0 else _opp(s) for i in range(6)]
            alt_probes.append(build(alt))

        def kw_of(seq):
            sums = [rnd.randint(11, 18) if v == "TAI" else rnd.randint(4, 10) for v in seq]
            dices = [_dice_for_point(rnd, p) for p in sums]
            return dict(seq=list(seq), sums_history=sums, dices_history=dices, loss_streak=0,
                        ensemble_votes=[], all_signals=[], tai_total=0, xiu_total=0)

        bet_g, alt_g = {}, {}
        for cls in model_classes:
            m = cls(); name = m.name
            if name in _META87:      # meta phụ thuộc vote của module khác → luôn NEUTRAL
                bet_g[name] = alt_g[name] = "NEUTRAL"; continue
            for probes, store, rev in ((bet_probes, bet_g, "BREAK"), (alt_probes, alt_g, "REVERSE")):
                br = tot = 0
                for seq in probes:
                    try: s = m.predict(**kw_of(seq))
                    except Exception: continue
                    if isinstance(s, dict) and s.get("side") in sides:
                        tot += 1; br += 1 if s["side"] != seq[-1] else 0
                if tot < 10: store[name] = "NEUTRAL"
                else:
                    r = br / tot
                    store[name] = rev if r >= 0.65 else "FOLLOW" if r <= 0.35 else "NEUTRAL"
        _GROUP_CACHE[key] = (bet_g, alt_g)
        return _GROUP_CACHE[key]


class Engine87(Engine85):
    # Meta chạy lượt 3 (thấy vote của cả hai nhóm)
    META = ("M05_WEIGHT_BAL", "M07_WEIGHT_EQ", "M13_PERF", "M17_WEIGHT_BAL", "M20_MAX_PERF", "M21_GLOBAL_BAL")
    REGIMES = ("INSUFFICIENT", "RANDOM", "1_1", "2_2", "3_3", "ZIGZAG", "BET", "LONG_BET")
    PERF_K = 20            # độ mạnh prior kéo hiệu suất regime về 0.5
    PERF_SLOPE = 3.0       # (post-0.5)*3 → bị kẹp ±0.15
    PERF_RANGE = 0.15      # PERF ∈ [0.85, 1.15]
    CONF_CAP = 68          # trần confidence hiển thị
    OVERLAY = False        # Engine88: bật module bệt nhẹ thích nghi
    BS_WIN, BS_DECAY, BS_PRIOR, BS_Z0 = 105, 0.98, 3.0, 0.8   # tham số đo bệt
    OV_MAX = 0.45          # phiếu tối đa của module bệt (so với tổng phiếu nền = 1.0)
    CTX_MODE = "SPEC"      # "OFF": không boost | "SPEC": LONG_BET boost nhóm BẺ cố định (theo yêu cầu) | "DATA": hướng boost đo từ dữ liệu

    # Hệ số ngữ cảnh TẠM THỜI theo regime: {regime: {nhóm_module: hệ_số}}
    CTX_BET = {"LONG_BET": {"BREAK": 1.4, "FOLLOW": 0.7},
               "BET":      {"BREAK": 1.15, "FOLLOW": 0.9}}
    CTX_ALT = {"1_1":     {"REVERSE": 1.4}}

    def __init__(self):
        super().__init__()
        # regime_perf[module][regime] = [hit, miss]
        self.regime_perf = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        self._last_regime = "INSUFFICIENT"
        self.ov_hits = deque(maxlen=40)     # module bệt tự chấm điểm chính nó
        self._ov_side = None
        self._bet_g, self._alt_g = _classify_modules(self._M_LARGE + [M23_StreakRegime, M24_MarkovDecay] + self._M_SUPPORT)

    # ── Regime ────────────────────────────────────────────────────────────
    @staticmethod
    def detect_regime(seq):
        n = len(seq)
        if n < 20: return "INSUFFICIENT"
        last, r = _last_run(seq)
        if r >= 5: return "LONG_BET"
        tail = seq[-6:]
        if len(tail) == 6 and all(tail[i] != tail[i - 1] for i in range(1, 6)): return "1_1"
        runs = _run_lengths(seq[-18:])[1:]            # bỏ run đầu bị cắt
        done = runs[:-1]                              # các run đã hoàn tất
        cur = runs[-1] if runs else r
        if len(done) >= 2 and done[-1] == done[-2] == 2 and cur <= 2: return "2_2"
        if len(done) >= 2 and done[-1] == done[-2] == 3 and cur <= 3: return "3_3"
        if len(done) >= 4 and done[-4:] in ([1, 2, 1, 2], [2, 1, 2, 1]): return "ZIGZAG"
        if r >= 3: return "BET"
        return "RANDOM"

    # ── Hệ số (đều tính lại mỗi lần, KHÔNG lưu) ───────────────────────────
    def _context_weight(self, name, regime, bet_dir=0):
        if regime in self.CTX_BET:
            if self.CTX_MODE == "OFF": return 1.0
            tbl = self.CTX_BET[regime]
            grp = self._bet_g.get(name, "NEUTRAL")
            if self.CTX_MODE == "DATA":
                # Hướng boost lấy từ dữ liệu: bệt đang dính → boost nhóm THEO; bệt hay gãy → boost nhóm BẺ; chưa rõ → 1.0
                up, dn = tbl["BREAK"], tbl["FOLLOW"]
                if bet_dir > 0:  return {"FOLLOW": up, "BREAK": dn}.get(grp, 1.0)
                if bet_dir < 0:  return {"BREAK": up, "FOLLOW": dn}.get(grp, 1.0)
                return 1.0
            return tbl.get(grp, 1.0)
        if regime in self.CTX_ALT: return self.CTX_ALT[regime].get(self._alt_g.get(name, "NEUTRAL"), 1.0)
        return 1.0

    def _bet_overlay(self, seq, regime, last_v):
        """MODULE BỆT NHẸ: chỉ hoạt động khi đang bệt (>=3). Tự đo từ dữ liệu gần đây:
        bệt đang dính → THEO, bệt hay gãy → BẺ, chưa rõ → IM. Tự giảm lực nếu đang đoán trật liên tục."""
        self._ov_side = None
        if regime not in ("BET", "LONG_BET"): return 0.0, ""
        p, z, ne = _bet_stat(seq, self.BS_WIN, self.BS_DECAY, self.BS_PRIOR)
        st = min(1.0, max(0.0, (abs(z) - self.BS_Z0) / 1.5))
        if st <= 0: return 0.0, f"bệt=IM(p={p:.2f})"
        h = list(self.ov_hits)[-16:]
        if len(h) >= 10:
            r = sum(h) / len(h)
            if r < 0.42: st *= 0.4
            elif r > 0.58: st = min(1.0, st * 1.15)
        follow = p > 0.5
        side = last_v if follow else _opp(last_v)
        self._ov_side = side
        w = self.OV_MAX * st
        return (w if side == "TAI" else -w), f"bệt={'THEO' if follow else 'BẺ'}(p={p:.2f},z={z:.1f},lực={st:.2f})"

    def _perf_weight(self, name, regime):
        h, m = self.regime_perf[name][regime] if name in self.regime_perf else (0, 0)
        n = h + m
        post = (h + 0.5 * self.PERF_K) / (n + self.PERF_K)
        return 1.0 + max(-self.PERF_RANGE, min(self.PERF_RANGE, (post - 0.5) * self.PERF_SLOPE))

    def _edge(self):
        n = len(self.ens_hits)
        if n < 20: return 0.0, None, n
        h = sum(self.ens_hits)
        return max(0.0, _wilson_lb(h, n) - 0.5), h / n, n

    # ── Học: chấm điểm module theo regime lúc nó dự đoán ───────────────────
    def learn(self, predicted, actual):
        if not predicted or not actual: return
        super().learn(predicted, actual)          # cập nhật streak, ens_hits, pred_sides
        if self._ov_side: self.ov_hits.append(1 if self._ov_side == actual else 0)
        rg = self._last_regime
        for name, side in self._last_sig.items():
            self.regime_perf[name][rg][0 if side == actual else 1] += 1

    # ── Dự đoán 3 lượt ────────────────────────────────────────────────────
    def predict(self):
        seq = list(self.seq); sums_h = list(self.sums); dices_h = list(self.dices)
        if len(seq) < 5:
            side = seq[-1] if seq else "TAI"
            self._last_sig = {}; self._last_regime = "INSUFFICIENT"
            return {"side": side, "confidence": 50, "p_tai": 0.5, "reasoning": "Khởi tạo — chưa đủ dữ liệu",
                    "models": [], "loss_streak": self.loss_streak, "run_len": len(seq), "acc30": None,
                    "regime": "INSUFFICIENT"}
        last_v, rlen = _last_run(seq)
        regime = self.detect_regime(seq); self._last_regime = regime
        base = dict(seq=seq, sums_history=sums_h, dices_history=dices_h, loss_streak=self.loss_streak)

        def run(models, extra):
            out = {}
            for m in models:
                try:
                    s = m.predict(**{**base, **extra})
                    if isinstance(s, dict) and s.get("side") in ("TAI", "XIU"):
                        out[m.name] = {"side": s["side"], "conf": float(s.get("conf", 0.5)),
                                       "reason": s.get("reason", ""), "model": m.name}
                except Exception:
                    pass
            return out

        large_plain = [m for m in self.large if m.name not in self.META]
        large_meta  = [m for m in self.large if m.name in self.META]
        # Lượt 1: module lớn thường
        sig1 = run(large_plain, {})
        v1 = [s["side"] for s in sig1.values()]
        # Lượt 2: module phụ thấy vote lượt 1
        sig2 = run(self.support, {"ensemble_votes": v1, "tai_total": v1.count("TAI"), "xiu_total": v1.count("XIU")})
        v12 = v1 + [s["side"] for s in sig2.values()]
        # Lượt 3: meta thấy vote cả hai lượt
        sig3 = run(large_meta, {"ensemble_votes": v12, "all_signals": list(sig1.values()) + list(sig2.values()),
                                "tai_total": v12.count("TAI"), "xiu_total": v12.count("XIU")})
        large_sigs = {**sig1, **sig3}; support_sigs = sig2
        all_sigs = {**large_sigs, **support_sigs}
        self._last_sig = {k: v["side"] for k, v in all_sigs.items()}

        bet_dir = _cont_dir(seq) if (self.CTX_MODE == "DATA" and regime in self.CTX_BET) else 0   # tạm thời, không lưu
        # Phiếu: base = 0.50/N mỗi nhóm (bằng nhau tuyệt đối), × context × perf (đều tạm thời)
        votes = {}
        for group in (large_sigs, support_sigs):
            N = len(group)
            if N == 0: continue
            b = 0.50 / N
            for name, s in group.items():
                w = b * self._context_weight(name, regime, bet_dir) * self._perf_weight(name, regime)
                votes[name] = w if s["side"] == "TAI" else -w
        ov, ov_txt = self._bet_overlay(seq, regime, last_v) if self.OVERLAY else (0.0, "")
        tot = sum(abs(v) for v in votes.values()) + abs(ov); S = sum(votes.values()) + ov

        if tot <= 0 or abs(S) < 1e-12:
            ps = list(self.pred_sides)[-10:]
            pred = "XIU" if ps.count("TAI") > ps.count("XIU") else "TAI" if ps.count("XIU") > ps.count("TAI") else last_v
            margin = 0.0
        else:
            pred = "TAI" if S > 0 else "XIU"; margin = abs(S) / tot

        edge, acc, n = self._edge()
        conf_pct = max(50, min(self.CONF_CAP, 50 + int(round(edge * 100)) + (1 if margin > 0.25 else 0)))
        p_tai = round(0.5 + (conf_pct - 50) / 100 if pred == "TAI" else 0.5 - (conf_pct - 50) / 100, 4)

        top = sorted(votes.items(), key=lambda kv: abs(kv[1]), reverse=True)[:4]
        det = "; ".join(f"[{k}] {all_sigs[k].get('reason','')}" for k, _ in top)
        reasoning = (f"{pred} {conf_pct}% | regime={regime} run={rlen} {ov_txt} "
                     f"TAI={sum(v for v in votes.values() if v > 0):.3f} XIU={-sum(v for v in votes.values() if v < 0):.3f} | {det}")
        acc30 = None
        if len(self.pred_hist) >= 5:
            k = min(30, len(self.pred_hist))
            acc30 = round(sum(1 for i in range(-k, 0) if self.pred_hist[i] == self.result_hist[i]) / k, 3)
        expert_votes = {m.name: 0.0 for m in self.large}
        for nm, s in large_sigs.items():
            if nm in expert_votes: expert_votes[nm] = s["conf"] if s["side"] == "TAI" else 1 - s["conf"]
        self.last_info = {"has_edge": bool(n >= 50 and edge > 0), "ensemble_acc": acc, "n": n}
        nl = max(1, len(large_sigs))
        return {"side": pred, "confidence": conf_pct, "p_tai": p_tai, "reasoning": reasoning,
                "experts": {m.name: round(0.5 / nl, 4) for m in self.large},   # trọng số nền bằng nhau
                "expert_votes": expert_votes, "loss_streak": self.loss_streak, "run_len": rlen,
                "acc30": acc30, "total_signals": len(all_sigs),
                "models_voted_tai": sum(1 for s in all_sigs.values() if s["side"] == "TAI"),
                "models_voted_xiu": sum(1 for s in all_sigs.values() if s["side"] == "XIU"),
                "has_edge": self.last_info["has_edge"], "regime": regime}


class Engine88(Engine87):
    """Engine87 + module bệt nhẹ thích nghi. KHÔNG còn ép bẻ khi bệt; hướng theo/bẻ do dữ liệu quyết định."""
    OVERLAY = True
    CTX_MODE = "OFF"


class Engine88B(Engine87):
    OVERLAY = True
    CTX_MODE = "DATA"


class Engine87D(Engine87):
    """Engine87 với hướng boost bệt lấy từ dữ liệu (CTX_MODE=DATA)."""
    CTX_MODE = "DATA"


# ══════════════════════════════════════════════════════════════════════════
#  ENGINE 89 — Dân chủ tuyệt đối + hệ số ngữ cảnh tạm thời đo từ chính chuỗi + confidence hiệu chỉnh thật
#   • KHÔNG BET_PRESSURE / FORCE_BREAK / HERD_PULL / LOSS_FLIP_BET. Không có dòng nào kiểu "rlen >= X → ép bẻ".
#   • KHÔNG dùng m.w. Nhóm lớn chia đều 0.50/N_large, nhóm phụ chia đều 0.50/N_support (N = số module ĐANG vote).
#   • Hệ số ngữ cảnh (boost/nerf) tính lại mỗi predict() từ chính chuỗi `seq`, KHÔNG lưu state, không ảnh hưởng phiên sau.
#     Hướng boost (theo hay bẻ) KHÔNG định sẵn: do P(giả thuyết regime đúng) đo từ dữ liệu quyết định.
#   • Predict 3 lượt: (1) large thường gồm M23/M24 → (2) support thấy vote lượt 1 → (3) meta thấy cả hai.
#   • Confidence = độ chính xác THỰC ĐO của engine (bảng hiệu chỉnh theo margin + regime, có shrink), trần 78.
#   • Không SKIP: luôn trả TAI hoặc XIU.
# ══════════════════════════════════════════════════════════════════════════
_META89 = tuple(c.name for c in (M05_WeightBalance, M07_WeightEqualize, M13_Performance,
                                 M17_WeightBalance, M20_MaxPerformance, M21_GlobalBalance))


class Engine89(Engine85):
    META = _META89                 # tên thật của 6 module meta (Engine87 ghi nhầm tên M17)
    REG_WIN    = 80                # cửa sổ đuôi dùng để nhận dạng regime
    REL_HORIZON = 300              # số phiên gần nhất dùng để đo độ tin cậy của regime
    REL_DECAY  = 0.985             # decay khi đo độ tin cậy regime
    REL_PRIOR  = 3.0               # prior Bayes cho p(regime đúng)
    CTX_GAIN   = 4.0               # độ khuếch đại hệ số ngữ cảnh (chỉ có tác dụng khi dữ liệu chứng minh được)
    CTX_LO, CTX_HI = 0.05, 8.00    # chặn hệ số, không module nào bị xóa sổ / thổi phồng quá mức
    CAL_MAX    = 400               # số phiên lưu cho bảng hiệu chỉnh
    CAL_K_BASE = 30                # shrink về 0.5 cho accuracy nền
    CAL_K_LOC  = 20                # shrink về accuracy nền cho nhóm margin/regime
    CONF_CAP   = 78                # trần confidence (mỗi phiên ~90% random)

    def __init__(self):
        super().__init__()
        self.calib = deque(maxlen=self.CAL_MAX)     # (margin, regime, hit) — bảng hiệu chỉnh confidence
        self._pend = None                           # (margin, regime) của dự đoán đang chờ kết quả
        self._last_sig = {}

    # ── Regime ────────────────────────────────────────────────────────────
    @staticmethod
    def _regime_info(win, n_total):
        """Phân loại regime từ đuôi chuỗi. Trả (regime, expected_side|None, cur_run, target|None).
        expected_side là GIẢ THUYẾT của regime (nhịp cầu tiếp theo); độ đúng của nó sẽ được đo từ dữ liệu."""
        if n_total < 20 or len(win) < 12:
            return "INSUFFICIENT", None, 0, None
        last, cur = _last_run(win)
        runs = _run_lengths(win)
        done = runs[1:-1] if len(runs) >= 3 else []        # bỏ run đầu bị cắt + run đang chạy

        def nxt(T):                                        # run chưa đủ độ dài mục tiêu → theo, đủ rồi → đảo
            return last if cur < T else _opp(last)

        if len(done) >= 4 and all(d == 1 for d in done[-4:]) and cur == 1:
            return "1_1", nxt(1), cur, 1
        if len(done) >= 2 and done[-1] == done[-2] and 2 <= done[-1] <= 4 and cur <= done[-1]:
            k = done[-1]
            return f"{k}_{k}", nxt(k), cur, k
        if (len(done) >= 4 and done[-4] == done[-2] and done[-3] == done[-1]
                and done[-4] != done[-3] and cur <= done[-2]):
            return "ZIGZAG", nxt(done[-2]), cur, done[-2]    # cầu lặp chu kỳ 2 theo độ dài run (1-2-1-2, 2-3-2-3...)
        # Ngưỡng LONG_BET tự thích nghi: vượt mean+2σ độ dài run thực tế của chuỗi (≈5 khi chuỗi thuần ngẫu nhiên)
        thr = 5
        if len(done) >= 8:
            d = done[-60:]; mu = sum(d) / len(d)
            sd = math.sqrt(sum((x - mu) ** 2 for x in d) / len(d))
            thr = max(4, int(math.ceil(mu + 2 * sd)))
        if cur >= thr: return "LONG_BET", last, cur, None  # giả thuyết: bệt tiếp (đúng hay sai do dữ liệu đo)
        if cur >= 3:   return "BET", last, cur, None
        return "RANDOM", None, cur, None

    def detect_regime(self, seq=None):
        seq = list(self.seq) if seq is None else list(seq)
        return self._regime_info(seq[-self.REG_WIN:], len(seq))[0]

    # ── Đo độ tin cậy của giả thuyết regime từ chính chuỗi (không lưu state) ──
    def _regime_reliability(self, seq, regime, cur):
        """Replay lịch sử: mỗi lần quá khứ rơi đúng (regime, độ dài run hiện tại), giả thuyết regime có đúng không?
        Trả (p, z, n_eff). Chưa có bằng chứng → p≈0.5, z≈0."""
        n = len(seq); key = (regime, min(cur, 6))
        hit = tot = 0.0
        for i in range(max(20, n - self.REL_HORIZON), n - 1):
            win = seq[max(0, i + 1 - self.REG_WIN): i + 1]
            rg, ex, c, _ = self._regime_info(win, i + 1)
            if ex is None or (rg, min(c, 6)) != key: continue
            w = self.REL_DECAY ** (n - 2 - i)
            tot += w
            if seq[i + 1] == ex: hit += w
        a = self.REL_PRIOR
        p = (hit + a) / (tot + 2 * a)
        z = (p - 0.5) / math.sqrt(0.25 / (tot + 2 * a))
        return p, z, tot

    # ── Hệ số ngữ cảnh TẠM THỜI: chỉ sống trong 1 lần predict() ───────────
    def _context_weight(self, side, exp_side, p, z):
        """Module vote cùng giả thuyết regime → ×(1+g·e), ngược giả thuyết → ×(1−g·e),
        e = 2(p−0.5) đo từ dữ liệu, nhân độ mạnh bằng chứng min(1,|z|/2). Chưa có bằng chứng → 1.0."""
        if exp_side is None: return 1.0
        e = (p - 0.5) * 2.0 * min(1.0, abs(z) / 2.0)
        m = 1.0 + self.CTX_GAIN * e if side == exp_side else 1.0 - self.CTX_GAIN * e
        return max(self.CTX_LO, min(self.CTX_HI, m))

    # ── Confidence thật: từ accuracy đo được của chính engine ─────────────
    def _calibrated_confidence(self, margin, regime):
        recs = list(self.calib); n = len(recs)
        if n < 10:
            return 50, 0.5, f"chưa đủ mẫu hiệu chỉnh (n={n})"
        last100 = recs[-100:]
        base = (sum(r[2] for r in last100) + 0.5 * self.CAL_K_BASE) / (len(last100) + self.CAL_K_BASE)
        k = max(15, n // 4)
        near = sorted(recs, key=lambda r: abs(r[0] - margin))[:k]       # các phiên có độ đồng thuận gần giống
        knn = (sum(r[2] for r in near) + self.CAL_K_LOC * base) / (len(near) + self.CAL_K_LOC)
        same = [r for r in recs if r[1] == regime][-60:]                # cùng regime
        reg = (sum(r[2] for r in same) + self.CAL_K_LOC * base) / (len(same) + self.CAL_K_LOC)
        p = base + (knn - base) + (reg - base)
        p = max(0.5, min(self.CONF_CAP / 100.0, p))
        return int(round(p * 100)), p, f"nền={base:.3f} margin~{knn:.3f}(k={len(near)}) regime~{reg:.3f}(n={len(same)})"

    # ── Học ────────────────────────────────────────────────────────────────
    def learn(self, predicted, actual):
        if not predicted or not actual: return
        super().learn(predicted, actual)             # streak, own[], ens_hits, pred_sides
        if self._pend is not None:
            m, rg = self._pend
            self.calib.append((m, rg, 1 if predicted == actual else 0))
            self._pend = None

    # ── Dự đoán 3 lượt ─────────────────────────────────────────────────────
    def predict(self):
        seq = list(self.seq); sums_h = list(self.sums); dices_h = list(self.dices)
        acc30 = None
        if len(self.pred_hist) >= 5:
            k = min(30, len(self.pred_hist))
            acc30 = round(sum(1 for i in range(-k, 0) if self.pred_hist[i] == self.result_hist[i]) / k, 3)
        if len(seq) < 5:
            side = _opp(seq[-1]) if seq else "TAI"
            self._last_sig = {}; self._pend = None
            return {"side": side, "confidence": 50, "p_tai": 0.5, "regime": "INSUFFICIENT",
                    "run_len": len(seq), "reasoning": "Khởi tạo — chưa đủ dữ liệu, chọn tạm",
                    "acc30": acc30, "loss_streak": self.loss_streak, "score_tai": 0.0, "score_xiu": 0.0,
                    "models_voted_tai": 0, "models_voted_xiu": 0, "total_signals": 0}
        last_v, rlen = _last_run(seq)
        regime, exp_side, cur, target = self._regime_info(seq[-self.REG_WIN:], len(seq))
        base = dict(seq=seq, sums_history=sums_h, dices_history=dices_h, loss_streak=self.loss_streak)

        def run(models, extra):
            out = {}
            for m in models:
                try:
                    s = m.predict(**{**base, **extra})
                    if isinstance(s, dict) and s.get("side") in ("TAI", "XIU"):
                        out[m.name] = {"side": s["side"], "conf": float(s.get("conf", 0.5)),
                                       "reason": s.get("reason", ""), "model": m.name}
                except Exception:
                    pass
            return out

        large_plain = [m for m in self.large if m.name not in self.META]       # gồm M23, M24
        large_meta  = [m for m in self.large if m.name in self.META]
        sig1 = run(large_plain, {})                                             # lượt 1: M23/M24 được gọi ở đây
        v1 = [s["side"] for s in sig1.values()]
        sig2 = run(self.support, {"ensemble_votes": v1, "tai_total": v1.count("TAI"), "xiu_total": v1.count("XIU")})
        v12 = v1 + [s["side"] for s in sig2.values()]
        sig3 = run(large_meta, {"ensemble_votes": v12, "all_signals": list(sig1.values()) + list(sig2.values()),
                                "tai_total": v12.count("TAI"), "xiu_total": v12.count("XIU")})
        large_sigs = {**sig1, **sig3}; support_sigs = sig2
        all_sigs = {**large_sigs, **support_sigs}
        self._last_sig = {k: v["side"] for k, v in all_sigs.items()}

        # Độ tin cậy của giả thuyết regime — đo lại từ seq mỗi phiên, bỏ ngay sau khi dùng
        if exp_side is not None:
            p_rg, z_rg, n_rg = self._regime_reliability(seq, regime, cur)
        else:
            p_rg, z_rg, n_rg = 0.5, 0.0, 0.0

        # Phiếu: nền bằng nhau 0.50/N mỗi nhóm × hệ số ngữ cảnh tạm thời
        votes = {}
        for grp in (large_sigs, support_sigs):
            N = len(grp)
            if N == 0: continue
            b = 0.50 / N
            for name, s in grp.items():
                w = b * self._context_weight(s["side"], exp_side, p_rg, z_rg)
                votes[name] = w if s["side"] == "TAI" else -w
        S = sum(votes.values()); tot = sum(abs(v) for v in votes.values())

        if tot <= 0 or abs(S) < 1e-12:                 # hòa tuyệt đối → theo giả thuyết regime đã đo, rồi M24/M23
            if exp_side is not None and p_rg != 0.5:
                pred = exp_side if p_rg > 0.5 else _opp(exp_side)
            elif "M24_MARKOV_DECAY" in sig1: pred = sig1["M24_MARKOV_DECAY"]["side"]
            elif "M23_STREAK_REGIME" in sig1: pred = sig1["M23_STREAK_REGIME"]["side"]
            else: pred = _opp(last_v)
            margin = 0.0
        else:
            pred = "TAI" if S > 0 else "XIU"; margin = abs(S) / tot

        conf, p_win, basis = self._calibrated_confidence(margin, regime)
        self._pend = (margin, regime)
        p_tai = round(p_win if pred == "TAI" else 1.0 - p_win, 4)
        s_tai = sum(v for v in votes.values() if v > 0); s_xiu = -sum(v for v in votes.values() if v < 0)

        top = sorted(votes.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]
        det = "; ".join(f"[{k}] {all_sigs[k].get('reason','')}" for k, _ in top)
        rg_txt = (f"giả thuyết regime→{exp_side} đúng p={p_rg:.2f} z={z_rg:.1f}" if exp_side else "không có giả thuyết")
        reasoning = (f"{pred} {conf}% | regime={regime} run={rlen} {rg_txt} | TAI={s_tai:.3f} XIU={s_xiu:.3f} "
                     f"margin={margin:.2f} | tin cậy: {basis} | {det}")
        expert_votes = {m.name: 0.0 for m in self.large}
        for nm, s in large_sigs.items():
            if nm in expert_votes: expert_votes[nm] = s["conf"] if s["side"] == "TAI" else 1 - s["conf"]
        nl = max(1, len(large_sigs))
        return {"side": pred, "confidence": conf, "p_tai": p_tai, "regime": regime, "run_len": rlen,
                "reasoning": reasoning, "acc30": acc30, "loss_streak": self.loss_streak,
                "score_tai": round(s_tai, 5), "score_xiu": round(s_xiu, 5),
                "margin": round(margin, 4), "regime_expected": exp_side, "regime_p": round(p_rg, 4),
                "experts": {m.name: round(0.5 / nl, 4) for m in self.large},   # trọng số nền bằng nhau
                "expert_votes": expert_votes, "total_signals": len(all_sigs),
                "models_voted_tai": sum(1 for s in all_sigs.values() if s["side"] == "TAI"),
                "models_voted_xiu": sum(1 for s in all_sigs.values() if s["side"] == "XIU"),
                "has_edge": bool(len(self.calib) >= 50 and p_win > 0.5)}


# Chọn engine cho Brain: mặc định giữ Engine88 như cũ; đặt PAW_ENGINE=89 để dùng Engine89
ENGINE_CLS = Engine89 if os.getenv("PAW_ENGINE", "88").strip() == "89" else Engine88


# ══════════════════════════════════════════════════════════════════════════
#  BRAIN ADAPTER — dùng Engine84 làm core
# ══════════════════════════════════════════════════════════════════════════
class Brain:
    """Adapter giữ nguyên hợp đồng app cũ, Engine84 làm engine dự đoán."""
    def __init__(self):
        self.engine = ENGINE_CLS()
        self.history = deque(maxlen=500)
        self.points  = deque(maxlen=500)
        self._seen_ids = set()
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
            "regime": raw.get("regime"),
            "score_tai": raw.get("score_tai"), "score_xiu": raw.get("score_xiu"),
            "total_signals": raw.get("total_signals", 0),
            "evaluation": {
                "n": len(perf),
                "accuracy_30": round(acc,4) if acc is not None else None,
                "random_baseline": 0.5,
                "has_evidence": len(perf) >= 20,
                "edge_significant": bool(raw.get("has_edge")),
                "warning": ("Chưa đủ dữ liệu" if len(perf) < 20 else (None if raw.get("has_edge") else "Chưa có bằng chứng thống kê vượt 50%")),
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
        }
        self._last_prediction = result
        return result

    def learn(self, pk, y: bool):
        if not isinstance(pk, dict) or pk.get("side") not in ("TAI","XIU"): return
        actual = "TAI" if y else "XIU"
        won = pk["side"] == actual
        self.engine.update(pk["side"], actual)
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
        self.err = ""; self.ms = 0; self.n_fetch = 0; self.raw = []

    def load_history(self):
        try:
            with _history_lock:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f: store = json.load(f)
            rows = store.get(self.code, []) if isinstance(store, dict) else []
            if isinstance(rows, list): self.hist = deque([x for x in rows if isinstance(x, dict)][-HIST_MAX:], maxlen=HIST_MAX)
        except (OSError, ValueError, TypeError): self.hist = deque(maxlen=HIST_MAX)

    def save_history(self):
        try:
            with _history_lock:
                try:
                    with open(HISTORY_FILE, "r", encoding="utf-8") as f: store = json.load(f)
                    if not isinstance(store, dict): store = {}
                except (OSError, ValueError, TypeError): store = {}
                store[self.code] = list(self.hist)[-HIST_MAX:]
                tmp = HISTORY_FILE + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(store, f, ensure_ascii=False, separators=(",", ":"))
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp, HISTORY_FILE)
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
            if not self.ready: self.raw = raw_load(self.code)          # lần đầu: nạp dữ liệu thô đã lưu
            merged = merge_rows(self.raw, rows)
            if merged:
                if [r["id"] for r in merged] != [r["id"] for r in self.raw]: raw_save(self.code, merged)
                self.raw = merged; rows = merged
            self.ms = int((time.time() - t0) * 1000); self.err = ""
            self.ok_ts = time.time(); self.n_fetch += 1
            try: self.apply(rows, rebuild)
            except Exception as e:
                import traceback; traceback.print_exc()
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

        for row in (r for r in rows if r["id"] > self.last_id):
            pd = self.pending
            is_live = bool(pd and pd["phien"] == row["id"])
            pk = pd["pk"] if is_live else self.brain.predict()
            du = pk.get("side") if isinstance(pk, dict) else None
            valid_prediction = du in ("TAI", "XIU")
            win = (du == row["result"]) if valid_prediction else None
            if valid_prediction:
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
def index(): return out({"ok": True, "api": "PAW TX v4 + RealBrain V8", "endpoints": ["/tx/hu", "/tx/md5", "/history/tx/hu", "/history/tx/md5", "/admin", "/ping"]})

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
    return {"code": t.code, "name": t.name, "enabled": t.enabled, "ready": t.ready, "err": t.err, "ms": t.ms, "n_fetch": t.n_fetch, "age": round(time.time() - t.ok_ts) if t.ok_ts else None, "last": t.last, "pending": {"phien": pd["phien"], "du_doan": pd["du_doan"], "conf": pd["do_tin_cay"], "p_tai": pd["p_tai"], "evaluation": pk.get("evaluation"), "baseline_side": pk.get("baseline_side"), "temp": pk.get("temp", 1.0), "reasoning": pk.get("reasoning", ""), "loss_streak": pk.get("loss_streak", 0), "run_len": pk.get("run_len", 0), "cau": _cau_number_sequence(t.brain), "acc30": pk.get("acc30"), "regime": pk.get("regime"), "hard_reset": pk.get("nhom", {}).get("hard_reset", False)} if pd else None, "experts": ex, "st_all": stats(hist), "st_live": stats(live), "st_30": stats(l30), "hist": hist[::-1]}

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

LOGIN = """<!doctype html><html lang=vi><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name=theme-color content="#ffffff"><title>PAW TX · Đăng nhập</title><style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#0f1b2d;--mut:#6b7a90;--line:#e6ecf4;--brand:#2f6bff;--brand2:#18c4b8}
body{min-height:100vh;display:grid;place-items:center;padding:22px;background:#fff;color:var(--ink);font:14px/1.55 Inter,-apple-system,Segoe UI,Roboto,system-ui,sans-serif;position:relative;overflow:hidden}
body:before,body:after{content:"";position:fixed;border-radius:50%;filter:blur(70px);opacity:.35;z-index:0}
body:before{width:340px;height:340px;left:-90px;top:-90px;background:#cfe0ff}
body:after{width:300px;height:300px;right:-80px;bottom:-80px;background:#c9f5ef}
.card{position:relative;z-index:1;width:min(400px,100%);padding:34px 30px;border:1px solid var(--line);border-radius:24px;background:#fff;box-shadow:0 24px 60px rgba(32,60,110,.10)}
.mark{width:52px;height:52px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 10px 24px rgba(47,107,255,.28);margin-bottom:18px}
.mark svg{width:26px;height:26px}
.eyebrow{font:700 10px/1 ui-monospace,Menlo,monospace;letter-spacing:.2em;color:var(--brand);margin-bottom:8px}
h1{font-size:26px;letter-spacing:-.03em}
.sub{color:var(--mut);margin:4px 0 22px}
label{display:block;font-size:12px;font-weight:600;color:#44546a;margin:14px 0 6px}
input{width:100%;height:46px;padding:0 14px;border:1.5px solid var(--line);border-radius:12px;font:inherit;color:var(--ink);background:#fbfdff;outline:none;transition:.15s}
input:focus{border-color:var(--brand);box-shadow:0 0 0 4px rgba(47,107,255,.12);background:#fff}
button{width:100%;height:48px;margin-top:22px;border:0;border-radius:13px;font:700 14px inherit;color:#fff;cursor:pointer;background:linear-gradient(135deg,var(--brand),#5a8dff);box-shadow:0 10px 22px rgba(47,107,255,.28);transition:.15s}
button:hover{transform:translateY(-1px);box-shadow:0 14px 28px rgba(47,107,255,.34)}
.err{margin-bottom:6px;padding:10px 13px;border-radius:11px;background:#fff1f2;border:1px solid #ffd5da;color:#c0283d;font-size:13px;font-weight:600}
.foot{margin-top:20px;text-align:center;font:600 10px ui-monospace,Menlo,monospace;letter-spacing:.18em;color:#a3b0c2}
</style></head><body><main class=card><div class=mark><svg viewBox="0 0 40 40" fill=none><path d="M20 4S32 16 32 24a12 12 0 1 1-24 0C8 16 20 4 20 4Z" fill=white /></svg></div><div class=eyebrow>SECURE ADMIN ACCESS</div><h1>PAW TX Admin</h1><div class=sub>Đăng nhập để vào trung tâm điều khiển</div>__ERR__<form method=post action=/admin/login><label>Tài khoản</label><input name=username value=admin autocomplete=username required><label>Mật khẩu</label><input type=password name=password autocomplete=current-password required><button type=submit>Đăng nhập →</button></form><div class=foot>PAW TX CONTROL CENTER</div></main></body></html>"""

PAGE = r"""<!doctype html>
<html lang="vi"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<title>PAW TX · Control Center</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#fff;--soft:#f6f9fd;--soft2:#eef3fa;--line:#e6ecf4;--line2:#d5dfec;--ink:#0f1b2d;--ink2:#33445c;--mut:#6b7a90;--mut2:#9aa8bb;
--tai:#e5484d;--tai-bg:#fff0f1;--xiu:#0a95b8;--xiu-bg:#e9f8fc;--ok:#18a56b;--ok-bg:#e9f9f1;--bad:#e5484d;--brand:#2f6bff;--brand-bg:#edf3ff;--warn:#d98a00;
--r:18px;--sh:0 1px 2px rgba(20,40,80,.04),0 8px 24px rgba(20,40,80,.05)}
html,body{background:#fff}
body{color:var(--ink);font:14px/1.5 Inter,-apple-system,Segoe UI,Roboto,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
button{font:inherit;cursor:pointer}
/* top bar */
.top{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top-in{max-width:1180px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:14px}
.logo{width:36px;height:36px;border-radius:11px;display:grid;place-items:center;background:linear-gradient(135deg,var(--brand),#18c4b8);box-shadow:0 6px 16px rgba(47,107,255,.25)}
.logo svg{width:19px;height:19px}
.brand b{display:block;font-size:15px;letter-spacing:-.02em}.brand small{color:var(--mut);font-size:11px}
.sp{flex:1}
.pill{display:inline-flex;align-items:center;gap:7px;padding:6px 11px;border-radius:99px;background:var(--soft);border:1px solid var(--line);font-size:11px;font-weight:700;color:var(--ink2);letter-spacing:.03em}
.dot{width:8px;height:8px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 3px rgba(24,165,107,.18)}.dot.bad{background:var(--bad);box-shadow:0 0 0 3px rgba(229,72,77,.18)}.dot.off{background:var(--mut2);box-shadow:none}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;height:36px;padding:0 14px;border-radius:10px;border:1px solid var(--line2);background:#fff;color:var(--ink2);font-weight:600;font-size:13px;transition:.15s}
.btn:hover{border-color:var(--brand);color:var(--brand);background:var(--brand-bg)}
.btn.pri{background:var(--brand);border-color:var(--brand);color:#fff}.btn.pri:hover{background:#2358d6;color:#fff}
.btn.dan:hover{border-color:var(--bad);color:var(--bad);background:var(--tai-bg)}
.btn.sm{height:30px;padding:0 10px;font-size:12px;border-radius:8px}
/* layout */
.wrap{max-width:1180px;margin:0 auto;padding:22px 20px 70px}
.tabs{display:flex;gap:8px;margin-bottom:18px;overflow-x:auto}
.tab{display:flex;align-items:center;gap:9px;padding:10px 16px;border-radius:13px;border:1px solid var(--line);background:#fff;font-weight:700;color:var(--mut);white-space:nowrap;transition:.15s}
.tab.on{color:var(--ink);border-color:var(--brand);background:var(--brand-bg);box-shadow:0 4px 14px rgba(47,107,255,.12)}
.grid{display:grid;gap:16px}.g2{grid-template-columns:1.35fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}
@media(max-width:860px){.g2,.g3{grid-template-columns:1fr}.top-in{padding:10px 14px}.wrap{padding:16px 14px 60px}.brand small{display:none}}
.card{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:20px;box-shadow:var(--sh)}
.card h3{font-size:11px;font-weight:800;letter-spacing:.14em;color:var(--mut);text-transform:uppercase;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;gap:10px}
/* hero */
.hero{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center}
.side{font-size:clamp(46px,9vw,74px);font-weight:900;letter-spacing:-.05em;line-height:1}
.side.TAI{color:var(--tai)}.side.XIU{color:var(--xiu)}.side.none{color:var(--mut2)}
.phien{color:var(--mut);font-size:12px;font-weight:600;margin-bottom:6px}
.ring{position:relative;width:118px;height:118px}.ring svg{transform:rotate(-90deg)}
.ring .c{position:absolute;inset:0;display:grid;place-items:center;text-align:center}
.ring b{font-size:26px;letter-spacing:-.04em;display:block;line-height:1}.ring small{font-size:9px;font-weight:800;letter-spacing:.15em;color:var(--mut)}
.split{margin-top:18px}.split .lbl{display:flex;justify-content:space-between;font-size:11px;font-weight:800;margin-bottom:6px}
.bar{height:10px;border-radius:99px;background:var(--xiu-bg);overflow:hidden;display:flex}.bar i{display:block;background:linear-gradient(90deg,#ff7c80,var(--tai));transition:width .5s}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.chip{padding:6px 10px;border-radius:9px;background:var(--soft);border:1px solid var(--line);font-size:11px;color:var(--mut);font-weight:700}.chip b{color:var(--ink);margin-left:5px}
.chip.warn b{color:var(--warn)}.chip.bad b{color:var(--bad)}
.cau{display:flex;gap:5px;flex-wrap:wrap;margin-top:14px}
.cau span{min-width:26px;height:26px;padding:0 7px;border-radius:8px;display:grid;place-items:center;font:800 12px ui-monospace,Menlo,monospace;background:var(--soft2);color:var(--ink2)}
.cau span:last-child{background:var(--ink);color:#fff}
details{margin-top:14px}summary{cursor:pointer;font-size:12px;font-weight:700;color:var(--brand);list-style:none}
details p{margin-top:8px;padding:11px 13px;border-radius:11px;background:var(--soft);border:1px solid var(--line);font-size:12px;color:var(--ink2);line-height:1.6;word-break:break-word}
/* last result */
.dice{display:flex;gap:8px;margin:2px 0 14px}.die{width:46px;height:46px;border-radius:12px;background:#fff;border:1.5px solid var(--line2);display:grid;place-items:center;font-size:34px;line-height:1;color:var(--ink);box-shadow:0 3px 8px rgba(20,40,80,.06)}
.kv{display:grid;grid-template-columns:1fr 1fr;gap:10px}.kv div{padding:11px 12px;border-radius:12px;background:var(--soft);border:1px solid var(--line)}
.kv small{display:block;font-size:10px;font-weight:800;letter-spacing:.12em;color:var(--mut);margin-bottom:3px}.kv b{font-size:17px;letter-spacing:-.02em}
.TAIc{color:var(--tai)}.XIUc{color:var(--xiu)}.win{color:var(--ok)}.lose{color:var(--bad)}
/* stats */
.stat .n{font-size:34px;font-weight:900;letter-spacing:-.04em;line-height:1}.stat .n small{font-size:15px;color:var(--mut)}
.stat .s{margin-top:6px;font-size:12px;color:var(--mut);font-weight:600}
.wl{margin-top:12px;height:8px;border-radius:99px;background:var(--tai-bg);overflow:hidden}.wl i{display:block;height:100%;background:linear-gradient(90deg,#3ccf91,var(--ok));transition:width .5s}
/* chart */
svg.spark{width:100%;height:120px;display:block}
.strip{display:flex;gap:4px;flex-wrap:wrap;margin-top:12px}.strip i{width:14px;height:14px;border-radius:5px;background:var(--ok)}.strip i.l{background:var(--bad)}.strip i.s{background:var(--line2)}
/* experts */
.ex{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:8px}
.exi{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:11px;border:1px solid var(--line);background:#fff;font-size:11px;font-weight:700;color:var(--ink2);min-width:0}
.exi span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}
.exi em{font-style:normal;font:800 10px ui-monospace,Menlo,monospace;padding:3px 7px;border-radius:7px}
.exi em.T{background:var(--tai-bg);color:var(--tai)}.exi em.X{background:var(--xiu-bg);color:var(--xiu)}.exi em.N{background:var(--soft2);color:var(--mut)}
/* table */
.seg{display:inline-flex;padding:3px;border-radius:10px;background:var(--soft2)}.seg button{border:0;background:transparent;padding:5px 11px;border-radius:8px;font-size:11px;font-weight:800;color:var(--mut)}.seg button.on{background:#fff;color:var(--ink);box-shadow:0 1px 4px rgba(20,40,80,.1)}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:13px;max-height:420px;overflow-y:auto}
table{width:100%;border-collapse:collapse;font-size:12.5px}th{position:sticky;top:0;background:var(--soft);text-align:left;padding:10px 12px;font-size:10px;letter-spacing:.12em;color:var(--mut);font-weight:800;text-transform:uppercase;border-bottom:1px solid var(--line)}
td{padding:9px 12px;border-bottom:1px solid var(--soft2);white-space:nowrap}tr:last-child td{border-bottom:0}tr:hover td{background:var(--soft)}
.tag{display:inline-block;padding:2px 9px;border-radius:99px;font-size:10.5px;font-weight:800}.tag.TAI{background:var(--tai-bg);color:var(--tai)}.tag.XIU{background:var(--xiu-bg);color:var(--xiu)}.tag.win{background:var(--ok-bg);color:var(--ok)}.tag.lose{background:var(--tai-bg);color:var(--bad)}.tag.skip{background:var(--soft2);color:var(--mut)}
/* ctrl + prot */
.row{display:flex;gap:8px;flex-wrap:wrap}.health{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:14px}
.health div{padding:9px 11px;border-radius:11px;background:var(--soft);border:1px solid var(--line)}.health small{display:block;font-size:9.5px;font-weight:800;letter-spacing:.12em;color:var(--mut)}.health b{font-size:14px}
.errbox{margin-top:12px;padding:10px 12px;border-radius:11px;background:var(--tai-bg);border:1px solid #ffd5da;color:#b42334;font-size:12px;font-weight:600}
.codebox{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:13px 15px;border-radius:13px;background:var(--soft);border:1px dashed var(--line2);margin-bottom:10px}
.codebox b{font:800 22px ui-monospace,Menlo,monospace;letter-spacing:.2em}
.url{font:600 11px ui-monospace,Menlo,monospace;color:var(--mut);word-break:break-all;margin-bottom:12px}.url b{color:var(--brand)}
.sw{padding:3px 10px;border-radius:99px;font-size:10px;font-weight:900;letter-spacing:.1em}.sw.on{background:var(--ok-bg);color:var(--ok)}.sw.off{background:var(--soft2);color:var(--mut)}
.toast{position:fixed;left:50%;bottom:24px;transform:translate(-50%,30px);opacity:0;padding:11px 18px;border-radius:12px;background:var(--ink);color:#fff;font-weight:600;font-size:13px;box-shadow:0 12px 30px rgba(0,0,0,.2);transition:.25s;z-index:50;max-width:90vw}
.toast.show{opacity:1;transform:translate(-50%,0)}.toast.err{background:#b42334}
.empty{padding:30px;text-align:center;color:var(--mut2);font-weight:600}
.foot{margin-top:34px;text-align:center;font:600 10px ui-monospace,Menlo,monospace;letter-spacing:.18em;color:var(--mut2)}
</style></head><body>
<header class="top"><div class="top-in">
  <div class="logo"><svg viewBox="0 0 40 40" fill="none"><path d="M20 4S32 16 32 24a12 12 0 1 1-24 0C8 16 20 4 20 4Z" fill="#fff"/></svg></div>
  <div class="brand"><b>PAW TX</b><small>Control Center</small></div>
  <div class="sp"></div>
  <span class="pill"><i class="dot" id="apiDot"></i><span id="apiStatus">ĐANG TẢI</span></span>
  <span class="pill mono" title="Tự làm mới">⟳ <span id="countdown">4</span>s</span>
  <a href="/admin/logout" class="btn sm dan" style="text-decoration:none">Thoát</a>
</div></header>
<main class="wrap">
  <div class="tabs" id="tabs"></div>
  <div id="view"><div class="empty">Đang tải dữ liệu…</div></div>
  <section class="card" style="margin-top:16px">
    <h3>Bảo vệ API <span class="sw off" id="protState">TẮT</span></h3>
    <div class="codebox"><b id="codeDisplay">••••••</b><button class="btn sm" onclick="copyCode()">Copy</button></div>
    <div class="url" id="urlPreview">Tạo mã để xem URL</div>
    <div class="row">
      <button class="btn pri sm" onclick="genCode()">Tạo mã mới</button>
      <button class="btn sm" onclick="setProt('enable')">Bật bảo vệ</button>
      <button class="btn sm" onclick="setProt('disable')">Tắt bảo vệ</button>
      <button class="btn sm dan" onclick="revokeCode()">Thu hồi</button>
    </div>
    <div class="url" id="protInfo" style="margin:12px 0 0"></div>
  </section>
  <div class="foot">PAW TX · CONTROL CENTER</div>
</main>
<div class="toast" id="toast"></div>
<script>
const CSRF='__CSRF__';
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let DATA=[],cur=null,filt='all',timer=4,prot={enabled:false,has_code:false,code:''};
const FACE=['⚀','⚁','⚂','⚃','⚄','⚅'];
const nm=s=>s==='TAI'?'TÀI':s==='XIU'?'XỈU':'—';
const pct=v=>v==null?'—':(v*100).toFixed(1)+'%';
function toast(m,ok=true){const t=$('toast');t.textContent=m;t.className='toast show'+(ok?'':' err');clearTimeout(toast._t);toast._t=setTimeout(()=>t.className='toast',2400)}

function ring(conf,side){
  const R=50,C=2*Math.PI*R,p=Math.max(0,Math.min(100,conf||0))/100,col=side==='TAI'?'#e5484d':side==='XIU'?'#0a95b8':'#9aa8bb';
  return `<div class="ring"><svg width="118" height="118" viewBox="0 0 118 118"><circle cx="59" cy="59" r="${R}" fill="none" stroke="#eef3fa" stroke-width="11"/><circle cx="59" cy="59" r="${R}" fill="none" stroke="${col}" stroke-width="11" stroke-linecap="round" stroke-dasharray="${(C*p).toFixed(1)} ${C.toFixed(1)}"/></svg><div class="c"><div><b>${conf==null?'—':conf+'%'}</b><small>TIN CẬY</small></div></div></div>`;
}
function spark(hist){
  const h=hist.slice().reverse().filter(x=>x.trang_thai==='win'||x.trang_thai==='lose');
  if(h.length<6)return '<div class="empty" style="padding:18px">Chưa đủ dữ liệu vẽ biểu đồ</div>';
  const W=600,H=120,w=Math.min(15,h.length>>1),pts=[];
  for(let i=w-1;i<h.length;i++){let s=0;for(let k=i-w+1;k<=i;k++)s+=h[k].trang_thai==='win'?1:0;pts.push(s/w)}
  const x=i=>(i/(pts.length-1||1))*(W-16)+8,y=v=>H-10-v*(H-24);
  const line=pts.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' ');
  return `<svg class="spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#2f6bff" stop-opacity=".22"/><stop offset="1" stop-color="#2f6bff" stop-opacity="0"/></linearGradient></defs><line x1="0" x2="${W}" y1="${y(.5)}" y2="${y(.5)}" stroke="#d5dfec" stroke-dasharray="5 5"/><path d="${line} L${x(pts.length-1)} ${H} L${x(0)} ${H} Z" fill="url(#g)"/><path d="${line}" fill="none" stroke="#2f6bff" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/></svg><div style="display:flex;justify-content:space-between;font-size:10px;color:var(--mut2);font-weight:700;margin-top:4px"><span>Winrate trượt ${w} phiên</span><span>— 50%</span></div>`;
}
function stat(title,s){
  const t=s.win+s.lose,p=t?s.win*100/t:0;
  return `<div class="card stat"><h3>${title}</h3><div class="n">${t?p.toFixed(1):'—'}<small>%</small></div><div class="s">${s.win} thắng · ${s.lose} thua${s.skip?` · ${s.skip} bỏ`:''}</div><div class="wl"><i style="width:${p}%"></i></div></div>`;
}
function view(t){
  const p=t.pending,l=t.last;
  let h='';
  const ptai=p&&p.p_tai!=null?p.p_tai:0.5, taiPct=Math.round(ptai*100);
  const cau=(p&&p.cau&&p.cau!=='—')?p.cau.split('-').map(n=>`<span>${esc(n)}</span>`).join(''):'';
  h+=`<div class="grid g2"><section class="card"><h3>Dự đoán phiên tiếp theo <span class="mono" style="letter-spacing:0">#${p?esc(p.phien):'—'}</span></h3>
    <div class="hero"><div><div class="phien">${esc(t.name)} · phiên ${p?esc(p.phien):'—'}</div><div class="side ${p?p.du_doan:'none'}">${p?nm(p.du_doan):'—'}</div></div>${ring(p?p.conf:null,p?p.du_doan:null)}</div>
    <div class="split"><div class="lbl"><span class="TAIc">TÀI ${taiPct}%</span><span class="XIUc">XỈU ${100-taiPct}%</span></div><div class="bar"><i style="width:${taiPct}%"></i></div></div>
    <div class="chips"><span class="chip">REGIME<b>${esc(p&&p.regime||'—')}</b></span><span class="chip">BỆT<b>${p?p.run_len:0}</b></span><span class="chip ${p&&p.loss_streak>=3?'bad':p&&p.loss_streak>=2?'warn':''}">THUA LIÊN TIẾP<b>${p?p.loss_streak:0}</b></span><span class="chip">ACC30<b>${p&&p.acc30!=null?pct(p.acc30):'—'}</b></span></div>
    ${cau?`<div class="cau">${cau}</div>`:''}
    ${p&&p.reasoning?`<details><summary>Xem lý do dự đoán</summary><p>${esc(p.reasoning)}</p></details>`:''}
  </section>
  <section class="card"><h3>Kết quả phiên trước <span class="mono" style="letter-spacing:0">#${l?esc(l.phien):'—'}</span></h3>
    ${l?`<div class="dice">${(l.xuc_xac||[]).map(d=>`<div class="die">${FACE[d-1]||d}</div>`).join('')}</div>
    <div class="kv"><div><small>TỔNG</small><b>${esc(l.tong)}</b></div><div><small>KẾT QUẢ</small><b class="${l.ket_qua}c">${nm(l.ket_qua)}</b></div><div><small>ĐÃ DỰ ĐOÁN</small><b>${l.du_doan?nm(l.du_doan):'—'}</b></div><div><small>TRẠNG THÁI</small><b class="${l.trang_thai}">${l.trang_thai==='win'?'THẮNG':l.trang_thai==='lose'?'THUA':'—'}</b></div></div>`:'<div class="empty">Chưa có dữ liệu</div>'}
  </section></div>`;
  h+=`<div class="grid g3" style="margin-top:16px">${stat('Tất cả',t.st_all)}${stat('Live',t.st_live)}${stat('30 phiên gần nhất',t.st_30)}</div>`;
  const last40=t.hist.slice(0,40).reverse();
  h+=`<section class="card" style="margin-top:16px"><h3>Xu hướng độ chính xác</h3>${spark(t.hist)}<div class="strip">${last40.map(x=>`<i class="${x.trang_thai==='win'?'':x.trang_thai==='lose'?'l':'s'}" title="#${esc(x.phien)}"></i>`).join('')}</div></section>`;
  h+=`<div class="grid g2" style="margin-top:16px;grid-template-columns:1fr 1fr">
  <section class="card"><h3>Điều khiển bàn</h3>
    <div class="health"><div><small>TRẠNG THÁI</small><b>${t.enabled?(t.ready?'Đang chạy':'Đang khởi tạo'):'Đã tắt'}</b></div><div><small>ĐỘ TRỄ NGUỒN</small><b>${t.ms||0} ms</b></div><div><small>CẬP NHẬT CÁCH ĐÂY</small><b>${t.age==null?'—':t.age+' s'}</b></div><div><small>SỐ LẦN LẤY</small><b>${t.n_fetch}</b></div></div>
    <div class="row"><button class="btn pri sm" onclick="act('${t.code}','refresh')">Làm mới</button><button class="btn sm" onclick="act('${t.code}','relearn')">Học lại</button><button class="btn sm ${t.enabled?'dan':''}" onclick="act('${t.code}','${t.enabled?'off':'on'}')">${t.enabled?'Tắt bàn':'Bật bàn'}</button></div>
    ${t.err?`<div class="errbox">⚠ ${esc(t.err)}</div>`:''}
  </section>
  <section class="card"><h3>Phiếu của ${t.experts.length} module lớn</h3>${t.experts.length?`<div class="ex">${t.experts.map(e=>{const v=e.p,c=v>0.505?'T':v<0.495?'X':'N';return `<div class="exi"><span title="${esc(e.name)}">${esc(e.name.replace(/^M\d+_/,'M'+(e.name.match(/^M(\d+)/)||[0,''])[1]+' '))}</span><em class="${c}">${c==='T'?'TÀI':c==='X'?'XỈU':'—'}</em></div>`}).join('')}</div>`:'<div class="empty">Chưa có phiếu</div>'}</section></div>`;
  const rows=t.hist.filter(x=>filt==='all'||(filt==='live'&&x.live)||(filt==='win'&&x.trang_thai==='win')||(filt==='lose'&&x.trang_thai==='lose')).slice(0,60);
  h+=`<section class="card" style="margin-top:16px"><h3>Lịch sử dự đoán <span class="seg">${[['all','Tất cả'],['live','Live'],['win','Thắng'],['lose','Thua']].map(([k,v])=>`<button class="${filt===k?'on':''}" onclick="setFilt('${k}')">${v}</button>`).join('')}</span></h3>
  ${rows.length?`<div class="tw"><table><thead><tr><th>Phiên</th><th>Dự đoán</th><th>Kết quả</th><th>Xúc xắc</th><th>Tổng</th><th>Tin cậy</th><th>Trạng thái</th></tr></thead><tbody>${rows.map(x=>`<tr><td class="mono">#${esc(x.phien)}${x.live?' <span style="color:var(--ok)">●</span>':''}</td><td><span class="tag ${x.du_doan}">${nm(x.du_doan)}</span></td><td><span class="tag ${x.ket_qua}">${nm(x.ket_qua)}</span></td><td class="mono">${(x.xuc_xac||[]).join('·')||'—'}</td><td class="mono">${esc(x.tong)}</td><td class="mono">${x.conf!=null?x.conf+'%':'—'}</td><td><span class="tag ${x.trang_thai}">${x.trang_thai==='win'?'THẮNG':x.trang_thai==='lose'?'THUA':'BỎ'}</span></td></tr>`).join('')}</tbody></table></div>`:'<div class="empty">Không có dòng nào</div>'}</section>`;
  return h;
}
function draw(){
  if(!DATA.length)return;
  if(!cur||!DATA.find(t=>t.code===cur))cur=DATA[0].code;
  $('tabs').innerHTML=DATA.map(t=>`<button class="tab ${t.code===cur?'on':''}" onclick="pick('${t.code}')"><i class="dot ${!t.enabled?'off':t.err?'bad':''}"></i>${esc(t.name)}</button>`).join('');
  $('view').innerHTML=view(DATA.find(t=>t.code===cur));
  const ok=DATA.every(t=>!t.enabled||(t.ready&&!t.err));
  $('apiStatus').textContent=ok?'API ONLINE':'ĐANG LỖI NGUỒN';$('apiDot').className='dot'+(ok?'':' bad');
}
function pick(c){cur=c;draw()}
function setFilt(f){filt=f;draw()}
async function load(){
  try{
    const r=await fetch('/admin/data',{cache:'no-store'});
    if(r.status===401){location.href='/admin';return}
    const j=await r.json();if(!j.ok)throw Error(j.loi||'API error');
    DATA=j.tables||[];draw();timer=4;
  }catch(e){$('apiStatus').textContent='LỖI KẾT NỐI';$('apiDot').className='dot bad';toast('Lỗi: '+e.message,false)}
}
async function act(c,a){
  try{const r=await fetch(`/admin/act/${c}/${a}`,{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();toast(j.ok?'Đã thực hiện: '+a:'Lỗi: '+(j.loi||''),j.ok);load()}
  catch(e){toast('Lỗi mạng',false)}
}
async function loadProt(){
  try{
    const r=await fetch('/admin/aprot/status',{headers:{'X-CSRF-Token':CSRF}});const j=await r.json();
    prot={...prot,enabled:j.enabled,has_code:j.has_code};
    const st=$('protState');st.textContent=j.enabled?'BẬT':'TẮT';st.className='sw '+(j.enabled?'on':'off');
    $('protInfo').textContent=`Bảo vệ: ${j.enabled?'BẬT':'TẮT'} · ${j.has_code?'Đã có mã':'Chưa có mã'}`;
    if(!prot.code&&j.has_code)$('codeDisplay').textContent='••••••';
  }catch(e){$('protInfo').textContent='Lỗi tải trạng thái'}
}
async function genCode(){
  try{const r=await fetch('/admin/aprot/gen',{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();if(!j.ok)throw Error(j.loi);
    prot.code=j.code;prot.has_code=true;$('codeDisplay').textContent=j.code;
    $('urlPreview').innerHTML=`<b>${esc(location.origin)}/${esc(j.code)}/tx/hu</b>`;toast('Đã tạo mã: '+j.code);loadProt()}
  catch(e){toast('Tạo mã thất bại',false)}
}
async function setProt(action){
  if(action==='enable'&&!prot.has_code){toast('Hãy tạo mã trước',false);return}
  try{const fd=new FormData();fd.append('action',action);
    const r=await fetch('/admin/aprot/set',{method:'POST',headers:{'X-CSRF-Token':CSRF},body:fd});const j=await r.json();if(!j.ok)throw Error(j.loi);
    toast(action==='enable'?'Đã bật bảo vệ':'Đã tắt bảo vệ');loadProt()}
  catch(e){toast('Không cập nhật được',false)}
}
async function revokeCode(){
  if(!confirm('Thu hồi mã sẽ TẮT bảo vệ. Tiếp tục?'))return;
  try{const r=await fetch('/admin/aprot/revoke',{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();if(!j.ok)throw Error(j.loi);
    prot={enabled:false,has_code:false,code:''};$('codeDisplay').textContent='••••••';$('urlPreview').textContent='Tạo mã để xem URL';toast('Đã thu hồi mã');loadProt()}
  catch(e){toast('Thu hồi thất bại',false)}
}
function copyCode(){
  if(!prot.code){toast('Chưa có mã (mã chỉ hiện ngay lúc tạo)',false);return}
  navigator.clipboard?.writeText(prot.code).then(()=>toast('Đã copy: '+prot.code)).catch(()=>toast('Clipboard lỗi',false))
}
setInterval(()=>{timer=Math.max(0,timer-1);$('countdown').textContent=timer;if(timer===0){load();timer=4}},1000);
load();loadProt();
</script></body></html>"""


@app.route("/admin/login", methods=["POST"])
def admin_login():
    ip = request.remote_addr or "?"; now = time.time()
    for k in [k for k, v in _fails.items() if not [x for x in v if now - x < 300]]: _fails.pop(k, None)   # dọn IP cũ, tránh phình bộ nhớ
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
        import html as _html
        err_html = f'<div class=err>{_html.escape(e)}</div>' if e else ""
        html = LOGIN.replace("__ERR__", err_html)
        r = make_response(html); r.headers["Content-Type"] = "text/html; charset=utf-8"; return r
    r = make_response(PAGE.replace("__CSRF__", session.get("csrf", "")))
    r.headers["Content-Type"] = "text/html; charset=utf-8"; return r

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
