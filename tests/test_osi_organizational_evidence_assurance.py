from __future__ import annotations

import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from software.framework.osi_component import Disposition
from software.importer.osi_organizational_evidence_assurance import (
    OSIOrganizationalEvidenceAssurance,
)


FIXTURE = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "osi-organizational-evidence-synthetic"


class OSIOrganizationalEvidenceAssuranceTests(unittest.TestCase):
    def package(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name) / "package"
        shutil.copytree(FIXTURE, destination)
        return destination

    @staticmethod
    def rewrite(path: Path, mutate) -> None:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
            headers = list(rows[0])
        mutate(rows)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def append_row(path: Path, row: dict[str, str]) -> None:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = list(reader.fieldnames or [])
            rows = list(reader)
        rows.append(row)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def test_valid_synthetic_package_passes(self) -> None:
        report = OSIOrganizationalEvidenceAssurance(self.package()).assure()
        self.assertEqual(report.overall_disposition, Disposition.PASS)

    def test_missing_evidence_provenance_blocks_package(self) -> None:
        package = self.package()
        self.rewrite(package / "evidence.csv", lambda rows: rows[0].update(source_id="OSI-SYN-SRC-999"))
        report = OSIOrganizationalEvidenceAssurance(package).assure()
        self.assertEqual(report.overall_disposition, Disposition.FAIL)
        self.assertIn("FK_SOURCE", {finding.code for finding in report.results[2].findings})

    def test_candidate_requires_negative_boundary(self) -> None:
        package = self.package()
        self.rewrite(package / "observation_candidate.csv", lambda rows: rows[0].update(negative_boundary=""))
        report = OSIOrganizationalEvidenceAssurance(package).assure()
        self.assertEqual(report.overall_disposition, Disposition.FAIL)
        self.assertIn("BOUNDARY_MISSING", {finding.code for finding in report.results[6].findings})

    def test_unreviewed_candidate_requires_human_review(self) -> None:
        package = self.package()
        self.rewrite(package / "observation_candidate.csv", lambda rows: rows[0].update(review_status="needs_review", reviewed_by=""))
        report = OSIOrganizationalEvidenceAssurance(package).assure()
        self.assertEqual(report.overall_disposition, Disposition.REQUIRES_HUMAN_REVIEW)
        self.assertIn("OBSERVATION_REVIEW_REQUIRED", {finding.code for finding in report.results[5].findings})

    def test_non_synthetic_identity_is_blocked(self) -> None:
        package = self.package()
        self.rewrite(package / "organization.csv", lambda rows: rows[0].update(organization_id="ORG-001"))
        report = OSIOrganizationalEvidenceAssurance(package).assure()
        self.assertEqual(report.overall_disposition, Disposition.FAIL)
        self.assertIn("SYNTHETIC_ID_INVALID", {finding.code for finding in report.results[5].findings})

    def test_contradictory_candidate_is_preserved_for_review(self) -> None:
        package = self.package()
        self.append_row(package / "observation_candidate.csv", {
            "observation_id": "OSI-SYN-OBS-004",
            "evidence_id": "OSI-SYN-EVD-001",
            "observation_text": "The same synthetic record is interpreted as showing that the documented handoff practice was not used.",
            "observation_type": "contradictory_observation",
            "confidence": "0.42",
            "confidence_basis": "A deliberately contradictory synthetic interpretation is introduced for review.",
            "review_status": "needs_review",
            "reviewed_by": "",
            "negative_boundary": "Does not establish which interpretation is correct, routine behavior, or outcome quality.",
            "created_at": "2026-08-02T00:00:00Z",
        })
        component = OSIOrganizationalEvidenceAssurance(package)
        report = component.assure()
        self.assertEqual(report.overall_disposition, Disposition.REQUIRES_HUMAN_REVIEW)
        self.assertEqual(len(component.data["observation_candidate.csv"]), 4)
        self.assertIn("OBSERVATION_REVIEW_REQUIRED", {finding.code for finding in report.results[5].findings})

    def test_confounded_candidates_remain_bounded(self) -> None:
        package = self.package()
        self.append_row(package / "observation_candidate.csv", {
            "observation_id": "OSI-SYN-OBS-005",
            "evidence_id": "OSI-SYN-EVD-002",
            "observation_text": "The concentrated routing condition may reflect either a temporary transition constraint or an established dependency pattern.",
            "observation_type": "confounded_observation",
            "confidence": "0.45",
            "confidence_basis": "The synthetic record is compatible with two bounded explanations and contains no duration measure.",
            "review_status": "accepted",
            "reviewed_by": "synthetic-reviewer",
            "negative_boundary": "Does not establish duration, cause, individual fault, or organizational performance.",
            "created_at": "2026-08-02T00:00:00Z",
        })
        component = OSIOrganizationalEvidenceAssurance(package)
        report = component.assure()
        self.assertEqual(report.overall_disposition, Disposition.PASS)
        self.assertEqual(len(component.data["observation_candidate.csv"]), 4)


if __name__ == "__main__":
    unittest.main()
