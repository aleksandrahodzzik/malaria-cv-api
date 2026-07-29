# Фаза 17 — regulatory applicability

Дата проверки: 2026-07-28. Это исследовательский gap analysis, не юридическое
заключение.

## Intended-purpose dependency

Если software предназначено производителем для исследования человеческого
образца с целью предоставления информации о pathological process, оно может
попасть в контур IVDR, включая software, в зависимости от точного intended
purpose. Если остаётся demonstrator/research tool без medical intended purpose,
классификация может быть иной. Marketing/UI/API claims являются частью
доказательств intended purpose.

## Applicability matrix

| Framework | Potential applicability | Current evidence | Decision owner |
|---|---|---|---|
| EU IVDR 2017/746 | Высокая при IVD diagnostic intended purpose | Human blood image + malaria classification, но research-only claim | Regulatory counsel/notified-body strategy |
| EU MDR 2017/745 | Требует boundary analysis; IVDR может быть более специфичен | Software only | Regulatory counsel |
| EU AI Act 2024/1689 | Зависит от prohibited/high-risk/product-safety role and dates | AI model/API | EU legal/regulatory assessment |
| GDPR | Вероятно при identifiable/pseudonymous health data | App не хранит images, deployment unknown | Controller/DPO |
| FDA SaMD | При US medical intended use | Нет US claim/submission | FDA regulatory specialist |
| IMDRF SaMD | Полезная categorization/risk framework | Clinical significance undefined | Product/regulatory team |

## No-compliance rule

Docker, pytest, model card или reporting guideline сами по себе не доказывают
conformity, clearance, certification или clinical performance.
