"""Focused tests for D0-POST-002 mixed objective."""

from __future__ import annotations

from pathlib import Path
import sys

import torch

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from post_training.mixed_objective import (
    language_model_loss,
    mixed_loss,
    response_loss,
)
from post_training.sft_data import (
    IGNORE_INDEX,
)


def test_response_loss_masks_prompt() -> None:
    logits = torch.randn(
        1,
        3,
        5,
    )

    targets = torch.tensor(
        [[IGNORE_INDEX, 2, 3]]
    )

    loss = response_loss(
        logits,
        targets,
    )

    assert torch.isfinite(loss)


def test_response_loss_rejects_empty_supervision() -> None:
    logits = torch.randn(
        1,
        2,
        5,
    )

    targets = torch.tensor(
        [[IGNORE_INDEX, IGNORE_INDEX]]
    )

    try:
        response_loss(
            logits,
            targets,
        )
    except ValueError:
        return

    raise AssertionError(
        "empty SFT supervision was accepted"
    )


def test_lm_loss_is_finite() -> None:
    logits = torch.randn(
        2,
        4,
        7,
    )

    targets = torch.randint(
        0,
        7,
        (2, 4),
    )

    loss = language_model_loss(
        logits,
        targets,
    )

    assert torch.isfinite(loss)


def test_mixed_loss_formula() -> None:
    sft = torch.tensor(2.0)
    lm = torch.tensor(4.0)

    result = mixed_loss(
        sft,
        lm,
        0.25,
    )

    assert abs(
        float(result.item()) - 3.0
    ) < 1e-6


def test_zero_retention_matches_sft() -> None:
    sft = torch.tensor(2.5)
    lm = torch.tensor(8.0)

    result = mixed_loss(
        sft,
        lm,
        0.0,
    )

    assert float(result.item()) == 2.5


def test_negative_weight_rejected() -> None:
    try:
        mixed_loss(
            torch.tensor(1.0),
            torch.tensor(1.0),
            -0.1,
        )
    except ValueError:
        return

    raise AssertionError(
        "negative retention weight accepted"
    )


def main() -> None:
    tests = [
        test_response_loss_masks_prompt,
        test_response_loss_rejects_empty_supervision,
        test_lm_loss_is_finite,
        test_mixed_loss_formula,
        test_zero_retention_matches_sft,
        test_negative_weight_rejected,
    ]

    for test in tests:
        test()
        print(
            f"✓ {test.__name__}"
        )

    print()
    print(
        "All D0-POST-002 focused tests passed."
    )


if __name__ == "__main__":
    main()
