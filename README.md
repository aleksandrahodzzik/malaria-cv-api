# Malaria Cell Classification API

Исследовательский web/API-прототип для классификации заранее выделенного
изображения отдельной клетки крови.

> [!WARNING]
> Сервис не является медицинским изделием, не ставит диагноз пациенту, не
> исключает малярию и не предназначен для выбора лечения. Softmax-score не
> является калиброванной вероятностью правильного результата.

## Текущее состояние

Backend, UI и тестовый HTTP-контур реализованы. Утверждённая ML-модель в
репозиторий не входит и по умолчанию не настроена. Поэтому после чистого
запуска:

- `/health` возвращает `200`;
- UI доступен на `/`;
- `/ready` возвращает `503` с `reason=model_not_configured`;
- `/analyze` возвращает `503`, пока не предоставлен проверенный model artifact.

Такое поведение намеренно: приложение не подменяет отсутствующую модель и не
делает фиктивные predictions.

## Возможности

- FastAPI application factory и lifespan;
- разделённые liveness/readiness probes;
- JPEG/PNG/WEBP upload;
- encoded-size и decoded-pixel limits;
- MIME-to-decoded-format, single-frame и image-mode validation;
- Pillow verification до processor;
- PyTorch inference вне event loop;
- bounded inference concurrency на процесс;
- queue и execution timeouts с корректным учётом native worker;
- fail-closed проверка `id2label`;
- обязательные `safetensors` и запрет remote code;
- централизованный error envelope;
- валидируемый `X-Request-ID`;
- security headers;
- dependency-free responsive UI;
- machine-readable intended-use and pipeline boundaries;
- explicit pre-cropped-cell acknowledgement in UI;
- offline statistical validation toolkit;
- non-root multi-stage Docker image;
- Ruff, Mypy, Pytest и coverage gate.

## UI

После запуска откройте:

```text
http://localhost:8000/
```

Интерфейс:

- показывает readiness модели;
- локально проверяет тип и размер файла;
- отображает preview без сохранения истории;
- поддерживает drag-and-drop и отмену запроса;
- выводит model class и score;
- требует подтверждения, что input является одной заранее вырезанной клеткой;
- показывает реализованные, отсутствующие и невалидированные звенья pipeline;
- явно сообщает ограничения и research-only назначение.

API documentation:

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI: `http://localhost:8000/openapi.json`

## Быстрый запуск

### Требования

- Python 3.11 или 3.12;
- локальный утверждённый model artifact для настоящего инференса;
- Docker — опционально.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-bootstrap.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

### Linux/macOS

```bash
python -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-bootstrap.txt
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
.venv/bin/python -m uvicorn src.main:app --reload
```

Без `MODEL_NAME` UI и health endpoints работают, но inference остаётся
fail-closed.

## Конфигурация модели

Не указывайте случайную публичную модель. До настройки должны быть проверены:

- лицензия;
- model card;
- training/evaluation provenance;
- immutable revision/checksum;
- preprocessing;
- число logits;
- точный порядок labels;
- external performance и limitations.

Пример для утверждённого локального artifact:

```dotenv
MODEL_NAME=C:\models\approved-malaria-cell-model
MODEL_LOCAL_FILES_ONLY=true
MODEL_EXPECTED_LABELS=["Parasitized","Uninfected"]
```

Пример для проверенного Hugging Face repository:

```dotenv
MODEL_NAME=organization/approved-malaria-cell-model
MODEL_REVISION=0123456789abcdef0123456789abcdef01234567
MODEL_LOCAL_FILES_ONLY=false
MODEL_EXPECTED_LABELS=["Parasitized","Uninfected"]
```

Для production рекомендуется заранее получить artifact, проверить hashes и
запускать с `MODEL_LOCAL_FILES_ONLY=true`.

Полный пример находится в [.env.example](.env.example).

## API

Канонические versioned endpoints:

| Method | Path | Назначение |
|---|---|---|
| GET | `/api/v1/health` | liveness |
| GET | `/api/v1/ready` | readiness модели |
| GET | `/api/v1/capabilities` | публичные limits/metadata |
| GET | `/api/v1/methodology` | exact task и границы pipeline |
| POST | `/api/v1/analyze` | research-only cell classification |

Для совместимости те же endpoints пока доступны без `/api/v1`.
Legacy `/ready`, `/capabilities` и `/analyze` исключены из canonical OpenAPI и
возвращают `Deprecation: true` вместе с `Link` на versioned successor.

### Capabilities

```bash
curl http://localhost:8000/api/v1/capabilities
```

Пример:

```json
{
  "api_version": "1.2.0",
  "intended_use": "research_only",
  "task": "pre_cropped_single_cell_classification",
  "analysis_level": "cell",
  "model_configured": false,
  "accepted_content_types": [
    "image/jpeg",
    "image/png",
    "image/webp"
  ],
  "max_upload_size_mb": 10,
  "max_image_pixels": 25000000,
  "probabilities_calibrated": false,
  "patient_diagnosis_supported": false,
  "slide_aggregation_supported": false,
  "parasitemia_supported": false,
  "human_review_required": true
}
```

### Methodology

`GET /api/v1/methodology` возвращает машиночитаемую цепочку:

```text
input -> technical QC -> detection/segmentation -> cell classification
      -> slide aggregation -> patient interpretation -> human review
      -> clinical action
```

Реализованный software scope ограничен техническим приёмом изображения и
research-only классификацией одной заранее вырезанной клетки. Biological
quality control, detection, slide/patient aggregation и clinical action
отсутствуют или не валидированы.

### Readiness без модели

```json
{
  "status": "not_ready",
  "model_loaded": false,
  "model_name": null,
  "reason": "model_not_configured"
}
```

### Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "accept: application/json" \
  -F "file=@cell.png;type=image/png"
```

Успешный ответ содержит:

- `predicted_cell_class` — основной безопасный термин;
- `diagnosis` — deprecated compatibility alias, не диагноз пациента;
- `confidence` — некалиброванный softmax-score;
- `probabilities` — scores всех классов;
- `calibrated=false`;
- `intended_use=research_only`;
- `task=pre_cropped_single_cell_classification`;
- `analysis_level=cell`;
- `human_review_required=true`;
- `patient_diagnosis_supported=false`;
- `parasitemia_supported=false`;
- обязательные limitations.

## Offline statistical validation

Модуль `src.validation.statistics` реализует проверяемые расчёты для будущего
locked validation cohort:

- confusion matrix и threshold metrics;
- ROC/PR curve points и AUC;
- Wilson и exact Clopper–Pearson intervals;
- prevalence transport для PPV/NPV;
- seeded patient/slide cluster bootstrap;
- Brier, NLL, ECE и reliability bins;
- risk–coverage baseline;
- sample-size approximation с design effect;
- expected-cost и exact McNemar.

Наличие toolkit не является валидацией текущей модели. Без approved model,
patient-linked данных и locked test predictions все model performance metrics
остаются `NOT EXECUTED`.

### Error envelope

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "detail": "The approved model is not configured, loaded, or ready.",
  "request_id": "d78d9ea1-7c4a-41f2-9e71-f06831ad665d"
}
```

Внутренние исключения не возвращаются клиенту.

## Проверки

С Make:

```bash
make lint
make test
make check
```

Напрямую в Windows:

```powershell
.\.venv\Scripts\python.exe -m ruff format --check src tests
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80 tests
.\.venv\Scripts\python.exe -m pip check
```

Mocked unit/API tests не считаются доказательством реальной ML-модели.
Artifact-backed smoke test должен быть отдельным release gate.

## Docker

```bash
docker build -t malaria-cv-api:local .
docker run --rm -p 8000:8000 malaria-cv-api:local
```

Image использует одного worker по умолчанию: каждый worker хранит отдельную
копию модели. Увеличивать worker count можно только после измерения peak RSS,
latency и throughput на утверждённой модели.

Docker `HEALTHCHECK` проверяет только liveness через `/health`. В orchestrator
нужно отдельно настроить readiness probe на `/ready`; без модели она корректно
возвращает `503`.

Для настоящего offline inference model directory/cache следует монтировать
read-only и передавать соответствующие переменные окружения.

## Структура

```text
.
├── .github/workflows/ci.yml
├── PROMPTS/
├── audit/
├── src/
│   ├── api/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   ├── ui/
│   └── main.py
├── tests/
├── .env.example
├── Dockerfile
├── Makefile
├── pyproject.toml
├── constraints.txt
├── requirements-bootstrap.txt
├── requirements.txt
└── requirements-dev.txt
```

## Известные ограничения

- утверждённая модель не поставляется;
- транзитивные версии зафиксированы в `constraints.txt`, bootstrap `pip`
  проверяется по hash, но полного hash-verified cross-platform lock пока нет;
- нет real-model smoke test;
- нет authentication/rate limiting для публичного deployment;
- per-process semaphore не заменяет внешний global quota;
- нет external clinical evaluation, calibration, OOD или abstention;
- нет patient/slide aggregation;
- Docker build и load tests требуют отдельного окружения.

Полные findings и roadmap: [audit/README.md](audit/README.md).

Дополнительные доказательства:

- [Claim-to-Evidence matrix](audit/phase3/CLAIM_TO_EVIDENCE_MATRIX.md);
- [аудит архитектуры](audit/phase4/ARCHITECTURE_AUDIT.md);
- [аудит provenance модели](audit/phase5/MODEL_PROVENANCE_AUDIT.md);
- [model STOP-SHIP](audit/phase5/STOP_SHIP_DECISION.md);
- [аудит intended use](audit/phase6/INTENDED_USE_AUDIT.md);
- [Dataset Datasheet](audit/phase7/DATASET_DATASHEET_CURRENT.md);
- [статус математической валидации](audit/phase8/MATHEMATICAL_VALIDATION_STATUS.md).

## Лицензия

Исходный код распространяется по MIT License: [LICENSE](LICENSE).

MIT License проекта не предоставляет автоматически права на сторонние model
weights или datasets. Их лицензии должны проверяться отдельно.
