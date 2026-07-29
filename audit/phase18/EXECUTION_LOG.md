# Execution log — final verification

Дата: 2026-07-28. Working directory:
`C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`.

## Static quality

Command: `.\.venv\Scripts\python.exe -m ruff format --check src tests scripts`

Exit code: 0

Relevant stdout: `25 files already formatted`

Interpretation: PASS.

Command: `.\.venv\Scripts\python.exe -m ruff check src tests scripts`

Exit code: 0

Relevant stdout: `All checks passed!`

Interpretation: PASS.

Command: `.\.venv\Scripts\python.exe -m mypy src scripts`

Exit code: 0

Relevant stdout: `Success: no issues found in 20 source files`

Interpretation: PASS.

## Tests

Command: `.\.venv\Scripts\python.exe -m pytest --cov=src
--cov-report=xml --cov-report=term-missing --cov-branch --cov-fail-under=80
tests`

Exit code: 0

Duration: 16.28 s pytest-reported

Relevant stdout: `77 passed`; `Total coverage: 88.61%`

Interpretation: PASS for software contract; not model/clinical evidence.

Command: `.\.venv\Scripts\python.exe -m pip check`

Exit code: 0

Relevant stdout: `No broken requirements found.`

Interpretation: PASS in active environment.

Command: `.\.venv\Scripts\python.exe -m compileall -q src tests scripts`

Exit code: 0

Interpretation: PASS.

## Benchmark

Command: `.\.venv\Scripts\python.exe -m scripts.benchmark_api`

Exit code: 0

Duration: 11.8 s tool wall time

Relevant stdout: `status=NON_MODEL_BASELINE_ONLY`; all 600 requests HTTP 200.

Interpretation: T0/T1 VERIFIED; T2/T3 NOT EXECUTED.

## Document integrity

Master-prompt fences: 372, even.

Numbered top-level headings: 49, sequential 0–48.

CSV parsed: 23 phase CSV artifacts.

README/audit local links: PASS.

`git diff --check`: PASS.

Docker build/model smoke/external cohort: NOT EXECUTED for reasons documented
in phases 5, 11 and 14.
