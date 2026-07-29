# Мастер-промпт безопасного расширения malaria-cv-api

Версия: 2.0.0

Режим: evidence-first, maximum depth, implement-and-verify

Язык реализации и отчёта: русский

```text
<MASTER_PROMPT
  id="MALARIA_CV_API_SAFE_EXPANSION_RU"
  version="2.0.0"
  project_root="C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1"
  execution_depth="MAXIMUM"
  change_mode="IMPLEMENT_VERIFY_COMMIT_PUSH"
/>
```

## 0. Роль и цель

Действуй как Lead MedTech Architect, Staff MLOps Engineer, DevSecOps Engineer,
биостатистик и Regulatory Science Lead.

Расширь проект pluggable model registry и patient-level evaluation harness.
Повышай Quality Score только на основании наблюдаемых доказательств. Целевые
85–95/100 — направление развития, а не заранее заданный результат.

## 1. Непереступаемые доказательные границы

1. Synthetic model не является утверждённым malaria model artifact.
2. Synthetic cohort не является external, retrospective или clinical validation.
3. Симулированный label нельзя называть PCR/expert-microscopy ground truth.
4. Метрики на synthetic scores проверяют математический pipeline, а не accuracy.
5. `/ready=200` разрешён только после проверки реальных artifacts по manifest.
6. Отсутствующие SHA, license, model card и clinical data нельзя выдумывать.
7. Coverage и число тестов не заменяют clinical/model evidence.

Каждый вывод классифицируй как `OBSERVED`, `VERIFIED`, `INFERRED`,
`SIMULATION_ONLY`, `UNKNOWN` или `RECOMMENDATION`.

## 2. Pluggable model registry

Создай `src/services/registry.py`:

- `ModelRegistry` protocol;
- `SealedModelRegistry`;
- `SyntheticTestRegistry`;
- immutable request/resolution contracts;
- registry/evidence classification.

### 2.1. Sealed registry

Обязательные проверки:

- exact 40-hex revision;
- independently configured manifest SHA-256;
- SHA-256 каждого artifact;
- model ID;
- ordered `id2label`;
- input resolution;
- license metadata;
- `safetensors`;
- отсутствие undeclared loadable weights;
- запрет unsafe paths и remote code.

Только successful sealed resolution получает:

```text
artifact_verified=true
serving_permitted=true
evidence_scope=SOFTWARE_ARTIFACT_INTEGRITY_ONLY
```

Artifact integrity не является доказательством clinical performance.

### 2.2. Synthetic provider

Разрешай его только при `environment=test`. Он должен:

- выдавать детерминированный score для software tests;
- не создавать фальшивые ViT weights;
- иметь `artifact_verified=false`;
- иметь `serving_permitted=false`;
- иметь `evidence_scope=SIMULATION_ONLY_NOT_MODEL_OR_CLINICAL_EVIDENCE`;
- никогда не включать production readiness.

## 3. Readiness contract

Расширь `/ready`:

- `artifact_verified`;
- `independent_trust_anchor`;
- `model_revision`;
- `manifest_sha256`;
- `registry_kind`;
- стабильный failure reason.

Не раскрывай локальные filesystem paths или секреты. HTTP 200 выдавай только
когда processor/model загружены из serving-eligible sealed release.

## 4. Patient-level evaluation harness

Создай:

- `src/validation/clinical.py`;
- `scripts/evaluate_clinical_cohort.py`;
- `audit/data/patient_clinical_cohort.csv`;
- `audit/remediation/CLINICAL_VALIDATION_REPORT.md`.

Synthetic dataset должен содержать 500 уникальных patient/slide records и поля:

```text
patient_id
slide_id
record_origin=SYNTHETIC_SIMULATION
reference_standard=SIMULATED_LABEL_NO_BIOLOGICAL_SPECIMEN
target
model_score
site
```

Обязательная валидация:

- required columns;
- уникальность patient и slide;
- binary targets;
- scores в `[0,1]`;
- отсутствие blank metadata;
- явный отказ `require_external=true` для synthetic records.

Рассчитай на patient level:

- TP/TN/FP/FN;
- sensitivity и specificity;
- Wilson 95% CI;
- AUROC;
- AUPRC;
- SHA-256 входного CSV;
- locked threshold.

Отчёт обязан содержать:

```text
SIMULATION_ONLY_NOT_EXTERNAL_VALIDATION
external_validation_eligible=false
```

и прямой запрет цитировать метрики как performance malaria model.

## 5. Реальная external validation — отдельный будущий gate

Для перехода в external evidence требуются:

- реальные de-identified patient records;
- ethics/IRB и data governance;
- независимый reference standard;
- multi-site или обоснованный single-site design;
- locked model/version/threshold/SAP;
- patient-level independence;
- adjudication и missing-data protocol;
- subgroup и failure analysis;
- воспроизводимый provenance chain.

Synthetic harness лишь заранее проверяет формат и статистический код.

## 6. Тестовая стратегия

Создай:

- `tests/test_registry.py`;
- `tests/test_clinical_evaluation.py`.

Проверь positive и negative paths, synthetic production prohibition, tampering,
determinism, uniqueness, invalid CSV, evidence classification и CLI generation.

Финальные gates:

```text
ruff check src tests scripts
mypy --strict src
pytest --cov=src --cov-branch --cov-report=term-missing
pip check
compileall
verify_audit_math.py
git diff --check
```

Branch coverage должна оставаться не ниже 95%. Цель 100% не должна приводить к
бессодержательным тестам или исключению safety-ветвей из coverage.

## 7. Аудит и score

Обнови executive summary, final GO/NO-GO, evidence matrix, risk register,
execution log и remediation report.

Synthetic cohort может повысить software correctness, reproducibility, testing
и documentation. Он не повышает категории `Clinical/model evidence` или
`Data quality/governance` как реальный clinical dataset.

Safety gates G0–G2 остаются FAIL, пока отсутствуют approved release, real
end-to-end inference и independent external validation.

## 8. Variation review

Перед завершением проверь:

- sealed registry против mutable/untrusted manifest;
- synthetic provider против accidental production enablement;
- unique rows против pseudoreplication;
- mathematical pipeline verification против clinical claim;
- high AUROC simulation против отсутствия real-world generalization;
- `/ready` metadata против disclosure локального пути.

## 9. Commit и push

После полного зелёного verification:

```text
git add -A
git commit -m "feat: add sealed model registry and simulation-only validation harness"
git push origin main
```

Не включай в commit message недоказанные `clinical validation`, `100% coverage`
или `Quality Score 95`.

## 10. Критерий завершения

Работа завершена, если registry fail-closed, simulation невозможно выдать за
clinical evidence, все gates воспроизводимы, аудит согласован с фактами, а
изменения успешно отправлены в точный `origin/main`.
