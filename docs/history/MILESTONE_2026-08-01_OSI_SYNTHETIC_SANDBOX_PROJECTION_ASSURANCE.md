---
artifact_id: milestone-osi-synthetic-sandbox-projection-001
title: OSI Synthetic Sandbox Projection Assurance
domain: osi
layer: research
authority: working
status: proposed
version: "0.1"
owner: osi-architecture
lifecycle_state: validation
last_reviewed: "2026-08-01"
review_cycle: milestone
---

# OSI Synthetic Sandbox Projection Assurance

## Development boundary

On 2026-08-01, the OSI synthetic organizational-evidence package completed a
guarded local graph-mechanics test against `OSI-Sandbox`. The test uses one
embedded synthetic organization → source → evidence → observation record. No
real organizational material is read or supplied by the importer.

## Controls exercised

- The invalid-package exercise removed the required negative boundary and was
  blocked before authentication or graph I/O.
- Offline preflight permits only `neo4j://127.0.0.1:7687`, `OSI-Sandbox`,
  `synthetic_only`, and `diagnostic_output: not_authorized`.
- A deliberate local action and Neo4j password were required before each
  synthetic graph write.
- Non-synthetic, incomplete, out-of-range, or unreviewed records are blocked
  by the projection assurance layer before a graph connection.
- Read-only post-import validation checks the exact run and global cardinality
  of the organization, source, evidence, observation, supporting relationship,
  and expected path.

## Controlled validation

Two explicit imports were validated. The second run was
`OSI-SANDBOX-RUN-F8FE36A9A794`; it confirmed one relationship for that run and
one global synthetic record of every expected node, relationship, and path.
`idempotent_structure` returned `true`.

| Check | Result |
|---|---:|
| Run relationship count | 1 |
| Synthetic organization node count | 1 |
| Synthetic source node count | 1 |
| Synthetic evidence node count | 1 |
| Synthetic observation node count | 1 |
| Synthetic observation relationship count | 1 |
| Expected organization-to-observation path count | 1 |
| Structural idempotency | `true` |

## Interpretation and limits

This proves a narrow, repeatable, guarded local graph path for one embedded
synthetic observation. It does not prove suitability for real organizational
data, diagnostics, analytics, scoring, causal claims, or use of the
`osi-reference` database as an import target. It does not instantiate or
validate Trust, Flow, Organizational Health, or state-transition constructs.

## Next governed boundary

The next OSI stage is not analytics. It is a broader synthetic projection
package with explicit schema, provenance, import audit, rollback, and
exception-handling requirements. Only after that boundary is validated should
the project consider a human-reviewed, uncertainty-preserving observation
preview.
