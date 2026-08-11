"""Harness controls for data, tool, model, output, and stop permissions."""

from __future__ import annotations

from dataclasses import dataclass

from .adapters import ModelResponse
from .contracts import PipelineRequest


@dataclass(frozen=True, slots=True)
class HarnessPolicy:
    """Fail-closed execution policy for the simulated Sentinel-30 path."""

    require_synthetic: bool = True
    require_consent: bool = True
    max_turns: int = 24
    max_output_chars: int = 600
    allowed_tools: tuple[str, ...] = ("extractor", "tts")


@dataclass(frozen=True, slots=True)
class HarnessDecision:
    """Authorization result with an operator-readable reason."""

    allowed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class Harness:
    """Enforce the boundary before any model adapter is called."""

    policy: HarnessPolicy

    @classmethod
    def simulation(cls) -> Harness:
        """Return the default no-live-integration policy."""
        return cls(policy=HarnessPolicy())

    def authorize(self, request: PipelineRequest) -> HarnessDecision:
        """Authorize a request only when simulation and consent gates pass."""
        if self.policy.require_synthetic and not request.synthetic:
            return HarnessDecision(False, "synthetic_input_required")
        if self.policy.require_consent and not request.consent:
            return HarnessDecision(False, "consent_required")
        if request.voice_cloning_requested:
            return HarnessDecision(False, "voice_cloning_disabled")
        manifest = request.manifest
        if not all((manifest.dataset_id, manifest.provenance, manifest.license_id, manifest.consent_version)):
            return HarnessDecision(False, "data_manifest_required")
        if manifest.provenance not in ("synthetic", "licensed"):
            return HarnessDecision(False, "unapproved_provenance")
        if not request.turns:
            return HarnessDecision(False, "transcript_required")
        if len(request.turns) > self.policy.max_turns:
            return HarnessDecision(False, "turn_budget_exceeded")
        return HarnessDecision(True, "authorized")

    def accepts(self, response: ModelResponse) -> bool:
        """Check the machine-consumed response envelope before TTS."""
        return bool(response.text.strip()) and len(response.text) <= self.policy.max_output_chars

    def allows_tool(self, tool_name: str) -> bool:
        """Check a named capability at the point where a tool would run."""
        return tool_name in self.policy.allowed_tools
