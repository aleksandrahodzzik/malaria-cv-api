# Offline readiness

Дата: 2026-07-28

## Проверенный scope

Для Windows x64 + CPython 3.12 сформирован локальный wheelhouse:

- 66 wheel-файлов;
- 207,935,795 bytes;
- каждый файл получил SHA-256;
- bootstrap `pip` установлен offline с `--require-hashes`;
- весь dev/runtime graph установлен с `--no-index`;
- quality gates выполнены в offline-окружении.

## Математическая оценка

```text
OfflineReadiness =
  0.25 * DependencyAvailability
  + 0.25 * ModelAvailability
  + 0.20 * BuildIndependence
  + 0.15 * RuntimeNoEgress
  + 0.15 * IntegrityVerification
```

| Component | Score | Evidence |
|---|---:|---|
| DependencyAvailability | 1.00 | final Windows wheelhouse установлен offline |
| ModelAvailability | 0.00 | approved model artifact отсутствует |
| BuildIndependence | 0.50 | Python install доказан; Docker build не выполнен |
| RuntimeNoEgress | 0.75 | UI local; local-only model mode есть, но не проверен с artifact |
| IntegrityVerification | 0.35 | bootstrap hash + wheel manifest; полного enforced lock нет |

```text
OfflineReadiness = 0.25 + 0 + 0.10 + 0.1125 + 0.0525 = 0.515
```

Итог: `0.515 / 1.0`, статус `PARTIAL`.

Это не air-gapped release: wheelhouse platform-specific, модель отсутствует,
Linux/Python 3.11 bundle и Docker image не проверены.

После проверки временный wheelhouse и тестовые виртуальные окружения удалены,
чтобы не сохранять около 208 MB бинарных пакетов и несколько копий окружения
в рабочем репозитории. Для воспроизведения доказательств сохранены:

- `WHEELHOUSE_MANIFEST.sha256` — имена, размеры и SHA-256 всех 66 файлов;
- `snapshots/final-offline.txt` — итоговый package/version snapshot;
- `COMMAND_LOG.md` — буквальные команды, коды завершения и существенный вывод;
- `SBOM.cdx.json` — CycloneDX SBOM.
