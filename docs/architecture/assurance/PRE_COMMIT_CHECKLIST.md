# Pre-Commit Review Checklist

## Architecture
- [ ] Eight dimensions and order are correct.
- [ ] `Finding` is the rule-to-report gate.
- [ ] `AssuranceResult` is the per-dimension object.
- [ ] `AssuranceReport` is the component-level record.
- [ ] `OSIComponent` is the required base interface.

## Behavior
- [ ] Severity-to-disposition mapping is correct.
- [ ] Overall disposition priority is correct.
- [ ] Consent handling is correct.
- [ ] Regression parity behavior is correct.
- [ ] Audit metadata is complete.
- [ ] Findings require traceability through reference or evidence.

## Compatibility
- [ ] `osi_pia_validate.py` remains the compatibility entry point.
- [ ] `CSVPackageValidator` remains a compatibility alias during transition.
- [ ] Legacy acceptance semantics are preserved.

## Documentation
- [ ] Normative requirements are distinguished from implementation notes.
- [ ] No unsupported behavior is described as implemented.
- [ ] Paths and versions are correct.
- [ ] Package is ready for `/architecture`.
