---
artifact_id: ontology-graph-property-dictionary-001
domain: shared
layer: ontology
authority: supporting
status: active
version: "0.2"
owner: graph-maintainers
---

# Graph Property Dictionary

**Status:** Working reference aligned to architecture profile v0.2

The versioned contracts and migrations are authoritative. This dictionary is a
compact guide to common property names.

## Capability

| Property | Meaning |
|---|---|
| `capability_id` | Stable, non-semantic capability identity |
| `capability_name` | Current human-readable capability name |
| `definition` | Operational definition, with definition status when provisional |
| `definition_status` | Maturity of the definition |
| `status` | `proposed`, `working`, `established`, or `deprecated` |
| `ontology_version` | Version of the ontology under which the definition is interpreted |

Confidence is not a property of the Capability or the Participant. Confidence
belongs to a bounded analytical assertion such as
`Evidence-[:SUPPORTS]->Capability`.

## Evidence-to-Capability assertion

| Property | Meaning |
|---|---|
| `mapping_id` | Stable identity of one evidence-to-capability assertion |
| `assertion_id` | Shared assertion-architecture alias for `mapping_id` |
| `confidence` | Bounded numeric confidence from `0.00` through `1.00` |
| `confidence_basis` | Rationale for that confidence |
| `assertion_basis` | Shared assertion-architecture alias for the basis |
| `proposed_by` | Human, model, reviewer, or accountable legacy source |
| `review_status` | `proposed`, `accepted`, `rejected`, or `needs_review` |
| `created_at` | Assertion record time |
| `reviewed_at` | Optional review time |

## Common temporal properties

- `created_at` and `updated_at` are the canonical record timestamps.
- Event, observation, collection, and source times remain separate.
- Unknown time is represented explicitly with a corresponding status property;
  migration time must not be presented as source or event time.
