# Аудит функций UI и backend

## 1. Product baseline

UI отсутствует. Единственный human interface — Swagger/ReDoc. Backend
реализует liveness, readiness и один upload endpoint в двух path namespaces.

Целевой безопасный interim product: исследовательский web/API прототип для
классификации заранее выделенного изображения отдельной клетки, без
диагностических claims.

## 2. Endpoint inventory

| Method | Path | Purpose | Auth | Limits | Основной gap |
|---|---|---|---|---|---|
| GET | `/health` | liveness | none | cheap | дублируется |
| GET | `/ready` | model readiness | none | cheap | нет stable reason/code |
| POST | `/analyze` | cell image score | none | 10 MB/25 MP | clinical wording, no concurrency bound |
| GET | `/api/v1/health` | liveness | none | cheap | duplicate |
| GET | `/api/v1/ready` | readiness | none | cheap | duplicate |
| POST | `/api/v1/analyze` | cell image score | none | 10 MB/25 MP | duplicate |
| GET | `/docs`, `/redoc` | API UI | none | none | не end-user UI |

## 3. UI gap

Отсутствуют:

- назначение и research-only limitation до upload;
- readiness indicator;
- file picker/drag-and-drop;
- preview и local validation;
- loading/cancel/error states;
- uncalibrated-score explanation;
- result semantics;
- links to API docs;
- responsive/accessibility behavior.

UI нужен как controlled demonstrator, но не должен визуально имитировать
медицинское устройство или выдавать treatment advice.

## 4. Backend findings

### UB-001 — misleading result semantics

Severity: `CRITICAL`
Evidence: `diagnosis`, `clinical prediction`, `confidence probability`.

Decision: ввести безопасное `predicted_cell_class`, пометить score как
некалиброванный, добавить `research_only`/limitations. Backward compatibility
оценить явно.

### UB-002 — model artifact unavailable

Severity: `CRITICAL / BLOCKED EXTERNALLY`
Evidence: нет weights/cache; public model ранее не подтверждён.

Decision: не подменять модель. Улучшить fail-closed readiness и artifact
configuration.

### UB-003 — error leakage and schema mismatch

Severity: `HIGH`
Evidence: exception strings возвращаются клиенту; `ErrorResponse` не
соответствует FastAPI default body.

Decision: centralized stable error envelope.

### UB-004 — untrusted correlation ID

Severity: `MEDIUM`
Evidence: произвольный header отражается в log/response.

Decision: bounded ASCII format, иначе server UUID.

### UB-005 — unbounded inference admission

Severity: `HIGH`
Evidence: каждый запрос запускает `to_thread`; два Gunicorn processes.

Decision: per-process semaphore и queue admission timeout; production topology
остаётся subject to load testing.

### UB-006 — unsafe label fallback

Severity: `CRITICAL`
Evidence: при отсутствии metadata код предполагает class order.

Decision: fail closed на invalid model contract.

### UB-007 — missing model revision

Severity: `HIGH`
Evidence: `from_pretrained(name)` без immutable revision.

Decision: поддержать explicit revision/local-files-only и документировать;
release обязан задать immutable revision.

### UB-008 — incomplete DX/reproducibility

Severity: `MEDIUM`
Evidence: нет `.env.example`, `pyproject.toml`, lock; README mojibake.

Decision: добавить config examples/tool policy, исправить docs и dependency
name. Lock generation — отдельный шаг после выбора resolver/policy.

### UB-009 — CI is quality-only

Severity: `MEDIUM`
Evidence: нет format/pip check/coverage floor; HF cache бесполезен при mocks.

Decision: усилить проверяемыми локально gates, не притворяться real model CI.

### UB-010 — no end-user UI

Severity: `MEDIUM`
Evidence: static/template files и root page отсутствуют.

Decision: добавить dependency-free accessible research UI со всеми failure
states и без external CDN.

## 5. Variants

| Problem | As-is | Minimal | Target | Decision |
|---|---|---|---|---|
| UI | Swagger only | single HTML | separate frontend | Minimal: достаточно для research demo |
| Errors | default/detail | central envelope | RFC 9457 ecosystem | Central compatible envelope |
| Concurrency | unbounded | semaphore | inference server/queue | Semaphore сейчас; server после profiling |
| Labels | fallback | validate metadata | signed model manifest | Fail closed + manifest roadmap |
| Model source | mutable name | revision config | baked signed artifact | Revision now; baked artifact next |
| Claims | diagnosis | deprecate/rename | validated clinical terminology | Safe rename and research context |

## 6. UI requirements

### Required

- semantic Russian page;
- research-only banner;
- service readiness;
- accepted types/size;
- picker + drag/drop;
- local preview;
- submit disabled until valid/ready;
- abortable request;
- safe `textContent` rendering;
- success score bars;
- unavailable, invalid, oversize, busy and generic errors;
- object URL cleanup;
- keyboard/focus/live region;
- no third-party scripts, analytics or persistence.

### Explicitly excluded

- patient diagnosis;
- treatment recommendation;
- user accounts/database;
- history of uploaded medical images;
- Grad-CAM as trust decoration;
- batch workflow without user research;
- fabricated model metrics.

## 7. Acceptance summary

Implementation passes only if:

- mocked HTTP/API tests remain green;
- new error/security/concurrency/model-contract tests pass;
- root UI and assets return correctly;
- JavaScript parses;
- no unsafe `innerHTML`;
- README is valid UTF-8 without mojibake;
- docs openly state model blocker;
- lint/type/format/coverage gates pass.
