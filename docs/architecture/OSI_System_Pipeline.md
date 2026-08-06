# OSI System Pipeline

**Status:** Working architecture  
**Purpose:** Define how information moves through OSI/PIA and how reusable engines connect through stable contracts.

## Principle

The repository stores contracts. Engines operate on those contracts.

No engine may depend on a particular participant, organization, or source
document. Engines accept contract-compliant inputs and produce
contract-compliant outputs.

The reusable interface between engines is informally called the **chopsticks rule**:

> An engine is reusable only when it can be picked up by its documented inputs and outputs without reaching into its internal implementation.

## Pipeline

```text
Source material
    ↓
Normalization Engine
    ↓
Canonical CSV package
    ↓
Validation Engine
    ↓
Validated package + validation report
    ↓
Import Engine
    ↓
Neo4j graph + import audit
    ↓
Analysis Engine
    ↓
Observations, indicators, and state transitions
    ↓
Reporting Engine
    ↓
Human-readable publication or decision support
```

## Engine Interface Contract

Every engine must declare:

1. **Inputs** — accepted files, records, versions, and preconditions.
2. **Outputs** — produced artifacts and their contract versions.
3. **Validation** — blocking errors, warnings, and notices.
4. **Side effects** — files written, graph writes, or other state changes.
5. **Idempotency** — whether rerunning produces duplicates or unsafe changes.
6. **Auditability** — logs, counts, provenance, and version metadata.
7. **Failure behavior** — what is rolled back, preserved, or marked incomplete.

## Engines

### Normalization Engine

Converts source material into the canonical participant package while preserving provenance and separating source evidence from interpretation.

### Validation Engine

Checks package structure, field values, identifiers, foreign keys, provenance, privacy boundaries, and contract version compatibility.

### Import Engine

Writes validated records to Neo4j using stable identifiers, dependency order, rerunnable `MERGE` behavior, and import audit records.

### Analysis Engine

Produces derived observations, indicators, hypotheses, and state-transition candidates without altering source Evidence.

### Reporting Engine

Publishes evidence-backed findings with explicit separation among evidence, observation, interpretation, confidence, and possible action.

## Version Flow

Every package and engine run must record:

- data contract version
- CSV contract version
- validation contract version
- import contract version
- ontology version
- engine version
- run identifier
- run timestamp

## Architectural Boundary

```text
Contracts define truth conditions.
Engines enforce or transform according to contracts.
Audits explain what happened.
Humans retain interpretive and ethical responsibility.
```

## Initial Build Order

1. Canonical CSV templates
2. Validation engine
3. Generic import engine
4. Import audit output
5. Synthetic participant regression packages
6. Analysis and reporting engines
