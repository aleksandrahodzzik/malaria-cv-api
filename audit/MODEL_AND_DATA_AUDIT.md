# Model and data audit

## Model

Historical identifier `trpakov/vit-malaria-classification` was not found in
the checked public author inventory or local Hugging Face cache. No model card,
license, weights, immutable revision, checksum, `id2label`, processor config or
training manifest was supplied.

Verdict: **STOP-SHIP / UNKNOWN performance**. Another model must not be
silently substituted.

## Intended task

Implemented input contract: pre-cropped individual cell classification.
Detection, segmentation, counting, slide aggregation, parasitemia and patient
diagnosis are absent.

## Data

Project training/evaluation data and patient/slide split manifest are absent.
NIH/NLM malaria data is a scientific reference, not proven provenance of the
missing model. Leakage, annotation quality, geography/device/stain/species
coverage and consent/license cannot be verified for the project artifact.

## Required acceptance package

- immutable model manifest and license decision;
- patient/slide/cell lineage and split;
- Datasheet and Model Card;
- duplicate/near-duplicate/augmentation leakage audit;
- external patient-level locked cohort;
- QC/OOD/subgroup/calibration evidence.

Detailed evidence: phases 5–10.
