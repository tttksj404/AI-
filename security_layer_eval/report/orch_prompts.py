"""역할별 시스템 프롬프트 + 설계 의도 설명 이미지.

각 역할(라우터/응대/추출/압축/기획)이 실제로 어떤 프롬프트를 쓰는지 전문을 싣고,
'왜 이렇게 설계했나'를 함께 보여 주는 발표용 카드형 이미지.

출력: results/fig_orch_prompts.png
실행: python report/orch_prompts.py
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
CODE_BG = "#f4f1ea"

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


def txt(ax, x, y, s, color=TEXT, fs=10, bold=False, ha="left", va="top", z=4, mono=False):
    kw = {}
    if mono:
        kw["family"] = "monospace"
    ax.text(x, y, s, ha=ha, va=va, color=color, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=z, **kw)


# ── 역할 카드 정의 (실제 프롬프트 전문 + 설계 의도) ─────────────────
# prompt 는 roles.py 의 실제 문자열을 그대로 옮긴 것.
CARDS = [
    {
        "tag": "라우터 (Router)",
        "accent": ORANGE,
        "placement": "결정론 · LLM 아님 · 매 턴 · 비용/지연 0",
        "prompt_title": "정규식 (프롬프트 없음)",
        "prompt": ("_CRISIS_RE = re.compile(\n"
                   "  r\"이체|송금|보내|입금|계좌|인증번호|otp|\"\n"
                   "  r\"비밀번호|보안카드|앱|설치|링크|\"\n"
                   "  r\"구속|영장|상환|마감\", re.I)\n\n"
                   "is_crisis_turn(발화)  →  True/False"),
        "why": ("왜: 위기 판정에까지 LLM을 쓰면 매 턴 추가 콜·지연·비용이 붙는다. "
                "사기 대본의 위험 신호(이체·계좌·앱·영장)는 어휘가 정형적이라 정규식으로 "
                "충분히 잡힌다. 결정론이라 비용 0·지연 0이고, '왜 승급했는지'가 감사 가능."),
    },
    {
        "tag": "응대 (Responder) — 동기 임계경로",
        "accent": BLUE,
        "placement": "평시=haiku(저가) / 위기턴=sonnet(중급) · 매 턴 1콜",
        "prompt_title": "시스템: 73세 김순자 할머니 페르소나 + 응답 지시",
        "prompt": ("[페르소나] 너는 73세 김순자 할머니다. (성격·말투·가족관계·\n"
                   "  금융 미숙·청력 약함 등 일관된 설정 — persona.py)\n\n"
                   "[응답 지시] 위 통화에 이어 '할머니'로서 다음 한마디만\n"
                   "  통화하듯 한두 문장으로 짧게 말하라. 지문·따옴표·\n"
                   "  설명 없이 대사만 출력.\n\n"
                   "[작전 힌트(있으면)] 이번엔 특히 '<항목>'을 캐내라."),
        "why": ("왜: 사용자(사기범)가 실제로 기다리는 유일한 콜 → 임계경로에 둔다. "
                "평시 잡담은 haiku로 충분하고, 정보가 오가는 위기턴만 sonnet으로 1단 승급해 "
                "감정 텍스처를 살린다. Opus는 쓰지 않는다(과잉). 짧은 1~2문장 강제 = 출력 토큰·지연 절감."),
    },
    {
        "tag": "추출 (Extractor) — 비동기",
        "accent": SAGE,
        "placement": "haiku(저가) · 매 턴 · 응답 송출 후 백그라운드",
        "prompt_title": "시스템: 단서 추출 분석기 (JSON 강제)",
        "prompt": ("너는 보이스피싱 통화에서 단서를 추출하는 분석기다.\n"
                   "통화 전체에서 '사기범이 실제로 말한 사실'만 뽑아\n"
                   "JSON 하나만 출력(코드펜스 금지):\n"
                   "{\"agency\":\"<사칭기관>\",\"account\":\"<계좌번호>\",\n"
                   " \"amount\":\"<요구금액>\",\"deadline\":\"<송금시한>\",\n"
                   " \"app\":\"<악성앱/URL>\"}\n"
                   "없는 값은 빈 문자열. 추정·창작 금지."),
        "why": ("왜: 수사·차단에 쓸 핵심 정보(기관·계좌·금액·시한·앱) 5종을 구조화한다. "
                "임계경로 밖이라 응답 지연에 0 기여 → 저가 haiku로 충분. '추정·창작 금지'로 "
                "환각을 억제(빈칸 허용). 실측상 저가 모델로도 추출 F1 1.00 (고급모델과 동등)."),
    },
    {
        "tag": "압축 (Compactor) — 비동기",
        "accent": PURPLE,
        "placement": "haiku(저가) · 4턴마다(K_COMPACT=4)",
        "prompt_title": "시스템: 통화 메모리 압축기 (5줄 이내)",
        "prompt": ("너는 통화 메모리 압축기다. 아래 통화를 미끼봇이\n"
                   "다음 응답에 쓸 수 있게 '수집된 단서 + 현재 분위기/요구'를\n"
                   "5줄 이내 한국어 요약으로 압축하라.\n"
                   "새 정보 위주로, 군더더기 없이. 머리말 없이 요약만 출력."),
        "why": ("왜: 통화가 길어지면 전체 이력을 매 턴 넣는 비용이 폭주한다. 4턴마다 요약으로 "
                "대체하면 입력 토큰을 일정하게 유지(긴 통화 확장성의 핵심). 비동기라 지연 영향 없음. "
                "최근 2쌍(KEEP=2)은 원문 보존 → 직전 맥락 손실 방지."),
    },
    {
        "tag": "기획 (Planner / Opus 전략가) — 운영 OFF",
        "accent": RED,
        "placement": "미사용(USE_PLANNER=False) · 실험에서만 존재",
        "prompt_title": "시스템: 작전 오케스트레이터 (참고 — 운영 비활성)",
        "prompt": ("너는 보이스피싱 대응 미끼봇의 작전 오케스트레이터다.\n"
                   "아직 확보 못한 단서 중 다음 턴 1순위와, 73세 할머니가\n"
                   "의심받지 않게 끌어낼 한 문장 전술을 정한다.\n"
                   "JSON: {\"next_target\":\"<항목>\",\"tactic\":\"<전략>\"}\n\n"
                   "  ※ 운영에서는 호출하지 않음."),
        "why": ("왜 끄는가: 매 턴(T3) 또는 저빈도(T6, 3턴마다) Opus 기획을 실측 비교한 결과 "
                "비용은 3~11배 늘지만 추출 F1·위장유지 점수 이득이 없었다(T6: 비용+144%, 몰입 -2점). "
                "→ 가설 기각. 운영에서는 비활성, 설정 토글로만 재활성 가능."),
    },
]


def main():
    fig, ax = plt.subplots(figsize=(15.5, 20))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    # 제목
    txt(ax, 50, 99, "미끼봇 오케스트레이션 — 역할별 프롬프트 & 설계 의도",
        TEXT, 21, bold=True, ha="center")
    txt(ax, 50, 96.4,
        "각 역할이 실제로 쓰는 시스템 프롬프트 전문(roles.py) + 왜 그렇게 설계했는가",
        DIM, 11.5, ha="center")
    txt(ax, 50, 94.7,
        "추상 티어(haiku=저가 / sonnet=중급 / opus=최상위)는 프로바이더별 실모델에 매핑 — 프롬프트는 모델 무관",
        DIM2, 9.5, ha="center")

    top = 92.0
    card_h = 17.2
    gap = 0.7
    for i, c in enumerate(CARDS):
        y1 = top - i * (card_h + gap)
        y0 = y1 - card_h
        # 카드 외곽
        rbox(ax, 3, y0, 94, card_h, PANEL, edge=LINEC, lw=1.2, rad=0.5, z=1)
        # 왼쪽 액센트 바
        ax.add_patch(FancyBboxPatch((3.3, y0 + 0.4), 0.9, card_h - 0.8,
                     boxstyle="round,pad=0.01,rounding_size=0.2",
                     facecolor=c["accent"], edgecolor="none", zorder=3))
        yy = y1 - 1.3
        # 역할 태그 + 배치
        txt(ax, 6, yy, c["tag"], c["accent"], 14, bold=True)
        yy -= 2.0
        rbox(ax, 6, yy - 0.3, 56, 2.2, BG, edge=c["accent"], lw=0.9, rad=0.25, z=3)
        txt(ax, 7, yy + 1.35, "배치 · " + c["placement"], DIM, 9.5, bold=True, va="top")

        # 프롬프트 박스 (왼쪽)
        py = y1 - 1.6
        rbox(ax, 6, y0 + 1.2, 52, card_h - 4.6, CODE_BG, edge=LINEC, lw=0.8, rad=0.25, z=3)
        txt(ax, 7.3, y0 + card_h - 4.9, c["prompt_title"], TEXT, 9.5, bold=True, va="top")
        txt(ax, 7.3, y0 + card_h - 6.5, c["prompt"], DIM, 8.3, va="top")

        # 왜 박스 (오른쪽)
        rbox(ax, 60, y0 + 1.2, 35, card_h - 2.6, BG, edge=c["accent"], lw=1.0, rad=0.3, z=3)
        txt(ax, 61.5, y1 - 1.7, "설계 의도 (왜)", c["accent"], 11, bold=True, va="top")
        # why 텍스트 줄바꿈
        why = c["why"]
        # 간단한 wrap (글자수 기준)
        import textwrap
        wrapped = textwrap.fill(why, width=27)
        txt(ax, 61.5, y1 - 3.6, wrapped, TEXT, 9.2, va="top")

    fig.savefig(RESULTS / "fig_orch_prompts.png", dpi=185,
                bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("생성: results/fig_orch_prompts.png")


if __name__ == "__main__":
    main()
