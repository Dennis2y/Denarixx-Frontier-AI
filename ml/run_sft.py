"""Denarixx D0 supervised fine-tuning runner.

D0-POST-001 proves that an accepted pretrained D0 checkpoint can be
post-trained on instruction/response examples while preserving the
pretrained tokenizer and model architecture.

This is research infrastructure, not a production training system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

from models.d0 import D0Config, D0Model
from post_training.sft_data import (
    IGNORE_INDEX,
    encode_dataset,
    load_instruction_jsonl,
    split_instruction_dataset,
)
from post_training.sft_evaluator import (
    masked_response_loss,
)
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


def response_only_loss(
    logits: torch.Tensor,
    targets: torch.Tensor,
) -> torch.Tensor:
    """Compatibility wrapper around canonical SFT loss."""

    if not bool(
        targets.ne(IGNORE_INDEX).any()
    ):
        raise ValueError(
            "SFT batch contains no supervised response tokens"
        )

    return masked_response_loss(
        logits,
        targets,
    )


def pad_batch(
    examples: list,
    pad_token_id: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    if not examples:
        raise ValueError("cannot build an empty SFT batch")

    max_length = max(
        len(example.input_ids)
        for example in examples
    )

    inputs: list[list[int]] = []
    targets: list[list[int]] = []

    for example in examples:
        padding = (
            max_length
            - len(example.input_ids)
        )

        inputs.append(
            list(example.input_ids)
            + [pad_token_id] * padding
        )

        targets.append(
            list(example.target_ids)
            + [IGNORE_INDEX] * padding
        )

    return (
        torch.tensor(
            inputs,
            dtype=torch.long,
        ),
        torch.tensor(
            targets,
            dtype=torch.long,
        ),
    )


def evaluate_sft(
    model: D0Model,
    encoded_examples: list,
    pad_token_id: int,
    device: torch.device,
) -> dict[str, float | int]:
    was_training = model.training
    model.eval()

    total_loss = 0.0
    batches = 0
    supervised_tokens = 0

    with torch.no_grad():
        for example in encoded_examples:
            inputs, targets = pad_batch(
                [example],
                pad_token_id,
            )

            inputs = inputs.to(device)
            targets = targets.to(device)

            logits, _ = model(inputs)

            loss = response_only_loss(
                logits,
                targets,
            )

            count = int(
                targets.ne(IGNORE_INDEX)
                .sum()
                .item()
            )

            total_loss += (
                float(loss.item())
                * count
            )

            supervised_tokens += count
            batches += 1

    if was_training:
        model.train()

    if supervised_tokens < 1:
        raise RuntimeError(
            "SFT evaluation produced no supervised tokens"
        )

    average_loss = (
        total_loss
        / supervised_tokens
    )

    try:
        perplexity = math.exp(average_loss)
    except OverflowError:
        perplexity = math.inf

    return {
        "averageLoss": average_loss,
        "perplexity": perplexity,
        "examplesEvaluated": batches,
        "supervisedTokens": supervised_tokens,
    }


def run(
    checkpoint_path: Path,
    dataset_path: Path,
    output_dir: Path,
    run_id: str,
    max_steps: int = 20,
    batch_size: int = 4,
    learning_rate: float = 1e-4,
    seed: int = 42,
) -> dict:
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")

    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    if learning_rate <= 0:
        raise ValueError(
            "learning_rate must be > 0"
        )

    checkpoint_path = checkpoint_path.resolve()
    dataset_path = dataset_path.resolve()

    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"checkpoint not found: {checkpoint_path}"
        )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"SFT dataset not found: {dataset_path}"
        )

    seed_everything(seed)

    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    if "model_config" not in checkpoint:
        raise ValueError(
            "checkpoint has no model_config"
        )

    if "tokenizer" not in checkpoint:
        raise ValueError(
            "checkpoint has no tokenizer"
        )

    config = D0Config(
        **checkpoint["model_config"]
    )

    tokenizer = CharacterTokenizer.from_dict(
        checkpoint["tokenizer"]
    )

    examples = load_instruction_jsonl(
        dataset_path
    )

    encoded = encode_dataset(
        tokenizer=tokenizer,
        examples=examples,
        context_length=config.context_length,
    )

    if not encoded:
        raise ValueError(
            "SFT dataset contains no encoded examples"
        )

    train_examples, validation_examples = (
        split_instruction_dataset(
            encoded,
            validation_fraction=0.25,
        )
    )

    if not train_examples:
        raise ValueError(
            "SFT training split contains no examples"
        )

    if not validation_examples:
        raise ValueError(
            "SFT validation split contains no examples"
        )

    device = select_device()

    model = D0Model(config).to(device)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    pretrained_counts = parameter_counts(model)

    # CharacterTokenizer has no dedicated PAD token.
    # Padding inputs are ignored in the loss, so reuse token 0
    # strictly for padded input positions.
    pad_token_id = 0

    initial_evaluation = evaluate_sft(
        model=model,
        encoded_examples=validation_examples,
        pad_token_id=pad_token_id,
        device=device,
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=0.01,
    )

    generator = torch.Generator().manual_seed(
        seed
    )

    metrics: list[dict] = []

    model.train()

    started = time.perf_counter()

    for step in range(1, max_steps + 1):
        indices = torch.randint(
            low=0,
            high=len(train_examples),
            size=(batch_size,),
            generator=generator,
        ).tolist()

        selected = [
            train_examples[index]
            for index in indices
        ]

        inputs, targets = pad_batch(
            selected,
            pad_token_id,
        )

        inputs = inputs.to(device)
        targets = targets.to(device)

        step_started = time.perf_counter()

        logits, _ = model(inputs)

        loss = response_only_loss(
            logits,
            targets,
        )

        optimizer.zero_grad(
            set_to_none=True
        )

        loss.backward()

        gradient_norm = float(
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                1.0,
            ).item()
        )

        optimizer.step()

        supervised_tokens = int(
            targets.ne(IGNORE_INDEX)
            .sum()
            .item()
        )

        elapsed = max(
            time.perf_counter()
            - step_started,
            1e-6,
        )

        metrics.append(
            {
                "step": step,
                "trainingLoss": float(
                    loss.item()
                ),
                "gradientNorm": gradient_norm,
                "supervisedTokens": supervised_tokens,
                "tokensPerSecond": (
                    supervised_tokens
                    / elapsed
                ),
            }
        )

    final_evaluation = evaluate_sft(
        model=model,
        encoded_examples=validation_examples,
        pad_token_id=pad_token_id,
        device=device,
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / f"{run_id}.pt"
    )

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    payload = {
        "format_version": 1,
        "model_name": "denarixx-d0-sft",
        "post_training_stage": "sft",
        "run_id": run_id,
        "created_at": created_at,
        "base_checkpoint": str(
            checkpoint_path
        ),
        "base_training_step": checkpoint.get(
            "training_step"
        ),
        "model_config": model.config_dict(),
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": (
            optimizer.state_dict()
        ),
        "tokenizer": tokenizer.to_dict(),
        "parameter_counts": (
            parameter_counts(model)
        ),
        "dataset": {
            "path": str(dataset_path),
            "sha256": sha256_file(
                dataset_path
            ),
            "examples": len(examples),
            "encodedExamples": len(encoded),
            "trainingExamples": len(train_examples),
            "validationExamples": len(validation_examples),
            "validationFraction": 0.25,
            "splitStrategy": "ordered_tail_holdout",
        },
        "training": {
            "maxSteps": max_steps,
            "batchSize": batch_size,
            "learningRate": learning_rate,
            "seed": seed,
            "device": str(device),
        },
        "initial_evaluation": (
            initial_evaluation
        ),
        "final_evaluation": (
            final_evaluation
        ),
        "metrics": metrics,
    }

    torch.save(
        payload,
        output_path,
    )

    elapsed_seconds = (
        time.perf_counter()
        - started
    )

    return {
        "runId": run_id,
        "status": "complete",
        "stage": "sft",
        "baseCheckpoint": str(
            checkpoint_path
        ),
        "checkpointPath": str(
            output_path
        ),
        "device": str(device),
        "seed": seed,
        "stepsExecuted": max_steps,
        "datasetExamples": len(examples),
        "trainingExamples": len(train_examples),
        "validationExamples": len(validation_examples),
        "validationFraction": 0.25,
        "splitStrategy": "ordered_tail_holdout",
        "parameterCounts": (
            parameter_counts(model)
        ),
        "pretrainedParameterCounts": (
            pretrained_counts
        ),
        "initialEvaluation": (
            initial_evaluation
        ),
        "finalEvaluation": (
            final_evaluation
        ),
        "metrics": metrics,
        "elapsedSeconds": elapsed_seconds,
        "modelConfig": model.config_dict(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--dataset",
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
        "--batch-size",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-4,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    args = parser.parse_args()

    try:
        result = run(
            checkpoint_path=args.checkpoint,
            dataset_path=args.dataset,
            output_dir=args.output_dir,
            run_id=args.run_id,
            max_steps=args.max_steps,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            seed=args.seed,
        )

        print(json.dumps(result))

    except Exception as error:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error": str(error),
                }
            )
        )
        raise


if __name__ == "__main__":
    main()
