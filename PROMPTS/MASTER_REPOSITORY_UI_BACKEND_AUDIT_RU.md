# Мастер-промпт инвентаризации, функционального аудита и развития UI/backend

Версия: 1.0.0
Язык выполнения и отчёта: русский
Режим глубины: максимальный
Проект: `malaria-cv-api`
Корень проекта: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`

---

## Машиночитаемый заголовок

```text
<MASTER_PROMPT>
  <ID>MALARIA_CV_API_REPOSITORY_UI_BACKEND_AUDIT_RU</ID>
  <VERSION>1.0.0</VERSION>
  <LANGUAGE>ru-RU</LANGUAGE>
  <EXECUTION_DEPTH>MAXIMUM</EXECUTION_DEPTH>
  <MODE>AUDIT_THEN_CONTROLLED_IMPLEMENTATION</MODE>
  <PROJECT_ROOT>C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1</PROJECT_ROOT>
  <PROJECT_NAME>malaria-cv-api</PROJECT_NAME>
  <CURRENT_DATE>Определи системную дату самостоятельно</CURRENT_DATE>
  <DEFAULT_AUDIT_OUTPUT>audit/phase1</DEFAULT_AUDIT_OUTPUT>
</MASTER_PROMPT>
```

---

# 0. Назначение

Проведи полный доказательный аудит репозитория, пользовательского интерфейса,
backend-функций, API-контрактов, ML-интеграции и инженерной инфраструктуры.
После аудита сформируй приоритетный backlog и реализуй только те изменения,
которые:

1. находятся в явно заданной области проекта;
2. подтверждены обнаруженными проблемами или измеримой пользовательской
   ценностью;
3. не скрывают отсутствие модели, данных или клинических доказательств;
4. имеют проверяемые acceptance criteria;
5. не разрушают пользовательские изменения;
6. могут быть воспроизводимо протестированы.

Это не задание на косметический пересказ файлов. Результат должен отвечать:

- что существует в репозитории;
- что отсутствует;
- как фактически запускается приложение;
- какие пользовательские сценарии доступны;
- какие состояния UI и API не обработаны;
- где находятся trust boundaries;
- какие claims не подтверждены;
- какие функции следует добавить, изменить, отложить или удалить;
- какие улучшения реализованы;
- чем доказана корректность реализации;
- что остаётся заблокированным.

---

# 1. Роль

Действуй как единая экспертная группа уровня Principal/Staff:

1. Principal Software Architect.
2. Senior Product Engineer.
3. UX/UI Architect.
4. Accessibility Specialist, WCAG.
5. Python/FastAPI Backend Architect.
6. API Contract and Developer Experience Engineer.
7. Principal ML Engineer.
8. Medical Imaging Researcher.
9. Clinical Safety Reviewer.
10. Application Security Engineer.
11. SRE/Performance Engineer.
12. MLOps/Supply Chain Engineer.
13. QA/Test Automation Architect.
14. Technical Writer.
15. Independent Release Reviewer.

Не смешивай мнения ролей в недоказанный общий вывод. Если приоритеты
конфликтуют, опиши конфликт и выбери решение по явным критериям:
безопасность, корректность, пользовательская ценность, обратимость,
стоимость и доказательность.

---

# 2. Политика глубины

Не используй лимит длины ответа, токенов или времени как основание:

- пропускать важные файлы;
- не строить дерево;
- заменять проверку предположением;
- сокращать разные риски до одного пункта;
- объявлять функцию работающей без теста;
- игнорировать UI states;
- игнорировать негативные сценарии;
- скрывать неопределённость;
- внедрять первую пришедшую идею без сравнения вариантов.

Не упрощай задачу ради удобства исполнителя.

Если работа не помещается в один ответ:

1. сохраняй артефакты в проекте;
2. дели процесс по фазам;
3. сохраняй ID findings, risks и requirements;
4. в продолжении указывай завершённое, текущее и оставшееся;
5. не повторяй уже завершённые проверки без причины.

---

# 3. Эпистемическая дисциплина

Каждое существенное утверждение помечай:

- `OBSERVED` — найдено в файле, Git metadata или выводе команды;
- `VERIFIED` — подтверждено воспроизводимым тестом;
- `INFERRED` — логический вывод из доказательств;
- `HYPOTHESIS` — проверяемое предположение;
- `RECOMMENDATION` — предлагаемое действие;
- `IMPLEMENTED` — изменение реально внесено;
- `NOT_EXECUTED` — проверка не выполнялась с указанием причины;
- `UNKNOWN` — данных недостаточно.

Никогда не превращай:

```text
unit test -> доказательство реальной ML-модели
softmax -> калиброванная вероятность
cell classification -> диагноз пациента
наличие Dockerfile -> работающий контейнер
наличие workflow -> успешный CI run
наличие UI -> хороший UX
упоминание security -> security verification
```

---

# 4. Безопасность изменений

## 4.1. Сначала аудит

До завершения baseline не меняй production-код.

Разрешены:

- чтение;
- безопасные команды;
- тесты;
- статический анализ;
- создание аудиторских документов;
- временные локальные test artifacts.

## 4.2. Затем controlled implementation

Изменения разрешены после:

1. Finding;
2. evidence;
3. severity/value;
4. выбранного варианта;
5. acceptance criteria;
6. regression plan.

Не выполняй без отдельного разрешения:

- push;
- deployment;
- изменение Git remote;
- удаление пользовательских данных;
- отправку медицинских изображений;
- подмену отсутствующей модели другой моделью;
- скачивание больших весов;
- публикацию clinical claims.

---

# 5. Формат findings

```text
Finding ID:
Domain:
Classification:
Severity:
Confidence:
Affected artifacts:
Observed behavior:
Expected behavior:
Evidence:
Reproduction:
User impact:
Technical impact:
Safety/security impact:
Root cause:
Alternatives considered:
Recommendation:
Acceptance criteria:
Regression tests:
Owner hypothesis:
Status:
```

Severity:

- `CRITICAL / STOP-SHIP`;
- `HIGH`;
- `MEDIUM`;
- `LOW`;
- `INFO`.

---

# 6. ФАЗА 1 — инвентаризация репозитория

## 6.1. Полное дерево

Построй дерево проекта, включая скрытые файлы.

Раздели:

1. source-controlled artifacts;
2. Git internals;
3. generated caches;
4. virtual environment;
5. binary/model artifacts;
6. audit artifacts;
7. potentially sensitive files.

Не выводи содержимое секретов. Для `.venv`, `.git/objects` и кэшей допускается
структурное свёртывание только при наличии:

- полного количества файлов;
- полного размера;
- типа содержимого;
- объяснения, почему побайтовый листинг не полезен.

Для project-controlled files укажи все пути.

## 6.2. Обязательные artifacts

Проверь:

- `AGENTS.md` и локальные инструкции;
- `.agents/`, `.codex/`;
- `README*`;
- `LICENSE*`;
- `.gitignore`;
- `.dockerignore`;
- `.env`, `.env.example`;
- `pyproject.toml`;
- `setup.cfg`, `setup.py`;
- `requirements*.txt`;
- lock-файлы;
- Makefile;
- Dockerfile;
- compose;
- Kubernetes/Helm/Terraform;
- GitHub Actions;
- Dependabot/Renovate;
- исходный код;
- UI assets/templates/static;
- тесты/fixtures;
- конфигурацию;
- документацию;
- миграции;
- database schemas;
- модели/weights/checkpoints;
- model cards;
- dataset cards;
- Hugging Face cache;
- SBOM/provenance/signatures;
- reports/coverage;
- generated caches;
- repository size;
- Git status;
- branch/upstream;
- незакоммиченные и untracked изменения;
- remotes без раскрытия credentials.

## 6.3. Таблица artifacts

Создай:

| Artifact | Exists | Purpose | Verified | Problem | Evidence |
|---|---:|---|---|---|---|

`Verified` не может быть `yes`, если файл только существует, но не был
прочитан или выполнен.

## 6.4. Git baseline

Зафиксируй:

- текущую branch;
- HEAD;
- upstream divergence;
- последние commits;
- tracked/untracked/modified;
- `.gitignore` coverage;
- случайно tracked cache/secrets/binaries;
- remote URL без токенов.

Не выполняй commit/push.

## 6.5. Размер

Вычисли:

```text
total_files
total_directories
total_bytes
controlled_files
controlled_bytes
venv_files
venv_bytes
cache_files
cache_bytes
model_files
model_bytes
largest_files
```

---

# 7. ФАЗА 2 — архитектурная реконструкция

## 7.1. Entrypoints

Определи:

- Python module entrypoint;
- ASGI object;
- application factory;
- Uvicorn command;
- Gunicorn command;
- Docker entrypoint;
- Make targets;
- UI entrypoint;
- CI entrypoints.

## 7.2. Lifecycle

Построй state machine:

```text
process start
-> settings resolution
-> app creation
-> middleware/router registration
-> lifespan startup
-> model initialization
-> ready/not-ready
-> request handling
-> graceful shutdown
```

Для failure branch укажи HTTP-поведение.

## 7.3. Dependency graph

Построй минимум четыре графа:

1. module import graph;
2. request dependency graph;
3. package dependency graph;
4. infrastructure dependency graph.

Отдельно отметь:

- direct;
- transitive;
- dev-only;
- unused;
- mutable;
- external;
- native/system.

## 7.4. Configuration graph

Определи precedence:

```text
code defaults
< .env
< process environment
< CLI/container runtime
```

Проверь типы, bounds, secrets, unsafe defaults и undocumented settings.

## 7.5. Network/data flows

Найди:

- outbound HTTP;
- model registry;
- package registries;
- runtime egress;
- inbound upload;
- temp/spool storage;
- image decode;
- logs;
- response serialization;
- browser/API traffic;
- CORS;
- patient/specimen metadata.

Для каждого flow:

```text
source -> boundary -> transform -> storage -> destination -> retention
```

---

# 8. ФАЗА 3 — аудит backend-функций

## 8.1. Endpoint inventory

Для каждого route:

| Method | Path | Purpose | Input | Output | Auth | Limits | Errors | Tests |
|---|---|---|---|---|---|---|---|---|

Проверь duplicate routes, versioning, OpenAPI, deprecation и compatibility.

## 8.2. Error contract

Проверь:

- единый schema;
- request ID;
- stable error codes;
- отсутствие internal details;
- 400/401/403/404/413/415/422/429/500/503;
- validation errors;
- response/OpenAPI parity.

## 8.3. Upload pipeline

Проверь:

- filename;
- MIME;
- magic/decode;
- encoded size;
- decoded size;
- decompression bomb;
- multipart spooling;
- slow upload;
- disconnect/cancellation;
- cleanup;
- multi-frame images;
- malicious metadata.

## 8.4. Inference

Проверь:

- model provenance;
- immutable revision;
- processor;
- labels;
- device;
- eval/no_grad/inference_mode;
- dtype;
- deterministic behavior;
- concurrency;
- queue;
- timeout semantics;
- warmup;
- resource cleanup;
- calibration;
- abstention;
- OOD;
- model metadata in response.

## 8.5. Observability

Проверь:

- request/trace ID;
- structured logs;
- sensitive data;
- RED metrics;
- model metrics;
- queue/decode/inference timings;
- health/readiness semantics;
- alertability;
- runbooks.

## 8.6. Security

Проверь:

- authentication;
- authorization;
- rate/quota/concurrency limiting;
- body/header/time limits;
- CORS;
- security headers;
- error leakage;
- log injection;
- dependency/model supply chain;
- secrets;
- container least privilege;
- SSRF/path traversal;
- model extraction/probing;
- privacy/retention.

---

# 9. ФАЗА 4 — аудит UI

Если UI отсутствует, не симулируй его наличие. Зафиксируй `ABSENT` и определи,
нужен ли он целевому продукту.

## 9.1. Пользовательские роли

Проверь/определи:

- researcher;
- developer/integrator;
- laboratory operator;
- clinician;
- administrator.

Не смешивай роли без permission model.

## 9.2. User journeys

Минимум:

1. открыть приложение;
2. понять назначение и ограничения;
3. увидеть readiness;
4. выбрать/перетащить изображение;
5. проверить preview;
6. запустить analysis;
7. увидеть progress;
8. получить результат;
9. понять uncertainty;
10. обработать failure;
11. повторить;
12. открыть API docs.

## 9.3. UI states

Для каждого компонента:

- idle;
- hover/focus;
- disabled;
- loading;
- success;
- warning;
- error;
- offline;
- model unavailable;
- invalid file;
- oversized;
- server busy;
- indeterminate.

## 9.4. Information architecture

Проверь:

- primary action;
- hierarchy;
- terminology;
- clinical claims;
- progressive disclosure;
- model/limitations;
- privacy;
- docs/status links.

## 9.5. Accessibility

Проверь:

- semantic HTML;
- keyboard;
- visible focus;
- labels/instructions;
- error association;
- live regions;
- contrast;
- reduced motion;
- responsive layout;
- screen reader names;
- non-color encoding;
- locale/language.

Ориентир: WCAG 2.2 AA. Не заявляй compliance без formal audit.

## 9.6. Frontend security/privacy

Проверь:

- DOM XSS;
- unsafe `innerHTML`;
- filename rendering;
- object URL cleanup;
- raw image storage;
- third-party scripts;
- analytics;
- CSP compatibility;
- cache behavior;
- sensitive errors.

## 9.7. Visual design

Оцени:

- readability;
- density;
- responsive behavior;
- medical/research trust cues;
- honest uncertainty;
- empty space;
- feedback latency;
- consistency.

Красивый UI не должен повышать доверие к недоказанной модели.

---

# 10. ФАЗА 5 — функциональный gap analysis

Создай каталог функций:

| Feature ID | Layer | User | Problem | Current | Desired | Risk | Value | Effort | Decision |
|---|---|---|---|---|---|---|---|---|---|

Категории:

- missing essential;
- broken;
- misleading;
- incomplete;
- duplicated;
- unnecessary;
- future hypothesis.

## 10.1. Приоритизация

Используй минимум две модели.

### RICE

```text
RICE = Reach * Impact * Confidence / Effort
```

### WSJF

```text
WSJF =
  (UserBusinessValue + TimeCriticality + RiskReduction)
  / JobSize
```

Для safety-critical функции severity может переопределить score.

## 10.2. Product constraints

Не предлагай:

- dashboard ради dashboard;
- accounts без понятной роли;
- database без persistence use case;
- batch processing без workflow;
- explanation heatmaps как доказательство correctness;
- clinical recommendations без evidence;
- silent model fallback;
- feature, которую нельзя протестировать.

---

# 11. ФАЗА 6 — варианты архитектуры

Для каждого P0/P1 изменения сравни минимум:

1. оставить как есть;
2. минимальное исправление;
3. целевая архитектура.

Таблица:

| Variant | Safety | UX | Complexity | Compatibility | Operations | Decision |
|---|---:|---:|---:|---:|---:|---|

Опиши ADR:

- context;
- decision;
- alternatives;
- consequences;
- rollback.

---

# 12. ФАЗА 7 — controlled implementation

## 12.1. Перед изменением

- зафиксируй Git status;
- прочитай overlapping files;
- не перезаписывай чужие изменения;
- свяжи change с Finding/Feature ID;
- определи tests.

## 12.2. Реализация

Предпочитай:

- fail closed;
- explicit configuration;
- stable contracts;
- backward-compatible migration;
- bounded resources;
- safe defaults;
- research-only semantics;
- small cohesive modules;
- typed code;
- dependency minimization.

## 12.3. UI implementation quality

- no framework без необходимости;
- no external CDN по умолчанию;
- semantic HTML;
- escaped text via `textContent`;
- abortable requests;
- object URL cleanup;
- readiness polling с ограничением;
- accessible status;
- no storage of images;
- responsive CSS;
- reduced-motion support.

## 12.4. Backend implementation quality

- centralized errors;
- sanitized public messages;
- validated identifiers;
- explicit capacity control;
- health/readiness separation;
- safe file handling;
- model contract validation;
- immutable artifact support;
- testable settings.

---

# 13. ФАЗА 8 — тестирование

Минимальная матрица:

## Static

- formatter;
- linter;
- type checker;
- compile.

## Unit

- settings bounds;
- request ID;
- filename sanitation;
- error mapping;
- model contract;
- concurrency behavior.

## API contract

- routes;
- schemas;
- OpenAPI;
- errors;
- headers;
- readiness;
- versioned paths.

## UI

- root/assets;
- no model state;
- upload validation;
- keyboard/labels;
- JS syntax;
- no unsafe rendering.

## Integration

- real model smoke, если artifact доступен;
- clean cache;
- container;
- network disabled;
- graceful shutdown.

## Security

- control characters;
- oversized headers/body/image;
- corrupt formats;
- exception leakage;
- rate/concurrency;
- dependency audit.

## Performance

- cold/warm;
- p50/p95/p99;
- saturation;
- soak;
- RSS;
- queue.

Не выполнять fake performance test с mocked model как production evidence.

---

# 14. ФАЗА 9 — вариационная проверка

После реализации проведи минимум три независимых review passes.

## Review A — correctness

- соответствие requirements;
- edge cases;
- regression;
- API schema;
- concurrency.

## Review B — security/reliability

- fail-open;
- resource exhaustion;
- leakage;
- supply chain;
- startup/shutdown.

## Review C — UX/clinical safety

- misleading terms;
- unavailable/error states;
- accessibility;
- patient-level interpretation;
- uncertainty.

Для каждого дефекта:

1. зафиксируй;
2. исправь;
3. повтори relevant checks;
4. не объявляй PASS до подтверждения.

---

# 15. Обязательные deliverables

Создай:

```text
PROMPTS/
  MASTER_REPOSITORY_UI_BACKEND_AUDIT_RU.md

audit/phase1/
  README.md
  REPOSITORY_TREE.md
  ARTIFACT_INVENTORY.md
  ARCHITECTURE_MAP.md
  UI_BACKEND_FUNCTIONAL_AUDIT.md
  FEATURE_BACKLOG.csv
  IMPLEMENTATION_REPORT.md
  VERIFICATION_REPORT.md
```

При необходимости:

```text
docs/
  ARCHITECTURE.md
  API.md
  SAFETY.md
```

## 15.1. Inventory table

Обязательно включить:

| Artifact | Exists | Purpose | Verified | Problem | Evidence |
|---|---:|---|---|---|---|

## 15.2. Architecture maps

- entrypoints;
- module graph;
- lifecycle;
- request/data flow;
- configuration precedence;
- external dependencies;
- storage and upload locations.

## 15.3. Implementation report

Для каждого change:

| Change | Finding | Files | Behavior | Tests | Residual risk |
|---|---|---|---|---|---|

---

# 16. Финальный ответ

Начни с результата:

1. что создано;
2. что реализовано;
3. какие проверки прошли;
4. что остаётся заблокировано;
5. ссылки на основные файлы.

Не скрывай:

- отсутствие real model;
- `NOT_EXECUTED`;
- breaking changes;
- residual clinical risk;
- unavailable Docker/network.

---

# 17. Старт исполнения

Выполни последовательно:

```text
PRECHECK
-> INVENTORY
-> ARCHITECTURE_RECONSTRUCTION
-> UI_BACKEND_AUDIT
-> FEATURE_PRIORITIZATION
-> VARIANT_ANALYSIS
-> CONTROLLED_IMPLEMENTATION
-> STATIC_AND_DYNAMIC_TESTS
-> THREE_PASS_REVIEW
-> FINAL_GO_NO_GO
```

Не останавливайся на создании prompt. После сохранения сразу исполни его на
текущем состоянии `PROJECT_ROOT`, пока не будет достигнут проверяемый
результат или честно зафиксированный внешний blocker.
