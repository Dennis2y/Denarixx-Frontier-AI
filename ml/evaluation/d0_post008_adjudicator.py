"""
D0-POST-008 dedicated formal-result adjudicator.

This module implements the independently frozen POST-008
adjudication policy.

It consumes comparison evidence only.

It does not:
- open a dataset;
- load a checkpoint;
- perform inference;
- perform scoring;
- train or retrain;
- create formal-exposure evidence;
- authorize formal execution.
"""

from __future__ import annotations

from typing import Any, Mapping


STAGE = "D0-POST-008"

EXPECTED_FAMILIES = (
    "echo",
    "boolean",
    "plural",
    "opposite",
    "world_fact",
)

MINIMUM_CANDIDATE_EXACT_MATCHES = 1
MAXIMUM_FAMILY_REGRESSION = 0.05


def adjudicate(
    comparison: Mapping[str, Any],
) -> dict[str, Any]:
    if comparison.get("stage") != STAGE:
        raise ValueError("comparison has wrong stage")

    required = {
        "baselineAggregateResponseLoss",
        "candidateAggregateResponseLoss",
        "baselineExactMatches",
        "candidateExactMatches",
        "perFamilyComparison",
    }

    missing = required.difference(comparison)

    if missing:
        raise ValueError(
            "comparison missing required fields: "
            + ", ".join(sorted(missing))
        )

    baseline_loss = float(
        comparison["baselineAggregateResponseLoss"]
    )
    candidate_loss = float(
        comparison["candidateAggregateResponseLoss"]
    )

    baseline_exact = int(
        comparison["baselineExactMatches"]
    )
    candidate_exact = int(
        comparison["candidateExactMatches"]
    )

    minimum_exact_passed = (
        candidate_exact
        >= MINIMUM_CANDIDATE_EXACT_MATCHES
    )

    strict_exact_improvement_passed = (
        candidate_exact > baseline_exact
    )

    aggregate_improvement_passed = (
        candidate_loss < baseline_loss
    )

    raw_families = comparison["perFamilyComparison"]

    if not isinstance(raw_families, Mapping):
        raise ValueError(
            "perFamilyComparison must be a mapping"
        )

    if set(raw_families) != set(EXPECTED_FAMILIES):
        raise ValueError(
            "comparison family set does not match "
            "frozen POST-008 families"
        )

    family_results: dict[str, Any] = {}
    all_families_passed = True

    for family in EXPECTED_FAMILIES:
        entry = raw_families[family]

        if not isinstance(entry, Mapping):
            raise ValueError(
                f"invalid family comparison: {family}"
            )

        if (
            "baselineResponseLoss" not in entry
            or "candidateResponseLoss" not in entry
        ):
            raise ValueError(
                f"family comparison missing loss values: {family}"
            )

        baseline_family_loss = float(
            entry["baselineResponseLoss"]
        )
        candidate_family_loss = float(
            entry["candidateResponseLoss"]
        )

        if baseline_family_loss < 0.0:
            raise ValueError(
                f"negative baseline family loss: {family}"
            )

        if candidate_family_loss < 0.0:
            raise ValueError(
                f"negative candidate family loss: {family}"
            )

        if baseline_family_loss == 0.0:
            maximum_allowed = 0.0
            passed = candidate_family_loss == 0.0
            zero_baseline_rule = True
        else:
            maximum_allowed = (
                baseline_family_loss
                * (1.0 + MAXIMUM_FAMILY_REGRESSION)
            )

            passed = (
                candidate_family_loss
                <= maximum_allowed
            )

            zero_baseline_rule = False

        if not passed:
            all_families_passed = False

        family_results[family] = {
            "baselineResponseLoss":
                baseline_family_loss,
            "candidateResponseLoss":
                candidate_family_loss,
            "maximumAllowedResponseLoss":
                maximum_allowed,
            "zeroBaselineRuleApplied":
                zero_baseline_rule,
            "passed":
                passed,
        }

    formal_pass = (
        minimum_exact_passed
        and strict_exact_improvement_passed
        and aggregate_improvement_passed
        and all_families_passed
    )

    return {
        "stage": STAGE,
        "status": "adjudicated",
        "minimumCandidateExactMatchesPassed":
            minimum_exact_passed,
        "strictExactMatchImprovementPassed":
            strict_exact_improvement_passed,
        "aggregateResponseLossImprovementPassed":
            aggregate_improvement_passed,
        "allFiveFamiliesRetentionPassed":
            all_families_passed,
        "perFamilyAdjudication":
            family_results,
        "formalPass":
            formal_pass,
    }
