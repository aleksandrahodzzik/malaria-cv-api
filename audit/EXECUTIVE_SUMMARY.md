# Executive summary

## 1. Решение

**Итоговая оценка готовности: 28/100.**

**Решение: NO-GO.**

Проект можно рассматривать как исходную заготовку backend-сервиса и учебный
контур тестирования HTTP-контракта. Его нельзя честно обозначать как
`production-ready`, `clinical prediction`, диагностический инструмент или
валидированную MedTech-систему.

Оценка 28/100 является экспертной моделью зрелости, а не статистической
оценкой точности. Критические gates имеют приоритет над суммарным баллом.

| Область | Вес | Оценка 0–5 | Вклад |
|---|---:|---:|---:|
| Клиническая и модельная доказательность | 25 | 0.0 | 0.0 |
| Данные и data governance | 15 | 0.5 | 1.5 |
| Корректность ПО и API | 12 | 3.5 | 8.4 |
| Security и privacy | 12 | 1.5 | 3.6 |
| Надёжность и производительность | 10 | 1.5 | 3.0 |
| MLOps и воспроизводимость | 10 | 2.0 | 4.0 |
| Тестирование и CI | 8 | 3.0 | 4.8 |
| Документация и regulatory readiness | 8 | 1.6 | 2.6 |
| **Итого** | **100** |  | **27.9 ≈ 28** |

## 2. Критические gates

| Gate | Статус | Основание |
|---|---|---|
| Repository gate | PARTIAL | Исходники доступны; `.git` не является рабочим репозиторием |
| Environment gate | PASS | Python-окружение запускает lint, type check и unit tests |
| Model gate | **FAIL** | Модель не найдена публично/локально; реальная загрузка не доказана |
| Data provenance gate | **FAIL** | Training/evaluation manifest, split и лицензия модели отсутствуют |
| Statistical evidence gate | **FAIL** | Нет prediction-level данных и независимой оценки |
| Clinical safety gate | **FAIL** | Нет intended use, clinical performance и human factors evidence |
| Security gate | FAIL | Нет auth/rate limit, supply-chain pinning и security verification |
| Deployment gate | NOT EXECUTED | Docker недоступен в текущем окружении |

Любой из четырёх выделенных FAIL достаточен для NO-GO независимо от качества
FastAPI-кода.

## 3. Что реально подтверждено

- `VERIFIED`: `ruff check src tests` — успешно.
- `VERIFIED`: `ruff format --check src tests` — 14 файлов отформатированы.
- `VERIFIED`: `mypy src` — ошибок не обнаружено в 12 исходных файлах.
- `VERIFIED`: `pytest --cov=src ...` — 9 тестов успешно, общее покрытие 74%.
- `VERIFIED`: `python -m compileall src tests` — успешно.
- `VERIFIED`: `pip check` — нарушенных зависимостей не обнаружено.
- `OBSERVED`: есть `/health`, `/ready`, `/analyze`, а также повторная
  регистрация маршрутов под `/api/v1`.
- `OBSERVED`: изображение проверяется Pillow, ограничивается размер файла и
  площадь декодированного изображения.
- `OBSERVED`: PyTorch-инференс переносится в `asyncio.to_thread()`.
- `OBSERVED`: контейнер настроен на непривилегированного пользователя UID
  10001.

Эти факты подтверждают наличие качественных элементов инженерного каркаса,
но не подтверждают доступность модели, точность, безопасность или
клиническую полезность.

## 4. Stop-ship findings

### Finding ID: F-001

Classification: `INFERRED`  
Severity: `CRITICAL / STOP-SHIP`  
Confidence: `HIGH`

Evidence:

- `src/core/config.py` задаёт
  `trpakov/vit-malaria-classification`.
- В публичном профиле `trpakov` на Hugging Face на дату аудита перечислены
  только `vit-face-expression` и `vit-pneumonia`.
- Точный поиск не нашёл публичную карточку указанной malaria-модели.
- Локальный каталог Hugging Face cache отсутствует.
- `tests/test_api.py` подменяет `load_model` и весь успешный инференс.

Reproduction:

1. Проверить `MODEL_NAME`.
2. Открыть `https://huggingface.co/trpakov/models`.
3. Проверить локальный `%USERPROFILE%\.cache\huggingface\hub`.
4. Сопоставить фикстуры `client` и `mock_classifier_service`.

Impact: сервис на чистой машине, вероятнее всего, стартует без готовой модели;
`/ready` останется 503, а `/analyze` будет недоступен через dependency.

Root cause: внешний model artifact не закреплён и не поставляется с продуктом.

Recommendation: выбрать проверенный model artifact, зафиксировать immutable
revision/commit SHA, checksum, лицензию, model card, label contract и
processor contract; добавить отдельный real-model smoke test.

Acceptance criteria:

- загрузка проходит из пустого cache;
- повторный offline-запуск проходит из утверждённого локального artifact;
- SHA256 и Hugging Face revision совпадают с manifest;
- тестовый пример даёт ожидаемое соответствие индекса и класса;
- SBOM и license review включают веса и tokenizer/processor assets.

### Finding ID: F-002

Classification: `OBSERVED`  
Severity: `CRITICAL / STOP-SHIP`  
Confidence: `HIGH`

Evidence: отсутствуют model card, training manifest, dataset manifest,
patient-level split, внешний test set, confusion matrix, calibration report и
prediction-level результаты.

Impact: невозможно вычислить sensitivity, specificity, PPV, NPV, AUROC,
AUPRC, confidence intervals, calibration и subgroup performance.

Root cause: в репозиторий включён serving-код без доказательного ML-пакета.

Recommendation: создать versioned ML evidence package и заблокировать release
без прохождения model/data/statistical gates.

Acceptance criteria: требования описаны в
`MODEL_DATA_STATISTICAL_AUDIT.md`.

### Finding ID: F-003

Classification: `OBSERVED + INFERRED`  
Severity: `CRITICAL / STOP-SHIP`  
Confidence: `HIGH`

Evidence: API принимает изображение отдельной клетки и возвращает поле
`diagnosis`; нет агрегации по мазку/пациенту, подсчёта паразитемии,
reference-standard protocol или clinical workflow.

Impact: результат cell-level classification может быть ошибочно
интерпретирован как диагноз пациента. Это создаёт риск ложного отрицательного
или ложного положительного клинического решения.

Root cause: несогласованность уровня предсказания, intended use и языка API.

Recommendation: до клинической валидации переименовать результат в
`predicted_cell_class`, добавить явное `research_use_only`, исключить
`diagnosis/clinical prediction` из документации; отдельно проектировать
slide/patient-level систему.

Acceptance criteria: утверждён intended use, user population, specimen
workflow, reference standard, aggregation protocol, risk controls и
prospective evaluation plan.

### Finding ID: F-004

Classification: `OBSERVED`  
Severity: `HIGH`  
Confidence: `HIGH`

Evidence: softmax-вероятность округляется и публикуется как `confidence`;
`CONFIDENCE_THRESHOLD` объявлен, но не участвует в решении; нет calibration и
abstention.

Impact: числу может быть приписан смысл вероятности корректности, которого оно
не имеет; система всегда выбирает класс даже при OOD или низком качестве.

Recommendation: оценить calibration на независимом наборе, использовать
temperature scaling или другой заранее заданный метод, ввести класс
`indeterminate/reject` и quality/OOD gates.

Acceptance criteria: ECE/Brier/NLL с bootstrap CI, reliability diagram,
risk-coverage curve и заранее утверждённые пороги на locked test set.

## 5. Главные технические риски

1. Ошибки внутреннего инференса возвращаются клиенту в `detail`, раскрывая
   внутренние сообщения исключений.
2. Нет аутентификации, квот, rate limiting и глобального request-body limit.
3. Доверенный входной `X-Request-ID` без формата и длины попадает в логи и
   ответ.
4. Два Gunicorn worker независимо загрузят модель, что умножает RAM и
   вызывает конкурентное скачивание весов при старте.
5. Docker base image, Python dependencies, GitHub Actions и model revision не
   закреплены неизменяемыми digest/SHA.
6. Нет Docker build test, container scan, dependency audit, secret scan,
   SBOM, provenance/attestation и coverage threshold.
7. Диапазоны версий без lock/hashes делают сборку невоспроизводимой.
8. Текущая локальная среда использует Python 3.12, CI/Docker — 3.11; матрица
   совместимости отсутствует.

## 6. Ответы на основные вопросы

- Запуск с нуля: **не доказан**, поскольку реальная модель не загружается в
  тестах, Docker не был доступен.
- Воспроизводимость: **частичная**; кодовые проверки воспроизводятся, набор
  зависимостей не зафиксирован lock/hash.
- Доступность модели: **не подтверждена; публичные признаки указывают на
  отсутствие**.
- Корректность классов и preprocessing: **UNKNOWN**.
- Ошибочные файлы: базовые случаи покрыты; adversarial/decompression/parser
  cases не покрыты.
- Sensitivity/specificity: **UNKNOWN**, вычислять их без данных запрещено.
- Независимое внешнее тестирование: **не обнаружено**.
- Data leakage/patient split: **UNKNOWN**.
- Calibration/selective prediction: **отсутствуют**.
- Domain shift и плохое качество: **не контролируются доказанным способом**.
- Перегрузка: **не тестировалась**.
- Clinical workflow: **не определён и не валидирован**.
- Production-ready: **нет**.

## 7. Следующее рациональное решение

До расширения API остановить feature development и выполнить Gate 0:

1. выбрать и юридически проверить модель;
2. зафиксировать immutable artifact и label/preprocessing contract;
3. собрать patient-level evaluation dataset;
4. воспроизвести реальный smoke test;
5. убрать клинические claims;
6. только после этого инвестировать в calibration, OOD, load tests и
   deployment.

Без Gate 0 дальнейшая оптимизация контейнера или UI увеличивает видимость
продукта, но не его доказательную ценность.
