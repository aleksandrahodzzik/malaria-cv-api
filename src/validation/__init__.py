"""Offline statistical validation utilities.

These helpers do not validate the currently configured model by themselves.
They provide deterministic calculations after an approved, patient-linked
validation cohort and locked predictions become available.
"""

from src.validation.aggregation import (
    BetaBinomialMoments,
    CorrectedRate,
    apparent_positive_rate,
    beta_binomial_moments,
    false_positive_accumulation,
    minimum_cells_for_detection,
    rogan_gladen_rate,
)
from src.validation.capacity import (
    LatencySummary,
    erlang_c,
    little_law,
    ram_estimate,
    summarize_latency,
    utilization,
)
from src.validation.clinical import (
    ClinicalCohortRecord,
    ClinicalEvaluation,
    evaluate_patient_cohort,
    generate_synthetic_cohort,
    load_cohort_csv,
    render_evaluation_report,
    write_cohort_csv,
)
from src.validation.prioritization import (
    adjusted_rpn,
    priority_score,
    quality_score,
)
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
    "BetaBinomialMoments",
    "ConfusionCounts",
    "CorrectedRate",
    "ClinicalCohortRecord",
    "ClinicalEvaluation",
    "LatencySummary",
    "apparent_positive_rate",
    "adjusted_rpn",
    "beta_binomial_moments",
    "binary_metrics",
    "calibration_metrics",
    "clopper_pearson_interval",
    "cluster_bootstrap_intervals",
    "expected_cost",
    "evaluate_patient_cohort",
    "false_positive_accumulation",
    "erlang_c",
    "little_law",
    "mcnemar_exact",
    "minimum_cells_for_detection",
    "prevalence_predictive_values",
    "priority_score",
    "quality_score",
    "risk_coverage_curve",
    "generate_synthetic_cohort",
    "load_cohort_csv",
    "render_evaluation_report",
    "ram_estimate",
    "rogan_gladen_rate",
    "sample_size_for_proportion",
    "summarize_latency",
    "utilization",
    "wilson_interval",
    "write_cohort_csv",
]
