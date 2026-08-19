"""Run a real Denarixx D0 research experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

from data.tiny_dataset import batch, load_text, split_tokens
from evaluation.d0_evaluator import evaluate_language_model
from models.d0 import D0Config, D0Model
from tokenizers.char import CharacterTokenizer
from training.reproducibility import (
    environment_metadata,
    seed_everything,
    select_device,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def parameter_counts(model: D0Model) -> dict:
    total = sum(parameter.numel() for parameter in model.parameters())
    trainable = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return {
        "totalParameters": int(total),
        "trainableParameters": int(trainable),
    }


def generate(
    model: D0Model,
    tokenizer: CharacterTokenizer,
    prompt: str,
    max_tokens: int,
    temperature: float,
    generator: torch.Generator | None = None,
) -> str:
    if not prompt:
        raise ValueError("generation prompt cannot be empty")

    if max_tokens < 1:
        raise ValueError("max_tokens must be >= 1")

    device = next(model.parameters()).device
    was_training = model.training
    model.eval()

    tokens = tokenizer.encode(prompt)

    input_tokens = torch.tensor(
        [tokens[-model.config.context_length :]],
        dtype=torch.long,
        device=device,
    )

    with torch.no_grad():
        for _ in range(max_tokens):
            context = input_tokens[:, -model.config.context_length :]
            logits, _ = model(context)

            next_logits = logits[:, -1, :] / max(temperature, 0.05)
            probabilities = torch.softmax(next_logits, dim=-1)

            # torch.multinomial with a CPU generator cannot be used directly
            # against tensors on every accelerator backend. Sampling on CPU
            # keeps this tiny research implementation portable.
            sampled = torch.multinomial(
                probabilities.detach().cpu(),
                num_samples=1,
                generator=generator,
            )

            next_token = sampled.to(device)
            input_tokens = torch.cat((input_tokens, next_token), dim=1)

    if was_training:
        model.train()

    return tokenizer.decode(input_tokens[0].detach().cpu().tolist())


def advance_scheduler(
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.CosineAnnealingLR,
) -> float:
    """
    Advance the D0 cosine schedule without allowing a completed cosine
    cycle to rebound during checkpoint continuation.

    Before T_max, preserve PyTorch CosineAnnealingLR behavior exactly.
    At or beyond T_max, hold every optimizer parameter group at eta_min.
    """

    if scheduler.last_epoch >= scheduler.T_max:
        eta_min = float(scheduler.eta_min)

        for group in optimizer.param_groups:
            group["lr"] = eta_min

        return eta_min

    scheduler.step()

    return float(scheduler.get_last_lr()[0])


def run(
    max_steps: int,
    seed: int,
    checkpoint_dir: Path,
    run_id: str,
    resume_checkpoint: Path | None = None,
    corpus_path: Path | None = None,
    batch_size: int = 8,
    learning_rate: float = 3e-4,
    normalization: str = "layernorm",
    position_encoding: str = "rope",
) -> dict:
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1")

    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    if learning_rate <= 0:
        raise ValueError("learning_rate must be > 0")

    if normalization not in {"layernorm", "rmsnorm"}:
        raise ValueError(
            "normalization must be 'layernorm' or 'rmsnorm'"
        )

    if position_encoding not in {"absolute", "rope"}:
        raise ValueError(
            "position_encoding must be 'absolute' or 'rope'"
        )

    seed_everything(seed)

    batch_generator = torch.Generator().manual_seed(seed)
    generation_generator = torch.Generator().manual_seed(seed + 1)

    device = select_device()

    if corpus_path is None:
        corpus_path = (
            Path(__file__).parent
            / "data"
            / "dev_corpus.txt"
        )

    corpus_path = corpus_path.resolve()

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"corpus not found: {corpus_path}"
        )

    corpus_text = load_text(corpus_path)
    dataset_hash = sha256_file(corpus_path)

    resume_state = None

    if resume_checkpoint:
        if not resume_checkpoint.exists():
            raise FileNotFoundError(
                f"resume checkpoint not found: {resume_checkpoint}"
            )

        resume_state = torch.load(
            resume_checkpoint,
            map_location="cpu",
            weights_only=False,
        )

        tokenizer = CharacterTokenizer.from_dict(
            resume_state["tokenizer"]
        )
    else:
        tokenizer = CharacterTokenizer.train(corpus_text)

    encoded = tokenizer.encode(corpus_text)
    train_tokens, validation_tokens = split_tokens(encoded)

    if resume_state:
        config = D0Config(**resume_state["model_config"])
    else:
        config = D0Config(
            vocab_size=tokenizer.vocab_size,
            context_length=32,
            hidden_size=64,
            layers=2,
            attention_heads=4,
            dropout=0.0,
            normalization=normalization,
            position_encoding=position_encoding,
        )

    model = D0Model(config).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=0.01,
    )

    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=max_steps,
        eta_min=3e-5,
    )

    start_step = 0

    if resume_state:
        model.load_state_dict(resume_state["model_state_dict"])
        optimizer.load_state_dict(resume_state["optimizer_state_dict"])

        if resume_state.get("scheduler_state_dict"):
            scheduler.load_state_dict(
                resume_state["scheduler_state_dict"]
            )

        start_step = int(
            resume_state.get("training_step", 0)
        )

        if max_steps <= start_step:
            raise ValueError(
                f"max_steps ({max_steps}) must be greater than "
                f"checkpoint step ({start_step})"
            )

    metrics: list[dict] = []
    started = time.perf_counter()
    created_at = datetime.now(timezone.utc).isoformat()

    initial_evaluation = evaluate_language_model(
        model=model,
        data=validation_tokens,
        context_length=config.context_length,
    )

    for step in range(start_step + 1, max_steps + 1):
        step_started = time.perf_counter()

        inputs, targets = batch(
            train_tokens,
            config.context_length,
            batch_size,
            batch_generator,
        )

        inputs = inputs.to(device)
        targets = targets.to(device)

        _, loss = model(inputs, targets)

        if loss is None:
            raise RuntimeError("D0 training produced no loss")

        optimizer.zero_grad(set_to_none=True)
        loss.backward()

        gradient_norm = float(
            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                1.0,
            ).item()
        )

        optimizer.step()
        learning_rate_used = advance_scheduler(
            optimizer,
            scheduler,
        )

        elapsed = max(
            time.perf_counter() - step_started,
            1e-6,
        )

        metric = {
            "step": step,
            "trainingLoss": float(loss.item()),
            "learningRate": learning_rate_used,
            "tokensProcessedThisRun": int(
                (step - start_step) * inputs.numel()
            ),
            "tokensPerSecond": float(
                inputs.numel() / elapsed
            ),
            "gradientNorm": gradient_norm,
            "elapsedSeconds": float(
                time.perf_counter() - started
            ),
        }

        metrics.append(metric)

    final_evaluation = evaluate_language_model(
        model=model,
        data=validation_tokens,
        context_length=config.context_length,
    )

    checkpoint_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    checkpoint_path = checkpoint_dir / f"{run_id}.pt"

    checkpoint_payload = {
        "format_version": 2,
        "model_name": "denarixx-d0-baseline",
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict(),
        "training_step": max_steps,
        "model_config": model.config_dict(),
        "parameter_counts": parameter_counts(model),
        "tokenizer": tokenizer.to_dict(),
        "dataset": {
            "id": corpus_path.stem,
            "path": str(corpus_path),
            "sha256": dataset_hash,
            "characters": len(corpus_text),
            "tokens": len(encoded),
            "trainTokens": int(len(train_tokens)),
            "validationTokens": int(
                len(validation_tokens)
            ),
            "provenance": (
                "local development corpus authored for "
                "Denarixx pipeline validation"
            ),
        },
        "seed": seed,
        "device": str(device),
        "environment": environment_metadata(),
        "created_at": created_at,
        "resumed_from_checkpoint": (
            str(resume_checkpoint)
            if resume_checkpoint
            else None
        ),
        "initial_evaluation": (
            initial_evaluation.to_dict()
        ),
        "final_evaluation": (
            final_evaluation.to_dict()
        ),
    }

    torch.save(
        checkpoint_payload,
        checkpoint_path,
    )

    inference_started = time.perf_counter()

    sample = generate(
        model=model,
        tokenizer=tokenizer,
        prompt="Denarixx ",
        max_tokens=24,
        temperature=0.8,
        generator=generation_generator,
    )

    inference_ms = (
        time.perf_counter() - inference_started
    ) * 1000

    result = {
        "runId": run_id,
        "status": "complete",
        "createdAt": created_at,
        "device": str(device),
        "model": "denarixx-d0-baseline",
        "dataset": corpus_path.stem,
        "datasetSha256": dataset_hash,
        "startStep": start_step,
        "maxSteps": max_steps,
        "stepsExecuted": max_steps - start_step,
        "seed": seed,
        "parameterCounts": parameter_counts(model),
        "initialEvaluation": (
            initial_evaluation.to_dict()
        ),
        "finalEvaluation": (
            final_evaluation.to_dict()
        ),
        "metrics": metrics,
        "checkpointPath": str(checkpoint_path),
        "sample": sample,
        "inference": {
            "tokensGenerated": 24,
            "latencyMs": inference_ms,
            "tokensPerSecond": (
                24
                / max(
                    inference_ms / 1000,
                    1e-6,
                )
            ),
        },
        "modelConfig": model.config_dict(),
        "trainingConfig": {
            "batchSize": batch_size,
            "learningRate": learning_rate,
            "maxSteps": max_steps,
        },
        "environment": environment_metadata(),
        "limitations": [
            "D0 is a tiny research model.",
            "The current tokenizer is character-level.",
            "The current corpus is only for pipeline validation.",
            "These results are not frontier-model benchmarks.",
        ],
    }

    report_path = (
        Path(__file__).parent.parent
        / "research"
        / "reports"
        / f"{run_id}.json"
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    result["reportPath"] = str(report_path)

    return result


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--run-id",
        required=True,
    )

    parser.add_argument(
        "--resume-checkpoint",
        type=Path,
    )

    parser.add_argument(
        "--corpus",
        type=Path,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=3e-4,
    )

    parser.add_argument(
        "--normalization",
        choices=["layernorm", "rmsnorm"],
        default="layernorm",
    )

    parser.add_argument(
        "--position-encoding",
        choices=["absolute", "rope"],
        default="rope",
    )

    args = parser.parse_args()

    try:
        result = run(
            max_steps=args.max_steps,
            seed=args.seed,
            checkpoint_dir=args.checkpoint_dir,
            run_id=args.run_id,
            resume_checkpoint=args.resume_checkpoint,
            corpus_path=args.corpus,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            normalization=args.normalization,
            position_encoding=args.position_encoding,
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
