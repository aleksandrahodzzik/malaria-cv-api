# Технический аудит

## 1. Scope и метод

Проверены исходники `src/`, тесты, requirements, Dockerfile, Makefile,
GitHub Actions и README. Production-код не изменялся. Выполнялись только
безопасные локальные команды; Docker и Make отсутствовали в окружении.

Baseline:

- ОС: Windows NT 10.0.26200.0.
- Системный Python: 3.12.0.
- `.venv` Python: 3.12.0.
- pip: 26.1.2.
- Docker: `NOT_FOUND`.
- Make: `NOT_FOUND`.
- Git executable: доступен, но текущий `.git` не содержит рабочего
  репозитория.

Наблюдается несовпадение runtime-матрицы: локально Python 3.12, в CI и
Dockerfile — Python 3.11. Это не ошибка само по себе, но совместимость должна
проверяться явно.

## 2. Результаты воспроизводимых команд

| Проверка | Результат | Интерпретация |
|---|---|---|
| `pip check` | PASS | Текущий venv не имеет объявленных конфликтов |
| `ruff check src tests` | PASS | Статические style/lint правила проходят |
| `ruff format --check src tests` | PASS | 14 файлов соответствуют formatter |
| `mypy src` | PASS | Ошибок в 12 source files не найдено |
| `pytest --cov=src ... tests/` | PASS | 9 passed за 37.41 s |
| Coverage | 74% total | `inference.py` — 41%, критический ML path слабее всего |
| `compileall src tests` | PASS | Синтаксис/bytecode compilation проходят |
| Docker build/run | NOT EXECUTED | Docker отсутствует |
| Make targets | NOT EXECUTED | Make отсутствует |
| Real model load | FAIL/NOT REPRODUCIBLE | Model artifact отсутствует |

Покрытие по ключевым модулям:

- `src/api/dependencies.py`: 86%.
- `src/api/routes.py`: 83%.
- `src/core/middleware.py`: 83%.
- `src/main.py`: 83%.
- `src/services/inference.py`: 41%.

## 3. Архитектурная трассировка

Наблюдаемый путь:

```text
HTTP multipart upload
  -> content-type check
  -> chunked accumulation up to MAX_UPLOAD_SIZE_MB
  -> Pillow verify/open/load/RGB
  -> MAX_IMAGE_PIXELS
  -> AutoImageProcessor
  -> model forward under torch.no_grad()
  -> softmax
  -> id2label
  -> top class + all class probabilities
```

Сильные стороны:

- готовность отделена от liveness;
- модель загружается в lifespan, а не на каждый запрос;
- декодирование и PyTorch forward выполняются вне event loop;
- применён `torch.no_grad()` и `eval()`;
- есть проверка формата изображения и площади;
- CORS по умолчанию закрыт;
- API использует Pydantic response models.

Ограничения:

- нет ограничителя количества одновременно работающих inference threads;
- отсутствует явное device placement и resource policy;
- нет model revision/checksum;
- нет quality/OOD/abstention gate;
- результаты округляются до четырёх знаков до выбора/выдачи;
- fallback label mapping может скрыть дефект model config.

## 4. Подробные findings

### Finding ID: T-001

Classification: `OBSERVED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: `requirements.txt` использует широкие диапазоны; base image
`python:3.11-slim` не закреплён digest; pip обновляется до текущей версии.

Reproduction: открыть `requirements.txt` и Dockerfile.

Impact: две сборки из одного commit могут получить разные пакеты/base image и
поведение. Невозможна строгая аттестация.

Root cause: отсутствует воспроизводимый release dependency workflow.

Recommendation:

1. Ввести `requirements.lock` или эквивалент с transitive pins.
2. Генерировать hashes.
3. Закрепить base image по digest.
4. Разделить human-edited input constraints и generated lock.
5. Обновлять через контролируемые PR с тестами.

Acceptance criteria: clean build дважды создаёт функционально идентичный
environment; SBOM diff пуст кроме разрешённых metadata; все hashes
проверяются.

### Finding ID: T-002

Classification: `OBSERVED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: тестовая fixture подменяет `load_model`, а successful prediction
полностью создаётся `MagicMock`.

Reproduction: `tests/test_api.py`, fixtures `client` и
`mock_classifier_service`.

Impact: CI остаётся зелёным при несуществующей модели, неправильном
processor, перевёрнутых labels или несовместимых logits.

Root cause: unit contract tests не дополнены artifact-backed integration
tests.

Recommendation: сохранить быстрые mocked unit tests, но добавить:

- offline golden test с миниатюрным test artifact;
- release smoke test с утверждённой настоящей моделью;
- clean-cache model acquisition test;
- label/preprocessing contract test;
- negative test на mismatch числа logits и labels.

Acceptance criteria: намеренное изменение model revision или перестановка
labels ломает release gate.

### Finding ID: T-003

Classification: `OBSERVED`  
Severity: `MEDIUM`  
Confidence: `HIGH`

Evidence: `CONFIDENCE_THRESHOLD` существует только в конфигурации и не
используется в decision logic.

Impact: оператор может ошибочно считать, что низкоуверенные ответы
отфильтровываются.

Root cause: незавершённый конфигурационный контракт.

Recommendation: либо удалить параметр до реализации, либо формально определить
его семантику после калибровки: threshold не должен автоматически означать
порог инфекции без анализа costs/prevalence.

Acceptance criteria: configuration test доказывает изменение поведения;
OpenAPI и model card описывают `abstain` semantics.

### Finding ID: T-004

Classification: `OBSERVED`  
Severity: `MEDIUM`  
Confidence: `HIGH`

Evidence: internal exception string возвращается клиенту:
`Internal inference failure: {exc}`; аналогично для чтения upload.

Impact: раскрытие путей, имён backend-компонентов, provider errors и деталей
конфигурации; нестабильный внешний API.

Root cause: смешаны внутреннее журналирование и публичная ошибка.

Recommendation: логировать exception с request ID внутри, клиенту возвращать
стабильный код (`INFERENCE_FAILED`) и безопасное сообщение.

Acceptance criteria: тесты с искусственными секретами/путями в exception
показывают, что они отсутствуют в HTTP body.

### Finding ID: T-005

Classification: `OBSERVED`  
Severity: `MEDIUM`  
Confidence: `HIGH`

Evidence: schema `ErrorResponse` документируется, но стандартные
`HTTPException` ответы FastAPI имеют форму `{"detail": ...}` и не
гарантируют заявленные поля, включая request ID.

Impact: OpenAPI-контракт ошибки расходится с runtime; клиентские SDK могут
ломаться.

Root cause: отсутствует единый exception handler.

Recommendation: централизовать Problem Details-подобный формат с
`code/message/request_id`, не раскрывая internals.

Acceptance criteria: contract tests для 400/413/422/500/503 сравнивают
фактические ответы со схемой OpenAPI.

### Finding ID: T-006

Classification: `OBSERVED`  
Severity: `LOW`  
Confidence: `HIGH`

Evidence: одни и те же endpoints зарегистрированы в корне и под `/api/v1`.

Impact: удвоенная attack surface и неоднозначный lifecycle/versioning.

Root cause: обратная совместимость не описана.

Recommendation: выбрать canonical versioned path; root оставить только
health endpoints либо задокументированный redirect/deprecation.

Acceptance criteria: список маршрутов соответствует утверждённой API policy,
deprecated paths имеют срок удаления.

### Finding ID: T-007

Classification: `INFERRED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: Gunicorn запускает два worker; каждый процесс выполняет lifespan
load. Веса не baked в image.

Impact: удвоение RSS, параллельная загрузка модели, долгий/нестабильный startup
и возможное исчерпание диска/RAM.

Root cause: число workers выбрано без capacity model.

Recommendation: измерить один worker, затем выбрать topology:

- один model process и bounded concurrency;
- отдельный inference server;
- либо N workers только после доказанного memory budget.

Acceptance criteria:

```text
N_workers * RSS_peak_per_worker + OS_margin + request_buffers < memory_limit
```

с запасом не менее утверждённого SRE headroom; startup не зависит от
неограниченного внешнего egress.

### Finding ID: T-008

Classification: `OBSERVED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: CI не собирает контейнер, не выполняет реальную модель, не задаёт
coverage threshold, не запускает dependency/container/secret scanning;
GitHub Actions закреплены только major tags.

Impact: release artifact может отличаться от тестируемого окружения; supply
chain и regressions не блокируют merge.

Root cause: CI проверяет только code quality.

Recommendation: добавить release workflow:

1. lock verification;
2. lint/type/unit;
3. coverage floor;
4. artifact-backed smoke;
5. Docker build/run/readiness;
6. SBOM;
7. vulnerability, license и secret scans;
8. action pinning по full commit SHA;
9. image signing/provenance;
10. deploy только immutable digest.

Acceptance criteria: намеренно уязвимая dependency, отсутствующая модель,
неверный healthcheck или falling coverage блокируют pipeline.

### Finding ID: T-009

Classification: `OBSERVED`  
Severity: `MEDIUM`  
Confidence: `HIGH`

Evidence: `requirements-dev.txt` явно устанавливает `httpx2>=2.9.1`, но
Starlette `TestClient` использует отдельный пакет `httpx`. В текущем venv
установлены одновременно `httpx2==2.9.1` и `httpx==0.28.1`; `pip show`
указывает, что `httpx2` не имеет reverse dependencies.

Impact: лишний пакет и transitive dependency tree увеличивают supply-chain,
license и vulnerability surface, не участвуя в тестах.

Root cause: dev dependency не обоснована или выбрано неправильное имя пакета.

Recommendation: подтвердить назначение `httpx2`; если оно отсутствует —
удалить из input requirements и регенерировать lock. Явно закреплять тот
`httpx`, который совместим с TestClient.

Acceptance criteria: dependency graph содержит только используемые пакеты;
тесты проходят в чистом окружении; SBOM review не содержит необоснованный
`httpx2`.

## 5. API correctness и edge cases

Текущее тестирование подтверждает:

- 200 для liveness;
- 200/503 для readiness в mocked состояниях;
- 200 для mocked valid image;
- 400 для unsupported/missing MIME;
- 400 для empty body;
- 413 при превышении application accumulation limit;
- ValueError для очевидно повреждённого изображения.

Не подтверждено:

- реальный JPEG/PNG/WEBP через настоящий processor/model;
- image content не соответствует MIME;
- animated/multi-frame images;
- EXIF orientation/profile edge cases;
- truncated/crafted files и parser fuzz corpus;
- decompression bombs около порога;
- медленный upload, disconnect, cancellation и timeout;
- filename/header Unicode/control characters;
- одновременные запросы и thread saturation;
- 422 contract;
- duplicate endpoints parity;
- headers на необработанном exception;
- OpenAPI/error schema consistency.

## 6. Container и deployment

Положительно:

- multi-stage build;
- runtime без compiler toolchain;
- non-root UID/GID;
- `--no-install-recommends`;
- liveness HEALTHCHECK.

Разрывы:

- Docker не был собран в этой среде;
- base images mutable;
- модель не входит в artifact;
- healthcheck проверяет liveness, не readiness;
- нет read-only rootfs/capability/seccomp/resource examples;
- `curl` увеличивает runtime surface только ради healthcheck;
- нет signal/shutdown/startup validation;
- нет declared memory/CPU limits;
- нет TLS/network policy;
- нет image scan/signature/SBOM.

Локальный импорт Gunicorn worker на Windows падает из-за отсутствия Unix
модуля `fcntl`. Это ожидаемая платформенная несовместимость Gunicorn и не
считается доказательством ошибки Linux-контейнера; реальный Linux test
остался `NOT EXECUTED`.

## 7. Definition of Done для инженерной части

Инженерный gate можно считать пройденным только если:

- clean checkout + lock создаёт окружение без ручных действий;
- реальные model assets доступны по immutable идентификатору;
- Docker image собирается, стартует и становится ready без mutable network
  dependency;
- unit, integration, contract, security и load tests проходят;
- p95/p99, throughput, RSS и error rate измерены;
- публичные ошибки не раскрывают internals;
- auth, quotas, timeouts и body limits включены на подтверждённом deployment
  boundary;
- SBOM, vulnerability results, подпись и provenance привязаны к image digest.
