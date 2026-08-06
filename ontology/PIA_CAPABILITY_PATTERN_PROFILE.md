---
artifact_id: ontology-pia-capability-pattern-001
domain: pia
layer: ontology
authority: working
status: proposed
version: "0.2.0"
owner: pia-ontology
lifecycle_state: formulation
---

# PIA Capability and Pattern Profile

## Purpose

This working profile expands the PIA reference graph's ability to represent
capabilities demonstrated across varied professional, technical, service,
educational, and project experiences. It applies the
[PIA Behavioral Capability Inference Principle](../principles/PIA%20Behavioral%20Capability%20Inference%20Principle.md)
without turning broad report headings into unsupported person labels.

The profile defines:

- eight report-level `Pattern` objects;
- a behavioral capability vocabulary;
- permitted capability-to-pattern groupings;
- evidence-to-capability assertion requirements; and
- bounded finding states for later assessment and reporting.

It does not define participant scores, load participant data, or promote the
experimental PIA assessment stack.

## Semantic boundaries

### Capability

A Capability is a defined operational capacity that one or more evidence
items may support. The mapping concerns what the evidence demonstrates in its
documented context. It is not a permanent statement about a person.

### Pattern

A Pattern is a report-level analytical grouping assembled from capabilities
and their supporting evidence. A Pattern is revisable, time-bounded, and
participant-reviewable. Pattern names organize interpretation; they do not
operate as evidence-to-capability targets.

### Generic-label prohibition

`Teamwork` and `Leadership` must not be created as direct Capability targets
under this profile. Evidence must map to the specific behavior demonstrated.
The broader ideas may appear only in the pattern names `Collaboration and
Teamwork` and `Leadership and Human Development`.

## Pattern vocabulary

| Pattern ID | Pattern name | Scope |
|---|---|---|
| `PAT-PIA-SYSTEMS-INFORMATION` | Systems and Information | Building, organizing, enabling, or stewarding information and operational systems |
| `PAT-PIA-PROJECT-EXECUTION` | Project Design and Execution | Designing, planning, coordinating, and delivering bounded work |
| `PAT-PIA-ANALYSIS-DECISION-SUPPORT` | Analysis and Decision Support | Examining information, assessing conditions, and improving decisions |
| `PAT-PIA-COMMUNICATION-TRANSLATION` | Communication and Translation | Making information usable across formats, audiences, and domains |
| `PAT-PIA-COLLABORATION-TEAMWORK` | Collaboration and Teamwork | Coordinating interdependent work with other people and groups |
| `PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT` | Leadership and Human Development | Directing, enabling, developing, or stewarding people and shared work |
| `PAT-PIA-RISK-RESILIENCE-STEWARDSHIP` | Risk, Resilience, and Stewardship | Protecting people, information, continuity, resources, and governed obligations |
| `PAT-PIA-LEARNING-ADAPTATION` | Learning, Adaptation, and Professional Development | Learning from experience and applying development to changed practice |

## Capability vocabulary

The pattern shown is the capability's primary reporting home. A capability may
contribute to an additional pattern when the declared crosswalk supports it.

### Systems and information

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-KNOWLEDGE-PLATFORM-IMPLEMENTATION` | Knowledge Platform Implementation | Configures, introduces, or materially implements a platform used to organize or exchange knowledge |
| `CAP-PIA-KNOWLEDGE-MANAGEMENT` | Knowledge Management | Structures, maintains, retrieves, and improves the usability of shared knowledge |
| `CAP-PIA-INFORMATION-ARCHITECTURE` | Information Architecture | Organizes information structures, categories, navigation, and relationships for intended use |
| `CAP-PIA-OPERATIONAL-DATA-SYSTEM-DESIGN` | Operational Data System Design | Designs data structures or tools around an operational need and workflow |
| `CAP-PIA-WORKFLOW-DIGITIZATION` | Workflow Digitization | Converts a manual or fragmented process into a usable digital workflow |
| `CAP-PIA-INFORMATION-STEWARDSHIP` | Information Stewardship | Preserves the quality, accessibility, appropriate use, and governance of information |

### Project design and execution

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-PROJECT-DESIGN` | Project Design | Defines a bounded problem, intended result, work structure, and implementation approach |
| `CAP-PIA-IMPLEMENTATION-PLANNING` | Implementation Planning | Sequences resources, dependencies, stakeholders, and actions needed to put a design into use |
| `CAP-PIA-PROJECT-LEADERSHIP` | Project Leadership | Directs and coordinates a bounded project toward its documented purpose |
| `CAP-PIA-PROCESS-IMPROVEMENT-DELIVERY` | Process Improvement Delivery | Moves a process improvement from identified need through usable implementation |
| `CAP-PIA-CHANGE-SUPPORT` | Change Support | Helps people and work practices move through an introduced change |

### Analysis and decision support

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-OPERATIONAL-ANALYSIS` | Operational Analysis | Examines activities, constraints, dependencies, and effects to clarify an operational situation |
| `CAP-PIA-INTELLIGENCE-ANALYSIS` | Intelligence Analysis | Integrates relevant information into a bounded, uncertainty-aware analytical judgment |
| `CAP-PIA-THREAT-RISK-ASSESSMENT` | Threat and Risk Assessment | Identifies plausible threats, vulnerabilities, consequences, and response considerations |
| `CAP-PIA-DECISION-SUPPORT` | Decision Support | Produces or organizes analysis so an accountable person can make a better-informed decision |
| `CAP-PIA-SHARED-PROBLEM-SOLVING` | Shared Problem-Solving | Works with others to define, examine, and resolve a problem |

### Communication and translation

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-VISUAL-INFORMATION-TRANSLATION` | Visual Information Translation | Converts complex information into a visual form suited to the intended audience and decision |
| `CAP-PIA-TECHNICAL-NONTECHNICAL-TRANSLATION` | Technical-Nontechnical Translation | Preserves meaning while translating between technical and nontechnical audiences |
| `CAP-PIA-BRIEFING-PRESENTATION` | Briefing and Presentation | Organizes and communicates information for a defined audience, purpose, and setting |
| `CAP-PIA-DOCUMENTATION-DESIGN` | Documentation Design | Creates usable documentation whose structure supports comprehension and action |

### Collaboration and teamwork

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-COLLABORATIVE-EXECUTION` | Collaborative Execution | Completes interdependent work through active coordination with others |
| `CAP-PIA-CROSS-FUNCTIONAL-COLLABORATION` | Cross-Functional Collaboration | Coordinates work across distinct specialties, functions, or organizational boundaries |
| `CAP-PIA-STAKEHOLDER-COORDINATION` | Stakeholder Coordination | Aligns relevant people around needs, constraints, responsibilities, and next actions |
| `CAP-PIA-KNOWLEDGE-SHARING` | Knowledge Sharing | Makes useful knowledge available to others in a form they can apply |
| `CAP-PIA-FEEDBACK-INTEGRATION` | Feedback Integration | Elicits, evaluates, and incorporates relevant feedback into work |
| `CAP-PIA-ROLE-COORDINATION` | Role Coordination | Clarifies and coordinates interdependent responsibilities |
| `CAP-PIA-HANDOFF-MANAGEMENT` | Handoff Management | Preserves continuity, context, and accountability when work passes between people or functions |
| `CAP-PIA-CONFLICT-NAVIGATION` | Conflict Navigation | Works through disagreement or competing needs while preserving a usable path forward |
| `CAP-PIA-COLLABORATIVE-TECHNOLOGY-ADOPTION` | Collaborative Technology Adoption | Helps a group adopt technology through coordinated implementation, feedback, and use |

### Leadership and human development

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-TEAM-LEADERSHIP` | Team Leadership | Directs or enables the coordinated work of a defined team |
| `CAP-PIA-OPERATIONAL-LEADERSHIP` | Operational Leadership | Guides people and resources through ongoing operational responsibilities |
| `CAP-PIA-TECHNICAL-LEADERSHIP` | Technical Leadership | Provides technical direction, judgment, standards, or coordination for shared work |
| `CAP-PIA-TRAINING-DEVELOPMENT-LEADERSHIP` | Training and Development Leadership | Leads a sustained effort to improve the capability of other people |
| `CAP-PIA-GOVERNANCE-LEADERSHIP` | Governance Leadership | Establishes or stewards decision rights, standards, accountability, or review processes |
| `CAP-PIA-CRISIS-LEADERSHIP` | Crisis Leadership | Coordinates action and judgment under disruption, urgency, or elevated consequence |
| `CAP-PIA-INFORMAL-PEER-LEADERSHIP` | Informal or Peer Leadership | Influences and enables shared work without relying on formal supervisory authority |
| `CAP-PIA-CHANGE-LEADERSHIP` | Change Leadership | Directs or meaningfully enables a transition in systems, practices, or shared behavior |
| `CAP-PIA-STRATEGIC-LEADERSHIP` | Strategic Leadership | Connects long-range direction, tradeoffs, and coordinated action across a broad scope |
| `CAP-PIA-USER-ENABLEMENT` | User Enablement | Helps intended users understand, adopt, and effectively use a system or practice |
| `CAP-PIA-TRAINING-PROGRAM-DESIGN` | Training Program Design | Designs structured learning around defined needs, objectives, and application |
| `CAP-PIA-PERFORMANCE-DEVELOPMENT` | Performance Development | Uses guidance, practice, or feedback to improve another person's work capability |
| `CAP-PIA-TEAM-CAPABILITY-DEVELOPMENT` | Team Capability Development | Improves the collective ability of a group to perform shared work |
| `CAP-PIA-KNOWLEDGE-TRANSFER` | Knowledge Transfer | Deliberately moves usable know-how from one person or context to another |

### Risk, resilience, and stewardship

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-PHYSICAL-SECURITY-OPERATIONS` | Physical Security Operations | Applies protective processes and situational judgment in a physical operating environment |
| `CAP-PIA-SECURITY-SYSTEMS-OPERATIONS` | Security Systems Operations | Operates, coordinates, or improves technical systems used for protection and response |
| `CAP-PIA-EMERGENCY-CONTINUITY-PLANNING` | Emergency and Continuity Planning | Prepares coordinated actions that preserve critical activity through disruption |
| `CAP-PIA-GOVERNANCE-RESOURCE-STEWARDSHIP` | Governance and Resource Stewardship | Uses authority, resources, and controls within an accountable governance boundary |
| `CAP-PIA-COMPLIANCE-STEWARDSHIP` | Compliance Stewardship | Maintains or improves conformance with applicable obligations while preserving traceability |

### Learning, adaptation, and professional development

| Capability ID | Capability | Operational definition |
|---|---|---|
| `CAP-PIA-REFLECTIVE-LEARNING` | Reflective Learning | Examines experience to identify lessons, limits, and improved future practice |
| `CAP-PIA-PROFESSIONAL-LEARNING-ENGAGEMENT` | Professional Learning Engagement | Engages with structured learning, training, or credentialing relevant to professional development without implying workplace application |
| `CAP-PIA-PROFESSIONAL-DEVELOPMENT-APPLICATION` | Professional Development Application | Applies learning or development activity to actual work |
| `CAP-PIA-ADAPTIVE-PRACTICE` | Adaptive Practice | Adjusts methods or behavior in response to evidence, constraints, or changed conditions |

## Cross-pattern contributions

The executable profile assigns every capability to its primary pattern and
adds these bounded secondary contributions:

- Collaborative Technology Adoption also contributes to Systems and
  Information.
- Shared Problem-Solving also contributes to Collaboration and Teamwork.
- Change Leadership also contributes to Project Design and Execution.
- Knowledge Transfer also contributes to Communication and Translation.
- Information Stewardship also contributes to Risk, Resilience, and
  Stewardship.
- User Enablement also contributes to Communication and Translation.
- Team Capability Development also contributes to Collaboration and Teamwork.

These are ontology groupings, not claims about a participant.

## Capability evidence mapping profile

An Evidence-to-Capability `SUPPORTS` assertion created under this profile must
include the contracted mapping metadata plus:

| Property | Required meaning |
|---|---|
| `mapping_profile` | `pia-capability-evidence-mapping-0.2` |
| `inference_level` | `directly_demonstrated`, `strongly_inferred`, or `contextually_suggested` |
| `evidence_role` | `behavioral_demonstration` or `educational_preparation` |
| `claim_scope` | `demonstrated_application` or `knowledge_exposure` |
| `application_status` | Whether application is described, topically aligned but unverified, or not established |
| `aligned_experience_ids` | Optional listed experiences with explicit or topical alignment |
| `alignment_basis` | Why an experience alignment was or was not made |
| `credential_definition_status` | `source_defined`, `issuer_verified`, `participant_defined`, `title_only_unknown`, or `conflicting_definition` for educational evidence |
| `credential_definition_source` | Source used to define the course or credential domain |
| `credential_definition_uri` | Optional stable issuer or source URI |
| `credential_domain_scope` | Bounded assessed domain when the definition is resolved |
| `definition_expansion_required` | Whether intake must request or research a fuller definition |
| `behavioral_basis` | The source-grounded behavior supporting this capability |
| `negative_boundary` | What this evidence does not prove |
| `scope_limit` | The experience, role, project, time, or operating context to which the inference is bounded |
| `source_independence_note` | Whether supporting sources are independent, related, duplicated, or not yet assessed |

Additional rules:

- every supplied evidence record receives a traceable consideration
  disposition even when it does not warrant a capability assertion;
- a title, credential, or self-label alone is not a behavioral demonstration;
- course and credential bodies may support `educational_preparation` and
  `knowledge_exposure` mappings;
- educational mappings remain `contextually_suggested`, `needs_review`, and
  at or below `0.49` confidence;
- educational mappings never establish workplace application, proficiency,
  outcome quality, or professional identity by themselves;
- course-to-experience alignment may be explicit or topical, but topical
  alignment is not causal attribution or independent corroboration;
- title-only or conflicting credential definitions remain explicit and enter
  a definition-expansion queue rather than silently acquiring meaning;
- an issuer-verified credential definition establishes assessed domain, not
  participant application or performance;
- same-context problem-directed and interdependent group evidence may strongly
  infer Shared Problem-Solving, bounded against consensus, equal contribution,
  shared authority, and group membership alone;
- learning that is demonstrably adapted, translated, or taught for work may
  strongly infer Reflective Learning without implying a formal reflective
  method;
- repeated copies of one source do not become corroboration;
- `contextually_suggested` mappings must remain `needs_review` and may not
  exceed `0.49` confidence;
- `strongly_inferred` mappings may not exceed `0.89` confidence before human
  acceptance;
- directly demonstrated confidence remains bounded by evidence specificity,
  fidelity, provenance, and relevant contradiction;
- a negative boundary cannot be blank or replaced by generic boilerplate.

## Pattern finding states

Later assessments may use only these pattern-level states:

| Finding state | Meaning |
|---|---|
| `evidence_present` | The current evidence supports one or more relevant capabilities |
| `emerging_evidence` | Relevant evidence exists but remains limited, indirect, or under review |
| `insufficient_evidence` | The scoped evidence cannot presently support a finding |
| `mixed_or_contradictory_evidence` | Relevant evidence materially conflicts or points in different directions |
| `not_yet_assessed` | The evidence has not been evaluated for this pattern |

No state is equivalent to a global capability judgment. In particular,
`insufficient_evidence` does not mean the participant lacks the capability.

## Example

Evidence that a participant configured and introduced a shared collaboration
platform, organized its information structure, trained users, and coordinated
adoption could support:

- Knowledge Platform Implementation — directly demonstrated;
- Knowledge Management — directly demonstrated or strongly inferred,
  depending on the evidence detail;
- User Enablement — directly demonstrated;
- Collaborative Technology Adoption — directly demonstrated; and
- Change Leadership — strongly inferred when the evidence establishes
  coordinated transition behavior.

It does not by itself prove formal people-management authority, enterprise
strategy ownership, universal teamwork ability, or success outside the
documented implementation context.

## Implementation and promotion

Migration
[`005_pia_behavioral_capability_profile.cypher`](../graph/migrations/005_pia_behavioral_capability_profile.cypher)
installs this proposed vocabulary in `pia-reference`. The parameterized
[capability evidence importer](../graph/cypher/imports/import_capability_evidence_mappings_v0.2.cypher)
preserves the assertion fields, and the
[profile validator](../graph/cypher/validation/validate_pia_capability_evidence_profile_v0.2.cypher)
checks the reproducible boundary.

Implementation is not promotion. The principle, profile, and graph projection
remain working and proposed until reviewed under the governance model.
