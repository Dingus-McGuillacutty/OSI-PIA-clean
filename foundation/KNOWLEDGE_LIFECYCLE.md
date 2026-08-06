# Knowledge Lifecycle

## Purpose

The Knowledge Lifecycle defines the seven states through which knowledge progresses within the OSI/PIA ecosystem.

The lifecycle governs knowledge rather than documents. Any artifact capable of carrying knowledge—including research notes, datasets, graph structures, software, ontologies, architecture, methodologies, AI outputs, and educational material—may participate in this lifecycle.

## The Seven States

1. **Observation**
2. **Exploration**
3. **Formulation**
4. **Congruence**
5. **Validation**
6. **Promotion**
7. **Stewardship**

> Promotion represents increased justified confidence, not certainty.

## State Definitions

### 1. Observation

A phenomenon, condition, pattern, question, discrepancy, or possibility is noticed and recorded without requiring a settled explanation.

Typical outputs include:

- field notes
- raw findings
- questions
- anomalies
- initial evidence
- participant or system observations

### 2. Exploration

The observation is investigated through inquiry, comparison, evidence gathering, interpretation, and alternative explanations.

Typical outputs include:

- working notes
- source collections
- exploratory analysis
- competing hypotheses
- provisional relationships
- prototypes

### 3. Formulation

The explored material is organized into a coherent model, proposition, method, structure, or design that can be examined and challenged.

Typical outputs include:

- working definitions
- draft models
- proposed architecture
- methodological drafts
- candidate schemas
- explicit hypotheses

### 4. Congruence

The formulation is evaluated for compatibility without contradiction across relevant ontological, epistemic, architectural, data, human, system, implementation, temporal, governance, and AI domains.

Congruence is not agreement. It is compatibility without contradiction.

Typical outputs include:

- contradiction checks
- dependency review
- terminology alignment
- architectural fit assessment
- impact analysis
- identified exceptions or unresolved tensions

### 5. Validation

The congruent formulation is tested against evidence, implementation, use, replication, expert review, or repeated design examination.

Validation methods depend on the artifact and may include:

- empirical testing
- implementation testing
- graph assurance
- participant evidence
- comparative analysis
- peer or maintainer review
- repeated successful use

### 6. Promotion

Knowledge is advanced to a higher-confidence status and recognized for broader reliance, implementation, teaching, or canonical reference.

Promotion must be justified and recorded. It does not imply finality or certainty.

Typical outputs include:

- canonical documentation
- accepted architecture
- approved methodology
- released component
- adopted ontology
- validated educational material

### 7. Stewardship

Promoted knowledge is actively maintained over time. Stewardship includes review, provenance preservation, versioning, correction, refinement, deprecation, replacement, and retirement.

Stewardship prevents promoted knowledge from becoming invisible, static, or falsely permanent.

## State Transitions

Movement through the lifecycle is a series of justified state transitions.

Each transition should answer:

1. What state is the knowledge currently in?
2. What evidence supports that classification?
3. What evidence or review is required for the next state?
4. Who has authority to recognize the transition?
5. How will the decision and provenance be recorded?

The lifecycle should not be treated as mechanically linear in all cases. Knowledge may return to an earlier state when new evidence, contradiction, implementation failure, or environmental change requires renewed exploration or formulation.

## Relationship to Other Architecture

### Congruence Protocol

The Congruence Protocol evaluates whether a formulation is compatible with the wider OSI/PIA ecosystem and sufficiently free of unresolved contradiction to continue advancing.

### Knowledge Management Governance

Knowledge Management Governance defines transition authority, evidence expectations, canonical status, versioning, deprecation, and stewardship responsibilities.

### Assurance

Assurance provides structured evaluation of information, structures, and implementations. Assurance results may supply evidence for congruence, validation, promotion, or continued stewardship.

### ADRs

Architectural Decision Records preserve significant decisions, context, rationale, alternatives, consequences, and status. ADRs may document promotion decisions and later supersession.

## Application Across the Ecosystem

The lifecycle applies to:

- research
- architecture
- principles
- ontologies
- graph models
- datasets
- analytics
- software components
- component contracts
- AI-generated material
- methodologies
- participant materials
- educational and certification content
- governance protocols

## Human and AI Use

Humans and AI systems working within OSI/PIA should identify the lifecycle state of material when that state affects how the material may be interpreted or used.

AI-generated content begins as a contribution to observation, exploration, or formulation unless it is grounded in already-promoted knowledge and used within its supported scope. AI generation alone does not validate or promote knowledge.

## Teaching Model

The lifecycle is also a teaching framework. Learners should be able to recognize:

- the difference between noticing and explaining
- the difference between a coherent formulation and a validated one
- the role of congruence before adoption
- the meaning of justified promotion
- the continuing responsibility of stewardship

## Status

This document establishes the Knowledge Lifecycle as a core architectural reference for the OSI/PIA ecosystem. Detailed transition criteria and authority are governed by Knowledge Management Governance and may mature through future ADRs and implementation guidance.
