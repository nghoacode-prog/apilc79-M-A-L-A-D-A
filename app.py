# -*- coding: utf-8 -*-
"""
PAW TX API v6 — PRO EDITION (Gói + Đơn hàng + Key SLL + Devices)
════════════════════════════════════════════════════════════════════════════════
• API dự đoán (Hũ + MD5) chỉ dùng được SAU khi kích hoạt key tại /makey
• Hệ thống GÓI (ngày/tuần/tháng...), ĐƠN HÀNG, tạo key SLL có đơn hàng đẹp
• Mỗi key gắn thiết bị (device) khi kích hoạt — admin xem info đầy đủ
• Render free: /tmp + backup cloud Gist (GIST_TOKEN + GIST_ID) → không mất key
• Engine 84 model + tầng phân tích cầu NGẮN / TRUNG / DÀI + bộ ổn định dài hạn
"""
import hmac, json, math, os, secrets, threading, time, uuid
from collections import deque, Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict

import requests
from flask import Flask, jsonify, make_response, redirect, request, session
from werkzeug.exceptions import HTTPException

URLS  = {"hu":  os.getenv("API_URL_HU",  "https://wtx.tele68.com/v1/tx/sessions"),
         "md5": os.getenv("API_URL_MD5", "https://wtxmd52.tele68.com/v1/txmd5/sessions")}
NAMES = {"hu": "Hũ", "md5": "MD5"}

HIST_MAX  = 50
POLL_SEC  = 4
MIN_GAP   = 3
STALE_SEC = 8

ICON       = {"win": "✅", "lose": "❌", "cho": "⏳", "skip": "⏸️"}
VN         = timezone(timedelta(hours=7))
STATE_FILE   = os.getenv("STATE_FILE",   "/tmp/paw_tx_toggles.json")
CFG_FILE     = os.getenv("CFG_FILE",     "/tmp/paw_tx_cfg.json")
HISTORY_FILE = os.getenv("HISTORY_FILE", "/tmp/paw_tx_history.json")
STORE_FILE   = os.getenv("STORE_FILE",   "/tmp/paw_tx_store.json")
BASE_URL       = os.getenv("BASE_URL", "https://apilc79-m-a-l-a-d-a.onrender.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
if not ADMIN_PASSWORD:
    # Không cho mật khẩu cứng! Nếu chưa set env → tự sinh ngẫu nhiên mỗi lần deploy,
    # in ra Render Logs (chỉ chủ server thấy). Set ADMIN_PASSWORD trên Render để cố định.
    ADMIN_PASSWORD = secrets.token_urlsafe(9)
    print("════════════════════════════════════════════════════", flush=True)
    print(" MẬT KHẨU ADMIN LẦN CHẠY NÀY: %s" % ADMIN_PASSWORD, flush=True)
    print(" (Set env ADMIN_PASSWORD trên Render để tự đặt mật khẩu cố định)", flush=True)
    print("════════════════════════════════════════════════════", flush=True)
ADMIN_KEY_PREFIX = os.getenv("ADMIN_API_PREFIX", "VT")

_history_lock = threading.Lock()

# ═══════════════════════════════════════════════════════════════════════════════
#  STORE v2: keys + packages + orders + settings  (JSON + Gist backup)
# ═══════════════════════════════════════════════════════════════════════════════
GIST_TOKEN = os.getenv("GIST_TOKEN", "")
GIST_ID    = os.getenv("GIST_ID",    "")
_store_lock = threading.Lock()
_backup_dirty = {"at": 0.0}

def _empty_store():
    return {"keys": {}, "packages": {}, "orders": {}, "settings": {}, "admin_key": "",
            "meta": {"created": now_iso()}}

def _load_store():
    try:
        d = json.load(open(STORE_FILE, encoding="utf-8"))
        if isinstance(d, dict) and "keys" in d:
            d.setdefault("packages", {}); d.setdefault("orders", {}); d.setdefault("settings", {})
            return d
    except Exception: pass
    if GIST_TOKEN and GIST_ID:
        try:
            r = requests.get(f"https://api.github.com/gists/{GIST_ID}",
                             headers={"Authorization": f"token {GIST_TOKEN}"}, timeout=(3, 8))
            raw = (r.json().get("files") or {}).get("paw_tx_store.json", {}).get("content")
            if raw:
                d = json.loads(raw)
                if isinstance(d, dict) and "keys" in d:
                    d.setdefault("packages", {}); d.setdefault("orders", {}); d.setdefault("settings", {})
                    json.dump(d, open(STORE_FILE, "w", encoding="utf-8"))
                    return d
        except Exception: pass
    return _empty_store()

def _gist_push(payload):
    if not (GIST_TOKEN and GIST_ID): return
    try:
        requests.patch(f"https://api.github.com/gists/{GIST_ID}",
                       headers={"Authorization": f"token {GIST_TOKEN}",
                                "Accept": "application/vnd.github+json"},
                       json={"files": {"paw_tx_store.json": {"content":
                             json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}}},
                       timeout=(3, 8))
    except Exception: pass

def _backup_loop():
    while True:
        time.sleep(20)
        if _backup_dirty["at"] and time.time() - _backup_dirty["at"] >= 10:
            _backup_dirty["at"] = 0.0
            try:
                with _store_lock:
                    snap = json.load(open(STORE_FILE, encoding="utf-8"))
                _gist_push(snap)
            except Exception: pass

def save_store(store=None):
    with _store_lock:
        tmp = STORE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(STORE, f, ensure_ascii=False, separators=(",", ":"))
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, STORE_FILE)
    _backup_dirty["at"] = time.time()

def now_iso(): return datetime.now(VN).replace(microsecond=0).isoformat()

STORE = _load_store()

def _gen_key(prefix="PAXU"):
    alpha = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    blk = lambda: "".join(secrets.choice(alpha) for _ in range(4))
    return f"{prefix.upper()}-{blk()}-{blk()}-{blk()}"

KEY_ALPHA = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def _dur_text(sec):
    """3600*30 -> '1 ngày 6 giờ'. None/0 -> vĩnh viễn."""
    if not sec: return "Vĩnh viễn ♾️"
    d, rem = divmod(int(sec), 86400); h = rem // 3600
    parts = ([f"{d} ngày"] if d else []) + ([f"{h} giờ"] if h else [])
    return " ".join(parts) or "dưới 1 giờ"

def _key_dur_sec(k):
    """Thời hạn (giây) của key; None = vĩnh viễn. Key cũ chỉ có duration_days vẫn chạy."""
    if "duration_sec" in k:
        v = k["duration_sec"]
        return int(v) if v else None      # None/0 = vĩnh viễn
    d = k.get("duration_days")
    return int(d) * 86400 if d else None

def _pkg_sec(p):
    return (int(p.get("days") or 0) * 86400 + int(p.get("hours") or 0) * 3600) or None

def _to_int(v, default=0):
    try: return max(0, int(float(str(v).strip())))
    except Exception: return default

def _new_key(kid, prefix, pk, name, note, order_id=""):
    now = time.time()
    return {"id": kid, "key": kid, "name": name, "role": "key", "status": "active",
            "package_id": pk["id"] if pk else "", "price": pk["price"] if pk else "",
            "duration_days": pk["days"] if pk else None,
            "created_at": now_iso(), "expires_ts": None, "expires_at": None,
            "max_devices": 1, "activated": False, "activated_at": None,
            "token": None, "note": note, "order_id": order_id,
            "devices": {}, "calls_hu": 0, "calls_md5": 0, "last_call": None}

def _device_info(k, tok):
    return k.get("devices", {}).get(tok, {})

def key_status(k):
    exp = k.get("expires_ts")
    if k.get("status") == "banned": return "khóa"
    if exp and time.time() > exp: return "hết hạn"
    if not k.get("activated"): return "chưa kích hoạt"
    return "hoạt động"

def key_is_usable(k):
    if not k: return (False, "key không tồn tại")
    st = key_status(k)
    if st == "khóa": return (False, "key đã bị khóa")
    if st == "hết hạn": return (False, "key đã hết hạn — liên hệ admin gia hạn")
    if k.get("role") != "admin" and st == "chưa kích hoạt":
        return (False, "key chưa kích hoạt — vào " + BASE_URL + "/makey")
    return (True, "")

def touch_call(k, tok, table):
    if k.get("role") == "admin": return
    f = "calls_hu" if table == "hu" else "calls_md5"
    k[f] = int(k.get(f, 0)) + 1
    k["last_call"] = now_iso()
    dev = k.setdefault("devices", {}).get(tok)
    if dev:
        dev["calls_hu" if table == "hu" else "calls_md5"] = int(dev.get("calls_hu" if table == "hu" else "calls_md5", 0)) + 1
        dev["last_call"] = now_iso()

def _key_public(k):
    devs = [{"ten_thiet_bi": d.get("name", "Thiết bị") + " " + str(i + 1), "kich_hoat": d.get("activated_at"),
             "lan_cuoi_goi": d.get("last_call"), "luot_goi_hu": d.get("calls_hu", 0),
             "luot_goi_md5": d.get("calls_md5", 0), "mo_ta": d.get("ua", "")}
            for i, d in enumerate((k.get("devices") or {}).values())]
    pk = STORE["packages"].get(k.get("package_id") or "", {})
    return {"id": k["id"], "key": k["key"], "ten": k.get("name", ""),
            "trang_thai": key_status(k), "gia": k.get("price", ""),
            "goi": k.get("package_name") or (pk.get("name", "") if pk else ""),
            "thoi_han": _dur_text(_key_dur_sec(k)), "thoi_han_giay": _key_dur_sec(k),
            "han_bao_nhieu_ngay": k.get("duration_days"),
            "ngay_tao": k.get("created_at"), "ngay_het_han": k.get("expires_at"),
            "da_kich_hoat": bool(k.get("activated")), "ngay_kich_hoat": k.get("activated_at"),
            "gioi_han_thiet_bi": k.get("max_devices", 1), "thiet_bi": devs,
            "luot_goi_hu": k.get("calls_hu", 0), "luot_goi_md5": k.get("calls_md5", 0),
            "don_hang": k.get("order_id", ""), "ghi_chu": k.get("note", ""),
            "loai": k.get("role", "key")}

def get_key_by_key(key): return STORE["keys"].get(key)
def get_key_by_token(tok):
    if not tok: return None
    for k in STORE["keys"].values():
        if k.get("token") == tok and tok: return k
    return None

def device_check(k, tok, device_id):
    """BẮT BUỘC: request gọi API dự đoán phải kèm X-Device-ID đúng
    với thiết bị đã bind lúc kích hoạt. Không cho header rỗng vượt qua.
    Trả (True, "") nếu hợp lệ, ngược lại (False, lý do)."""
    if k.get("role") == "admin":
        return True, ""
    device_id = (device_id or "").strip()
    if not device_id:
        return False, "thiếu X-Device-ID — key đã gắn thiết bị, phải gửi đúng mã thiết bị"
    devs = k.get("devices") or {}
    dev = devs.get(tok)
    if not dev:
        return False, "key chưa gắn thiết bị — kích hoạt tại /makey trước"
    bound = dev.get("device_id")
    if not bound:
        # Thiet bi cu (truoc khi co co che nay) chua co device_id ->
        # BAT BUOC phai gan ngay lan goi dau, khong cho qua tu do mai mai
        dev["device_id"] = device_id
        return True, ""
    if bound != device_id:
        return False, "sai thiết bị — key này đã gắn thiết bị khác"
    return True, ""

# ═══════════════════════════════════════════════════════════════════════════════
#  APP CORE
# ═══════════════════════════════════════════════════════════════════════════════
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  PERMANENT_SESSION_LIFETIME=timedelta(hours=10))
app.json.ensure_ascii = False
app.json.sort_keys    = False

@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-Requested-With, X-Device-ID"
    resp.headers["Access-Control-Max-Age"]        = "86400"
    if not request.path.startswith("/admin"):
        resp.headers["Cache-Control"] = "no-store"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp

@app.errorhandler(Exception)
def on_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    msg  = e.description if isinstance(e, HTTPException) else "Lỗi máy chủ"
    return out({"ok": False, "loi": "http_%d" % code, "thong_bao": msg}, code)

def out(payload, status=200):
    compact = str(request.args.get("compact", "")) == "1"
    r = make_response(json.dumps(payload, ensure_ascii=False,
                                 indent=(0 if compact else 2),
                                 separators=((",", ":") if compact else None)), status)
    r.headers["Content-Type"] = "application/json; charset=utf-8"
    return r

_http = requests.Session()
_http.headers.update({"User-Agent": "Mozilla/5.0 (PAW-TX/6)", "Accept": "application/json"})

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
    """S8 FIXED: Xác suất gãy khi streak đang ở độ dài run_len.
    Scan mỗi vị trí i, khi run_at[i]==run_len xem i+1 là gãy hay tiếp.
    Bug cũ: đếm mọi lần streak kết thúc → luôn = 1.0 (vì kết thúc = gãy).
    """
    if len(seq) < 15: return 0.5
    # run_at[i] = độ dài run TẠI vị trí i
    run_at = [1] * len(seq)
    for i in range(1, len(seq)):
        run_at[i] = run_at[i-1] + 1 if seq[i] == seq[i-1] else 1
    brk = cont = 0
    for i in range(len(seq) - 1):
        if run_at[i] == run_len:
            if seq[i+1] != seq[i]: brk += 1
            else: cont += 1
    total = brk + cont
    if total < 3:
        # Chưa đủ mẫu → prior nhẹ: bệt dài hơn thì hơi nghiêng bẻ
        return min(0.62, 0.50 + (run_len - 1) * 0.02)
    return (brk + 1.0) / (total + 2.0)  # Laplace smoothing

def sub_run_pattern_equal(seq: list, n_runs: int = 3) -> int:
    """Phát hiện cầu đều: n run liên tiếp cùng độ dài. Trả độ dài chung hoặc 0."""
    runs = _run_lengths(seq)
    if len(runs) < n_runs: return 0
    last_n = runs[-n_runs:]
    return last_n[0] if len(set(last_n)) == 1 and last_n[0] >= 1 else 0

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
        # Bệt dài: hỏi lịch sử thực, không hardcode bẻ
        if cau == "BET_DAI":
            p_brk = sub_break_prob_historical(seq, rlen)
            conf = _clamp(0.52 + abs(p_brk - 0.5) * 1.5, 0.52, 0.70)
            if p_brk >= 0.50:
                return {"side": _opp(last), "conf": conf,
                        "reason": f"M01: BET_DAI run={rlen} p_brk={p_brk:.2f}→bẻ"}
            else:
                return {"side": last, "conf": conf,
                        "reason": f"M01: BET_DAI run={rlen} p_cont={1-p_brk:.2f}→theo"}
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
        # Cầu dài >= 5 → hỏi data, không hardcode bẻ
        if rlen >= 5:
            conf = _clamp(0.52 + abs(brk_p - 0.5) * 1.4, 0.52, 0.70)
            pred = _opp(last) if brk_p >= 0.50 else last
            return {"side": pred, "conf": conf, "reason": f"M06: Run={rlen} p_brk={brk_p:.2f}→{'bẻ' if brk_p>=0.5 else 'theo'}"}
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
        # BỆT ADJUSTER v5+ — 3 tầng data-driven
        #
        # Tầng 1 — Specific: p_brk tại ĐÚNG rlen (cần ≥5 mẫu)
        # Tầng 2 — General:  p_brk pool run ≥ rlen  (cần ≥5 mẫu)
        # Tầng 3 — Prior:    thống kê chung bệt dài hay gãy hơn
        #
        # → Có điểm bẻ tự nhiên khi bệt dài mà không FORCE cứng
        # → Khi lịch sử bệt hay TIẾP → nudge theo thay vì bẻ oan
        # → Không LOSS_FLIP — thua liên tiếp chỉ shrink confidence
        # ══════════════════════════════════════════════════════════════
        bet_override_reason = ""
        if rlen >= 2 and total_w > 0 and len(seq) >= 20:
            # Tính run_at[i] = độ dài run tại vị trí i
            _ra = [1] * len(seq)
            for _i in range(1, len(seq)):
                _ra[_i] = _ra[_i-1] + 1 if seq[_i] == seq[_i-1] else 1

            # Tầng 1: đếm tại đúng run_len == rlen
            _b1 = _c1 = 0
            for _i in range(len(seq) - 1):
                if _ra[_i] == rlen:
                    if seq[_i+1] != seq[_i]: _b1 += 1
                    else: _c1 += 1
            _n1 = _b1 + _c1

            if _n1 >= 5:
                _p = (_b1 + 1.0) / (_n1 + 2.0)
                _src = f"T1 n={_n1}"
            else:
                # Tầng 2: pool run >= rlen
                _b2 = _c2 = 0
                for _i in range(len(seq) - 1):
                    if _ra[_i] >= rlen:
                        if seq[_i+1] != seq[_i]: _b2 += 1
                        else: _c2 += 1
                _n2 = _b2 + _c2
                if _n2 >= 5:
                    _p = (_b2 + 1.0) / (_n2 + 2.0)
                    _src = f"T2 n={_n2}"
                else:
                    # Tầng 3: prior — bệt dài thống kê hay gãy hơn
                    # run=2→0.52, 3→0.55, 4→0.58, 5→0.61, 6→0.64, 7→0.66
                    _p = min(0.68, 0.49 + (rlen - 1) * 0.03)
                    _src = f"T3 prior"

            _dev = abs(_p - 0.5)
            # Strength tỉ lệ deviation, cap 0.26 để không override toàn bộ ensemble
            _strength = min(0.26, _dev * 2.0)
            _adj = _strength * total_w

            if _p > 0.54:  # Lịch sử nghiêng bẻ
                _be = _opp(last_v)
                if _be == "TAI": score_tai += _adj; score_xiu -= _adj * 0.4
                else:            score_xiu += _adj; score_tai -= _adj * 0.4
                bet_override_reason = f"BRK[{_src}] run={rlen} p={_p:.2f} s={_strength:.2f}"
            elif _p < 0.46:  # Lịch sử nghiêng theo
                if last_v == "TAI": score_tai += _adj; score_xiu -= _adj * 0.4
                else:               score_xiu += _adj; score_tai -= _adj * 0.4
                bet_override_reason = f"CONT[{_src}] run={rlen} p_c={1-_p:.2f} s={_strength:.2f}"
            else:
                bet_override_reason = f"NEU[{_src}] run={rlen} p={_p:.2f}"

            # Cầu đều đang đúng nhịp → giảm áp bẻ
            _eq = sub_run_pattern_equal(seq, 3)
            if _eq and rlen == _eq and _eq <= 3:
                _mid = (score_tai + score_xiu) / 2
                score_tai = score_tai * 0.88 + _mid * 0.12
                score_xiu = score_xiu * 0.88 + _mid * 0.12
                bet_override_reason += f" | DEU-{_eq} hạ áp"

        # Thua liên tiếp → chỉ shrink confidence, KHÔNG đảo chiều cứng
        if self.loss_streak >= 3 and total_w > 0:
            _sh = min(0.18, (self.loss_streak - 2) * 0.04)
            _mid = (score_tai + score_xiu) / 2
            score_tai = score_tai * (1 - _sh) + _mid * _sh
            score_xiu = score_xiu * (1 - _sh) + _mid * _sh
            bet_override_reason += f" | SHR={_sh:.2f}"

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

    def update(self, pred_side: str, actual_side: str, pk=None):
        self.learn(pred_side, actual_side)


# ══════════════════════════════════════════════════════════════════════════
#  REGIME ENGINE — đọc nhịp cầu (BỆT / ĐẢO / LẪN), tự đổi chiến lược khi cầu đổi
#  Engine84 giờ chỉ là 1 chuyên gia trong bộ; mỗi chuyên gia được chấm điểm
#  walk-forward trên phiên thật, trọng số = kỹ năng gần đây (8 phiên nhanh + 30 phiên chậm).
#  Chuyên gia nào đang sai liên tục thì trọng số về 0 → tự bỏ cầu cũ, theo cầu mới.
# ══════════════════════════════════════════════════════════════════════════
def _logit(p):
    p = max(0.02, min(0.98, p))
    return math.log(p / (1.0 - p))

class RegimeEngine(Engine84):
    EXPERTS = ("HAZARD", "RUNMIRROR", "MOMENTUM", "CTX", "ENGINE84")
    DECAY = 0.985          # phiên càng cũ càng ít trọng lượng (bảng đếm tự quên cầu cũ)

    def __init__(self):
        super().__init__()
        self.ehits = {n: deque(maxlen=60) for n in self.EXPERTS}

    def _scan(self, seq):
        """Một lượt quét: hazard theo độ dài bệt, bảng (bệt hiện tại, bệt trước), ngữ cảnh bậc 2-4."""
        n = len(seq)
        haz = defaultdict(lambda: [0.0, 0.0])      # r -> [theo, gãy]
        mir = defaultdict(lambda: [0.0, 0.0])      # (r, prev) -> [theo, gãy]
        ctx = {k: defaultdict(lambda: [0.0, 0.0]) for k in (2, 3, 4)}   # pattern -> [TAI, XIU]
        r, prev = 1, 0
        for t in range(1, n):
            w = self.DECAY ** (n - 1 - t)
            follow = seq[t] == seq[t - 1]
            i = 0 if follow else 1
            haz[min(r, 8)][i] += w
            mir[(min(r, 4), min(prev, 4))][i] += w
            for k in (2, 3, 4):
                if t >= k:
                    ctx[k][tuple(seq[t - k:t])][0 if seq[t] == "TAI" else 1] += w
            if follow: r += 1
            else: prev, r = r, 1
        return haz, mir, ctx, prev

    def _experts(self, seq, last, rlen):
        haz, mir, ctx, prev = self._scan(seq)
        pt = lambda pf: pf if last == "TAI" else 1.0 - pf      # p_theo -> p_tai
        out = {}
        # 1) HAZARD: với độ dài bệt hiện tại, lịch sử gần đây hay GÃY hay hay TIẾP?
        f, b = haz[min(rlen, 8)]
        pf = (f + 1.0) / (f + b + 2.0)
        runs = _run_lengths(seq)
        if len(runs) >= 8 and rlen > max(runs[:-1][-60:]):      # bệt dài hơn mọi bệt đã thấy → nghiêng bẻ
            pf = min(pf, 0.42)
        pf = _clamp(pf, 0.30, 0.70)
        out["HAZARD"] = (pt(pf), f"bệt {rlen}: {'theo' if pf >= .5 else 'bẻ'} {max(pf, 1-pf):.0%}")
        # 2) RUNMIRROR: cặp (nhịp hiện tại, nhịp trước) — bắt cầu 1-1, 2-2, 3-3, 2-1-2...
        f, b = mir[(min(rlen, 4), min(prev, 4))]
        pf = (f + 1.0) / (f + b + 2.0) if f + b >= 4 else 0.5
        pf = _clamp(pf, 0.30, 0.70)
        out["RUNMIRROR"] = (pt(pf), f"nhịp {min(prev,4)}→{min(rlen,4)}: {'theo' if pf >= .5 else 'bẻ'} {max(pf, 1-pf):.0%}")
        # 3) MOMENTUM: 12 phiên gần nhất cầu đang BỆT hay đang ĐẢO?
        w = seq[-12:]
        alt = sum(1 for i in range(1, len(w)) if w[i] != w[i - 1]) / max(1, len(w) - 1)
        pf = _clamp(0.5 + (0.5 - alt) * 0.6, 0.35, 0.65)
        out["MOMENTUM"] = (pt(pf), f"đảo {alt:.0%}/12p")
        # 4) CTX: ngữ cảnh 4/3/2 phiên cuối đã ra gì tiếp theo (cần >= 6 mẫu)
        p, tag = 0.5, "thiếu mẫu"
        for k in (4, 3, 2):
            c = ctx[k].get(tuple(seq[-k:])) if len(seq) >= k else None
            if c and c[0] + c[1] >= 6:
                p = (c[0] + 1.0) / (c[0] + c[1] + 2.0); tag = f"bậc{k}: TÀI {p:.0%}"; break
        out["CTX"] = (_clamp(p, 0.30, 0.70), tag)
        return out, alt

    def predict(self) -> Dict:
        base = Engine84.predict(self)
        seq = list(self.seq)
        base["expert_sides"] = {}; base["regime"] = "—"
        if len(seq) < 12:
            return base
        last, rlen = _last_run(seq)
        ex, alt = self._experts(seq, last, rlen)
        ex["ENGINE84"] = (_clamp(float(base.get("p_tai", 0.5)), 0.35, 0.65), "Engine84")

        # trọng số = kỹ năng walk-forward (shrink về 0.5), chỉ chuyên gia đang HƠN 50% mới có tiếng nói
        skill = {}
        for n in self.EXPERTS:
            h = list(self.ehits[n]); fast, slow = h[-8:], h[-30:]
            sf = (sum(fast) + 3.0) / (len(fast) + 6.0) - 0.5
            ss = (sum(slow) + 3.0) / (len(slow) + 6.0) - 0.5
            skill[n] = max(0.0, 0.55 * sf + 0.45 * ss)
        tot = sum(skill.values())
        if tot < 1e-9:      # chưa chuyên gia nào có kỹ năng → chia đều, nhưng giảm mạnh độ tin
            weights = {n: 1.0 / len(self.EXPERTS) for n in self.EXPERTS}; damp = 0.35
        else:
            weights = {n: skill[n] / tot for n in self.EXPERTS}
            damp = min(1.0, 0.35 + 5.0 * max(skill.values()))
        z = damp * sum(weights[n] * _logit(ex[n][0]) for n in self.EXPERTS)
        p_tai = 1.0 / (1.0 + math.exp(-z))
        pred = "TAI" if p_tai >= 0.5 else "XIU"
        if abs(p_tai - 0.5) < 0.004: pred = _opp(last)       # hòa → bẻ
        conf = max(52, min(68, int(round(max(p_tai, 1 - p_tai) * 100))))
        p_out = round(0.5 + (conf - 50) / 100 if pred == "TAI" else 0.5 - (conf - 50) / 100, 4)

        regime = "ĐẢO" if alt >= 0.62 else "BỆT" if alt <= 0.38 else "LẪN"
        top = sorted(self.EXPERTS, key=lambda n: -weights[n])[:3]
        det = "; ".join(f"[{n} {weights[n]:.0%}] {ex[n][1]}" for n in top)
        base.update({
            "side": pred, "confidence": conf, "p_tai": p_out,
            "reasoning": f"{pred} {conf}% | cầu {regime} · bệt {rlen} {last} | {det}",
            "experts": {n: round(weights[n], 4) for n in self.EXPERTS},
            "expert_votes": {n: round(ex[n][0], 4) for n in self.EXPERTS},
            "expert_sides": {n: ("TAI" if ex[n][0] >= 0.5 else "XIU") for n in self.EXPERTS},
            "total_signals": len(self.EXPERTS),
            "models_voted_tai": sum(1 for n in self.EXPERTS if ex[n][0] >= 0.5),
            "models_voted_xiu": sum(1 for n in self.EXPERTS if ex[n][0] < 0.5),
            "run_len": rlen, "regime": regime,
        })
        return base

    def update(self, pred_side, actual_side, pk=None):
        Engine84.learn(self, pred_side, actual_side)
        sides = (pk or {}).get("expert_sides") or {}
        for n, s in sides.items():
            if n in self.ehits and s in ("TAI", "XIU"):
                self.ehits[n].append(1 if s == actual_side else 0)


# ══════════════════════════════════════════════════════════════════════════
#  BRAIN ADAPTER — dùng Engine84 làm core
# ══════════════════════════════════════════════════════════════════════════
class Brain:
    """Adapter giữ nguyên hợp đồng app cũ, Engine84 làm engine dự đoán."""
    def __init__(self):
        self.engine = RegimeEngine()
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
            "expert_sides": raw.get("expert_sides", {}),
            "regime": raw.get("regime", "—"),
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
        }
        self._last_prediction = result
        return result

    def learn(self, pk, y: bool):
        if not isinstance(pk, dict) or pk.get("side") not in ("TAI","XIU"): return
        actual = "TAI" if y else "XIU"
        won = pk["side"] == actual
        self.engine.update(pk["side"], actual, pk)
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
# ═══════════════════════════════════════════════════════════════════════════════
#  BOOT: KEY-ADMIN + GÓI MẶC ĐỊNH
# ═══════════════════════════════════════════════════════════════════════════════
if not STORE.get("admin_key") or STORE["admin_key"] not in STORE["keys"]:
    akey = _gen_key(ADMIN_KEY_PREFIX)
    STORE["admin_key"] = akey
    STORE["keys"][akey] = {"id": "adm-" + akey, "key": akey, "name": "ADMIN-CONSOLE",
                           "role": "admin", "status": "active", "price": "0",
                           "package_id": "", "duration_days": None, "created_at": now_iso(),
                           "expires_ts": None, "expires_at": None, "max_devices": 9,
                           "note": "auto", "order_id": "", "activated": True,
                           "activated_at": now_iso(), "token": None,
                           "devices": {}, "calls_hu": 0, "calls_md5": 0, "last_call": None}
    save_store()

TPL_PRETTY = (
    "✅ THANH TOÁN THÀNH CÔNG\n"
    "━━━━━━━━━━━━━━━━\n"
    "Cảm ơn {name} đã ủng hộ PAW 💙\n\n"
    "🔑 KEY:  {key}\n"
    "📦 Gói:  {package}\n"
    "⏳ Thời hạn:  {duration}\n"
    "💰 Thanh toán:  {price}\n"
    "🧾 Mã đơn:  {order}\n"
    "━━━━━━━━━━━━━━━━\n"
    "📲 CÁCH KÍCH HOẠT\n"
    "1️⃣ Mở tool: {tool_url}\n"
    "2️⃣ Dán key vào ô KÍCH HOẠT\n"
    "3️⃣ Bấm kích hoạt → vào dùng luôn 🍀\n\n"
    "⚠️ Hạn tính từ lúc kích hoạt · 1 key = 1 thiết bị\n"
    "🆘 Hỗ trợ: {support}")
TPL_SHORT = (
    "✅ {name} ơi, key của bạn đây\n"
    "🔑 {key}\n"
    "📦 {package} · ⏳ {duration} · 💰 {price}\n"
    "👉 Dán key vào ô KÍCH HOẠT: {tool_url}\n"
    "🆘 {support}")
TPL_MIN = "🔑 {key}\n⏳ {duration}\nKích hoạt tại: {tool_url}"
TEMPLATES = {"dep": TPL_PRETTY, "gon": TPL_SHORT, "toi_gian": TPL_MIN}
OLD_DEFAULT_TPL = "✅ THANH TOÁN THÀNH CÔNG\n──────────\n🔑 Key: {key}\n📦 Gói: {package}\n💰 Giá: {price}\n📅 Hạn dùng: {expiry}\n🎮 Dùng cho: Hũ + MD5\n──────────\nDán key vào ô KÍCH HOẠT trong tool để dùng 🍀"
DEFAULT_SETTINGS = {
    "payment_template": TPL_PRETTY,
    "default_prefix": "PAXU",
    "tool_url": "",
    "support": "https://t.me/K0ZT1",
}
STORE.setdefault("settings", {})
for k, v in DEFAULT_SETTINGS.items():
    STORE["settings"].setdefault(k, v)
# Nâng cấp mẫu cũ (có link kích hoạt) → mẫu gọn mới
if ("{activate_url}" in STORE["settings"].get("payment_template", "")
        or STORE["settings"].get("payment_template", "") == OLD_DEFAULT_TPL):
    STORE["settings"]["payment_template"] = DEFAULT_SETTINGS["payment_template"]

# Gói chuẩn: 1 / 3 / 7 / 30 ngày (+ vĩnh viễn). Store cũ giữ nguyên, chỉ bổ sung thiếu.
if not STORE["packages"]:
    for pid, p in {
        "P1":  {"name": "Gói 1 Ngày",  "icon": "🌞", "price": "50K",   "days": 1,  "max_devices": 1},
        "P3":  {"name": "Gói 3 Ngày",  "icon": "🌙", "price": "120K",  "days": 3,  "max_devices": 1},
        "P7":  {"name": "Gói 7 Ngày",  "icon": "📆", "price": "250K",  "days": 7,  "max_devices": 1},
        "P30": {"name": "Gói 30 Ngày", "icon": "🗓️", "price": "500K",  "days": 30, "max_devices": 1},
        "PLT": {"name": "Gói Vĩnh Viễn", "icon": "♾️", "price": "2.000K", "days": 0, "max_devices": 1},
    }.items():
        STORE["packages"][pid] = {"id": pid, **p}
else:
    for pid, dy in {"P1": 1, "P3": 3, "P7": 7, "P30": 30}.items():
        if pid not in STORE["packages"]:
            STORE["packages"][pid] = {"id": pid, "name": "Gói %d Ngày" % dy, "icon": "📆",
                                       "price": "", "days": dy, "max_devices": 1}
for _p in STORE["packages"].values(): _p.setdefault("hours", 0)
save_store()

# ═══════════════════════════════════════════════════════════════════════════════
#  PHÂN TÍCH CẦU NGẮN / TRUNG / DÀI + ỔN ĐỊNH DÀI HẠN
# ═══════════════════════════════════════════════════════════════════════════════
def _zone_window(seq, w):
    win = seq[-w:] if len(seq) >= 3 else seq
    if not win: return {"so_phien": 0, "tai": 0, "xiu": 0, "lech": 0.0, "huong": "TRUNG_TINH", "do_manh": 0.0}
    t, x = win.count("TAI"), win.count("XIU")
    n = len(win); imb = (t - x) / n
    huong = "TAI" if imb > 0.15 else "XIU" if imb < -0.15 else "TRUNG_TINH"
    return {"so_phien": n, "tai": t, "xiu": x, "lech": round(imb, 3),
            "huong": huong, "do_manh": round(min(1.0, abs(imb) * 2), 3)}

def _run_lengths_local(seq):
    if not seq: return []
    runs, cur, cnt = [], seq[0], 1
    for v in seq[1:]:
        if v == cur: cnt += 1
        else: runs.append(cnt); cur, cnt = v, 1
    runs.append(cnt); return runs

def _run_at_index(seq):
    ra = [1] * len(seq)
    for i in range(1, len(seq)):
        ra[i] = ra[i - 1] + 1 if seq[i] == seq[i - 1] else 1
    return ra

def _break_prob(seq, rlen):
    """Xác suất gãy của run độ dài rlen — 3 tầng data-driven (đủ mẫu → dùng lịch sử)."""
    if len(seq) < 15: return 0.5, "chưa đủ dữ liệu"
    ra = _run_at_index(seq)
    b1 = c1 = 0
    for i in range(len(seq) - 1):
        if ra[i] == rlen:
            if seq[i + 1] != seq[i]: b1 += 1
            else: c1 += 1
    if b1 + c1 >= 5: return (b1 + 1.0) / (b1 + c1 + 2.0), f"tầng1 n={b1+c1}"
    b2 = c2 = 0
    for i in range(len(seq) - 1):
        if ra[i] >= rlen:
            if seq[i + 1] != seq[i]: b2 += 1
            else: c2 += 1
    if b2 + c2 >= 5: return (b2 + 1.0) / (b2 + c2 + 2.0), f"tầng2 n={b2+c2}"
    return min(0.68, 0.49 + (rlen - 1) * 0.03), "tầng3 prior"

def analyze_cau(seq):
    """Phân tầng cầu NGẮN (3-5 phiên) / TRUNG (6-15) / DÀI (>15) + nhận dạng."""
    if len(seq) < 5:
        return {"da_du_du_lieu": False}
    runs = _run_lengths_local(seq[-30:])
    last, rlen = seq[-1], _run_lengths_local(seq)[-1]
    cau_prefix = "-".join(str(r) for r in _run_lengths_local(seq)[-5:])
    # Nhận dạng: bệt / xen kẽ / trung gian
    avg_run = sum(runs) / len(runs)
    mx = max(runs)
    loai = "BỆT" if mx >= 5 else "XEN_KẼ_1_1" if avg_run <= 1.3 else "NHỊP_2_2" if (avg_run <= 2.5 and mx <= 3) else "PHỨC_HỢP"
    ngan  = _zone_window(seq, 5)
    trung = _zone_window(seq, 12)
    dai   = _zone_window(seq, 30)
    p_brk, tg = _break_prob(seq, rlen)
    khuyen_ngi = ("BẺ" if p_brk > 0.54 else "THEO" if p_brk < 0.46 else "CÂN NHẮC") if rlen >= 2 else "CHỜ_NHỊP"
    return {"da_du_du_lieu": True, "dang_cau": cau_prefix, "phan_loai": loai,
            "run_hien_tai": {"ben": last, "do_dai": rlen},
            "ngan": ngan, "trung": trung, "dai": dai,
            "p_gay_run": round(p_brk, 3), "nguon_p": tg,
            "khuyen_nghi": khuyen_ngi}

def stability_info(brain):
    """Bộ điều hành ổn định: đo chất lượng dài hạn, giảm tin khi chuỗi thua dài."""
    hits = list(getattr(brain, "hit", []))
    n = len(hits)
    acc = round(sum(hits) / n, 3) if n else None
    ls = getattr(brain, "loss_streak", 0)
    che_do = "BÌNH_THƯỜNG" if ls < 3 else "GIẢM_TIN_CÂY" if ls < 5 else "TẨN_TRỌNG_TỐI_ĐA"
    return {"danh_gia_phien": n, "do_chinh_xac_30": acc,
            "chuoi_thua": ls, "che_do": che_do,
            "chu_thich": ("Đang ở chế độ an toàn: hệ thống siết độ tin cậy, ưu tiên không bắt nhịp bừa" if ls >= 3 else "Hệ thống hoạt động ổn định")}

# ═══════════════════════════════════════════════════════════════════════════════
#  /MAKEY — KÍCH HOẠT KEY
# ═══════════════════════════════════════════════════════════════════════════════
_makey_fails, _makey_block = {}, {}

def _ratelimit(ip):
    now = time.time()
    if _makey_block.get(ip, 0) > now: return False
    _makey_fails[ip] = [t for t in _makey_fails.get(ip, []) if now - t < 300]
    return len(_makey_fails[ip]) < 10

def _record_fail(ip):
    _makey_fails.setdefault(ip, []).append(time.time())
    if len(_makey_fails[ip]) >= 10: _makey_block[ip] = time.time() + 600

@app.route("/makey", methods=["GET", "POST"])
def makey():
    """Kích hoạt key: POST {\"key\": ...} hoặc GET /makey?key=...&device=tên
    → trả token dùng cho cả 2 bàn Hũ + MD5."""
    ip = request.remote_addr or "0.0.0.0"
    if not _ratelimit(ip):
        return out({"ok": False, "loi": "rate_limited", "thong_bao": "Thử quá nhiều lần, chờ 10 phút"}, 429)
    j = request.get_json(silent=True) or {}
    key = (j.get("key") or request.form.get("key") or request.args.get("key") or "").strip().upper()
    dev_name = (j.get("device") or request.args.get("device") or "").strip()[:40]
    if not key:
        return out({"ok": False, "loi": "missing_key", "thong_bao": "Thiếu key — gửi {\"key\": \"PAXU-XXXX-XXXX-XXXX\"}"}, 400)
    k = get_key_by_key(key)
    if k is None:
        _record_fail(ip)
        return out({"ok": False, "loi": "invalid_key", "thong_bao": "Key không tồn tại"}, 404)
    # LUU Y: key_is_usable() coi "chua kich hoat" la KHONG usable, nhung
    # /makey chinh la noi KICH HOAT lan dau - khong duoc chan truong hop
    # nay, chi chan khoa / het han (loi code goc gay vong lap, khong ai
    # kich hoat duoc key moi).
    st = key_status(k)
    if k.get("role") != "admin" and st in ("khóa", "hết hạn"):
        _msg = "key đã bị khóa" if st == "khóa" else "key đã hết hạn — liên hệ admin gia hạn"
        return out({"ok": False, "loi": "key_locked", "thong_bao": _msg}, 403)
    first = False
    if not k.get("token"):
        k["token"] = secrets.token_urlsafe(24)
        first = True
    if k.get("role") != "admin":
        if not k.get("activated"):
            _sec = _key_dur_sec(k)
            if _sec:  # tính hạn từ lúc kích hoạt (hỗ trợ cả giờ)
                k["expires_ts"] = time.time() + _sec
                k["expires_at"] = datetime.fromtimestamp(k["expires_ts"], VN).replace(microsecond=0).isoformat()
            k["activated"] = True; k["activated_at"] = now_iso(); first = True
        # bind thiết bị (tối đa max_devices token riêng, đơn giản: 1 token)
        if first or not k.get("devices"):
            k.setdefault("devices", {})[k["token"]] = {
                "activated_at": now_iso(), "last_call": None, "ip": ip,
                "ua": (request.headers.get("User-Agent", "") or "")[:120],
                "calls_hu": 0, "calls_md5": 0}
            if dev_name: k["devices"][k["token"]]["name"] = dev_name
    save_store()
    pk = STORE["packages"].get(k.get("package_id") or "", {})
    msg_tt = _payment_msg(k)
    return out({"ok": True,
                "tieude": "✅ KÍCH HOẠT THÀNH CÔNG!",
                "token": k["token"], "key": k["key"], "ten": k.get("name", ""),
                "goi": k.get("package_name") or pk.get("name", ""), "het_han": k.get("expires_at") or "Vĩnh viễn ♾️",
                "thoi_han": _dur_text(_key_dur_sec(k)), "con_lai_giay": (max(0, int(k["expires_ts"] - time.time())) if k.get("expires_ts") else None),
                "quyen": ["hu", "md5"],
                "api_du_doan": {"hu": f"{BASE_URL}/api/{k['token']}/hu",
                                 "md5": f"{BASE_URL}/api/{k['token']}/md5"},
                "api_lich_su": {"hu": f"{BASE_URL}/api/{k['token']}/history/hu",
                                 "md5": f"{BASE_URL}/api/{k['token']}/history/md5"},
                "tin_nhan_thanh_toan": msg_tt,
                "lan_dau_kich_hoat": first})

# ═══════════════════════════════════════════════════════════════════════════════
#  API DỰ ĐOÁN (CẦN KEY ĐÃ KÍCH HOẠT)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/api/<token>/<code>", methods=["GET", "OPTIONS"])
def api_predict(token, code):
    code = code.lower()
    if code not in URLS:
        return out({"ok": False, "loi": "not_found", "thong_bao": "Bàn không hợp lệ: chỉ có hu hoặc md5"}, 404)
    k = get_key_by_token(token)
    ok, msg = key_is_usable(k)
    if not ok:
        return out({"ok": False, "loi": "unauthorized", "thong_bao": msg, "huong_dan": "POST /makey {\"key\": ...}"}, 401)
    dev_ok, dev_msg = device_check(k, token, request.headers.get("X-Device-ID"))
    if not dev_ok:
        return out({"ok": False, "loi": "device_mismatch", "thong_bao": dev_msg}, 403)
    t, err = table_or_error(code)
    if err: return err
    touch_call(k, token, code); save_store()
    res = view_main(t)
    seq = list(t.brain.engine.seq)
    res["phan_tich_cau"] = analyze_cau(seq)
    res["on_dinh"] = stability_info(t.brain)
    pk = STORE["packages"].get(k.get("package_id") or "", {})
    con_lai = "Vĩnh viễn ♾️"
    if k.get("expires_ts"):
        giay = max(0, int(k["expires_ts"] - time.time()))
        con_lai = f"{giay // 86400} ngày {giay % 86400 // 3600} giờ"
    res["key"] = {"key": k["key"], "ten": k.get("name", ""), "goi": pk.get("name", ""),
                  "con_lai": con_lai, "dieu_khoan": "1 key dùng chung cho bàn Hũ + MD5"}
    return out(res)

@app.route("/api/<token>/history/<code>")
def api_history(token, code):
    code = code.lower()
    if code not in URLS:
        return out({"ok": False, "loi": "not_found", "thong_bao": "Bàn không hợp lệ: hu hoặc md5"}, 404)
    k = get_key_by_token(token)
    ok, msg = key_is_usable(k)
    if not ok:
        return out({"ok": False, "loi": "unauthorized", "thong_bao": msg}, 401)
    dev_ok, dev_msg = device_check(k, token, request.headers.get("X-Device-ID"))
    if not dev_ok:
        return out({"ok": False, "loi": "device_mismatch", "thong_bao": dev_msg}, 403)
    t, err = table_or_error(code)
    if err: return err
    touch_call(k, token, code); save_store()
    try: limit = max(1, min(HIST_MAX, int(request.args.get("limit", HIST_MAX))))
    except Exception: limit = HIST_MAX
    return out(view_history(t, limit))

@app.get("/huong-dan")
def huong_dan():
    """Trang JSON hướng dẫn cho ai làm tool HTML gọi API."""
    return out({
        "ok": True,
        "tieu_de": "📖 HƯỚNG DẪN GỌI API PAW TX (cho tool HTML riêng)",
        "buoc_1_kich_hoat_key": {
            "mo_ta": "Tool gọi endpoint này khi khách dán key vào ô KÍCH HOẠT (cần key admin đã tạo).",
            "phuong_thuc": "POST",
            "url": BASE_URL + "/makey",
            "body_json": {"key": "PAXU-XXXX-XXXX-XXXX"},
            "hoac_get": BASE_URL + "/makey?key=PAXU-XXXX-XXXX-XXXX",
            "tra_ve_quan_trong": "token — lưu lại, mọi API sau dùng token này (một lần kích hoạt là đủ)",
            "loi_thuong_gap": {"invalid_key": "key không tồn tại", "key_locked": "key bị khóa/hết hạn/chưa kích hoạt được"}
        },
        "buoc_2_goi_du_doan_2_ban": {
            "hu": BASE_URL + "/api/<TOKEN>/hu",
            "md5": BASE_URL + "/api/<TOKEN>/md5",
            "phuong_thuc": "GET",
            "tra_ve": {"du_doan_tiep_theo": "phien_hien_tai.du_doan (TAI/XIU)", "do_tin_cay": "phien_hien_tai.do_tin_cay",
                        "ly_do": "tu_hoc + phan_tich_cau + ly_do chi tiết trong phien_hien_tai", "cau": "phien_hien_tai.cau (VD 1-2-1)"},
            "vi_du_js": "const r = await fetch('" + BASE_URL + "/api/' + token + '/hu').then(x=>x.json());\nalert(r.phien_hien_tai.du_doan);"
        },
        "buoc_3_lich_su": {"hu": BASE_URL + "/api/<TOKEN>/history/hu?limit=50",
                            "md5": BASE_URL + "/api/<TOKEN>/history/md5?limit=50"},
        "luu_y": ["1 key = dùng cả 2 bàn Hũ + MD5, không cần kích hoạt lại",
                   "Token sống theo key, hết hạn khi key hết hạn/bị khóa",
                   "API trả JSON in đẹp, thêm ?compact=1 để gọn"]})

@app.get("/ping")
def ping(): return out({"ok": True, "t": now_iso()})

@app.get("/")
def index():
    return out({"ok": True, "api": "PAW TX v6 PRO — Gói + Đơn hàng + Engine 84 models",
                "su_dung": ["1) Admin tạo gói & key (SLL theo đơn hàng)",
                             "2) POST /makey {\"key\": ...} → nhận token",
                             "3) GET /api/<token>/hu  ·  GET /api/<token>/md5",
                             "4) GET /api/<token>/history/hu  ·  /md5"],
                "admin": "/admin"})

# ═══════════════════════════════════════════════════════════════════════════════
#  POLLER NỀN
# ═══════════════════════════════════════════════════════════════════════════════
def load_toggles():
    off = {x.strip() for x in os.getenv("DISABLED_TABLES", "").split(",") if x.strip()}
    try: saved = json.load(open(STATE_FILE))
    except Exception: saved = {}
    for c, t in TABLES.items(): t.enabled = bool(saved.get(c, c not in off))

def save_toggles():
    try: json.dump({c: t.enabled for c, t in TABLES.items()}, open(STATE_FILE, "w"))
    except Exception: pass

load_toggles()
_poller = {"on": False}; _plock = threading.Lock()

def _loop():
    while True:
        for t in TABLES.values():
            if t.enabled:
                try: t.refresh()
                except Exception: pass
        time.sleep(POLL_SEC)

@app.before_request
def start_poller():
    if not _poller["on"]:
        with _plock:
            if not _poller["on"]:
                _poller["on"] = True
                threading.Thread(target=_loop, daemon=True).start()
                threading.Thread(target=_backup_loop, daemon=True).start()

def table_or_error(code):
    t = TABLES.get(code)
    if not t: return None, out({"ok": False, "loi": "not_found", "thong_bao": "Dùng hu hoặc md5"}, 404)
    if not t.enabled: return None, out({"ok": False, "loi": "table_off", "thong_bao": "Bàn %s đang tắt" % t.name}, 503)
    if not t.ready: t.refresh()
    elif time.time() - t.fetch_ts > STALE_SEC:
        threading.Thread(target=t.refresh, kwargs={"block": False}, daemon=True).start()
    if not t.ready:
        return None, out({"ok": False, "loi": "upstream_error", "thong_bao": "Chưa lấy được dữ liệu", "chi_tiet": t.err}, 503)
    return t, None

# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN API
# ═══════════════════════════════════════════════════════════════════════════════
def authed(): return bool(session.get("adm")) and session.get("adm_until", 0) > time.time()
def guard():
    if not authed(): return out({"ok": False, "loi": "unauthorized", "thong_bao": "Chưa đăng nhập"}, 401)
    return None

@app.post("/admin/login")
def admin_login():
    j = request.get_json(silent=True) or request.form
    if j.get("pw", "") == ADMIN_PASSWORD:
        session["adm"] = True; session["adm_until"] = time.time() + 10 * 3600
        return out({"ok": True, "thong_bao": "Đăng nhập thành công"})
    return out({"ok": False, "thong_bao": "Sai mật khẩu"}, 401)

@app.get("/admin/login")
def admin_login_get():
    """Đường dự phòng: mở thẳng .../admin/login?pw=MATKHAU để vào luôn."""
    if request.args.get("pw", "") == ADMIN_PASSWORD:
        session["adm"] = True; session["adm_until"] = time.time() + 10 * 3600
        return redirect("/admin")
    return redirect("/admin")

@app.get("/admin/logout")
def admin_logout(): session.clear(); return redirect("/admin")

class _SafeFmt(dict):
    def __missing__(self, key): return "{" + key + "}"

def _payment_msg(k):
    st = STORE["settings"]
    pk = STORE["packages"].get(k.get("package_id") or "", {})
    sec = _key_dur_sec(k); exp = k.get("expires_at")
    if exp: expiry = "đến " + str(exp)[:16].replace("T", " ")
    elif sec: expiry = "tính từ lúc kích hoạt (" + _dur_text(sec) + ")"
    else: expiry = "Vĩnh viễn ♾️"
    v = {"key": k.get("key", ""), "price": k.get("price") or "—",
         "package": k.get("package_name") or pk.get("name") or "Tuỳ chỉnh",
         "name": k.get("name") or "Quý khách", "duration": _dur_text(sec), "expiry": expiry,
         "order": k.get("order_id") or "—",
         "tool_url": st.get("tool_url") or "(link tool — admin gửi riêng)",
         "support": st.get("support") or "—", "activate_url": BASE_URL + "/makey"}
    try: return st.get("payment_template", TPL_PRETTY).format_map(_SafeFmt(v))
    except Exception: return TPL_SHORT.format_map(_SafeFmt(v))

@app.get("/admin/api/overview")
def adm_overview():
    g = guard()
    if g: return g
    keys = [k for k in STORE["keys"].values() if k.get("role") != "admin"]
    admk = STORE["keys"].get(STORE.get("admin_key", ""), {})
    if not admk.get("token"):
        admk["token"] = secrets.token_urlsafe(24); save_store()
    tables = []
    for c, t in TABLES.items():
        tk = stats(list(t.hist))
        tables.append({"code": c, "ten": t.name, "bat": t.enabled, "phien_hien_tai": t.last_id,
                       "loi": t.err, "luoi_ms": t.ms,
                       "du_doan_tiep": (t.pending or {}).get("du_doan"),
                       "ty_le_thang": tk["ty_le"], "thang": tk["win"], "thua": tk["lose"]})
    doanh_thu_orders = sum(1 for _ in STORE["orders"])
    return {"so_key": len(keys), "da_kich_hoat": sum(1 for k in keys if k.get("activated")),
            "het_han": sum(1 for k in keys if key_status(k) == "hết hạn"),
            "dang_hoat_dong": sum(1 for k in keys if key_status(k) == "hoạt động"),
            "luot_goi_hu": sum(int(k.get("calls_hu", 0)) for k in STORE["keys"].values()),
            "luot_goi_md5": sum(int(k.get("calls_md5", 0)) for k in STORE["keys"].values()),
            "so_goi": len(STORE["packages"]), "so_don_hang": doanh_thu_orders,
            "key_admin_console": {"key": STORE.get("admin_key", ""), "token": admk.get("token", ""),
                                   "api_history": f"/api/{admk.get('token', '')}/history/hu"},
            "ban": tables, "cap_nhat": now_iso()}

# ── Gói ──
@app.get("/admin/api/packages")
def adm_pkgs():
    g = guard()
    if g: return g
    return out({"ok": True, "packages": [{**p, "hours": p.get("hours", 0), "thoi_han": _dur_text(_pkg_sec(p))} for p in STORE["packages"].values()]})

@app.post("/admin/api/packages")
def adm_pkg_edit():
    g = guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    pid = str(d.get("id", "")).strip().upper() or ("P" + uuid.uuid4().hex[:4].upper())
    if d.get("delete"):
        STORE["packages"].pop(pid, None); save_store()
        return out({"ok": True, "thong_bao": "Đã xóa gói " + pid})
    if pid not in STORE["packages"] and not d.get("name"):
        return out({"ok": False, "thong_bao": "Gói mới cần đặt tên"}, 400)
    p = STORE["packages"].setdefault(pid, {"id": pid, "name": "", "icon": "✨", "price": "", "days": 30, "hours": 0, "max_devices": 1})
    for f in ("name", "icon", "price"):
        if d.get(f) is not None and str(d[f]).strip() != "": p[f] = str(d[f]).strip()
    if d.get("days") is not None and str(d.get("days")).strip() != "": p["days"] = min(3650, _to_int(d["days"]))
    if d.get("hours") is not None and str(d.get("hours")).strip() != "": p["hours"] = min(100000, _to_int(d["hours"]))
    if str(d.get("max_devices", "")).isdigit(): p["max_devices"] = int(d["max_devices"])
    p.setdefault("hours", 0)
    save_store()
    p["thoi_han"] = _dur_text(_pkg_sec(p))
    return out({"ok": True, "package": p})

# ── Tạo key SLL + đơn hàng ──
@app.post("/admin/api/keys")
def adm_create():
    g = guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    count = max(1, min(200, _to_int(d.get("count", 1), 1)))
    pk = STORE["packages"].get(str(d.get("package_id", "")).strip().upper())
    prefix = (str(d.get("prefix") or STORE["settings"]["default_prefix"]).strip()[:6]).upper() or "PAXU"
    # Thời hạn: vĩnh viễn > tự nhập ngày/giờ > gói. (duration_days = tương thích bản cũ)
    has_days  = str(d.get("days", "")).strip() != ""
    has_hours = str(d.get("hours", "")).strip() != ""
    if d.get("permanent") in (True, 1, "1", "true"):
        sec, label = None, "Vĩnh viễn"
    elif has_days or has_hours:
        sec = min(3650, _to_int(d.get("days"))) * 86400 + min(100000, _to_int(d.get("hours"))) * 3600
        if sec <= 0: return out({"ok": False, "thong_bao": "Nhập số ngày hoặc số giờ lớn hơn 0"}, 400)
        label = "Tuỳ chỉnh · " + _dur_text(sec)
    elif str(d.get("duration_days", "")).strip() != "":
        sec = _to_int(d["duration_days"]) * 86400 or None
        label = "Tuỳ chỉnh · " + _dur_text(sec)
    elif pk:
        sec, label = _pkg_sec(pk), pk["name"]
    else:
        return out({"ok": False, "thong_bao": "Chọn gói, hoặc nhập số ngày/giờ"}, 400)
    price = str(d["price"]).strip() if str(d.get("price", "")).strip() else (pk["price"] if pk else "")
    name = str(d.get("name", "")).strip()
    note = str(d.get("note", ""))
    max_dev = _to_int(d.get("max_devices"), 0) or (pk.get("max_devices", 1) if pk else 1)
    oid = "DH" + datetime.now(VN).strftime("%y%m%d") + "-" + uuid.uuid4().hex[:5].upper()
    STORE["orders"][oid] = {"id": oid, "khach": name or "Khách lẻ", "package": label,
                             "price": price, "so_key": count, "ngay_tao": now_iso(),
                             "trang_thai": "mới", "thoi_han": _dur_text(sec), "keys": []}
    created = []
    for _ in range(count):
        key = _gen_key(prefix)
        while key in STORE["keys"]: key = _gen_key(prefix)
        k = _new_key(key, prefix, {"id": pk["id"], "price": price, "days": 0} if (pk and not (has_days or has_hours)) else None, name, note, oid)
        k["price"] = price; k["max_devices"] = max_dev
        k["duration_sec"] = sec; k["duration_days"] = (sec // 86400 or None) if sec else None
        k["package_name"] = label
        k["package_id"] = pk["id"] if (pk and label == pk["name"]) else ""
        STORE["keys"][key] = k
        STORE["orders"][oid]["keys"].append(key)
        created.append(key)
    save_store()
    msgs = [{"key": kk, "tin_nhan": _payment_msg(STORE["keys"][kk])} for kk in created]
    return out({"ok": True, "don_hang": oid, "da_tao": len(created), "goi": label, "thoi_han": _dur_text(sec),
                "tin_nhan_thanh_toan": msgs,
                "tin_nhan_gop": "\n\n".join(m["tin_nhan"] for m in msgs) if len(msgs) > 1 else msgs[0]["tin_nhan"]})

@app.get("/admin/api/keys")
def adm_keys():
    g = guard()
    if g: return g
    ks = [_key_public(k) for k in sorted(STORE["keys"].values(), key=lambda x: x["created_at"], reverse=True)]
    return out({"ok": True, "tong": len(ks), "keys": ks})

@app.post("/admin/api/keys/<kid>")
def adm_edit(kid):
    g = guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    for k in STORE["keys"].values():
        if k["id"] == kid or k["key"] == kid:
            if "name"  in d: k["name"] = str(d["name"])
            if "price" in d: k["price"] = str(d["price"])
            if "note"  in d: k["note"] = str(d["note"])
            if d.get("status") in ("banned", "active"): k["status"] = d["status"]
            if d.get("max_devices") and str(d["max_devices"]).isdigit(): k["max_devices"] = int(d["max_devices"])
            _ext = _to_int(d.get("extend_days")) * 86400 + _to_int(d.get("extend_hours")) * 3600
            if _ext:
                if k.get("activated") and k.get("expires_ts"):
                    k["expires_ts"] = max(k["expires_ts"], time.time()) + _ext
                    k["expires_at"] = datetime.fromtimestamp(k["expires_ts"], VN).replace(microsecond=0).isoformat()
                    k["duration_sec"] = (_key_dur_sec(k) or 0) + _ext
                elif not k.get("activated") and _key_dur_sec(k):
                    k["duration_sec"] = _key_dur_sec(k) + _ext
                k["duration_days"] = (k["duration_sec"] // 86400 or None) if k.get("duration_sec") else k.get("duration_days")
            if d.get("reset_calls"):
                k["calls_hu"] = 0; k["calls_md5"] = 0; k["devices"] = {}
            if d.get("revoke_activation"):
                k["activated"] = False; k["activated_at"] = None; k["token"] = None
                k["devices"] = {}; k["expires_ts"] = None; k["expires_at"] = None
                if k.get("duration_sec") is None and k.get("duration_days"): k["duration_sec"] = k["duration_days"] * 86400
            save_store()
            return out({"ok": True, "key": _key_public(k), "tin_nhan_thanh_toan": _payment_msg(k)})
    return out({"ok": False, "thong_bao": "Không tìm thấy key"}, 404)

@app.post("/admin/api/keys/<kid>/delete")
def adm_del(kid):
    g = guard()
    if g: return g
    k = STORE["keys"].get(kid)
    if k and k.get("role") != "admin":
        del STORE["keys"][kid]
        for o in STORE["orders"].values():
            if kid in o.get("keys", []): o["keys"].remove(kid)
        save_store()
        return out({"ok": True, "thong_bao": "Đã xóa " + kid})
    return out({"ok": False, "thong_bao": "Không tìm thấy key"}, 404)

@app.get("/admin/api/orders")
def adm_orders():
    g = guard()
    if g: return g
    ords = sorted(STORE["orders"].values(), key=lambda o: o["ngay_tao"], reverse=True)
    for o in ords:
        o["trang_thai_thuc"] = {kk: key_status(STORE["keys"][kk]) for kk in o["keys"] if kk in STORE["keys"]}
    return out({"ok": True, "tong": len(ords), "don_hang": ords})

@app.post("/admin/api/orders/<oid>")
def adm_order_act(oid):
    g = guard()
    if g: return g
    o = STORE["orders"].get(oid)
    if not o: return out({"ok": False, "thong_bao": "Không có đơn hàng"}, 404)
    d = request.get_json(silent=True) or request.form
    if d.get("delete"):
        for kk in o["keys"]: STORE["keys"].pop(kk, None)
        del STORE["orders"][oid]; save_store()
        return out({"ok": True, "thong_bao": "Đã xóa đơn + toàn bộ key của đơn"})
    if d.get("status"): o["trang_thai"] = str(d["status"])
    save_store()
    return out({"ok": True, "don_hang": o})

@app.route("/admin/api/settings", methods=["GET", "POST"])
def adm_settings():
    g = guard()
    if g: return g
    if request.method == "POST":
        d = request.get_json(silent=True) or request.form
        for f in ("payment_template", "default_prefix"):
            if d.get(f) and str(d[f]).strip(): STORE["settings"][f] = str(d[f]).strip() if f == "default_prefix" else str(d[f])
        for f in ("tool_url", "support"):
            if f in d: STORE["settings"][f] = str(d[f]).strip()
        save_store()
    st = dict(STORE["settings"])
    st["preview"] = _payment_msg({"key": "PAXU-A7K3-M9ZD-2F9T", "price": "250K", "name": "Anh Tú",
                                   "package_name": "Gói 3 Ngày", "duration_sec": 3 * 86400,
                                   "order_id": "DH260101-AB12C", "expires_at": None})
    return out({"ok": True, "settings": st, "templates": TEMPLATES})

@app.get("/admin/api/history/<code>")
def adm_history_api(code):
    g = guard()
    if g: return g
    code = code.lower()
    if code not in URLS: return out({"ok": False, "thong_bao": "hu hoặc md5"}, 404)
    t, err = table_or_error(code)
    if err: return err
    try: limit = max(1, min(HIST_MAX, int(request.args.get("limit", 30))))
    except Exception: limit = 30
    res = view_history(t, limit)
    m = view_main(t)
    res["phien_hien_tai"] = m["phien_hien_tai"]; res["phien_truoc"] = m["phien_truoc"]
    res["che_do_cau"] = ((t.pending or {}).get("pk") or {}).get("regime")
    res["phan_tich_cau"] = analyze_cau(list(t.brain.engine.seq))
    return out(res)
# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN UI — NỀN TRẮNG, ICON ĐẸP, COPY 1 CHẠM
# ═══════════════════════════════════════════════════════════════════════════════
ADMIN_HTML = r"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>PAW TX · Admin</title>
<script>try{var t=localStorage.getItem('paw_theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.dataset.theme=t}catch(e){document.documentElement.dataset.theme='light'}</script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--r:16px;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
[data-theme=light]{--bg:#fff;--bg2:#f5f7fb;--card:#fff;--bd:#e4e9f1;--tx:#0f172a;--tx2:#475569;--tx3:#94a3b8;--pri:#2563eb;--pri-s:#e8f0ff;--ok:#15803d;--ok-s:#e3f6ea;--bad:#dc2626;--bad-s:#fdeaea;--warn:#b45309;--warn-s:#fef3dc;--tai:#e11d48;--tai-s:#ffe9ee;--xiu:#0369a1;--xiu-s:#e0f2fe;--sh:0 1px 2px rgba(15,23,42,.05),0 6px 20px rgba(15,23,42,.06);color-scheme:light}
[data-theme=dark]{--bg:#000;--bg2:#0a0a0c;--card:#111114;--bd:#27272c;--tx:#f4f4f6;--tx2:#a1a1aa;--tx3:#6b6b74;--pri:#4f8cff;--pri-s:#14264a;--ok:#4ade80;--ok-s:#0e2a1a;--bad:#f87171;--bad-s:#2e1214;--warn:#fbbf24;--warn-s:#2c2209;--tai:#fb7185;--tai-s:#2e1219;--xiu:#38bdf8;--xiu-s:#0c2433;--sh:0 1px 0 rgba(255,255,255,.03),0 8px 28px rgba(0,0,0,.6);color-scheme:dark}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg2);color:var(--tx);font:14px/1.55 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;min-height:100vh;transition:background .2s,color .2s}
button{font:inherit;cursor:pointer;border:0;color:inherit;background:none}
input,select,textarea{font:inherit;color:var(--tx);background:var(--bg);border:1.5px solid var(--bd);border-radius:11px;padding:10px 12px;width:100%;outline:none;transition:border .15s,box-shadow .15s}
input:focus,select:focus,textarea:focus{border-color:var(--pri);box-shadow:0 0 0 3px var(--pri-s)}
textarea{resize:vertical;font-family:var(--mono);font-size:12.5px;line-height:1.6}
label{display:block;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--tx3);margin:12px 0 5px}
code{font-family:var(--mono);font-size:12px;background:var(--bg2);border:1px solid var(--bd);padding:1px 6px;border-radius:6px}
h2{font-size:17px;font-weight:800;letter-spacing:-.02em;margin-bottom:4px}
.muted{color:var(--tx3);font-size:12.5px}
.hide{display:none!important}

/* topbar */
.top{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(14px);border-bottom:1px solid var(--bd);padding:max(10px,env(safe-area-inset-top)) 16px 0}
.top-in{max-width:1240px;margin:0 auto;display:flex;align-items:center;gap:10px;height:46px}
.logo{width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,#2563eb,#7c3aed);display:grid;place-items:center;color:#fff;font-weight:900;font-size:15px}
.brand{font-weight:900;letter-spacing:-.03em;font-size:16px}.brand small{display:block;font-size:9.5px;color:var(--tx3);letter-spacing:.16em;font-weight:700;margin-top:-3px}
.sp{flex:1}
.ibtn{width:38px;height:38px;border-radius:11px;border:1.5px solid var(--bd);display:grid;place-items:center;font-size:17px;background:var(--card)}
.ibtn:hover{border-color:var(--pri)}
.tabs{max-width:1240px;margin:0 auto;display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;padding:6px 0 8px}
.tabs::-webkit-scrollbar{display:none}
.tabs button{white-space:nowrap;padding:8px 13px;border-radius:999px;font-weight:700;font-size:12.5px;color:var(--tx2);border:1.5px solid transparent}
.tabs button:hover{background:var(--bg2)}
.tabs button.on{background:var(--tx);color:var(--bg)}
.sep{width:1px;background:var(--bd);margin:6px 4px;flex:none}
.main{max-width:1240px;margin:0 auto;padding:18px 16px calc(60px + env(safe-area-inset-bottom))}

/* basics */
.card{background:var(--card);border:1px solid var(--bd);border-radius:var(--r);padding:18px;box-shadow:var(--sh);margin-bottom:14px;min-width:0}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:10px 16px;border-radius:11px;font-weight:800;font-size:13px;border:1.5px solid var(--bd);background:var(--card);transition:.15s}
.btn:hover{border-color:var(--pri);color:var(--pri)}
.btn:active{transform:scale(.97)}
.btn.pri{background:var(--pri);border-color:var(--pri);color:#fff}.btn.pri:hover{filter:brightness(1.1);color:#fff}
.btn.danger{color:var(--bad)}.btn.danger:hover{border-color:var(--bad);color:var(--bad)}
.btn.sm{padding:6px 10px;font-size:12px;border-radius:9px}
.btn.big{width:100%;padding:14px;font-size:15px;border-radius:13px}
.pill{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:999px;font-size:11px;font-weight:800;letter-spacing:.03em;white-space:nowrap}
.pill.act{background:var(--ok-s);color:var(--ok)}.pill.ban{background:var(--bad-s);color:var(--bad)}.pill.exp{background:var(--warn-s);color:var(--warn)}.pill.idle{background:var(--bg2);color:var(--tx2);border:1px solid var(--bd)}
.pill.tai{background:var(--tai-s);color:var(--tai)}.pill.xiu{background:var(--xiu-s);color:var(--xiu)}
.dot{width:7px;height:7px;border-radius:50%;background:currentColor;animation:pl 2s infinite}@keyframes pl{50%{opacity:.35}}
.kk{font-family:var(--mono);font-weight:700;font-size:12.5px;letter-spacing:.02em}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:14px}
.kpi{background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:14px 16px;box-shadow:var(--sh)}
.kpi b{display:block;font-size:26px;font-weight:900;letter-spacing:-.04em;line-height:1.1}.kpi span{font-size:12px;color:var(--tx2)}
.bar{height:8px;border-radius:99px;background:var(--bg2);overflow:hidden;border:1px solid var(--bd)}.bar i{display:block;height:100%;border-radius:99px;background:var(--pri)}
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:10.5px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--tx3);padding:9px 10px;border-bottom:1.5px solid var(--bd);white-space:nowrap}
td{padding:10px;border-bottom:1px solid var(--bd);font-size:13px;vertical-align:middle}
tr:last-child td{border-bottom:0}
.scroll{overflow:auto;max-width:100%;border:1px solid var(--bd);border-radius:12px}
.scroll table{min-width:620px}
#toast{position:fixed;left:50%;bottom:calc(22px + env(safe-area-inset-bottom));transform:translateX(-50%);background:var(--tx);color:var(--bg);padding:11px 18px;border-radius:12px;font-weight:700;font-size:13px;z-index:99;display:none;box-shadow:var(--sh);max-width:92vw}
.modalbg{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;z-index:80;padding:14px}
.modal{background:var(--card);border:1px solid var(--bd);border-radius:18px;max-width:600px;width:100%;max-height:88vh;overflow:auto;padding:20px;box-shadow:var(--sh)}
.msg{white-space:pre-wrap;font-size:13.5px;line-height:1.7;padding:16px;border-radius:14px;background:var(--bg2);border:1.5px dashed var(--bd);word-break:break-word}

/* chọn gói */
.opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.opt{display:flex;flex-direction:column;gap:2px;align-items:flex-start;text-align:left;padding:12px 14px;border-radius:14px;border:1.5px solid var(--bd);background:var(--card);transition:.15s}
.opt .ic{font-size:20px}.opt b{font-size:14px}.opt small{color:var(--tx3);font-size:11.5px}
.opt:hover{border-color:var(--pri)}
.opt.on{border-color:var(--pri);background:var(--pri-s);box-shadow:0 0 0 3px var(--pri-s)}
.quick{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.quick button{padding:6px 11px;border-radius:999px;border:1.5px solid var(--bd);font-size:12px;font-weight:700;background:var(--card)}
.quick button:hover{border-color:var(--pri);color:var(--pri)}
.summary{margin-top:14px;padding:12px 14px;border-radius:12px;background:var(--pri-s);color:var(--pri);font-weight:700;font-size:13px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 2px}
.chips code{cursor:pointer}.chips code:hover{border-color:var(--pri);color:var(--pri)}

/* lịch sử mỗi bàn */
.hs-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.hs-title{font-size:22px;font-weight:900;letter-spacing:-.03em}
.totals{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:14px}
.tot{background:var(--card);border:1px solid var(--bd);border-radius:16px;padding:16px;text-align:center;box-shadow:var(--sh)}
.tot b{display:block;font-size:clamp(28px,6vw,40px);font-weight:900;letter-spacing:-.05em;line-height:1}
.tot span{font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--tx3)}
.tot.w b{color:var(--ok)}.tot.l b{color:var(--bad)}.tot.r b{color:var(--pri)}
.pred{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.pred .big{font-size:clamp(40px,9vw,64px);font-weight:900;letter-spacing:-.05em;line-height:1}
.pred .big.TAI{color:var(--tai)}.pred .big.XIU{color:var(--xiu)}
.dots{display:flex;flex-wrap:wrap;gap:5px}.dots i{width:22px;height:22px;border-radius:7px;display:grid;place-items:center;font-style:normal;font-size:11px;font-weight:900}
.dots i.w{background:var(--ok-s);color:var(--ok)}.dots i.l{background:var(--bad-s);color:var(--bad)}.dots i.s{background:var(--bg2);color:var(--tx3)}
.tier{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.tier .t{border:1px solid var(--bd);border-radius:12px;padding:12px;font-size:12.5px;background:var(--bg2)}
.seg{display:flex;height:22px;border-radius:7px;overflow:hidden;margin:7px 0;font-size:10.5px;font-weight:800;color:#fff}.seg i{display:grid;place-items:center;font-style:normal}
tr.win td{background:color-mix(in srgb,var(--ok-s) 55%,transparent)}tr.lose td{background:color-mix(in srgb,var(--bad-s) 55%,transparent)}

/* login */
#loginBox{min-height:100vh;display:grid;place-items:center;padding:20px;background:var(--bg2)}
.login{width:min(400px,100%);padding:30px}
</style></head><body>

<div id="loginBox" class="hide"><div class="card login">
  <div class="logo" style="width:52px;height:52px;font-size:24px;margin:0 auto 14px">P</div>
  <h2 style="text-align:center;font-size:22px">PAW TX Admin</h2>
  <p class="muted" style="text-align:center;margin-bottom:6px">Đăng nhập để quản lý key, gói và lịch sử</p>
  <label>Mật khẩu admin</label>
  <input id="pw" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')login()">
  <br><br><button class="btn pri big" onclick="login()">Đăng nhập →</button>
  <p style="text-align:center;margin-top:14px"><button class="btn sm" onclick="toggleTheme()">🌗 Đổi nền trắng / đen</button></p>
</div></div>

<div id="app" class="hide">
<header class="top"><div class="top-in">
  <div class="logo">P</div><div class="brand">PAW TX<small>ADMIN SUITE</small></div><div class="sp"></div>
  <button class="ibtn" id="thm" onclick="toggleTheme()" title="Đổi nền trắng / đen">🌙</button>
  <button class="ibtn" onclick="refreshAll()" title="Làm mới">↻</button>
  <a class="ibtn" href="/admin/logout" title="Thoát" style="text-decoration:none;color:inherit">⎋</a>
</div>
<nav class="tabs" id="tabs">
  <button class="on" data-v="ov" onclick="nav('ov')">📊 Tổng quan</button>
  <button data-v="mk" onclick="nav('mk')">🔑 Tạo key</button>
  <button data-v="kl" onclick="nav('kl')">🗂 Key</button>
  <button data-v="dh" onclick="nav('dh')">🧾 Đơn hàng</button>
  <button data-v="pkg" onclick="nav('pkg')">📦 Gói</button>
  <button data-v="pay" onclick="nav('pay')">💬 Tin nhắn đơn</button>
  <span class="sep"></span>
  <button data-v="hs_hu" onclick="nav('hs_hu')">🃏 Lịch sử Hũ</button>
  <button data-v="hs_md5" onclick="nav('hs_md5')">🧊 Lịch sử MD5</button>
  <span class="sep"></span>
  <button data-v="hd" onclick="nav('hd')">📖 API &amp; Tool</button>
</nav></header>
<main class="main">
  <div id="v-ov"></div><div id="v-mk" class="hide"></div><div id="v-kl" class="hide"></div><div id="v-dh" class="hide"></div>
  <div id="v-pkg" class="hide"></div><div id="v-pay" class="hide"></div>
  <div id="v-hs_hu" class="hide"></div><div id="v-hs_md5" class="hide"></div><div id="v-hd" class="hide"></div>
</main></div>
<div id="toast"></div>

<script>
let PKGS=[],KEYS=[],S={},TPLS={},CUR='ov',hsT={hu:null,md5:null},MK={sel:''};
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const dfmt=h=>{try{return esc(String(h).replace('T',' ').slice(0,16))}catch(e){return '—'}};
function toast(m){const t=$('toast');t.textContent=m;t.style.display='block';clearTimeout(t._h);t._h=setTimeout(()=>t.style.display='none',2600)}
function cp(t,l){const done=()=>toast('📋 Đã copy '+(l||''));
  if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(done).catch(()=>fb(t,done));else fb(t,done)}
function fb(t,done){const a=document.createElement('textarea');a.value=t;a.style.cssText='position:fixed;opacity:0';document.body.appendChild(a);a.select();try{document.execCommand('copy');done()}catch(e){toast('Không copy được')}a.remove()}
function setTheme(t){document.documentElement.dataset.theme=t;try{localStorage.setItem('paw_theme',t)}catch(e){}const b=$('thm');if(b)b.textContent=t==='dark'?'☀️':'🌙'}
function toggleTheme(){setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark')}
function modal(h){closeModal();const m=document.createElement('div');m.className='modalbg';m.id='mdl';m.innerHTML='<div class="modal">'+h+'</div>';m.onclick=e=>{if(e.target===m)closeModal()};document.body.appendChild(m)}
function closeModal(){const m=$('mdl');if(m)m.remove()}
async function api(p,o={}){const r=await fetch(p,{headers:{'Content-Type':'application/json'},credentials:'same-origin',...o});
  let j;try{j=await r.json()}catch(e){toast('Server trả mã '+r.status);throw e}
  if(r.status===401&&p.startsWith('/admin')){$('app').classList.add('hide');$('loginBox').classList.remove('hide');throw 0}return j}
const post=(p,b)=>api(p,{method:'POST',body:JSON.stringify(b||{})});

/* ── đăng nhập / điều hướng ── */
async function login(){try{const r=await fetch('/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({pw:($('pw').value||'').trim()})});
  const j=await r.json();j.ok?start():toast(j.thong_bao||'Sai mật khẩu')}catch(e){toast('Không kết nối được server')}}
function start(){$('loginBox').classList.add('hide');$('app').classList.remove('hide');setTheme(document.documentElement.dataset.theme);refreshAll()}
async function refreshAll(){await Promise.all([packages(true),settings(true)]);nav(CUR)}
function nav(v){CUR=v;document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.v===v));
  ['ov','mk','kl','dh','pkg','pay','hs_hu','hs_md5','hd'].forEach(x=>$('v-'+x).classList.toggle('hide',x!==v));
  Object.keys(hsT).forEach(c=>{clearInterval(hsT[c]);hsT[c]=null});
  ({ov:overview,mk:mkForm,kl:keys,dh:orders,pkg:packages,pay:settings,hs_hu:()=>historyUI('hu'),hs_md5:()=>historyUI('md5'),hd:hd})[v]();
  window.scrollTo({top:0})}
const stP=t=>({'hoạt động':'<span class="pill act"><span class="dot"></span>hoạt động</span>','khóa':'<span class="pill ban">khóa</span>','hết hạn':'<span class="pill exp">hết hạn</span>','chưa kích hoạt':'<span class="pill idle">chưa kích hoạt</span>'}[t]||esc(t));

/* ── 📊 Tổng quan ── */
async function overview(){let j;try{j=await api('/admin/api/overview')}catch(e){return}
 const a=j.key_admin_console||{};
 $('v-ov').innerHTML=`<div class="kpis">
  <div class="kpi"><b>${j.so_key}</b><span>🔑 key đã tạo</span></div><div class="kpi"><b>${j.dang_hoat_dong}</b><span>🟢 đang hoạt động</span></div>
  <div class="kpi"><b>${j.da_kich_hoat}</b><span>✅ đã kích hoạt</span></div><div class="kpi"><b>${j.het_han}</b><span>⏰ hết hạn</span></div>
  <div class="kpi"><b>${j.so_don_hang}</b><span>🧾 đơn hàng</span></div><div class="kpi"><b>${j.luot_goi_hu+j.luot_goi_md5}</b><span>📡 lượt gọi API</span></div></div>
 <div class="grid2">${j.ban.map(b=>`<div class="card"><div class="hs-head" style="margin:0 0 10px">
   <h2 style="margin:0">${b.code==='hu'?'🃏':'🧊'} Bàn ${esc(b.ten)}</h2><span class="kk">#${b.phien_hien_tai}</span><div class="sp"></div>
   ${b.loi?'<span class="pill ban">⚠ lỗi nguồn</span>':'<span class="pill act"><span class="dot"></span>LIVE</span>'}</div>
   <div style="display:flex;gap:14px;align-items:baseline;flex-wrap:wrap">
    ${b.du_doan_tiep?`<span class="pill ${b.du_doan_tiep==='TAI'?'tai':'xiu'}" style="font-size:14px;padding:5px 13px">Dự đoán: ${b.du_doan_tiep==='TAI'?'TÀI':'XỈU'}</span>`:''}
    <span>✅ <b>${b.thang}</b> &nbsp;❌ <b>${b.thua}</b> &nbsp;tỷ lệ <b>${b.ty_le_thang}%</b></span></div>
   <div class="bar" style="margin:10px 0 12px"><i style="width:${Math.min(100,b.ty_le_thang)}%"></i></div>
   <button class="btn sm" onclick="nav('hs_${b.code}')">Xem lịch sử bàn ${esc(b.ten)} →</button></div>`).join('')}</div>
 <div class="card"><h2>🛡️ Key admin riêng</h2><p class="muted">Token dùng cho trang history riêng của bạn (tự sinh khi server chạy lại).</p>
  <p style="margin-top:8px"><span class="kk">${esc(a.key||'')}</span> · <code>${esc(a.token||'')}</code> <button class="btn sm" onclick="cp('${esc(a.token||'')}','token')">📋 Copy</button></p></div>`}

/* ── 🔑 Tạo key ── */
const tsec=p=>((+p.days||0)*24+(+p.hours||0));
function mkForm(){
 const list=PKGS.slice().sort((a,b)=>(tsec(a)||1e9)-(tsec(b)||1e9));
 if(!MK.sel||(!['_custom','_perm'].includes(MK.sel)&&!PKGS.find(p=>p.id===MK.sel)))MK.sel=(PKGS.find(p=>p.id==='P3')||list[0]||{id:'_custom'}).id;
 const hasPerm=PKGS.some(p=>tsec(p)===0);
 $('v-mk').innerHTML=`<div class="grid2" style="align-items:start"><div>
  <div class="card"><h2>1️⃣ Chọn thời hạn</h2><p class="muted">Hạn tính từ lúc khách bấm kích hoạt trong tool.</p><br>
   <div class="opts" id="opts">
    ${list.map(p=>`<button class="opt" data-id="${p.id}" onclick="mkPick('${p.id}')"><span class="ic">${esc(p.icon||'📦')}</span><b>${esc(p.name)}</b><small>${esc(p.thoi_han)} · ${esc(p.price||'chưa đặt giá')}</small></button>`).join('')}
    ${hasPerm?'':`<button class="opt" data-id="_perm" onclick="mkPick('_perm')"><span class="ic">♾️</span><b>Vĩnh viễn</b><small>không hết hạn</small></button>`}
    <button class="opt" data-id="_custom" onclick="mkPick('_custom')"><span class="ic">✏️</span><b>Tự nhập</b><small>số ngày / số giờ</small></button></div>
   <div id="cust" class="hide" style="margin-top:14px"><div class="row">
     <div><label>Số ngày</label><input id="o_days" type="number" min="0" inputmode="numeric" placeholder="0" oninput="mkSum()"></div>
     <div><label>Số giờ</label><input id="o_hours" type="number" min="0" inputmode="numeric" placeholder="0" oninput="mkSum()"></div></div>
    <div class="quick">${[['1 giờ',0,1],['3 giờ',0,3],['6 giờ',0,6],['12 giờ',0,12],['1 ngày',1,0],['3 ngày',3,0],['7 ngày',7,0],['14 ngày',14,0],['30 ngày',30,0]].map(q=>`<button onclick="mkQ(${q[1]},${q[2]})">${q[0]}</button>`).join('')}</div></div>
   <div class="summary" id="mkSum"></div></div>
  <div class="card"><h2>2️⃣ Thông tin đơn</h2>
   <div class="row"><div><label>Số lượng key</label><input id="o_n" type="number" value="1" min="1" max="200"></div>
    <div><label>Tên khách</label><input id="o_name" placeholder="VD: Anh Tú"></div></div>
   <div class="row"><div><label>Giá (trống = theo gói)</label><input id="o_price" placeholder="VD: 250K"></div>
    <div><label>Tiền tố key</label><input id="o_pre" placeholder="${esc(S.default_prefix||'PAXU')}"></div></div>
   <label>Ghi chú nội bộ</label><input id="o_note" placeholder="Không gửi cho khách">
   <br><br><button class="btn pri big" onclick="createOrder()">🚀 Tạo key + xuất tin nhắn</button></div>
 </div><div id="o_out"><div class="card"><h2>💬 Tin nhắn gửi khách</h2><p class="muted">Tạo key xong, tin nhắn đẹp hiện ở đây — bấm copy là gửi được luôn.</p></div></div></div>`;
 mkPick(MK.sel)}
function mkPick(id){MK.sel=id;document.querySelectorAll('#opts .opt').forEach(b=>b.classList.toggle('on',b.dataset.id===id));
 $('cust').classList.toggle('hide',id!=='_custom');mkSum()}
function mkQ(d,h){$('o_days').value=d||'';$('o_hours').value=h||'';mkSum()}
function mkSum(){const el=$('mkSum');if(!el)return;let t;
 if(MK.sel==='_perm')t='♾️ Key vĩnh viễn, không hết hạn';
 else if(MK.sel==='_custom'){const d=+$('o_days').value||0,h=+$('o_hours').value||0;t=(d||h)?`⏳ Hạn dùng: ${[d?d+' ngày':'',h?h+' giờ':''].filter(Boolean).join(' ')} (tính từ lúc kích hoạt)`:'⚠️ Nhập số ngày hoặc số giờ'}
 else{const p=PKGS.find(x=>x.id===MK.sel);t=p?`📦 ${p.name} · ⏳ ${p.thoi_han} · 💰 ${p.price||'chưa đặt giá'}`:''}
 el.textContent=t}
async function createOrder(){
 const d={count:$('o_n').value||1,prefix:$('o_pre').value||undefined,name:$('o_name').value,price:$('o_price').value||undefined,note:$('o_note').value};
 if(MK.sel==='_custom'){d.days=$('o_days').value;d.hours=$('o_hours').value;if(!(+d.days||+d.hours))return toast('Nhập số ngày hoặc số giờ')}
 else if(MK.sel==='_perm')d.permanent=true;else d.package_id=MK.sel;
 let j;try{j=await post('/admin/api/keys',d)}catch(e){return}
 if(!j.ok)return toast(j.thong_bao||'Lỗi');
 window.__msgs=j.tin_nhan_thanh_toan;
 $('o_out').innerHTML=`<div class="card"><div class="hs-head" style="margin-bottom:6px"><h2 style="margin:0">✅ Đã tạo ${j.da_tao} key</h2><span class="pill idle">🧾 ${j.don_hang}</span><span class="pill idle">⏳ ${esc(j.thoi_han)}</span></div>
  ${j.tin_nhan_thanh_toan.map((t,i)=>`<div style="margin-top:12px"><div class="msg">${esc(t.tin_nhan)}</div>
   <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px"><button class="btn pri sm" onclick="cp(window.__msgs[${i}].tin_nhan,'tin nhắn')">📋 Copy tin nhắn</button>
   <button class="btn sm" onclick="cp('${t.key}','key')">🔑 Copy key</button></div></div>`).join('')}
  ${j.da_tao>1?`<br><button class="btn big" onclick="cp(window.__msgs.map(x=>x.key).join('\\n'),'danh sách key')">📋 Copy tất cả ${j.da_tao} key</button>`:''}</div>`;
 toast('✅ Đã tạo '+j.da_tao+' key')}

/* ── 🗂 Key ── */
let KF='all';
async function keys(){let j;try{j=await api('/admin/api/keys')}catch(e){return};KEYS=j.keys;
 $('v-kl').innerHTML=`<div class="card"><div class="hs-head" style="margin-bottom:10px"><h2 style="margin:0">🗂 Danh sách key (${KEYS.length})</h2><div class="sp"></div><button class="btn pri sm" onclick="nav('mk')">+ Tạo key</button></div>
  <input id="kq" placeholder="🔍 Tìm key / tên khách / mã đơn…" oninput="rk()">
  <div class="quick" id="kf">${['all','hoạt động','chưa kích hoạt','hết hạn','khóa'].map(s=>`<button data-s="${s}" onclick="KF='${s}';rk()">${s==='all'?'Tất cả':s}</button>`).join('')}</div><br>
  <div class="scroll" style="max-height:66vh"><table id="ktbl"></table></div></div>`;rk()}
function rk(){const q=($('kq')&&$('kq').value||'').toLowerCase();
 document.querySelectorAll('#kf button').forEach(b=>{b.style.background=b.dataset.s===KF?'var(--tx)':'';b.style.color=b.dataset.s===KF?'var(--bg)':''});
 const ks=KEYS.filter(k=>(KF==='all'||k.trang_thai===KF)&&(!q||(k.key+' '+k.ten+' '+k.don_hang).toLowerCase().includes(q)));
 $('ktbl').innerHTML=`<tr><th>Key</th><th>Khách</th><th>Gói · hạn</th><th>Hết hạn</th><th>TT</th><th>Gọi</th><th></th></tr>`+(ks.length?ks.map(k=>`<tr>
  <td><span class="kk">${k.key}</span></td><td><b>${esc(k.ten||'—')}</b><br><span class="muted">${esc(k.don_hang||'')}</span></td>
  <td>${esc(k.goi||'tuỳ chỉnh')}<br><span class="muted">${esc(k.thoi_han)}</span></td><td>${k.ngay_het_han?dfmt(k.ngay_het_han):(k.da_kich_hoat?'♾️':'<span class="muted">chưa tính</span>')}</td>
  <td>${stP(k.trang_thai)}</td><td>${k.luot_goi_hu}/${k.luot_goi_md5}</td>
  <td style="white-space:nowrap"><button class="btn sm" title="Copy tin nhắn" onclick="kact('${k.id}','copy')">📋</button>
   <button class="btn sm" title="${k.trang_thai==='khóa'?'Mở khóa':'Khóa'}" onclick="kact('${k.id}','${k.trang_thai==='khóa'?'mo':'khoa'}')">${k.trang_thai==='khóa'?'🔓':'🔒'}</button>
   <button class="btn sm" title="Gia hạn" onclick="kext('${k.id}')">⏫</button>
   <button class="btn sm" title="Chi tiết" onclick="kdetail('${k.id}')">⚙️</button></td></tr>`).join(''):'<tr><td colspan="7" class="muted" style="text-align:center;padding:26px">Không có key nào</td></tr>')}
async function kact(id,act){
 if(act==='copy'){const j=await post('/admin/api/keys/'+id);if(j.ok)cp(j.tin_nhan_thanh_toan,'tin nhắn');return}
 if(act==='delete'&&!confirm('Xóa key này?'))return;
 if(act==='revoke'&&!confirm('Gỡ kích hoạt: khách phải kích hoạt lại, hạn tính lại từ đầu. Tiếp tục?'))return;
 const j=act==='delete'?await post('/admin/api/keys/'+id+'/delete'):await post('/admin/api/keys/'+id,{khoa:{status:'banned'},mo:{status:'active'},revoke:{revoke_activation:true}}[act]);
 if(j.ok){toast('✔ Xong');closeModal();keys()}else toast(j.thong_bao||'Lỗi')}
function kext(id){const k=KEYS.find(x=>x.id===id);modal(`<h2>⏫ Gia hạn <span class="kk">${k.key}</span></h2><p class="muted">Hiện tại: ${esc(k.thoi_han)}${k.ngay_het_han?' · hết '+dfmt(k.ngay_het_han):''}</p>
 <div class="row"><div><label>Cộng thêm ngày</label><input id="e_d" type="number" min="0" placeholder="0"></div><div><label>Cộng thêm giờ</label><input id="e_h" type="number" min="0" placeholder="0"></div></div>
 <div class="quick">${[['+6 giờ',0,6],['+1 ngày',1,0],['+3 ngày',3,0],['+7 ngày',7,0],['+30 ngày',30,0]].map(q=>`<button onclick="$('e_d').value=${q[1]||''};$('e_h').value=${q[2]||''}">${q[0]}</button>`).join('')}</div>
 <br><button class="btn pri big" onclick="kextGo('${id}')">Gia hạn</button>`)}
async function kextGo(id){const d=+$('e_d').value||0,h=+$('e_h').value||0;if(!d&&!h)return toast('Nhập số ngày hoặc giờ');
 const j=await post('/admin/api/keys/'+id,{extend_days:d,extend_hours:h});if(j.ok){toast('✔ Đã gia hạn');closeModal();keys()}else toast(j.thong_bao||'Lỗi')}
function kdetail(id){const k=KEYS.find(x=>x.id===id);if(!k)return;
 modal(`<h2>⚙️ Key <span class="kk">${k.key}</span></h2><p style="margin:8px 0">${stP(k.trang_thai)} <span class="pill idle">💰 ${esc(k.gia||'—')}</span> <span class="pill idle">⏳ ${esc(k.thoi_han)}</span> <span class="pill idle">🧾 ${esc(k.don_hang||'—')}</span></p>
 <b style="font-size:13px">📱 Thiết bị (${k.thiet_bi.length}/${k.gioi_han_thiet_bi})</b>
 ${k.thiet_bi.length?`<div class="scroll" style="margin-top:6px"><table><tr><th>Kích hoạt</th><th>Gọi cuối</th><th>Hũ/MD5</th></tr>${k.thiet_bi.map(d=>`<tr><td>${dfmt(d.kich_hoat)}</td><td>${d.lan_cuoi_goi?dfmt(d.lan_cuoi_goi):'chưa gọi'}</td><td>${d.luot_goi_hu}/${d.luot_goi_md5}</td></tr>`).join('')}</table></div>`:'<p class="muted">Chưa có thiết bị.</p>'}
 <div class="row"><div><label>Tên khách</label><input id="kd_nm" value="${esc(k.ten)}"></div><div><label>Số thiết bị tối đa</label><input id="kd_md" type="number" value="${k.gioi_han_thiet_bi}"></div></div>
 <label>Ghi chú</label><input id="kd_nt" value="${esc(k.ghi_chu)}"><br>
 <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn pri" onclick="ksave('${k.id}')">💾 Lưu</button><button class="btn" onclick="cp('${k.key}','key')">🔑 Copy key</button>
 <button class="btn" onclick="kact('${k.id}','revoke')">♻️ Gỡ kích hoạt</button><button class="btn danger" onclick="if(confirm('Xóa key?'))kact('${k.id}','delete')">🗑 Xóa</button></div>`)}
async function ksave(id){const j=await post('/admin/api/keys/'+id,{name:$('kd_nm').value,note:$('kd_nt').value,max_devices:$('kd_md').value});if(j.ok){toast('💾 Đã lưu');closeModal();keys()}else toast(j.thong_bao||'Lỗi')}

/* ── 🧾 Đơn hàng ── */
async function orders(){let j;try{j=await api('/admin/api/orders')}catch(e){return}
 $('v-dh').innerHTML=`<div class="card"><h2>🧾 Đơn hàng (${j.tong})</h2><p class="muted">Mỗi lần tạo key là 1 đơn. Đổi trạng thái để theo dõi đã gửi / đã thu tiền.</p></div>`+
 (j.don_hang.length?j.don_hang.map(o=>`<div class="card"><div class="hs-head" style="margin-bottom:6px"><b class="kk">${o.id}</b><span class="pill idle">${esc(o.package)}</span><span class="pill idle">⏳ ${esc(o.thoi_han||'')}</span><span class="pill idle">💰 ${esc(o.price||'—')}</span>
  <div class="sp"></div><select style="width:auto;padding:6px 10px" onchange="oSet('${o.id}',this.value)">${['mới','đã gửi','đã thanh toán','huỷ'].map(s=>`<option ${o.trang_thai===s?'selected':''}>${s}</option>`).join('')}</select>
  <button class="btn sm danger" onclick="oDel('${o.id}')">🗑</button></div>
  <div class="muted">👤 ${esc(o.khach)} · ${dfmt(o.ngay_tao)}</div>
  <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">${o.keys.map(k=>`<span class="pill idle" style="cursor:pointer" onclick="cp('${k}','key')"><span class="kk">${k}</span> ${stP((o.trang_thai_thuc||{})[k]||'')}</span>`).join('')}</div></div>`).join(''):'<div class="card muted">Chưa có đơn hàng.</div>')}
async function oSet(id,s){const j=await post('/admin/api/orders/'+id,{status:s});toast(j.ok?'✔ Đã cập nhật':'Lỗi')}
async function oDel(id){if(!confirm('Xóa đơn + TOÀN BỘ key của đơn này?'))return;const j=await post('/admin/api/orders/'+id,{delete:true});if(j.ok){toast('🗑 Đã xóa');orders()}}

/* ── 📦 Gói ── */
async function packages(silent){let j;try{j=await api('/admin/api/packages');PKGS=j.packages}catch(e){return}
 if(silent)return;
 $('v-pkg').innerHTML=`<div class="card"><div class="hs-head" style="margin-bottom:8px"><h2 style="margin:0">📦 Gói dịch vụ</h2><div class="sp"></div><button class="btn pri sm" onclick="pkgForm('')">+ Thêm gói</button></div>
  <p class="muted">Giá và thời hạn ở đây tự điền vào key + tin nhắn. Hạn có thể tính theo ngày và giờ (cả 2 = 0 → vĩnh viễn).</p><br>
  <div class="scroll"><table><tr><th>Gói</th><th>Giá</th><th>Thời hạn</th><th></th></tr>
  ${PKGS.slice().sort((a,b)=>(tsec(a)||1e9)-(tsec(b)||1e9)).map(p=>`<tr><td>${esc(p.icon||'')} <b>${esc(p.name)}</b></td><td>${esc(p.price||'—')}</td><td>${esc(p.thoi_han)}</td>
  <td style="white-space:nowrap"><button class="btn sm" onclick="pkgForm('${p.id}')">✏️ Sửa</button> <button class="btn sm danger" onclick="pkgDel('${p.id}')">🗑</button></td></tr>`).join('')}</table></div></div>`}
function pkgForm(id){const p=PKGS.find(x=>x.id===id)||{id:'',icon:'✨',name:'',price:'',days:1,hours:0};
 modal(`<h2>${id?'✏️ Sửa gói':'➕ Gói mới'}</h2>
 <div class="row"><div><label>Icon</label><input id="pf_ic" value="${esc(p.icon)}"></div><div><label>Tên gói</label><input id="pf_nm" value="${esc(p.name)}" placeholder="VD: Gói 12 giờ"></div></div>
 <div class="row"><div><label>Giá</label><input id="pf_pr" value="${esc(p.price)}" placeholder="VD: 30K"></div><div><label>Số ngày</label><input id="pf_dy" type="number" min="0" value="${p.days||0}"></div><div><label>Số giờ</label><input id="pf_hr" type="number" min="0" value="${p.hours||0}"></div></div>
 <p class="muted" style="margin-top:8px">Ngày = 0 và giờ = 0 → gói vĩnh viễn.</p><br><button class="btn pri big" onclick="pkgSave('${p.id||''}')">💾 Lưu gói</button>`)}
async function pkgSave(id){const j=await post('/admin/api/packages',{id,icon:$('pf_ic').value,name:$('pf_nm').value,price:$('pf_pr').value,days:$('pf_dy').value||0,hours:$('pf_hr').value||0});
 if(j.ok){toast('💾 Đã lưu gói');closeModal();await packages(true);packages()}else toast(j.thong_bao||'Lỗi')}
async function pkgDel(id){if(!confirm('Xóa gói '+id+'?'))return;const j=await post('/admin/api/packages',{id,delete:true});if(j.ok){toast('🗑 Đã xóa');await packages(true);packages()}}

/* ── 💬 Tin nhắn đơn ── */
const DEMO={key:'PAXU-A7K3-M9ZD-2F9T',package:'Gói 3 Ngày',duration:'3 ngày',price:'250K',order:'DH260101-AB12C',name:'Anh Tú',expiry:'tính từ lúc kích hoạt (3 ngày)'};
async function settings(silent){let j;try{j=await api('/admin/api/settings');S=j.settings;TPLS=j.templates||{}}catch(e){return}
 if(silent)return;
 $('v-pay').innerHTML=`<div class="grid2" style="align-items:start"><div class="card"><h2>💬 Mẫu tin nhắn gửi khách</h2>
  <p class="muted">Bấm biến để chèn vào chỗ con trỏ.</p>
  <div class="chips">${['key','package','duration','price','name','order','expiry','tool_url','support'].map(v=>`<code onclick="insVar('{${v}}')">{${v}}</code>`).join('')}</div>
  <div class="quick"><button onclick="tpl('dep')">✨ Mẫu đẹp</button><button onclick="tpl('gon')">📨 Mẫu gọn</button><button onclick="tpl('toi_gian')">⚡ Tối giản</button></div>
  <textarea id="pay_tpl" rows="15" style="margin-top:10px">${esc(S.payment_template)}</textarea>
  <div class="row"><div><label>Link tool (khách mở để kích hoạt)</label><input id="s_tool" value="${esc(S.tool_url||'')}" placeholder="https://… link file tool HTML của bạn"></div>
  <div><label>Liên hệ hỗ trợ</label><input id="s_sup" value="${esc(S.support||'')}"></div></div>
  <div class="row"><div><label>Tiền tố key mặc định</label><input id="s_pre" value="${esc(S.default_prefix||'PAXU')}" maxlength="6"></div></div>
  <br><button class="btn pri big" onclick="saveSettings()">💾 Lưu</button></div>
  <div class="card"><h2>👀 Xem trước</h2><p class="muted">Khách demo: gói 3 ngày, 250K</p><br><div class="msg" id="pay_prev"></div><br>
   <button class="btn pri" onclick="cp($('pay_prev').textContent,'bản xem trước')">📋 Copy</button></div></div>`;
 $('pay_tpl').oninput=payPrev;$('s_tool').oninput=payPrev;$('s_sup').oninput=payPrev;payPrev()}
function tpl(n){if(TPLS[n]){$('pay_tpl').value=TPLS[n];payPrev()}}
function insVar(v){const t=$('pay_tpl'),a=t.selectionStart,b=t.selectionEnd;t.value=t.value.slice(0,a)+v+t.value.slice(b);t.focus();t.selectionStart=t.selectionEnd=a+v.length;payPrev()}
function payPrev(){const v={...DEMO,tool_url:$('s_tool').value||'(link tool — admin gửi riêng)',support:$('s_sup').value||'—'};
 $('pay_prev').textContent=$('pay_tpl').value.replace(/\{(\w+)\}/g,(m,k)=>v[k]??m)}
async function saveSettings(){const j=await post('/admin/api/settings',{payment_template:$('pay_tpl').value,tool_url:$('s_tool').value,support:$('s_sup').value,default_prefix:$('s_pre').value});
 if(j.ok){S=j.settings;toast('💾 Đã lưu')}else toast(j.thong_bao||'Lỗi')}

/* ── 🃏🧊 LỊCH SỬ — mỗi bàn 1 trang riêng ── */
const TB={hu:{ic:'🃏',c:'Hũ'},md5:{ic:'🧊',c:'MD5'}};
async function historyUI(code){let j;try{j=await api('/admin/api/history/'+code+'?limit=50')}catch(e){return}
 const el=$('v-hs_'+code);if(!el)return;
 const pa=j.phan_tich_cau||{},hh=j.phien_hien_tai||{},ph=j.phien_truoc||{},li=j.lich_su||[],st=j.thong_ke||{win:0,lose:0,skip:0,ty_le:0};
 const lbl=s=>s==='TAI'?'TÀI':s==='XIU'?'XỈU':(s||'—');
 el.innerHTML=`<div class="hs-head"><span style="font-size:28px">${TB[code].ic}</span><div class="hs-title">Bàn ${esc(j.ban)}</div><span class="pill act"><span class="dot"></span>TỰ CẬP NHẬT 5s</span>${j.che_do_cau&&j.che_do_cau!=='—'?`<span class="pill idle">cầu ${esc(j.che_do_cau)}</span>`:''}<div class="sp"></div><button class="btn sm" onclick="historyUI('${code}')">↻ Làm mới</button></div>
 <div class="totals"><div class="tot w"><b>${st.win}</b><span>Tổng thắng</span></div><div class="tot l"><b>${st.lose}</b><span>Tổng thua</span></div><div class="tot r"><b>${st.ty_le}%</b><span>Tỷ lệ thắng</span></div></div>
 <div class="muted" style="margin:-4px 0 12px;text-align:center">Tính trên ${li.length} phiên gần nhất của riêng bàn ${esc(j.ban)}${st.skip?` · bỏ qua ${st.skip}`:''}</div>
 ${hh.du_doan?`<div class="card"><div class="pred"><div><div class="muted" style="font-weight:800;letter-spacing:.1em">DỰ ĐOÁN PHIÊN #${hh.phien}</div><div class="big ${hh.du_doan}">${lbl(hh.du_doan)}</div></div>
  <div style="flex:1;min-width:200px"><div class="muted" style="font-weight:800">ĐỘ TIN CẬY ${hh.do_tin_cay||'—'}%</div><div class="bar" style="margin:6px 0 10px"><i style="width:${Math.min(100,Math.max(4,((hh.do_tin_cay||50)-40)*3.5))}%"></i></div>
  <div class="muted">🧵 Chuỗi cầu: <b style="color:var(--tx)">${esc(hh.cau||'—')}</b></div>
  <div class="muted">${ph.icon||''} Phiên trước #${ph.phien||'—'}: dự đoán ${lbl(ph.du_doan)} → ra ${lbl(ph.ket_qua)}</div></div></div></div>`:''}
 <div class="card"><b style="font-size:13px">Chuỗi ${Math.min(30,li.length)} phiên gần nhất</b> <span class="muted">(mới nhất bên trái)</span><div class="dots" style="margin-top:8px">${li.slice(0,30).map(h=>`<i class="${h.trang_thai==='win'?'w':h.trang_thai==='lose'?'l':'s'}" title="#${h.phien}">${h.trang_thai==='win'?'✓':h.trang_thai==='lose'?'✗':'·'}</i>`).join('')}</div></div>
 ${pa.da_du_du_lieu?`<div class="card"><h2>🔎 Phân tích cầu</h2><div class="tier" style="margin-top:8px">
  ${[['⚡ Ngắn hạn','ngan'],['🌀 Trung hạn','trung'],['🌊 Dài hạn','dai']].map(([n,k])=>`<div class="t"><b>${n} · ${pa[k].so_phien} phiên</b><div class="seg"><i style="background:#e11d48;flex:${pa[k].tai||.01}">${pa[k].tai}T</i><i style="background:#0284c7;flex:${pa[k].xiu||.01}">${pa[k].xiu}X</i></div>👉 <b>${esc(pa[k].huong)}</b> (lệch ${pa[k].lech})</div>`).join('')}
  <div class="t"><b>🎯 Đánh giá cầu</b><br>Dạng ${esc(pa.dang_cau)} · ${esc(pa.phan_loai)}<br>Run: <b>${pa.run_hien_tai.ben} ×${pa.run_hien_tai.do_dai}</b> · P(gãy) <b>${pa.p_gay_run}</b><br>Khuyến nghị: <span class="pill ${pa.khuyen_nghi==='BẺ'?'exp':pa.khuyen_nghi==='THEO'?'act':'idle'}">${esc(pa.khuyen_nghi)}</span></div></div></div>`:''}
 <div class="card"><h2>📋 Biên bản từng phiên — bàn ${esc(j.ban)}</h2><div class="scroll" style="margin-top:10px;max-height:560px"><table><tr><th>Phiên</th><th>Dự đoán</th><th>Xúc xắc</th><th>Tổng</th><th>Kết quả</th><th>Kết</th></tr>
 ${li.length?li.map(h=>`<tr class="${h.trang_thai}"><td><span class="kk">#${h.phien}</span></td><td>${h.du_doan?`<span class="pill ${h.du_doan==='TAI'?'tai':'xiu'}">${lbl(h.du_doan)}</span>`:'—'}</td><td class="kk">${(h.xuc_xac||[]).join(' · ')||'—'}</td><td><b>${h.tong??'—'}</b></td>
 <td>${h.ket_qua?`<span class="pill ${h.ket_qua==='TAI'?'tai':'xiu'}">${lbl(h.ket_qua)}</span>`:'—'}</td><td style="font-size:16px">${h.icon||''}</td></tr>`).join(''):'<tr><td colspan="6" class="muted" style="text-align:center;padding:26px">Chưa có phiên nào được ghi</td></tr>'}</table></div></div>`;
 if(!hsT[code])hsT[code]=setInterval(()=>{if(CUR==='hs_'+code)historyUI(code)},5000)}

/* ── 📖 API & Tool ── */
async function hd(){let d;try{d=await api('/huong-dan')}catch(e){return}
 const B=d.buoc_1_kich_hoat_key.url.replace(/\/makey$/,'');
 $('v-hd').innerHTML=`<div class="card"><h2>🔁 Luồng bán key → khách dùng tool</h2><br>
  <div class="tier"><div class="t"><b>1️⃣ Admin tạo key</b><br>Tab 🔑 Tạo key → chọn gói hoặc nhập ngày/giờ → copy tin nhắn gửi khách.</div>
  <div class="t"><b>2️⃣ Khách mở tool</b><br>Dán key vào ô KÍCH HOẠT. Tool gọi <code>POST /makey</code> → nhận token, hạn tính từ lúc này.</div>
  <div class="t"><b>3️⃣ Tool lấy dự đoán</b><br>Mỗi 4s gọi <code>GET /api/&lt;token&gt;/hu</code> và <code>/md5</code> kèm header <code>X-Device-ID</code>.</div></div></div>
 <div class="card"><h2>🔗 Endpoint</h2><div class="msg" style="margin-top:8px;font-family:var(--mono);font-size:12.5px">Kích hoạt:  POST ${B}/makey   {"key":"PAXU-XXXX-XXXX-XXXX"}
Dự đoán Hũ:  GET ${B}/api/&lt;TOKEN&gt;/hu
Dự đoán MD5: GET ${B}/api/&lt;TOKEN&gt;/md5
Lịch sử:     GET ${B}/api/&lt;TOKEN&gt;/history/hu · /md5
Header bắt buộc khi gọi dự đoán: X-Device-ID</div>
 <br><button class="btn" onclick="cp('${B}','URL gốc')">📋 Copy URL gốc</button></div>`}

(async()=>{setTheme(document.documentElement.dataset.theme);
 try{const r=await fetch('/admin/api/overview',{credentials:'same-origin'});if(r.status===200)return start()}catch(e){}
 $('loginBox').classList.remove('hide')})();
</script></body></html>
"""

@app.route("/admin", methods=["GET"])
def admin_page():
    r = make_response(ADMIN_HTML, 200)
    r.headers["Content-Type"] = "text/html; charset=utf-8"; r.headers["Cache-Control"] = "no-store"
    return r

app.add_url_rule("/admin/makey", endpoint="makey_alias", view_func=makey, methods=["GET", "POST"])
app.add_url_rule("/admin/api/<token>/<code>", endpoint="api_predict_alias", view_func=api_predict, methods=["GET", "OPTIONS"])
app.add_url_rule("/admin/api/<token>/history/<code>", endpoint="api_history_alias", view_func=api_history, methods=["GET"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)
