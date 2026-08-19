from __future__ import annotations

import ast
import sys
from pathlib import Path

import torch

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from evaluation.d04_final_evaluator import (
    EXPECTED_FAMILIES,
    evaluate_rows,
    validate_rows,
)
from models.d0 import D0Config, D0Model
from tokenizers.char import CharacterTokenizer


EVALUATOR = (
    ML_ROOT
    / "evaluation"
    / "d04_final_evaluator.py"
)

CONTROLLER = (
    ML_ROOT
    / "evaluation"
    / "d04_execution_controller.py"
)


def synthetic_rows():
    return [
        {
            "family": family,
            "instruction": "a",
            "response": "b",
        }
        for family in sorted(EXPECTED_FAMILIES)
    ]


def synthetic_model():
    tokenizer = CharacterTokenizer.train(
        "Instruction: a\nResponse: b\n"
    )

    config = D0Config(
        vocab_size=tokenizer.vocab_size,
        context_length=32,
        hidden_size=16,
        layers=1,
        attention_heads=4,
        dropout=0.0,
    )

    torch.manual_seed(1234)

    model = D0Model(config)
    model.eval()

    return model, tokenizer


def test_validate_rows_accepts_all_families():
    validate_rows(synthetic_rows())


def test_missing_family_rejected():
    rows = synthetic_rows()[:-1]

    try:
        validate_rows(rows)
    except ValueError:
        return

    raise AssertionError(
        "missing family was accepted"
    )


def test_unknown_family_rejected():
    rows = synthetic_rows()

    rows[0] = {
        **rows[0],
        "family": "unknown",
    }

    try:
        validate_rows(rows)
    except ValueError:
        return

    raise AssertionError(
        "unknown family was accepted"
    )


def test_synthetic_evaluation_is_deterministic():
    model, tokenizer = synthetic_model()
    rows = synthetic_rows()

    first = evaluate_rows(
        model=model,
        tokenizer=tokenizer,
        rows=rows,
    ).to_dict()

    second = evaluate_rows(
        model=model,
        tokenizer=tokenizer,
        rows=rows,
    ).to_dict()

    assert first == second


def test_token_weighted_result_is_valid():
    model, tokenizer = synthetic_model()

    result = evaluate_rows(
        model=model,
        tokenizer=tokenizer,
        rows=synthetic_rows(),
    )

    assert result.examples_evaluated == 5
    assert result.response_tokens_evaluated > 0
    assert result.response_loss >= 0.0
    assert set(result.per_family) == (
        EXPECTED_FAMILIES
    )


def test_evaluator_does_not_load_checkpoint():
    source = EVALUATOR.read_text(
        encoding="utf-8"
    )

    assert "torch.load(" not in source
    assert "load_checkpoint(" not in source
    assert "d0-post002-accepted.pt" not in source


def test_controller_requires_authorization():
    source = CONTROLLER.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(source)

    assert "AUTHORIZE_D04_CANONICAL_EVALUATION" in source
    assert "DENARIXX_D04_AUTHORIZATION" in source

    functions = {
        node.name
        for node in tree.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        )
    }

    assert "require_authorization" in functions
    assert "execute" in functions


def test_no_training_operations_in_evaluator():
    source = EVALUATOR.read_text(
        encoding="utf-8"
    )

    forbidden = (
        ".backward(",
        "optimizer.step(",
        ".zero_grad(",
        "torch.optim.",
    )

    for token in forbidden:
        assert token not in source


def main():
    tests = [
        test_validate_rows_accepts_all_families,
        test_missing_family_rejected,
        test_unknown_family_rejected,
        test_synthetic_evaluation_is_deterministic,
        test_token_weighted_result_is_valid,
        test_evaluator_does_not_load_checkpoint,
        test_controller_requires_authorization,
        test_no_training_operations_in_evaluator,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All D0.4 final evaluator synthetic tests passed."
    )


if __name__ == "__main__":
    main()
