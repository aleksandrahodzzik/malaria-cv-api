# Execution log — phases 3–5

Дата: 2026-07-28
Shell: PowerShell
Workspace: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`.

## HF exact endpoint matrix

Command:

```text
curl.exe -sS -L -o NUL -w %{http_code} --max-time 30 <URL>
```

Exit code: `0` для каждого HTTP-запроса.

Relevant stdout:

```text
api/models/trpakov/vit-malaria-classification        HTTP 401  950 ms
trpakov/vit-malaria-classification                   HTTP 401  321 ms
resolve/main/config.json                             HTTP 401  408 ms
resolve/main/preprocessor_config.json                HTTP 401  439 ms
resolve/main/model.safetensors                       HTTP 401  188 ms
resolve/main/pytorch_model.bin                       HTTP 401  610 ms
resolve/main/README.md                               HTTP 401  260 ms
resolve/main/.gitattributes                          HTTP 401  213 ms
api/models?author=trpakov&limit=100&full=true        HTTP 200  196 ms
```

Relevant stderr: none.

Interpretation: exact model is not publicly reproducible; author public API
works and does not list it.

## HF client variation

Command:

```text
HfApi().list_models(author="trpakov", limit=100)
```

Exit code: `0`.

Relevant stdout:

```text
['trpakov/vit-face-expression', 'trpakov/vit-pneumonia']
```

Interpretation: independent official-client variation confirms public API list.

## Real model loader

Command:

```text
MalariaClassifierService(
  "trpakov/vit-malaria-classification"
).load_model()
```

Exit code: `1`.
Duration: `9731 ms`.

Relevant stderr:

```text
RepositoryNotFoundError
401 Unauthorized
preprocessor_config.json
RuntimeError: Model initialization failure
```

Interpretation: historical startup path fails before weights download.

## Local full gate

Command:

```text
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80 -q
python -m ruff format --check .
python -m ruff check .
python -m mypy src
python -m compileall -q src tests
node --check src/ui/app.js
python -m pip check
```

Exit code: `0`.
Duration pytest/combined primary gate: `38206 ms`.

Relevant stdout:

```text
43 passed
coverage 87.96%
Ruff PASS
Mypy PASS
compileall PASS
node PASS
pip check PASS
```

## Clean-room A

Command:

```text
python -m venv audit/phase5/.verification-venv
python -m pip install --require-hashes -r requirements-bootstrap.txt
python -m pip install -r requirements-dev.txt
```

Venv exit: `0`, `15360 ms`.

Первая sandbox network-попытка:

```text
ExitCode: 1
DurationMs: 8580
WinError 10013
```

Она не интерпретировалась как dependency failure.

Повтор с разрешённым network:

```text
BootstrapExit: 0
DependencyExit: 0
DurationMs: 515917
```

Quality gate:

```text
43 passed
coverage 87.96%
all static/import/pip gates PASS
DurationMs: 52182
```

## Resolver drift observation

Comparison:

```text
previous snapshot: annotated-doc==0.0.4
new snapshot:      annotated-doc==0.0.5
VersionMatch:      65/66 = 0.984848...
```

Interpretation: transitive version drift was real.

Remediation: added `constraints.txt`.

## Clean-room B after constraints

Command:

```text
python -m venv audit/phase5/.verification-venv-b
python -m pip install --require-hashes -r requirements-bootstrap.txt
python -m pip install -r requirements-dev.txt
```

Exit code: `0`.

Snapshot comparison:

```text
SnapshotA=66
SnapshotB=66
OnlyA=0
OnlyB=0
ExactMatch=True
```

Independent gate:

```text
43 passed
coverage 87.96%
Ruff PASS
Mypy PASS
pip check PASS
DurationMs: 43880
```

## Cleanup

Command:

```text
Resolve-Path and verify both targets are children of audit/phase5
Remove-Item -LiteralPath <verified-target> -Recurse -Force
```

Exit code: `0`.
Duration: `42500 ms`.

Removed:

```text
audit/phase5/.verification-venv
audit/phase5/.verification-venv-b
```

Snapshots, reports and evidence were retained.

## First remote CI run

Run:

```text
https://github.com/aleksandrahodzzik/malaria-cv-api/actions/runs/30371963285
```

Result:

```text
overall: failure
Python 3.12: success
Python 3.11: dependency installation failure
```

Public log download required repository admin authentication and returned
`403`, но job metadata локализовала failure в install step. Независимая
проверка official PyPI JSON API показала:

```text
numpy/2.5.1 requires_python >=3.12
numpy/2.4.2 requires_python >=3.11
```

Remediation: Python-version markers в `constraints.txt`.
