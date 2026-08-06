"""Offline assurance for an exact synthetic OSI sandbox projection package."""

from __future__ import annotations

from typing import Any

from software.importer.osi_sandbox_projection_preflight import (
    SANDBOX_DATABASE,
    SANDBOX_URI,
    preflight,
)


def build_manifest(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Create the minimal declared package for an OSI synthetic-only import."""

    return {
        "target_environment": "local_sandbox",
        "target_database": SANDBOX_DATABASE,
        "projection_mode": "synthetic_only",
        "diagnostic_output": "not_authorized",
        "record_count": len(records),
        "record_selection": "|".join(record["observation_id"] for record in records),
        "graph_write": "not_performed",
    }


class OSISandboxProjectionAssurance:
    """Validate a synthetic-only projection package without a graph client."""

    def assure(self, records: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
        findings: list[str] = []
        expected = [record.get("observation_id", "") for record in records]
        if manifest.get("target_environment") != "local_sandbox":
            findings.append("Target environment must be local_sandbox.")
        if manifest.get("target_database") != SANDBOX_DATABASE:
            findings.append("Target database must be OSI-Sandbox.")
        if manifest.get("projection_mode") != "synthetic_only":
            findings.append("Projection mode must remain synthetic_only.")
        if manifest.get("diagnostic_output") != "not_authorized":
            findings.append("Diagnostic output must remain not_authorized.")
        if manifest.get("graph_write") != "not_performed":
            findings.append("Graph write must remain not_performed during assurance.")
        if manifest.get("record_selection", "").split("|") != expected:
            findings.append("Manifest selection does not exactly match package records.")
        if manifest.get("record_count") != len(records):
            findings.append("Manifest count does not match package records.")
        for index, record in enumerate(records, start=1):
            required = {
                "organization_id", "source_id", "evidence_id", "observation_id",
                "observation_text", "confidence", "confidence_basis", "negative_boundary",
                "review_status", "reviewed_by",
            }
            missing = sorted(key for key in required if not str(record.get(key, "")).strip())
            if missing:
                findings.append(f"Record {index} is missing: {', '.join(missing)}.")
                continue
            if not str(record["organization_id"]).startswith("OSI-SYN-ORG-"):
                findings.append(f"Record {index} organization ID is not synthetic.")
            if not str(record["source_id"]).startswith("OSI-SYN-SRC-"):
                findings.append(f"Record {index} source ID is not synthetic.")
            if not str(record["evidence_id"]).startswith("OSI-SYN-EVD-"):
                findings.append(f"Record {index} evidence ID is not synthetic.")
            if not str(record["observation_id"]).startswith("OSI-SYN-OBS-"):
                findings.append(f"Record {index} observation ID is not synthetic.")
            try:
                confidence = float(record["confidence"])
                if not 0.0 <= confidence <= 1.0:
                    raise ValueError
            except (TypeError, ValueError):
                findings.append(f"Record {index} confidence must be between 0 and 1.")
            if record.get("review_status") != "accepted":
                findings.append(f"Record {index} must be accepted before sandbox projection.")
        target = None
        if not findings:
            target = preflight(manifest, uri=SANDBOX_URI, database=SANDBOX_DATABASE)
        return {
            "status": "pass" if not findings else "block",
            "findings": findings,
            "records": records,
            "manifest": manifest,
            "target_preflight": target,
            "graph_write": "not_performed",
        }
