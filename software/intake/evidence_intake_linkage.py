#!/usr/bin/env python3
"""Protected linkage from staged artifacts to evidence review candidates.

artifact_id: component-pia-evidence-intake-linkage-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from software.intake.evidence_extraction import (
    PARSER_VERSION,
    EvidenceExtractionError,
    SafeEvidenceExtractor,
)
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)


class ProtectedEvidenceIntakeLinkage:
    """Coordinate in-memory extraction and encrypted candidate persistence."""

    def __init__(
        self,
        store: ProtectedParticipantIntakeStore,
        *,
        extractor: SafeEvidenceExtractor | None = None,
    ) -> None:
        self.store = store
        self.extractor = extractor or SafeEvidenceExtractor()

    def extract(
        self,
        *,
        session_id: str,
        source_artifact_id: str,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        artifact, content = self.store.read_artifact_content(
            session_id=session_id,
            source_artifact_id=source_artifact_id,
            actor_subject=actor_subject,
            actor_role=actor_role,
        )
        canonical_source_artifact_id = str(
            artifact.get("duplicate_of_source_artifact_id")
            or source_artifact_id
        )
        if canonical_source_artifact_id != source_artifact_id:
            artifact, content = self.store.read_artifact_content(
                session_id=session_id,
                source_artifact_id=canonical_source_artifact_id,
                actor_subject=actor_subject,
                actor_role=actor_role,
            )
        try:
            result = self.extractor.extract(
                filename=str(artifact["original_filename"]),
                content=content,
            )
        except EvidenceExtractionError as exc:
            result = {
                "extraction_status": "failed",
                "parser_id": PARSER_VERSION,
                "parser_profile": "safe-parser-failed",
                "source_extension": Path(
                    str(artifact["original_filename"])
                ).suffix.lower(),
                "extracted_text": "",
                "extracted_text_checksum": "",
                "candidates": [],
                "warnings": [str(exc)],
                "capability_assertions_created": [],
            }
        return self.store.save_evidence_extraction(
            session_id=session_id,
            source_artifact_id=canonical_source_artifact_id,
            result=result,
            actor_subject=actor_subject,
            actor_role=actor_role,
        )

    def review(
        self,
        *,
        session_id: str,
        evidence_id: str,
        disposition: str,
        corrected_text: str = "",
        reason: str = "",
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        return self.store.review_evidence_candidate(
            session_id=session_id,
            evidence_id=evidence_id,
            disposition=disposition,
            corrected_text=corrected_text,
            reason=reason,
            actor_subject=actor_subject,
            actor_role=actor_role,
        )

    def status(
        self,
        *,
        session_id: str,
        actor_role: str,
    ) -> list[dict[str, Any]]:
        return self.store.list_evidence_extractions(
            session_id=session_id,
            actor_role=actor_role,
        )
