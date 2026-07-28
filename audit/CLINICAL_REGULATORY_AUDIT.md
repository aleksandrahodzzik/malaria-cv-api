# Клинико-регуляторный аудит

## 1. Важное ограничение

Этот документ — gap analysis, а не юридическая консультация, regulatory
classification или разрешение медицинского применения. Конкретная
классификация зависит от утверждённого intended purpose, рынка, claims,
workflow и ответственности производителя.

## 2. Intended use gap

В репозитории нет контролируемого документа, который однозначно определяет:

- заболевание и клинический вопрос;
- intended user;
- target population;
- specimen и acquisition protocol;
- input quality requirements;
- роль результата;
- setting и comparator;
- противопоказания/исключения;
- consequence ложноположительного/ложноотрицательного результата;
- human oversight;
- region/jurisdiction.

README и OpenAPI используют `MedTech`, `clinical prediction` и `diagnosis`.
Это расширяет воспринимаемое назначение гораздо дальше, чем доказанный
cell-level classifier.

## 3. Cell-level versus clinical diagnosis

Из одной cropped cell нельзя сделать отрицательный диагноз пациента:
неинфицированная клетка может принадлежать инфицированному пациенту. Даже
класс `Parasitized` на отдельном crop требует подтверждения reference
standard и понимания false positives.

Система не выполняет:

- проверку репрезентативности мазка;
- выбор полей зрения;
- обнаружение/сегментацию всех клеток;
- подсчёт инфицированных клеток;
- parasitemia;
- species/stage identification;
- specimen/patient aggregation;
- clinical history integration;
- quality control;
- review workflow.

Поэтому термин `diagnosis` является некорректным до появления доказанной
многоуровневой системы.

## 4. Benefit-risk chain

```text
Неверный cell output
  -> неверная slide interpretation
  -> неверное patient decision
  -> задержка/ненужное лечение
  -> клинический вред
```

Критический риск — false negative в intended workflow. Но false positive
тоже способен привести к ненужному лечению, пропуску альтернативного
диагноза и resource burden. Приоритет ошибок должен исходить из clinical use,
а не из generic accuracy.

## 5. Scientific reporting и risk of bias

### CLAIM 2024

Применим как checklist прозрачности medical imaging AI: acquisition protocol,
patient/image counts, level of split, reference standard, external testing,
uncertainty, error analysis, intended use и availability.

Текущий статус: большинство ML-study items `NO/UNKNOWN`, поскольку study
report отсутствует. CLAIM не является scoring certification.

### TRIPOD+AI

Полезен, если система формулируется как diagnostic prediction model. Требует
прозрачного описания данных, methods, evaluation, fairness, open science и
limitations.

Текущий статус: неприменим для заявления соответствия без model study.
Документ прямо является reporting guideline, а не quality appraisal.

### PROBAST+AI

Использовать для formal risk-of-bias/applicability review после появления
study package. Сейчас domains о participants/data, predictors/input, outcome,
analysis и applicability нельзя оценить; общий риск следует считать
`UNCLEAR/HIGH`, а не low.

### STARD-AI/DECIDE-AI/CONSORT-AI/SPIRIT-AI

- STARD-AI — диагностическая accuracy study.
- DECIDE-AI — early-stage clinical evaluation human-AI interaction.
- SPIRIT-AI — protocol интервенционного clinical trial.
- CONSORT-AI — отчёт такого trial.

Нельзя отмечать compliance только потому, что checklist упомянут. Текущий
проект ещё не достиг фаз, для которых есть необходимые исследования.

### FUTURE-AI

Принципы trustworthy/deployable healthcare AI полезны для lifecycle plan,
но сами по себе не доказывают effectiveness.

## 6. GMLP gap

В сопоставлении с lifecycle-oriented GMLP отсутствуют либо не доказаны:

- multidisciplinary governance;
- representative intended-use data;
- независимость train/test;
- clinically relevant test conditions;
- human-AI team performance;
- clear user information;
- deployed monitoring;
- retraining/change control;
- total product lifecycle risk management.

## 7. Quality management artifacts

Для медицинского пути потребуются как минимум:

- design and development plan;
- controlled intended use/user needs;
- software requirements and architecture;
- bidirectional traceability;
- risk management file;
- data/model lifecycle procedures;
- configuration/change control;
- verification and validation plans/reports;
- cybersecurity file;
- usability/human factors engineering;
- clinical evaluation/performance evidence;
- supplier controls;
- complaint/vigilance/CAPA;
- post-market/performance monitoring;
- release records.

Применимость конкретных ISO/IEC и regulatory требований должна определяться
по юрисдикции и классификации, а не утверждаться автоматически.

## 8. Privacy и ethics

Microscopy images и filenames могут быть связаны с patient/specimen
identifiers. Не определены:

- lawful basis/consent;
- data minimization;
- de-identification;
- retention/deletion;
- access control;
- data residency;
- audit logging;
- secondary use;
- breach response.

До обработки реальных данных нужен privacy impact assessment и data-flow
inventory. Передача изображений внешнему model provider не выполняется
текущим inference path, но runtime скачивает model assets; egress boundary
всё равно должен быть описан.

## 9. Human factors

Нужны исследования того, как оператор:

- понимает `confidence`;
- различает cell class и patient diagnosis;
- реагирует на `indeterminate`;
- исправляет плохой crop;
- обнаруживает ошибку автоматизации;
- не попадает в automation bias;
- документирует override.

Primary endpoint human-AI evaluation может включать diagnostic performance,
time-to-result, override quality и critical error rate, но должен быть
предопределён.

## 10. Regulatory gates

### R0 — research-only boundary

- убрать clinical claims;
- явная маркировка non-diagnostic/research-only;
- запрет реальных clinical decisions;
- data governance.

### R1 — intended purpose

- рынок/юрисдикция;
- пользователь, population, specimen;
- клиническая роль;
- outputs/limitations;
- risk classification hypothesis с counsel review.

### R2 — quality/risk system

- controlled lifecycle;
- risk controls and traceability;
- cybersecurity and supplier controls.

### R3 — analytical/technical performance

- locked artifact;
- software verification;
- robustness/reproducibility;
- dataset and statistical evidence.

### R4 — clinical performance

- external retrospective evidence;
- human factors;
- prospective/clinical evaluation, если требуется;
- benefit-risk.

### R5 — deployment lifecycle

- monitoring;
- incident/vigilance;
- change/retraining plan;
- rollback;
- post-market evidence.

Текущий статус: R0 не пройден из-за языка claims; R1–R5 не пройдены.

## 11. Безопасный interim positioning

До появления evidence допустимое описание:

> Экспериментальный программный прототип API для исследования классификации
> заранее выделенных изображений отдельных клеток. Не предназначен для
> диагностики, исключения малярии, выбора лечения или оценки пациента.

Даже это описание требует доступной и проверенной модели для фактического
демо.

## 12. Clinical acceptance criteria

Клинический gate нельзя открыть, пока:

- утверждён intended use;
- модель и данные прослеживаемы;
- patient-level external testing выполнено;
- sensitivity/specificity и CI удовлетворяют заранее заданным требованиям;
- quality/OOD/abstention controls доказаны;
- клинический workflow и human oversight валидированы;
- benefit-risk положителен;
- regulatory/QMS стратегия утверждена компетентными специалистами;
- post-deployment monitoring и incident response готовы.
