"""Offline statistical validation utilities.

These helpers do not validate the currently configured model by themselves.
They provide deterministic calculations after an approved, patient-linked
validation cohort and locked predictions become available.
"""

from src.validation.statistics import (
    BinaryMetrics,
    ConfusionCounts,
    binary_metrics,
    calibration_metrics,
    clopper_pearson_interval,
    cluster_bootstrap_intervals,
    expected_cost,
    mcnemar_exact,
    prevalence_predictive_values,
    risk_coverage_curve,
    sample_size_for_proportion,
    wilson_interval,
)

__all__ = [
    "BinaryMetrics",
    "ConfusionCounts",
    "binary_metrics",
    "calibration_metrics",
    "clopper_pearson_interval",
    "cluster_bootstrap_intervals",
    "expected_cost",
    "mcnemar_exact",
    "prevalence_predictive_values",
    "risk_coverage_curve",
    "sample_size_for_proportion",
    "wilson_interval",
]
