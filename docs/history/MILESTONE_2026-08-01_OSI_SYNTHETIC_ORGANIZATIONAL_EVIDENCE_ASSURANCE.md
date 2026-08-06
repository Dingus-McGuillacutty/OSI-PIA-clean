---
artifact_id: milestone-osi-organizational-evidence-assurance-001
title: OSI Synthetic Organizational-Evidence Assurance
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

# OSI Synthetic Organizational-Evidence Assurance

## Development boundary

On 2026-08-01, OSI gained a reproducible, participant-free synthetic package
and assurance component for the path from organizational structure and source
provenance to a bounded observation candidate.

The package validates synthetic organization, organizational unit, position,
collection, source, evidence, and observation-candidate records. Its tests
exercise the valid path and reject broken provenance, non-synthetic identity,
and missing negative boundaries; they also hold an unreviewed candidate for
human review.

## What this demonstrates

- organization-scoped provenance can be represented and checked before graph
  work;
- observation candidates retain a confidence basis, explicit limit, and
  accountable-review gate; and
- the synthetic package can be assured without participant data, a Neo4j
  connection, or a graph write.

## What this does not demonstrate

This milestone does not validate an OSI graph import, real organizational data
handling, organizational diagnostics, analytics, scoring, causal claims, or
the planned Trust, Flow, Organizational Health, or state-transition constructs.
It does not authorize use with a real organization.

## Next governed boundary

The next OSI increment is a synthetic-only sandbox projection contract,
preflight, importer, and post-write/idempotency validator. That work must keep
the observation's source, scope, confidence basis, and negative boundary
intact and may not silently promote it into a diagnosis.
