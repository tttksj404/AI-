"""Sentinel-30 v3 diagrams — light academic research style (14종)."""
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import (
    Circle,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
    Wedge,
)

_ROOT = Path(__file__).resolve().parent

# ---------- Korean font (deck + OS fallback) ----------
_FONT_PATHS = [
    _ROOT / "fonts" / "Pretendard-Regular.ttf",
    _ROOT / "fonts" / "Pretendard-SemiBold.ttf",
    _ROOT / "fonts" / "Pretendard-Bold.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",        # macOS
    "/Library/Fonts/AppleSDGothicNeo.ttc",
    r"C:\Windows\Fonts\malgun.ttf",                       # Windows
    r"C:\Windows\Fonts\malgunbd.ttf",
]
_loaded = []
for fp in _FONT_PATHS:
    if Path(fp).exists():
        fm.fontManager.addfont(str(fp))
        _loaded.append(str(fp))

# Prefer whichever is available on the current OS
if any("pretendard" in p.lower() for p in _loaded):
    plt.rcParams["font.family"] = "Pretendard"
    plt.rcParams["font.monospace"] = ["Consolas", "Pretendard", "DejaVu Sans Mono"]
elif any("malgun" in p.lower() for p in _loaded):
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["font.monospace"] = ["Consolas", "Malgun Gothic", "DejaVu Sans Mono"]
else:
    plt.rcParams["font.family"] = "Apple SD Gothic Neo"
    plt.rcParams["font.monospace"] = ["Menlo", "Apple SD Gothic Neo", "DejaVu Sans Mono"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = _ROOT
OUT = ROOT / "images"
OUT.mkdir(exist_ok=True)

# ===== LIGHT PALETTE (전 다이어그램 공통) =====
BG = "#fbfaf7"
PANEL = "#ffffff"
PANEL2 = "#f3f1eb"
PANEL3 = "#ece6dc"
LINEC = "#ded8ce"
TEXT = "#26231f"
DIM = "#6f6a61"
DIM2 = "#aaa39a"

NEON_O = "#d8652a"   # primary orange
NEON_S = "#5d8c61"   # sage/green
NEON_B = "#3f7ca8"   # blue
NEON_P = "#7b669b"   # purple
NEON_R = "#bf4a42"   # red/warning
NEON_Y = "#b28a32"   # gold

# legacy aliases (호환)
INK = TEXT
SLATE = DIM
ORANGE = NEON_O
SAGE = NEON_S
DUSK = NEON_B
RED = NEON_R
GOLD = NEON_Y
PURPLE = NEON_P
TAN = PANEL2
CREAM = BG


MAX_PX = 1800  # API many-image 요청 2000px 제한 회피용 cap


def save(fig, name, dpi=200):
    path = OUT / name
    fig.patch.set_facecolor(BG)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    # 1800px 초과 시 다운스케일 (Lanczos)
    from PIL import Image
    with Image.open(path) as im:
        w, h = im.size
        m = max(w, h)
        if m > MAX_PX:
            s = MAX_PX / m
            im.resize((int(w * s), int(h * s)), Image.LANCZOS).save(path, optimize=True)
            print(f"[OK] {path.name}  ({w}x{h} → {int(w*s)}x{int(h*s)})")
            return
    print(f"[OK] {path.name}  ({w}x{h})")


def _setup(figsize):
    """공통 라이트 캔버스 셋업."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    return fig, ax


def _title(ax, x, y, title, sub=None, ha="center"):
    """타이틀 + 서브타이틀."""
    ax.text(x, y, title, fontsize=19, fontweight="bold", color=TEXT, ha=ha)
    if sub:
        ax.text(x, y - 0.5, sub, fontsize=11, color=DIM, ha=ha)


def _panel(ax, x, y, w, h, accent=None):
    """라이트 패널 박스. accent 색상이 있으면 상단에 thin bar.
    NOTE: zorder=0.5로 두어 default patch(1)·text(3)이 항상 위에 그려지도록 강제."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.04,rounding_size=0.12",
                                facecolor=PANEL, edgecolor=LINEC, linewidth=0.7,
                                zorder=0.5))
    if accent:
        ax.add_patch(Rectangle((x, y + h - 0.04), w, 0.04,
                               facecolor=accent, edgecolor=accent, zorder=0.8))


def _node(ax, x, y, r, color, label=None, sublabel=None, big=False):
    """노드 + glow halo."""
    for hr, ha in [(r * 2.0, 0.06), (r * 1.55, 0.12), (r * 1.2, 0.2)]:
        ax.add_patch(Circle((x, y), hr, facecolor=color, alpha=ha,
                            edgecolor="none", zorder=3))
    ax.add_patch(Circle((x, y), r, facecolor=PANEL2,
                        edgecolor=color, linewidth=2.2 if big else 1.5, zorder=4))
    if label:
        ax.text(x, y + 0.15 if sublabel else 0, label,
                fontsize=11.5 if big else 10, fontweight="bold",
                color=TEXT, ha="center", va="center", zorder=5,
                path_effects=[pe.withStroke(linewidth=2.4, foreground=PANEL2)])
    if sublabel:
        ax.text(x, y - 0.22, sublabel, fontsize=8.5, color=color,
                ha="center", zorder=5, family="monospace")


def _neon_arrow(ax, x1, y1, x2, y2, color=NEON_O, lw=1.4, alpha=0.85,
                glow=True, head=True):
    """neon glow 화살표."""
    if glow:
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw * 3,
                alpha=0.18, zorder=1, solid_capstyle="round")
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw,
            alpha=alpha, zorder=2, solid_capstyle="round")
    if head:
        # 작은 화살표 끝
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     arrowstyle="-|>", mutation_scale=12,
                                     color=color, linewidth=0, alpha=alpha,
                                     zorder=3))


# ================================================================
#  1. 시스템 아키텍처 — 5단 데이터 흐름 (라이트)
# ================================================================
def system_architecture():
    """Landscape — 5단 가로 흐름 (좌→우 화살표)."""
    fig, ax = _setup((16, 5.5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5.5)
    # 타이틀 — 카드와 충분히 떨어지도록 위로 올림
    ax.text(8, 5.20, "System Architecture",
            fontsize=18, fontweight="bold", color=TEXT, ha="center")
    ax.text(8, 4.85, "사기범 발신부터 정보전 허브 자동 공급까지 5단 데이터 흐름",
            fontsize=10.5, color=DIM, ha="center")

    layers = [
        ("01", "미끼번호 풀", "통신사 협력\n비활성 번호 N만개",
         "사기범 무작위 발신 유입", NEON_O),
        ("02", "AI 미끼봇\n(Honeypot)", "멀티 에이전트 LLM\n한국어 STT/TTS",
         "30분~2h 통화 유지\n70대 페르소나", NEON_S),
        ("03", "정보 수집 엔진", "음성지문 + 시나리오 8종\n계좌·URL 추출",
         "통화에서 자발적\n정보 노출 흡수", NEON_B),
        ("04", "실시간 정보전 허브", "통신사·경찰망\n금감원 신고 채널",
         "PoC: 모의 신고 이벤트\n자동화는 추후 계획", NEON_P),
        ("05", "시니어 가디언 앱", "부모 위험 통화 감지\n자녀 푸시",
         "1억+ 송금 5분 내\n자녀 거부권", NEON_Y),
    ]

    n = len(layers)
    card_w = 2.8
    gap = 0.30
    total = n * card_w + (n - 1) * gap
    x0 = (16 - total) / 2
    y_card = 0.95
    card_h = 3.55
    for i, (num, name, tech, role, c) in enumerate(layers):
        x = x0 + i * (card_w + gap)
        _panel(ax, x, y_card, card_w, card_h, accent=c)
        # 상단 큰 번호
        ax.text(x + card_w - 0.25, y_card + card_h - 0.30, num,
                fontsize=28, fontweight="bold", color=c, alpha=0.55,
                ha="right", va="top", family="monospace")
        # 제목
        ax.text(x + 0.25, y_card + card_h - 0.45, name, fontsize=11.5,
                fontweight="bold", color=TEXT, va="top", linespacing=1.2)
        # 기술
        ax.text(x + 0.25, y_card + card_h - 1.70, tech, fontsize=9, color=DIM,
                va="top", linespacing=1.4)
        # 역할
        ax.text(x + 0.25, y_card + 0.30, role, fontsize=9, color=c, va="bottom",
                style="italic", linespacing=1.3)

    # 화살표 (좌→우 카드 사이)
    for i in range(n - 1):
        x_left = x0 + i * (card_w + gap) + card_w
        x_right = x_left + gap - 0.02
        ay = y_card + card_h / 2
        _neon_arrow(ax, x_left, ay, x_right, ay, color=NEON_O, lw=1.4)

    # 하단 메시지
    ax.text(8, 0.50,
            "→ 사기범 발신을 자원으로 흡수, 정보를 자동 공급해 ROI 감소 유도",
            fontsize=10.5, color=NEON_O, ha="center", style="italic",
            fontweight="bold")
    save(fig, "01_architecture.png")


# ================================================================
#  2. 30분 골든타임 (라이트)
# ================================================================
def golden_timeline():
    fig, ax = _setup((14, 6.5))
    ax.set_xlim(-2, 68)
    ax.set_ylim(-3.5, 6.5)
    _title(ax, 33, 5.8, "30분 골든타임",
           "송금 완료 ~ 인출 시작 사이의 시간 자산화")

    # zones
    ax.add_patch(FancyBboxPatch((0, -0.5), 30, 1.0,
                                boxstyle="round,pad=0.02,rounding_size=0.15",
                                facecolor=NEON_O, edgecolor=NEON_O, alpha=0.16,
                                zorder=1))
    ax.add_patch(FancyBboxPatch((30, -0.5), 35, 1.0,
                                boxstyle="round,pad=0.02,rounding_size=0.15",
                                facecolor=NEON_R, edgecolor=NEON_R, alpha=0.12,
                                zorder=1))
    # base timeline (subtle)
    ax.plot([0, 65], [0, 0], color=LINEC, linewidth=1.4, zorder=2)

    # zone labels
    ax.text(15, 2.5, "GOLDEN  TIME", fontsize=11, fontweight="bold",
            color=NEON_O, ha="center", family="monospace")
    ax.text(15, 2.0, "30분 — 우리의 개입 구간", fontsize=10.5,
            color=TEXT, ha="center")
    ax.text(47, 2.5, "추적 불가 구간", fontsize=11, fontweight="bold",
            color=NEON_R, ha="center")
    ax.text(47, 2.0, "자금 추적이 사실상 불가능", fontsize=10.5,
            color=DIM, ha="center")

    events = [
        (0, "T+0", "통화 시작", NEON_B),
        (15, "T+15", "송금 완료\n(피해자 평균)", NEON_O),
        (30, "T+30", "사기범 계좌\n인출 시작", NEON_R),
        (60, "T+60", "자금 추적\n사실상 불가", "#a93434"),
    ]
    for x, label, desc, c in events:
        # glow node
        for r, a in [(0.95, 0.12), (0.7, 0.22)]:
            ax.add_patch(Circle((x, 0), r, facecolor=c, alpha=a,
                                edgecolor="none", zorder=3))
        ax.add_patch(Circle((x, 0), 0.35, facecolor=BG,
                            edgecolor=c, linewidth=2.2, zorder=4))
        ax.text(x, 1.25, label, fontsize=10.5, fontweight="bold",
                color=c, ha="center", family="monospace", zorder=5)
        ax.text(x, -1.7, desc, fontsize=10, color=DIM, ha="center",
                va="center", zorder=5)

    # 우리 개입 강조 (화살표는 desc 텍스트 아래로)
    ax.annotate("Sentinel-30 개입\n시간 흡수 + 정보 수집 + 신고 자동화",
                xy=(15, -0.5), xytext=(11, -3.0),
                fontsize=10.5, fontweight="bold", color=NEON_S, ha="center",
                arrowprops=dict(arrowstyle="->", color=NEON_S, lw=1.8,
                                connectionstyle="arc3,rad=-0.18"),
                zorder=2)
    save(fig, "02_golden_timeline.png")


# ================================================================
#  3. SWOT (라이트 2x2)
# ================================================================
def swot_matrix():
    fig, ax = _setup((14, 9.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    _title(ax, 7, 9.4, "SWOT Analysis",
           "내부 강·약점 × 외부 기회·위협")

    cells = [
        (0.5, 4.95, 6.5, 3.85, "S  STRENGTHS", NEON_S, [
            "Active Defense 프레임 — 국내 유일 차별화",
            "영국 Daisy AI 벤치마크 + 한국 맞춤 설계",
            "멀티 에이전트 LLM 구조로 컨텍스트 한계 돌파",
            "6개 법령 합법성 검토 완료",
            "MITRE ATLAS · OWASP LLM 위협 모델 통합",
        ]),
        (7.0, 4.95, 6.5, 3.85, "W  WEAKNESSES", NEON_Y, [
            "통신사·은행 제휴 없으면 미끼번호 풀 확보 난항",
            "한국어 노년 화자 STT 학습 데이터 부족",
            "AI 인간 사칭 — AI 기본법 시행령 미확정",
            "6인 팀 4주 — 풀스택 구현 한계",
            "사기범 음성지문 오인식 시 명예훼손 리스크",
        ]),
        (0.5, 0.85, 6.5, 3.85, "O  OPPORTUNITIES", NEON_B, [
            "2024 보이스피싱 피해 8,545억 — 사회적 압박 최고",
            "금감원·금융보안원 사기 대응 예산 확대",
            "영국 Ofcom 적법성 인증 — 국제 선례 존재",
            "AI 기본법 (2026 시행) — 공공안전 예외 등록 가능",
            "시중은행 FDS 고도화 수요 (제휴 PoC 기회)",
        ]),
        (7.0, 0.85, 6.5, 3.85, "T  THREATS", NEON_R, [
            "사기범의 적대적 공격 — TTS 합성음 식별 회피",
            "통신사 약관·전기통신사업법 해석 변동",
            "경찰청·금감원 데이터 공유 채널 정치적 변수",
            "글로벌 사기 거점(중국·동남아) 협조 한계",
            "유사 솔루션 (KT 후후·SKT 에이닷·토스 사이렌) 미끼봇 흡수",
        ]),
    ]
    for x, y, w, h, title, color, items in cells:
        _panel(ax, x, y, w, h, accent=color)
        ax.text(x + 0.4, y + h - 0.5, title, fontsize=12.5, fontweight="bold",
                color=color, family="monospace")
        for k, item in enumerate(items):
            iy = y + h - 1.15 - k * 0.55
            # neon dot bullet
            ax.add_patch(Circle((x + 0.55, iy + 0.1), 0.06,
                                facecolor=color, edgecolor="none", zorder=4))
            ax.text(x + 0.85, iy, item, fontsize=9.8, color=TEXT, va="bottom")
    save(fig, "03_swot.png")


# ================================================================
#  4. 리스크 매트릭스 (라이트 heatmap)
# ================================================================
def risk_matrix():
    """Landscape — 16:6 aspect. 좌측 매트릭스 + 우측 범례 분리."""
    fig, ax = _setup((16, 6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 6)
    _title(ax, 8, 5.85, "Risk Matrix",
           "발생확률 × 영향도 (우선순위 히트맵)")

    # 매트릭스 영역 (좌측)
    mx0, my0 = 1.6, 0.85
    cell_w, cell_h = 1.4, 1.15
    cell_colors = [
        ["#eef2e8", "#f4ecd6", "#f1dccd"],   # row 0 = LOW prob
        ["#f4ecd6", "#f1dccd", "#ecc4b8"],   # row 1 = MID prob
        ["#f1dccd", "#ecc4b8", "#dfa195"],   # row 2 = HIGH prob
    ]
    for i in range(3):       # prob row
        for j in range(3):   # impact col
            ax.add_patch(Rectangle((mx0 + j * cell_w, my0 + i * cell_h),
                                   cell_w - 0.05, cell_h - 0.05,
                                   facecolor=cell_colors[i][j],
                                   edgecolor=BG, linewidth=2))

    # 축 라벨 (axis off 우회: ax.text 직접)
    for j, lab in enumerate(["LOW", "MID", "HIGH"]):
        ax.text(mx0 + j * cell_w + (cell_w - 0.05) / 2, my0 - 0.3,
                lab, fontsize=11, color=DIM, family="monospace", ha="center")
    for i, lab in enumerate(["LOW", "MID", "HIGH"]):
        ax.text(mx0 - 0.25, my0 + i * cell_h + (cell_h - 0.05) / 2,
                lab, fontsize=11, color=DIM, family="monospace",
                ha="right", va="center")
    ax.text(mx0 + 1.5 * cell_w, my0 - 0.62, "영향도 →",
            fontsize=11, color=TEXT, ha="center", fontweight="bold")
    ax.text(mx0 - 0.85, my0 + 1.5 * cell_h, "발생 확률 →",
            fontsize=11, color=TEXT, ha="center", va="center",
            rotation=90, fontweight="bold")

    # 리스크 노드: (prob_row, impact_col, label, color)
    risks = [
        (2, 2, "R1", NEON_R),
        (1, 2, "R2", NEON_R),
        (1, 1, "R3", NEON_Y),
        (2, 1, "R4", NEON_O),
        (1, 2, "R5", NEON_R),
        (2, 1, "R6", NEON_O),
        (1, 1, "R7", NEON_Y),
        (1, 1, "R8", NEON_Y),
    ]
    placed = {}
    for p, im, label, c in risks:
        key = (p, im)
        n = placed.get(key, 0)
        dx = (n % 2) * 0.45 - 0.22
        dy = (n // 2) * 0.4 - 0.18
        placed[key] = n + 1
        cx = mx0 + im * cell_w + (cell_w - 0.05) / 2 + dx
        cy = my0 + p * cell_h + (cell_h - 0.05) / 2 + dy
        for r, a in [(0.32, 0.18), (0.24, 0.32)]:
            ax.add_patch(Circle((cx, cy), r, facecolor=c, alpha=a,
                                edgecolor="none", zorder=3))
        ax.add_patch(Circle((cx, cy), 0.19, facecolor=PANEL2,
                            edgecolor=c, linewidth=1.8, zorder=4))
        ax.text(cx, cy, label, fontsize=9, color=TEXT,
                fontweight="bold", ha="center", va="center", zorder=5)

    # 범례 (우측 패널) — 8개 세로 배치
    leg_x = 8.5
    _panel(ax, leg_x, 0.65, 7.1, 4.40)
    ax.text(leg_x + 0.3, 4.75, "RISK LIST", fontsize=10, fontweight="bold",
            color=NEON_O, family="monospace", va="center")
    ax.plot([leg_x + 0.3, leg_x + 6.8], [4.50, 4.50],
            color=LINEC, linewidth=0.6)

    legend = [
        ("R1", "미끼봇 협박·모욕 발화", NEON_R),
        ("R2", "실존 제3자 정보 노출", NEON_R),
        ("R3", "사기범 데이터 무기한 보관", NEON_Y),
        ("R4", "음성지문 오인식 (선의의 일반인)", NEON_O),
        ("R5", "통신사 약관·전기통신사업법", NEON_R),
        ("R6", "AI 인간 사칭 (AI 기본법)", NEON_O),
        ("R7", "적대적 공격 분류 우회", NEON_Y),
        ("R8", "가디언 앱 개인정보 유출", NEON_Y),
    ]
    for i, (lbl, desc, c) in enumerate(legend):
        col = i % 2
        row = i // 2
        x = leg_x + 0.35 + col * 3.4
        y = 4.10 - row * 0.78
        ax.add_patch(Circle((x + 0.13, y), 0.16, facecolor=PANEL2,
                            edgecolor=c, linewidth=1.4))
        ax.text(x + 0.13, y, lbl, fontsize=8.5, color=TEXT,
                fontweight="bold", ha="center", va="center")
        ax.text(x + 0.45, y, desc, fontsize=9, color=DIM, va="center")
    save(fig, "04_risk_matrix.png")


# ================================================================
#  5. KPI 대시보드 — 큰 stat 카드
# ================================================================
def kpi_dashboard():
    fig, ax = _setup((14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7.2)
    _title(ax, 7, 6.9, "KPI Dashboard",
           "기존 솔루션 대비 Sentinel-30 핵심 4대 지표")

    kpis = [
        ("탐지율", "기존 78%", "87%", "+9%p", NEON_B,
         [0.78, 0.87]),
        ("사기범 시간 흡수", "기존 0분", "30분", "+30분", NEON_S,
         [0.0, 1.0]),
        ("환수 골든타임", "기존 240분", "30분", "-210분", NEON_O,
         [1.0, 0.125]),
        ("법정 신고시한 충족", "기존 65%", "100%", "+35%p", NEON_Y,
         [0.65, 1.0]),
    ]
    card_w = 3.2
    card_h = 4.6
    x0 = 0.4
    gap = 0.15
    for i, (name, prev, curr, delta, color, bars) in enumerate(kpis):
        x = x0 + i * (card_w + gap)
        y = 1.3
        # panel
        _panel(ax, x, y, card_w, card_h, accent=color)
        # label
        ax.text(x + 0.3, y + card_h - 0.45, name,
                fontsize=11, fontweight="bold", color=DIM)
        # big number
        ax.text(x + card_w / 2, y + 2.85, curr,
                fontsize=44, fontweight="bold", color=color,
                ha="center", va="center",
                path_effects=[pe.withStroke(linewidth=4, foreground=PANEL)])
        # delta chip
        ax.add_patch(FancyBboxPatch((x + 0.3, y + 1.85), card_w - 0.6, 0.42,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=color, edgecolor=color, alpha=0.18))
        ax.text(x + card_w / 2, y + 2.06, delta,
                fontsize=11.5, fontweight="bold", color=color, ha="center",
                va="center")
        # mini comparison bar
        bar_y = y + 1.25
        bar_h = 0.28
        bar_x = x + 0.3
        bar_w = card_w - 0.6
        # 트랙 (배경)
        ax.add_patch(Rectangle((bar_x, bar_y), bar_w, bar_h,
                               facecolor=PANEL3, edgecolor="none", zorder=3))
        ax.add_patch(Rectangle((bar_x, bar_y - bar_h * 1.4),
                               bar_w, bar_h,
                               facecolor=PANEL3, edgecolor="none", zorder=3))
        # 값 막대
        ax.add_patch(Rectangle((bar_x, bar_y), bar_w * bars[0], bar_h,
                               facecolor=DIM, edgecolor="none", zorder=4))
        ax.add_patch(Rectangle((bar_x, bar_y - bar_h * 1.4),
                               bar_w * bars[1], bar_h,
                               facecolor=color, edgecolor="none", zorder=4))
        ax.text(bar_x, bar_y + bar_h + 0.05, "이전", fontsize=8.5,
                color=DIM)
        ax.text(bar_x, bar_y - bar_h * 1.4 - 0.22, "신규", fontsize=8.5,
                color=color)
        # prev label
        ax.text(x + card_w / 2, y + 0.4, prev, fontsize=9, color=DIM,
                ha="center", style="italic")

    ax.text(7, 0.45, "모든 KPI는 SMART (Specific · Measurable · Achievable · Relevant · Time-bound) 충족",
            fontsize=9.5, color=DIM, ha="center", style="italic")
    save(fig, "05_kpi_dashboard.png")


# ================================================================
#  6. 7대 레이어 — Hexagon 그리드
# ================================================================
def seven_layers():
    """Landscape redesign — 7 columns single row for full slide width fit."""
    fig, ax = _setup((16, 5.5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5.5)
    _title(ax, 8, 5.25, "7-Layer Defense-in-Depth",
           "Sentinel-30의 능동방어 7대 레이어")

    layers = [
        ("01", "AI 미끼봇", "멀티에이전트 LLM\n노인 페르소나 + TTS", NEON_O),
        ("02", "정보 수집 엔진", "음성지문·시나리오 8종\n계좌·URL 추출", NEON_B),
        ("03", "정보전 허브", "통신사·경찰망 신고\n(FDS는 추후)", NEON_S),
        ("04", "AI 자체 보안", "MITRE ATLAS\nOWASP LLM Top10", NEON_P),
        ("05", "IR 워크플로우", "금감원 24h 자동신고\nCISO 보고 자동화", NEON_B),
        ("06", "법적 안전지대", "6개 법령 검토\n8대 리스크 방어", NEON_Y),
        ("07", "시니어 UX", "70대 5명 인터뷰\n가족 동반 알림", NEON_R),
    ]
    # 7 columns × 1 row
    cols = 7
    gap = 0.18
    x0 = 0.35
    avail = 16 - 2 * x0
    cw = (avail - (cols - 1) * gap) / cols
    ch = 3.85
    y0 = 0.55

    for idx, (num, title, sub, c) in enumerate(layers):
        x = x0 + idx * (cw + gap)
        y = y0
        _panel(ax, x, y, cw, ch, accent=c)
        # large number — top right, 작게 + 더 흐리게 (제목과 겹침 회피)
        ax.text(x + cw - 0.2, y + ch - 0.28, num, fontsize=22,
                fontweight="bold", color=c, alpha=0.28, ha="right", va="top",
                family="monospace")
        # title — 번호 영역 침범 안 하도록 폭 제한
        ax.text(x + 0.25, y + ch - 0.40, title, fontsize=11.5,
                fontweight="bold", color=TEXT, va="top")
        # body
        ax.text(x + 0.25, y + 0.8, sub, fontsize=9, color=DIM, va="bottom",
                linespacing=1.45)
        # corner dot
        ax.add_patch(Circle((x + 0.3, y + 0.3), 0.09, facecolor=c,
                            edgecolor="none", alpha=0.9))
    save(fig, "06_seven_layers.png")


# ================================================================
#  7. 페르소나 카드 (라이트)
# ================================================================
def personas():
    fig, ax = _setup((16, 6.0))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 6.0)
    # 타이틀 — 카드 상단과 충분히 떨어지도록
    ax.text(8, 5.70, "Core Personas",
            fontsize=18, fontweight="bold", color=TEXT, ha="center")
    ax.text(8, 5.38, "타겟 사용자 3종 — 통화 흡수 전·중·후 관점",
            fontsize=10.5, color=DIM, ha="center")

    cards = [
        {"name": "박○○ (72세, 여)", "role": "주 피해 타겟", "color": NEON_Y,
         "avatar": "고령자",
         "pain": "검찰 사칭 통화 시 인지 트랜스에 빠짐\n자녀에게 연락 못 하고 송금",
         "needs": "큰 글씨 경고 + 자녀 자동 알림\n송금 직전 가족 거부권",
         "scenario": "검찰 사칭 → 미끼봇이 가로채\n자녀 푸시 → 5분 내 차단"},
        {"name": "김○○ (38세, 남)", "role": "은행 디지털보안 담당자", "color": NEON_B,
         "avatar": "은행",
         "pain": "FDS 룰 업데이트가 사후적\n환수 골든타임 항상 놓침",
         "needs": "사기범 계좌 실시간 자동 피드\n금감원 24h 자동 신고",
         "scenario": "허브 API 연동 → FDS 동결 검토\nIR 플레이북 자동 실행"},
        {"name": "이○○ (45세, 여)", "role": "고령 부모 둔 자녀", "color": NEON_S,
         "avatar": "자녀",
         "pain": "부모 통화 인지 불가\n사후 신고만 가능",
         "needs": "부모 위험 통화 실시간 푸시\n원격 송금 차단 권한",
         "scenario": "가디언 앱 알림 → 통화 가로채기\n가족 3자 통화 전환"},
    ]
    card_w = 4.9
    gap = 0.35
    x0 = (16 - 3 * card_w - 2 * gap) / 2

    for i, p in enumerate(cards):
        x = x0 + i * (card_w + gap)
        y = 0.25
        h = 4.75
        c = p["color"]
        _panel(ax, x, y, card_w, h, accent=c)

        # 큰 원 아바타
        ax.add_patch(Circle((x + card_w / 2, y + h - 0.9), 0.45,
                            facecolor=c, alpha=0.18, edgecolor=c,
                            linewidth=1.4, zorder=3))
        ax.text(x + card_w / 2, y + h - 0.9, p["avatar"],
                fontsize=11.5, fontweight="bold", color=c,
                ha="center", va="center", zorder=4)

        # 이름·역할
        ax.text(x + card_w / 2, y + h - 1.75, p["name"],
                fontsize=11.5, fontweight="bold", color=TEXT, ha="center")
        ax.text(x + card_w / 2, y + h - 2.05, p["role"],
                fontsize=9.5, color=c, ha="center", style="italic")

        # 3 섹션 — 카드 높이 4.75에 맞춤
        for label, body, yy, c2 in [
            ("PAIN POINT", p["pain"], y + h - 2.35, NEON_R),
            ("NEEDS", p["needs"], y + h - 3.20, NEON_S),
            ("SCENARIO", p["scenario"], y + h - 4.05, NEON_O),
        ]:
            ax.text(x + 0.35, yy, label, fontsize=8.5, fontweight="bold",
                    color=c2, family="monospace")
            ax.text(x + 0.35, yy - 0.35, body, fontsize=9.3, color=TEXT,
                    va="top", linespacing=1.4)
    save(fig, "07_personas.png")


# ================================================================
#  8. ROI 메커니즘 — 큰 수식 + 3 벡터
# ================================================================
def roi_mechanism():
    fig, ax = _setup((14, 7.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7.8)
    _title(ax, 7, 7.5, "Scam Industry ROI",
           "산업 ROI 분해 — 3개 공격 벡터")

    # 큰 수식
    ax.text(7, 6.3, "Revenue", fontsize=14, color=DIM, ha="center",
            family="monospace")
    ax.text(7, 5.55,
            "= [발신 통화 수] × [성공률] × [건당 피해액] - [운영 비용]",
            fontsize=14, color=TEXT, ha="center")

    # 3개 attack vector
    attacks = [
        (3.0, "통화 수", "DOWN", "미끼번호 풀이 사기범 발신을\n실제 피해자가 아닌 봇으로 흡수",
         NEON_B, "↓"),
        (7.0, "성공률", "DOWN", "미끼봇 정보 → 통신사·경찰망\n→ 송금 시도 차단",
         NEON_S, "↓"),
        (11.0, "운영 비용", "UP", "사기범 시간 30분~2h 흡수\n시간당 매출 감소",
         NEON_R, "↑"),
    ]
    for x, name, dir_label, desc, c, arrow in attacks:
        w = 3.3
        h = 2.7
        _panel(ax, x - w / 2, 1.6, w, h, accent=c)
        # 큰 화살표
        ax.text(x - 1.0, 1.6 + h - 0.7, arrow, fontsize=40,
                fontweight="bold", color=c, ha="center", va="center",
                path_effects=[pe.withStroke(linewidth=4, foreground=PANEL)])
        # name
        ax.text(x + 0.2, 1.6 + h - 0.65, name, fontsize=14, fontweight="bold",
                color=TEXT, va="center")
        ax.text(x + 0.2, 1.6 + h - 1.1, dir_label, fontsize=9.5,
                color=c, family="monospace", va="center")
        # desc
        ax.text(x, 1.6 + 0.65, desc, fontsize=9.5, color=DIM, ha="center",
                va="center", linespacing=1.4)
        # arrow from equation
        _neon_arrow(ax, x, 5.2, x, 1.6 + h + 0.05, color=c, lw=1.0)

    # 임팩트 결론
    ax.add_patch(FancyBboxPatch((1.5, 0.4), 11, 0.85,
                                boxstyle="round,pad=0.04,rounding_size=0.12",
                                facecolor=PANEL2, edgecolor=NEON_O,
                                linewidth=1.4))
    ax.text(7, 0.82,
            "산업의 시간당 매출이 0에 수렴할 때 사기 콜센터형 조직은 자연 감소",
            fontsize=12, fontweight="bold", color=NEON_O, ha="center",
            va="center")
    save(fig, "08_roi_mechanism.png")


# ================================================================
#  9. 간트차트 (라이트)
# ================================================================
def gantt():
    fig, ax = _setup((14, 7.5))
    ax.set_xlim(-0.3, 4.6)
    ax.set_ylim(-1, 9)
    _title(ax, 2.15, 8.5, "Project Timeline",
           "예선 4주 + 본선 무박 2일")

    tasks = [
        ("법리 검토서 작성", 0, 2, NEON_P),
        ("70대 사용성 인터뷰", 1, 2, NEON_B),
        ("멀티에이전트 봇 프로토타입", 1, 2.5, NEON_O),
        ("시연 영상 시안", 2, 1.5, NEON_Y),
        ("기획서 v1.0", 2, 1.5, NEON_S),
        ("최종 발표자료 + 시연 영상", 3, 1, NEON_O),
        ("적대적 공격 시연 준비", 3, 1, NEON_R),
    ]
    for i, (name, start, dur, c) in enumerate(tasks):
        y = len(tasks) - 1 - i
        # glow bar
        for w_pad, alpha in [(0.06, 0.18), (0.03, 0.32)]:
            ax.add_patch(FancyBboxPatch((start - w_pad, y - 0.32 - w_pad),
                                        dur + 2 * w_pad, 0.64 + 2 * w_pad,
                                        boxstyle="round,pad=0.01,rounding_size=0.06",
                                        facecolor=c, edgecolor="none",
                                        alpha=alpha))
        # main bar
        ax.add_patch(FancyBboxPatch((start, y - 0.32), dur, 0.64,
                                    boxstyle="round,pad=0.01,rounding_size=0.06",
                                    facecolor=c, edgecolor=c, alpha=0.95))
        ax.text(start + dur / 2, y, name, fontsize=10.5, color=BG,
                ha="center", va="center", fontweight="bold")

    # vertical milestone line (bar 우측 가장자리와 같은 x이므로 zorder 낮춰 뒤로)
    ax.axvline(4, color=NEON_O, linestyle="--", linewidth=1.6, alpha=0.85,
               zorder=0.3)
    ax.text(4.15, 7.5, "본선 무박 2일", fontsize=11, fontweight="bold",
            color=NEON_O)

    # week labels
    for x, lbl in zip([0, 1, 2, 3, 4], ["W1", "W2", "W3", "W4", "FINAL"]):
        ax.text(x, -0.6, lbl, fontsize=11, color=DIM,
                ha="center", family="monospace", fontweight="bold")
        if x < 4:
            ax.plot([x, x], [-0.4, 7], color=LINEC, linewidth=0.4, alpha=0.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    save(fig, "09_gantt.png")


# ================================================================
#  10. Multi-Agent (라이트)
# ================================================================
def multi_agent():
    """Landscape redesign — 16:6 aspect for slide content area fit.
    상단: 5종 에이전트 가로 배치 · 중단: Memory Compaction(좌) + IMPACT(우) ·
    하단: MODEL TIERING + PROBLEM 라인."""
    fig, ax = _setup((16, 6.2))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 6.2)

    # ─── 타이틀 ──────────────────────────────────────────────
    ax.text(8, 5.92, "Multi-Agent Architecture",
            fontsize=18, fontweight="bold", color=TEXT, ha="center")
    ax.text(8, 5.62, "통화 2시간에도 컨텍스트 한계 없음 · 토큰 비용 -62% · 응답 1.5초 이내",
            fontsize=10.5, color=DIM, ha="center")

    # ─── 상단: 5종 에이전트 가로 배치 (y 4.4 ± 0.95) ───────────
    agents = [
        ("Safety",     "Haiku",  "협박·실존정보 차단",      NEON_R, 1.7),
        ("Persona",    "Sonnet", "70대 노인 화법",         NEON_S, 4.6),
        ("Orchestrator","OPUS",  "응답 결정·분기",         NEON_O, 8.0),
        ("Memory",     "Sonnet", "5턴마다 요약 압축",       NEON_P, 11.4),
        ("Extractor",  "Sonnet", "계좌·URL·시나리오",      NEON_B, 14.3),
    ]
    ay = 4.40
    cx = 8.0
    for name, model, role, color, x in agents:
        if name == "Orchestrator":
            continue
        _neon_arrow(ax, cx, ay, x, ay, color=NEON_O, lw=1.2, alpha=0.5)

    for name, model, role, color, x in agents:
        is_center = (name == "Orchestrator")
        if is_center:
            for r, a in [(0.78, 0.07), (0.60, 0.13), (0.46, 0.20)]:
                ax.add_patch(Circle((x, ay), r, facecolor=color, alpha=a,
                                    edgecolor="none", zorder=3))
            ax.add_patch(Circle((x, ay), 0.38, facecolor=PANEL2,
                                edgecolor=color, linewidth=2.4, zorder=4))
        else:
            ax.add_patch(Circle((x, ay), 0.27, facecolor=PANEL2,
                                edgecolor=color, linewidth=1.8, zorder=4))
            ax.add_patch(Circle((x, ay + 0.03), 0.07, facecolor=color,
                                edgecolor="none", zorder=5))

        ax.text(x, ay + (0.78 if is_center else 0.58), name,
                fontsize=11 if is_center else 10, fontweight="bold",
                color=TEXT, ha="center", zorder=5)
        ax.text(x, ay - (0.72 if is_center else 0.55), model,
                fontsize=9.5 if is_center else 8.5, color=color,
                fontweight="bold", ha="center", zorder=5, family="monospace")
        ax.text(x, ay - (1.00 if is_center else 0.83), role,
                fontsize=8.5, color=DIM, ha="center", zorder=5)

    # ─── 중단 좌측: Memory Compaction timeline (x: 0.4 ~ 9.4) ───
    seq_y = 2.35
    seq_x0 = 0.4
    seq_w = 9.0
    boxes = [
        ("T1", "dim"), ("T2", "dim"), ("T3", "dim"), ("T4", "dim"), ("T5", "dim"),
        ("S1", "neon"),
        ("T6", "dim"), ("T7", "dim"), ("T8", "dim"), ("T9", "dim"), ("T10", "dim"),
        ("S2", "neon"),
        ("T11", "dim"), ("T12", "dim"),
    ]
    ax.text(seq_x0, seq_y + 0.65, "MEMORY COMPACTION",
            fontsize=9.5, fontweight="bold", color=NEON_O, family="monospace")
    ax.text(seq_x0 + 2.45, seq_y + 0.65, "5턴마다 요약(S) → 입력 토큰 일정",
            fontsize=9.5, color=DIM)
    bw = seq_w / len(boxes)
    for i, (lbl, kind) in enumerate(boxes):
        x = seq_x0 + i * bw
        if kind == "neon":
            for r, a in [(bw * 0.55, 0.15), (bw * 0.45, 0.25)]:
                ax.add_patch(Circle((x + bw / 2, seq_y + 0.20), r,
                                    facecolor=NEON_O, alpha=a, edgecolor="none"))
            ax.add_patch(FancyBboxPatch((x + 0.04, seq_y), bw - 0.08, 0.40,
                                        boxstyle="round,pad=0.01,rounding_size=0.05",
                                        facecolor=NEON_O, edgecolor=NEON_O,
                                        alpha=0.95))
            ax.text(x + bw / 2, seq_y + 0.20, lbl, fontsize=8.5,
                    color=BG, ha="center", va="center", fontweight="bold",
                    family="monospace")
        else:
            ax.add_patch(FancyBboxPatch((x + 0.04, seq_y), bw - 0.08, 0.40,
                                        boxstyle="round,pad=0.01,rounding_size=0.05",
                                        facecolor=PANEL2, edgecolor=LINEC,
                                        linewidth=0.8))
            ax.text(x + bw / 2, seq_y + 0.20, lbl, fontsize=8.2,
                    color=DIM, ha="center", va="center", family="monospace")
    ax.text(seq_x0, seq_y - 0.28,
            "Orchestrator 입력 = [요약본 + 최근 2턴] ~ 8K tokens (통화 길이 무관)",
            fontsize=9, color=DIM)

    # ─── 중단 우측: IMPACT 3 KPI 박스 (x: 9.8 ~ 15.6) ──────────
    impact_x = 9.8
    impact_w = 5.8
    _panel(ax, impact_x, 2.05, impact_w, 1.10)
    ax.text(impact_x + 0.25, 2.95, "IMPACT", fontsize=9.5, fontweight="bold",
            color=NEON_O, family="monospace")
    kpis = [
        (impact_x + 0.55, 2.40, "1.5s",  "응답 지연 상한", NEON_S),
        (impact_x + 2.40, 2.40, "-62%",  "토큰 비용",      NEON_O),
        (impact_x + 4.30, 2.40, "∞",     "통화 길이 무제한", NEON_B),
    ]
    for x, y, val, lbl, c in kpis:
        ax.text(x, y, val, fontsize=22, fontweight="bold", color=c,
                path_effects=[pe.withStroke(linewidth=3, foreground=PANEL)])
        ax.text(x, y - 0.35, lbl, fontsize=8.5, color=DIM)

    # ─── 하단: MODEL TIERING 가로 + PROBLEM 라인 ──────────────
    ax.text(0.4, 1.45, "MODEL TIERING", fontsize=9.5, fontweight="bold",
            color=NEON_O, family="monospace")
    tier_y = 0.85
    tiers = [
        ("OPUS",   "x1", NEON_O),
        ("SONNET", "x3", NEON_S),
        ("HAIKU",  "x1", NEON_B),
    ]
    tx = 0.4
    tier_w = 1.7
    for name, cnt, c in tiers:
        ax.add_patch(FancyBboxPatch((tx, tier_y), tier_w, 0.42,
                                    boxstyle="round,pad=0.02,rounding_size=0.06",
                                    facecolor=PANEL2, edgecolor=c, linewidth=1.2))
        ax.text(tx + 0.18, tier_y + 0.21, name, fontsize=9.5, color=c,
                fontweight="bold", family="monospace", va="center")
        ax.text(tx + tier_w - 0.15, tier_y + 0.21, cnt, fontsize=10, color=TEXT,
                fontweight="bold", ha="right", va="center", family="monospace")
        tx += tier_w + 0.18

    # PROBLEM 라인 (전체 폭 하단)
    _panel(ax, 0.4, 0.10, 15.2, 0.55)
    ax.text(0.65, 0.38, "PROBLEM", fontsize=8.5, fontweight="bold",
            color=NEON_R, family="monospace", va="center")
    ax.text(1.95, 0.38,
            "단일 LLM → 2h 통화 시 컨텍스트 200K 누적 → 응답 지연·환각·페르소나 붕괴",
            fontsize=9.5, color=TEXT, va="center")

    save(fig, "10_multi_agent.png")


# ================================================================
#  11. Fallback + Active Learning (라이트)
# ================================================================
def fallback_loop():
    """Landscape redesign — 16:6 aspect, 좌측 분류 흐름 + 우측 Active Learning 루프."""
    fig, ax = _setup((16, 6.0))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 6.0)
    ax.text(8, 5.75, "Fallback + Active Learning",
            fontsize=18, fontweight="bold", color=TEXT, ha="center")
    ax.text(8, 5.45, "예외 시나리오 처리와 자가 학습 루프",
            fontsize=10.5, color=DIM, ha="center")

    # ── 좌측: 분류 흐름 (x: 0.3 ~ 7.6) ───────────────────────
    # 1) 분류기
    cls_x, cls_y, cls_w, cls_h = 0.3, 3.85, 7.3, 1.15
    _panel(ax, cls_x, cls_y, cls_w, cls_h, accent=NEON_O)
    ax.text(cls_x + cls_w / 2, cls_y + cls_h - 0.30,
            "1차 시나리오 분류기 (8종)",
            fontsize=13, fontweight="bold", color=TEXT, ha="center")
    ax.text(cls_x + cls_w / 2, cls_y + cls_h - 0.62,
            "검찰·은행·자녀·택배·대출·세무서·경찰·보안업체",
            fontsize=9.5, color=DIM, ha="center")
    ax.text(cls_x + cls_w / 2, cls_y + 0.20,
            "confidence score (0.0 ~ 1.0)",
            fontsize=9.5, color=NEON_O, ha="center", family="monospace",
            fontweight="bold")

    # 2) 분기 라벨
    branch_y = 2.65
    branch_h = 1.05
    branch_l_x, branch_l_w = 0.3, 3.55
    branch_r_x, branch_r_w = 4.05, 3.55

    _neon_arrow(ax, cls_x + 1.5, cls_y, branch_l_x + branch_l_w / 2,
                branch_y + branch_h, color=NEON_S, lw=1.5)
    _neon_arrow(ax, cls_x + cls_w - 1.5, cls_y, branch_r_x + branch_r_w / 2,
                branch_y + branch_h, color=NEON_Y, lw=1.5)
    arrow_mid_y = (cls_y + branch_y + branch_h) / 2
    ax.text(branch_l_x + branch_l_w / 2 + 0.6, arrow_mid_y,
            ">= 0.6", fontsize=11, fontweight="bold",
            color=NEON_S, family="monospace",
            bbox=dict(facecolor=BG, edgecolor=NEON_S, boxstyle="round,pad=0.14",
                      linewidth=0.8))
    ax.text(branch_r_x + branch_r_w / 2 - 0.6, arrow_mid_y,
            "< 0.6", fontsize=11, fontweight="bold",
            color=NEON_Y, family="monospace",
            bbox=dict(facecolor=BG, edgecolor=NEON_Y, boxstyle="round,pad=0.14",
                      linewidth=0.8))

    # Known
    _panel(ax, branch_l_x, branch_y, branch_l_w, branch_h, accent=NEON_S)
    ax.text(branch_l_x + branch_l_w / 2, branch_y + branch_h - 0.30,
            "Known Scenario", fontsize=11.5, fontweight="bold",
            color=TEXT, ha="center")
    ax.text(branch_l_x + branch_l_w / 2, branch_y + branch_h - 0.60,
            "전용 페르소나 → 정보 추출 풀가동",
            fontsize=9.5, color=DIM, ha="center")
    ax.text(branch_l_x + branch_l_w / 2, branch_y + 0.20,
            "예: 검찰 → 무서워하는 노인", fontsize=9.5, color=NEON_S,
            ha="center", fontweight="bold")

    # Unknown
    _panel(ax, branch_r_x, branch_y, branch_r_w, branch_h, accent=NEON_Y)
    ax.text(branch_r_x + branch_r_w / 2, branch_y + branch_h - 0.30,
            "Unknown_Scam (fallback)", fontsize=11.5, fontweight="bold",
            color=TEXT, ha="center")
    ax.text(branch_r_x + branch_r_w / 2, branch_y + branch_h - 0.60,
            "일반 노인 페르소나 + 시간끌기",
            fontsize=9.5, color=DIM, ha="center")
    ax.text(branch_r_x + branch_r_w / 2, branch_y + 0.20,
            "전체 통화 녹취 + 메타 저장", fontsize=9.5, color=NEON_Y,
            ha="center", fontweight="bold")

    # 3) 정보 허브
    hub_y, hub_h = 1.30, 1.10
    _panel(ax, 0.3, hub_y, 7.3, hub_h, accent=NEON_B)
    ax.text(3.95, hub_y + hub_h - 0.30,
            "정보 허브 (통신사 · 경찰망 자동 신고)",
            fontsize=12, fontweight="bold", color=TEXT, ha="center")
    ax.text(3.95, hub_y + 0.25,
            "Known(자동 차단)  ·  Unknown(수동 검토 큐)",
            fontsize=10, color=DIM, ha="center")
    _neon_arrow(ax, branch_l_x + branch_l_w / 2, branch_y,
                3.95 - 0.5, hub_y + hub_h, color=NEON_S, lw=1.3)
    _neon_arrow(ax, branch_r_x + branch_r_w / 2, branch_y,
                3.95 + 0.5, hub_y + hub_h, color=NEON_Y, lw=1.3)

    # ── 우측: Active Learning Loop (x: 8.0 ~ 15.7) ──────────
    al_x, al_y, al_w, al_h = 8.0, 3.85, 7.7, 1.15
    _panel(ax, al_x, al_y, al_w, al_h, accent=NEON_P)
    ax.text(al_x + al_w / 2, al_y + al_h - 0.30,
            "Active Learning 루프 (주간 배치)",
            fontsize=13, fontweight="bold", color=TEXT, ha="center")
    ax.text(al_x + al_w / 2, al_y + al_h - 0.62,
            "Unknown_Scam 집계 → 클러스터링 → 라벨링 → 9번째 시나리오 등재",
            fontsize=9.5, color=DIM, ha="center")
    ax.text(al_x + al_w / 2, al_y + 0.20,
            "법무·운영 검토 → 분류기 재배포",
            fontsize=10, color=NEON_P, ha="center", fontweight="bold")

    # 4 step nodes — 가로로
    step_y = 2.55
    step_h = 1.35
    step_xs = [8.5, 10.30, 12.10, 13.90]
    step_w = 1.55
    steps_data = [
        ("1. 수집", "Unknown\n통화 전사"),
        ("2. 클러스터링", "LLM embedding\nHDBSCAN"),
        ("3. 라벨링", "운영자 검토\n시나리오 명명"),
        ("4. 재학습", "분류기 튜닝\n페르소나 추가"),
    ]
    for x, (title, body) in zip(step_xs, steps_data):
        ax.add_patch(FancyBboxPatch((x, step_y), step_w, step_h,
                                    boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor=PANEL2, edgecolor=NEON_P,
                                    linewidth=1.4, zorder=4))
        ax.text(x + step_w / 2, step_y + step_h - 0.25, title,
                fontsize=10.5, fontweight="bold", color=TEXT,
                ha="center", zorder=5)
        ax.text(x + step_w / 2, step_y + 0.35, body, fontsize=9,
                color=DIM, ha="center", va="center", zorder=5,
                linespacing=1.3)
    # 연결 화살표
    for i in range(3):
        x1 = step_xs[i] + step_w
        x2 = step_xs[i + 1]
        _neon_arrow(ax, x1, step_y + step_h / 2, x2, step_y + step_h / 2,
                    color=NEON_P, lw=1.3, glow=False)

    # 루프 back: step 4 → 분류기 (점선)
    back_y = 1.95
    last_x = step_xs[3] + step_w
    ax.plot([last_x, 15.5], [step_y + step_h / 2, step_y + step_h / 2],
            color=NEON_P, linewidth=1.3, linestyle=(0, (4, 3)))
    ax.plot([15.5, 15.5], [step_y + step_h / 2, back_y],
            color=NEON_P, linewidth=1.3, linestyle=(0, (4, 3)))
    ax.plot([15.5, cls_x + cls_w / 2], [back_y, back_y],
            color=NEON_P, linewidth=1.3, linestyle=(0, (4, 3)))
    ax.add_patch(FancyArrowPatch((cls_x + cls_w / 2, back_y),
                                 (cls_x + cls_w / 2, cls_y - 0.02),
                                 arrowstyle="-|>", mutation_scale=12,
                                 color=NEON_P, linewidth=1.3,
                                 linestyle=(0, (4, 3))))
    ax.text(11.6, 2.15, "분류기 업데이트 (월 1회 배포)",
            fontsize=10, fontweight="bold", color=NEON_P, ha="center")

    # ── 하단 결과 (전체 폭) ──────────────────────────────────
    _panel(ax, 0.3, 0.20, 15.4, 0.85, accent=NEON_O)
    ax.text(0.55, 0.78, "확장성 효과",
            fontsize=11, fontweight="bold", color=NEON_O, va="center")
    ax.text(0.55, 0.42,
            "8종 → 12종 → 16종 시나리오 자동 확장 · \"학습 안 된 사기\"도 통화는 끊지 않고 정보·신고로 흡수",
            fontsize=10, color=TEXT, va="center")
    save(fig, "11_fallback_loop.png")


# ================================================================
#  12. 본선 시연 화면 (라이트 3패널)
# ================================================================
def demo_layout():
    fig, ax = _setup((14, 8.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    _title(ax, 7, 8.7, "Live Demo Layout",
           "본선 라이브 시연 화면 — 3분할 동시 가시화")

    # 좌측: 사기범 음성
    _panel(ax, 0.3, 0.8, 4.3, 7.2, accent=NEON_O)
    ax.text(2.45, 7.5, "LEFT · 사기범 입력 음성",
            fontsize=11, fontweight="bold", color=NEON_O, ha="center")
    ax.text(2.45, 7.05, "(녹음 파일 재생)", fontsize=9, color=DIM, ha="center")

    # waveform with neon glow
    rng = np.random.default_rng(7)
    t = np.linspace(0.6, 4.0, 240)
    wave = (np.sin(t * 8) + 0.6 * np.sin(t * 15) + 0.4 * np.sin(t * 25)) * \
           (0.6 + 0.4 * np.sin(t * 0.5))
    wave *= rng.uniform(0.5, 1.0, size=len(t))
    # glow
    ax.plot(t, 5.0 + wave * 0.8, color=NEON_O, linewidth=3, alpha=0.18)
    ax.plot(t, 5.0 - wave * 0.8, color=NEON_O, linewidth=3, alpha=0.18)
    # main
    ax.plot(t, 5.0 + wave * 0.8, color=NEON_O, linewidth=1)
    ax.plot(t, 5.0 - wave * 0.8, color=NEON_O, linewidth=1)
    ax.fill_between(t, 5.0 - wave * 0.8, 5.0 + wave * 0.8,
                    color=NEON_O, alpha=0.18)

    # transcript box
    ax.add_patch(FancyBboxPatch((0.7, 2.5), 3.5, 1.3,
                                boxstyle="round,pad=0.03,rounding_size=0.08",
                                facecolor=PANEL2, edgecolor=NEON_O,
                                linewidth=1.2))
    ax.text(2.45, 3.45, "검찰입니다.", fontsize=10.5, color=TEXT,
            ha="center", style="italic")
    ax.text(2.45, 3.10, "김지수 씨 통장이...", fontsize=10.5, color=TEXT,
            ha="center", style="italic")
    ax.text(2.45, 2.7, "(시연용 더미 대본)", fontsize=8.5, color=DIM,
            ha="center")
    ax.text(2.45, 1.4, "PLAY 00:42 / 02:15", fontsize=11, fontweight="bold",
            color=TEXT, ha="center", family="monospace")

    # 중앙: 멀티에이전트 상태
    _panel(ax, 4.8, 0.8, 4.4, 7.2, accent=NEON_S)
    ax.text(7.0, 7.5, "CENTER · 멀티 에이전트 동작",
            fontsize=11, fontweight="bold", color=NEON_S, ha="center")
    ax.text(7.0, 7.05, "(처리 중인 에이전트가 발광)",
            fontsize=9, color=DIM, ha="center")

    agent_states = [
        ("Orchestrator", "Opus", "분기 결정 중", NEON_O, True),
        ("Persona", "Sonnet", "응답 생성", NEON_S, True),
        ("Memory", "Sonnet", "T+38 압축 완료", NEON_P, False),
        ("Extractor", "Sonnet", "계좌 추출 시도", NEON_B, True),
        ("Safety", "Haiku", "OK", NEON_R, False),
    ]
    for i, (name, model, state, c, active) in enumerate(agent_states):
        y = 6.0 - i * 1.0
        edge = c if active else DIM2
        alpha = 1.0 if active else 0.5
        # glow if active
        if active:
            for r, a in [(0.45, 0.10), (0.32, 0.20)]:
                ax.add_patch(Circle((5.45, y), r, facecolor=c, alpha=a,
                                    edgecolor="none"))
        # box
        ax.add_patch(FancyBboxPatch((5.2, y - 0.32), 3.6, 0.66,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=PANEL2, edgecolor=edge,
                                    linewidth=1.6 if active else 0.8))
        # status dot
        ax.add_patch(Circle((5.45, y), 0.10, facecolor=c if active else DIM2,
                            edgecolor="none"))
        ax.text(5.7, y + 0.10, name, fontsize=10, fontweight="bold",
                color=TEXT if active else DIM, va="center")
        ax.text(5.7, y - 0.13, f"[{model}]  {state}", fontsize=9,
                color=c if active else DIM, va="center", alpha=alpha)

    # 우측: 실시간 추출
    _panel(ax, 9.4, 0.8, 4.3, 7.2, accent=NEON_B)
    ax.text(11.55, 7.5, "RIGHT · 실시간 추출 결과",
            fontsize=11, fontweight="bold", color=NEON_B, ha="center")
    ax.text(11.55, 7.05, "(허브로 전송되는 데이터)",
            fontsize=9, color=DIM, ha="center")

    fields = [
        ("시나리오", "검찰 사칭", "98%", NEON_S),
        ("음성지문", "VP-3a8f...", "신규", NEON_O),
        ("계좌", "농협 301-XX", "검출", NEON_O),
        ("URL", "—", "—", DIM2),
        ("악성앱", "—", "—", DIM2),
        ("발신번호", "+82-10-XXXX", "변조 의심", NEON_R),
        ("통화시간", "00:42 → 진행", "", NEON_B),
    ]
    for i, (k, v, badge, c) in enumerate(fields):
        y = 6.3 - i * 0.65
        ax.add_patch(FancyBboxPatch((9.7, y - 0.22), 3.7, 0.5,
                                    boxstyle="round,pad=0.01,rounding_size=0.05",
                                    facecolor=PANEL2, edgecolor=LINEC,
                                    linewidth=0.6, zorder=3))
        ax.text(9.85, y, k, fontsize=9, fontweight="bold", color=DIM,
                va="center", zorder=5)
        ax.text(10.85, y, v, fontsize=9, color=TEXT, va="center", zorder=5)
        if badge and badge != "—":
            ax.add_patch(FancyBboxPatch((12.4, y - 0.16), 1.05, 0.32,
                                        boxstyle="round,pad=0.02,rounding_size=0.06",
                                        facecolor=c, edgecolor=c, alpha=0.92,
                                        zorder=4))
            ax.text(12.925, y, badge, fontsize=7.5, color=BG,
                    ha="center", va="center", fontweight="bold", zorder=5)

    ax.text(7, 0.4,
            "사기범 음성 → 멀티에이전트 동작 → 추출 결과 동시 가시화",
            fontsize=10.5, color=DIM, ha="center", style="italic")
    save(fig, "12_demo_layout.png")


# ================================================================
#  13. 데이터 수집 동의 분리 (라이트 2 패널)
# ================================================================
def consent_split():
    fig, ax = _setup((14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    _title(ax, 7, 8.7, "Data Collection Split",
           "사기범 측 vs 사용자 측 — 동의 모델 2분할")

    # A: 사기범 측
    _panel(ax, 0.3, 1.0, 6.6, 7.0, accent=NEON_O)
    ax.text(3.6, 7.6, "A.  사기범 측 수집", fontsize=14, fontweight="bold",
            color=TEXT, ha="center")
    ax.text(3.6, 7.18, "(미끼번호 → 사기범 발신)", fontsize=10.5, color=NEON_O,
            ha="center", style="italic")

    a_items = [
        ("데이터", "사기범 음성 · 계좌 · 시나리오"),
        ("동의 주체", "필요 없음"),
        ("법적 근거", "통신비밀보호법 §14 (1자 동의 원칙)"),
        ("판례", "대법원 2008도1237"),
        ("UX 요구", "없음 (사기범이 자발 발신)"),
    ]
    for i, (k, v) in enumerate(a_items):
        y = 6.2 - i * 1.05
        ax.add_patch(FancyBboxPatch((0.65, y - 0.4), 5.9, 0.92,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=PANEL2, edgecolor=LINEC,
                                    linewidth=0.6))
        ax.text(0.95, y + 0.18, k, fontsize=9.5, fontweight="bold",
                color=NEON_O, va="center")
        ax.text(0.95, y - 0.18, v, fontsize=10, color=TEXT, va="center")

    # B: 사용자 측
    _panel(ax, 7.1, 1.0, 6.6, 7.0, accent=NEON_B)
    ax.text(10.4, 7.6, "B.  사용자 측 수집", fontsize=14, fontweight="bold",
            color=TEXT, ha="center")
    ax.text(10.4, 7.18, "(시니어 가디언 앱 가입자)", fontsize=10.5, color=NEON_B,
            ha="center", style="italic")

    b_items = [
        ("데이터", "통화 메타데이터 + 위험 알림"),
        ("동의 주체", "본인 + (필요시) 자녀 보호자"),
        ("법적 근거", "개인정보보호법 §15 ①1호 (명시적 동의)"),
        ("동의 UX", "에이닷 모델 차용 — 가입 시 1회 + 철회 가능"),
        ("UX 요구", "고령자용 큰 글씨 동의서 · 음성 안내"),
    ]
    for i, (k, v) in enumerate(b_items):
        y = 6.2 - i * 1.05
        ax.add_patch(FancyBboxPatch((7.45, y - 0.4), 5.9, 0.92,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=PANEL2, edgecolor=LINEC,
                                    linewidth=0.6))
        ax.text(7.75, y + 0.18, k, fontsize=9.5, fontweight="bold",
                color=NEON_B, va="center")
        ax.text(7.75, y - 0.18, v, fontsize=10, color=TEXT, va="center")

    ax.text(7, 0.55,
            "→ 두 경로 분리로 \"미끼봇은 별도 동의 없이 합법 운용, 가디언 앱만 명시 동의\" 구조 확립",
            fontsize=10.5, fontweight="bold", color=NEON_O, ha="center")
    save(fig, "13_consent_split.png")


# ================================================================
#  14. Scope realization — 실구현 vs 로드맵 (라이트 2분할)
# ================================================================
def scope_realization():
    fig, ax = _setup((14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    _title(ax, 7, 8.7, "Implementation Scope",
           "이번 해커톤 실구현 vs v2 사업화 로드맵")

    # 좌측 실구현
    _panel(ax, 0.4, 0.8, 8.0, 7.2, accent=NEON_S)
    ax.text(4.4, 7.6, "LIVE DEMO  ·  실제 구현 4종",
            fontsize=13.5, fontweight="bold", color=NEON_S, ha="center")
    real = [
        ("01", "AI 미끼봇",
         "멀티에이전트 5종 + STT/TTS 파이프라인"),
        ("02", "정보 수집 엔진",
         "음성지문 DB + 시나리오 8종 분류 + 엔티티 추출"),
        ("03", "사기 시나리오 자동 분류",
         "8종 + Unknown fallback + Active Learning 루프"),
        ("04", "AI 자체 보안 계층",
         "MITRE ATLAS AML.T0043/T0048 + OWASP LLM Top10"),
    ]
    for i, (num, name, body) in enumerate(real):
        y = 6.5 - i * 1.35
        ax.add_patch(FancyBboxPatch((0.75, y - 0.5), 7.3, 1.15,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=PANEL2, edgecolor=LINEC,
                                    linewidth=0.6))
        # large number
        ax.text(1.4, y + 0.08, num, fontsize=28, fontweight="bold",
                color=NEON_S, alpha=0.85, ha="center", va="center",
                family="monospace")
        ax.text(2.3, y + 0.3, name, fontsize=12, fontweight="bold",
                color=TEXT, va="center")
        ax.text(2.3, y - 0.15, body, fontsize=9.5, color=DIM, va="center")
        # checkmark
        ax.add_patch(Circle((7.7, y + 0.08), 0.15, facecolor=NEON_S,
                            alpha=0.18, edgecolor=NEON_S, linewidth=1.2))
        ax.text(7.7, y + 0.08, "✓", fontsize=13, color=NEON_S,
                ha="center", va="center", fontweight="bold")

    # 우측 v2 로드맵
    _panel(ax, 8.7, 0.8, 5.0, 7.2)
    ax.text(11.2, 7.6, "추후 계획  ·  사업화 후",
            fontsize=13, fontweight="bold", color=DIM, ha="center")
    later = [
        ("FDS 실연계", "시중은행 PoC — 1차 타겟"),
        ("통신사 미끼번호 풀", "KT 후후·SKT 협력 — MoU 단계"),
        ("경찰청 사이버수사대 연계", "디지털성범죄대응팀 채널"),
        ("다국어 사기범 응대", "중국어·러시아어 (글로벌 거점)"),
        ("AML 자금세탁 영역 확장", "Hack-Back 아닌 정보전 확장"),
    ]
    for i, (name, body) in enumerate(later):
        y = 6.5 - i * 1.1
        ax.add_patch(FancyBboxPatch((9.0, y - 0.4), 4.5, 0.95,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=PANEL2, edgecolor=LINEC,
                                    linewidth=0.5))
        # round dot
        ax.add_patch(Circle((9.3, y), 0.08, facecolor=DIM,
                            edgecolor="none"))
        ax.text(9.55, y + 0.16, name, fontsize=10, fontweight="bold",
                color=DIM, va="center")
        ax.text(9.55, y - 0.18, body, fontsize=8.8, color=DIM2, va="center",
                style="italic")

    ax.text(7, 0.4,
            "발표·기획서는 \"오늘 동작하는 것\"과 \"내일 동작할 것\"을 명확히 구분",
            fontsize=10.5, color=DIM, ha="center", style="italic")
    save(fig, "14_scope_realization.png")


# ================================================================
#  17. 시니어 가디언 앱 와이어프레임 (라이트 + 폰 mock 2종)
# ================================================================
def wireframe_senior():
    """고령자(부모) 화면 + 자녀 화면 — 폰 mock 2장 나란히."""
    fig, ax = _setup((14, 9.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    _title(ax, 7, 9.6, "Senior Guardian — Wireframe",
           "70대 5명 인터뷰 기반 · 한 화면 한 행동 원칙")

    def phone_frame(cx, cy, w=4.3, h=7.6, title=None, accent=NEON_O):
        """폰 외곽 + notch."""
        # outer frame
        ax.add_patch(FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.32",
                                    facecolor="#000000", edgecolor=LINEC,
                                    linewidth=1.4, zorder=2))
        # screen
        ax.add_patch(FancyBboxPatch((cx - w/2 + 0.12, cy - h/2 + 0.18),
                                    w - 0.24, h - 0.36,
                                    boxstyle="round,pad=0.01,rounding_size=0.22",
                                    facecolor=PANEL, edgecolor=accent,
                                    linewidth=0.8, zorder=2.5))
        # notch
        ax.add_patch(FancyBboxPatch((cx - 0.45, cy + h/2 - 0.32), 0.9, 0.18,
                                    boxstyle="round,pad=0.01,rounding_size=0.08",
                                    facecolor="#000000", edgecolor="none",
                                    zorder=3))
        # bottom home indicator
        ax.add_patch(FancyBboxPatch((cx - 0.55, cy - h/2 + 0.07), 1.1, 0.04,
                                    boxstyle="round,pad=0.005,rounding_size=0.02",
                                    facecolor=DIM2, edgecolor="none", zorder=3))
        if title:
            ax.text(cx, cy + h/2 + 0.35, title, fontsize=12.5,
                    fontweight="bold", color=accent, ha="center")

    def btn(cx, cy, w, h, label, c, sub=None, big=False):
        ax.add_patch(FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                                    boxstyle="round,pad=0.02,rounding_size=0.10",
                                    facecolor=c, edgecolor="none",
                                    alpha=0.92, zorder=4))
        ax.text(cx, cy + (0.08 if sub else 0), label,
                fontsize=14 if big else 11.5, fontweight="bold",
                color="#000000" if c in (NEON_Y,) else "#ffffff",
                ha="center", va="center", zorder=5)
        if sub:
            ax.text(cx, cy - 0.16, sub, fontsize=8.5,
                    color="#000000" if c in (NEON_Y,) else "#ffffff",
                    alpha=0.85, ha="center", va="center", zorder=5)

    # ---------------- 좌: 고령자(부모) 화면 ----------------
    cx_a = 3.3
    cy_a = 5.0
    phone_frame(cx_a, cy_a, title="A · 고령자 화면 (72세 박○○)", accent=NEON_R)

    # 상단 상태 — 위험 표시
    ax.add_patch(FancyBboxPatch((cx_a - 1.85, cy_a + 2.5), 3.7, 0.85,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor=NEON_R, edgecolor="none", alpha=0.95, zorder=4))
    ax.text(cx_a, cy_a + 3.05, "위험 통화 차단됨", fontsize=15,
            fontweight="bold", color="#ffffff", ha="center", zorder=5)
    ax.text(cx_a, cy_a + 2.72, "검찰 사칭 · 98% 사기 의심", fontsize=9.5,
            color="#ffffff", ha="center", alpha=0.92, zorder=5)

    # 큰 안내 텍스트 (28pt 시뮬레이션 — 시각상 큰 글씨)
    ax.text(cx_a, cy_a + 1.85, "절대 돈을 보내지", fontsize=15,
            fontweight="bold", color=TEXT, ha="center", zorder=5)
    ax.text(cx_a, cy_a + 1.45, "마세요", fontsize=15,
            fontweight="bold", color=TEXT, ha="center", zorder=5)
    ax.text(cx_a, cy_a + 1.05, "(음성 안내 동시 송출)", fontsize=8.5,
            color=DIM, ha="center", style="italic", zorder=5)

    # 자녀 알림 카드
    ax.add_patch(FancyBboxPatch((cx_a - 1.85, cy_a + 0.10), 3.7, 0.78,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=PANEL2, edgecolor=NEON_S,
                                linewidth=0.8, zorder=4))
    ax.add_patch(Circle((cx_a - 1.62, cy_a + 0.55), 0.16,
                        facecolor=NEON_S, edgecolor="none", alpha=0.9, zorder=5))
    ax.text(cx_a - 1.62, cy_a + 0.55, "v", fontsize=10, fontweight="bold",
            color="#0d0d0c", ha="center", va="center", zorder=6)
    ax.text(cx_a - 1.35, cy_a + 0.62, "딸 이○○에게 자동 알림",
            fontsize=10, fontweight="bold", color=TEXT, ha="left", zorder=5)
    ax.text(cx_a - 1.35, cy_a + 0.28, "방금 발송 · 응답 대기 중",
            fontsize=8.3, color=DIM, ha="left", zorder=5)

    # 큰 단일 행동 버튼
    btn(cx_a, cy_a - 0.85, 3.5, 0.95, "지금 통화 끊기", NEON_R, big=True)

    # 보조 버튼
    btn(cx_a - 0.9, cy_a - 2.0, 1.55, 0.6, "자녀에게 전화", NEON_S)
    btn(cx_a + 0.9, cy_a - 2.0, 1.55, 0.6, "112 신고", NEON_B)

    # 푸터
    ax.text(cx_a, cy_a - 2.78, "Sentinel-30 보호 중 · AI 사용 안내됨",
            fontsize=7.5, color=DIM, ha="center", zorder=5)

    # ---------------- 우: 자녀 화면 ----------------
    cx_b = 10.7
    cy_b = 5.0
    phone_frame(cx_b, cy_b, title="B · 자녀 화면 (45세 이○○)", accent=NEON_S)

    # 상단 푸시
    ax.add_patch(FancyBboxPatch((cx_b - 1.85, cy_b + 2.5), 3.7, 0.85,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor=NEON_S, edgecolor="none", alpha=0.92, zorder=4))
    ax.text(cx_b, cy_b + 3.05, "부모 위험 통화 감지", fontsize=14,
            fontweight="bold", color="#0d0d0c", ha="center", zorder=5)
    ax.text(cx_b, cy_b + 2.72, "박○○ 어머니 · 14:32 · 진행 5분 12초", fontsize=9.0,
            color="#0d0d0c", ha="center", alpha=0.92, zorder=5)

    # 위험도 미터
    ax.text(cx_b - 1.7, cy_b + 1.95, "위험도", fontsize=9.5, color=DIM,
            ha="left", zorder=5)
    ax.add_patch(FancyBboxPatch((cx_b - 1.85, cy_b + 1.40), 3.7, 0.28,
                                boxstyle="round,pad=0.005,rounding_size=0.06",
                                facecolor=PANEL2, edgecolor=LINEC, linewidth=0.6, zorder=4))
    # 98% 채움
    ax.add_patch(FancyBboxPatch((cx_b - 1.85, cy_b + 1.40), 3.7 * 0.98, 0.28,
                                boxstyle="round,pad=0.005,rounding_size=0.06",
                                facecolor=NEON_R, edgecolor="none", alpha=0.9, zorder=4.5))
    ax.text(cx_b + 1.6, cy_b + 1.54, "98%", fontsize=10,
            fontweight="bold", color="#ffffff", ha="right", zorder=5)

    # 시나리오 라벨
    ax.text(cx_b - 1.7, cy_b + 0.95, "유형 · 검찰 사칭", fontsize=10,
            color=TEXT, ha="left", zorder=5)
    ax.text(cx_b - 1.7, cy_b + 0.60, "추출 · 농협 301-XXXX · 1.2억 송금 요구",
            fontsize=8.7, color=DIM, ha="left", zorder=5)

    # 행동 버튼 (4종 그리드)
    btn(cx_b - 0.9, cy_b - 0.30, 1.55, 0.75, "송금 차단", NEON_R,
        sub="원격으로 차단")
    btn(cx_b + 0.9, cy_b - 0.30, 1.55, 0.75, "3자 합류", NEON_O,
        sub="가족 통화 전환")
    btn(cx_b - 0.9, cy_b - 1.30, 1.55, 0.75, "통화 종료", NEON_B,
        sub="부모 자동 차단")
    btn(cx_b + 0.9, cy_b - 1.30, 1.55, 0.75, "신고 접수", NEON_Y,
        sub="경찰·금감원")

    # 푸터: 통화 요약
    ax.add_patch(FancyBboxPatch((cx_b - 1.85, cy_b - 2.55), 3.7, 0.55,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=PANEL2, edgecolor=LINEC,
                                linewidth=0.6, zorder=4))
    ax.text(cx_b, cy_b - 2.27, "통화 요약 보기  >", fontsize=9.5,
            color=NEON_B, ha="center", zorder=5)

    # 하단 캡션
    ax.text(7, 0.45,
            "원칙: 한 화면 한 행동 · 28pt 이상 · 음성 안내 동시 · "
            "FCM+SMS 이중화 푸시 5초 이내 도달",
            fontsize=10, color=DIM, ha="center", style="italic")
    save(fig, "17_wireframe_senior.png")


# ================================================================
#  Slide 3 보강 — 연도별 피해액 추이 + 기관사칭 비중 도넛
# ================================================================
def chart_problem_trend():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5),
                                    gridspec_kw={"width_ratios": [1.4, 1]})
    fig.patch.set_facecolor(BG)
    for a in (ax1, ax2):
        a.set_facecolor(BG)
        for s in a.spines.values():
            s.set_visible(False)

    # 좌: 연도별 피해액 막대 (2020~2024)
    years = ["2020", "2021", "2022", "2023", "2024"]
    values = [7_000, 7_744, 5_438, 4_472, 8_545]  # 단위: 억 원
    colors_b = [NEON_B, NEON_B, NEON_B, NEON_B, NEON_R]
    bars = ax1.bar(years, values, color=colors_b, width=0.55,
                   edgecolor="none", zorder=3)
    for bar, v in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 200, f"{v:,}",
                 ha="center", fontsize=12, color=TEXT, fontweight="bold")
    ax1.set_ylim(0, 10_200)
    ax1.set_yticks([0, 2000, 4000, 6000, 8000])
    ax1.set_yticklabels(["0", "2,000", "4,000", "6,000", "8,000"],
                        fontsize=9.5, color=DIM)
    ax1.tick_params(axis="x", labelsize=11, colors=TEXT, pad=6)
    ax1.tick_params(axis="y", colors=DIM)
    ax1.grid(axis="y", color=LINEC, linewidth=0.6, alpha=0.7, zorder=1)
    ax1.set_axisbelow(True)
    ax1.set_title("연도별 보이스피싱 피해액 (억 원)",
                  fontsize=13, color=TEXT, fontweight="bold",
                  loc="left", pad=14)
    ax1.text(0, -1700, "출처: 경찰청 — 2024년 8,545억으로 역대 최고",
             fontsize=9.5, color=DIM)

    # 우: 도넛 — 유형별 비중
    sizes = [75, 17, 8]
    labels = ["기관사칭형", "대출빙자형", "기타"]
    cols = [NEON_R, NEON_O, DIM2]
    wedges, _ = ax2.pie(sizes, colors=cols, startangle=90,
                        counterclock=False,
                        wedgeprops=dict(width=0.32, edgecolor=BG, linewidth=3))
    # 가운데 큰 숫자
    ax2.text(0, 0.08, "75%", fontsize=36, fontweight="bold",
             color=NEON_R, ha="center", va="center")
    ax2.text(0, -0.22, "기관사칭형", fontsize=11, color=TEXT,
             ha="center", va="center", fontweight="bold")
    ax2.text(0, -0.36, "5,867억", fontsize=9.5, color=DIM,
             ha="center", va="center")
    # 우측 라벨
    yy = 1.1
    for label, sz, col in zip(labels, sizes, cols):
        ax2.scatter(1.35, yy, s=80, c=col, zorder=5)
        ax2.text(1.48, yy, f"{label}  {sz}%", fontsize=10.5,
                 color=TEXT, va="center")
        yy -= 0.32
    ax2.set_xlim(-1.4, 2.6)
    ax2.set_ylim(-1.5, 1.4)
    ax2.set_aspect("equal")
    ax2.set_title("유형별 피해 비중 (2024)",
                  fontsize=13, color=TEXT, fontweight="bold",
                  loc="left", pad=14, x=-0.1)

    fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.14,
                        wspace=0.30)
    save(fig, "chart_problem_trend.png")


# ================================================================
#  Slide 23 보강 — Impact Before / After 비교 막대
# ================================================================
def chart_impact_comparison():
    fig, ax = plt.subplots(figsize=(14, 5.0))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_visible(False)

    # 4개 지표 — 환급법 효과 + Sentinel-30 효과 누적
    categories = ["보이스피싱\n피해액 (억)", "60대 피해\n비중 (%)",
                  "환수 골든\n타임 (분)", "법정 신고\n충족 (%)"]
    base = [8545, 52.3, 240, 65]
    after_law = [6664, 41.8, 240, 65]  # 환급법만 -22%
    after_full = [6131, 31.4, 30, 100]   # +Sentinel-30
    # 정규화 (각 카테고리 기준 max = 100)
    norm_base = [100, 100, 100, 100]
    norm_law = [a/b*100 for a, b in zip(after_law, base)]
    norm_full = [a/b*100 for a, b in zip(after_full, base)]

    import numpy as np
    x = np.arange(len(categories))
    w = 0.27
    b1 = ax.bar(x - w, norm_base, w, label="현재 (2024)",
                color=DIM2, edgecolor="none", zorder=3)
    b2 = ax.bar(x,     norm_law,  w, label="환급법 시행 후 (-22~35%)",
                color=NEON_B, edgecolor="none", zorder=3)
    b3 = ax.bar(x + w, norm_full, w, label="+ Sentinel-30 (증분 효과)",
                color=NEON_O, edgecolor="none", zorder=3)

    # 위에 실제 수치 라벨
    for bars, vals in [(b1, base), (b2, after_law), (b3, after_full)]:
        for bar, v in zip(bars, vals):
            label = f"{v:,}" if v >= 100 else f"{v}"
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 2.5, label,
                    ha="center", fontsize=9, color=TEXT)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11, color=TEXT)
    ax.set_ylim(0, 175)
    ax.set_yticks([0, 50, 100, 150])
    ax.set_yticklabels(["0", "50", "100", "150"],
                       fontsize=9, color=DIM)
    ax.set_ylabel("현재(2024) = 100 기준 정규화", fontsize=10, color=DIM)
    ax.axhline(100, color=LINEC, linewidth=0.6, linestyle="--", zorder=1)
    ax.grid(axis="y", color=LINEC, linewidth=0.6, alpha=0.7, zorder=1)
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", frameon=False, fontsize=10,
              labelcolor=TEXT, ncol=3, bbox_to_anchor=(1, 1.08))
    ax.set_title("환급법 시행 효과 위에 누적되는 Sentinel-30 증분 효과",
                 fontsize=13, color=TEXT, fontweight="bold",
                 loc="left", pad=20)

    fig.subplots_adjust(left=0.06, right=0.98, top=0.85, bottom=0.16)
    save(fig, "chart_impact_comparison.png")


# ================================================================
#  Slide 16 보강 — 운영비 항목별 도넛 + 합계
# ================================================================
def chart_cost_donut():
    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    items = [
        ("Orchestrator (Opus)", 1400, NEON_R),
        ("Persona/Extractor (Sonnet)", 420, NEON_O),
        ("TTS (노년 음성)", 240, NEON_B),
        ("STT (Whisper)", 90, NEON_S),
        ("Memory Compactor (Haiku)", 90, NEON_P),
    ]
    sizes = [v for _, v, _ in items]
    cols = [c for _, _, c in items]
    labels = [n for n, _, _ in items]
    total = sum(sizes)

    wedges, _ = ax.pie(sizes, colors=cols, startangle=90,
                       counterclock=False,
                       wedgeprops=dict(width=0.30, edgecolor=BG, linewidth=3))
    ax.text(0, 0.10, f"{total:,}원", fontsize=24, fontweight="bold",
            color=TEXT, ha="center", va="center")
    ax.text(0, -0.18, "30분 통화 1건", fontsize=11, color=DIM,
            ha="center", va="center")

    # 라벨 우측에 정렬
    yy = 1.05
    for label, sz, col in zip(labels, sizes, cols):
        pct = sz/total*100
        ax.scatter(1.35, yy, s=70, c=col, zorder=5)
        ax.text(1.48, yy + 0.04, label, fontsize=9.5, color=TEXT, va="center")
        ax.text(1.48, yy - 0.10, f"{sz:,}원 · {pct:.0f}%",
                fontsize=9, color=DIM, va="center")
        yy -= 0.35

    ax.set_xlim(-1.4, 3.0)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)
    save(fig, "chart_cost_donut.png")


# ================================================================
#  Slide 4 보강 — 시장 포지셔닝 맵 (2D)
# ================================================================
def chart_market_position():
    fig, ax = plt.subplots(figsize=(12, 7.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # 4사분면 — X: B2B(기관) ↔ B2C(개인 사용자), Y: 정보 공유 ↔ 통화 시점
    # 4개 영역 옅은 배경
    for x0, y0, w, h, col in [
        (-1.05, -0.05, 1.05, 1.10, "#f4ecd6"),
        (0, -0.05, 1.05, 1.10, "#f1dccd"),
        (-1.05, -1.05, 1.05, 1.00, "#eef2e8"),
        (0, -1.05, 1.05, 1.00, "#f7f4ed"),
    ]:
        ax.add_patch(Rectangle((x0, y0), w, h, facecolor=col,
                               edgecolor="none", alpha=0.6, zorder=1))

    # 축
    ax.axhline(0, color=LINEC, linewidth=1.2, zorder=2)
    ax.axvline(0, color=LINEC, linewidth=1.2, zorder=2)

    # 점 (이름, x, y, 컬러, 사이즈)
    players = [
        ("정부 통합대응단", -0.78,  0.82, NEON_R, 700),
        ("ASAP (금감원)",   -0.50,  0.55, NEON_B, 950),
        ("AIVOSS (국과수)", -0.65, -0.55, NEON_P, 750),
        ("KT 후후",          0.55,  0.28, NEON_S, 700),
        ("SKT 에이닷\n(가족 케어)", 0.42,  0.55, NEON_S, 750),
        ("LG 익시오",        0.72,  0.20, NEON_S, 700),
        ("SKT 언더커버봇",   -0.30, -0.30, NEON_P, 750),
        ("메타크라우드",     0.45, -0.45, "#a06a8d", 700),
        ("시티즌코난",       0.20, -0.75, NEON_Y, 550),
        ("Sentinel-30",      0.78,  0.82, NEON_O, 1500),
    ]
    for name, x, y, c, s in players:
        ax.scatter(x, y, s=s, c=c, alpha=0.85, edgecolor="white",
                   linewidth=2.0, zorder=4)
        # 라벨 위/아래 자동
        offset_y = 0.10 if name != "Sentinel-30" else 0.13
        weight = "bold" if name == "Sentinel-30" else "normal"
        fs = 9.5 if "\n" in name else 10.5
        ax.text(x, y + offset_y, name, fontsize=fs,
                color=TEXT if name != "Sentinel-30" else NEON_O,
                ha="center", va="bottom", fontweight=weight, zorder=5,
                linespacing=1.1)

    # 축 라벨
    ax.text(1.07, 0, "개인 사용자 (B2C)", fontsize=11, color=DIM,
            va="center", ha="left", fontweight="bold")
    ax.text(-1.07, 0, "기관 (B2B)", fontsize=11, color=DIM,
            va="center", ha="right", fontweight="bold")
    ax.text(0, 1.10, "통화 시점 대응", fontsize=11, color=DIM,
            ha="center", va="bottom", fontweight="bold")
    ax.text(0, -1.10, "사후 정보 공유", fontsize=11, color=DIM,
            ha="center", va="top", fontweight="bold")

    # 4사분면 텍스트 (옅게)
    ax.text(-0.95, 1.0, "B2B · 통화 시점", fontsize=9, color=DIM2, alpha=0.7)
    ax.text(0.05, 1.0, "B2C · 통화 시점", fontsize=9, color=DIM2, alpha=0.7)
    ax.text(-0.95, -1.0, "B2B · 사후 공유", fontsize=9, color=DIM2, alpha=0.7)
    ax.text(0.05, -1.0, "B2C · 사후 공유", fontsize=9, color=DIM2, alpha=0.7)

    ax.set_xlim(-1.15, 1.55)
    ax.set_ylim(-1.20, 1.25)
    ax.set_aspect("auto")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    ax.set_title("보이스피싱 대응 시장 포지셔닝 — 비어있는 'B2C × 통화 시점' 영역",
                 fontsize=13, color=TEXT, fontweight="bold",
                 loc="left", pad=18)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.90, bottom=0.06)
    save(fig, "chart_market_position.png")


def _ios_phone_frame(ax, x, y, w, h):
    """iOS 14 Pro 스타일 폰 베젤 (Dynamic Island + 둥근 모서리)."""
    bezel = FancyBboxPatch((x, y), w, h,
                            boxstyle="round,pad=0.0,rounding_size=0.35",
                            facecolor="#1c1815", edgecolor="#0e0c0a",
                            linewidth=1.2)
    ax.add_patch(bezel)
    pad = 0.10
    sx, sy = x + pad, y + pad
    sw, sh = w - 2*pad, h - 2*pad
    screen = FancyBboxPatch((sx, sy), sw, sh,
                             boxstyle="round,pad=0.0,rounding_size=0.28",
                             facecolor="#f7f5ef", edgecolor="none")
    ax.add_patch(screen)
    island_w = sw * 0.32
    island_h = 0.16
    island_x = sx + (sw - island_w)/2
    island_y = sy + sh - island_h - 0.08
    ax.add_patch(FancyBboxPatch((island_x, island_y), island_w, island_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.08",
                                 facecolor="#0e0c0a", edgecolor="none"))
    ax.text(sx + 0.16, sy + sh - 0.08, "9:41",
            fontsize=6.5, color=TEXT, fontweight="bold", va="center")
    ax.text(sx + sw - 0.16, sy + sh - 0.08, "•••  ●●●  ▮",
            fontsize=5.5, color=DIM, ha="right", va="center")
    hi_w = sw * 0.32
    hi_h = 0.04
    ax.add_patch(FancyBboxPatch((sx + (sw - hi_w)/2, sy + 0.04),
                                 hi_w, hi_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.02",
                                 facecolor="#0e0c0a", edgecolor="none"))
    return sx, sy, sw, sh


def senior_app_mockup():
    """Toss/Kakao 시니어 친화 UI 4 화면 mockup — 16:7 landscape."""
    fig, ax = _setup((16, 7.5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 7.5)
    ax.text(8, 7.20, "시니어 가디언 앱 — 자녀용 핵심 4화면",
            fontsize=18, fontweight="bold", color=TEXT, ha="center")
    ax.text(8, 6.85,
            "React Native iOS/Android · Toss·Kakao 스타일 큰 글씨 · 한 화면 한 행동 원칙",
            fontsize=10.5, color=DIM, ha="center")

    phone_w = 3.30
    phone_h = 6.10
    gap = 0.50
    total_w = 4*phone_w + 3*gap
    x0 = (16 - total_w)/2

    # === 화면 1: 홈 (부모 카드 리스트) ===
    px = x0; py = 0.30
    sx, sy, sw, sh = _ios_phone_frame(ax, px, py, phone_w, phone_h)
    ax.text(sx + 0.18, sy + sh - 0.45, "내 가족",
            fontsize=14, fontweight="bold", color=TEXT, va="center")
    ax.text(sx + sw - 0.18, sy + sh - 0.45, "⚙",
            fontsize=12, color=DIM, ha="right", va="center")
    card1_y = sy + sh - 1.70
    card_h = 1.45
    ax.add_patch(FancyBboxPatch((sx + 0.18, card1_y), sw - 0.36, card_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.10",
                                 facecolor="white", edgecolor=LINEC, linewidth=0.8))
    ax.add_patch(Rectangle((sx + 0.18, card1_y), 0.08, card_h,
                            facecolor=NEON_S, edgecolor="none"))
    ax.text(sx + 0.36, card1_y + card_h - 0.30, "박○○ 어머니",
            fontsize=12, fontweight="bold", color=TEXT)
    ax.text(sx + 0.36, card1_y + card_h - 0.55, "72세 · 강남구",
            fontsize=9, color=DIM)
    ax.add_patch(Circle((sx + 0.42, card1_y + 0.55), 0.07,
                        facecolor=NEON_S, edgecolor="none"))
    ax.text(sx + 0.55, card1_y + 0.55, "안전",
            fontsize=10, fontweight="bold", color=NEON_S, va="center")
    ax.text(sx + sw - 0.36, card1_y + 0.55, "최근 통화 12:34",
            fontsize=8.5, color=DIM, ha="right", va="center")
    ax.text(sx + 0.36, card1_y + 0.25, "위험도 0%  ·  최근 30일 차단 0건",
            fontsize=8.5, color=DIM)
    card2_y = card1_y - 1.65
    ax.add_patch(FancyBboxPatch((sx + 0.18, card2_y), sw - 0.36, card_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.10",
                                 facecolor="white", edgecolor=LINEC, linewidth=0.8))
    ax.add_patch(Rectangle((sx + 0.18, card2_y), 0.08, card_h,
                            facecolor=NEON_S, edgecolor="none"))
    ax.text(sx + 0.36, card2_y + card_h - 0.30, "이○○ 아버지",
            fontsize=12, fontweight="bold", color=TEXT)
    ax.text(sx + 0.36, card2_y + card_h - 0.55, "75세 · 서초구",
            fontsize=9, color=DIM)
    ax.add_patch(Circle((sx + 0.42, card2_y + 0.55), 0.07,
                        facecolor=NEON_S, edgecolor="none"))
    ax.text(sx + 0.55, card2_y + 0.55, "안전",
            fontsize=10, fontweight="bold", color=NEON_S, va="center")
    ax.text(sx + sw - 0.36, card2_y + 0.55, "최근 통화 어제",
            fontsize=8.5, color=DIM, ha="right", va="center")
    ax.text(sx + 0.36, card2_y + 0.25, "위험도 0%  ·  최근 30일 차단 0건",
            fontsize=8.5, color=DIM)
    btn_y = sy + 0.50
    btn_h = 0.55
    ax.add_patch(FancyBboxPatch((sx + 0.18, btn_y), sw - 0.36, btn_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.12",
                                 facecolor=NEON_B, edgecolor="none"))
    ax.text(sx + sw/2, btn_y + btn_h/2, "+  부모 추가하기",
            fontsize=12, fontweight="bold", color="white",
            ha="center", va="center")
    ax.text(px + phone_w/2, py - 0.05, "①  홈 — 부모 카드",
            fontsize=10.5, fontweight="bold", color=NEON_B,
            ha="center", va="top")

    # === 화면 2: 위험 통화 감지 ===
    px = x0 + (phone_w + gap); py = 0.30
    sx, sy, sw, sh = _ios_phone_frame(ax, px, py, phone_w, phone_h)
    alert_h = 0.50
    ax.add_patch(FancyBboxPatch((sx + 0.10, sy + sh - alert_h - 0.45),
                                 sw - 0.20, alert_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.10",
                                 facecolor=NEON_R, edgecolor="none"))
    ax.text(sx + sw/2, sy + sh - 0.45 - alert_h/2,
            "⚠  부모 위험 통화 감지",
            fontsize=11, fontweight="bold", color="white",
            ha="center", va="center")
    ax.text(sx + sw/2, sy + sh - 1.40, "박○○ 어머니",
            fontsize=14, fontweight="bold", color=TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 1.70, "진행 5분 12초",
            fontsize=9.5, color=DIM, ha="center")
    risk_cx = sx + sw/2; risk_cy = sy + sh - 3.0
    for r, a in [(0.78, 0.12), (0.62, 0.20)]:
        ax.add_patch(Circle((risk_cx, risk_cy), r, facecolor=NEON_R,
                            alpha=a, edgecolor="none"))
    ax.add_patch(Circle((risk_cx, risk_cy), 0.50, facecolor="white",
                        edgecolor=NEON_R, linewidth=2.2))
    ax.text(risk_cx, risk_cy + 0.06, "98%",
            fontsize=18, fontweight="bold", color=NEON_R,
            ha="center", va="center")
    ax.text(risk_cx, risk_cy - 0.22, "위험도",
            fontsize=8, color=DIM, ha="center", va="center")
    ax.add_patch(FancyBboxPatch((sx + 0.18, sy + sh - 4.50),
                                 sw - 0.36, 0.85,
                                 boxstyle="round,pad=0.0,rounding_size=0.08",
                                 facecolor="white", edgecolor=LINEC, linewidth=0.7))
    ax.text(sx + 0.30, sy + sh - 3.85, "유형",
            fontsize=8, color=DIM)
    ax.text(sx + 0.30, sy + sh - 4.10, "검찰 사칭 (T0043)",
            fontsize=10.5, fontweight="bold", color=TEXT)
    ax.text(sx + 0.30, sy + sh - 4.35,
            "계좌 농협 301-XX  ·  1,200만원 요구",
            fontsize=8.5, color=DIM)
    btn_y = sy + 0.50
    btn_h = 0.55
    bw_btn = (sw - 0.36 - 0.10)/2
    ax.add_patch(FancyBboxPatch((sx + 0.18, btn_y), bw_btn, btn_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.12",
                                 facecolor=PANEL2, edgecolor=LINEC, linewidth=0.7))
    ax.text(sx + 0.18 + bw_btn/2, btn_y + btn_h/2, "통화 듣기",
            fontsize=11, fontweight="bold", color=TEXT,
            ha="center", va="center")
    ax.add_patch(FancyBboxPatch((sx + 0.18 + bw_btn + 0.10, btn_y),
                                 bw_btn, btn_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.12",
                                 facecolor=NEON_R, edgecolor="none"))
    ax.text(sx + 0.18 + bw_btn + 0.10 + bw_btn/2, btn_y + btn_h/2,
            "거부권 행사",
            fontsize=11, fontweight="bold", color="white",
            ha="center", va="center")
    ax.text(px + phone_w/2, py - 0.05, "②  위험 통화 감지",
            fontsize=10.5, fontweight="bold", color=NEON_R,
            ha="center", va="top")

    # === 화면 3: 거부권 5분 룰 (4선택지) ===
    px = x0 + 2*(phone_w + gap); py = 0.30
    sx, sy, sw, sh = _ios_phone_frame(ax, px, py, phone_w, phone_h)
    ax.text(sx + sw/2, sy + sh - 0.45, "거부권 행사 (5분 룰)",
            fontsize=12, fontweight="bold", color=TEXT,
            ha="center", va="center")
    ax.text(sx + sw/2, sy + sh - 1.30, "송금 차단까지",
            fontsize=10, color=DIM, ha="center")
    ax.text(sx + sw/2, sy + sh - 2.10, "04:47",
            fontsize=40, fontweight="bold", color=NEON_O,
            ha="center", va="center")
    bar_y = sy + sh - 2.65
    bar_w_full = sw - 0.50
    ax.add_patch(FancyBboxPatch((sx + 0.25, bar_y), bar_w_full, 0.12,
                                 boxstyle="round,pad=0.0,rounding_size=0.06",
                                 facecolor=PANEL2, edgecolor="none"))
    ax.add_patch(FancyBboxPatch((sx + 0.25, bar_y), bar_w_full * 0.65, 0.12,
                                 boxstyle="round,pad=0.0,rounding_size=0.06",
                                 facecolor=NEON_O, edgecolor="none"))
    ax.text(sx + sw/2, sy + sh - 3.10, "어떻게 도와드릴까요?",
            fontsize=11, fontweight="bold", color=TEXT, ha="center")
    ax.text(sx + sw/2, sy + sh - 3.40, "아래 4가지 중 선택하세요",
            fontsize=8.5, color=DIM, ha="center")
    actions = [("송금 차단", NEON_R), ("3자 합류", NEON_B),
               ("통화 종료", NEON_Y), ("신고 접수", NEON_S)]
    btn_w = (sw - 0.36 - 0.10)/2
    btn_h = 0.65
    for i, (label, col) in enumerate(actions):
        row = i // 2
        ccol = i % 2
        bx = sx + 0.18 + ccol*(btn_w + 0.10)
        by_ = sy + 1.30 - row*(btn_h + 0.10)
        ax.add_patch(FancyBboxPatch((bx, by_), btn_w, btn_h,
                                     boxstyle="round,pad=0.0,rounding_size=0.12",
                                     facecolor=col, edgecolor="none"))
        ax.text(bx + btn_w/2, by_ + btn_h/2, label,
                fontsize=11, fontweight="bold", color="white",
                ha="center", va="center")
    ax.text(px + phone_w/2, py - 0.05, "③  거부권 5분 룰",
            fontsize=10.5, fontweight="bold", color=NEON_O,
            ha="center", va="top")

    # === 화면 4: 통화 요약 (AI) ===
    px = x0 + 3*(phone_w + gap); py = 0.30
    sx, sy, sw, sh = _ios_phone_frame(ax, px, py, phone_w, phone_h)
    ax.text(sx + 0.18, sy + sh - 0.45, "통화 요약",
            fontsize=14, fontweight="bold", color=TEXT, va="center")
    ax.text(sx + sw - 0.18, sy + sh - 0.45, "AI",
            fontsize=10, fontweight="bold", color=NEON_S,
            ha="right", va="center")
    ax.text(sx + 0.18, sy + sh - 0.95,
            "박○○ 어머니  ·  진행 중", fontsize=10, color=TEXT)
    ax.text(sx + 0.18, sy + sh - 1.18, "12:34 ~ 5분 23초 경과",
            fontsize=8.5, color=DIM)
    timeline_y0 = sy + sh - 1.80
    events = [
        ("00:00", "검찰 사칭 시작", NEON_R),
        ("00:45", "계좌 농협 송금 요구", NEON_R),
        ("01:30", "가족 연락 차단 시도", NEON_R),
        ("02:15", "Sentinel-30 미끼봇 응대", NEON_S),
        ("03:42", "사기범 계좌 정보 추출", NEON_S),
        ("진행중", "시간 흡수 + 통신사 신고", NEON_S),
    ]
    for i, (ts, txt, col) in enumerate(events):
        ey = timeline_y0 - i*0.45
        ax.add_patch(Circle((sx + 0.30, ey), 0.06, facecolor=col, edgecolor="none"))
        if i < len(events) - 1:
            ax.plot([sx + 0.30, sx + 0.30], [ey - 0.06, ey - 0.39],
                    color=col, linewidth=1.0, alpha=0.4)
        ax.text(sx + 0.42, ey + 0.07, ts,
                fontsize=7.5, fontweight="bold", color=col)
        ax.text(sx + 0.42, ey - 0.08, txt, fontsize=8, color=TEXT)
    btn_y = sy + 0.50
    btn_h = 0.55
    ax.add_patch(FancyBboxPatch((sx + 0.18, btn_y), sw - 0.36, btn_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.12",
                                 facecolor=PANEL2, edgecolor=NEON_B, linewidth=1.2))
    ax.text(sx + sw/2, btn_y + btn_h/2, "전체 통화 녹취 보기 ›",
            fontsize=10.5, fontweight="bold", color=NEON_B,
            ha="center", va="center")
    ax.text(px + phone_w/2, py - 0.05, "④  통화 요약 (AI Memory)",
            fontsize=10.5, fontweight="bold", color=NEON_S,
            ha="center", va="top")

    save(fig, "20_senior_app_mockup.png")


def operator_dashboard_mockup():
    """운영자 대시보드 — Next.js + Tailwind 스타일 mockup 16:7."""
    fig, ax = _setup((16, 7.5))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 7.5)
    ax.text(8, 7.20, "운영자 대시보드 — 경찰·금감원·관제센터용 콘솔",
            fontsize=18, fontweight="bold", color=TEXT, ha="center")
    ax.text(8, 6.85,
            "Next.js + Tailwind CSS · 실시간 통화 모니터·Unknown 큐·라벨링 UI·신고 로그",
            fontsize=10.5, color=DIM, ha="center")

    # 브라우저 윈도우
    win_x, win_y = 0.4, 0.4
    win_w, win_h = 15.2, 6.10
    ax.add_patch(FancyBboxPatch((win_x, win_y), win_w, win_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.15",
                                 facecolor="#0e0c0a", edgecolor="none"))
    pad = 0.06
    sx, sy = win_x + pad, win_y + pad
    sw, sh = win_w - 2*pad, win_h - 2*pad
    ax.add_patch(FancyBboxPatch((sx, sy), sw, sh,
                                 boxstyle="round,pad=0.0,rounding_size=0.12",
                                 facecolor="#f5f3ed", edgecolor="none"))
    tabbar_h = 0.32
    ax.add_patch(Rectangle((sx, sy + sh - tabbar_h), sw, tabbar_h,
                            facecolor="#ede8df", edgecolor="none"))
    for i, col in enumerate(["#ef5a52", "#f4b54a", "#5d8c61"]):
        ax.add_patch(Circle((sx + 0.20 + i*0.20, sy + sh - tabbar_h/2),
                            0.07, facecolor=col, edgecolor="none"))
    ax.add_patch(FancyBboxPatch((sx + 0.85, sy + sh - tabbar_h + 0.04),
                                 sw - 1.10, tabbar_h - 0.08,
                                 boxstyle="round,pad=0.0,rounding_size=0.06",
                                 facecolor="white", edgecolor=LINEC, linewidth=0.5))
    ax.text(sx + 1.05, sy + sh - tabbar_h/2,
            "[보안]  console.sentinel30.kr",
            fontsize=7.5, color=DIM, va="center")

    header_h = 0.50
    header_y = sy + sh - tabbar_h - header_h
    ax.add_patch(Rectangle((sx, header_y), sw, header_h,
                            facecolor=NEON_P, edgecolor="none"))
    ax.text(sx + 0.25, header_y + header_h/2,
            "Sentinel-30  ·  운영자 콘솔",
            fontsize=12, fontweight="bold", color="white", va="center")
    ax.text(sx + sw - 0.25, header_y + header_h/2,
            "운영자: 김○○  ·  활성 통화 12  ·  Unknown 큐 3",
            fontsize=9, color="white", ha="right", va="center")

    sidebar_w = 1.85
    sidebar_y = sy
    sidebar_h = header_y - sy
    ax.add_patch(Rectangle((sx, sidebar_y), sidebar_w, sidebar_h,
                            facecolor="#ede8df", edgecolor="none"))
    nav_items = [
        ("●", "실시간 모니터", NEON_O, True),
        ("○", "Unknown 큐 (3)", NEON_R, False),
        ("○", "라벨링 UI", TEXT, False),
        ("○", "분류기 배포", TEXT, False),
        ("○", "신고 로그", TEXT, False),
        ("○", "통계 대시보드", TEXT, False),
        ("○", "운영자 관리", TEXT, False),
    ]
    for i, (icon, name, col, active) in enumerate(nav_items):
        ny = header_y - 0.45 - i*0.42
        if active:
            ax.add_patch(FancyBboxPatch((sx + 0.10, ny - 0.15),
                                         sidebar_w - 0.20, 0.32,
                                         boxstyle="round,pad=0.0,rounding_size=0.05",
                                         facecolor="white", edgecolor="none"))
        ax.text(sx + 0.22, ny, icon, fontsize=9, color=col, va="center")
        ax.text(sx + 0.42, ny, name,
                fontsize=9.5, fontweight="bold" if active else "normal",
                color=TEXT if active else DIM, va="center")

    main_x = sx + sidebar_w
    main_w = sw - sidebar_w
    main_y = sy
    main_h = header_y - sy

    kpi_y = main_y + main_h - 1.20
    kpi_h = 1.00
    kpis = [("12", "활성 통화", NEON_O, "+3 (24h)"),
            ("3", "Unknown 큐", NEON_R, "검토 대기"),
            ("87%", "탐지율 (PoC)", NEON_S, "+9%p"),
            ("4,506분", "흡수 누적", NEON_B, "75시간")]
    kpi_w = (main_w - 0.4 - 3*0.20)/4
    for i, (val, lbl, col, sub) in enumerate(kpis):
        kx = main_x + 0.20 + i*(kpi_w + 0.20)
        ax.add_patch(FancyBboxPatch((kx, kpi_y), kpi_w, kpi_h,
                                     boxstyle="round,pad=0.0,rounding_size=0.10",
                                     facecolor="white", edgecolor=LINEC, linewidth=0.6))
        ax.add_patch(Rectangle((kx, kpi_y + kpi_h - 0.04),
                                kpi_w, 0.04,
                                facecolor=col, edgecolor="none"))
        ax.text(kx + 0.18, kpi_y + kpi_h - 0.45, val,
                fontsize=18, fontweight="bold", color=col, va="center")
        ax.text(kx + 0.18, kpi_y + 0.40, lbl, fontsize=8.5, color=DIM)
        ax.text(kx + 0.18, kpi_y + 0.20, sub, fontsize=7.5, color=col,
                fontweight="bold")

    tbl_y = main_y + 0.20
    tbl_h = kpi_y - tbl_y - 0.20
    ax.add_patch(FancyBboxPatch((main_x + 0.20, tbl_y),
                                 main_w - 0.40, tbl_h,
                                 boxstyle="round,pad=0.0,rounding_size=0.10",
                                 facecolor="white", edgecolor=LINEC, linewidth=0.6))
    ax.text(main_x + 0.40, tbl_y + tbl_h - 0.30,
            "실시간 통화 모니터 (위험도 ↓)",
            fontsize=12, fontweight="bold", color=TEXT)
    ax.text(main_x + main_w - 0.40, tbl_y + tbl_h - 0.30,
            "자동 갱신 5초 · WebSocket ●",
            fontsize=8, color=NEON_S, ha="right")

    col_y = tbl_y + tbl_h - 0.70
    col_xs = [0.40, 1.40, 2.95, 4.55, 5.85, 7.20, 9.10]
    headers = ["ID", "수신 부모", "시나리오", "위험도",
               "진행", "추출 정보", "액션"]
    for cx, h in zip(col_xs, headers):
        ax.text(main_x + cx, col_y, h,
                fontsize=8.5, fontweight="bold", color=DIM)
    ax.plot([main_x + 0.30, main_x + main_w - 0.30],
            [col_y - 0.18, col_y - 0.18],
            color=LINEC, linewidth=0.5)

    rows = [
        ("ID-1042", "박○○", "검찰 사칭", "98%", "12:34",
         "계좌 농협 301-XX", "거부권 발동", NEON_R),
        ("ID-1041", "김○○", "은행 사칭", "76%", "08:12",
         "URL piab-bank.kr", "자녀 푸시 완료", NEON_O),
        ("ID-1040", "이○○", "Unknown", "0.41", "15:42",
         "신뢰도 미달", "운영자 검토 →", NEON_Y),
        ("ID-1039", "정○○", "자녀 사칭", "65%", "03:18",
         "송금 요구 800만", "통신사 신고", NEON_B),
        ("ID-1038", "최○○", "택배 사칭", "82%", "06:55",
         "악성앱 URL 차단", "차단 완료", NEON_S),
    ]
    row_h = 0.45
    for i, row in enumerate(rows):
        ry = col_y - 0.50 - i*row_h
        ax.add_patch(Rectangle((main_x + 0.30, ry - 0.08),
                                0.06, 0.28,
                                facecolor=row[7], edgecolor="none"))
        for ci, (cx, val) in enumerate(zip(col_xs[:7], row[:7])):
            sz = 8.5 if ci != 3 else 10
            col_text = TEXT if ci != 3 else row[7]
            fw = "bold" if ci in (0, 3, 6) else "normal"
            ax.text(main_x + cx, ry, val,
                    fontsize=sz, fontweight=fw, color=col_text, va="center")

    foot_y = tbl_y + 0.20
    ax.text(main_x + 0.40, foot_y,
            "▲ Unknown 큐 3건 대기 — 클릭하여 라벨링 진행",
            fontsize=9, color=NEON_R, fontweight="bold")

    save(fig, "21_operator_dashboard_mockup.png")


if __name__ == "__main__":
    system_architecture()
    golden_timeline()
    swot_matrix()
    risk_matrix()
    kpi_dashboard()
    seven_layers()
    personas()
    roi_mechanism()
    gantt()
    multi_agent()
    fallback_loop()
    demo_layout()
    consent_split()
    scope_realization()
    wireframe_senior()
    senior_app_mockup()
    operator_dashboard_mockup()
    print("\n=== 17종 라이트 연구 발표 다이어그램 생성 완료 ===")
