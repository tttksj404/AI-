"""Explicit state graph for the offline voice-phishing vertical slice."""

from __future__ import annotations

from dataclasses import dataclass, field

from .adapters import (
    DialogueModel,
    DialogueRequest,
    IntelExtractor,
    ModelPool,
    OptInPersonalizer,
    Personalizer,
    SimulationDialogue,
    SimulationExtractor,
    SimulationSTT,
    SimulationTTS,
    SpeechSynthesizer,
    SpeechToText,
)
from .contracts import (
    ExtractedIntel,
    ModelRole,
    ModelTrace,
    PipelineRequest,
    PipelineResult,
    RiskLevel,
    ReviewStatus,
    Stage,
    TraceInput,
)
from .harness import Harness
from .policy import evidence_hash, safe_fallback, sanitize_output
from .orchestrator import Orchestrator


@dataclass(frozen=True, slots=True)
class VoicePipeline:
    """Run typed stages while keeping model, policy, and evidence boundaries explicit."""

    stt: SpeechToText
    dialogue: DialogueModel
    extractor: IntelExtractor
    synthesizer: SpeechSynthesizer
    personalizer: Personalizer
    harness: Harness
    model_pool: ModelPool
    orchestrator: Orchestrator = field(default_factory=Orchestrator)

    @classmethod
    def simulation(cls) -> VoicePipeline:
        """Create a fully offline pipeline with the production role map."""
        return cls(
            stt=SimulationSTT(),
            dialogue=SimulationDialogue(),
            extractor=SimulationExtractor(),
            synthesizer=SimulationTTS(),
            personalizer=OptInPersonalizer(),
            harness=Harness.simulation(),
            model_pool=ModelPool.simulation(),
        )

    def run(self, request: PipelineRequest) -> PipelineResult:
        """Execute ingest, STT, route, response, extraction, TTS, and review."""
        traces: list[ModelTrace] = []
        decision = self.harness.authorize(request)
        traces.append(self._trace(TraceInput(Stage.INGEST, ModelRole.ROUTER, decision.reason)))
        if not decision.allowed:
            return self._blocked_result(traces)

        turns = self.stt.transcribe(request)
        traces.append(self._trace(TraceInput(Stage.STT, ModelRole.STT, str(len(turns)))))
        latest = turns[-1] if turns else None
        plan = self.orchestrator.plan(turns)
        risk = plan.risk
        traces.append(self._trace(TraceInput(Stage.ROUTE, ModelRole.ROUTER, risk.value)))
        input_blocked = plan.input_blocked
        traces.append(self._trace(TraceInput(
            Stage.INPUT_GUARD,
            ModelRole.ROUTER,
            "fallback" if input_blocked else "allow",
        )))
        personalization_used = False
        fallback = input_blocked
        if input_blocked:
            reply = safe_fallback()
            traces.append(self._trace(TraceInput(Stage.RESPOND, ModelRole.ROUTER, "input_guard_fallback")))
        else:
            personalization = self.personalizer.context(request.profile)
            personalization_used = personalization.applied
            traces.append(self._trace(TraceInput(Stage.PERSONALIZE, ModelRole.PERSONALIZER, str(personalization.applied))))
            response = self.dialogue.respond(
                DialogueRequest(
                    latest_turn=latest if latest else request.turns[0],
                    transcript=turns,
                    risk=risk,
                    profile_context=personalization.context,
                )
            )
            sanitized = sanitize_output(response.text)
            fallback = sanitized.blocked or not self.harness.accepts(response)
            reply = safe_fallback() if fallback else sanitized.text
            traces.append(self._trace(TraceInput(Stage.RESPOND, ModelRole.RESPONDER, reply)))
            traces.append(self._trace(TraceInput(
                Stage.OUTPUT_GUARD,
                ModelRole.ROUTER,
                "blocked" if sanitized.blocked else "allow",
            )))
        audio_refs: tuple[str, ...] = ()
        if self.harness.allows_tool("tts"):
            speech = self.synthesizer.synthesize(reply)
            audio_refs = (speech.audio_ref,)
            traces.append(self._trace(TraceInput(Stage.TTS, ModelRole.TTS, speech.audio_ref)))
        else:
            fallback = True
        intel = ExtractedIntel()
        if self.harness.allows_tool("extractor"):
            intel = self.extractor.extract(turns)
            traces.append(self._trace(TraceInput(Stage.EXTRACT, ModelRole.EXTRACTOR, str(intel))))
        else:
            fallback = True
        traces.append(self._trace(TraceInput(Stage.EVIDENCE, ModelRole.EXTRACTOR, str(intel))))
        review_required = fallback or plan.review_required
        if review_required:
            traces.append(self._trace(TraceInput(Stage.REVIEW, ModelRole.JUDGE, risk.value)))
        traces.append(self._trace(TraceInput(Stage.COMPLETE, ModelRole.ROUTER, "complete")))
        return PipelineResult(
            risk=risk,
            reply=reply,
            intel=intel,
            audio_refs=audio_refs,
            human_review_required=review_required,
            fallback_used=fallback,
            personalization_used=personalization_used,
            review_status=ReviewStatus.PENDING if review_required else ReviewStatus.NOT_REQUIRED,
            trace=tuple(traces),
        )

    def _blocked_result(self, traces: list[ModelTrace]) -> PipelineResult:
        """Return a review-required result without invoking model adapters."""
        traces.append(self._trace(TraceInput(Stage.REVIEW, ModelRole.JUDGE, "harness_block")))
        return PipelineResult(
            risk=RiskLevel.UNKNOWN,
            reply=safe_fallback(),
            intel=ExtractedIntel(),
            audio_refs=(),
            human_review_required=True,
            fallback_used=True,
            personalization_used=False,
            review_status=ReviewStatus.PENDING,
            trace=tuple(traces),
        )

    def _trace(self, item: TraceInput) -> ModelTrace:
        """Create a hash-only trace using the role's configured model."""
        spec = self.model_pool.spec_for(item.role)
        return ModelTrace(
            stage=item.stage,
            role=item.role,
            model=spec.model,
            evidence_hash=evidence_hash(item.payload),
        )
