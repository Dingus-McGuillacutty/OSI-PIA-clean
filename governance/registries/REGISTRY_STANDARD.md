---
artifact_id: standard-registry-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.1"
owner: repository-governance
---

# Registry Standard

## Purpose

This standard defines what a repository registry is, the fields every registry
uses, and the rules for creating and maintaining entries.

## Registry role

A registry is a governed index. It:

- assigns a stable inventory identity;
- points to the canonical artifact;
- records domain, layer, authority, status, owner, and version;
- exposes dependencies by stable ID;
- makes duplication and unresolved authority visible.

A registry does not:

- reproduce the indexed artifact;
- silently promote working material;
- make implementation authoritative over ontology or contracts;
- resolve conflicting artifacts without review;
- replace Git history or an ADR.

## Required table schema

Every registry MUST use these columns in this order:

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `example-001` | Human-readable name | `shared` | `architecture` | `canonical` | `active` | `architecture` | `1.0` | Relative Markdown link | Stable artifact ID or `—` |

Individual registries MAY add notes below the common table. They MUST NOT alter
the field names or use private variants of the controlled vocabularies.

## Governed item indexes

A type registry MAY append a secondary item index when the registered artifact
contains governed items that need stable identity, such as ontology concepts
or relationship definitions.

The item index:

- is clearly separated from the common artifact table;
- declares its own fixed field order and controlled vocabularies;
- uses stable namespaced item IDs;
- points to definition authority rather than repeating definitions;
- keeps conceptual status separate from implementation status;
- does not cause one item to appear as multiple canonical artifact rows.

Registry-specific item schemas are governed by the registry that declares
them. Changing an item schema requires a registry version change and
validation update.

## Field rules

### Artifact ID

The ID is stable, unique across the repository, lowercase, and independent of
the current path. It SHOULD begin with a type prefix such as `adr-`,
`architecture-`, `component-`, `connector-`, `contract-`, `graph-`,
`ontology-`, `principle-`, `publication-`, `research-`, `software-`, or
`standard-`.

### Name

The name is concise and human-readable. It is not an alternate identifier.

### Domain

Use one value:

```text
shared
osi
pia
implementation
test
```

### Layer

Use the architectural responsibility of the artifact, not merely its current
folder. Common values include:

```text
governance
decision
architecture
foundation
principle
ontology
contract
graph
analysis
connector
component
software
research
publication
standard
test
```

### Authority

Use `canonical`, `supporting`, `working`, or `historical` as defined by the
[Repository Conventions](../Repository_Conventions.md).

### Status

Use `active`, `proposed`, `review-required`, `deprecated`, `superseded`, or
`retired`.

### Owner

The owner is a stewardship role, not necessarily a named person. Examples are
`repository-governance`, `osi-architecture`, `pia-ontology`,
`graph-maintainers`, or `assurance-maintainers`.

### Version

Use the artifact's declared version. Use `unversioned` only for a compatibility
artifact that has not yet gained explicit version metadata. Do not infer a
version from a commit hash or filename when the artifact states none.

### Canonical Location

Use a relative Markdown link from the registry to the artifact. A registry may
index a governed directory when the directory, manifest, and entry document
together form one artifact.

### Depends On

Use stable artifact IDs, separated by `<br>` when more than one dependency is
required. Use `—` when no governed dependency is known. Do not place file paths
in this field.

## Entry rules

- One row represents one governed artifact.
- One artifact ID appears in one primary registry.
- A registry may describe a relationship to another artifact without adding a
  duplicate row.
- Two entries MUST NOT claim canonical authority for the same scope and version.
- Unresolved collisions are `review-required`.
- Historical and compatibility entries retain their original identity and
  point to their replacement when known.
- Live databases, private data, secrets, and generated runtime state are not
  registry artifacts. Their reproducible specifications may be registered.

## Change protocol

Add or update a registry row in the same commit when:

- a governed artifact is created;
- its canonical path changes;
- its status, authority, owner, or version changes;
- a dependency is added or removed;
- it is superseded, deprecated, or retired.

A material schema change to this standard requires repository-governance
review. A bulk registry rewrite MUST be separated from unrelated semantic or
path migrations.

## Review

Registry review verifies:

- IDs are unique;
- locations resolve;
- metadata and row values agree;
- dependencies resolve to registered IDs or are explicitly pending;
- OSI and PIA domain assignments are not ambiguous;
- canonical authority is not duplicated;
- `review-required` items are represented in the migration plan.

Registries SHOULD eventually gain automated validation. Until then, link,
schema, duplicate-ID, and dependency checks form the minimum review baseline.
