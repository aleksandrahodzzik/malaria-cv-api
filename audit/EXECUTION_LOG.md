# Execution log

Дата актуального remediation run: 2026-07-29.

| Command/check | Result | Evidence |
|---|---|---|
| Baseline pytest branch coverage | PASS | 78 passed; 88.52% |
| Post-remediation pytest branch coverage | PASS | 163 passed; 98.11%; gate 95 |
| `ruff check src tests scripts` | PASS | no issues |
| `mypy --strict src` | PASS | 24 source files |
| Manifest negative/positive tests | PASS | missing/tampered/mismatch/offline/unsafe branches |
| QC tests | PASS | crisp/blur/contrast/color/resolution branches |
| Slide aggregation tests | PASS | Wilson boundaries and route guardrails |
| Auth/rate-limit tests | PASS | 401/403/429/expiry/cardinality |
| `scripts/verify_audit_math.py` | PASS | weights 100; score 51.02 |
| Markdown/CSV consistency | PASS | re-evaluated canonical artifacts |

Точные финальные stdout/stderr и длительности находятся в
`remediation/VERIFICATION.md`.
