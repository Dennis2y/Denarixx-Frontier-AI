"""Run deterministic greedy inference from a Denarixx D0 checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from inference.d0_inference import (
    run_greedy_inference,
)


def run(
    checkpoint_path: Path,
    prompt: str,
    max_tokens: int,
    temperature: float | None = None,
) -> dict:
    """
    Compatibility entrypoint.

    D0-INF-001 defines the canonical inference mode as greedy decoding.
    The historical temperature argument is accepted for compatibility
    but does not affect deterministic greedy decoding.
    """

    result = run_greedy_inference(
        checkpoint_path=checkpoint_path,
        prompt=prompt,
        max_tokens=max_tokens,
    )

    payload = result.to_dict()

    if temperature is not None:
        payload["temperatureIgnored"] = True

    return payload


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--prompt",
        required=True,
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=24,
    )

    # Retained so the existing API invocation does not break.
    # Greedy decoding is deterministic and temperature-independent.
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
    )

    args = parser.parse_args()

    try:
        print(
            json.dumps(
                run(
                    checkpoint_path=args.checkpoint,
                    prompt=args.prompt,
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                )
            )
        )
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
