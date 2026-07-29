# Counterfactual and four-pass review

## Model artifact

- Primary: `trpakov/vit-malaria-classification` отсутствует публично.
- Alternative: private, renamed или только в локальном cache.
- Test: публичный профиль/registry, локальный cache и settings.
- Result: public profile показывает другие модели; local approved bundle не найден.
- Residual: владелец может предоставить private controlled release.

## QC

- Primary: rejected image непригодно.
- Alternative: редкий валидный stain/domain не проходит heuristic threshold.
- Test: multi-site labeled QC cohort with subgroup/device analysis.
- Result: выполнены только deterministic fixtures.
- Residual: высокий; clinical/OOD claim запрещён.

## Rate limiting

- Primary: quota снижает anonymous burst DoS.
- Alternative: multi-worker/multi-replica или distributed IP rotation обходит лимит.
- Test: gateway-level distributed load test.
- Result: per-process unit/integration behavior verified.
- Residual: global quota required before public deployment.

## Wilson slide interval

- Primary: интервал показывает sampling uncertainty predicted-positive fraction.
- Alternative: узкий interval ошибочно воспринимается как clinical certainty.
- Test: compare binomial, cluster bootstrap and model-error corrected study analysis.
- Result: API disclaimer and claim boundary verified.
- Residual: no patient/slide clinical inference allowed.

## Review A — skeptical biostatistician

PASS для формулы Wilson и disclosure. FAIL для patient-level evidence:
pseudoreplication, classifier error и external validation остаются.

## Review B — security/SRE

PASS для manifest failure, auth negative paths, request quota и bounded key store.
PARTIAL для distributed quota, TLS, secrets rotation, container and capacity.

## Review C — clinical/regulatory

PASS для research-only wording и no-patient-diagnosis fields. FAIL для clinical
deployment из-за отсутствия intended clinical protocol и performance evidence.

## Review D — logic/math

Weights = 100. Quality Score = 52.38. Coverage = 98.29%. Wilson tests include
0/10, 5/10, 10/10. Target 95/100 не подменяет фактический результат.
