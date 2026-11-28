"""
════════════════════════════════════════════════════════════════════════════════
• API dự đoán (Hũ + MD5) chỉ dùng được SAU khi kích hoạt key tại /makey
• Hệ thống GÓI (ngày/tuần/tháng...), ĐƠN HÀNG, tạo key SLL có đơn hàng đẹp
• Mỗi key gắn thiết bị (device) khi kích hoạt — admin xem info đầy đủ
• Render free: /tmp + backup cloud Gist (GIST_TOKEN + GIST_ID) → không mất key
• Engine 84 model + tầng phân tích cầu NGẮN / TRUNG / DÀI + bộ ổn định dài hạn
• v7: ĐA KHUNG CẦU 3 TẦNG 4/13/24 (conviction gate — thiếu mẫu/cầu chưa lệch
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
• v19: CHECK-ALL + XOÁ LỊCH SỬ MỖI BÀN — gộp bản security v17.1 (2FA TOTP,
  CSRF, audit log, phiên trượt, IP allowlist, khoá IP backoff luỹ thừa, thu hồi
  phiên, bảo mật headers mạnh) với chống cầu loạn v18 (EMA p_tai, cờ CẦU LOẠN
  trần tin 55%, đồng thuận chu kỳ điều chỉnh trọng số) · sửa bug: trang Bảo mật
  dùng class-table không tồn tại (tràn bảng trên mobile), auto phân tích dừng
  khi cuộn trang, mất thẻ Chu kỳ 3 tầng trên admin → trả lại đầy đủ ·
  TÍNH NĂNG MỚI: nút XOÁ LỊCH SỬ ở thẻ Bảng phiên của mỗi bàn
  (POST /admin/api/history/<code>/reset, yêu cầu đăng nhập + CSRF, có xác nhận,
  xoá ~ lịch sử chấm + file lưu + brain học lại từ đầu; phiên nguồn vẫn chạy
  bình thường, lịch sử tích luỹ lại từ đó).
"""
import base64, struct, hmac, hashlib, json, math, os, secrets, threading, time, uuid
from collections import deque, Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict

import requests
from flask import Flask, jsonify, make_response, redirect, request, session
from werkzeug.exceptions import HTTPException

URLS  = {"hu":     os.getenv("API_URL_HU",     "https://wtx.tele68.com/v1/tx/sessions"),
         "md5":    os.getenv("API_URL_MD5",    "https://wtxmd52.tele68.com/v1/txmd5/sessions"),
         "sunwin": os.getenv("API_URL_SUNWIN", "https://eagles-bonds-builder-canyon.trycloudflare.com/sunwin/api/tx")}
NAMES = {"hu": "LC79 Hũ", "md5": "LC79 MD5", "sunwin": "Sunwin"}
# Game logic: mỗi GAME một loại key riêng (không dùng chung)
#   lc79   → 2 bàn Hũ + MD5   ·   sunwin → 1 bàn Sunwin
GAME_OF  = {"hu": "lc79", "md5": "lc79", "sunwin": "sunwin"}
GAMES    = {"lc79":   "LC79 · Hũ + MD5 (2 bàn)",
            "sunwin": "Sunwin (1 bàn)",
            "all":    "Tất cả các game"}
GAME_ICON = {"lc79": "🎲", "sunwin": "🍒", "all": "♾️"}

HIST_MAX  = 50
# Lịch sử bảng phiên CHỈ ghi phiên hệ thống đã dự đoán thật (live). Đặt SHOW_REPLAY=1 nếu muốn nạp thêm
# phiên "chấm lại" (backtest) từ dữ liệu nguồn khi khởi động — các dòng đó được gắn nhãn replay.
SHOW_REPLAY = os.getenv("SHOW_REPLAY", "0") == "1"
POLL_SEC  = 4
MIN_GAP   = 3
STALE_SEC = 8
# FIX BUG#2: helper đọc env an toàn — env var sai kiểu không còn làm crash lúc import
def _safe_env_float(name, dflt, lo, hi):
    try: v = float(os.getenv(name, str(dflt)) or dflt)
    except (TypeError, ValueError): v = dflt
    return max(lo, min(hi, v))
def _safe_env_int(name, dflt, lo, hi):
    try: v = int(float(os.getenv(name, str(dflt)) or dflt))
    except (TypeError, ValueError): v = dflt
    return max(lo, min(hi, v))
# FIX v17: cache env vars một lần khi khởi động thay vì đọc lại mỗi lần predict()
_CYCLE_WEIGHT = _safe_env_float("CYCLE_WEIGHT", 0.40, 0.05, 0.8)
_NO_SKIP      = os.getenv("NO_SKIP", "1").strip() != "0"
_FLIP_AFTER   = _safe_env_int("FLIP_AFTER", 3, 2, 10)

ICON       = {"win": "✅", "lose": "❌", "cho": "⏳", "skip": "⏸️"}
VN         = timezone(timedelta(hours=7))
STATE_FILE   = os.getenv("STATE_FILE",   "/tmp/paw_tx_toggles.json")
CFG_FILE     = os.getenv("CFG_FILE",     "/tmp/paw_tx_cfg.json")
HISTORY_FILE = os.getenv("HISTORY_FILE", "/tmp/paw_tx_history.json")
STORE_FILE   = os.getenv("STORE_FILE",   "/tmp/paw_tx_store.json")
BASE_URL       = os.getenv("BASE_URL", "https://apilc79-m-a-l-a-d-a-1.onrender.com")
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
_call_dirty   = {"at": 0.0}

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
        # FIX BUG#3: flush stat lượt gọi (touch_call) xuống đĩa mỗi 30s khi dirty
        if _call_dirty["at"] and time.time() - _call_dirty["at"] >= 30:
            _call_dirty["at"] = 0.0
            try: save_store()
            except Exception: pass
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
            # FIX BUG#4: tôn trọng tham số store nếu caller truyền snapshot dict
            payload = store if isinstance(store, dict) else STORE
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
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
    # FIX BUG#3: đánh dấu dirty — save_store() sẽ được flush định kỳ trong _backup_loop
    _call_dirty["at"] = time.time()

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
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict",
                  SESSION_COOKIE_SECURE=bool(os.getenv("RENDER") or os.getenv("COOKIE_SECURE") == "1"),
                  SESSION_COOKIE_NAME="paw_s", PERMANENT_SESSION_LIFETIME=timedelta(hours=10))
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
    if request.path.startswith("/admin"):          # admin: không CORS, header bảo mật đặt ở admin_headers
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp
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
# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
PAW TX · STABLE CORE v23 — WF-ENSEMBLE + CYCLECORE + LUẬT ĂN · ĐỘ TIN CALIBRATED
════════════════════════════════════════════════════════════════════════════════

ĐỘ TIN CALIBRATED (thay cho dải 58–72% "rải đều" của bản cũ — ĐÃ BỎ):
  · Số % hiển thị = xác suất ensemble thật, bị HẠ bởi bằng chứng tự quan sát:
    hệ ăn thật bao nhiêu % (Wilson 90% trên nhật ký calib) thì được hiển thị
    tối đa cỡ bấy nhiêu. Muốn hiển thị 65% thì hệ phải ăn thật ≥ ~66%/phiên.
  · |p − 0.5| < 0.02 (không lợi thế)  → 50% + chế độ NO_EDGE, nói thẳng không có edge.
  · Chưa đủ 20 phiên tự quan sát      → tối đa 55% (WARMUP), không được phồng.
  · Đây là game 3 xúc xắc: P(TÀI) thật 48.61%. KHÔNG thuật toán nào thắng
    được xác suất dài hạn — hệ v23 trung thực: ăn ~50% là đúng thực tế,
    việc của nó là không phồng số và không nhảy phía vô nghĩa, KHÔNG PHẢI
    hứa 70%. Ai hứa 70% là đang phịa.

CÁCH GẮN (RẤT QUAN TRỌNG):
  Trong file app, XOÁ toàn bộ khối engine cũ BẮT ĐẦU từ dòng

      def _dice_sum_prior():

  (ngay trước dòng chú thích "# RealBrain V8 được nhúng trực tiếp...")

  CHO ĐẾN hết phần replay() cũ, tức là tới ngay TRƯỚC dòng:

      # ── Trạng thái từng bàn ────...   (class Table)

  rồi DÁN TOÀN BỘ file này vào đúng chỗ đó. Mọi thứ bên ngoài khối này
  (Table, /api, analyze_cau, phan_tich_chu_ky_3_tang, ... admin) KHÔNG phải sửa.

GIỮ NGUYÊN HỢP ĐỒNG CŨ:
  Brain.observe / Brain.predict / Brain.learn · replay / entry ·
  brain.engine.seq, brain.engine.sums (cho analyze_cau + view) ·
  đủ fields của pk cho UI (governor, evaluation, chu_ky_3_tang,
  khung_da_phien, cau_loan, dong_thuan_chu_ky, regime, pl, nhom...).

BIẾN MÔI TRƯỜNG MỚI (Render → Environment, đều có mặc định):
  SC_CONF_LO       = đáy dải độ tin hiển thị   (mặc định 50 — đáy THẬT)
  SC_CONF_HI       = đỉnh dải độ tin hiển thị  (mặc định 70 — trần KHÔNG THỂ
                     vượt dù ensemble có "tự tin" tới đâu; muốn thêm phải do
                     tỉ lệ ăn thật chứng minh qua Wilson, không phải env này)
  (Hysteresis / VETO / DEFAULT_SIDE của v21 ĐÃ XOÁ — v22+ tính lại từ dữ liệu
   mỗi phiên, không giữ phía cũ, không nghiêng cứng XỈU khi hết tín hiệu:
   đa số phiên đã có thì theo đa số, hoà thì theo phiên gần nhất.)

THIẾT KẾ — THAY GÌ CHO BẢN CŨ:
  1) BỎ rừng 84 model trùng lặp + các con số tin cậy "cứng" 60–67% không có
     cơ sở: đây là nguyên nhân chính khiến hệ tự tin sai, nhảy TÀI XỈU và
     chạy theo cầu giả.
  2) 6 NHÓM PHÂN TÍCH ĐA DẠNG, mỗi nhóm là 1 chuyên gia hội nghị độc lập:
       HAZARD     - bệt: lịch sử gần đây cho thấy run hiện tại hay TIẾP hay GÃY
       RUNMIRROR  - hình dáng nhịp: cặp (nhịp trước, nhịp nay) 1-1, 2-2, 3-3...
       CTX        - trí nhớ Markov: 2-3 phiên cuối kế tiếp hay ra gì
       REVERSION  - hồi quy cân bằng: dư TÀI nhiều quá thì nghiêng XỈU (và ngược lại)
       MOMENTUM   - xu hướng EMA ngắn (4) vs dài (12)
       FREQ       - tần suất dài 36 phiên: chỉ lên tiếng khi lệch hẳn cực trị
  3) Mọi con số đều ĐO TRÊN DỮ LIỆU THẬT (trọng số quên 0.96^n + Laplace),
     thiếu mẫu => im lặng (0.5). Không hội nghị bắt bẻ khi chưa có bằng chứng.
  4) TRỌNG SỐ KỸ NĂNG walk-forward: mỗi chuyên gia bị chấm THẬT trên chính
     dự đoán của nó (bản cũ chấm SAI: gán kết quả của cả hệ cho mọi model,
     nên trọng số sai ngẫu nhiên). Chuyên gia đang sai
     thì tự im dần; cả hội nghị đều trung bình => hệ tự nén về 50/50.
  5) ỔN ĐỊNH LÂU DÀI:
       - KHÔNG flip theo chuỗi thua, KHÔNG đảo chiều cứng (nguyên nhân hệ
         whipsaw thua cả chuỗi); chỉ thu nhỏ độ tin khi đang thua.
       - Độ tin CALIBRATED: hiển thị đúng bằng chứng (xem đầu file), KHÔNG
         rải đều 58–72% như bản cũ — con số giả làm user đánh mạnh rồi
         phá tài khoản; hệ ăn ~50% thì phải hiện ~50%.
       - Không có tín hiệu => theo đa số phiên đã có (hoà: phiên gần nhất),
         độ tin nằm ở đáy. KHÔNG nghiêng cứng XỈU.
  6) KHÔNG SKIP TUYỆT ĐỐI — auto phân tích dự đoán 100% phiên: từ phiên đầu
     tiên đã ra một phía (BOOT: theo bệt ngắn, chưa rõ thì prior XỈU), từ
     12 phiên trở lên là hội nghị 6 chuyên gia đầy đủ. Không còn trạng thái
     CHỜ/CAM. AUTO-FLIP chống kẹt: chỉ flip khi thua đủ chuỗi VÀ hệ không
     còn bằng chứng nào cho phía đang giữ.
"""
import os
import math
from collections import deque, defaultdict
from typing import Dict

# ── Cấu hình StableCore — đọc MỘT LẦN lúc khởi động ──────────────────────────
def _sc_int(env, dflt, lo, hi):
    try:
        return max(lo, min(hi, int(float(os.getenv(env, str(dflt))))))
    except (TypeError, ValueError):
        return dflt

def _sc_float(env, dflt, lo, hi):
    try:
        return max(lo, min(hi, float(os.getenv(env, str(dflt)))))
    except (TypeError, ValueError):
        return dflt

def _sc_side(env, dflt):
    try:
        v = (os.getenv(env, "") or "").strip().upper()
        return v if v in ("TAI", "XIU") else dflt
    except Exception:
        return dflt

# dải độ tin hiển thị: đáy THẬT 50% — trần _SC_CONF_HI (70%) chỉ là trần cứng;
# con số trong dải do _conf_final() quyết định theo bằng chứng calib, KHÔNG rải đều.
_SC_CONF_LO      = _sc_int("SC_CONF_LO", 50, 50, 60)
_SC_CONF_HI      = max(_SC_CONF_LO + 5, _sc_int("SC_CONF_HI", 70, 55, 85))

_P_TAI_THUC = 105.0 / 216.0    # 0.4861 — xác suất thật của TÀI (3 xúc xắc chuẩn)

# ── Helpers dùng chung (các hàm phân tích phía sau app cũng cần _clamp/_opp) ─
def _clamp(p, lo=0.38, hi=0.62):
    return max(lo, min(hi, p))

def _opp(side: str) -> str:
    return "XIU" if side == "TAI" else "TAI"

def _side_da_so_gan(seq: list):
    """CẤM MẶC ĐỊNH: side dự phòng LUÔN suy từ dữ liệu, không bao giờ trả
    hằng số — đa số các phiên đã có, hoà thì theo phiên gần nhất."""
    if not seq: return None
    _t = seq.count("TAI")
    if _t * 2 > len(seq): return "TAI"
    if _t * 2 < len(seq): return "XIU"
    return seq[-1]

def _run_lengths(seq: list) -> list:
    if not seq:
        return []
    runs, cur, cnt = [], seq[0], 1
    for v in seq[1:]:
        if v == cur:
            cnt += 1
        else:
            runs.append(cnt)
            cur, cnt = v, 1
    runs.append(cnt)
    return runs

def _last_run(seq: list):
    if not seq:
        return ("", 0)
    cur, cnt = seq[-1], 1
    for v in reversed(seq[:-1]):
        if v == cur:
            cnt += 1
        else:
            break
    return (cur, cnt)

def _logit(p):
    p = max(0.02, min(0.98, p))
    return math.log(p / (1.0 - p))

def _sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))

# ══════════════════════════════════════════════════════════════════════════════
#  CORE — hội nghị 6 chuyên gia + trọng số kỹ năng walk-forward
# ══════════════════════════════════════════════════════════════════════════════
class _Core:
    """Bộ máy StableCore. Mỗi chuyên gia trả {side, p, tag}:
    p = độ tin VÀO CHÍNH SIDE đã chọn (>=0.5). p < 0.52 coi như 'im lặng',
    không góp sức vào hội nghị nhưng vẫn nộp side để chấm kỹ năng."""
    EXPERTS = ("NGẮN", "TRUNG", "DÀI")

    def __init__(self):
        self.seq   = deque(maxlen=500)
        self.sums  = deque(maxlen=500)
        self.dices = deque(maxlen=200)
        self.eshits = {n: deque(maxlen=60) for n in self.EXPERTS}
        self.loss_streak = 0
        self.win_streak  = 0
        self.total_w = 0
        self.total_l = 0

    # ── nạp phiên ──
    def push(self, rows: list):
        for r in rows:
            if not isinstance(r, dict):
                continue
            res = r.get("result", "")
            if res not in ("TAI", "XIU"):
                continue
            self.seq.append(res)
            p = r.get("point") or r.get("total")
            if p:
                self.sums.append(int(p))
            d = r.get("dices", [])
            if d and len(d) == 3:
                self.dices.append([int(x) for x in d])

    # ── chấm kỹ năng mỗi chuyên gia (0..1) ──
    def skill(self, name) -> float:
        h = list(self.eshits.get(name) or [])
        if len(h) < 6:
            return 0.0
        # ỔN ĐỊNH LÂU DÀI: cửa sổ chấm dài hơn (10/40 thay vì 8/30) + nghiêng
        # về slow, rồi làm mượt bằng EMA — skill đổi CHẬM, không nhảy theo
        # may mắn/bia đá ngắn hạn. Trước đây fast-8 phiên khiến trọng số dao
        # động mạnh → hệ tốt vài phiên rồi tự làm rối chính nó → lose liên tục.
        fast, slow = h[-10:], h[-40:]
        sf = (sum(fast) + 2.0) / (len(fast) + 4.0) - 0.5
        ss = (sum(slow) + 3.0) / (len(slow) + 6.0) - 0.5
        raw = float(max(0.0, 0.45 * (sf * 2.0) + 0.55 * (ss * 2.0)))
        if not hasattr(self, "_skill_ema"):
            self._skill_ema = {}
        prev = self._skill_ema.get(name)
        val = raw if prev is None else round(0.6 * prev + 0.4 * raw, 4)
        self._skill_ema[name] = val
        return val

    # ── học cuối phiên: chấm ĐÚNG từng chuyên gia trên CHÍNH dự đoán của nó ──
    def update(self, pred_side: str, actual_side: str, pk=None):
        won = pred_side == actual_side
        if won:
            self.win_streak += 1
            self.loss_streak = 0
            self.total_w += 1
        else:
            self.loss_streak += 1
            self.win_streak = 0
            self.total_l += 1
        sides = (pk or {}).get("expert_sides") or {}
        for nme, sd in sides.items():
            if nme in self.eshits and sd in ("TAI", "XIU"):
                self.eshits[nme].append(1 if sd == actual_side else 0)

    # ═══════════ 6 CHUYÊN GIA ═══════════
    def experts(self, seq: list) -> Dict[str, Dict]:
        n = len(seq)
        last, rlen = _last_run(seq)

        # run_at[i] = độ dài nhịp tại vị trí i
        run_at = [1] * n
        for i in range(1, n):
            run_at[i] = run_at[i - 1] + 1 if seq[i] == seq[i - 1] else 1
        # độ dài nhịp TRƯỚC nhịp hiện tại
        prev_run = 0
        ip = n - 1 - rlen
        if ip >= 0:
            prev_run = 1
            j = ip - 1
            while j >= 0 and seq[j] == seq[ip]:
                prev_run += 1
                j -= 1
        out = {}

        # 1) HAZARD — bệt: run hiện tại hay TIẾP hay GÃY (đo trên lịch sử thật)
        rk = min(rlen, 8)
        f = b = 0.0
        for i in range(n - 1):
            if run_at[i] == rk:
                w = 0.96 ** (n - 1 - i)
                if seq[i + 1] == seq[i]:
                    f += w
                else:
                    b += w
        pf = (f + 1.0) / (f + b + 2.0)
        if rlen > 3 and rlen > max(run_at[:-1]):
            pf = min(pf, 0.42)   # bệt dài hơn mọi bệt đã thấy => nghiêng gãy
        pf = _clamp(pf, 0.38, 0.62)
        s1 = last if pf >= 0.5 else _opp(last)
        out["HAZARD"] = {"side": s1, "p": max(pf, 1.0 - pf),
                         "tag": "bệt %d %s: %s %.0f%%" % (
                             rlen, last, "theo" if pf >= 0.5 else "bẻ",
                             max(pf, 1.0 - pf) * 100)}

        # 2) RUNMIRROR — cặp nhịp (trước, nay): 1-1, 2-2, 3-3, 2-1...
        mir = defaultdict(lambda: [0.0, 0.0])
        for i in range(1, n - 1):
            key = (min(run_at[i - 1], 4), min(run_at[i], 4))
            w = 0.96 ** (n - 1 - i)
            if seq[i + 1] == seq[i]:
                mir[key][0] += w
            else:
                mir[key][1] += w
        m2 = mir.get((min(prev_run, 4), min(rlen, 4)))
        if m2 and (m2[0] + m2[1]) >= 4:
            pf2 = _clamp((m2[0] + 1.0) / (m2[0] + m2[1] + 2.0), 0.38, 0.62)
            s2 = last if pf2 >= 0.5 else _opp(last)
            out["RUNMIRROR"] = {"side": s2, "p": max(pf2, 1.0 - pf2),
                                "tag": "nhịp %d-%d: %s %.0f%%" % (
                                    min(prev_run, 4), min(rlen, 4),
                                    "theo" if pf2 >= 0.5 else "bẻ",
                                    max(pf2, 1.0 - pf2) * 100)}
        else:
            out["RUNMIRROR"] = {"side": last, "p": 0.5,
                                "tag": "nhịp %d-%d: thiếu mẫu" % (min(prev_run, 4), min(rlen, 4))}

        # 3) CTX — trí nhớ Markov: 3 phiên cuối (yếu mẫu thì 2 phiên cuối)
        ctx3 = defaultdict(lambda: [0.0, 0.0])
        ctx2 = defaultdict(lambda: [0.0, 0.0])
        for i in range(1, n):
            w = 0.96 ** (n - 1 - i)
            tgt = 0 if seq[i] == "TAI" else 1
            ctx2[(seq[i - 1],)][tgt] += w
            if i >= 3:
                ctx3[tuple(seq[i - 3:i])][tgt] += w
        p_c, tag_c, used = 0.5, "khóm 0: thiếu mẫu", 0
        for k, tbl in ((3, ctx3), (2, ctx2)):
            key = tuple(seq[-k:])
            c = tbl.get(key)
            if c and (c[0] + c[1]) >= 8:
                p_c = (c[0] + 1.0) / (c[0] + c[1] + 2.0)
                used = k
                tag_c = "khóm %d phiên: TÀI %.0f%%" % (k, p_c * 100)
                break
        p_c = _clamp(p_c, 0.38, 0.62)
        out["CTX"] = {"side": "TAI" if p_c >= 0.5 else "XIU",
                      "p": max(p_c, 1.0 - p_c) if used else 0.5, "tag": tag_c}

        # 4) REVERSION — hồi quy cân bằng trên khung 24 phiên (chỉ khi lệch z>=1.2)
        w24 = seq[-24:]
        n24, t24 = len(w24), w24.count("TAI")
        if n24 >= 12:
            z = (t24 / n24 - 0.5) / math.sqrt(0.25 / n24)
            if abs(z) >= 1.2:
                p_r = _clamp(0.5 - 0.06 * z, 0.42, 0.58)
                out["REVERSION"] = {"side": "TAI" if p_r >= 0.5 else "XIU",
                                    "p": max(p_r, 1.0 - p_r),
                                    "tag": "cân bằng z=%.2f (24p)" % z}
            else:
                out["REVERSION"] = {"side": last, "p": 0.5,
                                    "tag": "cân bằng z=%.2f: bình thường" % z}
        else:
            out["REVERSION"] = {"side": last, "p": 0.5, "tag": "thiếu mẫu (24p)"}

        # 5) MOMENTUM — EMA ngắn (4) vs dài (12)
        bins = [1 if v == "TAI" else 0 for v in seq]
        ln = min(12, n)
        if n >= 14 and ln >= 8:
            a = 2.0 / (ln + 1.0)
            e12 = bins[-ln]
            for v in bins[-ln + 1:]:
                e12 = a * v + (1.0 - a) * e12
            a4 = 2.0 / 5.0
            e4 = bins[-4]
            for v in bins[-3:]:
                e4 = a4 * v + (1.0 - a4) * e4
            d_m = e4 - e12
            if abs(d_m) >= 0.06:
                p_m = _clamp(0.5 + 4.0 * d_m, 0.42, 0.58)
                out["MOMENTUM"] = {"side": "TAI" if p_m >= 0.5 else "XIU",
                                   "p": max(p_m, 1.0 - p_m),
                                   "tag": "xu hướng EMA d=%.2f" % d_m}
            else:
                out["MOMENTUM"] = {"side": last, "p": 0.5, "tag": "xu hướng phẳng"}
        else:
            out["MOMENTUM"] = {"side": last, "p": 0.5, "tag": "thiếu mẫu EMA"}

        # 6) FREQ — tần suất dài 36 phiên, chỉ lên tiếng khi lệch hẳn cực trị
        w36 = seq[-36:]
        n36, t36 = len(w36), w36.count("TAI")
        if n36 >= 24:
            dev = t36 / n36 - 0.5
            if abs(dev) >= 0.16:
                p_f = _clamp(0.5 - dev * 0.35, 0.44, 0.56)
                out["FREQ"] = {"side": "TAI" if p_f >= 0.5 else "XIU",
                               "p": max(p_f, 1.0 - p_f),
                               "tag": "36p TÀI %.0f%% => lệch hẳn" % (t36 / n36 * 100)}
            else:
                out["FREQ"] = {"side": last, "p": 0.5, "tag": "36p gần cân bằng"}
        else:
            out["FREQ"] = {"side": last, "p": 0.5, "tag": "thiếu mẫu (36p)"}
        return out

    # ═══════════ HỘI NGHỊ ═══════════
    def combine(self, ex: Dict[str, Dict], seq: list = None):
        """v27: Trả (p_tai, skills, expert_sides).
        CauAdapter đọc cầu → điều chỉnh p từng expert TRƯỚC khi logit-vote.
        Giải quyết: kẹt phía / bỏ sót cầu 1-1 / bệt bị bẻ nhầm."""
        skills = {n: self.skill(n) for n in self.EXPERTS}
        tot = sum(skills.values())
        expert_sides = {}

        # v27: đọc cầu để điều chỉnh trọng số
        cau_ctx = _read_cau_now(seq) if (seq and len(seq) >= 6) else None

        _uniform = tot < 1e-9
        zbar = 0.0
        for n in self.EXPERTS:
            e = ex[n]
            pt_raw = e["p"] if e["side"] == "TAI" else 1.0 - e["p"]

            # v27: điều chỉnh p theo cầu trước khi vote
            if cau_ctx and cau_ctx["type"] != "HON_HOP":
                pt_adj = _cau_weight_adjust(cau_ctx, n, pt_raw)
            else:
                pt_adj = pt_raw

            expert_sides[n] = e["side"] if pt_adj >= 0.52 else (None if pt_adj > 0.48 else _opp(e["side"]))
            w = 1.0 / len(self.EXPERTS) if _uniform else skills[n]
            zbar += w * _logit(pt_adj)

        zbar = max(-0.55, min(0.55, zbar / (len(self.EXPERTS) if _uniform else tot)))
        damp = min(1.0, (0.55 if _uniform else 0.30) + 1.1 * max(skills.values()))
        p_out = _sigmoid(damp * zbar)

        # v27: anti-stuck — nếu cầu 1-1 rõ (strength > 0.75) và p_out sai chiều → ép đúng
        if cau_ctx and cau_ctx["type"] == "XEN_KE" and cau_ctx["strength"] > 0.75:
            last = cau_ctx["last"]
            correct_p_tai = 0.42 if last == "TAI" else 0.58  # nếu cuối TAI → tiếp theo XIU
            # Chỉ ép khi hội nghị đang sai chiều hẳn
            if (last == "TAI" and p_out > 0.52) or (last == "XIU" and p_out < 0.48):
                p_out = correct_p_tai
        elif cau_ctx and cau_ctx["type"] == "BET" and cau_ctx["strength"] > 0.70 and cau_ctx["rlen"] <= 4:
            last = cau_ctx["last"]
            correct_p_tai = 0.58 if last == "TAI" else 0.42  # theo bệt
            # Chỉ ép nhẹ khi hội nghị đang ngược bệt
            if (last == "TAI" and p_out < 0.48) or (last == "XIU" and p_out > 0.52):
                p_out = p_out * 0.4 + correct_p_tai * 0.6

        return _clamp(p_out, 0.38, 0.62), skills, expert_sides

# ══════════════════════════════════════════════════════════════════════════════
#  BRAIN — hợp đồng giữ nguyên cho Table / replay / API
# ══════════════════════════════════════════════════════════════════════════════
# ═════════════════════════════════════════════════════════════════════════════
#  CAU LIBRARY v28 — THƯ VIỆN ~24 MẪU CẦU + TỰ CHỌN CẦU ĐANG "ĂN" + THEO/BẺ
#  Mỗi mẫu là 1 hàm: nhìn đuôi chuỗi → nếu khớp thì nói phiên kế là gì (bit 1=TÀI).
#  Chọn cầu: backtest TỪNG mẫu trên ~120 phiên gần nhất (chỉ dùng dữ liệu trước phiên đó,
#  không nhìn tương lai) → mẫu nào đang khớp VÀ có tỉ lệ đúng (cận dưới Wilson) cao nhất thì được chọn.
#  THEO = dự đoán trùng phiên vừa ra · BẺ = dự đoán ngược phiên vừa ra.
#  Không mẫu nào vượt may rủi → nói thẳng "chưa rõ cầu", không bịa.
# ═════════════════════════════════════════════════════════════════════════════
def _cl_runs(b):
    r = []
    for x in b:
        if r and r[-1][0] == x: r[-1][1] += 1
        else: r.append([x, 1])
    return r

def _cl_lb(h, n, z=2.2):   # z cao ~ hiệu chỉnh việc chọn 1 trong ~24 mẫu (tránh "ăn may")
    if n <= 0: return 0.0
    p = h / n; d = 1 + z * z / n
    c = p + z * z / (2 * n); m = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return max(0.0, (c - m) / d)

def _cl_bet_theo(b):
    L = _cl_runs(b)[-1][1]
    return (b[-1], "Bệt %d phiên → theo" % L) if 2 <= L <= 4 else None
def _cl_bet_be(k):
    def f(b):
        L = _cl_runs(b)[-1][1]
        ok = (L >= 5) if k == 5 else (L == k)
        return (1 - b[-1], "Bệt %d%s → bẻ" % (L, "")) if ok else None
    return f
def _cl_bet_hist(b):
    R = [x[1] for x in _cl_runs(b)]; L = R[-1]; done = [r for r in R[:-1] if r >= L]
    if L < 2 or len(done) < 6: return None
    cont = sum(1 for r in done if r > L) / len(done)
    return (b[-1] if cont >= 0.5 else 1 - b[-1], "Lịch sử bệt ≥%d: %d%% đi tiếp" % (L, round(cont * 100)))
def _cl_alt_len(b):
    a = 1
    while a < len(b) and b[-1 - a] != b[-a]: a += 1
    return a
def _cl_dao(b):
    a = _cl_alt_len(b)
    return (1 - b[-1], "Cầu 1-1 (xen kẽ %d phiên) → theo nhịp đảo" % a) if 4 <= a <= 6 else None
def _cl_dao_be(b):
    a = _cl_alt_len(b)
    return (b[-1], "Xen kẽ %d phiên quá dài → bẻ nhịp" % a) if a >= 7 else None
def _cl_chuky(k):
    def f(b):
        if len(b) < 2 * k or b[-k:] != b[-2 * k:-k]: return None
        nm = "-".join(str(x[1]) for x in _cl_runs(b[-k:]))
        return (b[-k], "Cầu %s (chu kỳ %d phiên lặp)" % (nm, k))
    return f
def _cl_guong(m):
    def f(b):
        if len(b) < 2 * m + 1 or b[-m:] != b[-2 * m:-m][::-1]: return None
        return (b[-2 * m - 1], "Cầu gương %d phiên" % m)
    return f
def _cl_ngram(k):
    def f(b):
        key = b[-k:]; nx = [b[j + k] for j in range(len(b) - k) if b[j:j + k] == key]
        if len(nx) < 3: return None
        t = sum(nx); r = t / len(nx)
        if 0.35 < r < 0.65: return None
        return (1 if r > .5 else 0, "Mẫu %s đã lặp %d lần, %d%% ra %s" % ("".join("T" if x else "X" for x in key), len(nx), round(max(r, 1 - r) * 100), "Tài" if r > .5 else "Xỉu"))
    return f
def _cl_lech(theo, w=10, th=7):
    def f(b):
        x = b[-w:]
        if len(x) < w: return None
        t = sum(x)
        if t >= th: maj = 1
        elif t <= w - th: maj = 0
        else: return None
        return (maj if theo else 1 - maj, "Nghiêng %d/%d %s → %s" % (max(t, w - t), w, "Tài" if maj else "Xỉu", "theo bên nhiều" if theo else "bẻ hồi về giữa"))
    return f
def _cl_trend(d):
    def f(b):
        R = [x[1] for x in _cl_runs(b)]
        if len(R) < 3 or R[-3] + d != R[-2]: return None
        T = R[-2] + d
        if T < 1: return None
        return (b[-1] if R[-1] < T else 1 - b[-1], "Cầu %s dần (%d-%d-…)" % ("tăng" if d > 0 else "giảm", R[-3], R[-2]))
    return f
def _cl_nhip(p):
    def f(b):
        R = [x[1] for x in _cl_runs(b)]; c = len(R) - 1
        if c < 2 * p or any(R[c - 1 - i] != R[c - 1 - i - p] for i in range(p)): return None
        T = R[c - p]; nm = "-".join(str(R[c - p + i]) for i in range(p)) if p > 1 else "%d-%d" % (T, T)
        return (b[-1] if R[c] < T else 1 - b[-1], "Cầu %s nhịp run đều (run đích %d)" % (nm, T))
    return f

_CL_TPL = [("BET_NGAN_THEO", "Bệt ngắn", _cl_bet_theo), ("BET_3_BE", "Bệt 3 bẻ", _cl_bet_be(3)),
    ("BET_4_BE", "Bệt 4 bẻ", _cl_bet_be(4)), ("BET_DAI_BE", "Bệt dài bẻ", _cl_bet_be(5)),
    ("BET_LICH_SU", "Bệt theo lịch sử gãy", _cl_bet_hist), ("DAO_1_1", "Cầu 1-1", _cl_dao),
    ("DAO_DAI_BE", "1-1 dài bẻ", _cl_dao_be)] + \
    [("CHU_KY_%d" % k, "Chu kỳ %d" % k, _cl_chuky(k)) for k in (2, 3, 4, 5, 6)] + \
    [("GUONG_%d" % m, "Cầu gương %d" % m, _cl_guong(m)) for m in (3, 4)] + \
    [("MAU_LAP_%d" % k, "Mẫu lặp %d" % k, _cl_ngram(k)) for k in (3, 4, 5)] + \
    [("LECH_THEO", "Lệch theo", _cl_lech(True)), ("LECH_BE", "Lệch bẻ", _cl_lech(False)),
     ("LECH_13_THEO", "Nghiêng 13 phiên", _cl_lech(True, 13, 9)), ("LECH_6_THEO", "Nghiêng 6 phiên", _cl_lech(True, 6, 5)),
     ("LECH_20_THEO", "Nghiêng 20 phiên", _cl_lech(True, 20, 13)),
     ("TANG_DAN", "Cầu tăng dần", _cl_trend(1)), ("GIAM_DAN", "Cầu giảm dần", _cl_trend(-1))] + \
    [("NHIP_RUN_%d" % p, "Nhịp run %d" % p, _cl_nhip(p)) for p in (1, 2, 3)]
_CL_CACHE = {}

def _cl_describe(b):
    """Luôn mô tả được cầu hiện tại (kể cả khi chưa mẫu nào được kiểm chứng) — mức MÔ_TẢ."""
    R = [x[1] for x in _cl_runs(b)]; sig = "-".join(str(x) for x in R[-4:])
    w = b[-13:]; t = sum(w); n = len(w)
    if t * 2 == n: ph = 1 - b[-1]; why = "cân bằng → đảo phiên cuối"
    else:
        ph = 1 if t * 2 > n else 0; why = "nghiêng %d/%d %s" % (max(t, n - t), n, "Tài" if ph else "Xỉu")
    return {"ma": "MO_TA", "ten": "Cầu hỗn hợp %s" % sig, "mo_ta": "hình dạng run %s · %s" % (sig, why),
            "phia": "TAI" if ph else "XIU", "hanh_dong": "THEO" if ph == b[-1] else "BẺ",
            "hit": 0, "n": 0, "ti_le": 0.0, "do_tin_cay_lb": 0.0, "muc": "MÔ_TẢ"}

def _cl_chu_ky(b):
    """Phân tích 3 chu kỳ 4 / 13 / 24 phiên: mỗi chu kỳ nhận dạng loại cầu + phía nghiêng."""
    out = []
    for ten, w in (("NGẮN", 4), ("TRUNG", 13), ("DÀI", 24)):
        x = b[-w:]
        if len(x) < 3: continue
        n = len(x); t = sum(x); R = [r[1] for r in _cl_runs(x)]
        alt = sum(1 for i in range(1, n) if x[i] != x[i - 1]) / (n - 1); mx = max(R); maj = max(t, n - t) / n
        if alt >= 0.8: loai, ph = "1-1", 1 - x[-1]
        elif mx >= max(3, round(n * 0.6)): loai, ph = "BỆT", x[-1]
        elif maj >= 0.7: loai, ph = "NGHIÊNG", 1 if t * 2 > n else 0
        elif mx <= 2 and 0.45 <= alt < 0.8: loai, ph = "NHỊP 2", (x[-1] if R[-1] < 2 else 1 - x[-1])
        else: loai, ph = "HỖN HỢP", (None if t * 2 == n else (1 if t * 2 > n else 0))
        out.append({"tang": ten, "w": w, "loai": loai, "tai": t, "xiu": n - t,
                    "phia": None if ph is None else ("TAI" if ph else "XIU"),
                    "hanh_dong": None if ph is None else ("THEO" if ph == x[-1] else "BẺ")})
    return out

def cau_library_pick(seq):
    """MỖI PHIÊN đều trả 1 cầu có tên: {cau_chon:{ten,mo_ta,hanh_dong THEO/BẺ,phia,hit,n,ti_le,do_tin_cay_lb,muc}, chu_ky:[4/13/24], khop:[...]}.
    muc: ĐÁNG_TIN (vượt may rủi) · THAM_KHẢO (>50% nhưng ít mẫu) · YẾU · MÔ_TẢ (chưa kiểm chứng, chỉ gọi tên hình dạng)."""
    b = [1 if s == "TAI" else 0 for s in seq[-200:]]
    if len(b) < 3: return {"da_du_du_lieu": False, "cau_chon": None, "chu_ky": [], "khop": [], "nhan": "Chưa đủ phiên để nhận cầu"}
    ck = "".join(map(str, b))
    if ck in _CL_CACHE: return _CL_CACHE[ck]
    st = {}
    if len(b) >= 14:
        for i in range(max(10, len(b) - 120), len(b)):
            pre = b[max(0, i - 150):i]
            for fam, _, fn in _CL_TPL:
                r = fn(pre)
                if r:
                    h, n = st.get(fam, (0, 0)); st[fam] = (h + (1 if r[0] == b[i] else 0), n + 1)
    now = []
    for fam, ten, fn in _CL_TPL:
        r = fn(b)
        if not r: continue
        h, n = st.get(fam, (0, 0)); lb = _cl_lb(h, n)
        now.append({"ma": fam, "ten": ten, "mo_ta": r[1], "phia": "TAI" if r[0] else "XIU",
                    "hanh_dong": "THEO" if r[0] == b[-1] else "BẺ", "hit": h, "n": n,
                    "ti_le": round(h / n, 3) if n else 0.0, "do_tin_cay_lb": round(lb, 3)})
    now = [c for c in now if c["n"] >= 6]
    now.sort(key=lambda c: (c["do_tin_cay_lb"], c["ti_le"], c["n"]), reverse=True)
    res = {"da_du_du_lieu": len(b) >= 14, "cau_chon": None, "cau_khac": [], "khop": now, "dang_khop": [c["ten"] for c in now],
           "chu_ky": _cl_chu_ky(b), "luu_y": "tỉ lệ đo trên lịch sử gần, không đảm bảo phiên tới"}
    if now:
        top = now[0]
        top["muc"] = "ĐÁNG_TIN" if (top["do_tin_cay_lb"] > 0.5 and top["n"] >= 8) else ("THAM_KHẢO" if top["ti_le"] > 0.5 else "YẾU")
        res["cau_chon"] = top; res["cau_khac"] = now[1:4]
    if res["cau_chon"] is None: res["cau_chon"] = _cl_describe(b)
    c = res["cau_chon"]
    res["nhan"] = "%s → %s %s%s" % (c["mo_ta"], c["hanh_dong"], "TÀI" if c["phia"] == "TAI" else "XỈU",
                                    (" (%d/%d phiên ăn)" % (c["hit"], c["n"])) if c["n"] else " (chưa kiểm chứng)")
    if len(_CL_CACHE) > 64: _CL_CACHE.clear()
    _CL_CACHE[ck] = res
    return res

def cau_module_report(scored):
    on = [k for k, v in scored.items() if v["weight"] > 0]
    soft = [k for k, v in scored.items() if v["weight"] <= 0 and v.get("w_soft", 0) > 0]
    off = [k for k, v in scored.items() if v["weight"] <= 0 and v.get("w_soft", 0) <= 0]
    return {"tong": len(scored), "dang_dung": len(on), "tham_khao": len(soft), "da_tat": len(off),
            "ten_da_tat": off[:16], "manh_nhat": sorted(on, key=lambda k: -scored[k]["weight"])[:5]}

def cau_unstick(pred_sides, hits, seq, cau_pick):
    """GỠ KẸT: hệ dự đoán liền 1 phía mà thua → ép sang phía có bằng chứng.
    Trả (side, ly_do) hoặc None nếu hệ đang bình thường."""
    ps = list(pred_sides)[-6:]; hs = list(hits)[-6:]
    k = min(len(ps), len(hs))
    if k < 4: return None
    ps, hs = ps[-k:], hs[-k:]
    top = "TAI" if ps.count("TAI") >= ps.count("XIU") else "XIU"; same = ps.count(top)
    if same < max(4, k - 1): return None
    if sum(h for p, h in zip(ps, hs) if p == top) > same * 0.34: return None
    cc = (cau_pick or {}).get("cau_chon")
    if cc and cc["ti_le"] > 0.5 and cc["phia"] != top:
        return cc["phia"], "kẹt %s %d/%d phiên thua → theo %s (%s)" % (top, same, k, cc["ten"], cc["hanh_dong"])
    w = list(seq)[-10:]; t = w.count("TAI")
    if t != len(w) - t:
        m = "TAI" if t > len(w) - t else "XIU"
        if m != top: return m, "kẹt %s %d/%d phiên thua → kết quả đang nghiêng %s %d/%d" % (top, same, k, m, max(t, len(w) - t), len(w))
    return ("XIU" if top == "TAI" else "TAI"), "kẹt %s %d/%d phiên thua → đảo phía" % (top, same, k)

# ══════════════════════════════════════════════════════════════════════════════
#  CYCLECORE v22 — 3 TẦNG NGẮN / TRUNG / DÀI TRÊN 26 PHIÊN GẦN NHẤT
#  Sửa gốc lỗi "đầu ổn, sau gãy / kẹt một phía":
#   · v21 có bộ "giữ phía cũ" (hysteresis 0.02) + EMA p_tai + _stick_side: tín hiệu thật
#     thường < 0.02 nên hệ gần như KHÔNG BAO GIỜ đổi phía (đo: có lúc dự đoán 82 phiên cùng 1 phía).
#   · v22: MỖI phiên tính lại từ dữ liệu, KHÔNG nhìn dự đoán phiên trước.
#  Cách làm: 10 luật cầu → mỗi luật được chấm walk-forward (chưa nhìn tương lai) trên
#  3 cửa sổ: NGẮN 8 · TRUNG 14 · DÀI 26 phiên. Mỗi tầng chọn luật ăn nhất, rồi TRỪ phần
#  "ăn may do chọn 1 trong 10" (selection bias) — tầng nào không vượt nổi mức may rủi thì
#  không được bỏ phiếu. Không tầng nào đủ tin → vẫn ra 1 phía (không SKIP) nhưng độ tin ở đáy.
# ══════════════════════════════════════════════════════════════════════════════
CC_WINDOWS = (("NGẮN", 4), ("TRUNG", 13), ("DÀI", 24))
CC_RULES = ("BỆT", "ĐẢO", "BỆT_GÃY", "NHỊP_ĐỀU", "MẪU_LẶP", "CHU_KỲ_2", "CHU_KỲ_3", "CHU_KỲ_4",
            "CÂN_BẰNG", "ĐÀ_5")

# ══════════════════════════════════════════════════════════════════════════════
#  CauAdapter v27 — ĐỌC CẦU TRƯỚC, ĐIỀU CHỈNH TRỌNG SỐ EXPERT SAU
#  Triết lý: đừng hardcode luật, đọc cầu từ dữ liệu rồi boost/damp expert phù hợp
#  Không thêm layer mới — chỉ điều chỉnh trọng số trong hội nghị hiện tại
# ══════════════════════════════════════════════════════════════════════════════
def _read_cau_now(seq: list) -> dict:
    """Đọc cầu hiện tại từ 12 phiên gần nhất.
    Trả: {type, strength, last, rlen, alt_rate, avg_run}
    type: XEN_KE | NHIP_2 | NHIP_3 | BET | HON_HOP"""
    if len(seq) < 6:
        return {"type": "HON_HOP", "strength": 0.0, "last": seq[-1] if seq else "TAI",
                "rlen": 1, "alt_rate": 0.5, "avg_run": 1.0}
    w = seq[-12:]
    runs = _run_lengths(w)
    last, rlen = w[-1], runs[-1]
    n = len(w)

    # Tỷ lệ đảo chiều thực tế
    alt = sum(1 for i in range(1, len(w)) if w[i] != w[i-1]) / (len(w) - 1) if len(w) > 1 else 0.5
    avg_run = sum(runs) / len(runs)

    # Tỷ lệ từng loại run
    r1 = sum(1 for r in runs if r == 1) / len(runs)
    r2 = sum(1 for r in runs if r == 2) / len(runs)
    r3 = sum(1 for r in runs if r == 3) / len(runs)

    # Fast-detect: 5 phiên cuối xen kẽ liên tục
    tail5 = w[-6:] if len(w) >= 6 else w
    alt5  = sum(1 for i in range(1, len(tail5)) if tail5[i] != tail5[i-1]) / max(1, len(tail5)-1)

    if alt5 >= 0.85 or (r1 >= 0.60 and avg_run <= 1.6):
        st = min(1.0, alt5 * 1.1 if alt5 >= 0.85 else r1 * 1.3)
        return {"type": "XEN_KE", "strength": round(st, 3), "last": last, "rlen": rlen,
                "alt_rate": alt, "avg_run": avg_run}
    if r2 >= 0.50 and avg_run <= 2.8:
        return {"type": "NHIP_2", "strength": round(r2, 3), "last": last, "rlen": rlen,
                "alt_rate": alt, "avg_run": avg_run}
    if r3 >= 0.42:
        return {"type": "NHIP_3", "strength": round(r3, 3), "last": last, "rlen": rlen,
                "alt_rate": alt, "avg_run": avg_run}
    if rlen >= 4 or (avg_run >= 2.5 and alt <= 0.38):
        st = min(0.9, 0.5 + rlen * 0.08 if rlen >= 4 else 0.5 + (2.5 - alt) * 0.4)
        return {"type": "BET", "strength": round(st, 3), "last": last, "rlen": rlen,
                "alt_rate": alt, "avg_run": avg_run}
    return {"type": "HON_HOP", "strength": 0.5, "last": last, "rlen": rlen,
            "alt_rate": alt, "avg_run": avg_run}


def _cau_weight_adjust(cau: dict, expert_name: str, base_p: float) -> float:
    """Điều chỉnh p của 1 expert dựa vào cầu đã nhận diện.
    Không thay đổi side — chỉ kéo p về 0.5 (giảm ảnh hưởng) hoặc tăng lên.
    Trả p đã điều chỉnh."""
    ctype = cau["type"]
    st    = cau["strength"]   # 0..1
    last  = cau["last"]
    rlen  = cau["rlen"]
    p     = base_p

    if ctype == "XEN_KE":
        # Cầu 1-1: ĐẢO là đúng → boost ĐẢO, damp THEO
        is_theo = (p >= 0.5) == (last == "TAI")  # expert đang theo cầu
        if expert_name in ("HAZARD",):
            # HAZARD thường theo run → damp khi 1-1
            p = 0.5 + (p - 0.5) * max(0.2, 1.0 - st * 0.7)
        elif expert_name in ("CTX", "RUNMIRROR"):
            # CTX và RUNMIRROR đọc context → boost khi cầu rõ
            p = 0.5 + (p - 0.5) * min(1.3, 1.0 + st * 0.4)
        elif expert_name == "MOMENTUM":
            # Momentum theo đà 4p — khi 1-1 đà đảo rất rõ → boost
            p = 0.5 + (p - 0.5) * min(1.25, 1.0 + st * 0.3)
        elif is_theo and expert_name == "REVERSION":
            # Reversion hay bẻ → phù hợp 1-1 → boost
            p = 0.5 + (p - 0.5) * min(1.2, 1.0 + st * 0.25)

    elif ctype in ("NHIP_2", "NHIP_3"):
        L = 2 if ctype == "NHIP_2" else 3
        # Nhịp đều: theo nếu run < L, bẻ nếu run >= L
        should_theo = rlen < L
        is_theo = (p >= 0.5) == (last == "TAI")
        if (should_theo and is_theo) or (not should_theo and not is_theo):
            # Expert đang đúng hướng → boost nhẹ
            p = 0.5 + (p - 0.5) * min(1.2, 1.0 + st * 0.25)
        else:
            # Expert đang ngược → damp
            p = 0.5 + (p - 0.5) * max(0.35, 1.0 - st * 0.5)

    elif ctype == "BET":
        # Bệt: THEO là đúng (trừ khi quá dài) → boost HAZARD/RUNMIRROR, damp ĐẢO
        is_theo = (p >= 0.5) == (last == "TAI")
        overshoot = rlen >= 5  # bệt quá dài → có thể gãy
        if expert_name == "HAZARD":
            # HAZARD đọc lịch sử gãy → ưu tiên khi bệt
            p = 0.5 + (p - 0.5) * min(1.3, 1.0 + st * 0.35)
        elif expert_name == "CTX":
            p = 0.5 + (p - 0.5) * min(1.2, 1.0 + st * 0.2)
        elif not is_theo and not overshoot:
            # Expert bẻ nhưng bệt chưa hết → damp
            p = 0.5 + (p - 0.5) * max(0.3, 1.0 - st * 0.55)

    # HON_HOP: không điều chỉnh, để hội nghị tự cân bằng
    return _clamp(p, 0.38, 0.62)


def _cc_rules(s):
    """Dự đoán của từng luật cho phiên KẾ TIẾP của chuỗi s (None = luật không có ý kiến)."""
    s = s[-120:]; n = len(s); last = s[-1]; out = {}
    runs = _run_lengths(s); cur = runs[-1]
    out["BỆT"] = last
    out["ĐẢO"] = _opp(last)
    done = runs[:-1]
    surv = sum(1 for r in done if r >= cur); end = sum(1 for r in done if r == cur)
    pf = (end + 1.0) / (surv + 2.0)
    out["BỆT_GÃY"] = _opp(last) if pf > 0.56 else (last if pf < 0.44 else None)
    rec = done[-8:]
    if len(rec) >= 4:
        L = max(set(rec), key=lambda v: (rec.count(v), -v))
        if rec.count(L) / len(rec) >= 0.5:
            out["NHỊP_ĐỀU"] = last if cur < L else _opp(last)
    if len(runs) >= 3:
        out["MẪU_LẶP"] = last if cur < runs[-3] else _opp(last)
    for p in (2, 3, 4):
        if n > p: out["CHU_KỲ_%d" % p] = s[-p]
    w12 = s[-12:]
    if len(w12) >= 10:
        t = w12.count("TAI"); r = t / len(w12)
        out["CÂN_BẰNG"] = "XIU" if r >= 0.67 else ("TAI" if r <= 0.33 else None)
    w5 = s[-5:]
    if len(w5) == 5:
        t = w5.count("TAI")
        out["ĐÀ_5"] = "TAI" if t >= 4 else ("XIU" if t <= 1 else None)
    return out

def _cc_tiers(seq, cache):
    """seq: list TAI/XIU. cache: dict {độ dài prefix → luật} (chỉ phụ thuộc quá khứ nên cache an toàn)."""
    n = len(seq)
    if n < 12: return None
    lo = max(8, n - 26)
    for t in range(lo, n + 1):
        if t not in cache: cache[t] = _cc_rules(seq[:t])
    if len(cache) > 140:
        for k in sorted(cache)[:len(cache) - 100]: cache.pop(k, None)
    R = len(CC_RULES); tiers = []
    for name, W in CC_WINDOWS:
        a = max(8, n - W); best = None
        for rule in CC_RULES:
            f = h = 0
            for t in range(a, n):
                v = cache[t].get(rule)
                if v: f += 1; h += 1 if v == seq[t] else 0
            if f < max(4, W // 3): continue
            acc = (h + 1.0) / (f + 2.0)
            if best is None or acc > best[1] or (acc == best[1] and f > best[2]):
                best = (rule, acc, f, h)
        if not best:
            tiers.append({"tang": name, "window": W, "ok": False, "phia": None, "ly_do": "thiếu mẫu"}); continue
        rule, acc, f, h = best
        bias = 0.6 * math.sqrt(math.log(R) / (2.0 * f))        # mức "ăn may" kỳ vọng khi chọn 1 trong R luật
        margin = max(0.0, acc - 0.5 - bias)
        side = cache[n].get(rule)
        tiers.append({"tang": name, "window": W, "ok": side is not None, "luat": rule, "phia": side,
                      "acc": round(acc, 3), "f": f, "h": h, "margin": round(margin, 3),
                      "du_tin": margin > 0.0 and side is not None})
    return tiers

def _cc_decide(seq, cache, own_acc=None):
    """Trả (side, conf_strength 0..1, tiers, ghi_chú, che_do)."""
    tiers = _cc_tiers(seq, cache)
    if tiers is None: return None
    gay = (own_acc is not None and own_acc < 0.42)             # hệ đang gãy → ưu tiên tầng ngắn (đổi nhịp nhanh)
    wt = {"NGẮN": 1.5 if gay else 1.0, "TRUNG": 1.0, "DÀI": 0.8 if gay else 1.0}
    sc = 0.0; tot = 0.0
    for t in tiers:
        if t.get("du_tin"):
            w = wt[t["tang"]] * t["margin"]; tot += w
            sc += w if t["phia"] == "TAI" else -w
    if tot > 0 and abs(sc) > 1e-9:
        side = "TAI" if sc > 0 else "XIU"
        agree = sum(1 for t in tiers if t.get("du_tin") and t["phia"] == side)
        strength = min(1.0, abs(sc) / 0.18) * (0.7 + 0.3 * agree / 3.0)
        return side, strength, tiers, "tầng đủ tin: " + " · ".join(
            "%s %s→%s (%d/%d)" % (t["tang"], t["luat"], t["phia"], t["h"], t["f"]) for t in tiers if t.get("du_tin")), ("GÃY→NGẮN" if gay else "PLAY")
    # không tầng nào vượt mức may rủi → vẫn ra phía theo luật tốt nhất tầng TRUNG/DÀI, độ tin ở đáy
    for pick in ("TRUNG", "DÀI", "NGẮN"):
        t = next((x for x in tiers if x["tang"] == pick and x.get("phia")), None)
        if t:
            return t["phia"], 0.0, tiers, "chưa tầng nào vượt mức may rủi; theo %s %s (%d/%d)" % (pick, t["luat"], t["h"], t["f"]), "THAM_KHẢO"
    return _side_da_so_gan(seq), 0.0, tiers, "không luật nào có ý kiến → đa số phiên gần", "THAM_KHẢO"


# ══════════════════════════════════════════════════════════════════════════════
#  LUẬT ĂN — hệ tự quan sát CHÍNH MÌNH: dự đoán ở mức tin bao nhiêu % thì thực tế ăn bao nhiêu %
#  → gợi ý THEO / BẺ / KHÔNG TIN, kèm khoảng tin cậy Wilson 90% để không kết luận bừa khi mẫu ít.
# ══════════════════════════════════════════════════════════════════════════════
def _wilson(h, n, z=1.645):
    if n <= 0: return 0.0, 1.0
    p = h / n; d = 1 + z * z / n
    c = p + z * z / (2 * n); m_ = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - m_) / d, (c + m_) / d

def _la_goi_y(h, n, min_n=20):
    """Quy tắc duy nhất: chỉ kết luận khi KHOẢNG TIN CẬY nằm hẳn một phía của 50%."""
    if n < min_n: return "CHƯA ĐỦ MẪU", "cần ≥ %d phiên (đang %d)" % (min_n, n)
    lo, hi = _wilson(h, n)
    if lo > 0.5:  return "THEO", "ăn %.0f%% (%d/%d), chắc ≥ %.0f%%" % (h / n * 100, h, n, lo * 100)
    if hi < 0.5:  return "BẺ", "chỉ ăn %.0f%% (%d/%d), chắc ≤ %.0f%% → đánh NGƯỢC lại" % (h / n * 100, h, n, hi * 100)
    return "NGANG MAY RỦI", "ăn %.0f%% (%d/%d), chưa lệch khỏi 50%% — đừng tăng tiền" % (h / n * 100, h, n)

def _la_group(rows, keyf, order=None):
    g = {}
    for r in rows:
        k = keyf(r)
        if k is None: continue
        a = g.setdefault(k, [0, 0]); a[1] += 1; a[0] += 1 if r["win"] else 0
    out = []
    for k in (order or sorted(g)):
        if k not in g: continue
        h, n = g[k]; kq, gc = _la_goi_y(h, n)
        out.append({"nhom": k, "n": n, "an": h, "ty_le": round(h / n * 100, 1), "khuyen_nghi": kq, "ghi_chu": gc})
    return out

# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSIS CORE v25 — ~20 GÓC NHÌN ĐỘC LẬP, CHẤM WALK-FORWARD, KHÔNG PRIOR LỆCH PHÍA
#  Lỗi v24: neo p vào prior 105/216 (=48,6% → luôn nghiêng XỈU). Khi các góc nhìn chưa có
#  trọng số thì p rơi đúng vào prior → dự đoán XỈU mãi (ảnh: 7/7, 8/10 phiên liền XỈU).
#  Lỗi phụ: góc nhìn "không ý kiến" (p=0.5) bị chấm như đoán TÀI.
#  v25: · góc nhìn không ý kiến thì KHÔNG được chấm / không bỏ phiếu
#       · mỗi góc nhìn có điểm tin cậy = độ ăn walk-forward (80 phiên + 30 phiên gần nhất) TRỪ phần ăn may
#       · chưa góc nhìn nào đủ tin → vẫn ra phía theo góc nhìn đang ăn tốt nhất, độ tin ở đáy
#       · hàm thuần: chỉ phụ thuộc lịch sử, không nhớ dự đoán phiên trước
# ══════════════════════════════════════════════════════════════════════════════
_AN_CACHE = {}
_AN_TXT = {"TAI": "T", "XIU": "X"}
_AN_NHOM = {"MARKOV_1": "Xác suất chuỗi", "MARKOV_2": "Xác suất chuỗi", "MARKOV_3": "Xác suất chuỗi",
            "RHYTHM": "Nhịp cầu", "RUN_HAZARD": "Bệt / gãy", "FREQUENCY": "Cân bằng", "REVERSION": "Cân bằng",
            "DA_5": "Đà ngắn", "SUM_BAND": "Tổng điểm", "SUM_REVERT": "Tổng điểm"}

def _an_band(p):
    return 0 if p <= 7 else 1 if p <= 9 else 2 if p == 10 else 3 if p == 11 else 4 if p <= 13 else 5

def _an_features(s, pts):
    """p(Tài) của từng góc nhìn cho phiên kế tiếp + câu giải thích. p=0.5 nghĩa là KHÔNG CÓ Ý KIẾN."""
    n = len(s); out = {}; note = {}
    if n < 6: return out, note
    last = s[-1]; runs = _run_lengths(s); cur = runs[-1]
    def lap(hits, k=1.0): return (hits.count("TAI") + k) / (len(hits) + 2.0 * k)
    # ── chuỗi Markov bậc 1/2/3 ──
    for k in (1, 2, 3):
        if n > k + 3:
            ctx = tuple(s[-k:]); hits = [s[i + k] for i in range(n - k) if tuple(s[i:i + k]) == ctx]
            if len(hits) >= (3 if k < 3 else 4):
                out["MARKOV_%d" % k] = lap(hits)
                note["MARKOV_%d" % k] = "sau %s → Tài %d%% (gặp %d lần)" % ("-".join(_AN_TXT[x] for x in ctx), round(lap(hits) * 100), len(hits))
    # ── nhịp đảo/bệt của 3 bước gần nhất ──
    if n >= 6:
        pat = tuple(1 if s[i] != s[i - 1] else 0 for i in range(n - 3, n)); hits = []
        for i in range(3, n - 1):
            if tuple(1 if s[j] != s[j - 1] else 0 for j in range(i - 2, i + 1)) == pat: hits.append(s[i + 1])
        if len(hits) >= 4:
            out["RHYTHM"] = lap(hits); note["RHYTHM"] = "nhịp %s từng lặp %d lần → Tài %d%%" % ("".join("đ" if x else "b" for x in pat), len(hits), round(lap(hits) * 100))
    # ── bệt gãy theo độ dài run ──
    done = runs[:-1]; surv = sum(1 for r in done if r >= cur); end = sum(1 for r in done if r == cur)
    if surv >= 5:
        pf = (end + 1.0) / (surv + 2.0)                      # xác suất run gãy ở độ dài hiện tại
        out["RUN_HAZARD"] = (1 - pf) if last == "TAI" else pf
        note["RUN_HAZARD"] = "đang bệt %d %s: từng gãy %d/%d lần → gãy %d%%" % (cur, "Tài" if last == "TAI" else "Xỉu", end, surv, round(pf * 100))
    # ── cầu số (hình dạng k run cuối) ──
    pr = []; shp = {k: [] for k in (1, 2, 3, 4, 5)}
    for i, v in enumerate(s):
        if i == 0 or v != s[i - 1]: pr.append(1)
        else: pr[-1] += 1
        if i < n - 1:
            for k in shp:
                if len(pr) >= k: shp[k].append((tuple(min(8, x) for x in pr[-k:]), s[i + 1]))
    for k in shp:
        sh = tuple(min(8, x) for x in runs[-k:]); hits = [y for key, y in shp[k] if key == sh]
        nm = "CAU_" + "-".join(str(x) for x in sh)
        if len(hits) >= 4:
            out[nm] = lap(hits); note[nm] = "cầu %s đã gặp %d lần → Tài %d%%" % ("-".join(str(x) for x in sh), len(hits), round(lap(hits) * 100))
    # ── luật cầu rõ (xen kẽ / chu kỳ / nhịp đều / mẫu lặp) ──
    try: rl = _cc_rules(s)
    except Exception: rl = {}
    lab = {"BỆT": "theo phiên trước", "ĐẢO": "đảo phiên trước", "NHỊP_ĐỀU": "theo nhịp run đều", "MẪU_LẶP": "mẫu x-y-x-y",
           "CHU_KỲ_2": "lặp chu kỳ 2", "CHU_KỲ_3": "lặp chu kỳ 3", "CHU_KỲ_4": "lặp chu kỳ 4"}
    for nm, txt in lab.items():
        v = rl.get(nm)
        if v: out["LUAT_" + nm] = 0.60 if v == "TAI" else 0.40; note["LUAT_" + nm] = "luật %s → %s" % (txt, "Tài" if v == "TAI" else "Xỉu")
    # ── cân bằng / đà ──
    w = s[-24:]; t = w.count("TAI")
    out["FREQUENCY"] = (t + 1.0) / (len(w) + 2.0); note["FREQUENCY"] = "24 phiên gần: %d Tài / %d Xỉu (theo bên nhiều)" % (t, len(w) - t)
    w = s[-20:]
    if len(w) >= 12:
        r = w.count("TAI") / len(w); out["REVERSION"] = 0.5 - 0.30 * (r - 0.5)
        note["REVERSION"] = "20 phiên Tài %d%% → kéo về cân bằng" % round(r * 100)
    w = s[-5:]
    if len(w) == 5:
        t5 = w.count("TAI")
        if t5 >= 4 or t5 <= 1:
            out["DA_5"] = 0.62 if t5 >= 4 else 0.38; note["DA_5"] = "5 phiên gần %d Tài → bám đà" % t5
    # ── tổng điểm (nếu nguồn có xúc xắc) ──
    if pts and len(pts) == n and n >= 20:
        b = _an_band(pts[-1]); hits = [s[i + 1] for i in range(n - 1) if _an_band(pts[i]) == b]
        if len(hits) >= 6:
            out["SUM_BAND"] = lap(hits); note["SUM_BAND"] = "tổng trước %d (nhóm %d): %d lần → Tài %d%%" % (pts[-1], b, len(hits), round(lap(hits) * 100))
        m8 = sum(pts[-8:]) / 8.0
        out["SUM_REVERT"] = max(0.35, min(0.65, 0.5 - 0.05 * (m8 - 10.5)))
        note["SUM_REVERT"] = "tổng TB 8 phiên %.1f (chuẩn 10.5) → %s" % (m8, "hồi Xỉu" if m8 > 10.5 else "hồi Tài")
    return {k: max(0.15, min(0.85, float(v))) for k, v in out.items()}, note

def _an_get(seq, pts, t):
    key = ("".join("T" if x == "TAI" else "X" for x in seq[max(0, t - 100):t]),
           "".join(chr(65 + p % 26) for p in (pts[max(0, t - 100):t] if pts and len(pts) == len(seq) else [])))
    r = _AN_CACHE.get(key)
    if r is None:
        if len(_AN_CACHE) > 6000: _AN_CACHE.clear()
        r = _AN_CACHE[key] = _an_features(seq[max(0, t - 100):t], pts[max(0, t - 100):t] if pts and len(pts) == len(seq) else None)
    return r

def _wf_signal_probs(seq, pts=None):
    """Chấm walk-forward từng góc nhìn: chỉ tính những phiên góc nhìn CÓ ý kiến."""
    seq = list(seq)[-200:]; n = len(seq)
    pts = list(pts)[-200:] if pts else None
    cur, note = _an_get(seq, pts, n)
    lo = max(10, n - 80); R = 22.0; scored = {}
    pre = {t: _an_get(seq, pts, t)[0] for t in range(lo, n)}
    for name, p_now in cur.items():
        h80 = n80 = h30 = n30 = 0; brier = 0.0; psum = 0.0
        for t in range(lo, n):
            v = pre[t].get(name)
            if v is None or abs(v - 0.5) < 0.01: continue
            y = 1.0 if seq[t] == "TAI" else 0.0; ok = (v >= 0.5) == (y == 1.0)
            n80 += 1; h80 += ok; brier += (v - y) ** 2; psum += v
            if t >= n - 30: n30 += 1; h30 += ok
        acc80 = (h80 + 2.0) / (n80 + 4.0) if n80 else 0.5
        acc30 = (h30 + 1.0) / (n30 + 2.0) if n30 else 0.5
        acc = 0.4 * acc80 + 0.6 * acc30                   # nghiêng về gần đây: hệ đổi nhịp nhanh khi 'gãy'
        bias = 0.6 * math.sqrt(math.log(R) / (2.0 * max(n80, 1)))           # mức ăn may khi chọn 1 trong ~20 góc nhìn
        w_strict = max(0.0, acc - 0.5 - bias) if n80 >= 12 else 0.0
        w_soft = max(0.0, acc - 0.5) if n80 >= 12 else 0.0
        scored[name] = {"p": round(p_now, 4), "acc": round(acc, 4), "acc80": round(acc80, 4), "acc30": round(acc30, 4),
                        "n": n80, "n30": n30, "p_tb": round(psum / n80, 4) if n80 else 0.5, "weight": round(w_strict, 4), "w_soft": round(w_soft, 4),
                        "brier": round(brier / n80, 4) if n80 else 0.25,
                        "nhom": _AN_NHOM.get(name) or ("Cầu số" if name.startswith("CAU_") else "Luật cầu" if name.startswith("LUAT_") else "Khác"),
                        "mo_ta": note.get(name, "")}
    try:                                                    # v30: mẫu cầu của thư viện cũng là module, chấm walk-forward như module khác
        for c in (cau_library_pick(seq).get("khop") or []):
            h, n_ = c["hit"], c["n"]; acc_ = (h + 2.0) / (n_ + 4.0)
            scored["CL_" + c["ma"]] = {"p": 0.6 if c["phia"] == "TAI" else 0.4, "acc": round(acc_, 4), "acc80": round(acc_, 4), "acc30": round(acc_, 4),
                "n": n_, "n30": n_, "p_tb": 0.5, "weight": round(max(0.0, c["do_tin_cay_lb"] - 0.5), 4) if n_ >= 12 else 0.0,
                "w_soft": round(max(0.0, acc_ - 0.5), 4) if n_ >= 12 else 0.0, "brier": 0.25, "nhom": "Thư viện cầu", "mo_ta": c["mo_ta"]}
    except Exception: pass
    return scored

def _an_decide(scored, seq):
    """→ (p_out, che_do, side, chi_tiet). Không prior; không nhớ phiên trước."""
    items = [(k, v) for k, v in scored.items() if abs(v["p"] - 0.5) >= 0.01]
    last = seq[-1] if seq else "TAI"
    if not items: return 0.5, "NO_EDGE", _opp(last), []
    W = sum(v["weight"] for _, v in items); soft = False
    if W <= 1e-9:                                           # chưa góc nhìn nào vượt mức may rủi
        soft = True; W = sum(v["w_soft"] for _, v in items)
    key = "w_soft" if soft else "weight"
    if W <= 1e-9:                                           # không ai ăn trên 50% → theo đa số nhẹ, tin = đáy
        _it2 = [x for x in items if x[1]["acc"] >= 0.5] or items      # v30: bỏ module vô giá trị khỏi nhóm đa số
        z = sum(_logit(v["p"]) for _, v in _it2) / len(_it2); mass = 0.0
    else:
        def _pp(v):                                         # chế độ THAM KHẢO: trừ thiên lệch tĩnh (vd luôn nghiêng bên nhiều) để không kẹt 1 phía
            return v["p"] if not soft else max(0.15, min(0.85, v["p"] - (v.get("p_tb", 0.5) - 0.5)))
        z = sum(v[key] * _logit(_pp(v)) for _, v in items) / W
        mass = min(1.0, W / 0.20) * (0.5 if soft else 1.0)
    z_f = z * mass if mass > 0 else z * 0.15
    if abs(z_f) < 1e-9:                                     # hoà tuyệt đối: theo Markov bậc 2→1, cuối cùng đảo phiên trước
        for nm in ("MARKOV_2", "MARKOV_1"):
            if nm in scored and abs(scored[nm]["p"] - 0.5) > 1e-6: z_f = _logit(scored[nm]["p"]) * 1e-3; break
        else: z_f = 1e-3 if last == "XIU" else -1e-3
    p_out = _clamp(_sigmoid(z_f), 0.15, 0.85)
    che = "THAM_KHẢO" if soft else "WF-ENSEMBLE"
    ranked = sorted(items, key=lambda kv: -abs((kv[1][key] if W > 1e-9 else 0.01) * _logit(kv[1]["p"])))
    return p_out, che, ("TAI" if p_out >= 0.5 else "XIU"), ranked


def _cau_phan_tich(seq, scored):
    """Đọc nhiều cầu số hiện tại: THEO, BẺ hoặc THIẾU MẪU."""
    s = list(seq)[-160:]
    if not s:
        return [{"mau": "—", "hanh_dong": "THIẾU MẪU", "p_tai": 0.5, "accuracy": 0.5, "n": 0, "trong_so": 0}
                for _ in range(5)]
    last = s[-1]; runs = _run_lengths(s); out = []
    for k in (1, 2, 3, 4, 5):
        shape = "-".join(str(min(8, int(x))) for x in runs[-k:])
        name = "CAU_" + shape; item = scored.get(name, {})
        p = float(item.get("p", 0.5)); n = int(item.get("n", 0)); acc = float(item.get("acc", 0.5))
        next_side = "TAI" if p >= 0.5 else "XIU"
        action = "THEO" if next_side == last else "BẺ"
        if n < 8 or abs(p - 0.5) < 0.035 or float(item.get("weight", 0)) <= 0:
            action = "THIẾU MẪU"
        out.append({"mau": shape, "hanh_dong": action, "p_tai": round(p, 4),
                    "accuracy": round(acc, 4), "n": n, "trong_so": item.get("weight", 0)})
    return out


def _cau_so(seq, limit=10):
    """Chuỗi cầu chỉ bằng số: 1-1-1, 2-2, 1-2-1..."""
    runs = _run_lengths(list(seq)[-max(1, limit * 3):])
    return "-".join(str(int(x)) for x in runs[-limit:]) if runs else "—"


def luat_an(brain, pk_now=None):
    rows = list(getattr(brain, "calib", []))
    n = len(rows); h = sum(1 for r in rows if r["win"])
    kq, gc = _la_goi_y(h, n)
    res = {"so_phien_do": n, "tong": {"ty_le": round(h / n * 100, 1) if n else None, "khuyen_nghi": kq, "ghi_chu": gc}}
    bk = [(50, 54), (55, 59), (60, 64), (65, 70)]        # khớp dải độ tin CALIBRATED 50–70
    def kb(r):
        for a, b in bk:
            if a <= r["conf"] <= b: return "%d–%d%%" % (a, b)
        return "%d–%d%%" % bk[-1] if r["conf"] > bk[-1][1] else "%d–%d%%" % bk[0]
    res["theo_do_tin"] = _la_group(rows, kb, ["%d–%d%%" % x for x in bk])
    res["nguong"] = []                                   # "khi tin ≥ T% thì ăn bao nhiêu"
    for T in (58, 60, 62, 64, 66, 68, 70):
        sub = [r for r in rows if r["conf"] >= T]
        if len(sub) >= 8:
            hh = sum(1 for r in sub if r["win"]); k2, g2 = _la_goi_y(hh, len(sub))
            res["nguong"].append({"tin_tu": T, "n": len(sub), "ty_le": round(hh / len(sub) * 100, 1), "khuyen_nghi": k2})
    res["theo_che_do"] = _la_group(rows, lambda r: r["che_do"])
    res["theo_so_tang_dong_thuan"] = _la_group(rows, lambda r: "%d/3 tầng" % r["n_tang"], ["0/3 tầng", "1/3 tầng", "2/3 tầng", "3/3 tầng"])
    res["theo_cau"] = _la_group(rows, lambda r: r["regime"])
    res["theo_chuoi_thua"] = _la_group(rows, lambda r: ("sau thắng/đầu" if r["ls"] == 0 else "sau thua 1" if r["ls"] == 1 else "sau thua 2+"),
                                       ["sau thắng/đầu", "sau thua 1", "sau thua 2+"])
    res["theo_luat"] = sorted(_la_group(rows, lambda r: r["luat"]), key=lambda x: -x["n"])[:6]
    res["theo_phia"] = _la_group(rows, lambda r: "dự đoán " + r["side"])
    # mẹo cho phiên HIỆN TẠI: nhóm độ tin + nhóm chế độ đang áp dụng
    if isinstance(pk_now, dict) and pk_now.get("side") in ("TAI", "XIU"):
        cf = int(pk_now.get("confidence") or 0)
        fake = {"conf": cf}
        key = kb(fake); a = next((x for x in res["theo_do_tin"] if x["nhom"] == key), None)
        cd = (pk_now.get("governor") or {}).get("che_do"); b = next((x for x in res["theo_che_do"] if x["nhom"] == cd), None)
        parts = []; vote = []
        for lab, x in (("độ tin " + key, a), ("chế độ " + str(cd), b)):
            if x and x["khuyen_nghi"] in ("THEO", "BẺ"):
                vote.append(x["khuyen_nghi"]); parts.append("%s: %s (%s)" % (lab, x["khuyen_nghi"], x["ghi_chu"]))
            elif x: parts.append("%s: %s" % (lab, x["khuyen_nghi"].lower()))
        if "BẺ" in vote and "THEO" not in vote:   mt = "BẺ"
        elif "THEO" in vote and "BẺ" not in vote: mt = "THEO"
        elif vote:                                mt = "MÂU THUẪN"
        else:                                     mt = "CHƯA RÕ"
        res["meo_hien_tai"] = {"du_doan_he": pk_now["side"], "do_tin": cf, "khuyen_nghi": mt,
                               "danh_cho": (("ĐÁNH NGƯỢC " + _opp(pk_now["side"])) if mt == "BẺ" else ("ĐÁNH THEO " + pk_now["side"]) if mt == "THEO" else "đừng tăng tiền"),
                               "chi_tiet": parts}
    res["luu_y"] = ("Chỉ kết luận THEO/BẺ khi khoảng tin cậy 90% lệch hẳn khỏi 50% và đủ ≥20 phiên. "
                    "Nhiều nhóm cùng xét nên thỉnh thoảng sẽ có nhóm lệch do ngẫu nhiên — ưu tiên nhóm có n lớn, và kiểm tra lại sau vài chục phiên.")
    return res


# ══════════════════════════════════════════════════════════════════════════════
#  CẦU NHANH v31 — NHẬN CẦU TỨC THỜI + THEO/BẺ RÕ RÀNG
#  Vì sao v30 nhận cầu chậm: thư viện cầu phải backtest ~120 phiên, cận Wilson z=2.2 mới dám chọn
#  (cầu mới xuất hiện cần ~15–20 phiên để "được công nhận"), rồi p còn bị kẹp 0.38–0.62 và
#  chìm trong ensemble 80 phiên.
#  Cách mới: mỗi mẫu cầu tự chấm bằng ĐIỂM TRƯỢT — chỉ nhìn ~14 phiên cuối, phiên mới nhất nặng nhất
#  (nửa đời ≈ 3 phiên), cộng "chuỗi đúng liên tiếp" (streak). 3–4 phiên khớp là nhận được cầu;
#  vừa sai liền 2 lần thì bị loại ngay. Kết quả là 1 câu rõ: tên cầu · đang chạy mấy phiên · THEO hay BẺ.
# ══════════════════════════════════════════════════════════════════════════════
def _cn_runs(b):
    r = []
    for x in b:
        if r and r[-1][0] == x: r[-1][1] += 1
        else: r.append([x, 1])
    return r

def _cn_period(q):
    """Cầu theo run: độ dài run đích = độ dài run cách q nhịp trước. q=1: 1-1, 2-2, 3-3…; q=2: 3-1-3-1, 2-1-2-1…"""
    def f(b):
        R = _cn_runs(b)
        if len(R) < q + 2: return None
        cur = R[-1][1]; T = R[-1 - q][1]
        if R[-1 - q][1] != R[-1 - 2 * q][1] if len(R) > 2 * q else False:   # run đích phải từng lặp (đã có ≥2 chu kỳ)
            return None
        if len(R) <= 2 * q: return None
        return b[-1] if cur < T else 1 - b[-1]
    return f

def _cn_bet(b):
    R = _cn_runs(b); L = R[-1][1]
    return b[-1] if 2 <= L <= 5 else None

def _cn_chuky(k):
    def f(b):
        if len(b) < 2 * k + 1 or b[-k:] != b[-2 * k:-k]: return None
        return b[-k]
    return f

def _cn_guong(m):
    def f(b):
        if len(b) < 2 * m + 1 or b[-m:] != b[-2 * m:-m][::-1]: return None
        return b[-2 * m - 1]
    return f

def _cn_trend(d):
    def f(b):
        R = [x[1] for x in _cn_runs(b)]
        if len(R) < 3 or R[-3] + d != R[-2]: return None
        T = R[-2] + d
        return None if T < 1 else (b[-1] if R[-1] < T else 1 - b[-1])
    return f

_CN_TPL = [
    ("BỆT", "bệt", _cn_bet),
    ("1-1", "xen kẽ 1-1", _cn_period(1)),         # run đích = run trước: tự thích nghi 1-1 / 2-2 / 3-3
    ("A-B", "cầu 2 nhịp lặp (vd 3-1-3-1, 2-1-2-1)", _cn_period(2)),
    ("A-B-C", "cầu 3 nhịp lặp", _cn_period(3)),
] + [("CK%d" % k, "chu kỳ %d phiên" % k, _cn_chuky(k)) for k in (2, 3, 4, 5, 6)] \
  + [("GƯƠNG%d" % m, "cầu gương %d" % m, _cn_guong(m)) for m in (3, 4)] \
  + [("TĂNG", "run tăng dần", _cn_trend(1)), ("GIẢM", "run giảm dần", _cn_trend(-1))]

def _cn_name(code, b):
    R = [x[1] for x in _cn_runs(b)]
    if code == "1-1":
        T = R[-2] if len(R) >= 2 else 1
        return "Cầu %d-%d" % (T, T)
    if code == "A-B" and len(R) >= 3:
        x, y = sorted((R[-3], R[-2]), reverse=True); return "Cầu %d-%d" % (x, y)
    if code == "A-B-C" and len(R) >= 4: return "Cầu %s" % "-".join(str(v) for v in R[-4:-1])
    if code == "BỆT": return "Bệt %d" % R[-1]
    if code.startswith("CK"):
        k = int(code[2:]); rr = [x[1] for x in _cn_runs(b[-k:])]
        return "Cầu %s (chu kỳ %d)" % ("-".join(str(v) for v in rr), k)
    return dict((c, n) for c, n, _ in _CN_TPL).get(code, code).capitalize()

def cau_nhanh(seq, K=14, decay=0.78, smin=3, s2diem=0.7, dmin=0.58):
    """Nhận cầu NGAY: trả {cau:{ten,ma,phia,hanh_dong,streak,diem,do_ro,trang_thai,mo_ta}, ung_vien:[...]} hoặc cau=None."""
    b = [1 if s == "TAI" else 0 for s in seq[-120:]]
    n = len(b)
    if n < 6: return {"cau": None, "ung_vien": [], "nhan": "chưa đủ phiên"}
    cands = []
    for code, lab, fn in _CN_TPL:
        now = fn(b)
        if now is None: continue
        w = 1.0; sw = sh = 0.0; streak = 0; broken = False; fired = 0; hits = 0; last2 = []
        for age in range(K):
            t = n - 1 - age
            if t < 6: break
            pr = fn(b[:t])
            if pr is None: continue
            ok = (pr == b[t]); fired += 1; hits += ok
            sw += w; sh += w * ok; w *= decay
            if age == len(last2) and ok and not broken: streak += 1
            else: broken = True
            last2.append(ok)
        if fired < 2: continue
        diem = (sh + 0.8) / (sw + 1.6)                       # Laplace trên số đếm có trọng số
        sai_gan = (len(last2) >= 2 and not last2[0] and not last2[1])
        sai_moi = (len(last2) >= 1 and not last2[0])
        cands.append({"ma": code, "ten": _cn_name(code, b), "phia": "TAI" if now else "XIU",
                      "hanh_dong": "THEO" if now == b[-1] else "BẺ", "streak": streak, "hit": hits, "n": fired,
                      "diem": round(diem, 3), "sai_moi": sai_moi, "sai_gan": sai_gan})
    # lọc: phải có bằng chứng GẦN ĐÂY
    ok_c = [c for c in cands if not c["sai_gan"] and c["diem"] >= dmin and (c["streak"] >= smin or (c["streak"] >= 2 and c["diem"] >= s2diem))]
    ok_c.sort(key=lambda c: (c["diem"] + 0.03 * min(c["streak"], 6) - (0.25 if c["sai_moi"] else 0.0), c["streak"], c["n"]), reverse=True)  # vừa sai → nhường cầu mới
    out = {"cau": None, "ung_vien": ok_c[1:4], "tat_ca": len(cands)}
    if not ok_c:
        out["nhan"] = "chưa thấy cầu rõ (ngẫu nhiên / đang chuyển cầu)"; return out
    c = dict(ok_c[0])
    c["do_ro"] = round(min(1.0, max(0.0, (c["diem"] - 0.55) / 0.35 * (0.6 + 0.1 * min(c["streak"], 4)))), 3)
    c["trang_thai"] = ("RÕ" if (c["streak"] >= 4 and c["diem"] >= 0.8) else "ĐANG CHẠY" if c["streak"] >= 3 else "MỚI HÌNH THÀNH")
    if c["sai_moi"]: c["trang_thai"] = "VỪA LỆCH 1 NHỊP"; c["do_ro"] = round(c["do_ro"] * 0.5, 3)
    c["mo_ta"] = "%s · chạy %d phiên liền (đúng %d/%d gần đây)" % (c["ten"], c["streak"], c["hit"], c["n"])
    out["cau"] = c
    out["nhan"] = "%s → %s %s" % (c["mo_ta"], c["hanh_dong"], "TÀI" if c["phia"] == "TAI" else "XỈU")
    return out


class Brain:
    def __init__(self):
        self.engine = _Core()
        self.history = deque(maxlen=500)
        self.points  = deque(maxlen=500)
        self._seen_ids = set()
        self._last_prediction = None
        self._stick_side = None
        self._p_ema = None
        self._cc_cache = {}
        self.last_cycle = None
        self.loss_streak = 0
        self.win_streak  = 0
        self.hit = deque(maxlen=30)
        self.pred_sides = deque(maxlen=30)
        self.calib = deque(maxlen=400)      # nhật ký tự quan sát: (độ tin, chế độ, ... → thắng/thua)

    def observe(self, row):
        """Nuôi dữ liệu phiên. Chấp nhận phiên thiếu điểm (nguồn chỉ có kết quả)."""
        if not isinstance(row, dict):
            return False
        try:
            sid = int(row.get("id"))
        except (TypeError, ValueError):
            return False
        result = str(row.get("result", "")).strip().upper()
        if sid in self._seen_ids or result not in ("TAI", "XIU"):
            return False
        self._seen_ids.add(sid)
        point = None
        try:
            point = int(row.get("point"))
            if not 3 <= point <= 18:
                return False
        except (TypeError, ValueError):
            pass
        self.history.append(1 if result == "TAI" else 0)
        if point is not None:
            self.points.append(point)
            self.engine.push([{"result": result, "point": point,
                               "dices": row.get("dices", [])}])
        else:
            self.engine.push([{"result": result, "point": None, "dices": []}])
        return True

    # ── độ tin CALIBRATED — hết thời "rải đều 58–72%" ──
    def _conf_final(self, p_out: float, n_seq: int):
        """Trả (conf, che_do). Nguyên tắc: số hiển thị phải xứng với tỉ lệ ăn
        THẬT mà hệ đã tự đo trên chính dự đoán của nó (khoảng tin cậy Wilson
        90% trên nhật ký calib). Không có bằng chứng => không được phồng."""
        raw = 100.0 * max(p_out, 1.0 - p_out)            # 50..85 theo ensemble
        # 1) ensemble không lệch khỏi 50/50 đủ nghĩa => NO_EDGE, nói thẳng
        if abs(p_out - 0.5) < 0.02:
            return 50, "NO_EDGE"
        # 2) chưa đủ dữ liệu tự quan sát => trần 55%, chưa chứng minh được gì
        hits = list(self.hit)
        n_ev = len(hits)
        if n_seq < 12 or n_ev < 20:
            return max(50, min(55, int(round(raw)))), "WARMUP"
        # 3) đủ mẫu: trần hiển thị bám theo Wilson lower bound của tỉ lệ ăn thật
        #    (ăn 50% → 52; ăn 55% → ~54; ăn 60% → ~58; ăn 65% → ~62; ăn 70% → ~66)
        lo, _hi = _wilson(sum(hits), n_ev)
        cap = 50.0 + 40.0 * max(0.0, lo - 0.5) * 2.0
        cap = min(max(cap, 52.0), float(_SC_CONF_HI))
        conf = int(round(min(cap, max(50.0, raw))))
        return max(_SC_CONF_LO, conf), "WF-ENSEMBLE"

    # ── lõi dự đoán ──
    def predict(self):
        """v27: Dự đoán phiên kế tiếp. CauAdapter đọc cầu → điều chỉnh p_out sau ensemble."""
        seq = list(self.engine.seq); sums_h = list(self.engine.sums)
        acc, n_ev = self._eval(); last, rlen = _last_run(seq) if seq else ("", 0)
        pts = list(self.points) if len(self.points) == len(seq) else None
        sig = _wf_signal_probs(seq, pts)
        p_out, che_do_conf, pred, ranked = _an_decide(sig, seq)

        # ── v31: CẦU NHANH — nhận cầu tức thời, là động cơ CHÍNH khi thấy cầu; ensemble làm nền ──
        cau_now = _read_cau_now(seq) if len(seq) >= 6 else None
        _cau_adj_note = ""
        try: cau_pick = cau_library_pick(seq)
        except Exception: cau_pick = None
        try: cn = cau_nhanh(seq)
        except Exception: cn = {"cau": None, "ung_vien": [], "nhan": "lỗi"}
        _c = cn.get("cau")
        if _c:
            tgt = 0.5 + 0.06 + 0.12 * _c["do_ro"]                     # 0.56 … 0.68 nghiêng về phía cầu
            tgt = tgt if _c["phia"] == "TAI" else 1.0 - tgt
            al = 0.45 + 0.45 * _c["do_ro"]                            # cầu càng rõ càng lấn ensemble
            if _c["trang_thai"] == "MỚI HÌNH THÀNH": al = min(al, 0.55)
            if _c["trang_thai"] == "VỪA LỆCH 1 NHỊP": al = min(al, 0.30)
            p_out = _clamp(p_out * (1 - al) + tgt * al, 0.25, 0.75)
            _cau_adj_note = "[CẦU %s: %s %s]" % (_c["ten"], _c["hanh_dong"], "TÀI" if _c["phia"] == "TAI" else "XỈU")
        else:                                                         # chưa nhận ra cầu tức thời → dùng cầu đã kiểm chứng của thư viện (bậc 2)
            _cc = (cau_pick or {}).get("cau_chon")
            if _cc and (_cc.get("muc") == "ĐÁNG_TIN" or (_cc.get("ti_le", 0) >= 0.62 and _cc.get("n", 0) >= 8)):
                _t = 0.5 + min(0.12, max(0.05, (_cc["do_tin_cay_lb"] - 0.5) * 0.9 + 0.05))
                _al = 0.6 if _cc["muc"] == "ĐÁNG_TIN" else 0.4
                p_out = _clamp(p_out * (1 - _al) + (_t if _cc["phia"] == "TAI" else 1 - _t) * _al, 0.3, 0.7)
                _cau_adj_note = "[Cầu kiểm chứng %s: %s %s]" % (_cc["ten"], _cc["hanh_dong"], "TÀI" if _cc["phia"] == "TAI" else "XỈU")
        try: _us = None if (_c and _c["trang_thai"] in ("RÕ", "ĐANG CHẠY")) else cau_unstick(self.pred_sides, self.hit, seq, cau_pick)
        except Exception: _us = None
        if _us:
            p_out = 0.57 if _us[0] == "TAI" else 0.43
            _cau_adj_note = (_cau_adj_note + " " if _cau_adj_note else "") + "[GỠ KẸT: %s]" % _us[1]
        pred = "TAI" if p_out >= 0.5 else "XIU"
        # ─────────────────────────────────────────────────────────────────────

        conf, che_c2 = self._conf_final(p_out, len(seq))
        if che_do_conf == "WF-ENSEMBLE": che_do_conf = che_c2
        elif che_c2 == "NO_EDGE": che_do_conf = "NO_EDGE"
        w12 = seq[-12:]
        alt = sum(1 for i in range(1, len(w12)) if w12[i] != w12[i - 1]) / max(1, len(w12) - 1)
        regime = "ĐẢO" if alt >= 0.62 else "BỆT" if alt <= 0.38 else "LẪN"
        max_run12 = max(_run_lengths(w12)) if w12 else 1
        cau_loan = bool(len(w12) >= 8 and alt >= 0.58 and max_run12 <= 2)
        try:
            tiers = _cc_tiers(seq, self._cc_cache) or []
        except Exception:
            tiers = []
        try:
            mr = cau_multi_consensus(seq)
            khung_rows = mr[2] if isinstance(mr, tuple) and len(mr) >= 3 and isinstance(mr[2], list) else []
        except Exception:
            khung_rows = []
        sides = {name: ("TAI" if x["p"] >= 0.5 else "XIU") for name, x in sig.items()}
        votes = {name: x["acc"] for name, x in sig.items()}
        strength = round(abs(p_out - 0.5) * 2.0, 4)
        cau_so = _cau_so(seq)
        cau_reads = _cau_phan_tich(seq, sig)
        cau_detail = " · ".join("%s:%s p=%.1f%% n=%d" % (x["mau"], x["hanh_dong"], x["p_tai"] * 100, x["n"])
                                for x in cau_reads if x["hanh_dong"] != "THIẾU MẪU") or "cầu số chưa đủ mẫu"
        n_tai = sum(1 for _, v in ranked if v["p"] >= 0.5); n_xiu = len(ranked) - n_tai
        def _fmt(kv):
            k, v = kv
            return "%s (%s) ăn %d%%/%d" % (v.get("mo_ta") or k, "Tài" if v["p"] >= 0.5 else "Xỉu", round(v["acc"] * 100), v["n"])
        side_v = [kv for kv in ranked if (kv[1]["p"] >= 0.5) == (pred == "TAI")][:3]
        opp_v = [kv for kv in ranked if (kv[1]["p"] >= 0.5) != (pred == "TAI")][:1]
        detail = "%d/%d góc nhìn nghiêng %s · ủng hộ: %s" % (n_tai if pred == "TAI" else n_xiu, len(ranked), "TÀI" if pred == "TAI" else "XỈU", "; ".join(_fmt(kv) for kv in side_v) or "—")
        if opp_v: detail += " · ngược: " + _fmt(opp_v[0])
        goc_nhin = [{"ten": k, "nhom": v["nhom"], "phia": "TAI" if v["p"] >= 0.5 else "XIU", "p_tai": v["p"], "acc": v["acc"], "n": v["n"],
                     "trong_so": v["weight"], "mo_ta": v["mo_ta"]} for k, v in ranked[:14]]
        tier_agree = sum(1 for t in tiers if t.get("phia") == pred)
        strength = round(abs(p_out - 0.5) * 2.0, 4)
        cyc = {"da_du_du_lieu": len(seq) >= 12, "tangs": [
            {"tang": t["tang"], "window": t["window"], "trang_thai": "OK" if t.get("phia") else "THIẾU",
             "chu_ky": t.get("luat"), "vanh": t.get("luat"), "phia": t.get("phia"),
             "do_manh": t.get("margin", 0.0), "acc": t.get("acc"), "run_hien_tai": rlen,
             "mo_ta": "%s: %s → %s (%s/%s phiên ăn)" % (t["tang"], t.get("luat"), t.get("phia"), t.get("h"), t.get("f"))}
            for t in tiers], "side": pred, "p_tai": round(p_out, 4),
            "dong_thuan": tier_agree, "so_tang_chot": len([t for t in tiers if t.get("du_tin")]),
            "cau_so": cau_so, "cau_phan_tich": cau_reads, "goc_nhin": goc_nhin,
            "mo_ta": "cầu " + cau_so + " · " + detail}
        self.last_cycle = cyc
        pl, nhom = self._pl_nhom(sum_h=sums_h[-1] if sums_h else None, run_len=rlen)
        result = {
            "side": pred, "confidence": conf, "p_tai": round(p_out, 4),
            "reasoning": "%s %d%% | %s | p(Tài)=%.1f%% | cầu số %s | %s%s" % (pred, conf, (cn.get("nhan") or "chưa thấy cầu rõ"), p_out * 100, cau_so, detail, " " + _cau_adj_note if _cau_adj_note else ""),
            "cau_now": cau_now, "cau_nhanh": cn,
            "cau_chon": cau_pick, "module": cau_module_report(sig),
            "experts": {n: x["weight"] for n, x in sig.items()}, "expert_votes": votes,
            "expert_sides": sides, "signal_detail": sig, "cau_so": cau_so,
            "cau_phan_tich": cau_reads, "goc_nhin": goc_nhin,
            "forced_skip": False, "cau_loan": cau_loan, "dong_thuan_chu_ky": tier_agree,
            "regime": regime, "khung_da_phien": khung_rows, "chu_ky_3_tang": cyc,
            "loss_streak": self.engine.loss_streak, "run_len": rlen, "acc30": acc,
            "total_signals": len([x for x in sig.values() if x["weight"] > 0]),
            "models_voted_tai": sum(1 for x in sig.values() if x["weight"] > 0 and x["p"] >= 0.5),
            "models_voted_xiu": sum(1 for x in sig.values() if x["weight"] > 0 and x["p"] < 0.5),
            "evaluation": self._evaluation(n_ev, acc), "baseline_side": None, "baseline_p_tai": None,
            "pl": pl, "nhom": nhom, "hard_reset": False, "inverse_mode": False,
            "governor": {"che_do": che_do_conf, "suc_manh": strength, "acc30": acc,
                         "ly_do": "backtest walk-forward, không dùng dữ liệu tương lai; trần độ tin bám Wilson 90% trên tự quan sát; " + detail},
            "no_edge": che_do_conf == "NO_EDGE",
        }
        self._stick_side = pred; self._last_prediction = result
        return result

    # ── học sau mỗi phiên ──
    def learn(self, pk, y: bool):
        if not isinstance(pk, dict) or pk.get("side") not in ("TAI", "XIU"):
            return
        actual = "TAI" if y else "XIU"
        won = pk["side"] == actual
        try:
            _tg = ((pk.get("chu_ky_3_tang") or {}).get("tangs") or [])
            _lu = next((t.get("chu_ky") for t in _tg if t.get("tang") == "TRUNG" and t.get("chu_ky")), None) or "—"
            self.calib.append({"conf": int(pk.get("confidence") or 0), "che_do": (pk.get("governor") or {}).get("che_do") or "—",
                               "n_tang": int(pk.get("dong_thuan_chu_ky") or 0), "regime": pk.get("regime") or "—",
                               "ls": int(self.loss_streak), "luat": _lu, "side": pk["side"], "win": bool(won)})
        except Exception:
            pass
        self.engine.update(pk["side"], actual, pk)
        self.hit.append(1 if won else 0)
        self.pred_sides.append(pk["side"])
        self.loss_streak = 0 if won else self.loss_streak + 1
        self.win_streak  = 1 if won else 0

    def _run_len(self):
        return len(self.engine.seq) and _last_run(list(self.engine.seq))[1] or 0

    def _eval(self):
        hits = list(self.hit)
        if not hits:
            return None, 0
        return round(sum(hits) / len(hits), 4), len(hits)

    def _evaluation(self, n_ev, acc):
        return {"n": n_ev,
                "accuracy_30": acc,
                "random_baseline": 0.5,
                "has_evidence": n_ev >= 20,
                "warning": ("Chưa đủ dữ liệu" if n_ev < 20 else None)}

    def _pl_nhom(self, sum_h=None, run_len=0):
        so_phien = len(self.engine.seq)
        nhom = ("L" if (sum_h is not None and sum_h <= 9)
                else "M" if (sum_h is not None and sum_h <= 11) else "H") \
            if sum_h is not None else None
        acc, _ = self._eval()
        pl = {"so_phien": so_phien, "tong_truoc": sum_h, "nhom": nhom,
              "bệt": run_len, "p_tai_diem": None, "p_tai_nhom": None}
        nhom_b = {"loss_streak": self.engine.loss_streak,
                  "hard_reset": False,
                  "loss_tu_hoc": (round(1.0 - acc, 4) if acc is not None else None),
                  "loss_thuat_toan": None}
        return pl, nhom_b

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY + REPLAY — giữ nguyên hợp đồng cũ
# ══════════════════════════════════════════════════════════════════════════════
def entry(row, pk, win, live=False):
    """Một dòng lịch sử: phiên đã ra + dự đoán đã đưa ra cho phiên đó."""
    du = pk.get("side") if isinstance(pk, dict) else None
    if du not in ("TAI", "XIU"):
        status = "skip"
    else:
        status = "win" if win else "lose"
    return {"phien": row["id"], "du_doan": du, "ket_qua": row["result"],
            "xuc_xac": list(row.get("dices") or []), "tong": row["point"],
            "trang_thai": status, "icon": ICON.get(status, ""),
            "live": bool(live),
            "conf": pk.get("confidence") if isinstance(pk, dict) else None}

REPLAY_WARMUP = 12   # số phiên tối thiểu trước khi bắt đầu chấm điểm lại

def replay(rows):
    """Dựng lại Brain từ danh sách phiên cũ: dự đoán TRƯỚC, học SAU (giống lúc
    chạy thật). Trailing (predict → observe → learn)."""
    brain = Brain()
    entries = []
    for row in rows:
        if len(brain.history) >= REPLAY_WARMUP:
            try:
                pk = brain.predict()
            except Exception:
                pk = None
            if isinstance(pk, dict) and pk.get("side") in ("TAI", "XIU"):
                win = pk["side"] == row["result"]
                brain.observe(row)
                brain.learn(pk, row["result"] == "TAI")
                entries.append(entry(row, pk, win, False))
            else:
                brain.observe(row)
        else:
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
            if isinstance(rows, list):
                good = [x for x in rows if isinstance(x, dict) and (SHOW_REPLAY or x.get("live"))]
                self.hist = deque(good[-HIST_MAX:], maxlen=HIST_MAX)
        except (OSError, ValueError, TypeError): self.hist = deque(maxlen=HIST_MAX)

    def hist_list(self):
        for _ in range(6):
            try: return list(self.hist)
            except RuntimeError: time.sleep(0.005)
        return []

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
            rolled_back = bool(self.ready and newest < self.last_id)   # ID nguồn bị reset → lịch sử cũ vô nghĩa
            self.brain, replay_entries = replay(rows)
            if rolled_back:
                self.hist.clear(); self.save_history()
            if SHOW_REPLAY and replay_entries:
                have = {h.get("phien") for h in self.hist}
                add = []
                for e in replay_entries[-HIST_MAX:]:
                    if e.get("phien") not in have: e["replay"] = True; add.append(e)
                if add:
                    merged = sorted(list(self.hist) + add, key=lambda h: h.get("phien") or 0)[-HIST_MAX:]
                    self.hist = deque(merged, maxlen=HIST_MAX); self.save_history()
            self.last = {"phien": newest, "xuc_xac": rows[-1]["dices"], "tong": rows[-1]["point"], "ket_qua": rows[-1]["result"], "du_doan": None, "trang_thai": "khong"}
            self.last_id = newest; self.ready = True; self._pend(); return

        for row in (r for r in rows if r["id"] > self.last_id):
            pd = self.pending
            is_live = bool(pd and pd["phien"] == row["id"])
            pk = pd["pk"] if is_live else self.brain.predict()
            du = pk.get("side") if isinstance(pk, dict) else None
            valid_prediction = du in ("TAI", "XIU")
            win = (du == row["result"]) if valid_prediction else None
            # FIX v17: observe TRƯỚC (nạp kết quả thực vào engine), rồi mới learn
            # Trước đây: learn → observe → loss_streak tính sai vì seq chưa có phiên mới
            self.brain.observe(row)
            if valid_prediction:
                self.brain.learn(pk, row["result"] == "TAI")
            if is_live:
                self.hist.append(entry(row, pk, win, True)); self.save_history()
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
    # FIX BUG#1: guard None — t.last / t.pending có thể chưa được nạp (trước lần refresh đầu)
    last = t.last or {}
    pd   = t.pending or {}
    if not last:
        return {"ok": True, "ban": t.name, "phien_truoc": None,
                "phien_hien_tai": None, "lich_su": [],
                "thong_ke": stats(t.hist_list()), "cap_nhat": now_iso(),
                "canh_bao": "Chưa có dữ liệu phiên đầu tiên"}
    items = t.hist_list()
    if items and last and items[-1].get("phien") == last.get("phien"): items = items[:-1]
    phien_truoc = {"phien": last.get("phien"), "xuc_xac": last.get("xuc_xac"), "tong": last.get("tong"), "ket_qua": last.get("ket_qua"), "du_doan": last.get("du_doan"), "trang_thai": last.get("trang_thai"), "icon": ICON.get(last.get("trang_thai"), "")}
    prediction_side = pd.get("du_doan")
    phien_hien_tai = {
        "phien": pd.get("phien"),
        "du_doan": prediction_side,
        "do_tin_cay": pd.get("do_tin_cay"),
        "trang_thai": "TÁC ĐỘNG (auto)" if prediction_side else "CHỜ",
        "cau_loan": bool((pd.get("pk") or {}).get("cau_loan")),
        "dong_thuan_chu_ky": (pd.get("pk") or {}).get("dong_thuan_chu_ky"),
        "cau": _cau_number_sequence(t.brain),
        "cau_chon": (pd.get("pk") or {}).get("cau_chon"), "module": (pd.get("pk") or {}).get("module"),
        "ket_qua": None,
        "icon": "🔴" if prediction_side == "TAI" else "🔵" if prediction_side == "XIU" else "—",
        "cap_nhat": now_iso(),
    }
    lich_su = [{"phien": h["phien"], "du_doan": h["du_doan"], "ket_qua": h["ket_qua"], "trang_thai": h["trang_thai"], "icon": h["icon"]} for h in items[-5:][::-1]]
    res = {"ok": True, "ban": t.name, "phien_truoc": phien_truoc, "phien_hien_tai": phien_hien_tai, "lich_su": lich_su, "thong_ke": stats(t.hist_list()), "cap_nhat": now_iso()}
    if t.err: res["canh_bao"] = "Nguồn dữ liệu lỗi, đang dùng dữ liệu gần nhất"
    try: res["cau_nhanh"] = ((pd or {}).get("pk") or {}).get("cau_nhanh")
    except Exception: pass
    try: res["goc_nhin"] = ((pd or {}).get("pk") or {}).get("goc_nhin")
    except Exception: pass
    try: res["luat_an"] = luat_an(t.brain, (pd or {}).get("pk"))
    except Exception: pass
    if pd and pd.get("pk"):
        pkd = pd["pk"]; pl = pkd.get("pl") or {}; nh = pkd.get("nhom") or {}
        res["tu_hoc"] = {"cua_so": 50, "so_phien": pl.get("so_phien"), "tong_truoc": pl.get("tong_truoc"), "nhom_tong": pl.get("nhom"), "bet": pl.get("bệt"), "p_tai_tu_diem": pl.get("p_tai_diem"), "p_tai_theo_nhom": pl.get("p_tai_nhom"), "acc30": pkd.get("acc30"), "loss_tu_hoc": nh.get("loss_tu_hoc"), "loss_thuat_toan": nh.get("loss_thuat_toan"), "trong_so_tu_hoc": 1.0, "governor": pkd.get("governor"), "evaluation": pkd.get("evaluation")}
    return res

def view_history(t, limit):
    items = t.hist_list()[::-1][:limit]
    return {"ok": True, "ban": t.name, "tong": len(items), "thong_ke": stats(t.hist_list()), "cap_nhat": now_iso(), "lich_su": [{"phien": h["phien"], "du_doan": h["du_doan"], "ket_qua": h["ket_qua"], "xuc_xac": h["xuc_xac"], "tong": h["tong"], "trang_thai": h["trang_thai"], "icon": h["icon"], "live": h["live"]} for h in items]}

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
CAU_WINDOWS = (4, 13, 24)
# Muốn đổi bộ khung không cần sửa code: set env CAU_WINDOWS=5,12,30
try:
    _w_env = [int(x) for x in os.getenv("CAU_WINDOWS", "4,13,24").split(",") if x.strip()]
    if len(_w_env) >= 3 and all(2 <= x <= 200 for x in _w_env):
        CAU_WINDOWS = tuple(sorted(set(_w_env))[:5])
except Exception:
    pass
CAU_WINDOWS_LABEL = "/".join(str(x) for x in CAU_WINDOWS) + "p"

def cau_multi_consensus(seq, windows=CAU_WINDOWS):
    """v17.1 — Hợp nhất dự báo đa khung (mặc định 4/13/24) + CỔNG CONVICTION.
    Cải tiến: khi khung ngắn (5p) mâu thuẫn rõ với khung dài (30p) + regime shift
    → giảm trọng số khung dài để không bị kéo ngược bởi cầu cũ.
    Trả về (p_tai_hop_nhat, mo_ta_ngan, bang_chi_tiet_tung_khung)."""
    # v17.1: phát hiện regime shift — để điều chỉnh trọng số khung
    _shift, _shift_str = _detect_regime_shift(seq, recent_n=8, old_n=20)

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
        # Trọng số gốc: khung lệch mạnh tin hơn
        ws = 0.5 + z["do_manh"]
        # v17.1: khi cầu vừa chuyển nhịp → khung dài mang thông tin cầu cũ → giảm ws
        if _shift and w >= 20:
            ws *= max(0.3, 1.0 - _shift_str * 0.6)
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
    # v17.1: khi có regime shift mạnh, nới lỏng điều kiện 1 chút:
    #   chỉ cần 1 khung lệch mạnh (thay vì 2) VÀ cùng hướng với tín hiệu gần nhất
    _strong = [r for r in rows if r["do_manh"] >= 0.22]
    _sides = {(1 if r["p_tai"] >= 0.53 else -1 if r["p_tai"] <= 0.47 else 0) for r in _strong}

    # Ngưỡng đồng thuận: mặc định cần 2 khung mạnh; shift mạnh → 1 khung đủ
    _min_strong = 1 if (_shift and _shift_str > 0.5) else 2

    if len(rows) < len(windows) or len(_strong) < _min_strong or len(_sides) != 1:
        _thieu = "" if len(rows) == len(windows) else f" ({len(rows)}/{len(windows)} khung đủ mẫu)"
        _nho = "" if len(_strong) >= _min_strong else f" · lệch mạnh <{_min_strong} khung"
        _nen = " · khung mạnh ngược nhau" if len(_sides) > 1 else ""
        _shn = f" [SHIFT {_shift_str:.0%}]" if _shift else ""
        return 0.5, f"MULTIW chờ tín hiệu{_thieu}{_nho}{_nen}{_shn}", rows
    _shn = f" [SHIFT {_shift_str:.0%}→giảm w30p]" if _shift else ""
    tag = (f"{len(rows)} khung {CAU_WINDOWS_LABEL}: "
           f"TÀI {tai_c} · XỈU {xiu_c} · trung tính {len(rows)-tai_c-xiu_c} → nghiêng {p_out:.0%}{_shn}")
    return p_out, tag, rows

def analyze_cau(seq):
    """Phân tầng cầu NGẮN (3-5 phiên) / TRUNG (6-15) / DÀI (>15)
    + BẢNG 3 TẦNG KHUNG (mặc định 4/13/24) + nhận dạng + khuyến nghị."""
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
    # Đa khung: 3 tầng khung chốt (mặc định 4/13/24)
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

def _detect_regime_shift(seq, recent_n=8, old_n=20):
    """v17.1: Phát hiện cầu vừa chuyển loại trong `recent_n` phiên gần nhất
    so với `old_n` phiên trước đó. Trả (shifted: bool, shift_strength: 0..1).
    Dùng để giảm trọng số của cửa sổ dài khi cầu vừa đổi nhịp."""
    # Tự điều chỉnh old_n khi seq ngắn — cần ít nhất recent_n + 6 phiên
    actual_old = min(old_n, max(6, len(seq) - recent_n))
    if len(seq) < recent_n + 6:
        return False, 0.0
    recent = seq[-recent_n:]
    old    = seq[-(recent_n + actual_old):-recent_n]
    # So sánh tỷ lệ đảo chiều (volatility) giữa hai vùng
    def _alt_rate(s):
        if len(s) < 2: return 0.5
        return sum(1 for i in range(1, len(s)) if s[i] != s[i-1]) / (len(s) - 1)
    r_alt = _alt_rate(recent); o_alt = _alt_rate(old)
    delta = abs(r_alt - o_alt)
    # Cầu chuyển loại mạnh nếu tỷ lệ đảo chiều thay đổi >25%
    shifted = delta > 0.25
    return shifted, min(1.0, delta * 3.0)

def _cycle_layer(seq, window, tag, cap_lag=6):
    """v17.1 — Đọc 1 tầng chu kỳ trên `window` phiên gần nhất.
    Cải tiến: phát hiện regime shift → giảm ảnh hưởng của cửa sổ dài
    khi cầu vừa đổi nhịp, tránh bị kéo lùi bởi cầu cũ."""
    w = seq[-window:]
    n = len(w)
    if n < 8:
        return {"tang": tag, "window": window, "so_phien": n, "trang_thai": "THIẾU_DỮ_LIỆU",
                "p_tai": None, "do_manh": 0.0, "mo_ta": tag + ": cần ≥ 8 phiên"}

    # v17.1: Phát hiện cầu chuyển loại — nếu cầu vừa đổi nhịp trong 8 phiên gần,
    # cắt ngắn cửa sổ về nửa để bỏ bớt ảnh hưởng của cầu cũ
    shifted, shift_str = _detect_regime_shift(seq, recent_n=8, old_n=min(window, 20))
    if shifted and window > 12:
        # Cầu đổi loại: dùng nửa cửa sổ gần nhất để tránh nhiễu từ cầu cũ
        effective_w = max(10, window // 2)
        w = seq[-effective_w:]
        n = len(w)

    bins = [1 if v == "TAI" else 0 for v in w]
    # 1) Chu kỳ lặp chủ đạo: lag có tương quan mạnh nhất (1..cap_lag)
    best_lag, best_ac = 1, _autocorr_lag(bins, 1)
    for lag in range(2, cap_lag + 1):
        ac = _autocorr_lag(bins, lag)
        if abs(ac) > abs(best_ac): best_lag, best_ac = lag, ac

    last_side = w[-1]
    runs = _run_lengths_local(w)
    avg_run = sum(runs) / len(runs)
    cur_run = runs[-1]

    # 2) Vị trí trong chu kỳ run: đầu / giữa / quá hạn
    if cur_run > avg_run * 1.2:  vi_tri = "QUA_HAN"
    elif cur_run >= 2:            vi_tri = "GIUA_CHU_KY"
    else:                         vi_tri = "DAU_CHU_KY"

    # 3) Kiểu vận hành: ĐẢO (tương quan âm) / BÁM (tương quan dương) / hỏi data
    if best_ac <= -0.18:   loai_van, the = "ĐẢO", _opp(last_side)
    elif best_ac >= 0.18:  loai_van, the = "BÁM", last_side
    else:
        p_brk, _tg = _break_prob(w, cur_run)
        loai_van = "ĐẢO" if p_brk > 0.52 else "BÁM"
        the = _opp(last_side) if loai_van == "ĐẢO" else last_side

    strength = min(1.0, abs(best_ac) * 2.2)
    # v17.1: giảm strength khi cầu vừa chuyển — tín hiệu kém tin cậy hơn
    if shifted:
        strength *= (1.0 - shift_str * 0.5)

    p = 0.5 + (0.10 if the == "TAI" else -0.10) * strength
    if vi_tri == "QUA_HAN":
        p += (-0.05 if the == last_side else 0.05)
    p = _clamp(p, 0.38, 0.62)

    shift_note = f" [SHIFT {shift_str:.0%}]" if shifted else ""
    mo_ta = "%s: chu kỳ L%d (%s) · run %d/%.1f phiên · %s%s" % (
        tag, best_lag, loai_van, cur_run, avg_run,
        vi_tri.replace("_", " ").lower(), shift_note)

    return {"tang": tag, "window": window, "so_phien": n, "trang_thai": "OK",
            "chu_ky": best_lag, "ac": round(best_ac, 3), "vanh": loai_van,
            "run_hien_tai": cur_run, "run_tb": round(avg_run, 2), "vi_tri": vi_tri,
            "phia": the, "p_tai": round(p, 3), "do_manh": round(strength, 3),
            "regime_shift": shifted, "shift_strength": round(shift_str, 3),
            "mo_ta": mo_ta}

def phan_tich_chu_ky_3_tang(seq):
    """v17.1 — LÕI HỢP NHẤT 3 TẦNG CHU KỲ (trọng số ĐỘNG):
      NGẮN  (12 phiên) — cầu nhanh 1-1 / 2-2, phản ứng tức thì
      TRUNG (30 phiên) — nhịp giữa, keo giữa cầu nhanh và bệt
      DÀI   (60 phiên) — bệt / quy luật dài, ổn định nhưng trễ

    Cải tiến v17.1 so với v17:
    - Trọng số ĐỘNG: khi cầu vừa chuyển loại (regime shift), tầng NGẮN được
      tăng mạnh, tầng DÀI bị giảm → không bị kéo ngược bởi cầu cũ
    - Khi các tầng mâu thuẫn nhau (không đồng thuận), p_tai bị kéo về 0.5
      (trả tín hiệu yếu để governor và engine tự quyết)
    - Tầng thiếu dữ liệu = không phiếu · tín hiệu yếu = trọng số tự giảm"""
    specs = [("NGẮN",  int(os.getenv("CK_NGAN",  "12"))),
             ("TRUNG", int(os.getenv("CK_TRUNG", "30"))),
             ("DÀI",   int(os.getenv("CK_DAI",   "60")))]

    # Phát hiện regime shift toàn cục (8 phiên gần vs 20 phiên trước)
    _glob_shift, _glob_shift_str = _detect_regime_shift(seq, recent_n=8, old_n=20)

    # Trọng số cơ sở: cứng
    _base_w = {"NGẮN": 0.45, "TRUNG": 0.32, "DÀI": 0.23}
    # Khi cầu chuyển mạnh → boost NGẮN, giảm DÀI theo mức shift
    if _glob_shift:
        _shift_boost = _glob_shift_str * 0.25   # tối đa +25% cho NGẮN
        _base_w["NGẮN"]  = min(0.70, _base_w["NGẮN"]  + _shift_boost)
        _base_w["TRUNG"] = max(0.15, _base_w["TRUNG"] - _shift_boost * 0.4)
        _base_w["DÀI"]   = max(0.08, _base_w["DÀI"]  - _shift_boost * 0.6)
        # Chuẩn hoá lại về tổng = 1
        _tot = sum(_base_w.values())
        _base_w = {k: v / _tot for k, v in _base_w.items()}

    layers, s_p, s_w, names = [], 0.0, 0.0, []
    for tag, window in specs:
        ly = _cycle_layer(seq, window, tag)
        layers.append(ly)
        if ly.get("p_tai") is None:
            continue
        base = _base_w[tag]
        wv = base * (0.35 + 0.65 * ly["do_manh"])
        # v17.1: giảm trọng số tầng DÀI thêm nếu tầng đó cũng báo shift nội bộ
        if tag == "DÀI" and ly.get("regime_shift"):
            wv *= (1.0 - ly.get("shift_strength", 0.3) * 0.5)
        s_p += ly["p_tai"] * wv; s_w += wv
        names.append("%s L%d %s→%s" % (tag, ly["chu_ky"], ly["vanh"], ly["phia"]))

    if s_w <= 0:
        return {"da_du_du_lieu": False, "tangs": layers, "side": None,
                "ghi_chu": "Chưa đủ dữ liệu để đọc chu kỳ (cần ≥ 12 phiên)"}

    p = s_p / s_w

    # v17.1: Kiểm tra đồng thuận giữa các tầng
    # Nếu tầng NGẮN và DÀI trái chiều nhau → kéo p về trung tâm 0.5
    # (tín hiệu mâu thuẫn, không đủ cơ sở ra phán quyết mạnh)
    valid_layers = [ly for ly in layers if ly.get("p_tai") is not None]
    if len(valid_layers) >= 2:
        sides_vote = [ly["phia"] for ly in valid_layers]
        tai_count = sides_vote.count("TAI")
        xiu_count = sides_vote.count("XIU")
        # Mâu thuẫn: không nhất trí → kéo p về 0.5 theo mức độ mâu thuẫn
        if tai_count > 0 and xiu_count > 0:
            # Tỷ lệ nhất trí: 1.0 = đồng lòng hoàn toàn, 0.5 = chia đôi
            agree_rate = max(tai_count, xiu_count) / len(sides_vote)
            # Pull về 0.5 khi agree_rate thấp
            pull = (1.0 - agree_rate) * 2.0   # 0..1
            p = p * (1.0 - pull * 0.5) + 0.5 * (pull * 0.5)

    side = "TAI" if p >= 0.5 else "XIU"
    dong_thuan = sum(1 for ly in valid_layers if ly.get("phia") == side)
    shift_note = f" [SHIFT {_glob_shift_str:.0%}→boost NGẮN]" if _glob_shift else ""

    return {"da_du_du_lieu": True, "tangs": layers, "p_tai": round(p, 3),
            "side": side, "so_tang_chot": len(names), "dong_thuan": dong_thuan,
            "regime_shift": _glob_shift, "shift_strength": round(_glob_shift_str, 3),
            "mo_ta": (" · ".join(names) if names else "không tầng nào chốt") + shift_note}

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
    if not t: return None, out({"ok": False, "loi": "not_found", "thong_bao": "Dùng hu, md5 hoặc sunwin"}, 404)
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
# ───────── BẢO MẬT ADMIN v17 ─────────
# CSRF · cookie Strict/Secure · phiên trượt 30' + tuyệt đối 10h · gắn UA · thu hồi mọi phiên (epoch)
# TOTP 2FA (ADMIN_TOTP_SECRET) · IP allowlist (ADMIN_IPS) · chống dò mật khẩu backoff luỹ thừa · nhật ký kiểm toán
_adm_fails, _adm_block, _adm_strikes = {}, {}, {}
_totp_used = {"c": 0}
ADMIN_TOTP_SECRET = os.getenv("ADMIN_TOTP_SECRET", "").strip().replace(" ", "")
ADMIN_IPS = [x.strip() for x in os.getenv("ADMIN_IPS", "").split(",") if x.strip()]
_ADM_IDLE, _ADM_MAX = 1800, 10 * 3600

def _client_ip():
    """Chỉ tin X-Forwarded-For khi chạy sau proxy (Render): lấy hop CUỐI do proxy thêm, không lấy hop đầu (giả được)."""
    xff = request.headers.get("X-Forwarded-For", "")
    if xff and (os.getenv("RENDER") or os.getenv("TRUST_PROXY") == "1"):
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts: return parts[-1]
    return request.remote_addr or "0.0.0.0"

def _ua_hash():
    return hashlib.sha256((request.headers.get("User-Agent", "") or "").encode()).hexdigest()[:16]

def _audit(ev, note="", save=False):
    try:
        lst = STORE.setdefault("audit", [])
        lst.append({"t": now_iso(), "ev": ev, "ip": _client_ip(), "note": str(note)[:160],
                    "ua": (request.headers.get("User-Agent", "") or "")[:90]})
        if len(lst) > 400: del lst[:len(lst) - 400]
        if save: save_store()
    except Exception: pass

def _adm_blocked(ip):
    return _adm_block.get(ip, 0) > time.time()

def _adm_fail(ip):
    now = time.time()
    lst = [t for t in _adm_fails.get(ip, []) if now - t < 900]
    lst.append(now); _adm_fails[ip] = lst
    if len(lst) >= 5:                                   # 5 lần sai → khoá, mỗi lần tái phạm gấp đôi (tối đa 6h)
        k = _adm_strikes.get(ip, 0); _adm_strikes[ip] = k + 1
        _adm_block[ip] = now + min(21600, 900 * (2 ** k)); _adm_fails[ip] = []
        _audit("khoa_ip", "đăng nhập sai nhiều lần", True)

def _adm_ok(ip):
    _adm_fails.pop(ip, None); _adm_block.pop(ip, None); _adm_strikes.pop(ip, None)

def _totp_code(secret, counter):
    pad = "=" * (-len(secret) % 8)
    key = base64.b32decode(secret.upper() + pad, casefold=True)
    h = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    o = h[-1] & 0x0F
    return "%06d" % ((struct.unpack(">I", h[o:o + 4])[0] & 0x7FFFFFFF) % 1000000)

def _totp_ok(code):
    if not ADMIN_TOTP_SECRET: return True
    code = "".join(ch for ch in str(code or "") if ch.isdigit())
    if len(code) != 6: return False
    c0 = int(time.time() // 30)
    for d in (0, -1, 1):
        c = c0 + d
        if c > _totp_used["c"] and hmac.compare_digest(_totp_code(ADMIN_TOTP_SECRET, c), code):
            _totp_used["c"] = c                          # mã dùng 1 lần, chống replay
            return True
    return False

def _adm_epoch(): return int(STORE.setdefault("adm_epoch", 1))

def authed():
    if not session.get("adm"): return False
    now = time.time()
    if session.get("adm_until", 0) <= now: return False
    if now - session.get("adm_last", 0) > _ADM_IDLE: return False
    if session.get("ep") != _adm_epoch(): return False
    if session.get("ua") != _ua_hash(): return False
    return True

def guard():
    if not authed(): return out({"ok": False, "loi": "unauthorized", "thong_bao": "Chưa đăng nhập"}, 401)
    return None

def _csrf_ok():
    tok = session.get("csrf") or ""
    got = request.headers.get("X-CSRF-Token", "")
    return bool(tok) and hmac.compare_digest(tok.encode(), got.encode())

@app.before_request
def admin_shield():
    """Cổng chung cho /admin*: allowlist IP, kiểm Origin, CSRF cho mọi thao tác ghi, phiên trượt."""
    p = request.path
    if not p.startswith("/admin"): return None
    if request.method == "OPTIONS": return make_response("", 204)
    if ADMIN_IPS and _client_ip() not in ADMIN_IPS:
        return make_response("Not found", 404)
    if request.method not in ("GET", "HEAD"):
        org = request.headers.get("Origin", "")
        if org and org.split("://", 1)[-1] != request.host:
            _audit("csrf_origin", org, True)
            return out({"ok": False, "loi": "forbidden", "thong_bao": "Nguồn yêu cầu không hợp lệ"}, 403)
        if p != "/admin/login" and authed() and not _csrf_ok():
            _audit("csrf_token", p, True)
            return out({"ok": False, "loi": "csrf", "thong_bao": "Phiên không hợp lệ (CSRF) — tải lại trang"}, 403)
    if authed():
        session["adm_last"] = time.time()
    return None

@app.after_request
def admin_headers(resp):
    if request.path.startswith("/admin"):
        for k in ("Access-Control-Allow-Origin", "Access-Control-Allow-Methods", "Access-Control-Allow-Headers",
                  "Access-Control-Expose-Headers", "Access-Control-Max-Age", "Access-Control-Allow-Private-Network"):
            resp.headers.pop(k, None)
        resp.headers["Cache-Control"] = "no-store, max-age=0"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Robots-Tag"] = "noindex, nofollow"
        resp.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        resp.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self'; "
            "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if os.getenv("RENDER") or os.getenv("COOKIE_SECURE") == "1":
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return resp

@app.get("/admin/api/authinfo")
def adm_authinfo():
    """Trang đăng nhập hỏi: đã cấu hình mật khẩu / 2FA chưa; nếu đã đăng nhập thì kèm CSRF token."""
    a = authed()
    return out({"ok": True, "has_password": bool(ADMIN_PASSWORD), "totp": bool(ADMIN_TOTP_SECRET),
                "authed": a, "csrf": (session.get("csrf") if a else None)})

@app.post("/admin/login")
def admin_login():
    ip = _client_ip()
    if _adm_blocked(ip):
        wait = int(_adm_block.get(ip, 0) - time.time())
        return out({"ok": False, "thong_bao": "Đã khoá tạm thời — thử lại sau %d phút" % (wait // 60 + 1)}, 429)
    if not ADMIN_PASSWORD:
        return out({"ok": False, "thong_bao": "Chưa đặt ADMIN_PASSWORD trên Render (Environment → thêm biến rồi redeploy)"}, 503)
    j = request.get_json(silent=True) or request.form
    pw = str(j.get("pw", "") or "")
    pw_ok = bool(pw) and hmac.compare_digest(pw.encode(), ADMIN_PASSWORD.encode())
    otp_ok = _totp_ok(j.get("otp", "")) if pw_ok else False
    if pw_ok and otp_ok:
        _adm_ok(ip)
        session.clear()                                  # xoay phiên: chống session fixation
        session.permanent = True
        now = time.time()
        session.update({"adm": True, "adm_until": now + _ADM_MAX, "adm_last": now, "ep": _adm_epoch(),
                        "ua": _ua_hash(), "csrf": secrets.token_urlsafe(32)})
        _audit("dang_nhap", "ok", True)
        return out({"ok": True, "thong_bao": "Đăng nhập thành công", "csrf": session["csrf"]})
    time.sleep(0.6)                                      # làm chậm dò mật khẩu
    _adm_fail(ip)
    _audit("dang_nhap_sai", "sai OTP" if pw_ok else "sai mật khẩu", True)
    return out({"ok": False, "thong_bao": ("Sai mã 2FA" if pw_ok else "Sai mật khẩu hoặc mã 2FA"),
                "can_otp": bool(ADMIN_TOTP_SECRET)}, 401)

@app.get("/admin/login")
def admin_login_get():
    """Đã bỏ đăng nhập bằng ?pw= (mật khẩu lọt vào log/lịch sử trình duyệt). Chỉ chuyển về trang admin."""
    return redirect("/admin")

@app.post("/admin/logout")
def admin_logout():
    if authed() and not _csrf_ok():
        return out({"ok": False, "loi": "csrf"}, 403)
    _audit("dang_xuat", "", True); session.clear()
    return out({"ok": True})

@app.get("/admin/api/security")
def adm_security():
    g = guard()
    if g: return g
    pwl = len(ADMIN_PASSWORD)
    checks = [
        {"ten": "Mật khẩu quản trị", "ok": pwl >= 12, "ghi_chu": "%d ký tự — nên ≥ 12, có chữ hoa/thường/số" % pwl},
        {"ten": "Xác thực 2 lớp (TOTP)", "ok": bool(ADMIN_TOTP_SECRET), "ghi_chu": "Đặt biến ADMIN_TOTP_SECRET (base32) để bật" if not ADMIN_TOTP_SECRET else "Đang bật"},
        {"ten": "Giới hạn IP (ADMIN_IPS)", "ok": bool(ADMIN_IPS), "ghi_chu": "Chưa giới hạn — tuỳ chọn" if not ADMIN_IPS else "%d IP được phép" % len(ADMIN_IPS)},
        {"ten": "Cookie Secure + HTTPS", "ok": bool(app.config.get("SESSION_COOKIE_SECURE")), "ghi_chu": "Bật khi chạy trên Render/HTTPS"},
        {"ten": "SECRET_KEY cố định", "ok": bool(os.getenv("SECRET_KEY")), "ghi_chu": "Không đặt → mỗi lần redeploy mọi phiên bị đăng xuất"},
        {"ten": "CSRF · CSP · chặn iframe", "ok": True, "ghi_chu": "Luôn bật"},
    ]
    now = time.time()
    return out({"ok": True, "checks": checks, "idle_phut": _ADM_IDLE // 60, "toi_da_gio": _ADM_MAX // 3600,
                "ip_hien_tai": _client_ip(),
                "ip_dang_khoa": [{"ip": i, "con_lai_phut": int((t - now) / 60) + 1} for i, t in _adm_block.items() if t > now],
                "nhat_ky": list(reversed(STORE.get("audit", [])[-120:]))})

@app.post("/admin/api/security/revoke")
def adm_revoke_sessions():
    g = guard()
    if g: return g
    STORE["adm_epoch"] = _adm_epoch() + 1
    _audit("thu_hoi_phien", "đăng xuất mọi thiết bị", True)
    session.clear()
    return out({"ok": True})

@app.post("/admin/api/security/unblock")
def adm_unblock_ip():
    g = guard()
    if g: return g
    ip = str((request.get_json(silent=True) or {}).get("ip", ""))
    _adm_ok(ip); _audit("mo_khoa_ip", ip, True)
    return out({"ok": True})

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
        tk = stats(t.hist_list())
        pt = {}
        try:
            _eng = getattr(getattr(t, "brain", None), "engine", None)
            _seq = list(getattr(_eng, "seq", []) or [])
            _sums = list(getattr(_eng, "sums", []) or [])
            if _seq:
                _ck = analyze_chu_ky(_seq, _sums)
                pt = {"du_doan": _ck.get("du_doan"), "do_tin_cay": _ck.get("do_tin_cay"),
                      "nhip": _ck.get("nhip"), "do_thuan": _ck.get("do_thuan"),
                      "trang_thai": _ck.get("trang_thai"), "muc": _ck.get("muc"),
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
    if code not in URLS: return out({"ok": False, "thong_bao": "hu, md5 hoặc sunwin"}, 404)
    t, err = table_or_error(code)
    if err: return err
    try: limit = max(1, min(HIST_MAX, int(request.args.get("limit", HIST_MAX))))
    except Exception: limit = HIST_MAX
    res = view_history(t, limit)
    m = view_main(t)
    res["phien_hien_tai"] = m["phien_hien_tai"]; res["phien_truoc"] = m["phien_truoc"]
    res["che_do_cau"] = ((t.pending or {}).get("pk") or {}).get("regime")
    res["phan_tich_cau"] = analyze_cau(list(t.brain.engine.seq))
    _pk = (t.pending or {}).get("pk") or {}
    _sig = _pk.get("signal_detail") or _wf_signal_probs(list(t.brain.engine.seq))
    res["cau_so"] = _pk.get("cau_so") or _cau_so(list(t.brain.engine.seq))
    res["cau_phan_tich"] = _pk.get("cau_phan_tich") or _cau_phan_tich(list(t.brain.engine.seq), _sig)
    try: res["chu_ky"] = analyze_chu_ky(list(t.brain.engine.seq), list(getattr(t.brain.engine, "sums", [])))
    except Exception as _e: res["chu_ky"] = {"da_du_du_lieu": False, "ghi_chu": "lỗi phân tích: %s" % _e}
    # v19: chu kỳ NGẮN/TRUNG/DÀI — lấy từ dự đoán đang treo (pk) hoặc lần predict cuối
    res["cau_nhanh"] = ((t.pending or {}).get("pk") or {}).get("cau_nhanh")
    res["chu_ky_3_tang"] = ((t.pending or {}).get("pk") or {}).get("chu_ky_3_tang") \
        or getattr(t.brain, "last_cycle", None) or {"da_du_du_lieu": False}
    return out(res)

@app.route("/admin/api/history/<code>/reset", methods=["POST"])
def adm_history_reset(code):
    """v19 — XOÁ LỊCH SỬ CỦA 1 BÀN (Hũ / MD5 / Sunwin).
    Xoá: bảng lịch sử đã chấm + file lưu lâu dài + brain (học lại từ đầu).
    KHÔNG đụng nguồn/API nhà cái — phiên vẫn chạy bình thường, history tích luỹ lại từ đó."""
    g = guard()
    if g: return g
    code = code.lower()
    if code not in URLS: return out({"ok": False, "thong_bao": "bàn không hợp lệ"}, 404)
    t, err = table_or_error(code)
    if err: return err
    with t.lock:
        t.hist.clear()
        t.brain = Brain()          # học lại từ đầu, không chấm điểm lại dữ liệu cũ
        t.pending = None
        t.ready = True             # giữ last_id nên phiên mới tiếp tục được chấm bình thường
    t.save_history()               # ghi đè store[code] = [] — gộp code vẫn nguyên
    t._pend()
    return out({"ok": True, "thong_bao": "Đã xoá lịch sử " + NAMES[code]})

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

# ══════════════════════════════════════════════════════════════════════════════
#  THUẬT TOÁN ĐỌC CẦU V20 — ĐA DẠNG · THÔNG MINH · ỔN ĐỊNH
#  Triết lý: nhận dạng CẦU TRƯỚC, chọn LUẬT PHÙ HỢP, lọc NHIỄU chặt
#  Không dự đoán khi tín hiệu mâu thuẫn → chờ cầu chín
# ══════════════════════════════════════════════════════════════════════════════

def _classify_cau(seq):
    """Nhận dạng loại cầu hiện tại — nền tảng để chọn luật phù hợp.
    Trả: (loai_cau, do_tin, mo_ta)
    Các loại: BET_DAI / BET_NGAN / XEN_KE_11 / NHIP_22 / NHIP_33 /
              CAU_SONG / CAU_GON / CAU_CHAN_LE / HON_HOP / NHIEU"""
    if len(seq) < 6:
        return "NHIEU", 0.0, "thiếu dữ liệu"
    runs = _run_lengths_local(seq)
    last, cur_run = seq[-1], runs[-1]
    recent_runs = runs[-12:] if len(runs) >= 12 else runs

    avg = sum(recent_runs) / len(recent_runs)
    mx  = max(recent_runs)
    mn  = min(recent_runs)
    rng = mx - mn  # độ dao động

    # Tính xen kẽ: bao nhiêu % các run = 1
    r1_rate = sum(1 for r in recent_runs if r == 1) / len(recent_runs)
    # Tính run đều: bao nhiêu % các run = 2
    r2_rate = sum(1 for r in recent_runs if r == 2) / len(recent_runs)
    # Tính run = 3
    r3_rate = sum(1 for r in recent_runs if r == 3) / len(recent_runs)

    # 1) Cầu xen kẽ 1-1: >70% run = 1
    if r1_rate >= 0.70 and avg <= 1.4:
        return "XEN_KE_11", min(0.9, r1_rate), f"xen kẽ 1-1 ({r1_rate:.0%} run=1)"

    # 2) Nhịp 2-2: >60% run = 2
    if r2_rate >= 0.60 and avg <= 2.6:
        return "NHIP_22", min(0.85, r2_rate), f"nhịp 2-2 ({r2_rate:.0%} run=2)"

    # 3) Nhịp 3-3: >50% run = 3
    if r3_rate >= 0.50:
        return "NHIP_33", min(0.80, r3_rate), f"nhịp 3-3 ({r3_rate:.0%} run=3)"

    # 4) Bệt dài: run hiện tại >= 4 hoặc max >= 5
    if cur_run >= 4 or (mx >= 5 and avg >= 3.0):
        return "BET_DAI", min(0.85, 0.5 + cur_run * 0.07), f"bệt dài run={cur_run} avg={avg:.1f}"

    # 5) Bệt ngắn: avg 2-3, không xen kẽ
    if 1.8 <= avg <= 3.2 and rng <= 2:
        return "BET_NGAN", 0.65, f"bệt ngắn avg={avg:.1f}"

    # 6) Cầu chẵn-lẻ: run xen kẽ chẵn/lẻ
    if len(recent_runs) >= 6:
        parity = [r % 2 for r in recent_runs]
        if parity[-3:] in ([0,1,0],[1,0,1]):
            return "CAU_CHAN_LE", 0.68, f"chẵn-lẻ xen kẽ"

    # 7) Cầu sóng (tăng-giảm): 3-1-3-1 hoặc 1-3-1-3
    if len(recent_runs) >= 6:
        diffs = [recent_runs[i+1]-recent_runs[i] for i in range(len(recent_runs)-1)]
        sign_changes = sum(1 for i in range(len(diffs)-1) if diffs[i]*diffs[i+1] < 0)
        if sign_changes >= len(diffs) - 2 and rng >= 2:
            return "CAU_SONG", 0.65, f"cầu sóng (tăng-giảm, range={rng})"

    # 8) Cầu gộp (block): run lớn rồi xen kẽ, lặp lại
    if mx >= 3 and avg >= 1.8 and rng >= 2:
        return "CAU_GON", 0.58, f"cầu gộp mixed avg={avg:.1f} range={rng}"

    # 9) Hỗn hợp
    if rng >= 3 or avg > 3.5:
        return "HON_HOP", 0.45, f"hỗn hợp range={rng}"

    return "HON_HOP", 0.50, f"khó nhận dạng avg={avg:.1f}"


def _ck_rules_v20(seq):
    """Luật cầu v20 — đa dạng, nhận diện thông minh, không hardcode.
    Mỗi luật trả dự đoán tại bước kế tiếp (None = không có ý kiến).
    Nhóm luật theo TYPE cầu: mỗi nhóm chỉ nên mạnh ở loại cầu của nó."""
    if len(seq) < 6:
        return {}
    runs = _run_lengths_local(seq)
    cur = runs[-1]; last = seq[-1]; opp = _opp(last)
    done = runs[:-1][-150:]; n = len(seq)
    out = {}

    # ── NHÓM 1: LUẬT BỆT (theo / bẻ dựa data lịch sử) ──────────────────────
    # L1: Bệt theo — khi run ngắn và cầu ổn định, theo tiếp
    out["BET_THEO"] = last

    # L2: Bệt bẻ — khi run đã quá dài so với lịch sử
    if done:
        surv = sum(1 for r in done if r >= cur)
        end  = sum(1 for r in done if r == cur)
        pf   = (end + 1.0) / (surv + 2.0)       # P(gãy ở độ dài này)
        out["BET_HAZARD"] = opp if pf > 0.56 else (last if pf < 0.44 else None)
    else:
        out["BET_HAZARD"] = opp if cur >= 4 else last

    # L3: Bệt kỳ vọng — sau run dài bất thường, luôn bẻ
    if done:
        p99 = sorted(done)[int(len(done)*0.80)] if len(done) >= 5 else 3
        out["BET_P80"] = opp if cur >= p99 else None
    
    # ── NHÓM 2: LUẬT XEN KẼ 1-1 ─────────────────────────────────────────────
    # L4: Xen kẽ đảo — cầu 1-1 → luôn bẻ
    out["XK_DAO"] = opp

    # L5: Xen kẽ kiểm chứng — xác suất bẻ thực tế trong 20p gần nhất
    if len(seq) >= 10:
        w20 = seq[-20:]
        flip = sum(1 for i in range(1, len(w20)) if w20[i] != w20[i-1])
        flip_rate = flip / (len(w20) - 1) if len(w20) > 1 else 0.5
        out["XK_STAT"] = opp if flip_rate >= 0.55 else last

    # ── NHÓM 3: LUẬT NHỊP ĐỀU (run trung bình L) ────────────────────────────
    # L6: Nhịp L phổ biến — dự đoán theo nhịp run phổ biến nhất
    if len(done) >= 4:
        from collections import Counter as _C
        dom_run = _C(done).most_common(1)[0][0]
        out["NHIP_L"] = last if cur < dom_run else opp
    
    # L7: Nhịp trung bình — theo run avg
    if done:
        avg_run = sum(done[-20:]) / len(done[-20:])
        out["NHIP_AVG"] = last if cur < avg_run else opp

    # ── NHÓM 4: LUẬT MẪU LẶP (pattern 2-5 bước) ─────────────────────────────
    # L8: Chu kỳ 2: T X T X → bẻ
    out["CK2"] = seq[-2] if len(seq) >= 2 else None   # lấy từ 2 phiên trước
    # L9: Chu kỳ 3
    out["CK3"] = seq[-3] if len(seq) >= 3 else None
    # L10: Chu kỳ 4
    out["CK4"] = seq[-4] if len(seq) >= 4 else None
    # L11: Chu kỳ 5
    out["CK5"] = seq[-5] if len(seq) >= 5 else None

    # ── NHÓM 5: LUẬT MẪU XY (run-pattern) ───────────────────────────────────
    # L12: Mẫu X-Y-X-Y trong run lengths
    if len(runs) >= 4:
        r1, r2 = runs[-3], runs[-2]  # 2 run trước
        # Nếu r-2 ≈ r-4 (xen kẽ dài-ngắn), thì run tiếp theo ≈ r-1
        if len(runs) >= 5:
            r3, r4 = runs[-4], runs[-5]
            if abs(r1 - r3) <= 1 and abs(r2 - r4) <= 1:
                # Mẫu xy-xy: run tiếp theo nên là r2
                out["PAT_XY"] = last if cur < r2 else opp
            else:
                out["PAT_XY"] = None
        else:
            out["PAT_XY"] = None
    
    # L13: Cầu gương: sau 3-1 thường ra 1-3 hoặc ngược lại
    if len(runs) >= 4:
        if runs[-2] >= 3 and runs[-3] == 1:
            out["PAT_MIRROR"] = opp if cur >= 1 else last   # sau bệt dài thường xen kẽ
        elif runs[-2] == 1 and runs[-3] >= 3:
            out["PAT_MIRROR"] = last if cur < 3 else opp   # sau xen kẽ thường bệt
        else:
            out["PAT_MIRROR"] = None

    # ── NHÓM 6: LUẬT CÂN BẰNG (mean reversion) ───────────────────────────────
    # L14: Cân bằng 10p — khi lệch nhiều, kéo về
    if len(seq) >= 10:
        w10 = seq[-10:]
        t10, x10 = w10.count("TAI"), w10.count("XIU")
        imb10 = (t10 - x10) / 10
        if abs(imb10) >= 0.4:
            out["BAL10"] = "XIU" if imb10 > 0 else "TAI"  # kéo về phía thiểu số
        else:
            out["BAL10"] = None

    # L15: Cân bằng 20p
    if len(seq) >= 20:
        w20 = seq[-20:]
        t20, x20 = w20.count("TAI"), w20.count("XIU")
        imb20 = (t20 - x20) / 20
        if abs(imb20) >= 0.3:
            out["BAL20"] = "XIU" if imb20 > 0 else "TAI"
        else:
            out["BAL20"] = None

    # ── NHÓM 7: LUẬT DỰA TRÊN ENTROPY / BIẾN ĐỘNG ────────────────────────────
    # L16: Entropy thấp + run ngắn → theo (cầu ổn định)
    if len(seq) >= 10:
        w = seq[-10:]
        t, x = w.count("TAI"), w.count("XIU")
        p = t / (t + x) if (t + x) > 0 else 0.5
        ent = -(p * math.log2(p+1e-9) + (1-p) * math.log2(1-p+1e-9)) if p not in (0,1) else 0.0
        if ent < 0.6:   # cầu ổn định
            out["ENT_STABLE"] = last
        elif ent > 0.9: # cầu hỗn loạn → bẻ cũng nguy
            out["ENT_STABLE"] = None
        else:
            out["ENT_STABLE"] = None

    # L17: Momentum — xu hướng 5p gần nhất so với 5p trước
    if len(seq) >= 10:
        r5 = seq[-5:].count("TAI") / 5
        r5b = seq[-10:-5].count("TAI") / 5
        mom = r5 - r5b
        if abs(mom) >= 0.3:
            out["MOMENTUM"] = "TAI" if mom > 0 else "XIU"
        else:
            out["MOMENTUM"] = None

    # ── NHÓM 8: LUẬT CHẴN LẺ / SÓNG ─────────────────────────────────────────
    # L18: Chẵn-lẻ run: nếu các run gần đây xen kẽ chẵn/lẻ → tiếp theo ngược
    if len(runs) >= 4:
        parity = [r % 2 for r in runs[-4:]]
        if parity[-2:] in ([0,1],[1,0]):
            nxt_parity = 1 - parity[-1]
            # Chẵn → run ngắn chẵn → theo / Lẻ → run ngắn lẻ → bẻ
            out["CHAN_LE"] = last if (nxt_parity == 0 and cur < 2) else opp if (nxt_parity == 1 and cur < 2) else None
        else:
            out["CHAN_LE"] = None

    return out


def _ck_table_v20(seq, span=120):
    """Xây bảng dự đoán cho từng luật tại mỗi bước thời gian."""
    n = len(seq)
    t0 = max(10, n - span)
    tab = {}
    for t in range(t0, n + 1):
        pr = _ck_rules_v20(seq[:t])
        for k, v in pr.items():
            tab.setdefault(k, {})[t] = v
    return tab, t0


def _ck_score_v20(tab, seq, rule, lo, hi):
    """Tính (fired, hit, streak_hit, streak_miss) của một luật trong [lo, hi)."""
    f = h = 0
    streak_h = streak_m = cur_sh = cur_sm = 0
    for t in range(lo, hi):
        v = tab.get(rule, {}).get(t)
        if v is None:
            continue
        f += 1
        if v == seq[t]:
            h += 1; cur_sh += 1; cur_sm = 0
        else:
            cur_sm += 1; cur_sh = 0
        streak_h = max(streak_h, cur_sh)
        streak_m = max(streak_m, cur_sm)
    return f, h, streak_h, streak_m


def _ck_pick_v20(tab, seq, t, cau_type, win=40, minf=8):
    """Chọn luật tốt nhất — có ngữ cảnh cầu (cau_type).
    Ưu tiên: luật phù hợp cầu AND đang ăn tốt nhất gần đây.
    Penalty: luật đang thua liên tiếp >= 4."""
    # Nhóm luật theo loại cầu: mỗi luật được boost khi đúng cầu
    CAU_PREF = {
        "XEN_KE_11": ["XK_DAO","XK_STAT","CK2","BAL10"],
        "NHIP_22":   ["NHIP_L","NHIP_AVG","CK2","CK4","PAT_XY"],
        "NHIP_33":   ["NHIP_L","NHIP_AVG","CK3","PAT_XY"],
        "BET_DAI":   ["BET_HAZARD","BET_P80","BAL10","BAL20","MOMENTUM"],
        "BET_NGAN":  ["BET_THEO","NHIP_AVG","ENT_STABLE"],
        "CAU_CHAN_LE":["CHAN_LE","CK2","CK4","PAT_XY"],
        "CAU_SONG":  ["NHIP_AVG","PAT_MIRROR","CHAN_LE","MOMENTUM"],
        "CAU_GON":   ["NHIP_L","BET_HAZARD","PAT_MIRROR"],
        "HON_HOP":   ["BAL10","BAL20","MOMENTUM","CK3"],
    }
    pref_rules = set(CAU_PREF.get(cau_type, []))
    lo = max(10, t - win)
    best = None
    for rule in tab:
        f, h, sh, sm = _ck_score_v20(tab, seq, rule, lo, t)
        if f < minf:
            continue
        # Accuracy làm mượt (Laplace)
        acc = (h + 1.5) / (f + 3.0)
        # Boost nếu luật phù hợp cầu hiện tại
        if rule in pref_rules:
            acc = min(0.92, acc * 1.08)
        # Penalty nếu đang thua liên tiếp >= 4
        if sm >= 4:
            acc *= max(0.5, 1.0 - (sm - 3) * 0.12)
        # Penalty nếu có ý kiến quá ít lần
        if f < 15:
            acc *= 0.92
        if best is None or acc > best[1]:
            best = (rule, acc, f, h)
    return best


def _rhythm_read_v20(seq):
    """Đọc cầu v20: nhận dạng TYPE cầu → chọn luật phù hợp → ra hướng.
    Mức: RÕ (>=0.68) / KHÁ (>=0.62) / THAM_KHẢO / CHỜ.
    CHỜ khi: thiếu data, luật mâu thuẫn, luật đang thua dài."""
    if len(seq) < 20:
        return {"nhip": "CHƯAĐỦDỮLIỆU", "do_thuan": 0.0, "du_doan": None,
                "run_hien_tai": 0, "muc": "CHỜ", "luat": None,
                "loai_cau": "NHIEU", "ly_do": "cần ≥ 20 phiên"}

    # Bước 1: nhận dạng cầu
    cau_type, cau_conf, cau_desc = _classify_cau(seq)
    runs = _run_lengths_local(seq); cur = runs[-1]

    # Bước 2: xây bảng luật + chọn luật tốt nhất
    tab, _ = _ck_table_v20(seq, 120)
    n = len(seq)
    b = _ck_pick_v20(tab, seq, n, cau_type)

    if not b:
        return {"nhip": "KHÔNG_RÕ", "do_thuan": 0.5, "du_doan": None,
                "run_hien_tai": cur, "muc": "CHỜ", "luat": None,
                "loai_cau": cau_type, "ly_do": "chưa luật nào đủ mẫu"}

    rule, acc, f, h = b
    side = tab[rule].get(n)

    # Nếu luật tốt nhất không có ý kiến → tìm luật kế tiếp có ý kiến
    if not side:
        cands = []
        for r in tab:
            if tab[r].get(n) is not None:
                f2, h2, sh2, sm2 = _ck_score_v20(tab, seq, r, max(10, n-40), n)
                if f2 >= 8:
                    _acc = (h2 + 1.5) / (f2 + 3.0)
                    if r in set(["XK_DAO","XK_STAT","NHIP_L","BET_HAZARD","BAL10","BAL20","MOMENTUM"]):
                        _acc = min(0.92, _acc * 1.05)
                    cands.append((_acc, r, f2, h2))
        if cands:
            acc, rule, f, h = max(cands)
            side = tab[rule][n]

    if not side:
        return {"nhip": "NHIỄU", "do_thuan": round(acc, 2), "du_doan": None,
                "run_hien_tai": cur, "muc": "CHỜ", "luat": rule,
                "loai_cau": cau_type, "ly_do": "luật không có ý kiến bước tiếp"}

    # Bước 3: kiểm tra đồng thuận — tránh ra tín hiệu khi các luật chống nhau
    votes_tai = votes_xiu = 0
    for r in list(tab.keys()):
        v = tab[r].get(n)
        if v == "TAI": votes_tai += 1
        elif v == "XIU": votes_xiu += 1
    total_v = votes_tai + votes_xiu
    if total_v >= 4:
        majority_rate = max(votes_tai, votes_xiu) / total_v
        # Khi tỷ lệ đồng thuận < 55% → tín hiệu yếu → giảm acc
        if majority_rate < 0.55:
            acc *= 0.85   # penalty mâu thuẫn

    # Bước 4: điều chỉnh theo chất lượng cầu
    acc = acc * (0.80 + 0.20 * cau_conf)  # cầu rõ → tăng tin

    muc = "RÕ" if acc >= 0.68 else ("KHÁ" if acc >= 0.62 else "THAM KHẢO")

    # Map tên luật → tên nhịp dễ đọc
    NHIP_MAP = {
        "XK_DAO":"XEN_KẼ_1-1","XK_STAT":"XEN_KẼ_STAT","BET_THEO":"BỆT_THEO",
        "BET_HAZARD":"BỆT_GÃY","BET_P80":"BỆT_QUÁ_HẠN","NHIP_L":"NHỊP_ĐỀU",
        "NHIP_AVG":"NHỊP_AVG","CK2":"CHU_KỲ_2","CK3":"CHU_KỲ_3","CK4":"CHU_KỲ_4",
        "CK5":"CHU_KỲ_5","PAT_XY":"MẪU_XY","PAT_MIRROR":"MẪU_GƯƠNG",
        "BAL10":"CÂN_BẰNG_10","BAL20":"CÂN_BẰNG_20","ENT_STABLE":"ỔN_ĐỊNH",
        "MOMENTUM":"ĐÀ_XU_HƯỚNG","CHAN_LE":"CHẴN_LẺ",
    }
    nhip = NHIP_MAP.get(rule, rule)

    return {
        "nhip": nhip, "do_thuan": round(acc, 2), "du_doan": side,
        "run_hien_tai": cur, "muc": muc, "luat": rule,
        "loai_cau": cau_type, "cau_conf": round(cau_conf, 2),
        "dong_thuan": f"{max(votes_tai,votes_xiu)}/{total_v}" if total_v else "—",
        "ly_do": (f"[{cau_type}·{cau_desc}] luật {nhip} ăn {h}/{f} → nghiêng {side}")
    }

# Alias ngược chiều để không break các chỗ gọi cũ
def _ck_rules(seq):  return _ck_rules_v20(seq)
def _ck_table(seq, span=120): return _ck_table_v20(seq, span)
def _ck_score(tab, seq, rule, lo, hi): return _ck_score_v20(tab, seq, rule, lo, hi)[:2]
def _ck_pick(tab, seq, t, win=40, minf=8):
    cau_type, _, _ = _classify_cau(seq[:t])
    return _ck_pick_v20(tab, seq, t, cau_type, win, minf)
def _rhythm_read(seq): return _rhythm_read_v20(seq)


def _ck_backtest(seq):
    """Tự chấm TOÀN BỘ quy trình v20 trên 40 phiên cuối."""
    n = len(seq)
    if n < 60:
        return {"so_phien_thu": 0, "so_lan_ra_tin_hieu": 0, "dung": 0, "ty_le": None}
    tab, _ = _ck_table_v20(seq, 120)
    fired = hit = 0
    start = n - 40
    for t in range(start, n):
        sub_seq = seq[:t]
        cau_type, _, _ = _classify_cau(sub_seq)
        b = _ck_pick_v20(tab, seq, t, cau_type)
        if not b:
            continue
        v = tab[b[0]].get(t)
        if v:
            fired += 1
            hit += 1 if v == seq[t] else 0
    return {
        "so_phien_thu": 40, "so_lan_ra_tin_hieu": fired, "dung": hit,
        "ty_le": round(hit / fired * 100, 1) if fired else None
    }


def analyze_chu_ky(seq, sums=None):
    """Engine tổng hợp v20: nhận dạng cầu + đọc nhịp + backtest + silence gate."""
    seq = [s for s in seq if s in ("TAI", "XIU")][-200:]
    n = len(seq)
    if n < 20:
        return {"da_du_du_lieu": False, "so_phien": n, "ghi_chu": "Cần ≥ 20 phiên để đọc nhịp"}

    key = (n, hash(tuple(seq[-110:])))
    if key in _CK_CACHE:
        return _CK_CACHE[key]

    # Nhận dạng cầu (dùng để hiển thị + điều chỉnh)
    cau_type, cau_conf, cau_desc = _classify_cau(seq)

    rd = _rhythm_read_v20(seq)
    side = rd["du_doan"]; muc = rd["muc"]
    bt = _ck_backtest(seq)

    tin_hieu = []
    if side:
        tin_hieu.append({
            "nguon": f"luật {rd['nhip']} [{cau_type}]",
            "huong": side,
            "trong_so": rd["do_thuan"]
        })
        r = bt.get("ty_le")
        if r is not None and bt["so_lan_ra_tin_hieu"] >= 15:
            if r >= 55:
                tin_hieu.append({"nguon": "tự chấm toàn quy trình", "huong": side, "trong_so": 0.5})
            elif r < 48:
                muc = "THAM KHẢO"
                tin_hieu.append({"nguon": "tự chấm toàn quy trình", "huong": "YẾU", "trong_so": 0.0})

    # Silence gate: khi backtest thấp + mức thấp → không ra tín hiệu
    bt_rate = bt.get("ty_le") or 50.0
    if muc == "THAM KHẢO" and bt_rate < 50 and bt.get("so_lan_ra_tin_hieu", 0) >= 20:
        side = None; muc = "CHỜ"
        rd["ly_do"] = f"silence: backtest {bt_rate}% < 50% → chờ cầu chín"

    conf = 0.0
    if side:
        conf = round(min(0.68, 0.5 + 0.55 * max(0.0, rd["do_thuan"] - 0.5)), 3)
    if muc == "THAM KHẢO" and side:
        conf = min(conf, 0.54)

    wave = [
        seq[max(0, i - 9):i + 1].count("TAI") / min(10, i + 1)
        for i in range(n - 1, max(0, n - 51), -10)
    ]
    ttr = "TÁC ĐỘNG" if (side and muc in ("RÕ", "KHÁ")) else ("THAM KHẢO" if side else "CHỜ")

    res = {
        "da_du_du_lieu": True, "so_phien": n,
        "du_doan": side, "do_tin_cay": conf,
        "trang_thai": ttr, "muc": muc,
        "luat": rd.get("luat"), "nhip": rd["nhip"],
        "loai_cau": cau_type, "cau_desc": cau_desc, "cau_conf": round(cau_conf, 2),
        "dong_thuan": rd.get("dong_thuan", "—"),
        "do_thuan": rd["do_thuan"], "run_hien_tai": rd["run_hien_tai"],
        "ly_do": rd["ly_do"],
        "cau_run": "-".join(str(r) for r in _run_lengths_local(seq)[-12:]),
        "tin_hieu": tin_hieu,
        "ket_luan": (
            f"[{cau_type}] luật {rd['nhip']} · mức {muc} ({rd['do_thuan']:.0%}) → nghiêng {side}"
            if side else f"Chưa đủ cơ sở — {rd['ly_do']}"
        ),
        "song_ty_le_tai": [round(x, 2) for x in wave],
        "ty_le_tai_chung": round(sum(1 for s in seq if s == "TAI") / n, 3),
        "tong_tb20": round(sum(list(sums)[-20:]) / len(list(sums)[-20:]), 1) if sums else None,
        "backtest": bt,
        "luu_y": "RÕ ≥68% · KHÁ ≥62% · THAM KHẢO còn lại. Backtest trên 40 phiên cuối thực tế, không nhìn tương lai."
    }

    if len(_CK_CACHE) > 20:
        _CK_CACHE.clear()
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
.bhero{display:grid;grid-template-columns:auto minmax(0,1fr);gap:18px;align-items:center}
.bhero .stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.bmini{background:var(--s2);border:1px solid var(--line);border-radius:12px;padding:9px 11px}
.bmini small{display:block;font-size:10.5px;font-weight:800;letter-spacing:.06em;color:var(--tx3);text-transform:uppercase}
.bmini b{font-size:19px;font-weight:900}
.base{position:relative;height:8px;border-radius:99px;background:var(--s3);overflow:visible}
.base i{display:block;height:100%;border-radius:99px;background:var(--grad)}
.base u{position:absolute;left:50%;top:-3px;bottom:-3px;width:2px;background:var(--tx3);text-decoration:none}
.bpred{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:14px}
.bside{border-radius:16px;padding:16px;display:flex;align-items:center;gap:14px;min-width:0}
.bside.tai{background:var(--taiSoft);border:1.5px solid var(--tai)}
.bside.xiu{background:var(--xiuSoft);border:1.5px solid var(--xiu)}
.bside.wait{background:var(--s2);border:1.5px dashed var(--line2)}
.bside .big{font-size:34px;font-weight:900;line-height:1.05;letter-spacing:-.02em}
.seg{display:inline-flex;background:var(--s2);border:1px solid var(--line);border-radius:11px;padding:3px;gap:2px}
.seg button{padding:6px 12px;border-radius:8px;font-size:12px;font-weight:800;color:var(--tx2)}
.seg button.on{background:var(--s1);color:var(--tx);box-shadow:0 1px 4px rgba(20,30,60,.16)}
.btbl{max-height:560px;overflow:auto}
.btbl thead th{position:sticky;top:0;background:var(--s1);z-index:1}
.dc{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:7px;background:var(--s3);font-weight:800;font-size:12px;margin-right:3px}
@media(max-width:720px){.bhero{grid-template-columns:1fr}.bhero .stats{grid-template-columns:repeat(2,minmax(0,1fr))}.bpred{grid-template-columns:1fr}}
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
  <div id="otpbox" class="hide"><label>Mã xác thực 2 lớp (6 số)</label>
   <input id="otp" inputmode="numeric" autocomplete="one-time-code" maxlength="8" placeholder="000000" style="letter-spacing:.35em;text-align:center;font-weight:800" onkeydown="if(event.key==='Enter')doLogin()"></div>
  <button class="btn pri big" style="margin-top:12px" data-act="login"><svg class="ic sm"><use href="#i-lock"/></svg> Vào quản trị</button>
  <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--line);font-size:11.5px;line-height:1.7" class="muted">
   <div>✓ Phiên tự hết hạn sau 30 phút không thao tác</div><div>✓ Chống dò mật khẩu: sai 5 lần → khoá IP</div><div>✓ Mọi lần đăng nhập đều được ghi nhật ký</div></div>
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
let CSRF='';
async function ensureCsrf(){
 if(CSRF)return;
 try{const r=await fetch('/admin/api/authinfo',{credentials:'same-origin'});const j=await r.json();if(j.csrf)CSRF=j.csrf;}catch(e){}
}
async function api(p,o){
 o=o||{};bar(1);
 try{
  const mth=String(o.method||'GET').toUpperCase();
  if(mth!=='GET')await ensureCsrf();
  const hd={'Content-Type':'application/json'};if(CSRF)hd['X-CSRF-Token']=CSRF;
  const r=await fetch(p,Object.assign({credentials:'same-origin'},o,{headers:hd}));
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
 sec:{t:'Bảo mật',s:'Phiên · khoá IP · nhật ký kiểm toán',g:'HỆ THỐNG',i:'lock',r:vSec},
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
  const r=await fetch('/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({pw:($('pw').value||'').trim(),otp:(($('otp')||{}).value||'').trim()})});
  const j=await r.json();
  if(j.ok){CSRF=j.csrf||'';$('pw').value='';if($('otp'))$('otp').value='';await boot();}
  else{if(j.can_otp){const ob=$('otpbox');if(ob)ob.classList.remove('hide');}toast(j.thong_bao||'Đăng nhập thất bại');}
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
 +'<div style="margin-top:3px">'+(side?'<span class="tag '+(side==='TAI'?'tai':'xiu')+' lg">'+SIDE(side)+(pt.do_tin_cay?' · '+Math.round(num(pt.do_tin_cay)*100)+'%':'')+'</span>':'<span class="tag exp lg">CHƯA ĐỦ CƠ SỞ</span>')+'</div>'
 +'<div class="muted" style="margin-top:6px">Phiên #'+esc(b.phien_hien_tai||'—')+' · '+num(b.luoi_ms)+'ms · '+num(b.thang)+' thắng / '+num(b.thua)+' thua</div>'
 +'</div></div>'
 +'<dl class="dl" style="border-top:1px solid var(--line);padding-top:9px">'
 +'<dt>Nhịp đang đọc</dt><dd>'+(pt.nhip?esc(pt.nhip):'—')+'</dd>'
 +'<dt>Mức rõ</dt><dd>'+(pt.muc?esc(pt.muc):'—')+(pt.do_thuan!=null?' · luật ăn '+Math.round(num(pt.do_thuan)*100)+'%':'')+'</dd>'
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

 every(25000,()=>{if(CUR==='ov')vOverview().catch(()=>{});});
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
 +'<span class="tag '+(c.du_doan==='TAI'?'tai':c.du_doan==='XIU'?'xiu':'')+' lg">'+(c.du_doan?SIDE(c.du_doan)+' · '+Math.round(num(c.do_tin_cay)*100)+'%':'CHƯA ĐỦ CƠ SỞ')+'</span>'
 +'<span class="tag idle">nhịp '+esc(c.nhip||'?')+'</span><span class="tag idle">run '+cur+'</span>'
 +'<div style="flex:1;min-width:150px"><div class="pgb"><i style="width:'+Math.round(num(c.do_thuan)*100)+'%'+(num(c.do_thuan)>=0.7?';background:var(--ok)':'')+'"></i></div>'
 +'<small class="muted">mức '+esc(c.muc||'—')+' · luật ăn '+Math.round(num(c.do_thuan)*100)+'% / 40 phiên (RÕ ≥ 68%)</small></div></div>'
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
/* v19: thẻ PHÂN TÍCH CHU KỲ NGẮN / TRUNG / DÀI */
function cnLine(cn,side){
 if(!cn)return '';const c=cn.cau;
 if(!c)return '<div class="muted" style="margin:6px 0">Cầu: <b>chưa thấy cầu rõ</b> (ngẫu nhiên / đang chuyển cầu) — đang theo ensemble.</div>';
 const col=c.phia==='TAI'?'tai':'xiu';
 return '<div style="margin:6px 0;padding:8px 10px;border:1px solid var(--line);border-radius:10px"><b>'+esc(c.ten)+'</b> <span class="tag '+(c.trang_thai==='RÕ'?'act':'')+'">'+esc(c.trang_thai)+'</span>'
  +'<div class="muted">chạy '+num(c.streak)+' phiên liền · đúng '+num(c.hit)+'/'+num(c.n)+' gần đây · độ rõ '+Math.round(num(c.do_ro)*100)+'%</div>'
  +'<div style="margin-top:4px"><span class="tag '+(c.hanh_dong==='THEO'?'act':'ban')+' lg">'+esc(c.hanh_dong)+'</span> → <b style="color:var(--'+col+')">'+SIDE(c.phia)+'</b> <span class="muted">('+(c.hanh_dong==='THEO'?'giống phiên vừa ra':'ngược phiên vừa ra')+')</span></div></div>';
}
function czCard(cz,cn){
 const head='<div class="card"><div class="card-h"><span class="hi">'+ic('chart','sm')+'</span><h2 class="sp">Phân tích đa góc nhìn</h2>';
 if(!cz||!cz.da_du_du_lieu)return head+'<span class="tag exp">chờ dữ liệu</span></div><p class="muted">Cần ≥ 12 phiên để phân tích.</p></div>';
 const side=cz.side,pT=Math.round(num(cz.p_tai)*100),pW=side==='TAI'?pT:100-pT;
 const gn=(cz.goc_nhin||[]).map(g=>{
  const on=g.phia===side,tw=Math.round(Math.min(1,num(g.trong_so)/0.2)*100);
  return '<div class="evr"><div class="ei"'+(on?' style="border:1.5px solid var(--acc);color:var(--acc)"':'')+'>'+(g.phia==='TAI'?'T':'X')+'</div>'
  +'<div class="sp"><div class="b">'+esc(g.nhom)+' <span class="muted">· '+esc(g.ten)+'</span></div><div class="muted">'+esc(g.mo_ta||'')+'</div>'
  +'<div class="muted">ăn '+Math.round(num(g.acc)*100)+'% / '+num(g.n)+' phiên · trọng số '+(tw?tw+'%':'0 (chưa vượt may rủi)')+'</div></div>'
  +'<b class="nowrap" style="color:var(--'+(g.phia==='TAI'?'tai':'xiu')+')">'+SIDE(g.phia)+' '+Math.round((g.phia==='TAI'?num(g.p_tai):1-num(g.p_tai))*100)+'%</b></div>';
 }).join('');
 const tg=(cz.tangs||[]).map(t=>'<span class="pill'+(t.phia===side?' on':'')+'" title="'+esc(t.mo_ta||'')+'">'+esc(t.tang)+' '+num(t.window)+'p · '+esc(t.chu_ky||'—')+' → '+(t.phia?SIDE(t.phia):'—')+'</span>').join(' ');
 return head+'<span class="tag '+(side==='TAI'?'tai':'xiu')+' lg">'+SIDE(side)+' '+pW+'%</span><span class="tag act">'+num((cz.goc_nhin||[]).filter(g=>g.phia===side).length)+'/'+num((cz.goc_nhin||[]).length)+' góc nhìn đồng thuận</span></div>'
  +cnLine(cn||cz.cau_nhanh,side)+'<p class="muted" style="margin-top:2px">'+esc(cz.mo_ta||'')+'</p>'
  +(tg?'<div style="margin:6px 0">'+tg+'</div>':'')+'<div style="margin-top:6px">'+(gn||'<p class="muted">Chưa góc nhìn nào có đủ mẫu.</p>')+'</div></div>';
}
function banStreaks(li){
 /* li: mới → cũ; chỉ tính phiên có dự đoán thật (win/lose) */
 const a=li.filter(h=>h.trang_thai==='win'||h.trang_thai==='lose');
 let cur=0,curT=a.length?a[0].trang_thai:'',bw=0,bl=0,r=0,rt='';
 for(let i=0;i<a.length;i++){if(a[i].trang_thai===curT&&(i===cur))cur++;}
 for(const h of a.slice().reverse()){if(h.trang_thai===rt)r++;else{rt=h.trang_thai;r=1}if(rt==='win')bw=Math.max(bw,r);else bl=Math.max(bl,r)}
 const rate=n=>{const s=a.slice(0,n);return s.length?Math.round(s.filter(h=>h.trang_thai==='win').length*100/s.length):null};
 return {cur,curT,bw,bl,r10:rate(10),r20:rate(20),n:a.length};
}
function banTable(li){
 const f=DB.bf||'all';
 const rows=li.filter(h=>f==='all'||h.trang_thai===f);
 const cnt=k=>li.filter(h=>h.trang_thai===k).length;
 const seg=[['all','Tất cả',li.length],['win','WIN',cnt('win')],['lose','LOSE',cnt('lose')],['skip','SKIP',cnt('skip')]]
  .map(x=>'<button class="'+(f===x[0]?'on':'')+'" data-act="bFilt" data-arg="'+x[0]+'">'+x[1]+' <span class="muted">'+x[2]+'</span></button>').join('');
 return '<div class="card"><div class="card-h"><h2 class="sp">Bảng phiên</h2><span class="muted nowrap">'+rows.length+'/'+li.length+' phiên</span></div>'
 +'<div style="display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin-bottom:10px"><div class="seg">'+seg+'</div>'
 +'<button class="btn sm bad" data-act="resetHist" data-arg="'+esc(DB.bcode||'')+'">'+ic('trash','sm')+' Xoá lịch sử</button></div>'
 +'<div class="scrollx btbl"><table><thead><tr><th>Phiên</th><th>Dự đoán</th><th>Xúc xắc</th><th>Tổng</th><th>Kết quả</th><th>Chấm</th></tr></thead><tbody>'
 +(rows.map(h=>{const st=h.trang_thai;const rc=st==='win'?' class="r-win"':st==='lose'?' class="r-lose"':'';
   const badge=st==='win'?'<span class="tag wl-w">'+ic('check','xs')+' WIN</span>':st==='lose'?'<span class="tag wl-l">'+ic('close','xs')+' LOSE</span>':'<span class="tag">SKIP</span>';
   return '<tr'+rc+'><td class="mono">#'+esc(h.phien)+'</td><td>'+(h.du_doan?'<span class="tag '+(h.du_doan==='TAI'?'tai':'xiu')+'">'+SIDE(h.du_doan)+'</span>':'—')+'</td>'
   +'<td>'+((h.xuc_xac||[]).map(d=>'<span class="dc">'+esc(d)+'</span>').join('')||'—')+'</td><td><b>'+(h.tong==null?'—':h.tong)+'</b></td>'
   +'<td>'+(h.ket_qua?'<span class="tag '+(h.ket_qua==='TAI'?'tai':'xiu')+'">'+SIDE(h.ket_qua)+'</span>':'—')+'</td><td>'+badge+'</td></tr>';}).join('')
   ||'<tr><td colspan="6" class="muted" style="text-align:center;padding:22px">Chưa có phiên nào — lịch sử chỉ ghi các phiên hệ thống đã dự đoán thật từ lúc chạy.</td></tr>')
 +'</tbody></table></div></div>';
}
function banRender(j,code){
 const li=j.lich_su||[],st=j.thong_ke||{},hh=j.phien_hien_tai||{},pt=j.phien_truoc||{};
 const sl0=(document.querySelector('#v .scrollx')||{}).scrollLeft||0,sy=window.scrollY;
 const nm={hu:'BÀN HŨ',md5:'BÀN MD5',sunwin:'BÀN SUNWIN'}[code]||code;
 const note=code==='sunwin'?'Key Sunwin riêng — 1 key 1 bàn':'Key LC79 dùng chung 2 bàn Hũ + MD5';
 const S=banStreaks(li),rate=num(st.ty_le),graded=num(st.win)+num(st.lose);
 const stk=S.cur?('<b style="color:var(--'+(S.curT==='win'?'ok':'bad')+')">'+S.cur+' '+(S.curT==='win'?'thắng':'thua')+'</b>'):'<b>—</b>';
 const side=hh.du_doan;
 const predBox=side
  ?'<div class="bside '+(side==='TAI'?'tai':'xiu')+'"><div><div class="muted" style="font-size:11px;font-weight:800;letter-spacing:.06em">DỰ ĐOÁN PHIÊN #'+esc(hh.phien||'—')+'</div><div class="big" style="color:var(--'+(side==='TAI'?'tai':'xiu')+')">'+SIDE(side)+'</div></div>'
    +'<div style="margin-left:auto;text-align:right"><div class="muted" style="font-size:11px">Độ tin cậy mô hình tự tính</div><b style="font-size:20px">'+num(hh.do_tin_cay)+'%</b></div></div>'
  :'<div class="bside wait"><div><div class="muted" style="font-size:11px;font-weight:800;letter-spacing:.06em">PHIÊN #'+esc(hh.phien||'—')+'</div><div class="big" style="color:var(--tx3)">CHỜ</div></div><div class="muted" style="margin-left:auto;max-width:210px;font-size:12px">'+(hh.cau_loan?'Cầu loạn — không phát tín hiệu':'Chưa đủ cơ sở để đưa dự đoán')+'</div></div>';
 const prevBox='<div class="bside" style="background:var(--s2);border:1px solid var(--line)"><div><div class="muted" style="font-size:11px;font-weight:800;letter-spacing:.06em">PHIÊN VỪA RA #'+esc(pt.phien||'—')+'</div>'
  +'<div style="margin-top:4px">'+((pt.xuc_xac||[]).map(d=>'<span class="dc">'+esc(d)+'</span>').join(''))+' <b>= '+(pt.tong==null?'—':pt.tong)+'</b> '+(pt.ket_qua?'<span class="tag '+(pt.ket_qua==='TAI'?'tai':'xiu')+'">'+SIDE(pt.ket_qua)+'</span>':'')+'</div></div>'
  +'<div style="margin-left:auto">'+(pt.trang_thai==='win'?'<span class="tag wl-w">'+ic('check','xs')+' WIN</span>':pt.trang_thai==='lose'?'<span class="tag wl-l">'+ic('close','xs')+' LOSE</span>':'<span class="tag">—</span>')+'</div></div>';
 $('v').innerHTML='<div class="card"><div class="card-h"><span class="hi">'+ic(code==='sunwin'?'sw':code==='md5'?'hash':'dice','sm')+'</span><h2 class="sp">'+nm+'</h2><span class="muted">'+note+' · cập nhật '+dfmt(j.cap_nhat)+'</span></div>'
 +'<div class="bhero"><div style="text-align:center">'+ring(rate,rate>=55?'ok':'warn')+'<div class="muted" style="font-size:11px;margin-top:4px">thắng thực tế</div></div>'
 +'<div><div class="stats">'
 +'<div class="bmini"><small>WIN</small><b style="color:var(--ok)">'+num(st.win)+'</b></div>'
 +'<div class="bmini"><small>LOSE</small><b style="color:var(--bad)">'+num(st.lose)+'</b></div>'
 +'<div class="bmini"><small>SKIP</small><b>'+num(st.skip)+'</b></div>'
 +'<div class="bmini"><small>Chuỗi hiện tại</small>'+stk+'</div></div>'
 +'<div class="base" style="margin-top:12px"><i style="width:'+Math.min(100,rate)+'%"></i><u></u></div>'
 +'<div class="muted" style="font-size:11.5px;margin-top:5px">Vạch giữa = 50% (mức đoán ngẫu nhiên). Mẫu '+graded+' phiên đã chấm · 10 gần nhất '+(S.r10==null?'—':S.r10+'%')+' · 20 gần nhất '+(S.r20==null?'—':S.r20+'%')+' · thắng dài nhất '+S.bw+' · thua dài nhất '+S.bl+'. Mẫu nhỏ thì dao động mạnh là bình thường.</div></div></div>'
 +'<div class="muted" style="font-size:11px;font-weight:800;letter-spacing:.06em;margin:14px 0 5px">CHUỖI '+li.length+' PHIÊN GẦN NHẤT (mới → cũ)</div>'
 +'<div class="dots">'+li.map(h=>'<i class="'+(h.trang_thai==='win'?'w':h.trang_thai==='lose'?'l':h.trang_thai==='skip'?'s':'')+'" title="#'+esc(h.phien)+'"></i>').join('')+'</div></div>'
 +'<div class="bpred">'+predBox+prevBox+'</div><div style="height:14px"></div>'
 +'<div class="grid g2">'+czCard(j.chu_ky_3_tang,j.cau_nhanh)+ckCard(j.chu_ky)+'</div>'
 +((j.phan_tich_cau&&j.phan_tich_cau.khung_da_phien&&j.phan_tich_cau.khung_da_phien.length)
   ?'<div class="card"><div class="card-h"><span class="hi">'+ic('chart','sm')+'</span><h2 class="sp">Tầng khung phiên</h2></div><div class="pills">'
    +j.phan_tich_cau.khung_da_phien.map(r=>'<span class="pill '+(r.p_tai>=0.53?'on':'')+'" title="TÀI '+r.tai+' · XỈU '+r.xiu+' · lệch '+r.lech+'">'+num(r.khung)+'p · '+(r.goc==='đảo'?'đảo':'theo')+' · '+Math.round(r.p_tai*100)+'%</span>').join('')
    +'</div>'+(j.phan_tich_cau.dong_thuan_da_khung?'<p class="muted" style="margin-top:8px">'+esc(j.phan_tich_cau.dong_thuan_da_khung.mo_ta||'')+'</p>':'')+'</div>':'')
 +'<div id="btblWrap">'+banTable(li)+'</div>';
 const w=document.querySelector('#v .scrollx');if(w)w.scrollLeft=sl0;window.scrollTo(0,sy);
}
async function vBan(code){
 if(DB.bcode!==code)DB.bf='all';DB.bcode=code;DB.bf=DB.bf||'all';
 const draw=async()=>{
  const j=await api('/admin/api/history/'+code+'?limit=50');
  DB.bj=j;banRender(j,code);
 };
 await draw();
 /* auto phân tích luôn chạy — làm mới mỗi 8s */
 every(8000,()=>{if(CUR===code)draw().catch(()=>{});});
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

async function vSec(){
 $('v').innerHTML='<div class="card"><p class="muted">Đang tải…</p></div>';
 const j=await api('/admin/api/security');
 const ck=(j.checks||[]).map(c=>'<tr><td><b>'+esc(c.ten)+'</b></td><td><span class="tag '+(c.ok?'act':'exp')+'">'+(c.ok?'✓ ĐẠT':'! CHƯA')+'</span></td><td class="muted">'+esc(c.ghi_chu)+'</td></tr>').join('');
 const lk=(j.ip_dang_khoa||[]).map(x=>'<div style="display:flex;gap:8px;align-items:center;margin-top:6px"><span class="mono sp">'+esc(x.ip)+'</span><span class="muted">còn ~'+num(x.con_lai_phut)+'′</span><button class="btn sm" data-act="unblock" data-arg="'+esc(x.ip)+'">Mở khoá</button></div>').join('')||'<p class="muted">Không có IP nào đang bị khoá.</p>';
 const EV={dang_nhap:'Đăng nhập',dang_nhap_sai:'Đăng nhập SAI',dang_xuat:'Đăng xuất',khoa_ip:'Khoá IP',thu_hoi_phien:'Thu hồi phiên',mo_khoa_ip:'Mở khoá IP',csrf_origin:'Chặn Origin lạ',csrf_token:'Chặn CSRF'};
 const lg=(j.nhat_ky||[]).map(x=>'<tr><td class="mono nowrap">'+esc(String(x.t||'').replace('T',' ').slice(0,19))+'</td><td><b style="color:var(--'+(/sai|khoa|csrf/.test(x.ev)?'bad':'tx')+')">'+esc(EV[x.ev]||x.ev)+'</b></td><td class="mono">'+esc(x.ip)+'</td><td class="muted">'+esc(x.note||'')+'</td></tr>').join('')||'<tr><td colspan="4" class="muted">Chưa có sự kiện.</td></tr>';
 $('v').innerHTML='<div class="split"><div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('lock','sm')+'</span><h2 class="sp">Kiểm tra cấu hình</h2></div><div class="scrollx"><table><tbody>'+ck+'</tbody></table></div>'
 +'<p class="muted" style="margin-top:10px">IP của bạn: <span class="mono">'+esc(j.ip_hien_tai)+'</span> · Phiên: '+num(j.idle_phut)+' phút không thao tác / tối đa '+num(j.toi_da_gio)+' giờ</p></div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('shield','sm')+'</span><h2 class="sp">IP đang bị khoá</h2></div>'+lk+'</div>'
 +'<div class="card"><div class="card-h"><span class="hi">'+ic('logout','sm')+'</span><h2 class="sp">Thu hồi mọi phiên</h2></div><p class="muted">Đăng xuất tất cả thiết bị đang mở admin (kể cả máy này). Dùng khi nghi lộ mật khẩu.</p><button class="btn bad big" data-act="revoke">Đăng xuất mọi thiết bị</button></div></div>'
 +'<div><div class="card"><div class="card-h"><span class="hi">'+ic('clock','sm')+'</span><h2 class="sp">Nhật ký kiểm toán</h2></div><div class="scrollx"><table><thead><tr><th>Thời gian</th><th>Sự kiện</th><th>IP</th><th>Ghi chú</th></tr></thead><tbody>'+lg+'</tbody></table></div></div></div></div>';
}
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
 +'<p class="muted">Phiên hết hạn sau 30 phút không thao tác (tối đa 10 giờ). Xem nhật ký & thu hồi phiên ở trang Bảo mật.</p>'
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
 resetHist:async(code)=>{if(!confirm('XOÁ TOÀN BỘ lịch sử chấm điểm của bàn này? Không thể hoàn tác.'))return;
  try{await post('/admin/api/history/'+code+'/reset');toast('Đã xoá lịch sử bàn');await reload();}catch(e){}},
 logout:async()=>{try{await post('/admin/logout');}catch(e){}CSRF='';location.reload();},
 theme:()=>toggleTheme(),
 reload:()=>reload(),
 unblock:async(ip)=>{await post('/admin/api/security/unblock',{ip});toast('Đã mở khoá');vSec();},
 revoke:async()=>{if(!confirm('Đăng xuất mọi thiết bị?'))return;await post('/admin/api/security/revoke');CSRF='';location.reload();},
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
 bFilt:(v)=>{DB.bf=v;const w=$('btblWrap');if(w&&DB.bj)w.innerHTML=banTable(DB.bj.lich_su||[]);},
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
 let hasPw=true,ok=false;
 try{const r=await fetch('/admin/api/authinfo',{credentials:'same-origin'});if(r.ok){const j=await r.json();hasPw=!!j.has_password;ok=!!j.authed;CSRF=j.csrf||'';
  const ob=$('otpbox');if(ob)ob.classList.toggle('hide',!j.totp);}}catch(e){ok=false;}
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