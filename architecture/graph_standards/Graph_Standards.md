# Graph Standards

## Purpose

These standards govern OSI/PIA graph projections across domains. Specific node
properties, enums, import behavior, and acceptance criteria remain in their
versioned contracts.

## Authority

- Conceptual meaning comes from [`ontology/`](../../ontology/README.md).
- Database roles and projection boundaries come from the shared
  [`Graph Architecture`](../graph_ontology/Graph_Architecture.md).
- Namespace mappings conform to the
  [`Namespace Standard`](../../governance/policies/NAMESPACE_STANDARD.md).
- Projection maturity is recorded in the
  [`Graph Ontology Crosswalk`](../graph_ontology/graph_Ontology.md).
- Participant graph behavior comes from the
  [`Data and Graph Contract`](../../docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md)
  and
  [`Import Contract`](../../docs/contracts/OSI_PIA_Import_Contract_v0.1.md).
- Executable database mechanics belong in versioned schema or migration files
  under [`graph/`](../../graph/README.md).

## Graph contract

Every graph object must answer:

1. **What are you?** A canonical label or relationship type with defined
   semantics.
2. **Who are you?** A stable, non-semantic identity where the object requires
   independent identity.
3. **Why do you exist?** Traceable provenance, derivation, assertion basis, or
   operational purpose.

## Naming

- Node labels use singular `PascalCase`.
- Relationship types use directional `UPPER_SNAKE_CASE`.
- Properties use `snake_case`.
- Constraint and index names identify the label, property, and purpose.
- Synonyms do not become parallel labels. Add one canonical term and record
  aliases in ontology documentation.

## Identity

- Each canonical entity type has one contracted stable identity.
- IDs are immutable, non-semantic, and must not contain sensitive personal
  information.
- Human-readable names and titles are not identifiers.
- Imports use stable-key `MERGE` and must be rerunnable without duplication.
- Relationship assertions use a stable mapping identity when review,
  confidence, or lifecycle history must be preserved.

## Properties

- Every property must have an ontology, contract, derivation, validation, or
  operational purpose.
- Required values, types, enums, and null behavior belong in a versioned
  contract or dictionary.
- Unknown values remain unknown. Empty strings, invented defaults, and
  placeholder nodes must not conceal missing information.
- Operational properties such as import-run references must remain
  distinguishable from domain meaning.

## Relationships and assertions

- Define the allowed start label, end label, direction, and meaning.
- Preserve provenance relationships independently from analytical
  relationships.
- Assertions carry their basis, proposer, uncertainty, review status, and
  timestamps when required by contract.
- Rejected or superseded assertions remain auditable.
- A relationship name must not reverse or broaden its meaning between
  domains.

## Evidence and interpretation

Source-grounded Evidence is immutable except through explicit correction or
supersession. Indicators, capability mappings, assessments, hypotheses,
diagnoses, and recommendations remain separate graph objects or assertions.
No analytical process may overwrite the evidence from which it was derived.

## Temporal behavior

- Events, states, and transitions declare their time semantics.
- Partial, unknown, current, and bounded dates remain distinguishable.
- Changes that matter to reasoning or audit create history rather than
  silently replacing prior state.

## Schema and migrations

- Executable Cypher must be distinguishable from descriptive catalogues.
- Schema changes are idempotent where Neo4j supports `IF NOT EXISTS`.
- One migration represents one coherent, reviewable change.
- Breaking identity, meaning, or direction changes require an ADR,
  compatibility boundary, migration, rollback or recovery guidance, and
  updated validation.
- A graph object is not described as implemented until schema, import,
  validation, and documentation agree.

## Validation checklist

Before promotion or release, verify:

- stable identities are unique;
- required endpoints exist;
- provenance chains are complete;
- relationship direction and cardinality match the contract;
- assertions expose required review and uncertainty metadata;
- imports are idempotent;
- no unexpected orphan or placeholder nodes exist;
- privacy and consent boundaries are preserved;
- post-import validation passes;
- the ontology crosswalk and changelog are current.

## Versioning

Use the contract compatibility rules:

- patch for non-breaking clarification;
- minor for additive compatible objects or relationships;
- major for breaking identity, meaning, field, node, or relationship changes.

Graph implementation versions should be traceable from imported objects and
assurance reports when practical.
