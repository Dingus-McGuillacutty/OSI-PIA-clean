# PIA Live Synthetic Sandbox Validation

Date: 2026-08-12  
Status: Validated working checkpoint  
Run: `PIA-SANDBOX-RUN-B58CF1C470F3`

## Controlled result

The existing PIA synthetic importer wrote one synthetic evidence-to-capability
mapping to the local `PIA-Sandbox`. Read-only validation then returned:

| Check | Result |
| --- | ---: |
| Status | `pass` |
| Relationships | 1 |
| Evidence nodes | 1 |
| Capability nodes | 1 |
| Mapping relationships | 1 |
| Expected paths | 1 |
| Properties valid | `true` |
| Idempotent structure | `true` |
| Validator graph write | `not_performed` |

## Evidence and limits

The validated path is `PIA-SYN-EVD-001` → `SUPPORTS` →
`CAP-PIA-HANDOFF-MANAGEMENT`. The package is synthetic-only. This test
demonstrates guarded graph mechanics and traceable bounded representation; it
does not establish competence, performance, causality, or production
participant-data readiness.

## Walkthrough assets

The paired graph and table screenshots are included in the [Live Sandbox Graph
Tour](../evidence/visualizations/LIVE_SANDBOX_GRAPH_TOUR.md).
