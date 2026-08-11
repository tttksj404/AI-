"""Turn-level orchestration decisions without model or I/O side effects."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import RiskLevel, TranscriptTurn
from .policy import GuardDecision, classify_risk, guard_decision


@dataclass(frozen=True, slots=True)
class TurnPlan:
    """Decision envelope passed from orchestration to the state graph."""

    risk: RiskLevel
    input_blocked: bool
    personalization_enabled: bool
    review_required: bool


@dataclass(frozen=True, slots=True)
class Orchestrator:
    """Select policy branches; it owns no microphone, model, or TTS resource."""

    def plan(self, turns: tuple[TranscriptTurn, ...]) -> TurnPlan:
        """Create a turn plan from the latest parsed transcript turn."""
        latest_text = turns[-1].text if turns else ""
        risk = classify_risk(latest_text)
        input_blocked = guard_decision(latest_text) is GuardDecision.FALLBACK
        return TurnPlan(
            risk=risk,
            input_blocked=input_blocked,
            personalization_enabled=not input_blocked,
            review_required=input_blocked or risk in (RiskLevel.HIGH, RiskLevel.UNKNOWN),
        )
