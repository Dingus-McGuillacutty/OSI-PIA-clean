from __future__ import annotations

import io
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

from software.intake.evidence_extraction import (
    EvidenceExtractionError,
    SafeEvidenceExtractor,
)
from software.intake.evidence_intake_linkage import (
    ProtectedEvidenceIntakeLinkage,
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


def minimal_docx(paragraphs: list[str]) -> bytes:
    body = "".join(
        (
            "<w:p><w:r><w:t>"
            + text.replace("&", "&amp;").replace("<", "&lt;")
            + "</w:t></w:r></w:p>"
        )
        for text in paragraphs
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body>'
        f"{body}</w:body></w:document>"
    )
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", xml)
    return output.getvalue()


def minimal_pdf(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        (
            f"<< /Length {len(stream)} >>\nstream\n".encode()
            + stream
            + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, value in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode())
        output.extend(value)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode()
    )
    return bytes(output)


class PIASafeEvidenceExtractorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = SafeEvidenceExtractor()

    def test_text_extraction_preserves_provenance_and_avoids_capabilities(
        self,
    ) -> None:
        result = self.extractor.extract(
            filename="resume.txt",
            content=(
                b"EXPERIENCE\n\nManaged regional operations.\n\n"
                b"Reduced response time by 20 percent."
            ),
        )
        self.assertEqual(result["extraction_status"], "complete")
        self.assertEqual(result["capability_assertions_created"], [])
        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(
            result["candidates"][0]["source_section"],
            "EXPERIENCE",
        )
        self.assertEqual(
            result["candidates"][0]["evidence_type"],
            "responsibility",
        )
        self.assertEqual(
            result["candidates"][1]["evidence_type"],
            "achievement",
        )
        self.assertTrue(
            all(
                item["review_status"] == "unreviewed"
                for item in result["candidates"]
            )
        )

    def test_csv_formula_content_remains_inert_text(self) -> None:
        result = self.extractor.extract(
            filename="positions.csv",
            content=(
                b"title,description\n"
                b"Analyst,=HYPERLINK(\"https://invalid.example\",\"click\")\n"
            ),
        )
        rendered = result["candidates"][0]["evidence_text"]
        self.assertIn("=HYPERLINK", rendered)
        self.assertEqual(
            result["candidates"][0]["source_locator"],
            "row 2",
        )

    def test_rtf_and_docx_extract_without_embedded_execution(self) -> None:
        rtf = self.extractor.extract(
            filename="profile.rtf",
            content=(
                b"{\\rtf1\\ansi EXPERIENCE\\par "
                b"Developed an incident response plan.}"
            ),
        )
        self.assertEqual(rtf["candidates"][0]["evidence_type"], "output")

        docx = self.extractor.extract(
            filename="resume.docx",
            content=minimal_docx(
                ["PROJECTS", "Created a regional security procedure."]
            ),
        )
        self.assertEqual(docx["parser_profile"], "docx/word-document-xml")
        self.assertEqual(len(docx["candidates"]), 1)
        self.assertEqual(docx["candidates"][0]["source_section"], "PROJECTS")

    def test_exact_duplicate_text_is_collapsed_without_losing_provenance(
        self,
    ) -> None:
        repeated = "Managed a documented operational handoff."
        result = self.extractor.extract(
            filename="resume.docx",
            content=minimal_docx(["EXPERIENCE", repeated, repeated]),
        )

        self.assertEqual(len(result["candidates"]), 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["evidence_text"], repeated)
        self.assertEqual(candidate["source_locator"], "paragraph 2")
        self.assertEqual(
            candidate["duplicate_source_locators"],
            ["paragraph 3"],
        )
        self.assertEqual(candidate["source_occurrence_count"], 2)
        self.assertEqual(
            candidate["deduplication_status"],
            "exact_text_collapsed",
        )

    def test_legacy_doc_and_general_zip_require_manual_preparation(self) -> None:
        for filename in ("legacy.doc", "documents.zip"):
            result = self.extractor.extract(
                filename=filename,
                content=b"retained but not parsed",
            )
            self.assertEqual(
                result["extraction_status"],
                "review_required",
            )
            self.assertEqual(result["candidates"], [])

    def test_invalid_docx_fails_closed(self) -> None:
        with self.assertRaises(EvidenceExtractionError):
            self.extractor.extract(
                filename="invalid.docx",
                content=b"not a zip archive",
            )

    @unittest.skipUnless(
        importlib.util.find_spec("pypdf"),
        "pypdf extraction dependency is not installed",
    )
    def test_selectable_pdf_text_is_extracted_with_page_locator(self) -> None:
        result = self.extractor.extract(
            filename="resume.pdf",
            content=minimal_pdf("Managed a global operations program."),
        )
        self.assertEqual(result["extraction_status"], "complete")
        self.assertEqual(
            result["candidates"][0]["source_locator"],
            "page 1, paragraph 1",
        )
        self.assertEqual(
            result["candidates"][0]["evidence_type"],
            "responsibility",
        )


class PIAProtectedEvidenceLinkageTests(unittest.TestCase):
    OWNER_PASSPHRASE = "owner-passphrase-for-tests"
    RECOVERY_PASSPHRASE = "recovery-passphrase-for-tests"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.store_root = root / "participant-store"
        self.store = ProtectedParticipantIntakeStore.create(
            self.store_root,
            owner_passphrase=self.OWNER_PASSPHRASE,
            recovery_path=root / "offline" / "recovery.json",
            recovery_passphrase=self.RECOVERY_PASSPHRASE,
            scanner=FakeScanner(),
            acl_hardener=fake_acl_hardener,
        )
        self.linkage = ProtectedEvidenceIntakeLinkage(self.store)

    def create_session(self, *, scope: str = "evidence_extraction") -> dict:
        return self.store.create_session(
            participant_label="Synthetic Intake Subject Alpha",
            purpose="Evidence extraction and participant review test",
            processing_scope=scope,
            consent_status="granted",
            confidentiality="participant_private",
            retention_class="30_days",
            actor_subject="local-owner",
            actor_role="owner",
        )

    def stage(self, session_id: str) -> dict:
        return self.store.stage_upload(
            session_id=session_id,
            original_filename="resume.txt",
            content=(
                b"EXPERIENCE\n\nManaged an operations team.\n\n"
                b"Reduced processing time by 20 percent."
            ),
            document_type="career_document",
            actor_subject="local-owner",
            actor_role="owner",
        )

    def test_extracted_text_and_candidates_remain_encrypted_at_rest(self) -> None:
        session = self.create_session()
        session_id = session["intake_session_id"]
        artifact = self.stage(session_id)
        extraction = self.linkage.extract(
            session_id=session_id,
            source_artifact_id=artifact["source_artifact_id"],
            actor_subject="local-owner",
            actor_role="owner",
        )
        session_dir = self.store_root / "sessions" / session_id
        session_ciphertext = (session_dir / "session.piaenc").read_bytes()
        extraction_ciphertext = (
            self.store_root / extraction["storage_reference"]
        ).read_bytes()
        self.assertNotIn(b"Managed an operations team", session_ciphertext)
        self.assertNotIn(b"Managed an operations team", extraction_ciphertext)
        self.assertEqual(extraction["capability_assertions_created"], [])
        self.assertTrue(self.store.validate()["accepted"])

        replay = self.linkage.extract(
            session_id=session_id,
            source_artifact_id=artifact["source_artifact_id"],
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(replay["disposition"], "existing_extraction")

        duplicate = self.stage(session_id)
        duplicate_replay = self.linkage.extract(
            session_id=session_id,
            source_artifact_id=duplicate["source_artifact_id"],
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(
            duplicate_replay["extraction_id"],
            extraction["extraction_id"],
        )
        self.assertEqual(
            duplicate_replay["disposition"],
            "existing_extraction",
        )

    def test_review_is_append_only_and_controls_downstream_inclusion(self) -> None:
        session = self.create_session()
        session_id = session["intake_session_id"]
        artifact = self.stage(session_id)
        extraction = self.linkage.extract(
            session_id=session_id,
            source_artifact_id=artifact["source_artifact_id"],
            actor_subject="local-owner",
            actor_role="owner",
        )
        first, second = extraction["evidence_candidates"]
        accepted = self.linkage.review(
            session_id=session_id,
            evidence_id=first["evidence_id"],
            disposition="accepted",
            actor_subject="local-owner",
            actor_role="owner",
        )
        corrected = self.linkage.review(
            session_id=session_id,
            evidence_id=second["evidence_id"],
            disposition="corrected",
            corrected_text="Reduced processing time by approximately 20 percent.",
            reason="Clarified the estimate.",
            actor_subject="local-owner",
            actor_role="owner",
        )
        excluded = self.linkage.review(
            session_id=session_id,
            evidence_id=first["evidence_id"],
            disposition="rejected",
            reason="This line is not useful for the intended analysis.",
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertTrue(
            accepted["evidence_candidate"]["included_in_downstream"]
        )
        self.assertEqual(
            corrected["evidence_candidate"]["review_status"],
            "reviewed",
        )
        self.assertFalse(
            excluded["evidence_candidate"]["included_in_downstream"]
        )
        self.assertEqual(
            excluded["review_event"]["supersedes_review_event_id"],
            accepted["review_event"]["review_event_id"],
        )
        stored = self.store.get_session(session_id, actor_role="owner")
        self.assertEqual(len(stored["evidence_review_events"]), 3)
        self.assertEqual(
            stored["evidence_extractions"][0]["evidence_candidates"][1][
                "extracted_evidence_text"
            ],
            "Reduced processing time by 20 percent.",
        )
        self.assertTrue(self.store.validate()["accepted"])

    def test_tampered_extraction_ciphertext_fails_store_validation(self) -> None:
        session = self.create_session()
        session_id = session["intake_session_id"]
        artifact = self.stage(session_id)
        extraction = self.linkage.extract(
            session_id=session_id,
            source_artifact_id=artifact["source_artifact_id"],
            actor_subject="local-owner",
            actor_role="owner",
        )
        path = self.store_root / extraction["storage_reference"]
        protected = bytearray(path.read_bytes())
        protected[-1] ^= 1
        path.write_bytes(protected)
        validation = self.store.validate()
        self.assertFalse(validation["accepted"])
        self.assertIn(
            "EXTRACTION_DECRYPTION_FAILED",
            {finding["code"] for finding in validation["findings"]},
        )

    def test_parser_failure_is_recorded_without_plaintext_or_candidates(self) -> None:
        session = self.create_session()
        session_id = session["intake_session_id"]
        artifact = self.store.stage_upload(
            session_id=session_id,
            original_filename="invalid.docx",
            content=b"not a docx container",
            document_type="career_document",
            actor_subject="local-owner",
            actor_role="owner",
        )
        extraction = self.linkage.extract(
            session_id=session_id,
            source_artifact_id=artifact["source_artifact_id"],
            actor_subject="local-owner",
            actor_role="owner",
        )
        self.assertEqual(extraction["extraction_status"], "failed")
        self.assertEqual(extraction["evidence_candidates"], [])
        self.assertEqual(extraction["storage_reference"], "")
        self.assertTrue(extraction["warnings"])
        self.assertTrue(self.store.validate()["accepted"])

    def test_extraction_requires_explicit_scope_and_open_consent(self) -> None:
        session = self.create_session(scope="report_generation")
        artifact = self.stage(session["intake_session_id"])
        with self.assertRaises(IntakePreflightError):
            self.linkage.extract(
                session_id=session["intake_session_id"],
                source_artifact_id=artifact["source_artifact_id"],
                actor_subject="local-owner",
                actor_role="owner",
            )

        authorized = self.create_session()
        artifact = self.stage(authorized["intake_session_id"])
        self.store.withdraw_session(
            authorized["intake_session_id"],
            reason="Participant withdrew.",
            actor_subject="local-owner",
            actor_role="owner",
        )
        with self.assertRaises(IntakePreflightError):
            self.linkage.extract(
                session_id=authorized["intake_session_id"],
                source_artifact_id=artifact["source_artifact_id"],
                actor_subject="local-owner",
                actor_role="owner",
            )


if __name__ == "__main__":
    unittest.main()
