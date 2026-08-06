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
