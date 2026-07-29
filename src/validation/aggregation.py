"""Planning mathematics for cell-to-slide aggregation.

Nothing in this module creates a clinically validated patient result. The
functions expose assumptions so study designers can quantify why a naive
cell-count rule is insufficient.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class CorrectedRate:
    """Misclassification-corrected rate with boundary clipping disclosed."""

    apparent_rate: float
    unconstrained_rate: float
    constrained_rate: float
    clipped: bool


@dataclass(frozen=True)
class BetaBinomialMoments:
    """Mean, variance and intra-cluster correlation of a beta-binomial count."""

    mean_count: float
    variance_count: float
    mean_rate: float
    intraclass_correlation: float
    design_effect: float
    effective_sample_size: float


def apparent_positive_rate(positive_cells: int, examined_cells: int) -> float:
    """Return k/m after validating count semantics."""
    _validate_counts(positive_cells, examined_cells)
    if examined_cells == 0:
        raise ValueError("At least one examined cell is required.")
    return positive_cells / examined_cells


def rogan_gladen_rate(
    positive_cells: int,
    examined_cells: int,
    *,
    sensitivity: float,
    specificity: float,
) -> CorrectedRate:
    """Correct an apparent cell-positive rate for known Se/Sp.

    The correction is only applicable when the supplied operating
    characteristics are valid for the same sampling and acquisition domain.
    """
    apparent = apparent_positive_rate(positive_cells, examined_cells)
    _validate_probability(sensitivity, "sensitivity")
    _validate_probability(specificity, "specificity")
    denominator = sensitivity + specificity - 1
    if denominator <= 0:
        raise ValueError("Correction requires sensitivity + specificity > 1.")
    unconstrained = (apparent + specificity - 1) / denominator
    constrained = min(1.0, max(0.0, unconstrained))
    return CorrectedRate(
        apparent_rate=apparent,
        unconstrained_rate=unconstrained,
        constrained_rate=constrained,
        clipped=constrained != unconstrained,
    )


def false_positive_accumulation(
    *,
    specificity: float,
    examined_cells: int,
) -> float:
    """Independent-cell illustration of at least one false positive.

    This is deliberately not named a patient probability. Correlated cells and
    domain shift invalidate the independence assumption.
    """
    _validate_probability(specificity, "specificity")
    if examined_cells < 0:
        raise ValueError("examined_cells must be non-negative.")
    return 1 - specificity**examined_cells


def minimum_cells_for_detection(
    *,
    true_cell_rate: float,
    cell_sensitivity: float,
    target_detection_probability: float,
) -> int:
    """Optimistic independent-sampling lower bound for detecting one cell."""
    _validate_probability(true_cell_rate, "true_cell_rate")
    _validate_probability(cell_sensitivity, "cell_sensitivity")
    if not 0 < target_detection_probability < 1:
        raise ValueError("target_detection_probability must be within (0, 1).")
    per_draw_detection = true_cell_rate * cell_sensitivity
    if per_draw_detection == 0:
        raise ValueError("Detection is impossible when rate or sensitivity is zero.")
    if per_draw_detection == 1:
        return 1
    return math.ceil(
        math.log1p(-target_detection_probability) / math.log1p(-per_draw_detection)
    )


def beta_binomial_moments(
    examined_cells: int,
    *,
    alpha: float,
    beta: float,
) -> BetaBinomialMoments:
    """Return beta-binomial moments and cluster design effect."""
    if examined_cells <= 0:
        raise ValueError("examined_cells must be positive.")
    if alpha <= 0 or beta <= 0:
        raise ValueError("alpha and beta must be positive.")
    total = alpha + beta
    mean_rate = alpha / total
    correlation = 1 / (total + 1)
    design_effect = 1 + (examined_cells - 1) * correlation
    binomial_variance = examined_cells * mean_rate * (1 - mean_rate)
    return BetaBinomialMoments(
        mean_count=examined_cells * mean_rate,
        variance_count=binomial_variance * design_effect,
        mean_rate=mean_rate,
        intraclass_correlation=correlation,
        design_effect=design_effect,
        effective_sample_size=examined_cells / design_effect,
    )


def _validate_counts(positive_cells: int, examined_cells: int) -> None:
    if positive_cells < 0 or examined_cells < 0 or positive_cells > examined_cells:
        raise ValueError("Require 0 <= positive_cells <= examined_cells.")


def _validate_probability(value: float, name: str) -> None:
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be finite and within [0, 1].")
