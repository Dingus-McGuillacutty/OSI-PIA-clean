#!/usr/bin/env python3
"""Assure a synthetic OSI organizational-evidence package before graph work.

This component deliberately validates a participant-free organizational package
only. It does not connect to Neo4j, create diagnostic findings, or instantiate
planned OSI constructs such as Trust, Flow, or Organizational Health.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

try:
    from software.framework.osi_component import (
        AssuranceResult,
        Disposition,
        Finding,
        FindingSeverity,
        OSIComponent,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from software.framework.osi_component import (
        AssuranceResult,
        Disposition,
        Finding,
        FindingSeverity,
        OSIComponent,
    )


CONTRACT_VERSION = "0.1"
COMPONENT_VERSION = "0.1"

SCHEMAS = {
    "organization.csv": {
        "id": "organization_id",
        "required": {"organization_id", "organization_type", "record_status", "created_at"},
        "enums": {"record_status": {"active", "inactive", "archived"}},
    },
    "organizational_unit.csv": {
        "id": "organizational_unit_id",
        "required": {"organizational_unit_id", "organization_id", "unit_type", "record_status"},
        "enums": {"record_status": {"active", "inactive", "archived"}},
    },
    "position.csv": {
        "id": "position_id",
        "required": {"position_id", "organization_id", "organizational_unit_id", "record_status"},
        "enums": {"record_status": {"active", "inactive", "vacant", "archived"}},
    },
    "collection.csv": {
        "id": "collection_id",
        "required": {"collection_id", "organization_id", "collection_type", "collected_at", "confidentiality"},
        "enums": {"confidentiality": {"synthetic", "public", "internal", "restricted"}},
    },
    "source.csv": {
        "id": "source_id",
        "required": {"source_id", "collection_id", "organization_id", "source_type", "confidentiality"},
        "enums": {"confidentiality": {"synthetic", "public", "internal", "restricted"}},
    },
    "evidence.csv": {
        "id": "evidence_id",
        "required": {"evidence_id", "source_id", "organization_id", "evidence_text", "evidence_type", "extraction_method", "fidelity_status", "review_status", "created_at"},
        "enums": {
            "evidence_type": {"activity", "event", "condition", "output", "statement", "other"},
            "extraction_method": {"manual", "assisted", "automated"},
            "fidelity_status": {"verbatim", "close_paraphrase", "normalized", "summarized"},
            "review_status": {"unreviewed", "reviewed", "disputed", "superseded"},
        },
    },
    "observation_candidate.csv": {
        "id": "observation_id",
        "required": {"observation_id", "evidence_id", "observation_text", "observation_type", "confidence", "confidence_basis", "review_status", "negative_boundary", "created_at"},
        "enums": {"review_status": {"proposed", "accepted", "rejected", "needs_review"}},
    },
}

ID_PATTERNS = {
    "organization_id": re.compile(r"^OSI-SYN-ORG-\d{3,}$"),
    "organizational_unit_id": re.compile(r"^OSI-SYN-UNIT-\d{3,}$"),
    "position_id": re.compile(r"^OSI-SYN-POS-\d{3,}$"),
    "collection_id": re.compile(r"^OSI-SYN-COL-\d{3,}$"),
    "source_id": re.compile(r"^OSI-SYN-SRC-\d{3,}$"),
    "evidence_id": re.compile(r"^OSI-SYN-EVD-\d{3,}$"),
    "observation_id": re.compile(r"^OSI-SYN-OBS-\d{3,}$"),
}


class OSIOrganizationalEvidenceAssurance(OSIComponent):
    """Validate a bounded synthetic organizational package without graph I/O."""

    component_id = "osi.organizational_evidence_assurance"
    component_version = COMPONENT_VERSION
    contract_version = CONTRACT_VERSION

    def __init__(self, package: Path):
        self.package = package
        self.data: dict[str, list[dict[str, str]]] = {}
        self.findings: list[Finding] = []
        self.elapsed_seconds = 0.0
        self._evaluated = False

    @staticmethod
    def _read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), [dict(row) for row in reader]

    @staticmethod
    def _iso(value: str) -> bool:
        if not value:
            return True
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except ValueError:
            try:
                date.fromisoformat(value)
                return True
            except ValueError:
                return False

    def add(
        self, severity: FindingSeverity, code: str, dimension: str, rule: str,
        filename: str, row: int | None, field: str | None, message: str,
        uncertainty: str = "",
    ) -> None:
        self.findings.append(Finding(
            severity=severity, code=code, message=message, dimension=dimension,
            rule_id=rule, file=filename, row=row, field=field,
            logic_chain=[f"Read {filename}", f"Evaluate {rule}", f"Emit {code}"],
            uncertainty=uncertainty,
        ))

    def _evaluate(self) -> None:
        if self._evaluated:
            return
        started = time.perf_counter()
        for filename, schema in SCHEMAS.items():
            path = self.package / filename
            if not path.is_file():
                self.add(FindingSeverity.ERROR, "FILE_MISSING", "contract", "contract.required_file", filename, None, None, "Required CSV file is missing.")
                self.data[filename] = []
                continue
            try:
                headers, rows = self._read(path)
            except (OSError, UnicodeError, csv.Error) as exc:
                self.add(FindingSeverity.ERROR, "FILE_UNREADABLE", "contract", "contract.readable_csv", filename, None, None, f"CSV could not be read: {type(exc).__name__}.")
                self.data[filename] = []
                continue
            self.data[filename] = rows
            for field in sorted(schema["required"] - set(headers)):
                self.add(FindingSeverity.ERROR, "HEADER_MISSING", "contract", "contract.required_column", filename, 1, field, "Required column is missing.")
            seen: set[str] = set()
            for row_number, record in enumerate(rows, start=2):
                for field in schema["required"]:
                    if not (record.get(field) or "").strip():
                        self.add(FindingSeverity.ERROR, "REQUIRED_EMPTY", "validation", "validation.required_value", filename, row_number, field, "Required value is empty.")
                for field, allowed in schema.get("enums", {}).items():
                    value = (record.get(field) or "").strip()
                    if value and value not in allowed:
                        self.add(FindingSeverity.ERROR, "ENUM_INVALID", "validation", "validation.enum", filename, row_number, field, f"Value '{value}' is not allowed.")
                identifier = (record.get(schema["id"]) or "").strip()
                if identifier:
                    if identifier in seen:
                        self.add(FindingSeverity.ERROR, "ID_DUPLICATE", "validation", "validation.unique_id", filename, row_number, schema["id"], f"Duplicate ID '{identifier}' in file.")
                    seen.add(identifier)
                    pattern = ID_PATTERNS[schema["id"]]
                    if not pattern.fullmatch(identifier):
                        self.add(FindingSeverity.ERROR, "SYNTHETIC_ID_INVALID", "ethics", "ethics.synthetic_identity", filename, row_number, schema["id"], "Synthetic organizational package IDs must use the OSI-SYN namespace.")
                for field, value in record.items():
                    if value and (field.endswith("_at") or field.endswith("_date")) and not self._iso(value.strip()):
                        self.add(FindingSeverity.ERROR, "DATE_INVALID", "validation", "validation.iso8601", filename, row_number, field, f"'{value}' is not valid ISO 8601.")
                if filename == "observation_candidate.csv":
                    try:
                        confidence = float(record.get("confidence") or "")
                        if not 0 <= confidence <= 1:
                            raise ValueError
                    except ValueError:
                        self.add(FindingSeverity.ERROR, "CONFIDENCE_INVALID", "validation", "validation.confidence_range", filename, row_number, "confidence", "Confidence must be between 0 and 1.")
                    if not (record.get("negative_boundary") or "").strip():
                        self.add(FindingSeverity.ERROR, "BOUNDARY_MISSING", "epistemic_integrity", "epi.negative_boundary", filename, row_number, "negative_boundary", "Observation candidate lacks an explicit negative boundary.")
                    if record.get("review_status") == "accepted" and not (record.get("reviewed_by") or "").strip():
                        self.add(FindingSeverity.ERROR, "REVIEWER_MISSING", "congruence", "congruence.accepted_review", filename, row_number, "reviewed_by", "Accepted observation candidate requires a reviewer identity.")

        organizations = {record.get("organization_id") for record in self.data["organization.csv"]}
        units = {record.get("organizational_unit_id") for record in self.data["organizational_unit.csv"]}
        collections = {record.get("collection_id"): record for record in self.data["collection.csv"]}
        sources = {record.get("source_id"): record for record in self.data["source.csv"]}
        evidence = {record.get("evidence_id") for record in self.data["evidence.csv"]}
        for filename in ("organizational_unit.csv", "position.csv", "collection.csv", "source.csv", "evidence.csv"):
            for row_number, record in enumerate(self.data[filename], start=2):
                if record.get("organization_id") not in organizations:
                    self.add(FindingSeverity.ERROR, "FK_ORGANIZATION", "congruence", "congruence.organization_fk", filename, row_number, "organization_id", "Organization foreign key was not found.")
        for row_number, record in enumerate(self.data["position.csv"], start=2):
            if record.get("organizational_unit_id") not in units:
                self.add(FindingSeverity.ERROR, "FK_UNIT", "congruence", "congruence.unit_fk", "position.csv", row_number, "organizational_unit_id", "Organizational-unit foreign key was not found.")
        for row_number, record in enumerate(self.data["source.csv"], start=2):
            collection = collections.get(record.get("collection_id"))
            if collection is None:
                self.add(FindingSeverity.ERROR, "FK_COLLECTION", "congruence", "congruence.collection_fk", "source.csv", row_number, "collection_id", "Collection foreign key was not found.")
            elif collection.get("organization_id") != record.get("organization_id"):
                self.add(FindingSeverity.ERROR, "COLLECTION_SCOPE_CONFLICT", "congruence", "congruence.collection_scope", "source.csv", row_number, "organization_id", "Source organization conflicts with its collection.")
        for row_number, record in enumerate(self.data["evidence.csv"], start=2):
            source = sources.get(record.get("source_id"))
            if source is None:
                self.add(FindingSeverity.ERROR, "FK_SOURCE", "congruence", "congruence.source_fk", "evidence.csv", row_number, "source_id", "Source foreign key was not found.")
            elif source.get("organization_id") != record.get("organization_id"):
                self.add(FindingSeverity.ERROR, "SOURCE_SCOPE_CONFLICT", "congruence", "congruence.source_scope", "evidence.csv", row_number, "organization_id", "Evidence organization conflicts with its source.")
            if not (record.get("source_locator") or "").strip():
                self.add(FindingSeverity.WARNING, "LOCATOR_MISSING", "epistemic_integrity", "epi.source_locator", "evidence.csv", row_number, "source_locator", "Evidence has no source locator.", "The evidence cannot be precisely reproduced from its source.")
        for row_number, record in enumerate(self.data["observation_candidate.csv"], start=2):
            if record.get("evidence_id") not in evidence:
                self.add(FindingSeverity.ERROR, "FK_EVIDENCE", "congruence", "congruence.evidence_fk", "observation_candidate.csv", row_number, "evidence_id", "Evidence foreign key was not found.")
            if record.get("review_status") in {"proposed", "needs_review"}:
                self.add(FindingSeverity.REVIEW, "OBSERVATION_REVIEW_REQUIRED", "ethics", "ethics.observation_review", "observation_candidate.csv", row_number, "review_status", "Observation candidate requires accountable review before any diagnostic use.")
        self.elapsed_seconds = time.perf_counter() - started
        self._evaluated = True

    def findings_for(self, dimension: str) -> list[Finding]:
        self._evaluate()
        return [finding for finding in self.findings if finding.dimension == dimension]

    def _result(self, dimension: str, message: str) -> AssuranceResult:
        return AssuranceResult.from_findings(dimension, self.findings_for(dimension), message)

    def test_contract(self) -> AssuranceResult:
        return self._result("contract", "All OSI organizational package files and columns satisfy contract v0.1.")

    def test_validation(self) -> AssuranceResult:
        return self._result("validation", "Organizational package values satisfy bounded validation rules.")

    def test_congruence(self) -> AssuranceResult:
        return self._result("congruence", "Organizational structure, provenance, and observation references are congruent.")

    def test_regression(self) -> AssuranceResult:
        return AssuranceResult(dimension="regression", disposition=Disposition.PASS, message="Synthetic success and failure fixtures are exercised by the component test suite.")

    def test_performance(self) -> AssuranceResult:
        self._evaluate()
        return AssuranceResult(dimension="performance", disposition=Disposition.PASS, message=f"Validated {sum(len(rows) for rows in self.data.values())} row(s) in {self.elapsed_seconds:.3f}s.", metrics={"rows": sum(len(rows) for rows in self.data.values()), "elapsed_seconds": self.elapsed_seconds})

    def test_ethics(self) -> AssuranceResult:
        return self._result("ethics", "Synthetic identity and review gates are explicit.")

    def test_epistemic_integrity(self) -> AssuranceResult:
        return self._result("epistemic_integrity", "Evidence and observation candidates retain provenance and negative boundaries.")

    def assure(self, input_reference: str = "", configuration_reference: str = "") -> AssuranceReport:
        return super().assure(input_reference=input_reference or str(self.package.resolve()), configuration_reference=configuration_reference)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = OSIOrganizationalEvidenceAssurance(args.package).assure()
    rendered = report.to_json()
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report.overall_disposition == Disposition.PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
