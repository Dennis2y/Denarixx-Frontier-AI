"""Focused regression tests for D0-EVAL-001."""

from __future__ import annotations

import math
from pathlib import Path
import sys

import torch
from torch import nn

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from evaluation.d0_eval001 import (
    evaluate_checkpoint,
    evaluate_instruction_examples,
    evaluate_language_model_tokens,
    load_instruction_examples,
    sha256_file,
    validate_tokenizer_coverage,
)
from inference.d0_inference import (
    load_checkpoint,
)


ROOT = ML_ROOT.parent

PRETRAINED = (
    ROOT
    / "local-checkpoints"
    / "d0-arch002-rope-seed42.pt"
)

SFT = (
    ROOT
    / "local-checkpoints"
    / "d0-post001-sft-seed42.pt"
)

LM_DATA = (
    ML_ROOT
    / "data"
    / "d0_eval001_lm.txt"
)

INSTRUCTION_DATA = (
    ML_ROOT
    / "data"
    / "d0_eval001_instructions.jsonl"
)

PRETRAIN_DATA = (
    ML_ROOT
    / "data"
    / "d0_research_corpus.txt"
)

SFT_DATA = (
    ML_ROOT
    / "data"
    / "d0_sft_tiny.jsonl"
)


class FixedModel(nn.Module):
    def __init__(
        self,
        vocab_size: int,
    ) -> None:
        super().__init__()

        self.vocab_size = vocab_size

    def forward(
        self,
        tokens: torch.Tensor,
        targets: torch.Tensor | None = None,
    ):
        batch, sequence = tokens.shape

        logits = torch.zeros(
            batch,
            sequence,
            self.vocab_size,
        )

        return logits, None


def test_eval_files_exist() -> None:
    assert LM_DATA.is_file()
    assert INSTRUCTION_DATA.is_file()


def test_eval_hashes_are_stable_shape() -> None:
    for path in [
        LM_DATA,
        INSTRUCTION_DATA,
    ]:
        digest = sha256_file(path)

        assert len(digest) == 64

        int(digest, 16)


def test_instruction_dataset_loads() -> None:
    examples = load_instruction_examples(
        INSTRUCTION_DATA
    )

    assert len(examples) == 6

    assert examples[0] == {
        "instruction": "say research",
        "response": "research",
    }


def test_eval_instruction_strings_not_in_sft_data() -> None:
    source = SFT_DATA.read_text(
        encoding="utf-8"
    )

    examples = load_instruction_examples(
        INSTRUCTION_DATA
    )

    for example in examples:
        assert (
            example["instruction"]
            not in source
        )


def test_eval_lm_lines_not_in_pretraining_data() -> None:
    training = PRETRAIN_DATA.read_text(
        encoding="utf-8"
    )

    evaluation = LM_DATA.read_text(
        encoding="utf-8"
    )

    for line in evaluation.splitlines():
        line = line.strip()

        if line:
            assert line not in training


def test_tokenizer_coverage_accepts_eval_data() -> None:
    loaded = load_checkpoint(
        PRETRAINED
    )

    validate_tokenizer_coverage(
        loaded.tokenizer,
        LM_DATA.read_text(
            encoding="utf-8"
        ),
    )

    for example in load_instruction_examples(
        INSTRUCTION_DATA
    ):
        validate_tokenizer_coverage(
            loaded.tokenizer,
            (
                example["instruction"]
                + "\n"
                + example["response"]
                + "\n"
            ),
        )


def test_tokenizer_coverage_rejects_unknown() -> None:
    loaded = load_checkpoint(
        PRETRAINED
    )

    try:
        validate_tokenizer_coverage(
            loaded.tokenizer,
            "snowman \u2603",
        )
    except ValueError:
        return

    raise AssertionError(
        "unknown evaluation character was accepted"
    )


def test_lm_loss_is_token_weighted() -> None:
    model = FixedModel(
        vocab_size=4
    )

    result = evaluate_language_model_tokens(
        model=model,
        tokens=[0, 1, 2, 3, 0, 1],
        context_length=4,
    )

    expected = math.log(4.0)

    assert abs(
        result.average_loss - expected
    ) < 1e-6

    assert result.tokens_evaluated == 5

    assert result.windows_evaluated == 2


def test_lm_metrics_are_finite() -> None:
    loaded = load_checkpoint(
        PRETRAINED
    )

    text = LM_DATA.read_text(
        encoding="utf-8"
    )

    tokens = loaded.tokenizer.encode(
        text
    )

    result = evaluate_language_model_tokens(
        model=loaded.model,
        tokens=tokens,
        context_length=(
            loaded.model.config.context_length
        ),
    )

    assert math.isfinite(
        result.average_loss
    )

    assert math.isfinite(
        result.perplexity
    )

    assert result.tokens_evaluated > 0


def test_instruction_metrics_are_finite() -> None:
    loaded = load_checkpoint(
        SFT
    )

    result = evaluate_instruction_examples(
        checkpoint_path=SFT,
        model=loaded.model,
        tokenizer=loaded.tokenizer,
        examples=load_instruction_examples(
            INSTRUCTION_DATA
        ),
        context_length=(
            loaded.config.context_length
        ),
    )

    assert math.isfinite(
        result.response_loss
    )

    assert math.isfinite(
        result.response_perplexity
    )

    assert (
        result.response_tokens_evaluated
        > 0
    )

    assert result.examples_evaluated == 6


def test_checkpoint_evaluation_is_deterministic() -> None:
    first = evaluate_checkpoint(
        checkpoint_path=SFT,
        lm_path=LM_DATA,
        instruction_path=INSTRUCTION_DATA,
    )

    second = evaluate_checkpoint(
        checkpoint_path=SFT,
        lm_path=LM_DATA,
        instruction_path=INSTRUCTION_DATA,
    )

    assert (
        first["language_model"]
        == second["language_model"]
    )

    assert (
        first["instruction"]
        == second["instruction"]
    )


def test_pretrained_sft_invariants_match() -> None:
    pretrained = evaluate_checkpoint(
        checkpoint_path=PRETRAINED,
        lm_path=LM_DATA,
        instruction_path=INSTRUCTION_DATA,
    )

    sft = evaluate_checkpoint(
        checkpoint_path=SFT,
        lm_path=LM_DATA,
        instruction_path=INSTRUCTION_DATA,
    )

    assert (
        pretrained["model_config"]
        == sft["model_config"]
    )

    assert (
        pretrained["tokenizer"]
        == sft["tokenizer"]
    )

    assert (
        pretrained["parameter_count"]
        == 102784
    )

    assert (
        sft["parameter_count"]
        == 102784
    )


def test_eval_datasets_are_distinct_from_training() -> None:
    assert (
        sha256_file(LM_DATA)
        != sha256_file(PRETRAIN_DATA)
    )

    assert (
        sha256_file(INSTRUCTION_DATA)
        != sha256_file(SFT_DATA)
    )


def main() -> None:
    tests = [
        test_eval_files_exist,
        test_eval_hashes_are_stable_shape,
        test_instruction_dataset_loads,
        test_eval_instruction_strings_not_in_sft_data,
        test_eval_lm_lines_not_in_pretraining_data,
        test_tokenizer_coverage_accepts_eval_data,
        test_tokenizer_coverage_rejects_unknown,
        test_lm_loss_is_token_weighted,
        test_lm_metrics_are_finite,
        test_instruction_metrics_are_finite,
        test_checkpoint_evaluation_is_deterministic,
        test_pretrained_sft_invariants_match,
        test_eval_datasets_are_distinct_from_training,
    ]

    for test in tests:
        test()
        print(
            f"✓ {test.__name__}"
        )

    print()
    print(
        "All D0-EVAL-001 focused tests passed."
    )


if __name__ == "__main__":
    main()
