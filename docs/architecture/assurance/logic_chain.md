# Logic Chain Standard

Version: **Pre-1.0 normative draft**

## Definition

```text
Evidence → Observation → Interpretation → Inference → Conclusion → Recommendation
```

Low-level rules may use fewer semantic stages, but each Finding must show how input became a result.

## Minimum implementation

1. what was read or observed
2. what rule or condition was evaluated
3. what determination was made
4. what consequence followed

Example:

```text
Read participant consent status
Determine that consent is withdrawn
Apply the non-import consent boundary
Block package import
```

## Requirements

Logic Chains are non-empty, ordered, explicit about decision boundaries, preserve uncertainty, and remain attached to the Finding.

## Prohibited patterns

Do not provide only a conclusion, imply absent evidence, conceal judgment, or replace uncertainty with certainty.

Evidence is the basis. The Logic Chain explains what the component did with that basis.
