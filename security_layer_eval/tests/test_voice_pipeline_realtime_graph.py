from __future__ import annotations

import pytest

from security_layer_eval.voice_pipeline.realtime_graph import (
    FirstAudioBudget,
    InvalidRealtimeTransition,
    RealtimeGraph,
    RealtimeState,
)


def test_disclosed_mid_call_graph_reaches_media_and_loops_to_next_turn() -> None:
    graph = RealtimeGraph()
    for state in (
        RealtimeState.ASR_ENDPOINT,
        RealtimeState.RISK_GATE,
        RealtimeState.HANDOFF_SNAPSHOT,
        RealtimeState.CONTEXT_READY,
        RealtimeState.FILLER_PLAY,
        RealtimeState.LLM_STREAM,
        RealtimeState.TTS_STREAM,
        RealtimeState.MEDIA_PACKETIZE,
        RealtimeState.MEDIA_SEND,
        RealtimeState.INBOUND_TURN,
    ):
        graph = graph.advance(state)

    assert graph.state is RealtimeState.INBOUND_TURN
    assert RealtimeState.FILLER_PLAY in graph.history
    assert RealtimeState.TTS_STREAM in graph.history


def test_graph_rejects_skipping_risk_gate_or_media_packetizer() -> None:
    with pytest.raises(InvalidRealtimeTransition):
        RealtimeGraph().advance(RealtimeState.LLM_STREAM)

    graph = RealtimeGraph()
    for state in (RealtimeState.ASR_ENDPOINT, RealtimeState.RISK_GATE, RealtimeState.BOT_FROM_START,
                  RealtimeState.CONTEXT_READY, RealtimeState.FILLER_PLAY, RealtimeState.LLM_STREAM,
                  RealtimeState.TTS_STREAM):
        graph = graph.advance(state)
    with pytest.raises(InvalidRealtimeTransition):
        graph.advance(RealtimeState.MEDIA_SEND)


def test_first_audio_budget_matches_the_remote_cosvoice3_path_target() -> None:
    budget = FirstAudioBudget(tts_first_chunk_ms=2_600.0)

    assert budget.critical_path_ms == 4_000.0
    assert budget.target_met is True

    failing_budget = FirstAudioBudget(tts_first_chunk_ms=3_700.0)
    assert failing_budget.target_met is False
