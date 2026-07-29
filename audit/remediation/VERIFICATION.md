# Verification record

Дата: 2026-07-29. Environment: Windows, Python 3.12.0.

## Final commands

### Ruff

```text
Command: .venv\Scripts\python.exe -m ruff check src tests scripts
Exit code: 0
Duration: 307 ms
Relevant stdout: All checks passed!
Relevant stderr: empty
Interpretation: PASS
```

### strict mypy

```text
Command: .venv\Scripts\python.exe -m mypy --strict src
Exit code: 0
Duration: 1177 ms
Relevant stdout: Success: no issues found in 24 source files
Relevant stderr: empty
Interpretation: PASS
```

### pytest branch coverage

```text
Command: .venv\Scripts\python.exe -m pytest --cov=src --cov-branch --cov-report=term-missing
Exit code: 0
Duration: 28869 ms
Relevant stdout: 163 passed; TOTAL 98.11%; required 95.0% reached
Relevant stderr: empty
Interpretation: PASS
```

### Dependency consistency

```text
Command: .venv\Scripts\python.exe -m pip check
Exit code: 0
Duration: 1041 ms
Relevant stdout: No broken requirements found.
Relevant stderr: empty
Interpretation: PASS
```

### Compilation

```text
Command: .venv\Scripts\python.exe -m compileall -q src tests scripts
Exit code: 0
Duration: 211 ms
Relevant stdout: empty
Relevant stderr: empty
Interpretation: PASS
```

### Audit mathematics

```text
Command: .venv\Scripts\python.exe scripts/verify_audit_math.py
Exit code: 0
Duration: 228 ms
Relevant stdout: status PASS; weights 100; quality score 51.02
Relevant stderr: empty
Interpretation: PASS
```

Variation: первый прямой запуск выявил `ModuleNotFoundError: src`; entrypoint был
исправлен и повторно проверен. Модульный и прямой способы теперь согласованы.

### Diff integrity

```text
Command: git diff --check
Exit code: 0
Duration: 131 ms
Relevant stdout: empty
Relevant stderr: LF/CRLF working-copy notice only
Interpretation: PASS
```

### Audit artifact formats

```text
Command: Import-Csv for every audit/**/*.csv; ConvertFrom-Json for model_manifest.example.json
Exit code: 0
Relevant stdout: CSV_OK count=32; JSON_OK
Relevant stderr: empty
Interpretation: PASS
```

## Not executed

- real-model inference: approved artifact absent;
- Docker T2/T3 load: approved artifact absent;
- clinical metrics: validation cohort absent;
- patient-level external validation: data/protocol absent;
- distributed quota test: gateway/Redis deployment absent.
