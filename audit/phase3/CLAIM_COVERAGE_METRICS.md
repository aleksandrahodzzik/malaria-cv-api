# Claim evidence coverage metrics

Дата: 2026-07-28
Источник: `CLAIM_TO_EVIDENCE_MATRIX.csv`.

## Результат

| Slice | Claims | Supported | Partial | Unsupported | Contradicted | Not testable | Weighted coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 20 | 2 | 7 | 4 | 6 | 1 | 0.1667 |
| CURRENT | 24 | 19 | 4 | 0 | 0 | 1 | 0.9083 |
| ALL | 44 | 21 | 11 | 4 | 6 | 2 | 0.5729 |

Дополнительные показатели:

| Slice | SupportedRate | FalseMarketingRate | UntestableRate |
|---|---:|---:|---:|
| BASELINE | 0.1000 | 0.5000 | 0.0500 |
| CURRENT | 0.7917 | 0.0000 | 0.0417 |
| ALL | 0.4773 | 0.2273 | 0.0455 |

## Формулы

```text
ClaimEvidenceCoverage =
  Σ(RiskWeight_i * VerdictWeight_i)
  / Σ(RiskWeight_i)

SupportedRate = SUPPORTED / N

FalseMarketingRate =
  (UNSUPPORTED + CONTRADICTED) / N

UntestableRate =
  NOT_TESTABLE_WITH_CURRENT_EVIDENCE / N
```

Для baseline:

```text
weighted numerator   = 15
weighted denominator = 90
coverage             = 15 / 90 = 0.1667
```

Для current:

```text
weighted numerator   = 99
weighted denominator = 109
coverage             = 99 / 109 = 0.9083
```

## Ограничение интерпретации

`0.9083` не является вероятностью качества или production-готовности. Это
только доля риска claims, покрытая доступными доказательствами. Critical claim
о real-model результате остаётся `NOT_TESTABLE`, поэтому safety override
сохраняет `NO-GO` для ML production и clinical use.
