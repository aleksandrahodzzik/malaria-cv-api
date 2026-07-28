# Инвентаризация artifacts

`Verified=yes` означает, что artifact не только найден, но и прочитан либо
проверен командой.

| Artifact | Exists | Purpose | Verified | Problem | Evidence |
|---|---:|---|---:|---|---|
| `AGENTS.md` | no | Local agent instructions | yes | Отсутствует | recursive lookup |
| `.agents/` | yes | Local agent metadata | yes | Пусто | hidden directory inspection |
| `.codex/` | no | Project Codex configuration | yes | Отсутствует | hidden directory inspection |
| `README.md` | yes | User/developer documentation | yes | Mojibake; неподтверждённые production/clinical claims | file read |
| `LICENSE` | yes | MIT license | yes | Лицензия кода не покрывает неизвестные model weights/data | file read |
| `.gitignore` | yes | Ignore policy | yes | Хорошо исключает secrets/cache/models | file read |
| `.dockerignore` | yes | Docker context policy | yes | Исключает все `*.md`, включая потенциальную runtime docs metadata | file read |
| `.env` | no | Local settings | yes | Нормально для clean repo | path check |
| `.env.example` | no | Documented configuration | yes | Существенный DX/config gap | path check |
| `pyproject.toml` | no | Tool configuration/project metadata | yes | Lint/type/test policy не централизована | path check |
| `requirements.txt` | yes | Runtime dependencies | yes | Диапазоны без lock/hash | file read |
| `requirements-dev.txt` | yes | Test/dev dependencies | yes | Необоснованный `httpx2`; нет audit tooling | file read + pip metadata |
| Lock file | no | Reproducible dependencies | yes | Сборка mutable | known names lookup |
| `Makefile` | yes | Developer commands | yes | `github-push` опасно смешивает init/commit/remote/push; Make отсутствует локально | file read + command lookup |
| `Dockerfile` | yes | Container build/runtime | yes | Mutable image, 2 model workers, runtime model download | file read |
| Compose | no | Local deployment | yes | Нет resource/config example | path check |
| Kubernetes/Helm/Terraform | no | Deployment IaC | yes | Deployment вне репозитория/UNKNOWN | recursive file lookup |
| `.github/workflows/ci.yml` | yes | CI quality gate | yes | Нет format, pip check, coverage floor, container/security/model tests | file read |
| Dependabot/Renovate | no | Dependency updates | yes | Нет automated update policy | recursive lookup |
| `src/main.py` | yes | ASGI app/factory/lifespan | yes | Duplicate root/v1 routes; UI отсутствует | file read |
| `src/api/routes.py` | yes | HTTP endpoints/upload | yes | Internal exception leakage; clinical wording | file read |
| `src/api/dependencies.py` | yes | Model service DI | yes | 503 detail не стандартизирован | file read |
| `src/core/config.py` | yes | Pydantic settings | yes | Broken model default; unused confidence threshold | file read/search |
| `src/core/middleware.py` | yes | Request ID/latency | yes | Trusts arbitrary request ID | file read |
| `src/services/inference.py` | yes | Image/model inference | yes | Mutable model; fallback labels; no capacity bound | file read |
| `src/schemas/payload.py` | yes | API schema | yes | `diagnosis`, calibrated-probability implication | file read |
| UI templates/static | no | Human interface | yes | UI полностью отсутствует | recursive lookup |
| `tests/test_api.py` | yes | Unit/API tests | yes | Real model mocked; limited error/security coverage | file read/test run |
| Migrations/schema | no | Database evolution | yes | Database не используется; not applicable | recursive lookup/code search |
| Model weights | no | ML inference artifact | yes | STOP-SHIP для real inference | extension/path lookup |
| Model card | no | Model provenance | yes | STOP-SHIP | recursive lookup |
| Dataset card/manifest | no | Data provenance | yes | STOP-SHIP для evidence | recursive lookup |
| Hugging Face cache | no | Cached model assets | yes | Нет offline artifact | three path checks |
| SBOM/provenance/signature | no | Supply-chain evidence | yes | Release integrity не доказана | recursive lookup |
| `.coverage` | yes | Local coverage database | yes | Generated artifact, ignored Git | pytest/size inspection |
| Audit reports | yes | Evidence/risk/roadmap | yes | Нужна синхронизация после реализации | file tree |
| Git repository | yes | Version control | yes | Чистый; один initial commit | git status/log |
| Git remote | yes | GitHub origin | yes | HTTPS URL, credentials не раскрыты | git remote |

## Git evidence

```text
branch: main
HEAD: 09c24d7
upstream: origin/main
ahead/behind: 0/0
working tree before this phase: clean
remote: https://github.com/aleksandrahodzzik/malaria-cv-api.git
```

После начала фазы новые prompt/audit files закономерно становятся изменениями
рабочего дерева; они принадлежат текущей задаче.
