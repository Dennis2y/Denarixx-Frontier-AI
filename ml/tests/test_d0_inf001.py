"""Focused tests for D0-INF-001 inference validation."""

from __future__ import annotations

from pathlib import Path

import torch

from inference.d0_inference import (
    load_checkpoint,
    run_greedy_inference,
    validate_prompt_coverage,
)


ROOT = Path(__file__).resolve().parents[2]

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


def test_pretrained_checkpoint_loads() -> None:
    loaded = load_checkpoint(
        PRETRAINED
    )

    assert (
        loaded.config.normalization
        == "layernorm"
    )

    assert (
        loaded.config.position_encoding
        == "rope"
    )

    assert (
        loaded.config.context_length
        == 32
    )


def test_sft_checkpoint_loads() -> None:
    loaded = load_checkpoint(
        SFT
    )

    assert (
        loaded.checkpoint[
            "post_training_stage"
        ]
        == "sft"
    )

    assert (
        loaded.config.context_length
        == 32
    )


def test_sft_invariants_match_pretrained() -> None:
    base = load_checkpoint(
        PRETRAINED
    )

    sft = load_checkpoint(
        SFT
    )

    assert (
        base.config
        == sft.config
    )

    assert (
        base.tokenizer.to_dict()
        == sft.tokenizer.to_dict()
    )

    assert (
        sum(
            parameter.numel()
            for parameter
            in sft.model.parameters()
        )
        == 102784
    )


def test_greedy_is_deterministic() -> None:
    first = run_greedy_inference(
        checkpoint_path=SFT,
        prompt="say true\n",
        max_tokens=8,
    )

    second = run_greedy_inference(
        checkpoint_path=SFT,
        prompt="say true\n",
        max_tokens=8,
    )

    assert (
        first.generated_token_ids
        == second.generated_token_ids
    )

    assert (
        first.generated_text
        == second.generated_text
    )


def test_output_preserves_full_prompt() -> None:
    prompt = (
        "say true\n"
        "say false\n"
        "say token\n"
        "say yes\n"
    )

    result = run_greedy_inference(
        checkpoint_path=SFT,
        prompt=prompt,
        max_tokens=4,
    )

    assert (
        result.output.startswith(
            prompt
        )
    )


def test_long_prompt_uses_context_window() -> None:
    loaded = load_checkpoint(
        SFT
    )

    prompt = "a" * 40

    result = run_greedy_inference(
        checkpoint_path=SFT,
        prompt=prompt,
        max_tokens=2,
    )

    assert result.prompt_tokens == 40

    assert (
        result.prompt_tokens_used
        == loaded.config.context_length
    )

    assert result.prompt_truncated


def test_short_prompt_not_truncated() -> None:
    result = run_greedy_inference(
        checkpoint_path=SFT,
        prompt="say true\n",
        max_tokens=2,
    )

    assert not result.prompt_truncated

    assert (
        result.prompt_tokens
        == result.prompt_tokens_used
    )


def test_unknown_character_rejected() -> None:
    loaded = load_checkpoint(
        SFT
    )

    try:
        validate_prompt_coverage(
            loaded.tokenizer,
            "Q",
        )
    except ValueError as error:
        assert (
            "absent from checkpoint tokenizer"
            in str(error)
        )
    else:
        raise AssertionError(
            "unknown prompt character was not rejected"
        )


def test_empty_prompt_rejected() -> None:
    loaded = load_checkpoint(
        SFT
    )

    try:
        validate_prompt_coverage(
            loaded.tokenizer,
            "",
        )
    except ValueError as error:
        assert (
            "must not be empty"
            in str(error)
        )
    else:
        raise AssertionError(
            "empty prompt was not rejected"
        )


def test_invalid_max_tokens_rejected() -> None:
    try:
        run_greedy_inference(
            checkpoint_path=SFT,
            prompt="say true\n",
            max_tokens=0,
        )
    except ValueError as error:
        assert (
            "max_tokens must be >= 1"
            in str(error)
        )
    else:
        raise AssertionError(
            "invalid max_tokens was not rejected"
        )


def test_generation_metadata() -> None:
    result = run_greedy_inference(
        checkpoint_path=SFT,
        prompt="say token\n",
        max_tokens=4,
    )

    assert (
        result.tokens_generated
        == 4
    )

    assert (
        len(
            result.generated_token_ids
        )
        == 4
    )

    assert (
        result.decoding
        == "greedy"
    )

    assert (
        result.parameter_count
        == 102784
    )

    assert (
        result.context_length
        == 32
    )

    assert (
        result.latency_ms
        > 0
    )

    assert (
        result.generation_latency_ms
        > 0
    )

    assert (
        result.tokens_per_second
        > 0
    )


def test_model_is_eval_mode() -> None:
    loaded = load_checkpoint(
        SFT
    )

    assert not loaded.model.training


def test_checkpoint_weights_differ() -> None:
    base = torch.load(
        PRETRAINED,
        map_location="cpu",
        weights_only=False,
    )

    sft = torch.load(
        SFT,
        map_location="cpu",
        weights_only=False,
    )

    changed = 0

    for name, tensor in (
        base["model_state_dict"].items()
    ):
        if not torch.equal(
            tensor,
            sft[
                "model_state_dict"
            ][name],
        ):
            changed += 1

    assert changed > 0


def main() -> None:
    tests = [
        test_pretrained_checkpoint_loads,
        test_sft_checkpoint_loads,
        test_sft_invariants_match_pretrained,
        test_greedy_is_deterministic,
        test_output_preserves_full_prompt,
        test_long_prompt_uses_context_window,
        test_short_prompt_not_truncated,
        test_unknown_character_rejected,
        test_empty_prompt_rejected,
        test_invalid_max_tokens_rejected,
        test_generation_metadata,
        test_model_is_eval_mode,
        test_checkpoint_weights_differ,
    ]

    for test in tests:
        test()
        print(
            f"✓ {test.__name__}"
        )

    print()
    print(
        "All D0-INF-001 focused tests passed."
    )


if __name__ == "__main__":
    main()
