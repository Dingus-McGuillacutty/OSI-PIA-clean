from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from software.framework.osi_component import Disposition
from software.importer.csv_assurance_engine import CSVAssuranceEngine, main, validate_package


HEADERS = {
    "participant.csv": ["participant_id", "status", "consent_status", "created_at", "updated_at"],
    "source.csv": ["source_id", "participant_id", "source_type", "collected_at", "confidentiality"],
    "experience.csv": ["experience_id", "participant_id", "experience_type", "title", "date_status"],
    "evidence.csv": ["evidence_id", "source_id", "participant_id", "experience_id", "source_locator", "evidence_text", "evidence_type", "extraction_method", "fidelity_status", "review_status", "created_at"],
    "capability.csv": ["capability_id", "capability_name", "definition", "status", "ontology_version"],
    "evidence_capability_mapping.csv": ["mapping_id", "evidence_id", "capability_id", "relationship_type", "confidence", "confidence_basis", "proposed_by", "review_status", "created_at"],
}

ROWS = {
    "participant.csv": [["PIA-9001", "active", "granted", "2026-01-01", "2026-01-01"]],
    "source.csv": [["PIA-9001-SRC-001", "PIA-9001", "interview", "2026-01-01", "restricted"]],
    "experience.csv": [["PIA-9001-EXP-001", "PIA-9001", "employment", "Example", "known"]],
    "evidence.csv": [["PIA-9001-EVD-001", "PIA-9001-SRC-001", "PIA-9001", "PIA-9001-EXP-001", "transcript:12", "Observed evidence", "activity", "manual", "verbatim", "reviewed", "2026-01-01"]],
    "capability.csv": [["CAP-EXAMPLE", "Example", "Example capability", "working", "0.1"]],
    "evidence_capability_mapping.csv": [["PIA-9001-MAP-001", "PIA-9001-EVD-001", "CAP-EXAMPLE", "SUPPORTS", "0.80", "Direct evidence", "human", "accepted", "2026-01-01"]],
}


def write_package(root: Path, consent_status: str = "granted") -> None:
    for filename, headers in HEADERS.items():
        rows = [list(row) for row in ROWS[filename]]
        if filename == "participant.csv":
            rows[0][2] = consent_status
        with (root / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)


class CanonicalCSVAssuranceV1Tests(unittest.TestCase):
    def make_package(self, consent_status: str = "granted") -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        write_package(root, consent_status)
        return root

    def test_report_is_cached_and_stable(self):
        engine = CSVAssuranceEngine(self.make_package())
        first = engine.assure()
        second = engine.assure()
        self.assertIs(first, second)
        self.assertEqual(first.run_id, second.run_id)

    def test_all_eight_gates_pass_for_valid_package(self):
        report = CSVAssuranceEngine(self.make_package()).assure()
        self.assertEqual(Disposition.PASS, report.overall_disposition)
        self.assertEqual(
            [
                "contract",
                "validation",
                "congruence",
                "regression",
                "performance",
                "ethics",
                "epistemic_integrity",
                "audit",
            ],
            [result.dimension for result in report.results],
        )
        self.assertTrue(all(result.disposition == Disposition.PASS for result in report.results))

    def test_regression_gate_runs_independent_compatibility_engine(self):
        report = CSVAssuranceEngine(self.make_package()).assure()
        regression = next(result for result in report.results if result.dimension == "regression")
        self.assertEqual(Disposition.PASS, regression.disposition)
        self.assertTrue(regression.metrics["canonical_accepted"])
        self.assertTrue(regression.metrics["compatibility_accepted"])
        self.assertEqual(0, regression.metrics["canonical_errors"])
        self.assertEqual(0, regression.metrics["compatibility_errors"])

    def test_audit_gate_proves_json_serialization(self):
        engine = CSVAssuranceEngine(self.make_package())
        report = engine.assure()
        rendered = report.to_json()
        decoded = json.loads(rendered)
        audit = next(result for result in report.results if result.dimension == "audit")
        self.assertEqual(Disposition.PASS, audit.disposition)
        self.assertEqual("1.0", audit.metrics["component_version"])
        self.assertEqual("1.0", decoded["component_version"])

    def test_withdrawn_consent_blocks_and_cli_returns_two(self):
        package = self.make_package("withdrawn")
        report = CSVAssuranceEngine(package).assure()
        self.assertEqual(Disposition.FAIL, report.overall_disposition)
        self.assertEqual(2, main([str(package), "--assurance-only"]))

    def test_pending_consent_requires_review_but_does_not_fail_cli(self):
        package = self.make_package("pending")
        report = CSVAssuranceEngine(package).assure()
        self.assertEqual(Disposition.REQUIRES_HUMAN_REVIEW, report.overall_disposition)
        self.assertEqual(0, main([str(package), "--assurance-only"]))

    def test_legacy_report_uses_canonical_version(self):
        report = validate_package(self.make_package())
        self.assertEqual("1.0", report["component_version"])
        self.assertEqual("1.0", report["assurance"]["component_version"])


if __name__ == "__main__":
    unittest.main()
