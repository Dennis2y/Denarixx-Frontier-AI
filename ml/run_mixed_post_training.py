"""D0-POST-002 mixed SFT + LM-retention runner."""

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
    split_instruction_dataset,
)
from run_sft import pad_batch
from tokenizers.char import CharacterTokenizer


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


def parameter_counts(
    model: torch.nn.Module,
) -> dict[str, int]:
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


def run(
    checkpoint_path: Path,
    sft_dataset_path: Path,
    lm_dataset_path: Path,
    output_dir: Path,
    run_id: str,
    max_steps: int = 20,
    sft_batch_size: int = 4,
    lm_batch_size: int = 4,
    learning_rate: float = 1e-4,
    retention_weight: float = 0.25,
    seed: int = 42,
) -> dict:

    if max_steps < 1:
        raise ValueError(
            "max_steps must be >= 1"
        )

    if sft_batch_size < 1:
        raise ValueError(
            "sft_batch_size must be >= 1"
        )

    if lm_batch_size < 1:
        raise ValueError(
            "lm_batch_size must be >= 1"
        )

    if learning_rate <= 0:
        raise ValueError(
            "learning_rate must be > 0"
        )

    if retention_weight < 0:
        raise ValueError(
            "retention_weight must be >= 0"
        )

    checkpoint_path = checkpoint_path.resolve()
    sft_dataset_path = sft_dataset_path.resolve()
    lm_dataset_path = lm_dataset_path.resolve()

    for path in [
        checkpoint_path,
        sft_dataset_path,
        lm_dataset_path,
    ]:
        if not path.exists():
            raise FileNotFoundError(str(path))

    seed_everything(seed)

    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    config = D0Config(
        **checkpoint["model_config"]
    )

    tokenizer = CharacterTokenizer.from_dict(
        checkpoint["tokenizer"]
    )

    sft_examples = load_instruction_jsonl(
        sft_dataset_path
    )

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=sft_examples,
        context_length=config.context_length,
    )

    train_examples, validation_examples = (
        split_instruction_dataset(
            encoded,
            validation_fraction=0.25,
        )
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

    device = select_device()

    model = D0Model(config).to(device)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    original_counts = parameter_counts(model)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=0.01,
    )

    sft_generator = (
        torch.Generator().manual_seed(seed)
    )

    lm_generator = (
        torch.Generator().manual_seed(seed + 1)
    )

    pad_token_id = 0
    metrics = []

    model.train()

    for step in range(1, max_steps + 1):

        indices = torch.randint(
            low=0,
            high=len(train_examples),
            size=(sft_batch_size,),
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
            lm_batch_size,
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
            retention_weight,
        )

        optimizer.zero_grad(
            set_to_none=True
        )

        total_loss.backward()

        gradient_norm = float(
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                1.0,
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
            }
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir / f"{run_id}.pt"
    )

    payload = {
        "format_version": 1,
        "model_name": (
            "denarixx-d0-mixed-post-training"
        ),
        "post_training_stage": (
            "mixed_sft_lm_retention"
        ),
        "run_id": run_id,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "base_checkpoint": str(
            checkpoint_path
        ),
        "base_checkpoint_sha256": (
            sha256_file(checkpoint_path)
        ),
        "model_config": model.config_dict(),
        "model_state_dict": (
            model.state_dict()
        ),
        "optimizer_state_dict": (
            optimizer.state_dict()
        ),
        "tokenizer": tokenizer.to_dict(),
        "parameter_counts": (
            parameter_counts(model)
        ),
        "datasets": {
            "sft": {
                "path": str(
                    sft_dataset_path
                ),
                "sha256": sha256_file(
                    sft_dataset_path
                ),
                "examples": len(
                    sft_examples
                ),
                "trainingExamples": len(
                    train_examples
                ),
                "validationExamples": len(
                    validation_examples
                ),
            },
            "lmRetention": {
                "path": str(
                    lm_dataset_path
                ),
                "sha256": sha256_file(
                    lm_dataset_path
                ),
                "tokens": len(lm_tokens),
            },
        },
        "training": {
            "maxSteps": max_steps,
            "sftBatchSize": sft_batch_size,
            "lmBatchSize": lm_batch_size,
            "learningRate": learning_rate,
            "weightDecay": 0.01,
            "gradientClipNorm": 1.0,
            "retentionWeight": (
                retention_weight
            ),
            "seed": seed,
            "device": str(device),
            "objective": (
                "L_sft + lambda * L_lm"
            ),
        },
        "metrics": metrics,
    }

    if (
        parameter_counts(model)
        != original_counts
    ):
        raise RuntimeError(
            "parameter count changed"
        )

    torch.save(
        payload,
        output_path,
    )

    return {
        "status": "complete",
        "runId": run_id,
        "checkpointPath": str(
            output_path
        ),
        "stepsExecuted": max_steps,
        "retentionWeight": (
            retention_weight
        ),
        "parameterCounts": (
            parameter_counts(model)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--sft-dataset",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--lm-dataset",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--run-id",
        required=True,
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--sft-batch-size",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--lm-batch-size",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-4,
    )

    parser.add_argument(
        "--retention-weight",
        type=float,
        default=0.25,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    args = parser.parse_args()

    result = run(
        checkpoint_path=args.checkpoint,
        sft_dataset_path=args.sft_dataset,
        lm_dataset_path=args.lm_dataset,
        output_dir=args.output_dir,
        run_id=args.run_id,
        max_steps=args.max_steps,
        sft_batch_size=args.sft_batch_size,
        lm_batch_size=args.lm_batch_size,
        learning_rate=args.learning_rate,
        retention_weight=args.retention_weight,
        seed=args.seed,
    )

    print(json.dumps(result))


if __name__ == "__main__":
    main()
