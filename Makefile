# ==============================================================================
# Makefile for Malaria Cell Classification Microservice (malaria-cv-api)
# ==============================================================================

PYTHON ?= python
VENV_DIR ?= .venv
IMAGE_NAME ?= malaria-cv-api
IMAGE_TAG ?= latest
GITHUB_REPO ?= https://github.com/aleksandrahodzzik/malaria-cv-api.git

ifeq ($(OS),Windows_NT)
VENV_PYTHON := $(VENV_DIR)/Scripts/python.exe
else
VENV_PYTHON := $(VENV_DIR)/bin/python
endif

.PHONY: help init run test lint docker-build github-push clean

help: ## Show this help menu
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Initialize virtual environment and install development dependencies
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"
	@echo "Installing development dependencies..."
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt
	@echo "Initialization complete!"

run: ## Run local Uvicorn development server
	$(VENV_PYTHON) -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Execute pytest test suite with coverage report
	$(VENV_PYTHON) -m pytest --cov=src --cov-report=term-missing --cov-report=html tests/

lint: ## Run code linters (ruff) and type checker (mypy)
	$(VENV_PYTHON) -m ruff check src tests
	$(VENV_PYTHON) -m mypy src

docker-build: ## Build security-hardened Docker image
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

github-push: ## Initialize local git repo, commit code, and push to GitHub repository
	git init
	git branch -M main
	git add .
	git commit -m "feat: initial release of production Malaria Cell Classification Microservice"
	git remote remove origin || true
	git remote add origin $(GITHUB_REPO)
	git push -u origin main

clean: ## Clean cache files, pyc, pytest, and venv artifacts
ifeq ($(OS),Windows_NT)
	powershell -NoProfile -Command "Get-ChildItem -Path src,tests -Directory -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force; Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache,htmlcov,.mypy_cache,.ruff_cache; Remove-Item -Force -ErrorAction SilentlyContinue .coverage"
else
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache .ruff_cache __pycache__ src/__pycache__ src/*/__pycache__ tests/__pycache__
endif
