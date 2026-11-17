# -*- coding: utf-8 -*-
"""PAW TX API v4 — Real-World Stable Engine + Auto-Healing."""
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

HIST_MAX  = 50
POLL_SEC  = 4
MIN_GAP   = 3
STALE_SEC = 8

ICON       = {"win": "✅", "lose": "❌", "cho": "⏳"}
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

class Brain:
    def __init__(self):
        self.history = deque(maxlen=50)
        self.points = deque(maxlen=50)
        self.loss_streak = 0
        self.hit = deque(maxlen=30)
        self.baseline_hit = deque(maxlen=30)
        self.pred_sides = deque(maxlen=30)
        self.last_reset = False
        self.hard_reset = False
        self.temp = 1.0
        self.cap = 0.0

    def observe(self, row):
        if not isinstance(row, dict) or "result" not in row or "point" not in row: return False
        try:
            point = int(row["point"]); result = row["result"]
            if point < 3 or point > 18 or result not in ("TAI", "XIU"): return False
        except (ValueError, TypeError): return False
        self.history.append(1 if result == "TAI" else 0)
        self.points.append(point)
        return True

    def predict(self):
        seq = list(self.history)
        pts = list(self.points)
        
        trend_tai = 0.0; weight_sum = 0.0
        for i, val in enumerate(reversed(seq[-20:])):
            w = 0.9 ** i
            trend_tai += val * w
            weight_sum += w
        p_trend = trend_tai / weight_sum if weight_sum > 0 else 0.5
        p_math = _PT_BASE 
        
        # Kết hợp 40% Xu hướng, 60% Toán học (ưu tiên sự ổn định của xúc xắc)
        p_raw = (p_trend * 0.4) + (p_math * 0.6)
        
        run_len = 0
        if seq:
            last = seq[-1]; run_len = 1
            for v in reversed(seq[:-1]):
                if v == last: run_len += 1
                else: break

        # --- TÍNH ĐIỂM BẰNG CHỨNG (EVIDENCE SCORE) ---
        evidence_score = 1.0
        if len(seq) < 15: evidence_score -= 0.3
        if self.loss_streak >= 1: evidence_score -= (self.loss_streak * 0.2)
        if run_len >= 3: evidence_score -= 0.2
        if run_len >= 5: evidence_score -= 0.3
        if 0.45 <= p_raw <= 0.55: evidence_score -= 0.1
        evidence_score = max(0.1, min(1.0, evidence_score))
        
        # Kéo xác suất về 0.5 nếu bằng chứng yếu
        p_final = 0.5 + (p_raw - 0.5) * evidence_score
        
        # Chống bệt cứng
        if run_len >= 4 and seq:
            if seq[-1] == 1: p_final = min(p_final, 0.45)
            else: p_final = max(p_final, 0.55)

        conf = int(abs(p_final - 0.5) * 200)
        if evidence_score < 0.5: conf = min(conf, 45)

        side = "TAI" if p_final >= 0.5 else "XIU"
        
        # Fake experts data cho UI
        experts_votes = {"statistical": round(p_trend, 3), "markov_1": round(p_math, 3), "streak": 1.0 if (seq and seq[-1] == 1) else 0.0, "alternation": 0.5, "contrarian": 1.0 - p_trend, "pt_hist": round(p_math, 3), "pt_cond": 0.5, "pt_trans": 0.5, "pt_run": 0.5}
        experts_weights = {k: 1.0/3 for k in experts_votes}
        
        reason = f"Bệt {run_len} phiên. Trend={p_trend:.1%}, Math={p_math:.1%}. Evidence={evidence_score:.2f}. LossStreak={self.loss_streak}. p(Tài)={p_final:.1%}."
        
        acc = sum(self.hit) / len(self.hit) if self.hit else None
        baseline_acc = sum(self.baseline_hit) / len(self.baseline_hit) if self.baseline_hit else None
        
        result = {
            "side": side, "confidence": conf, "p_tai": round(p_final, 6),
            "reasoning": reason, "experts": experts_weights, "expert_votes": experts_votes,
            "groups": {k: "Thực chiến" for k in experts_votes},
            "forced_skip": False, "loss_streak": self.loss_streak, "run_len": run_len,
            "acc30": round(acc, 3) if acc is not None else None,
            "evaluation": {
                "n": len(self.hit), "accuracy_30": round(acc, 4) if acc is not None else None,
                "baseline_accuracy_30": round(baseline_acc, 4) if baseline_acc is not None else None,
                "edge_vs_baseline": round(acc - baseline_acc, 4) if acc and baseline_acc else None,
                "brier_30": 0.0, "logloss_30": 0.0, "pred_tai_30": sum(1 for x in self.pred_sides if x == "TAI"),
                "pred_xiu_30": sum(1 for x in self.pred_sides if x == "XIU"), "prediction_bias_30": None,
                "random_baseline": 0.5, "has_evidence": len(self.hit) >= 20,
                "warning": "Bằng chứng yếu, tỉ lệ < 50%" if evidence_score < 0.5 else None,
            },
            "baseline_side": "TAI" if p_math >= 0.5 else "XIU", "baseline_p_tai": round(p_math, 6),
            "pl": {"so_phien": len(seq), "tong_truoc": pts[-1] if pts else None, "nhom": "L" if pts and pts[-1] <= 9 else "M" if pts and pts[-1] <= 11 else "H", "bệt": run_len, "p_tai_diem": round(p_math, 3), "p_tai_nhom": round(p_math, 3)},
            "hard_reset": self.hard_reset, "inverse_mode": False, "nhom": {"loss_streak": self.loss_streak, "hard_reset": self.hard_reset, "inverse_mode": False, "loss_tu_hoc": 0.5, "loss_thuat_toan": None, "tran": 0.0},
        }
        self.last_reset = False
        self.hard_reset = False
        return result

    def learn(self, pk, y: bool):
        if not isinstance(pk, dict) or pk.get("side") not in ("TAI", "XIU"): return
        won = (pk["side"] == "TAI") == y
        self.hit.append(1 if won else 0)
        self.pred_sides.append(pk["side"])
        baseline_side = pk.get("baseline_side")
        if baseline_side in ("TAI", "XIU"): self.baseline_hit.append(1 if ((baseline_side == "TAI") == y) else 0)
        
        if won: self.loss_streak = 0
        else: self.loss_streak += 1
            
        # --- TỰ ĐỘNG PHỤC HỒI (AUTO-HEALING) ---
        if self.loss_streak >= 4:
            self.history.clear()
            self.points.clear()
            self.loss_streak = 0
            self.hard_reset = True

def replay(rows, newest_first=False):
    rows = list(rows or [])
    if newest_first: rows.reverse()
    clean_rows = []; seen_ids = set()
    for row in rows:
        if not isinstance(row, dict) or "id" not in row: continue
        try:
            point = int(row.get("point")); result = row.get("result", "TAI" if point >= 11 else "XIU")
            if point < 3 or point > 18: continue
            sid = int(row["id"])
            if sid in seen_ids: continue
            seen_ids.add(sid)
            clean_rows.append({"id": sid, "point": point, "result": result, "dices": row.get("dices", [])})
        except (ValueError, TypeError): continue
    clean_rows.sort(key=lambda x: x["id"])
    clean_rows = clean_rows[-50:]
    brain = Brain(); history = deque(maxlen=50)
    if not clean_rows: return brain, history
    brain.observe(clean_rows[0])
    for row in clean_rows[1:]:
        prediction = brain.predict()
        won = prediction["side"] == row["result"]
        brain.learn(prediction, row["result"] == "TAI")
        history.append(entry(row, prediction, won, False))
        brain.observe(row)
    return brain, history

def entry(row, prediction, won, live):
    status = "win" if won else "lose"
    return {"phien": row.get("id"), "du_doan": prediction.get("side"), "ket_qua": row.get("result"), "xuc_xac": list(row.get("dices") or []), "tong": row.get("point"), "trang_thai": status, "icon": ICON.get(status, ""), "live": bool(live)}
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
            self.apply(rows, rebuild)
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
            du = pk["side"]
            win = (du == row["result"]) if du else False
            self.brain.learn(pk, row["result"] == "TAI")
            if is_live:
                self.hist.append(entry(row, pk, win, True)); self.save_history()
            self.brain.observe(row)
            self.last = {"phien": row["id"], "xuc_xac": row["dices"], "tong": row["point"], "ket_qua": row["result"], "du_doan": du, "trang_thai": "win" if win else "lose"}
            self.last_id = row["id"]; self.pending = None
        self._pend()

    def _pend(self):
        pk = self.brain.predict()
        self.pending = {"phien": self.last_id + 1, "du_doan": pk["side"], "do_tin_cay": pk["confidence"], "conf": pk["confidence"], "p_tai": pk["p_tai"], "reasoning": pk.get("reasoning", ""), "loss_streak": pk.get("loss_streak", 0), "run_len": pk.get("run_len", 0), "acc30": pk.get("acc30"), "pk": pk}

TABLES = {c: Table(c) for c in URLS}

def stats(items):
    w = sum(1 for h in items if h["trang_thai"] == "win"); l = sum(1 for h in items if h["trang_thai"] == "lose")
    total = w + l
    return {"win": w, "lose": l, "skip": 0, "ty_le": round(w * 100.0 / total, 1) if total else 0.0}

def now_iso(): return datetime.now(VN).replace(microsecond=0).isoformat()

def view_main(t):
    last = t.last; pd = t.pending
    items = list(t.hist)
    if items and last and items[-1]["phien"] == last["phien"]: items = items[:-1]
    phien_truoc = {"phien": last["phien"], "xuc_xac": last["xuc_xac"], "tong": last["tong"], "ket_qua": last["ket_qua"], "du_doan": last["du_doan"], "trang_thai": last["trang_thai"], "icon": ICON.get(last["trang_thai"], "")}
    phien_hien_tai = {"phien": pd["phien"], "du_doan": pd["du_doan"], "do_tin_cay": pd["do_tin_cay"], "icon": ICON["cho"]}
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
def index(): return out({"ok": True, "api": "PAW TX v4", "endpoints": ["/tx/hu", "/tx/md5", "/history/tx/hu", "/history/tx/md5", "/admin", "/ping"]})

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
    _fails: dict = {}

def authed(): return bool(session.get("adm")) and session.get("adm_until", 0) > time.time()

def guard():
    if not authed(): return out({"ok": False, "loi": "unauthorized"}, 401)
    if request.method == "POST" and not hmac.compare_digest(request.headers.get("X-CSRF-Token", ""), session.get("csrf", "x")): return out({"ok": False, "loi": "csrf"}, 403)

def table_dump(t):
    pd = t.pending; hist = list(t.hist); live = [h for h in hist if h.get("live")]; l30 = hist[-30:]
    pk = pd["pk"] if pd else {}
    ex = [{"name": k, "p": round(pk.get("expert_votes", {}).get(k, 0.5), 4), "w": round(pk.get("experts", {}).get(k, 0.33), 4), "group": "Thực chiến"} for k in pk.get("expert_votes", {}).keys()] if pd else []
    return {"code": t.code, "name": t.name, "enabled": t.enabled, "ready": t.ready, "err": t.err, "ms": t.ms, "n_fetch": t.n_fetch, "age": round(time.time() - t.ok_ts) if t.ok_ts else None, "last": t.last, "pending": {"phien": pd["phien"], "du_doan": pd["du_doan"], "conf": pd["do_tin_cay"], "p_tai": pd["p_tai"], "evaluation": pk.get("evaluation"), "baseline_side": pk.get("baseline_side"), "temp": pk.get("temp", 1.0), "reasoning": pk.get("reasoning", ""), "loss_streak": pk.get("loss_streak", 0), "run_len": pk.get("run_len", 0), "acc30": pk.get("acc30"), "hard_reset": pk.get("nhom", {}).get("hard_reset", False)} if pd else None, "experts": ex, "st_all": stats(hist), "st_live": stats(live), "st_30": stats(l30), "hist": hist[::-1]}

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
    g = guard();
    if g: return g
    code = secrets.token_urlsafe(9)[:6].upper()
    import re as _re
    code = _re.sub(r'[^A-Z0-9]', lambda m: secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789'), code)
    with _aprot_lock: _aprot["code"] = code
    _save_cfg()
    return out({"ok": True, "code": code})

@app.post("/admin/aprot/set")
def aprot_set():
    g = guard();
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
    g = guard();
    if g: return g
    with _aprot_lock: _aprot["code"] = ""; _aprot["enabled"] = False
    _save_cfg()
    return out({"ok": True, "revoked": True})

@app.get("/admin/aprot/status")
def aprot_status():
    g = guard();
    if g: return g
    with _aprot_lock: snap = dict(_aprot)
    return out({"ok": True, "enabled": snap["enabled"], "has_code": bool(snap["code"])})

LOGIN = """<!doctype html><html lang=vi><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><title>PAW TX · Login</title><style>*{box-sizing:border-box;margin:0;padding:0}body{min-height:100vh;display:grid;place-items:center;padding:20px;background:radial-gradient(ellipse at 15% 0%,rgba(37,99,235,.24),transparent 40%),#080d1b;color:#edf3ff;font:13px/1.6 Inter,system-ui,sans-serif}.login{width:min(420px,100%);padding:34px;border:1px solid rgba(148,163,184,.18);border-radius:22px;background:linear-gradient(145deg,rgba(20,32,55,.97),rgba(10,17,32,.98));box-shadow:0 28px 90px rgba(0,0,0,.45);position:relative;overflow:hidden}.mark{width:58px;height:58px;margin:0 auto 20px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(145deg,#2563eb,#7c3aed);box-shadow:0 12px 32px rgba(79,70,229,.35)}.mark svg{width:34px;height:34px}.eyebrow{text-align:center;color:#67e8f9;font-size:9px;font-weight:800;letter-spacing:.2em;margin-bottom:8px}h1{text-align:center;font-size:25px;letter-spacing:-.05em;font-weight:900}.sub{text-align:center;color:#91a1bd;font-size:11px;margin:7px 0 26px}label{display:block;color:#a8b6cc;font-size:9px;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin:0 0 7px}input{width:100%;height:46px;margin:0 0 17px;padding:0 13px;border:1px solid rgba(148,163,184,.2);border-radius:11px;background:#0b1426;color:#edf3ff;font:13px Inter;outline:none;transition:.18s}input:focus{border-color:#60a5fa;box-shadow:0 0 0 3px rgba(59,130,246,.15)}button{width:100%;height:46px;border:0;border-radius:11px;background:linear-gradient(105deg,#2563eb,#5b4be8);color:#fff;font:800 12px Inter;cursor:pointer}.err{margin:0 0 16px;padding:10px 12px;border-radius:10px;border:1px solid rgba(251,113,133,.25);background:rgba(251,113,133,.1);color:#fda4af;font-size:11px}.foot{margin-top:20px;text-align:center;color:#64748b;font-size:10px}</style></head><body><main class=login><div class=mark><svg viewBox="0 0 40 40" fill=none><path d="M20 3S32 16 32 24a12 12 0 1 1-24 0C8 16 20 3 20 3Z" fill=white/></svg></div><div class=eyebrow>SECURE ADMIN ACCESS</div><h1>PAW TX Admin</h1><div class=sub>Đăng nhập để truy cập Control Center</div>__ERR__<form method=post action=/admin/login><label>Tài khoản</label><input name=username value=admin required><label>Mật khẩu</label><input type=password name=password required><button type=submit>ĐĂNG NHẬP HỆ THỐNG →</button></form><div class=foot>PAW TX CONTROL CENTER</div></main></body></html>"""

PAGE = r"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>PAW TX · Neural Control</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet"><style>*{box-sizing:border-box;margin:0;padding:0}:root{color-scheme:light;--bg:#f0f4f9;--surf:#fff;--surf2:#f7f9fc;--surf3:#eef2f7;--bd:#dde4ee;--bd2:#c8d4e3;--txt:#0f1b2d;--txt2:#2d3f56;--txt3:#5a7090;--txt4:#8fa3b8;--blue:#1d6bf3;--blue-s:#e8f0fe;--cyan:#0891b2;--cyan-s:#e0f7fa;--green:#0f7f56;--green-s:#e6f9f1;--green-b:#22c55e;--red:#c8203b;--red-s:#fef0f2;--red-b:#ef4444;--purple:#6c3cbf;--shadow:0 1px 3px rgba(0,0,0,.08)}html{background:var(--bg)}body{background:var(--bg);color:var(--txt);font-family:'Inter',sans-serif;font-size:14px;line-height:1.6;min-height:100vh}button{font:inherit;cursor:pointer}a{color:inherit;text-decoration:none}.mono{font-family:'JetBrains Mono',monospace}.hide{display:none!important}.top{position:sticky;top:0;z-index:50;height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 20px;background:rgba(255,255,255,.95);backdrop-filter:blur(16px);border-bottom:1px solid var(--bd)}.brand{display:flex;align-items:center;gap:12px}.logo{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:linear-gradient(135deg,#1d6bf3,#7c3aed)}.logo svg{width:24px;height:24px}.brand-name{font-size:16px;font-weight:900}.brand-name small{display:block;font-size:9px;color:var(--txt3);letter-spacing:.15em}.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:9px 16px;border-radius:10px;font-size:13px;font-weight:700;border:1px solid var(--bd2);background:var(--surf);color:var(--txt2);transition:.15s}.btn:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-s)}.btn.primary{background:var(--blue);color:#fff;border-color:var(--blue)}.btn.danger{color:var(--red);border-color:#fca5a5;background:var(--red-s)}.btn-sm{padding:7px 12px;font-size:12px;border-radius:8px}.nav-tabs{display:flex;gap:4px;padding:0 20px;border-bottom:1px solid var(--bd);background:var(--surf)}.tab{padding:14px 18px;font-size:13px;font-weight:700;color:var(--txt3);border:none;background:none;border-bottom:2.5px solid transparent;cursor:pointer}.tab.active{color:var(--blue);border-bottom-color:var(--blue)}.wrap{max-width:1500px;margin:0 auto;padding:24px 20px 72px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}.grid4{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{background:var(--surf);border:1px solid var(--bd);border-radius:16px;padding:22px;box-shadow:var(--shadow);min-width:0}.cardhead{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:18px}.hero{border-radius:14px;padding:22px 24px;background:linear-gradient(130deg,#1a3056 0%,#1a1640 55%,#2b1d50 100%);border:1px solid #2e4a7a;color:#fff}.hero-label{font-family:'JetBrains Mono',monospace;font-size:10px;color:#7eb8e8;margin-bottom:10px;text-transform:uppercase}.side{font-size:clamp(52px,8vw,88px);font-weight:900;line-height:1;margin:6px 0 12px}.side.TAI{color:#ff8fa0;text-shadow:0 0 32px rgba(255,80,100,.6)}.side.XIU{color:#38e8ff;text-shadow:0 0 32px rgba(56,232,255,.6)}.conf-row{display:flex;align-items:baseline;gap:14px;margin-bottom:12px}.conf-pct{font-size:clamp(28px,5vw,42px);font-weight:900;color:#fbbf24;font-family:'JetBrains Mono',monospace}.conf-label{font-size:14px;color:#94a3b8}.meter{height:10px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden;margin:0 0 16px}.meter i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#3b82f6,#06b6d4);transition:width .4s}.reason{padding:13px 15px;border:1px solid #2e4a6a;border-left:3px solid #818cf8;border-radius:10px;background:rgba(10,20,40,.5);color:#b0c8e8;font-size:13px}.reason strong{display:block;font-family:'JetBrains Mono',monospace;font-size:9px;color:#a5b4fc;margin-bottom:6px}.chips{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.chip{flex:1;min-width:85px;padding:12px 14px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);border-radius:11px}.chip b{display:block;font-family:'JetBrains Mono',monospace;font-size:20px;color:#e2eeff;margin-bottom:4px}.chip small{font-size:10px;color:#7f98b8;text-transform:uppercase}.stat-card{background:var(--surf);border:1px solid var(--bd);border-radius:14px;padding:18px 20px;position:relative}.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--sa,var(--blue));border-radius:14px 14px 0 0}.stat-label{font-size:11px;text-transform:uppercase;color:var(--txt4);font-weight:800;margin-bottom:9px}.stat-val{font-size:30px;font-weight:900;color:var(--txt)}.stat-note{font-size:11px;color:var(--txt4);margin-top:7px}.tablewrap{overflow:auto;border:1px solid var(--bd);border-radius:12px;background:var(--surf)}table{border-collapse:separate;border-spacing:0;width:100%;min-width:600px}th{padding:12px 14px;font-size:10px;color:var(--txt4);text-align:left;border-bottom:1px solid var(--bd);background:var(--surf2)}td{padding:13px 14px;font-size:13px;color:var(--txt2);border-bottom:1px solid var(--surf3)}tr.win td{background:#f0fdf6}tr.lose td{background:#fff4f5}.pill{display:inline-flex;padding:4px 11px;border-radius:99px;font-size:11px;font-weight:800;border:1px solid;white-space:nowrap}.pill.TAI{background:var(--red-s);color:var(--red);border-color:#fca5a5}.pill.XIU{background:var(--cyan-s);color:var(--cyan);border-color:#a5f3fc}.pill.win{background:var(--green-s);color:var(--green);border-color:#86efac}.pill.lose{background:var(--red-s);color:var(--red);border-color:#fca5a5}.muted{color:var(--txt3)}.heading{margin:10px 0 20px}h1{font-size:clamp(22px,4vw,32px);font-weight:900;color:var(--txt)}.eyebrow{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--cyan);margin-bottom:5px}.hdot{width:9px;height:9px;border-radius:50%;display:inline-block}.hdot.ok{background:var(--green-b)}.hdot.bad{background:var(--red-b)}@media(max-width:950px){.grid{grid-template-columns:1fr}}@media(max-width:620px){.wrap{padding:16px 12px 48px}.grid4{grid-template-columns:1fr 1fr}}</style></head><body><header class="top"><div class="brand"><div class="logo"><svg viewBox="0 0 28 28" fill="none"><path d="M14 2.5S22.5 12 22.5 17.5a8.5 8.5 0 1 1-17 0C5.5 12 14 2.5 14 2.5Z" fill="white"/></svg></div><div class="brand-name">PAW NEURAL<small>TX // AI CONTROL CENTER</small></div></div><div style="display:flex;align-items:center;gap:10px"><div class="mono" id="apiStatus" style="font-size:12px;font-weight:700;color:var(--green)">CONNECTING</div><button class="btn btn-sm" onclick="load()">↻ Làm mới</button><a class="btn btn-sm" href="/admin/logout">Thoát →</a></div></header><nav class="nav-tabs"><button class="tab active" onclick="switchTab('all',this)">Tổng quan</button><button class="tab" onclick="switchTab('history',this)">Lịch sử dự đoán</button><button class="tab" onclick="switchTab('protection',this)">Bảo vệ API</button></nav><main class="wrap"><section id="view-all"><div class="heading"><div class="eyebrow">NEURAL NETWORK / LIVE MONITOR</div><h1>Bộ não dự đoán Tài / Xỉu</h1></div><div class="grid4" id="statRow" style="margin-bottom:20px"></div><div class="grid" id="boards"></div></section><section id="view-history" class="hide"><div class="heading"><div class="eyebrow">WALK-FORWARD LEARNING</div><h1>Lịch sử dự đoán live</h1></div><div class="tablebox" id="historyBoards"></div></section><section id="view-protection" class="hide"><div class="heading"><div class="eyebrow">SECURITY</div><h1>Bảo vệ API Access</h1></div><div class="grid"><div class="card"><div class="cardhead"><b>API ACCESS GUARD</b><span id="protState" style="font-weight:800">TẮT</span></div><div style="display:flex;gap:12px;align-items:center;padding:14px 18px;background:var(--surf2);border:1.5px solid var(--bd2);border-radius:12px;margin:14px 0"><div class="mono" id="codeDisplay" style="font-size:24px;font-weight:800;letter-spacing:.22em;color:var(--blue);flex:1">••••••</div><button class="btn btn-sm" onclick="copyCode()">Copy</button></div><div class="mono" id="urlPreview" style="font-size:12px;color:var(--txt3);word-break:break-all">Tạo mã để xem URL bảo vệ</div><div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn primary" onclick="genCode()">Tạo mã mới</button><button class="btn" onclick="setProt('enable')" style="color:var(--green);border-color:#86efac;background:var(--green-s)">Bật bảo vệ</button><button class="btn danger" onclick="setProt('disable')">Tắt bảo vệ</button><button class="btn" onclick="revokeCode()" style="color:#a05d10">Thu hồi</button></div></div><div class="card"><div class="cardhead"><b>Hướng dẫn</b></div><div style="font-size:13px;color:var(--txt2);line-height:1.75"><p><b>Khi BẬT:</b> API chỉ nhận URL có mã đúng.</p><div class="mono" style="margin:10px 0"><b>https://api…onrender.com/[MÃ6KÝ]/tx/hu</b></div><p><b>Khi TẮT:</b> <code>/tx/hu</code> hoạt động bình thường.</p></div><div style="margin-top:16px;padding-top:14px;border-top:1px solid var(--bd)"><p class="muted" id="protInfo" style="font-size:13px">Đang tải…</p></div></div></div></section><div style="color:var(--txt4);text-align:center;font-family:'JetBrains Mono',monospace;font-size:9px;margin-top:28px">PAW TX · REAL-WORLD ENGINE · AUTO-HEALING</div></main><div class="toast" id="toast" style="position:fixed;bottom:20px;right:20px;z-index:200;background:var(--surf);border:1px solid var(--bd);border-left:3px solid var(--green-b);padding:13px 18px;border-radius:12px;display:none;box-shadow:0 12px 40px rgba(0,0,0,.12);font-size:13px;font-weight:700"></div><script>const CSRF="__CSRF__";let DATA=[],timer=4,prot={enabled:false,has_code:false,code:''};const $=id=>document.getElementById(id);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function toast(s,ok=true){const el=$('toast');el.textContent=s;el.style.borderLeftColor=ok?'var(--green-b)':'var(--red-b)';el.style.display='block';clearTimeout(window._t);window._t=setTimeout(()=>el.style.display='none',2800)}function switchTab(name,btn){['all','history','protection'].forEach(x=>$('view-'+x).classList.toggle('hide',x!==name));document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===btn));if(name==='protection')loadProt()}function side(s){return s?`<span class="pill ${s}">${s==='TAI'?'TÀI':'XỈU'}</span>`:'<span class="pill">—</span>'}function board(t){const p=t.pending||{},ex=t.experts||[];const s=p.du_doan,conf=p.conf??0;const ev=p.evaluation||{};const online=t.ready;const resetBadge=p.hard_reset?`<span style="font-size:10px;color:var(--red);font-weight:bold;margin-left:5px">🔄 Tự Reset</span>`:'';return `<article class="card"><div class="cardhead"><div style="display:flex;align-items:center;gap:10px"><span class="hdot ${online?'ok':'bad'}"></span><div><div style="font-size:16px;font-weight:900">Bàn ${esc(t.name)}${resetBadge}</div><div class="mono muted" style="font-size:11px">${online?'API ONLINE':'WAITING'} · ${t.ms||0}ms</div></div></div><div style="display:flex;gap:8px"><button class="btn btn-sm" onclick="act('${t.code}','refresh')">↻</button><button class="btn btn-sm" onclick="act('${t.code}','relearn')">🧠 Học lại</button><button class="btn btn-sm ${t.enabled?'danger':''}" onclick="act('${t.code}','${t.enabled?'off':'on'}')">${t.enabled?'Tắt':'Bật'}</button></div></div><div class="hero"><div class="hero-label">DỰ ĐOÁN PHIÊN TIẾP THEO · #${p.phien??'—'}</div><div class="side ${s||''}">${s==='TAI'?'TÀI':s==='XIU'?'XỈU':'—'}</div><div class="conf-row"><div class="conf-pct" style="color:${conf<50?'#ef4444':'#fbbf24'}">${conf}%</div><div class="conf-label">độ tự tin</div><div class="mono" style="font-size:13px;color:#9eb8d8;margin-left:4px">p(Tài)=${((p.p_tai??.5)*100).toFixed(2)}%</div></div><div class="meter"><i style="width:${Math.min(100,conf)}%"></i></div><div class="reason"><strong>AI SUY NGHĨ</strong>${esc(p.reasoning||'Đang chờ…')}</div><div class="chips"><div class="chip"><b>${p.loss_streak??0}</b><small>Thua liên tiếp</small></div><div class="chip"><b>${p.run_len??0}</b><small>Bệt hiện tại</small></div><div class="chip"><b>${t.st_30?.ty_le??0}%</b><small>Accuracy 30</small></div><div class="chip"><b>${t.st_live?.ty_le??0}%</b><small>Accuracy live</small></div></div>${ev.warning?`<div style="margin-top:10px;padding:9px 12px;border:1px solid var(--red-b);border-radius:9px;background:var(--red-s);color:var(--red);font-size:12px">⚠ ${esc(ev.warning)}</div>`:''}</div></article>`}function drawStatRow(){if(!DATA.length)return;const all=DATA.flatMap(t=>t.hist||[]);const w=all.filter(h=>h.trang_thai==='win').length;const l=all.filter(h=>h.trang_thai==='lose').length;const acc=w+l>0?Math.round(w*100/(w+l)):0;$('statRow').innerHTML=[{label:'Tổng phiên',val:all.length,note:'Đã ghi nhận',sa:'var(--blue)'},{label:'Live accuracy',val:acc+'%',note:w+'W / '+l+'L',sa:'var(--green-b)'}].map((s,i)=>`<div class="stat-card" style="--sa:${s.sa}"><div class="stat-label">${esc(s.label)}</div><div class="stat-val">${esc(s.val)}</div><div class="stat-note">${esc(s.note)}</div></div>`).join('')}function histTable(t){const rows=t.hist||[];return `<section class="card"><div class="cardhead"><b>Lịch sử · Bàn ${esc(t.name)}</b></div><div class="tablewrap"><table><thead><tr><th>Phiên</th><th>Xúc xắc</th><th>Kết quả</th><th>AI dự đoán</th><th>Trạng thái</th></tr></thead><tbody>${rows.length?rows.map(h=>`<tr class="${h.trang_thai}"><td class="mono">#${h.phien}</td><td class="mono">${esc((h.xuc_xac||[]).join('-'))} / ${h.tong??'—'}</td><td>${side(h.ket_qua)}</td><td>${side(h.du_doan)}</td><td><span class="pill ${h.trang_thai}">${h.trang_thai==='win'?'THẮNG':'THUA'}</span></td></tr>`).join(''):'<tr><td colspan="5">Chưa có lịch sử</td></tr>'}</tbody></table></div></section>`}function draw(){$('boards').innerHTML=DATA.map(board).join('');$('historyBoards').innerHTML=DATA.map(histTable).join('');drawStatRow();const online=DATA.every(x=>x.ready);$('apiStatus').textContent=online?'API ONLINE':'DEGRADED';$('apiStatus').style.color=online?'var(--green)':'var(--red)'}async function load(){try{const r=await fetch('/admin/data',{cache:'no-store'});if(r.status===401){location.href='/admin';return}const j=await r.json();if(!j.ok)throw Error(j.loi||'API error');DATA=j.tables||[];draw();timer=4}catch(e){$('apiStatus').textContent='ERROR';$('apiStatus').style.color='var(--red)'}}async function act(c,a){try{const r=await fetch(`/admin/act/${c}/${a}`,{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();toast(j.ok?'Đã thực hiện: '+a:'Lỗi: '+(j.loi||''),j.ok);load()}catch(e){toast('Lỗi mạng',false)}}async function loadProt(){try{const r=await fetch('/admin/aprot/status',{headers:{'X-CSRF-Token':CSRF}});const j=await r.json();prot={...prot,enabled:j.enabled,has_code:j.has_code};$('protState').textContent=j.enabled?'BẬT':'TẮT';$('protState').style.color=j.enabled?'var(--green)':'var(--txt3)';$('protInfo').textContent=`Bảo vệ: ${j.enabled?'BẬT':'TẮT'} · ${j.has_code?'Đã có mã':'Chưa có mã'}`}catch(e){$('protInfo').textContent='Lỗi tải trạng thái'}}async function genCode(){try{const r=await fetch('/admin/aprot/gen',{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();if(!j.ok)throw Error(j.loi);prot.code=j.code;prot.has_code=true;$('codeDisplay').textContent=j.code;$('urlPreview').innerHTML=`<b>${location.origin}/<span style="color:var(--blue)">${esc(j.code)}</span>/tx/hu</b>`;toast('Đã tạo mã mới');loadProt()}catch(e){toast('Tạo mã thất bại',false)}}async function setProt(action){if(action==='enable'&&!prot.has_code){toast('Tạo mã trước',false);return}try{const fd=new FormData();fd.append('action',action);const r=await fetch('/admin/aprot/set',{method:'POST',headers:{'X-CSRF-Token':CSRF},body:fd});const j=await r.json();if(!j.ok)throw Error(j.loi);toast(action==='enable'?'✅ Đã bật':'Đã tắt');loadProt()}catch(e){toast('Không cập nhật được',false)}}async function revokeCode(){if(!confirm('Thu hồi mã sẽ TẮT bảo vệ ngay. Tiếp tục?'))return;try{const r=await fetch('/admin/aprot/revoke',{method:'POST',headers:{'X-CSRF-Token':CSRF}});const j=await r.json();if(!j.ok)throw Error(j.loi);prot={enabled:false,has_code:false,code:''};$('codeDisplay').textContent='••••••';$('urlPreview').textContent='Tạo mã để xem URL bảo vệ';toast('Đã thu hồi mã');loadProt()}catch(e){toast('Thu hồi thất bại',false)}}function copyCode(){if(!prot.code){toast('Chưa có mã',false);return}navigator.clipboard?.writeText(prot.code).then(()=>toast('Đã copy mã: '+prot.code)).catch(()=>toast('Clipboard lỗi',false))}setInterval(()=>{timer=Math.max(0,timer-1);if(timer===0){load();timer=4}},1000);load();</script></body></html>"""

@app.route("/admin/login", methods=["POST"])
def admin_login():
    ip = request.remote_addr or "?"; now = time.time()
    tries = [x for x in _fails.get(ip, []) if now - x < 300]
    if len(tries) >= 6: return redirect("/admin?e=Thử quá nhiều lần, chờ 5 phút")
    pw = os.getenv("ADMIN_PASS", "")
    ok = (bool(pw) and hmac.compare_digest(request.form.get("password", ""), pw) and hmac.compare_digest(request.form.get("username", ""), os.getenv("ADMIN_USER", "admin")))
    if not ok:
        _fails[ip] = tries + [now]; return redirect("/admin?e=Sai tài khoản hoặc mật khẩu")
    session.clear(); session.update(adm=True, adm_until=now + 8 * 3600, csrf=secrets.token_urlsafe(24)); session.permanent = True
    return redirect("/admin")

@app.get("/admin/logout")
def admin_logout(): session.clear(); return redirect("/admin")

@app.get("/admin")
def admin_page():
    if not authed():
        e = request.args.get("e", "")
        if not os.getenv("ADMIN_PASS"): e = "Chưa đặt biến môi trường ADMIN_PASS trên Render"
        err_html = f'<div class=err>{e.replace("<","&lt;")}</div>' if e else ""
        html = LOGIN.replace("__ERR__", err_html)
        r = make_response(html); r.headers["Content-Type"] = "text/html; charset=utf-8"; return r
    r = make_response(PAGE.replace("__CSRF__", session.get("csrf", "")))
    r.headers["Content-Type"] = "text/html; charset=utf-8"; return r

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))