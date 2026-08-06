---
artifact_id: registry-principle-001
domain: shared
layer: governance
authority: canonical
status: active
version: "1.1"
owner: repository-governance
---

# Principle Registry

## Scope

This registry indexes foundational, engineering, ethical, and measurement
principles that constrain architecture and implementation.

| Artifact ID | Name | Domain | Layer | Authority | Status | Owner | Version | Canonical Location | Depends On |
|---|---|---|---|---|---|---|---|---|---|
| `principle-osi-foundational-001` | Foundational OSI Principles | `osi` | `principle` | `canonical` | `active` | `osi-architecture` | `unversioned` | [Foundational Principles](../../principles/Foundational%20Principles.md) | `—` |
| `principle-shared-engineering-001` | OSI-PIA Engineering Principles | `shared` | `principle` | `canonical` | `active` | `architecture-maintainers` | `unversioned` | [Engineering Principles](../../principles/Engineering%20Principles.md) | `principle-osi-hippocratic-001` |
| `principle-osi-hippocratic-001` | OSI Hippocratic Principle | `osi` | `governance` | `canonical` | `active` | `osi-governance` | `unversioned` | [OSI Hippocratic Principle](../../governance/OSI%20Hippocratic%20Principle.md) | `principle-osi-foundational-001` |
| `principle-pia-measurement-001` | PIA Measurement Doctrine | `pia` | `governance` | `canonical` | `active` | `pia-governance` | `unversioned` | [PIA Measurement Doctrine](../../governance/PIA_MEASUREMENT_DOCTRINE.md) | `adr-pia-0001`<br>`ontology-shared-meta-001` |
| `principle-pia-behavioral-inference-001` | PIA Behavioral Capability Inference Principle | `pia` | `principle` | `working` | `proposed` | `pia-ontology` | `0.2.0` | [Behavioral Capability Inference Principle](../../principles/PIA%20Behavioral%20Capability%20Inference%20Principle.md) | `principle-pia-measurement-001`<br>`ontology-shared-meta-001` |
| `principle-architecture-supporting-001` | Supporting Architectural Principles | `shared` | `principle` | `supporting` | `active` | `architecture-maintainers` | `unversioned` | [Architectural principles](../../docs/principles/architectural_principles.md) | `principle-shared-engineering-001` |
| `principle-hippocratic-supporting-001` | Supporting Hippocratic Principle | `osi` | `principle` | `supporting` | `review-required` | `osi-governance` | `unversioned` | [Hippocratic principle reference](../../docs/principles/hippocratic_principle.md) | `principle-osi-hippocratic-001` |

## Authority note

The supporting Hippocratic document remains review-required until its
relationship to the canonical governance principle is explicitly described or
it is superseded.
