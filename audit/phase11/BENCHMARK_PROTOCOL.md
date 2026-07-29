# Фаза 11 — benchmark protocol

Дата: 2026-07-28. ОС: Windows 11 build 26200. Python: 3.12.0.

## Уровни

- T0: `/health` через in-process ASGI transport.
- T1: `/analyze` с валидным PNG и synthetic async classifier.
- T2: реальный Pillow + processor + locked model.
- T3: Docker/reverse proxy/network/endurance.

В этой итерации VERIFIED только T0/T1. T2/T3 — NOT EXECUTED: утверждённая
модель отсутствует, Docker CLI недоступен. Следовательно, измерения нельзя
использовать для production sizing.

## Метод

- `python -m scripts.benchmark_api`;
- 10 warm-up и 100 measured requests на сценарий;
- concurrency: 1, 2, 4, 8, 16;
- фиксированный synthetic response;
- wall-clock `perf_counter`;
- p50/p90/p95/p99, mean, sample SD, normal-approximation 95% CI;
- error rate по non-2xx/exception;
- application request logs отключены только для чистоты benchmark output.

## Ограничения

Нет TCP/TLS, Gunicorn, model load, PIL decode внутри mock, PyTorch, CPU/RSS,
native thread saturation или representative images. Малый T1 выброс при c=4
показывает важность повторных прогонов и environment isolation.
