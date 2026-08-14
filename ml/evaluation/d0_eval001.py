"""Canonical checkpoint evaluation for D0-EVAL-001."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import torch
from torch import nn

from inference.d0_inference import (
    load_checkpoint,
    run_greedy_inference,
)


@dataclass(frozen=True)
class LanguageModelEvaluation:
    average_loss: float
    perplexity: float
    tokens_evaluated: int
    windows_evaluated: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InstructionEvaluation:
    response_loss: float
    response_perplexity: float
    response_tokens_evaluated: int
    examples_evaluated: int
    exact_matches: int

    @property
    def exact_match_rate(self) -> float:
        return self.exact_matches / self.examples_evaluated

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["exact_match_rate"] = self.exact_match_rate
        return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def validate_tokenizer_coverage(
    tokenizer: Any,
    text: str,
) -> None:
    alphabet = set(tokenizer.alphabet)

    unknown = sorted(
        set(text) - alphabet
    )

    if unknown:
        raise ValueError(
            "evaluation text contains characters "
            f"outside checkpoint tokenizer: {unknown!r}"
        )


def load_instruction_examples(
    path: Path,
) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            payload = json.loads(line)

            instruction = payload.get(
                "instruction"
            )

            response = payload.get(
                "response"
            )

            if (
                not isinstance(instruction, str)
                or not instruction
            ):
                raise ValueError(
                    "invalid instruction at line "
                    f"{line_number}"
                )

            if (
                not isinstance(response, str)
                or not response
            ):
                raise ValueError(
                    "invalid response at line "
                    f"{line_number}"
                )

            examples.append(
                {
                    "instruction": instruction,
                    "response": response,
                }
            )

    if not examples:
        raise ValueError(
            "instruction evaluation set is empty"
        )

    return examples


def evaluate_language_model_tokens(
    *,
    model: nn.Module,
    tokens: list[int],
    context_length: int,
) -> LanguageModelEvaluation:
    if context_length < 1:
        raise ValueError(
            "context_length must be positive"
        )

    if len(tokens) < 2:
        raise ValueError(
            "language-model evaluation requires "
            "at least two tokens"
        )

    model.eval()

    total_nll = 0.0
    total_tokens = 0
    windows = 0

    with torch.no_grad():
        start = 0

        while start < len(tokens) - 1:
            end = min(
                start + context_length,
                len(tokens) - 1,
            )

            x_values = tokens[start:end]
            y_values = tokens[
                start + 1 : end + 1
            ]

            if not x_values:
                break

            x = torch.tensor(
                [x_values],
                dtype=torch.long,
            )

            y = torch.tensor(
                [y_values],
                dtype=torch.long,
            )

            logits, _ = model(x)

            token_count = int(y.numel())

            loss_sum = nn.functional.cross_entropy(
                logits.reshape(
                    -1,
                    logits.size(-1),
                ),
                y.reshape(-1),
                reduction="sum",
            )

            total_nll += float(
                loss_sum.item()
            )

            total_tokens += token_count
            windows += 1
            start = end

    if total_tokens == 0:
        raise RuntimeError(
            "no language-model evaluation tokens"
        )

    average_loss = total_nll / total_tokens

    try:
        perplexity = math.exp(average_loss)
    except OverflowError:
        perplexity = math.inf

    return LanguageModelEvaluation(
        average_loss=average_loss,
        perplexity=perplexity,
        tokens_evaluated=total_tokens,
        windows_evaluated=windows,
    )


def evaluate_instruction_examples(
    *,
    checkpoint_path: Path,
    model: nn.Module,
    tokenizer: Any,
    examples: list[dict[str, str]],
    context_length: int,
) -> InstructionEvaluation:
    if not examples:
        raise ValueError(
            "instruction evaluation requires examples"
        )

    model.eval()

    total_nll = 0.0
    total_response_tokens = 0
    exact_matches = 0

    with torch.no_grad():
        for example in examples:
            prompt = (
                example["instruction"]
                + "\n"
            )

            response = (
                example["response"]
                + "\n"
            )

            full_text = prompt + response

            validate_tokenizer_coverage(
                tokenizer,
                full_text,
            )

            full_tokens = tokenizer.encode(
                full_text
            )

            prompt_tokens = tokenizer.encode(
                prompt
            )

            if len(full_tokens) < 2:
                raise ValueError(
                    "instruction example is too short"
                )

            if (
                len(full_tokens) - 1
                > context_length
            ):
                raise ValueError(
                    "instruction evaluation example "
                    "exceeds checkpoint context length"
                )

            x = torch.tensor(
                [full_tokens[:-1]],
                dtype=torch.long,
            )

            targets = torch.tensor(
                [full_tokens[1:]],
                dtype=torch.long,
            )

            logits, _ = model(x)

            first_response_target = (
                len(prompt_tokens) - 1
            )

            response_logits = logits[
                :,
                first_response_target:,
                :,
            ]

            response_targets = targets[
                :,
                first_response_target:,
            ]

            token_count = int(
                response_targets.numel()
            )

            if token_count < 1:
                raise RuntimeError(
                    "instruction example has no "
                    "response targets"
                )

            loss_sum = nn.functional.cross_entropy(
                response_logits.reshape(
                    -1,
                    response_logits.size(-1),
                ),
                response_targets.reshape(-1),
                reduction="sum",
            )

            total_nll += float(
                loss_sum.item()
            )

            total_response_tokens += (
                token_count
            )

            generation = run_greedy_inference(
                checkpoint_path=checkpoint_path,
                prompt=prompt,
                max_tokens=len(
                    tokenizer.encode(response)
                ),
            )

            generated = generation.generated_text

            if generated == response:
                exact_matches += 1

    if total_response_tokens == 0:
        raise RuntimeError(
            "no response tokens evaluated"
        )

    average_loss = (
        total_nll
        / total_response_tokens
    )

    try:
        perplexity = math.exp(average_loss)
    except OverflowError:
        perplexity = math.inf

    return InstructionEvaluation(
        response_loss=average_loss,
        response_perplexity=perplexity,
        response_tokens_evaluated=(
            total_response_tokens
        ),
        examples_evaluated=len(examples),
        exact_matches=exact_matches,
    )


def evaluate_checkpoint(
    *,
    checkpoint_path: Path,
    lm_path: Path,
    instruction_path: Path,
) -> dict[str, Any]:
    loaded = load_checkpoint(
        checkpoint_path
    )

    model = loaded.model
    tokenizer = loaded.tokenizer

    lm_text = lm_path.read_text(
        encoding="utf-8"
    )

    validate_tokenizer_coverage(
        tokenizer,
        lm_text,
    )

    lm_tokens = tokenizer.encode(
        lm_text
    )

    instructions = load_instruction_examples(
        instruction_path
    )

    lm_result = evaluate_language_model_tokens(
        model=model,
        tokens=lm_tokens,
        context_length=(
            loaded.config.context_length
        ),
    )

    instruction_result = (
        evaluate_instruction_examples(
            checkpoint_path=checkpoint_path,
            model=model,
            tokenizer=tokenizer,
            examples=instructions,
            context_length=(
                loaded.config.context_length
            ),
        )
    )

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    return {
        "checkpoint": str(checkpoint_path),
        "model_name": loaded.checkpoint.get(
            "model_name",
            "denarixx-d0",
        ),
        "post_training_stage": (
            loaded.checkpoint.get(
                "post_training_stage"
            )
        ),
        "model_config": asdict(
            loaded.config
        ),
        "parameter_count": parameter_count,
        "tokenizer": tokenizer.to_dict(),
        "datasets": {
            "language_model": {
                "path": str(lm_path),
                "sha256": sha256_file(
                    lm_path
                ),
            },
            "instruction": {
                "path": str(
                    instruction_path
                ),
                "sha256": sha256_file(
                    instruction_path
                ),
            },
        },
        "language_model": (
            lm_result.to_dict()
        ),
        "instruction": (
            instruction_result.to_dict()
        ),
    }
