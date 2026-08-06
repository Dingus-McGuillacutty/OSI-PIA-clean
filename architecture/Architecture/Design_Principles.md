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

