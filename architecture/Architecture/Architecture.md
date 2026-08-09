# OSI Repository Architecture

## Purpose

This document explains how the OSI repository is organized, why its major directories are separate, and how ideas move from early research into formal concepts, data structures, graph models, and eventual software.

The repository is not only a storage location.

It is the working architecture of Organizational Systems Intelligence.

Its structure should help distinguish:

- what OSI assumes
- what OSI defines
- what OSI is testing
- what OSI measures
- what OSI implements
- what OSI must never become

---

## Repository model

The repository is organized as a sequence of connected layers.

```text
Governance
    â†“
Foundation
    â†“
Principles
    â†“
Ontology
    â†“
Research
    â†“
Data
    â†“
Graph
    â†“
Analysis
    â†“
Software
```

These layers are related, but they are not interchangeable.

Each answers a different question.

---

## Governance

```text
governance/
```

Governance defines the ethical boundaries of OSI.

It answers:

> How must this system be used?

This directory contains the principles that constrain research, measurement, interpretation, and implementation.

Examples include:

- the OSI Hippocratic Principle
- privacy standards
- minimum necessary observation
- limits on automation
- explainability requirements
- safeguards against coercive use
- rules for handling uncertainty

Governance applies to every other layer of the repository.

No technical capability overrides an ethical constraint.

---

## Foundation

```text
foundation/
```

Foundation contains the deepest conceptual architecture of OSI.

It answers:

> What kind of system is an organization?

This directory contains the broadest and most durable ideas in the framework.

Examples include:

- organizations as living cooperative systems
- organizational topology
- field conditions
- organizational energy
- organizational flow
- capability capital
- effective capability
- organizational health
- state transitions

Foundation documents should change slowly.

They should not contain every new hypothesis or temporary research idea.

---

## Principles

```text
principles/
```

Principles contains general propositions that guide interpretation and design.

It answers:

> What appears to be generally true about organizational systems?

Examples include:

- trust regulates organizational flow
- predictability enables participation
- capability may be blocked or suppressed
- organizational behavior is adaptive
- health is emergent
- measurement should preserve uncertainty
- diagnostics should support repair rather than blame

Principles are broader than individual research findings but may remain open to refinement.

---

## Ontology

```text
ontology/
```

Ontology defines the things that exist within the OSI model and the relationships among them.

It answers:

> What entities, properties, events, and relationships must OSI represent?

Examples include:

- Person
- Organization
- Role
- Position
- Team
- Capability
- Observation
- Evidence
- Event
- State
- State Transition
- Assessment
- Outcome
- Vacancy

The ontology is conceptual.

It should remain understandable without knowledge of Neo4j or any other technical platform.

The ontology should drive implementation.

Implementation should not silently redefine the ontology.

---

## Research

```text
active-research/
```

Research contains ideas that are still being explored, tested, compared, or validated.

It answers:

> What do we not yet know?

This directory may include:

- hypotheses
- candidate constructs
- proposed indicators
- measurement experiments
- literature notes
- validation studies
- unresolved questions
- test datasets
- methodological discussions

Research is expected to change frequently.

A concept should usually begin here before being promoted into a more stable part of the repository.

---

## Data

```text
data/
```

Data defines how observations are structured, documented, validated, and prepared for analysis.

It answers:

> What information do we collect, and what does each field mean?

This directory may contain:

- data dictionaries
- field definitions
- schemas
- validation rules
- import templates
- synthetic examples
- anonymized examples
- measurement specifications
- transformation documentation

The repository should generally store data architecture rather than private operational datasets.

Sensitive, personally identifiable, or confidential data should remain outside the public repository.

---

## Graph

```text
graph/
```

Graph contains the implementation of the OSI ontology as a connected model.

It answers:

> How are OSI concepts represented in Neo4j or another graph system?

This directory may contain:

- node-label definitions
- relationship definitions
- constraints
- indexes
- Cypher queries
- migrations
- seed data
- graph diagrams
- import mappings
- backup procedures

The graph is an implementation of the ontology.

The live Neo4j database is not the same thing as the graph architecture.

Git should contain what is needed to understand and rebuild the graph, not necessarily the active database files or private data.

---

## Analysis

```text
analysis/
```

Analysis contains repeatable methods for interpreting OSI data.

It answers:

> How do we turn structured evidence into useful organizational understanding?

This directory may eventually contain:

- analytical models
- scoring methods
- risk models
- vacancy-cost calculations
- state-transition analysis
- network analysis
- organizational-flow measures
- trust and predictability indicators
- notebooks
- scripts
- result templates

Analysis should distinguish clearly between:

- observed facts
- calculated indicators
- inferred constructs
- interpretations
- recommendations

---

## Software

```text
software/
```

Software contains applications and tools built from the OSI framework.

It answers:

> How can people interact with and use the system?

Possible future contents include:

- data-entry interfaces
- graph-management tools
- dashboards
- reporting systems
- connector frameworks
- visualization tools
- APIs
- diagnostic applications

Software should implement the framework without replacing it.

OSI must remain understandable independently of any single application.

---

## Decisions

```text
decisions/
```

Decisions contains Architecture Decision Records.

It answers:

> Why was this design choice made?

An ADR should be created when a decision materially affects:

- the conceptual model
- data architecture
- graph structure
- governance
- research method
- implementation direction

Examples include:

- modeling organizations as living cooperative systems
- treating predictability as a precondition of trust
- representing health as an emergent construct
- choosing Neo4j as the initial graph platform
- separating observations from assessments

Decision records preserve reasoning that might otherwise be lost.

---

## Patterns

```text
patterns/
```

Patterns describes recurring organizational configurations or dynamics.

It answers:

> What recognizable forms appear repeatedly across organizational systems?

Examples might include:

- vacancy spiral
- leadership churn
- capability island
- trust cascade
- information silo
- capability suppression
- organizational recovery
- healthy feedback loop

Patterns are not automatically laws.

They are reusable descriptions of phenomena that may appear across multiple cases.

---

## Examples

```text
examples/
```

Examples demonstrates how OSI concepts work in practice.

It answers:

> What does this look like in a concrete case?

Examples should normally use:

- fictional organizations
- synthetic data
- anonymized cases
- simplified demonstrations

A useful example may include:

```text
README.md
data.csv
graph.cypher
analysis.md
```

Examples help translate theory into something observable and teachable.

---

## Relationship between PIA and OSI

PIA and OSI are related but distinct.

PIA focuses primarily on understanding the capabilities, experiences, outputs, and development of individuals.

OSI focuses on the organizational systems in which people participate.

A simplified relationship is:

```text
PIA
Person-level capability and evidence
    â†“
Participation and relationships
    â†“
OSI
Organizational structure, conditions, flow, and state
```

PIA may contribute information about:

- capability
- experience
- production
- development
- role history
- individual state transitions

OSI may use that information to study:

- capability distribution
- capability utilization
- organizational flow
- blocked or suppressed capability
- trust conditions
- structural constraints
- organizational outcomes

PIA should not reduce a person to a score.

OSI should not reduce an organization to a dashboard.

Both should preserve human context and uncertainty.

---

## Movement of ideas through the repository

New concepts should not immediately become canonical.

A typical development path is:

```text
Conversation or observation
    â†“
Research note
    â†“
Hypothesis
    â†“
Operational definition
    â†“
Test or evidence
    â†“
Refined principle or ontology concept
    â†“
Data specification
    â†“
Graph implementation
    â†“
Analytical method
    â†“
Software feature
```

Not every idea will move through every stage.

Some ideas may remain useful hypotheses.

Some may be rejected.

Some may require major revision.

The repository should preserve enough history to understand that evolution.

---

## Promotion criteria

A concept may move from `active-research/` into a more stable directory when it has:

- a clear definition
- a known purpose
- distinction from related concepts
- supporting evidence or strong rationale
- documented limitations
- compatibility with governance
- a stable role in the larger model

Possible destinations include:

```text
foundation/
principles/
ontology/
patterns/
data/
graph/
```

Promotion does not mean permanent truth.

It means the concept is stable enough to serve as part of the current working architecture.

---

## Separation of concerns

Several directories may appear to overlap.

The distinction is intentional.

### Foundation versus principles

Foundation defines the broad system model.

Principles state propositions about how that system tends to behave.

### Ontology versus graph

Ontology defines concepts independently of technology.

Graph implements those concepts in Neo4j.

### Research versus foundation

Research contains uncertainty and exploration.

Foundation contains the current stable conceptual model.

### Data versus graph

Data defines fields, observations, schemas, and evidence structures.

Graph defines how those entities and relationships are connected.

### Analysis versus software

Analysis defines methods and calculations.

Software provides tools that execute or present them.

### Governance versus everything else

Governance constrains all research, data collection, analysis, and implementation.

---

## Evidence architecture

OSI should preserve the path from source information to conclusion.

A simplified evidence chain is:

```text
Source
    â†“
Observation
    â†“
Evidence
    â†“
Indicator
    â†“
Construct
    â†“
Assessment
    â†“
Interpretation
    â†“
Possible action
```

Each stage should remain distinguishable.

An assessment should not be presented as a direct observation.

An indicator should not be treated as the construct itself.

A recommendation should not be mistaken for a measured fact.

---

## Version-control philosophy

Git should preserve:

- conceptual changes
- documentation
- schema changes
- analytical methods
- Cypher files
- data templates
- migration history
- decision history
- synthetic examples
- reproducible scripts

Git should generally not contain:

- live database directories
- credentials
- passwords
- private participant data
- confidential organizational data
- raw personal archives
- automatic logs
- temporary files
- large database dumps

The repository should contain the architecture required to rebuild the system without exposing the private data used within it.

---

## Architectural principle

The repository should preserve a clear chain:

```text
Ethics constrain theory.

Theory defines concepts.

Concepts define data.

Data supports the graph.

The graph supports analysis.

Analysis supports human understanding.

Human understanding may support careful action.
```

## Graph Contract

Every graph object within PIA and OSI adheres to a common engineering contract.

Every node must answer:

1. What are you?
2. Who are you?
3. Why do you exist?

This contract provides a stable interface for reasoning, visualization, querying, and future automation.

See:

- [`Graph_Standards.md`](../graph_standards/Graph_Standards.md)
- [`OSI/PIA Reference Graph Congruence Profile`](../graph_ontology/REFERENCE_GRAPH_CONGRUENCE.md)

The final purpose of OSI is not surveillance, control, or administrative optimization for its own sake.

Its purpose is to help people understand, diagnose, repair, and strengthen the cooperative human systems in which they work.

