"""Sentinel-30 v3 diagrams — DARK MODE + NEON 통일판 (14종)."""
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

# ---------- Korean font (mac) ----------
for fp in ["/System/Library/Fonts/AppleSDGothicNeo.ttc",
           "/Library/Fonts/AppleSDGothicNeo.ttc"]:
    if Path(fp).exists():
        fm.fontManager.addfont(fp)
        break
plt.rcParams["font.family"] = "Apple SD Gothic Neo"
plt.rcParams["font.monospace"] = ["Menlo", "Apple SD Gothic Neo", "DejaVu Sans Mono"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "images"
OUT.mkdir(exist_ok=True)

# ===== DARK PALETTE (전 다이어그램 공통) =====
BG = "#0d0d0c"
PANEL = "#1a1a18"
PANEL2 = "#222220"
PANEL3 = "#2a2a27"
LINEC = "#3a3a36"
TEXT = "#f5f0e6"
DIM = "#8a8780"
DIM2 = "#5e5b54"

NEON_O = "#ff8c5a"   # primary orange
NEON_S = "#9fcd6d"   # sage/green
NEON_B = "#7ab8e8"   # sky/blue
NEON_P = "#c89cf0"   # purple
NEON_R = "#ff6b6b"   # red/warning
NEON_Y = "#ffd97a"   # gold

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
    """공통 다크 캔버스 셋업."""
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.axis("off")
    return fig, ax


def _title(ax, x, y, title, sub=None, ha="center"):
    """타이틀 + 서브타이틀 (Apple Keynote 풍 위계)."""
    ax.text(x, y, title, fontsize=19, fontweight="bold", color=TEXT, ha=ha)
    if sub:
        ax.text(x, y - 0.5, sub, fontsize=11, color=DIM, ha=ha)


def _panel(ax, x, y, w, h, accent=None):
    """다크 패널 박스. accent 색상이 있으면 상단에 thin bar.
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
#  1. 시스템 아키텍처 — 5단 데이터 흐름 (다크)
# ================================================================
def system_architecture():
    fig, ax = _setup((14, 9.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    _title(ax, 7, 9.4, "System Architecture",
           "사기범 발신부터 정보전 허브 자동 공급까지 5단 데이터 흐름")

    layers = [
        ("01", "미끼번호 풀", "통신사 협력 · 비활성 번호 N만개",
         "사기범 무작위 발신 유입", NEON_O),
        ("02", "AI 미끼봇 (Honeypot)", "멀티 에이전트 LLM · 한국어 STT/TTS",
         "평균 30분 ~ 2h 통화 유지 · 70대 페르소나", NEON_S),
        ("03", "정보 수집 엔진", "음성지문 · 시나리오 8종 · 계좌·URL 추출",
         "통화에서 자발적 정보 노출 흡수", NEON_B),
        ("04", "실시간 정보전 허브", "통신사 · 경찰망 · 금감원 자동 신고",
         "FDS 연계는 v2 로드맵 (사업화 후)", NEON_P),
        ("05", "시니어 가디언 앱", "부모 위험 통화 감지 · 자녀 푸시",
         "1억+ 송금 5분 내 자녀 거부권", NEON_Y),
    ]

    n = len(layers)
    card_h = 1.45
    gap = 0.18
    y0 = 0.55
    total_h = n * card_h + (n - 1) * gap
    for i, (num, name, tech, role, c) in enumerate(layers):
        idx = n - 1 - i
        y = y0 + idx * (card_h + gap)
        # 패널
        _panel(ax, 0.5, y, 13.0, card_h, accent=c)
        # 좌측 큰 번호
        ax.text(1.1, y + card_h / 2, num, fontsize=36, fontweight="bold",
                color=c, ha="center", va="center", family="monospace",
                alpha=0.85)
        # 본문
        ax.text(2.2, y + card_h - 0.35, name, fontsize=13.5, fontweight="bold",
                color=TEXT, va="top")
        ax.text(2.2, y + card_h - 0.7, tech, fontsize=10, color=DIM, va="top")
        ax.text(2.2, y + 0.22, role, fontsize=9.5, color=c, va="bottom",
                style="italic")

    # 화살표 (위→아래 흐름)
    for i in range(n - 1):
        y_top = y0 + (n - 1 - i) * (card_h + gap)
        y_bot = y_top - gap - 0.02
        _neon_arrow(ax, 7.0, y_top, 7.0, y_bot, color=NEON_O, lw=1.2)

    # 하단 메시지
    ax.text(7, 0.2,
            "→ 사기범 발신을 자원으로 흡수, 정보를 자동 공급하여 ROI 붕괴",
            fontsize=10.5, color=NEON_O, ha="center", style="italic",
            fontweight="bold")
    save(fig, "01_architecture.png")


# ================================================================
#  2. 30분 골든타임 (다크)
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
    ax.annotate("Sentinel-30 개입\n시간 약탈 + 정보 추출 + 허브 동결",
                xy=(15, -0.5), xytext=(11, -3.0),
                fontsize=10.5, fontweight="bold", color=NEON_S, ha="center",
                arrowprops=dict(arrowstyle="->", color=NEON_S, lw=1.8,
                                connectionstyle="arc3,rad=-0.18"),
                zorder=2)
    save(fig, "02_golden_timeline.png")


# ================================================================
#  3. SWOT (다크 2x2)
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
            "2024 보이스피싱 피해 1.97조 — 사회적 압박 최고",
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
#  4. 리스크 매트릭스 (다크 heatmap)
# ================================================================
def risk_matrix():
    fig, ax = _setup((12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    _title(ax, 6, 7.5, "Risk Matrix",
           "발생확률 × 영향도 (다크 히트맵)")

    # 매트릭스 영역
    mx0, my0 = 1.8, 1.6     # 좌하단
    cell_w, cell_h = 1.6, 1.4
    cell_colors = [
        ["#1a2a1c", "#3a3320", "#4a2820"],   # row 0 = LOW prob
        ["#3a3320", "#4a2820", "#5a2018"],   # row 1 = MID prob
        ["#4a2820", "#5a2018", "#6e1818"],   # row 2 = HIGH prob
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
    ax.text(mx0 + 1.5 * cell_w, my0 - 0.85, "영향도 →",
            fontsize=12, color=TEXT, ha="center", fontweight="bold")
    ax.text(mx0 - 0.95, my0 + 1.5 * cell_h, "발생 확률 →",
            fontsize=12, color=TEXT, ha="center", va="center",
            rotation=90, fontweight="bold")

    # 리스크 노드: (prob_row, impact_col, label, color)
    risks = [
        (2, 2, "R1", NEON_R),
        (1, 2, "R2", NEON_R),
        (1, 1, "R3", NEON_Y),
        (2, 1, "R4", NEON_O),
        (1, 2, "R5", NEON_R),
        (2, 1, "R6", NEON_O),
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

    # 범례 (하단)
    legend = [
        ("R1", "미끼봇 협박·모욕 발화"),
        ("R2", "실존 제3자 정보 노출"),
        ("R3", "사기범 데이터 무기한 보관"),
        ("R4", "음성지문 오인식 (선의의 일반인)"),
        ("R5", "통신사 약관·전기통신사업법"),
        ("R6", "AI 인간 사칭 (AI 기본법)"),
    ]
    for i, (lbl, desc) in enumerate(legend):
        row = i // 3
        col = i % 3
        x = 0.4 + col * 3.95
        y = 0.6 - row * 0.35
        ax.text(x, y, lbl, fontsize=9.5, color=NEON_O, fontweight="bold",
                family="monospace", va="center")
        ax.text(x + 0.35, y, desc, fontsize=9, color=DIM, va="center")
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
        ("사기범 시간 약탈", "기존 0분", "30분", "+30분", NEON_S,
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
    fig, ax = _setup((14, 8.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    _title(ax, 7, 8.7, "7-Layer Defense-in-Depth",
           "Sentinel-30의 능동방어 7대 레이어")

    layers = [
        ("01", "AI 미끼봇", "멀티에이전트 LLM\n노인 페르소나 + TTS", NEON_O),
        ("02", "정보 수집 엔진", "음성지문 · 시나리오 8종\n계좌·URL 추출", NEON_B),
        ("03", "정보전 허브", "통신사·경찰망 자동공급\n(FDS는 v2)", NEON_S),
        ("04", "AI 자체 보안", "MITRE ATLAS\nOWASP LLM Top10", NEON_P),
        ("05", "IR 워크플로우", "금감원 24h 자동신고\nCISO 보고 자동화", NEON_B),
        ("06", "법적 안전지대", "6개 법령 검토\n8대 리스크 방어", NEON_Y),
        ("07", "시니어 UX", "70대 5명 인터뷰\n가족 동반 알림", NEON_R),
    ]
    # 4 columns, 2 rows
    cols, rows = 4, 2
    cw, ch = 3.0, 3.2
    x0, y0 = 0.7, 0.7
    gap_x, gap_y = 0.35, 0.4

    for idx, (num, title, sub, c) in enumerate(layers):
        col = idx % cols
        row = 1 - idx // cols
        x = x0 + col * (cw + gap_x)
        y = y0 + row * (ch + gap_y)
        # panel
        _panel(ax, x, y, cw, ch, accent=c)
        # large number — top right
        ax.text(x + cw - 0.4, y + ch - 0.4, num, fontsize=40,
                fontweight="bold", color=c, alpha=0.5, ha="right", va="top",
                family="monospace")
        # title
        ax.text(x + 0.4, y + ch - 0.55, title, fontsize=13.5,
                fontweight="bold", color=TEXT, va="top")
        # body
        ax.text(x + 0.4, y + 1.05, sub, fontsize=10, color=DIM, va="bottom",
                linespacing=1.4)
        # corner dot
        ax.add_patch(Circle((x + 0.45, y + 0.45), 0.10, facecolor=c,
                            edgecolor="none", alpha=0.9))
    save(fig, "06_seven_layers.png")


# ================================================================
#  7. 페르소나 카드 (다크)
# ================================================================
def personas():
    fig, ax = _setup((14, 8.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    _title(ax, 7, 8.6, "Core Personas",
           "타겟 사용자 3종 — 통화 흡수 전·중·후 관점")

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
         "scenario": "허브 API 연동 → FDS 즉시 동결\nIR 플레이북 자동 실행"},
        {"name": "이○○ (45세, 여)", "role": "고령 부모 둔 자녀", "color": NEON_S,
         "avatar": "자녀",
         "pain": "부모 통화 인지 불가\n사후 신고만 가능",
         "needs": "부모 위험 통화 실시간 푸시\n원격 송금 차단 권한",
         "scenario": "가디언 앱 알림 → 통화 가로채기\n가족 3자 통화 전환"},
    ]
    card_w = 4.2
    gap = 0.4
    x0 = (14 - 3 * card_w - 2 * gap) / 2

    for i, p in enumerate(cards):
        x = x0 + i * (card_w + gap)
        y = 0.5
        h = 7.1
        c = p["color"]
        _panel(ax, x, y, card_w, h, accent=c)

        # 큰 원 아바타
        ax.add_patch(Circle((x + card_w / 2, y + h - 1.4), 0.65,
                            facecolor=c, alpha=0.18, edgecolor=c,
                            linewidth=1.5, zorder=3))
        ax.text(x + card_w / 2, y + h - 1.4, p["avatar"],
                fontsize=14, fontweight="bold", color=c,
                ha="center", va="center", zorder=4)

        # 이름·역할
        ax.text(x + card_w / 2, y + h - 2.55, p["name"],
                fontsize=12, fontweight="bold", color=TEXT, ha="center")
        ax.text(x + card_w / 2, y + h - 2.95, p["role"],
                fontsize=10.5, color=c, ha="center", style="italic")

        # 3 섹션
        for label, body, yy, c2 in [
            ("PAIN POINT", p["pain"], y + h - 3.55, NEON_R),
            ("NEEDS", p["needs"], y + h - 5.05, NEON_S),
            ("SCENARIO", p["scenario"], y + h - 6.55, NEON_O),
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
           "산업 ROI 파괴 메커니즘 — 3개 공격 벡터")

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
        (11.0, "운영 비용", "UP", "사기범 시간 30분~2h 약탈\n시간당 매출 무너짐",
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
            "산업의 시간당 매출이 0에 수렴할 때 사기 콜센터형 조직은 자연 붕괴",
            fontsize=12, fontweight="bold", color=NEON_O, ha="center",
            va="center")
    save(fig, "08_roi_mechanism.png")


# ================================================================
#  9. 간트차트 (다크)
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
#  10. Multi-Agent (이미 다크) — 유지
# ================================================================
def multi_agent():
    fig, ax = _setup((14, 9.2))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9.2)

    ax.text(7, 8.85, "Multi-Agent Architecture",
            fontsize=20, fontweight="bold", color=TEXT, ha="center")
    ax.text(7, 8.45, "통화 2시간에도 컨텍스트 한계 없음 · 토큰 비용 -62%",
            fontsize=11.5, color=DIM, ha="center")

    cx, cy = 4.0, 4.85
    sat_r = 2.25
    sats = [
        ("Persona", "Sonnet", "70대 노인 화법", NEON_S, cx, cy + sat_r),
        ("Extractor", "Sonnet", "계좌·URL·시나리오", NEON_B, cx + sat_r * 0.95, cy),
        ("Memory", "Sonnet", "5턴마다 요약 압축", NEON_P, cx, cy - sat_r),
        ("Safety", "Haiku", "협박·실존정보 차단", NEON_R, cx - sat_r * 0.95, cy),
    ]
    for name, model, role, color, sx, sy in sats:
        _neon_arrow(ax, cx, cy, sx, sy, color=NEON_O, lw=1.4, alpha=0.9)
    for name, model, role, color, sx, sy in sats:
        _node(ax, sx, sy, 0.55, color)
        ax.add_patch(Circle((sx, sy + 0.06), 0.12, facecolor=color,
                            edgecolor="none", zorder=5))
        # 위쪽 위성(Persona)은 텍스트를 위로 — Orchestrator glow(r=1.7) 회피
        if sy > cy:
            n_y, m_y, r_y = sy + 1.55, sy + 1.25, sy + 0.95
        else:
            n_y, m_y, r_y = sy - 0.95, sy - 1.25, sy - 1.55
        ax.text(sx, n_y, name, fontsize=11, fontweight="bold",
                color=TEXT, ha="center", zorder=5)
        ax.text(sx, m_y, model, fontsize=8.5, color=color,
                ha="center", zorder=5, family="monospace")
        ax.text(sx, r_y, role, fontsize=9, color=DIM,
                ha="center", zorder=5)

    # 중앙 Orchestrator
    for r, a in [(1.7, 0.06), (1.3, 0.12), (1.0, 0.20)]:
        ax.add_patch(Circle((cx, cy), r, facecolor=NEON_O, alpha=a,
                            edgecolor="none", zorder=3))
    ax.add_patch(Circle((cx, cy), 0.75, facecolor=PANEL2,
                        edgecolor=NEON_O, linewidth=2.4, zorder=4))
    ax.text(cx, cy + 0.18, "Orchestrator", fontsize=11.5, fontweight="bold",
            color=TEXT, ha="center", zorder=5,
            path_effects=[pe.withStroke(linewidth=3, foreground=PANEL2)])
    ax.text(cx, cy - 0.15, "OPUS", fontsize=10, fontweight="bold",
            color=NEON_O, ha="center", zorder=5, family="monospace")
    ax.text(cx, cy - 0.42, "응답 결정 · 분기", fontsize=8.5, color=DIM,
            ha="center", zorder=5)

    # footer 제거: PROBLEM 박스(y=0.15~0.70)와 겹치는 문제. 동일 정보가 다이어그램에 명확.

    panel_x, panel_w = 8.5, 5.3
    _panel(ax, panel_x, 1.0, panel_w, 6.6)

    ax.text(panel_x + 0.35, 7.15, "MEMORY COMPACTION",
            fontsize=9.5, fontweight="bold", color=NEON_O, family="monospace")
    ax.text(panel_x + 0.35, 6.78, "5턴마다 요약 → 입력 토큰 일정",
            fontsize=10.5, color=TEXT)

    seq_y = 5.9
    seq_x0 = panel_x + 0.35
    boxes = [
        ("T1", "dim"), ("T2", "dim"), ("T3", "dim"), ("T4", "dim"), ("T5", "dim"),
        ("S1", "neon"),
        ("T6", "dim"), ("T7", "dim"), ("T8", "dim"), ("T9", "dim"), ("T10", "dim"),
        ("S2", "neon"),
        ("T11", "dim"), ("T12", "dim"),
    ]
    bw = (panel_w - 0.7) / len(boxes)
    for i, (lbl, kind) in enumerate(boxes):
        x = seq_x0 + i * bw
        if kind == "neon":
            for r, a in [(bw * 0.55, 0.15), (bw * 0.45, 0.25)]:
                ax.add_patch(Circle((x + bw / 2, seq_y + 0.18), r,
                                    facecolor=NEON_O, alpha=a, edgecolor="none"))
            ax.add_patch(FancyBboxPatch((x + 0.04, seq_y), bw - 0.08, 0.36,
                                        boxstyle="round,pad=0.01,rounding_size=0.05",
                                        facecolor=NEON_O, edgecolor=NEON_O,
                                        alpha=0.95))
            ax.text(x + bw / 2, seq_y + 0.18, lbl, fontsize=8.5,
                    color=BG, ha="center", va="center", fontweight="bold",
                    family="monospace")
        else:
            ax.add_patch(FancyBboxPatch((x + 0.04, seq_y), bw - 0.08, 0.36,
                                        boxstyle="round,pad=0.01,rounding_size=0.05",
                                        facecolor=PANEL2, edgecolor=LINEC,
                                        linewidth=0.8))
            ax.text(x + bw / 2, seq_y + 0.18, lbl, fontsize=8.2,
                    color=DIM, ha="center", va="center", family="monospace")

    ax.text(panel_x + 0.35, 5.45,
            "Orchestrator 입력 = [요약본 + 최근 2턴] ~ 8K tokens (통화 길이 무관)",
            fontsize=9, color=DIM)

    ax.plot([panel_x + 0.35, panel_x + panel_w - 0.35], [5.05, 5.05],
            color=LINEC, linewidth=0.6)

    ax.text(panel_x + 0.35, 4.65, "IMPACT", fontsize=9.5, fontweight="bold",
            color=NEON_O, family="monospace")

    kpis = [
        (panel_x + 0.35, 3.65, "1.5s", "응답 지연 상한", NEON_S),
        (panel_x + 2.05, 3.65, "-62%", "토큰 비용", NEON_O),
        (panel_x + 3.75, 3.65, "∞", "통화 길이", NEON_B),
    ]
    for x, y, val, lbl, c in kpis:
        ax.text(x, y, val, fontsize=28, fontweight="bold", color=c,
                path_effects=[pe.withStroke(linewidth=4, foreground=PANEL)])
        ax.text(x, y - 0.65, lbl, fontsize=9, color=DIM)

    ax.plot([panel_x + 0.35, panel_x + panel_w - 0.35], [2.65, 2.65],
            color=LINEC, linewidth=0.6)

    ax.text(panel_x + 0.35, 2.25, "MODEL TIERING", fontsize=9.5, fontweight="bold",
            color=NEON_O, family="monospace")
    tier_y = 1.65
    tiers = [
        ("OPUS", "x1", NEON_O),
        ("SONNET", "x3", NEON_S),
        ("HAIKU", "x1", NEON_B),
    ]
    tx = panel_x + 0.35
    for name, cnt, c in tiers:
        ax.add_patch(FancyBboxPatch((tx, tier_y - 0.18), 1.55, 0.5,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=PANEL2, edgecolor=c, linewidth=1.2))
        ax.text(tx + 0.15, tier_y + 0.07, name, fontsize=9.5, color=c,
                fontweight="bold", family="monospace", va="center")
        ax.text(tx + 1.42, tier_y + 0.07, cnt, fontsize=10, color=TEXT,
                fontweight="bold", ha="right", va="center", family="monospace")
        tx += 1.65

    _panel(ax, 0.3, 0.15, 13.4, 0.55)
    ax.text(0.55, 0.42, "PROBLEM", fontsize=9, fontweight="bold",
            color=NEON_R, family="monospace", va="center")
    ax.text(2.0, 0.42,
            "단일 LLM → 30분~2h 통화 시 컨텍스트 200K 누적 → 응답 지연 · 환각 · 페르소나 붕괴",
            fontsize=10, color=TEXT, va="center")

    save(fig, "10_multi_agent.png")


# ================================================================
#  11. Fallback + Active Learning (다크)
# ================================================================
def fallback_loop():
    fig, ax = _setup((14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9.5)
    _title(ax, 7, 9.2, "Fallback + Active Learning",
           "예외 시나리오 처리와 자가 학습 루프")

    # 1차 분류기 (좌측)
    cls_x, cls_y, cls_w, cls_h = 0.5, 7.0, 6.0, 1.5
    _panel(ax, cls_x, cls_y, cls_w, cls_h, accent=NEON_O)
    ax.text(cls_x + cls_w / 2, cls_y + cls_h - 0.4, "1차 시나리오 분류기 (8종)",
            fontsize=12, fontweight="bold", color=TEXT, ha="center")
    ax.text(cls_x + cls_w / 2, cls_y + cls_h - 0.85,
            "검찰 · 은행 · 자녀 · 택배 · 대출 · 세무서 · 경찰 · 보안업체",
            fontsize=9.5, color=DIM, ha="center")
    ax.text(cls_x + cls_w / 2, cls_y + 0.25,
            "confidence score (0.0 ~ 1.0)",
            fontsize=9, color=NEON_O, ha="center", family="monospace")

    # 분기
    branch_y = 5.4
    branch_x_l = 1.7
    branch_x_r = 5.0
    branch_w = 2.3
    branch_h = 1.8

    _neon_arrow(ax, cls_x + cls_w / 2, cls_y, branch_x_l + branch_w / 2,
                branch_y + branch_h, color=NEON_S, lw=1.5)
    _neon_arrow(ax, cls_x + cls_w / 2, cls_y, branch_x_r + branch_w / 2,
                branch_y + branch_h, color=NEON_Y, lw=1.5)
    ax.text(2.4, 6.7, ">= 0.6", fontsize=10, fontweight="bold",
            color=NEON_S, family="monospace")
    ax.text(4.7, 6.7, "< 0.6", fontsize=10, fontweight="bold",
            color=NEON_Y, family="monospace")

    # Known
    _panel(ax, branch_x_l, branch_y, branch_w, branch_h, accent=NEON_S)
    ax.text(branch_x_l + branch_w / 2, branch_y + branch_h - 0.4,
            "Known Scenario", fontsize=11, fontweight="bold",
            color=TEXT, ha="center")
    ax.text(branch_x_l + branch_w / 2, branch_y + branch_h - 0.85,
            "전용 페르소나 응답 분기\n예: 검찰 → 무서워하는 노인",
            fontsize=9, color=DIM, ha="center", va="top", linespacing=1.3)
    ax.text(branch_x_l + branch_w / 2, branch_y + 0.3,
            "정보 추출 풀가동", fontsize=9.5, color=NEON_S, ha="center",
            style="italic")

    # Unknown
    _panel(ax, branch_x_r, branch_y, branch_w, branch_h, accent=NEON_Y)
    ax.text(branch_x_r + branch_w / 2, branch_y + branch_h - 0.4,
            "Unknown_Scam (fallback)", fontsize=11, fontweight="bold",
            color=TEXT, ha="center")
    ax.text(branch_x_r + branch_w / 2, branch_y + branch_h - 0.85,
            "일반 노인 페르소나 + 시간끌기\nLLM 보조 추출 시도",
            fontsize=9, color=DIM, ha="center", va="top", linespacing=1.3)
    ax.text(branch_x_r + branch_w / 2, branch_y + 0.3,
            "전체 통화 녹취 + 메타 저장", fontsize=9.5, color=NEON_Y,
            ha="center", style="italic")

    # 둘 다 → Hub
    hub_x, hub_y, hub_w, hub_h = 1.5, 3.0, 5.0, 1.4
    _panel(ax, hub_x, hub_y, hub_w, hub_h, accent=NEON_B)
    ax.text(hub_x + hub_w / 2, hub_y + hub_h - 0.4,
            "정보 허브 (통신사 · 경찰망 자동 신고)",
            fontsize=10.5, fontweight="bold", color=TEXT, ha="center")
    ax.text(hub_x + hub_w / 2, hub_y + 0.4,
            "Known(자동 차단)  ·  Unknown(수동 검토 큐)",
            fontsize=9, color=DIM, ha="center")

    _neon_arrow(ax, branch_x_l + branch_w / 2, branch_y,
                hub_x + hub_w / 2 - 0.6, hub_y + hub_h, color=NEON_S, lw=1.2)
    _neon_arrow(ax, branch_x_r + branch_w / 2, branch_y,
                hub_x + hub_w / 2 + 0.6, hub_y + hub_h, color=NEON_Y, lw=1.2)

    # 우측: Active Learning Loop
    al_x, al_y, al_w, al_h = 7.5, 7.0, 6.0, 1.5
    _panel(ax, al_x, al_y, al_w, al_h, accent=NEON_P)
    ax.text(al_x + al_w / 2, al_y + al_h - 0.4,
            "Active Learning 루프 (주간 배치)",
            fontsize=12, fontweight="bold", color=TEXT, ha="center")
    ax.text(al_x + al_w / 2, al_y + al_h - 0.85,
            "Unknown_Scam 집계 → 클러스터링 → 라벨링 → 9번째 시나리오 등재",
            fontsize=9.5, color=DIM, ha="center")
    ax.text(al_x + al_w / 2, al_y + 0.25,
            "법무·운영 검토 → 분류기 재배포",
            fontsize=9.5, color=NEON_P, ha="center", style="italic")

    # 4 step nodes
    step_y = 5.6
    steps = [
        (8.05, "1. 수집", "Unknown 통화 전사", NEON_P),
        (9.7, "2. 클러스터링", "LLM embedding\nHDBSCAN", NEON_P),
        (11.35, "3. 라벨링", "운영자 1회 검토\n새 시나리오 명명", NEON_P),
        (13.0, "4. 재학습", "분류기 파인튜닝\n+ 페르소나 추가", NEON_P),
    ]
    for x, title, body, c in steps:
        # halo
        for r, a in [(0.6, 0.10), (0.42, 0.18)]:
            ax.add_patch(Circle((x, step_y + 0.55), r, facecolor=c, alpha=a,
                                edgecolor="none", zorder=3))
        ax.add_patch(FancyBboxPatch((x - 0.6, step_y - 0.4), 1.2, 1.55,
                                    boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor=PANEL2, edgecolor=c, linewidth=1.4,
                                    zorder=4))
        ax.text(x, step_y + 0.85, title, fontsize=9.5, fontweight="bold",
                color=TEXT, ha="center", zorder=5)
        ax.text(x, step_y + 0.05, body, fontsize=8.5, color=DIM,
                ha="center", va="center", zorder=5, linespacing=1.3)

    for x1, x2 in [(8.05, 9.7), (9.7, 11.35), (11.35, 13.0)]:
        _neon_arrow(ax, x1 + 0.6, step_y + 0.55, x2 - 0.6, step_y + 0.55,
                    color=NEON_P, lw=1.2, glow=False)

    # 루프 back arrow (Active Learning step 4 → 분류기)
    ax.plot([13.0, 13.6], [step_y - 0.4, step_y - 0.4],
            color=NEON_P, linewidth=1.3, linestyle=(0, (4, 3)))
    ax.plot([13.6, 13.6], [step_y - 0.4, 3.0],
            color=NEON_P, linewidth=1.3, linestyle=(0, (4, 3)))
    ax.plot([13.6, cls_x + cls_w / 2], [3.0, 3.0],
            color=NEON_P, linewidth=1.3, linestyle=(0, (4, 3)))
    ax.add_patch(FancyArrowPatch((cls_x + cls_w / 2, 3.0),
                                 (cls_x + cls_w / 2, cls_y - 0.05),
                                 arrowstyle="-|>", mutation_scale=14,
                                 color=NEON_P, linewidth=1.3,
                                 linestyle=(0, (4, 3))))
    ax.text(8.5, 3.25, "분류기 업데이트 (월 1회 배포)",
            fontsize=10, fontweight="bold", color=NEON_P, style="italic")

    # 하단 결과
    _panel(ax, 0.5, 1.0, 13.0, 1.4, accent=NEON_O)
    ax.text(7, 1.95, "확장성 효과",
            fontsize=11.5, fontweight="bold", color=NEON_O, ha="center")
    ax.text(7, 1.4,
            "8종 → 12종 → 16종 시나리오 자동 확장 · \"학습 안 된 사기\"도 통화는 끊지 않고 정보·신고로 흡수",
            fontsize=10.5, color=TEXT, ha="center")
    save(fig, "11_fallback_loop.png")


# ================================================================
#  12. 본선 시연 화면 (다크 3패널)
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
    ax.text(2.45, 1.4, "▶ 00:42 / 02:15", fontsize=11, fontweight="bold",
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
#  13. 데이터 수집 동의 분리 (다크 2 패널)
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
#  14. Scope realization — 실구현 vs 로드맵 (다크 2분할)
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
    ax.text(11.2, 7.6, "v2 ROADMAP  ·  사업화 후",
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
    print("\n=== 14종 다크모드 다이어그램 생성 완료 ===")
