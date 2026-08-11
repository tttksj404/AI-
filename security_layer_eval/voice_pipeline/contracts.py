"""Voice-phishing pipeline value objects and JSON boundary types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, unique
from typing import Final, NewType, TypeAlias

SessionId = NewType("SessionId", str)
JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
EMPTY_TEXT: Final = ""


@unique
class ModelRole(StrEnum):
    """Model roles are routed independently so each can be evaluated."""

    STT = "stt"
    ROUTER = "router"
    RESPONDER = "responder"
    EXTRACTOR = "extractor"
    PERSONALIZER = "personalizer"
    TTS = "tts"
    JUDGE = "judge"


@unique
class Speaker(StrEnum):
    """Synthetic conversation speaker labels."""

    CALLER = "caller"
    AGENT = "agent"


@unique
class RiskLevel(StrEnum):
    """Risk state used by routing and human-review gates."""

    LOW = "low"
    HIGH = "high"
    UNKNOWN = "unknown"


@unique
class Stage(StrEnum):
    """Observable state-graph stages."""

    INGEST = "ingest"
    STT = "stt"
    INPUT_GUARD = "input_guard"
    PERSONALIZE = "personalize"
    ROUTE = "route"
    RESPOND = "respond"
    OUTPUT_GUARD = "output_guard"
    EXTRACT = "extract"
    TTS = "tts"
    EVIDENCE = "evidence"
    REVIEW = "review"
    COMPLETE = "complete"


@unique
class ReviewStatus(StrEnum):
    """Human-review state; required-risk results begin in pending state."""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class DataManifest:
    """Provenance metadata required before a synthetic run can start."""

    dataset_id: str
    provenance: str
    license_id: str
    consent_version: str


@dataclass(frozen=True, slots=True)
class UserProfile:
    """Minimal, consent-gated personalization context."""

    profile_id: str
    preferred_greeting: str
    memory_opt_in: bool
    processing_opt_in: bool = False
    training_opt_in: bool = False
    external_model_opt_in: bool = False
    consent_version: str = ""


@dataclass(frozen=True, slots=True)
class TranscriptTurn:
    """One parsed transcript turn."""

    speaker: Speaker
    text: str


@dataclass(frozen=True, slots=True)
class PipelineRequest:
    """Input that is allowed into the simulation pipeline."""

    session_id: str
    synthetic: bool
    consent: bool
    turns: tuple[TranscriptTurn, ...]
    profile: UserProfile
    manifest: DataManifest
    voice_cloning_requested: bool = False


@dataclass(frozen=True, slots=True)
class ExtractedIntel:
    """Structured evidence extracted from a synthetic transcript."""

    agency: str = EMPTY_TEXT
    account: str = EMPTY_TEXT
    amount: str = EMPTY_TEXT
    url: str = EMPTY_TEXT
    deadline: str = EMPTY_TEXT
    app: str = EMPTY_TEXT


@dataclass(frozen=True, slots=True)
class ModelTrace:
    """Hash-only evidence for one model or deterministic policy decision."""

    stage: Stage
    role: ModelRole
    model: str
    evidence_hash: str


@dataclass(frozen=True, slots=True)
class TraceInput:
    """Input used to create a trace entry without parameter sprawl."""

    stage: Stage
    role: ModelRole
    payload: str


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """User-visible result plus machine-readable evidence and gates."""

    risk: RiskLevel
    reply: str
    intel: ExtractedIntel
    audio_refs: tuple[str, ...]
    human_review_required: bool
    fallback_used: bool
    personalization_used: bool
    review_status: ReviewStatus
    trace: tuple[ModelTrace, ...]

    def to_json(self) -> JsonObject:
        """Serialize only the stable result contract, never raw transcript text."""
        public_account = "redacted" if self.intel.account else EMPTY_TEXT
        public_url = "redacted" if self.intel.url else EMPTY_TEXT
        return {
            "risk": self.risk.value,
            "reply": self.reply,
            "intel": {
                "agency": self.intel.agency,
                "account": public_account,
                "amount": self.intel.amount,
                "url": public_url,
                "deadline": self.intel.deadline,
                "app": self.intel.app,
            },
            "audio_refs": list(self.audio_refs),
            "human_review_required": self.human_review_required,
            "fallback_used": self.fallback_used,
            "personalization_used": self.personalization_used,
            "review_status": self.review_status.value,
            "trace": [
                {
                    "stage": item.stage.value,
                    "role": item.role.value,
                    "model": item.model,
                    "evidence_hash": item.evidence_hash,
                }
                for item in self.trace
            ],
        }
