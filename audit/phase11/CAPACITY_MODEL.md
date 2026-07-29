# Capacity model

`src/validation/capacity.py` реализует проверяемые planning helpers:

- `rho = lambda / (c * mu)`;
- Little: `L = lambda * W`;
- Erlang-C для устойчивого M/M/c при `rho < 1`;
- `RAM = c*(model+runtime+activation)+shared+upload+safety`;
- latency summary с интерполированными quantiles.

## Правила применения

1. `mu` брать только из real-model steady-state benchmark.
2. Учитывать per-process model copy; Copy-on-Write нельзя считать
   гарантированным после PyTorch initialization.
3. Измерить nested PyTorch/OpenMP threads и избежать oversubscription.
4. Проверить admitted concurrency, queue timeout и request cancellation.
5. Начальный исследуемый диапазон `rho <= 0.7` — эвристика, не SLO.
6. Добавить upload buffers и decoded-image amplification в RAM.
7. Подтвердить результат soak test и failure injection.

## Текущее решение

Один Gunicorn worker плюс bounded inference semaphore безопаснее
неизмеренного размножения модели. Это не доказательство достаточной capacity.
Production capacity: UNKNOWN.
