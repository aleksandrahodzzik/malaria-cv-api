# Implementation report

Дата: 2026-07-28

## Реализовано

1. Добавлен ранний ASGI transport limit для `/analyze` и
   `/api/v1/analyze`; он работает до multipart parsing, проверяет
   `Content-Length` и считает streamed body без заголовка.
2. Early 413 сохраняет stable error envelope и request ID.
3. UI блокирует file input, remove и drop-zone на время активного запроса,
   исключая рассинхронизацию результата и выбранного файла.
4. Добавлена доступная семантика `aria-disabled`.
5. Добавлен hash-verified bootstrap `pip==26.1.2`.
6. Удалён floating `pip install --upgrade pip` из Makefile, Docker и CI.
7. После отдельного candidate validation обновлены vulnerable dependencies.
8. Добавлен обязательный `torchvision` CPU pin для Transformers 5.
9. TestClient переведён на `httpx2`; deprecation warning исчез.
10. Добавлены два transport-limit теста.
11. После обнаруженного resolver drift добавлен полный version constraints
    snapshot для 66 runtime/dev/bootstrap packages.
12. Две независимые constrained-установки дали exact `66/66` match.

## Верификация

```text
Tests: 43 passed
Coverage: 87.96%
Ruff format: PASS
Ruff lint: PASS
Mypy strict: PASS
pip check: PASS
compileall: PASS
node --check: PASS
Final constrained dependency snapshots: 66 == 66
Jaccard: 1.0
VersionMatch: 1.0
pip-audit: no known vulnerabilities in covered packages
```

## Не заявляется

- Docker build не выполнен;
- Python 3.11 local run не выполнен;
- real model не загружался;
- torch/torchvision не покрыты выбранным advisory source;
- clinical validity не доказана;
- hash-verified cross-platform lock ещё не создан; version constraints есть.
