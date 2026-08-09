from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from software.intake.validate_pia_intake_phase1 import validate_package


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPOSITORY_ROOT
    / "data"
    / "contracts"
    / "pia_intake_phase1_contract_v0.1.json"
)
FIXTURE_PATH = (
    REPOSITORY_ROOT
    / "data"
    / "fixtures"
    / "pia-intake-phase1-synthetic"
)
TEMPLATE_PATH = REPOSITORY_ROOT / "data" / "templates" / "pia-intake-v0.1"


def rewrite_row(
    package: Path,
    file_name: str,
    row_index: int,
    updates: dict[str, str],
) -> None:
    path = package / file_name
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        rows = list(reader)
    rows[row_index].update(updates)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


class PIAIntakePhase1ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def copied_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        package = Path(temporary.name) / "package"
        shutil.copytree(FIXTURE_PATH, package)
        return temporary, package

    def test_synthetic_fixture_is_accepted_with_routed_review(self) -> None:
        result = validate_package(
            FIXTURE_PATH,
            CONTRACT_PATH,
            repository_fixture=True,
        )
        self.assertTrue(result["accepted"])
        self.assertEqual(result["counts"]["files"], 8)
        self.assertEqual(result["counts"]["records"], 13)
        self.assertEqual(result["counts"]["errors"], 0)
        self.assertIn(
            "DEFINITION_REVIEW_ROUTED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_empty_templates_exactly_match_machine_contract(self) -> None:
        for file_name in self.contract["required_files"]:
            with (TEMPLATE_PATH / file_name).open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                headers = next(csv.reader(handle))
            self.assertEqual(headers, self.contract["files"][file_name]["headers"])

    def test_repository_fixture_rejects_non_synthetic_participant(self) -> None:
        temporary, package = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        non_synthetic_participant_id = "-".join(("PIA", "1001"))
        rewrite_row(
            package,
            "intake_session.csv",
            0,
            {"participant_id": non_synthetic_participant_id},
        )
        result = validate_package(
            package,
            CONTRACT_PATH,
            repository_fixture=True,
        )
        self.assertFalse(result["accepted"])
        self.assertIn(
            "REPOSITORY_PARTICIPANT_DATA_PROHIBITED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_unresolved_definition_must_be_safely_routed(self) -> None:
        temporary, package = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        rewrite_row(
            package,
            "credential_definition.csv",
            1,
            {
                "definition_expansion_required": "false",
                "next_action": "",
            },
        )
        result = validate_package(package, CONTRACT_PATH, repository_fixture=True)
        self.assertFalse(result["accepted"])
        self.assertIn(
            "UNRESOLVED_DEFINITION_NOT_ROUTED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_issuer_verified_definition_requires_definition_source(self) -> None:
        temporary, package = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        rewrite_row(
            package,
            "credential_definition.csv",
            0,
            {"primary_source_artifact_ids": ""},
        )
        result = validate_package(package, CONTRACT_PATH, repository_fixture=True)
        self.assertFalse(result["accepted"])
        self.assertIn(
            "RESOLVED_DEFINITION_INCOMPLETE",
            {finding["code"] for finding in result["findings"]},
        )

    def test_review_target_must_resolve(self) -> None:
        temporary, package = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        rewrite_row(
            package,
            "review_event.csv",
            0,
            {"target_record_id": "PIA-9001-APP-999"},
        )
        result = validate_package(package, CONTRACT_PATH, repository_fixture=True)
        self.assertFalse(result["accepted"])
        self.assertIn(
            "DYNAMIC_TARGET_UNRESOLVED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_projection_scope_count_must_match_selection(self) -> None:
        temporary, package = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        rewrite_row(
            package,
            "projection_manifest.csv",
            0,
            {"record_count": "3"},
        )
        result = validate_package(package, CONTRACT_PATH, repository_fixture=True)
        self.assertFalse(result["accepted"])
        self.assertIn(
            "PROJECTION_COUNT_MISMATCH",
            {finding["code"] for finding in result["findings"]},
        )

    def test_supersession_cannot_self_reference(self) -> None:
        temporary, package = self.copied_fixture()
        self.addCleanup(temporary.cleanup)
        rewrite_row(
            package,
            "credential_definition_queue.csv",
            0,
            {"supersedes_queue_item_id": "PIA-9001-QUE-001"},
        )
        result = validate_package(package, CONTRACT_PATH, repository_fixture=True)
        self.assertFalse(result["accepted"])
        self.assertIn(
            "SUPERSESSION_SELF_REFERENCE",
            {finding["code"] for finding in result["findings"]},
        )

    def test_definition_identity_and_queue_state_axes_remain_distinct(self) -> None:
        definition_headers = self.contract["files"]["credential_definition.csv"][
            "headers"
        ]
        queue_headers = self.contract["files"]["credential_definition_queue.csv"][
            "headers"
        ]
        self.assertNotIn("participant_id", definition_headers)
        self.assertIn("processing_state", queue_headers)
        self.assertIn("knowledge_status", queue_headers)
        self.assertIn("review_disposition", queue_headers)


if __name__ == "__main__":
    unittest.main()
