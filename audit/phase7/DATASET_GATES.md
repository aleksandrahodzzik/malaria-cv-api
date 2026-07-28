# Dataset gates

| Gate | Current status | Blocking evidence |
|---|---|---|
| D1 Provenance | FAIL | exact model dataset/version/license absent |
| D2 Lineage | FAIL | patient/slide/FOV/crop manifest absent |
| D3 Split | FAIL | patient-isolated split not demonstrated |
| D4 Labels | FAIL | reference standard/adjudication absent |
| D5 Representativeness | FAIL | intended population and external sites absent |
| D6 Integrity | FAIL | checksums/duplicate/leakage audit absent |
| D7 Documentation | FAIL | current datasheet cannot be completed |

## Gate logic

```text
if D1 == FAIL or D2 == FAIL or D3 == FAIL:
    independent_performance = NOT_ESTABLISHED
    production_model = NO_GO
    clinical_use = NO_GO
```

Reference NIH/NLM resources improve future feasibility, but do not change the
current gate because model-to-dataset lineage is missing.
