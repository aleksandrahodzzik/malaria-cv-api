# Calibration and selective-classification plan

## Current state

- Softmax output is explicitly uncalibrated.
- No calibration split exists.
- No threshold or uncertainty gate is approved.
- Current API therefore returns research scores and requires human review.

## Calibration experiment

1. Freeze base model and locked predictions.
2. Fit temperature scaling on calibration split.
3. Fit Platt scaling and isotonic regression as predefined comparators.
4. Select without inspecting final test labels.
5. Evaluate on locked external test:
   - Brier;
   - NLL;
   - ECE with declared bins;
   - reliability diagram;
   - slope/intercept;
   - cluster bootstrap CIs.
6. Store calibration artifact, method, data version and checksum.
7. Revalidate after model/data/acquisition change.

## Selective experiment

Baselines:

- maximum softmax probability;
- predictive entropy;
- top-two margin;
- temperature-scaled confidence.

Additional methods require separately trained/evaluated artifacts:

- deep ensemble;
- OOD score;
- acquisition/image-quality model.

For every threshold report:

```text
coverage
selective risk
rejected count
positive/negative rejection rates
site/device/subgroup coverage
human-review delay
errors after rejection
```

Reject is not success. It must enter a defined human workflow and is included
in ExpectedCost through `C_REJECT` and `C_DELAY`.

## Prohibition

No epistemic-uncertainty claim may be based only on raw maximum softmax.
