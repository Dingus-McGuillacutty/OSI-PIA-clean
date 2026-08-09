---
artifact_id: contract-osi-synthetic-sandbox-projection-001
title: OSI Synthetic Sandbox Projection Contract v0.1
domain: osi
layer: contract
authority: working
status: proposed
version: "0.1"
owner: osi-architecture
lifecycle_state: formulation
---

# OSI Synthetic Sandbox Projection Contract v0.1

## Purpose

This contract governs the narrow synthetic-only path from an accepted OSI
organizational observation candidate to a local Neo4j sandbox. It verifies
graph mechanics without using real organizational material or authorizing an
organizational diagnostic.

## Authorized target

| Field | Required value |
|---|---|
| Environment | `local_sandbox` |
| URI | `neo4j://127.0.0.1:7687` |
| Database | `OSI-Sandbox` |
| Projection mode | `synthetic_only` |
| Diagnostic output | `not_authorized` |

`osi-reference` is a governed reference database and is never an import
target for this contract.

## Required record fields

Each projection record contains synthetic organization, source, evidence, and
observation identities; observation text; confidence and its basis; a negative
boundary; accepted review status; and an accountable reviewer identity.

All identities use the `OSI-SYN-*` namespace. The package is rejected before
authentication or graph I/O when any identity is non-synthetic, a required
field is empty, confidence is outside `0` through `1`, the observation lacks a
negative boundary, or review is not `accepted`.

## Graph shape

```text
(Organization)-[:HAS_SOURCE]->(Source)-[:CONTAINS_EVIDENCE]->(Evidence)
  -[:SUPPORTS_OBSERVATION]->(ObservationCandidate)
```

The `SUPPORTS_OBSERVATION` relationship retains the bounded observation text,
confidence, confidence basis, negative boundary, review state, reviewer,
synthetic marker, and import-run marker.

## Explicit exclusions

This contract does not permit a supplied data payload, external organizational
data, writes to a reference graph, diagnostic findings, scores, causal claims,
or the use of Trust, Flow, Organizational Health, or state-transition
constructs. It is not authorization to use the tooling with a real
organization.

## Required post-write assurance

After a deliberate import, a read-only validator must confirm the run's exact
record and globally confirm exactly one Organization, Source, Evidence,
ObservationCandidate, observation relationship, and expected four-node path.
Repeating the import must not create a duplicate structure.

## Import audit, rollback, and exceptions

Each deliberate import creates one synthetic `OSIImportRun` record with a
`started`, `completed`, or `failed` status, record count, target database, and
timestamps. A completed run is not considered validated unless its audit
record and graph shape both pass read-only checks.

Rollback accepts only a full `OSI-SANDBOX-RUN-*` identifier and only removes
observation relationships tagged with that exact run. Unknown, non-synthetic,
or superseded run identifiers produce a controlled exception result; they do
not trigger a broad deletion. Import exceptions report their type and status,
and failed runs are recorded when the database connection is available.
