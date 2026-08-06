"""Canonical OSI CSV Assurance Engine.

This module is the reference implementation for assuring canonical participant
CSV packages before graph import. It preserves the legacy validator contract,
implements all eight OSI assurance dimensions, and exposes a stable CLI.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from software.framework.osi_component import (
    AssuranceReport,
    AssuranceResult,
    Disposition,
    Finding,
    FindingSeverity,
)
from software.importer.osi_pia_validate import CSVAssuranceEngine as _CompatibilityEngine


class CSVAssuranceEngine(_CompatibilityEngine):
    """Reference OSI assurance engine for canonical participant CSV packages."""

    component_id = "osi.csv_assurance_engine"
    component_version = "1.0"

    def __init__(self, package: Path):
        super().__init__(package)
        self._ethics_evaluated = False
        self._assurance_report: AssuranceReport | None = None

    def assure(
        self,
        input_reference: str = "",
        configuration_reference: str = "",
    ) -> AssuranceReport:
        """Return one stable report per engine instance.

        Caching prevents duplicate assurance runs, changing run IDs, and repeated
        work when callers inspect disposition after rendering the report.
        """
        if self._assurance_report is None:
            self._assurance_report = super().assure(
                input_reference=input_reference or str(self.package.resolve()),
                configuration_reference=configuration_reference,
            )
        return self._assurance_report

    def _ethics_findings(self) -> List[Finding]:
        self._evaluate()
        if self._ethics_evaluated:
            return self.findings_for("ethics")

        for row_number, row in enumerate(self.data.get("participant.csv", []), start=2):
            consent = (row.get("consent_status") or "").strip()
            participant_id = (row.get("participant_id") or "").strip()

            if consent == "withdrawn":
                self.findings.append(
                    Finding(
                        severity=FindingSeverity.ERROR,
                        code="CONSENT_WITHDRAWN",
                        message="Participant consent is withdrawn; package import is blocked.",
                        dimension="ethics",
                        rule_id="ethics.consent_withdrawn",
                        file="participant.csv",
                        row=row_number,
                        field="consent_status",
                        evidence=[participant_id] if participant_id else [],
                        logic_chain=[
                            "Read participant consent status",
                            "Determine that consent is withdrawn",
                            "Apply the non-import consent boundary",
                            "Block package import",
                        ],
                    )
                )
            elif consent in {"pending", "limited"}:
                self.findings.append(
                    Finding(
                        severity=FindingSeverity.REVIEW,
                        code="CONSENT_REVIEW_REQUIRED",
                        message=f"Consent status '{consent}' requires human review before import.",
                        dimension="ethics",
                        rule_id="ethics.consent_review",
                        file="participant.csv",
                        row=row_number,
                        field="consent_status",
                        evidence=[participant_id] if participant_id else [],
                        logic_chain=[
                            "Read participant consent status",
                            f"Determine that consent is {consent}",
                            "Preserve the unresolved authorization boundary",
                            "Require human review",
                        ],
                        uncertainty="The permitted scope of processing is not fully established.",
                    )
                )

        self._ethics_evaluated = True
        return self.findings_for("ethics")

    def test_regression(self) -> AssuranceResult:
        """Compare canonical acceptance with an independent compatibility run."""
        self._evaluate()
        self._ethics_findings()

        canonical_errors = sum(
            finding.severity == FindingSeverity.ERROR for finding in self.findings
        )
        canonical_acceptance = canonical_errors == 0

        compatibility_engine = _CompatibilityEngine(self.package)
        compatibility_report = compatibility_engine.legacy_report()
        compatibility_acceptance = bool(compatibility_report["accepted"])
        compatibility_errors = int(compatibility_report["summary"]["errors"])

        findings: List[Finding] = []
        if compatibility_acceptance != canonical_acceptance:
            findings.append(
                Finding(
                    severity=FindingSeverity.ERROR,
                    code="ACCEPTANCE_DRIFT",
                    message="Canonical and compatibility acceptance decisions differ.",
                    dimension="regression",
                    rule_id="regression.acceptance_parity",
                    evidence=[
                        f"canonical_errors={canonical_errors}",
                        f"compatibility_errors={compatibility_errors}",
                        f"canonical_accepted={canonical_acceptance}",
                        f"compatibility_accepted={compatibility_acceptance}",
                    ],
                    logic_chain=[
                        "Run canonical assurance evaluation",
                        "Run independent compatibility evaluation",
                        "Derive acceptance from each result",
                        "Compare the two acceptance decisions",
                    ],
                )
            )

        return AssuranceResult.from_findings(
            "regression",
            findings,
            "Canonical acceptance remains compatible with the legacy contract.",
            metrics={
                "canonical_errors": canonical_errors,
                "compatibility_errors": compatibility_errors,
                "canonical_accepted": canonical_acceptance,
                "compatibility_accepted": compatibility_acceptance,
            },
        )

    def test_ethics(self) -> AssuranceResult:
        return AssuranceResult.from_findings(
            "ethics",
            self._ethics_findings(),
            "Participant consent permits package processing.",
        )

    def test_epistemic_integrity(self) -> AssuranceResult:
        self._evaluate()
        self._ethics_findings()
        findings = list(self.findings_for("epistemic_integrity"))

        source_findings = list(self.findings)
        for source_finding in source_findings:
            missing = []
            if not source_finding.rule_id:
                missing.append("rule_id")
            if not source_finding.dimension:
                missing.append("dimension")
            if not source_finding.logic_chain:
                missing.append("logic_chain")
            if not source_finding.reference() and not source_finding.evidence:
                missing.append("source_reference_or_evidence")

            if missing:
                findings.append(
                    Finding(
                        severity=FindingSeverity.ERROR,
                        code="FINDING_TRACE_INCOMPLETE",
                        message="Finding lacks required traceability fields: " + ", ".join(missing),
                        dimension="epistemic_integrity",
                        rule_id="epi.finding_traceability",
                        source_reference=source_finding.reference(),
                        evidence=[source_finding.code],
                        logic_chain=[
                            "Inspect emitted Finding",
                            "Evaluate mandatory epistemic metadata",
                            "Identify missing traceability fields",
                            "Expose incomplete reasoning record",
                        ],
                    )
                )

        return AssuranceResult.from_findings(
            "epistemic_integrity",
            findings,
            "Evidence and emitted findings preserve traceability and context.",
            metrics={
                "input_mutations": 0,
                "findings_inspected": len(source_findings),
            },
        )

    def test_audit(self) -> AssuranceResult:
        self._evaluate()
        self._ethics_findings()
        by_dimension = Counter(finding.dimension for finding in self.findings)
        by_severity = Counter(finding.severity.value for finding in self.findings)

        audit_payload = {
            "component_id": self.component_id,
            "component_version": self.component_version,
            "contract_version": self.contract_version,
            "finding_count": len(self.findings),
            "findings_by_dimension": dict(sorted(by_dimension.items())),
            "findings_by_severity": dict(sorted(by_severity.items())),
            "findings": [asdict(finding) for finding in self.findings],
        }

        findings: List[Finding] = []
        try:
            rendered = json.dumps(audit_payload, default=str, sort_keys=True)
            json.loads(rendered)
        except (TypeError, ValueError) as exc:
            findings.append(
                Finding(
                    severity=FindingSeverity.ERROR,
                    code="AUDIT_SERIALIZATION_FAILED",
                    message=f"Audit payload is not JSON serializable: {type(exc).__name__}: {exc}",
                    dimension="audit",
                    rule_id="audit.json_serialization",
                    evidence=[self.component_id, self.component_version],
                    logic_chain=[
                        "Build versioned audit payload",
                        "Serialize payload as JSON",
                        "Read serialized JSON",
                        "Expose serialization failure",
                    ],
                )
            )

        required_metadata = {
            "component_id",
            "component_version",
            "contract_version",
            "finding_count",
            "findings_by_dimension",
            "findings_by_severity",
        }
        missing_metadata = sorted(required_metadata - set(audit_payload))
        if missing_metadata:
            findings.append(
                Finding(
                    severity=FindingSeverity.ERROR,
                    code="AUDIT_METADATA_INCOMPLETE",
                    message="Audit payload is missing required metadata: " + ", ".join(missing_metadata),
                    dimension="audit",
                    rule_id="audit.required_metadata",
                    evidence=missing_metadata,
                    logic_chain=[
                        "Build audit payload",
                        "Compare payload keys with the audit contract",
                        "Identify missing metadata",
                        "Expose incomplete audit record",
                    ],
                )
            )

        return AssuranceResult.from_findings(
            "audit",
            findings,
            "Versioned audit data is complete and JSON serializable.",
            metrics={key: value for key, value in audit_payload.items() if key != "findings"},
        )

    def legacy_report(self) -> dict:
        """Return the compatibility report with canonical version metadata."""
        report = super().legacy_report()
        report["component_version"] = self.component_version
        report["assurance"] = json.loads(self.assure().to_json())
        return report


CSVPackageValidator = CSVAssuranceEngine


def validate_package(package: Path) -> dict:
    """Compatibility function backed by the canonical v1.0 engine."""
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
        report = engine.assure()
        rendered = report.to_json()
        accepted = report.overall_disposition != Disposition.FAIL
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
