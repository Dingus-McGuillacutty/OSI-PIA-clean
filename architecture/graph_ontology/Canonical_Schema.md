# Canonical Graph Schema References

This file preserves the original architecture location while directing readers
to the current authorities. It does not duplicate ontology definitions,
contracts, or executable schema.

## Database architecture

- [`Graph_Architecture.md`](Graph_Architecture.md) defines the shared graph
  layers and the separate reference-database roles.
- [`OSI_Reference_Database.md`](OSI_Reference_Database.md) defines the
  `osi-reference` acceptance boundary.
- [`PIA_Reference_Database.md`](PIA_Reference_Database.md) defines the
  `pia-reference` acceptance boundary.

## Conceptual authority

- [`ontology/README.md`](../../ontology/README.md) defines the ontology
  boundary.
- The
  [`Ontology Registry`](../../governance/registries/ONTOLOGY_REGISTRY.md)
  is the canonical inventory of namespaced ontology identities and status.
- [`ontology/CORE CONCEPTS.md`](../../ontology/CORE%20CONCEPTS.md) defines
  current core concepts.
- [`ontology/META_ONTOLOGY.md`](../../ontology/META_ONTOLOGY.md) defines the
  working ontology meta-model.

## Graph projection

- [`graph_Ontology.md`](graph_Ontology.md) maps approved concepts and contracts
  to current, experimental, and planned graph objects.
- [`Graph_Standards.md`](../graph_standards/Graph_Standards.md) defines
  cross-cutting graph engineering rules.
- [`graph/schema/README.md`](../../graph/schema/README.md) identifies the
  executable and descriptive contents of the current schema directory.

## Contract authority

- [`OSI_PIA_Data_Graph_Contract_v0.1.md`](../../docs/contracts/OSI_PIA_Data_Graph_Contract_v0.1.md)
  defines participant records and their graph mappings.
- [`OSI_PIA_Import_Contract_v0.1.md`](../../docs/contracts/OSI_PIA_Import_Contract_v0.1.md)
  defines controlled graph writes.

The ontology defines meaning. Contracts define accepted representations.
Versioned schema and migrations define executable mechanics. No one layer may
silently redefine another.
