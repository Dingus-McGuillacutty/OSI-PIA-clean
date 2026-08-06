from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from software.framework.osi_component import Disposition
from software.importer.csv_assurance_engine import CSVAssuranceEngine


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


class CompletedCSVAssuranceEngineTests(unittest.TestCase):
    def make_engine(self, consent_status: str = "granted") -> CSVAssuranceEngine:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        write_package(root, consent_status)
        return CSVAssuranceEngine(root)

    def result_for(self, engine: CSVAssuranceEngine, dimension: str):
        report = engine.assure()
        return next(result for result in report.results if result.dimension == dimension)

    def test_complete_valid_package_passes_all_runtime_gates(self):
        engine = self.make_engine()
        report = engine.assure()
        dispositions = {result.dimension: result.disposition for result in report.results}
        self.assertEqual(Disposition.PASS, dispositions["contract"])
        self.assertEqual(Disposition.PASS, dispositions["validation"])
        self.assertEqual(Disposition.PASS, dispositions["congruence"])
        self.assertEqual(Disposition.PASS, dispositions["regression"])
        self.assertEqual(Disposition.PASS, dispositions["performance"])
        self.assertEqual(Disposition.PASS, dispositions["ethics"])
        self.assertEqual(Disposition.PASS, dispositions["epistemic_integrity"])
        self.assertEqual(Disposition.PASS, dispositions["audit"])
        self.assertEqual(Disposition.PASS, report.overall_disposition)

    def test_withdrawn_consent_blocks_import(self):
        engine = self.make_engine("withdrawn")
        ethics = self.result_for(engine, "ethics")
        self.assertEqual(Disposition.FAIL, ethics.disposition)
        self.assertEqual("CONSENT_WITHDRAWN", ethics.findings[0].code)
        self.assertEqual(Disposition.FAIL, engine.assure().overall_disposition)

    def test_pending_and_limited_consent_require_human_review(self):
        for consent_status in ("pending", "limited"):
            with self.subTest(consent_status=consent_status):
                engine = self.make_engine(consent_status)
                ethics = self.result_for(engine, "ethics")
                self.assertEqual(Disposition.REQUIRES_HUMAN_REVIEW, ethics.disposition)
                self.assertEqual("CONSENT_REVIEW_REQUIRED", ethics.findings[0].code)

    def test_regression_gate_preserves_legacy_acceptance_parity(self):
        engine = self.make_engine()
        regression = self.result_for(engine, "regression")
        self.assertEqual(Disposition.PASS, regression.disposition)
        self.assertTrue(regression.metrics["canonical_accepted"])
        self.assertTrue(regression.metrics["compatibility_accepted"])
        self.assertEqual(0, regression.metrics["canonical_errors"])
        self.assertEqual(0, regression.metrics["compatibility_errors"])

    def test_epistemic_gate_inspects_every_emitted_finding(self):
        engine = self.make_engine()
        epistemic = self.result_for(engine, "epistemic_integrity")
        self.assertEqual(len(engine.findings), epistemic.metrics["findings_inspected"])
        self.assertEqual(0, epistemic.metrics["input_mutations"])

    def test_audit_gate_emits_versioned_summary(self):
        engine = self.make_engine()
        audit = self.result_for(engine, "audit")
        self.assertEqual("1.0", audit.metrics["component_version"])
        self.assertEqual(engine.contract_version, audit.metrics["contract_version"])
        self.assertIn("finding_count", audit.metrics)
        self.assertIn("findings_by_dimension", audit.metrics)
        self.assertIn("findings_by_severity", audit.metrics)


if __name__ == "__main__":
    unittest.main()
