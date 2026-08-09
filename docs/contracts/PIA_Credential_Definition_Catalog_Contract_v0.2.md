---
artifact_id: contract-pia-credential-catalog-001
domain: pia
layer: contract
authority: working
status: proposed
version: "0.2.0"
owner: pia-intake
lifecycle_state: formulation
development_state: in_progress_subject_to_change
---

# PIA Credential Definition Catalog Contract v0.2

## Purpose

This contract defines the participant-free reference package used by Phase 3
of the PIA Intake Subsystem to resolve what a credential issuer says a
credential covers.

It separates:

- public issuer and credential identities;
- versioned credential definitions;
- public definition-source metadata;
- assessed domain elements;
- accountable definition reviews; and
- unresolved definition-expansion work.

The catalog does not contain participant credential completion, application,
performance, identity, or contact data.

## Governing boundary

A catalog definition can support a bounded statement about issuer-published
eligibility, assessment, or domain scope. It cannot establish that a
participant:

- earned or currently holds the credential;
- performed effectively in any assessed domain;
- applied the preparation at work;
- possesses every capability topically related to the credential; or
- should be assigned a professional identity.

Credential-to-capability crosswalks remain a later ontology-mapping concern.
They are not part of this Phase 3 catalog contract.

## Package files

| File | Record |
|---|---|
| `credential_issuer.csv` | Public credential issuer identity |
| `credential_family.csv` | Stable credential identity across versions |
| `credential_definition.csv` | One versioned or effective-dated definition |
| `credential_definition_source.csv` | Public source and integrity metadata |
| `credential_domain_element.csv` | Bounded issuer-defined domain or area |
| `credential_definition_review.csv` | Human review decision and limits |
| `credential_definition_expansion_queue.csv` | Participant-free unresolved catalog work |

The exact machine-readable headers, enumerations, identifier patterns, and
required fields are defined by
[`pia_credential_definition_catalog_contract_v0.2.json`](../../data/contracts/pia_credential_definition_catalog_contract_v0.2.json).

Pipe-delimited values may be used for aliases and foreign-key lists in this
working version.

## Knowledge and review separation

Definition knowledge state and review disposition are independent.

Definition knowledge values:

```text
title_only_unknown
source_needed
source_defined
issuer_verified
conflicting_definition
obsolete_definition
inaccessible_definition
```

Review values:

```text
pending
accepted
accepted_with_limits
revision_requested
rejected
disputed
superseded
```

An official issuer source may justify `source_defined`. It does not become
`issuer_verified` or reusable merely because software downloaded it.
`issuer_verified` requires an accepted or accepted-with-limits definition
review supported by issuer-primary material.

## Source capture

Every accessible definition source records:

- submitted and resolved URI;
- source type and authority;
- publisher and document identity;
- retrieval time;
- SHA-256 content fingerprint;
- content size;
- relevant section locator;
- access and review state; and
- a retention or licensing note.

The repository retains metadata and bounded summaries by default. It does not
retain a complete source copy unless authority to retain and redistribute that
copy is established.

A source fingerprint proves which retrieved byte representation was reviewed.
It does not prove that the source remains unchanged at the URI.

## Versioning

- Material changes to assessed scope, eligibility, examination method, or
  effective period create a new `credential_definition_id`.
- Definitions remain linked through
  `supersedes_credential_definition_id`.
- Supersession chains must be acyclic.
- Historical definitions remain addressable.
- A participant completion date may resolve to an applicable definition only
  when the effective period is known.
- An unresolved version remains a queue item rather than silently using the
  current definition.

## Title and acronym collision

Titles and acronyms are search keys, not identities. Two issuers may use the
same title or acronym.

Resolution therefore considers:

1. normalized title or alias;
2. issuer identity or issuer hint;
3. version label;
4. effective date; and
5. accepted review state.

An unresolved collision produces `ambiguous_title` and a definition-expansion
queue proposal. It must not choose the most popular or first matching
credential.

## Resolution outcomes

The working resolver may return:

| Outcome | Meaning |
|---|---|
| `resolved` | One accepted definition satisfies the supplied boundaries |
| `definition_found_pending_review` | A source-defined candidate exists but is not reusable yet |
| `ambiguous_title` | More than one family or definition remains plausible |
| `version_unknown` | Family is known but the applicable definition is not |
| `source_needed` | No adequately sourced definition is available |
| `inaccessible_definition` | The expected definition source cannot currently be reviewed |
| `conflicting_definition` | Material source or version conflict remains unresolved |

Resolution identifies reference meaning only. It does not resolve participant
completion or application.

## Expansion queue

The repository queue contains catalog work only. It may retain a credential
title, issuer hint, version hint, candidate reference IDs, reason, status, and
next action.

It must not retain:

- participant identifiers or labels;
- certificate numbers;
- participant completion dates;
- private source locations;
- participant notes;
- participant application claims; or
- contact information.

Participant-scoped definition questions remain in the encrypted intake store.
Only a minimized, participant-free reference question may be promoted into
the shared catalog queue.

## Review boundary

No automated resolver, extraction process, or proposing agent may accept its
own definition.

Every proposed definition, definition source, and domain element records a
`proposed_by_actor_id`. Every review records a distinct
`reviewer_actor_id`. These are accountable process identities rather than
participant identities. A review is invalid when its reviewer identity equals
the proposal identity of its target.

Accepted definitions require:

- at least one reviewed source;
- a domain summary;
- a negative boundary;
- completed definition review;
- review date;
- review cycle; and
- no unresolved material conflict.

An accepted-with-limits definition must state the limits explicitly in its
review record.

The current decision on an accepted definition, source, or domain element must
match that target's latest review record. One package decision creates
separate review records for the definition and each related source and domain
element so that every accepted target is independently traceable.

The Phase 3A transition vocabulary is:

| Decision | Reuse effect | Expansion-queue effect |
|---|---|---|
| `accepted` | Eligible for `issuer_verified` resolution | `closed` |
| `accepted_with_limits` | Eligible for bounded `issuer_verified` resolution | `closed` |
| `revision_requested` | Not reusable | `in_progress` |
| `rejected` | Excluded from current resolution | `blocked` |
| `disputed` | Not reusable pending governance resolution | `blocked` |

Unresolved effective boundaries prevent unqualified acceptance. They may be
handled through explicit limited acceptance or revision.

## Preview-first mutation

A Phase 3A review is first applied to a temporary catalog copy and validated.
Preview never mutates the source catalog. Apply requires a successful staged
validation, explicit write enablement, explicit confirmation, a single-writer
lock, append-only review records, rollback on installation failure, and
installed-state revalidation.

The workbench is governed in detail by the
[Phase 3A Credential Review Profile](../../architecture/pia-intake/PIA_Phase_3A_Credential_Review_Profile.md).

## Validation

The Phase 3 validator checks:

- exact contract files and headers;
- required values and enumerations;
- stable and unique identities;
- foreign-key integrity;
- issuer-primary support for issuer-verified definitions;
- source retrieval and SHA-256 metadata;
- definition and review boundaries;
- proposer/reviewer separation and current-decision consistency;
- domain-source traceability;
- title collision preservation;
- effective-date and supersession consistency;
- expansion-queue next actions;
- absence of participant-scoped fields and signatures; and
- resolver exclusion of rejected or superseded definitions.

## Status

This contract is `working/proposed`, in progress, and subject to change.
Implementation supports reversible participant-free testing. It does not
authorize production credential interpretation, autonomous review, graph
projection, or participant assessment.
