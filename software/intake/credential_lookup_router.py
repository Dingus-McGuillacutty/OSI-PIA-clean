#!/usr/bin/env python3
"""Phase 3B.1 minimized, catalog-first credential lookup router.

The router accepts participant-free reference descriptors only. It performs
no external network access and persists no request or response.

artifact_id: component-pia-credential-lookup-router-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from software.intake.credential_definition_catalog import (
    DEFAULT_CATALOG,
    DEFAULT_CONTRACT as DEFAULT_CATALOG_CONTRACT,
    REPOSITORY_ROOT,
    RESTRICTED_VALUE_PATTERNS,
    CredentialDefinitionCatalog,
)


DEFAULT_LOOKUP_CONTRACT = (
    REPOSITORY_ROOT
    / "data"
    / "contracts"
    / "pia_credential_lookup_request_contract_v0.1.json"
)
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
BOUNDARY = (
    "Reference lookup does not establish participant completion, current "
    "standing, application, proficiency, performance, or identity."
)


class CredentialLookupError(ValueError):
    """Raised when a minimized lookup request violates its boundary."""


def _normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(value.split())


@dataclass(frozen=True)
class CredentialLookupRequest:
    credential_title: str
    issuer_hint: str = ""
    version_hint: str = ""
    credential_type_hint: str = ""
    jurisdiction_hint: str = ""
    source_scope: str = "pia_catalog_only"
    purpose: str = "reference_definition_resolution"

    def canonical_values(self) -> dict[str, str]:
        return {
            field: _normalized(str(value))
            for field, value in asdict(self).items()
        }


class CredentialLookupRouter:
    """Validates and routes participant-free reference lookups."""

    def __init__(
        self,
        catalog_root: Path | str = DEFAULT_CATALOG,
        *,
        catalog_contract_path: Path | str = DEFAULT_CATALOG_CONTRACT,
        lookup_contract_path: Path | str = DEFAULT_LOOKUP_CONTRACT,
    ) -> None:
        self.catalog_root = Path(catalog_root).resolve()
        self.catalog_contract_path = Path(catalog_contract_path).resolve()
        self.lookup_contract_path = Path(lookup_contract_path).resolve()
        self.lookup_contract = json.loads(
            self.lookup_contract_path.read_text(encoding="utf-8")
        )

    def request_from_mapping(
        self, value: dict[str, Any]
    ) -> CredentialLookupRequest:
        if not isinstance(value, dict):
            raise CredentialLookupError("Lookup request must be an object.")
        request_contract = self.lookup_contract["request"]
        allowed_fields = set(request_contract["allowed_fields"])
        prohibited_fragments = tuple(
            fragment.casefold()
            for fragment in request_contract["prohibited_field_fragments"]
        )
        unknown_fields = sorted(set(value) - allowed_fields)
        if unknown_fields:
            prohibited = [
                field
                for field in unknown_fields
                if any(
                    fragment in field.casefold()
                    for fragment in prohibited_fragments
                )
            ]
            if prohibited:
                raise CredentialLookupError(
                    "Participant-scoped lookup fields are prohibited: "
                    + ", ".join(prohibited)
                )
            raise CredentialLookupError(
                "Lookup fields are not permitted: " + ", ".join(unknown_fields)
            )

        normalized_input: dict[str, str] = {}
        for field in allowed_fields:
            raw = value.get(field, "")
            if raw is None:
                raw = ""
            if not isinstance(raw, str):
                raise CredentialLookupError(
                    f"Lookup field {field!r} must be text."
                )
            normalized_input[field] = raw.strip()
        normalized_input["source_scope"] = (
            normalized_input["source_scope"] or "pia_catalog_only"
        )
        normalized_input["purpose"] = (
            normalized_input["purpose"]
            or "reference_definition_resolution"
        )
        request = CredentialLookupRequest(**normalized_input)
        self.validate_request(request)
        return request

    def validate_request(self, request: CredentialLookupRequest) -> None:
        values = asdict(request)
        contract = self.lookup_contract["request"]
        for field in contract["required_fields"]:
            if not values.get(field, ""):
                raise CredentialLookupError(
                    f"Required lookup field {field!r} is empty."
                )
        for field, maximum in contract["max_lengths"].items():
            value = values.get(field, "")
            if len(value) > maximum:
                raise CredentialLookupError(
                    f"Lookup field {field!r} exceeds {maximum} characters."
                )
            if value and CONTROL_CHARACTER_PATTERN.search(value):
                raise CredentialLookupError(
                    f"Lookup field {field!r} contains control characters."
                )
            for code, pattern in RESTRICTED_VALUE_PATTERNS:
                if value and pattern.search(value):
                    raise CredentialLookupError(
                        f"Lookup value violates the {code} privacy boundary."
                    )
        for field, allowed in contract["enums"].items():
            if values.get(field, "") not in allowed:
                raise CredentialLookupError(
                    f"Lookup field {field!r} is outside the governed vocabulary."
                )

    def route(
        self, request: CredentialLookupRequest | dict[str, Any]
    ) -> dict[str, Any]:
        if isinstance(request, dict):
            request = self.request_from_mapping(request)
        elif not isinstance(request, CredentialLookupRequest):
            raise CredentialLookupError(
                "Lookup request must use the governed request type."
            )
        else:
            self.validate_request(request)

        catalog = CredentialDefinitionCatalog(
            self.catalog_root, self.catalog_contract_path
        )
        validation = catalog.validate()
        if not validation["valid"]:
            raise CredentialLookupError(
                "The local credential catalog must validate before routing."
            )
        resolution = catalog.resolve(
            request.credential_title,
            issuer_hint=request.issuer_hint,
            version_hint=request.version_hint,
        )
        fingerprint = self._fingerprint(request)
        route = self._route_for_status(
            resolution["resolution_status"], request=request
        )
        result: dict[str, Any] = {
            "lookup_request_id": (
                f"CRED-LOOKUP-{fingerprint[:12].upper()}-001"
            ),
            "request_fingerprint": f"sha256:{fingerprint}",
            "resolution_status": resolution["resolution_status"],
            "routing_outcome": route["routing_outcome"],
            "credential_definition_id": resolution.get(
                "credential_definition_id", ""
            ),
            "candidate_credential_family_ids": resolution.get(
                "candidate_credential_family_ids", []
            ),
            "candidate_credential_definition_ids": resolution.get(
                "candidate_credential_definition_ids", []
            ),
            "participant_clarification_required": route[
                "participant_clarification_required"
            ],
            "clarification_prompt": route["clarification_prompt"],
            "public_catalog_action": route["public_catalog_action"],
            "external_lookup_permitted": False,
            "next_action": route["next_action"],
            "participant_claims_established": [],
            "boundary": BOUNDARY,
            "negative_boundaries": resolution.get("negative_boundaries", []),
        }
        if "expansion_queue_proposal" in resolution:
            result["participant_free_queue_proposal"] = resolution[
                "expansion_queue_proposal"
            ]
        self.validate_response(result)
        return result

    def validate_response(self, result: dict[str, Any]) -> None:
        response_contract = self.lookup_contract["response"]
        missing = [
            field
            for field in response_contract["required_fields"]
            if field not in result
        ]
        if missing:
            raise CredentialLookupError(
                "Router response is incomplete: " + ", ".join(missing)
            )
        if result["routing_outcome"] not in response_contract[
            "routing_outcomes"
        ]:
            raise CredentialLookupError("Router outcome is not governed.")
        if result["public_catalog_action"] not in response_contract[
            "public_catalog_actions"
        ]:
            raise CredentialLookupError("Catalog action is not governed.")
        if result["participant_claims_established"] != []:
            raise CredentialLookupError(
                "Reference lookup cannot establish participant claims."
            )
        if result["external_lookup_permitted"] is not False:
            raise CredentialLookupError(
                "Phase 3B.1 cannot authorize external lookup."
            )
        serialized = json.dumps(result, ensure_ascii=False)
        for code, pattern in RESTRICTED_VALUE_PATTERNS:
            if pattern.search(serialized):
                raise CredentialLookupError(
                    f"Router response violates the {code} privacy boundary."
                )

    @staticmethod
    def _fingerprint(request: CredentialLookupRequest) -> str:
        canonical = json.dumps(
            request.canonical_values(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def _route_for_status(
        status: str,
        *,
        request: CredentialLookupRequest,
    ) -> dict[str, Any]:
        routes: dict[str, dict[str, Any]] = {
            "resolved": {
                "routing_outcome": "resolved",
                "participant_clarification_required": False,
                "clarification_prompt": "",
                "public_catalog_action": "none",
                "next_action": (
                    "Reuse the accepted PIA definition; assess completion and "
                    "application separately in protected intake."
                ),
            },
            "definition_found_pending_review": {
                "routing_outcome": "manual_definition_review",
                "participant_clarification_required": False,
                "clarification_prompt": "",
                "public_catalog_action": "use_existing_review_queue",
                "next_action": (
                    "Complete Phase 3A independent definition review; do not "
                    "ask the participant to research the public definition."
                ),
            },
            "version_unknown": {
                "routing_outcome": "confirm_version",
                "participant_clarification_required": True,
                "clarification_prompt": (
                    "Which edition, version, examination outline, or "
                    "completion-period form of this credential applies?"
                ),
                "public_catalog_action": "none",
                "next_action": (
                    "Request only the missing version distinction, then rerun "
                    "catalog-first resolution."
                ),
            },
            "ambiguous_title": {
                "routing_outcome": "ambiguous_credential",
                "participant_clarification_required": True,
                "clarification_prompt": (
                    "Which issuing organization and exact credential title "
                    "apply to this record?"
                ),
                "public_catalog_action": "none",
                "next_action": (
                    "Request only the issuer/title distinction, then rerun "
                    "catalog-first resolution."
                ),
            },
            "source_needed": {
                "routing_outcome": "external_registry_lookup",
                "participant_clarification_required": False,
                "clarification_prompt": "",
                "public_catalog_action": (
                    "propose_participant_free_source_research"
                ),
                "next_action": (
                    "Prepare a participant-free external-registry lookup; "
                    "Phase 3B.1 does not execute network access."
                ),
            },
            "inaccessible_definition": {
                "routing_outcome": "source_access_review",
                "participant_clarification_required": False,
                "clarification_prompt": "",
                "public_catalog_action": "use_existing_review_queue",
                "next_action": (
                    "Locate an accessible issuer or approved archived source."
                ),
            },
            "conflicting_definition": {
                "routing_outcome": "conflict_review",
                "participant_clarification_required": False,
                "clarification_prompt": "",
                "public_catalog_action": "use_existing_review_queue",
                "next_action": (
                    "Route the material definition conflict to assurance or "
                    "governance review."
                ),
            },
        }
        if status not in routes:
            raise CredentialLookupError(
                f"Catalog returned unsupported resolution status {status!r}."
            )
        route = dict(routes[status])
        if (
            status == "version_unknown"
            and not request.version_hint
        ):
            route["clarification_prompt"] = (
                "What year or named edition of this credential applies, if "
                "that information is available?"
            )
        return route


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Route a participant-free credential reference through the local "
            "PIA catalog. Phase 3B.1 performs no network access or persistence."
        )
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--issuer", default="")
    parser.add_argument("--version", default="")
    parser.add_argument(
        "--credential-type",
        default="",
        choices=(
            "",
            "certification",
            "license",
            "certificate",
            "course_completion",
            "badge",
            "degree",
            "other",
        ),
    )
    parser.add_argument("--jurisdiction", default="")
    parser.add_argument("--catalog-root", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--catalog-contract",
        type=Path,
        default=DEFAULT_CATALOG_CONTRACT,
    )
    parser.add_argument(
        "--lookup-contract",
        type=Path,
        default=DEFAULT_LOOKUP_CONTRACT,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    router = CredentialLookupRouter(
        args.catalog_root,
        catalog_contract_path=args.catalog_contract,
        lookup_contract_path=args.lookup_contract,
    )
    try:
        result = router.route(
            {
                "credential_title": args.title,
                "issuer_hint": args.issuer,
                "version_hint": args.version,
                "credential_type_hint": args.credential_type,
                "jurisdiction_hint": args.jurisdiction,
                "source_scope": "pia_catalog_only",
                "purpose": "reference_definition_resolution",
            }
        )
    except CredentialLookupError as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
