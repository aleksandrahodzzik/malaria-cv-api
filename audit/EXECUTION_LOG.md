# Execution log

Дата актуального remediation run: 2026-07-29.

| Command/check | Result | Evidence |
|---|---|---|
| Baseline pytest branch coverage | PASS | 78 passed; 88.52% |
| Post-expansion pytest branch coverage | PASS | 185 passed; 98.29%; gate 95 |
| `ruff format --check src tests scripts` | PASS | 41 files formatted |
| `ruff check src tests scripts` | PASS | no issues |
| `mypy --strict src` | PASS | 26 source files |
| Manifest negative/positive tests | PASS | missing/tampered/mismatch/offline/unsafe branches |
| QC tests | PASS | crisp/blur/contrast/color/resolution branches |
| Slide aggregation tests | PASS | Wilson boundaries and route guardrails |
| Auth/rate-limit tests | PASS | 401/403/429/expiry/cardinality |
| Registry tests | PASS | sealed/tampered/synthetic prohibition/evidence scope |
| Synthetic cohort harness | PASS | 500 unique records; simulation-only classification |
| `scripts/verify_audit_math.py` | PASS | weights 100; score 52.38 |
| GitHub Actions Linux matrix | PASS | run 30463000521; Python 3.11 and 3.12 |
| Markdown/CSV consistency | PASS | re-evaluated canonical artifacts |

Точные финальные stdout/stderr и длительности находятся в
`remediation/VERIFICATION.md`.
