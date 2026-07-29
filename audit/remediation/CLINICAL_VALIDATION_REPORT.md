# Patient-level evaluation harness report

Evidence classification: **SIMULATION_ONLY_NOT_EXTERNAL_VALIDATION**

> This report verifies the evaluation pipeline. It does not establish clinical
> performance when `external_validation_eligible` is false.

## Provenance

- Source: `audit/data/patient_clinical_cohort.csv`
- SHA-256: `98ab1ac534c6945a3f3c5fbdd9cfdfb139676bd2f3e84c00ec7cc147038a7c12`
- Patients: 500
- Positive: 100
- Negative: 400
- External validation eligible: `false`

## Locked operating point

- Threshold: 0.5000
- TP/TN/FP/FN: 83/322/78/17
- Sensitivity: 0.830000
- Sensitivity Wilson 95% CI: [0.744520, 0.891064]
- Specificity: 0.805000
- Specificity Wilson 95% CI: [0.763348, 0.840849]
- AUROC: 0.931075
- AUPRC: 0.832583

## Interpretation boundary

These values describe deterministic simulated scores when the source records
are marked `SYNTHETIC_SIMULATION`. They must not be cited as malaria-model
accuracy, PCR validation, expert-microscopy validation, external validation,
regulatory evidence, or justification for clinical deployment.
