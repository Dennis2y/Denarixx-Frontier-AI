"""
D0-POST-008 scoring dependency adapter.

GOVERNANCE CONTRACT

This module provides the dependency interface required by the frozen
POST-008 execution harness.

It does not:

- embed the POST-008 formal dataset path;
- open historical formal datasets;
- authorize formal execution;
- create formal-exposure evidence;
- select candidate checkpoints;
- perform training or retraining;
- modify checkpoints;
- modify the tokenizer;
- tune adjudication thresholds from formal results.

The execution harness is responsible for supplying the dataset path
and checkpoint paths.

score_checkpoint() accepts rows already loaded by the harness and
does not accept or reopen a dataset path.
"""

from __future__ import annotations

import json
import math

from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from evaluation import d0_post003_dev as dev_eval
from post_training.sft_data import InstructionExample


STAGE = "D0-POST-008"

EXPECTED_ROW_KEYS = frozenset(
    {
        "family",
        "instruction",
        "response",
    }
)


def normalize_response(text: str) -> str:
    """
    Deterministic normalization for exact-match comparison.

    No semantic rewriting or model-dependent transformation occurs.
    """

    return text.strip()


def load_rows(
    path: Path,
) -> list[dict[str, str]]:
    """
    Load rows only from the path explicitly supplied by the harness.

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

            if (
                not isinstance(family, str)
                or not family.strip()
            ):
                raise ValueError(
                    f"row {line_number}: invalid family"
                )

            if (
                not isinstance(instruction, str)
                or not instruction.strip()
            ):
                raise ValueError(
                    f"row {line_number}: invalid instruction"
                )

            if (
                not isinstance(response, str)
                or not response.strip()
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
    Structural validation only.

    POST-008 formal family composition and formal row-count policy
    remain governed by the separately frozen dataset specification.
    This adapter deliberately does not invent those values.
    """

    if not rows:
        raise ValueError(
            "POST-008 dataset contains no rows"
        )

    for index, row in enumerate(
        rows,
        start=1,
    ):
        if set(row) != EXPECTED_ROW_KEYS:
            raise ValueError(
                f"row {index} must contain exactly "
                "family, instruction, response"
            )

        for key in (
            "family",
            "instruction",
            "response",
        ):
            value = row[key]

            if (
                not isinstance(value, str)
                or not value.strip()
            ):
                raise ValueError(
                    f"row {index}: invalid {key}"
                )


def score_checkpoint(
    checkpoint_path: Path,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Deterministically score one checkpoint against already-loaded rows.

    CRITICAL:

    No dataset path is accepted here.

    The harness must load the dataset once and pass the same in-memory
    rows to baseline and candidate scoring.
    """

    validate_rows(rows)

    model, tokenizer, checkpoint = (
        dev_eval.load_model(
            Path(checkpoint_path)
        )
    )

    total_loss_sum = 0.0
    total_tokens = 0
    exact_matches = 0

    family_loss_sum: dict[str, float] = (
        defaultdict(float)
    )

    family_tokens: dict[str, int] = (
        defaultdict(int)
    )

    family_exact: dict[str, int] = (
        defaultdict(int)
    )

    family_examples: dict[str, int] = (
        defaultdict(int)
    )

    results: list[dict[str, Any]] = []

    for index, row in enumerate(
        rows,
        start=1,
    ):
        family = str(row["family"])

        example = InstructionExample(
            instruction=str(
                row["instruction"]
            ),
            response=str(
                row["response"]
            ),
        )

        loss_sum, token_count = (
            dev_eval.response_loss_for_example(
                model,
                tokenizer,
                example,
            )
        )

        if token_count <= 0:
            raise ValueError(
                "POST-008 scoring produced "
                "non-positive response tokens"
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

        total_loss_sum += float(loss_sum)
        total_tokens += int(token_count)
        exact_matches += int(exact)

        family_loss_sum[family] += float(
            loss_sum
        )

        family_tokens[family] += int(
            token_count
        )

        family_exact[family] += int(exact)
        family_examples[family] += 1

        results.append(
            {
                "index": index,
                "family": family,
                "instruction":
                    example.instruction,
                "expected": expected,
                "generated": generated,
                "exactMatch": exact,
                "responseLoss":
                    float(loss_sum)
                    / int(token_count),
                "responseTokens":
                    int(token_count),
            }
        )

    if total_tokens <= 0:
        raise ValueError(
            "POST-008 scoring produced zero tokens"
        )

    families = sorted(
        family_examples.keys()
    )

    per_family: dict[str, Any] = {}

    for family in families:
        tokens = family_tokens[family]

        if tokens <= 0:
            raise ValueError(
                "family produced zero response "
                f"tokens: {family}"
            )

        per_family[family] = {
            "examples":
                family_examples[family],
            "responseTokens":
                tokens,
            "responseLoss":
                family_loss_sum[family]
                / tokens,
            "exactMatches":
                family_exact[family],
        }

    aggregate_loss = (
        total_loss_sum / total_tokens
    )

    return {
        "stage": STAGE,
        "checkpoint":
            str(checkpoint_path),
        "checkpointSha256":
            dev_eval.sha256_file(
                Path(checkpoint_path)
            ),
        "modelName":
            checkpoint.get("model_name"),
        "examples":
            len(rows),
        "responseTokens":
            total_tokens,
        "aggregateResponseLoss":
            aggregate_loss,
        "responsePerplexity":
            math.exp(aggregate_loss),
        "exactMatches":
            exact_matches,
        "exactMatchRate":
            exact_matches / len(rows),
        "families":
            families,
        "perFamily":
            per_family,
        "results":
            results,
    }


def _validate_scoring_result(
    result: Mapping[str, Any],
    name: str,
) -> None:
    required = {
        "stage",
        "checkpoint",
        "checkpointSha256",
        "examples",
        "responseTokens",
        "aggregateResponseLoss",
        "exactMatches",
        "exactMatchRate",
        "families",
        "perFamily",
        "results",
    }

    missing = required.difference(result)

    if missing:
        raise ValueError(
            f"{name} result missing fields: "
            + ", ".join(sorted(missing))
        )

    if result["stage"] != STAGE:
        raise ValueError(
            f"{name} result has wrong stage"
        )

    if int(result["examples"]) <= 0:
        raise ValueError(
            f"{name} result has no examples"
        )

    if int(result["responseTokens"]) <= 0:
        raise ValueError(
            f"{name} result has no response tokens"
        )

    families = result["families"]

    if (
        not isinstance(families, list)
        or not families
    ):
        raise ValueError(
            f"{name} result has invalid families"
        )

    per_family = result["perFamily"]

    if set(per_family) != set(families):
        raise ValueError(
            f"{name} result family mismatch"
        )


def compare_results(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Compare already-persisted aggregate results.

    IMPORTANT:

    This function deliberately does NOT make the final POST-008
    pass/fail decision.

    Formal adjudication thresholds must be frozen separately before
    formal execution. Inventing or inheriting POST-007 thresholds here
    would violate that boundary.
    """

    _validate_scoring_result(
        baseline,
        "baseline",
    )

    _validate_scoring_result(
        candidate,
        "candidate",
    )

    baseline_families = list(
        baseline["families"]
    )

    candidate_families = list(
        candidate["families"]
    )

    if baseline_families != candidate_families:
        raise ValueError(
            "baseline/candidate family sets differ"
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

    family_comparison: dict[str, Any] = {}

    for family in baseline_families:
        baseline_family = (
            baseline["perFamily"][family]
        )

        candidate_family = (
            candidate["perFamily"][family]
        )

        family_comparison[family] = {
            "baselineResponseLoss":
                float(
                    baseline_family[
                        "responseLoss"
                    ]
                ),
            "candidateResponseLoss":
                float(
                    candidate_family[
                        "responseLoss"
                    ]
                ),
            "baselineExactMatches":
                int(
                    baseline_family[
                        "exactMatches"
                    ]
                ),
            "candidateExactMatches":
                int(
                    candidate_family[
                        "exactMatches"
                    ]
                ),
        }

    return {
        "stage": STAGE,
        "status":
            "comparison-complete-"
            "adjudication-not-frozen",
        "baselineCheckpointSha256":
            baseline["checkpointSha256"],
        "candidateCheckpointSha256":
            candidate["checkpointSha256"],
        "baselineAggregateResponseLoss":
            baseline_loss,
        "candidateAggregateResponseLoss":
            candidate_loss,
        "aggregateResponseLossDelta":
            candidate_loss
            - baseline_loss,
        "baselineExactMatches":
            baseline_exact,
        "candidateExactMatches":
            candidate_exact,
        "exactMatchDelta":
            candidate_exact
            - baseline_exact,
        "perFamilyComparison":
            family_comparison,
        "formalPass":
            None,
    }
