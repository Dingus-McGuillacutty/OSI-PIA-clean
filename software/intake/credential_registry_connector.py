#!/usr/bin/env python3
"""Controlled external credential-reference connectors for PIA Phase 3B.2.

Connectors accept only the participant-free Phase 3B lookup request. They
return review candidates and never accept or install credential definitions.

artifact_id: component-pia-credential-registry-connector-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from software.intake.credential_lookup_router import (
    CredentialLookupRequest,
    CredentialLookupRouter,
)


PRODUCTION_ENDPOINT = (
    "https://apps.credentialengine.org/assistant/search/ctdl"
)
SANDBOX_ENDPOINT = (
    "https://sandbox.credentialengine.org/assistant/search/ctdl"
)
APPROVED_ENDPOINTS = {PRODUCTION_ENDPOINT, SANDBOX_ENDPOINT}
DEFAULT_TIMEOUT_SECONDS = 20
MAX_RESULTS = 10


class CredentialRegistryError(RuntimeError):
    """Raised when a controlled public registry lookup cannot be completed."""


class CredentialRegistryConnector(Protocol):
    connector_id: str
    registry_name: str

    def search(
        self,
        request: CredentialLookupRequest,
    ) -> dict[str, Any]:
        ...


Transport = Callable[
    [str, dict[str, str], dict[str, Any], int],
    dict[str, Any],
]


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _canonical_fingerprint(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _language_text(value: Any, *, maximum: int) -> str:
    if isinstance(value, str):
        return value.strip()[:maximum]
    if isinstance(value, dict):
        for candidate in value.values():
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()[:maximum]
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, str) and item.strip():
                        return item.strip()[:maximum]
    if isinstance(value, list):
        for item in value:
            text = _language_text(item, maximum=maximum)
            if text:
                return text
    return ""


def _string_values(value: Any, *, maximum_items: int = 12) -> list[str]:
    candidates = value if isinstance(value, list) else [value]
    result: list[str] = []
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            result.append(candidate.strip()[:500])
        elif isinstance(candidate, dict):
            reference = (
                candidate.get("@id")
                or candidate.get("ceterms:ctid")
                or candidate.get("ceterms:name")
            )
            if isinstance(reference, str) and reference.strip():
                result.append(reference.strip()[:500])
        if len(result) >= maximum_items:
            break
    return result


def _default_transport(
    endpoint: str,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    request = Request(
        endpoint,
        method="POST",
        headers=headers,
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise CredentialRegistryError(
                    f"The credential registry returned HTTP {response.status}."
                )
            content_type = response.headers.get_content_type()
            if content_type not in {"application/json", "application/ld+json"}:
                raise CredentialRegistryError(
                    "The credential registry returned an unexpected content type."
                )
            raw = response.read(5 * 1024 * 1024 + 1)
    except HTTPError as exc:
        if exc.code in {401, 403}:
            message = "Credential registry authorization was rejected."
        elif exc.code == 429:
            message = "Credential registry request limit was reached."
        else:
            message = f"The credential registry returned HTTP {exc.code}."
        raise CredentialRegistryError(message) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise CredentialRegistryError(
            "The credential registry could not be reached safely."
        ) from exc
    if len(raw) > 5 * 1024 * 1024:
        raise CredentialRegistryError(
            "The credential registry response exceeded the bounded size."
        )
    try:
        value = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CredentialRegistryError(
            "The credential registry response was not valid JSON."
        ) from exc
    if not isinstance(value, dict):
        raise CredentialRegistryError(
            "The credential registry response was not an object."
        )
    return value


@dataclass(frozen=True)
class CredentialEngineSearchConnector:
    """Server-side Credential Engine CTDL Search API connector."""

    api_key: str = field(repr=False)
    endpoint: str = PRODUCTION_ENDPOINT
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    transport: Transport = _default_transport

    connector_id = "connector-pia-credential-engine-search-001"
    registry_name = "Credential Engine Registry"

    def __post_init__(self) -> None:
        if self.endpoint not in APPROVED_ENDPOINTS:
            raise CredentialRegistryError(
                "The credential registry endpoint is not allowlisted."
            )
        if not self.api_key.strip():
            raise CredentialRegistryError(
                "A server-side Credential Engine API key is required."
            )
        if not 1 <= self.timeout_seconds <= 60:
            raise CredentialRegistryError(
                "The credential registry timeout must be between 1 and 60 seconds."
            )

    @staticmethod
    def _credential_types(credential_type: str) -> list[str]:
        return {
            "certification": ["ceterms:Certification"],
            "license": ["ceterms:License"],
            "certificate": ["ceterms:Certificate"],
            "course_completion": [
                "ceterms:CertificateOfCompletion",
                "ceterms:Certificate",
            ],
            "badge": [
                "ceterms:Badge",
                "ceterms:DigitalBadge",
                "ceterms:OpenBadge",
            ],
            "degree": ["ceterms:Degree"],
            "other": ["ceterms:Credential"],
            "": ["ceterms:Credential"],
        }[credential_type]

    def build_query(
        self,
        request: CredentialLookupRequest,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {
            "@type": self._credential_types(
                request.credential_type_hint
            ),
            "ceterms:name": {
                "search:value": request.credential_title,
                "search:matchType": "search:contains",
            },
            "search:resourcePublishType": "primary",
        }
        if request.issuer_hint:
            query["ceterms:ownedBy"] = {
                "ceterms:name": {
                    "search:value": request.issuer_hint,
                    "search:matchType": "search:contains",
                }
            }
        return {
            "Query": {
                **query,
            },
            "Skip": 0,
            "Take": MAX_RESULTS,
            "Sort": "search:relevance",
            "IncludeResultsMetadata": True,
            "DescriptionSetType": "Resource",
        }

    @staticmethod
    def _result_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
        value = (
            payload.get("Results")
            or payload.get("results")
            or payload.get("@graph")
            or []
        )
        if not isinstance(value, list):
            raise CredentialRegistryError(
                "The credential registry result collection was invalid."
            )
        return [row for row in value if isinstance(row, dict)][:MAX_RESULTS]

    @staticmethod
    def _metadata_index(
        payload: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        value = payload.get("ResultsMetadata") or payload.get(
            "resultsMetadata"
        )
        if not isinstance(value, list):
            return {}
        result: dict[str, dict[str, Any]] = {}
        for item in value:
            if not isinstance(item, dict):
                continue
            uri = str(
                item.get("ResourceURI") or item.get("resourceURI") or ""
            ).strip()
            if uri:
                result[uri] = item
        return result

    @classmethod
    def normalize_response(
        cls,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        metadata = cls._metadata_index(payload)
        candidates: list[dict[str, Any]] = []
        for row in cls._result_rows(payload):
            resource_uri = str(row.get("@id") or "").strip()[:1000]
            record_metadata = metadata.get(resource_uri, {})
            candidate = {
                "external_identity": str(
                    row.get("ceterms:ctid") or resource_uri
                ).strip()[:500],
                "resource_uri": resource_uri,
                "credential_name": _language_text(
                    row.get("ceterms:name"), maximum=300
                ),
                "credential_types": _string_values(row.get("@type")),
                "description": _language_text(
                    row.get("ceterms:description"), maximum=1200
                ),
                "subject_webpage": _language_text(
                    row.get("ceterms:subjectWebpage"), maximum=1000
                ),
                "owner_references": _string_values(
                    row.get("ceterms:ownedBy")
                ),
                "offerer_references": _string_values(
                    row.get("ceterms:offeredBy")
                ),
                "credential_status_types": _string_values(
                    row.get("ceterms:credentialStatusType")
                ),
                "record_created": str(
                    record_metadata.get("RecordCreated", "")
                )[:80],
                "record_updated": str(
                    record_metadata.get("RecordUpdated", "")
                )[:80],
                "record_owned_by": str(
                    record_metadata.get("RecordOwnedBy", "")
                )[:500],
                "record_published_by": str(
                    record_metadata.get("RecordPublishedBy", "")
                )[:500],
                "record_publish_type": str(
                    record_metadata.get("RecordPublishType", "")
                )[:80],
            }
            if not candidate["credential_name"]:
                continue
            candidate["candidate_fingerprint"] = _canonical_fingerprint(
                candidate
            )
            candidates.append(candidate)
        return candidates

    def search(
        self,
        request: CredentialLookupRequest,
    ) -> dict[str, Any]:
        # Reuse the strict request contract even if a caller bypassed the
        # catalog-first linkage service.
        CredentialLookupRouter().validate_request(request)
        query = self.build_query(request)
        payload = self.transport(
            self.endpoint,
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "PIA-Credential-Resolution/0.1",
            },
            query,
            self.timeout_seconds,
        )
        candidates = self.normalize_response(payload)
        total = payload.get("TotalResults")
        if not isinstance(total, int):
            total = payload.get("totalResults")
        if not isinstance(total, int):
            total = len(candidates)
        return {
            "connector_id": self.connector_id,
            "registry_name": self.registry_name,
            "registry_environment": (
                "sandbox"
                if self.endpoint == SANDBOX_ENDPOINT
                else "production"
            ),
            "retrieved_at": _utc_now(),
            "query_fingerprint": _canonical_fingerprint(query),
            "total_results": max(total, 0),
            "candidates": candidates,
            "disposition": (
                "candidates_pending_phase3a_review"
                if candidates
                else "no_registry_match"
            ),
            "definition_accepted": False,
            "participant_claims_established": [],
            "boundary": (
                "Registry matches are public reference candidates and require "
                "Phase 3A review before reusable definition acceptance."
            ),
        }
