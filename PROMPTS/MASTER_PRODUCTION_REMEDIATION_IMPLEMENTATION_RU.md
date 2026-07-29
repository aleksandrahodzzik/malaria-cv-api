# Мастер-промпт глубокой реализации и развития `malaria-cv-api`

Версия: 4.0.0
Язык выполнения и отчёта: русский
Режим глубины: максимальный
Тип работы: evidence-driven remediation and implementation
Корень проекта: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`

---

## Машиночитаемый заголовок

```text
<MASTER_PROMPT>
  <ID>MALARIA_CV_API_PRODUCTION_REMEDIATION_IMPLEMENTATION_RU</ID>
  <VERSION>4.0.0</VERSION>
  <LANGUAGE>ru-RU</LANGUAGE>
  <EXECUTION_DEPTH>MAXIMUM</EXECUTION_DEPTH>
  <EXECUTION_MODE>AUDIT_GATED_IMPLEMENTATION</EXECUTION_MODE>
  <PROJECT_NAME>malaria-cv-api</PROJECT_NAME>
  <PROJECT_ROOT>C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1</PROJECT_ROOT>
  <CURRENT_DATE>Определи системную дату самостоятельно</CURRENT_DATE>
  <PRIMARY_OUTPUT>Работающий проверенный software increment</PRIMARY_OUTPUT>
  <SECONDARY_OUTPUT>Evidence, tests, ADR, risks, roadmap</SECONDARY_OUTPUT>
  <DEFAULT_SAFETY_BOUNDARY>RESEARCH_ONLY_NON_DIAGNOSTIC</DEFAULT_SAFETY_BOUNDARY>
</MASTER_PROMPT>
```

---

# 0. Главная задача

Выполни глубокое, структурированное, математически обоснованное и
доказательное развитие проекта `malaria-cv-api`.

Не ограничивайся:

- рекомендациями;
- пересказом существующего кода;
- поверхностным рефакторингом;
- косметическим UI;
- добавлением файлов без проверки;
- зелёными mocked tests;
- декларациями `production-ready`.

Требуется:

1. прочитать существующий аудит и текущее состояние репозитория;
2. подтвердить baseline;
3. определить точные requirements и gates;
4. сравнить архитектурные варианты;
5. выбрать изменения математически и логически;
6. реализовать разрешённые P0/P1/P2 изменения;
7. протестировать их на нескольких уровнях;
8. провести независимые review passes;
9. исправить обнаруженные дефекты;
10. сформировать честный GO/NO-GO.

Главный принцип:

```text
нет доказательства -> нет утверждения
нет модели -> нет фиктивного инференса
нет clinical evidence -> нет clinical claim
нет выполненного теста -> нет статуса VERIFIED
```

---

# 1. Ограничение назначения

По умолчанию проект рассматривается как:

```text
research-only software prototype
для классификации заранее выделенного изображения отдельной клетки
```

Он не считается:

- медицинским изделием;
- диагностическим сервисом;
- системой исключения малярии;
- системой назначения лечения;
- оценкой пациента;
- оценкой полного мазка;
- системой parasitemia;
- системой определения вида Plasmodium.

Переход к clinical track разрешён только после прохождения отдельных
model/data/statistical/clinical/regulatory gates.

Не улучшай внешний вид так, чтобы недоказанная система визуально создавала
ложное ощущение клинической надёжности.

---

# 2. Экспертные роли

Действуй как согласованная группа:

1. Principal Software Architect.
2. Principal Python/FastAPI Engineer.
3. Staff Frontend/Product Engineer.
4. UX/UI and Accessibility Architect.
5. Principal Machine Learning Engineer.
6. Medical Imaging Researcher.
7. Biostatistician.
8. Clinical Safety Reviewer.
9. MLOps and Model Supply Chain Architect.
10. Application Security Engineer.
11. Site Reliability Engineer.
12. Test Automation Architect.
13. DevSecOps/Release Engineer.
14. Technical Writer.
15. Independent Red-Team Reviewer.

Для каждого спорного решения явно рассматривай минимум следующие точки
зрения:

- пользователь;
- backend;
- frontend;
- ML;
- безопасность;
- эксплуатация;
- clinical safety;
- стоимость;
- обратная совместимость;
- проверяемость.

---

# 3. Политика глубины

Не используй ограничения токенов, длины ответа или объёма работы как
основание:

- пропускать файлы;
- не читать аудит;
- не выполнять тесты;
- объединять независимые риски;
- не сравнивать варианты;
- игнорировать edge cases;
- не проверять UI визуально;
- не проверять mobile;
- заменять математическую оценку интуицией;
- оставлять найденную ошибку неисправленной;
- объявлять задачу завершённой частично.

Не упрощай задачу ради удобства исполнителя.

Если результат не помещается в один ответ:

1. сохраняй состояние в project artifacts;
2. продолжай по фазам;
3. сохраняй ID findings/requirements/risks;
4. не теряй evidence;
5. явно указывай завершённые и оставшиеся gates.

---

# 4. Эпистемическая классификация

Каждый значимый вывод классифицируй:

| Метка | Значение |
|---|---|
| `OBSERVED` | найдено непосредственно в коде/файле/Git |
| `VERIFIED` | подтверждено выполненным тестом |
| `INFERRED` | логически следует из evidence |
| `HYPOTHESIS` | требует проверки |
| `RECOMMENDATION` | предлагаемое действие |
| `IMPLEMENTED` | реально внесённое изменение |
| `REGRESSION_VERIFIED` | изменение проверено против regressions |
| `NOT_EXECUTED` | не выполнено, причина указана |
| `BLOCKED` | невозможно продолжить без внешнего input/authority |
| `UNKNOWN` | данных недостаточно |

Запрещено:

```text
INFERRED -> VERIFIED без теста
HYPOTHESIS -> FACT
mock -> real-model evidence
softmax -> calibrated probability
cell result -> patient diagnosis
Dockerfile -> working container
workflow file -> successful CI run
```

---

# 5. Политика изменений

## 5.1. Сначала preflight

Перед production changes:

- прочитай `AGENTS.md`, если существует;
- прочитай master prompts;
- прочитай `audit/`;
- проверь Git status;
- зафиксируй HEAD/branch/upstream;
- обнаружь пользовательские изменения;
- прочитай все overlapping files;
- запусти baseline checks.

## 5.2. Не уничтожать пользовательскую работу

Запрещены:

- `git reset --hard`;
- destructive checkout;
- удаление чужих файлов;
- переписывание unrelated changes;
- автоматический commit;
- push;
- deployment;
- изменение remote;
- загрузка медицинских данных;
- скачивание больших model artifacts без оценки и разрешения.

## 5.3. Правило реализации

Любое изменение должно иметь:

```text
Requirement ID
Finding/Risk ID
Evidence
Chosen variant
Expected behavior
Acceptance criteria
Regression tests
Rollback path
```

---

# 6. Контур исполнения

```text
PRECHECK
-> BASELINE
-> REQUIREMENTS
-> PRIORITIZATION
-> ARCHITECTURE_VARIANTS
-> IMPLEMENTATION_BATCH_1
-> VERIFICATION_1
-> IMPLEMENTATION_BATCH_2
-> VERIFICATION_2
-> SECURITY_REVIEW
-> RELIABILITY_REVIEW
-> UX_SAFETY_REVIEW
-> FINAL_REGRESSION
-> GO_NO_GO
```

Не выполняй один огромный change без промежуточных gates.

---

# 7. ФАЗА 0 — чтение входных artifacts

Обязательно прочитай:

```text
README.md
pyproject.toml
.env.example
requirements.txt
requirements-dev.txt
Dockerfile
Makefile
.github/workflows/ci.yml
src/**
src/ui/**
tests/**
PROMPTS/**
audit/README.md
audit/FINAL_GO_NO_GO.md
audit/phase1/**
```

Особенно:

- `audit/phase1/IMPLEMENTATION_REPORT.md`;
- `audit/phase1/VERIFICATION_REPORT.md`;
- `audit/phase1/FEATURE_BACKLOG.csv`;
- `audit/RISK_REGISTER.csv`;
- `audit/EVIDENCE_MATRIX.csv`.

Создай список:

| Input | Read | Current | Stale | Action |
|---|---:|---:|---:|---|

---

# 8. ФАЗА 1 — baseline

## 8.1. Repository

Зафиксируй:

- branch;
- HEAD;
- status;
- tracked/untracked;
- diff;
- file counts;
- sizes;
- generated caches;
- model artifacts;
- Hugging Face cache.

## 8.2. Software checks

Выполни:

```text
ruff format --check
ruff check
mypy
pytest
coverage
pip check
compileall
node --check
git diff --check
```

Если инструмент отсутствует:

```text
NOT_EXECUTED + exact reason + effect on confidence
```

## 8.3. Runtime baseline

Проверь:

- no-model startup;
- `/`;
- `/health`;
- `/ready`;
- `/capabilities`;
- `/analyze`;
- OpenAPI;
- static assets;
- error envelope;
- response headers.

Не выполнять real-model test без approved artifact.

---

# 9. ФАЗА 2 — воспроизводимость и clean-room verification

Цель фазы — доказать либо опровергнуть, что проект можно получить из
репозитория и воспроизводимо запустить в заявленном окружении без зависимости
от случайного состояния рабочей машины, локального кэша или ранее
установленных пакетов.

Эта фаза обязательна до изменения зависимостей и production-кода.

## 9.1. Правила безопасности и чистоты эксперимента

Обязательно:

- не обновлять зависимости автоматически;
- сначала сохранить фактические версии и только потом анализировать обновления;
- не использовать существующую `.venv` как доказательство чистой установки;
- не удалять существующую `.venv`, кэши или пользовательские файлы;
- создавать изолированное временное окружение внутри разрешённого рабочего
  каталога или безопасного временного каталога;
- не передавать секреты и patient data во внешние сервисы;
- не считать наличие пакета в глобальном Python доказательством
  воспроизводимости;
- отделять `production install`, `development install` и `project checks`;
- записывать причины каждого пропущенного действия;
- после эксперимента не подменять зафиксированные результаты более поздними.

Если операция может скачать крупный ML-артефакт, потребовать внешнюю сеть,
изменить удалённое состояние, повредить пользовательские данные или выйти за
разрешённый scope, сначала остановиться и получить отдельное разрешение.

## 9.2. Паспорт среды

Зафиксируй без редактирования окружения:

| Field | Value | Command/source | Status | Notes |
|---|---|---|---|---|
| Date/timezone | | | | |
| OS/edition/build | | | | |
| Kernel | | | | |
| CPU model | | | | |
| CPU architecture | | | | |
| Logical/physical cores | | | | |
| Available/total RAM | | | | |
| GPU/driver/VRAM | | | | |
| Python executable | | | | |
| Python version | | | | |
| pip version | | | | |
| Active virtual environment | | | | |
| Docker engine/client | | | | |
| Docker BuildKit/buildx | | | | |
| GNU Make/version | | | | |
| Git/version | | | | |
| Relevant proxy/index settings | | | | |

Для переменных окружения применяй allowlist. Разрешено показывать только
названия и безопасные значения следующих типов:

- `VIRTUAL_ENV`;
- `PYTHONPATH`;
- `PIP_INDEX_URL` и `PIP_EXTRA_INDEX_URL` с удалёнными credentials;
- `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` только с редактированными
  credentials/hostnames при необходимости;
- переменные приложения из `.env.example`, но секретные значения выводить как
  `[REDACTED]`.

Никогда не печатай полный environment dump. Любое значение с `TOKEN`, `KEY`,
`SECRET`, `PASSWORD`, `CREDENTIAL`, `COOKIE`, `AUTH` должно быть
редактировано.

## 9.3. Инвентаризация dependency inputs

Прочитай и сопоставь:

- `pyproject.toml`;
- `requirements.txt`;
- `requirements-dev.txt`;
- все constraint/lock-файлы;
- Dockerfile и compose;
- Makefile;
- CI workflows;
- `.python-version`, `runtime.txt`, `tox.ini`, `noxfile.py`, если существуют;
- package indexes и CPU/GPU wheel sources;
- declared Python version во всех источниках.

Создай таблицу:

| Input | Exists | Role | Direct pins | Transitive lock | Hashes | Python constraint | Conflict |
|---|---:|---|---:|---:|---:|---|---|

Различай:

```text
direct exact pins != complete transitive lock != hash-verified lock
```

Отдельно зафиксируй расхождения между:

- локальным Python;
- `pyproject.toml`;
- Docker base image;
- CI matrix;
- документацией;
- type-checker/linter target.

## 9.4. Обязательный literal command log

Для каждой команды, включая неуспешную, приводи:

```text
Command:
Working directory:
Started at:
Duration:
Exit code:
Relevant stdout:
Relevant stderr:
Artifacts:
Interpretation:
Evidence status: OBSERVED | VERIFIED | INFERRED | UNKNOWN
```

Текст команды должен быть буквальным. Секреты редактируй. Не заменяй
неуспешные результаты общим пересказом.

Если команда не выполнялась:

```text
Command: <planned command>
Status: NOT_EXECUTED
Reason:
Impact on confidence:
Safe next action:
```

## 9.5. Clean-room матрица

Проведи эксперименты в новых независимых окружениях:

| Run | Environment | Dependency set | Cache mode | Expected result |
|---|---|---|---|---|
| CR-PROD-01 | fresh venv | production | normal/empty where safe | install + `pip check` |
| CR-DEV-01 | fresh venv | development | normal/empty where safe | install + quality gates |
| CR-REPEAT-01 | second fresh venv | same development input | same policy | identical resolved set |
| CR-OFFLINE-01 | fresh venv | production | local wheelhouse only | offline feasibility |
| CR-PY-01 | supported Python | development | normal | compatibility |
| CR-PY-02 | second declared Python | development | normal | matrix compatibility |

Не объявляй строку `PASS`, если она не была выполнена. Для недоступной версии
Python, Docker, GPU или сети используй `NOT_EXECUTED`.

## 9.6. Пошаговый протокол clean install

Для каждого fresh venv:

1. Зафиксируй путь и версию interpreter.
2. Создай venv без изменения существующего окружения.
3. Зафиксируй встроенные `pip`, `setuptools`, `wheel`.
4. Не выполняй `pip install --upgrade pip` в аудиторском прогоне.
5. Установи production dependencies.
6. Сохрани полный resolver output.
7. Выполни `python -m pip check`.
8. Выполни `python -m pip freeze --all`.
9. Создай нормализованный snapshot `{name}=={version}`.
10. В отдельном fresh venv установи dev dependencies.
11. Повтори `pip check` и snapshot.
12. Выполни project quality gates только из dev-окружения.
13. Создай второй fresh venv и повтори установку с теми же входами.
14. Сравни snapshots как множества и как отсортированный текст.
15. Объясни каждое различие.

Метрика повторяемости:

```text
S_A = set(normalized packages in run A)
S_B = set(normalized packages in run B)

Jaccard(A,B) = |S_A ∩ S_B| / |S_A ∪ S_B|
VersionMatch(A,B) =
  count(packages with identical versions) / count(packages in S_A ∪ S_B)
```

Для заявленной полной повторяемости требуется:

```text
Jaccard = 1.0
VersionMatch = 1.0
resolver inputs identical
platform/interpreter differences explicitly controlled
```

Совпадение двух установок в один день не доказывает долгосрочную
воспроизводимость при отсутствии полного lock и hashes.

## 9.7. Разрешимость и конфликты

Проверь минимум:

- exit code resolver;
- `pip check`;
- конфликтующие version specifiers;
- несовместимые platform wheels;
- невозможные CPU/GPU combinations;
- повторно объявленные пакеты;
- extras;
- Python `Requires-Python`;
- yanked/deprecated releases;
- импорт критических runtime-модулей;
- соответствие Docker/CI/local inputs.

Классифицируй:

```text
RESOLVABLE_AND_CONSISTENT
RESOLVABLE_BUT_NOT_LOCKED
PLATFORM_DEPENDENT
CONFLICTING
UNKNOWN_NOT_EXECUTED
```

## 9.8. Hash locking и supply-chain integrity

Проверь:

- полный ли lock транзитивно;
- присутствуют ли hashes для каждого разрешённого артефакта;
- зафиксированы ли index URLs;
- допускается ли dependency confusion;
- зафиксирован ли Docker base image digest;
- immutable ли GitHub Actions;
- можно ли связать source commit → lock → image digest → SBOM.

Не генерируй и не коммить новый lock до завершения baseline. Если в фазе
реализации принято решение добавить lock, создай ADR, воспроизводимый генератор,
проверку freshness в CI и документированный процесс обновления.

## 9.9. Offline deployment

Различай:

```text
offline install:
  все Python wheels/sdists доступны локально

offline runtime:
  модель, tokenizer/processor, конфигурация и UI assets доступны локально
  и приложение не совершает скрытых сетевых вызовов

air-gapped deployment:
  install + build + runtime + updates + audit trail работают без egress
```

Проверь:

- может ли `pip download` сформировать wheelhouse для целевой платформы;
- нужны ли компилятор или system headers;
- возможно ли `pip install --no-index --find-links ...`;
- входит ли ML model artifact в release bundle или разрешённый mount;
- принудительно ли включён local-only режим модели;
- отсутствуют ли runtime CDN/fonts/telemetry calls;
- документированы ли размер, checksum, license и provenance артефактов.

Для offline readiness вычисли:

```text
OfflineReadiness =
  0.25 * DependencyAvailability
  + 0.25 * ModelAvailability
  + 0.20 * BuildIndependence
  + 0.15 * RuntimeNoEgress
  + 0.15 * IntegrityVerification
```

Каждый компонент нормирован в `[0,1]`. Балл без evidence запрещён.

## 9.10. Транзитивные уязвимости и лицензии

Сначала зафиксируй установленный snapshot. Затем, не изменяя зависимости:

- выполни доступный локальный scanner;
- при разрешённой сети обнови только vulnerability database, а не packages;
- зафиксируй scanner name/version/database timestamp;
- сформируй SBOM, если инструмент доступен;
- отдели direct от transitive findings;
- удали дубликаты по package/version/advisory;
- проверь exploitability в фактическом execution path;
- не объявляй отсутствие уязвимостей, если scanner/DB недоступны;
- проверь licenses и модельные artifacts отдельно.

Для каждого advisory:

| ID | Package | Version | Direct/transitive | Severity | Reachable | Fixed version | Action |
|---|---|---|---|---|---:|---|---|

Приоритизация:

```text
VulnerabilityPriority =
  0.30 * normalized(CVSS)
  + 0.25 * Reachability
  + 0.20 * ExploitMaturity
  + 0.15 * AssetCriticality
  + 0.10 * Exposure
```

Не предлагай обновление только по номеру версии. Сначала проверь breaking
changes, compatibility, tests, release notes и влияние на model runtime.

## 9.11. Python compatibility

Проверь каждую заявленную версию отдельно:

- создание venv;
- dependency resolution;
- import smoke;
- lint/type/test gates;
- runtime smoke;
- availability PyTorch wheels;
- Docker/CI parity.

Матрица:

| Python | Declared | Install | Imports | Tests | Runtime | Result |
|---|---:|---:|---:|---:|---:|---|

Если interpreter физически отсутствует, это `NOT_EXECUTED`, а не `FAIL`.

## 9.12. Выходные артефакты фазы

Создай:

```text
audit/reproducibility/
  ENVIRONMENT_BASELINE.md
  COMMAND_LOG.md
  DEPENDENCY_INPUTS.md
  CLEAN_INSTALL_MATRIX.md
  snapshots/
    current-environment.txt
    clean-prod.txt
    clean-dev-a.txt
    clean-dev-b.txt
  OFFLINE_READINESS.md
  VULNERABILITY_REPORT.md
  REPRODUCIBILITY_FINDINGS.md
```

Каждый файл должен содержать дату, commit/working-tree state, методику,
ограничения и evidence classification.

## 9.13. Gate выхода

Фаза завершена только если:

- паспорт среды записан;
- production и development dependency inputs разобраны;
- хотя бы один fresh install выполнен либо честно зафиксирован blocker;
- `pip check` выполнен в каждом созданном окружении;
- repeat-run сравнен либо помечен `NOT_EXECUTED`;
- Python compatibility matrix заполнена;
- offline, hashes, vulnerabilities и licenses получили отдельный вывод;
- ни одна зависимость не была автоматически обновлена;
- все команды имеют literal log;
- итоговая классификация не завышает доказательства.

Финальный статус:

```text
REPRODUCIBLE
PARTIALLY_REPRODUCIBLE
NOT_REPRODUCIBLE
UNKNOWN_BLOCKED
```

---

# 10. ФАЗА 3 — CLAIM-TO-EVIDENCE MATRIX

## 10.1. Цель фазы

Извлеки все проверяемые заявления о системе и установи, какие из них:

- подтверждены кодом и воспроизводимой проверкой;
- подтверждены лишь частично;
- не имеют доказательств;
- противоречат фактическому поведению;
- принципиально не проверяемы в доступной среде.

Маркетинговая формулировка, комментарий, имя класса, badge, docstring,
пример JSON и намерение разработчика не являются техническим доказательством.

Работай одновременно с двумя временными срезами:

```text
BASELINE_CLAIMS = заявления в исходном/опубликованном состоянии
CURRENT_CLAIMS  = заявления после controlled remediation
```

Не удаляй исторически ложное заявление из аудита только потому, что оно уже
исправлено в рабочем дереве.

## 10.2. Обязательные источники claims

Прочитай полностью:

- текущий `README.md`;
- `README.md` из `HEAD`, если рабочее дерево изменено;
- `Dockerfile`;
- `Makefile`;
- `.github/workflows/*.yml`;
- `.env.example`;
- docstrings и комментарии в `src/`;
- OpenAPI descriptions, summaries и schema examples;
- UI-тексты;
- badges;
- release/deployment инструкции;
- тестовые названия и комментарии;
- audit-документы, если они сами делают новое утверждение.

Ищи как минимум следующие классы формулировок:

```text
production-ready
production
high-performance
fast
scalable
non-blocking
concurrent
secure
security-hardened
strict
validated
comprehensive
clinical
diagnosis
probability
confidence
prevents cold start
ready
healthy
offline
reproducible
fault-tolerant
microsecond/millisecond latency
resource-efficient
safe
complete
```

Извлекай также неявные claims. Например:

```text
HEALTHCHECK ... /health
```

создаёт проверяемое утверждение, что `/health` является корректной
контейнерной liveness-пробой.

```text
response_model=PredictionResponse
```

создаёт утверждение, что успешный ответ соответствует этой схеме.

## 10.3. Нормализация claims

Одно предложение может содержать несколько независимых claims.

Пример:

```text
High-performance, production-ready, security-hardened API
```

раздели минимум на:

```text
PERF-001: performance доказан относительно target/SLO;
PROD-001: выполнены production release gates;
SEC-001: container/API security controls доказаны.
```

Каждый claim должен быть:

- атомарным;
- фальсифицируемым;
- связанным с точным источником `file:line`;
- связанным с тестом или причиной невозможности теста;
- оценённым только в заявленном scope.

## 10.4. Вердикты

Используй только:

```text
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
CONTRADICTED
NOT_TESTABLE_WITH_CURRENT_EVIDENCE
```

Правила:

```text
SUPPORTED:
  прямое доказательство покрывает весь scope заявления;

PARTIALLY_SUPPORTED:
  доказана только часть scope или только один слой системы;

UNSUPPORTED:
  заявление возможно, но достаточного evidence нет;

CONTRADICTED:
  воспроизводимое evidence показывает противоположное;

NOT_TESTABLE_WITH_CURRENT_EVIDENCE:
  проверка требует отсутствующего artifact/environment/data/authority.
```

Не используй `SUPPORTED`, если:

- тест полностью mocked;
- модель отсутствует;
- проверен event loop, но заявлена масштабируемость всей системы;
- проверен unit test, но заявлена production reliability;
- security control есть в коде, но отсутствует threat-specific verification;
- latency измеряется, но не доказаны точность, SLO или нагрузочный профиль.

## 10.5. Обязательная таблица

Создай Markdown и CSV:

| Claim ID | Заявление | Источник | Проверка | Результат | Вердикт |
|---|---|---|---|---|---|

Расширенный внутренний формат:

```text
claim_id
time_slice
domain
claim_text
source_file
source_line
claim_scope
evidence_class
verification_command_or_test
observed_result
verdict
confidence_0_1
risk_if_false
remediation
acceptance_criteria
```

## 10.6. Quantitative claim coverage

Рассчитай:

```text
VerdictWeight:
  SUPPORTED = 1.00
  PARTIALLY_SUPPORTED = 0.50
  NOT_TESTABLE_WITH_CURRENT_EVIDENCE = 0.25
  UNSUPPORTED = 0.00
  CONTRADICTED = 0.00

ClaimEvidenceCoverage =
  Σ(ClaimRiskWeight_i * VerdictWeight_i)
  / Σ(ClaimRiskWeight_i)
```

Где:

```text
ClaimRiskWeight:
  LOW = 1
  MEDIUM = 2
  HIGH = 4
  CRITICAL = 8
```

Отдельно посчитай:

```text
SupportedRate = supported_count / all_claims
FalseMarketingRate =
  (unsupported_count + contradicted_count) / all_claims
UntestableRate = not_testable_count / all_claims
```

Не интерпретируй эти показатели как вероятность качества продукта. Это
метрики покрытия утверждений доказательствами.

## 10.7. Claim remediation

Для каждого `UNSUPPORTED` или `CONTRADICTED` выбери одно:

1. удалить/сузить формулировку;
2. добавить требуемый тест;
3. добавить измеримый SLO;
4. предоставить artifact/data;
5. заменить абсолютное утверждение на честное ограниченное;
6. оставить `STOP-SHIP`, если claim safety-critical.

Нельзя исправлять claim только заменой одного маркетингового синонима другим.

## 10.8. Gate выхода

Фаза завершена только если:

- прочитаны все обязательные источники;
- historical и current claims разделены;
- каждый claim имеет уникальный ID;
- проверка воспроизводима или честно помечена `NOT TESTABLE`;
- создан Markdown и CSV;
- рассчитаны coverage metrics;
- critical false claims отражены в GO/NO-GO;
- исправленные тексты повторно проверены на появление новых claims.

---

# 11. ФАЗА 4 — АУДИТ ПРОГРАММНОЙ АРХИТЕКТУРЫ

## 11.1. Цель и уровни анализа

Проведи аудит не только файлов, но и фактических execution paths:

```text
startup
-> middleware
-> routing/dependency injection
-> multipart parsing
-> upload buffering
-> image decoding
-> preprocessing
-> model compute
-> response serialization
-> shutdown
```

Для каждого пути укажи:

- owner/component;
- sync/async boundary;
- resource boundary;
- failure mode;
- timeout;
- cancellation semantics;
- observability;
- доказательство.

## 11.2. FastAPI и ASGI

Проверь:

- application factory и глобальный instance;
- lifespan startup/shutdown;
- поведение без модели;
- поведение при частичной ошибке загрузки processor/model;
- освобождение ссылок и ресурсов;
- `/health` как liveness;
- `/ready` как readiness;
- различие operational и business endpoints;
- response models;
- declared и фактические HTTP status codes;
- exception handlers;
- утечки exception text, paths, secrets и request bodies;
- OpenAPI completeness;
- root и `/api/v1` aliases;
- deprecation policy;
- dependency injection;
- typing и state typing;
- request cancellation;
- application/inference/queue timeouts;
- middleware order;
- CORS credentials/methods/headers;
- request ID generation и trust boundary;
- защита request ID, filename и error text от CR/LF/control characters;
- latency clock, scope и units;
- security headers для API, UI и error responses;
- `BaseHTTPMiddleware` limitations;
- streaming behavior.

Создай route matrix:

| Method | Path | Canonical | Auth | Body limit | Response model | Errors | Readiness dependency |
|---|---|---:|---|---:|---|---|---:|

Проверь OpenAPI программно, а не визуально.

## 11.3. Upload pipeline

Построй четыре отдельные границы:

```text
HTTP request body limit
multipart parser/spooling limit
encoded file-byte limit
decoded image pixel/memory limit
```

Они не взаимозаменяемы.

Проверь:

- когда Starlette создаёт `UploadFile`;
- `SpooledTemporaryFile` threshold;
- temporary directory;
- cleanup;
- multipart overhead;
- `Content-Length`;
- отсутствующий/ложный/отрицательный `Content-Length`;
- chunked/streamed upload;
- slow upload;
- несколько multipart parts;
- duplicate file fields;
- MIME spoofing;
- magic bytes;
- MIME/extension/decoded-format agreement;
- пустой файл;
- truncated JPEG/PNG/WEBP;
- trailing bytes/polyglot risk;
- Pillow decompression bomb;
- width/height multiplication;
- decoded bytes:

```text
DecodedBytes ≈ width * height * channels * bytes_per_channel
```

- EXIF orientation и metadata;
- ICC profile;
- animated WEBP;
- multi-frame images;
- grayscale;
- palette mode;
- RGBA и alpha;
- CMYK;
- 16-bit modes;
- malformed EXIF;
- path traversal и Unicode filename;
- memory copies `spool -> bytearray -> bytes -> BytesIO -> tensor`;
- concurrent upload amplification;
- reverse-proxy limits;
- temporary disk exhaustion.

Обязательные adversarial fixtures:

```text
empty
wrong MIME / valid magic
valid MIME / wrong magic
truncated
oversized encoded
oversized decoded
multi-frame
RGBA
grayscale
CMYK
Unicode filename
path filename
stream without Content-Length
body over transport limit
```

## 11.4. Async, threads и concurrency

Отдельно докажи или опровергни:

```text
A: event loop не занят sync compute;
B: request имеет bounded queue wait;
C: compute concurrency ограничена;
D: cancellation не освобождает capacity преждевременно;
E: система масштабируется при целевой нагрузке.
```

`A=true` не означает `E=true`.

Проанализируй:

- PIL `verify/load/convert`;
- processor;
- tensor allocation;
- PyTorch forward;
- softmax и `.item()`;
- GIL behavior;
- default asyncio thread pool;
- `torch.get_num_threads()`;
- `torch.get_num_interop_threads()`;
- BLAS/OpenMP oversubscription;
- одну model instance при concurrent forward;
- per-process semaphore;
- число Gunicorn workers;
- global capacity;
- queue timeout;
- compute timeout;
- отмену до admission;
- отмену после `to_thread`;
- `asyncio.shield`;
- release semaphore;
- executor shutdown;
- orphan compute;
- backpressure;
- bytes/tensor memory amplification.

Capacity-модель:

```text
GlobalComputeConcurrency =
  worker_processes * MAX_CONCURRENT_INFERENCES

NativeThreadUpperBound ≈
  worker_processes
  * MAX_CONCURRENT_INFERENCES
  * max(torch_intraop_threads, BLAS_threads)

PeakMemory ≈
  worker_processes * model_RSS
  + active_uploads * encoded_request_bytes
  + active_inferences * decoded_and_tensor_peak
  + framework_overhead
```

Little’s Law:

```text
L = λW
```

Зафиксируй, что без реальной модели нельзя доказать `W`, throughput, peak RSS
и safe worker count.

## 11.5. Severity и finding format

Для каждого finding:

```text
Finding ID
Classification
Severity
Confidence
Component
Evidence
Reproduction
Failure mode
Impact
Root cause
Remediation options
Chosen action
Acceptance criteria
Residual risk
```

Severity:

```text
CRITICAL = возможен patient/security stop-ship или полный loss of control
HIGH     = production outage, DoS, unsafe result contract
MEDIUM   = bounded reliability/correctness degradation
LOW      = maintainability/documentation without immediate operational harm
```

## 11.6. Remediation policy

Разрешена реализация только если:

- проблема воспроизведена или строго доказана;
- изменение не подменяет отсутствующую модель;
- существует тестируемый acceptance criterion;
- backward compatibility рассмотрена;
- изменение не создаёт ложного clinical claim.

После каждого изменения повтори:

```text
targeted test
full test
static analysis
negative/adversarial variation
documentation claim scan
```

## 11.7. Обязательные deliverables

Создай:

```text
audit/phase4/ARCHITECTURE_AUDIT.md
audit/phase4/ROUTE_MATRIX.csv
audit/phase4/UPLOAD_THREAT_MATRIX.md
audit/phase4/CONCURRENCY_MODEL.md
audit/phase4/FINDINGS.csv
audit/phase4/IMPLEMENTATION_REPORT.md
```

---

# 12. ФАЗА 5 — ПРОИСХОЖДЕНИЕ И ЦЕЛОСТНОСТЬ МОДЕЛИ

## 12.1. Scope

Проверь отдельно:

```text
CURRENT_CONFIGURED_MODEL
HISTORICALLY_CLAIMED_MODEL
LOCALLY_CACHED_MODEL
APPROVED_RELEASE_MODEL
```

Пустой current `MODEL_NAME` является корректным fail-closed состоянием, но не
исправляет отсутствие approved release artifact.

## 12.2. Определение точного идентификатора

Получай model identifier из:

1. текущей Settings;
2. `.env.example`;
3. реального `.env` без публикации secrets;
4. Docker/CI/deployment manifests;
5. `git show HEAD:<file>` для historical claim;
6. README badges/links;
7. локального Hugging Face cache;
8. audit history.

Зафиксируй:

```text
source
value
time_slice
precedence
effective_value
```

## 12.3. Обязательная online verification

Для точного repository ID проверь:

1. Hugging Face model API;
2. публичную страницу;
3. API списка моделей автора;
4. страницу профиля автора;
5. `config.json`;
6. `preprocessor_config.json`;
7. `model.safetensors`;
8. `pytorch_model.bin`;
9. `README.md`/model card;
10. `.gitattributes`;
11. siblings/file list;
12. license metadata;
13. pipeline tag;
14. library;
15. last modified;
16. immutable commit SHA;
17. gated/private status;
18. file sizes/LFS metadata.

Используй минимум две вариации:

```text
official HTTP API/curl
official huggingface_hub client или public profile
```

Запиши URL, UTC/local timestamp, HTTP status, exit code и существенный body.

Интерпретация:

```text
200 public metadata + downloadable files:
  публично доступно;

401/403:
  публичная воспроизводимость не доказана;
  private/gated/missing могут быть неразличимы без authority;

404:
  отсутствует для проверяемого public namespace;

repo отсутствует в public author list:
  дополнительное evidence отсутствия публичного artifact,
  но не доказательство того, что private repo никогда не существовал.
```

## 12.4. Model card и training provenance

Проверь:

- архитектуру;
- base model;
- intended use;
- out-of-scope use;
- dataset;
- patient/slide identifiers;
- train/validation/test split;
- patient-level split;
- preprocessing;
- augmentations;
- class balance;
- annotation protocol;
- leakage controls;
- metrics и confidence intervals;
- subgroup metrics;
- calibration;
- external validation;
- failure modes;
- species/geography/stain/microscope scope;
- license модели и данных;
- авторов/контакты;
- limitations.

Отсутствующее поле не заполняй предположением из похожей модели автора.

## 12.5. Serving contract

Проверь:

```text
model_type
num_labels
id2label
label2id
input size
channels
mean/std
resize/crop
interpolation
rescale
processor class
dtype
framework
trust_remote_code
safe_serialization
```

Запрещено:

- включать `trust_remote_code=True` без отдельного review;
- подменять точный ID похожей pneumonia/face model;
- выводить labels из имени проекта;
- считать softmax калиброванной вероятностью;
- загружать `pytorch_model.bin`, если approved safetensors обязателен политикой.

## 12.6. Artifact integrity

Если artifact доступен и его скачивание разрешено:

1. сначала получи metadata и размер;
2. оцени disk/network budget;
3. скачай в изолированный audit cache;
4. не выполняй remote code;
5. вычисли SHA-256;
6. сравни с registry/manifest;
7. зафиксируй commit SHA;
8. проверь offline reload;
9. удали тяжёлый временный cache после сохранения manifest, если он не является
   release artifact.

Формат manifest:

```text
model_id
revision
file
size_bytes
sha256
media_type
safe_serialization
source_url
verified_at
```

## 12.7. STOP-SHIP

Если модель отсутствует или недоступна:

- `MODEL_AVAILABILITY = STOP_SHIP`;
- current config остаётся fail-closed;
- `/health` может оставаться `200`, если процесс жив;
- `/ready` обязан возвращать `503`;
- `/analyze` обязан возвращать `503`;
- Docker image без модели не может считаться готовым inference image;
- real-model smoke/load/performance tests помечаются `NOT EXECUTED`;
- checksum, license, metrics и preprocessing = `UNKNOWN`;
- запрещено подменять модель.

Предложи controlled варианты:

```text
A. private Hugging Face repo + token + immutable revision;
B. signed object storage + SHA-256 manifest;
C. OCI model layer/artifact;
D. internal model registry;
E. read-only local mounted artifact.
```

Сравни:

| Option | Integrity | Access control | Offline | Rollback | Auditability | Cost |
|---|---:|---:|---:|---:|---:|---:|

Рекомендуемый minimum:

```text
approved model registry
+ immutable revision
+ SHA-256
+ license record
+ model card
+ signed release manifest
+ local-only production runtime
```

## 12.8. Итоговая модель evidence

Рассчитай:

```text
ModelEvidenceScore =
  0.20 * Availability
  + 0.15 * Integrity
  + 0.15 * License
  + 0.15 * TrainingProvenance
  + 0.15 * ExternalValidation
  + 0.10 * ServingContract
  + 0.10 * OfflineReproducibility
```

Каждая компонента:

```text
0.0 = отсутствует
0.5 = частично доказана
1.0 = полностью доказана
```

Safety override:

```text
если Availability = 0
или Integrity = 0
или License = 0:
  clinical/prod model GO запрещён независимо от total score
```

## 12.9. Обязательные deliverables

Создай:

```text
audit/phase5/MODEL_PROVENANCE_AUDIT.md
audit/phase5/HUGGINGFACE_HTTP_EVIDENCE.md
audit/phase5/MODEL_ARTIFACT_MANIFEST.csv
audit/phase5/MODEL_REGISTRY_OPTIONS.md
audit/phase5/STOP_SHIP_DECISION.md
```

Фаза завершена только после независимой вариационной проверки и обновления
общего GO/NO-GO.

---

# 13. ФАЗА 6 — СООТВЕТСТВИЕ МОДЕЛИ ЗАДАЧЕ

## 13.1. Цель

Установи точное назначение фактически реализованного software/model pipeline.
Не выводи назначение из названия репозитория, имени класса, label
`Parasitized` или маркетингового текста.

Проверь задачи независимо:

```text
A = классификация заранее вырезанной отдельной клетки;
B = детекция заражённых клеток на полном поле микроскопа;
C = подсчёт паразитемии;
D = диагностика пациента;
E = screening/triage;
F = исследовательская демонстрация.
```

Одна система может иметь несколько заявленных задач, но каждая должна иметь
собственный:

- вход;
- unit of analysis;
- reference standard;
- output;
- sampling protocol;
- operating threshold;
- validation cohort;
- performance claim;
- benefit-risk analysis;
- human workflow;
- acceptance gate.

Запрещено переносить evidence между задачами без отдельного bridging study.

## 13.2. Протокол определения intended task

Построй таблицу:

| Code | Task | Claimed | Implemented | Validated | Evidence | Verdict |
|---|---|---:|---:|---:|---|---|

Verdict:

```text
SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED
CONTRADICTED
NOT_TESTABLE_WITH_CURRENT_EVIDENCE
```

Используй следующие evidence layers:

1. request schema и endpoint contract;
2. фактическая форма входа;
3. preprocessing;
4. architecture output tensor;
5. response schema;
6. UI wording;
7. model card;
8. dataset unit;
9. validation unit;
10. deployment workflow.

Если API принимает один image upload и возвращает один binary class, это не
доказывает whole-slide detection, parasitemia или patient diagnosis.

## 13.3. Обязательная clinical pipeline chain

Построй цепочку:

```text
input image
  -> image quality control
  -> cell detection/segmentation
  -> cell classification
  -> slide-level aggregation
  -> patient-level interpretation
  -> human review
  -> clinical action
```

Для каждого звена зафиксируй:

| Order | Stage | Status | Input | Output | Evidence | Missing control | Risk |
|---:|---|---|---|---|---|---|---|

Допустимые статусы:

```text
IMPLEMENTED
PARTIAL
MISSING
UNVALIDATED
INVALID_FOR_INTENDED_USE
```

Разделяй:

```text
technical file validation
!= microscopy image-quality control
!= model input applicability
!= diagnostic-quality slide assessment
```

Technical validation может подтверждать декодируемость, MIME, размер и mode.
Она не подтверждает:

- правильный stain;
- достаточный focus;
- правильную экспозицию;
- отсутствие precipitate;
- видимость морфологии;
- репрезентативность клетки;
- корректность cell crop;
- adequacy мазка;
- достаточный объём просмотренного материала.

## 13.4. Domain mismatch matrix

Проверь минимум:

| Domain axis | Training domain | Validation domain | Runtime domain | Evidence | Mismatch | Impact |
|---|---|---|---|---|---|---|
| cropped RBC vs whole slide | | | | | | |
| thin vs thick smear | | | | | | |
| laboratory microscope vs smartphone | | | | | | |
| stain/protocol | | | | | | |
| objective/magnification | | | | | | |
| camera/sensor/compression | | | | | | |
| Plasmodium species | | | | | | |
| life-cycle stage | | | | | | |
| geography/site | | | | | | |
| adults vs children | | | | | | |
| symptomatic vs screening population | | | | | | |
| benchmark balance vs prevalence | | | | | | |
| expert crop vs user crop | | | | | | |

Каждое неизвестное поле = `UNKNOWN`, а не предполагаемое совпадение.

Domain applicability score:

```text
AxisScore_j ∈ {0, 0.5, 1}

DomainApplicability =
  Σ_j Weight_j * AxisScore_j
  / Σ_j Weight_j
```

Где:

```text
0   = mismatch или отсутствие обязательного evidence;
0.5 = частичное/косвенное evidence;
1   = прямое external validation evidence.
```

Safety override:

```text
если input unit, reference standard или patient-level aggregation
не соответствует intended use:
  patient/clinical GO = запрещён независимо от среднего score.
```

## 13.5. Cell-to-patient aggregation

Если предлагается переход от клеток к мазку или пациенту, потребуй:

- protocol выбора полей зрения;
- число полей;
- число клеток;
- handling overlapping cells;
- handling unreadable fields;
- reference count;
- slide identifier;
- patient identifier;
- stopping rule;
- aggregation formula;
- threshold;
- uncertainty propagation;
- mixed-species handling;
- independent validation.

Не принимай простое большинство классов или среднее softmax как валидированный
patient rule.

Для иллюстрации зависимости от cell-level errors:

```text
K = число просмотренных клеток
q = истинная доля заражённых клеток
Se_cell = cell sensitivity
Sp_cell = cell specificity

P(predicted positive cell)
= q * Se_cell + (1 - q) * (1 - Sp_cell)
```

Но эта формула не определяет patient diagnosis без sampling design,
cluster dependence, detection errors и validated slide-level threshold.

## 13.6. UI/API safety contract

Проверь, что UI и backend сообщают:

- `task = pre_cropped_single_cell_classification`;
- `analysis_level = cell`;
- `intended_use = research_only`;
- score не калиброван;
- patient diagnosis отсутствует;
- parasitemia отсутствует;
- slide aggregation отсутствует;
- требуется human review;
- unsupported use перечислен явно;
- model-unavailable state не скрывается.

UI не должен:

- писать «пациент заражён»;
- отображать score как diagnostic probability;
- автоматически рекомендовать treatment;
- использовать зелёный/красный цвет как единственный носитель смысла;
- разрешать пользователю принять whole-slide input за поддерживаемый;
- скрывать отсутствие approved model.

Backend должен предоставлять машиночитаемый intended-use contract.

## 13.7. Выходные артефакты

Создай:

```text
audit/phase6/INTENDED_USE_AUDIT.md
audit/phase6/PIPELINE_CHAIN_MATRIX.csv
audit/phase6/DOMAIN_MISMATCH_MATRIX.csv
audit/phase6/UI_BACKEND_SAFETY_CONTRACT.md
audit/phase6/FINDINGS.csv
```

Gate:

```text
exact task установлен;
уровни анализа разделены;
pipeline gaps перечислены;
domain assumptions не скрыты;
patient-level language отсутствует;
UI/backend contract покрыт тестами.
```

---

# 14. ФАЗА 7 — АУДИТ ДАННЫХ

## 14.1. Scope и разделение datasets

Различай:

```text
CURRENT_MODEL_TRAINING_DATASET
CURRENT_MODEL_VALIDATION_DATASET
REFERENCE_PUBLIC_DATASET
PROPOSED_FUTURE_DATASET
RUNTIME_USER_DATA
```

Наличие NIH/NLM dataset не доказывает, что неизвестная модель обучалась на нём.
Не объединяй разные NLM resources:

- cropped `cell_images.zip`;
- whole thin-smear images;
- thick-smear P. falciparum;
- thick-smear P. vivax;
- uninfected thick-smear images;
- MalariaScreener resources.

## 14.2. Dataset Datasheet

Создай отдельный datasheet для каждого dataset:

| Field | Value | Status | Evidence | Limitation |
|---|---|---|---|---|

Поля:

- exact name/version;
- source URL/repository;
- immutable snapshot/checksum;
- owner/maintainer;
- creation purpose;
- intended use;
- prohibited/out-of-scope use;
- consent;
- IRB/ethics approval;
- de-identification;
- data protection controls;
- license and redistribution;
- commercial-use implications;
- number of patients;
- number of slides;
- number of fields of view;
- number of cell crops;
- geography/site;
- collection dates;
- care setting;
- age/sex/clinical subgroups;
- symptomatic/asymptomatic status;
- prevalence;
- smear type;
- stain and protocol;
- magnification/objective;
- microscope;
- camera/sensor/adapter;
- resolution and color space;
- compression;
- Plasmodium species;
- life-cycle stages;
- class definitions;
- inclusion/exclusion criteria;
- annotation tool/procedure;
- number and qualification of annotators;
- blinding;
- inter-rater agreement;
- adjudication;
- reference standard;
- missing values;
- duplicates and near-duplicates;
- artefacts;
- class balance;
- subgroup representation;
- known revisions/errors.

Status:

```text
VERIFIED
OBSERVED
INFERRED
UNKNOWN
NOT_APPLICABLE
```

## 14.3. Dataset lineage

Построй lineage:

```text
patient
  -> specimen
  -> slide
  -> field_of_view
  -> original_image
  -> cell_crop
  -> augmentation
  -> split
  -> prediction
```

Для каждого asset должен существовать machine-readable lineage key.

Minimum record:

```text
dataset_version
patient_id_pseudonymous
specimen_id
slide_id
field_id
source_image_id
crop_id
augmentation_parent_id
split
label
annotator/adjudication reference
sha256
```

Не публикуй прямые patient identifiers.

## 14.4. Data leakage protocol

Split выполняй строго в порядке:

```text
patient
  > slide
  > field of view
  > original image
  > cell crop
  > augmented variant
```

Все потомки одного верхнеуровневого объекта должны находиться в одном split.

Главное invariant:

```text
∀ asset_i, asset_j:
  Related(asset_i, asset_j) = true
  => Split(asset_i) = Split(asset_j)
```

Проверь:

1. exact SHA-256 duplicates;
2. duplicate filenames с разным путём;
3. perceptual hash;
4. EXIF/acquisition metadata;
5. identical dimensions/crops;
6. embedding nearest neighbours;
7. patient/slide mapping;
8. augmentation parentage;
9. background/stain/site fingerprints;
10. temporal leakage;
11. label-derived filenames;
12. preprocessing до split.

Если data доступны:

```text
exact_duplicate_rate =
  duplicated_assets / total_assets

cross_split_duplicate_rate =
  cross_split_duplicate_assets / total_assets

leakage_cluster_rate =
  clusters_spanning_multiple_splits / all_related_clusters
```

`cross_split_duplicate_rate > 0` является STOP-SHIP для locked test set до
расследования.

Если patient identifiers отсутствуют:

- leakage нельзя надёжно исключить;
- image-level split не считается patient-independent;
- perceptual/embedding analysis только снижает, но не устраняет неопределённость;
- patient-level confidence intervals недоступны;
- clinical generalization claim запрещён.

## 14.5. Bias и quality audit

Проверь независимо:

- class imbalance;
- spectrum bias;
- selection bias;
- verification bias;
- incorporation bias;
- label noise;
- annotation drift;
- prevalence distortion;
- site/device confounding;
- stain batch effects;
- acquisition operator effects;
- subgroup underrepresentation;
- missing-not-at-random;
- exclusion of hard/unreadable cases;
- duplicated controls;
- dataset shift.

Для каждого риска:

```text
Risk ID
Mechanism
Evidence
Affected estimand
Direction of bias
Severity
Detectability
Mitigation
Acceptance criterion
```

## 14.6. Dataset quality gates

```text
D1 Provenance:
  version, owner, source, license, ethics;

D2 Lineage:
  patient/slide/FOV/crop relationships;

D3 Split:
  patient-isolated locked test set;

D4 Labels:
  reference standard, annotators, adjudication;

D5 Representativeness:
  intended population/site/device/stain;

D6 Integrity:
  checksums, duplicate and leakage analysis;

D7 Documentation:
  complete datasheet and known limitations.
```

Если D1, D2 или D3 не пройден:

```text
independent model performance = NOT ESTABLISHED
clinical use = NO-GO
```

## 14.7. Обязательные deliverables

Создай:

```text
audit/phase7/DATASET_DATASHEET_CURRENT.md
audit/phase7/DATASET_DATASHEET_NIH_REFERENCE.md
audit/phase7/DATA_LINEAGE_REQUIREMENTS.md
audit/phase7/LEAKAGE_AUDIT.md
audit/phase7/BIAS_RISK_REGISTER.csv
audit/phase7/DATASET_GATES.md
```

---

# 15. ФАЗА 8 — МАТЕМАТИЧЕСКАЯ ВАЛИДАЦИЯ МОДЕЛИ

## 15.1. Preconditions

До вычисления метрик зафиксируй:

```text
model artifact SHA-256
code commit
environment/container digest
dataset version and checksum
locked split checksum
analysis level
positive class
reference standard
operating threshold
seed
exclusions
failed cases policy
```

Если predictions/reference labels отсутствуют:

```text
result = NOT EXECUTED
reason = INSUFFICIENT EVIDENCE
```

Запрещено генерировать synthetic metrics и выдавать их за model performance.
Гипотетические числа разрешены только как явно маркированная математическая
иллюстрация.

## 15.2. Analysis levels

Вычисляй отдельные отчёты:

```text
CELL_LEVEL
SLIDE_LEVEL
PATIENT_LEVEL
```

Каждый отчёт должен иметь собственные `N`, confusion matrix, CI и unit IDs.
Нельзя использовать тысячи cell crops как независимые patient observations.

## 15.3. Confusion matrix и основные метрики

Пусть:

```text
TP = true positive
TN = true negative
FP = false positive
FN = false negative
```

Рассчитай:

```text
Sensitivity = TP / (TP + FN)

Specificity = TN / (TN + FP)

PPV = TP / (TP + FP)

NPV = TN / (TN + FN)

F1 = 2TP / (2TP + FP + FN)

BalancedAccuracy =
  0.5 * (Sensitivity + Specificity)

FPR = FP / (FP + TN)

FNR = FN / (FN + TP)

MCC =
  (TP*TN - FP*FN)
  / sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))
```

Undefined denominator должен давать `UNDEFINED`, не `0`.

Обязательно:

- confusion matrix;
- sensitivity;
- specificity;
- PPV;
- NPV;
- F1;
- balanced accuracy;
- MCC;
- ROC curve;
- AUROC;
- PR curve;
- AUPRC;
- threshold;
- 95% CI;
- failed/rejected case count.

Accuracy не является главной метрикой.

## 15.4. Prevalence shift

Для prevalence `π`:

```text
PPV(π) =
  Sensitivity * π
  / (
      Sensitivity * π
      + (1 - Specificity) * (1 - π)
    )

NPV(π) =
  Specificity * (1 - π)
  / (
      (1 - Sensitivity) * π
      + Specificity * (1 - π)
    )
```

Покажи таблицу минимум для:

```text
π ∈ {0.01, 0.05, 0.10, 0.25, 0.50}
```

Добавь intended-setting prevalence только с источником.

Balanced dataset:

```text
π_test = 0.50
```

не означает:

```text
π_deployment = 0.50
```

Поэтому test PPV нельзя автоматически переносить в clinical population.

## 15.5. Confidence intervals

Для sensitivity denominator:

```text
n_positive = число независимых положительных units
```

Для specificity:

```text
n_negative = число независимых отрицательных units
```

Выполни:

1. Wilson interval;
2. Clopper-Pearson interval;
3. patient/slide-level cluster bootstrap;
4. минимум 2000 resamples при достаточных ресурсах;
5. seed по умолчанию `20260728`;
6. percentile и при наличии tooling BCa sensitivity analysis.

Если clusters содержат один outcome class, зафиксируй unstable/undefined
bootstrap, не подменяй iid interval.

## 15.6. Validation cohort size

Первичная аппроксимация:

```text
n_positive ≈
  z_(1-α/2)^2 * Se * (1-Se) / d_Se^2

n_negative ≈
  z_(1-α/2)^2 * Sp * (1-Sp) / d_Sp^2
```

Для clustering:

```text
DE = 1 + (m - 1) * ρ_ICC
n_adjusted = ceil(n * DE)
```

Покажи sensitivity analysis по:

- ожидаемым Se/Sp;
- half-width;
- cluster size;
- ICC;
- dropout/unreadable rate;
- subgroup objectives.

Это planning approximation, не окончательный clinical study design.
Финальный protocol утверждает биостатистик.

## 15.7. Calibration

На независимом calibration split:

```text
BrierScore =
  (1/N) * Σ_i (p_i - y_i)^2

NLL =
  -(1/N) * Σ_i [
    y_i log(p_i)
    + (1-y_i) log(1-p_i)
  ]

ECE =
  Σ_b (n_b/N) * |accuracy(b) - confidence(b)|
```

Представь:

- reliability diagram;
- Brier;
- NLL;
- ECE с binning definition;
- calibration intercept;
- calibration slope;
- confidence intervals, где применимо.

Сравни:

- uncalibrated;
- temperature scaling;
- Platt scaling;
- isotonic regression.

Правила:

```text
fit calibrator on calibration split only;
select method without test leakage;
evaluate final calibrator once on locked test;
store calibrator artifact and checksum;
do not call softmax a calibrated probability by default.
```

## 15.8. Threshold и clinical cost

Не используй только `argmax`.

```text
ExpectedCost(t) =
  C_FN * FN(t)
  + C_FP * FP(t)
  + C_REJECT * Reject(t)
  + C_DELAY * Delay(t)
```

Оптимизация:

```text
minimize ExpectedCost(t)

subject to:
  Sensitivity(t) >= Se_min
  Specificity(t) >= Sp_min
```

Costs и constraints должны происходить из intended use, clinical experts и
risk management. Если они неизвестны:

- threshold остаётся research-only;
- проведи sensitivity analysis по сетке cost ratios;
- не выбирай произвольный «оптимальный» threshold;
- покажи Pareto frontier sensitivity/specificity/coverage.

## 15.9. Selective classification

```text
accept(x) = 1, если uncertainty(x) <= τ
reject(x) = 1, иначе

Coverage(τ) =
  accepted / N

SelectiveRisk(τ) =
  errors_among_accepted / accepted
```

Построй risk-coverage curve для:

- max softmax probability baseline;
- predictive entropy;
- top-two margin;
- temperature-scaled confidence;
- deep ensemble, если trained replicas доступны;
- approved OOD score.

Укажи:

- rejected count;
- rejection handling;
- human escalation;
- delay;
- subgroup coverage;
- false reassurance risk.

Softmax confidence не является автоматической оценкой эпистемической
неопределённости.

## 15.10. Model comparison

Для одинаковых cases:

- exact/standard McNemar для paired binary correctness;
- DeLong для correlated AUROC;
- cluster bootstrap для delta sensitivity/specificity;
- CI для всех deltas;
- correction for multiple comparisons;
- predefined primary comparator;
- clinically meaningful non-inferiority/superiority margin.

Не объявляй победителя:

- по третьему знаку;
- без paired analysis;
- без CI;
- после post-hoc выбора subgroup;
- при несовпадающих test sets.

## 15.11. Исполняемый validation toolkit

Реализуй dependency-minimal offline module, который:

- валидирует binary labels/probabilities;
- не скрывает undefined metrics;
- вычисляет confusion matrix и threshold metrics;
- строит ROC/PR curve points и AUC;
- вычисляет prevalence transport;
- вычисляет Wilson и exact Clopper-Pearson;
- выполняет seeded cluster bootstrap;
- вычисляет Brier/NLL/ECE/reliability;
- строит MSP risk-coverage baseline;
- вычисляет sample-size approximation;
- вычисляет explicit expected cost;
- поддерживает exact McNemar;
- покрыт unit tests;
- не принимает patient data через публичный endpoint;
- не заявляет validation без настоящего locked cohort.

## 15.12. Обязательные deliverables

Создай:

```text
audit/phase8/MATHEMATICAL_VALIDATION_STATUS.md
audit/phase8/STATISTICAL_ANALYSIS_PLAN.md
audit/phase8/PREVALENCE_SHIFT_ILLUSTRATION.csv
audit/phase8/SAMPLE_SIZE_SCENARIOS.csv
audit/phase8/CALIBRATION_AND_SELECTIVE_PLAN.md
audit/phase8/MODEL_COMPARISON_PLAN.md
audit/phase8/VALIDATION_TOOLKIT_VERIFICATION.md
audit/phase8/VARIATION_REPORT.md
```

Gate:

```text
calculations unit-tested;
analysis levels explicit;
no invented model metrics;
all unavailable analyses marked NOT EXECUTED;
seed/method recorded;
clinical threshold remains unapproved without cost evidence;
GO/NO-GO updated.
```

---

# 16. ФАЗА 9 — АГРЕГАЦИЯ ОТ КЛЕТКИ К ПАЦИЕНТУ

## 16.1. Safety boundary

Cell-level prediction не является slide-level или patient-level result.
Не добавляй patient endpoint до появления validated acquisition, sampling,
detection, aggregation и reference-standard protocol.

Определи отдельно:

```text
cell_estimand
slide_estimand
patient_estimand
parasitemia_estimand
clinical_action
```

Для каждого укажи unit, denominator, reference standard, threshold, CI,
rejection rule и validation cohort.

## 16.2. Naive estimator и его ограничения

Пусть:

```text
m = число исследованных клеток
k = число predicted-positive клеток
p_i = cell score
r = k / m
```

Наивная оценка:

```text
parasitemia_hat_naive = k / m
```

Она смешивает:

- detector misses/duplicates;
- classifier sensitivity/specificity;
- unreadable/rejected cells;
- within-slide correlation;
- incomplete field coverage;
- biased field/cell sampling;
- stage/species differences;
- low-density infection;
- denominator definition.

Не называй `k/m` clinically meaningful parasitemia без bridging validation.

## 16.3. Misclassification correction

При известных validated `Se_cell` и `Sp_cell`:

```text
r = q * Se_cell + (1-q) * (1-Sp_cell)

q_hat_RG =
  (r + Sp_cell - 1)
  / (Se_cell + Sp_cell - 1)
```

Это Rogan–Gladen-type correction. Проверь:

- `Se + Sp > 1`;
- uncertainty Se/Sp;
- applicability к site/stain/stage;
- cluster dependence;
- boundary estimates;
- detector contribution.

Покажи unconstrained и `[0,1]` constrained estimates, но не скрывай boundary
clipping.

## 16.4. Запрещённая independence shortcut

Не используй без доказательства:

```text
P(patient positive) = 1 - Π_i (1-p_i)
```

Формула предполагает условную независимость и calibrated `p_i`. При
correlated cells и даже малом false-positive rate результат быстро стремится к
единице.

Проведи sensitivity illustration:

```text
P(at least one FP | m truly negative independent cells)
= 1 - Sp_cell^m
```

Маркируй это как independence illustration, а не clinical model.

## 16.5. Hierarchical design

Предложи уровни:

```text
patient
  -> slide/specimen
    -> field of view
      -> detected cell
        -> classifier observation
```

Рассмотри:

- generalized linear mixed model;
- beta-binomial overdispersion;
- Bayesian hierarchical model;
- measurement-error model for detector/classifier;
- zero-inflated/low-parasitemia component;
- species/stage-specific effects;
- site/device/stain random effects.

Beta-binomial:

```text
q_slide ~ Beta(alpha, beta)
k | q_slide ~ Binomial(m, q_slide)

E[k] = m * alpha/(alpha+beta)

Var[k] =
  m * μ * (1-μ)
  * [1 + (m-1)ρ]

ρ = 1/(alpha+beta+1)
```

Model choice, priors и posterior decision rule pre-register до locked test.

## 16.6. Minimum sampling

Для optimistic independent-sampling illustration:

```text
P(detect >= 1) = 1 - (1 - q*Se_cell)^m

m_required =
  ceil(log(1-target_detection_probability)
       / log(1-q*Se_cell))
```

Это нижняя planning bound, а не validated minimum. Реальный protocol учитывает:

- clustering/design effect;
- detector miss rate;
- unreadable fraction;
- field selection;
- stage/species sensitivity;
- stopping rules;
- microscopy reference standard.

## 16.7. Architecture comparison

Сравни:

```text
A. cropped-cell classification
B. detection/segmentation + classification + counting
C. whole-field/whole-slide end-to-end detector
```

| Criterion | A | B | C |
|---|---|---|---|
| Input burden | expert/manual crop | raw field + annotations | raw field/slide |
| Detection errors | hidden upstream | explicit/measurable | integrated |
| Counting | absent | native | possible |
| Interpretability | cell class | detections/counts | field-level |
| Annotation cost | cell labels | boxes/masks + labels | boxes/masks/field labels |
| Deployment complexity | low | high | medium/high |
| Patient bridge | absent | possible after validation | possible after validation |
| Domain-shift surface | crop | detector + classifier | end-to-end |

Не выбирай architecture без intended use, data availability и target hardware.

## 16.8. Gate и deliverables

Создай:

```text
audit/phase9/AGGREGATION_AUDIT.md
audit/phase9/ARCHITECTURE_COMPARISON.csv
audit/phase9/AGGREGATION_MATHEMATICS.md
audit/phase9/PATIENT_LEVEL_GATE.md
```

Patient aggregation остаётся `NO-GO`, пока нет validated detector/sampling,
patient-linked cohort, reference standard, aggregation threshold и human
review workflow.

---

# 17. ФАЗА 10 — ROBUSTNESS, OOD И FAILURE ANALYSIS

## 17.1. Taxonomy

Разделяй:

```text
technical corruption
acquisition shift
biological/domain shift
semantic OOD
adversarial input
pipeline failure
```

Минимальные corruptions:

- blur/defocus/motion blur;
- JPEG/WebP compression;
- brightness/contrast/gamma;
- white balance/color cast/stain shift;
- scale/rotation/crop shift;
- occlusion/overlap;
- leukocytes/platelets/artefacts/dust;
- empty background/non-blood/document/face/noise;
- other microscope/site/institution;
- adversarial perturbation.

## 17.2. Corruption protocol

Для каждого corruption:

```text
severity ∈ {0,1,2,3,4,5}
seed
parameter mapping
clinical rationale
pixel-space constraint
identity check at severity=0
artifact checksum
```

Строй:

```text
Metric(corruption, severity)
Delta_from_clean
failure/reject rate
calibration degradation
subgroup/site interaction
```

Не используй augmentation, меняющую clinically meaningful morphology, как
«исправление» без медицинского review.

## 17.3. OOD

Оцени:

- MSP baseline;
- entropy;
- energy/margin if supported;
- embedding-distance baseline;
- dedicated OOD set;
- image-quality/reject model;
- ensemble disagreement.

Не подбирай OOD threshold на final test. Report:

```text
AUROC_OOD
AUPRC_OOD
FPR@TPR
coverage
selective risk
false accept OOD
false reject ID
```

## 17.4. Failure clustering

Таблица:

| Cluster | Count | Error type | Severity | Cause hypothesis | Evidence | Mitigation |
|---|---:|---|---|---|---|---|

Кластеризуй по:

- morphology;
- stain/color;
- acquisition;
- crop geometry;
- predicted/true class;
- confidence/entropy;
- site/device;
- species/stage;
- detector failure.

## 17.5. Explainability

Если применяется Grad-CAM/XAI:

- не трактуй heatmap как causality;
- выполни model/randomization sanity checks;
- оцени parameter/layer sensitivity;
- проверь stability под малым perturbation;
- сравни с expert ROI;
- документируй cherry-picking risk.

## 17.6. Implementation boundary

Разрешено реализовать deterministic offline corruption harness. Запрещено
включать corruptions/TTA в production preprocessing без model-specific
validation.

Deliverables:

```text
audit/phase10/ROBUSTNESS_OOD_PLAN.md
audit/phase10/CORRUPTION_TAXONOMY.csv
audit/phase10/FAILURE_ANALYSIS_TEMPLATE.csv
audit/phase10/ROBUSTNESS_EXECUTION_STATUS.md
```

---

# 18. ФАЗА 11 — PERFORMANCE И CAPACITY MODEL

## 18.1. Benchmark tiers

Разделяй:

```text
T0 = no-model API/framework baseline
T1 = mocked/synthetic inference baseline
T2 = approved real-model single-worker
T3 = approved real-model deployment topology
```

Не переносить T0/T1 latency на T2/T3.

## 18.2. Scenarios

Измерь:

- cold process startup;
- model load;
- warm startup;
- first request;
- sequential steady state;
- concurrency 1,2,4,8,16;
- file-size/input-resolution matrix;
- valid/invalid/oversized/corrupt;
- timeout/cancellation/capacity rejection;
- graceful shutdown under load.

Повтори сценарии. Запиши:

```text
N
warmup count
mean
standard deviation
95% CI method
p50/p90/p95/p99
throughput
error/timeout/reject rate
CPU
RSS/peak RSS
threads
queue depth
model load time
```

## 18.3. Queueing

```text
μ = service rate одного worker
λ = arrival rate
c = workers/servers
ρ = λ/(c*μ)
```

Если `ρ -> 1`, queue latency растёт нелинейно. Проверяй candidate operating
points около `ρ <= 0.7`, но не объявляй 0.7 универсальным SLO.

Little’s Law:

```text
L = λW
```

Проверяй согласованность measured throughput/latency/concurrency.

## 18.4. Memory

```text
RAM_total ≈
  c * (RAM_model + RAM_runtime + RAM_activation_peak)
  + RAM_shared
  + RAM_upload_buffers
  + safety_margin
```

Gunicorn workers обычно создают отдельные process-local model copies.
Подтверди RSS экспериментом; не называй copy-on-write устойчивой экономией
после mutable framework initialization без измерения.

## 18.5. Topology comparison

Сравни:

- 1 process + bounded concurrency;
- multiple Gunicorn processes;
- dedicated inference worker;
- durable/non-durable queue;
- ONNX Runtime;
- quantization;
- TorchScript/`torch.compile`;
- CPU/GPU.

Optimization gate:

```text
baseline measured
correctness regression suite exists
target bottleneck identified
candidate measured on same cases/hardware
accuracy/calibration delta acceptable
```

Deliverables:

```text
audit/phase11/BENCHMARK_PROTOCOL.md
audit/phase11/BENCHMARK_RESULTS.csv
audit/phase11/CAPACITY_MODEL.md
audit/phase11/TOPOLOGY_OPTIONS.csv
```

---

# 19. ФАЗА 12 — RELIABILITY И OBSERVABILITY

## 19.1. Signals

Проверь:

- structured JSON logs;
- correlation ID;
- traces;
- metrics;
- alerts/dashboards;
- audit log;
- code/model/dataset/checksum provenance;
- liveness/readiness/startup;
- graceful shutdown;
- timeout/retry/circuit breaker;
- backpressure/rate limit.

## 19.2. Metric contract

API:

```text
request_count
request_duration_seconds
request_size_bytes
response_size_bytes
http_error_count
active_requests
rejected_requests
```

ML:

```text
inference_duration_seconds
model_load_status
model_load_duration_seconds
prediction_distribution
score/entropy_distribution
reject_rate
ood_rate
image_quality_failure_count
```

System:

```text
cpu
rss_bytes
thread_count
queue_depth
disk
container_restart_count
```

Cardinality controls:

- не использовать filename/request ID как metric label;
- model revision label только bounded;
- не использовать patient/site identifiers без approved aggregation/privacy.

## 19.3. Logging privacy

Не логируй:

- image bytes;
- filenames с patient metadata;
- direct identifiers;
- Authorization/API keys/tokens;
- request bodies;
- local secret paths;
- raw model repository credentials.

Structured event minimum:

```text
timestamp
level
event
service_version
request_id
method
route/path template
status
duration_ms
error_type
```

## 19.4. SLO framework

Не выдумывай targets. Предложи candidate ranges и вопросы владельцу:

```text
availability
p95/p99 latency
5xx rate
capacity rejection rate
model-not-ready duration
data-quality reject rate
```

Monthly error budget:

```text
ErrorBudget =
  (1 - SLO_target) * total_time
```

Определи burn-rate alerts только после утверждения SLO.

Deliverables:

```text
audit/phase12/RELIABILITY_OBSERVABILITY_AUDIT.md
audit/phase12/METRIC_CATALOG.csv
audit/phase12/SLO_FRAMEWORK.md
audit/phase12/PRIVACY_LOGGING_POLICY.md
```

---

# 20. ФАЗА 13 — SECURITY И PRIVACY

## 20.1. STRIDE

Assets:

- images/results/clinical metadata;
- model/registry/token/checksum;
- container/runtime;
- CI secrets/logs/infrastructure.

Actors:

- anonymous user/bot;
- malicious user;
- compromised dependency/model repo;
- insider;
- supply-chain attacker.

Для каждого threat:

```text
Threat ID
STRIDE class
Asset
Actor
Entry point
Concrete attack path
Existing control
Gap
Likelihood
Impact
Detection
Mitigation
Acceptance
```

## 20.2. Required checks

Проверь:

- authn/authz/global rate limits;
- TLS/reverse proxy trust;
- CORS;
- upload/decompression/image parser DoS;
- filename/log/error injection;
- model extraction/inversion/membership inference;
- adversarial inputs;
- dependency confusion/unpinned transitives;
- unsigned/mutable artifacts;
- unsafe pickle/remote code;
- secrets/history;
- Actions permissions/SHA pinning;
- SBOM/CVE scanning;
- non-root/capabilities/read-only/no-new-privileges;
- CPU/RAM/pids/disk limits;
- network egress/model integrity.

## 20.3. Privacy

Определи:

- data controller/processor roles;
- purpose and legal basis;
- minimization;
- retention/deletion;
- encryption in transit/at rest;
- access logs;
- incident response;
- data subject handling;
- DPIA trigger;
- cross-border transfer;
- model/privacy attack risk.

Не загружай patient images во внешние scanners.

## 20.4. Framework mapping

Сопоставь findings:

- OWASP API Security Top 10 2023;
- NIST SSDF SP 800-218;
- NIST AI RMF;
- applicable medical cybersecurity guidance.

Deliverables:

```text
audit/phase13/STRIDE_THREAT_MODEL.md
audit/phase13/SECURITY_FINDINGS.csv
audit/phase13/PRIVACY_GAP_ANALYSIS.md
audit/phase13/CONTROL_MAPPING.csv
```

---

# 21. ФАЗА 14 — DOCKER И SUPPLY CHAIN

## 21.1. Docker

Проверь:

- base digest;
- stage isolation;
- image size;
- non-root UID/GID;
- writable dirs;
- OS packages/cleanup;
- runtime curl/shell;
- HEALTHCHECK/startup semantics;
- exec form/signals/graceful timeout;
- worker/model copies;
- model download/egress;
- reproducibility/CVEs/SBOM/provenance.

Не объявляй build/runtime PASS без Docker execution.

## 21.2. Python/model supply chain

Проверь:

- direct/transitive locks;
- hashes/platform matrix;
- PyTorch index/CPU-GPU wheel;
- model immutable revision;
- safetensors;
- SHA-256/signature;
- license;
- offline install/load;
- dependency/model SBOM.

## 21.3. CI

Проверь:

- top-level `permissions`;
- full action commit SHA;
- `persist-credentials`;
- untrusted PR/token behavior;
- dependency cache poisoning surface;
- artifact retention;
- attestations;
- release/environment approvals.

## 21.4. Prediction lineage

Цепочка:

```text
source commit
-> dependency lock
-> tested model revision/checksum
-> container digest
-> SBOM
-> signature/attestation
-> deployment revision
-> request/prediction provenance
```

Каждое production prediction должно быть связано с immutable release
manifest без раскрытия secrets клиенту.

Deliverables:

```text
audit/phase14/DOCKER_AUDIT.md
audit/phase14/SUPPLY_CHAIN_AUDIT.md
audit/phase14/RELEASE_LINEAGE.md
audit/phase14/CI_HARDENING.md
```

---

# 22. ФАЗА 15 — TEST STRATEGY

## 22.1. Test pyramid/matrix

Раздели:

1. unit;
2. API contract;
3. integration;
4. real-model smoke;
5. model regression;
6. security;
7. property-based/fuzz;
8. load;
9. resilience;
10. end-to-end.

## 22.2. Mock boundary

Проверь, не скрывает ли mock:

- unavailable artifact;
- wrong labels/preprocessing/logits;
- load/license/version incompatibility;
- unsafe serialization;
- device/dtype issue;
- calibration absence.

Mocked success = software contract test, не model integration evidence.

## 22.3. Required cases

Покрой:

- health/ready/not-ready;
- missing/empty/unsupported/spoofed/corrupt/truncated;
- encoded/decoded oversize;
- grayscale/RGBA/CMYK/WEBP/multiframe;
- concurrency/timeout/cancellation/capacity;
- model/processor exceptions;
- label/logit/revision contracts;
- deterministic prediction;
- golden/OOD/low-quality;
- structured logging privacy;
- aggregation/capacity/corruption mathematical invariants.

## 22.4. Golden tests

```text
model revision/checksum fixed
image SHA-256 fixed
processor version fixed
hardware/determinism documented
tolerance justified
class/rank and probability tolerance
```

Не сравнивай float строго. Golden assets должны быть лицензированы и
de-identified.

Deliverables:

```text
audit/phase15/TEST_STRATEGY.md
audit/phase15/TEST_MATRIX.csv
audit/phase15/MOCK_GAP_ANALYSIS.md
```

---

# 23. ФАЗА 16 — CLINICAL WORKFLOW И HUMAN FACTORS

## 23.1. Intended use

Различай:

- research/educational;
- screening;
- triage;
- clinical decision support;
- autonomous diagnosis.

Определи intended user/population/setting/acquisition/training/contraindications,
override, escalation, uncertainty и FP/FN consequences.

## 23.2. UI/API semantics

Проверь термины:

```text
diagnosis
prediction
screening result
score/confidence
calibrated probability
uncertainty
requires review
quality flag
```

Не показывай raw softmax как disease probability.

Safe research response должен включать:

```text
cell_prediction
uncalibrated_score
requires_review = true
uncertainty_reason
technical_quality_flags
model revision/checksum when approved
serving/preprocessing/calibration version
intended_use
request_id
```

## 23.3. Automation bias

Проверь:

- salience/color/wording;
- default action;
- score anchoring;
- alert fatigue;
- confirmation bias;
- override friction;
- missing-context warning;
- reviewer accountability;
- training/competency.

Conduct formative usability test before clinical workflow and summative test
under applicable human-factors process.

Deliverables:

```text
audit/phase16/CLINICAL_WORKFLOW.md
audit/phase16/HUMAN_FACTORS_RISK_ANALYSIS.csv
audit/phase16/SAFE_RESPONSE_CONTRACT.md
```

---

# 24. ФАЗА 17 — REGULATORY APPLICABILITY

## 24.1. Non-legal boundary

Не давай окончательного юридического заключения. Определи jurisdiction,
intended purpose и claims до классификации.

Различай:

- human specimen image processing;
- IVD purpose;
- medical-device software;
- research software;
- general wellness;
- decision support.

## 24.2. Applicability matrix

Оцени:

- EU MDR 2017/745;
- EU IVDR 2017/746;
- EU AI Act 2024/1689;
- GDPR;
- FDA SaMD для US plan;
- IMDRF SaMD;
- national target-market rules.

Для каждого:

```text
Applicability
Trigger
Current evidence
Gap
Decision owner
Required specialist review
```

## 24.3. Standards

Перед указанием версии проверь официальную актуальную редакцию:

- ISO 13485;
- ISO 14971;
- IEC 62304;
- IEC 62366-1;
- IEC 81001-5-1;
- ISO/IEC 27001;
- applicable CLSI/WHO microscopy recommendations.

Стандарт может быть платным; не выдумывай его normative clauses из secondary
summary.

## 24.4. Gap areas

| Area | Applicability | Evidence | Gap | Required artifact |
|---|---|---|---|---|
| QMS | | | | |
| intended purpose | | | | |
| risk management | | | | |
| software lifecycle | | | | |
| performance evaluation | | | | |
| usability | | | | |
| cybersecurity | | | | |
| post-market | | | | |
| change control | | | | |
| traceability | | | | |
| human oversight | | | | |
| technical documentation | | | | |

Tests/Docker не равны regulatory compliance.

Deliverables:

```text
audit/phase17/REGULATORY_APPLICABILITY.md
audit/phase17/STANDARDS_VERIFICATION.md
audit/phase17/REGULATORY_GAP_MATRIX.csv
```

---

# 25. СИСТЕМА ОЦЕНКИ

## 25.1. Quality score

Scores `0..5`; weights:

```text
Clinical/model evidence      25
Data quality/governance      15
Software correctness         12
Security/privacy             12
Reliability/performance      10
MLOps/reproducibility        10
Testing/CI                    8
Documentation/regulatory     8
Total                       100
```

```text
QualityScore =
  Σ_i weight_i * score_i / 5
```

Для каждого score дай evidence и confidence. Docker не компенсирует отсутствие
clinical evidence.

Safety gates:

```text
G0 model exists/access/license
G1 end-to-end inference reproducible
G2 independent external validation
G3 safe failure
G4 basic security
G5 intended use
G6 claims match evidence
```

```text
if G0 or G1 fail:
  production inference = NO_GO

if G2 fail:
  clinical deployment = NO_GO
```

## 25.2. Risk register

```text
S,O,D ∈ {1,2,3,4,5}
D=1 easy pre-harm detection
D=5 hard detection

RPN = S*O*D
C ∈ [0,1]
U = 1-C
AdjustedPriority = RPN*(1+U)
```

Thresholds зафиксируй до scoring:

```text
Critical >= 100
High      >= 50
Medium    >= 20
Low       < 20
```

Отдельный STOP-SHIP override:

- missing/unlicensed/unreproducible model;
- possible label inversion;
- uncontrolled clinically dangerous FN;
- critical vulnerability/license violation;
- clinical claim without validation.

Deliverables:

```text
audit/phase18/QUALITY_SCORE.md
audit/phase18/RISK_REGISTER.csv
audit/phase18/SAFETY_GATES.md
audit/phase18/FINAL_GO_NO_GO.md
```

---

# 26. ФАЗА 18 — формализация требований

Создай requirements registry:

| ID | Domain | Requirement | Source | Priority | Acceptance | Status |
|---|---|---|---|---|---|---|

Domains:

- PRODUCT;
- UI;
- ACCESSIBILITY;
- API;
- ML;
- SECURITY;
- RELIABILITY;
- OBSERVABILITY;
- MLOPS;
- DEVEX;
- TESTING;
- DOCUMENTATION;
- CLINICAL_SAFETY.

Каждое требование должно быть:

- однозначным;
- наблюдаемым;
- тестируемым;
- ограниченным scope;
- связанным с риском или ценностью.

Плохое требование:

```text
сделать интерфейс красивым
```

Хорошее:

```text
UI-007:
При model_not_configured primary action disabled,
reason отображается в aria-live,
горизонтальный overflow отсутствует при 320 CSS px.
```

---

# 27. Математическая приоритизация

Используй несколько моделей одновременно.

## 27.1. Обязательная основная формула

Для каждой рекомендации задай:

```text
Impact I ∈ {1,2,3,4,5}
Urgency U ∈ {1,2,3,4,5}
Evidence E ∈ [0.25,1.0]
Effort F ∈ {1,2,3,4,5}
DependencyComplexity D ∈ {1,2,3,4,5}

PriorityScore = (I * U * E) / sqrt(F * D)
```

Проверь диапазоны и пересчитай score отдельным скриптом. Число не заменяет
policy:

```text
STOP_SHIP > regulatory_mandatory > patient_safety
          > evidence_enabler > security/reliability > feature > optimization
```

STOP-SHIP всегда располагается выше любого числового результата. Regulatory
mandatory action выше feature development. Patient-safety action выше
performance optimization.

Для каждой рекомендации обязательно документируй:

- проблему и root cause;
- предлагаемое решение;
- ожидаемый эффект;
- evidence и confidence;
- зависимости;
- трудоёмкость;
- внедренческий/residual risk;
- измеримый acceptance criterion;
- способ измерения эффекта;
- owner role.

## 27.2. RICE

```text
RICE_i =
  Reach_i * Impact_i * Confidence_i
  / Effort_i
```

Нормализация:

```text
Reach ∈ [1, 10]
Impact ∈ [0.25, 3]
Confidence ∈ [0, 1]
Effort > 0
```

## 27.3. WSJF

```text
WSJF_i =
  (UserValue_i
   + TimeCriticality_i
   + RiskReduction_i
   + OpportunityEnablement_i)
  / JobSize_i
```

## 27.4. Risk-adjusted value

```text
RAV_i =
  (ExpectedValue_i * P_success_i
   + RiskReduction_i
   + EvidenceGain_i)
  / (Cost_i * Time_i * Irreversibility_i)
```

## 27.5. Cost of delay

```text
CoD_i =
  UserLossPerPeriod_i
  + SecurityExposurePerPeriod_i
  + OperationalCostPerPeriod_i
  + EvidenceDelayPerPeriod_i
```

## 27.6. FMEA

```text
RPN_i = Severity_i * Occurrence_i * Detectability_i
```

Где:

```text
Severity ∈ [1, 5]
Occurrence ∈ [1, 5]
Detectability ∈ [1, 5]
```

Uncertainty-adjusted:

```text
AdjustedRPN_i =
  RPN_i * (1 + Uncertainty_i)
```

Safety override:

```text
если Severity = 5 и возможен patient harm,
priority = P0 независимо от RICE/WSJF
```

## 27.7. Итог

```text
Priority_i =
  SafetyOverride
  затем rank(RAV, WSJF, RICE, CoD, AdjustedRPN)
```

Не подгоняй числа под заранее выбранное решение.

---

# 28. Архитектурные варианты

## 28.1. Обязательные продуктовые стратегии

Сравни минимум:

```text
A = исследовательский cell-classification API
B = laboratory screening assistant для pre-cropped cells
C = detection + segmentation + classification + counting
D = clinical decision-support с обязательным human review
```

Для каждой оцени:

- научную и инженерную сложность;
- необходимые patient/slide/cell данные;
- инфраструктуру;
- realistic time-to-market;
- clinical и commercial value;
- regulatory burden;
- safety/residual risk;
- команду и внешние компетенции;
- обратимость решения;
- exit/kill criteria.

Наиболее сложная стратегия не считается лучшей автоматически. Отдельно
рассмотри staged path `A -> B -> C -> D`, но не предполагай, что переход
обязателен.

## 28.2. Варианты функции

Для каждой крупной функции сравни:

1. `AS_IS`;
2. `MINIMAL_SAFE`;
3. `TARGET_ARCHITECTURE`.

Таблица:

| Variant | Correctness | Safety | UX | Reliability | Complexity | Cost | Compatibility | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|

Используй weighted decision:

```text
Score_variant =
  Σ(weight_j * normalized_metric_j)
  - migration_penalty
  - residual_risk_penalty
```

Weights должны суммироваться к 1.

Для safety-sensitive проекта рекомендуемый baseline:

```text
Safety         0.25
Correctness    0.20
Reliability    0.15
Testability    0.10
Compatibility  0.10
UX             0.10
Cost           0.05
Complexity     0.05
```

Допускается изменение весов с объяснением.

---

# 29. ADR

Для архитектурных решений создай ADR:

```text
ADR ID
Title
Status
Context
Decision drivers
Options
Quantitative comparison
Decision
Consequences
Risks
Rollback
Verification
```

Минимальные ADR topics:

- API versioning and legacy routes;
- model artifact delivery;
- concurrency topology;
- authentication boundary;
- error contract;
- UI hosting;
- dependency locking;
- observability.

---

# 30. Backend remediation

## 17.1. API surface

Проверь и при необходимости реализуй:

- canonical versioned routes;
- root operational routes;
- deprecation policy;
- capabilities/version metadata;
- correct status codes;
- stable schemas;
- idempotency там, где применимо;
- content negotiation;
- request/response limits;
- safe public messages.

## 17.2. Error contract

Требования:

```text
code
detail
request_id
optional retry_after
no internal exception
no filesystem path
no secret
no raw request body
```

Обработать:

- FastAPI HTTPException;
- Starlette HTTPException;
- validation;
- unsupported media;
- oversized payload;
- model unavailable;
- queue busy;
- internal exception;
- cancellation.

## 17.3. Upload pipeline

Проверить:

- MIME;
- filename;
- encoded bytes;
- decoded pixels;
- content validation;
- temp spooling;
- cleanup;
- multi-frame files;
- EXIF;
- decompression bombs;
- malformed files;
- cancellation;
- slow upload;
- reverse-proxy limit.

## 17.4. Concurrency

Разделить:

```text
request admission
queue wait
decode
preprocess
model compute
response serialization
```

Не считать `asyncio.to_thread()` достаточным capacity control.

Проверить cancellation:

```text
cancelled coroutine != stopped native thread
```

Semaphore/queue slot нельзя освобождать до фактического завершения compute.

## 17.5. Configuration

Требования:

- safe defaults;
- bounds;
- no wildcard CORS;
- production invariants;
- explicit model;
- immutable revision;
- local-files-only;
- documented env;
- no secrets in repo;
- settings tests.

---

# 31. Model/MLOps gate

## 18.1. Нельзя подменять модель

Если approved model отсутствует:

- не выбирай случайную;
- не используй pneumonia model;
- не генерируй fake weights;
- не скрывай blocker;
- сохраняй health/UI;
- readiness остаётся fail-closed.

## 18.2. Artifact contract

Approved model package должен иметь:

```text
model_id
revision
SHA256
architecture
processor config
id2label
num_labels
expected input
license
model card
training provenance
evaluation provenance
known limitations
approval
```

## 18.3. Runtime validation

Проверить:

- exact label order;
- logits shape;
- processor compatibility;
- revision;
- local-only mode;
- checksum;
- eval/inference_mode;
- deterministic golden cases;
- corrupt artifact;
- missing files;
- offline startup.

## 18.4. Supply chain

Реализовать/спланировать:

- model manifest;
- checksums;
- read-only mount;
- no production egress;
- SBOM;
- signing;
- provenance;
- rollback to previous model digest.

---

# 32. UI implementation

## 19.1. Product semantics

UI должен ясно показывать:

- research-only;
- pre-cropped cell;
- model readiness;
- uncalibrated score;
- limitations;
- no diagnosis;
- no treatment;
- no exclusion of malaria.

## 19.2. States

Реализовать и проверить:

- idle;
- ready;
- model not configured;
- model load failed;
- offline;
- file selected;
- invalid MIME;
- empty;
- oversized;
- preview;
- uploading;
- analysing;
- cancelled;
- queue busy;
- server error;
- success;
- indeterminate future state.

## 19.3. Accessibility

Ориентир WCAG 2.2 AA:

- semantic HTML;
- keyboard;
- labels;
- focus;
- skip link;
- live regions;
- visible errors;
- contrast;
- touch targets;
- responsive 320+ CSS px;
- reduced motion;
- no color-only state;
- screen-reader accessible scores.

Не заявлять WCAG compliance без formal audit.

## 19.4. Frontend security/privacy

- no unsafe `innerHTML`;
- use `textContent`;
- CSP compatible;
- no third-party CDN;
- no analytics по умолчанию;
- no image persistence;
- object URL cleanup;
- abortable fetch;
- no PHI in localStorage;
- no sensitive error rendering.

## 19.5. Browser verification

Проверить:

- desktop;
- tablet;
- mobile;
- unavailable state;
- success;
- error;
- keyboard;
- horizontal overflow;
- console errors;
- network requests;
- CSP.

---

# 33. Authentication and authorization

Не внедряй случайную auth-систему без deployment context.

Сначала определи:

- public/private;
- service-to-service/browser;
- users/principals;
- roles;
- tenant model;
- gateway;
- identity provider;
- secret rotation;
- audit requirements.

Сравни:

- API key;
- OAuth2/OIDC;
- mTLS;
- private network/gateway auth.

Выбери только после threat model.

Минимум для public inference:

- identity;
- rate limit;
- quota;
- global concurrency;
- abuse monitoring;
- revocation;
- no keys in frontend source.

---

# 34. Reliability и performance

## 21.1. Capacity model

```text
λ = requests / second
S = mean service time
μ = 1 / S
c = concurrent inference slots
ρ = λ / (c * μ)
```

Не проектировать normal operation при:

```text
ρ -> 1
```

## 21.2. Little’s Law

```text
L = λW
```

Где:

- `L` — среднее число jobs;
- `λ` — throughput;
- `W` — среднее время в системе.

## 21.3. Memory

```text
RAM_total =
  workers * (model_RSS + framework_RSS)
  + concurrency * request_peak_memory
  + cache
  + OS_headroom
```

```text
request_peak_memory ≈
  encoded_bytes
  + decoded_pixels * channels * bytes_per_channel
  + processor_tensors
  + intermediate_activations
```

## 21.4. Load scenarios

- cold start;
- warm single;
- step load;
- burst;
- saturation;
- slow upload;
- mixed invalid;
- cancellation;
- soak;
- restart;
- provider/cache failure.

Метрики:

- p50/p95/p99/max;
- throughput;
- queue wait;
- decode;
- model time;
- RSS/peak RSS;
- CPU;
- errors;
- rejection;
- startup;
- readiness.

Не выдумывать SLO. Сначала получить product/SRE targets.

---

# 35. Observability

Проверить/реализовать:

- structured logs;
- request ID;
- trace ID;
- status/latency;
- decode time;
- queue time;
- inference time;
- readiness reason;
- model revision;
- resource saturation;
- rejection count;
- error codes;
- privacy-safe attributes.

RED:

```text
Rate
Errors
Duration
```

USE:

```text
Utilization
Saturation
Errors
```

Не логировать:

- raw image;
- patient identifiers;
- full body;
- secrets;
- unbounded filename/header.

---

# 36. Dependency и build reproducibility

Проверить:

- exact direct pins;
- transitive lock;
- hashes;
- CPU/GPU variants;
- Python 3.11/3.12;
- OS markers;
- base image digest;
- package indexes;
- unused packages;
- licenses;
- vulnerabilities.

Целевой release:

```text
input constraints
-> generated lock
-> hash verification
-> clean build
-> SBOM
-> scan
-> signature
-> provenance
-> immutable image digest
```

Не считать exact direct pins полноценным lock.

---

# 37. Container/CI/CD

## 24.1. Docker

Проверить:

- build;
- non-root;
- ownership;
- UI assets;
- model mount;
- local-only;
- liveness;
- readiness;
- signal handling;
- shutdown;
- one-worker safe default;
- resource limits;
- read-only root filesystem;
- temp filesystem;
- network egress.

## 24.2. CI

Проверить:

- Python matrix;
- format;
- lint;
- types;
- tests;
- coverage;
- pip check;
- lock consistency;
- secret scan;
- dependency audit;
- container build;
- image scan;
- artifact-backed smoke;
- SBOM;
- signing;
- immutable actions SHA.

## 24.3. Deployment

Без разрешения:

```text
не deploy
не push
не менять remote
```

При разрешении:

- deploy only saved/immutable artifact;
- post-deploy smoke;
- readiness;
- rollback;
- monitor.

---

# 38. Security threat model

Построй:

```text
assets
actors
trust boundaries
entry points
abuse cases
controls
residual risk
```

Минимальные threats:

- upload DoS;
- decompression bomb;
- decoder exploit;
- slowloris;
- concurrency exhaustion;
- model probing/extraction;
- malicious filename/request ID;
- exception disclosure;
- supply-chain compromise;
- model substitution;
- cache poisoning;
- unauthorized use;
- PHI leakage;
- log injection;
- unsafe CORS;
- dependency compromise.

Для каждого:

| Threat | Likelihood | Impact | Detectability | Control | Test | Residual |
|---|---:|---:|---:|---|---|---|

---

# 39. Тестовая архитектура

## 26.1. Pyramid

```text
static
-> unit
-> contract
-> component
-> integration
-> container
-> system
-> performance
-> clinical evidence
```

## 26.2. Unit

- settings;
- error mapping;
- request ID;
- filename;
- model contract;
- logits;
- queue;
- cancellation;
- score semantics.

## 26.3. Contract

- OpenAPI;
- responses;
- status codes;
- deprecated fields;
- capabilities;
- headers;
- error envelope.

## 26.4. UI

- assets;
- syntax;
- unavailable;
- selection;
- invalid;
- success;
- cancel;
- progress semantics;
- mobile;
- accessibility.

## 26.5. Model integration

Только с approved artifact:

- clean cache;
- offline;
- golden inputs;
- expected labels;
- deterministic tolerance;
- corrupt artifact;
- resource profile.

## 26.6. Mutation expectation

Проверить, что tests падают при:

- inverted labels;
- missing revision;
- internal exception leak;
- removed semaphore;
- wildcard CORS;
- changed error schema;
- clinical wording regression.

---

# 40. Statistical/clinical track

Этот track не блокирует улучшение software skeleton, но блокирует claims.

## 27.1. Data

- patient/slide/cell IDs;
- patient-level split;
- external site;
- reference standard;
- annotation;
- license;
- quality;
- subgroup;
- no leakage.

## 27.2. Metrics

```text
Sensitivity = TP / (TP + FN)
Specificity = TN / (TN + FP)
PPV = TP / (TP + FP)
NPV = TN / (TN + FN)
```

Prevalence:

```text
PPV(π) =
  Se * π
  / [Se * π + (1-Sp) * (1-π)]

NPV(π) =
  Sp * (1-π)
  / [(1-Se) * π + Sp * (1-π)]
```

Calibration:

```text
Brier = (1/n) Σ(p_i - y_i)^2
NLL = -(1/n) Σ[y_i log(p_i) + (1-y_i) log(1-p_i)]
```

Selective prediction:

```text
Coverage = accepted / total
SelectiveRisk = errors_among_accepted / accepted
```

Нужны:

- CI;
- cluster-aware analysis;
- AUROC/AUPRC;
- calibration;
- risk-coverage;
- subgroup;
- domain shift;
- external testing;
- decision utility.

Без них:

```text
clinical gate = FAIL
```

---

# 41. Implementation batching

## 41.1. Обязательный roadmap

Построй пять горизонтов:

| Horizon | Focus |
|---|---|
| 0–7 дней | STOP-SHIP, model provenance, claims, critical security, smoke |
| 8–30 дней | registry/revision, evaluation harness, datasheet/model card, calibration/reject, lock, metrics |
| 31–60 дней | external data, patient validation, image QC/OOD, load, auth/rate limit, staging |
| 61–90 дней | silent deployment, human factors, workflow, risk/incident/drift |
| 3–6 месяцев | multi-site, slide/patient pipeline, parasitemia, prospective/regulatory/QMS/PMS |

Для каждой initiative укажи deliverable, accountable owner, зависимости,
estimated person-weeks, measurable exit criteria, risk и fallback. Даты
начинаются только после утверждения ресурсов и P0 model decision.

## Batch A — correctness/safety

- broken contracts;
- exception leakage;
- label safety;
- model fail-closed;
- clinical wording;
- config invariants.

## Batch B — reliability/security

- admission;
- cancellation;
- limits;
- request IDs;
- headers;
- supply-chain controls.

## Batch C — UI/UX

- states;
- accessibility;
- responsive;
- privacy;
- honest score semantics.

## Batch D — reproducibility/operations

- lock;
- Docker;
- CI;
- SBOM;
- scans;
- observability.

После каждого batch:

```text
format
lint
types
targeted tests
full tests
diff review
```

---

# 42. Вариационная проверка

Проведи минимум четыре review passes.

## Review A — скептический биостатистик

- leakage и pseudoreplication;
- patient/slide denominator;
- cluster-aware CI;
- prevalence/PPV/NPV;
- calibration/threshold/test-set misuse;
- external validation и statistical claims.

## Review B — security/SRE red team

- malicious inputs;
- DoS/resource exhaustion;
- leaks/secrets/log injection;
- mutable model/dependencies/actions;
- concurrency/memory/timeouts/readiness;
- fail-open и incident recovery.

## Review C — clinical/regulatory reviewer

- cell result против patient diagnosis;
- intended use и human oversight;
- automation bias и terminology;
- clinical performance evidence;
- change control, monitoring и conditional applicability.

## Review D — логическая и математическая проверка

- weights и score;
- formula domains/division by zero;
- TP/TN/FP/FN consistency;
- units, CI и sample-size assumptions;
- contradictions между summary, risk, roadmap и verdict;
- воспроизводимый независимый calculation script.

Процесс:

```text
find
-> record
-> fix
-> targeted retest
-> full regression
```

## 42.1. Counterfactual check

Для каждого Critical/High finding зафиксируй:

```text
Primary hypothesis
Alternative hypothesis
Discriminating test
Observed result или NOT EXECUTED
Residual uncertainty
```

Для каждого irreversible/high-cost архитектурного решения сравни минимум три
варианта по преимуществам, недостаткам, стоимости, риску, обратимости и
evidence. Не принимай первую правдоподобную причину без discriminating test.

---

# 43. Definition of Done

Перед завершением выполни machine-checkable completeness checklist:

- выполненные команды и exit codes перечислены;
- NOT EXECUTED содержит причину;
- Critical findings имеют evidence и reproduction;
- model availability/license/labels/preprocessing/revision проверены либо
  явно UNKNOWN/BLOCKED;
- cell/slide/patient levels не смешаны;
- prevalence, calibration, uncertainty, OOD и independence рассмотрены;
- security, supply chain и capacity рассмотрены;
- regulatory conclusions условны;
- weights равны 100;
- формулы определяют переменные и domains;
- DOI/URL и access date проверены;
- recommendations, roadmap и verdict логически согласованы.

Software increment завершён только если:

- requirements linked;
- implementation complete;
- all available checks pass;
- coverage threshold pass;
- UI browser-tested;
- errors stable;
- security regression tested;
- docs updated;
- audit synchronized;
- residual risks explicit;
- no secret;
- no accidental user change loss;
- Git diff reviewed;
- no push/deploy without permission.

Real inference завершён только если:

- approved model;
- immutable revision;
- checksum;
- license;
- model card;
- label/processor contract;
- golden smoke;
- offline run;
- capacity measurements.

Clinical readiness завершена только если:

- intended use;
- data lineage;
- external evidence;
- statistical plan;
- human factors;
- QMS/risk;
- regulatory review;
- monitoring.

---

# 44. Обязательные deliverables

Создай канонический итоговый пакет:

```text
audit/
  EXECUTIVE_SUMMARY.md
  REPOSITORY_INVENTORY.md
  CLAIM_EVIDENCE_MATRIX.md
  TECHNICAL_AUDIT.md
  MODEL_AND_DATA_AUDIT.md
  STATISTICAL_VALIDATION_PLAN.md
  SECURITY_THREAT_MODEL.md
  CLINICAL_REGULATORY_GAP_ANALYSIS.md
  RISK_REGISTER.csv
  EVIDENCE_MATRIX.csv
  DEVELOPMENT_ROADMAP.md
  FINAL_GO_NO_GO.md
```

Executive summary обязан содержать общий verdict, technical/clinical
readiness, STOP-SHIP, top-5 risks/recommendations, VERIFIED и UNKNOWN.

Findings schema:

```text
ID | Domain | Severity | Fact/Inference | Evidence | Impact | Recommendation
```

Также создай implementation evidence:

```text
audit/implementation/
  README.md
  INPUT_BASELINE.md
  REQUIREMENTS.csv
  PRIORITIZATION.csv
  RISK_REGISTER.csv
  ARCHITECTURE_DECISIONS.md
  CHANGE_PLAN.md
  IMPLEMENTATION_LOG.md
  TEST_MATRIX.md
  SECURITY_REVIEW.md
  RELIABILITY_REVIEW.md
  UX_SAFETY_REVIEW.md
  VERIFICATION_REPORT.md
  FINAL_GO_NO_GO.md
```

При реализации новых contracts:

```text
docs/
  ARCHITECTURE.md
  API_CONTRACT.md
  MODEL_ARTIFACT_CONTRACT.md
  OPERATIONS.md
  SAFETY_LIMITATIONS.md
```

---

# 45. Формат implementation log

| Change ID | Requirement | Risk | Files | Behavior | Tests | Status | Residual |
|---|---|---|---|---|---|---|---|

Для каждого изменения:

```text
Before
After
Reason
Alternatives
Compatibility
Security effect
Operational effect
Verification
```

---

# 46. Финальный GO/NO-GO

Дай отдельный verdict:

- source development;
- local no-model UI;
- mocked demo;
- real-model local inference;
- container;
- public nonclinical API;
- research benchmark;
- retrospective research;
- prospective evaluation;
- clinical decision support;
- autonomous diagnosis.

Формат:

| Scenario | Verdict | Evidence | Blockers | Next gate |
|---|---|---|---|---|

Verdicts:

- `GO`;
- `CONDITIONAL_GO`;
- `NO_GO`;
- `INSUFFICIENT_EVIDENCE`.

Минимальные scenarios:

- Local demo;
- Public non-clinical API;
- Research use;
- Retrospective clinical research;
- Prospective silent evaluation;
- Clinical decision support;
- Autonomous diagnosis.

---

# 47. Финальный ответ пользователю

Начни с результата:

1. что реализовано;
2. какие проблемы закрыты;
3. какие tests прошли;
4. какие screenshots/runtime checks выполнены;
5. что осталось blocked;
6. ссылки на файлы.

Не скрывай:

- отсутствие модели;
- невозможность Docker;
- отсутствие vulnerability scanner;
- mocked nature tests;
- незапущенный CI;
- residual clinical risk;
- uncommitted changes.

---

# 48. Команда начала

После явной команды пользователя применить этот prompt:

```text
1. Прочитай prompt полностью.
2. Прочитай текущие audit artifacts.
3. Выполни preflight.
4. Зафиксируй baseline.
5. Выполни claim, architecture и model provenance gates.
6. Установи exact task и clinical pipeline gaps.
7. Выполни dataset/leakage gates.
8. Выполни mathematical validation или честно зафиксируй NOT_EXECUTED.
9. Создай requirements/prioritization.
10. Покажи или зафиксируй выбранные batches.
11. Реализуй разрешённые changes.
12. Проведи четыре review passes.
13. Исправь defects.
14. Сформируй final evidence и GO/NO-GO.
```

Не останавливайся после написания плана, когда пользователь отдельно
разрешил исполнение. Но если пользователь попросил сначала только
мастер-промпт, сохрани prompt и не начинай production changes до следующей
явной команды.
