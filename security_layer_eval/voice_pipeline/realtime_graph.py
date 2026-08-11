"""Safe, disclosed real-time call graph and first-audio budget contract.

This module describes the execution shape needed for a consented anti-fraud
test endpoint.  It intentionally has no covert identity-switch or
"undetectable bot" state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, unique


@unique
class RealtimeState(StrEnum):
    """Observable states in one disclosed test-call loop."""

    CALL_INGRESS = "call_ingress"
    ASR_ENDPOINT = "asr_endpoint"
    RISK_GATE = "risk_gate"
    DISCONNECT = "disconnect"
    BOT_FROM_START = "bot_from_start"
    HANDOFF_SNAPSHOT = "handoff_snapshot"
    CONTEXT_READY = "context_ready"
    FILLER_PLAY = "filler_play"
    LLM_STREAM = "llm_stream"
    TTS_STREAM = "tts_stream"
    MEDIA_PACKETIZE = "media_packetize"
    MEDIA_SEND = "media_send"
    INBOUND_TURN = "inbound_turn"
    REVIEW = "review"
    COMPLETE = "complete"


class InvalidRealtimeTransition(ValueError):
    """Raised when orchestration tries to skip a safety or evidence gate."""


_TRANSITIONS: dict[RealtimeState, frozenset[RealtimeState]] = {
    RealtimeState.CALL_INGRESS: frozenset({RealtimeState.ASR_ENDPOINT}),
    RealtimeState.ASR_ENDPOINT: frozenset({RealtimeState.RISK_GATE}),
    RealtimeState.RISK_GATE: frozenset({
        RealtimeState.DISCONNECT,
        RealtimeState.BOT_FROM_START,
        RealtimeState.HANDOFF_SNAPSHOT,
    }),
    RealtimeState.DISCONNECT: frozenset({RealtimeState.REVIEW}),
    RealtimeState.BOT_FROM_START: frozenset({RealtimeState.CONTEXT_READY}),
    RealtimeState.HANDOFF_SNAPSHOT: frozenset({RealtimeState.CONTEXT_READY}),
    RealtimeState.CONTEXT_READY: frozenset({RealtimeState.FILLER_PLAY}),
    RealtimeState.FILLER_PLAY: frozenset({RealtimeState.LLM_STREAM}),
    RealtimeState.LLM_STREAM: frozenset({RealtimeState.TTS_STREAM}),
    RealtimeState.TTS_STREAM: frozenset({RealtimeState.MEDIA_PACKETIZE}),
    RealtimeState.MEDIA_PACKETIZE: frozenset({RealtimeState.MEDIA_SEND}),
    RealtimeState.MEDIA_SEND: frozenset({RealtimeState.INBOUND_TURN, RealtimeState.REVIEW}),
    RealtimeState.INBOUND_TURN: frozenset({RealtimeState.ASR_ENDPOINT}),
    RealtimeState.REVIEW: frozenset({RealtimeState.COMPLETE}),
    RealtimeState.COMPLETE: frozenset(),
}


@dataclass(frozen=True, slots=True)
class RealtimeGraph:
    """Small deterministic state machine used by the live adapter."""

    state: RealtimeState = RealtimeState.CALL_INGRESS
    history: tuple[RealtimeState, ...] = field(default_factory=tuple)

    def advance(self, next_state: RealtimeState) -> RealtimeGraph:
        """Return a new graph state only when the transition is explicitly allowed."""
        allowed = _TRANSITIONS[self.state]
        if next_state not in allowed:
            raise InvalidRealtimeTransition(
                f"{self.state.value} -> {next_state.value} is not an allowed transition"
            )
        return RealtimeGraph(
            state=next_state,
            history=(*self.history, self.state),
        )

    @property
    def terminal(self) -> bool:
        """Whether the graph has reached a terminal state."""
        return self.state is RealtimeState.COMPLETE


@dataclass(frozen=True, slots=True)
class FirstAudioBudget:
    """Sequential critical-path budget from handoff to first playable audio."""

    handoff_ms: float = 300.0
    asr_endpoint_ms: float = 250.0
    llm_ttft_ms: float = 700.0
    tts_first_chunk_ms: float = 2_600.0
    media_send_ms: float = 150.0
    target_ms: float = 5_000.0

    @property
    def critical_path_ms(self) -> float:
        """Return the additive worst-case budget used by the release gate."""
        return sum((
            self.handoff_ms,
            self.asr_endpoint_ms,
            self.llm_ttft_ms,
            self.tts_first_chunk_ms,
            self.media_send_ms,
        ))

    @property
    def target_met(self) -> bool:
        """Return whether the planned path fits the first-audio target."""
        return self.critical_path_ms <= self.target_ms
