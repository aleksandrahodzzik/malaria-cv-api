# Архитектурная реконструкция

## 1. Entrypoints

| Layer | Entrypoint | Evidence |
|---|---|---|
| Python | `python -m src.main` | `if __name__ == "__main__"` |
| ASGI | `src.main:app` | module global |
| Factory | `src.main:create_application()` | source |
| Development | `uvicorn src.main:app --reload` | Makefile |
| Container | `gunicorn ... src.main:app` | Dockerfile |
| Tests | `pytest tests/` | CI/Makefile |
| CI | `.github/workflows/ci.yml` | workflow |
| UI | отсутствует в baseline | file/route inventory |

## 2. Module graph

```text
src.main
├── src.api.routes
│   ├── src.api.dependencies
│   │   └── src.services.inference
│   ├── src.core.config
│   ├── src.schemas.payload
│   └── src.services.inference
├── src.core.config
├── src.core.middleware
└── src.services.inference
    ├── src.core.config
    └── src.schemas.payload
```

External direct packages:

```text
fastapi -> starlette, pydantic
pydantic-settings -> pydantic, dotenv
transformers -> huggingface-hub, tokenizers, safetensors, numpy
torch -> native CPU runtime
pillow -> native image decoders
uvicorn -> ASGI server
gunicorn -> process manager on Unix
python-multipart -> multipart parser
```

Dev graph:

```text
pytest + pytest-cov
ruff
mypy + types-Pillow
httpx         <- фактически используется TestClient
httpx2        <- direct dev dependency, reverse dependencies отсутствуют
```

## 3. Application lifecycle

```text
module import
-> Settings() читает defaults/.env/process environment
-> create_application()
-> FastAPI + optional CORS + request middleware + duplicate routers
-> ASGI lifespan startup
-> MalariaClassifierService(MODEL_NAME)
-> AutoImageProcessor.from_pretrained()
-> AutoModelForImageClassification.from_pretrained()
   ├── success -> eval -> app.state.classifier_service -> READY
   └── error   -> None -> NOT_READY, процесс продолжает работать
-> HTTP requests
-> lifespan shutdown
-> app.state.classifier_service = None
```

## 4. Configuration precedence

Pydantic Settings фактически использует:

```text
field defaults
< .env
< process environment
< explicit Settings constructor values
```

Docker `PORT=8000` задаётся, но Gunicorn bind жёстко фиксирован на `8000`,
поэтому runtime `PORT` не управляет фактическим bind.

Настройки:

- project/version/description/API prefix;
- host/port/debug;
- model name и неиспользуемый confidence threshold;
- upload MB, MIME types, max decoded pixels;
- CORS origins.

Secrets отсутствуют. API authentication отсутствует.

## 5. HTTP/data flow

```text
browser/client
-> ASGI server
-> RequestTrackingMiddleware
-> FastAPI multipart parser / UploadFile spool
-> content-type validation
-> chunked in-memory bytearray
-> Pillow verify/open/load/RGB
-> Transformers image processor
-> PyTorch model
-> logits -> softmax -> id2label
-> Pydantic response
-> latency/request-ID headers
-> client
```

### User file locations

- вход: multipart request;
- Starlette `UploadFile`: spooled temporary file, threshold controlled
  upstream library;
- application: `bytearray` в RAM;
- decode: Pillow objects в worker thread;
- persistent storage: отсутствует;
- explicit cleanup: `UploadFile.close()` в `finally`;
- logs: filename попадает в некоторые error logs.

## 6. External network dependencies

Runtime:

```text
AutoImageProcessor.from_pretrained(MODEL_NAME)
AutoModelForImageClassification.from_pretrained(MODEL_NAME)
-> Hugging Face Hub or configured mirror/cache
```

Build:

```text
apt repositories
PyPI
download.pytorch.org
Docker registry
GitHub Actions marketplace
```

No application outbound request after successful local model load was found.

## 7. Storage

- database: none;
- migrations: none;
- application uploads: not persisted;
- model: expected in Hugging Face cache, but cache absent;
- observability: stdout/stderr only;
- audit evidence: `audit/`;
- local generated state: `.venv`, `.coverage`, tool caches.

## 8. Trust boundaries

```text
untrusted browser/client
-> multipart parser
-> decoder
-> ML runtime

untrusted upstream registries
-> build/model artifacts
-> production process

repository documentation
-> user interpretation
-> potential clinical misuse
```

Наиболее опасный semantic boundary: cell-level model output называется
`diagnosis`, хотя patient/slide workflow отсутствует.
