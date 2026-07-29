# Executive summary

Дата повторной оценки: 2026-07-29. Классификация: evidence-backed software
remediation; не clinical validation и не юридическое заключение.

## Verdict

- Software remediation: **PASS** для заявленного локального scope.
- Technical production readiness: **NO-GO** без утверждённого model release.
- Clinical readiness: **NO-GO**.
- Local no-model research UI: **GO**.
- Quality Score: **51.02/100**, с override незакрытых safety gates.
- Branch coverage: **98.11%**, 163 tests.

Цель 95/100 не присвоена: 40 из 100 весовых баллов относятся к
clinical/model evidence и data governance, которых невозможно создать
рефакторингом API.

## Реализовано и VERIFIED

1. Fail-closed model governance:
   - exact 40-hex revision;
   - локальный `model_manifest.json`;
   - независимый manifest SHA-256 trust anchor;
   - streaming checksum всех заявленных artifacts;
   - проверка model ID, revision, labels, input resolution и license metadata;
   - запрет unsafe paths, undeclared safetensors, pickle и remote code;
   - `/ready` возвращает `MODEL_ARTIFACT_NOT_VERIFIED` при failure.
2. Engineering QC до processor/model:
   - discrete Laplacian variance;
   - contrast;
   - stain-like color ratio;
   - resolution и aspect ratio;
   - HTTP 422 с ordered reasons и QC metrics.
3. Research-only slide summary:
   - bounded multiple uploads;
   - predicted-cell counts;
   - Wilson 95% interval;
   - `RESEARCH_ONLY_UNCALIBRATED_SLIDE_SUMMARY`;
   - явный запрет patient diagnosis и clinically validated parasitemia claim.
4. Security:
   - optional API-key authentication;
   - constant-time comparison;
   - per-process sliding-window quota;
   - invalid key не создаёт отдельный quota bucket;
   - bounded client-key cardinality.
5. Verification:
   - 163 tests;
   - 98.11% branch coverage;
   - Ruff PASS;
   - strict mypy PASS;
   - coverage gate повышен с 80 до 95.

## Residual STOP-SHIP

1. Утверждённый лицензированный malaria model artifact отсутствует.
2. `trpakov/vit-malaria-classification` не обнаружен в публичном профиле,
   где на дату проверки перечислены только `vit-face-expression` и
   `vit-pneumonia`; SHA намеренно не выдуман.
3. Real-model clean/offline end-to-end inference не выполнен.
4. Независимая patient-level external validation отсутствует.
5. QC thresholds являются инженерными эвристиками, не clinically validated OOD.
6. Patient-level aggregation, reference standard и decision rule отсутствуют.

## Safety gates

| Gate | Status | Evidence |
|---|---|---|
| G0 model exists/licensed/verified | FAIL | verifier реализован, release отсутствует |
| G1 real end-to-end reproducible | FAIL | только mocked/synthetic tests |
| G2 independent external validation | FAIL | cohort/predictions отсутствуют |
| G3 safe rejection | PARTIAL | deterministic QC есть; clinical/OOD validation нет |
| G4 baseline security | PARTIAL | auth/quota есть; global gateway/TLS/deployment не проверены |
| G5 intended use | PASS | research-only cell/slide-summary boundaries |
| G6 claims match evidence | PASS | score и verdict не повышены искусственно |

## Следующий обязательный шаг

Владелец модели должен предоставить controlled release bundle: artifact,
model card, license evidence, exact revision, patient/slide-safe provenance и
manifest trust-anchor approval. После этого выполняются clean/offline smoke,
golden regression, T2/T3 capacity и независимая внешняя валидация.
