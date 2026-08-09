#!/usr/bin/env python3
"""Security controls for the Windows-local PIA Phase 2B intake.

The module uses Windows DPAPI to bind the store master key to the current
Windows user, AES-256-GCM for authenticated encryption, scrypt password
verification for the local owner account, and Windows AMSI for in-memory
malware inspection.

artifact_id: component-pia-intake-phase2b-security-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import base64
import ctypes
import hashlib
import hmac
import json
import os
import platform
import re
import secrets
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:  # pragma: no cover - exercised by deployment preflight
    raise RuntimeError(
        "PIA Phase 2B requires the cryptography package for AES-256-GCM."
    ) from exc

from software.intake.local_private_intake import (
    IntakePreflightError,
    LocalIntakeError,
    REPOSITORY_ROOT,
)


ENCRYPTED_BLOB_MAGIC = b"PIA2B1\x00"
DPAPI_UI_FORBIDDEN = 0x1
SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1
SCRYPT_MAXMEM = 64 * 1024 * 1024
MIN_PASSPHRASE_CHARACTERS = 14
AMSI_RESULT_CLEAN = 0
AMSI_RESULT_NOT_DETECTED = 1
AMSI_RESULT_BLOCKED_BY_ADMIN_START = 16384
AMSI_RESULT_BLOCKED_BY_ADMIN_END = 20479
AMSI_RESULT_DETECTED = 32768


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    try:
        temporary.write_bytes(content)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    atomic_bytes(
        path,
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LocalIntakeError(f"Could not read protected intake control: {path}") from exc
    if not isinstance(value, dict):
        raise LocalIntakeError(f"Protected intake control is not an object: {path}")
    return value


def canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def add_integrity_tag(
    value: dict[str, Any],
    key: bytes,
    *,
    context: str,
) -> dict[str, Any]:
    tagged = dict(value)
    tagged.pop("integrity_tag", None)
    tagged["integrity_tag"] = hmac.new(
        key,
        context.encode("utf-8") + b"\x00" + canonical_json(tagged),
        hashlib.sha256,
    ).hexdigest()
    return tagged


def verify_integrity_tag(
    value: dict[str, Any],
    key: bytes,
    *,
    context: str,
) -> bool:
    claimed = str(value.get("integrity_tag", ""))
    unsigned = dict(value)
    unsigned.pop("integrity_tag", None)
    expected = hmac.new(
        key,
        context.encode("utf-8") + b"\x00" + canonical_json(unsigned),
        hashlib.sha256,
    ).hexdigest()
    return bool(claimed) and hmac.compare_digest(claimed, expected)


def b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def unb64(value: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(value.encode("ascii"))
    except (ValueError, UnicodeError) as exc:
        raise LocalIntakeError("A protected value is not valid base64.") from exc


def derive_scrypt_key(passphrase: str, salt: bytes) -> bytes:
    if len(passphrase) < MIN_PASSPHRASE_CHARACTERS:
        raise IntakePreflightError(
            "The passphrase must contain at least "
            f"{MIN_PASSPHRASE_CHARACTERS} characters."
        )
    return hashlib.scrypt(
        passphrase.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        maxmem=SCRYPT_MAXMEM,
        dklen=32,
    )


if platform.system() == "Windows":
    from ctypes import wintypes

    class _DataBlob(ctypes.Structure):
        _fields_ = [
            ("cbData", wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
        ]


def _require_windows() -> None:
    if platform.system() != "Windows":
        raise IntakePreflightError(
            "Phase 2B currently requires Windows DPAPI and Windows AMSI."
        )


def dpapi_protect(content: bytes) -> bytes:
    """Protect bytes for the current Windows user without UI prompts."""

    _require_windows()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    input_buffer = (ctypes.c_ubyte * len(content)).from_buffer_copy(content)
    input_blob = _DataBlob(
        len(content),
        ctypes.cast(input_buffer, ctypes.POINTER(ctypes.c_ubyte)),
    )
    output_blob = _DataBlob()
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(_DataBlob),
        wintypes.LPCWSTR,
        ctypes.POINTER(_DataBlob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(_DataBlob),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    if not crypt32.CryptProtectData(
        ctypes.byref(input_blob),
        "PIA Phase 2B store master key",
        None,
        None,
        None,
        DPAPI_UI_FORBIDDEN,
        ctypes.byref(output_blob),
    ):
        raise LocalIntakeError(
            f"Windows DPAPI protection failed with error {ctypes.get_last_error()}."
        )
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree(output_blob.pbData)


def dpapi_unprotect(content: bytes) -> bytes:
    """Unprotect bytes for the current Windows user and verify DPAPI integrity."""

    _require_windows()
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    input_buffer = (ctypes.c_ubyte * len(content)).from_buffer_copy(content)
    input_blob = _DataBlob(
        len(content),
        ctypes.cast(input_buffer, ctypes.POINTER(ctypes.c_ubyte)),
    )
    output_blob = _DataBlob()
    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(_DataBlob),
        ctypes.c_void_p,
        ctypes.POINTER(_DataBlob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(_DataBlob),
    ]
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    if not crypt32.CryptUnprotectData(
        ctypes.byref(input_blob),
        None,
        None,
        None,
        None,
        DPAPI_UI_FORBIDDEN,
        ctypes.byref(output_blob),
    ):
        raise LocalIntakeError(
            f"Windows DPAPI unprotection failed with error {ctypes.get_last_error()}."
        )
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree(output_blob.pbData)


def encrypt_bytes(key: bytes, content: bytes, *, aad: str) -> bytes:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(key).encrypt(nonce, content, aad.encode("utf-8"))
    return ENCRYPTED_BLOB_MAGIC + nonce + ciphertext


def decrypt_bytes(key: bytes, protected: bytes, *, aad: str) -> bytes:
    if not protected.startswith(ENCRYPTED_BLOB_MAGIC):
        raise LocalIntakeError("Protected content has an invalid format marker.")
    nonce_start = len(ENCRYPTED_BLOB_MAGIC)
    nonce = protected[nonce_start : nonce_start + 12]
    ciphertext = protected[nonce_start + 12 :]
    if len(nonce) != 12 or not ciphertext:
        raise LocalIntakeError("Protected content is incomplete.")
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, aad.encode("utf-8"))
    except InvalidTag as exc:
        raise LocalIntakeError(
            "Protected content failed authenticated-integrity validation."
        ) from exc


class EncryptionManager:
    """Manage a DPAPI-protected master key and encrypted recovery bundle."""

    def __init__(self, store_root: Path, master_key: bytes) -> None:
        if len(master_key) != 32:
            raise LocalIntakeError("The Phase 2B master key has an invalid length.")
        self.store_root = store_root
        self.master_key = master_key

    @property
    def protected_key_path(self) -> Path:
        return self.store_root / "keys" / "master-key.dpapi"

    @classmethod
    def create(
        cls,
        store_root: Path,
        *,
        recovery_path: Path,
        recovery_passphrase: str,
        store_id: str,
    ) -> tuple["EncryptionManager", dict[str, Any]]:
        if recovery_path.exists():
            raise IntakePreflightError("The recovery-bundle path already exists.")
        if not recovery_path.is_absolute():
            raise IntakePreflightError("The recovery-bundle path must be absolute.")
        resolved_recovery = recovery_path.resolve()
        if is_within(resolved_recovery, store_root) or is_within(
            resolved_recovery, REPOSITORY_ROOT
        ):
            raise IntakePreflightError(
                "The recovery bundle must be outside both the intake store and Git."
            )
        master_key = secrets.token_bytes(32)
        manager = cls(store_root, master_key)
        atomic_bytes(manager.protected_key_path, dpapi_protect(master_key))
        bundle = manager._build_recovery_bundle(
            recovery_passphrase,
            store_id=store_id,
        )
        atomic_json(resolved_recovery, bundle)
        recovered = manager.recover_key(
            resolved_recovery,
            recovery_passphrase,
            expected_store_id=store_id,
        )
        if not hmac.compare_digest(recovered, master_key):
            raise LocalIntakeError("The newly created recovery bundle failed verification.")
        summary = {
            "recovery_bundle_checksum": hashlib.sha256(
                resolved_recovery.read_bytes()
            ).hexdigest(),
            "recovery_verified_at": utc_now(),
        }
        return manager, summary

    @classmethod
    def open(cls, store_root: Path) -> "EncryptionManager":
        path = store_root / "keys" / "master-key.dpapi"
        if not path.is_file():
            raise IntakePreflightError("The DPAPI-protected store key is missing.")
        return cls(store_root, dpapi_unprotect(path.read_bytes()))

    def _build_recovery_bundle(
        self,
        passphrase: str,
        *,
        store_id: str,
    ) -> dict[str, Any]:
        salt = secrets.token_bytes(16)
        key = derive_scrypt_key(passphrase, salt)
        aad = f"pia-phase2b-recovery:{store_id}"
        return {
            "format": "pia-phase2b-recovery-v1",
            "store_id": store_id,
            "created_at": utc_now(),
            "kdf": {
                "name": "scrypt",
                "n": SCRYPT_N,
                "r": SCRYPT_R,
                "p": SCRYPT_P,
                "salt": b64(salt),
            },
            "protected_master_key": b64(
                encrypt_bytes(key, self.master_key, aad=aad)
            ),
        }

    @staticmethod
    def recover_key(
        recovery_path: Path,
        passphrase: str,
        *,
        expected_store_id: str,
    ) -> bytes:
        bundle = read_json(recovery_path)
        if (
            bundle.get("format") != "pia-phase2b-recovery-v1"
            or bundle.get("store_id") != expected_store_id
        ):
            raise IntakePreflightError("The recovery bundle does not match this store.")
        kdf = bundle.get("kdf", {})
        if not isinstance(kdf, dict) or (
            kdf.get("name"),
            kdf.get("n"),
            kdf.get("r"),
            kdf.get("p"),
        ) != ("scrypt", SCRYPT_N, SCRYPT_R, SCRYPT_P):
            raise IntakePreflightError("The recovery bundle uses unsupported KDF settings.")
        key = derive_scrypt_key(passphrase, unb64(str(kdf.get("salt", ""))))
        return decrypt_bytes(
            key,
            unb64(str(bundle.get("protected_master_key", ""))),
            aad=f"pia-phase2b-recovery:{expected_store_id}",
        )

    def wrap_session_key(self, session_id: str, session_key: bytes) -> bytes:
        return encrypt_bytes(
            self.master_key,
            session_key,
            aad=f"session-key:{session_id}",
        )

    def unwrap_session_key(self, session_id: str, protected_key: bytes) -> bytes:
        session_key = decrypt_bytes(
            self.master_key,
            protected_key,
            aad=f"session-key:{session_id}",
        )
        if len(session_key) != 32:
            raise LocalIntakeError("The protected session key has an invalid length.")
        return session_key


class OwnerAuthenticator:
    """Store and verify local owner/reviewer passwords without retaining them."""

    def __init__(self, path: Path, integrity_key: bytes) -> None:
        self.path = path
        self.integrity_key = integrity_key

    def _read_record(self) -> dict[str, Any]:
        record = read_json(self.path)
        if not verify_integrity_tag(
            record,
            self.integrity_key,
            context="pia-phase2b-local-accounts",
        ):
            raise LocalIntakeError(
                "The local account registry failed integrity validation."
            )
        return record

    def _write_record(self, record: dict[str, Any]) -> None:
        atomic_json(
            self.path,
            add_integrity_tag(
                record,
                self.integrity_key,
                context="pia-phase2b-local-accounts",
            ),
        )

    def initialize(self, passphrase: str) -> dict[str, Any]:
        if self.path.exists():
            raise IntakePreflightError("The local owner account already exists.")
        owner = self._new_account("local-owner", "owner", passphrase)
        record = {
            "format": "pia-local-accounts-v1",
            "created_at": utc_now(),
            "accounts": [owner],
        }
        self._write_record(record)
        return {
            "subject": owner["subject"],
            "role": owner["role"],
            "created_at": owner["created_at"],
        }

    @staticmethod
    def _new_account(subject: str, role: str, passphrase: str) -> dict[str, Any]:
        if not re.fullmatch(r"[a-z][a-z0-9-]{2,39}", subject):
            raise IntakePreflightError(
                "Account IDs must be lowercase letters, numbers, or hyphens."
            )
        if role not in {"owner", "reviewer", "participant"}:
            raise IntakePreflightError("The account role is unsupported.")
        salt = secrets.token_bytes(16)
        verifier = derive_scrypt_key(passphrase, salt)
        return {
            "subject": subject,
            "role": role,
            "created_at": utc_now(),
            "kdf": {
                "name": "scrypt",
                "n": SCRYPT_N,
                "r": SCRYPT_R,
                "p": SCRYPT_P,
                "salt": b64(salt),
            },
            "verifier": b64(verifier),
        }

    def _account(self, subject: str) -> dict[str, Any] | None:
        record = self._read_record()
        if record.get("format") != "pia-local-accounts-v1":
            raise IntakePreflightError("The local account registry is unsupported.")
        accounts = record.get("accounts", [])
        if not isinstance(accounts, list):
            raise IntakePreflightError("The local account registry is invalid.")
        return next(
            (
                account
                for account in accounts
                if isinstance(account, dict) and account.get("subject") == subject
            ),
            None,
        )

    def verify(self, passphrase: str, *, subject: str = "local-owner") -> bool:
        account = self._account(subject)
        if account is None:
            return False
        kdf = account.get("kdf", {})
        if not isinstance(kdf, dict) or (
            kdf.get("name"),
            kdf.get("n"),
            kdf.get("r"),
            kdf.get("p"),
        ) != ("scrypt", SCRYPT_N, SCRYPT_R, SCRYPT_P):
            raise IntakePreflightError("The owner account uses unsupported KDF settings.")
        try:
            candidate = derive_scrypt_key(
                passphrase,
                unb64(str(kdf.get("salt", ""))),
            )
        except IntakePreflightError:
            return False
        return hmac.compare_digest(
            candidate,
            unb64(str(account.get("verifier", ""))),
        )

    def identity(self, subject: str = "local-owner") -> dict[str, str]:
        account = self._account(subject)
        if account is None:
            raise IntakePreflightError("The local account does not exist.")
        return {
            "subject": str(account.get("subject", "")),
            "role": str(account.get("role", "")),
        }

    def authenticate(self, subject: str, passphrase: str) -> dict[str, str] | None:
        if not self.verify(passphrase, subject=subject):
            return None
        return self.identity(subject)

    def add_reviewer(self, subject: str, passphrase: str) -> dict[str, str]:
        record = self._read_record()
        if record.get("format") != "pia-local-accounts-v1":
            raise IntakePreflightError("The local account registry is unsupported.")
        accounts = record.get("accounts", [])
        if not isinstance(accounts, list):
            raise IntakePreflightError("The local account registry is invalid.")
        if any(
            isinstance(account, dict) and account.get("subject") == subject
            for account in accounts
        ):
            raise IntakePreflightError("The local account ID already exists.")
        account = self._new_account(subject, "reviewer", passphrase)
        accounts.append(account)
        self._write_record(record)
        return {
            "subject": str(account["subject"]),
            "role": str(account["role"]),
        }

    def add_participant(self, subject: str, passphrase: str) -> dict[str, str]:
        """Add a synthetic/local participant account through owner administration."""
        record = self._read_record()
        accounts = record.get("accounts", [])
        if not isinstance(accounts, list):
            raise IntakePreflightError("The local account registry is invalid.")
        if any(isinstance(account, dict) and account.get("subject") == subject for account in accounts):
            raise IntakePreflightError("The local account ID already exists.")
        account = self._new_account(subject, "participant", passphrase)
        accounts.append(account)
        self._write_record(record)
        return {"subject": str(account["subject"]), "role": str(account["role"])}


@dataclass(frozen=True)
class MalwareScanResult:
    status: str
    provider: str
    result_code: int
    scanned_at: str

    @property
    def accepted(self) -> bool:
        return self.status == "clean"


class WindowsAMSIScanner:
    """Scan document bytes in memory through the registered Windows provider."""

    provider_name = "windows-amsi"

    def scan(self, content: bytes, *, content_name: str) -> MalwareScanResult:
        _require_windows()
        if not content:
            raise IntakePreflightError("Empty content cannot be malware-scanned.")
        amsi = ctypes.WinDLL("amsi", use_last_error=True)
        context = ctypes.c_void_p()
        amsi.AmsiInitialize.argtypes = [
            ctypes.c_wchar_p,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        amsi.AmsiInitialize.restype = ctypes.c_long
        amsi.AmsiScanBuffer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_ulong,
            ctypes.c_wchar_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        amsi.AmsiScanBuffer.restype = ctypes.c_long
        amsi.AmsiUninitialize.argtypes = [ctypes.c_void_p]
        amsi.AmsiUninitialize.restype = None
        hr = amsi.AmsiInitialize("PIA Phase 2B Intake", ctypes.byref(context))
        if hr != 0:
            raise LocalIntakeError(
                f"Windows AMSI initialization failed with HRESULT 0x{hr & 0xFFFFFFFF:08X}."
            )
        try:
            buffer = (ctypes.c_ubyte * len(content)).from_buffer_copy(content)
            result = ctypes.c_int()
            hr = amsi.AmsiScanBuffer(
                context,
                ctypes.cast(buffer, ctypes.c_void_p),
                len(content),
                content_name,
                None,
                ctypes.byref(result),
            )
            if hr != 0:
                raise LocalIntakeError(
                    f"Windows AMSI scan failed with HRESULT 0x{hr & 0xFFFFFFFF:08X}."
                )
            code = int(result.value)
            if code in {AMSI_RESULT_CLEAN, AMSI_RESULT_NOT_DETECTED}:
                status = "clean"
            elif (
                AMSI_RESULT_BLOCKED_BY_ADMIN_START
                <= code
                <= AMSI_RESULT_BLOCKED_BY_ADMIN_END
            ):
                status = "blocked_by_policy"
            elif code >= AMSI_RESULT_DETECTED:
                status = "malware_detected"
            else:
                status = "risk_requires_review"
            return MalwareScanResult(
                status=status,
                provider=self.provider_name,
                result_code=code,
                scanned_at=utc_now(),
            )
        finally:
            amsi.AmsiUninitialize(context)

    def preflight(self) -> MalwareScanResult:
        return self.scan(
            b"PIA Phase 2B antimalware capability preflight.",
            content_name="pia-phase2b-preflight.txt",
        )


def harden_windows_directory(root: Path) -> dict[str, str]:
    """Restrict a newly created store to the current Windows user and SYSTEM."""

    _require_windows()
    if any(root.iterdir()):
        raise IntakePreflightError(
            "ACL hardening only runs on a new, empty participant store."
        )
    identity = subprocess.run(
        ["whoami"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    ).stdout.strip()
    if not identity:
        raise LocalIntakeError("Could not determine the current Windows identity.")
    command = [
        "icacls",
        str(root),
        "/inheritance:r",
        "/grant:r",
        f"{identity}:(OI)(CI)F",
        "/grant:r",
        "*S-1-5-18:(OI)(CI)F",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise LocalIntakeError(
            "Windows ACL hardening failed; participant mode remains blocked."
        )
    return {"acl_state": "restricted_current_user_and_system", "identity": identity}


@dataclass
class AuthSession:
    token_hash: str
    csrf_token: str
    subject: str
    role: str
    client_address: str
    user_agent_hash: str
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime


class AuthSessionManager:
    """In-memory, restart-invalidated owner sessions for the local web UI."""

    def __init__(
        self,
        *,
        idle_minutes: int = 20,
        maximum_hours: int = 8,
    ) -> None:
        self.idle_timeout = timedelta(minutes=idle_minutes)
        self.maximum_lifetime = timedelta(hours=maximum_hours)
        self.sessions: dict[str, AuthSession] = {}

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("ascii")).hexdigest()

    @staticmethod
    def _user_agent_hash(user_agent: str) -> str:
        return hashlib.sha256(user_agent.encode("utf-8")).hexdigest()

    def create(
        self,
        *,
        subject: str,
        role: str,
        client_address: str,
        user_agent: str,
    ) -> tuple[str, AuthSession]:
        now = datetime.now(UTC)
        token = secrets.token_urlsafe(32)
        token_hash = self._token_hash(token)
        session = AuthSession(
            token_hash=token_hash,
            csrf_token=secrets.token_urlsafe(32),
            subject=subject,
            role=role,
            client_address=client_address,
            user_agent_hash=self._user_agent_hash(user_agent),
            created_at=now,
            last_seen_at=now,
            expires_at=now + self.maximum_lifetime,
        )
        self.sessions[token_hash] = session
        return token, session

    def verify(
        self,
        token: str,
        *,
        client_address: str,
        user_agent: str,
    ) -> AuthSession | None:
        if not token:
            return None
        token_hash = self._token_hash(token)
        session = self.sessions.get(token_hash)
        if session is None:
            return None
        now = datetime.now(UTC)
        if (
            now > session.expires_at
            or now - session.last_seen_at > self.idle_timeout
            or session.client_address != client_address
            or session.user_agent_hash != self._user_agent_hash(user_agent)
        ):
            self.sessions.pop(token_hash, None)
            return None
        session.last_seen_at = now
        return session

    def revoke(self, token: str) -> None:
        if token:
            self.sessions.pop(self._token_hash(token), None)


class LoginThrottle:
    """Bound repeated local login attempts without persisting entered secrets."""

    def __init__(self, *, limit: int = 5, window_minutes: int = 5) -> None:
        self.limit = limit
        self.window = timedelta(minutes=window_minutes)
        self.attempts: dict[str, list[datetime]] = {}

    def allowed(self, client_address: str) -> bool:
        now = datetime.now(UTC)
        recent = [
            attempt
            for attempt in self.attempts.get(client_address, [])
            if now - attempt <= self.window
        ]
        self.attempts[client_address] = recent
        return len(recent) < self.limit

    def record_failure(self, client_address: str) -> None:
        self.attempts.setdefault(client_address, []).append(datetime.now(UTC))

    def clear(self, client_address: str) -> None:
        self.attempts.pop(client_address, None)
