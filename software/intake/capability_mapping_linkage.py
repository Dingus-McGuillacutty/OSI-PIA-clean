#!/usr/bin/env python3
"""Protected handoff from accepted evidence to mapping proposals.

artifact_id: component-pia-capability-mapping-linkage-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import re
import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Any

from software.intake.local_private_intake import IntakePreflightError
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)


MAPPING_PROFILE = "pia-capability-evidence-mapping-0.2"
_CAPABILITY_ENTRY = re.compile(
    r"id:\s*'(?P<id>CAP-PIA-[A-Z0-9-]+)'\s*,\s*"
    r"name:\s*'(?P<name>[^']+)'",
    re.DOTALL,
)
_PROFILE_MIGRATION = (
    Path(__file__).resolve().parents[2]
    / "graph"
    / "migrations"
    / "005_pia_behavioral_capability_profile.cypher"
)
_GENERIC_CAPABILITY_WORDS = {
    "ability", "capability", "leadership", "management", "operations",
    "professional", "skill", "skills", "work",
}


@lru_cache(maxsize=1)
def capability_catalog() -> dict[str, str]:
    """Load the working PIA capability vocabulary without participant data."""

    try:
        content = _PROFILE_MIGRATION.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise IntakePreflightError(
            "The working PIA capability vocabulary is unavailable."
        ) from exc
    catalog = {
        match.group("id"): match.group("name")
        for match in _CAPABILITY_ENTRY.finditer(content)
    }
    if not catalog:
        raise IntakePreflightError(
            "The working PIA capability vocabulary is invalid."
        )
    return catalog


class ProtectedCapabilityMappingLinkage:
    """Create review-required mapping proposals; never accept or project them."""

    def __init__(self, store: ProtectedParticipantIntakeStore) -> None:
        self.store = store

    def propose(
        self,
        *,
        session_id: str,
        evidence_id: str,
        proposal: dict[str, Any],
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        capability_id = str(proposal.get("profile_capability_id", "")).strip()
        catalog = capability_catalog()
        if capability_id not in catalog:
            raise IntakePreflightError(
                "Choose a capability from the working PIA capability profile."
            )
        normalized = dict(proposal)
        normalized["mapping_profile"] = MAPPING_PROFILE
        normalized["profile_capability_id"] = capability_id
        normalized["capability_name"] = catalog[capability_id]
        return self.store.create_capability_mapping_proposal(
            session_id=session_id,
            evidence_id=evidence_id,
            proposal=normalized,
            actor_subject=actor_subject,
            actor_role=actor_role,
        )

    def status(
        self,
        *,
        session_id: str,
        actor_role: str,
    ) -> list[dict[str, Any]]:
        return self.store.list_capability_mapping_proposals(
            session_id=session_id,
            actor_role=actor_role,
        )

    def accept_direct(
        self,
        *,
        session_id: str,
        evidence_id: str,
        proposal: dict[str, Any],
        actor_subject: str,
        actor_role: str,
        custom_capability_name: str = "",
    ) -> dict[str, Any]:
        """Record one authorized reviewer's bounded capability decision."""

        session = self.store.resume_session(
            session_id,
            actor_subject=actor_subject,
            actor_role=actor_role,
        )
        if session.get("processing_state") != "review_complete":
            raise IntakePreflightError(
                "Complete authorized evidence review before linking capabilities."
            )
        candidate = next(
            (
                item
                for extraction in session.get("evidence_extractions", [])
                for item in extraction.get("evidence_candidates", [])
                if item.get("evidence_id") == evidence_id
            ),
            None,
        )
        if candidate is None:
            raise IntakePreflightError("Choose accepted evidence first.")
        artifact = next(
            (
                item
                for item in session.get("artifacts", [])
                if item.get("source_artifact_id") == candidate.get("source_id")
            ),
            None,
        )
        normalized = dict(proposal)
        if artifact and artifact.get("document_type") == "credential_learning":
            if normalized.get("inference_level") != "contextually_suggested":
                raise IntakePreflightError(
                    "Training evidence may support bounded knowledge exposure, "
                    "not a strong operational-capability inference."
                )
            normalized.update(
                evidence_role="educational_preparation",
                claim_scope="knowledge_exposure",
                application_status="topically_aligned_not_verified",
                confidence=min(float(normalized.get("confidence", 0.4)), 0.49),
                credential_definition_status="source_defined",
                credential_definition_source="submitted credential record",
            )
        custom_name = " ".join(custom_capability_name.split())
        if custom_name:
            if (
                len(custom_name) < 3
                or len(custom_name) > 100
                or len(custom_name.split()) > 8
                or not re.fullmatch(r"[A-Za-z][A-Za-z0-9 &/()'-]*", custom_name)
            ):
                raise IntakePreflightError(
                    "A new capability must be a concise, readable name of 3 to 100 characters."
                )
            evidence_tokens = {
                token
                for token in re.findall(
                    r"[a-z0-9]+", str(candidate.get("evidence_text", "")).lower()
                )
                if len(token) > 3 and token not in _GENERIC_CAPABILITY_WORDS
            }
            capability_tokens = {
                token
                for token in re.findall(r"[a-z0-9]+", custom_name.lower())
                if len(token) > 3 and token not in _GENERIC_CAPABILITY_WORDS
            }
            if not capability_tokens or not capability_tokens.intersection(
                evidence_tokens
            ):
                raise IntakePreflightError(
                    "The new capability name is not reasonably grounded in the "
                    "accepted evidence wording. Choose a listed capability or use "
                    "a narrower evidence-linked name."
                )
            digest = hashlib.sha256(custom_name.casefold().encode()).hexdigest()[:12]
            normalized["mapping_profile"] = MAPPING_PROFILE
            normalized["profile_capability_id"] = f"CAP-PIA-LOCAL-{digest.upper()}"
            normalized["capability_name"] = custom_name
            created = self.store.create_capability_mapping_proposal(
                session_id=session_id,
                evidence_id=evidence_id,
                proposal=normalized,
                actor_subject=actor_subject,
                actor_role=actor_role,
            )
        else:
            created = self.propose(
                session_id=session_id,
                evidence_id=evidence_id,
                proposal=normalized,
                actor_subject=actor_subject,
                actor_role=actor_role,
            )
        return self.store.review_capability_mapping_proposal(
            session_id=session_id,
            mapping_id=str(created["mapping_id"]),
            disposition="accepted",
            reason="Authorized reviewer recorded a direct bounded capability decision.",
            narrowed_scope_limit="",
            narrowed_negative_boundary="",
            actor_subject=actor_subject,
            actor_role=actor_role,
            allow_same_actor=True,
        )

    def review(
        self,
        *,
        session_id: str,
        mapping_id: str,
        disposition: str,
        reason: str,
        narrowed_scope_limit: str,
        narrowed_negative_boundary: str,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        return self.store.review_capability_mapping_proposal(
            session_id=session_id,
            mapping_id=mapping_id,
            disposition=disposition,
            reason=reason,
            narrowed_scope_limit=narrowed_scope_limit,
            narrowed_negative_boundary=narrowed_negative_boundary,
            actor_subject=actor_subject,
            actor_role=actor_role,
        )

    def vocabulary(self) -> list[dict[str, str]]:
        return [
            {"profile_capability_id": capability_id, "capability_name": name}
            for capability_id, name in sorted(capability_catalog().items())
        ]
