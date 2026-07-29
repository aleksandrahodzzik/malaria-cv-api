# Repository inventory — current snapshot

Дата: 2026-07-29. Commit baseline:
`fc47dac078b88f7316595e3468447ef4a879d6f8`.

## Runtime

- Entrypoint: `src.main:app`.
- Application factory: `src.main.create_application`.
- Lifespan: model service initialization; missing model leaves readiness 503.
- Canonical API: `/api/v1`; compatibility aliases expose deprecation headers.
- UI: same-origin static research upload interface.
- User-file path: request-body middleware → multipart `UploadFile` → bounded
  bytes → Pillow decode/validation → inference service.
- External runtime call: optional Hugging Face model resolution at startup;
  production remote use requires immutable revision.

## Major artifacts

| Artifact | Exists | Current purpose/status |
|---|---|---|
| README/LICENSE/.env.example | Yes | Research contract/config/license |
| requirements/constraints/bootstrap hashes | Yes | Partial reproducibility; full hash lock absent |
| Dockerfile | Yes | Multi-stage non-root; build not executed locally |
| GitHub Actions | Yes | Python 3.11/3.12; full action SHA pinning |
| src/api/core/services/schemas/ui | Yes | Application |
| src/validation | Yes | Offline planning calculations, not model validation |
| tests | Yes | 77 mocked/software tests |
| audit phases 1–19 | Yes | Evidence, risks, roadmap, reviews |
| Approved model weights/manifest | No | STOP-SHIP |
| Project dataset/patient split manifest | No | Data validation blocked |

Detailed trees and baseline commands remain in `phase1/` and
`reproducibility/`; this file is the current canonical inventory summary.
