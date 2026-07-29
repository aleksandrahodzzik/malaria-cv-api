# Фаза 9 — агрегация от клетки к пациенту

Дата среза: 2026-07-28. Режим: READ-ONLY по отношению к клиническим данным.

## Вердикт

Текущий сервис реализует только классификацию заранее вырезанной клетки.
Slide-level и patient-level агрегация, детектор клеток, оценка паразитемии,
контроль полноты поля и клиническая интерпретация отсутствуют. Поэтому результат
API нельзя преобразовывать в диагноз пациента. Patient-level deployment:
**NO-GO**.

## Реализованная цепочка

| Звено | Статус | Доказательство |
|---|---|---|
| Получение cropped-cell image | VERIFIED | `POST /api/v1/analyze` |
| Транспортная и декодерная валидация | VERIFIED | middleware, Pillow-проверки и API-тесты |
| Биологический image quality control | ABSENT | нет фокуса, окраски, масштаба, типа клетки |
| Cell detection/segmentation | ABSENT | API принимает готовый crop |
| Cell classification | BLOCKED | код есть, утверждённая модель отсутствует |
| Slide aggregation | ABSENT | нет slide ID и агрегатора |
| Patient interpretation | ABSENT | нет patient ID, reference standard и валидированного порога |
| Human review | PARTIAL | UI требует подтверждения исследовательского назначения |
| Clinical action | OUT OF SCOPE | явно запрещена документацией |

## Математическая позиция

Для `m` исследованных клеток и `k` положительных классификаций наблюдаемая
доля `q = k/m` является *apparent positive rate*, но не доказанной
паразитемией. Если известны валидированные клеточные `Se` и `Sp`, поправка
Rogan–Gladen имеет вид:

`p_hat = (q + Sp - 1) / (Se + Sp - 1)`.

Она идентифицируема только при `Se + Sp > 1`, чувствительна к domain shift и
не устраняет ошибки детектора, sampling bias или внутрислайдовую корреляцию.
Реализация в `src/validation/aggregation.py` возвращает также флаг clipping и
предназначена для планирования, а не для online-диагноза.

Формула `1 - product(1 - p_i)` запрещена как patient probability: условная
независимость клеток не доказана, а даже при нулевой истинной
распространённости вероятность хотя бы одного false positive равна
`1 - Sp^m` и быстро приближается к единице.

## Допустимый путь развития

1. Зафиксировать intended use и единицу решения.
2. Ввести patient/slide/field lineage без персональных идентификаторов в API.
3. Валидировать детектор и классификатор раздельно и end-to-end.
4. Обучить hierarchical/beta-binomial агрегатор только на development cohort.
5. Выбрать minimum cell count и patient threshold по clinical loss.
6. Проверить на независимом patient-level test cohort.
7. Добавить обязательный `requires_review` и безопасный отказ.

## Finding

Finding ID: AGG-001

Classification: VERIFIED

Severity: Critical

Confidence: 1.00

Evidence: отсутствуют slide/patient identifiers, aggregation pipeline и
patient-level validation.

Reproduction: просмотреть route/schema и цепочку inference.

Impact: одиночный клеточный прогноз может быть ошибочно принят за диагноз.

Root cause: продуктовая граница пока ограничена cropped-cell demo.

Recommendation: не добавлять patient result до завершения patient-level
протокола.

Acceptance criteria: независимая patient-level validation, locked protocol,
reference standard, CI и безопасный response contract.
