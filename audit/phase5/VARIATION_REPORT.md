# Вариационная проверка фаз 3–5

Дата: 2026-07-28

## Вариация 1 — historical model provenance

| Метод | Результат |
|---|---|
| Exact Hugging Face HTTP API | 401 |
| Exact page/files | 401 |
| Public author API | только две unrelated models |
| `huggingface_hub.HfApi` | тот же список |
| Real Transformers loader | exit 1 |
| Local cache | отсутствует |

Вывод стабилен:

```text
historical model is not publicly reproducible
```

## Вариация 2 — dependency resolver drift

Сравнение ранее сохранённого snapshot и новой установки без нового constraints:

```text
old: annotated-doc==0.0.4
new: annotated-doc==0.0.5
package-name Jaccard = 1.0
VersionMatch = 65 / 66 = 0.984848...
```

Это воспроизводимо опровергло claim о полной version repeatability во времени.

Remediation:

```text
constraints.txt
```

фиксирует все 66 наблюдаемых runtime/dev/bootstrap версий.

## Вариация 3 — две установки после constraints

```text
Snapshot A = 66
Snapshot B = 66
Only A = 0
Only B = 0
ExactMatch = true
Jaccard = 1.0
VersionMatch = 1.0
```

Обе установки созданы независимо через `python -m venv` и resolver.

## Вариация 4 — два test environments

| Environment | Dependency generation | Tests | Coverage | Ruff | Mypy | pip check |
|---|---|---:|---:|---|---|---|
| Existing project `.venv` | prior/local | 43 | 87.96% | PASS | PASS | PASS |
| Clean constrained A | fresh resolver | 43 | 87.96% | PASS | PASS | PASS |
| Clean constrained B | fresh resolver | 43 | 87.96% | PASS | PASS | PASS |

## Ограничение

`constraints.txt` фиксирует версии, но не hashes каждого platform wheel/sdist.
Следовательно:

```text
version reproducibility = VERIFIED for tested Windows/Python 3.12 runs
artifact integrity      = PARTIAL
cross-platform lock     = NOT VERIFIED
```

## Вариация 5 — GitHub Actions Python matrix

Первый remote run после push:

```text
run_id = 30371963285
Python 3.12 = SUCCESS
Python 3.11 = FAILURE at dependency installation
```

PyPI metadata подтвердил root cause:

```text
numpy==2.5.1 requires Python >=3.12
```

Это означало, что Windows/Python 3.12 snapshot нельзя безусловно применять к
Python 3.11.

Remediation:

```text
numpy==2.4.2; python_version < "3.12"
numpy==2.5.1; python_version >= "3.12"
```

`numpy 2.4.2` официально заявляет `Requires-Python >=3.11`.

Также Actions с Node 20 runtime заменены на актуальные major versions:

```text
actions/checkout@v6
actions/setup-python@v6
actions/upload-artifact@v6
```
