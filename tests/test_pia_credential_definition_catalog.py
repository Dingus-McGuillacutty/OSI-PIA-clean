from __future__ import annotations

import csv
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from software.intake.credential_definition_catalog import (
    DEFAULT_CATALOG,
    CredentialDefinitionCatalog,
)
from software.intake.credential_definition_review import (
    CredentialDefinitionReviewService,
    CredentialReviewRequest,
)


class PIACredentialDefinitionCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.catalog_root = (
            Path(self.temporary_directory.name) / "credential-catalog"
        )
        shutil.copytree(DEFAULT_CATALOG, self.catalog_root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _rows(self, filename: str) -> tuple[list[str], list[dict[str, str]]]:
        path = self.catalog_root / filename
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), list(reader)

    def _write(
        self,
        filename: str,
        headers: list[str],
        rows: list[dict[str, str]],
    ) -> None:
        path = self.catalog_root / filename
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def _update(
        self,
        filename: str,
        id_field: str,
        record_id: str,
        **updates: str,
    ) -> None:
        headers, rows = self._rows(filename)
        for row in rows:
            if row[id_field] == record_id:
                row.update(updates)
                self._write(filename, headers, rows)
                return
        self.fail(f"{record_id!r} was not found in {filename!r}")

    def _append(self, filename: str, row: dict[str, str]) -> None:
        headers, rows = self._rows(filename)
        rows.append({field: row.get(field, "") for field in headers})
        self._write(filename, headers, rows)

    @staticmethod
    def _codes(report: dict[str, object]) -> set[str]:
        return {
            finding["code"]
            for finding in report["findings"]  # type: ignore[index]
        }

    def _accept_psp_definition(self) -> None:
        service = CredentialDefinitionReviewService(
            self.catalog_root,
            clock=lambda: datetime(
                2026, 7, 28, 23, 0, tzinfo=timezone.utc
            ),
        )
        service.apply(
            CredentialReviewRequest(
                credential_definition_id="CRED-DEF-ASIS-PSP-2022-001",
                reviewer_actor_id="credential-reviewer-local-001",
                reviewer_role="credential_definition_reviewer",
                decision="accepted_with_limits",
                review_basis=(
                    "Issuer body of knowledge and certification handbook "
                    "support the bounded definition."
                ),
                limitations=(
                    "Exact effective start date remains unstated; resolve a "
                    "completion period separately."
                ),
                sources_reviewed=True,
                boundary_reviewed=True,
            )
        )

    def test_seed_catalog_is_valid_and_participant_free(self) -> None:
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertTrue(report["valid"])
        self.assertEqual(report["summary"]["error"], 0)
        self.assertEqual(report["summary"]["records_checked"], 9)

    def test_seed_psp_candidate_requires_independent_review(self) -> None:
        catalog = CredentialDefinitionCatalog(self.catalog_root)
        result = catalog.resolve(
            "PSP",
            issuer_hint="ASIS",
            version_hint=(
                "Body of Knowledge updated 2022; exam updates introduced in late 2023"
            ),
        )
        self.assertEqual(
            result["resolution_status"], "definition_found_pending_review"
        )
        self.assertEqual(result["knowledge_status"], "source_defined")
        self.assertEqual(
            result["candidate_credential_definition_ids"],
            ["CRED-DEF-ASIS-PSP-2022-001"],
        )
        self.assertEqual(result["participant_claims_established"], [])
        self.assertEqual(
            result["expansion_queue_proposal"]["reason_code"],
            "definition_pending_review",
        )

    def test_independently_reviewed_definition_can_resolve(self) -> None:
        self._accept_psp_definition()
        catalog = CredentialDefinitionCatalog(self.catalog_root)
        self.assertTrue(catalog.validate()["valid"])
        result = catalog.resolve("Physical Security Professional", issuer_hint="ASIS")
        self.assertEqual(result["resolution_status"], "resolved")
        self.assertEqual(
            result["credential_definition_id"],
            "CRED-DEF-ASIS-PSP-2022-001",
        )
        self.assertNotIn("expansion_queue_proposal", result)

    def test_unknown_title_produces_minimized_expansion_proposal(self) -> None:
        result = CredentialDefinitionCatalog(self.catalog_root).resolve(
            "Synthetic Unknown Credential",
            issuer_hint="Synthetic Public Issuer",
        )
        self.assertEqual(result["resolution_status"], "source_needed")
        queue = result["expansion_queue_proposal"]
        self.assertEqual(queue["reason_code"], "source_needed")
        self.assertNotIn("participant_id", queue)
        self.assertNotIn("completion_date", queue)
        self.assertNotIn("certificate_number", queue)

    def test_known_family_with_wrong_version_stays_version_unknown(self) -> None:
        result = CredentialDefinitionCatalog(self.catalog_root).resolve(
            "PSP",
            issuer_hint="ASIS",
            version_hint="Unresolved historical edition",
        )
        self.assertEqual(result["resolution_status"], "version_unknown")
        self.assertEqual(
            result["expansion_queue_proposal"]["reason_code"], "version_unknown"
        )

    def test_title_collision_is_not_silently_collapsed(self) -> None:
        self._accept_psp_definition()
        self._append(
            "credential_issuer.csv",
            {
                "credential_issuer_id": "CRED-ISS-SYNTHETIC-001",
                "canonical_name": "Synthetic Public Credential Board",
                "aliases": "SPCB",
                "homepage_uri": "https://example.org/",
                "jurisdiction": "test-only",
                "review_status": "accepted",
                "created_at": "2026-07-28T23:00:00Z",
                "updated_at": "2026-07-28T23:00:00Z",
            },
        )
        self._append(
            "credential_family.csv",
            {
                "credential_family_id": "CRED-FAM-SYNTHETIC-PSP",
                "credential_issuer_id": "CRED-ISS-SYNTHETIC-001",
                "canonical_title": "Physical Security Professional",
                "acronym": "PSP",
                "aliases": "",
                "credential_type": "certification",
                "review_status": "accepted",
                "created_at": "2026-07-28T23:00:00Z",
                "updated_at": "2026-07-28T23:00:00Z",
            },
        )
        catalog = CredentialDefinitionCatalog(self.catalog_root)
        self.assertTrue(catalog.validate()["valid"])
        ambiguous = catalog.resolve("PSP")
        self.assertEqual(ambiguous["resolution_status"], "ambiguous_title")
        resolved = catalog.resolve("PSP", issuer_hint="ASIS")
        self.assertEqual(resolved["resolution_status"], "resolved")

    def test_accepted_definition_requires_matching_review_record(self) -> None:
        self._update(
            "credential_definition.csv",
            "credential_definition_id",
            "CRED-DEF-ASIS-PSP-2022-001",
            review_status="accepted",
            last_reviewed="2026-07-28",
            review_cycle="annual",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn("ACCEPTED_DEFINITION_REVIEW_MISSING", self._codes(report))

    def test_issuer_verified_requires_reviewed_issuer_source(self) -> None:
        self._update(
            "credential_definition.csv",
            "credential_definition_id",
            "CRED-DEF-ASIS-PSP-2022-001",
            definition_status="issuer_verified",
            definition_expansion_required="false",
            next_action="",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn("ISSUER_VERIFIED_BOUNDARY_INVALID", self._codes(report))

    def test_accepted_with_limits_review_must_state_limit(self) -> None:
        self._append(
            "credential_definition_review.csv",
            {
                "credential_definition_review_id": "CRED-REV-ASIS-PSP-001",
                "target_record_type": "credential_definition",
                "target_record_id": "CRED-DEF-ASIS-PSP-2022-001",
                "reviewer_role": "credential_definition_reviewer",
                "reviewer_actor_id": "credential-reviewer-local-001",
                "decision": "accepted_with_limits",
                "review_basis": "Synthetic review exercise.",
                "limitations": "",
                "reviewed_at": "2026-07-28T23:00:00Z",
            },
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn("LIMITED_REVIEW_WITHOUT_LIMIT", self._codes(report))

    def test_participant_label_is_blocked_from_public_queue(self) -> None:
        self._update(
            "credential_definition_expansion_queue.csv",
            "definition_expansion_item_id",
            "CRED-EXP-ASIS-PSP-REVIEW-001",
            credential_title="Participant " + "001 private credential",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn(
            "RESTRICTED_VALUE_PARTICIPANT_LABEL",
            self._codes(report),
        )

    def test_private_local_path_is_blocked_from_catalog(self) -> None:
        self._update(
            "credential_definition_source.csv",
            "credential_definition_source_id",
            "CRED-SRC-ASIS-PSP-BOK-2022-001",
            snapshot_reference=r"C:\Users\Example\private-source.pdf",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn(
            "RESTRICTED_VALUE_LOCAL_PRIVATE_PATH",
            self._codes(report),
        )

    def test_accessible_source_requires_valid_fingerprint(self) -> None:
        self._update(
            "credential_definition_source.csv",
            "credential_definition_source_id",
            "CRED-SRC-ASIS-PSP-BOK-2022-001",
            content_checksum="sha256:not-a-fingerprint",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn("SOURCE_CHECKSUM_INVALID", self._codes(report))

    def test_inaccessible_source_may_lack_content_fingerprint(self) -> None:
        self._update(
            "credential_definition_source.csv",
            "credential_definition_source_id",
            "CRED-SRC-ASIS-PSP-BOK-2022-001",
            access_status="inaccessible",
            content_checksum="",
            content_size_bytes="",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertTrue(report["valid"])

    def test_broken_domain_source_reference_is_blocking(self) -> None:
        self._update(
            "credential_domain_element.csv",
            "credential_domain_element_id",
            "CRED-DOM-ASIS-PSP-2022-001",
            source_ids="CRED-SRC-DOES-NOT-EXIST-001",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn("FOREIGN_KEY_UNRESOLVED", self._codes(report))

    def test_definition_supersession_cycle_is_blocking(self) -> None:
        self._update(
            "credential_definition.csv",
            "credential_definition_id",
            "CRED-DEF-ASIS-PSP-2022-001",
            supersedes_credential_definition_id=(
                "CRED-DEF-ASIS-PSP-2022-001"
            ),
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertFalse(report["valid"])
        self.assertIn("SUPERSESSION_CYCLE", self._codes(report))

    def test_domain_weights_expose_incomplete_scope_without_false_precision(
        self,
    ) -> None:
        self._update(
            "credential_domain_element.csv",
            "credential_domain_element_id",
            "CRED-DOM-ASIS-PSP-2022-003",
            weight_percent="30",
        )
        report = CredentialDefinitionCatalog(self.catalog_root).validate()
        self.assertTrue(report["valid"])
        self.assertIn("DOMAIN_WEIGHTS_NOT_100", self._codes(report))


if __name__ == "__main__":
    unittest.main()
