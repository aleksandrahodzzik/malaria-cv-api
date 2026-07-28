# Reproducibility findings

> Update 2026-07-28: повторная установка обнаружила drift
> `annotated-doc 0.0.4 -> 0.0.5`. Добавлен `constraints.txt`; две последующие
> независимые установки дали exact `66/66` match. Подробности:
> [`../phase5/VARIATION_REPORT.md`](../phase5/VARIATION_REPORT.md).

Итоговый статус: `PARTIALLY_REPRODUCIBLE`

## REP-001

Finding ID: REP-001
Classification: VERIFIED
Severity: HIGH
Confidence: HIGH
Evidence: два независимых финальных snapshot по 66 пакетов
Reproduction: online candidate и offline clean install
Impact: Windows/Python 3.12 graph воспроизводится на дату аудита
Root cause: exact direct pins и стабильный resolver result
Recommendation: сохранить lock-generation pipeline
Acceptance criteria: cross-platform hashed lock и CI freshness gate

## REP-002

Finding ID: REP-002
Classification: OBSERVED
Severity: HIGH
Confidence: HIGH
Evidence: runtime transitive versions отсутствуют в requirements inputs
Reproduction: сравнить direct inputs с `pip freeze --all`
Impact: будущий resolver может выбрать другой transitive graph
Root cause: exact direct pins ошибочно заменяли полный lock
Recommendation: генерировать отдельные Linux/Windows locks с hashes
Acceptance criteria: clean install с `--require-hashes` для всего graph

## REP-003

Finding ID: REP-003
Classification: VERIFIED
Severity: HIGH
Confidence: HIGH
Evidence: baseline scanner exit 1; final candidate exit 0
Reproduction: см. `VULNERABILITY_REPORT.md`
Impact: уменьшен известный supply-chain risk для image/model processing
Root cause: устаревшие direct pins
Recommendation: CI advisory gate с reviewed exceptions
Acceptance criteria: scanner exit 0 или documented time-bound waiver

## REP-004

Finding ID: REP-004
Classification: UNKNOWN
Severity: MEDIUM
Confidence: HIGH
Evidence: Docker и Python 3.11 отсутствуют локально
Reproduction: команды помечены `NOT_EXECUTED`
Impact: Linux container parity не доказана
Root cause: недоступность инструментов в audit host
Recommendation: выполнить clean matrix в GitHub Actions/BuildKit
Acceptance criteria: Python 3.11/3.12 + Docker build/smoke PASS

## REP-005

Finding ID: REP-005
Classification: UNKNOWN
Severity: CRITICAL
Confidence: HIGH
Evidence: approved model artifact отсутствует
Reproduction: default `/ready` возвращает 503
Impact: offline clinical/model runtime и real inference не доказаны
Root cause: fail-closed model configuration
Recommendation: artifact-backed release gate
Acceptance criteria: checksum/license/model contract + fixed fixture smoke
