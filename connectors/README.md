---
artifact_id: connector-collection-001
domain: shared
layer: connector
authority: canonical
status: active
version: "1.1"
owner: connector-maintainers
---

# Connectors

## Purpose

Connectors translate external sources into governed OSI-PIA records while
preserving provenance, privacy, domain scope, and contract boundaries.

Every connector conforms to the
[Connector Standard](Connector_Standard.md) and has one numbered canonical
directory.

## Registered connectors

| Connector | Domain scope | Status | Purpose |
|---|---|---|---|
| [`connector-001-linkedin`](connector-001-linkedin/) | `pia` | Active | Normalize a participant-authorized LinkedIn archive into reviewable PIA evidence records |
| [`connector-002-credential-engine`](connector-002-credential-engine/) | `pia` | Proposed | Search public CTDL credential records through the Phase 3B minimization and Phase 3A review boundaries |

The authoritative machine-readable inventory is the
[Connector Registry](../governance/registries/CONNECTOR_REGISTRY.md).

## Boundary

A connector is an adapter, not an ontology authority or analytical engine. It
may normalize source material into a contracted form, but it must not silently
verify claims, infer identity, assign capability, or create OSI conclusions.

Private source archives and generated participant records remain outside the
public repository.
