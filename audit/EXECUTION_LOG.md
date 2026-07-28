# Журнал исполнения аудита

Дата: 2026-07-27.

## 1. Safe local checks

| Команда/проверка | Статус | Результат |
|---|---|---|
| Environment discovery | PASS | Windows, Python/pip зафиксированы |
| Repository inventory | PASS | Исходники и инфраструктура перечислены |
| `pip check` | PASS | `No broken requirements found` |
| `ruff check src tests` | PASS | `All checks passed` |
| `ruff format --check src tests` | PASS | 14 files already formatted |
| `mypy src` | PASS | 12 source files, no issues |
| `pytest --cov=src --cov-report=term-missing tests/` | PASS | 9 passed, total 74% |
| `python -m compileall src tests` | PASS | Compilation successful |
| Hugging Face cache lookup | PASS | Cache root not found |
| `pip show httpx2` / `pip show httpx` | PASS | Оба установлены; `httpx2` unused |
| Docker discovery | PASS | Executable not found |
| Make discovery | PASS | Executable not found |
| Git worktree check | FAIL | Not a Git repository |
| Direct HF API from shell | NOT EXECUTED | Network connection unavailable |

`FAIL` здесь означает обнаруженное несоответствие, а не сбой самого аудита.

## 2. External verification

Через доступный web-инструмент проверены:

- публичный model profile `trpakov`;
- официальный NIH/NLM dataset index;
- CLAIM 2024;
- TRIPOD+AI;
- PROBAST+AI;
- STARD-AI;
- FUTURE-AI;
- NIST AI RMF и SSDF;
- FDA/IMDRF GMLP;
- EU AI Act, IVDR и MDCG guidance index.

Точная страница/API malaria-модели не открылась; публичный профиль
показывает только две другие модели. Поэтому вывод сформулирован
`INFERRED/HIGH`, а не как безусловный HTTP 404.

## 3. Test interpretation

Pytest duration: 37.41 s; полный command duration около 41.6 s.

```text
9 passed
total coverage 74%
inference.py coverage 41%
```

Fixture подменяет `MalariaClassifierService.load_model`; successful analyze
использует `MagicMock`. Следовательно, тесты валидируют HTTP orchestration, но
не настоящие weights, processor, logits или labels.

## 4. Audit artifact verification

Проведено после генерации:

- все обязательные файлы присутствуют;
- внутренние README links разрешаются;
- CSV импортируются;
- 16 risk IDs и 26 evidence IDs уникальны;
- risk CSV: 16 data rows, 15 columns;
- evidence CSV: 26 data rows, 7 columns;
- RPN formula проверена для всех строк;
- Markdown code fences сбалансированы;
- PPV/NPV example пересчитан:
  `PPV=0.0876`, `NPV=0.9994`;
- production-код в ходе этой фазы не редактировался.

После обнаружения `httpx2` были обновлены technical finding, evidence matrix,
risk register и inventory. После обновления проверка повторена:
`MISSING=0`, `BROKEN_LINKS=0`, `RPN_ERRORS=0`, `FENCE_ERRORS=0`,
duplicate IDs отсутствуют.

## 5. Неисполненные проверки и причина

- Docker build/run/scan — Docker не установлен.
- Make targets — Make не установлен.
- Real-model smoke — artifact не доступен.
- Vulnerability scan — scanner не установлен; зависимости не скачивались
  дополнительно ради аудита.
- Load/soak — без модели и утверждённого hardware profile результат невалиден.
- Clinical metrics — prediction-level dataset отсутствует.
- Git diff/history — `.git` не является рабочим repository.

Ни один `NOT EXECUTED` не был заменён выдуманным результатом.
