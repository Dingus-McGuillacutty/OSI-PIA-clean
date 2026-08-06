# OSI/PIA Graph Evidence Tour

**Classification:** Synthetic demonstration — no real participant data.

## 1. Basic PIA evidence chain

PIA preserves the inspectable path from participant-authorized source material
to evidence and bounded capability representation.

```mermaid
flowchart LR
    P["Synthetic Participant"]
    S1["Source Document<br/>Professional profile"]
    S2["Source Document<br/>Project record"]
    E1["Evidence<br/>Coordinated access planning"]
    E2["Evidence<br/>Resolved operational issue"]
    X["Experience<br/>Security operations"]
    C["Capability<br/>Physical Security Operations"]
    P -->|authorized source| S1
    P -->|authorized source| S2
    S1 -->|supports| E1
    S2 -->|supports| E2
    E1 -->|contextualizes| X
    E2 -->|contextualizes| X
    X -->|bounded interpretation| C
```

## 2. Evidence convergence

A capability can retain multiple supporting evidence paths without treating
frequency as proof of competence.

```mermaid
flowchart LR
    T["Training<br/>Incident coordination"] -->|supports with limits| C["Capability<br/>Incident Management"]
    X["Experience<br/>Operational response"] -->|supports| C
    P["Project<br/>Continuity exercise"] -->|supports| C
    W["Publication<br/>Procedure / briefing"] -->|supports with limits| C
```

## 3. Capability blockage

OSI distinguishes capability absence from capability blockage.

```mermaid
flowchart LR
    Person["Synthetic Participant"] -->|has capability| Cap["Capability<br/>Systems Thinking"]
    Person -->|occupies| Role["Role<br/>Security Coordinator"]
    Need["Organizational Need<br/>Continuity Planning"] -->|requires| Cap
    Cap -.->|cannot reach need| Route["Usable organizational route"]
    Role -->|constrained by| Block["Structural blockage<br/>No decision access"]
    Block -.->|interrupts| Route
```

## 4. Bridge position and dependency bottleneck

A vacancy can change topology when one role carries unique relationships,
knowledge, or routing responsibility.

```mermaid
flowchart LR
    A["Team A<br/>Operations"] -->|coordination| B["Bridge Role<br/>Knowledge routing"]
    B -->|dependency routing| C["Team C<br/>Continuity"]
    B -->|specialist connection| D["Team D<br/>Technical support"]
    B -->|holds| K["Tacit knowledge"]
    K -->|concentrated in one role| N["Low redundancy"]
```

## 5. State transition

OSI examines what changes when a role or relationship changes state.

```mermaid
flowchart LR
    subgraph A["State A · bridge active"]
        A1["Team A"] --> A2["Bridge Role"] --> A3["Continuity Work"]
        A2 --> A4["Technical Support"]
    end
    A -->|role vacancy / access loss| B
    subgraph B["State B · bridge unavailable"]
        B1["Team A"] -.-> B2["Fragmented route"]
        B2 -.-> B3["Continuity Work"]
        B4["Work accumulation"]
    end
```

## 6. Trust and flow

Trust is represented as a bounded condition connected to observable cooperation
and capability utilization.

```mermaid
flowchart LR
    F["Field condition<br/>Predictable handoffs"] -->|supports| T["Trust condition<br/>Information sharing"]
    T -->|enables| C["Cooperation<br/>Joint problem-solving"]
    C -->|supports| M["Mentoring / delegation"]
    M -->|makes possible| U["Capability utilization"]
```

## 7. Evidence provenance

Interpretations remain traceable through assurance to their source material.

```mermaid
flowchart LR
    S["Source document<br/>Synthetic project record"] -->|contains| E["Extracted evidence<br/>Coordinated continuity work"]
    E -->|passes through| A["Assurance result<br/>Accepted with limits"]
    A -->|bounds| I["Interpretation<br/>Supports continuity planning"]
    I -->|supports| C["Capability representation<br/>Continuity coordination"]
```

## 8. Congruence across ontologies

Participant and organizational concepts can relate without being collapsed.

```mermaid
flowchart LR
    subgraph PIA["PIA domain"]
        PC["Capability<br/>Continuity Coordination"]
        PE["Evidence<br/>Planning activity"] -->|supports| PC
    end
    subgraph OSI["OSI domain"]
        OC["Organizational condition<br/>Coordination capacity"]
        OF["Observed condition<br/>Decision pathway"] -->|informs| OC
    end
    PC -.->|bounded relation| X["Governed congruence mapping"]
    OC -.->|bounded relation| X
```

## 9. Assurance path

Graph objects are downstream of package validation and assurance.

```mermaid
flowchart LR
    P["Synthetic evidence package"] -->|submitted| V["Validation<br/>Schema, provenance, boundaries"]
    V -->|produces| R["Assurance report"]
    R -->|authorizes bounded projection| C["Certified projection manifest"]
    C -->|projects| G["Sandbox graph object"]
```

## 10. Knowledge lifecycle

The architecture can represent how knowledge is developed, tested, promoted,
and maintained.

```mermaid
flowchart LR
    Q["Research question<br/>Can governed knowledge develop?"] --> E["Experiment / evidence"]
    E --> C["Congruence review"] --> V["Validation"] --> P["Promotion decision"]
    P --> K["Canonical terminology"] --> S["Stewardship"]
    S -.->|feedback| Q
```

## 11. Governed cross-domain mapping

Individual and organizational knowledge can relate through explicit bounded
mappings while preserving domain boundaries.

```mermaid
flowchart LR
    PE["PIA evidence<br/>Participant-authorized experience"] -->|supports| PC["PIA capability<br/>Bounded interpretation"]
    OE["OSI observation<br/>Organizational condition"] -->|supports| OP["OSI pattern<br/>System relationship"]
    PC -.->|qualified relation| M["Governed cross-domain mapping"]
    OP -.->|qualified relation| M
```
