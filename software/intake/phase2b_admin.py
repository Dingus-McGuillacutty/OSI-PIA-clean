#!/usr/bin/env python3
"""Interactive administration for the PIA Phase 2B protected intake store.

Passphrases are collected locally with getpass and are never accepted as
command-line arguments.

artifact_id: component-pia-intake-phase2b-admin-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import argparse
import getpass
import json
from pathlib import Path

from software.intake.local_private_intake import LocalIntakeError
from software.intake.phase2b_security import MIN_PASSPHRASE_CHARACTERS
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)


def _new_passphrase(label: str) -> str:
    first = getpass.getpass(f"{label} passphrase: ")
    second = getpass.getpass(f"Confirm {label.lower()} passphrase: ")
    return _validate_new_passphrase(label, first, second)


def _validate_new_passphrase(
    label: str,
    first: str,
    second: str,
) -> str:
    if first != second:
        raise LocalIntakeError(
            f"The two {label.lower()} passphrase entries do not match."
        )
    if len(first) < MIN_PASSPHRASE_CHARACTERS:
        raise LocalIntakeError(
            f"The {label.lower()} passphrase was received as "
            f"{len(first)} character(s); at least "
            f"{MIN_PASSPHRASE_CHARACTERS} are required."
        )
    return first


def _new_passphrase_window(label: str) -> str:
    """Collect a new passphrase in local masked windows."""

    try:
        import tkinter as tk
        from tkinter import simpledialog
    except ImportError as exc:
        raise LocalIntakeError(
            "The windowed passphrase prompt is unavailable in this Python "
            "installation."
        ) from exc
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        first = simpledialog.askstring(
            "PIA protected intake",
            (
                f"Enter the {label.lower()} passphrase.\n\n"
                f"Use at least {MIN_PASSPHRASE_CHARACTERS} characters."
            ),
            show="*",
            parent=root,
        )
        if first is None:
            raise LocalIntakeError(
                f"The {label.lower()} passphrase entry was cancelled."
            )
        second = simpledialog.askstring(
            "PIA protected intake",
            f"Confirm the {label.lower()} passphrase.",
            show="*",
            parent=root,
        )
        if second is None:
            raise LocalIntakeError(
                f"The {label.lower()} passphrase confirmation was cancelled."
            )
        return _validate_new_passphrase(label, first, second)
    finally:
        root.destroy()


def _existing_passphrase_window(label: str) -> str:
    """Collect one existing passphrase in a local masked window."""

    try:
        import tkinter as tk
        from tkinter import simpledialog
    except ImportError as exc:
        raise LocalIntakeError(
            "The windowed passphrase prompt is unavailable in this Python "
            "installation."
        ) from exc
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        passphrase = simpledialog.askstring(
            "PIA protected intake",
            f"Enter the {label.lower()} passphrase.",
            show="*",
            parent=root,
        )
        if passphrase is None:
            raise LocalIntakeError(
                f"The {label.lower()} passphrase entry was cancelled."
            )
        return passphrase
    finally:
        root.destroy()


def _existing_owner(
    store: ProtectedParticipantIntakeStore,
    *,
    windowed: bool = False,
) -> None:
    passphrase = (
        _existing_passphrase_window("Local owner")
        if windowed
        else getpass.getpass("Local owner passphrase: ")
    )
    if not store.authenticator.verify(passphrase):
        raise LocalIntakeError("Local owner authentication failed.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Administer the Windows-local PIA Phase 2B participant store."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    initialize = subparsers.add_parser(
        "initialize",
        help="Create an encrypted participant store and offline recovery bundle.",
    )
    initialize.add_argument("--storage-root", required=True, type=Path)
    initialize.add_argument("--recovery-bundle", required=True, type=Path)
    initialize.add_argument(
        "--windowed-passphrases",
        action="store_true",
        help=(
            "Collect masked passphrases in local windows instead of the "
            "terminal."
        ),
    )

    reviewer = subparsers.add_parser(
        "add-reviewer",
        help="Add a password-authenticated reviewer account.",
    )
    reviewer.add_argument("--storage-root", required=True, type=Path)
    reviewer.add_argument("--account-id", required=True)
    reviewer.add_argument(
        "--windowed-passphrases",
        action="store_true",
        help="Collect masked owner and reviewer passphrases in local windows.",
    )

    participant = subparsers.add_parser(
        "add-participant",
        help="Add a synthetic/local participant account for controlled UI testing.",
    )
    participant.add_argument("--storage-root", required=True, type=Path)
    participant.add_argument("--account-id", required=True)
    participant.add_argument(
        "--windowed-passphrases",
        action="store_true",
        help="Collect masked owner and participant passphrases in local windows.",
    )

    validate = subparsers.add_parser(
        "validate",
        help="Validate encryption, audit integrity, retention, and stored content.",
    )
    validate.add_argument("--storage-root", required=True, type=Path)

    retention = subparsers.add_parser(
        "retention",
        help="Preview or execute expired-session deletion.",
    )
    retention.add_argument("--storage-root", required=True, type=Path)
    retention.add_argument(
        "--apply",
        action="store_true",
        help="Delete expired sessions; omission performs a dry run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "initialize":
            prompt = (
                _new_passphrase_window
                if args.windowed_passphrases
                else _new_passphrase
            )
            owner_passphrase = prompt("Local owner")
            recovery_passphrase = prompt("Offline recovery")
            store = ProtectedParticipantIntakeStore.create(
                args.storage_root,
                owner_passphrase=owner_passphrase,
                recovery_path=args.recovery_bundle,
                recovery_passphrase=recovery_passphrase,
            )
            print(
                json.dumps(
                    {
                        "status": "initialized",
                        "store_id": store.manifest["store_id"],
                        "storage_root": str(store.root),
                        "recovery_bundle": str(args.recovery_bundle.resolve()),
                        "participant_mode": "working_candidate",
                    },
                    indent=2,
                )
            )
            return 0

        store = ProtectedParticipantIntakeStore.open(args.storage_root)
        if args.command == "validate":
            result = store.validate()
            print(json.dumps(result, indent=2))
            return 0 if result["accepted"] else 1
        if args.command == "add-reviewer":
            _existing_owner(store, windowed=args.windowed_passphrases)
            reviewer_passphrase = (
                _new_passphrase_window("Reviewer")
                if args.windowed_passphrases
                else _new_passphrase("Reviewer")
            )
            identity = store.authenticator.add_reviewer(
                args.account_id,
                reviewer_passphrase,
            )
            store._append_audit(
                "reviewer_account_added",
                actor_subject="local-owner",
                actor_role="owner",
                details=identity,
            )
            print(json.dumps({"status": "created", **identity}, indent=2))
            return 0
        if args.command == "add-participant":
            _existing_owner(store, windowed=args.windowed_passphrases)
            participant_passphrase = (
                _new_passphrase_window("Participant")
                if args.windowed_passphrases
                else _new_passphrase("Participant")
            )
            identity = store.authenticator.add_participant(
                args.account_id,
                participant_passphrase,
            )
            store._append_audit(
                "participant_account_added",
                actor_subject="local-owner",
                actor_role="owner",
                details=identity,
            )
            print(json.dumps({"status": "created", **identity}, indent=2))
            return 0
        if args.command == "retention":
            _existing_owner(store)
            result = store.enforce_retention(
                actor_subject="local-owner",
                actor_role="owner",
                dry_run=not args.apply,
            )
            print(json.dumps(result, indent=2))
            return 0
    except (OSError, LocalIntakeError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
