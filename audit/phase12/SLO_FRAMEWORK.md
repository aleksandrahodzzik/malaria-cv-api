# SLO framework

Конкретные SLO не утверждены без business/clinical requirements.

Кандидатные диапазоны для обсуждения:

- technical availability: 99.0–99.9%;
- p95 warm latency: определяется после T2/T3 baseline;
- 5xx: 0.1–1.0%;
- overload rejection: отдельно от internal 5xx;
- model-ready availability: отдельно от API liveness.

`ErrorBudget = (1 - SLO) * total_time`.

Для 30 суток это даёт примерно 7.2 часа при 99.0%, 43.2 минуты при 99.9%.
Это иллюстрация, а не принятый target. Clinical safety metrics — false-negative,
quality rejection и review SLA — не должны растворяться в HTTP availability.
