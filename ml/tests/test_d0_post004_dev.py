"""Policy-only tests for POST-004 development selector.

These tests MUST NOT load the frozen development
or formal datasets.
"""

from __future__ import annotations

from pathlib import Path
import sys

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from evaluation.d0_post004_dev import (
    select_candidate,
)


def candidate(
    step: int,
    exact: int,
    families: int,
    loss: float,
) -> dict:

    return {
        "candidateStep": step,
        "checkpoint": f"step{step}.pt",
        "checkpointSha256": f"sha{step}",
        "exactMatchCount": exact,
        "familyCoverage": families,
        "aggregateResponseLoss": loss,
    }


def test_rejects_all_zero_exact() -> None:

    result = select_candidate(
        [
            candidate(40, 0, 0, 1.0),
            candidate(80, 0, 0, 0.9),
            candidate(120, 0, 0, 0.8),
        ]
    )

    assert not result[
        "developmentSelectionPass"
    ]

    assert result["selectedCandidate"] is None


def test_exact_match_count_is_primary() -> None:

    result = select_candidate(
        [
            candidate(40, 1, 1, 0.5),
            candidate(80, 2, 1, 1.0),
            candidate(120, 1, 2, 0.1),
        ]
    )

    assert (
        result["selectedCandidate"][
            "candidateStep"
        ]
        == 80
    )


def test_family_coverage_breaks_exact_tie() -> None:

    result = select_candidate(
        [
            candidate(40, 2, 1, 0.2),
            candidate(80, 2, 2, 0.8),
            candidate(120, 1, 1, 0.1),
        ]
    )

    assert (
        result["selectedCandidate"][
            "candidateStep"
        ]
        == 80
    )


def test_loss_breaks_exact_family_tie() -> None:

    result = select_candidate(
        [
            candidate(40, 2, 2, 0.8),
            candidate(80, 2, 2, 0.4),
            candidate(120, 1, 1, 0.1),
        ]
    )

    assert (
        result["selectedCandidate"][
            "candidateStep"
        ]
        == 80
    )


def test_earlier_step_is_final_tiebreak() -> None:

    result = select_candidate(
        [
            candidate(40, 2, 2, 0.4),
            candidate(80, 2, 2, 0.4),
            candidate(120, 2, 2, 0.4),
        ]
    )

    assert (
        result["selectedCandidate"][
            "candidateStep"
        ]
        == 40
    )


def test_source_does_not_reference_formal_dataset() -> None:

    source = (
        ML_ROOT
        / "evaluation"
        / "d0_post004_dev.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "d0_" + "post003_" + "formal.jsonl"
    )

    assert forbidden not in source


def main() -> None:

    tests = [
        test_rejects_all_zero_exact,
        test_exact_match_count_is_primary,
        test_family_coverage_breaks_exact_tie,
        test_loss_breaks_exact_family_tie,
        test_earlier_step_is_final_tiebreak,
        test_source_does_not_reference_formal_dataset,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All POST-004 development selector "
        "policy tests passed."
    )


if __name__ == "__main__":
    main()
