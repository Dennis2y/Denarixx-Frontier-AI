"""Tiny local dataset loader for CPU smoke experiments."""

from pathlib import Path

import torch


def load_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if len(text) < 128:
        raise ValueError("development corpus is too small")
    return text


def split_tokens(tokens: list[int], validation_fraction: float = 0.15) -> tuple[torch.Tensor, torch.Tensor]:
    values = torch.tensor(tokens, dtype=torch.long)
    split_at = max(2, int(len(values) * (1 - validation_fraction)))
    return values[:split_at], values[split_at:]


def batch(data: torch.Tensor, context_length: int, batch_size: int, generator: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    if len(data) <= context_length + 1:
        raise ValueError("dataset must contain more tokens than the context length")
    starts = torch.randint(0, len(data) - context_length - 1, (batch_size,), generator=generator)
    inputs = torch.stack([data[start : start + context_length] for start in starts])
    targets = torch.stack([data[start + 1 : start + context_length + 1] for start in starts])
    return inputs, targets