# Приоритизированный портфель рекомендаций

Дата среза: 2026-07-29.

## Правило порядка

Числовой `PriorityScore = I*U*E/sqrt(F*D)` используется только внутри
policy-класса. Итоговый порядок:

`STOP-SHIP > regulatory mandatory > patient safety > evidence enabler >
security/reliability > feature > optimization`.

Поэтому REC-004 с score 5.0 выше REC-010 с 6.67: первая закрывает отсутствие
patient-level evidence, а вторая — обязательный security baseline.

## Top-5

1. Утвердить model artifact, лицензию, revision, checksum и label/processor
   contract.
2. Утвердить intended purpose и поддерживать research-only claims.
3. Воспроизвести clean/offline end-to-end inference.
4. Построить patient-linked external validation.
5. Реализовать biological QC/OOD/reject до любого clinical workflow.

Полные проблема, решение, evidence, зависимости, effort, риски, acceptance и
measurement находятся в `PRIORITIZED_RECOMMENDATIONS.csv`.

## Ограничение

Score показывает порядок исследования/исполнения, но не вероятность успеха и
не обещание клинической пользы. Estimated effort — диапазон планирования,
который требуется уточнить после model/data decisions.
