# Паспорт среды воспроизводимости

Дата: 2026-07-28
Часовой пояс: Europe/Warsaw
Project root: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`
Git branch: `main`
Git HEAD: `09c24d74e9c87868d6806d25aba85b58bca0e522`
Working tree: dirty; существующие изменения пользователя сохранены

## Фактическая среда

| Field | Value | Evidence status | Notes |
|---|---|---|---|
| OS | Microsoft Windows 10.0.26200 | VERIFIED | `.NET RuntimeInformation` |
| Architecture | x64 | VERIFIED | OS и process x64 |
| CPU | AMD Ryzen 5 7535HS with Radeon Graphics | VERIFIED | registry |
| Logical processors | 12 | VERIFIED | environment |
| Total RAM | 33,049,239,552 bytes (30.78 GiB) | VERIFIED | `Microsoft.VisualBasic.Devices.ComputerInfo` |
| Available RAM | 14,889,959,424 bytes (13.87 GiB) | VERIFIED | тот же probe |
| Discrete GPU | UNKNOWN | UNKNOWN | CIM access denied; `nvidia-smi` отсутствует |
| Python | 3.12.0 | VERIFIED | system и clean venv |
| Python 3.11 | NOT_EXECUTED | UNKNOWN | interpreter отсутствует локально |
| Initial clean pip | 23.2.1 | VERIFIED | новый `venv` |
| Final pinned pip | 26.1.2 | VERIFIED | hash-verified bootstrap |
| Active venv at baseline | none | VERIFIED | `VIRTUAL_ENV` пуст |
| Node | 24.15.0 | VERIFIED | `node --version` |
| Docker | NOT_EXECUTED | UNKNOWN | команда отсутствует |
| GNU Make | NOT_EXECUTED | UNKNOWN | команда отсутствует |
| Git | 2.54.0.windows.1 | VERIFIED | `git --version` |

## Safe environment allowlist

| Variable | State |
|---|---|
| `VIRTUAL_ENV` | unset |
| `PYTHONPATH` | unset |
| `PIP_INDEX_URL` | unset |
| `PIP_EXTRA_INDEX_URL` | unset |
| `HTTP_PROXY` | unset |
| `HTTPS_PROXY` | unset |
| `NO_PROXY` | unset |

Полный environment dump не выполнялся. Секреты не читались и не выводились.

## Version alignment

| Source | Declared Python |
|---|---|
| local system | 3.12.0 |
| Ruff target | 3.11 |
| Mypy target | 3.11 |
| Docker base | 3.11 |
| CI matrix | 3.11, 3.12 |
| README | 3.11, 3.12 |

Вывод: Python 3.12 подтверждён локально. Python 3.11 заявлен согласованно в
Docker/CI, но локальный clean-room прогон для него не выполнен.
