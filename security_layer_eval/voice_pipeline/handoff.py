"""Safe context handoff contracts for start-of-call and mid-call entry."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import StrEnum, unique

from .contracts import TranscriptTurn


@unique
class BotEntryMode(StrEnum):
    """How the disclosed test bot enters a call."""

    FROM_START = "from_start"
    MID_CALL_TRANSFER = "mid_call_transfer"


@dataclass(frozen=True, slots=True)
class HandoffContext:
    """Bounded context passed to the next responder after a call handoff."""

    call_id: str
    mode: BotEntryMode
    summary: str
    recent_turns: tuple[TranscriptTurn, ...]
    profile_context: str
    trace_digest: str

    def to_prompt(self) -> str:
        """Render LLM context while keeping telemetry separate from raw content."""
        lines = ["[CALL_HANDOFF]", f"entry_mode={self.mode.name}"]
        if self.summary:
            lines.append(f"summary={self.summary}")
        if self.profile_context:
            lines.append(f"opt_in_profile={self.profile_context}")
        lines.append("recent_turns=")
        lines.extend(f"{turn.speaker.value}: {turn.text}" for turn in self.recent_turns)
        return "\n".join(lines)

    def to_trace_payload(self) -> str:
        """Return metadata only; raw transcript text never enters the trace payload."""
        return f"{self.call_id}|{self.mode.value}|{self.trace_digest}|turns={len(self.recent_turns)}"


def build_handoff_context(
    *,
    call_id: str,
    mode: BotEntryMode,
    prior_turns: tuple[TranscriptTurn, ...],
    summary: str,
    profile_context: str,
    max_recent_turns: int = 8,
) -> HandoffContext:
    """Build a bounded, hashable context envelope for a safe test handoff."""
    bounded_turns = prior_turns[-max_recent_turns:] if max_recent_turns > 0 else ()
    raw = "|".join(
        (call_id, mode.value, summary, profile_context)
        + tuple(f"{turn.speaker.value}:{turn.text}" for turn in bounded_turns)
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return HandoffContext(
        call_id=call_id,
        mode=mode,
        summary=summary,
        recent_turns=bounded_turns,
        profile_context=profile_context,
        trace_digest=digest,
    )
