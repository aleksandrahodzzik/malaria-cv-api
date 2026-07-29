# Phase 5 — происхождение и целостность модели

Дата: 2026-07-28

## Четыре model states

| State | Value | Classification |
|---|---|---|
| Current configured model | `MODEL_NAME=""` | VERIFIED fail-closed |
| Historically claimed model | `trpakov/vit-malaria-classification` | OBSERVED in `HEAD` |
| Locally cached model | none found | VERIFIED for checked paths |
| Approved release model | none | STOP-SHIP |

Текущая конфигурация была сознательно исправлена: приложение больше не делает
сетевой запрос к недоказанной модели по умолчанию. Это повышает безопасность,
но не создаёт approved model artifact.

## Online provenance

Полный протокол: [HUGGINGFACE_HTTP_EVIDENCE.md](HUGGINGFACE_HTTP_EVIDENCE.md).

Кратко:

- exact API/page/config/processor/weights/model card отвечают `401`;
- официальный public author API перечисляет только две другие модели;
- официальный `huggingface_hub` client подтверждает тот же список;
- real Transformers loader завершается ошибкой;
- локальный cache отсутствует.

Вердикт:

```text
trpakov/vit-malaria-classification
= NOT PUBLICLY REPRODUCIBLE
= STOP-SHIP
```

Private repository теоретически возможен, но credentials, immutable revision,
manifest и authorization evidence в проекте отсутствуют.

## Проверка обязательных полей

| Поле | Результат |
|---|---|
| Exact model ID | historical value known |
| Public availability | FAIL |
| Architecture | UNKNOWN |
| Base model | UNKNOWN |
| Config | UNAVAILABLE |
| Processor config | UNAVAILABLE |
| `num_labels` | UNKNOWN |
| `id2label` | UNKNOWN |
| `label2id` | UNKNOWN |
| Input size/channels | UNKNOWN |
| Mean/std/resize/crop | UNKNOWN |
| Weight format | UNKNOWN |
| Safetensors availability | UNKNOWN/UNAVAILABLE |
| `trust_remote_code` need | UNKNOWN; runtime policy forbids it |
| License | UNKNOWN |
| Model card | UNKNOWN |
| Training dataset | UNKNOWN |
| Patient-level split | UNKNOWN |
| Metrics | UNKNOWN |
| Calibration | UNKNOWN |
| External validation | UNKNOWN |
| Last modified | UNKNOWN |
| Commit SHA/revision | UNKNOWN |
| Artifact size | UNKNOWN |
| SHA-256 | NOT COMPUTABLE |
| Offline reload | NOT EXECUTED |

Никакие поля не перенесены из `vit-pneumonia` или `vit-face-expression`.

## Serving controls, реализованные в приложении

Даже будущий approved artifact будет принят только если:

- labels точно совпадают с `MODEL_EXPECTED_LABELS`;
- индексы contiguous от нуля;
- `num_labels` согласован;
- logits имеют shape `[1, num_labels]`;
- `trust_remote_code=False`;
- `use_safetensors=True`;
- remote production model имеет immutable revision;
- production рекомендуется запускать local-only.

Эти controls проверяют serving contract, но не доказывают training provenance
или clinical validity.

## Model Evidence Score

```text
Availability           = 0.00
Integrity              = 0.00
License                = 0.00
TrainingProvenance     = 0.00
ExternalValidation     = 0.00
ServingContract        = 0.25
OfflineReproducibility = 0.00
```

```text
ModelEvidenceScore =
  0.20*0
  + 0.15*0
  + 0.15*0
  + 0.15*0
  + 0.15*0
  + 0.10*0.25
  + 0.10*0
  = 0.025
```

`0.025/1.0` не является performance score. Это полнота model evidence.

Safety override:

```text
Availability = 0
Integrity = 0
License = 0
=> production/clinical model GO запрещён
```

## Влияние на runtime

### Current default

```text
startup: succeeds without model
/health: 200
/ready: 503 MODEL_NOT_CONFIGURED
/analyze: 503
```

### Historical model ID

```text
startup loader: fails
app process: remains live
/health: 200
/ready: 503 model_initialization_failed
/analyze: 503
```

Docker `HEALTHCHECK /health` доказывает только liveness процесса. Для
orchestrator deployment обязательна отдельная readiness probe `/ready`.

## Решение

Модель не заменять. Следующая допустимая работа начинается с approved artifact
package и подписанного manifest.
