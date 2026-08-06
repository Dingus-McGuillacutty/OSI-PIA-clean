# PIA Validation Snapshot

Snapshot ID:
PIA-VS-0001

Dataset:
[dataset name and version]

Generated:
[timestamp]

Pipeline Version:
[commit, release, or configuration version]

---

## 1. Input Summary

Records received:
Records accepted:
Records rejected:
Records modified during normalization:
Known missing fields:
Source authorization record:

---

## 2. Graph Summary

Nodes created:
Relationships created:
Node types:
Relationship types:
Disconnected nodes:
Duplicate candidates:
Constraint violations:
Import warnings:

Graph Integrity Status:
PASS / PASS WITH WARNINGS / FAIL

---

## 3. Observed Patterns

### Pattern 1

Observation:
[plain description of what the graph shows]

Supporting evidence:
- relevant nodes;
- relevant relationships;
- source records;
- calculation or query used.

Interpretation:
[what the observation may mean]

Confidence:
LOW / MODERATE / HIGH

Alternative explanations:
[other plausible interpretations]

---

### Pattern 2

Observation:

Supporting evidence:

Interpretation:

Confidence:

Alternative explanations:

---

## 4. Traceability Sample

Analytical statement:
[example conclusion]

Derived from:
[source records]

Graph path:
[node → relationship → node]

Query or metric:
[query identifier or calculation]

Transformation history:
[normalization and mapping steps]

Reviewer:
[name or identifier]

---

## 5. Contradictions and Anomalies

Evidence that does not fit the primary interpretation:

Unexpected graph structures:

Missing evidence:

Possible data-quality problems:

Possible model or ontology problems:

---

## 6. Assurance Result

Governance Gate:
PASS / WARNING / FAIL

Evidence Gate:
PASS / WARNING / FAIL

Graph Gate:
PASS / WARNING / FAIL

Assessment Gate:
PASS / WARNING / FAIL

Overall Status:
SUPPORTED / PROVISIONAL / NOT SUPPORTED

---

## 7. Human Review

Reviewed by:

Review date:

Decision:
- Accept as preliminary evidence
- Accept with restrictions
- Return for revision
- Reject

Reviewer rationale:

### Adversarial Test ###

finding_id: PIA-F-003

observation:
  Departures clustered after a leadership transition.

working_interpretation:
  The transition may have contributed to workforce instability.

disconfirming_evidence:
  - departures were already scheduled before the transition
  - departures reflect retirement eligibility
  - similar departments experienced the same pattern
  - the sample excludes retained or transferred employees

current_status:
  PROVISIONAL