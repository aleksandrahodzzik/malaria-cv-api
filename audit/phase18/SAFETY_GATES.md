# Safety gates

Пороги risk register зафиксированы до итоговой интерпретации:

- Critical: AdjustedPriority >= 100;
- High: 50–<100;
- Medium: 20–<50;
- Low: <20.

STOP-SHIP — отдельный override независимо от RPN.

| Gate | Requirement | Current | Verdict |
|---|---|---|---|
| G0 | Model exists, accessible, licensed, immutable | Model absent | FAIL |
| G1 | Reproducible end-to-end inference | Real inference blocked | FAIL |
| G2 | Independent external validation | None | FAIL |
| G3 | Safe rejection/QC/uncertainty | API busy/error; no biological reject | FAIL |
| G4 | Baseline security protection | Strong partial controls; no auth/edge rate limit | PARTIAL |
| G5 | Intended use defined | Research cropped-cell only defined; clinical use undefined | PASS for research / FAIL clinical |
| G6 | Claims match evidence | Research wording improved; old production claims audited | PARTIAL |

Rules:

- G0/G1 FAIL → production NO-GO.
- G2 FAIL → clinical deployment NO-GO.
- Любой STOP-SHIP требует закрытия и повторной независимой проверки.
