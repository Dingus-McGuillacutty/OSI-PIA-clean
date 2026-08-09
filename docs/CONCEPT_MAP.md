# OSI / PIA Concept Map

## Purpose

This document provides a human-readable map of the major concepts in the OSI/PIA ecosystem and the relationships among them. It complements the folder structure by organizing the project around ideas rather than file locations.

## Knowledge Management Architecture

```text
Knowledge Lifecycle
        |
        | defines knowledge states
        v
Congruence Protocol
        |
        | evaluates readiness and compatibility
        v
Knowledge Management Governance
        |
        | governs authority, evidence, and promotion
        v
Assurance
        |
        | evaluates fidelity and operational suitability
        v
Stewardship
        |
        | maintains, reviews, versions, and retires knowledge
        v
Canonical Project Knowledge
```

## Knowledge Lifecycle

```text
Observation
    -> Exploration
    -> Formulation
    -> Congruence
    -> Validation
    -> Promotion
    -> Stewardship
```

Promotion represents increased justified confidence, not certainty.

## Core Organizational Concepts

```text
Trust
    -> Cooperation
    -> Motivation
    -> Capability Utilization
    -> Resilience
    -> Organizational Performance

Capability Capital
    -> People
    -> Relationships
    -> Experience
    -> Demonstrated Evidence
    -> Conditions enabling capability to be used

Organizational Metabolism
    -> Movement of people
    -> Movement of capability
    -> Movement of knowledge
    -> Movement of work
    -> State transitions over time
```

## Ontology to Graph Projection

```text
Foundation and Research
    -> propose system meaning
Domain Ontology
    -> defines concepts and relationships
Ontology Meta-Model
    -> defines item kinds, status, and projection rules
Data and Graph Contracts
    -> define accepted records and mappings
Graph Architecture
    -> separates shared rules from OSI and PIA database roles
Graph Ontology Crosswalk
    -> records mapping and implementation maturity
OSI Reference + PIA Reference
    -> implement distinct namespaced domain projections
Migrations, Import, and Validation
    -> implement and test Neo4j mechanics and congruence
Graph Assurance
    -> evaluates integrity and suitability
```

These steps are governed mappings, not interchangeable representations. A
concept may be canonical without being implemented, and an experimental graph
label may exist without being canonical.

## Architecture and Implementation

```text
Foundational Principles
    -> Architecture
    -> ADRs
    -> Component Contracts
    -> Implementation
    -> Assurance
    -> Evidence and Findings
```

## OSI and PIA

```text
Professional Identity Architecture (PIA)
    -> models the individual professional system
    -> evidence, experience, capability, identity, and development

Organizational Systems Intelligence (OSI)
    -> models the cooperative organizational system
    -> relationships, trust, movement, capability, structure, and state change

Explicit PIA-to-OSI mapping
    -> may relate participant-controlled capability evidence to a declared
       organizational purpose
    -> preserves namespaces, provenance, consent, and human review
    -> does not merge the domains or turn either graph into authority over the
       other
```

The two domains share epistemic and graph architecture. Cross-domain products
exist only through governed mappings; name similarity or a shared technical
platform does not establish semantic equivalence.

## Documentation Relationships

- **Glossary** defines canonical vocabulary.
- **Principles** establish foundational commitments.
- **Research** explores and tests ideas.
- **Architecture** records stable design.
- **ADRs** preserve significant decisions and their rationale.
- **Components** define implementation behavior.
- **History** records architectural evolution.
- **Knowledge Management Governance** governs how knowledge moves among these states and locations.

## Maintenance

Update this map when a concept becomes foundational, when relationships materially change, or when a new cross-cutting architectural mechanism is introduced.
