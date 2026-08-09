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
    ↓
Foundation
    ↓
Principles
    ↓
Ontology
    ↓
Research
    ↓
Data
    ↓
Graph
    ↓
Analysis
    ↓
Software
```

These layers are related, but they are not interchangeable.

Each answers a different question.

---


## Relationship between PIA and OSI

PIA and OSI are related but distinct.

PIA focuses primarily on understanding the capabilities, experiences, outputs, and development of individuals.

OSI focuses on the organizational systems in which people participate.

A simplified relationship is:

```text
PIA
Person-level capability and evidence
    ↓
Participation and relationships
    ↓
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
    ↓
Research note
    ↓
Hypothesis
    ↓
Operational definition
    ↓
Test or evidence
    ↓
Refined principle or ontology concept
    ↓
Data specification
    ↓
Graph implementation
    ↓
Analytical method
    ↓
Software feature
```

Not every idea will move through every stage.

Some ideas may remain useful hypotheses.

Some may be rejected.

Some may require major revision.

The repository should preserve enough history to understand that evolution.

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
