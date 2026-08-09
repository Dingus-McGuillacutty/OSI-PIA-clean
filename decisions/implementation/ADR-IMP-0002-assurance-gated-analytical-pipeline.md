---
artifact_id: adr-imp-0002
domain: implementation
layer: decision
authority: working
status: proposed
version: "1.0"
owner: assurance-maintainers
---

# ADR-IMP-0002: Adopt an Assurance-Gated Analytical Pipeline

## Status

Proposed

## Normalization date

2026-07-23

## Context

The platform describes assurance before ingestion, graph assurance, and
traceable analysis, but the original decision fragment did not define a
complete accepted gate contract or the status of its named artifacts.

## Proposed decision

Every material stage transition should require an assurance gate. Gates should
produce versioned, reviewable artifacts appropriate to their stage. Analytical
conclusions should remain versioned alongside supporting evidence. No public
report should bypass the applicable assurance process.

The proposed Evidence Assurance Report (EAR), Graph Integrity Report (GIR), and
Analytical Assurance Report (AAR) names remain provisional until their
contracts and ownership are defined.

## Consequences if accepted

- Pipeline stages expose explicit entry and exit criteria.
- Gate outcomes remain auditable and attributable.
- Reports preserve links to evidence, graph state, methods, and review.
- Gate failure or human-review requirements block unauthorized progression.
- Each assurance artifact requires a versioned contract.

## Open questions

- Which stages require blocking gates versus advisory review?
- Are EAR, GIR, and AAR separate contracts or profiles of one assurance report?
- Which authority may approve waivers?
- How are long-running analyses invalidated when upstream evidence changes?

## Related records

- [ADR-SHARED-0003](../shared/ADR-SHARED-0003-assurance-before-ingestion.md)
- [ADR-SHARED-0004](../shared/ADR-SHARED-0004-assurance-report-canonical-output.md)
- [ADR-SHARED-0006](../shared/ADR-SHARED-0006-graph-before-analytics.md)
