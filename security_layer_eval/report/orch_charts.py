"""오케스트레이션 실험 결과 → 발표용 도표 3종.
스타일 = 기존 Sentinel30 라이트 아카데믹 팔레트(gen_images_v3 / comparison_table 와 동일).

입력 : results/orch_results.json  (run_orch_eval.py 산출)
출력 :
  fig_orch_table.png          토폴로지 5종 한눈 비교표(토큰·₩·지연·F1·몰입)
  fig_orch_tradeoff.png       비용(₩) × 임계지연 산점 — 좌하단=효율(버블=추출F1)
  fig_orch_cost_breakdown.png 통화당 비용 ₩ 역할별 분해(왜 T4/T5가 싼가)
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

BG = "#fbfaf7"; PANEL = "#ffffff"; PANEL2 = "#f3f1eb"; LINEC = "#ded8ce"
TEXT = "#26231f"; DIM = "#6f6a61"; DIM2 = "#aaa39a"
ORANGE = "#d8652a"; SAGE = "#5d8c61"; BLUE = "#3f7ca8"; PURPLE = "#7b669b"
RED = "#bf4a42"; GOLD = "#b28a32"
WIN_BG = "#e4ede7"; BAD_BG = "#f6e4e0"

FONT_DIR = next((d for d in (ROOT / "fonts", ROOT.parent / "fonts")
                 if (d / "Pretendard-Regular.ttf").exists()), ROOT / "fonts")
for fn in ("Pretendard-Regular.ttf", "Pretendard-SemiBold.ttf", "Pretendard-Bold.ttf"):
    if (FONT_DIR / fn).exists():
        fm.fontManager.addfont(str(FONT_DIR / fn))
try:
    plt.rcParams["font.family"] = fm.FontProperties(
        fname=str(FONT_DIR / "Pretendard-Regular.ttf")).get_name()
    plt.rcParams["font.sans-serif"] = [plt.rcParams["font.family"], "Malgun Gothic", "DejaVu Sans"]
except Exception:
    pass
plt.rcParams["axes.unicode_minus"] = False

TOPO_COLOR = {"T1": DIM, "T2": RED, "T3": GOLD, "T4": SAGE, "T5": BLUE, "T6": PURPLE}
TOPO_SYNC = {"T1": "Sonnet 1콜(응답+추출)", "T2": "Opus 1콜",
             "T3": "Opus기획→Sonnet응대", "T4": "Sonnet응대만(기획 비동기)",
             "T5": "Haiku/Sonnet 라우터", "T6": "Haiku/Sonnet 라우터+Opus 저빈도"}
ORDER = ["T1", "T2", "T3", "T4", "T5", "T6"]
WINNER = "T5"   # 확정 우승: 2콜 평균 최저비용·최저지연·F1 1.00. T6(Opus저빈도)는 T5보다 비용+144%·지연+693ms·몰입-2점 → 가설기각


def load(name="orch_results.json"):
    p = RESULTS / name
    if not p.exists():
        raise SystemExit(f"결과 없음: {p} — 먼저 run_orch_eval.py 실행")
    return json.loads(p.read_text(encoding="utf-8"))


def aggregate(data):
    """토폴로지별 평균(여러 콜이면) 집계."""
    acc = defaultdict(lambda: {"tok": [], "krw": [], "ms": [], "f1": [],
                               "judge": [], "name": "", "roles": defaultdict(float),
                               "n": 0})
    for r in data["runs"]:
        t = r["topology"]; a = acc[t]
        a["name"] = r["name"]
        a["tok"].append(r["tokens"]["total_tokens"])
        a["krw"].append(r["tokens"]["cost_krw"])
        a["ms"].append(r["critical_ms"]["median"])
        a["f1"].append(r["extraction"]["f1"])
        if r.get("judge"):
            a["judge"].append(r["judge"].get("overall", 0))
        for role, v in r["by_role"].items():
            a["roles"][role] += v["cost_krw"]
        a["n"] += 1
    out = {}
    for t, a in acc.items():
        mean = lambda xs: float(np.mean(xs)) if xs else 0.0
        out[t] = {
            "name": a["name"], "tok": mean(a["tok"]), "krw": mean(a["krw"]),
            "ms": mean(a["ms"]), "f1": mean(a["f1"]),
            "judge": mean(a["judge"]) if a["judge"] else None,
            "roles": {k: v / a["n"] for k, v in a["roles"].items()},
        }
    return out


# ── 1) 비교표 ──────────────────────────────────────────────────────
def fig_table(agg, data):
    rows = [t for t in ORDER if t in agg]
    n = len(rows)
    fig, ax = plt.subplots(figsize=(13.6, 1.9 + n * 0.7))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.set_xlim(0, 100); ax.set_ylim(0, n + 2.2); ax.axis("off")

    # 컬럼 경계 (7컬럼 → 8경계)
    cols = [1.5, 11, 39, 54, 69, 82, 91, 98.5]
    headers = ["토폴로지", "동기 임계경로(지연 결정)", "토큰/통화",
               "비용 ₩/통화", "임계지연 med", "추출 F1", "몰입/100"]
    row_h = 1.0
    top = n + 0.55

    def panel(x0, x1, yc, bg, accent=None, h=row_h):
        ax.add_patch(FancyBboxPatch((x0, yc - h/2 + 0.07), x1 - x0, h - 0.14,
                     boxstyle="round,pad=0.02,rounding_size=0.10",
                     facecolor=bg, edgecolor=LINEC, linewidth=0.7, zorder=1))
        if accent:
            ax.add_patch(Rectangle((x0 + 0.12, yc - h/2 + 0.1), 0.26, h - 0.2,
                                   facecolor=accent, edgecolor="none", zorder=2))

    def txt(x, yc, t, color, bold=False, fs=12, ha="center"):
        ax.text(x, yc, t, ha=ha, va="center", color=color,
                fontsize=fs, fontweight="bold" if bold else "normal", zorder=3)

    # 헤더
    yc = top
    for j in range(len(headers)):
        panel(cols[j], cols[j+1], yc, TEXT)
        txt((cols[j]+cols[j+1])/2, yc, headers[j], "white", bold=True, fs=11.5)

    best_krw = min(agg[t]["krw"] for t in rows)
    best_ms = min(agg[t]["ms"] for t in rows)
    best_f1 = max(agg[t]["f1"] for t in rows)

    for i, t in enumerate(rows):
        a = agg[t]; yc = top - (i + 1) * row_h
        is_win = (t == WINNER)
        is_bad = (t == "T3")   # Opus를 매 턴 동기로 → 지연·비용 최악
        rbg = WIN_BG if is_win else (BAD_BG if is_bad else PANEL)
        acc = SAGE if is_win else (RED if is_bad else ORANGE)
        # 토폴로지명
        panel(cols[0], cols[1], yc, rbg, accent=acc)
        txt(cols[0] + 0.7, yc, t, TOPO_COLOR.get(t, TEXT), bold=True, fs=13, ha="left")
        # 배치
        panel(cols[1], cols[2], yc, rbg)
        nm = a["name"] + ("  ★운영 권장(최저지연·확장형)" if is_win else "")
        txt(cols[1] + 0.8, yc - 0.16, nm, TEXT, bold=is_win, fs=10.6, ha="left")
        txt(cols[1] + 0.8, yc + 0.2, TOPO_SYNC.get(t, ""), DIM, fs=9.4, ha="left")
        # 토큰
        panel(cols[2], cols[3], yc, rbg)
        txt((cols[2]+cols[3])/2, yc, f"{a['tok']:,.0f}", TEXT, fs=11.5)
        # 비용
        panel(cols[3], cols[4], yc, rbg)
        txt((cols[3]+cols[4])/2, yc, f"₩{a['krw']:,.0f}",
            SAGE if abs(a['krw']-best_krw) < 1e-6 else (RED if is_bad else TEXT),
            bold=abs(a['krw']-best_krw) < 1e-6, fs=11.8)
        # 지연
        panel(cols[4], cols[5], yc, rbg)
        txt((cols[4]+cols[5])/2, yc, f"{a['ms']:,.0f}ms",
            SAGE if abs(a['ms']-best_ms) < 1e-6 else TEXT,
            bold=abs(a['ms']-best_ms) < 1e-6, fs=11.8)
        # F1
        panel(cols[5], cols[6], yc, rbg)
        txt((cols[5]+cols[6])/2, yc, f"{a['f1']:.2f}",
            SAGE if abs(a['f1']-best_f1) < 1e-6 else TEXT,
            bold=abs(a['f1']-best_f1) < 1e-6, fs=11.8)
        # 몰입
        panel(cols[6], cols[7], yc, rbg)
        jv = "—" if a["judge"] is None else f"{a['judge']:.0f}"
        txt((cols[6]+cols[7])/2, yc, jv, TEXT, fs=11.8)

    m = data["meta"]
    ax.text(cols[0], top + 1.45, "미끼봇 오케스트레이션 배치 비교 — 토큰·비용·지연·정확도",
            fontsize=18, fontweight="bold", color=TEXT, va="bottom")
    ax.text(cols[0], top + 0.95,
            f"동일 스크립트 통화({m['turns']}턴) · 토큰=usage 실측 · 비용=공시단가 계산(₩) · "
            f"지연=동기 임계경로 duration_api_ms(상대비교) · LLM=Claude(OAuth)",
            fontsize=10.2, color=DIM, va="bottom")
    ax.text(cols[0], 0.16,
            "핵심: 비용·지연 싱크 = '매 턴 Opus 기획'(T3·T4 총비용의 ~77%). 동기(T3)면 지연도 2배. "
            "비용 최저는 T1(단일 저가, 역할 미분리)·지연 최저는 T5(적응형, 역할분리·확장형) — 둘 다 Opus 없는 단순구조. "
            "T6(Opus 3턴마다, 저빈도) 검증: 비용+144%·지연+693ms에도 품질 이득 없음(몰입 -2점) → 운영안 = T5.",
            fontsize=9.5, color=DIM, va="bottom")

    fig.tight_layout()
    fig.savefig(RESULTS / "fig_orch_table.png", dpi=190, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_orch_table.png")


# ── 2) 비용×지연 트레이드오프 ──────────────────────────────────────
def fig_tradeoff(agg):
    rows = [t for t in ORDER if t in agg]
    fig, ax = plt.subplots(figsize=(9.6, 7.0))
    fig.patch.set_facecolor(BG); ax.set_facecolor(PANEL)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINEC)
    ax.grid(color=LINEC, lw=0.8, alpha=0.7); ax.set_axisbelow(True)
    ax.tick_params(colors=DIM, labelsize=11)

    f1s = [agg[t]["f1"] for t in rows]
    for t in rows:
        a = agg[t]
        size = 500 + (a["f1"]) * 2600
        c = TOPO_COLOR.get(t, DIM)
        win = (t == WINNER)
        ax.scatter(a["krw"], a["ms"], s=size, color=c, alpha=0.9 if win else 0.55,
                   edgecolor=TEXT if win else c, linewidth=2.2 if win else 0, zorder=3)
        ax.annotate(f"{t}\n{a['name']}\nF1 {a['f1']:.2f}",
                    (a["krw"], a["ms"]), ha="center", va="center",
                    fontsize=10.5 if win else 9.3,
                    fontweight="bold" if win else "normal",
                    color="white" if t in ("T2", "T4", "T5", "T6") else TEXT, zorder=4)

    ax.set_xlabel("통화당 비용  ₩ (낮을수록 좋음 →)", fontsize=12.5, color=TEXT)
    ax.set_ylabel("응답 임계경로 지연  median ms (낮을수록 좋음 ↓)", fontsize=12.5, color=TEXT)
    ax.set_title("효율 프런티어 — 좌하단이 우수 (버블 크기 = 추출 F1)",
                 fontsize=16, fontweight="bold", color=TEXT, pad=14)
    ax.invert_yaxis()
    # 좌하단 스위트스폿 화살표
    ax.annotate("효율 스위트스폿", xy=(0.06, 0.06), xycoords="axes fraction",
                fontsize=11, color=SAGE, fontweight="bold")
    fig.text(0.5, 0.012,
             "토큰=usage 실측 · 비용=공시단가(₩) · 지연=동기 임계경로 duration_api_ms(상대비교) · 동일 스크립트 통화",
             ha="center", fontsize=8.8, color=DIM)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(RESULTS / "fig_orch_tradeoff.png", dpi=190, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_orch_tradeoff.png")


# ── 3) 역할별 비용 분해 ────────────────────────────────────────────
def fig_cost_breakdown(agg):
    rows = [t for t in ORDER if t in agg]
    # 역할을 4그룹으로 정규화
    def group(role):
        if "planner" in role:
            return "기획(Opus)"
        if "responder" in role and "extract" in role:
            return "응답+추출(단일콜)"
        if "responder" in role:
            return "응답"
        if "extract" in role:
            return "추출(Haiku)"
        if "compact" in role:
            return "압축(Haiku)"
        return role
    groups = ["기획(Opus)", "응답+추출(단일콜)", "응답", "추출(Haiku)", "압축(Haiku)"]
    gcolor = {"기획(Opus)": RED, "응답+추출(단일콜)": GOLD, "응답": BLUE,
              "추출(Haiku)": SAGE, "압축(Haiku)": PURPLE}

    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    fig.patch.set_facecolor(BG); ax.set_facecolor(PANEL)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINEC)
    ax.grid(axis="x", color=LINEC, lw=0.8, alpha=0.7); ax.set_axisbelow(True)
    ax.tick_params(colors=DIM, labelsize=11)

    y = np.arange(len(rows))[::-1]
    for gi, g in enumerate(groups):
        left = np.zeros(len(rows))
        vals = []
        for k, t in enumerate(rows):
            roles = agg[t]["roles"]
            v = sum(val for role, val in roles.items() if group(role) == g)
            vals.append(v)
        # cumulative left
        base = []
        for k, t in enumerate(rows):
            prior = sum(sum(val for role, val in agg[t]["roles"].items()
                            if group(role) == groups[j]) for j in range(gi))
            base.append(prior)
        ax.barh(y, vals, left=base, color=gcolor[g], label=g, height=0.62,
                edgecolor=BG, linewidth=1.0)

    ax.set_yticks(y)
    ax.set_yticklabels([f"{t}\n{agg[t]['name']}" for t in rows], fontsize=10.5, color=TEXT)
    for k, t in enumerate(rows):
        total = agg[t]["krw"]
        ax.text(total + max(agg[u]["krw"] for u in rows) * 0.01, y[k],
                f"₩{total:,.0f}", va="center", fontsize=11, color=TEXT, fontweight="bold")
    ax.set_xlabel("통화당 비용  ₩ (역할별 분해)", fontsize=12.5, color=TEXT)
    ax.set_title("비용은 어디서 오는가 — Opus 기획을 임계경로에서 빼면(T4) / 없애면(T5) 절감",
                 fontsize=14.5, fontweight="bold", color=TEXT, pad=12)
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    fig.text(0.5, 0.01,
             "비용=공시단가 계산(₩) · 토큰=usage 실측 · 동일 스크립트 통화",
             ha="center", fontsize=8.8, color=DIM)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(RESULTS / "fig_orch_cost_breakdown.png", dpi=190, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_orch_cost_breakdown.png")


def main():
    data = load()
    agg = aggregate(data)
    fig_table(agg, data)
    fig_tradeoff(agg)
    fig_cost_breakdown(agg)


if __name__ == "__main__":
    main()
