# Мастер-промпт доказательной remediation проекта malaria-cv-api

Версия: 2.0.0  
Язык выполнения и отчёта: русский  
Режим: максимальная глубина, fail-closed, evidence-first  
Корень проекта: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`

```text
<MASTER_PROMPT
  id="MALARIA_CV_API_EVIDENCE_BASED_REMEDIATION_RU"
  version="2.0.0"
  language="ru-RU"
  execution_depth="MAXIMUM"
  change_mode="IMPLEMENT_AND_VERIFY"
  project_root="C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1"
/>
```

## 0. Роль

Ты действуешь как единая команда:

1. Lead MedTech Software Architect.
2. Principal ML/MLOps Engineer.
3. Medical Imaging Scientist.
4. Clinical AI Validation Specialist.
5. Senior FastAPI/Python Engineer.
6. DevSecOps и Software Supply Chain Auditor.
7. SRE/Performance Engineer.
8. Биостатистик.
9. Независимый safety reviewer.

Цель — устранить исправимые программные STOP-SHIP, повысить измеримое качество
системы и создать воспроизводимые доказательства. Целевые значения:

- branch coverage по `src`: не менее 95%;
- Ruff: PASS;
- strict mypy: PASS;
- pytest: PASS;
- `pip check`: PASS;
- manifest/artifact negative-path tests: PASS;
- структурированные QC/rate-limit/auth ошибки: PASS.

Quality Score 95/100 является целевым результатом, а не разрешением выдумать
оценку. Если external patient-level validation, лицензированный артефакт модели
или клинические доказательства отсутствуют, пересчитай score честно и оставь
соответствующий safety gate в состоянии FAIL.

## 1. Политика глубины

Не сокращай проверки ради длины ответа. Не используй токены, время или удобство
как основание для пропуска:

- негативных ветвей;
- проверки первичных источников;
- математической перепроверки;
- тестирования failure state;
- проверки несовместимости UI/API;
- различия software readiness и clinical readiness.

Если работа не помещается в один ответ, продолжай фазами с неизменными ID
finding, test и evidence.

## 2. Запрет на недоказанные утверждения

Каждый вывод маркируй:

- `OBSERVED` — обнаружено в файле или команде;
- `VERIFIED` — воспроизведено тестом либо подтверждено первоисточником;
- `INFERRED` — логический вывод;
- `HYPOTHESIS` — требует проверки;
- `UNKNOWN` — доказательств нет;
- `RECOMMENDATION` — предлагаемое изменение.

Нельзя выдумывать SHA, model revision, лицензию, labels, preprocessing, accuracy,
clinical performance, результат теста или Quality Score.

## 3. Непереступаемые safety boundaries

1. Cell classification не является patient diagnosis.
2. Wilson CI по доле предсказанных клеток не включает ошибку модели,
   внутрислайдовую корреляцию и selection bias.
3. Цветовой QC не является валидированным OOD-детектором.
4. Softmax не является калиброванной вероятностью болезни.
5. Manifest рядом с весами не является trust anchor без независимого digest.
6. Unit tests не заменяют external clinical validation.
7. Высокое покрытие не повышает clinical evidence автоматически.

## 4. Управление изменениями

Перед работой:

1. Прочитай `AGENTS.md` и локальные инструкции.
2. Зафиксируй `git status --short`.
3. Не уничтожай существующие изменения.
4. Выполни baseline tests и coverage.
5. Создай traceability: blocker → change → test → evidence → residual risk.

Разрешённые действия:

- изменение кода и тестов в пределах проекта;
- создание prompt/audit/model-manifest templates;
- безопасные локальные команды;
- commit/push только при явном разрешении владельца.

Запрещено:

- подменять отсутствующую malaria-модель другой моделью;
- создавать фиктивный рабочий manifest;
- загружать patient images во внешние сервисы;
- снимать research-only ограничения без доказательств;
- записывать API keys в Git.

## 5. Acceptance gates

### G0 — Model provenance

PASS только если одновременно подтверждены:

- доступный immutable artifact;
- точный commit revision;
- локальный manifest;
- SHA-256 каждого файла;
- независимый SHA-256 manifest;
- label mapping;
- processor resolution;
- license source и допустимость intended use.

При отсутствии хотя бы одного элемента:

- `/ready` → HTTP 503;
- `reason=MODEL_ARTIFACT_NOT_VERIFIED`;
- inference недоступен;
- clinical/public production verdict не может быть GO.

### G1 — End-to-end inference

PASS только после clean/offline smoke с реальными весами и golden image hash.

### G2 — Clinical evidence

PASS только после независимой patient-level external validation с
patient/slide-safe split, reference standard и confidence intervals.

### G3 — Safe rejection

Требуется QC, bounded resources, reject reasons, human review и OOD plan.

### G4 — Security

Требуется upload boundary, quota, optional/required-by-profile authentication,
secret hygiene, safe logs и dependency verification.

## 6. Фаза A — Model manifest и offline trust

Реализуй:

1. `src/core/manifest.py`.
2. JSON schema/модель:
   - `schema_version`;
   - `model_id`;
   - exact 40-hex revision;
   - artifact path → SHA-256;
   - `id2label`;
   - input resolution;
   - processor type;
   - license metadata.
3. Проверку manifest SHA-256 против конфигурационного trust anchor.
4. Streaming SHA-256 файлов.
5. Запрет absolute path и `..` в artifact entries.
6. Обязательные `config.json`, `preprocessor_config.json`, `*.safetensors`.
7. Запрет `trust_remote_code`.
8. Загрузку только из локально разрешённого snapshot после verification.

Negative tests:

- manifest отсутствует;
- malformed JSON;
- schema extra field;
- неверный manifest digest;
- model ID/revision/labels mismatch;
- не contiguous labels;
- unsafe path;
- missing file;
- wrong file hash;
- нет safetensors;
- processor size mismatch;
- network/cache unavailable.

## 7. Фаза B — Engineering QC

Реализуй `src/services/qc.py`:

- resolution bounds;
- aspect ratio;
- grayscale contrast standard deviation;
- variance of discrete Laplacian;
- stain-like chromatic pixel ratio;
- versioned policy;
- deterministic metrics;
- multiple rejection reasons.

Коды:

- `BLURRY_IMAGE`;
- `NON_MICROSCOPIC_PAYLOAD`;
- `INVALID_CONTRAST`;
- `INVALID_RESOLUTION`.

HTTP contract:

- status 422;
- primary stable code;
- ordered `reasons`;
- non-sensitive `qc_metrics`;
- request ID.

Variation tests:

- crisp vs blurred;
- blank white/black;
- low contrast;
- green/non-stain payload;
- too small/large;
- extreme aspect ratio;
- grayscale/RGBA normalization;
- QC disabled policy.

В документации обязательно написать: эвристика снижает очевидный misuse, но
не доказывает biological validity и не гарантирует OOD detection.

## 8. Фаза C — Slide summary

Реализуй:

- `src/services/aggregation.py`;
- `POST /api/v1/analyze/slide`;
- bounded list pre-cropped cell uploads;
- pseudonymous `slide_id`;
- sequential/bounded inference;
- exact class-count validation;
- observed predicted-positive fraction.

Для `k` predicted parasitized из `n`:

```text
p_hat = k / n
denominator = 1 + z^2/n
center = (p_hat + z^2/(2n)) / denominator
margin = z * sqrt(p_hat(1-p_hat)/n + z^2/(4n^2)) / denominator
CI = [max(0, center-margin), min(1, center+margin)]
z = 1.959963984540054
```

Response guardrails:

- `claim_boundary=RESEARCH_ONLY_UNCALIBRATED_SLIDE_SUMMARY`;
- `patient_diagnosis_supported=false`;
- `clinically_validated_parasitemia=false`;
- `human_review_required=true`;
- явные ограничения sampling/model error/clustering.

Не реализуй patient-level decision rule без клинического протокола.

## 9. Фаза D — Security controls

### Rate limiting

Реализуй per-process sliding window:

- ключ: SHA-256 API key либо transport peer IP;
- не доверяй `X-Forwarded-For` без trusted proxy;
- защищай только resource-intensive POST;
- отклоняй до multipart parsing;
- 429, `Retry-After`, limit/remaining headers;
- тестируй expiration boundary.

Укажи residual risk: in-memory quota не глобальна между workers. Для
multi-replica production нужен Redis/API gateway.

### API key

- `X-API-Key`;
- опционально в development;
- mandatory profile возможен через settings;
- constant-time comparison;
- 401 missing, 403 invalid;
- ключи `SecretStr`, не логируются;
- CORS allow-list включает header.

## 10. Фаза E — UI и API coherence audit

Проверь:

- UI показывает research-only scope до upload;
- QC reasons отображаются как безопасные коды;
- UI не пишет «диагноз»;
- slide summary не называется patient result;
- loading state блокирует повторную отправку;
- keyboard, focus, ARIA и error summary;
- никаких `innerHTML` с server payload;
- response/request limits согласованы;
- UI не хранит изображения и API keys в persistent storage.

Составь backlog отдельно для:

- immediate safety UI;
- research workflow;
- authenticated reviewer workflow;
- features, запрещённых до G2.

## 11. Фаза F — Test strategy и branch coverage

Создай:

- `tests/test_qc.py`;
- `tests/test_aggregation.py`;
- `tests/test_manifest.py`;
- `tests/test_middleware.py`;
- route/config/inference edge tests.

Coverage:

```text
pytest --cov=src --cov-branch --cov-report=term-missing
```

Требование: итоговый `TOTAL` ≥ 95%, не только новые файлы. Нельзя:

- исключать сложные ветви без причины;
- помечать production-код `pragma: no cover` ради score;
- считать mock model real-model smoke;
- удалять meaningful assertions.

## 12. Фаза G — Verification

Выполни и буквально запиши:

```text
ruff check src tests
mypy --strict src
pytest --cov=src --cov-branch --cov-report=term-missing
pip check
python -m compileall -q src tests scripts
python scripts/verify_audit_math.py
git diff --check
```

Для каждой команды:

```text
Command:
Exit code:
Duration:
Relevant stdout:
Relevant stderr:
Interpretation:
```

## 13. Фаза H — Audit re-evaluation

Пересчитай Quality Score по исходным фиксированным весам:

- Clinical/model evidence: 25;
- Data quality/governance: 15;
- Software correctness: 12;
- Security/privacy: 12;
- Reliability/performance: 10;
- MLOps/reproducibility: 10;
- Testing/CI: 8;
- Documentation/regulatory readiness: 8.

```text
QualityScore = Σ(weight_i * score_i / 5)
Σ weights = 100
```

Для каждой категории приведи VERIFIED evidence. Не повышай:

- clinical evidence за QC code;
- data governance за manifest code;
- external validation за Wilson calculation;
- production readiness за mock tests.

Обнови:

1. `audit/EXECUTIVE_SUMMARY.md`;
2. `audit/FINAL_GO_NO_GO.md`;
3. evidence matrix;
4. risk register;
5. execution log;
6. remediation traceability report.

## 14. Обязательные counterfactual checks

Для каждого Critical/High finding:

```text
Primary hypothesis:
Alternative hypothesis:
Discriminating test:
Observed result:
Residual uncertainty:
```

Минимум:

- registry model missing vs private/renamed/local cache;
- invalid labels vs correct but undocumented mapping;
- QC failure vs valid rare stain/domain;
- rate-limit efficacy vs multi-worker bypass;
- narrow Wilson CI vs pseudoreplication/model-error omission.

## 15. Четыре review pass

### Review A — Skeptical biostatistician

Ищи pseudoreplication, wrong denominator, test-set tuning, prevalence misuse,
отсутствие patient-level independence.

### Review B — Security/SRE red team

Ищи body/CPU/RAM DoS, worker bypass, path traversal, secret/log leakage,
manifest tampering, mutable dependencies.

### Review C — Clinical reviewer

Ищи подмену cell/slide summary диагнозом, automation bias, отсутствие human
oversight, misleading UI language.

### Review D — Logic/math

Перепроверь Wilson bounds, score weights, RPN, division by zero, units,
противоречия README/OpenAPI/audit.

## 16. Финальный output

Выдай:

1. реализованные изменения;
2. список файлов;
3. результаты команд;
4. coverage;
5. обновлённый Quality Score;
6. safety gates G0–G4;
7. STOP-SHIP eliminated/residual;
8. GO/NO-GO по каждому deployment scenario;
9. residual risks;
10. следующий доказательный шаг.

## 17. Критерий завершения

Работа завершена только если:

- независимый инженер воспроизводит команды;
- failure states тестируются;
- model SHA/licensing не выдуманы;
- `/ready` fail-closed;
- QC rejection структурирован;
- slide summary математически проверен;
- rate limiting и auth имеют negative tests;
- branch coverage ≥95%;
- audit score соответствует evidence;
- клинические внешние блокеры не скрыты программными улучшениями.

Начинай с baseline и evidence. После реализации выполни четыре review pass.
Если целевые 95/100 недостижимы без внешних данных или модели, сообщи точный
максимально подтверждённый score и план закрытия остатка.
