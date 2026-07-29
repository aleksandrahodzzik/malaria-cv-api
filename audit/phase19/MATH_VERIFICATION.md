# Mathematical verification

Актуальная проверка: 2026-07-29.

```json
{"status":"PASS","recommendations_verified":16,"quality_weight_total":100.0,"quality_score":51.02,"risks_verified":12}
```

Проверено:

- `PriorityScore = I * U * E / sqrt(F * D)` для 16 рекомендаций;
- сумма Quality Score weights = 100;
- post-remediation Quality Score = 51.02;
- `AdjustedPriority = S * O * D * (2 - confidence)` для 12 рисков;
- Wilson interval unit tests для boundary и central cases.

95/100 не присвоено: математическая цель не может заменять отсутствующие
clinical/model/data evidence.
