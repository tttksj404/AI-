"""First-audio and full-audio latency contracts for telephone-like tests."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LatencySample:
    """One end-to-end sample with first-audio stages separated from completion."""

    handoff_ms: float
    asr_endpoint_ms: float
    llm_ttft_ms: float
    tts_first_chunk_ms: float
    media_send_ms: float
    full_audio_ms: float

    @property
    def first_audio_ms(self) -> float:
        """Time from caller handoff to the first playable response audio."""
        return (
            self.handoff_ms
            + self.asr_endpoint_ms
            + self.llm_ttft_ms
            + self.tts_first_chunk_ms
            + self.media_send_ms
        )


@dataclass(frozen=True, slots=True)
class LatencyBudget:
    """Acceptance thresholds; first audio is the user-visible target."""

    first_audio_target_ms: float
    full_audio_target_ms: float | None = None


@dataclass(frozen=True, slots=True)
class LatencyReport:
    """Robust summary used to decide whether a scenario is usable."""

    median_first_audio_ms: float
    p95_first_audio_ms: float
    median_full_audio_ms: float
    p95_full_audio_ms: float
    first_audio_target_met: bool
    full_audio_target_met: bool


def _percentile(values: tuple[float, ...], percentile: float) -> float:
    ordered = sorted(values)
    rank = max(1, math.ceil(len(ordered) * percentile)) - 1
    return ordered[min(rank, len(ordered) - 1)]


def summarize_latency(
    samples: tuple[LatencySample, ...],
    budget: LatencyBudget,
) -> LatencyReport:
    """Summarize samples and evaluate both time-to-first-audio and completion."""
    if not samples:
        raise ValueError("at least one latency sample is required")
    first = tuple(sample.first_audio_ms for sample in samples)
    full = tuple(sample.full_audio_ms for sample in samples)
    full_target = (
        budget.full_audio_target_ms
        if budget.full_audio_target_ms is not None
        else budget.first_audio_target_ms
    )
    return LatencyReport(
        median_first_audio_ms=float(sorted(first)[len(first) // 2]),
        p95_first_audio_ms=_percentile(first, 0.95),
        median_full_audio_ms=float(sorted(full)[len(full) // 2]),
        p95_full_audio_ms=_percentile(full, 0.95),
        first_audio_target_met=_percentile(first, 0.95) <= budget.first_audio_target_ms,
        full_audio_target_met=_percentile(full, 0.95) <= full_target,
    )
