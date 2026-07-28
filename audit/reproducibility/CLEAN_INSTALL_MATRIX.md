# Clean install matrix

Дата: 2026-07-28

| Run | Python | Input | Network | Result | `pip check` | Tests |
|---|---:|---|---|---|---|---|
| CR-PROD-01 | 3.12.0 | baseline production | online | PASS | PASS | import smoke PASS |
| CR-DEV-01 | 3.12.0 | baseline development | online | PASS | PASS | 28/28 PASS |
| CR-REPEAT-01 | 3.12.0 | baseline development | offline wheelhouse | PASS | PASS | 30/30 after code changes |
| SEC-CANDIDATE-01 | 3.12.0 | remediated candidate | online | PASS after adding torchvision | PASS | 30/30 PASS |
| CR-RELEASE-OFFLINE-01 | 3.12.0 | final project inputs | fully offline | PASS | PASS | 30/30 PASS |
| CR-PY311-01 | unavailable | final project inputs | n/a | NOT_EXECUTED | NOT_EXECUTED | NOT_EXECUTED |
| CR-DOCKER-01 | unavailable | Dockerfile | n/a | NOT_EXECUTED | NOT_EXECUTED | NOT_EXECUTED |

## Repeatability

Сравнение `SEC-CANDIDATE-01` и `CR-RELEASE-OFFLINE-01`:

```text
|S_A| = 66
|S_B| = 66
|S_A intersection S_B| = 66
|S_A union S_B| = 66

Jaccard(A,B) = 66 / 66 = 1.0
VersionMatch(A,B) = 66 / 66 = 1.0
```

Оба набора используют Python 3.12/x64/Windows. Это доказывает повторяемость
для данной platform tuple на дату аудита, но не долгосрочную cross-platform
повторяемость: runtime transitive lock с hashes пока отсутствует.

## Final quality gates

| Gate | Result |
|---|---|
| critical ML imports | PASS |
| `pip check` | PASS |
| Ruff format | PASS |
| Ruff lint | PASS |
| strict Mypy | PASS |
| pytest | 30 passed |
| branch coverage | 85.83% |
| compileall | PASS |
| JavaScript syntax | PASS |
| vulnerability scan | PASS with torch/torchvision coverage limitation |
