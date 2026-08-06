#!/usr/bin/env python3
"""Create an independent, participant-data-free OSI-PIA release repository.

artifact_id: software-clean-release-builder-001
domain: implementation
layer: software
authority: canonical
status: active
version: 1.0.0
owner: repository-governance
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


RELEASE_AUTHOR_NAME = "OSI-PIA Release Process"
RELEASE_AUTHOR_EMAIL = "release@local.invalid"


class ReleaseError(RuntimeError):
    """A clean-release precondition or verification failed."""


def run(
    command: list[str],
    *,
    cwd: Path,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=capture,
        text=True,
    )
    if result.returncode != 0:
        rendered = " ".join(command)
        details = (result.stdout + result.stderr).strip()
        raise ReleaseError(f"{rendered} failed: {details}")
    return result


def git(source: Path, *arguments: str) -> str:
    return run(["git", *arguments], cwd=source).stdout.strip()


def verify_source(source: Path, source_ref: str) -> tuple[str, str]:
    if not (source / ".git").exists():
        raise ReleaseError(f"source is not a Git repository: {source}")

    baseline_commit = git(source, "rev-parse", "HEAD")
    tree_id = git(source, "rev-parse", f"{source_ref}^{{tree}}")
    validator = source / "software" / "governance" / "validate_repository_governance.py"
    if not validator.is_file():
        raise ReleaseError(f"governance validator is missing: {validator}")

    run(
        [sys.executable, str(validator), "--root", str(source)],
        cwd=source,
    )
    return baseline_commit, tree_id


def safe_extract(archive_path: Path, destination: Path) -> None:
    destination_root = destination.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if target != destination_root and destination_root not in target.parents:
                raise ReleaseError(
                    f"archive member escapes destination: {member.filename}"
                )
        archive.extractall(destination)


def export_tree(source: Path, source_ref: str, destination: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="osi-pia-clean-release-") as temp:
        archive_path = Path(temp) / "release.zip"
        run(
            [
                "git",
                "archive",
                "--format=zip",
                f"--output={archive_path}",
                source_ref,
            ],
            cwd=source,
        )
        safe_extract(archive_path, destination)


def write_provenance(
    destination: Path,
    *,
    baseline_commit: str,
    tree_id: str,
) -> None:
    created = dt.date.today().isoformat()
    content = f"""# Clean Release Provenance

## Release identity

- Created: `{created}`
- Source baseline commit: `{baseline_commit}`
- Sanitized source tree: `{tree_id}`
- Release method: independent root history
- Restricted source history imported: no
- Git remote configured: no

## Boundary

This repository was generated from a validated sanitized tree. The restricted
development repository remains a separate archive and may contain historical
participant material. Its commits and Git objects are not ancestors or object
sources for this release.

Participant datasets, participant-derived reports and graph snapshots,
participant-specific imports, credentials, live databases, and private
connector output are excluded. Tests and examples use synthetic identities.

## Verification

The release builder verifies governance invariants, a single root commit, no
commit parent, no remote, and no Git object alternates. Full compilation and
test results are recorded by the release handoff that created this repository.
"""
    (destination / "CLEAN_RELEASE_PROVENANCE.md").write_text(
        content,
        encoding="utf-8",
        newline="\n",
    )


def initialize_release(destination: Path) -> str:
    run(["git", "init", "--initial-branch=main"], cwd=destination)
    run(["git", "add", "--all"], cwd=destination)
    run(
        [
            "git",
            "-c",
            f"user.name={RELEASE_AUTHOR_NAME}",
            "-c",
            f"user.email={RELEASE_AUTHOR_EMAIL}",
            "commit",
            "-m",
            "chore(release): establish sanitized OSI-PIA lineage",
        ],
        cwd=destination,
    )
    return git(destination, "rev-parse", "HEAD")


def verify_release(destination: Path) -> None:
    validator = (
        destination
        / "software"
        / "governance"
        / "validate_repository_governance.py"
    )
    run(
        [sys.executable, str(validator), "--root", str(destination)],
        cwd=destination,
    )

    if git(destination, "rev-list", "--count", "--all") != "1":
        raise ReleaseError("release repository must contain exactly one commit")
    if git(destination, "rev-list", "--parents", "-n", "1", "HEAD").count(" ") != 0:
        raise ReleaseError("release HEAD must be a root commit with no parent")
    if git(destination, "remote"):
        raise ReleaseError("release repository must not have a configured remote")
    if (destination / ".git" / "objects" / "info" / "alternates").exists():
        raise ReleaseError("release repository must not use Git object alternates")
    if git(destination, "status", "--porcelain"):
        raise ReleaseError("release repository worktree is not clean")


def create_release(source: Path, source_ref: str, destination: Path) -> str:
    source = source.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise ReleaseError(f"destination already exists: {destination}")
    if destination == source or source in destination.parents:
        raise ReleaseError("destination must be outside the source repository")

    baseline_commit, tree_id = verify_source(source, source_ref)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()
    try:
        export_tree(source, source_ref, destination)
        write_provenance(
            destination,
            baseline_commit=baseline_commit,
            tree_id=tree_id,
        )
        release_commit = initialize_release(destination)
        verify_release(destination)
        return release_commit
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an independent sanitized OSI-PIA release repository."
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()

    try:
        commit = create_release(args.source, args.source_ref, args.destination)
    except ReleaseError as error:
        print(f"Clean release failed: {error}", file=sys.stderr)
        return 1

    print(f"Clean release created at {args.destination.resolve()}")
    print(f"Root commit: {commit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
