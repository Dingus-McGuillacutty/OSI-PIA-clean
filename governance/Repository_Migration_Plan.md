---
artifact_id: repo-migration-plan-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.2"
owner: repository-governance
---

# Repository Migration Plan

## Purpose

This plan records known repository-structure inconsistencies and the controlled
sequence for resolving them. It prevents cleanup work from silently changing
authority, breaking references, or entangling the OSI and PIA domains.

This document authorizes no move by itself. Each migration requires its own
reviewable change, validation, and registry update.

## Migration principles

1. Establish governance before changing paths.
2. Register canonical artifacts before moving them.
3. Preserve Git history and prior identifiers.
4. Separate mechanical relocation from changes in meaning.
5. Keep OSI and PIA as peer domains.
6. Make cross-domain dependencies explicit.
7. Validate on case-sensitive and case-insensitive paths.
8. Prefer small, reversible migrations.

## Status vocabulary

| Status | Meaning |
|---|---|
| `identified` | The inconsistency is recorded but the destination is not approved |
| `planned` | Scope and intended destination are defined |
| `ready` | Dependencies and validation are complete |
| `in-progress` | A bounded migration is underway |
| `complete` | The new location is authoritative and references are updated |
| `deferred` | Intentionally postponed with rationale |

## Migration register

| ID | Scope | Current state | Intended state | Status | Required validation |
|---|---|---|---|---|---|
| MIG-001 | ADR collections | Three colliding ADR collections were reconciled; duplicate decisions remain as explicit superseded history | Scope-based `decisions/shared/`, `decisions/osi/`, `decisions/pia/`, and `decisions/implementation/` with one index | complete | Registry reconciled, duplicate decisions reviewed, inbound links updated, status preserved |
| MIG-002 | Connector 001 assets | Root compatibility assets were verified byte-identical and retired | `connectors/connector-001-linkedin/` is the sole canonical location | complete | SHA-256 comparison, reference scan, manifest validation, connector tests |
| MIG-003 | Domain path casing | Paths such as `analysis/PIA/` and retained graph compatibility paths use mixed naming conventions | Lowercase domain paths applied consistently through bounded migrations | identified | Case-sensitive checkout, link scan, script path scan, graph import validation |
| MIG-004 | Graph domain boundaries | Shared, OSI, and PIA graph artifacts coexist below common schema and migration directories | Explicit shared and domain ownership without duplicating common graph contracts | complete | Graph registry, dependency map, migration ordering, reference-graph congruence validation |
| MIG-005 | Architecture collections | Repository, domain, graph, assurance, and knowledge architecture span `architecture/` and `docs/architecture/` | Authority is explicit; files move only where navigation cannot resolve the overlap | deferred | Architecture registry, link scan, documentation index review |
| MIG-006 | Legacy top-level implementation paths | Connector-related `src/`, `config/`, and `templates/` copies are retired; top-level `cypher/` remains to be assessed | Canonical component and graph locations identified; remaining compatibility paths retired deliberately | identified | Reference scan, package/test execution, graph path validation |
| MIG-007 | PIA participant data boundary | Participant datasets, a participant-specific graph import, and a participant-numbered publication path were tracked in the repository | No participant datasets or participant-linked publication paths in the current repository tree; local sources are loaded explicitly when needed for testing | complete | Tracked-path privacy scan, `.gitignore` review, synthetic-fixture tests, import contract validation |
| MIG-008 | Artifact metadata | Most existing governed artifacts predate the common metadata convention | Metadata added when each artifact is materially reviewed, not through an unreviewed bulk rewrite | planned | Schema validation, registry consistency, semantic review |
| MIG-009 | Review-required supporting authorities | `principle-hippocratic-supporting-001` and `contract-data-legacy-001` remain `review-required` | Each is explicitly reconciled, superseded, or retired without losing provenance | identified | Semantic comparison, affected-steward review, registry update, inbound-reference scan |
| MIG-010 | Historical participant-data exposure | The restricted development lineage contains participant-linked paths in five historical commits | Preserve the restricted archive and publish only from an independently initialized sanitized lineage | ready | History scan, clean-tree signature scan, single-root verification, no alternates or remotes, governance and test validation |

## Ordered execution

### Phase 1: Governance baseline

- establish repository architecture;
- establish repository conventions;
- establish this migration plan.

### Phase 2: Repository registries

- define one registry standard;
- create authoritative registries;
- record existing canonical and compatibility locations;
- mark unresolved conflicts `review-required`.

### Phase 3: Decision normalization

Completed 2026-07-23:

- compared ADRs by decision, not filename;
- assigned stable scoped identifiers;
- recorded supersession and dependency relationships;
- moved records after the mapping was registered.

### Phase 4: Connector normalization

Completed 2026-07-23:

- compared root and numbered Connector 001 assets by SHA-256;
- declared the numbered connector canonical;
- added the connector standard and required manifest fields;
- retired byte-identical compatibility copies after reference validation.

### Phase 5: Domain path normalization

- normalize one domain and layer at a time;
- preserve explicit shared, OSI, and PIA boundaries;
- avoid a repository-wide case-only rename.

### Phase 6: Graph and implementation consolidation

- complete dependency inventories;
- distinguish shared graph mechanics from OSI and PIA projections;
- reconcile legacy top-level implementation paths;
- verify both reference databases after every executable migration.

### Phase 7: Participant-data boundary

Completed 2026-07-24 for the current repository tree:

- removed tracked participant packages and participant-specific graph imports;
- converted the participant-numbered anti-report into an explicitly synthetic
  methodological example;
- excluded `data/PIA-participants/` from version control;
- retained only contracts, templates, synthetic test fixtures, and generic
  governed examples;
- required participant datasets to be supplied from explicitly configured
  local sources when testing or importing;
- added an automated tracked-path privacy check.

Git history is a separate exposure surface. MIG-010 formally bounds that risk
and prevents publication or wider sharing from treating current-tree removal
as proof that historical objects are clear.

### Phase 8: Clean release lineage

Prepared 2026-07-24:

- audited the restricted lineage and confirmed participant-linked paths in
  five historical commits;
- removed participant-derived development status and live PIA graph snapshots
  from the release tree;
- replaced restricted participant IDs and named analyst defaults with
  synthetic IDs and placeholders;
- established the
  [Clean Release Standard](CLEAN_RELEASE_STANDARD.md);
- added a registered builder that creates a one-commit root history without
  remotes, alternates, or source Git objects;
- extended governance validation to reject restricted participant identifiers
  and participant-derived snapshot paths.

MIG-010 is `ready`: the governed local clean lineage can be produced and
verified. Remote creation, visibility, and push remain a separate publication
action requiring explicit authorization.

## Migration change record

Each migration commit MUST record:

```yaml
migration_id:
scope:
current_locations:
canonical_destination:
artifact_ids:
dependencies:
semantic_change: false
validation:
recovery:
```

If `semantic_change` is `true`, the change requires an ADR or another explicit
authority record in addition to the migration entry.

## Validation baseline

Use the checks relevant to the affected layer:

- clean repository link and path scan;
- no unregistered duplicate authority;
- no broken imports, tests, or workflow paths;
- existing automated tests pass;
- manifests and machine-readable contracts parse;
- graph migrations remain idempotent;
- OSI and PIA reference-graph validators pass when graph paths change;
- private participant material remains excluded from the current tracked tree;
- historical participant-data exposure is assessed before publication or
  wider sharing;
- `git diff --check` reports no whitespace errors.

## Recovery

A migration must remain recoverable until validation is complete. Recovery may
restore the previous path, retain a documented compatibility entry point, or
revert the bounded migration commit. Recovery must never discard participant
data, provenance, decision history, or accepted graph history.

## Maintenance

Update this register when a migration is proposed, changes status, gains a
dependency, or completes. The registries must be updated in the same commit
that changes a canonical artifact location.
