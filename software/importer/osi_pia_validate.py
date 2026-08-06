#!/usr/bin/env python3
"""Assure an OSI/PIA participant CSV package before graph import.

The CSV Assurance Engine preserves the validator's existing checks and CLI
behavior while routing every result through the shared OSI assurance contract.
Standard-library only. Emits JSON and exits non-zero when blocking errors are
found.
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
from typing import Iterable, List

try:
    from software.framework.osi_component import (
        AssuranceResult,
        Disposition,
        Finding,
        FindingSeverity,
        OSIComponent,
    )
except ModuleNotFoundError:  # Support direct execution from software/importer.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from software.framework.osi_component import (
        AssuranceResult,
        Disposition,
        Finding,
        FindingSeverity,
        OSIComponent,
    )


CONTRACT_VERSION = "0.1"
COMPONENT_VERSION = "0.2"

SCHEMAS = {
    "participant.csv": {
        "required": {"participant_id", "status", "consent_status", "created_at", "updated_at"},
        "enums": {
            "status": {"active", "inactive", "withdrawn", "archived"},
            "consent_status": {"pending", "granted", "limited", "withdrawn"},
        },
    },
    "source.csv": {
        "required": {"source_id", "participant_id", "source_type", "collected_at", "confidentiality"},
        "enums": {
            "source_type": {"resume", "cover_letter", "interview", "questionnaire", "portfolio", "record", "other"},
            "confidentiality": {"public", "internal", "restricted", "participant_private"},
        },
    },
    "experience.csv": {
        "required": {"experience_id", "participant_id", "experience_type", "title", "date_status"},
        "enums": {
            "experience_type": {"employment", "education", "project", "service", "creative_work", "other"},
            "date_status": {"known", "partial", "current", "unknown"},
        },
    },
    "evidence.csv": {
        "required": {"evidence_id", "source_id", "participant_id", "evidence_text", "evidence_type", "extraction_method", "fidelity_status", "review_status", "created_at"},
        "enums": {
            "evidence_type": {"activity", "responsibility", "output", "achievement", "event", "condition", "statement", "other"},
            "extraction_method": {"manual", "assisted", "automated"},
            "fidelity_status": {"verbatim", "close_paraphrase", "normalized", "summarized"},
            "review_status": {"unreviewed", "reviewed", "participant_confirmed", "disputed", "superseded"},
        },
    },
    "capability.csv": {
        "required": {"capability_id", "capability_name", "definition", "status", "ontology_version"},
        "enums": {"status": {"proposed", "working", "established", "deprecated"}},
    },
    "evidence_capability_mapping.csv": {
        "required": {"mapping_id", "evidence_id", "capability_id", "relationship_type", "confidence", "confidence_basis", "proposed_by", "review_status", "created_at"},
        "enums": {
            "relationship_type": {"SUPPORTS"},
            "review_status": {"proposed", "accepted", "rejected", "needs_review"},
        },
    },
}

ID_PATTERNS = {
    "participant_id": re.compile(r"^PIA-\d{3,}$"),
    "source_id": re.compile(r"^PIA-\d{3,}-SRC-\d{3,}$"),
    "experience_id": re.compile(r"^PIA-\d{3,}-EXP-\d{3,}$"),
    "evidence_id": re.compile(r"^PIA-\d{3,}-EVD-\d{3,}$"),
    "mapping_id": re.compile(r"^PIA-\d{3,}-MAP-\d{3,}$"),
    "capability_id": re.compile(r"^CAP-[A-Z0-9-]+$"),
}

PRIMARY_ID_FIELDS = {
    "participant.csv": "participant_id",
    "source.csv": "source_id",
    "experience.csv": "experience_id",
    "evidence.csv": "evidence_id",
    "capability.csv": "capability_id",
    "evidence_capability_mapping.csv": "mapping_id",
}


class CSVAssuranceEngine(OSIComponent):
    """Reference OSI assurance implementation for participant CSV packages."""

    component_id = "osi.csv_assurance_engine"
    component_version = COMPONENT_VERSION
    contract_version = CONTRACT_VERSION

    def __init__(self, package: Path):
        self.package = package
        self.findings: List[Finding] = []
        self.data: dict[str, list[dict[str, str]]] = {}
        self.headers: dict[str, list[str]] = {}
        self.elapsed_seconds = 0.0
        self._evaluated = False

    @staticmethod
    def parse_iso(value: str) -> bool:
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

    @staticmethod
    def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), [dict(row) for row in reader]

    def add_finding(
        self,
        severity: FindingSeverity,
        code: str,
        dimension: str,
        rule_id: str,
        file: str,
        row: int | None,
        field: str | None,
        message: str,
        evidence: list[str] | None = None,
        logic_chain: list[str] | None = None,
        uncertainty: str = "",
    ) -> None:
        """Create a traceable Finding rather than writing directly to a report."""
        self.findings.append(
            Finding(
                severity=severity,
                code=code,
                message=message,
                dimension=dimension,
                rule_id=rule_id,
                file=file,
                row=row,
                field=field,
                evidence=evidence or [],
                logic_chain=logic_chain or [
                    f"Read {file}",
                    f"Evaluate {rule_id}",
                    f"Emit {code}",
                ],
                uncertainty=uncertainty,
            )
        )

    def _evaluate(self) -> None:
        if self._evaluated:
            return

        started = time.perf_counter()

        for filename, schema in SCHEMAS.items():
            path = self.package / filename
            if not path.exists():
                self.add_finding(
                    FindingSeverity.ERROR, "FILE_MISSING", "contract",
                    "contract.required_file", filename, None, None,
                    "Required CSV file is missing."
                )
                self.data[filename] = []
                self.headers[filename] = []
                continue

            try:
                headers, rows = self.read_csv(path)
            except (OSError, UnicodeError, csv.Error) as exc:
                self.add_finding(
                    FindingSeverity.ERROR, "FILE_UNREADABLE", "contract",
                    "contract.readable_csv", filename, None, None,
                    f"CSV could not be read: {type(exc).__name__}: {exc}"
                )
                self.data[filename] = []
                self.headers[filename] = []
                continue

            self.headers[filename] = headers
            self.data[filename] = rows

            for field in sorted(schema["required"] - set(headers)):
                self.add_finding(
                    FindingSeverity.ERROR, "HEADER_MISSING", "contract",
                    "contract.required_column", filename, 1, field,
                    "Required column is missing."
                )

            primary_id_field = PRIMARY_ID_FIELDS[filename]
            seen_primary_ids: set[str] = set()
            for row_number, row in enumerate(rows, start=2):
                for field in schema["required"]:
                    if not (row.get(field) or "").strip():
                        self.add_finding(
                            FindingSeverity.ERROR, "REQUIRED_EMPTY", "validation",
                            "validation.required_value", filename, row_number, field,
                            "Required value is empty."
                        )

                for field, allowed in schema.get("enums", {}).items():
                    value = (row.get(field) or "").strip()
                    if value and value not in allowed:
                        self.add_finding(
                            FindingSeverity.ERROR, "ENUM_INVALID", "validation",
                            "validation.enum", filename, row_number, field,
                            f"Value '{value}' is not allowed."
                        )

                for field, pattern in ID_PATTERNS.items():
                    value = (row.get(field) or "").strip()
                    if not value:
                        continue
                    if not pattern.fullmatch(value):
                        self.add_finding(
                            FindingSeverity.WARNING, "ID_FORMAT", "validation",
                            "validation.id_format", filename, row_number, field,
                            f"ID '{value}' does not match the recommended pattern.",
                            uncertainty="The identifier may still be usable but violates the working convention."
                        )
                    if field == primary_id_field:
                        if value in seen_primary_ids:
                            self.add_finding(
                                FindingSeverity.ERROR, "ID_DUPLICATE", "validation",
                                "validation.unique_id", filename, row_number, field,
                                f"Duplicate ID '{value}' in file."
                            )
                        seen_primary_ids.add(value)

                for field, value in row.items():
                    if value and (field.endswith("_at") or field.endswith("_date")):
                        if not self.parse_iso(value.strip()):
                            self.add_finding(
                                FindingSeverity.ERROR, "DATE_INVALID", "validation",
                                "validation.iso8601", filename, row_number, field,
                                f"'{value}' is not valid ISO 8601."
                            )

                if filename == "evidence_capability_mapping.csv":
                    raw = (row.get("confidence") or "").strip()
                    if raw:
                        try:
                            confidence = float(raw)
                            if not 0 <= confidence <= 1:
                                raise ValueError
                        except ValueError:
                            self.add_finding(
                                FindingSeverity.ERROR, "CONFIDENCE_INVALID", "validation",
                                "validation.confidence_range", filename, row_number,
                                "confidence", "Confidence must be between 0.00 and 1.00."
                            )

                if filename == "evidence.csv" and not (row.get("experience_id") or "").strip():
                    self.add_finding(
                        FindingSeverity.WARNING, "EXPERIENCE_MISSING", "epistemic_integrity",
                        "epi.experience_context", filename, row_number, "experience_id",
                        "Evidence has no Experience context.",
                        uncertainty="The evidence may be valid but its organizational context is incomplete."
                    )

                if filename == "evidence.csv" and not (row.get("source_locator") or "").strip():
                    self.add_finding(
                        FindingSeverity.WARNING, "LOCATOR_MISSING", "epistemic_integrity",
                        "epi.source_locator", filename, row_number, "source_locator",
                        "Evidence has no source locator.",
                        uncertainty="The assertion cannot be precisely reproduced from its source."
                    )

        participants = {r.get("participant_id", "") for r in self.data["participant.csv"]}
        sources = {r.get("source_id", ""): r for r in self.data["source.csv"]}
        experiences = {r.get("experience_id", ""): r for r in self.data["experience.csv"]}
        evidence = {r.get("evidence_id", ""): r for r in self.data["evidence.csv"]}
        capabilities = {r.get("capability_id", "") for r in self.data["capability.csv"]}

        for filename in ("source.csv", "experience.csv", "evidence.csv"):
            for row_number, row in enumerate(self.data[filename], start=2):
                if row.get("participant_id") not in participants:
                    self.add_finding(
                        FindingSeverity.ERROR, "FK_PARTICIPANT", "congruence",
                        "congruence.participant_fk", filename, row_number,
                        "participant_id", "Participant foreign key was not found."
                    )

        for row_number, row in enumerate(self.data["evidence.csv"], start=2):
            source = sources.get(row.get("source_id", ""))
            if not source:
                self.add_finding(
                    FindingSeverity.ERROR, "FK_SOURCE", "congruence",
                    "congruence.source_fk", "evidence.csv", row_number,
                    "source_id", "Source foreign key was not found."
                )
            elif source.get("participant_id") != row.get("participant_id"):
                self.add_finding(
                    FindingSeverity.ERROR, "PARTICIPANT_MISMATCH", "congruence",
                    "congruence.source_participant", "evidence.csv", row_number,
                    "participant_id", "Evidence and Source participant IDs do not match."
                )

            exp_id = row.get("experience_id", "")
            if exp_id and exp_id not in experiences:
                self.add_finding(
                    FindingSeverity.ERROR, "FK_EXPERIENCE", "congruence",
                    "congruence.experience_fk", "evidence.csv", row_number,
                    "experience_id", "Experience foreign key was not found."
                )

        for row_number, row in enumerate(self.data["evidence_capability_mapping.csv"], start=2):
            if row.get("evidence_id") not in evidence:
                self.add_finding(
                    FindingSeverity.ERROR, "FK_EVIDENCE", "congruence",
                    "congruence.evidence_fk", "evidence_capability_mapping.csv",
                    row_number, "evidence_id", "Evidence foreign key was not found."
                )
            if row.get("capability_id") not in capabilities:
                self.add_finding(
                    FindingSeverity.ERROR, "FK_CAPABILITY", "congruence",
                    "congruence.capability_fk", "evidence_capability_mapping.csv",
                    row_number, "capability_id", "Capability foreign key was not found."
                )

        self.elapsed_seconds = time.perf_counter() - started
        self._evaluated = True

    def findings_for(self, dimension: str) -> List[Finding]:
        self._evaluate()
        return [finding for finding in self.findings if finding.dimension == dimension]

    def test_contract(self) -> AssuranceResult:
        return AssuranceResult.from_findings(
            "contract", self.findings_for("contract"),
            "All required files and columns satisfy contract v0.1."
        )

    def test_validation(self) -> AssuranceResult:
        return AssuranceResult.from_findings(
            "validation", self.findings_for("validation"),
            "Field values satisfy validation rules."
        )

    def test_congruence(self) -> AssuranceResult:
        return AssuranceResult.from_findings(
            "congruence", self.findings_for("congruence"),
            "Cross-file relationships are congruent."
        )

    def test_regression(self) -> AssuranceResult:
        self._evaluate()
        return AssuranceResult(
            dimension="regression",
            disposition=Disposition.NOT_APPLICABLE,
            message="Regression corpus is not yet configured for this component."
        )

    def test_performance(self) -> AssuranceResult:
        self._evaluate()
        total_rows = sum(len(rows) for rows in self.data.values())
        return AssuranceResult(
            dimension="performance",
            disposition=Disposition.PASS,
            message=f"Validated {total_rows} row(s) in {self.elapsed_seconds:.3f}s.",
            metrics={"rows": total_rows, "elapsed_seconds": self.elapsed_seconds},
        )

    def test_ethics(self) -> AssuranceResult:
        self._evaluate()
        return AssuranceResult(
            dimension="ethics",
            disposition=Disposition.PASS,
            message="Existing validator behavior includes no blocking ethics rule yet."
        )

    def test_epistemic_integrity(self) -> AssuranceResult:
        return AssuranceResult.from_findings(
            "epistemic_integrity", self.findings_for("epistemic_integrity"),
            "Evidence retains source and experience context required for traceability.",
            metrics={"input_mutations": 0},
        )

    def assure(self, input_reference: str = "", configuration_reference: str = ""):
        return super().assure(
            input_reference=input_reference or str(self.package.resolve()),
            configuration_reference=configuration_reference,
        )

    def legacy_report(self) -> dict:
        """Preserve the pre-refactor JSON shape for existing scripts and users."""
        self._evaluate()
        counts = {name: len(rows) for name, rows in self.data.items()}
        summary = {
            "errors": sum(f.severity == FindingSeverity.ERROR for f in self.findings),
            "warnings": sum(f.severity == FindingSeverity.WARNING for f in self.findings),
            "notices": sum(f.severity == FindingSeverity.NOTICE for f in self.findings),
        }
        return {
            "contract_version": CONTRACT_VERSION,
            "component_id": self.component_id,
            "component_version": self.component_version,
            "package": str(self.package.resolve()),
            "accepted": summary["errors"] == 0,
            "counts": counts,
            "summary": summary,
            "findings": [
                {
                    "severity": finding.severity.value,
                    "code": finding.code,
                    "file": finding.file,
                    "row": finding.row,
                    "field": finding.field,
                    "message": finding.message,
                    "dimension": finding.dimension,
                    "rule_id": finding.rule_id,
                    "evidence": finding.evidence,
                    "logic_chain": finding.logic_chain,
                    "confidence": finding.confidence,
                    "uncertainty": finding.uncertainty,
                }
                for finding in self.findings
            ],
            "assurance": json.loads(self.assure().to_json()),
        }


# Compatibility alias during the transition from validator to assurance engine.
CSVPackageValidator = CSVAssuranceEngine


def validate_package(package: Path) -> dict:
    """Compatibility wrapper preserving the original public function."""
    return CSVAssuranceEngine(package).legacy_report()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Directory containing the six canonical CSV files")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report to this path")
    parser.add_argument(
        "--assurance-only",
        action="store_true",
        help="Emit only the standard OSI AssuranceReport rather than the compatibility report",
    )
    args = parser.parse_args(argv)

    if not args.package.is_dir():
        parser.error(f"Package directory does not exist: {args.package}")

    engine = CSVAssuranceEngine(args.package)
    if args.assurance_only:
        rendered = engine.assure().to_json()
        accepted = engine.assure().overall_disposition != Disposition.FAIL
    else:
        report = engine.legacy_report()
        rendered = json.dumps(report, indent=2)
        accepted = report["accepted"]

    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 0 if accepted else 2


if __name__ == "__main__":
    sys.exit(main())
