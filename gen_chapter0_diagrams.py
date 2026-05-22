# -*- coding: utf-8 -*-
"""Chapter 0 시각 자료 — 모듈 의존 맵, 14일 간트차트."""
from pathlib import Path
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

FONT_PATH = r"C:\Windows\Fonts\malgun.ttf"
FONT_BOLD = r"C:\Windows\Fonts\malgunbd.ttf"
fm.fontManager.addfont(FONT_PATH)
fm.fontManager.addfont(FONT_BOLD)
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(r"C:\Users\SSAFY\Desktop\AI해커톤\images")
OUT.mkdir(exist_ok=True)

# Claude palette
CREAM = "#faf9f5"
TAN = "#e8e6dc"
WARM = "#f1efe6"
INK = "#141413"
SLATE = "#5a5853"
MID = "#b0aea5"
ORANGE = "#d97757"
SAGE = "#788c5d"
BLUE = "#6a9bcc"
LINE = "#e8e6dc"


def save(fig, name, dpi=200):
    fig.patch.set_facecolor(CREAM)
    path = OUT / name
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=CREAM)
    plt.close(fig)
    print(f"[OK] {path.name}")


# ============================================================
# 1) 모듈 의존 맵 — 9개 기능 + 6인 담당자 매핑
# ============================================================
def module_map():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_facecolor(CREAM)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9.5)
    ax.axis("off")
    ax.set_title("기능 모듈 맵 — 9개 기능 × 6인 담당",
                 fontsize=19, fontweight="bold", color=INK, pad=10)

    # Layer headers
    layers = [
        ("입력 단", 8.0, ORANGE),
        ("AI 코어", 5.7, ORANGE),
        ("저장 · 조회", 3.4, ORANGE),
        ("출력 · 알림", 1.1, ORANGE),
    ]
    for label, y, c in layers:
        ax.text(-0.4, y + 0.4, label, fontsize=10, fontweight="bold",
                color=c, ha="left", va="center", rotation=0)

    # Modules: (x, y, w, h, name, owner, kind)
    # kind: real | mock | shared
    modules = [
        # 입력 단
        (0.5, 7.5, 3.0, 1.2, "① Twilio Webhook", "백엔드", "real"),
        (3.8, 7.5, 3.0, 1.2, "② STT (Whisper)", "ML-2", "real"),
        (7.1, 7.5, 3.0, 1.2, "③ 음성 변환 audio.py", "ML-2 / 백엔드", "real"),
        (10.4, 7.5, 3.0, 1.2, "④ VAD vad.py", "ML-2", "real"),
        # AI 코어
        (0.5, 5.2, 3.0, 1.2, "⑤ 미끼봇 LLM", "ML-1", "real"),
        (3.8, 5.2, 3.0, 1.2, "⑥ 정보 추출", "ML-2", "real"),
        (7.1, 5.2, 3.0, 1.2, "⑦ TTS (Typecast)", "ML-1", "real"),
        (10.4, 5.2, 3.0, 1.2, "⑧ History 압축", "ML-1", "real"),
        # 저장 단
        (0.5, 2.9, 6.3, 1.2, "⑨ DB models.py (6 tables)", "백엔드", "real"),
        (7.1, 2.9, 6.3, 1.2, "⑩ Redis 캐시 + 화이트리스트", "백엔드", "real"),
        # 출력 단
        (0.5, 0.6, 4.2, 1.2, "⑪ Streamlit 대시보드", "백엔드 + UX", "real"),
        (5.0, 0.6, 4.2, 1.2, "⑫ FCM 푸시 알림", "백엔드", "shared"),
        (9.5, 0.6, 3.9, 1.2, "⑬ FDS 동결 (모킹)", "UX", "mock"),
    ]
    color_map = {"real": ORANGE, "mock": MID, "shared": SAGE}
    for x, y, w, h, name, owner, kind in modules:
        c = color_map[kind]
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                             facecolor=c, edgecolor="none", alpha=0.95)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h - 0.35, name,
                fontsize=11.5, fontweight="bold", color="white", ha="center")
        ax.text(x + w / 2, y + 0.25, owner,
                fontsize=9.5, color="white", ha="center", alpha=0.92)

    # Layer arrows (downward flow)
    for y_from, y_to in [(7.45, 6.45), (5.15, 4.15), (2.85, 1.85)]:
        arr = FancyArrowPatch((7, y_from), (7, y_to),
                              arrowstyle="-|>", mutation_scale=22,
                              color=SLATE, linewidth=2)
        ax.add_patch(arr)

    # Legend
    ax.text(0.5, -0.2, "■ 진짜 구현 (AI 가치)",
            fontsize=10, color=ORANGE, fontweight="bold")
    ax.text(4.0, -0.2, "■ 인프라 공유",
            fontsize=10, color=SAGE, fontweight="bold")
    ax.text(7.0, -0.2, "■ 모킹 (시연용)",
            fontsize=10, color=SLATE, fontweight="bold")
    ax.text(10.0, -0.2, "→ 데이터 흐름",
            fontsize=10, color=SLATE)

    save(fig, "00_module_map.png")


# ============================================================
# 2) 14일 간트차트 — 5/13 ~ 5/27, 6인 담당
# ============================================================
def gantt_14days():
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_facecolor(CREAM)
    ax.set_xlim(-1, 15.5)
    ax.set_ylim(-0.5, 7)
    ax.axis("off")
    ax.set_title("14일 일정 — 6인 × 5/13~5/27",
                 fontsize=19, fontweight="bold", color=INK, pad=10)

    # Day labels (top axis)
    days = ["5/13", "5/14", "5/15", "5/16", "5/17", "5/18", "5/19",
            "5/20", "5/21", "5/22", "5/23", "5/24", "5/25", "5/26", "5/27"]
    week_labels = ["수", "목", "금", "토", "일", "월", "화", "수",
                   "목", "금", "토", "일", "월", "화", "수"]
    for i, (d, w) in enumerate(zip(days, week_labels)):
        is_weekend = w in ["토", "일"]
        col = ORANGE if w == "월" else SLATE
        ax.text(i + 0.5, 6.4, d, fontsize=9, color=col,
                fontweight="bold", ha="center")
        ax.text(i + 0.5, 6.05, w, fontsize=8,
                color=ORANGE if is_weekend else MID, ha="center")

    # Role rows
    roles = [
        ("기획·발표", SAGE),
        ("ML-1", ORANGE),
        ("ML-2", ORANGE),
        ("백엔드", BLUE),
        ("UX", "#c99a4e"),
        ("법리·보안", "#a67b6d"),
    ]
    row_h = 0.85
    for idx, (role, color) in enumerate(roles):
        y = 5.5 - idx * row_h
        # Role label
        ax.text(-0.8, y + row_h / 2 - 0.25, role,
                fontsize=11, fontweight="bold", color=INK, ha="left", va="center")
        # Alternating row bg
        if idx % 2 == 0:
            ax.add_patch(Rectangle((0, y), 15, row_h - 0.1,
                                   facecolor=WARM, edgecolor="none", alpha=0.5))

    # Tasks: (role_idx, start_day, duration, label, color)
    tasks = [
        # 기획·발표
        (0, 0, 2, "데이터 셋업", SAGE),
        (0, 2, 3, "시연 스토리보드", SAGE),
        (0, 5, 3, "기획안 v2", SAGE),
        (0, 8, 4, "발표 슬라이드", SAGE),
        (0, 13, 2, "리허설 3회", SAGE),
        # ML-1 (미끼봇)
        (1, 0, 2, "TTS 선정", ORANGE),
        (1, 2, 3, "미끼봇 프롬프트", ORANGE),
        (1, 5, 3, "응답 자연성 튜닝", ORANGE),
        (1, 8, 4, "음성 통합", ORANGE),
        (1, 12, 1, "디버그 ⚠", "#c4623f"),
        (1, 13, 2, "리허설", ORANGE),
        # ML-2 (정보 추출)
        (2, 0, 2, "데이터 30+100건", ORANGE),
        (2, 2, 3, "JSON 스키마", ORANGE),
        (2, 5, 3, "정보 추출 엔진", ORANGE),
        (2, 8, 4, "Whisper 통합", ORANGE),
        (2, 12, 1, "디버그 ⚠", "#c4623f"),
        (2, 13, 2, "리허설", ORANGE),
        # 백엔드
        (3, 0, 2, "레포·DB", BLUE),
        (3, 2, 3, "FastAPI 스켈레톤", BLUE),
        (3, 5, 3, "Streamlit", BLUE),
        (3, 8, 4, "Twilio 통합", BLUE),
        (3, 12, 1, "디버그 ⚠", "#a04a2a"),
        (3, 13, 2, "리허설", BLUE),
        # UX
        (4, 0, 2, "와이어프레임", "#c99a4e"),
        (4, 2, 3, "사기범 음원 편집", "#c99a4e"),
        (4, 5, 3, "Figma 목업", "#c99a4e"),
        (4, 8, 4, "영상 편집", "#c99a4e"),
        (4, 12, 1, "디버그 ⚠", "#a06e2a"),
        (4, 13, 2, "최종 영상", "#c99a4e"),
        # 법리·보안
        (5, 0, 2, "법리 검토표", "#a67b6d"),
        (5, 2, 3, "저작권 검토", "#a67b6d"),
        (5, 5, 3, "약관 초안", "#a67b6d"),
        (5, 8, 4, "보안 자가검증", "#a67b6d"),
        (5, 12, 1, "디버그 ⚠", "#7e5448"),
        (5, 13, 2, "리허설 Q&A", "#a67b6d"),
    ]
    for role_idx, start, dur, label, color in tasks:
        y = 5.5 - role_idx * row_h + 0.12
        h = row_h - 0.34
        ax.add_patch(Rectangle((start, y), dur, h,
                               facecolor=color, edgecolor=CREAM,
                               linewidth=1.5))
        if dur >= 2:
            ax.text(start + dur / 2, y + h / 2, label,
                    fontsize=8.5, color="white", fontweight="bold",
                    ha="center", va="center")

    # Milestone markers (top)
    milestones = [
        (2, "데이터·음성 셋업 완료"),
        (5, "주말 집중 시작"),
        (8, "기획안 v2 완료"),
        (12, "디버깅 전용일"),
        (15, "본선 진출"),
    ]
    for day, label in milestones:
        ax.axvline(day, color=ORANGE, linestyle="--", linewidth=0.8, alpha=0.5)
        ax.text(day, -0.3, label, fontsize=8, color=ORANGE,
                ha="center", style="italic")

    # Day grid lines
    for d in range(16):
        ax.axvline(d, color=LINE, linewidth=0.3, alpha=0.7, zorder=0)

    save(fig, "00_gantt_14days.png")


if __name__ == "__main__":
    module_map()
    gantt_14days()
    print("\n=== Chapter 0 다이어그램 2종 생성 완료 ===")
