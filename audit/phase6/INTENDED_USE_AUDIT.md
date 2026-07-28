# Фаза 6 — соответствие модели задаче

Дата: 2026-07-28
Режим: evidence-first, отсутствие approved model сохранено как STOP-SHIP.

## Итог

Фактически реализованы только:

- **A — классификация заранее вырезанной отдельной клетки**: software path
  реализован, но модель и performance не валидированы;
- **F — исследовательская демонстрация**: реализована и явно обозначена.

Задачи B–E не реализованы и не должны выводиться из cell-level ответа.

| Code | Task | Claimed now | Implemented | Validated | Verdict |
|---|---|---:|---:|---:|---|
| A | Pre-cropped single-cell classification | yes | software only | no | PARTIALLY_SUPPORTED |
| B | Whole-field detection | no | no | no | UNSUPPORTED |
| C | Parasitemia estimation | no | no | no | UNSUPPORTED |
| D | Patient diagnosis | explicitly excluded | no | no | UNSUPPORTED |
| E | Screening/triage | explicitly excluded | no | no | UNSUPPORTED |
| F | Research demonstration | yes | yes | n/a as diagnostic claim | SUPPORTED |

## Evidence

- `POST /api/v1/analyze` принимает один файл и возвращает один class vector.
- Request не содержит patient, slide, field-of-view или cell lineage.
- Processor получает один RGB image.
- Нет detector/segmenter, cell counter или slide aggregator.
- `PredictionResponse.analysis_level = cell`.
- `patient_diagnosis_supported = false`.
- `parasitemia_supported = false`.
- `/api/v1/methodology` публикует восемь звеньев pipeline.
- UI требует подтверждения pre-cropped single-cell input.
- Approved model artifact и locked validation cohort отсутствуют.

## Critical interpretation

Технически корректно декодированный cell crop не является:

1. доказательством качества микроскопии;
2. репрезентативной выборкой клеток мазка;
3. оценкой parasite density;
4. patient-level reference result;
5. основанием для treatment.

WHO microscopy workflow рассматривает examination и counting thick/thin blood
films как отдельные процедуры. Текущий single-cell endpoint их не реализует:

- https://www.who.int/publications/i/item/HTM-GMP-MM-SOP-09
- https://www.who.int/docs/default-source/wpro---documents/toolkit/malaria-sop/gmp-sop-08-revised.pdf

## Domain applicability

Для текущей неизвестной модели training domain не документирован. Все оси,
кроме software input unit, имеют статус `UNKNOWN`. Численный
DomainApplicabilityScore не вычисляется: подстановка нулей создала бы ложную
видимость измеренного mismatch, а подстановка единиц — ложную уверенность.

Safety override срабатывает:

```text
patient-level aggregation = MISSING
patient-level reference standard = MISSING
clinical workflow validation = MISSING

=> patient/clinical use = NO-GO
```

## Решение

- Research UI/API без клинических claims: CONDITIONAL GO.
- Real-model cell inference: NO-GO до approved artifact и cell-level external
  validation.
- Slide/patient/clinical use: NO-GO.
