# PIA Evidence Fidelity Index — Working Methodology

**Status:** Research Draft  
**Canonical:** No  
**Method maturity:** Concept development and validation planning

Nothing in this document should be considered part of the canonical PIA methodology until promoted through the repository architecture.

## Purpose

The PIA Evidence Fidelity Index (EFI) is a proposed method for describing the quality and support characteristics of evidence used in a specific PIA assessment.

EFI evaluates evidence. It does not evaluate the intrinsic value of a participant.

## Scope requirement

Every EFI result must be scoped to:

- a bounded claim or assessment;
- a defined evidence set;
- a method version;
- a known evidence-state date or boundary;
- stated exclusions and limitations.

An EFI value without scope is invalid.

## Proposed dimensions

### Provenance
Can the origin of the evidence be identified and traced?

### Specificity
Does the evidence describe concrete actions, outputs, decisions, responsibilities, or outcomes?

### Relevance
Does the evidence materially bear on the scoped claim?

### Verification
Can the evidence be authenticated or independently confirmed?

### Corroboration
Do genuinely independent sources support the same conclusion?

### Coverage
Does the evidence address the important parts of the scoped assessment?

### Consistency
Do sources align without unexplained conflict?

### Contradiction
Is there evidence that challenges or qualifies the conclusion?

### Recency
Is the evidence sufficiently current for the conclusion being considered?

### Traceability
Can the assessment be reconstructed from its supporting sources and reasoning steps?

## Candidate output form

EFI should initially favor a dimensional profile rather than a universal scalar.

```yaml
assessment_scope: "Technical leadership in Project Alpha"
evidence_state_date: "YYYY-MM-DD"
method_version: "working-0.1"

evidence_fidelity:
  provenance: high
  specificity: high
  relevance: high
  verification: moderate
  corroboration: limited
  coverage: moderate
  consistency: moderate
  contradiction: unresolved
  recency: high
  traceability: high

overall_interpretation:
  confidence: moderate
  limitations:
    - "Limited independent corroboration"
    - "Outcome evidence is incomplete"
```

A future composite may be explored only if it remains transparent, decomposable, and empirically defensible.

## Interpretation constraints

A low or incomplete EFI result means that the evidence supporting the scoped conclusion is limited.

It does not mean the participant lacks the capability, is unreliable, has low potential, is unsuitable for employment, or that the claim is necessarily false.

Absence of evidence is not automatically evidence of absence.

## Independence and repetition

Multiple documents derived from the same author or source chain may add context but do not necessarily add independent corroboration.

A resume claim, the same claim in a cover letter, and the same claim in a self-authored narrative may represent three source artifacts but one underlying self-report.

The method should represent source dependence explicitly.

## Contradiction handling

Contradiction should not be hidden inside a composite value.

The method should preserve the nature of the contradiction, the affected claim, source and provenance, whether the contradiction is resolved, and the reasoning used to qualify the assessment.

## Uncertainty and missingness

Unknown, unverified, missing, and contradictory are different conditions. They should not share one default value.

## Provisionality

EFI describes an evidence state, not a permanent condition.

New evidence may change coverage, verification, corroboration, contradiction, confidence, and interpretation.

Version history should make those changes reconstructable.

## Validation needs

Before promotion, EFI requires:

- operational definitions for each dimension;
- inter-rater reliability testing;
- sensitivity to different evidence types;
- testing for source dependence;
- testing for false precision;
- participant review and comprehension;
- misuse analysis;
- comparison of dimensional and composite outputs;
- documented limitations;
- governance review;
- implementation congruence testing.

## Open research questions

1. Which dimensions are independent enough to measure separately?
2. Should different claims require different dimension weights?
3. Can a composite index be useful without encouraging person scoring?
4. How should contradiction interact with corroboration and coverage?
5. How should source dependence be represented?
6. What interface best communicates low evidence without implying low capability?
7. How should time decay vary by evidence type and claim?
8. What minimum information is required to reproduce an EFI assessment?
9. How should participant-provided corrections enter the evidence state?
10. What downstream uses should be prohibited even if technically possible?
