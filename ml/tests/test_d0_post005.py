"""Static safety tests for D0-POST-005 controller."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path
import sys
import tempfile


ML_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ML_ROOT.parent

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

import run_post005


BASE = (
    PROJECT_ROOT
    / "local-checkpoints"
    / "d0-post003-capability-seed42.pt"
)

TRAIN = ML_ROOT / "data" / "d0_post004_train.jsonl"
DEV = ML_ROOT / "data" / "d0_post004_dev.jsonl"
LM = ML_ROOT / "data" / "d0_research_corpus.txt"

PLAN = (
    PROJECT_ROOT
    / "local-evidence"
    / "d0-post005-training-plan"
    / "FROZEN_TRAINING_PLAN.md"
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


def controller_source() -> str:
    return (
        ML_ROOT / "run_post005.py"
    ).read_text(encoding="utf-8")


def test_frozen_constants() -> None:
    assert run_post005.MAX_STEPS == 120
    assert run_post005.CANDIDATE_STEPS == (40, 80, 120)
    assert run_post005.SFT_BATCH_SIZE == 4
    assert run_post005.LM_BATCH_SIZE == 4
    assert run_post005.LEARNING_RATE == 1e-4
    assert run_post005.WEIGHT_DECAY == 0.01
    assert run_post005.GRADIENT_CLIP_NORM == 1.0
    assert run_post005.RETENTION_WEIGHT == 0.25
    assert run_post005.SEED == 42
    assert run_post005.SFT_GENERATOR_SEED == 42
    assert run_post005.LM_GENERATOR_SEED == 43


def test_frozen_identities() -> None:
    assert sha256_file(BASE) == (
        run_post005.EXPECTED_BASE_SHA256
    )

    assert sha256_file(TRAIN) == (
        run_post005.EXPECTED_TRAIN_SHA256
    )

    assert sha256_file(DEV) == (
        run_post005.EXPECTED_DEV_SHA256
    )

    assert sha256_file(LM) == (
        run_post005.EXPECTED_LM_SHA256
    )

    assert sha256_file(PLAN) == (
        run_post005.FROZEN_PLAN_SHA256
    )


def test_parent_is_post003() -> None:
    assert run_post005.EXPECTED_BASE_SHA256 == (
        "3b409092c120242fe4ed75113758390dee3e8e627"
        "507afdf7bcbc1bb5b3ccc06"
    )


def test_no_post004_reference_checkpoint() -> None:
    source = controller_source()

    assert (
        "d0-post004-capability-seed42-step120.pt"
        not in source
    )

    assert (
        "ae927ca3e779a0eda7c8fff025fc7cfd3a41568cb"
        "236148f444c75507ef35441"
        not in source
    )


def test_no_protected_formal_reference() -> None:
    source = controller_source()

    assert "d0_post003_formal.jsonl" not in source


def test_run_signature_is_frozen() -> None:
    tree = ast.parse(controller_source())

    run_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "run"
    )

    names = [
        argument.arg
        for argument in run_node.args.args
    ]

    assert names == [
        "checkpoint_path",
        "train_dataset_path",
        "lm_dataset_path",
        "output_path",
        "run_id",
    ]


def test_no_dataset_resplit() -> None:
    assert (
        "split_instruction_dataset"
        not in controller_source()
    )


def test_fresh_optimizer() -> None:
    source = controller_source()

    assert "torch.optim.AdamW" in source
    assert "optimizer.load_state_dict" not in source

    assert (
        'checkpoint["optimizer_state_dict"]'
        not in source
    )


def test_modified_train_is_rejected() -> None:
    original = TRAIN.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp) / "train.jsonl"

        fake.write_text(
            original + "\n",
            encoding="utf-8",
        )

        try:
            run_post005.verify_frozen_inputs(
                checkpoint_path=BASE,
                train_dataset_path=fake,
                lm_dataset_path=LM,
            )
        except ValueError:
            return

    raise AssertionError(
        "modified training dataset was accepted"
    )


def test_no_top_level_run_call() -> None:
    tree = ast.parse(controller_source())

    for node in tree.body:
        if not isinstance(node, ast.Expr):
            continue

        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "run"
        ):
            raise AssertionError(
                "run() called at module top level"
            )


def main() -> None:
    tests = [
        test_frozen_constants,
        test_frozen_identities,
        test_parent_is_post003,
        test_no_post004_reference_checkpoint,
        test_no_protected_formal_reference,
        test_run_signature_is_frozen,
        test_no_dataset_resplit,
        test_fresh_optimizer,
        test_modified_train_is_rejected,
        test_no_top_level_run_call,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print("All D0-POST-005 controller tests passed.")


if __name__ == "__main__":
    main()
