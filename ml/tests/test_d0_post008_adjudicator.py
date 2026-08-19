from __future__ import annotations

import copy

import pytest

from evaluation.d0_post008_adjudicator import adjudicate


FAMILIES = (
    "echo",
    "boolean",
    "plural",
    "opposite",
    "world_fact",
)


def comparison(
    *,
    baseline_loss=2.0,
    candidate_loss=1.9,
    baseline_exact=0,
    candidate_exact=1,
    baseline_family_loss=1.0,
    candidate_family_loss=1.0,
):
    return {
        "stage": "D0-POST-008",
        "baselineAggregateResponseLoss":
            baseline_loss,
        "candidateAggregateResponseLoss":
            candidate_loss,
        "baselineExactMatches":
            baseline_exact,
        "candidateExactMatches":
            candidate_exact,
        "perFamilyComparison": {
            family: {
                "baselineResponseLoss":
                    baseline_family_loss,
                "candidateResponseLoss":
                    candidate_family_loss,
                "baselineExactMatches": 0,
                "candidateExactMatches": 0,
            }
            for family in FAMILIES
        },
    }


def test_all_conditions_pass():
    result = adjudicate(comparison())
    assert result["formalPass"] is True


def test_candidate_must_have_at_least_one_exact_match():
    value = comparison(
        baseline_exact=0,
        candidate_exact=0,
    )

    result = adjudicate(value)

    assert (
        result["minimumCandidateExactMatchesPassed"]
        is False
    )
    assert result["formalPass"] is False


def test_exact_match_must_strictly_improve():
    value = comparison(
        baseline_exact=1,
        candidate_exact=1,
    )

    result = adjudicate(value)

    assert (
        result["strictExactMatchImprovementPassed"]
        is False
    )
    assert result["formalPass"] is False


def test_aggregate_loss_must_strictly_improve():
    value = comparison(
        baseline_loss=2.0,
        candidate_loss=2.0,
    )

    result = adjudicate(value)

    assert (
        result["aggregateResponseLossImprovementPassed"]
        is False
    )
    assert result["formalPass"] is False


def test_exact_five_percent_family_regression_passes():
    value = comparison(
        baseline_family_loss=1.0,
        candidate_family_loss=1.05,
    )

    result = adjudicate(value)

    assert (
        result["allFiveFamiliesRetentionPassed"]
        is True
    )
    assert result["formalPass"] is True


def test_more_than_five_percent_family_regression_fails():
    value = comparison()

    value["perFamilyComparison"]["plural"][
        "candidateResponseLoss"
    ] = 1.050001

    result = adjudicate(value)

    assert (
        result["perFamilyAdjudication"]["plural"][
            "passed"
        ]
        is False
    )
    assert (
        result["allFiveFamiliesRetentionPassed"]
        is False
    )
    assert result["formalPass"] is False


def test_zero_baseline_requires_zero_candidate():
    value = comparison()

    value["perFamilyComparison"]["echo"][
        "baselineResponseLoss"
    ] = 0.0

    value["perFamilyComparison"]["echo"][
        "candidateResponseLoss"
    ] = 0.000001

    result = adjudicate(value)

    assert (
        result["perFamilyAdjudication"]["echo"][
            "zeroBaselineRuleApplied"
        ]
        is True
    )
    assert result["formalPass"] is False


def test_zero_baseline_and_zero_candidate_passes():
    value = comparison()

    value["perFamilyComparison"]["echo"][
        "baselineResponseLoss"
    ] = 0.0

    value["perFamilyComparison"]["echo"][
        "candidateResponseLoss"
    ] = 0.0

    result = adjudicate(value)

    assert (
        result["perFamilyAdjudication"]["echo"][
            "passed"
        ]
        is True
    )
    assert result["formalPass"] is True


def test_one_failed_family_causes_formal_failure():
    value = comparison()

    value["perFamilyComparison"]["world_fact"][
        "candidateResponseLoss"
    ] = 1.2

    result = adjudicate(value)

    assert result["formalPass"] is False


def test_wrong_stage_rejected():
    value = comparison()
    value["stage"] = "WRONG"

    with pytest.raises(
        ValueError,
        match="wrong stage",
    ):
        adjudicate(value)


def test_family_set_mismatch_rejected():
    value = comparison()

    del value["perFamilyComparison"]["boolean"]

    with pytest.raises(
        ValueError,
        match="family set",
    ):
        adjudicate(value)


def test_missing_required_field_rejected():
    value = comparison()

    del value["candidateExactMatches"]

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        adjudicate(value)


def test_negative_family_loss_rejected():
    value = comparison()

    value["perFamilyComparison"]["opposite"][
        "candidateResponseLoss"
    ] = -0.1

    with pytest.raises(
        ValueError,
        match="negative candidate family loss",
    ):
        adjudicate(value)


def test_input_is_not_modified():
    value = comparison()
    original = copy.deepcopy(value)

    adjudicate(value)

    assert value == original
