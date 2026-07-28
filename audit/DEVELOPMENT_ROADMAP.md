# Roadmap развития

## Принцип приоритизации

Использована модель:

```text
PriorityScore =
  (PatientRiskReduction · EvidenceGain · DependencyUnlock · Confidence)
  / (Effort · TimeToFeedback)
```

Точные экономические коэффициенты неизвестны, поэтому план использует
качественные классы `P0–P3`. P0 снимает stop-ship или предотвращает
некорректный clinical claim; P1 открывает доказательную валидацию; P2
укрепляет production; P3 оптимизирует после подтверждения value.

## Сейчас: 0–7 дней

### P0. Зафиксировать границы продукта

1. Удалить из публичного позиционирования `production-ready`, `clinical
   prediction` и `diagnosis` до появления evidence.
2. Утвердить interim `research-only` disclaimer.
3. Определить, является ли цель:
   - учебным API;
   - cell-level research tool;
   - slide-level decision support;
   - clinical device.

Definition of Done: один контролируемый intended-use документ согласован
Product + ML + Clinical + Regulatory.

### P0. Восстановить model artifact

1. Установить происхождение указанного model ID.
2. Если artifact утрачен — не заменять его молча pneumonia/другой моделью.
3. Выбрать malaria-модель только после проверки:
   - training/evaluation data;
   - architecture/config;
   - labels;
   - preprocessing;
   - license;
   - metrics и leakage risk.
4. Зафиксировать commit revision и SHA256.

Definition of Done: model manifest, model card, license record и clean-cache
smoke test.

### P0. Закрыть опасные API claims

Планируемое изменение после отдельного разрешения:

- `diagnosis` -> `predicted_cell_class`;
- добавить `indeterminate`;
- безопасные error codes;
- документировать limitations.

Definition of Done: OpenAPI и README не допускают patient-level
интерпретации.

## 7–30 дней

### P1. Reproducible release

- lock transitive dependencies и hashes;
- pin base image digest и GitHub Actions SHA;
- bake/attach approved model artifact;
- Docker build/run/readiness test;
- SBOM, license, CVE, secrets, signature, provenance.

### P1. Test pyramid

- сохранить быстрые unit tests;
- добавить processor/model contract tests;
- golden positive/negative/indeterminate cases;
- corrupt/adversarial image corpus;
- OpenAPI/error contract;
- Linux container integration;
- coverage floor, прежде всего для inference.

### P1. Security baseline

- identity, quota, rate limit;
- request/body/header/time limits;
- bounded inference concurrency;
- safe errors;
- validated request IDs;
- structured privacy-safe logs.

### P1. Dataset registry

- patient/slide/cell hierarchy;
- checksums, licenses, annotations;
- patient-level partitions;
- duplicate/leakage analysis;
- external-site acquisition plan.

## 31–60 дней

### P1. Baseline ML study

1. Зарегистрировать protocol.
2. Выбрать простые baselines и candidate model.
3. Оценить locked internal test:
   - confusion matrix;
   - Se/Sp;
   - AUROC/AUPRC;
   - CI с cluster bootstrap;
   - subgroup/error analysis.
4. Не оптимизировать на final test.

### P1. Calibration и abstention

- separate calibration partition;
- temperature scaling baseline;
- Brier/NLL/ECE/reliability;
- image-quality gate;
- OOD baseline;
- risk-coverage evaluation.

### P2. Capacity engineering

- one-worker memory/latency benchmark;
- concurrency topology;
- cold/warm/spike/soak tests;
- SLO/error budget;
- resource limits и autoscaling hypothesis.

## 61–90 дней

### P1. External testing

- новый site/device/time period;
- patient-level locked evaluation;
- pre-specified subgroup matrix;
- compare against current workflow/reference standard;
- complete CLAIM/TRIPOD+AI report;
- independent statistical review.

### P2. Operational readiness

- OpenTelemetry/metrics;
- runbooks;
- alert and rollback tests;
- model/data drift plan;
- release approval workflow;
- backup/cache/provider outage exercises.

### P2. Human factors prototype

- результаты и uncertainty понятны intended users;
- test automation bias;
- review/override/indeterminate workflow;
- collect usability hazards.

## 91–180 дней

### Если цель остаётся research-only

- публичный reproducible benchmark;
- model/data cards;
- external replication;
- прозрачные limitations;
- versioned nonclinical API.

### Если цель — clinical decision support

- QMS и risk management file;
- formal regulatory strategy по выбранному рынку;
- clinical evaluation plan;
- prospective workflow study;
- human-AI performance;
- cybersecurity and privacy validation;
- post-market/change-control plan.

Clinical claims не выпускаются по календарю: только после evidence gates.

## Backlog после доказательства ценности

- slide-level detection/segmentation;
- parasitemia estimation;
- species/stage support;
- active learning с controlled annotation;
- multi-site federated/central learning;
- ensembles;
- hardware acceleration;
- batch inference/UI.

Эти функции не должны опережать доказательство корректного cell-level
artifact и intended use.

## Эксперименты с максимальной информационной ценностью

| Experiment | Что решает | Стоимость | Приоритет |
|---|---|---:|---|
| Clean-cache real model load | Существует ли продуктовый ML path | Низкая | P0 |
| Golden label/preprocessor contract | Инверсия classes/preprocessing | Низкая | P0 |
| Patient leakage audit | Реальны ли метрики | Средняя | P0 |
| External-site small pilot | Масштаб domain shift | Средняя | P1 |
| Calibration/risk-coverage | Безопасность confidence | Средняя | P1 |
| One-worker capacity profile | Deployment topology | Низкая | P1 |
| Human-AI formative test | Ошибки интерпретации | Средняя | P1 |

## Release checklist

- [ ] Intended use утверждён.
- [ ] Clinical claims соответствуют evidence.
- [ ] Model revision/checksum/license подтверждены.
- [ ] Data lineage и patient split подтверждены.
- [ ] Locked statistical report утверждён.
- [ ] Calibration/OOD/abstention gates пройдены.
- [ ] Security/privacy gates пройдены.
- [ ] Container reproducible, scanned, signed.
- [ ] Load/soak/SLO пройдены.
- [ ] Monitoring, incident и rollback готовы.
- [ ] Независимый reviewer подписал GO.

Пока любой P0 checkbox открыт, release остаётся NO-GO.
