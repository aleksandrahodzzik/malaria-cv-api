# Phase 8 variation report

## Review A — mathematical correctness

- Hand-calculated confusion matrix checked.
- Perfect-ranking ROC/PR AUC invariant checked.
- Required prevalence points checked against direct formulas.
- Wilson and Clopper-Pearson numerical references checked.
- Design effect and cost decomposition checked.

## Review B — boundary/adversarial inputs

- empty arrays rejected;
- length mismatch rejected;
- non-binary target rejected;
- NaN score rejected;
- negative costs rejected;
- undefined denominators remain explicit;
- exact CI handles 0/n and n/n boundaries.

## Review C — clinical interpretation

- no model metrics invented;
- illustrations labelled `HYPOTHETICAL_ONLY`;
- cell/slide/patient levels separated;
- patient diagnosis and parasitemia remain unsupported;
- calibration test leakage explicitly prohibited;
- MSP not described as epistemic uncertainty.

## Review D — reproducibility

- deterministic seed exposed;
- no new runtime dependency added;
- public API does not accept validation cohorts;
- source module and tests are included in normal lint/type/test gates.

Final command results are appended after the complete repository gate.

## Final repository gate

```text
Ruff format: PASS
Ruff lint: PASS
Mypy strict (src): PASS — 15 source files
Pytest: PASS — 64 tests
Coverage: PASS — 87.78%
JavaScript syntax: PASS
compileall: PASS
pip check: PASS
```
