# Phases 6–8 implementation report

Дата: 2026-07-28

## Implemented

| Change | Purpose | Evidence |
|---|---|---|
| `/api/v1/methodology` | machine-readable intended task and pipeline gaps | API/OpenAPI tests |
| Expanded capabilities | prevent cell-to-patient semantic escalation | constant schema tests |
| Expanded prediction contract | exact task, level, review and unsupported uses | success/OpenAPI tests |
| UI scope acknowledgement | require pre-cropped single-cell declaration | disabled action and static regression |
| UI pipeline visualization | expose implemented/partial/missing/unvalidated stages | safe DOM construction |
| Offline validation module | deterministic statistical calculations | unit tests |
| Phase 6 audit | exact task/domain/pipeline assessment | five artifacts |
| Phase 7 audit | current/reference datasheets, leakage and bias gates | six artifacts |
| Phase 8 audit | SAP, prevalence, sample size, calibration and comparison | nine artifacts |

## Deliberately not implemented

- no replacement model;
- no synthetic validation dataset;
- no public patient-data validation endpoint;
- no patient diagnosis or parasitemia;
- no clinical threshold;
- no biological QC claim;
- no calibration artifact without calibration data;
- no DeLong result without paired predictions.

## Residual STOP-SHIP

1. Approved model artifact missing.
2. Current model dataset and split unknown.
3. Patient/slide lineage missing.
4. External validation absent.
5. Biological image QC absent.
6. Auth/global quota/load/Docker evidence incomplete.
7. Clinical workflow and regulatory path absent.

## Compatibility

All response additions are additive. Existing `diagnosis` alias remains
deprecated. Canonical `/api/v1/analyze` request remains one multipart file.
