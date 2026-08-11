"""Consent-gated, deterministic training-data preparation for later GPU runs."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .policy import redact_text


@dataclass(frozen=True, slots=True)
class TrainingDataRejectedError(Exception):
    """Raised when a record violates the synthetic/consent training boundary."""

    session_id: str
    reason: str

    def __str__(self) -> str:
        return f"training record rejected: {self.session_id} ({self.reason})"


@dataclass(frozen=True, slots=True)
class TrainingRecord:
    """One redaction-ready record before deterministic split assignment."""

    session_id: str
    text: str
    label: str
    consented: bool
    synthetic: bool
    training_opt_in: bool = False


@dataclass(frozen=True, slots=True)
class TrainingSplit:
    """Immutable train/validation partition."""

    train: tuple[TrainingRecord, ...]
    validation: tuple[TrainingRecord, ...]


def _prepare(record: TrainingRecord) -> TrainingRecord:
    if not record.synthetic:
        raise TrainingDataRejectedError(record.session_id, "real_audio_or_transcript")
    if not record.consented:
        raise TrainingDataRejectedError(record.session_id, "consent_missing")
    if not record.training_opt_in:
        raise TrainingDataRejectedError(record.session_id, "training_opt_in_missing")
    return TrainingRecord(
        session_id=record.session_id,
        text=redact_text(record.text),
        label=record.label,
        consented=record.consented,
        synthetic=record.synthetic,
        training_opt_in=record.training_opt_in,
    )


def build_split(records: tuple[TrainingRecord, ...], validation_ratio: float = 0.25) -> TrainingSplit:
    """Redact records and assign them deterministically by session hash."""
    prepared = tuple(sorted((_prepare(record) for record in records), key=lambda item: item.session_id))
    boundary = int(len(prepared) * (1.0 - validation_ratio))
    ordered = tuple(
        sorted(
            prepared,
            key=lambda item: hashlib.sha256(item.session_id.encode("utf-8")).hexdigest(),
        )
    )
    return TrainingSplit(train=ordered[:boundary], validation=ordered[boundary:])
