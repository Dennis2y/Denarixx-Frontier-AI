from __future__ import annotations

from typing import Any


EXPECTED_FAMILIES = (
    "echo",
    "boolean",
    "plural",
    "opposite",
    "world_fact",
)

MAX_FAMILY_REGRESSION = 0.05


def _validate_result(result: dict[str, Any], name: str) -> None:
    required = {
        "aggregateResponseLoss",
        "exactMatches",
        "perFamily",
    }

    missing = required - set(result)

    if missing:
        raise ValueError(
            f"{name} missing required fields: "
            + ", ".join(sorted(missing))
        )

    aggregate = float(result["aggregateResponseLoss"])
    exact = int(result["exactMatches"])

    if aggregate < 0:
        raise ValueError(f"{name} aggregate loss must be >= 0")

    if exact < 0:
        raise ValueError(f"{name} exactMatches must be >= 0")

    per_family = result["perFamily"]

    if not isinstance(per_family, dict):
        raise ValueError(f"{name} perFamily must be a dictionary")

    if set(per_family) != set(EXPECTED_FAMILIES):
        raise ValueError(
            f"{name} must contain exactly the five frozen families"
        )

    for family in EXPECTED_FAMILIES:
        data = per_family[family]

        if not isinstance(data, dict):
            raise ValueError(
                f"{name} family {family} must be a dictionary"
            )

        if "responseLoss" not in data:
            raise ValueError(
                f"{name} family {family} missing responseLoss"
            )

        loss = float(data["responseLoss"])

        if loss < 0:
            raise ValueError(
                f"{name} family {family} loss must be >= 0"
            )


def compare_formal_results(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:

    _validate_result(baseline, "baseline")
    _validate_result(candidate, "candidate")

    baseline_loss = float(
        baseline["aggregateResponseLoss"]
    )
    candidate_loss = float(
        candidate["aggregateResponseLoss"]
    )

    baseline_exact = int(
        baseline["exactMatches"]
    )
    candidate_exact = int(
        candidate["exactMatches"]
    )

    minimum_exact = candidate_exact >= 1

    strict_exact_improvement = (
        candidate_exact > baseline_exact
    )

    aggregate_improvement = (
        candidate_loss < baseline_loss
    )

    family_comparison: dict[str, Any] = {}
    all_families_retained = True

    for family in EXPECTED_FAMILIES:
        baseline_family_loss = float(
            baseline["perFamily"][family]["responseLoss"]
        )

        candidate_family_loss = float(
            candidate["perFamily"][family]["responseLoss"]
        )

        if baseline_family_loss == 0.0:
            limit = 0.0
            passed = candidate_family_loss == 0.0
            zero_baseline_rule = True
        else:
            limit = (
                baseline_family_loss
                * (1.0 + MAX_FAMILY_REGRESSION)
            )
            passed = candidate_family_loss <= limit
            zero_baseline_rule = False

        if not passed:
            all_families_retained = False

        family_comparison[family] = {
            "baselineResponseLoss": baseline_family_loss,
            "candidateResponseLoss": candidate_family_loss,
            "maximumAllowedResponseLoss": limit,
            "zeroBaselineRuleApplied": zero_baseline_rule,
            "passed": passed,
        }

    formal_pass = (
        minimum_exact
        and strict_exact_improvement
        and aggregate_improvement
        and all_families_retained
    )

    return {
        "minimumCandidateExactMatchesPassed":
            minimum_exact,
        "strictExactMatchImprovementPassed":
            strict_exact_improvement,
        "aggregateResponseLossImprovementPassed":
            aggregate_improvement,
        "allFiveFamiliesRetentionPassed":
            all_families_retained,
        "perFamilyComparison":
            family_comparison,
        "formalPass":
            formal_pass,
    }
