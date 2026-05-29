"""운영 역할 배치 (Production role assignment).

오케스트레이션 효율 실험(T1~T6 × Claude/GPT/Gemini 3사 교차검증)에서 증명된 결론을
그대로 '운영 설정'으로 못박은 모듈. 실험이 보여준 구조적 사실(프로바이더 무관):

  · 동기 멀티콜(T3: 기획→응대 직렬)  → 임계경로 지연 재앙(2~4배)
  · 고급모델·상시 기획(T2/T4/T6의 Opus) → 비용 3~11배, 추출 F1 이득 없음
  · 단순구조(T1/T5)  → 추출 F1 동등하면서 비용·지연 최저권
      - T1: 최저비용이나 역할 미분리 → 압축 없음·확장 불가(단발 baseline)
      - T5: 최저지연 + 역할분리(추출·압축 비동기) → 확장 가능 ⇒ 운영 채택

따라서 운영 배치 = T5(haiku-adaptive)를 명시화한 것:
  기본은 저가 티어, 위기턴만 중급 티어로 '1단 승급', 추출·압축은 비동기 저가,
  Opus 기획자 없음. 모델은 추상 티어(cheap/mid)로만 지정 → 프로바이더 교체에 무관.

이 모듈이 역할-티어-배치의 단일 진실원천(single source of truth)이다.
실측 비교는 orch.topologies(T1~T6)에 그대로 남겨 둔다(실험 재현용).
"""
from __future__ import annotations
import statistics
from dataclasses import dataclass

from . import roles, metrics
from .scripts import FIELDS

# ── 운영 파라미터 (실험에서 채택된 값) ─────────────────────────────
BASE_TIER    = "haiku"    # 평시 응대 — 저가 티어(cheap). 통화의 대부분.
CRISIS_TIER  = "sonnet"   # 위기턴 응대 — 중급 티어(mid)로 1단 승급. Opus 아님.
EXTRACT_TIER = "haiku"    # 단서 추출 — 비동기·저가. 임계경로 밖.
COMPACT_TIER = "haiku"    # 메모리 압축 — 비동기·저가. 입력토큰을 일정하게 유지.
USE_PLANNER  = False      # Opus 전략가 — 실험상 비용낭비(품질 이득 0) → 운영 OFF.
K_COMPACT    = 4          # 압축 주기(턴). 4턴마다 1회.
KEEP         = 2          # 압축 후에도 항상 원문 보존하는 최근 대화 쌍 수.


@dataclass(frozen=True)
class RoleSpec:
    role: str        # 역할
    placement: str   # "동기(임계경로)" | "비동기" | "결정론(LLM 아님)"
    tier: str        # 배정 티어(또는 라우터 분기 설명)
    cadence: str     # 호출 빈도
    why: str         # 채택 근거(실험 결론)


# ── 역할 배치표 (= 운영 설정의 사람이 읽는 형태) ───────────────────
ROLE_PLAN: list[RoleSpec] = [
    RoleSpec(
        role="라우터(Router)",
        placement="결정론(LLM 아님)",
        tier="—  (정규식, 비용 0·지연 0)",
        cadence="매 턴(응대 직전)",
        why="위기 키워드(이체·계좌·인증번호·앱·영장 등) 정규식 판정으로 응대 티어를 "
            "고른다. LLM 호출이 아니라 비용·지연이 0 → 승급 판단을 공짜로 한다."),
    RoleSpec(
        role="응대(Responder)",
        placement="동기(임계경로)",
        tier=f"평시={BASE_TIER}(저가) / 위기턴={CRISIS_TIER}(중급)",
        cadence="매 턴 1콜",
        why="사용자가 기다리는 유일한 콜이라 임계경로에 둔다. 평시는 저가로 충분하고, "
            "정보가 오가는 위기턴만 중급으로 승급. T5가 최저지연을 낸 핵심."),
    RoleSpec(
        role="추출(Extractor)",
        placement="비동기",
        tier=f"{EXTRACT_TIER}(저가)",
        cadence="매 턴 1콜(응답 송출 후 백그라운드)",
        why="사칭기관·계좌·금액·시한·악성앱 5종을 통화 전체에서 뽑는다. 임계경로 밖이라 "
            "지연에 무관. 저가 티어로도 추출 F1이 고급모델과 동등(실험 확인)."),
    RoleSpec(
        role="압축(Compactor)",
        placement="비동기",
        tier=f"{COMPACT_TIER}(저가)",
        cadence=f"{K_COMPACT}턴마다 1회",
        why="누적 이력을 요약해 입력토큰을 일정하게 유지(긴 통화 비용 폭주 방지). "
            "비동기라 지연 영향 없음. 장기 통화 확장성의 핵심."),
    RoleSpec(
        role="기획(Planner/Opus 전략가)",
        placement="미사용(OFF)",
        tier="—",
        cadence="0",
        why="T4/T6에서 상시·저빈도 Opus 기획을 넣어봤으나 비용만 늘고 추출 F1·위장유지 "
            "이득이 없었다(T6=권장 아님으로 정정). 운영에서는 끈다."),
]


# ── 라우터: 응대 티어 선택(결정론) ─────────────────────────────────
def responder_tier(utt: str) -> str:
    """이번 사기범 발화가 위기턴이면 중급, 평시면 저가 티어를 반환."""
    return CRISIS_TIER if roles.is_crisis_turn(utt) else BASE_TIER


# ── 운영 러너 (ROLE_PLAN 설정에 그대로 따른다) ─────────────────────
def run_production(call: dict, turns: int | None = None) -> dict:
    """T5-adaptive 운영 배치로 한 통화를 처리. 결과는 run_topology와 동일 스키마."""
    scammer_turns = call["turns"][:turns] if turns else call["turns"]

    history: list[tuple[str, str]] = []
    summary = ""
    all_metas: list[dict] = []   # 동기+비동기 전체 콜
    per_turn: list[dict] = []
    intel: dict = {}             # 누적 추출 스키마

    for i, utt in enumerate(scammer_turns):
        crisis = roles.is_crisis_turn(utt)
        ctx = roles.compact_context(summary, history, utt, keep=KEEP)

        # 동기 임계경로: 라우터 → 응대(평시 저가 / 위기 중급)
        tier = CRISIS_TIER if crisis else BASE_TIER
        reply, mr = roles.responder(ctx, tier)
        mr = dict(mr); mr["role"] = f"responder({tier})"
        all_metas.append(mr)
        critical_ms = mr.get("api_ms", 0)
        history.append((utt, reply))

        # 비동기: 추출(매 턴) + 압축(K턴마다)
        sx, mx = roles.extract_intel(history, None, EXTRACT_TIER)
        mx = dict(mx); mx["role"] = "extract"; all_metas.append(mx)
        if sx:
            for f in FIELDS:
                v = str(sx.get(f, "") or "").strip()
                if v:
                    intel[f] = v

        if USE_PLANNER:  # 운영 기본 OFF — 설정으로만 켤 수 있게 남겨 둠
            plan_ctx = "지금까지의 통화:\n" + roles.transcript_text(history)
            _, mp = roles.planner(plan_ctx, "opus")
            mp = dict(mp); mp["role"] = "planner(opus,off-by-default)"
            all_metas.append(mp)

        if (i + 1) % K_COMPACT == 0:
            summary, mc = roles.compactor(history, None, COMPACT_TIER)
            mc = dict(mc); mc["role"] = "compact"; all_metas.append(mc)

        per_turn.append({"i": i, "crisis": crisis, "tier": tier,
                         "critical_ms": critical_ms, "reply": reply})

    cms = [t["critical_ms"] for t in per_turn]
    prf = metrics.extraction_prf(intel, call["ground_truth"])
    return {
        "profile": "PRODUCTION(T5-adaptive)",
        "call": call.get("title", ""),
        "n_turns": len(scammer_turns),
        "tokens": metrics.sum_tokens(all_metas),
        "critical_ms": {
            "median": statistics.median(cms) if cms else 0,
            "mean": statistics.mean(cms) if cms else 0,
            "max": max(cms) if cms else 0,
            "per_turn": cms,
        },
        "n_calls": len(all_metas),
        "final_schema": intel,
        "extraction": prf,
        "per_turn": per_turn,
        "history": history,
    }


# ── 역할 배치표 출력 ───────────────────────────────────────────────
def print_plan() -> None:
    print("=" * 78)
    print(" 미끼봇 운영 역할 배치  (T5-adaptive — 실험 채택안)")
    print("=" * 78)
    for s in ROLE_PLAN:
        print(f"\n[{s.role}]")
        print(f"  배치 : {s.placement}")
        print(f"  티어 : {s.tier}")
        print(f"  빈도 : {s.cadence}")
        print(f"  근거 : {s.why}")
    print("\n" + "-" * 78)
    print(" 한 줄 요약 : 평시 저가 1콜(동기) + 위기턴만 중급 승급, "
          "추출·압축은 저가 비동기, Opus 없음.")
    print("-" * 78)


if __name__ == "__main__":  # python -m orch.production
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print_plan()
