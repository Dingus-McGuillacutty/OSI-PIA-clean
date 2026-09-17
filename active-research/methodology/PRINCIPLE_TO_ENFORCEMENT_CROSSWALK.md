---
artifact_id: research-principle-enforcement-crosswalk-001
title: "Principle-to-Enforcement Crosswalk"
domain: shared
layer: active-research
authority: working
status: proposed
version: "0.1"
owner: research-governance
lifecycle_state: formulation
review_cycle: milestone
last_reviewed: "2026-09-16"
---

# Principle-to-Enforcement Crosswalk

## Purpose

This working crosswalk traces a small initial set of OSI-PIA principles from
philosophical statement to governance rule, architecture or contract, and
observable implementation evidence. It distinguishes conceptual coherence from
actual enforcement.

The crosswalk does not promote a principle, contract, validator, or test. A
row may show that a rule is documented without showing that software enforces
it. A passed technical test may show structural congruence without proving the
underlying concept or ethical claim.

## Reading rule

- **Documented** — a governing or research artifact states the principle or
  boundary.
- **Specified** — an architecture, contract, or schema gives it an operational
  form.
- **Implemented** — code, configuration, or workflow contains a corresponding
  behavior or check.
- **Validated** — a named test or assurance result demonstrates that behavior
  for a bounded fixture or condition.
- **Open** — the proposed chain is incomplete, untested, or not authorized for
  production use.

The strongest status in a row is limited by the weakest necessary link. A
documented principle with no implementation evidence remains documented, not
implemented. An implementation test does not promote an authority state.

## Initial crosswalk

| Principle or commitment | Governance / boundary rule | Architecture, contract, or schema | Implementation or validator evidence | Current status | Open question |
|---|---|---|---|---|---|
| Evidence before inference | Source facts, observations, interpretations, and conclusions remain distinct; no unsupported claim may be promoted | Assurance logic chain; PIA evidence and capability-mapping contracts; evidence-to-observation graph relationships | CSV assurance and protected-intake validation paths; synthetic graph assurance records | Specified and boundedly validated | Which checks fail closed for every output path, not only the current fixtures? |
| Capability is not a credential, and capability may be blocked | A credential or role label is not itself proof of capability or usable opportunity | PIA evidence/capability mapping profile; OSI blockage and false-capability evidence cases | Synthetic OSI cases demonstrate bounded blockage and misattribution paths | Documented and demonstrated in synthetic evidence | Which independent observations are required before a capability inference is portable? |
| Trust and capability utilization are systemic | Do not assign a person-level explanation when organizational conditions may account for the observed outcome | OSI organization-source-evidence-observation model; separate OSI/PIA domain projections | OSI synthetic organization-to-observation import and validation | Specified and synthetically validated | What measurable receiving conditions are sufficient for a bounded OSI observation? |
| Epistemic integrity must survive transformation | Every assertion must retain provenance, limits, uncertainty, and review state | Assurance Architecture and Logic Chain; graph provenance and confidence metadata | Assurance reports, graph congruence validators, and read-only sandbox validation | Implemented for bounded paths; production status open | Are contradiction, supersession, and temporal validity enforced consistently across exports? |
| Human judgment and contestability have priority | Automation cannot override review, authorize promotion, or create consequential decisions by itself | Human-Centered Capability Infrastructure principle; protected intake review and correction contracts | Participant/reviewer decision workflow and output-assurance holds | Implemented in working local workflow; not production-authorized | Is every participant-facing decision reversible, inspectable, and retained with audit evidence? |
| OSI must not become a control mechanism | Understanding may guide responsible human attention but cannot by itself authorize guilt, punishment, employment action, surveillance, or control | OSI Hippocratic Principle; PIA Measurement Doctrine; Clean Release Standard | Protected intake boundaries, human-review requirements, output-assurance holds, and synthetic-only graph tests | Canonical principle with bounded implementation evidence; broad enforcement open | Which high-impact paths are mechanically blocked rather than only prohibited in documentation? |
| Temporal authority is bounded | Historical validity does not create unlimited authority over the present or future | Temporal Authority article; evidence dates, state transitions, and provenance requirements | Current records preserve dates and source context; a complete temporal validator is not yet established | Documented; implementation gap remains | What test detects stale claims being reused outside their temporal jurisdiction? |
| OSI and PIA remain peer domains | No cross-domain mapping may erase namespaces, infer identity from organizational conditions, or turn a PIA claim into an OSI fact | Graph Architecture, namespace standard, and explicit mapping requirements | Separate `osi-reference` and `pia-reference` baselines with synthetic projection tests | Implemented and synthetically validated | Which cross-domain mapping contracts are required before any non-synthetic projection? |
| Orientation precedes optimization | A human or computational participant must understand purpose, authority, and limits before acting | FOR_HUMANS, FOR_MACHINES, Start Here, and machine-orientation protocol | Assisted Claude orientation and governance-comprehension finding; blind access remains separate | Demonstrated under assisted retrieval | Can the same boundary be recognized under blind access and lower-capability models? |
| No single observer is definitive | No source, model, or projection alone establishes a universal conclusion; disagreement remains visible | Evidence fidelity methodology, provenance fields, confidence and review metadata | Source disagreement and bounded synthetic validation tests | Specified; broader corroboration testing open | How should independent-source dependence and contradiction be surfaced to participants? |

## What the first pass shows

The architecture is conceptually coherent across principles, governance,
contracts, graph structure, and public research. The evidence is uneven,
however. The strongest current chains are:

```text
evidence before inference
  -> assurance logic chain
  -> bounded contracts and graph paths
  -> synthetic validation

OSI/PIA separation
  -> graph architecture and namespaces
  -> separate reference projections
  -> synthetic congruence validation

human review and contestability
  -> protected intake and output contracts
  -> review decisions and assurance holds
  -> bounded local workflow tests
```

Temporal validity, independent corroboration, and production-grade
contestability remain less complete. They should not be described as fully
enforced merely because the principles are clearly stated.

## Philosophy-layer map

The five related documents answer different questions. They should remain
linked without being collapsed into one authority artifact:

| Document | Primary question | Current role | Boundary |
|---|---|---|---|
| [OSI Philosophical Constitution](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/foundation/OSI_CONSTITUTION.md) | What does OSI exist to protect and cultivate? | Supporting philosophical foundation at congruence | Does not operate policy, authorize promotion, or override governance |
| [Foundational Principles](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/principles/Foundational%20Principles.md) | What does the architecture commit to about organizations, capability, and knowledge? | Canonical principle source in the registry | Describes commitments; does not replace governance or assurance |
| [OSI Hippocratic Principle](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/governance/OSI%20Hippocratic%20Principle.md) | What must OSI never become or do? | Canonical harm-prevention governance principle | Constrains use; does not by itself prove technical enforcement |
| [PIA Measurement Doctrine](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/governance/PIA_MEASUREMENT_DOCTRINE.md) | What does PIA measure, and what must it refuse to claim? | Canonical PIA interpretive safeguard | Bounds interpretation; does not authorize production processing |
| [Human-Centered Capability Infrastructure](https://github.com/Dingus-McGuillacutty/OSI-PIA-clean/blob/main/principles/Human-Centered%20Capability%20Infrastructure.md) | Who should benefit from the infrastructure and how? | Working proposed affirmative design principle | Remains subject to governance review and promotion |

The map itself is a research aid. It does not change the authority carried by
any of the documents it compares. The metadata system should eventually be
normalized for the older principle and doctrine files that are still indexed
without front matter; that is a separate stewardship task from deciding their
substantive authority.

## Review protocol

For each subsequent row:

1. identify the exact principle and its current authority;
2. identify the governing rule or decision that gives it operational meaning;
3. link the contract, schema, or architecture artifact that specifies it;
4. name the implementation, validator, or workflow that performs the check;
5. attach a bounded test result or mark validation open;
6. record what the chain does not establish; and
7. route proposed promotion or enforcement changes through the normal review
   and governance path.

## Boundary

This is a research instrument for traceability. It does not establish that the
principles are universally true, that every implementation is safe, or that a
passing synthetic test authorizes production use. Its purpose is to make gaps
visible before conceptual coherence is mistaken for enforcement.
