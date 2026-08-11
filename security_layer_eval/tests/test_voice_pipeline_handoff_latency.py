from __future__ import annotations

from security_layer_eval.voice_pipeline.contracts import RiskLevel, Speaker, TranscriptTurn
from security_layer_eval.voice_pipeline.call_routing import (
    CallDisposition,
    decide_call_disposition,
)
from security_layer_eval.voice_pipeline.handoff import (
    BotEntryMode,
    build_handoff_context,
)
from security_layer_eval.voice_pipeline.latency import (
    LatencyBudget,
    LatencySample,
    summarize_latency,
)


def test_mid_call_handoff_preserves_summary_and_recent_turn_order() -> None:
    turns = (
        TranscriptTurn(Speaker.CALLER, "The caller claimed to be from a bank."),
        TranscriptTurn(Speaker.AGENT, "I will listen, but I will not share a code."),
        TranscriptTurn(Speaker.CALLER, "They asked me to install an app."),
    )

    context = build_handoff_context(
        call_id="call-001",
        mode=BotEntryMode.MID_CALL_TRANSFER,
        prior_turns=turns,
        summary="Caller claims bank affiliation and requests an app install.",
        profile_context="Use a calm, short speaking style.",
    )

    prompt = context.to_prompt()

    assert "MID_CALL_TRANSFER" in prompt
    assert "Caller claims bank affiliation" in prompt
    assert prompt.index(turns[0].text) < prompt.index(turns[1].text)
    assert prompt.index(turns[1].text) < prompt.index(turns[2].text)
    assert context.trace_digest
    assert turns[0].text not in context.to_trace_payload()


def test_start_mode_can_begin_with_empty_prior_context() -> None:
    context = build_handoff_context(
        call_id="call-002",
        mode=BotEntryMode.FROM_START,
        prior_turns=(),
        summary="",
        profile_context="",
    )

    assert "FROM_START" in context.to_prompt()
    assert context.recent_turns == ()


def test_first_audio_budget_uses_p95_and_separates_full_audio() -> None:
    samples = (
        LatencySample(120.0, 600.0, 80.0, 900.0, 100.0, 1800.0),
        LatencySample(140.0, 700.0, 90.0, 1100.0, 120.0, 2200.0),
        LatencySample(160.0, 800.0, 100.0, 1200.0, 120.0, 12500.0),
    )
    report = summarize_latency(samples, LatencyBudget(first_audio_target_ms=5000.0))

    assert report.median_first_audio_ms == 2150.0
    assert report.p95_first_audio_ms == 2380.0
    assert report.median_full_audio_ms == 2200.0
    assert report.first_audio_target_met is True
    assert report.full_audio_target_met is False


def test_high_risk_call_is_ended_before_bot_entry() -> None:
    assert decide_call_disposition(RiskLevel.HIGH, BotEntryMode.MID_CALL_TRANSFER) is CallDisposition.DISCONNECT


def test_low_risk_test_call_can_enter_bot_from_start_or_mid_call() -> None:
    assert decide_call_disposition(RiskLevel.LOW, BotEntryMode.FROM_START) is CallDisposition.BOT_FROM_START
    assert decide_call_disposition(RiskLevel.LOW, BotEntryMode.MID_CALL_TRANSFER) is CallDisposition.MID_CALL_TRANSFER
