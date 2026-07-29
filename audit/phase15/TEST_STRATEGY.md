# Фаза 15 — test strategy

## Слои

1. Unit: конфигурация, decoder, aggregation/statistics/capacity/robustness.
2. API contract: status/schema/headers/error codes/deprecation.
3. Integration: multipart → decode → service boundary.
4. Real-model smoke: immutable model manifest, label/preprocessor parity.
5. Model regression: locked golden cohort и tolerances.
6. Security: bombs, spoofing, logs, headers, dependencies.
7. Property-based: sizes/modes/corruptions/invalid numeric parameters.
8. Load: T2/T3 concurrency, RSS, timeouts, recovery.
9. Resilience: model load failure, cancellation, worker kill, disk/network fault.
10. End-to-end: acquisition → review → audit trail на representative setting.

## Правила

- Mocks подтверждают software contract, но не существование/качество модели.
- Golden image фиксируется hash; model/preprocessor/calibration — immutable SHA.
- Floating point сравнивается tolerance и task-level invariant, не `==`.
- Patient/slide cases нельзя дробить между train/calibration/test.
- Model metric regression gate работает на untouched external/locked set.
- Security и overload tests должны проверять bounded resources, не только status.

## Current assessment

Сильны API/unit/static typing/CI. Отсутствуют real-model, external model
regression, Docker, sustained load, resilience и clinical E2E tests.
