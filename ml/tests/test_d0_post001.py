"""Focused tests for D0-POST-001 SFT infrastructure."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import torch

from models.d0 import D0Config, D0Model
from post_training.sft_data import (
    IGNORE_INDEX,
    encode_dataset,
    encode_instruction,
    load_instruction_jsonl,
    split_instruction_dataset,
)
from run_sft import (
    pad_batch,
    response_only_loss,
)
from tokenizers.char import CharacterTokenizer


ROOT = Path(__file__).resolve().parents[2]

BASE_CHECKPOINT = (
    ROOT
    / "local-checkpoints"
    / "d0-arch002-rope-seed42.pt"
)

DATASET = (
    ROOT
    / "ml"
    / "data"
    / "d0_sft_tiny.jsonl"
)


def load_base():
    checkpoint = torch.load(
        BASE_CHECKPOINT,
        map_location="cpu",
        weights_only=False,
    )

    tokenizer = CharacterTokenizer.from_dict(
        checkpoint["tokenizer"]
    )

    config = D0Config(
        **checkpoint["model_config"]
    )

    return checkpoint, tokenizer, config


def test_base_checkpoint_identity() -> None:
    checkpoint, _, config = load_base()

    assert config.normalization == "layernorm"
    assert config.position_encoding == "rope"
    assert config.context_length == 32

    assert (
        checkpoint["dataset"]["sha256"]
        == "936b53855c5fa65cc408fb0b29108966445215a474ccfcce7ae7fe9f41fcc072"
    )


def test_dataset_loads() -> None:
    examples = load_instruction_jsonl(
        DATASET
    )

    assert len(examples) == 12


def test_dataset_uses_existing_tokenizer() -> None:
    _, tokenizer, config = load_base()

    examples = load_instruction_jsonl(
        DATASET
    )

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=examples,
        context_length=config.context_length,
    )

    assert len(encoded) == 12

    assert max(
        len(example.input_ids)
        for example in encoded
    ) <= config.context_length


def test_response_only_masking() -> None:
    _, tokenizer, config = load_base()

    example = load_instruction_jsonl(
        DATASET
    )[0]

    encoded = encode_instruction(
        tokenizer=tokenizer,
        example=example,
        context_length=config.context_length,
    )

    supervised = [
        target
        for target in encoded.target_ids
        if target != IGNORE_INDEX
    ]

    assert len(supervised) == (
        encoded.response_tokens
    )

    assert encoded.response_tokens > 0


def test_padding_masks_targets() -> None:
    _, tokenizer, config = load_base()

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=load_instruction_jsonl(
            DATASET
        )[:2],
        context_length=config.context_length,
    )

    inputs, targets = pad_batch(
        encoded,
        pad_token_id=0,
    )

    assert inputs.shape == targets.shape

    for index, example in enumerate(encoded):
        original_length = len(
            example.input_ids
        )

        if original_length < inputs.size(1):
            assert torch.all(
                targets[
                    index,
                    original_length:
                ]
                == IGNORE_INDEX
            )


def test_response_only_loss_is_finite() -> None:
    checkpoint, tokenizer, config = load_base()

    model = D0Model(config)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=load_instruction_jsonl(
            DATASET
        )[:2],
        context_length=config.context_length,
    )

    inputs, targets = pad_batch(
        encoded,
        pad_token_id=0,
    )

    logits, _ = model(inputs)

    loss = response_only_loss(
        logits,
        targets,
    )

    assert torch.isfinite(loss)
    assert float(loss.item()) > 0


def test_gradient_update_changes_weights() -> None:
    checkpoint, tokenizer, config = load_base()

    model = D0Model(config)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=load_instruction_jsonl(
            DATASET
        )[:2],
        context_length=config.context_length,
    )

    inputs, targets = pad_batch(
        encoded,
        pad_token_id=0,
    )

    before = (
        model.token_embedding.weight
        .detach()
        .clone()
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=1e-4,
    )

    logits, _ = model(inputs)

    loss = response_only_loss(
        logits,
        targets,
    )

    optimizer.zero_grad(
        set_to_none=True
    )

    loss.backward()
    optimizer.step()

    after = (
        model.token_embedding.weight
        .detach()
    )

    assert not torch.equal(
        before,
        after,
    )


def test_tokenizer_round_trip_preserved() -> None:
    checkpoint, tokenizer, _ = load_base()

    payload = tokenizer.to_dict()

    assert payload == checkpoint["tokenizer"]

    reconstructed = (
        CharacterTokenizer.from_dict(
            payload
        )
    )

    assert (
        reconstructed.to_dict()
        == checkpoint["tokenizer"]
    )


def test_unknown_character_rejected() -> None:
    _, tokenizer, config = load_base()

    payload = {
        "instruction": "Q",
        "response": "yes",
    }

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bad.jsonl"

        path.write_text(
            json.dumps(payload) + "\n",
            encoding="utf-8",
        )

        examples = load_instruction_jsonl(
            path
        )

        try:
            encode_dataset(
                tokenizer=tokenizer,
                examples=examples,
                context_length=config.context_length,
            )
        except ValueError as error:
            assert (
                "absent from pretrained tokenizer"
                in str(error)
            )
        else:
            raise AssertionError(
                "unknown character was not rejected"
            )


def test_architecture_parameter_count_preserved() -> None:
    checkpoint, _, config = load_base()

    model = D0Model(config)

    count = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    assert count == 102784

    assert (
        count
        == checkpoint[
            "parameter_counts"
        ]["totalParameters"]
    )



def test_held_out_split_is_75_25() -> None:
    _, tokenizer, config = load_base()

    examples = load_instruction_jsonl(
        DATASET
    )

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=examples,
        context_length=config.context_length,
    )

    train, validation = split_instruction_dataset(
        encoded,
        validation_fraction=0.25,
    )

    assert len(encoded) == 12
    assert len(train) == 9
    assert len(validation) == 3

    assert train == encoded[:9]
    assert validation == encoded[9:]


def test_validation_examples_are_never_training_examples() -> None:
    _, tokenizer, config = load_base()

    examples = load_instruction_jsonl(
        DATASET
    )

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=examples,
        context_length=config.context_length,
    )

    train, validation = split_instruction_dataset(
        encoded,
        validation_fraction=0.25,
    )

    train_ids = {
        tuple(example.input_ids)
        for example in train
    }

    validation_ids = {
        tuple(example.input_ids)
        for example in validation
    }

    assert train_ids.isdisjoint(
        validation_ids
    )


def test_expected_holdout_contents() -> None:
    examples = load_instruction_jsonl(
        DATASET
    )

    assert [
        example.instruction
        for example in examples[:9]
    ] == [
        "say yes",
        "say no",
        "say ai",
        "say data",
        "say safe",
        "say model",
        "say code",
        "say train",
        "say test",
    ]

    assert [
        example.instruction
        for example in examples[9:]
    ] == [
        "say true",
        "say false",
        "say token",
    ]

def main() -> None:
    tests = [
        test_base_checkpoint_identity,
        test_dataset_loads,
        test_dataset_uses_existing_tokenizer,
        test_response_only_masking,
        test_padding_masks_targets,
        test_response_only_loss_is_finite,
        test_gradient_update_changes_weights,
        test_tokenizer_round_trip_preserved,
        test_unknown_character_rejected,
        test_architecture_parameter_count_preserved,
        test_held_out_split_is_75_25,
        test_validation_examples_are_never_training_examples,
        test_expected_holdout_contents,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All D0-POST-001 focused tests passed."
    )


if __name__ == "__main__":
    main()
