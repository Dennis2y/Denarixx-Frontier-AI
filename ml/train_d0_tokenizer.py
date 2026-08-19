"""Train and evaluate the Denarixx D0.3 custom tokenizer."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import tokenizers

from ml.tokenizers.char import CharacterTokenizer
from ml.tokenizers.d0_bpe import D0BPETokenizer


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def compression_metrics(
    text: str,
    token_count: int,
) -> dict:
    words = text.split()
    characters = len(text)

    return {
        "characters": characters,
        "words": len(words),
        "tokens": token_count,
        "tokensPerCharacter": (
            token_count / characters
            if characters
            else None
        ),
        "tokensPerWord": (
            token_count / len(words)
            if words
            else None
        ),
        "charactersPerToken": (
            characters / token_count
            if token_count
            else None
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--corpus",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--vocab-size",
        type=int,
        default=64,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.corpus.exists():
        raise FileNotFoundError(
            f"corpus not found: {args.corpus}"
        )

    text = args.corpus.read_text(
        encoding="utf-8"
    )

    if not text:
        raise ValueError("corpus is empty")

    args.output_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    custom = D0BPETokenizer.train(
        text=text,
        vocab_size=args.vocab_size,
        min_frequency=1,
    )

    baseline = CharacterTokenizer.train(text)

    custom_ids = custom.encode(text)
    baseline_ids = baseline.encode(text)

    reconstructed = custom.decode(custom_ids)

    if reconstructed != text:
        raise RuntimeError(
            "custom tokenizer round-trip failed"
        )

    tokenizer_path = (
        args.output_dir / "tokenizer.json"
    )

    custom.save(tokenizer_path)

    vocabulary_path = (
        args.output_dir / "vocabulary.json"
    )

    vocabulary_path.write_text(
        json.dumps(
            custom.vocabulary(),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    custom_metrics = compression_metrics(
        text,
        len(custom_ids),
    )

    baseline_metrics = compression_metrics(
        text,
        len(baseline_ids),
    )

    comparison = {
        "milestone": "D0.3",
        "status": "complete",
        "objective": "Train a custom tokenizer.",
        "tokenizer": {
            "name": "denarixx-d0-bpe",
            "type": "BPE",
            "trainedBy": "Denarixx",
            "pretrainedVocabularyUsed": False,
            "requestedVocabSize": args.vocab_size,
            "actualVocabSize": custom.vocab_size,
            "specialTokens": [
                "<pad>",
                "<unk>",
                "<bos>",
                "<eos>",
            ],
        },
        "dataset": {
            "path": str(args.corpus),
            "sha256": sha256_file(args.corpus),
            "characters": len(text),
            "utf8Bytes": len(
                text.encode("utf-8")
            ),
            "lines": len(text.splitlines()),
        },
        "customTokenizerMetrics": custom_metrics,
        "characterBaselineMetrics": baseline_metrics,
        "comparison": {
            "baselineTokenCount": len(
                baseline_ids
            ),
            "customTokenCount": len(
                custom_ids
            ),
            "tokenCountReduction": (
                len(baseline_ids)
                - len(custom_ids)
            ),
            "tokenCountReductionFraction": (
                (
                    len(baseline_ids)
                    - len(custom_ids)
                )
                / len(baseline_ids)
                if baseline_ids
                else None
            ),
        },
        "roundTripVerified": True,
        "compatibility": {
            "integratedIntoD0Model": False,
            "existingD0CheckpointsCompatible": False,
            "reason": (
                "D0.3 intentionally trains and evaluates "
                "the tokenizer independently. Existing D0 "
                "checkpoints retain their original "
                "character-tokenizer vocabulary."
            ),
        },
        "environment": {
            "pythonVersion": platform.python_version(),
            "pythonImplementation": (
                platform.python_implementation()
            ),
            "platform": platform.platform(),
            "tokenizersVersion": tokenizers.__version__,
        },
        "limitations": [
            (
                "The D0.3 corpus is a tiny local "
                "development corpus."
            ),
            (
                "Compression results are pipeline-validation "
                "results, not production tokenizer benchmarks."
            ),
            (
                "Multilingual efficiency is not established "
                "by this corpus."
            ),
            (
                "The tokenizer is not yet integrated into "
                "D0 model training or inference."
            ),
        ],
        "createdAt": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    comparison_path = (
        args.output_dir / "comparison.json"
    )

    comparison_path.write_text(
        json.dumps(
            comparison,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    manifest = {
        "milestone": "D0.3",
        "artifacts": {
            "tokenizer": {
                "path": str(tokenizer_path),
                "sha256": sha256_file(
                    tokenizer_path
                ),
            },
            "vocabulary": {
                "path": str(vocabulary_path),
                "sha256": sha256_file(
                    vocabulary_path
                ),
            },
            "comparison": {
                "path": str(comparison_path),
                "sha256": sha256_file(
                    comparison_path
                ),
            },
        },
    }

    manifest_path = (
        args.output_dir / "manifest.json"
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            comparison,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
