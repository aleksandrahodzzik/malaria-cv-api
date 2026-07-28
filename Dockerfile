# ==============================================================================
# Multi-Stage Security-Hardened Dockerfile for Malaria Classification Microservice
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

COPY requirements.txt .

# Create isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install production Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

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

# Production Gunicorn + Uvicorn worker entrypoint
ENTRYPOINT ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "src.main:app"]
