from __future__ import annotations

import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "fixtures" / "osi-organizational-evidence-synthetic"
MAP = ROOT / "docs" / "evidence" / "case_data_map.csv"


class OSICaseDataMapTests(unittest.TestCase):
    def read_ids(self, filename: str, field: str) -> set[str]:
        with (FIXTURE / filename).open(encoding="utf-8", newline="") as handle:
            return {row[field] for row in csv.DictReader(handle)}

    def test_mapped_case_ids_resolve_to_fixture_records(self) -> None:
        source_ids = self.read_ids("source.csv", "source_id")
        evidence_ids = self.read_ids("evidence.csv", "evidence_id")
        observation_ids = self.read_ids("observation_candidate.csv", "observation_id")
        with MAP.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(
            {row["case_id"] for row in rows},
            {"evidence-osi-case-001", "evidence-osi-case-002", "evidence-osi-case-003"},
        )
        for row in rows:
            if row["mapping_status"] == "not_instantiated":
                self.assertFalse(row["source_id"] or row["evidence_id"] or row["observation_id"])
                continue
            self.assertIn(row["source_id"], source_ids)
            self.assertIn(row["evidence_id"], evidence_ids)
            self.assertIn(row["observation_id"], observation_ids)
            self.assertTrue(row["negative_boundary"])


if __name__ == "__main__":
    unittest.main()
