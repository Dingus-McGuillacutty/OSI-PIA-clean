#!/usr/bin/env python3
"""Governed Phase 3A review service for participant-free credential definitions.

artifact_id: component-pia-credential-definition-review-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from software.intake.credential_definition_catalog import (
    ACTOR_ID_PATTERN,
    CURRENT_REVIEW_STATES,
    DEFAULT_CATALOG,
    DEFAULT_CONTRACT,
    CredentialDefinitionCatalog,
)


REVIEWABLE_DECISIONS = {
    "accepted",
    "accepted_with_limits",
    "revision_requested",
    "rejected",
    "disputed",
}
REVIEWER_ROLES = {
    "credential_definition_reviewer",
    "assurance_reviewer",
    "governance_reviewer",
}
MUTATED_FILES = (
    "credential_definition.csv",
    "credential_definition_source.csv",
    "credential_domain_element.csv",
    "credential_definition_review.csv",
    "credential_definition_expansion_queue.csv",
)


class CredentialReviewError(ValueError):
    """Raised when a review cannot safely proceed."""


@dataclass(frozen=True)
class CredentialReviewRequest:
    credential_definition_id: str
    reviewer_actor_id: str
    reviewer_role: str
    decision: str
    review_basis: str
    limitations: str = ""
    review_cycle: str = "annual"
    sources_reviewed: bool = False
    boundary_reviewed: bool = False

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "CredentialReviewRequest":
        return cls(
            credential_definition_id=str(
                value.get("credential_definition_id", "")
            ).strip(),
            reviewer_actor_id=str(value.get("reviewer_actor_id", "")).strip(),
            reviewer_role=str(value.get("reviewer_role", "")).strip(),
            decision=str(value.get("decision", "")).strip(),
            review_basis=str(value.get("review_basis", "")).strip(),
            limitations=str(value.get("limitations", "")).strip(),
            review_cycle=str(value.get("review_cycle", "annual")).strip(),
            sources_reviewed=value.get("sources_reviewed") is True,
            boundary_reviewed=value.get("boundary_reviewed") is True,
        )


class CredentialDefinitionReviewService:
    """Preview and apply accountable reviews to a participant-free catalog."""

    def __init__(
        self,
        catalog_root: Path | str = DEFAULT_CATALOG,
        contract_path: Path | str = DEFAULT_CONTRACT,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.catalog_root = Path(catalog_root).resolve()
        self.contract_path = Path(contract_path).resolve()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def status(self) -> dict[str, Any]:
        catalog = self._validated_catalog()
        queue = self.list_review_queue(catalog=catalog)
        return {
            "catalog_root": str(self.catalog_root),
            "contract_version": catalog.contract["contract"]["version"],
            "catalog_valid": True,
            "ready_for_review": len(queue),
            "participant_data_allowed": False,
            "boundary": (
                "This service reviews public credential meaning only. It does "
                "not receive participant records or establish completion, "
                "application, proficiency, performance, or identity."
            ),
        }

    def list_review_queue(
        self,
        *,
        catalog: CredentialDefinitionCatalog | None = None,
    ) -> list[dict[str, Any]]:
        catalog = catalog or self._validated_catalog()
        definition_ids: list[str] = []
        for item in catalog.rows["credential_definition_expansion_queue.csv"]:
            if item.get("processing_state") not in {
                "ready_for_review",
                "in_progress",
            }:
                continue
            definition_ids.extend(
                candidate
                for candidate in item.get(
                    "candidate_credential_definition_ids", ""
                ).split("|")
                if candidate
            )
        return [
            self.review_package(definition_id, catalog=catalog)
            for definition_id in dict.fromkeys(definition_ids)
        ]

    def review_package(
        self,
        credential_definition_id: str,
        *,
        catalog: CredentialDefinitionCatalog | None = None,
    ) -> dict[str, Any]:
        catalog = catalog or self._validated_catalog()
        definition = self._find(
            catalog.rows["credential_definition.csv"],
            "credential_definition_id",
            credential_definition_id,
        )
        if definition is None:
            raise CredentialReviewError("Credential definition was not found.")
        sources = [
            dict(row)
            for row in catalog.rows["credential_definition_source.csv"]
            if row.get("credential_definition_id") == credential_definition_id
        ]
        domains = [
            dict(row)
            for row in catalog.rows["credential_domain_element.csv"]
            if row.get("credential_definition_id") == credential_definition_id
        ]
        family = self._find(
            catalog.rows["credential_family.csv"],
            "credential_family_id",
            definition.get("credential_family_id", ""),
        )
        issuer = self._find(
            catalog.rows["credential_issuer.csv"],
            "credential_issuer_id",
            definition.get("credential_issuer_id", ""),
        )
        queue_items = [
            dict(row)
            for row in catalog.rows[
                "credential_definition_expansion_queue.csv"
            ]
            if credential_definition_id
            in row.get("candidate_credential_definition_ids", "").split("|")
        ]
        proposal_actors = sorted(
            {
                row.get("proposed_by_actor_id", "")
                for row in [definition, *sources, *domains]
                if row.get("proposed_by_actor_id")
            }
        )
        return {
            "credential_definition": dict(definition),
            "credential_family": dict(family or {}),
            "credential_issuer": dict(issuer or {}),
            "sources": sources,
            "domain_elements": domains,
            "queue_items": queue_items,
            "proposal_actor_ids": proposal_actors,
            "review_boundary": (
                "Acceptance makes this public definition reusable as reference "
                "meaning only. It does not establish a participant claim."
            ),
        }

    def preview(self, request: CredentialReviewRequest) -> dict[str, Any]:
        with tempfile.TemporaryDirectory(prefix="pia-phase3a-preview-") as temp:
            staged_root = Path(temp) / "catalog"
            result = self._prepare_review(request, staged_root)
            result["applied"] = False
            result["mode"] = "preview"
            return result

    def apply(self, request: CredentialReviewRequest) -> dict[str, Any]:
        with self._catalog_lock():
            with tempfile.TemporaryDirectory(prefix="pia-phase3a-apply-") as temp:
                staged_root = Path(temp) / "catalog"
                result = self._prepare_review(request, staged_root)
                self._install_staged_files(staged_root)
            installed = self._validated_catalog()
            result["applied"] = True
            result["mode"] = "apply"
            result["installed_validation"] = installed.validate()
            return result

    def _prepare_review(
        self,
        request: CredentialReviewRequest,
        staged_root: Path,
    ) -> dict[str, Any]:
        current = self._validated_catalog()
        package = self.review_package(
            request.credential_definition_id, catalog=current
        )
        self._validate_request(request, package)
        shutil.copytree(self.catalog_root, staged_root)
        timestamp = self._timestamp()
        changes, review_ids = self._mutate_catalog(
            staged_root, request, timestamp
        )
        projected = CredentialDefinitionCatalog(staged_root, self.contract_path)
        validation = projected.validate()
        if not validation["valid"]:
            codes = sorted(
                {
                    finding["code"]
                    for finding in validation["findings"]
                    if finding["severity"] == "error"
                }
            )
            raise CredentialReviewError(
                "Projected catalog failed validation: " + ", ".join(codes)
            )
        resolution = projected.resolve(
            package["credential_definition"]["canonical_title"],
            issuer_hint=package["credential_issuer"].get("canonical_name", ""),
            version_hint=package["credential_definition"].get(
                "version_label", ""
            ),
        )
        return {
            "credential_definition_id": request.credential_definition_id,
            "decision": request.decision,
            "reviewer_actor_id": request.reviewer_actor_id,
            "reviewed_at": timestamp,
            "review_record_ids": review_ids,
            "changes": changes,
            "projected_validation": validation,
            "projected_resolution_status": resolution["resolution_status"],
            "participant_claims_established": [],
        }

    def _validate_request(
        self,
        request: CredentialReviewRequest,
        package: dict[str, Any],
    ) -> None:
        if not ACTOR_ID_PATTERN.fullmatch(request.reviewer_actor_id):
            raise CredentialReviewError(
                "Reviewer identity must be a 3-80 character accountable actor ID."
            )
        if request.reviewer_actor_id in package["proposal_actor_ids"]:
            raise CredentialReviewError(
                "The proposing actor cannot review its own definition package."
            )
        if request.reviewer_role not in REVIEWER_ROLES:
            raise CredentialReviewError("Reviewer role is not authorized.")
        if request.decision not in REVIEWABLE_DECISIONS:
            raise CredentialReviewError("Review decision is not supported.")
        if len(request.review_basis) < 20:
            raise CredentialReviewError(
                "Review basis must provide a concise accountable rationale."
            )
        if request.decision == "accepted_with_limits" and not request.limitations:
            raise CredentialReviewError(
                "Acceptance with limits requires an explicit limitation."
            )
        if request.review_cycle != "annual":
            raise CredentialReviewError(
                "Phase 3A currently permits the annual review cycle only."
            )
        if not request.sources_reviewed or not request.boundary_reviewed:
            raise CredentialReviewError(
                "Confirm both source inspection and negative-boundary review."
            )

        definition = package["credential_definition"]
        sources = package["sources"]
        domains = package["domain_elements"]
        if not sources or not domains:
            raise CredentialReviewError(
                "A reviewable package requires sources and domain elements."
            )
        if request.decision in CURRENT_REVIEW_STATES:
            issuer_sources = [
                source
                for source in sources
                if source.get("source_authority") == "issuer_primary"
                and source.get("access_status") == "accessible"
            ]
            if not issuer_sources:
                raise CredentialReviewError(
                    "Acceptance requires an accessible issuer-primary source."
                )
            if definition.get("source_conflict_status") in {
                "material",
                "unresolved",
            }:
                raise CredentialReviewError(
                    "Material source conflict must be resolved before acceptance."
                )
            if (
                request.decision == "accepted"
                and (
                    not definition.get("effective_from")
                    or not definition.get("effective_to")
                )
            ):
                raise CredentialReviewError(
                    "Unknown effective boundaries require acceptance with limits."
                )

    def _mutate_catalog(
        self,
        root: Path,
        request: CredentialReviewRequest,
        timestamp: str,
    ) -> tuple[list[dict[str, str]], list[str]]:
        definitions = self._read_csv(root, "credential_definition.csv")
        sources = self._read_csv(root, "credential_definition_source.csv")
        domains = self._read_csv(root, "credential_domain_element.csv")
        reviews = self._read_csv(root, "credential_definition_review.csv")
        queue = self._read_csv(
            root, "credential_definition_expansion_queue.csv"
        )
        definition = self._find(
            definitions,
            "credential_definition_id",
            request.credential_definition_id,
        )
        if definition is None:
            raise CredentialReviewError("Credential definition was not found.")
        targets: list[tuple[str, dict[str, str], str]] = [
            (
                "credential_definition",
                definition,
                "credential_definition_id",
            )
        ]
        targets.extend(
            ("credential_definition_source", row, "credential_definition_source_id")
            for row in sources
            if row.get("credential_definition_id")
            == request.credential_definition_id
        )
        targets.extend(
            ("credential_domain_element", row, "credential_domain_element_id")
            for row in domains
            if row.get("credential_definition_id")
            == request.credential_definition_id
        )

        changes: list[dict[str, str]] = []
        for _, row, id_field in targets:
            old_status = row.get("review_status", "")
            row["review_status"] = request.decision
            if "updated_at" in row:
                row["updated_at"] = timestamp
            changes.append(
                {
                    "target_record_id": row[id_field],
                    "field": "review_status",
                    "before": old_status,
                    "after": request.decision,
                }
            )

        now_date = timestamp[:10]
        if request.decision in CURRENT_REVIEW_STATES:
            updates = {
                "definition_status": "issuer_verified",
                "definition_expansion_required": "false",
                "next_action": "",
                "last_reviewed": now_date,
                "review_cycle": request.review_cycle,
            }
            queue_state = "closed"
            queue_action = (
                "Independent reference-definition review completed; monitor "
                "the annual cycle and issuer changes."
            )
        else:
            updates = {
                "definition_expansion_required": "true",
                "last_reviewed": now_date,
                "review_cycle": request.review_cycle,
            }
            if definition.get("definition_status") == "issuer_verified":
                updates["definition_status"] = "source_defined"
            if request.decision == "revision_requested":
                queue_state = "in_progress"
                queue_action = (
                    "Revise the definition package in response to the recorded "
                    "review basis and resubmit it for independent review."
                )
            elif request.decision == "rejected":
                queue_state = "blocked"
                queue_action = (
                    "Do not reuse this definition; identify a corrected source "
                    "or replacement definition before reopening review."
                )
            else:
                queue_state = "blocked"
                queue_action = (
                    "Resolve the recorded definition dispute through governance "
                    "review before reuse."
                )
            updates["next_action"] = queue_action
        for field, after in updates.items():
            before = definition.get(field, "")
            definition[field] = after
            if before != after:
                changes.append(
                    {
                        "target_record_id": request.credential_definition_id,
                        "field": field,
                        "before": before,
                        "after": after,
                    }
                )

        for item in queue:
            if request.credential_definition_id not in item.get(
                "candidate_credential_definition_ids", ""
            ).split("|"):
                continue
            for field, after in (
                ("processing_state", queue_state),
                ("next_action", queue_action),
                ("updated_at", timestamp),
            ):
                before = item.get(field, "")
                item[field] = after
                if before != after:
                    changes.append(
                        {
                            "target_record_id": item[
                                "definition_expansion_item_id"
                            ],
                            "field": field,
                            "before": before,
                            "after": after,
                        }
                    )

        prior_by_target: dict[str, dict[str, str]] = {}
        for review in reviews:
            target_id = review.get("target_record_id", "")
            previous = prior_by_target.get(target_id)
            if previous is None or review.get("reviewed_at", "") >= previous.get(
                "reviewed_at", ""
            ):
                prior_by_target[target_id] = review

        review_ids: list[str] = []
        for index, (target_type, row, id_field) in enumerate(targets, start=1):
            target_id = row[id_field]
            digest = hashlib.sha256(
                "\x00".join(
                    [
                        request.reviewer_actor_id,
                        target_id,
                        request.decision,
                        timestamp,
                        str(len(reviews)),
                    ]
                ).encode("utf-8")
            ).hexdigest()[:12].upper()
            review_id = f"CRED-REV-P3A-{digest}-{index:03d}"
            reviews.append(
                {
                    "credential_definition_review_id": review_id,
                    "target_record_type": target_type,
                    "target_record_id": target_id,
                    "reviewer_role": request.reviewer_role,
                    "reviewer_actor_id": request.reviewer_actor_id,
                    "decision": request.decision,
                    "review_basis": request.review_basis,
                    "limitations": request.limitations,
                    "reviewed_at": timestamp,
                    "supersedes_credential_definition_review_id": (
                        prior_by_target.get(target_id, {}).get(
                            "credential_definition_review_id", ""
                        )
                    ),
                }
            )
            review_ids.append(review_id)

        self._write_csv(root, "credential_definition.csv", definitions)
        self._write_csv(root, "credential_definition_source.csv", sources)
        self._write_csv(root, "credential_domain_element.csv", domains)
        self._write_csv(root, "credential_definition_review.csv", reviews)
        self._write_csv(
            root, "credential_definition_expansion_queue.csv", queue
        )
        return changes, review_ids

    def _validated_catalog(self) -> CredentialDefinitionCatalog:
        catalog = CredentialDefinitionCatalog(
            self.catalog_root, self.contract_path
        )
        validation = catalog.validate()
        if not validation["valid"]:
            raise CredentialReviewError(
                "The source catalog must validate before review."
            )
        return catalog

    def _timestamp(self) -> str:
        value = self.clock()
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z")

    @contextmanager
    def _catalog_lock(self) -> Iterator[None]:
        lock_path = self.catalog_root / ".phase3a-review.lock"
        try:
            descriptor = os.open(
                lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY
            )
        except FileExistsError as exc:
            raise CredentialReviewError(
                "Another catalog review is currently being applied."
            ) from exc
        try:
            try:
                os.write(
                    descriptor,
                    (
                        f"pid={os.getpid()}\ncreated_at={self._timestamp()}\n"
                    ).encode("utf-8"),
                )
            finally:
                os.close(descriptor)
            yield
        finally:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

    def _install_staged_files(self, staged_root: Path) -> None:
        originals = {
            filename: (self.catalog_root / filename).read_bytes()
            for filename in MUTATED_FILES
        }
        transaction = hashlib.sha256(self._timestamp().encode()).hexdigest()[:12]
        installed: list[str] = []
        try:
            for filename in MUTATED_FILES:
                target = self.catalog_root / filename
                temporary = self.catalog_root / f".{filename}.{transaction}.tmp"
                temporary.write_bytes((staged_root / filename).read_bytes())
                os.replace(temporary, target)
                installed.append(filename)
        except Exception:
            for filename in installed:
                target = self.catalog_root / filename
                temporary = (
                    self.catalog_root / f".{filename}.{transaction}.rollback"
                )
                temporary.write_bytes(originals[filename])
                os.replace(temporary, target)
            raise

    def _read_csv(
        self, root: Path, filename: str
    ) -> list[dict[str, str]]:
        with (root / filename).open(
            "r", encoding="utf-8-sig", newline=""
        ) as handle:
            return [
                {key: value or "" for key, value in row.items()}
                for row in csv.DictReader(handle)
            ]

    def _write_csv(
        self,
        root: Path,
        filename: str,
        rows: list[dict[str, str]],
    ) -> None:
        headers = self._contract_headers(filename)
        with (root / filename).open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(
                {field: row.get(field, "") for field in headers}
                for row in rows
            )

    def _contract_headers(self, filename: str) -> list[str]:
        catalog = CredentialDefinitionCatalog(
            self.catalog_root, self.contract_path
        )
        return list(catalog.contract["files"][filename]["headers"])

    @staticmethod
    def _find(
        rows: list[dict[str, str]], id_field: str, record_id: str
    ) -> dict[str, str] | None:
        return next(
            (row for row in rows if row.get(id_field) == record_id), None
        )
