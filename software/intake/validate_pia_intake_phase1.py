#!/usr/bin/env python3
"""Validate a PIA Intake Phase 1 package.

Standard-library only. The validator enforces the machine-readable record
contract, participant-free repository-fixture rules, record relationships,
state boundaries, supersession safety, and projection gates.

artifact_id: component-pia-intake-phase1-validator-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = (
    REPOSITORY_ROOT
    / "data"
    / "contracts"
    / "pia_intake_phase1_contract_v0.1.json"
)
DEFAULT_FIXTURE = (
    REPOSITORY_ROOT
    / "data"
    / "fixtures"
    / "pia-intake-phase1-synthetic"
)
PIPE = "|"
SECRET_PATTERN = re.compile(
    r"(?i)(?:password|passwd|secret|access[_-]?token|api[_-]?key)\s*="
)


def _finding(
    findings: list[dict[str, str]],
    severity: str,
    code: str,
    message: str,
    file_name: str = "",
    record_id: str = "",
    field: str = "",
) -> None:
    findings.append(
        {
            "severity": severity,
            "code": code,
            "message": message,
            "file": file_name,
            "record_id": record_id,
            "field": field,
        }
    )


def _values(value: str) -> list[str]:
    return [item.strip() for item in value.split(PIPE) if item.strip()]


def _read_csv(
    path: Path,
    expected_headers: list[str],
    findings: list[dict[str, str]],
) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            actual_headers = reader.fieldnames or []
            if actual_headers != expected_headers:
                _finding(
                    findings,
                    "error",
                    "HEADERS_MISMATCH",
                    "Headers must exactly match the contract, including order.",
                    path.name,
                )
                return []
            rows = []
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    _finding(
                        findings,
                        "error",
                        "EXTRA_CSV_FIELD",
                        f"Row {line_number} contains more values than headers.",
                        path.name,
                    )
                    continue
                rows.append({key: (value or "").strip() for key, value in row.items()})
            return rows
    except (OSError, UnicodeError, csv.Error) as exc:
        _finding(
            findings,
            "error",
            "CSV_READ_FAILED",
            str(exc),
            path.name,
        )
        return []


def _valid_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _valid_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return "T" in value
    except ValueError:
        return False


def _validate_scalar_fields(
    file_name: str,
    spec: dict[str, Any],
    rows: list[dict[str, str]],
    findings: list[dict[str, str]],
) -> None:
    primary_field = spec["id_field"]
    primary_pattern = re.compile(spec["id_pattern"])
    field_patterns = {
        field: re.compile(pattern)
        for field, pattern in spec.get("field_patterns", {}).items()
    }
    seen: set[str] = set()

    for row_number, row in enumerate(rows, start=2):
        record_id = row.get(primary_field, "") or f"row-{row_number}"

        for field in spec.get("required", []):
            if not row.get(field, ""):
                _finding(
                    findings,
                    "error",
                    "REQUIRED_VALUE_MISSING",
                    f"Required field {field!r} is empty.",
                    file_name,
                    record_id,
                    field,
                )

        primary_value = row.get(primary_field, "")
        if primary_value and not primary_pattern.fullmatch(primary_value):
            _finding(
                findings,
                "error",
                "PRIMARY_ID_INVALID",
                f"{primary_field!r} does not match its stable-ID pattern.",
                file_name,
                record_id,
                primary_field,
            )
        if primary_value in seen:
            _finding(
                findings,
                "error",
                "PRIMARY_ID_DUPLICATE",
                f"Duplicate primary ID {primary_value!r}.",
                file_name,
                record_id,
                primary_field,
            )
        seen.add(primary_value)

        for field, pattern in field_patterns.items():
            value = row.get(field, "")
            if value and not pattern.fullmatch(value):
                _finding(
                    findings,
                    "error",
                    "FIELD_PATTERN_INVALID",
                    f"{field!r} does not match its contract pattern.",
                    file_name,
                    record_id,
                    field,
                )

        for field, choices in spec.get("enums", {}).items():
            value = row.get(field, "")
            if value not in choices:
                _finding(
                    findings,
                    "error",
                    "ENUM_VALUE_INVALID",
                    f"{field!r} must be one of: {', '.join(choices)}.",
                    file_name,
                    record_id,
                    field,
                )

        for field in spec.get("boolean_fields", []):
            value = row.get(field, "")
            if value and value not in {"true", "false"}:
                _finding(
                    findings,
                    "error",
                    "BOOLEAN_INVALID",
                    f"{field!r} must be true or false.",
                    file_name,
                    record_id,
                    field,
                )

        for field in spec.get("date_fields", []):
            value = row.get(field, "")
            if value and not _valid_date(value):
                _finding(
                    findings,
                    "error",
                    "DATE_INVALID",
                    f"{field!r} must be an ISO 8601 date.",
                    file_name,
                    record_id,
                    field,
                )

        for field in spec.get("datetime_fields", []):
            value = row.get(field, "")
            if value and not _valid_datetime(value):
                _finding(
                    findings,
                    "error",
                    "DATETIME_INVALID",
                    f"{field!r} must be an ISO 8601 datetime.",
                    file_name,
                    record_id,
                    field,
                )

        for field in spec.get("integer_fields", []):
            value = row.get(field, "")
            try:
                if value and int(value) < 0:
                    raise ValueError
            except ValueError:
                _finding(
                    findings,
                    "error",
                    "INTEGER_INVALID",
                    f"{field!r} must be a non-negative integer.",
                    file_name,
                    record_id,
                    field,
                )

        for field, bounds in spec.get("number_fields", {}).items():
            value = row.get(field, "")
            try:
                number = float(value)
                if number < bounds["minimum"] or number > bounds["maximum"]:
                    raise ValueError
            except ValueError:
                _finding(
                    findings,
                    "error",
                    "NUMBER_INVALID",
                    (
                        f"{field!r} must be between "
                        f"{bounds['minimum']} and {bounds['maximum']}."
                    ),
                    file_name,
                    record_id,
                    field,
                )

        for field, value in row.items():
            if value and SECRET_PATTERN.search(value):
                _finding(
                    findings,
                    "error",
                    "SECRET_LIKE_VALUE",
                    "Secret-like key/value material is prohibited in intake records.",
                    file_name,
                    record_id,
                    field,
                )


def _id_indexes(
    contract: dict[str, Any],
    package_rows: dict[str, list[dict[str, str]]],
) -> tuple[dict[str, set[str]], set[str]]:
    indexes: dict[str, set[str]] = {}
    all_ids: set[str] = set()
    for file_name, spec in contract["files"].items():
        id_field = spec["id_field"]
        ids = {
            row[id_field]
            for row in package_rows.get(file_name, [])
            if row.get(id_field, "")
        }
        indexes[file_name] = ids
        all_ids.update(ids)
    return indexes, all_ids


def _validate_foreign_keys(
    contract: dict[str, Any],
    package_rows: dict[str, list[dict[str, str]]],
    indexes: dict[str, set[str]],
    findings: list[dict[str, str]],
) -> None:
    for file_name, spec in contract["files"].items():
        id_field = spec["id_field"]
        for row in package_rows[file_name]:
            record_id = row[id_field]
            for foreign_key in spec.get("foreign_keys", []):
                field = foreign_key["field"]
                value = row.get(field, "")
                if not value:
                    if foreign_key.get("required", False):
                        _finding(
                            findings,
                            "error",
                            "FOREIGN_KEY_MISSING",
                            f"Required foreign key {field!r} is empty.",
                            file_name,
                            record_id,
                            field,
                        )
                    continue
                target_file = foreign_key["target_file"]
                if value not in indexes[target_file]:
                    _finding(
                        findings,
                        "error",
                        "FOREIGN_KEY_UNRESOLVED",
                        f"{field!r} does not resolve in {target_file}.",
                        file_name,
                        record_id,
                        field,
                    )


def _validate_supersession(
    contract: dict[str, Any],
    package_rows: dict[str, list[dict[str, str]]],
    findings: list[dict[str, str]],
) -> None:
    for file_name, spec in contract["files"].items():
        supersedes_field = spec.get("supersedes_field")
        if not supersedes_field:
            continue
        id_field = spec["id_field"]
        links = {
            row[id_field]: row.get(supersedes_field, "")
            for row in package_rows[file_name]
            if row.get(id_field, "")
        }
        for record_id, predecessor in links.items():
            if not predecessor:
                continue
            if predecessor == record_id:
                _finding(
                    findings,
                    "error",
                    "SUPERSESSION_SELF_REFERENCE",
                    "A record may not supersede itself.",
                    file_name,
                    record_id,
                    supersedes_field,
                )
            elif predecessor not in links:
                _finding(
                    findings,
                    "error",
                    "SUPERSESSION_TARGET_UNRESOLVED",
                    "The superseded record is not present in the package.",
                    file_name,
                    record_id,
                    supersedes_field,
                )

        for start in links:
            visited: set[str] = set()
            current = start
            while current and current in links:
                if current in visited:
                    _finding(
                        findings,
                        "error",
                        "SUPERSESSION_CYCLE",
                        "Supersession links contain a cycle.",
                        file_name,
                        start,
                        supersedes_field,
                    )
                    break
                visited.add(current)
                current = links[current]


def _validate_participant_scope(
    contract: dict[str, Any],
    package_rows: dict[str, list[dict[str, str]]],
    repository_fixture: bool,
    findings: list[dict[str, str]],
) -> None:
    session_participants = {
        row["intake_session_id"]: row["participant_id"]
        for row in package_rows["intake_session.csv"]
    }
    synthetic_pattern = re.compile(contract["shared"]["synthetic_participant_pattern"])

    for file_name, spec in contract["files"].items():
        if not spec.get("participant_scoped", False):
            continue
        for row in package_rows[file_name]:
            record_id = row[spec["id_field"]]
            participant_id = row.get("participant_id", "")
            session_id = row.get("intake_session_id", "")
            expected_participant = session_participants.get(session_id)
            if expected_participant and participant_id != expected_participant:
                _finding(
                    findings,
                    "error",
                    "PARTICIPANT_SESSION_MISMATCH",
                    "The participant ID differs from the intake session owner.",
                    file_name,
                    record_id,
                    "participant_id",
                )
            if participant_id and record_id.startswith("PIA-"):
                expected_prefix = f"{participant_id}-"
                if not record_id.startswith(expected_prefix):
                    _finding(
                        findings,
                        "error",
                        "PARTICIPANT_ID_PREFIX_MISMATCH",
                        "Participant-scoped primary IDs must share the participant prefix.",
                        file_name,
                        record_id,
                        spec["id_field"],
                    )
            if (
                repository_fixture
                and participant_id
                and not synthetic_pattern.fullmatch(participant_id)
            ):
                _finding(
                    findings,
                    "error",
                    "REPOSITORY_PARTICIPANT_DATA_PROHIBITED",
                    "Repository fixtures must use reserved synthetic participant IDs.",
                    file_name,
                    record_id,
                    "participant_id",
                )


def _require_source_ids(
    value: str,
    source_ids: set[str],
    findings: list[dict[str, str]],
    file_name: str,
    record_id: str,
    field: str,
) -> None:
    for source_id in _values(value):
        if source_id not in source_ids:
            _finding(
                findings,
                "error",
                "SOURCE_REFERENCE_UNRESOLVED",
                f"Source artifact {source_id!r} is not in this package.",
                file_name,
                record_id,
                field,
            )


def _validate_dynamic_targets(
    contract: dict[str, Any],
    package_rows: dict[str, list[dict[str, str]]],
    indexes: dict[str, set[str]],
    findings: list[dict[str, str]],
) -> None:
    target_files = contract["dynamic_target_files"]
    for file_name in ("review_event.csv", "intake_assurance_finding.csv"):
        id_field = contract["files"][file_name]["id_field"]
        for row in package_rows[file_name]:
            record_id = row[id_field]
            target_type = row["target_record_type"]
            target_file = target_files.get(target_type)
            if not target_file or row["target_record_id"] not in indexes[target_file]:
                _finding(
                    findings,
                    "error",
                    "DYNAMIC_TARGET_UNRESOLVED",
                    "The review or finding target does not resolve in this package.",
                    file_name,
                    record_id,
                    "target_record_id",
                )


def _validate_record_boundaries(
    contract: dict[str, Any],
    package_rows: dict[str, list[dict[str, str]]],
    indexes: dict[str, set[str]],
    all_ids: set[str],
    findings: list[dict[str, str]],
) -> None:
    source_ids = indexes["source_artifact.csv"]

    for row in package_rows["intake_session.csv"]:
        if row["consent_status"] == "withdrawn" and row["processing_state"] not in {
            "blocked",
            "closed",
        }:
            _finding(
                findings,
                "error",
                "WITHDRAWN_SESSION_NOT_STOPPED",
                "A withdrawn session must be blocked or closed.",
                "intake_session.csv",
                row["intake_session_id"],
                "processing_state",
            )

    for row in package_rows["source_artifact.csv"]:
        record_id = row["source_artifact_id"]
        kind = row["artifact_kind"]
        if kind == "upload" and (
            not row["original_filename"] or not row["media_type"]
        ):
            _finding(
                findings,
                "error",
                "UPLOAD_METADATA_MISSING",
                "Uploads require an original filename and media type.",
                "source_artifact.csv",
                record_id,
            )
        if kind == "external_link_snapshot" and not all(
            (
                row["submitted_uri"],
                row["resolved_uri"],
                row["retrieved_at"],
                row["content_checksum"],
            )
        ):
            _finding(
                findings,
                "error",
                "LINK_SNAPSHOT_INCOMPLETE",
                "External-link snapshots require both URIs, retrieval time, and content checksum.",
                "source_artifact.csv",
                record_id,
            )
        if kind == "extracted_content" and (
            not row["parent_artifact_id"]
            or row["extraction_method"] == "not_applicable"
            or row["extraction_status"] != "complete"
        ):
            _finding(
                findings,
                "error",
                "EXTRACTED_CONTENT_INCOMPLETE",
                "Extracted content requires a parent, method, and complete status.",
                "source_artifact.csv",
                record_id,
            )

    resolved_statuses = {"source_defined", "issuer_verified", "participant_defined"}
    unresolved_statuses = {
        "title_only_unknown",
        "source_needed",
        "conflicting_definition",
        "obsolete_definition",
        "inaccessible_definition",
    }
    for row in package_rows["credential_definition.csv"]:
        record_id = row["credential_definition_id"]
        status = row["definition_status"]
        _require_source_ids(
            row["primary_source_artifact_ids"],
            source_ids,
            findings,
            "credential_definition.csv",
            record_id,
            "primary_source_artifact_ids",
        )
        _require_source_ids(
            row["secondary_source_artifact_ids"],
            source_ids,
            findings,
            "credential_definition.csv",
            record_id,
            "secondary_source_artifact_ids",
        )
        if status in resolved_statuses and (
            not row["primary_source_artifact_ids"]
            or not row["domain_scope"]
            or not row["negative_boundary"]
            or row["definition_expansion_required"] != "false"
        ):
            _finding(
                findings,
                "error",
                "RESOLVED_DEFINITION_INCOMPLETE",
                "A resolved definition requires source, scope, boundary, and no expansion flag.",
                "credential_definition.csv",
                record_id,
            )
        if status in unresolved_statuses:
            if (
                row["definition_expansion_required"] != "true"
                or not row["next_action"]
            ):
                _finding(
                    findings,
                    "error",
                    "UNRESOLVED_DEFINITION_NOT_ROUTED",
                    "An unresolved definition must request expansion and name a next action.",
                    "credential_definition.csv",
                    record_id,
                )
            else:
                _finding(
                    findings,
                    "warning",
                    "DEFINITION_REVIEW_ROUTED",
                    "An unresolved definition remains safely routed for review.",
                    "credential_definition.csv",
                    record_id,
                    "definition_status",
                )
        if row["review_status"] in {"accepted", "accepted_with_limits"} and (
            not row["last_reviewed"] or not row["review_cycle"]
        ):
            _finding(
                findings,
                "error",
                "ACCEPTED_DEFINITION_REVIEW_METADATA_MISSING",
                "Accepted definitions require last-reviewed and review-cycle values.",
                "credential_definition.csv",
                record_id,
            )

    for row in package_rows["credential_application_assertion.csv"]:
        record_id = row["application_assertion_id"]
        _require_source_ids(
            row["supporting_source_artifact_ids"],
            source_ids,
            findings,
            "credential_application_assertion.csv",
            record_id,
            "supporting_source_artifact_ids",
        )
        if row["application_status"] in {
            "explicitly_attributed_in_source",
            "participant_reported_application",
        } and not row["experience_id"]:
            _finding(
                findings,
                "error",
                "APPLICATION_EXPERIENCE_MISSING",
                "Attributed application requires a participant experience ID.",
                "credential_application_assertion.csv",
                record_id,
                "experience_id",
            )
        if row["review_status"] in {"accepted", "accepted_with_limits"} and not row[
            "reviewed_at"
        ]:
            _finding(
                findings,
                "error",
                "APPLICATION_REVIEW_TIME_MISSING",
                "Accepted application assertions require a review time.",
                "credential_application_assertion.csv",
                record_id,
                "reviewed_at",
            )

    for file_name in ("review_event.csv",):
        for row in package_rows[file_name]:
            _require_source_ids(
                row["supporting_source_artifact_ids"],
                source_ids,
                findings,
                file_name,
                row["review_event_id"],
                "supporting_source_artifact_ids",
            )
            try:
                if int(row["target_record_version"]) < 1:
                    raise ValueError
            except ValueError:
                _finding(
                    findings,
                    "error",
                    "TARGET_VERSION_INVALID",
                    "Target record version must be a positive integer.",
                    file_name,
                    row["review_event_id"],
                    "target_record_version",
                )

    for row in package_rows["intake_assurance_finding.csv"]:
        if row["severity"] == "blocking" and not row["safe_next_action"]:
            _finding(
                findings,
                "error",
                "BLOCKING_FINDING_UNROUTED",
                "Blocking findings require a safe next action.",
                "intake_assurance_finding.csv",
                row["finding_id"],
                "safe_next_action",
            )

    for row in package_rows["projection_manifest.csv"]:
        record_id = row["projection_manifest_id"]
        selection = _values(row["record_selection"])
        unknown = [selected for selected in selection if selected not in all_ids]
        if unknown:
            _finding(
                findings,
                "error",
                "PROJECTION_SELECTION_UNRESOLVED",
                f"Projection selection contains unknown IDs: {', '.join(unknown)}.",
                "projection_manifest.csv",
                record_id,
                "record_selection",
            )
        if row["record_count"].isdigit() and int(row["record_count"]) != len(selection):
            _finding(
                findings,
                "error",
                "PROJECTION_COUNT_MISMATCH",
                "Projection record count does not match the enumerated selection.",
                "projection_manifest.csv",
                record_id,
                "record_count",
            )
        if row["projection_mode"] == "apply" and (
            row["assurance_status"] != "pass"
            or row["approval_status"] != "approved"
            or not row["approved_by"]
        ):
            _finding(
                findings,
                "error",
                "PROJECTION_APPLY_GATE_FAILED",
                "Apply mode requires passed assurance and explicit approval.",
                "projection_manifest.csv",
                record_id,
            )
        if row["applied_at"] and row["post_validation_status"] == "not_run":
            _finding(
                findings,
                "error",
                "POST_VALIDATION_NOT_RUN",
                "Applied projections require a post-validation result.",
                "projection_manifest.csv",
                record_id,
                "post_validation_status",
            )
        if row["participant_id"] and "reference" in row["target_database"].lower():
            _finding(
                findings,
                "error",
                "PARTICIPANT_REFERENCE_PROJECTION_PROHIBITED",
                "Participant-scoped records may not target a reference database.",
                "projection_manifest.csv",
                record_id,
                "target_database",
            )

    for row in package_rows["credential_definition_queue.csv"]:
        record_id = row["queue_item_id"]
        _require_source_ids(
            row["definition_source_artifact_ids"],
            source_ids,
            findings,
            "credential_definition_queue.csv",
            record_id,
            "definition_source_artifact_ids",
        )
        if row["processing_state"] == "blocked" and not row["blocked_reason"]:
            _finding(
                findings,
                "error",
                "BLOCKED_QUEUE_REASON_MISSING",
                "Blocked queue items require a reason.",
                "credential_definition_queue.csv",
                record_id,
                "blocked_reason",
            )
        if row["processing_state"] == "closed" and row["review_disposition"] == "pending":
            _finding(
                findings,
                "error",
                "QUEUE_CLOSED_WITH_PENDING_REVIEW",
                "A queue item cannot close while review remains pending.",
                "credential_definition_queue.csv",
                record_id,
            )
        if row["knowledge_status"] in unresolved_statuses and not row["next_action"]:
            _finding(
                findings,
                "error",
                "QUEUE_UNRESOLVED_WITHOUT_NEXT_ACTION",
                "An unresolved queue item requires a next action.",
                "credential_definition_queue.csv",
                record_id,
                "next_action",
            )


def validate_package(
    package: Path,
    contract_path: Path = DEFAULT_CONTRACT,
    *,
    repository_fixture: bool = False,
) -> dict[str, Any]:
    """Validate one package and return a deterministic JSON-ready result."""
    package = Path(package).resolve()
    contract_path = Path(contract_path).resolve()
    findings: list[dict[str, str]] = []

    try:
        contract_document = json.loads(contract_path.read_text(encoding="utf-8"))
        contract = contract_document
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "accepted": False,
            "contract_version": "",
            "package": str(package),
            "counts": {"files": 0, "records": 0, "errors": 1, "warnings": 0},
            "findings": [
                {
                    "severity": "error",
                    "code": "CONTRACT_READ_FAILED",
                    "message": str(exc),
                    "file": str(contract_path),
                    "record_id": "",
                    "field": "",
                }
            ],
        }

    package_rows: dict[str, list[dict[str, str]]] = {}
    for file_name in contract["required_files"]:
        path = package / file_name
        if not path.is_file():
            _finding(
                findings,
                "error",
                "REQUIRED_FILE_MISSING",
                "Required package file is missing.",
                file_name,
            )
            package_rows[file_name] = []
            continue
        spec = contract["files"][file_name]
        package_rows[file_name] = _read_csv(path, spec["headers"], findings)
        _validate_scalar_fields(file_name, spec, package_rows[file_name], findings)

    if not package_rows.get("intake_session.csv"):
        _finding(
            findings,
            "error",
            "INTAKE_SESSION_REQUIRED",
            "A package requires at least one intake session.",
            "intake_session.csv",
        )

    indexes, all_ids = _id_indexes(contract, package_rows)
    _validate_foreign_keys(contract, package_rows, indexes, findings)
    _validate_supersession(contract, package_rows, findings)
    _validate_participant_scope(
        contract,
        package_rows,
        repository_fixture,
        findings,
    )
    _validate_dynamic_targets(contract, package_rows, indexes, findings)
    _validate_record_boundaries(
        contract,
        package_rows,
        indexes,
        all_ids,
        findings,
    )

    errors = sum(item["severity"] == "error" for item in findings)
    warnings = sum(item["severity"] == "warning" for item in findings)
    record_count = sum(len(rows) for rows in package_rows.values())
    return {
        "accepted": errors == 0,
        "contract_version": contract["contract"]["version"],
        "package": str(package),
        "repository_fixture_mode": repository_fixture,
        "counts": {
            "files": len(package_rows),
            "records": record_count,
            "errors": errors,
            "warnings": warnings,
        },
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a PIA Intake Phase 1 record package."
    )
    parser.add_argument(
        "package",
        nargs="?",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="Directory containing the eight contracted CSV files.",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT,
        help="Machine-readable contract JSON.",
    )
    parser.add_argument(
        "--repository-fixture",
        action="store_true",
        help="Require reserved PIA-9000+ synthetic participant identifiers.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit compact JSON instead of formatted JSON.",
    )
    args = parser.parse_args(argv)
    result = validate_package(
        args.package,
        args.contract,
        repository_fixture=args.repository_fixture,
    )
    json.dump(
        result,
        sys.stdout,
        indent=None if args.json else 2,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
