# Graph Migrations

## Purpose

This directory contains ordered, executable Neo4j changes that have a defined
target database, compatibility boundary, verification query, and recovery
guidance.

Migrations implement an approved graph projection. They do not create
conceptual authority by themselves.

## Application

Apply migrations in numeric order to the target database named in each file.
Each migration must be reviewed before production use and backed up according
to the operating environment's recovery policy.

| Migration | Target | Change | Validation |
|---|---|---|---|
| [`001_osi_reference_meta_ontology.cypher`](001_osi_reference_meta_ontology.cypher) | `osi-reference` | Adds the working ontology registry and knowledge-governance vocabulary | [`validate_osi_reference_meta_ontology_v0.1.cypher`](../cypher/validation/validate_osi_reference_meta_ontology_v0.1.cypher) |
| [`002_pia_reference_meta_ontology.cypher`](002_pia_reference_meta_ontology.cypher) | `pia-reference` | Adds a separate PIA registry using the shared knowledge-governance vocabulary | [`validate_pia_reference_meta_ontology_v0.1.cypher`](../cypher/validation/validate_pia_reference_meta_ontology_v0.1.cypher) |
| [`003_osi_reference_architecture_congruence.cypher`](003_osi_reference_architecture_congruence.cypher) | `osi-reference` | Aligns specialization labels, provenance, analytical assertion metadata, bounded core declarations, and the shared architecture profile | [`validate_osi_reference_architecture_congruence_v0.2.cypher`](../cypher/validation/validate_osi_reference_architecture_congruence_v0.2.cypher) |
| [`004_pia_reference_architecture_congruence.cypher`](004_pia_reference_architecture_congruence.cypher) | `pia-reference` | Aligns contract properties, explicit unknowns, assertion metadata, relationship meanings, confidence, bounded core declarations, and the shared architecture profile | [`validate_pia_reference_architecture_congruence_v0.2.cypher`](../cypher/validation/validate_pia_reference_architecture_congruence_v0.2.cypher) |
| [`005_pia_behavioral_capability_profile.cypher`](005_pia_behavioral_capability_profile.cypher) | `pia-reference` | Adds the proposed capability-evidence vocabulary, eight report-level patterns, educational preparation boundary, and governed capability-to-pattern groupings without participant data | [`validate_pia_capability_evidence_profile_v0.2.cypher`](../cypher/validation/validate_pia_capability_evidence_profile_v0.2.cypher) |

## Guarantees

- Migration files are additive unless their header explicitly says otherwise.
- Stable-key `MERGE` and `IF NOT EXISTS` are used where Neo4j supports them.
- A successful rerun against an unchanged graph does not duplicate nodes,
  relationships, constraints, or indexes.
- Domain data is not relabeled or rewritten by registry migrations.
- Congruence migrations may add specialization labels, canonical property
  aliases, and reviewed relationship-type corrections exactly as declared in
  their headers. Legacy properties are retained.

## Recovery

Migration `001` is isolated by the `managed_by` value
`001_osi_reference_meta_ontology`. If recovery is required, restore the
pre-migration database backup. Selective removal of registry objects is
possible using that marker, but it should be reviewed and performed as a
separate recovery change rather than embedded in the forward migration.

Migration `002` uses the corresponding marker
`002_pia_reference_meta_ontology` in the `pia-reference` database and follows
the same recovery boundary.

Migration `003` is additive. Its aligned objects carry
`alignment_version = '0.2.0'`, `aligned_by`, or the migration's `managed_by`
marker.

Migration `004` corrects two scoped relationship types. The replacement
relationships retain `migrated_from_relationship_type` and the complete legacy
property map. Restore the pre-migration backup for full recovery, or implement
a reviewed reverse migration from those markers.

Migration `005` is additive and marks its vocabulary through
`profile_managed_by` and its groupings through `grouping_profile`. It reuses
exact Capability and Pattern names when present, assigns separate profile IDs,
and does not overwrite a reused node's prior definition, status, identity, or
ownership. It creates no participant data. Restore the pre-migration backup
for full recovery; selective removal requires a reviewed reverse migration
because a reused node may predate the profile.
