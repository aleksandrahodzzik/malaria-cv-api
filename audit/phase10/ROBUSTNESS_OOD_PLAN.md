# Фаза 10 — robustness, OOD и failure analysis

## Что реализовано

`src/validation/robustness.py` создаёт детерминированные offline-corruptions:
blur, brightness, contrast, JPEG, rotation, scale, crop shift, occlusion,
color cast и pixel noise. Severity ограничена диапазоном 0–5, seed по
умолчанию — `20260728`. Identity и determinism покрыты тестами.

Этот код не входит в production preprocessing и не изменяет вход пользователя.

## Что не выполнено

Model performance degradation, OOD AUROC/FPR95, risk-coverage curves, Grad-CAM
sanity checks и межцентровая robustness validation: **NOT EXECUTED**, поскольку
нет утверждённой доступной модели и размеченного независимого cohort.

## Locked protocol

1. Заморозить model SHA, preprocessing и cohort manifest.
2. Сохранить чистый baseline prediction для каждого случая.
3. Для каждой corruption family применить severity 1–5 с фиксированным seed.
4. Считать patient/slide-level delta Se, Sp, AUROC, AUPRC, ECE и reject rate.
5. Bootstrap проводить по patient/slide cluster, минимум 2000 resamples.
6. Строить performance-vs-severity с CI, не выбирать post hoc удобную severity.
7. Для non-blood/OOD набора считать AUROC, AUPRC, FPR95 и coverage-risk.
8. Ручной review ошибок вести вслепую к predicted label.
9. Изменение preprocessing после просмотра test failures требует нового test set.

## Safety rule

XAI heatmap — инструмент гипотез, не доказательство причинности или
клинической корректности. Любой XAI должен пройти parameter sensitivity,
randomization sanity checks и specialist review.
