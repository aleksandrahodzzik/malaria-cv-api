# UI/backend safety contract

## Машиночитаемые invariants

`GET /api/v1/capabilities`:

- `intended_use = research_only`;
- `task = pre_cropped_single_cell_classification`;
- `analysis_level = cell`;
- `probabilities_calibrated = false`;
- `patient_diagnosis_supported = false`;
- `slide_aggregation_supported = false`;
- `parasitemia_supported = false`;
- `human_review_required = true`.

`GET /api/v1/methodology`:

- supported task codes: A, F;
- unsupported task codes: B, C, D, E;
- explicit pipeline statuses and domain assumptions.

`POST /api/v1/analyze` adds:

- exact task and analysis level;
- technical validation flag that explicitly excludes microscopy QC;
- mandatory human-review flag;
- negative patient-diagnosis and parasitemia capabilities.

## UI controls

- Primary action remains disabled until file, ready model and scope
  acknowledgement are all present.
- Acknowledgement says the input is one pre-cropped cell and contains no
  identifying data.
- Score warning names uncalibrated output and human review.
- Pipeline visualization separates implemented, partial, missing and
  unvalidated stages using text and colour.
- No patient diagnosis or treatment recommendation is rendered.

## Acceptance evidence

- OpenAPI schema tests assert constant safety fields.
- Endpoint test asserts all pipeline stages.
- Static asset test checks intended-use client path.
- Security rule remains: no `innerHTML`; remote HTML is not injected.

## Residual limitations

- Checkbox is a human-factors guard, not proof of correct input.
- No biological image-quality model exists.
- No authenticated reviewer workflow or sign-off.
- No audit record of acknowledgement.
- No approved model, threshold, calibration or OOD detector.
