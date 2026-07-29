# Решение по продуктовой стратегии

## Рекомендация

Сейчас выбрать **A: research cell-classification API** с жёсткой
research-only границей. Параллельно собирать evidence, позволяющий принять или
отклонить B. Не начинать C/D как обязательную последовательность.

## Почему

- A соответствует фактически реализованному input contract.
- Он позволяет закрыть provenance, leakage, calibration и reproducibility с
  меньшей стоимостью.
- B может иметь ограниченную laboratory value, но требует controlled sampling,
  QC, patient validation и human factors.
- C потенциально решает более полезную задачу, но добавляет detector/counting
  errors и дорогую slide annotation.
- D имеет максимальный regulatory/patient-safety burden и сейчас не имеет
  supporting evidence.

## Kill gates

- A прекращается/переформулируется, если нельзя получить лицензированный
  artifact или leakage-safe dataset.
- B не начинается без external patient-level cell evidence и review capacity.
- C прекращается, если component pipeline не улучшает counting/workflow outcome
  относительно ручного baseline.
- D не начинается без prospective silent evaluation и controlled QMS.
