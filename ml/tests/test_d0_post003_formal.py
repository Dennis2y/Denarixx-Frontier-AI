from __future__ import annotations

import importlib.util
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post003_formal.py"
)

spec = importlib.util.spec_from_file_location(
    "d0_post003_formal",
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
        "responsePerplexity": 2.0,
        "exactMatches": exact,
        "perFamily": {
            family: {
                "responseLoss": value,
                "exactMatches": 0,
            }
            for family, value in family_losses.items()
        },
    }


def test_compare_pass():
    baseline = synthetic_result(
        3.0,
        0,
        {
            "echo": 3.0,
            "binary": 3.0,
            "transform": 3.0,
            "qa": 3.0,
            "semantic": 3.0,
        },
    )

    candidate = synthetic_result(
        2.8,
        0,
        {
            "echo": 2.8,
            "binary": 2.9,
            "transform": 2.7,
            "qa": 3.0,
            "semantic": 3.1,
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert result["aggregateResponseLossImproved"]
    assert result["exactMatchNotWorse"]
    assert result["familiesNoWorse"] == 4
    assert result["familyRequirementPassed"]
    assert result["formalPass"]


def test_equal_aggregate_loss_fails():
    baseline = synthetic_result(
        3.0,
        0,
        {family: 3.0 for family in formal.EXPECTED_FAMILIES},
    )

    candidate = synthetic_result(
        3.0,
        0,
        {family: 2.9 for family in formal.EXPECTED_FAMILIES},
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert not result["aggregateResponseLossImproved"]
    assert not result["formalPass"]


def test_worse_exact_match_fails():
    baseline = synthetic_result(
        3.0,
        2,
        {family: 3.0 for family in formal.EXPECTED_FAMILIES},
    )

    candidate = synthetic_result(
        2.8,
        1,
        {family: 2.8 for family in formal.EXPECTED_FAMILIES},
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert not result["exactMatchNotWorse"]
    assert not result["formalPass"]


def test_only_three_families_no_worse_fails():
    baseline = synthetic_result(
        3.0,
        0,
        {
            "echo": 3.0,
            "binary": 3.0,
            "transform": 3.0,
            "qa": 3.0,
            "semantic": 3.0,
        },
    )

    candidate = synthetic_result(
        2.9,
        0,
        {
            "echo": 2.8,
            "binary": 2.9,
            "transform": 3.0,
            "qa": 3.1,
            "semantic": 3.2,
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert result["familiesNoWorse"] == 3
    assert not result["familyRequirementPassed"]
    assert not result["formalPass"]


def test_four_families_no_worse_passes_requirement():
    baseline = synthetic_result(
        3.0,
        0,
        {
            "echo": 3.0,
            "binary": 3.0,
            "transform": 3.0,
            "qa": 3.0,
            "semantic": 3.0,
        },
    )

    candidate = synthetic_result(
        2.9,
        0,
        {
            "echo": 3.0,
            "binary": 2.9,
            "transform": 2.8,
            "qa": 2.7,
            "semantic": 3.2,
        },
    )

    result = formal.compare_results(
        baseline,
        candidate,
    )

    assert result["familiesNoWorse"] == 4
    assert result["familyRequirementPassed"]


def test_parameter_count_constant():
    assert formal.EXPECTED_PARAMETER_COUNT == 102784


def test_architecture_constants():
    assert formal.EXPECTED_VOCAB_SIZE == 42
    assert formal.EXPECTED_CONTEXT_LENGTH == 32
    assert formal.EXPECTED_HIDDEN_SIZE == 64
    assert formal.EXPECTED_LAYERS == 2
    assert formal.EXPECTED_ATTENTION_HEADS == 4
    assert formal.EXPECTED_DROPOUT == 0.0


def test_dataset_structure_synthetic():
    rows = []

    for family in sorted(formal.EXPECTED_FAMILIES):
        for i in range(5):
            rows.append(
                {
                    "family": family,
                    "instruction": f"{family} synthetic {i}",
                    "response": "true",
                }
            )

    formal.validate_dataset_structure(rows)


def test_dataset_wrong_count_rejected():
    rows = [
        {
            "family": "echo",
            "instruction": "synthetic",
            "response": "synthetic",
        }
    ]

    try:
        formal.validate_dataset_structure(rows)
    except ValueError:
        return

    raise AssertionError(
        "Expected malformed synthetic dataset to be rejected"
    )


def test_formal_test_source_does_not_reference_real_dataset():
    source = Path(__file__).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "d0_post003_" + "formal.jsonl"
    )

    assert forbidden not in source


def test_no_model_scoring_during_import():
    # Importing the evaluator must not create or load any result.
    assert callable(formal.compare_results)
    assert callable(formal.run_formal_evaluation)


if __name__ == "__main__":
    tests = [
        test_compare_pass,
        test_equal_aggregate_loss_fails,
        test_worse_exact_match_fails,
        test_only_three_families_no_worse_fails,
        test_four_families_no_worse_passes_requirement,
        test_parameter_count_constant,
        test_architecture_constants,
        test_dataset_structure_synthetic,
        test_dataset_wrong_count_rejected,
        test_formal_test_source_does_not_reference_real_dataset,
        test_no_model_scoring_during_import,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All POST-003 formal evaluator synthetic tests passed."
    )
