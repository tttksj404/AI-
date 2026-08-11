"""Fail-closed call disposition for safe test routing."""

from __future__ import annotations

from enum import StrEnum, unique

from .contracts import RiskLevel
from .handoff import BotEntryMode


@unique
class CallDisposition(StrEnum):
    """Action selected before any bot audio is sent."""

    DISCONNECT = "disconnect"
    BOT_FROM_START = "bot_from_start"
    MID_CALL_TRANSFER = "mid_call_transfer"


def decide_call_disposition(risk: RiskLevel, mode: BotEntryMode) -> CallDisposition:
    """End high/unknown risk calls and route only low-risk test paths to the bot."""
    if risk in (RiskLevel.HIGH, RiskLevel.UNKNOWN):
        return CallDisposition.DISCONNECT
    if mode is BotEntryMode.FROM_START:
        return CallDisposition.BOT_FROM_START
    return CallDisposition.MID_CALL_TRANSFER
