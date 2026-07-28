# Literal command log

Дата: 2026-07-28
Working directory для всех команд:
`C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`

Секреты не выводились. Многословный resolver output сокращён до релевантных
строк; полный результат наблюдался в execution session.

## CMD-001 — Python launcher venv

```text
Command: py -3.12 -m venv audit\reproducibility\.work\prod-a
Duration: 1111 ms
Exit code: 101
Relevant stdout: empty
Relevant stderr:
  Unable to create process ... A specified logon session does not exist.
Interpretation:
  Windows launcher видел interpreter, но не создал процесс в managed session.
Evidence status: VERIFIED
```

## CMD-002 — direct clean venv

```text
Command: python -m venv audit\reproducibility\.work\prod-a
Duration: 18495 ms
Exit code: 0
Relevant stdout:
  Python 3.12.0
  pip 23.2.1
Relevant stderr: empty
Interpretation: fresh venv создан без изменения существующей .venv.
Evidence status: VERIFIED
```

## CMD-003 — baseline production install

```text
Command: .\audit\reproducibility\.work\prod-a\Scripts\python.exe -m pip install -r requirements.txt
Duration: 411566 ms
Exit code: 0
Relevant stdout:
  Successfully installed ... torch-2.13.0+cpu ... transformers-4.57.6
Relevant stderr:
  notice о доступном pip; upgrade не выполнялся
Interpretation: baseline production inputs разрешимы на Windows/Python 3.12.
Evidence status: VERIFIED
```

Первый sandboxed attempt этой команды завершился `Exit code: 1` через
`16862 ms` из-за `WinError 10013`; после разрешения сетевого доступа та же
команда выполнена без изменения inputs.

## CMD-004 — baseline dev install

```text
Command: .\audit\reproducibility\.work\dev-a\Scripts\python.exe -m pip install -r requirements-dev.txt
Duration: 430494 ms
Exit code: 0
Relevant stdout:
  Successfully installed ... pytest-8.4.2 ... mypy-1.20.2
Relevant stderr:
  notice о доступном pip; upgrade не выполнялся
Interpretation: baseline development inputs разрешимы.
Evidence status: VERIFIED
```

## CMD-005 — baseline quality gates

```text
Command:
  .\audit\reproducibility\.work\dev-a\Scripts\python.exe -m ruff format --check src tests
  .\audit\reproducibility\.work\dev-a\Scripts\python.exe -m ruff check src tests
  .\audit\reproducibility\.work\dev-a\Scripts\python.exe -m mypy src
  .\audit\reproducibility\.work\dev-a\Scripts\python.exe -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80 tests/
Exit code: 0 / 0 / 0 / 0
Duration: 1622 / 191 / 5560 / 31456 ms
Relevant stdout:
  15 files already formatted
  All checks passed!
  Success: no issues found in 13 source files
  28 passed; Total coverage: 84.89%
Relevant stderr: empty
Interpretation: baseline source checks проходят в clean dev venv.
Evidence status: VERIFIED
```

## CMD-006 — baseline offline install

```text
Command: .\audit\reproducibility\.work\dev-b-offline\Scripts\python.exe -m pip install --no-index --find-links .\audit\reproducibility\wheelhouse -r requirements-dev.txt
Duration: 363370 ms
Exit code: 0
Relevant stdout:
  Looking in links: local wheelhouse
  Successfully installed 60-package snapshot
Relevant stderr: empty
Interpretation: baseline graph устанавливается без package-index network.
Evidence status: VERIFIED
```

## CMD-007 — baseline snapshot comparison

```text
Command: pip freeze --all in dev-a and dev-b-offline + normalized Compare-Object
Duration: 7100 ms
Exit code: 0
Relevant stdout:
  DevA=60 DevB=60 Intersection=60 Union=60
  Jaccard=1 VersionMatch=1
Relevant stderr: empty
Interpretation: два baseline snapshots идентичны.
Evidence status: VERIFIED
```

## CMD-008 — baseline vulnerability scan

```text
Command: .\audit\reproducibility\.work\security-scanner\Scripts\python.exe -m pip_audit --path .\audit\reproducibility\.work\prod-a\Lib\site-packages --progress-spinner off
Duration: 4274 ms
Exit code: 1
Relevant stdout:
  Found 39 known vulnerabilities in 4 packages
  gunicorn 21.2.0
  pillow 10.4.0
  pip 23.2.1
  transformers 4.57.6
Relevant stderr:
  torch 2.13.0+cpu could not be audited through PyPI mapping
Interpretation: security gate failed; automatic fix не использован.
Evidence status: VERIFIED
```

## CMD-009 — candidate install

```text
Command:
  .\audit\reproducibility\.work\candidate\Scripts\python.exe -m pip install pip==26.1.2
  .\audit\reproducibility\.work\candidate\Scripts\python.exe -m pip install -r .\audit\reproducibility\candidate-requirements.txt
Duration: 435845 ms
Exit code: 0 / 0
Relevant stdout:
  Successfully installed pip-26.1.2
  Successfully installed gunicorn-22.0.0 pillow-12.3.0
  transformers-5.14.1 pytest-9.0.3 httpx2-2.7.0
Relevant stderr: empty
Interpretation: reviewed candidate graph разрешим.
Evidence status: VERIFIED
```

## CMD-010 — candidate test before torchvision

```text
Command: .\audit\reproducibility\.work\candidate\Scripts\python.exe -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80 tests/
Duration: 20360 ms
Exit code: 1
Relevant stdout:
  1 failed, 29 passed
Relevant stderr:
  AutoImageProcessor requires the Torchvision library
Interpretation:
  Major Transformers update не был принят до добавления явной совместимой
  image backend dependency.
Evidence status: VERIFIED
```

## CMD-011 — torchvision compatibility

```text
Command: .\audit\reproducibility\.work\candidate\Scripts\python.exe -m pip install torchvision==0.28.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
Duration: 11407 ms
Exit code: 0
Relevant stdout:
  torchvision 0.28.0+cpu requires torch==2.13.0
  Successfully installed torchvision-0.28.0+cpu
Relevant stderr: empty
Interpretation: resolver подтвердил точную torch/torchvision пару.
Evidence status: VERIFIED
```

## CMD-012 — remediated candidate verification

```text
Command:
  critical imports
  ruff format --check
  ruff check
  mypy
  pytest with branch coverage
  compileall
Exit code: all 0
Relevant stdout:
  vision_imports_ok 0.28.0+cpu True True
  30 passed
  Total coverage: 85.83%
Relevant stderr: empty
Interpretation: candidate проходит functional/static gates.
Evidence status: VERIFIED
```

## CMD-013 — remediated vulnerability scan

```text
Command: .\audit\reproducibility\.work\security-scanner\Scripts\python.exe -m pip_audit --path .\audit\reproducibility\.work\candidate\Lib\site-packages --progress-spinner off
Duration: 8229 ms
Exit code: 0
Relevant stdout:
  No known vulnerabilities found
Relevant stderr:
  torch and torchvision could not be audited through PyPI mapping
Interpretation: covered candidate packages clear current advisory gate.
Evidence status: VERIFIED_WITH_LIMITATION
```

## CMD-014 — combined hash-mode download negative test

```text
Command: .\audit\reproducibility\.work\candidate\Scripts\python.exe -m pip download -r requirements-bootstrap.txt -r requirements-dev.txt --dest .\audit\reproducibility\release-wheelhouse
Duration: 5400 ms
Exit code: 1
Relevant stdout: pip wheel download started
Relevant stderr:
  Hashes are required in --require-hashes mode, but they are missing from
  runtime requirements.
Interpretation:
  pip корректно распространил hash mode на все combined inputs. Bootstrap и
  runtime wheelhouse затем скачаны отдельными командами.
Evidence status: VERIFIED
```

## CMD-015 — final offline install

```text
Command:
  .\audit\reproducibility\.work\release-offline\Scripts\python.exe -m pip install --no-index --find-links .\audit\reproducibility\release-wheelhouse --require-hashes -r requirements-bootstrap.txt
  .\audit\reproducibility\.work\release-offline\Scripts\python.exe -m pip install --no-index --find-links .\audit\reproducibility\release-wheelhouse -r requirements-dev.txt
Duration: 396888 ms
Exit code: 0 / 0
Relevant stdout:
  Successfully installed pip-26.1.2
  Successfully installed final 66-package graph
Relevant stderr: empty
Interpretation: финальный graph воспроизводимо устанавливается offline.
Evidence status: VERIFIED
```

## CMD-016 — final independent gates

```text
Command:
  pip check
  critical torch/torchvision/transformers/Pillow imports
  ruff format --check src tests
  ruff check src tests
  mypy src
  pytest --cov=src --cov-report=term-missing --cov-fail-under=80 tests/
  compileall -q src tests
Duration: 44000 ms total
Exit code: all 0
Relevant stdout:
  No broken requirements found.
  imports_ok 2.13.0+cpu 0.28.0+cpu 5.14.1 12.3.0
  15 files already formatted
  All checks passed!
  Success: no issues found in 13 source files
  30 passed; Total coverage: 85.83%
Relevant stderr: empty
Interpretation: release-offline environment passes all available gates.
Evidence status: VERIFIED
```

## CMD-017 — unavailable tools

```text
Command: docker version
Status: NOT_EXECUTED
Reason: docker command not found
Impact on confidence: container build/runtime unknown
Safe next action: run CI/BuildKit smoke on Linux
```

```text
Command: make --version
Status: NOT_EXECUTED
Reason: make command not found
Impact on confidence: Make targets inspected but not locally executed
Safe next action: run on GNU Make host
```

```text
Command: Python 3.11 clean-room matrix
Status: NOT_EXECUTED
Reason: Python 3.11 interpreter not installed
Impact on confidence: local 3.11 compatibility unknown
Safe next action: execute CI 3.11 job
```
