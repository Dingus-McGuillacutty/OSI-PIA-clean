#!/usr/bin/env python3
"""Protected-to-public credential-resolution linkage for PIA Phase 3B.

The service constructs a new minimized lookup request from an encrypted
participant session, invokes the local catalog first, optionally invokes an
approved public registry connector, and stores the private relationship only
inside the encrypted session.

artifact_id: component-pia-credential-intake-linkage-001
authority: working
status: proposed
version: 0.1.0
lifecycle_state: formulation
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from software.intake.credential_lookup_router import (
    CredentialLookupRequest,
    CredentialLookupRouter,
)
from software.intake.credential_registry_connector import (
    CredentialRegistryConnector,
    CredentialRegistryError,
)
from software.intake.local_private_intake import IntakePreflightError
from software.intake.protected_participant_intake import (
    ProtectedParticipantIntakeStore,
)


CLARIFICATION_FIELDS = {
    "credential_title",
    "issuer_hint",
    "version_hint",
}


class CredentialIntakeLinkage:
    """Coordinates private intake and participant-free reference resolution."""

    def __init__(
        self,
        store: ProtectedParticipantIntakeStore,
        *,
        router: CredentialLookupRouter | None = None,
        connector: CredentialRegistryConnector | None = None,
    ) -> None:
        self.store = store
        self.router = router or CredentialLookupRouter()
        self.connector = connector

    @property
    def external_lookup_configured(self) -> bool:
        return self.connector is not None

    def _request(
        self,
        descriptor: dict[str, Any],
    ) -> CredentialLookupRequest:
        # Construct a new object from the exact public descriptor allow-list.
        # Never serialize a participant record and attempt to remove fields.
        minimized = {
            "credential_title": descriptor.get("credential_title", ""),
            "issuer_hint": descriptor.get("issuer_hint", ""),
            "version_hint": descriptor.get("version_hint", ""),
            "credential_type_hint": descriptor.get(
                "credential_type_hint", ""
            ),
            "jurisdiction_hint": descriptor.get("jurisdiction_hint", ""),
            "source_scope": "pia_catalog_only",
            "purpose": "reference_definition_resolution",
        }
        return self.router.request_from_mapping(minimized)

    def _resolve_public_reference(
        self,
        request: CredentialLookupRequest,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        local_result = self.router.route(request)
        external_result: dict[str, Any] = {
            "configured": self.external_lookup_configured,
            "attempted": False,
            "disposition": "not_needed",
            "candidates": [],
        }
        if local_result["routing_outcome"] != "external_registry_lookup":
            return local_result, external_result
        if self.connector is None:
            external_result["disposition"] = "connector_not_configured"
            return local_result, external_result
        external_result["attempted"] = True
        try:
            connector_result = self.connector.search(request)
        except CredentialRegistryError as exc:
            external_result.update(
                {
                    "disposition": "connector_error",
                    "error": str(exc),
                }
            )
        else:
            external_result.update(connector_result)
        return local_result, external_result

    @staticmethod
    def _participant_view(record: dict[str, Any]) -> dict[str, Any]:
        local_result = record["local_lookup"]
        external_result = record["external_lookup"]
        next_action = str(local_result["next_action"])
        if external_result.get("disposition") == (
            "candidates_pending_phase3a_review"
        ):
            next_action = (
                "A possible public registry match was found. It is awaiting "
                "independent definition review; no capability claim has been "
                "made from it."
            )
        elif external_result.get("disposition") == "no_registry_match":
            next_action = (
                "No public registry match was found. A reviewer may add an "
                "issuer link or research the credential definition manually."
            )
        elif external_result.get("disposition") == "connector_error":
            next_action = (
                "The public registry could not be checked. The local result "
                "was preserved and can be retried without re-entering private "
                "participant information."
            )
        elif external_result.get("disposition") == "connector_not_configured":
            next_action = (
                "The local catalog has no definition yet. External registry "
                "lookup is not configured, so public-source review remains "
                "available as a manual step."
            )
        return {
            "credential_entry_id": record["credential_entry_id"],
            "credential_title": record["descriptor"]["credential_title"],
            "issuer_hint": record["descriptor"]["issuer_hint"],
            "version_hint": record["descriptor"]["version_hint"],
            "routing_outcome": local_result["routing_outcome"],
            "resolution_status": local_result["resolution_status"],
            "credential_definition_id": local_result[
                "credential_definition_id"
            ],
            "participant_clarification_required": local_result[
                "participant_clarification_required"
            ],
            "clarification_prompt": local_result["clarification_prompt"],
            "external_lookup_disposition": external_result.get(
                "disposition", ""
            ),
            "external_candidate_count": len(
                external_result.get("candidates", [])
            ),
            "next_action": next_action,
            "participant_claims_established": [],
            "updated_at": record["updated_at"],
        }

    def resolve(
        self,
        *,
        session_id: str,
        descriptor: dict[str, Any],
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        request = self._request(descriptor)
        local_result, external_result = self._resolve_public_reference(request)
        record = self.store.save_credential_resolution(
            session_id=session_id,
            credential_entry_id="",
            descriptor=asdict(request),
            local_lookup=local_result,
            external_lookup=external_result,
            clarification=None,
            actor_subject=actor_subject,
            actor_role=actor_role,
        )
        return self._participant_view(record)

    def clarify(
        self,
        *,
        session_id: str,
        credential_entry_id: str,
        field: str,
        response: str,
        actor_subject: str,
        actor_role: str,
    ) -> dict[str, Any]:
        if field not in CLARIFICATION_FIELDS:
            raise IntakePreflightError(
                "Clarification is limited to title, issuer, or version."
            )
        response = response.strip()
        if not response or len(response) > 300:
            raise IntakePreflightError(
                "A short credential clarification is required."
            )
        record = self.store.get_credential_resolution(
            session_id,
            credential_entry_id=credential_entry_id,
            actor_role=actor_role,
        )
        if record["local_lookup"].get(
            "participant_clarification_required"
        ) is not True:
            raise IntakePreflightError(
                "This credential does not currently require participant clarification."
            )
        descriptor = dict(record["descriptor"])
        descriptor[field] = response
        request = self._request(descriptor)
        local_result, external_result = self._resolve_public_reference(request)
        updated = self.store.save_credential_resolution(
            session_id=session_id,
            credential_entry_id=credential_entry_id,
            descriptor=asdict(request),
            local_lookup=local_result,
            external_lookup=external_result,
            clarification={"field": field, "response": response},
            actor_subject=actor_subject,
            actor_role=actor_role,
        )
        return self._participant_view(updated)

    def status(
        self,
        *,
        session_id: str,
        actor_role: str,
    ) -> list[dict[str, Any]]:
        records = self.store.list_credential_resolutions(
            session_id,
            actor_role=actor_role,
        )
        return [self._participant_view(record) for record in records]
