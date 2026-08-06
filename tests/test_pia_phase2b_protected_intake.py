from __future__ import annotations

import base64
import json
import platform
import re
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from software.intake.phase2b_admin import _build_parser, _new_passphrase
from software.intake.mapping_output_linkage import ProtectedMappingOutputLinkage
from software.intake.sandbox_projection_preflight import preflight
from software.intake.synthetic_sandbox_import import validate_synthetic_rows
from software.intake.local_private_intake import (
    IntakePreflightError,
    LocalIntakeError,
)
from software.intake.phase2b_security import (
    MalwareScanResult,
    WindowsAMSIScanner,
    dpapi_protect,
    dpapi_unprotect,
    utc_now,
)
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)
from software.intake.protected_intake_server import create_server


class FakeScanner:
    provider_name = "test-in-memory-scanner"

    def __init__(self, status: str = "clean") -> None:
        self.status = status

    def preflight(self) -> MalwareScanResult:
        return MalwareScanResult(
            status="clean",
            provider=self.provider_name,
            result_code=0,
            scanned_at=utc_now(),
        )

    def scan(self, content: bytes, *, content_name: str) -> MalwareScanResult:
        return MalwareScanResult(
            status=self.status,
            provider=self.provider_name,
            result_code=0 if self.status == "clean" else 32768,
            scanned_at=utc_now(),
        )


def fake_acl_hardener(root: Path) -> dict[str, str]:
    return {
        "acl_state": "test-restricted-current-user-and-system",
        "identity": "test-owner",
    }


class PIAPhase2BProtectedIntakeTests(unittest.TestCase):
    OWNER_PASSPHRASE = "owner-passphrase-for-tests"
    RECOVERY_PASSPHRASE = "recovery-passphrase-for-tests"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.store_root = root / "participant-store"
        self.recovery_path = root / "offline" / "recovery.json"
        self.store = ProtectedParticipantIntakeStore.create(
            self.store_root,
            owner_passphrase=self.OWNER_PASSPHRASE,
            recovery_path=self.recovery_path,
            recovery_passphrase=self.RECOVERY_PASSPHRASE,
            scanner=FakeScanner(),
            acl_hardener=fake_acl_hardener,
        )

    def create_session(
        self,
        *,
        participant_id: str | None = None,
    ) -> dict[str, object]:
        return self.store.create_session(
            participant_label="Synthetic Intake Subject Alpha",
            purpose="Research participant intake and report development",
            processing_scope="credential_definition|capability_mapping|report_generation",
            consent_status="granted",
            confidentiality="participant_private",
            retention_class="30_days",
            actor_subject="local-owner",
            actor_role="owner",
            participant_id=participant_id,
        )

    def stage_document(self, session_id: str) -> dict[str, object]:
        return self.store.stage_upload(
            session_id=session_id,
            original_filename="participant-resume.txt",
            content=b"private participant evidence",
            document_type="career_document",
            actor_subject="local-owner",
            actor_role="owner",
        )

    def test_resumable_session_index_is_bounded_and_audited(self) -> None:
        session = self.create_session()
        self.stage_document(str(session["intake_session_id"]))

        index = self.store.list_resumable_sessions(
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(len(index["sessions"]), 1)
        summary = index["sessions"][0]
        self.assertEqual(
            summary["intake_session_id"],
            session["intake_session_id"],
        )
        self.assertEqual(summary["artifact_count"], 1)
        self.assertEqual(summary["evidence_reviewed_count"], 0)
        self.assertEqual(summary["evidence_pending_count"], 0)
        self.assertTrue(summary["has_saved_work"])
        self.assertEqual(summary["created_at"], session["created_at"])
        self.assertNotIn("purpose", summary)
        self.assertNotIn("artifacts", summary)

        resumed = self.store.resume_session(
            str(session["intake_session_id"]),
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(
            resumed["participant_label"],
            "Synthetic Intake Subject Alpha",
        )
        event_types = {
            event["event_type"] for event in self.store._read_audit()
        }
        self.assertIn("resumable_session_index_viewed", event_types)
        self.assertIn("participant_session_resumed", event_types)

    def test_resumable_session_index_identifies_empty_work(self) -> None:
        session = self.create_session()

        index = self.store.list_resumable_sessions(
            actor_subject="local-owner",
            actor_role="owner",
        )

        self.assertEqual(len(index["sessions"]), 1)
        summary = index["sessions"][0]
        self.assertEqual(
            summary["intake_session_id"],
            session["intake_session_id"],
        )
        self.assertFalse(summary["has_saved_work"])
        self.assertEqual(summary["artifact_count"], 0)
        self.assertEqual(summary["evidence_candidate_count"], 0)
        self.assertEqual(summary["credential_count"], 0)

    def test_owner_authentication_and_recovery_bundle(self) -> None:
        self.assertTrue(
            self.store.authenticator.verify(self.OWNER_PASSPHRASE)
        )
        self.assertFalse(self.store.authenticator.verify("incorrect-passphrase"))
        recovered = self.store.encryption.recover_key(
            self.recovery_path,
            self.RECOVERY_PASSPHRASE,
            expected_store_id=str(self.store.manifest["store_id"]),
        )
        self.assertEqual(recovered, self.store.encryption.master_key)

    def test_admin_passphrase_preflight_identifies_short_entry(self) -> None:
        with patch(
            "software.intake.phase2b_admin.getpass.getpass",
            side_effect=["thirteenchars", "thirteenchars"],
        ):
            with self.assertRaisesRegex(
                LocalIntakeError,
                "local owner passphrase was received as 13",
            ):
                _new_passphrase("Local owner")

        accepted = "four words are safely longer"
        with patch(
            "software.intake.phase2b_admin.getpass.getpass",
            side_effect=[accepted, accepted],
        ):
            self.assertEqual(_new_passphrase("Offline recovery"), accepted)

    def test_reviewer_setup_supports_windowed_passphrases(self) -> None:
        args = _build_parser().parse_args(
            [
                "add-reviewer",
                "--storage-root",
                str(self.store_root),
                "--account-id",
                "reviewer-001",
                "--windowed-passphrases",
            ]
        )
        self.assertTrue(args.windowed_passphrases)

    def test_reviewer_account_authenticates_with_bounded_role(self) -> None:
        reviewer = self.store.authenticator.add_reviewer(
            "reviewer-001",
            "reviewer-passphrase-for-tests",
        )
        identity = self.store.authenticator.authenticate(
            "reviewer-001",
            "reviewer-passphrase-for-tests",
        )
        self.assertEqual(reviewer["role"], "reviewer")
        self.assertEqual(identity, reviewer)

    def test_session_metadata_and_document_are_encrypted_at_rest(self) -> None:
        session = self.create_session()
        artifact = self.stage_document(str(session["intake_session_id"]))
        session_dir = (
            self.store_root / "sessions" / str(session["intake_session_id"])
        )
        protected_session = (session_dir / "session.piaenc").read_bytes()
        protected_artifact = (
            self.store_root / str(artifact["storage_reference"])
        ).read_bytes()

        self.assertNotIn(b"Synthetic Intake Subject Alpha", protected_session)
        self.assertNotIn(b"participant-resume.txt", protected_session)
        self.assertNotIn(b"private participant evidence", protected_artifact)
        self.assertTrue(self.store.validate()["accepted"])

    def test_malware_gate_blocks_without_storing_document(self) -> None:
        session = self.create_session()
        self.store.scanner = FakeScanner(status="malware_detected")
        with self.assertRaises(IntakePreflightError):
            self.stage_document(str(session["intake_session_id"]))

        stored_session = self.store.get_session(
            str(session["intake_session_id"]),
            actor_role="owner",
        )
        self.assertEqual(stored_session["artifacts"], [])
        artifact_dir = (
            self.store_root
            / "sessions"
            / str(session["intake_session_id"])
            / "artifacts"
        )
        self.assertEqual(list(artifact_dir.iterdir()), [])

    def test_withdrawal_blocks_processing_and_optional_deletion_erases_session(self) -> None:
        session = self.create_session()
        session_id = str(session["intake_session_id"])
        self.stage_document(session_id)
        withdrawn = self.store.withdraw_session(
            session_id,
            reason="Participant withdrew permission.",
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(withdrawn["consent_status"], "withdrawn")
        self.assertEqual(withdrawn["processing_state"], "blocked")
        with self.assertRaises(IntakePreflightError):
            self.stage_document(session_id)

        tombstone = self.store.delete_session(
            session_id,
            reason_code="withdrawal",
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertFalse((self.store_root / "sessions" / session_id).exists())
        self.assertFalse(tombstone["participant_content_retained"])
        self.assertTrue(
            (self.store_root / "tombstones" / f"{session_id}.json").is_file()
        )

    def test_deleted_session_cannot_prepare_output_preview(self) -> None:
        session = self.create_session()
        session_id = str(session["intake_session_id"])
        self.store.delete_session(
            session_id,
            reason_code="participant_request",
            actor_subject="local-owner",
            actor_role="owner",
        )
        with self.assertRaises(LocalIntakeError):
            ProtectedMappingOutputLinkage(self.store).preview(
                session_id=session_id, actor_role="owner"
            )

    def test_deleted_identifiers_are_permanently_retired(self) -> None:
        first = self.create_session()
        first_id = str(first["intake_session_id"])
        self.store.delete_session(
            first_id,
            reason_code="test_cleanup",
            actor_subject="local-owner",
            actor_role="owner",
        )

        second = self.create_session()
        self.assertNotEqual(
            second["participant_id"],
            first["participant_id"],
        )
        self.assertRegex(
            str(second["intake_session_id"]),
            r"^PIA-[1-8][0-9]{3}-INT-001$",
        )

        same_participant = self.create_session(
            participant_id=str(first["participant_id"])
        )
        self.assertEqual(
            same_participant["intake_session_id"],
            f"{first['participant_id']}-INT-002",
        )
        self.assertTrue(self.store.validate()["accepted"])

    def test_reused_deleted_identifier_fails_closed(self) -> None:
        session = self.create_session()
        session_id = str(session["intake_session_id"])
        directory = self.store_root / "sessions" / session_id
        key_content = (directory / "session-key.piaenc").read_bytes()
        record_content = (directory / "session.piaenc").read_bytes()
        self.store.delete_session(
            session_id,
            reason_code="test_cleanup",
            actor_subject="local-owner",
            actor_role="owner",
        )
        directory.mkdir()
        (directory / "artifacts").mkdir()
        (directory / "extractions").mkdir()
        (directory / "session-key.piaenc").write_bytes(key_content)
        (directory / "session.piaenc").write_bytes(record_content)

        result = self.store.validate()
        self.assertFalse(result["accepted"])
        self.assertIn(
            "DELETED_SESSION_IDENTIFIER_REUSED",
            {finding["code"] for finding in result["findings"]},
        )
        with self.assertRaises(LocalIntakeError):
            self.store.list_resumable_sessions(
                actor_subject="local-owner",
                actor_role="owner",
            )
        with self.assertRaises(LocalIntakeError):
            self.store.resume_session(
                session_id,
                actor_subject="local-owner",
                actor_role="owner",
            )

    def test_reviewer_cannot_delete_session(self) -> None:
        session = self.create_session()
        with self.assertRaises(IntakePreflightError):
            self.store.delete_session(
                str(session["intake_session_id"]),
                reason_code="participant_request",
                actor_subject="reviewer-001",
                actor_role="reviewer",
            )

    def test_retention_dry_run_and_execution(self) -> None:
        session = self.create_session()
        session_id = str(session["intake_session_id"])
        future = datetime.now(UTC) + timedelta(days=31)
        preview = self.store.enforce_retention(
            actor_subject="local-owner",
            actor_role="owner",
            now=future,
            dry_run=True,
        )
        self.assertEqual(preview["expired_session_ids"], [session_id])
        self.assertTrue((self.store_root / "sessions" / session_id).exists())

        executed = self.store.enforce_retention(
            actor_subject="local-owner",
            actor_role="owner",
            now=future,
            dry_run=False,
        )
        self.assertEqual(executed["deleted_session_ids"], [session_id])
        self.assertFalse((self.store_root / "sessions" / session_id).exists())

    def test_tampered_ciphertext_fails_validation(self) -> None:
        session = self.create_session()
        artifact = self.stage_document(str(session["intake_session_id"]))
        path = self.store_root / str(artifact["storage_reference"])
        protected = bytearray(path.read_bytes())
        protected[-1] ^= 1
        path.write_bytes(protected)

        result = self.store.validate()
        self.assertFalse(result["accepted"])
        self.assertIn(
            "ARTIFACT_DECRYPTION_FAILED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_audit_chain_is_encrypted_and_tamper_evident(self) -> None:
        self.create_session()
        audit_bytes = self.store.audit_path.read_bytes()
        self.assertNotIn(b"participant_session_created", audit_bytes)
        lines = self.store.audit_path.read_text(encoding="utf-8").splitlines()
        envelope = json.loads(lines[0])
        protected = bytearray.fromhex(envelope["protected_event"])
        protected[-1] ^= 1
        envelope["protected_event"] = protected.hex()
        lines[0] = json.dumps(envelope)
        self.store.audit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        result = self.store.validate()
        self.assertFalse(result["accepted"])
        self.assertIn(
            "AUDIT_DECRYPTION_FAILED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_manifest_and_account_registry_are_tamper_evident(self) -> None:
        manifest_path = self.store_root / "store.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["controls"]["graph_projection"] = "enabled"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(IntakePreflightError):
            ProtectedParticipantIntakeStore.open(
                self.store_root,
                scanner=FakeScanner(),
                run_malware_preflight=False,
            )

        manifest["controls"]["graph_projection"] = "disabled"
        manifest_path.write_text(json.dumps(self.store.manifest), encoding="utf-8")
        auth_path = self.store_root / "auth.json"
        auth = json.loads(auth_path.read_text(encoding="utf-8"))
        auth["accounts"][0]["role"] = "reviewer"
        auth_path.write_text(json.dumps(auth), encoding="utf-8")
        with self.assertRaises(LocalIntakeError):
            self.store.authenticator.identity()
        result = self.store.validate()
        self.assertIn(
            "ACCOUNT_REGISTRY_INTEGRITY_FAILED",
            {finding["code"] for finding in result["findings"]},
        )

    def test_deletion_tombstone_is_integrity_protected(self) -> None:
        session = self.create_session()
        session_id = str(session["intake_session_id"])
        self.store.delete_session(
            session_id,
            reason_code="test_cleanup",
            actor_subject="local-owner",
            actor_role="owner",
        )
        tombstone_path = self.store_root / "tombstones" / f"{session_id}.json"
        tombstone = json.loads(tombstone_path.read_text(encoding="utf-8"))
        tombstone["reason_code"] = "participant_request"
        tombstone_path.write_text(json.dumps(tombstone), encoding="utf-8")

        result = self.store.validate()
        self.assertFalse(result["accepted"])
        self.assertIn(
            "DELETION_TOMBSTONE_INVALID",
            {finding["code"] for finding in result["findings"]},
        )

    @unittest.skipUnless(platform.system() == "Windows", "Windows control check")
    def test_windows_dpapi_and_amsi_capabilities(self) -> None:
        value = b"phase2b-windows-control-check"
        self.assertEqual(dpapi_unprotect(dpapi_protect(value)), value)
        self.assertTrue(WindowsAMSIScanner().preflight().accepted)

    def test_protected_server_requires_login_and_csrf(self) -> None:
        server = create_server(self.store, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base_url = f"http://127.0.0.1:{server.server_port}"
        user_agent = "PIA-Phase2B-Test"

        login_page_request = urllib.request.Request(
            f"{base_url}/",
            headers={"User-Agent": user_agent},
        )
        with urllib.request.urlopen(login_page_request) as response:
            page = response.read().decode()
            self.assertIn("Open the local participant workspace.", page)
            self.assertNotIn("Create participant session", page)

        unauthenticated = urllib.request.Request(
            f"{base_url}/api/sessions",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": user_agent,
            },
            data=b"{}",
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(unauthenticated)
        self.assertEqual(raised.exception.code, 401)

        login = urllib.request.Request(
            f"{base_url}/api/login",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": user_agent,
            },
            data=json.dumps(
                {
                    "account_id": "local-owner",
                    "passphrase": self.OWNER_PASSPHRASE,
                }
            ).encode(),
        )
        with urllib.request.urlopen(login) as response:
            cookie = response.headers["Set-Cookie"].split(";", 1)[0]

        protected_page_request = urllib.request.Request(
            f"{base_url}/",
            headers={"Cookie": cookie, "User-Agent": user_agent},
        )
        with urllib.request.urlopen(protected_page_request) as response:
            page = response.read().decode()
            self.assertIn("Create participant session", page)
            self.assertIn("Continue or manage protected work", page)
            self.assertIn("Review saved sessions", page)
            self.assertIn("Sessions with saved work", page)
            self.assertIn("Empty sessions (", page)
            self.assertIn("Current session", page)
            self.assertIn("Create a separate session anyway", page)
            self.assertIn("Last removed session: ", page)
            self.assertIn("Check what a credential represents.", page)
            self.assertIn("Image files are not supported yet.", page)
            self.assertIn("Change review decision", page)
            self.assertIn("Save corrected wording", page)
            self.assertIn("Current review: ", page)
            self.assertIn("The current review stays ", page)
            self.assertIn("until a new decision is saved.", page)
            self.assertIn(
                "Earlier review decisions remain in the protected audit history.",
                page,
            )
            self.assertNotIn("const revised=prompt(", page)
            csrf_match = re.search(r"const CSRF=(\"[^\"]+\")", page)
            self.assertIsNotNone(csrf_match)
            csrf = json.loads(csrf_match.group(1))

        create_request = urllib.request.Request(
            f"{base_url}/api/sessions",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "participant_label": "Synthetic Intake Subject Alpha",
                    "purpose": "Protected participant test",
                    "processing_scope": (
                        "evidence_extraction|credential_definition|"
                        "capability_mapping|report_generation"
                    ),
                    "consent_status": "granted",
                    "confidentiality": "participant_private",
                    "retention_class": "30_days",
                }
            ).encode(),
        )
        with urllib.request.urlopen(create_request) as response:
            session = json.loads(response.read())
            self.assertRegex(session["intake_session_id"], r"^PIA-[1-8][0-9]{3}-INT-001$")

        artifact_request = urllib.request.Request(
            f"{base_url}/api/artifacts",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "original_filename": "resume.txt",
                    "document_type": "career_document",
                    "content_base64": base64.b64encode(
                        b"EXPERIENCE\n\nManaged a security program."
                    ).decode(),
                }
            ).encode(),
        )
        with urllib.request.urlopen(artifact_request) as response:
            artifact = json.loads(response.read())
            self.assertEqual(response.status, 201)

        extraction_request = urllib.request.Request(
            f"{base_url}/api/extractions",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "source_artifact_id": artifact["source_artifact_id"],
                }
            ).encode(),
        )
        with urllib.request.urlopen(extraction_request) as response:
            extraction = json.loads(response.read())
            self.assertEqual(response.status, 201)
            self.assertEqual(
                extraction["capability_assertions_created"],
                [],
            )
            evidence_id = extraction["evidence_candidates"][0][
                "evidence_id"
            ]

        evidence_review_request = urllib.request.Request(
            f"{base_url}/api/evidence/review",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "evidence_id": evidence_id,
                    "disposition": "accepted",
                    "corrected_text": "",
                    "reason": "",
                }
            ).encode(),
        )
        with urllib.request.urlopen(evidence_review_request) as response:
            review = json.loads(response.read())
            self.assertTrue(
                review["evidence_candidate"]["included_in_downstream"]
            )

        mapping_request = urllib.request.Request(
            f"{base_url}/api/mappings/propose",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "evidence_id": evidence_id,
                    "profile_capability_id": (
                        "CAP-PIA-STAKEHOLDER-COORDINATION"
                    ),
                    "inference_level": "directly_demonstrated",
                    "evidence_role": "behavioral_demonstration",
                    "claim_scope": "demonstrated_application",
                    "application_status": "described_in_source",
                    "confidence": 0.72,
                    "confidence_basis": (
                        "The reviewed evidence describes a bounded "
                        "coordination activity."
                    ),
                    "aligned_experience_ids": "",
                    "alignment_basis": (
                        "No separate experience record is asserted in this "
                        "protected intake increment."
                    ),
                    "credential_definition_status": "",
                    "credential_definition_source": "",
                    "credential_definition_uri": "",
                    "credential_domain_scope": "",
                    "definition_expansion_required": False,
                    "behavioral_basis": (
                        "The source-grounded evidence describes the "
                        "coordination behavior."
                    ),
                    "negative_boundary": (
                        "Does not establish formal authority, outcomes, or "
                        "a durable participant trait."
                    ),
                    "scope_limit": "The documented source item only.",
                    "source_independence_note": (
                        "One reviewed source chain; independent corroboration "
                        "is not established."
                    ),
                }
            ).encode(),
        )
        with urllib.request.urlopen(mapping_request) as response:
            mapping = json.loads(response.read())
            self.assertEqual(response.status, 201)
            self.assertEqual(mapping["review_status"], "proposed")
            self.assertTrue(mapping["human_review_required"])
            self.assertEqual(mapping["relationship_type"], "SUPPORTS")

        self_review_request = urllib.request.Request(
            f"{base_url}/api/mappings/review",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "mapping_id": mapping["mapping_id"],
                    "disposition": "accepted",
                    "reason": "Attempted self review.",
                    "narrowed_scope_limit": "",
                    "narrowed_negative_boundary": "",
                }
            ).encode(),
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(self_review_request)
        self.assertEqual(raised.exception.code, 400)

        self.store.authenticator.add_reviewer(
            "reviewer-001", "reviewer-passphrase-for-tests"
        )
        reviewer_login = urllib.request.Request(
            f"{base_url}/api/login",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "PIA-Phase2B-Reviewer-Test",
            },
            data=json.dumps(
                {
                    "account_id": "reviewer-001",
                    "passphrase": "reviewer-passphrase-for-tests",
                }
            ).encode(),
        )
        with urllib.request.urlopen(reviewer_login) as response:
            reviewer_cookie = response.headers["Set-Cookie"].split(";", 1)[0]
        reviewer_page = urllib.request.Request(
            f"{base_url}/",
            headers={
                "Cookie": reviewer_cookie,
                "User-Agent": "PIA-Phase2B-Reviewer-Test",
            },
        )
        with urllib.request.urlopen(reviewer_page) as response:
            reviewer_csrf = json.loads(
                re.search(
                    r"const CSRF=(\"[^\"]+\")", response.read().decode()
                ).group(1)
            )
        reviewer_request = urllib.request.Request(
            f"{base_url}/api/mappings/review",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": reviewer_cookie,
                "User-Agent": "PIA-Phase2B-Reviewer-Test",
                "X-PIA-CSRF": reviewer_csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "mapping_id": mapping["mapping_id"],
                    "disposition": "accepted",
                    "reason": "Independent review accepts the bounded mapping.",
                    "narrowed_scope_limit": "",
                    "narrowed_negative_boundary": "",
                }
            ).encode(),
        )
        with urllib.request.urlopen(reviewer_request) as response:
            mapping_review = json.loads(response.read())
            self.assertEqual(mapping_review["mapping"]["review_status"], "accepted")
            self.assertEqual(mapping_review["mapping"]["reviewed_by"], "reviewer-001")

        output_preview_request = urllib.request.Request(
            f"{base_url}/api/outputs/preview",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": reviewer_cookie,
                "User-Agent": "PIA-Phase2B-Reviewer-Test",
                "X-PIA-CSRF": reviewer_csrf,
            },
            data=json.dumps(
                {"intake_session_id": session["intake_session_id"]}
            ).encode(),
        )
        with urllib.request.urlopen(output_preview_request) as response:
            preview = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(
                preview["projection_manifest"]["projection_mode"], "dry_run"
            )
            self.assertEqual(
                preview["projection_manifest"]["graph_write"], "not_performed"
            )
            self.assertEqual(
                len(preview["participant_preview"]["interpretations"]), 1
            )
            self.assertEqual(
                preview["participant_preview"]["status"],
                "ready_for_participant_review",
            )
            self.assertEqual(
                len(preview["technical_companion"]["interpretations"]), 1
            )

        feedback_request = urllib.request.Request(
            f"{base_url}/api/outputs/feedback",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": reviewer_cookie,
                "User-Agent": "PIA-Phase2B-Reviewer-Test",
                "X-PIA-CSRF": reviewer_csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "note": "Please reconsider the wording before sharing this draft.",
                }
            ).encode(),
        )
        with urllib.request.urlopen(feedback_request) as response:
            feedback = json.loads(response.read())
            self.assertEqual(response.status, 201)
            self.assertFalse(feedback["changes_evidence"])
            self.assertFalse(feedback["changes_mapping"])

        with urllib.request.urlopen(output_preview_request) as response:
            after_feedback = json.loads(response.read())
            self.assertEqual(
                after_feedback["projection_manifest"]["record_selection"],
                preview["projection_manifest"]["record_selection"],
            )

        credential_request = urllib.request.Request(
            f"{base_url}/api/credentials",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "credential_title": "PSP",
                    "issuer_hint": "ASIS",
                    "version_hint": "",
                    "credential_type_hint": "certification",
                    "jurisdiction_hint": "international",
                }
            ).encode(),
        )
        with urllib.request.urlopen(credential_request) as response:
            credential = json.loads(response.read())
            self.assertEqual(response.status, 201)
            self.assertEqual(
                credential["routing_outcome"],
                "manual_definition_review",
            )
            self.assertEqual(
                credential["participant_claims_established"], []
            )

        session_index_request = urllib.request.Request(
            f"{base_url}/api/sessions",
            method="GET",
            headers={
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
        )
        with urllib.request.urlopen(session_index_request) as response:
            session_index = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(len(session_index["sessions"]), 1)
            self.assertEqual(
                session_index["sessions"][0]["intake_session_id"],
                session["intake_session_id"],
            )
            self.assertEqual(
                session_index["sessions"][0]["evidence_candidate_count"],
                len(extraction["evidence_candidates"]),
            )
            self.assertEqual(
                session_index["sessions"][0]["credential_count"],
                1,
            )
            self.assertEqual(
                session_index["sessions"][0]["evidence_reviewed_count"],
                1,
            )
            self.assertEqual(
                session_index["sessions"][0]["evidence_pending_count"],
                len(extraction["evidence_candidates"]) - 1,
            )
            self.assertTrue(
                session_index["sessions"][0]["has_saved_work"]
            )

        resume_request = urllib.request.Request(
            f"{base_url}/api/sessions/resume",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session[
                        "intake_session_id"
                    ],
                }
            ).encode(),
        )
        with urllib.request.urlopen(resume_request) as response:
            resumed = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(
                resumed["session"]["intake_session_id"],
                session["intake_session_id"],
            )
            self.assertEqual(len(resumed["artifacts"]), 1)
            self.assertEqual(
                resumed["evidence_extractions"][0][
                    "evidence_candidates"
                ][0]["current_review_disposition"],
                "accepted",
            )
            self.assertEqual(
                resumed["credential_resolutions"][0][
                    "credential_entry_id"
                ],
                credential["credential_entry_id"],
            )
            self.assertEqual(
                resumed["capability_mapping_proposals"][0]["mapping_id"],
                mapping["mapping_id"],
            )
            self.assertEqual(
                resumed["capability_mapping_proposals"][0]["review_status"],
                "accepted",
            )

        prohibited_credential_request = urllib.request.Request(
            f"{base_url}/api/credentials",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Cookie": cookie,
                "User-Agent": user_agent,
                "X-PIA-CSRF": csrf,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "credential_title": "PSP",
                    "issuer_hint": "ASIS",
                    "version_hint": "",
                    "credential_type_hint": "certification",
                    "jurisdiction_hint": "international",
                    "participant_note": "Private context must be rejected.",
                }
            ).encode(),
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(prohibited_credential_request)
        self.assertEqual(raised.exception.code, 400)


class MappingOutputRegressionTests(unittest.TestCase):
    def _mapping(self, mapping_id: str, *, boundary: str) -> dict[str, object]:
        return {
            "mapping_id": mapping_id,
            "profile_capability_id": "CAP-PIA-HANDOFF-MANAGEMENT",
            "capability_name": "Handoff Management",
            "review_status": "accepted",
            "inference_level": "strongly_inferred",
            "confidence": 0.7,
            "confidence_basis": (
                "The reviewed source describes a documented handoff activity."
            ),
            "scope_limit": "This applies only to the documented handoff activity.",
            "negative_boundary": boundary,
            "source_independence_note": "One reviewed source chain is available.",
            "evidence_id": "PIA-SYN-EVD-001",
        }

    def _preview(self, mappings: list[dict[str, object]]) -> dict[str, object]:
        class SyntheticStore:
            def list_capability_mapping_proposals(self, **_: object) -> list[dict[str, object]]:
                return mappings

        return ProtectedMappingOutputLinkage(SyntheticStore()).preview(
            session_id="PIA-SYN-INT-001", actor_role="reviewer"
        )

    def test_groups_clean_mappings_into_report_ready_preview(self) -> None:
        preview = self._preview(
            [
                self._mapping(f"PIA-SYN-MAP-00{number}", boundary="Does not establish formal authority or outcomes.")
                for number in range(1, 4)
            ]
        )
        participant = preview["participant_preview"]
        self.assertEqual(participant["status"], "ready_for_participant_review")
        self.assertEqual(len(participant["interpretations"]), 1)
        self.assertEqual(participant["interpretations"][0]["mapping_ids"].__len__(), 3)
        self.assertEqual(preview["projection_manifest"]["assurance_status"], "pass")
        self.assertEqual(len(preview["technical_companion"]["interpretations"]), 3)
        self.assertEqual(preview["sandbox_projection_assurance"]["status"], "pass")
        self.assertEqual(
            len(preview["sandbox_projection_assurance"]["records"]), 3
        )
        self.assertEqual(
            preview["sandbox_projection_assurance"]["target_preflight"]["database"],
            "PIA-Sandbox",
        )

    def test_holds_preview_but_preserves_technical_mapping(self) -> None:
        preview = self._preview(
            [self._mapping("PIA-SYN-MAP-001", boundary="Test")]
        )
        self.assertEqual(
            preview["participant_preview"]["status"], "held_for_output_assurance"
        )
        self.assertEqual(len(preview["participant_preview"]["quality_findings"]), 1)
        self.assertEqual(preview["projection_manifest"]["assurance_status"], "warning")
        self.assertEqual(len(preview["technical_companion"]["interpretations"]), 1)
        self.assertEqual(preview["sandbox_projection_assurance"]["graph_write"], "not_performed")

    def test_excludes_superseded_mapping_from_current_output(self) -> None:
        historical = self._mapping(
            "PIA-SYN-MAP-001", boundary="Does not establish formal authority or outcomes."
        )
        historical["review_status"] = "superseded"
        replacement = self._mapping(
            "PIA-SYN-MAP-002", boundary="Does not establish formal authority or outcomes."
        )
        replacement["supersedes_mapping_id"] = "PIA-SYN-MAP-001"
        preview = self._preview([historical, replacement])
        self.assertEqual(
            preview["participant_preview"]["interpretations"][0]["mapping_ids"],
            ["PIA-SYN-MAP-002"],
        )
        self.assertEqual(
            preview["projection_manifest"]["record_selection"], "PIA-SYN-MAP-002"
        )

    def test_dry_run_manifest_is_stable_and_sandbox_only(self) -> None:
        first = self._mapping(
            "PIA-SYN-MAP-002", boundary="Does not establish formal authority or outcomes."
        )
        second = self._mapping(
            "PIA-SYN-MAP-001", boundary="Does not establish formal authority or outcomes."
        )
        forward = self._preview([first, second])["projection_manifest"]
        reverse = self._preview([second, first])["projection_manifest"]
        self.assertEqual(forward["record_selection"], "PIA-SYN-MAP-001|PIA-SYN-MAP-002")
        self.assertEqual(forward["package_checksum"], reverse["package_checksum"])
        self.assertEqual(forward["target_environment"], "local_sandbox")
        self.assertEqual(forward["target_database"], "PIA-Sandbox")
        self.assertEqual(forward["projection_mode"], "dry_run")
        self.assertEqual(forward["graph_write"], "not_performed")

    def test_sandbox_preflight_rejects_wrong_target_or_mode(self) -> None:
        manifest = {
            "target_environment": "local_sandbox",
            "target_database": "PIA-Sandbox",
            "projection_mode": "dry_run",
        }
        with self.assertRaises(IntakePreflightError):
            preflight(manifest, uri="neo4j://127.0.0.1:7687", database="pia-reference")
        manifest["projection_mode"] = "apply"
        with self.assertRaises(IntakePreflightError):
            preflight(manifest, uri="neo4j://127.0.0.1:7687", database="PIA-Sandbox")

    def test_sandbox_assurance_blocks_invalid_confidence(self) -> None:
        mapping = self._mapping(
            "PIA-SYN-MAP-001", boundary="Does not establish formal authority or outcomes."
        )
        mapping["confidence"] = 1.2
        preview = self._preview([mapping])
        self.assertEqual(preview["sandbox_projection_assurance"]["status"], "block")
        self.assertIn("Invalid mapping record PIA-SYN-MAP-001.", preview["sandbox_projection_assurance"]["findings"])

    def test_synthetic_import_rejects_invalid_package_before_io(self) -> None:
        invalid = [
            {
                "mapping_id": "PIA-SYN-MAP-001",
                "evidence_id": "PIA-SYN-EVD-001",
                "capability_id": "CAP-PIA-HANDOFF-MANAGEMENT",
                "confidence": 1.2,
                "confidence_basis": "Deliberately invalid control-test row.",
            }
        ]
        self.assertEqual(
            validate_synthetic_rows(invalid),
            ["Row 1 confidence must be between 0 and 1."],
        )

    def test_synthetic_import_rejects_non_synthetic_and_duplicate_ids(self) -> None:
        invalid = [
            {
                "mapping_id": "PIA-MAP-001",
                "evidence_id": "PIA-EVD-001",
                "capability_id": "CAP-OTHER",
                "confidence": 0.7,
                "confidence_basis": "",
            },
            {
                "mapping_id": "PIA-MAP-001",
                "evidence_id": "PIA-SYN-EVD-002",
                "capability_id": "CAP-PIA-TEST",
                "confidence": 0.5,
                "confidence_basis": "Synthetic.",
            },
        ]
        findings = validate_synthetic_rows(invalid)
        self.assertIn("Row 1 mapping ID is not synthetic.", findings)
        self.assertIn("Row 1 evidence ID is not synthetic.", findings)
        self.assertIn("Row 1 capability ID is outside the PIA namespace.", findings)
        self.assertIn("Row 1 confidence basis is empty.", findings)
        self.assertIn("Synthetic package contains duplicate mapping IDs.", findings)


if __name__ == "__main__":
    unittest.main()
