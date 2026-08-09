#!/usr/bin/env python3
"""Bounded handoff from accepted mappings to preview and dry-run output.

artifact_id: component-pia-mapping-output-linkage-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from software.intake.local_private_intake import IntakePreflightError
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)
from software.intake.sandbox_projection_assurance import SandboxProjectionAssurance


OUTPUT_PROFILE = "pia-mapping-output-handoff-0.2"
_TEST_ONLY_TERMS = {"test", "testing", "synthetic", "placeholder"}


def _participant_ready(item: dict[str, Any]) -> tuple[bool, str]:
    """Reject incomplete or obvious test-only framing from polished output."""

    for field in ("confidence_basis", "scope_limit", "negative_boundary"):
        value = str(item.get(field, "")).strip()
        if len(value) < 16:
            return False, f"{field.replace('_', ' ')} is too brief"
        if value.lower() in _TEST_ONLY_TERMS:
            return False, f"{field.replace('_', ' ')} is test-only"
    return True, ""


class ProtectedMappingOutputLinkage:
    """Render accepted mappings without graph writes, scoring, or publication."""

    def __init__(self, store: ProtectedParticipantIntakeStore) -> None:
        self.store = store

    def preview(
        self, *, session_id: str, actor_role: str
    ) -> dict[str, Any]:
        mappings = self.store.list_capability_mapping_proposals(
            session_id=session_id, actor_role=actor_role
        )
        accepted = [
            item for item in mappings if item.get("review_status") == "accepted"
        ]
        if not accepted:
            raise IntakePreflightError(
                "A preview requires at least one accepted mapping."
            )
        accepted.sort(key=lambda item: str(item.get("mapping_id", "")))
        selection = [str(item["mapping_id"]) for item in accepted]
        package_checksum = hashlib.sha256(
            json.dumps(selection, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        technical_interpretations = [
            {
                "mapping_id": item["mapping_id"],
                "profile_capability_id": item["profile_capability_id"],
                "capability": item["capability_name"],
                "inference_level": item["inference_level"],
                "confidence": item["confidence"],
                "confidence_basis": item["confidence_basis"],
                "scope_limit": item["scope_limit"],
                "negative_boundary": item["negative_boundary"],
                "source_independence_note": item["source_independence_note"],
                "evidence_id": item["evidence_id"],
            }
            for item in accepted
        ]
        groups: dict[str, dict[str, Any]] = {}
        quality_findings: list[dict[str, str]] = []
        for item in accepted:
            ready, reason = _participant_ready(item)
            if not ready:
                quality_findings.append(
                    {
                        "mapping_id": item["mapping_id"],
                        "reason": reason,
                        "next_action": (
                            "Create a new bounded proposal with participant-readable "
                            "basis, scope, and boundary; do not alter the accepted "
                            "record in place."
                        ),
                    }
                )
                continue
            key = str(item["profile_capability_id"])
            group = groups.setdefault(
                key,
                {
                    "capability": item["capability_name"],
                    "participant_summary": (
                        "Your reviewed evidence suggests a bounded pattern related to "
                        + item["capability_name"]
                        + "."
                    ),
                    "mapping_ids": [],
                    "confidence": float(item["confidence"]),
                    "inference_level": item["inference_level"],
                    "confidence_basis": item["confidence_basis"],
                    "scope_limits": [],
                    "negative_boundaries": [],
                },
            )
            group["mapping_ids"].append(item["mapping_id"])
            if float(item["confidence"]) > group["confidence"]:
                group["confidence"] = float(item["confidence"])
                group["inference_level"] = item["inference_level"]
                group["confidence_basis"] = item["confidence_basis"]
            for output_key, input_key in (
                ("scope_limits", "scope_limit"),
                ("negative_boundaries", "negative_boundary"),
            ):
                value = str(item[input_key])
                if value not in group[output_key]:
                    group[output_key].append(value)
        grouped = sorted(groups.values(), key=lambda item: item["capability"])
        report_ready = bool(grouped) and not quality_findings
        result = {
            "output_profile": OUTPUT_PROFILE,
            "participant_preview": {
                "title": "Working capability overview",
                "status": "ready_for_participant_review" if report_ready else "held_for_output_assurance",
                "interpretations": grouped,
                "quality_findings": quality_findings,
                "limits": (
                    "This preview groups accepted, bounded interpretations. "
                    "It is not a score, ranking, graph record, or published report."
                ),
            },
            "technical_companion": {
                "title": "Technical evidence companion",
                "interpretations": technical_interpretations,
                "purpose": "Retains every accepted mapping and its individual evidence boundary.",
            },
            "projection_manifest": {
                "projection_manifest_id": "transient-" + package_checksum[:16],
                "intake_session_id": session_id,
                "target_environment": "local_sandbox",
                "target_database": "PIA-Sandbox",
                "projection_mode": "dry_run",
                "contract_version": OUTPUT_PROFILE,
                "record_selection": "|".join(selection),
                "record_count": len(selection),
                "package_checksum": package_checksum,
                "assurance_status": "pass" if report_ready else "warning",
                "approval_status": "pending",
                "post_validation_status": "not_run",
                "graph_write": "not_performed",
            },
        }
        result["sandbox_projection_assurance"] = SandboxProjectionAssurance().build(result)
        return result
