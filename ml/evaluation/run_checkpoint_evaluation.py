"""Evaluate a saved Denarixx D0 checkpoint independently."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from data.tiny_dataset import load_text, split_tokens
from evaluation.d0_evaluator import evaluate_language_model
from models.d0 import D0Config, D0Model
from tokenizers.char import CharacterTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    checkpoint = torch.load(
        args.checkpoint,
        map_location="cpu",
        weights_only=False,
    )

    config = D0Config(
        **checkpoint["model_config"]
    )

    tokenizer = CharacterTokenizer.from_dict(
        checkpoint["tokenizer"]
    )

    model = D0Model(config)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    corpus_path = (
        ML_ROOT / "data" / "dev_corpus.txt"
    )

    tokens = tokenizer.encode(
        load_text(corpus_path)
    )

    _, validation_tokens = split_tokens(tokens)

    result = evaluate_language_model(
        model=model,
        data=validation_tokens,
        context_length=config.context_length,
    )

    print(
        json.dumps(
            {
                "status": "complete",
                "checkpoint": str(
                    args.checkpoint
                ),
                "model": checkpoint.get(
                    "model_name",
                    "denarixx-d0",
                ),
                "trainingStep": checkpoint.get(
                    "training_step"
                ),
                "evaluation": result.to_dict(),
            }
        )
    )


if __name__ == "__main__":
    main()
