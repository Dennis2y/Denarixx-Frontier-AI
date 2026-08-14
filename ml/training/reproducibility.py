"""Reproducibility helpers for Denarixx experiments."""

from __future__ import annotations

import platform
import random
import sys

import torch


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def environment_metadata() -> dict:
    return {
        "pythonVersion": sys.version.split()[0],
        "pythonImplementation": platform.python_implementation(),
        "platform": platform.platform(),
        "torchVersion": torch.__version__,
        "cudaAvailable": torch.cuda.is_available(),
        "cudaVersion": torch.version.cuda,
        "mpsAvailable": bool(
            hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ),
    }


def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")
