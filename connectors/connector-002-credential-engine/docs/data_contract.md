# Connector 002 data contract

Connector 002 accepts the
`contract-pia-credential-lookup-json-001` request and returns bounded public
reference candidates under
`contract-pia-credential-resolution-linkage-json-001`.

The connector:

- calls only the allowlisted Credential Engine production or sandbox Search
  API endpoint;
- sends the API key only in the server-side authorization header;
- limits searches to ten primary-source credential results;
- requests no graph or description-set expansion;
- bounds the response size and text retained per field;
- fingerprints the query and each normalized candidate;
- preserves registry identity and publishing metadata when present;
- fails closed on authorization, rate, availability, size, type, or JSON
  errors;
- returns an empty participant-claims collection; and
- never installs a catalog definition.

Every candidate proceeds to independent Phase 3A public-definition review.
