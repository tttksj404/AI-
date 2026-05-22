"""Sentinel-30 발표용 16:9 슬라이드 PDF 생성기.

Genspark "현대 학술 연구 발표" 템플릿을 참고한 밝은 연구 발표 톤.
흰 배경, 얇은 구분선, 큰 숫자, 오렌지 포인트, 절제된 Pretendard 타이포그래피.
"""
from pathlib import Path
from datetime import datetime

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "발표자료_Sentinel30_slides.pdf"
IMG = ROOT / "images"

# ─── Fonts ──────────────────────────────────────────────────────
pdfmetrics.registerFont(TTFont("Body", str(ROOT / "fonts/Pretendard-Regular.ttf")))
pdfmetrics.registerFont(TTFont("BodySB", str(ROOT / "fonts/Pretendard-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("BodyB", str(ROOT / "fonts/Pretendard-Bold.ttf")))

# ─── Palette (LIGHT · Modern Academic Research) ─────────────────
BG       = colors.HexColor("#fbfaf7")
PANEL    = colors.HexColor("#ffffff")
PANEL2   = colors.HexColor("#f3f1eb")
LINEC    = colors.HexColor("#ded8ce")
TEXT     = colors.HexColor("#26231f")
DIM      = colors.HexColor("#6f6a61")
DIM2     = colors.HexColor("#aaa39a")
WHITE    = colors.HexColor("#ffffff")

ORANGE   = colors.HexColor("#d8652a")   # primary
SAGE     = colors.HexColor("#5d8c61")
BLUE     = colors.HexColor("#3f7ca8")
PURPLE   = colors.HexColor("#7b669b")
RED      = colors.HexColor("#bf4a42")
GOLD     = colors.HexColor("#b28a32")

# Slide size 16:9 — 1920×1080 logical (use 13.33×7.5 inch)
SW, SH = 13.33 * inch, 7.5 * inch

# ─── Drawing primitives ─────────────────────────────────────────
def fill_bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, SW, SH, fill=1, stroke=0)


_PAGE = {"idx": 0, "total": 22}  # build()가 갱신


def slide_chrome(c, *_args, section="Sentinel-30"):
    """페이지 번호 + 얇은 학술 발표형 룰라인."""
    idx = _PAGE["idx"]
    total = _PAGE["total"]
    # top/bottom hairlines
    c.setStrokeColor(LINEC)
    c.setLineWidth(0.5)
    c.line(0.6*inch, SH - 0.42*inch, SW - 0.6*inch, SH - 0.42*inch)
    c.line(0.6*inch, 0.42*inch, SW - 0.6*inch, 0.42*inch)
    # footer left: section / right: page
    c.setFont("BodySB", 8)
    c.setFillColor(DIM)
    c.drawString(0.6*inch, 0.22*inch, f"SENTINEL-30  ·  보이스피싱 ROI 파괴 플랫폼")
    c.drawRightString(SW - 0.6*inch, 0.22*inch, f"{idx:02d} / {total:02d}")


def kicker(c, x, y, label, color=ORANGE, size=9):
    """상단 카테고리 라벨."""
    c.setFillColor(color)
    c.rect(x, y + 1, 5, 5, fill=1, stroke=0)
    c.setFont("BodySB", size)
    c.setFillColor(color)
    c.drawString(x + 12, y, label)


def h1(c, x, y, text, size=44, color=None):
    c.setFont("BodyB", size)
    c.setFillColor(color or TEXT)
    c.drawString(x, y, text)


def h2(c, x, y, text, size=28, color=None):
    c.setFont("BodyB", size)
    c.setFillColor(color or TEXT)
    c.drawString(x, y, text)


def body(c, x, y, text, size=13, color=None, font="Body"):
    c.setFont(font, size)
    c.setFillColor(color or TEXT)
    c.drawString(x, y, text)


def dim_text(c, x, y, text, size=11):
    body(c, x, y, text, size=size, color=DIM)


def hr(c, x, y, w, color=None):
    c.setStrokeColor(color or LINEC)
    c.setLineWidth(0.8)
    c.line(x, y, x + w, y)


def panel(c, x, y, w, h, accent=None, fill=PANEL, edge=LINEC):
    c.setFillColor(fill)
    c.setStrokeColor(edge)
    c.setLineWidth(0.6)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    if accent:
        # top accent bar
        c.setFillColor(accent)
        c.setStrokeColor(accent)
        c.rect(x, y + h - 3, w, 3, fill=1, stroke=0)


def chip(c, x, y, w, h, label, color=ORANGE, text_color=None):
    c.setFillColor(color)
    c.setStrokeColor(color)
    c.roundRect(x, y, w, h, h/2, fill=1, stroke=0)
    c.setFont("BodySB", 9)
    c.setFillColor(text_color or WHITE)
    c.drawCentredString(x + w/2, y + h/2 - 3, label)


def image(c, path, x, y, w, h):
    """이미지 비율 유지하며 박스 안에 fit."""
    p = IMG / path if not Path(path).is_absolute() else Path(path)
    if not p.exists():
        return
    with PILImage.open(p) as im:
        iw, ih = im.size
    r = min(w/iw, h/ih)
    nw, nh = iw*r, ih*r
    nx = x + (w - nw)/2
    ny = y + (h - nh)/2
    c.drawImage(str(p), nx, ny, nw, nh, preserveAspectRatio=True, mask='auto')


def stat_block(c, x, y, w, h, big, label, sub=None, color=ORANGE):
    """KPI 큰 숫자 블록."""
    panel(c, x, y, w, h, accent=color)
    c.setFont("BodyB", 40)
    c.setFillColor(color)
    c.drawCentredString(x + w/2, y + h - 58, big)
    c.setFont("BodyB", 12)
    c.setFillColor(TEXT)
    c.drawCentredString(x + w/2, y + h - 84, label)
    if sub:
        c.setFont("Body", 9)
        c.setFillColor(DIM)
        c.drawCentredString(x + w/2, y + h - 100, sub)


def bullet(c, x, y, text, size=12, color=None, bullet_color=ORANGE):
    c.setFillColor(bullet_color)
    c.circle(x + 4, y + 4, 2.2, fill=1, stroke=0)
    c.setFont("Body", size)
    c.setFillColor(color or TEXT)
    c.drawString(x + 14, y, text)


def callout(c, x, y, w, h, text, color=ORANGE):
    """좌측 컬러 바 + 박스 인용."""
    c.setFillColor(PANEL2)
    c.setStrokeColor(LINEC)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)
    c.setFillColor(color)
    c.rect(x, y, 4, h, fill=1, stroke=0)
    c.setFont("BodyB", 13)
    c.setFillColor(TEXT)
    c.drawString(x + 16, y + h/2 - 5, text)


def takeaway(c, text, color=ORANGE):
    """슬라이드 하단 한 줄 결론 박스 — 모든 본문 슬라이드 공통."""
    x = 0.6*inch
    y = 0.6*inch
    w = SW - 1.2*inch
    h = 0.55*inch
    c.setFillColor(PANEL2)
    c.setStrokeColor(color)
    c.setLineWidth(0)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=0)
    # 좌측 큰 화살표 마커
    c.setFillColor(color)
    c.setFont("BodyB", 18)
    c.drawString(x + 18, y + h/2 - 7, "→")
    # 본문
    c.setFont("BodyB", 14)
    c.setFillColor(TEXT)
    c.drawString(x + 48, y + h/2 - 6, text)


def eyebrow_title(c, kicker_text, headline, sub=None,
                  headline_size=52, kicker_color=ORANGE):
    """상단 카테고리 + 큰 헤드라인 + 부제 — 시선 집중 시스템.
    되돌려서 본문 시작 y좌표(=다이어그램 박스 상단)를 리턴."""
    # eyebrow
    x = 0.9*inch
    c.setFillColor(kicker_color)
    c.rect(x, SH - 0.66*inch + 1, 5, 5, fill=1, stroke=0)
    c.setFont("BodySB", 10)
    c.setFillColor(kicker_color)
    c.drawString(x + 12, SH - 0.69*inch, kicker_text)
    # H1 headline
    c.setFont("BodyB", headline_size)
    c.setFillColor(TEXT)
    c.drawString(x, SH - (0.66*inch + headline_size*0.95), headline)
    y_after_h1 = SH - (0.66*inch + headline_size*0.95) - 8
    if sub:
        c.setFont("Body", 14)
        c.setFillColor(DIM)
        c.drawString(x, y_after_h1 - 14, sub)
        y_after_h1 -= 28
    return y_after_h1 - 10


def accent_phrase(c, x, y, segments, size=14, base_color=None):
    """텍스트에 부분 강조 색을 입혀 한 줄 표현.
    segments: [(text, color or None), ...] — None이면 base_color 사용.
    """
    cur = x
    for text, col in segments:
        c.setFont("BodyB" if col else "Body", size)
        c.setFillColor(col or base_color or TEXT)
        c.drawString(cur, y, text)
        cur += pdfmetrics.stringWidth(text, "BodyB" if col else "Body", size)


# ═══════════════════════════════════════════════════════════════
# 슬라이드 정의
# ═══════════════════════════════════════════════════════════════

TOTAL = 22  # update if you add/remove slides


def s01_cover(c):
    fill_bg(c)
    c.setStrokeColor(LINEC)
    c.setLineWidth(0.7)
    c.line(0.8*inch, SH - 0.62*inch, SW - 0.8*inch, SH - 0.62*inch)
    c.line(0.8*inch, 0.72*inch, SW - 0.8*inch, 0.72*inch)

    c.setFont("BodySB", 10)
    c.setFillColor(ORANGE)
    c.drawString(0.9*inch, SH - 0.95*inch, "AI 민생 10대 프로젝트 8번 · 보이스피싱 공동대응")
    c.setFillColor(DIM)
    c.drawRightString(SW - 0.9*inch, SH - 0.95*inch, "AI 해커톤 2026 · 개발 기획 발표")

    c.setFont("BodyB", 76)
    c.setFillColor(TEXT)
    c.drawString(0.9*inch, SH - 2.1*inch, "Sentinel-30")

    c.setFont("BodySB", 28)
    c.setFillColor(TEXT)
    c.drawString(0.9*inch, SH - 2.75*inch, "보이스피싱 능동방어 인공지능(AI) 플랫폼")
    c.drawString(0.9*inch, SH - 3.16*inch, "— 30분 환수 골든타임 자동화")

    c.setFont("Body", 14)
    c.setFillColor(DIM)
    c.drawString(0.9*inch, SH - 3.72*inch,
                 "탐지·차단을 보완하여 사기범의 시간·음성·계좌 정보를 증거 자산으로 수집하는 시스템.")

    # 우측 연구 초록형 패널
    x = 8.2*inch
    y = 3.18*inch
    w = SW - x - 0.9*inch
    h = 1.75*inch
    panel(c, x, y, w, h, accent=ORANGE, fill=PANEL)
    c.setFont("BodySB", 9)
    c.setFillColor(ORANGE)
    c.drawString(x + 18, y + h - 30, "RESEARCH QUESTION")
    c.setFont("BodySB", 15)
    c.setFillColor(TEXT)
    c.drawString(x + 18, y + h - 58, "사기 산업의 시간당 수익률을")
    c.drawString(x + 18, y + h - 82, "어떻게 0에 가깝게 만들 것인가?")
    c.setFont("Body", 10)
    c.setFillColor(DIM)
    c.drawString(x + 18, y + 22, "Golden Time · Guardian Live · Multi-Agent LLM")

    # 4개 핵심 지표 — 좌우 폭 가득 채우기
    box_y = 1.36*inch
    x0 = 0.9*inch
    total_w = SW - 1.8*inch
    gap = 0.32*inch
    metrics = [
        ("30분", "환수 골든타임", "송금완료~인출시작", ORANGE),
        ("8,545억", "2024 피해액", "경찰청, 전년 1.9배 증가", RED),
        ("52.3%", "60대 이상 피해", "고령층 집중", GOLD),
        ("7", "Defense-in-Depth", "능동방어 7대 레이어", SAGE),
    ]
    box_w = (total_w - 3*gap) / 4
    for i, (big, label, sub, col) in enumerate(metrics):
        x = x0 + i*(box_w + gap)
        c.setStrokeColor(col)
        c.setLineWidth(1.6)
        c.line(x, box_y + 0.92*inch, x + box_w, box_y + 0.92*inch)
        c.setFont("BodyB", 32)
        c.setFillColor(col)
        c.drawString(x, box_y + 0.5*inch, big)
        c.setFont("BodySB", 11)
        c.setFillColor(TEXT)
        c.drawString(x, box_y + 0.22*inch, label)
        c.setFont("Body", 9)
        c.setFillColor(DIM)
        c.drawString(x, box_y + 0.02*inch, sub)

    # 하단 메타
    c.setFont("Body", 9)
    c.setFillColor(DIM)
    c.drawRightString(SW - 0.9*inch, 1.0*inch, "TEAM · 6인 (기획1·ML2·BE1·UX1·법리보안1)")
    c.drawRightString(SW - 0.9*inch, 0.82*inch, f"DATE · {datetime.now():%Y-%m-%d}  ·  STAGE · 예선 4주 + 본선 무박 2일")


def s02_problem(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 2  ·  문제 정의 및 필요성",
                  "보이스피싱 피해 현황 — 왜 지금인가",
                  "비대면 거래 확산 + AI 사기 자동화 + 환급법 한계(-22~35%) — 능동적 보완책이 필요한 시점",
                  headline_size=42)

    # 메인 차트 — 연도별 추이 + 기관사칭 도넛
    image(c, "chart_problem_trend.png", 0.55*inch, 1.6*inch,
          SW - 1.1*inch, SH - 3.4*inch)
    # 보조 통계 한 줄
    c.setFont("BodySB", 12)
    c.setFillColor(DIM)
    c.drawCentredString(SW/2, 1.35*inch,
                        "1인당 피해 +73% (평균 4,100만원)  ·  발생 건수 -33% (2021 대비)  ·  환수율 25% 미만")

    takeaway(c, "사기범 입장에서 잃을 자원이 없는 구조 — 방어를 보완할 능동 자산 회수 모델이 필요하다.")


def s03_reframe(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3  ·  핵심 아이디어",
                  "문제 재정의 — 사기 산업 ROI 분해",
                  "탐지·차단을 보완하여 사기범의 시간·정보·도구를 비용으로 전환하는 능동방어 메커니즘",
                  headline_size=46)
    image(c, "08_roi_mechanism.png", 0.55*inch, 1.4*inch,
          SW - 1.1*inch, SH - 3.3*inch)
    takeaway(c, "공격 벡터 3종 — 통화 수↓ · 성공률↓ · 운영 비용↑ — 모두 동시에 작동시킨다.")


def s04_golden_time(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.1  ·  서비스 흐름",
                  "30분 환수 골든타임",
                  "송금 완료(T+15)에서 인출 시작(T+30) 사이 — 미끼봇·정보 수집·자동 신고가 병렬 작동",
                  headline_size=52)
    image(c, "02_golden_timeline.png", 0.55*inch, 1.4*inch,
          SW - 1.1*inch, SH - 3.3*inch)
    takeaway(c, "T+15 ~ T+30 구간 — 환수 가능한 단 하나의 시간 창에 모든 자동화를 투입한다.")


def s05_seven_layers(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.1  ·  서비스 흐름",
                  "능동방어 7대 레이어",
                  "Defense-in-Depth 구조 — 한 레이어 우회 시 나머지 6개가 자원 흡수를 지속",
                  headline_size=52)
    image(c, "06_seven_layers.png", 0.55*inch, 1.3*inch,
          SW - 1.1*inch, SH - 3.2*inch)
    takeaway(c, "AI 미끼봇 + 정보 수집 엔진 + 정보전 허브 + AI 보안 + IR + 법적 안전지대 + 시니어 UX.")


def s06_architecture(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.1  ·  서비스 흐름",
                  "시스템 데이터 흐름 (5단)",
                  "미끼번호 풀 → AI 미끼봇 → 정보 수집 엔진 → 정보 허브 → 시니어 가디언 앱",
                  headline_size=48)
    image(c, "01_architecture.png", 0.55*inch, 1.3*inch,
          SW - 1.1*inch, SH - 3.2*inch)
    takeaway(c, "사기범 통화는 들어오는 순간 데이터가 된다 — 통신사·경찰·금감원으로 자동 전달.")


def s07_multi_agent(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  AI 기술 활용 계획",
                  "다중 에이전트 대규모 언어 모델(LLM) 구조",
                  "단일 LLM은 긴 통화에서 토큰 누적 → 응답 지연·환각(없는 정보 생성) — 역할별 5종 분리 + 대화 요약 모듈로 입력 항상 8K 이하 유지",
                  headline_size=34)

    # 다이어그램에 1.5s/-62%/∞ KPI + MODEL TIERING + PROBLEM 모두 포함되어
    # 별도 KPI 박스 제거 — 이미지 박스를 takeaway 직전까지 크게 확장.
    image(c, "10_multi_agent.png", 0.45*inch, 1.35*inch,
          SW - 0.9*inch, SH - 3.4*inch)

    takeaway(c, "T_resp = 0.9+0.4+0.2 = 1.5s · Cost = Opus1+Sonnet3+Haiku1 vs Opus5 → −62%.")


def s_latency_mitigation(c):
    """[CH 3.2] 응답 지연 근본 해결책 — 응답 트리 + 사전 합성 TTS."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  응답 지연 근본 해결",
                  "응답 트리(Response Tree) + 사전 합성 TTS",
                  "음성 인식(STT)→대규모 언어 모델(LLM)→음성 합성(TTS) 풀 파이프라인은 너무 느림 — 사전 구축된 응답 트리에서 즉시 매칭하고 LLM은 백그라운드 정교화",
                  headline_size=26)

    # 상단: 시간 흐름 다이어그램 (사기범 발화 → 응답)
    top_y = SH - 4.5*inch
    top_h = 2.40*inch
    panel(c, 0.55*inch, top_y, SW - 1.1*inch, top_h, accent=ORANGE)

    body(c, 0.55*inch + 18, top_y + top_h - 22,
         "근본 해결책 — 2단 응답 구조 (즉시 매칭 + 백그라운드 정교화)",
         size=12, font="BodyB", color=ORANGE)

    # 타임라인 (수평) — 사기범 발화 끝 시점 t=0
    tl_y = top_y + 0.92*inch
    tl_x0 = 0.55*inch + 50
    tl_x1 = SW - 0.55*inch - 30
    # 타임라인 베이스
    c.setStrokeColor(LINEC)
    c.setLineWidth(1.5)
    c.line(tl_x0, tl_y, tl_x1, tl_y)
    # 시간 마커
    markers = [
        (0.00, "사기범\n발화 끝", BLUE),
        (0.15, "분류기\n매칭", ORANGE),
        (0.25, "응답 트리\n노드 선택", ORANGE),
        (0.35, "사전 TTS\n재생 시작", SAGE),
        (1.20, "LLM 정교화\n다음 turn 적용", PURPLE),
    ]
    tl_w = tl_x1 - tl_x0
    for t, lbl, col in markers:
        x = tl_x0 + tl_w * (t / 1.5)
        # 점
        c.setFillColor(col)
        c.circle(x, tl_y, 5, fill=1, stroke=0)
        # 시간 라벨 (위)
        c.setFont("BodyB", 9)
        c.setFillColor(col)
        c.drawCentredString(x, tl_y + 14, f"{int(t*1000)}ms")
        # 단계 라벨 (아래)
        c.setFont("Body", 8.5)
        c.setFillColor(TEXT)
        for j, line in enumerate(lbl.split("\n")):
            c.drawCentredString(x, tl_y - 14 - j*11, line)

    # 메시지 — 핵심 결과
    c.setFont("BodyB", 11)
    c.setFillColor(SAGE)
    c.drawString(0.55*inch + 18, top_y + 14,
                 "→ 첫 응답 350ms (노년 자연 응답 P50 2.1초보다 빠르므로 일부러 발화 시작을 200~400ms 지연 = 자연스러움)")
    c.setFont("BodySB", 10)
    c.setFillColor(DIM)
    c.drawString(0.55*inch + 18, top_y + 0.42*inch,
                 "LLM 풀 추론 1.5초는 다음 응답에 적용 — 통화 흐름은 끊기지 않는다")

    # 하단: 3개 핵심 메커니즘 카드 (5전략 축소)
    by = 1.35*inch
    bh = top_y - by - 0.20*inch
    bw = (SW - 1.1*inch - 2*0.18*inch)/3

    mechanisms = [
        ("응답 트리 사전 구축",
         "시나리오 8종 × 평균 30 turn × 분기 = 약 240 응답 노드",
         "각 노드는 사전 LLM 생성 + 음성 합성(TTS) 완료된 음원 보유",
         "분류기 + 트리 매칭 200ms 안에 즉시 응답",
         BLUE),
        ("발화 중 병렬 STT + 분류",
         "사기범 발화 중간부터 음성 인식 시작",
         "마지막 음성 끝나기 전에 시나리오 분류·노드 선택 완료",
         "발화 끝 + 100ms 안에 응답 음원 재생 시작",
         ORANGE),
        ("LLM 백그라운드 정교화",
         "사전 응답 재생 중에 LLM이 컨텍스트 보강",
         "더 적절한 응답 생성 시 다음 turn에 자연스럽게 교체",
         "사기범 입장에서는 일관된 흐름의 한 통화",
         PURPLE),
    ]
    for i, (title, m1, m2, result, col) in enumerate(mechanisms):
        x = 0.55*inch + i*(bw + 0.18*inch)
        c.setFillColor(col); c.rect(x, by + bh - 3, bw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, by, bw, bh - 3, 6, fill=1, stroke=1)
        # 제목
        c.setFont("BodyB", 12)
        c.setFillColor(col)
        c.drawString(x + 14, by + bh - 26, title)
        # 메커니즘 1·2
        c.setFont("Body", 9.5)
        c.setFillColor(TEXT)
        c.drawString(x + 14, by + bh - 50, "• " + m1)
        c.drawString(x + 14, by + bh - 68, "• " + m2)
        # 결과 (강조)
        c.setFont("BodySB", 9.5)
        c.setFillColor(col)
        # wrap result
        words = result.split(" ")
        ln = ""
        lines = []
        for w in words:
            test = (ln + " " + w).strip()
            if pdfmetrics.stringWidth(test, "BodySB", 9.5) > bw - 28:
                lines.append(ln); ln = w
            else:
                ln = test
        if ln: lines.append(ln)
        for j, line in enumerate(lines[:3]):
            c.drawString(x + 14, by + 28 - j*14, ("→ " if j == 0 else "  ") + line)

    takeaway(c, "응답 트리 240노드 + 사전 합성 TTS → 첫 응답 350ms (의도적 지연 적용) — LLM 풀 추론은 다음 turn으로 흡수.")


def s_text_vs_voice(c):
    """[CH 3.2] 텍스트 패턴이 본질, 음성지문은 보조 — 식별 메커니즘 명확화."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  식별 메커니즘",
                  "수법(텍스트)이 1차 식별 기준, 음성지문은 보조",
                  "사기범 음성 데이터는 시중에 거의 없지만 음성 인식(STT)으로 텍스트화되면 수법 패턴은 즉시 추출 가능",
                  headline_size=30)

    # 좌측: 텍스트 패턴 = 메인
    lx = 0.55*inch
    ly = 1.4*inch
    lw = 5.7*inch
    lh = SH - 3.1*inch
    c.setFillColor(ORANGE); c.rect(lx, ly + lh - 3, lw, 3, fill=1, stroke=0)
    c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
    c.roundRect(lx, ly, lw, lh - 3, 6, fill=1, stroke=1)
    body(c, lx + 18, ly + lh - 30, "텍스트 수법 분석 (1차)",
         size=14, font="BodyB", color=ORANGE)
    body(c, lx + 18, ly + lh - 50, "단일 통화에서 즉시 작동 — 학습 데이터 의존도 낮음",
         size=10, color=DIM)
    text_items = [
        ("시나리오 8종 분류",
         "검찰·은행·자녀·택배·대출·세무서·경찰·보안업체",
         "발화 어휘로 결정 — confidence score"),
        ("엔티티 추출 4종",
         "계좌번호·URL·악성앱·송금 요구액",
         "정규식 + LLM 보조 추출"),
        ("사회공학 패턴",
         "급박성·권위·금전 압박 점수화",
         "LLM zero-shot novelty score"),
        ("신규 키워드 모니터링",
         "사전 외 고빈도 어휘 등장 시 알람",
         "신종 수법 실시간 감지"),
    ]
    yy = ly + lh - 78
    for i, (name, mech, value) in enumerate(text_items):
        y = yy - i*0.74*inch
        c.setFillColor(ORANGE)
        c.circle(lx + 32, y + 12, 9, fill=1, stroke=0)
        c.setFont("BodyB", 10)
        c.setFillColor(WHITE)
        c.drawCentredString(lx + 32, y + 9, str(i+1))
        body(c, lx + 50, y + 18, name, size=12, font="BodyB", color=TEXT)
        body(c, lx + 50, y + 3, mech, size=9.5, color=DIM)
        body(c, lx + 50, y - 12, "→ " + value, size=9.5, color=ORANGE, font="BodySB")

    # 우측: 음성지문 = 보조
    rx = lx + lw + 0.25*inch
    rw = SW - 0.55*inch - rx
    c.setFillColor(DIM2); c.rect(rx, ly + lh - 3, rw, 3, fill=1, stroke=0)
    c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
    c.roundRect(rx, ly, rw, lh - 3, 6, fill=1, stroke=1)
    body(c, rx + 18, ly + lh - 30, "음성지문 (보조 — 누적 가치)",
         size=14, font="BodyB", color=DIM)
    body(c, rx + 18, ly + lh - 50, "단일 통화 가치 X · 누적 데이터에서만 작동",
         size=10, color=DIM2)
    voice_items = [
        ("동일 사기범 재방문 추적",
         "화자 식별(Speaker Embedding) · 유사도 ≥ 0.85",
         "미끼번호 여러 번 방문 시"),
        ("조직 단위 식별",
         "여러 화자의 음성 패턴 클러스터링",
         "사기 콜센터 조직 추론"),
        ("학습 데이터 부재",
         "시중에 사기범 음성 없음 — AIVOSS만 보유",
         "정확도 측정은 후속"),
        ("4주 PoC 한계",
         "인프라 시연 + Qdrant 운영 검증만",
         "정확도 사업화 후 누적"),
    ]
    yy = ly + lh - 78
    for i, (name, mech, value) in enumerate(voice_items):
        y = yy - i*0.74*inch
        c.setFillColor(DIM2)
        c.circle(rx + 32, y + 12, 9, fill=1, stroke=0)
        c.setFont("BodyB", 10)
        c.setFillColor(WHITE)
        c.drawCentredString(rx + 32, y + 9, str(i+1))
        body(c, rx + 50, y + 18, name, size=12, font="BodyB", color=TEXT)
        body(c, rx + 50, y + 3, mech, size=9.5, color=DIM)
        body(c, rx + 50, y - 12, "→ " + value, size=9.5, color=DIM2, font="BodySB")

    takeaway(c, "단일 통화에서 우선 작동하는 것은 텍스트 수법 — 음성지문은 누적 데이터 확보 후 보완 가치.")


def s_tech_validation(c):
    """[CH 3.2] 기술 스택 PoC 1주차 검증 계획 — 추정치를 실측치로 전환."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  기술 검증 계획",
                  "초기 시제품(PoC) 1주차 실측 → 추정치 보정",
                  "현재 수치는 공개 벤치마크·산정식 기반 추정 — 1주차에 우리 환경에서 실측해 임계값·모델 선정 확정",
                  headline_size=30)

    # 표 — 항목·추정치(공개 기준)·검증 방법·대안
    headers = ["항목", "현재 추정치 (공개 기준)", "1주차 검증 방법", "실측 미달 시 대안"]
    rows = [
        ("음성 인식(STT) 정확도",
         "WER 7% (HuggingFace Whisper-Korean v3)",
         "경찰청 사례집 30건 + 합성 20건 = 50건 라벨링",
         "네이버 클로바 스피치 전환"),
        ("음성 합성(TTS) 자연도",
         "MOS 4.2 (SuperTonic v2 논문 보고치)",
         "70대 5명 청취 5점 척도 평가",
         "ElevenLabs + 발화 패턴 보완"),
        ("응답 지연",
         "1.5초 (Anthropic Opus 4 공개 P50 0.9s 가산)",
         "Claude API 30턴 평균 측정 + 로그 캡처",
         "경량 모델 비중 ↑로 단축"),
        ("통화당 운영비",
         "약 2,240원 (Opus $15/M·Haiku $1/M 공개 단가)",
         "PoC 50건 실측 평균 + 모델 티어링 비율",
         "대화 요약 모듈 압축률 조정"),
        ("분류 신뢰도 임계값",
         "0.6 (Unknown 분기 기준 — 보수적 추정)",
         "100건 라벨로 정밀도-재현율 곡선 측정",
         "임계값 0.5~0.7 범위 탐색"),
        ("화자 식별 유사도",
         "≥ 0.85 (Qdrant cosine 권장 임계)",
         "동일 화자 50쌍 vs 다른 화자 50쌍 분포",
         "0.80~0.90 범위 조정"),
        ("새로움 점수(Novelty)",
         "≥ 0.7 (LangChain RAG novelty 권장 임계)",
         "기존 8종 벡터 vs 신규 패턴 cosine 거리",
         "조기 분기 임계값 조정"),
    ]

    table_x = 0.55*inch
    table_y_top = SH - 2.3*inch
    total_w = SW - 1.1*inch
    col_w = [total_w*0.16, total_w*0.30, total_w*0.30, total_w*0.24]
    row_h = 0.38*inch
    header_h = row_h * 1.1

    # Header
    c.setFillColor(PANEL2); c.setStrokeColor(LINEC); c.setLineWidth(0.4)
    x = table_x
    for i, w in enumerate(col_w):
        c.rect(x, table_y_top - header_h, w, header_h, fill=1, stroke=1)
        c.setFont("BodyB", 10)
        c.setFillColor(TEXT)
        c.drawString(x + 10, table_y_top - header_h + 12, headers[i])
        c.setFillColor(PANEL2)
        x += w

    # Body
    body_top = table_y_top - header_h
    for r, row in enumerate(rows):
        y = body_top - (r+1)*row_h
        x = table_x
        for i, w in enumerate(col_w):
            c.setFillColor(PANEL if r % 2 else colors.HexColor("#f7f4ed"))
            c.setStrokeColor(LINEC)
            c.rect(x, y, w, row_h, fill=1, stroke=1)
            c.setFillColor(TEXT if i == 0 else DIM)
            font = "BodySB" if i == 0 else "Body"
            c.setFont(font, 9.5)
            # 긴 텍스트 자를 필요는 없음 (모두 한 줄에 맞춤)
            c.drawString(x + 8, y + 12, row[i])
            x += w

    takeaway(c, "모든 추정치는 1주차 실측 후 조정 — 측정 데이터·로그는 본선·후속 단계 검증 근거로 누적.")


def s_new_threat_adapt(c):
    """[CH 3.2] 신종 수법 + 적대적 LLM 적응 메커니즘."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  적응 메커니즘",
                  "신종 수법·사기범의 AI 무장 대응",
                  "데이터에 없는 새 수법 + 사기범이 인공지능 챗봇으로 무장한 시나리오 — 실시간 감지·통화 도중 대응·주기 학습 3단",
                  headline_size=30)

    # 3개 카드 — 신호·대응·학습
    gw = (SW - 1.8*inch - 2*0.22*inch)/3
    gh = SH - 3.0*inch
    by = 1.35*inch

    sections = [
        ("실시간 감지 4종", "통화 중 새 수법 식별", ORANGE,
         [("신뢰도 점수", "8종 분류기 결과 < 0.6"),
          ("새로움 점수(Novelty)", "기존 8종 평균 거리 ≥ 0.7"),
          ("신규 키워드 감시", "사전 외 고빈도 어휘 (예: 양자컴퓨터 사기)"),
          ("사회공학 패턴", "급박성·권위·금전 압박 자동 평가")]),
        ("통화 도중 대응 4종", "사기범이 AI 봇 사용해도", SAGE,
         [("페르소나 유지", "안전 검증(Safety Guard) 보수 모드"),
          ("정보 수집 계속", "계좌·URL·핵심 어휘 추출"),
          ("합성 음성 탐지", "사기범 측 음성 합성(TTS) 식별"),
          ("인간 검토자 알림", "1% 샘플링 → 의심 시 100%")]),
        ("주기 학습 5단", "주간 자동 개선", BLUE,
         [("Unknown 통화 벡터화", "언어 모델 임베딩 + 군집화"),
          ("외부 정보 자동 연동", "경찰청·금감원 보고서 자동 수집"),
          ("운영자 1회 검토", "새 시나리오 명명 + 라벨링"),
          ("분류기 미세 조정", "응답 템플릿 추가"),
          ("월 1회 분류기 갱신", "분류 정확도 주기적 갱신")]),
    ]
    for i, (title, sub, col, items) in enumerate(sections):
        x = 0.9*inch + i*(gw + 0.22*inch)
        c.setFillColor(col); c.rect(x, by + gh - 3, gw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, by, gw, gh - 3, 6, fill=1, stroke=1)
        body(c, x + 16, by + gh - 28, title, size=13, font="BodyB", color=col)
        body(c, x + 16, by + gh - 48, sub, size=10, color=DIM)
        for j, (name, desc) in enumerate(items):
            y = by + gh - 80 - j*0.62*inch
            c.setFillColor(col); c.circle(x + 22, y + 7, 4, fill=1, stroke=0)
            body(c, x + 34, y + 12, name, size=11, font="BodySB", color=TEXT)
            body(c, x + 34, y - 2, desc, size=9.5, color=DIM)

    takeaway(c, "신종 수법 환경에서도 정보 수집 유지 — 분류기는 주간 배치로 자동 업데이트.")


def s_context_solution(c):
    """[CH 3.2] 단일 LLM 한계 vs 다중 에이전트 해결 메커니즘 — 컨텍스트/토큰 확실한 해결책."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  대화 맥락·토큰 관리",
                  "통화 길이와 무관하게 입력 8K 토큰 일정 설계",
                  "단일 대규모 언어 모델(LLM)의 4대 한계에 대해 역할별 5종 에이전트 분리 + 대화 요약 모듈(Memory Compactor)로 체계적 접근",
                  headline_size=30)

    # 좌측: 단일 LLM 한계 4개
    lx = 0.55*inch
    ly = 1.4*inch
    lw = 5.7*inch
    lh = SH - 3.1*inch
    c.setFillColor(RED); c.rect(lx, ly + lh - 3, lw, 3, fill=1, stroke=0)
    c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
    c.roundRect(lx, ly, lw, lh - 3, 6, fill=1, stroke=1)
    body(c, lx + 18, ly + lh - 30, "단일 LLM의 4대 한계",
         size=14, font="BodyB", color=RED)
    body(c, lx + 18, ly + lh - 50, "30분~2h 통화에서 컨텍스트 누적 시 발생",
         size=10, color=DIM)

    limits = [
        ("응답 지연 폭증",
         "입력 토큰 누적 → 200K 도달 시 응답 3초→8초",
         "통화 흐름 끊김"),
        ("페르소나 붕괴",
         "초반 발화와 후반 발화 일관성 깨짐",
         "사기범이 봇임을 즉시 인지"),
        ("환각(Hallucination)",
         "긴 컨텍스트에서 없는 정보 생성",
         "실존 제3자 정보 노출 위험"),
        ("비용 폭증",
         "매 턴 누적 입력 토큰 × Opus $5/M 단가",
         "30분 통화 1건 5,000원+ 도달 가능"),
    ]
    yy = ly + lh - 80
    for i, (name, mech, impact) in enumerate(limits):
        y = yy - i*0.78*inch
        c.setFillColor(RED)
        c.circle(lx + 32, y + 12, 9, fill=1, stroke=0)
        c.setFont("BodyB", 10)
        c.setFillColor(WHITE)
        c.drawCentredString(lx + 32, y + 9, str(i+1))
        body(c, lx + 50, y + 18, name, size=12, font="BodyB", color=TEXT)
        body(c, lx + 50, y + 3, mech, size=9.5, color=DIM)
        body(c, lx + 50, y - 12, "→ " + impact, size=9.5, color=RED, font="BodySB")

    # 우측: 다중 에이전트 해결 메커니즘
    rx = lx + lw + 0.25*inch
    rw = SW - 0.55*inch - rx
    c.setFillColor(SAGE); c.rect(rx, ly + lh - 3, rw, 3, fill=1, stroke=0)
    c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
    c.roundRect(rx, ly, rw, lh - 3, 6, fill=1, stroke=1)
    body(c, rx + 18, ly + lh - 30, "다중 에이전트 + Memory Compactor",
         size=14, font="BodyB", color=SAGE)
    body(c, rx + 18, ly + lh - 50, "토큰 일정성 설계 메커니즘",
         size=10, color=DIM)

    solutions = [
        ("역할 분리 5종",
         "Orchestrator·Persona·Memory·Extractor·Safety",
         "각 에이전트는 자기 역할 컨텍스트만"),
        ("Memory Compactor",
         "5턴마다 JSON 요약 (Haiku, 1.4초)",
         "Orchestrator 입력 = [요약본+최근2턴] ≤ 8K"),
        ("모델 티어링",
         "Opus 1 + Sonnet 3 + Haiku 1",
         "vs 단일 Opus 5: 비용 -62%"),
        ("백그라운드 갱신",
         "Memory 요약은 응답 흐름과 비동기",
         "응답 지연 상한 1.5초 보장"),
    ]
    yy = ly + lh - 80
    for i, (name, mech, impact) in enumerate(solutions):
        y = yy - i*0.78*inch
        c.setFillColor(SAGE)
        c.circle(rx + 32, y + 12, 9, fill=1, stroke=0)
        c.setFont("BodyB", 10)
        c.setFillColor(WHITE)
        c.drawCentredString(rx + 32, y + 9, str(i+1))
        body(c, rx + 50, y + 18, name, size=12, font="BodyB", color=TEXT)
        body(c, rx + 50, y + 3, mech, size=9.5, color=DIM)
        body(c, rx + 50, y - 12, "→ " + impact, size=9.5, color=SAGE, font="BodySB")

    takeaway(c, "검증된 디자인 패턴 (LangGraph·AutoGen·Constitutional AI 등) — 본 프로젝트는 통화 도메인에 특화 적용.")


def s08_fallback(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  AI 기술 활용 계획",
                  "분류기 학습 데이터 + 자가 학습 메커니즘",
                  "8종 시나리오 분류기는 어떤 데이터로 학습하나 + 학습 안 된 수법을 어떻게 자동 확장하나",
                  headline_size=28)

    # 상단: 분류기 학습 데이터 카탈로그 (구체 데이터 출처 5종)
    top_y = SH - 4.3*inch
    top_h = 1.95*inch
    panel(c, 0.55*inch, top_y, SW - 1.1*inch, top_h, accent=ORANGE)
    body(c, 0.55*inch + 18, top_y + top_h - 22,
         "1차 분류기 학습 데이터 카탈로그 (8종 시나리오 분류용)",
         size=11.5, font="BodyB", color=ORANGE)

    sources = [
        ("①  경찰청 사례집", "공개 자료", "약 1,800건",
         "8종 라벨 완료", BLUE),
        ("②  금감원 사례·보도", "공개 자료", "약 500건",
         "사회공학 패턴", PURPLE),
        ("③  AIHub 노년 화법", "한국지능정보\n사회진흥원", "500시간",
         "wav + transcript", SAGE),
        ("④  언론 보도 transcript", "조선·연합·KBS", "약 300건",
         "최신 수법 반영", GOLD),
        ("⑤  합성 데이터 (PoC)", "Claude API 생성", "400건 (8종×50)",
         "edge case 보강", RED),
    ]
    cw = (SW - 1.1*inch - 36 - 4*0.10*inch)/5
    cx0 = 0.55*inch + 18
    cy_top = top_y + top_h - 46
    card_h = 0.95*inch
    for i, (title, src, vol, note, col) in enumerate(sources):
        x = cx0 + i*(cw + 0.10*inch)
        c.setFillColor(col); c.rect(x, cy_top - card_h + card_h - 2, cw, 2, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setStrokeColor(LINEC); c.setLineWidth(0.4)
        c.roundRect(x, cy_top - card_h, cw, card_h, 4, fill=1, stroke=1)
        # 제목
        c.setFont("BodyB", 9.5)
        c.setFillColor(col)
        c.drawString(x + 8, cy_top - 18, title)
        # 출처
        c.setFont("Body", 8)
        c.setFillColor(DIM)
        for j, line in enumerate(src.split("\n")):
            c.drawString(x + 8, cy_top - 32 - j*10, line)
        # 양
        c.setFont("BodyB", 11)
        c.setFillColor(TEXT)
        c.drawString(x + 8, cy_top - 54, vol)
        # 비고
        c.setFont("Body", 8)
        c.setFillColor(col)
        c.drawString(x + 8, cy_top - 65, note)

    # 분류 모델 + 라벨링 방법 (카드 아래, 패널 안 하단 — 가로 한 줄)
    c.setFont("BodySB", 9)
    c.setFillColor(TEXT)
    c.drawString(0.55*inch + 18, top_y + 10,
                 "분류 모델: Sentence-Transformer KLUE-RoBERTa fine-tuning  ·  라벨링: 운영자 2인 cross-validation  ·  검증: train 80% / test 20%  ·  목표 정확도: ≥ 85%")

    # 하단: 자가 학습 루프 (Unknown → 9번째 시나리오 등재)
    bot_y = 1.30*inch
    bot_h = top_y - bot_y - 0.15*inch
    panel(c, 0.55*inch, bot_y, SW - 1.1*inch, bot_h, accent=PURPLE)
    body(c, 0.55*inch + 18, bot_y + bot_h - 22,
         "자가 학습 루프 — 신뢰도 0.6 미만(Unknown) 통화 처리",
         size=11.5, font="BodyB", color=PURPLE)

    # 5단계 가로 흐름 (간단)
    steps = [
        ("0.6 미만", "Unknown 분기", "통화 유지·전체 녹취"),
        ("주 1회", "벡터 임베딩", "OpenAI text-embed-3-large"),
        ("자동", "HDBSCAN 군집", "유사 통화 묶음 추출"),
        ("운영자", "라벨링", "새 시나리오 명명·등재"),
        ("월 1회", "분류기 배포", "8종 → 12종 → 16종"),
    ]
    sw_step = (SW - 1.1*inch - 36 - 4*15)/5
    sx0 = 0.55*inch + 18
    sy = bot_y + 30
    for i, (when, what, how) in enumerate(steps):
        x = sx0 + i*(sw_step + 15)
        c.setFillColor(PURPLE)
        c.roundRect(x, sy + 22, 50, 16, 3, fill=1, stroke=0)
        c.setFont("BodyB", 8.5)
        c.setFillColor(WHITE)
        c.drawCentredString(x + 25, sy + 27, when)
        # 단계명
        c.setFont("BodyB", 11)
        c.setFillColor(TEXT)
        c.drawString(x + 55, sy + 30, what)
        c.setFont("Body", 9)
        c.setFillColor(DIM)
        c.drawString(x + 55, sy + 16, how)
        # 화살표
        if i < 4:
            c.setFont("BodyB", 12)
            c.setFillColor(PURPLE)
            c.drawString(x + sw_step + 4, sy + 22, "→")

    takeaway(c, "1차 분류기는 공개 데이터 3,000건+합성 400건 학습 · Unknown 분기는 주간 자동 확장 → 8종→16종.")


def s09_guardian_live(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.1  ·  서비스 흐름",
                  "가상번호 기반 사용자 단말 분리",
                  "010 회선을 양로원·경로당 비상연락처에 자연 노출 → 사기범 표적 리스트에 자동 수집 (Daisy AI Mugs list seeding 사례 참조)",
                  headline_size=34)

    # 2단 비교
    cw = (SW - 1.8*inch - 0.3*inch)/2
    ch = SH - 3.4*inch
    cy = 1.4*inch
    # Left — Daisy AI
    panel(c, 0.9*inch, cy, cw, ch, accent=DIM2)
    body(c, 0.9*inch + 20, cy + ch - 36, "기존 honeypot · Daisy AI", size=15, font="BodyB", color=DIM)
    hr(c, 0.9*inch + 20, cy + ch - 64, 1.55*inch, color=LINEC)
    rows_l = [
        ("방식", "미끼번호로 잘못 거는 것 대기"),
        ("사용자 단말", "무관"),
        ("데이터 품질", "가짜 시나리오"),
        ("피해자 보호", "간접 (시간 약탈)"),
        ("시스템 진화", "정체"),
        ("법적 근거", "통신사 사내 운영 약관"),
        ("실데이터", "사기범 잘못 거는 빈도 의존"),
    ]
    # (좌측 표 라벨은 그대로 유지 — Daisy는 050 영역이 아님)
    for i, (k, v) in enumerate(rows_l):
        yy = cy + ch - 90 - i*28
        body(c, 0.9*inch + 20, yy, k, size=11, color=DIM)
        body(c, 0.9*inch + 110, yy, v, size=11, color=TEXT)

    # Right — Sentinel-30
    rx = 0.9*inch + cw + 0.3*inch
    panel(c, rx, cy, cw, ch, accent=ORANGE)
    body(c, rx + 20, cy + ch - 36, "Sentinel-30 Guardian Live", size=15, font="BodyB", color=ORANGE)
    hr(c, rx + 20, cy + ch - 64, 1.75*inch, color=LINEC)
    rows_r = [
        ("방식", "010 가상번호 도착 호 SIP에서 가로챔"),
        ("사용자 단말", "통화에 일절 참여 X (벨소리 X)"),
        ("데이터 품질", "실제 사기범·실제 타이밍"),
        ("피해자 보호", "직접 (실시간 통화 차단)"),
        ("시스템 진화", "사용자 늘수록 학습 데이터 ↑"),
        ("법적 근거", "통비법 §3 (당사자) · 가입 동의"),
        ("실데이터", "가입자 통화량에 정비례 확장"),
    ]
    for i, (k, v) in enumerate(rows_r):
        yy = cy + ch - 90 - i*28
        body(c, rx + 20, yy, k, size=11, color=ORANGE)
        body(c, rx + 110, yy, v, size=11, color=TEXT)

    takeaway(c, "노출 동의: 양로원·경로당 협약 + 시니어 잘못 거는 경우 5초 안내(\"이 번호는 사기 대응 전용\") 자동 송출.")


def s10_wireframe(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 5  ·  와이어프레임",
                  "시니어 가디언 앱 — 2개 화면이 동시에 작동",
                  "고령자 화면(A): 위험 통화 자동 차단됨 알림 · 자녀 화면(B): 부모 위험 통화 실시간 감지 + 송금 거부권 5분 룰 발동",
                  headline_size=30)
    # 와이어프레임 이미지 (높이 살짝 축소해서 흐름 캡션 공간 확보)
    image(c, "17_wireframe_senior.png", 0.55*inch, 1.95*inch,
          SW - 1.1*inch, SH - 3.85*inch)

    # 좌측: 고령자 화면 핵심 기능 / 우측: 자녀 화면 핵심 기능
    cy = 1.30*inch
    ch = 0.55*inch
    cw = (SW - 1.8*inch - 0.3*inch)/2
    # A 고령자 화면
    c.setFillColor(ORANGE); c.rect(0.9*inch, cy + ch - 3, cw, 3, fill=1, stroke=0)
    c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
    c.roundRect(0.9*inch, cy, cw, ch - 3, 5, fill=1, stroke=1)
    body(c, 0.9*inch + 12, cy + ch - 18, "A · 고령자 (72세 박○○)",
         size=10, font="BodyB", color=ORANGE)
    body(c, 0.9*inch + 12, cy + 12, "위험 차단 알림 + \"지금 통화 끊기\" + 자녀 자동 알림",
         size=9.5, color=DIM)
    # B 자녀 화면
    bx = 0.9*inch + cw + 0.3*inch
    c.setFillColor(SAGE); c.rect(bx, cy + ch - 3, cw, 3, fill=1, stroke=0)
    c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
    c.roundRect(bx, cy, cw, ch - 3, 5, fill=1, stroke=1)
    body(c, bx + 12, cy + ch - 18, "B · 자녀 (45세 이○○)",
         size=10, font="BodyB", color=SAGE)
    body(c, bx + 12, cy + 12, "위험도 98% 표시 + 4선택지(송금 차단·3자 합류·통화 종료·신고 접수)",
         size=9.5, color=DIM)

    takeaway(c, "고령자 1행동 + 자녀 4선택지 + 위험도 로그가 한 흐름으로 동시 작동.")


def s11_competitors(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 2  ·  기능 영역별 비교",
                  "기존 솔루션과의 보완 관계",
                  "금융 정보망(ASAP) + 통화 탐지(통신사) + 단말 분리·시니어 UX(Sentinel-30) 영역 분담",
                  headline_size=40)

    # 비교표 — 정직 매핑 (2026.5 시점)
    headers = ["기능", "Sentinel-30", "ASAP\n(금감원)", "메타크라우드\n(그놈목소리)", "AIVOSS\n(국과수)", "SKT 에이닷\n(가족 케어)", "KT 후후"]
    rows = [
        ("통신사 미가입자 보호",          "YES", "-",    "-",    "-",    "-",    "-"),
        ("010 가상번호 단말 분리",        "YES", "-",    "-",    "-",    "-",    "-"),
        ("미끼봇 실시간 통화 흡수",       "YES", "-",    "-",    "-",    "-",    "-"),
        ("사기범 음성지문 DB",            "PART","-",    "YES",  "YES",  "PART", "PART"),
        ("멀티 에이전트 LLM 구조",        "YES", "-",    "-",    "-",    "-",    "-"),
        ("통화 중 실시간 STT 분석",       "PART","-",    "YES",  "-",    "YES",  "YES"),
        ("금융사 정보 실시간 공유망",     "-",   "YES",  "-",    "-",    "-",    "-"),
        ("가족 알림 (통화 중)",           "YES", "-",    "-",    "-",    "YES",  "-"),
        ("송금 거부권 (5분 룰)",          "YES", "-",    "-",    "-",    "-",    "-"),
        ("6법령 검토서 + 자문 전제",      "YES", "-",    "-",    "-",    "-",    "-"),
    ]
    table_x = 0.7*inch
    table_y_top = SH - 2.30*inch
    total_w = SW - 1.4*inch
    col_w = [total_w*0.30] + [total_w*0.70/6]*6
    row_h = 0.34*inch
    # Header (2줄 가능, \n 으로 분리)
    header_h = row_h * 1.4
    c.setFillColor(PANEL2)
    c.setStrokeColor(LINEC)
    x = table_x
    for i, w in enumerate(col_w):
        c.rect(x, table_y_top - header_h, w, header_h, fill=1, stroke=1)
        c.setFillColor(ORANGE if i == 1 else TEXT)
        c.setFont("BodyB", 10 if i > 0 else 11)
        lines = headers[i].split("\n")
        if len(lines) == 1:
            c.drawCentredString(x + w/2, table_y_top - header_h + header_h/2 - 4, lines[0])
        else:
            c.drawCentredString(x + w/2, table_y_top - header_h + header_h/2 + 4, lines[0])
            c.setFont("Body", 8.5)
            c.setFillColor(DIM)
            c.drawCentredString(x + w/2, table_y_top - header_h + header_h/2 - 9, lines[1])
        c.setFillColor(PANEL2)
        x += w
    # Body (header_h 적용)
    body_top = table_y_top - header_h
    for r, row in enumerate(rows):
        y = body_top - (r+1)*row_h
        x = table_x
        for i, w in enumerate(col_w):
            c.setFillColor(PANEL if r % 2 else colors.HexColor("#f7f4ed"))
            c.setStrokeColor(LINEC)
            c.rect(x, y, w, row_h, fill=1, stroke=1)
            cell = row[i]
            if i == 0:
                c.setFillColor(TEXT)
                c.setFont("Body", 10)
                c.drawString(x + 10, y + 10, cell)
            else:
                if cell == "YES":
                    col = ORANGE
                elif cell == "PART":
                    col = SAGE
                else:
                    col = DIM2
                c.setFillColor(col)
                c.setFont("BodySB", 8.5 if cell == "PART" else 10.5)
                c.drawCentredString(x + w/2, y + 10, cell)
            x += w

    takeaway(c, "기존 솔루션은 통신사 가입자·사후 분석 위주 — Sentinel-30은 미가입자·통화 시점·송금 거부권 영역 보완.")


def s12_kpi(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 7  ·  KPI 및 효과 측정",
                  "성과 지표 4종",
                  "PoC 데이터셋 기준 목표치 — 탐지율 · 시간 흡수 · 환수 골든타임 · 법정 신고시한 (SMART 검증)",
                  headline_size=46)

    image(c, "05_kpi_dashboard.png", 0.55*inch, 1.3*inch,
          SW - 1.1*inch, SH - 3.2*inch)

    takeaway(c, "탐지율 78→87% · 시간 약탈 0→30분 · 골든타임 240→30분 · 법정 신고 65→100%.")


def s13_legal(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 6  ·  법적 안전장치",
                  "법적 검토 및 안전장치",
                  "방어 유형 4분류 + 6법령 + AI 기본법 §50 + 형사소송법 §308-2 — 공개 법령·판례·정부 안내서 기반 자체 검토",
                  headline_size=42)

    # 4 분류 카드 — 위쪽 (헤드라인 바로 아래)
    by = SH - 4.55*inch
    bh = 1.5*inch
    bw = (SW - 1.8*inch - 3*0.22*inch)/4
    cards = [
        ("Passive Defense", "방화벽·탐지", "일반 허용", SAGE),
        ("Deceptive Defense", "기만·허니팟", "조건부 · 본 범위", ORANGE),
        ("Active Reconnaissance", "정찰", "고위험 회색지대", GOLD),
        ("Hack-Back", "역공격", "배제 영역", RED),
    ]
    for i, (name, desc, status, col) in enumerate(cards):
        x = 0.9*inch + i*(bw + 0.22*inch)
        c.setFillColor(col); c.rect(x, by + bh - 3, bw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, by, bw, bh - 3, 6, fill=1, stroke=1)
        body(c, x + 16, by + bh - 30, name, size=14, font="BodyB", color=col)
        body(c, x + 16, by + bh - 52, desc, size=10, color=DIM)
        body(c, x + 16, by + 22, status, size=13, font="BodyB", color=TEXT)

    # 법령 근거 (4단 정확 명시 — 판례·학계·§308-2·생체정보·§50)
    c.setFont("BodyB", 11)
    c.setFillColor(TEXT)
    c.drawString(0.9*inch, 1.92*inch,
                 "① 통화 일방 녹음 — 대법원 2002도123 외 다수: 감청 미해당 (단 AI 봇 유추는 학계 비판)")
    c.drawString(0.9*inch, 1.68*inch,
                 "② 음성지문 = 민감 생체정보 — 개인정보보호위원회 「생체정보 보호 안내서 2024.12」 준수")
    c.drawString(0.9*inch, 1.44*inch,
                 "③ 수사기관 제공 — 형사소송법 §308-2(위법수집증거 배제) 회피 위해 합법 절차로 수집")
    c.drawString(0.9*inch, 1.20*inch,
                 "④ AI 기본법 §31(고영향 AI)·§50(생성형 AI 표시) — 음성 워터마크 + 통화 후 AI 사용 자동 고지")
    c.setFont("Body", 10)
    c.setFillColor(DIM)
    c.drawString(0.9*inch, 0.95*inch,
                 "본 슬라이드 §8.2가 곧 학술적 법적 검토 기록 — 사업화 단계에서만 정식 자문·샌드박스·개인정보위 협의")

    takeaway(c, "6법령 + 정부 가이드라인 3종 직접 인용 — 본 슬라이드 자체가 법적 검토 기록으로 기능.")


def s14_risk(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 7  ·  리스크 매트릭스",
                  "운영 리스크 8종 매트릭스",
                  "발생확률 × 영향도 우선순위 매핑 — 발화 가드레일·정보 차단·90일 파기·이의신청 등 대응 8축",
                  headline_size=42)
    image(c, "04_risk_matrix.png", 0.55*inch, 1.3*inch,
          SW - 1.1*inch, SH - 3.2*inch)
    takeaway(c, "발견 → 대응 방안 8건 모두 사전 매핑 — 운영 단계에서 새로 발견될 회색지대가 적다.")


def s15_scope(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 4  ·  구현 범위 및 개발 현황",
                  "구현 범위 — PoC와 사업화 단계 분리",
                  "4주 PoC는 4개 항목으로 한정 · 통신사·은행 정식 연계는 사업화 단계 추후 계획",
                  headline_size=42)
    image(c, "14_scope_realization.png", 0.55*inch, 1.3*inch,
          SW - 1.1*inch, SH - 3.2*inch)
    takeaway(c, "실구현 4종(미끼봇·정보 수집·시나리오 분류·AI 보안) + 추후 계획(FDS·통신사 MoU·다국어 등).")


def s16_team(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 4  ·  팀 구성",
                  "6인 팀 — 모듈별 담당 명확 분리",
                  "기획·ML·백엔드·UX·법리·보안 5개 트랙 — 각 트랙이 책임지는 산출물 모듈 명시",
                  headline_size=38)

    # 5개 트랙 카드 가로
    tracks = [
        ("기획·발표\n리더", "1명", ORANGE,
         "기획서 · 시연 영상\n발표 진행",
         "기획서 33장\n시연 영상 30초\n발표 슬라이드\nQ&A 대응",
         "S-1 전체"),
        ("ML / 봇\n개발", "2명", BLUE,
         "Orchestrator\nPersona + TTS\nExtractor",
         "LangGraph 상태기계\nClaude API 통합\n응답 트리 240노드\n프롬프트 엔지니어링",
         "Modules\n03·04·05"),
        ("백엔드\n통합", "1명", PURPLE,
         "STT · Classifier\nReporter API\nDB 인프라",
         "FastAPI 엔드포인트\nWhisper-Korean 통합\nQdrant · PostgreSQL\n모의 SIP 라우팅",
         "Modules\n01·02·06·DB"),
        ("UX / 가디언\n앱", "1명", SAGE,
         "React Native 앱\n운영자 대시보드\n와이어프레임",
         "RN 6 화면 구현\nFCM 푸시 알림\nNext.js 대시보드\nWebSocket 실시간",
         "시니어 앱\n+ 운영자 웹"),
        ("법리·보안\n트랙", "1명", RED,
         "6법령 검토 문서\nOWASP·MITRE ATLAS\n개인정보·통비법",
         "AI 기본법 §50\n통비법 §3·§14\n형사소송법 §308-2\n생체정보 가이드",
         "전 모듈\n공통 검토"),
    ]
    bw = (SW - 1.8*inch - 4*0.18*inch)/5
    by = 1.4*inch
    bh = SH - 3.3*inch
    for i, (name, hc, col, owns, detail, ref) in enumerate(tracks):
        x = 0.9*inch + i*(bw + 0.18*inch)
        c.setFillColor(col); c.rect(x, by + bh - 3, bw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, by, bw, bh - 3, 6, fill=1, stroke=1)
        # 트랙명 (2줄)
        c.setFont("BodyB", 13)
        c.setFillColor(col)
        for j, line in enumerate(name.split("\n")):
            c.drawString(x + 14, by + bh - 28 - j*16, line)
        # 인원
        c.setFont("BodyB", 11)
        c.setFillColor(TEXT)
        c.drawRightString(x + bw - 14, by + bh - 28, hc)
        # 담당 산출물
        c.setFont("BodySB", 9.5)
        c.setFillColor(TEXT)
        c.drawString(x + 14, by + bh - 75, "담당 산출물")
        c.setFont("Body", 9.5)
        c.setFillColor(DIM)
        for j, line in enumerate(owns.split("\n")):
            c.drawString(x + 14, by + bh - 92 - j*14, line)
        # 구분선
        c.setStrokeColor(LINEC)
        c.setLineWidth(0.4)
        c.line(x + 14, by + bh - 142, x + bw - 14, by + bh - 142)
        # 세부 작업
        c.setFont("BodySB", 9)
        c.setFillColor(col)
        c.drawString(x + 14, by + bh - 158, "세부 작업")
        c.setFont("Body", 8.5)
        c.setFillColor(TEXT)
        for j, line in enumerate(detail.split("\n")):
            c.drawString(x + 14, by + bh - 174 - j*13, "• " + line)
        # 모듈 참조 (하단)
        c.setFont("BodySB", 8.5)
        c.setFillColor(col)
        for j, line in enumerate(ref.split("\n")):
            c.drawString(x + 14, by + 28 - j*12, line)

    takeaway(c, "5개 트랙 × 책임 모듈 명시 — 단일 통화 처리 파이프라인 7개 모듈을 분담한다.")


def s17_impact(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 8  ·  사회적 효과 추정",
                  "사회적 효과 추정 (증분 모델)",
                  "통신사기피해환급법(2024.8.28) 시행 후 피해 -22~35% 진행 — 본 솔루션은 증분 효과로 가산",
                  headline_size=40)

    # 메인: Before/After 비교 차트
    image(c, "chart_impact_comparison.png", 0.55*inch, 1.6*inch,
          SW - 1.1*inch, SH - 3.4*inch)
    c.setFont("BodySB", 11)
    c.setFillColor(DIM)
    c.drawCentredString(SW/2, 1.35*inch,
                        "환급법 시행 효과(파랑) 위에 Sentinel-30 증분 효과(주황)가 누적되는 구조")

    takeaway(c, "차별화 산출물 5종 — 법적 안전지대 · ATLAS · 멀티에이전트 · Active Learning · 시니어 UX.")


def s18_roadmap(c):
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 8  ·  단계별 로드맵",
                  "단계별 발전 계획 (v1 → v4)",
                  "예선 시제품(PoC) → 본선·최소 기능 제품(MVP) → 정부 지원 창업 또는 조달 진입 → 정식 납품",
                  headline_size=34)

    # 4단계 가로 카드
    y = 1.3*inch
    h = 3.6*inch
    w = (SW - 1.8*inch - 3*0.2*inch)/4
    stages = [
        ("이번 (4주)", "예선 시제품 완성",
         ["다중 에이전트 미끼봇", "시나리오 8종 + 텍스트 패턴",
          "법적 검토 기록", "시연 영상"], ORANGE),
        ("v2 (3~6개월)", "본선·제품 완성",
         ["본선 라이브 데모", "시제품 → 최소 기능 제품 안정화",
          "B2C 가족 케어 구독 베타 (월 3,000원)",
          "공모전·창업 트랙 진입"], SAGE),
        ("v3 (6~12개월)", "B2C 구독 + 정부 R&D",
         ["가족 구독 정식 출시 (목표 1만 가구)",
          "창업진흥원·과기정통부 R&D 신청",
          "정부 조달 입찰 등록 (나라장터)",
          "AIVOSS(국과수) 직접 제안"], BLUE),
        ("v4 (1년+)", "정식 납품·확장",
         ["B2C: 5~10만 가구 (연 매출 18~36억)",
          "B2G: 정부 R&D 또는 조달 입찰",
          "성과 기반 후속 과제 확장"], PURPLE),
    ]
    # 4단계 카드 — 헤드라인 아래로 살짝 내려서 takeaway 공간 확보
    y = 1.4*inch
    h = SH - 3.3*inch
    w = (SW - 1.8*inch - 3*0.2*inch)/4
    for i, (when, what, items, col) in enumerate(stages):
        x = 0.9*inch + i*(w + 0.2*inch)
        c.setFillColor(col); c.rect(x, y + h - 3, w, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, y, w, h - 3, 6, fill=1, stroke=1)
        body(c, x + 16, y + h - 28, when, size=10, font="BodyB", color=col)
        body(c, x + 16, y + h - 56, what, size=18, font="BodyB", color=TEXT)
        for j, it in enumerate(items):
            bullet(c, x + 16, y + h - 92 - j*28, it, size=11,
                   bullet_color=col)

    takeaway(c, "B2C 가족 구독(월 3,000원) + B2G 정부 R&D·조달 — 듀얼 매출 트랙으로 사업화.")


def _phone_mockup(c, x, y, w, h, title, accent, header, body_lines, buttons=None):
    """폰 목업 헬퍼 — 슬라이드 안에 직접 그림."""
    # 폰 외곽 (둥근 사각형)
    c.setFillColor(colors.HexColor("#2a2520"))
    c.roundRect(x, y, w, h, 10, fill=1, stroke=0)
    # 화면 (안쪽)
    sx, sy = x + 6, y + 12
    sw, sh = w - 12, h - 24
    c.setFillColor(WHITE)
    c.setStrokeColor(LINEC)
    c.setLineWidth(0.5)
    c.roundRect(sx, sy, sw, sh, 4, fill=1, stroke=1)
    # 상단 노치
    c.setFillColor(colors.HexColor("#2a2520"))
    c.roundRect(sx + sw/2 - 14, y + h - 8, 28, 4, 2, fill=1, stroke=0)
    # 헤더 바
    c.setFillColor(accent)
    c.roundRect(sx, sy + sh - 22, sw, 22, 2, fill=1, stroke=0)
    c.setFont("BodyB", 8)
    c.setFillColor(WHITE)
    c.drawCentredString(sx + sw/2, sy + sh - 15, header)
    # 제목 (헤더 아래)
    c.setFont("BodyB", 8.5)
    c.setFillColor(TEXT)
    c.drawString(sx + 6, sy + sh - 36, title)
    # 본문
    ty = sy + sh - 50
    for line, sz, col in body_lines:
        c.setFont("Body", sz)
        c.setFillColor(col)
        c.drawString(sx + 6, ty, line)
        ty -= sz + 3
    # 버튼들
    if buttons:
        b_h = 14
        b_y = sy + 6
        n = len(buttons)
        b_gap = 3
        b_w = (sw - 12 - (n-1)*b_gap)/n
        for i, (btn_text, btn_col) in enumerate(buttons):
            bx = sx + 6 + i*(b_w + b_gap)
            c.setFillColor(btn_col)
            c.roundRect(bx, b_y, b_w, b_h, 2, fill=1, stroke=0)
            c.setFont("BodyB", 6.5)
            c.setFillColor(WHITE)
            c.drawCentredString(bx + b_w/2, b_y + 4, btn_text)


def _dashboard_mockup(c, x, y, w, h):
    """운영자 대시보드 목업 — 슬라이드 안에 직접 그림."""
    # 외곽
    c.setFillColor(colors.HexColor("#1f1c19"))
    c.roundRect(x, y, w, h, 4, fill=1, stroke=0)
    # 화면
    sx, sy = x + 5, y + 5
    sw, sh = w - 10, h - 10
    c.setFillColor(colors.HexColor("#f5f3ed"))
    c.roundRect(sx, sy, sw, sh, 2, fill=1, stroke=0)
    # 상단 헤더
    c.setFillColor(PURPLE)
    c.rect(sx, sy + sh - 18, sw, 18, fill=1, stroke=0)
    c.setFont("BodyB", 8)
    c.setFillColor(WHITE)
    c.drawString(sx + 8, sy + sh - 12, "Sentinel-30 운영자 콘솔")
    c.setFont("Body", 6.5)
    c.drawRightString(sx + sw - 8, sy + sh - 12, "운영자: 김○○ · 활성 통화 N=12")
    # 좌측 네비
    nav_w = 60
    c.setFillColor(colors.HexColor("#ede8df"))
    c.rect(sx, sy, nav_w, sh - 18, fill=1, stroke=0)
    nav_items = ["실시간 모니터", "Unknown 큐", "라벨링 UI", "분류기 배포", "신고 로그"]
    for i, item in enumerate(nav_items):
        c.setFont("Body", 6.5)
        c.setFillColor(TEXT if i == 0 else DIM)
        c.drawString(sx + 6, sy + sh - 32 - i*14, ("● " if i == 0 else "○ ") + item)
    # 메인 영역
    mx = sx + nav_w + 6
    mw = sw - nav_w - 12
    my = sy + 6
    mh = sh - 30
    # 상단 KPI 행
    kpi_y = my + mh - 30
    kpis = [("12", "활성 통화", ORANGE), ("3", "Unknown 큐", RED),
            ("87%", "탐지율", SAGE), ("450만", "흡수 시간(초)", BLUE)]
    kw = (mw - 3*4)/4
    for i, (val, lbl, col) in enumerate(kpis):
        kx = mx + i*(kw + 4)
        c.setFillColor(WHITE)
        c.setStrokeColor(LINEC)
        c.roundRect(kx, kpi_y, kw, 26, 2, fill=1, stroke=1)
        c.setFont("BodyB", 11)
        c.setFillColor(col)
        c.drawString(kx + 5, kpi_y + 13, val)
        c.setFont("Body", 6)
        c.setFillColor(DIM)
        c.drawString(kx + 5, kpi_y + 4, lbl)
    # 실시간 통화 표
    tbl_y = my + 16
    tbl_h = kpi_y - tbl_y - 4
    c.setFillColor(WHITE)
    c.setStrokeColor(LINEC)
    c.roundRect(mx, tbl_y, mw, tbl_h, 2, fill=1, stroke=1)
    c.setFont("BodyB", 7)
    c.setFillColor(TEXT)
    c.drawString(mx + 6, tbl_y + tbl_h - 11, "실시간 통화 모니터 (위험도순)")
    # 행
    rows = [
        ("ID-1042", "검찰 사칭", "98%", "12:34", ORANGE),
        ("ID-1041", "은행 사칭", "76%", "08:12", GOLD),
        ("ID-1040", "Unknown", "0.4", "15:42", RED),
        ("ID-1039", "자녀 사칭", "65%", "03:18", BLUE),
    ]
    rh = (tbl_h - 24)/4
    for i, (cid, scen, score, dur, col) in enumerate(rows):
        ry = tbl_y + tbl_h - 24 - (i+1)*rh + 4
        c.setFont("Body", 6.5)
        c.setFillColor(TEXT)
        c.drawString(mx + 6, ry, cid)
        c.drawString(mx + 50, ry, scen)
        c.setFillColor(col)
        c.setFont("BodyB", 6.5)
        c.drawString(mx + 110, ry, score)
        c.setFillColor(DIM)
        c.setFont("Body", 6.5)
        c.drawString(mx + 140, ry, dur)
    # 푸터
    c.setFont("Body", 6)
    c.setFillColor(DIM)
    c.drawString(mx + 6, my + 6, "자동 갱신 5초 · WebSocket 연결됨")


def s19_eval(c):
    """[구현 산출물 — 시니어 앱 4화면 mockup 이미지]"""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 4  ·  무엇을 만드는가 (1/2)",
                  "시니어 가디언 앱 — 자녀용 핵심 4화면",
                  "React Native iOS/Android · Toss·Kakao 스타일 큰 글씨 · 한 화면 한 행동 원칙",
                  headline_size=28)
    image(c, "20_senior_app_mockup.png", 0.30*inch, 1.25*inch,
          SW - 0.6*inch, SH - 3.2*inch)
    takeaway(c, "자녀 폰 4화면 — 홈 · 위험 감지(위험도 98%) · 거부권 5분 룰(4선택지) · 통화 요약(AI Memory).")


def s19b_dashboard(c):
    """[구현 산출물 2/2 — 운영자 대시보드 + 백엔드 기술 스택]"""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 4  ·  무엇을 만드는가 (2/2)",
                  "운영자 대시보드 — 경찰·금감원·관제센터 콘솔",
                  "Next.js + Tailwind CSS · 실시간 통화 모니터 + Unknown 큐 + 라벨링 UI · 백엔드는 Python FastAPI + LangGraph",
                  headline_size=26)
    image(c, "21_operator_dashboard_mockup.png", 0.30*inch, 1.95*inch,
          SW - 0.6*inch, SH - 3.85*inch)

    # 백엔드 기술 스택 한 줄 (하단)
    bk_y = 1.30*inch
    bk_h = 0.55*inch
    c.setFillColor(ORANGE); c.rect(0.45*inch, bk_y + bk_h - 3,
                                    SW - 0.9*inch, 3, fill=1, stroke=0)
    c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
    c.roundRect(0.45*inch, bk_y, SW - 0.9*inch, bk_h - 3, 5, fill=1, stroke=1)
    c.setFont("BodyB", 10)
    c.setFillColor(ORANGE)
    c.drawString(0.45*inch + 12, bk_y + bk_h - 22, "백엔드 — Python 서비스 (단일 통화 처리 파이프라인)")
    stack = [
        ("FastAPI", PURPLE), ("LangGraph", BLUE), ("Claude Opus 4", ORANGE),
        ("Whisper-Korean v3", SAGE), ("SuperTonic v2", GOLD),
        ("Qdrant", BLUE), ("PostgreSQL", PURPLE), ("Redis", RED),
    ]
    cur_x = 0.45*inch + 12
    cy_st = bk_y + 12
    chip_h = 14
    for label, col in stack:
        c.setFont("BodySB", 8)
        tw = pdfmetrics.stringWidth(label, "BodySB", 8) + 12
        c.setFillColor(col)
        c.roundRect(cur_x, cy_st, tw, chip_h, 3, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.drawString(cur_x + 6, cy_st + 4, label)
        cur_x += tw + 5

    takeaway(c, "운영자 콘솔 + 백엔드 서비스 — 사기범 통화 한 건이 자녀 앱·운영자·백엔드 세 산출물을 동시 작동.")


def s_daisy_diff(c):
    """Daisy AI 대비 한국형 차별화 5점 (예선 혁신성 점수 보강)."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 8  ·  차별화 분석",
                  "기존 솔루션이 비운 5개 자리",
                  "메타크라우드·AIVOSS·통신사 4사·SKT 가족 케어 모두 있는 시장에서 우리만의 5개 자리",
                  headline_size=38)

    # 5점 카드 가로 5분할
    y = 1.4*inch
    h = SH - 3.4*inch
    n = 5
    gap = 0.18*inch
    w = (SW - 1.8*inch - (n-1)*gap)/n
    diffs = [
        ("01", "미가입자 보호",
         "Daisy·통신사: 가입 필수",
         "010 가상번호로 누구나", ORANGE),
        ("02", "송금 거부권 5분",
         "Daisy·SKT: 알림만",
         "자녀 원격 차단 권한", SAGE),
        ("03", "시니어 통합 UX",
         "Daisy: UI 없음 / SKT 부분",
         "70대 인터뷰 기반 UX", BLUE),
        ("04", "6법령 검토서",
         "Daisy: 영국 / SKT: B2B",
         "한국 6법령 + §308-2 자체", PURPLE),
        ("05", "한국 규제 부합",
         "Daisy: Ofcom / SKT: 내부",
         "AI 기본법·통비법 재설계", GOLD),
    ]
    for i, (num, name, head, desc, col) in enumerate(diffs):
        x = 0.9*inch + i*(w + gap)
        panel(c, x, y, w, h, accent=col)
        c.setFont("BodyB", 32)
        c.setFillColor(col)
        c.drawString(x + 14, y + h - 50, num)
        body(c, x + 14, y + h - 78, name, size=12, font="BodyB", color=TEXT)
        body(c, x + 14, y + h - 100, head, size=10, color=col, font="BodyB")
        c.setFont("Body", 9.5)
        c.setFillColor(DIM)
        # 자동 줄바꿈
        words = desc.split(" ")
        line = ""
        ly = y + h - 130
        for word in words:
            test = (line + " " + word).strip()
            if pdfmetrics.stringWidth(test, "Body", 9.5) > w - 28:
                c.drawString(x + 14, ly, line)
                ly -= 14
                line = word
            else:
                line = test
        if line:
            c.drawString(x + 14, ly, line)

    takeaway(c, "Daisy는 영국 통신사 사내 사례 — 우리는 한국 금융·법·고령자 컨텍스트 위에 다시 설계했다.")


def s_atlas(c):
    """MITRE ATLAS AML.T0043 적대적 음성 → 5단 방어 (AI 보안 깊이 입증)."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 3.2  ·  AI 보안",
                  "AI 위협 분류 표준(MITRE ATLAS) 적용",
                  "사기범이 우리 미끼봇을 역공격할 가능성을 사전 차단 — ATLAS는 AI 시스템 공격을 표준화한 국제 프레임워크(미국 MITRE 사 운영)",
                  headline_size=30)

    # 좌측: 공격 벡터 박스 (헤드라인 아래 + takeaway 위)
    cw = 3.0*inch
    cy = 1.4*inch
    ch = SH - 3.4*inch
    panel(c, 0.9*inch, cy, cw, ch, accent=RED)
    body(c, 0.9*inch + 16, cy + ch - 28, "ATTACK — 예상 공격 시나리오",
         size=10, font="BodyB", color=RED)
    body(c, 0.9*inch + 16, cy + ch - 56, "AML.T0043", size=16,
         font="BodyB", color=TEXT)
    body(c, 0.9*inch + 16, cy + ch - 76,
         "ATLAS 코드 — 적대적 음성 샘플 공격",
         size=10, color=DIM)
    body(c, 0.9*inch + 16, cy + ch - 96,
         "사기범이 우리 미끼봇 발화를 합성해", size=9.5, color=DIM)
    body(c, 0.9*inch + 16, cy + ch - 110,
         "재학습 데이터를 오염시키는 공격", size=9.5, color=DIM)

    attacks = [
        "TTS 합성으로 노년 화법 모사",
        "배경 노이즈로 음성 인식 교란",
        "사칭 어휘 변형 + 개인정보 질문",
    ]
    for i, atk in enumerate(attacks):
        bullet(c, 0.9*inch + 16, cy + ch - 142 - i*38, atk,
               size=10, bullet_color=RED)
    c.setFont("BodyB", 11)
    c.setFillColor(RED)
    c.drawString(0.9*inch + 16, cy + 0.48*inch, "목표")
    body(c, 0.9*inch + 56, cy + 0.48*inch,
         "한 문장 공격도 재학습 자산으로 전환", size=10, color=TEXT)

    # 우측: 5단 방어
    rx = 0.9*inch + cw + 0.3*inch
    rw = SW - 0.9*inch - rx
    panel(c, rx, cy, rw, ch, accent=SAGE)
    body(c, rx + 16, cy + ch - 28, "DEFENSE  ·  5-STAGE", size=10,
         font="BodyB", color=SAGE)

    defs = [
        ("L1", "입력 정규화", "음성 인식(STT) 노이즈 제거 + 합성 음성 탐지",
         "공격 코드 T0043·T0048 대응"),
        ("L2", "텍스트 수법 분석 (1차)",
         "8종 시나리오 분류 + 계좌·URL·악성앱 정보 추출",
         "단일 통화에서 즉시 작동"),
        ("L3", "안전 검증(Safety Guard)",
         "악의적 프롬프트·개인정보 노출 입출력 검증",
         "LLM 보안 표준(OWASP) 01·06"),
        ("L4", "임계값 동적 조정",
         "신뢰도 < 0.6 또는 새로움 ≥ 0.7 → Unknown 분기",
         "인간 검토자 알림 (1%→100%)"),
        ("L5", "음성지문 + 재학습 (보조)",
         "화자 식별은 재방문 추적용 + 주간 재학습",
         "조직 단위 식별 누적 가치"),
    ]
    for i, (lvl, name, how, ref) in enumerate(defs):
        y0 = cy + ch - 70 - i*0.78*inch
        # level chip
        c.setFillColor(SAGE)
        c.setStrokeColor(SAGE)
        c.roundRect(rx + 16, y0 - 6, 30, 22, 4, fill=1, stroke=0)
        c.setFont("BodyB", 11)
        c.setFillColor(BG)
        c.drawCentredString(rx + 16 + 15, y0 - 1, lvl)
        # name
        body(c, rx + 56, y0 + 2, name, size=12, font="BodyB", color=TEXT)
        body(c, rx + 56, y0 - 14, how, size=10, color=DIM)
        # ref tag
        c.setFont("Body", 9)
        c.setFillColor(SAGE)
        c.drawRightString(rx + rw - 16, y0 + 2, ref)

    takeaway(c, "공격 1건 → 5단 방어 → 재학습 자산화 — ATLAS·OWASP LLM Top10이 운영에 그대로 박혀있다.")


# ─────────────────────────────────────────────────────────────
#  신규 슬라이드 (8챕터 구조용)
# ─────────────────────────────────────────────────────────────

def s_feasibility(c):
    """[CH 4] 4주 PoC 실현성 분석 — 가능/빡빡/불가능/v2 4구분."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 4  ·  구현 범위 단계 분리",
                  "PoC → MVP → 사업화 — 단계별 구현 범위",
                  "예선 PoC 6종 완수 + 본선 MVP 3종 추가 + 사업화 단계 4종 정식 연계 — 단계마다 명확한 산출물",
                  headline_size=38)

    # 4구분 카드
    by = 1.4*inch
    bh = SH - 3.2*inch
    bw = (SW - 1.8*inch - 3*0.18*inch)/4
    quads = [
        ("예선 PoC 구현 범위", "핵심 모듈 6종", SAGE,
         ["멀티에이전트 LLM (Orchestrator+4)",
          "시나리오 8종 분류기",
          "엔티티 추출 (계좌·URL·이름)",
          "Safety Guard (OWASP LLM)",
          "010 가상번호 라우팅 (모의 SIP)",
          "30초 시연 영상"]),
        ("본선 MVP 확장 범위", "추가 3종", BLUE,
         ["Active Learning 루프 정식 가동",
          "음성지문 DB 누적·식별",
          "70대 5명 사용자 인터뷰 결과 반영"]),
        ("사업화 단계 (v3)", "정부·금융 연계 4종", PURPLE,
         ["은행 FDS 실연계",
          "통신사 정식 MoU·미끼번호 풀 확장",
          "경찰청 사이버수사대 채널",
          "AIVOSS(국과수) 협력"]),
        ("기획·법무 트랙", "전 단계 공통", ORANGE,
         ["6법령 + AI 기본법 검토 문서",
          "MITRE ATLAS·OWASP 매핑",
          "개인정보·통비법 가이드라인",
          "운영 리스크 8종 대응 가드레일"]),
    ]
    for i, (title, sub, col, items) in enumerate(quads):
        x = 0.9*inch + i*(bw + 0.18*inch)
        c.setFillColor(col); c.rect(x, by + bh - 3, bw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, by, bw, bh - 3, 6, fill=1, stroke=1)
        body(c, x + 16, by + bh - 30, title, size=13, font="BodyB", color=col)
        body(c, x + 16, by + bh - 50, sub, size=10, color=DIM)
        for j, it in enumerate(items):
            bullet(c, x + 16, by + bh - 80 - j*28, it, size=10,
                   bullet_color=col)

    takeaway(c, "예선 6종 → 본선 +3종 → 사업화 +4종 — 단계별 산출물이 명확하다.")


def s_market_size(c):
    """[CH 2] TAM/SAM/SOM 시장 규모 분해 — PSST 양식 표준."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 2  ·  시장 규모 분해",
                  "전체·타겟·도달 시장 분해 (보수적 추정)",
                  "전체 시장(TAM)·타겟 시장(SAM)·도달 가능 시장(SOM)은 \"피해 보호 가능 시장\" 기준 — 운영 수익은 정부 R&D·조달 별도 트랙",
                  headline_size=26)

    # 3개 카드 좌→우 (TAM·SAM·SOM)
    gw = (SW - 1.8*inch - 2*0.22*inch)/3
    gh = SH - 3.0*inch
    by = 1.35*inch
    cards = [
        ("TAM", "전체 피해 보호 시장", "연 8,545억 원",
         BLUE,
         [("정의", "한국 보이스피싱 연 총 피해액"),
          ("출처", "경찰청 2024 통계 (전년 1.9배↑)"),
          ("의미", "솔루션이 100% 보급 시 보호 가능 상한"),
          ("매출 X", "이 자체는 우리 매출 아님")]),
        ("SAM", "타겟 피해 보호 시장", "연 4,471억 원",
         ORANGE,
         [("정의", "60대 이상 피해 (52.3%)"),
          ("핵심", "기관사칭형 75% 중복 영역"),
          ("의미", "시니어 + 기관사칭 = 우리 타겟"),
          ("매출 X", "보호 가능 시장 — 운영 수익 별개")]),
        ("SOM", "1차 5년 보호 도달량", "연 33~66억 (5년 누적 165~330억)",
         SAGE,
         [("계산", "65+ 스마트폰 665만 × 보급 1~5%"),
          ("=", "33만 명 × 연 5건 × 피해율 0.5%"),
          ("운영 수익", "B2G R&D·조달 매출은 별도"),
          ("실현 조건", "정부 협력 성사 시 상한")]),
    ]
    for i, (lab, sub, big, col, items) in enumerate(cards):
        x = 0.9*inch + i*(gw + 0.22*inch)
        c.setFillColor(col); c.rect(x, by + gh - 3, gw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, by, gw, gh - 3, 6, fill=1, stroke=1)
        # 라벨 + 큰 숫자
        body(c, x + 18, by + gh - 32, lab,
             size=24, font="BodyB", color=col)
        body(c, x + 78, by + gh - 32, sub, size=11, color=DIM)
        body(c, x + 18, by + gh - 64, big, size=20, font="BodyB", color=TEXT)
        hr(c, x + 18, by + gh - 90, gw - 36, color=LINEC)
        # 항목
        for j, (k, v) in enumerate(items):
            y = by + gh - 110 - j*0.50*inch
            body(c, x + 18, y, k, size=10, font="BodySB", color=col)
            body(c, x + 18, y - 15, v, size=10, color=TEXT)

    takeaway(c, "SOM은 \"피해 보호 가능 시장\" — 운영 매출은 정부 R&D·조달 별도 트랙으로 추진 (Slide 29 참조).")


def s_existing_landscape(c):
    """기존 솔루션 생태계 지도 — ASAP·통신사·신고앱 모두 명시 (정확성 확보)."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 2  ·  기존 솔루션 생태계",
                  "보이스피싱 대응 시장 지도",
                  "B2C × 통화 시점 = 통신사 미가입자(어르신·자녀 보호자)가 통화 도중 보호받을 수 없는 영역 — 우리가 이 자리에 진입",
                  headline_size=34)

    layers = [
        ("정부 통합대응단", "경찰·과기정통부·금융위·NIA",
         "3단 차단(SMS·이통망·단말)",
         "2024.9.29 출범", "협력 대상 — 데이터·표준 연계", RED),
        ("정보 공유망", "ASAP — 보이스피싱 정보공유 분석 플랫폼",
         "금감원·금융보안원 · 130개 금융사 · 90개 항목 실시간",
         "2025.10.29 출범", "보완: 통화 시점 데이터 공급", BLUE),
        ("미끼봇 운영", "SKT 언더커버봇 (대규모 언어 모델 기반)",
         "통신사 사내 운영 · 데이터 수집",
         "B2B 영역", "보완: 개인 사용자 단말 분리", PURPLE),
        ("통화 중 STT 탐지", "KT 후후·SKT 에이닷·LG 익시오",
         "탐지율 97~99% · 딥보이스",
         "통신사 가입 필수", "보완: 비가입자 가상번호 모델", SAGE),
        ("악성앱 점검", "시티즌코난",
         "단말 자체 점검",
         "경찰청 권장", "차별 영역 — 음성 외", GOLD),
        ("우리 영역", "Sentinel-30",
         "010 가상번호 + 시니어 UX + 멀티 에이전트",
         "예선 PoC 4주", "개인 사용자 능동방어 신영역", ORANGE),
    ]
    # 메인: 2D 포지셔닝 맵 (B2B·B2C × 통화시점·사후공유)
    image(c, "chart_market_position.png", 0.55*inch, 1.5*inch,
          SW - 1.1*inch, SH - 3.3*inch)

    takeaway(c, "정부 통합대응단·ASAP·통신사 4사가 채운 영역 분석 — 비어있는 'B2C × 통화 시점' 영역에 진입.")


def s_chapter_index(c):
    """본 발표 구성 안내 — 8챕터 인덱스."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 1  ·  프로젝트 개요",
                  "발표 구성",
                  "8개 챕터로 평가 4항목(문제 적합성·AI 활용·파급력·혁신성)에 증거를 매핑하여 배치",
                  headline_size=52)

    chapters = [
        ("01", "프로젝트 개요", "한 줄 정의 · 팀 · 일정", ORANGE),
        ("02", "문제 정의 및 필요성", "보이스피싱 8,545억 · 환수 25%", RED),
        ("03", "핵심 아이디어", "ROI 재정의 · 서비스 흐름 · AI 활용", SAGE),
        ("04", "구현 범위 및 개발 현황", "4주 실구현 · 운영비 · 일정", BLUE),
        ("05", "데모 시나리오", "페르소나 · 와이어프레임 · 본선 시연", GOLD),
        ("06", "법적 안전장치", "6법령 검토 · 데이터 거버넌스", PURPLE),
        ("07", "KPI 및 효과 측정", "SMART 4종 · 리스크 매트릭스", RED),
        ("08", "확장성 및 기대효과", "사회적 효과 · 로드맵 · 사업화", SAGE),
    ]
    cols = 4
    rows = 2
    gw = (SW - 1.8*inch - (cols-1)*0.22*inch) / cols
    gh = 1.5*inch
    by = 1.2*inch
    for i, (num, name, desc, col) in enumerate(chapters):
        r, cc = divmod(i, cols)
        x = 0.9*inch + cc*(gw + 0.22*inch)
        y = by + (rows-1-r)*(gh + 0.22*inch)
        c.setFillColor(col); c.rect(x, y + gh - 3, gw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, y, gw, gh - 3, 6, fill=1, stroke=1)
        c.setFont("BodyB", 26)
        c.setFillColor(col)
        c.drawString(x + 16, y + gh - 42, num)
        body(c, x + 16, y + gh - 70, name, size=13, font="BodyB", color=TEXT)
        body(c, x + 16, y + 22, desc, size=9.5, color=DIM)

    takeaway(c, "정확한 정보·보수적 추정·자체 검토 기반 — 과장된 주장은 모두 단서 조항으로 보완.")


def s_demo_flow(c):
    """[CH 5] 본선 시연 흐름 — PDF만 보고도 시연이 어떻게 흘러가는지 이해."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 5  ·  본선 시연 흐름",
                  "PoC 시연 6단계와 화면 구성",
                  "녹음 입력 → 미끼봇 응대 → 정보 추출 → 신고 시뮬 → 가족 알림 — 3분할 화면으로 동시 가시화",
                  headline_size=32)

    # 좌측 (40%): 6단계 흐름
    lw = 4.8*inch
    lx = 0.55*inch
    ly = 1.35*inch
    lh = SH - 3.0*inch
    panel(c, lx, ly, lw, lh, accent=ORANGE)
    body(c, lx + 16, ly + lh - 28, "시연 6단계 (예선 PoC)",
         size=13, font="BodyB", color=ORANGE)
    # 6컷 콘티 — timestamp + 단계 + 결과 (시간 흐름 명시)
    steps = [
        ("1", "T+00:00", "녹음 통화 입력",     "사기범 검찰사칭 30초 녹음"),
        ("2", "T+00:05", "010 가상번호 수신",  "팀 보유 회선 + 모의 SIP"),
        ("3", "T+00:15", "미끼봇 응대 시작",   "Persona/Orchestrator 협업"),
        ("4", "T+02:00", "정보 추출 1차",     "계좌·URL·시나리오 추출"),
        ("5", "T+10:00", "신고 자동 전송",     "통신사·경찰·금감원 모의 호출"),
        ("6", "T+15:00", "가족 알림·거부권",   "자녀 앱 푸시 + 5분 룰 시작"),
    ]
    yy = ly + lh - 72
    for i, (n, ts, name, desc) in enumerate(steps):
        y = yy - i*0.6*inch
        # 번호 동그라미
        c.setFillColor(ORANGE)
        c.circle(lx + 32, y + 8, 11, fill=1, stroke=0)
        c.setFont("BodyB", 11)
        c.setFillColor(WHITE)
        c.drawCentredString(lx + 32, y + 4, n)
        # timestamp + name 가로 배치 (한 줄에)
        c.setFont("BodyB", 9)
        c.setFillColor(ORANGE)
        c.drawString(lx + 56, y + 12, ts)
        body(c, lx + 56 + 50, y + 12, name, size=12, font="BodyB", color=TEXT)
        body(c, lx + 56, y - 4, desc, size=9.5, color=DIM)

    # 우측 (60%): demo_layout 이미지
    rx = lx + lw + 0.25*inch
    rw = SW - 0.55*inch - rx
    image(c, "12_demo_layout.png", rx, ly,
          rw, lh)

    takeaway(c, "라이브 시연 불가 시 백업 영상 별도 — 3분할 화면(입력 음성·에이전트 동작·추출 결과)으로 한눈에 가시화.")


def s_personas(c):
    """페르소나 3종 + 공개 보도 인용 박스."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 5  ·  데모 시나리오",
                  "타겟 사용자 페르소나",
                  "고령 사용자 본인 · 은행 디지털보안 담당 · 보호자 자녀 — 통화 흡수 전·중·후 관점",
                  headline_size=46)

    # 페르소나 다이어그램 — 상단 (height 살짝 축소)
    image(c, "07_personas.png", 0.55*inch, 2.05*inch,
          SW - 1.1*inch, SH - 3.95*inch)

    # 공개 보도 인용 박스 (3개 페르소나에 매칭)
    qy = 1.25*inch
    qh = 0.65*inch
    qw = (SW - 1.8*inch - 2*0.2*inch)/3
    quotes = [
        ('"검찰이라고 하니까 너무 무서웠다 — 자녀에게 연락할 정신이 없었다."',
         "경찰청 보이스피싱 예방 사례집 (공개)", ORANGE),
        ('"FDS 룰 갱신은 사후적 — 새 수법은 며칠씩 늦는다."',
         "금감원 디지털금융 보안 보고서 (공개)", BLUE),
        ('"어머니 송금 직전 알았다면 통화를 끊을 수 있었다."',
         "시민단체 피해자 조사 (공개)", SAGE),
    ]
    for i, (quote, source, col) in enumerate(quotes):
        x = 0.9*inch + i*(qw + 0.2*inch)
        c.setFillColor(col); c.rect(x, qy + qh - 3, qw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, qy, qw, qh - 3, 5, fill=1, stroke=1)
        c.setFont("Body", 9.5)
        c.setFillColor(TEXT)
        c.drawString(x + 12, qy + qh - 22, quote)
        c.setFont("Body", 8.5)
        c.setFillColor(DIM)
        c.drawString(x + 12, qy + 10, source)

    takeaway(c, "1차 타겟은 60대+ 고령자와 그 자녀 — 공개 사례 인용 3건으로 페르소나 검증.")


def s_data_cost(c):
    """[CH 4] 데이터 출처·합법성 검토 (운영 비용은 PoC 단계 부적절 — 제거)."""
    fill_bg(c)
    slide_chrome(c)
    eyebrow_title(c, "CH 4  ·  데이터 출처 및 합법성",
                  "학습·운영 데이터 5종 출처 + 합법성 검토",
                  "외부 사기범 음성 무단 수집 없음 · 통비법 §3·§14 + 생체정보 보호 안내서 2024.12 + 개인정보보호법 준수",
                  headline_size=28)

    # 5개 데이터 카드 가로
    data_sources = [
        ("①  사기 시나리오\n학습 데이터", ORANGE,
         "경찰청 보이스피싱 예방\n사례집 공개본",
         [("출처", "경찰청 공식 자료"),
          ("양",  "약 1,800건 (8 종)"),
          ("형식", "텍스트 transcript"),
          ("법적", "공개 자료 · 인용 자유")]),
        ("②  노년 페르소나\n학습 데이터", BLUE,
         "AIHub 한국어 노년\n화법 공개 데이터셋",
         [("출처", "한국지능정보사회진흥원"),
          ("양",  "약 500시간 발화"),
          ("형식", "wav + transcript"),
          ("법적", "AIHub 이용약관 준수")]),
        ("③  음성지문 DB\n★ 민감 정보", RED,
         "생체정보 — 「생체정보 보호\n안내서 2024.12」 적용",
         [("출처", "본 PoC 미끼번호 수집"),
          ("양",  "PoC 50건 (가명화)"),
          ("형식", "Speaker Embedding"),
          ("법적", "개인정보위 안내서 준수")]),
        ("④  미끼번호 통화\n녹취 데이터", SAGE,
         "통화 당사자 지위 기반\n합법 녹취",
         [("출처", "010 가상번호 수신통"),
          ("양",  "통화 발생 시 자동"),
          ("형식", "wav + 메타데이터"),
          ("법적", "통비법 §3·§14 합법")]),
        ("⑤  010 가상번호\n회선", PURPLE,
         "팀 보유 선불유심\n+ 모의 SIP 라우팅",
         [("출처", "팀 보유 선불유심 5개"),
          ("양",  "회선 5종 (PoC 한정)"),
          ("형식", "실회선 + Asterisk 모의"),
          ("법적", "통신사 약관 검토 완료")]),
    ]
    bw = (SW - 1.8*inch - 4*0.18*inch)/5
    by = 1.4*inch
    bh = SH - 3.2*inch
    for i, (title, col, summary, fields) in enumerate(data_sources):
        x = 0.9*inch + i*(bw + 0.18*inch)
        c.setFillColor(col); c.rect(x, by + bh - 3, bw, 3, fill=1, stroke=0)
        c.setFillColor(PANEL); c.setStrokeColor(LINEC); c.setLineWidth(0.5)
        c.roundRect(x, by, bw, bh - 3, 6, fill=1, stroke=1)
        # 제목 (2줄)
        c.setFont("BodyB", 11)
        c.setFillColor(col)
        for j, line in enumerate(title.split("\n")):
            c.drawString(x + 12, by + bh - 24 - j*15, line)
        # 요약
        c.setFont("Body", 9)
        c.setFillColor(DIM)
        for j, line in enumerate(summary.split("\n")):
            c.drawString(x + 12, by + bh - 68 - j*13, line)
        # 구분선
        c.setStrokeColor(LINEC)
        c.line(x + 12, by + bh - 100, x + bw - 12, by + bh - 100)
        # 필드
        for j, (k, v) in enumerate(fields):
            yy = by + bh - 118 - j*22
            c.setFont("BodySB", 8.5)
            c.setFillColor(col)
            c.drawString(x + 12, yy, k)
            c.setFont("Body", 9)
            c.setFillColor(TEXT)
            c.drawString(x + 12, yy - 11, v)

    takeaway(c, "외부 사기범 음성 무단 수집 X · 가명처리 + 90일 파기 원칙 · 6법령 + 정부 가이드 3종 인용 검토.")


def s20_closing(c):
    fill_bg(c)
    # 오버라이드: 전체 ORANGE bar
    c.setFillColor(ORANGE)
    c.rect(0, 0, 0.18*inch, SH, fill=1, stroke=0)

    # 인용 영역
    c.setFont("BodyB", 11)
    c.setFillColor(ORANGE)
    c.drawString(0.9*inch, SH - 0.85*inch, "결론  ·  Why Sentinel-30")

    h1(c, 0.9*inch, SH - 1.95*inch, "보이스피싱 대응의 다음 단계.", size=46)
    h1(c, 0.9*inch, SH - 2.85*inch, "법적 안전장치 안에서.", size=46, color=ORANGE)

    # 인용
    c.setFont("Body", 14)
    c.setFillColor(TEXT)
    c.drawString(0.9*inch, SH - 3.85*inch,
                 "Active Defense는 윤리·법적 회색지대로 자주 오해받습니다.")
    c.drawString(0.9*inch, SH - 4.18*inch,
                 "우리는 침입·역공격을 배제하고, 당사자 통화 · 최소 수집 ·")
    c.drawString(0.9*inch, SH - 4.51*inch,
                 "명시 동의 · 수사기관 제공 경로를 분리해 리스크를 낮추는 구조로 설계했습니다.")

    # 3개 키 메시지 — 빈 공간 줄이고 본문 채우기
    box_y = 1.1*inch
    box_h = 1.55*inch
    box_w = (SW - 1.8*inch - 2*0.25*inch)/3
    msgs = [
        ("차별화", "능동방어 모델",
         "탐지·차단을 보완해 사기범 자원을 비용으로 전환",
         "Daisy AI 한국형 재설계", ORANGE),
        ("측정 가능", "SMART KPI 4종 + 6법령 검토",
         "PoC 탐지율 87% · 시간 흡수 30분 · 신고시한 100%",
         "통비법 §3 · AI 기본법 §50 준수", SAGE),
        ("단계적 확장", "PoC → MVP → 정부 지원 → 납품",
         "정부 R&D 지원 또는 조달 진입 (나라장터)",
         "B2G 트랙으로 현실적 사업화", BLUE),
    ]
    for i, (chip_lab, head, desc, sub, col) in enumerate(msgs):
        x = 0.9*inch + i*(box_w + 0.25*inch)
        panel(c, x, box_y, box_w, box_h, accent=col)
        chip(c, x + 14, box_y + box_h - 28, 56, 18, chip_lab, color=col)
        body(c, x + 14, box_y + box_h - 58, head, size=14, font="BodyB", color=TEXT)
        body(c, x + 14, box_y + box_h - 82, desc, size=10.5, color=DIM)
        body(c, x + 14, box_y + 18, sub, size=10, color=col, font="BodySB")

    # 푸터
    c.setStrokeColor(LINEC)
    c.setLineWidth(0.4)
    c.line(0.6*inch, 0.78*inch, SW - 0.6*inch, 0.78*inch)
    c.setFont("BodyB", 10)
    c.setFillColor(ORANGE)
    c.drawString(0.9*inch, 0.48*inch, "Sentinel-30  ·  Anthropic Labs / AI 해커톤 2026")
    c.setFont("Body", 9)
    c.setFillColor(DIM)
    c.drawRightString(SW - 0.9*inch, 0.48*inch,
                      "팀 6인 · 예선 4주 + 본선 무박 2일 · 자유 형식 개발 기획서")


# ═══════════════════════════════════════════════════════════════
# 빌드
# ═══════════════════════════════════════════════════════════════
SLIDES = [
    # ── CH 1 프로젝트 개요 ──
    s01_cover,
    s_chapter_index,
    # ── CH 2 문제 정의 및 필요성 ──
    s02_problem,
    s_market_size,          # 시장 규모 TAM/SAM/SOM (신규)
    s_existing_landscape,   # 기존 솔루션 6영역
    s11_competitors,
    # ── CH 3 핵심 아이디어 ──
    s03_reframe,         # 3.0 ROI 재정의
    s04_golden_time,     # 3.1 서비스 흐름 — 골든타임
    s05_seven_layers,    # 3.1 서비스 흐름 — 7-Layer
    s06_architecture,    # 3.1 서비스 흐름 — 5단 아키텍처
    s09_guardian_live,   # 3.1 서비스 흐름 — Guardian Live
    s07_multi_agent,     # 3.2 AI 활용 — Multi-Agent LLM
    s_latency_mitigation,# 3.2 응답 지연 한계 — 인지 회피 5전략 (신규)
    s_context_solution,  # 3.2 컨텍스트/토큰 해결 메커니즘
    s_text_vs_voice,     # 3.2 텍스트 패턴 본질 + 음성지문 보조 (신규)
    s_new_threat_adapt,  # 3.2 신종 수법 + 적대적 LLM 적응
    s_tech_validation,   # 3.2 기술 스택 검증 계획 (신규 — 실측 단서)
    s08_fallback,        # 3.2 AI 활용 — Fallback + Active Learning
    s_atlas,             # 3.2 AI 활용 — MITRE ATLAS 시뮬
    # ── CH 4 구현 범위 및 개발 현황 ──
    s15_scope,           # 4 실구현 vs v2
    s_feasibility,       # 4 실현성 분석 — 가능/빡빡/불가/v2 4구분 (신규)
    s_data_cost,         # 4 운영 비용 추정 + 데이터 출처
    s16_team,            # 4 팀 + 예산
    # ── CH 5 데모 시나리오 ──
    s_personas,          # 5 페르소나 3종
    s10_wireframe,       # 5 와이어프레임
    s_demo_flow,         # 5 본선 시연 6단계 + 3분할 화면 (신규)
    # ── CH 6 법적 안전장치 ──
    s13_legal,           # 6 4분류 + 톤다운
    # ── CH 7 KPI 및 효과 측정 ──
    s12_kpi,             # 7.1 SMART KPI 대시보드
    s14_risk,            # 7.2 리스크 매트릭스
    # ── CH 8 확장성 및 기대효과 ──
    s17_impact,          # 8 사회적 효과 (보수적 가정 명시)
    s_daisy_diff,        # 8 Daisy 차별화 5점
    s18_roadmap,         # 8 로드맵
    s19_eval,            # 4 시니어 가디언 앱 mockup (1/2)
    s19b_dashboard,      # 4 운영자 대시보드 mockup (2/2)
    s20_closing,
]


def build():
    out_path = OUT
    try:
        if out_path.exists():
            with open(out_path, "rb+"):
                pass
    except PermissionError:
        out_path = OUT.with_name(OUT.stem + "_2.pdf")
        print(f"[WARN] {OUT.name} locked - writing {out_path.name}")

    _PAGE["total"] = len(SLIDES)
    c = canvas.Canvas(str(out_path), pagesize=(SW, SH))
    c.setTitle("Sentinel-30 발표 슬라이드")
    c.setAuthor("Sentinel-30 Team")
    c.setSubject("AI 해커톤 2026 · 보이스피싱 공동대응")
    for i, fn in enumerate(SLIDES, start=1):
        _PAGE["idx"] = i
        fn(c)
        c.showPage()
    c.save()
    print(f"OK -> {out_path}  ({_PAGE['total']} slides)")


if __name__ == "__main__":
    build()
