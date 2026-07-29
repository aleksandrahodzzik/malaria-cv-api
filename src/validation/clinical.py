"""Patient-level evaluation harness with strict provenance classification.

Synthetic records exercise statistical code only. They are never accepted as
external clinical validation or evidence of real model performance.
"""

from __future__ import annotations

import csv
import hashlib
import random
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from src.validation.statistics import (
    BinaryMetrics,
    ConfusionCounts,
    area_under_curve,
    binary_metrics,
    confusion_counts,
    precision_recall_curve,
    roc_curve,
    wilson_interval,
)

SYNTHETIC_ORIGIN = "SYNTHETIC_SIMULATION"
SYNTHETIC_REFERENCE = "SIMULATED_LABEL_NO_BIOLOGICAL_SPECIMEN"
SIMULATION_EVIDENCE_SCOPE = "SIMULATION_ONLY_NOT_EXTERNAL_VALIDATION"
EXTERNAL_EVIDENCE_SCOPE = "EXTERNAL_OBSERVED_VALIDATION_CANDIDATE"

_REQUIRED_COLUMNS = {
    "patient_id",
    "slide_id",
    "record_origin",
    "reference_standard",
    "target",
    "model_score",
    "site",
}


@dataclass(frozen=True, slots=True)
class ClinicalCohortRecord:
    """One patient-independent slide record."""

    patient_id: str
    slide_id: str
    record_origin: str
    reference_standard: str
    target: int
    model_score: float
    site: str


@dataclass(frozen=True, slots=True)
class ClinicalEvaluation:
    """Patient-level discrimination results at one locked threshold."""

    patient_count: int
    positive_count: int
    negative_count: int
    threshold: float
    counts: ConfusionCounts
    metrics: BinaryMetrics
    auroc: float
    auprc: float
    sensitivity_95_ci: tuple[float, float]
    specificity_95_ci: tuple[float, float]
    evidence_scope: str
    external_validation_eligible: bool


def generate_synthetic_cohort(
    *,
    patient_count: int = 500,
    seed: int = 20260729,
) -> list[ClinicalCohortRecord]:
    """Generate deterministic simulation records without clinical provenance."""
    if patient_count < 20:
        raise ValueError("Synthetic cohort requires at least 20 patients.")
    randomizer = random.Random(seed)
    sites = ("SIMULATED_SITE_A", "SIMULATED_SITE_B", "SIMULATED_SITE_C")
    records: list[ClinicalCohortRecord] = []
    for index in range(1, patient_count + 1):
        target = int(index % 5 == 0)
        centre = 0.72 if target else 0.28
        score = min(0.99, max(0.01, centre + randomizer.uniform(-0.35, 0.35)))
        records.append(
            ClinicalCohortRecord(
                patient_id=f"SYN-PAT-{index:04d}",
                slide_id=f"SYN-SLIDE-{index:04d}",
                record_origin=SYNTHETIC_ORIGIN,
                reference_standard=SYNTHETIC_REFERENCE,
                target=target,
                model_score=round(score, 6),
                site=sites[(index - 1) % len(sites)],
            )
        )
    return records


def write_cohort_csv(
    records: Sequence[ClinicalCohortRecord],
    destination: Path,
) -> None:
    """Write a deterministic cohort artifact with explicit provenance columns."""
    if not records:
        raise ValueError("Cannot write an empty cohort.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "patient_id",
                "slide_id",
                "record_origin",
                "reference_standard",
                "target",
                "model_score",
                "site",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "patient_id": record.patient_id,
                    "slide_id": record.slide_id,
                    "record_origin": record.record_origin,
                    "reference_standard": record.reference_standard,
                    "target": record.target,
                    "model_score": f"{record.model_score:.6f}",
                    "site": record.site,
                }
            )


def load_cohort_csv(
    source: Path,
    *,
    require_external: bool = False,
) -> list[ClinicalCohortRecord]:
    """Load and validate unique patient/slide records from a CSV artifact."""
    try:
        with source.open("r", encoding="utf-8", newline="") as cohort_file:
            reader = csv.DictReader(cohort_file)
            columns = set(reader.fieldnames or ())
            missing = _REQUIRED_COLUMNS - columns
            if missing:
                raise ValueError(
                    "Cohort is missing required columns: " + ", ".join(sorted(missing))
                )
            rows = list(reader)
    except OSError as exc:
        raise ValueError("Cohort file cannot be read.") from exc

    if not rows:
        raise ValueError("Cohort contains no records.")

    records: list[ClinicalCohortRecord] = []
    for row_number, row in enumerate(rows, start=2):
        try:
            target = int(row["target"])
            model_score = float(row["model_score"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Cohort row {row_number} has invalid target or score."
            ) from exc
        if target not in {0, 1} or not 0.0 <= model_score <= 1.0:
            raise ValueError(
                f"Cohort row {row_number} violates binary label/score bounds."
            )
        text_values = {
            name: row[name].strip()
            for name in (
                "patient_id",
                "slide_id",
                "record_origin",
                "reference_standard",
                "site",
            )
        }
        if not all(text_values.values()):
            raise ValueError(f"Cohort row {row_number} contains blank metadata.")
        records.append(
            ClinicalCohortRecord(
                **text_values,
                target=target,
                model_score=model_score,
            )
        )

    patient_ids = [record.patient_id for record in records]
    slide_ids = [record.slide_id for record in records]
    if len(set(patient_ids)) != len(patient_ids):
        raise ValueError("Cohort patient_id values must be unique.")
    if len(set(slide_ids)) != len(slide_ids):
        raise ValueError("Cohort slide_id values must be unique.")
    if require_external and any(
        record.record_origin != "EXTERNAL_OBSERVED" for record in records
    ):
        raise ValueError(
            "Cohort is not eligible for external clinical validation evidence."
        )
    return records


def evaluate_patient_cohort(
    records: Sequence[ClinicalCohortRecord],
    *,
    threshold: float = 0.5,
) -> ClinicalEvaluation:
    """Calculate patient-level metrics while preserving evidence provenance."""
    if not records:
        raise ValueError("At least one patient record is required.")
    targets = [record.target for record in records]
    scores = [record.model_score for record in records]
    counts = confusion_counts(targets, scores, threshold=threshold)
    metrics = binary_metrics(counts)
    if metrics.sensitivity is None or metrics.specificity is None:
        raise ValueError("Evaluation requires positive and negative patients.")

    roc_points = roc_curve(targets, scores)
    pr_points = precision_recall_curve(targets, scores)
    all_external = all(
        record.record_origin == "EXTERNAL_OBSERVED"
        and record.reference_standard not in {SYNTHETIC_REFERENCE, ""}
        for record in records
    )
    return ClinicalEvaluation(
        patient_count=len(records),
        positive_count=sum(targets),
        negative_count=len(records) - sum(targets),
        threshold=threshold,
        counts=counts,
        metrics=metrics,
        auroc=area_under_curve(
            roc_points,
            x_key="false_positive_rate",
            y_key="true_positive_rate",
        ),
        auprc=area_under_curve(
            pr_points,
            x_key="recall",
            y_key="precision",
        ),
        sensitivity_95_ci=wilson_interval(
            counts.true_positive,
            counts.true_positive + counts.false_negative,
        ),
        specificity_95_ci=wilson_interval(
            counts.true_negative,
            counts.true_negative + counts.false_positive,
        ),
        evidence_scope=(
            EXTERNAL_EVIDENCE_SCOPE if all_external else SIMULATION_EVIDENCE_SCOPE
        ),
        external_validation_eligible=all_external,
    )


def render_evaluation_report(
    evaluation: ClinicalEvaluation,
    *,
    source: Path,
    source_label: str | None = None,
) -> str:
    """Render a report that cannot silently promote simulation to evidence."""
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    displayed_source = source_label or source.as_posix()
    metrics = evaluation.metrics
    counts_text = (
        f"{evaluation.counts.true_positive}/"
        f"{evaluation.counts.true_negative}/"
        f"{evaluation.counts.false_positive}/"
        f"{evaluation.counts.false_negative}"
    )
    sensitivity_ci_text = (
        f"[{evaluation.sensitivity_95_ci[0]:.6f}, "
        f"{evaluation.sensitivity_95_ci[1]:.6f}]"
    )
    specificity_ci_text = (
        f"[{evaluation.specificity_95_ci[0]:.6f}, "
        f"{evaluation.specificity_95_ci[1]:.6f}]"
    )
    return f"""# Patient-level evaluation harness report

Evidence classification: **{evaluation.evidence_scope}**

> This report verifies the evaluation pipeline. It does not establish clinical
> performance when `external_validation_eligible` is false.

## Provenance

- Source: `{displayed_source}`
- SHA-256: `{digest}`
- Patients: {evaluation.patient_count}
- Positive: {evaluation.positive_count}
- Negative: {evaluation.negative_count}
- External validation eligible: `{str(evaluation.external_validation_eligible).lower()}`

## Locked operating point

- Threshold: {evaluation.threshold:.4f}
- TP/TN/FP/FN: {counts_text}
- Sensitivity: {metrics.sensitivity:.6f}
- Sensitivity Wilson 95% CI: {sensitivity_ci_text}
- Specificity: {metrics.specificity:.6f}
- Specificity Wilson 95% CI: {specificity_ci_text}
- AUROC: {evaluation.auroc:.6f}
- AUPRC: {evaluation.auprc:.6f}

## Interpretation boundary

These values describe deterministic simulated scores when the source records
are marked `{SYNTHETIC_ORIGIN}`. They must not be cited as malaria-model
accuracy, PCR validation, expert-microscopy validation, external validation,
regulatory evidence, or justification for clinical deployment.
"""
