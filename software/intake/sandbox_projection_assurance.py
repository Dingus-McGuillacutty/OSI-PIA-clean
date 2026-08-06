"""Offline assurance for a participant-minimized PIA sandbox projection.

artifact_id: component-pia-sandbox-projection-assurance-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

from typing import Any

from software.intake.sandbox_projection_preflight import (
    SANDBOX_DATABASE,
    SANDBOX_URI,
    preflight,
)


class SandboxProjectionAssurance:
    """Validate an exact dry-run package; this class has no graph client."""

    def build(self, preview: dict[str, Any]) -> dict[str, Any]:
        manifest = dict(preview["projection_manifest"])
        records = [
            {
                "mapping_id": item["mapping_id"],
                "evidence_id": item["evidence_id"],
                "capability_id": item.get("profile_capability_id", ""),
                "relationship_type": "SUPPORTS",
                "confidence": item["confidence"],
                "confidence_basis": item["confidence_basis"],
                "review_status": "accepted",
                "projection_scope": "participant_minimized",
            }
            for item in preview["technical_companion"]["interpretations"]
        ]
        selected = manifest["record_selection"].split("|")
        findings: list[str] = []
        if manifest["target_environment"] != "local_sandbox":
            findings.append("Target environment must be local_sandbox.")
        if manifest["target_database"] != "PIA-Sandbox":
            findings.append("Target database must be PIA-Sandbox.")
        if manifest["projection_mode"] != "dry_run":
            findings.append("Projection mode must remain dry_run.")
        if manifest["graph_write"] != "not_performed":
            findings.append("Graph write must remain not_performed.")
        if selected != [record["mapping_id"] for record in records]:
            findings.append("Manifest selection does not exactly match package records.")
        if len(records) != manifest["record_count"]:
            findings.append("Manifest count does not match package records.")
        for record in records:
            if record["relationship_type"] != "SUPPORTS" or not 0 <= float(record["confidence"]) <= 1:
                findings.append(f"Invalid mapping record {record['mapping_id']}.")
        target = None
        if not findings:
            target = preflight(manifest, uri=SANDBOX_URI, database=SANDBOX_DATABASE)
        return {"status": "pass" if not findings else "block", "findings": findings, "records": records, "manifest": manifest, "target_preflight": target, "graph_write": "not_performed"}
