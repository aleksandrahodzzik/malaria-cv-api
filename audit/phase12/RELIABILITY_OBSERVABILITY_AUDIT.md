# Фаза 12 — reliability и observability

## Verified

- privacy-conscious JSON logs с allowlist полей;
- request ID с bounded validation;
- duration, status, method и path;
- version в JSON и `X-Service-Version`;
- `/health` и model-aware `/ready`;
- inference semaphore, queue timeout и execution timeout;
- graceful application lifespan;
- `Cache-Control: no-store` для API;
- generic client/server error contracts;
- opt-in `/metrics` с отдельным `X-Metrics-Key`, fixed-label counters,
  duration histogram и active-request gauge;
- неизвестные raw paths нормализуются в `__unmatched__` в metrics и JSON logs.

## Gaps

- нет OpenTelemetry traces, внешней multi-worker агрегации metrics;
- нет dashboard, alert rules и error-budget automation;
- нет central audit-log retention policy;
- нет startup probe orchestration;
- нет circuit breaker для внешнего model registry;
- нет global edge rate limit/auth;
- нет queue-depth/system telemetry;
- deployment/container/model checksum не во всех runtime events.

Публичный анонимный `/metrics` не добавлен. Exporter выключен по умолчанию,
скрыт из OpenAPI и требует отдельный 32+ character `X-Metrics-Key`; production
deployment всё равно должен ограничить endpoint внутренней сетью или collector
channel.

## Finding

Finding ID: OBS-001

Classification: PARTIALLY REMEDIATED

Severity: High

Confidence: 0.95

Evidence: код логирования и защищённый in-process exporter есть; alerts,
dashboard и cross-worker aggregation отсутствуют.

Impact: деградация модели/очереди может остаться незамеченной.

Recommendation: OpenTelemetry/Prometheus через internal boundary.

Acceptance criteria: versioned metric catalog, alert tests, dashboard,
retention/privacy review и runbook.
