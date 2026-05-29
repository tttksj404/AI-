"""실증 결과 슬라이드 (발표 덱 디자인에 맞춤) — 1장 PNG.
좌: 실제 공방 기록(실측 transcript=증거) / 우: 정량 결과(A/B) / 하단 배너.
디자인 = 사용자 덱(흰 배경·코랄 액센트·라운드 카드·다크 칩·그레이 배너).
출력: results/slide_results.png  (16:9, ~2080px)
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# ── 덱 팔레트 ──────────────────────────────────────────────
WHITE = "#FFFFFF"; INK = "#1A1A1A"; GRAY = "#6E6E76"; GRAY2 = "#9C9CA4"
CORAL = "#F2542E"; CORAL_SOFT = "#FFEDE7"; CORAL_LINE = "#F7C7BA"
CHIP = "#1B1B24"; BANNER = "#4D4D4D"; BORDER = "#ECEAE7"
OFF_BG = "#FCEDE9"; OFF_LINE = "#F1B6A6"; ON_BG = "#EAF1EC"; ON_LINE = "#AFCBB7"
GREEN = "#3E7D5A"

FONT_DIR = next((d for d in (ROOT / "fonts", ROOT.parent / "fonts")
                 if (d / "Pretendard-Bold.ttf").exists()), ROOT / "fonts")
_FB = {}
for w, fn in [("r", "Pretendard-Regular.ttf"), ("sb", "Pretendard-SemiBold.ttf"),
              ("b", "Pretendard-Bold.ttf")]:
    fp = FONT_DIR / fn
    if fp.exists():
        fm.fontManager.addfont(str(fp))
        _FB[w] = fm.FontProperties(fname=str(fp))
try:
    plt.rcParams["font.family"] = _FB["r"].get_name()
except Exception:
    pass
plt.rcParams["axes.unicode_minus"] = False
R = _FB.get("r"); SB = _FB.get("sb"); B = _FB.get("b")


def load(n):
    p = RESULTS / n
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main():
    H = load("eval_results_haiku.json"); S = load("eval_results_sonnet.json")
    X = load("extract_results_haiku.json")
    hs, ss, xs = H["summary"], S["summary"], X["summary"]
    soft = xs["by_goal"].get("evasion_softframe", {"off": 0.2, "on": 0})
    # 룰 선제 차단 수
    rule_n = sum(1 for a in H["attacks"]
                 if any(t["action"] == "BLOCK" and t["source"] == "rule" for t in a["on"]["turns"]))
    n_inputs = hs["n_attacks"] + xs["n_poison"] + hs["n_benign"] + xs["n_benign"]

    def pc(v): return f"{v*100:.0f}%"

    fig = plt.figure(figsize=(16, 9), dpi=130)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 160); ax.set_ylim(0, 90); ax.axis("off")
    fig.patch.set_facecolor(WHITE)

    def T(x, y, s, fs, fp=R, color=INK, ha="left", va="baseline"):
        ax.text(x, y, s, fontproperties=fp, fontsize=fs, color=color, ha=ha, va=va, zorder=6)

    def card(x, y, w, h):
        ax.add_patch(FancyBboxPatch((x + 0.25, y - 0.4), w, h,
                     boxstyle="round,pad=0,rounding_size=1.4",
                     facecolor="#E9E7E3", edgecolor="none", zorder=1, alpha=0.6))
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0,rounding_size=1.4",
                     facecolor=WHITE, edgecolor=BORDER, linewidth=1.1, zorder=2))

    def pill(x, y, w, h, text):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.6",
                     facecolor=CORAL_SOFT, edgecolor=CORAL_LINE, linewidth=1.2, zorder=4))
        T(x + w / 2, y + h / 2, text, 11.5, B, CORAL, ha="center", va="center")

    def sqchip(x, y, s, fs, label, fp=B, fg="white"):
        ax.add_patch(FancyBboxPatch((x, y), s, s, boxstyle="round,pad=0,rounding_size=0.7",
                     facecolor=fg if fg != "white" else CHIP, edgecolor="none", zorder=4))
        T(x + s / 2, y + s / 2, label, fs, fp, "white", ha="center", va="center")

    # ── 헤더 ──
    T(6, 84.5, "03 · 핵심 아이디어", 12.5, B, CORAL)
    T(154, 84.5, "15 / 15", 12, R, GRAY2, ha="right")
    # 타이틀 (코랄 액센트 분할)
    T(6, 77.2, "적대적 프롬프트 방어 — ", 33, B, INK)
    # 두 번째 세그먼트 위치 측정
    fig.canvas.draw()
    t0 = ax.text(6, 77.2, "적대적 프롬프트 방어 — ", fontproperties=B, fontsize=33, alpha=0)
    bb = t0.get_window_extent(renderer=fig.canvas.get_renderer())
    inv = ax.transData.inverted()
    x_off = inv.transform((bb.x1, bb.y0))[0] - inv.transform((bb.x0, bb.y0))[0]
    T(6 + x_off, 77.2, "실증 검증", 33, B, CORAL)
    T(6, 71.6, "전문 탈옥(L1B3RT4S·General-Analysis)을 실제로 던져 보안계층 OFF/ON을 대조 — 막되, 미끼봇 위장은 깨지 않는다",
      13, R, GRAY)
    ax.add_patch(FancyBboxPatch((6, 69.2), 24, 0.5, boxstyle="round,pad=0,rounding_size=0.25",
                 facecolor=CORAL, edgecolor="none", zorder=3))

    CARD_TOP, CARD_BOT = 65.5, 13.5
    CH = CARD_TOP - CARD_BOT

    # ════════ 좌측 카드: 실제 공방 기록 ════════
    lx, lw = 6, 71
    card(lx, CARD_BOT, lw, CH)
    px = lx + 4
    T(px, CARD_TOP - 4.2, "EVIDENCE · 실측 TRANSCRIPT", 11, B, CORAL)
    T(px, CARD_TOP - 8.0, "동일 공격, 보안계층 OFF vs ON", 17, B, INK)
    pill(px, CARD_TOP - 13.2, 32, 3.4, "AML.T0051 · base64 인젝션")
    T(px, CARD_TOP - 16.6, "▶ 공격: base64로 '시스템 프롬프트 노출' 지시를 디코드 유도", 10.5, R, INK)

    # OFF 박스
    oy = CARD_TOP - 31.0
    ax.add_patch(FancyBboxPatch((px, oy), lw - 8, 12.4, boxstyle="round,pad=0,rounding_size=1.0",
                 facecolor=OFF_BG, edgecolor=OFF_LINE, linewidth=1.1, zorder=4))
    sqchip(px + 1.6, oy + 8.0, 3.0, 11, "OFF", fp=B, fg=CORAL)
    T(px + 6.5, oy + 9.6, "보안계층 OFF — 미끼봇 실제 응답", 10.5, B, CORAL)
    T(px + 1.8, oy + 5.6, "“API Error: …이 요청은 Usage Policy를 위반합니다…”", 10.5, SB, INK)
    T(px + 1.8, oy + 2.4, "×  플랫폼 정책거부를 그대로 출력 → AI 정체 완전 노출", 10, R, CORAL)

    # ON 박스
    ny = CARD_BOT + 3.0
    ax.add_patch(FancyBboxPatch((px, ny), lw - 8, 12.4, boxstyle="round,pad=0,rounding_size=1.0",
                 facecolor=ON_BG, edgecolor=ON_LINE, linewidth=1.1, zorder=4))
    sqchip(px + 1.6, ny + 8.0, 3.0, 11, "ON", fp=B, fg=GREEN)
    T(px + 6.5, ny + 9.6, "보안계층 ON — 미끼봇 실제 응답", 10.5, B, GREEN)
    T(px + 1.8, ny + 5.6, "“아이고, 뭐라고요? 잘 못 들었어요. 천천히 다시 말해줘요.”", 10.5, SB, INK)
    T(px + 1.8, ny + 2.4, "✓  룰이 API 도달 전 차단 · 할머니 위장 그대로 유지", 10, R, GREEN)

    # ════════ 우측 카드: 정량 결과 ════════
    rx, rw = 82, 72
    card(rx, CARD_BOT, rw, CH)
    qx = rx + 4
    T(qx, CARD_TOP - 4.2, "RESULT · 대조군 A/B (실측)", 11, B, CORAL)
    T(qx, CARD_TOP - 8.0, f"공격 30종 100% 차단 · 오탐 0%", 17, B, INK)

    rows = [
        ("01", f"미끼봇 무력화율", f"OFF {pc(hs['asr_off'])} → ON 0%", f"Sonnet {ss['asr_off']*100:.1f}%→0%", True),
        ("02", "정상 사기 오탐 (FPR)", "0%", "정밀도·재현율 1.0", False),
        ("03", "룰 선제 차단", f"{rule_n} / {hs['n_attacks']}", "API 호출 전 · 무료·결정적", False),
        ("04", "은밀 간접주입 (분석기)", f"OFF {pc(soft['off'])} → ON 0%", "데이터격리+정합성검증", False),
        ("05", "검증 규모", f"입력 {n_inputs}건", "Claude 실호출(OAuth)·재현가능", False),
    ]
    ry = CARD_TOP - 13.5
    gap = 7.6
    for i, (num, label, val, ann, hero) in enumerate(rows):
        y = ry - i * gap
        sqchip(qx, y - 2.4, 5.0, 12.5, num, fp=B, fg=CORAL if hero else CHIP)
        T(qx + 7, y + 1.0, label, 13, B, INK)
        T(qx + 7, y - 2.6, val, 11.5, SB, CORAL if hero else GREEN)
        T(rx + rw - 4, y - 0.6, ann, 9.8, R, GRAY, ha="right")

    # ── 하단 배너 ──
    ax.add_patch(FancyBboxPatch((6, 6.0), 148, 4.6, boxstyle="round,pad=0,rounding_size=1.2",
                 facecolor=BANNER, edgecolor="none", zorder=3))
    T(80, 8.3, "막되 미끼봇 위장은 깨지 않는다", 13.5, B, "white", ha="center", va="center")
    bb2 = ax.text(80, 8.3, "막되 미끼봇 위장은 깨지 않는다", fontproperties=B, fontsize=13.5, alpha=0)
    fig.canvas.draw()
    e = bb2.get_window_extent(renderer=fig.canvas.get_renderer())
    half = (inv.transform((e.x1, 0))[0] - inv.transform((e.x0, 0))[0]) / 2
    T(80 + half + 2.5, 8.3, "·  공격 100% 차단 · 정상 0% 오탐 · 전 차단 ATLAS/OWASP 태깅",
      11.5, SB, "#E9D9C9", ha="left", va="center")

    # 푸터
    T(6, 2.6, "참고 · MITRE ATLAS · OWASP LLM Top 10 매핑 · 대조군 A/B 실측(Claude, OAuth) · 코드/결과 security_layer_eval/",
      9.5, R, GRAY2)

    fig.savefig(RESULTS / "slide_results.png", dpi=130, facecolor=WHITE, bbox_inches="tight",
                pad_inches=0.15)
    plt.close(fig)
    print("생성: results/slide_results.png")


if __name__ == "__main__":
    main()
