# Итоговое решение по фазе воспроизводимости

Дата: 2026-07-28
Область проверки: Windows x64, CPython 3.12, backend, research-only UI,
production- и development-зависимости.

## Решения по сценариям

| Сценарий | Решение | Основание |
|---|---|---|
| Локальная разработка без реальной модели | **CONDITIONAL GO** | Два constrained snapshot совпали 66/66; 43 теста; lint, type-check и clean install прошли |
| Исследовательская демонстрация на синтетических/нечувствительных данных | **CONDITIONAL GO** | API и UI проверены, но вывод модели не воспроизведён |
| Публичный production API | **NO-GO** | Не проверены Docker/Linux/Python 3.11; нет полного enforced hash lock, rate limiting и доказанного model artifact |
| Air-gapped deployment | **NO-GO** | Dependency wheelhouse проверен только для Windows/Python 3.12 и не содержит модели |
| Клиническое применение | **NO-GO** | Отсутствуют утверждённое intended use, provenance модели, patient-level external validation, калибровка и clinical risk controls |

## Подтверждённые критерии

- `VERIFIED`: production- и dev-зависимости разрешаются в чистом окружении.
- `VERIFIED`: финальный граф повторён в отдельном полностью offline-окружении.
- `VERIFIED`: 66 из 66 package/version записей совпадают;
  `Jaccard = 1.0`, `VersionMatch = 1.0`.
- `VERIFIED`: 43 теста прошли, покрытие составило 87.96%.
- `VERIFIED`: после обнаруженного transitive drift две constrained-установки
  дали exact 66/66 package-version match.
- `VERIFIED`: Ruff, Mypy strict, `compileall`, `pip check` и JS syntax check прошли.
- `VERIFIED`: для пакетов, распознанных advisory-источником `pip-audit`,
  известные уязвимости не обнаружены.
- `UNKNOWN`: уязвимости `torch==2.13.0+cpu` и
  `torchvision==0.28.0+cpu`, потому что эти версии не сопоставлены
  сканером с PyPI advisory records.

## Блокирующие критерии выхода

Решение для публичного production может быть пересмотрено только после:

1. Воспроизводимого Docker/Linux build и runtime smoke test.
2. Проверки заявленной минимальной версии Python, включая 3.11.
3. Полного platform-specific hash lock для транзитивного графа.
4. Поставки модели как версионированного, хэшированного и лицензированного
   артефакта с запрещённым неявным сетевым fallback.
5. Нагрузочных тестов и resource limits с доказанными SLO.
6. Rate limiting, authentication/authorization для непубличного workflow,
   audit logging и операционного runbook.
7. Независимой model/data/clinical validation для любого медицинского
   утверждения.

## Ссылки на доказательства

- [COMMAND_LOG.md](COMMAND_LOG.md)
- [CLEAN_INSTALL_MATRIX.md](CLEAN_INSTALL_MATRIX.md)
- [VULNERABILITY_REPORT.md](VULNERABILITY_REPORT.md)
- [OFFLINE_READINESS.md](OFFLINE_READINESS.md)
- [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md)
- [SBOM.cdx.json](SBOM.cdx.json)
- [WHEELHOUSE_MANIFEST.sha256](WHEELHOUSE_MANIFEST.sha256)
