"""Explicit synthetic-only OSI-Sandbox graph import runner.

The importer embeds exactly one synthetic record. It never reads external or
organizational data and requires a deliberate local action before graph I/O.
"""

from __future__ import annotations

import argparse
import getpass
import uuid
from datetime import UTC, datetime
from typing import Any

from software.importer.osi_sandbox_projection_assurance import (
    OSISandboxProjectionAssurance,
    build_manifest,
)
from software.importer.osi_sandbox_projection_preflight import SANDBOX_DATABASE, SANDBOX_URI


SYNTHETIC_RECORDS = [{
    "organization_id": "OSI-SYN-ORG-001",
    "organization_name": "Synthetic Northstar Services",
    "source_id": "OSI-SYN-SRC-001",
    "evidence_id": "OSI-SYN-EVD-001",
    "observation_id": "OSI-SYN-OBS-001",
    "observation_text": "Synthetic service-transition record supports a bounded observation of cross-unit handoff coordination.",
    "confidence": 0.68,
    "confidence_basis": "One synthetic source-grounded record describes a documented cross-unit service-transition activity.",
    "negative_boundary": "Does not establish organizational performance, trust, health, causality, or a durable organizational trait.",
    "review_status": "accepted",
    "reviewed_by": "synthetic-reviewer",
}, {
    "organization_id": "OSI-SYN-ORG-001",
    "organization_name": "Synthetic Northstar Services",
    "source_id": "OSI-SYN-SRC-002",
    "evidence_id": "OSI-SYN-EVD-002",
    "observation_id": "OSI-SYN-OBS-002",
    "observation_text": "The reviewed record supports a bounded observation that decision routing was concentrated around one operational role during this transition.",
    "confidence": 0.58,
    "confidence_basis": "One reviewed synthetic source describes a concentrated routing condition.",
    "negative_boundary": "Does not establish harmful centralization, individual fault, or organizational performance.",
    "review_status": "accepted",
    "reviewed_by": "synthetic-reviewer",
}, {
    "organization_id": "OSI-SYN-ORG-001",
    "organization_name": "Synthetic Northstar Services",
    "source_id": "OSI-SYN-SRC-003",
    "evidence_id": "OSI-SYN-EVD-003",
    "observation_id": "OSI-SYN-OBS-003",
    "observation_text": "The reviewed record supports a bounded observation that delivery continuity coexisted with dependence on undocumented role knowledge.",
    "confidence": 0.62,
    "confidence_basis": "One reviewed synthetic source describes delivery continuity and undocumented knowledge dependence.",
    "negative_boundary": "Does not establish organizational health, future failure, or causal effect.",
    "review_status": "accepted",
    "reviewed_by": "synthetic-reviewer",
}]


def _password_window() -> str:
    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
    try:
        value = simpledialog.askstring("OSI-Sandbox import", "Enter the local Neo4j password.", show="*", parent=root)
        if value is None:
            raise SystemExit("Sandbox import cancelled.")
        return value
    finally:
        root.destroy()


WRITE = """
MERGE (run:OSIImportRun {run_id: $run_id})
SET run.synthetic = true, run.status = 'completed', run.record_count = size($records),
    run.imported_at = $imported_at, run.target_database = $target_database
WITH run
UNWIND $records AS record
MERGE (o:Organization {organization_id: record.organization_id})
  ON CREATE SET o.organization_name = record.organization_name, o.synthetic = true,
                o.created_by = 'osi_synthetic_sandbox_import'
MERGE (s:Source {source_id: record.source_id})
  ON CREATE SET s.synthetic = true
MERGE (e:Evidence {evidence_id: record.evidence_id})
  ON CREATE SET e.synthetic = true
MERGE (obs:ObservationCandidate {observation_id: record.observation_id})
  ON CREATE SET obs.synthetic = true
MERGE (o)-[:HAS_SOURCE {source_id: record.source_id}]->(s)
MERGE (s)-[:CONTAINS_EVIDENCE {evidence_id: record.evidence_id}]->(e)
MERGE (e)-[r:SUPPORTS_OBSERVATION {observation_id: record.observation_id}]->(obs)
SET r.observation_text = record.observation_text,
    r.confidence = record.confidence,
    r.confidence_basis = record.confidence_basis,
    r.negative_boundary = record.negative_boundary,
    r.review_status = record.review_status,
    r.reviewed_by = record.reviewed_by,
    r.synthetic = true,
    r.last_import_run = $run_id,
    r.imported_at = $imported_at
WITH run, count(r) AS imported
SET run.imported_count = imported
RETURN imported
"""

AUDIT_START = """
MERGE (run:OSIImportRun {run_id: $run_id})
SET run.synthetic = true, run.status = 'started', run.record_count = $record_count,
    run.started_at = $timestamp, run.target_database = $target_database
RETURN run.run_id AS run_id
"""

AUDIT_FAILURE = """
MERGE (run:OSIImportRun {run_id: $run_id})
SET run.synthetic = true, run.status = 'failed', run.failure_type = $failure_type,
    run.failure_message = $failure_message, run.failed_at = $timestamp,
    run.target_database = $target_database
RETURN run.run_id AS run_id
"""

ROLLBACK = """
MATCH (run:OSIImportRun {run_id: $run_id, synthetic: true})
MATCH ()-[r:SUPPORTS_OBSERVATION {last_import_run: $run_id}]->()
WITH run, collect(r) AS relationships
FOREACH (relationship IN relationships | DELETE relationship)
SET run.status = 'rolled_back', run.rolled_back_count = size(relationships),
    run.rolled_back_at = $timestamp
RETURN size(relationships) AS rolled_back
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthetic-only OSI-Sandbox importer.")
    parser.add_argument("--apply-synthetic", action="store_true", help="Permit the synthetic OSI sandbox write.")
    parser.add_argument("--exercise-invalid-package", action="store_true", help="Prove an invalid package is blocked before authentication or graph I/O.")
    parser.add_argument("--windowed-password", action="store_true", help="Use a local masked password window.")
    parser.add_argument("--rollback-run-id", help="Roll back the latest synthetic run's observation relationships.")
    args = parser.parse_args()
    if args.apply_synthetic and args.exercise_invalid_package or args.rollback_run_id and (args.apply_synthetic or args.exercise_invalid_package):
        parser.error("Choose one of --apply-synthetic, --exercise-invalid-package, or --rollback-run-id.")
    if args.rollback_run_id and not args.rollback_run_id.startswith("OSI-SANDBOX-RUN-"):
        parser.error("Rollback ID is not an OSI sandbox run identifier.")
    records = [dict(record) for record in SYNTHETIC_RECORDS]
    if args.exercise_invalid_package:
        records[0]["negative_boundary"] = ""
    manifest = build_manifest(records)
    assurance = OSISandboxProjectionAssurance().assure(records, manifest)
    if args.exercise_invalid_package:
        print({"status": "pass" if assurance["status"] == "block" else "fail", "control": "invalid_package_rejection", "findings": assurance["findings"], "authentication": "not_attempted", "graph_write": "not_performed"})
        return 0 if assurance["status"] == "block" else 1
    if args.rollback_run_id:
        password = _password_window() if args.windowed_password else getpass.getpass("Local Neo4j password: ")
        try:
            from neo4j import GraphDatabase
            with GraphDatabase.driver(SANDBOX_URI, auth=("neo4j", password)) as driver:
                with driver.session(database=SANDBOX_DATABASE) as session:
                    result = session.run(ROLLBACK, run_id=args.rollback_run_id, timestamp=datetime.now(UTC).isoformat()).single()
                    if result is None:
                        print({"status": "exception", "run_id": args.rollback_run_id, "reason": "audit_run_not_found_or_not_synthetic", "graph_write": "not_performed"})
                        return 1
                    print({"status": "rolled_back", "run_id": args.rollback_run_id, "relationships_removed": result["rolled_back"], "graph_write": "performed_synthetic_only"})
                    return 0
        except Exception as exc:
            print({"status": "exception", "run_id": args.rollback_run_id, "exception_type": type(exc).__name__, "message": str(exc), "graph_write": "not_confirmed"})
            return 1
    if assurance["status"] != "pass":
        print({"status": "block", "findings": assurance["findings"], "authentication": "not_attempted", "graph_write": "not_performed"})
        return 1
    run_id = "OSI-SANDBOX-RUN-" + uuid.uuid4().hex[:12].upper()
    print({"run_id": run_id, "uri": SANDBOX_URI, "database": SANDBOX_DATABASE, "rows": len(records), "mode": "apply_synthetic" if args.apply_synthetic else "dry_run"})
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
            timestamp = datetime.now(UTC).isoformat()
            session.run(AUDIT_START, run_id=run_id, record_count=len(records), timestamp=timestamp, target_database=SANDBOX_DATABASE).consume()
            try:
                result = session.run(WRITE, records=records, run_id=run_id, imported_at=timestamp, target_database=SANDBOX_DATABASE).single()
                print({"run_id": run_id, "imported": result["imported"], "audit_status": "completed", "graph_write": "performed_synthetic_only"})
            except Exception as exc:
                session.run(AUDIT_FAILURE, run_id=run_id, failure_type=type(exc).__name__, failure_message=str(exc), timestamp=datetime.now(UTC).isoformat(), target_database=SANDBOX_DATABASE).consume()
                print({"status": "exception", "run_id": run_id, "exception_type": type(exc).__name__, "message": str(exc), "audit_status": "failed", "graph_write": "not_confirmed"})
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
