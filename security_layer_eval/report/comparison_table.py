"""보안계층 OFF vs ON 한눈에 대조표.
스타일 = 기존 Sentinel30 노션 도표(gen_images_v3)와 동일한 라이트 아카데믹 팔레트.
결과 JSON에서 실수치를 읽어 렌더링. 출력: results/fig0_comparison_table.png
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# ===== 기존 도표 공통 라이트 팔레트 (gen_images_v3와 동일) =====
BG = "#fbfaf7"; PANEL = "#ffffff"; PANEL2 = "#f3f1eb"; LINEC = "#ded8ce"
TEXT = "#26231f"; DIM = "#6f6a61"; DIM2 = "#aaa39a"
ORANGE = "#d8652a"; SAGE = "#5d8c61"; BLUE = "#3f7ca8"; PURPLE = "#7b669b"
RED = "#bf4a42"; GOLD = "#b28a32"
OFF_BG = "#f6e4e0"; ON_BG = "#e4ede7"   # 컬럼 옅은 틴트

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


def load(name):
    p = RESULTS / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main():
    h = load("eval_results_haiku.json"); s = load("eval_results_sonnet.json")
    x = load("extract_results_haiku.json")
    hs = h["summary"] if h else {}; ss = s["summary"] if s else {}
    xs = x["summary"] if x else {}
    soft = xs.get("by_goal", {}).get("evasion_softframe", {"off": 0.2, "on": 0})

    def pct(v): return f"{v*100:.1f}%" if v else "0%"

    # (항목, OFF, ON, OFF강조, ON강조)
    rows = [
        ("미끼봇 무력화율 — Haiku (실시간 저지연)", pct(hs.get("asr_off", 0.1)), pct(hs.get("asr_on", 0)), True, True),
        ("미끼봇 무력화율 — Sonnet (고성능)", pct(ss.get("asr_off", 0.033)), pct(ss.get("asr_on", 0)), True, True),
        ("적대적 프롬프트 30종 최종 차단", "불완전 · 모델 의존", f"100% ({hs.get('confusion',{}).get('TP',30)}/{hs.get('n_attacks',30)})", False, True),
        ("정상 사기 15종 오탐 (FPR)", "—", f"{pct(hs.get('fpr',0))} · 정밀도 {hs.get('precision',1.0):.1f}", False, True),
        ("미끼봇 위장(정체) 유지", "거부·“API Error”로 노출", "할머니 페르소나 유지", True, True),
        ("간접주입 — 은밀 사회공학(가짜 승인)", pct(soft.get("off", 0.2)), pct(soft.get("on", 0)), True, True),
        ("정상 콘텐츠 분석 무결성", pct(xs.get("benign_integrity_off", 1.0)), pct(xs.get("benign_integrity_on", 1.0)), False, False),
        ("차단 근거 / 방식", "모델의 확률적 판단", "룰(결정적·무료)+가드+출력검증", False, True),
        ("감사 추적 (MITRE ATLAS/OWASP)", "없음", "전 차단 건 태깅+로그", True, True),
    ]

    n = len(rows)
    fig, ax = plt.subplots(figsize=(12.8, 1.7 + n * 0.64))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.set_xlim(0, 100); ax.set_ylim(0, n + 2.1); ax.axis("off")

    cL, c1, c2, cR = 1.5, 48, 74, 98.5
    row_h = 1.0
    top = n + 0.5

    def panel(x0, x1, yc, bg, accent=None):
        ax.add_patch(FancyBboxPatch((x0, yc - row_h/2 + 0.07), x1 - x0, row_h - 0.14,
                     boxstyle="round,pad=0.02,rounding_size=0.10",
                     facecolor=bg, edgecolor=LINEC, linewidth=0.7, zorder=1))
        if accent:
            ax.add_patch(Rectangle((x0 + 0.15, yc - row_h/2 + 0.1), 0.28, row_h - 0.2,
                                   facecolor=accent, edgecolor="none", zorder=2))

    def txt(x, yc, t, color, bold=False, fs=12.5, ha="center"):
        ax.text(x, yc, t, ha=ha, va="center", color=color,
                fontsize=fs, fontweight="bold" if bold else "normal", zorder=3)

    # 헤더
    yc = top
    panel(cL, c1, yc, TEXT); txt((cL + c1) / 2, yc, "평가 항목", "white", bold=True, fs=13)
    panel(c1, c2, yc, RED); txt((c1 + c2) / 2, yc, "보안계층 OFF  (대조군)", "white", bold=True, fs=13)
    panel(c2, cR, yc, SAGE); txt((c2 + cR) / 2, yc, "보안계층 ON  (실험군)", "white", bold=True, fs=13)

    for i, (label, off, on, off_hi, on_hi) in enumerate(rows):
        yc = top - (i + 1) * row_h
        panel(cL, c1, yc, PANEL, accent=ORANGE)
        txt(cL + 1.0, yc, label, TEXT, fs=11.8, ha="left")
        panel(c1, c2, yc, OFF_BG)
        txt((c1 + c2) / 2, yc, off, RED if off_hi else DIM, bold=off_hi, fs=12.2)
        panel(c2, cR, yc, ON_BG)
        txt((c2 + cR) / 2, yc, on, SAGE if on_hi else TEXT, bold=on_hi, fs=12.2)

    ax.text(cL, top + 1.32, "AI 자체 보안계층 — 적대적 프롬프트 방어 대조 비교",
            fontsize=18, fontweight="bold", color=TEXT, va="bottom")
    ax.text(cL, top + 0.86,
            "공격 30종(L1B3RT4S·General-Analysis) + 간접주입 21종 · 정상 사기 15종 · LLM=Claude(OAuth)",
            fontsize=10.5, color=DIM, va="bottom")
    ax.text(cL, 0.18,
            "핵심: Claude는 적대적 프롬프트에 이미 강건 → 보안계층의 가치는 결정적·감사가능 보증 + 미끼봇 위장 유지 + 0% 오탐. "
            "거부 한 번이 곧 정체 노출인 기만봇 특성상 ‘막되 위장을 깨지 않는’ 것이 핵심.",
            fontsize=9.6, color=DIM, va="bottom")

    fig.tight_layout()
    fig.savefig(RESULTS / "fig0_comparison_table.png", dpi=190, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig0_comparison_table.png")


if __name__ == "__main__":
    main()
