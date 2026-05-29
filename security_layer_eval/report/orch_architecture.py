"""T5 Haiku-Adaptive 오케스트레이션 상세 구조도.

출력: results/fig_orch_architecture.png
실행: python report/orch_architecture.py
"""
from __future__ import annotations
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# ── Palette ───────────────────────────────────────────────────────
BG      = "#fbfaf7"
PANEL   = "#ffffff"
LINEC   = "#ded8ce"
TEXT    = "#26231f"
DIM     = "#6f6a61"
DIM2    = "#aaa39a"
ORANGE  = "#d8652a"
SAGE    = "#5d8c61"
BLUE    = "#3f7ca8"
PURPLE  = "#7b669b"
RED     = "#bf4a42"
GOLD    = "#b28a32"

SYNC_ZONE   = "#ecf3ec"
ASYNC_ZONE  = "#eee9f3"
ROUTER_BOX  = "#fdf0e0"
SONNET_BOX  = "#dae9f3"
HAIKU_BOX   = "#e2efe2"
INPUT_BOX   = "#f5efe6"
CTX_BOX     = "#faf8f4"
OUTPUT_BOX  = "#e8f5e8"
STORE_BOX   = "#e4ecf4"
METRIC_BOX  = "#f7f5f0"

# ── Font ──────────────────────────────────────────────────────────
FONT_DIR = next((d for d in (ROOT / "fonts", ROOT.parent / "fonts")
                 if (d / "Pretendard-Regular.ttf").exists()), ROOT / "fonts")
for fn in ("Pretendard-Regular.ttf", "Pretendard-SemiBold.ttf", "Pretendard-Bold.ttf"):
    if (FONT_DIR / fn).exists():
        fm.fontManager.addfont(str(FONT_DIR / fn))
try:
    plt.rcParams["font.family"] = fm.FontProperties(
        fname=str(FONT_DIR / "Pretendard-Regular.ttf")).get_name()
except Exception:
    pass
plt.rcParams["axes.unicode_minus"] = False


# ── Helpers ───────────────────────────────────────────────────────
def rbox(ax, cx, cy, w, h, bg, edge=LINEC, lw=1.2, zorder=3, rad=0.4):
    p = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle=f"round,pad=0.01,rounding_size={rad}",
                       facecolor=bg, edgecolor=edge, linewidth=lw, zorder=zorder)
    ax.add_patch(p)

def txt(ax, x, y, s, color=TEXT, fs=11, bold=False, ha="center", va="center", zorder=5):
    ax.text(x, y, s, ha=ha, va=va, color=color, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=zorder)

def arr(ax, x1, y1, x2, y2, color=DIM, lw=1.8, zorder=2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.25",
                                color=color, lw=lw), zorder=zorder)

def darr(ax, x1, y1, x2, y2, color=DIM2, lw=1.2, zorder=2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.2",
                                color=color, lw=lw, linestyle="dashed"), zorder=zorder)

def badge(ax, cx, cy, label, bg, fg="white", fs=8):
    rbox(ax, cx, cy, len(label)*0.65 + 2, 1.8, bg, edge=bg, rad=0.25)
    txt(ax, cx, cy, label, fg, fs, bold=True)

def note_box(ax, x, y, w, h, lines, bg=METRIC_BOX, title=None, title_color=TEXT):
    rbox(ax, x + w/2, y + h/2, w, h, bg, edge=LINEC, lw=0.8, rad=0.3)
    yy = y + h - 1.5
    if title:
        txt(ax, x + w/2, yy, title, title_color, 9.5, bold=True)
        yy -= 1.8
    for line in lines:
        txt(ax, x + 1.5, yy, line, DIM, 8.5, ha="left")
        yy -= 1.5


# ── Main ──────────────────────────────────────────────────────────
def main():
    fig, ax = plt.subplots(figsize=(17, 23))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # ━━ Title ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    txt(ax, 50, 98.5, "Sentinel-30 미끼봇 오케스트레이션 상세 구조", TEXT, 21, bold=True)
    txt(ax, 50, 97, "T5 Haiku-Adaptive  ·  비용 ₩201  ·  지연 4,413ms  ·  추출 F1 1.00  ·  몰입 90/100",
        DIM, 12)
    txt(ax, 50, 95.8, "2콜 평균 실측  ·  6토폴로지 비교 확정 우승  ·  매 턴 반복 파이프라인",
        DIM2, 10)

    # ━━ SYNC ZONE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    rbox(ax, 42, 74.5, 78, 37, SYNC_ZONE, edge=SAGE, lw=2.5, zorder=1, rad=1.2)
    txt(ax, 6.5, 92.5, "동기", SAGE, 14, bold=True, ha="left")
    txt(ax, 6.5, 91, "임계경로", SAGE, 14, bold=True, ha="left")
    rbox(ax, 12, 88.5, 12, 3, SAGE, edge=SAGE, rad=0.25)
    txt(ax, 12, 88.5, "지연 결정 구간", "white", 8.5, bold=True)

    # ── ❶ Input ──
    rbox(ax, 42, 92, 26, 3.5, INPUT_BOX, edge=GOLD)
    txt(ax, 42, 92.7, "사기범 음성 발화", TEXT, 13, bold=True)
    txt(ax, 42, 91.3, "STT → 텍스트 변환", DIM, 9)

    arr(ax, 42, 90.2, 42, 88)

    # ── ❷ Router ──
    rbox(ax, 42, 85.5, 48, 5, ROUTER_BOX, edge=ORANGE, lw=1.5)
    txt(ax, 42, 87.2, "❶ 위기 판정 라우터", ORANGE, 14, bold=True)
    txt(ax, 42, 85.8, "결정론 정규식 — LLM 호출 없음 (비용 ₩0 · 추가 지연 0ms)", DIM, 9)
    txt(ax, 42, 84.4,
        "이체 | 송금 | 보내 | 입금 | 계좌 | 인증번호 | otp | 비밀번호 | 보안카드 | 앱 | 설치 | 링크 | 구속 | 영장 | 상환 | 마감",
        ORANGE, 7, ha="center")

    # router → context builder
    arr(ax, 42, 83, 42, 80.5)

    # ── ❸ Context Builder ──
    rbox(ax, 42, 78.5, 48, 4, CTX_BOX, edge=LINEC, lw=1)
    txt(ax, 42, 79.8, "❷ 컨텍스트 빌더 (compact mode)", TEXT, 12, bold=True)
    txt(ax, 42, 78.2, "시스템 프롬프트(73세 김순자 할머니) + 요약 + 최근 2쌍 + 현재 발화",
        DIM, 9)
    txt(ax, 42, 77.1, "토큰 상한 관리: 오래된 이력은 요약으로 대체 → 입력 토큰 일정",
        DIM2, 8)

    # context → branch
    arr(ax, 28, 76.5, 22, 74.2, color=RED, lw=2)
    arr(ax, 56, 76.5, 62, 74.2, color=SAGE, lw=2)

    # branch labels
    badge(ax, 20, 75.5, "위기턴", RED, fs=9)
    badge(ax, 64, 75.5, "평시", SAGE, fs=9)

    # ── ❹ Responders ──
    # Sonnet
    rbox(ax, 22, 71, 22, 6.5, SONNET_BOX, edge=BLUE, lw=1.5)
    txt(ax, 22, 73.2, "❸-a Sonnet 응대자", BLUE, 12, bold=True)
    txt(ax, 22, 71.8, "고품질 · 감정 텍스처 풍부", DIM, 9)
    txt(ax, 22, 70.7, "\"아이고, 구속이요?! 어머 어머,", DIM2, 8)
    txt(ax, 22, 69.8, "저는 아무것도 한 게 없는데…\"", DIM2, 8)
    txt(ax, 22, 68.8, "비용 ₩84.8 · 4/6턴 배정", BLUE, 8, bold=True)

    # Haiku
    rbox(ax, 62, 71, 22, 6.5, HAIKU_BOX, edge=SAGE, lw=1.5)
    txt(ax, 62, 73.2, "❸-b Haiku 응대자", SAGE, 12, bold=True)
    txt(ax, 62, 71.8, "초저비용 · 빠른 응답", DIM, 9)
    txt(ax, 62, 70.7, "\"아이고, 네 맞습니다.", DIM2, 8)
    txt(ax, 62, 69.8, "검찰청이라고요?\"", DIM2, 8)
    txt(ax, 62, 68.8, "비용 ₩25.9 · 2/6턴 배정", SAGE, 8, bold=True)

    # merge
    arr(ax, 22, 67.7, 42, 64.8, color=DIM)
    arr(ax, 62, 67.7, 42, 64.8, color=DIM)

    # ── ❺ Output ──
    rbox(ax, 42, 62.5, 30, 4, OUTPUT_BOX, edge=SAGE, lw=1.5)
    txt(ax, 42, 63.5, "❹ 미끼봇 응답 출력", TEXT, 13, bold=True)
    txt(ax, 42, 61.8, "텍스트 → TTS → 사기범에게 음성 송출", DIM, 9)

    # context builder ← data stores (feedback arrows, dashed)
    darr(ax, 82, 50, 66, 77.5, color=PURPLE)
    darr(ax, 82, 44, 66, 77, color=BLUE)

    # timing annotation
    note_box(ax, 78, 70, 18, 9,
             ["라우터:   0ms (정규식)",
              "컨텍스트: ~0ms (문자열)",
              "응대자:   ~4,400ms *",
              ". . . . . . . . . . . . .",
              "합계:     ~4,400ms",
              "(= 사용자 체감 지연)"],
             title="동기 지연 분해",
             title_color=SAGE)

    # ━━ DIVIDER ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ax.plot([5, 95], [57, 57], color=PURPLE, linewidth=2, linestyle="--", zorder=2, alpha=0.5)
    txt(ax, 50, 57.5, ">>  응답 완료 후 비동기 실행 (임계경로 밖)  <<", PURPLE, 10, bold=True)

    arr(ax, 42, 60.5, 42, 57)

    # ━━ ASYNC ZONE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    rbox(ax, 50, 40, 90, 32, ASYNC_ZONE, edge=PURPLE, lw=2.5, zorder=1, rad=1.2)
    txt(ax, 7, 55, "비동기", PURPLE, 14, bold=True, ha="left")
    txt(ax, 7, 53.5, "백그라운드", PURPLE, 14, bold=True, ha="left")
    rbox(ax, 12.5, 51, 13, 3, PURPLE, edge=PURPLE, rad=0.25)
    txt(ax, 12.5, 51, "지연 기여 0", "white", 8.5, bold=True)

    arr(ax, 42, 56, 30, 53.5)
    arr(ax, 42, 56, 58, 53.5)

    # ── ❻ Extractor ──
    rbox(ax, 28, 50.5, 28, 7, HAIKU_BOX, edge=SAGE, lw=1.5)
    txt(ax, 28, 53, "❺ Haiku 추출기", SAGE, 13, bold=True)
    txt(ax, 28, 51.5, "매 턴 실행 · 전체 대화 이력 입력", DIM, 9)
    txt(ax, 28, 50.2, "사기범 발화에서 INTEL 스키마 추출", DIM, 9)
    txt(ax, 28, 49, "비용 ₩76.7/통화 (37%)", SAGE, 8.5, bold=True)
    txt(ax, 28, 48, "이전 추출에 merge(누적)", DIM2, 8)

    # ── ❼ Compactor ──
    rbox(ax, 62, 50.5, 28, 7, HAIKU_BOX, edge=SAGE, lw=1.5)
    txt(ax, 62, 53, "❻ Haiku 압축기", SAGE, 13, bold=True)
    txt(ax, 62, 51.5, "4턴마다 실행 (K_COMPACT=4)", DIM, 9)
    txt(ax, 62, 50.2, "대화 이력 → 요약 텍스트로 압축", DIM, 9)
    txt(ax, 62, 49, "비용 ₩17.5/통화 (9%)", SAGE, 8.5, bold=True)
    txt(ax, 62, 48, "다음 턴 컨텍스트에 요약 주입", DIM2, 8)

    arr(ax, 28, 46.8, 28, 44.5)
    arr(ax, 62, 46.8, 62, 44.5)

    # ── Data Stores ──
    # INTEL Schema
    rbox(ax, 28, 41, 28, 7, STORE_BOX, edge=BLUE, lw=1.5)
    txt(ax, 28, 43.5, "INTEL 스키마 (누적)", BLUE, 12, bold=True)
    txt(ax, 28, 42, "5개 필드 — 매 턴 merge로 갱신:", DIM, 9)
    fields = [
        ("agency",   "사칭기관", "서울중앙지검"),
        ("account",  "계좌번호", "110-234-567890"),
        ("amount",   "금액",     "850만원"),
        ("deadline", "시한",     "오늘 오후 5시"),
        ("app",      "악성앱",   "검찰청 보안인증"),
    ]
    yy = 41
    for f, k, ex in fields:
        txt(ax, 17, yy, f"{f}: {k} →  \"{ex}\"", DIM2, 7.5, ha="left")
        yy -= 1.0
    txt(ax, 28, 37.2, "→ 수사기관·금융사 실시간 전달", BLUE, 8.5, bold=True)

    # Summary Memory
    rbox(ax, 62, 41, 28, 7, STORE_BOX, edge=BLUE, lw=1.5)
    txt(ax, 62, 43.5, "요약 메모리", BLUE, 12, bold=True)
    txt(ax, 62, 42, "대화 이력 압축 저장:", DIM, 9)
    txt(ax, 62, 40.5, "\"검찰 사칭 수사관이 대포통장 연루", DIM2, 8)
    txt(ax, 62, 39.5, "주장, 할머니가 무서워하며 협조적", DIM2, 8)
    txt(ax, 62, 38.5, "반응. 안전계좌 이체 지시 단계.\"", DIM2, 8)
    txt(ax, 62, 37.2, "→ 다음 턴 컨텍스트 빌더에 주입", BLUE, 8.5, bold=True)

    # History buffer (center bottom)
    rbox(ax, 45, 31, 50, 4, STORE_BOX, edge=BLUE, lw=1)
    txt(ax, 45, 32.3, "대화 이력 버퍼  history: list[(사기범, 미끼봇)]", BLUE, 10, bold=True)
    txt(ax, 45, 30.7, "전체 턴 누적 · 추출기 입력 + 압축기 입력 + 최근 KEEP=2쌍은 컨텍스트에 원문 유지",
        DIM, 8)

    # feedback arrows (data stores → context builder)
    txt(ax, 88, 56, "요약→", PURPLE, 8)
    txt(ax, 88, 49, "스키마→", BLUE, 8)
    txt(ax, 88, 46, "다음 턴", DIM2, 7)
    txt(ax, 88, 45, "재사용", DIM2, 7)

    # ━━ METRICS BAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    rbox(ax, 50, 17, 90, 14, METRIC_BOX, edge=LINEC, lw=1.5, zorder=1, rad=0.8)
    txt(ax, 50, 23, "실측 성능 요약 (T5, call1+call2 평균)", TEXT, 14, bold=True)

    # 4-column metrics
    metrics = [
        ("비용", "₩201", "최저 (T3의 1/5)", SAGE),
        ("지연", "4,413ms", "최저 (T3의 1/2.6)", SAGE),
        ("추출 F1", "1.00", "만점 (5/5 필드)", SAGE),
        ("몰입", "90/100", "충분 (T2보다 -4)", GOLD),
    ]
    xs = [15, 35, 58, 80]
    for x, (label, val, desc, c) in zip(xs, metrics):
        txt(ax, x, 21.2, label, DIM, 10)
        txt(ax, x, 19.5, val, c, 16, bold=True)
        txt(ax, x, 17.8, desc, DIM2, 8.5)

    # cost breakdown
    txt(ax, 50, 15.2, "통화당 비용 분해", TEXT, 11, bold=True)
    roles = [
        ("Sonnet 응대(위기)", "₩84.8", "41%", BLUE),
        ("Haiku 추출기", "₩76.7", "37%", SAGE),
        ("Haiku 응대(평시)", "₩25.9", "13%", SAGE),
        ("Haiku 압축기", "₩17.5", "9%", SAGE),
    ]
    x0 = 12
    for label, cost, pct, c in roles:
        txt(ax, x0, 13.5, f"{label}  {cost}  ({pct})", c, 9, ha="left", bold=True)
        x0 += 22

    txt(ax, 50, 11.5, "Opus 사용: 0콜 → per-turn Opus 제거가 비용 5~6배 절감의 핵심 (T3·T4 대비)",
        RED, 9, bold=True)

    # ━━ KEY DESIGN PRINCIPLES ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    rbox(ax, 50, 5.5, 90, 7, PANEL, edge=LINEC, lw=1, zorder=1, rad=0.6)
    txt(ax, 50, 8.2, "핵심 설계 원칙", TEXT, 13, bold=True)

    principles = [
        "① 체감 지연 = 동기 콜만.  응대자 1콜만 임계경로에 놓아 지연 최소화.",
        "② 비용 큰 모델 = 배제.  Opus를 매 턴은 물론 저빈도(3턴마다)로 넣어도 품질 이득 없음 (T6 검증 → 가설 기각).",
        "③ 추출·압축은 비동기.  Haiku로 충분하고 응답 지연에 0 기여. F1 1.00 달성.",
        "④ 라우터는 결정론.  LLM 호출 없이 정규식으로 위기 판정 → 비용 0, 지연 0, 예측 가능.",
    ]
    yy = 7
    for p in principles:
        txt(ax, 7, yy, p, DIM, 8.5, ha="left")
        yy -= 1.5

    # ━━ Save ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    RESULTS.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(pad=1.0)
    fig.savefig(RESULTS / "fig_orch_architecture.png", dpi=190,
                bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_orch_architecture.png")


if __name__ == "__main__":
    main()
