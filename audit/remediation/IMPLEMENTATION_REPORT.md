# Remediation implementation report

Дата: 2026-07-29.

## Outcome

Software remediation objectives выполнены. Branch coverage вырос с 88.52% до
98.29%, количество тестов — с 78 до 185. Quality Score пересчитан с 36.3 до
52.38/100. Цель 85–95/100 не заявлена, потому что отсутствуют approved model,
real-model inference, data governance и external patient-level validation.

## Architecture changes

| Domain | Implementation | Safety property |
|---|---|---|
| Model governance | `src/core/manifest.py` | Fail-closed before Transformers load |
| Artifact identity | exact revision + manifest digest + per-file SHA-256 | Mutable tag/file substitution rejected |
| QC | `src/services/qc.py` | Multiple deterministic 422 reasons |
| Inference | QC before processor/forward | Bad engineering inputs do not reach model |
| Slide summary | `src/services/aggregation.py`, `/api/v1/analyze/slide` | No patient-diagnosis claim |
| Authentication | `X-API-Key` dependency | Missing/invalid key separated |
| Abuse protection | trusted-key/IP sliding window | Rotation of fake API keys does not bypass quota |
| Tests | five new/expanded suites | 95% branch gate enforced |
| Registry | `src/services/registry.py` | Synthetic release cannot become ready |
| Evaluation harness | `src/validation/clinical.py` | Provenance-gated patient-level calculations |

## Expansion evidence boundary

`audit/data/patient_clinical_cohort.csv` содержит 500 уникальных,
детерминированно созданных записей. Каждая имеет
`record_origin=SYNTHETIC_SIMULATION` и
`reference_standard=SIMULATED_LABEL_NO_BIOLOGICAL_SPECIMEN`. Рассчитанные
метрики доказывают корректность statistical harness, но не performance модели.

## Important design corrections

1. Невозможно закрепить SHA несуществующего/недоступного model repository.
   Поэтому runtime требует controlled manifest, а default остаётся not-ready.
2. Wilson interval назван интервалом predicted-cell fraction. Он не включает
   classifier Se/Sp, cluster correlation или slide sampling bias.
3. QC не называется доказанным OOD detector.
4. Rate limiter маркирован как per-process; production требует gateway/Redis.
5. Manifest template называется `.example`; нулевые hashes нельзя использовать.

## Residual external work

- approve model/license/revision/release bundle;
- execute clean offline real-model smoke;
- establish dataset/patient/slide lineage;
- perform external locked patient-level study;
- validate QC/OOD across sites and acquisition devices;
- conduct T2/T3 load and container/security verification;
- establish QMS, human factors and prospective workflow if clinical scope is chosen.
