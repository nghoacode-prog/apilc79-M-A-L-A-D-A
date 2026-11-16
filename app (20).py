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
WARM      = 8     # cần ít nhất 8 phiên để có đủ tín hiệu
POLL_SEC  = 4
MIN_GAP   = 3
STALE_SEC = 8

# Hedge hyperparameters
ETA   = 3.0   # learning rate đủ mạnh để weights phân hoá rõ
GAMMA = 0.04  # floor rất thấp → expert tốt được thưởng nhiều
REG   = 0.20  # ghìm nhiệt độ

ICON       = {"win": "✅", "lose": "❌", "cho": "⏳"}
VN         = timezone(timedelta(hours=7))
STATE_FILE = os.getenv("STATE_FILE", "/tmp/paw_tx_toggles.json")

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
    return resp

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
            sid   = int(it["id"])
            dices = [int(x) for x in (it.get("dices") or [])][:3]
            if "point" not in it and not dices: continue
            point = int(it["point"]) if "point" in it else sum(dices)
            res   = str(it.get("resultTruyenThong") or "").upper()
            if res not in ("TAI", "XIU"): res = "TAI" if point >= 11 else "XIU"
            got[sid] = {"id": sid, "dices": dices, "point": point, "result": res}
        except (KeyError, TypeError, ValueError):
            continue
    return [got[k] for k in sorted(got)]

def fetch_sessions(url):
    r = _http.get(url, timeout=(3, 7)); r.raise_for_status()
    return parse_sessions(r.json())

FETCH = fetch_sessions

# ══════════════════════════════════════════════════════════════════════════════
#  BRAIN v3 — AI nâng cấp đáng kể
#  Thêm: Markov-3, alternating pattern, streak bias detector,
#        point-parity expert, momentum expert, anti-chasing bias.
#  Tổng: 13 expert (tăng từ 8) với Hedge online learning.
# ══════════════════════════════════════════════════════════════════════════════
def _logit(p):
    p = min(0.9499, max(0.0501, p))
    return math.log(p / (1 - p))

def _sig(z):
    return 1.0 / (1.0 + math.exp(-max(-15, min(15, z))))

class Brain:
    NAMES = (
        "markov1", "markov2", "markov3",
        "ngram", "alternate", "run",
        "persist", "trend", "revert",
        "dice_bias", "dice_streak",
        "momentum", "anti_chase",
    )
    N = len(NAMES)

    def __init__(self):
        self.r    = deque(maxlen=WINDOW)  # 1=TAI, 0=XIU
        self.pt   = deque(maxlen=WINDOW)  # điểm xúc xắc
        # Hedge: tổng loss luỹ kế mỗi expert (không dùng deque — tích lũy tuyến tính)
        self.L    = {n: 0.0 for n in self.NAMES}
        self.zh   = deque(maxlen=40)      # (z_score, y) để calibrate temp
        self.temp = 1.0
        self.w    = {n: 1.0 / self.N for n in self.NAMES}
        self.t    = 0  # số phiên đã học

    # ─────────────────────────────────────────────────────────────────────────
    # 13 Expert — tín hiệu mạnh, không clamp về 0.5
    # Quy tắc: trả về xác suất TAI trong [0.05, 0.95]
    # ─────────────────────────────────────────────────────────────────────────
    def experts(self):
        r = list(self.r); n = len(r)
        ex = {k: 0.5 for k in self.NAMES}
        if n < 4: return ex
        last = r[-1]

        def follow(L):
            if n < L + 1: return 0, 0
            suf = r[-L:]; k = m = 0
            for i in range(n - L):
                if r[i:i+L] == suf: m += 1; k += r[i+L]
            return k, m

        # ── Markov 1/2/3 — Laplace smoothing nhỏ để tín hiệu sắc hơn ──────
        k1, m1 = follow(1)
        ex["markov1"] = (k1 + 0.5) / (m1 + 1.0)   # sắc hơn Laplace(1)

        if n >= 5:
            k2, m2 = follow(2)
            ex["markov2"] = (k2 + 0.5) / (m2 + 1.0) if m2 >= 1 else ex["markov1"]

        if n >= 8:
            k3, m3 = follow(3)
            ex["markov3"] = (k3 + 0.5) / (m3 + 1.0) if m3 >= 1 else ex["markov2"]

        # ── N-gram dài nhất khớp được ≥ 2 lần ──────────────────────────────
        for L in range(min(6, n-2), 2, -1):
            k, m = follow(L)
            if m >= 2:
                ex["ngram"] = (k + 0.5) / (m + 1.0); break

        # ── Alternate: xen kẽ T-X 10 phiên gần ─────────────────────────────
        win = r[-min(10,n):]
        flips = sum(1 for i in range(1, len(win)) if win[i] != win[i-1])
        alt   = flips / (len(win)-1) if len(win) > 1 else 0.5
        # alt cao → kỳ vọng ngược last; alt thấp → tiếp tục last
        ex["alternate"] = alt*(1-last) + (1-alt)*last

        # ── Run: chuỗi hiện tại vs lịch sử chuỗi ───────────────────────────
        c = 1
        while c < n and r[n-1-c] == last: c += 1
        body = r[:n-c]; reach = cont = 0; i = 0
        while i < len(body):
            j = i
            while j < len(body) and body[j] == body[i]: j += 1
            ln = j - i
            if ln >= c: reach += 1; cont += int(ln > c)
            i = j
        pc = (cont + 1) / (reach + 2)
        ex["run"] = pc if last else 1-pc

        # ── Persist: tỉ lệ giữ nguyên trong 20 phiên gần ───────────────────
        win20 = r[-min(20,n):]
        same  = sum(1 for i in range(1, len(win20)) if win20[i] == win20[i-1])
        ps    = (same + 1) / (len(win20) - 1 + 2)
        ex["persist"] = ps if last else 1-ps

        # ── Trend: EMA nhanh (alpha=0.35) → phản ứng nhanh hơn ─────────────
        ema = 0.5
        for v in r: ema = 0.65*ema + 0.35*v
        ex["trend"] = max(0.05, min(0.95, 0.5 + 1.2*(ema-0.5)))  # khuếch đại

        # ── Revert: mean-reversion 20 phiên ─────────────────────────────────
        mean20 = sum(r[-min(20,n):]) / min(20,n)
        ex["revert"] = max(0.05, min(0.95, 0.5 - 1.2*(mean20-0.5)))

        # ── Dice bias: điểm trung bình 5 phiên ──────────────────────────────
        pts = list(self.pt)
        if pts:
            avg5 = sum(pts[-min(5,len(pts)):]) / min(5,len(pts))
            ex["dice_bias"] = max(0.05, min(0.95, 0.5 - 0.06*(avg5-10.5)))

        # ── Dice streak: chuỗi điểm cao/thấp liên tiếp ──────────────────────
        if len(pts) >= 4:
            hi = sum(1 for p in pts[-4:] if p >= 11)
            ex["dice_streak"] = (hi + 0.5) / 5.0

        # ── Momentum: xung lực ngắn vs dài ──────────────────────────────────
        if n >= 8:
            s5  = sum(r[-5:]) / 5
            l20 = sum(r[-min(20,n):]) / min(20,n)
            ex["momentum"] = max(0.05, min(0.95, 0.5 + 1.5*(s5-l20)))

        # ── Anti-chase: chống bias TAI/XIU quá lệch ─────────────────────────
        tai = sum(r[-min(15,n):]) / min(15,n)
        ex["anti_chase"] = max(0.05, min(0.95, 0.5 - 1.8*(tai-0.5)))

        return ex  # KHÔNG clamp tổng thể — từng expert đã tự clamp

    # ── Dự đoán ──────────────────────────────────────────────────────────────
    def predict(self):
        ex   = self.experts()
        z    = sum(self.w[k] * _logit(ex[k]) for k in self.NAMES)
        p    = _sig(self.temp * z)
        side = "TAI" if p >= 0.5 else "XIU"
        conf = round(max(p, 1-p) * 100)
        return {"p": p, "z": z, "ex": ex, "side": side, "conf": conf,
                "w": dict(self.w), "temp": round(self.temp, 3)}

    # ── Học sau khi biết kết quả ─────────────────────────────────────────────
    def learn(self, pk, y: bool):
        """
        Gọi TRƯỚC observe().
        pk = snapshot predict() đã lưu từ lúc chưa biết kết quả.
        y  = True nếu kết quả là TAI.
        """
        self.t += 1

        # 1. Hedge loss mỗi expert — dùng tổng luỹ kế chuẩn
        for k in self.NAMES:
            p_k = pk["ex"][k]
            self.L[k] += -math.log(max(1e-9, p_k if y else 1-p_k))

        # 2. Hedge weight update: w_k ∝ exp(-ETA * L_k)
        lo = min(self.L.values())
        e  = {k: math.exp(-ETA * (self.L[k]-lo)) for k in self.NAMES}
        Z  = sum(e.values())
        # GAMMA floor thấp sau 15 phiên, cao hơn khi ít data
        gam = GAMMA if self.t >= 15 else 0.15 - (0.15-GAMMA)*(self.t/15)
        self.w = {k: (1-gam)*e[k]/Z + gam/self.N for k in self.NAMES}

        # 3. Calibrate temperature — log-loss trên 40 phiên gần
        self.zh.append((pk["z"], y))
        if len(self.zh) >= 10:
            best, bl = 1.0, 1e9
            zh_list = list(self.zh)
            for i in range(2, 41):   # 0.2 → 4.0
                t = i / 10.0; lo2 = 0.0
                for z2, yy in zh_list:
                    q   = _sig(t*z2)
                    lo2 -= math.log(max(1e-9, q if yy else 1-q))
                lo2 = lo2/len(zh_list) + REG*(t-1)**2
                if lo2 < bl: bl, best = lo2, t
            self.temp = best

    def observe(self, row):
        """Gọi SAU learn() để cập nhật lịch sử."""
        self.r.append(1 if row["result"] == "TAI" else 0)
        self.pt.append(row["point"])

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

def replay(rows):
    """Train Brain trên data quá khứ — KHÔNG lưu hist.
    Luồng đúng: observe(t-1 về trước) → predict(t) → learn khi biết kết quả(t).
    Tức là Brain thấy lịch sử 0..i-1 rồi dự đoán phiên i, sau đó học từ kết quả i.
    """
    b = Brain()
    # Warm-up: nạp WARM phiên đầu vào lịch sử không predict
    for row in rows[:WARM]:
        b.observe(row)
    # Train: từ phiên WARM trở đi — predict → biết kết quả → learn → observe
    for row in rows[WARM:]:
        pk = b.predict()                        # dự đoán dựa trên lịch sử hiện tại
        b.learn(pk, row["result"] == "TAI")     # học từ kết quả thật
        b.observe(row)                          # cập nhật lịch sử
    return b, deque(maxlen=HIST_MAX)  # hist trắng — chỉ live mới được ghi

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
            pd = self.pending; du = None; tt = "khong"
            if pd and pd["phien"] == row["id"]:
                win = pd["du_doan"] == row["result"]
                self.brain.learn(pd["pk"], row["result"] == "TAI")  # learn trước
                self.hist.append(entry(row, pd["pk"], win, True))
                du = pd["du_doan"]; tt = "win" if win else "lose"
            self.brain.observe(row)  # observe sau
            self.last = {
                "phien": row["id"], "xuc_xac": row["dices"],
                "tong": row["point"], "ket_qua": row["result"],
                "du_doan": du, "trang_thai": tt,
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

# ── Login page ─────────────────────────────────────────────────────────────────
LOGIN = """<!doctype html>
<html lang=vi>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>PAW TX · Đăng nhập</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{min-height:100vh;display:grid;place-items:center;
  background:radial-gradient(ellipse 80% 60% at 50% -10%,rgba(37,99,235,.18),transparent),#f1f5f9;
  font:14px/1.6 'Inter',system-ui,sans-serif;color:#0f172a}
.card{width:min(380px,94vw);background:#fff;border:1px solid #e2e8f0;border-radius:22px;
  padding:36px;box-shadow:0 8px 32px rgba(15,23,42,.1)}
.logo{display:flex;justify-content:center;margin-bottom:22px}
.logo svg{width:52px;height:52px;animation:float 3s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
h1{text-align:center;font-size:21px;font-weight:850;letter-spacing:-.04em;margin-bottom:4px}
.sub{text-align:center;color:#64748b;font-size:13px;margin-bottom:28px}
label{font-size:10.5px;font-weight:750;color:#64748b;letter-spacing:.06em;text-transform:uppercase}
input{width:100%;margin:6px 0 16px;padding:10px 13px;border:1px solid #e2e8f0;
  border-radius:10px;background:#f8faff;color:#0f172a;font:inherit;outline:none;transition:.15s}
input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.12);background:#fff}
button{width:100%;padding:11px;border:0;border-radius:10px;background:#2563eb;color:#fff;
  font:600 14px inherit;cursor:pointer;transition:.15s}
button:hover{background:#1d4ed8}
.err{background:#fff1f2;border:1px solid #fecdd3;color:#dc2626;padding:10px 13px;
  border-radius:9px;font-size:13px;margin-bottom:16px}
.foot{text-align:center;margin-top:18px;font-size:11.5px;color:#94a3b8}
</style>
<div class=card>
  <div class=logo>
    <svg viewBox="0 0 52 52" fill="none">
      <defs>
        <linearGradient id=g1 x1=0 y1=0 x2=1 y2=1>
          <stop offset=0% stop-color=#60a5fa/>
          <stop offset=50% stop-color=#3b82f6/>
          <stop offset=100% stop-color=#4f46e5/>
        </linearGradient>
        <filter id=sh><feDropShadow dx=0 dy=3 stdDeviation=3 flood-color=#2563eb flood-opacity=.4/></filter>
      </defs>
      <path d="M26 4C26 4 40 20 40 30C40 38.3 33.7 45 26 45C18.3 45 12 38.3 12 30C12 20 26 4 26 4Z" fill="url(#g1)" filter="url(#sh)"/>
      <ellipse cx=20 cy=27.5 rx=4 ry=6.5 fill="rgba(255,255,255,.65)" transform="rotate(-28 20 27.5)"/>
    </svg>
  </div>
  <h1>PAW TX Admin</h1>
  <div class=sub>Hệ thống quản lý dự đoán LC79</div>
  __ERR__
  <form method=post action=/admin/login>
    <label>Tài khoản</label>
    <input name=username value=admin autocomplete=username>
    <label>Mật khẩu</label>
    <input type=password name=password autocomplete=current-password autofocus>
    <button type=submit>Đăng nhập</button>
  </form>
  <div class=foot>Phiên có hiệu lực 8 giờ</div>
</div>"""

# ── Admin SPA ──────────────────────────────────────────────────────────────────
PAGE = r"""<!doctype html>
<html lang=vi>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>PAW TX · Admin</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
:root{
  --bg:#f1f5f9; --bg2:#e9edf5; --s:#fff; --bd:#e2e8f0; --bd2:#bfdbfe;
  --t:#0f172a;  --t2:#475569; --t3:#94a3b8;
  --blue:#2563eb; --blue-d:#1d4ed8; --blue-li:#eff6ff;
  --indigo:#4f46e5; --indigo-li:#f5f3ff;
  --green:#16a34a; --green-li:#f0fdf4;
  --red:#dc2626;   --red-li:#fff1f2;
  --amber:#d97706; --amber-li:#fffbeb;
  --sh: 0 1px 3px rgba(15,23,42,.06), 0 4px 16px rgba(15,23,42,.04);
  --sh2: 0 4px 14px rgba(15,23,42,.08), 0 14px 36px rgba(15,23,42,.06);
}
*{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg);scroll-behavior:smooth}
body{font:13.5px/1.6 'Inter',system-ui,sans-serif;background:var(--bg);color:var(--t);-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.mono{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:11.5px;letter-spacing:.01em}

/* ── layout ── */
.wrap{max-width:1300px;margin:0 auto;padding:0 20px}

/* ── topbar ── */
.topbar{position:sticky;top:0;z-index:50;height:60px;
  background:rgba(255,255,255,.9);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
  border-bottom:1px solid var(--bd);box-shadow:0 1px 0 var(--bd)}
.tinner{display:flex;align-items:center;justify-content:space-between;height:100%;gap:14px}
.brand{display:flex;align-items:center;gap:10px;font-size:15px;font-weight:850;letter-spacing:-.035em;color:var(--t)}
.brand svg{width:32px;height:32px;animation:dropFloat 3.5s ease-in-out infinite;flex-shrink:0}
@keyframes dropFloat{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-5px) scale(1.04)}}
.tbright{display:flex;align-items:center;gap:8px}
.tick{font-size:11px;color:var(--t3);display:flex;align-items:center;gap:5px}
.tick-dot{width:7px;height:7px;border-radius:50%;background:#22c55e;
  box-shadow:0 0 0 3px rgba(34,197,94,.18);animation:pulse 2s infinite}
@keyframes pulse{50%{box-shadow:0 0 0 7px transparent}}

/* ── buttons ── */
.btn{display:inline-flex;align-items:center;gap:6px;padding:7px 13px;
  border:1px solid var(--bd);border-radius:9px;font:600 12px 'Inter',system-ui;
  color:var(--t2);background:var(--s);cursor:pointer;white-space:nowrap;
  transition:all .15s;line-height:1}
.btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-li)}
.btn:active{transform:scale(.97)}
.btn-blue{background:var(--blue);border-color:var(--blue);color:#fff}
.btn-blue:hover{background:var(--blue-d);color:#fff}
.btn-sm{padding:5px 10px;font-size:11.5px;border-radius:7px}

/* ── switch ── */
.sw{width:40px;height:22px;border-radius:11px;background:var(--bd);
  position:relative;cursor:pointer;border:0;flex-shrink:0;transition:background .2s}
.sw::after{content:'';position:absolute;top:3px;left:3px;width:16px;height:16px;
  border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.2);transition:.2s}
.sw.on{background:var(--green)}.sw.on::after{left:21px}

/* ── cards ── */
.card{background:var(--s);border:1px solid var(--bd);border-radius:16px;
  padding:20px;box-shadow:var(--sh);min-width:0;transition:border-color .18s,box-shadow .18s}
.card:hover{border-color:var(--bd2);box-shadow:var(--sh2)}

/* ── predict banner ── */
.pred-banner{
  background:linear-gradient(130deg,#1d4ed8 0%,#4f46e5 60%,#7c3aed 100%);
  border-radius:18px;padding:22px 26px;color:#fff;position:relative;overflow:hidden;
  animation:fadeUp .4s ease both
}
.pred-banner::after{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 90% at 85% 50%,rgba(255,255,255,.12),transparent);pointer-events:none}
.pb-label{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;opacity:.75;margin-bottom:6px}
.pb-side{font-size:36px;font-weight:900;letter-spacing:-.05em;line-height:1}
.pb-conf{font-size:14px;font-weight:700;opacity:.88;margin-top:4px}
.pb-meta{font-size:11.5px;opacity:.7;margin-top:2px}
.pb-right{text-align:right;position:relative;z-index:1}
.pb-prev-label{font-size:10.5px;font-weight:700;opacity:.65;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px}

/* ── stat chips ── */
.chips{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 0}
.chip{flex:1;min-width:90px;background:var(--bg2);border:1px solid var(--bd);
  border-radius:12px;padding:12px 14px;text-align:center;transition:border-color .15s}
.chip:hover{border-color:var(--bd2)}
.chip-val{font-size:20px;font-weight:850;letter-spacing:-.04em;line-height:1;margin-bottom:3px}
.chip-lbl{font-size:10px;color:var(--t3);letter-spacing:.04em;font-weight:600;text-transform:uppercase}
.chip-val.green{color:var(--green)}.chip-val.red{color:var(--red)}.chip-val.blue{color:var(--blue)}

/* ── badges ── */
.badge{display:inline-flex;align-items:center;padding:3px 9px;border-radius:20px;
  font-size:10.5px;font-weight:800;border:1px solid;white-space:nowrap;letter-spacing:.02em}
/* TÀI = đỏ · XỈU = xanh nước (cyan/teal) */
.TAI{background:#fff1f2;color:#dc2626;border-color:#fca5a5;font-weight:900}
.XIU{background:#ecfeff;color:#0891b2;border-color:#a5f3fc;font-weight:900}
.win{background:var(--green-li);color:var(--green);border-color:#bbf7d0}
.lose{background:var(--red-li);color:var(--red);border-color:#fecdd3}
.neutral{background:var(--bg2);color:var(--t2);border-color:var(--bd)}

/* ── health ── */
.hdot{width:7px;height:7px;border-radius:50%;display:inline-block;flex-shrink:0}
.hdot.ok{background:#22c55e;box-shadow:0 0 0 3px rgba(34,197,94,.2);animation:pulse 2s infinite}
.hdot.warn{background:#f59e0b;box-shadow:0 0 0 3px rgba(245,158,11,.18)}
.hdot.bad{background:#ef4444;box-shadow:0 0 0 3px rgba(239,68,68,.18);animation:pulse 1s infinite}

/* ── progress bar ── */
.prog{height:5px;background:var(--bd);border-radius:5px;overflow:hidden;flex:1;min-width:0}
.prog i{display:block;height:100%;border-radius:5px;transition:width .3s ease}

/* ── expert rows ── */
.ex-row{display:grid;grid-template-columns:108px 1fr 68px;align-items:center;gap:8px;padding:4px 0}
.ex-name{font-size:11.5px;font-weight:600;color:var(--t2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* ── tables ── */
.tbl-scroll{overflow-x:auto;border-radius:12px;border:1px solid var(--bd)}
table{width:100%;border-collapse:separate;border-spacing:0;white-space:nowrap}
thead{position:sticky;top:0;z-index:2}
th{padding:10px 14px;font-size:9.5px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--t3);background:var(--bg2);border-bottom:1px solid var(--bd);text-align:left;font-weight:800}
td{padding:11px 14px;font-size:12.5px;border-bottom:1px solid #f1f5f9;color:var(--t2);background:var(--s)}
tbody tr:hover td{background:#f8fbff}
tbody tr:last-child td{border-bottom:0}

/* ── section header ── */
.sec-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.sec-title{font-size:15px;font-weight:800;letter-spacing:-.03em;color:var(--t)}
.sec-sub{font-size:11.5px;color:var(--t3);margin-top:2px}

/* ── layout grid ── */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.row{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:8px 0}
.row+.row{border-top:1px solid var(--bd)}
.flex{display:flex;align-items:center;gap:8px}
.muted{color:var(--t3)}.small{font-size:11.5px}

/* ── err ── */
.err-box{background:var(--red-li);border:1px solid #fecdd3;color:var(--red);
  padding:9px 13px;border-radius:9px;font-size:12px;margin-top:12px;display:flex;gap:7px;align-items:center}

/* ── toast ── */
#toast{position:fixed;right:16px;bottom:20px;z-index:9999;background:var(--s);
  border:1px solid var(--bd);border-left:3px solid #22c55e;padding:11px 16px;
  border-radius:11px;box-shadow:var(--sh2);display:none;font-size:13px;min-width:230px;
  animation:fadeUp .2s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ── page sections ── */
.section{padding:20px 0 0}
.sep{height:1px;background:var(--bd);margin:24px 0}

/* ── live badge ── */
.live-badge{display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:700;
  padding:2px 8px;border-radius:20px;background:#fff0f0;border:1px solid #fecdd3;color:var(--red)}
.live-dot{width:5px;height:5px;border-radius:50%;background:var(--red);animation:pulse .8s infinite}

/* ── countdown ── */
.count-wrap{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--t3)}
#countdown{font-weight:700;color:var(--blue);font-variant-numeric:tabular-nums}

@media(max-width:860px){
  .g2{grid-template-columns:1fr}
  .pred-banner{padding:18px 20px}
  .pb-side{font-size:28px}
}
@media(max-width:540px){
  .wrap{padding:0 12px}
  .topbar{height:52px}
  .chips{gap:7px}
  .ex-row{grid-template-columns:84px 1fr 56px}
  .pbinner{flex-direction:column;gap:14px}
  .pb-right{text-align:left}
}
</style>
</head>
<body>

<!-- ── TOPBAR ── -->
<div class=topbar>
  <div class="wrap tinner">
    <div class=brand>
      <svg viewBox="0 0 36 36" fill="none">
        <defs>
          <linearGradient id=lg x1=0 y1=0 x2=1 y2=1>
            <stop stop-color=#60a5fa/><stop offset=50% stop-color=#3b82f6/><stop offset=100% stop-color=#4f46e5/>
          </linearGradient>
          <filter id=sh2><feDropShadow dx=0 dy=2 stdDeviation=2.5 flood-color=#2563eb flood-opacity=.4/></filter>
        </defs>
        <path d="M18 3C18 3 28 14.5 28 22C28 27.5 23.5 32 18 32C12.5 32 8 27.5 8 22C8 14.5 18 3 18 3Z" fill="url(#lg)" filter="url(#sh2)"/>
        <ellipse cx=14 cy=20.5 rx=3 ry=4.8 fill="rgba(255,255,255,.65)" transform="rotate(-28 14 20.5)"/>
      </svg>
      PAW TX Admin
    </div>
    <div class=tbright>
      <div class=tick><div class=tick-dot></div><span id=tickLbl>Đang kết nối…</span></div>
      <div class=count-wrap>Làm mới sau <span id=countdown>4</span>s</div>
      <a class=btn href=/admin/logout>Đăng xuất</a>
    </div>
  </div>
</div>

<!-- ── CONTENT ── -->
<div class=wrap>

  <!-- DỰ ĐOÁN -->
  <div class=section>
    <div class=g2 id=predCards></div>
  </div>

  <div class=sep></div>

  <!-- LỊCH SỬ HŨ -->
  <div class=section id=secHu>
    <div class=sec-head>
      <div>
        <div class=sec-title>📊 Lịch sử dự đoán · Bàn Hũ</div>
        <div class=sec-sub id=subHu>50 phiên gần nhất</div>
      </div>
      <div class=flex id=statHu></div>
    </div>
    <div class=tbl-scroll><table>
      <thead><tr><th>#Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>Dự đoán</th><th>Trạng thái</th><th>Nguồn</th></tr></thead>
      <tbody id=rowsHu></tbody>
    </table></div>
  </div>

  <div class=sep></div>

  <!-- LỊCH SỬ MD5 -->
  <div class=section id=secMd5 style="padding-bottom:40px">
    <div class=sec-head>
      <div>
        <div class=sec-title>📊 Lịch sử dự đoán · Bàn MD5</div>
        <div class=sec-sub id=subMd5>50 phiên gần nhất</div>
      </div>
      <div class=flex id=statMd5></div>
    </div>
    <div class=tbl-scroll><table>
      <thead><tr><th>#Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>Dự đoán</th><th>Trạng thái</th><th>Nguồn</th></tr></thead>
      <tbody id=rowsMd5></tbody>
    </table></div>
  </div>

</div>
<div id=toast></div>

<script>
const CSRF="__CSRF__";
let D=[], _cdInt=null, _cdVal=4;
const $=id=>document.getElementById(id);
const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* ── Toast ── */
function toast(m, ok=true){
  const el=$('toast');
  el.innerHTML=`<span style="font-weight:800;font-size:14px">${ok?'✓':'✕'}</span> ${E(m)}`;
  el.style.borderLeftColor=ok?'#22c55e':'#ef4444';
  el.style.display='block';
  clearTimeout(el._t); el._t=setTimeout(()=>el.style.display='none', 3000);
}

/* ── Action ── */
async function act(c,a){
  try{
    const r=await fetch('/admin/act/'+c+'/'+a,{method:'POST',headers:{'X-CSRF-Token':CSRF}});
    const j=await r.json(); toast(j.ok?'Đã thực hiện: '+a:'Lỗi: '+(j.loi||'?'), j.ok); load();
  }catch(e){toast('Lỗi mạng',false)}
}

/* ── Helpers ── */
const side=s=>s?`<span class="badge ${s}">${s==='TAI'?'TÀI':'XỈU'}</span>`:'—';

function statBadges(st){
  return `<span class="badge win" style="font-size:12px;padding:4px 11px">✅ ${st.win} thắng</span>
          <span class="badge lose" style="font-size:12px;padding:4px 11px">❌ ${st.lose} thua</span>
          <span class="badge neutral" style="font-size:12px;padding:4px 11px">📈 ${st.ty_le}%</span>`;
}

function tableRows(hist){
  if(!hist||!hist.length) return '<tr><td colspan=6 style="text-align:center;padding:28px;color:#94a3b8">Chưa có dữ liệu</td></tr>';
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
      ?'<span class="live-badge"><span class=live-dot></span>live</span>'
      :'<span class="muted small">📂 nạp</span>'}</td>
  </tr>`).join('');
}

/* ── Draw predict cards ── */
function drawPred(){
  $('predCards').innerHTML = D.map(t=>{
    const l=t.last, p=t.pending, en=t.enabled, rd=t.ready;
    const hdot=`<span class="hdot ${!en?'warn':t.err?'bad':'ok'}"></span>`;
    const ageStr=t.age==null?'–':(t.age<60?t.age+'s':Math.floor(t.age/60)+'m')+' trước';

    if(!rd||!l||!p){
      return `<div class=card>
        <div class=row><b style="font-size:16px;font-weight:800">${E(t.name)}</b>
          <button class="sw ${en?'on':''}" onclick="act('${t.code}','${en?'off':'on'}')"></button>
        </div>
        <div class="muted small" style="padding:16px 0">${en?'Đang nạp dữ liệu…':'Bàn đang tắt'}</div>
      </div>`;
    }

    const prevOk=l.trang_thai==='win';
    const prevIcon=l.trang_thai==='win'?'✅':l.trang_thai==='lose'?'❌':'—';

    const isTai = p.du_doan==='TAI';
    const pbSideColor = isTai ? '#fca5a5' : '#67e8f9';
    const pbSideShadow = isTai ? 'rgba(220,38,38,.4)' : 'rgba(8,145,178,.4)';
    return `<div class=card>
      <!-- header -->
      <div class=row style="padding-bottom:14px;border-bottom:1px solid var(--bd);margin-bottom:14px">
        <span class=flex style="gap:10px">
          ${hdot}
          <span style="font-size:16px;font-weight:850;letter-spacing:-.03em">Bàn ${E(t.name)}</span>
          <span class="badge ${rd?'win':'lose'}" style="font-size:10px">${rd?'Online':'Offline'}</span>
        </span>
        <span class=flex>
          <span class="muted small">${ageStr} · ${t.ms}ms</span>
          <button class="sw ${en?'on':''}" onclick="act('${t.code}','${en?'off':'on'}')" title="${en?'Tắt':'Bật'}"></button>
        </span>
      </div>

      <!-- predict banner -->
      <div class=pred-banner>
        <div class="flex pbinner" style="justify-content:space-between;gap:16px;position:relative;z-index:1">
          <div>
            <div class=pb-label>DỰ ĐOÁN PHIÊN #${p.phien}</div>
            <div class=pb-side style="color:${pbSideColor};text-shadow:0 2px 16px ${pbSideShadow}">${isTai?'TÀI ☀️':'XỈU 🌙'}</div>
            <div class=pb-conf>Độ tin cậy: <b>${p.conf}%</b></div>
            <div class=pb-meta>p(TÀI) = ${p.p_tai} · temp = ${p.temp}</div>
          </div>
          <div class=pb-right>
            <div class=pb-prev-label>Phiên trước #${l.phien}</div>
            <div style="display:flex;align-items:center;gap:8px;justify-content:flex-end;margin:4px 0">
              ${side(l.ket_qua)}
              <span style="font-size:11.5px;opacity:.8;font-family:'JetBrains Mono',monospace">
                ${(l.xuc_xac||[]).join('-')} = ${l.tong}
              </span>
            </div>
            <div style="display:flex;align-items:center;gap:7px;justify-content:flex-end">
              <span style="font-size:11.5px;opacity:.75">Dự đoán: ${side(l.du_doan)}</span>
              <span style="font-size:16px">${prevIcon}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- stats chips -->
      <div class=chips>
        <div class=chip>
          <div class="chip-val ${t.st_live.ty_le>=50?'green':'red'}">${t.st_live.ty_le}%</div>
          <div class=chip-lbl>${(t.st_live.win+t.st_live.lose)>0&&t.st_live.win+t.st_live.lose<=5?'5 gần nhất':'Live ('+( t.st_live.win+t.st_live.lose)+')'}</div>
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

      <!-- experts -->
      <div style="margin-top:16px;border-top:1px solid var(--bd);padding-top:14px">
        <div style="font-size:11px;font-weight:800;color:var(--t3);letter-spacing:.07em;text-transform:uppercase;margin-bottom:10px">
          13 Expert AI · p(TÀI) / trọng số
        </div>
        ${t.experts.map(x=>{
          const pp=Math.round(x.p*100), ww=Math.round(x.w*100);
          const col=pp>55?'var(--blue)':pp<45?'var(--indigo)':'var(--t3)';
          return `<div class=ex-row>
            <span class=ex-name>${x.name.replace(/_/g,' ')}</span>
            <div class=prog><i style="width:${pp*2}%;background:${col}"></i></div>
            <span class="mono" style="font-size:10.5px;color:var(--t3);text-align:right">${pp}%·${ww}%</span>
          </div>`;
        }).join('')}
      </div>

      <!-- actions -->
      <div class=row style="margin-top:14px;padding-top:12px;border-top:1px solid var(--bd)">
        <span class=flex>
          <button class="btn btn-blue btn-sm" onclick="act('${t.code}','refresh')">↻ Làm mới</button>
          <button class="btn btn-sm" onclick="act('${t.code}','relearn')">🧠 Học lại</button>
        </span>
        <span class=flex>
          <a class="btn btn-sm" href="/tx/${t.code}?pretty=1" target=_blank>/tx</a>
          <a class="btn btn-sm" href="/history/tx/${t.code}?pretty=1" target=_blank>/history</a>
        </span>
      </div>

      ${t.err?`<div class=err-box>⚠ ${E(t.err)}</div>`:''}
    </div>`;
  }).join('');
}

/* ── Draw history tables ── */
function drawHistory(){
  const hu  = D.find(x=>x.code==='hu');
  const md5 = D.find(x=>x.code==='md5');

  if(hu){
    $('rowsHu').innerHTML = tableRows(hu.hist);
    $('statHu').innerHTML = statBadges(hu.st_all);
    $('subHu').textContent = `${hu.hist.length} phiên · cập nhật ${hu.age!=null?hu.age+'s trước':'–'}`;
  }
  if(md5){
    $('rowsMd5').innerHTML = tableRows(md5.hist);
    $('statMd5').innerHTML = statBadges(md5.st_all);
    $('subMd5').textContent = `${md5.hist.length} phiên · cập nhật ${md5.age!=null?md5.age+'s trước':'–'}`;
  }
}

/* ── Countdown ── */
function startCountdown(){
  clearInterval(_cdInt); _cdVal=4;
  $('countdown').textContent=_cdVal;
  _cdInt=setInterval(()=>{
    _cdVal=Math.max(0,_cdVal-1);
    $('countdown').textContent=_cdVal;
  },1000);
}

/* ── Load ── */
async function load(){
  try{
    const r=await fetch('/admin/data');
    if(r.status===401){location.href='/admin';return}
    D=(await r.json()).tables;
    $('tickLbl').textContent='Tự động cập nhật';
    drawPred(); drawHistory(); startCountdown();
  }catch(e){
    $('tickLbl').textContent='Lỗi kết nối';
    toast('Mất kết nối, thử lại…',false);
  }
}

load(); setInterval(load,4000);
</script>
</body>
</html>"""

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
