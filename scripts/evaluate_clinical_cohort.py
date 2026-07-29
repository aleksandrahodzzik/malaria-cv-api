"""Generate or evaluate a patient-level cohort with provenance guardrails."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.validation.clinical import (  # noqa: E402
    evaluate_patient_cohort,
    generate_synthetic_cohort,
    load_cohort_csv,
    render_evaluation_report,
    write_cohort_csv,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the deterministic command-line contract."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "audit/data/patient_clinical_cohort.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT
        / "audit/remediation/CLINICAL_VALIDATION_REPORT.md",
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--generate-synthetic", action="store_true")
    parser.add_argument("--require-external", action="store_true")
    return parser


def _source_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.name


def main() -> int:
    """Run generation/evaluation and return a process status."""
    arguments = build_parser().parse_args()
    if arguments.generate_synthetic:
        write_cohort_csv(generate_synthetic_cohort(), arguments.input)

    records = load_cohort_csv(
        arguments.input,
        require_external=arguments.require_external,
    )
    evaluation = evaluate_patient_cohort(records, threshold=arguments.threshold)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        render_evaluation_report(
            evaluation,
            source=arguments.input,
            source_label=_source_label(arguments.input),
        ),
        encoding="utf-8",
    )
    print(
        "status=PASS "
        f"patients={evaluation.patient_count} "
        f"scope={evaluation.evidence_scope} "
        f"external_eligible={evaluation.external_validation_eligible}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
