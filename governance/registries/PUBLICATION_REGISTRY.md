---
artifact_id: registry-publication-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.7"
owner: repository-governance
---

# Publication Registry

## Scope

This registry indexes governed publications and examples. Publication
conformance rules are registered as `standard-publication-001` in the Standard
Registry.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `public-documentation-landing-001` | OSI-PIA Public Documentation Landing | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `1.1` | [Public landing](../../docs/index.md) | `standard-publication-001` |
| `publication-start-here-001` | OSI-PIA Start Here | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `1.1` | [Start Here](../../docs/START_HERE.md) | `standard-publication-001` |
| `publication-see-it-work-001` | OSI-PIA See It Work Guide | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `1.1` | [See It Work](../../docs/SEE_IT_WORK.md) | `standard-publication-001` |
| `publication-evidence-index-001` | OSI-PIA Evidence Index | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `1.0` | [Evidence](../../docs/evidence/index.md) | `standard-publication-001` |
| `evidence-osi-case-data-map-001` | OSI Evidence Case-to-Data Map | `osi` | `evidence` | `supporting` | `proposed` | `osi-research` | `0.1` | [Case-to-data map](../../docs/evidence/CASE_DATA_MAP.md) | `standard-publication-001`<br>`evidence-osi-case-001`<br>`evidence-osi-case-002`<br>`evidence-osi-case-003` |
| `publication-research-index-001` | OSI-PIA Research Index | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `1.0` | [Research](../../docs/research-standards/README.md) | `standard-publication-001` |
| `publication-repository-link-001` | OSI-PIA Repository Link | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `1.0` | [Repository](../../docs/REPOSITORY.md) | `standard-publication-001` |
| `publication-articles-index-001` | OSI-PIA Articles Index | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `1.0` | [Articles](../../docs/publications/articles/index.md) | `standard-publication-001` |
| `publication-article-hiring-translation-001` | Hiring Does Not Have a Talent Problem. It Has a Translation Problem. | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.1` | [Hiring translation article](../../docs/publications/articles/2026-08-11_hiring-translation-problem.md) | `standard-publication-001` |
| `publication-article-false-negative-001` | The False Negative Machine | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.1` | [False Negative Machine](../../docs/publications/articles/2026-08-13_false-negative-machine.md) | `standard-publication-001` |
| `publication-article-manufactured-polish-001` | Real Capability vs. Manufactured Polish | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.1` | [Manufactured Polish](../../docs/publications/articles/2026-08-18_real-capability-vs-manufactured-polish.md) | `standard-publication-001` |
| `milestone-osi-live-sandbox-validation-2026-08-12` | OSI Live Synthetic Sandbox Validation | `osi` | `assurance` | `working` | `active` | `osi-architecture` | `0.1` | [OSI sandbox validation](../../docs/history/MILESTONE_2026-08-12_OSI_LIVE_SANDBOX_VALIDATION.md) | `standard-publication-001` |
| `publication-article-hidden-workers-capability-leakage-001` | Hidden Workers and Capability Leakage | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.2` | [Hidden Workers and Capability Leakage](../../docs/publications/articles/2026-08-29_hidden-workers-capability-leakage.md) | `standard-publication-001` |
| `publication-article-wrong-metrics-001` | The Wrong Metrics Are Steering the System | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.2` | [The Wrong Metrics Are Steering the System](../../docs/publications/articles/2026-08-29_wrong-metrics-steering-system.md) | `standard-publication-001` |
| `publication-article-personal-evidence-system-001` | The Future Is Not the Perfect Résumé | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.1` | [The Future Is Not the Perfect Résumé](../../docs/publications/articles/2026-08-29_future-not-perfect-resume.md) | `standard-publication-001` |
| `publication-article-ats-reader-layer-001` | Poking a Hole in the Fog of ATS War | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.1` | [Poking a Hole in the Fog of ATS War](../../docs/publications/articles/2026-08-29_poking-hole-ats-war.md) | `standard-publication-001` |
| `publication-article-what-pia-pca-builds-001` | What PIA/PCA Is Trying to Build | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.2` | [What PIA/PCA Is Trying to Build](../../docs/publications/articles/2026-09-03_what-pia-pca-is-trying-to-build.md) | `standard-publication-001` |
| `publication-article-what-osi-measures-001` | What OSI Is Trying to Measure | `shared` | `publication` | `supporting` | `active` | `publication-stewardship` | `0.1` | [What OSI Is Trying to Measure](../../docs/publications/articles/2026-09-03_what-osi-is-trying-to-measure.md) | `standard-publication-001` |
| `publication-pia-anti-report-001` | PIA Synthetic Annotated Anti-Report | `pia` | `publication` | `supporting` | `active` | `publication-maintainers` | `unversioned` | [Synthetic Annotated Anti-Report](../../docs/publications/examples/AntiPatterns/PIA_Synthetic_Annotated_AntiReport.md) | `standard-publication-001`<br>`principle-pia-measurement-001` |
| `publication-project-status-001` | OSI-PIA Project Status | `shared` | `publication` | `supporting` | `active` | `repository-governance` | `0.4.0` | [Project Status](../../docs/PROJECT_STATUS.md) | `governance-model-001`<br>`architecture-pia-intake-subsystem-001`<br>`architecture-graph-platform-001` |
| `evidence-osi-case-001` | OSI Evidence Case 001 — Capability Blockage | `osi` | `evidence` | `supporting` | `proposed` | `osi-research` | `0.2` | [Capability Blockage](../../docs/evidence/demonstrations/OSI_Evidence_Case_001_Capability_Blockage.md) | `standard-publication-001`<br>`principle-osi-foundational-001` |
| `evidence-osi-case-002` | OSI Evidence Case 002 — False Capability Signal | `osi` | `evidence` | `supporting` | `proposed` | `osi-research` | `0.2` | [False Capability Signal](../../docs/evidence/demonstrations/OSI_Evidence_Case_002_False_Capability_Signal.md) | `standard-publication-001`<br>`principle-osi-foundational-001` |
| `evidence-osi-case-003` | OSI Evidence Case 003 — Misattribution of Failure | `osi` | `evidence` | `supporting` | `proposed` | `osi-research` | `0.2` | [Misattribution of Failure](../../docs/evidence/demonstrations/OSI_Evidence_Case_003_Misattribution_of_Failure.md) | `standard-publication-001`<br>`principle-osi-foundational-001` |

## Publication authority

Examples demonstrate patterns and anti-patterns; they do not become evidence
about a participant or establish ontology. New public outputs must preserve
the evidence, consent, uncertainty, and human-review boundaries of the
publication standard.
