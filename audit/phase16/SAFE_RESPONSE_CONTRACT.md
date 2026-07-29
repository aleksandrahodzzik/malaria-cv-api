# Proposed safe response contract

До patient-level validation контракт может существовать только как design:

```json
{
  "predicted_cell_class": "Parasitized|Uninfected|Indeterminate",
  "confidence_score": 0.0,
  "confidence_semantics": "calibrated cell-class score, not disease probability",
  "calibration_version": "sha256:...",
  "requires_review": true,
  "uncertainty_reason": "quality|ood|low_margin|null",
  "quality_flags": ["..."],
  "model_name": "approved-alias",
  "model_revision": "immutable-sha",
  "preprocessing_version": "sha256:...",
  "intended_use": "research pre-cropped cell classification only",
  "request_id": "..."
}
```

Не возвращать local model path, patient identifiers, raw logits или claims о
diagnosis/treatment. Добавление slide/patient result требует отдельной schema
version и пройденного patient safety gate.
