"""Mixed-objective utilities for D0-POST-002."""

from __future__ import annotations

import torch
from torch import nn

from post_training.sft_data import IGNORE_INDEX


def response_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
) -> torch.Tensor:
    if not bool(
        targets.ne(IGNORE_INDEX).any()
    ):
        raise ValueError(
            "SFT batch contains no supervised tokens"
        )

    return nn.functional.cross_entropy(
        logits.reshape(-1, logits.size(-1)),
        targets.reshape(-1),
        ignore_index=IGNORE_INDEX,
    )


def language_model_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
) -> torch.Tensor:
    if logits.ndim != 3:
        raise ValueError(
            "LM logits must have shape "
            "[batch, sequence, vocabulary]"
        )

    if targets.ndim != 2:
        raise ValueError(
            "LM targets must have shape "
            "[batch, sequence]"
        )

    if logits.shape[:2] != targets.shape:
        raise ValueError(
            "LM logits and targets have incompatible shapes"
        )

    return nn.functional.cross_entropy(
        logits.reshape(-1, logits.size(-1)),
        targets.reshape(-1),
    )


def mixed_loss(
    sft_loss: torch.Tensor,
    lm_loss: torch.Tensor,
    retention_weight: float,
) -> torch.Tensor:
    if retention_weight < 0:
        raise ValueError(
            "retention_weight must be >= 0"
        )

    return (
        sft_loss
        + retention_weight * lm_loss
    )
