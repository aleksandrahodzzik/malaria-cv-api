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
- generic client/server error contracts.

## Gaps

- нет Prometheus/OpenTelemetry metrics/traces;
- нет dashboard, alert rules и error-budget automation;
- нет central audit-log retention policy;
- нет startup probe orchestration;
- нет circuit breaker для внешнего model registry;
- нет global edge rate limit/auth;
- нет queue-depth/system telemetry;
- deployment/container/model checksum не во всех runtime events.

Не добавлен публичный `/metrics`: без authentication/network boundary он может
раскрывать operational metadata. Метрики следует публиковать на отдельном
internal listener или защищённом collector channel.

## Finding

Finding ID: OBS-001

Classification: VERIFIED

Severity: High

Confidence: 0.95

Evidence: код логирования есть; exporter/alerts отсутствуют.

Impact: деградация модели/очереди может остаться незамеченной.

Recommendation: OpenTelemetry/Prometheus через internal boundary.

Acceptance criteria: versioned metric catalog, alert tests, dashboard,
retention/privacy review и runbook.
