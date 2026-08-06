---
artifact_id: standard-namespace-001
domain: shared
layer: standard
authority: canonical
status: active
version: "1.0"
owner: repository-governance
---

# Namespace Standard

## Purpose

This standard makes domain identity explicit and consistent across repository
metadata, ontology identifiers, graph projections, manifests, contracts, and
outputs. It prevents similarly named OSI and PIA concepts from being treated
as equivalent merely because they share a label.

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` indicate requirement strength.

## Namespace vocabulary

Every governed artifact belongs to exactly one repository domain and uses the
corresponding primary namespace:

| Namespace | Scope |
|---|---|
| `shared` | Cross-domain epistemology, governance, assurance, contracts, or infrastructure whose meaning is genuinely common |
| `osi` | Organizational-system concepts, evidence, analyses, graph projections, and outputs |
| `pia` | Participant evidence, capabilities, bounded assessments, graph projections, and outputs |
| `implementation` | Technical machinery that does not create OSI or PIA meaning |
| `test` | Fixtures and verification behavior with no production authority |

Combined namespace values such as `osi-pia`, `common`, or `global` MUST NOT be
introduced. An artifact used by both domains is `shared` only when its meaning
is actually shared. Otherwise, it retains its domain and is connected through
an explicit mapping or contract.

## Representation rules

### Governed artifacts

Markdown frontmatter uses the `domain` field defined by the
[Repository Conventions](../Repository_Conventions.md). The artifact ID
remains stable and registry-specific; it does not replace domain metadata.

```yaml
artifact_id: ontology-osi-core-001
domain: osi
```

Executable files SHOULD carry equivalent metadata in their native comment,
manifest, or enclosing registered package.

### Ontology items

Concept and relationship identities use:

```text
{namespace}:{lower_snake_case_name}
```

Examples:

```text
shared:evidence
osi:organization
pia:assessment
implementation:graph_migration
test:participant_package_valid
```

The namespaced ontology ID is the semantic identity. A human-readable name or
graph label is only a representation of that identity.

### Graph projections

Graph labels use `PascalCase`; relationship types use
`UPPER_SNAKE_CASE`. Every governed label or relationship type MUST resolve to
one namespaced identity in the
[Ontology Registry](../registries/ONTOLOGY_REGISTRY.md) or be marked
experimental and unpromoted in the graph crosswalk.

Examples:

| Ontology ID | Graph representation |
|---|---|
| `osi:organization` | `Organization` |
| `pia:assessment` | `Assessment` |
| `pia:uses_capability` | `USES_CAPABILITY` |

`osi-reference` and `pia-reference` are database or deployment identifiers,
not ontology namespaces. Graph registry IDs such as
`concept:osi-reference:Organization` identify implementation records; they do
not replace the canonical ontology ID.

Operational nodes and relationships MUST be attributable to a namespace
through the record itself or its enclosing package, import run, contract, or
database boundary. A physical database boundary alone MUST NOT be used to
justify an otherwise ambiguous cross-domain record.

### Manifests and configuration

YAML manifests use lowercase namespace values:

```yaml
domain: implementation
namespace: implementation
```

A connector or package that is authorized for more than one domain declares a
`domain_scope` list while retaining one primary `namespace`. The declared
namespace describes semantic output; it is not inferred from the executing
user, source system, file path, or destination database.

### Contracts and records

Contracts MUST state the namespace of the identities they define or carry.
When a record does not repeat a namespace field, the enclosing contract and
package manifest MUST establish it unambiguously.

Fields that contain ontology identities use full namespaced values. Fields
that contain graph labels or relationship types MUST name the governing
crosswalk or schema version.

### Exports and reports

Generated outputs retain:

- producing artifact or component identity and version;
- primary namespace and domain scope;
- source contract and schema version;
- provenance and applicable consent boundary;
- transformation or analysis identity;
- assurance disposition and review status.

OSI and PIA outputs MUST remain separately attributable. A combined report or
export requires an explicit cross-domain mapping and MUST NOT erase the
namespace of source assertions.

## Cross-domain mappings

A mapping between two domains is a governed artifact or contracted record. It
declares:

1. stable mapping identity and version;
2. source and target namespaced identities;
3. permitted purpose and prohibited interpretation;
4. direction and whether the mapping is exact, narrower, broader, or
   contextual;
5. provenance-preservation requirements;
6. assurance and human-review requirements;
7. owner, status, and retirement or replacement behavior.

A mapping relates concepts; it does not merge them. Similar names, shared
graph labels, or technical co-location do not establish semantic equivalence.

## Validation

Namespace validation checks that:

- every governed artifact declares one allowed domain;
- ontology item IDs use an allowed lowercase prefix and `lower_snake_case`;
- graph representations resolve to registered ontology identities;
- manifests and contracts declare unambiguous namespace scope;
- cross-domain dependencies have an explicit purpose and mapping authority;
- test and implementation identities are not promoted into domain ontology;
- outputs preserve source namespace and provenance.

New work MUST conform. Existing compatibility material is corrected through a
bounded migration rather than silently reinterpreted.

## Governing decisions

- [ADR-SHARED-0001: Repository Domain Boundaries](../../decisions/shared/ADR-SHARED-0001-repository-domain-boundaries.md)
- [ADR-SHARED-0002: Shared Epistemology, Distinct Domain Ontologies](../../decisions/shared/ADR-SHARED-0002-shared-epistemology-distinct-domain-ontologies.md)
