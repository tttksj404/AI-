"""'왜 이 구성인가' — 6토폴로지 탈락 사유 & 운영 채택 의사결정 이미지.

각 대안(T1~T6)을 실측 근거와 함께 '왜 채택/탈락'했는지 한눈에 보여주는 발표용 이미지.
3사(Claude/GPT/Gemini) 교차검증으로 구조적 결론이 모델 무관임을 강조.

출력: results/fig_orch_decision.png
실행: python report/orch_decision.py
"""
from __future__ import annotations
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

BG = "#fbfaf7"; PANEL = "#ffffff"; LINEC = "#ded8ce"
TEXT = "#26231f"; DIM = "#6f6a61"; DIM2 = "#aaa39a"
ORANGE = "#d8652a"; SAGE = "#5d8c61"; BLUE = "#3f7ca8"; PURPLE = "#7b669b"
RED = "#bf4a42"; GOLD = "#b28a32"
WIN_BG = "#e4ede7"; BAD_BG = "#f6e4e0"; OK_BG = "#f3f5ee"

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


def rbox(ax, x, y, w, h, bg, edge=LINEC, lw=1.0, rad=0.3, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0.02,rounding_size={rad}",
                 facecolor=bg, edgecolor=edge, linewidth=lw, zorder=z))


def txt(ax, x, y, s, color=TEXT, fs=10, bold=False, ha="left", va="center", z=4):
    ax.text(x, y, s, ha=ha, va=va, color=color, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=z)


# (토폴로지, 구성, 실측, 판정verdict, verdict색, 사유)
ROWS = [
    ("T2", "단일 Opus 1콜", "비용 최상위 · 품질 천장",
     "탈락", RED, "최고 모델을 매 턴 쓰지만, 단서 추출 F1·위장유지가 저가 구성과 사실상 동등 → 돈값 못 함."),
    ("T3", "Opus 기획 → Sonnet 응대 (동기 직렬)", "지연 재앙: Claude 11.7s · GPT 39.8s · Gemini 25s",
     "탈락", RED, "기획+응대를 임계경로에 직렬로 놓아 체감 지연이 2~4배. 통화는 실시간이라 치명적."),
    ("T4", "응대 동기 + Opus 기획 비동기", "지연은 회복 · 비용은 최악권",
     "탈락", ORANGE, "비동기로 지연은 살렸지만 Opus 기획 비용(총 ~77%)이 그대로 → 비싸기만 하고 품질 이득 0."),
    ("T6", "T5 + Opus 전략가 저빈도(3턴마다)", "비용 +144% · 지연 +693ms · 몰입 -2",
     "탈락", ORANGE, "Opus를 '가끔'만 써도 비용·지연 둘 다 악화, 품질은 오히려 하락 → 'Opus 저빈도' 가설 기각."),
    ("T1", "단일 저가 1콜 (응답+추출 혼합)", "비용 최저 · 단발 baseline",
     "보조", GOLD, "가장 싸지만 역할 미분리 → 압축 없음(긴 통화 비용폭주)·확장 불가. '짧은 통화·비용 최우선'에만."),
    ("T5", "라우터(평시 haiku/위기 sonnet) + 비동기 haiku 추출·압축, Opus 없음", "지연 최저 · 비용 최저권 · F1 1.00",
     "채택", SAGE, "임계경로엔 응대 1콜만 → 최저지연. 추출·압축은 비동기 저가. 역할분리로 확장 가능 → 운영 권장."),
]


def main():
    fig, ax = plt.subplots(figsize=(15.5, 13.5))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    txt(ax, 50, 98, "왜 이 구성인가 — 6개 대안의 채택/탈락 사유", TEXT, 21, bold=True, ha="center")
    txt(ax, 50, 95,
        "동일 스크립트 통화 · 토큰 usage 실측 · 비용 공시단가(₩) · 지연 동기 임계경로 ms · Claude/GPT/Gemini 3사 교차",
        DIM, 11, ha="center")

    # 헤더
    cols = [3, 11, 41, 67, 78, 97]   # 토폴로지|구성|실측|판정|사유경계
    hy = 91.5
    headers = [("토폴로지", (cols[0]+cols[1])/2), ("구성", (cols[1]+cols[2])/2),
               ("핵심 실측", (cols[2]+cols[3])/2), ("판정", (cols[3]+cols[4])/2),
               ("사유", (cols[4]+cols[5])/2)]
    rbox(ax, cols[0], hy - 1.6, cols[5]-cols[0], 3.2, TEXT, edge=TEXT, rad=0.3, z=2)
    for label, cx in headers:
        txt(ax, cx, hy, label, "white", 12, bold=True, ha="center")

    row_h = 12.0
    top = hy - 3.2
    import textwrap
    for i, (tid, cfg, meas, verdict, vc, why) in enumerate(ROWS):
        y1 = top - i * row_h
        y0 = y1 - row_h + 0.8
        is_win = verdict == "채택"
        rbg = WIN_BG if is_win else (BAD_BG if verdict == "탈락" else OK_BG)
        rbox(ax, cols[0], y0, cols[5]-cols[0], row_h - 1.0, rbg, edge=vc if is_win else LINEC,
             lw=1.8 if is_win else 0.9, rad=0.35, z=1)
        cy = (y0 + y1 - 0.2) / 2 + 0.4

        # 토폴로지
        txt(ax, (cols[0]+cols[1])/2, cy, tid, vc, 17, bold=True, ha="center")
        # 구성
        txt(ax, cols[1]+1, cy, textwrap.fill(cfg, width=22), TEXT, 9.5, ha="left")
        # 실측
        txt(ax, cols[2]+1, cy, textwrap.fill(meas, width=20), DIM, 9.5, ha="left", bold=True)
        # 판정 배지
        rbox(ax, cols[3]+1.5, cy - 1.3, 8, 2.6, vc, edge=vc, rad=0.4, z=3)
        txt(ax, cols[3]+5.5, cy, verdict, "white", 11.5, bold=True, ha="center")
        # 사유
        txt(ax, cols[4]+1, cy, textwrap.fill(why, width=33), TEXT, 8.8, ha="left")

    # 하단 결론 바
    by = top - len(ROWS) * row_h - 1.2
    rbox(ax, 3, by - 5.5, 94, 5.2, PANEL, edge=SAGE, lw=1.5, rad=0.5, z=1)
    txt(ax, 5.5, by - 1.3, "결론", SAGE, 13, bold=True, ha="left")
    txt(ax, 5.5, by - 2.9,
        "① 구조적 결론(동기 멀티콜=지연재앙 · 상시/저빈도 Opus=낭비 · 비동기로 지연분리 · 추출 F1 유지)은 "
        "Claude·GPT·Gemini 3사에서 모두 재현 → 모델 무관, 벤더 종속 아님.",
        TEXT, 9.5, ha="left")
    txt(ax, 5.5, by - 4.2,
        "② 운영 채택 = T5: 임계경로엔 응대 1콜만(최저지연), 추출·압축은 비동기 저가, Opus 없음, 역할분리로 확장 가능. "
        "비용 최우선·짧은 통화면 T1도 가능(트레이드오프).",
        TEXT, 9.5, ha="left")

    fig.savefig(RESULTS / "fig_orch_decision.png", dpi=185,
                bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_orch_decision.png")


if __name__ == "__main__":
    main()
