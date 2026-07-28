"""Tests for deterministic offline statistical validation primitives."""

import math

import pytest

from src.validation.statistics import (
    ConfusionCounts,
    area_under_curve,
    binary_metrics,
    calibration_metrics,
    clopper_pearson_interval,
    cluster_bootstrap_intervals,
    confusion_counts,
    expected_cost,
    mcnemar_exact,
    precision_recall_curve,
    prevalence_predictive_values,
    risk_coverage_curve,
    roc_curve,
    sample_size_for_proportion,
    wilson_interval,
)


def test_confusion_and_binary_metrics() -> None:
    counts = confusion_counts(
        [1, 1, 1, 0, 0, 0],
        [0.9, 0.8, 0.2, 0.7, 0.3, 0.1],
        threshold=0.5,
    )
    assert counts == ConfusionCounts(
        true_positive=2,
        true_negative=2,
        false_positive=1,
        false_negative=1,
    )
    metrics = binary_metrics(counts)
    assert metrics.sensitivity == pytest.approx(2 / 3)
    assert metrics.specificity == pytest.approx(2 / 3)
    assert metrics.ppv == pytest.approx(2 / 3)
    assert metrics.npv == pytest.approx(2 / 3)
    assert metrics.f1 == pytest.approx(2 / 3)
    assert metrics.balanced_accuracy == pytest.approx(2 / 3)
    assert metrics.mcc == pytest.approx(1 / 3)


def test_undefined_metrics_remain_none() -> None:
    metrics = binary_metrics(ConfusionCounts(0, 2, 0, 0))
    assert metrics.sensitivity is None
    assert metrics.false_negative_rate is None
    assert metrics.specificity == 1.0
    assert metrics.ppv is None
    assert metrics.mcc is None


@pytest.mark.parametrize("prevalence", [0.01, 0.05, 0.10, 0.25, 0.50])
def test_prevalence_transport(prevalence: float) -> None:
    ppv, npv = prevalence_predictive_values(0.95, 0.90, prevalence)
    expected_ppv = 0.95 * prevalence / (0.95 * prevalence + 0.10 * (1 - prevalence))
    expected_npv = (
        0.90 * (1 - prevalence) / (0.05 * prevalence + 0.90 * (1 - prevalence))
    )
    assert ppv == pytest.approx(expected_ppv)
    assert npv == pytest.approx(expected_npv)


def test_wilson_and_clopper_pearson_intervals() -> None:
    wilson = wilson_interval(90, 100)
    exact = clopper_pearson_interval(90, 100)
    assert wilson == pytest.approx((0.825634, 0.944771), abs=1e-6)
    assert exact == pytest.approx((0.823777, 0.950995), abs=1e-6)
    assert clopper_pearson_interval(0, 10)[0] == 0.0
    assert clopper_pearson_interval(10, 10)[1] == 1.0


def test_roc_pr_and_auc_perfect_ranking() -> None:
    targets = [0, 0, 1, 1]
    scores = [0.1, 0.2, 0.8, 0.9]
    roc = roc_curve(targets, scores)
    pr = precision_recall_curve(targets, scores)
    assert area_under_curve(
        roc, x_key="false_positive_rate", y_key="true_positive_rate"
    ) == pytest.approx(1.0)
    assert area_under_curve(pr, x_key="recall", y_key="precision") == pytest.approx(1.0)


def test_calibration_metrics_perfect_probabilities_are_small() -> None:
    result = calibration_metrics([0, 0, 1, 1], [0.01, 0.02, 0.98, 0.99], bins=5)
    assert result["brier_score"] == pytest.approx(0.00025)
    assert result["negative_log_likelihood"] < 0.03
    assert result["expected_calibration_error"] == pytest.approx(0.015)
    assert result["reliability"]


def test_risk_coverage_orders_most_confident_first() -> None:
    curve = risk_coverage_curve([1, 0, 1], [0.9, 0.2, 0.4])
    assert curve[0]["coverage"] == pytest.approx(1 / 3)
    assert curve[0]["selective_risk"] == 0.0
    assert curve[-1]["coverage"] == 1.0
    assert curve[-1]["selective_risk"] == pytest.approx(1 / 3)


def test_risk_coverage_accepts_equal_confidence_as_one_group() -> None:
    curve = risk_coverage_curve([1, 0, 1], [0.9, 0.1, 0.6])
    assert curve[0]["coverage"] == pytest.approx(2 / 3)
    assert curve[0]["selective_risk"] == 0.0
    assert curve[-1]["coverage"] == 1.0


def test_cluster_bootstrap_is_seeded_and_clustered() -> None:
    targets = [1, 1, 0, 0, 1, 0]
    scores = [0.9, 0.8, 0.1, 0.2, 0.7, 0.3]
    clusters = ["p1", "p1", "p2", "p2", "p3", "p3"]
    first = cluster_bootstrap_intervals(
        targets,
        scores,
        clusters,
        threshold=0.5,
        resamples=100,
        seed=7,
    )
    second = cluster_bootstrap_intervals(
        targets,
        scores,
        clusters,
        threshold=0.5,
        resamples=100,
        seed=7,
    )
    assert first == second
    assert first["sensitivity"] == (1.0, 1.0)
    assert first["specificity"] == (1.0, 1.0)


def test_sample_size_design_effect() -> None:
    result = sample_size_for_proportion(
        0.95,
        0.03,
        mean_cluster_size=20,
        intraclass_correlation=0.05,
    )
    assert result["design_effect"] == pytest.approx(1.95)
    assert result["adjusted_ceiling"] == math.ceil(
        float(result["iid_unrounded"]) * 1.95
    )


def test_expected_cost_requires_explicit_non_negative_costs() -> None:
    counts = ConfusionCounts(8, 7, 2, 3)
    assert (
        expected_cost(
            counts,
            cost_false_negative=10,
            cost_false_positive=1,
            rejected=2,
            cost_reject=0.5,
        )
        == 33
    )
    with pytest.raises(ValueError):
        expected_cost(
            counts,
            cost_false_negative=-1,
            cost_false_positive=1,
        )


def test_exact_mcnemar() -> None:
    result = mcnemar_exact(
        [True, True, True, False, False],
        [True, False, False, True, False],
    )
    assert result["first_only_correct"] == 2
    assert result["second_only_correct"] == 1
    assert result["discordant"] == 3
    assert result["p_value_two_sided_exact"] == 1.0


@pytest.mark.parametrize(
    ("targets", "scores"),
    [
        ([], []),
        ([0, 2], [0.1, 0.9]),
        ([0, 1], [0.1, math.nan]),
        ([0], [0.1, 0.2]),
    ],
)
def test_invalid_statistical_inputs_fail_closed(
    targets: list[int],
    scores: list[float],
) -> None:
    with pytest.raises(ValueError):
        confusion_counts(targets, scores, threshold=0.5)
