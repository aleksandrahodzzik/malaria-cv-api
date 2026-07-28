# Дерево репозитория

## 1. Полная статистика baseline

| Метрика | Значение |
|---|---:|
| Directories | 3 452 |
| Files | 32 124 |
| Total bytes | 1 024 953 056 |
| Git internal files | 75 |
| Git internal bytes | 140 931 |
| `.venv` files | 31 983 |
| `.venv` bytes | 931 789 989 |
| Project cache files | 27 |
| Project cache bytes | 92 762 613 |
| Project-controlled files без Git/cache/venv | 39 |
| Project-controlled bytes | 259 523 |
| Model/binary ML artifacts | 0 |

Virtual environment составляет приблизительно 90.9% размера workspace.
Project cache почти полностью определяется `.mypy_cache/3.12/cache.db`
размером около 92.6 MB.

## 2. Project-controlled tree до реализации

```text
.
├── .agents/                         # пустой каталог
├── .github/
│   └── workflows/
│       └── ci.yml
├── PROMPTS/
│   ├── MASTER_AUDIT_EXECUTION_ORCHESTRATOR_RU.md
│   ├── MASTER_AUDIT_PROMPT_RU.md
│   └── MASTER_REPOSITORY_UI_BACKEND_AUDIT_RU.md
├── audit/
│   ├── phase1/
│   │   ├── README.md
│   │   ├── REPOSITORY_TREE.md
│   │   ├── ARTIFACT_INVENTORY.md
│   │   ├── ARCHITECTURE_MAP.md
│   │   ├── UI_BACKEND_FUNCTIONAL_AUDIT.md
│   │   └── FEATURE_BACKLOG.csv
│   ├── CLINICAL_REGULATORY_AUDIT.md
│   ├── DEVELOPMENT_ROADMAP.md
│   ├── EVIDENCE_MATRIX.csv
│   ├── EXECUTION_LOG.md
│   ├── EXECUTIVE_SUMMARY.md
│   ├── FINAL_GO_NO_GO.md
│   ├── MODEL_DATA_STATISTICAL_AUDIT.md
│   ├── README.md
│   ├── REPOSITORY_INVENTORY.md
│   ├── RISK_REGISTER.csv
│   ├── SECURITY_RELIABILITY_AUDIT.md
│   ├── SOURCES.md
│   └── TECHNICAL_AUDIT.md
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── middleware.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── payload.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── inference.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .coverage
├── .dockerignore
├── .gitignore
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── requirements-dev.txt
└── requirements.txt
```

## 3. Скрытые и generated деревья

```text
.git/
├── HEAD, config, index, description
├── hooks/                           # стандартные sample hooks
├── info/
├── logs/
├── objects/                         # 49 object files baseline
└── refs/

.venv/
├── Include/
├── Lib/site-packages/               # Python dependencies
├── Scripts/                         # python/pip/ruff/mypy/pytest
└── pyvenv.cfg

.mypy_cache/
└── 3.12/                            # type-analysis cache, включая cache.db

.pytest_cache/
└── v/cache/

.ruff_cache/
└── 0.16.0/
```

Все 31 983 файла `.venv` и Git objects были учтены в количестве и размере.
Побайтовый перечень не включён в отчёт, потому что это generated/internal
content, не являющийся архитектурой проекта; source-controlled paths
перечислены полностью.

## 4. Крупнейшие файлы

| Path | Bytes | Класс |
|---|---:|---|
| `.venv/Lib/site-packages/torch/lib/torch_cpu.dll` | 305 081 856 | generated dependency |
| `.mypy_cache/3.12/cache.db` | 92 647 424 | generated cache |
| `.venv/Scripts/ruff.exe` | 32 211 456 | generated tool |
| `.venv/Lib/site-packages/torch/lib/torch_cpu.lib` | 29 242 954 | generated dependency |
| `.venv/.../numpy.libs/...openblas...dll` | 20 405 760 | generated dependency |

## 5. ML artifacts и cache

- Repository model files: `0`.
- `%USERPROFILE%\.cache\huggingface`: не обнаружен.
- `%LOCALAPPDATA%\huggingface`: не обнаружен.
- Workspace `.cache/huggingface`: не обнаружен.
- `models/`, `*.safetensors`, `*.pt`, `*.onnx`: не обнаружены.

Следствие: runtime полностью зависит от внешнего `from_pretrained`, если
model identifier доступен.
