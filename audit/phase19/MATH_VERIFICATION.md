# Mathematical verification

Command:

`.\.venv\Scripts\python.exe -m scripts.verify_audit_math`

Exit code: 0.

Result:

```json
{"status":"PASS","recommendations_verified":16,"quality_weight_total":100.0,"quality_score":36.3,"risks_verified":12}
```

Verified equations:

- `PriorityScore = I*U*E/sqrt(F*D)`;
- `QualityScore = sum(weight*score/5)`;
- `AdjustedRPN = S*O*D*(2-confidence)`.

Domain checks are unit-tested: integer scales 1–5, evidence 0.25–1.0,
confidence 0–1 and quality weights exactly 100.

Policy order is not computed from these equations. STOP-SHIP, regulatory
mandatory and patient-safety overrides remain explicit governance decisions.
