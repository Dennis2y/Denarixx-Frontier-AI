"""Canonical configurations for Denarixx D0 research."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TrainingConfig:
    max_steps: int = 100
    batch_size: int = 8
    learning_rate: float = 3e-4
    minimum_learning_rate: float = 3e-5
    weight_decay: float = 0.01
    gradient_clip: float = 1.0
    seed: int = 42

    def to_dict(self) -> dict:
        return asdict(self)


BASELINE_SEEDS = [42, 1337, 2026]


def baseline_training_config(
    seed: int = 42,
    max_steps: int = 100,
) -> TrainingConfig:
    return TrainingConfig(
        max_steps=max_steps,
        seed=seed,
    )
