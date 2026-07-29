"""Tests for aggregation, robustness and capacity planning helpers."""

import math

import pytest
from PIL import Image, ImageChops

from src.validation.aggregation import (
    apparent_positive_rate,
    beta_binomial_moments,
    false_positive_accumulation,
    minimum_cells_for_detection,
    rogan_gladen_rate,
)
from src.validation.capacity import (
    erlang_c,
    little_law,
    ram_estimate,
    summarize_latency,
    utilization,
)
from src.validation.prioritization import (
    adjusted_rpn,
    priority_score,
    quality_score,
)
from src.validation.robustness import (
    SUPPORTED_CORRUPTIONS,
    apply_corruption,
    corruption_suite,
)


def test_rogan_gladen_correction_and_clipping() -> None:
    corrected = rogan_gladen_rate(
        20,
        100,
        sensitivity=0.9,
        specificity=0.95,
    )
    assert corrected.apparent_rate == 0.2
    assert corrected.unconstrained_rate == pytest.approx(0.176470588)
    assert corrected.constrained_rate == corrected.unconstrained_rate
    assert corrected.clipped is False

    clipped = rogan_gladen_rate(
        0,
        100,
        sensitivity=0.9,
        specificity=0.8,
    )
    assert clipped.unconstrained_rate < 0
    assert clipped.constrained_rate == 0
    assert clipped.clipped is True


def test_aggregation_inputs_fail_closed() -> None:
    with pytest.raises(ValueError):
        apparent_positive_rate(2, 1)
    with pytest.raises(ValueError):
        rogan_gladen_rate(1, 2, sensitivity=0.4, specificity=0.5)
    with pytest.raises(ValueError):
        minimum_cells_for_detection(
            true_cell_rate=0,
            cell_sensitivity=0.9,
            target_detection_probability=0.95,
        )


def test_false_positive_accumulation_is_only_independence_math() -> None:
    assert false_positive_accumulation(
        specificity=0.99,
        examined_cells=100,
    ) == pytest.approx(1 - 0.99**100)


def test_minimum_cell_lower_bound() -> None:
    count = minimum_cells_for_detection(
        true_cell_rate=0.01,
        cell_sensitivity=0.9,
        target_detection_probability=0.95,
    )
    assert count == 332


def test_beta_binomial_exposes_design_effect() -> None:
    moments = beta_binomial_moments(100, alpha=2, beta=18)
    assert moments.mean_count == 10
    assert moments.mean_rate == 0.1
    assert moments.intraclass_correlation == pytest.approx(1 / 21)
    assert moments.design_effect > 1
    assert moments.effective_sample_size < 100


def test_capacity_formulas() -> None:
    assert (
        utilization(
            arrival_rate=7,
            service_rate_per_worker=5,
            workers=2,
        )
        == 0.7
    )
    assert little_law(throughput=4, mean_time_in_system=0.25) == 1

    queue = erlang_c(
        arrival_rate=7,
        service_rate_per_worker=5,
        workers=2,
    )
    assert queue["utilization"] == 0.7
    assert queue["mean_queue_wait"] > 0
    assert queue["mean_requests_in_system"] == pytest.approx(
        7 * queue["mean_time_in_system"]
    )

    with pytest.raises(ValueError, match="stable"):
        erlang_c(arrival_rate=10, service_rate_per_worker=5, workers=2)


def test_memory_and_latency_summary() -> None:
    assert (
        ram_estimate(
            workers=2,
            model_per_worker=100,
            runtime_per_worker=20,
            activation_peak_per_worker=30,
            shared=10,
            upload_buffers=5,
            safety_margin=15,
        )
        == 330
    )

    summary = summarize_latency([10, 20, 30, 40, 50])
    assert summary.count == 5
    assert summary.mean == 30
    assert summary.p50 == 30
    assert summary.p90 == 46
    assert summary.p99 == pytest.approx(49.6)


def test_corruption_severity_zero_is_identity() -> None:
    image = Image.new("RGB", (16, 16), color=(100, 120, 140))
    for corruption in SUPPORTED_CORRUPTIONS:
        output = apply_corruption(image, corruption, 0)
        assert output is not image
        assert ImageChops.difference(output, image).getbbox() is None


def test_corruption_suite_is_deterministic_and_shape_preserving() -> None:
    image = Image.new("RGB", (16, 12), color=(100, 120, 140))
    first = corruption_suite(image, severities=[1, 3], seed=7)
    second = corruption_suite(image, severities=[1, 3], seed=7)
    assert len(first) == len(SUPPORTED_CORRUPTIONS) * 2
    for key, output in first.items():
        assert output.size == image.size
        assert output.mode == "RGB"
        assert output.tobytes() == second[key].tobytes()


def test_corruption_validation() -> None:
    image = Image.new("RGB", (4, 4))
    with pytest.raises(ValueError, match="Unsupported"):
        apply_corruption(image, "unknown", 1)
    with pytest.raises(ValueError, match="severity"):
        apply_corruption(image, "gaussian_blur", 6)


def test_governance_score_formulas_and_domains() -> None:
    assert priority_score(
        impact=5,
        urgency=5,
        evidence=1.0,
        effort=2,
        dependency_complexity=2,
    ) == pytest.approx(12.5)
    assert adjusted_rpn(
        severity=5,
        occurrence=4,
        detectability=5,
        confidence=0.8,
    ) == pytest.approx(120)
    assert quality_score(
        [
            (25, 0),
            (15, 0.5),
            (12, 4),
            (12, 2.5),
            (10, 2),
            (10, 2),
            (8, 4),
            (8, 3),
        ]
    ) == pytest.approx(36.3)

    with pytest.raises(ValueError, match="evidence"):
        priority_score(
            impact=5,
            urgency=5,
            evidence=0.1,
            effort=1,
            dependency_complexity=1,
        )
    with pytest.raises(ValueError, match="total 100"):
        quality_score([(99, 5)])
    with pytest.raises(ValueError, match="integer"):
        adjusted_rpn(
            severity=True,
            occurrence=1,
            detectability=1,
            confidence=1,
        )


def test_aggregation_planning_edge_cases() -> None:
    with pytest.raises(ValueError, match="At least one"):
        apparent_positive_rate(0, 0)
    with pytest.raises(ValueError, match="non-negative"):
        false_positive_accumulation(specificity=0.9, examined_cells=-1)
    with pytest.raises(ValueError, match=r"within \(0, 1\)"):
        minimum_cells_for_detection(
            true_cell_rate=0.1,
            cell_sensitivity=0.9,
            target_detection_probability=1.0,
        )
    assert (
        minimum_cells_for_detection(
            true_cell_rate=1.0,
            cell_sensitivity=1.0,
            target_detection_probability=0.9,
        )
        == 1
    )
    with pytest.raises(ValueError, match="examined_cells"):
        beta_binomial_moments(0, alpha=1, beta=1)
    with pytest.raises(ValueError, match="alpha"):
        beta_binomial_moments(10, alpha=0, beta=1)
    with pytest.raises(ValueError, match="finite"):
        false_positive_accumulation(specificity=math.nan, examined_cells=1)


def test_capacity_planning_edge_cases() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        little_law(throughput=-1, mean_time_in_system=1)
    with pytest.raises(ValueError, match="Memory"):
        ram_estimate(
            workers=0,
            model_per_worker=1,
            runtime_per_worker=1,
            activation_peak_per_worker=1,
            shared=1,
            upload_buffers=1,
            safety_margin=1,
        )
    with pytest.raises(ValueError, match="Finite"):
        summarize_latency([])
    with pytest.raises(ValueError, match="Finite"):
        summarize_latency([math.inf])
    single = summarize_latency([5.0])
    assert single.standard_deviation == 0
    assert single.p99 == 5
    with pytest.raises(ValueError, match="arrival_rate"):
        utilization(arrival_rate=-1, service_rate_per_worker=1, workers=1)


def test_governance_score_edge_cases() -> None:
    with pytest.raises(ValueError, match="At least one"):
        quality_score([])
    with pytest.raises(ValueError, match="Weights"):
        quality_score([(100, math.nan)])
    with pytest.raises(ValueError, match="confidence"):
        adjusted_rpn(
            severity=1,
            occurrence=1,
            detectability=1,
            confidence=math.inf,
        )
