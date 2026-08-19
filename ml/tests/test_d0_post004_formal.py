from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post004_formal.py"
)

spec = importlib.util.spec_from_file_location(
    "d0_post004_formal",
    MODULE_PATH,
)

assert spec is not None
assert spec.loader is not None

formal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(formal)


def synthetic_result(
    loss: float,
    exact: int,
    family_losses: dict[str, float],
):
    return {
        "aggregateResponseLoss": loss,
        "exactMatches": exact,
        "perFamily": {
            family: {
                "responseLoss": value,
                "exactMatches": 0,
            }
            for family, value
            in family_losses.items()
        },
    }


def baseline_result():
    return synthetic_result(
        3.0,
        0,
        {
            family: 3.0
            for family
            in formal.EXPECTED_FAMILIES
        },
    )


def test_pass_at_exact_tolerance_boundaries():
    baseline = baseline_result()

    candidate = synthetic_result(
        3.06,
        1,
        {
            family: 3.15
            for family
            in formal.EXPECTED_FAMILIES
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert result["exactMatchStrictlyImproved"]
    assert result[
        "candidateHasAtLeastOneExactMatch"
    ]
    assert result["aggregateRetentionPassed"]
    assert result["allFamiliesWithinTolerance"]
    assert result["formalPass"]


def test_equal_exact_count_fails():
    baseline = synthetic_result(
        3.0,
        1,
        {
            family: 3.0
            for family
            in formal.EXPECTED_FAMILIES
        },
    )

    candidate = synthetic_result(
        2.9,
        1,
        {
            family: 2.9
            for family
            in formal.EXPECTED_FAMILIES
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert not result[
        "exactMatchStrictlyImproved"
    ]
    assert not result["formalPass"]


def test_zero_exact_fails():
    baseline = baseline_result()

    candidate = synthetic_result(
        2.8,
        0,
        {
            family: 2.8
            for family
            in formal.EXPECTED_FAMILIES
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert not result[
        "candidateHasAtLeastOneExactMatch"
    ]
    assert not result["formalPass"]


def test_aggregate_over_two_percent_fails():
    baseline = baseline_result()

    candidate = synthetic_result(
        3.061,
        1,
        {
            family: 3.0
            for family
            in formal.EXPECTED_FAMILIES
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert not result[
        "aggregateRetentionPassed"
    ]
    assert not result["formalPass"]


def test_single_family_over_five_percent_fails():
    baseline = baseline_result()

    family_losses = {
        family: 3.0
        for family
        in formal.EXPECTED_FAMILIES
    }

    family = sorted(
        formal.EXPECTED_FAMILIES
    )[0]

    family_losses[family] = 3.151

    candidate = synthetic_result(
        3.0,
        1,
        family_losses,
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert not result[
        "allFamiliesWithinTolerance"
    ]
    assert not result["formalPass"]


def test_all_five_families_are_enforced():
    baseline = baseline_result()

    candidate = synthetic_result(
        2.9,
        1,
        {
            "echo": 2.9,
            "binary": 2.9,
            "transform": 2.9,
            "qa": 2.9,
            "semantic": 3.2,
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert len(
        result["perFamilyComparison"]
    ) == 5

    assert not result[
        "perFamilyComparison"
    ]["semantic"]["withinTolerance"]

    assert not result["formalPass"]


def test_better_loss_and_more_exact_pass():
    baseline = synthetic_result(
        3.0,
        2,
        {
            family: 3.0
            for family
            in formal.EXPECTED_FAMILIES
        },
    )

    candidate = synthetic_result(
        2.7,
        3,
        {
            family: 2.8
            for family
            in formal.EXPECTED_FAMILIES
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert result["formalPass"]


def test_parameter_count_constant():
    assert formal.EXPECTED_PARAMETER_COUNT == 102784


def test_architecture_constants():
    assert formal.EXPECTED_VOCAB_SIZE == 42
    assert formal.EXPECTED_CONTEXT_LENGTH == 32
    assert formal.EXPECTED_HIDDEN_SIZE == 64
    assert formal.EXPECTED_LAYERS == 2
    assert formal.EXPECTED_ATTENTION_HEADS == 4
    assert formal.EXPECTED_DROPOUT == 0.0


def test_tolerance_constants():
    assert (
        formal.AGGREGATE_REGRESSION_TOLERANCE
        == 0.02
    )

    assert (
        formal.FAMILY_REGRESSION_TOLERANCE
        == 0.05
    )


def test_dataset_structure_synthetic():
    rows = []

    for family in sorted(
        formal.EXPECTED_FAMILIES
    ):
        for index in range(5):
            rows.append(
                {
                    "family": family,
                    "instruction":
                        f"{family} synthetic {index}",
                    "response": "true",
                }
            )

    formal.validate_dataset_structure(rows)


def test_wrong_family_count_rejected():
    rows = [
        {
            "family": "echo",
            "instruction": "synthetic",
            "response": "true",
        }
    ]

    try:
        formal.validate_dataset_structure(rows)
    except ValueError:
        return

    raise AssertionError(
        "Malformed synthetic dataset accepted"
    )


def test_test_source_does_not_name_real_dataset():
    source = Path(__file__).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "d0_post003_" + "formal.jsonl"
    )

    assert forbidden not in source


def test_scoring_is_locked():
    try:
        formal.run_formal_evaluation(
            "synthetic-baseline",
            "synthetic-candidate",
            "synthetic-dataset",
        )
    except RuntimeError as exc:
        assert "not authorized" in str(exc)
        return

    raise AssertionError(
        "Formal scoring lock did not activate"
    )


TESTS = [
    test_pass_at_exact_tolerance_boundaries,
    test_equal_exact_count_fails,
    test_zero_exact_fails,
    test_aggregate_over_two_percent_fails,
    test_single_family_over_five_percent_fails,
    test_all_five_families_are_enforced,
    test_better_loss_and_more_exact_pass,
    test_parameter_count_constant,
    test_architecture_constants,
    test_tolerance_constants,
    test_dataset_structure_synthetic,
    test_wrong_family_count_rejected,
    test_test_source_does_not_name_real_dataset,
    test_scoring_is_locked,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All POST-004 formal policy tests passed."
    )
