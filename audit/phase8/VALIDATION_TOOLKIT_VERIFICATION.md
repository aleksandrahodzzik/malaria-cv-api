# Validation toolkit verification

Module: `src/validation/statistics.py`

## Covered calculations

| Functionality | Test evidence |
|---|---|
| Confusion matrix and core metrics | deterministic hand-checkable example |
| Undefined denominators | preserved as `None` |
| PPV/NPV prevalence transport | five required prevalence values |
| Wilson CI | published numerical reference value |
| Clopper-Pearson CI | exact numerical reference value and boundary cases |
| ROC/PR/AUC | perfect-ranking invariant |
| Brier/NLL/ECE | near-perfect probability example |
| Risk-coverage | confidence-order invariant |
| Cluster bootstrap | seeded repeatability and whole-cluster sampling |
| Sample size/design effect | algebraic invariant |
| Expected cost | explicit component sum and negative-cost rejection |
| McNemar | paired discordance count and exact p-value |
| Invalid inputs | empty, non-binary, NaN and length mismatch rejected |

## Numerical policies

- probabilities must be finite and within `[0, 1]`;
- metric denominators are never silently replaced;
- NLL clips only for numerical log safety;
- Clopper-Pearson is obtained by binomial-tail inversion;
- cluster bootstrap resamples whole cluster IDs with replacement;
- default bootstrap seed is `20260728`;
- calibration slope/intercept may be `None` under singular/separated data;
- curve AUC uses a declared trapezoidal convention.

## Scope

The toolkit is offline and does not expose patient-linked validation data
through the public API.
