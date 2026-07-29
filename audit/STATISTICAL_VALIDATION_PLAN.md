# Statistical validation plan — canonical

## Units

Report cell-, slide- and patient-level results separately. Primary clinical
analysis, if authorized, resamples patients; cells from one patient are not
independent observations.

## Locked analysis

1. Freeze intended purpose, model/preprocessing/calibration and cohort manifest.
2. Split by patient → slide → field → cell → augmented variant.
3. Fit/calibrate only on development/calibration partitions.
4. Keep test labels inaccessible until protocol/threshold lock.
5. Report confusion matrix, Se/Sp/PPV/NPV/F1/balanced accuracy/MCC,
   AUROC/AUPRC and 95% cluster-aware CI.
6. Transport PPV/NPV across prevalence and report calibration
   Brier/NLL/ECE/slope/intercept.
7. Optimize threshold via prespecified clinical loss/constraints.
8. Report risk-coverage, QC/OOD, subgroups and external-site degradation.
9. Compare paired models using McNemar/DeLong/cluster bootstrap as applicable.
10. Independent biostatistical review before claim.

Current status: toolkit VERIFIED; model predictions/cohort analysis
**NOT EXECUTED**. Full protocol: phase8 and phase9.
