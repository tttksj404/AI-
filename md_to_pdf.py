"""Markdown -> PDF (Korean-safe, image embed, cover page)."""
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    Flowable,
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(r"C:\Users\SSAFY\Desktop\AI해커톤")
SRC = ROOT / "기획서_Sentinel30.md"
OUT = ROOT / "기획서_Sentinel30_v2.pdf"

pdfmetrics.registerFont(TTFont("Malgun", r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBold", r"C:\Windows\Fonts\malgunbd.ttf"))

styles = getSampleStyleSheet()
# Claude Design official palette (Anthropic Labs)
CREAM = colors.HexColor("#faf9f5")   # Light
TAN = colors.HexColor("#e8e6dc")     # Light Gray
WARM = colors.HexColor("#f1efe6")    # tint
INK = colors.HexColor("#141413")     # Dark
SLATE = colors.HexColor("#5a5853")   # secondary text (darker than mid-gray for readability)
MID = colors.HexColor("#b0aea5")     # Mid Gray
ORANGE = colors.HexColor("#d97757")  # primary accent
BURNT = colors.HexColor("#c4623f")   # darker accent
RUST = colors.HexColor("#a04a2a")    # deepest accent
GOLD = colors.HexColor("#d97757")    # alias
SAGE = colors.HexColor("#788c5d")    # tertiary green
DUSK = colors.HexColor("#6a9bcc")    # secondary blue
MAUVE = colors.HexColor("#6a9bcc")   # alias to blue
LINE = colors.HexColor("#e8e6dc")    # divider
# Back-compat aliases used elsewhere
NAVY = INK
BLUE = BURNT
GRAY = SLATE
LGRAY = LINE

BODY = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Malgun", fontSize=10.5,
    leading=16, alignment=TA_LEFT, spaceAfter=6, textColor=INK,
)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="MalgunBold", fontSize=22,
    leading=28, spaceBefore=18, spaceAfter=12, textColor=BURNT,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="MalgunBold", fontSize=15,
    leading=20, spaceBefore=14, spaceAfter=8, textColor=ORANGE,
    keepWithNext=1,
)
H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"], fontName="MalgunBold", fontSize=12.5,
    leading=17, spaceBefore=10, spaceAfter=6, textColor=INK,
    keepWithNext=1,
)
H4 = ParagraphStyle(
    "H4", parent=styles["Heading4"], fontName="MalgunBold", fontSize=11.5,
    leading=15, spaceBefore=8, spaceAfter=4, textColor=SLATE,
    keepWithNext=1,
)
QUOTE = ParagraphStyle(
    "Quote", parent=BODY, fontName="Malgun", fontSize=11, leading=17,
    leftIndent=14, textColor=INK,
    backColor=WARM,
    borderColor=ORANGE, borderWidth=0, borderPadding=10,
    spaceBefore=6, spaceAfter=8,
)
CAPTION = ParagraphStyle(
    "Cap", parent=BODY, fontName="Malgun", fontSize=9.5, leading=12,
    alignment=TA_CENTER, textColor=SLATE, spaceBefore=2, spaceAfter=10,
)
CODE = ParagraphStyle(
    "Code", parent=styles["Code"], fontName="Courier", fontSize=8.8,
    leading=11.5, textColor=INK,
    backColor=TAN, leftIndent=6, rightIndent=6,
    borderColor=LINE, borderWidth=0.5, borderPadding=6,
    spaceBefore=4, spaceAfter=6,
)
# Code block style for content containing Hangul (Courier has no Korean glyphs).
CODE_KO = ParagraphStyle(
    "CodeKO", parent=styles["Code"], fontName="Malgun", fontSize=9.5,
    leading=14, textColor=INK,
    backColor=TAN, leftIndent=8, rightIndent=8,
    borderColor=LINE, borderWidth=0.5, borderPadding=8,
    spaceBefore=4, spaceAfter=6,
)
CALLOUT_TITLE = ParagraphStyle(
    "CalloutTitle", parent=BODY, fontName="MalgunBold", fontSize=10,
    leading=14, textColor=ORANGE, spaceAfter=2,
)
CALLOUT_BODY = ParagraphStyle(
    "CalloutBody", parent=BODY, fontName="Malgun", fontSize=10.5,
    leading=16, textColor=INK, spaceAfter=0,
)
PULLQUOTE = ParagraphStyle(
    "PullQuote", parent=BODY, fontName="MalgunBold", fontSize=14,
    leading=22, textColor=INK, alignment=TA_LEFT,
    spaceBefore=10, spaceAfter=10,
)
STAT_BIG = ParagraphStyle(
    "StatBig", parent=BODY, fontName="MalgunBold", fontSize=26,
    leading=30, textColor=ORANGE, spaceAfter=0,
)
STAT_LABEL = ParagraphStyle(
    "StatLabel", parent=BODY, fontName="Malgun", fontSize=9,
    leading=12, textColor=SLATE, spaceAfter=0,
)
TLDR_LABEL = ParagraphStyle(
    "TldrLabel", parent=BODY, fontName="MalgunBold", fontSize=9,
    leading=11, textColor=colors.white, spaceAfter=2, alignment=TA_LEFT,
)
TLDR_BODY = ParagraphStyle(
    "TldrBody", parent=BODY, fontName="MalgunBold", fontSize=11.5,
    leading=17, textColor=INK, spaceAfter=0,
)
CODEHEAD_FILE = ParagraphStyle(
    "CodeHeadFile", parent=BODY, fontName="Courier", fontSize=9,
    leading=12, textColor=ORANGE, spaceAfter=2,
)
CODEHEAD_DESC = ParagraphStyle(
    "CodeHeadDesc", parent=BODY, fontName="Malgun", fontSize=10,
    leading=14, textColor=INK, spaceAfter=0,
)
WARN_LABEL = ParagraphStyle(
    "WarnLabel", parent=BODY, fontName="MalgunBold", fontSize=9,
    leading=11, textColor=colors.white, spaceAfter=2,
)
WARN_BODY = ParagraphStyle(
    "WarnBody", parent=BODY, fontName="Malgun", fontSize=10,
    leading=14, textColor=INK, spaceAfter=0,
)
GRID_LABEL = ParagraphStyle(
    "GridLabel", parent=BODY, fontName="MalgunBold", fontSize=8.5,
    leading=10, textColor=ORANGE, spaceAfter=2,
)
GRID_VALUE = ParagraphStyle(
    "GridValue", parent=BODY, fontName="Malgun", fontSize=10,
    leading=14, textColor=INK, spaceAfter=0,
)


def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier" backColor="#E8DDCB">\1</font>', text)
    return text


def img_block(rel_path, caption=None):
    """Embed image keeping aspect ratio. No KeepTogether to avoid auto-shrink."""
    abs_path = ROOT / rel_path
    if not abs_path.exists():
        return [Paragraph(f"[이미지 누락: {rel_path}]", BODY)]
    with PILImage.open(abs_path) as im:
        w, h = im.size
    avail = A4[0] - 36 * mm
    iw = avail
    ih = h * (iw / w)
    max_h = A4[1] - 50 * mm
    if ih > max_h:
        ih = max_h
        iw = w * (ih / h)
    img = Image(str(abs_path), width=iw, height=ih)
    elems = [img]
    if caption:
        elems.append(Paragraph(caption, CAPTION))
    else:
        elems.append(Spacer(1, 8))
    return elems


def parse_table(lines):
    rows = []
    for ln in lines:
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows.append(cells)
    if len(rows) >= 2 and all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in rows[1]):
        return rows[0], rows[2:]
    return rows[0], rows[1:]


def build_table(header, body):
    col_count = max(len(header), max((len(r) for r in body), default=0))

    def fix(row, header_row=False):
        row = list(row) + [""] * (col_count - len(row))
        style = ParagraphStyle(
            "TblH" if header_row else "TblB", parent=BODY,
            fontName="MalgunBold" if header_row else "Malgun",
            fontSize=10, leading=14,
            textColor=colors.white if header_row else INK,
            spaceAfter=0,
        )
        return [Paragraph(inline(c), style) for c in row]

    data = [fix(header, header_row=True)] + [fix(r) for r in body]
    avail = A4[0] - 36 * mm
    col_widths = [avail / col_count] * col_count
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    # Anthropic-style table: header band + hairline row dividers, no full grid.
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Malgun"),
        ("FONTNAME", (0, 0), (-1, 0), "MalgunBold"),
        ("BACKGROUND", (0, 0), (-1, 0), ORANGE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 0, ORANGE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, TAN]),
    ]
    # hairline between body rows
    for r in range(1, len(data) - 1):
        style.append(("LINEBELOW", (0, r), (-1, r), 0.4, LINE))
    tbl.setStyle(TableStyle(style))
    return tbl


# ---------------- Section divider (full-page) ----------------

SECTION_TAGLINES = {
    "0": "5분 안에 프로젝트·역할·일정을 한눈에",
    "I": "프로젝트 개요와 핵심 정의",
    "II": "외부 환경과 시장의 압력",
    "III": "3C · SWOT · 페르소나로 본 차별화",
    "IV": "7대 레이어와 시스템 아키텍처",
    "V": "타겟 · 예산 · 일정 · 역할",
    "VI": "성과를 측정하는 4대 지표",
    "VII": "발생확률 × 영향도",
    "VIII": "6개 법령과 6대 리스크 방어",
    "IX": "사기 산업 ROI를 0으로",
    "X": "근거 자료와 인용",
    "XI": "데이터·시연·구조·일정의 실행 구체화",
    "XII": "오늘 코드 에디터를 열면 무엇을 쓰는가",
    "XIII": "5분 시작 · 파일 치트시트 · 트러블슈팅 · 용어 사전",
}

# Each chapter's "이 챕터의 핵심 3가지" — for the divider page
SECTION_HIGHLIGHTS = {
    "0": [
        ("원페이저", "무엇·왜·어떻게·누가·언제까지"),
        ("모듈 맵", "5레이어 18모듈·담당자 매핑"),
        ("역할 카드", "6인 첫날·의존·KPI 가이드"),
    ],
    "I": [
        ("정의", "사기 산업 시간당 매출을 0으로"),
        ("차별화", "Active Defense — 시간·정보·도구 약탈"),
        ("팀", "6인 4주 + 본선 2일"),
    ],
    "II": [
        ("피해", "2024년 8,545억 원"),
        ("골든타임", "30분 환수 윈도우"),
        ("기술", "한국어 LLM·TTS 성숙"),
    ],
    "III": [
        ("3C", "고령자·자녀·은행 디지털보안"),
        ("SWOT", "법리 트랙이 유일 차별 자원"),
        ("페르소나", "박순자 73세 + 김지영 28세 자녀"),
    ],
    "IV": [
        ("레이어", "미끼번호→봇→정보전→앱 5단"),
        ("MoSCoW", "Must 5종 / Should 3종"),
        ("위협", "MITRE ATLAS + OWASP LLM Top 10"),
    ],
    "V": [
        ("타겟", "시중은행·금감원·통신사"),
        ("예산", "130만 원 (예선 4주)"),
        ("역할", "기획·ML·백엔드·UX·법리 분담"),
    ],
    "VI": [
        ("탐지율", "87% (기존 78%)"),
        ("시간 약탈", "통화당 30분 이상"),
        ("환수 윈도우", "30분 이내 모의 동결"),
    ],
    "VII": [
        ("리스크 6종", "R1~R6 발생확률 × 영향도"),
        ("최우선", "R1 미끼봇 협박 발화"),
        ("대응", "Safety Guard + 가드레일"),
    ],
    "VIII": [
        ("법령", "통비법·개보법·신용정보법 등 6종"),
        ("판례", "대법원 2008도1237 (당사자 녹음)"),
        ("선례", "영국 Ofcom Active Defense 인증"),
    ],
    "IX": [
        ("정량", "환수율 1.97% → 30% 목표"),
        ("정성", "시니어 가족 동반 안전망"),
        ("국제", "Daisy AI 한국형 벤치마크"),
    ],
    "X": [
        ("법령", "현행 6개 + 2026 시행"),
        ("표준", "ISMS-P · MITRE ATLAS · OWASP"),
        ("통계", "경찰청·금감원·MarketsandMarkets"),
    ],
    "XI": [
        ("데이터", "정량·시나리오·합성 3계층"),
        ("음성", "Typecast + 7→1.5초 마스킹"),
        ("Guardian Live", "보호 번호로 단말 분리"),
    ],
    "XII": [
        ("스택", "FastAPI + Claude + Twilio + Streamlit"),
        ("스키마", "models.py 6개 테이블"),
        ("연결", "12.14 데이터 배선 11종"),
    ],
    "XIII": [
        ("5분", "환경 셋업 체크리스트"),
        ("치트시트", "파일 25개 한 줄 정리"),
        ("트러블", "자주 막히는 곳 10개"),
    ],
}


class SectionDivider(Flowable):
    """Full-page chapter intro: huge Roman numeral + chapter title + tagline.
    Drawn inside the page frame (origin = bottom-left of frame)."""

    def __init__(self, roman, title):
        super().__init__()
        self.roman = roman
        self.title = title

    def wrap(self, aw, ah):
        # Consume the entire remaining frame height so a PageBreak follows naturally
        self._w, self._h = aw, ah
        return aw, ah

    def draw(self):
        c = self.canv
        W = self._w
        H = self._h
        # Right-edge Orange ribbon
        c.setFillColor(ORANGE)
        c.rect(W - 14 * mm, 0, 14 * mm, H, fill=1, stroke=0)

        # Centered content vertically (~60% from bottom)
        cy = H * 0.62

        # Huge translucent Roman numeral as backdrop (Light Gray)
        c.setFillColor(TAN)
        c.setFont("MalgunBold", 220)
        c.drawString(0, cy - 70 * mm, self.roman)

        # CHAPTER label
        c.setFillColor(ORANGE)
        c.setFont("MalgunBold", 11)
        c.drawString(0, cy + 30 * mm, f"CHAPTER {self.roman}")

        # Chapter title - large Dark
        c.setFillColor(INK)
        c.setFont("MalgunBold", 34)
        c.drawString(0, cy + 14 * mm, self.title)

        # Thin Orange rule
        c.setStrokeColor(ORANGE)
        c.setLineWidth(2)
        c.line(0, cy + 6 * mm, 50 * mm, cy + 6 * mm)

        # Tagline
        c.setFillColor(SLATE)
        c.setFont("Malgun", 13)
        tag = SECTION_TAGLINES.get(self.roman, "")
        c.drawString(0, cy - 4 * mm, tag)

        # "이 챕터의 핵심 3가지" 카드 (있는 챕터만, 페이지 하단에 배치 - 워터마크보다 아래)
        highlights = SECTION_HIGHLIGHTS.get(self.roman)
        if highlights:
            # Top of cards: ~30mm above bottom margin
            card_y = 32 * mm
            card_h = 32 * mm
            card_gap = 4 * mm
            ribbon_w = 14 * mm
            avail_w = W - ribbon_w
            card_w = (avail_w - 2 * card_gap) / 3
            # Section label above cards
            c.setFillColor(ORANGE)
            c.setFont("MalgunBold", 10)
            c.drawString(0, card_y + card_h + 6 * mm, "이 챕터의 핵심 3가지")
            c.setStrokeColor(ORANGE)
            c.setLineWidth(0.6)
            c.line(0, card_y + card_h + 3 * mm, 40 * mm, card_y + card_h + 3 * mm)
            for idx, (label, value) in enumerate(highlights):
                x = idx * (card_w + card_gap)
                # Card body - stronger contrast
                c.setFillColor(TAN)
                c.setStrokeColor(ORANGE)
                c.setLineWidth(0.8)
                c.rect(x, card_y, card_w, card_h, fill=1, stroke=1)
                # Top color bar
                c.setFillColor(ORANGE)
                c.rect(x, card_y + card_h - 1.5 * mm, card_w, 1.5 * mm, fill=1, stroke=0)
                # Label
                c.setFillColor(ORANGE)
                c.setFont("MalgunBold", 9)
                c.drawString(x + 5 * mm, card_y + card_h - 9 * mm, label.upper())
                # Value (wrap if too long)
                c.setFillColor(INK)
                c.setFont("MalgunBold", 11)
                # Simple word wrap for value
                text_obj = c.beginText(x + 5 * mm, card_y + card_h - 16 * mm)
                text_obj.setFont("MalgunBold", 10.5)
                text_obj.setLeading(13)
                words = value.split(" ")
                line = ""
                max_chars = int((card_w - 10 * mm) / 2.4)  # ~2.4mm per Hangul char @ 10.5pt
                for w in words:
                    cand = (line + " " + w).strip()
                    if len(cand) > max_chars and line:
                        text_obj.textLine(line)
                        line = w
                    else:
                        line = cand
                if line:
                    text_obj.textLine(line)
                c.drawText(text_obj)

        # Vertical brand label on the orange ribbon
        c.saveState()
        c.translate(W - 6 * mm, 10 * mm)
        c.rotate(90)
        c.setFillColor(CREAM)
        c.setFont("MalgunBold", 10.5)
        c.drawString(0, 0, f"SENTINEL-30 / CHAPTER {self.roman}")
        c.restoreState()


# ---------------- Headings with left marker + number chip ----------------

NUM_RE = re.compile(r"^(\d+(?:\.\d+)*)\s+(.*)$")


def styled_heading(text, level):
    """level: 2 or 3. Returns a Table flowable styled as an Anthropic-style heading."""
    m = NUM_RE.match(text)
    if m:
        num, body = m.group(1), m.group(2)
    else:
        num, body = "", text
    if level == 2:
        font_size = 15
        leading = 19
        chip_bg = ORANGE
        chip_fg = colors.white
        body_color = INK
        marker_w = 1.4 * mm
        space_before = 14
        space_after = 6
    else:
        font_size = 12.5
        leading = 16
        chip_bg = TAN
        chip_fg = ORANGE
        body_color = INK
        marker_w = 1.0 * mm
        space_before = 10
        space_after = 4

    num_html = ""
    if num:
        num_html = (
            f'<font face="MalgunBold" size="{font_size - 2}" '
            f'color="{chip_fg.hexval()}" backColor="{chip_bg.hexval()}"> {num} </font>&nbsp;&nbsp;'
        )
    txt = f'{num_html}<font face="MalgunBold" size="{font_size}" '
    txt += f'color="{body_color.hexval()}">{inline(body)}</font>'

    p_style = ParagraphStyle(
        f"H{level}m", parent=BODY, fontName="MalgunBold",
        fontSize=font_size, leading=leading, spaceAfter=0, spaceBefore=0,
        textColor=body_color,
    )
    avail = A4[0] - 36 * mm
    inner = Paragraph(txt, p_style)
    tbl = Table(
        [[ "", inner ]],
        colWidths=[marker_w + 3 * mm, avail - marker_w - 3 * mm],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [
        Spacer(1, space_before),
        tbl,
        HRFlowable(width="100%", thickness=0.4, color=LINE,
                   spaceBefore=4, spaceAfter=space_after),
    ]


# ---------------- Callouts ----------------

def callout_stat(value, label):
    """Big stat callout: huge orange number + label."""
    avail = A4[0] - 36 * mm
    inner = [
        Paragraph(value, STAT_BIG),
        Paragraph(label, STAT_LABEL),
    ]
    tbl = Table([[inner]], colWidths=[avail])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TAN),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return [Spacer(1, 6), tbl, Spacer(1, 6)]


def callout_quote(text):
    """Pull quote: large bold text with left orange bar."""
    avail = A4[0] - 36 * mm
    inner = Paragraph(text, PULLQUOTE)
    tbl = Table([[inner]], colWidths=[avail])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    return [Spacer(1, 8), tbl, Spacer(1, 8)]


def build_workflow(steps):
    """Vertical workflow with numbered steps and arrows.
    steps: list of (label, description, kind) where kind ∈ {"real", "mock", "user", "info"}.
    Renders as a series of horizontal cards joined by Orange down-arrows."""
    KIND_COLOR = {
        "real": ORANGE,
        "mock": MID,
        "user": INK,
        "info": SAGE,
    }
    KIND_TAG = {
        "real": "AI 구현",
        "mock": "모킹",
        "user": "사용자",
        "info": "결과",
    }
    avail = A4[0] - 36 * mm
    elems = []
    arrow_style = ParagraphStyle(
        "wfArrow", parent=BODY, fontName="MalgunBold", fontSize=14,
        leading=16, textColor=ORANGE, alignment=TA_CENTER, spaceAfter=0,
    )
    label_style = ParagraphStyle(
        "wfLabel", parent=BODY, fontName="MalgunBold", fontSize=11.5,
        leading=15, textColor=INK, spaceAfter=2,
    )
    desc_style = ParagraphStyle(
        "wfDesc", parent=BODY, fontName="Malgun", fontSize=10,
        leading=14, textColor=SLATE, spaceAfter=0,
    )
    badge_style = ParagraphStyle(
        "wfBadge", parent=BODY, fontName="MalgunBold", fontSize=8,
        leading=10, textColor=colors.white, alignment=TA_CENTER, spaceAfter=0,
    )
    for idx, (label, desc, kind) in enumerate(steps):
        c = KIND_COLOR.get(kind, ORANGE)
        # number circle column
        num_para = Paragraph(f'<font color="white">{idx + 1}</font>', badge_style)
        body_inner = [
            Paragraph(label, label_style),
            Paragraph(desc, desc_style),
        ]
        badge_inner = Paragraph(KIND_TAG.get(kind, ""), badge_style)
        # outer table: [num_col, body_col, badge_col]
        num_col_w = 12 * mm
        badge_col_w = 22 * mm
        body_col_w = avail - num_col_w - badge_col_w
        row = Table(
            [[num_para, body_inner, badge_inner]],
            colWidths=[num_col_w, body_col_w, badge_col_w],
        )
        row.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), c),
            ("BACKGROUND", (1, 0), (1, 0), CREAM),
            ("BACKGROUND", (2, 0), (2, 0), c),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("ALIGN", (2, 0), (2, 0), "CENTER"),
            ("LEFTPADDING", (1, 0), (1, 0), 12),
            ("RIGHTPADDING", (1, 0), (1, 0), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEABOVE", (1, 0), (1, 0), 0.4, LINE),
            ("LINEBELOW", (1, 0), (1, 0), 0.4, LINE),
        ]))
        elems.append(row)
        if idx < len(steps) - 1:
            elems.append(Paragraph("↓", arrow_style))
    return [Spacer(1, 6)] + elems + [Spacer(1, 8)]


def callout_tldr(text):
    """TL;DR: Dark left rail with white label + big readable body."""
    avail = A4[0] - 36 * mm
    label_cell = Paragraph("TL;DR", TLDR_LABEL)
    body_cell = Paragraph(text, TLDR_BODY)
    label_w = 18 * mm
    tbl = Table(
        [[label_cell, body_cell]],
        colWidths=[label_w, avail - label_w],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), INK),
        ("BACKGROUND", (1, 0), (1, 0), WARM),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    return [Spacer(1, 6), tbl, Spacer(1, 8)]


def code_header(file_path, description):
    """Pre-code header: file path + (optional) one-line purpose."""
    avail = A4[0] - 36 * mm
    cell = [Paragraph(
        f'<font face="MalgunBold" color="{ORANGE.hexval()}">FILE</font> '
        f'&nbsp;&nbsp;<font face="Courier" color="{INK.hexval()}">{file_path}</font>',
        CODEHEAD_FILE,
    )]
    if description and description.strip():
        cell.append(Paragraph(description, CODEHEAD_DESC))
    tbl = Table([[cell]], colWidths=[avail])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TAN),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [Spacer(1, 6), tbl]


def warning_box(text):
    """Yellow/orange warning box for '흔한 실수' content."""
    avail = A4[0] - 36 * mm
    label_cell = Paragraph("⚠ 주의", WARN_LABEL)
    body_cell = Paragraph(text, WARN_BODY)
    label_w = 18 * mm
    tbl = Table(
        [[label_cell, body_cell]],
        colWidths=[label_w, avail - label_w],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BURNT),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fbf2e9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [Spacer(1, 6), tbl, Spacer(1, 8)]


def info_grid(pairs):
    """2 or 3 column grid: (label, value) tuples. Useful for WHAT/WHY/PREREQ/NEXT headers."""
    avail = A4[0] - 36 * mm
    cols = len(pairs)
    col_w = avail / cols
    row = []
    for label, value in pairs:
        cell = [Paragraph(label, GRID_LABEL), Paragraph(value, GRID_VALUE)]
        row.append(cell)
    tbl = Table([row], colWidths=[col_w] * cols)
    style = [
        ("BACKGROUND", (0, 0), (-1, -1), WARM),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]
    # Vertical dividers between cells
    for c in range(1, cols):
        style.append(("LINEBEFORE", (c, 0), (c, 0), 0.4, LINE))
    tbl.setStyle(TableStyle(style))
    return [Spacer(1, 6), tbl, Spacer(1, 8)]


def callout_legal(title, text):
    """Legal/note box: Light Gray bg with Blue left bar."""
    avail = A4[0] - 36 * mm
    inner = [Paragraph(title, CALLOUT_TITLE), Paragraph(text, CALLOUT_BODY)]
    tbl = Table([[inner]], colWidths=[avail])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TAN),
        ("LINEBEFORE", (0, 0), (0, -1), 3, DUSK),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return [Spacer(1, 6), tbl, Spacer(1, 6)]


IMG_RE = re.compile(r"!\[(.*?)\]\((.+?)\)")


def next_nonblank_is_image(lines, start):
    """Return True if the next non-empty line is a markdown image."""
    k = start
    while k < len(lines) and not lines[k].strip():
        k += 1
    if k >= len(lines):
        return False
    return IMG_RE.fullmatch(lines[k].strip()) is not None


def parse_md(md_text):
    flow = []
    lines = md_text.split("\n")
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Image
        m = IMG_RE.fullmatch(stripped)
        if m:
            caption = m.group(1) or None  # empty alt -> no caption
            rel = m.group(2)
            flow.extend(img_block(rel, caption))
            i += 1
            continue

        # Code fence (also supports ```workflow special block)
        if stripped.startswith("```"):
            fence_tag = stripped[3:].strip().lower()
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            if fence_tag == "workflow":
                # Parse lines of: kind | label | description
                steps = []
                for cl in code_lines:
                    parts = [p.strip() for p in cl.split("|")]
                    if len(parts) == 3:
                        kind, label, desc = parts
                        steps.append((label, desc, kind))
                if steps:
                    flow.extend(build_workflow(steps))
                continue
            code_text = "\n".join(code_lines)
            # Auto-detect file path comment as first line (e.g. "# backend/app/services/miketbot.py")
            first_line = code_lines[0].strip() if code_lines else ""
            file_path_m = re.match(
                r"^(?://|#|<!--)\s*([a-zA-Z0-9_./\-]+\.(?:py|kt|xml|yml|yaml|sql|toml|js|ts|json|md|sh))",
                first_line,
            )
            if file_path_m:
                flow.extend(code_header(file_path_m.group(1), ""))
            has_hangul = any("가" <= ch <= "힣" for ch in code_text)
            flow.append(Preformatted(code_text, CODE_KO if has_hangul else CODE))
            continue

        # Headings
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            # Section divider for roman-numeral chapters: "I. 기획 개요", "II. ..."
            # Also accept "0. 한눈에 보기" for Chapter 0
            roman = re.match(r"^([0IVXLC]+)\.\s+(.+)$", title)
            if roman:
                flow.append(PageBreak())
                flow.append(SectionDivider(roman.group(1), roman.group(2)))
                # next H2 should start on a fresh page
                flow.append(PageBreak())
            else:
                flow.append(PageBreak())
                flow.append(Paragraph(inline(title), H1))
                flow.append(HRFlowable(width="100%", thickness=1.5, color=ORANGE,
                                       spaceBefore=2, spaceAfter=8))
            i += 1
            continue
        if stripped.startswith("## "):
            flow.extend(styled_heading(stripped[3:], level=2))
            i += 1
            continue
        if stripped.startswith("### "):
            if next_nonblank_is_image(lines, i + 1):
                flow.append(CondPageBreak(180 * mm))
            flow.extend(styled_heading(stripped[4:], level=3))
            i += 1
            continue
        if stripped.startswith("#### "):
            if next_nonblank_is_image(lines, i + 1):
                flow.append(CondPageBreak(180 * mm))
            flow.append(Paragraph(inline(stripped[5:]), H4))
            i += 1
            continue

        if re.fullmatch(r"-{3,}", stripped):
            flow.append(HRFlowable(width="100%", thickness=0.6, color=LGRAY,
                                   spaceBefore=4, spaceAfter=4))
            i += 1
            continue

        if stripped.startswith("> "):
            quote_lines = []
            while i < n and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").lstrip())
                i += 1
            joined = " ".join(quote_lines).strip()
            # Callout triggers
            stat_m = re.match(r"^📊\s*(.+?)\s*\|\s*(.+)$", joined)
            legal_m = re.match(r"^(?:⚖|📌)\s*(.+?):\s*(.+)$", joined)
            tldr_m = re.match(r"^(?:🎯|TL;DR)\s*[:：]?\s*(.+)$", joined)
            warn_m = re.match(r"^(?:⚠|⚠️)\s*(.+)$", joined)
            file_m = re.match(r"^📄\s*([^\s]+)\s*[—\-]\s*(.+)$", joined)
            grid_m = re.match(r"^🧭\s*(.+)$", joined)
            if tldr_m:
                flow.extend(callout_tldr(inline(tldr_m.group(1))))
            elif warn_m:
                flow.extend(warning_box(inline(warn_m.group(1))))
            elif file_m:
                flow.extend(code_header(file_m.group(1), inline(file_m.group(2))))
            elif grid_m:
                # 🧭 LABEL1: value1 | LABEL2: value2 | LABEL3: value3
                pairs = []
                for chunk in grid_m.group(1).split("|"):
                    parts = chunk.strip().split(":", 1)
                    if len(parts) == 2:
                        pairs.append((parts[0].strip(), inline(parts[1].strip())))
                if pairs:
                    flow.extend(info_grid(pairs))
            elif stat_m:
                flow.extend(callout_stat(stat_m.group(1), stat_m.group(2)))
            elif legal_m:
                flow.extend(callout_legal(legal_m.group(1), legal_m.group(2)))
            elif joined.startswith("**") and joined.endswith("**"):
                flow.extend(callout_quote(inline(joined.strip("*"))))
            elif joined.startswith('"') and joined.endswith('"'):
                flow.extend(callout_quote(inline(joined)))
            else:
                flow.append(Paragraph(inline(joined), QUOTE))
            continue

        if stripped.startswith("|") and "|" in stripped[1:]:
            tbl_lines = []
            while i < n and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i])
                i += 1
            if len(tbl_lines) >= 2:
                header, body = parse_table(tbl_lines)
                flow.append(build_table(header, body))
                flow.append(Spacer(1, 6))
            continue

        if re.match(r"^\s*[-*]\s+", line):
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                m2 = re.match(r"^(\s*)[-*]\s+(.*)$", lines[i])
                indent = len(m2.group(1))
                text = m2.group(2)
                style = ParagraphStyle(
                    "ListItem", parent=BODY,
                    leftIndent=16 + indent * 8,
                    bulletIndent=4 + indent * 8,
                    spaceAfter=2,
                )
                flow.append(Paragraph(inline(text), style, bulletText="•"))
                i += 1
            continue

        if re.match(r"^\s*\d+\.\s+", line):
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                m2 = re.match(r"^(\s*)(\d+)\.\s+(.*)$", lines[i])
                indent = len(m2.group(1))
                num = m2.group(2)
                text = m2.group(3)
                style = ParagraphStyle(
                    "OrdItem", parent=BODY,
                    leftIndent=18 + indent * 8,
                    bulletIndent=4 + indent * 8,
                    spaceAfter=2,
                )
                flow.append(Paragraph(inline(text), style, bulletText=f"{num}."))
                i += 1
            continue

        if not stripped:
            flow.append(Spacer(1, 4))
            i += 1
            continue

        # plain paragraph
        para_lines = [line]
        i += 1
        while i < n:
            nxt = lines[i]
            ns = nxt.strip()
            if (not ns or ns.startswith("#") or ns.startswith("```") or
                ns.startswith("|") or ns.startswith(">") or
                IMG_RE.fullmatch(ns) or
                re.match(r"^\s*[-*]\s+", nxt) or
                re.match(r"^\s*\d+\.\s+", nxt) or
                re.fullmatch(r"-{3,}", ns)):
                break
            para_lines.append(nxt)
            i += 1
        flow.append(Paragraph(inline(" ".join(s.strip() for s in para_lines)), BODY))

    return flow


def cover_page(canvas, doc):
    """Cover (Claude Design): Dark left rail, big title, right-side stat tiles."""
    canvas.saveState()
    W, H = A4

    # 1) Background
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)

    # 2) Left dark rail with rotated brand text
    canvas.setFillColor(INK)
    canvas.rect(0, 0, 14 * mm, H, fill=1, stroke=0)
    canvas.saveState()
    canvas.translate(9 * mm, 30 * mm)
    canvas.rotate(90)
    canvas.setFillColor(CREAM)
    canvas.setFont("MalgunBold", 9.5)
    canvas.drawString(0, 0, "ANTHROPIC LABS  /  AI 해커톤 2026  /  사회안전 ⑧")
    canvas.restoreState()

    # 3) Orange accent block (signature ribbon)
    canvas.setFillColor(ORANGE)
    canvas.rect(14 * mm, H - 80 * mm, 2.5 * mm, 60 * mm, fill=1, stroke=0)

    # 4) Eyebrow
    canvas.setFont("MalgunBold", 10)
    canvas.setFillColor(ORANGE)
    canvas.drawString(22 * mm, H - 30 * mm, "PROJECT BRIEF")
    canvas.setFont("Malgun", 10)
    canvas.setFillColor(SLATE)
    canvas.drawString(48 * mm, H - 30 * mm, "/  Active Defense Platform")

    # 5) Title block
    canvas.setFont("MalgunBold", 60)
    canvas.setFillColor(INK)
    canvas.drawString(22 * mm, H - 60 * mm, "Sentinel-30")
    canvas.setFont("MalgunBold", 16)
    canvas.setFillColor(INK)
    canvas.drawString(22 * mm, H - 74 * mm, "보이스피싱 산업의 ROI를 무너뜨리는")
    canvas.drawString(22 * mm, H - 84 * mm, "AI 능동방어 플랫폼")

    # 6) Pull quote band (full width)
    canvas.setFillColor(TAN)
    canvas.rect(22 * mm, H - 113 * mm, W - 44 * mm, 16 * mm, fill=1, stroke=0)
    canvas.setFillColor(ORANGE)
    canvas.rect(22 * mm, H - 113 * mm, 1.5 * mm, 16 * mm, fill=1, stroke=0)
    canvas.setFont("MalgunBold", 13)
    canvas.setFillColor(INK)
    canvas.drawString(28 * mm, H - 104 * mm,
                      "\"우리는 피해자를 지키지 않는다. 사기범을 망친다.\"")

    # 7) Stat tiles row — three big numbers
    tile_y = H - 162 * mm
    tile_h = 35 * mm
    tile_w = (W - 44 * mm - 8 * mm) / 3
    stats = [
        ("30분", "환수 골든타임", ORANGE),
        ("₩1.97조", "2024 보이스피싱 피해", INK),
        ("7", "Defense-in-Depth 레이어", SAGE),
    ]
    for idx, (val, lbl, color) in enumerate(stats):
        x = 22 * mm + idx * (tile_w + 4 * mm)
        # tile body
        canvas.setFillColor(CREAM)
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.rect(x, tile_y, tile_w, tile_h, fill=1, stroke=1)
        # top color bar
        canvas.setFillColor(color)
        canvas.rect(x, tile_y + tile_h - 1.5 * mm, tile_w, 1.5 * mm, fill=1, stroke=0)
        # value
        canvas.setFillColor(color)
        canvas.setFont("MalgunBold", 24)
        canvas.drawString(x + 6 * mm, tile_y + 16 * mm, val)
        # label
        canvas.setFillColor(SLATE)
        canvas.setFont("Malgun", 9.5)
        canvas.drawString(x + 6 * mm, tile_y + 7 * mm, lbl)

    # 8) Mini diagram strip — attack vs defense
    strip_y = H - 188 * mm
    canvas.setFont("MalgunBold", 10)
    canvas.setFillColor(ORANGE)
    canvas.drawString(22 * mm, strip_y + 14 * mm, "MECHANISM")
    canvas.setFont("Malgun", 10.5)
    canvas.setFillColor(INK)
    canvas.drawString(22 * mm, strip_y + 6 * mm,
                      "사기범 발신  →  미끼봇 흡수  →  정보 추출  →  FDS·통신사·경찰망 자동 공급  →  ROI 붕괴")
    # arrow underline
    canvas.setStrokeColor(ORANGE)
    canvas.setLineWidth(0.8)
    canvas.line(22 * mm, strip_y, W - 22 * mm, strip_y)

    # 9) Metadata grid
    meta_y = H - 222 * mm
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(22 * mm, meta_y + 4 * mm, W - 22 * mm, meta_y + 4 * mm)
    items = [
        ("CATEGORY", "⑧ AI 기반 보이스피싱 공동 대응"),
        ("TEAM", "6인 (기획 1 / ML 2 / 백엔드 1 / UX 1 / 법리·보안 1)"),
        ("DATE", "2026-05-12"),
        ("STAGE", "예선 4주 + 본선 무박 2일"),
    ]
    col_w = (W - 44 * mm) / 2
    for idx, (k, v) in enumerate(items):
        col = idx % 2
        row = idx // 2
        x = 22 * mm + col * col_w
        y = meta_y - row * 12 * mm
        canvas.setFont("MalgunBold", 8.5)
        canvas.setFillColor(ORANGE)
        canvas.drawString(x, y, k)
        canvas.setFont("Malgun", 10.5)
        canvas.setFillColor(INK)
        canvas.drawString(x, y - 5 * mm, v)

    # 10) Footer band
    canvas.setFillColor(INK)
    canvas.rect(14 * mm, 0, W - 14 * mm, 12 * mm, fill=1, stroke=0)
    canvas.setFont("Malgun", 9)
    canvas.setFillColor(CREAM)
    canvas.drawString(22 * mm, 4.5 * mm,
                      "Sentinel-30  ·  Active Defense × 금융 IR × 법적 안전지대")
    canvas.setFont("MalgunBold", 9)
    canvas.drawRightString(W - 22 * mm, 4.5 * mm, "COVER")

    canvas.restoreState()


def on_page(canvas, doc):
    canvas.saveState()
    W, H = A4
    # warm cream background
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # top accent (thin Orange line, Anthropic style)
    canvas.setFillColor(ORANGE)
    canvas.rect(0, H - 2.5 * mm, W, 2.5 * mm, fill=1, stroke=0)
    # footer
    canvas.setFont("Malgun", 8.5)
    canvas.setFillColor(SLATE)
    canvas.drawString(18 * mm, 10 * mm,
                      "Sentinel-30 — 보이스피싱 산업 ROI 파괴 플랫폼")
    canvas.drawRightString(W - 18 * mm, 10 * mm, f"- {doc.page} -")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(18 * mm, 12 * mm, W - 18 * mm, 12 * mm)
    canvas.restoreState()


def resolve_output(target: Path) -> Path:
    """If target is locked (open in viewer), pick a free suffixed name."""
    def writable(p: Path) -> bool:
        try:
            if p.exists():
                with open(p, "ab"):
                    pass
            return True
        except PermissionError:
            return False
    if writable(target):
        return target
    stem, suf = target.stem, target.suffix
    for i in range(2, 50):
        cand = target.with_name(f"{stem}_{i}{suf}")
        if writable(cand):
            print(f"[WARN] {target.name} is locked - writing to {cand.name}")
            return cand
    raise PermissionError(f"No writable filename near {target}")


def main():
    md = SRC.read_text(encoding="utf-8")
    md = re.sub(r"^# Sentinel-30.*?\n---\n", "", md, count=1, flags=re.DOTALL)
    story = parse_md(md)
    story.insert(0, PageBreak())

    out = resolve_output(OUT)
    doc = SimpleDocTemplate(
        str(out), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="Sentinel-30 기획서",
        author="AI 해커톤 팀",
    )
    doc.build(story, onFirstPage=cover_page, onLaterPages=on_page)
    print(f"OK -> {out}")


if __name__ == "__main__":
    main()
