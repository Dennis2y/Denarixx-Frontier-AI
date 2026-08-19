"""
D0-POST-007 formal-evaluation dependency adapter.

IMPORTANT GOVERNANCE CONTRACT

This module contains stage-specific scoring dependencies only.

It does not:
- hard-code the POST-007 formal dataset path;
- create formal-exposure evidence;
- authorize formal execution;
- select checkpoints;
- perform training;
- modify the tokenizer;
- weaken instruction encoding;
- reopen a dataset from score_checkpoint().

The future execution harness is responsible for loading the sealed
formal rows exactly once after the formal-exposure boundary.

Both baseline and candidate scoring receive the same already-loaded
row sequence.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from evaluation import d0_post003_dev as dev_eval
from evaluation.d0_post007_compatibility import (
    EXPECTED_FAMILIES,
)
from post_training.sft_data import InstructionExample


STAGE = "D0-POST-007"

EXPECTED_FAMILIES = tuple(EXPECTED_FAMILIES)
EXPECTED_FAMILY_SET = frozenset(EXPECTED_FAMILIES)

EXPECTED_ROW_KEYS = frozenset(
    {
        "family",
        "instruction",
        "response",
    }
)


def normalize_response(text: str) -> str:
    """
    Preserve literal exact-match semantics.

    POST-007 introduces no candidate-specific or evaluator-specific
    normalization.
    """

    if not isinstance(text, str):
        raise TypeError("response must be a string")

    return text


def load_rows(
    path: Path,
) -> list[dict[str, str]]:
    """
    Load rows from the path explicitly supplied by the future harness.

    No formal dataset path is embedded in this module.
    """

    rows: list[dict[str, str]] = []

    with Path(path).open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, raw in enumerate(
            handle,
            start=1,
        ):
            line = raw.strip()

            if not line:
                continue

            payload = json.loads(line)

            if set(payload) != EXPECTED_ROW_KEYS:
                raise ValueError(
                    f"row {line_number} must contain exactly "
                    "family, instruction, response"
                )

            family = payload["family"]
            instruction = payload["instruction"]
            response = payload["response"]

            if not isinstance(family, str) or not family:
                raise ValueError(
                    f"row {line_number}: invalid family"
                )

            if (
                not isinstance(instruction, str)
                or not instruction
            ):
                raise ValueError(
                    f"row {line_number}: invalid instruction"
                )

            if (
                not isinstance(response, str)
                or not response
            ):
                raise ValueError(
                    f"row {line_number}: invalid response"
                )

            rows.append(
                {
                    "family": family,
                    "instruction": instruction,
                    "response": response,
                }
            )

    validate_rows(rows)

    return rows


def validate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    """
    Validate the frozen POST-007 structural contract.

    This is intentionally model-independent.
    """

    if len(rows) != 25:
        raise ValueError(
            "POST-007 requires exactly 25 rows; "
            f"got {len(rows)}"
        )

    family_counts: dict[str, int] = defaultdict(int)
    normalized_instructions: set[str] = set()

    for index, row in enumerate(rows):
        if set(row) != EXPECTED_ROW_KEYS:
            raise ValueError(
                f"row {index}: unexpected semantic fields"
            )

        family = row.get("family")
        instruction = row.get("instruction")
        response = row.get("response")

        if family not in EXPECTED_FAMILY_SET:
            raise ValueError(
                f"row {index}: unexpected family {family!r}"
            )

        if (
            not isinstance(instruction, str)
            or not instruction
        ):
            raise ValueError(
                f"row {index}: invalid instruction"
            )

        if (
            not isinstance(response, str)
            or not response
        ):
            raise ValueError(
                f"row {index}: invalid response"
            )

        expected_family = EXPECTED_FAMILIES[
            index % len(EXPECTED_FAMILIES)
        ]

        if family != expected_family:
            raise ValueError(
                f"row {index}: expected family "
                f"{expected_family!r}; got {family!r}"
            )

        normalized_instruction = " ".join(
            instruction.strip().lower().split()
        )

        if normalized_instruction in normalized_instructions:
            raise ValueError(
                "duplicate normalized instruction: "
                f"{normalized_instruction}"
            )

        normalized_instructions.add(
            normalized_instruction
        )

        family_counts[str(family)] += 1

    if set(family_counts) != EXPECTED_FAMILY_SET:
        raise ValueError(
            "POST-007 family set mismatch"
        )

    for family in EXPECTED_FAMILIES:
        if family_counts[family] != 5:
            raise ValueError(
                f"{family} requires exactly 5 rows; "
                f"got {family_counts[family]}"
            )


def score_checkpoint(
    checkpoint_path: Path,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Score one checkpoint against rows already loaded by the harness.

    CRITICAL:
    No dataset path is accepted here.

    The future harness must load the sealed dataset once and then
    pass the exact same in-memory rows to baseline and candidate.
    """

    validate_rows(rows)

    model, tokenizer, checkpoint = dev_eval.load_model(
        Path(checkpoint_path)
    )

    total_loss_sum = 0.0
    total_tokens = 0
    exact_matches = 0

    family_loss_sum: dict[str, float] = defaultdict(float)
    family_tokens: dict[str, int] = defaultdict(int)
    family_exact: dict[str, int] = defaultdict(int)
    family_examples: dict[str, int] = defaultdict(int)

    results: list[dict[str, Any]] = []

    for index, row in enumerate(
        rows,
        start=1,
    ):
        family = str(row["family"])

        example = InstructionExample(
            instruction=str(row["instruction"]),
            response=str(row["response"]),
        )

        loss_sum, token_count = (
            dev_eval.response_loss_for_example(
                model,
                tokenizer,
                example,
            )
        )

        generated = dev_eval.greedy_generate(
            model,
            tokenizer,
            example,
        )

        expected = example.response

        exact = (
            normalize_response(generated)
            == normalize_response(expected)
        )

        total_loss_sum += loss_sum
        total_tokens += token_count
        exact_matches += int(exact)

        family_loss_sum[family] += loss_sum
        family_tokens[family] += token_count
        family_exact[family] += int(exact)
        family_examples[family] += 1

        results.append(
            {
                "index": index,
                "family": family,
                "instruction": example.instruction,
                "expected": expected,
                "generated": generated,
                "exactMatch": exact,
                "responseLoss":
                    loss_sum / token_count,
                "responseTokens": token_count,
            }
        )

    if total_tokens <= 0:
        raise ValueError(
            "POST-007 scoring produced zero tokens"
        )

    per_family: dict[str, Any] = {}

    for family in EXPECTED_FAMILIES:
        tokens = family_tokens[family]

        if tokens <= 0:
            raise ValueError(
                "family produced zero response tokens: "
                f"{family}"
            )

        per_family[family] = {
            "examples": family_examples[family],
            "responseTokens": tokens,
            "responseLoss":
                family_loss_sum[family] / tokens,
            "exactMatches": family_exact[family],
        }

    aggregate_loss = total_loss_sum / total_tokens

    return {
        "stage": STAGE,
        "checkpoint": str(checkpoint_path),
        "checkpointSha256":
            dev_eval.sha256_file(Path(checkpoint_path)),
        "modelName": checkpoint.get("model_name"),
        "examples": len(rows),
        "responseTokens": total_tokens,
        "aggregateResponseLoss": aggregate_loss,
        "responsePerplexity": math.exp(aggregate_loss),
        "exactMatches": exact_matches,
        "exactMatchRate":
            exact_matches / len(rows),
        "perFamily": per_family,
        "results": results,
    }


# ------------------------------------------------------------------
# D0-POST-007 frozen formal adjudication comparator
# ------------------------------------------------------------------

MAX_FAMILY_REGRESSION = 0.05
MINIMUM_CANDIDATE_EXACT_MATCHES = 1


def _validate_scoring_result(
    result: dict[str, Any],
    name: str,
) -> None:
    """
    Validate only the aggregate fields required by the frozen
    POST-007 formal adjudication policy.

    This function performs no dataset access and no model access.
    """

    if not isinstance(result, dict):
        raise TypeError(
            f"{name} result must be a dictionary"
        )

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

    aggregate = float(
        result["aggregateResponseLoss"]
    )

    exact = int(
        result["exactMatches"]
    )

    if aggregate < 0:
        raise ValueError(
            f"{name} aggregate response loss must be >= 0"
        )

    if exact < 0:
        raise ValueError(
            f"{name} exactMatches must be >= 0"
        )

    per_family = result["perFamily"]

    if not isinstance(per_family, dict):
        raise ValueError(
            f"{name} perFamily must be a dictionary"
        )

    if set(per_family) != set(EXPECTED_FAMILIES):
        raise ValueError(
            f"{name} must contain exactly the five "
            "frozen POST-007 families"
        )

    for family in EXPECTED_FAMILIES:
        family_result = per_family[family]

        if not isinstance(family_result, dict):
            raise ValueError(
                f"{name} family {family} must be "
                "a dictionary"
            )

        if "responseLoss" not in family_result:
            raise ValueError(
                f"{name} family {family} "
                "missing responseLoss"
            )

        loss = float(
            family_result["responseLoss"]
        )

        if loss < 0:
            raise ValueError(
                f"{name} family {family} "
                "response loss must be >= 0"
            )


def compare_results(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    """
    Apply the frozen D0-POST-007 formal adjudication policy.

    This comparator consumes already aggregated scoring results.

    It performs:
      - no dataset access,
      - no checkpoint loading,
      - no inference,
      - no scoring,
      - no normalization,
      - no threshold adaptation.
    """

    _validate_scoring_result(
        baseline,
        "baseline",
    )

    _validate_scoring_result(
        candidate,
        "candidate",
    )

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

    minimum_exact = (
        candidate_exact
        >= MINIMUM_CANDIDATE_EXACT_MATCHES
    )

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
            baseline["perFamily"][family][
                "responseLoss"
            ]
        )

        candidate_family_loss = float(
            candidate["perFamily"][family][
                "responseLoss"
            ]
        )

        if baseline_family_loss == 0.0:
            maximum_allowed = 0.0

            passed = (
                candidate_family_loss == 0.0
            )

            zero_baseline_rule = True

        else:
            maximum_allowed = (
                baseline_family_loss
                * (1.0 + MAX_FAMILY_REGRESSION)
            )

            passed = (
                candidate_family_loss
                <= maximum_allowed
            )

            zero_baseline_rule = False

        if not passed:
            all_families_retained = False

        family_comparison[family] = {
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
        minimum_exact
        and strict_exact_improvement
        and aggregate_improvement
        and all_families_retained
    )

    return {
        "stage": STAGE,
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
