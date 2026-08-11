"""Evaluation and promotion loop for model/rule changes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, unique

from .contracts import PipelineResult, ReviewStatus, RiskLevel


@unique
class GateAction(StrEnum):
    """Promotion decision after a candidate run."""

    PROMOTE = "promote"
    HOLD = "hold"
    ROLLBACK = "rollback"


@dataclass(frozen=True, slots=True)
class GateResult:
    """Machine-readable gate output for a run artifact."""

    action: GateAction
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PromotionLoop:
    """Keep unsafe, fallback, and review-required candidates out of promotion."""

    def evaluate(self, result: PipelineResult) -> GateResult:
        """Return hold until a candidate satisfies safety and review gates."""
        reasons: list[str] = []
        if result.human_review_required and result.review_status is not ReviewStatus.APPROVED:
            reasons.append("human_review")
        if result.fallback_used:
            reasons.append("fallback_used")
        if result.risk is RiskLevel.UNKNOWN:
            reasons.append("unknown_queue")
        action = GateAction.HOLD if reasons else GateAction.PROMOTE
        return GateResult(action=action, reasons=tuple(reasons))
