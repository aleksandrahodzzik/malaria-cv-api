# Аудит модели, данных и статистической доказательности

## 1. Model gate

### Текущий результат: FAIL

`MODEL_NAME = trpakov/vit-malaria-classification` обнаружен в коде. Однако:

- публичный профиль автора Hugging Face показывает две другие модели;
- точная malaria-модель публично не обнаружена;
- локальный Hugging Face cache отсутствует;
- модель не закреплена `revision`;
- отсутствуют checksum, model card и лицензия;
- tests подменяют и загрузку, и успешный prediction.

Корректная формулировка вывода: публичная доступность модели
**не подтверждена и с высокой вероятностью отсутствует**. Возможность
приватного, переименованного или удалённого repository остаётся, поэтому
утверждение не превращается в абсолютное доказательство несуществования.

### Непроверяемые свойства

| Гипотеза | Статус |
|---|---|
| Модель обучена на malaria cell classification | UNKNOWN |
| Архитектура является ViT | UNKNOWN для artifact |
| Число logits равно 2 | UNKNOWN |
| `id2label` соответствует классам | UNKNOWN |
| Индекс 0 означает `Parasitized` | UNKNOWN |
| Processor соответствует обучению | UNKNOWN |
| RGB conversion допустим | UNKNOWN |
| Лицензия допускает использование | UNKNOWN |
| Метрики model card достоверны | UNKNOWN |
| Веса идентичны использованным в заявленных экспериментах | UNKNOWN |

Fallback `{0: Parasitized, 1: Uninfected}` опасен: отсутствие metadata
маскируется успешным выполнением с потенциально перевёрнутой семантикой.

## 2. Dataset audit

В самом проекте нет dataset manifest, данных, ссылок на exact training split
или patient identifiers. Поэтому нельзя утверждать, что модель обучалась на
NIH/NLM cell dataset.

Официальный NIH/NLM malaria index содержит несколько разных ресурсов, в том
числе:

- `cell_images.zip`;
- patient-to-cell mapping CSV для parasitized/uninfected;
- `NIH-NLM-ThinBloodSmearsPf`;
- thick-smear и MalariaScreener datasets.

Это не один взаимозаменяемый датасет. Cropped-cell binary classification,
whole thin-smear detection/counting и thick-smear tasks имеют разные unit of
analysis, annotation protocol и intended output.

В литературе для известного cropped-cell набора сообщается 27 558 отдельных
клеточных изображений, полученных от 150 инфицированных и 50 здоровых
пациентов в Бангладеш. Эти числа относятся к исходной работе/набору, а не к
неизвестной Hugging Face модели.

### Главный leakage risk

Если случайно делить клетки на train/test, клетки одного пациента или слайда
могут попасть в обе выборки. Модель способна использовать stain, illumination,
device или patient/slide artifacts, завышая оценку.

Обязательная иерархия split:

```text
patient_id -> slide_id -> field_id -> cell_id
```

Ни один ancestor идентификатора evaluation sample не должен присутствовать
в development partition. Внешний test должен отличаться минимум учреждением,
временем или acquisition pipeline.

## 3. Необходимый data manifest

Для каждого sample:

- immutable sample ID и checksum;
- patient, slide, field и cell IDs;
- site/country/time period;
- acquisition device и magnification;
- smear type, stain и protocol;
- Plasmodium species/stage, если применимо;
- reference-standard label и annotator provenance;
- adjudication и inter-reader agreement;
- demographics, когда допустимо и этично;
- image quality attributes;
- split assignment и причина исключения;
- license/consent/data-use ограничения;
- transformations от raw image до model input.

Отдельно хранить dataset card с missingness, дубликатами, label uncertainty,
class balance, subgroup coverage и known shifts.

## 4. Единица анализа и intended target

Текущий input — одна cropped cell. Поэтому допустимый технический output:

```text
predicted_cell_class ∈ {parasitized_like, uninfected_like, indeterminate}
```

Он не равен:

- диагнозу пациента;
- определению отсутствия малярии;
- species identification;
- parasitemia;
- severity;
- рекомендации лечения.

Чтобы перейти к patient outcome, требуется определить:

```text
cell predictions
  -> quality-controlled field aggregation
  -> slide-level estimate
  -> specimen-level result
  -> patient-level decision
  -> clinical action
```

Для каждого перехода нужны собственные reference standard, uncertainty и
verification.

## 5. Статистический analysis plan

### 5.1. Locked protocol

До просмотра результатов external test зафиксировать:

- primary endpoint;
- unit of analysis;
- positive class;
- threshold/abstention policy;
- reference standard;
- inclusion/exclusion;
- sample size;
- subgroup hierarchy;
- handling missing/invalid inputs;
- confidence interval method;
- multiplicity strategy;
- allowed recalibration;
- failure criteria.

Development, tuning, calibration и final evaluation должны быть отдельными на
patient level.

### 5.2. Confusion matrix

Для заранее заданного threshold:

```text
Sensitivity = TP / (TP + FN)
Specificity = TN / (TN + FP)
PPV         = TP / (TP + FP)
NPV         = TN / (TN + FN)
F1          = 2TP / (2TP + FP + FN)
BalancedAcc = (Sensitivity + Specificity) / 2
```

Публиковать numerator/denominator и 95% CI, не только проценты. Для
кластеризованных клеток использовать patient/slide-level bootstrap или
модель, учитывающую внутрикластерную корреляцию. Наивный cell-level CI будет
слишком узким.

### 5.3. Prevalence transport

PPV и NPV зависят от prevalence `π`:

```text
PPV(π) = Se·π / [Se·π + (1-Sp)·(1-π)]
NPV(π) = Sp·(1-π) / [(1-Se)·π + Sp·(1-π)]
```

Следовательно, balanced public dataset не позволяет напрямую сообщать
реальные predictive values. Требуется prevalence range, соответствующий
intended setting.

Иллюстрация, не метрика проекта: при `Se=0.95`, `Sp=0.90`,
`π=0.01`:

```text
PPV ≈ 0.0876
NPV ≈ 0.9994
```

То есть даже условно сильные Se/Sp могут дать большинство ложных тревог при
низкой prevalence. Пример предназначен только для демонстрации математики.

### 5.4. Discrimination

Обязательно:

- ROC и AUROC с 95% CI;
- precision-recall curve и AUPRC;
- sensitivity при клинически обоснованных specificity points;
- specificity при sensitivity constraints;
- confusion matrices;
- failure examples.

При сравнении моделей на одних случаях применять парное сравнение AUROC,
например DeLong, при выполнении предпосылок. Статистическая значимость не
заменяет клинически значимую разницу.

### 5.5. Calibration

Raw softmax не считается калиброванной вероятностью.

Проверить:

```text
Brier = (1/n) Σ(p_i - y_i)^2
NLL   = -(1/n) Σ[y_i log p_i + (1-y_i) log(1-p_i)]
ECE   = Σ_b (|B_b|/n) · |acc(B_b) - conf(B_b)|
```

Нужны reliability diagram, calibration intercept/slope, bootstrap CI и
оценка по сайтам/subgroups. Temperature scaling обучается только на
calibration partition; final test остаётся locked.

### 5.6. Selective prediction

Модель должна иметь возможность отказаться:

```text
accept(x) = 1, если quality(x) проходит
                 и OOD_score(x) проходит
                 и uncertainty(x) ≤ τ
```

Оценивать:

- coverage = доля принятых samples;
- selective risk = error среди принятых;
- risk-coverage curve;
- false-negative rate среди rejected/accepted;
- причина каждого reject.

Порог нельзя выбирать по final test. Abstention не должен скрывать
систематический провал определённой группы.

### 5.7. Domain shift/OOD

Test matrix:

- другое учреждение/география;
- другой микроскоп/камера/смартфон;
- stain variation;
- illumination, focus, compression;
- different species/stages;
- non-cell crops, leukocytes, platelets, debris;
- artifacts/overlap;
- thick smear и whole field как out-of-scope inputs;
- synthetic corruptions и adversarial perturbations.

Maximum softmax probability может служить baseline OOD score, но не
достаточным safety control. Рассмотреть ensembles/feature-distance или иной
метод только после baseline и с заранее определённой оценкой.

### 5.8. Subgroups и fairness

Минимум оценить site/device/stain/species/parasitemia/quality. Demographic
analysis проводится при наличии законного и научно обоснованного доступа к
данным. Публиковать sample size и uncertainty: маленькие subgroup counts не
должны маскироваться point estimates.

### 5.9. Clinical utility

После доказанной discrimination/calibration оценить decision curve:

```text
NetBenefit(t) = TP/n - FP/n · t/(1-t)
```

Сравнивать с `treat-all`, `treat-none` и текущим workflow. Threshold `t`
должен иметь клинический смысл, а не выбираться для красивой accuracy.

## 6. Sample size

Конкретный `n` нельзя честно назначить без:

- target Se/Sp и минимально допустимых границ;
- желаемой ширины CI;
- prevalence;
- unit of analysis;
- cluster sizes и ICC;
- subgroup objectives;
- допустимого числа failures.

Первичный расчёт для sensitivity при числе positive cases:

```text
n_pos ≈ z_(1-α/2)^2 · Se·(1-Se) / d^2
```

и аналогично для specificity на negative cases. Затем корректировать на
design effect:

```text
DE = 1 + (m - 1)·ICC
n_clustered ≈ n_iid · DE
```

Для надёжной calibration нужны event counts и simulation-based design.
Окончательный protocol должен быть проверен биостатистиком.

## 7. Experiment registry

Каждый эксперимент должен хранить:

- code commit;
- environment lock;
- container digest;
- model artifact checksum/revision;
- dataset manifest/split checksum;
- random seeds и determinism settings;
- hardware;
- metrics с CI;
- calibration artifact;
- failed/aborted runs;
- approval status.

## 8. Acceptance gates

### Gate M1 — provenance

- model card и intended use;
- immutable revision/SHA256;
- лицензия;
- architecture/config;
- label and preprocessing contracts.

### Gate M2 — data

- patient/slide lineage;
- no leakage;
- license/consent;
- external site;
- quality and subgroup manifest.

### Gate M3 — performance

- locked protocol;
- Se/Sp/AUROC/AUPRC with CI;
- error analysis;
- subgroup results;
- comparator.

### Gate M4 — uncertainty/safety

- calibration;
- abstention;
- OOD/quality;
- risk-coverage;
- explicit failure response.

### Gate M5 — clinical utility

- approved intended use;
- workflow and human factors;
- decision-curve or equivalent benefit-risk evidence;
- prospective evaluation before clinical claims.

На дату аудита ни один gate M1–M5 не пройден.
