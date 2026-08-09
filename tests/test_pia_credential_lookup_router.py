from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from software.intake.credential_definition_catalog import DEFAULT_CATALOG
from software.intake.credential_definition_review import (
    CredentialDefinitionReviewService,
    CredentialReviewRequest,
)
from software.intake.credential_lookup_router import (
    DEFAULT_LOOKUP_CONTRACT,
    CredentialLookupError,
    CredentialLookupRouter,
)


DEFINITION_ID = "CRED-DEF-ASIS-PSP-2022-001"


class PIACredentialLookupRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.catalog_root = Path(self.temporary_directory.name) / "catalog"
        shutil.copytree(DEFAULT_CATALOG, self.catalog_root)
        self.router = CredentialLookupRouter(self.catalog_root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _rows(self, filename: str) -> tuple[list[str], list[dict[str, str]]]:
        with (self.catalog_root / filename).open(
            "r", encoding="utf-8", newline=""
        ) as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), list(reader)

    def _write(
        self,
        filename: str,
        headers: list[str],
        rows: list[dict[str, str]],
    ) -> None:
        with (self.catalog_root / filename).open(
            "w", encoding="utf-8", newline=""
        ) as handle:
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
        self.fail(f"{record_id!r} was not found.")

    def _accept_psp(self) -> None:
        service = CredentialDefinitionReviewService(
            self.catalog_root,
            clock=lambda: datetime(
                2026, 7, 29, 2, 0, tzinfo=timezone.utc
            ),
        )
        service.apply(
            CredentialReviewRequest(
                credential_definition_id=DEFINITION_ID,
                reviewer_actor_id="credential-reviewer-local-001",
                reviewer_role="credential_definition_reviewer",
                decision="accepted_with_limits",
                review_basis=(
                    "Issuer sources and all bounded domain elements were "
                    "independently reviewed for reference reuse."
                ),
                limitations=(
                    "Exact effective start and end dates remain unstated."
                ),
                sources_reviewed=True,
                boundary_reviewed=True,
            )
        )

    @staticmethod
    def lookup(**overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "credential_title": "PSP",
            "issuer_hint": "ASIS",
            "version_hint": "",
            "credential_type_hint": "certification",
            "jurisdiction_hint": "international",
            "source_scope": "pia_catalog_only",
            "purpose": "reference_definition_resolution",
        }
        value.update(overrides)
        return value

    def test_machine_contract_declares_strict_participant_free_boundary(
        self,
    ) -> None:
        contract = json.loads(
            DEFAULT_LOOKUP_CONTRACT.read_text(encoding="utf-8")
        )
        self.assertTrue(contract["contract"]["participant_data_prohibited"])
        self.assertFalse(contract["contract"]["phase_3b1_network_access"])
        self.assertEqual(contract["contract"]["phase_3b1_persistence"], "none")
        self.assertNotIn(
            "participant_id", contract["request"]["allowed_fields"]
        )
        self.assertIn(
            "completion_date",
            contract["request"]["prohibited_field_fragments"],
        )

    def test_existing_pending_package_routes_to_phase_3a_without_participant(
        self,
    ) -> None:
        result = self.router.route(self.lookup())
        self.assertEqual(
            result["routing_outcome"], "manual_definition_review"
        )
        self.assertFalse(result["participant_clarification_required"])
        self.assertEqual(
            result["public_catalog_action"], "use_existing_review_queue"
        )
        self.assertFalse(result["external_lookup_permitted"])
        self.assertEqual(result["participant_claims_established"], [])

    def test_accepted_definition_resolves_without_repeated_research(self) -> None:
        self._accept_psp()
        result = self.router.route(self.lookup())
        self.assertEqual(result["routing_outcome"], "resolved")
        self.assertEqual(result["credential_definition_id"], DEFINITION_ID)
        self.assertFalse(result["participant_clarification_required"])
        self.assertEqual(result["public_catalog_action"], "none")

    def test_unknown_credential_routes_to_future_external_lookup(self) -> None:
        result = self.router.route(
            self.lookup(
                credential_title="Synthetic Unknown Credential",
                issuer_hint="Synthetic Public Issuer",
            )
        )
        self.assertEqual(
            result["routing_outcome"], "external_registry_lookup"
        )
        self.assertFalse(result["external_lookup_permitted"])
        self.assertFalse(result["participant_clarification_required"])
        self.assertEqual(
            result["public_catalog_action"],
            "propose_participant_free_source_research",
        )
        self.assertIn("participant_free_queue_proposal", result)

    def test_wrong_version_requests_only_version_clarification(self) -> None:
        result = self.router.route(
            self.lookup(version_hint="Unresolved historical edition")
        )
        self.assertEqual(result["routing_outcome"], "confirm_version")
        self.assertTrue(result["participant_clarification_required"])
        self.assertIn("version", result["clarification_prompt"].casefold())
        self.assertEqual(result["public_catalog_action"], "none")

    def test_inaccessible_definition_routes_source_review(self) -> None:
        self._update(
            "credential_definition.csv",
            "credential_definition_id",
            DEFINITION_ID,
            definition_status="inaccessible_definition",
            next_action="Locate an accessible issuer source.",
        )
        result = self.router.route(self.lookup())
        self.assertEqual(result["routing_outcome"], "source_access_review")
        self.assertFalse(result["participant_clarification_required"])

    def test_material_conflict_routes_assurance_review(self) -> None:
        self._update(
            "credential_definition.csv",
            "credential_definition_id",
            DEFINITION_ID,
            definition_status="conflicting_definition",
            source_conflict_status="material",
            next_action="Resolve the material issuer-source conflict.",
        )
        result = self.router.route(self.lookup())
        self.assertEqual(result["routing_outcome"], "conflict_review")
        self.assertFalse(result["participant_clarification_required"])

    def test_request_identity_is_deterministic_and_normalized(self) -> None:
        first = self.router.route(self.lookup())
        second = self.router.route(
            self.lookup(
                credential_title="  psp ",
                issuer_hint="asis",
                jurisdiction_hint="INTERNATIONAL",
            )
        )
        self.assertEqual(
            first["request_fingerprint"], second["request_fingerprint"]
        )
        self.assertEqual(
            first["lookup_request_id"], second["lookup_request_id"]
        )

    def test_participant_and_private_fields_are_rejected_not_stripped(
        self,
    ) -> None:
        prohibited = (
            ("participant_id", "PIA-9001"),
            ("intake_session_id", "PIA-9001-INT-001"),
            ("certificate_number", "12345"),
            ("completion_date", "2025-01-01"),
            ("participant_note", "Private context"),
            ("document_path", r"C:\private\credential.pdf"),
        )
        for field, value in prohibited:
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    CredentialLookupError, "prohibited"
                ):
                    self.router.route(self.lookup(**{field: value}))

    def test_private_looking_values_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            CredentialLookupError, "privacy boundary"
        ):
            self.router.route(
                self.lookup(credential_title="Participant " + "001 credential")
            )
        with self.assertRaisesRegex(
            CredentialLookupError, "privacy boundary"
        ):
            self.router.route(
                self.lookup(issuer_hint="person@example.org")
            )
        with self.assertRaisesRegex(
            CredentialLookupError, "privacy boundary"
        ):
            self.router.route(
                self.lookup(version_hint=r"C:\Users\Example\private.pdf")
            )

    def test_arbitrary_unknown_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(CredentialLookupError, "not permitted"):
            self.router.route(self.lookup(unexpected_context="value"))


if __name__ == "__main__":
    unittest.main()
