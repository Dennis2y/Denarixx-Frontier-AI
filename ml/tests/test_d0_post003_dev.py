"""Tests for POST-003 development evaluator.

These tests MUST NOT load the frozen POST-003
development dataset.
"""

from __future__ import annotations

from pathlib import Path
import sys

import torch

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from evaluation.d0_post003_dev import (
    compare,
    greedy_generate,
    parameter_count,
)
from models.d0 import D0Config, D0Model
from tokenizers.char import CharacterTokenizer


def test_compare_pass() -> None:
    baseline = {
        "responseLoss": 3.0,
        "exactMatches": 1,
    }

    candidate = {
        "responseLoss": 2.5,
        "exactMatches": 1,
    }

    result = compare(
        baseline,
        candidate,
    )

    assert result["responseLossImproved"]
    assert result["exactMatchNotWorse"]
    assert result["developmentPass"]


def test_compare_rejects_equal_loss() -> None:
    baseline = {
        "responseLoss": 2.5,
        "exactMatches": 1,
    }

    candidate = {
        "responseLoss": 2.5,
        "exactMatches": 2,
    }

    result = compare(
        baseline,
        candidate,
    )

    assert not result["responseLossImproved"]
    assert not result["developmentPass"]


def test_compare_rejects_worse_exact_match() -> None:
    baseline = {
        "responseLoss": 3.0,
        "exactMatches": 2,
    }

    candidate = {
        "responseLoss": 2.0,
        "exactMatches": 1,
    }

    result = compare(
        baseline,
        candidate,
    )

    assert result["responseLossImproved"]
    assert not result["exactMatchNotWorse"]
    assert not result["developmentPass"]


def test_parameter_count_matches_d0() -> None:
    config = D0Config(
        vocab_size=42,
        context_length=32,
        hidden_size=64,
        layers=2,
        attention_heads=4,
        dropout=0.0,
        normalization="layernorm",
        position_encoding="rope",
    )

    model = D0Model(config)

    assert parameter_count(model) == 102784


def test_greedy_generation_is_deterministic() -> None:
    alphabet = [
        "\n", " ", ",", "-", ".", "0",
        "A", "B", "C", "D", "E", "I",
        "R", "S", "T", "W",
        "a", "b", "c", "d", "e", "f",
        "g", "h", "i", "j", "k", "l",
        "m", "n", "o", "p", "q", "r",
        "s", "t", "u", "v", "w", "x",
        "y", "z",
    ]

    tokenizer = CharacterTokenizer(
        alphabet=alphabet
    )

    config = D0Config(
        vocab_size=42,
        context_length=32,
        hidden_size=64,
        layers=2,
        attention_heads=4,
        dropout=0.0,
        normalization="layernorm",
        position_encoding="rope",
    )

    torch.manual_seed(123)
    model = D0Model(config)
    model.eval()

    class Example:
        instruction = "say ai"
        response = "ai"

    first = greedy_generate(
        model,
        tokenizer,
        Example(),
    )

    second = greedy_generate(
        model,
        tokenizer,
        Example(),
    )

    assert first == second


def test_tests_do_not_reference_frozen_dev() -> None:
    source = Path(__file__).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "d0_" + "post003_" + "dev.jsonl"
    )

    assert forbidden not in source


def main() -> None:
    tests = [
        test_compare_pass,
        test_compare_rejects_equal_loss,
        test_compare_rejects_worse_exact_match,
        test_parameter_count_matches_d0,
        test_greedy_generation_is_deterministic,
        test_tests_do_not_reference_frozen_dev,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All POST-003 development evaluator "
        "tests passed."
    )


if __name__ == "__main__":
    main()
