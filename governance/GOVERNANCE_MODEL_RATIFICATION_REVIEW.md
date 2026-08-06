---
artifact_id: governance-model-ratification-review-001
title: OSI-PIA Governance Model Ratification Review
domain: shared
layer: governance
authority: supporting
status: active
version: "0.1.0"
owner: repository-governance
lifecycle_state: validation
last_reviewed: "2026-07-24"
review_cycle: annual
---

# OSI-PIA Governance Model Ratification Review

## Review decision

The OSI-PIA Governance Model version `0.2.0` is internally congruent with the
current written architecture after the corrections recorded below. Its
governance validation is reproducible and is required in continuous
integration.

The model remains `authority: working`, `status: proposed`, and
`lifecycle_state: congruence`. This review supplies Validation evidence; it
does not perform Promotion. The next decision is a scoped shared ADR that
either ratifies the model or returns it for a stated revision.

## Scope

The review compared the model with:

- Repository Architecture and Repository Conventions;
- Knowledge Lifecycle and Knowledge Management Governance;
- the Registry, Namespace, Connector, Graph, and component standards;
- accepted shared, OSI, PIA, and implementation ADRs;
- foundational, engineering, Hippocratic, and PIA measurement principles;
- ontology, graph, contract, assurance, research, and publication registries;
- the current repository tree, automated tests, and continuous-integration
  workflow.

## Section review

| Governance Model area | Authority compared | Result | Review note |
|---|---|---|---|
| Status and adoption | Knowledge Management Governance; Repository Conventions | congruent after revision | Version `0.2.0` is explicitly at Congruence and does not claim Promotion |
| Authority framework | Repository Architecture; accepted ADRs; Registry Standard | congruent with bounded ratification decision | Current dependencies describe derivation; the ratification ADR must establish the post-promotion constitutional direction |
| Domain governance | ADR-SHARED-0001 and ADR-SHARED-0002; Namespace Standard | congruent | OSI and PIA remain peers with explicit shared mappings and no silent semantic inheritance |
| Identity and registries | Repository Conventions; Registry Standard | congruent | Stable identity, canonical location, status, authority, ownership, and dependency rules agree |
| Ontology and graph | ontology and graph registries; Graph Standards; reference-graph congruence profile | congruent | Technology-independent ontology remains authoritative over projections and database convenience |
| Evidence, connectors, contracts, and data | assurance architecture; connector and contract standards; Hippocratic and measurement principles | congruent after participant-data correction | Participant datasets are now local-only and the tracked-tree boundary is machine checked |
| Decisions, change, and migration | ADR governance; Repository Migration Plan | congruent | Durable choices, bounded migrations, validation, and recovery remain traceable |
| Lifecycle, promotion, and retirement | Knowledge Lifecycle; Knowledge Management Governance | congruent after role mapping | Contributor, Reviewer, Maintainer, Promotion Authority, and Steward now map explicitly to model roles |
| Assurance and human-centered governance | Assurance Architecture; ethical and measurement authorities | congruent | Automation supplies evidence but cannot make consequential human or promotion decisions |
| Stewardship, exceptions, and compliance | Knowledge Management Governance; Repository Conventions | congruent with bounded exception registry | The exception schema is explicit; no active exception exists; the first accepted exception requires a designated durable registry home |
| Review and amendment | Repository Conventions; Knowledge Management Governance | congruent after review metadata addition | `last_reviewed` is `2026-07-24`; the active review cycle is annual from the completed review, with event triggers retained |

## Findings and dispositions

### RR-001 — Participant data in the repository

**Original condition:** Participant source exports, normalized datasets, and a
participant-specific graph import were tracked despite the repository's
privacy rules.

**Disposition:** Resolved for the current repository tree.

- removed `data/PIA-participants/`;
- removed the participant-specific graph import;
- added `/data/PIA-participants/` to `.gitignore`;
- documented local, explicitly configured loading in `data/README.md`;
- replaced a participant-numbered anti-report path with an explicitly
  synthetic methodological example;
- retained synthetic temporary test fixtures and non-identifying contract
  examples;
- added an automated check that fails if either participant-data path becomes
  tracked or a participant-numbered publication path is introduced.

Earlier Git objects may still contain removed material. MIG-010 formally
bounds this historical exposure: it must be assessed before publication or
wider sharing, and any history rewrite requires explicit authorization and
remote coordination. Current-tree removal is not evidence that history is
clear.

### RR-002 — Constitutional dependency direction

**Original condition:** The proposal said standards implement the model while
the model's registry row depended on those existing standards.

**Disposition:** Formally bounded until ratification.

At Congruence, the dependencies accurately record the proposal's derivation
from canonical authorities. The ratification ADR must state which standards
become subordinate implementations, update the affected dependency rows in
the same change, and reject any cycle. No dependency reversal is implied
before Promotion.

### RR-003 — Promotion role ambiguity

**Original condition:** Model-specific stewardship roles did not explicitly
map to the canonical knowledge-governance roles.

**Disposition:** Resolved in version `0.2.0`.

The model now maps Contributor, Reviewer, Maintainer, Promotion Authority, and
Steward to its domain roles. Repository access or implementation ownership
does not confer Promotion Authority. Ratification of this model requires an
accepted scoped shared ADR.

### RR-004 — Governance validation was manual

**Original condition:** Registry, metadata, link, dependency, ontology, review
status, and participant-data checks were not reproducible in the repository.

**Disposition:** Resolved.

`software/governance/validate_repository_governance.py` now checks:

- registry schema, controlled values, unique IDs, canonical locations, and
  metadata agreement;
- registered dependency resolution and cycle absence;
- governed Markdown metadata and review fields;
- repository-relative Markdown links;
- namespaced ontology item identity;
- migration coverage for every `review-required` artifact;
- current tracked paths for the participant-data boundary.

The validator has a repository integration test and a dedicated
continuous-integration step.

### RR-005 — Exception persistence

**Original condition:** The model defined exception content but did not name a
durable registry.

**Disposition:** Bounded without inventing an unused registry.

Every exception must be a governed `exception-` artifact linked from the
affected primary registry row or migration record. No active exception exists.
The ratification authority must designate a durable registry home before the
first exception is accepted.

### RR-006 — Review schedule metadata

**Original condition:** Annual review was stated only in prose.

**Disposition:** Resolved.

Repository Conventions now define `last_reviewed` and `review_cycle`. The
model records this development review on `2026-07-24` and uses an annual cycle,
while retaining earlier event-based review triggers.

### RR-007 — Unrepresented review-required artifacts

**Original condition:** `principle-hippocratic-supporting-001` and
`contract-data-legacy-001` were `review-required` but absent from the migration
plan.

**Disposition:** Resolved as a visible bounded migration.

MIG-009 now requires semantic comparison, steward review, registry resolution,
and inbound-reference validation for both artifacts.

### RR-008 — Stale graph-boundary migration status

**Original condition:** MIG-004 remained `identified` after explicit graph
ownership, registries, migration ordering, and reference-graph congruence were
implemented.

**Disposition:** Resolved.

MIG-004 is now `complete`; future graph changes remain subject to its
registered architecture and validators.

## Redundancy assessment

The model consolidates but does not replace detailed implementation standards.
No canonical document is removed by this review. Apparent repetition is
acceptable where the model states constitutional intent and the lower
authority supplies a bounded schema, interface, or procedure.

The only dependency-direction change is deferred to the ratification ADR so
that a proposal cannot silently make its current authorities subordinate.

## Validation record

Validation is complete when all of the following pass on the same working
tree:

| Check | Required result |
|---|---|
| Governance validator | no registry, metadata, dependency, link, ontology, review-status, or participant-boundary errors |
| Python compilation | governance validator, software, and tests compile |
| Automated test suite | all discovered tests pass |
| Diff integrity | no whitespace errors |
| Participant tracked-path scan | no path below `data/PIA-participants/` or a participant-specific graph-import directory |

Completed 2026-07-24:

| Check | Result |
|---|---|
| Governance validator | passed: 94 registry rows, 48 governed metadata artifacts, 360 repository links, 91 ontology IDs, and the tracked repository tree checked |
| Python compilation | passed for `software/` and `tests/` |
| Automated test suite | passed: 20 of 20 tests |
| Diff integrity | passed: no whitespace errors |
| Participant tracked-path scan | passed: no tracked participant dataset, participant-specific graph-import path, or participant-numbered publication path |

Validation evidence supports a ratification decision but does not itself
promote the model.

## Ratification gate

The model is ready for a ratification decision when:

1. the Validation record above passes;
2. affected stewards accept or amend this review;
3. a scoped shared ADR records promotion rationale, authority, dependency
   direction, canonical location, stewardship, known limitations, and review
   expectations;
4. the model and registry metadata are advanced together.

If ratified, the promotion change should establish version `1.0.0`,
`authority: canonical`, `status: active`, and the appropriate post-promotion
lifecycle state. This review does not make that change.
