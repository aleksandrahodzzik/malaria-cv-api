# Data lineage requirements

## Required hierarchy

```text
patient
  -> specimen
  -> slide
  -> field_of_view
  -> source_image
  -> cell_crop
  -> augmented_variant
  -> split
  -> locked_prediction
```

## Required manifest columns

```text
dataset_version
patient_id_pseudonymous
specimen_id
slide_id
field_id
source_image_id
crop_id
augmentation_parent_id
split
label
reference_standard
annotation_version
acquisition_site
device
stain
species
sha256
```

## Invariants

1. Direct identifiers are excluded.
2. Pseudonymous identifiers are stable inside the controlled study.
3. All descendants of a patient remain in one split.
4. Split is assigned before crop augmentation.
5. Test labels remain locked from model development.
6. Every prediction links to model SHA, code commit and source asset SHA.
7. Exclusions and failed decodes stay in the analysis ledger.

## Acceptance queries

```text
COUNT(DISTINCT split) GROUP BY patient_id_pseudonymous = 1
COUNT(DISTINCT split) GROUP BY slide_id = 1
COUNT(DISTINCT split) GROUP BY source_image_id = 1
COUNT(DISTINCT split) GROUP BY augmentation_parent_id = 1
COUNT(DISTINCT sha256, split) spanning splits = 0
```

No current manifest exists, therefore all queries are `NOT EXECUTED`.
