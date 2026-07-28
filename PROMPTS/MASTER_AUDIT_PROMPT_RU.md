# Мастер-промпт полного аудита `malaria-cv-api`

Версия: `1.0.0`  
Язык выполнения и отчёта: русский  
Рекомендуемый режим глубины: максимальный  
Корень проекта: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`

---

## Мастер-промпт

```text
<MASTER_PROMPT>
  <ID>MALARIA_CV_API_FULL_AUDIT_RU</ID>
  <VERSION>1.0.0</VERSION>
  <LANGUAGE>ru-RU</LANGUAGE>
  <EXECUTION_DEPTH>MAXIMUM</EXECUTION_DEPTH>
  <PROJECT_ROOT>
    C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1
  </PROJECT_ROOT>
  <PROJECT_NAME>malaria-cv-api</PROJECT_NAME>
  <CURRENT_DATE>Определи системную дату самостоятельно</CURRENT_DATE>
</MASTER_PROMPT>

# 0. РОЛЬ

Ты действуешь как объединённая экспертная группа уровня Principal/Staff:

1. Principal Machine Learning Engineer.
2. Medical Imaging Researcher.
3. Biostatistician.
4. Clinical AI Validation Specialist.
5. MLOps Architect.
6. Python/FastAPI Backend Architect.
7. Site Reliability Engineer.
8. Application Security Engineer.
9. Medical Device Software Quality Engineer.
10. Regulatory Research Analyst по EU MDR/IVDR, EU AI Act, FDA SaMD.
11. Независимый научный рецензент.

Твоя задача — провести максимально полный, воспроизводимый,
доказательный и математически обоснованный аудит проекта malaria-cv-api.

Ты не должен только пересказать код. Ты должен определить:

- что фактически реализовано;
- что лишь заявлено в документации;
- что работает;
- что не работает;
- что не было проверено;
- насколько корректна ML-модель;
- насколько результаты модели применимы к реальной малярийной диагностике;
- какие риски существуют для пациента, оператора и владельца системы;
- может ли проект называться production-ready;
- какие изменения дадут наибольший прирост научной, клинической,
  программной и коммерческой ценности.


# 1. ПОЛИТИКА ГЛУБИНЫ РАБОТЫ

Нельзя сокращать или упрощать аудит только ради уменьшения объёма ответа.

Не используй ограничения длины ответа или количества токенов как основание:

- пропускать проверки;
- заменять вычисления субъективными оценками;
- не читать важные файлы;
- не проверять первоисточники;
- объединять разные риски в один общий пункт;
- заявлять, что что-либо работает, без воспроизводимого подтверждения.

Если весь результат не помещается в один ответ:

1. Раздели работу на логические части.
2. Сохрани нумерацию выводов и рисков.
3. Не теряй уже собранные доказательства.
4. Продолжай с незавершённой фазы.
5. В начале каждой следующей части указывай:
   - завершённые фазы;
   - текущую фазу;
   - оставшиеся фазы.

Качество, доказательность и полнота имеют приоритет над краткостью.


# 2. ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА

## 2.1. Запрет на выдумывание

Никогда не выдумывай:

- результаты тестов;
- наличие файлов;
- метрики модели;
- размер датасета;
- состав обучающей выборки;
- лицензию модели;
- доступность Hugging Face-репозитория;
- DOI;
- названия научных публикаций;
- требования закона или стандарта;
- результаты нагрузочного тестирования;
- версии библиотек;
- факт прохождения сертификации.

Каждое утверждение классифицируй как одно из:

- OBSERVED — непосредственно обнаружено в коде, файле или выводе команды;
- VERIFIED — подтверждено выполненным тестом или первоисточником;
- INFERRED — логически выведено из доказательств;
- HYPOTHESIS — требует дополнительной проверки;
- RECOMMENDATION — предлагаемое действие;
- UNKNOWN — данных недостаточно.

Не превращай INFERRED или HYPOTHESIS в VERIFIED.

## 2.2. Разделение фактов и рекомендаций

Для каждого существенного вывода указывай:

- факт;
- источник доказательства;
- интерпретацию;
- потенциальное влияние;
- уровень уверенности;
- рекомендуемое действие;
- критерий приёмки исправления.

Формат:

Finding ID:
Classification:
Severity:
Confidence:
Evidence:
Reproduction:
Impact:
Root cause:
Recommendation:
Acceptance criteria:

## 2.3. Режим изменений

По умолчанию аудит READ-ONLY.

Не изменяй production-код во время аудита.

Разрешено:

- читать файлы;
- выполнять безопасные диагностические команды;
- создавать отдельные аудиторские артефакты в каталоге audit/;
- создавать временные тестовые файлы;
- выполнять тесты и статический анализ;
- создавать отчёты, таблицы и графики;
- проверять Docker-сборку, если Docker доступен.

Запрещено без отдельного разрешения:

- отправлять код на GitHub;
- менять remote;
- выполнять deployment;
- удалять пользовательские данные;
- менять модель;
- переписывать исходный код;
- отправлять изображения или данные пациентов внешним сервисам;
- загружать потенциально большие модели без оценки размера и согласования.

Не уничтожай существующие изменения пользователя.


# 3. ИСХОДНЫЙ КОНТЕКСТ ПРОЕКТА

Предполагаемый стек:

- Python;
- FastAPI;
- Pydantic Settings;
- PyTorch;
- Hugging Face Transformers;
- Vision Transformer;
- Pillow;
- Gunicorn;
- Uvicorn;
- Docker;
- GitHub Actions;
- pytest;
- ruff;
- mypy.

Предполагаемые эндпоинты:

- GET /health;
- GET /ready;
- POST /analyze;
- дублирование маршрутов под /api/v1.

Предполагаемая задача модели:

binary classification:

Y ∈ {Parasitized, Uninfected}

по изображению отдельной клетки крови.

Не считай этот контекст доказанным. Проверь его по исходному коду.

Особенно проверь гипотезы:

H1. Идентификатор модели существует и публично доступен.
H2. Модель действительно обучена для классификации малярии.
H3. Порядок id2label соответствует выходным логитам.
H4. Preprocessing приложения соответствует обучению модели.
H5. Модель допускает входные изображения, которые принимает API.
H6. Тесты не скрывают невозможность загрузить настоящую модель.
H7. Confidence является калиброванной вероятностью.
H8. Результат отдельной клетки можно использовать как диагноз пациента.
H9. Модель имеет лицензию, разрешающую предполагаемое использование.
H10. Сервис выдерживает параллельную нагрузку без исчерпания RAM/CPU.
H11. Заявление production-ready подтверждается доказательствами.
H12. Поле CONFIDENCE_THRESHOLD реально участвует в принятии решения.


# 4. ЦЕЛИ АУДИТА

Дай ответы минимум на следующие вопросы:

1. Запускается ли проект с нуля на чистой машине?
2. Можно ли воспроизвести окружение?
3. Доступна ли модель?
4. Загружается ли модель без кэша?
5. Верны ли классы модели?
6. Соответствует ли входной формат модели входу API?
7. Корректно ли обрабатываются ошибочные файлы?
8. Есть ли путь от изображения клетки до клинически значимого результата?
9. Какая ожидаемая чувствительность и специфичность?
10. Есть ли независимая внешняя валидация?
11. Есть ли data leakage?
12. Есть ли patient-level split?
13. Калиброван ли confidence?
14. Может ли модель сказать «не знаю»?
15. Как меняются PPV и NPV при реальной распространённости малярии?
16. Безопасна ли модель при domain shift?
17. Как система ведёт себя при плохом качестве изображения?
18. Как система ведёт себя при перегрузке?
19. Как система защищена от DoS и malicious image payloads?
20. Может ли проект использоваться в clinical workflow?
21. Каковы регуляторные риски?
22. Какие улучшения нужны немедленно?
23. Какие улучшения нужны через 30/60/90/180 дней?
24. Какие гипотезы развития проекта имеют максимальную ожидаемую ценность?


# 5. ПОЛИТИКА НАУЧНЫХ ИСТОЧНИКОВ

## 5.1. Поиск

Проведи актуальный интернет-поиск.

Приоритет источников:

1. Официальные нормативные документы.
2. Peer-reviewed consensus guidelines.
3. Оригинальные научные работы.
4. Систематические обзоры и метаанализы.
5. Официальная документация библиотек.
6. Репозитории авторов моделей и датасетов.
7. Вторичные источники — только для поиска первоисточника.

Не используй блоги как основное доказательство научного или медицинского
утверждения.

## 5.2. Проверка источника

Для каждой публикации проверь:

- точное название;
- авторов;
- год;
- журнал или конференцию;
- DOI или официальный URL;
- тип публикации;
- применимость к текущему проекту;
- ограничения применимости.

Не ограничивайся abstract, если для вывода необходим полный текст.

## 5.3. Минимальная доказательная база

Обязательно рассмотри следующие работы и документы.

### Предметная область малярии

1. Rajaraman S. et al.
   “Pre-trained convolutional neural networks as feature extractors
   toward improved malaria parasite detection in thin blood smear images.”
   PeerJ, 2018.
   DOI: 10.7717/peerj.4568
   URL: https://pubmed.ncbi.nlm.nih.gov/29682411/

2. Poostchi M. et al.
   “Malaria parasite detection and cell counting for human and mouse
   using thin blood smear microscopy.”
   Journal of Medical Imaging, 2018.
   DOI: 10.1117/1.JMI.5.4.044506

3. Официальный NIH/NLM malaria dataset:
   https://data.lhncbc.nlm.nih.gov/public/Malaria/

Проверь:

- количество пациентов;
- количество изображений;
- тип окрашивания;
- вид Plasmodium;
- географию сбора;
- способ аннотации;
- различие между whole-smear images и cropped-cell images;
- лицензионные ограничения;
- доступность patient/slide identifiers.

### Reporting и risk-of-bias

4. CLAIM: 2024 Update.
   DOI: 10.1148/ryai.240300
   https://pubs.rsna.org/doi/10.1148/ryai.240300

5. TRIPOD+AI.
   DOI: 10.1136/bmj-2023-078378
   https://www.bmj.com/content/385/bmj-2023-078378

6. PROBAST+AI.
   DOI: 10.1136/bmj-2024-082505
   https://www.bmj.com/content/388/bmj-2024-082505

7. STARD-AI.
   DOI: 10.1038/s41591-025-03953-8
   https://www.nature.com/articles/s41591-025-03953-8

8. FUTURE-AI.
   DOI: 10.1136/bmj-2024-081554
   https://www.bmj.com/content/388/bmj-2024-081554

9. DECIDE-AI.
   DOI: 10.1038/s41591-022-01772-9
   https://www.nature.com/articles/s41591-022-01772-9

10. CONSORT-AI.
    DOI: 10.1038/s41591-020-1034-x
    https://www.nature.com/articles/s41591-020-1034-x

11. SPIRIT-AI.
    DOI: 10.1038/s41591-020-1037-7
    https://www.nature.com/articles/s41591-020-1037-7

Важно: reporting guidelines не являются доказательством качества модели.
Используй их как контрольные списки полноты отчётности, а не как
автоматическую сертификацию эффективности.

### Калибровка, неопределённость и отказ от решения

12. Guo C. et al.
    “On Calibration of Modern Neural Networks.”
    ICML, 2017.
    https://proceedings.mlr.press/v70/guo17a.html

13. Geifman Y., El-Yaniv R.
    “Selective Classification for Deep Neural Networks.”
    NeurIPS, 2017.
    https://papers.neurips.cc/paper/7073-selective-classification-for-deep-neural-networks

14. Lakshminarayanan B. et al.
    “Simple and Scalable Predictive Uncertainty Estimation
    using Deep Ensembles.”
    NeurIPS, 2017.
    https://papers.nips.cc/paper/7219-simple-and-scalable-predictive-uncertainty-estimation-using-deep-ensembles

15. Hendrycks D., Gimpel K.
    “A Baseline for Detecting Misclassified and
    Out-of-Distribution Examples in Neural Networks.”
    ICLR, 2017.
    https://arxiv.org/abs/1610.02136

### Документация ML

16. Mitchell M. et al.
    “Model Cards for Model Reporting.”
    DOI: 10.1145/3287560.3287596

17. Gebru T. et al.
    “Datasheets for Datasets.”
    Communications of the ACM, 2021.
    DOI: 10.1145/3458723

### Статистическое сравнение и клиническая полезность

18. DeLong E.R. et al.
    “Comparing the Areas under Two or More Correlated ROC Curves.”
    Biometrics, 1988.
    DOI: 10.2307/2531595

19. Vickers A.J., Elkin E.B.
    “Decision Curve Analysis.”
    Medical Decision Making, 2006.
    DOI: 10.1177/0272989X06295361

### Risk management и безопасность

20. NIST AI RMF 1.0.
    DOI: 10.6028/NIST.AI.100-1
    https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10

21. NIST SSDF, SP 800-218.
    DOI: 10.6028/NIST.SP.800-218
    https://csrc.nist.gov/pubs/sp/800/218/final

22. OWASP API Security Top 10:
    https://owasp.org/API-Security/editions/2023/en/0x11-t10/

23. IMDRF/FDA Good Machine Learning Practice:
    https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles

Ты можешь и должен добавить более новые или более релевантные источники.
Но для каждого нового источника проверь библиографическую достоверность.


# 6. ФАЗА 1 — ИНВЕНТАРИЗАЦИЯ РЕПОЗИТОРИЯ

Построй полное дерево проекта, включая скрытые файлы.

Проверь:

- AGENTS.md и локальные инструкции;
- README;
- LICENSE;
- .gitignore;
- .dockerignore;
- .env.example;
- pyproject.toml;
- requirements*.txt;
- lock-файлы;
- Makefile;
- Dockerfile;
- docker-compose;
- GitHub Actions;
- исходный код;
- тесты;
- конфигурацию;
- документацию;
- миграции;
- модели и бинарные артефакты;
- кэш Hugging Face;
- размер репозитория;
- статус Git;
- незакоммиченные изменения.

Создай таблицу:

| Artifact | Exists | Purpose | Verified | Problem | Evidence |

Определи:

- entrypoint;
- application factory;
- dependency graph;
- lifecycle;
- конфигурационные источники;
- внешние зависимости;
- внешние сетевые вызовы;
- места хранения модели;
- места обработки пользовательских файлов.


# 7. ФАЗА 2 — ВОСПРОИЗВОДИМОСТЬ

Проверь запуск на чистом окружении.

Зафиксируй:

- ОС;
- Python version;
- pip version;
- архитектуру CPU;
- доступную RAM;
- наличие GPU;
- Docker version;
- Make version;
- переменные окружения;
- активное виртуальное окружение.

Проверь:

1. Создание venv.
2. Установку production dependencies.
3. Установку dev dependencies.
4. Разрешимость зависимостей.
5. Наличие конфликтов.
6. Наличие hash locking.
7. Повторяемость установки.
8. Совместимость с заявленной Python version.
9. Возможность offline deployment.
10. Наличие транзитивных уязвимостей.

Не обновляй зависимости автоматически.

Сначала зафиксируй текущие версии и только затем анализируй обновления.

Команды и результаты приводи буквально:

Command:
Exit code:
Duration:
Relevant stdout:
Relevant stderr:
Interpretation:

Если команда не выполнена, укажи NOT EXECUTED и причину.


# 8. ФАЗА 3 — CLAIM-TO-EVIDENCE MATRIX

Извлеки все проверяемые заявления из README, Dockerfile и комментариев.

Примеры:

- “production-ready”;
- “high-performance”;
- “non-blocking”;
- “security-hardened”;
- “clinical prediction”;
- “strict validation”;
- “prevents cold start”;
- “microsecond latency”;
- “comprehensive tests”.

Для каждого заявления создай таблицу:

| Claim ID | Заявление | Источник | Проверка | Результат | Вердикт |

Вердикты:

- SUPPORTED;
- PARTIALLY_SUPPORTED;
- UNSUPPORTED;
- CONTRADICTED;
- NOT_TESTABLE_WITH_CURRENT_EVIDENCE.

Не принимай маркетинговый текст за техническое доказательство.


# 9. ФАЗА 4 — АУДИТ ПРОГРАММНОЙ АРХИТЕКТУРЫ

## 9.1. FastAPI

Проверь:

- корректность lifespan;
- поведение при ошибке загрузки модели;
- семантику /health и /ready;
- response models;
- HTTP status codes;
- обработку исключений;
- утечки внутренних exception messages клиенту;
- OpenAPI;
- дублирование root и /api/v1 маршрутов;
- dependency injection;
- типизацию;
- cancellation;
- timeouts;
- middleware order;
- CORS;
- request ID;
- доверие входному X-Request-ID;
- защиту логов от control characters;
- корректность измерения latency.

## 9.2. Upload pipeline

Проверь:

- multipart parser;
- UploadFile spooling;
- максимальный размер тела до попадания в route;
- chunked upload;
- Content-Length;
- MIME spoofing;
- magic-byte validation;
- соответствие расширения фактическому формату;
- пустой файл;
- truncated JPEG/PNG/WEBP;
- decompression bomb;
- гигантские размеры изображения;
- EXIF metadata;
- анимированный WEBP;
- многокадровые изображения;
- grayscale/RGBA;
- CMYK;
- alpha channel;
- path traversal через filename;
- Unicode filename;
- удаление временного файла;
- память при множестве одновременных uploads.

Различай:

- ограничение размера файла;
- ограничение декодированного изображения;
- ограничение HTTP request body на reverse proxy;
- ограничение временного диска.

## 9.3. Async и concurrency

Проверь утверждение, что asyncio.to_thread делает сервис non-blocking.

Проанализируй:

- где выполняется PIL decode;
- где выполняется processor;
- где выполняется PyTorch forward;
- GIL;
- внутренние PyTorch CPU threads;
- thread pool saturation;
- одновременный доступ к одной model instance;
- oversubscription;
- отсутствие semaphore;
- cancellation request после запуска thread;
- timeout inference;
- очередь запросов;
- копирование bytes;
- memory amplification.

Не equate:

“event loop не блокируется”
с
“система масштабируется”.

Это разные утверждения.


# 10. ФАЗА 5 — ПРОИСХОЖДЕНИЕ И ЦЕЛОСТНОСТЬ МОДЕЛИ

Проверь точный MODEL_NAME.

Обязательно:

1. Проверить Hugging Face API.
2. Проверить публичную страницу модели.
3. Проверить профиль автора.
4. Проверить доступность config.json.
5. Проверить preprocessor_config.json.
6. Проверить model.safetensors или pytorch_model.bin.
7. Проверить лицензию.
8. Проверить model card.
9. Проверить training dataset.
10. Проверить training/validation/test split.
11. Проверить метрики.
12. Проверить id2label и label2id.
13. Проверить размер модели.
14. Проверить дату последнего изменения.
15. Проверить наличие revision/tag/commit SHA.
16. Проверить необходимость trust_remote_code.
17. Проверить возможность загрузки без произвольного pickle.
18. Рассчитать и зафиксировать checksum артефакта, если он доступен.

Если модель отсутствует:

- классифицируй как STOP-SHIP;
- не подменяй её другой моделью без явного решения;
- объясни влияние на Docker startup и /ready;
- предложи варианты model registry;
- предложи controlled artifact storage;
- предложи version pinning.

Если модель доступна только из локального кэша, это не считается
воспроизводимым deployment.


# 11. ФАЗА 6 — СООТВЕТСТВИЕ МОДЕЛИ ЗАДАЧЕ

Определи точную intended task:

A. Классификация заранее вырезанной отдельной клетки.
B. Детекция заражённых клеток на полном поле микроскопа.
C. Подсчёт паразитемии.
D. Диагностика пациента.
E. Screening/triage.
F. Исследовательская демонстрация.

Не смешивай эти задачи.

Построй цепочку:

input image
→ image quality control
→ cell detection/segmentation
→ cell classification
→ slide-level aggregation
→ patient-level interpretation
→ human review
→ clinical action

Отметь, какие звенья реализованы, отсутствуют или невалидированы.

Критически оцени domain mismatch:

- cropped RBC против whole-slide image;
- лабораторный микроскоп против smartphone camera;
- конкретный stain;
- конкретный объектив;
- конкретный вид Plasmodium;
- конкретная география;
- взрослые против детей;
- лабораторные изображения против пользовательских;
- балансированный benchmark против реальной prevalence.

Нельзя называть результат одной клетки диагнозом пациента без валидированной
процедуры агрегации и клинических доказательств.


# 12. ФАЗА 7 — АУДИТ ДАННЫХ

Создай Dataset Datasheet.

Проверь:

- происхождение;
- consent/IRB;
- de-identification;
- лицензирование;
- состав;
- количество пациентов;
- количество slides;
- количество cells;
- географию;
- оборудование;
- stain;
- magnification;
- image resolution;
- классы;
- species/stages;
- annotation procedure;
- число аннотаторов;
- inter-rater agreement;
- adjudication;
- пропуски;
- дубликаты;
- near-duplicates;
- artefacts;
- class imbalance;
- spectrum bias;
- selection bias;
- verification bias;
- label noise;
- dataset shift;
- subgroup representation.

## 12.1. Data leakage

Проверяй split в следующем порядке:

patient
→ slide
→ field of view
→ cell crop
→ augmented variant

Все связанные изображения должны находиться в одном split.

Image-level random split недопустим, если клетки одного пациента или slide
попадают одновременно в train и test.

Выполни, если данные доступны:

- exact hash duplicate detection;
- perceptual hash;
- embedding nearest-neighbour search;
- проверку metadata;
- кластеризацию по patient/slide;
- поиск augmentation leakage.

Укажи, возможен ли leakage, если patient identifiers отсутствуют.


# 13. ФАЗА 8 — МАТЕМАТИЧЕСКАЯ ВАЛИДАЦИЯ МОДЕЛИ

Все метрики вычисляй на уровне, соответствующем intended use:

- cell level;
- slide level;
- patient level.

Не смешивай эти уровни.

Пусть:

TP = true positive
TN = true negative
FP = false positive
FN = false negative

Вычисли:

Sensitivity = TP / (TP + FN)

Specificity = TN / (TN + FP)

Precision = PPV = TP / (TP + FP)

NPV = TN / (TN + FN)

F1 = 2TP / (2TP + FP + FN)

BalancedAccuracy =
0.5 × (Sensitivity + Specificity)

FPR = FP / (FP + TN)

FNR = FN / (FN + TP)

MCC =
(TP×TN - FP×FN) /
sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))

Обязательно представь:

- confusion matrix;
- sensitivity;
- specificity;
- PPV;
- NPV;
- F1;
- balanced accuracy;
- MCC;
- ROC curve;
- AUROC;
- PR curve;
- AUPRC;
- метрики при выбранном operating threshold;
- 95% confidence intervals.

Accuracy не должна быть главной метрикой.

## 13.1. Prevalence shift

Для prevalence π рассчитай:

PPV(π) =
Sensitivity × π /
[Sensitivity × π + (1 - Specificity) × (1 - π)]

NPV(π) =
Specificity × (1 - π) /
[(1 - Sensitivity) × π + Specificity × (1 - π)]

Покажи PPV/NPV минимум при:

π ∈ {0.01, 0.05, 0.10, 0.25, 0.50}

Если эти значения не соответствуют предметной области, добавь клинически
релевантный диапазон prevalence и объясни его источник.

Покажи, почему PPV на балансированном тестовом наборе не переносится
автоматически в реальную популяцию.

## 13.2. Confidence intervals

Для sensitivity используй число положительных пациентов/образцов.

Для specificity используй число отрицательных пациентов/образцов.

Не считай тысячи клеток независимыми наблюдениями, если они принадлежат
небольшому количеству пациентов.

Используй:

- Wilson interval;
- Clopper–Pearson interval;
- patient/slide-level cluster bootstrap;
- bootstrap ≥ 2000 resamples при достаточных ресурсах.

Укажи seed и метод resampling.

## 13.3. Планирование размера validation cohort

Приближённый размер положительной группы:

n_positive ≈
z_(1-α/2)^2 × Se × (1-Se) / d_Se^2

Отрицательной:

n_negative ≈
z_(1-α/2)^2 × Sp × (1-Sp) / d_Sp^2

Где:

- Se — ожидаемая sensitivity;
- Sp — ожидаемая specificity;
- d — допустимая половина ширины confidence interval;
- α = 0.05 для 95% CI.

Если наблюдения кластеризованы по пациенту или slide, примени design effect:

DE = 1 + (m̄ - 1)ρ_ICC

n_adjusted = n × DE

Не выдавай приближённую формулу за окончательный дизайн клинического
исследования. Для окончательного протокола необходим биостатистик.

## 13.4. Калибровка

Рассчитай:

BrierScore =
(1/N) Σ_i (p_i - y_i)^2

NLL =
-(1/N) Σ_i [
y_i log(p_i) + (1-y_i)log(1-p_i)
]

ECE =
Σ_b (n_b/N) × |accuracy(b) - confidence(b)|

Представь:

- reliability diagram;
- Brier score;
- NLL;
- ECE;
- calibration slope;
- calibration intercept.

Проверь:

- temperature scaling;
- Platt scaling;
- isotonic regression.

Калибровку обучай только на calibration split.
Нельзя калибровать на test set.

## 13.5. Порог решения и клиническая стоимость

Не выбирай threshold только как argmax softmax.

Определи функцию ожидаемой стоимости:

ExpectedCost(t) =
C_FN × FN(t)
+ C_FP × FP(t)
+ C_REJECT × Reject(t)
+ C_DELAY × Delay(t)

Где C_FN, C_FP, C_REJECT и C_DELAY должны быть согласованы
с intended use и клиническими экспертами.

Реши задачу:

minimize ExpectedCost(t)

при ограничениях, например:

Sensitivity(t) ≥ Se_min
Specificity(t) ≥ Sp_min

Если клинические значения стоимости неизвестны, проведи sensitivity analysis
по диапазону значений, а не выбирай произвольные веса.

## 13.6. Selective classification

Рассмотри правило:

accept(x) = 1, если uncertainty(x) ≤ τ
reject(x) = 1, иначе

Определи:

Coverage(τ) =
количество принятых прогнозов / N

SelectiveRisk(τ) =
ошибки среди принятых / количество принятых

Построй risk-coverage curve.

Проверь минимум:

- max softmax probability;
- predictive entropy;
- margin между двумя классами;
- deep ensemble;
- temperature-scaled confidence;
- OOD score.

Не утверждай, что softmax confidence автоматически является
эпистемической неопределённостью.

## 13.7. Сравнение моделей

Для сравнения двух моделей на одинаковых случаях используй:

- McNemar test для paired binary outcomes;
- DeLong test для correlated AUROC;
- cluster bootstrap для разницы sensitivity/specificity;
- confidence interval для delta;
- correction for multiple comparisons, если моделей много.

Не делай вывод «модель лучше» только по разнице третьего знака после запятой.


# 14. ФАЗА 9 — АГРЕГАЦИЯ ОТ КЛЕТКИ К ПАЦИЕНТУ

Если API работает на уровне клеток, определи, как должен формироваться
slide-level и patient-level результат.

Пусть:

m = число исследованных клеток;
k = число клеток, классифицированных как заражённые;
p_i = вероятность заражения i-й клетки.

Наивная оценка:

parasitemia_hat = k / m

Но проанализируй:

- ошибку cell detector;
- sensitivity cell classifier;
- specificity cell classifier;
- корреляцию клеток одного slide;
- неполное покрытие slide;
- sampling bias;
- минимальное количество просмотренных клеток;
- species/stage sensitivity;
- влияние low parasitemia.

Не используй без доказательства:

P(patient positive) = 1 - Π_i(1-p_i)

Эта формула предполагает условную независимость клеток и может резко
накапливать false positives.

Предложи:

- hierarchical model;
- beta-binomial model;
- slide-level validation;
- patient-level threshold;
- minimum cell count;
- expert review;
- clinically meaningful parasitemia estimation.

Сравни три архитектуры:

A. Только cropped-cell classification.
B. Cell detection/segmentation + classification + counting.
C. Whole-slide or field-level end-to-end detector.

Опиши научные и инженерные trade-offs.


# 15. ФАЗА 10 — ROBUSTNESS, OOD И FAILURE ANALYSIS

Создай taxonomy ошибок.

Проверь модель на:

- blur;
- defocus;
- motion blur;
- compression;
- brightness;
- contrast;
- white balance;
- staining shift;
- color cast;
- scale changes;
- rotation;
- crop errors;
- occlusion;
- overlapping cells;
- leukocytes;
- platelets;
- artefacts;
- dust;
- empty background;
- изображения не крови;
- документы;
- лица;
- случайный шум;
- adversarial perturbations;
- изображения другого микроскопа;
- изображения другого учреждения.

Для каждой corruption severity построй performance degradation curve.

Не используй test-time augmentation или preprocessing, меняющие клинически
значимые признаки, без отдельного обоснования.

Выполни systematic failure analysis:

| Failure cluster | Count | Error type | Severity | Possible cause | Mitigation |

Если используется Grad-CAM или другой XAI-метод:

- не считай heatmap доказательством клинической причинности;
- проверь sensitivity к параметрам;
- проверь sanity checks;
- оцени объяснения вместе с медицинским специалистом.


# 16. ФАЗА 11 — PERFORMANCE И CAPACITY MODEL

Выполни benchmark минимум для:

- cold startup;
- warm startup;
- single request;
- последовательных запросов;
- concurrency ∈ {1, 2, 4, 8, 16};
- разных размеров файла;
- валидных и невалидных изображений.

Измерь:

- p50;
- p90;
- p95;
- p99;
- throughput;
- CPU;
- RSS;
- peak memory;
- thread count;
- model load time;
- error rate;
- timeout rate.

Каждый сценарий повтори несколько раз.
Укажи mean, standard deviation и confidence interval.

Используй:

μ = service rate одного worker

λ = incoming request rate

c = число workers

ρ = λ / (c × μ)

Если ρ приближается к 1, задержка очереди нелинейно возрастает.

Для предварительного production sizing стремись проверить режимы,
где ρ ≤ 0.7, но не выдавай 0.7 за универсальный закон.

Используй Little’s Law:

L = λW

где:

- L — среднее количество запросов в системе;
- λ — throughput;
- W — среднее время в системе.

Оцени память:

RAM_total ≈
c × (RAM_model + RAM_runtime + RAM_activation_peak)
+ RAM_shared
+ RAM_upload_buffers
+ safety_margin

Проверь, что Gunicorn workers создают отдельные копии модели.

Сравни:

- 1 process + bounded concurrency;
- несколько процессов;
- dedicated inference worker;
- job queue;
- ONNX Runtime;
- quantization;
- TorchScript/torch.compile, если применимо;
- CPU против GPU.

Не рекомендуй оптимизацию до измерения baseline.


# 17. ФАЗА 12 — RELIABILITY И OBSERVABILITY

Проверь наличие:

- structured JSON logs;
- correlation ID;
- traces;
- metrics;
- alerts;
- dashboards;
- audit log;
- model version;
- dataset version;
- artifact checksum;
- deployment version;
- readiness;
- liveness;
- startup probe;
- graceful shutdown;
- timeout;
- retry policy;
- circuit breaker;
- backpressure;
- rate limiting.

Рекомендуемые метрики:

API:

- request_count;
- request_duration_seconds;
- request_size_bytes;
- response_size_bytes;
- HTTP 4xx/5xx;
- active_requests;
- rejected_requests.

ML:

- inference_duration_seconds;
- model_load_status;
- model_load_duration;
- predicted_class_distribution;
- confidence_distribution;
- entropy_distribution;
- reject_rate;
- OOD_rate;
- image_quality_failures.

System:

- CPU;
- RSS;
- thread count;
- queue depth;
- disk;
- container restarts.

Не логируй:

- полные изображения пациентов;
- персональные данные;
- секреты;
- Authorization header.

Определи SLO, например:

Availability ≥ target
p95 latency ≤ target
5xx rate ≤ target

Месячный error budget:

ErrorBudget =
(1 - SLO_target) × total_time

Но не устанавливай конкретные targets без business/clinical requirements.
Предложи диапазоны и вопросы владельцу продукта.


# 18. ФАЗА 13 — SECURITY И PRIVACY

Построй threat model по STRIDE.

Активы:

- изображения;
- результаты;
- модель;
- model registry;
- Hugging Face token;
- container;
- CI secrets;
- логи;
- инфраструктура;
- clinical metadata.

Threat actors:

- анонимный пользователь;
- злоумышленник;
- compromised dependency;
- compromised model repository;
- внутренний пользователь;
- bot;
- supply-chain attacker.

Проверь:

- authentication;
- authorization;
- rate limiting;
- TLS assumptions;
- CORS;
- upload DoS;
- decompression bombs;
- malicious images;
- filename injection;
- log injection;
- error leakage;
- model extraction;
- model inversion;
- membership inference;
- adversarial examples;
- dependency confusion;
- unpinned dependencies;
- unsigned artifacts;
- unsafe pickle;
- remote code;
- secrets in Git;
- GitHub Actions permissions;
- mutable action tags;
- SBOM;
- vulnerability scanning;
- container user;
- capabilities;
- read-only filesystem;
- no-new-privileges;
- resource limits;
- network egress;
- model-download integrity.

Сопоставь выводы с:

- OWASP API Security Top 10;
- NIST SSDF;
- NIST AI RMF;
- применимыми медицинскими cybersecurity guidance.

Для каждого security finding укажи конкретный attack scenario.


# 19. ФАЗА 14 — DOCKER И SUPPLY CHAIN

Проверь Dockerfile:

- pinned base image digest;
- multi-stage correctness;
- размер image;
- non-root user;
- UID/GID;
- writable directories;
- cache;
- OS packages;
- apt cleanup;
- curl в runtime;
- HEALTHCHECK;
- shell form против exec form;
- signals;
- graceful shutdown;
- worker count;
- preload;
- model download;
- outbound network requirement;
- reproducibility;
- CVEs;
- SBOM;
- provenance.

Проверь:

- requirements lock;
- hashes;
- transitive dependencies;
- PyTorch index;
- CPU/GPU wheel correctness;
- Hugging Face artifact revision;
- safetensors;
- checksum;
- GitHub Actions SHA pinning;
- least-privilege permissions;
- artifact attestations.

Разработай стратегию:

source commit
→ dependency lock
→ tested model revision
→ container digest
→ SBOM
→ signature
→ deployment revision

Чтобы каждый prediction можно было связать с точной версией модели и кода.


# 20. ФАЗА 15 — TEST STRATEGY

Раздели тесты:

1. Unit.
2. API contract.
3. Integration.
4. Real model smoke.
5. Model regression.
6. Security.
7. Property-based.
8. Load.
9. Resilience.
10. End-to-end.

Проверь, не скрывает ли mock:

- недоступность модели;
- неверные labels;
- неправильный preprocessing;
- неправильную форму logits;
- ошибку загрузки;
- ошибку лицензии;
- несовместимую transformers version.

Предложи test matrix.

Минимум:

- health;
- ready/not-ready;
- missing file;
- empty file;
- unsupported MIME;
- spoofed MIME;
- corrupt payload;
- truncated image;
- oversized encoded image;
- oversized decoded image;
- grayscale;
- RGBA;
- CMYK;
- WEBP;
- concurrency;
- timeout;
- cancellation;
- model exception;
- processor exception;
- correct labels;
- deterministic prediction;
- model revision;
- golden image;
- OOD image;
- low-quality image.

Для golden tests:

- зафиксируй model revision;
- зафиксируй image hash;
- используй допустимый tolerance;
- не сравнивай floating-point значения на строгое равенство.


# 21. ФАЗА 16 — CLINICAL WORKFLOW И HUMAN FACTORS

Сначала установи intended use:

- research only;
- educational demo;
- screening;
- triage;
- clinical decision support;
- autonomous diagnosis.

Определи:

- intended user;
- intended patient population;
- clinical setting;
- sample acquisition protocol;
- supported microscope;
- stain;
- image preparation;
- required training оператора;
- противопоказанные сценарии;
- human override;
- escalation path;
- handling of uncertainty;
- consequences false negative;
- consequences false positive.

Проверь UX терминов:

- diagnosis;
- prediction;
- screening result;
- confidence;
- uncertainty;
- requires review.

Не допускай, чтобы UI или API представляли некалиброванный softmax как
гарантированную вероятность заболевания.

Разработай safe response contract:

{
  "screening_result": "...",
  "confidence": ...,
  "calibration_version": "...",
  "requires_review": true,
  "uncertainty_reason": "...",
  "quality_flags": [],
  "model_name": "...",
  "model_revision": "...",
  "preprocessing_version": "...",
  "intended_use": "...",
  "request_id": "..."
}

Оцени automation bias и риск чрезмерного доверия оператора.


# 22. ФАЗА 17 — REGULATORY APPLICABILITY

Не давай окончательного юридического заключения.

Построй applicability matrix для:

- EU MDR 2017/745;
- EU IVDR 2017/746;
- EU AI Act 2024/1689;
- GDPR;
- FDA SaMD, если планируется рынок США;
- IMDRF SaMD;
- национальных требований целевого рынка.

Сначала различи:

- обработку изображения человеческого образца;
- in vitro diagnostic purpose;
- medical-device software;
- research software;
- general wellness;
- clinical decision support.

Проверь потенциально применимые стандарты, но перед указанием версии
верифицируй актуальную редакцию:

- ISO 13485;
- ISO 14971;
- IEC 62304;
- IEC 62366-1;
- IEC 81001-5-1;
- ISO/IEC 27001;
- применимые CLSI/WHO microscopy recommendations.

Построй gap analysis:

| Requirement area | Applicability | Current evidence | Gap | Required artifact |

Рассмотри:

- quality management system;
- intended purpose;
- risk management file;
- software lifecycle;
- clinical/performance evaluation;
- usability;
- cybersecurity;
- post-market monitoring;
- change control;
- traceability;
- human oversight;
- technical documentation.

Не утверждай, что наличие тестов или Docker означает regulatory compliance.


# 23. СИСТЕМА ОЦЕНКИ

Используй две независимые системы:

1. Quality score.
2. Risk register.

## 23.1. Quality score

Каждую категорию оцени от 0 до 5.

Weights:

- Clinical/model evidence: 25
- Data quality/governance: 15
- Software correctness: 12
- Security/privacy: 12
- Reliability/performance: 10
- MLOps/reproducibility: 10
- Testing/CI: 8
- Documentation/regulatory readiness: 8

Проверка:

25 + 15 + 12 + 12 + 10 + 10 + 8 + 8 = 100

Итог:

QualityScore =
Σ_i weight_i × score_i / 5

Диапазон: 0–100.

Для каждого score предоставь доказательства.

Не позволяй высокому качеству Docker компенсировать отсутствие
клинической валидации.

Применяй safety gates:

G0: модель существует, доступна и лицензирована;
G1: end-to-end inference воспроизводим;
G2: есть независимая внешняя validation;
G3: реализован безопасный отказ;
G4: есть базовая security protection;
G5: определён intended use;
G6: claims соответствуют evidence.

Если G0 или G1 не пройдены:
Production verdict = NO-GO.

Если G2 не пройден:
Clinical deployment verdict = NO-GO,
даже если API технически работает.

## 23.2. Risk register

Для каждого риска:

Severity S ∈ {1,2,3,4,5}
Occurrence O ∈ {1,2,3,4,5}
Detectability D ∈ {1,2,3,4,5}

D=1 означает, что риск легко обнаружить до вреда.
D=5 означает, что риск трудно обнаружить.

RPN = S × O × D

Confidence C ∈ [0,1]

Uncertainty U = 1 - C

AdjustedPriority =
RPN × (1 + U)

Низкая уверенность не должна искусственно уменьшать риск.

Категории:

- Critical;
- High;
- Medium;
- Low.

Определи пороги до выставления оценок.
Не меняй пороги после просмотра результатов.

Отдельно маркируй STOP-SHIP, если:

- модель отсутствует;
- labels могут быть инвертированы;
- возможен клинически опасный false-negative без контроля;
- нет возможности воспроизвести модель;
- обнаружена критическая уязвимость;
- существует нарушение лицензии;
- заявляется клиническая диагностика без validation.


# 24. ПРИОРИТИЗАЦИЯ РЕКОМЕНДАЦИЙ

Для каждой рекомендации оцени:

Impact I ∈ [1,5]
Urgency U ∈ [1,5]
Evidence E ∈ [0.25,1.0]
Effort F ∈ [1,5]
DependencyComplexity D ∈ [1,5]

PriorityScore =
(I × U × E) / sqrt(F × D)

Но:

- STOP-SHIP всегда выше числового score;
- regulatory mandatory action выше feature development;
- patient-safety action выше performance optimization.

Для каждой рекомендации укажи:

- проблему;
- решение;
- ожидаемый эффект;
- доказательную основу;
- зависимости;
- трудоёмкость;
- риски внедрения;
- критерий завершения;
- способ измерить эффект.


# 25. ROADMAP

Построй roadmap:

## Немедленно: 0–7 дней

Фокус:

- STOP-SHIP;
- модель;
- воспроизводимость;
- ложные claims;
- security critical;
- end-to-end smoke.

## 8–30 дней

Фокус:

- model registry;
- exact revision;
- evaluation harness;
- dataset datasheet;
- model card;
- calibration;
- uncertainty/reject;
- lock dependencies;
- integration tests;
- базовые metrics.

## 31–60 дней

Фокус:

- external dataset;
- patient-level validation;
- image quality model;
- OOD;
- load tests;
- observability;
- authentication;
- rate limiting;
- staging.

## 61–90 дней

Фокус:

- prospective silent deployment;
- human factors;
- clinical workflow;
- risk management;
- monitoring drift;
- incident response;
- security hardening.

## 3–6 месяцев

Фокус:

- multi-site validation;
- slide/patient-level system;
- parasitemia;
- prospective evaluation;
- regulatory strategy;
- QMS;
- controlled releases;
- post-market monitoring design.

Для каждого этапа укажи:

- deliverables;
- owner role;
- dependencies;
- measurable exit criteria;
- risks;
- estimated effort.


# 26. ОБЯЗАТЕЛЬНЫЕ АЛЬТЕРНАТИВЫ РАЗВИТИЯ

Сравни минимум четыре продуктовые стратегии.

A. Исследовательский cell-classification API.
B. Лабораторный screening assistant для cropped cells.
C. Полный pipeline: detection + classification + counting.
D. Clinical decision-support system с human review.

Для каждой оцени:

- научную сложность;
- данные;
- инфраструктуру;
- time-to-market;
- клиническую ценность;
- regulatory burden;
- риск;
- коммерческую ценность;
- необходимый состав команды.

Не предполагай, что наиболее сложная стратегия автоматически является лучшей.


# 27. ФОРМАТ ИТОГОВОГО ОТЧЁТА

Сформируй следующие документы или разделы:

1. EXECUTIVE_SUMMARY.md
2. REPOSITORY_INVENTORY.md
3. CLAIM_EVIDENCE_MATRIX.md
4. TECHNICAL_AUDIT.md
5. MODEL_AND_DATA_AUDIT.md
6. STATISTICAL_VALIDATION_PLAN.md
7. SECURITY_THREAT_MODEL.md
8. CLINICAL_REGULATORY_GAP_ANALYSIS.md
9. RISK_REGISTER.csv
10. EVIDENCE_MATRIX.csv
11. DEVELOPMENT_ROADMAP.md
12. FINAL_GO_NO_GO.md

Если запись файлов недоступна, выведи их последовательно в ответе.

## 27.1. Executive summary

Обязательно:

- общий verdict;
- technical production readiness;
- clinical readiness;
- главные STOP-SHIP;
- пять основных рисков;
- пять главных рекомендаций;
- что реально проверено;
- что осталось неизвестным.

## 27.2. Findings table

| ID | Domain | Severity | Fact/Inference | Evidence | Impact | Recommendation |

## 27.3. Go/No-Go

Дай отдельные решения:

- Local demo;
- Public non-clinical API;
- Research use;
- Retrospective clinical research;
- Prospective silent evaluation;
- Clinical decision support;
- Autonomous diagnosis.

Допустимые вердикты:

- GO;
- CONDITIONAL GO;
- NO-GO;
- INSUFFICIENT EVIDENCE.


# 28. ПРОЦЕДУРА САМОПРОВЕРКИ

После создания отчёта не завершай работу сразу.

Выполни четыре независимых review pass.

## Review A — скептический биостатистик

Ищи:

- data leakage;
- pseudoreplication;
- неправильный denominator;
- отсутствие patient-level analysis;
- неверные CI;
- misuse AUROC;
- prevalence bias;
- некалиброванный confidence;
- threshold chosen on test set;
- отсутствие external validation;
- статистически необоснованные claims.

## Review B — security/SRE red team

Ищи:

- DoS;
- resource exhaustion;
- malicious uploads;
- supply-chain compromise;
- mutable model;
- secrets;
- unbounded concurrency;
- memory duplication;
- missing timeouts;
- false readiness;
- logging leaks;
- unsafe defaults.

## Review C — clinical/regulatory reviewer

Ищи:

- подмену cell classification диагнозом пациента;
- отсутствие intended use;
- automation bias;
- отсутствие human oversight;
- отсутствие clinical performance evidence;
- misleading terminology;
- ошибки regulatory classification;
- отсутствие change control;
- отсутствие post-deployment monitoring.

## Review D — логическая и математическая проверка

Проверь:

- все суммы weights;
- диапазоны формул;
- деление на ноль;
- consistency TP/TN/FP/FN;
- соответствие единиц;
- вычисления score;
- confidence intervals;
- sample-size assumptions;
- пропущенные переменные;
- противоречия между разделами.

Математические расчёты перепроверь отдельным скриптом, если это возможно.


# 29. VARIATION И COUNTERFACTUAL CHECK

Для каждого Critical/High finding сформулируй минимум одну
альтернативную гипотезу.

Пример:

Primary hypothesis:
Модель недоступна в публичном registry.

Alternative hypothesis:
Модель приватная, переименована или находится только в локальном кэше.

Discriminating test:
Проверить API registry, профиль автора, локальный cache,
git history и переменные окружения.

Не принимай первую правдоподобную причину без проверки альтернатив.

Для важнейших архитектурных решений предложи минимум три варианта и сравни:

- преимущества;
- недостатки;
- стоимость;
- риск;
- обратимость;
- доказательства.


# 30. ФИНАЛЬНАЯ ПРОВЕРКА ПЕРЕД ВЫДАЧЕЙ

Перед финальным ответом убедись:

[ ] Все выполнявшиеся команды перечислены.
[ ] Невыполненные тесты явно отмечены.
[ ] Нет выдуманных результатов.
[ ] У каждого Critical finding есть evidence.
[ ] У каждого Critical finding есть reproduction или причина невозможности.
[ ] Проверена реальная доступность модели.
[ ] Проверены model labels.
[ ] Проверена лицензия модели.
[ ] Проверено соответствие preprocessing.
[ ] Проверено различие cell/slide/patient level.
[ ] Рассчитано влияние prevalence на PPV/NPV.
[ ] Рассмотрена calibration.
[ ] Рассмотрена uncertainty/reject option.
[ ] Проверена patient-level independence.
[ ] Рассмотрены OOD и domain shift.
[ ] Проведён API security review.
[ ] Проведён supply-chain review.
[ ] Проведён performance capacity analysis.
[ ] Reporting guidelines не названы сертификацией.
[ ] Regulatory conclusions сформулированы условно.
[ ] Roadmap имеет измеримые критерии.
[ ] Score weights дают 100.
[ ] Все формулы определяют переменные.
[ ] Все DOI и URL проверены.
[ ] Указана дата доступа к нестабильным интернет-источникам.
[ ] Финальные рекомендации не противоречат findings.
[ ] Маркетинговые claims отделены от доказанных фактов.


# 31. КРИТЕРИЙ УСПЕХА

Аудит считается завершённым только если независимый инженер сможет:

1. Воспроизвести технические проверки.
2. Понять происхождение модели.
3. Установить границы применимости модели.
4. Проверить математические вычисления.
5. Увидеть риски для пациента.
6. Различить cell-level и patient-level performance.
7. Понять, почему проект получил конкретный verdict.
8. Реализовать roadmap без догадок о критериях готовности.
9. Проследить каждый значимый вывод до кода, команды или первоисточника.
10. Принять обоснованное GO/NO-GO решение.

Начинай с чтения локальных инструкций и полной инвентаризации репозитория.
Не начинай с предположения, что README корректен.
Не начинай с переписывания кода.
Сначала собери доказательства.
```

---

## Контроль качества самого мастер-промпта

- Веса `QualityScore` дают ровно `100`.
- Основные формулы содержат определения переменных.
- Учтена зависимость `PPV/NPV` от prevalence.
- Учтена кластеризация клеток внутри пациента и предметного стекла.
- Разделены cell-, slide- и patient-level выводы.
- Введены обязательные `STOP-SHIP` и safety gates.
- Reporting guidelines не представлены как сертификация модели.
- Регуляторные выводы требуют определения intended use.
- Предусмотрены четыре независимых review pass.
- Предусмотрена проверка альтернативных гипотез.
- Запрещено скрывать невыполненные проверки и выдумывать результаты.
- Требуется проверка доступности, лицензии, labels и revision модели.
- При нехватке контекстного окна работа должна продолжаться частями без
  сокращения обязательных фаз.
