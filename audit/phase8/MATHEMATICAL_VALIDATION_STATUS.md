# Mathematical validation status

Дата: 2026-07-28

## Decision

```text
MODEL PERFORMANCE: NOT EXECUTED
REASON: INSUFFICIENT EVIDENCE
```

Отсутствуют:

- approved model artifact/SHA-256;
- locked cell/slide/patient validation cohort;
- reference labels;
- patient/slide cluster identifiers;
- raw scores;
- calibration split;
- predeclared operating threshold;
- intended-setting cost and prevalence.

Поэтому для текущей модели не вычислены и не выдуманы:

- confusion matrix;
- sensitivity/specificity;
- PPV/NPV;
- F1/MCC;
- AUROC/AUPRC;
- calibration;
- risk-coverage;
- subgroup metrics;
- clinical utility.

## Реализованный toolkit

`src.validation.statistics` предоставляет:

- validated confusion counts;
- threshold metrics с `None` для undefined denominators;
- ROC/PR points и trapezoidal AUC;
- prevalence PPV/NPV transport;
- Wilson и exact Clopper-Pearson intervals;
- seeded patient/slide cluster bootstrap;
- Brier, NLL, ECE, reliability bins, calibration intercept/slope;
- maximum-softmax risk-coverage baseline;
- sample-size approximation with design effect;
- explicit expected-cost calculation;
- exact paired McNemar test.

Это вычислительная инфраструктура, а не доказательство качества модели.

## Unit of analysis gate

Текущий endpoint = cell-level. Slide/patient metrics невозможны, потому что:

- slide/patient IDs не принимаются и не создаются;
- sampling/aggregation отсутствуют;
- patient reference standard отсутствует.

Нельзя использовать число cell crops как размер patient cohort.

## CI gate

Wilson и Clopper-Pearson доступны для независимого unit count. Cluster bootstrap
использует whole-cluster resampling с replacement, seed `20260728` и default
`2000` resamples. Применение к текущей модели не выполнено из-за отсутствия
данных.
