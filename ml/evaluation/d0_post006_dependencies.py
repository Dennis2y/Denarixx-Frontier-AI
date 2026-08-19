"""
D0-POST-006 dependency bindings.

This module provides the row-based dependency contract required by
d0_post006_execution_harness.

IMPORTANT:

Importing this module does not:
- load a dataset,
- load a checkpoint,
- perform inference,
- execute formal scoring.

The scorer consumes rows already loaded by the execution harness.
"""

from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from evaluation import d0_post003_dev as dev_eval
from evaluation.d0_post006_formal import (
    EXPECTED_FAMILIES,
    compare_formal_results,
)
from post_training.sft_data import InstructionExample


EXPECTED_FAMILY_SET = set(EXPECTED_FAMILIES)


def normalize_response(text: str) -> str:
    """
    Frozen POST-006 exact-match normalization.

    At present the validated historical evaluator uses literal
    generated-response equality. POST-006 therefore preserves that
    behavior rather than introducing an unvalidated transformation.

    This function exists explicitly so baseline and candidate use
    exactly the same frozen operation.
    """
    if not isinstance(text, str):
        raise TypeError("response must be a string")

    return text


def load_rows(path: Path) -> list[dict[str, str]]:
    """
    Load POST-006 rows from the path supplied by the execution harness.

    The function intentionally contains no hard-coded formal path.
    """
    import json

    rows: list[dict[str, str]] = []

    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()

            if not line:
                continue

            payload = json.loads(line)

            if set(payload) != {
                "family",
                "instruction",
                "response",
            }:
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

            if not isinstance(instruction, str) or not instruction:
                raise ValueError(
                    f"row {line_number}: invalid instruction"
                )

            if not isinstance(response, str) or not response:
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

    return rows


def validate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    if len(rows) != 25:
        raise ValueError(
            f"POST-006 requires exactly 25 rows; got {len(rows)}"
        )

    family_counts: dict[str, int] = defaultdict(int)
    normalized_instructions: set[str] = set()

    for index, row in enumerate(rows):
        family = row.get("family")
        instruction = row.get("instruction")
        response = row.get("response")

        if family not in EXPECTED_FAMILY_SET:
            raise ValueError(
                f"row {index}: unexpected family {family!r}"
            )

        if not isinstance(instruction, str) or not instruction:
            raise ValueError(
                f"row {index}: invalid instruction"
            )

        if not isinstance(response, str) or not response:
            raise ValueError(
                f"row {index}: invalid response"
            )

        normalized_instruction = " ".join(
            instruction.strip().lower().split()
        )

        if normalized_instruction in normalized_instructions:
            raise ValueError(
                "duplicate normalized instruction: "
                f"{normalized_instruction}"
            )

        normalized_instructions.add(normalized_instruction)
        family_counts[family] += 1

    if set(family_counts) != EXPECTED_FAMILY_SET:
        raise ValueError(
            "POST-006 family set mismatch"
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

    No dataset path is accepted here. This prevents the scorer from
    independently reopening the sealed formal dataset.

    The returned object is already the fully aggregated POST-006
    result required by the comparison policy.
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

    for index, row in enumerate(rows, start=1):
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
                "responseLoss": loss_sum / token_count,
                "responseTokens": token_count,
            }
        )

    if total_tokens <= 0:
        raise ValueError("POST-006 scoring produced zero tokens")

    per_family: dict[str, Any] = {}

    for family in EXPECTED_FAMILIES:
        tokens = family_tokens[family]

        if tokens <= 0:
            raise ValueError(
                f"family produced zero response tokens: {family}"
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
        "checkpoint": str(checkpoint_path),
        "checkpointSha256":
            dev_eval.sha256_file(Path(checkpoint_path)),
        "modelName": checkpoint.get("model_name"),
        "examples": len(rows),
        "responseTokens": total_tokens,
        "aggregateResponseLoss": aggregate_loss,
        "responsePerplexity": math.exp(aggregate_loss),
        "exactMatches": exact_matches,
        "exactMatchRate": exact_matches / len(rows),
        "perFamily": per_family,
        "results": results,
    }


def compare_results(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    return compare_formal_results(
        dict(baseline),
        dict(candidate),
    )
