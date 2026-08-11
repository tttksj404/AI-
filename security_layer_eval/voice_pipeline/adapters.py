"""Typed model contracts and deterministic adapters for the vertical slice."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, Final

from .contracts import (
    ExtractedIntel,
    ModelRole,
    PipelineRequest,
    RiskLevel,
    TranscriptTurn,
    UserProfile,
)

AMOUNT_RE: Final[re.Pattern[str]] = re.compile(r"(?<!\d)([\d,]+)\s*원")
URL_RE: Final[re.Pattern[str]] = re.compile(r"https?://[A-Za-z0-9./?&=_:%#-]+")
ACCOUNT_RE: Final[re.Pattern[str]] = re.compile(r"(?<!\d)\d{2,3}-\d{3,4}-\d{4}(?!\d)")


@dataclass(frozen=True, slots=True)
class ModelSpec:
    """Deployment contract for one role, independent of provider SDKs."""

    role: ModelRole
    model: str
    backend: str
    device: str
    offline_only: bool
    requires_gpu: bool


@dataclass(frozen=True, slots=True)
class ModelPool:
    """Role-to-model map used by both simulation and GPU deployment."""

    specs: tuple[ModelSpec, ...]

    @classmethod
    def default(cls) -> ModelPool:
        """Build the recommended local runtime role map."""
        return cls(
            specs=(
                ModelSpec(ModelRole.STT, "Systran/faster-whisper-large-v3-turbo", "faster-whisper", "cuda", False, True),
                ModelSpec(ModelRole.ROUTER, "rule-router-v1", "policy", "cpu", False, False),
                ModelSpec(ModelRole.RESPONDER, "Qwen/Qwen3-4B", "vllm", "cuda", False, True),
                ModelSpec(ModelRole.EXTRACTOR, "Qwen/Qwen3-4B", "vllm-json", "cuda", False, True),
                ModelSpec(ModelRole.PERSONALIZER, "Qwen/Qwen3-4B+user-lora", "peft", "cuda", False, True),
                ModelSpec(ModelRole.TTS, "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", "qwen3-tts", "cuda", False, True),
                ModelSpec(ModelRole.JUDGE, "Qwen/Qwen3-32B", "vllm", "cuda", True, True),
            )
        )

    @classmethod
    def simulation(cls) -> ModelPool:
        """Build a no-GPU role map so offline runs cannot imply GPU execution."""
        return cls(
            specs=tuple(
                ModelSpec(
                    role=spec.role,
                    model=f"simulation-{spec.role.value}",
                    backend="simulation",
                    device="cpu",
                    offline_only=spec.offline_only,
                    requires_gpu=False,
                )
                for spec in cls.default().specs
            )
        )

    def spec_for(self, role: ModelRole) -> ModelSpec:
        """Resolve a role or raise a typed configuration error."""
        for spec in self.specs:
            if spec.role is role:
                return spec
        raise ModelRoleUnavailableError(role=role)


@dataclass(frozen=True, slots=True)
class ModelRoleUnavailableError(Exception):
    """Raised when a required role is absent from a model pool."""

    role: ModelRole

    def __str__(self) -> str:
        return f"model role unavailable: {self.role.value}"


@dataclass(frozen=True, slots=True)
class DialogueRequest:
    """Typed input passed to the responder model."""

    latest_turn: TranscriptTurn
    transcript: tuple[TranscriptTurn, ...]
    risk: RiskLevel
    profile_context: str


@dataclass(frozen=True, slots=True)
class ModelResponse:
    """Typed responder output before safety sanitization."""

    text: str
    model: str


@dataclass(frozen=True, slots=True)
class SpeechResult:
    """Reference to synthesized audio; simulation never writes real audio."""

    audio_ref: str
    model: str


@dataclass(frozen=True, slots=True)
class PersonalizationResult:
    """Whether user context was applied under explicit opt-in."""

    applied: bool
    context: str


class SpeechToText(Protocol):
    """ASR adapter contract."""

    def transcribe(self, request: PipelineRequest) -> tuple[TranscriptTurn, ...]: ...


class DialogueModel(Protocol):
    """Responder adapter contract."""

    def respond(self, request: DialogueRequest) -> ModelResponse: ...


class IntelExtractor(Protocol):
    """Structured evidence extraction contract."""

    def extract(self, turns: tuple[TranscriptTurn, ...]) -> ExtractedIntel: ...


class SpeechSynthesizer(Protocol):
    """TTS adapter contract."""

    def synthesize(self, text: str) -> SpeechResult: ...


class Personalizer(Protocol):
    """Consent-gated personalization contract."""

    def context(self, profile: UserProfile) -> PersonalizationResult: ...


@dataclass(frozen=True, slots=True)
class SimulationSTT:
    """Pass through pre-authored synthetic turns without downloading a model."""

    model: str = "simulated-faster-whisper"

    def transcribe(self, request: PipelineRequest) -> tuple[TranscriptTurn, ...]:
        return request.turns


@dataclass(frozen=True, slots=True)
class SimulationDialogue:
    """Deterministic responder used for offline tests and demos."""

    model: str = "simulated-Qwen3-4B"

    def respond(self, request: DialogueRequest) -> ModelResponse:
        match request.risk:
            case RiskLevel.HIGH:
                text = "확인 중입니다. 추가 송금이나 인증번호 전달은 진행하지 마세요."
            case RiskLevel.LOW:
                text = f"{request.profile_context} 내용을 확인해 보겠습니다." if request.profile_context else "내용을 확인해 보겠습니다."
            case RiskLevel.UNKNOWN:
                text = "확인이 필요한 통화입니다. 담당자 검토로 전환하겠습니다."
            case unreachable:
                from typing import assert_never
                assert_never(unreachable)
        return ModelResponse(text=text, model=self.model)


@dataclass(frozen=True, slots=True)
class SimulationExtractor:
    """Extract evidence with transparent regexes for contract testing."""

    model: str = "simulated-Qwen3-4B-json"

    def extract(self, turns: tuple[TranscriptTurn, ...]) -> ExtractedIntel:
        text = " ".join(turn.text for turn in turns)
        amount_match = AMOUNT_RE.search(text)
        url_match = URL_RE.search(text)
        account_match = ACCOUNT_RE.search(text)
        agency = "금융감독원" if "금융감독원" in text else ""
        return ExtractedIntel(
            agency=agency,
            account=account_match.group(0) if account_match else "",
            amount=amount_match.group(1).replace(",", "") if amount_match else "",
            url=url_match.group(0).rstrip(".,") if url_match else "",
        )


@dataclass(frozen=True, slots=True)
class SimulationTTS:
    """Return deterministic audio references instead of producing a voice file."""

    model: str = "simulated-Qwen3-TTS-0.6B"

    def synthesize(self, text: str) -> SpeechResult:
        from .policy import evidence_hash
        return SpeechResult(audio_ref=f"simulation://tts/{evidence_hash(text)[:12]}", model=self.model)


@dataclass(frozen=True, slots=True)
class OptInPersonalizer:
    """Apply only the minimal profile field after explicit user opt-in."""

    model: str = "simulated-user-profile-adapter"

    def context(self, profile: UserProfile) -> PersonalizationResult:
        if profile.memory_opt_in and profile.processing_opt_in and profile.preferred_greeting:
            return PersonalizationResult(applied=True, context=profile.preferred_greeting)
        return PersonalizationResult(applied=False, context="")
