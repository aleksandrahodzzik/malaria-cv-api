# Data leakage audit

## Status

`NOT EXECUTED — DATA UNAVAILABLE`

No current training/test assets, patient IDs, slide IDs, split manifest or
embeddings are available.

## What can be concluded

- Leakage is possible and cannot be excluded.
- The current model has no reproducible validation claim.
- The presence of NLM patient mapping CSV files in the public index shows that
  patient-aware analysis is technically possible for that reference resource.
- It does not show that the unknown model used those mappings.

## Required execution order

1. Validate manifest and identifiers.
2. Compare exact SHA-256 across splits.
3. Compare source and crop lineage.
4. Detect perceptual near-duplicates.
5. Search embedding nearest neighbours with blinded threshold calibration.
6. Inspect metadata/acquisition clusters.
7. Search augmentation parent leakage.
8. Review suspicious clusters manually.
9. Rebuild patient-isolated split if any violation exists.
10. Lock and checksum the corrected split.

## STOP-SHIP conditions

- one patient in multiple splits;
- one slide/FOV/source image in multiple splits;
- augmented variant separated from parent;
- exact cross-split duplicate;
- unknown patient grouping for a claimed patient-level validation;
- test set used for calibration or threshold selection.

Perceptual or embedding similarity alone is a review signal, not automatic proof
of biological duplication.
