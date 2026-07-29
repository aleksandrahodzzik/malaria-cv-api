# CI hardening status

| Control | Status |
|---|---|
| Minimum permissions | VERIFIED |
| Full SHA action pinning | VERIFIED |
| Persisted checkout credentials disabled | VERIFIED |
| Job timeout/concurrency | VERIFIED |
| Python 3.11/3.12 matrix | VERIFIED in previous run |
| Dependency hash lock | PARTIAL |
| Secret scan | ABSENT |
| SAST/dependency audit gating | PARTIAL |
| Container build/scan | ABSENT |
| SBOM attestation/signing | ABSENT |
| Model artifact smoke | BLOCKED |

SHA updates должны выполняться отдельным reviewed change с проверкой upstream
release/tag и commit provenance.
