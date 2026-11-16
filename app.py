# -*- coding: utf-8 -*-
"""PAW TX API - bản nhẹ cho Render free (không cần database).
Endpoint:  /tx/hu  /tx/md5  /history/tx/hu  /history/tx/md5  /admin  /ping
Mọi JSON đều bật CORS (HTML ở domain khác gọi GET thoải mái).
Start:  gunicorn app:app --workers 1 --threads 4 --timeout 30
Env:    ADMIN_PASS (bắt buộc để vào /admin), ADMIN_USER (mặc định admin), SECRET_KEY,
        API_URL_HU, API_URL_MD5 (nếu muốn đổi nguồn)."""
import hmac, json, math, os, secrets, threading, time
from collections import deque
from datetime import datetime, timedelta, timezone

import requests
from flask import Flask, jsonify, make_response, redirect, request, session
from werkzeug.exceptions import HTTPException

URLS = {"hu": os.getenv("API_URL_HU", "https://wtx.tele68.com/v1/tx/sessions"),
        "md5": os.getenv("API_URL_MD5", "https://wtxmd52.tele68.com/v1/txmd5/sessions")}
NAMES = {"hu": "Hũ", "md5": "MD5"}
WINDOW = 30      # mỗi bàn chỉ học tối đa 30 phiên gần nhất
HIST_MAX = 50    # lịch sử tối đa 50 phiên mỗi bàn
WARM = 8         # cần tối thiểu 8 phiên trước khi bắt đầu dự đoán
POLL_SEC = 4     # chu kỳ lấy dữ liệu nền
MIN_GAP = 3      # không gọi upstream dày hơn 3 giây
STALE_SEC = 8    # dữ liệu cũ hơn 8 giây thì request sẽ kích hoạt làm mới nền
ETA, GAMMA, REG = 2.5, 0.15, 0.3   # tốc độ học, chia sẻ cố định, ghìm nhiệt độ về 1
ICON = {"win": "✅", "lose": "❌", "cho": "⏳"}
VN = timezone(timedelta(hours=7))
STATE_FILE = os.getenv("STATE_FILE", "/tmp/paw_tx_toggles.json")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", PERMANENT_SESSION_LIFETIME=timedelta(hours=8))
app.json.ensure_ascii = False
app.json.sort_keys = False


# ------------------------------- CORS + lỗi luôn trả JSON --------------------
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-Requested-With"
    resp.headers["Access-Control-Max-Age"] = "86400"
    if not request.path.startswith("/admin"):
        resp.headers["Cache-Control"] = "no-store"
    return resp


@app.errorhandler(Exception)
def on_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    msg = e.description if isinstance(e, HTTPException) else "Lỗi máy chủ"
    return jsonify({"ok": False, "error": "http_%d" % code, "message": msg}), code


def out(payload, status=200):
    """Trả JSON; thêm ?pretty=1 để xem cho dễ đọc."""
    if request.args.get("pretty"):
        r = make_response(json.dumps(payload, ensure_ascii=False, indent=2), status)
        r.headers["Content-Type"] = "application/json; charset=utf-8"
        return r
    return jsonify(payload), status


# ------------------------------- Lấy + chuẩn hóa dữ liệu upstream ------------
_http = requests.Session()
_http.headers.update({"User-Agent": "Mozilla/5.0 (PAW-TX)", "Accept": "application/json"})


def parse_sessions(data):
    """list upstream (mới → cũ) → danh sách phiên cũ → mới, đã chuẩn hóa."""
    rows = data.get("list") if isinstance(data, dict) else data
    got = {}
    for it in rows or []:
        try:
            sid = int(it["id"]); dices = [int(x) for x in (it.get("dices") or [])][:3]
            if "point" not in it and not dices: continue
            point = int(it["point"]) if "point" in it else sum(dices)
            res = str(it.get("resultTruyenThong") or "").upper()
            if res not in ("TAI", "XIU"): res = "TAI" if point >= 11 else "XIU"
            got[sid] = {"id": sid, "dices": dices, "point": point, "result": res}
        except (KeyError, TypeError, ValueError):
            continue
    return [got[k] for k in sorted(got)]


def fetch_sessions(url):
    r = _http.get(url, timeout=(3, 7)); r.raise_for_status()
    return parse_sessions(r.json())


FETCH = fetch_sessions   # test có thể thay thế


# ------------------------------- AI tự học (cửa sổ 30 phiên, mỗi bàn riêng) ---
def _logit(p):
    p = min(0.9, max(0.1, p)); return math.log(p / (1 - p))


def _sig(z):
    return 1 / (1 + math.exp(-z))


class Brain:
    """8 chuyên gia + trọng số học theo cửa sổ trượt 30 phiên (Hedge có chia sẻ cố định)
    + hiệu chỉnh nhiệt độ để không tự tin quá mức. Chỉ dùng dữ liệu quá khứ, không nhìn trước."""
    NAMES = ("markov1", "markov2", "ngram", "run", "persist", "trend", "revert", "dice")

    def __init__(s):
        s.r = deque(maxlen=WINDOW); s.pt = deque(maxlen=WINDOW)
        s.loss = {n: deque(maxlen=WINDOW) for n in s.NAMES}
        s.zh = deque(maxlen=WINDOW); s.temp = 1.0
        s.w = {n: 1.0 / len(s.NAMES) for n in s.NAMES}

    def experts(s):
        r = list(s.r); n = len(r); ex = {k: 0.5 for k in s.NAMES}
        if n < 4: return ex
        last = r[-1]

        def follow(L):  # đếm cái gì đã xuất hiện sau cùng chuỗi đuôi dài L
            suf = r[-L:]; k = m = 0
            for i in range(n - L):
                if r[i:i + L] == suf: m += 1; k += r[i + L]
            return k, m
        k, m = follow(1); ex["markov1"] = (k + 1) / (m + 2)
        if n >= 6: k, m = follow(2); ex["markov2"] = (k + 1.5) / (m + 3)
        for L in range(min(6, n - 2), 2, -1):
            k, m = follow(L)
            if m >= 2: ex["ngram"] = (k + 1) / (m + 2); break
        c = 1
        while c < n and r[n - 1 - c] == last: c += 1
        reach = cont = 0; i = 0; body = r[:n - c]
        while i < len(body):
            j = i
            while j < len(body) and body[j] == body[i]: j += 1
            ln = j - i
            if ln >= c: reach += 1; cont += int(ln > c)
            i = j
        pc = (cont + 1) / (reach + 2); ex["run"] = pc if last else 1 - pc
        same = sum(1 for i in range(1, n) if r[i] == r[i - 1])   # tỉ lệ "giữ nguyên" gộp cả hai cửa
        ps = (same + 1) / (n - 1 + 2); ex["persist"] = ps if last else 1 - ps
        ema = 0.5
        for v in r: ema = 0.65 * ema + 0.35 * v
        ex["trend"] = 0.5 + 0.5 * (ema - 0.5)
        ex["revert"] = 0.5 - 0.5 * (sum(r) / n - 0.5)
        pts = list(s.pt)[-3:]
        if pts: ex["dice"] = 0.5 - 0.03 * (sum(pts) / len(pts) - 10.5)
        return {k: min(0.9, max(0.1, v)) for k, v in ex.items()}

    def predict(s):
        ex = s.experts(); z = sum(s.w[k] * _logit(ex[k]) for k in s.NAMES); p = _sig(s.temp * z)
        side = "TAI" if (p > 0.5 or (p == 0.5 and (not s.r or s.r[-1]))) else "XIU"
        return {"p": p, "z": z, "ex": ex, "side": side, "conf": round(max(p, 1 - p) * 100), "w": dict(s.w), "temp": s.temp}

    def learn(s, pk, y):
        for k in s.NAMES:
            p = pk["ex"][k]; s.loss[k].append(-math.log(p if y else 1 - p))
        s.zh.append((pk["z"], y))
        tot = {k: sum(s.loss[k]) for k in s.NAMES}; lo = min(tot.values())
        e = {k: math.exp(-ETA * (tot[k] - lo)) for k in s.NAMES}; Z = sum(e.values())
        s.w = {k: (1 - GAMMA) * e[k] / Z + GAMMA / len(s.NAMES) for k in s.NAMES}
        if len(s.zh) >= 12:   # chọn nhiệt độ tốt nhất trên cửa sổ học
            best, bl = 1.0, 1e9
            for i in range(5, 21):
                t = i / 10; l = 0.0
                for z, yy in s.zh:
                    q = _sig(t * z); l -= math.log(max(1e-6, q if yy else 1 - q))
                l = l / len(s.zh) + REG * (t - 1) ** 2
                if l < bl: bl, best = l, t
            s.temp = best

    def observe(s, row):
        s.r.append(1 if row["result"] == "TAI" else 0); s.pt.append(row["point"])


def entry(row, pk, win, live):
    return {"phien": row["id"], "du_doan": pk["side"], "ket_qua": row["result"], "xuc_xac": row["dices"], "tong": row["point"],
            "trang_thai": "win" if win else "lose", "icon": ICON["win" if win else "lose"], "live": live}


def replay(rows):
    """Nạp nhanh từ ~105 phiên có sẵn: chạy lần lượt cũ → mới, mỗi bước chỉ dùng quá khứ."""
    b = Brain(); hist = deque(maxlen=HIST_MAX)
    for i, row in enumerate(rows):
        if i >= WARM:
            pk = b.predict(); win = pk["side"] == row["result"]
            b.learn(pk, row["result"] == "TAI"); hist.append(entry(row, pk, win, False))
        b.observe(row)
    return b, hist


# ------------------------------- Trạng thái từng bàn --------------------------
class Table:
    def __init__(s, code):
        s.code, s.name, s.url = code, NAMES[code], URLS[code]
        s.enabled = True; s.lock = threading.Lock(); s.reset()

    def reset(s):
        s.ready = False; s.brain = None; s.hist = deque(maxlen=HIST_MAX); s.last = None; s.pending = None
        s.last_id = 0; s.fetch_ts = 0.0; s.ok_ts = 0.0; s.err = ""; s.ms = 0; s.n_fetch = 0

    def refresh(s, force=False, block=True, rebuild=False):
        if not s.lock.acquire(blocking=block): return
        try:
            if not force and s.ready and time.time() - s.fetch_ts < MIN_GAP: return
            s.fetch_ts = time.time(); t0 = time.time()
            try: rows = FETCH(s.url)
            except Exception as e:
                s.err = "%s: %s" % (type(e).__name__, str(e)[:120]); return
            if not rows: s.err = "Upstream trả danh sách rỗng"; return
            s.ms = int((time.time() - t0) * 1000); s.err = ""; s.ok_ts = time.time(); s.n_fetch += 1
            s.apply(rows, rebuild)
        finally:
            s.lock.release()

    def apply(s, rows, rebuild=False):
        newest = rows[-1]["id"]
        if rebuild or not s.ready or newest < s.last_id or rows[0]["id"] > s.last_id + 1:
            s.brain, s.hist = replay(rows)   # nạp lại toàn bộ từ danh sách upstream
            h = s.hist[-1] if s.hist and s.hist[-1]["phien"] == newest else None
            s.last = {"phien": newest, "xuc_xac": rows[-1]["dices"], "tong": rows[-1]["point"], "ket_qua": rows[-1]["result"],
                      "du_doan": h["du_doan"] if h else None, "trang_thai": h["trang_thai"] if h else "khong"}
            s.last_id = newest; s.ready = True; s._pend(); return
        for row in (r for r in rows if r["id"] > s.last_id):
            pd = s.pending; du = None; tt = "khong"
            if pd and pd["phien"] == row["id"]:
                win = pd["du_doan"] == row["result"]; s.brain.learn(pd["pk"], row["result"] == "TAI")
                s.hist.append(entry(row, pd["pk"], win, True)); du = pd["du_doan"]; tt = "win" if win else "lose"
            s.brain.observe(row)
            s.last = {"phien": row["id"], "xuc_xac": row["dices"], "tong": row["point"], "ket_qua": row["result"], "du_doan": du, "trang_thai": tt}
            s.last_id = row["id"]; s.pending = None
        s._pend()

    def _pend(s):
        pk = s.brain.predict()
        s.pending = {"phien": s.last_id + 1, "du_doan": pk["side"], "do_tin_cay": pk["conf"], "p_tai": round(pk["p"], 3), "pk": pk}


TABLES = {c: Table(c) for c in URLS}


def stats(items):
    w = sum(1 for h in items if h["trang_thai"] == "win"); l = len(items) - w
    return {"win": w, "lose": l, "ty_le": round(w * 100.0 / len(items), 1) if items else 0.0}


def now_iso():
    return datetime.now(VN).replace(microsecond=0).isoformat()


def view_main(t):
    last, pd = t.last, t.pending
    items = list(t.hist)
    if items and last and items[-1]["phien"] == last["phien"]: items = items[:-1]
    pre = {"phien": last["phien"], "xuc_xac": last["xuc_xac"], "tong": last["tong"], "ket_qua": last["ket_qua"],
           "hien_thi": "%s = %d · %s" % ("-".join(map(str, last["xuc_xac"])), last["tong"], "TÀI" if last["ket_qua"] == "TAI" else "XỈU"),
           "du_doan": last["du_doan"], "trang_thai": last["trang_thai"], "icon": ICON.get(last["trang_thai"], "")}
    res = {"ok": True, "ban": t.name, "phien_truoc": pre,
           "phien_hien_tai": {"phien": pd["phien"], "du_doan": pd["du_doan"], "do_tin_cay": pd["do_tin_cay"], "trang_thai": "cho", "icon": ICON["cho"]},
           "lich_su": [{k: h[k] for k in ("phien", "du_doan", "ket_qua", "xuc_xac", "trang_thai", "icon")} for h in items[-5:][::-1]],
           "thong_ke": stats(list(t.hist)), "cap_nhat": now_iso()}
    if t.err: res["canh_bao"] = "Nguồn dữ liệu đang lỗi, đang dùng dữ liệu gần nhất"
    return res


def view_history(t, limit):
    items = list(t.hist)[::-1][:limit]
    return {"ok": True, "ban": t.name, "tong": len(items), "thong_ke": stats(list(t.hist)), "cap_nhat": now_iso(),
            "lich_su": [{k: h[k] for k in ("phien", "du_doan", "ket_qua", "xuc_xac", "tong", "trang_thai", "icon", "live")} for h in items]}


# ------------------------------- Bật/tắt bàn + luồng nền ----------------------
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
                _poller["on"] = True; threading.Thread(target=_loop, daemon=True).start()


def table_or_error(code):
    t = TABLES.get(code)
    if not t: return None, out({"ok": False, "error": "not_found", "message": "Bàn không tồn tại (dùng hu hoặc md5)"}, 404)
    if not t.enabled: return None, out({"ok": False, "error": "table_off", "message": "Bàn %s đang tắt" % t.name}, 503)
    if not t.ready: t.refresh()   # lần đầu sau khi thức dậy: nạp nhanh 105 phiên
    elif time.time() - t.fetch_ts > STALE_SEC:   # trả ngay dữ liệu đang có, làm mới ở nền (không chờ upstream)
        threading.Thread(target=t.refresh, kwargs={"block": False}, daemon=True).start()
    if not t.ready: return None, out({"ok": False, "error": "upstream_error", "message": "Chưa lấy được dữ liệu, thử lại sau vài giây", "chi_tiet": t.err}, 503)
    return t, None


@app.get("/tx/<code>")
def api_main(code):
    t, err = table_or_error(code)
    return err or out(view_main(t))


@app.get("/history/tx/<code>")
def api_history(code):
    t, err = table_or_error(code)
    if err: return err
    try: limit = max(1, min(HIST_MAX, int(request.args.get("limit", HIST_MAX))))
    except ValueError: limit = HIST_MAX
    return out(view_history(t, limit))


@app.get("/ping")
def ping():
    return out({"ok": True, "t": now_iso()})


@app.get("/")
def index():
    return out({"ok": True, "name": "PAW TX API", "endpoints": ["/tx/hu", "/tx/md5", "/history/tx/hu", "/history/tx/md5", "/admin", "/ping"]})


# ------------------------------- Admin ----------------------------------------
_fails = {}


def authed():
    return bool(session.get("adm")) and session.get("adm_until", 0) > time.time()


def guard():
    if not authed(): return out({"ok": False, "error": "unauthorized"}, 401)
    if request.method == "POST" and not hmac.compare_digest(request.headers.get("X-CSRF-Token", ""), session.get("csrf", "x")):
        return out({"ok": False, "error": "csrf"}, 403)


@app.route("/admin/login", methods=["POST"])
def admin_login():
    ip = request.remote_addr or "?"; now = time.time()
    tries = [x for x in _fails.get(ip, []) if now - x < 300]
    if len(tries) >= 6: return redirect("/admin?e=Thử quá nhiều lần, chờ 5 phút")
    pw = os.getenv("ADMIN_PASS", "")
    ok = bool(pw) and hmac.compare_digest(request.form.get("password", ""), pw) and hmac.compare_digest(request.form.get("username", ""), os.getenv("ADMIN_USER", "admin"))
    if not ok:
        _fails[ip] = tries + [now]; return redirect("/admin?e=Sai tài khoản hoặc mật khẩu")
    session.clear(); session.update(adm=True, adm_until=now + 8 * 3600, csrf=secrets.token_urlsafe(24)); session.permanent = True
    return redirect("/admin")


@app.get("/admin/logout")
def admin_logout():
    session.clear(); return redirect("/admin")


def table_dump(t):
    pd = t.pending; hist = list(t.hist)
    live = [h for h in hist if h["live"]]; l30 = hist[-30:]
    ex = [{"name": k, "p": round(pd["pk"]["ex"][k], 3), "w": round(pd["pk"]["w"][k], 3)} for k in Brain.NAMES] if pd else []
    now = time.time()
    return {"code": t.code, "name": t.name, "enabled": t.enabled, "ready": t.ready, "err": t.err, "ms": t.ms, "n_fetch": t.n_fetch,
            "age": round(now - t.ok_ts) if t.ok_ts else None, "last": t.last,
            "pending": {"phien": pd["phien"], "du_doan": pd["du_doan"], "conf": pd["do_tin_cay"], "p_tai": pd["p_tai"], "temp": pd["pk"]["temp"]} if pd else None,
            "experts": ex, "st_all": stats(hist), "st_live": stats(live), "st_30": stats(l30), "hist": hist[::-1]}


@app.get("/admin/data")
def admin_data():
    g = guard()
    return g or out({"ok": True, "tables": [table_dump(t) for t in TABLES.values()]})


@app.post("/admin/act/<code>/<act>")
def admin_act(code, act):
    g = guard()
    if g: return g
    t = TABLES.get(code)
    if not t or act not in ("on", "off", "refresh", "relearn"): return out({"ok": False, "error": "bad_request"}, 400)
    if act in ("on", "off"):
        t.enabled = act == "on"; save_toggles()
    elif act == "refresh": t.refresh(force=True)
    else:
        t.refresh(force=True, rebuild=True)   # học lại từ 105 phiên upstream
    return out({"ok": True, "enabled": t.enabled, "err": t.err})


LOGIN = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>PAW TX · Đăng nhập</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0a0e16;color:#e8edf6;font:14px system-ui,sans-serif}form{width:min(360px,92vw);background:#121a2a;border:1px solid #222c3f;border-radius:14px;padding:28px}
h1{margin:0 0 18px;font-size:20px}input{width:100%;box-sizing:border-box;margin:6px 0 14px;padding:10px 12px;border-radius:8px;border:1px solid #2d3a52;background:#0e131d;color:inherit}
button{width:100%;padding:11px;border:0;border-radius:8px;background:#4c8dff;color:#fff;font-weight:600;cursor:pointer}.e{background:#3b1420;color:#fb7185;padding:9px 12px;border-radius:8px;margin-bottom:12px}</style>
<form method=post action=/admin/login><h1>PAW TX · Admin</h1>__ERR__<label>Tài khoản</label><input name=username value=admin autocomplete=username><label>Mật khẩu</label><input type=password name=password autocomplete=current-password autofocus><button>Đăng nhập</button></form>"""

PAGE = r"""<!doctype html><html lang=vi><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>PAW TX · Admin</title>
<style>:root{--bg:#080b12;--c:#121a2a;--b:#222c3f;--t:#e8edf6;--m:#9aa8c0;--a:#4c8dff;--g:#10b981;--r:#ef4444;--y:#f59e0b}
html[data-t=light]{--bg:#f6f7f9;--c:#fff;--b:#e5e7eb;--t:#111827;--m:#6b7280}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--t);font:13px/1.5 system-ui,sans-serif}header{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;border-bottom:1px solid var(--b)}
h1{font-size:17px;margin:0}main{max-width:1180px;margin:0 auto;padding:18px;display:grid;gap:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(340px,100%),1fr));gap:16px}
.card{background:var(--c);border:1px solid var(--b);border-radius:12px;padding:16px;min-width:0}.row{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:8px 0;flex-wrap:wrap}@media(max-width:480px){main{padding:12px}header{padding:12px}.card{padding:12px}}.m{color:var(--m)}.mono{font-family:ui-monospace,monospace}
.btn{border:1px solid var(--b);background:transparent;color:var(--t);border-radius:8px;padding:6px 11px;cursor:pointer}.btn:hover{border-color:var(--a)}.p{background:var(--a);border-color:var(--a);color:#fff}
.sw{width:42px;height:24px;border-radius:12px;background:var(--b);position:relative;cursor:pointer;border:0}.sw:after{content:"";position:absolute;top:3px;left:3px;width:18px;height:18px;border-radius:50%;background:#fff;transition:.2s}.sw.on{background:var(--g)}.sw.on:after{left:21px}
.badge{padding:3px 12px;border-radius:99px;font-weight:700}.TAI{background:#8b5cf622;color:#a78bfa}.XIU{background:#4c8dff22;color:#4c8dff}.win{color:var(--g)}.lose{color:var(--r)}
.bar{height:6px;background:var(--b);border-radius:6px;overflow:hidden}.bar i{display:block;height:100%;background:var(--a)}table{width:100%;border-collapse:collapse}th,td{padding:7px 10px;border-bottom:1px solid var(--b);text-align:left;white-space:nowrap}th{color:var(--m);font-size:11px;text-transform:uppercase}
.sc{overflow:auto;max-height:420px}.chip{border:1px solid var(--b);border-radius:8px;padding:6px 10px;flex:1;text-align:center}.chip b{display:block;font-size:16px}.err{color:var(--r)}
#toast{position:fixed;right:16px;bottom:16px;background:var(--c);border:1px solid var(--b);padding:10px 14px;border-radius:10px;display:none}</style>
<header><h1>PAW TX · Admin</h1><div><button class=btn onclick=th()>Sáng/Tối</button> <a class=btn href=/admin/logout>Đăng xuất</a></div></header>
<main><div class=grid id=cards></div><div class=card><div class=row><b>Lịch sử 50 phiên</b><span><button class=btn id=tabhu onclick="tab='hu';draw()">Hũ</button> <button class=btn id=tabmd5 onclick="tab='md5';draw()">MD5</button></span></div><div class=sc id=hist></div></div></main><div id=toast></div>
<script>const CSRF="__CSRF__";let D=[],tab='hu';const $=id=>document.getElementById(id),E=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function th(){const n=document.documentElement.dataset.t==='light'?'dark':'light';document.documentElement.dataset.t=n;localStorage.setItem('tx-t',n)}document.documentElement.dataset.t=localStorage.getItem('tx-t')||'dark';
function toast(m){const t=$('toast');t.textContent=m;t.style.display='block';setTimeout(()=>t.style.display='none',2500)}
async function load(){try{const r=await fetch('/admin/data');if(r.status===401){location.href='/admin';return}D=(await r.json()).tables;draw()}catch(e){}}
async function act(c,a){const r=await fetch('/admin/act/'+c+'/'+a,{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();toast(j.ok?'Đã thực hiện':'Lỗi: '+(j.error||''));load()}
const side=s=>s?'<span class="badge '+s+'">'+(s==='TAI'?'TÀI':'XỈU')+'</span>':'—';
function draw(){$('cards').innerHTML=D.map(t=>{const l=t.last,p=t.pending;return '<div class=card><div class=row><b style="font-size:16px">Bàn '+E(t.name)+'</b><button class="sw '+(t.enabled?'on':'')+'" onclick="act(\''+t.code+'\',\''+(t.enabled?'off':'on')+'\')"></button></div>'
+(t.ready?'<div class=row><span class=m>Phiên trước #'+l.phien+'</span><span class=mono>'+l.xuc_xac.join('-')+' = '+l.tong+'</span>'+side(l.ket_qua)+'</div><div class=row><span class=m>Đã dự đoán</span>'+side(l.du_doan)+'<span>'+({win:'✅',lose:'❌'}[l.trang_thai]||'—')+'</span></div>'
+'<div class=row><b>Dự đoán #'+p.phien+'</b>'+side(p.du_doan)+'<span class=mono>'+p.conf+'%</span></div><div class=row><div class=chip><b>'+t.st_live.ty_le+'%</b><span class=m>live ('+(t.st_live.win+t.st_live.lose)+')</span></div><div class=chip><b>'+t.st_30.ty_le+'%</b><span class=m>30 gần nhất</span></div><div class=chip><b>'+t.st_all.ty_le+'%</b><span class=m>'+t.st_all.win+'W/'+t.st_all.lose+'L</span></div></div>'
+'<div class=m style="margin:10px 0 4px">Chuyên gia AI (p Tài · trọng số) · nhiệt độ '+p.temp+'</div>'+t.experts.map(x=>'<div class=row style="margin:3px 0"><span style="width:70px">'+x.name+'</span><div class=bar style="flex:1"><i style="width:'+Math.round(x.w*100*2.2)+'%"></i></div><span class="mono m">'+Math.round(x.p*100)+'% · '+Math.round(x.w*100)+'%</span></div>').join(''):'<div class="m row">'+(t.enabled?'Đang nạp dữ liệu…':'Bàn đang tắt')+'</div>')
+'<div class=row><span class="m mono">'+(t.age==null?'chưa có dữ liệu':'cập nhật '+t.age+'s trước · '+t.ms+'ms')+'</span><span class=err>'+E(t.err)+'</span></div>'
+'<div class=row><span><button class="btn p" onclick="act(\''+t.code+'\',\'refresh\')">Làm mới</button> <button class=btn onclick="act(\''+t.code+'\',\'relearn\')">Học lại</button></span><span><a class=btn href=/tx/'+t.code+'?pretty=1 target=_blank>/tx/'+t.code+'</a> <a class=btn href=/history/tx/'+t.code+'?pretty=1 target=_blank>history</a></span></div></div>'}).join('');
const t=D.find(x=>x.code===tab);$('hist').innerHTML=t?'<table><tr><th>Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>Dự đoán</th><th>TT</th><th>Nguồn</th></tr>'+t.hist.map(h=>'<tr><td class=mono>#'+h.phien+'</td><td class=mono>'+h.xuc_xac.join('-')+' = '+h.tong+'</td><td>'+side(h.ket_qua)+'</td><td>'+side(h.du_doan)+'</td><td class='+h.trang_thai+'>'+h.icon+'</td><td class=m>'+(h.live?'live':'nạp nhanh')+'</td></tr>').join('')+'</table>':''}
load();setInterval(load,4000)</script></html>"""


@app.get("/admin")
def admin_page():
    if not authed():
        e = request.args.get("e", "")
        if not os.getenv("ADMIN_PASS"): e = "Chưa đặt biến môi trường ADMIN_PASS trên Render"
        html = LOGIN.replace("__ERR__", ('<div class=e>%s</div>' % (e.replace("<", "&lt;"))) if e else "")
        r = make_response(html); r.headers["Content-Type"] = "text/html; charset=utf-8"; return r
    r = make_response(PAGE.replace("__CSRF__", session.get("csrf", ""))); r.headers["Content-Type"] = "text/html; charset=utf-8"; return r


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
