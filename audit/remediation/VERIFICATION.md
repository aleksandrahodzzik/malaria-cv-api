# Verification record

Дата: 2026-07-29. Environment: Windows, Python 3.12.0.

## Final commands

### Ruff formatting

```text
Command: .venv\Scripts\python.exe -m ruff format --check src tests scripts
Exit code: 0
Relevant stdout: 41 files already formatted
Relevant stderr: empty
Interpretation: PASS
```

### Ruff

```text
Command: .venv\Scripts\python.exe -m ruff check src tests scripts
Exit code: 0
Duration: 301 ms
Relevant stdout: All checks passed!
Relevant stderr: empty
Interpretation: PASS
```

### strict mypy

```text
Command: .venv\Scripts\python.exe -m mypy --strict src
Exit code: 0
Duration: 1237 ms
Relevant stdout: Success: no issues found in 26 source files
Relevant stderr: empty
Interpretation: PASS
```

### pytest branch coverage

```text
Command: .venv\Scripts\python.exe -m pytest --cov=src --cov-branch --cov-report=term-missing
Exit code: 0
Duration: 28354 ms
Relevant stdout: 185 passed; TOTAL 98.29%; required 95.0% reached
Relevant stderr: empty
Interpretation: PASS
```

### Dependency consistency

```text
Command: .venv\Scripts\python.exe -m pip check
Exit code: 0
Duration: 1102 ms
Relevant stdout: No broken requirements found.
Relevant stderr: empty
Interpretation: PASS
```

### Compilation

```text
Command: .venv\Scripts\python.exe -m compileall -q src tests scripts
Exit code: 0
Duration: 207 ms
Relevant stdout: empty
Relevant stderr: empty
Interpretation: PASS
```

### Audit mathematics

```text
Command: .venv\Scripts\python.exe scripts/verify_audit_math.py
Exit code: 0
Duration: 196 ms
Relevant stdout: status PASS; weights 100; quality score 52.38
Relevant stderr: empty
Interpretation: PASS
```

Variation: первый прямой запуск выявил `ModuleNotFoundError: src`; entrypoint был
исправлен и повторно проверен. Модульный и прямой способы теперь согласованы.

### Diff integrity

```text
Command: git diff --check
Exit code: 0
Duration: 102 ms
Relevant stdout: empty
Relevant stderr: LF/CRLF working-copy notice only
Interpretation: PASS
```

### Audit artifact formats

```text
Command: Import-Csv for every audit/**/*.csv; ConvertFrom-Json for model_manifest.example.json
Exit code: 0
Relevant stdout: CSV_OK count=33; JSON_OK
Relevant stderr: empty
Interpretation: PASS
```

### Simulation cohort harness

```text
Command: .venv\Scripts\python.exe scripts/evaluate_clinical_cohort.py
Exit code: 0
Duration: 471 ms
Relevant stdout: status=PASS patients=500 scope=SIMULATION_ONLY_NOT_EXTERNAL_VALIDATION external_eligible=False
Relevant stderr: empty
Interpretation: PASS for software/statistical pipeline; NOT clinical evidence
```

Variation: первый expansion `git diff --check` обнаружил два Markdown trailing
spaces. Они удалены; повторный запуск завершился с exit code 0.

Variation: первый GitHub Actions run для expansion остановился на `Check
Formatting`. Локальный запуск воспроизвёл расхождение, `ruff format` исправил
10 файлов, после чего format check, Ruff, mypy и все 185 тестов прошли повторно.

Variation: второй run прошёл formatting/Ruff/mypy, но pytest завершился ошибкой
на Linux 3.11 и 3.12. Проверка platform-dependent branches выявила, что
`Path("C:\\model").is_absolute()` истинно на Windows и ложно на Linux. Trust
policy, registry classification и readiness redaction дополнены явной
`PureWindowsPath`-проверкой; точная CI-команда воспроизведена локально с
pytest 9.0.3 и pytest-asyncio 1.3.0.

### GitHub Actions Linux matrix

```text
Run: 30463000521
Commit: 28ad3483067af9a6025f9b575f46a6c0cd9b92e5
Platforms: ubuntu-latest; Python 3.11 and 3.12
Status: completed
Conclusion: success
URL: https://github.com/aleksandrahodzzik/malaria-cv-api/actions/runs/30463000521
Interpretation: PASS
```

## Not executed

- real-model inference: approved artifact absent;
- Docker T2/T3 load: approved artifact absent;
- real clinical metrics: governed validation cohort absent; simulation-only
  harness executed;
- patient-level external validation: data/protocol absent;
- distributed quota test: gateway/Redis deployment absent.
