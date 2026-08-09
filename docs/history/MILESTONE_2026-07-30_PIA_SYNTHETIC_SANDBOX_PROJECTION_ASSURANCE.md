# Milestone: PIA Synthetic Sandbox Projection Assurance

Date: 2026-07-30

Status: Implemented and validated working checkpoint

Authority: Working/proposed; synthetic-only sandbox boundary remains in force

Commit: To be assigned at the next intentional commit boundary

Builds on: [PIA Mapping-to-Output Preview](MILESTONE_2026-07-29_PIA_MAPPING_TO_OUTPUT_PREVIEW.md)

## Overview

This checkpoint validates the first intentionally narrow Neo4j projection path:
one embedded synthetic evidence-to-capability assertion written only to the
local `PIA-Sandbox` database. It establishes technical behavior of a guarded
sandbox import; it does not authorize projection of protected participant
material.

## Controls exercised

- an offline projection-assurance package requires an exact accepted-mapping
  selection, valid confidence, `local_sandbox`, `PIA-Sandbox`, and `dry_run`;
- preflight permits only the declared local URI and `PIA-Sandbox` target;
- the importer accepts no supplied participant payload and embeds one clearly
  synthetic row only;
- an explicit `--apply-synthetic` action and local Neo4j password are required
  before a write;
- malformed, non-synthetic, duplicate, incomplete, or out-of-range package
  records are rejected before authentication or graph I/O; and
- read-only post-import validation verifies the run payload and the global
  cardinality of the evidence node, capability node, mapping relationship, and
  expected path.

## Controlled validation

The synthetic import was executed twice against `PIA-Sandbox`. The second run
was `PIA-SANDBOX-RUN-DB739AAD9589`. Its read-only validation returned:

| Check | Result |
|---|---:|
| Run relationship count | 1 |
| Synthetic evidence node count | 1 |
| Synthetic capability node count | 1 |
| Synthetic mapping relationship count | 1 |
| Expected evidence-to-capability path count | 1 |
| Structural idempotency | `true` |

The deliberate invalid-package exercise also passed: an out-of-range
confidence was blocked before authentication and reported `graph_write:
not_performed`. The focused protected-intake regression suite passed with 28
tests.

## Interpretation and limits

This proves that the bounded synthetic package can be imported, read back, and
re-imported without duplicate structural records in the local sandbox. It does
not prove production security, participant-data suitability, graph semantics
beyond the one synthetic assertion, report publication, or independent review.
The sandbox retains only the latest run identifier on the synthetic
relationship; it is a technical test marker, not a durable production import
audit model.

## Remaining gates

- a governed participant-minimized projection contract and approved target
  authorization;
- durable graph import audit, rollback, and exception handling;
- participant projection deletion and retention semantics;
- broader graph schema, provenance, and authorization assurance; and
- controlled-pilot privacy, consent, security, operational, and independent
  review before any real-participant processing or projection.
