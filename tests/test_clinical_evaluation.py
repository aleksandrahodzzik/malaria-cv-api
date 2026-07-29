"""Patient-level evaluation harness and provenance guardrail tests."""

from __future__ import annotations

import csv
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from scripts.evaluate_clinical_cohort import main
from src.validation.clinical import (
    EXTERNAL_EVIDENCE_SCOPE,
    SIMULATION_EVIDENCE_SCOPE,
    SYNTHETIC_ORIGIN,
    ClinicalCohortRecord,
    evaluate_patient_cohort,
    generate_synthetic_cohort,
    load_cohort_csv,
    render_evaluation_report,
    write_cohort_csv,
)


def test_synthetic_cohort_is_deterministic_unique_and_explicit() -> None:
    first = generate_synthetic_cohort()
    second = generate_synthetic_cohort()

    assert first == second
    assert len(first) == 500
    assert sum(record.target for record in first) == 100
    assert len({record.patient_id for record in first}) == 500
    assert len({record.slide_id for record in first}) == 500
    assert {record.record_origin for record in first} == {SYNTHETIC_ORIGIN}


def test_synthetic_generation_rejects_tiny_cohort() -> None:
    with pytest.raises(ValueError, match="at least 20"):
        generate_synthetic_cohort(patient_count=19)


def test_csv_round_trip_and_external_evidence_rejection(tmp_path: Path) -> None:
    path = tmp_path / "cohort.csv"
    records = generate_synthetic_cohort(patient_count=20)
    write_cohort_csv(records, path)
    assert load_cohort_csv(path) == records
    with pytest.raises(ValueError, match="not eligible"):
        load_cohort_csv(path, require_external=True)


def test_empty_records_cannot_be_written_or_evaluated(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="empty"):
        write_cohort_csv([], tmp_path / "empty.csv")
    with pytest.raises(ValueError, match="At least one"):
        evaluate_patient_cohort([])


def test_simulation_evaluation_and_report_are_not_clinical_claims(
    tmp_path: Path,
) -> None:
    path = tmp_path / "cohort.csv"
    records = generate_synthetic_cohort()
    write_cohort_csv(records, path)
    evaluation = evaluate_patient_cohort(records)
    report = render_evaluation_report(evaluation, source=path)

    assert evaluation.patient_count == 500
    assert evaluation.positive_count == 100
    assert evaluation.negative_count == 400
    assert 0.0 < evaluation.auroc < 1.0
    assert 0.0 < evaluation.auprc < 1.0
    assert evaluation.evidence_scope == SIMULATION_EVIDENCE_SCOPE
    assert evaluation.external_validation_eligible is False
    assert "must not be cited as malaria-model" in report
    assert "External validation eligible: `false`" in report


def test_external_observed_records_are_classified_as_candidate_evidence() -> None:
    records = [
        ClinicalCohortRecord(
            patient_id=f"P-{index}",
            slide_id=f"S-{index}",
            record_origin="EXTERNAL_OBSERVED",
            reference_standard="PCR_LOCKED_PROTOCOL_V1",
            target=target,
            model_score=score,
            site="SITE-A",
        )
        for index, (target, score) in enumerate(
            [(0, 0.1), (0, 0.4), (1, 0.6), (1, 0.9)],
            start=1,
        )
    ]
    evaluation = evaluate_patient_cohort(records)
    assert evaluation.evidence_scope == EXTERNAL_EVIDENCE_SCOPE
    assert evaluation.external_validation_eligible is True
    assert evaluation.metrics.sensitivity == 1.0
    assert evaluation.metrics.specificity == 1.0


def test_evaluation_requires_both_classes() -> None:
    record = generate_synthetic_cohort(patient_count=20)[0]
    records = [
        replace(record, patient_id=f"P-{index}", slide_id=f"S-{index}")
        for index in range(2)
    ]
    with pytest.raises(ValueError, match="positive and negative"):
        evaluate_patient_cohort(records)


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "patient_id",
        "slide_id",
        "record_origin",
        "reference_standard",
        "target",
        "model_score",
        "site",
    ]
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _valid_row() -> dict[str, str]:
    return {
        "patient_id": "P-1",
        "slide_id": "S-1",
        "record_origin": "EXTERNAL_OBSERVED",
        "reference_standard": "PCR",
        "target": "1",
        "model_score": "0.9",
        "site": "SITE-A",
    }


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("target", "bad", "invalid target"),
        ("model_score", "nan", "bounds"),
        ("target", "2", "bounds"),
        ("patient_id", " ", "blank"),
    ],
)
def test_loader_rejects_invalid_rows(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    path = tmp_path / f"{field}.csv"
    row = _valid_row()
    row[field] = value
    _write_rows(path, [row])
    with pytest.raises(ValueError, match=message):
        load_cohort_csv(path)


def test_loader_rejects_missing_columns_empty_and_unreadable(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    missing.write_text("patient_id\nP-1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required"):
        load_cohort_csv(missing)

    empty = tmp_path / "empty.csv"
    _write_rows(empty, [])
    with pytest.raises(ValueError, match="no records"):
        load_cohort_csv(empty)

    with pytest.raises(ValueError, match="cannot be read"):
        load_cohort_csv(tmp_path / "absent.csv")


@pytest.mark.parametrize("duplicate_field", ["patient_id", "slide_id"])
def test_loader_rejects_non_independent_identifiers(
    tmp_path: Path,
    duplicate_field: str,
) -> None:
    path = tmp_path / f"duplicate-{duplicate_field}.csv"
    first = _valid_row()
    second = {
        **first,
        "patient_id": "P-2",
        "slide_id": "S-2",
        "target": "0",
        "model_score": "0.1",
    }
    second[duplicate_field] = first[duplicate_field]
    _write_rows(path, [first, second])
    with pytest.raises(ValueError, match=duplicate_field):
        load_cohort_csv(path)


def test_cli_generates_simulation_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cohort = tmp_path / "cohort.csv"
    report = tmp_path / "report.md"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "evaluate_clinical_cohort.py",
            "--input",
            str(cohort),
            "--output",
            str(report),
            "--generate-synthetic",
        ],
    )
    assert main() == 0
    assert cohort.is_file()
    assert "SIMULATION_ONLY" in report.read_text(encoding="utf-8")
    assert "status=PASS patients=500" in capsys.readouterr().out
