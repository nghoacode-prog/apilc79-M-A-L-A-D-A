# -*- coding: utf-8 -*-
"""
PAW TX API v7 — PRO EDITION (Gói + Đơn hàng + Key SLL + Devices)
════════════════════════════════════════════════════════════════════════════════
• API dự đoán (Hũ + MD5) chỉ dùng được SAU khi kích hoạt key tại /makey
• Hệ thống GÓI (ngày/tuần/tháng...), ĐƠN HÀNG, tạo key SLL có đơn hàng đẹp
• Mỗi key gắn thiết bị (device) khi kích hoạt — admin xem info đầy đủ
• Render free: /tmp + backup cloud Gist (GIST_TOKEN + GIST_ID) → không mất key
• Engine 84 model + tầng phân tích cầu NGẮN / TRUNG / DÀI + bộ ổn định dài hạn
• v7: ĐA KHUNG CẦU 2→50 PHIÊN (15 khung quét song song, hợp nhất thành expert
  MULTIW) · CHỈNH GIÁ GÓI TRỰC TIẾP /admin/api/packages/<id>/price + bảng sửa
  giá trong tab Bán key · 26 mẫu tin nhắn thanh toán đẹp cho Telegram
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
             "luot_goi_md5": d.get("calls_md5", 0), "mo_ta": d.get("ua", ""),
             "da_gan": bool(d.get("device_id"))}
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

def req_device_id():
    """Mã thiết bị: header X-Device-ID (ưu tiên) hoặc ?device= (dự phòng khi mạng chặn header lạ)."""
    return (request.headers.get("X-Device-ID") or request.args.get("device") or "").strip()

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
    if not bound or (device_id.startswith("pw_") and not str(bound).startswith("pw_")):
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

@app.before_request
def cors_preflight():
    """Preflight (OPTIONS) PHẢI trả 204 ngay, không qua kiểm tra key/device.
    Trước đây OPTIONS đi vào api_predict → thiếu X-Device-ID → 401/403 → trình duyệt
    báo 'server chặn header X-Device-ID (CORS)'."""
    if request.method == "OPTIONS":
        return make_response("", 204)

@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    req_h = request.headers.get("Access-Control-Request-Headers", "")
    base_h = "Content-Type, Accept, X-Requested-With, X-Device-ID, Authorization"
    resp.headers["Access-Control-Allow-Headers"] = (base_h + ", " + req_h) if req_h else base_h
    resp.headers["Access-Control-Expose-Headers"] = "Content-Type"
    resp.headers["Access-Control-Max-Age"]        = "86400"
    resp.headers["Access-Control-Allow-Private-Network"] = "true"
    resp.headers["Vary"] = "Origin, Access-Control-Request-Headers"
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
    EXPERTS = ("HAZARD", "RUNMIRROR", "MOMENTUM", "CTX", "MULTIW", "ENGINE84")
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
        # 5) MULTIW: đồng thuận đa khung 2 → 50 phiên (quét 15 khung)
        try:
            _pw, _tagw, _mwrows = cau_multi_consensus(seq)
        except Exception:
            _pw, _tagw, _mwrows = 0.5, "chưa đủ dữ liệu", []
        out["MULTIW"] = (_clamp(_pw, 0.30, 0.70), _tagw)
        return out, alt, _mwrows

    def predict(self) -> Dict:
        base = Engine84.predict(self)
        seq = list(self.seq)
        base["expert_sides"] = {}; base["regime"] = "—"
        if len(seq) < 12:
            return base
        last, rlen = _last_run(seq)
        ex, alt, mw_rows = self._experts(seq, last, rlen)
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
        top = sorted(self.EXPERTS, key=lambda n: -weights[n])[:4]
        det = "; ".join(f"[{n} {weights[n]:.0%}] {ex[n][1]}" for n in top)
        _mw_t = sum(1 for _r in mw_rows if _r["p_tai"] >= 0.53)
        _mw_x = sum(1 for _r in mw_rows if _r["p_tai"] <= 0.47)
        base.update({
            "side": pred, "confidence": conf, "p_tai": p_out,
            "reasoning": (f"{pred} {conf}% | cầu {regime} · bệt {rlen} {last} | {det} | "
                          f"đa khung 2→50p: TÀI {_mw_t}/{len(mw_rows)} · XỈU {_mw_x}/{len(mw_rows)}"),
            "khung_da_phien": mw_rows,
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
            "khung_da_phien": raw.get("khung_da_phien", []),
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
TPL_HOADON = (
    "🧾 HOÁ ĐƠN ĐIỆN TỬ\n"
    "┌─────────────────────\n"
    "│ Mã đơn   : {order}\n"
    "│ Khách    : {name}\n"
    "│ Gói      : {package}\n"
    "│ Thời hạn : {duration}\n"
    "│ Thanh toán: {price}\n"
    "├─────────────────────\n"
    "│ 🔑 KEY: {key}\n"
    "└─────────────────────\n"
    "✅ ĐÃ THANH TOÁN · Cảm ơn {name}!\n\n"
    "👉 Kích hoạt: {tool_url}\n"
    "🆘 Hỗ trợ: {support}")
TPL_VIP = (
    "╔══════════════════╗\n"
    "   👑  PAW VIP ACCESS  👑\n"
    "╚══════════════════╝\n"
    "Chào {name}, đơn {order} đã xác nhận ✅\n\n"
    "🔑  {key}\n\n"
    "💎 Gói: {package}\n"
    "⏳ Hạn dùng: {duration}\n"
    "💰 Đã thanh toán: {price}\n\n"
    "▸ Mở tool → dán key → bấm KÍCH HOẠT\n"
    "▸ Link: {tool_url}\n"
    "▸ CSKH: {support}")
TPL_THAN_THIEN = (
    "Dạ em gửi {name} key nè 🥰\n\n"
    "🔑 {key}\n"
    "📦 {package} · {duration}\n\n"
    "Cách dùng: mở {tool_url} rồi dán key vào ô KÍCH HOẠT là chạy luôn ạ 🍀\n"
    "Có gì cứ nhắn em: {support} 💙")
TPL_NEON = (
    "⚡️ ━━━ PAW · KEY MỚI ━━━ ⚡️\n"
    "👤 {name}\n"
    "🔑 {key}\n"
    "▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
    "📦 {package}\n"
    "⏱ {duration}\n"
    "💳 {price}\n"
    "🧾 {order}\n"
    "▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
    "🚀 Kích hoạt: {tool_url}\n"
    "💬 {support}")
TPL_HUONG_DAN = (
    "✅ THANH TOÁN THÀNH CÔNG — {order}\n\n"
    "Cảm ơn {name}! Key của bạn:\n"
    "🔑 {key}\n\n"
    "📋 THÔNG TIN\n"
    "• Gói: {package}\n"
    "• Thời hạn: {duration}\n"
    "• Thanh toán: {price}\n\n"
    "📲 HƯỚNG DẪN\n"
    "1. Mở {tool_url}\n"
    "2. Dán key vào ô KÍCH HOẠT\n"
    "3. Bấm KÍCH HOẠT, chờ vào game\n\n"
    "⚠️ LƯU Ý\n"
    "• 1 key chỉ dùng cho 1 thiết bị\n"
    "• Hạn tính từ lúc kích hoạt\n"
    "• Không chia sẻ key cho người khác\n\n"
    "🆘 Hỗ trợ: {support}")
TPL_BAO_HANH = (
    "🎉 KEY CỦA {name} ĐÂY!\n"
    "🔑 {key}\n"
    "━━━━━━━━━━━━━━\n"
    "📦 {package} ({duration})\n"
    "🛡 Bảo hành trong suốt thời hạn gói\n"
    "🔁 Đổi thiết bị: nhắn {support}\n"
    "━━━━━━━━━━━━━━\n"
    "👉 {tool_url}")
TPL_DONG = "🔑 {key} | 📦 {package} | ⏳ {duration} | 💰 {price} | 🧾 {order} | 👉 {tool_url}"
TPL_TRANG_TRONG = (
    "Thông tin key — {order}\n"
    "—\n"
    "Khách hàng: {name}\n"
    "Key: {key}\n"
    "Gói: {package}\n"
    "Thời hạn: {duration}\n"
    "Giá: {price}\n"
    "—\n"
    "Kích hoạt tại {tool_url}\n"
    "Hỗ trợ: {support}")
TPL_CAM_ON = (
    "💙 CẢM ƠN {name} ĐÃ TIN TƯỞNG PAW 💙\n\n"
    "Đơn {order} đã thanh toán thành công ✅\n"
    "━━━━━━━━━━━━━━━━\n"
    "🔑 {key}\n"
    "📦 {package} · ⏳ {duration}\n"
    "━━━━━━━━━━━━━━━━\n"
    "1️⃣ {tool_url}\n"
    "2️⃣ Dán key → KÍCH HOẠT\n"
    "3️⃣ Vào game, chúc {name} nhiều may mắn 🍀\n\n"
    "🆘 {support}")
# ── 14 MẪU MỚI · KHUNG KÝ HIỆU ĐẸP CHO TELEGRAM ──────────────────────────────
TPL_ROYAL = (
    "┏━━━━━━━━━━━━━━━━━━┓\n"
    "  👑 PAW · ROYAL ACCESS 👑\n"
    "┗━━━━━━━━━━━━━━━━━━┛\n"
    "👤 Khách : {name}\n"
    "🧾 Đơn   : {order}\n"
    "─────────────────\n"
    "🔑 KEY · {key}\n"
    "💎 Gói · {package}\n"
    "⏳ Hạn · {duration}\n"
    "💰 TT · {price}\n"
    "─────────────────\n"
    "▸ Kích hoạt: {tool_url}\n"
    "▸ Hỗ trợ  : {support}\n"
    "« Trân trọng cảm ơn quý khách! »")
TPL_SA0 = (
    "★━━━━━━━━━━━━━━━━━━★\n"
    "  ⭐ PAW · KEY ĐƯỢC CHẤP NHẬN ⭐\n"
    "★━━━━━━━━━━━━━━━━━━★\n"
    "Cảm ơn {name} đã thanh toán ✅\n\n"
    "🔑 Key: {key}\n"
    "📦 {package} · ⏳ {duration} · 💰 {price}\n"
    "🧾 {order}\n\n"
    "★━━━━━━━━━━━━━━━━━━★\n"
    "📲 Kích hoạt: {tool_url}\n"
    "🆘 Hỗ trợ: {support}")
TPL_DIAMOND = (
    "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆\n"
    "      💎 PAW DIAMOND 💎\n"
    "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆\n"
    "👤 {name} · 🧾 {order}\n\n"
    "🔑 KEY: {key}\n\n"
    "💎 Gói: {package}\n"
    "⏱ Thời hạn: {duration}\n"
    "💵 Thanh toán: {price}\n\n"
    "◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆◇◆\n"
    "👉 Kích hoạt ngay: {tool_url}\n"
    "📞 Hỗ trợ: {support}")
TPL_HOT = (
    "🔥🔥🔥 PAW HOT DEAL 🔥🔥🔥\n"
    "╔══════════════════════╗\n"
    "👤 Khách: {name}\n"
    "🧾 Đơn: {order}\n"
    "🔑 KEY: {key}\n"
    "📦 Gói: {package}\n"
    "⏳ Hạn: {duration}\n"
    "💰 TT: {price}\n"
    "╚══════════════════════╝\n"
    "⚡ Vào {tool_url} dán key là cháy 🔥\n"
    "💬 Hỗ trợ 24/7: {support}")
TPL_TIM = (
    "💖 ───────────────── 💖\n"
    "   CẢM ƠN {name} ĐÃ ỦNG HỘ\n"
    "💖 ───────────────── 💖\n"
    "🔑 {key}\n"
    "📦 {package} · ⏳ {duration}\n"
    "💰 {price} · 🧾 {order}\n"
    "💖 ───────────────── 💖\n"
    "👉 Kích hoạt: {tool_url}\n"
    "💙 Hỗ trợ: {support}")
TPL_CAFE = (
    "☕ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ☕\n"
    "Dạ chào {name}, đơn {order} đã xong nha ✅\n\n"
    "🔑 {key}\n\n"
    "☕ Gói {package} dùng {duration}, giá {price}\n"
    "☕ Mở {tool_url} dán key là dùng được liền\n"
    "Có gì cần hỗ trợ cứ nhắn: {support}")
TPL_MATRIX = (
    "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
    "  ▌ PAW · ACCESS KEY ▐\n"
    "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟\n"
    "┃ 👤 {name}\n"
    "┃ 🧾 {order}\n"
    "┣━━━━━━━━━━━━━━\n"
    "┃ 🔑 {key}\n"
    "┣━━━━━━━━━━━━━━\n"
    "┃ 📦 {package}\n"
    "┃ ⏱ {duration}\n"
    "┃ 💳 {price}\n"
    "▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜\n"
    "┃ ▶ {tool_url}\n"
    "┃ ✆ {support}\n"
    "▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟")
TPL_KHOI = (
    "▁▂▃▄▅▆▇█ THÀNH CÔNG █▇▆▅▄▃▂▁\n"
    "✅ Đơn {order} · Khách {name}\n\n"
    "🔑 KEY: {key}\n"
    "📦 {package} | ⏳ {duration} | 💰 {price}\n\n"
    "▁▂▃▄▅▆▇█ PAW TX █▇▆▅▄▃▂▁\n"
    "📲 {tool_url}\n"
    "🆘 {support}")
TPL_XANH = (
    "🌿••••••••••••••••••🌿\n"
    "     HOÁ ĐƠN XANH · PAW\n"
    "🌿••••••••••••••••••🌿\n"
    "🌱 Khách: {name}\n"
    "🌱 Đơn: {order}\n"
    "━━━━━━━━━━━━━━━━\n"
    "🔑 {key}\n"
    "🌿 {package} · {duration}\n"
    "💸 {price}\n"
    "━━━━━━━━━━━━━━━━\n"
    "🍀 Kích hoạt: {tool_url}\n"
    "🌿 Hỗ trợ: {support}")
TPL_VUONG = (
    "⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢\n"
    "   ✔ PAW · KEY ACTIVE\n"
    "⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢\n"
    "▪️ Khách : {name}\n"
    "▪️ Đơn   : {order}\n"
    "▪️ Key   : {key}\n"
    "▪️ Gói   : {package}\n"
    "▪️ Hạn   : {duration}\n"
    "▪️ TT    : {price}\n"
    "⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢\n"
    "▶ {tool_url}\n"
    "☎ {support}")
TPL_SONG = (
    "~~~~ 🌊 PAW · TÍN HIỆU ĐÃ GỬI 🌊 ~~~~\n"
    "{name} ơi, key của đơn {order} đây nè:\n\n"
    "🔑 {key}\n\n"
    "🌊 Gói: {package}\n"
    "🌊 Thời hạn: {duration}\n"
    "🌊 Thanh toán: {price}\n\n"
    "~~~~ 🌊 ~~~~~ 🌊 ~~~~~ 🌊 ~~~~\n"
    "Kích hoạt tại: {tool_url}\n"
    "Hỗ trợ: {support}")
TPL_MEO = (
    " /(˶ᵔᵕᵔ˶)/ \n"
    "🐾 KEY CỦA {name} NÈ 🐾\n"
    "♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥\n"
    "🔑 {key}\n"
    "📦 {package} · ⏳ {duration}\n"
    "💰 {price} · 🧾 {order}\n"
    "♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥\n"
    "Vào {tool_url} dán key là xong nha 🐾\n"
    "Gặp gì khó cứ hú em: {support} 💬")
TPL_GALAXY = (
    "✦•┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈✦\n"
    "      🌌 GALAXY KEY 🌌\n"
    "✦•┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈✦\n"
    "Hi {name} 🌠 đơn {order} đã confirm!\n\n"
    "🔑 {key}\n\n"
    "━━━━━━━━━━━━━━\n"
    "💾 Gói : {package}\n"
    "⌛ Hạn : {duration}\n"
    "💳 TT  : {price}\n"
    "━━━━━━━━━━━━━━\n"
    "🚀 Kích hoạt: {tool_url}\n"
    "🛰 CSKH: {support}")
TPL_VUONG2 = (
    "╔═════════════════.*.🌙\n"
    "   PAW · BIÊN LAI CHÍNH THỨC\n"
    "🌙.*.═════════════════╗\n"
    "║ Mã đơn    : {order}\n"
    "║ Khách     : {name}\n"
    "║ Gói       : {package}\n"
    "║ Thời hạn  : {duration}\n"
    "║ Thanh toán: {price}\n"
    "╟───────────────────\n"
    "║ 🔑 {key}\n"
    "╚═════════════════.*.\n"
    "✅ ĐÃ XÁC NHẬN THANH TOÁN\n"
    "👉 {tool_url}\n"
    "☎ {support}")
TEMPLATES = {"dep": TPL_PRETTY, "hoadon": TPL_HOADON, "vip": TPL_VIP, "neon": TPL_NEON,
             "huongdan": TPL_HUONG_DAN, "camon": TPL_CAM_ON, "thanthien": TPL_THAN_THIEN,
             "baohanh": TPL_BAO_HANH, "royal": TPL_ROYAL, "sao": TPL_SA0,
             "kimcuong": TPL_DIAMOND, "nong": TPL_HOT, "tim": TPL_TIM, "cafe": TPL_CAFE,
             "matrix": TPL_MATRIX, "khoiluong": TPL_KHOI, "xanh": TPL_XANH,
             "vuong": TPL_VUONG, "song": TPL_SONG, "meo": TPL_MEO, "galaxy": TPL_GALAXY,
             "bienlai": TPL_VUONG2, "gon": TPL_SHORT, "dong": TPL_DONG,
             "trang": TPL_TRANG_TRONG, "toi_gian": TPL_MIN}
TEMPLATE_NAMES = {"dep": "✨ Đẹp (mặc định)", "hoadon": "🧾 Hoá đơn", "vip": "👑 VIP khung", "neon": "⚡ Neon",
                  "huongdan": "📋 Đầy đủ hướng dẫn", "camon": "💙 Cảm ơn", "thanthien": "🥰 Thân thiện",
                  "baohanh": "🛡 Bảo hành", "royal": "👑 Royal", "sao": "⭐ Sao",
                  "kimcuong": "💎 Kim cương", "nong": "🔥 Nóng", "tim": "💖 Thương yêu",
                  "cafe": "☕ Nhẹ nhàng", "matrix": "🟩 Ma trận", "khoiluong": "▅ Khối",
                  "xanh": "🌿 Tươi mát", "vuong": "⬜ Lục giác", "song": "🌊 Sóng",
                  "meo": "🐱 Dễ thương", "galaxy": "🌌 Galaxy", "bienlai": "🌙 Biên lai năm",
                  "gon": "📨 Gọn", "dong": "➖ 1 dòng",
                  "trang": "📄 Trang nhã", "toi_gian": "⚡ Tối giản"}
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

# ── ĐỌC CẦU ĐA KHUNG 2 → 50 PHIÊN ─────────────────────────────────────────────
# Quét 15 khung phiên: 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 50.
# Mỗi khung chấm một p_tai riêng:
#   • lệch mạnh  → nghiêng ĐẢO CHIỀU (mean reversion), khung ngắn phản ứng nhanh
#   • lệch yếu   → theo nhịp hiện tại (lười bẻ khi cầu chưa rõ)
# rồi hợp nhất có trọng số (khung lệch mạnh tiếng nói to hơn) → 1 tín hiệu
# MULTIW đưa vào bếp ensemble chung với HAZARD / RUNMIRROR / MOMENTUM / CTX.
CAU_WINDOWS = (2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 50)

def cau_multi_consensus(seq, windows=CAU_WINDOWS):
    """Hợp nhất dự báo từ 15 khung phiên 2→50.
    Trả về (p_tai_hop_nhat, mo_ta_ngan, bang_chi_tiet_tung_khung)."""
    rows = []
    s_p = s_w = 0.0
    for w in windows:
        z = _zone_window(seq, w)
        n = z["so_phien"]
        if n < max(6, w // 2):
            continue                        # khung cần đủ nửa mẫu mới đáng tin
        f = max(0.15, 0.8 - w * 0.012)      # khung càng ngắn phản ứng càng nhanh
        if z["do_manh"] >= 0.22:
            p = 0.5 - z["lech"] * f         # lệch nặng → nghiêng đảo chiều
            goc = "đảo"
        else:
            p = 0.5 + (0.05 if (n and seq and seq[-1] == "TAI") else -0.05)
            goc = "theo"                    # lệch yếu → theo nhịp hiện tại
        p = _clamp(p, 0.34, 0.66)
        ws = 0.5 + z["do_manh"]             # trọng số: khung lệch mạnh tin hơn
        rows.append({"khung": w, "so_phien": n, "tai": z["tai"], "xiu": z["xiu"],
                     "lech": z["lech"], "huong": z["huong"], "do_manh": z["do_manh"],
                     "goc": goc, "p_tai": round(p, 3)})
        s_p += p * ws; s_w += ws
    if not rows:
        return 0.5, "chưa đủ dữ liệu", []
    p_out = s_p / s_w
    tai_c = sum(1 for r in rows if r["p_tai"] >= 0.53)
    xiu_c = sum(1 for r in rows if r["p_tai"] <= 0.47)
    tag = (f"đa khung {rows[0]['khung']}-{rows[-1]['khung']}p: "
           f"TÀI {tai_c} · XỈU {xiu_c} · trung tính {len(rows)-tai_c-xiu_c} → nghiêng {p_out:.0%}")
    return p_out, tag, rows

def analyze_cau(seq):
    """Phân tầng cầu NGẮN (3-5 phiên) / TRUNG (6-15) / DÀI (>15)
    + BẢNG ĐA KHUNG 2→50 phiên + nhận dạng + khuyến nghị."""
    if len(seq) < 5:
        return {"da_du_du_lieu": False, "khung_da_phien": []}
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
    # Đa khung 2 → 50 phiên
    mw_p, mw_tag, mw_rows = cau_multi_consensus(seq)
    dong_thuan = {
        "tai":    sum(1 for r in mw_rows if r["p_tai"] >= 0.53),
        "xiu":    sum(1 for r in mw_rows if r["p_tai"] <= 0.47),
        "trung_tinh": sum(1 for r in mw_rows if 0.47 < r["p_tai"] < 0.53),
        "tong_khung": len(mw_rows),
        "mo_ta": mw_tag,
    }
    return {"da_du_du_lieu": True, "dang_cau": cau_prefix, "phan_loai": loai,
            "run_hien_tai": {"ben": last, "do_dai": rlen},
            "ngan": ngan, "trung": trung, "dai": dai,
            "khung_da_phien": mw_rows, "dong_thuan_da_khung": dong_thuan,
            "p_tai_da_khung": round(mw_p, 3),
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
    ip = (request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr or "0.0.0.0")
    if not _ratelimit(ip):
        return out({"ok": False, "loi": "rate_limited", "thong_bao": "Thử quá nhiều lần, chờ 10 phút"}, 429)
    j = request.get_json(silent=True) or {}
    key = (j.get("key") or request.form.get("key") or request.args.get("key") or "").strip().upper()
    dev_name = (j.get("device") or request.args.get("device") or "").strip()[:40]
    dev_id = (j.get("device_id") or request.headers.get("X-Device-ID") or "").strip()[:80]
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
            if dev_id: k["devices"][k["token"]]["device_id"] = dev_id
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
    dev_ok, dev_msg = device_check(k, token, req_device_id())
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
    dev_ok, dev_msg = device_check(k, token, req_device_id())
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
    return out({"ok": True, "api": "PAW TX v7 PRO — Đa khung 2→50p + Gói + Đơn hàng + Engine 84 + 26 mẫu tin nhắn",
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

# ── Chỉnh giá gói TRỰC TIẾP ──
@app.post("/admin/api/packages/<pid>/price")
def adm_pkg_price(pid):
    """Sửa giá của 1 gói ngay lập tức, không cần đụng tới thông tin khác.
    Body: {"price": "250K", "sync_keys": true}
    • sync_keys: đồng bộ giá mới sang những key CHƯA kích hoạt đang gắn gói này
      (key đã kích hoạt giữ nguyên giá đã bán).
    """
    g = guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    pid = (pid or "").strip().upper()
    p = STORE["packages"].get(pid)
    if not p:
        return out({"ok": False, "thong_bao": "Không tìm thấy gói " + pid}, 404)
    price = str(d.get("price", "")).strip()
    if price == "":
        return out({"ok": False, "thong_bao": "Thiếu giá mới (VD: 250K)"}, 400)
    p["price"] = price
    synced = 0
    if d.get("sync_keys"):
        for k in STORE["keys"].values():
            if k.get("role") != "admin" and k.get("package_id") == pid and not k.get("activated"):
                k["price"] = price; synced += 1
    save_store()
    p["thoi_han"] = _dur_text(_pkg_sec(p))
    msg = "Đã cập nhật giá gói %s → %s" % (pid, price) + (" · đồng bộ %d key chưa kích hoạt" % synced if synced else "")
    return out({"ok": True, "package": p, "synced_keys": synced, "thong_bao": msg})

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
            if d.get("reset_device"):
                for _dv in (k.get("devices") or {}).values(): _dv["device_id"] = None
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
    return out({"ok": True, "settings": st, "templates": TEMPLATES, "template_names": TEMPLATE_NAMES})

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
<meta name="theme-color" content="#0b0d14">
<title>PAW · Admin</title>
<script>try{var t=localStorage.getItem('paw_theme')||'dark';document.documentElement.dataset.theme=t}catch(e){document.documentElement.dataset.theme='dark'}</script>
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
:root{--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;--r:16px}
[data-theme=dark]{--bg:#07080d;--s1:#0e1018;--s2:#151823;--s3:#1c2030;--bd:#232838;--tx:#eef0f7;--tx2:#a2a9c0;--tx3:#666e88;--pri:#7c8cff;--pri2:#5b6cff;--pris:rgba(124,140,255,.14);--ok:#35e0a1;--oks:rgba(53,224,161,.13);--bad:#ff6b81;--bads:rgba(255,107,129,.13);--warn:#ffc247;--warns:rgba(255,194,71,.13);--tai:#ff5d77;--xiu:#35c0ff;color-scheme:dark}
[data-theme=light]{--bg:#f2f4fa;--s1:#fff;--s2:#f5f6fb;--s3:#eaedf6;--bd:#e0e4f0;--tx:#12162a;--tx2:#52597a;--tx3:#8a91ad;--pri:#4457ff;--pri2:#2f42f0;--pris:rgba(68,87,255,.1);--ok:#0f9d6b;--oks:rgba(15,157,107,.12);--bad:#e0334f;--bads:rgba(224,51,79,.1);--warn:#b87400;--warns:rgba(184,116,0,.12);--tai:#e0334f;--xiu:#0a84c6;color-scheme:light}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--tx);font:14px/1.5 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;min-height:100vh}
button{font:inherit;color:inherit;border:0;background:none;cursor:pointer}
input,select,textarea{font:inherit;color:var(--tx);background:var(--s2);border:1.5px solid var(--bd);border-radius:12px;padding:11px 13px;width:100%;outline:none;transition:border-color .15s,box-shadow .15s}
input:focus,select:focus,textarea:focus{border-color:var(--pri);box-shadow:0 0 0 3px var(--pris)}
textarea{font-family:var(--mono);font-size:12.5px;line-height:1.6;resize:vertical}
label{display:block;font-size:10.5px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:var(--tx3);margin:14px 0 6px}
.hide{display:none!important}.mut{color:var(--tx3);font-size:12.5px}.mono{font-family:var(--mono)}
h1{font-size:22px;font-weight:900;letter-spacing:-.03em}h2{font-size:15px;font-weight:800;letter-spacing:-.01em}
svg.i{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0;vertical-align:-4px}
/* shell */
.shell{display:grid;grid-template-columns:232px 1fr;min-height:100vh}
.side{position:sticky;top:0;height:100vh;padding:18px 14px;border-right:1px solid var(--bd);background:var(--s1);display:flex;flex-direction:column;gap:4px}
.brand{display:flex;align-items:center;gap:10px;padding:4px 8px 16px}
.logo{width:36px;height:36px;border-radius:11px;background:linear-gradient(135deg,var(--pri2),#b06bff);display:grid;place-items:center;color:#fff;font-weight:900}
.brand b{font-size:15px;letter-spacing:-.02em;display:block;line-height:1.1}.brand small{font-size:10px;color:var(--tx3);letter-spacing:.14em;font-weight:700}
.nav{display:flex;align-items:center;gap:11px;padding:11px 12px;border-radius:12px;color:var(--tx2);font-weight:700;width:100%;text-align:left}
.nav:hover{background:var(--s2)}.nav.on{background:var(--pris);color:var(--pri)}
.side .sp{flex:1}
.main{padding:22px clamp(14px,3vw,34px) 110px;max-width:1100px;width:100%}
.head{display:flex;align-items:center;gap:12px;margin-bottom:18px}.head .sp{flex:1}
.ibtn{width:40px;height:40px;border-radius:12px;background:var(--s1);border:1px solid var(--bd);display:grid;place-items:center;color:var(--tx2)}
.bar{display:none}
@media(max-width:900px){
 .shell{display:block}.side{display:none}
 .bar{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;left:0;right:0;bottom:0;z-index:50;background:color-mix(in srgb,var(--s1) 94%,transparent);backdrop-filter:blur(16px);border-top:1px solid var(--bd);padding:6px 6px max(8px,env(safe-area-inset-bottom))}
 .bar button{display:flex;flex-direction:column;align-items:center;gap:3px;padding:7px 2px;border-radius:12px;font-size:10.5px;font-weight:700;color:var(--tx3)}
 .bar button.on{color:var(--pri)}.bar button.cta .ic{background:linear-gradient(135deg,var(--pri2),#b06bff);color:#fff}
 .bar .ic{width:38px;height:28px;border-radius:10px;display:grid;place-items:center}.bar button.on:not(.cta) .ic{background:var(--pris)}
}
/* ui */
.card{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);padding:16px;margin-bottom:14px}
.grid{display:grid;gap:14px}.g2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:10px 15px;border-radius:12px;background:var(--s3);font-weight:700;font-size:13.5px;border:1px solid var(--bd);transition:transform .1s}
.btn:active{transform:scale(.96)}.btn.pri{background:linear-gradient(135deg,var(--pri2),var(--pri));color:#fff;border-color:transparent}
.btn.ok{background:var(--oks);color:var(--ok);border-color:transparent}.btn.bad{background:var(--bads);color:var(--bad);border-color:transparent}
.btn.big{width:100%;padding:14px;font-size:15px}.btn.sm{padding:7px 11px;font-size:12.5px;border-radius:10px}
.pill{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:99px;font-size:11px;font-weight:800;background:var(--s3);color:var(--tx2)}
.pill.act{background:var(--oks);color:var(--ok)}.pill.ban{background:var(--bads);color:var(--bad)}.pill.exp{background:var(--warns);color:var(--warn)}.pill.idle{background:var(--pris);color:var(--pri)}
.pill.tai{background:var(--bads);color:var(--tai)}.pill.xiu{background:rgba(53,192,255,.14);color:var(--xiu)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:14px}
.kpi{background:var(--s1);border:1px solid var(--bd);border-radius:14px;padding:14px}
.kpi b{display:block;font-size:26px;font-weight:900;letter-spacing:-.03em;line-height:1.1}.kpi span{font-size:11.5px;color:var(--tx3);font-weight:700}
.opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(128px,1fr));gap:9px}
.opt{text-align:left;padding:12px;border-radius:14px;background:var(--s2);border:1.5px solid var(--bd)}
.opt b{display:block;font-size:13.5px}.opt small{color:var(--tx3);font-size:11.5px}.opt.on{border-color:var(--pri);background:var(--pris)}
.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{padding:6px 11px;border-radius:99px;background:var(--s2);border:1px solid var(--bd);font-size:12px;font-weight:700;color:var(--tx2)}.chip.on{background:var(--pris);border-color:var(--pri);color:var(--pri)}
.msg{white-space:pre-wrap;word-break:break-word;background:var(--s2);border:1px dashed var(--bd);border-radius:14px;padding:14px;font-size:13.5px;line-height:1.6}
.kr{display:flex;flex-direction:column;gap:8px;padding:13px;border-radius:14px;background:var(--s1);border:1px solid var(--bd);margin-bottom:9px}
.kr .t{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.kr .k{font-family:var(--mono);font-weight:800;font-size:14px;letter-spacing:.02em}
.kr .m{display:flex;gap:12px;flex-wrap:wrap;font-size:12px;color:var(--tx3)}.kr .m b{color:var(--tx2)}
.kr .a{display:flex;gap:6px;flex-wrap:wrap}
.search{position:relative;margin-bottom:10px}.search input{padding-left:40px}.search svg{position:absolute;left:13px;top:12px;color:var(--tx3)}
.dots{display:flex;gap:4px;flex-wrap:wrap}.dots i{width:13px;height:13px;border-radius:4px;background:var(--s3)}.dots i.w{background:var(--ok)}.dots i.l{background:var(--bad)}
table{width:100%;border-collapse:collapse;font-size:13px}th{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--tx3);text-align:left;padding:8px}td{padding:8px;border-top:1px solid var(--bd)}
.scroll{overflow:auto}
.tpls{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.tp{text-align:left;padding:12px;border-radius:14px;background:var(--s2);border:1.5px solid var(--bd);display:flex;flex-direction:column;gap:7px}
.tp.on{border-color:var(--pri);background:var(--pris)}.tp b{font-size:13px}.tp pre{font:11px/1.45 var(--mono);color:var(--tx3);white-space:pre-wrap;max-height:116px;overflow:hidden;-webkit-mask:linear-gradient(#000 60%,transparent)}
/* modal + toast */
.mbg{position:fixed;inset:0;z-index:90;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);display:flex;align-items:flex-end;justify-content:center}
.modal{background:var(--s1);border:1px solid var(--bd);border-radius:22px 22px 0 0;padding:18px 16px max(18px,env(safe-area-inset-bottom));width:100%;max-width:520px;max-height:90vh;overflow:auto}
@media(min-width:700px){.mbg{align-items:center}.modal{border-radius:22px}}
#toast{position:fixed;left:50%;bottom:92px;transform:translateX(-50%);z-index:120;background:var(--tx);color:var(--bg);padding:10px 18px;border-radius:99px;font-weight:800;font-size:13px;display:none;box-shadow:0 8px 30px rgba(0,0,0,.4)}
/* login */
#login{min-height:100vh;display:grid;place-items:center;padding:20px}
.lg{width:100%;max-width:360px;text-align:center}.lg .logo{width:60px;height:60px;border-radius:18px;margin:0 auto 16px;font-size:26px}
.lg .card{text-align:left;margin-top:20px}
</style></head><body>
<div id="login" class="hide"><div class="lg"><div class="logo">P</div><h1>PAW Admin</h1><p class="mut">Đăng nhập để quản lý key</p>
 <div class="card"><label style="margin-top:0">Mật khẩu</label><input id="pw" type="password" autocomplete="current-password" placeholder="••••••••" onkeydown="if(event.key==='Enter')login()"><br><br><button class="btn pri big" onclick="login()">Vào quản trị</button></div></div></div>

<div id="app" class="shell hide">
 <aside class="side"><div class="brand"><div class="logo">P</div><div><b>PAW TX</b><small>ADMIN</small></div></div>
  <div id="snav"></div><div class="sp"></div>
  <button class="nav" onclick="toggleTheme()"><span id="thi"></span> Giao diện</button>
  <button class="nav" onclick="location.href='/admin/logout'"><span id="loi"></span> Đăng xuất</button></aside>
 <div><main class="main"><div class="head"><h1 id="ttl"></h1><div class="sp"></div>
   <button class="ibtn" onclick="refresh()" id="rfb"></button><button class="ibtn" onclick="toggleTheme()" id="thb"></button></div>
  <div id="v"></div></main></div>
 <nav class="bar" id="bar"></nav>
</div>
<div id="toast"></div>

<script>
const P={
 plus:'<path d="M12 5v14M5 12h14"/>',key:'<path d="m21 2-2 2m-7.6 7.6a5.5 5.5 0 1 1-7.8 7.8 5.5 5.5 0 0 1 7.8-7.8zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3"/>',
 bill:'<path d="M6 2h12v20l-3-2-3 2-3-2-3 2z"/><path d="M9 7h6M9 11h6M9 15h4"/>',msg:'<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
 grid:'<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
 chart:'<path d="M3 3v18h18"/><path d="m7 15 4-5 3 3 5-7"/>',box:'<path d="m21 8-9-5-9 5v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
 copy:'<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',lock:'<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
 unlock:'<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 7.5-2"/>',trash:'<path d="M3 6h18M8 6V4h8v2m-9 0 1 14h8l1-14"/>',
 ref:'<path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5"/>',sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 moon:'<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',out:'<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
 search:'<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',dev:'<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M11 18h2"/>',
 edit:'<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',clock:'<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 hash:'<path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/>',gem:'<path d="M6 3h12l4 6-10 13L2 9z"/><path d="M2 9h20"/>',book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5V22h16"/>',
 x:'<path d="M18 6 6 18M6 6l12 12"/>',more:'<circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/>'};
const ic=n=>`<svg class="i" viewBox="0 0 24 24">${P[n]||''}</svg>`;
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const dfmt=h=>h?esc(String(h).replace('T',' ').slice(0,16)):'—';
const VIEWS=[['mk','Bán key','plus'],['kl','Key','key'],['dh','Đơn hàng','bill'],['pay','Tin nhắn','msg'],['ov','Tổng quan','chart'],['pkg','Gói','box'],['hs_hu','Bàn Hũ','gem'],['hs_md5','Bàn MD5','hash'],['hd','API','book']];
const BAR=['mk','kl','dh','pay'];
let CUR='mk',PKGS=[],KEYS=[],S={},TPLS={},TN={},MK={sel:'',tpl:'',res:null},KF={q:'',st:'all'},hsT=null;

function toast(m){const t=$('toast');t.textContent=m;t.style.display='block';clearTimeout(t._h);t._h=setTimeout(()=>t.style.display='none',2200)}
function cp(t,l){const ok=()=>toast('Đã copy '+(l||''));
 if(navigator.clipboard&&isSecureContext)navigator.clipboard.writeText(t).then(ok).catch(()=>fb(t,ok));else fb(t,ok)}
function fb(t,ok){const a=document.createElement('textarea');a.value=t;a.style.cssText='position:fixed;opacity:0';document.body.appendChild(a);a.select();try{document.execCommand('copy');ok()}catch(e){toast('Không copy được')}a.remove()}
function setTheme(t){document.documentElement.dataset.theme=t;try{localStorage.setItem('paw_theme',t)}catch(e){}$('thi').innerHTML=$('thb').innerHTML=ic(t==='dark'?'sun':'moon')}
function toggleTheme(){setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark')}
function modal(h){closeModal();const m=document.createElement('div');m.className='mbg';m.id='mdl';m.innerHTML='<div class="modal">'+h+'</div>';m.onclick=e=>{if(e.target===m)closeModal()};document.body.appendChild(m)}
function closeModal(){const m=$('mdl');if(m)m.remove()}
async function api(p,o={}){const r=await fetch(p,{headers:{'Content-Type':'application/json'},credentials:'same-origin',...o});
 let j;try{j=await r.json()}catch(e){toast('Server trả mã '+r.status);throw e}
 if(r.status===401&&p.startsWith('/admin')){$('app').classList.add('hide');$('login').classList.remove('hide');throw 0}return j}
const post=(p,b)=>api(p,{method:'POST',body:JSON.stringify(b||{})});

async function login(){try{const r=await fetch('/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({pw:($('pw').value||'').trim()})});
 const j=await r.json();j.ok?start():toast(j.thong_bao||'Sai mật khẩu')}catch(e){toast('Không kết nối được server')}}
function start(){$('login').classList.add('hide');$('app').classList.remove('hide');
 $('loi').innerHTML=ic('out');$('rfb').innerHTML=ic('ref');setTheme(document.documentElement.dataset.theme);
 $('snav').innerHTML=VIEWS.map(([k,n,i])=>`<button class="nav" data-v="${k}" onclick="nav('${k}')">${ic(i)} ${n}</button>`).join('');
 $('bar').innerHTML=BAR.map(k=>{const v=VIEWS.find(x=>x[0]===k);return `<button data-v="${k}" class="${k==='mk'?'cta':''}" onclick="nav('${k}')"><span class="ic">${ic(v[2])}</span>${v[1]}</button>`}).join('')+`<button data-v="more" onclick="moreMenu()"><span class="ic">${ic('grid')}</span>Khác</button>`;
 refresh()}
function moreMenu(){modal(`<h2 style="margin-bottom:12px">Khác</h2><div class="opts">${VIEWS.filter(v=>!BAR.includes(v[0])).map(([k,n,i])=>`<button class="opt" onclick="closeModal();nav('${k}')">${ic(i)}<b style="margin-top:6px">${n}</b></button>`).join('')}</div>`)}
async function refresh(){await Promise.all([loadPk(),loadSet()]);nav(CUR)}
function nav(v){CUR=v;clearInterval(hsT);hsT=null;
 document.querySelectorAll('[data-v]').forEach(b=>b.classList.toggle('on',b.dataset.v===v||(v&&!BAR.includes(v)&&b.dataset.v==='more')));
 const meta=VIEWS.find(x=>x[0]===v);$('ttl').textContent=meta?meta[1]:'';
 ({ov,mk:mkView,kl:keysView,dh:ordersView,pkg:pkgView,pay:payView,hs_hu:()=>histView('hu'),hs_md5:()=>histView('md5'),hd:hdView})[v]();scrollTo({top:0})}
async function loadPk(){const j=await api('/admin/api/packages');PKGS=j.packages||[]}
async function loadSet(){const j=await api('/admin/api/settings');S=j.settings||{};TPLS=j.templates||{};TN=j.template_names||{}}
const pillSt=t=>({'hoạt động':'act','khóa':'ban','hết hạn':'exp','chưa kích hoạt':'idle'}[t]||'');

/* ── Tin nhắn: định dạng phía client để đổi mẫu tức thì ── */
function fmtMsg(tpl,k){
 const v={key:k.key,name:k.ten||k.name||'Quý khách',price:k.gia||k.price||'—',package:k.goi||k.package||'Tuỳ chỉnh',duration:k.thoi_han||k.duration||'—',
  order:k.don_hang||k.order||'—',expiry:k.ngay_het_han?'đến '+String(k.ngay_het_han).slice(0,16).replace('T',' '):(String(k.thoi_han||'').includes('Vĩnh')?'Vĩnh viễn ♾️':'tính từ lúc kích hoạt ('+(k.thoi_han||'')+')'),
  tool_url:S.tool_url||'(link tool — admin gửi riêng)',support:S.support||'—',activate_url:location.origin+'/makey'};
 return String(tpl||'').replace(/\{(\w+)\}/g,(m,x)=>v[x]??m)}
const DEMO={key:'PAXU-A7K3-M9ZD-2F9T',ten:'Anh Tú',gia:'250K',goi:'Gói 3 Ngày',thoi_han:'3 ngày',don_hang:'DH261122-AB12C'};
function tplPicker(sel,fn){return `<div class="chips">${Object.keys(TPLS).map(k=>`<button class="chip ${k===sel?'on':''}" onclick="${fn}('${k}')">${esc(TN[k]||k)}</button>`).join('')}</div>`}

/* ── Bán key ── */
const tsec=p=>((+p.days||0)*24+(+p.hours||0));
/* Chỉnh giá gói TRỰC TIẾP ngay trong tab bán key */
function pqRow(p){const i=esc(p.id);return `<div style="display:flex;gap:8px;align-items:center;margin-bottom:9px"><span style="flex:1;font-weight:700;font-size:13px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(p.icon||'')} ${esc(p.name)}</span><input id="pqv_${i}" value="${esc(p.price||'')}" style="width:96px;padding:8px 10px;flex-shrink:0" placeholder="giá"><label style="display:flex;gap:4px;align-items:center;margin:0;font-size:11px;font-weight:700;color:var(--tx2);text-transform:none;letter-spacing:0;white-space:nowrap"><input type="checkbox" id="pqk_${i}" checked style="width:auto">sync</label><button class="btn sm pri" onclick="pkgQuickPrice('${i}')">Lưu</button></div>`}
async function pkgQuickPrice(id){const j=await post('/admin/api/packages/'+encodeURIComponent(id)+'/price',{price:($('pqv_'+id)||{}).value||'',sync_keys:($('pqk_'+id)&&$('pqk_'+id).checked)?1:0});if(j.ok){toast(j.thong_bao||'Đã lưu');await loadPk();mkView()}else toast(j.thong_bao||'Lỗi')}
function mkView(){
 const list=PKGS.slice().sort((a,b)=>(tsec(a)||1e9)-(tsec(b)||1e9));
 if(!MK.sel||(!['_c','_p'].includes(MK.sel)&&!PKGS.find(p=>p.id===MK.sel)))MK.sel=(PKGS.find(p=>p.id==='P3')||list[0]||{id:'_c'}).id;
 if(!MK.tpl)MK.tpl=Object.keys(TPLS).find(k=>TPLS[k]===S.payment_template)||Object.keys(TPLS)[0];
 const hasPerm=PKGS.some(p=>tsec(p)===0);
 $('v').innerHTML=`<div class="grid g2" style="align-items:start"><div>
  <div class="card"><h2>1 · Chọn thời hạn</h2><p class="mut" style="margin:2px 0 12px">Hạn tính từ lúc khách kích hoạt.</p>
   <div class="opts">${list.map(p=>`<button class="opt ${MK.sel===p.id?'on':''}" onclick="mkPick('${p.id}')"><b>${esc(p.icon||'')} ${esc(p.name)}</b><small>${esc(p.thoi_han)} · ${esc(p.price||'chưa đặt giá')}</small></button>`).join('')}
    ${hasPerm?'':`<button class="opt ${MK.sel==='_p'?'on':''}" onclick="mkPick('_p')"><b>♾️ Vĩnh viễn</b><small>không hết hạn</small></button>`}
    <button class="opt ${MK.sel==='_c'?'on':''}" onclick="mkPick('_c')"><b>✏️ Tự nhập</b><small>ngày / giờ</small></button></div>
   <div id="cust" class="${MK.sel==='_c'?'':'hide'}"><div class="row"><div><label>Số ngày</label><input id="o_days" type="number" min="0" inputmode="numeric" placeholder="0"></div><div><label>Số giờ</label><input id="o_hours" type="number" min="0" inputmode="numeric" placeholder="0"></div></div>
    <div class="chips" style="margin-top:10px">${[['1 giờ',0,1],['3 giờ',0,3],['6 giờ',0,6],['12 giờ',0,12],['1 ngày',1,0],['3 ngày',3,0],['7 ngày',7,0],['30 ngày',30,0]].map(q=>`<button class="chip" onclick="$('o_days').value=${q[1]||''};$('o_hours').value=${q[2]||''}">${q[0]}</button>`).join('')}</div></div></div>
  <div class="card"><h2>2 · Thông tin đơn</h2><div class="row"><div><label>Số lượng key</label><input id="o_n" type="number" value="1" min="1" max="200" inputmode="numeric"></div><div><label>Tên khách</label><input id="o_name" placeholder="VD: Anh Tú"></div></div>
   <div class="row"><div><label>Giá (trống = theo gói)</label><input id="o_price" placeholder="VD: 250K"></div><div><label>Tiền tố key</label><input id="o_pre" placeholder="${esc(S.default_prefix||'PAXU')}" maxlength="6"></div></div>
   <label>Ghi chú</label><input id="o_note" placeholder="Tuỳ chọn"><br><button class="btn pri big" onclick="mkGo(this)">${ic('plus')} Tạo key & lấy tin nhắn</button></div>
  <div class="card"><h2>💰 Chỉnh giá gói</h2><p class="mut" style="margin:2px 0 10px">Đổi giá ngay tại đây. Tick "sync" sẽ đổi cả giá của những key CHƯA kích hoạt của gói (key đã bán giữ nguyên).</p>
   <div id="pqrows">${list.map(p=>pqRow(p)).join('')}</div></div></div>
  <div id="mkres"></div></div>`;mkRes()}
function mkPick(id){MK.sel=id;mkView()}
async function mkGo(btn){
 const b={count:+$('o_n').value||1,name:$('o_name').value.trim(),price:$('o_price').value.trim(),prefix:$('o_pre').value.trim(),note:$('o_note').value.trim()};
 if(MK.sel==='_p')b.permanent=1;else if(MK.sel==='_c'){b.days=$('o_days').value;b.hours=$('o_hours').value;if(!+b.days&&!+b.hours)return toast('Nhập số ngày hoặc giờ')}else b.package_id=MK.sel;
 btn.disabled=true;let j;try{j=await post('/admin/api/keys',b)}catch(e){btn.disabled=false;return}btn.disabled=false;
 if(!j.ok)return toast(j.thong_bao||'Lỗi');
 const pk=PKGS.find(p=>p.id===MK.sel);
 MK.res={order:j.don_hang,goi:j.goi,thoi_han:j.thoi_han,name:b.name,price:b.price||(pk&&pk.price)||'',keys:j.tin_nhan_thanh_toan.map(x=>x.key)};
 toast('Đã tạo '+j.da_tao+' key');mkRes();$('mkres').scrollIntoView({behavior:'smooth'})}
function mkRes(){const r=MK.res,el=$('mkres');if(!el)return;if(!r){el.innerHTML='';return}
 const msgs=r.keys.map(key=>fmtMsg(TPLS[MK.tpl],{key,ten:r.name,gia:r.price,goi:r.goi,thoi_han:r.thoi_han,don_hang:r.order}));
 window._msgs=msgs;
 el.innerHTML=`<div class="card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><h2>Đơn ${esc(r.order)}</h2><span class="pill act">${r.keys.length} key</span></div>
  <label style="margin-top:0">Mẫu tin nhắn</label>${tplPicker(MK.tpl,'mkTpl')}<br>
  ${msgs.map((m,i)=>`<div class="msg" style="margin-bottom:8px">${esc(m)}</div><div style="display:flex;gap:6px;margin-bottom:12px"><button class="btn pri" style="flex:1" onclick="cp(_msgs[${i}],'tin nhắn')">${ic('copy')} Copy tin nhắn</button><button class="btn" onclick="cp('${r.keys[i]}','key')">${ic('key')} Key</button></div>`).join('')}
  ${msgs.length>1?`<button class="btn big" onclick="cp(_msgs.join('\\n\\n'),'tất cả')">${ic('copy')} Copy tất cả ${msgs.length} tin</button>`:''}</div>`}
function mkTpl(k){MK.tpl=k;mkRes()}

/* ── Danh sách key ── */
async function keysView(){const j=await api('/admin/api/keys');KEYS=(j.keys||[]).filter(k=>k.loai!=='admin');keysRender(true)}
function keysRender(full){
 if(full)$('v').innerHTML=`<div class="search">${ic('search')}<input id="ks" placeholder="Tìm key, tên khách, đơn…" value="${esc(KF.q)}" oninput="KF.q=this.value;keysRender()"></div>
  <div class="chips" style="margin-bottom:12px">${[['all','Tất cả'],['hoạt động','Hoạt động'],['chưa kích hoạt','Chưa kích hoạt'],['hết hạn','Hết hạn'],['khóa','Khóa']].map(([k,n])=>`<button class="chip ${KF.st===k?'on':''}" onclick="KF.st='${k}';keysRender(true)">${n}</button>`).join('')}</div><div id="kl"></div>`;
 const q=KF.q.toLowerCase().trim();
 const L=KEYS.filter(k=>(KF.st==='all'||k.trang_thai===KF.st)&&(!q||[k.key,k.ten,k.don_hang,k.goi,k.ghi_chu].join(' ').toLowerCase().includes(q)));
 $('kl').innerHTML=L.length?L.map(k=>`<div class="kr"><div class="t"><span class="k">${esc(k.key)}</span><span class="pill ${pillSt(k.trang_thai)}">${esc(k.trang_thai)}</span></div>
  <div class="m"><span>${ic('key')} <b>${esc(k.ten||'Khách lẻ')}</b></span><span>${esc(k.goi||'—')} · ${esc(k.thoi_han)}</span><span>${esc(k.gia||'')}</span></div>
  <div class="m"><span>Hết hạn: <b>${k.da_kich_hoat?dfmt(k.ngay_het_han)||'Vĩnh viễn':'chưa kích hoạt'}</b></span><span>Hũ <b>${k.luot_goi_hu}</b> · MD5 <b>${k.luot_goi_md5}</b></span><span>${ic('dev')} <b>${(k.thiet_bi||[]).length}</b></span></div>
  <div class="a"><button class="btn sm pri" onclick="keyMsg('${k.id}')">${ic('copy')} Tin nhắn</button><button class="btn sm" onclick="keyEdit('${k.id}')">${ic('edit')} Sửa</button>
   ${k.trang_thai==='khóa'?`<button class="btn sm ok" onclick="keyAct('${k.id}',{status:'active'})">${ic('unlock')} Mở</button>`:`<button class="btn sm bad" onclick="keyAct('${k.id}',{status:'banned'})">${ic('lock')} Khóa</button>`}</div></div>`).join(''):'<div class="card mut" style="text-align:center">Không có key nào</div>';
 const kc=KEYS.length;if(full){const h=$('ttl');h.textContent='Key · '+kc}}
const kf=id=>KEYS.find(k=>k.id===id);
function keyMsg(id){const k=kf(id);if(!k)return;let sel=Object.keys(TPLS).find(x=>TPLS[x]===S.payment_template)||Object.keys(TPLS)[0];
 window._kt=t=>{sel=t;draw()};const draw=()=>{const m=fmtMsg(TPLS[sel],k);window._km=m;
  modal(`<div style="display:flex;align-items:center;margin-bottom:10px"><h2 style="flex:1">Tin nhắn · ${esc(k.key)}</h2><button class="ibtn" onclick="closeModal()">${ic('x')}</button></div>${tplPicker(sel,'_kt')}<br><div class="msg">${esc(m)}</div><br><button class="btn pri big" onclick="cp(_km,'tin nhắn')">${ic('copy')} Copy tin nhắn</button>`)};draw()}
async function keyAct(id,b){const j=await post('/admin/api/keys/'+encodeURIComponent(id),b);if(j.ok){toast('Đã cập nhật');closeModal();keysView()}else toast(j.thong_bao||'Lỗi')}
function keyEdit(id){const k=kf(id);if(!k)return;
 modal(`<div style="display:flex;align-items:center;margin-bottom:6px"><h2 style="flex:1" class="mono">${esc(k.key)}</h2><button class="ibtn" onclick="closeModal()">${ic('x')}</button></div>
 <p class="mut">${esc(k.goi||'')} · tạo ${dfmt(k.ngay_tao)} · ${k.da_kich_hoat?'kích hoạt '+dfmt(k.ngay_kich_hoat):'chưa kích hoạt'}${k.don_hang?' · '+esc(k.don_hang):''}</p>
 <div class="row"><div><label>Tên khách</label><input id="e_name" value="${esc(k.ten)}"></div><div><label>Giá</label><input id="e_price" value="${esc(k.gia)}"></div></div>
 <label>Ghi chú</label><input id="e_note" value="${esc(k.ghi_chu)}"><button class="btn pri big" style="margin-top:12px" onclick="keyAct('${id}',{name:$('e_name').value,price:$('e_price').value,note:$('e_note').value})">Lưu thông tin</button>
 <label>Gia hạn</label><div class="row"><input id="e_d" type="number" min="0" placeholder="+ ngày" inputmode="numeric"><input id="e_h" type="number" min="0" placeholder="+ giờ" inputmode="numeric"></div>
 <button class="btn ok big" style="margin-top:8px" onclick="keyAct('${id}',{extend_days:$('e_d').value||0,extend_hours:$('e_h').value||0})">${ic('clock')} Cộng thời gian</button>
 <label>Thiết bị (${(k.thiet_bi||[]).length})</label>${(k.thiet_bi||[]).map(d=>`<div class="mut" style="margin-bottom:4px">${ic('dev')} ${esc(d.ten_thiet_bi)} · gọi cuối ${dfmt(d.lan_cuoi_goi)}${d.da_gan===false?' · chưa gắn':''}</div>`).join('')||'<div class="mut">Chưa có</div>'}
 <div class="row" style="margin-top:10px"><button class="btn" onclick="if(confirm('Gỡ thiết bị đã gắn? Khách sẽ gắn lại máy mới ở lần dùng đầu.'))keyAct('${id}',{reset_device:1})">${ic('dev')} Gỡ thiết bị</button>
 <button class="btn" onclick="if(confirm('Thu hồi kích hoạt? Key về trạng thái chưa dùng, khách phải kích hoạt lại.'))keyAct('${id}',{revoke_activation:1})">${ic('ref')} Thu hồi KH</button></div>
 <button class="btn bad big" style="margin-top:8px" onclick="if(confirm('Xoá hẳn key này?'))keyDel('${id}')">${ic('trash')} Xoá key</button>`)}
async function keyDel(id){const j=await post('/admin/api/keys/'+encodeURIComponent(id)+'/delete');toast(j.thong_bao||'Xong');closeModal();keysView()}

/* ── Đơn hàng ── */
async function ordersView(){const j=await api('/admin/api/orders');const L=j.don_hang||[];
 $('v').innerHTML=L.length?L.map(o=>`<div class="kr"><div class="t"><span class="k">${esc(o.id)}</span><span class="pill ${o.trang_thai==='đã giao'?'act':'idle'}">${esc(o.trang_thai)}</span><span class="mut" style="margin-left:auto">${dfmt(o.ngay_tao)}</span></div>
  <div class="m"><span><b>${esc(o.khach)}</b></span><span>${esc(o.package)}</span><span>${esc(o.price||'')}</span><span>${o.so_key} key</span></div>
  <div class="m mono" style="flex-direction:column;gap:2px">${(o.keys||[]).map(k=>`<span>${esc(k)} · <b>${esc((o.trang_thai_thuc||{})[k]||'')}</b></span>`).join('')}</div>
  <div class="a"><button class="btn sm ok" onclick="ordAct('${o.id}',{status:'đã giao'})">Đã giao</button><button class="btn sm" onclick="cp('${(o.keys||[]).join('\\n')}','key')">${ic('copy')} Copy key</button><button class="btn sm bad" onclick="if(confirm('Xoá đơn + toàn bộ key của đơn?'))ordAct('${o.id}',{delete:1})">${ic('trash')}</button></div></div>`).join(''):'<div class="card mut" style="text-align:center">Chưa có đơn nào</div>'}
async function ordAct(id,b){const j=await post('/admin/api/orders/'+encodeURIComponent(id),b);toast(j.thong_bao||'Đã cập nhật');ordersView()}

/* ── Gói ── */
function pkgView(){$('v').innerHTML=`<div class="grid g2">${PKGS.map(p=>pkgCard(p)).join('')}${pkgCard({id:'',name:'',icon:'✨',price:'',days:30,hours:0,max_devices:1,_new:1})}</div>`}
function pkgCard(p){const n=p._new,i=n?'new':p.id;return `<div class="card"><h2>${n?'Thêm gói mới':esc(p.icon)+' '+esc(p.name)}</h2>
 <div class="row"><div><label>Tên</label><input id="pk_n_${i}" value="${esc(p.name)}"></div><div><label>Icon</label><input id="pk_i_${i}" value="${esc(p.icon)}"></div></div>
 <div class="row"><div><label>Giá</label><input id="pk_p_${i}" value="${esc(p.price)}"></div><div><label>Thiết bị</label><input id="pk_m_${i}" type="number" value="${p.max_devices||1}"></div></div>
 <div class="row"><div><label>Ngày</label><input id="pk_d_${i}" type="number" value="${p.days||0}"></div><div><label>Giờ</label><input id="pk_h_${i}" type="number" value="${p.hours||0}"></div></div><br>
 <div style="display:flex;gap:8px"><button class="btn pri" style="flex:1" onclick="pkgSave('${p.id}','${i}')">Lưu</button>${n?'':`<button class="btn bad" onclick="if(confirm('Xoá gói?'))pkgDel('${p.id}')">${ic('trash')}</button>`}</div></div>`}
async function pkgSave(id,i){const g=x=>$('pk_'+x+'_'+i).value;const j=await post('/admin/api/packages',{id,name:g('n'),icon:g('i'),price:g('p'),max_devices:g('m'),days:g('d'),hours:g('h')});
 if(j.ok){toast('Đã lưu gói');await loadPk();pkgView()}else toast(j.thong_bao||'Lỗi')}
async function pkgDel(id){await post('/admin/api/packages',{id,delete:1});await loadPk();pkgView()}

/* ── Tin nhắn thanh toán ── */
function payView(){let cur=S.payment_template;
 $('v').innerHTML=`<div class="grid g2" style="align-items:start"><div>
  <div class="card"><h2>Chọn mẫu</h2><p class="mut" style="margin:2px 0 12px">Bấm để dùng làm mẫu mặc định, xem trước bên cạnh.</p>
   <div class="tpls">${Object.keys(TPLS).map(k=>`<button class="tp ${TPLS[k]===cur?'on':''}" onclick="payPick('${k}')"><b>${esc(TN[k]||k)}</b><pre>${esc(fmtMsg(TPLS[k],DEMO))}</pre></button>`).join('')}</div></div>
  <div class="card"><h2>Tuỳ chỉnh</h2><p class="mut">Biến: bấm để chèn vào chỗ con trỏ.</p>
   <div class="chips" style="margin:8px 0">${['key','package','duration','price','name','order','expiry','tool_url','support'].map(v=>`<button class="chip mono" onclick="payIns('{${v}}')">{${v}}</button>`).join('')}</div>
   <textarea id="pay_tpl" rows="13">${esc(cur)}</textarea>
   <div class="row"><div><label>Link tool</label><input id="s_tool" value="${esc(S.tool_url||'')}" placeholder="https://… link tool HTML"></div><div><label>Liên hệ hỗ trợ</label><input id="s_sup" value="${esc(S.support||'')}"></div></div>
   <div class="row"><div><label>Tiền tố key</label><input id="s_pre" value="${esc(S.default_prefix||'PAXU')}" maxlength="6"></div></div><br><button class="btn pri big" onclick="paySave()">Lưu cài đặt</button></div></div>
  <div class="card" style="position:sticky;top:12px"><h2>Xem trước</h2><p class="mut" style="margin-bottom:10px">Khách demo: Gói 3 ngày · 250K</p><div class="msg" id="pay_prev"></div><br><button class="btn pri big" onclick="cp($('pay_prev').textContent,'bản xem trước')">${ic('copy')} Copy</button></div></div>`;
 ['pay_tpl','s_tool','s_sup'].forEach(x=>$(x).oninput=payPrev);payPrev()}
function payPrev(){const t=$('pay_tpl').value;$('pay_prev').textContent=fmtMsg(t,DEMO).replace(S.tool_url||'(link tool — admin gửi riêng)',$('s_tool').value||'(link tool — admin gửi riêng)').replace(S.support||'—',$('s_sup').value||'—')}
function payPick(k){$('pay_tpl').value=TPLS[k];payPrev();document.querySelectorAll('.tp').forEach(b=>b.classList.remove('on'));toast('Đã chọn mẫu — bấm Lưu cài đặt')}
function payIns(v){const t=$('pay_tpl'),a=t.selectionStart,b=t.selectionEnd;t.value=t.value.slice(0,a)+v+t.value.slice(b);t.focus();t.selectionStart=t.selectionEnd=a+v.length;payPrev()}
async function paySave(){const j=await post('/admin/api/settings',{payment_template:$('pay_tpl').value,tool_url:$('s_tool').value,support:$('s_sup').value,default_prefix:$('s_pre').value});
 if(j.ok){S=j.settings;toast('Đã lưu');payView()}else toast(j.thong_bao||'Lỗi')}

/* ── Tổng quan ── */
async function ov(){const j=await api('/admin/api/overview'),a=j.key_admin_console||{};
 $('v').innerHTML=`<div class="kpis">${[['so_key','Key đã tạo'],['dang_hoat_dong','Đang hoạt động'],['da_kich_hoat','Đã kích hoạt'],['het_han','Hết hạn'],['so_don_hang','Đơn hàng']].map(([k,n])=>`<div class="kpi"><b>${j[k]}</b><span>${n}</span></div>`).join('')}<div class="kpi"><b>${j.luot_goi_hu+j.luot_goi_md5}</b><span>Lượt gọi API</span></div></div>
 <div class="grid g2">${j.ban.map(b=>`<div class="card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><h2>Bàn ${esc(b.ten)}</h2><span class="mut">#${b.phien_hien_tai||'—'}</span><span class="pill ${b.loi?'ban':'act'}" style="margin-left:auto">${b.loi?'lỗi nguồn':'LIVE'}</span></div>
  ${b.du_doan_tiep?`<span class="pill ${b.du_doan_tiep==='TAI'?'tai':'xiu'}" style="font-size:13px;padding:5px 12px">Dự đoán: ${b.du_doan_tiep==='TAI'?'TÀI':'XỈU'}</span>`:''}
  <p style="margin:10px 0 4px"><b style="color:var(--ok)">${b.thang}</b> thắng · <b style="color:var(--bad)">${b.thua}</b> thua · <b>${b.ty_le_thang}%</b></p><button class="btn sm" onclick="nav('hs_${b.code}')">Xem lịch sử</button></div>`).join('')}</div>
 <div class="card"><h2>Key admin riêng</h2><p class="mut" style="margin:2px 0 8px">Token cho trang history riêng của bạn.</p><p class="mono" style="word-break:break-all">${esc(a.key||'')} · ${esc(a.token||'')}</p><br><button class="btn sm" onclick="cp('${esc(a.token||'')}','token')">${ic('copy')} Copy token</button></div>`}

/* ── Lịch sử bàn ── */
async function histView(code){const draw=async()=>{let j;try{j=await api('/admin/api/history/'+code+'?limit=40')}catch(e){return}
 const li=j.lich_su||[],st=j.thong_ke||{win:0,lose:0,ty_le:0},hh=j.phien_hien_tai||{},lb=s=>s==='TAI'?'TÀI':s==='XIU'?'XỈU':(s||'—');
 $('v').innerHTML=`<div class="kpis"><div class="kpi"><b style="color:var(--ok)">${st.win}</b><span>Thắng</span></div><div class="kpi"><b style="color:var(--bad)">${st.lose}</b><span>Thua</span></div><div class="kpi"><b>${st.ty_le}%</b><span>Tỷ lệ thắng</span></div></div>
 ${hh.du_doan?`<div class="card"><span class="mut">DỰ ĐOÁN PHIÊN #${hh.phien}</span><div style="font-size:34px;font-weight:900;color:var(--${hh.du_doan==='TAI'?'tai':'xiu'})">${lb(hh.du_doan)} <small style="font-size:15px;color:var(--tx2)">${hh.do_tin_cay||''}%</small></div><div class="mut">Cầu: ${esc(hh.cau||'—')}</div></div>`:''}
 <div class="card"><h2 style="margin-bottom:8px">Chuỗi gần nhất</h2><div class="dots">${li.map(h=>`<i class="${h.trang_thai==='win'?'w':h.trang_thai==='lose'?'l':''}" title="#${h.phien}"></i>`).join('')}</div></div>
 ${(j.phan_tich_cau&&j.phan_tich_cau.khung_da_phien&&j.phan_tich_cau.khung_da_phien.length)?`<div class="card"><h2 style="margin-bottom:8px">Phân tích đa khung 2→50 phiên</h2><div class="chips">${j.phan_tich_cau.khung_da_phien.map(r=>`<span class="chip ${r.p_tai>=0.53?'on':''}" title="khung ${r.khung}p · TÀI ${r.tai} XỈU ${r.xiu} · lệch ${r.lech}">⏱ ${r.khung}p ${r.goc==='đảo'?'🔄':'➡️'} ${(r.p_tai*100).toFixed(0)}%</span>`).join('')}</div>${j.phan_tich_cau.dong_thuan_da_khung?`<p class="mut" style="margin-top:8px">${esc(j.phan_tich_cau.dong_thuan_da_khung.mo_ta||'')}</p>`:''}</div>`:''}
 <div class="card scroll"><table><tr><th>Phiên</th><th>Dự đoán</th><th>Xúc xắc</th><th>Tổng</th><th>KQ</th><th></th></tr>${li.map(h=>`<tr><td class="mono">#${h.phien}</td><td>${h.du_doan?`<span class="pill ${h.du_doan==='TAI'?'tai':'xiu'}">${lb(h.du_doan)}</span>`:'—'}</td><td class="mono">${(h.xuc_xac||[]).join('·')||'—'}</td><td><b>${h.tong??'—'}</b></td><td>${h.ket_qua?`<span class="pill ${h.ket_qua==='TAI'?'tai':'xiu'}">${lb(h.ket_qua)}</span>`:'—'}</td><td>${h.icon||''}</td></tr>`).join('')}</table></div>`};
 await draw();hsT=setInterval(()=>{if(CUR==='hs_'+code)draw()},5000)}

/* ── API ── */
function hdView(){const B=location.origin;$('v').innerHTML=`<div class="card"><h2>Luồng bán key</h2><p class="mut" style="margin-top:6px">1) Tạo key ở tab Bán key → copy tin nhắn gửi khách.<br>2) Khách mở tool, dán key vào ô KÍCH HOẠT.<br>3) Tool tự gọi API dự đoán mỗi 4 giây kèm mã thiết bị.</p></div>
 <div class="card"><h2>Endpoint</h2><div class="msg mono" style="margin-top:8px;font-size:12px">POST ${B}/makey  {"key":"PAXU-XXXX-XXXX-XXXX"}\nGET  ${B}/api/&lt;TOKEN&gt;/hu\nGET  ${B}/api/&lt;TOKEN&gt;/md5\nGET  ${B}/api/&lt;TOKEN&gt;/history/hu\nHeader: X-Device-ID</div><br><button class="btn" onclick="cp('${B}','URL gốc')">${ic('copy')} Copy URL gốc</button></div>`}

(async()=>{try{const r=await fetch('/admin/api/overview',{credentials:'same-origin'});if(r.status===200)return start()}catch(e){}
 $('login').classList.remove('hide')})();
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
