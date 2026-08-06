"""Explicit synthetic-only PIA-Sandbox graph import runner.

artifact_id: component-pia-synthetic-sandbox-import-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import argparse
import getpass
import uuid
from datetime import UTC, datetime
from typing import Any

from software.intake.sandbox_projection_preflight import SANDBOX_DATABASE, SANDBOX_URI


SYNTHETIC_ROWS = [
    {"mapping_id": "PIA-SYN-MAP-001", "evidence_id": "PIA-SYN-EVD-001", "capability_id": "CAP-PIA-HANDOFF-MANAGEMENT", "confidence": 0.7, "confidence_basis": "Synthetic test evidence describes a bounded handoff activity."},
]


def validate_synthetic_rows(rows: list[dict[str, Any]]) -> list[str]:
    """Reject malformed or non-synthetic packages before authentication or I/O."""

    findings: list[str] = []
    if not rows:
        findings.append("Synthetic import package must contain at least one row.")
    for index, row in enumerate(rows, start=1):
        required = {
            "mapping_id",
            "evidence_id",
            "capability_id",
            "confidence",
            "confidence_basis",
        }
        missing = sorted(required - row.keys())
        if missing:
            findings.append(f"Row {index} is missing: {', '.join(missing)}.")
            continue
        if not str(row["mapping_id"]).startswith("PIA-SYN-MAP-"):
            findings.append(f"Row {index} mapping ID is not synthetic.")
        if not str(row["evidence_id"]).startswith("PIA-SYN-EVD-"):
            findings.append(f"Row {index} evidence ID is not synthetic.")
        if not str(row["capability_id"]).startswith("CAP-PIA-"):
            findings.append(f"Row {index} capability ID is outside the PIA namespace.")
        try:
            confidence = float(row["confidence"])
        except (TypeError, ValueError):
            findings.append(f"Row {index} confidence is not numeric.")
        else:
            if not 0.0 <= confidence <= 1.0:
                findings.append(f"Row {index} confidence must be between 0 and 1.")
        if not str(row["confidence_basis"]).strip():
            findings.append(f"Row {index} confidence basis is empty.")
    mapping_ids = [row.get("mapping_id") for row in rows]
    if len(mapping_ids) != len(set(mapping_ids)):
        findings.append("Synthetic package contains duplicate mapping IDs.")
    return findings


def _password_window() -> str:
    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
    try:
        value = simpledialog.askstring("PIA-Sandbox import", "Enter the local Neo4j password.", show="*", parent=root)
        if value is None:
            raise SystemExit("Sandbox import cancelled.")
        return value
    finally:
        root.destroy()

WRITE = """
UNWIND $rows AS row
MERGE (e:Evidence {evidence_id: row.evidence_id})
  ON CREATE SET e.synthetic = true, e.created_by = 'synthetic_sandbox_import'
MERGE (c:Capability {profile_capability_id: row.capability_id})
  ON CREATE SET c.capability_name = row.capability_id, c.synthetic = true
MERGE (e)-[r:SUPPORTS {mapping_id: row.mapping_id}]->(c)
SET r.confidence = row.confidence, r.confidence_basis = row.confidence_basis,
    r.review_status = 'accepted', r.synthetic = true, r.last_import_run = $run_id,
    r.imported_at = $imported_at
RETURN count(r) AS imported
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthetic-only PIA-Sandbox importer.")
    parser.add_argument("--apply-synthetic", action="store_true", help="Permit the synthetic sandbox write.")
    parser.add_argument(
        "--exercise-invalid-package",
        action="store_true",
        help="Prove a deliberately invalid package is blocked before authentication or graph I/O.",
    )
    parser.add_argument("--windowed-password", action="store_true", help="Use a local masked password window.")
    args = parser.parse_args()
    if args.apply_synthetic and args.exercise_invalid_package:
        parser.error("--apply-synthetic and --exercise-invalid-package cannot be combined.")
    rows = [dict(row) for row in SYNTHETIC_ROWS]
    if args.exercise_invalid_package:
        rows[0]["confidence"] = 1.2
        findings = validate_synthetic_rows(rows)
        blocked = bool(findings)
        print(
            {
                "status": "pass" if blocked else "fail",
                "control": "invalid_package_rejection",
                "findings": findings,
                "authentication": "not_attempted",
                "graph_write": "not_performed",
            }
        )
        return 0 if blocked else 1
    findings = validate_synthetic_rows(rows)
    if findings:
        print(
            {
                "status": "block",
                "findings": findings,
                "authentication": "not_attempted",
                "graph_write": "not_performed",
            }
        )
        return 1
    run_id = "PIA-SANDBOX-RUN-" + uuid.uuid4().hex[:12].upper()
    print({"run_id": run_id, "uri": SANDBOX_URI, "database": SANDBOX_DATABASE, "rows": len(rows), "mode": "apply_synthetic" if args.apply_synthetic else "dry_run"})
    if not args.apply_synthetic:
        return 0
    password = _password_window() if args.windowed_password else getpass.getpass("Local Neo4j password: ")
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise SystemExit("Install neo4j Python driver before an explicit sandbox import.") from exc
    with GraphDatabase.driver(SANDBOX_URI, auth=("neo4j", password)) as driver:
        driver.verify_connectivity(database=SANDBOX_DATABASE)
        with driver.session(database=SANDBOX_DATABASE) as session:
            result = session.run(WRITE, rows=rows, run_id=run_id, imported_at=datetime.now(UTC).isoformat())
            print({"run_id": run_id, "imported": result.single()["imported"], "graph_write": "performed_synthetic_only"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
