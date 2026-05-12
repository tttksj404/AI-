"""Sentinel-30 diagrams in Claude design palette (warm cream + burnt orange)."""
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
fm.fontManager.addfont(FONT_PATH)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(r"C:\Users\SSAFY\Desktop\AI해커톤\images")
OUT.mkdir(exist_ok=True)

# Claude Design official palette (Anthropic Labs)
CREAM = "#faf9f5"        # Light - primary background
TAN = "#e8e6dc"          # Light Gray - soft accent
WARM = "#f1efe6"         # tint between Light and Light Gray
INK = "#141413"          # Dark - text
SLATE = "#b0aea5"        # Mid Gray - secondary text
ORANGE = "#d97757"       # primary accent
BURNT = "#c4623f"        # darker orange for emphasis (derived)
RUST = "#a04a2a"         # deepest accent (derived)
SAGE = "#788c5d"         # tertiary green
DUSK = "#6a9bcc"         # secondary blue
GOLD = "#d97757"         # alias to orange
MAUVE = "#6a9bcc"        # alias to blue (no mauve in official palette)
LINE = "#e8e6dc"         # subtle divider = Light Gray


def save(fig, name, dpi=200):
    fig.patch.set_facecolor(CREAM)
    path = OUT / name
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=CREAM)
    plt.close(fig)
    print(f"[OK] {path.name}")


# ========== 1. 시스템 아키텍처 ==========
def system_architecture():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_facecolor(CREAM)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Sentinel-30 시스템 아키텍처",
                 fontsize=19, fontweight="bold", color=INK, pad=15,
                 fontname="Malgun Gothic")

    layers = [
        (1, 8.2, 12, 1.2, "① 미끼번호 풀 (통신사 협력)",
         "비활성 번호 N만 개를 미끼로 등록 → 사기범 무작위 발신 유입", ORANGE),
        (1, 6.4, 12, 1.4, "② AI 미끼봇 (Honeypot Bot)",
         "한국어 STT  +  노인 페르소나 LLM (가드레일)  +  한국어 TTS  →  평균 30분~2h 통화 유지", BURNT),
        (1, 4.6, 12, 1.4, "③ 정보 수집 엔진",
         "음성 지문화 · 사기 시나리오 분류 · 계좌·URL·악성앱 패키지명 추출 · 발신 메타데이터", MAUVE),
        (1, 2.5, 12, 1.6, "④ 실시간 정보전 허브  (가명처리 + 암호화)",
         "시중은행 FDS 즉시 동결  │  통신사 번호 차단  │  경찰청 사이버수사대  │  금감원 24h 자동 신고",
         SAGE),
        (1, 0.4, 12, 1.4, "⑤ 시니어 가디언 앱 (옵션)",
         "부모 통화 위험 감지 → 자녀 푸시 · 1억 이상 송금 5분 내 자녀 거부권", GOLD),
    ]

    for x, y, w, h, title, sub, c in layers:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.18",
                             facecolor=c, edgecolor="none", alpha=0.94)
        ax.add_patch(box)
        ax.text(x + 0.35, y + h - 0.35, title,
                fontsize=13.5, fontweight="bold", color="white", va="top")
        ax.text(x + 0.35, y + h - 0.9, sub,
                fontsize=10.5, color="white", va="top", alpha=0.96)

    for y1, y2 in [(8.15, 7.85), (6.35, 6.05), (4.55, 4.15), (2.45, 2.05)]:
        arr = FancyArrowPatch((7, y1), (7, y2),
                              arrowstyle="-|>", mutation_scale=22,
                              color=SLATE, linewidth=2)
        ax.add_patch(arr)
    save(fig, "01_architecture.png")


# ========== 2. 30분 골든타임 ==========
def golden_timeline():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.set_facecolor(CREAM)
    ax.set_xlim(-5, 70)
    ax.set_ylim(-3, 5)
    ax.axis("off")
    ax.set_title("30분 골든타임 — 사기 산업의 시간 약탈 구조",
                 fontsize=18, fontweight="bold", color=INK, pad=10)

    ax.plot([0, 65], [0, 0], color=SLATE, linewidth=3, zorder=1)
    ax.add_patch(Rectangle((0, -0.3), 30, 0.6, facecolor=GOLD, alpha=0.32, zorder=0))
    ax.add_patch(Rectangle((30, -0.3), 35, 0.6, facecolor=RUST, alpha=0.25, zorder=0))
    ax.text(15, -1.3, "Golden Time (30분)", fontsize=12.5, fontweight="bold",
            color=BURNT, ha="center")
    ax.text(47, -1.3, "추적 불가 구간", fontsize=12.5, fontweight="bold",
            color=RUST, ha="center")

    events = [
        (0, "T+0", "통화 시작", ORANGE),
        (15, "T+15", "송금 완료\n(피해자 평균)", GOLD),
        (30, "T+30", "사기범 계좌\n인출 시작", BURNT),
        (60, "T+60", "자금 추적\n불가 영역", RUST),
    ]
    for x, label, desc, c in events:
        ax.scatter(x, 0, s=280, color=c, zorder=3,
                   edgecolor=CREAM, linewidth=2.5)
        ax.text(x, 0.65, label, fontsize=11.5, fontweight="bold",
                color=c, ha="center")
        ax.text(x, 2.0, desc, fontsize=10.5, color=SLATE, ha="center", va="center")

    ax.annotate("Sentinel-30 개입 구간\n사기범 시간 약탈 + FDS 즉시 동결",
                xy=(15, -0.3), xytext=(15, -2.5),
                fontsize=11.5, fontweight="bold", color=SAGE, ha="center",
                arrowprops=dict(arrowstyle="->", color=SAGE, lw=2))
    save(fig, "02_golden_timeline.png")


# ========== 3. SWOT ==========
def swot_matrix():
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_facecolor(CREAM)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("SWOT 분석", fontsize=19, fontweight="bold", color=INK, pad=10)

    cells = [
        (0.3, 5.3, 5.7, 4.3, "Strengths (강점)", [
            "• Active Defense 프레임 — 국내 유일 차별화",
            "• 영국 Daisy AI 벤치마크 + 한국 맞춤 설계",
            "• 6개 법령 합법성 검토 완료 (법리 트랙)",
            "• MITRE ATLAS · OWASP LLM 위협 모델 통합",
            "• 70대 5명 사용성 인터뷰 — UX 정성 근거",
        ], SAGE),
        (6.0, 5.3, 5.7, 4.3, "Weaknesses (약점)", [
            "• 통신사·은행 제휴 없으면 미끼번호 풀 확보 난항",
            "• 한국어 노년 화자 STT 학습 데이터 부족",
            "• AI 인간 사칭 — AI 기본법 시행령 미확정",
            "• 6인 팀 4주 — 풀스택 구현 한계 (모킹 의존)",
            "• 사기범 음성지문 오인식 시 명예훼손 리스크",
        ], GOLD),
        (0.3, 0.5, 5.7, 4.3, "Opportunities (기회)", [
            "• 2024 보이스피싱 피해 1.97조 — 사회적 압박 최고",
            "• 금감원 · 금융보안원 사기 대응 예산 확대",
            "• 영국 Ofcom 적법성 인증 — 국제 선례 존재",
            "• AI 기본법 (2026 시행) — 공공안전 예외 등록 가능",
            "• 시중은행 FDS 고도화 수요 (제휴 PoC 기회)",
        ], ORANGE),
        (6.0, 0.5, 5.7, 4.3, "Threats (위협)", [
            "• 사기범의 적대적 공격 — TTS 합성음 식별 회피",
            "• 통신사 약관 · 전기통신사업법 해석 변동",
            "• 경찰청 · 금감원 데이터 공유 채널 정치적 변수",
            "• 글로벌 사기 거점(중국·동남아) 협조 한계",
            "• 유사 솔루션 (KT 후후·시티즌코난) 기능 흡수",
        ], BURNT),
    ]

    for x, y, w, h, title, items, c in cells:
        bg = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                            facecolor=WARM, edgecolor=c, linewidth=2.2)
        ax.add_patch(bg)
        # color bar
        ax.add_patch(FancyBboxPatch((x, y + h - 0.8), w, 0.8,
                                    boxstyle="round,pad=0.05,rounding_size=0.15",
                                    facecolor=c, edgecolor="none", alpha=0.92))
        ax.text(x + 0.3, y + h - 0.4, title,
                fontsize=14, fontweight="bold", color="white", va="center")
        for k, item in enumerate(items):
            ax.text(x + 0.3, y + h - 1.45 - k * 0.55, item,
                    fontsize=10.3, color=INK, va="top")
    save(fig, "03_swot.png")


# ========== 4. 리스크 매트릭스 ==========
def risk_matrix():
    fig, ax = plt.subplots(figsize=(11, 9))
    ax.set_facecolor(CREAM)
    ax.set_title("리스크 매트릭스 — 발생확률 × 영향도",
                 fontsize=18, fontweight="bold", color=INK, pad=15)

    # gradient on official palette (Light Gray -> Orange tints)
    grid_colors = [
        ["#e8e6dc", "#f0d9c8", "#ecbfa6"],
        ["#f0d9c8", "#ecbfa6", "#e3a07f"],
        ["#ecbfa6", "#e3a07f", "#d97757"],
    ]
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((j + 0.5, i + 0.5), 1, 1,
                                   facecolor=grid_colors[i][j],
                                   edgecolor=CREAM, linewidth=3))

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["하 (Low)", "중 (Mid)", "상 (High)"], fontsize=11, color=INK)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["하 (Low)", "중 (Mid)", "상 (High)"], fontsize=11, color=INK)
    ax.set_xlabel("영향도", fontsize=13, fontweight="bold", color=INK)
    ax.set_ylabel("발생 확률", fontsize=13, fontweight="bold", color=INK)
    ax.set_xlim(0.4, 3.6)
    ax.set_ylim(0.4, 3.6)
    ax.tick_params(axis="both", colors=SLATE)
    for spine in ax.spines.values():
        spine.set_color(LINE)

    risks = [
        (3, 3, "R1"), (2, 3, "R2"), (2, 2, "R3"),
        (3, 2, "R4"), (2, 3, "R5"), (3, 2, "R6"),
    ]
    placed = {}
    for p, im, label in risks:
        key = (p, im)
        n = placed.get(key, 0)
        dx = (n % 2) * 0.28 - 0.14
        dy = (n // 2) * 0.28 - 0.14
        placed[key] = n + 1
        ax.scatter(im + dx, p + dy, s=1000, color=BURNT,
                   edgecolor=CREAM, linewidth=2.5, zorder=3)
        ax.text(im + dx, p + dy, label,
                fontsize=10, color="white", fontweight="bold",
                ha="center", va="center", zorder=4)

    legend_text = (
        "R1 미끼봇 협박·모욕 발화      R2 실존 제3자 정보 노출\n"
        "R3 사기범 데이터 무기한 보관   R4 음성지문 오인식 (선의 일반인)\n"
        "R5 통신사 약관·전기통신사업법  R6 AI 인간 사칭 (AI 기본법)"
    )
    ax.text(0.4, -0.15, legend_text, fontsize=9.5, color=SLATE,
            transform=ax.transAxes, va="top")
    save(fig, "04_risk_matrix.png")


# ========== 5. KPI 대시보드 ==========
def kpi_dashboard():
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5))
    fig.patch.set_facecolor(CREAM)
    fig.suptitle("KPI 대시보드 — 기존 솔루션 대비 Sentinel-30",
                 fontsize=18, fontweight="bold", color=INK, y=1.02)

    kpis = [
        ("탐지율", [78, 87], "%", ORANGE),
        ("사기범 시간 약탈\n(분/통화)", [0, 30], "분", SAGE),
        ("환수 골든타임\n(분)", [240, 30], "분", GOLD),
        ("법정 신고시한\n(24h) 충족률", [65, 100], "%", BURNT),
    ]
    for ax, (title, vals, unit, c) in zip(axes, kpis):
        ax.set_facecolor(CREAM)
        bars = ax.bar(["기존", "Sentinel-30"], vals,
                      color=[TAN, c], edgecolor=CREAM, linewidth=2)
        ax.set_title(title, fontsize=12, fontweight="bold", color=INK)
        ax.set_ylim(0, max(vals) * 1.25 if max(vals) > 0 else 50)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(LINE)
        ax.spines["left"].set_color(LINE)
        ax.tick_params(axis="y", labelsize=9, colors=SLATE)
        ax.tick_params(axis="x", labelsize=10.5, colors=INK)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(vals) * 0.03,
                    f"{v}{unit}", ha="center", fontsize=11.5,
                    fontweight="bold", color=INK)
    plt.tight_layout()
    save(fig, "05_kpi_dashboard.png")


# ========== 6. 7대 레이어 ==========
def seven_layers():
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_facecolor(CREAM)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.set_title("Sentinel-30 7대 레이어",
                 fontsize=19, fontweight="bold", color=INK, pad=10)

    layers = [
        ("1", "AI 미끼봇", "한국어 LLM + 노인 페르소나\n+ 음성합성", ORANGE),
        ("2", "정보 수집 엔진", "음성지문 · 계좌 · 시나리오\n자동 추출", MAUVE),
        ("3", "실시간 정보전 허브", "FDS · 통신사 · 경찰망\n데이터 자동 공급", SAGE),
        ("4", "AI 자체 보안", "OWASP LLM Top 10\n+ MITRE ATLAS 대응", DUSK),
        ("5", "IR 워크플로우", "금융보안원 가이드 기반\nCISO · 금감원 자동보고", INK),
        ("6", "법적 안전지대", "6개 법령 합법성 검토\n+ 6대 리스크 방어책", GOLD),
        ("7", "시니어 UX", "70대 5명 인터뷰\n가족 동반 알림", BURNT),
    ]

    cols, rows = 4, 2
    cw, ch = 3.0, 3.4
    x0, y0 = 0.7, 0.6
    gap_x, gap_y = 0.3, 0.4

    for idx, (num, title, sub, c) in enumerate(layers):
        col = idx % cols
        row = 1 - idx // cols
        x = x0 + col * (cw + gap_x)
        y = y0 + row * (ch + gap_y)
        box = FancyBboxPatch((x, y), cw, ch,
                             boxstyle="round,pad=0.05,rounding_size=0.22",
                             facecolor=c, edgecolor="none", alpha=0.94)
        ax.add_patch(box)
        ax.text(x + 0.35, y + ch - 0.45, num,
                fontsize=34, fontweight="bold", color="white", alpha=0.5, va="top")
        ax.text(x + cw / 2, y + ch - 1.15, title,
                fontsize=14.5, fontweight="bold", color="white", ha="center", va="top")
        ax.text(x + cw / 2, y + ch - 2.05, sub,
                fontsize=10.5, color="white", ha="center", va="top", alpha=0.96)
    save(fig, "06_seven_layers.png")


# ========== 7. 페르소나 ==========
def personas():
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.patch.set_facecolor(CREAM)
    fig.suptitle("핵심 페르소나 — 3종",
                 fontsize=18, fontweight="bold", color=INK, y=1.02)

    cards = [
        {
            "name": "박○○ (72세, 여)",
            "role": "주 피해 타겟",
            "color": GOLD,
            "pain": "검찰 사칭 통화 시 인지 트랜스에 빠짐\n자녀에게 연락 못 하고 송금",
            "needs": "큰 글씨 경고 + 자녀 자동 알림\n송금 직전 가족 거부권",
            "scenario": "검찰 사칭 → 미끼봇이 가로채\n→ 자녀 푸시 → 5분 내 차단",
        },
        {
            "name": "김○○ (38세, 남)",
            "role": "은행 디지털보안 담당자",
            "color": ORANGE,
            "pain": "FDS 룰 업데이트가 사후적\n환수 골든타임 항상 놓침",
            "needs": "사기범 계좌 실시간 자동 피드\n금감원 24h 자동 신고",
            "scenario": "허브 API 연동 → FDS 즉시 동결\n→ IR 플레이북 자동 실행",
        },
        {
            "name": "이○○ (45세, 여)",
            "role": "고령 부모 둔 자녀",
            "color": SAGE,
            "pain": "부모 통화 인지 불가\n사후 신고만 가능",
            "needs": "부모 위험 통화 실시간 푸시\n원격 송금 차단 권한",
            "scenario": "가디언 앱 알림 → 통화 가로채기\n→ 가족 3자 통화 전환",
        },
    ]

    for ax, p in zip(axes, cards):
        ax.set_facecolor(CREAM)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        c = p["color"]

        ax.add_patch(FancyBboxPatch((0.2, 7.6), 9.6, 2.0,
                                    boxstyle="round,pad=0.05,rounding_size=0.2",
                                    facecolor=c, edgecolor="none", alpha=0.94))
        ax.text(5, 8.9, p["name"], fontsize=14.5, fontweight="bold",
                color="white", ha="center")
        ax.text(5, 8.0, p["role"], fontsize=11, color="white",
                ha="center", alpha=0.94)

        sections = [
            ("Pain Point", p["pain"], 5.2),
            ("Needs", p["needs"], 3.0),
            ("Scenario", p["scenario"], 0.8),
        ]
        for label, body, y in sections:
            ax.add_patch(FancyBboxPatch((0.2, y), 9.6, 2.0,
                                        boxstyle="round,pad=0.05,rounding_size=0.15",
                                        facecolor=WARM, edgecolor=c, linewidth=1.8))
            ax.text(0.5, y + 1.65, label, fontsize=10.8,
                    fontweight="bold", color=c)
            ax.text(0.5, y + 0.55, body, fontsize=10, color=INK)
    plt.tight_layout()
    save(fig, "07_personas.png")


# ========== 8. ROI 메커니즘 ==========
def roi_mechanism():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_facecolor(CREAM)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("사기 산업 ROI 파괴 메커니즘",
                 fontsize=18, fontweight="bold", color=INK, pad=10)

    ax.text(0.5, 5.8, "사기 산업 총수입", fontsize=13.5,
            fontweight="bold", color=INK)
    eq = "= [발신 통화 수] × [성공률] × [건당 피해액]  -  [운영 비용]"
    ax.text(0.5, 5.1, eq, fontsize=12, color=SLATE)

    attacks = [
        (3.5, "통화 수 ↓", "미끼번호 풀이 사기범 발신을\n실제 피해자가 아닌 봇으로 흡수", ORANGE),
        (7.0, "성공률 ↓", "미끼봇 정보 → FDS 즉시 동결\n→ 송금 시도 차단", SAGE),
        (10.5, "운영 비용 ↑", "사기범 시간을 30분~2h 약탈\n시간당 매출 무너짐", BURNT),
    ]
    for x, title, desc, c in attacks:
        box = FancyBboxPatch((x - 1.7, 2.0), 3.4, 2.5,
                             boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=c, edgecolor="none", alpha=0.94)
        ax.add_patch(box)
        ax.text(x, 4.0, title, fontsize=14, fontweight="bold",
                color="white", ha="center")
        ax.text(x, 2.85, desc, fontsize=10.3, color="white",
                ha="center", va="center", alpha=0.96)
        arr = FancyArrowPatch((x, 4.7), (x, 4.55),
                              arrowstyle="-|>", mutation_scale=18,
                              color=SLATE, linewidth=1.5)
        ax.add_patch(arr)

    ax.text(7, 0.7,
            "→ 산업의 시간당 매출이 0에 수렴할 때 사기 콜센터형 조직은 자연 붕괴",
            fontsize=12, fontweight="bold", color=INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=TAN, alpha=0.7,
                      edgecolor=GOLD, linewidth=1.5))
    save(fig, "08_roi_mechanism.png")


# ========== 9. 간트차트 ==========
def gantt():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_facecolor(CREAM)
    ax.set_title("프로젝트 일정 (예선 4주 + 본선 2일)",
                 fontsize=18, fontweight="bold", color=INK, pad=10)

    tasks = [
        ("법리 검토서 작성", 0, 2, INK),
        ("70대 사용성 인터뷰", 1, 2, ORANGE),
        ("LLM 페르소나 프로토타입", 1, 2.5, MAUVE),
        ("시연 영상 시안", 2, 1.5, DUSK),
        ("기획서 v1.0", 2, 1.5, SAGE),
        ("최종 발표자료 + 시연 영상", 3, 1, GOLD),
        ("적대적 공격 시연 준비", 3, 1, BURNT),
    ]
    for i, (name, start, dur, c) in enumerate(tasks):
        ax.barh(i, dur, left=start, color=c, edgecolor=CREAM, linewidth=2,
                height=0.65)
        ax.text(start + dur / 2, i, name, fontsize=10.2, color="white",
                ha="center", va="center", fontweight="bold")

    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([""] * len(tasks))
    ax.invert_yaxis()
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_xticklabels(["W1", "W2", "W3", "W4", "본선"], fontsize=11, color=INK)
    ax.set_xlim(-0.2, 4.5)
    ax.grid(axis="x", alpha=0.25, color=LINE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.spines["left"].set_color(LINE)
    ax.axvline(4, color=BURNT, linestyle="--", linewidth=1.5, alpha=0.65)
    ax.text(4.25, -0.5, "본선 무박 2일",
            fontsize=11, fontweight="bold", color=BURNT)
    save(fig, "09_gantt.png")


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
    print("\n전체 이미지 생성 완료 (Claude palette)")
