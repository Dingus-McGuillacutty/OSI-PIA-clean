# OSI Assurance Implementation Matrix v0.1

This matrix translates the common assurance framework into practical tests for different OSI–PIA component types.

| Component type | Contract | Validation | Technical congruence | Philosophical congruence | Regression | Performance | Ethics | Audit |
|---|---|---|---|---|---|---|---|---|
| Normalization engine | Accepted source forms and canonical records | Required fields, IDs, enums, dates | Every output traces to source location | Meaning, context, and uncertainty preserved | Golden source produces accepted canonical package | Records/time and manual interventions | No unsupported interpretation or sensitive-data expansion | Source, engine, contract, output hashes |
| Import engine | Accepted package and graph mutations | Referential integrity and constraints | Graph matches validated package | Evidence/interpretation boundary remains intact | Re-import is idempotent and golden graph remains stable | Nodes and relationships/time | No hidden enrichment or unauthorized linkage | ImportRun with counts and disposition |
| Validation engine | Rules, severity, report format | Rule execution and report integrity | Report corresponds to actual defects | Warnings do not imply unsupported judgment | Known-invalid fixtures fail predictably | Records checked/time | Rules do not encode discriminatory assumptions | Rule versions and full findings |
| Analysis engine | Inputs, outputs, inference boundaries | Computation and mapping checks | Findings trace to evidence and method | Uncertainty retained; observation not presented as fact | Golden graph yields expected findings | Query/runtime measures | Consequential outputs require human review | Analysis version, parameters, evidence paths |
| Scoring model | Variables, weights, scale, intended use | Range, missing data, calculation | Score reproduces declared formula | Score does not falsely imply total human or organizational value | Fixed fixtures yield stable scores | Batch runtime | Bias, misuse, interpretability, appeal/review path | Model version, inputs, score explanation |
| Visualization | Data contract and display semantics | Valid fields and rendering | Visual marks match source values | Scale, emphasis, and omission do not mislead | Snapshot/data fixture comparison | Render time | Privacy, accessibility, non-manipulative presentation | Data/version/render metadata |
| Report/exporter | Included objects and output format | Structure, links, citations, encoding | Export matches graph/query result | Context and caveats preserved | Golden export comparison | Generation time/file size | Redaction and audience controls | Source query, template, version, timestamp |
| Schema/contract | Scope, terms, compatibility | Syntax and internal consistency | Implementations can map to declared structure | Terms align with OSI principles | Existing fixtures remain representable | Not usually applicable | Privacy and interpretive boundaries explicit | Version, reviewers, change rationale |
| AI-assisted extraction | Model task, allowed inputs/outputs, refusal rules | Structured output and required provenance | Extracted claims map to exact source passages | Model does not silently invent, strengthen, or diagnose | Fixed source set evaluated across versions | Time/token/manual review | Sensitive inference, consent, bias, mandatory human review | Model/version/prompt/source/result/reviewer |
| Human review workflow | Roles, decisions, escalation, evidence access | Required steps and dispositions | Decision maps to reviewed evidence | Reviewer distinguishes observation, inference, and judgment | Calibration cases and inter-rater review | Review time and backlog | Fairness, conflict of interest, appeal and correction | Reviewer, decision basis, waivers, timestamp |

## Minimum Qualification Package

Before a component may be marked `qualified`, it must contain:

1. a completed `component_manifest.yaml`;
2. an implementation or explicit non-code procedure;
3. tests addressing all seven assurance dimensions;
4. at least one golden fixture;
5. at least one invalid or adverse fixture when invalid input is possible;
6. a machine-readable assurance report;
7. documented human-review gates;
8. a completed Chopsticks Test.

## Congruence Test Pattern

Each component should answer the same three questions:

1. **Correspondence:** Does the output accurately correspond to the input and declared transformation?
2. **Preservation:** Were provenance, context, uncertainty, and evidence boundaries preserved?
3. **Alignment:** Does the result remain aligned with OSI’s purpose of diagnosis, understanding, development, and human agency rather than surveillance or control?

## Waivers

A waiver may document why a test is temporarily unavailable, but it cannot convert a failed required test into a pass. Waivers must include:

- assurance dimension;
- reason;
- risk created;
- compensating control;
- approver;
- expiration or review date.
