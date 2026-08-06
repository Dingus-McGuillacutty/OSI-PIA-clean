from __future__ import annotations

import base64
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from software.intake.local_intake_server import create_server
from software.intake.local_private_intake import (
    IntakePreflightError,
    LocalIntakeStore,
    ParticipantModeBlockedError,
    REPOSITORY_ROOT,
)


class PIALocalPrivateIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.store_root = Path(self.temporary.name) / "pia-phase2-synthetic"
        self.store = LocalIntakeStore(self.store_root)

    def create_session(self) -> dict[str, object]:
        return self.store.create_session(
            participant_id="PIA-9001",
            participant_label="Synthetic Intake Subject Alpha",
            purpose="Synthetic Phase 2 validation",
            processing_scope="credential_definition|capability_mapping",
            consent_status="granted",
            confidentiality="participant_private",
            retention_class="synthetic_test",
        )

    def test_storage_root_must_remain_outside_repository(self) -> None:
        with self.assertRaises(IntakePreflightError):
            LocalIntakeStore(REPOSITORY_ROOT / "private-test")

    def test_participant_mode_fails_closed_without_encryption(self) -> None:
        with self.assertRaises(ParticipantModeBlockedError):
            LocalIntakeStore(self.store_root, mode="participant")

    def test_session_preflight_requires_authorization(self) -> None:
        with self.assertRaises(IntakePreflightError):
            self.store.create_session(
                participant_id="PIA-9001",
                participant_label="Synthetic Intake Subject Alpha",
                purpose="Synthetic Phase 2 validation",
                processing_scope="credential_definition",
                consent_status="pending",
                confidentiality="participant_private",
                retention_class="synthetic_test",
            )

    def test_staging_records_checksum_provenance_and_exact_duplicate(self) -> None:
        session = self.create_session()
        first = self.store.stage_upload(
            session_id=str(session["intake_session_id"]),
            original_filename="synthetic-resume.txt",
            content=b"synthetic evidence only",
            document_type="career_document",
        )
        duplicate = self.store.stage_upload(
            session_id=str(session["intake_session_id"]),
            original_filename="renamed-synthetic-resume.txt",
            content=b"synthetic evidence only",
            document_type="career_document",
        )

        self.assertEqual(first["disposition"], "staged")
        self.assertEqual(duplicate["disposition"], "exact_duplicate")
        self.assertEqual(
            duplicate["duplicate_of_source_artifact_id"],
            first["source_artifact_id"],
        )
        self.assertEqual(first["checksum"], duplicate["checksum"])
        self.assertEqual(len(list(self.store_root.rglob("*.blob"))), 1)
        self.assertTrue(self.store.validate()["accepted"])

    def test_integrity_validation_detects_changed_stored_content(self) -> None:
        session = self.create_session()
        artifact = self.store.stage_upload(
            session_id=str(session["intake_session_id"]),
            original_filename="synthetic-credential.txt",
            content=b"synthetic credential",
            document_type="credential_learning",
        )
        stored_path = self.store_root / str(artifact["storage_reference"])
        stored_path.write_bytes(b"changed after staging")

        result = self.store.validate()
        self.assertFalse(result["accepted"])
        self.assertIn(
            "CHECKSUM_MISMATCH",
            {finding["code"] for finding in result["findings"]},
        )

    def test_staging_rejects_tampered_session_identity(self) -> None:
        session = self.create_session()
        session_path = (
            self.store_root
            / "sessions"
            / str(session["intake_session_id"])
            / "session.json"
        )
        stored_session = json.loads(session_path.read_text(encoding="utf-8"))
        stored_session["participant_id"] = "../not-a-synthetic-participant"
        session_path.write_text(json.dumps(stored_session), encoding="utf-8")

        with self.assertRaises(IntakePreflightError):
            self.store.stage_upload(
                session_id=str(session["intake_session_id"]),
                original_filename="synthetic.txt",
                content=b"synthetic",
                document_type="supporting_evidence",
            )

    def test_local_server_creates_session_and_stages_document(self) -> None:
        server, token = create_server(self.store, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base_url = f"http://127.0.0.1:{server.server_port}"

        with urllib.request.urlopen(f"{base_url}/") as response:
            page = response.read().decode()
            self.assertIn("Synthetic test data only.", page)
            self.assertIn("Start a governed intake session.", page)
            self.assertEqual(response.headers["Cache-Control"], "no-store")

        with urllib.request.urlopen(f"{base_url}/api/status") as response:
            status = json.loads(response.read())
            self.assertEqual(status["mode"], "synthetic")
            self.assertEqual(response.headers["X-Frame-Options"], "DENY")

        session_request = urllib.request.Request(
            f"{base_url}/api/sessions",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-PIA-Local-Token": token,
            },
            data=json.dumps(
                {
                    "participant_label": "Synthetic Intake Subject Alpha",
                    "purpose": "Synthetic API test",
                    "processing_scope": "credential_definition",
                    "consent_status": "granted",
                    "confidentiality": "participant_private",
                    "retention_class": "synthetic_test",
                }
            ).encode(),
        )
        with urllib.request.urlopen(session_request) as response:
            session = json.loads(response.read())

        artifact_request = urllib.request.Request(
            f"{base_url}/api/artifacts",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-PIA-Local-Token": token,
            },
            data=json.dumps(
                {
                    "intake_session_id": session["intake_session_id"],
                    "original_filename": "synthetic-course.txt",
                    "document_type": "credential_learning",
                    "content_base64": base64.b64encode(b"synthetic course").decode(),
                }
            ).encode(),
        )
        with urllib.request.urlopen(artifact_request) as response:
            artifact = json.loads(response.read())
            self.assertEqual(artifact["disposition"], "staged")

    def test_local_server_rejects_missing_request_token(self) -> None:
        server, _ = create_server(self.store, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/sessions",
            method="POST",
            headers={"Content-Type": "application/json"},
            data=b"{}",
        )
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(request)
        self.assertEqual(raised.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
