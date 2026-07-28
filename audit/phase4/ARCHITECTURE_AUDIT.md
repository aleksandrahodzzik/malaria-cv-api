# Phase 4 — аудит программной архитектуры

Дата: 2026-07-28
Проверенная реализация: FastAPI/Starlette/Pillow/PyTorch service после
controlled remediation.

## Итог

Backend является качественным research-only каркасом с fail-closed модельным
контуром, bounded per-process inference и безопасным API error contract.
Он не является публично production-ready: approved model отсутствует, Docker
не собран, нет authentication/global rate limit и real-model capacity evidence.

## Execution path

```text
ASGI server
-> RequestTrackingMiddleware
-> LegacyRouteDeprecationMiddleware
-> RequestBodyLimitMiddleware
-> FastAPI routing/dependency injection
-> Starlette multipart parser / UploadFile spool
-> encoded file read limit
-> asyncio semaphore admission
-> asyncio.to_thread
   -> Pillow verify
   -> reopen / format, frame, mode, pixel checks
   -> load + RGB conversion
   -> AutoImageProcessor
   -> torch.inference_mode forward
   -> logits shape + id2label contract
   -> softmax
-> Pydantic response serialization
```

## FastAPI/ASGI

| Проверка | Результат | Evidence |
|---|---|---|
| Application factory | PASS | `create_application()` |
| Lifespan | PASS/PARTIAL | model load выполняется до request serving; real artifact отсутствует |
| Startup failure | PASS | процесс остаётся live, model state fail-closed |
| `/health` | PASS | не зависит от модели |
| `/ready` | PASS | 503 при отсутствии/ошибке модели |
| Response models | PASS | OpenAPI contract test |
| Stable errors | PASS | 404/422/413/415/500/503/504 |
| Internal error leakage | PASS | path/decoder detail не возвращаются клиенту |
| Canonical OpenAPI | PASS | legacy business aliases скрыты |
| Legacy migration | PASS | `Deprecation` + successor `Link` |
| Request ID | PASS | bounded ASCII pattern либо UUID4 |
| Log control characters | PASS/PARTIAL | request ID и filename очищены; full logging pipeline не fuzz-tested |
| CORS | PASS/PARTIAL | explicit origins; methods/headers ограничены; deployment origins не заданы |
| Latency | PASS | `perf_counter`, milliseconds, two decimals |
| Authentication | FAIL/OPEN | отсутствует |
| Global rate limit | FAIL/OPEN | отсутствует |

### Lifespan failure semantics

Если `MODEL_NAME=""`:

```text
classifier_service = None
model_error_code = model_not_configured
health = 200
ready = 503
analyze = 503
```

Если loader выбрасывает ошибку:

```text
load_model wraps -> RuntimeError
lifespan catches RuntimeError
model_error_code = model_initialization_failed
```

Такое поведение корректно для research UI и liveness, но контейнер без approved
artifact не должен считаться готовым inference deployment.

## Upload pipeline

Наблюдаемые границы:

```text
transport body =
  MAX_UPLOAD_SIZE_MB * 2^20
  + MAX_MULTIPART_OVERHEAD_BYTES

encoded file =
  MAX_UPLOAD_SIZE_MB * 2^20

decoded area =
  width * height <= MAX_IMAGE_PIXELS
```

`Starlette 1.3.1` использует:

```text
MultiPartParser.spool_max_size = 1,048,576
MultiPartParser.max_part_size  = 1,048,576
max_files default              = 1000
max_fields default             = 1000
```

Файлы больше 1 MiB переходят в `SpooledTemporaryFile` на временном диске.
Endpoint закрывает `UploadFile` в `finally`.

Filename extension сознательно не является trust boundary. Решение принимает
пара:

```text
declared MIME <-> Pillow decoded format
```

Это позволяет безопасно принять PNG с display filename `cell.jpg`, если
фактический multipart MIME — `image/png`; имя не используется для выбора
decoder или filesystem path.

Подробности: [UPLOAD_THREAT_MATRIX.md](UPLOAD_THREAT_MATRIX.md).

## Async/concurrency

Подтверждены разные утверждения:

```text
A event-loop offload                 = VERIFIED
B bounded queue wait                 = VERIFIED
C per-process compute admission      = VERIFIED
D cancellation capacity accounting  = VERIFIED
E production scalability            = UNKNOWN
```

Pillow decode, processor и PyTorch forward находятся внутри одного
`asyncio.to_thread`. Semaphore получает slot до создания worker task.

При request cancellation handler ждёт фактическое завершение native thread
перед release slot.

При execution timeout:

1. клиентский wait прекращается;
2. возвращается `504`;
3. native thread продолжает вычисление;
4. task сохраняется в strong-reference set;
5. semaphore освобождается callback только после фактического завершения.

Подробности: [CONCURRENCY_MODEL.md](CONCURRENCY_MODEL.md).

## Остаточные stop-ship риски

1. Нет approved model artifact.
2. Нет authentication/authorization.
3. Нет global rate limit/admission control перед multipart parser.
4. Нет reverse-proxy slow-upload/header/body timeouts.
5. Docker/Linux runtime не проверен.
6. Нет real-model latency, throughput, RSS и worker-count evidence.
7. Нет platform-specific hash-verified transitive lock; version constraints есть.
8. Нет clinical/data validation.

## Решение

```text
local research/no-model UI: CONDITIONAL GO
public inference production: NO-GO
clinical use: NO-GO
```
