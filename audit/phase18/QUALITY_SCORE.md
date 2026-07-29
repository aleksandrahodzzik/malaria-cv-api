# Quality score — evidence snapshot

Дата: 2026-07-28. Шкала категории 0–5. Итог:
`sum(weight_i * score_i / 5)`.

| Category | Weight | Score | Contribution | Evidence |
|---|---:|---:|---:|---|
| Clinical/model evidence | 25 | 0.0 | 0.0 | Approved model/external validation absent |
| Data quality/governance | 15 | 0.5 | 1.5 | Datasheet/gates designed; project dataset unavailable |
| Software correctness | 12 | 4.0 | 9.6 | Typed API, validation, bounded concurrency, tests |
| Security/privacy | 12 | 2.5 | 6.0 | Strong input/log/CI controls; no auth/edge limits |
| Reliability/performance | 10 | 2.0 | 4.0 | T0/T1 baseline; no real model/Docker/soak |
| MLOps/reproducibility | 10 | 2.0 | 4.0 | constraints/SBOM; model/hash lock/base digest missing |
| Testing/CI | 8 | 4.0 | 6.4 | Unit/API/type/CI; real-model/E2E absent |
| Documentation/regulatory readiness | 8 | 3.0 | 4.8 | Extensive audit; no controlled QMS/regulatory file |
| **Total** | **100** |  | **36.3/100** | Safety gates override arithmetic |

Score не является сертификацией. Категории не взаимозаменяемы: software/Docker
не компенсируют отсутствие clinical evidence.
