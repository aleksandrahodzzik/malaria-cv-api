# Отдельный мастер-промпт планирования и оркестрации аудита `malaria-cv-api`

Версия: `1.0.0`  
Язык выполнения и отчёта: русский  
Режим глубины: максимальный  
Тип задачи: разработка и исполнение доказательного плана аудита  
Корень проекта: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`  
Спецификация аудита:
`PROMPTS\MASTER_AUDIT_PROMPT_RU.md`

---

## Мастер-промпт

```text
<MASTER_PROMPT>
  <ID>MALARIA_CV_API_AUDIT_EXECUTION_ORCHESTRATOR_RU</ID>
  <VERSION>1.0.0</VERSION>
  <LANGUAGE>ru-RU</LANGUAGE>
  <EXECUTION_DEPTH>MAXIMUM</EXECUTION_DEPTH>
  <MODE>READ_ONLY_EVIDENCE_FIRST</MODE>
  <PROJECT_ROOT>
    C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1
  </PROJECT_ROOT>
  <AUDIT_SPECIFICATION>
    C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1\PROMPTS\MASTER_AUDIT_PROMPT_RU.md
  </AUDIT_SPECIFICATION>
  <CURRENT_DATE>Определи по системному времени</CURRENT_DATE>
</MASTER_PROMPT>


# 0. НАЗНАЧЕНИЕ

Твоя задача — не переписать спецификацию аудита и не пересказать её.

Ты должен:

1. Полностью прочитать `AUDIT_SPECIFICATION`.
2. Преобразовать требования спецификации в исполнимый пошаговый план.
3. Определить зависимости между этапами.
4. Назначить каждому этапу входы, действия, инструменты, выходы и критерии
   завершения.
5. Выполнить план, если пользователь не ограничил задачу только
   проектированием.
6. Поддерживать журнал доказательств и состояния.
7. Останавливать клинические или production-рекомендации, если отсутствуют
   обязательные доказательства.
8. Выполнить независимую верификацию результата несколькими способами.

Основной файл `MASTER_AUDIT_PROMPT_RU.md` является предметной спецификацией.
Настоящий файл является отдельным промпт-оркестратором исполнения.


# 1. НЕПРИКОСНОВЕННЫЕ ПРИНЦИПЫ

## 1.1. Полнота

Не сокращай обязательную область аудита ради краткости.

Не используй ограничения длины ответа как причину:

- пропустить этап;
- не проверить источник;
- не выполнить доступную команду;
- заменить вычисление субъективной оценкой;
- скрыть неизвестное;
- объединить независимые риски;
- объявить работу завершённой до прохождения exit gates.

Если контекст или ответ заканчивается:

1. Сохрани состояние.
2. Зафиксируй завершённые результаты.
3. Продолжи с первой незавершённой операции.
4. Не повторяй уже подтверждённые действия без необходимости.
5. Не сокращай остаток задачи для искусственного завершения.

## 1.2. Доказательность

Разрешённые классы утверждений:

- `OBSERVED`;
- `VERIFIED`;
- `INFERRED`;
- `HYPOTHESIS`;
- `RECOMMENDATION`;
- `UNKNOWN`.

Запрещено:

- выдавать `HYPOTHESIS` за `VERIFIED`;
- писать, что тест прошёл, если он не выполнялся;
- указывать метрики без исходных данных;
- выдумывать DOI, стандарты, версии или лицензии;
- скрывать отрицательные результаты;
- считать отсутствие найденных данных доказательством их отсутствия.

## 1.3. Безопасность действий

По умолчанию работай в режиме `READ_ONLY`.

Разрешены:

- чтение файлов;
- безопасные диагностические команды;
- тесты;
- статический анализ;
- создание аудиторских артефактов в `audit/`;
- временные файлы в безопасном временном каталоге.

Без отдельного разрешения запрещены:

- изменение production-кода;
- push;
- deployment;
- изменение remote;
- удаление пользовательских файлов;
- внешняя отправка медицинских изображений;
- загрузка больших моделей без оценки размера;
- действия, влияющие на реальных пользователей.


# 2. ПРЕДВАРИТЕЛЬНЫЙ РАЗБОР ЗАДАЧИ

До выполнения аудита создай `Audit Charter`:

| Поле | Требование |
|---|---|
| Project | malaria-cv-api |
| Project root | Абсолютный путь |
| Audit specification | Абсолютный путь |
| Intended output | План и/или полный аудит |
| Mutation policy | READ_ONLY |
| Scientific scope | Medical imaging, malaria, ML validation |
| Engineering scope | API, Docker, CI/CD, MLOps, SRE |
| Safety scope | Clinical, security, privacy |
| Jurisdiction | Определить; по умолчанию проверить EU/Poland и условно USA |
| Known constraints | Зафиксировать по среде |
| Unknowns | Перечислить |

Определи смысл запроса пользователя:

- `PLAN_ONLY`: создать детальный план без исполнения;
- `PLAN_AND_EXECUTE`: создать план и выполнить его;
- `EXECUTE_EXISTING_PLAN`: использовать существующий план;
- `UPDATE_AUDIT`: обновить ранее созданный аудит.

Если режим явно не указан, используй `PLAN_AND_EXECUTE`, но сохраняй
READ_ONLY-политику.


# 3. ДЕКОМПОЗИЦИЯ НА WORK PACKAGES

Преобразуй спецификацию аудита в следующие work packages.

## WP-00 — Preflight

Входы:

- project root;
- локальные инструкции;
- разрешения среды;
- текущая дата.

Действия:

- подтвердить путь;
- найти инструкции;
- определить доступные инструменты;
- зафиксировать ОС, Python, Docker, Git и Make;
- найти незавершённую предыдущую работу.

Выходы:

- environment record;
- limitations record;
- initial assumptions.

Exit gate:

- корень проекта подтверждён;
- ограничения известны;
- опасные действия не запланированы.

## WP-01 — Repository inventory

Действия:

- построить полное дерево;
- классифицировать файлы;
- определить entrypoints;
- определить компоненты;
- определить внешние сервисы;
- построить dependency map.

Выходы:

- `REPOSITORY_INVENTORY.md`;
- architecture map;
- artifact register.

Exit gate:

- каждый существенный компонент связан с исходным файлом.

## WP-02 — Reproducibility

Действия:

- проверить зависимости;
- проверить совместимость Python;
- выполнить lint;
- выполнить type checking;
- выполнить tests;
- проверить запуск приложения;
- проверить сборку контейнера, если Docker доступен.

Для каждой команды сохранить:

| Command | Exit code | Duration | Stdout summary | Stderr | Verdict |

Exit gate:

- ни один результат не заявлен без вывода команды;
- невыполненные проверки явно отмечены.

## WP-03 — Claim verification

Действия:

- извлечь claims из README, комментариев и deployment-файлов;
- определить проверяемый критерий каждого claim;
- сопоставить claim с evidence.

Вердикты:

- `SUPPORTED`;
- `PARTIALLY_SUPPORTED`;
- `UNSUPPORTED`;
- `CONTRADICTED`;
- `NOT_TESTABLE`.

Выход:

- `CLAIM_EVIDENCE_MATRIX.md`.

## WP-04 — Software architecture

Области:

- FastAPI;
- lifecycle;
- dependency injection;
- request/response contracts;
- upload pipeline;
- error handling;
- concurrency;
- thread pool;
- timeouts;
- cancellation;
- middleware;
- configuration;
- observability.

Exit gate:

- у каждого Critical/High finding есть reproduction и code reference.

## WP-05 — Model provenance

Проверить:

- существование model ID;
- публичную доступность;
- model card;
- license;
- training data;
- metrics;
- revision;
- checksum;
- labels;
- preprocessing;
- unsafe pickle/remote code;
- воспроизводимость без локального кэша.

Safety gate:

Если модель не существует, не лицензирована или labels неизвестны:

`MODEL_GATE = FAIL`

и production verdict не может быть `GO`.

## WP-06 — Data audit

Проверить:

- provenance;
- patient/slide/cell hierarchy;
- leakage;
- duplicate images;
- annotation;
- class balance;
- prevalence;
- selection bias;
- spectrum bias;
- domain shift;
- licensing;
- privacy.

Выход:

- `DATASET_DATASHEET.md`.

## WP-07 — Statistical validation

Требуемые уровни:

- cell;
- slide;
- patient.

Требуемые метрики:

- sensitivity;
- specificity;
- PPV;
- NPV;
- F1;
- MCC;
- balanced accuracy;
- AUROC;
- AUPRC;
- confidence intervals;
- calibration;
- risk-coverage.

Запрещено смешивать уровни наблюдения.

## WP-08 — Robustness and OOD

Проверить:

- corruptions;
- blur;
- scale;
- stain shift;
- microscope shift;
- non-cell input;
- non-blood input;
- empty background;
- adversarial/resource attacks;
- uncertainty;
- reject option.

## WP-09 — Performance and capacity

Измерить:

- cold/warm startup;
- p50/p95/p99;
- throughput;
- CPU;
- RAM;
- concurrency;
- failure rate;
- model duplication between workers.

Использовать:

ρ = λ / (cμ)

L = λW

RAM_total ≈
c × (RAM_model + RAM_runtime + RAM_activation_peak)
+ shared_memory
+ upload_buffers
+ safety_margin

## WP-10 — Security and privacy

Использовать:

- STRIDE;
- OWASP API Security Top 10;
- NIST SSDF;
- NIST AI RMF;
- supply-chain analysis.

Для каждого риска описать реальный attack scenario.

## WP-11 — Clinical and regulatory

Определить:

- intended use;
- intended user;
- patient population;
- workflow;
- human review;
- false-negative harm;
- false-positive harm;
- EU MDR/IVDR applicability;
- EU AI Act applicability;
- GDPR;
- FDA/IMDRF applicability, если релевантно.

Не выдавать юридическое заключение.

## WP-12 — Risk register and roadmap

Рассчитать:

RPN = Severity × Occurrence × Detectability

AdjustedPriority = RPN × (1 + Uncertainty)

Для рекомендаций:

PriorityScore =
(Impact × Urgency × Evidence) /
sqrt(Effort × DependencyComplexity)

STOP-SHIP имеет приоритет над числовыми оценками.

## WP-13 — Independent review

Выполнить четыре прохода:

1. Biostatistics.
2. Security/SRE.
3. Clinical/regulatory.
4. Logic/mathematics.

## WP-14 — Final synthesis

Собрать:

- executive summary;
- findings;
- evidence matrix;
- risk register;
- validation plan;
- roadmap;
- отдельные GO/NO-GO verdicts.


# 4. STATE MACHINE

Используй эту state machine без пропуска обязательных переходов:

<STATE_MACHINE format="yaml">
audit:
  initial: PRECHECK

  transitions:
    PRECHECK:
      next: INVENTORY
      gate: environment_and_scope_recorded

    INVENTORY:
      next: REPRODUCIBILITY
      gate: artifact_register_complete

    REPRODUCIBILITY:
      next: CLAIM_VERIFICATION
      gate: commands_and_failures_recorded

    CLAIM_VERIFICATION:
      next: SOFTWARE_AUDIT
      gate: claim_matrix_complete

    SOFTWARE_AUDIT:
      next: MODEL_PROVENANCE
      gate: technical_findings_reproducible

    MODEL_PROVENANCE:
      next: DATA_AUDIT
      gate: model_gate_decided

    DATA_AUDIT:
      next: STATISTICAL_VALIDATION
      gate: dataset_datasheet_complete

    STATISTICAL_VALIDATION:
      next: ROBUSTNESS
      gate: metrics_reproducible_or_marked_unknown

    ROBUSTNESS:
      next: PERFORMANCE
      gate: failure_taxonomy_complete

    PERFORMANCE:
      next: SECURITY
      gate: measurements_or_not_executed_reasons_recorded

    SECURITY:
      next: CLINICAL_REGULATORY
      gate: threat_model_complete

    CLINICAL_REGULATORY:
      next: RISK_ROADMAP
      gate: intended_use_and_applicability_recorded

    RISK_ROADMAP:
      next: INDEPENDENT_REVIEW
      gate: critical_risks_have_mitigations

    INDEPENDENT_REVIEW:
      next: FINAL_REPORT
      gate: contradictions_resolved_or_disclosed

    FINAL_REPORT:
      terminal: true
      gate: final_checklist_passed
</STATE_MACHINE>


# 5. ЖУРНАЛ СОСТОЯНИЯ

После каждого work package обновляй:

| Field | Value |
|---|---|
| Current state | |
| Completed work packages | |
| Pending work packages | |
| Blocking conditions | |
| Assumptions | |
| Unknowns | |
| Evidence count | |
| Critical findings | |
| Last command | |
| Last artifact | |

Если выполнение прерывается, этот журнал является точкой продолжения.


# 6. EVIDENCE LEDGER

Каждое доказательство регистрируй:

| Evidence ID | Type | Source | Access date | Command/URL | Result | Reliability |
|---|---|---|---|---|---|---|

Типы:

- `CODE`;
- `CONFIG`;
- `COMMAND_OUTPUT`;
- `TEST_RESULT`;
- `MODEL_ARTIFACT`;
- `DATASET_ARTIFACT`;
- `PRIMARY_PAPER`;
- `OFFICIAL_GUIDANCE`;
- `REGULATORY_TEXT`;
- `EXPERT_ASSUMPTION`.

Надёжность:

- `HIGH`;
- `MEDIUM`;
- `LOW`.

Правила:

1. Code comment не равен доказательству поведения.
2. README не равен результату теста.
3. Model card не заменяет внешнюю валидацию.
4. Reporting guideline не является сертификацией.
5. Локальный кэш не доказывает воспроизводимость чистого deployment.
6. Cell-level accuracy не доказывает patient-level diagnostic performance.


# 7. МАТЕМАТИЧЕСКИЙ КОНТРОЛЬ

Проверь формулы и знаменатели.

Sensitivity = TP / (TP + FN)

Specificity = TN / (TN + FP)

PPV = TP / (TP + FP)

NPV = TN / (TN + FN)

F1 = 2TP / (2TP + FP + FN)

MCC =
(TP×TN - FP×FN) /
sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))

Для prevalence π:

PPV(π) =
Se×π / [Se×π + (1-Sp)(1-π)]

NPV(π) =
Sp(1-π) / [(1-Se)π + Sp(1-π)]

Для calibration:

Brier =
(1/N) Σ_i (p_i-y_i)^2

NLL =
-(1/N) Σ_i [
y_i log(p_i) + (1-y_i)log(1-p_i)
]

ECE =
Σ_b (n_b/N) × |accuracy_b-confidence_b|

Для threshold:

ExpectedCost(t) =
C_FN×FN(t)
+ C_FP×FP(t)
+ C_REJECT×Reject(t)
+ C_DELAY×Delay(t)

Все числа перепроверь отдельным скриптом.

Не считай клетки независимыми, если они принадлежат одному пациенту или
предметному стеклу. Применяй cluster bootstrap или соответствующую
иерархическую модель.


# 8. УПРАВЛЕНИЕ НЕИЗВЕСТНОСТЬЮ

Для каждого неизвестного укажи:

| Unknown ID | Question | Why it matters | How to verify | Blocking? |

Если входных данных недостаточно:

- не угадывай;
- продолжай независимые этапы;
- обозначь влияние неизвестности;
- подготовь конкретный запрос владельцу проекта;
- не блокируй весь аудит, если можно выполнить другие work packages.


# 9. ВАРИАЦИЯ И АЛЬТЕРНАТИВНЫЕ ГИПОТЕЗЫ

Для каждого Critical/High finding:

1. Сформулируй primary hypothesis.
2. Сформулируй минимум одну alternative hypothesis.
3. Определи discriminating test.
4. Выполни тест, если он безопасен.
5. Обнови confidence.

Формат:

Primary hypothesis:
Alternative hypothesis:
Discriminating evidence:
Test:
Result:
Updated confidence:

Для ключевых архитектурных рекомендаций предложи минимум три варианта.

Сравни:

- эффект;
- усилия;
- риск;
- обратимость;
- зависимости;
- научную обоснованность;
- клиническую применимость.


# 10. НЕЗАВИСИМЫЕ REVIEW PASSES

## Reviewer A — биостатистик

Ищи:

- leakage;
- pseudoreplication;
- неправильный split;
- неверный denominator;
- prevalence bias;
- calibration leakage;
- threshold overfitting;
- некорректные confidence intervals;
- отсутствие patient-level evidence.

## Reviewer B — Security/SRE

Ищи:

- DoS;
- resource exhaustion;
- malicious input;
- unbounded concurrency;
- missing timeout;
- supply-chain compromise;
- mutable model;
- secrets;
- monitoring gaps.

## Reviewer C — Clinical/regulatory

Ищи:

- подмену screening диагнозом;
- отсутствие intended use;
- отсутствие human oversight;
- automation bias;
- misleading confidence;
- отсутствие clinical evidence;
- необоснованные regulatory statements.

## Reviewer D — Logic/mathematics

Ищи:

- арифметические ошибки;
- несогласованные единицы;
- противоречивые verdicts;
- неверные формулы;
- division by zero;
- неправильное суммирование весов;
- рекомендации без связи с findings.


# 11. ПРИОРИТИЗАЦИЯ

QualityScore:

- Clinical/model evidence: 25
- Data quality/governance: 15
- Software correctness: 12
- Security/privacy: 12
- Reliability/performance: 10
- MLOps/reproducibility: 10
- Testing/CI: 8
- Documentation/regulatory readiness: 8

Сумма:

25 + 15 + 12 + 12 + 10 + 10 + 8 + 8 = 100

QualityScore =
Σ(weight_i × score_i / 5)

Safety gates:

- G0: модель существует и лицензирована;
- G1: end-to-end inference воспроизводим;
- G2: есть независимая validation;
- G3: реализован safe failure;
- G4: есть security baseline;
- G5: определён intended use;
- G6: claims соответствуют evidence.

Если G0 или G1 не пройдены:

`TECHNICAL_PRODUCTION = NO-GO`

Если G2 не пройден:

`CLINICAL_DEPLOYMENT = NO-GO`


# 12. ROADMAP

Сформируй планы:

- 0–7 дней;
- 8–30 дней;
- 31–60 дней;
- 61–90 дней;
- 3–6 месяцев;
- 6–12 месяцев, если клиническая стратегия реалистична.

Для каждого пункта:

| ID | Action | Evidence | Owner role | Dependencies | Effort | Exit criterion |

Порядок:

1. STOP-SHIP.
2. Patient safety.
3. Regulatory mandatory.
4. Reproducibility.
5. Security.
6. Validation.
7. Reliability.
8. Performance.
9. Product features.


# 13. ВЫХОДНЫЕ АРТЕФАКТЫ

В режиме `PLAN_ONLY` создай:

1. `AUDIT_CHARTER.md`
2. `AUDIT_EXECUTION_PLAN.md`
3. `AUDIT_DEPENDENCY_MAP.md`
4. `AUDIT_TEST_MATRIX.md`
5. `AUDIT_EVIDENCE_REQUIREMENTS.md`
6. `AUDIT_ACCEPTANCE_GATES.md`

В режиме `PLAN_AND_EXECUTE` дополнительно создай:

7. `EXECUTIVE_SUMMARY.md`
8. `REPOSITORY_INVENTORY.md`
9. `CLAIM_EVIDENCE_MATRIX.md`
10. `TECHNICAL_AUDIT.md`
11. `MODEL_AND_DATA_AUDIT.md`
12. `STATISTICAL_VALIDATION_PLAN.md`
13. `SECURITY_THREAT_MODEL.md`
14. `CLINICAL_REGULATORY_GAP_ANALYSIS.md`
15. `RISK_REGISTER.csv`
16. `EVIDENCE_MATRIX.csv`
17. `DEVELOPMENT_ROADMAP.md`
18. `FINAL_GO_NO_GO.md`

Храни аудиторские материалы отдельно от production-кода.


# 14. ФИНАЛЬНЫЕ VERDICTS

Выдай отдельный verdict для:

- local demo;
- public non-clinical API;
- research use;
- retrospective clinical research;
- prospective silent evaluation;
- clinical decision support;
- autonomous diagnosis.

Допустимые значения:

- `GO`;
- `CONDITIONAL GO`;
- `NO-GO`;
- `INSUFFICIENT EVIDENCE`.

У каждого verdict должны быть:

- evidence;
- unmet gates;
- residual risks;
- условия перехода к следующему статусу.


# 15. ФИНАЛЬНАЯ ПРОВЕРКА

Перед завершением проверь:

[ ] Полностью прочитана спецификация аудита.
[ ] Режим задачи определён.
[ ] Все work packages рассмотрены.
[ ] Все выполненные команды зарегистрированы.
[ ] Невыполненные проверки обозначены.
[ ] Нет выдуманных результатов.
[ ] Проверена доступность модели.
[ ] Проверены license, revision, labels и preprocessing.
[ ] Cell-, slide- и patient-level evidence разделены.
[ ] Проверен patient-level split.
[ ] Смоделирован prevalence shift.
[ ] Проверена calibration.
[ ] Рассмотрена uncertainty и reject option.
[ ] Проведён software audit.
[ ] Проведён security audit.
[ ] Проведён clinical/regulatory review.
[ ] Проверена производительность или указана причина отсутствия измерений.
[ ] Critical/High findings имеют evidence.
[ ] Critical/High findings имеют acceptance criteria.
[ ] Выполнены альтернативные гипотезы.
[ ] Проведены четыре независимых review pass.
[ ] Математика перепроверена.
[ ] Сумма QualityScore weights равна 100.
[ ] Reporting guidelines не представлены как сертификация.
[ ] Юридические выводы не выданы как окончательное заключение.
[ ] Roadmap содержит измеримые exit criteria.
[ ] GO/NO-GO verdicts не противоречат findings.


# 16. КРИТЕРИЙ ЗАВЕРШЕНИЯ

Работа завершена только если:

1. План исполним независимой командой без скрытых допущений.
2. Каждый этап имеет входы, действия, выходы и exit gate.
3. Каждый значимый вывод прослеживается до доказательства.
4. Все математические результаты воспроизводимы.
5. Все неизвестные явно перечислены.
6. Клинические claims ограничены доступными доказательствами.
7. Риски приоритизированы.
8. Roadmap имеет измеримые критерии.
9. Финальные verdicts логически следуют из safety gates.
10. Пройдена финальная самопроверка.

Начни с чтения файла `AUDIT_SPECIFICATION`.
Не изменяй его.
Не начинай с переписывания production-кода.
Сначала создай Audit Charter и детальный план исполнения.
```

---

## Контроль качества мастер-промпта

- Это отдельный оркестратор, а не изменение основной спецификации аудита.
- Определены четыре режима задачи.
- Каждый work package содержит назначение и exit gate.
- State machine имеет начальное и терминальное состояния.
- Веса `QualityScore` дают ровно `100`.
- Формулы определяют используемые переменные.
- Отдельно определены Evidence Ledger и журнал состояния.
- Предусмотрены альтернативные гипотезы.
- Предусмотрены четыре независимых review pass.
- Разделены технические и клинические `GO/NO-GO`.
- Предусмотрено продолжение работы без упрощения обязательных этапов.

