# OSI-PIA Platform Roadmap

## Completed and promoted foundation

### Assurance Framework v1.0

- Component Contract
- Finding Contract
- AssuranceResult Contract
- AssuranceReport Contract
- CSV Assurance Engine v1.0
- Continuous integration
- Reference documentation

This remains the shared certified foundation for later graph and participant
work.

## Validated working milestones

### OSI synthetic organizational-evidence assurance

**Recorded:** 2026-08-01
**Authority:** `working/proposed`; synthetic package validation only

- a participant-free organizational package now carries synthetic
  organization, structure, provenance, evidence, and observation-candidate
  records;
- its validator rejects invalid identities, broken provenance, missing
  negative boundaries, invalid confidence values, and unreviewed candidates;
- fixture and negative-path tests are reproducible; and
- the component does not connect to Neo4j, write a graph, create a diagnosis,
  or instantiate planned OSI analytic constructs.

This establishes the OSI equivalent of an evidence-assurance foundation. It
does not validate organizational analytics, graph projection, or use with a
real organization.

### OSI synthetic sandbox projection assurance

**Recorded:** 2026-08-01
**Authority:** `working/proposed`; synthetic-only sandbox use only

- an offline preflight permits only the declared local `OSI-Sandbox` target;
- malformed, non-synthetic, incomplete, or unreviewed records are blocked
  before authentication or graph I/O;
- one embedded synthetic organization → source → evidence → observation path
  was deliberately imported twice; and
- read-only validation proved one node of each required type, one supporting
  relationship, one expected path, and idempotent structure after the repeat.

This checkpoint validates local synthetic OSI graph mechanics. It does not
authorize real organizational projection, `osi-reference` imports,
organizational analytics, diagnostic output, or production graph import.

### OSI expanded synthetic projection package

**Recorded:** 2026-08-02
**Authority:** `working/proposed`; synthetic-only sandbox use only

- expanded the assured package from one to three source-grounded observation
  records covering process, structural, and resilience conditions;
- imported all three records into `OSI-Sandbox` twice; and
- read-only validation confirmed three sources, evidence records, observations,
  relationships, and expected paths with idempotent structure.

This expands graph-mechanics coverage. It does not validate OSI analytics,
diagnostics, real organizational data, or production graph behavior.

### PIA protected intake and credential-resolution baseline

**Recorded:** 2026-07-28
**Authority:** `working/proposed`; controlled-pilot review remains open

- Phase 2A local synthetic intake;
- Phase 2B encrypted Windows-local participant-intake candidate;
- authentication, authorization, malware inspection, withdrawal, deletion,
  retention, recovery, and tamper validation;
- participant-facing document selection and classification;
- Phase 3 participant-free credential-definition catalog and resolver; and
- reproducible repository, protection, catalog, and interface tests.

See the
[milestone record](docs/history/MILESTONE_2026-07-28_PIA_PROTECTED_INTAKE_AND_CREDENTIAL_RESOLUTION.md).

This milestone identifies an implemented development boundary. It is not a
production authorization or promotion of its working architecture.

### PIA protected evidence review and session lifecycle

**Recorded:** 2026-07-28
**Authority:** `working/proposed`; controlled-pilot review remains open

- bounded non-executing extraction of supported text-bearing documents;
- encrypted extracted-text persistence and exact provenance;
- participant-controlled evidence acceptance, correction, and exclusion;
- explicit separation between extraction and capability conclusions;
- authenticated session continuation and saved-work progress;
- clear separation of current, saved, empty, and removed session states; and
- permanent retirement and fail-closed validation of deleted session
  identifiers.

See the
[checkpoint record](docs/history/MILESTONE_2026-07-28_PIA_PROTECTED_EVIDENCE_AND_SESSION_LIFECYCLE.md).

This checkpoint advances the protected-intake implementation while preserving
its Formulation state and operational gate.

### PIA governed evidence-to-mapping handoff

**Recorded:** 2026-07-29
**Authority:** `working/proposed`; controlled-pilot and independent-review
requirements remain open

- accepted source-grounded evidence can create bounded, encrypted mapping
  proposals against the working capability vocabulary;
- distinct-account accept, reject, and scope-narrowing outcomes are preserved
  in protected audit history;
- an unresolved-proposal review queue supports direct reviewer selection; and
- controlled synthetic testing and protected-store validation confirmed all
  three decision paths.

See the
[milestone record](docs/history/MILESTONE_2026-07-29_PIA_GOVERNED_MAPPING_HANDOFF.md).

This checkpoint does not authorize graph projection, participant report claims,
or production participant processing.

### PIA mapping-to-output preview

**Recorded:** 2026-07-29
**Authority:** `working/proposed`; report publication and graph projection remain gated

- accepted mappings are deconflicted into a bounded participant preview;
- technical mapping detail is retained separately;
- output assurance holds incomplete or test-only framing; and
- a fresh synthetic test passed the participant-preview and dry-run-manifest
  path with no graph write.

See the [milestone record](docs/history/MILESTONE_2026-07-29_PIA_MAPPING_TO_OUTPUT_PREVIEW.md).

### PIA synthetic sandbox projection assurance

**Recorded:** 2026-07-30
**Authority:** `working/proposed`; synthetic-only sandbox use only

- exact dry-run projection packages are assured before any connection;
- the importer permits one embedded synthetic assertion only and requires an
  explicit local action and password;
- malformed packages are blocked before authentication or graph I/O; and
- a repeated local sandbox import was read back with exactly one evidence node,
  capability node, mapping relationship, and expected path.

See the [milestone record](docs/history/MILESTONE_2026-07-30_PIA_SYNTHETIC_SANDBOX_PROJECTION_ASSURANCE.md).

This checkpoint validates local synthetic graph mechanics. It does not
authorize participant projection, production graph import, or reporting.

## Current development

Development proceeds in two governed lanes that share assurance, provenance,
privacy, and human-review requirements.

### Shared graph lane — assured graph import

Objective: transform assured packages into a canonical Neo4j graph while
preserving provenance and audit references.

Expected deliverables:

- import pipeline;
- graph schema validation;
- import contracts;
- import audit;
- import CLI; and
- explicit sandbox, reference, and operational database boundaries.

Success criterion: only packages with an acceptable governed Assurance Report
and projection manifest proceed to their authorized graph target.

### OSI lane — organizational evidence assurance

Objective: extend the validated synthetic organization package into an
authorized, read-only sandbox projection and later bounded observation output,
without treating observations as diagnostic conclusions.

Expected deliverables:

- sandbox projection contract and target declaration;
- explicit organizational graph schema and post-write validator;
- idempotency, provenance, and rollback checks; and
- human-reviewed, uncertainty-preserving observation preview.

Success criterion: a synthetic, reviewed observation can be represented once
in an authorized OSI sandbox and read back with its evidence, scope, and
negative boundary intact.

### PIA lane — governed mapping-to-output handoff

Objective: prepare accepted, bounded mapping decisions for a dry-run
projection manifest and participant-reviewable outputs without copying
participant records into shared graph or public-definition systems.

Expected deliverables:

- accountable projection-manifest design;
- output-specific evidence, confidence, uncertainty, and boundary displays;
- participant-reviewable correction and dispute handoff;
- controlled dry-run graph-target validation; and
- controlled-pilot recovery, privacy, security, consent, and operational
  review.

Success criterion: an accepted bounded mapping can be represented in a
participant-reviewable output and a dry-run projection manifest without
exposing participant identity or converting interpretation into an unsupported
claim.

## Next milestones

### Shared graph assurance

Provide graph-level integrity, provenance, congruence, regression,
performance, ethics, epistemic-integrity, and audit guarantees.

### PIA Phase 4 — application linkage and participant feedback

Connect reviewed credential preparation to participant-controlled experience
evidence while distinguishing:

- explicit source attribution;
- participant-reported application;
- topical alignment without verification; and
- application not established.

Corrections, disputes, clarification, and supersession remain explicit.

## Later milestones

### PIA ontology mapping and assurance

Generate mapping-profile-compliant proposals and validate agent boundaries,
overreach, conflict, source dependence, and participant-review requirements.

### PIA projection and outputs

Extend the validated synthetic sandbox pattern to governed participant-
minimized projection contracts, authorized target controls, durable import
audit, and participant-facing and technical reports from the same assured
state.

### OSI analytics

Build reproducible workforce flow, capability, trust, network, organizational
metabolism, and state-transition analytics on assured graph data.

### Organizational intelligence

Produce explainable organizational-health intelligence with human review and
explicit uncertainty.

## Dependency paths

```text
Shared Assurance Framework ✔
├── Assured Graph Import
│   └── Graph Assurance
│       └── OSI Analytics
│           └── Organizational Intelligence
│
└── PIA Protected Intake Baseline ✔ (working/proposed)
    └── Protected Evidence Review and Session Lifecycle ✔ (working/proposed)
        └── Credential Definition Review and Evidence-to-Mapping Handoff
            └── Application Linkage and Participant Feedback
                └── Ontology Mapping and Assurance
                    └── Projection and Participant-Reviewable Outputs
```

Cross-domain work occurs only through explicit governed mappings. No milestone
may bypass assurance, provenance, traceability, privacy, participant consent,
retention, withdrawal, or accountable human review.
