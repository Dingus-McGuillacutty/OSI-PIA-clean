---
artifact_id: contract-pia-intake-phase1-001
domain: pia
layer: contract
authority: working
status: proposed
version: "0.1.0"
owner: pia-intake
lifecycle_state: formulation
---

# PIA Intake Phase 1 Record Contract v0.1

> **Development state: IN PROGRESS — SUBJECT TO CHANGE.**
> This working, proposed contract package defines the first participant-free
> implementation boundary for the PIA intake subsystem. It is suitable for
> synthetic fixtures and reversible local development only. It is not an
> accepted participant-data, production, or graph-write contract.

## Purpose

This contract defines the stable record identities, fields, state
vocabularies, foreign-key relationships, supersession behavior, and blocking
validation required by Phase 1 of the
[PIA Intake Subsystem Framework](../../architecture/pia-intake/PIA_Intake_Subsystem_Framework.md).

It provides seven distinct record types:

1. Intake Session;
2. Source Artifact;
3. Credential Definition;
4. Credential Application Assertion;
5. Review Event;
6. Intake Assurance Finding; and
7. Projection Manifest.

It also defines a materialized `CredentialDefinitionQueueItem` workflow view.
The queue is not an eighth source of truth; its fields point to the contracted
records and preserve routing state.

The machine-readable projection is:

[`pia_intake_phase1_contract_v0.1.json`](../../data/contracts/pia_intake_phase1_contract_v0.1.json)

## Governing boundary

This contract is additive to, and subordinate to:

- the [PIA Measurement Doctrine](../../governance/PIA_MEASUREMENT_DOCTRINE.md);
- the
  [OSI-PIA Data and Graph Contract](OSI_PIA_Data_Graph_Contract_v0.1.md);
- the
  [PIA Capability Evidence Mapping Profile](PIA_Capability_Evidence_Mapping_Profile_v0.2.md);
- the [OSI-PIA Import Contract](OSI_PIA_Import_Contract_v0.1.md);
- the
  [PIA Credential Definition Library](../../architecture/pia-intake/PIA_Credential_Definition_Library.md);
  and
- repository privacy, namespace, provenance, assurance, and governance rules.

This contract does not authorize participant data in Git. Repository fixtures
must use reserved synthetic participant identifiers in the `PIA-9000` through
`PIA-9999` range.

## Contract principles

- Original, derived, definitional, application, review, assurance, and
  projection records remain distinct.
- Every record has one stable primary identity.
- Corrections create a new record version and point to the superseded record.
- A record may not supersede itself.
- Processing state, knowledge status, and review disposition are separate.
- Unknown values remain empty or use an allowed explicit knowledge state.
- Credential definitions never contain participant identifiers.
- Credential definitions describe preparation; application assertions
  describe proposed participant-context connections.
- Review events append history and never erase prior proposals.
- Projection manifests enumerate scope; projection code may not expand it.
- A report or graph output cannot re-enter intake without a new Source
  Artifact record.

## Package files

A Phase 1 package contains:

```text
intake_session.csv
source_artifact.csv
credential_definition.csv
credential_application_assertion.csv
review_event.csv
intake_assurance_finding.csv
projection_manifest.csv
credential_definition_queue.csv
```

UTF-8 CSV, RFC 4180 quoting, lowercase `snake_case` headers, ISO 8601 dates and
datetimes, and empty optional values are required. Literal null substitutes
such as `N/A` or `none` are prohibited unless an enum explicitly defines the
value.

## Common identities

| Record | ID field | Working pattern |
|---|---|---|
| Intake Session | `intake_session_id` | `PIA-{participant}-INT-{sequence}` |
| Source Artifact | `source_artifact_id` | `PIA-{participant}-ART-{sequence}` |
| Credential Definition | `credential_definition_id` | `CRED-DEF-{stable-token}-{sequence}` |
| Credential Family | `credential_family_id` | `CRED-FAM-{stable-token}` |
| Application Assertion | `application_assertion_id` | `PIA-{participant}-APP-{sequence}` |
| Review Event | `review_event_id` | `PIA-{participant}-REV-{sequence}` |
| Assurance Finding | `finding_id` | `PIA-{participant}-FND-{sequence}` |
| Projection Manifest | `projection_manifest_id` | `PIA-{participant}-PRJ-{sequence}` |
| Queue Item | `queue_item_id` | `PIA-{participant}-QUE-{sequence}` |

Readable tokens are not definition authority. Final identifier syntax remains
subject to namespace review, but issued IDs are immutable.

## Shared state vocabularies

### Processing state

```text
received
preflight
in_progress
waiting_for_input
ready_for_review
ready_for_projection
projected
closed
blocked
```

### Review disposition

```text
pending
accepted
accepted_with_limits
revision_requested
rejected
disputed
superseded
```

### Credential knowledge status

```text
title_only_unknown
source_needed
source_defined
issuer_verified
participant_defined
conflicting_definition
obsolete_definition
inaccessible_definition
```

These axes must not be collapsed. For example, a queue item may be
`waiting_for_input`, `conflicting_definition`, and `pending`.

## 1. Intake Session

An Intake Session is a purpose-bounded collection and review episode.

Header:

```csv
intake_session_id,participant_id,purpose,processing_scope,consent_status,confidentiality,retention_class,processing_state,created_by,created_at,updated_at,supersedes_intake_session_id
```

| Field | Required | Rule |
|---|---:|---|
| `intake_session_id` | yes | Stable unique identity |
| `participant_id` | yes | Existing participant or reserved synthetic ID |
| `purpose` | yes | Plain-language purpose |
| `processing_scope` | yes | Bounded operations authorized for this session |
| `consent_status` | yes | `pending`, `granted`, `limited`, or `withdrawn` |
| `confidentiality` | yes | `internal`, `restricted`, or `participant_private` |
| `retention_class` | yes | Governed retention reference or working value |
| `processing_state` | yes | Shared processing state |
| `created_by` | yes | Human or bounded process identity |
| `created_at` | yes | ISO 8601 datetime |
| `updated_at` | yes | ISO 8601 datetime |
| `supersedes_intake_session_id` | no | Prior session record version |

`withdrawn` consent requires `processing_state` of `blocked` or `closed`.
Consent for one purpose does not authorize a different purpose.

## 2. Source Artifact

A Source Artifact represents an uploaded file, external-source snapshot,
derived extraction, structured statement, or public reference captured by
intake.

Header:

```csv
source_artifact_id,intake_session_id,participant_id,artifact_kind,parent_artifact_id,submitted_by,original_filename,media_type,submitted_uri,resolved_uri,storage_reference,checksum,content_checksum,collected_at,retrieved_at,confidentiality,consent_scope,extraction_method,extraction_status,review_status,created_at,supersedes_source_artifact_id
```

`artifact_kind` values:

```text
upload
external_link_snapshot
extracted_content
structured_statement
public_reference
```

`extraction_method` values:

```text
not_applicable
manual
assisted
automated
```

`extraction_status` values:

```text
not_requested
pending
complete
failed
review_required
```

Required fields are:

```text
source_artifact_id
intake_session_id
participant_id
artifact_kind
submitted_by
storage_reference
checksum
collected_at
confidentiality
consent_scope
extraction_method
extraction_status
review_status
created_at
```

Conditional rules:

- `upload` requires `original_filename` and `media_type`.
- `external_link_snapshot` requires `submitted_uri`, `resolved_uri`,
  `retrieved_at`, and `content_checksum`.
- `extracted_content` requires `parent_artifact_id` and a non-`not_applicable`
  extraction method.
- `parent_artifact_id` must resolve within the package when populated.
- Restricted originals remain private; `storage_reference` must not contain a
  credential, token, password, or embedded private content.

## 3. Credential Definition

A Credential Definition is a reusable, participant-free description of one
credential version.

Header:

```csv
credential_definition_id,credential_family_id,canonical_title,acronym,issuer_name,version_label,effective_from,effective_to,lifecycle_status,definition_status,credential_type,jurisdiction,eligibility_summary,experience_requirement_summary,assessment_summary,domain_scope,primary_source_artifact_ids,secondary_source_artifact_ids,source_conflict_status,negative_boundary,definition_expansion_required,next_action,review_status,last_reviewed,review_cycle,supersedes_credential_definition_id,created_at,updated_at
```

`lifecycle_status` values:

```text
active
historical
retired
renamed
superseded
unknown
```

`credential_type` values:

```text
certification
license
certificate
course_completion
badge
degree
other
```

`source_conflict_status` values:

```text
none
possible
material
unresolved
```

Conditional rules:

- `issuer_verified` requires a primary Source Artifact, domain scope,
  negative boundary, and `definition_expansion_required=false`.
- `title_only_unknown`, `source_needed`, `conflicting_definition`,
  `obsolete_definition`, or `inaccessible_definition` requires
  `definition_expansion_required=true` and a nonempty `next_action`.
- `accepted` or `accepted_with_limits` requires `last_reviewed` and
  `review_cycle`.
- `superseded` lifecycle or review state requires
  `supersedes_credential_definition_id`.
- The record must not contain `participant_id` or participant-specific
  completion, application, or performance fields.

Pipe-delimited source ID lists are permitted in Phase 1. Later contracts may
replace them with normalized association records.

## 4. Credential Application Assertion

A Credential Application Assertion proposes how a credential definition
relates to a participant's documented experience.

Header:

```csv
application_assertion_id,intake_session_id,participant_id,credential_definition_id,credential_evidence_id,experience_id,application_status,alignment_basis,supporting_source_artifact_ids,confidence,negative_boundary,proposed_by,review_status,created_at,reviewed_at,supersedes_application_assertion_id
```

`application_status` values:

```text
explicitly_attributed_in_source
participant_reported_application
topically_aligned_not_verified
not_established
```

Rules:

- `credential_definition_id` resolves to Credential Definition.
- `credential_evidence_id` and `experience_id` use existing base-contract
  identities.
- Explicit or participant-reported application requires an experience.
- Topical alignment must state that it is not proof of application or
  causation.
- `confidence` is between `0.00` and `1.00`.
- Every assertion has an alignment basis and negative boundary.
- Accepted review requires `reviewed_at`.
- The assertion does not alter the Credential Definition.

## 5. Review Event

A Review Event is append-only feedback about a specific record version.

Header:

```csv
review_event_id,intake_session_id,target_record_type,target_record_id,target_record_version,actor_role,actor_reference,disposition,field_scope,reason,response_text,supporting_source_artifact_ids,created_at,supersedes_review_event_id
```

`target_record_type` values:

```text
intake_session
source_artifact
credential_definition
application_assertion
assurance_finding
projection_manifest
credential_definition_queue
```

`actor_role` values:

```text
participant
intake_operator
credential_definition_reviewer
ontology_reviewer
assurance_reviewer
projection_reviewer
```

Rules:

- The target record must resolve within the package for Phase 1 fixtures.
- `actor_reference` is a role or pseudonymous identifier, not an email
  address or access credential.
- A Review Event never modifies or deletes its target.
- A correction results in a revised target and a new Review Event.

## 6. Intake Assurance Finding

An Intake Assurance Finding records a contract, provenance, privacy, consent,
definition, inference, conflict, projection, or audit result.

Header:

```csv
finding_id,intake_session_id,target_record_type,target_record_id,dimension,severity,code,message,evidence_references,logic_chain,uncertainty,disposition,safe_next_action,created_at,resolved_at,supersedes_finding_id
```

`dimension` values:

```text
contract
provenance
privacy
consent
definition
inference
conflict
projection
audit
```

`severity` values:

```text
notice
review
error
blocking
```

`disposition` values:

```text
open
accepted
routed
resolved
waived
superseded
```

Blocking findings require a safe next action and prevent
`ready_for_projection` or `apply` until resolved by an authorized review
event.

## 7. Projection Manifest

A Projection Manifest enumerates the exact records authorized for a
validation, dry-run, or graph write.

Header:

```csv
projection_manifest_id,intake_session_id,participant_id,target_environment,target_database,projection_mode,contract_version,record_selection,record_count,package_checksum,assurance_status,approval_status,approved_by,created_at,applied_at,post_validation_status,supersedes_projection_manifest_id
```

`target_environment` values:

```text
local_sandbox
governed_test
governed_production
```

`projection_mode` values:

```text
validate
dry_run
apply
```

`assurance_status` values:

```text
pending
pass
warning
block
```

`approval_status` values:

```text
pending
approved
rejected
superseded
```

`post_validation_status` values:

```text
not_run
pass
warning
fail
```

Rules:

- `record_selection` is a stable, pipe-delimited record-ID set in Phase 1.
- `record_count` equals the number of selected IDs.
- `apply` requires assurance `pass`, approval `approved`, and `approved_by`.
- An applied manifest requires `applied_at` and post-validation status.
- Participant data cannot target a reference-vocabulary database.
- The projection implementation may write only the declared selection.

## Credential Definition Queue workflow view

Header:

```csv
queue_item_id,intake_session_id,participant_id,credential_evidence_id,credential_title,issuing_authority,credential_definition_id,definition_source_artifact_ids,current_provisional_capability_ids,processing_state,knowledge_status,review_disposition,priority,assigned_role,attempt_count,last_attempt_at,blocked_reason,next_action,created_at,updated_at,supersedes_queue_item_id
```

`priority` values:

```text
low
normal
high
urgent
```

`assigned_role` values:

```text
intake_operator
credential_definition_agent
credential_definition_reviewer
participant
assurance_reviewer
unassigned
```

Rules:

- `credential_evidence_id` identifies the source-grounded participant
  credential record under the base data contract.
- A populated `credential_definition_id` resolves to the definition table.
- Unknown, source-needed, conflicting, obsolete, or inaccessible knowledge
  requires a nonempty next action.
- `blocked` processing requires `blocked_reason`.
- `closed` requires a non-`pending` review disposition.
- Attempt count is a nonnegative integer.
- Supersession preserves queue history instead of changing the meaning of a
  prior item in place.

## Foreign-key relationships

```text
SourceArtifact.intake_session_id
  -> IntakeSession.intake_session_id

CredentialApplicationAssertion.intake_session_id
  -> IntakeSession.intake_session_id

CredentialApplicationAssertion.credential_definition_id
  -> CredentialDefinition.credential_definition_id

ReviewEvent.intake_session_id
  -> IntakeSession.intake_session_id

IntakeAssuranceFinding.intake_session_id
  -> IntakeSession.intake_session_id

ProjectionManifest.intake_session_id
  -> IntakeSession.intake_session_id

CredentialDefinitionQueueItem.intake_session_id
  -> IntakeSession.intake_session_id

CredentialDefinitionQueueItem.credential_definition_id
  -> CredentialDefinition.credential_definition_id when populated
```

Dynamic targets in Review Events and Assurance Findings resolve by
`target_record_type` plus `target_record_id`.

## Supersession

All supersession fields follow the same rules:

- target identity is in the same record type;
- self-supersession is prohibited;
- the target must exist for a complete Phase 1 package;
- supersession chains must not contain cycles;
- a superseded record remains available for audit; and
- current views exclude a superseded record when a valid successor exists.

## Blocking validation

A Phase 1 package fails when it has:

- missing required files, columns, or values;
- unknown columns;
- duplicate primary identities;
- invalid stable-ID format;
- invalid enum, boolean, integer, number, date, or datetime;
- unresolved required foreign keys;
- participant mismatch with the Intake Session;
- credential definition containing participant fields;
- issuer-verified definition without source, scope, or boundary;
- unresolved definition without expansion and next action;
- application assertion without scope or negative boundary;
- accepted record without required review time;
- invalid review or assurance target;
- invalid projection count or apply gate;
- self-supersession, missing supersession target, or cycle;
- a restricted participant signature in a repository fixture; or
- real participant identifiers in a repository fixture.

## Warning and review validation

Nonblocking review findings may include:

- missing optional version or effective date;
- secondary-source-only definition;
- stale review date;
- topical application alignment;
- source conflict marked `possible`;
- pending participant response;
- projection held at dry-run;
- public-source snapshot retention uncertainty; or
- incomplete ontology crosswalk.

Warnings must not be rewritten as successful verification.

## Synthetic reference package

The participant-free reference fixture is:

[`pia-intake-phase1-synthetic`](../../data/fixtures/pia-intake-phase1-synthetic/)

It uses reserved synthetic identifiers and exercises:

- a purpose- and consent-bounded Intake Session;
- uploaded, external-link, and derived Source Artifacts;
- one issuer-verified credential definition;
- one unresolved title-only definition;
- an explicit application assertion;
- participant review;
- an open definition finding;
- a dry-run projection manifest; and
- separate knowledge, processing, and review queue states.

The fixture is test data, not a real participant package or public credential
catalog.

## Reference validator

The working Phase 1 validator is:

[`validate_pia_intake_phase1.py`](../../software/intake/validate_pia_intake_phase1.py)

It is a standard-library, participant-free development component. Passing it
establishes structural contract conformance only; it does not verify source
truth, credential ownership, participant performance, or production
readiness.

## Promotion boundary

This contract remains working and proposed until:

- privacy and threat-model review is complete;
- record and identifier semantics pass ontology review;
- state transitions and supersession pass synthetic regression tests;
- participant feedback and withdrawal paths are tested;
- the credential-library source and licensing boundary is reviewed;
- graph projection has dry-run and post-write assurance;
- an ADR accepts the agent authority model; and
- PIA intake, ontology, assurance, graph, and governance stewards approve
  promotion.
