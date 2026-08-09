// PIA capability evidence and pattern profile v0.2.
// Target database: pia-reference
//
// Preconditions:
// - migrations 002 and 004 have been applied;
// - ontology:pia-reference exists;
// - a current backup exists under the operating environment's recovery policy.
//
// Scope:
// - additive working vocabulary only;
// - no participant, source, experience, evidence, or assessment data;
// - exact-name reuse avoids duplicating an existing capability or pattern;
// - implementation does not promote the principle or ontology profile.

CREATE CONSTRAINT pia_profile_capability_id_unique IF NOT EXISTS
FOR (n:Capability) REQUIRE n.profile_capability_id IS UNIQUE;

CREATE CONSTRAINT pia_profile_pattern_id_unique IF NOT EXISTS
FOR (n:Pattern) REQUIRE n.profile_pattern_id IS UNIQUE;

MATCH (ontology:Ontology {ontology_id: 'ontology:pia-reference'})

MERGE (migration:GraphMigration {
  migration_id: '005_pia_behavioral_capability_profile'
})
ON CREATE SET
  migration.applied_at = datetime(),
  migration.created_at = datetime()
SET
  migration.name = 'PIA Capability Evidence and Pattern Profile',
  migration.target_database = 'pia-reference',
  migration.version = '0.2.0',
  migration.status = 'applied',
  migration.managed_by = '005_pia_behavioral_capability_profile',
  migration.knowledge_lifecycle_state = 'formulation',
  migration.ontology_status = 'working',
  migration.updated_at = datetime()

MERGE (ontology)-[:APPLIED_MIGRATION]->(migration);

MATCH (legacy_pattern:Pattern)
WHERE legacy_pattern.pattern_name IS NULL
  AND legacy_pattern.name IN [
    'Systems and Information',
    'Project Design and Execution',
    'Analysis and Decision Support',
    'Communication and Translation',
    'Collaboration and Teamwork',
    'Leadership and Human Development',
    'Risk, Resilience, and Stewardship',
    'Learning, Adaptation, and Professional Development'
  ]
SET legacy_pattern.pattern_name = legacy_pattern.name;

UNWIND [
  {
    id: 'PAT-PIA-SYSTEMS-INFORMATION',
    name: 'Systems and Information',
    definition: 'Building, organizing, enabling, or stewarding information and operational systems'
  },
  {
    id: 'PAT-PIA-PROJECT-EXECUTION',
    name: 'Project Design and Execution',
    definition: 'Designing, planning, coordinating, and delivering bounded work'
  },
  {
    id: 'PAT-PIA-ANALYSIS-DECISION-SUPPORT',
    name: 'Analysis and Decision Support',
    definition: 'Examining information, assessing conditions, and improving decisions'
  },
  {
    id: 'PAT-PIA-COMMUNICATION-TRANSLATION',
    name: 'Communication and Translation',
    definition: 'Making information usable across formats, audiences, and domains'
  },
  {
    id: 'PAT-PIA-COLLABORATION-TEAMWORK',
    name: 'Collaboration and Teamwork',
    definition: 'Coordinating interdependent work with other people and groups'
  },
  {
    id: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT',
    name: 'Leadership and Human Development',
    definition: 'Directing, enabling, developing, or stewarding people and shared work'
  },
  {
    id: 'PAT-PIA-RISK-RESILIENCE-STEWARDSHIP',
    name: 'Risk, Resilience, and Stewardship',
    definition: 'Protecting people, information, continuity, resources, and governed obligations'
  },
  {
    id: 'PAT-PIA-LEARNING-ADAPTATION',
    name: 'Learning, Adaptation, and Professional Development',
    definition: 'Learning from experience and applying development to changed practice'
  }
] AS item
MERGE (pattern:Pattern {pattern_name: item.name})
ON CREATE SET
  pattern.pattern_id = item.id,
  pattern.definition = item.definition,
  pattern.status = 'working',
  pattern.ontology_version = 'pia-capability-pattern-profile-0.2.0',
  pattern.knowledge_lifecycle_state = 'formulation',
  pattern.participant_review_required = true,
  pattern.synthetic = false,
  pattern.managed_by = '005_pia_behavioral_capability_profile',
  pattern.created_at = datetime()
SET
  pattern.profile_pattern_id = item.id,
  pattern.profile_definition = item.definition,
  pattern.profile_status = 'working',
  pattern.profile_ontology_version =
    'pia-capability-pattern-profile-0.2.0',
  pattern.profile_method_version =
    'pia-capability-evidence-mapping-0.2',
  pattern.profile_knowledge_lifecycle_state = 'formulation',
  pattern.profile_participant_review_required = true,
  pattern.profile_synthetic = false,
  pattern.profile_managed_by =
    '005_pia_behavioral_capability_profile',
  pattern.updated_at = datetime();

UNWIND [
  {
    id: 'CAP-PIA-KNOWLEDGE-PLATFORM-IMPLEMENTATION',
    name: 'Knowledge Platform Implementation',
    definition: 'Configures, introduces, or materially implements a platform used to organize or exchange knowledge',
    primary_pattern: 'PAT-PIA-SYSTEMS-INFORMATION'
  },
  {
    id: 'CAP-PIA-KNOWLEDGE-MANAGEMENT',
    name: 'Knowledge Management',
    definition: 'Structures, maintains, retrieves, and improves the usability of shared knowledge',
    primary_pattern: 'PAT-PIA-SYSTEMS-INFORMATION'
  },
  {
    id: 'CAP-PIA-INFORMATION-ARCHITECTURE',
    name: 'Information Architecture',
    definition: 'Organizes information structures, categories, navigation, and relationships for intended use',
    primary_pattern: 'PAT-PIA-SYSTEMS-INFORMATION'
  },
  {
    id: 'CAP-PIA-OPERATIONAL-DATA-SYSTEM-DESIGN',
    name: 'Operational Data System Design',
    definition: 'Designs data structures or tools around an operational need and workflow',
    primary_pattern: 'PAT-PIA-SYSTEMS-INFORMATION'
  },
  {
    id: 'CAP-PIA-WORKFLOW-DIGITIZATION',
    name: 'Workflow Digitization',
    definition: 'Converts a manual or fragmented process into a usable digital workflow',
    primary_pattern: 'PAT-PIA-SYSTEMS-INFORMATION'
  },
  {
    id: 'CAP-PIA-INFORMATION-STEWARDSHIP',
    name: 'Information Stewardship',
    definition: 'Preserves the quality, accessibility, appropriate use, and governance of information',
    primary_pattern: 'PAT-PIA-SYSTEMS-INFORMATION'
  },
  {
    id: 'CAP-PIA-PROJECT-DESIGN',
    name: 'Project Design',
    definition: 'Defines a bounded problem, intended result, work structure, and implementation approach',
    primary_pattern: 'PAT-PIA-PROJECT-EXECUTION'
  },
  {
    id: 'CAP-PIA-IMPLEMENTATION-PLANNING',
    name: 'Implementation Planning',
    definition: 'Sequences resources, dependencies, stakeholders, and actions needed to put a design into use',
    primary_pattern: 'PAT-PIA-PROJECT-EXECUTION'
  },
  {
    id: 'CAP-PIA-PROJECT-LEADERSHIP',
    name: 'Project Leadership',
    definition: 'Directs and coordinates a bounded project toward its documented purpose',
    primary_pattern: 'PAT-PIA-PROJECT-EXECUTION'
  },
  {
    id: 'CAP-PIA-PROCESS-IMPROVEMENT-DELIVERY',
    name: 'Process Improvement Delivery',
    definition: 'Moves a process improvement from identified need through usable implementation',
    primary_pattern: 'PAT-PIA-PROJECT-EXECUTION'
  },
  {
    id: 'CAP-PIA-CHANGE-SUPPORT',
    name: 'Change Support',
    definition: 'Helps people and work practices move through an introduced change',
    primary_pattern: 'PAT-PIA-PROJECT-EXECUTION'
  },
  {
    id: 'CAP-PIA-OPERATIONAL-ANALYSIS',
    name: 'Operational Analysis',
    definition: 'Examines activities, constraints, dependencies, and effects to clarify an operational situation',
    primary_pattern: 'PAT-PIA-ANALYSIS-DECISION-SUPPORT'
  },
  {
    id: 'CAP-PIA-INTELLIGENCE-ANALYSIS',
    name: 'Intelligence Analysis',
    definition: 'Integrates relevant information into a bounded, uncertainty-aware analytical judgment',
    primary_pattern: 'PAT-PIA-ANALYSIS-DECISION-SUPPORT'
  },
  {
    id: 'CAP-PIA-THREAT-RISK-ASSESSMENT',
    name: 'Threat and Risk Assessment',
    definition: 'Identifies plausible threats, vulnerabilities, consequences, and response considerations',
    primary_pattern: 'PAT-PIA-ANALYSIS-DECISION-SUPPORT'
  },
  {
    id: 'CAP-PIA-DECISION-SUPPORT',
    name: 'Decision Support',
    definition: 'Produces or organizes analysis so an accountable person can make a better-informed decision',
    primary_pattern: 'PAT-PIA-ANALYSIS-DECISION-SUPPORT'
  },
  {
    id: 'CAP-PIA-SHARED-PROBLEM-SOLVING',
    name: 'Shared Problem-Solving',
    definition: 'Works with others to define, examine, and resolve a problem',
    primary_pattern: 'PAT-PIA-ANALYSIS-DECISION-SUPPORT'
  },
  {
    id: 'CAP-PIA-VISUAL-INFORMATION-TRANSLATION',
    name: 'Visual Information Translation',
    definition: 'Converts complex information into a visual form suited to the intended audience and decision',
    primary_pattern: 'PAT-PIA-COMMUNICATION-TRANSLATION'
  },
  {
    id: 'CAP-PIA-TECHNICAL-NONTECHNICAL-TRANSLATION',
    name: 'Technical-Nontechnical Translation',
    definition: 'Preserves meaning while translating between technical and nontechnical audiences',
    primary_pattern: 'PAT-PIA-COMMUNICATION-TRANSLATION'
  },
  {
    id: 'CAP-PIA-BRIEFING-PRESENTATION',
    name: 'Briefing and Presentation',
    definition: 'Organizes and communicates information for a defined audience, purpose, and setting',
    primary_pattern: 'PAT-PIA-COMMUNICATION-TRANSLATION'
  },
  {
    id: 'CAP-PIA-DOCUMENTATION-DESIGN',
    name: 'Documentation Design',
    definition: 'Creates usable documentation whose structure supports comprehension and action',
    primary_pattern: 'PAT-PIA-COMMUNICATION-TRANSLATION'
  },
  {
    id: 'CAP-PIA-COLLABORATIVE-EXECUTION',
    name: 'Collaborative Execution',
    definition: 'Completes interdependent work through active coordination with others',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-CROSS-FUNCTIONAL-COLLABORATION',
    name: 'Cross-Functional Collaboration',
    definition: 'Coordinates work across distinct specialties, functions, or organizational boundaries',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-STAKEHOLDER-COORDINATION',
    name: 'Stakeholder Coordination',
    definition: 'Aligns relevant people around needs, constraints, responsibilities, and next actions',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-KNOWLEDGE-SHARING',
    name: 'Knowledge Sharing',
    definition: 'Makes useful knowledge available to others in a form they can apply',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-FEEDBACK-INTEGRATION',
    name: 'Feedback Integration',
    definition: 'Elicits, evaluates, and incorporates relevant feedback into work',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-ROLE-COORDINATION',
    name: 'Role Coordination',
    definition: 'Clarifies and coordinates interdependent responsibilities',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-HANDOFF-MANAGEMENT',
    name: 'Handoff Management',
    definition: 'Preserves continuity, context, and accountability when work passes between people or functions',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-CONFLICT-NAVIGATION',
    name: 'Conflict Navigation',
    definition: 'Works through disagreement or competing needs while preserving a usable path forward',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-COLLABORATIVE-TECHNOLOGY-ADOPTION',
    name: 'Collaborative Technology Adoption',
    definition: 'Helps a group adopt technology through coordinated implementation, feedback, and use',
    primary_pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    id: 'CAP-PIA-TEAM-LEADERSHIP',
    name: 'Team Leadership',
    definition: 'Directs or enables the coordinated work of a defined team',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-OPERATIONAL-LEADERSHIP',
    name: 'Operational Leadership',
    definition: 'Guides people and resources through ongoing operational responsibilities',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-TECHNICAL-LEADERSHIP',
    name: 'Technical Leadership',
    definition: 'Provides technical direction, judgment, standards, or coordination for shared work',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-TRAINING-DEVELOPMENT-LEADERSHIP',
    name: 'Training and Development Leadership',
    definition: 'Leads a sustained effort to improve the capability of other people',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-GOVERNANCE-LEADERSHIP',
    name: 'Governance Leadership',
    definition: 'Establishes or stewards decision rights, standards, accountability, or review processes',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-CRISIS-LEADERSHIP',
    name: 'Crisis Leadership',
    definition: 'Coordinates action and judgment under disruption, urgency, or elevated consequence',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-INFORMAL-PEER-LEADERSHIP',
    name: 'Informal or Peer Leadership',
    definition: 'Influences and enables shared work without relying on formal supervisory authority',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-CHANGE-LEADERSHIP',
    name: 'Change Leadership',
    definition: 'Directs or meaningfully enables a transition in systems, practices, or shared behavior',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-STRATEGIC-LEADERSHIP',
    name: 'Strategic Leadership',
    definition: 'Connects long-range direction, tradeoffs, and coordinated action across a broad scope',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-USER-ENABLEMENT',
    name: 'User Enablement',
    definition: 'Helps intended users understand, adopt, and effectively use a system or practice',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-TRAINING-PROGRAM-DESIGN',
    name: 'Training Program Design',
    definition: 'Designs structured learning around defined needs, objectives, and application',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-PERFORMANCE-DEVELOPMENT',
    name: 'Performance Development',
    definition: 'Uses guidance, practice, or feedback to improve another person\'s work capability',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-TEAM-CAPABILITY-DEVELOPMENT',
    name: 'Team Capability Development',
    definition: 'Improves the collective ability of a group to perform shared work',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-KNOWLEDGE-TRANSFER',
    name: 'Knowledge Transfer',
    definition: 'Deliberately moves usable know-how from one person or context to another',
    primary_pattern: 'PAT-PIA-LEADERSHIP-HUMAN-DEVELOPMENT'
  },
  {
    id: 'CAP-PIA-PHYSICAL-SECURITY-OPERATIONS',
    name: 'Physical Security Operations',
    definition: 'Applies protective processes and situational judgment in a physical operating environment',
    primary_pattern: 'PAT-PIA-RISK-RESILIENCE-STEWARDSHIP'
  },
  {
    id: 'CAP-PIA-SECURITY-SYSTEMS-OPERATIONS',
    name: 'Security Systems Operations',
    definition: 'Operates, coordinates, or improves technical systems used for protection and response',
    primary_pattern: 'PAT-PIA-RISK-RESILIENCE-STEWARDSHIP'
  },
  {
    id: 'CAP-PIA-EMERGENCY-CONTINUITY-PLANNING',
    name: 'Emergency and Continuity Planning',
    definition: 'Prepares coordinated actions that preserve critical activity through disruption',
    primary_pattern: 'PAT-PIA-RISK-RESILIENCE-STEWARDSHIP'
  },
  {
    id: 'CAP-PIA-GOVERNANCE-RESOURCE-STEWARDSHIP',
    name: 'Governance and Resource Stewardship',
    definition: 'Uses authority, resources, and controls within an accountable governance boundary',
    primary_pattern: 'PAT-PIA-RISK-RESILIENCE-STEWARDSHIP'
  },
  {
    id: 'CAP-PIA-COMPLIANCE-STEWARDSHIP',
    name: 'Compliance Stewardship',
    definition: 'Maintains or improves conformance with applicable obligations while preserving traceability',
    primary_pattern: 'PAT-PIA-RISK-RESILIENCE-STEWARDSHIP'
  },
  {
    id: 'CAP-PIA-REFLECTIVE-LEARNING',
    name: 'Reflective Learning',
    definition: 'Examines experience to identify lessons, limits, and improved future practice',
    primary_pattern: 'PAT-PIA-LEARNING-ADAPTATION'
  },
  {
    id: 'CAP-PIA-PROFESSIONAL-DEVELOPMENT-APPLICATION',
    name: 'Professional Development Application',
    definition: 'Applies learning or development activity to actual work',
    primary_pattern: 'PAT-PIA-LEARNING-ADAPTATION'
  },
  {
    id: 'CAP-PIA-PROFESSIONAL-LEARNING-ENGAGEMENT',
    name: 'Professional Learning Engagement',
    definition: 'Engages with structured learning, training, or credentialing relevant to professional development without implying workplace application',
    primary_pattern: 'PAT-PIA-LEARNING-ADAPTATION'
  },
  {
    id: 'CAP-PIA-ADAPTIVE-PRACTICE',
    name: 'Adaptive Practice',
    definition: 'Adjusts methods or behavior in response to evidence, constraints, or changed conditions',
    primary_pattern: 'PAT-PIA-LEARNING-ADAPTATION'
  }
] AS item
MERGE (capability:Capability {capability_name: item.name})
ON CREATE SET
  capability.capability_id = item.id,
  capability.definition = item.definition,
  capability.status = 'working',
  capability.ontology_version = 'pia-capability-pattern-profile-0.2.0',
  capability.definition_status = 'working_behavioral_definition',
  capability.managed_by = '005_pia_behavioral_capability_profile',
  capability.created_at = datetime()
SET
  capability.profile_capability_id = item.id,
  capability.profile_definition = item.definition,
  capability.profile_status = 'working',
  capability.profile_ontology_version =
    'pia-capability-pattern-profile-0.2.0',
  capability.profile_definition_status =
    'working_behavioral_definition',
  capability.inference_profile = 'pia-capability-evidence-mapping-0.2',
  capability.profile_managed_by =
    '005_pia_behavioral_capability_profile',
  capability.updated_at = datetime()
WITH capability, item
MATCH (pattern:Pattern {profile_pattern_id: item.primary_pattern})
MERGE (capability)-[contribution:CONTRIBUTES_TO]->(pattern)
ON CREATE SET
  contribution.contribution_id =
    item.id + '--' + item.primary_pattern,
  contribution.assertion_id =
    'ASSERT-' + item.id + '--' + item.primary_pattern,
  contribution.assertion_basis =
    'Primary grouping declared by PIA Capability and Pattern Profile v0.1.0',
  contribution.confidence = 1.0,
  contribution.confidence_basis =
    'Exact declared ontology grouping; not a participant probability',
  contribution.proposed_by = 'pia-ontology',
  contribution.review_status = 'proposed',
  contribution.human_review_required = true,
  contribution.relationship_semantic_class = 'analytical_assertion',
  contribution.created_at = datetime()
SET
  contribution.grouping_profile =
    'pia-capability-pattern-profile-0.2.0',
  contribution.profile_managed_by =
    '005_pia_behavioral_capability_profile',
  contribution.updated_at = datetime();

UNWIND [
  {
    capability: 'CAP-PIA-COLLABORATIVE-TECHNOLOGY-ADOPTION',
    pattern: 'PAT-PIA-SYSTEMS-INFORMATION'
  },
  {
    capability: 'CAP-PIA-SHARED-PROBLEM-SOLVING',
    pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  },
  {
    capability: 'CAP-PIA-CHANGE-LEADERSHIP',
    pattern: 'PAT-PIA-PROJECT-EXECUTION'
  },
  {
    capability: 'CAP-PIA-KNOWLEDGE-TRANSFER',
    pattern: 'PAT-PIA-COMMUNICATION-TRANSLATION'
  },
  {
    capability: 'CAP-PIA-INFORMATION-STEWARDSHIP',
    pattern: 'PAT-PIA-RISK-RESILIENCE-STEWARDSHIP'
  },
  {
    capability: 'CAP-PIA-USER-ENABLEMENT',
    pattern: 'PAT-PIA-COMMUNICATION-TRANSLATION'
  },
  {
    capability: 'CAP-PIA-TEAM-CAPABILITY-DEVELOPMENT',
    pattern: 'PAT-PIA-COLLABORATION-TEAMWORK'
  }
] AS item
MATCH (capability:Capability {profile_capability_id: item.capability})
MATCH (pattern:Pattern {profile_pattern_id: item.pattern})
MERGE (capability)-[contribution:CONTRIBUTES_TO]->(pattern)
ON CREATE SET
  contribution.contribution_id =
    item.capability + '--' + item.pattern,
  contribution.assertion_id =
    'ASSERT-' + item.capability + '--' + item.pattern,
  contribution.assertion_basis =
    'Secondary grouping declared by PIA Capability and Pattern Profile v0.1.0',
  contribution.confidence = 1.0,
  contribution.confidence_basis =
    'Exact declared ontology grouping; not a participant probability',
  contribution.proposed_by = 'pia-ontology',
  contribution.review_status = 'proposed',
  contribution.human_review_required = true,
  contribution.relationship_semantic_class = 'analytical_assertion',
  contribution.created_at = datetime()
SET
  contribution.grouping_profile =
    'pia-capability-pattern-profile-0.2.0',
  contribution.profile_managed_by =
    '005_pia_behavioral_capability_profile',
  contribution.updated_at = datetime();

MATCH (migration:GraphMigration {
  migration_id: '005_pia_behavioral_capability_profile'
})
MATCH (pattern:Pattern {
  profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
})
WITH migration, count(DISTINCT pattern) AS pattern_count
MATCH (capability:Capability {
  profile_ontology_version: 'pia-capability-pattern-profile-0.2.0'
})
RETURN
  migration.migration_id AS migration_id,
  migration.status AS status,
  pattern_count,
  count(DISTINCT capability) AS capability_count;
