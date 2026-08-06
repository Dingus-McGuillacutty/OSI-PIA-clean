# PIA Measurement Doctrine

**Status:** Governance Draft  
**Scope:** Professional Identity Architecture and any OSI component using PIA-derived evidence

## Purpose

This doctrine defines what PIA measures, what it does not measure, and the limits governing interpretation of its outputs.

Its purpose is to prevent evidence architecture from becoming person scoring.

## Foundational principle

> **PIA evaluates evidence—not people.**

PIA assesses the evidential support for specific conclusions. It does not assess the intrinsic value of a participant.

All PIA outputs are statements about the current state of available evidence and the confidence of resulting assessments. They are not statements about a participant's worth, potential, intelligence, morality, social value, or future capability.

## Object of measurement

The object of measurement is the evidence supporting a bounded claim or assessment.

PIA may evaluate provenance, specificity, relevance, traceability, verification, corroboration, source independence, consistency, contradiction, recency, coverage, and uncertainty.

These characteristics belong to the evidence record. They do not belong to the participant as permanent personal attributes.

## Behavioral capability inference

PIA may infer a capability when source-grounded behavior operationally
supports it even if the source does not use the capability's preferred name.
The system must distinguish directly demonstrated behavior, strong behavioral
inference, and contextual suggestion.

A job title, credential, self-description, or broad label does not establish
demonstrated application by itself. Broad ideas such as teamwork and
leadership must be decomposed into the specific behavior or bounded
educational preparation supported by the evidence.

All supplied evidence must be considered and assigned a traceable
disposition. Coursework, education, training, and credentials may support
claims about structured learning, topic exposure, professional preparation,
and capability relevance even when direct workplace application is not
documented. Such evidence must remain distinguishable from behavioral
demonstration.

Course content may be topically aligned with listed experiences when both
support the same capability. That alignment is analytically useful but does
not establish that the course caused, preceded, or was applied in the
experience unless the source states that connection.

Credential titles with unresolved bodies of knowledge must be marked
`title_only_unknown` or `conflicting_definition` and routed to a
definition-expansion queue. An issuer definition may establish the
credential's assessed domain but not participant application or performance.
Explicit source linkage between credential completion and a listed experience
may be recorded separately from the credential's educational claim.

Problem-directed behavior occurring in a documented interdependent group,
department, project, or organizational context may support a bounded strong
inference of shared problem-solving. Mere group membership is insufficient,
and the inference does not establish consensus, equal contribution, or shared
authority.

Every behavioral inference must retain its evidence chain, behavioral basis,
confidence and basis, review state, source-independence limits, contextual
scope, and a negative boundary stating what the evidence does not prove.

The working
[PIA Behavioral Capability Inference Principle](../principles/PIA%20Behavioral%20Capability%20Inference%20Principle.md)
and
[PIA Capability and Pattern Profile](../ontology/PIA_CAPABILITY_PATTERN_PROFILE.md)
provide the proposed implementation vocabulary. They remain subordinate to
this doctrine until promoted through governance.

## Knowledge distinctions

```text
Claim
    ↓
Observation
    ↓
Evidence
    ↓
Verification
    ↓
Assessment
    ↓
Interpretation
    ↓
Decision
```

A claim may initiate inquiry but does not verify itself. An observation records what was perceived or documented. Evidence is information used to support or challenge a bounded conclusion. Verification evaluates whether evidence can be authenticated or independently confirmed. Assessment integrates evidence using an explicit method. Interpretation explains what the assessment may mean. A decision is a human action for which accountable decision-makers remain responsible.

No layer may silently substitute for another.

## Facts, claims, and verified facts

The system should not collapse self-report, documentary evidence, independent corroboration, and verified facts into one undifferentiated category.

Repeated self-authored claims do not become independent corroboration through repetition.

Unknown should remain unknown. Estimated should remain estimated. Assumed should remain assumed.

## Evidence Fidelity Index

The Evidence Fidelity Index, while under development, may summarize characteristics of evidence supporting a specific assessment.

It must always be scoped to a defined claim or assessment, a known evidence set, an explicit method version, and a stated time or evidence-state boundary.

EFI is not a person score, reputation score, employability measure, prediction of future performance, or proxy for human worth.

A low EFI indicates limitations in the evidence available for the scoped assessment. It does not establish absence of capability.

## Quantitative restraint

Numbers may create an appearance of certainty that the evidence does not justify.

Therefore:

- precision should not exceed methodological validity;
- confidence should not exceed evidential support;
- composite values should remain decomposable;
- underlying evidence dimensions should remain visible;
- uncertainty and missingness should be preserved;
- thresholds should be documented and contestable;
- model versions should remain traceable.

Opaque scores are incompatible with this doctrine.

## Participant agency

Participants are active contributors to their evidence records, not passive objects of measurement.

Where appropriate, participants should be able to review relevant evidence, provide context, identify errors, challenge interpretations, contribute additional evidence, understand how an assessment was produced, and understand what uncertainty remains.

Participant input does not automatically override conflicting evidence, but it must remain representable and distinguishable within the evidence record.

## Provisionality and correction

Assessments are provisional statements based on current evidence.

New evidence may strengthen, weaken, qualify, or reverse an assessment.

The architecture should preserve enough evidence, reasoning, and version history for consequential assessments to be revisited.

Knowledge systems should make correction inexpensive. Irreversible conclusions require proportionally stronger evidence. Architecture should favor learning over certainty.

## Permitted assessment language

Preferred language describes evidence and confidence:

- evidence strongly supports;
- evidence moderately supports;
- evidence is presently insufficient;
- independent corroboration is limited;
- coverage is incomplete;
- contradictory evidence remains unresolved;
- emerging evidence is present;
- the pattern has not yet been assessed;
- confidence is low, moderate, or high for this scoped conclusion.

Language should not transform evidential conditions into essential judgments about the participant.
Insufficient evidence means that the scoped evidence cannot presently support
the finding; it does not mean the participant lacks the capability.

## Prohibited interpretations

PIA outputs must not be represented as a reputation score, credit-like score, universal rank, measure of human worth, morality score, intelligence score, automatic employability score, autonomous hiring or exclusion decision, proof that an undocumented capability is absent, or permanent identity classification.

## Human accountability

AI may assist with extraction, organization, comparison, pattern detection, and explanation.

AI does not remove human responsibility for consequential decisions.

The system should improve the visibility and accountability of human judgment rather than conceal judgment behind automation.

## Governing statement

> **The strength of an assessment must never exceed the strength of its supporting evidence.**

When governance, documentation, methodology, interface, and implementation diverge from this doctrine, the divergence is an architectural defect.
