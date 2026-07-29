"""Slide aggregation and Wilson interval tests."""

import math
from dataclasses import dataclass

import pytest

from src.services.aggregation import (
    aggregate_slide_predictions,
    wilson_score_interval,
)


@dataclass
class Prediction:
    predicted_cell_class: str


@pytest.mark.parametrize(
    ("successes", "total", "expected_lower", "expected_upper"),
    [
        (0, 10, 0.0, 0.2775),
        (5, 10, 0.2366, 0.7634),
        (10, 10, 0.7225, 1.0),
    ],
)
def test_wilson_known_values(
    successes: int,
    total: int,
    expected_lower: float,
    expected_upper: float,
) -> None:
    interval = wilson_score_interval(successes, total)
    assert interval.lower == pytest.approx(expected_lower, abs=0.0001)
    assert interval.upper == pytest.approx(expected_upper, abs=0.0001)


@pytest.mark.parametrize(
    ("successes", "total", "z_score", "message"),
    [
        (0, 0, 1.96, "total"),
        (-1, 10, 1.96, "successes"),
        (11, 10, 1.96, "successes"),
        (1, 10, 0.0, "z_score"),
        (1, 10, math.inf, "z_score"),
    ],
)
def test_wilson_rejects_invalid_inputs(
    successes: int,
    total: int,
    z_score: float,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        wilson_score_interval(successes, total, z_score=z_score)


def test_slide_aggregation_counts_labels() -> None:
    predictions = [Prediction("Parasitized")] * 3 + [Prediction("Uninfected")] * 7
    result = aggregate_slide_predictions(predictions)
    assert result.total_cells == 10
    assert result.parasitized_cells == 3
    assert result.uninfected_cells == 7
    assert result.parasitemia_fraction == 0.3
    assert 0.10 < result.wilson_95.lower < 0.11
    assert 0.60 < result.wilson_95.upper < 0.61


def test_slide_aggregation_supports_explicit_contract_labels() -> None:
    result = aggregate_slide_predictions(
        [Prediction("P"), Prediction("N")],
        parasitized_label="P",
        uninfected_label="N",
    )
    assert result.parasitized_cells == 1


def test_slide_aggregation_rejects_empty_and_unknown_labels() -> None:
    with pytest.raises(ValueError, match="At least one"):
        aggregate_slide_predictions([])
    with pytest.raises(ValueError, match="unknown"):
        aggregate_slide_predictions([Prediction("Ambiguous")])
