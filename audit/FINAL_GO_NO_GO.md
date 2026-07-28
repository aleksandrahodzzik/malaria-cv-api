# Финальный GO / NO-GO

Дата: 2026-07-27  
Версия: 1.0.0

## 1. Решение по сценариям

| Сценарий | Решение | Условия |
|---|---|---|
| Просмотр исходников и unit-test scaffold | GO | Только как инженерный пример |
| Локальное mocked API demo | CONDITIONAL GO | Явно сообщать, что prediction синтетический |
| Локальное demo с реальной malaria-моделью | NO-GO | Artifact не доступен/не доказан |
| Публичный non-clinical API | NO-GO | Нет модели, security/capacity gates |
| Research benchmark | NO-GO | Нет provenance, данных и statistical report |
| Retrospective clinical research | NO-GO | Нет protocol/ethics/data/reference standard |
| Prospective clinical evaluation | NO-GO | Не пройдены предыдущие gates |
| Clinical decision support | NO-GO | Нет clinical performance/QMS/regulatory path |
| Autonomous diagnosis | NO-GO | Недопустимо при текущем evidence |

## 2. Гипотезы H1–H12

| ID | Гипотеза | Вердикт |
|---|---|---|
| H1 | Идентификатор модели существует и публично доступен | FAIL с высокой уверенностью; альтернативно private/renamed/deleted |
| H2 | Модель обучена для malaria classification | UNKNOWN |
| H3 | `id2label` соответствует logits | UNKNOWN / STOP-SHIP |
| H4 | Preprocessing соответствует обучению | UNKNOWN / STOP-SHIP |
| H5 | Модель допускает входы API | UNKNOWN |
| H6 | Тесты скрывают невозможность загрузить модель | VERIFIED: load и success path mocked |
| H7 | Confidence — калиброванная вероятность | FAIL: evidence отсутствует |
| H8 | Результат клетки применим как диагноз пациента | FAIL |
| H9 | Лицензия разрешает использование | UNKNOWN |
| H10 | Сервис выдерживает параллельную нагрузку | UNKNOWN |
| H11 | Production-ready подтверждено | FAIL |
| H12 | `CONFIDENCE_THRESHOLD` участвует в решении | FAIL |

## 3. Решающее доказательство

Зелёный HTTP-тест строит `PredictionResponse` вручную. Он не вызывает
настоящий processor/model. Поэтому:

```text
9 passed
≠ model available
≠ correct labels
≠ valid preprocessing
≠ measured diagnostic performance
≠ clinical safety
```

## 4. Minimum path to conditional nonclinical GO

1. Утвердить research-only intended use.
2. Предоставить лицензионно допустимый immutable model artifact.
3. Проверить processor, logits и labels golden tests.
4. Убрать `diagnosis/clinical` claims.
5. Собрать и запустить Linux container.
6. Ввести auth/rate/body/time/concurrency controls.
7. Выполнить real-model smoke, security scan и basic load test.
8. Публиковать только model-level limitations, без patient claims.

Это открывает лишь nonclinical research API, но не clinical use.

## 5. Minimum path to clinical evaluation

Дополнительно:

- patient/slide-level data lineage;
- locked external evaluation;
- Se/Sp/AUROC/AUPRC/calibration с CI;
- subgroup/domain-shift analysis;
- quality/OOD/abstention;
- intended workflow и human factors;
- QMS/risk/cyber/privacy;
- regulatory strategy;
- prospective protocol и oversight.

## 6. Независимая проверка против чрезмерных выводов

- Точный HTTP 404 модели не был получен через локальную сеть: она
  заблокирована. Вывод основан на публичном профиле и exact search, поэтому
  сформулирован вероятностно.
- Docker не тестировался из-за отсутствия Docker. Его проблемы отмечены как
  static findings, не как runtime failures.
- CPU/RAM hardware не определены из-за ограничений системного запроса.
- Уязвимости зависимостей не выдуманы: vulnerability scanner не был
  установлен, результат отмечен `NOT EXECUTED`.
- Sensitivity, specificity и accuracy модели не указаны, потому что
  prediction-level data отсутствуют.
- Регуляторный класс не назначен без intended purpose и jurisdiction review.

## 7. Финальная формулировка

`malaria-cv-api` имеет хороший базовый FastAPI skeleton и несколько
правильных защитных решений, однако критическая модельная цепочка не
воспроизводится, а медицинская доказательная база отсутствует. До закрытия
P0 gates проект должен позиционироваться только как незавершённый
экспериментальный прототип. Финальное решение на текущую дату:
**NO-GO / STOP-SHIP для любого релиза, который обещает настоящую malaria
classification или клиническое применение**.
