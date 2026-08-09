# PIA Capability Evidence Mapping Profile v0.2

**Status:** Working, proposed extension  
**Scope:** Evidence-to-Capability assertions using the PIA Capability and
Pattern Profile  
**Base contract:** OSI-PIA Data and Graph Contract v0.1

## Purpose

This profile adds the fields required to distinguish behavioral application,
educational preparation, behavioral inference, and contextual suggestion
without changing the base participant package contract. It applies only when:

```text
mapping_profile = pia-capability-evidence-mapping-0.2
```

The governing meanings and vocabulary are defined by the
[PIA Behavioral Capability Inference Principle](../../principles/PIA%20Behavioral%20Capability%20Inference%20Principle.md)
and the
[PIA Capability and Pattern Profile](../../ontology/PIA_CAPABILITY_PATTERN_PROFILE.md).

## Base requirements

Every mapping retains all Evidence–Capability Mapping fields required by the
[Data and Graph Contract](OSI_PIA_Data_Graph_Contract_v0.1.md):

- `mapping_id`;
- `evidence_id`;
- `capability_id`;
- `relationship_type = SUPPORTS`;
- `confidence`;
- `confidence_basis`;
- `proposed_by`;
- `review_status`;
- `created_at`; and
- optional `reviewed_at`.

The congruent graph assertion also retains `assertion_id`,
`assertion_basis`, `human_review_required`, and
`relationship_semantic_class = analytical_assertion`.

## Extension fields

| Field | Type | Required | Allowed value or meaning |
|---|---|---:|---|
| `mapping_profile` | string | yes | `pia-capability-evidence-mapping-0.2` |
| `profile_capability_id` | string | yes | Stable Capability ID declared in the working PIA profile |
| `inference_level` | enum | yes | `directly_demonstrated`, `strongly_inferred`, `contextually_suggested` |
| `evidence_role` | enum | yes | `behavioral_demonstration`, `educational_preparation` |
| `claim_scope` | enum | yes | `demonstrated_application`, `knowledge_exposure` |
| `application_status` | enum | yes | `described_in_source`, `explicitly_attributed_in_source`, `topically_aligned_not_verified`, `not_established` |
| `aligned_experience_ids` | delimited stable IDs | no | Listed experiences with explicit or topical alignment |
| `alignment_basis` | string | yes | Basis and epistemic limit of any experience alignment |
| `credential_definition_status` | enum | educational mappings | `source_defined`, `issuer_verified`, `participant_defined`, `title_only_unknown`, `conflicting_definition` |
| `credential_definition_source` | string | educational mappings | Source used to interpret the course or credential body |
| `credential_definition_uri` | string | no | Stable source or issuer URI when available |
| `credential_domain_scope` | string | resolved credential definitions | Bounded assessed domain |
| `definition_expansion_required` | boolean | educational mappings | `true` for title-only or conflicting definitions |
| `behavioral_basis` | string | yes | Source-grounded behavior that supports the mapping |
| `negative_boundary` | string | yes | What the behavior does not establish |
| `scope_limit` | string | yes | Experience, project, role, time, or operating context of the inference |
| `source_independence_note` | string | yes | Independence, relationship, duplication, or unknown status of supporting sources |

`behavioral_basis` becomes the graph relationship's `assertion_basis`.

## Validation rules

1. Every supplied evidence item must receive a consideration disposition,
   whether or not it produces a mapping.
2. A title, credential, or self-label alone cannot satisfy a
   `behavioral_demonstration` claim.
3. Course and credential bodies may support `educational_preparation` with
   `claim_scope = knowledge_exposure`.
4. An educational mapping must use
   `inference_level = contextually_suggested`,
   `review_status = needs_review`, and `confidence <= 0.49`.
5. Educational evidence alone cannot set
   `application_status = described_in_source`.
   `explicitly_attributed_in_source` is permitted only when a source
   explicitly links completion or preparation to one or more listed
   experiences; the educational claim remains `knowledge_exposure`.
6. Topical course-to-experience alignment does not prove causation,
   sequencing, application, or independent corroboration.
7. Every educational mapping must state its definition status. A
   `title_only_unknown` or `conflicting_definition` mapping must set
   `definition_expansion_required = true`. An `issuer_verified` definition
   must retain its source, URI, and bounded domain scope.
8. Same-context problem-directed behavior and interdependent group,
   department, project, or organizational evidence may strongly infer Shared
   Problem-Solving. Group membership alone is insufficient.
9. `negative_boundary`, `scope_limit`, `alignment_basis`, and
   `source_independence_note` cannot
   be empty.
10. `contextually_suggested` must have `review_status = needs_review` and
   `confidence <= 0.49`.
11. An unaccepted `strongly_inferred` mapping must have
   `confidence <= 0.89`.
12. `Teamwork` and `Leadership` are prohibited direct Capability targets under
   this profile.
13. Duplicate source copies do not count as independent corroboration.
14. Missing, mixed, or contradictory evidence must remain visible.
15. A rejected or superseded mapping must not be presented as current
   participant evidence.

These are assertion-quality gates. They are not measures of the participant.

## Conservative suggestion policy

Capability suggestions are triage aids, not mappings. A suggestion must never
be selected automatically or enter the graph without the normal proposal and
review gates.

- `direct` suggestions may be shown only when the source wording directly
  describes the capability's bounded behavior.
- `contextual` suggestions may be shown only as secondary, review-required
  possibilities and must use `inference_level = contextually_suggested` with
  confidence at or below `0.49`.
- No suggestion is shown when the interpretation would require assumptions
  about competence, authority, outcomes, leadership, a durable trait, or a
  broader capability than the source supports.
- A suggestion display is limited to one primary and two secondary candidates.
- Growth opportunities and ontology gaps are reported separately from
  supported capability suggestions.
- Duplicate or near-duplicate source copies do not increase suggestion
  confidence or count as independent corroboration.

The interface must display the evidence-to-capability reason and the boundary
for every suggestion. A participant or reviewer may reject, replace, or defer a
suggestion without changing the underlying Evidence record.

## Parameterized import

The reference importer accepts a `$mappings` list and writes only to existing
Evidence and Capability nodes:

[`import_capability_evidence_mappings_v0.2.cypher`](../../graph/cypher/imports/import_capability_evidence_mappings_v0.2.cypher)

Rows that do not satisfy the executable predicates are not written. Callers
must compare the returned mapping IDs with the submitted IDs and treat any
difference as a validation finding rather than a silent success.

## Validation

The reference validator checks vocabulary completeness, generic-label
prohibition, capability-to-pattern contribution metadata, behavioral mapping
fields, inference-level confidence bounds, and permitted pattern finding
states:

[`validate_pia_capability_evidence_profile_v0.2.cypher`](../../graph/cypher/validation/validate_pia_capability_evidence_profile_v0.2.cypher)

The profile passes with zero participant mappings because the reference
database may contain vocabulary without participant data. Once mappings
exist, every mapping using this profile must pass the same checks.

## Compatibility and promotion

This is an additive extension to v0.1. Existing contract-valid mappings remain
valid but do not acquire behavioral-inference status without the required
fields.

The profile remains working and proposed. Installation in a reference graph
does not make it canonical.
