"""Sentinel-30 v3 diagrams — mac port + 5 new visuals.

Adds:
  10_multi_agent.png     멀티 에이전트 구조 (컨텍스트 윈도우 문제 해결)
  11_fallback_loop.png   예외 시나리오 fallback + Active Learning 루프
  12_demo_layout.png     본선 시연 화면 분할 mockup
  13_consent_split.png   데이터 수집 경로 분리 (사기범 vs 사용자)
  14_scope_realization.png 실구현 vs 추후고도화 (FDS 톤다운)

Regenerates the original 9 with the same Claude palette but using mac fonts.
"""
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle, Circle, Wedge

# ---------- Korean font (mac) ----------
FONT_CANDIDATES = [
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/Library/Fonts/AppleSDGothicNeo.ttc",
]
for fp in FONT_CANDIDATES:
    if Path(fp).exists():
        fm.fontManager.addfont(fp)
        break
plt.rcParams["font.family"] = "Apple SD Gothic Neo"
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "images"
OUT.mkdir(exist_ok=True)

# Claude Design palette
CREAM = "#faf9f5"
TAN = "#e8e6dc"
WARM = "#f1efe6"
INK = "#141413"
SLATE = "#5a5853"
MID = "#b0aea5"
ORANGE = "#d97757"
BURNT = "#c4623f"
RUST = "#a04a2a"
SAGE = "#788c5d"
DUSK = "#6a9bcc"
GOLD = "#d69e2e"
RED = "#c53030"
GREEN = SAGE
NAVY = INK
BLUE = DUSK
SKY = "#9bc1e6"
LGRAY = TAN
GRAY = SLATE
LINE = TAN

# Aliases for legibility
PURPLE = "#805ad5"


def save(fig, name, dpi=200):
    fig.patch.set_facecolor(CREAM)
    path = OUT / name
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=CREAM)
    plt.close(fig)
    print(f"[OK] {path.name}")


# ================================================================
#                       기존 9개 (재생성)
# ================================================================

def system_architecture():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Sentinel-30 시스템 아키텍처",
                 fontsize=18, fontweight="bold", color=NAVY, pad=15)

    layers = [
        (1, 8.2, 12, 1.2, "① 미끼번호 풀 (통신사 협력)",
         "비활성 번호 N만 개를 미끼로 등록 → 사기범 무작위 발신 유입", NAVY),
        (1, 6.4, 12, 1.4, "② AI 미끼봇 (Honeypot Bot)",
         "한국어 STT  +  멀티에이전트 LLM (Opus·Sonnet·Haiku)  +  한국어 TTS  →  평균 30분~2h 통화 유지", ORANGE),
        (1, 4.6, 12, 1.4, "③ 정보 수집 엔진",
         "음성 지문화 · 사기 시나리오 8종 자동 분류 · 계좌·URL·악성앱 패키지명 추출", DUSK),
        (1, 2.5, 12, 1.6, "④ 실시간 정보전 허브  (가명처리 + 암호화)  · FDS 연계는 v2 로드맵",
         "통신사 번호 차단  │  경찰청 사이버수사대  │  금감원 24h 자동 신고  │  FDS(추후 사업화)",
         SAGE),
        (1, 0.4, 12, 1.4, "⑤ 시니어 가디언 앱 (옵션)",
         "부모 통화 위험 감지 → 자녀 푸시 · 1억 이상 송금 5분 내 자녀 거부권", GOLD),
    ]
    for x, y, w, h, title, sub, c in layers:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                             facecolor=c, edgecolor=c, alpha=0.92)
        ax.add_patch(box)
        ax.text(x + 0.3, y + h - 0.35, title,
                fontsize=13, fontweight="bold", color="white", va="top")
        ax.text(x + 0.3, y + h - 0.85, sub,
                fontsize=10.3, color="white", va="top", alpha=0.96)
    for x1, y1, x2, y2 in [(7, 8.15, 7, 7.85), (7, 6.35, 7, 6.05),
                           (7, 4.55, 7, 4.15), (7, 2.45, 7, 2.05)]:
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     arrowstyle="-|>", mutation_scale=22,
                                     color=SLATE, linewidth=2))
    save(fig, "01_architecture.png")


def golden_timeline():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.set_xlim(-5, 70)
    ax.set_ylim(-3, 5)
    ax.axis("off")
    ax.set_title("30분 골든타임 — 사기 산업의 시간 약탈 구조",
                 fontsize=17, fontweight="bold", color=NAVY, pad=10)
    ax.plot([0, 65], [0, 0], color=SLATE, linewidth=3, zorder=1)
    ax.add_patch(Rectangle((0, -0.3), 30, 0.6, facecolor=ORANGE, alpha=0.25, zorder=0))
    ax.add_patch(Rectangle((30, -0.3), 35, 0.6, facecolor=RED, alpha=0.2, zorder=0))
    ax.text(15, -1.3, "Golden Time (30분)", fontsize=12, fontweight="bold",
            color=BURNT, ha="center")
    ax.text(47, -1.3, "추적 불가 구간", fontsize=12, fontweight="bold",
            color=RED, ha="center")
    events = [
        (0, "T+0", "통화 시작", DUSK),
        (15, "T+15", "송금 완료\n(피해자 평균)", ORANGE),
        (30, "T+30", "사기범 계좌\n인출 시작", RED),
        (60, "T+60", "자금 추적\n불가 영역", "#7f1d1d"),
    ]
    for x, label, desc, c in events:
        ax.scatter(x, 0, s=260, color=c, zorder=3, edgecolor="white", linewidth=2)
        ax.text(x, 0.6, label, fontsize=11, fontweight="bold", color=c, ha="center")
        ax.text(x, 2.0, desc, fontsize=10, color=SLATE, ha="center", va="center")
    ax.annotate("Sentinel-30 개입 구간\n사기범 시간 약탈 + FDS 즉시 동결",
                xy=(15, -0.3), xytext=(15, -2.5),
                fontsize=11, fontweight="bold", color=SAGE, ha="center",
                arrowprops=dict(arrowstyle="->", color=SAGE, lw=2))
    save(fig, "02_golden_timeline.png")


def swot_matrix():
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("SWOT 분석", fontsize=18, fontweight="bold", color=NAVY, pad=10)
    cells = [
        (0.3, 5.3, 5.7, 4.3, "Strengths (강점)", [
            "• Active Defense 프레임 — 국내 유일 차별화",
            "• 영국 Daisy AI 벤치마크 + 한국 맞춤 설계",
            "• 멀티에이전트 구조로 컨텍스트 한계 돌파",
            "• 6개 법령 합법성 검토 완료",
            "• MITRE ATLAS · OWASP LLM 위협 모델 통합",
        ], SAGE),
        (6.0, 5.3, 5.7, 4.3, "Weaknesses (약점)", [
            "• 통신사·은행 제휴 없으면 미끼번호 풀 확보 난항",
            "• 한국어 노년 화자 STT 학습 데이터 부족",
            "• AI 인간 사칭 — AI 기본법 시행령 미확정",
            "• 6인 팀 4주 — 풀스택 구현 한계",
            "• 사기범 음성지문 오인식 시 명예훼손 리스크",
        ], GOLD),
        (0.3, 0.5, 5.7, 4.3, "Opportunities (기회)", [
            "• 2024 보이스피싱 피해 1.97조 — 사회적 압박 최고",
            "• 금감원·금융보안원 사기 대응 예산 확대",
            "• 영국 Ofcom 적법성 인증 — 국제 선례 존재",
            "• AI 기본법 (2026 시행) — 공공안전 예외 등록 가능",
            "• 시중은행 FDS 고도화 수요 (제휴 PoC 기회)",
        ], DUSK),
        (6.0, 0.5, 5.7, 4.3, "Threats (위협)", [
            "• 사기범의 적대적 공격 — TTS 합성음 식별 회피",
            "• 통신사 약관·전기통신사업법 해석 변동",
            "• 경찰청·금감원 데이터 공유 채널 정치적 변수",
            "• 글로벌 사기 거점(중국·동남아) 협조 한계",
            "• 유사 솔루션 (KT 후후·시티즌코난) 기능 흡수",
        ], RED),
    ]
    for x, y, w, h, title, items, c in cells:
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.05,rounding_size=0.12",
                                    facecolor=c, edgecolor=c, alpha=0.15, linewidth=2))
        ax.text(x + 0.25, y + h - 0.35, title,
                fontsize=14, fontweight="bold", color=c, va="top")
        for k, item in enumerate(items):
            ax.text(x + 0.25, y + h - 1.05 - k * 0.55, item,
                    fontsize=10.2, color=SLATE, va="top")
    save(fig, "03_swot.png")


def risk_matrix():
    fig, ax = plt.subplots(figsize=(11, 9))
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_title("리스크 매트릭스 — 발생확률 × 영향도",
                 fontsize=17, fontweight="bold", color=NAVY, pad=15)
    grid_colors = [
        ["#e8f0d8", "#fef4d8", "#fde0c8"],
        ["#fef4d8", "#fde0c8", "#fbcbb8"],
        ["#fde0c8", "#fbcbb8", "#f4a98c"],
    ]
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((j + 0.5, i + 0.5), 1, 1,
                                   facecolor=grid_colors[i][j],
                                   edgecolor="white", linewidth=2))
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["하 (Low)", "중 (Mid)", "상 (High)"], fontsize=11)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["하 (Low)", "중 (Mid)", "상 (High)"], fontsize=11)
    ax.set_xlabel("영향도", fontsize=13, fontweight="bold")
    ax.set_ylabel("발생 확률", fontsize=13, fontweight="bold")
    ax.set_xlim(0.4, 3.6)
    ax.set_ylim(0.4, 3.6)
    risks = [
        (3, 3, "R1\n미끼봇 협박발화"),
        (2, 3, "R2\n실존 제3자\n정보 노출"),
        (2, 2, "R3\n데이터\n장기보관"),
        (3, 2, "R4\n음성지문\n오인식"),
        (2, 3, "R5\n통신사\n약관위반"),
        (3, 2, "R6\nAI 사칭\n윤리"),
    ]
    placed = {}
    for p, im, label in risks:
        key = (p, im)
        n = placed.get(key, 0)
        dx = (n % 2) * 0.25 - 0.12
        dy = (n // 2) * 0.25 - 0.12
        placed[key] = n + 1
        ax.scatter(im + dx, p + dy, s=900, color=INK,
                   edgecolor="white", linewidth=2, zorder=3, alpha=0.88)
        ax.text(im + dx, p + dy, label.split("\n")[0],
                fontsize=8.5, color="white", fontweight="bold",
                ha="center", va="center", zorder=4)
    legend_text = (
        "R1 미끼봇 협박·모욕 발화      R2 실존 제3자 정보 노출\n"
        "R3 사기범 데이터 무기한 보관   R4 음성지문 오인식 (선의 일반인)\n"
        "R5 통신사 약관·전기통신사업법  R6 AI 인간 사칭 (AI 기본법)"
    )
    ax.text(0.4, -0.15, legend_text, fontsize=9.5, color=SLATE,
            transform=ax.transAxes, va="top")
    save(fig, "04_risk_matrix.png")


def kpi_dashboard():
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5))
    fig.suptitle("KPI 대시보드 — 기존 솔루션 대비 Sentinel-30",
                 fontsize=17, fontweight="bold", color=NAVY, y=1.02)
    kpis = [
        ("탐지율", [78, 87], "%", DUSK),
        ("사기범 시간 약탈\n(분/통화)", [0, 30], "분", SAGE),
        ("환수 골든타임\n(분)", [240, 30], "분", ORANGE),
        ("법정 신고시한\n(24h) 충족률", [65, 100], "%", INK),
    ]
    for ax, (title, vals, unit, c) in zip(axes, kpis):
        bars = ax.bar(["기존", "Sentinel-30"], vals,
                      color=[TAN, c], edgecolor="white", linewidth=2)
        ax.set_title(title, fontsize=12, fontweight="bold", color=NAVY)
        ax.set_ylim(0, max(vals) * 1.25 if max(vals) > 0 else 50)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", labelsize=9)
        ax.tick_params(axis="x", labelsize=10.5)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(vals) * 0.03,
                    f"{v}{unit}", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    plt.tight_layout()
    save(fig, "05_kpi_dashboard.png")


def seven_layers():
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title("Sentinel-30 7대 레이어",
                 fontsize=18, fontweight="bold", color=NAVY, pad=10)
    layers = [
        ("1", "AI 미끼봇", "멀티에이전트 LLM +\n노인 페르소나 + 음성합성", ORANGE),
        ("2", "정보 수집 엔진", "음성지문 · 시나리오 8종\n자동 분류", DUSK),
        ("3", "실시간 정보전 허브", "통신사 · 경찰망 자동 공급\n(FDS는 v2 로드맵)", SAGE),
        ("4", "AI 자체 보안", "OWASP LLM Top 10 +\nMITRE ATLAS 대응", PURPLE),
        ("5", "IR 워크플로우", "금감원 24h 자동 신고\nCISO 보고 자동화", INK),
        ("6", "법적 안전지대", "6개 법령 합법성 검토\n+ 8대 리스크 방어", GOLD),
        ("7", "시니어 UX", "70대 5명 인터뷰\n가족 동반 알림", RED),
    ]
    cols = 4
    cw, ch = 3.0, 3.4
    x0, y0 = 0.7, 0.6
    gap_x, gap_y = 0.3, 0.4
    for idx, (num, title, sub, c) in enumerate(layers):
        col = idx % cols
        row = 1 - idx // cols
        x = x0 + col * (cw + gap_x)
        y = y0 + row * (ch + gap_y)
        ax.add_patch(FancyBboxPatch((x, y), cw, ch,
                                    boxstyle="round,pad=0.05,rounding_size=0.18",
                                    facecolor=c, edgecolor=c, alpha=0.92))
        ax.text(x + 0.3, y + ch - 0.4, num,
                fontsize=32, fontweight="bold", color="white", alpha=0.55, va="top")
        ax.text(x + cw / 2, y + ch - 1.1, title,
                fontsize=14, fontweight="bold", color="white", ha="center", va="top")
        ax.text(x + cw / 2, y + ch - 2.0, sub,
                fontsize=10.5, color="white", ha="center", va="top", alpha=0.96)
    save(fig, "06_seven_layers.png")


def personas():
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.suptitle("핵심 페르소나 — 3종",
                 fontsize=17, fontweight="bold", color=NAVY, y=1.02)
    cards = [
        {"name": "박○○ (72세, 여)", "role": "주 피해 타겟", "color": GOLD,
         "pain": "검찰 사칭 통화 시 인지 트랜스에 빠짐\n자녀에게 연락 못 하고 송금",
         "needs": "큰 글씨 경고 + 자녀 자동 알림\n송금 직전 가족 거부권",
         "scenario": "검찰 사칭 → 미끼봇이 가로채\n→ 자녀 푸시 → 5분 내 차단"},
        {"name": "김○○ (38세, 남)", "role": "은행 디지털보안 담당자", "color": DUSK,
         "pain": "FDS 룰 업데이트가 사후적\n환수 골든타임 항상 놓침",
         "needs": "사기범 계좌 실시간 자동 피드\n금감원 24h 자동 신고",
         "scenario": "허브 API 연동 → FDS 즉시 동결\n→ IR 플레이북 자동 실행"},
        {"name": "이○○ (45세, 여)", "role": "고령 부모 둔 자녀", "color": SAGE,
         "pain": "부모 통화 인지 불가\n사후 신고만 가능",
         "needs": "부모 위험 통화 실시간 푸시\n원격 송금 차단 권한",
         "scenario": "가디언 앱 알림 → 통화 가로채기\n→ 가족 3자 통화 전환"},
    ]
    for ax, p in zip(axes, cards):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        c = p["color"]
        ax.add_patch(FancyBboxPatch((0.2, 7.6), 9.6, 2.0,
                                    boxstyle="round,pad=0.05,rounding_size=0.15",
                                    facecolor=c, edgecolor=c, alpha=0.92))
        ax.text(5, 8.9, p["name"], fontsize=14, fontweight="bold", color="white", ha="center")
        ax.text(5, 8.0, p["role"], fontsize=11, color="white", ha="center", alpha=0.92)
        for label, body, y in [("Pain Point", p["pain"], 5.2),
                               ("Needs", p["needs"], 3.0),
                               ("Scenario", p["scenario"], 0.8)]:
            ax.add_patch(FancyBboxPatch((0.2, y), 9.6, 2.0,
                                        boxstyle="round,pad=0.05,rounding_size=0.1",
                                        facecolor="white", edgecolor=c, linewidth=1.8))
            ax.text(0.45, y + 1.7, label, fontsize=10.5, fontweight="bold", color=c)
            ax.text(0.45, y + 0.55, body, fontsize=10, color=SLATE)
    plt.tight_layout()
    save(fig, "07_personas.png")


def roi_mechanism():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("사기 산업 ROI 파괴 메커니즘",
                 fontsize=17, fontweight="bold", color=NAVY, pad=10)
    ax.text(0.5, 5.8, "사기 산업 총수입", fontsize=13, fontweight="bold", color=NAVY)
    eq = "= [발신 통화 수] × [성공률] × [건당 피해액]  −  [운영 비용]"
    ax.text(0.5, 5.1, eq, fontsize=12, color=SLATE)
    attacks = [
        (3.5, "통화 수 ↓", "미끼번호 풀이 사기범 발신을\n실제 피해자가 아닌 봇으로 흡수", DUSK),
        (7.0, "성공률 ↓", "미끼봇 정보 → 통신사·경찰망\n→ 송금 시도 차단", SAGE),
        (10.5, "운영 비용 ↑", "사기범 시간을 30분~2h 약탈\n시간당 매출 무너짐", RED),
    ]
    for x, title, desc, c in attacks:
        ax.add_patch(FancyBboxPatch((x - 1.7, 2.0), 3.4, 2.5,
                                    boxstyle="round,pad=0.05,rounding_size=0.15",
                                    facecolor=c, edgecolor=c, alpha=0.92))
        ax.text(x, 4.0, title, fontsize=14, fontweight="bold", color="white", ha="center")
        ax.text(x, 2.85, desc, fontsize=10.3, color="white",
                ha="center", va="center", alpha=0.96)
        ax.add_patch(FancyArrowPatch((x, 4.7), (x, 4.55),
                                     arrowstyle="-|>", mutation_scale=18,
                                     color=SLATE, linewidth=1.5))
    ax.text(7, 0.7,
            "→ 산업의 시간당 매출이 0에 수렴할 때 사기 콜센터형 조직은 자연 붕괴",
            fontsize=12, fontweight="bold", color=NAVY, ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=GOLD, alpha=0.25,
                      edgecolor=GOLD, linewidth=1.5))
    save(fig, "08_roi_mechanism.png")


def gantt():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_title("프로젝트 일정 (예선 4주 + 본선 2일)",
                 fontsize=17, fontweight="bold", color=NAVY, pad=10)
    tasks = [
        ("법리 검토서 작성", 0, 2, INK),
        ("70대 사용성 인터뷰", 1, 2, DUSK),
        ("멀티에이전트 봇 프로토타입", 1, 2.5, ORANGE),
        ("시연 영상 시안", 2, 1.5, PURPLE),
        ("기획서 v1.0", 2, 1.5, SAGE),
        ("최종 발표자료 + 시연 영상", 3, 1, GOLD),
        ("적대적 공격 시연 준비", 3, 1, RED),
    ]
    for i, (name, start, dur, c) in enumerate(tasks):
        ax.barh(i, dur, left=start, color=c, edgecolor="white", linewidth=2, height=0.65)
        ax.text(start + dur / 2, i, name, fontsize=10, color="white",
                ha="center", va="center", fontweight="bold")
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([""] * len(tasks))
    ax.invert_yaxis()
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xticklabels(["W1", "W2", "W3", "W4", "본선"], fontsize=11)
    ax.set_xlim(-0.2, 4.5)
    ax.grid(axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axvline(4, color=SLATE, linestyle="--", linewidth=1.5, alpha=0.7)
    ax.text(4.25, -0.5, "본선 무박 2일", fontsize=11, fontweight="bold", color=SLATE)
    save(fig, "09_gantt.png")


# ================================================================
#                  새로 추가되는 5종 다이어그램
# ================================================================

def multi_agent_OLD():
    """이전 버전 — 보존용. 호출하지 않음."""
    fig, ax = plt.subplots(figsize=(14, 9.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("AI 미끼봇 멀티 에이전트 구조  —  통화 2시간에도 컨텍스트 한계 없음",
                 fontsize=16, fontweight="bold", color=NAVY, pad=12)

    # 상단: 문제 정의
    ax.add_patch(FancyBboxPatch((0.3, 8.6), 13.4, 1.1,
                                boxstyle="round,pad=0.05,rounding_size=0.12",
                                facecolor=TAN, edgecolor=ORANGE, linewidth=1.2))
    ax.text(0.6, 9.35, "❶ 문제", fontsize=11, fontweight="bold", color=BURNT)
    ax.text(0.6, 8.95,
            "단일 LLM으로 30분~2h 통화를 유지하면 컨텍스트 윈도우(200K) 누적 → 응답 지연·환각·페르소나 붕괴",
            fontsize=10.8, color=INK)

    # 중단: 에이전트 5종 카드
    ax.add_patch(FancyBboxPatch((0.3, 7.7), 13.4, 0.7,
                                boxstyle="round,pad=0.05,rounding_size=0.1",
                                facecolor=ORANGE, edgecolor=ORANGE, alpha=0.92))
    ax.text(7, 8.05, "❷ 해결 — 역할별 에이전트 5종 분리 (모델 티어링 + 메모리 압축)",
            fontsize=12, fontweight="bold", color="white", ha="center")

    # 5 agent cards — role을 2~3줄로 분리해서 카드 폭에 맞게
    agents = [
        # (x, w, name, model, role(줄바꿈 포함), color)
        (0.3, 2.55, "① Orchestrator", "Opus",
         "응답 결정 · 분기\n자식 에이전트 호출\n전체 흐름 통제", BURNT),
        (3.05, 2.55, "② Persona Speaker", "Sonnet",
         "70대 노인 화법 변환\nTTS 직전 출력\n호흡·머뭇거림 삽입", ORANGE),
        (5.80, 2.55, "③ Memory Compactor", "Sonnet",
         "5턴마다 대화 요약\n장기 메모리 관리\n토큰 누적 방지", DUSK),
        (8.55, 2.55, "④ Info Extractor", "Sonnet",
         "계좌·URL·시나리오\n키워드 병렬 추출\n구조화 JSON 출력", SAGE),
        (11.30, 2.40, "⑤ Safety Guard", "Haiku",
         "욕설·협박 필터\n실존정보 누설 차단\nTTS 전 사전 검열", PURPLE),
    ]
    for x, w, name, model, role, c in agents:
        # body
        ax.add_patch(FancyBboxPatch((x, 4.5), w, 3.0,
                                    boxstyle="round,pad=0.04,rounding_size=0.12",
                                    facecolor=c, edgecolor=c, alpha=0.92))
        ax.text(x + w / 2, 7.20, name, fontsize=11.5, fontweight="bold",
                color="white", ha="center")
        # model tier chip
        ax.add_patch(FancyBboxPatch((x + w / 2 - 0.55, 6.55), 1.1, 0.35,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="white", edgecolor="white", alpha=0.95))
        ax.text(x + w / 2, 6.72, model, fontsize=9.5, fontweight="bold",
                color=c, ha="center", va="center")
        ax.text(x + w / 2, 5.7, role, fontsize=9.3, color="white",
                ha="center", va="center", linespacing=1.35)

    # 데이터 흐름 화살표
    # Orchestrator → 나머지
    for tx in [3.05 + 2.55/2, 5.80 + 2.55/2, 8.55 + 2.55/2, 11.30 + 2.40/2]:
        ax.add_patch(FancyArrowPatch((0.3 + 2.55/2, 4.4), (tx, 4.4),
                                     arrowstyle="-|>", mutation_scale=14,
                                     color=SLATE, linewidth=1.2,
                                     connectionstyle="arc3,rad=-0.0"))

    # 하단: 메모리 압축 흐름 시각화
    ax.add_patch(FancyBboxPatch((0.3, 2.6), 13.4, 1.6,
                                boxstyle="round,pad=0.04,rounding_size=0.12",
                                facecolor=WARM, edgecolor=DUSK, linewidth=1.2))
    ax.text(0.55, 3.95, "❸ 메모리 압축 흐름", fontsize=11, fontweight="bold", color=DUSK)

    # turn boxes
    turns = [
        (1.2, "T1"), (2.0, "T2"), (2.8, "T3"), (3.6, "T4"), (4.4, "T5"),
        (5.8, "요약1"), (6.7, "T6"), (7.5, "T7"), (8.3, "T8"), (9.1, "T9"), (9.9, "T10"),
        (11.2, "요약2"), (12.1, "T11"), (12.9, "T12"),
    ]
    for x, label in turns:
        c = DUSK if "요약" in label else SLATE
        ax.add_patch(Rectangle((x - 0.32, 2.85), 0.64, 0.45,
                               facecolor=c if "요약" in label else "white",
                               edgecolor=c, linewidth=1))
        ax.text(x, 3.07, label, fontsize=8.5,
                color="white" if "요약" in label else c,
                ha="center", va="center", fontweight="bold")
    # arrows merging into summary
    for x in [1.2, 2.0, 2.8, 3.6, 4.4]:
        ax.add_patch(FancyArrowPatch((x, 3.32), (5.7, 3.32),
                                     arrowstyle="-", color=SLATE, linewidth=0.6, alpha=0.5))
    ax.add_patch(FancyArrowPatch((5.7, 3.32), (5.8, 3.32),
                                 arrowstyle="-|>", color=DUSK, linewidth=1.4, mutation_scale=10))
    for x in [6.7, 7.5, 8.3, 9.1, 9.9]:
        ax.add_patch(FancyArrowPatch((x, 3.32), (11.1, 3.32),
                                     arrowstyle="-", color=SLATE, linewidth=0.6, alpha=0.5))
    ax.add_patch(FancyArrowPatch((11.1, 3.32), (11.2, 3.32),
                                 arrowstyle="-|>", color=DUSK, linewidth=1.4, mutation_scale=10))

    ax.text(0.55, 2.75, "5턴마다 Compactor가 요약 → Orchestrator 입력은 항상 [요약본 + 최근 2턴]으로 고정 (< 8K 토큰)",
            fontsize=9.5, color=SLATE, va="top")

    # 효과 박스
    ax.add_patch(FancyBboxPatch((0.3, 0.6), 13.4, 1.8,
                                boxstyle="round,pad=0.05,rounding_size=0.12",
                                facecolor=SAGE, edgecolor=SAGE, alpha=0.92))
    ax.text(0.6, 2.15, "❹ 효과", fontsize=11, fontweight="bold", color="white")
    bullets = [
        "• 통화 길이와 무관하게 Orchestrator 입력 토큰 일정 → 응답 지연 < 1.5초 유지",
        "• 모델 티어링 (Opus 1 · Sonnet 3 · Haiku 1) → 토큰 비용 -62%",
        "• Safety Guard가 TTS 전 단계에서 협박·욕설·실존 정보 차단 → 법적 리스크 R1·R2 완화",
        "• 각 에이전트가 독립적으로 교체 가능 → 새 시나리오 추가 시 Extractor 프롬프트만 수정",
    ]
    for i, b in enumerate(bullets):
        ax.text(0.6, 1.75 - i * 0.32, b, fontsize=10, color="white", va="top")

    save(fig, "10_multi_agent.png")


def multi_agent():
    """10_multi_agent.png — DARK MODE 노드+엣지 데이터 흐름 다이어그램.

    중앙: Orchestrator (Opus). 위성: Persona / Memory / Extractor / Safety.
    엣지: orange neon. 하단: 메모리 압축 시퀀스. 우측: KPI 임팩트.
    """
    import matplotlib.patheffects as pe

    # Dark palette
    BG = "#0d0d0c"
    PANEL = "#1a1a18"
    PANEL2 = "#222220"
    LINEC = "#3a3a36"
    TEXT = "#f5f0e6"
    DIM = "#8a8780"
    NEON_O = "#ff8c5a"
    NEON_S = "#9fcd6d"
    NEON_B = "#7ab8e8"
    NEON_P = "#c89cf0"
    NEON_R = "#ff6b6b"

    fig, ax = plt.subplots(figsize=(14, 9.2))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9.2)
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # ───────── 타이틀
    ax.text(7, 8.7, "Multi-Agent Architecture",
            fontsize=20, fontweight="bold", color=TEXT, ha="center",
            family="Apple SD Gothic Neo")
    ax.text(7, 8.25, "통화 2시간에도 컨텍스트 한계 없음 · 토큰 비용 -62%",
            fontsize=11.5, color=DIM, ha="center")

    # ───────── 좌측: 노드 그래프 (Orchestrator + 4 위성)
    # 중앙 노드 위치 (x=4)
    cx, cy = 4.0, 4.8
    sat_r = 2.7  # 위성 거리
    sats = [
        ("Persona", "Sonnet", "70대 노인 화법", NEON_S, cx, cy + sat_r),
        ("Extractor", "Sonnet", "계좌·URL·시나리오", NEON_B, cx + sat_r * 0.95, cy),
        ("Memory", "Sonnet", "5턴마다 요약 압축", NEON_P, cx, cy - sat_r),
        ("Safety", "Haiku", "협박·실존정보 차단", NEON_R, cx - sat_r * 0.95, cy),
    ]

    # 엣지 먼저 (밑에 깔리도록)
    for name, model, role, color, sx, sy in sats:
        # halo line (glow)
        ax.plot([cx, sx], [cy, sy], color=NEON_O, linewidth=4, alpha=0.18, zorder=1)
        ax.plot([cx, sx], [cy, sy], color=NEON_O, linewidth=1.4, alpha=0.8, zorder=2)
        # arrow head on satellite end
        ax.add_patch(FancyArrowPatch((cx, cy), (sx, sy),
                                     arrowstyle="-|>", mutation_scale=14,
                                     color=NEON_O, linewidth=0, alpha=0.9, zorder=3))

    # 위성 노드
    for name, model, role, color, sx, sy in sats:
        # outer glow
        for r, a in [(0.95, 0.12), (0.75, 0.22)]:
            ax.add_patch(Circle((sx, sy), r, facecolor=color, alpha=a,
                                edgecolor="none", zorder=3))
        # solid disc
        ax.add_patch(Circle((sx, sy), 0.55, facecolor=PANEL2,
                            edgecolor=color, linewidth=1.6, zorder=4))
        # icon (filled small dot)
        ax.add_patch(Circle((sx, sy + 0.06), 0.12, facecolor=color,
                            edgecolor="none", zorder=5))
        # label below
        ax.text(sx, sy - 0.95, name, fontsize=11, fontweight="bold",
                color=TEXT, ha="center", zorder=5)
        # model chip
        ax.text(sx, sy - 1.25, model, fontsize=8.5, color=color,
                ha="center", zorder=5, family="monospace")
        # role
        ax.text(sx, sy - 1.55, role, fontsize=9, color=DIM,
                ha="center", zorder=5)

    # 중앙 Orchestrator — 큰 노드 with neon orange glow
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

    # 좌측 그래프 캡션
    ax.text(cx, 0.95, "역할 분리 → 각 에이전트 독립 교체 가능",
            fontsize=10, color=DIM, ha="center", style="italic")

    # ───────── 우측 패널: 메모리 압축 + KPI
    # 우측 패널 박스
    panel_x, panel_w = 8.5, 5.3
    ax.add_patch(FancyBboxPatch((panel_x, 1.0), panel_w, 6.6,
                                boxstyle="round,pad=0.04,rounding_size=0.15",
                                facecolor=PANEL, edgecolor=LINEC, linewidth=0.8,
                                zorder=2))

    # 우측 ❶ 메모리 압축 시퀀스
    ax.text(panel_x + 0.35, 7.15, "MEMORY COMPACTION",
            fontsize=9.5, fontweight="bold", color=NEON_O, family="monospace")
    ax.text(panel_x + 0.35, 6.78, "5턴마다 요약 → 입력 토큰 일정",
            fontsize=10.5, color=TEXT)

    # 시퀀스 도형: T1-T5 → 요약 → T6-T10 → 요약 → T11-T12
    seq_y = 5.9
    seq_x0 = panel_x + 0.35
    boxes = [
        ("T1", "dim"), ("T2", "dim"), ("T3", "dim"), ("T4", "dim"), ("T5", "dim"),
        ("Σ1", "neon"),
        ("T6", "dim"), ("T7", "dim"), ("T8", "dim"), ("T9", "dim"), ("T10", "dim"),
        ("Σ2", "neon"),
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
            "Orchestrator 입력 = [요약본 + 최근 2턴]  ≈ 8K tokens (통화 길이 무관)",
            fontsize=9, color=DIM)

    # 구분선
    ax.plot([panel_x + 0.35, panel_x + panel_w - 0.35], [5.05, 5.05],
            color=LINEC, linewidth=0.6)

    # 우측 ❷ KPI 임팩트 — 큰 숫자
    ax.text(panel_x + 0.35, 4.65, "IMPACT", fontsize=9.5, fontweight="bold",
            color=NEON_O, family="monospace")

    kpis = [
        (panel_x + 0.35, 3.65, "1.5s", "응답 지연 상한", NEON_S),
        (panel_x + 2.05, 3.65, "-62%", "토큰 비용", NEON_O),
        (panel_x + 3.75, 3.65, "∞", "통화 길이", NEON_B),
    ]
    for x, y, val, lbl, c in kpis:
        ax.text(x, y, val, fontsize=28, fontweight="bold", color=c,
                family="Apple SD Gothic Neo",
                path_effects=[pe.withStroke(linewidth=4, foreground=PANEL)])
        ax.text(x, y - 0.65, lbl, fontsize=9, color=DIM)

    # 구분선
    ax.plot([panel_x + 0.35, panel_x + panel_w - 0.35], [2.65, 2.65],
            color=LINEC, linewidth=0.6)

    # 우측 ❸ 티어링
    ax.text(panel_x + 0.35, 2.25, "MODEL TIERING", fontsize=9.5, fontweight="bold",
            color=NEON_O, family="monospace")
    tier_y = 1.65
    tiers = [
        ("OPUS", "×1", NEON_O),
        ("SONNET", "×3", NEON_S),
        ("HAIKU", "×1", NEON_B),
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

    # 하단 문제 정의 — 모노톤 한 줄
    ax.add_patch(FancyBboxPatch((0.3, 0.15), 13.4, 0.55,
                                boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor=PANEL, edgecolor=LINEC, linewidth=0.6))
    ax.text(0.55, 0.42, "PROBLEM", fontsize=9, fontweight="bold",
            color=NEON_R, family="monospace", va="center")
    ax.text(2.0, 0.42,
            "단일 LLM → 30분~2h 통화 시 컨텍스트 200K 누적 → 응답 지연 · 환각 · 페르소나 붕괴",
            fontsize=10, color=TEXT, va="center")

    save_dark(fig, "10_multi_agent.png", BG)


def save_dark(fig, name, bg):
    """dark-mode 다이어그램 저장."""
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=bg)
    plt.close(fig)
    print(f"[OK·DARK] {path.name}")


def fallback_loop():
    """11_fallback_loop.png — 학습 안 된 시나리오 fallback + Active Learning 루프."""
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("예외 시나리오 처리  —  Fallback + Active Learning 루프",
                 fontsize=16, fontweight="bold", color=NAVY, pad=12)

    # 좌측: 실시간 분기
    ax.add_patch(FancyBboxPatch((0.3, 7.5), 6.5, 2.0,
                                boxstyle="round,pad=0.04,rounding_size=0.12",
                                facecolor=ORANGE, edgecolor=ORANGE, alpha=0.92))
    ax.text(3.55, 9.05, "1차 시나리오 분류기 (8종)", fontsize=12.5,
            fontweight="bold", color="white", ha="center")
    ax.text(3.55, 8.5, "검찰 · 은행 · 자녀 · 택배 · 대출 · 세무서 · 경찰 · 보안업체",
            fontsize=10, color="white", ha="center")
    ax.text(3.55, 8.0, "confidence score 계산 (0.0 ~ 1.0)",
            fontsize=10, color="white", ha="center", alpha=0.92)

    # confidence branch
    ax.add_patch(FancyArrowPatch((3.55, 7.5), (2.0, 6.2),
                                 arrowstyle="-|>", mutation_scale=18,
                                 color=SAGE, linewidth=2))
    ax.add_patch(FancyArrowPatch((3.55, 7.5), (5.2, 6.2),
                                 arrowstyle="-|>", mutation_scale=18,
                                 color=GOLD, linewidth=2))
    ax.text(2.4, 6.85, "≥ 0.6", fontsize=10, fontweight="bold", color=SAGE)
    ax.text(4.7, 6.85, "< 0.6", fontsize=10, fontweight="bold", color=GOLD)

    # left branch: known
    ax.add_patch(FancyBboxPatch((0.3, 4.5), 3.4, 1.6,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=SAGE, edgecolor=SAGE, alpha=0.92))
    ax.text(2.0, 5.78, "Known Scenario", fontsize=11, fontweight="bold",
            color="white", ha="center")
    ax.text(2.0, 5.35, "전용 페르소나 응답 분기\n예: 검찰 → 무서워하는 노인",
            fontsize=9.5, color="white", ha="center", va="center")
    ax.text(2.0, 4.78, "정보 추출 풀가동", fontsize=9.5,
            color="white", ha="center", style="italic", alpha=0.92)

    # right branch: unknown
    ax.add_patch(FancyBboxPatch((3.8, 4.5), 3.4, 1.6,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=GOLD, edgecolor=GOLD, alpha=0.92))
    ax.text(5.5, 5.78, "Unknown_Scam (fallback)", fontsize=11, fontweight="bold",
            color="white", ha="center")
    ax.text(5.5, 5.35, "일반 노인 페르소나 + 시간끌기\n정보추출은 LLM 보조로만 시도",
            fontsize=9.5, color="white", ha="center", va="center")
    ax.text(5.5, 4.78, "전체 통화 녹취 + 메타 저장",
            fontsize=9.5, color="white", ha="center", style="italic", alpha=0.92)

    # 두 분기 모두 정보 허브로
    ax.add_patch(FancyArrowPatch((2.0, 4.5), (3.6, 3.4),
                                 arrowstyle="-|>", mutation_scale=16,
                                 color=SLATE, linewidth=1.5))
    ax.add_patch(FancyArrowPatch((5.5, 4.5), (3.9, 3.4),
                                 arrowstyle="-|>", mutation_scale=16,
                                 color=SLATE, linewidth=1.5))

    ax.add_patch(FancyBboxPatch((1.8, 2.3), 4.0, 1.1,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=INK, edgecolor=INK, alpha=0.92))
    ax.text(3.8, 3.0, "정보 허브 (통신사·경찰망 자동 신고)",
            fontsize=10.5, fontweight="bold", color="white", ha="center")
    ax.text(3.8, 2.55, "신고 우선순위: Known(자동 차단) / Unknown(수동 검토 큐)",
            fontsize=9, color="white", ha="center", alpha=0.92)

    # 우측: Active Learning 루프 (수직)
    ax.add_patch(FancyBboxPatch((7.6, 7.5), 6.1, 2.0,
                                boxstyle="round,pad=0.04,rounding_size=0.12",
                                facecolor=DUSK, edgecolor=DUSK, alpha=0.92))
    ax.text(10.65, 9.05, "Active Learning 루프 (주간 배치)", fontsize=12.5,
            fontweight="bold", color="white", ha="center")
    ax.text(10.65, 8.5, "Unknown_Scam 통화 집계 → 클러스터링 → 라벨링 후보 추출",
            fontsize=10, color="white", ha="center")
    ax.text(10.65, 8.0, "법무·운영 검토 → 9번째 시나리오 등재",
            fontsize=10, color="white", ha="center", alpha=0.92)

    # active learning steps
    steps = [
        (8.0, 6.4, "1. 수집", "Unknown 통화\n전사·메타데이터"),
        (9.6, 6.4, "2. 클러스터링", "LLM embedding\nk-means/HDBSCAN"),
        (11.2, 6.4, "3. 라벨링", "운영자 1회 검토\n새 시나리오 명명"),
        (12.8, 6.4, "4. 재학습", "분류기 파인튜닝\n+ 페르소나 추가"),
    ]
    for x, y, title, body in steps:
        ax.add_patch(FancyBboxPatch((x - 0.7, y - 0.85), 1.4, 1.7,
                                    boxstyle="round,pad=0.04,rounding_size=0.1",
                                    facecolor="white", edgecolor=DUSK, linewidth=1.5))
        ax.text(x, y + 0.55, title, fontsize=9.8, fontweight="bold",
                color=DUSK, ha="center")
        ax.text(x, y - 0.1, body, fontsize=8.8, color=SLATE,
                ha="center", va="center")

    for x_from, x_to in [(8.0, 9.6), (9.6, 11.2), (11.2, 12.8)]:
        ax.add_patch(FancyArrowPatch((x_from + 0.7, 6.4), (x_to - 0.7, 6.4),
                                     arrowstyle="-|>", mutation_scale=16,
                                     color=DUSK, linewidth=1.5))

    # loop back arrow from step 4 → 1차 분류기
    ax.add_patch(FancyArrowPatch((12.8, 5.55), (12.8, 4.6),
                                 arrowstyle="-", color=DUSK, linewidth=1.5, linestyle="--"))
    ax.add_patch(FancyArrowPatch((12.8, 4.6), (3.55, 4.6),
                                 arrowstyle="-", color=DUSK, linewidth=1.5, linestyle="--"))
    ax.add_patch(FancyArrowPatch((3.55, 4.6), (3.55, 7.4),
                                 arrowstyle="-|>", mutation_scale=16,
                                 color=DUSK, linewidth=1.5, linestyle="--"))
    ax.text(8.0, 4.4, "분류기 업데이트 (월 1회 배포)",
            fontsize=10, fontweight="bold", color=DUSK, ha="center")

    # 하단 결과 박스
    ax.add_patch(FancyBboxPatch((7.6, 2.3), 6.1, 1.1,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=SAGE, edgecolor=SAGE, alpha=0.92))
    ax.text(10.65, 3.0, "확장성 효과", fontsize=10.5,
            fontweight="bold", color="white", ha="center")
    ax.text(10.65, 2.55, "8종 → 12종 → 16종으로 시나리오 자동 확장 가능",
            fontsize=9.5, color="white", ha="center", alpha=0.96)

    # 하단 메시지
    ax.text(7, 1.2,
            "→ \"학습 안 된 사기\"도 통화는 끊지 않고 정보 수집·신고로 흡수, 시스템은 매주 똑똑해진다",
            fontsize=11, fontweight="bold", color=NAVY, ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=GOLD, alpha=0.25,
                      edgecolor=GOLD, linewidth=1.5))

    save(fig, "11_fallback_loop.png")


def demo_layout():
    """12_demo_layout.png — 본선 시연 화면 3분할 mockup."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title("본선 라이브 시연 화면 구성  —  3분할 동시 가시화",
                 fontsize=16, fontweight="bold", color=NAVY, pad=10)

    # 좌측 패널: 사기범 음성 파형
    ax.add_patch(FancyBboxPatch((0.3, 1.0), 4.3, 7.0,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=INK, edgecolor=INK))
    ax.text(2.45, 7.5, "LEFT  ·  사기범 입력 음성", fontsize=11,
            fontweight="bold", color="white", ha="center")
    ax.text(2.45, 7.05, "(녹음 파일 재생)", fontsize=9, color=MID, ha="center")
    # 가짜 waveform
    rng = np.random.default_rng(7)
    t = np.linspace(0.6, 4.0, 240)
    wave = (np.sin(t * 8) + 0.6 * np.sin(t * 15) + 0.4 * np.sin(t * 25)) * \
           (0.6 + 0.4 * np.sin(t * 0.5))
    wave *= rng.uniform(0.5, 1.0, size=len(t))
    ax.plot(t, 5.0 + wave * 0.8, color=ORANGE, linewidth=1)
    ax.plot(t, 5.0 - wave * 0.8, color=ORANGE, linewidth=1)
    ax.fill_between(t, 5.0 - wave * 0.8, 5.0 + wave * 0.8, color=ORANGE, alpha=0.25)
    ax.add_patch(Rectangle((0.7, 2.2), 3.5, 1.4, facecolor=BURNT, alpha=0.25,
                           edgecolor=ORANGE, linewidth=1))
    ax.text(2.45, 3.2, "[검찰입니다. 김지수 씨 통장이...]",
            fontsize=10, color="white", ha="center", style="italic")
    ax.text(2.45, 2.7, "(시연용 더미 대본)", fontsize=8.5, color=MID, ha="center")
    ax.text(2.45, 1.5, "▶ 00:42 / 02:15", fontsize=10, fontweight="bold",
            color="white", ha="center")

    # 중앙 패널: 멀티에이전트 활동
    ax.add_patch(FancyBboxPatch((4.8, 1.0), 4.4, 7.0,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=CREAM, edgecolor=ORANGE, linewidth=2))
    ax.text(7.0, 7.5, "CENTER  ·  멀티 에이전트 동작",
            fontsize=11, fontweight="bold", color=BURNT, ha="center")
    ax.text(7.0, 7.05, "(실시간 처리 중인 에이전트가 깜빡임)",
            fontsize=9, color=SLATE, ha="center")

    agent_states = [
        (5.2, 6.0, "Orchestrator", "Opus", "분기 결정 중", BURNT, True),
        (5.2, 5.0, "Persona", "Sonnet", "응답 생성", ORANGE, True),
        (5.2, 4.0, "Memory", "Sonnet", "T+38 압축 완료", DUSK, False),
        (5.2, 3.0, "Extractor", "Sonnet", "계좌 추출 시도", SAGE, True),
        (5.2, 2.0, "Safety", "Haiku", "OK", PURPLE, False),
    ]
    for x, y, name, model, state, c, active in agent_states:
        edge = c if active else MID
        lw = 2 if active else 0.8
        ax.add_patch(FancyBboxPatch((x, y - 0.32), 3.6, 0.7,
                                    boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor="white", edgecolor=edge, linewidth=lw))
        ax.scatter(x + 0.25, y + 0.02, s=70, color=c if active else MID,
                   zorder=3)
        ax.text(x + 0.5, y + 0.13, f"{name}", fontsize=10, fontweight="bold",
                color=INK, va="center")
        ax.text(x + 0.5, y - 0.13, f"[{model}]  {state}", fontsize=8.5,
                color=SLATE, va="center")

    # 우측 패널: 추출 정보 실시간
    ax.add_patch(FancyBboxPatch((9.4, 1.0), 4.3, 7.0,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=WARM, edgecolor=SAGE, linewidth=2))
    ax.text(11.55, 7.5, "RIGHT  ·  실시간 추출 결과",
            fontsize=11, fontweight="bold", color=SAGE, ha="center")
    ax.text(11.55, 7.05, "(허브로 전송되는 데이터)", fontsize=9,
            color=SLATE, ha="center")

    fields = [
        ("시나리오", "검찰 사칭", "98%", SAGE),
        ("음성지문", "VP-3a8f...", "신규", ORANGE),
        ("계좌", "농협 301-XX-XX", "검출", BURNT),
        ("URL", "—", "—", MID),
        ("악성앱", "—", "—", MID),
        ("발신번호", "+82-10-XXXX", "변조 의심", RED),
        ("통화시간", "00:42 → 진행 중", "", DUSK),
    ]
    for i, (k, v, badge, c) in enumerate(fields):
        y = 6.3 - i * 0.65
        ax.add_patch(Rectangle((9.7, y - 0.22), 3.7, 0.5,
                               facecolor="white", edgecolor=LINE, linewidth=0.8))
        ax.text(9.85, y, k, fontsize=9.5, fontweight="bold", color=SLATE, va="center")
        ax.text(11.1, y, v, fontsize=9.5, color=INK, va="center")
        if badge and badge != "—":
            ax.add_patch(FancyBboxPatch((13.0, y - 0.13), 0.3, 0.26,
                                        boxstyle="round,pad=0.02,rounding_size=0.06",
                                        facecolor=c, edgecolor=c, alpha=0.92))
            ax.text(13.15, y, badge, fontsize=7.5, color="white",
                    ha="center", va="center", fontweight="bold")

    # 하단 메시지
    ax.text(7, 0.5,
            "사기범 음성 → 멀티에이전트 동작 → 추출 결과를 동시에 보여줌으로써 \"무엇이 일어나는지\" 한눈에 전달",
            fontsize=10.5, color=NAVY, ha="center", style="italic")

    save(fig, "12_demo_layout.png")


def consent_split():
    """13_consent_split.png — 데이터 수집 동의 경로 2분할."""
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title("데이터 수집 경로 분리  —  사기범 측 vs 사용자 측 (동의 모델)",
                 fontsize=16, fontweight="bold", color=NAVY, pad=10)

    # 좌측: 사기범 측
    ax.add_patch(FancyBboxPatch((0.3, 1.5), 6.0, 6.5,
                                boxstyle="round,pad=0.05,rounding_size=0.15",
                                facecolor=ORANGE, edgecolor=ORANGE, alpha=0.92))
    ax.text(3.3, 7.3, "A.  사기범 측 수집", fontsize=14, fontweight="bold",
            color="white", ha="center")
    ax.text(3.3, 6.8, "(미끼번호 → 사기범 발신)", fontsize=10,
            color="white", ha="center", alpha=0.92)

    a_items = [
        ("데이터", "사기범 음성·계좌·시나리오"),
        ("동의 주체", "필요 없음"),
        ("법적 근거", "통신비밀보호법 §14\n(1자 동의 원칙)"),
        ("판례", "대법원 2008도1237\n— 통화 당사자 녹음 합법"),
        ("UX 요구", "없음 (사기범이 자발 발신)"),
    ]
    for i, (k, v) in enumerate(a_items):
        y = 6.0 - i * 0.95
        ax.add_patch(FancyBboxPatch((0.6, y - 0.4), 5.4, 0.85,
                                    boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor="white", edgecolor="white", alpha=0.94))
        ax.text(0.85, y + 0.1, k, fontsize=9.5, fontweight="bold", color=BURNT)
        ax.text(2.3, y + 0.1, v, fontsize=9.5, color=INK, va="center")

    # 우측: 사용자 측
    ax.add_patch(FancyBboxPatch((6.7, 1.5), 6.0, 6.5,
                                boxstyle="round,pad=0.05,rounding_size=0.15",
                                facecolor=DUSK, edgecolor=DUSK, alpha=0.92))
    ax.text(9.7, 7.3, "B.  사용자 측 수집", fontsize=14, fontweight="bold",
            color="white", ha="center")
    ax.text(9.7, 6.8, "(시니어 가디언 앱 가입자)", fontsize=10,
            color="white", ha="center", alpha=0.92)

    b_items = [
        ("데이터", "통화 메타데이터 + 위험 알림"),
        ("동의 주체", "본인 + (필요시) 자녀 보호자"),
        ("법적 근거", "개인정보보호법 §15 ①1호\n— 명시적 동의"),
        ("동의 UX", "에이닷 모델 차용:\n가입 시 1회 동의 + 언제든 철회"),
        ("UX 요구", "고령자용 큰 글씨 동의서·음성 안내"),
    ]
    for i, (k, v) in enumerate(b_items):
        y = 6.0 - i * 0.95
        ax.add_patch(FancyBboxPatch((7.0, y - 0.4), 5.4, 0.85,
                                    boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor="white", edgecolor="white", alpha=0.94))
        ax.text(7.25, y + 0.1, k, fontsize=9.5, fontweight="bold", color=DUSK)
        ax.text(8.7, y + 0.1, v, fontsize=9.5, color=INK, va="center")

    # 하단
    ax.text(6.5, 0.85,
            "두 경로를 분리함으로써 \"미끼봇은 별도 동의 없이 합법 운용, 가디언 앱만 명시 동의\" 구조 확립",
            fontsize=10.5, fontweight="bold", color=NAVY, ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=GOLD, alpha=0.25,
                      edgecolor=GOLD, linewidth=1.5))

    save(fig, "13_consent_split.png")


def scope_realization():
    """14_scope_realization.png — 실구현 vs 추후고도화 (FDS 톤다운)."""
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("이번 해커톤 구현 범위  —  핵심 4개는 실제 동작, FDS는 사업화 후 PoC",
                 fontsize=15.5, fontweight="bold", color=NAVY, pad=10)

    # 좌측: 실구현 (진하게)
    ax.add_patch(FancyBboxPatch((0.3, 0.8), 7.2, 6.5,
                                boxstyle="round,pad=0.05,rounding_size=0.14",
                                facecolor=SAGE, edgecolor=SAGE, alpha=0.92))
    ax.text(3.9, 6.6, "✔  실제 구현  (Live Demo)", fontsize=14, fontweight="bold",
            color="white", ha="center")
    real = [
        ("①", "AI 미끼봇", "멀티에이전트 5종 + STT/TTS 파이프라인"),
        ("②", "정보 수집 엔진", "음성지문 DB + 시나리오 8종 분류 + 엔티티 추출"),
        ("③", "사기 시나리오 자동 분류", "8종 + Unknown fallback + Active Learning 루프"),
        ("④", "AI 자체 보안 계층", "MITRE ATLAS AML.T0043/T0048 + OWASP LLM Top10 대응"),
    ]
    for i, (idx, name, body) in enumerate(real):
        y = 5.5 - i * 1.15
        ax.add_patch(FancyBboxPatch((0.6, y - 0.45), 6.6, 0.95,
                                    boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor="white", edgecolor="white", alpha=0.95))
        ax.text(0.95, y + 0.05, idx, fontsize=20, fontweight="bold",
                color=SAGE, va="center")
        ax.text(1.65, y + 0.18, name, fontsize=11.5, fontweight="bold",
                color=INK, va="center")
        ax.text(1.65, y - 0.16, body, fontsize=9.5, color=SLATE, va="center")

    # 우측: 추후고도화 (흐리게)
    ax.add_patch(FancyBboxPatch((7.8, 0.8), 4.9, 6.5,
                                boxstyle="round,pad=0.05,rounding_size=0.14",
                                facecolor=TAN, edgecolor=MID, linewidth=1.5))
    ax.text(10.25, 6.6, "▷  v2 로드맵  (사업화 후)", fontsize=13, fontweight="bold",
            color=SLATE, ha="center")
    later = [
        ("FDS 실연계", "시중은행 PoC 계약 필요 — 1차 타겟"),
        ("통신사 미끼번호 풀", "KT 후후·SKT 협력 — MoU 단계"),
        ("경찰청 사이버수사대 연계", "디지털성범죄대응팀 채널"),
        ("다국어 사기범 응대", "중국어·러시아어 (글로벌 거점 대응)"),
        ("AML 자금세탁 영역 확장", "Hack-Back 아닌 정보전 확장"),
    ]
    for i, (name, body) in enumerate(later):
        y = 5.5 - i * 1.0
        ax.add_patch(FancyBboxPatch((8.05, y - 0.4), 4.45, 0.85,
                                    boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor="white", edgecolor=LINE, linewidth=0.8))
        ax.text(8.25, y + 0.15, name, fontsize=10.3, fontweight="bold",
                color=SLATE, va="center")
        ax.text(8.25, y - 0.16, body, fontsize=9, color=MID, va="center", style="italic")

    # 하단 메시지
    ax.text(6.5, 0.35,
            "발표·기획서는 \"오늘 동작하는 것\"과 \"내일 동작할 것\"을 명확히 구분 — 실구현 가치만으로 심사",
            fontsize=10, color=NAVY, ha="center", style="italic")

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
    print("\n=== 14종 이미지 생성 완료 ===")
