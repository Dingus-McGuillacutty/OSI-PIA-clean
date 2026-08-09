# DATA/README.md

# OSI Data

## Purpose

This directory contains the data architecture that supports
Organizational Systems Intelligence.

The emphasis is on **data definition**, **structure**, and **quality**,
not on storing operational datasets.

OSI separates the concepts being measured from the observations that
support those measurements.

---

## What belongs here

- data dictionaries
- import schemas
- field definitions
- validation rules
- measurement specifications
- sample datasets
- synthetic datasets
- anonymized examples
- data standards

---

## Suggested structure

data/
â”œâ”€â”€ dictionaries/
â”œâ”€â”€ schemas/
â”œâ”€â”€ examples/
â”œâ”€â”€ templates/
â”œâ”€â”€ validation/
â””â”€â”€ imports/

---

## Data philosophy

Data should remain:

- understandable
- reproducible
- explainable
- attributable
- version controlled

Every field should have a defined meaning.

Every dataset should have a known origin.

Every transformation should be reproducible.

---

## Relationship to other directories

foundation/
Defines what the concepts mean.

ontology/
Defines the entities and relationships.

graph/
Implements those concepts inside Neo4j.

active-research/
Uses the data to test hypotheses.

---

## Guiding principle

Data is evidence.

Evidence supports observations.

Observations support assessments.

Assessments support understanding.

OSI should never confuse these levels.
