# Независимые review passes

Дата: 2026-07-29.

## Review A — скептический биостатистик

Проверены unit of analysis, leakage, pseudoreplication, denominators,
cluster-CI, prevalence, calibration, thresholds и external validation.

Результат:

- cell/slide/patient уровни разделены;
- patient independence не заявлена;
- текущие performance metrics остаются NOT EXECUTED;
- 36.3/100 не является accuracy;
- обнаружен риск, что старые summary/roadmap создают ложный current baseline;
  канонические отчёты обновлены.

## Review B — security/SRE red team

Проверены upload/resource abuse, concurrency, logs, model/dependency/action
integrity, readiness, timeouts и memory topology.

Результат:

- allowlisted JSON logs, limits и bounded per-process inference подтверждены;
- action SHA pinning подтверждён CI;
- auth/global quota, full hash lock, base/model signature и T2/T3 остаются gaps;
- не внедрён misleading in-process «global» rate limiter.

## Review C — clinical/regulatory

Проверены intended use, terminology, cell/patient boundary, human oversight,
automation bias, evidence и change/monitoring controls.

Результат:

- research-only cell contract согласован;
- clinical/patient claim остаётся NO-GO;
- regulatory applicability условна и market/intended-purpose dependent;
- стратегия D блокируется до prospective silent evidence и controlled QMS.

## Review D — логико-математический

Проверены формулы, domains, weights, RPN, recommendation scores, roadmap/verdict
и master-prompt structure.

Результат:

- веса quality score = 100;
- contribution = 36.3;
- adjusted RPN не уменьшается при uncertainty;
- recommendation scores воспроизводимы;
- policy overrides отделены от numeric score;
- prompt headings и fences проверяются отдельно.

## Исправленные противоречия

Исторические 28/100, 9 tests и 74% coverage удалены из канонических summary.
Текущий доказанный baseline: 36.3/100, 78 tests, 88.52% branch coverage; это не
меняет clinical NO-GO.
