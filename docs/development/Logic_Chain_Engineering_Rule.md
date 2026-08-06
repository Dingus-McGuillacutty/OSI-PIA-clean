# Logic Chain Engineering Rule

## Rule

Every significant OSI analytical output shall be explainable by following its Logic Chain back to originating evidence.

## A component must not

- silently rewrite source meaning;
- convert an inference into a fact;
- inflate confidence;
- erase uncertainty;
- discard provenance;
- hide an analytical transformation;
- or produce an untraceable recommendation.

## Minimum trace record

Each derived assertion should be able to carry or resolve:

- assertion identifier;
- assertion type;
- supporting evidence or assertion identifiers;
- transformation or rule identifier;
- confidence and confidence basis;
- unresolved uncertainty;
- component identifier and version;
- contract version;
- run identifier;
- timestamp;
- and reviewer or approval state when applicable.

## Review shorthand

> Follow the Logic Chain.

## Failure classification

- A broken Logic Chain is an **Epistemic Integrity failure**.
- An unverifiable Logic Chain is an **assurance failure**.
- A hidden Logic Chain is a **governance failure**.
