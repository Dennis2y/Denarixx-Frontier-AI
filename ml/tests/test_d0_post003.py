"""Focused regression tests for D0-POST-003.

These tests validate the frozen training implementation
without executing the POST-003 optimization run.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import tempfile

import torch


ML_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ML_ROOT.parent

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


import run_post003
from post_training.mixed_objective import mixed_loss


BASE = (
    PROJECT_ROOT
    / "local-checkpoints"
    / "d0-post002-accepted.pt"
)

TRAIN = (
    ML_ROOT
    / "data"
    / "d0_post003_train.jsonl"
)

DEV = (
    ML_ROOT
    / "data"
    / "d0_post003_dev.jsonl"
)

LM = (
    ML_ROOT
    / "data"
    / "d0_research_corpus.txt"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def test_frozen_constants() -> None:
    assert run_post003.MAX_STEPS == 20
    assert run_post003.SFT_BATCH_SIZE == 4
    assert run_post003.LM_BATCH_SIZE == 4
    assert run_post003.LEARNING_RATE == 1e-4
    assert run_post003.WEIGHT_DECAY == 0.01
    assert run_post003.GRADIENT_CLIP_NORM == 1.0
    assert run_post003.RETENTION_WEIGHT == 0.25
    assert run_post003.SEED == 42
    assert run_post003.SFT_GENERATOR_SEED == 42
    assert run_post003.LM_GENERATOR_SEED == 43


def test_frozen_input_hashes() -> None:
    assert sha256_file(BASE) == (
        run_post003.EXPECTED_BASE_SHA256
    )

    assert sha256_file(TRAIN) == (
        run_post003.EXPECTED_TRAIN_SHA256
    )

    assert sha256_file(LM) == (
        run_post003.EXPECTED_LM_SHA256
    )


def test_prepare_uses_exact_training_split() -> None:
    state = run_post003.prepare_training_state(
        checkpoint_path=BASE,
        train_dataset_path=TRAIN,
        lm_dataset_path=LM,
    )

    assert len(state["train_examples"]) == 25


def test_dev_is_not_training_input() -> None:
    train_text = TRAIN.read_text(encoding="utf-8")
    dev_text = DEV.read_text(encoding="utf-8")

    train_lines = {
        line
        for line in train_text.splitlines()
        if line.strip()
    }

    dev_lines = {
        line
        for line in dev_text.splitlines()
        if line.strip()
    }

    assert train_lines.isdisjoint(dev_lines)


def test_runner_does_not_resplit_dataset() -> None:
    source = (
        ML_ROOT / "run_post003.py"
    ).read_text(encoding="utf-8")

    assert "split_instruction_dataset" not in source


def test_frozen_hash_rejects_modified_train() -> None:
    original = TRAIN.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "train.jsonl"

        fake.write_text(
            original + "\n",
            encoding="utf-8",
        )

        try:
            run_post003.verify_frozen_inputs(
                checkpoint_path=BASE,
                train_dataset_path=fake,
                lm_dataset_path=LM,
            )
        except ValueError:
            return

    raise AssertionError(
        "modified POST-003 training data was accepted"
    )


def test_checkpoint_architecture_invariants() -> None:
    checkpoint = torch.load(
        BASE,
        map_location="cpu",
        weights_only=False,
    )

    config, tokenizer = (
        run_post003.verify_checkpoint(
            checkpoint
        )
    )

    assert config.vocab_size == 42
    assert config.context_length == 32
    assert config.hidden_size == 64
    assert config.layers == 2
    assert config.attention_heads == 4
    assert config.dropout == 0.0
    assert config.normalization == "layernorm"
    assert config.position_encoding == "rope"
    assert len(tokenizer.alphabet) == 42


def test_fresh_optimizer_policy() -> None:
    source = (
        ML_ROOT / "run_post003.py"
    ).read_text(encoding="utf-8")

    assert "torch.optim.AdamW" in source

    assert (
        'checkpoint["optimizer_state_dict"]'
        not in source
    )

    assert "optimizer.load_state_dict" not in source


def test_mixed_objective_frozen_lambda() -> None:
    sft = torch.tensor(2.0)
    lm = torch.tensor(4.0)

    result = mixed_loss(
        sft,
        lm,
        run_post003.RETENTION_WEIGHT,
    )

    assert abs(
        float(result.item()) - 3.0
    ) < 1e-6


def test_generators_are_deterministic() -> None:
    first = torch.Generator().manual_seed(
        run_post003.SFT_GENERATOR_SEED
    )

    second = torch.Generator().manual_seed(
        run_post003.SFT_GENERATOR_SEED
    )

    a = torch.randint(
        0,
        25,
        (20, 4),
        generator=first,
    )

    b = torch.randint(
        0,
        25,
        (20, 4),
        generator=second,
    )

    assert torch.equal(a, b)


def test_prepare_does_not_create_checkpoint() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        directory = Path(tmp)

        before = list(directory.iterdir())

        run_post003.prepare_training_state(
            checkpoint_path=BASE,
            train_dataset_path=TRAIN,
            lm_dataset_path=LM,
        )

        after = list(directory.iterdir())

        assert before == after


def main() -> None:
    tests = [
        test_frozen_constants,
        test_frozen_input_hashes,
        test_prepare_uses_exact_training_split,
        test_dev_is_not_training_input,
        test_runner_does_not_resplit_dataset,
        test_frozen_hash_rejects_modified_train,
        test_checkpoint_architecture_invariants,
        test_fresh_optimizer_policy,
        test_mixed_objective_frozen_lambda,
        test_generators_are_deterministic,
        test_prepare_does_not_create_checkpoint,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All D0-POST-003 implementation tests passed."
    )


if __name__ == "__main__":
    main()
