"""Deterministic governance-score calculations used by audit artifacts.

Numeric scores support ordering within a policy class. They never override a
STOP-SHIP, regulatory-mandatory, or patient-safety decision.
"""

from __future__ import annotations

import math


def priority_score(
    *,
    impact: int,
    urgency: int,
    evidence: float,
    effort: int,
    dependency_complexity: int,
) -> float:
    """Return (I * U * E) / sqrt(F * D) after validating declared domains."""
    _validate_integer_scale(impact, "impact")
    _validate_integer_scale(urgency, "urgency")
    _validate_integer_scale(effort, "effort")
    _validate_integer_scale(dependency_complexity, "dependency_complexity")
    if not math.isfinite(evidence) or not 0.25 <= evidence <= 1.0:
        raise ValueError("evidence must be finite and within [0.25, 1.0].")
    return (impact * urgency * evidence) / math.sqrt(effort * dependency_complexity)


def quality_score(
    weighted_scores: list[tuple[float, float]],
) -> float:
    """Return a 0-100 quality score; weights must total exactly 100."""
    if not weighted_scores:
        raise ValueError("At least one category is required.")
    if any(
        not math.isfinite(weight)
        or not math.isfinite(score)
        or weight <= 0
        or not 0 <= score <= 5
        for weight, score in weighted_scores
    ):
        raise ValueError("Weights must be positive and scores within [0, 5].")
    total_weight = math.fsum(weight for weight, _ in weighted_scores)
    if not math.isclose(total_weight, 100.0, abs_tol=1e-9):
        raise ValueError("Quality-score weights must total 100.")
    return math.fsum(weight * score / 5 for weight, score in weighted_scores)


def adjusted_rpn(
    *,
    severity: int,
    occurrence: int,
    detectability: int,
    confidence: float,
) -> float:
    """Return S*O*D*(1 + 1-confidence) with validated FMEA domains."""
    _validate_integer_scale(severity, "severity")
    _validate_integer_scale(occurrence, "occurrence")
    _validate_integer_scale(detectability, "detectability")
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("confidence must be finite and within [0, 1].")
    return severity * occurrence * detectability * (2 - confidence)


def _validate_integer_scale(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
        raise ValueError(f"{name} must be an integer within [1, 5].")
