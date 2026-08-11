"""Deterministic safety, risk, redaction, and evidence policies."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from enum import StrEnum, unique
from typing import Final

from .contracts import RiskLevel

DEV_EVIDENCE_KEY = b"sentinel30-development-only"

INJECTION_MARKERS: Final[tuple[str, ...]] = (
    "ignore previous",
    "ignore all instructions",
    "system prompt",
    "시스템 프롬프트",
    "이전 지시를 무시",
    "지시를 무시하고",
)
SCAM_MARKERS: Final[tuple[str, ...]] = (
    "금융감독원",
    "검찰",
    "경찰",
    "계좌",
    "송금",
    "이체",
    "인증번호",
    "https://",
)
PHONE_RE: Final[re.Pattern[str]] = re.compile(r"(?<!\d)01\d[- ]?\d{3,4}[- ]?\d{4}(?!\d)")
CARD_RE: Final[re.Pattern[str]] = re.compile(r"(?<!\d)(?:\d{4}[- ]?){3}\d{4}(?!\d)")
JUMIN_RE: Final[re.Pattern[str]] = re.compile(r"(?<!\d)\d{6}-\d{7}(?!\d)")


@unique
class GuardDecision(StrEnum):
    """Input guard outcome."""

    ALLOW = "allow"
    FALLBACK = "fallback"


@dataclass(frozen=True, slots=True)
class OutputGuardResult:
    """Sanitized output and whether a safe replacement was required."""

    text: str
    blocked: bool


def classify_risk(text: str) -> RiskLevel:
    """Classify synthetic input with fail-closed handling for empty text."""
    normalized = text.casefold()
    if not normalized.strip():
        return RiskLevel.UNKNOWN
    if any(marker.casefold() in normalized for marker in INJECTION_MARKERS):
        return RiskLevel.HIGH
    if any(marker.casefold() in normalized for marker in SCAM_MARKERS):
        return RiskLevel.HIGH
    return RiskLevel.LOW


def guard_decision(text: str) -> GuardDecision:
    """Return fallback when the input attempts to redirect the agent."""
    return GuardDecision.FALLBACK if classify_risk(text) is RiskLevel.HIGH and any(
        marker.casefold() in text.casefold() for marker in INJECTION_MARKERS
    ) else GuardDecision.ALLOW


def redact_text(text: str) -> str:
    """Mask phone, card, and resident-registration-like identifiers."""
    masked = PHONE_RE.sub(lambda match: match.group(0)[:3] + "-****-****", text)
    masked = CARD_RE.sub("****-****-****-****", masked)
    return JUMIN_RE.sub("******-*******", masked)


def sanitize_output(text: str) -> OutputGuardResult:
    """Mask identifiers and replace output that exposes agent-control markers."""
    masked = redact_text(text)
    if any(marker.casefold() in masked.casefold() for marker in INJECTION_MARKERS):
        return OutputGuardResult(text=safe_fallback(), blocked=True)
    return OutputGuardResult(text=masked, blocked=False)


def safe_fallback() -> str:
    """Return the fixed response used when safety policy blocks generation."""
    return "안전 확인을 위해 추가 개인정보나 송금 요청에는 응하지 않겠습니다."


def evidence_hash(payload: str) -> str:
    """HMAC evidence payloads so traces do not expose guessable plaintext hashes."""
    key = os.environ.get("SENTINEL_EVIDENCE_HMAC_KEY", "").encode("utf-8") or DEV_EVIDENCE_KEY
    return hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
