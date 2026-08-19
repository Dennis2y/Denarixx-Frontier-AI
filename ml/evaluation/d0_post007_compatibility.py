from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch

from post_training.sft_data import (
    InstructionExample,
    encode_instruction,
    format_instruction,
    validate_text_coverage,
)
from tokenizers.char import CharacterTokenizer


EXPECTED_FAMILIES = (
    "echo",
    "boolean",
    "plural",
    "opposite",
    "world_fact",
)

EXPECTED_EXAMPLES = 25
EXPECTED_PER_FAMILY = 5

EXPECTED_FIELDS = {
    "instruction",
    "response",
    "family",
}


class CompatibilityError(ValueError):
    pass


@dataclass(frozen=True)
class CompatibilityContract:
    tokenizer: CharacterTokenizer
    context_length: int


def load_compatibility_contract(
    checkpoint_path: Path,
) -> CompatibilityContract:
    """
    Load tokenizer/configuration metadata required for structural
    compatibility validation.

    IMPORTANT:
    This function does NOT construct a model.
    It does NOT load model weights into a model.
    It does NOT execute inference.
    It does NOT compute loss.
    """

    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    if "tokenizer" not in checkpoint:
        raise CompatibilityError(
            "checkpoint missing tokenizer metadata"
        )

    if "model_config" not in checkpoint:
        raise CompatibilityError(
            "checkpoint missing model_config metadata"
        )

    tokenizer = CharacterTokenizer.from_dict(
        checkpoint["tokenizer"]
    )

    config = checkpoint["model_config"]

    if not isinstance(config, Mapping):
        raise CompatibilityError(
            "checkpoint model_config must be a mapping"
        )

    context_length = config.get("context_length")

    if not isinstance(context_length, int):
        raise CompatibilityError(
            "checkpoint context_length must be an integer"
        )

    if context_length < 2:
        raise CompatibilityError(
            "checkpoint context_length is invalid"
        )

    return CompatibilityContract(
        tokenizer=tokenizer,
        context_length=context_length,
    )


def validate_structure(
    rows: Sequence[Mapping[str, Any]],
) -> None:

    if len(rows) != EXPECTED_EXAMPLES:
        raise CompatibilityError(
            "POST-007 dataset must contain exactly "
            f"{EXPECTED_EXAMPLES} rows"
        )

    family_counts: Counter[str] = Counter()

    instructions: set[str] = set()
    complete_rows: set[tuple[str, str, str]] = set()

    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise CompatibilityError(
                f"row {index} must be a mapping"
            )

        if set(row) != EXPECTED_FIELDS:
            raise CompatibilityError(
                f"row {index} must contain exactly "
                "instruction, response, family"
            )

        instruction = row["instruction"]
        response = row["response"]
        family = row["family"]

        if not isinstance(instruction, str):
            raise CompatibilityError(
                f"row {index} instruction must be a string"
            )

        if not instruction.strip():
            raise CompatibilityError(
                f"row {index} instruction is empty"
            )

        if not isinstance(response, str):
            raise CompatibilityError(
                f"row {index} response must be a string"
            )

        if not response:
            raise CompatibilityError(
                f"row {index} response is empty"
            )

        if family not in EXPECTED_FAMILIES:
            raise CompatibilityError(
                f"row {index} has invalid family: {family!r}"
            )

        if instruction in instructions:
            raise CompatibilityError(
                f"duplicate instruction at row {index}"
            )

        instructions.add(instruction)

        identity = (
            instruction,
            response,
            family,
        )

        if identity in complete_rows:
            raise CompatibilityError(
                f"duplicate complete row at row {index}"
            )

        complete_rows.add(identity)
        family_counts[family] += 1

    expected_counts = {
        family: EXPECTED_PER_FAMILY
        for family in EXPECTED_FAMILIES
    }

    if dict(family_counts) != expected_counts:
        raise CompatibilityError(
            "POST-007 dataset must contain exactly "
            "five rows per family"
        )

    for cycle in range(EXPECTED_PER_FAMILY):
        start = cycle * len(EXPECTED_FAMILIES)
        end = start + len(EXPECTED_FAMILIES)

        observed = tuple(
            str(row["family"])
            for row in rows[start:end]
        )

        if observed != EXPECTED_FAMILIES:
            raise CompatibilityError(
                "POST-007 rows must use deterministic "
                "five-family interleaving"
            )


def validate_row_encoding(
    row: Mapping[str, Any],
    *,
    contract: CompatibilityContract,
    index: int,
) -> None:

    example = InstructionExample(
        instruction=str(row["instruction"]),
        response=str(row["response"]),
    )

    prompt, response = format_instruction(example)

    try:
        validate_text_coverage(
            contract.tokenizer,
            prompt,
        )
    except ValueError as exc:
        raise CompatibilityError(
            f"row {index} prompt tokenizer coverage failed: "
            f"{exc}"
        ) from exc

    try:
        validate_text_coverage(
            contract.tokenizer,
            response,
        )
    except ValueError as exc:
        raise CompatibilityError(
            f"row {index} response tokenizer coverage failed: "
            f"{exc}"
        ) from exc

    try:
        encoded = encode_instruction(
            tokenizer=contract.tokenizer,
            example=example,
            context_length=contract.context_length,
        )
    except ValueError as exc:
        raise CompatibilityError(
            f"row {index} instruction encoding failed: {exc}"
        ) from exc

    if encoded.response_tokens < 1:
        raise CompatibilityError(
            f"row {index} contains no supervised response tokens"
        )


def validate_compatibility(
    rows: Sequence[Mapping[str, Any]],
    *,
    contract: CompatibilityContract,
) -> dict[str, Any]:

    validate_structure(rows)

    for index, row in enumerate(rows, start=1):
        validate_row_encoding(
            row,
            contract=contract,
            index=index,
        )

    return {
        "stage": "D0-POST-007",
        "compatible": True,
        "rowsValidated": len(rows),
        "families": list(EXPECTED_FAMILIES),
        "rowsPerFamily": EXPECTED_PER_FAMILY,
        "modelInferenceExecuted": False,
        "lossComputed": False,
        "candidateCheckpointRequired": False,
    }
