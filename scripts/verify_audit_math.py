"""Verify governance calculations committed in audit CSV artifacts."""

from __future__ import annotations

import csv
import json
import sys
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_prioritization = import_module("src.validation.prioritization")
adjusted_rpn = _prioritization.adjusted_rpn
priority_score = _prioritization.priority_score
quality_score = _prioritization.quality_score


def _rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    recommendation_rows = _rows("audit/phase19/PRIORITIZED_RECOMMENDATIONS.csv")
    for row in recommendation_rows:
        calculated = priority_score(
            impact=int(row["I"]),
            urgency=int(row["U"]),
            evidence=float(row["E"]),
            effort=int(row["F"]),
            dependency_complexity=int(row["D"]),
        )
        recorded = float(row["PriorityScore"])
        if abs(calculated - recorded) > 0.00005:
            raise ValueError(
                f"{row['ID']} score mismatch: {recorded} != {calculated:.4f}"
            )

    quality_rows = _rows("audit/phase19/QUALITY_SCORE_INPUT.csv")
    quality = quality_score(
        [(float(row["Weight"]), float(row["Score"])) for row in quality_rows]
    )
    recorded_contribution = sum(float(row["Contribution"]) for row in quality_rows)
    if abs(quality - recorded_contribution) > 1e-9:
        raise ValueError("Quality-score contribution mismatch.")

    risk_rows = _rows("audit/RISK_REGISTER.csv")
    for row in risk_rows:
        calculated = adjusted_rpn(
            severity=int(row["S"]),
            occurrence=int(row["O"]),
            detectability=int(row["D"]),
            confidence=float(row["Confidence"]),
        )
        recorded = float(row["AdjustedPriority"])
        if abs(calculated - recorded) > 1e-9:
            raise ValueError(
                f"{row['ID']} adjusted RPN mismatch: {recorded} != {calculated}"
            )

    print(
        json.dumps(
            {
                "status": "PASS",
                "recommendations_verified": len(recommendation_rows),
                "quality_weight_total": sum(
                    float(row["Weight"]) for row in quality_rows
                ),
                "quality_score": round(quality, 2),
                "risks_verified": len(risk_rows),
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
