# Фаза 13 — STRIDE threat model

Дата: 2026-07-28. Scope: API, uploads, model artifact, CI/container, logs.

| STRIDE | Concrete scenario | Asset | Existing control | Residual risk |
|---|---|---|---|---|
| Spoofing | Анонимный клиент выдаёт себя за лабораторного оператора | Results/workflow | Нет clinical claim | High: authentication absent |
| Tampering | Mutable remote model меняет weights/labels | Model/result | revision required for production remote model | High: approved artifact absent |
| Repudiation | Оператор отрицает выполненный анализ | Audit trail | request ID/event logs | High: no identity/signature/retention |
| Information disclosure | Filename/exception содержит patient/path data | Privacy/logs | filename/error text removed from logs | Medium: deployment logging unverified |
| Denial of service | Concurrent image bombs exhaust decode RAM | Availability | body/pixel limits, semaphore | High: no edge rate/resource limits |
| Elevation of privilege | Compromised dependency/action executes in CI | Source/secrets | read-only permissions, SHA-pinned actions | Medium/High: dependency hashes incomplete |

## Trust boundaries

1. Internet client → reverse proxy/API.
2. Multipart bytes → image decoder.
3. Application → local/remote model registry.
4. CI runner → package registries/actions.
5. Container → host/kernel.
6. Logs/metrics → telemetry backend.

## Privacy

Images must be treated as potentially sensitive health data even when direct
identifiers are absent. Purpose limitation, legal basis, retention, deletion,
data-subject rights, processor agreements, region/transfer and breach response
remain deployment-owner obligations. Ни одно изображение не отправляется
внешнему сервису текущим route-кодом; remote model download при startup является
отдельным egress, не передачей image payload.
