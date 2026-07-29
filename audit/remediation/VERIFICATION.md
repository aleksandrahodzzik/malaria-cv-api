# Verification record

Дата: 2026-07-29. Environment: Windows, Python 3.12.0.

## Final commands

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

## Not executed

- real-model inference: approved artifact absent;
- Docker T2/T3 load: approved artifact absent;
- real clinical metrics: governed validation cohort absent; simulation-only
  harness executed;
- patient-level external validation: data/protocol absent;
- distributed quota test: gateway/Redis deployment absent.
