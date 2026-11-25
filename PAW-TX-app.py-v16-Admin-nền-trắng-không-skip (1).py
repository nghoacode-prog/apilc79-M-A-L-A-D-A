# -*- coding: utf-8 -*-
"""
PAW TX API v13 — STUDIO EDITION (LC79 1 key 2 bàn Hũ+MD5 · Sunwin 1 key 1 bàn · Governor ổn định · Admin Studio)
════════════════════════════════════════════════════════════════════════════════
• API dự đoán (Hũ + MD5) chỉ dùng được SAU khi kích hoạt key tại /makey
• Hệ thống GÓI (ngày/tuần/tháng...), ĐƠN HÀNG, tạo key SLL có đơn hàng đẹp
• Mỗi key gắn thiết bị (device) khi kích hoạt — admin xem info đầy đủ
• Render free: /tmp + backup cloud Gist (GIST_TOKEN + GIST_ID) → không mất key
• Engine 84 model + tầng phân tích cầu NGẮN / TRUNG / DÀI + bộ ổn định dài hạn
• v7: ĐA KHUNG CẦU 3 TẦNG 5/12/30 (conviction gate — thiếu mẫu/cầu chưa lệch
  rõ thì MULTIW bỏ phiếu) · CHỈNH GIÁ GÓI TRỰC TIẾP /admin/api/packages/<id>/price + bảng sửa
  giá trong tab Bán key · 26 mẫu tin nhắn thanh toán đẹp cho Telegram
• v7.1: HỆ CTV — admin tạo tk CTV + cấp quyền chi tiết (tạo key, khóa/mở key,
  cộng hạn, tự nhập giá, xem lượt gọi) + hạn mức key/ngày + gói được phép bán;
  CTV tạo key BẮT BUỘC tên khách; portal riêng /ctv; admin xem chi tiết CTV:
  keys, đơn hàng, doanh thu, key theo ngày, nhật ký toàn bộ hành động
• v9: THANH TOÁN CTV — đơn thanh toán điện tử + QR BIDV VietQR (điền sẵn tiền + nội dung),
  CTV chuyển khoản → bấm "Đã thanh toán" + gửi bill → ADMIN DUYỆT TAY; quá giờ chốt (SETTLE_TO)
  còn nợ & chưa báo thanh toán → TỰ ĐỘNG THU HỒI toàn bộ key + khóa chức năng; duyệt xong tự mở lại
• v10: ADMIN NÂNG CẤP — Tổng quan thông minh (cảnh báo, doanh thu, top CTV, gia hạn, ngủ đông) · tab KHÁCH HÀNG
  (hồ sơ + thiết bị + lịch sử) · tab LỊCH SỬ KEY (tạo/kích hoạt/gọi API/hết hạn/hành động CTV) · chi tiết CTV 6 tab ·
  link + tin nhắn đăng nhập CTV (/ctv, /ctv/login) · PHÂN TÍCH CHU KỲ có kiểm định thống kê + backtest tự đo
• v11: SIẾT CHU KỲ — chỉ công nhận 1 chu kỳ chủ đạo duy nhất (z ≥ 3.0 sau hiệu chỉnh đa phép thử
  + CẢ NỬA TRƯỚC lẫn nửa sau phải cùng hướng = "tính liên tục"), tín hiệu mâu thuẫn → CHỜ không chơi ·
  MULTIW siết cổng: cần ≥ 2 khung lệch mạnh VÀ cùng hướng mới lên tiếng
• v12: 3 BÀN — LC79 (Hũ + MD5) + SUNWIN (API riêng, tự bootstrap lịch sử từ
  chuỗi "cau") · KEY THEO GAME: LC79 và Sunwin dùng key riêng, gọi nhầm → 403 ·
  GOVERNOR ỔN ĐỊNH: cấm mặc định, conf thấp acc30 đang thua → tự đóng cửa (CHỜ),
  chống lật loạn (hysteresis) · CHU KỲ làm lại theo NHỊP RUN (1 đáp án duy nhất,
  độ thuần ≥ 0.7 + backtest tự chấm < 50% thì tự ngừng phát tin) · ADMIN UI: nav
  nhóm, gói/key chọn game, badge Sunwin
• v13: ADMIN STUDIO — làm mới 100% giao diện /admin (rail + topbar + workspace,
  Ctrl+K palette, topbar sticky, kim chỉ nam 2 LOẠI KEY: LC79 = 1 key dùng chung
  2 bàn Hũ + MD5 · SUNWIN = 1 key 1 bàn, key mới không còn loại "all" trừ gói cũ
  tương thích) · Bán key 3 bước rõ ràng (Loại key → Thời hạn → Thông tin) ·
  Lịch sử từng bàn có theme riêng (Sunwin 🍒 màu cam) + KPI tách lượt gọi
  LC79/Sunwin · keylog + khách hàng đếm cả lượt gọi Sunwin
• v14: ADMIN STUDIO 2 — banner hero doanh thu (sparkline 14 ngày SVG), donut
  tỷ lệ thắng cho tổng quan + từng bàn, băng màu riêng theo bàn (Hũ mint /
  MD5 tím / Sunwin cam), bảng lịch sử zebra + hover, LỌC KEY THEO LOẠI
  (LC79 / Sunwin / key cũ all) ngay đầu trang Key, khối contract endpoint
  (✅/⛔) ngay ở bước chọn loại key, sidebar in rõ luật "mỗi game 1 key riêng"
• v15: ADMIN UI LÀM LẠI — bỏ toàn bộ icon ký tự/emoji, thay bằng bộ icon SVG
  (sprite inline, 46 symbol, sắc nét mọi độ phân giải, không phụ thuộc font);
  bố cục mới: rail nhóm chức năng + topbar trạng thái tự động + lưới KPI +
  thẻ "Bàn cược · tự động phân tích" (nhịp / độ thuần / backtest / dự đoán hiện tại
  lấy từ engine, tự cập nhật 25s) · trang Key có bộ lọc dạng segmented + thanh bulk ·
  Bán key 3 bước có stepper, gói tự lọc theo loại key · theme sáng/tối nhớ lựa chọn.
• v15.1: ADMIN_PASSWORD CHỈ lấy từ biến môi trường (không còn sinh ngẫu nhiên mỗi
  lần deploy), chặn dò mật khẩu (8 lần sai → khoá 15 phút), /admin/api/authinfo cho
  trang đăng nhập biết đã cấu hình hay chưa; sửa loạt lỗi: token admin không lưu,
  sắp xếp key/đơn hàng có thể crash khi thiếu ngày tạo, cảnh báo bàn lỗi trỏ sai trang,
  trùng id input trong form CTV, danh sách key không tự làm mới, mất giá trị ngày/giờ
  khi đổi gói, theme không được nạp lại sau khi tải trang.
• v16: ADMIN NỀN TRẮNG — data-theme mặc định "light" (nền trắng, nhớ lựa chọn
  sáng/tối) · meta theme-color trắng · media query ≤560px: KPI 2 cột,
  thẻ gọn, bảng chữ nhỏ → dùng tốt trên điện thoại lẫn PC · BẢNG PHIÊN: dòng
  WIN tô nền xanh, dòng LOSE tô nền đỏ + badge WIN/LOSE màu riêng để xem nhanh ·
  CHẾ ĐỘ KHÔNG-SKIP: Brain.predict không còn trả side=None (hết trạng thái CHỜ/
  skip) — conf chưa đạt ngưỡng thì vẫn ra 1 phía an toàn (giữ phía cũ → engine →
  phiếu đa số), tắt bằng biến môi trường NO_SKIP=0 · giữ nguyên gate thích nghi
  + hysteresis + backtest tự chấm để thuật toán ổn định lâu dài, tự phân tích
  và tự cập nhật 8s mỗi bàn.
• v16.1: CHỐNG KẸT PHÍA — sau khi thấy hệ đứng nguyên 1 phía (vd XỈU) dù cầu
  đang đảo liên tục: (1) đổi thứ tự ưu tiên NO-SKIP: phía ENGINE chốt trước,
  phía cũ chỉ là dự phòng; (2) siết hysteresis ép giữ phía 0.030 → 0.015;
  (3) thêm AUTO-FLIP: cùng phía thua 3 phiên liên tiếp (FLIP_AFTER, mặc định 3)
  → tự đảo chiều tức thì với nhãn [AUTO-FLIP] trong reasoning, không thể kẹt
  1 phía mãi nữa.
"""
import base64, hmac, hashlib, json, math, os, secrets, threading, time, uuid
from collections import deque, Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict

import requests
from flask import Flask, jsonify, make_response, redirect, request, session
from werkzeug.exceptions import HTTPException

URLS  = {"hu":     os.getenv("API_URL_HU",     "https://wtx.tele68.com/v1/tx/sessions"),
         "md5":    os.getenv("API_URL_MD5",    "https://wtxmd52.tele68.com/v1/txmd5/sessions"),
         "sunwin": os.getenv("API_URL_SUNWIN", "https://asbestos-promote-mississippi-wizard.trycloudflare.com/sunwin/api/tx")}
NAMES = {"hu": "LC79 Hũ", "md5": "LC79 MD5", "sunwin": "Sunwin"}
# Game logic: mỗi GAME một loại key riêng (không dùng chung)
#   lc79   → 2 bàn Hũ + MD5   ·   sunwin → 1 bàn Sunwin
GAME_OF  = {"hu": "lc79", "md5": "lc79", "sunwin": "sunwin"}
GAMES    = {"lc79":   "LC79 · Hũ + MD5 (2 bàn)",
            "sunwin": "Sunwin (1 bàn)",
            "all":    "Tất cả các game"}
GAME_ICON = {"lc79": "🎲", "sunwin": "🍒", "all": "♾️"}

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
# ── MẬT KHẨU ADMIN: CHỈ lấy từ biến môi trường ADMIN_PASSWORD trên Render.
# Không sinh mật khẩu ngẫu nhiên nữa (đổi mỗi lần deploy = không đăng nhập được).
# Nếu chưa set biến → /admin/login từ chối và báo rõ cần thêm biến, không mở cửa.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
if not ADMIN_PASSWORD:
    print("════════════════════════════════════════════════════", flush=True)
    print(" [ADMIN] CHƯA ĐẶT BIẾN ADMIN_PASSWORD", flush=True)
    print(" [ADMIN] Render → Environment → Add Environment Variable", flush=True)
    print(" [ADMIN] Key = ADMIN_PASSWORD · Value = mật khẩu bạn muốn → Save → redeploy", flush=True)
    print("════════════════════════════════════════════════════", flush=True)
else:
    print("[ADMIN] Đã nạp ADMIN_PASSWORD từ biến môi trường (%d ký tự)" % len(ADMIN_PASSWORD), flush=True)
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
    return {"keys": {}, "packages": {}, "orders": {}, "settings": {}, "ctvs": {}, "ctvlog": [], "ctvpays": {},
            "admin_key": "",
            "meta": {"created": now_iso()}}

def _load_store():
    try:
        d = json.load(open(STORE_FILE, encoding="utf-8"))
        if isinstance(d, dict) and "keys" in d:
            d.setdefault("packages", {}); d.setdefault("orders", {}); d.setdefault("settings", {})
            d.setdefault("ctvs", {}); d.setdefault("ctvlog", []); d.setdefault("ctvpays", {})
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
                    d.setdefault("ctvs", {}); d.setdefault("ctvlog", []); d.setdefault("ctvpays", {})
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
    if not sec: return "Vĩnh viễn"
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

def _new_key(kid, prefix, pk, name, note, order_id="", game="all"):
    now = time.time()
    return {"id": kid, "key": kid, "name": name, "role": "key", "status": "active",
            "package_id": pk["id"] if pk else "", "price": pk["price"] if pk else "",
            "duration_days": pk["days"] if pk else None,
            "created_at": now_iso(), "expires_ts": None, "expires_at": None,
            "max_devices": 1, "activated": False, "activated_at": None,
            "token": None, "note": note, "order_id": order_id,
            "game": game,
            "devices": {}, "calls_hu": 0, "calls_md5": 0, "calls_sunwin": 0, "last_call": None}

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

def key_allowed_codes(k):
    """v12: mỗi GAME một loại key riêng. Key admin/gói 'all' dùng mọi bàn."""
    if not isinstance(k, dict): return []
    if k.get("role") == "admin": return list(URLS)
    g = k.get("game") or "all"
    if g == "all": return list(URLS)
    return [c for c in URLS if GAME_OF.get(c) == g]

def key_access_ok(k, code):
    return code in key_allowed_codes(k)

def touch_call(k, tok, table):
    if k.get("role") == "admin": return
    f = "calls_" + table
    k[f] = int(k.get(f, 0)) + 1
    k["last_call"] = now_iso()
    dev = k.setdefault("devices", {}).get(tok)
    if dev:
        dev[f] = int(dev.get(f, 0)) + 1
        dev["last_call"] = now_iso()

def _key_public(k):
    devs = [{"ten_thiet_bi": d.get("name", "Thiết bị") + " " + str(i + 1), "kich_hoat": d.get("activated_at"),
             "lan_cuoi_goi": d.get("last_call"), "luot_goi_hu": d.get("calls_hu", 0),
             "luot_goi_md5": d.get("calls_md5", 0), "luot_goi_sunwin": d.get("calls_sunwin", 0), "mo_ta": d.get("ua", ""),
             "da_gan": bool(d.get("device_id"))}
            for i, d in enumerate((k.get("devices") or {}).values())]
    pk = STORE["packages"].get(k.get("package_id") or "", {})
    return {"id": k["id"], "key": k["key"], "ten": k.get("name", ""),
            "trang_thai": key_status(k), "gia": k.get("price", ""),
            "goi": k.get("package_name") or (pk.get("name", "") if pk else ""),
            "game": k.get("game") or "all",
            "ten_game": GAMES.get(k.get("game") or "all", "Tất cả"),
            "thoi_han": _dur_text(_key_dur_sec(k)), "thoi_han_giay": _key_dur_sec(k),
            "han_bao_nhieu_ngay": k.get("duration_days"),
            "ngay_tao": k.get("created_at"), "ngay_het_han": k.get("expires_at"),
            "da_kich_hoat": bool(k.get("activated")), "ngay_kich_hoat": k.get("activated_at"),
            "gioi_han_thiet_bi": k.get("max_devices", 1), "thiet_bi": devs,
            "luot_goi_hu": k.get("calls_hu", 0), "luot_goi_md5": k.get("calls_md5", 0),
            "luot_goi_sunwin": k.get("calls_sunwin", 0),
            "don_hang": k.get("order_id", ""), "ghi_chu": k.get("note", ""),
            "loai": k.get("role", "key"), "by": k.get("by", "admin")}

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
    """Parser chung: nuôi cả nguồn cũ (id/dices/point) lẫn nguồn kiểu
    Sunwin (phien/xuc_xac(1..3)/tong/ket_qua). Trả về list phiên chuẩn hoá."""
    rows = data.get("list") if isinstance(data, dict) else data
    if rows is None and isinstance(data, dict) and ("phien" in data or "id" in data):
        rows = [data]                                   # API kiểu Sunwin trả 1 object
    got  = {}
    for it in rows or []:
        if not isinstance(it, dict): continue
        try:
            sid = None
            for kk in ("id", "phien"):
                if kk in it:
                    sid = int(it[kk]); break
            if sid is None: continue
            raw_dices = it.get("dices") if it.get("dices") is not None else it.get("xuc_xac")
            if raw_dices is None and all(kk in it for kk in ("xuc_xac1", "xuc_xac2", "xuc_xac3")):
                raw_dices = [it["xuc_xac1"], it["xuc_xac2"], it["xuc_xac3"]]
            dices = [int(x) for x in raw_dices[:3]] if isinstance(raw_dices, (list, tuple)) else []
            dice_ok = len(dices) == 3 and all(1 <= x <= 6 for x in dices)
            point = None
            if dice_ok: point = sum(dices)
            else:
                for kk in ("point", "tong"):
                    if it.get(kk) is not None:
                        try:
                            pv = int(it[kk])
                            if 3 <= pv <= 18: point = pv
                        except (TypeError, ValueError): pass
                        break
            # ket_qua ("Tài"/"Xỉu") là nguồn chuẩn nếu có, không thì suy từ điểm
            res = None
            kq = str(it.get("ket_qua", "") or "").strip().lower().replace("ỉ", "i")
            if kq in ("tai", "t"): res = "TAI"
            elif kq in ("xiu", "x"): res = "XIU"
            if res is None:
                if point is None: continue
                res = "TAI" if point >= 11 else "XIU"
            elif point is None:
                pass                                          # chỉ có kết quả (đủ cho engine.seq)
            got[sid] = {"id": sid, "dices": dices, "point": point, "result": res}
        except (KeyError, TypeError, ValueError):
            continue
    out_rows = [got[k] for k in sorted(got)]
    # BOOTSTRAP TỪ CHUỖI "CAU": nguồn chỉ nhận ~1 phiên nhưng kèm "cau" (VD
    # "TXXXXXTXTTXTXXT") → dựng lịch sử ảo để engine đủ dữ liệu ngay từ đầu.
    if isinstance(data, dict) and data.get("cau") and out_rows and len(out_rows) < 24:
        try:
            newest = out_rows[-1]; kq = newest["result"]
            ban_dau_cuoi = "T" if kq == "TAI" else "X"
            cau = [ch for ch in str(data["cau"]).upper() if ch in "TX"]
            if cau and (cau[-1] == ban_dau_cuoi or cau[0] == ban_dau_cuoi):
                # xác định chiều: đuôi chuỗi là phiên mới nhất (chuẩn), nếu không
                # khớp mà đầu chuỗi khớp thì chuỗi đang "mới nhất ở đầu"
                newest_first = (cau[-1] != ban_dau_cuoi and cau[0] == ban_dau_cuoi)
                body = cau[1:] if newest_first else cau[:-1]     # phần trước phiên mới nhất
                days = [{"id": newest["id"] - (j + 1), "dices": [], "point": None,
                         "result": "TAI" if ch == "T" else "XIU"}
                        for j, ch in enumerate(reversed(body))]
                days.reverse()                                    # id tăng dần
                have = {r["id"] for r in out_rows}
                out_rows = [d for d in days if d["id"] not in have] + out_rows
        except Exception: pass
    return out_rows

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
            return {"side": None, "confidence": 0,
                    "p_tai": 0.5, "reasoning": "[CAM] CHỜ — chưa đủ dữ liệu (governor cấm mặc định)",
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
        # 5) MULTIW: đồng thuận 3 tầng khung (mặc định 5/12/30) + conviction gate
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
                          f"khung {CAU_WINDOWS_LABEL}: TÀI {_mw_t}/{len(mw_rows)} · XỈU {_mw_x}/{len(mw_rows)}"),
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
        """Nuôi dữ liệu phiên. Chấp nhận phiên thiếu điểm (nguồn chỉ có kết quả,
        VD bootstrap từ chuỗi "cau" của Sunwin)."""
        if not isinstance(row, dict): return False
        try:
            sid = int(row.get("id"))
        except (TypeError, ValueError): return False
        result = str(row.get("result", "")).strip().upper()
        if sid in self._seen_ids or result not in ("TAI", "XIU"): return False
        self._seen_ids.add(sid)
        point = None
        try:
            point = int(row.get("point"))
            if not 3 <= point <= 18: return False
        except (TypeError, ValueError): pass
        self.history.append(1 if result == "TAI" else 0)
        if point is not None:
            self.points.append(point)
            self.engine.push([{"result": result, "point": point,
                               "dices": row.get("dices", [])}])
        else:
            self.engine.push([{"result": result, "point": None, "dices": []}])
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
        # ── v17: LÕI CHU KỲ NGẮN / TRUNG / DÀI — hoà trộn vào p_tai cuối ────
        # Engine 84 model vẫn chạy, nhưng p_tai cuối là TRỌNG SỐ HOÀ TRỢN giữa
        # engine và phân tích chu kỳ 3 tầng (NGẮN 12 · TRUNG 30 · DÀI 60).
        # CYCLE_WEIGHT (mặc định 0.40) = độ tin tầng chu kỳ; đổi qua biến môi trường.
        try:
            cyc = phan_tich_chu_ky_3_tang(list(self.engine.seq))
        except Exception:
            cyc = None
        self.last_cycle = cyc
        if isinstance(cyc, dict) and cyc.get("p_tai") is not None:
            w_cyc = float(os.getenv("CYCLE_WEIGHT", "0.40") or 0.40)
            w_cyc = min(0.8, max(0.05, w_cyc))
            p_mix = (1.0 - w_cyc) * float(result.get("p_tai", 0.5)) + w_cyc * float(cyc["p_tai"])
            result["p_tai"] = round(p_mix, 4)
            result["side"] = "TAI" if p_mix >= 0.5 else "XIU"
            result["confidence"] = max(50, min(89, int(round(50 + abs(p_mix - 0.5) * 150))))
            result["reasoning"] = "[CHU KỲ %d/3 tầng → %s] %s | %s" % (
                cyc.get("dong_thuan", 0), cyc.get("side", "—"),
                str(cyc.get("mo_ta", ""))[:90], str(result.get("reasoning", ""))[:90])
        result["chu_ky_3_tang"] = cyc if isinstance(cyc, dict) else {"da_du_du_lieu": False}
        # ── GOVERNOR v12 — ỔN ĐỊNH LÂU DÀI, CẤM LÀ MẶC ĐỊNH ──────────────
        # Triết lý: hệ thống chỉ "phát tin" khi ĐANG ĂN HOẶC tín hiệu thật sự
        # vững; đang thua → tự đóng cửa thay vì chơi random. Ba lớp:
        #   1) GATE THÍCH NGHI: ngưỡng conf tối thiểu đi theo chất lượng 30
        #      phiên gần nhất → ăn được thì mở nhẹ, thua là siết gần như đóng.
        #   2) KHÁNG NHIỄU (hysteresis): p sát 50% thì GIỮ NGUYÊN phía cũ,
        #      không cho tổng hợp lật qua lật lại tạo cảm giác ngẫu nhiên.
        #      v16.1: siết ngưỡng 0.030 → 0.015 để hệ phản ứng nhanh hơn với
        #      cầu đang đảo chiều liên tục (trước đây kẹt 1 phía mất nhiều phiên).
        #   3) CẤM MẶC ĐỊNH: không đạt gate → side = None (bản = "skip"), API
        #      trả rõ "CHỜ" thay vì phán bậy.
        ev = result["evaluation"]
        acc30 = ev.get("accuracy_30")
        n_played = ev.get("n", 0)
        if n_played < 6:          gate_min = 62   # chưa có bằng chứng → rất cẩn trọng
        elif acc30 is None:       gate_min = 62
        elif acc30 >= 0.58:       gate_min = 55   # đang ăn ngon → mở nhẹ
        elif acc30 >= 0.52:       gate_min = 59   # bằng mực → khắt khe
        elif acc30 >= 0.49:       gate_min = 63   # dưới mực nhẹ → siết
        else:                     gate_min = 67   # đang thua → gần như đóng cửa
        _goi_y = float(result.get("p_tai", 0.5))
        stick = getattr(self, "_stick_side", None)
        if stick and result["side"] != stick and abs(_goi_y - 0.5) < 0.015:
            # dao động nhỏ quanh 50% → giữ phía cũ, không lật loạn
            result["side"] = stick
            _goi_y = round(0.5 + 0.03 if stick == "TAI" else 0.5 - 0.03, 4)
            result["p_tai"] = _goi_y
            result["confidence"] = max(52, int(result["confidence"]) - 4)
            result["reasoning"] = "[GIỮ PHÍA] tín hiệu quá mờ (" + result["side"] + ") — không lật: " + str(result.get("reasoning", ""))[:120]
        # v16 — CHẾ ĐỘ KHÔNG-SKIP (mặc định BẬT, biến môi trường NO_SKIP=0 để tắt):
        # governor KHÔNG còn đóng cửa (side=None) nữa. Khi conf chưa đạt ngưỡng,
        # hệ thống vẫn ra 1 phía duy nhất theo thứ tự ưu tiên: phía ENGINE đang
        # chốt → phía đang giữ (hysteresis) → phiếu đa số của models.
        # v16.1: đổi thứ tự ưu tiên — trước đây ưu tiên "giữ phía cũ" nên cầu
        # đảo liên tục thì hệ đứng nguyên 1 phía và thua cả chuỗi.
        no_skip = os.getenv("NO_SKIP", "1").strip() != "0"
        if int(result["confidence"]) < gate_min or n_played < 4:
            ly_do_cam = ("chưa đủ dữ liệu tự học" if n_played < 4 else
                         f"conf {result['confidence']}% < ngưỡng {gate_min}% (acc30={acc30})")
            if no_skip:
                fb = result.get("side")
                if fb not in ("TAI", "XIU"):
                    fb = stick if stick in ("TAI", "XIU") else None
                if fb not in ("TAI", "XIU"):
                    tai_v = int(result.get("models_voted_tai", 0) or 0)
                    xiu_v = int(result.get("models_voted_xiu", 0) or 0)
                    fb = "TAI" if tai_v >= xiu_v else "XIU"
                result["side"] = fb
                result["confidence"] = max(51, min(60, int(result["confidence"]) or 51))
                result["p_tai"] = (round(max(float(result.get("p_tai", 0.5)), 0.51), 4) if fb == "TAI"
                                   else round(min(float(result.get("p_tai", 0.5)), 0.49), 4))
                result["governor"] = {"che_do": "NO-SKIP", "nguong_conf": gate_min,
                                      "acc30": acc30,
                                      "ly_do": "cấm skip — ra phía an toàn (" + ly_do_cam + ")"}
                result["reasoning"] = "[NO-SKIP] " + str(result.get("reasoning", ""))[:140]
                self._stick_side = fb
            else:
                result["governor"] = {"che_do": "CAM", "nguong_conf": gate_min,
                                      "acc30": acc30, "ly_do": ly_do_cam}
                result["side"] = None
                result["confidence"] = 0
                result["reasoning"] = f"[CAM] CHỜ — không đủ điều kiện phát tin ({ly_do_cam})"
                self._stick_side = None
        else:
            result["governor"] = {"che_do": "PLAY", "nguong_conf": gate_min, "acc30": acc30, "ly_do": "tín hiệu đạt chuẩn"}
            self._stick_side = result["side"]
        # v16.1 — AUTO-FLIP CHỐNG KẸT PHÍA: nếu k cuộc dự đoán gần nhất CÙNG
        # một phía và CẢ K đều thua (mặc định k=3) → hệ đang bị kẹt nhầm phía,
        # tự đảo chiều ngay thay vì bám phía cũ ra đến cùng. Áp dụng cả
        # khi governor đang PLAY lẫn NO-SKIP, nên không thể kẹt XỈU/TÀI mãi.
        _ps = list(self.pred_sides); _ht = list(self.hit)
        _k = int(os.getenv("FLIP_AFTER", "3"))
        if (_k >= 2 and len(_ps) >= _k and len(_ht) >= _k
                and _ps[-1] == _ps[-2] and all(s == _ps[-1] for s in _ps[-_k:])
                and not any(_ht[-_k:])):
            stuck = _ps[-1]
            result["side"] = _opp(stuck)
            result["p_tai"] = round(0.5 + (0.03 if stuck == "XIU" else -0.03), 4)
            result["confidence"] = max(int(result["confidence"]) or 55, 55)
            result["governor"] = {"che_do": "AUTO-FLIP", "nguong_conf": gate_min,
                                  "acc30": acc30,
                                  "ly_do": "cùng phía thua %d phiên liên tiếp (%s) → đảo chiều" % (_k, stuck)}
            result["reasoning"] = "[AUTO-FLIP] " + str(result.get("reasoning", ""))[:120]
            self._stick_side = result["side"]
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
        "trang_thai": "TÁC ĐỘNG (auto)" if prediction_side else "CHỜ",
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

# v12 MIGRATION: mọi key/gói cũ gắn GAME (mặc định "all" = dùng cả LC79 + Sunwin)
for _k in STORE["keys"].values():
    if "game" not in _k: _k["game"] = "all"
for _p in STORE["packages"].values():
    if not _p.get("game"): _p["game"] = "all"

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
        "P1":  {"name": "Gói 1 Ngày",  "icon": "🌞", "price": "30K",   "days": 1,  "max_devices": 1},
        "P3":  {"name": "Gói 3 Ngày",  "icon": "🌙", "price": "75K",   "days": 3,  "max_devices": 1},
        "P7":  {"name": "Gói 7 Ngày",  "icon": "📆", "price": "135K",  "days": 7,  "max_devices": 1},
        "P30": {"name": "Gói 30 Ngày", "icon": "🗓️", "price": "200K",  "days": 30, "max_devices": 1},
        "PLT": {"name": "Gói Vĩnh Viễn", "icon": "♾️", "price": "2.000K", "days": 0, "max_devices": 1},
    }.items():
        STORE["packages"][pid] = {"id": pid, **p}
else:
    for pid, dy in {"P1": 1, "P3": 3, "P7": 7, "P30": 30}.items():
        if pid not in STORE["packages"]:
            STORE["packages"][pid] = {"id": pid, "name": "Gói %d Ngày" % dy, "icon": "📆",
                                       "price": "", "days": dy, "max_devices": 1}
for _p in STORE["packages"].values(): _p.setdefault("hours", 0)
for _pid, _w in {"P1": "22K", "P3": "50K", "P7": "90K", "P30": "145K"}.items():
    if _pid in STORE["packages"]: STORE["packages"][_pid].setdefault("wholesale", _w)
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

# ── ĐỌC CẦU ĐA KHUNG — 3 TẦNG CHỐT ───────────────────────────────────────────
# Chỉ 3 tầng: 5 (cầu nhanh 1-1/2-2) · 12 (nhịp giữa) · 30 (cân bằng dài).
# Bài học từ bản 6-15 khung: khung càng nhiều phiếu càng loãng, quyết định càng
# nhiễu. 3 tầng đủ đọc cầu + CỔNG CONVICTION chặt (v11):
#   • mỗi khung phải đủ nguyên mẫu (n = w) mới được tính
#   • thiếu khung dữ liệu   → MULTIW BỎ PHIẾU (trả 0.5 = 0 tiếng nói)
#   • lệch mạnh < 2 khung   → MULTIW BỎ PHIẾU
#   • các khung lệch mạnh ngược hướng → MULTIW BỎ PHIẾU (không tự đảo loạn)
CAU_WINDOWS = (5, 12, 30)
# Muốn đổi bộ khung không cần sửa code: set env CAU_WINDOWS=5,12,30
try:
    _w_env = [int(x) for x in os.getenv("CAU_WINDOWS", "5,12,30").split(",") if x.strip()]
    if len(_w_env) >= 3 and all(2 <= x <= 200 for x in _w_env):
        CAU_WINDOWS = tuple(sorted(set(_w_env))[:5])
except Exception:
    pass
CAU_WINDOWS_LABEL = "/".join(str(x) for x in CAU_WINDOWS) + "p"

def cau_multi_consensus(seq, windows=CAU_WINDOWS):
    """Hợp nhất dự báo đa khung (mặc định 5/12/30) + CỔNG CONVICTION v11.
    Trả về (p_tai_hop_nhat, mo_ta_ngan, bang_chi_tiet_tung_khung)."""
    rows = []
    s_p = s_w = 0.0
    for w in windows:
        z = _zone_window(seq, w)
        n = z["so_phien"]
        if n < w:                           # khung phải đủ nguyên mẫu mới tính
            continue
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
    # CỔNG CONVICTION v11 (siết hơn bản 0.22-đơn-lẻ):
    #   1) đủ nguyên mẫu mọi khung      2) ≥ 2 khung lệch mạnh (do_manh ≥ 0.22)
    #   3) các khung lệch mạnh PHẢI CÙNG HƯỚNG — 5p tồng, 30p bẻ → bỏ phiếu, chờ
    # Chỉ thiếu 1 trong 3 → MULTIW BỎ PHIẾU (0.5 → logit = 0, không kéo bảng hợp nhất đi đâu cả)
    _strong = [r for r in rows if r["do_manh"] >= 0.22]
    _sides = {(1 if r["p_tai"] >= 0.53 else -1 if r["p_tai"] <= 0.47 else 0) for r in _strong}
    if len(rows) < len(windows) or len(_strong) < 2 or len(_sides) != 1:
        _thieu = "" if len(rows) == len(windows) else f" ({len(rows)}/{len(windows)} khung đủ mẫu)"
        _nho = "" if len(_strong) >= 2 else " · lệch mạnh <2 khung"
        _nen = " · khung mạnh ngược nhau" if len(_sides) > 1 else ""
        return 0.5, f"MULTIW chờ tín hiệu{_thieu}{_nho}{_nen}", rows
    tag = (f"{len(rows)} khung {CAU_WINDOWS_LABEL}: "
           f"TÀI {tai_c} · XỈU {xiu_c} · trung tính {len(rows)-tai_c-xiu_c} → nghiêng {p_out:.0%}")
    return p_out, tag, rows

def analyze_cau(seq):
    """Phân tầng cầu NGẮN (3-5 phiên) / TRUNG (6-15) / DÀI (>15)
    + BẢNG 3 TẦNG KHUNG (mặc định 5/12/30) + nhận dạng + khuyến nghị."""
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
    # Đa khung: 3 tầng khung chốt (mặc định 5/12/30)
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

# ── v17: LÕI THUẬT TOÁN MỚI — PHÂN TÍCH CHU KỲ NGẮN / TRUNG / DÀI ────────────
# Mỗi tầng tự đọc chu kỳ lặp chủ đạo của cửa sổ của nó (autocorrelation lag 1..6
# + nhịp run + vị trí trong chu kỳ), bỏ phiếu có trọng số vào dự đoán cuối.
def _autocorr_lag(bins, lag):
    """Tương quan tự động của chuỗi 0/1 tại khoảng cách `lag` phiên.
    Âm mạnh = cầu ĐẢO chu kỳ lẻ · Dương mạnh = cầu BÁM nhịp / bệt."""
    n = len(bins)
    if n <= lag + 2: return 0.0
    mu = sum(bins) / n
    num = sum((bins[i] - mu) * (bins[i - lag] - mu) for i in range(lag, n))
    den = sum((v - mu) ** 2 for v in bins)
    return num / den if den > 1e-9 else 0.0

def _cycle_layer(seq, window, tag, cap_lag=6):
    """Đọc 1 tầng chu kỳ trên `window` phiên gần nhất.
    Trả về chu kỳ chủ đạo (L phiên), kiểu vận hành ĐẢO/BÁM, vị trí hiện đang
    ở đâu trong chu kỳ run, và p_tai của tầng."""
    w = seq[-window:]
    n = len(w)
    if n < 8:
        return {"tang": tag, "window": window, "so_phien": n, "trang_thai": "THIÉU_DU_LIEU",
                "p_tai": None, "do_manh": 0.0, "mo_ta": tag + ": cần ≥ 8 phiên"}
    bins = [1 if v == "TAI" else 0 for v in w]
    # 1) Chu kỳ lặp chủ đạo: lag có tương quan mạnh nhất (1..6)
    best_lag, best_ac = 1, _autocorr_lag(bins, 1)
    for lag in range(2, cap_lag + 1):
        ac = _autocorr_lag(bins, lag)
        if abs(ac) > abs(best_ac): best_lag, best_ac = lag, ac
    last_side = w[-1]
    runs = _run_lengths_local(w)
    avg_run = sum(runs) / len(runs)
    cur_run = runs[-1]
    # 2) Vị trí trong chu kỳ run: đầu / giữa / quá hạn (run vượt trung bình chu kỳ)
    if cur_run > avg_run: vi_tri = "QUA_HAN"
    elif cur_run >= 2:    vi_tri = "GIUA_CHU_KY"
    else:                 vi_tri = "DAU_CHU_KY"
    # 3) Kiểu vận hành: ĐẢO (tương quan âm) / BÁM (tương quan dương) / hỏi data
    if best_ac <= -0.18:   loai_van, the = "ĐẢO", _opp(last_side)
    elif best_ac >= 0.18:  loai_van, the = "BÁM", last_side
    else:
        p_brk, _tg = _break_prob(w, cur_run)
        loai_van = "ĐẢO" if p_brk > 0.52 else "BÁM"
        the = _opp(last_side) if loai_van == "ĐẢO" else last_side
    strength = min(1.0, abs(best_ac) * 2.2)
    p = 0.5 + (0.10 if the == "TAI" else -0.10) * strength
    if vi_tri == "QUA_HAN":               # run đã dài hơn trung bình chu kỳ → nắn về phía gãy
        p += (-0.05 if the == last_side else 0.05)
    p = _clamp(p, 0.38, 0.62)
    mo_ta = "%s: chu kỳ L%d (%s) · run %d/%.1f phiên · %s" % (
        tag, best_lag, loai_van, cur_run, avg_run, vi_tri.replace("_", " ").lower())
    return {"tang": tag, "window": window, "so_phien": n, "trang_thai": "OK",
            "chu_ky": best_lag, "ac": round(best_ac, 3), "vanh": loai_van,
            "run_hien_tai": cur_run, "run_tb": round(avg_run, 2), "vi_tri": vi_tri,
            "phia": the, "p_tai": round(p, 3), "do_manh": round(strength, 3),
            "mo_ta": mo_ta}

def phan_tich_chu_ky_3_tang(seq):
    """v17 — LÕI HỢP NHẤT 3 TẦNG CHU KỲ:
      NGẮN  (12 phiên) — cầu nhanh 1-1 / 2-2, phản ứng tức thì, trọng số lớn nhưng nhiễu
      TRUNG (30 phiên) — nhịp giữa, keo giữa cầu nhanh và bệt
      DÀI   (60 phiên) — bệt / quy luật dài, ổn định nhưng trễ
    Tầng thiếu dữ liệu = không phiếu · tín hiệu yếu = trọng số tự giảm.
    Trả về p_tai hợp nhất + phía + bảng chi tiết 3 tầng."""
    specs = [("NGẮN", int(os.getenv("CK_NGAN", "12"))),
             ("TRUNG", int(os.getenv("CK_TRUNG", "30"))),
             ("DÀI", int(os.getenv("CK_DAI", "60")))]
    layers, s_p, s_w, names = [], 0.0, 0.0, []
    for tag, window in specs:
        ly = _cycle_layer(seq, window, tag)
        layers.append(ly)
        if ly.get("p_tai") is not None:
            base = {"NGẮN": 0.45, "TRUNG": 0.32, "DÀI": 0.23}[tag]
            wv = base * (0.35 + 0.65 * ly["do_manh"])
            s_p += ly["p_tai"] * wv; s_w += wv
            names.append("%s L%d %s→%s" % (tag, ly["chu_ky"], ly["vanh"], ly["phia"]))
    if s_w <= 0:
        return {"da_du_du_lieu": False, "tangs": layers, "side": None,
                "ghi_chu": "Chưa đủ dữ liệu để đọc chu kỳ (cần ≥ 12 phiên)"}
    p = s_p / s_w
    side = "TAI" if p >= 0.5 else "XIU"
    dong_thuan = sum(1 for ly in layers if ly.get("p_tai") is not None and ly.get("phia") == side)
    return {"da_du_du_lieu": True, "tangs": layers, "p_tai": round(p, 3),
            "side": side, "so_tang_chot": len(names), "dong_thuan": dong_thuan,
            "mo_ta": " · ".join(names) if names else "không tầng nào chốt"}

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
    """Kích hoạt key: POST {"key": ...} hoặc GET /makey?key=...&device=tên
    → trả token + quyền các bàn theo GAME của key (LC79 hoặc Sunwin)."""
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
                "calls_hu": 0, "calls_md5": 0, "calls_sunwin": 0}
            if dev_name: k["devices"][k["token"]]["name"] = dev_name
            if dev_id: k["devices"][k["token"]]["device_id"] = dev_id
    save_store()
    pk = STORE["packages"].get(k.get("package_id") or "", {})
    msg_tt = _payment_msg(k)
    # v12: mỗi GAME một loại key riêng — token chỉ mở các bàn của game key đó
    _codes = key_allowed_codes(k)
    return out({"ok": True,
                "tieude": "✅ KÍCH HOẠT THÀNH CÔNG!",
                "token": k["token"], "key": k["key"], "ten": k.get("name", ""),
                "goi": k.get("package_name") or pk.get("name", ""), "het_han": k.get("expires_at") or "Vĩnh viễn ♾️",
                "thoi_han": _dur_text(_key_dur_sec(k)), "con_lai_giay": (max(0, int(k["expires_ts"] - time.time())) if k.get("expires_ts") else None),
                "game": k.get("game") or "all",
                "quyen": _codes,
                "api_du_doan": {c: f"{BASE_URL}/api/{k['token']}/{c}" for c in _codes},
                "api_lich_su": {c: f"{BASE_URL}/api/{k['token']}/history/{c}" for c in _codes},
                "tin_nhan_thanh_toan": msg_tt,
                "lan_dau_kich_hoat": first})

# ═══════════════════════════════════════════════════════════════════════════════
#  API DỰ ĐOÁN (CẦN KEY ĐÃ KÍCH HOẠT)
# ═══════════════════════════════════════════════════════════════════════════════
@app.route("/api/<token>/<code>", methods=["GET", "OPTIONS"])
def api_predict(token, code):
    code = code.lower()
    if code not in URLS:
        return out({"ok": False, "loi": "not_found", "thong_bao": "Bàn không hợp lệ: " + ", ".join(URLS)}, 404)
    k = get_key_by_token(token)
    ok, msg = key_is_usable(k)
    if not ok:
        return out({"ok": False, "loi": "unauthorized", "thong_bao": msg, "huong_dan": "POST /makey {\"key\": ...}"}, 401)
    if not key_access_ok(k, code):
        return out({"ok": False, "loi": "wrong_game", "thong_bao": f"Key này loại {GAMES.get(k.get('game') or 'all', 'all')} — không mở được bàn {NAMES[code]}. Mua key riêng cho game đó nhé."}, 403)
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
                  "game": k.get("game") or "all", "ten_game": GAMES.get(k.get("game") or "all", "Tất cả"),
                  "con_lai": con_lai, "dieu_khoan": "1 key 1 game — " + GAMES.get(k.get("game") or "all", "Tất cả")}
    return out(res)

@app.route("/api/<token>/history/<code>")
def api_history(token, code):
    code = code.lower()
    if code not in URLS:
        return out({"ok": False, "loi": "not_found", "thong_bao": "Bàn không hợp lệ: " + ", ".join(URLS)}, 404)
    k = get_key_by_token(token)
    ok, msg = key_is_usable(k)
    if not ok:
        return out({"ok": False, "loi": "unauthorized", "thong_bao": msg}, 401)
    if not key_access_ok(k, code):
        return out({"ok": False, "loi": "wrong_game", "thong_bao": f"Key này không mở được bàn {NAMES[code]}"}, 403)
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
        "buoc_2_goi_du_doan_3_ban": {
            **{"phuong_thuc": "GET",
               "tra_ve": {"du_doan_tiep_theo": "phien_hien_tai.du_doan (TAI/XIU/null=CHỜ)", "do_tin_cay": "phien_hien_tai.do_tin_cay",
                          "ly_do": "tu_hoc + phan_tich_cau + ly_do chi tiết trong phien_hien_tai", "cau": "phien_hien_tai.cau (VD 1-2-1)"},
               "vi_du_js": "const r = await fetch('" + BASE_URL + "/api/' + token + '/hu').then(x=>x.json());\nalert(r.phien_hien_tai.du_doan);"},
            **{c: BASE_URL + "/api/<TOKEN>/" + c for c in URLS},
            **{"_luu_y_phan_quyen": "mỗi GAME một loại key riêng: key LC79 mở Hũ + MD5, key Sunwin mở Sunwin riêng"}},
        "buoc_3_lich_su": {**{c: BASE_URL + "/api/<TOKEN>/history/" + c + "?limit=50" for c in URLS}},
        "luu_y": ["mỗi game một key riêng: key LC79 (Hũ + MD5) và key Sunwin (bàn Sunwin) không thay thế nhau",
                   "Token sống theo key, hết hạn khi key hết hạn/bị khóa",
                   "API trả JSON in đẹp, thêm ?compact=1 để gọn"]})

@app.get("/ping")
def ping(): return out({"ok": True, "t": now_iso()})

@app.get("/")
def index():
    return out({"ok": True, "api": "PAW TX v14 STUDIO — 3 bàn (LC79 Hũ/MD5 + Sunwin) · key theo game · Governor ổn định (cấm mặc định) · nhịp run 1 đáp án · Gói + Đơn + CTV + Engine84 + 26 mẫu tin",
                "su_dung": ["1) Admin tạo gói & key (SLL theo đơn hàng) — chọn GAME cho key",
                             "2) Admin thêm CTV tại /admin → tab CTV (cấp quyền, hạn mức, gói)",
                             "3) CTV đăng nhập /ctv → tạo key (bắt buộc tên khách) → gửi tin nhắn cho khách",
                             "4) Khách POST /makey {\"key\": ...} → nhận token + đúng các bàn của game key đó",
                             "5) GET /api/<token>/hu · GET /api/<token>/md5 · GET /api/<token>/sunwin"],
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
                threading.Thread(target=_ctv_enforce_loop, daemon=True).start()

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

_adm_fails, _adm_block = {}, {}

def _client_ip():
    return (request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.remote_addr or "0.0.0.0")

def _adm_blocked(ip):
    return _adm_block.get(ip, 0) > time.time()

def _adm_fail(ip):
    now = time.time()
    lst = [t for t in _adm_fails.get(ip, []) if now - t < 900]
    lst.append(now); _adm_fails[ip] = lst
    if len(lst) >= 8: _adm_block[ip] = now + 900

def _adm_ok(ip):
    _adm_fails.pop(ip, None); _adm_block.pop(ip, None)

@app.get("/admin/api/authinfo")
def adm_authinfo():
    """Cho trang đăng nhập biết đã cấu hình ADMIN_PASSWORD chưa (không lộ giá trị)."""
    return out({"ok": True, "has_password": bool(ADMIN_PASSWORD)})

@app.post("/admin/login")
def admin_login():
    ip = _client_ip()
    if _adm_blocked(ip):
        return out({"ok": False, "thong_bao": "Sai quá nhiều lần — thử lại sau 15 phút"}, 429)
    if not ADMIN_PASSWORD:
        return out({"ok": False, "thong_bao": "Chưa đặt ADMIN_PASSWORD trên Render (Environment → thêm biến rồi redeploy)"}, 503)
    j = request.get_json(silent=True) or request.form
    pw = str(j.get("pw", "") or "")
    if pw and hmac.compare_digest(pw.encode(), ADMIN_PASSWORD.encode()):
        _adm_ok(ip)
        session["adm"] = True; session["adm_until"] = time.time() + 10 * 3600
        return out({"ok": True, "thong_bao": "Đăng nhập thành công"})
    _adm_fail(ip)
    return out({"ok": False, "thong_bao": "Sai mật khẩu"}, 401)

@app.get("/admin/login")
def admin_login_get():
    """Đường dự phòng: mở thẳng .../admin/login?pw=MATKHAU để vào luôn."""
    ip = _client_ip()
    if ADMIN_PASSWORD and not _adm_blocked(ip) and hmac.compare_digest(str(request.args.get("pw", "")).encode(), ADMIN_PASSWORD.encode()):
        _adm_ok(ip)
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
    _adm_kid = STORE.get("admin_key", "")
    admk = STORE["keys"].get(_adm_kid)
    if admk is None and _adm_kid:
        admk = STORE["keys"].setdefault(_adm_kid, {"id": _adm_kid, "key": _adm_kid, "role": "admin",
                                                   "created_at": now_iso(), "status": "active"})
    admk = admk or {}
    if not admk.get("token"):
        admk["token"] = secrets.token_urlsafe(24); save_store()
    tables = []
    for c, t in TABLES.items():
        tk = stats(list(t.hist))
        pt = {}
        try:
            _eng = getattr(getattr(t, "brain", None), "engine", None)
            _seq = list(getattr(_eng, "seq", []) or [])
            _sums = list(getattr(_eng, "sums", []) or [])
            if _seq:
                _ck = analyze_chu_ky(_seq, _sums)
                pt = {"du_doan": _ck.get("du_doan"), "do_tin_cay": _ck.get("do_tin_cay"),
                      "nhip": _ck.get("nhip"), "do_thuan": _ck.get("do_thuan"),
                      "trang_thai": _ck.get("trang_thai"),
                      "backtest": (_ck.get("backtest") or {}), "ket_luan": _ck.get("ket_luan")}
        except Exception as _e:
            pt = {"loi": str(_e)[:80]}
        tables.append({"code": c, "ten": t.name, "game": GAME_OF.get(c, ""), "bat": t.enabled, "phien_hien_tai": t.last_id,
                       "loi": t.err, "luoi_ms": t.ms,
                       "du_doan_tiep": (t.pending or {}).get("du_doan"),
                       "phan_tich": pt,
                       "ty_le_thang": tk["ty_le"], "thang": tk["win"], "thua": tk["lose"]})
    doanh_thu_orders = len(STORE["orders"])
    return {"so_key": len(keys), "da_kich_hoat": sum(1 for k in keys if k.get("activated")),
            "het_han": sum(1 for k in keys if key_status(k) == "hết hạn"),
            "dang_hoat_dong": sum(1 for k in keys if key_status(k) == "hoạt động"),
            "luot_goi_hu": sum(_to_int(k.get("calls_hu")) for k in STORE["keys"].values()),
            "luot_goi_md5": sum(_to_int(k.get("calls_md5")) for k in STORE["keys"].values()),
            "luot_goi_sunwin": sum(_to_int(k.get("calls_sunwin")) for k in STORE["keys"].values()),
            "so_goi": len(STORE["packages"]), "so_don_hang": doanh_thu_orders,
            "key_admin_console": {"key": STORE.get("admin_key", ""), "token": admk.get("token", ""),
                                   "api_history": f"/api/{admk.get('token', '')}/history/hu"},
            "doanh_thu_k": sum(_money_k(k.get("price")) for k in keys),
            "so_ctv": len(STORE.get("ctvs") or {}),
            "sap_het_han": sum(1 for k in keys if k.get("expires_ts") and 0 < k["expires_ts"] - time.time() < 86400 and key_status(k) == "hoạt động"),
            "key_theo_ngay": _keys_per_day(14),
            "gist_backup": bool(GIST_TOKEN and GIST_ID),
            "ban": tables, "cap_nhat": now_iso()}

def _keys_per_day(n=14):
    base = datetime.now(VN).date(); cnt = defaultdict(int)
    for k in STORE["keys"].values():
        if k.get("role") != "admin": cnt[(k.get("created_at") or "")[:10]] += 1
    return [[(base - timedelta(days=i)).strftime("%m-%d"), cnt[(base - timedelta(days=i)).strftime("%Y-%m-%d")]] for i in range(n - 1, -1, -1)]

@app.get("/admin/api/export.csv")
def adm_export():
    g = guard()
    if g: return g
    import csv, io
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["key", "khach", "goi", "gia", "trang_thai", "thoi_han", "tao_luc", "kich_hoat", "het_han", "don_hang", "nguoi_tao", "loai_game", "goi_hu", "goi_md5", "goi_sunwin"])
    for k in sorted(STORE["keys"].values(), key=lambda x: x.get("created_at", ""), reverse=True):
        if k.get("role") == "admin": continue
        w.writerow([k["key"], k.get("name", ""), k.get("package_name", ""), k.get("price", ""), key_status(k),
                    _dur_text(_key_dur_sec(k)), k.get("created_at", ""), k.get("activated_at") or "", k.get("expires_at") or "",
                    k.get("order_id", ""), k.get("by", "admin"), (k.get("game") or "all"), k.get("calls_hu", 0),
                    k.get("calls_md5", 0), k.get("calls_sunwin", 0)])
    r = make_response("\ufeff" + buf.getvalue(), 200)
    r.headers["Content-Type"] = "text/csv; charset=utf-8"
    r.headers["Content-Disposition"] = "attachment; filename=paw_keys_%s.csv" % datetime.now(VN).strftime("%Y%m%d_%H%M")
    return r

@app.post("/admin/api/keys-bulk")
def adm_bulk():
    g = guard()
    if g: return g
    d = request.get_json(silent=True) or {}
    ids = [str(x) for x in (d.get("ids") or [])][:500]; act = d.get("action"); n = 0
    for kid in ids:
        k = STORE["keys"].get(kid)
        if not k or k.get("role") == "admin": continue
        if act == "ban": k["status"] = "banned"; n += 1
        elif act == "active": k["status"] = "active"; n += 1
        elif act == "delete":
            del STORE["keys"][kid]; n += 1
            for o in STORE["orders"].values():
                if kid in o.get("keys", []): o["keys"].remove(kid)
    save_store()
    return out({"ok": True, "thong_bao": "Đã xử lý %d key" % n, "so_key": n})

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
    p = STORE["packages"].setdefault(pid, {"id": pid, "name": "", "icon": "", "price": "", "days": 30, "hours": 0, "max_devices": 1, "game": "all"})
    for f in ("name", "icon", "price", "wholesale"):
        if d.get(f) is not None and str(d[f]).strip() != "": p[f] = str(d[f]).strip()
    if str(d.get("game", "")).strip().lower() in GAMES: p["game"] = str(d["game"]).strip().lower()
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

# ── Tạo key SLL + đơn hàng (dùng chung ADMIN + CTV) ──
def create_keys_batch(d, owner="admin"):
    """Sinh key + đơn hàng. owner = 'admin' hoặc 'ctv:<username>'.
    Trả về (resp_dict, http_status)."""
    count = max(1, min(200, _to_int(d.get("count", 1), 1)))
    pk = STORE["packages"].get(str(d.get("package_id", "")).strip().upper())
    prefix = (str(d.get("prefix") or STORE["settings"]["default_prefix"]).strip()[:6]).upper() or "PAXU"
    # v12: GAME của key — client chọn, ưu tiên chọn của client => gói => tất cả
    _g = str(d.get("game", "")).strip().lower()
    _pg = str((pk or {}).get("game", "all") or "all")
    game = _g if _g in GAMES else (_pg if _pg in GAMES else "all")
    # Thời hạn: vĩnh viễn > tự nhập ngày/giờ > gói. (duration_days = tương thích bản cũ)
    has_days  = str(d.get("days", "")).strip() != ""
    has_hours = str(d.get("hours", "")).strip() != ""
    if d.get("permanent") in (True, 1, "1", "true"):
        sec, label = None, "Vĩnh viễn"
    elif has_days or has_hours:
        sec = min(3650, _to_int(d.get("days"))) * 86400 + min(100000, _to_int(d.get("hours"))) * 3600
        if sec <= 0: return {"ok": False, "thong_bao": "Nhập số ngày hoặc số giờ lớn hơn 0"}, 400
        label = "Tuỳ chỉnh · " + _dur_text(sec)
    elif str(d.get("duration_days", "")).strip() != "":
        sec = _to_int(d["duration_days"]) * 86400 or None
        label = "Tuỳ chỉnh · " + _dur_text(sec)
    elif pk:
        sec, label = _pkg_sec(pk), pk["name"]
    else:
        return {"ok": False, "thong_bao": "Chọn gói, hoặc nhập số ngày/giờ"}, 400
    price = str(d["price"]).strip() if str(d.get("price", "")).strip() else (pk["price"] if pk else "")
    name = str(d.get("name", "")).strip()
    note = str(d.get("note", ""))
    max_dev = _to_int(d.get("max_devices"), 0) or (pk.get("max_devices", 1) if pk else 1)
    oid = "DH" + datetime.now(VN).strftime("%y%m%d") + "-" + uuid.uuid4().hex[:5].upper()
    STORE["orders"][oid] = {"id": oid, "khach": name or "Khách lẻ", "package": label,
                             "price": price, "so_key": count, "ngay_tao": now_iso(),
                             "trang_thai": "mới", "thoi_han": _dur_text(sec), "keys": [],
                             "by": owner}
    created = []
    for _ in range(count):
        key = _gen_key(prefix)
        while key in STORE["keys"]: key = _gen_key(prefix)
        k = _new_key(key, prefix, {"id": pk["id"], "price": price, "days": 0} if (pk and not (has_days or has_hours)) else None, name, note, oid, game=game)
        k["price"] = price; k["max_devices"] = max_dev
        k["duration_sec"] = sec; k["duration_days"] = (sec // 86400 or None) if sec else None
        k["package_name"] = label
        k["package_id"] = pk["id"] if (pk and label == pk["name"]) else ""
        k["by"] = owner
        STORE["keys"][key] = k
        STORE["orders"][oid]["keys"].append(key)
        created.append(key)
    save_store()
    msgs = [{"key": kk, "tin_nhan": _payment_msg(STORE["keys"][kk])} for kk in created]
    return ({"ok": True, "don_hang": oid, "da_tao": len(created), "goi": label, "thoi_han": _dur_text(sec),
             "tin_nhan_thanh_toan": msgs,
             "tin_nhan_gop": "\n\n".join(m["tin_nhan"] for m in msgs) if len(msgs) > 1 else msgs[0]["tin_nhan"]}, 200)

@app.post("/admin/api/keys")
def adm_create():
    g = guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    r, st = create_keys_batch(d, "admin")
    return out(r, st)

@app.get("/admin/api/keys")
def adm_keys():
    g = guard()
    if g: return g
    ks = [_key_public(k) for k in sorted(STORE["keys"].values(), key=lambda x: x.get("created_at") or "", reverse=True)]
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
    ords = sorted(STORE["orders"].values(), key=lambda o: o.get("ngay_tao") or "", reverse=True)
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
    if d.get("bill_ok"): o["bill_ok"] = True
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
    try: res["chu_ky"] = analyze_chu_ky(list(t.brain.engine.seq), list(getattr(t.brain.engine, "sums", [])))
    except Exception as _e: res["chu_ky"] = {"da_du_du_lieu": False, "ghi_chu": "lỗi phân tích: %s" % _e}
    return out(res)

# ═══════════════════════════════════════════════════════════════════════════════
#  CTV — CỘNG TÁC VIÊN. Admin tạo tk + cấp quyền; CTV bán key bên dưới,
#  mỗi key gắn tài khoản CTV; admin theo dõi chi tiết, hạn mức, nhật ký.
# ═══════════════════════════════════════════════════════════════════════════════
CTV_PERM_DEFS = [
    ("create_key",   "Tạo key"),
    ("lock_key",     "Khóa / mở key do mình tạo"),
    ("extend_key",   "Cộng thời hạn key do mình tạo"),
    ("custom_price", "Tự nhập giá bán khác giá gói"),
    ("see_calls",    "Xem lượt gọi API của key"),
]
DEFAULT_CTV_PERMS = {"create_key": True, "lock_key": False, "extend_key": False,
                     "custom_price": False, "see_calls": False}

def _hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(8)
    h = hmac.new(salt.encode(), (pw or "").encode(), hashlib.sha256).hexdigest()
    return "%s$%s" % (salt, h)

def _check_pw(pw, stored):
    try: ok = hmac.compare_digest(_hash_pw(pw, str(stored or "").split("$", 1)[0]).split("$", 1)[1],
                                  str(stored or "").split("$", 1)[1])
    except Exception: ok = False
    return ok

def _pkg_list(v):
    if isinstance(v, (list, tuple)): return sorted({str(x).strip().upper() for x in v if str(x).strip()})
    return sorted({x.strip().upper() for x in str(v or "").split(",") if x.strip()})

def _money_k(s):
    """'250K'/'2.000K' → số K gần đúng để ước doanh thu (chỉ để hiển thị)."""
    return _to_int(str(s or "").lower().replace("k", "").replace(".", "").replace(",", "").strip() or "0")

def _ctv_log(u, action, detail=""):
    try:
        log = STORE.setdefault("ctvlog", [])
        log.append({"ctv": u, "action": action, "detail": str(detail)[:200], "at": now_iso()})
        del log[:-500]
    except Exception: pass

SETTLE_FROM = min(22, max(0, _to_int(os.getenv("SETTLE_FROM", "20"), 20)))   # mở khung thu tiền
SETTLE_TO   = min(23, max(1, _to_int(os.getenv("SETTLE_TO", "22"), 22)))     # CHỐT: quá giờ này còn nợ → thu hồi key
SETTLE_LABEL = "%02d:00–%02d:00" % (SETTLE_FROM, SETTLE_TO)

def _ctv_outstanding(u):
    """Đơn còn nợ theo FIFO: tiền CTV đã trả trừ vào đơn cũ nhất trước."""
    c = (STORE.get("ctvs") or {}).get(u) or {}
    left = _to_int(c.get("paid_k")); res = []
    for o in sorted((o for o in STORE["orders"].values() if o.get("by") == "ctv:" + u), key=lambda o: o.get("ngay_tao", "")):
        cost = _to_int(o.get("cost_k"))
        if left >= cost: left -= cost; continue
        res.append((o, cost - left)); left = 0
    return res

def _ctv_debt_info(c):
    u = c["username"]; now = datetime.now(VN); today = now.strftime("%Y-%m-%d")
    out_ = _ctv_outstanding(u)
    no = sum(r for _, r in out_)
    qua = sum(r for o, r in out_ if (o.get("ngay_tao") or "")[:10] < today
              or (now.hour >= SETTLE_TO and (o.get("ngay_tao") or "")[:10] == today))
    lim = c.get("credit_limit_k"); lim = 500 if lim is None else _to_int(lim)
    mine = [o for o in STORE["orders"].values() if o.get("by") == "ctv:" + u]
    op = _open_slip(u); cho_duyet = bool(op and op.get("status") == "cho_duyet")
    dl = now.replace(hour=SETTLE_TO, minute=0, second=0, microsecond=0)
    lock = c.get("debt_lock")
    ly_do = ""
    if lock:
        ly_do = "Đã THU HỒI %d key + khóa chức năng vì nợ quá hạn — thanh toán, bấm \"Đã thanh toán\" và chờ admin duyệt để mở lại toàn bộ" % _to_int(lock.get("keys"))
    elif qua > 0:
        ly_do = "Còn nợ quá hạn %dK — thanh toán cho admin để mở lại quyền tạo key" % qua
    return {"no_k": no, "qua_han_k": qua, "han_muc_k": lim, "con_duoc_no_k": max(0, lim - no),
            "da_tra_k": _to_int(c.get("paid_k")), "tong_nhap_k": sum(_to_int(o.get("cost_k")) for o in mine),
            "don_chua_bill": sum(1 for o in mine if not o.get("bill")),
            "khoa_tao_key": qua > 0 or bool(lock), "ly_do": ly_do, "khung_thu_tien": SETTLE_LABEL,
            "chot": "%02d:00" % SETTLE_TO, "giay_con_lai": max(0, int((dl - now).total_seconds())) if now < dl else 0,
            "thu_hoi": bool(lock), "cho_duyet": cho_duyet}

# ═══════════════════════════════════════════════════════════════════════════════
#  v9 · THANH TOÁN CTV — Đơn thanh toán điện tử + QR BIDV VietQR + admin duyệt tay
#       + TỰ ĐỘNG THU HỒI toàn bộ key & khóa chức năng khi quá hạn chưa thanh toán
# ═══════════════════════════════════════════════════════════════════════════════
PAY_BANK = {"ten": os.getenv("PAY_BANK_NAME", "BIDV"),
            "ten_day_du": os.getenv("PAY_BANK_FULL", "Ngân hàng TMCP Đầu tư và Phát triển Việt Nam"),
            "bin": os.getenv("PAY_BIN", "970418"),
            "stk": os.getenv("PAY_ACC", "8970267100"),
            "chu_tk": os.getenv("PAY_HOLDER", "NGUYEN VAN HOA")}
PAY_QR_B64 = "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/wBRXX5nJ9lWc8vrPypy+s/KgrG9iuQ/1Fdfmcn2U9iuQ/1Fdfmcn2VZzy+s/KnL6z8qCt/C8Yv0WY2KSSyXRkbK+BznOpJAABI3ZJ0rBszjdLh1+jYxz3voahrWtGy4mN2gB4rNcvrPyppBXBhmMX6LMLHJLZLmxjK+Auc6jkAAEjSSTyqwfMmOkxC9sja573UM7Q1o2STG7QA8VmNH0rU9kFY7sVyHpqxXX5lJ9lZTFMYv8eT2d8lkujWNrIXOc6kkAADxsn3Ksj16SflTXrKDUIiICxuTNc7Hbo1gcXGllAA6knkKySFBWM7Fch3/ABFdfmcn2V38exe/sv1tc+x3QNbUxEk0cnQc4/sqynXrPypr1lBj8gaX2G5NYHOc6mlAA6k+4KrX9iuQ/wBRXX5nJ9lWcaTXrPyoK0rPi+QMu1E51juoAnYSTRydPdD+yrIbsC601obskwyAAdd+5K7nL6ymkFY5xXId/wARXX5nJ9laexXIf6iuvzOT7Ks516ynL6z8qCtG04vf2XOkc6x3UATMJJo5P6Q/sqyStBNtnABJMLhofirta9BTSCs6jxbIG10BNiuoAkbv+85PT+KrMR1Tl9Z+VahA0uC4DdDUADZ8m79hXOiCs9uLX/7og/cK668rv8Ck/pfiqyyn/wAhHvf3o/Yt+vWflWoQNLjqP8hJ+Kf2LkQoKz5cWyD7ovd9w7rrypP4HL/S/FVktMCLZEDsEQga/wBldrl9Z+VNIK0K7FsgdcJyLHdSDK4/gcn9I/2VZTQAihpwRoiNvQ/EFzaO+61HZAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBETaAibTaAiIgIiICIiAibRAREQETaICIiAiJtARNptAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQEREBERAREQdG+1j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"      # ảnh QR tĩnh dự phòng (nếu trình duyệt không vẽ được QR động)

def _emv(tag, val): return "%s%02d%s" % (tag, len(val), val)

def _crc16(s):
    crc = 0xFFFF
    for ch in s.encode():
        crc ^= ch << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return "%04X" % crc

def vietqr_payload(amount_vnd, content):
    """Chuỗi VietQR động (chuẩn Napas247 / EMVCo) — điền sẵn số tiền + nội dung chuyển khoản."""
    guid = (_emv("00", "A000000727")
            + _emv("01", _emv("00", PAY_BANK["bin"]) + _emv("01", PAY_BANK["stk"]))
            + _emv("02", "QRIBFTTA"))
    body = _emv("00", "01") + _emv("01", "12") + _emv("38", guid) + _emv("53", "704")
    if amount_vnd and amount_vnd > 0: body += _emv("54", str(int(amount_vnd)))
    body += _emv("58", "VN")
    content = "".join(ch for ch in str(content or "").upper() if ch.isalnum() or ch == " ")[:25]
    if content: body += _emv("62", _emv("08", content))
    body += "6304"
    return body + _crc16(body)

def _ctv_slips(u):
    return sorted((s for s in (STORE.get("ctvpays") or {}).values() if s.get("ctv") == u),
                  key=lambda s: s.get("created_at", ""), reverse=True)

def _open_slip(u):
    for s in _ctv_slips(u):
        if s.get("status") in ("cho_ck", "cho_duyet"): return s
    return None

def _new_slip_id():
    pays = STORE.setdefault("ctvpays", {})
    while True:
        sid = "TT" + datetime.now(VN).strftime("%d%m") + "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(4))
        if sid not in pays: return sid

def _ensure_slip(c):
    """Mỗi CTV tối đa 1 phiếu đang mở. Phiếu 'chờ chuyển khoản' tự cập nhật theo công nợ hiện tại."""
    u = c["username"]; inf = _ctv_debt_info(c); cur = _open_slip(u)
    if cur and cur["status"] == "cho_duyet": return cur
    if inf["no_k"] <= 0:
        if cur: cur["status"] = "huy"; cur["admin_note"] = "Hết nợ"; save_store()
        return None
    if cur and _to_int(cur.get("amount_k")) == inf["no_k"]: return cur
    if cur: cur["status"] = "huy"; cur["admin_note"] = "Công nợ đổi → phiếu mới"
    sid = _new_slip_id()
    s = {"id": sid, "ctv": u, "amount_k": inf["no_k"], "status": "cho_ck", "created_at": now_iso(),
         "noi_dung": "PAW" + sid, "bill": "", "note": "", "paid_at": "", "approved_at": "", "admin_note": "", "got_k": 0,
         "orders": [{"id": o["id"], "khach": o.get("khach", ""), "con_no_k": r} for o, r in _ctv_outstanding(u)][:60]}
    pays = STORE.setdefault("ctvpays", {}); pays[sid] = s
    if len(pays) > 800:      # dọn phiếu cũ đã xong
        for k_ in sorted((k for k, v in pays.items() if v["status"] in ("da_duyet", "tu_choi", "huy")),
                         key=lambda k: pays[k].get("created_at", ""))[:len(pays) - 700]:
            pays.pop(k_, None)
    save_store()
    return s

def _slip_view(s):
    if not s: return None
    amt = _to_int(s.get("amount_k")); sid = s["id"]
    c = (STORE.get("ctvs") or {}).get(s.get("ctv")) or {}
    return {"id": sid, "ma": "TT-%s-%s" % (sid[2:6], sid[6:]), "ctv": s.get("ctv"), "ctv_ten": c.get("name", ""),
            "so_tien_k": amt, "noi_dung": s.get("noi_dung", ""), "trang_thai": s.get("status"),
            "tao_luc": s.get("created_at"), "bao_luc": s.get("paid_at", ""), "duyet_luc": s.get("approved_at", ""),
            "bill": s.get("bill", ""), "ghi_chu": s.get("note", ""), "ghi_chu_admin": s.get("admin_note", ""),
            "thuc_nhan_k": _to_int(s.get("got_k")), "don": s.get("orders", []),
            "payload": vietqr_payload(amt * 1000, s.get("noi_dung", "")) if s.get("status") in ("cho_ck", "cho_duyet") else ""}

# ── THU HỒI / KHÔI PHỤC KEY THEO CÔNG NỢ ──
def _ctv_revoke_all(c):
    u = c["username"]; n = 0; ts = time.time()
    for k in STORE["keys"].values():
        if k.get("by") == "ctv:" + u and k.get("status") != "banned" and key_status(k) != "hết hạn":
            k["status"] = "banned"; k["revoked_debt"] = True; k["revoked_ts"] = ts; n += 1
    return n

def _ctv_restore_all(c):
    u = c["username"]; n = 0; now = time.time()
    for k in STORE["keys"].values():
        if k.get("by") == "ctv:" + u and k.get("revoked_debt"):
            gap = max(0, now - (k.get("revoked_ts") or now))
            if k.get("expires_ts") and k["expires_ts"] > (k.get("revoked_ts") or now):   # bù thời gian bị thu hồi cho khách
                k["expires_ts"] += gap
                k["expires_at"] = datetime.fromtimestamp(k["expires_ts"], VN).replace(microsecond=0).isoformat()
            k["status"] = "active"; k.pop("revoked_debt", None); k.pop("revoked_ts", None); n += 1
    return n

def _ctv_enforce(c):
    """Quá hạn + chưa báo thanh toán → thu hồi TOÀN BỘ key + khóa chức năng.
       Hết nợ quá hạn (admin đã duyệt/thu tiền) → mở lại key + chức năng."""
    u = c["username"]; inf = _ctv_debt_info(c); op = _open_slip(u)
    pending = bool(op and op.get("status") == "cho_duyet"); changed = False
    if inf["qua_han_k"] > 0 and not pending and not c.get("debt_lock"):
        n = _ctv_revoke_all(c)
        c["debt_lock"] = {"at": now_iso(), "keys": n, "qua_han_k": inf["qua_han_k"]}
        _ctv_log(u, "auto_thu_hoi", "%d key · quá hạn %dK" % (n, inf["qua_han_k"])); changed = True
    elif inf["qua_han_k"] <= 0 and c.get("debt_lock"):
        n = _ctv_restore_all(c); c.pop("debt_lock", None)
        _ctv_log(u, "auto_mo_lai", "%d key được khôi phục" % n); changed = True
    if changed: save_store()
    return changed

def _ctv_enforce_loop():
    while True:
        try:
            for c in list((STORE.get("ctvs") or {}).values()): _ctv_enforce(c)
        except Exception: pass
        time.sleep(30)

# ── CTV · API thanh toán ──
@app.get("/pay/qr.jpg")
def pay_qr_static():
    r = make_response(base64.b64decode(PAY_QR_B64), 200)
    r.headers["Content-Type"] = "image/jpeg"; r.headers["Cache-Control"] = "public, max-age=86400"
    return r

@app.get("/ctv/api/pay")
def ctv_pay():
    c, g = ctv_guard()
    if g: return g
    s = _ensure_slip(c); cur_id = s["id"] if s else ""
    hist = [_slip_view(x) for x in _ctv_slips(c["username"]) if x["status"] in ("da_duyet", "tu_choi") and x["id"] != cur_id][:10]
    return out({"ok": True, "cong_no": _ctv_debt_info(c), "phieu": _slip_view(s), "lich_su": hist, "bank": PAY_BANK})

@app.post("/ctv/api/pay/<pid>/paid")
def ctv_pay_paid(pid):
    c, g = ctv_guard()
    if g: return g
    s = (STORE.get("ctvpays") or {}).get(pid)
    if not s or s.get("ctv") != c["username"]: return out({"ok": False, "thong_bao": "Không tìm thấy phiếu của bạn"}, 404)
    if s["status"] != "cho_ck": return out({"ok": False, "thong_bao": "Phiếu này không ở trạng thái chờ chuyển khoản"}, 400)
    d = request.get_json(silent=True) or request.form
    bill = str(d.get("bill", "")).strip()
    if len(bill) < 4: return out({"ok": False, "thong_bao": "Nhập mã giao dịch / link ảnh bill chuyển khoản (tối thiểu 4 ký tự)"}, 400)
    s["status"] = "cho_duyet"; s["bill"] = bill[:300]; s["note"] = str(d.get("note", "")).strip()[:200]; s["paid_at"] = now_iso()
    _ctv_log(c["username"], "bao_da_thanh_toan", "%s · %dK" % (pid, _to_int(s.get("amount_k")))); save_store()
    return out({"ok": True, "thong_bao": "✅ Đã gửi — chờ admin kiểm tra tiền & duyệt. Trong lúc chờ, key của bạn không bị thu hồi."})

@app.post("/ctv/api/pay/<pid>/undo")
def ctv_pay_undo(pid):
    c, g = ctv_guard()
    if g: return g
    s = (STORE.get("ctvpays") or {}).get(pid)
    if not s or s.get("ctv") != c["username"]: return out({"ok": False, "thong_bao": "Không tìm thấy phiếu của bạn"}, 404)
    if s["status"] != "cho_duyet": return out({"ok": False, "thong_bao": "Phiếu không ở trạng thái chờ duyệt"}, 400)
    s["status"] = "cho_ck"; s["paid_at"] = ""
    _ctv_log(c["username"], "huy_bao_thanh_toan", pid); save_store()
    return out({"ok": True, "thong_bao": "Đã hủy báo — bạn có thể sửa bill rồi gửi lại"})

# ── ADMIN · duyệt thanh toán ──
@app.get("/admin/api/pays")
def adm_pays():
    g = guard()
    if g: return g
    allp = sorted((STORE.get("ctvpays") or {}).values(), key=lambda s: s.get("paid_at") or s.get("created_at", ""), reverse=True)
    pend = [s for s in allp if s["status"] == "cho_duyet"]
    if request.args.get("brief"): return out({"ok": True, "cho_duyet": len(pend)})
    return out({"ok": True, "cho_duyet": [_slip_view(s) for s in pend],
                "lich_su": [_slip_view(s) for s in allp if s["status"] in ("da_duyet", "tu_choi")][:40]})

@app.post("/admin/api/pays/<pid>")
def adm_pay_act(pid):
    g = guard()
    if g: return g
    s = (STORE.get("ctvpays") or {}).get(pid)
    if not s: return out({"ok": False, "thong_bao": "Không có phiếu " + pid}, 404)
    if s["status"] != "cho_duyet": return out({"ok": False, "thong_bao": "Phiếu không ở trạng thái chờ duyệt"}, 400)
    d = request.get_json(silent=True) or request.form
    act = str(d.get("action", "")); note = str(d.get("note", "")).strip()[:200]
    c = (STORE.get("ctvs") or {}).get(s["ctv"])
    if act == "approve":
        amt = _to_int(d.get("amount_k")) or _to_int(s.get("amount_k"))
        if amt <= 0: return out({"ok": False, "thong_bao": "Số tiền thực nhận phải > 0"}, 400)
        if c:
            c["paid_k"] = _to_int(c.get("paid_k")) + amt
            c.setdefault("payments", []).append({"at": now_iso(), "amount_k": amt, "note": ("Phiếu %s %s" % (pid, note)).strip()[:120]})
            del c["payments"][:-100]
        s["status"] = "da_duyet"; s["approved_at"] = now_iso(); s["got_k"] = amt; s["admin_note"] = note
        _ctv_log(s["ctv"], "admin_duyet_tt", "%s · %dK" % (pid, amt)); save_store()
        restored = bool(c and _ctv_enforce(c) and not c.get("debt_lock"))
        inf = _ctv_debt_info(c) if c else {"no_k": 0}
        return out({"ok": True, "thong_bao": "Đã duyệt %dK · còn nợ %dK%s" % (amt, inf["no_k"], " · đã MỞ LẠI key + chức năng" if restored else "")})
    if act == "reject":
        s["status"] = "tu_choi"; s["approved_at"] = now_iso(); s["admin_note"] = note or "Không nhận được tiền"
        _ctv_log(s["ctv"], "admin_tu_choi_tt", pid); save_store()
        if c: _ctv_enforce(c)
        locked = bool(c and c.get("debt_lock"))
        return out({"ok": True, "thong_bao": "Đã từ chối phiếu" + (" · CTV đang quá hạn → key đã bị THU HỒI" if locked else "")})
    return out({"ok": False, "thong_bao": "action phải là approve hoặc reject"}, 400)

def ctv_authed():
    u = session.get("ctv")
    if not u: return None
    c = (STORE.get("ctvs") or {}).get(u)
    return c if (c and c.get("status") == "active") else None

def ctv_guard():
    c = ctv_authed()
    if not c: return None, out({"ok": False, "loi": "unauthorized", "thong_bao": "Chưa đăng nhập CTV"}, 401)
    try: _ctv_enforce(c)
    except Exception: pass
    return c, None

def _ctv_public(c):
    u = c["username"]
    keys = [k for k in STORE["keys"].values() if k.get("by") == "ctv:" + u]
    return {"username": u, "ten": c.get("name", ""),
            "trang_thai": "hoạt động" if c.get("status") == "active" else "bị khóa",
            "quyen": dict(DEFAULT_CTV_PERMS, **(c.get("perms") or {})),
            "goi_duoc_cap": c.get("allowed_packages", []),
            "prefix": c.get("key_prefix", ""), "hoa_hong": c.get("commission_pct", 0),
            "cap_key_ngay": c.get("max_keys_per_day", 0), "ghi_chu": c.get("note", ""),
            "ngay_tao": c.get("created_at"),
            "don_hang": sum(1 for o in STORE["orders"].values() if o.get("by") == "ctv:" + u),
            "so_key": len(keys),
            "da_kich_hoat": sum(1 for k in keys if k.get("activated")),
            "dang_hoat_dong": sum(1 for k in keys if key_status(k) == "hoạt động"),
            "het_han": sum(1 for k in keys if key_status(k) == "hết hạn"),
            "doanh_thu_gan_key": sum(_money_k(k.get("price")) for k in keys),
            "han_muc_k": _ctv_debt_info(c)["han_muc_k"], "no_k": _ctv_debt_info(c)["no_k"],
            "qua_han_k": _ctv_debt_info(c)["qua_han_k"], "don_chua_bill": _ctv_debt_info(c)["don_chua_bill"],
            "thu_hoi": bool(c.get("debt_lock")), "cho_duyet": _ctv_debt_info(c)["cho_duyet"]}

# ── ADMIN · quản lý CTV ──
@app.get("/admin/api/ctvs")
def adm_ctvs():
    g = guard()
    if g: return g
    lst = [_ctv_public(c) for c in (STORE.get("ctvs") or {}).values()]
    lst.sort(key=lambda x: x["username"])
    return out({"ok": True, "tong": len(lst), "ctvs": lst})

@app.post("/admin/api/ctvs")
def adm_ctv_new():
    g = guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    u = str(d.get("username", "")).strip().lower()
    pw = str(d.get("password", "")).strip()
    if not 3 <= len(u) <= 20 or not all(ch in "abcdefghijklmnopqrstuvwxyz0123456789._" for ch in u):
        return out({"ok": False, "thong_bao": "Username 3-20 ký tự (a-z, 0-9, dấu chấm, gạch dưới)"}, 400)
    if u in (STORE.get("ctvs") or {}): return out({"ok": False, "thong_bao": "Username đã tồn tại"}, 400)
    if len(pw) < 4: return out({"ok": False, "thong_bao": "Mật khẩu tối thiểu 4 ký tự"}, 400)
    ctv = {"username": u, "password_hash": _hash_pw(pw), "name": (str(d.get("name", "")).strip() or u)[:60],
           "status": "active", "created_at": now_iso(), "note": str(d.get("note", ""))[:300],
           "perms": dict(DEFAULT_CTV_PERMS, **{k: bool(v) for k, v in (d.get("perms") or {}).items()}),
           "allowed_packages": _pkg_list(d.get("allowed_packages")),
           "key_prefix": str(d.get("key_prefix", "")).strip()[:6].upper(),
           "commission_pct": min(100, _to_int(d.get("commission_pct"))),
           "max_keys_per_day": _to_int(d.get("max_keys_per_day")),
           "credit_limit_k": _to_int(d.get("credit_limit_k"), 500) if str(d.get("credit_limit_k", "")).strip() != "" else 500,
           "paid_k": 0, "payments": []}
    STORE.setdefault("ctvs", {})[u] = ctv
    _ctv_log(u, "created_by_admin")
    save_store()
    return out({"ok": True, "ctv": _ctv_public(ctv), "thong_bao": "Đã tạo CTV " + u})

@app.post("/admin/api/ctvs/<u>")
def adm_ctv_edit(u):
    g = guard()
    if g: return g
    cur = (STORE.get("ctvs") or {}).get(u)
    if not cur: return out({"ok": False, "thong_bao": "Không có CTV " + u}, 404)
    d = request.get_json(silent=True) or request.form
    if d.get("delete"):
        del STORE["ctvs"][u]; _ctv_log(u, "deleted_by_admin"); save_store()
        return out({"ok": True, "thong_bao": "Đã xóa CTV " + u + " (key cũ vẫn giữ nguyên, đã gắn nhãn CTV " + u + ")"})
    if d.get("name") is not None: cur["name"] = str(d["name"]).strip()[:60]
    pw = str(d.get("password", "")).strip()
    if pw and len(pw) < 4:
        return out({"ok": False, "thong_bao": "Mật khẩu tối thiểu 4 ký tự"}, 400)
    if pw:
        cur["password_hash"] = _hash_pw(pw)
        _ctv_log(u, "password_reset_by_admin")
    if d.get("status") in ("active", "locked"):
        cur["status"] = d["status"]
        _ctv_log(u, "unlocked_by_admin" if d["status"] == "active" else "locked_by_admin")
    if d.get("max_keys_per_day") is not None: cur["max_keys_per_day"] = _to_int(d["max_keys_per_day"])
    if str(d.get("credit_limit_k", "")).strip() != "": cur["credit_limit_k"] = _to_int(d["credit_limit_k"])
    if d.get("commission_pct") is not None: cur["commission_pct"] = min(100, _to_int(d["commission_pct"]))
    if d.get("key_prefix") is not None: cur["key_prefix"] = str(d["key_prefix"]).strip()[:6].upper()
    if d.get("allowed_packages") is not None: cur["allowed_packages"] = _pkg_list(d["allowed_packages"])
    if isinstance(d.get("perms"), dict):
        p = cur.setdefault("perms", {})
        for k2, v2 in d["perms"].items(): p[k2] = bool(v2)
    if d.get("note") is not None: cur["note"] = str(d["note"])[:300]
    save_store()
    return out({"ok": True, "ctv": _ctv_public(cur), "thong_bao": "Đã lưu CTV " + u})

@app.post("/admin/api/ctvs/<u>/collect")
def adm_ctv_collect(u):
    """Admin xác nhận ĐÃ THU tiền của CTV (cộng vào số đã trả, trừ nợ theo đơn cũ nhất)."""
    g = guard()
    if g: return g
    c = (STORE.get("ctvs") or {}).get(u)
    if not c: return out({"ok": False, "thong_bao": "Không có CTV " + u}, 404)
    d = request.get_json(silent=True) or request.form
    amt = _to_int(d.get("amount_k"))
    if amt <= 0: return out({"ok": False, "thong_bao": "Nhập số tiền đã thu (đơn vị K) lớn hơn 0"}, 400)
    c["paid_k"] = _to_int(c.get("paid_k")) + amt
    c.setdefault("payments", []).append({"at": now_iso(), "amount_k": amt, "note": str(d.get("note", ""))[:120]})
    del c["payments"][:-100]
    _ctv_log(u, "collect", "%dK" % amt); save_store()
    _ctv_enforce(c)
    inf = _ctv_debt_info(c)
    return out({"ok": True, "cong_no": inf, "thong_bao": "Đã ghi thu %dK · còn nợ %dK" % (amt, inf["no_k"])})

@app.get("/admin/api/ctvs/<u>")
def adm_ctv_detail(u):
    """Chi tiết 1 CTV: profile + toàn bộ key + đơn + nhật ký + key theo ngày."""
    g = guard()
    if g: return g
    cur = (STORE.get("ctvs") or {}).get(u)
    if not cur: return out({"ok": False, "thong_bao": "Không có CTV " + u}, 404)
    keys = [_key_public(k) for k in sorted((k for k in STORE["keys"].values() if k.get("by") == "ctv:" + u),
            key=lambda x: x.get("created_at", ""), reverse=True)]
    ords = sorted((o for o in STORE["orders"].values() if o.get("by") == "ctv:" + u),
                  key=lambda o: o.get("ngay_tao", ""), reverse=True)[:30]
    log = [L for L in reversed(STORE.get("ctvlog", [])[-500:]) if L.get("ctv") == u][:80]
    days = {}
    for k in keys:
        d0 = (k.get("ngay_tao") or "")[:10]
        if d0: days[d0] = days.get(d0, 0) + 1
    return out({"ok": True, "ctv": _ctv_public(cur), "keys": keys, "don_hang": ords,
                "nhat_ky": log, "khach_hang": _customers("ctv:" + u), "dong_thoi_gian": _key_events("ctv:" + u, 150), "key_theo_ngay": sorted(days.items())[-14:],
                "cong_no": _ctv_debt_info(cur), "thanh_toan": list(reversed(cur.get("payments", [])))[:20],
                "don_no": [{"id": o["id"], "khach": o.get("khach"), "con_no_k": r, "ngay": o.get("ngay_tao"), "bill": o.get("bill", "")} for o, r in _ctv_outstanding(u)]})

# ── CTV · đăng nhập + API ──
@app.post("/ctv/login")
def ctv_login():
    ip = (request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr or "0.0.0.0")
    if not _ratelimit(ip):
        return out({"ok": False, "thong_bao": "Thử quá nhiều lần, chờ 10 phút"}, 429)
    d = request.get_json(silent=True) or request.form
    u = str(d.get("username", "")).strip().lower()
    c = (STORE.get("ctvs") or {}).get(u)
    if not c or not _check_pw(str(d.get("password") or ""), c.get("password_hash")):
        _record_fail(ip)
        return out({"ok": False, "thong_bao": "Sai tài khoản hoặc mật khẩu CTV"}, 401)
    if c.get("status") != "active":
        return out({"ok": False, "thong_bao": "Tài khoản CTV đang bị khóa — liên hệ admin"}, 403)
    session["ctv"] = u
    _ctv_log(u, "login")
    return out({"ok": True, "thong_bao": "Xin chào " + (c.get("name") or u)})

@app.get("/ctv/logout")
def ctv_logout():
    u = session.get("ctv")
    if u: _ctv_log(u, "logout")
    session.pop("ctv", None)
    return redirect("/ctv")

@app.get("/ctv/api/overview")
def ctv_overview():
    c, g = ctv_guard()
    if g: return g
    u = c["username"]
    allowed = c.get("allowed_packages") or []
    today = datetime.now(VN).strftime("%Y-%m-%d")
    made_today = sum(1 for k in STORE["keys"].values()
                     if k.get("by") == "ctv:" + u and (k.get("created_at") or "")[:10] == today)
    pub = _ctv_public(c)
    return out({"ok": True, "ten": c.get("name") or u, "prefix": c.get("key_prefix") or "", "cong_no": _ctv_debt_info(c),
                "quyen": dict(DEFAULT_CTV_PERMS, **(c.get("perms") or {})),
                "hom_nay_da_tao": made_today, "cap_key_ngay": _to_int(c.get("max_keys_per_day")),
                "tong_key": pub["so_key"], "da_kich_hoat": pub["da_kich_hoat"],
                "dang_hoat_dong": pub["dang_hoat_dong"], "het_han": pub["het_han"],
                "doanh_thu_gan_key": pub["doanh_thu_gan_key"],
                "goi_duoc_ban": [{**p, "thoi_han": _dur_text(_pkg_sec(p))}
                                 for pid, p in STORE["packages"].items()
                                 if not allowed or pid in allowed]})

@app.post("/ctv/api/keys")
def ctv_create_key():
    c, g = ctv_guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    perms = dict(DEFAULT_CTV_PERMS, **(c.get("perms") or {}))
    if not perms.get("create_key"):
        return out({"ok": False, "thong_bao": "Bạn không có quyền tạo key — liên hệ admin"}, 403)
    # TÊN KHÁCH HÀNG BẮT BUỘC
    name = str(d.get("name", "")).strip()
    if len(name) < 2:
        return out({"ok": False, "thong_bao": "⚠️ BẮT BUỘC nhập TÊN KHÁCH HÀNG (tối thiểu 2 ký tự) trước khi tạo key"}, 400)
    pid = str(d.get("package_id", "")).strip().upper()
    pk = STORE["packages"].get(pid)
    if not pk: return out({"ok": False, "thong_bao": "Gói không tồn tại"}, 404)
    allowed = c.get("allowed_packages") or []
    if allowed and pid not in allowed:
        return out({"ok": False, "thong_bao": "Bạn chưa được cấp gói này — liên hệ admin"}, 403)
    # CTV chỉ tạo theo gói được cấp, không tự ngày/giờ/vĩnh viễn
    if d.get("permanent") or str(d.get("days", "")).strip() or str(d.get("hours", "")).strip():
        return out({"ok": False, "thong_bao": "CTV chỉ tạo key theo gói đã được cấp"}, 403)
    price = str(d.get("price", "")).strip()
    if price and not perms.get("custom_price"):
        return out({"ok": False, "thong_bao": "Bạn không có quyền tự nhập giá — sẽ tính theo giá gói"}, 403)
    # CÔNG NỢ: tạo trước – thu tiền 20:00–22:00 cuối ngày
    inf = _ctv_debt_info(c)
    if inf["khoa_tao_key"]:
        return out({"ok": False, "thong_bao": "⛔ " + inf["ly_do"], "cong_no": inf}, 403)
    unit_k = _money_k(pk.get("wholesale"))
    if unit_k <= 0:
        return out({"ok": False, "thong_bao": "Gói này chưa có giá nhập — liên hệ admin"}, 403)
    cost_k = unit_k * max(1, min(200, _to_int(d.get("count", 1), 1)))
    if inf["no_k"] + cost_k > inf["han_muc_k"]:
        return out({"ok": False, "thong_bao": "⚠️ Vượt hạn mức nợ %dK (đang nợ %dK, đơn này %dK) — thanh toán cho admin để tiếp tục" % (inf["han_muc_k"], inf["no_k"], cost_k), "cong_no": inf}, 403)
    # Hạn mức key/ngày
    cap = _to_int(c.get("max_keys_per_day"))
    cnt = max(1, min(200, _to_int(d.get("count", 1), 1)))
    if cap > 0:
        today = datetime.now(VN).strftime("%Y-%m-%d")
        made_today = sum(1 for k in STORE["keys"].values()
                         if k.get("by") == "ctv:" + c["username"] and (k.get("created_at") or "")[:10] == today)
        if made_today + cnt > cap:
            return out({"ok": False, "thong_bao": "⚠️ Hạn mức %d key/ngày — hôm nay đã tạo %d" % (cap, made_today)}, 403)
    d = dict(d)
    d["count"] = cnt; d["name"] = name; d["package_id"] = pid
    d.pop("days", None); d.pop("hours", None); d.pop("permanent", None)
    d.setdefault("prefix", c.get("key_prefix") or "")
    r, st = create_keys_batch(d, "ctv:" + c["username"])
    if r.get("ok"):
        o_ = STORE["orders"].get(r["don_hang"])
        if o_: o_["cost_k"] = cost_k; o_["unit_k"] = unit_k; o_["bill"] = ""; o_["bill_ok"] = False
        save_store()
        _ctv_log(c["username"], "create_key", "%d key · gói %s · KH %s · nhập %dK" % (r["da_tao"], pid, name, cost_k))
        r["cong_no"] = _ctv_debt_info(c); r["gia_nhap_k"] = cost_k
    return out(r, st)

@app.get("/ctv/api/orders")
def ctv_orders():
    c, g = ctv_guard()
    if g: return g
    L = sorted((o for o in STORE["orders"].values() if o.get("by") == "ctv:" + c["username"]), key=lambda o: o.get("ngay_tao", ""), reverse=True)[:80]
    return out({"ok": True, "cong_no": _ctv_debt_info(c), "don_hang": [
        {"id": o["id"], "khach": o.get("khach"), "goi": o.get("package"), "so_key": o.get("so_key"), "gia": o.get("price"),
         "gia_nhap_k": o.get("cost_k", 0), "ngay_tao": o.get("ngay_tao"), "bill": o.get("bill", ""), "bill_ok": bool(o.get("bill_ok")),
         "keys": o.get("keys", [])} for o in L]})

@app.post("/ctv/api/orders/<oid>/bill")
def ctv_order_bill(oid):
    c, g = ctv_guard()
    if g: return g
    o = STORE["orders"].get(oid)
    if not o or o.get("by") != "ctv:" + c["username"]:
        return out({"ok": False, "thong_bao": "Đơn này không phải của bạn"}, 403)
    if o.get("bill_ok"): return out({"ok": False, "thong_bao": "Bill đã được admin duyệt, không sửa được"}, 400)
    d = request.get_json(silent=True) or request.form
    b = str(d.get("bill", "")).strip()
    if len(b) < 4: return out({"ok": False, "thong_bao": "Nhập mã giao dịch / link ảnh bill của khách (tối thiểu 4 ký tự)"}, 400)
    o["bill"] = b[:300]; o["bill_at"] = now_iso()
    _ctv_log(c["username"], "bill", oid); save_store()
    return out({"ok": True, "thong_bao": "Đã gửi bill — chờ admin duyệt"})

@app.get("/ctv/api/keys")
def ctv_keys():
    c, g = ctv_guard()
    if g: return g
    u = c["username"]
    ks = [_key_public(k) for k in sorted((k for k in STORE["keys"].values() if k.get("by") == "ctv:" + u),
          key=lambda x: x.get("created_at", ""), reverse=True)]
    if not dict(DEFAULT_CTV_PERMS, **(c.get("perms") or {})).get("see_calls"):
        for k in ks: k.pop("luot_goi_hu", None); k.pop("luot_goi_md5", None)
    return out({"ok": True, "tong": len(ks), "keys": ks})

@app.get("/ctv/api/keys/<kid>/msg")
def ctv_key_msg(kid):
    c, g = ctv_guard()
    if g: return g
    for k in STORE["keys"].values():
        if k.get("key") == kid or k.get("id") == kid:
            if k.get("by") != "ctv:" + c["username"]:
                return out({"ok": False, "thong_bao": "Key này không do bạn tạo"}, 403)
            return out({"ok": True, "tin_nhan": _payment_msg(k)})
    return out({"ok": False, "thong_bao": "Không tìm thấy key"}, 404)

@app.post("/ctv/api/keys/<kid>")
def ctv_key_act(kid):
    c, g = ctv_guard()
    if g: return g
    d = request.get_json(silent=True) or request.form
    perms = dict(DEFAULT_CTV_PERMS, **(c.get("perms") or {}))
    if c.get("debt_lock"):
        return out({"ok": False, "thong_bao": "⛔ " + _ctv_debt_info(c)["ly_do"]}, 403)
    for k in STORE["keys"].values():
        if k.get("key") == kid or k.get("id") == kid:
            if k.get("by") != "ctv:" + c["username"]:
                return out({"ok": False, "thong_bao": "Key này không do bạn tạo"}, 403)
            if d.get("status") in ("banned", "active"):
                if not perms.get("lock_key"):
                    return out({"ok": False, "thong_bao": "Bạn không có quyền khóa/mở key"}, 403)
                k["status"] = d["status"]
                _ctv_log(c["username"], "lock_key" if d["status"] == "banned" else "unlock_key", kid)
            _ext = _to_int(d.get("extend_days")) * 86400 + _to_int(d.get("extend_hours")) * 3600
            if _ext:
                if not perms.get("extend_key"):
                    return out({"ok": False, "thong_bao": "Bạn không có quyền cộng thời hạn"}, 403)
                if k.get("activated") and k.get("expires_ts"):
                    k["expires_ts"] = max(k["expires_ts"], time.time()) + _ext
                    k["expires_at"] = datetime.fromtimestamp(k["expires_ts"], VN).replace(microsecond=0).isoformat()
                    k["duration_sec"] = (_key_dur_sec(k) or 0) + _ext
                elif not k.get("activated") and _key_dur_sec(k):
                    k["duration_sec"] = _key_dur_sec(k) + _ext
                k["duration_days"] = (k.get("duration_sec") // 86400 or None) if k.get("duration_sec") else k.get("duration_days")
                _ctv_log(c["username"], "extend_key", "%s +%s" % (kid, _dur_text(_ext)))
            save_store()
            return out({"ok": True, "key": _key_public(k), "tin_nhan_thanh_toan": _payment_msg(k)})
    return out({"ok": False, "thong_bao": "Không tìm thấy key"}, 404)
# ═══════════════════════════════════════════════════════════════════════════════
#  v10 · KHÁCH HÀNG · LỊCH SỬ KEY · INSIGHTS · CHU KỲ
# ═══════════════════════════════════════════════════════════════════════════════
def _ts(iso):
    try: return datetime.fromisoformat(str(iso)).timestamp()
    except Exception: return 0.0

def _customers(owner=None, q=""):
    """Gom key theo (người bán, tên khách) → hồ sơ khách: chi tiêu, thiết bị, lượt gọi, nhãn chăm sóc."""
    q = (q or "").strip().lower(); now = time.time(); groups = {}
    for k in STORE["keys"].values():
        if k.get("role") == "admin": continue
        by = k.get("by") or "admin"
        if owner and by != owner: continue
        nm = " ".join(str(k.get("name") or "").split()) or "(không tên)"
        groups.setdefault(by + "|" + nm.lower(), {"khach": nm, "owner": by, "ks": []})["ks"].append(k)
    res = []
    for g in groups.values():
        ks = g["ks"]; sts = [key_status(k) for k in ks]; devs, seen = [], set()
        for k in ks:
            for d in (k.get("devices") or {}).values():
                sg = d.get("device_id") or d.get("ua") or id(d)
                if sg in seen: continue
                seen.add(sg)
                devs.append({"ten": d.get("name", "Thiết bị"), "mo_ta": str(d.get("ua", ""))[:120],
                             "kich_hoat": d.get("activated_at"), "lan_cuoi_goi": d.get("last_call"),
                             "luot_goi": int(d.get("calls_hu", 0)) + int(d.get("calls_md5", 0)) + int(d.get("calls_sunwin", 0)), "key": k["key"]})
        last_call = max((k.get("last_call") or "" for k in ks), default="")
        exp = [k["expires_ts"] for k, s in zip(ks, sts) if s == "hoạt động" and k.get("expires_ts")]
        spend = sum(_money_k(k.get("price")) for k in ks)
        st = ("hoạt động" if "hoạt động" in sts else "chưa kích hoạt" if "chưa kích hoạt" in sts
              else "hết hạn" if "hết hạn" in sts else "khóa")
        tags = []
        if exp and min(exp) - now < 86400: tags.append("sắp hết hạn")
        if st == "hoạt động" and (not last_call or now - _ts(last_call) > 3 * 86400): tags.append("ngủ đông")
        if len(ks) >= 3 or spend >= 500: tags.append("VIP")
        if len(ks) >= 2: tags.append("khách quay lại")
        if st == "hết hạn": tags.append("cần chăm sóc")
        acts = [last_call] + [k.get("created_at") or "" for k in ks] + [k.get("activated_at") or "" for k in ks]
        row = {"khach": g["khach"], "owner": g["owner"], "trang_thai": st, "nhan": tags,
               "so_key": len(ks), "dang_chay": sts.count("hoạt động"), "da_kich_hoat": sum(1 for k in ks if k.get("activated")),
               "chi_tieu_k": spend, "lan_dau": min((k.get("created_at") or "" for k in ks), default=""),
               "hoat_dong_cuoi": max(acts), "goi_api_cuoi": last_call or None,
               "het_han_som": datetime.fromtimestamp(min(exp), VN).replace(microsecond=0).isoformat() if exp else None,
               "luot_goi": sum(int(k.get("calls_hu", 0)) + int(k.get("calls_md5", 0)) + int(k.get("calls_sunwin", 0)) for k in ks),
               "thiet_bi": devs, "keys": [_key_public(k) for k in sorted(ks, key=lambda x: x.get("created_at", ""), reverse=True)]}
        hay = (g["khach"] + " " + g["owner"] + " " + " ".join(k["key"] for k in ks) + " " + " ".join(d["mo_ta"] for d in devs)).lower()
        if q and q not in hay: continue
        res.append(row)
    res.sort(key=lambda r: r["hoat_dong_cuoi"], reverse=True)
    return res

def _key_events(owner=None, limit=200, q="", loai=""):
    """Dòng thời gian: tạo key · kích hoạt · gọi API · hết hạn · hành động CTV."""
    ev = []; now = time.time(); q = (q or "").strip().lower()
    for k in STORE["keys"].values():
        if k.get("role") == "admin": continue
        by = k.get("by") or "admin"
        if owner and by != owner: continue
        pk = STORE["packages"].get(k.get("package_id") or "", {})
        base = {"key": k["key"], "khach": k.get("name") or "", "by": by,
                "goi": k.get("package_name") or pk.get("name", ""), "gia": k.get("price", "")}
        ev.append(dict(base, at=k.get("created_at") or "", loai="tao_key", mo_ta="Tạo key" + (" · đơn " + k["order_id"] if k.get("order_id") else "")))
        if k.get("activated_at"):
            dv = ", ".join(d.get("name", "TB") for d in (k.get("devices") or {}).values())
            ev.append(dict(base, at=k["activated_at"], loai="kich_hoat", mo_ta="Khách kích hoạt" + (" · " + dv if dv else "")))
        if k.get("last_call"):
            ev.append(dict(base, at=k["last_call"], loai="goi_api", mo_ta="Gọi API gần nhất · Hũ %s · MD5 %s · Sunwin %s" % (k.get("calls_hu", 0), k.get("calls_md5", 0), k.get("calls_sunwin", 0))))
        if k.get("expires_ts") and now > k["expires_ts"]:
            ev.append(dict(base, at=k.get("expires_at") or "", loai="het_han", mo_ta="Key hết hạn"))
    for L in STORE.get("ctvlog", []):
        if L.get("action") == "create_key": 
            if not owner or ("ctv:" + str(L.get("ctv"))) == owner:
                ev.append({"at": L.get("at", ""), "loai": "ctv_create_key", "by": "ctv:" + str(L.get("ctv")), "khach": "", "key": "", "goi": "", "gia": "",
                           "mo_ta": "CTV tạo key · " + str(L.get("detail", ""))})
            continue
        if owner and ("ctv:" + str(L.get("ctv"))) != owner: continue
        ev.append({"at": L.get("at", ""), "loai": "ctv_" + str(L.get("action")), "by": "ctv:" + str(L.get("ctv")), "khach": "", "key": "", "goi": "", "gia": "",
                   "mo_ta": str(L.get("action")) + ((" · " + str(L["detail"])) if L.get("detail") else "")})
    if loai: ev = [e for e in ev if e["loai"] == loai or (loai == "ctv" and e["loai"].startswith("ctv_"))]
    if q: ev = [e for e in ev if q in (e["khach"] + " " + e["key"] + " " + e["by"] + " " + e["mo_ta"]).lower()]
    # tạo key ở admin/ctv đã có sự kiện riêng → bỏ trùng log "ctv_create_key" khi đang lọc đúng loại tao_key
    ev.sort(key=lambda e: e["at"], reverse=True)
    return ev[:limit]

@app.get("/admin/api/customers")
def adm_customers():
    g = guard()
    if g: return g
    by = request.args.get("by", ""); lst = _customers(by or None, request.args.get("q", ""))
    return out({"ok": True, "tong": len(lst), "khach": lst,
                "chu": sorted({r["owner"] for r in lst})})

@app.get("/admin/api/keylog")
def adm_keylog():
    g = guard()
    if g: return g
    by = request.args.get("by", "") or None
    lim = max(20, min(1000, _to_int(request.args.get("limit", 300), 300)))
    ev = _key_events(by, lim, request.args.get("q", ""), request.args.get("loai", ""))
    base = datetime.now(VN).date(); cnt = defaultdict(int); act = defaultdict(int); hours = [0] * 24
    for k in STORE["keys"].values():
        if k.get("role") == "admin" or (by and (k.get("by") or "admin") != by): continue
        cnt[(k.get("created_at") or "")[:10]] += 1; act[(k.get("activated_at") or "")[:10]] += 1
        try: hours[int((k.get("created_at") or "")[11:13])] += 1
        except Exception: pass
    days = [(base - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)]
    owners = sorted({(k.get("by") or "admin") for k in STORE["keys"].values() if k.get("role") != "admin"})
    return out({"ok": True, "tong": len(ev), "su_kien": ev, "chu": owners,
                "theo_ngay": [[d[5:], cnt[d], act[d]] for d in days], "theo_gio": hours})

@app.get("/admin/api/insights")
def adm_insights():
    g = guard()
    if g: return g
    now = time.time(); today = datetime.now(VN).date()
    keys = [k for k in STORE["keys"].values() if k.get("role") != "admin"]
    rev, cnt, hours = defaultdict(int), defaultdict(int), [0] * 24
    for k in keys:
        d0 = (k.get("created_at") or "")[:10]; rev[d0] += _money_k(k.get("price")); cnt[d0] += 1
        try: hours[int((k.get("created_at") or "")[11:13])] += 1
        except Exception: pass
    days = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(13, -1, -1)]
    d14 = [[d[5:], rev[d], cnt[d]] for d in days]
    last7, prev7 = sum(x[1] for x in d14[-7:]), sum(x[1] for x in d14[:7])
    own = {}
    for k in keys:
        by = k.get("by") or "admin"
        o = own.setdefault(by, {"by": by, "ten": ((STORE.get("ctvs") or {}).get(by[4:], {}).get("name") if by.startswith("ctv:") else "Admin") or by,
                               "so_key": 0, "kich_hoat": 0, "doanh_thu_k": 0, "doanh_thu_7d_k": 0, "key_7d": 0})
        o["so_key"] += 1; o["kich_hoat"] += 1 if k.get("activated") else 0
        o["doanh_thu_k"] += _money_k(k.get("price"))
        if (k.get("created_at") or "")[:10] >= days[-7]:
            o["doanh_thu_7d_k"] += _money_k(k.get("price")); o["key_7d"] += 1
    top = sorted(own.values(), key=lambda o: (o["doanh_thu_7d_k"], o["doanh_thu_k"]), reverse=True)[:8]
    pk = {}
    for k in keys:
        nm = k.get("package_name") or STORE["packages"].get(k.get("package_id") or "", {}).get("name") or "Tuỳ chỉnh"
        p = pk.setdefault(nm, {"goi": nm, "so_key": 0, "doanh_thu_k": 0}); p["so_key"] += 1; p["doanh_thu_k"] += _money_k(k.get("price"))
    renew, dorm = [], []
    for k in keys:
        st = key_status(k); exp = k.get("expires_ts")
        base = {"key": k["key"], "khach": k.get("name") or "(không tên)", "by": k.get("by") or "admin", "trang_thai": st}
        if exp and ((st == "hoạt động" and 0 < exp - now < 72 * 3600) or (st == "hết hạn" and now - exp < 7 * 86400)):
            renew.append(dict(base, het_han=k.get("expires_at"), gio_con=round((exp - now) / 3600, 1)))
        if st == "hoạt động":
            lc = _ts(k.get("last_call")) if k.get("last_call") else 0
            ref = lc or _ts(k.get("activated_at"))
            if ref and now - ref > (3 if lc else 1) * 86400:
                dorm.append(dict(base, ngay_im=round((now - ref) / 86400, 1), tung_goi=bool(lc)))
    renew.sort(key=lambda r: r["gio_con"]); dorm.sort(key=lambda r: -r["ngay_im"])
    alerts = []
    for c in (STORE.get("ctvs") or {}).values():
        p = _ctv_public(c)
        if p.get("thu_hoi"): alerts.append({"muc": "bad", "text": "CTV %s đang bị THU HỒI key (nợ quá hạn)" % p["username"], "go": "ctv"})
        elif p.get("qua_han_k"): alerts.append({"muc": "warn", "text": "CTV %s nợ quá hạn %sK" % (p["username"], p["qua_han_k"]), "go": "ctv"})
        if p.get("cho_duyet"): alerts.append({"muc": "warn", "text": "CTV %s có phiếu thanh toán chờ duyệt" % p["username"], "go": "ctv"})
        if p.get("don_chua_bill"): alerts.append({"muc": "info", "text": "CTV %s còn %s đơn chưa gửi bill" % (p["username"], p["don_chua_bill"]), "go": "dh"})
    for c, t in TABLES.items():
        if t.err: alerts.append({"muc": "bad", "text": "Bàn %s lỗi nguồn: %s" % (t.name, str(t.err)[:80]), "go": c})
    if renew: alerts.append({"muc": "info", "text": "%d key sắp/vừa hết hạn — cơ hội gia hạn" % len(renew), "go": "ov"})
    if not (GIST_TOKEN and GIST_ID): alerts.append({"muc": "warn", "text": "Chưa bật backup Gist — redeploy Render sẽ mất key", "go": "ov"})
    act = sum(1 for k in keys if k.get("activated"))
    return out({"ok": True, "doanh_thu_14": d14, "doanh_thu_7d_k": last7, "doanh_thu_7d_truoc_k": prev7,
                "doanh_thu_hom_nay_k": rev[days[-1]], "key_hom_nay": cnt[days[-1]],
                "ty_le_kich_hoat": round(act / len(keys) * 100, 1) if keys else 0,
                "top_chu": top, "theo_goi": sorted(pk.values(), key=lambda p: -p["doanh_thu_k"]),
                "theo_gio": hours, "gia_han": renew[:40], "ngu_dong": dorm[:25], "canh_bao": alerts})

@app.get("/ctv/login")
def ctv_login_page(): return redirect("/ctv")

# ── PHÂN TÍCH CHU KỲ v12 — "CỤC NHỊP" (run-pattern) ────────────────────────────
# Tư duy mới: chu kỳ thật của Tài Xỉu nằm ở NHỊP ĐỘ DÀI RUN (chuỗi cầu), chứ
# không phải ở autocorrelation của chuỗi T/X thô (đó là lý do bản cũ thử 15 chu
# kỳ p2..p16 luôn ra "nhiều chu kỳ" loạn vì nhiễu cho qua). Quy trình stateless,
# deterministic, MỘT đáp án duy nhất:
#   B1: đổi dãy thành chuỗi độ dài run  R = [r1, r2, ...]  (VD 4-1-1-2-1)
#   B2: đo ĐỘ THUẦN của từng loại nhịp trên 8 run gần nhất:
#         XEN_KẼ_1_1  (% run = 1)          NHỊP_2_2 / NHỊP_3_3  (% run = L)
#         BỆT (% run ≥ 3)                  MẪU_x_y (motif 2 run lặp)
#   B3: nhịp thắng cuộc chỉ được PHÁN khi độ thuần ≥ 0.7:
#         1-1            → bẻ (ngược phiên cuối)
#         L-L, BỆT, MẪU  → theo nếu run đang đi chưa đủ L/max, đủ rồi thì bẻ
#   B4: không nhịp nào chín → du_doan = None, trạng thái "CHỜ" (không chơi).
#   B5: TỰ CHẤM: áp chính luật này cho từng điểm trong 60 phiên cuối (không nhìn
#       tương lai) → số lần phát tin + tỉ lệ đúng, chỉ tin khi backtest > 55%.
_CK_CACHE = {}

def _rhythm_read(seq):
    """Đo nhịp hiện tại, trả về {nhip, do_thuan, du_doan, run_hien_tai, ly_do}.
    du_doan chỉ có nghĩa khi do_thuan >= 0.7; None = chưa chín."""
    if len(seq) < 10:
        return {"nhip": "CHƯAĐỦDỮLIỆU", "do_thuan": 0.0, "du_doan": None, "run_hien_tai": 0,
                "ly_do": "cần ≥ 10 phiên"}
    runs = _run_lengths_local(seq)
    cur = runs[-1]
    recent = runs[-8:]
    m = len(recent)
    # nhịp L-L (2-2, 3-3): run gần nhất đều bằng L
    for L in (2, 3):
        pL = sum(1 for r in recent if r == L) / m
        if pL >= 0.7:
            if cur >= L:
                return {"nhip": f"NHỊP_{L}_{L}", "do_thuan": round(pL, 2), "du_doan": _opp(seq[-1]),
                        "run_hien_tai": cur, "ly_do": f"run đang đi đã đủ {L} phiên → bẻ"}
            return {"nhip": f"NHỊP_{L}_{L}", "do_thuan": round(pL, 2), "du_doan": seq[-1],
                    "run_hien_tai": cur, "ly_do": f"nhịp {L}-{L} chuẩn, run mới chạy {cur}/{L} → theo"}
    # xen kẽ 1-1
    p1 = sum(1 for r in recent if r == 1) / m
    if p1 >= 0.7:
        return {"nhip": "XEN_KẼ_1_1", "do_thuan": round(p1, 2), "du_doan": _opp(seq[-1]),
                "run_hien_tai": cur, "ly_do": "xen kẽ chuẩn 1-1 → bẻ"}
    # bệt: run dài là chuyện bình thường, chạy theo tới khi gãy
    pbrk = sum(1 for r in recent if r >= 3) / m
    if pbrk >= 0.7:
        mxr = max(recent)
        if cur < mxr:
            return {"nhip": "BỆT", "do_thuan": round(pbrk, 2), "du_doan": seq[-1],
                    "run_hien_tai": cur, "ly_do": f"bệt chuẩn (max {mxr}), run mới {cur} chưa tới nấc cũ → chạy tiếp"}
    # motif 2-run lặp (VD 3-1-3-1-3-1)
    if len(runs) >= 7:
        win = runs[-8:]
        motif = (win[0], win[1])
        khop = sum(1 for i in range(len(win) - 1) if (win[i], win[i + 1]) == motif)
        thu = khop / (len(win) - 1)
        if thu >= 0.7:
            nxt = motif[len(win) % 2]        # run kế tiếp theo mô hình
            if cur < nxt:
                return {"nhip": "MẪU_%d_%d" % motif, "do_thuan": round(thu, 2), "du_doan": seq[-1],
                        "run_hien_tai": cur, "ly_do": f"mẫu lặp {'-'.join(map(str, motif))}, run mới {cur}/{nxt} → theo"}
            return {"nhip": "MẪU_%d_%d" % motif, "do_thuan": round(thu, 2), "du_doan": _opp(seq[-1]),
                    "run_hien_tai": cur, "ly_do": f"mẫu lặp {'-'.join(map(str, motif))} đã hết nấc → bẻ"}
    return {"nhip": "LOẠN", "do_thuan": round(max(p1, pbrk), 2), "du_doan": None,
            "run_hien_tai": cur, "ly_do": "nhịp chưa chín (độ thuần < 0.7) — KHÔNG chơi"}

def _ck_backtest(seq):
    """Tự chấm: áp _rhythm_read cho từng điểm trong 60 phiên cuối (không nhìn tương lai)."""
    start = max(30, len(seq) - 60); fired = hit = 0
    for t in range(start, len(seq)):
        rd = _rhythm_read(seq[:t])
        if rd.get("du_doan"):
            fired += 1
            hit += 1 if rd["du_doan"] == seq[t] else 0
    return {"so_phien_thu": len(seq) - start, "so_lan_ra_tin_hieu": fired, "dung": hit,
            "ty_le": round(hit / fired * 100, 1) if fired else None}

def analyze_chu_ky(seq, sums=None):
    seq = [s for s in seq if s in ("TAI", "XIU")][-200:]; n = len(seq)
    if n < 12: return {"da_du_du_lieu": False, "so_phien": n, "ghi_chu": "Cần ≥ 12 phiên để đọc nhịp"}
    key = (n, hash(tuple(seq[-100:])))
    if key in _CK_CACHE: return _CK_CACHE[key]
    rd = _rhythm_read(seq)
    side = rd["du_doan"]
    bt = _ck_backtest(seq)
    tin_hieu = []
    if side:
        tin_hieu.append({"nguon": "nhịp run " + rd["nhip"], "huong": side, "trong_so": rd["do_thuan"]})
        if bt.get("ty_le") is not None and bt["ty_le"] >= 55:
            tin_hieu.append({"nguon": "backtest tự đo", "huong": side, "trong_so": 0.5})
        if bt.get("ty_le") is not None and bt["ty_le"] < 50:
            side = None        # luật này đang không ăn trên bàn này → tự đóng cửa
            tin_hieu.append({"nguon": "backtest tự đo", "huong": "TỪ CHỐI", "trong_so": 0.0})
    conf = round(min(0.72, 0.5 + 0.30 * rd["do_thuan"]), 3) if side else 0.0
    wave = [seq[max(0, i - 9):i + 1].count("TAI") / min(10, i + 1)
            for i in range(n - 1, max(0, n - 51), -10)]
    res = {"da_du_du_lieu": True, "so_phien": n,
           "du_doan": side, "do_tin_cay": conf,
           "trang_thai": "TÁC ĐỘNG" if side else "CHỜ",
           "nhip": rd["nhip"], "do_thuan": rd["do_thuan"], "run_hien_tai": rd["run_hien_tai"],
           "ly_do": rd["ly_do"], "cau_run": "-".join(str(r) for r in _run_lengths_local(seq)[-12:]),
           "tin_hieu": tin_hieu,
           "ket_luan": (f"Nhịp {rd['nhip']} (thuần {rd['do_thuan']:.0%}) → {side}: {rd['ly_do']}" if side
                        else f"NHỊP CHƯA CHÍN ({rd['nhip']}, thuần {rd['do_thuan']:.0%}) — {rd['ly_do']}"),
           "song_ty_le_tai": [round(x, 2) for x in wave],
           "ty_le_tai_chung": round(sum(1 for s in seq if s == "TAI") / n, 3),
           "tong_tb20": round(sum(list(sums)[-20:]) / len(list(sums)[-20:]), 1) if sums else None,
           "backtest": bt,
           "luu_y": "Chỉ chơi khi nhịp chín (độ thuần ≥ 0.7) và backtest tự đo > 55%. Còn lại: CHỜ."}
    if len(_CK_CACHE) > 16: _CK_CACHE.clear()
    _CK_CACHE[key] = res
    return res

# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN UI v13 — STUDIO: 2 loại key (LC79 2 bàn / Sunwin 1 bàn) · topbar + rail · palette · lịch sử 3 bàn
# ═══════════════════════════════════════════════════════════════════════════════
ADMIN_HTML = r"""<!doctype html><html lang="vi" data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffffff">
<title>PAW TX · Quản trị</title>
<style>
:root{--r:16px;--r-sm:10px;--mono:'SF Mono',ui-monospace,Menlo,Consolas,monospace;--ease:cubic-bezier(.22,.61,.36,1)}
[data-theme=dark]{--bg:#070b12;--s1:#0c111a;--s2:#121926;--s3:#1a2334;--line:#212b3d;--line2:#2c3a53;--tx:#ecf1fa;--tx2:#96a3bf;--tx3:#5d6a89;--acc:#2bd6b0;--acc2:#5b8cf7;--accSoft:rgba(43,214,176,.11);--grad:linear-gradient(135deg,#2bd6b0,#4f8ff7);--ok:#2fd9a3;--okSoft:rgba(47,217,163,.12);--bad:#fb7483;--badSoft:rgba(251,116,131,.12);--warn:#f3c15e;--warnSoft:rgba(243,193,94,.12);--tai:#ff5d77;--taiSoft:rgba(255,93,119,.13);--xiu:#3ebdf7;--xiuSoft:rgba(62,189,247,.13);--sw:#ff9f5f;--swSoft:rgba(255,159,95,.13);--sh:0 14px 34px rgba(0,0,0,.34);color-scheme:dark}
[data-theme=light]{--bg:#ffffff;--s1:#ffffff;--s2:#f5f7fc;--s3:#ecf0f9;--line:#e1e6f2;--line2:#cbd4e8;--tx:#111731;--tx2:#4f5a7c;--tx3:#8892b2;--acc:#0b9c86;--acc2:#3f55ea;--accSoft:rgba(11,156,134,.09);--grad:linear-gradient(135deg,#0b9c86,#3f55ea);--ok:#0b9a68;--okSoft:rgba(11,154,104,.1);--bad:#d93b52;--badSoft:rgba(217,59,82,.08);--warn:#9a6800;--warnSoft:rgba(154,104,0,.09);--tai:#d93b52;--taiSoft:rgba(217,59,82,.09);--xiu:#077fb6;--xiuSoft:rgba(7,127,182,.09);--sw:#bf6611;--swSoft:rgba(191,102,17,.09);--sh:0 10px 26px rgba(20,30,60,.08);color-scheme:light}
*{box-sizing:border-box}
html{background:var(--bg);-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.55 Inter,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;min-height:100vh}
button{font:inherit;color:inherit;border:0;background:none;cursor:pointer;padding:0;text-align:left}
input,select,textarea{font:inherit;color:var(--tx);background:var(--s2);border:1.5px solid var(--line);border-radius:11px;padding:10px 12px;width:100%;outline:none;transition:border-color .15s,box-shadow .15s}
input:focus,select:focus,textarea:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--accSoft)}
input::placeholder,textarea::placeholder{color:var(--tx3)}
textarea{font-family:var(--mono);font-size:12.5px;line-height:1.62;resize:vertical}
select{appearance:none;background-image:linear-gradient(45deg,transparent 50%,var(--tx3) 50%),linear-gradient(135deg,var(--tx3) 50%,transparent 50%);background-position:calc(100% - 17px) 18px,calc(100% - 12px) 18px;background-size:5px 5px,5px 5px;background-repeat:no-repeat;padding-right:32px}
label{display:block;font-size:10.5px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:var(--tx3);margin:14px 0 6px}
h1,h2,h3{margin:0}
h1{font-size:19px;font-weight:900;letter-spacing:-.02em}
h2{font-size:14px;font-weight:800;letter-spacing:-.01em}
h3{font-size:12.5px;font-weight:800}
p{margin:0 0 8px}
a{color:var(--acc);text-decoration:none}
.ic{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.85;stroke-linecap:round;stroke-linejoin:round;flex:0 0 auto;vertical-align:-3px;display:inline-block}
.ic.xs{width:13px;height:13px;vertical-align:-2px}
.ic.sm{width:15px;height:15px;vertical-align:-2px}
.ic.lg{width:22px;height:22px}
.ic.xl{width:26px;height:26px}
.muted{color:var(--tx3);font-size:12.5px}
.dim{color:var(--tx2)}
.mono{font-family:var(--mono)}
.hide{display:none!important}
.nowrap{white-space:nowrap}
.sp{flex:1;min-width:0}
.tr{text-align:right}
.mt6{margin-top:6px}.mt10{margin-top:10px}.mt14{margin-top:14px}
/* ── shell ───────────────────────────────────────────── */
.shell{display:grid;grid-template-columns:256px minmax(0,1fr);min-height:100vh}
.rail{position:sticky;top:0;height:100vh;display:flex;flex-direction:column;padding:16px 12px 12px;border-right:1px solid var(--line);background:var(--s1);overflow:auto}
.brand{display:flex;align-items:center;gap:11px;padding:2px 8px 14px;margin-bottom:4px}
.brand .mark{width:40px;height:40px;border-radius:13px;background:var(--grad);color:#fff;display:grid;place-items:center;box-shadow:0 8px 20px rgba(43,214,176,.26)}
.brand b{display:block;font-size:15px;line-height:1.15;letter-spacing:-.02em}
.brand small{font-size:9.5px;letter-spacing:.17em;font-weight:800;color:var(--tx3)}
.grp{font-size:9.5px;font-weight:800;letter-spacing:.15em;color:var(--tx3);padding:15px 12px 6px}
.navi{display:flex;align-items:center;gap:10px;width:100%;padding:9px 11px;border-radius:11px;color:var(--tx2);font-weight:700;font-size:13px;position:relative;transition:background .13s,color .13s}
.navi:hover{background:var(--s2);color:var(--tx)}
.navi.on{background:var(--accSoft);color:var(--acc)}
.navi.on::before{content:'';position:absolute;left:-12px;top:9px;bottom:9px;width:3px;border-radius:9px;background:var(--grad)}
.navi .ic{opacity:.85}
.navi.on .ic{opacity:1}
.navi .bdg{margin-left:auto;font-size:10.5px;font-weight:900;padding:1px 7px;border-radius:99px;background:var(--badSoft);color:var(--bad)}
.rail .grow{flex:1}
.railfoot{border-top:1px solid var(--line);margin-top:10px;padding-top:8px}
.main{min-width:0;display:flex;flex-direction:column}
.topbar{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:10px;padding:11px clamp(14px,2.6vw,28px);border-bottom:1px solid var(--line);background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(14px)}
.topbar .ttl{min-width:0}
.topbar .ttl small{display:block;font-size:11.5px;color:var(--tx3);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.topbar .chipg{font-size:9.5px;font-weight:800;letter-spacing:.11em;color:var(--tx3);border:1px solid var(--line);border-radius:99px;padding:3px 9px;white-space:nowrap}
.tbtn{width:36px;height:36px;border-radius:10px;background:var(--s2);border:1px solid var(--line);display:grid;place-items:center;color:var(--tx2);flex-shrink:0;transition:border-color .13s,color .13s}
.tbtn:hover{border-color:var(--line2);color:var(--tx)}
.searchbtn{display:flex;align-items:center;gap:7px;padding:8px 11px;border-radius:11px;background:var(--s2);border:1px solid var(--line);color:var(--tx3);font-size:12px;font-weight:700}
.searchbtn kbd{font:10px var(--mono);background:var(--s3);border:1px solid var(--line);border-radius:5px;padding:1px 5px;color:var(--tx2)}
.livepill{display:none;align-items:center;gap:6px;padding:6px 10px;border-radius:99px;background:var(--okSoft);color:var(--ok);font-size:11px;font-weight:800}
.livepill.on{display:inline-flex}
.livepill i{width:6px;height:6px;border-radius:50%;background:currentColor;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.8)}}
.work{padding:18px clamp(14px,2.6vw,28px) 110px;width:100%;max-width:1340px;margin:0 auto}
/* ── cards ───────────────────────────────────────────── */
.card{background:var(--s1);border:1px solid var(--line);border-radius:var(--r);padding:16px;margin-bottom:14px}
.card.tight{padding:12px}
.card-h{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:12px}
.card-h h2{flex:0 1 auto}
.card-h .sp{flex:1}
.card-h .hi{width:28px;height:28px;border-radius:9px;background:var(--accSoft);color:var(--acc);display:grid;place-items:center;flex:0 0 auto}
.grid{display:grid;gap:14px}
.g2{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(236px,1fr))}
.g4{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.split{display:grid;grid-template-columns:minmax(0,1fr) 372px;gap:14px;align-items:start}
@media(max-width:1080px){.split{grid-template-columns:1fr}}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
/* ── kpi / hero ──────────────────────────────────────── */
.kgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;margin-bottom:14px}
.kpi{background:var(--s1);border:1px solid var(--line);border-radius:14px;padding:13px 14px;min-width:0;position:relative;overflow:hidden}
.kpi .kl{display:flex;align-items:center;gap:6px;font-size:10.5px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;color:var(--tx3);margin-bottom:6px}
.kpi b{display:block;font-size:23px;font-weight:900;letter-spacing:-.03em;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi small{display:block;font-size:11.5px;color:var(--tx3);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi.ok b{color:var(--ok)}.kpi.wn b{color:var(--warn)}.kpi.bd b{color:var(--bad)}.kpi.bl b{color:var(--acc2)}.kpi.sw b{color:var(--sw)}
.hero{position:relative;overflow:hidden;background:var(--grad);border-radius:var(--r);color:#fff;padding:18px 20px;margin-bottom:14px;box-shadow:0 14px 30px rgba(43,214,176,.2)}
.hero .hrow{display:flex;gap:20px;align-items:center;flex-wrap:wrap;position:relative;z-index:1}
.hero .lbl{font-size:10.5px;font-weight:800;letter-spacing:.1em;opacity:.92}
.hero .hv{font-size:32px;font-weight:900;letter-spacing:-.035em;line-height:1.12}
.hero .bdg{display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:800;background:rgba(0,0,0,.2);padding:3px 10px;border-radius:99px;margin-top:5px}
.spark{display:flex;align-items:flex-end;gap:3px;height:58px;flex:1;min-width:150px}
.spark i{flex:1;background:rgba(255,255,255,.4);border-radius:3px 3px 0 0;min-height:2px;transition:height .3s}
.spark i.hi{background:#fff}
/* ── buttons ─────────────────────────────────────────── */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:9px 13px;border-radius:11px;background:var(--s3);border:1px solid var(--line);font-weight:800;font-size:13px;transition:filter .15s,transform .1s,border-color .15s;color:var(--tx)}
.btn:hover{filter:brightness(1.08);border-color:var(--line2)}
.btn:active{transform:scale(.975)}
.btn.pri{background:var(--grad);color:#fff;border-color:transparent;box-shadow:0 5px 14px rgba(43,214,176,.22)}
.btn.ok{background:var(--okSoft);color:var(--ok);border-color:transparent}
.btn.bad{background:var(--badSoft);color:var(--bad);border-color:transparent}
.btn.warn{background:var(--warnSoft);color:var(--warn);border-color:transparent}
.btn.ghost{background:transparent}
.btn.sm{padding:6px 10px;font-size:12px;border-radius:9px}
.btn.big{width:100%;padding:12px;font-size:14px}
.btn[disabled]{opacity:.5;pointer-events:none}
.btn.load{pointer-events:none;opacity:.75}
.btn.load::before{content:'';width:13px;height:13px;border:2px solid currentColor;border-top-color:transparent;border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.btns{display:flex;gap:7px;flex-wrap:wrap;align-items:center}
/* ── segmented / chips ───────────────────────────────── */
.fgroup{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-top:10px}
.flabel{font-size:10px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--tx3);min-width:66px}
.seg{display:flex;gap:3px;padding:3px;background:var(--s2);border:1px solid var(--line);border-radius:11px;flex-wrap:wrap}
.seg button{padding:6px 11px;border-radius:8px;font-size:12px;font-weight:800;color:var(--tx3);transition:background .12s,color .12s;white-space:nowrap}
.seg button:hover{color:var(--tx)}
.seg button.on{background:var(--s1);color:var(--acc);box-shadow:0 2px 8px rgba(0,0,0,.16)}
.pills{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.pill{padding:5px 11px;border-radius:99px;background:var(--s2);border:1px solid var(--line);font-size:11.5px;font-weight:800;color:var(--tx2)}
.pill.on{background:var(--accSoft);border-color:var(--acc);color:var(--acc)}
.tag{display:inline-flex;align-items:center;gap:4px;padding:2px 9px;border-radius:99px;font-size:11px;font-weight:800;background:var(--s3);color:var(--tx2);white-space:nowrap}
.tag.act{background:var(--okSoft);color:var(--ok)}
.tag.ban{background:var(--badSoft);color:var(--bad)}
.tag.exp{background:var(--warnSoft);color:var(--warn)}
.tag.idle{background:var(--accSoft);color:var(--acc)}
.tag.bl{background:rgba(91,140,247,.13);color:var(--acc2)}
.tag.tai{background:var(--taiSoft);color:var(--tai)}
.tag.xiu{background:var(--xiuSoft);color:var(--xiu)}
.tag.sw{background:var(--swSoft);color:var(--sw)}
.tag.lg{font-size:13px;padding:5px 13px}
/* ── options ─────────────────────────────────────────── */
.opts{display:grid;grid-template-columns:repeat(auto-fill,minmax(158px,1fr));gap:8px}
.opt{width:100%;padding:11px 12px;border-radius:13px;background:var(--s2);border:1.5px solid var(--line);transition:border-color .13s,background .13s}
.opt b{display:flex;align-items:center;gap:6px;font-size:13px;font-weight:800}
.opt small{display:block;color:var(--tx3);font-size:11.5px;margin-top:2px}
.opt:hover{border-color:var(--line2)}
.opt.on{border-color:var(--acc);background:var(--accSoft);box-shadow:0 0 0 1px var(--acc)}
/* ── list rows ───────────────────────────────────────── */
.li{display:flex;gap:11px;align-items:flex-start;flex-wrap:wrap;padding:12px;border-radius:13px;background:var(--s2);border:1px solid var(--line);margin-bottom:8px;transition:border-color .13s}
.li:hover{border-color:var(--line2)}
.li.click{cursor:pointer}
.li-main{flex:1;min-width:170px}
.li-top{display:flex;gap:7px;align-items:center;flex-wrap:wrap}
.li-meta{display:flex;gap:12px;flex-wrap:wrap;font-size:11.5px;color:var(--tx3);margin-top:4px}
.li-meta b{color:var(--tx2)}
.k{font-family:var(--mono);font-weight:800;font-size:13px;letter-spacing:-.01em}
.ck{width:17px;height:17px;accent-color:var(--acc);flex-shrink:0;margin-top:3px}
.bulkbar{position:sticky;top:64px;z-index:30;display:flex;gap:7px;align-items:center;flex-wrap:wrap;padding:9px 11px;margin-bottom:10px;border-radius:13px;background:var(--s1);border:1px solid var(--acc);box-shadow:var(--sh)}
.evr{display:flex;gap:10px;padding:9px 0;border-top:1px solid var(--line);align-items:flex-start}
.evr:first-child{border-top:0}
.evr .ei{width:24px;height:24px;border-radius:8px;background:var(--s2);color:var(--tx2);display:grid;place-items:center;flex:0 0 auto}
.evr .b{font-size:12.5px;font-weight:700}
/* ── tables ──────────────────────────────────────────── */
.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:var(--tx3);text-align:left;padding:8px;border-bottom:1px solid var(--line2);white-space:nowrap;font-weight:800}
td{padding:8px;border-bottom:1px solid var(--line);white-space:nowrap}
tbody tr:hover td{background:var(--s2)}
tbody tr:last-child td{border-bottom:0}
/* v16: tô màu riêng dòng WIN / LOSE trong bảng phiên */
tbody tr.r-win td{background:var(--okSoft)}
tbody tr.r-lose td{background:var(--badSoft)}
tbody tr.r-win td:first-child{box-shadow:inset 3px 0 0 var(--ok)}
tbody tr.r-lose td:first-child{box-shadow:inset 3px 0 0 var(--bad)}
.tag.wl-w{background:var(--okSoft);color:var(--ok);font-size:12px;padding:3px 11px}
.tag.wl-l{background:var(--badSoft);color:var(--bad);font-size:12px;padding:3px 11px}
/* ── charts ──────────────────────────────────────────── */
.bars{display:flex;align-items:flex-end;gap:5px;height:106px;padding-top:6px}
.bars>div{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px;height:100%;min-width:0}
.bars i{display:block;width:100%;border-radius:5px 5px 2px 2px;background:var(--grad);min-height:3px;transition:height .35s}
.bars span{font-size:9px;color:var(--tx3);white-space:nowrap}
.bars b{font-size:9.5px;color:var(--tx2);font-weight:700}
.heat{display:grid;grid-template-columns:repeat(24,1fr);gap:3px;align-items:end;height:58px}
.heat i{display:block;border-radius:3px 3px 1px 1px;background:var(--acc2);min-height:3px}
.hl{display:grid;grid-template-columns:repeat(24,1fr);gap:3px;font-size:8.5px;color:var(--tx3);text-align:center;margin-top:3px}
.ring{position:relative;width:84px;height:84px;border-radius:50%;display:grid;place-items:center;flex-shrink:0;background:conic-gradient(var(--rc,var(--ok)) calc(var(--pv)*1%),var(--s3) 0)}
.ring::after{content:'';position:absolute;inset:8px;border-radius:50%;background:var(--s1)}
.ring b{position:relative;z-index:1;font-size:18px;font-weight:900}
.dots{display:flex;gap:4px;flex-wrap:wrap}
.dots i{width:12px;height:12px;border-radius:3px;background:var(--s3)}
.dots i.w{background:var(--ok)}.dots i.l{background:var(--bad)}.dots i.s{background:var(--line2)}
.pgb{height:6px;border-radius:99px;background:var(--s3);overflow:hidden}
.pgb i{display:block;height:100%;border-radius:99px;background:var(--grad)}
/* ── misc ────────────────────────────────────────────── */
.msg{white-space:pre-wrap;word-break:break-word;background:var(--s2);border:1px dashed var(--line2);border-radius:12px;padding:12px;font-size:13px;line-height:1.62}
.alert{display:flex;gap:9px;align-items:center;width:100%;padding:9px 11px;border-radius:11px;margin-bottom:6px;background:var(--s2);border:1px solid var(--line);font-size:12.5px;font-weight:600;transition:border-color .13s}
.alert:hover{border-color:var(--line2)}
.alert.bad{border-color:var(--bad);background:var(--badSoft)}
.alert.warn{border-color:var(--warn);background:var(--warnSoft)}
.alert .ai{color:var(--tx2);display:grid;place-items:center}
.alert.bad .ai{color:var(--bad)}.alert.warn .ai{color:var(--warn)}
.note{display:flex;gap:9px;align-items:flex-start;padding:10px 12px;border-radius:11px;background:var(--s2);border:1px solid var(--line);font-size:12.5px;color:var(--tx2);line-height:1.6}
.note .ic{margin-top:2px;color:var(--acc)}
.note.warn{border-color:var(--warn);background:var(--warnSoft);color:var(--warn)}
.note.bad{border-color:var(--bad);background:var(--badSoft);color:var(--bad)}
.note.warn .ic,.note.bad .ic{color:inherit}
.dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:12.5px}
.dl dt{color:var(--tx3);font-weight:700}
.dl dd{margin:0;text-align:right;font-weight:700}
.aside-sticky{position:sticky;top:72px}
/* ── modal ───────────────────────────────────────────── */
.mbg{position:fixed;inset:0;z-index:90;background:rgba(0,0,0,.64);backdrop-filter:blur(4px);display:flex;align-items:flex-end;justify-content:center;padding:0}
.modal{background:var(--s1);border:1px solid var(--line);border-radius:20px 20px 0 0;padding:16px;width:100%;max-width:580px;max-height:92vh;overflow:auto;animation:up .2s var(--ease)}
@media(min-width:760px){.mbg{align-items:center;padding:20px}.modal{border-radius:20px}.modal.xm{max-width:880px}}
@keyframes up{from{transform:translateY(14px);opacity:.4}to{transform:none;opacity:1}}
.mh{display:flex;align-items:center;gap:9px;margin-bottom:6px}
.mh h2{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#toast{position:fixed;left:50%;top:14px;transform:translateX(-50%);z-index:130;background:var(--tx);color:var(--bg);padding:9px 16px;border-radius:99px;font-weight:800;font-size:12.5px;display:none;box-shadow:0 12px 30px rgba(0,0,0,.42);max-width:88vw;text-align:center}
#pbar{position:fixed;top:0;left:0;height:3px;width:0;z-index:200;background:var(--grad);opacity:0;transition:width .3s,opacity .3s;pointer-events:none}
.skel{height:70px;border-radius:14px;margin-bottom:10px;background:linear-gradient(90deg,var(--s2),var(--s3),var(--s2));background-size:200% 100%;animation:sh 1.2s infinite}
@keyframes sh{to{background-position:-200% 0}}
/* ── login ───────────────────────────────────────────── */
.loginwrap{min-height:100vh;display:grid;place-items:center;padding:22px}
.lgbox{width:100%;max-width:370px}
.lgbox .mark{width:58px;height:58px;border-radius:18px;background:var(--grad);color:#fff;display:grid;place-items:center;margin:0 auto 16px;box-shadow:0 12px 30px rgba(43,214,176,.28)}
.pw{position:relative}
.pw input{padding-right:44px}
.pw .eye{position:absolute;right:6px;top:5px;width:32px;height:32px;display:grid;place-items:center;color:var(--tx3);border-radius:8px}
.pw .eye:hover{color:var(--tx)}
/* ── bottom bar ──────────────────────────────────────── */
.tabbar{display:none}
@media(max-width:960px){
 .shell{display:block}
 .rail{display:none}
 .tabbar{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;left:0;right:0;bottom:0;z-index:50;background:color-mix(in srgb,var(--s1) 96%,transparent);backdrop-filter:blur(14px);border-top:1px solid var(--line);padding:5px 5px max(6px,env(safe-area-inset-bottom))}
 .tabbar button{display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 2px;border-radius:10px;font-size:10px;font-weight:800;color:var(--tx3)}
 .tabbar button.on{color:var(--acc);background:var(--accSoft)}
 .searchbtn kbd{display:none}
 .row,.row3{grid-template-columns:1fr}
 .work{padding-bottom:96px}
 .topbar{padding:10px 14px}
 .topbar .chipg{display:none}
 .kpi b{font-size:20px}
 .hero .hv{font-size:27px}
}
@media(max-width:560px){
 .kgrid{grid-template-columns:repeat(2,1fr)}
 .hero{padding:15px 16px}.hero .hv{font-size:23px}
 .card{padding:12px;border-radius:14px}
 .work{padding:10px 10px 96px;max-width:100%}
 table{font-size:11.5px}th,td{padding:7px 6px}
 .seg{width:100%}.seg button{flex:1;padding:6px 8px}
 .kpi b{font-size:19px}.kpi{padding:11px 12px}
 .li{padding:10px}.btn{padding:9px 11px;font-size:12.5px}
}
::-webkit-scrollbar{width:8px;height:8px}::-webkit-scrollbar-thumb{background:var(--line);border-radius:8px}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body>

<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true" focusable="false">
<defs>
<symbol id="i-home" viewBox="0 0 24 24"><path d="M3 10.6 12 3l9 7.6V20a1 1 0 0 1-1 1h-5.2v-6H9.2v6H4a1 1 0 0 1-1-1z"/></symbol>
<symbol id="i-dice" viewBox="0 0 24 24"><rect x="3.2" y="3.2" width="17.6" height="17.6" rx="4.2"/><path d="M8.2 8.2h.01M15.8 8.2h.01M12 12h.01M8.2 15.8h.01M15.8 15.8h.01"/></symbol>
<symbol id="i-hash" viewBox="0 0 24 24"><path d="M4.5 9h15M4.5 15h15M10 3.5 8 20.5M16 3.5l-2 17"/></symbol>
<symbol id="i-sw" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.4"/><circle cx="12" cy="12" r="3.1"/></symbol>
<symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
<symbol id="i-receipt" viewBox="0 0 24 24"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2z"/><path d="M9.2 8.2h5.6M9.2 12h5.6"/></symbol>
<symbol id="i-users" viewBox="0 0 24 24"><path d="M15.6 20.4v-1.8a3.8 3.8 0 0 0-3.8-3.8H6.6a3.8 3.8 0 0 0-3.8 3.8v1.8"/><circle cx="9.2" cy="7.4" r="3.6"/><path d="M17 4.3a3.6 3.6 0 0 1 0 6.9M21.2 20.4v-1.8a3.8 3.8 0 0 0-2.9-3.7"/></symbol>
<symbol id="i-key" viewBox="0 0 24 24"><circle cx="8.4" cy="15.6" r="4.1"/><path d="M11.4 12.6 20.6 3.4M17.6 3.4h3.2v3.2"/></symbol>
<symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.8"/><path d="M12 7.2v5.2l3.2 2"/></symbol>
<symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 3 20 6v6.1c0 4.9-3.4 8.2-8 8.9-4.6-.7-8-4-8-8.9V6z"/></symbol>
<symbol id="i-box" viewBox="0 0 24 24"><path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></symbol>
<symbol id="i-msg" viewBox="0 0 24 24"><path d="M20.5 12.6a7.9 7.9 0 0 1-11.4 7L4 21l1.5-4.6A7.9 7.9 0 1 1 20.5 12.6z"/><path d="M8.6 11h6.8M8.6 14.4h4.4"/></symbol>
<symbol id="i-gear" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.2"/><path d="M12 2.6v3M12 18.4v3M2.6 12h3M18.4 12h3M5.1 5.1 7.2 7.2M16.8 16.8l2.1 2.1M18.9 5.1 16.8 7.2M7.2 16.8l-2.1 2.1"/></symbol>
<symbol id="i-book" viewBox="0 0 24 24"><path d="M4 4.6A2 2 0 0 1 6 2.6h13v18H6a2 2 0 0 0-2 2z"/><path d="M4 4.6v15.2M8.4 7.4h6.4M8.4 11.4h6.4"/></symbol>
<symbol id="i-search" viewBox="0 0 24 24"><circle cx="10.8" cy="10.8" r="7"/><path d="M20.2 20.2 16 16"/></symbol>
<symbol id="i-refresh" viewBox="0 0 24 24"><path d="M20.2 11.2a8.2 8.2 0 1 0-2.4 6.5M20.4 4.2v7h-7"/></symbol>
<symbol id="i-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.4v2.2M12 19.4v2.2M2.4 12h2.2M19.4 12h2.2M5.2 5.2l1.6 1.6M17.2 17.2l1.6 1.6M18.8 5.2l-1.6 1.6M6.8 17.2l-1.6 1.6"/></symbol>
<symbol id="i-moon" viewBox="0 0 24 24"><path d="M20.4 14.6A8.6 8.6 0 0 1 9.4 3.6a8.6 8.6 0 1 0 11 11z"/></symbol>
<symbol id="i-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></symbol>
<symbol id="i-check" viewBox="0 0 24 24"><path d="M4.5 12.6 9.6 17.8 19.6 6.6"/></symbol>
<symbol id="i-edit" viewBox="0 0 24 24"><path d="M4 20h4.2L19 9.2a2.9 2.9 0 0 0-4.2-4.2L4 15.8z"/><path d="M13.8 6.2l4 4"/></symbol>
<symbol id="i-trash" viewBox="0 0 24 24"><path d="M4 7h16M9.2 7V4h5.6v3M6.2 7l1 13.4h9.6L17.8 7"/></symbol>
<symbol id="i-lock" viewBox="0 0 24 24"><rect x="4.2" y="10.2" width="15.6" height="10.2" rx="2.4"/><path d="M8.2 10.2V7.2a3.8 3.8 0 0 1 7.6 0v3"/></symbol>
<symbol id="i-unlock" viewBox="0 0 24 24"><rect x="4.2" y="10.2" width="15.6" height="10.2" rx="2.4"/><path d="M8.2 10.2V7.2a3.8 3.8 0 0 1 7.2-1.6"/></symbol>
<symbol id="i-copy" viewBox="0 0 24 24"><rect x="9" y="9" width="11.4" height="11.4" rx="2.4"/><path d="M5.6 15.2V5.6a2 2 0 0 1 2-2h8"/></symbol>
<symbol id="i-save" viewBox="0 0 24 24"><path d="M19.2 21H4.8V3h11.4l3 3z"/><path d="M8.2 3v6h7.6V3M8.2 21v-7h7.6v7"/></symbol>
<symbol id="i-wallet" viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="13.4" rx="2.6"/><path d="M3 10.4h18M16.2 14.6h2"/></symbol>
<symbol id="i-next" viewBox="0 0 24 24"><path d="M9.2 6l6 6-6 6"/></symbol>
<symbol id="i-up" viewBox="0 0 24 24"><path d="M12 19.2V5M6 11l6-6 6 6"/></symbol>
<symbol id="i-down" viewBox="0 0 24 24"><path d="M12 4.8V19M6 13l6 6 6-6"/></symbol>
<symbol id="i-eye" viewBox="0 0 24 24"><path d="M2.4 12S6 6.2 12 6.2 21.6 12 21.6 12 18 17.8 12 17.8 2.4 12 2.4 12z"/><circle cx="12" cy="12" r="2.7"/></symbol>
<symbol id="i-alert" viewBox="0 0 24 24"><path d="M12 3.6 2.8 20.2h18.4z"/><path d="M12 9.6v4.2M12 17h.01"/></symbol>
<symbol id="i-info" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.8"/><path d="M12 11v5.4M12 7.8h.01"/></symbol>
<symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13.2 2.4 4 14.2h6.8L10.2 21.6 20 9.8h-6.8z"/></symbol>
<symbol id="i-link" viewBox="0 0 24 24"><path d="M10 14.2a4 4 0 0 0 5.7 0l3-3a4 4 0 1 0-5.7-5.7L11.5 7"/><path d="M14 9.8a4 4 0 0 0-5.7 0l-3 3a4 4 0 1 0 5.7 5.7L12.5 17"/></symbol>
<symbol id="i-download" viewBox="0 0 24 24"><path d="M12 3.4v11.8M7 10.4l5 5 5-5M4 20.6h16"/></symbol>
<symbol id="i-external" viewBox="0 0 24 24"><path d="M14 3.4h6.6V10M20.6 3.4 11 13M19 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h5"/></symbol>
<symbol id="i-menu" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></symbol>
<symbol id="i-dot" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.6" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-chart" viewBox="0 0 24 24"><path d="M3.4 20.6h17.2M6.6 20.6V11M11.4 20.6V5M16.2 20.6v-7.4M21 20.6v-4"/></symbol>
<symbol id="i-calendar" viewBox="0 0 24 24"><rect x="3.2" y="5.2" width="17.6" height="16" rx="2.6"/><path d="M3.2 10.2h17.6M8.2 2.8v4M15.8 2.8v4"/></symbol>
<symbol id="i-filter" viewBox="0 0 24 24"><path d="M3.4 5.2h17.2l-6.8 8v6.4l-3.6-2v-4.4z"/></symbol>
<symbol id="i-logout" viewBox="0 0 24 24"><path d="M15 4h4a1.4 1.4 0 0 1 1.4 1.4v13.2A1.4 1.4 0 0 1 19 20h-4M9.8 8 5.8 12l4 4M5.8 12h10"/></symbol>
<symbol id="i-spark" viewBox="0 0 24 24"><path d="M3 13h3.6L9 6l3.4 12 2.2-7H21"/></symbol>
<symbol id="i-tag" viewBox="0 0 24 24"><path d="M20.4 12.6 12.6 20.4a1.8 1.8 0 0 1-2.5 0L3.6 14a1.8 1.8 0 0 1-.5-1.3V4.6a1.6 1.6 0 0 1 1.6-1.6h8.1a1.8 1.8 0 0 1 1.3.5l6.3 6.3a1.8 1.8 0 0 1 0 2.8z"/><path d="M8 8h.01"/></symbol>
<symbol id="i-mark" viewBox="0 0 24 24"><path d="M4 19V8.6a2 2 0 0 1 2-2h5.2L14 9.4h4a2 2 0 0 1 2 2V19a1.6 1.6 0 0 1-1.6 1.6H5.6A1.6 1.6 0 0 1 4 19z" fill="currentColor" stroke="none"/><path d="M8.4 13.6h6.4" stroke="#070b12" stroke-width="1.9"/></symbol>
</defs>
</svg>

<div id="login" class="loginwrap hide"><div class="lgbox">
 <div class="mark"><svg class="ic xl"><use href="#i-mark"/></svg></div>
 <div style="text-align:center;margin-bottom:16px"><h1 style="font-size:21px">PAW TX · Quản trị</h1>
  <p class="muted" style="font-size:12px;margin-top:5px">KEY LC79 = 2 bàn Hũ + MD5 &nbsp;·&nbsp; KEY SUNWIN = 1 bàn</p></div>
 <div class="card" style="margin:0">
  <div id="lgwarn" class="note warn hide" style="margin-bottom:12px"><svg class="ic sm"><use href="#i-alert"/></svg><span>Chưa đặt biến <b>ADMIN_PASSWORD</b> trên Render. Vào Environment → thêm biến rồi redeploy.</span></div>
  <label style="margin-top:0">Mật khẩu quản trị</label>
  <div class="pw"><input id="pw" type="password" autocomplete="current-password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doLogin()">
   <button class="eye" type="button" data-act="eye" title="Hiện / ẩn"><svg class="ic sm"><use href="#i-eye"/></svg></button></div>
  <button class="btn pri big" style="margin-top:12px" data-act="login"><svg class="ic sm"><use href="#i-lock"/></svg> Vào quản trị</button>
  <p class="muted" style="margin:12px 0 0;font-size:11.5px">Mật khẩu lấy từ biến môi trường ADMIN_PASSWORD trên Render.</p>
 </div>
</div></div>

<div id="app" class="shell hide">
 <aside class="rail">
  <div class="brand"><div class="mark"><svg class="ic lg"><use href="#i-mark"/></svg></div><div><b>PAW TX</b><small>QUẢN TRỊ</small></div></div>
  <div id="nav"></div>
  <div class="grow"></div>
  <div class="railfoot">
   <button class="navi" data-act="theme"><svg class="ic" id="sym-theme"><use href="#i-moon"/></svg><span>Đổi giao diện</span></button>
   <button class="navi" data-act="go" data-arg="hd"><svg class="ic"><use href="#i-book"/></svg><span>Hướng dẫn API</span></button>
   <button class="navi" data-act="logout"><svg class="ic"><use href="#i-logout"/></svg><span>Đăng xuất</span></button>
  </div>
 </aside>
 <div class="main">
  <header class="topbar">
   <div class="ttl"><h1 id="ttl">Tổng quan</h1><small id="sub"></small></div>
   <span class="chipg" id="chipg">VẬN HÀNH</span>
   <div class="sp"></div>
   <span class="livepill" id="livepill"><i></i>Tự động</span>
   <button class="searchbtn" data-act="palette" title="Tìm trang (Ctrl K)"><svg class="ic sm"><use href="#i-search"/></svg><kbd>Ctrl K</kbd></button>
   <button class="tbtn" data-act="reload" id="rf" title="Tải lại"><svg class="ic"><use href="#i-refresh"/></svg></button>
   <button class="tbtn" data-act="theme" title="Đổi giao diện" id="th"><svg class="ic"><use href="#i-moon"/></svg></button>
  </header>
  <main class="work"><div id="v"></div></main>
 </div>
 <nav class="tabbar" id="tabs"></nav>
</div>
<div id="pbar"></div><div id="toast"></div>

<script>
/* ─────────── 1. ICON (SVG, không dùng emoji) ─────────── */
function ic(n,cls){return '<svg class="ic'+(cls?' '+cls:'')+'" aria-hidden="true"><use href="#i-'+(n||'dot')+'"/></svg>';}
function sy(n,cls){return ic(n,cls);}

/* ─────────── 2. TIỆN ÍCH ─────────── */
const $=id=>document.getElementById(id);
const $$=(sel,root)=>Array.prototype.slice.call((root||document).querySelectorAll(sel));
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num=v=>{const n=parseFloat(String(v==null?0:v).replace(/[^\d.-]/g,''));return isNaN(n)?0:n;};
const dfmt=h=>h?esc(String(h).replace('T',' ').slice(0,16)):'—';
const XM=n=>{n=num(n);return Math.abs(n)>=1000?(n/1000).toLocaleString('vi-VN',{maximumFractionDigits:1})+' triệu':(Math.round(n*10)/10).toLocaleString('vi-VN')+'K';};
const pct=v=>Math.round(num(v))+'%';
const KLABEL={lc79:'LC79 · 2 bàn (Hũ + MD5)',sunwin:'Sunwin · 1 bàn',all:'Tất cả (key cũ)'};
const KSHORT={lc79:'LC79',sunwin:'SUNWIN',all:'KEY CŨ'};
const kcls=g=>g==='sunwin'?'sw':'idle';
const pill=t=>({'hoạt động':'act','khóa':'ban','hết hạn':'exp','chưa kích hoạt':'idle'}[t]||'');
const SIDE=s=>s==='TAI'?'TÀI':s==='XIU'?'XỈU':'—';
const XOWN=b=>!b||b==='admin'?'Admin':String(b).replace('ctv:','CTV ');
function ago(iso){if(!iso)return '—';const s=(Date.now()-new Date(iso))/1000;if(isNaN(s))return dfmt(iso);
 if(s<60)return 'vừa xong';if(s<3600)return Math.floor(s/60)+' phút trước';if(s<86400)return Math.floor(s/3600)+' giờ trước';return Math.floor(s/86400)+' ngày trước';}
const EVIC={tao_key:'plus',kich_hoat:'check',goi_api:'bolt',het_han:'clock',ctv_login:'logout',ctv_logout:'logout',ctv_create_key:'plus',ctv_collect:'wallet',ctv_bill:'receipt',ctv_lock_key:'lock',ctv_unlock_key:'unlock',ctv_extend_key:'clock'};
function evIc(loai){return ic(EVIC[loai]||'dot','sm');}

/* ─────────── 3. MẠNG ─────────── */
let _busy=0;
function bar(on){_busy=Math.max(0,_busy+(on?1:-1));const p=$('pbar');if(!p)return;
 if(_busy>0){p.style.opacity='1';if(!p.style.width||p.style.width==='0px')p.style.width='35%';}
 else{p.style.width='100%';setTimeout(()=>{p.style.opacity='0';p.style.width='0';},320);}}
async function api(p,o){
 o=o||{};bar(1);
 try{
  const r=await fetch(p,Object.assign({credentials:'same-origin',headers:{'Content-Type':'application/json'}},o));
  if(r.status===401&&p.indexOf('/admin')===0){showLogin();throw new Error('unauthorized');}
  const ct=(r.headers.get('content-type')||'');
  if(ct.indexOf('json')<0)throw new Error('Máy chủ trả mã '+r.status);
  return await r.json();
 }finally{bar(-1);}
}
const post=(p,b)=>api(p,{method:'POST',body:JSON.stringify(b||{})});
function toast(m){const t=$('toast');if(!t)return;t.textContent=m;t.style.display='block';clearTimeout(t._h);t._h=setTimeout(()=>{t.style.display='none';},2800);}

/* ─────────── 4. KHO DỮ LIỆU + ĐIỀU HƯỚNG ─────────── */
const DB={pkgs:[],keys:[],keysAt:0,kv:[],orders:[],ctvs:[],pays:[],paysHis:[],cust:[],ov:null,ins:null,tpls:{},tnames:{},set:{},
 sel:new Set(),page:40,kf:{q:'',st:'all',by:'all',sort:'new',game:'all'},
 mk:{game:'lc79',pkg:'',tpl:'',days:'',hours:'',perm:false,res:null,msgs:[]},
 lk:{by:'all',loai:'all',q:''},kfq:{q:'',by:'all',tag:'all'},xd:{u:'',j:null,tab:'ov'},pgame:{}};
let CUR='ov',TIMER=null;
function clearTimer(){if(TIMER){clearInterval(TIMER);TIMER=null;}}
function every(ms,fn){clearTimer();TIMER=setInterval(fn,ms);}

const VIEWS={
 ov:{t:'Tổng quan',s:'Doanh thu · cầu · cảnh báo vận hành',g:'VẬN HÀNH',i:'home',r:vOverview},
 hu:{t:'Bàn Hũ',s:'LC79 · Tài Xỉu Hũ · tự cập nhật 8s',g:'VẬN HÀNH',i:'dice',r:()=>vBan('hu')},
 md5:{t:'Bàn MD5',s:'LC79 · Tài Xỉu MD5 · tự cập nhật 8s',g:'VẬN HÀNH',i:'hash',r:()=>vBan('md5')},
 sunwin:{t:'Bàn Sunwin',s:'Sunwin · 1 bàn riêng · tự cập nhật 8s',g:'VẬN HÀNH',i:'sw',r:()=>vBan('sunwin')},
 mk:{t:'Bán key',s:'Tạo key · lấy tin nhắn gửi khách',g:'BÁN HÀNG',i:'plus',r:vCreate},
 dh:{t:'Đơn hàng',s:'Theo dõi đơn · giao key · bill',g:'BÁN HÀNG',i:'receipt',r:vOrders},
 kh:{t:'Khách hàng',s:'Hồ sơ khách · thiết bị · lịch sử',g:'BÁN HÀNG',i:'users',r:vCustomers},
 kl:{t:'Danh sách key',s:'Lọc · sửa · khoá · gia hạn',g:'KEY',i:'key',r:vKeys},
 lk:{t:'Lịch sử key',s:'Sự kiện tạo · kích hoạt · gọi API',g:'KEY',i:'clock',r:vLog},
 ctv:{t:'Cộng tác viên',s:'Tài khoản · quyền · công nợ',g:'ĐỐI TÁC',i:'shield',r:vCtv},
 pkg:{t:'Gói giá',s:'Thời hạn · giá lẻ · giá nhập',g:'ĐỐI TÁC',i:'box',r:vPkgs},
 tpl:{t:'Mẫu tin nhắn',s:'Nội dung gửi khách · biến tự động',g:'HỆ THỐNG',i:'msg',r:vTpl},
 set:{t:'Cài đặt',s:'Link tool · hỗ trợ · token · sao lưu',g:'HỆ THỐNG',i:'gear',r:vSet},
 hd:{t:'Hướng dẫn API',s:'Luồng bán key · endpoint',g:'HỆ THỐNG',i:'book',r:vGuide}
};
const GROUPS=['VẬN HÀNH','BÁN HÀNG','KEY','ĐỐI TÁC','HỆ THỐNG'];
const TABS=['ov','mk','kl','ctv','more'];

function drawNav(){
 const box=$('nav');if(!box)return;
 box.innerHTML=GROUPS.map(g=>'<div class="grp">'+g+'</div>'+Object.keys(VIEWS).filter(k=>VIEWS[k].g===g).map(k=>{
  const v=VIEWS[k],badge=(k==='ctv'&&DB.pays.length)?'<span class="bdg">'+DB.pays.length+'</span>':'';
  return '<button class="navi'+(CUR===k?' on':'')+'" data-act="go" data-arg="'+k+'">'+ic(v.i)+'<span>'+esc(v.t)+'</span>'+badge+'</button>';
 }).join('')).join('');
 const tb=$('tabs');
 tb.innerHTML=TABS.map(k=>{
  if(k==='more')return '<button data-act="more"'+(CUR!=='ov'&&TABS.indexOf(CUR)<0?' class="on"':'')+'>'+ic('menu','sm')+'Thêm</button>';
  const v=VIEWS[k];return '<button data-act="go" data-arg="'+k+'"'+(CUR===k?' class="on"':'')+'>'+ic(v.i,'sm')+esc(v.t.split(' ')[0])+'</button>';
 }).join('');
}
function markNav(){$$('#nav .navi').forEach(b=>b.classList.toggle('on',b.dataset.arg===CUR));
 $$('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.arg===CUR||(b.dataset.act==='more'&&TABS.indexOf(CUR)<0)));}
function setAuto(on){const p=$('livepill');if(p)p.classList.toggle('on',!!on);}

async function go(id){
 if(!VIEWS[id])id='ov';
 clearTimer();setAuto(false);closeModal();CUR=id;DB.sel.clear();DB.page=40;
 const v=VIEWS[id];$('ttl').textContent=v.t;$('sub').textContent=v.s;
 const cg=$('chipg');if(cg)cg.textContent=v.g;
 markNav();
 $('v').innerHTML='<div class="skel"></div><div class="skel"></div><div class="skel"></div>';
 try{await v.r();}
 catch(e){
  if(String(e&&e.message)==='unauthorized')return;
  $('v').innerHTML='<div class="card"><div class="card-h"><h2 class="sp">Không tải được trang này</h2><button class="btn sm" data-act="reload">'+ic('refresh','sm')+' Thử lại</button></div><p class="muted">'+esc(e&&e.message||'lỗi không xác định')+'</p></div>';
 }
 window.scrollTo({top:0});
}
async function reload(){
 try{await loadBase();}catch(e){}
 drawNav();
 await go(CUR);
 toast('Đã tải lại dữ liệu');
}
async function loadBase(){
 const pk=await api('/admin/api/packages');DB.pkgs=pk.packages||[];
 const st=await api('/admin/api/settings');DB.set=st.settings||{};DB.tpls=st.templates||{};DB.tnames=st.template_names||{};
 if(DB.mk.pkg&&!DB.pkgs.some(p=>p.id===DB.mk.pkg))DB.mk.pkg='';
 if(!DB.mk.pkg)DB.mk.pkg=(DB.pkgs.find(p=>p.id==='P3')||DB.pkgs[0]||{}).id||'';
 if(!DB.mk.tpl)DB.mk.tpl=Object.keys(DB.tpls).find(k=>DB.tpls[k]===DB.set.payment_template)||Object.keys(DB.tpls)[0]||'';
}

/* ─────────── 5. MODAL / THEME / LOGIN ─────────── */
function modal(html,wide){closeModal();
 const m=document.createElement('div');m.className='mbg';m.id='mdl';
 m.innerHTML='<div class="modal'+(wide?' xm':'')+'">'+html+'</div>';
 m.addEventListener('click',e=>{if(e.target===m)closeModal();});
 document.body.appendChild(m);}
function closeModal(){const m=$('mdl');if(m)m.remove();}
function setTheme(t){document.documentElement.dataset.theme=t;try{localStorage.setItem('paw_theme',t);}catch(e){}
 const n=t==='dark'?'moon':'sun';
 const a=$('sym-theme');if(a)a.innerHTML='<use href="#i-'+n+'"/>';
 const b=$('th');if(b)b.innerHTML='<svg class="ic"><use href="#i-'+n+'"/></svg>';}
function toggleTheme(){setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark');}
function showLogin(){const app=$('app'),lg=$('login');if(app)app.classList.add('hide');if(lg)lg.classList.remove('hide');}
async function doLogin(){
 const btn=document.querySelector('#login .btn.pri');if(btn){btn.disabled=true;btn.classList.add('load');}
 try{
  const r=await fetch('/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({pw:($('pw').value||'').trim()})});
  const j=await r.json();
  if(j.ok){await boot();}else toast(j.thong_bao||'Sai mật khẩu');
 }catch(e){toast('Không kết nối được máy chủ');}
 finally{if(btn){btn.disabled=false;btn.classList.remove('load');}}
}
function palette(){
 const rows=Object.keys(VIEWS).map(k=>'<button class="opt" data-act="go-close" data-arg="'+k+'" style="width:100%;margin-bottom:7px">'+ic(VIEWS[k].i,'sm')+' <b style="display:inline">'+esc(VIEWS[k].t)+'</b> <small>'+esc(VIEWS[k].g)+'</small></button>').join('');
 modal('<div class="mh"><h2>Đi tới trang</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div><input id="pal" placeholder="Gõ tên trang…" oninput="palFilter(this.value)"><div id="palr" style="margin-top:10px">'+rows+'</div>',true);
 palFilter('');$('pal').focus();
}
function palFilter(q){q=(q||'').toLowerCase();
 const html=Object.keys(VIEWS).filter(k=>VIEWS[k].t.toLowerCase().indexOf(q)>=0||VIEWS[k].g.toLowerCase().indexOf(q)>=0||VIEWS[k].s.toLowerCase().indexOf(q)>=0)
  .map(k=>'<button class="opt" data-act="go-close" data-arg="'+k+'" style="width:100%;margin-bottom:6px">'+ic(VIEWS[k].i,'sm')+' <b style="display:inline">'+esc(VIEWS[k].t)+'</b> <small>'+esc(VIEWS[k].s)+'</small></button>').join('');
 $('palr').innerHTML=html||'<p class="muted">Không thấy trang nào</p>';}

/* ─────────── 6. TỔNG QUAN ─────────── */
function bars(arr,fmt){const mx=Math.max(1,...arr.map(x=>num(x[1])));
 return '<div class="bars">'+arr.map((x,i)=>{
  const h=Math.round(num(x[1])/mx*82);
  return '<div><b>'+(num(x[1])?(fmt?fmt(x[1]):num(x[1])):'')+'</b><i style="height:'+Math.max(2,h)+'%"></i><span>'+esc(String(x[0]).slice(-2))+'</span></div>';
 }).join('')+'</div>';}
function heat(arr){const mx=Math.max(1,...arr.map(num));
 return '<div class="heat">'+arr.map((v,i)=>'<i title="'+i+'h · '+v+' key" style="height:'+Math.max(5,Math.round(num(v)/mx*100))+'%;opacity:'+(num(v)?0.35+0.65*num(v)/mx:0.18)+'"></i>').join('')+'</div>'
  +'<div class="hl">'+arr.map((v,i)=>'<span>'+(i%3===0?i:'')+'</span>').join('')+'</div>';}
function spark(arr){const mx=Math.max(1,...arr.map(x=>num(x[1])));
 return '<div class="spark">'+arr.map((x,i)=>'<i'+(i===arr.length-1?' class="hi"':'')+' style="height:'+Math.max(3,Math.round(num(x[1])/mx*100))+'%" title="'+esc(x[0])+': '+XM(x[1])+'"></i>').join('')+'</div>';}
function ring(p,cls){return '<div class="ring" style="--pv:'+Math.max(0,Math.min(100,num(p)))+';--rc:var(--'+(cls||'ok')+')"><b>'+Math.round(num(p))+'%</b></div>';}
function barline(rows){
 return rows.map(r=>'<div style="margin-bottom:10px"><div style="display:flex;gap:8px;font-size:12.5px;align-items:baseline"><b class="sp" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(r[0])+'</b><span class="muted nowrap">'+r[1]+'</span></div>'
  +'<div class="pgb" style="margin-top:5px"><i style="width:'+Math.max(2,Math.min(100,num(r[2])))+'%"></i></div></div>').join('');
}
function analysisCard(b){
 const pt=b.phan_tich||{},bt=(pt.backtest||{}).ty_le;
 const side=pt.du_doan||b.du_doan_tiep;
 const code=esc(b.code),live=!b.loi;
 return '<div class="card"><div class="card-h"><span class="hi">'+ic(b.game==='sunwin'?'sw':'dice','sm')+'</span><h2 class="sp">'+esc(b.ten)+'</h2>'
 +'<span class="tag '+(live?'act':'ban')+'">'+(live?'LIVE':'lỗi nguồn')+'</span></div>'
 +'<div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:10px">'+ring(num(b.ty_le_thang),num(b.ty_le_thang)>=55?'ok':'warn')
 +'<div style="flex:1;min-width:130px">'
 +'<div class="muted" style="font-size:11px;font-weight:800;letter-spacing:.06em">PHIÊN TIẾP THEO</div>'
 +'<div style="margin-top:3px">'+(side?'<span class="tag '+(side==='TAI'?'tai':'xiu')+' lg">'+SIDE(side)+(pt.do_tin_cay?' · '+Math.round(num(pt.do_tin_cay)*100)+'%':'')+'</span>':'<span class="tag exp lg">CHỜ — chưa đủ tín hiệu</span>')+'</div>'
 +'<div class="muted" style="margin-top:6px">Phiên #'+esc(b.phien_hien_tai||'—')+' · '+num(b.luoi_ms)+'ms · '+num(b.thang)+' thắng / '+num(b.thua)+' thua</div>'
 +'</div></div>'
 +'<dl class="dl" style="border-top:1px solid var(--line);padding-top:9px">'
 +'<dt>Nhịp đang đọc</dt><dd>'+(pt.nhip?esc(pt.nhip):'—')+'</dd>'
 +'<dt>Độ thuần</dt><dd>'+(pt.do_thuan!=null?Math.round(num(pt.do_thuan)*100)+'%':'—')+'</dd>'
 +'<dt>Backtest tự chấm</dt><dd style="color:var(--'+(bt==null?'tx2':bt>=55?'ok':bt<50?'bad':'warn')+')">'+(bt==null?'—':bt+'%')+'</dd>'
 +'</dl>'
 +'<button class="btn sm" style="margin-top:10px" data-act="go" data-arg="'+code+'">'+ic('chart','sm')+' Xem phân tích đầy đủ '+ic('next','xs')+'</button></div>';
}

async function vOverview(){
 const ov=await api('/admin/api/overview');
 let ins=null;try{ins=await api('/admin/api/insights');}catch(e){ins=null;}
 DB.ov=ov;DB.ins=ins;
 const a=ov.key_admin_console||{},ban=ov.ban||[];
 const apicalls=num(ov.luot_goi_hu)+num(ov.luot_goi_md5)+num(ov.luot_goi_sunwin);
 const d14=(ins&&ins.doanh_thu_14)||[];
 const g7=ins?num(ins.doanh_thu_7d_k)-num(ins.doanh_thu_7d_truoc_k):0;
 const p7=(ins&&num(ins.doanh_thu_7d_truoc_k))?Math.round(g7/num(ins.doanh_thu_7d_truoc_k)*100):null;
 const alerts=(ins&&ins.canh_bao)||[];

 $('v').innerHTML=
 (alerts.length?('<div class="card"><div class="card-h"><span class="hi">'+ic('alert','sm')+'</span><h2 class="sp">Cần chú ý</h2><span class="tag exp">'+alerts.length+'</span></div>'
   +alerts.map(x=>'<button class="alert '+(x.muc||'')+'" data-act="alertgo" data-arg="'+esc(x.go||'ov')+'"><span class="ai">'+ic(x.muc==='bad'?'alert':x.muc==='warn'?'alert':'info','sm')+'</span><span class="sp">'+esc(x.text)+'</span>'+ic('next','xs')+'</button>').join('')+'</div>'):'')
 +'<div class="hero"><div class="hrow"><div><div class="lbl">DOANH THU HÔM NAY · '+num(ins&&ins.key_hom_nay)+' KEY</div><div class="hv">'+XM(ins?ins.doanh_thu_hom_nay_k:0)+'</div>'
 +'<span class="bdg">'+ic('chart','xs')+' 7 ngày '+XM(ins?ins.doanh_thu_7d_k:0)+(p7===null?'':' · '+(g7>=0?'+':'')+p7+'%')+'</span></div>'
 +'<div style="flex:1;min-width:160px"><div class="lbl" style="margin-bottom:4px">DOANH THU 14 NGÀY</div>'+spark(d14)+'</div></div></div>'
 +'<div class="kgrid">'
 +'<div class="kpi"><div class="kl">'+ic('check','xs')+'Tỷ lệ kích hoạt</div><b>'+pct(ins?ins.ty_le_kich_hoat:0)+'</b><small>key đã dùng thử</small></div>'
 +'<div class="kpi ok"><div class="kl">'+ic('key','xs')+'Key đang chạy</div><b>'+num(ov.dang_hoat_dong)+'</b><small>trên tổng '+num(ov.so_key)+' key</small></div>'
 +'<div class="kpi wn"><div class="kl">'+ic('clock','xs')+'Cần gia hạn</div><b>'+((ins&&ins.gia_han)?ins.gia_han.length:0)+'</b><small>sắp / vừa hết hạn</small></div>'
 +'<div class="kpi bl"><div class="kl">'+ic('bolt','xs')+'Lượt gọi API</div><b>'+apicalls.toLocaleString('vi-VN')+'</b><small>Hũ '+num(ov.luot_goi_hu)+' · MD5 '+num(ov.luot_goi_md5)+' · SW '+num(ov.luot_goi_sunwin)+'</small></div>'
 +'<div class="kpi"><div class="kl">'+ic('shield','xs')+'Cộng tác viên</div><b>'+num(ov.so_ctv)+'</b><small>'+num(ov.so_don_hang)+' đơn đã tạo</small></div>'
 +'<div class="kpi ok"><div class="kl">'+ic('wallet','xs')+'Doanh thu ước</div><b>'+XM(ov.doanh_thu_k)+'</b><small>theo giá đã bán</small></div>'
 +'<div class="kpi"><div class="kl">'+ic('box','xs')+'Tổng key</div><b>'+num(ov.so_key)+'</b><small>'+num(ov.het_han)+' hết hạn</small></div>'
 +'<div class="kpi '+(ov.gist_backup?'ok':'wn')+'"><div class="kl">'+ic('save','xs')+'Sao lưu Gist</div><b>'+(ov.gist_backup?'BẬT':'TẮT')+'</b><small>'+(ov.gist_backup?'an toàn khi redeploy':'nên bật ngay')+'</small></div>'
 +'</div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('spark','sm')+'</span><h2 class="sp">Bàn cược · tự động phân tích</h2><span class="muted">engine tự dự đoán mỗi phiên · tự chấm lại</span></div>'
 +'<div class="grid g3">'+ban.map(analysisCard).join('')+'</div></div>'
 +'<div class="grid g2"><div class="card"><div class="card-h"><h2 class="sp">Doanh thu 14 ngày</h2><span class="muted">'+XM(ins?ins.doanh_thu_7d_k:0)+' / 7 ngày</span></div>'+bars((ins?ins.doanh_thu_14:[]).map(x=>[x[0],x[1]]),XM)+'</div>'
 +'<div class="card"><div class="card-h"><h2 class="sp">Key tạo 14 ngày</h2><span class="muted">'+num(ov.key_theo_ngay?ov.key_theo_ngay.reduce((s,x)=>s+num(x[1]),0):0)+' key</span></div>'+bars(d14.map(x=>[x[0],x[2]]))+'</div></div>'
 +(ins&&ins.top_chu&&ins.top_chu.length?'<div class="card"><div class="card-h"><span class="hi">'+ic('users','sm')+'</span><h2 class="sp">Người bán tốt nhất · 7 ngày</h2></div>'
   +barline(ins.top_chu.map(o=>{const mx=Math.max(1,...ins.top_chu.map(z=>num(z.doanh_thu_7d_k)||num(z.doanh_thu_k)));
    return [o.ten+' · '+XOWN(o.by),'<b>'+XM(o.doanh_thu_7d_k)+'</b> · '+num(o.key_7d)+' key',Math.round((num(o.doanh_thu_7d_k)||num(o.doanh_thu_k))/mx*100)];}))+'</div>':'')
 +(ins&&ins.theo_goi&&ins.theo_goi.length?'<div class="card"><div class="card-h"><span class="hi">'+ic('box','sm')+'</span><h2 class="sp">Gói bán chạy</h2></div>'
   +barline(ins.theo_goi.slice(0,8).map(p=>{const mx=Math.max(1,...ins.theo_goi.map(z=>num(z.doanh_thu_k)));
    return [p.goi,num(p.so_key)+' key · <b>'+XM(p.doanh_thu_k)+'</b>',Math.round(num(p.doanh_thu_k)/mx*100)];}))+'</div>':'')
 +'<div class="grid g2"><div class="card"><div class="card-h"><h2 class="sp">Giờ vàng tạo key</h2><span class="muted">0h → 23h</span></div>'+(ins?heat(ins.theo_gio||[]):'<p class="muted">—</p>')+'</div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('gear','sm')+'</span><h2 class="sp">Hệ thống</h2><span class="tag '+(ov.gist_backup?'act':'exp')+'">'+(ov.gist_backup?'Gist bật':'Gist tắt')+'</span></div>'
 +'<p class="muted" style="margin-bottom:4px">Token API quản trị (dùng cho /api/&lt;token&gt;/…):</p>'
 +'<p class="mono" style="word-break:break-all;font-size:12px;margin-bottom:10px">'+esc(a.token||'—')+'</p>'
 +'<div class="btns"><button class="btn sm" data-act="copyraw" data-arg="'+esc(a.token||'')+'">'+ic('copy','sm')+' Copy token</button>'
 +'<button class="btn sm" data-act="copyraw" data-arg="'+esc(a.key||'')+'">'+ic('key','sm')+' Copy key admin</button>'
 +'<button class="btn sm" data-act="go" data-arg="hd">'+ic('book','sm')+' Endpoint</button></div></div></div>'
 +(ins&&ins.gia_han&&ins.gia_han.length?'<div class="card"><div class="card-h"><span class="hi">'+ic('clock','sm')+'</span><h2 class="sp">Cơ hội gia hạn</h2><span class="tag exp">'+(ins.gia_han||[]).length+' key</span></div>'
   +ins.gia_han.slice(0,10).map((r,i)=>'<div class="evr"><div class="ei">'+ic('clock','sm')+'</div><div class="sp" style="min-width:0"><div class="b">'+esc(r.khach)+' <span class="muted">'+esc(XOWN(r.by))+'</span></div><div class="muted mono">'+esc(r.key)+'</div></div>'
   +'<span class="tag '+(r.trang_thai==='hết hạn'?'ban':'exp')+'">'+(r.trang_thai==='hết hạn'?'đã hết':'còn '+Math.max(0,Math.round(num(r.gio_con)))+'h')+'</span>'
   +'<button class="btn sm" data-act="renew" data-arg="'+i+'">'+ic('copy','sm')+' Copy lời nhắn</button></div>').join('')+'</div>':'')
 +(ins&&ins.ngu_dong&&ins.ngu_dong.length?'<div class="card"><div class="card-h"><span class="hi">'+ic('users','sm')+'</span><h2 class="sp">Khách ngủ đông</h2><span class="muted">còn hạn nhưng lâu không dùng</span></div>'
   +ins.ngu_dong.slice(0,8).map(r=>'<div class="evr"><div class="ei">'+ic('users','sm')+'</div><div class="sp" style="min-width:0"><div class="b">'+esc(r.khach)+' <span class="muted">'+esc(XOWN(r.by))+'</span></div><div class="muted mono">'+esc(r.key)+'</div></div>'
   +'<span class="tag exp">'+(r.tung_goi?'im '+num(r.ngay_im)+' ngày':'chưa gọi API')+'</span></div>').join('')+'</div>':'');

 every(25000,()=>{if(CUR==='ov'&&window.scrollY<80)vOverview().catch(()=>{});});
 setAuto(true);
}
function renewMsg(r){const t=r.trang_thai==='hết hạn'?'đã hết hạn':'sắp hết hạn (còn ~'+Math.max(1,Math.round(num(r.gio_con)))+' giờ)';
 return 'Chào '+r.khach+', key '+r.key+' của bạn '+t+'. Muốn gia hạn nhắn mình nhé'+(DB.set.support?' · '+DB.set.support:'');}

/* ─────────── 7. BÁN KEY ─────────── */
function secPkg(p){return num(p.days)*24+num(p.hours);}
function stepHead(n,title,note){const badge=(String(n).length>2)?n:'<span style="font-size:12px;font-weight:900">'+n+'</span>';return '<div class="card-h"><span class="hi">'+badge+'</span><h2 class="sp">'+title+'</h2>'+(note?'<span class="muted">'+note+'</span>':'')+'</div>';}
function vCreate(){
 const all=DB.pkgs.slice().sort((a,b)=>(secPkg(a)||1e9)-(secPkg(b)||1e9));
 const game=DB.mk.game==='sunwin'?'sunwin':'lc79';
 if(DB.mk.pkg&&DB.mk.pkg!=='_c'&&DB.mk.pkg!=='_p'&&!all.some(p=>p.id===DB.mk.pkg&&((p.game||'all')===game||(p.game||'all')==='all')))DB.mk.pkg='';
 const list=all.filter(p=>(p.game||'all')===game||(p.game||'all')==='all');
 if(!DB.mk.pkg&&list.length)DB.mk.pkg=list[0].id;
 const mk=DB.mk,hasPerm=list.some(p=>secPkg(p)===0);
 $('v').innerHTML='<div class="split" id="mkgrid">'
 +'<div>'
 +'<div class="card">'+stepHead('1','Loại key','bước 1 / 3')
 +'<div class="opts">'
 +'<button class="opt '+(game==='lc79'?'on':'')+'" data-act="mkGame" data-arg="lc79"><b>'+ic('dice','sm')+' KEY LC79</b><small>1 key dùng chung 2 bàn: Hũ + MD5</small></button>'
 +'<button class="opt '+(game==='sunwin'?'on':'')+'" data-act="mkGame" data-arg="sunwin"><b>'+ic('sw','sm')+' KEY SUNWIN</b><small>1 key chỉ mở bàn Sunwin</small></button></div>'
 +'<div class="pills" style="margin-top:10px">'+(game==='lc79'
   ?'<span class="tag act">'+ic('check','xs')+' /hu mở</span><span class="tag act">'+ic('check','xs')+' /md5 mở</span><span class="tag ban">'+ic('lock','xs')+' /sunwin chặn</span>'
   :'<span class="tag sw">'+ic('check','xs')+' /sunwin mở</span><span class="tag ban">'+ic('lock','xs')+' /hu · /md5 chặn</span>')+'</div>'
 +'<p class="muted" style="margin:10px 0 0">Mỗi game một loại key riêng, không dùng chéo. Sai bàn trả lỗi 403 wrong_game.</p></div>'
 +'<div class="card">'+stepHead('2','Thời hạn','bước 2 / 3')
 +'<p class="muted">Hạn tính từ lúc khách kích hoạt key.</p><div class="opts">'
 +list.map(p=>'<button class="opt '+(mk.pkg===p.id?'on':'')+'" data-act="mkPkg" data-arg="'+esc(p.id)+'"><b>'+esc(p.name)+'</b><small>'+esc(p.thoi_han)+' · '+esc(p.price||'chưa đặt giá')+' · '+esc(KSHORT[p.game]||'')+'</small></button>').join('')
 +(hasPerm?'':'<button class="opt '+(mk.perm?'on':'')+'" data-act="mkPkg" data-arg="_p"><b>Vĩnh viễn</b><small>không hết hạn</small></button>')
 +'<button class="opt '+(mk.pkg==='_c'?'on':'')+'" data-act="mkPkg" data-arg="_c"><b>Tự nhập</b><small>theo ngày / giờ</small></button></div>'
 +'<div id="custbox" class="'+(mk.pkg==='_c'?'':'hide')+'"><div class="row"><div><label>Số ngày</label><input id="o_days" type="number" min="0" inputmode="numeric" value="'+esc(mk.days)+'" placeholder="0"></div>'
 +'<div><label>Số giờ</label><input id="o_hours" type="number" min="0" inputmode="numeric" value="'+esc(mk.hours)+'" placeholder="0"></div></div>'
 +'<div class="pills" style="margin-top:9px">'+[['1 giờ',0,1],['3 giờ',0,3],['6 giờ',0,6],['12 giờ',0,12],['1 ngày',1,0],['3 ngày',3,0],['7 ngày',7,0],['30 ngày',30,0]]
   .map(q=>'<button class="pill" data-act="mkQuick" data-arg="'+q[1]+':'+q[2]+'">'+q[0]+'</button>').join('')+'</div></div></div>'
 +'<div class="card">'+stepHead('3','Thông tin khách','bước 3 / 3')
 +'<div class="row"><div><label>Số lượng key</label><input id="o_n" type="number" value="1" min="1" max="200" inputmode="numeric"></div>'
 +'<div><label>Tên khách</label><input id="o_name" placeholder="VD: Anh Tú"></div></div>'
 +'<div class="row"><div><label>Giá (trống = theo gói)</label><input id="o_price" placeholder="VD: 250K"></div>'
 +'<div><label>Tiền tố key</label><input id="o_pre" maxlength="6" placeholder="'+esc(DB.set.default_prefix||'PAXU')+'"></div></div>'
 +'<label>Ghi chú</label><input id="o_note" placeholder="Tuỳ chọn">'
 +'<button class="btn pri big" style="margin-top:14px" data-act="mkGo">'+ic('plus','sm')+' Tạo KEY '+(game==='sunwin'?'SUNWIN':'LC79')+' &amp; lấy tin nhắn</button></div>'
 +'<div class="card">'+stepHead(ic('wallet','sm'),'Sửa giá gói nhanh','tick "sync" để đổi cả key chưa kích hoạt')
 +all.map(p=>'<div style="display:flex;gap:7px;align-items:center;margin-bottom:8px"><span class="sp" style="font-size:12.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(p.name)+'</span>'
   +'<input id="qp_'+esc(p.id)+'" value="'+esc(p.price||'')+'" style="width:96px;padding:7px 9px" placeholder="giá">'
   +'<label style="display:flex;gap:4px;align-items:center;margin:0;font-size:11px;text-transform:none;letter-spacing:0;color:var(--tx2)"><input type="checkbox" id="qs_'+esc(p.id)+'" checked style="width:auto">sync</label>'
   +'<button class="btn sm pri" data-act="qPrice" data-arg="'+esc(p.id)+'">Lưu</button></div>').join('')+'</div>'
 +'</div>'
 +'<div id="mkres" class="aside-sticky">'+mkResult()+'</div></div>';
}
function mkResult(){
 const r=DB.mk.res;
 if(!r)return '<div class="card"><div class="card-h"><span class="hi">'+ic('msg','sm')+'</span><h2>Kết quả</h2></div><p class="muted">Tạo key xong, tin nhắn gửi khách sẽ hiện ở đây. Bấm là copy được luôn.</p></div>';
 DB.mk.msgs=r.msgs||[];
 return '<div class="card"><div class="card-h"><span class="hi">'+ic('check','sm')+'</span><h2 class="sp">Đơn '+esc(r.order)+'</h2><span class="tag act">'+r.keys.length+' key</span><span class="tag '+kcls(r.game)+'">'+esc(KLABEL[r.game]||'')+'</span></div>'
 +'<label style="margin-top:0">Mẫu tin nhắn</label><div class="pills" style="margin-bottom:10px">'+Object.keys(DB.tpls).map(k=>
   '<button class="pill '+(DB.mk.tpl===k?'on':'')+'" data-act="mkTpl" data-arg="'+esc(k)+'">'+esc(DB.tnames[k]||k)+'</button>').join('')+'</div>'
 +DB.mk.msgs.map((m,i)=>'<div class="msg" style="margin-bottom:7px">'+esc(m)+'</div><div class="btns" style="margin-bottom:10px">'
   +'<button class="btn pri sm" style="flex:1" data-act="copyMsg" data-arg="'+i+'">'+ic('copy','sm')+' Copy tin nhắn</button>'
   +'<button class="btn sm" data-act="copyMsgKey" data-arg="'+i+'">'+ic('key','sm')+' Key</button></div>').join('')
 +(DB.mk.msgs.length>1?'<button class="btn big" data-act="copyAll">'+ic('copy','sm')+' Copy tất cả '+DB.mk.msgs.length+' tin</button>':'')+'</div>';
}

/* ─────────── 8. DANH SÁCH KEY ─────────── */
function keyFilter(){
 const f=DB.kf,q=(f.q||'').toLowerCase().trim();
 let L=(DB.keys||[]).filter(k=>
   (f.st==='all'||k.trang_thai===f.st) &&
   (f.game==='all'||(f.game==='legacy'?(k.game||'all')==='all':(k.game||'all')===f.game)) &&
   (f.by==='all'||(f.by==='admin'?!String(k.by||'').startsWith('ctv:'):String(k.by||'').startsWith('ctv:'))) &&
   (!q||[k.key,k.ten,k.don_hang,k.goi,k.ghi_chu,k.by].join(' ').toLowerCase().indexOf(q)>=0));
 if(f.sort==='old')L=L.slice().reverse();
 if(f.sort==='calls')L=L.slice().sort((a,b)=>(num(b.luot_goi_hu)+num(b.luot_goi_md5)+num(b.luot_goi_sunwin))-(num(a.luot_goi_hu)+num(a.luot_goi_md5)+num(a.luot_goi_sunwin)));
 return L;
}
async function vKeys(force){
 if(force||!DB.keys.length||Date.now()-DB.keysAt>60000){const j=await api('/admin/api/keys');DB.keys=(j.keys||[]).filter(k=>k.loai!=='admin');DB.keysAt=Date.now();}
 const L=keyFilter();DB.kv=L;
 const vis=L.slice(0,DB.page);const f=DB.kf;
 const seg=(act,cur,items)=>'<div class="seg">'+items.map(x=>'<button class="'+(cur===x[0]?'on':'')+'" data-act="'+act+'" data-arg="'+x[0]+'">'+x[1]+'</button>').join('')+'</div>';
 $('v').innerHTML=
 '<div class="card tight">'
 +'<input id="ks" placeholder="Tìm key, tên khách, đơn, CTV…" value="'+esc(f.q)+'" oninput="kfq(this.value)">'
 +'<div class="fgroup"><span class="flabel">Trạng thái</span>'+seg('kSt',f.st,[['all','Tất cả'],['hoạt động','Hoạt động'],['chưa kích hoạt','Chưa kích hoạt'],['hết hạn','Hết hạn'],['khóa','Khóa']])+'</div>'
 +'<div class="fgroup"><span class="flabel">Nguồn</span>'+seg('kBy',f.by,[['all','Mọi nguồn'],['admin','Admin'],['ctv','CTV']])+'</div>'
 +'<div class="fgroup"><span class="flabel">Loại key</span>'+seg('kGame',f.game,[['all','Mọi loại'],['lc79','LC79 · 2 bàn'],['sunwin','Sunwin · 1 bàn'],['legacy','Key cũ (all)']])+'</div>'
 +'<div class="fgroup"><span class="flabel">Sắp xếp</span>'+seg('kSort',f.sort,[['new','Mới nhất'],['old','Cũ nhất'],['calls','Gọi nhiều']])
   +'<span class="sp"></span><a class="btn sm" href="/admin/api/export.csv">'+ic('download','sm')+' CSV</a><span class="muted">'+L.length+' key khớp bộ lọc</span></div></div>'
 +'<div id="bk"></div><div id="klist"></div>';
 renderKeyList(vis,L);
}
function renderKeyList(vis,L){
 const bk=$('bk'),kl=$('klist');if(!bk||!kl)return;
 bk.innerHTML=DB.sel.size
  ?'<div class="bulkbar"><b>'+DB.sel.size+' đã chọn</b><button class="btn sm" data-act="bulkCopy">'+ic('copy','sm')+' Copy</button>'
   +'<button class="btn sm bad" data-act="bulk" data-arg="ban">'+ic('lock','sm')+' Khoá</button>'
   +'<button class="btn sm ok" data-act="bulk" data-arg="active">'+ic('unlock','sm')+' Mở</button>'
   +'<button class="btn sm bad" data-act="bulk" data-arg="delete">'+ic('trash','sm')+' Xoá</button>'
   +'<button class="btn sm" data-act="bulkClear">Bỏ chọn</button></div>'
  :(L.length?'<div style="margin-bottom:8px"><button class="btn sm" data-act="selAll">Chọn tất cả '+L.length+' key đang lọc</button></div>':'');
 kl.innerHTML=vis.map(k=>{
  const i=DB.kv.indexOf(k);
  return '<div class="li"><input type="checkbox" class="ck" '+(DB.sel.has(k.id)?'checked':'')+' data-act="sel" data-arg="'+i+'">'
  +'<div class="li-main"><div class="li-top"><span class="k">'+esc(k.key)+'</span>'
  +'<span class="tag '+pill(k.trang_thai)+'">'+esc(k.trang_thai)+'</span><span class="tag '+kcls(k.game)+'">'+esc(KSHORT[k.game]||k.game)+'</span>'
  +(String(k.by||'').startsWith('ctv:')?'<span class="tag idle">CTV '+esc(String(k.by).slice(4))+'</span>':'')+'</div>'
  +'<div class="li-meta"><span>'+esc(k.ten||'Khách lẻ')+'</span><span>'+esc(k.goi||'—')+' · '+esc(k.thoi_han)+'</span><span>'+esc(k.gia||'')+'</span></div>'
  +'<div class="li-meta"><span>Hạn: <b>'+(k.da_kich_hoat?(dfmt(k.ngay_het_han)==='—'?'Vĩnh viễn':dfmt(k.ngay_het_han)):'chưa kích hoạt')+'</b></span>'
  +'<span>Gọi: <b>'+num(k.luot_goi_hu)+'</b> Hũ · <b>'+num(k.luot_goi_md5)+'</b> MD5 · <b>'+num(k.luot_goi_sunwin)+'</b> SW</span>'
  +'<span>'+num((k.thiet_bi||[]).length)+' thiết bị</span></div></div>'
  +'<div class="btns"><button class="btn sm pri" data-act="kMsg" data-arg="'+i+'">'+ic('msg','sm')+' Tin nhắn</button>'
  +'<button class="btn sm" data-act="kEdit" data-arg="'+i+'">'+ic('edit','sm')+'</button>'
  +(k.trang_thai==='khóa'
    ?'<button class="btn sm ok" data-act="kAct" data-arg="'+i+':active">'+ic('unlock','sm')+'</button>'
    :'<button class="btn sm bad" data-act="kAct" data-arg="'+i+':banned">'+ic('lock','sm')+'</button>')+'</div></div>';
 }).join('')||'<div class="card muted" style="text-align:center">Không có key nào khớp bộ lọc</div>';
 if(L.length>vis.length){const b=document.createElement('button');b.className='btn big';b.style.marginTop='6px';b.textContent='Xem thêm '+(L.length-vis.length)+' key';
  b.onclick=()=>{DB.page+=40;DB.kv=L;renderKeyList(L.slice(0,DB.page),L);};kl.appendChild(b);}
}

/* ─────────── 9. ĐƠN HÀNG ─────────── */
async function vOrders(){
 const j=await api('/admin/api/orders');DB.orders=j.don_hang||[];
 const stat=(k,v,cls)=>'<div class="kpi '+(cls||'')+'"><div class="kl">'+k+'</div><b>'+v+'</b></div>';
 $('v').innerHTML='<div class="kgrid">'
 +stat(ic('receipt','xs')+'Tổng đơn',DB.orders.length)
 +stat(ic('check','xs')+'Đã giao',DB.orders.filter(o=>o.trang_thai==='đã giao').length,'ok')
 +stat(ic('clock','xs')+'Đơn mới',DB.orders.filter(o=>o.trang_thai!=='đã giao').length,'wn')
 +stat(ic('wallet','xs')+'Giá trị ước',XM(DB.orders.reduce((s,o)=>s+num(_moneyK(o.price)),0)))
 +'</div>'
 +(DB.orders.length?DB.orders.map((o,i)=>{
  const keys=(o.keys||[]);
  return '<div class="li"><div class="li-main"><div class="li-top"><span class="k">'+esc(o.id)+'</span>'
  +'<span class="tag '+(o.trang_thai==='đã giao'?'act':'idle')+'">'+esc(o.trang_thai)+'</span>'
  +(String(o.by||'').startsWith('ctv:')?'<span class="tag idle">CTV '+esc(String(o.by).slice(4))+'</span>':'')
  +'<span class="muted" style="margin-left:auto">'+dfmt(o.ngay_tao)+'</span></div>'
  +'<div class="li-meta"><span><b>'+esc(o.khach)+'</b></span><span>'+esc(o.package)+'</span><span>'+esc(o.price||'')+'</span><span>'+keys.length+' key</span>'
  +'<span>'+esc(o.thoi_han||'')+'</span>'+(o.bill?'<span>Bill '+(o.bill_ok?'<b style="color:var(--ok)">OK</b>':'<b style="color:var(--warn)">chưa duyệt</b>')+': '+esc(String(o.bill).slice(0,26))+'</span>':'')+'</div>'
  +'<div class="li-meta" style="flex-direction:column;align-items:flex-start;gap:3px">'+keys.map(k=>'<span class="mono">'+esc(k)+' · '+(o.trang_thai_thuc||{})[k]+'</span>').join('')+'</div></div>'
  +'<div class="btns">'
  +(o.trang_thai!=='đã giao'?'<button class="btn sm ok" data-act="ordAct" data-arg="'+i+':status">'+ic('check','sm')+' Đã giao</button>':'')
  +(String(o.by||'').startsWith('ctv:')&&o.bill&&!o.bill_ok?'<button class="btn sm pri" data-act="ordAct" data-arg="'+i+':bill">'+ic('check','sm')+' Duyệt bill</button>':'')
  +'<button class="btn sm" data-act="ordCopy" data-arg="'+i+'">'+ic('copy','sm')+' Key</button>'
  +'<button class="btn sm bad" data-act="ordAct" data-arg="'+i+':delete">'+ic('trash','sm')+'</button></div></div>';
 }).join(''):'<div class="card muted" style="text-align:center">Chưa có đơn hàng</div>');
}
function _moneyK(s){return num(String(s||'').toLowerCase().replace('k','').replace(/[.,]/g,''));}

/* ─────────── 10. KHÁCH HÀNG ─────────── */
async function vCustomers(){
 const j=await api('/admin/api/customers');DB.cust=j.khach||[];
 const f=DB.kfq,q=(f.q||'').toLowerCase().trim();
 const own=['all'].concat(j.chu||[]);
 const tags=['all','VIP','sắp hết hạn','ngủ đông','cần chăm sóc','khách quay lại'];
 const L=DB.cust.filter(c=>(f.by==='all'||c.owner===f.by)&&(f.tag==='all'||(c.nhan||[]).indexOf(f.tag)>=0)
  &&(!q||(c.khach+' '+c.owner+' '+(c.keys||[]).map(k=>k.key).join(' ')+' '+(c.thiet_bi||[]).map(d=>d.mo_ta).join(' ')).toLowerCase().indexOf(q)>=0));
 DB.custv=L;
 $('v').innerHTML='<div class="card tight"><input id="khq" placeholder="Tìm tên khách, key, thiết bị, CTV…" value="'+esc(f.q)+'" oninput="khq(this.value)">'
 +'<div class="fgroup"><span class="flabel">Người bán</span><div class="pills">'+own.map(o=>'<button class="pill '+(f.by===o?'on':'')+'" data-act="khBy" data-arg="'+esc(o)+'">'+(o==='all'?'Tất cả':esc(XOWN(o)))+'</button>').join('')+'</div></div>'
 +'<div class="fgroup"><span class="flabel">Nhãn</span><div class="pills">'+tags.map(t=>'<button class="pill '+(f.tag===t?'on':'')+'" data-act="khTag" data-arg="'+esc(t)+'">'+(t==='all'?'Mọi nhãn':esc(t))+'</button>').join('')+'</div>'
 +'<span class="sp"></span><span class="muted">'+L.length+' khách</span></div></div>'
 +(L.map((c,i)=>'<div class="li click" data-act="khOpen" data-arg="'+i+'">'
   +'<div class="li-main"><div class="li-top"><b style="font-size:14px">'+esc(c.khach)+'</b>'
   +'<span class="tag '+pill(c.trang_thai)+'">'+esc(c.trang_thai)+'</span>'+(c.nhan||[]).map(t=>'<span class="tag bl">'+esc(t)+'</span>').join('')
   +'<span class="muted" style="margin-left:auto">'+esc(XOWN(c.owner))+'</span></div>'
   +'<div class="li-meta"><span>Key <b>'+num(c.so_key)+'</b> (chạy '+num(c.dang_chay)+')</span><span>Chi <b>'+XM(c.chi_tieu_k)+'</b></span>'
   +'<span>Thiết bị <b>'+num((c.thiet_bi||[]).length)+'</b></span><span>Gọi <b>'+num(c.luot_goi)+'</b></span><span>Gần nhất <b>'+ago(c.hoat_dong_cuoi)+'</b></span></div></div>'
   +ic('next','sm')+'</div>').join('')||'<div class="card muted" style="text-align:center">Không có khách phù hợp</div>');
}
async function openCustomer(i){
 const c=DB.custv[i];if(!c)return;
 let ev=[];try{const r=await api('/admin/api/keylog?limit=60&by='+encodeURIComponent(c.owner)+'&q='+encodeURIComponent(c.khach));ev=r.su_kien||[];}catch(e){}
 modal('<div class="mh"><h2>'+esc(c.khach)+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
 +'<p class="muted">'+esc(XOWN(c.owner))+' · khách từ '+dfmt(c.lan_dau)+' · hoạt động '+ago(c.hoat_dong_cuoi)+'</p>'
 +'<div class="kgrid" style="margin-top:10px"><div class="kpi"><b>'+num(c.so_key)+'</b><small>Key</small></div>'
 +'<div class="kpi ok"><b>'+XM(c.chi_tieu_k)+'</b><small>Đã chi</small></div><div class="kpi bl"><b>'+num(c.luot_goi)+'</b><small>Lượt gọi API</small></div></div>'
 +'<div class="grp" style="padding-left:0">THIẾT BỊ ('+(c.thiet_bi||[]).length+')</div>'
 +((c.thiet_bi||[]).map(d=>'<div class="li"><div class="li-main"><div class="li-top"><b>'+esc(d.ten)+'</b> <span class="muted mono">'+esc(d.key)+'</span></div>'
   +'<div class="li-meta"><span>Kích hoạt '+dfmt(d.kich_hoat)+'</span><span>Gọi cuối '+ago(d.lan_cuoi_goi)+'</span><span>'+num(d.luot_goi)+' lượt</span></div>'
   +(d.mo_ta?'<div class="muted" style="word-break:break-all;font-size:11px;margin-top:3px">'+esc(d.mo_ta)+'</div>':'')+'</div></div>').join('')||'<p class="muted">Chưa kích hoạt thiết bị nào</p>')
 +'<div class="grp" style="padding-left:0">KEY ('+(c.keys||[]).length+')</div>'
 +((c.keys||[]).map(k=>'<div class="li"><div class="li-main"><div class="li-top"><span class="k">'+esc(k.key)+'</span>'
   +'<span class="tag '+pill(k.trang_thai)+'">'+esc(k.trang_thai)+'</span><span class="tag '+kcls(k.game)+'">'+esc(KSHORT[k.game]||k.game)+'</span></div>'
   +'<div class="li-meta"><span>'+esc(k.goi||'')+' · '+esc(k.gia||'')+'</span><span>Tạo '+dfmt(k.ngay_tao)+'</span>'
   +'<span>Hạn '+(k.ngay_het_han?dfmt(k.ngay_het_han):esc(k.thoi_han||'—'))+'</span>'
   +'<span>Hũ '+num(k.luot_goi_hu)+' · MD5 '+num(k.luot_goi_md5)+' · SW '+num(k.luot_goi_sunwin)+'</span></div></div>'
   +'<button class="btn sm" data-act="copyraw" data-arg="'+esc(k.key)+'">'+ic('copy','sm')+'</button></div>').join(''))
 +'<div class="grp" style="padding-left:0">LỊCH SỬ</div>'
 +(ev.map(e=>'<div class="evr"><div class="ei">'+evIc(e.loai)+'</div><div class="sp" style="min-width:0"><div class="b">'+esc(e.mo_ta)+'</div>'
   +'<div class="muted">'+esc(e.key||'')+(e.goi?' · '+esc(e.goi):'')+'</div></div><span class="muted nowrap">'+ago(e.at)+'</span></div>').join('')||'<p class="muted">Chưa có</p>'),true);
}

/* ─────────── 11. LỊCH SỬ KEY ─────────── */
async function vLog(){
 const f=DB.lk;
 const u='/admin/api/keylog?limit=400'+(f.by!=='all'?'&by='+encodeURIComponent(f.by):'')+(f.loai!=='all'?'&loai='+f.loai:'')+(f.q?'&q='+encodeURIComponent(f.q):'');
 const j=await api(u);
 const LO=[['all','Tất cả'],['tao_key','Tạo key'],['kich_hoat','Kích hoạt'],['goi_api','Gọi API'],['het_han','Hết hạn'],['ctv','Hành động CTV']];
 $('v').innerHTML='<div class="grid g2"><div class="card"><div class="card-h"><h2 class="sp">Tạo / kích hoạt · 14 ngày</h2></div>'
 +bars((j.theo_ngay||[]).map(x=>[x[0],x[1]]))+'<p class="muted" style="margin-top:6px">Kích hoạt: '+((j.theo_ngay||[]).reduce((s,x)=>s+num(x[2]),0))+' trong 14 ngày</p></div>'
 +'<div class="card"><div class="card-h"><h2 class="sp">Giờ tạo key</h2></div>'+(j.theo_gio?heat(j.theo_gio):'<p class="muted">—</p>')+'</div></div>'
 +'<div class="card tight"><input id="lkq" placeholder="Tìm khách, key, CTV…" value="'+esc(f.q)+'" oninput="lkq(this.value)">'
 +'<div class="fgroup"><span class="flabel">Người bán</span><div class="pills">'+['all'].concat(j.chu||[]).map(o=>'<button class="pill '+(f.by===o?'on':'')+'" data-act="lkBy" data-arg="'+esc(o)+'">'+(o==='all'?'Mọi người bán':esc(XOWN(o)))+'</button>').join('')+'</div></div>'
 +'<div class="fgroup"><span class="flabel">Loại</span><div class="pills">'+LO.map(x=>'<button class="pill '+(f.loai===x[0]?'on':'')+'" data-act="lkLoai" data-arg="'+x[0]+'">'+x[1]+'</button>').join('')+'</div></div></div>'
 +'<div class="card"><div class="card-h"><h2 class="sp">Sự kiện</h2><span class="muted">'+num(j.tong)+'</span></div>'
 +((j.su_kien||[]).map(e=>'<div class="evr"><div class="ei">'+evIc(e.loai)+'</div><div class="sp" style="min-width:0"><div class="b">'+esc(e.mo_ta)+'</div>'
   +'<div class="muted">'+(e.khach?'<b>'+esc(e.khach)+'</b> · ':'')+esc(XOWN(e.by))+(e.key?' · <span class="mono">'+esc(e.key)+'</span>':'')+(e.goi?' · '+esc(e.goi)+' '+esc(e.gia||''):'')+'</div></div>'
   +'<span class="muted nowrap">'+ago(e.at)+'</span></div>').join('')||'<p class="muted">Chưa có sự kiện</p>')+'</div>';
}

/* ─────────── 12. BÀN CƯỢC ─────────── */
function ckCard(c){
 if(!c)return '';
 if(!c.da_du_du_lieu)return '<div class="card"><div class="card-h"><span class="hi">'+ic('spark','sm')+'</span><h2>Nhịp cầu</h2></div><p class="muted">'+esc(c.ghi_chu||'')+'</p></div>';
 const b=c.backtest||{},bt=b.ty_le,cur=num(c.run_hien_tai);
 const runs=(c.cau_run&&c.cau_run!=='')?String(c.cau_run).split('-'):[];
 return '<div class="card"><div class="card-h"><span class="hi">'+ic('spark','sm')+'</span><h2 class="sp">Nhịp cầu · đọc run</h2>'
 +'<span class="tag '+(c.trang_thai==='TÁC ĐỘNG'?'act':'idle')+'">'+(c.trang_thai==='TÁC ĐỘNG'?'TÁC ĐỘNG':'CHỜ')+'</span><span class="muted">'+num(c.so_phien)+' phiên</span></div>'
 +'<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:8px 0">'
 +'<span class="tag '+(c.du_doan==='TAI'?'tai':c.du_doan==='XIU'?'xiu':'')+' lg">'+(c.du_doan?SIDE(c.du_doan)+' · '+Math.round(num(c.do_tin_cay)*100)+'%':'KHÔNG CHƠI — CHỜ')+'</span>'
 +'<span class="tag idle">nhịp '+esc(c.nhip||'?')+'</span><span class="tag idle">run '+cur+'</span>'
 +'<div style="flex:1;min-width:150px"><div class="pgb"><i style="width:'+Math.round(num(c.do_thuan)*100)+'%'+(num(c.do_thuan)>=0.7?';background:var(--ok)':'')+'"></i></div>'
 +'<small class="muted">độ thuần '+Math.round(num(c.do_thuan)*100)+'% (chín ≥ 70%)</small></div></div>'
 +'<p style="font-size:13px">'+esc(c.ket_luan)+'</p>'
 +'<div class="grp" style="padding-left:0">THANG RUN GẦN NHẤT</div>'
 +(runs.length?'<div class="pills">'+runs.map((x,i)=>'<span class="pill '+(i===runs.length-1?'on':'')+'">'+esc(x)+'</span>').join('')+'</div>':'<p class="muted">—</p>')
 +((c.tin_hieu||[]).length?'<div class="grp" style="padding-left:0">TÍN HIỆU ĐANG TỒN</div><div class="pills">'
   +c.tin_hieu.map(t=>'<span class="pill '+(t.huong==='TỪ CHỐI'?'':'on')+'">'+esc(t.nguon)+' → '+(t.huong==='TỪ CHỐI'?'bị loại':SIDE(t.huong))+' ('+esc(t.trong_so)+')</span>').join('')+'</div>':'')
 +'<div class="grp" style="padding-left:0">TỰ CHẤM · '+(b.so_phien_thu||0)+' phiên gần nhất</div>'
 +'<p>Ra tín hiệu <b>'+num(b.so_lan_ra_tin_hieu)+'</b> lần · đúng <b>'+num(b.dung)+'</b>'
 +(bt!==null&&bt!==undefined?' · <b style="color:var(--'+(bt>=55?'ok':bt<50?'bad':'warn')+')">'+bt+'%</b>':'')
 +(bt!==null&&bt<50?' · <span class="tag ban">luật tự khoá: không phát tin</span>':(bt!==null&&bt>=55?' · <span class="tag act">luật đang ăn</span>':''))+'</p>'
 +'<div class="grp" style="padding-left:0">SÓNG TỶ LỆ TÀI (mỗi 10 phiên)</div><div class="pills">'
 +((c.song_ty_le_tai||[]).map(v=>'<span class="pill '+(v>=0.6?'on':'')+'">'+Math.round(v*100)+'%</span>').join(''))+'</div>'
 +'<p class="muted" style="margin-top:10px;font-size:12px">'+esc(c.luu_y||'')+'</p></div>';
}
async function vBan(code){
 const draw=async()=>{
  const j=await api('/admin/api/history/'+code+'?limit=40');
  const li=j.lich_su||[],st=j.thong_ke||{},hh=j.phien_hien_tai||{};
  const nm={hu:'BÀN HŨ',md5:'BÀN MD5',sunwin:'BÀN SUNWIN'}[code]||code;
  const note=code==='sunwin'?'Key Sunwin riêng — 1 key 1 bàn':'Key LC79 dùng chung 2 bàn Hũ + MD5';
  $('v').innerHTML='<div class="kgrid">'
  +'<div class="kpi ok"><div class="kl">'+ic('check','xs')+'WIN · Thắng</div><b style="color:var(--ok)">'+num(st.win)+'</b></div>'
  +'<div class="kpi bd"><div class="kl">'+ic('close','xs')+'LOSE · Thua</div><b style="color:var(--bad)">'+num(st.lose)+'</b></div>'
  +'<div class="kpi bl"><div class="kl">'+ic('chart','xs')+'Tỷ lệ thắng</div><b>'+num(st.ty_le)+'%</b></div>'
  +'<div class="kpi wn"><div class="kl">'+ic('clock','xs')+'Skip (đã cấm)</div><b>'+num(st.skip)+'</b></div></div>'
  +'<div class="card"><div class="card-h"><span class="hi">'+ic(code==='sunwin'?'sw':code==='md5'?'hash':'dice','sm')+'</span><h2 class="sp">'+nm+'</h2><span class="muted">'+note+' · cập nhật '+dfmt(j.cap_nhat)+'</span></div>'
  +'<div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap">'+ring(num(st.ty_le),num(st.ty_le)>=55?'ok':'warn')
  +'<div><div class="muted">Tổng phiên đã chấm</div><b style="font-size:17px">'+(num(st.win)+num(st.lose))+'</b></div>'
  +'<div style="flex:1;min-width:180px"><div class="muted" style="font-size:11px;font-weight:800;letter-spacing:.06em;margin-bottom:4px">CHUỖI GẦN NHẤT</div>'
  +'<div class="dots">'+li.slice(0,40).map(h=>'<i class="'+(h.trang_thai==='win'?'w':h.trang_thai==='lose'?'l':h.trang_thai==='skip'?'s':'')+'" title="#'+esc(h.phien)+'"></i>').join('')+'</div></div></div></div>'
  +'<div class="card"><div class="card-h"><span class="hi">'+ic('bolt','sm')+'</span><h2 class="sp">Dự đoán phiên #'+esc(hh.phien||'—')+'</h2>'
  +'<span class="tag '+(hh.du_doan?'act':'exp')+'">'+(hh.du_doan?'TÁC ĐỘNG':'CHỜ')+'</span></div>'
  +(hh.du_doan?'<div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap"><span class="tag '+(hh.du_doan==='TAI'?'tai':'xiu')+' lg" style="font-size:17px">'+SIDE(hh.du_doan)+' '+num(hh.do_tin_cay)+'%</span>'
    +'<div><div class="muted">Cầu hiện tại</div><span class="mono">'+esc(hh.cau||'—')+'</span></div></div>'
   :'<p style="font-size:16px;font-weight:800;color:var(--tx3)">Đang chờ — chế độ CHỜ đang bật (set biến môi trường NO_SKIP=1 để cấm skip)</p><p class="muted">Hệ thống tự bật lại khi cầu đủ chín (conf ≥ ngưỡng).</p>')
  +'</div>'
  +ckCard(j.chu_ky)
  +((j.phan_tich_cau&&j.phan_tich_cau.khung_da_phien&&j.phan_tich_cau.khung_da_phien.length)
    ?'<div class="card"><div class="card-h"><span class="hi">'+ic('chart','sm')+'</span><h2 class="sp">Tầng khung phiên</h2></div><div class="pills">'
     +j.phan_tich_cau.khung_da_phien.map(r=>'<span class="pill '+(r.p_tai>=0.53?'on':'')+'" title="TÀI '+r.tai+' · XỈU '+r.xiu+' · lệch '+r.lech+'">'+num(r.khung)+'p · '+(r.goc==='đảo'?'đảo':'theo')+' · '+Math.round(r.p_tai*100)+'%</span>').join('')
     +'</div>'+(j.phan_tich_cau.dong_thuan_da_khung?'<p class="muted" style="margin-top:8px">'+esc(j.phan_tich_cau.dong_thuan_da_khung.mo_ta||'')+'</p>':'')+'</div>':'')
  +'<div class="card"><div class="card-h"><h2 class="sp">Bảng phiên</h2><span class="muted">'+li.length+' phiên</span></div><div class="scrollx"><table><thead><tr><th>Phiên</th><th>Dự đoán</th><th>Xúc xắc</th><th>Tổng</th><th>Kết quả</th><th>KẾT QUẢ DỰ ĐOÁN</th></tr></thead><tbody>'
  +li.map(h=>{const st=h.trang_thai;const rc=st==='win'?' class="r-win"':st==='lose'?' class="r-lose"':'';
   const badge=st==='win'?'<span class="tag wl-w">'+ic('check','xs')+' WIN</span>':st==='lose'?'<span class="tag wl-l">'+ic('close','xs')+' LOSE</span>':'<span class="tag">SKIP</span>';
   return '<tr'+rc+'><td class="mono">#'+esc(h.phien)+'</td><td>'+(h.du_doan?'<span class="tag '+(h.du_doan==='TAI'?'tai':'xiu')+'">'+SIDE(h.du_doan)+'</span>':'—')+'</td>'
   +'<td class="mono">'+((h.xuc_xac||[]).join(' · ')||'—')+'</td><td><b>'+(h.tong==null?'—':h.tong)+'</b></td>'
   +'<td>'+(h.ket_qua?'<span class="tag '+(h.ket_qua==='TAI'?'tai':'xiu')+'">'+SIDE(h.ket_qua)+'</span>':'—')+'</td>'
   +'<td>'+badge+'</td></tr>';}).join('')+'</tbody></table></div></div>';
 };
 await draw();
 every(8000,()=>{if(CUR===code&&window.scrollY<120)draw().catch(()=>{});});
 setAuto(true);
}

/* ─────────── 13. CTV ─────────── */
async function vCtv(){
 const j=await api('/admin/api/ctvs');DB.ctvs=j.ctvs||[];
 let pr={cho_duyet:[],lich_su:[]};try{pr=await api('/admin/api/pays');}catch(e){}
 DB.pays=pr.cho_duyet||[];DB.paysHis=pr.lich_su||[];
 drawNav();
 const url=location.origin+'/ctv';
 const act=DB.ctvs.filter(c=>c.trang_thai==='hoạt động').length;
 const debt=DB.ctvs.reduce((s,c)=>s+num(c.no_k),0);
 $('v').innerHTML='<div class="kgrid">'
 +'<div class="kpi"><div class="kl">'+ic('shield','xs')+'Tổng CTV</div><b>'+DB.ctvs.length+'</b><small>'+act+' đang hoạt động</small></div>'
 +'<div class="kpi wn"><div class="kl">'+ic('wallet','xs')+'Công nợ</div><b>'+num(debt)+'K</b><small>chưa thu</small></div>'
 +'<div class="kpi '+(DB.pays.length?'bd':'ok')+'"><div class="kl">'+ic('receipt','xs')+'Chờ duyệt</div><b>'+DB.pays.length+'</b><small>phiếu thanh toán</small></div></div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('link','sm')+'</span><h2 class="sp">Trang đăng nhập CTV</h2>'
 +'<button class="btn sm pri" data-act="copyraw" data-arg="'+esc(url)+'">'+ic('copy','sm')+' Copy link</button>'
 +'<button class="btn sm" data-act="openCtv">'+ic('external','sm')+' Mở trang</button></div>'
 +'<p class="mono" style="word-break:break-all;font-size:12px;margin:0">'+esc(url)+'</p></div>'
 +'<div class="btns" style="margin-bottom:12px"><button class="btn pri" data-act="ctvNew">'+ic('plus','sm')+' Thêm CTV</button>'
 +'<button class="btn" data-act="payHist">'+ic('clock','sm')+' Lịch sử thanh toán</button></div>'
 +(DB.pays.length?'<div class="card" style="border-color:var(--warn)"><div class="card-h"><span class="hi" style="background:var(--warnSoft);color:var(--warn)">'+ic('wallet','sm')+'</span><h2 class="sp">Chờ duyệt thanh toán ('+DB.pays.length+')</h2></div>'
   +'<p class="muted">Kiểm tra tiền đã về tài khoản + bill của CTV rồi mới duyệt.</p>'
   +DB.pays.map((x,i)=>'<div class="li" style="border-color:var(--warn)"><div class="li-main"><div class="li-top">'
     +'<span class="k">'+esc(x.ma)+'</span><span class="tag exp">chờ duyệt</span><b style="margin-left:auto">'+num(x.so_tien_k)+'K</b></div>'
     +'<div class="li-meta"><span>CTV <b>'+esc(x.ctv)+'</b> '+esc(x.ctv_ten||'')+'</span><span>báo lúc '+esc(String(x.bao_luc||'').slice(5,16).replace('T',' '))+'</span></div>'
     +'<div class="li-meta"><span>Nội dung CK: <b class="mono">'+esc(x.noi_dung)+'</b></span>'+(x.bill?'<span>Bill: '+esc(String(x.bill).slice(0,24))+'</span>':'')+(x.ghi_chu?'<span>'+esc(x.ghi_chu)+'</span>':'')+'</div></div>'
     +'<div class="btns"><button class="btn sm ok" data-act="payApprove" data-arg="'+i+'">'+ic('check','sm')+' Duyệt</button>'
     +'<button class="btn sm bad" data-act="payReject" data-arg="'+i+'">'+ic('close','sm')+' Từ chối</button>'
     +'<button class="btn sm" data-act="copyraw" data-arg="'+esc(x.noi_dung)+'">'+ic('copy','sm')+'</button></div></div>').join('')+'</div>':'')
 +(DB.ctvs.length?DB.ctvs.map((c,i)=>'<div class="li"><div class="li-main"><div class="li-top">'
   +'<span class="k">'+esc(c.username)+'</span><span class="tag '+(c.trang_thai==='hoạt động'?'act':'ban')+'">'+esc(c.trang_thai)+'</span>'
   +(c.thu_hoi?'<span class="tag ban">THU HỒI KEY</span>':'')+(c.cho_duyet?'<span class="tag exp">chờ duyệt TT</span>':'')
   +'<b style="margin-left:auto">'+esc(c.ten||'')+'</b></div>'
   +'<div class="li-meta"><span>Key <b>'+num(c.so_key)+'</b></span><span>Đơn <b>'+num(c.don_hang)+'</b></span><span>Đang chạy <b>'+num(c.dang_hoat_dong)+'</b></span><span>Đã kích hoạt <b>'+num(c.da_kich_hoat)+'</b></span></div>'
   +'<div class="li-meta"><span>Gói bán: <b>'+((c.goi_duoc_cap||[]).length?esc(c.goi_duoc_cap.join(', ')):'tất cả')+'</b></span>'
   +'<span>Hạn mức: <b>'+(num(c.cap_key_ngay)||'∞')+'</b>/ngày</span><span>Hoa hồng <b>'+num(c.hoa_hong)+'%</b></span><span>Doanh thu ~ <b>'+XM(c.doanh_thu_gan_key)+'</b></span></div>'
   +'<div class="li-meta"><span>Nợ <b style="color:var(--'+(num(c.no_k)?'warn':'ok')+')">'+num(c.no_k)+'K</b>'+(num(c.qua_han_k)?' <span class="tag ban">QUÁ HẠN '+num(c.qua_han_k)+'K</span>':'')+'</span>'
   +'<span>Hạn mức nợ <b>'+num(c.han_muc_k)+'K</b></span><span>Đơn chưa bill <b style="color:var(--'+(num(c.don_chua_bill)?'bad':'tx2')+')">'+num(c.don_chua_bill)+'</b></span></div></div>'
   +'<div class="btns"><button class="btn sm ok" data-act="ctvCollect" data-arg="'+i+'">'+ic('wallet','sm')+' Thu tiền</button>'
   +'<button class="btn sm" data-act="ctvLogin" data-arg="'+i+'">'+ic('key','sm')+' Gửi login</button>'
   +'<button class="btn sm pri" data-act="ctvDetail" data-arg="'+i+'">'+ic('eye','sm')+' Chi tiết</button>'
   +(c.trang_thai==='hoạt động'
     ?'<button class="btn sm bad" data-act="ctvLock" data-arg="'+i+':locked">'+ic('lock','sm')+'</button>'
     :'<button class="btn sm ok" data-act="ctvLock" data-arg="'+i+':active">'+ic('unlock','sm')+'</button>')
   +'<button class="btn sm bad" data-act="ctvDel" data-arg="'+i+'">'+ic('trash','sm')+'</button></div></div>').join('')
  :'<div class="card muted" style="text-align:center">Chưa có CTV nào</div>');
}
function ctvForm(u){
 const c=(DB.ctvs||[]).find(x=>x.username===u)||{};
 const perms=Object.assign({create_key:1,lock_key:0,extend_key:0,custom_price:0,see_calls:0},c.quyen||{});
 const PERMS=[['create_key','Tạo key'],['lock_key','Khoá / mở key'],['extend_key','Cộng hạn'],['custom_price','Tự nhập giá'],['see_calls','Xem lượt gọi']];
 const apps=c.goi_duoc_cap||[];
 modal('<div class="mh"><h2>'+(u?'Sửa CTV · '+esc(u):'Thêm CTV mới')+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
 +(u?'':'<div class="row"><div><label>Username</label><input id="c_u" placeholder="vd: ctvminh"></div><div><label>Mật khẩu</label><input id="c_pw" placeholder="tối thiểu 4 ký tự"></div></div>')
 +'<div class="row"><div><label>Tên hiển thị</label><input id="c_name" value="'+esc(c.ten||'')+'" placeholder="vd: Minh Store"></div>'
 +(u?'<div><label>Đổi mật khẩu (trống = giữ)</label><input id="c_pw" placeholder="••••"></div>':'<div><label>Tiền tố key</label><input id="c_pre" maxlength="6" value="'+esc(c.prefix||'')+'" placeholder="VD: CTV1"></div>')+'</div>'
 +'<div class="row"><div><label>Hạn mức key/ngày (0 = ∞)</label><input id="c_max" type="number" min="0" value="'+num(c.cap_key_ngay)+'"></div>'
 +'<div><label>Hoa hồng %</label><input id="c_comm" type="number" min="0" max="100" value="'+num(c.hoa_hong)+'"></div></div>'
 +'<div class="row"><div><label>Hạn mức nợ (K)</label><input id="c_lim" type="number" min="0" value="'+num(c.han_muc_k||500)+'"></div>'
 +(u?'<div><label>Tiền tố key</label><input id="c_pre2" maxlength="6" value="'+esc(c.prefix||'')+'"></div>':'<div></div>')+'</div>'
 +'<label>Quyền</label><div class="pills">'+PERMS.map(p=>'<label class="pill" style="display:flex;gap:5px;align-items:center;text-transform:none;letter-spacing:0;margin:0;color:var(--tx2);font-size:11.5px"><input type="checkbox" class="ck" id="p_'+p[0]+'" '+(perms[p[0]]?'checked':'')+' style="width:auto;accent-color:var(--acc)"> '+p[1]+'</label>').join('')+'</div>'
 +'<label>Gói được bán (trống = tất cả)</label><div class="pills">'+DB.pkgs.map(p=>'<label class="pill" style="display:flex;gap:5px;align-items:center;text-transform:none;letter-spacing:0;margin:0;color:var(--tx2);font-size:11.5px"><input type="checkbox" class="ck pkapp" value="'+esc(p.id)+'" '+(apps.indexOf(p.id)>=0?'checked':'')+' style="width:auto;accent-color:var(--acc)"> '+esc(p.name)+' · '+esc(p.price||'?')+'</label>').join('')+'</div>'
 +'<label>Ghi chú nội bộ</label><input id="c_note" value="'+esc(c.ghi_chu||'')+'">'
 +'<button class="btn pri big" style="margin-top:13px" data-act="ctvSave" data-arg="'+esc(u||'')+'">'+ic('save','sm')+' Lưu</button>',true);
}
function ctvLoginMsg(u,pw){
 return 'TÀI KHOẢN CỘNG TÁC VIÊN\n\nTrang đăng nhập: '+location.origin+'/ctv\nTên đăng nhập: '+u+'\nMật khẩu: '+(pw||'(mật khẩu của bạn)')
 +'\n\nVào tab "Tạo key" → chọn gói → nhập TÊN KHÁCH → tạo key.'
 +'\nCuối ngày thanh toán công nợ trong tab "Thanh toán" (QR có sẵn số tiền + nội dung).'
 +'\nQuá giờ chốt mà còn nợ chưa báo thanh toán, key sẽ bị thu hồi tự động.';
}
async function ctvDetail(u){
 const j=await api('/admin/api/ctvs/'+encodeURIComponent(u));
 DB.xd={u:u,j:j,tab:'ov'};drawCtvDetail(true);
}
function drawCtvDetail(first){
 const j=DB.xd.j||{},c=j.ctv||{},cn=j.cong_no||{};
 const T=[['ov','Tổng quan'],['kh','Khách ('+((j.khach_hang||[]).length)+')'],['ls','Lịch sử key'],['ks','Key ('+((j.keys||[]).length)+')'],['no','Công nợ'],['nk','Nhật ký']];
 const tg=j.key_theo_ngay||[],loi=num(c.doanh_thu_gan_key)-num(cn.tong_nhap_k);
 let body='';
 if(DB.xd.tab==='ov'){
  body='<div class="kgrid"><div class="kpi"><b>'+num(c.so_key)+'</b><small>Tổng key</small></div>'
  +'<div class="kpi"><b>'+num(c.da_kich_hoat)+'</b><small>Đã kích hoạt ('+(num(c.so_key)?Math.round(num(c.da_kich_hoat)/num(c.so_key)*100):0)+'%)</small></div>'
  +'<div class="kpi ok"><b>'+XM(c.doanh_thu_gan_key)+'</b><small>Doanh thu bán</small></div>'
  +'<div class="kpi"><b>'+XM(cn.tong_nhap_k)+'</b><small>Tiền nhập</small></div>'
  +'<div class="kpi '+(loi>=0?'ok':'wn')+'"><b>'+XM(loi)+'</b><small>Lãi gộp ước</small></div>'
  +'<div class="kpi"><b>'+((j.khach_hang||[]).length)+'</b><small>Khách</small></div></div>'
  +'<div class="card"><div class="card-h"><h2>Key tạo theo ngày</h2></div>'+bars(tg.map(x=>[x[0],x[1]]))+'</div>'
  +'<p class="muted">Trạng thái: <b>'+esc(c.trang_thai)+'</b> · tạo '+dfmt(c.ngay_tao)+' · hạn mức nợ '+num(cn.han_muc_k)+'K · hoa hồng '+num(c.hoa_hong)+'%</p>';
 } else if(DB.xd.tab==='kh'){
  body=(j.khach_hang||[]).map(c2=>'<div class="li"><div class="li-main"><div class="li-top"><b>'+esc(c2.khach)+'</b><span class="tag '+pill(c2.trang_thai)+'">'+esc(c2.trang_thai)+'</span></div>'
   +'<div class="li-meta"><span>Key <b>'+num(c2.so_key)+'</b> (chạy '+num(c2.dang_chay)+')</span><span>Chi <b>'+XM(c2.chi_tieu_k)+'</b></span><span>Gọi <b>'+num(c2.luot_goi)+'</b></span><span>'+ago(c2.hoat_dong_cuoi)+'</span></div></div></div>').join('')||'<p class="muted">Chưa có khách</p>';
 } else if(DB.xd.tab==='ls'){
  body=(j.dong_thoi_gian||[]).map(e=>'<div class="evr"><div class="ei">'+evIc(e.loai)+'</div><div class="sp" style="min-width:0"><div class="b">'+esc(e.mo_ta)+'</div>'
   +'<div class="muted">'+(e.khach?esc(e.khach)+' · ':'')+(e.key?'<span class="mono">'+esc(e.key)+'</span>':'')+(e.goi?' · '+esc(e.goi)+' '+esc(e.gia||''):'')+'</div></div>'
   +'<span class="muted nowrap">'+ago(e.at)+'</span></div>').join('')||'<p class="muted">Chưa có</p>';
 } else if(DB.xd.tab==='ks'){
  body=(j.keys||[]).slice(0,100).map(k=>'<div class="li"><div class="li-main"><div class="li-top">'
   +'<span class="k">'+esc(k.key)+'</span><span class="tag '+pill(k.trang_thai)+'">'+esc(k.trang_thai)+'</span><span class="tag '+kcls(k.game)+'">'+esc(KSHORT[k.game]||k.game)+'</span>'
   +'<b style="margin-left:auto">'+esc(k.ten||'')+'</b></div>'
   +'<div class="li-meta"><span>'+esc(k.goi||'')+' · '+esc(k.gia||'')+'</span><span>Tạo '+dfmt(k.ngay_tao)+'</span>'
   +'<span>Hũ '+num(k.luot_goi_hu)+' · MD5 '+num(k.luot_goi_md5)+' · SW '+num(k.luot_goi_sunwin)+'</span></div></div></div>').join('')||'<p class="muted">Chưa có key</p>';
 } else if(DB.xd.tab==='no'){
  body='<div class="pills"><span class="pill '+(num(cn.no_k)?'':'on')+'">Nợ '+num(cn.no_k)+'K</span><span class="pill">Hạn mức '+num(cn.han_muc_k)+'K</span>'
  +'<span class="pill">Đã trả '+num(cn.da_tra_k)+'K / nhập '+num(cn.tong_nhap_k)+'K</span><span class="pill">Chưa bill '+num(cn.don_chua_bill)+'</span></div>'
  +((j.don_no||[]).map(o=>'<div class="evr"><div class="sp"><b>'+esc(o.id)+'</b> · '+esc(o.khach||'')+'</div><span>nợ <b>'+num(o.con_no_k)+'K</b></span><span class="muted">'+(o.bill?'có bill':'chưa bill')+'</span></div>').join(''))
  +'<div class="grp" style="padding-left:0">LỊCH SỬ THU TIỀN</div>'
  +((j.thanh_toan||[]).map(t=>'<div class="evr"><div class="ei">'+ic('wallet','sm')+'</div><div class="sp">thu <b>'+num(t.amount_k)+'K</b> '+esc(t.note||'')+'</div><span class="muted">'+esc(String(t.at).slice(5,16).replace('T',' '))+'</span></div>').join('')||'<p class="muted">Chưa thu lần nào</p>');
 } else {
  body=(j.nhat_ky||[]).map(L=>'<div class="evr"><div class="ei">'+evIc('ctv_'+L.action)+'</div><div class="sp" style="min-width:0"><div class="b">'+esc(L.action)+'</div><div class="muted">'+esc(L.detail||'')+'</div></div><span class="muted nowrap">'+esc(String(L.at||'').slice(5,16).replace('T',' '))+'</span></div>').join('')||'<p class="muted">Chưa có</p>';
 }
 const h='<div class="mh"><h2>CTV · '+esc(c.username)+' — '+esc(c.ten||'')+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
 +'<div class="pills" style="margin:8px 0 12px">'+T.map(t=>'<button class="pill '+(DB.xd.tab===t[0]?'on':'')+'" data-act="xdTab" data-arg="'+t[0]+'">'+t[1]+'</button>').join('')+'</div>'
 +'<div id="xdb">'+body+'</div>';
 if(first)modal(h,true);else{const m=document.querySelector('#mdl .modal');if(m)m.innerHTML=h;}
}
async function ctvCollect(u,debt){
 modal('<div class="mh"><h2>Thu tiền · '+esc(u)+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
 +'<p class="muted">Đang nợ <b>'+num(debt)+'K</b>. Nhập số tiền ĐÃ NHẬN thực tế (K). Hệ thống trừ vào đơn cũ nhất trước.</p>'
 +'<label>Số tiền đã thu (K)</label><input id="cl_amt" type="number" min="1" value="'+(num(debt)||'')+'" inputmode="numeric">'
 +'<label>Ghi chú (mã CK, giờ nhận…)</label><input id="cl_note" placeholder="tuỳ chọn">'
 +'<button class="btn ok big" style="margin-top:12px" data-act="ctvCollectGo" data-arg="'+esc(u)+'">'+ic('check','sm')+' Xác nhận đã thu</button>');
}

/* ─────────── 14. GÓI GIÁ ─────────── */
function vPkgs(){
 $('v').innerHTML='<div class="grid g2">'+DB.pkgs.map((p,i)=>pkgCard(p,i)).join('')+pkgCard({id:'',name:'',price:'',days:30,hours:0,max_devices:1,game:'all'},-1)+'</div>';
}
function pkgCard(p,i){
 const n=i<0,key=n?'new':String(i),g=p.game||'all';
 const cur=(DB.pgame||{})[key]||g;
 return '<div class="card"><div class="card-h"><span class="hi">'+ic('box','sm')+'</span><h2 class="sp">'+(n?'Thêm gói mới':esc(p.name))+'</h2>'+(n?'':'<span class="tag '+kcls(g)+'">'+esc(KSHORT[g]||g)+'</span>')+'</div>'
 +'<div class="row"><div><label>Tên gói</label><input id="pn_'+key+'" value="'+esc(p.name)+'"></div>'
 +'<div><label>Thời hạn · ngày / giờ</label><div class="row"><input id="pd_'+key+'" type="number" min="0" value="'+num(p.days)+'" placeholder="ngày"><input id="ph_'+key+'" type="number" min="0" value="'+num(p.hours)+'" placeholder="giờ"></div></div></div>'
 +'<div class="row"><div><label>Giá bán lẻ</label><input id="pp_'+key+'" value="'+esc(p.price||'')+'" placeholder="VD: 250K"></div>'
 +'<div><label>Giá nhập CTV</label><input id="pw_'+key+'" value="'+esc(p.wholesale||'')+'" placeholder="VD: 22K"></div></div>'
 +'<div class="row"><div><label>Thiết bị tối đa</label><input id="pm_'+key+'" type="number" min="1" value="'+num(p.max_devices||1)+'"></div>'
 +'<div><label>Loại key tạo ra</label><div class="pills" style="padding-top:4px">'+['lc79','sunwin','all'].map(x=>
   '<button class="pill '+(cur===x?'on':'')+'" data-act="pkgGame" data-arg="'+key+':'+x+'">'+esc(KSHORT[x]||x)+'</button>').join('')+'</div></div></div>'
 +'<div class="btns" style="margin-top:12px"><button class="btn pri" style="flex:1" data-act="pkgSave" data-arg="'+key+'">'+ic('save','sm')+' Lưu</button>'
 +(n?'':'<button class="btn bad" data-act="pkgDel" data-arg="'+key+'">'+ic('trash','sm')+'</button>')+'</div></div>';
}

/* ─────────── 15. MẪU TIN NHẮN ─────────── */
function fmtMsg(tpl,o){
 const v={key:o.key,name:o.ten||o.name||'Quý khách',price:o.gia||o.price||'—',
  package:o.goi||o.package||'Tuỳ chỉnh',duration:o.thoi_han||o.duration||'—',
  order:o.don_hang||o.order||'—',
  expiry:o.ngay_het_han?('đến '+String(o.ngay_het_han).slice(0,16).replace('T',' ')):(String(o.thoi_han||'').indexOf('Vĩnh')>=0?'Vĩnh viễn':'tính từ lúc kích hoạt ('+(o.thoi_han||'')+')'),
  tool_url:DB.set.tool_url||'(link tool — admin gửi riêng)',support:DB.set.support||'—',
  activate_url:location.origin+'/makey'};
 return String(tpl||'').replace(/\{(\w+)\}/g,(m,x)=>v[x]!=null?v[x]:m);
}
const DEMO={key:'PAXU-A7K3-M9ZD-2F9T',ten:'Anh Tú',gia:'250K',goi:'Gói 3 Ngày',thoi_han:'3 ngày',don_hang:'DH261122-AB12C'};
function vTpl(){
 const keys=Object.keys(DB.tpls);
 if(!DB.mk.tpl||!DB.tpls[DB.mk.tpl])DB.mk.tpl=keys.find(k=>DB.tpls[k]===DB.set.payment_template)||keys[0];
 const cur=DB.tpls[DB.mk.tpl]||'';
 $('v').innerHTML='<div class="split"><div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('msg','sm')+'</span><h2 class="sp">Chọn mẫu</h2><span class="muted">'+keys.length+' mẫu</span></div>'
 +'<div class="grid g3">'+keys.map(k=>'<button class="opt '+(DB.mk.tpl===k?'on':'')+'" data-act="tplPick" data-arg="'+esc(k)+'"><b>'+esc(DB.tnames[k]||k)+'</b>'
   +'<small style="max-height:52px;overflow:hidden">'+esc(fmtMsg(DB.tpls[k],DEMO).slice(0,70))+'…</small></button>').join('')+'</div></div>'
 +'<div class="card"><div class="card-h"><h2 class="sp">Nội dung</h2><button class="btn sm" data-act="tplReset">'+ic('refresh','sm')+' Khôi phục mẫu gốc</button></div>'
 +'<p class="muted">Bấm biến để chèn vào chỗ con trỏ.</p><div class="pills" style="margin:8px 0">'
 +['key','package','duration','price','name','order','expiry','tool_url','support'].map(x=>'<button class="pill mono" data-act="tplIns" data-arg="'+x+'">{'+x+'}</button>').join('')+'</div>'
 +'<textarea id="tpl_ta" rows="15" oninput="tplPrev()">'+esc(cur)+'</textarea>'
 +'<button class="btn pri big" style="margin-top:12px" data-act="tplSave">'+ic('save','sm')+' Lưu nội dung &amp; dùng mẫu này</button></div></div>'
 +'<div class="card aside-sticky"><div class="card-h"><h2>Xem trước</h2></div><p class="muted">Khách demo · Gói 3 ngày · 250K</p>'
 +'<div class="msg" id="tpl_prev"></div><button class="btn big" style="margin-top:10px" data-act="tplCopy">'+ic('copy','sm')+' Copy bản xem trước</button></div></div>';
 tplPrev();
}
function tplPrev(){const t=$('tpl_ta');if(!t)return;const e=$('tpl_prev');if(e)e.textContent=fmtMsg(t.value,DEMO);}

/* ─────────── 16. CÀI ĐẶT ─────────── */
async function vSet(){
 if(!DB.ov){try{DB.ov=await api('/admin/api/overview');}catch(e){}}
 const a=(DB.ov&&DB.ov.key_admin_console)||{};
 const api1=location.origin+'/api/'+(a.token||'<token>')+'/hu';
 $('v').innerHTML='<div class="split"><div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('gear','sm')+'</span><h2 class="sp">Thông tin gửi khách</h2></div>'
 +'<label>Link tool (gửi kèm tin nhắn)</label><input id="s_tool" value="'+esc(DB.set.tool_url||'')+'" placeholder="https://… link tool">'
 +'<label>Liên hệ hỗ trợ</label><input id="s_sup" value="'+esc(DB.set.support||'')+'" placeholder="VD: @paw_support">'
 +'<label>Tiền tố key mặc định</label><input id="s_pre" maxlength="6" value="'+esc(DB.set.default_prefix||'PAXU')+'">'
 +'<button class="btn pri big" style="margin-top:13px" data-act="setSave">'+ic('save','sm')+' Lưu cài đặt</button></div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('save','sm')+'</span><h2 class="sp">Sao lưu &amp; dữ liệu</h2><span class="tag '+((DB.ov&&DB.ov.gist_backup)?'act':'exp')+'">'+((DB.ov&&DB.ov.gist_backup)?'Gist đang bật':'Gist chưa bật')+'</span></div>'
 +'<p class="muted">Key lưu trong store của server. Nếu chạy Render free (không ổ đĩa), nên bật Gist để redeploy không mất key.</p>'
 +'<div class="btns"><a class="btn sm" href="/admin/api/export.csv">'+ic('download','sm')+' Xuất CSV</a>'
 +'<button class="btn sm" data-act="reload">'+ic('refresh','sm')+' Tải lại dữ liệu</button>'
 +'<button class="btn sm" data-act="theme">'+ic('moon','sm')+' Đổi giao diện</button></div></div></div>'
 +'<div><div class="card"><div class="card-h"><span class="hi">'+ic('key','sm')+'</span><h2 class="sp">Token API quản trị</h2></div>'
 +'<p class="muted">Dùng cho endpoint /api/&lt;token&gt;/… (tool khách gọi). Không chia sẻ công khai.</p>'
 +'<p class="mono" style="word-break:break-all;font-size:12px">'+esc(a.token||'—')+'</p>'
 +'<div class="btns"><button class="btn sm" data-act="copyraw" data-arg="'+esc(a.token||'')+'">'+ic('copy','sm')+' Copy token</button>'
 +'<button class="btn sm" data-act="copyraw" data-arg="'+esc(api1)+'">'+ic('copy','sm')+' Copy URL mẫu</button></div>'
 +'<label style="margin-top:14px">Key admin (dùng để mở tool)</label><p class="mono" style="word-break:break-all;font-size:12px">'+esc(a.key||'—')+'</p>'
 +'<button class="btn sm" data-act="copyraw" data-arg="'+esc(a.key||'')+'">'+ic('copy','sm')+' Copy key admin</button></div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('lock','sm')+'</span><h2 class="sp">Phiên đăng nhập</h2></div>'
 +'<p class="muted">Phiên quản trị giữ 10 giờ. Hết hạn thì đăng nhập lại. Mật khẩu đọc từ biến ADMIN_PASSWORD trên Render.</p>'
 +'<button class="btn bad big" data-act="logout">'+ic('logout','sm')+' Đăng xuất</button></div></div></div>';
}

/* ─────────── 17. HƯỚNG DẪN ─────────── */
function vGuide(){
 const B=location.origin;
 const ep='POST '+B+'/makey   {"key":"PAXU-XXXX-XXXX-XXXX"}\n'
 +'GET  '+B+'/api/<TOKEN>/hu       (LC79 · bàn Hũ)\n'
 +'GET  '+B+'/api/<TOKEN>/md5      (LC79 · bàn MD5) — cùng token với /hu\n'
 +'GET  '+B+'/api/<TOKEN>/sunwin   (Sunwin)\n'
 +'GET  '+B+'/api/<TOKEN>/history/<code>\n'
 +'Header bắt buộc: X-Device-ID';
 $('v').innerHTML='<div class="grid g2" style="align-items:start">'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('book','sm')+'</span><h2>Luồng bán key</h2></div>'
 +'<p class="muted" style="line-height:1.9">1 · Vào <b>Bán key</b> → chọn <b>KEY LC79</b> hoặc <b>KEY SUNWIN</b> → tạo key + copy tin nhắn gửi khách.<br>'
 +'2 · Khách mở tool, dán key vào ô KÍCH HOẠT.<br>'
 +'3 · Tool tự gọi API dự đoán mỗi 4 giây kèm mã thiết bị.</p></div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('key','sm')+'</span><h2>Phân quyền key</h2></div>'
 +'<div class="pills" style="margin:8px 0"><span class="tag idle">KEY LC79</span> mở <b>/hu</b> + <b>/md5</b></div>'
 +'<div class="pills" style="margin:8px 0"><span class="tag sw">KEY SUNWIN</span> chỉ mở <b>/sunwin</b></div>'
 +'<p class="muted">LC79 gọi /sunwin (hoặc ngược lại) → 403 wrong_game. Key loại "all" cũ vẫn mở mọi bàn.</p></div>'
 +'<div class="card" style="grid-column:1/-1"><div class="card-h"><span class="hi">'+ic('bolt','sm')+'</span><h2 class="sp">Endpoint</h2></div>'
 +'<div class="msg mono" style="font-size:11.5px">'+esc(ep)+'</div>'
 +'<div class="btns" style="margin-top:10px"><button class="btn sm" data-act="copyraw" data-arg="'+esc(B)+'">'+ic('copy','sm')+' Copy URL gốc</button>'
 +'<button class="btn sm" data-act="copyraw" data-arg="'+esc(ep)+'">'+ic('copy','sm')+' Copy endpoint</button></div></div></div>';
}

/* ─────────── 18. HÀNH ĐỘNG (dispatch) ─────────── */
function copyText(t,label){
 const done=()=>toast('Đã copy '+(label||''));
 if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(done).catch(()=>fallback(t,done));}
 else fallback(t,done);
}
function fallback(t,done){
 const a=document.createElement('textarea');a.value=t;a.style.cssText='position:fixed;top:0;left:0;opacity:0';
 document.body.appendChild(a);a.select();
 try{document.execCommand('copy');done();}catch(e){toast('Không copy được — copy tay giúp');}
 a.remove();
}
async function withBtn(el,fn){
 if(el){el.disabled=true;el.classList.add('load');}
 try{await fn();}catch(e){toast(String(e&&e.message||'Lỗi'));}
 finally{if(el){el.disabled=false;el.classList.remove('load');}}
}

const ACT={
 close:()=>closeModal(),
 eye:()=>{const p=$('pw');if(p)p.type=p.type==='password'?'text':'password';},
 login:()=>doLogin(),
 logout:()=>{location.href='/admin/logout';},
 theme:()=>toggleTheme(),
 reload:()=>reload(),
 palette:()=>palette(),
 go:(k)=>{if(!k)return;if($('mdl'))closeModal();go(k);},
 'go-close':(k)=>{closeModal();go(k);},
 more:()=>{
  const rest=Object.keys(VIEWS).filter(k=>TABS.indexOf(k)<0);
  modal('<div class="mh"><h2>Đi tới trang</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div><div class="opts">'
   +rest.map(k=>'<button class="opt" data-act="go-close" data-arg="'+k+'"><b>'+ic(VIEWS[k].i,'sm')+' '+esc(VIEWS[k].t)+'</b><small>'+esc(VIEWS[k].g)+'</small></button>').join('')+'</div>');
 },
 alertgo:(g)=>{if(g)go(g);},
 copyraw:(t)=>{if(t)copyText(t);},
 renew:(i)=>{const r=(DB.ins&&DB.ins.gia_han||[])[+i];if(r)copyText(renewMsg(r),'lời nhắn gia hạn');},
 /* bán key */
 mkGame:(g)=>{DB.mk.game=g;DB.mk.pkg='';vCreate();},
 mkPkg:(id)=>{const d=$('o_days'),h=$('o_hours');if(d)DB.mk.days=d.value;if(h)DB.mk.hours=h.value;DB.mk.pkg=id;vCreate();},
 mkQuick:(v)=>{const a=String(v||'').split(':');const d=$('o_days'),h=$('o_hours');if(d)d.value=a[0];if(h)h.value=a[1];
   DB.mk.days=a[0];DB.mk.hours=a[1];toast('Đã điền '+(+a[0]?(a[0]+' ngày '):'')+(+a[1]?(a[1]+' giờ'):''));},
 mkTpl:(k)=>{DB.mk.tpl=k;
   const r=DB.mk.res;if(r)r.msgs=r.keys.map(key=>fmtMsg(DB.tpls[k],{key:key,ten:r.name,gia:r.price,goi:r.goi,thoi_han:r.thoi_han,don_hang:r.order}));
   const el=$('mkres');if(el)el.innerHTML=mkResult();},
 copyMsg:(i)=>{const r=DB.mk.res;if(r&&r.msgs[+i])copyText(r.msgs[+i],'tin nhắn');},
 copyMsgKey:(i)=>{const r=DB.mk.res;if(r&&r.keys[+i])copyText(r.keys[+i],'key');},
 copyAll:()=>{if(DB.mk.res)copyText(DB.mk.msgs.join('\n\n'),'tất cả tin');},
 mkGo:(x,el)=>withBtn(el,async()=>{
  const mk=DB.mk;
  const body={count:+($('o_n').value||1),name:($('o_name').value||'').trim(),price:($('o_price').value||'').trim(),
   prefix:($('o_pre').value||'').trim(),note:($('o_note').value||'').trim(),game:mk.game};
  if(mk.pkg==='_c'){body.days=$('o_days').value;body.hours=$('o_hours').value;if(!num(body.days)&&!num(body.hours))return toast('Nhập số ngày hoặc giờ');}
  else if(mk.pkg==='_p')body.permanent=1;
  else if(mk.pkg)body.package_id=mk.pkg;
  else return toast('Chọn gói thời hạn');
  const j=await post('/admin/api/keys',body);
  if(!j||!j.ok)return toast((j&&j.thong_bao)||'Không tạo được key');
  const pk=DB.pkgs.find(p=>p.id===mk.pkg);
  mk.res={order:j.don_hang,goi:j.goi,thoi_han:j.thoi_han,name:body.name,price:body.price||(pk&&pk.price)||'',
   keys:(j.tin_nhan_thanh_toan||[]).map(x=>x.key),game:mk.game,
   msgs:(j.tin_nhan_thanh_toan||[]).map(x=>fmtMsg(DB.tpls[mk.tpl],{key:x.key,ten:body.name,gia:body.price||(pk&&pk.price)||'',goi:j.goi,thoi_han:j.thoi_han,don_hang:j.don_hang}))};
  DB.keysAt=0;
  toast('Đã tạo '+j.da_tao+' key');
  const el2=$('mkres');if(el2){el2.innerHTML=mkResult();el2.scrollIntoView({behavior:'smooth',block:'start'});}
 }),
 qPrice:(id,el)=>withBtn(el,async()=>{
  const v=($('qp_'+id)||{}).value||'',sync=($('qs_'+id)&&$('qs_'+id).checked)?1:0;
  const j=await post('/admin/api/packages/'+encodeURIComponent(id)+'/price',{price:v,sync_keys:sync});
  toast((j&&j.thong_bao)||'Đã lưu');await loadBase();vCreate();
 }),
 /* key list */
 kSt:(v)=>{DB.kf.st=v;DB.page=40;vKeys();},
 kBy:(v)=>{DB.kf.by=v;DB.page=40;vKeys();},
 kGame:(v)=>{DB.kf.game=v;DB.page=40;vKeys();},
 kSort:(v)=>{DB.kf.sort=v;DB.page=40;vKeys();},
 sel:(i,el)=>{const k=DB.kv[+i];if(!k)return;if(el.checked)DB.sel.add(k.id);else DB.sel.delete(k.id);renderKeyList(DB.kv.slice(0,DB.page),DB.kv);},
 selAll:()=>{DB.kv.forEach(k=>DB.sel.add(k.id));renderKeyList(DB.kv.slice(0,DB.page),DB.kv);},
 bulkClear:()=>{DB.sel.clear();renderKeyList(DB.kv.slice(0,DB.page),DB.kv);},
 bulkCopy:()=>copyText(Array.from(DB.sel).join('\n'),'key'),
 bulk:(a,el)=>withBtn(el,async()=>{
  if(a==='delete'&&!confirm('Xoá hẳn '+DB.sel.size+' key đã chọn?'))return;
  const j=await post('/admin/api/keys-bulk',{ids:Array.from(DB.sel),action:a});
  toast((j&&j.thong_bao)||'Xong');DB.sel.clear();DB.keys=[];DB.keysAt=0;await vKeys(true);
 }),
 kAct:(v,el)=>{const a=String(v||'').split(':');return withBtn(el,async()=>{
  const k=DB.kv[+a[0]];if(!k)return;
  const j=await post('/admin/api/keys/'+encodeURIComponent(k.id),{status:a[1]});
  toast((j&&j.thong_bao)||'Đã cập nhật');DB.keys=[];DB.keysAt=0;await vKeys(true);
 });},
 kEdit:(i)=>{const k=DB.kv[+i];if(!k)return;openKeyEdit(k);},
 kMsg:(i)=>{const k=DB.kv[+i];if(!k)return;openKeyMsg(k);},
 /* đơn hàng */
 ordAct:(v,el)=>{const a=String(v||'').split(':');return withBtn(el,async()=>{
  const o=DB.orders[+a[0]];if(!o)return;
  if(a[1]==='delete'&&!confirm('Xoá đơn '+o.id+' + toàn bộ key của đơn?'))return;
  const body=a[1]==='status'?{status:'đã giao'}:a[1]==='bill'?{bill_ok:1}:{delete:1};
  const j=await post('/admin/api/orders/'+encodeURIComponent(o.id),body);
  toast((j&&j.thong_bao)||'Đã cập nhật');await vOrders();
 });},
 ordCopy:(i)=>{const o=DB.orders[+i];if(o)copyText((o.keys||[]).join('\n'),'key của đơn');},
 /* khách */
 khBy:(v)=>{DB.kfq.by=v;vCustomers();},
 khTag:(v)=>{DB.kfq.tag=v;vCustomers();},
 khOpen:(i)=>openCustomer(+i),
 /* log */
 lkBy:(v)=>{DB.lk.by=v;vLog();},
 lkLoai:(v)=>{DB.lk.loai=v;vLog();},
 /* ctv */
 openCtv:()=>window.open(location.origin+'/ctv','_blank'),
 ctvNew:()=>ctvForm(''),
 ctvDetail:(i)=>{const c=DB.ctvs[+i];if(c)ctvDetail(c.username);},
 xdTab:(t)=>{DB.xd.tab=t;drawCtvDetail(false);},
 ctvCollect:(i)=>{const c=DB.ctvs[+i];if(c)ctvCollect(c.username,c.no_k);},
 ctvCollectGo:(u,el)=>withBtn(el,async()=>{
  const j=await post('/admin/api/ctvs/'+encodeURIComponent(u)+'/collect',{amount_k:($('cl_amt')||{}).value,note:($('cl_note')||{}).value});
  toast((j&&j.thong_bao)||'Đã ghi thu');closeModal();await vCtv();
 }),
 ctvLock:(v,el)=>{const a=String(v||'').split(':');return withBtn(el,async()=>{
  const c=DB.ctvs[+a[0]];if(!c)return;
  const j=await post('/admin/api/ctvs/'+encodeURIComponent(c.username),{status:a[1]});
  toast((j&&j.thong_bao)||'Đã cập nhật');await vCtv();
 });},
 ctvDel:(i)=>withBtn(null,async()=>{
  const c=DB.ctvs[+i];if(!c||!confirm('Xoá CTV '+c.username+'? Key cũ vẫn giữ nguyên.'))return;
  const j=await post('/admin/api/ctvs/'+encodeURIComponent(c.username),{delete:1});
  toast((j&&j.thong_bao)||'Đã xoá');await vCtv();
 }),
 ctvLogin:(i)=>{
  const c=DB.ctvs[+i];if(!c)return;
  modal('<div class="mh"><h2>Gửi login · '+esc(c.username)+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
  +'<p class="muted">Mật khẩu cũ đã mã hoá nên không xem lại được. Đặt mật khẩu mới rồi copy tin gửi CTV.</p>'
  +'<label>Mật khẩu mới</label><input id="xpw" placeholder="tối thiểu 4 ký tự">'
  +'<div class="msg" id="xlm" style="margin-top:12px">'+esc(ctvLoginMsg(c.username,'(mật khẩu)'))+'</div>'
  +'<div class="btns" style="margin-top:11px"><button class="btn pri" style="flex:1" data-act="ctvLoginGo" data-arg="'+esc(c.username)+'">Đặt mật khẩu + Copy</button>'
  +'<button class="btn" data-act="ctvLoginCopy" data-arg="'+esc(c.username)+'">Chỉ copy</button></div>');
 },
 ctvLoginGo:(u,el)=>withBtn(el,async()=>{
  const pw=($('xpw').value||'').trim();
  if(pw.length<4)return toast('Mật khẩu tối thiểu 4 ký tự');
  const j=await post('/admin/api/ctvs/'+encodeURIComponent(u),{password:pw});
  if(!j||!j.ok)return toast((j&&j.thong_bao)||'Lỗi');
  copyText(ctvLoginMsg(u,pw),'tin nhắn login');closeModal();
 }),
 ctvLoginCopy:(u)=>copyText(ctvLoginMsg(u,'(mật khẩu)'),'tin nhắn login'),
 ctvSave:(u,el)=>withBtn(el,async()=>{
  const perms={};
  [['create_key'],['lock_key'],['extend_key'],['custom_price'],['see_calls']].forEach(p=>{const e=$('p_'+p[0]);if(e)perms[p[0]]=e.checked?1:0;});
  const apps=$$('.pkapp').filter(x=>x.checked).map(x=>x.value);
  const pre=(($('c_pre')||{}).value!==undefined)?($('c_pre')||{}).value:(($('c_pre2')||{}).value||'');
  const body={name:($('c_name')||{}).value||'',max_keys_per_day:($('c_max')||{}).value,credit_limit_k:($('c_lim')||{}).value,
   commission_pct:($('c_comm')||{}).value,perms:perms,allowed_packages:apps,
   key_prefix:(pre||'').trim(),note:(($('c_note')||{}).value||'').trim()};
  const pw=(($('c_pw')||{}).value||'').trim();
  let url;
  if(!u){body.username=(($('c_u')||{}).value||'').trim();if(!pw)return toast('Nhập mật khẩu cho CTV mới');body.password=pw;url='/admin/api/ctvs';}
  else{if(pw)body.password=pw;url='/admin/api/ctvs/'+encodeURIComponent(u);}
  const j=await post(url,body);
  if(j&&j.ok){toast(j.thong_bao||'Đã lưu');closeModal();await vCtv();}else toast((j&&j.thong_bao)||'Lỗi');
 }),
 /* thanh toán */
 payApprove:(i)=>{
  const x=DB.pays[+i];if(!x)return;
  modal('<div class="mh"><h2>Duyệt thanh toán · '+esc(x.ctv)+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
  +'<p class="muted">Phiếu yêu cầu <b>'+num(x.so_tien_k)+'K</b>. Chỉ duyệt khi tiền ĐÃ VỀ tài khoản + có bill. Nhập số tiền THỰC NHẬN (K).</p>'
  +'<label>Số tiền thực nhận (K)</label><input id="tt_amt" type="number" min="1" value="'+num(x.so_tien_k)+'">'
  +'<label>Ghi chú</label><input id="tt_note" placeholder="tuỳ chọn (VD: đã nhận 21:45)">'
  +'<button class="btn ok big" style="margin-top:12px" data-act="payGo" data-arg="'+i+':approve">'+ic('check','sm')+' Xác nhận đã nhận tiền</button>');
 },
 payReject:(i)=>{
  const x=DB.pays[+i];if(!x)return;
  modal('<div class="mh"><h2>Từ chối phiếu · '+esc(x.ctv)+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
  +'<p class="muted">Từ chối khi CTV đang quá hạn → hệ thống sẽ thu hồi toàn bộ key của CTV.</p>'
  +'<label>Lý do</label><input id="tt_note" placeholder="VD: chưa thấy tiền về">'
  +'<button class="btn bad big" style="margin-top:12px" data-act="payGo" data-arg="'+i+':reject">Từ chối</button>');
 },
 payGo:(v,el)=>{const a=String(v||'').split(':');return withBtn(el,async()=>{
  const x=DB.pays[+a[0]];if(!x)return;
  const j=await post('/admin/api/pays/'+encodeURIComponent(x.id),{action:a[1],amount_k:($('tt_amt')||{}).value,note:($('tt_note')||{}).value});
  toast((j&&j.thong_bao)||'Đã xử lý');closeModal();await vCtv();
 });},
 payHist:async()=>{
  let L=DB.paysHis;
  if(!L.length){try{const j=await api('/admin/api/pays');L=j.lich_su||[];}catch(e){L=[];}}
  modal('<div class="mh"><h2>Lịch sử thanh toán CTV</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
  +'<div style="max-height:64vh;overflow:auto">'+(L.map(x=>'<div class="li"><div class="li-main"><div class="li-top">'
   +'<span class="k">'+esc(x.ma)+'</span><span class="tag '+(x.trang_thai==='da_duyet'?'act':'ban')+'">'+(x.trang_thai==='da_duyet'?'đã duyệt':'từ chối')+'</span>'
   +'<b style="margin-left:auto">'+num(x.trang_thai==='da_duyet'?x.thuc_nhan_k:x.so_tien_k)+'K</b></div>'
   +'<div class="li-meta"><span>CTV <b>'+esc(x.ctv)+'</b></span><span>'+esc(String(x.duyet_luc||x.tao_luc||'').slice(0,16).replace('T',' '))+'</span>'
   +(x.ghi_chu_admin?'<span>'+esc(x.ghi_chu_admin)+'</span>':'')+'</div></div></div>').join('')||'<p class="muted">Chưa có</p>')+'</div>',true);
 },
 /* gói */
 pkgGame:(v)=>{const a=String(v||'').split(':');DB.pgame[a[0]]=a[1];vPkgs();},
 pkgSave:(k,el)=>withBtn(el,async()=>{
  const g=x=>{const e=$('p'+x+'_'+k);return e?e.value:'';};
  const isNew=k==='new';
  const pid=isNew?'':(DB.pkgs[+k]||{}).id;
  const body={id:pid,name:g('n'),price:g('p'),wholesale:g('w'),days:g('d'),hours:g('h'),max_devices:g('m'),game:(DB.pgame||{})[k]||'all'};
  const j=await post('/admin/api/packages',body);
  if(j&&j.ok){toast('Đã lưu gói');await loadBase();vPkgs();}else toast((j&&j.thong_bao)||'Lỗi');
 }),
 pkgDel:(k,el)=>withBtn(el,async()=>{
  const p=DB.pkgs[+k];if(!p||!confirm('Xoá gói '+p.name+'?'))return;
  await post('/admin/api/packages',{id:p.id,delete:1});await loadBase();vPkgs();
 }),
 /* mẫu tin */
 tplPick:(k)=>{const ta=$('tpl_ta');if(ta&&DB.mk.tpl)DB.tpls[DB.mk.tpl]=ta.value;DB.mk.tpl=k;vTpl();},
 tplIns:(v)=>{const ta=$('tpl_ta');if(!ta)return;const a=ta.selectionStart,b=ta.selectionEnd,s='{'+v+'}';
  ta.value=ta.value.slice(0,a)+s+ta.value.slice(b);ta.focus();ta.selectionStart=ta.selectionEnd=a+s.length;tplPrev();},
 tplPrev:()=>tplPrev(),
 tplCopy:()=>copyText(fmtMsg(($('tpl_ta')||{}).value||'',DEMO),'bản xem trước'),
 tplReset:()=>{const ta=$('tpl_ta');if(ta)ta.value=DB.tpls[DB.mk.tpl]||'';tplPrev();},
 tplSave:(x,el)=>withBtn(el,async()=>{
  const t=($('tpl_ta')||{}).value||'';
  if(!t.trim())return toast('Nội dung trống');
  const j=await post('/admin/api/settings',{payment_template:t});
  if(j&&j.ok){await loadBase();toast('Đã lưu mẫu tin nhắn');}else toast((j&&j.thong_bao)||'Lỗi');
 }),
 /* cài đặt */
 setSave:(x,el)=>withBtn(el,async()=>{
  const j=await post('/admin/api/settings',{tool_url:($('s_tool')||{}).value||'',support:($('s_sup')||{}).value||'',default_prefix:($('s_pre')||{}).value||''});
  if(j&&j.ok){DB.set=j.settings;toast('Đã lưu cài đặt');}else toast((j&&j.thong_bao)||'Lỗi');
 })
};

/* ─────────── 19. MODAL NỘI DUNG ─────────── */
function findKey(id){return (DB.keys||[]).find(x=>x.id===id)||(DB.kv||[]).find(x=>x.id===id);}
function openKeyMsg(k){
 const sel=DB.mk.tpl||Object.keys(DB.tpls)[0];
 const draw=(t)=>{
  const m=fmtMsg(DB.tpls[t],k);
  modal('<div class="mh"><h2>Tin nhắn · '+esc(k.key)+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
  +'<div class="pills" style="margin-bottom:10px">'+Object.keys(DB.tpls).map(x=>'<button class="pill '+(x===t?'on':'')+'" data-act="kMsgTpl" data-arg="'+esc(k.id)+':'+esc(x)+'">'+esc(DB.tnames[x]||x)+'</button>').join('')+'</div>'
  +'<div class="msg">'+esc(m)+'</div><button class="btn pri big" style="margin-top:11px" data-act="kMsgCopy" data-arg="'+esc(k.id)+':'+esc(t)+'">'+ic('copy','sm')+' Copy tin nhắn</button>');
 };
 draw(sel);
 DB._keymsg=(id,t)=>{const kk=findKey(id);if(kk)draw(t);};
}
function openKeyEdit(k){
 modal('<div class="mh"><h2 class="mono">'+esc(k.key)+'</h2><button class="tbtn" data-act="close">'+ic('close')+'</button></div>'
 +'<p class="muted">'+esc(k.goi||'')+' · tạo '+dfmt(k.ngay_tao)+' · '+(k.da_kich_hoat?'kích hoạt '+dfmt(k.ngay_kich_hoat):'chưa kích hoạt')+(k.don_hang?' · '+esc(k.don_hang):'')+'</p>'
 +'<div class="row"><div><label>Tên khách</label><input id="e_name" value="'+esc(k.ten||'')+'"></div>'
 +'<div><label>Giá</label><input id="e_price" value="'+esc(k.gia||'')+'"></div></div>'
 +'<label>Ghi chú</label><input id="e_note" value="'+esc(k.ghi_chu||'')+'">'
 +'<button class="btn pri big" style="margin-top:11px" data-act="kSave" data-arg="'+esc(k.id)+'">'+ic('save','sm')+' Lưu thông tin</button>'
 +'<label>Cộng thêm thời gian</label><div class="row"><input id="e_d" type="number" min="0" placeholder="+ ngày"><input id="e_h" type="number" min="0" placeholder="+ giờ"></div>'
 +'<button class="btn ok big" style="margin-top:8px" data-act="kExtend" data-arg="'+esc(k.id)+'">'+ic('clock','sm')+' Cộng thời gian</button>'
 +'<label>Thiết bị ('+((k.thiet_bi||[]).length)+') · '+esc(KLABEL[k.game||'all']||'')+'</label>'
 +((k.thiet_bi||[]).map(d=>'<div class="muted" style="margin-bottom:4px">'+ic('dot','xs')+' '+esc(d.ten_thiet_bi)+' · gọi cuối '+dfmt(d.lan_cuoi_goi)+(d.da_gan===false?' · chưa gắn':'')+'</div>').join('')||'<div class="muted">Chưa có</div>')
 +'<div class="row" style="margin-top:10px"><button class="btn" data-act="kResetDev" data-arg="'+esc(k.id)+'">Gỡ thiết bị</button>'
 +'<button class="btn" data-act="kRevoke" data-arg="'+esc(k.id)+'">Thu hồi kích hoạt</button></div>'
 +'<button class="btn bad big" style="margin-top:8px" data-act="kDel" data-arg="'+esc(k.id)+'">'+ic('trash','sm')+' Xoá key</button>');
}

/* thêm các action phụ thuộc modal vào dispatcher */
ACT.kMsgTpl=(v)=>{const a=String(v||'').split(':');if(DB._keymsg)DB._keymsg(a[0],a.slice(1).join(':'));};
ACT.kMsgCopy=(v)=>{const a=String(v||'').split(':');const k=findKey(a[0]);
 if(k)copyText(fmtMsg(DB.tpls[a.slice(1).join(':')],k),'tin nhắn');};
ACT.kSave=(id,el)=>withBtn(el,async()=>{
 const j=await post('/admin/api/keys/'+encodeURIComponent(id),{name:($('e_name')||{}).value,price:($('e_price')||{}).value,note:($('e_note')||{}).value});
 toast((j&&j.thong_bao)||'Đã lưu');closeModal();DB.keys=[];DB.keysAt=0;await vKeys(true);
});
ACT.kExtend=(id,el)=>withBtn(el,async()=>{
 const d=num(($('e_d')||{}).value),h=num(($('e_h')||{}).value);
 if(!d&&!h)return toast('Nhập số ngày hoặc giờ');
 const j=await post('/admin/api/keys/'+encodeURIComponent(id),{extend_days:d,extend_hours:h});
 toast((j&&j.thong_bao)||'Đã cộng thời gian');closeModal();DB.keys=[];DB.keysAt=0;await vKeys(true);
});
ACT.kResetDev=(id,el)=>withBtn(el,async()=>{
 if(!confirm('Gỡ thiết bị đã gắn? Khách sẽ gắn lại máy mới ở lần dùng đầu.'))return;
 const j=await post('/admin/api/keys/'+encodeURIComponent(id),{reset_device:1});
 toast((j&&j.thong_bao)||'Đã gỡ');closeModal();DB.keys=[];DB.keysAt=0;await vKeys(true);
});
ACT.kRevoke=(id,el)=>withBtn(el,async()=>{
 if(!confirm('Thu hồi kích hoạt? Key về trạng thái chưa dùng.'))return;
 const j=await post('/admin/api/keys/'+encodeURIComponent(id),{revoke_activation:1});
 toast((j&&j.thong_bao)||'Đã thu hồi');closeModal();DB.keys=[];DB.keysAt=0;await vKeys(true);
});
ACT.kDel=(id,el)=>withBtn(el,async()=>{
 if(!confirm('Xoá hẳn key này?'))return;
 const j=await post('/admin/api/keys/'+encodeURIComponent(id)+'/delete');
 toast((j&&j.thong_bao)||'Đã xoá');closeModal();DB.keys=[];DB.keysAt=0;await vKeys(true);
});

/* ─────────── 20. INPUT DEBOUNCE ─────────── */
let _t1=null,_t2=null,_t3=null;
function kfq(v){DB.kf.q=v;clearTimeout(_t1);_t1=setTimeout(()=>{
  const L=keyFilter();DB.kv=L;
  const c=document.querySelector('#v .fgroup .muted');
  renderKeyList(L.slice(0,DB.page),L);
  if(c)c.textContent=L.length+' key khớp bộ lọc';
},280);}
function lkq(v){DB.lk.q=v;clearTimeout(_t2);_t2=setTimeout(()=>{vLog();},380);}
function khq(v){DB.kfq.q=v;clearTimeout(_t3);_t3=setTimeout(()=>{vCustomers();},320);}

/* ─────────── 21. CLICK DISPATCH + BOOT ─────────── */
document.addEventListener('click',e=>{
 const el=e.target.closest('[data-act]');
 if(!el)return;
 const fn=ACT[el.dataset.act];
 if(!fn)return;
 e.preventDefault();
 fn(el.dataset.arg||'',el);
});
document.addEventListener('keydown',e=>{
 if(e.key==='Escape')closeModal();
 if((e.ctrlKey||e.metaKey)&&String(e.key).toLowerCase()==='k'){e.preventDefault();palette();}
});

async function boot(){
 let hasPw=true;
 try{const r=await fetch('/admin/api/authinfo',{credentials:'same-origin'});if(r.ok){const j=await r.json();hasPw=!!j.has_password;}}catch(e){}
 let ok=false;
 try{const r=await fetch('/admin/api/overview',{credentials:'same-origin'});ok=(r.status===200);}catch(e){ok=false;}
 if(!ok){
  const w=$('lgwarn');if(w)w.classList.toggle('hide',hasPw);
  showLogin();return;
 }
 try{await loadBase();}catch(e){}
 const lg=$('login'),app=$('app');
 if(lg)lg.classList.add('hide');if(app)app.classList.remove('hide');
 let _th='light';try{_th=localStorage.getItem('paw_theme')||'light';}catch(e){}
 setTheme(_th==='dark'?'dark':'light');
 drawNav();
 try{const pr=await api('/admin/api/pays?brief=1');DB.pays=pr.cho_duyet?new Array(num(pr.cho_duyet)).fill(0):[];drawNav();}catch(e){}
 if(DB.pays.length)toast(DB.pays.length+' phiếu thanh toán CTV chờ duyệt');
 await go('ov');
}
boot();
</script>
</body></html>
"""
@app.route("/admin", methods=["GET"])
def admin_page():
    r = make_response(ADMIN_HTML, 200)
    r.headers["Content-Type"] = "text/html; charset=utf-8"; r.headers["Cache-Control"] = "no-store"
    return r

# ═══════════════════════════════════════════════════════════════════════════════
#  CTV PORTAL — TRANG LÀM VIỆC RIÊNG CHO CỘNG TÁC VIÊN (/ctv)
# ═══════════════════════════════════════════════════════════════════════════════
CTIV_HTML = r"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b0d14">
<title>PAW · Kênh CTV</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
:root{--mono:ui-monospace,Menlo,Consolas,monospace}
html{background:#07080d;color:#eef0f7;font:14px/1.5 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-text-size-adjust:100%;color-scheme:dark}
.skel{height:60px;border-radius:14px;margin-bottom:10px;background:linear-gradient(90deg,#151823,#1c2030,#151823);background-size:200% 100%;animation:sh 1.2s infinite}@keyframes sh{to{background-position:-200% 0}}
.bars{display:flex;align-items:flex-end;gap:5px;height:90px}.bars div{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;font-size:10px;color:#666e88;gap:3px}.bars i{display:block;width:100%;border-radius:5px 5px 2px 2px;background:linear-gradient(180deg,#7c8cff,#5b6cff);min-height:3px}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
body{min-height:100vh;background:#07080d}
button{font:inherit;color:inherit;border:0;background:none;cursor:pointer}
input{font:inherit;color:#eef0f7;background:#151823;border:1.5px solid #232838;border-radius:12px;padding:11px 13px;width:100%;outline:none}
input:focus{border-color:#7c8cff;box-shadow:0 0 0 3px rgba(124,140,255,.14)}
label{display:block;font-size:10.5px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:#666e88;margin:14px 0 6px}
.hide{display:none!important}.mut{color:#666e88;font-size:12.5px}.mono{font-family:var(--mono)}
h1{font-size:20px;font-weight:900;letter-spacing:-.02em}h2{font-size:15px;font-weight:800}
svg.i{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;vertical-align:-4px}
.main{padding:18px 14px 50px;max-width:760px;margin:0 auto}
.card{background:#0e1018;border:1px solid #232838;border-radius:16px;padding:16px;margin-bottom:12px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:10px 15px;border-radius:12px;background:#1c2030;font-weight:700;font-size:13.5px;border:1px solid #232838}
.btn:active{transform:scale(.97)}
.btn.pri{background:linear-gradient(135deg,#5b6cff,#7c8cff);color:#fff;border-color:transparent}
.btn.ok{background:rgba(53,224,161,.13);color:#35e0a1;border-color:transparent}
.btn.bad{background:rgba(255,107,129,.13);color:#ff6b81;border-color:transparent}
.btn.big{width:100%;padding:14px;font-size:15px}.btn.sm{padding:7px 11px;font-size:12.5px;border-radius:10px}
@keyframes spin{to{transform:rotate(360deg)}}
.btn.loading,.btn[disabled]{opacity:.55;pointer-events:none}
.btn.loading::before{content:'';width:14px;height:14px;border:2px solid currentColor;border-top-color:transparent;border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0}
@keyframes fadein{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.card,.kr,.kpi{animation:fadein .25s ease}
.pill{display:inline-flex;padding:3px 9px;border-radius:99px;font-size:11px;font-weight:800;background:#1c2030;color:#a2a9c0}
.pill.act{background:rgba(53,224,161,.13);color:#35e0a1}.pill.ban{background:rgba(255,107,129,.13);color:#ff6b81}
.pill.exp{background:rgba(255,194,71,.13);color:#ffc247}.pill.idle{background:rgba(124,140,255,.14);color:#7c8cff}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:10px;margin-bottom:12px}
.kpi{background:#0e1018;border:1px solid #232838;border-radius:14px;padding:13px}.kpi b{display:block;font-size:23px;font-weight:900}.kpi span{font-size:11px;color:#666e88;font-weight:700}
.msg{white-space:pre-wrap;word-break:break-word;background:#151823;border:1px dashed #232838;border-radius:14px;padding:14px;font-size:13.5px;line-height:1.6}
.kr{padding:13px;border-radius:14px;background:#0e1018;border:1px solid #232838;margin-bottom:9px}
.kr .t{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.kr .k{font-family:var(--mono);font-weight:800;font-size:13.5px}
.kr .m{display:flex;gap:12px;flex-wrap:wrap;font-size:12px;color:#666e88;margin-top:4px}.kr .m b{color:#a2a9c0}
.kr .a{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);z-index:120;background:#eef0f7;color:#07080d;padding:10px 18px;border-radius:99px;font-weight:800;font-size:13px;display:none;box-shadow:0 8px 30px rgba(0,0,0,.4)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{padding:6px 11px;border-radius:99px;background:#151823;border:1px solid #232838;font-size:12px;font-weight:700;color:#a2a9c0}
.chip.on{background:rgba(124,140,255,.14);border-color:#7c8cff;color:#7c8cff}
.tabs{display:flex;gap:8px;margin-bottom:14px}
.tabs button{flex:1;padding:12px 6px;border-radius:12px;background:#151823;border:1px solid #232838;font-weight:800;font-size:13px;color:#a2a9c0}
.tabs button.on{background:rgba(124,140,255,.14);border-color:#7c8cff;color:#7c8cff}
.tabs{overflow-x:auto;scrollbar-width:none}.tabs::-webkit-scrollbar{display:none}.tabs button{white-space:nowrap;flex:1 0 auto;padding:12px 12px}
.tk{position:relative;border-radius:22px;overflow:hidden;background:#0e1018;border:1px solid #2a3050;margin-bottom:12px;box-shadow:0 10px 40px rgba(91,108,255,.2)}
.tk .hd{padding:16px;background:linear-gradient(135deg,#4a5bff,#8a5bff 60%,#b06bff);color:#fff;display:flex;align-items:center;gap:12px}
.tk .hd .lg{width:42px;height:42px;border-radius:13px;background:rgba(255,255,255,.2);display:grid;place-items:center;font-weight:900;font-size:19px;flex-shrink:0}
.tk .hd small{display:block;font-size:10px;letter-spacing:.14em;opacity:.85;font-weight:800;text-transform:uppercase}
.tk .hd b{font-family:var(--mono);font-size:17px;letter-spacing:.05em}
.tk .hd .pill{margin-left:auto;flex-shrink:0}
.tk .amt{text-align:center;padding:18px 16px 4px}.tk .amt span{font-size:10.5px;font-weight:800;letter-spacing:.12em;color:#666e88;text-transform:uppercase}
.tk .amt b{display:block;font-size:36px;font-weight:900;letter-spacing:-.02em;background:linear-gradient(135deg,#8c9bff,#35e0a1);-webkit-background-clip:text;background-clip:text;color:transparent}
.tk .amt em{font-style:normal;font-size:12px;color:#666e88;font-weight:700}
.tk .cut{position:relative;height:22px;margin:10px 0}.tk .cut::before{content:'';position:absolute;left:20px;right:20px;top:50%;border-top:2px dashed #2a3050}
.tk .cut i{position:absolute;top:0;width:22px;height:22px;border-radius:50%;background:#07080d;border:1px solid #2a3050}.tk .cut i:first-child{left:-12px}.tk .cut i:last-child{right:-12px}
.tk .qr{width:240px;max-width:78%;margin:0 auto;padding:12px;border-radius:18px;background:#fff;box-shadow:0 6px 24px rgba(0,0,0,.4)}
.tk .qr .qh{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;font-weight:900;font-size:14px;color:#00695c}.tk .qr .qh em{font-style:normal;color:#c8102e;font-size:12px;letter-spacing:.04em}
.tk .qr img{width:100%;display:block;border-radius:6px}
.tk .rows{padding:10px 16px 6px}
.tk .r{display:flex;align-items:center;gap:8px;padding:10px 0;border-bottom:1px solid #1c2030}.tk .r:last-child{border:0}
.tk .r span{flex:0 0 86px;font-size:10.5px;font-weight:800;color:#666e88;text-transform:uppercase;letter-spacing:.06em}.tk .r b{flex:1;word-break:break-all;font-size:13.5px}
.tk .r b.big{font-family:var(--mono);font-size:15px;color:#8c9bff}
.tk .ft{padding:6px 16px 16px}
.stp{display:flex;gap:6px;margin:14px 16px 6px}.stp div{flex:1;text-align:center;font-size:10.5px;font-weight:800;color:#666e88}
.stp div i{display:grid;place-items:center;width:28px;height:28px;margin:0 auto 5px;border-radius:50%;background:#151823;border:1.5px solid #232838;font-style:normal;font-size:12px}
.stp .on{color:#8c9bff}.stp .on i{background:rgba(124,140,255,.18);border-color:#7c8cff}
.stp .done{color:#35e0a1}.stp .done i{background:rgba(53,224,161,.16);border-color:#35e0a1}
.warn{border-radius:14px;padding:12px 14px;font-size:12.5px;line-height:1.55;background:rgba(255,194,71,.1);border:1px solid rgba(255,194,71,.3);color:#ffc247;margin:0 16px 12px}
.warn.bad{background:rgba(255,107,129,.1);border-color:rgba(255,107,129,.35);color:#ff6b81}
</style></head><body>
<div id="toast"></div>
<div id="login" class="hide" style="min-height:100vh;display:grid;place-items:center;padding:20px"><div style="width:100%;max-width:350px;text-align:center">
 <div style="width:56px;height:56px;border-radius:16px;margin:0 auto 14px;background:linear-gradient(135deg,#5b6cff,#b06bff);display:grid;place-items:center;color:#fff;font-weight:900;font-size:24px">C</div>
 <h1>PAW · Kênh CTV</h1><p class="mut" style="margin-top:4px">Đăng nhập tài khoản cộng tác viên</p>
 <div class="card" style="text-align:left;margin-top:16px"><label style="margin-top:0">Tên đăng nhập</label><input id="lu" autocomplete="username"><br><label>Mật khẩu</label><input id="lp" type="password" autocomplete="current-password" onkeydown="if(event.key==='Enter')login()"><br><br>
 <button class="btn pri big" onclick="login()">Đăng nhập</button></div></div></div>

<div id="app" class="main hide">
 <div style="display:flex;align-items:center;margin-bottom:14px"><div style="flex:1"><h1 id="hi"></h1><span class="mut">Kênh cộng tác viên</span></div><button class="btn sm" onclick="location.href='/ctv/logout'">Đăng xuất</button></div>
 <div class="tabs"><button id="tab_ov" class="on" onclick="tab('ov')">📊 Tổng quan</button><button id="tab_mk" onclick="tab('mk')">🎫 Tạo key</button><button id="tab_kl" onclick="tab('kl')">🔑 Key</button><button id="tab_od" onclick="tab('od')">🧾 Đơn & bill</button><button id="tab_pay" onclick="tab('pay')">💳 Thanh toán</button></div>
 <div id="v"></div>
</div>
<script>
const P={copy:'<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',key:'<path d="m21 2-2 2m-7.6 7.6a5.5 5.5 0 1 1-7.8 7.8 5.5 5.5 0 0 1 7.8-7.8zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3"/>'};
const ic=n=>`<svg class="i" viewBox="0 0 24 24">${P[n]||''}</svg>`;
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));
const pillSt=t=>({'hoạt động':'act','khóa':'ban','hết hạn':'exp','chưa kích hoạt':'idle'}[t]||'');
document.addEventListener('keydown',e=>{if(e.key==='Escape'){const m=document.querySelector('[data-modal]');if(m)m.remove()}});
function toast(m){const t=$('toast');t.textContent=m;t.style.display='block';clearTimeout(t._h);t._h=setTimeout(()=>t.style.display='none',2200)}
function cp(t,l){const ok=()=>toast('Đã copy '+(l||''));if(navigator.clipboard&&isSecureContext)navigator.clipboard.writeText(t).then(ok).catch(()=>fb(t,ok));else fb(t,ok)}
function fb(t,ok){const a=document.createElement('textarea');a.value=t;a.style.cssText='position:fixed;opacity:0';document.body.appendChild(a);a.select();try{document.execCommand('copy');ok()}catch(e){toast('Không copy được')}a.remove()}
async function api(p,o={}){const r=await fetch(p,{headers:{'Content-Type':'application/json'},credentials:'same-origin',...o});
 if(r.status===401){showLogin();throw 0}
 let j;try{j=await r.json()}catch(e){toast('Server trả mã '+r.status);throw 0}return j}
const post=(p,b)=>api(p,{method:'POST',body:JSON.stringify(b||{})});
let ME={},PK={},KEYS=[],CUR='ov';
function debtCard(c,mini){if(!c)return '';const bad=c.khoa_tao_key;
 return `<div class="card" style="border-color:${c.thu_hoi?'#ff6b81':bad?'#ff6b81':c.no_k?'#ffc247':'#232838'}"><h2>💰 Công nợ với admin</h2>
  <div class="chips" style="margin-top:10px"><span class="chip ${c.no_k?'':'on'}" style="font-size:13px">Đang nợ <b>${c.no_k}K</b></span><span class="chip">Hạn mức ${c.han_muc_k}K · còn được nợ ${c.con_duoc_no_k}K</span>${c.cho_duyet?'<span class="chip" style="color:#ffc247">⏳ chờ admin duyệt</span>':''}${c.don_chua_bill?`<span class="chip" style="color:#ff6b81">🧾 ${c.don_chua_bill} đơn chưa gửi bill</span>`:''}</div>
  <p class="mut" style="margin-top:10px">${c.thu_hoi?'<b style="color:#ff6b81">🔒 '+esc(c.ly_do)+'</b>':bad?'<b style="color:#ff6b81">⛔ '+esc(c.ly_do)+'</b>':'Tạo key trước, <b>thanh toán cho admin trong khung '+esc(c.khung_thu_tien)+'</b> mỗi ngày. Quá '+esc(c.chot||'22:00')+' còn nợ mà chưa báo thanh toán → <b>tự động thu hồi toàn bộ key + khóa chức năng</b>.'}</p>
  ${!mini&&c.no_k?`<button class="btn pri big" style="margin-top:12px" onclick="tab('pay')">💳 Thanh toán ngay</button>`:''}</div>`}
function showLogin(){$('app').classList.add('hide');$('login').classList.remove('hide')}
async function login(){const btn=document.querySelector('#login .btn.big');if(btn)btn.classList.add('loading');
 try{const j=await post('/ctv/login',{username:$('lu').value.trim(),password:$('lp').value});if(j.ok)start();else toast(j.thong_bao||'Sai tài khoản')}catch(e){}
 finally{const b=document.querySelector('#login .btn.big');if(b)b.classList.remove('loading')}}
function tab(t){CUR=t;clearInterval(PAYT);['ov','mk','kl','od','pay'].forEach(x=>$('tab_'+x).classList.toggle('on',x===t));({ov:ovView,mk:mkView,kl:()=>{klRenderIn()},od:odView,pay:payView})[t]()}
async function start(){$('login').classList.add('hide');$('app').classList.remove('hide');
 const j=await api('/ctv/api/overview');ME=j;PK={};(j.goi_duoc_ban||[]).forEach(p=>PK[p.id]=p);
 $('hi').textContent='👋 '+(j.ten||'CTV');klFetch();ovView()}
async function klFetch(){try{const j=await api('/ctv/api/keys');KEYS=j.keys||[];if(CUR==='kl')klRenderIn()}catch(e){}}
async function ovView(){const j=await api('/ctv/api/overview');ME=j;
 $('v').innerHTML=debtCard(j.cong_no)+`<div class="kpis">
  <div class="kpi"><b>${j.hom_nay_da_tao||0}${j.cap_key_ngay?`<small style="font-size:13px;color:#666e88">/${j.cap_key_ngay}</small>`:''}</b><span>Key hôm nay</span></div>
  <div class="kpi"><b>${j.tong_key??'…'}</b><span>Tổng key đã tạo</span></div>
  <div class="kpi"><b>${j.da_kich_hoat??'…'}</b><span>Khách đã kích hoạt</span></div>
  <div class="kpi"><b>${j.dang_hoat_dong??'…'}</b><span>Đang chạy</span></div>
  <div class="kpi"><b>${j.het_han??'…'}</b><span>Hết hạn</span></div></div>
 <div class="card"><h2>Key tạo 7 ngày gần nhất</h2><div class="bars" style="margin-top:10px">${(()=>{const m={};(KEYS||[]).forEach(k=>{const d=String(k.ngay_tao||'').slice(5,10);m[d]=(m[d]||0)+1});const out=[];for(let i=6;i>=0;i--){const t=new Date(Date.now()-i*864e5+252e5),d=String(t.getUTCMonth()+1).padStart(2,'0')+'-'+String(t.getUTCDate()).padStart(2,'0');out.push([d,m[d]||0])}const mx=Math.max(1,...out.map(x=>x[1]));return out.map(([d,n])=>`<div><b style="color:#a2a9c0;font-size:10.5px">${n||''}</b><i style="height:${Math.round(n/mx*75)}%"></i><span>${d.slice(3)}</span></div>`).join('')})()}</div></div>
 <div class="card"><h2>Quyền của bạn</h2><div class="chips" style="margin-top:10px">
  ${j.quyen.create_key?'<span class="chip on">🎫 Tạo key</span>':'<span class="chip">⛔ Không được tạo key</span>'}
  ${j.quyen.lock_key?'<span class="chip on">🔒 Khóa/mở key mình tạo</span>':''}
  ${j.quyen.extend_key?'<span class="chip on">⏱ Cộng hạn key mình tạo</span>':''}
  ${j.quyen.custom_price?'<span class="chip on">💰 Tự nhập giá</span>':'<span class="chip">💰 Giá theo gói</span>'}
  ${j.quyen.see_calls?'<span class="chip on">📞 Xem lượt gọi API</span>':''}</div>
  <p class="mut" style="margin-top:10px">Gói được bán: <b>${PK&&Object.keys(PK).length?Object.values(PK).map(p=>esc((p.icon||'')+' '+p.name)).join(' · '):'—'}</b></p></div>
 <div class="card"><h2>Nội quy</h2><p class="mut" style="margin-top:6px">• Mỗi key BẮT BUỘC ghi tên khách hàng.<br>• Key tạo ra gắn với tài khoản CTV của bạn, admin theo dõi đầy đủ.<br>• 1 key = 1 thiết bị · hạn tính từ lúc khách kích hoạt.<br>• Sai phạm → tài khoản bị khóa, mất quyền bán.</p></div>`}
function mkView(){const pkList=Object.values(PK);
 $('v').innerHTML=`${debtCard(ME.cong_no,1)}<div class="card"><h2>🎫 Tạo key cho khách</h2>${pkList.length?'':'<p class="mut" style="margin-top:8px">Chưa được cấp gói nào — liên hệ admin.</p>'}
  <label style="margin-top:10px">Chọn gói</label>
  <div class="chips">${pkList.map(p=>`<button class="chip optpk" data-pid="${p.id}" onclick="mkSel('${p.id}')">${esc(p.icon||'')} ${esc(p.name)} · ${esc(p.price||'?')} ${({lc79:'🎲 LC79',sunwin:'🍒 Sunwin',all:'♾️ Tất cả'})[(p.game||'all')]||''}</button>`).join('')}</div>
  <div id="mkform" class="hide">
   <label>👤 Tên khách hàng — BẮT BUỘC</label><input id="k_name" placeholder="VD: Anh Tú">
   <div class="row"><div><label>Số lượng key</label><input id="k_n" type="number" value="1" min="1" max="50"></div>
   <div><label>Giá bán ${ME.quyen&&ME.quyen.custom_price?'(được phép đổi giá)':'(theo gói)'}</label><input id="k_price" ${ME.quyen&&ME.quyen.custom_price?'':'disabled'}></div></div>
   <label>Ghi chú</label><input id="k_note" placeholder="tuỳ chọn">
   <br><button class="btn pri big" onclick="mkGo(this)">${ic('key')} Tạo key & lấy tin nhắn</button></div></div>
 <div id="mkres"></div>`;
 const first=pkList[0];if(first)mkSel(first.id)}
let CURPK='';
function mkSel(id){if(!id)return;CURPK=id;document.querySelectorAll('.optpk').forEach(b=>b.classList.toggle('on',b.dataset.pid===id));
 $('mkform').classList.remove('hide');$('k_price').value=(PK[id]&&PK[id].price)||''}
async function mkGo(btn){
 if(!CURPK)return toast('Chọn gói trước');
 const name=$('k_name')?$('k_name').value.trim():'';
 if(name.length<2){$('k_name').focus();return toast('⚠️ BẮT BUỘC nhập TÊN KHÁCH HÀNG')}
 const b={package_id:CURPK,count:+$('k_n').value||1,name,note:($('k_note')?$('k_note').value:'').trim()};
 if(ME.quyen.custom_price)b.price=$('k_price').value.trim();
 btn.disabled=true;btn.classList.add('loading');let j;try{j=await post('/ctv/api/keys',b)}catch(e){btn.disabled=false;btn.classList.remove('loading');return}
 btn.disabled=false;btn.classList.remove('loading');if(!j.ok)return toast(j.thong_bao||'Lỗi');
 window._mk=(j.tin_nhan_thanh_toan||[]).map(x=>({key:x.key,msg:x.tin_nhan}));
 $('mkres').innerHTML=`<div class="card"><h2>✅ Đã tạo ${j.da_tao} key · ĐH ${esc(j.don_hang)}</h2>
  <div class="chips" style="margin:10px 0">${window._mk.map(m=>`<span class="chip mono">${esc(m.key)}</span>`).join('')}</div>
  ${window._mk.map((m,i)=>`<div class="msg" style="margin-bottom:8px">${esc(m.msg)}</div><div style="display:flex;gap:6px;margin-bottom:10px"><button class="btn pri" style="flex:1" onclick="cp(_mk[${i}].msg,'tin nhắn')">${ic('copy')} Copy tin nhắn</button><button class="btn" onclick="cp('${m.key}','key')">${ic('key')} Key</button></div>`).join('')}
  ${window._mk.length>1?`<button class="btn big" onclick="cp(_mk.map(m=>m.msg).join('\\n\\n'),'tất cả')">Copy tất cả</button>`:''}</div>`;
 toast('Đã tạo '+j.da_tao+' key');klFetch();if(j.cong_no)ME.cong_no=j.cong_no;
 $('mkres').scrollIntoView({behavior:'smooth'})}
const vnd=k=>(Number(k||0)*1000).toLocaleString('vi-VN');
function fmtCd(s){s=Math.max(0,Math.floor(s));const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;return (h?h+'g ':'')+String(m).padStart(2,'0')+'p '+String(x).padStart(2,'0')+'s'}
const TTLBL={cho_ck:['Chờ chuyển khoản','idle'],cho_duyet:['Chờ admin duyệt','exp'],da_duyet:['Đã duyệt','act'],tu_choi:['Bị từ chối','ban']};
let PAYT=null;
async function payView(){
 clearInterval(PAYT);$('v').innerHTML='<div class="skel"></div><div class="skel"></div>';
 let j;try{j=await api('/ctv/api/pay')}catch(e){return}
 ME.cong_no=j.cong_no;const c=j.cong_no,s=j.phieu,B=j.bank||{};let h=debtCard(c,1);
 if(s){const wait=s.trang_thai==='cho_duyet',lb=TTLBL[s.trang_thai]||['',''];
  h+=`<div class="tk"><div class="hd"><div class="lg">P</div><div><small>Đơn thanh toán điện tử</small><b>${esc(s.ma)}</b></div><span class="pill ${lb[1]}">${lb[0]}</span></div>
  <div class="stp"><div class="${wait?'done':'on'}"><i>1</i>Chuyển khoản</div><div class="${wait?'done':''}"><i>2</i>Báo đã thanh toán</div><div class="${wait?'on':''}"><i>3</i>Admin duyệt</div></div>
  <div class="amt"><span>Số tiền cần thanh toán</span><b>${vnd(s.so_tien_k)} đ</b><em>${s.so_tien_k}K · ${s.don.length} đơn · tạo ${esc(String(s.tao_luc||'').slice(11,16))}</em></div>
  <div class="cut"><i></i><i></i></div>
  <div class="qr"><div class="qh"><span>${esc(B.ten||'BIDV')}</span><em>VIETQR</em></div><div id="qrbox" style="min-height:180px"></div></div>
  <p id="qrnote" class="mut" style="text-align:center;margin:8px 16px 0"></p>
  <div class="rows">
   <div class="r"><span>Ngân hàng</span><b>${esc(B.ten||'')} · ${esc(B.ten_day_du||'')}</b></div>
   <div class="r"><span>Số TK</span><b class="big">${esc(B.stk||'')}</b><button class="btn sm" onclick="cp('${esc(B.stk||'')}','STK')">${ic('copy')}</button></div>
   <div class="r"><span>Chủ TK</span><b>${esc(B.chu_tk||'')}</b></div>
   <div class="r"><span>Số tiền</span><b class="big">${s.so_tien_k*1000}</b><button class="btn sm" onclick="cp('${s.so_tien_k*1000}','số tiền')">${ic('copy')}</button></div>
   <div class="r"><span>Nội dung CK</span><b class="big">${esc(s.noi_dung)}</b><button class="btn sm" onclick="cp('${esc(s.noi_dung)}','nội dung')">${ic('copy')}</button></div>
   <div class="r"><span>Hạn chốt</span><b>${esc(c.chot)} hôm nay${c.no_k&&c.giay_con_lai>0?' · còn <span class="cd" id="cd"></span>':''}</b></div></div>
  <div class="warn ${c.thu_hoi?'bad':''}">${c.thu_hoi?'🔒 Key của bạn đang bị THU HỒI. Chuyển khoản → bấm “Đã thanh toán” → admin duyệt xong sẽ tự mở lại toàn bộ key + chức năng.':'⚠️ Quá '+esc(c.chot)+' mà còn nợ và chưa báo thanh toán → hệ thống <b>tự thu hồi TOÀN BỘ key</b> + khóa chức năng. Ghi ĐÚNG nội dung chuyển khoản để admin đối chiếu.'}</div>
  <div class="ft">${wait?`<div class="msg" style="margin-bottom:10px">⏳ Đã gửi lúc ${esc(String(s.bao_luc||'').slice(11,16))} · bill: <b>${esc(s.bill)}</b><br>Chờ admin kiểm tra tiền và duyệt. Trong lúc chờ key không bị thu hồi.</div>
    <button class="btn big" onclick="ttUndo('${s.id}')">↩ Hủy báo / sửa bill</button>`
   :`<label style="margin-top:0">🧾 Mã giao dịch / link ảnh bill — BẮT BUỘC</label><input id="tt_bill" placeholder="VD: FT26112300123456 hoặc link ảnh bill">
    <label>Ghi chú cho admin (tuỳ chọn)</label><input id="tt_note" placeholder="VD: CK lúc 21:40 từ TK Vietcombank">
    <br><button class="btn ok big" onclick="ttPaid('${s.id}',this)">✅ Tôi đã thanh toán — gửi admin duyệt</button>
    <p class="mut" style="margin-top:8px;text-align:center">Nhớ gửi thêm ảnh bill cho admin để được duyệt nhanh.</p>`}</div>
  ${s.don.length?`<div style="padding:0 16px 16px"><label style="margin-top:0">Các đơn trong phiếu</label>${s.don.map(o=>`<div class="m" style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1c2030;font-size:12.5px"><span><b class="mono">${esc(o.id)}</b> · ${esc(o.khach||'')}</span><b>${o.con_no_k}K</b></div>`).join('')}</div>`:''}</div>`}
 else h+=`<div class="card" style="text-align:center;padding:26px"><div style="font-size:38px">✅</div><h2 style="margin-top:6px">Không còn công nợ</h2><p class="mut" style="margin-top:4px">Khi bạn tạo key mới, đơn thanh toán điện tử sẽ tự sinh tại đây.</p></div>`;
 const H=j.lich_su||[];
 if(H.length)h+=`<div class="card"><h2>📜 Lịch sử thanh toán</h2><div style="margin-top:10px">${H.map(x=>{const lb=TTLBL[x.trang_thai]||['',''];return `<div class="kr"><div class="t"><span class="k">${esc(x.ma)}</span><span class="pill ${lb[1]}">${lb[0]}</span><span style="margin-left:auto"><b>${x.trang_thai==='da_duyet'?x.thuc_nhan_k:x.so_tien_k}K</b></span></div><div class="m"><span>${esc(String(x.duyet_luc||x.tao_luc||'').slice(0,16).replace('T',' '))}</span>${x.ghi_chu_admin?`<span>💬 ${esc(x.ghi_chu_admin)}</span>`:''}</div></div>`}).join('')}</div></div>`;
 $('v').innerHTML=h;
 if(s)drawQR(s);
 if(c.no_k>0&&c.giay_con_lai>0){let left=c.giay_con_lai;const t=()=>{const e=$('cd');if(e)e.textContent=left>0?fmtCd(left):'ĐÃ QUÁ HẠN';left--};t();PAYT=setInterval(t,1000)}}
function drawQR(s,tries){const box=$('qrbox'),note=$('qrnote');if(!box)return;tries=tries||0;
 const img=document.createElement('img');img.alt='QR thanh toán';
 const fb=()=>{img.src='/pay/qr.jpg';note.textContent='QR tĩnh của ngân hàng — hãy tự nhập ĐÚNG số tiền và nội dung chuyển khoản bên dưới'};
 if(!window.qrcode&&tries<4){box.innerHTML='<div class="mut" style="text-align:center;padding:60px 0;color:#666e88">Đang tạo QR…</div>';return setTimeout(()=>drawQR(s,tries+1),500)}
 try{if(!window.qrcode||!s.payload)throw 0;const q=qrcode(0,'M');q.addData(s.payload);q.make();img.src=q.createDataURL(8,2);note.textContent='Quét bằng app ngân hàng — đã điền sẵn số tiền và nội dung chuyển khoản'}catch(e){fb()}
 box.innerHTML='';box.appendChild(img)}
async function ttPaid(id,btn){const b=($('tt_bill').value||'').trim();if(b.length<4){$('tt_bill').focus();return toast('⚠️ Nhập mã giao dịch / link ảnh bill (≥4 ký tự)')}
 if(!confirm('Xác nhận bạn ĐÃ chuyển khoản đúng số tiền + nội dung? Khai sai sẽ bị khóa tài khoản.'))return;
 btn.classList.add('loading');let j;try{j=await post('/ctv/api/pay/'+encodeURIComponent(id)+'/paid',{bill:b,note:($('tt_note').value||'').trim()})}catch(e){btn.classList.remove('loading');return}
 btn.classList.remove('loading');toast(j.thong_bao||'Xong');if(j.ok)payView()}
async function ttUndo(id){const j=await post('/ctv/api/pay/'+encodeURIComponent(id)+'/undo',{});toast(j.thong_bao||'Xong');if(j.ok)payView()}
let KST='all',KLIM=30;
async function odView(){$('v').innerHTML='<div class="skel"></div><div class="skel"></div>';let j;try{j=await api('/ctv/api/orders')}catch(e){return}
 ME.cong_no=j.cong_no;const L=j.don_hang||[];
 $('v').innerHTML=debtCard(j.cong_no)+`<div class="card"><h2>🧾 Đơn & bill thanh toán</h2><p class="mut" style="margin:4px 0 12px">MỖI đơn phải gửi bill (mã giao dịch / link ảnh) của khách. Tạo key không có bill → vi phạm, mất quyền.</p>
  ${L.length?L.map(o=>`<div class="kr"><div class="t"><span class="k">${esc(o.id)}</span><span class="pill ${o.bill_ok?'act':o.bill?'idle':'ban'}">${o.bill_ok?'bill đã duyệt':o.bill?'chờ duyệt':'CHƯA CÓ BILL'}</span></div>
   <div class="m"><span>👤 <b>${esc(o.khach||'')}</b></span><span>${esc(o.goi||'')} · ${o.so_key} key</span><span>Bán ${esc(o.gia||'')}</span><span>Nhập <b>${o.gia_nhap_k}K</b></span></div>
   ${o.bill_ok?`<div class="m"><span>Bill: ${esc(o.bill)}</span></div>`:`<div style="display:flex;gap:6px;margin-top:8px"><input id="bl_${o.id}" value="${esc(o.bill||'')}" placeholder="Mã GD / link ảnh bill"><button class="btn pri sm" onclick="sendBill('${o.id}')">Gửi</button></div>`}</div>`).join(''):'<div class="mut" style="text-align:center;padding:20px">Chưa có đơn nào</div>'}</div>`}
async function sendBill(id){const j=await post('/ctv/api/orders/'+encodeURIComponent(id)+'/bill',{bill:$('bl_'+id).value});toast(j.thong_bao||'Xong');if(j.ok)odView()}
function klRenderIn(){$('v').innerHTML=`<div class="card">
  <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px"><input id="kq" placeholder="🔍 Tìm key / tên khách" oninput="KLIM=30;klRender()" style="flex:1"><button class="btn sm" onclick="klFetch()">↺</button></div>
  <div class="chips" style="margin-bottom:12px">${[['all','Tất cả'],['hoạt động','Hoạt động'],['chưa kích hoạt','Chưa kích hoạt'],['hết hạn','Hết hạn'],['khóa','Khóa']].map(([k,n])=>`<button class="chip ${KST===k?'on':''}" onclick="KST='${k}';KLIM=30;klRenderIn()">${n}</button>`).join('')}<button class="chip" onclick="cp(KEYS.filter(k=>KST==='all'||k.trang_thai===KST).map(k=>k.key).join('\\n'),'danh sách key')">📋 Copy key</button></div>
  <div id="klbox"></div></div>`;klRender()}
function klRender(){const box=$('klbox');if(!box)return;
 const q=(($('kq')&&$('kq').value)||'').toLowerCase().trim();
 const L0=KEYS.filter(k=>(KST==='all'||k.trang_thai===KST)&&(!q||[k.key,k.ten,k.don_hang,k.goi].join(' ').toLowerCase().includes(q))),L=L0.slice(0,KLIM);
 box.innerHTML=L.length?L.map(k=>`<div class="kr"><div class="t"><span class="k">${esc(k.key)}</span><span class="pill ${pillSt(k.trang_thai)}">${esc(k.trang_thai)}</span></div>
  <div class="m"><span>👤 <b>${esc(k.ten||'')}</b></span><span>${esc(k.goi||'')} · ${esc(k.gia||'')}</span><span>Tạo ${esc(String(k.ngay_tao||'').slice(0,16).replace('T',' '))}</span>${k.da_kich_hoat?`<span>KH ${esc(String(k.ngay_kich_hoat||'').slice(0,16).replace('T',' '))}</span>`:'<span>chưa kích hoạt</span>'}</div>
  <div class="a"><button class="btn sm" onclick="keyMsg('${k.key}')">📋 Tin nhắn</button>
   ${ME.quyen.lock_key?(k.trang_thai==='khóa'?`<button class="btn sm ok" onclick="keyAct('${k.key}',{status:'active'})">🔓 Mở khóa</button>`:`<button class="btn sm bad" onclick="keyAct('${k.key}',{status:'banned'})">🔒 Khóa key</button>`):''}
   ${ME.quyen.extend_key?`<button class="btn sm" onclick="keyExt('${k.key}')">⏱ *</button>`:''}</div></div>`).join('')
  :'<div class="mut" style="text-align:center;padding:24px">Chưa có key nào</div>';
 if(L0.length>L.length)box.innerHTML+=`<button class="btn big" onclick="KLIM+=30;klRender()">Xem thêm (${L0.length-L.length})</button>`}
async function keyAct(id,b){const j=await post('/ctv/api/keys/'+encodeURIComponent(id),b);if(j.ok){toast('Đã cập nhật');klFetch();if(CUR==='ov')ovView()}else toast(j.thong_bao||'Lỗi')}
function keyExt(id){const n=prompt('Cộng thêm bao nhiêu NGÀY cho '+id+'?','0');if(n===null)return;
 const h=prompt('Cộng thêm bao nhiêu GIỜ?','0');if(h===null)return;
 keyAct(id,{extend_days:n||0,extend_hours:h||0})}
async function keyMsg(id){let j;try{j=await api('/ctv/api/keys/'+encodeURIComponent(id)+'/msg')}catch(e){return}
 if(!j.ok)return toast(j.thong_bao||'Lỗi');window._km=j.tin_nhan;
 const d=document.createElement('div');d.setAttribute('data-modal','1');d.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,.65);display:flex;align-items:center;justify-content:center;z-index:90;padding:16px';
 d.innerHTML='<div style="background:#0e1018;border:1px solid #232838;border-radius:16px;max-width:480px;width:100%;max-height:82vh;overflow:auto;padding:16px"><h2 style="margin-bottom:10px">'+esc(id)+'</h2><div class="msg">'+esc(j.tin_nhan)+'</div><div style="display:flex;gap:8px;margin-top:12px"><button class="btn pri" style="flex:1" id="_kcp">'+ic('copy')+' Copy tin nhắn</button><button class="btn" id="_kcl">Đóng</button></div></div>';
 document.body.appendChild(d);
 d.querySelector('#_kcp').onclick=()=>cp(window._km,'tin nhắn');
 d.querySelector('#_kcl').onclick=()=>d.remove();
 d.onclick=e=>{if(e.target===d)d.remove()}}
(async()=>{try{const r=await fetch('/ctv/api/overview',{credentials:'same-origin'});if(r.status===200)return start()}catch(e){}
 showLogin();$('login').classList.remove('hide')})();
</script></body></html>
"""

@app.route("/ctv", methods=["GET"])
def ctv_page():
    r = make_response(CTIV_HTML, 200)
    r.headers["Content-Type"] = "text/html; charset=utf-8"; r.headers["Cache-Control"] = "no-store"
    return r

app.add_url_rule("/admin/makey", endpoint="makey_alias", view_func=makey, methods=["GET", "POST"])
app.add_url_rule("/admin/api/<token>/<code>", endpoint="api_predict_alias", view_func=api_predict, methods=["GET", "OPTIONS"])
app.add_url_rule("/admin/api/<token>/history/<code>", endpoint="api_history_alias", view_func=api_history, methods=["GET"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, threaded=True)