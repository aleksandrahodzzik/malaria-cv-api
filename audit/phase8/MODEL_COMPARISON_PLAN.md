# Paired model comparison plan

## Preconditions

- same locked cases and reference labels;
- same analysis level;
- same exclusion/rejection policy;
- immutable artifacts;
- predefined primary comparator;
- predefined clinically meaningful margin.

## Tests

| Quantity | Method | Clustering |
|---|---|---|
| Paired correctness | exact McNemar | perform at intended independent unit |
| AUROC delta | DeLong | cluster-aware alternative/sensitivity analysis if needed |
| Sensitivity delta | paired cluster bootstrap | patient or slide cluster |
| Specificity delta | paired cluster bootstrap | patient or slide cluster |
| Calibration delta | paired cluster bootstrap | patient or slide cluster |
| Selective risk delta | paired bootstrap at fixed coverage | patient or slide cluster |

## Multiplicity

- one primary comparison;
- Holm or predefined FDR control for secondary models/endpoints;
- report raw and adjusted p-values;
- report effect sizes and CIs regardless of significance.

## Interpretation rule

```text
better =
  clinically meaningful delta
  + compatible confidence interval
  + no unacceptable safety/subgroup regression
  + passed provenance and calibration gates
```

A difference in the third decimal place is not sufficient.
