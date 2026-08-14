"""Independent evaluation utilities for Denarixx D0."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import torch

from models.d0 import D0Model


@dataclass(frozen=True)
class EvaluationResult:
    average_loss: float
    perplexity: float
    batches_evaluated: int
    tokens_evaluated: int

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_language_model(
    model: D0Model,
    data: torch.Tensor,
    context_length: int,
    batch_size: int = 4,
    max_batches: int = 16,
) -> EvaluationResult:
    """Evaluate D0 deterministically over sequential held-out windows."""

    if len(data) <= context_length + 1:
        raise ValueError("evaluation data is too small for configured context")

    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    if max_batches < 1:
        raise ValueError("max_batches must be >= 1")

    device = next(model.parameters()).device
    was_training = model.training
    model.eval()

    losses: list[float] = []
    tokens_evaluated = 0

    windows: list[tuple[torch.Tensor, torch.Tensor]] = []

    with torch.no_grad():
        last_start = len(data) - context_length - 1

        for start in range(0, last_start + 1, context_length):
            inputs = data[start : start + context_length]
            targets = data[start + 1 : start + context_length + 1]

            if len(inputs) != context_length or len(targets) != context_length:
                continue

            windows.append((inputs, targets))

            if len(windows) == batch_size:
                x = torch.stack([item[0] for item in windows]).to(device)
                y = torch.stack([item[1] for item in windows]).to(device)

                _, loss = model(x, y)

                if loss is None:
                    raise RuntimeError("evaluation produced no loss")

                losses.append(float(loss.item()))
                tokens_evaluated += int(y.numel())
                windows.clear()

                if len(losses) >= max_batches:
                    break

        if windows and len(losses) < max_batches:
            x = torch.stack([item[0] for item in windows]).to(device)
            y = torch.stack([item[1] for item in windows]).to(device)

            _, loss = model(x, y)

            if loss is None:
                raise RuntimeError("evaluation produced no loss")

            losses.append(float(loss.item()))
            tokens_evaluated += int(y.numel())

    if was_training:
        model.train()

    if not losses:
        raise RuntimeError("no evaluation batches could be constructed")

    average_loss = sum(losses) / len(losses)

    try:
        perplexity = math.exp(average_loss)
    except OverflowError:
        perplexity = math.inf

    return EvaluationResult(
        average_loss=average_loss,
        perplexity=perplexity,
        batches_evaluated=len(losses),
        tokens_evaluated=tokens_evaluated,
    )
