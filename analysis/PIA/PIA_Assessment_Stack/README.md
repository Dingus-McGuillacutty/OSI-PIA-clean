# PIA Assessment Stack

This migration adds a versionable analytical layer to the implemented PIA graph without altering the existing evidence chain.

## Existing graph preserved

`Participant → Experience ← Evidence ← Source`

`Evidence → Capability → Pattern`

## New assessment layer

- `(:Participant)-[:HAS_ASSESSMENT]->(:Assessment)`
- `(:Assessment)-[:EVALUATES]->(:Pattern)`
- `(:Assessment)-[:USES_CAPABILITY]->(:Capability)`
- `(:Assessment)-[:BASED_ON]->(:Evidence)`
- `(:Assessment)-[:SUPPORTS_IDENTITY]->(:IdentityHypothesis)`

Assessment records analyst interpretation while evidence, capability, and pattern nodes remain independently inspectable.

## Assessment properties

Required for Inspector integrity checks:

- `assessment_id`
- `created_at`
- `analyst`
- `method_version`
- `status`

Recommended:

- `confidence`
- `summary`
- `notes`
- `namespace`
- `updated_at`

## Run order

1. Back up the database.
2. Run `00_assessment_schema.cypher`.
3. Run `01_create_assessment_template.cypher` after replacing parameters.
4. Use `02_link_assessment_to_graph.cypher` to connect actual Pattern, Capability, Evidence, and IdentityHypothesis IDs.
5. Run `04_assessment_integrity.cypher`.
6. Run `05_assessment_trace.cypher` to inspect the complete analytical record.

Neo4j Browser treats each semicolon-delimited statement separately. The linking file contains four independent sections, so run only the sections you intend to use.

## Design rule

An Assessment may interpret graph objects but must not overwrite the underlying evidence. A later method version creates a new Assessment rather than rewriting an old one.
