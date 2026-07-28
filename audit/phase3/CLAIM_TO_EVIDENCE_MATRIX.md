# Phase 3 — Claim-to-Evidence Matrix

Дата проверки: 2026-07-28
Срезы: исходный `HEAD=09c24d7` и текущее рабочее состояние после remediation.

## Правило интерпретации

Marketing text, badge, docstring, комментарий и mocked unit test не считались
доказательством production-, performance- или clinical-готовности.

Полная машинно-читаемая таблица: [CLAIM_TO_EVIDENCE_MATRIX.csv](CLAIM_TO_EVIDENCE_MATRIX.csv).

| Claim ID | Заявление | Источник | Проверка | Результат | Вердикт |
|---|---|---|---|---|---|
| H-001 | production-ready | historical README | clean start и release gates | model/release evidence отсутствует | CONTRADICTED |
| H-002 | high-performance | historical README | SLO/load test inventory | SLO и benchmark отсутствуют | UNSUPPORTED |
| H-003 | MedTech API | historical README | intended use/clinical evidence | clinical validation отсутствует | CONTRADICTED |
| H-004 | rapid classification | historical README | real-model benchmark | model отсутствует | NOT_TESTABLE_WITH_CURRENT_EVIDENCE |
| H-005 | публичная malaria-модель `trpakov/...` | historical config/README | HF API/profile/files/loader | 401; public author list не содержит repo; loader exit 1 | CONTRADICTED |
| H-006 | `to_thread` = non-blocking inference | historical README | sync boundary inspection | event-loop offload доказан, scale — нет | PARTIALLY_SUPPORTED |
| H-007 | выдерживает concurrent production load | historical README | load evidence | не выполнялось | UNSUPPORTED |
| H-008 | lifespan предотвращает cold start | historical README | startup path | preload есть, artifact-backed timing нет | PARTIALLY_SUPPORTED |
| H-009 | request IDs | historical README | API tests | работает и валидируется | SUPPORTED |
| H-010 | latency milliseconds | historical README | clock/header inspection | monotonic ms header | SUPPORTED |
| H-011 | strict comprehensive validation | historical README | adversarial matrix | baseline не покрывал format/multiframe/modes | PARTIALLY_SUPPORTED |
| H-012 | security-hardened container | Docker/README | build/security scan | только static controls | UNSUPPORTED |
| H-013 | multi-stage non-root | Docker/README | static inspection | структура есть, build не выполнен | PARTIALLY_SUPPORTED |
| H-014 | automated CI gates | README/workflow | workflow + local equivalents | local pass; remote run pending | PARTIALLY_SUPPORTED |
| H-015 | `/ready` сразу ready | historical README | real loader | loader failure и 503 | CONTRADICTED |
| H-016 | diagnosis/confidence как clinical probability | historical example | calibration/validation | доказательств нет, softmax uncalibrated | CONTRADICTED |
| H-017 | clinical client | historical diagram | intended use | current contract research-only | CONTRADICTED |
| H-018 | comprehensive tests | walkthrough | test inventory | ML path mocked | PARTIALLY_SUPPORTED |
| H-019 | microsecond latency | walkthrough | header/rounding | milliseconds, 0.01 ms rounding | UNSUPPORTED |
| H-020 | no request-time model load | lifespan comment | call graph | условно при доступном artifact | PARTIALLY_SUPPORTED |
| C-001 | research-only | README/schema/UI | contract tests | согласовано | SUPPORTED |
| C-002 | default model absent | config/env | effective settings | `MODEL_NAME=""` | SUPPORTED |
| C-003 | health 200 without model | README/routes | API test | 200 | SUPPORTED |
| C-004 | UI available without model | README/main | asset tests | 200 | SUPPORTED |
| C-005 | ready 503 without model | README/routes | API test | 503 + reason | SUPPORTED |
| C-006 | analyze 503 without model | README/DI | API test | fail-closed | SUPPORTED |
| C-007 | no fake runtime predictions | README/main | runtime search | runtime fallback отсутствует | SUPPORTED |
| C-008 | factory + lifespan | README/main | call graph | реализовано | SUPPORTED |
| C-009 | separate health/readiness | README/routes | semantic tests | реализовано | SUPPORTED |
| C-010 | JPEG/PNG/WEBP contract | README/code | adversarial images | MIME/magic/mode/frame validation | SUPPORTED |
| C-011 | byte/pixel limits | README/code | transport/file/pixel tests | три application boundaries | SUPPORTED |
| C-012 | Pillow verify before processor | README/code | corrupt fixture | подтверждено | SUPPORTED |
| C-013 | sync pipeline off event loop | README/code | boundary/cancellation tests | весь sync pipeline в worker | SUPPORTED |
| C-014 | per-process bounded concurrency | README/code | queue/cancel tests | semaphore accounting корректно | SUPPORTED |
| C-015 | fail-closed labels | README/code | inverted label test | отклоняется | SUPPORTED |
| C-016 | safe error envelope | README/errors | error tests | internal details скрыты | SUPPORTED |
| C-017 | validated request ID | README/middleware | adversarial IDs | unsafe заменяется | SUPPORTED |
| C-018 | security headers | README/middleware | header tests | headers есть, hardening целиком не доказан | PARTIALLY_SUPPORTED |
| C-019 | responsive UI | README/CSS | static inspection | browser visual test отсутствует | PARTIALLY_SUPPORTED |
| C-020 | non-root multi-stage Docker | README/Docker | static inspection | build/runtime не выполнены | PARTIALLY_SUPPORTED |
| C-021 | quality gates | README/CI | local gate | проходят | SUPPORTED |
| C-022 | drag-drop/cancel UI | README/JS | static + syntax | browser interaction pending | PARTIALLY_SUPPORTED |
| C-023 | real-model UI result | README/JS | artifact E2E | model отсутствует | NOT_TESTABLE_WITH_CURRENT_EVIDENCE |
| C-024 | uncalibrated softmax semantics | README/schema | schema/inference tests | `calibrated=false` | SUPPORTED |

## Количественная оценка

Использованы веса:

```text
VerdictWeight:
SUPPORTED=1.0
PARTIALLY_SUPPORTED=0.5
NOT_TESTABLE_WITH_CURRENT_EVIDENCE=0.25
UNSUPPORTED=0
CONTRADICTED=0

RiskWeight:
LOW=1
MEDIUM=2
HIGH=4
CRITICAL=8
```

Числа рассчитываются из CSV и фиксируются в
[`CLAIM_COVERAGE_METRICS.md`](CLAIM_COVERAGE_METRICS.md).

## Главный вывод

Historical marketing слой был существенно сильнее доказательств: критические
claims о production, MedTech, clinical readiness и конкретной модели
противоречат воспроизводимым наблюдениям. Текущая документация значительно
точнее: она fail-closed, отделяет исследовательский cell-level score от диагноза
и явно перечисляет непроверенные слои.
