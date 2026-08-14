"""Canonical independent checkpoint evaluation for Denarixx D0."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ML_ROOT),
    )

from evaluation.d0_eval001 import (
    evaluate_checkpoint,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--lm-data",
        type=Path,
        default=(
            ML_ROOT
            / "data"
            / "d0_eval001_lm.txt"
        ),
    )

    parser.add_argument(
        "--instruction-data",
        type=Path,
        default=(
            ML_ROOT
            / "data"
            / "d0_eval001_instructions.jsonl"
        ),
    )

    args = parser.parse_args()

    result = evaluate_checkpoint(
        checkpoint_path=args.checkpoint,
        lm_path=args.lm_data,
        instruction_path=(
            args.instruction_data
        ),
    )

    print(
        json.dumps(
            {
                "status": "complete",
                "evaluation": result,
            }
        )
    )


if __name__ == "__main__":
    main()
