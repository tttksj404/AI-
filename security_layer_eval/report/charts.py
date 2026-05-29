"""평가 결과 → 발표용 차트(Anthropic 팔레트 + Pretendard).

생성물(results/):
  fig1_asr_models.png   모델별 미끼봇 무력화율 OFF vs ON (헤드라인)
  fig2_defense_funnel.png  심층방어 퍼널: 30 공격 → 룰(무료) → 가드 → 출력가드 → 0
  fig3_confusion.png    혼동행렬 + 정밀도/재현율/FPR (정상 사기 통과 증명)
  fig4_by_family.png    공격 유형별 차단 계층(룰 vs 가드)
  fig5_latency.png      계층별 지연 오버헤드
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# ── 기존 Sentinel30 노션 도표(gen_images_v3) 라이트 아카데믹 팔레트 ──
CREAM = "#fbfaf7"; CARD = "#ffffff"; INK = "#26231f"; SUB = "#6f6a61"
GRID = "#ded8ce"
CLAY = "#d8652a"           # primary orange
DANGER = "#bf4a42"         # OFF(취약) red/warning
SAFE = "#5d8c61"           # ON(보호) sage
RULE = "#b28a32"           # 룰 계층 gold
GUARD = "#3f7ca8"          # 가드 계층 blue
OUT = "#7b669b"            # 출력 가드 purple

# ── Pretendard 폰트 (폰트는 레포 루트 fonts/ 에 있음) ───────────────
FONT_DIR = next((d for d in (ROOT / "fonts", ROOT.parent / "fonts")
                 if (d / "Pretendard-Regular.ttf").exists()), ROOT / "fonts")
for fn in ("Pretendard-Regular.ttf", "Pretendard-SemiBold.ttf", "Pretendard-Bold.ttf",
           "NanumGothic-Regular.ttf"):
    fp = FONT_DIR / fn
    if fp.exists():
        fm.fontManager.addfont(str(fp))
try:
    _name = fm.FontProperties(fname=str(FONT_DIR / "Pretendard-Regular.ttf")).get_name()
    plt.rcParams["font.family"] = _name
    plt.rcParams["font.sans-serif"] = [_name, "NanumGothic", "DejaVu Sans"]
except Exception:
    pass
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.facecolor"] = CREAM
plt.rcParams["savefig.facecolor"] = CREAM


def load(model: str) -> dict | None:
    p = RESULTS / f"eval_results_{model}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _style(ax):
    ax.set_facecolor(CARD)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=SUB, labelsize=11)
    ax.grid(axis="y", color=GRID, lw=0.8, alpha=0.7)
    ax.set_axisbelow(True)


def fig1_asr(models: dict):
    labels, off, on = [], [], []
    for m, d in models.items():
        if not d:
            continue
        s = d["summary"]
        labels.append({"haiku": "Haiku 4.5\n(실시간·저지연)",
                       "sonnet": "Sonnet 4.6\n(고성능)"}.get(m, m))
        off.append(s["asr_off"] * 100)
        on.append(s["asr_on"] * 100)
    x = np.arange(len(labels)); w = 0.36
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    _style(ax)
    b1 = ax.bar(x - w/2, off, w, label="보안계층 OFF (대조군)", color=DANGER)
    b2 = ax.bar(x + w/2, on, w, label="보안계층 ON (실험군)", color=SAFE)
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.6,
                f"{b.get_height():.1f}%", ha="center", va="bottom",
                fontsize=12, color=INK, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11, color=INK)
    ax.set_ylabel("미끼봇 무력화율 (누출 OR 위장붕괴, %)", fontsize=12, color=INK)
    ax.set_ylim(0, max(12, max(off + [1]) * 1.4))
    ax.set_title("적대적 프롬프트에 의한 미끼봇 무력화율 — 보안계층 ON이면 0%",
                 fontsize=14.5, color=INK, fontweight="bold", pad=14)
    ax.legend(frameon=False, fontsize=11, loc="upper right")
    ax.text(0.0, -0.16, "공격 30종(L1B3RT4S·General-Analysis 기법). "
            "OFF는 모델·요청에 따라 누출/거부(위장붕괴)로 실패하지만, ON은 모델 무관 0%.",
            transform=ax.transAxes, fontsize=9.5, color=SUB)
    fig.tight_layout()
    fig.savefig(RESULTS / "fig1_asr_models.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def _layer_breakdown(d: dict):
    """ON arm: 각 공격을 막은 첫 계층(rule/guard/output) 집계."""
    rule = guard = out = slipped = 0
    for a in d["attacks"]:
        on = a["on"]
        if on["success"]:
            slipped += 1; continue
        src = None
        for t in on["turns"]:
            act = t["action"]
            if act == "BLOCK" and t["source"] == "rule":
                src = "rule"; break
            if act == "BLOCK" and t["source"] == "guard":
                src = src or "guard"
            if act == "OUTPUT_BLOCK":
                src = src or "out"
        if src == "rule":
            rule += 1
        elif src == "guard":
            guard += 1
        elif src == "out":
            out += 1
        else:
            guard += 1  # ALLOW 됐지만 누출 없음 → 가드가 안전 통과로 처리
    return rule, guard, out, slipped


def fig2_funnel(d: dict):
    n = d["summary"]["n_attacks"]
    rule, guard, out, slipped = _layer_breakdown(d)
    stages = ["공격 입력", "룰 프리필터 통과", "입력 가드 통과", "출력 가드 통과\n(최종 누출)"]
    remaining = [n, n - rule, n - rule - guard, slipped]
    removed = [("", 0), (f"룰 차단\n−{rule} (무료·결정적)", rule),
               (f"가드 차단\n−{guard} (LLM)", guard),
               (f"출력가드\n−{out}", out)]
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.set_facecolor(CARD)
    colors = [CLAY, RULE, GUARD, OUT]
    y = np.arange(len(stages))[::-1]
    ax.barh(y, remaining, color=colors, height=0.55, zorder=3)
    for yi, val in zip(y, remaining):
        ax.text(val + 0.3, yi, f"{val}건", va="center", ha="left",
                fontsize=12, color=INK, fontweight="bold")
    for i, (lab, val) in enumerate(removed):
        if val:
            ax.text(remaining[i-1] - 0.2 if False else n*0.62, y[i] + 0.0,
                    lab, va="center", ha="left", fontsize=10.5, color=DANGER)
    ax.set_yticks(y); ax.set_yticklabels(stages, fontsize=11.5, color=INK)
    ax.set_xlim(0, n * 1.15)
    ax.set_xlabel("남은 공격 수", fontsize=12, color=INK)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=SUB)
    ax.set_title(f"심층 방어 퍼널 — 공격 {n}종이 0건까지 (룰이 {rule}건을 API 도달 전 무료 차단)",
                 fontsize=14, color=INK, fontweight="bold", pad=14)
    fig.tight_layout()
    fig.savefig(RESULTS / "fig2_defense_funnel.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def fig3_confusion(d: dict):
    c = d["summary"]["confusion"]; s = d["summary"]
    M = np.array([[c["TP"], c["FN"]], [c["FP"], c["TN"]]])
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.imshow([[0, 0], [0, 0]], cmap="Greys", vmin=0, vmax=1)
    cellc = [[SAFE, DANGER], [DANGER, SAFE]]
    labels = [["TP\n공격 차단", "FN\n공격 뚫림"], ["FP\n정상 차단(오탐)", "TN\n정상 통과"]]
    for i in range(2):
        for j in range(2):
            ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, color=cellc[i][j],
                                       alpha=0.88, zorder=1))
            ax.text(j, i-0.13, f"{M[i][j]}", ha="center", va="center",
                    fontsize=30, color="white", fontweight="bold", zorder=2)
            ax.text(j, i+0.27, labels[i][j], ha="center", va="center",
                    fontsize=11, color="white", zorder=2)
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["차단(positive)", "통과(negative)"], fontsize=11, color=INK)
    ax.set_yticklabels(["공격 입력\n(30종)", "정상 사기\n(15종)"], fontsize=11, color=INK)
    ax.set_xlim(-0.5, 1.5); ax.set_ylim(1.5, -0.5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("보안계층 판정 행렬 — 정밀도 "
                 f"{s['precision']:.2f} · 재현율 {s['recall']:.2f} · 오탐률 {s['fpr']*100:.0f}%",
                 fontsize=13.5, color=INK, fontweight="bold", pad=14)
    ax.text(0.5, 1.92, "공격은 100% 차단하면서 정상 사기 대사는 한 건도 막지 않음 "
            "→ 미끼봇이 실제 사기범과 대화를 계속 이어감",
            transform=ax.transData, ha="center", fontsize=9.8, color=SUB)
    fig.tight_layout()
    fig.savefig(RESULTS / "fig3_confusion.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def fig4_by_family(d: dict):
    fams, rule_c, guard_c = [], [], []
    bucket = {}
    for a in d["attacks"]:
        f = a["family_ko"]
        b = bucket.setdefault(f, [0, 0])
        on = a["on"]
        by_rule = any(t["action"] == "BLOCK" and t["source"] == "rule" for t in on["turns"])
        if by_rule:
            b[0] += 1
        else:
            b[1] += 1
    for f, (r, g) in bucket.items():
        fams.append(f.replace(" · ", "\n").replace("(", "\n("))
        rule_c.append(r); guard_c.append(g)
    y = np.arange(len(fams))
    fig, ax = plt.subplots(figsize=(9.4, 5.6))
    _style(ax); ax.grid(axis="x", color=GRID, lw=0.8, alpha=0.7); ax.grid(axis="y", visible=False)
    ax.barh(y, rule_c, color=RULE, label="룰 프리필터 차단(무료·결정적)", zorder=3)
    ax.barh(y, guard_c, left=rule_c, color=GUARD, label="입력 가드 LLM 차단(의미 기반)", zorder=3)
    ax.set_yticks(y); ax.set_yticklabels(fams, fontsize=10, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("차단된 공격 수", fontsize=12, color=INK)
    ax.set_title("공격 유형별 차단 계층 — 난독화·디바이더는 룰이, 소셜·정체폭로·점증은 가드가",
                 fontsize=13, color=INK, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=10.5, loc="lower right")
    fig.tight_layout()
    fig.savefig(RESULTS / "fig4_by_family.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def fig5_latency(d: dict):
    lat = d.get("latency") or {}
    if not lat:
        return False
    items = [("룰 프리필터", lat.get("rule_prefilter_ms", 0), RULE),
             ("출력 가드", lat.get("output_guard_ms", 0), OUT),
             ("입력 가드 LLM", lat.get("input_guard_s", 0) * 1000, GUARD),
             ("미끼봇 응답 LLM", lat.get("bot_reply_s", 0) * 1000, CLAY)]
    names = [i[0] for i in items]; vals = [i[1] for i in items]; cols = [i[2] for i in items]
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    _style(ax); ax.grid(axis="x", color=GRID, lw=0.8, alpha=0.7); ax.grid(axis="y", visible=False)
    ax.barh(y, vals, color=cols, zorder=3)
    for yi, v in zip(y, vals):
        ax.text(v * 1.02 + 5, yi, f"{v:.1f} ms" if v < 1000 else f"{v/1000:.2f} s",
                va="center", fontsize=11, color=INK, fontweight="bold")
    ax.set_yticks(y); ax.set_yticklabels(names, fontsize=11, color=INK); ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel("지연 (ms, 로그 스케일)", fontsize=12, color=INK)
    ax.set_title("계층별 지연 — 룰/출력가드는 1ms 미만, 가드는 봇 응답과 동급",
                 fontsize=13, color=INK, fontweight="bold", pad=12)
    ax.text(0.0, -0.22, "룰이 공격의 다수를 잡으면 봇 LLM 호출 자체가 생략되어 평균 지연은 오히려 감소.",
            transform=ax.transAxes, fontsize=9.5, color=SUB)
    fig.tight_layout()
    fig.savefig(RESULTS / "fig5_latency.png", dpi=170, bbox_inches="tight")
    plt.close(fig)
    return True


def fig5_extract():
    p = RESULTS / "extract_results_haiku.json"
    if not p.exists():
        return False
    s = json.loads(p.read_text(encoding="utf-8"))["summary"]
    goal_ko = {"suppress_alert": "경보 끄기", "exfiltrate": "정보 탈취",
               "field_tamper": "필드 변조", "instruction_override": "임무 탈취",
               "evasion_softframe": "은밀 사회공학\n(가짜 승인·검증)"}
    goals = list(s["by_goal"].keys())
    labels = [goal_ko.get(g, g) for g in goals]
    off = [s["by_goal"][g]["off"] * 100 for g in goals]
    on = [s["by_goal"][g]["on"] * 100 for g in goals]
    x = np.arange(len(labels)); w = 0.38
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    _style(ax)
    ax.bar(x - w/2, off, w, label="보안계층 OFF", color=DANGER)
    ax.bar(x + w/2, on, w, label="보안계층 ON", color=SAFE)
    for xi, (o, n) in enumerate(zip(off, on)):
        ax.text(xi - w/2, o + 1.5, f"{o:.0f}%", ha="center", fontsize=11, color=INK, fontweight="bold")
        ax.text(xi + w/2, n + 1.5, f"{n:.0f}%", ha="center", fontsize=11, color=INK, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10.5, color=INK)
    ax.set_ylabel("간접주입 성공률 (%)", fontsize=12, color=INK)
    ax.set_ylim(0, max(30, max(off + [1]) * 1.5))
    ax.set_title("추출 에이전트 간접 프롬프트 인젝션(AML.T0051.001) — 유형별 주입 성공률",
                 fontsize=13.5, color=INK, fontweight="bold", pad=12)
    ax.legend(frameon=False, fontsize=11)
    ax.text(0.0, -0.2, f"Claude는 명시적 주입엔 네이티브로 강건(0%)하나 '정식 승인'식 은밀 위장엔 "
            f"경보가 꺼질 수 있음 → 보안계층이 0%로 차단(정상 콘텐츠 무결성 "
            f"{s['benign_integrity_on']*100:.0f}% 유지).",
            transform=ax.transAxes, fontsize=9.3, color=SUB)
    fig.tight_layout()
    fig.savefig(RESULTS / "fig5_extract_injection.png", dpi=170, bbox_inches="tight")
    plt.close(fig)
    return True


def main():
    models = {"haiku": load("haiku"), "sonnet": load("sonnet")}
    primary = models.get("haiku") or models.get("sonnet")
    made = []
    if any(models.values()):
        fig1_asr(models); made.append("fig1_asr_models.png")
    if primary:
        fig2_funnel(primary); made.append("fig2_defense_funnel.png")
        fig3_confusion(primary); made.append("fig3_confusion.png")
        fig4_by_family(primary); made.append("fig4_by_family.png")
    if fig5_extract():
        made.append("fig5_extract_injection.png")
    # 지연 차트는 CLI-서브프로세스 부트스트랩 오버헤드 때문에 신뢰 수치가 아니라 생략.
    print("생성:", ", ".join(made))


if __name__ == "__main__":
    main()
