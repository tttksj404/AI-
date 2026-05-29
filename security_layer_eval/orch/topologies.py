"""토폴로지 5종 + 턴 러너.

토폴로지(역할-모델-동기/비동기 배치):
  T1 monolith_sonnet   : Sonnet 1콜=응답+추출, 전체이력. 압축X. (순진한 baseline)
  T2 monolith_opus     : 위와 동일하되 Opus. (품질 천장 / 비용·지연 최악)
  T3 tiered_sequential : [동기] Opus기획 → Sonnet응대  |  [비동기] Haiku추출·압축
  T4 tiered_async      : [동기] Sonnet응대만(직전 턴 Opus기획 소비) |
                         [비동기] Opus기획(다음턴용)·Haiku추출·Haiku압축
  T5 haiku_adaptive    : [동기] 위기턴=Sonnet / 평시=Haiku (결정론 라우터) |
                         [비동기] Haiku추출·압축. (Opus 기획 없음 — 최저비용)

지연 메트릭 = '동기 임계경로(critical path)'에 든 콜의 duration_api_ms 합.
토큰/비용 = 그 턴의 모든 콜(동기+비동기) 합. → 비동기 배치가 지연만 줄이는 효과를 분리 측정.
"""
from __future__ import annotations
import statistics

from . import roles, metrics
from .scripts import FIELDS

K_COMPACT = 4   # 압축 주기(턴)
KEEP = 2        # 압축 토폴로지에서 항상 보존하는 최근 대화 쌍 수
K_PLAN = 3      # T6: Opus 전략가 저빈도 주기(턴) — 6턴 통화에서 2콜(매 턴 아님)

TOPOLOGIES = {
    "T1": {"name": "monolith-Sonnet", "kind": "monolith", "model": "sonnet",
           "compact": False, "desc": "단일 Sonnet 1콜(응답+추출), 전체이력"},
    "T2": {"name": "monolith-Opus", "kind": "monolith", "model": "opus",
           "compact": False, "desc": "단일 Opus 1콜(품질 천장)"},
    "T3": {"name": "tiered-sequential", "kind": "tiered", "compact": True,
           "sync": "Opus기획→Sonnet응대", "desc": "기획이 임계경로에 동기로 포함"},
    "T4": {"name": "tiered-async", "kind": "async", "compact": True,
           "sync": "Sonnet응대", "desc": "응대만 동기 / 기획·추출·압축 비동기(1턴지연)"},
    "T5": {"name": "haiku-adaptive", "kind": "adaptive", "compact": True,
           "sync": "Haiku|Sonnet(라우터)", "desc": "평시 Haiku, 위기턴만 Sonnet, 기획 없음"},
    "T6": {"name": "haiku-adaptive+opus전략가", "kind": "adaptive_strategist",
           "compact": True, "sync": "Haiku|Sonnet(라우터)",
           "desc": "T5 + Opus 전략가 저빈도(K_PLAN턴마다, 비동기) — 권장 운영안"},
}


def _tag(meta: dict, role: str) -> dict:
    meta = dict(meta)
    meta["role"] = role
    return meta


def _merge_schema(acc: dict, new: dict) -> dict:
    if not isinstance(new, dict):
        return acc
    for f in FIELDS:
        v = str(new.get(f, "") or "").strip()
        if v:
            acc[f] = v
    return acc


def run_topology(call: dict, topo_id: str, turns: int | None = None) -> dict:
    cfg = TOPOLOGIES[topo_id]
    scammer_turns = call["turns"][:turns] if turns else call["turns"]

    history: list[tuple[str, str]] = []
    summary = ""
    prev_plan = None            # T4: 직전 턴 기획(1턴 지연 소비)
    all_metas: list[dict] = []  # 동기+비동기 모든 콜
    per_turn: list[dict] = []
    mono_schema: dict = {}      # monolith 인라인 INTEL 누적
    last_extract: dict = {}     # tiered/async/adaptive 의 추출 스키마

    for i, utt in enumerate(scammer_turns):
        crisis = roles.is_crisis_turn(utt)
        critical: list[dict] = []  # 이 턴 동기 임계경로 콜

        if cfg["compact"]:
            ctx = roles.compact_context(summary, history, utt, keep=KEEP)
        else:
            ctx = roles.full_context(history, utt)

        # ── 동기 임계경로 ──────────────────────────────────────
        if cfg["kind"] == "monolith":
            reply, schema, m = roles.monolith_turn(ctx, cfg["model"])
            m = _tag(m, "responder+extract")
            critical.append(m); all_metas.append(m)
            mono_schema = _merge_schema(mono_schema, schema)

        elif cfg["kind"] == "tiered":            # T3: 기획→응대 동기
            plan, mp = roles.planner(ctx, "opus")
            mp = _tag(mp, "planner"); critical.append(mp); all_metas.append(mp)
            reply, mr = roles.responder(ctx, "sonnet", plan)
            mr = _tag(mr, "responder"); critical.append(mr); all_metas.append(mr)

        elif cfg["kind"] == "async":             # T4: 응대만 동기(직전 기획 소비)
            reply, mr = roles.responder(ctx, "sonnet", prev_plan)
            mr = _tag(mr, "responder"); critical.append(mr); all_metas.append(mr)

        elif cfg["kind"] in ("adaptive", "adaptive_strategist"):  # T5/T6: 라우터로 모델 선택
            rmodel = "sonnet" if crisis else "haiku"
            reply, mr = roles.responder(ctx, rmodel, prev_plan)
            mr = _tag(mr, f"responder({rmodel})"); critical.append(mr); all_metas.append(mr)

        history.append((utt, reply))

        # ── 비동기(임계경로 밖) 콜 ─────────────────────────────
        if cfg["kind"] in ("tiered", "async", "adaptive", "adaptive_strategist"):
            sx, mx = roles.extract_intel(history, None, "haiku")
            all_metas.append(_tag(mx, "extract"))
            if sx:
                last_extract = _merge_schema(dict(last_extract), sx)

            if cfg["kind"] == "async":
                # 다음 턴용 기획을 비동기로 미리 계산(현재 응답 반영)
                plan_ctx = "지금까지의 통화:\n" + roles.transcript_text(history)
                prev_plan, mp = roles.planner(plan_ctx, "opus")
                all_metas.append(_tag(mp, "planner(async)"))

            # T6: Opus 전략가를 저빈도로만 비동기 호출(매 턴 아님)
            if cfg["kind"] == "adaptive_strategist" and (i + 1) % K_PLAN == 0:
                plan_ctx = "지금까지의 통화:\n" + roles.transcript_text(history)
                prev_plan, mp = roles.planner(plan_ctx, "opus")
                all_metas.append(_tag(mp, "planner(opus,저빈도)"))

            if (i + 1) % K_COMPACT == 0:
                summary, mc = roles.compactor(history, None, "haiku")
                all_metas.append(_tag(mc, "compact"))

        per_turn.append({
            "i": i, "crisis": crisis,
            "critical_ms": sum(c.get("api_ms", 0) for c in critical),
            "critical_models": [c.get("model") for c in critical],
            "reply": reply,
        })

    final_schema = mono_schema if cfg["kind"] == "monolith" else last_extract
    cms = [t["critical_ms"] for t in per_turn]
    prf = metrics.extraction_prf(final_schema, call["ground_truth"])

    # 역할별 토큰 분해
    by_role: dict[str, dict] = {}
    for m in all_metas:
        r = m.get("role", "?")
        b = by_role.setdefault(r, {"calls": 0, "in": 0, "out": 0, "cache_read": 0,
                                   "cost_krw": 0.0})
        b["calls"] += 1
        b["in"] += m.get("input_tokens", 0)
        b["out"] += m.get("output_tokens", 0)
        b["cache_read"] += m.get("cache_read", 0)
        b["cost_krw"] += metrics.call_cost_krw(m)

    return {
        "topology": topo_id, "name": cfg["name"], "call": call.get("title", ""),
        "kind": cfg["kind"], "desc": cfg["desc"], "n_turns": len(scammer_turns),
        "tokens": metrics.sum_tokens(all_metas),
        "by_role": by_role,
        "critical_ms": {
            "median": statistics.median(cms) if cms else 0,
            "mean": statistics.mean(cms) if cms else 0,
            "max": max(cms) if cms else 0,
            "sum": sum(cms),
            "per_turn": cms,
        },
        "n_calls": len(all_metas),
        "n_sync_calls_per_turn": [len(t["critical_models"]) for t in per_turn],
        "final_schema": final_schema,
        "extraction": prf,
        "per_turn": per_turn,
        "history": history,
    }
