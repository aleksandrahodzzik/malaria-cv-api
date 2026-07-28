# ==============================================================================
# Multi-stage non-root Dockerfile for the research classification service
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Dependencies Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install OS build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-bootstrap.txt requirements.txt constraints.txt ./

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production Python dependencies without silently changing bootstrap
# tooling. Bootstrap-tool upgrades must be reviewed and pinned separately.
RUN python -m pip install --no-cache-dir --require-hashes \
        -r requirements-bootstrap.txt && \
    python -m pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 2: Final Non-Root Minimal Runtime Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Install lightweight runtime utilities (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root application user & group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Copy application source code
COPY --chown=appuser:appgroup src/ ./src

# Set non-root execution user
USER appuser

EXPOSE 8000

# Container liveness health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# One worker is the conservative default because every worker owns a model copy.
# Increase only after measuring peak RSS and latency with the approved model.
ENTRYPOINT ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--access-logfile", "-", "--error-logfile", "-", "-b", "0.0.0.0:8000", "src.main:app"]
