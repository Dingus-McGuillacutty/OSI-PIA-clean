---
artifact_id: decision-collection-001
domain: shared
layer: decision
authority: canonical
status: active
version: "1.0"
owner: repository-governance
---

# Architecture Decision Records

## Purpose

Architecture Decision Records preserve significant OSI-PIA decisions, their
context, alternatives, consequences, and relationships to more foundational
authority.

The canonical navigation and legacy-path mapping is
[`ADR_INDEX.md`](ADR_INDEX.md). The governed machine-readable inventory is the
[ADR Registry](../governance/registries/ADR_REGISTRY.md).

## Scope hierarchy

```text
decisions/
├── shared/          cross-domain governance, epistemology, assurance, and contracts
├── osi/             organizational-system meaning and architecture
├── pia/             participant evidence and assessment architecture
└── implementation/  technology and reference-implementation choices
```

OSI and PIA are peer decision scopes. Neither scope inherits decisions from the
other. Both may depend on accepted shared decisions. Implementation decisions
must not redefine shared, OSI, or PIA meaning.

## Identifier format

```text
ADR-{SCOPE}-{NNNN}-{descriptive-slug}.md
```

Allowed scopes are `SHARED`, `OSI`, `PIA`, and `IMP`. Numbers are sequential
within a scope and are never reused.

Hierarchy is expressed through `Depends On`, `Supersedes`, and related-record
links. It is not encoded by renumbering an accepted ADR.

## Status

- `Proposed`: under review and not binding;
- `Accepted`: current decision authority;
- `Superseded`: replaced by an identified ADR;
- `Deprecated`: retained but discouraged for new reliance;
- `Rejected`: considered and not adopted.

## Creating an ADR

1. Select the narrowest correct scope.
2. Reserve the next sequence in that scope.
3. Copy [`ADR-TEMPLATE.md`](ADR-TEMPLATE.md).
4. Declare artifact metadata and stable dependencies.
5. Update the ADR index and ADR registry in the same commit.
6. Record migration or compatibility effects where relevant.

An ADR explains why a durable choice exists. Architecture explains how the
system is structured, and commit history records implementation changes.
