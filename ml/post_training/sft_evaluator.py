"""Response-masked evaluation for Denarixx D0 SFT."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import torch
from torch import nn

from models.d0 import D0Model
from post_training.sft_data import (
    EncodedInstruction,
    IGNORE_INDEX,
    collate_examples,
)


@dataclass(frozen=True)
class SFTEvaluationResult:
    response_loss: float
    response_perplexity: float
    examples_evaluated: int
    response_tokens_evaluated: int

    def to_dict(self) -> dict:
        return asdict(self)


def masked_response_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
) -> torch.Tensor:
    return nn.functional.cross_entropy(
        logits.reshape(-1, logits.size(-1)),
        targets.reshape(-1),
        ignore_index=IGNORE_INDEX,
    )


def evaluate_sft(
    model: D0Model,
    examples: list[EncodedInstruction],
    pad_token_id: int,
    batch_size: int = 4,
) -> SFTEvaluationResult:
    if not examples:
        raise ValueError(
            "SFT evaluation requires examples"
        )

    if batch_size < 1:
        raise ValueError(
            "batch_size must be >= 1"
        )

    device = next(model.parameters()).device
    was_training = model.training
    model.eval()

    total_loss = 0.0
    total_tokens = 0

    with torch.no_grad():
        for start in range(
            0,
            len(examples),
            batch_size,
        ):
            chunk = examples[
                start : start + batch_size
            ]

            inputs, targets, _ = collate_examples(
                chunk,
                pad_token_id=pad_token_id,
            )

            inputs = inputs.to(device)
            targets = targets.to(device)

            logits, _ = model(inputs)

            loss = masked_response_loss(
                logits,
                targets,
            )

            supervised = int(
                (targets != IGNORE_INDEX)
                .sum()
                .item()
            )

            total_loss += (
                float(loss.item())
                * supervised
            )

            total_tokens += supervised

    if was_training:
        model.train()

    if total_tokens < 1:
        raise RuntimeError(
            "SFT evaluation found no response tokens"
        )

    average_loss = total_loss / total_tokens

    try:
        perplexity = math.exp(average_loss)
    except OverflowError:
        perplexity = math.inf

    return SFTEvaluationResult(
        response_loss=average_loss,
        response_perplexity=perplexity,
        examples_evaluated=len(examples),
        response_tokens_evaluated=total_tokens,
    )
