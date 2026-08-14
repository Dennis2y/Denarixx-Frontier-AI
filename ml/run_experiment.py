"""Run a small, real Denarixx D0 experiment and emit one JSON result."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import torch

from data.tiny_dataset import batch, load_text, split_tokens
from models.d0 import D0Config, D0Model
from tokenizers.char import CharacterTokenizer


def evaluate(model: D0Model, data: torch.Tensor, config: D0Config, generator: torch.Generator) -> float:
    model.eval()
    with torch.no_grad():
        inputs, targets = batch(data, config.context_length, 1, generator)
        _, loss = model(inputs, targets)
    model.train()
    return float(loss.item()) if loss is not None else math.nan


def generate(model: D0Model, tokenizer: CharacterTokenizer, prompt: str, max_tokens: int, temperature: float) -> str:
    model.eval()
    tokens = tokenizer.encode(prompt)
    input_tokens = torch.tensor([tokens[-model.config.context_length :]], dtype=torch.long)
    with torch.no_grad():
        for _ in range(max_tokens):
            logits, _ = model(input_tokens[:, -model.config.context_length :])
            probabilities = torch.softmax(logits[:, -1, :] / max(temperature, 0.05), dim=-1)
            next_token = torch.multinomial(probabilities, num_samples=1)
            input_tokens = torch.cat((input_tokens, next_token), dim=1)
    model.train()
    return tokenizer.decode(input_tokens[0].tolist())


def run(max_steps: int, seed: int, checkpoint_dir: Path, run_id: str) -> dict:
    torch.manual_seed(seed)
    generator = torch.Generator().manual_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    corpus_path = Path(__file__).parent / "data" / "dev_corpus.txt"
    tokenizer = CharacterTokenizer.train(load_text(corpus_path))
    train_tokens, validation_tokens = split_tokens(tokenizer.encode(load_text(corpus_path)))
    config = D0Config(vocab_size=tokenizer.vocab_size, context_length=32, hidden_size=64, layers=2, attention_heads=4)
    model = D0Model(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    metrics: list[dict] = []
    started = time.perf_counter()

    for step in range(1, max_steps + 1):
        step_started = time.perf_counter()
        inputs, targets = batch(train_tokens, config.context_length, 4, generator)
        inputs, targets = inputs.to(device), targets.to(device)
        _, loss = model(inputs, targets)
        if loss is None:
            raise RuntimeError("D0 training produced no loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        gradient_norm = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0).item())
        optimizer.step()
        elapsed = max(time.perf_counter() - step_started, 1e-6)
        validation_loss = evaluate(model, validation_tokens, config, generator)
        metrics.append(
            {
                "step": step,
                "trainingLoss": float(loss.item()),
                "validationLoss": validation_loss,
                "learningRate": 3e-4,
                "tokensProcessed": step * inputs.numel(),
                "tokensPerSecond": float(inputs.numel() / elapsed),
                "gradientNorm": gradient_norm,
                "elapsedSeconds": float(time.perf_counter() - started),
            }
        )

    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / f"{run_id}.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "training_step": max_steps,
            "model_config": model.config_dict(),
            "tokenizer": tokenizer.to_dict(),
            "dataset": {"path": str(corpus_path), "provenance": "local development corpus authored for Denarixx pipeline validation"},
            "seed": seed,
        },
        checkpoint_path,
    )
    output_started = time.perf_counter()
    sample = generate(model, tokenizer, "Denarixx ", 24, 0.8)
    inference_ms = (time.perf_counter() - output_started) * 1000
    return {
        "runId": run_id,
        "status": "complete",
        "device": str(device),
        "model": "denarixx-d0-baseline",
        "dataset": "denarixx-local-dev-v1",
        "maxSteps": max_steps,
        "seed": seed,
        "metrics": metrics,
        "checkpointPath": str(checkpoint_path),
        "sample": sample,
        "inference": {
            "tokensGenerated": 24,
            "latencyMs": inference_ms,
            "tokensPerSecond": 24 / max(inference_ms / 1000, 1e-6),
        },
        "modelConfig": model.config_dict(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-steps", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.max_steps, args.seed, args.checkpoint_dir, args.run_id)))
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        raise


if __name__ == "__main__":
    main()