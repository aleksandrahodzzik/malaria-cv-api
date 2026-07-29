# Final GO/NO-GO

Дата: 2026-07-29.

| Scenario | Verdict | Evidence | Blocker/condition |
|---|---|---|---|
| Local no-model UI/demo | GO | readiness failure and research UI verified | Не выдавать mocked output за model result |
| Local mocked API testing | GO | 78 local tests; Python 3.11/3.12 CI release gate | Только software contract |
| Public non-clinical API | NO-GO | no model/auth/global quota/T2-T3 | Artifact + security + capacity gates |
| Research cell use | CONDITIONAL GO | task boundary/toolkit documented | Approved model/data/protocol; no clinical claim |
| Retrospective clinical research | INSUFFICIENT EVIDENCE | no cohort/model | Ethics/data/model/statistical protocol |
| Prospective silent evaluation | INSUFFICIENT EVIDENCE | workflow not built | Prior retrospective/QC/human-factor gates |
| Clinical decision support | NO-GO | G2/G3 fail | External/prospective evidence + QMS/human review |
| Autonomous diagnosis | NO-GO | outside evidence/intended scope | Not an authorized development target |

Quality Score: **36.3/100**. G0/G1/G2/G3 failures override the arithmetic.
