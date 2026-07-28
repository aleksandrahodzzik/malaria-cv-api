# 🔬 Malaria Cell Classification Microservice (`malaria-cv-api`)

[![CI Pipeline](https://github.com/aleksandrahodzzik/malaria-cv-api/actions/workflows/ci.yml/badge.svg)](https://github.com/aleksandrahodzzik/malaria-cv-api/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2%2B-EE4C2C.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Model-trpakov%2Fvit--malaria--classification-orange)](https://huggingface.co/trpakov/vit-malaria-classification)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

High-performance, production-ready MedTech REST API microservice designed for rapid microscopic blood smear cell classification (**Parasitized** vs. **Uninfected**). Built with **FastAPI**, **PyTorch**, and HuggingFace's Vision Transformer (`trpakov/vit-malaria-classification`), following strict DevSecOps and MLOps standards.

---

## 🏗️ System Architecture & Workflow

The microservice offloads heavy matrix calculations to worker threads using `asyncio.to_thread()` to prevent blocking FastAPI's async event loop under concurrent production load.

```mermaid
sequenceDiagram
    autonumber
    actor Client as 🏥 Clinical Client / App
    participant MW as ⏱️ RequestTracking Middleware
    participant API as 🚀 FastAPI Router (/analyze)
    participant Service as 🧠 MalariaClassifierService
    participant Loop as 🔄 Event Loop (asyncio.to_thread)
    participant Model as 🔬 HuggingFace ViT Model

    Client->>MW: POST /analyze (Image File Upload)
    MW->>MW: Generate X-Request-ID (UUID4)
    MW->>API: Route Request
    API->>API: Validate Content-Type & File Size
    API->>Service: Call analyze_image(bytes, filename)
    Service->>Loop: Offload PyTorch compute to ThreadPool
    Loop->>Model: Preprocess Image & Execute ViT Forward Pass
    Model-->>Loop: Raw Logits (Parasitized vs Uninfected)
    Loop-->>Service: Class Probabilities & Top Diagnosis
    Service-->>API: Return Structured Prediction Schema
    API-->>MW: HTTP 200 OK Response
    MW-->>Client: Response + Headers (X-Request-ID, X-Response-Time-Ms)
```

---

## ✨ Key Architectural Features

- **Non-Blocking Inference Engine**: Uses `asyncio.to_thread()` to run PyTorch Vision Transformer inference without stalling the async event loop.
- **FastAPI Lifespan Management**: Pre-loads model weights during application startup lifespan, preventing cold-start latency on request handling.
- **Production Observability**: Automated ASGI middleware assigning correlation request IDs (`X-Request-ID`) and tracking request latency in milliseconds (`X-Response-Time-Ms`).
- **Strict Data Contracts**: Pydantic v2 models for comprehensive input validation, error handling, and swagger schema documentation.
- **DevSecOps Containerization**: Multi-stage, non-root Docker builds running Gunicorn with Uvicorn workers.
- **Continuous Integration**: GitHub Actions automated pipeline executing `ruff` linting, `mypy` static type checking, and `pytest` with code coverage.

---

## 📁 Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline (lint, mypy, pytest)
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI initialization & Lifespan manager
│   ├── api/
│   │   ├── dependencies.py     # Dependency injection providers
│   │   └── routes.py           # /health, /ready, /analyze REST endpoints
│   ├── core/
│   │   ├── config.py           # Pydantic BaseSettings configuration
│   │   └── middleware.py       # Tracing & latency ASGI middleware
│   ├── schemas/
│   │   └── payload.py          # Pydantic payload & response validation
│   └── services/
│       └── inference.py        # Async ViT PyTorch inference service
├── tests/
│   ├── __init__.py
│   └── test_api.py             # Pytest test suite with FastAPI TestClient
├── .gitignore                  # Python, PyTorch, & ML gitignore rules
├── Dockerfile                  # Security-hardened multi-stage build
├── Makefile                    # Developer ergonomics task automation
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development & testing dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Quick Start & Developer Ergonomics

### Prerequisites
- Python `3.11+`
- Docker (optional)

### 1. Initialize Development Environment
```bash
make init
# Or manually:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 2. Run Local Development Server
```bash
make run
# Access interactive OpenAPI documentation at http://localhost:8000/docs
```

### 3. Code Quality & Unit Testing
```bash
# Run linting (ruff) & static type checking (mypy)
make lint

# Run pytest test suite with coverage
make test
```

---

## 📡 API Endpoint Reference & cURL Examples

### 1. Liveness Probe (`GET /health`)
```bash
curl -X GET "http://localhost:8000/health" -H "accept: application/json"
```
**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-07-27T18:00:00.000000+00:00"
}
```

### 2. Service Readiness Probe (`GET /ready`)
```bash
curl -X GET "http://localhost:8000/ready" -H "accept: application/json"
```
**Response (200 OK):**
```json
{
  "status": "ready",
  "model_loaded": true,
  "model_name": "trpakov/vit-malaria-classification"
}
```

### 3. Cell Image Classification (`POST /analyze`)
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/cell_sample.png;type=image/png"
```
**Response (200 OK):**
```json
{
  "filename": "cell_sample.png",
  "diagnosis": "Parasitized",
  "confidence": 0.9845,
  "probabilities": [
    {
      "label": "Parasitized",
      "confidence": 0.9845
    },
    {
      "label": "Uninfected",
      "confidence": 0.0155
    }
  ],
  "execution_time_ms": 38.42,
  "timestamp": "2026-07-27T18:00:00.000000+00:00"
}
```

---

## 🐳 Docker Deployment

### Build Container Image
```bash
make docker-build
```

### Run Container
```bash
docker run -d -p 8000:8000 --name malaria-api malaria-cv-api:latest
```

---

## 🐙 GitHub Publishing Instructions

To initialize the local Git repository and push directly to GitHub (`aleksandrahodzzik/malaria-cv-api`):

```bash
make github-push
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
