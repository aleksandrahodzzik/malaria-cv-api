# Implementation report

Дата: 2026-07-28
Режим: controlled implementation после baseline
Push/deployment: не выполнялись

## 1. Результат

Реализован безопасный research-only web/API-контур. Основной внешний blocker
не скрыт: утверждённой реальной модели по-прежнему нет, поэтому default
runtime корректно остаётся `not_ready`.

## 2. Реализованные изменения

| Change | Finding | Files | Новое поведение | Tests | Residual risk |
|---|---|---|---|---|---|
| Research UI | UB-010/F-008 | `src/ui/*`, `src/main.py` | `/` показывает readiness, upload, preview, states, limitations | HTTP + Chrome desktop/mobile/success journey | Не formal WCAG audit |
| Safe result semantics | UB-001/F-001 | schemas/routes/inference/UI/README | `predicted_cell_class`, research-only, uncalibrated, limitations | response/OpenAPI tests | Deprecated `diagnosis` временно сохранён |
| Fail-closed model default | UB-002/F-002 | config/main/README/env | Без `MODEL_NAME` нет network request; readiness reason | capabilities/readiness tests | Approved artifact всё ещё отсутствует |
| Model revision controls | UB-007/F-007 | config/inference/env | revision/local-only передаются loader; production remote требует revision | settings/load tests | Нет checksum/signature/baked artifact |
| Model contract validation | UB-006/F-006 | inference | нет fallback labels; exact order/count/indices обязательны | normal/inverted contract tests | Golden real-model samples отсутствуют |
| Bounded admission | UB-005/F-005 | config/inference/routes | semaphore + bounded queue wait + 503/Retry-After | queue/API tests | Per-process, не global rate limit |
| Cancellation accounting | Review B | inference | semaphore удерживается до завершения native thread | static/unit regression | Native compute нельзя остановить |
| Central error envelope | UB-003/F-003 | `core/errors.py`, routes | `code/detail/request_id`; no internal exception body | 400/404/415/422/500/503 tests | Logs требуют production retention policy |
| Request ID validation | UB-004/F-004 | middleware | max 64 safe ASCII pattern; unsafe заменяется UUID | header tests | Distributed trace propagation не реализован |
| Security headers | Security review | middleware | nosniff/referrer/frame/permissions; UI CSP | HTTP tests/Chrome | Swagger не покрыт CSP намеренно |
| Filename sanitation | Upload review | routes | path/control chars не отражаются | API test | Filename всё ещё может быть sensitive metadata |
| Client capabilities | UI requirement | schemas/routes | limits/intended use доступны UI | API test | Не заменяет version negotiation |
| Settings invariants | Security review | config | wildcard CORS и ambiguous production model config запрещены | validation tests | Нет secret settings/auth |
| Reproducible direct versions | UB-008/F-012 | requirements | direct runtime/dev packages exact-pinned | pip check | Transitive hashes/lock ещё отсутствуют |
| Removed `httpx2` requirement | F-009 historical | requirements-dev | clean env устанавливает `httpx`, не `httpx2` | TestClient + pip check | Existing venv retains extraneous package |
| Tool policy | UB-008/F-009 | pyproject | strict Mypy, Ruff rules, pytest/coverage policy | all tools read config | Platform lock отсутствует |
| Line-ending policy | DX review | `.gitattributes` | source/docs/YAML фиксируются как LF | `git diff --check` | Existing clones may need renormalization |
| Environment example | UB-008/F-009 | `.env.example` | все settings документированы | Settings tests/manual review | Не содержит artifact checksum |
| CI matrix/gates | UB-009/F-011 | workflow | Python 3.11/3.12, format, pip check, 80% coverage | local equivalents PASS | Hosted workflow не запускался |
| Safer Docker default | UB-005 | Dockerfile | 1 worker вместо двух model copies | static review | Docker unavailable; build NOT_EXECUTED |
| Safer Makefile | DX review | Makefile | удалён mutating `github-push`; добавлены format/check | static review | Make unavailable locally |
| README rewrite | UB-008/F-010 | README | UTF-8, no mojibake, honest setup/limitations | mojibake scan | Требует синхронизации при новых releases |

## 3. API migration

Изменение сделано обратно совместимым:

- новый основной field: `predicted_cell_class`;
- старый `diagnosis` сохранён как deprecated alias;
- `confidence` сохранён, но schema прямо называет его uncalibrated softmax
  score;
- добавлены `calibrated=false`, `intended_use=research_only`,
  `limitations`.

Следующая major version должна удалить `diagnosis`, когда downstream clients
перейдут на новый field.

## 4. UI decisions

Выбран dependency-free UI вместо отдельного SPA:

- backend уже имеет один узкий workflow;
- нет необходимости в Node build chain;
- CSP не требует сторонних CDN;
- deploy остаётся единым artifact;
- surface проще тестировать и поддерживать.

Security/UX properties:

- только `textContent`, без `innerHTML`;
- `<progress>`, а не CSP-blocked inline styles;
- abortable fetch;
- object URL cleanup;
- file не сохраняется в localStorage/history;
- accessible labels/live region/focus;
- reduced-motion и responsive layouts;
- no analytics/external scripts.

## 5. Final controlled tree delta

Добавлены:

```text
.env.example
.gitattributes
pyproject.toml
src/core/errors.py
src/ui/index.html
src/ui/styles.css
src/ui/app.js
PROMPTS/MASTER_REPOSITORY_UI_BACKEND_AUDIT_RU.md
audit/phase1/*
```

Изменены:

```text
.github/workflows/ci.yml
Dockerfile
Makefile
README.md
requirements.txt
requirements-dev.txt
src/api/dependencies.py
src/api/routes.py
src/core/config.py
src/core/middleware.py
src/main.py
src/schemas/payload.py
src/services/inference.py
tests/test_api.py
```

## 6. Remaining P0/P1

### Blocked P0

1. Approved model artifact, license, revision and checksum.
2. Model/data cards и patient-level data lineage.
3. Artifact-backed golden smoke tests.
4. Statistical/clinical external evaluation.

### Engineering P1

1. Transitive lock с hashes.
2. SBOM, CVE/license scan, signing/provenance.
3. Docker/Linux runtime test.
4. Global auth/rate/quota на deployment boundary.
5. Real-model capacity/load/soak.
6. Formal accessibility and penetration tests.

## 7. Updated release verdict

| Scenario | Verdict |
|---|---|
| Static UI/backend development | GO |
| Mocked local demo с явной маркировкой | GO |
| Default no-model UI/health mode | GO |
| Real malaria inference | NO-GO до model artifact |
| Public API | NO-GO до auth/capacity/container/security gates |
| Clinical/research effectiveness claims | NO-GO |
