---
artifact_id: repo-conventions-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.2"
owner: repository-governance
---

# Repository Conventions

## Purpose

These conventions provide stable rules for human and machine readers of the
OSI-PIA repository. They govern identifiers, paths, metadata, authority,
status, references, and reviewable change.

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` indicate requirement strength.
Existing files that do not yet conform are compatibility cases governed by
the [Repository Migration Plan](Repository_Migration_Plan.md), not permission
to create more exceptions.

## Domain and namespace

Every governed artifact MUST declare exactly one domain:

```text
shared
osi
pia
implementation
test
```

Machine-readable ontology identifiers SHOULD use the same lowercase namespace:

```text
shared:evidence
osi:organization
pia:assessment
implementation:csv-assurance-engine
test:participant-package-valid
```

OSI and PIA identifiers MUST remain distinguishable. A shared identifier MUST
represent genuinely cross-domain meaning and MUST NOT be used to make one
domain's interpretation binding on the other.

The canonical
[Namespace Standard](policies/NAMESPACE_STANDARD.md) governs how these values
are represented in ontology IDs, graph projections, manifests, contracts, and
outputs. Repository conventions define the common metadata field; the
namespace standard defines its cross-layer use.

## Artifact metadata

New governed Markdown artifacts MUST begin with:

```yaml
---
artifact_id: stable-identifier
domain: shared
layer: governance
authority: canonical
status: active
version: "1.0"
owner: responsible-role
---
```

The required fields are:

| Field | Rule |
|---|---|
| `artifact_id` | Stable, unique, lowercase, and independent of the file path |
| `domain` | One value from the domain vocabulary |
| `layer` | Architectural responsibility, such as `governance`, `ontology`, `graph`, or `software` |
| `authority` | `canonical`, `supporting`, `working`, or `historical` |
| `status` | `active`, `proposed`, `review-required`, `deprecated`, `superseded`, or `retired` |
| `version` | Quoted semantic or document version; use `"unversioned"` only for compatibility records |
| `owner` | Stewardship role, not necessarily a person's name |

`lifecycle_state` MAY be added when the artifact is being managed through the
project [Knowledge Lifecycle](../foundation/KNOWLEDGE_LIFECYCLE.md).
Lifecycle state and operational status MUST NOT be treated as the same field.

`last_reviewed` and `review_cycle` MAY be added when an artifact has a
recurring review obligation:

```yaml
last_reviewed: "2026-07-24"
review_cycle: annual
```

`last_reviewed` uses an ISO 8601 calendar date (`YYYY-MM-DD`). Controlled
review cycles are `annual`, `semiannual`, `quarterly`, `milestone`, and
`event-driven`. When `review_cycle` is present, `last_reviewed` is required.
The next review is measured from the last completed review unless a governing
artifact defines an earlier event-based trigger.

Executable artifacts SHOULD carry the equivalent metadata in the native
comment or manifest format.

## Authority

- `canonical`: the authoritative repository reference for its declared scope;
- `supporting`: a valid explanation, view, or implementation that defers to a
  canonical artifact;
- `working`: exploratory or incomplete material that is not authoritative;
- `historical`: preserved to explain prior state and not used for new work.

Only one artifact SHOULD be canonical for the same scope and version. If two
artifacts overlap, the registry MUST identify the authority boundary or mark
the conflict `review-required`.

## Status

- `active`: current and available for use;
- `proposed`: awaiting the review required for adoption;
- `review-required`: usable only after a documented ambiguity is resolved;
- `deprecated`: retained but discouraged for new use;
- `superseded`: replaced by an identified artifact;
- `retired`: outside active project use.

Status does not imply truth, validation, or canonical authority.

## Names and paths

- New directory names MUST use lowercase `kebab-case`.
- New Markdown filenames SHOULD use descriptive `Pascal_Case.md` only where
  the surrounding canonical collection already uses that convention;
  otherwise use lowercase `kebab-case.md`.
- Python names use `snake_case.py`.
- Cypher names use a numeric sequence and `snake_case.cypher` when execution
  order matters.
- YAML and CSV field names use `snake_case`.
- Paths MUST NOT be renamed only for style. Renames require a migration record,
  reference update, and case-sensitive validation.

Existing mixed-case paths such as `analysis/PIA/` remain compatibility paths
until their controlled migration.

## Stable identifiers

### Architecture Decision Records

New ADR identifiers use:

```text
ADR-{SCOPE}-{NNNN}-{descriptive-slug}.md
```

Allowed scopes are:

```text
SHARED
OSI
PIA
IMP
```

Numbers are sequential within a scope. They are never reused. Hierarchy is
represented through dependencies and supersession links, not by changing an
accepted ADR's identifier.

Existing ADR identifiers remain traceable through the ADR registry until they
are migrated.

### Connectors

Connector directories use:

```text
connector-{NNN}-{descriptive-name}/
```

The numeric ID is stable and the descriptive suffix is readable. The manifest
MUST repeat the stable ID and explicitly declare its domain scope, contract
version, owner, and status.

### Other artifacts

Other artifact IDs use a registry-specific prefix followed by a stable
descriptive identifier or sequence. Renaming a file MUST NOT change its
`artifact_id`.

## Canonical locations and duplication

- Each governed artifact MUST have one canonical location.
- Registries point to artifacts; they do not repeat artifact content.
- A compatibility copy MUST identify its canonical source.
- Generated files MUST identify their generator and MUST NOT be edited as an
  independent authority.
- Apparent duplicates MUST be compared before either copy is removed.
- Private data, credentials, live databases, and generated secrets MUST NOT be
  committed.

## References

- Repository documents SHOULD use relative Markdown links.
- Dependencies in registries MUST use stable artifact IDs.
- A path change MUST update inbound references in the same migration.
- A superseded artifact MUST identify its replacement.
- Cross-domain references MUST state why the dependency is permitted.

## Commit and migration discipline

- One commit SHOULD represent one coherent architectural change.
- Governance and registry changes SHOULD precede file moves.
- Mechanical moves SHOULD be separated from semantic rewrites when practical.
- A migration MUST define scope, dependencies, validation, and recovery.
- Tests and documentation affected by a move MUST be updated in the same
  migration.
- Large reorganizations MUST be decomposed into reversible phases.

## Review checklist

Before accepting a governed artifact or repository migration, verify:

- domain and layer are explicit;
- the artifact ID is unique and stable;
- authority and status are not overstated;
- the canonical location is unambiguous;
- dependencies use governed identifiers;
- OSI and PIA boundaries remain intact;
- provenance, privacy, and consent are preserved;
- links, tests, and executable references still resolve;
- review metadata is current when a recurring review obligation applies;
- the appropriate registry and migration record are updated.


