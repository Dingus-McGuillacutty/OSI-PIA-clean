from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from software.framework.osi_component import Disposition
from software.importer.osi_pia_validate import CSVAssuranceEngine, validate_package


VALID_PACKAGE = {
    "participant.csv": (
        ["participant_id", "status", "consent_status", "created_at", "updated_at"],
        [["PIA-9001", "active", "granted", "2026-07-01", "2026-07-01"]],
    ),
    "source.csv": (
        ["source_id", "participant_id", "source_type", "collected_at", "confidentiality"],
        [["PIA-9001-SRC-001", "PIA-9001", "interview", "2026-07-01", "restricted"]],
    ),
    "experience.csv": (
        ["experience_id", "participant_id", "experience_type", "title", "date_status"],
        [["PIA-9001-EXP-001", "PIA-9001", "employment", "Example role", "known"]],
    ),
    "evidence.csv": (
        [
            "evidence_id", "source_id", "participant_id", "experience_id",
            "evidence_text", "evidence_type", "extraction_method",
            "fidelity_status", "review_status", "source_locator", "created_at",
        ],
        [[
            "PIA-9001-EVD-001", "PIA-9001-SRC-001", "PIA-9001",
            "PIA-9001-EXP-001", "Built a working system.", "achievement",
            "manual", "verbatim", "reviewed", "interview:line-12", "2026-07-01",
        ]],
    ),
    "capability.csv": (
        ["capability_id", "capability_name", "definition", "status", "ontology_version"],
        [["CAP-SYSTEMS", "Systems thinking", "Recognizes interacting structures.", "working", "0.1"]],
    ),
    "evidence_capability_mapping.csv": (
        [
            "mapping_id", "evidence_id", "capability_id", "relationship_type",
            "confidence", "confidence_basis", "proposed_by", "review_status", "created_at",
        ],
        [[
            "PIA-9001-MAP-001", "PIA-9001-EVD-001", "CAP-SYSTEMS", "SUPPORTS",
            "0.80", "Direct evidence", "human", "accepted", "2026-07-01",
        ]],
    ),
}


def write_package(root: Path, overrides: dict | None = None, omit: set[str] | None = None) -> None:
    package = dict(VALID_PACKAGE)
    package.update(overrides or {})
    omit = omit or set()

    for filename, (headers, rows) in package.items():
        if filename in omit:
            continue
        with (root / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)


class CSVAssuranceEngineTests(unittest.TestCase):
    def make_package(self, overrides: dict | None = None, omit: set[str] | None = None):
        temporary = tempfile.TemporaryDirectory()
        path = Path(temporary.name)
        write_package(path, overrides=overrides, omit=omit)
        self.addCleanup(temporary.cleanup)
        return path

    def result_map(self, engine: CSVAssuranceEngine):
        return {result.dimension: result for result in engine.assure().results}

    def test_valid_minimal_package_passes(self):
        package = self.make_package()
        engine = CSVAssuranceEngine(package)
        report = engine.assure()

        self.assertEqual(report.overall_disposition, Disposition.PASS)
        self.assertTrue(validate_package(package)["accepted"])
        self.assertEqual(validate_package(package)["summary"]["errors"], 0)

    def test_missing_file_fails_contract_and_legacy_gate(self):
        package = self.make_package(omit={"source.csv"})
        engine = CSVAssuranceEngine(package)
        results = self.result_map(engine)

        self.assertEqual(results["contract"].disposition, Disposition.FAIL)
        self.assertFalse(validate_package(package)["accepted"])
        self.assertIn("FILE_MISSING", {f.code for f in results["contract"].findings})

    def test_invalid_foreign_key_fails_congruence(self):
        headers, rows = VALID_PACKAGE["evidence.csv"]
        broken = [list(rows[0])]
        broken[0][1] = "PIA-9001-SRC-999"
        package = self.make_package(overrides={"evidence.csv": (headers, broken)})
        result = self.result_map(CSVAssuranceEngine(package))["congruence"]

        self.assertEqual(result.disposition, Disposition.FAIL)
        self.assertIn("FK_SOURCE", {f.code for f in result.findings})

    def test_repeated_foreign_keys_are_not_reported_as_duplicate_primary_ids(self):
        source_headers, source_rows = VALID_PACKAGE["source.csv"]
        sources = [list(source_rows[0])]
        sources.append(
            ["PIA-9001-SRC-002", "PIA-9001", "portfolio", "2026-07-02", "restricted"]
        )

        evidence_headers, evidence_rows = VALID_PACKAGE["evidence.csv"]
        evidence = [list(evidence_rows[0])]
        second_evidence = list(evidence_rows[0])
        second_evidence[evidence_headers.index("evidence_id")] = "PIA-9001-EVD-002"
        second_evidence[evidence_headers.index("evidence_text")] = "Documented a second record."
        second_evidence[evidence_headers.index("source_locator")] = "interview:line-13"
        evidence.append(second_evidence)

        package = self.make_package(
            overrides={
                "source.csv": (source_headers, sources),
                "evidence.csv": (evidence_headers, evidence),
            }
        )
        report = validate_package(package)

        self.assertTrue(report["accepted"])
        self.assertNotIn(
            "ID_DUPLICATE",
            {finding["code"] for finding in report["findings"]},
        )

    def test_missing_locator_is_epistemic_warning_not_blocking_error(self):
        headers, rows = VALID_PACKAGE["evidence.csv"]
        changed = [list(rows[0])]
        changed[0][headers.index("source_locator")] = ""
        package = self.make_package(overrides={"evidence.csv": (headers, changed)})
        engine = CSVAssuranceEngine(package)
        results = self.result_map(engine)

        self.assertEqual(
            results["epistemic_integrity"].disposition,
            Disposition.PASS_WITH_WARNINGS,
        )
        self.assertTrue(validate_package(package)["accepted"])

    def test_every_finding_has_traceable_logic_chain(self):
        package = self.make_package(omit={"source.csv"})
        engine = CSVAssuranceEngine(package)
        engine.assure()

        self.assertGreater(len(engine.findings), 0)
        for finding in engine.findings:
            with self.subTest(code=finding.code):
                self.assertTrue(finding.rule_id)
                self.assertTrue(finding.dimension)
                self.assertTrue(finding.reference())
                self.assertTrue(finding.logic_chain)
                self.assertGreaterEqual(len(finding.logic_chain), 3)

    def test_assurance_dimensions_are_complete_and_stable(self):
        package = self.make_package()
        dimensions = [result.dimension for result in CSVAssuranceEngine(package).assure().results]

        self.assertEqual(
            dimensions,
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
        )


if __name__ == "__main__":
    unittest.main()
