---
artifact_id: contract-osi-organizational-evidence-001
title: OSI Organizational Evidence Package Contract v0.1
domain: osi
layer: contract
authority: working
status: proposed
version: "0.1"
owner: osi-architecture
lifecycle_state: formulation
---

# OSI Organizational Evidence Package Contract v0.1

## Purpose

This working contract defines a participant-free, synthetic-first package for
testing the OSI path from organizational source material to a bounded,
reviewable observation candidate. It does not authorize organizational
surveillance, graph writes, diagnostic conclusions, or instantiation of
planned constructs such as Trust, Flow, or Organizational Health.

## Evidence path

```text
Organization → OrganizationalUnit / Position
Organization → Collection → Source → Evidence → ObservationCandidate
```

An `ObservationCandidate` is not a diagnosis. It records a limited statement
that a reviewer may accept, reject, or revise while preserving its evidence,
confidence basis, and negative boundary.

## Required files

| File | Stable ID | Required purpose |
|---|---|---|
| `organization.csv` | `organization_id` | Synthetic organization scope |
| `organizational_unit.csv` | `organizational_unit_id` | Bounded organizational unit |
| `position.csv` | `position_id` | Structural role position; no person record required |
| `collection.csv` | `collection_id` | Provenance collection and confidentiality boundary |
| `source.csv` | `source_id` | Source origin within a collection |
| `evidence.csv` | `evidence_id` | Faithful source-grounded record |
| `observation_candidate.csv` | `observation_id` | Bounded analytical candidate linked to one Evidence record |

## Required controls

- all fixture identifiers use the `OSI-SYN-*` namespace;
- every source, evidence, and structure record resolves to one organization;
- every evidence record resolves to one source;
- every observation candidate resolves to one evidence record;
- confidence is within `0` through `1` and has an explicit basis;
- every observation candidate states what it does **not** establish;
- accepted observation candidates identify an accountable reviewer; and
- proposed or review-required candidates cannot be represented as diagnostic
  output without later accountable review.

## Current assurance boundary

The associated validator performs no Neo4j connection or write. Its synthetic
fixture proves package identity, foreign-key integrity, provenance continuity,
confidence bounds, review gate, and negative-boundary enforcement. A later
import contract and sandbox stage must establish target authorization,
transactional behavior, import audit, post-write validation, and idempotency.
