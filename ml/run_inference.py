"""Load a D0 checkpoint and generate a measured sample."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch

from models.d0 import D0Config, D0Model
from tokenizers.char import CharacterTokenizer


def run(checkpoint_path: Path, prompt: str, max_tokens: int, temperature: float) -> dict:
    started = time.perf_counter()
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    config = D0Config(**checkpoint["model_config"])
    tokenizer = CharacterTokenizer.from_dict(checkpoint["tokenizer"])
    model = D0Model(config)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    tokens = tokenizer.encode(prompt)
    input_tokens = torch.tensor([tokens[-config.context_length :]], dtype=torch.long)
    with torch.no_grad():
        for _ in range(max_tokens):
            logits, _ = model(input_tokens[:, -config.context_length :])
            probabilities = torch.softmax(logits[:, -1, :] / max(temperature, 0.05), dim=-1)
            next_token = torch.argmax(probabilities, dim=-1, keepdim=True)
            input_tokens = torch.cat((input_tokens, next_token), dim=1)
    output = tokenizer.decode(input_tokens[0].tolist())
    latency_ms = (time.perf_counter() - started) * 1000
    return {
        "status": "complete",
        "output": output,
        "tokensGenerated": max_tokens,
        "latencyMs": latency_ms,
        "tokensPerSecond": max_tokens / max(latency_ms / 1000, 1e-6),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--max-tokens", type=int, default=24)
    parser.add_argument("--temperature", type=float, default=0.8)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.checkpoint, args.prompt, args.max_tokens, args.temperature)))
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}))
        raise


if __name__ == "__main__":
    main()