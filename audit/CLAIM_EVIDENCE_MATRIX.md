# Claim-to-evidence matrix — canonical summary

| Claim | Verdict | Evidence |
|---|---|---|
| Production-ready | CONTRADICTED | G0/G1 fail; model absent; T2/T3 not executed |
| Clinical prediction/diagnosis | CONTRADICTED | cell-only task; no patient validation |
| Non-blocking event loop | PARTIALLY SUPPORTED | compute offloaded; saturation/scaling still bounded/unknown |
| Strict image validation | PARTIALLY SUPPORTED | transport/format/pixel checks; no biological QC/OOD |
| Prevents request cold start | PARTIALLY SUPPORTED | lifespan attempts preload; artifact unavailable |
| Microsecond latency | UNSUPPORTED/MISLEADING | header has millisecond units/precision; no microsecond service guarantee |
| Security-hardened | PARTIALLY SUPPORTED | strong input/log/CI controls; auth/global quotas/signatures absent |
| Comprehensive tests | PARTIALLY SUPPORTED | strong software tests; no real-model/clinical/Docker E2E |

Полная извлечённая матрица и reproduction:
`phase3/CLAIM_TO_EVIDENCE_MATRIX.md` и `.csv`.
