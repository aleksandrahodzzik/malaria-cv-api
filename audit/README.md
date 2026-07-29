# Полный аудит `malaria-cv-api`

Версия отчёта: 1.0.0
Дата фиксации: 2026-07-27
Режим: READ-ONLY для production-кода
Корень: `C:\Users\Oleksandra\OneDrive\Desktop\biologi_test1`

> Обновление 2026-07-28: выполнена controlled remediation и добавлен
> research-only UI. Исходные документы ниже сохраняют baseline на момент
> первого аудита. Текущий implementation/verification status находится в
> [`audit/phase1/`](phase1/README.md). Фазы claim verification, архитектуры и
> model provenance находятся в [`audit/phase3/`](phase3/CLAIM_TO_EVIDENCE_MATRIX.md),
> [`audit/phase4/`](phase4/ARCHITECTURE_AUDIT.md) и
> [`audit/phase5/`](phase5/MODEL_PROVENANCE_AUDIT.md).
> Фазы intended use, datasets и математической валидации находятся в
> [`audit/phase6/`](phase6/INTENDED_USE_AUDIT.md),
> [`audit/phase7/`](phase7/DATASET_DATASHEET_CURRENT.md) и
> [`audit/phase8/`](phase8/MATHEMATICAL_VALIDATION_STATUS.md).
>
> Фазы 9–18 расширяют аудит до агрегации, robustness/OOD, capacity,
> observability, STRIDE/privacy, supply chain, тестовой стратегии, human
> factors, regulatory applicability и доказательного GO/NO-GO:
> [`phase9`](phase9/AGGREGATION_AUDIT.md),
> [`phase10`](phase10/ROBUSTNESS_OOD_PLAN.md),
> [`phase11`](phase11/BENCHMARK_PROTOCOL.md),
> [`phase12`](phase12/RELIABILITY_OBSERVABILITY_AUDIT.md),
> [`phase13`](phase13/STRIDE_THREAT_MODEL.md),
> [`phase14`](phase14/SUPPLY_CHAIN_AUDIT.md),
> [`phase15`](phase15/TEST_STRATEGY.md),
> [`phase16`](phase16/CLINICAL_WORKFLOW.md),
> [`phase17`](phase17/REGULATORY_APPLICABILITY.md) и
> [`phase18`](phase18/FINAL_GO_NO_GO.md).
>
> Фаза 19 синхронизирует канонические отчёты, policy-aware рекомендации,
> измеримый roadmap, продуктовые стратегии, counterfactual tests и четыре
> независимых review-pass:
> [`phase19`](phase19/RECOMMENDATION_PORTFOLIO.md).

## Канонический текущий пакет

- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
- [REPOSITORY_INVENTORY.md](REPOSITORY_INVENTORY.md)
- [CLAIM_EVIDENCE_MATRIX.md](CLAIM_EVIDENCE_MATRIX.md)
- [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md)
- [MODEL_AND_DATA_AUDIT.md](MODEL_AND_DATA_AUDIT.md)
- [STATISTICAL_VALIDATION_PLAN.md](STATISTICAL_VALIDATION_PLAN.md)
- [SECURITY_THREAT_MODEL.md](SECURITY_THREAT_MODEL.md)
- [CLINICAL_REGULATORY_GAP_ANALYSIS.md](CLINICAL_REGULATORY_GAP_ANALYSIS.md)
- [RISK_REGISTER.csv](RISK_REGISTER.csv)
- [EVIDENCE_MATRIX.csv](EVIDENCE_MATRIX.csv)
- [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)
- [FINAL_GO_NO_GO.md](FINAL_GO_NO_GO.md)

Фазовые документы сохраняют подробную историю evidence. При расхождении
актуальный verdict и score берутся из канонического пакета с датой
2026-07-29.

## Итог

Проект представляет собой аккуратно оформленный API-каркас, но не является
работоспособной и доказанной медицинской ML-системой. Итоговый вердикт:
**NO-GO для production, публичного ML API, исследований с выводами об
эффективности и любого клинического применения**.

Главная блокирующая причина: настроенная модель
`trpakov/vit-malaria-classification` не обнаружена в публичном профиле автора,
не находится в локальном Hugging Face cache, а тесты намеренно подменяют
загрузку и инференс. Следовательно, реальный путь
`image -> processor -> model -> logits -> label` не был воспроизведён.

## Состав отчёта

- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) — управленческий вывод,
  оценка готовности и stop-ship условия.
- [REPOSITORY_INVENTORY.md](REPOSITORY_INVENTORY.md) — baseline, структура,
  версии и границы проверенного окружения.
- [EXECUTION_LOG.md](EXECUTION_LOG.md) — воспроизводимый журнал команд и
  статусы `PASS/FAIL/NOT EXECUTED`.
- [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md) — код, API, тесты, зависимости,
  контейнер и CI/CD.
- [MODEL_DATA_STATISTICAL_AUDIT.md](MODEL_DATA_STATISTICAL_AUDIT.md) —
  происхождение модели, данные, математический протокол оценки, калибровка,
  OOD и клиническая полезность.
- [SECURITY_RELIABILITY_AUDIT.md](SECURITY_RELIABILITY_AUDIT.md) — threat
  model, abuse cases, отказоустойчивость и нагрузочная валидация.
- [CLINICAL_REGULATORY_AUDIT.md](CLINICAL_REGULATORY_AUDIT.md) — intended
  use, клинические ограничения и регуляторные разрывы.
- [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) — приоритетный план
  0/30/60/90/180 дней.
- [EVIDENCE_MATRIX.csv](EVIDENCE_MATRIX.csv) — трассировка заявлений к
  доказательствам.
- [RISK_REGISTER.csv](RISK_REGISTER.csv) — реестр рисков и критерии закрытия.
- [SOURCES.md](SOURCES.md) — проверенная доказательная база и область
  применимости источников.
- [FINAL_GO_NO_GO.md](FINAL_GO_NO_GO.md) — отдельные решения по сценариям
  эксплуатации.

## Легенда достоверности

- `OBSERVED` — непосредственно найдено в репозитории или выводе команды.
- `VERIFIED` — подтверждено воспроизводимым тестом или первоисточником.
- `INFERRED` — логический вывод из нескольких доказательств.
- `HYPOTHESIS` — проверяемое предположение.
- `RECOMMENDATION` — предлагаемое действие.
- `UNKNOWN` — данных недостаточно.

Зелёный unit-тест не интерпретировался как подтверждение медицинской
эффективности. Reporting guidelines использованы как контроль полноты
отчётности, а не как сертификат качества.
