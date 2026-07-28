# Repository inventory

## 1. Baseline

| Поле | Значение | Класс |
|---|---|---|
| Project root | `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1` | OBSERVED |
| Audit date | 2026-07-27 | VERIFIED |
| OS | Windows NT 10.0.26200.0 | VERIFIED |
| System Python | 3.12.0 | VERIFIED |
| Venv Python | 3.12.0 | VERIFIED |
| pip | 26.1.2 | VERIFIED |
| Docker | NOT_FOUND | VERIFIED |
| Make | NOT_FOUND | VERIFIED |
| Git repository | Не распознан; `.git` пуст/неполон | VERIFIED |
| CPU/RAM | UNKNOWN | System query unavailable |
| Hugging Face local cache | Root not found | VERIFIED |

## 2. Верхний уровень

```text
.agents/
.git/
.github/
.mypy_cache/
.pytest_cache/
.ruff_cache/
.venv/
PROMPTS/
src/
tests/
.coverage
.dockerignore
.gitignore
Dockerfile
LICENSE
Makefile
README.md
requirements-dev.txt
requirements.txt
```

Кэши и `.venv` рассматривались только как локальное состояние, не как
release artifacts.

## 3. Production modules

```text
src/
  api/
    dependencies.py
    routes.py
  core/
    config.py
    middleware.py
  schemas/
    payload.py
  services/
    inference.py
  main.py
```

## 4. Обнаруженные runtime endpoints

- `GET /health`
- `GET /ready`
- `POST /analyze`
- `GET /api/v1/health`
- `GET /api/v1/ready`
- `POST /api/v1/analyze`
- FastAPI OpenAPI/Swagger endpoints по умолчанию

## 5. Ключевые установленные версии

| Package | Version |
|---|---|
| fastapi | 0.140.5 |
| starlette | 1.3.1 |
| torch | 2.13.0+cpu |
| transformers | 4.57.6 |
| pillow | 10.4.0 |
| uvicorn | 0.51.0 |
| gunicorn | 21.2.0 |
| pydantic | 2.13.4 |
| pydantic-settings | 2.14.2 |
| python-multipart | 0.0.32 |
| pytest | 8.4.2 |
| pytest-cov | 4.1.0 |
| ruff | 0.16.0 |
| mypy | 1.20.2 |
| httpx | 0.28.1 |
| httpx2 | 2.9.1 |

Это snapshot локального venv, а не утверждённый lock. Production constraints
могут разрешить другой набор версий.

## 6. Отсутствующие release/evidence artifacts

- dependency lock с transitive hashes;
- model artifact и model manifest;
- model card/license/revision/checksum;
- dataset card/manifest/splits;
- statistical analysis report;
- calibration/OOD report;
- performance/load report;
- SBOM/signature/provenance;
- threat model/security test report;
- clinical intended-use/evaluation files;
- `.env.example`;
- deployment manifests;
- API authentication policy.

## 7. Scope exclusions

Не были доступны:

- работающий Git history и remote metadata;
- GitHub run results;
- container runtime;
- cloud/gateway/deployment конфигурация;
- model registry credentials;
- clinical datasets;
- private model repository;
- production logs/metrics;
- regulatory/QMS records.

Их состояние — `UNKNOWN`, если отсутствие не следует прямо из
репозитория.
