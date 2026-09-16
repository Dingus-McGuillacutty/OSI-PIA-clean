---
artifact_id: publication-project-status-001
title: OSI-PIA Project Status
domain: shared
layer: publication
authority: supporting
status: active
version: "0.5.3"
owner: repository-governance
lifecycle_state: validation
last_reviewed: "2026-09-16"
review_cycle: milestone
---

## Purpose and reading rule

This is the single orientation point for the project's present state. It is a
plain-language synthesis for contributors, reviewers, prospective users, and
automated documentation readers. It does **not** create architecture,
authority, a production authorization, or a claim about any participant. The
linked canonical documents govern when they differ from this summary.

## Machine-readable status

```json
{
  "project": "OSI-PIA",
  "as_of": "2026-09-16",
  "overall_authority": "working",
  "overall_status": "proposed",
  "production_participant_processing": "not_authorized",
  "participant_data_in_repository": "prohibited",
  "graph_projection": {
    "synthetic_local_sandbox": "validated",
    "real_participant_projection": "not_authorized",
    "real_organizational_projection": "not_authorized"
  },
  "current_focus": "governed artifact metadata, publication authoring, semantic discoverability, literature positioning, standards interoperability, and machine participation conformance",
  "canonical_sources": [
    "README.md",
    "ROADMAP.md",
    "governance/GOVERNANCE_MODEL.md",
    "architecture/pia-intake/PIA_Intake_Subsystem_Framework.md",
    "architecture/graph_ontology/Graph_Architecture.md"
  ]
}
```

## Executive state

## Current Public Status

As of September 2026, OSI-PIA has an active public GitHub Pages site, a
published public article series, documentation assurance records, registry and
link validation, and an enabled public discussion channel. The project remains
an active research and development system. It is not a production hiring,
employment-screening, psychological-assessment, or personnel-decision tool.

The public article series now includes the machine-participation sequence
*The False Negative Stack*, *Access Is Not Authority*, and *When the Gate Is
Right and Still Wrong*, followed by *Temporal Authority* and *Capability
Infrastructure Should Belong to the People It Describes*. These extend the
series from access and source authority into chronology, portability, and the
participant as a primary beneficiary. Publication remains a supporting
explanation layer and does not promote exploratory research into canonical
authority.

Artifact metadata is now governed through a versioned machine-readable contract
and validator-backed controlled vocabularies. Publication creation follows a
documented, reusable template path for individual articles and article series;
metadata remains an interface for interpretation, not a substitute for human
review or stewardship.

The project now maintains a living [Project Bibliography](publications/PROJECT_BIBLIOGRAPHY.md)
with 41 article-cited source locators and seven research-candidate sources for
PIA and OSI positioning. A working [Literature-Positioning Matrix](../active-research/methodology/LITERATURE_POSITIONING_MATRIX.md)
and accompanying [PIA/OSI positioning notes](../active-research/notes/PIA_OSI_LITERATURE_POSITIONING_NOTES.md)
separate established findings, recombination, and open propositions; they do
not make novelty or causal claims. This checkpoint is recorded in the
[literature bibliography and positioning milestone](history/MILESTONE_2026-09_LITERATURE_BIBLIOGRAPHY_POSITIONING.md).

A provisional [PIA ↔ Open Skills / LER Crosswalk](../active-research/methodology/PIA_LER_OPEN_SKILLS_CROSSWALK.md)
now defines the working boundary between PIA's richer evidence-and-inference
layer, a future semantic translation socket, established portable standards,
and OSI's organizational receiving conditions. It is not canonical architecture
or an authorization to export participant data.

The public [Briefs and Project Updates](publications/briefs/index.md) section
now preserves concise project-history context alongside the article series. Its
first brief records the independent convergence with the Open Skills/LER field
and the resulting human-centered division of labor.

OSI-PIA is a governed research-and-engineering project with two peer domains:

- **OSI** examines organizational systems, conditions, relationships, and
  state change.
- **PIA** helps a participant make their evidence, experience, preparation,
  capabilities, and development more visible without reducing them to a score
  or permanent label.

The project has a certified shared assurance foundation and a substantial PIA
working implementation. It is **not a production service** and is **not
authorized for unsupervised real-participant processing**. The central design
commitment is that evidence, interpretation, review, and graph representation
remain distinct and traceable.

## What is operationally demonstrated

| Area | Present state | Important boundary |
|---|---|---|
| Shared assurance | Assurance Framework v1.0, CSV assurance engine, contracts, and regression checks are established | Assurance does not itself authorize a downstream decision or graph write |
| Protected local intake | Local encrypted participant-store candidate, roles, malware inspection, withdrawal, deletion, retention, recovery, and audit-chain validation are implemented and tested | Working/proposed; not production security certification or public deployment |
| Evidence extraction and review | Bounded text extraction, encrypted derived text, provenance, and participant/reviewer keep-correct-exclude decisions are implemented | Unsupported or unreadable material is routed for review; extraction is not a capability conclusion |
| Credential meaning | Participant-free credential catalog, resolution, definition review, and limited lookup routing are implemented | Credential meaning does not prove completion, application, or performance |
| Capability mapping | Source-grounded mapping proposals, separate reviewer decisions, supersession, and output-assurance holds are implemented | A mapping is a bounded interpretation, not a permanent trait or score |
| Participant outputs | Working participant preview, technical companion, correction path, and dry-run manifest are implemented | No published report or production participant claim is authorized |
| Graph mechanics | One embedded synthetic assertion was imported twice into local `PIA-Sandbox`, then read-only validation proved no duplicate nodes, relationship, or path | Real participant projection, production target use, and durable import audit remain gated |
| OSI organizational evidence assurance | A participant-free synthetic organizational package is validated from organization and provenance records through a bounded observation candidate | No OSI diagnostic, Trust/Flow/Health construct, or organizational decision is authorized |
| OSI graph mechanics | Three embedded synthetic organization â†’ source â†’ evidence â†’ observation paths were imported twice into local `OSI-Sandbox`; read-only validation proved three paths with no duplicate structure | Real organizational projection, `osi-reference` import, production target use, and diagnostics remain gated |

## Current evidence flow

```text
Source material
  â†’ protected intake and provenance
  â†’ extraction and evidence review
  â†’ bounded mapping proposal and separate review
  â†’ participant preview + technical companion + dry-run manifest
  â†’ synthetic-only sandbox projection assurance
  â†’ future authorized participant-minimized projection
```

At every arrow, the system is intended to preserve source identity, limits,
review state, and correction history. A later stage cannot silently convert an
earlier-stage claim into stronger evidence.

OSI now has a verified synthetic-only projection path through `OSI-Sandbox`
covering three distinct bounded observations.
That path deliberately precedes real organizational data, `osi-reference`
imports, and any organizational diagnostic or analytic claim.

## Explicitly not authorized or not yet complete

- production, public, multi-user, or network-exposed participant intake;
- unsupervised real-participant processing;
- participant-data projection into Neo4j;
- automatic consequential assessment, ranking, hiring, exclusion, or
  employability claims;
- image and scanned-document OCR intake;
- durable graph import audit, rollback, exception handling, and graph-side
  deletion/retention semantics for participant projection;
- formal independent-review and exception governance for consequential use;
- production threat modeling, incident response, monitoring, accessibility,
  backup/recovery operations, and external privacy/security review; and
- promotion of the working PIA intake architecture, capability vocabulary, or
  Governance Model into canonical authority.
- OSI graph import, diagnostic output, organizational scoring, or use of
  planned OSI constructs such as Trust, Flow, or Organizational Health, except
  for the one embedded synthetic-only `OSI-Sandbox` test path.

## Current governance position

The proposed [Governance Model](../governance/GOVERNANCE_MODEL.md) has reached
Congruence and has a completed ratification review, but remains
`working/proposed`. The [ratification review](../governance/GOVERNANCE_MODEL_RATIFICATION_REVIEW.md)
requires a scoped shared ADR before promotion.

The [PIA Measurement Doctrine](../governance/PIA_MEASUREMENT_DOCTRINE.md) is
the practical interpretive safeguard: the system evaluates evidence supporting
a bounded claim, not a person's worth or universal potential. The [Clean
Release Standard](../governance/CLEAN_RELEASE_STANDARD.md) and repository
validation enforce a participant-data-free committed tree.

The working [Human-Centered Capability Infrastructure principle](../principles/Human-Centered%20Capability%20Infrastructure.md)
adds a shared design test: capability infrastructure should make a person's
capability understandable, portable, actionable, and developable for that
person—not merely more useful to institutions or technical intermediaries.
It remains proposed pending governance review.

## Next governed decisions

1. Define a participant-minimized projection contract: allowed fields,
   approval authority, target declaration, deletion/retention behavior, and
   acceptable assurance conditions.
2. Define durable graph import audit, rollback, exception, and post-write
   validation requirements before any non-synthetic projection.
3. Consolidate operational-readiness requirements for a controlled pilot:
   consent, privacy, threat model, incident response, key recovery, support,
   accessibility, and independent review.
4. Decide whether to ratify or revise the Governance Model through the scoped
   shared ADR required by its ratification review.
5. Review the seven bibliography candidates and update the literature-positioning
   matrix only after recording source-level limits and temporal scope.

## Canonical detail

- [Project README](../README.md) â€” project purpose and repository orientation.
- [Roadmap](../ROADMAP.md) â€” milestones and dependency order.
- [PIA Intake Subsystem Framework](../architecture/pia-intake/PIA_Intake_Subsystem_Framework.md) â€” proposed intake architecture and agent boundaries.
- [Graph Architecture](../architecture/graph_ontology/Graph_Architecture.md) â€” canonical graph roles and domain separation.
- [PIA Reference Database](../architecture/graph_ontology/PIA_Reference_Database.md) â€” participant-graph scope and acceptance boundary.
- [Sandbox Projection Assurance Milestone](history/MILESTONE_2026-07-30_PIA_SYNTHETIC_SANDBOX_PROJECTION_ASSURANCE.md) â€” tested synthetic graph mechanics.
- [Repository Registries](../governance/registries/README.md) â€” governed artifact inventory and authority state.
- [Literature bibliography and positioning milestone](history/MILESTONE_2026-09_LITERATURE_BIBLIOGRAPHY_POSITIONING.md) â€” source intake and positioning checkpoint.
- [PIA ↔ Open Skills / LER Crosswalk](../active-research/methodology/PIA_LER_OPEN_SKILLS_CROSSWALK.md) â€” provisional interoperability boundary.

