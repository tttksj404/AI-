"""3프로바이더(claude.exe / GPT-codex / Gemini) 오케스트레이션 교차비교 도표.
스타일 = 기존 Sentinel30 라이트 아카데믹 팔레트(orch_charts 와 동일).

입력(세 파일, 모두 call1_prosecutor 만 사용해 공정비교):
  results/orch_results.json         (claude.exe OAuth)
  results/orch_results_gpt.json     (GPT, ChatGPT 구독 OAuth=codex)
  results/orch_results_gemini.json  (Gemini, Google 구독 OAuth)
출력:
  fig_cross_latency.png    토폴로지×3사 임계지연 — 동기 T3 지연재앙이 모델무관 재현
  fig_cross_costrank.png   프로바이더별 비용 정규화(자기 최저=1.0) — 우승 토폴로지가 단가구조 의존
  fig_cross_summary.png    교차결론 체크표(강건 vs 단가의존)

정직 캐비엇: OAuth 백엔드(codex/gemini)는 에이전트 오버헤드 포함·구독 정액 →
비용 절대값의 프로바이더간 비교 금지. 그래서 비용은 '프로바이더 내부 정규화'만,
지연(ms)·F1 은 비교 가능 지표로 표시.
"""
from __future__ import annotations
import json
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

ORDER = ["T1", "T2", "T3", "T4", "T5", "T6"]
TOPO_DESC = {"T1": "단일 저가", "T2": "단일 최상위", "T3": "계층 동기",
             "T4": "계층 비동기", "T5": "적응형 라우터", "T6": "적응형+고급전략가"}
CALL = "call1_prosecutor"


def load_provider(name, label, color, real_cost=True):
    """real_cost=False(codex): 단일모델인데 추상티어 단가표가 적용돼 ₩가 아티팩트.
    토큰은 실측이라 토큰 기준 순위만 의미있음 → 비용 정규화 차트에서 ★/실선 제외."""
    p = RESULTS / name
    if not p.exists():
        raise SystemExit(f"결과 없음: {p} — 먼저 run_orch_eval.py 실행")
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = {}
    for r in d["runs"]:
        if r.get("call_id") != CALL:
            continue
        rows[r["topology"]] = {
            "tok": r["tokens"]["total_tokens"],
            "krw": r["tokens"]["cost_krw"],
            "ms": r["critical_ms"]["median"],
            "f1": r["extraction"]["f1"],
            "n_calls": r["n_calls"],
            "name": r["name"],
        }
    return {"label": label, "color": color, "rows": rows, "real_cost": real_cost}


def _ax_style(ax, grid_axis="y"):
    fig = ax.figure
    fig.patch.set_facecolor(BG); ax.set_facecolor(PANEL)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(LINEC)
    ax.grid(axis=grid_axis, color=LINEC, lw=0.8, alpha=0.7); ax.set_axisbelow(True)
    ax.tick_params(colors=DIM, labelsize=11)


# ── 1) 임계지연 그룹막대 (비교 가능 지표) ───────────────────────────
def fig_latency(provs):
    fig, ax = plt.subplots(figsize=(12.0, 6.4))
    _ax_style(ax)
    x = np.arange(len(ORDER)); w = 0.26
    for i, pv in enumerate(provs):
        ys = [pv["rows"].get(t, {}).get("ms", 0) / 1000.0 for t in ORDER]
        bars = ax.bar(x + (i - 1) * w, ys, w, color=pv["color"], label=pv["label"],
                      edgecolor=BG, linewidth=0.8, zorder=3)
        for b, v in zip(bars, ys):
            if v > 0:
                ax.text(b.get_x() + b.get_width() / 2, v + 0.4, f"{v:.1f}",
                        ha="center", va="bottom", fontsize=8.6, color=DIM)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{t}\n{TOPO_DESC[t]}" for t in ORDER], fontsize=10.5, color=TEXT)
    ax.set_ylabel("응답 임계경로 지연  median (초)", fontsize=12.5, color=TEXT)
    ax.set_title("동기 멀티콜(T3)의 지연 재앙은 모델·프로바이더 무관 — 3사 교차검증",
                 fontsize=16, fontweight="bold", color=TEXT, pad=14)
    ax.legend(loc="upper right", frameon=False, fontsize=11)
    # T3 강조
    t3i = ORDER.index("T3")
    ax.axvspan(t3i - 0.45, t3i + 0.45, color=RED, alpha=0.06, zorder=0)
    ax.annotate("동기 누적 → 지연 폭증\n(비동기 T4서 즉시 회복)",
                xy=(t3i, ax.get_ylim()[1] * 0.86), ha="center",
                fontsize=10.5, color=RED, fontweight="bold")
    fig.text(0.5, 0.012,
             "지연=동기 임계경로 duration_api_ms(상대비교) · 동일 스크립트 통화 call1(검찰사칭) 6턴 · "
             "지연은 시간 단위라 프로바이더간 비교 가능(비용 절대값은 비교 금지)",
             ha="center", fontsize=8.8, color=DIM)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(RESULTS / "fig_cross_latency.png", dpi=190, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_cross_latency.png")


# ── 2) 비용 정규화 순위 (프로바이더 내부) ───────────────────────────
def fig_costrank(provs):
    fig, ax = plt.subplots(figsize=(12.0, 6.4))
    _ax_style(ax)
    x = np.arange(len(ORDER)); w = 0.26
    for i, pv in enumerate(provs):
        present = [t for t in ORDER if t in pv["rows"]]
        mn = min(pv["rows"][t]["krw"] for t in present)
        win_t = min(present, key=lambda t: pv["rows"][t]["krw"])
        ys = [pv["rows"][t]["krw"] / mn if t in pv["rows"] else 0 for t in ORDER]
        real = pv["real_cost"]
        bars = ax.bar(x + (i - 1) * w, ys, w, color=pv["color"], label=pv["label"],
                      edgecolor=BG, linewidth=0.8, zorder=3,
                      alpha=1.0 if real else 0.45,
                      hatch=None if real else "///")
        for t, b, v in zip(ORDER, bars, ys):
            if v <= 0:
                continue
            if t == win_t and real:  # ★는 실측 비용(Claude·Gemini)만 — codex는 아티팩트
                ax.text(b.get_x() + b.get_width() / 2, v + 0.15, "★",
                        ha="center", va="bottom", fontsize=13, color=pv["color"],
                        fontweight="bold")
            ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.1f}×",
                    ha="center", va="bottom", fontsize=8.0, color=DIM)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{t}\n{TOPO_DESC[t]}" for t in ORDER], fontsize=10.5, color=TEXT)
    ax.set_ylabel("프로바이더 내부 비용 배수  (자기 최저 토폴로지 = 1.0×)", fontsize=12.0, color=TEXT)
    ax.axhline(1.0, color=SAGE, lw=1.1, ls="--", alpha=0.8, zorder=2)
    ax.set_title("고급모델·계층 오케스트레이션(T2·T3·T4·T6)에서 비용 폭증 — 단순구조(T1·T5)가 최저권",
                 fontsize=15.0, fontweight="bold", color=TEXT, pad=14)
    ax.legend(loc="upper left", frameon=False, fontsize=11)
    fig.text(0.5, 0.030,
             "실측 멀티모델 Claude·Gemini(실선·★)는 단일저가 T1이 최저비용(저가티어가 충분히 싸 단일콜이 이김), "
             "적응형 T5가 근소차 2위. 단일최상위(T2)·계층(T3/T4)·고급전략가(T6)는 최저 대비 3~11배.",
             ha="center", fontsize=8.8, color=DIM)
    fig.text(0.5, 0.010,
             "GPT(codex, 빗금)는 단일모델인데 추상티어 단가표가 적용돼 ₩가 아티팩트 — 토큰 기준 최저는 T1. 비용 절대값의 프로바이더간 비교 금지.",
             ha="center", fontsize=8.8, color=DIM)
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    fig.savefig(RESULTS / "fig_cross_costrank.png", dpi=190, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_cross_costrank.png")


# ── 3) 교차결론 체크표 ─────────────────────────────────────────────
def fig_summary(provs):
    labels = [pv["label"] for pv in provs]

    def ms(pv, t):
        return pv["rows"].get(t, {}).get("ms", 0)

    def krw(pv, t):
        return pv["rows"].get(t, {}).get("krw", 0)

    def f1(pv, t):
        return pv["rows"].get(t, {}).get("f1", 0)

    # 행별 셀 텍스트 + 강건 판정
    def cell_t3_latency(pv):
        worst = max(ORDER, key=lambda t: ms(pv, t))
        ok = (worst == "T3")
        return f"{ms(pv,'T3')/1000:.1f}s 최대", ok

    def cell_async(pv):
        ok = ms(pv, "T4") < ms(pv, "T3")
        return f"{ms(pv,'T3')/1000:.0f}→{ms(pv,'T4')/1000:.0f}s", ok

    def cell_t6(pv):
        ok = krw(pv, "T6") > krw(pv, "T5")
        mult = krw(pv, "T6") / krw(pv, "T5") if krw(pv, "T5") else 0
        return f"{mult:.1f}× 비용↑", ok

    def cell_f1(pv):
        vals = [f1(pv, t) for t in ORDER if t in pv["rows"]]
        lo, hi = min(vals), max(vals)
        ok = lo >= 0.85
        return ("1.00" if lo == hi else f"{lo:.2f}~{hi:.2f}"), ok

    def cell_best(pv):
        present = [t for t in ORDER if t in pv["rows"]]
        cw = min(present, key=lambda t: krw(pv, t))
        cl = min(present, key=lambda t: ms(pv, t))
        mark = "" if pv["real_cost"] else "*"  # codex 비용=아티팩트
        return f"₩ {cw}{mark} · 지연 {cl}", None  # 트레이드오프(강건 아님)

    spec = [
        ("동기 멀티콜(T3) 지연 최악", cell_t3_latency, "강건"),
        ("비동기(T4) 지연 회복", cell_async, "강건"),
        ("고급모델 전략가(T6) 낭비", cell_t6, "강건"),
        ("추출 정확도 F1 유지", cell_f1, "강건"),
        ("최저비용 vs 최저지연", cell_best, "트레이드오프"),
    ]

    nrows = len(spec)
    fig, ax = plt.subplots(figsize=(13.2, 1.9 + nrows * 0.92))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.set_xlim(0, 100); ax.set_ylim(0, nrows + 2.4); ax.axis("off")

    # 컬럼: 결론 | claude | gpt | gemini | 강건성
    cols = [1.5, 36, 52, 68, 84, 98.5]
    headers = ["3사 교차 결론"] + [l.split("\n")[0] for l in labels] + ["판정"]
    row_h = 1.0
    top = nrows + 0.6

    def panel(x0, x1, yc, bg, accent=None, h=row_h):
        ax.add_patch(FancyBboxPatch((x0, yc - h/2 + 0.07), x1 - x0, h - 0.14,
                     boxstyle="round,pad=0.02,rounding_size=0.10",
                     facecolor=bg, edgecolor=LINEC, linewidth=0.7, zorder=1))
        if accent:
            ax.add_patch(Rectangle((x0 + 0.12, yc - h/2 + 0.1), 0.26, h - 0.2,
                                   facecolor=accent, edgecolor="none", zorder=2))

    def txt(x, yc, t, color, bold=False, fs=11.5, ha="center"):
        ax.text(x, yc, t, ha=ha, va="center", color=color,
                fontsize=fs, fontweight="bold" if bold else "normal", zorder=3)

    # 헤더
    yc = top
    for j in range(len(headers)):
        panel(cols[j], cols[j+1], yc, TEXT)
        txt((cols[j]+cols[j+1])/2, yc, headers[j], "white", bold=True, fs=11.5)

    for i, (title, fn, verdict) in enumerate(spec):
        yc = top - (i + 1) * row_h
        robust = (verdict == "강건")
        rbg = WIN_BG if robust else PANEL2
        acc = SAGE if robust else GOLD
        panel(cols[0], cols[1], yc, rbg, accent=acc)
        txt(cols[0] + 0.7, yc, title, TEXT, bold=True, fs=10.2, ha="left")
        for k, pv in enumerate(provs):
            text, ok = fn(pv)
            panel(cols[1 + k], cols[2 + k], yc, rbg)
            mark = ""
            col = TEXT
            if ok is True:
                mark = "✓ "; col = SAGE
            elif ok is False:
                mark = "✗ "; col = RED
            txt((cols[1+k]+cols[2+k])/2, yc, mark + text, col, fs=9.4,
                bold=(ok is True))
        panel(cols[4], cols[5], yc, rbg)
        txt((cols[4]+cols[5])/2, yc, verdict, SAGE if robust else GOLD,
            bold=True, fs=11.5)

    ax.text(cols[0], top + 1.55,
            "오케스트레이션 결론의 3사 교차검증 — 무엇이 모델무관 강건한가",
            fontsize=17.5, fontweight="bold", color=TEXT, va="bottom")
    ax.text(cols[0], top + 1.05,
            "동일 스크립트 통화 call1(검찰사칭) 6턴 · Claude=claude.exe OAuth · GPT=ChatGPT 구독 OAuth(codex) · "
            "Gemini=Google 구독 OAuth",
            fontsize=10.0, color=DIM, va="bottom")
    ax.text(cols[0], 0.16,
            "결론: 구조적 원칙(동기=지연재앙·비동기 회복·per-turn 고급모델 낭비·F1 유지)은 3사 모두 재현되어 강건. "
            "단 최저'비용'(실측 멀티모델 Claude·Gemini는 단일저가 T1)과 최저'지연'(적응형 T5·비동기 T4)은 갈린다 — 둘 다 단순구조. "
            "GPT(*)는 단일모델이라 ₩=단가표 아티팩트(비교 제외), 지연·F1만 사용. OAuth 비용 절대값은 오버헤드·구독 탓 프로바이더간 비교 금지.",
            fontsize=9.0, color=DIM, va="bottom")

    fig.tight_layout()
    fig.savefig(RESULTS / "fig_cross_summary.png", dpi=190, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_cross_summary.png")


def main():
    provs = [
        load_provider("orch_results.json", "Claude\n(claude.exe)", BLUE),
        load_provider("orch_results_gpt.json", "GPT\n(codex)", ORANGE, real_cost=False),
        load_provider("orch_results_gemini.json", "Gemini", SAGE),
    ]
    fig_latency(provs)
    fig_costrank(provs)
    fig_summary(provs)


if __name__ == "__main__":
    main()
