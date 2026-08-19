"""
D0-POST-008 compatibility validator.

This module validates caller-supplied rows against the frozen
POST-008 structural and tokenizer/context compatibility contract.

It does not:

- select or open the POST-008 formal dataset;
- open historical formal datasets;
- load a checkpoint;
- execute a model;
- score a checkpoint;
- train or modify a model;
- create formal-exposure evidence.

The tokenizer and context length must be explicitly supplied by the
caller. Formal checkpoint selection is intentionally outside this
module.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Protocol, Sequence

from post_training.sft_data import (
    InstructionExample,
    encode_instruction,
    format_instruction,
    validate_text_coverage,
)


STAGE = "D0-POST-008"

EXPECTED_FAMILIES = (
    "echo",
    "boolean",
    "plural",
    "opposite",
    "world_fact",
)

EXPECTED_FAMILY_SET = frozenset(EXPECTED_FAMILIES)

EXPECTED_ROWS_PER_FAMILY = 8
EXPECTED_EXAMPLES = 40

EXPECTED_ROW_KEYS = frozenset(
    {
        "family",
        "instruction",
        "response",
    }
)


class CompatibilityError(ValueError):
    """Fail-closed POST-008 compatibility error."""


class TokenizerLike(Protocol):
    def encode(self, text: str) -> list[int]:
        ...


def validate_structure(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    if len(rows) != EXPECTED_EXAMPLES:
        raise CompatibilityError(
            "POST-008 requires exactly "
            f"{EXPECTED_EXAMPLES} rows"
        )

    family_counts: Counter[str] = Counter()

    seen_instructions: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()

    for index, row in enumerate(
        rows,
        start=1,
    ):
        if set(row) != EXPECTED_ROW_KEYS:
            raise CompatibilityError(
                f"row {index} must contain exactly "
                "family, instruction, response"
            )

        family = row["family"]
        instruction = row["instruction"]
        response = row["response"]

        if (
            not isinstance(family, str)
            or not family.strip()
        ):
            raise CompatibilityError(
                f"row {index}: invalid family"
            )

        if family not in EXPECTED_FAMILY_SET:
            raise CompatibilityError(
                f"row {index}: unknown family"
            )

        if (
            not isinstance(instruction, str)
            or not instruction.strip()
        ):
            raise CompatibilityError(
                f"row {index}: invalid instruction"
            )

        if (
            not isinstance(response, str)
            or not response.strip()
        ):
            raise CompatibilityError(
                f"row {index}: invalid response"
            )

        if instruction in seen_instructions:
            raise CompatibilityError(
                f"row {index}: duplicate instruction"
            )

        pair = (instruction, response)

        if pair in seen_pairs:
            raise CompatibilityError(
                f"row {index}: duplicate "
                "instruction/response pair"
            )

        seen_instructions.add(instruction)
        seen_pairs.add(pair)

        family_counts[family] += 1

    if set(family_counts) != EXPECTED_FAMILY_SET:
        raise CompatibilityError(
            "POST-008 family set mismatch"
        )

    for family in EXPECTED_FAMILIES:
        count = family_counts[family]

        if count != EXPECTED_ROWS_PER_FAMILY:
            raise CompatibilityError(
                f"family {family} requires exactly "
                f"{EXPECTED_ROWS_PER_FAMILY} rows"
            )


def validate_row_encoding(
    *,
    row: Mapping[str, Any],
    tokenizer: Any,
    context_length: int,
) -> dict[str, int]:
    if not isinstance(context_length, int):
        raise CompatibilityError(
            "context_length must be an integer"
        )

    if context_length <= 0:
        raise CompatibilityError(
            "context_length must be positive"
        )

    example = InstructionExample(
        instruction=str(row["instruction"]),
        response=str(row["response"]),
    )

    prompt, expected = format_instruction(example)

    try:
        validate_text_coverage(
            tokenizer,
            prompt,
        )

        validate_text_coverage(
            tokenizer,
            expected,
        )

        encoded = encode_instruction(
            tokenizer=tokenizer,
            example=example,
            context_length=context_length,
        )

    except Exception as exc:
        raise CompatibilityError(
            "row is not tokenizer/context compatible: "
            f"{exc}"
        ) from exc

    supervised_tokens = sum(
        1
        for target in encoded.target_ids
        if target != -100
    )

    if supervised_tokens <= 0:
        raise CompatibilityError(
            "row contains no supervised response tokens"
        )

    if len(encoded.input_ids) > context_length:
        raise CompatibilityError(
            "encoded row exceeds context length"
        )

    return {
        "inputTokens": len(encoded.input_ids),
        "supervisedResponseTokens": supervised_tokens,
    }


def validate_compatibility(
    *,
    rows: Sequence[Mapping[str, Any]],
    tokenizer: Any,
    context_length: int,
) -> dict[str, Any]:
    validate_structure(rows)

    per_row: list[dict[str, Any]] = []

    for index, row in enumerate(
        rows,
        start=1,
    ):
        metrics = validate_row_encoding(
            row=row,
            tokenizer=tokenizer,
            context_length=context_length,
        )

        per_row.append(
            {
                "index": index,
                "family": str(row["family"]),
                **metrics,
            }
        )

    return {
        "stage": STAGE,
        "status": "compatible",
        "examples": len(rows),
        "families": list(EXPECTED_FAMILIES),
        "rowsPerFamily":
            EXPECTED_ROWS_PER_FAMILY,
        "contextLength": context_length,
        "rows": per_row,
    }
