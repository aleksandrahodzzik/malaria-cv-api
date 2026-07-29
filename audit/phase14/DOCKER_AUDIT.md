# Фаза 14 — Docker audit

## Observed

- multi-stage Python slim build;
- fixed non-root UID/GID `10001`;
- runtime OS `curl` удалён; healthcheck использует Python stdlib;
- exec-form HEALTHCHECK и CMD;
- `STOPSIGNAL SIGTERM`, Gunicorn timeout/graceful-timeout;
- один Uvicorn worker, уменьшающий неизмеренное размножение модели;
- package constraints используются при build.

## Gaps

- base image pinned tag, но не digest;
- Docker build/runtime/CVE scan: NOT EXECUTED, Docker CLI unavailable;
- no read-only filesystem/no-new-privileges/cap-drop/resource-limit evidence
  (обычно задаётся deployment manifest);
- model artifact не baked/mounted по проверенному manifest;
- no image signature/provenance attestation;
- no measured image size/startup/RSS.

Finding ID: DOCKER-001

Classification: VERIFIED

Severity: High

Confidence: 1.00

Evidence: `FROM python:3.12-slim` без digest.

Impact: rebuild может получить иной base artifact.

Recommendation: после tested rebuild зафиксировать multi-arch-compatible digest.

Acceptance criteria: Docker build, CVE scan, smoke test, digest and SBOM bound to
release provenance.
