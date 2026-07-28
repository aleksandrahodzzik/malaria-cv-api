# Locked statistical analysis plan

## 1. Preconditions

До открытия test labels зафиксировать:

- intended use и analysis level;
- positive class;
- reference standard;
- eligibility/exclusions;
- model SHA-256;
- processor and calibration artifact SHA-256;
- dataset/split checksums;
- primary threshold and selection method;
- primary endpoints;
- minimum Se/Sp;
- missing/unreadable/rejected-case handling;
- subgroup hypotheses;
- seed `20260728`;
- code commit/container digest.

## 2. Cohorts

Отдельно:

1. training split;
2. calibration split;
3. internal validation;
4. locked patient-isolated test;
5. external site test;
6. prospective workflow cohort.

Test set не используется для calibration, threshold selection или feature
development.

## 3. Primary analysis

Primary estimands определяются intended use. Для research cell classifier:

- cell sensitivity и specificity at locked threshold;
- AUROC и AUPRC;
- F1, balanced accuracy, MCC;
- technical failure/reject rate;
- cluster-aware CI по patient/slide.

Для patient claim требуется отдельный validated aggregation pipeline и
patient-level estimands. Он сейчас отсутствует.

## 4. Confidence intervals

- Wilson и Clopper-Pearson как binomial sensitivity analysis.
- Primary uncertainty: patient/slide cluster bootstrap.
- 2000 resamples minimum; seed recorded.
- Report point estimate, 95% CI, independent unit count and cell count.
- Report unstable bootstrap samples and single-class clusters.

## 5. Discrimination curves

- ROC points over all unique thresholds.
- AUROC with CI.
- PR points and declared AUPRC convention.
- Operating point marked on both curves.
- Failed/rejected cases included in a separate intention-to-diagnose analysis.

## 6. Calibration

- Fit temperature, Platt and isotonic candidates on calibration split only.
- Choose method by predefined criterion.
- Evaluate Brier, NLL, ECE, slope/intercept and reliability on locked test.
- Store calibrator and checksum.
- Report binning scheme and confidence uncertainty.

## 7. Prevalence and utility

- Transport PPV/NPV to sourced prevalence range.
- Do not reinterpret transported values as prospective validation.
- Perform expected-cost sensitivity grid when expert costs are unknown.
- Decision-curve analysis only after a patient-level actionable use is defined.

## 8. Selective classification

- Baseline MSP, entropy and margin.
- Evaluate approved OOD/ensemble alternatives when available.
- Report risk-coverage and subgroup coverage.
- Rejected case escalates to defined human workflow.

## 9. Comparisons

- paired cases only;
- McNemar for binary errors;
- DeLong for correlated AUROC;
- cluster bootstrap delta Se/Sp;
- multiplicity correction;
- clinically meaningful margin;
- no winner claim from unpaired rounded metrics.

## 10. Reporting

Follow CLAIM/STARD-AI/TRIPOD+AI where applicable, without treating checklist
completion as performance evidence.
