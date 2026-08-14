"""Compare Denarixx research reports without inventing a winner."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def load_report(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def summarize(paths: list[Path]) -> dict:
    reports = [load_report(path) for path in paths]

    if not reports:
        raise ValueError("at least one report is required")

    losses = [
        float(
            report["finalEvaluation"][
                "average_loss"
            ]
        )
        for report in reports
    ]

    perplexities = [
        float(
            report["finalEvaluation"][
                "perplexity"
            ]
        )
        for report in reports
    ]

    throughputs = []

    for report in reports:
        values = [
            float(metric["tokensPerSecond"])
            for metric in report.get(
                "metrics",
                [],
            )
            if float(
                metric["tokensPerSecond"]
            ) > 0
        ]

        # Ignore the first step because accelerator
        # initialization/warm-up heavily distorts it.
        if len(values) > 1:
            values = values[1:]

        if values:
            throughputs.append(
                statistics.mean(values)
            )

    return {
        "runs": len(reports),
        "runIds": [
            report["runId"]
            for report in reports
        ],
        "seeds": [
            report["seed"]
            for report in reports
        ],
        "meanValidationLoss": (
            statistics.mean(losses)
        ),
        "validationLossStdDev": (
            statistics.stdev(losses)
            if len(losses) > 1
            else 0.0
        ),
        "meanPerplexity": (
            statistics.mean(perplexities)
        ),
        "perplexityStdDev": (
            statistics.stdev(perplexities)
            if len(perplexities) > 1
            else 0.0
        ),
        "meanTrainingTokensPerSecond": (
            statistics.mean(throughputs)
            if throughputs
            else None
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "reports",
        nargs="+",
        type=Path,
    )

    args = parser.parse_args()

    print(
        json.dumps(
            summarize(args.reports),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
