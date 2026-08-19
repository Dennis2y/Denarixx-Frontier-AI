"""D0-POST-005 frozen development training runner.

This runner implements the frozen POST-005 optimization
policy. It trains one deterministic trajectory and writes
snapshots only at the frozen candidate steps 40, 80, and 120.
It does not evaluate development or formal data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import torch

from data.tiny_dataset import batch as lm_batch
from models.d0 import D0Config, D0Model
from post_training.mixed_objective import (
    language_model_loss,
    mixed_loss,
    response_loss,
)
from post_training.sft_data import (
    IGNORE_INDEX,
    encode_dataset,
    load_instruction_jsonl,
)
from run_sft import pad_batch
from tokenizers.char import CharacterTokenizer


EXPECTED_BASE_SHA256 = (
    "3b409092c120242fe4ed75113758390dee3e8e62750"
    "7afdf7bcbc1bb5b3ccc06"
)

EXPECTED_TRAIN_SHA256 = (
    "93f60bf014810bc5a5592d1ad7f3c5bf7bef80011"
    "dea252ddb0455f006b9963f"
)

EXPECTED_LM_SHA256 = (
    "936b53855c5fa65cc408fb0b29108966445215a474"
    "ccfcce7ae7fe9f41fcc072"
)

EXPECTED_DEV_SHA256 = (
    "d54abaa83a4bbdcca313c557431fa5005e4490b710"
    "3f0f997ccd0c619f5c8a58"
)

FROZEN_PLAN_SHA256 = (
    "1629a882791cd4b12ea5d93322371b23e1c4ce1487"
    "b3589198d76cb969a10a42"
)

EXPECTED_PARAMETER_COUNT = 102784

EXPECTED_CONFIG = {
    "vocab_size": 42,
    "context_length": 32,
    "hidden_size": 64,
    "layers": 2,
    "attention_heads": 4,
    "dropout": 0.0,
    "normalization": "layernorm",
    "position_encoding": "rope",
}

MAX_STEPS = 120
CANDIDATE_STEPS = (40, 80, 120)
SFT_BATCH_SIZE = 4
LM_BATCH_SIZE = 4
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 0.01
GRADIENT_CLIP_NORM = 1.0
RETENTION_WEIGHT = 0.25
SEED = 42
SFT_GENERATOR_SEED = 42
LM_GENERATOR_SEED = 43


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        return torch.device("mps")

    return torch.device("cpu")


def parameter_counts(model: torch.nn.Module) -> dict[str, int]:
    return {
        "totalParameters": sum(
            parameter.numel()
            for parameter in model.parameters()
        ),
        "trainableParameters": sum(
            parameter.numel()
            for parameter in model.parameters()
            if parameter.requires_grad
        ),
    }


def verify_frozen_inputs(
    checkpoint_path: Path,
    train_dataset_path: Path,
    lm_dataset_path: Path,
) -> None:
    expected = {
        checkpoint_path: EXPECTED_BASE_SHA256,
        train_dataset_path: EXPECTED_TRAIN_SHA256,
        lm_dataset_path: EXPECTED_LM_SHA256,
    }

    for path, expected_sha in expected.items():
        if not path.exists():
            raise FileNotFoundError(str(path))

        actual_sha = sha256_file(path)

        if actual_sha != expected_sha:
            raise ValueError(
                "POST-005 frozen input identity mismatch: "
                f"{path}: expected {expected_sha}, "
                f"got {actual_sha}"
            )


def verify_checkpoint(
    checkpoint: dict,
) -> tuple[D0Config, CharacterTokenizer]:
    config_payload = checkpoint["model_config"]

    if config_payload != EXPECTED_CONFIG:
        raise ValueError(
            "POST-005 base model configuration changed"
        )

    tokenizer = CharacterTokenizer.from_dict(
        checkpoint["tokenizer"]
    )

    if len(tokenizer.alphabet) != 42:
        raise ValueError(
            "POST-005 tokenizer size changed"
        )

    config = D0Config(**config_payload)

    model = D0Model(config)

    counts = parameter_counts(model)

    if (
        counts["totalParameters"]
        != EXPECTED_PARAMETER_COUNT
    ):
        raise ValueError(
            "POST-005 parameter count changed"
        )

    return config, tokenizer


def prepare_training_state(
    checkpoint_path: Path,
    train_dataset_path: Path,
    lm_dataset_path: Path,
) -> dict:
    """Validate and construct POST-005 state without training."""

    checkpoint_path = checkpoint_path.resolve()
    train_dataset_path = train_dataset_path.resolve()
    lm_dataset_path = lm_dataset_path.resolve()

    verify_frozen_inputs(
        checkpoint_path,
        train_dataset_path,
        lm_dataset_path,
    )

    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    config, tokenizer = verify_checkpoint(checkpoint)

    train_examples_raw = load_instruction_jsonl(
        train_dataset_path
    )

    if len(train_examples_raw) != 40:
        raise ValueError(
            "POST-005 frozen training split must contain "
            "exactly 40 examples"
        )

    train_examples = encode_dataset(
        tokenizer=tokenizer,
        examples=train_examples_raw,
        context_length=config.context_length,
    )

    lm_text = lm_dataset_path.read_text(
        encoding="utf-8"
    )

    lm_tokens = torch.tensor(
        tokenizer.encode(lm_text),
        dtype=torch.long,
    )

    if (
        len(lm_tokens)
        <= config.context_length + 1
    ):
        raise ValueError(
            "LM retention corpus is too short"
        )

    return {
        "checkpoint": checkpoint,
        "config": config,
        "tokenizer": tokenizer,
        "train_examples": train_examples,
        "lm_tokens": lm_tokens,
    }


def run(
    checkpoint_path: Path,
    train_dataset_path: Path,
    lm_dataset_path: Path,
    output_path: Path,
    run_id: str,
) -> dict:
    """Execute the single frozen POST-005 training trajectory."""

    state = prepare_training_state(
        checkpoint_path=checkpoint_path,
        train_dataset_path=train_dataset_path,
        lm_dataset_path=lm_dataset_path,
    )

    seed_everything(SEED)

    checkpoint = state["checkpoint"]
    config = state["config"]
    tokenizer = state["tokenizer"]
    train_examples = state["train_examples"]
    lm_tokens = state["lm_tokens"]

    device = select_device()

    model = D0Model(config).to(device)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    original_counts = parameter_counts(model)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    # POST-005 deliberately creates a fresh optimizer.
    # No inherited optimizer state is loaded.

    sft_generator = torch.Generator().manual_seed(
        SFT_GENERATOR_SEED
    )

    lm_generator = torch.Generator().manual_seed(
        LM_GENERATOR_SEED
    )

    pad_token_id = 0
    metrics: list[dict] = []

    model.train()

    for step in range(1, MAX_STEPS + 1):
        indices = torch.randint(
            low=0,
            high=len(train_examples),
            size=(SFT_BATCH_SIZE,),
            generator=sft_generator,
        ).tolist()

        selected = [
            train_examples[index]
            for index in indices
        ]

        sft_inputs, sft_targets = pad_batch(
            selected,
            pad_token_id,
        )

        lm_inputs, lm_targets = lm_batch(
            lm_tokens,
            config.context_length,
            LM_BATCH_SIZE,
            lm_generator,
        )

        sft_inputs = sft_inputs.to(device)
        sft_targets = sft_targets.to(device)
        lm_inputs = lm_inputs.to(device)
        lm_targets = lm_targets.to(device)

        sft_logits, _ = model(sft_inputs)
        retention_logits, _ = model(lm_inputs)

        current_sft_loss = response_loss(
            sft_logits,
            sft_targets,
        )

        current_lm_loss = language_model_loss(
            retention_logits,
            lm_targets,
        )

        total_loss = mixed_loss(
            current_sft_loss,
            current_lm_loss,
            RETENTION_WEIGHT,
        )

        optimizer.zero_grad(set_to_none=True)

        total_loss.backward()

        gradient_norm = float(
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                GRADIENT_CLIP_NORM,
            ).item()
        )

        optimizer.step()

        metrics.append(
            {
                "step": step,
                "sftLoss": float(
                    current_sft_loss.item()
                ),
                "lmRetentionLoss": float(
                    current_lm_loss.item()
                ),
                "mixedLoss": float(
                    total_loss.item()
                ),
                "gradientNorm": gradient_norm,
                "supervisedTokens": int(
                    sft_targets.ne(
                        IGNORE_INDEX
                    ).sum().item()
                ),
                "lmTokens": int(
                    lm_targets.numel()
                ),
                "sampledTrainIndices": indices,
            }
        )

        if step in CANDIDATE_STEPS:
            snapshot_path = (
                output_path.resolve().parent
                / f"{output_path.resolve().stem}-step{step}.pt"
            )

            snapshot_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            snapshot_payload = {
                "format_version": 1,
                "model_name": "denarixx-d0-post005",
                "post_training_stage": (
                    "post005_development_mixed_retention"
                ),
                "run_id": run_id,
                "created_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "base_checkpoint": str(
                    checkpoint_path.resolve()
                ),
                "base_checkpoint_sha256": (
                    EXPECTED_BASE_SHA256
                ),
                "model_config": config.__dict__,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": (
                    optimizer.state_dict()
                ),
                "tokenizer": tokenizer.to_dict(),
                "parameter_counts": parameter_counts(model),
                "datasets": {
                    "supervisedTrain": {
                        "path": str(
                            train_dataset_path.resolve()
                        ),
                        "sha256": EXPECTED_TRAIN_SHA256,
                        "examples": 40,
                    },
                    "lmRetention": {
                        "path": str(
                            lm_dataset_path.resolve()
                        ),
                        "sha256": EXPECTED_LM_SHA256,
                        "tokens": len(lm_tokens),
                    },
                },
                "training": {
                    "optimizer": "AdamW",
                    "optimizerStateResumed": False,
                    "maxSteps": MAX_STEPS,
                    "candidateStep": step,
                    "candidateSteps": list(
                        CANDIDATE_STEPS
                    ),
                    "sftBatchSize": SFT_BATCH_SIZE,
                    "lmBatchSize": LM_BATCH_SIZE,
                    "learningRate": LEARNING_RATE,
                    "weightDecay": WEIGHT_DECAY,
                    "gradientClipNorm": (
                        GRADIENT_CLIP_NORM
                    ),
                    "retentionWeight": RETENTION_WEIGHT,
                    "seed": SEED,
                    "sftGeneratorSeed": (
                        SFT_GENERATOR_SEED
                    ),
                    "lmGeneratorSeed": (
                        LM_GENERATOR_SEED
                    ),
                    "scheduler": None,
                    "warmupSteps": 0,
                    "objective": (
                        "L_response + 0.25 * L_lm"
                    ),
                    "device": str(device),
                    "internalDatasetSplit": False,
                },
                "metrics": list(metrics),
            }

            torch.save(
                snapshot_payload,
                snapshot_path,
            )

    if parameter_counts(model) != original_counts:
        raise RuntimeError(
            "POST-005 changed model parameter counts"
        )

    output_path = output_path.resolve()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "format_version": 1,
        "model_name": "denarixx-d0-post005",
        "post_training_stage": (
            "post005_development_mixed_retention"
        ),
        "run_id": run_id,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "base_checkpoint": str(
            checkpoint_path.resolve()
        ),
        "base_checkpoint_sha256": (
            EXPECTED_BASE_SHA256
        ),
        "model_config": config.__dict__,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": (
            optimizer.state_dict()
        ),
        "tokenizer": tokenizer.to_dict(),
        "parameter_counts": parameter_counts(model),
        "datasets": {
            "supervisedTrain": {
                "path": str(
                    train_dataset_path.resolve()
                ),
                "sha256": EXPECTED_TRAIN_SHA256,
                "examples": 40,
            },
            "lmRetention": {
                "path": str(
                    lm_dataset_path.resolve()
                ),
                "sha256": EXPECTED_LM_SHA256,
                "tokens": len(lm_tokens),
            },
        },
        "training": {
            "optimizer": "AdamW",
            "optimizerStateResumed": False,
            "maxSteps": MAX_STEPS,
            "candidateStep": MAX_STEPS,
            "candidateSteps": list(
                CANDIDATE_STEPS
            ),
            "sftBatchSize": SFT_BATCH_SIZE,
            "lmBatchSize": LM_BATCH_SIZE,
            "learningRate": LEARNING_RATE,
            "weightDecay": WEIGHT_DECAY,
            "gradientClipNorm": (
                GRADIENT_CLIP_NORM
            ),
            "retentionWeight": RETENTION_WEIGHT,
            "seed": SEED,
            "sftGeneratorSeed": (
                SFT_GENERATOR_SEED
            ),
            "lmGeneratorSeed": (
                LM_GENERATOR_SEED
            ),
            "scheduler": None,
            "warmupSteps": 0,
            "objective": (
                "L_response + 0.25 * L_lm"
            ),
            "device": str(device),
            "internalDatasetSplit": False,
        },
        "metrics": metrics,
    }

    torch.save(payload, output_path)

    return {
        "status": "complete",
        "runId": run_id,
        "checkpointPath": str(output_path),
        "stepsExecuted": MAX_STEPS,
        "candidateStep": MAX_STEPS,
        "retentionWeight": RETENTION_WEIGHT,
        "parameterCounts": parameter_counts(model),
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--train-dataset",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--lm-dataset",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--run-id",
        required=True,
    )

    args = parser.parse_args()

    result = run(
        checkpoint_path=args.checkpoint,
        train_dataset_path=args.train_dataset,
        lm_dataset_path=args.lm_dataset,
        output_path=args.output,
        run_id=args.run_id,
    )

    print(json.dumps(result))


if __name__ == "__main__":
    main()
