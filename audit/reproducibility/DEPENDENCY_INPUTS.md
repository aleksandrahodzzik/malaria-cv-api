# Dependency inputs

Дата: 2026-07-28

| Input | Exists | Role | Direct pins | Transitive lock | Hashes | Python constraint | Problem |
|---|---:|---|---:|---:|---:|---|---|
| `requirements-bootstrap.txt` | yes | bootstrap pip | yes | n/a | yes | implicit | один wheel hash |
| `requirements.txt` | yes | production | yes | no | no | implicit | нет полного lock |
| `requirements-dev.txt` | yes | development | yes | no | no | implicit | включает production |
| `pyproject.toml` | yes | tool config | n/a | no | no | 3.11 targets | нет `[project].requires-python` |
| `Dockerfile` | yes | Linux image | via requirements | no | bootstrap only | 3.11 | base image не pinned digest |
| `.github/workflows/ci.yml` | yes | CI | via requirements | no | bootstrap only | 3.11/3.12 | Actions tags не immutable SHA |
| `Makefile` | yes | local workflow | via requirements | no | bootstrap only | system Python | GNU Make отсутствует локально |

Классификация:

```text
direct exact pins != complete transitive lock != hash-verified release lock
```

Текущий статус: `RESOLVABLE_BUT_NOT_LOCKED`.

## Проверенные изменения

Baseline был снят до обновлений. Затем отдельный candidate прошёл resolver,
imports, quality gates и vulnerability scan. После этого в project inputs
перенесены:

| Package | Before | After | Reason |
|---|---:|---:|---|
| pip | environment 23.2.1 | bootstrap 26.1.2 | известные advisory; hash pin |
| gunicorn | 21.2.0 | 22.0.0 | scanner fixed version |
| Pillow | 10.4.0 | 12.3.0 | обработка недоверенных изображений; security fixes |
| transformers | 4.57.6 | 5.14.1 | known advisory remediation |
| torchvision | absent | 0.28.0+cpu | обязательный backend для Transformers 5 image processor |
| pytest | 8.4.2 | 9.0.3 | dev advisory remediation |
| pytest-asyncio | 0.26.0 | 1.3.0 | pytest 9 compatibility |
| httpx | direct 0.28.1 | httpx2 2.7.0 direct | Starlette TestClient migration |
| types-Pillow | 10.2 stubs | removed | не используется из-за mypy override |

`httpx 0.28.1` остаётся транзитивной зависимостью `huggingface-hub`, но
Starlette TestClient использует установленный `httpx2`.
