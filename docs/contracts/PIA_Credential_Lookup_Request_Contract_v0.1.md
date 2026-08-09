---
artifact_id: contract-pia-credential-lookup-001
domain: pia
layer: contract
authority: working
status: proposed
version: "0.1.0"
owner: pia-intake
lifecycle_state: formulation
development_state: in_progress_subject_to_change
---

# PIA Credential Lookup Request Contract v0.1

## Purpose

This contract defines the minimized participant-free request that Phase 3B
uses to resolve public credential meaning.

The request may answer:

> Does the governed PIA library already contain a reusable definition matching
> this credential title, issuer, and version description?

It must not answer:

> Who supplied the credential, whether they completed it, what evidence they
> submitted, or how they applied it?

Phase 3B.1 checks the local PIA catalog only. External registry lookup,
protected-store integration, durable request persistence, and participant
clarification interfaces remain later controlled increments.

## Allowed request fields

| Field | Meaning |
|---|---|
| `credential_title` | Public credential title or acronym |
| `issuer_hint` | Public issuing-organization name or alias |
| `version_hint` | Public edition, version, exam outline, or body-of-knowledge label |
| `credential_type_hint` | Governed credential-type hint |
| `jurisdiction_hint` | Public regulatory or geographic scope |
| `source_scope` | Phase 3B.1 is fixed to `pia_catalog_only` |
| `purpose` | Fixed to `reference_definition_resolution` |

The exact allowed fields, lengths, enumerations, response fields, and routing
outcomes are defined by the
[machine-readable contract](../../data/contracts/pia_credential_lookup_request_contract_v0.1.json).

Unknown request fields are rejected. They are not silently stripped.

## Prohibited request content

A Phase 3B lookup request must not contain:

- participant identity or label;
- intake-session or participant evidence identity;
- certificate, license, or membership number;
- participant completion or expiration date;
- participant notes, feedback, or application claims;
- uploaded document or extracted private content;
- contact information;
- private storage location or local path; or
- employment, performance, or professional-identity evidence.

The request is reference-only even when it is created during a protected
participant intake.

## Catalog-first rule

Phase 3B checks the accepted local PIA catalog before any participant
clarification or external registry research.

| Catalog result | Phase 3B route |
|---|---|
| `resolved` | Reuse the accepted definition |
| `definition_found_pending_review` | Route the existing package to Phase 3A |
| `version_unknown` | Request only the missing version distinction |
| `ambiguous_title` | Request only the issuer or version distinction |
| `source_needed` | Propose participant-free external source research |
| `inaccessible_definition` | Route source-access review |
| `conflicting_definition` | Route assurance or governance conflict review |

Participant clarification is required only when the participant can uniquely
resolve an issuer or version distinction. Missing public definition research
is not transferred to the participant merely because the lookup originated
during their intake.

## Deterministic identity

The router derives:

- a canonical request fingerprint from the allowed normalized fields; and
- a participant-free `lookup_request_id` from that fingerprint.

Identical reference descriptors therefore produce the same identity without
retaining a participant or intake-session link.

The fingerprint establishes request equivalence. It does not establish
credential completion or ownership.

## Response boundary

Every response states:

- the catalog resolution status;
- the Phase 3B routing outcome;
- candidate reference identities;
- whether narrowly scoped clarification is required;
- the public catalog action;
- whether external lookup was permitted;
- a safe next action;
- an empty participant-claims collection; and
- the reference-only negative boundary.

Phase 3B.1 always returns `external_lookup_permitted=false`.

## Persistence

Phase 3B.1 performs an in-memory lookup and does not persist requests or
responses. Later persistence requires a separate retention, audit,
authentication, privacy, and correction design.

The participant-free expansion proposal returned by the existing resolver is
also not persisted by Phase 3B.1.

## Status

This contract is `working/proposed`, in progress, and subject to change. It
does not authorize external API access, API-key storage, participant-data
export, autonomous definition acceptance, or graph projection.
