# -*- coding: utf-8 -*-
"""
════════════════════════════════════════════════════════════════════════════════
PAW TX · STABLE CORE v21 — CƠ BẢN · ỔN ĐỊNH LÂU DÀI · ĐA DẠNG PHÂN TÍCH
════════════════════════════════════════════════════════════════════════════════

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
  SC_CONF_LO       = đáy dải độ tin hiển thị   (mặc định 58)
  SC_CONF_HI       = đỉnh dải độ tin hiển thị  (mặc định 72)
  SC_HYSTERESIS    = ngưỡng giữ phía cũ        (mặc định 0.02)
  SC_DEFAULT_SIDE  = phía khi không có tín hiệu nào (mặc định XIU — vì
                     xác suất TOÁN HỌC của TÀI chỉ 48.61% (105/216))
  SC_VETO          = 1/0 — bật/tắt phủ quyết khi mọi khung 5/12/30 trái hướng
  (giữ nguyên các biến cũ: NO_SKIP, FLIP_AFTER, CYCLE_WEIGHT, CAU_WINDOWS)

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
       - Hysteresis: tín hiệu mờ hơn SC_HYSTERESIS => giữ nguyên phía cũ.
       - EMA làm mượt p_tai qua các phiên.
       - Độ tin hiển thị rải đều trong dải 58-72% theo sức mạnh phân tích
         thật (lực hội nghị + đồng thuận chuyên gia + khung 5/12/30);
         cầu loạn hoặc bị khung phủ quyết thì nằm ở đáy dải.
       - Không có tín hiệu => nhìn xác suất toán học: TÀI thật 48.61% =>
         nghiêng XỈU (SC_DEFAULT_SIDE) thay vì đoán theo "cầu gần nhất".
  6) Governor giữ nguyên khung cũ (PLAY / NO-SKIP với NO_SKIP=1 / CAM),
     AUTO-FLIP chống kẹt còn lại nhưng CHẶT:HÃY hơn: chỉ flip khi thua đủ
     chuỗi VÀ hệ không còn bằng chứng nào cho phía đang giữ.
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

# dải độ tin hiển thị: SC_CONF_LO..SC_CONF_HI (58..72%), RẢI ĐỀU theo
# sức mạnh phân tích THẬT — không phải số ngẫu nhiên, càng phân tích
# càng đồng thuận thì điểm càng cao trong dải
_SC_CONF_LO      = _sc_int("SC_CONF_LO", 58, 52, 70)
_SC_CONF_HI      = max(_SC_CONF_LO + 1, _sc_int("SC_CONF_HI", 72, 53, 85))
_SC_DEFAULT_SIDE = _sc_side("SC_DEFAULT_SIDE", "XIU")
_SC_HYSTERESIS   = _sc_float("SC_HYSTERESIS", 0.02, 0.005, 0.06)
_SC_VETO         = (os.getenv("SC_VETO", "1").strip() != "0")

_P_TAI_THUC = 105.0 / 216.0    # 0.4861 — xác suất thật của TÀI (3 xúc xắc chuẩn)

# ── Helpers dùng chung (các hàm phân tích phía sau app cũng cần _clamp/_opp) ─
def _clamp(p, lo=0.38, hi=0.62):
    return max(lo, min(hi, p))

def _opp(side: str) -> str:
    return "XIU" if side == "TAI" else "TAI"

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
    EXPERTS = ("HAZARD", "RUNMIRROR", "CTX", "REVERSION", "MOMENTUM", "FREQ")

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
        fast, slow = h[-8:], h[-30:]
        sf = (sum(fast) + 2.0) / (len(fast) + 4.0) - 0.5
        ss = (sum(slow) + 3.0) / (len(slow) + 6.0) - 0.5
        return float(max(0.0, 0.55 * (sf * 2.0) + 0.45 * (ss * 2.0)))

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
    def combine(self, ex: Dict[str, Dict]):
        """Trả (p_tai, skills, expert_sides). Logit-trung bình có trọng số kỹ năng,
        sau đó làm ướt (damp) mức mạnh còn lại. Không skill => im lặng 50/50."""
        skills = {n: self.skill(n) for n in self.EXPERTS}
        tot = sum(skills.values())
        expert_sides = {}
        if tot < 1e-9:
            return 0.5, skills, expert_sides
        zbar = 0.0
        for n in self.EXPERTS:
            e = ex[n]
            expert_sides[n] = e["side"] if e["p"] >= 0.52 else None
            pt = e["p"] if e["side"] == "TAI" else 1.0 - e["p"]
            zbar += skills[n] * _logit(pt)
        zbar = max(-0.55, min(0.55, zbar / tot))
        damp = min(1.0, 0.30 + 1.1 * max(skills.values()))
        return _sigmoid(damp * zbar), skills, expert_sides

# ══════════════════════════════════════════════════════════════════════════════
#  BRAIN — hợp đồng giữ nguyên cho Table / replay / API
# ══════════════════════════════════════════════════════════════════════════════
class Brain:
    def __init__(self):
        self.engine = _Core()
        self.history = deque(maxlen=500)
        self.points  = deque(maxlen=500)
        self._seen_ids = set()
        self._last_prediction = None
        self._stick_side = None
        self._p_ema = None
        self.last_cycle = None
        self.loss_streak = 0
        self.win_streak  = 0
        self.hit = deque(maxlen=30)
        self.pred_sides = deque(maxlen=30)

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

    # ── lõi dự đoán ──
    def predict(self):
        seq = list(self.engine.seq)
        sums_h = list(self.engine.sums)
        acc, n_ev = self._eval()

        if len(seq) < 12:
            pl, nhom = self._pl_nhom(sum_h=sums_h[-1] if sums_h else None, run_len=0)
            return {"side": None, "confidence": 0, "p_tai": 0.5,
                    "reasoning": "[CAM] CHỜ — chưa đủ 12 phiên dữ liệu",
                    "experts": {}, "expert_votes": {}, "expert_sides": {},
                    "forced_skip": True, "cau_loan": False,
                    "dong_thuan_chu_ky": None, "regime": "—",
                    "khung_da_phien": [],
                    "chu_ky_3_tang": {"da_du_du_lieu": False},
                    "loss_streak": self.loss_streak, "run_len": 0,
                    "acc30": acc, "total_signals": 0,
                    "models_voted_tai": 0, "models_voted_xiu": 0,
                    "evaluation": self._evaluation(n_ev, acc),
                    "baseline_side": None, "baseline_p_tai": None,
                    "pl": pl, "nhom": nhom, "hard_reset": False,
                    "inverse_mode": False,
                    "governor": {"che_do": "CAM", "suc_manh": 0.0, "acc30": acc,
                                 "ly_do": "chưa đủ 12 phiên dữ liệu"}}

        last, rlen = _last_run(seq)

        # 1) hội nghị 6 chuyên gia
        ex = self.engine.experts(seq)
        p_tai, skills, expert_sides = self.engine.combine(ex)

        # 2) nhận diện chế độ cầu + hoà không tín hiệu => prior dài hạn
        w12 = seq[-12:]
        alt = sum(1 for i in range(1, len(w12)) if w12[i] != w12[i - 1]) / max(1, len(w12) - 1)
        regime = "ĐẢO" if alt >= 0.62 else "BỆT" if alt <= 0.38 else "LẪN"
        max_run12 = max(_run_lengths(w12)) if w12 else 1
        cau_loan = (alt >= 0.58 and max_run12 <= 2)

        if abs(p_tai - 0.5) < 0.004:
            # không ai có bằng chứng => giữ phía cũ, còn không thì prior toán học
            pred = self._stick_side or _SC_DEFAULT_SIDE
            reason_prior = ("không tín hiệu => prior %s (TÀI thật %.2f%%)"
                            % (_SC_DEFAULT_SIDE, _P_TAI_THUC * 100))
        else:
            pred = "TAI" if p_tai >= 0.5 else "XIU"
            reason_prior = ""

        # 3) HYSIERESIS — tín hiệu mờ thì giữ phía cũ, không lật loạn
        if (self._stick_side and pred != self._stick_side
                and abs(p_tai - 0.5) < _SC_HYSTERESIS):
            pred = self._stick_side
            p_tai = round(0.5 + _SC_HYSTERESIS if pred == "TAI" else 0.5 - _SC_HYSTERESIS, 4)
            reason_prior = "giữ phía cũ (hysteresis)"

        # 4) EMA làm mượt p_tai — giảm nhảy TÀI XỈU giữa các phiên
        if self._p_ema is not None:
            p_tai = round(0.75 * p_tai + 0.25 * float(self._p_ema), 4)
        self._p_ema = p_tai

        # 5) phủ quyết đa khung: mọi khung 5/12/30 đều trái hướng => hạ độ tin
        khung_rows = []
        try:
            if _SC_VETO:
                khung_rows = list(cau_multi_consensus(seq))
        except Exception:
            khung_rows = []
        veto = False
        if khung_rows:
            for_side = sum(1 for r in khung_rows
                           if (r["p_tai"] >= 0.53) == (pred == "TAI"))
            veto = (for_side == 0)
            dong_thuan_khung = for_side
        else:
            dong_thuan_khung = 0

        # 6) ĐỘ TIN HIỂN THỊ — dải SC_CONF_LO..SC_CONF_HI (58..72%), rải đều
        #    theo sức mạnh phân tích THẬT, 3 thành phần đều đo được:
        #      e_sig   : lực hội nghị (độ lệch logit của p_tai nội bộ)
        #      ag      : tỷ lệ chuyên gia "lên tiếng" đồng thuận với phía chốt
        #      kh_agree: tỷ lệ khung 5/12/30 cùng hướng
        e_sig = min(1.0, abs(p_tai - 0.5) / 0.12)
        active = [nm for nm in self.engine.EXPERTS if ex[nm]["p"] >= 0.52]
        ag = (sum(1 for nm in active if ex[nm]["side"] == pred) / len(active)) if active else 0.0
        kh_agree = (dong_thuan_khung / len(khung_rows)) if khung_rows else 0.5
        strength = 0.45 * e_sig + 0.35 * ag + 0.20 * kh_agree
        if cau_loan or veto:
            strength = min(strength, 0.30)   # cầu loạn / bị phủ quyết => dải thấp
        conf = int(round(_SC_CONF_LO + strength * (_SC_CONF_HI - _SC_CONF_LO)))
        p_out = round(0.5 + (conf - 50) / 100.0, 4) if pred == "TAI" \
            else round(0.5 - (conf - 50) / 100.0, 4)

        # 7) lý do — CON SỐ THẬT, không phóng đại
        det = "; ".join("%s[%s %d%%] %s" % (n, ex[n]["side"], int(ex[n]["p"] * 100),
                                            ex[n]["tag"])
                        for n in self.engine.EXPERTS if ex[n]["p"] >= 0.52)
        if not det:
            det = "cả hội nghị im lặng (thiếu mẫu / skill = 0)"
        if veto:
            det = "PHỦ QUYẾT KHUNG: mọi khung trái hướng | " + det
        if reason_prior:
            det = reason_prior + " | " + det

        cyc = None
        try:
            cyc = phan_tich_chu_ky_3_tang(list(seq))
        except Exception:
            cyc = None
        if not isinstance(cyc, dict):
            cyc = {"da_du_du_lieu": False}
        self.last_cycle = cyc

        pl, nhom = self._pl_nhom(sum_h=sums_h[-1] if sums_h else None, run_len=rlen)
        result = {
            "side": pred,
            "confidence": conf,
            "p_tai": p_out,
            "reasoning": "%s %d%% | cầu %s | %s" % (pred, conf, regime, det),
            "experts": {n: round(skills.get(n, 0.0), 4) for n in self.engine.EXPERTS},
            "expert_votes": {n: round(ex[n]["p"], 4) for n in self.engine.EXPERTS},
            "expert_sides": expert_sides,
            "forced_skip": False,
            "cau_loan": cau_loan,
            "dong_thuan_chu_ky": (int(cyc.get("dong_thuan", 0)) if cyc.get("dong_thuan") is not None
                                  else dong_thuan_khung),
            "regime": regime,
            "khung_da_phien": khung_rows,
            "chu_ky_3_tang": cyc,
            "loss_streak": self.engine.loss_streak,
            "run_len": rlen,
            "acc30": acc,
            "total_signals": sum(1 for n in self.engine.EXPERTS if ex[n]["p"] >= 0.52),
            "models_voted_tai": sum(1 for n in self.engine.EXPERTS
                                    if ex[n]["p"] >= 0.52 and ex[n]["side"] == "TAI"),
            "models_voted_xiu": sum(1 for n in self.engine.EXPERTS
                                    if ex[n]["p"] >= 0.52 and ex[n]["side"] == "XIU"),
            "evaluation": self._evaluation(n_ev, acc),
            "baseline_side": None, "baseline_p_tai": None,
            "pl": pl, "nhom": nhom,
            "hard_reset": False, "inverse_mode": False,
        }

        # 8) GOVERNOR — gate theo SỨC MẠNH THẬT (strength) + acc30, không theo
        #    conf hiển thị (conf giờ luôn nằm trong dải 58..72 để UI đọc được)
        ev = result["evaluation"]
        acc30 = ev.get("accuracy_30")
        n_played = ev.get("n", 0)
        no_skip = _NO_SKIP
        tin_ok = (n_played >= 4) and (strength >= 0.30) and not veto
        if tin_ok:
            result["governor"] = {"che_do": "PLAY", "suc_manh": round(strength, 3),
                                  "acc30": acc30, "ly_do": "tín hiệu đạt chuẩn"}
            self._stick_side = result["side"]
        else:
            ly_do_cam = ("chưa đủ dữ liệu tự học" if n_played < 4 else
                         "sức mạnh phân tích %.0f%% dưới ngưỡng (acc30=%s)"
                         % (strength * 100, acc30))
            if no_skip:
                fb = result["side"] or self._stick_side or _SC_DEFAULT_SIDE
                result["side"] = fb
                result["confidence"] = max(_SC_CONF_LO, min(_SC_CONF_LO + 4, int(result["confidence"])))
                result["p_tai"] = (round(max(float(result.get("p_tai", 0.5)), 0.5 + (_SC_CONF_LO - 50) / 100.0 - 0.07), 4)
                                   if fb == "TAI"
                                   else round(min(float(result.get("p_tai", 0.5)), 0.5 - (_SC_CONF_LO - 50) / 100.0 + 0.07), 4))
                result["governor"] = {"che_do": "NO-SKIP", "suc_manh": round(strength, 3),
                                      "acc30": acc30,
                                      "ly_do": "cấm skip — ra phía an toàn (" + ly_do_cam + ")"}
                result["reasoning"] = "[NO-SKIP] " + str(result["reasoning"])[:140]
                self._stick_side = fb
            else:
                result["governor"] = {"che_do": "CAM", "suc_manh": round(strength, 3),
                                      "acc30": acc30, "ly_do": ly_do_cam}
                result["side"] = None
                result["confidence"] = 0
                result["reasoning"] = "[CAM] CHỜ — " + ly_do_cam
                self._stick_side = None

        # 9) AUTO-FLIP CHẶT — chỉ khi thua đủ chuỗi VÀ hệ không còn bằng chứng
        #    nào cho phía đang giữ (khác bản cũ: flip mù cả khi tín hiệu còn mạnh)
        _ps = list(self.pred_sides)
        _ht = list(self.hit)
        _k = _FLIP_AFTER
        if (_k >= 2 and len(_ps) >= _k and len(_ht) >= _k
                and _ps[-1] == _ps[-2] and all(s == _ps[-1] for s in _ps[-_k:])
                and not any(_ht[-_k:])):
            stuck = _ps[-1]
            stuck_p = p_tai if stuck == "TAI" else 1.0 - float(p_tai)
            if stuck_p < 0.55:                       # không còn bằng chứng (p nội bộ thật)
                result["side"] = _opp(stuck)
                result["confidence"] = _SC_CONF_LO
                result["p_tai"] = (round(0.5 + (_SC_CONF_LO - 50) / 100.0, 4)
                                   if result["side"] == "TAI"
                                   else round(0.5 - (_SC_CONF_LO - 50) / 100.0, 4))
                result["governor"] = {"che_do": "AUTO-FLIP", "suc_manh": round(strength, 3),
                                      "acc30": acc30,
                                      "ly_do": "cùng phía thua %d phiên và hết bằng chứng (%s)"
                                               % (_k, stuck)}
                result["reasoning"] = "[AUTO-FLIP] " + str(result["reasoning"])[:120]
                self._stick_side = result["side"]

        self._last_prediction = result
        return result

    # ── học sau mỗi phiên ──
    def learn(self, pk, y: bool):
        if not isinstance(pk, dict) or pk.get("side") not in ("TAI", "XIU"):
            return
        actual = "TAI" if y else "XIU"
        won = pk["side"] == actual
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