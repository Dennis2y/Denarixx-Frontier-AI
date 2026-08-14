"""Instruction-data utilities for Denarixx D0 supervised fine-tuning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import torch

from tokenizers.char import CharacterTokenizer


IGNORE_INDEX = -100


@dataclass(frozen=True)
class InstructionExample:
    instruction: str
    response: str


@dataclass(frozen=True)
class EncodedInstruction:
    input_ids: list[int]
    target_ids: list[int]
    prompt_tokens: int
    response_tokens: int


def load_instruction_jsonl(
    path: Path,
) -> list[InstructionExample]:
    if not path.exists():
        raise FileNotFoundError(
            f"instruction dataset not found: {path}"
        )

    examples: list[InstructionExample] = []

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line:
            continue

        try:
            payload = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"invalid JSON on line {line_number}"
            ) from error

        instruction = payload.get("instruction")
        response = payload.get("response")

        if not isinstance(instruction, str):
            raise ValueError(
                f"line {line_number}: instruction must be a string"
            )

        if not isinstance(response, str):
            raise ValueError(
                f"line {line_number}: response must be a string"
            )

        if not instruction.strip():
            raise ValueError(
                f"line {line_number}: instruction is empty"
            )

        if not response:
            raise ValueError(
                f"line {line_number}: response is empty"
            )

        examples.append(
            InstructionExample(
                instruction=instruction,
                response=response,
            )
        )

    if not examples:
        raise ValueError(
            "instruction dataset contains no examples"
        )

    return examples


def format_instruction(
    example: InstructionExample,
) -> tuple[str, str]:
    """
    Return prompt and response text separately.

    D0 has a tiny 32-character context. The format is intentionally
    compact so POST-001 can validate the SFT lifecycle without
    pretending D0 is a production assistant.
    """

    # POST-001 must preserve the tokenizer embedded in the
    # accepted pretrained checkpoint. Do not introduce synthetic
    # role markers whose characters may not exist in that vocabulary.
    #
    # A compact newline separator is sufficient for this tiny
    # pipeline-validation experiment.
    prompt = example.instruction + "\n"
    response = example.response + "\n"

    return prompt, response


def validate_text_coverage(
    tokenizer: CharacterTokenizer,
    text: str,
) -> None:
    alphabet = set(tokenizer.alphabet)

    missing = sorted(
        set(text).difference(alphabet)
    )

    if missing:
        rendered = "".join(missing)

        raise ValueError(
            "instruction text contains characters absent "
            f"from pretrained tokenizer: {rendered!r}"
        )


def encode_instruction(
    tokenizer: CharacterTokenizer,
    example: InstructionExample,
    context_length: int,
) -> EncodedInstruction:
    prompt, response = format_instruction(example)

    validate_text_coverage(tokenizer, prompt)
    validate_text_coverage(tokenizer, response)

    prompt_ids = tokenizer.encode(prompt)
    response_ids = tokenizer.encode(response)

    combined = prompt_ids + response_ids

    # For next-token prediction:
    #
    # input  = combined[:-1]
    # target = combined[1:]
    #
    # A target position predicts combined[i + 1].
    # Mask every target whose predicted token belongs to the prompt.
    input_ids = combined[:-1]
    target_ids = combined[1:]

    prompt_target_count = max(
        len(prompt_ids) - 1,
        0,
    )

    masked_targets = (
        [IGNORE_INDEX] * prompt_target_count
        + target_ids[prompt_target_count:]
    )

    if len(input_ids) > context_length:
        raise ValueError(
            "formatted instruction exceeds D0 context length: "
            f"{len(input_ids)} > {context_length}"
        )

    supervised_tokens = sum(
        token != IGNORE_INDEX
        for token in masked_targets
    )

    if supervised_tokens < 1:
        raise ValueError(
            "instruction contains no supervised response tokens"
        )

    return EncodedInstruction(
        input_ids=input_ids,
        target_ids=masked_targets,
        prompt_tokens=len(prompt_ids),
        response_tokens=supervised_tokens,
    )


def encode_dataset(
    tokenizer: CharacterTokenizer,
    examples: list[InstructionExample],
    context_length: int,
) -> list[EncodedInstruction]:
    return [
        encode_instruction(
            tokenizer=tokenizer,
            example=example,
            context_length=context_length,
        )
        for example in examples
    ]


def split_instruction_dataset(
    examples: list[EncodedInstruction],
    validation_fraction: float = 0.25,
) -> tuple[
    list[EncodedInstruction],
    list[EncodedInstruction],
]:
    if len(examples) < 2:
        raise ValueError(
            "SFT dataset needs at least two examples"
        )

    validation_count = max(
        1,
        int(len(examples) * validation_fraction),
    )

    if validation_count >= len(examples):
        validation_count = len(examples) - 1

    train = examples[:-validation_count]
    validation = examples[-validation_count:]

    return train, validation


def collate_examples(
    examples: list[EncodedInstruction],
    pad_token_id: int,
) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
]:
    if not examples:
        raise ValueError(
            "cannot collate an empty SFT batch"
        )

    max_length = max(
        len(example.input_ids)
        for example in examples
    )

    inputs: list[list[int]] = []
    targets: list[list[int]] = []
    attention_mask: list[list[int]] = []

    for example in examples:
        padding = (
            max_length
            - len(example.input_ids)
        )

        inputs.append(
            example.input_ids
            + [pad_token_id] * padding
        )

        targets.append(
            example.target_ids
            + [IGNORE_INDEX] * padding
        )

        attention_mask.append(
            [1] * len(example.input_ids)
            + [0] * padding
        )

    return (
        torch.tensor(
            inputs,
            dtype=torch.long,
        ),
        torch.tensor(
            targets,
            dtype=torch.long,
        ),
        torch.tensor(
            attention_mask,
            dtype=torch.bool,
        ),
    )
