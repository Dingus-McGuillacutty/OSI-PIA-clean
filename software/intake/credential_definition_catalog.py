#!/usr/bin/env python3
"""Participant-free credential-definition catalog and Phase 3 resolver.

The catalog resolves public reference meaning. It never establishes that a
participant earned, retained, applied, or performed a credential.

artifact_id: component-pia-credential-definition-catalog-001
version: 0.2.0
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = (
    REPOSITORY_ROOT
    / "data"
    / "contracts"
    / "pia_credential_definition_catalog_contract_v0.2.json"
)
DEFAULT_CATALOG = (
    REPOSITORY_ROOT / "data" / "reference" / "pia-credential-library-v0.2"
)
PIPE = "|"
CURRENT_REVIEW_STATES = {"accepted", "accepted_with_limits"}
EXCLUDED_REVIEW_STATES = {"rejected", "superseded"}
UNRESOLVED_DEFINITION_STATES = {
    "title_only_unknown",
    "source_needed",
    "conflicting_definition",
    "obsolete_definition",
    "inaccessible_definition",
}
PROHIBITED_FIELD_FRAGMENT = re.compile(
    r"(?:participant|credential_holder|certificate_number|completion_date|"
    r"application_evidence|work_application|contact_email)",
    re.IGNORECASE,
)
RESTRICTED_VALUE_PATTERNS = (
    (
        "PARTICIPANT_LABEL",
        re.compile(r"\bparticipant[\s_-]*\d{1,6}\b", re.IGNORECASE),
    ),
    ("PIA_PARTICIPANT_ID", re.compile(r"\bPIA-\d{4,}\b", re.IGNORECASE)),
    (
        "LOCAL_PRIVATE_PATH",
        re.compile(r"(?:[A-Za-z]:\\Users\\|/home/[^/\s]+/)", re.IGNORECASE),
    ),
    (
        "EMAIL_ADDRESS",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    ),
)
SHA256_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
ACTOR_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._:-]{2,79}$", re.IGNORECASE)


@dataclass(frozen=True)
class CatalogFinding:
    severity: str
    code: str
    message: str
    filename: str = ""
    row_number: int | None = None
    field: str = ""
    record_id: str = ""


def _finding(
    severity: str,
    code: str,
    message: str,
    *,
    filename: str = "",
    row_number: int | None = None,
    field: str = "",
    record_id: str = "",
) -> CatalogFinding:
    return CatalogFinding(
        severity=severity,
        code=code,
        message=message,
        filename=filename,
        row_number=row_number,
        field=field,
        record_id=record_id,
    )


def _values(value: str) -> list[str]:
    return [item.strip() for item in value.split(PIPE) if item.strip()]


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", normalized))


def _valid_date(value: str) -> bool:
    if not value:
        return True
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _valid_datetime(value: str) -> bool:
    if not value:
        return True
    candidate = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _parse_date(value: str) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _date_in_range(
    effective_on: date,
    effective_from: str,
    effective_to: str,
) -> bool:
    lower = _parse_date(effective_from)
    upper = _parse_date(effective_to)
    if lower and effective_on < lower:
        return False
    if upper and effective_on > upper:
        return False
    return True


class CredentialDefinitionCatalog:
    """Loads, validates, and resolves a participant-free catalog package."""

    def __init__(
        self,
        catalog_root: Path | str = DEFAULT_CATALOG,
        contract_path: Path | str = DEFAULT_CONTRACT,
    ) -> None:
        self.catalog_root = Path(catalog_root).resolve()
        self.contract_path = Path(contract_path).resolve()
        self.contract = json.loads(self.contract_path.read_text(encoding="utf-8"))
        self.rows: dict[str, list[dict[str, str]]] = {}
        self.row_numbers: dict[str, dict[str, int]] = {}
        self.load_findings: list[CatalogFinding] = []
        self._load()

    def _load(self) -> None:
        expected_files = self.contract["required_files"]
        for filename in expected_files:
            file_contract = self.contract["files"][filename]
            path = self.catalog_root / filename
            if not path.is_file():
                self.rows[filename] = []
                self.row_numbers[filename] = {}
                self.load_findings.append(
                    _finding(
                        "error",
                        "REQUIRED_FILE_MISSING",
                        "Required catalog file is missing.",
                        filename=filename,
                    )
                )
                continue

            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                actual_headers = reader.fieldnames or []
                expected_headers = file_contract["headers"]
                if actual_headers != expected_headers:
                    self.load_findings.append(
                        _finding(
                            "error",
                            "HEADER_MISMATCH",
                            "Headers do not exactly match the catalog contract.",
                            filename=filename,
                        )
                    )
                loaded_rows = [
                    {str(key): (value or "").strip() for key, value in row.items()}
                    for row in reader
                ]
            self.rows[filename] = loaded_rows
            id_field = file_contract["id_field"]
            self.row_numbers[filename] = {
                row.get(id_field, ""): index
                for index, row in enumerate(loaded_rows, start=2)
                if row.get(id_field, "")
            }

    def _indexes(self) -> dict[str, dict[str, dict[str, str]]]:
        indexes: dict[str, dict[str, dict[str, str]]] = {}
        for filename, rows in self.rows.items():
            id_field = self.contract["files"][filename]["id_field"]
            indexes[filename] = {
                row.get(id_field, ""): row
                for row in rows
                if row.get(id_field, "")
            }
        return indexes

    def validate(self) -> dict[str, Any]:
        findings = list(self.load_findings)
        indexes = self._indexes()
        findings.extend(self._validate_scalar_fields())
        findings.extend(self._validate_privacy_boundary())
        findings.extend(self._validate_foreign_keys(indexes))
        findings.extend(self._validate_dynamic_review_targets(indexes))
        findings.extend(self._validate_sources(indexes))
        findings.extend(self._validate_definitions(indexes))
        findings.extend(self._validate_domains(indexes))
        findings.extend(self._validate_supersession())
        findings.extend(self._validate_resolution_boundaries())

        severity_counts = {
            severity: sum(1 for finding in findings if finding.severity == severity)
            for severity in ("error", "warning", "info")
        }
        return {
            "contract": self.contract["contract"]["artifact_id"],
            "contract_version": self.contract["contract"]["version"],
            "catalog_root": str(self.catalog_root),
            "valid": severity_counts["error"] == 0,
            "summary": {
                **severity_counts,
                "files_checked": len(self.contract["required_files"]),
                "records_checked": sum(len(rows) for rows in self.rows.values()),
            },
            "findings": [asdict(finding) for finding in findings],
        }

    def _validate_scalar_fields(self) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        for filename, file_contract in self.contract["files"].items():
            id_field = file_contract["id_field"]
            seen: set[str] = set()
            for row_number, row in enumerate(self.rows.get(filename, []), start=2):
                record_id = row.get(id_field, "")
                for field in file_contract.get("required", []):
                    if not row.get(field, ""):
                        findings.append(
                            _finding(
                                "error",
                                "REQUIRED_VALUE_MISSING",
                                "A required value is empty.",
                                filename=filename,
                                row_number=row_number,
                                field=field,
                                record_id=record_id,
                            )
                        )
                if record_id in seen:
                    findings.append(
                        _finding(
                            "error",
                            "DUPLICATE_ID",
                            "Record identity is duplicated.",
                            filename=filename,
                            row_number=row_number,
                            field=id_field,
                            record_id=record_id,
                        )
                    )
                seen.add(record_id)

                pattern = file_contract.get("id_pattern")
                if record_id and pattern and not re.fullmatch(pattern, record_id):
                    findings.append(
                        _finding(
                            "error",
                            "ID_PATTERN_INVALID",
                            "Record identity does not match the contract.",
                            filename=filename,
                            row_number=row_number,
                            field=id_field,
                            record_id=record_id,
                        )
                    )

                for field, allowed in file_contract.get("enums", {}).items():
                    value = row.get(field, "")
                    if value and value not in allowed:
                        findings.append(
                            _finding(
                                "error",
                                "ENUM_VALUE_INVALID",
                                f"Value is not permitted by the contract: {value!r}.",
                                filename=filename,
                                row_number=row_number,
                                field=field,
                                record_id=record_id,
                            )
                        )
                for field in file_contract.get("date_fields", []):
                    value = row.get(field, "")
                    if value and not _valid_date(value):
                        findings.append(
                            _finding(
                                "error",
                                "DATE_INVALID",
                                "Value must be an ISO 8601 date.",
                                filename=filename,
                                row_number=row_number,
                                field=field,
                                record_id=record_id,
                            )
                        )
                for field in file_contract.get("datetime_fields", []):
                    value = row.get(field, "")
                    if value and not _valid_datetime(value):
                        findings.append(
                            _finding(
                                "error",
                                "DATETIME_INVALID",
                                "Value must be an ISO 8601 datetime with timezone.",
                                filename=filename,
                                row_number=row_number,
                                field=field,
                                record_id=record_id,
                            )
                        )
                for field in (
                    "proposed_by_actor_id",
                    "reviewer_actor_id",
                ):
                    value = row.get(field, "")
                    if value and not ACTOR_ID_PATTERN.fullmatch(value):
                        findings.append(
                            _finding(
                                "error",
                                "ACTOR_ID_INVALID",
                                "Actor identity does not match the contract.",
                                filename=filename,
                                row_number=row_number,
                                field=field,
                                record_id=record_id,
                            )
                        )
        return findings

    def _validate_privacy_boundary(self) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        for filename, file_contract in self.contract["files"].items():
            id_field = file_contract["id_field"]
            for header in file_contract["headers"]:
                if PROHIBITED_FIELD_FRAGMENT.search(header):
                    findings.append(
                        _finding(
                            "error",
                            "PARTICIPANT_FIELD_PROHIBITED",
                            "The public catalog contract contains a participant-scoped field.",
                            filename=filename,
                            field=header,
                        )
                    )
            for row_number, row in enumerate(self.rows.get(filename, []), start=2):
                record_id = row.get(id_field, "")
                for field, value in row.items():
                    for code, pattern in RESTRICTED_VALUE_PATTERNS:
                        if value and pattern.search(value):
                            findings.append(
                                _finding(
                                    "error",
                                    f"RESTRICTED_VALUE_{code}",
                                    "Participant-scoped or private-looking content is prohibited.",
                                    filename=filename,
                                    row_number=row_number,
                                    field=field,
                                    record_id=record_id,
                                )
                            )
        return findings

    def _validate_foreign_keys(
        self,
        indexes: dict[str, dict[str, dict[str, str]]],
    ) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        for filename, file_contract in self.contract["files"].items():
            id_field = file_contract["id_field"]
            for row_number, row in enumerate(self.rows.get(filename, []), start=2):
                record_id = row.get(id_field, "")
                for foreign_key in file_contract.get("foreign_keys", []):
                    field = foreign_key["field"]
                    raw_value = row.get(field, "")
                    values = _values(raw_value) if foreign_key.get("multi") else [raw_value]
                    values = [value for value in values if value]
                    if foreign_key.get("required") and not values:
                        findings.append(
                            _finding(
                                "error",
                                "FOREIGN_KEY_REQUIRED",
                                "A required foreign-key value is empty.",
                                filename=filename,
                                row_number=row_number,
                                field=field,
                                record_id=record_id,
                            )
                        )
                    target = indexes.get(foreign_key["target_file"], {})
                    for value in values:
                        if value not in target:
                            findings.append(
                                _finding(
                                    "error",
                                    "FOREIGN_KEY_UNRESOLVED",
                                    f"Reference {value!r} does not resolve.",
                                    filename=filename,
                                    row_number=row_number,
                                    field=field,
                                    record_id=record_id,
                                )
                            )
        return findings

    def _validate_dynamic_review_targets(
        self,
        indexes: dict[str, dict[str, dict[str, str]]],
    ) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        type_to_file = {
            "credential_definition": "credential_definition.csv",
            "credential_definition_source": "credential_definition_source.csv",
            "credential_domain_element": "credential_domain_element.csv",
        }
        for row_number, review in enumerate(
            self.rows.get("credential_definition_review.csv", []), start=2
        ):
            target_type = review.get("target_record_type", "")
            target_id = review.get("target_record_id", "")
            target_file = type_to_file.get(target_type)
            target = (
                indexes.get(target_file, {}).get(target_id, {})
                if target_file
                else {}
            )
            if target_file and target_id not in indexes.get(target_file, {}):
                findings.append(
                    _finding(
                        "error",
                        "REVIEW_TARGET_UNRESOLVED",
                        "Definition review target does not resolve.",
                        filename="credential_definition_review.csv",
                        row_number=row_number,
                        field="target_record_id",
                        record_id=review.get("credential_definition_review_id", ""),
                    )
                )
            reviewer_actor_id = review.get("reviewer_actor_id", "")
            if reviewer_actor_id and not ACTOR_ID_PATTERN.fullmatch(
                reviewer_actor_id
            ):
                findings.append(
                    _finding(
                        "error",
                        "REVIEWER_ACTOR_ID_INVALID",
                        "Reviewer actor identity does not match the contract.",
                        filename="credential_definition_review.csv",
                        row_number=row_number,
                        field="reviewer_actor_id",
                        record_id=review.get(
                            "credential_definition_review_id", ""
                        ),
                    )
                )
            if (
                target
                and reviewer_actor_id
                and reviewer_actor_id == target.get("proposed_by_actor_id", "")
            ):
                findings.append(
                    _finding(
                        "error",
                        "SELF_REVIEW_PROHIBITED",
                        "A proposing actor cannot review its own record.",
                        filename="credential_definition_review.csv",
                        row_number=row_number,
                        field="reviewer_actor_id",
                        record_id=review.get(
                            "credential_definition_review_id", ""
                        ),
                    )
                )
            if (
                review.get("decision") == "accepted_with_limits"
                and not review.get("limitations")
            ):
                findings.append(
                    _finding(
                        "error",
                        "LIMITED_REVIEW_WITHOUT_LIMIT",
                        "An accepted-with-limits review must state its limits.",
                        filename="credential_definition_review.csv",
                        row_number=row_number,
                        field="limitations",
                        record_id=review.get("credential_definition_review_id", ""),
                    )
                )
            supersedes_id = review.get(
                "supersedes_credential_definition_review_id", ""
            )
            if supersedes_id:
                prior = indexes.get(
                    "credential_definition_review.csv", {}
                ).get(supersedes_id)
                if prior is None:
                    findings.append(
                        _finding(
                            "error",
                            "REVIEW_SUPERSESSION_UNRESOLVED",
                            "Superseded review identity does not resolve.",
                            filename="credential_definition_review.csv",
                            row_number=row_number,
                            field=(
                                "supersedes_credential_definition_review_id"
                            ),
                            record_id=review.get(
                                "credential_definition_review_id", ""
                            ),
                        )
                    )
                elif (
                    prior.get("target_record_type") != target_type
                    or prior.get("target_record_id") != target_id
                ):
                    findings.append(
                        _finding(
                            "error",
                            "REVIEW_SUPERSESSION_TARGET_MISMATCH",
                            "A review may supersede only a review of the same target.",
                            filename="credential_definition_review.csv",
                            row_number=row_number,
                            field=(
                                "supersedes_credential_definition_review_id"
                            ),
                            record_id=review.get(
                                "credential_definition_review_id", ""
                            ),
                        )
                    )
                elif prior.get("reviewed_at", "") > review.get(
                    "reviewed_at", ""
                ):
                    findings.append(
                        _finding(
                            "error",
                            "REVIEW_SUPERSESSION_TIME_INVALID",
                            "A review cannot supersede a later review.",
                            filename="credential_definition_review.csv",
                            row_number=row_number,
                            field="reviewed_at",
                            record_id=review.get(
                                "credential_definition_review_id", ""
                            ),
                        )
                    )
        return findings

    def _latest_review_by_target(self) -> dict[str, dict[str, str]]:
        latest: dict[str, dict[str, str]] = {}
        for review in self.rows.get("credential_definition_review.csv", []):
            target_id = review.get("target_record_id", "")
            if not target_id:
                continue
            previous = latest.get(target_id)
            if previous is None or review.get("reviewed_at", "") >= previous.get(
                "reviewed_at", ""
            ):
                latest[target_id] = review
        return latest

    def _validate_sources(
        self,
        indexes: dict[str, dict[str, dict[str, str]]],
    ) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        latest_reviews = self._latest_review_by_target()
        for row_number, source in enumerate(
            self.rows.get("credential_definition_source.csv", []), start=2
        ):
            record_id = source.get("credential_definition_source_id", "")
            for field in ("submitted_uri", "resolved_uri"):
                value = source.get(field, "")
                parsed = urlparse(value)
                if value and (parsed.scheme != "https" or not parsed.netloc):
                    findings.append(
                        _finding(
                            "error",
                            "PUBLIC_SOURCE_URI_INVALID",
                            "Public catalog source URIs must use HTTPS.",
                            filename="credential_definition_source.csv",
                            row_number=row_number,
                            field=field,
                            record_id=record_id,
                        )
                    )
            if source.get("access_status") == "accessible":
                if not SHA256_PATTERN.fullmatch(
                    source.get("content_checksum", "")
                ):
                    findings.append(
                        _finding(
                            "error",
                            "SOURCE_CHECKSUM_INVALID",
                            "Accessible source must have a sha256: content fingerprint.",
                            filename="credential_definition_source.csv",
                            row_number=row_number,
                            field="content_checksum",
                            record_id=record_id,
                        )
                    )
                try:
                    size = int(source.get("content_size_bytes", ""))
                    if size <= 0:
                        raise ValueError
                except ValueError:
                    findings.append(
                        _finding(
                            "error",
                            "SOURCE_SIZE_INVALID",
                            "Accessible source content size must be a positive integer.",
                            filename="credential_definition_source.csv",
                            row_number=row_number,
                            field="content_size_bytes",
                            record_id=record_id,
                        )
                    )

            definition_id = source.get("credential_definition_id", "")
            definition = indexes.get("credential_definition.csv", {}).get(
                definition_id, {}
            )
            declared_sources = set(
                _values(definition.get("primary_source_ids", ""))
                + _values(definition.get("secondary_source_ids", ""))
            )
            if definition and record_id not in declared_sources:
                findings.append(
                    _finding(
                        "warning",
                        "SOURCE_NOT_DECLARED_BY_DEFINITION",
                        "Source points to a definition that does not list it.",
                        filename="credential_definition_source.csv",
                        row_number=row_number,
                        field="credential_definition_id",
                        record_id=record_id,
                    )
                )
            review_status = source.get("review_status", "")
            if review_status in CURRENT_REVIEW_STATES:
                latest_review = latest_reviews.get(record_id, {})
                if latest_review.get("decision") != review_status:
                    findings.append(
                        _finding(
                            "error",
                            "ACCEPTED_SOURCE_REVIEW_MISSING",
                            "Accepted source requires a matching current review record.",
                            filename="credential_definition_source.csv",
                            row_number=row_number,
                            field="review_status",
                            record_id=record_id,
                        )
                    )
        return findings

    def _review_decisions_by_target(self) -> dict[str, set[str]]:
        decisions: dict[str, set[str]] = defaultdict(set)
        for review in self.rows.get("credential_definition_review.csv", []):
            decisions[review.get("target_record_id", "")].add(
                review.get("decision", "")
            )
        return decisions

    def _validate_definitions(
        self,
        indexes: dict[str, dict[str, dict[str, str]]],
    ) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        latest_reviews = self._latest_review_by_target()
        sources = indexes.get("credential_definition_source.csv", {})
        families = indexes.get("credential_family.csv", {})
        for row_number, definition in enumerate(
            self.rows.get("credential_definition.csv", []), start=2
        ):
            record_id = definition.get("credential_definition_id", "")
            family = families.get(definition.get("credential_family_id", ""), {})
            if (
                family
                and family.get("credential_issuer_id")
                != definition.get("credential_issuer_id")
            ):
                findings.append(
                    _finding(
                        "error",
                        "DEFINITION_ISSUER_FAMILY_MISMATCH",
                        "Definition issuer does not match its credential family.",
                        filename="credential_definition.csv",
                        row_number=row_number,
                        field="credential_issuer_id",
                        record_id=record_id,
                    )
                )

            effective_from = definition.get("effective_from", "")
            effective_to = definition.get("effective_to", "")
            if (
                _valid_date(effective_from)
                and _valid_date(effective_to)
                and effective_from
                and effective_to
                and _parse_date(effective_to) < _parse_date(effective_from)
            ):
                findings.append(
                    _finding(
                        "error",
                        "EFFECTIVE_RANGE_INVALID",
                        "Definition effective_to precedes effective_from.",
                        filename="credential_definition.csv",
                        row_number=row_number,
                        field="effective_to",
                        record_id=record_id,
                    )
                )

            expansion_required = (
                definition.get("definition_expansion_required") == "true"
            )
            if (
                definition.get("definition_status")
                in UNRESOLVED_DEFINITION_STATES
                and (not expansion_required or not definition.get("next_action"))
            ):
                findings.append(
                    _finding(
                        "error",
                        "UNRESOLVED_DEFINITION_WITHOUT_ACTION",
                        "Unresolved definition requires expansion and a next action.",
                        filename="credential_definition.csv",
                        row_number=row_number,
                        field="next_action",
                        record_id=record_id,
                    )
                )

            review_status = definition.get("review_status", "")
            if review_status in CURRENT_REVIEW_STATES:
                if not definition.get("last_reviewed") or not definition.get(
                    "review_cycle"
                ):
                    findings.append(
                        _finding(
                            "error",
                            "ACCEPTED_DEFINITION_REVIEW_METADATA_MISSING",
                            "Accepted definition requires review date and cycle.",
                            filename="credential_definition.csv",
                            row_number=row_number,
                            field="last_reviewed",
                            record_id=record_id,
                        )
                    )
                if (
                    latest_reviews.get(record_id, {}).get("decision")
                    != review_status
                ):
                    findings.append(
                        _finding(
                            "error",
                            "ACCEPTED_DEFINITION_REVIEW_MISSING",
                            "Accepted definition requires a matching review record.",
                            filename="credential_definition.csv",
                            row_number=row_number,
                            field="review_status",
                            record_id=record_id,
                        )
                    )
                if not definition.get("domain_summary") or not definition.get(
                    "negative_boundary"
                ):
                    findings.append(
                        _finding(
                            "error",
                            "ACCEPTED_DEFINITION_BOUNDARY_MISSING",
                            "Accepted definition requires domain and negative boundaries.",
                            filename="credential_definition.csv",
                            row_number=row_number,
                            record_id=record_id,
                        )
                    )

            primary_sources = [
                sources[source_id]
                for source_id in _values(definition.get("primary_source_ids", ""))
                if source_id in sources
            ]
            if definition.get("definition_status") == "issuer_verified":
                issuer_sources = [
                    source
                    for source in primary_sources
                    if source.get("source_authority") == "issuer_primary"
                    and source.get("review_status") in CURRENT_REVIEW_STATES
                    and source.get("access_status") == "accessible"
                ]
                if (
                    not issuer_sources
                    or review_status not in CURRENT_REVIEW_STATES
                    or expansion_required
                ):
                    findings.append(
                        _finding(
                            "error",
                            "ISSUER_VERIFIED_BOUNDARY_INVALID",
                            "Issuer-verified requires accepted issuer-primary support, accepted review, and no expansion requirement.",
                            filename="credential_definition.csv",
                            row_number=row_number,
                            field="definition_status",
                            record_id=record_id,
                        )
                    )

            if (
                definition.get("source_conflict_status") in {"material", "unresolved"}
                and definition.get("definition_status") != "conflicting_definition"
            ):
                findings.append(
                    _finding(
                        "error",
                        "MATERIAL_CONFLICT_STATUS_MISMATCH",
                        "Material or unresolved source conflict must remain conflicting_definition.",
                        filename="credential_definition.csv",
                        row_number=row_number,
                        field="definition_status",
                        record_id=record_id,
                    )
                )
        return findings

    def _validate_domains(
        self,
        indexes: dict[str, dict[str, dict[str, str]]],
    ) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        weights: dict[str, list[float]] = defaultdict(list)
        sources = indexes.get("credential_definition_source.csv", {})
        latest_reviews = self._latest_review_by_target()
        for row_number, element in enumerate(
            self.rows.get("credential_domain_element.csv", []), start=2
        ):
            record_id = element.get("credential_domain_element_id", "")
            weight = element.get("weight_percent", "")
            if weight:
                try:
                    parsed_weight = float(weight)
                    if not 0 <= parsed_weight <= 100:
                        raise ValueError
                    weights[element.get("credential_definition_id", "")].append(
                        parsed_weight
                    )
                except ValueError:
                    findings.append(
                        _finding(
                            "error",
                            "DOMAIN_WEIGHT_INVALID",
                            "Domain weight must be between 0 and 100.",
                            filename="credential_domain_element.csv",
                            row_number=row_number,
                            field="weight_percent",
                            record_id=record_id,
                        )
                    )
            for source_id in _values(element.get("source_ids", "")):
                source = sources.get(source_id, {})
                if source and source.get("credential_definition_id") != element.get(
                    "credential_definition_id"
                ):
                    findings.append(
                        _finding(
                            "error",
                            "DOMAIN_SOURCE_DEFINITION_MISMATCH",
                            "Domain element source belongs to another definition.",
                            filename="credential_domain_element.csv",
                            row_number=row_number,
                            field="source_ids",
                            record_id=record_id,
                        )
                    )
            review_status = element.get("review_status", "")
            if review_status in CURRENT_REVIEW_STATES:
                latest_review = latest_reviews.get(record_id, {})
                if latest_review.get("decision") != review_status:
                    findings.append(
                        _finding(
                            "error",
                            "ACCEPTED_DOMAIN_REVIEW_MISSING",
                            "Accepted domain element requires a matching current review record.",
                            filename="credential_domain_element.csv",
                            row_number=row_number,
                            field="review_status",
                            record_id=record_id,
                        )
                    )
        for definition_id, definition_weights in weights.items():
            if definition_weights and abs(sum(definition_weights) - 100.0) > 0.01:
                findings.append(
                    _finding(
                        "warning",
                        "DOMAIN_WEIGHTS_NOT_100",
                        "Weighted domain elements do not total 100 percent.",
                        filename="credential_domain_element.csv",
                        field="weight_percent",
                        record_id=definition_id,
                    )
                )
        return findings

    def _validate_supersession(self) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        for filename, file_contract in self.contract["files"].items():
            supersedes_field = file_contract.get("supersedes_field")
            if not supersedes_field:
                continue
            id_field = file_contract["id_field"]
            parent_by_id = {
                row.get(id_field, ""): row.get(supersedes_field, "")
                for row in self.rows.get(filename, [])
                if row.get(id_field, "")
            }
            for record_id in parent_by_id:
                visited: set[str] = set()
                cursor = record_id
                while cursor:
                    if cursor in visited:
                        findings.append(
                            _finding(
                                "error",
                                "SUPERSESSION_CYCLE",
                                "Supersession chain contains a cycle.",
                                filename=filename,
                                field=supersedes_field,
                                record_id=record_id,
                            )
                        )
                        break
                    visited.add(cursor)
                    cursor = parent_by_id.get(cursor, "")
        return findings

    def _validate_resolution_boundaries(self) -> list[CatalogFinding]:
        findings: list[CatalogFinding] = []
        accepted_by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
        for definition in self.rows.get("credential_definition.csv", []):
            if (
                definition.get("review_status") in CURRENT_REVIEW_STATES
                and definition.get("lifecycle_status") == "active"
            ):
                accepted_by_family[
                    definition.get("credential_family_id", "")
                ].append(definition)
        for family_id, definitions in accepted_by_family.items():
            if len(definitions) > 1 and any(
                not definition.get("effective_from")
                for definition in definitions
            ):
                findings.append(
                    _finding(
                        "error",
                        "ACTIVE_DEFINITION_OVERLAP_UNBOUNDED",
                        "Multiple accepted active definitions lack resolvable effective boundaries.",
                        filename="credential_definition.csv",
                        field="effective_from",
                        record_id=family_id,
                    )
                )
        return findings

    def _issuer_alias_index(self) -> dict[str, set[str]]:
        aliases: dict[str, set[str]] = {}
        for issuer in self.rows.get("credential_issuer.csv", []):
            issuer_id = issuer.get("credential_issuer_id", "")
            values = [
                issuer.get("canonical_name", ""),
                *_values(issuer.get("aliases", "")),
            ]
            aliases[issuer_id] = {_normalize(value) for value in values if value}
        return aliases

    def _family_alias_index(self) -> dict[str, set[str]]:
        aliases: dict[str, set[str]] = {}
        for family in self.rows.get("credential_family.csv", []):
            family_id = family.get("credential_family_id", "")
            values = [
                family.get("canonical_title", ""),
                family.get("acronym", ""),
                *_values(family.get("aliases", "")),
            ]
            aliases[family_id] = {_normalize(value) for value in values if value}
        return aliases

    def resolve(
        self,
        title: str,
        *,
        issuer_hint: str = "",
        version_hint: str = "",
        effective_on: str = "",
    ) -> dict[str, Any]:
        """Resolve public reference meaning without participant interpretation."""

        if not title.strip():
            raise ValueError("A credential title is required.")
        if effective_on and not _valid_date(effective_on):
            raise ValueError("effective_on must be an ISO 8601 date.")

        family_aliases = self._family_alias_index()
        normalized_title = _normalize(title)
        family_ids = {
            family_id
            for family_id, aliases in family_aliases.items()
            if normalized_title in aliases
        }
        families_by_id = {
            row["credential_family_id"]: row
            for row in self.rows.get("credential_family.csv", [])
        }

        if issuer_hint and family_ids:
            issuer_aliases = self._issuer_alias_index()
            normalized_issuer = _normalize(issuer_hint)
            family_ids = {
                family_id
                for family_id in family_ids
                if normalized_issuer
                in issuer_aliases.get(
                    families_by_id[family_id].get("credential_issuer_id", ""), set()
                )
            }

        if not family_ids:
            return self._resolution_result(
                title=title,
                issuer_hint=issuer_hint,
                version_hint=version_hint,
                status="source_needed",
                knowledge_status="source_needed",
                family_ids=[],
                definitions=[],
                next_action=(
                    "Capture an issuer-primary definition, version, and assessed domain."
                ),
            )

        definitions = [
            row
            for row in self.rows.get("credential_definition.csv", [])
            if row.get("credential_family_id") in family_ids
            and row.get("review_status") not in EXCLUDED_REVIEW_STATES
            and row.get("lifecycle_status") not in {"superseded", "retired"}
        ]
        if version_hint:
            normalized_version = _normalize(version_hint)
            definitions = [
                row
                for row in definitions
                if _normalize(row.get("version_label", "")) == normalized_version
            ]
        if effective_on:
            effective_date = _parse_date(effective_on)
            definitions = [
                row
                for row in definitions
                if _date_in_range(
                    effective_date,
                    row.get("effective_from", ""),
                    row.get("effective_to", ""),
                )
            ]

        if not definitions:
            return self._resolution_result(
                title=title,
                issuer_hint=issuer_hint,
                version_hint=version_hint,
                status="version_unknown",
                knowledge_status="source_needed",
                family_ids=sorted(family_ids),
                definitions=[],
                next_action=(
                    "Confirm the credential version or completion-period definition."
                ),
            )

        if any(
            row.get("definition_status") == "conflicting_definition"
            for row in definitions
        ):
            return self._resolution_result(
                title=title,
                issuer_hint=issuer_hint,
                version_hint=version_hint,
                status="conflicting_definition",
                knowledge_status="conflicting_definition",
                family_ids=sorted(family_ids),
                definitions=definitions,
                next_action="Resolve the material source or version conflict.",
            )

        accepted = [
            row
            for row in definitions
            if row.get("review_status") in CURRENT_REVIEW_STATES
            and row.get("definition_status") == "issuer_verified"
        ]
        if len(family_ids) > 1:
            return self._resolution_result(
                title=title,
                issuer_hint=issuer_hint,
                version_hint=version_hint,
                status="ambiguous_title",
                knowledge_status="source_needed",
                family_ids=sorted(family_ids),
                definitions=definitions,
                next_action="Confirm issuer and applicable version before reuse.",
            )
        if len(accepted) == 1:
            return self._resolution_result(
                title=title,
                issuer_hint=issuer_hint,
                version_hint=version_hint,
                status="resolved",
                knowledge_status="issuer_verified",
                family_ids=sorted(family_ids),
                definitions=accepted,
                next_action=(
                    "Reference this definition for credential meaning; assess participant "
                    "completion and application separately."
                ),
            )
        if len(accepted) > 1:
            return self._resolution_result(
                title=title,
                issuer_hint=issuer_hint,
                version_hint=version_hint,
                status="ambiguous_title",
                knowledge_status="source_needed",
                family_ids=sorted(family_ids),
                definitions=definitions,
                next_action="Confirm issuer and applicable version before reuse.",
            )

        if any(
            row.get("definition_status") == "inaccessible_definition"
            for row in definitions
        ):
            status = "inaccessible_definition"
            knowledge_status = "inaccessible_definition"
            next_action = "Locate an accessible issuer or approved archived source."
        else:
            status = "definition_found_pending_review"
            knowledge_status = definitions[0].get(
                "definition_status", "source_defined"
            )
            next_action = "Complete independent definition review before reuse."
        return self._resolution_result(
            title=title,
            issuer_hint=issuer_hint,
            version_hint=version_hint,
            status=status,
            knowledge_status=knowledge_status,
            family_ids=sorted(family_ids),
            definitions=definitions,
            next_action=next_action,
        )

    def _resolution_result(
        self,
        *,
        title: str,
        issuer_hint: str,
        version_hint: str,
        status: str,
        knowledge_status: str,
        family_ids: Iterable[str],
        definitions: Iterable[dict[str, str]],
        next_action: str,
    ) -> dict[str, Any]:
        definitions = list(definitions)
        definition_ids = sorted(
            row.get("credential_definition_id", "")
            for row in definitions
            if row.get("credential_definition_id")
        )
        negative_boundaries = sorted(
            {
                row.get("negative_boundary", "")
                for row in definitions
                if row.get("negative_boundary")
            }
        )
        queue_reason = {
            "source_needed": "source_needed",
            "version_unknown": "version_unknown",
            "ambiguous_title": "ambiguous_title",
            "definition_found_pending_review": "definition_pending_review",
            "inaccessible_definition": "inaccessible_definition",
            "conflicting_definition": "conflicting_definition",
        }.get(status)
        result: dict[str, Any] = {
            "resolution_status": status,
            "knowledge_status": knowledge_status,
            "credential_title": title,
            "issuer_hint": issuer_hint,
            "version_hint": version_hint,
            "candidate_credential_family_ids": list(family_ids),
            "candidate_credential_definition_ids": definition_ids,
            "credential_definition_id": (
                definition_ids[0] if status == "resolved" and definition_ids else ""
            ),
            "negative_boundaries": negative_boundaries,
            "next_action": next_action,
            "participant_claims_established": [],
            "boundary": (
                "Reference resolution does not establish participant completion, "
                "current standing, application, proficiency, or performance."
            ),
        }
        if queue_reason:
            result["expansion_queue_proposal"] = self.propose_expansion_item(
                title=title,
                issuer_hint=issuer_hint,
                version_hint=version_hint,
                family_ids=result["candidate_credential_family_ids"],
                definition_ids=definition_ids,
                reason_code=queue_reason,
                next_action=next_action,
            )
        return result

    @staticmethod
    def propose_expansion_item(
        *,
        title: str,
        issuer_hint: str,
        version_hint: str,
        family_ids: Iterable[str],
        definition_ids: Iterable[str],
        reason_code: str,
        next_action: str,
    ) -> dict[str, str]:
        """Create a participant-free queue proposal without persisting it."""

        now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        )
        fingerprint = hashlib.sha256(
            "\x00".join(
                [title, issuer_hint, version_hint, reason_code]
            ).encode("utf-8")
        ).hexdigest()[:12].upper()
        return {
            "definition_expansion_item_id": (
                f"CRED-EXP-RESOLUTION-{fingerprint}-001"
            ),
            "credential_title": title,
            "issuer_hint": issuer_hint,
            "version_hint": version_hint,
            "candidate_credential_family_ids": PIPE.join(sorted(family_ids)),
            "candidate_credential_definition_ids": PIPE.join(
                sorted(definition_ids)
            ),
            "reason_code": reason_code,
            "processing_state": "received",
            "priority": "normal",
            "next_action": next_action,
            "created_at": now,
            "updated_at": now,
            "supersedes_definition_expansion_item_id": "",
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate or query the participant-free PIA credential definition catalog."
        )
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT,
        help="Machine-readable catalog contract.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument(
        "catalog_root", type=Path, nargs="?", default=DEFAULT_CATALOG
    )

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument(
        "catalog_root", type=Path, nargs="?", default=DEFAULT_CATALOG
    )
    resolve_parser.add_argument("--title", required=True)
    resolve_parser.add_argument("--issuer", default="")
    resolve_parser.add_argument("--version", default="")
    resolve_parser.add_argument("--effective-on", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    catalog = CredentialDefinitionCatalog(args.catalog_root, args.contract)
    if args.command == "validate":
        result = catalog.validate()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["valid"] else 1

    validation = catalog.validate()
    if not validation["valid"]:
        print(json.dumps(validation, indent=2, ensure_ascii=False))
        return 1
    try:
        result = catalog.resolve(
            args.title,
            issuer_hint=args.issuer,
            version_hint=args.version,
            effective_on=args.effective_on,
        )
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
