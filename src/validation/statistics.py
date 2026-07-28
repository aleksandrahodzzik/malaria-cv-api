"""Dependency-free statistical primitives for locked binary validation data."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from statistics import NormalDist
from typing import Any

_EPSILON = 1e-15


@dataclass(frozen=True)
class ConfusionCounts:
    """Binary confusion-matrix counts at one declared analysis level."""

    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int

    def __post_init__(self) -> None:
        if min(asdict(self).values()) < 0:
            raise ValueError("Confusion-matrix counts cannot be negative.")

    @property
    def total(self) -> int:
        return (
            self.true_positive
            + self.true_negative
            + self.false_positive
            + self.false_negative
        )


@dataclass(frozen=True)
class BinaryMetrics:
    """Core discrimination metrics without silently replacing undefined values."""

    sensitivity: float | None
    specificity: float | None
    ppv: float | None
    npv: float | None
    f1: float | None
    balanced_accuracy: float | None
    false_positive_rate: float | None
    false_negative_rate: float | None
    mcc: float | None


def _divide(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def confusion_counts(
    y_true: Sequence[int],
    scores: Sequence[float],
    *,
    threshold: float,
) -> ConfusionCounts:
    """Calculate counts after validating labels, scores, and threshold."""
    _validate_binary_inputs(y_true, scores)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be within [0, 1].")

    tp = tn = fp = fn = 0
    for target, score in zip(y_true, scores, strict=True):
        prediction = int(score >= threshold)
        if target == 1 and prediction == 1:
            tp += 1
        elif target == 0 and prediction == 0:
            tn += 1
        elif target == 0 and prediction == 1:
            fp += 1
        else:
            fn += 1
    return ConfusionCounts(tp, tn, fp, fn)


def binary_metrics(counts: ConfusionCounts) -> BinaryMetrics:
    """Compute metrics at one operating threshold."""
    tp = counts.true_positive
    tn = counts.true_negative
    fp = counts.false_positive
    fn = counts.false_negative

    sensitivity = _divide(tp, tp + fn)
    specificity = _divide(tn, tn + fp)
    balanced = (
        (sensitivity + specificity) / 2.0
        if sensitivity is not None and specificity is not None
        else None
    )
    denominator = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return BinaryMetrics(
        sensitivity=sensitivity,
        specificity=specificity,
        ppv=_divide(tp, tp + fp),
        npv=_divide(tn, tn + fn),
        f1=_divide(2 * tp, 2 * tp + fp + fn),
        balanced_accuracy=balanced,
        false_positive_rate=_divide(fp, fp + tn),
        false_negative_rate=_divide(fn, fn + tp),
        mcc=_divide(tp * tn - fp * fn, denominator),
    )


def prevalence_predictive_values(
    sensitivity: float,
    specificity: float,
    prevalence: float,
) -> tuple[float, float]:
    """Transport PPV and NPV to a declared prevalence."""
    _validate_probability(sensitivity, "sensitivity")
    _validate_probability(specificity, "specificity")
    _validate_probability(prevalence, "prevalence")

    ppv_denominator = sensitivity * prevalence + (1 - specificity) * (1 - prevalence)
    npv_denominator = (1 - sensitivity) * prevalence + specificity * (1 - prevalence)
    ppv = _divide(sensitivity * prevalence, ppv_denominator)
    npv = _divide(specificity * (1 - prevalence), npv_denominator)
    if ppv is None or npv is None:
        raise ValueError("Predictive value is undefined for this boundary case.")
    return ppv, npv


def wilson_interval(
    successes: int,
    total: int,
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Wilson score interval for one binomial proportion."""
    _validate_binomial(successes, total)
    if total == 0:
        raise ValueError("Wilson interval requires total > 0.")
    z = _normal_quantile(confidence)
    proportion = successes / total
    z_squared = z * z
    denominator = 1 + z_squared / total
    centre = (proportion + z_squared / (2 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total + z_squared / (4 * total * total)
        )
        / denominator
    )
    return max(0.0, centre - half_width), min(1.0, centre + half_width)


def clopper_pearson_interval(
    successes: int,
    total: int,
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Exact equal-tailed interval by inversion of binomial tail tests."""
    _validate_binomial(successes, total)
    if total == 0:
        raise ValueError("Clopper-Pearson interval requires total > 0.")
    alpha_tail = (1 - confidence) / 2

    lower = 0.0
    if successes > 0:
        lower = _bisect_probability(
            lambda probability: _binomial_upper_tail(successes, total, probability),
            target=alpha_tail,
            increasing=True,
        )

    upper = 1.0
    if successes < total:
        upper = _bisect_probability(
            lambda probability: _binomial_lower_tail(successes, total, probability),
            target=alpha_tail,
            increasing=False,
        )
    return lower, upper


def roc_curve(
    y_true: Sequence[int],
    scores: Sequence[float],
) -> list[dict[str, float]]:
    """Return deterministic ROC points, including the all-negative origin."""
    _validate_binary_inputs(y_true, scores)
    positives = sum(y_true)
    negatives = len(y_true) - positives
    if positives == 0 or negatives == 0:
        raise ValueError("ROC requires both positive and negative examples.")

    points: list[dict[str, float]] = [
        {
            "threshold": math.inf,
            "false_positive_rate": 0.0,
            "true_positive_rate": 0.0,
        }
    ]
    for threshold in sorted(set(scores), reverse=True):
        counts = confusion_counts(y_true, scores, threshold=threshold)
        metrics = binary_metrics(counts)
        assert metrics.sensitivity is not None
        assert metrics.false_positive_rate is not None
        points.append(
            {
                "threshold": threshold,
                "false_positive_rate": metrics.false_positive_rate,
                "true_positive_rate": metrics.sensitivity,
            }
        )
    return points


def precision_recall_curve(
    y_true: Sequence[int],
    scores: Sequence[float],
) -> list[dict[str, float]]:
    """Return thresholded precision-recall points."""
    _validate_binary_inputs(y_true, scores)
    if sum(y_true) == 0:
        raise ValueError("Precision-recall curve requires positive examples.")

    points = [{"threshold": math.inf, "recall": 0.0, "precision": 1.0}]
    for threshold in sorted(set(scores), reverse=True):
        metrics = binary_metrics(confusion_counts(y_true, scores, threshold=threshold))
        assert metrics.sensitivity is not None
        points.append(
            {
                "threshold": threshold,
                "recall": metrics.sensitivity,
                "precision": metrics.ppv if metrics.ppv is not None else 1.0,
            }
        )
    return points


def area_under_curve(
    points: Sequence[dict[str, float]],
    *,
    x_key: str,
    y_key: str,
) -> float:
    """Trapezoidal area for an ordered curve."""
    if len(points) < 2:
        raise ValueError("At least two curve points are required.")
    area = 0.0
    for left, right in zip(points, points[1:], strict=False):
        delta = right[x_key] - left[x_key]
        if delta < 0:
            raise ValueError(f"Curve is not ordered by {x_key}.")
        area += delta * (left[y_key] + right[y_key]) / 2
    return area


def calibration_metrics(
    y_true: Sequence[int],
    probabilities: Sequence[float],
    *,
    bins: int = 10,
) -> dict[str, Any]:
    """Brier, NLL, ECE and reliability bins for binary probabilities."""
    _validate_binary_inputs(y_true, probabilities)
    if bins <= 0:
        raise ValueError("bins must be positive.")

    count = len(y_true)
    clipped = [min(1 - _EPSILON, max(_EPSILON, value)) for value in probabilities]
    brier = (
        sum(
            (probability - target) ** 2
            for target, probability in zip(y_true, probabilities, strict=True)
        )
        / count
    )
    nll = (
        -sum(
            target * math.log(probability) + (1 - target) * math.log(1 - probability)
            for target, probability in zip(y_true, clipped, strict=True)
        )
        / count
    )

    reliability: list[dict[str, float | int]] = []
    ece = 0.0
    for bin_index in range(bins):
        lower = bin_index / bins
        upper = (bin_index + 1) / bins
        indices = [
            index
            for index, value in enumerate(probabilities)
            if lower <= value < upper or (bin_index == bins - 1 and value == 1.0)
        ]
        if not indices:
            continue
        mean_probability = sum(probabilities[index] for index in indices) / len(indices)
        event_rate = sum(y_true[index] for index in indices) / len(indices)
        ece += len(indices) / count * abs(event_rate - mean_probability)
        reliability.append(
            {
                "lower": lower,
                "upper": upper,
                "count": len(indices),
                "mean_probability": mean_probability,
                "event_rate": event_rate,
            }
        )

    intercept, slope = _calibration_logistic_fit(y_true, clipped)
    return {
        "brier_score": brier,
        "negative_log_likelihood": nll,
        "expected_calibration_error": ece,
        "calibration_intercept": intercept,
        "calibration_slope": slope,
        "reliability": reliability,
    }


def risk_coverage_curve(
    y_true: Sequence[int],
    probabilities: Sequence[float],
) -> list[dict[str, float]]:
    """Risk-coverage curve using maximum softmax probability as a baseline."""
    _validate_binary_inputs(y_true, probabilities)
    grouped: dict[float, list[int]] = defaultdict(list)
    for target, probability in zip(y_true, probabilities, strict=True):
        confidence = max(probability, 1 - probability)
        grouped[confidence].append(int((probability >= 0.5) != bool(target)))

    points: list[dict[str, float]] = []
    errors = 0
    accepted = 0
    for confidence in sorted(grouped, reverse=True):
        accepted += len(grouped[confidence])
        errors += sum(grouped[confidence])
        points.append(
            {
                "uncertainty_threshold": 1 - confidence,
                "coverage": accepted / len(y_true),
                "selective_risk": errors / accepted,
            }
        )
    return points


def cluster_bootstrap_intervals(
    y_true: Sequence[int],
    scores: Sequence[float],
    cluster_ids: Sequence[str],
    *,
    threshold: float,
    resamples: int = 2000,
    seed: int = 20260728,
    confidence: float = 0.95,
) -> dict[str, tuple[float, float]]:
    """Percentile cluster bootstrap for sensitivity and specificity."""
    _validate_binary_inputs(y_true, scores)
    if len(cluster_ids) != len(y_true):
        raise ValueError("cluster_ids length must match y_true.")
    if not cluster_ids or any(not cluster_id for cluster_id in cluster_ids):
        raise ValueError("Every observation requires a non-empty cluster ID.")
    if resamples < 2:
        raise ValueError("resamples must be at least 2.")

    by_cluster: dict[str, list[int]] = defaultdict(list)
    for index, cluster_id in enumerate(cluster_ids):
        by_cluster[cluster_id].append(index)
    cluster_names = sorted(by_cluster)
    generator = random.Random(seed)
    sensitivities: list[float] = []
    specificities: list[float] = []

    for _ in range(resamples):
        sampled_clusters = generator.choices(cluster_names, k=len(cluster_names))
        indices = [
            index for cluster_id in sampled_clusters for index in by_cluster[cluster_id]
        ]
        sample_targets = [y_true[index] for index in indices]
        sample_scores = [scores[index] for index in indices]
        metrics = binary_metrics(
            confusion_counts(sample_targets, sample_scores, threshold=threshold)
        )
        if metrics.sensitivity is not None:
            sensitivities.append(metrics.sensitivity)
        if metrics.specificity is not None:
            specificities.append(metrics.specificity)

    if not sensitivities or not specificities:
        raise ValueError(
            "Bootstrap samples did not contain both outcome classes; "
            "the cohort or cluster structure is insufficient."
        )
    return {
        "sensitivity": _percentile_interval(sensitivities, confidence),
        "specificity": _percentile_interval(specificities, confidence),
    }


def sample_size_for_proportion(
    expected: float,
    half_width: float,
    *,
    confidence: float = 0.95,
    mean_cluster_size: float = 1.0,
    intraclass_correlation: float = 0.0,
) -> dict[str, float | int]:
    """Approximate cohort size with an optional clustering design effect."""
    _validate_probability(expected, "expected")
    if not 0 < half_width < 1:
        raise ValueError("half_width must be within (0, 1).")
    if mean_cluster_size < 1:
        raise ValueError("mean_cluster_size must be at least 1.")
    _validate_probability(intraclass_correlation, "intraclass_correlation")

    z = _normal_quantile(confidence)
    independent = z * z * expected * (1 - expected) / (half_width * half_width)
    design_effect = 1 + (mean_cluster_size - 1) * intraclass_correlation
    return {
        "iid_unrounded": independent,
        "design_effect": design_effect,
        "adjusted_unrounded": independent * design_effect,
        "adjusted_ceiling": math.ceil(independent * design_effect),
    }


def expected_cost(
    counts: ConfusionCounts,
    *,
    cost_false_negative: float,
    cost_false_positive: float,
    rejected: int = 0,
    cost_reject: float = 0.0,
    delayed: int = 0,
    cost_delay: float = 0.0,
) -> float:
    """Expected total decision cost for explicitly supplied non-negative costs."""
    values = (
        cost_false_negative,
        cost_false_positive,
        cost_reject,
        cost_delay,
    )
    if min(values) < 0 or rejected < 0 or delayed < 0:
        raise ValueError("Costs and event counts must be non-negative.")
    return (
        cost_false_negative * counts.false_negative
        + cost_false_positive * counts.false_positive
        + cost_reject * rejected
        + cost_delay * delayed
    )


def mcnemar_exact(
    first_correct: Sequence[bool],
    second_correct: Sequence[bool],
) -> dict[str, float | int]:
    """Two-sided exact McNemar test for paired correctness outcomes."""
    if len(first_correct) != len(second_correct) or not first_correct:
        raise ValueError("Paired non-empty outcome sequences are required.")
    first_only = sum(
        first and not second
        for first, second in zip(first_correct, second_correct, strict=True)
    )
    second_only = sum(
        second and not first
        for first, second in zip(first_correct, second_correct, strict=True)
    )
    discordant = first_only + second_only
    if discordant == 0:
        p_value = 1.0
    else:
        smaller = min(first_only, second_only)
        p_value = min(
            1.0,
            2
            * sum(
                math.comb(discordant, index) * 0.5**discordant
                for index in range(smaller + 1)
            ),
        )
    return {
        "first_only_correct": first_only,
        "second_only_correct": second_only,
        "discordant": discordant,
        "p_value_two_sided_exact": p_value,
    }


def _validate_binary_inputs(
    y_true: Sequence[int],
    probabilities: Sequence[float],
) -> None:
    if len(y_true) != len(probabilities) or not y_true:
        raise ValueError("Non-empty y_true and score arrays of equal length required.")
    if any(target not in (0, 1) for target in y_true):
        raise ValueError("y_true must contain only 0 and 1.")
    for value in probabilities:
        _validate_probability(value, "score")


def _validate_probability(value: float, name: str) -> None:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and within [0, 1].")


def _validate_binomial(successes: int, total: int) -> None:
    if successes < 0 or total < 0 or successes > total:
        raise ValueError("Require 0 <= successes <= total.")


def _normal_quantile(confidence: float) -> float:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be within (0, 1).")
    return NormalDist().inv_cdf(0.5 + confidence / 2)


def _log_binomial_probability(k: int, n: int, probability: float) -> float:
    if probability == 0:
        return 0.0 if k == 0 else -math.inf
    if probability == 1:
        return 0.0 if k == n else -math.inf
    return (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
        + k * math.log(probability)
        + (n - k) * math.log1p(-probability)
    )


def _log_sum_exp(values: Sequence[float]) -> float:
    maximum = max(values)
    if maximum == -math.inf:
        return -math.inf
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def _binomial_lower_tail(k: int, n: int, probability: float) -> float:
    logs = [_log_binomial_probability(index, n, probability) for index in range(k + 1)]
    return math.exp(_log_sum_exp(logs))


def _binomial_upper_tail(k: int, n: int, probability: float) -> float:
    logs = [
        _log_binomial_probability(index, n, probability) for index in range(k, n + 1)
    ]
    return math.exp(_log_sum_exp(logs))


def _bisect_probability(
    function: Any,
    *,
    target: float,
    increasing: bool,
) -> float:
    lower = 0.0
    upper = 1.0
    for _ in range(60):
        middle = (lower + upper) / 2
        value = function(middle)
        if (value < target) == increasing:
            lower = middle
        else:
            upper = middle
    return (lower + upper) / 2


def _percentile_interval(
    values: Sequence[float],
    confidence: float,
) -> tuple[float, float]:
    ordered = sorted(values)
    alpha = 1 - confidence
    lower_index = max(0, math.floor(alpha / 2 * (len(ordered) - 1)))
    upper_index = min(
        len(ordered) - 1,
        math.ceil((1 - alpha / 2) * (len(ordered) - 1)),
    )
    return ordered[lower_index], ordered[upper_index]


def _calibration_logistic_fit(
    y_true: Sequence[int],
    probabilities: Sequence[float],
) -> tuple[float | None, float | None]:
    """Fit event ~ intercept + slope*logit(p) with Newton updates."""
    if len(set(y_true)) < 2:
        return None, None
    logits = [math.log(value / (1 - value)) for value in probabilities]
    intercept = 0.0
    slope = 1.0
    for _ in range(100):
        fitted = [
            1 / (1 + math.exp(-max(-700.0, min(700.0, intercept + slope * x))))
            for x in logits
        ]
        weights = [max(_EPSILON, value * (1 - value)) for value in fitted]
        gradient_0 = sum(
            target - value for target, value in zip(y_true, fitted, strict=True)
        )
        gradient_1 = sum(
            (target - value) * x
            for target, value, x in zip(y_true, fitted, logits, strict=True)
        )
        h00 = sum(weights)
        h01 = sum(weight * x for weight, x in zip(weights, logits, strict=True))
        h11 = sum(weight * x * x for weight, x in zip(weights, logits, strict=True))
        determinant = h00 * h11 - h01 * h01
        if determinant <= _EPSILON:
            return None, None
        step_0 = (h11 * gradient_0 - h01 * gradient_1) / determinant
        step_1 = (-h01 * gradient_0 + h00 * gradient_1) / determinant
        intercept += step_0
        slope += step_1
        if max(abs(step_0), abs(step_1)) < 1e-10:
            return intercept, slope
    return intercept, slope
