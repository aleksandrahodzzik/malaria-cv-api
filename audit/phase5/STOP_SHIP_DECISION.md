# STOP-SHIP — model availability

Дата: 2026-07-28
Decision ID: `MODEL-STOP-SHIP-001`.

## Решение

```text
PUBLIC PRODUCTION INFERENCE = NO-GO
CLINICAL USE                = NO-GO
MODEL PERFORMANCE CLAIMS    = PROHIBITED
```

## Основание

1. Historical exact model ID не воспроизводится публично.
2. Public author list не содержит malaria repository.
3. Exact config, processor, weights и model card недоступны.
4. Real loader завершается `RepositoryNotFoundError/401`.
5. Локальный cache/weights отсутствуют.
6. License, revision, checksum, training data и metrics неизвестны.
7. Tests используют deterministic mock и не являются model evidence.

## Разрешённый режим

```text
research-only UI/API skeleton
synthetic/non-sensitive fixtures
mocked contract tests
health/readiness demonstrations
```

Запрещены:

- diagnosis или exclusion claims;
- patient decision support;
- performance/accuracy claims;
- подмена похожей моделью;
- deployment с implicit remote `main`;
- запуск неизвестного remote code/pickle.

## Exit criteria

STOP-SHIP может быть снят только если одновременно выполнены:

1. Approved model repository/storage определён.
2. Immutable revision/digest зафиксирован.
3. Все weights имеют проверенный SHA-256.
4. Safetensors load проходит без remote code.
5. License и право использования утверждены.
6. Model card и training/data provenance заполнены.
7. Exact preprocessing/label contract воспроизведён.
8. Clean-cache и offline smoke tests проходят.
9. External patient/slide-level validation выполнена для заявленного scope.
10. Calibration/OOD/abstention и clinical risk controls проверены.
