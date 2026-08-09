#!/usr/bin/env python3
"""Local-only PIA Intake Phase 2 sandbox storage.

This component implements a reversible synthetic-data sandbox. It deliberately
refuses real-participant mode until an approved encryption-at-rest provider is
configured.

artifact_id: component-pia-local-private-intake-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
STORE_SCHEMA_VERSION = "0.1.0"
MAX_ARTIFACT_BYTES = 25 * 1024 * 1024
SYNTHETIC_PARTICIPANT_PATTERN = re.compile(r"^PIA-9[0-9]{3}$")
SESSION_ID_PATTERN = re.compile(r"^(PIA-9[0-9]{3})-INT-([0-9]{3})$")
ARTIFACT_ID_PATTERN = re.compile(r"^(PIA-9[0-9]{3})-ART-([0-9]{3})$")
SAFE_RETENTION_CLASSES = {"synthetic_test"}
SAFE_CONFIDENTIALITY_CLASSES = {"internal", "restricted", "participant_private"}
SAFE_CONSENT_STATUSES = {"granted", "limited"}
DOCUMENT_TYPES = {
    "professional_profile",
    "career_document",
    "credential_learning",
    "supporting_evidence",
}
ALLOWED_EXTENSIONS = {
    ".csv",
    ".doc",
    ".docx",
    ".pdf",
    ".rtf",
    ".txt",
    ".zip",
}
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x1f\x7f]")


class LocalIntakeError(RuntimeError):
    """Base error for a rejected local-intake operation."""


class ParticipantModeBlockedError(LocalIntakeError):
    """Raised when participant data is requested without approved encryption."""


class IntakePreflightError(LocalIntakeError):
    """Raised when consent, scope, retention, or storage preflight fails."""


class IntakeNotFoundError(LocalIntakeError):
    """Raised when a requested session does not exist."""


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    try:
        temporary.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LocalIntakeError(f"Could not read governed intake record: {path}") from exc
    if not isinstance(value, dict):
        raise LocalIntakeError(f"Governed intake record is not a JSON object: {path}")
    return value


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _safe_original_filename(value: str) -> str:
    name = Path(value).name.strip()
    if (
        not name
        or name in {".", ".."}
        or len(name) > 180
        or CONTROL_CHARACTER_PATTERN.search(name)
    ):
        raise IntakePreflightError("The document filename is invalid.")
    return name


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class LocalIntakeStore:
    """A local Phase 2 store with fail-closed participant-data boundaries."""

    def __init__(self, root: Path | str, *, mode: str = "synthetic") -> None:
        supplied_root = Path(root).expanduser()
        if not supplied_root.is_absolute():
            raise IntakePreflightError("The storage root must be an absolute path.")

        self.root = supplied_root.resolve()
        self.mode = mode
        if _is_within(self.root, REPOSITORY_ROOT):
            raise IntakePreflightError(
                "The intake store must remain outside the Git repository."
            )
        if mode != "synthetic":
            raise ParticipantModeBlockedError(
                "Real-participant staging is blocked: this Phase 2 increment has "
                "no approved encryption-at-rest provider."
            )

    @property
    def manifest_path(self) -> Path:
        return self.root / "store.json"

    @property
    def audit_path(self) -> Path:
        return self.root / "audit.jsonl"

    @property
    def sessions_path(self) -> Path:
        return self.root / "sessions"

    def initialize(self) -> dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        self.sessions_path.mkdir(parents=True, exist_ok=True)
        if self.manifest_path.exists():
            manifest = _read_json(self.manifest_path)
            if manifest.get("schema_version") != STORE_SCHEMA_VERSION:
                raise LocalIntakeError("The local intake-store version is unsupported.")
            if manifest.get("mode") != self.mode:
                raise LocalIntakeError("The existing intake-store mode does not match.")
            return manifest

        manifest = {
            "artifact_id": "store-pia-local-intake-sandbox-001",
            "schema_version": STORE_SCHEMA_VERSION,
            "mode": self.mode,
            "data_boundary": "synthetic_only",
            "encryption_at_rest": "not_implemented_synthetic_only",
            "remote_processing": "disabled",
            "graph_projection": "disabled",
            "created_at": _utc_now(),
        }
        _atomic_json(self.manifest_path, manifest)
        self._append_audit("store_initialized", {"mode": self.mode})
        return manifest

    def _append_audit(self, event_type: str, details: dict[str, Any]) -> None:
        event = {
            "event_id": secrets.token_urlsafe(12),
            "event_type": event_type,
            "occurred_at": _utc_now(),
            "details": details,
        }
        self.root.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def _session_path(self, session_id: str) -> Path:
        if not SESSION_ID_PATTERN.fullmatch(session_id):
            raise IntakePreflightError("The intake-session identifier is invalid.")
        return self.sessions_path / session_id / "session.json"

    def _load_session(self, session_id: str) -> dict[str, Any]:
        path = self._session_path(session_id)
        if not path.exists():
            raise IntakeNotFoundError(f"Intake session {session_id!r} was not found.")
        return _read_json(path)

    def _write_session(self, session: dict[str, Any]) -> None:
        _atomic_json(self._session_path(session["intake_session_id"]), session)

    def _next_session_id(self, participant_id: str) -> str:
        highest = 0
        if self.sessions_path.exists():
            for path in self.sessions_path.iterdir():
                match = SESSION_ID_PATTERN.fullmatch(path.name)
                if match and match.group(1) == participant_id:
                    highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError("The participant has exhausted sandbox session IDs.")
        return f"{participant_id}-INT-{highest + 1:03d}"

    def next_synthetic_participant_id(self) -> str:
        self.initialize()
        used: set[int] = set()
        for path in self.sessions_path.iterdir():
            match = SESSION_ID_PATTERN.fullmatch(path.name)
            if match:
                used.add(int(match.group(1).removeprefix("PIA-")))
        for number in range(9000, 10000):
            if number not in used:
                return f"PIA-{number}"
        raise LocalIntakeError("The sandbox has exhausted synthetic participant IDs.")

    def create_session(
        self,
        *,
        participant_id: str,
        participant_label: str,
        purpose: str,
        processing_scope: str,
        consent_status: str,
        confidentiality: str,
        retention_class: str,
        created_by: str = "local-sandbox-user",
    ) -> dict[str, Any]:
        self.initialize()
        participant_id = participant_id.strip()
        participant_label = participant_label.strip()
        purpose = purpose.strip()
        processing_scope = processing_scope.strip()

        if not SYNTHETIC_PARTICIPANT_PATTERN.fullmatch(participant_id):
            raise IntakePreflightError(
                "Synthetic mode requires a reserved PIA-9000 through PIA-9999 ID."
            )
        if not participant_label or len(participant_label) > 80:
            raise IntakePreflightError("A short, non-identifying participant label is required.")
        if not purpose or len(purpose) > 500:
            raise IntakePreflightError("A bounded processing purpose is required.")
        if not processing_scope or len(processing_scope) > 500:
            raise IntakePreflightError("A bounded processing scope is required.")
        if consent_status not in SAFE_CONSENT_STATUSES:
            raise IntakePreflightError("Consent must be granted or explicitly limited.")
        if confidentiality not in SAFE_CONFIDENTIALITY_CLASSES:
            raise IntakePreflightError("The confidentiality class is not supported.")
        if retention_class not in SAFE_RETENTION_CLASSES:
            raise IntakePreflightError(
                "Only the synthetic_test retention class is enabled in this increment."
            )

        session_id = self._next_session_id(participant_id)
        now = _utc_now()
        session = {
            "schema_version": STORE_SCHEMA_VERSION,
            "intake_session_id": session_id,
            "participant_id": participant_id,
            "participant_label": participant_label,
            "purpose": purpose,
            "processing_scope": processing_scope,
            "consent_status": consent_status,
            "confidentiality": confidentiality,
            "retention_class": retention_class,
            "processing_state": "preflight",
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
            "supersedes_intake_session_id": "",
            "mode": self.mode,
            "remote_processing": "disabled",
            "graph_projection": "disabled",
            "artifacts": [],
        }
        self._write_session(session)
        self._append_audit(
            "session_created",
            {
                "intake_session_id": session_id,
                "participant_id": participant_id,
                "consent_status": consent_status,
                "retention_class": retention_class,
            },
        )
        return session

    def _next_artifact_id(self, session: dict[str, Any]) -> str:
        participant_id = session["participant_id"]
        highest = 0
        for artifact in session.get("artifacts", []):
            match = ARTIFACT_ID_PATTERN.fullmatch(
                str(artifact.get("source_artifact_id", ""))
            )
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError("The participant has exhausted sandbox artifact IDs.")
        return f"{participant_id}-ART-{highest + 1:03d}"

    def stage_upload(
        self,
        *,
        session_id: str,
        original_filename: str,
        content: bytes,
        document_type: str,
        submitted_by: str = "local-sandbox-user",
    ) -> dict[str, Any]:
        session = self._load_session(session_id)
        participant_id = str(session.get("participant_id", ""))
        session_match = SESSION_ID_PATTERN.fullmatch(session_id)
        if (
            not SYNTHETIC_PARTICIPANT_PATTERN.fullmatch(participant_id)
            or session_match is None
            or session_match.group(1) != participant_id
        ):
            raise IntakePreflightError(
                "The stored session identity failed synthetic-boundary validation."
            )
        if session["consent_status"] not in SAFE_CONSENT_STATUSES:
            raise IntakePreflightError("The intake session is not authorized for staging.")
        if session["processing_state"] in {"blocked", "closed"}:
            raise IntakePreflightError("The intake session is not open for staging.")
        if document_type not in DOCUMENT_TYPES:
            raise IntakePreflightError("A supported document type must be selected.")

        filename = _safe_original_filename(original_filename)
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise IntakePreflightError(
                f"The {extension or 'extensionless'} document type is not supported."
            )
        if not content:
            raise IntakePreflightError("The selected document is empty.")
        if len(content) > MAX_ARTIFACT_BYTES:
            raise IntakePreflightError("The selected document exceeds the 25 MB limit.")

        checksum = _sha256_bytes(content)
        duplicate = next(
            (
                artifact
                for artifact in session.get("artifacts", [])
                if artifact.get("checksum") == checksum
            ),
            None,
        )
        artifact_id = self._next_artifact_id(session)
        artifacts_dir = self._session_path(session_id).parent / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        storage_path = (artifacts_dir / f"{artifact_id}.blob").resolve()
        if not _is_within(storage_path, self.root):
            raise IntakePreflightError(
                "The staged-document location escapes the configured store."
            )

        if duplicate is None:
            temporary = storage_path.with_name(
                f".{storage_path.name}.{secrets.token_hex(8)}.tmp"
            )
            try:
                temporary.write_bytes(content)
                if _sha256_bytes(temporary.read_bytes()) != checksum:
                    raise LocalIntakeError("The staged document failed checksum verification.")
                os.replace(temporary, storage_path)
            finally:
                temporary.unlink(missing_ok=True)
            storage_reference = str(storage_path.relative_to(self.root)).replace("\\", "/")
            duplicate_of = ""
            disposition = "staged"
        else:
            storage_reference = duplicate["storage_reference"]
            duplicate_of = duplicate["source_artifact_id"]
            disposition = "exact_duplicate"

        now = _utc_now()
        media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        artifact = {
            "source_artifact_id": artifact_id,
            "intake_session_id": session_id,
            "participant_id": session["participant_id"],
            "artifact_kind": "upload",
            "parent_artifact_id": "",
            "submitted_by": submitted_by,
            "original_filename": filename,
            "media_type": media_type,
            "byte_size": len(content),
            "document_type": document_type,
            "submitted_uri": "",
            "resolved_uri": "",
            "storage_reference": storage_reference,
            "checksum": checksum,
            "content_checksum": "",
            "collected_at": now,
            "retrieved_at": "",
            "confidentiality": session["confidentiality"],
            "consent_scope": session["processing_scope"],
            "extraction_method": "not_applicable",
            "extraction_status": "not_requested",
            "review_status": "pending",
            "created_at": now,
            "supersedes_source_artifact_id": "",
            "duplicate_of_source_artifact_id": duplicate_of,
            "disposition": disposition,
            "malware_scan_status": "not_implemented_synthetic_only",
            "projection_status": "not_requested",
        }
        session["artifacts"].append(artifact)
        session["processing_state"] = "in_progress"
        session["updated_at"] = now
        self._write_session(session)
        self._append_audit(
            "artifact_duplicate_detected" if duplicate else "artifact_staged",
            {
                "intake_session_id": session_id,
                "source_artifact_id": artifact_id,
                "checksum": checksum,
                "duplicate_of_source_artifact_id": duplicate_of,
                "document_type": document_type,
            },
        )
        return artifact

    def get_session(self, session_id: str) -> dict[str, Any]:
        return self._load_session(session_id)

    def validate(self) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        session_count = 0
        artifact_count = 0
        if not self.manifest_path.exists():
            findings.append(
                {
                    "severity": "error",
                    "code": "STORE_NOT_INITIALIZED",
                    "message": "The local intake store has not been initialized.",
                }
            )
            return {
                "accepted": False,
                "counts": {"sessions": 0, "artifacts": 0, "errors": 1},
                "findings": findings,
            }

        manifest = _read_json(self.manifest_path)
        if manifest.get("mode") != "synthetic":
            findings.append(
                {
                    "severity": "error",
                    "code": "PARTICIPANT_MODE_NOT_AUTHORIZED",
                    "message": "Only synthetic sandbox mode is authorized.",
                }
            )

        for session_path in sorted(self.sessions_path.glob("*/session.json")):
            session_count += 1
            session = _read_json(session_path)
            session_id = str(session.get("intake_session_id", ""))
            participant_id = str(session.get("participant_id", ""))
            if not SESSION_ID_PATTERN.fullmatch(session_id):
                findings.append(
                    {
                        "severity": "error",
                        "code": "SESSION_ID_INVALID",
                        "message": f"Invalid intake-session ID: {session_id!r}.",
                    }
                )
            if not SYNTHETIC_PARTICIPANT_PATTERN.fullmatch(participant_id):
                findings.append(
                    {
                        "severity": "error",
                        "code": "NON_SYNTHETIC_PARTICIPANT",
                        "message": f"Non-synthetic participant ID: {participant_id!r}.",
                    }
                )
            if session.get("consent_status") not in SAFE_CONSENT_STATUSES:
                findings.append(
                    {
                        "severity": "error",
                        "code": "SESSION_NOT_AUTHORIZED",
                        "message": f"Session {session_id!r} lacks active authorization.",
                    }
                )
            if session.get("retention_class") not in SAFE_RETENTION_CLASSES:
                findings.append(
                    {
                        "severity": "error",
                        "code": "RETENTION_CLASS_UNSUPPORTED",
                        "message": f"Session {session_id!r} has unsupported retention.",
                    }
                )

            prior_checksums: dict[str, str] = {}
            for artifact in session.get("artifacts", []):
                artifact_count += 1
                artifact_id = str(artifact.get("source_artifact_id", ""))
                checksum = str(artifact.get("checksum", ""))
                duplicate_of = str(
                    artifact.get("duplicate_of_source_artifact_id", "")
                )
                storage_reference = str(artifact.get("storage_reference", ""))
                storage_path = (self.root / storage_reference).resolve()
                if not _is_within(storage_path, self.root):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "STORAGE_REFERENCE_ESCAPES_ROOT",
                            "message": f"Artifact {artifact_id!r} escapes the store.",
                        }
                    )
                    continue
                if not storage_path.is_file():
                    findings.append(
                        {
                            "severity": "error",
                            "code": "STAGED_CONTENT_MISSING",
                            "message": f"Artifact {artifact_id!r} has no stored content.",
                        }
                    )
                    continue
                actual_checksum = _sha256_bytes(storage_path.read_bytes())
                if actual_checksum != checksum:
                    findings.append(
                        {
                            "severity": "error",
                            "code": "CHECKSUM_MISMATCH",
                            "message": f"Artifact {artifact_id!r} failed integrity validation.",
                        }
                    )
                if duplicate_of and prior_checksums.get(checksum) != duplicate_of:
                    findings.append(
                        {
                            "severity": "error",
                            "code": "DUPLICATE_REFERENCE_INVALID",
                            "message": f"Artifact {artifact_id!r} has an invalid duplicate reference.",
                        }
                    )
                prior_checksums.setdefault(checksum, artifact_id)

        errors = sum(1 for finding in findings if finding["severity"] == "error")
        return {
            "accepted": errors == 0,
            "counts": {
                "sessions": session_count,
                "artifacts": artifact_count,
                "errors": errors,
            },
            "findings": findings,
        }
