#!/usr/bin/env python3
"""Protected Windows-local participant intake for PIA Phase 2B.

This working implementation keeps participant artifacts, session metadata, and
audit details encrypted at rest; scans document bytes in memory before
acceptance; and executes withdrawal, deletion, and retention boundaries.

artifact_id: component-pia-protected-participant-intake-001
authority: working
status: proposed
version: 0.5.0
lifecycle_state: formulation
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import secrets
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

from software.intake.local_private_intake import (
    ALLOWED_EXTENSIONS,
    DOCUMENT_TYPES,
    MAX_ARTIFACT_BYTES,
    CONTROL_CHARACTER_PATTERN,
    IntakeNotFoundError,
    IntakePreflightError,
    LocalIntakeError,
    REPOSITORY_ROOT,
)
from software.intake.phase2b_security import (
    EncryptionManager,
    MalwareScanResult,
    OwnerAuthenticator,
    WindowsAMSIScanner,
    add_integrity_tag,
    atomic_bytes,
    atomic_json,
    decrypt_bytes,
    encrypt_bytes,
    harden_windows_directory,
    is_within,
    parse_datetime,
    read_json,
    utc_now,
    verify_integrity_tag,
)


STORE_SCHEMA_VERSION = "0.2.0"
PARTICIPANT_ID_PATTERN = re.compile(r"^PIA-[1-8][0-9]{3}$")
SESSION_ID_PATTERN = re.compile(r"^(PIA-[1-8][0-9]{3})-INT-([0-9]{3})$")
ARTIFACT_ID_PATTERN = re.compile(r"^(PIA-[1-8][0-9]{3})-ART-([0-9]{3})$")
CREDENTIAL_ENTRY_ID_PATTERN = re.compile(
    r"^(PIA-[1-8][0-9]{3})-CRED-([0-9]{3})$"
)
EXTRACTION_ID_PATTERN = re.compile(
    r"^(PIA-[1-8][0-9]{3})-EXT-([0-9]{3})$"
)
EVIDENCE_ID_PATTERN = re.compile(
    r"^(PIA-[1-8][0-9]{3})-EVD-([0-9]{3})$"
)
EVIDENCE_REVIEW_ID_PATTERN = re.compile(
    r"^(PIA-[1-8][0-9]{3})-REV-([0-9]{3})$"
)
CAPABILITY_MAPPING_ID_PATTERN = re.compile(
    r"^(PIA-[1-8][0-9]{3})-MAP-([0-9]{3})$"
)
CAPABILITY_MAPPING_REVIEW_ID_PATTERN = re.compile(
    r"^(PIA-[1-8][0-9]{3})-MRV-([0-9]{3})$"
)
OUTPUT_FEEDBACK_ID_PATTERN = re.compile(r"^(PIA-[1-8][0-9]{3})-OUT-([0-9]{3})$")
LOOKUP_FINGERPRINT_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
RETENTION_DAYS = {
    "14_days": 14,
    "30_days": 30,
    "90_days": 90,
    "365_days": 365,
}
SAFE_CONSENT_STATUSES = {"granted", "limited"}
SAFE_CONFIDENTIALITY_CLASSES = {"restricted", "participant_private"}
SAFE_ACTOR_ROLES = {"owner", "reviewer", "participant"}
REVIEWER_ONLY_ACTIONS = {"capability_mapping", "capability_mapping_review", "report_generation", "credential_resolution"}
OWNER_ONLY_ACTIONS = {"delete", "retention"}
ZERO_HASH = "0" * 64
MAX_RESUMABLE_SESSION_SUMMARIES = 100


class MalwareScanner(Protocol):
    provider_name: str

    def scan(self, content: bytes, *, content_name: str) -> MalwareScanResult:
        ...

    def preflight(self) -> MalwareScanResult:
        ...


def _safe_filename(value: str) -> str:
    name = Path(value).name.strip()
    if (
        not name
        or name in {".", ".."}
        or len(name) > 180
        or CONTROL_CHARACTER_PATTERN.search(name)
    ):
        raise IntakePreflightError("The document filename is invalid.")
    return name


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _require_role(role: str, action: str) -> None:
    if role not in SAFE_ACTOR_ROLES:
        raise IntakePreflightError("The actor role is not authorized.")
    if action in OWNER_ONLY_ACTIONS and role != "owner":
        raise IntakePreflightError(f"Only the owner role may perform {action}.")
    if action in REVIEWER_ONLY_ACTIONS and role not in {"owner", "reviewer"}:
        raise IntakePreflightError(f"Only a reviewer role may perform {action}.")


class ProtectedParticipantIntakeStore:
    """A fail-closed local participant store with executable lifecycle controls."""

    def __init__(
        self,
        root: Path,
        *,
        manifest: dict[str, Any],
        encryption: EncryptionManager,
        scanner: MalwareScanner,
    ) -> None:
        self.root = root
        self.manifest = manifest
        self.encryption = encryption
        self.scanner = scanner
        self.authenticator = OwnerAuthenticator(
            self.root / "auth.json",
            self.encryption.master_key,
        )

    @property
    def manifest_path(self) -> Path:
        return self.root / "store.json"

    @property
    def audit_path(self) -> Path:
        return self.root / "audit.piaenc.jsonl"

    @property
    def sessions_path(self) -> Path:
        return self.root / "sessions"

    @property
    def tombstones_path(self) -> Path:
        return self.root / "tombstones"

    @staticmethod
    def _validate_root(root: Path | str) -> Path:
        supplied = Path(root).expanduser()
        if not supplied.is_absolute():
            raise IntakePreflightError("The protected storage root must be absolute.")
        resolved = supplied.resolve()
        if is_within(resolved, REPOSITORY_ROOT):
            raise IntakePreflightError(
                "The protected participant store must remain outside Git."
            )
        return resolved

    @classmethod
    def create(
        cls,
        root: Path | str,
        *,
        owner_passphrase: str,
        recovery_path: Path | str,
        recovery_passphrase: str,
        scanner: MalwareScanner | None = None,
        acl_hardener: Any = harden_windows_directory,
    ) -> "ProtectedParticipantIntakeStore":
        resolved = cls._validate_root(root)
        if resolved.exists() and any(resolved.iterdir()):
            raise IntakePreflightError(
                "A new participant store must begin in an empty directory."
            )
        resolved.mkdir(parents=True, exist_ok=True)
        acl_summary = acl_hardener(resolved)
        active_scanner = scanner or WindowsAMSIScanner()
        scan_preflight = active_scanner.preflight()
        if not scan_preflight.accepted:
            raise IntakePreflightError(
                "Antimalware preflight did not produce an accepted result."
            )

        store_id = f"PIA-STORE-{secrets.token_hex(8).upper()}"
        encryption, recovery_summary = EncryptionManager.create(
            resolved,
            recovery_path=Path(recovery_path).expanduser(),
            recovery_passphrase=recovery_passphrase,
            store_id=store_id,
        )
        authenticator = OwnerAuthenticator(
            resolved / "auth.json",
            encryption.master_key,
        )
        owner_summary = authenticator.initialize(owner_passphrase)
        now = utc_now()
        manifest = {
            "artifact_id": "store-pia-protected-participant-intake-001",
            "schema_version": STORE_SCHEMA_VERSION,
            "store_id": store_id,
            "mode": "participant",
            "authority": "working",
            "status": "proposed",
            "created_at": now,
            "updated_at": now,
            "controls": {
                "encryption_at_rest": "aes-256-gcm",
                "master_key_protection": "windows-dpapi-current-user",
                "session_key_model": "per-session-wrapped-key",
                "authentication": "scrypt-owner-login",
                "authorization_roles": ["owner", "reviewer"],
                "web_sessions": "memory-only-restart-invalidated",
                "malware_inspection": active_scanner.provider_name,
                "malware_plaintext_staging": "none-in-memory-scan",
                "retention_execution": "enabled",
                "withdrawal_blocking": "enabled",
                "deletion": "session-key-erasure-and-file-removal",
                "remote_processing": "disabled",
                "protected_evidence_extraction": (
                    "authorized-scope-and-review-gated"
                ),
                "participant_free_credential_lookup": "runtime-gated",
                "graph_projection": "disabled",
            },
            "acl_hardened": True,
            "acl_state": str(acl_summary.get("acl_state", "")),
            "acl_identity": str(acl_summary.get("identity", "")),
            "malware_preflight": {
                "status": scan_preflight.status,
                "provider": scan_preflight.provider,
                "result_code": scan_preflight.result_code,
                "scanned_at": scan_preflight.scanned_at,
            },
            "recovery": recovery_summary,
            "owner_account": owner_summary,
        }
        manifest = add_integrity_tag(
            manifest,
            encryption.master_key,
            context="pia-phase2b-store-manifest",
        )
        atomic_json(resolved / "store.json", manifest)
        (resolved / "sessions").mkdir(exist_ok=True)
        (resolved / "tombstones").mkdir(exist_ok=True)
        store = cls(
            resolved,
            manifest=manifest,
            encryption=encryption,
            scanner=active_scanner,
        )
        store._append_audit(
            "protected_store_initialized",
            actor_subject="local-owner",
            actor_role="owner",
            details={
                "store_id": store_id,
                "encryption_at_rest": "aes-256-gcm",
                "malware_inspection": active_scanner.provider_name,
                "recovery_verified_at": recovery_summary["recovery_verified_at"],
            },
        )
        return store

    @classmethod
    def open(
        cls,
        root: Path | str,
        *,
        scanner: MalwareScanner | None = None,
        run_malware_preflight: bool = True,
    ) -> "ProtectedParticipantIntakeStore":
        resolved = cls._validate_root(root)
        manifest = read_json(resolved / "store.json")
        if (
            manifest.get("schema_version") != STORE_SCHEMA_VERSION
            or manifest.get("mode") != "participant"
        ):
            raise IntakePreflightError("This is not a supported Phase 2B store.")
        controls = manifest.get("controls", {})
        if not isinstance(controls, dict) or (
            controls.get("encryption_at_rest"),
            controls.get("master_key_protection"),
            controls.get("remote_processing"),
            controls.get("graph_projection"),
        ) != (
            "aes-256-gcm",
            "windows-dpapi-current-user",
            "disabled",
            "disabled",
        ):
            raise IntakePreflightError("Required Phase 2B controls are not declared.")
        if manifest.get("acl_hardened") is not True:
            raise IntakePreflightError("The participant-store ACL gate is not satisfied.")
        encryption = EncryptionManager.open(resolved)
        if not verify_integrity_tag(
            manifest,
            encryption.master_key,
            context="pia-phase2b-store-manifest",
        ):
            raise IntakePreflightError(
                "The participant-store manifest failed integrity validation."
            )
        active_scanner = scanner or WindowsAMSIScanner()
        if run_malware_preflight:
            scan_preflight = active_scanner.preflight()
            if not scan_preflight.accepted:
                raise IntakePreflightError(
                    "Current antimalware preflight did not produce an accepted result."
                )
        store = cls(
            resolved,
            manifest=manifest,
            encryption=encryption,
            scanner=active_scanner,
        )
        if not store.authenticator.path.is_file():
            raise IntakePreflightError("The local owner account is missing.")
        return store

    def _session_dir(self, session_id: str) -> Path:
        if not SESSION_ID_PATTERN.fullmatch(session_id):
            raise IntakePreflightError("The participant session identifier is invalid.")
        path = (self.sessions_path / session_id).resolve()
        if not is_within(path, self.sessions_path.resolve()):
            raise IntakePreflightError("The participant session escapes the store.")
        return path

    def _session_paths(self, session_id: str) -> tuple[Path, Path]:
        directory = self._session_dir(session_id)
        return directory / "session-key.piaenc", directory / "session.piaenc"

    def _load_session(self, session_id: str) -> tuple[dict[str, Any], bytes]:
        key_path, record_path = self._session_paths(session_id)
        if not key_path.is_file() or not record_path.is_file():
            raise IntakeNotFoundError(f"Participant session {session_id!r} was not found.")
        session_key = self.encryption.unwrap_session_key(
            session_id,
            key_path.read_bytes(),
        )
        try:
            session = json.loads(
                decrypt_bytes(
                    session_key,
                    record_path.read_bytes(),
                    aad=f"session-record:{session_id}",
                )
            )
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise LocalIntakeError("The encrypted session record is invalid.") from exc
        if not isinstance(session, dict) or session.get("intake_session_id") != session_id:
            raise LocalIntakeError("The encrypted session identity does not match its path.")
        return session, session_key

    def _write_session(
        self,
        session: dict[str, Any],
        session_key: bytes,
    ) -> None:
        session_id = str(session["intake_session_id"])
        _, record_path = self._session_paths(session_id)
        atomic_bytes(
            record_path,
            encrypt_bytes(
                session_key,
                _canonical_json(session),
                aad=f"session-record:{session_id}",
            ),
        )

    def _read_audit(self) -> list[dict[str, Any]]:
        if not self.audit_path.exists():
            return []
        records: list[dict[str, Any]] = []
        try:
            lines = self.audit_path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            raise LocalIntakeError("The protected audit log could not be read.") from exc
        for expected_sequence, line in enumerate(lines, start=1):
            try:
                envelope = json.loads(line)
                sequence = int(envelope["sequence"])
                protected = bytes.fromhex(str(envelope["protected_event"]))
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                raise LocalIntakeError("The protected audit envelope is invalid.") from exc
            if sequence != expected_sequence:
                raise LocalIntakeError("The protected audit sequence is discontinuous.")
            try:
                event = json.loads(
                    decrypt_bytes(
                        self.encryption.master_key,
                        protected,
                        aad=f"audit-event:{sequence}",
                    )
                )
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise LocalIntakeError("The protected audit event is invalid.") from exc
            if not isinstance(event, dict) or event.get("sequence") != sequence:
                raise LocalIntakeError("The protected audit event identity is invalid.")
            records.append(event)
        return records

    def _append_audit(
        self,
        event_type: str,
        *,
        actor_subject: str,
        actor_role: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        _require_role(actor_role, "audit")
        records = self._read_audit()
        prior_hash = records[-1]["event_hash"] if records else ZERO_HASH
        event = {
            "sequence": len(records) + 1,
            "event_id": secrets.token_urlsafe(12),
            "event_type": event_type,
            "occurred_at": utc_now(),
            "actor_subject": actor_subject,
            "actor_role": actor_role,
            "previous_event_hash": prior_hash,
            "details": details,
        }
        event["event_hash"] = _sha256(_canonical_json(event))
        protected = encrypt_bytes(
            self.encryption.master_key,
            _canonical_json(event),
            aad=f"audit-event:{event['sequence']}",
        )
        envelope = {
            "sequence": event["sequence"],
            "protected_event": protected.hex(),
        }
        with self.audit_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(envelope, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event

    def _next_participant_id(self) -> str:
        used: set[int] = set()
        if self.sessions_path.exists():
            for directory in self.sessions_path.iterdir():
                match = SESSION_ID_PATTERN.fullmatch(directory.name)
                if match:
                    used.add(int(match.group(1).removeprefix("PIA-")))
        if self.tombstones_path.exists():
            for tombstone_path in self.tombstones_path.glob("*.json"):
                match = SESSION_ID_PATTERN.fullmatch(
                    tombstone_path.stem
                )
                if match:
                    used.add(
                        int(match.group(1).removeprefix("PIA-"))
                    )
        for number in range(1000, 9000):
            if number not in used:
                return f"PIA-{number}"
        raise LocalIntakeError("The protected store has exhausted participant IDs.")

    def _next_session_id(self, participant_id: str) -> str:
        highest = 0
        for directory in self.sessions_path.iterdir():
            match = SESSION_ID_PATTERN.fullmatch(directory.name)
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        for tombstone_path in self.tombstones_path.glob("*.json"):
            match = SESSION_ID_PATTERN.fullmatch(tombstone_path.stem)
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError("The participant has exhausted intake-session IDs.")
        return f"{participant_id}-INT-{highest + 1:03d}"

    def create_session(
        self,
        *,
        participant_label: str,
        purpose: str,
        processing_scope: str,
        consent_status: str,
        confidentiality: str,
        retention_class: str,
        actor_subject: str,
        actor_role: str,
        participant_id: str | None = None,
    ) -> dict[str, Any]:
        _require_role(actor_role, "create_session")
        participant_label = participant_label.strip()
        purpose = purpose.strip()
        processing_scope = processing_scope.strip()
        if not participant_label or len(participant_label) > 80:
            raise IntakePreflightError("A short participant label is required.")
        if not purpose or len(purpose) > 500:
            raise IntakePreflightError("A bounded processing purpose is required.")
        if not processing_scope or len(processing_scope) > 500:
            raise IntakePreflightError("A bounded processing scope is required.")
        if consent_status not in SAFE_CONSENT_STATUSES:
            raise IntakePreflightError("Consent must be granted or explicitly limited.")
        if confidentiality not in SAFE_CONFIDENTIALITY_CLASSES:
            raise IntakePreflightError("Participant data must be restricted or private.")
        if retention_class not in RETENTION_DAYS:
            raise IntakePreflightError("A supported finite retention class is required.")
        participant_id = participant_id or self._next_participant_id()
        if not PARTICIPANT_ID_PATTERN.fullmatch(participant_id):
            raise IntakePreflightError("The participant pseudonym is invalid.")

        session_id = self._next_session_id(participant_id)
        session_dir = self._session_dir(session_id)
        tombstone_path = self.tombstones_path / f"{session_id}.json"
        if tombstone_path.exists():
            raise LocalIntakeError(
                "A deleted participant session identifier may never be "
                "reused."
            )
        if session_dir.exists():
            raise LocalIntakeError("The participant session already exists.")
        session_dir.mkdir(parents=True)
        (session_dir / "artifacts").mkdir()
        (session_dir / "extractions").mkdir()
        session_key = secrets.token_bytes(32)
        key_path, _ = self._session_paths(session_id)
        atomic_bytes(
            key_path,
            self.encryption.wrap_session_key(session_id, session_key),
        )
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=RETENTION_DAYS[retention_class])
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
            "retention_expires_at": expires_at.isoformat(timespec="seconds").replace(
                "+00:00", "Z"
            ),
            "processing_state": "preflight",
            "created_by": actor_subject,
            "created_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "updated_at": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "withdrawn_at": "",
            "withdrawal_reason": "",
            "remote_processing": "disabled",
            "graph_projection": "disabled",
            "artifacts": [],
            "evidence_extractions": [],
            "evidence_review_events": [],
            "capability_mapping_proposals": [],
            "capability_mapping_review_events": [],
            "output_feedback_events": [],
            "credential_resolutions": [],
        }
        self._write_session(session, session_key)
        self._append_audit(
            "participant_session_created",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "participant_id": participant_id,
                "consent_status": consent_status,
                "retention_class": retention_class,
                "retention_expires_at": session["retention_expires_at"],
            },
        )
        return session

    def submit_for_review(
        self,
        session_id: str,
        *,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Record a participant-complete evidence handoff for reviewer work."""

        _require_role(actor_role, "submit_for_review")
        session, session_key = self._load_session(session_id)
        if actor_role == "participant" and session.get("created_by") != actor_subject:
            raise IntakePreflightError(
                "A participant may submit only their own protected workspace."
            )
        if session.get("consent_status") not in SAFE_CONSENT_STATUSES:
            raise IntakePreflightError(
                "This session is not authorized for reviewer handoff."
            )
        if session.get("processing_state") in {"blocked", "closed", "deleted"}:
            raise IntakePreflightError(
                "This session is not open for reviewer handoff."
            )
        candidates = [
            candidate
            for extraction in session.get("evidence_extractions", [])
            for candidate in extraction.get("evidence_candidates", [])
        ]
        if not candidates:
            raise IntakePreflightError(
                "Prepare and review evidence before submitting this workspace."
            )
        if any(
            candidate.get("review_status") == "unreviewed"
            for candidate in candidates
        ):
            raise IntakePreflightError(
                "Review every evidence item before submitting this workspace."
            )
        included = [
            candidate
            for candidate in candidates
            if candidate.get("included_in_downstream") is True
        ]
        if not included:
            raise IntakePreflightError(
                "Keep at least one evidence item before submitting this workspace."
            )
        now = utc_now()
        session["processing_state"] = "awaiting_review"
        session["submitted_for_review_at"] = now
        session["submitted_for_review_by"] = actor_subject
        session["updated_at"] = now
        self._write_session(session, session_key)
        self._append_audit(
            "participant_evidence_submitted_for_review",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "reviewed_evidence_count": len(candidates),
                "included_evidence_count": len(included),
            },
        )
        return {
            "intake_session_id": session_id,
            "processing_state": session["processing_state"],
            "reviewed_evidence_count": len(candidates),
            "included_evidence_count": len(included),
            "submitted_for_review_at": now,
        }

    def complete_evidence_review(
        self,
        session_id: str,
        *,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Close authorized evidence review and release the governed next stage."""

        _require_role(actor_role, "capability_mapping")
        session, session_key = self._load_session(session_id)
        if session.get("processing_state") != "awaiting_review":
            raise IntakePreflightError(
                "Only a participant-submitted workspace may complete evidence review."
            )
        candidates = [
            candidate
            for extraction in session.get("evidence_extractions", [])
            for candidate in extraction.get("evidence_candidates", [])
        ]
        reviewer_decisions = {
            str(event.get("target_record_id", ""))
            for event in session.get("evidence_review_events", [])
            if event.get("actor_role") in {"owner", "reviewer"}
        }
        evidence_groups: dict[str, list[dict[str, Any]]] = {}
        for candidate in candidates:
            evidence_key = " ".join(
                str(candidate.get("evidence_text", "")).split()
            ).casefold()
            evidence_groups.setdefault(evidence_key, []).append(candidate)
        missing = [
            evidence_key
            for evidence_key, group in evidence_groups.items()
            if not any(
                candidate.get("evidence_id") in reviewer_decisions
                for candidate in group
            )
        ]
        if missing:
            raise IntakePreflightError(
                f"Review every submitted evidence item before completion ({len(missing)} remaining)."
            )
        accepted = [
            group
            for group in evidence_groups.values()
            if any(
                candidate.get("included_in_downstream") is True
                for candidate in group
            )
        ]
        if not accepted:
            raise IntakePreflightError(
                "Accept at least one evidence item before completing review."
            )
        now = utc_now()
        session["processing_state"] = "review_complete"
        session["evidence_review_completed_at"] = now
        session["evidence_review_completed_by"] = actor_subject
        session["updated_at"] = now
        self._write_session(session, session_key)
        self._append_audit(
            "participant_evidence_review_completed",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "accepted_evidence_count": len(accepted),
                "next_stage": "capability_mapping_and_report_assurance",
                "graph_write": "not_performed",
            },
        )
        return {
            "intake_session_id": session_id,
            "processing_state": "review_complete",
            "accepted_evidence_count": len(accepted),
            "next_stage": "capability_mapping_and_report_assurance",
            "graph_write": "not_performed",
        }

    def _next_artifact_id(self, session: dict[str, Any]) -> str:
        participant_id = str(session["participant_id"])
        highest = 0
        for artifact in session.get("artifacts", []):
            match = ARTIFACT_ID_PATTERN.fullmatch(
                str(artifact.get("source_artifact_id", ""))
            )
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError("The participant has exhausted artifact IDs.")
        return f"{participant_id}-ART-{highest + 1:03d}"

    def stage_upload(
        self,
        *,
        session_id: str,
        original_filename: str,
        content: bytes,
        document_type: str,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        _require_role(actor_role, "stage_upload")
        session, session_key = self._load_session(session_id)
        if session.get("consent_status") not in SAFE_CONSENT_STATUSES:
            raise IntakePreflightError("This session is not authorized for staging.")
        if session.get("processing_state") in {"blocked", "closed", "deleted"}:
            raise IntakePreflightError("This session is not open for staging.")
        if parse_datetime(str(session["retention_expires_at"])) <= datetime.now(UTC):
            raise IntakePreflightError(
                "The session retention period has expired; staging is blocked."
            )
        if document_type not in DOCUMENT_TYPES:
            raise IntakePreflightError("A supported document type must be selected.")
        filename = _safe_filename(original_filename)
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise IntakePreflightError("The selected document type is not supported.")
        if not content:
            raise IntakePreflightError("The selected document is empty.")
        if len(content) > MAX_ARTIFACT_BYTES:
            raise IntakePreflightError("The selected document exceeds the 25 MB limit.")

        scan = self.scanner.scan(content, content_name=filename)
        if not scan.accepted:
            self._append_audit(
                "artifact_rejected_by_malware_gate",
                actor_subject=actor_subject,
                actor_role=actor_role,
                details={
                    "intake_session_id": session_id,
                    "provider": scan.provider,
                    "scan_status": scan.status,
                    "result_code": scan.result_code,
                    "scanned_at": scan.scanned_at,
                },
            )
            raise IntakePreflightError(
                "The document was blocked by malware inspection and was not stored."
            )

        checksum = _sha256(content)
        duplicate = next(
            (
                artifact
                for artifact in session.get("artifacts", [])
                if artifact.get("checksum") == checksum
            ),
            None,
        )
        artifact_id = self._next_artifact_id(session)
        artifacts_dir = (self._session_dir(session_id) / "artifacts").resolve()
        storage_path = (artifacts_dir / f"{artifact_id}.piaenc").resolve()
        if not is_within(storage_path, artifacts_dir):
            raise IntakePreflightError("The artifact location escapes the session.")

        if duplicate is None:
            atomic_bytes(
                storage_path,
                encrypt_bytes(
                    session_key,
                    content,
                    aad=f"artifact:{artifact_id}:{checksum}",
                ),
            )
            storage_reference = str(storage_path.relative_to(self.root)).replace(
                "\\", "/"
            )
            duplicate_of = ""
            disposition = "staged"
        else:
            storage_reference = str(duplicate["storage_reference"])
            duplicate_of = str(duplicate["source_artifact_id"])
            disposition = "exact_duplicate"

        now = utc_now()
        artifact = {
            "source_artifact_id": artifact_id,
            "intake_session_id": session_id,
            "participant_id": session["participant_id"],
            "artifact_kind": "upload",
            "submitted_by": actor_subject,
            "original_filename": filename,
            "media_type": mimetypes.guess_type(filename)[0]
            or "application/octet-stream",
            "byte_size": len(content),
            "document_type": document_type,
            "storage_reference": storage_reference,
            "checksum": checksum,
            "collected_at": now,
            "confidentiality": session["confidentiality"],
            "consent_scope": session["processing_scope"],
            "malware_scan_status": scan.status,
            "malware_scan_provider": scan.provider,
            "malware_scan_result_code": scan.result_code,
            "malware_scanned_at": scan.scanned_at,
            "extraction_status": "not_requested",
            "review_status": "pending",
            "created_at": now,
            "duplicate_of_source_artifact_id": duplicate_of,
            "disposition": disposition,
            "projection_status": "not_requested",
        }
        session["artifacts"].append(artifact)
        session["processing_state"] = "in_progress"
        session["updated_at"] = now
        self._write_session(session, session_key)
        self._append_audit(
            "artifact_duplicate_detected" if duplicate else "artifact_staged_encrypted",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "source_artifact_id": artifact_id,
                "checksum": checksum,
                "document_type": document_type,
                "duplicate_of_source_artifact_id": duplicate_of,
                "malware_scan_status": scan.status,
            },
        )
        return artifact

    def get_session(
        self,
        session_id: str,
        *,
        actor_role: str,
    ) -> dict[str, Any]:
        _require_role(actor_role, "read_session")
        session, _ = self._load_session(session_id)
        return session

    def list_resumable_sessions(
        self,
        *,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Return a bounded, minimal index of active protected sessions."""

        _require_role(actor_role, "read_session")
        now = datetime.now(UTC)
        summaries: list[dict[str, Any]] = []
        for directory in sorted(self.sessions_path.iterdir()):
            if (
                not directory.is_dir()
                or not SESSION_ID_PATTERN.fullmatch(directory.name)
            ):
                continue
            if (
                self.tombstones_path / f"{directory.name}.json"
            ).exists():
                raise LocalIntakeError(
                    "The protected store contains an active session whose "
                    "identifier was already deleted. Resolve the integrity "
                    "finding before continuing."
                )
            session, _ = self._load_session(directory.name)
            if (
                actor_role == "participant"
                and session.get("created_by") != actor_subject
            ):
                continue
            if (
                session.get("consent_status") not in SAFE_CONSENT_STATUSES
                or session.get("processing_state")
                in {"blocked", "closed", "deleted"}
                or parse_datetime(str(session["retention_expires_at"])) <= now
            ):
                continue
            candidates = [
                candidate
                for extraction in session.get(
                    "evidence_extractions", []
                )
                for candidate in extraction.get(
                    "evidence_candidates", []
                )
            ]
            reviewed_count = sum(
                1
                for candidate in candidates
                if candidate.get("review_status") != "unreviewed"
            )
            artifact_count = len(session.get("artifacts", []))
            credential_count = len(
                session.get("credential_resolutions", [])
            )
            summaries.append(
                {
                    "intake_session_id": session["intake_session_id"],
                    "participant_label": session["participant_label"],
                    "processing_state": session["processing_state"],
                    "processing_scope": session["processing_scope"],
                    "retention_expires_at": session[
                        "retention_expires_at"
                    ],
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"],
                    "artifact_count": artifact_count,
                    "evidence_candidate_count": len(candidates),
                    "evidence_reviewed_count": reviewed_count,
                    "evidence_pending_count": (
                        len(candidates) - reviewed_count
                    ),
                    "credential_count": credential_count,
                    "has_saved_work": bool(
                        artifact_count
                        or candidates
                        or credential_count
                    ),
                }
            )
        summaries.sort(
            key=lambda item: str(item["updated_at"]),
            reverse=True,
        )
        truncated = (
            len(summaries) > MAX_RESUMABLE_SESSION_SUMMARIES
        )
        visible = summaries[:MAX_RESUMABLE_SESSION_SUMMARIES]
        self._append_audit(
            "resumable_session_index_viewed",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "visible_session_count": len(visible),
                "truncated": truncated,
            },
        )
        return {
            "sessions": visible,
            "truncated": truncated,
        }

    def resume_session(
        self,
        session_id: str,
        *,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Open an active session for authenticated local continuation."""

        _require_role(actor_role, "read_session")
        if (
            self.tombstones_path / f"{session_id}.json"
        ).exists():
            raise LocalIntakeError(
                "This identifier has a deletion record and cannot be "
                "resumed."
            )
        session, _ = self._load_session(session_id)
        if (
            actor_role == "participant"
            and session.get("created_by") != actor_subject
        ):
            raise IntakePreflightError(
                "A participant may resume only their own protected workspace."
            )
        if session.get("consent_status") not in SAFE_CONSENT_STATUSES:
            raise IntakePreflightError(
                "This session can no longer be resumed because authorization "
                "is not active."
            )
        if session.get("processing_state") in {
            "blocked",
            "closed",
            "deleted",
        }:
            raise IntakePreflightError(
                "This session is not open for continued processing."
            )
        if parse_datetime(
            str(session["retention_expires_at"])
        ) <= datetime.now(UTC):
            raise IntakePreflightError(
                "This session cannot be resumed because retention has expired."
            )
        self._append_audit(
            "participant_session_resumed",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "processing_state": session["processing_state"],
            },
        )
        return session

    @staticmethod
    def _require_open_processing_scope(
        session: dict[str, Any],
        *,
        required_scope: str,
        activity_label: str,
    ) -> None:
        if session.get("consent_status") not in SAFE_CONSENT_STATUSES:
            raise IntakePreflightError(
                f"This session is not authorized for {activity_label}."
            )
        if session.get("processing_state") in {"blocked", "closed", "deleted"}:
            raise IntakePreflightError(
                f"This session is not open for {activity_label}."
            )
        if parse_datetime(str(session["retention_expires_at"])) <= datetime.now(
            UTC
        ):
            raise IntakePreflightError(
                "The session retention period has expired."
            )
        scopes = {
            value.strip()
            for value in str(session.get("processing_scope", "")).split("|")
            if value.strip()
        }
        if required_scope not in scopes:
            raise IntakePreflightError(
                f"{activity_label.capitalize()} is outside this session's "
                "authorized scope."
            )

    @classmethod
    def _require_open_credential_scope(
        cls,
        session: dict[str, Any],
    ) -> None:
        cls._require_open_processing_scope(
            session,
            required_scope="credential_definition",
            activity_label="credential resolution",
        )

    @classmethod
    def _require_open_evidence_scope(
        cls,
        session: dict[str, Any],
    ) -> None:
        cls._require_open_processing_scope(
            session,
            required_scope="evidence_extraction",
            activity_label="evidence extraction",
        )

    @classmethod
    def _require_open_mapping_scope(
        cls,
        session: dict[str, Any],
    ) -> None:
        scopes = {
            value.strip()
            for value in str(session.get("processing_scope", "")).split("|")
            if value.strip()
        }
        # Participant report sessions created before the explicit capability
        # scope was added remain eligible for the authorized reviewer handoff.
        if "capability_mapping" not in scopes and not (
            "participant_report" in scopes or "evidence_report" in scopes
        ):
            cls._require_open_processing_scope(
                session,
                required_scope="capability_mapping",
                activity_label="capability mapping",
            )
            return
        if "capability_mapping" not in scopes:
            cls._require_open_processing_scope(
                session,
                required_scope=(
                    "participant_report"
                    if "participant_report" in scopes
                    else "evidence_report"
                ),
                activity_label="capability mapping",
            )
            return
        cls._require_open_processing_scope(
            session,
            required_scope="capability_mapping",
            activity_label="capability mapping",
        )

    @staticmethod
    def _find_artifact(
        session: dict[str, Any],
        source_artifact_id: str,
    ) -> dict[str, Any]:
        for artifact in session.get("artifacts", []):
            if artifact.get("source_artifact_id") == source_artifact_id:
                return artifact
        raise IntakeNotFoundError(
            f"Source artifact {source_artifact_id!r} was not found."
        )

    def read_artifact_content(
        self,
        *,
        session_id: str,
        source_artifact_id: str,
        actor_subject: str,
        actor_role: str,
    ) -> tuple[dict[str, Any], bytes]:
        """Decrypt one authorized source artifact without writing plaintext."""

        _require_role(actor_role, "evidence_extraction")
        session, session_key = self._load_session(session_id)
        self._require_open_evidence_scope(session)
        artifact = self._find_artifact(session, source_artifact_id)
        checksum = str(artifact.get("checksum", ""))
        duplicate_of = str(
            artifact.get("duplicate_of_source_artifact_id", "")
        )
        storage_path = (
            self.root / str(artifact.get("storage_reference", ""))
        ).resolve()
        if not is_within(storage_path, self._session_dir(session_id).resolve()):
            raise IntakePreflightError(
                "The artifact location escapes its participant session."
            )
        if not storage_path.is_file():
            raise IntakeNotFoundError(
                "The encrypted source artifact is missing."
            )
        content = decrypt_bytes(
            session_key,
            storage_path.read_bytes(),
            aad=f"artifact:{duplicate_of or source_artifact_id}:{checksum}",
        )
        if _sha256(content) != checksum:
            raise LocalIntakeError(
                "The decrypted source artifact failed its integrity check."
            )
        self._append_audit(
            "artifact_opened_for_evidence_extraction",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "source_artifact_id": source_artifact_id,
                "checksum": checksum,
            },
        )
        return artifact, content

    @staticmethod
    def _next_extraction_id(session: dict[str, Any]) -> str:
        participant_id = str(session["participant_id"])
        highest = 0
        for record in session.get("evidence_extractions", []):
            match = EXTRACTION_ID_PATTERN.fullmatch(
                str(record.get("extraction_id", ""))
            )
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError(
                "The participant has exhausted evidence-extraction IDs."
            )
        return f"{participant_id}-EXT-{highest + 1:03d}"

    @staticmethod
    def _next_evidence_number(session: dict[str, Any]) -> int:
        participant_id = str(session["participant_id"])
        highest = 0
        for extraction in session.get("evidence_extractions", []):
            for candidate in extraction.get("evidence_candidates", []):
                match = EVIDENCE_ID_PATTERN.fullmatch(
                    str(candidate.get("evidence_id", ""))
                )
                if match and match.group(1) == participant_id:
                    highest = max(highest, int(match.group(2)))
        return highest + 1

    @staticmethod
    def _next_evidence_review_id(session: dict[str, Any]) -> str:
        participant_id = str(session["participant_id"])
        highest = 0
        for event in session.get("evidence_review_events", []):
            match = EVIDENCE_REVIEW_ID_PATTERN.fullmatch(
                str(event.get("review_event_id", ""))
            )
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError(
                "The participant has exhausted evidence-review IDs."
            )
        return f"{participant_id}-REV-{highest + 1:03d}"

    def save_evidence_extraction(
        self,
        *,
        session_id: str,
        source_artifact_id: str,
        result: dict[str, Any],
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Persist extraction text and candidates inside the encrypted session."""

        _require_role(actor_role, "evidence_extraction")
        session, session_key = self._load_session(session_id)
        self._require_open_evidence_scope(session)
        artifact = self._find_artifact(session, source_artifact_id)
        records = session.setdefault("evidence_extractions", [])
        if not isinstance(records, list):
            raise LocalIntakeError(
                "The encrypted evidence-extraction collection is invalid."
            )
        parser_id = str(result.get("parser_id", ""))
        for existing in records:
            if (
                existing.get("source_artifact_id") == source_artifact_id
                and existing.get("source_artifact_checksum")
                == artifact.get("checksum")
                and existing.get("parser_id") == parser_id
            ):
                replay = dict(existing)
                replay["disposition"] = "existing_extraction"
                return replay

        status = str(result.get("extraction_status", ""))
        if status not in {"complete", "failed", "review_required"}:
            raise IntakePreflightError(
                "The extraction result has an invalid status."
            )
        text = str(result.get("extracted_text", ""))
        text_checksum = str(result.get("extracted_text_checksum", ""))
        if text and _sha256(text.encode("utf-8")) != text_checksum:
            raise IntakePreflightError(
                "The extracted text checksum does not match its content."
            )
        candidates = result.get("candidates", [])
        warnings = result.get("warnings", [])
        if (
            not isinstance(candidates, list)
            or not isinstance(warnings, list)
            or result.get("capability_assertions_created") != []
        ):
            raise IntakePreflightError(
                "The extraction result crosses the evidence-only boundary."
            )

        extraction_id = self._next_extraction_id(session)
        first_evidence_number = self._next_evidence_number(session)
        evidence_candidates: list[dict[str, Any]] = []
        for offset, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                raise IntakePreflightError(
                    "An evidence candidate is invalid."
                )
            evidence_number = first_evidence_number + offset
            if evidence_number > 999:
                raise LocalIntakeError(
                    "The participant has exhausted evidence IDs."
                )
            evidence_text = str(candidate.get("evidence_text", "")).strip()
            if not evidence_text or len(evidence_text) > 2_000:
                raise IntakePreflightError(
                    "Evidence candidate text is empty or too long."
                )
            evidence_type = str(candidate.get("evidence_type", ""))
            if evidence_type not in {
                "activity",
                "responsibility",
                "output",
                "achievement",
                "event",
                "condition",
                "statement",
                "other",
            }:
                raise IntakePreflightError(
                    "An evidence candidate type is invalid."
                )
            evidence_candidates.append(
                {
                    **candidate,
                    "evidence_id": (
                        f"{session['participant_id']}-EVD-"
                        f"{evidence_number:03d}"
                    ),
                    "source_id": source_artifact_id,
                    "participant_id": session["participant_id"],
                    "extracted_evidence_text": evidence_text,
                    "evidence_text": evidence_text,
                    "review_status": "unreviewed",
                    "included_in_downstream": False,
                    "record_version": 1,
                    "created_at": utc_now(),
                    "updated_at": utc_now(),
                }
            )

        storage_reference = ""
        if text:
            extraction_dir = (
                self._session_dir(session_id) / "extractions"
            ).resolve()
            extraction_dir.mkdir(exist_ok=True)
            if not is_within(
                extraction_dir,
                self._session_dir(session_id).resolve(),
            ):
                raise IntakePreflightError(
                    "The extraction location escapes the session."
                )
            storage_path = (
                extraction_dir / f"{extraction_id}.piaenc"
            ).resolve()
            atomic_bytes(
                storage_path,
                encrypt_bytes(
                    session_key,
                    text.encode("utf-8"),
                    aad=f"extraction:{extraction_id}:{text_checksum}",
                ),
            )
            storage_reference = str(
                storage_path.relative_to(self.root)
            ).replace("\\", "/")

        now = utc_now()
        record = {
            "extraction_id": extraction_id,
            "intake_session_id": session_id,
            "participant_id": session["participant_id"],
            "source_artifact_id": source_artifact_id,
            "source_artifact_checksum": artifact["checksum"],
            "extraction_status": status,
            "parser_id": parser_id,
            "parser_profile": str(result.get("parser_profile", "")),
            "source_extension": str(result.get("source_extension", "")),
            "storage_reference": storage_reference,
            "extracted_text_checksum": text_checksum,
            "extracted_character_count": len(text),
            "evidence_candidates": evidence_candidates,
            "warnings": [str(item)[:500] for item in warnings],
            "created_by": actor_subject,
            "created_at": now,
            "updated_at": now,
            "capability_assertions_created": [],
            "disposition": "created",
        }
        records.append(record)
        session.setdefault("evidence_review_events", [])
        artifact["extraction_status"] = status
        artifact["extraction_method"] = (
            "automated"
            if status in {"complete", "failed"}
            else "not_applicable"
        )
        session["updated_at"] = now
        self._write_session(session, session_key)
        self._append_audit(
            (
                "evidence_extraction_failed"
                if status == "failed"
                else (
                    "evidence_extraction_review_required"
                    if status == "review_required"
                    else "evidence_extraction_created"
                )
            ),
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "source_artifact_id": source_artifact_id,
                "extraction_id": extraction_id,
                "extraction_status": status,
                "candidate_count": len(evidence_candidates),
                "parser_id": parser_id,
                "capability_assertion_count": 0,
            },
        )
        return record

    def list_evidence_extractions(
        self,
        *,
        session_id: str,
        actor_role: str,
    ) -> list[dict[str, Any]]:
        _require_role(actor_role, "read_session")
        session, _ = self._load_session(session_id)
        self._require_open_evidence_scope(session)
        records = session.get("evidence_extractions", [])
        if not isinstance(records, list):
            raise LocalIntakeError(
                "The encrypted evidence-extraction collection is invalid."
            )
        return records

    def review_evidence_candidate(
        self,
        *,
        session_id: str,
        evidence_id: str,
        disposition: str,
        corrected_text: str,
        reason: str,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Append a review event and update the current candidate view."""

        _require_role(actor_role, "evidence_review")
        if disposition not in {
            "accepted",
            "corrected",
            "rejected",
            "disputed",
        }:
            raise IntakePreflightError(
                "The evidence review disposition is invalid."
            )
        session, session_key = self._load_session(session_id)
        self._require_open_evidence_scope(session)
        candidate: dict[str, Any] | None = None
        for extraction in session.get("evidence_extractions", []):
            for item in extraction.get("evidence_candidates", []):
                if item.get("evidence_id") == evidence_id:
                    candidate = item
                    extraction["updated_at"] = utc_now()
                    break
            if candidate is not None:
                break
        if candidate is None:
            raise IntakeNotFoundError(
                f"Evidence candidate {evidence_id!r} was not found."
            )
        corrected_text = corrected_text.strip()
        reason = reason.strip()
        if len(reason) > 500:
            raise IntakePreflightError(
                "The evidence review reason is too long."
            )
        if disposition == "corrected":
            if not corrected_text or len(corrected_text) > 2_000:
                raise IntakePreflightError(
                    "A correction of 1 to 2,000 characters is required."
                )
            candidate["evidence_text"] = corrected_text
            candidate["review_status"] = "reviewed"
            candidate["included_in_downstream"] = True
        elif disposition == "accepted":
            if corrected_text:
                raise IntakePreflightError(
                    "Accepted evidence cannot include correction text."
                )
            candidate["review_status"] = "reviewed"
            candidate["included_in_downstream"] = True
        elif disposition == "rejected":
            if corrected_text:
                raise IntakePreflightError(
                    "Rejected evidence cannot include correction text."
                )
            candidate["review_status"] = "superseded"
            candidate["included_in_downstream"] = False
        else:
            if corrected_text:
                raise IntakePreflightError(
                    "Disputed evidence cannot include correction text."
                )
            candidate["review_status"] = "disputed"
            candidate["included_in_downstream"] = False
        candidate["record_version"] = int(
            candidate.get("record_version", 1)
        ) + 1
        candidate["updated_at"] = utc_now()

        events = session.setdefault("evidence_review_events", [])
        if not isinstance(events, list):
            raise LocalIntakeError(
                "The encrypted evidence-review collection is invalid."
            )
        prior_review_event_id = next(
            (
                str(event.get("review_event_id", ""))
                for event in reversed(events)
                if event.get("target_record_id") == evidence_id
            ),
            "",
        )
        event = {
            "review_event_id": self._next_evidence_review_id(session),
            "intake_session_id": session_id,
            "target_record_type": "evidence_candidate",
            "target_record_id": evidence_id,
            "target_record_version": candidate["record_version"],
            "actor_role": actor_role,
            "actor_reference": actor_subject,
            "disposition": disposition,
            "field_scope": (
                "evidence_text"
                if disposition == "corrected"
                else "review_status"
            ),
            "reason": reason or f"Evidence candidate {disposition}.",
            "response_text": corrected_text,
            "supporting_source_artifact_ids": [
                candidate["source_id"]
            ],
            "created_at": utc_now(),
            "supersedes_review_event_id": prior_review_event_id,
        }
        events.append(event)
        session["updated_at"] = utc_now()
        self._write_session(session, session_key)
        self._append_audit(
            "evidence_candidate_reviewed",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "evidence_id": evidence_id,
                "review_event_id": event["review_event_id"],
                "disposition": disposition,
                "included_in_downstream": candidate[
                    "included_in_downstream"
                ],
            },
        )
        return {
            "evidence_candidate": candidate,
            "review_event": event,
            "capability_assertions_created": [],
        }

    @staticmethod
    def _next_capability_mapping_id(session: dict[str, Any]) -> str:
        participant_id = str(session["participant_id"])
        highest = 0
        for record in session.get("capability_mapping_proposals", []):
            match = CAPABILITY_MAPPING_ID_PATTERN.fullmatch(
                str(record.get("mapping_id", ""))
            )
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError(
                "The participant has exhausted capability-mapping IDs."
            )
        return f"{participant_id}-MAP-{highest + 1:03d}"

    @staticmethod
    def _mapping_text(
        proposal: dict[str, Any],
        key: str,
        *,
        maximum: int = 2_000,
    ) -> str:
        value = str(proposal.get(key, "")).strip()
        if not value or len(value) > maximum:
            raise IntakePreflightError(
                f"Capability mapping field {key!r} is missing or too long."
            )
        return value

    def create_capability_mapping_proposal(
        self,
        *,
        session_id: str,
        evidence_id: str,
        proposal: dict[str, Any],
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Create a review-required mapping proposal from accepted evidence."""

        _require_role(actor_role, "capability_mapping")
        session, session_key = self._load_session(session_id)
        self._require_open_mapping_scope(session)
        candidate: dict[str, Any] | None = None
        for extraction in session.get("evidence_extractions", []):
            for item in extraction.get("evidence_candidates", []):
                if item.get("evidence_id") == evidence_id:
                    candidate = item
                    break
            if candidate is not None:
                break
        if candidate is None:
            raise IntakeNotFoundError(
                f"Evidence candidate {evidence_id!r} was not found."
            )
        if (
            candidate.get("review_status") != "reviewed"
            or candidate.get("included_in_downstream") is not True
            or not candidate.get("source_id")
            or not candidate.get("source_locator")
        ):
            raise IntakePreflightError(
                "Only accepted, source-grounded evidence may enter mapping."
            )
        if not isinstance(proposal, dict):
            raise IntakePreflightError("The capability mapping proposal is invalid.")

        inference_level = self._mapping_text(proposal, "inference_level", maximum=64)
        evidence_role = self._mapping_text(proposal, "evidence_role", maximum=64)
        claim_scope = self._mapping_text(proposal, "claim_scope", maximum=64)
        application_status = self._mapping_text(
            proposal, "application_status", maximum=64
        )
        if inference_level not in {
            "directly_demonstrated",
            "strongly_inferred",
            "contextually_suggested",
        }:
            raise IntakePreflightError("The mapping inference level is invalid.")
        if evidence_role not in {
            "behavioral_demonstration",
            "educational_preparation",
        }:
            raise IntakePreflightError("The mapping evidence role is invalid.")
        if claim_scope not in {"demonstrated_application", "knowledge_exposure"}:
            raise IntakePreflightError("The mapping claim scope is invalid.")
        if application_status not in {
            "described_in_source",
            "explicitly_attributed_in_source",
            "topically_aligned_not_verified",
            "not_established",
        }:
            raise IntakePreflightError("The mapping application status is invalid.")
        try:
            confidence = float(proposal.get("confidence"))
        except (TypeError, ValueError) as exc:
            raise IntakePreflightError("Mapping confidence must be numeric.") from exc
        if not 0.0 <= confidence <= 1.0:
            raise IntakePreflightError("Mapping confidence must be from 0.00 to 1.00.")

        profile_capability_id = self._mapping_text(
            proposal, "profile_capability_id", maximum=160
        )
        capability_name = self._mapping_text(proposal, "capability_name", maximum=200)
        mapping_profile = self._mapping_text(proposal, "mapping_profile", maximum=100)
        if mapping_profile != "pia-capability-evidence-mapping-0.2":
            raise IntakePreflightError("The capability mapping profile is invalid.")
        if evidence_role == "behavioral_demonstration":
            if claim_scope != "demonstrated_application":
                raise IntakePreflightError(
                    "Behavioral evidence must retain demonstrated-application scope."
                )
        else:
            if (
                inference_level != "contextually_suggested"
                or claim_scope != "knowledge_exposure"
                or confidence > 0.49
            ):
                raise IntakePreflightError(
                    "Educational preparation must remain a low-confidence "
                    "knowledge-exposure proposal."
                )
        if inference_level == "contextually_suggested" and confidence > 0.49:
            raise IntakePreflightError(
                "A contextual suggestion cannot exceed 0.49 confidence."
            )
        if inference_level == "strongly_inferred" and confidence > 0.89:
            raise IntakePreflightError(
                "An unreviewed strong inference cannot exceed 0.89 confidence."
            )
        credential_definition_status = str(
            proposal.get("credential_definition_status", "")
        ).strip()
        credential_definition_source = str(
            proposal.get("credential_definition_source", "")
        ).strip()
        credential_definition_uri = str(
            proposal.get("credential_definition_uri", "")
        ).strip()
        credential_domain_scope = str(
            proposal.get("credential_domain_scope", "")
        ).strip()
        definition_expansion_required = (
            proposal.get("definition_expansion_required") is True
        )
        if evidence_role == "educational_preparation":
            if credential_definition_status not in {
                "source_defined",
                "issuer_verified",
                "participant_defined",
                "title_only_unknown",
                "conflicting_definition",
            } or not credential_definition_source:
                raise IntakePreflightError(
                    "Educational preparation requires a bounded credential definition."
                )
            if (
                credential_definition_status
                in {"title_only_unknown", "conflicting_definition"}
                and not definition_expansion_required
            ):
                raise IntakePreflightError(
                    "An unresolved credential definition requires expansion."
                )
            if credential_definition_status == "issuer_verified" and (
                not credential_definition_uri or not credential_domain_scope
            ):
                raise IntakePreflightError(
                    "Issuer-verified preparation requires its source and domain scope."
                )

        record = {
            "mapping_id": self._next_capability_mapping_id(session),
            "intake_session_id": session_id,
            "participant_id": session["participant_id"],
            "evidence_id": evidence_id,
            "source_id": candidate["source_id"],
            "source_locator": candidate["source_locator"],
            "capability_id": profile_capability_id,
            "profile_capability_id": profile_capability_id,
            "capability_name": capability_name,
            "relationship_type": "SUPPORTS",
            "mapping_profile": mapping_profile,
            "confidence": confidence,
            "confidence_basis": self._mapping_text(proposal, "confidence_basis"),
            "proposed_by": actor_subject,
            "review_status": (
                "needs_review"
                if inference_level == "contextually_suggested"
                or evidence_role == "educational_preparation"
                else "proposed"
            ),
            "human_review_required": True,
            "relationship_semantic_class": "analytical_assertion",
            "inference_level": inference_level,
            "evidence_role": evidence_role,
            "claim_scope": claim_scope,
            "application_status": application_status,
            "aligned_experience_ids": str(
                proposal.get("aligned_experience_ids", "")
            ).strip()[:2_000],
            "alignment_basis": self._mapping_text(proposal, "alignment_basis"),
            "credential_definition_status": credential_definition_status,
            "credential_definition_source": credential_definition_source,
            "credential_definition_uri": credential_definition_uri,
            "credential_domain_scope": credential_domain_scope,
            "definition_expansion_required": definition_expansion_required,
            "behavioral_basis": self._mapping_text(proposal, "behavioral_basis"),
            "negative_boundary": self._mapping_text(proposal, "negative_boundary"),
            "scope_limit": self._mapping_text(proposal, "scope_limit"),
            "source_independence_note": self._mapping_text(
                proposal, "source_independence_note"
            ),
            "created_at": utc_now(),
            "reviewed_at": "",
            "mapping_disposition": "proposed",
            "replaces_mapping_id": str(proposal.get("replaces_mapping_id", "")).strip(),
        }
        records = session.setdefault("capability_mapping_proposals", [])
        if not isinstance(records, list):
            raise LocalIntakeError(
                "The encrypted capability-mapping collection is invalid."
            )
        records.append(record)
        session["updated_at"] = utc_now()
        self._write_session(session, session_key)
        self._append_audit(
            "capability_mapping_proposed",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "mapping_id": record["mapping_id"],
                "evidence_id": evidence_id,
                "profile_capability_id": profile_capability_id,
                "review_status": record["review_status"],
                "graph_projection": "not_created",
            },
        )
        return record

    def list_capability_mapping_proposals(
        self,
        *,
        session_id: str,
        actor_role: str,
    ) -> list[dict[str, Any]]:
        _require_role(actor_role, "read_session")
        session, _ = self._load_session(session_id)
        records = session.get("capability_mapping_proposals", [])
        if not isinstance(records, list):
            raise LocalIntakeError(
                "The encrypted capability-mapping collection is invalid."
            )
        return records

    def request_output_update(self, *, session_id: str, note: str, actor_subject: str, actor_role: str) -> dict[str, Any]:
        _require_role(actor_role, "read_session")
        note = note.strip()
        if not note or len(note) > 500:
            raise IntakePreflightError("An output-update request of 1 to 500 characters is required.")
        session, key = self._load_session(session_id)
        events = session.setdefault("output_feedback_events", [])
        participant_id = str(session["participant_id"])
        event_id = f"{participant_id}-OUT-{len(events) + 1:03d}"
        event = {"output_feedback_event_id": event_id, "intake_session_id": session_id, "note": note, "status": "requested", "actor_reference": actor_subject, "actor_role": actor_role, "created_at": utc_now(), "changes_evidence": False, "changes_mapping": False}
        events.append(event); session["updated_at"] = utc_now(); self._write_session(session, key)
        self._append_audit("output_update_requested", actor_subject=actor_subject, actor_role=actor_role, details={"intake_session_id": session_id, "output_feedback_event_id": event_id})
        return event

    @staticmethod
    def _next_capability_mapping_review_id(session: dict[str, Any]) -> str:
        participant_id = str(session["participant_id"])
        highest = 0
        for event in session.get("capability_mapping_review_events", []):
            match = CAPABILITY_MAPPING_REVIEW_ID_PATTERN.fullmatch(
                str(event.get("mapping_review_event_id", ""))
            )
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError(
                "The participant has exhausted capability-mapping review IDs."
            )
        return f"{participant_id}-MRV-{highest + 1:03d}"

    def review_capability_mapping_proposal(
        self,
        *,
        session_id: str,
        mapping_id: str,
        disposition: str,
        reason: str,
        narrowed_scope_limit: str,
        narrowed_negative_boundary: str,
        actor_subject: str,
        actor_role: str,
        allow_same_actor: bool = False,
    ) -> dict[str, Any]:
        """Review or supersede a proposal without altering its history."""

        _require_role(actor_role, "capability_mapping_review")
        if disposition not in {"accepted", "rejected", "narrowed"}:
            raise IntakePreflightError("The mapping review disposition is invalid.")
        session, session_key = self._load_session(session_id)
        self._require_open_mapping_scope(session)
        records = session.get("capability_mapping_proposals", [])
        if not isinstance(records, list):
            raise LocalIntakeError(
                "The encrypted capability-mapping collection is invalid."
            )
        mapping = next(
            (item for item in records if item.get("mapping_id") == mapping_id),
            None,
        )
        if mapping is None:
            raise IntakeNotFoundError(
                f"Capability mapping {mapping_id!r} was not found."
            )
        if mapping.get("review_status") not in {"proposed", "needs_review"}:
            raise IntakePreflightError(
                "Only an unresolved mapping proposal may be reviewed."
            )
        if actor_subject == mapping.get("proposed_by") and not allow_same_actor:
            raise IntakePreflightError(
                "A mapping proposal requires a reviewer distinct from its proposer."
            )
        reason = reason.strip()
        if not reason or len(reason) > 500:
            raise IntakePreflightError(
                "A mapping review reason of 1 to 500 characters is required."
            )
        now = utc_now()
        replacement: dict[str, Any] | None = None
        if disposition == "narrowed":
            narrowed_scope_limit = narrowed_scope_limit.strip()
            narrowed_negative_boundary = narrowed_negative_boundary.strip()
            if (
                not narrowed_scope_limit
                or not narrowed_negative_boundary
                or len(narrowed_scope_limit) > 2_000
                or len(narrowed_negative_boundary) > 2_000
            ):
                raise IntakePreflightError(
                    "A narrowed scope limit and negative boundary are required."
                )
            mapping["review_status"] = "superseded"
            mapping["mapping_disposition"] = "superseded"
            mapping["updated_at"] = now
            replacement = {
                **mapping,
                "mapping_id": self._next_capability_mapping_id(session),
                "scope_limit": narrowed_scope_limit,
                "negative_boundary": narrowed_negative_boundary,
                "review_status": "accepted",
                "mapping_disposition": "accepted_with_narrowed_scope",
                "reviewed_at": now,
                "reviewed_by": actor_subject,
                "human_review_required": False,
                "supersedes_mapping_id": mapping_id,
                "created_at": now,
                "updated_at": now,
            }
            records.append(replacement)
            result_mapping = replacement
        else:
            replacement_target = str(mapping.get("replaces_mapping_id", ""))
            if disposition == "accepted" and replacement_target:
                prior = next(
                    (item for item in records if item.get("mapping_id") == replacement_target),
                    None,
                )
                if prior is None or prior.get("review_status") != "accepted":
                    raise IntakePreflightError(
                        "A revised mapping must replace an accepted current mapping."
                    )
                prior["review_status"] = "superseded"
                prior["mapping_disposition"] = "superseded"
                prior["updated_at"] = now
                mapping["supersedes_mapping_id"] = replacement_target
            mapping["review_status"] = disposition
            mapping["mapping_disposition"] = disposition
            mapping["reviewed_at"] = now
            mapping["reviewed_by"] = actor_subject
            mapping["human_review_required"] = disposition != "accepted"
            mapping["updated_at"] = now
            result_mapping = mapping
        events = session.setdefault("capability_mapping_review_events", [])
        if not isinstance(events, list):
            raise LocalIntakeError(
                "The encrypted capability-mapping review collection is invalid."
            )
        event = {
            "mapping_review_event_id": self._next_capability_mapping_review_id(session),
            "intake_session_id": session_id,
            "target_mapping_id": mapping_id,
            "result_mapping_id": result_mapping["mapping_id"],
            "actor_role": actor_role,
            "actor_reference": actor_subject,
            "disposition": disposition,
            "reason": reason,
            "created_at": now,
            "decision_mode": (
                "reviewer_direct_acceptance"
                if allow_same_actor
                else "independent_proposal_review"
            ),
        }
        events.append(event)
        session["updated_at"] = now
        self._write_session(session, session_key)
        self._append_audit(
            "capability_mapping_reviewed",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "mapping_id": mapping_id,
                "result_mapping_id": result_mapping["mapping_id"],
                "disposition": disposition,
            },
        )
        return {"mapping": result_mapping, "review_event": event}

    @staticmethod
    def _next_credential_entry_id(
        session: dict[str, Any],
    ) -> str:
        participant_id = str(session["participant_id"])
        highest = 0
        for record in session.get("credential_resolutions", []):
            match = CREDENTIAL_ENTRY_ID_PATTERN.fullmatch(
                str(record.get("credential_entry_id", ""))
            )
            if match and match.group(1) == participant_id:
                highest = max(highest, int(match.group(2)))
        if highest >= 999:
            raise LocalIntakeError(
                "The participant has exhausted credential-entry IDs."
            )
        return f"{participant_id}-CRED-{highest + 1:03d}"

    def save_credential_resolution(
        self,
        *,
        session_id: str,
        credential_entry_id: str,
        descriptor: dict[str, Any],
        local_lookup: dict[str, Any],
        external_lookup: dict[str, Any],
        clarification: dict[str, str] | None,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Store a private reference-resolution relationship encrypted in-session."""
        _require_role(actor_role, "credential_resolution")
        session, session_key = self._load_session(session_id)
        self._require_open_credential_scope(session)

        expected_descriptor_fields = {
            "credential_title",
            "issuer_hint",
            "version_hint",
            "credential_type_hint",
            "jurisdiction_hint",
            "source_scope",
            "purpose",
        }
        if (
            not isinstance(descriptor, dict)
            or set(descriptor) != expected_descriptor_fields
            or not all(
                isinstance(value, str) for value in descriptor.values()
            )
            or not descriptor.get("credential_title", "").strip()
        ):
            raise IntakePreflightError(
                "The minimized credential descriptor is invalid."
            )
        if (
            not isinstance(local_lookup, dict)
            or local_lookup.get("participant_claims_established") != []
            or not LOOKUP_FINGERPRINT_PATTERN.fullmatch(
                str(local_lookup.get("request_fingerprint", ""))
            )
            or not str(local_lookup.get("lookup_request_id", "")).startswith(
                "CRED-LOOKUP-"
            )
        ):
            raise IntakePreflightError(
                "The public catalog lookup result is invalid."
            )
        if (
            not isinstance(external_lookup, dict)
            or external_lookup.get("participant_claims_established", [])
            != []
            or external_lookup.get("definition_accepted", False) is not False
        ):
            raise IntakePreflightError(
                "The external registry result crosses the acceptance boundary."
            )

        records = session.setdefault("credential_resolutions", [])
        if not isinstance(records, list):
            raise LocalIntakeError(
                "The encrypted credential-resolution collection is invalid."
            )
        existing: dict[str, Any] | None = None
        if credential_entry_id:
            match = CREDENTIAL_ENTRY_ID_PATTERN.fullmatch(
                credential_entry_id
            )
            if (
                match is None
                or match.group(1) != session.get("participant_id")
            ):
                raise IntakePreflightError(
                    "The credential-entry identifier is invalid."
                )
            existing = next(
                (
                    record
                    for record in records
                    if record.get("credential_entry_id")
                    == credential_entry_id
                ),
                None,
            )
            if existing is None:
                raise IntakeNotFoundError(
                    f"Credential entry {credential_entry_id!r} was not found."
                )
        else:
            credential_entry_id = self._next_credential_entry_id(session)

        now = utc_now()
        history = list(
            existing.get("clarification_history", []) if existing else []
        )
        if clarification is not None:
            field = str(clarification.get("field", "")).strip()
            response = str(clarification.get("response", "")).strip()
            if (
                field
                not in {
                    "credential_title",
                    "issuer_hint",
                    "version_hint",
                }
                or not response
                or len(response) > 300
                or CONTROL_CHARACTER_PATTERN.search(response)
            ):
                raise IntakePreflightError(
                    "The credential clarification is invalid."
                )
            history.append(
                {
                    "field": field,
                    "response": response,
                    "recorded_at": now,
                    "recorded_by": actor_subject,
                }
            )

        record = {
            "credential_entry_id": credential_entry_id,
            "descriptor": descriptor,
            "local_lookup": local_lookup,
            "external_lookup": external_lookup,
            "clarification_history": history,
            "created_at": (
                existing.get("created_at", now) if existing else now
            ),
            "updated_at": now,
        }
        if existing is None:
            records.append(record)
            event_type = "credential_reference_resolution_created"
        else:
            records[records.index(existing)] = record
            event_type = "credential_reference_resolution_updated"
        session["processing_state"] = "in_progress"
        session["updated_at"] = now
        self._write_session(session, session_key)
        self._append_audit(
            event_type,
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "credential_entry_id": credential_entry_id,
                "lookup_request_id": local_lookup["lookup_request_id"],
                "routing_outcome": local_lookup["routing_outcome"],
                "external_disposition": external_lookup.get(
                    "disposition", ""
                ),
                "clarification_recorded": clarification is not None,
            },
        )
        return record

    def get_credential_resolution(
        self,
        session_id: str,
        *,
        credential_entry_id: str,
        actor_role: str,
    ) -> dict[str, Any]:
        _require_role(actor_role, "read_session")
        session, _ = self._load_session(session_id)
        for record in session.get("credential_resolutions", []):
            if record.get("credential_entry_id") == credential_entry_id:
                return record
        raise IntakeNotFoundError(
            f"Credential entry {credential_entry_id!r} was not found."
        )

    def list_credential_resolutions(
        self,
        session_id: str,
        *,
        actor_role: str,
    ) -> list[dict[str, Any]]:
        _require_role(actor_role, "read_session")
        session, _ = self._load_session(session_id)
        records = session.get("credential_resolutions", [])
        if not isinstance(records, list):
            raise LocalIntakeError(
                "The encrypted credential-resolution collection is invalid."
            )
        return records

    def withdraw_session(
        self,
        session_id: str,
        *,
        reason: str,
        actor_subject: str,
        actor_role: str,
        delete_now: bool = False,
    ) -> dict[str, Any]:
        _require_role(actor_role, "withdraw")
        reason = reason.strip()
        if not reason or len(reason) > 500:
            raise IntakePreflightError("A bounded withdrawal reason is required.")
        session, session_key = self._load_session(session_id)
        if (
            actor_role == "participant"
            and session.get("created_by") != actor_subject
        ):
            raise IntakePreflightError(
                "A participant may withdraw only their own protected workspace."
            )
        now = utc_now()
        session["consent_status"] = "withdrawn"
        session["processing_state"] = "blocked"
        session["withdrawn_at"] = now
        session["withdrawal_reason"] = reason
        session["updated_at"] = now
        self._write_session(session, session_key)
        self._append_audit(
            "participant_session_withdrawn",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "withdrawn_at": now,
                "delete_now": delete_now,
                "reason": reason,
            },
        )
        if delete_now:
            return self.delete_session(
                session_id,
                reason_code="withdrawal",
                actor_subject=actor_subject,
                actor_role=actor_role,
            )
        return session

    @staticmethod
    def _erase_key_file(path: Path) -> None:
        if not path.is_file():
            return
        size = path.stat().st_size
        with path.open("r+b", buffering=0) as handle:
            handle.write(secrets.token_bytes(size))
            handle.flush()
            os.fsync(handle.fileno())
        path.unlink(missing_ok=True)

    def delete_session(
        self,
        session_id: str,
        *,
        reason_code: str,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        if actor_role == "participant":
            _require_role(actor_role, "withdraw")
        else:
            _require_role(actor_role, "delete")
        if reason_code not in {
            "participant_request",
            "withdrawal",
            "retention_expired",
            "test_cleanup",
        }:
            raise IntakePreflightError("The deletion reason code is unsupported.")
        session, _ = self._load_session(session_id)
        if (
            actor_role == "participant"
            and session.get("created_by") != actor_subject
        ):
            raise IntakePreflightError(
                "A participant may delete only their own protected workspace."
            )
        directory = self._session_dir(session_id)
        if not is_within(directory, self.sessions_path.resolve()):
            raise IntakePreflightError("The deletion target escapes the session store.")
        deleted_at = utc_now()
        self._append_audit(
            "participant_session_deleted",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "intake_session_id": session_id,
                "participant_id": session["participant_id"],
                "reason_code": reason_code,
                "artifact_count": len(session.get("artifacts", [])),
                "deleted_at": deleted_at,
                "deletion_method": "session-key-erasure-and-file-removal",
            },
        )
        key_path, _ = self._session_paths(session_id)
        self._erase_key_file(key_path)
        shutil.rmtree(directory)
        tombstone = {
            "format": "pia-phase2b-deletion-tombstone-v1",
            "intake_session_id": session_id,
            "participant_id": session["participant_id"],
            "reason_code": reason_code,
            "deleted_at": deleted_at,
            "deleted_by_role": actor_role,
            "participant_content_retained": False,
            "graph_projection_removed": "not_applicable_projection_disabled",
        }
        tombstone = add_integrity_tag(
            tombstone,
            self.encryption.master_key,
            context=f"pia-phase2b-tombstone:{session_id}",
        )
        atomic_json(self.tombstones_path / f"{session_id}.json", tombstone)
        return tombstone

    def enforce_retention(
        self,
        *,
        actor_subject: str,
        actor_role: str,
        now: datetime | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        _require_role(actor_role, "retention")
        effective_now = now or datetime.now(UTC)
        expired: list[str] = []
        deleted: list[str] = []
        for directory in sorted(self.sessions_path.iterdir()):
            if not directory.is_dir() or not SESSION_ID_PATTERN.fullmatch(directory.name):
                continue
            session, _ = self._load_session(directory.name)
            if parse_datetime(str(session["retention_expires_at"])) <= effective_now:
                expired.append(directory.name)
        if not dry_run:
            for session_id in expired:
                self.delete_session(
                    session_id,
                    reason_code="retention_expired",
                    actor_subject=actor_subject,
                    actor_role=actor_role,
                )
                deleted.append(session_id)
        self._append_audit(
            "retention_evaluated",
            actor_subject=actor_subject,
            actor_role=actor_role,
            details={
                "evaluated_at": effective_now.isoformat(timespec="seconds").replace(
                    "+00:00", "Z"
                ),
                "dry_run": dry_run,
                "expired_session_ids": expired,
                "deleted_session_ids": deleted,
            },
        )
        return {
            "evaluated_at": effective_now.isoformat(timespec="seconds").replace(
                "+00:00", "Z"
            ),
            "dry_run": dry_run,
            "expired_session_ids": expired,
            "deleted_session_ids": deleted,
        }

    def validate(self, *, now: datetime | None = None) -> dict[str, Any]:
        findings: list[dict[str, str]] = []
        session_count = 0
        artifact_count = 0
        evidence_extraction_count = 0
        evidence_candidate_count = 0
        evidence_review_count = 0
        credential_resolution_count = 0
        audit_count = 0
        tombstone_count = 0
        effective_now = now or datetime.now(UTC)
        if not verify_integrity_tag(
            self.manifest,
            self.encryption.master_key,
            context="pia-phase2b-store-manifest",
        ):
            findings.append(
                {
                    "severity": "error",
                    "code": "STORE_MANIFEST_INTEGRITY_FAILED",
                    "message": "The participant-store manifest failed validation.",
                }
            )
        try:
            self.authenticator.identity()
        except LocalIntakeError as exc:
            findings.append(
                {
                    "severity": "error",
                    "code": "ACCOUNT_REGISTRY_INTEGRITY_FAILED",
                    "message": str(exc),
                }
            )
        try:
            records = self._read_audit()
            audit_count = len(records)
            prior_hash = ZERO_HASH
            for event in records:
                claimed_hash = str(event.get("event_hash", ""))
                unhashed = dict(event)
                unhashed.pop("event_hash", None)
                if event.get("previous_event_hash") != prior_hash or _sha256(
                    _canonical_json(unhashed)
                ) != claimed_hash:
                    findings.append(
                        {
                            "severity": "error",
                            "code": "AUDIT_CHAIN_INVALID",
                            "message": "The protected audit chain failed validation.",
                        }
                    )
                    break
                prior_hash = claimed_hash
        except LocalIntakeError as exc:
            findings.append(
                {
                    "severity": "error",
                    "code": "AUDIT_DECRYPTION_FAILED",
                    "message": str(exc),
                }
            )

        for directory in sorted(self.sessions_path.iterdir()):
            if not directory.is_dir() or not SESSION_ID_PATTERN.fullmatch(directory.name):
                continue
            session_count += 1
            try:
                session, session_key = self._load_session(directory.name)
            except LocalIntakeError as exc:
                findings.append(
                    {
                        "severity": "error",
                        "code": "SESSION_DECRYPTION_FAILED",
                        "message": str(exc),
                    }
                )
                continue
            if parse_datetime(str(session["retention_expires_at"])) <= effective_now:
                findings.append(
                    {
                        "severity": "error",
                        "code": "RETENTION_EXECUTION_OVERDUE",
                        "message": f"Session {directory.name!r} has expired.",
                    }
                )
            if session.get("consent_status") == "withdrawn" and session.get(
                "processing_state"
            ) != "blocked":
                findings.append(
                    {
                        "severity": "error",
                        "code": "WITHDRAWN_SESSION_NOT_BLOCKED",
                        "message": f"Session {directory.name!r} is not blocked.",
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
                storage_path = (
                    self.root / str(artifact.get("storage_reference", ""))
                ).resolve()
                if not is_within(storage_path, directory.resolve()):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "ARTIFACT_REFERENCE_ESCAPES_SESSION",
                            "message": f"Artifact {artifact_id!r} escapes its session.",
                        }
                    )
                    continue
                if not storage_path.is_file():
                    findings.append(
                        {
                            "severity": "error",
                            "code": "ENCRYPTED_ARTIFACT_MISSING",
                            "message": f"Artifact {artifact_id!r} is missing.",
                        }
                    )
                    continue
                try:
                    content = decrypt_bytes(
                        session_key,
                        storage_path.read_bytes(),
                        aad=f"artifact:{duplicate_of or artifact_id}:{checksum}",
                    )
                except LocalIntakeError as exc:
                    findings.append(
                        {
                            "severity": "error",
                            "code": "ARTIFACT_DECRYPTION_FAILED",
                            "message": f"{artifact_id!r}: {exc}",
                        }
                    )
                    continue
                if _sha256(content) != checksum:
                    findings.append(
                        {
                            "severity": "error",
                            "code": "ARTIFACT_CHECKSUM_MISMATCH",
                            "message": f"Artifact {artifact_id!r} failed checksum validation.",
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

            source_artifact_ids = {
                str(artifact.get("source_artifact_id", ""))
                for artifact in session.get("artifacts", [])
            }
            seen_extractions: set[str] = set()
            seen_evidence: set[str] = set()
            extraction_records = session.get("evidence_extractions", [])
            if not isinstance(extraction_records, list):
                findings.append(
                    {
                        "severity": "error",
                        "code": "EVIDENCE_EXTRACTION_COLLECTION_INVALID",
                        "message": (
                            f"Session {directory.name!r} has an invalid "
                            "evidence-extraction collection."
                        ),
                    }
                )
                extraction_records = []
            for extraction in extraction_records:
                evidence_extraction_count += 1
                if not isinstance(extraction, dict):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "EVIDENCE_EXTRACTION_INVALID",
                            "message": (
                                f"Session {directory.name!r} contains an "
                                "invalid evidence-extraction record."
                            ),
                        }
                    )
                    continue
                extraction_id = str(extraction.get("extraction_id", ""))
                extraction_match = EXTRACTION_ID_PATTERN.fullmatch(
                    extraction_id
                )
                source_artifact_id = str(
                    extraction.get("source_artifact_id", "")
                )
                status = str(extraction.get("extraction_status", ""))
                if (
                    extraction_match is None
                    or extraction_match.group(1)
                    != session.get("participant_id")
                    or extraction_id in seen_extractions
                    or source_artifact_id not in source_artifact_ids
                    or status not in {
                        "complete",
                        "failed",
                        "review_required",
                    }
                    or extraction.get("capability_assertions_created") != []
                ):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "EVIDENCE_EXTRACTION_INVALID",
                            "message": (
                                f"Evidence extraction {extraction_id!r} "
                                "failed its identity or boundary checks."
                            ),
                        }
                    )
                seen_extractions.add(extraction_id)
                text_checksum = str(
                    extraction.get("extracted_text_checksum", "")
                )
                storage_reference = str(
                    extraction.get("storage_reference", "")
                )
                if storage_reference:
                    extraction_path = (
                        self.root / storage_reference
                    ).resolve()
                    if (
                        not is_within(extraction_path, directory.resolve())
                        or not extraction_path.is_file()
                    ):
                        findings.append(
                            {
                                "severity": "error",
                                "code": "ENCRYPTED_EXTRACTION_MISSING",
                                "message": (
                                    f"Evidence extraction {extraction_id!r} "
                                    "is missing or escapes its session."
                                ),
                            }
                        )
                    else:
                        try:
                            extracted_text = decrypt_bytes(
                                session_key,
                                extraction_path.read_bytes(),
                                aad=(
                                    f"extraction:{extraction_id}:"
                                    f"{text_checksum}"
                                ),
                            )
                        except LocalIntakeError as exc:
                            findings.append(
                                {
                                    "severity": "error",
                                    "code": "EXTRACTION_DECRYPTION_FAILED",
                                    "message": f"{extraction_id!r}: {exc}",
                                }
                            )
                        else:
                            if _sha256(extracted_text) != text_checksum:
                                findings.append(
                                    {
                                        "severity": "error",
                                        "code": "EXTRACTION_CHECKSUM_MISMATCH",
                                        "message": (
                                            f"Evidence extraction "
                                            f"{extraction_id!r} failed "
                                            "checksum validation."
                                        ),
                                    }
                                )
                elif text_checksum:
                    findings.append(
                        {
                            "severity": "error",
                            "code": "EXTRACTION_STORAGE_REFERENCE_MISSING",
                            "message": (
                                f"Evidence extraction {extraction_id!r} has "
                                "a checksum without encrypted content."
                            ),
                        }
                    )
                candidates = extraction.get("evidence_candidates", [])
                if not isinstance(candidates, list):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "EVIDENCE_CANDIDATE_COLLECTION_INVALID",
                            "message": (
                                f"Evidence extraction {extraction_id!r} has "
                                "an invalid candidate collection."
                            ),
                        }
                    )
                    continue
                for candidate in candidates:
                    evidence_candidate_count += 1
                    evidence_id = str(
                        candidate.get("evidence_id", "")
                    ) if isinstance(candidate, dict) else ""
                    evidence_match = EVIDENCE_ID_PATTERN.fullmatch(evidence_id)
                    if (
                        not isinstance(candidate, dict)
                        or evidence_match is None
                        or evidence_match.group(1)
                        != session.get("participant_id")
                        or evidence_id in seen_evidence
                        or candidate.get("source_id")
                        != source_artifact_id
                        or candidate.get("participant_id")
                        != session.get("participant_id")
                        or candidate.get("review_status")
                        not in {
                            "unreviewed",
                            "reviewed",
                            "disputed",
                            "superseded",
                        }
                        or candidate.get(
                            "capability_assertions_created"
                        )
                        != "none"
                    ):
                        findings.append(
                            {
                                "severity": "error",
                                "code": "EVIDENCE_CANDIDATE_INVALID",
                                "message": (
                                    f"Evidence candidate {evidence_id!r} "
                                    "failed its provenance or boundary checks."
                                ),
                            }
                        )
                    seen_evidence.add(evidence_id)

            seen_review_events: set[str] = set()
            review_targets: dict[str, str] = {}
            review_records = session.get("evidence_review_events", [])
            if not isinstance(review_records, list):
                findings.append(
                    {
                        "severity": "error",
                        "code": "EVIDENCE_REVIEW_COLLECTION_INVALID",
                        "message": (
                            f"Session {directory.name!r} has an invalid "
                            "evidence-review collection."
                        ),
                    }
                )
                review_records = []
            for event in review_records:
                evidence_review_count += 1
                review_id = str(
                    event.get("review_event_id", "")
                ) if isinstance(event, dict) else ""
                review_match = EVIDENCE_REVIEW_ID_PATTERN.fullmatch(review_id)
                supersedes_review_id = str(
                    event.get("supersedes_review_event_id", "")
                ) if isinstance(event, dict) else ""
                target_evidence_id = str(
                    event.get("target_record_id", "")
                ) if isinstance(event, dict) else ""
                if (
                    not isinstance(event, dict)
                    or review_match is None
                    or review_match.group(1)
                    != session.get("participant_id")
                    or review_id in seen_review_events
                    or event.get("target_record_type")
                    != "evidence_candidate"
                    or target_evidence_id not in seen_evidence
                    or event.get("disposition")
                    not in {
                        "accepted",
                        "corrected",
                        "rejected",
                        "disputed",
                    }
                    or (
                        supersedes_review_id
                        and (
                            supersedes_review_id
                            not in seen_review_events
                            or review_targets.get(supersedes_review_id)
                            != target_evidence_id
                        )
                    )
                ):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "EVIDENCE_REVIEW_EVENT_INVALID",
                            "message": (
                                f"Evidence review event {review_id!r} "
                                "failed validation."
                            ),
                        }
                    )
                seen_review_events.add(review_id)
                review_targets[review_id] = target_evidence_id

            seen_credential_entries: set[str] = set()
            credential_records = session.get("credential_resolutions", [])
            if not isinstance(credential_records, list):
                findings.append(
                    {
                        "severity": "error",
                        "code": "CREDENTIAL_RESOLUTION_COLLECTION_INVALID",
                        "message": (
                            f"Session {directory.name!r} has an invalid "
                            "credential-resolution collection."
                        ),
                    }
                )
                credential_records = []
            for record in credential_records:
                credential_resolution_count += 1
                if not isinstance(record, dict):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "CREDENTIAL_RESOLUTION_INVALID",
                            "message": (
                                f"Session {directory.name!r} contains an "
                                "invalid credential-resolution record."
                            ),
                        }
                    )
                    continue
                entry_id = str(record.get("credential_entry_id", ""))
                match = CREDENTIAL_ENTRY_ID_PATTERN.fullmatch(entry_id)
                local_lookup = record.get("local_lookup", {})
                external_lookup = record.get("external_lookup", {})
                if (
                    match is None
                    or match.group(1) != session.get("participant_id")
                    or entry_id in seen_credential_entries
                    or not isinstance(local_lookup, dict)
                    or local_lookup.get("participant_claims_established")
                    != []
                    or not LOOKUP_FINGERPRINT_PATTERN.fullmatch(
                        str(local_lookup.get("request_fingerprint", ""))
                    )
                    or not isinstance(external_lookup, dict)
                    or external_lookup.get(
                        "participant_claims_established", []
                    )
                    != []
                    or external_lookup.get(
                        "definition_accepted", False
                    )
                    is not False
                ):
                    findings.append(
                        {
                            "severity": "error",
                            "code": "CREDENTIAL_RESOLUTION_INVALID",
                            "message": (
                                f"Credential resolution {entry_id!r} failed "
                                "the protected linkage boundary."
                            ),
                        }
                    )
                seen_credential_entries.add(entry_id)

        for tombstone_path in sorted(self.tombstones_path.glob("*.json")):
            tombstone_count += 1
            try:
                tombstone = read_json(tombstone_path)
            except LocalIntakeError as exc:
                findings.append(
                    {
                        "severity": "error",
                        "code": "DELETION_TOMBSTONE_INVALID",
                        "message": str(exc),
                    }
                )
                continue
            session_id = str(tombstone.get("intake_session_id", ""))
            session_match = SESSION_ID_PATTERN.fullmatch(session_id)
            if (
                session_match is None
                or tombstone_path.stem != session_id
                or tombstone.get("participant_id") != session_match.group(1)
                or tombstone.get("participant_content_retained") is not False
                or not verify_integrity_tag(
                    tombstone,
                    self.encryption.master_key,
                    context=f"pia-phase2b-tombstone:{session_id}",
                )
            ):
                findings.append(
                    {
                        "severity": "error",
                        "code": "DELETION_TOMBSTONE_INVALID",
                        "message": f"Deletion tombstone {tombstone_path.name!r} failed validation.",
                    }
                )
            elif self._session_dir(session_id).exists():
                findings.append(
                    {
                        "severity": "error",
                        "code": "DELETED_SESSION_IDENTIFIER_REUSED",
                        "message": (
                            f"Deleted session identifier {session_id!r} "
                            "has been reused by an active session."
                        ),
                    }
                )

        errors = sum(1 for finding in findings if finding["severity"] == "error")
        return {
            "accepted": errors == 0,
            "counts": {
                "sessions": session_count,
                "artifacts": artifact_count,
                "evidence_extractions": evidence_extraction_count,
                "evidence_candidates": evidence_candidate_count,
                "evidence_reviews": evidence_review_count,
                "credential_resolutions": credential_resolution_count,
                "audit_events": audit_count,
                "deletion_tombstones": tombstone_count,
                "errors": errors,
            },
            "findings": findings,
        }
