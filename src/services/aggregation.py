"""Research-only aggregation of pre-cropped cell classifications."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


class CellPrediction(Protocol):
    """Minimum prediction contract required for aggregation."""

    predicted_cell_class: str


@dataclass(frozen=True, slots=True)
class WilsonInterval:
    """Two-sided Wilson score interval for a binomial proportion."""

    lower: float
    upper: float


@dataclass(frozen=True, slots=True)
class SlideAggregation:
    """Observed distribution of model-predicted cell classes."""

    total_cells: int
    parasitized_cells: int
    uninfected_cells: int
    parasitemia_fraction: float
    wilson_95: WilsonInterval


def wilson_score_interval(
    successes: int,
    total: int,
    *,
    z_score: float = 1.959963984540054,
) -> WilsonInterval:
    """Calculate a Wilson interval without assuming a normal plug-in variance."""
    if total <= 0:
        raise ValueError("total must be positive.")
    if successes < 0 or successes > total:
        raise ValueError("successes must be between zero and total.")
    if z_score <= 0 or not math.isfinite(z_score):
        raise ValueError("z_score must be finite and positive.")

    proportion = successes / total
    z_squared = z_score**2
    denominator = 1 + z_squared / total
    center = (proportion + z_squared / (2 * total)) / denominator
    margin = (
        z_score
        * math.sqrt(
            proportion * (1 - proportion) / total
            + z_squared / (4 * total**2)
        )
        / denominator
    )
    return WilsonInterval(
        lower=max(0.0, center - margin),
        upper=min(1.0, center + margin),
    )


def aggregate_slide_predictions(
    predictions: Sequence[CellPrediction],
    *,
    parasitized_label: str = "Parasitized",
    uninfected_label: str = "Uninfected",
) -> SlideAggregation:
    """Aggregate predictions while rejecting unknown labels."""
    if not predictions:
        raise ValueError("At least one cell prediction is required.")
    allowed = {parasitized_label, uninfected_label}
    labels = [prediction.predicted_cell_class for prediction in predictions]
    unknown = set(labels) - allowed
    if unknown:
        raise ValueError("Cell predictions contain an unknown class label.")

    parasitized = labels.count(parasitized_label)
    total = len(labels)
    return SlideAggregation(
        total_cells=total,
        parasitized_cells=parasitized,
        uninfected_cells=total - parasitized,
        parasitemia_fraction=parasitized / total,
        wilson_95=wilson_score_interval(parasitized, total),
    )
