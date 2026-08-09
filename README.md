# OSI-PIA
## Organizational Systems Intelligence and Professional Identity Architecture

> The repository is the canonical record of the OSI-PIA project.
> Conversations generate ideas; repository documents preserve, distinguish,
> and integrate them.

## Overview

Organizational Systems Intelligence is a research and engineering project for understanding how people, capabilities, relationships, organizational conditions, and state changes interact within human cooperative systems.

Professional Identity Architecture is a peer domain focused on
participant-controlled evidence, experience, capabilities, development, and
bounded assessment while keeping source facts separate from analytical
interpretation.

Through explicit governed mappings, PIA and OSI can support careful
organizational diagnosis, human development, and system repair. Neither domain
is subordinate to or authoritative over the other. They are not intended for
surveillance, coercive control, automated judgment, or the reduction of people
and organizations to simplistic scores.

## Validated foundation

- Assurance Framework v1.0
- CSV Assurance Engine v1.0
- Stable Component, Finding, AssuranceResult, and AssuranceReport contracts
- Continuous regression, audit, ethics, and epistemic-integrity assurance

## Current working milestone

PIA now has a validated local protected-intake, evidence-review, session
continuity, and participant-free credential-resolution checkpoint. This
includes a synthetic intake sandbox, encrypted Windows-local
participant-store candidate, bounded reviewable document extraction,
participant-controlled evidence decisions, executable withdrawal and
retention controls, durable session continuation, deletion-integrity
safeguards, an independently reviewable public credential catalog, and a
synthetic-only Neo4j sandbox-projection assurance path.

See the
[protected evidence and session-lifecycle checkpoint](docs/history/MILESTONE_2026-07-28_PIA_PROTECTED_EVIDENCE_AND_SESSION_LIFECYCLE.md),
which builds on the earlier
[protected-intake baseline](docs/history/MILESTONE_2026-07-28_PIA_PROTECTED_INTAKE_AND_CREDENTIAL_RESOLUTION.md).
The synthetic projection checkpoint is recorded separately in
[PIA Synthetic Sandbox Projection Assurance](docs/history/MILESTONE_2026-07-30_PIA_SYNTHETIC_SANDBOX_PROJECTION_ASSURANCE.md).
This development remains `working/proposed` and does not yet authorize
production real-participant processing.

## Platform paths

```text
Participant Package
â†“
CSV Assurance Engine
â†“
Assurance Report
â†“
Neo4j Graph Import
â†“
Graph Assurance
â†“
PIA analysis and participant-reviewable outputs

Organizational Evidence
â†“
Assurance and OSI Graph Projection
â†“
OSI analysis and human-accountable outputs

PIA â†” OSI only through explicit governed mappings
```

## Repository structure

- `foundation/` â€” current theoretical system model
- `ontology/` â€” technology-independent concepts and meta-ontology
- `software/` â€” platform implementation
- `tests/` â€” regression and integrity assurance
- `data/` â€” data contracts, guidance, templates, and controlled examples
- `connectors/` â€” numbered, contracted external-source adapters
- `graph/` â€” Neo4j schema, imports, validation, and graph data guidance
- `governance/` â€” ethical constraints, repository governance, conventions, and controlled migrations
- `architecture/` â€” domain, system, and graph architecture
- `docs/architecture/` â€” stable system design
- `docs/components/` â€” component reference manuals
- `decisions/` â€” scoped shared, OSI, PIA, and implementation decision rationale
- `docs/history/` â€” milestones and evolution
- `docs/research-standards/` â€” exploratory work
- `docs/principles/` â€” enduring engineering and ethical commitments

New here? Start with [`Start Here`](docs/START_HERE.md) for the guided
orientation. Then use [`docs/README.md`](docs/README.md) for the full
documentation map,
[`Project Status`](docs/PROJECT_STATUS.md) for the current implementation,
authorization, and next-decision snapshot,
[`docs/PLATFORM_OVERVIEW.md`](docs/PLATFORM_OVERVIEW.md) for a technical
orientation, and the
[`Repository Architecture`](governance/Repository_Architecture.md) for
repository authority and domain boundaries. The
[`Repository Registries`](governance/registries/README.md) provide the
authoritative artifact inventory. The proposed, Congruence-reviewed
[`Governance Model`](governance/GOVERNANCE_MODEL.md) consolidates these rules
without superseding the current canonical authorities; its
[ratification review](governance/GOVERNANCE_MODEL_RATIFICATION_REVIEW.md)
records the remaining promotion gate. The
[Clean Release Standard](governance/CLEAN_RELEASE_STANDARD.md) keeps the
restricted development archive separate from a participant-data-free release
lineage. See the
[`Graph Ontology Crosswalk`](architecture/graph_ontology/graph_Ontology.md)
for the boundary between conceptual, contracted, experimental, and implemented
graph objects.

## Guiding principles

- Assurance before ingestion
- Evidence before inference
- Explainability before automation
- Traceability before intelligence
- Ethics as a first-class concern
- Human judgment overrides automation

## Current development

Development now proceeds in two governed lanes:

- shared graph development: assured Neo4j import, Graph Assurance, and
  analytics on the certified graph model; and
- PIA development: controlled-pilot review, credential-definition review and
  protected queue integration, followed by application linkage, assurance,
  projection, and participant-reviewable outputs.

See [`ROADMAP.md`](ROADMAP.md) for milestone order and [`CHANGELOG.md`](CHANGELOG.md) for the project record.


