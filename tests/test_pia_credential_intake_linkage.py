from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from software.intake.credential_intake_linkage import CredentialIntakeLinkage
from software.intake.credential_lookup_router import CredentialLookupRouter
from software.intake.credential_registry_connector import (
    PRODUCTION_ENDPOINT,
    CredentialEngineSearchConnector,
    CredentialRegistryError,
)
from software.intake.local_private_intake import IntakePreflightError
from software.intake.phase2b_security import MalwareScanResult, utc_now
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)


class FakeScanner:
    provider_name = "test-in-memory-scanner"

    def preflight(self) -> MalwareScanResult:
        return MalwareScanResult(
            status="clean",
            provider=self.provider_name,
            result_code=0,
            scanned_at=utc_now(),
        )

    def scan(self, content: bytes, *, content_name: str) -> MalwareScanResult:
        return self.preflight()


def fake_acl_hardener(root: Path) -> dict[str, str]:
    return {
        "acl_state": "test-restricted-current-user-and-system",
        "identity": "test-owner",
    }


class FakeRegistryConnector:
    connector_id = "connector-test-public-registry-001"
    registry_name = "Synthetic Public Credential Registry"

    def __init__(self) -> None:
        self.requests = []

    def search(self, request: Any) -> dict[str, Any]:
        self.requests.append(request)
        return {
            "connector_id": self.connector_id,
            "registry_name": self.registry_name,
            "registry_environment": "test",
            "retrieved_at": "2026-07-29T00:00:00Z",
            "query_fingerprint": "sha256:" + ("1" * 64),
            "total_results": 1,
            "candidates": [
                {
                    "external_identity": "ce-synthetic-public-record",
                    "resource_uri": (
                        "https://credentialengineregistry.org/resources/"
                        "ce-synthetic-public-record"
                    ),
                    "credential_name": "Synthetic Public Credential",
                    "credential_types": ["ceterms:Certification"],
                    "description": "A synthetic public test record.",
                    "candidate_fingerprint": "sha256:" + ("2" * 64),
                }
            ],
            "disposition": "candidates_pending_phase3a_review",
            "definition_accepted": False,
            "participant_claims_established": [],
            "boundary": "Candidate only.",
        }


class PIACredentialIntakeLinkageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.store_root = root / "participant-store"
        self.store = ProtectedParticipantIntakeStore.create(
            self.store_root,
            owner_passphrase="owner-passphrase-for-tests",
            recovery_path=root / "offline" / "recovery.json",
            recovery_passphrase="recovery-passphrase-for-tests",
            scanner=FakeScanner(),
            acl_hardener=fake_acl_hardener,
        )

    def create_session(
        self,
        *,
        scope: str = (
            "credential_definition|capability_mapping|report_generation"
        ),
    ) -> dict[str, Any]:
        return self.store.create_session(
            participant_label="Synthetic Intake Subject Alpha",
            purpose="Synthetic credential linkage test",
            processing_scope=scope,
            consent_status="granted",
            confidentiality="participant_private",
            retention_class="30_days",
            actor_subject="local-owner",
            actor_role="owner",
        )

    @staticmethod
    def descriptor(**overrides: Any) -> dict[str, Any]:
        value = {
            "credential_title": "PSP",
            "issuer_hint": "ASIS",
            "version_hint": "",
            "credential_type_hint": "certification",
            "jurisdiction_hint": "international",
        }
        value.update(overrides)
        return value

    def test_catalog_first_result_is_stored_only_in_encrypted_session(
        self,
    ) -> None:
        session = self.create_session()
        service = CredentialIntakeLinkage(self.store)
        result = service.resolve(
            session_id=session["intake_session_id"],
            descriptor=self.descriptor(),
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(result["routing_outcome"], "manual_definition_review")
        self.assertEqual(result["participant_claims_established"], [])
        self.assertEqual(
            result["external_lookup_disposition"], "not_needed"
        )
        protected = (
            self.store_root
            / "sessions"
            / session["intake_session_id"]
            / "session.piaenc"
        ).read_bytes()
        self.assertNotIn(b"PSP", protected)
        self.assertNotIn(b"ASIS", protected)
        validation = self.store.validate()
        self.assertTrue(validation["accepted"])
        self.assertEqual(validation["counts"]["credential_resolutions"], 1)

    def test_unknown_credential_uses_optional_public_connector(
        self,
    ) -> None:
        session = self.create_session()
        connector = FakeRegistryConnector()
        service = CredentialIntakeLinkage(
            self.store,
            connector=connector,
        )
        result = service.resolve(
            session_id=session["intake_session_id"],
            descriptor=self.descriptor(
                credential_title="Synthetic Public Credential",
                issuer_hint="Synthetic Public Issuer",
            ),
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(
            result["routing_outcome"], "external_registry_lookup"
        )
        self.assertEqual(
            result["external_lookup_disposition"],
            "candidates_pending_phase3a_review",
        )
        self.assertEqual(result["external_candidate_count"], 1)
        self.assertEqual(result["participant_claims_established"], [])
        request = connector.requests[0]
        self.assertEqual(
            set(request.__dict__),
            {
                "credential_title",
                "issuer_hint",
                "version_hint",
                "credential_type_hint",
                "jurisdiction_hint",
                "source_scope",
                "purpose",
            },
        )

    def test_unknown_credential_remains_manual_without_connector(self) -> None:
        session = self.create_session()
        service = CredentialIntakeLinkage(self.store)
        result = service.resolve(
            session_id=session["intake_session_id"],
            descriptor=self.descriptor(
                credential_title="Synthetic Unlisted Credential",
                issuer_hint="Synthetic Public Issuer",
            ),
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(
            result["external_lookup_disposition"],
            "connector_not_configured",
        )
        self.assertIn("manual", result["next_action"].casefold())

    def test_version_clarification_is_private_and_reroutes(self) -> None:
        session = self.create_session()
        service = CredentialIntakeLinkage(self.store)
        first = service.resolve(
            session_id=session["intake_session_id"],
            descriptor=self.descriptor(
                version_hint="Unresolved historical edition"
            ),
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertTrue(first["participant_clarification_required"])
        self.assertEqual(first["routing_outcome"], "confirm_version")

        second = service.clarify(
            session_id=session["intake_session_id"],
            credential_entry_id=first["credential_entry_id"],
            field="version_hint",
            response=(
                "Body of Knowledge updated 2022; exam updates introduced "
                "in late 2023"
            ),
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(
            second["routing_outcome"], "manual_definition_review"
        )
        stored = self.store.get_credential_resolution(
            session["intake_session_id"],
            credential_entry_id=first["credential_entry_id"],
            actor_role="owner",
        )
        self.assertEqual(len(stored["clarification_history"]), 1)
        self.assertEqual(
            stored["clarification_history"][0]["field"], "version_hint"
        )

    def test_scope_and_withdrawal_block_credential_resolution(self) -> None:
        without_scope = self.create_session(scope="report_generation")
        service = CredentialIntakeLinkage(self.store)
        with self.assertRaisesRegex(IntakePreflightError, "scope"):
            service.resolve(
                session_id=without_scope["intake_session_id"],
                descriptor=self.descriptor(),
                actor_subject="local-owner",
                actor_role="owner",
            )

        active = self.create_session()
        self.store.withdraw_session(
            active["intake_session_id"],
            reason="Synthetic withdrawal test.",
            actor_subject="local-owner",
            actor_role="owner",
        )
        with self.assertRaisesRegex(IntakePreflightError, "authorized"):
            service.resolve(
                session_id=active["intake_session_id"],
                descriptor=self.descriptor(),
                actor_subject="local-owner",
                actor_role="owner",
            )

    def test_status_returns_private_session_relationship_only(self) -> None:
        session = self.create_session()
        service = CredentialIntakeLinkage(self.store)
        created = service.resolve(
            session_id=session["intake_session_id"],
            descriptor=self.descriptor(),
            actor_subject="local-owner",
            actor_role="owner",
        )
        status = service.status(
            session_id=session["intake_session_id"],
            actor_role="reviewer",
        )
        self.assertEqual(
            [item["credential_entry_id"] for item in status],
            [created["credential_entry_id"]],
        )


class PIACredentialEngineConnectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = CredentialLookupRouter().request_from_mapping(
            {
                "credential_title": "Synthetic Public Credential",
                "issuer_hint": "Synthetic Public Issuer",
                "version_hint": "",
                "credential_type_hint": "certification",
                "jurisdiction_hint": "international",
                "source_scope": "pia_catalog_only",
                "purpose": "reference_definition_resolution",
            }
        )

    def test_connector_uses_allowlisted_server_endpoint_and_hides_key(
        self,
    ) -> None:
        calls = []

        def transport(
            endpoint: str,
            headers: dict[str, str],
            payload: dict[str, Any],
            timeout: int,
        ) -> dict[str, Any]:
            calls.append((endpoint, headers, payload, timeout))
            return {
                "TotalResults": 1,
                "Results": [
                    {
                        "@id": (
                            "https://credentialengineregistry.org/resources/"
                            "ce-synthetic"
                        ),
                        "@type": ["ceterms:Certification"],
                        "ceterms:ctid": "ce-synthetic",
                        "ceterms:name": {
                            "en-US": "Synthetic Public Credential"
                        },
                        "ceterms:description": {
                            "en-US": "Synthetic description."
                        },
                        "ceterms:ownedBy": [
                            {
                                "@id": (
                                    "https://credentialengineregistry.org/"
                                    "resources/ce-synthetic-issuer"
                                )
                            }
                        ],
                    }
                ],
                "ResultsMetadata": [
                    {
                        "ResourceURI": (
                            "https://credentialengineregistry.org/resources/"
                            "ce-synthetic"
                        ),
                        "RecordPublishType": "primary",
                    }
                ],
            }

        connector = CredentialEngineSearchConnector(
            api_key="test-secret-api-key",
            transport=transport,
        )
        self.assertNotIn("test-secret-api-key", repr(connector))
        result = connector.search(self.request)
        endpoint, headers, payload, timeout = calls[0]
        self.assertEqual(endpoint, PRODUCTION_ENDPOINT)
        self.assertEqual(
            headers["Authorization"], "Bearer test-secret-api-key"
        )
        self.assertNotIn(
            "test-secret-api-key",
            json.dumps(result),
        )
        self.assertEqual(
            payload["Query"]["@type"], ["ceterms:Certification"]
        )
        self.assertEqual(
            payload["Query"]["ceterms:ownedBy"]["ceterms:name"][
                "search:value"
            ],
            "Synthetic Public Issuer",
        )
        self.assertEqual(
            result["disposition"],
            "candidates_pending_phase3a_review",
        )
        self.assertFalse(result["definition_accepted"])
        self.assertEqual(result["participant_claims_established"], [])

    def test_connector_rejects_unapproved_endpoint(self) -> None:
        with self.assertRaisesRegex(
            CredentialRegistryError, "allowlisted"
        ):
            CredentialEngineSearchConnector(
                api_key="test-secret-api-key",
                endpoint="https://example.invalid/search",
            )


if __name__ == "__main__":
    unittest.main()
