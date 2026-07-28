# Security, reliability и performance audit

## 1. Trust boundaries

```text
Untrusted client
  -> network/reverse proxy [UNKNOWN]
  -> ASGI multipart parser
  -> upload buffer
  -> Pillow decoder
  -> Transformers processor
  -> PyTorch model
  -> response/logging

Build operator
  -> package indexes + base image registry + GitHub Actions
  -> container artifact

Runtime worker
  -> Hugging Face endpoint/cache
  -> mutable model/config files
```

Внешний gateway, WAF, identity provider, secrets manager и orchestrator не
представлены в репозитории. Их наличие классифицировано `UNKNOWN`, а не
`ABSENT`. Само приложение соответствующих controls не реализует.

## 2. Assets

- доступность inference API;
- целостность model weights и label mapping;
- конфиденциальность изображений и metadata;
- журналы и request identifiers;
- compute/RAM/disk/network budget;
- release credentials и CI supply chain;
- достоверность клинически интерпретируемого результата.

## 3. Threat model

| Threat | Вектор | Текущий control | Разрыв |
|---|---|---|---|
| Resource exhaustion | много параллельных uploads/inference | file/pixel limit | нет auth/rate/concurrency limit |
| Multipart/body DoS | большой/медленный body до app loop | chunk accumulator | нет доказанного proxy/server body/time limit |
| Decoder exploitation | crafted JPEG/PNG/WEBP | Pillow verify/load, version bound | нет fuzz corpus/advisory gate/sandbox |
| Decompression bomb | малый encoded, большой decoded | pixel area check | нет тестов около границы/многокадровых cases |
| Model supply-chain substitution | mutable HF name/revision | отсутствует | нет checksum/signature/offline artifact |
| Dependency compromise | mutable package/action/base tags | version ranges | нет lock/hash/SHA/SBOM/provenance |
| Information disclosure | backend exception | logging | exception возвращается клиенту |
| Log injection | `X-Request-ID`, filename | request ID logging | нет charset/length/structured sanitation |
| Unauthorized costly use | public `/analyze` | отсутствует | нет identity/quota/accounting |
| Model extraction/probing | массовые probability queries | все probabilities возвращаются | нет abuse detection/query budget |
| OOD unsafe output | arbitrary valid image | MIME/decode only | нет semantic quality/OOD/reject |
| Privacy leakage | specimen/patient image upload | не описано хранение | нет privacy policy/retention/PHI controls |

## 4. Findings

### Finding ID: S-001

Classification: `OBSERVED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: `/analyze` не требует identity и не имеет application-level rate
limit/quota/concurrency semaphore.

Impact: compute exhaustion, cost abuse, starvation health checks и model
probing.

Root cause: API boundary security architecture не определена.

Recommendation:

- аутентификация сервис-сервис или user/client identity;
- per-principal и global quotas;
- token bucket/leaky bucket rate policy;
- bounded inference queue;
- отдельный low-cost health path;
- 429/503 с `Retry-After`;
- audit trail без чувствительных payloads.

Acceptance criteria: unauthorized call получает 401/403; burst сверх
утверждённого budget получает 429; sustained abuse не выводит readiness и
latency за SLO.

### Finding ID: S-002

Classification: `INFERRED`  
Severity: `HIGH`  
Confidence: `MEDIUM-HIGH`

Evidence: application прекращает накопление после лимита, но `UploadFile`
возникает после multipart parsing/spooling. Reverse proxy policy неизвестна.

Impact: attacker расходует socket, temp disk, parser CPU и worker time до
application check.

Recommendation: enforce max request body и upload duration на earliest
boundary; ограничить temp filesystem; настроить connection/header/body
timeouts; проверить slowloris и incomplete multipart.

Acceptance criteria: wire-level oversized/slow request завершается до
полного body, temp usage и worker count остаются в budget.

### Finding ID: S-003

Classification: `OBSERVED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: model и processor скачиваются по mutable name без revision/checksum.

Impact: drift, rollback ambiguity, compromised artifact, несовместимый
processor/labels.

Recommendation: build или controlled init step получает artifact по immutable
commit; manifest сверяет hashes; production runtime работает без публичного
egress; artifact сканируется и утверждается.

Acceptance criteria: изменение upstream `main` не меняет deployed model;
tampered file блокирует startup.

### Finding ID: S-004

Classification: `OBSERVED`  
Severity: `MEDIUM`  
Confidence: `HIGH`

Evidence: произвольный `X-Request-ID` сохраняется в state, log и response.

Impact: log forging, oversized logs/headers, correlation collision.

Recommendation: принимать только bounded pattern, например UUID/ULID
ASCII длиной до 64; отдельно хранить `client_request_id`, всегда генерировать
server trace ID; использовать structured logging.

Acceptance criteria: CR/LF, Unicode controls и oversized IDs отклоняются или
заменяются; log records остаются однострочными и parseable.

### Finding ID: S-005

Classification: `OBSERVED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: нет dependency audit, container scan, SBOM, secret scan и artifact
signature в CI.

Impact: известные CVE, лицензии и подмена supply chain не блокируют release.

Recommendation: внедрить risk-based policy с SLA remediation, VEX для
неприменимых CVE, CycloneDX/SPDX SBOM, secret scanning, SLSA-compatible
provenance и signing.

Acceptance criteria: policy breach блокирует merge/release; исключение имеет
owner, rationale и expiry.

## 5. Reliability model

### 5.1. Capacity

Минимальная модель:

```text
service_rate_per_worker μ ≈ 1 / mean_service_time
offered_load a = λ / μ
utilization ρ = λ / (c·μ)
```

Где `λ` — arrival rate, `c` — реально параллельные inference slots. Для
низкой tail latency нельзя проектировать систему у `ρ ≈ 1`. `to_thread()` не
создаёт бесплатную параллельность: CPU-bound PyTorch и memory bandwidth
остаются ограниченными, а число threads требует явного контроля.

Memory budget:

```text
RAM_required =
  workers · (model_RSS + framework_overhead)
  + concurrent_requests · (encoded_buffer + decoded_image + tensors)
  + cache + OS_headroom
```

Параметры сейчас не измерены, поэтому throughput и safe worker count
`UNKNOWN`.

### 5.2. Failure modes

- HF unavailable при cold start;
- partial/corrupt cache;
- одновременно стартующие workers;
- OOM kill;
- threadpool saturation;
- client disconnect во время inference;
- slow decode;
- disk pressure от temp uploads/cache;
- invalid model config;
- graceful shutdown во время запроса;
- readiness flapping.

Для каждого нужны injected failure test и recovery expectation.

## 6. Performance validation plan

### 6.1. До теста

Зафиксировать:

- model SHA, CPU/GPU, cores, RAM;
- container digest;
- worker/thread settings;
- input distribution по encoded size и resolution;
- warm/cold state;
- SLO и error budget.

### 6.2. Сценарии

1. Cold start из empty approved artifact store.
2. Warm single request.
3. Step load до saturation.
4. Spike.
5. 1–4 hour soak.
6. Mixed valid/invalid/oversize traffic.
7. Slow upload and disconnect.
8. Model/provider unavailable.
9. Worker restart and rolling deployment.

### 6.3. Метрики

- RPS/throughput;
- latency p50/p95/p99/max;
- queue time и inference time отдельно;
- HTTP 4xx/5xx/timeout rates;
- CPU, RSS, peak RSS, threads;
- temp disk/cache/network;
- startup/readiness duration;
- reject/abstention/OOD rates;
- per-input-size stratification.

### 6.4. Acceptance

Численные targets должен утвердить владелец продукта/SRE. Нельзя выдумывать
их в аудите. Минимально:

- ни одного OOM;
- memory plateau в soak;
- bounded queue;
- контролируемая деградация;
- readiness не сообщает ready до полного artifact verification;
- liveness не убивает здоровый, но медленный worker;
- error response не раскрывает internals.

## 7. Observability

Текущие request ID и latency headers полезны, но недостаточны.

Добавить:

- structured logs;
- OpenTelemetry traces;
- RED metrics для HTTP;
- model load duration/status;
- queue/inference/decode timings;
- resource saturation;
- input quality/OOD/abstention aggregates без raw patient data;
- model revision в operational metadata;
- alerts/runbooks/rollback.

Нельзя логировать raw images, filenames с PHI или полный payload по
умолчанию. Retention и access должны быть формально определены.

## 8. Security Definition of Done

- threat model reviewed;
- auth/rate/quota/body/time/concurrency controls tested;
- decoder fuzz corpus проходит;
- supply chain immutable и attested;
- secrets/PHI не попадают в logs/errors;
- SBOM/license/CVE policy применяется;
- container запускается least privilege, с resource limits и ограниченным
  egress;
- incident response и rollback rehearsed;
- penetration test выполнен перед публичным/клиническим использованием.
