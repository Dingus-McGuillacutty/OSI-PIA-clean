---
artifact_id: registry-publication-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.6"
owner: repository-governance
---

# Publication Registry

## Scope

This registry indexes governed publications and examples. Publication
conformance rules are registered as `standard-publication-001` in the Standard
Registry.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `publication-pia-anti-report-001` | PIA Synthetic Annotated Anti-Report | `pia` | `publication` | `supporting` | `active` | `publication-maintainers` | `unversioned` | [Synthetic Annotated Anti-Report](../../docs/publications/examples/AntiPatterns/PIA_Synthetic_Annotated_AntiReport.md) | `standard-publication-001`<br>`principle-pia-measurement-001` |
| `publication-project-status-001` | OSI-PIA Project Status | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `0.4.0` | [Project Status](../../docs/PROJECT_STATUS.md) | `governance-model-001`<br>`architecture-pia-intake-subsystem-001`<br>`architecture-graph-platform-001` |
| `evidence-osi-case-001` | OSI Evidence Case 001 — Capability Blockage | `osi` | `evidence` | `supporting` | `proposed` | `osi-research` | `0.1` | [Capability Blockage](../../docs/evidence/demonstrations/OSI_Evidence_Case_001_Capability_Blockage.md) | `standard-publication-001`<br>`principle-osi-foundational-001` |
| `evidence-osi-case-002` | OSI Evidence Case 002 — False Capability Signal | `osi` | `evidence` | `supporting` | `proposed` | `osi-research` | `0.1` | [False Capability Signal](../../docs/evidence/demonstrations/OSI_Evidence_Case_002_False_Capability_Signal.md) | `standard-publication-001`<br>`principle-osi-foundational-001` |
| `evidence-osi-case-003` | OSI Evidence Case 003 — Misattribution of Failure | `osi` | `evidence` | `supporting` | `proposed` | `osi-research` | `0.1` | [Misattribution of Failure](../../docs/evidence/demonstrations/OSI_Evidence_Case_003_Misattribution_of_Failure.md) | `standard-publication-001`<br>`principle-osi-foundational-001` |

## Publication authority

Examples demonstrate patterns and anti-patterns; they do not become evidence
about a participant or establish ontology. New public outputs must preserve
the evidence, consent, uncertainty, and human-review boundaries of the
publication standard.
