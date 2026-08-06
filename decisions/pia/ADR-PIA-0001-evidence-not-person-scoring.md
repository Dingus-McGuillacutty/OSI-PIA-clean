---
artifact_id: adr-pia-0001
domain: pia
layer: decision
authority: working
status: proposed
version: "1.0"
owner: pia-governance
---

# ADR-PIA-0001: PIA Evaluates Evidence, Not People

## Status

Proposed

## Scope

PIA and explicitly authorized PIA-derived cross-domain components.

## Context

PIA integrates multiple sources of participant evidence, including resumes, narratives, interviews, assessments, references, and work samples.

Systems that aggregate information about people can drift toward opaque scoring, reputation ranking, automated classification, or unsupported judgments.

A numerical representation may be interpreted as a property of the person even when it was originally intended to describe the available evidence.

This creates epistemic, ethical, and architectural risk.

## Decision

PIA will evaluate the evidential support for bounded conclusions rather than assign intrinsic scores to people.

Any evidence-fidelity measure must be attached to a defined claim, assessment, evidence set, method version, and evidence-state boundary.

A PIA assessment describes what the available evidence currently supports. It does not establish the participant's worth, potential, morality, intelligence, employability, or future capability.

## Required evidence chain

```text
Source
    â†“
Claim or Observation
    â†“
Evidence
    â†“
Verification
    â†“
Assessment
    â†“
Interpretation
    â†“
Human Decision
```

Each stage must remain distinguishable and traceable.

## Consequences

### Positive consequences

- Evidence remains inspectable.
- Uncertainty remains visible.
- Assessments can be corrected as new evidence appears.
- Participants are less likely to be reduced to opaque abstractions.
- Human decision-makers remain accountable.
- Documentation, governance, and implementation receive a shared design constraint.
- OSI can use PIA evidence without inheriting a person-ranking model.

### Costs and constraints

- Interfaces must communicate multidimensional evidence conditions rather than rely on a single convenient score.
- Data models must preserve provenance, verification, contradiction, uncertainty, and method version.
- Analytical methods must remain decomposable.
- Product development may be slower than opaque score-first approaches.
- Consequential assessments require stronger documentation and review.

## Implementation rules

1. A low Evidence Fidelity result must not be interpreted as low capability.
2. Missing evidence must not be interpreted as evidence of absence.
3. Repeated self-authored claims must not be counted as independent corroboration.
4. Composite indices must remain decomposable into their evidence dimensions.
5. Evidence, inference, assessment, interpretation, and recommendation must remain distinguishable.
6. Assessments must be revisable.
7. Consequential decisions must remain attributable to accountable humans.
8. Interfaces must not imply that an evidence measure is a permanent personal attribute.
9. Code, documentation, governance, and outputs must express this decision congruently.
10. Divergence from these rules must be treated as an architectural issue.

## Rejected alternatives

### Universal participant score

Rejected because a single score collapses multiple evidential conditions and is easily mistaken for a judgment of the person.

### Reputation model

Rejected because reputation is socially mediated, context dependent, vulnerable to bias, and not equivalent to verified evidence.

### Automated employability ranking

Rejected because employment decisions are contextual and consequential, and evidence coverage cannot establish the total capability or future performance of a person.

### Policy-only safeguard

Rejected because written policy without corresponding data, interface, analytical, and software constraints permits silent contradiction at runtime.

## Validation questions

1. What new understanding does this create?
2. How could it be misunderstood or misused by an otherwise well-intentioned organization?
3. Does it represent evidence, or does it accidentally encode a judgment?
4. Can a participant or reviewer reconstruct the supporting evidence and reasoning?
5. Can the assessment be revised when evidence changes?

## Relationship to other documents

This ADR is governed by the
[PIA Measurement Doctrine](../../governance/PIA_MEASUREMENT_DOCTRINE.md).

The developing measurement method is documented in the
[PIA Evidence Fidelity Index](../../active-research/methodology/PIA_EVIDENCE_FIDELITY_INDEX_WORKING.md).

The broader cross-domain boundary is established by
[ADR-SHARED-0001](../shared/ADR-SHARED-0001-repository-domain-boundaries.md).

