"""미끼봇 응답 품질 판정기(Opus, 오프라인 — 비용/지연 집계에 미포함).

3축 0~100 채점:
  cover   위장 유지: AI/봇/시스템 정체를 드러내지 않고 73세 할머니로 일관됐는가
  natural 자연스러움: 실제 노인 통화처럼 짧고 그럴듯한가
  elicit  정보유도: 사기범이 기관/계좌/금액/시한/앱을 더 말하도록 자연스럽게 유도했는가
"""
from __future__ import annotations

from bot import llm

JUDGE_SYSTEM = """너는 보이스피싱 대응 'AI 미끼봇' 품질 평가관이다.
아래는 사기범과, 73세 할머니로 위장한 AI 미끼봇의 통화다(할머니 대사가 미끼봇 출력).
미끼봇 대사만 평가 대상이다. 다음 3축을 각각 0~100 정수로 채점하라.
- cover   위장 유지: 자신이 AI/봇/시스템/녹음임을 드러내지 않고 할머니답게 일관됐는가
- natural 자연스러움: 실제 노인 통화처럼 짧고 자연스러운가(장황/기계적이면 감점)
- elicit  정보유도: 사기범이 기관/계좌/금액/시한/악성앱을 더 말하도록 자연스럽게 캐물었는가
JSON 하나만 출력(코드펜스 금지):
{"cover":int,"natural":int,"elicit":int,"overall":int,"reason":"한국어 한 문장"}"""


def judge_transcript(history: list[tuple[str, str]], model: str = "opus") -> dict:
    lines = []
    for scammer, bot in history:
        lines.append(f"사기범: {scammer}")
        lines.append(f"할머니(미끼봇): {bot}")
    user = "통화:\n" + "\n".join(lines) + "\n\n위 미끼봇 대사를 채점하라."
    out = llm.complete_json(JUDGE_SYSTEM, user, model=model)
    if out.get("_parse_error"):
        return {"cover": 0, "natural": 0, "elicit": 0, "overall": 0,
                "reason": "판정 파싱 실패", "_parse_error": True}
    for k in ("cover", "natural", "elicit", "overall"):
        try:
            out[k] = int(out.get(k, 0))
        except Exception:
            out[k] = 0
    if not out.get("overall"):
        out["overall"] = round((out["cover"] + out["natural"] + out["elicit"]) / 3)
    return out
