"""오케스트레이션 역할(요소) 모듈.

역할
  R 응대(responder)   : 김순자 할머니 페르소나 1턴 응답. 임계경로(동기) 후보.
  P 기획(planner)     : 오케스트레이터 — 다음에 캐낼 1순위 단서 + 한 문장 전술.
  C 압축(compactor)   : K턴마다 통화 메모리를 요약(입력 토큰을 일정하게 유지).
  X 추출(extractor)   : 통화 전체에서 스키마 단서 추출(off-path 가능).
  monolith            : 단일 모델 1콜이 응답+단서추출을 동시에(순진한 baseline).
  router              : 위기턴(이체/계좌/앱 등) 결정론적 판정 — T5 에스컬레이션용.

모든 LLM 접점은 llm.complete_metered / complete_json_metered 만 사용 → 토큰/지연 실측.
"""
from __future__ import annotations
import re

from bot import llm
from bot.persona import build_bot_system

BOT_SYSTEM = build_bot_system()

REPLY_INSTR = ("\n\n너는 김순자 할머니다. 위 통화에 이어 '할머니'로서 다음 한마디만 "
               "통화하듯 한두 문장으로 짧게 말하라. 지문·따옴표·설명 없이 대사만 출력.")

# 단일 모델 baseline: 응답과 단서갱신을 한 출력에 섞는다(역할 미분리의 대가를 드러냄).
MONOLITH_SYSTEM = BOT_SYSTEM + """

[추가 임무 — 매 턴]
대사를 출력한 뒤, 반드시 마지막 줄에 지금까지 통화에서 파악한 단서를 아래 형식으로 한 줄 덧붙여라.
<INTEL>{"agency":"","account":"","amount":"","deadline":"","app":""}</INTEL>
없는 값은 빈 문자열. 이 줄은 내부 기록용이며 상대에게 말하는 내용이 아니다."""

PLANNER_SYSTEM = """너는 보이스피싱 대응 미끼봇의 작전 오케스트레이터다.
지금까지의 통화를 보고, 아직 확보하지 못한 핵심 단서
(사칭기관/계좌번호/요구금액/송금시한/악성앱·URL) 중 다음 턴에 캐낼 1순위와,
73세 할머니가 의심받지 않게 그것을 자연스럽게 끌어낼 한 문장 전술을 정한다.
JSON 하나만 출력(코드펜스 금지):
{"next_target":"<항목>","tactic":"<할머니가 쓸 한 문장 전략>"}"""

COMPACTOR_SYSTEM = """너는 통화 메모리 압축기다. 아래 통화를 미끼봇이 다음 응답에 쓸 수 있게
'수집된 단서 + 현재 분위기/요구'를 5줄 이내 한국어 요약으로 압축하라.
새 정보 위주로, 군더더기 없이. 머리말 없이 요약만 출력."""

EXTRACT_SYSTEM = """너는 보이스피싱 통화에서 단서를 추출하는 분석기다.
아래 통화 전체에서 '사기범이 실제로 말한 사실'만 뽑아 JSON 하나만 출력(코드펜스 금지):
{"agency":"<사칭기관>","account":"<계좌번호>","amount":"<요구금액>","deadline":"<송금시한>","app":"<악성앱/URL>"}
없는 값은 빈 문자열. 추정·창작 금지."""


# ── 컨텍스트 빌더 ──────────────────────────────────────────────────
def _lines(history: list[tuple[str, str]]) -> list[str]:
    out = []
    for scammer, bot in history:
        out.append(f"사기범: {scammer}")
        if bot:
            out.append(f"할머니: {bot}")
    return out


def full_context(history, next_utt) -> str:
    lines = _lines(history) + [f"사기범: {next_utt}"]
    return "지금까지의 통화:\n" + "\n".join(lines)


def compact_context(summary, history, next_utt, keep: int = 2) -> str:
    head = f"[이전 통화 요약]\n{summary}\n\n" if summary else ""
    recent = _lines(history[-keep:]) + [f"사기범: {next_utt}"]
    return head + "[최근 대화]\n" + "\n".join(recent)


def transcript_text(history, next_utt=None) -> str:
    lines = _lines(history)
    if next_utt:
        lines.append(f"사기범: {next_utt}")
    return "\n".join(lines)


def _plan_hint(plan: dict | None) -> str:
    if not plan or not isinstance(plan, dict):
        return ""
    tgt = plan.get("next_target", "")
    tac = plan.get("tactic", "")
    if not (tgt or tac):
        return ""
    return f"\n\n[작전 힌트] 이번엔 특히 '{tgt}'를 캐내라. 전술: {tac}"


# ── 역할 함수 (모두 (결과, meta) 반환) ─────────────────────────────
def responder(context: str, model: str, plan: dict | None = None):
    user = context + _plan_hint(plan) + REPLY_INSTR
    text, meta = llm.complete_metered(BOT_SYSTEM, user, model=model)
    return text.strip(), meta


_INTEL_RE = re.compile(r"<INTEL>\s*(\{.*?\})\s*</INTEL>", re.DOTALL)


def monolith_turn(context: str, model: str):
    """단일 모델 1콜: 대사 + <INTEL> 단서. (대사, schema, meta)."""
    user = context + REPLY_INSTR
    text, meta = llm.complete_metered(MONOLITH_SYSTEM, user, model=model)
    schema = {}
    m = _INTEL_RE.search(text)
    if m:
        schema = llm._parse_json(m.group(1))
        if schema.get("_parse_error"):
            schema = {}
    reply = _INTEL_RE.sub("", text).strip()
    return reply, schema, meta


def planner(context: str, model: str = "opus"):
    plan, meta = llm.complete_json_metered(PLANNER_SYSTEM, context, model=model)
    return plan, meta


def compactor(history, next_utt, model: str = "haiku"):
    summary, meta = llm.complete_metered(COMPACTOR_SYSTEM,
                                         transcript_text(history, next_utt), model=model)
    return summary.strip(), meta


def extract_intel(history, next_utt, model: str = "haiku"):
    schema, meta = llm.complete_json_metered(EXTRACT_SYSTEM,
                                             transcript_text(history, next_utt), model=model)
    if schema.get("_parse_error"):
        schema = {}
    return schema, meta


# ── 라우터 (결정론적, 비용 0) ──────────────────────────────────────
_CRISIS_RE = re.compile(
    r"이체|송금|보내|입금|계좌|인증번호|otp|비밀번호|보안카드|앱|설치|링크|"
    r"구속|영장|상환|마감", re.I)


def is_crisis_turn(utt: str) -> bool:
    """위기/핵심 정보 턴인가 — T5 가 Haiku→Sonnet 에스컬레이션 판단에 사용."""
    return bool(_CRISIS_RE.search(utt))
