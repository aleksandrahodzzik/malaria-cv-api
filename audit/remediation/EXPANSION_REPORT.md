# Sealed registry and simulation harness expansion

Дата: 2026-07-29.

## Outcome

Реализованы два независимых контура:

1. `SealedModelRegistry` для настоящего immutable release.
2. `SyntheticTestRegistry` и patient-level simulation harness только для
   software/statistical verification.

Их evidence scope намеренно не смешивается.

## Registry contract

| Provider | Artifact verified | Serving permitted | Evidence scope |
|---|---:|---:|---|
| Sealed manifest registry | true после всех checks | true | software artifact integrity |
| Synthetic test registry | false | false | simulation only |

`/ready=200` требует загруженные processor/model и serving-eligible resolution.
Response публикует revision, manifest digest и registry kind, но не раскрывает
локальный filesystem path.

## Simulated cohort

- 500 уникальных patient IDs;
- 500 уникальных slide IDs;
- 100 simulated positives;
- 400 simulated negatives;
- deterministic seed `20260729`;
- CSV SHA-256:
  `98ab1ac534c6945a3f3c5fbdd9cfdfb139676bd2f3e84c00ec7cc147038a7c12`;
- `record_origin=SYNTHETIC_SIMULATION`;
- `reference_standard=SIMULATED_LABEL_NO_BIOLOGICAL_SPECIMEN`;
- `external_validation_eligible=false`.

Рассчитанные числа проверяют confusion-matrix, Wilson, ROC и PR pipeline.
Они не являются malaria-model performance или clinical evidence.

## Score impact

Quality Score повышен с 51.02 до **52.38/100** за registry architecture,
reproducibility, testing и documentation. Категории clinical/model evidence и
реального data governance не повышались.

## Safety gates

| Gate | Status | Reason |
|---|---|---|
| G0 approved model | FAIL | Release bundle отсутствует |
| G1 real end-to-end inference | FAIL | Synthetic engine не является моделью |
| G2 external validation | FAIL | Cohort полностью simulated |
| G3 safe rejection | PARTIAL | Engineering QC без external validation |
| G4 baseline security | PARTIAL | Per-process quota без gateway deployment |

## Counterfactual review

Primary hypothesis: generated 500-row cohort closes patient validation.

Alternative: it validates only file/statistical contracts.

Discriminating test: inspect `record_origin`, `reference_standard` and
`external_validation_eligible`.

Observed result: every row is synthetic and the report explicitly rejects the
external-evidence classification.

Primary hypothesis: deterministic synthetic scores are offline model weights.

Alternative: they are hash-derived software fixtures.

Discriminating test: inspect `SyntheticTestRegistry`.

Observed result: it has no model root/manifest and returns
`serving_permitted=false`.
