# Dataset Datasheet — текущая модель

Дата: 2026-07-28
Объект: training/calibration/validation data для текущего model artifact.

## Итог

Текущий dataset **не идентифицирован**. В репозитории нет:

- approved model artifact;
- model card;
- dataset name/version/checksum;
- training manifest;
- split manifest;
- patient/slide lineage;
- prediction table;
- calibration split;
- external validation cohort.

NIH/NLM public data нельзя автоматически считать training data текущей модели.

| Field | Value | Status | Evidence | Limitation |
|---|---|---|---|---|
| Exact dataset | unknown | UNKNOWN | model provenance audit | no model card |
| Dataset version | unknown | UNKNOWN | no manifest | reproducibility absent |
| Consent/IRB | unknown | UNKNOWN | no lineage | cannot transfer from reference data |
| De-identification | unknown | UNKNOWN | no dataset | privacy status unknown |
| License | unknown | UNKNOWN | no dataset record | commercial use blocked |
| Patients | unknown | UNKNOWN | no manifest | patient-level CI impossible |
| Slides | unknown | UNKNOWN | no manifest | slide independence unknown |
| Cells | unknown | UNKNOWN | no manifest | class balance unknown |
| Geography/site | unknown | UNKNOWN | no model card | domain applicability unknown |
| Equipment/stain | unknown | UNKNOWN | no model card | acquisition mismatch unknown |
| Species/stages | unknown | UNKNOWN | no model card | target definition unknown |
| Annotation | unknown | UNKNOWN | no protocol | label validity unknown |
| Split level | unknown | UNKNOWN | no split manifest | leakage cannot be excluded |
| Duplicates | not executed | UNKNOWN | data unavailable | leakage audit impossible |
| Class balance | unknown | UNKNOWN | data unavailable | accuracy uninterpretable |
| Subgroups | unknown | UNKNOWN | no metadata | fairness/generalization unknown |

## Gate

```text
D1 Provenance = FAIL
D2 Lineage = FAIL
D3 Patient-isolated split = FAIL
D4 Labels = FAIL
D5 Representativeness = FAIL
D6 Integrity = FAIL
D7 Documentation = FAIL
```

Решение: model performance и clinical generalization не установлены.
