from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import torch

from models.d0 import D0Config, D0Model


EXPECTED_PARAMETER_COUNT = 102784
EXPECTED_VOCAB_SIZE = 42
EXPECTED_CONTEXT_LENGTH = 32
EXPECTED_HIDDEN_SIZE = 64
EXPECTED_LAYERS = 2
EXPECTED_ATTENTION_HEADS = 4
EXPECTED_DROPOUT = 0.0

AGGREGATE_REGRESSION_TOLERANCE = 0.02
FAMILY_REGRESSION_TOLERANCE = 0.05

EXPECTED_FAMILIES = {
    "echo",
    "binary",
    "transform",
    "qa",
    "semantic",
}

EXPECTED_PER_FAMILY = 5


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def compare_results(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    baseline_loss = float(
        baseline["aggregateResponseLoss"]
    )
    candidate_loss = float(
        candidate["aggregateResponseLoss"]
    )

    baseline_exact = int(
        baseline["exactMatches"]
    )
    candidate_exact = int(
        candidate["exactMatches"]
    )

    aggregate_limit = baseline_loss * (
        1.0 + AGGREGATE_REGRESSION_TOLERANCE
    )

    aggregate_retention = (
        candidate_loss <= aggregate_limit
    )

    exact_strictly_better = (
        candidate_exact > baseline_exact
    )

    at_least_one_exact = candidate_exact >= 1

    baseline_family = baseline["perFamily"]
    candidate_family = candidate["perFamily"]

    family_comparison: dict[str, Any] = {}
    all_families_within_tolerance = True

    for family in sorted(EXPECTED_FAMILIES):
        baseline_family_loss = float(
            baseline_family[family]["responseLoss"]
        )
        candidate_family_loss = float(
            candidate_family[family]["responseLoss"]
        )

        limit = baseline_family_loss * (
            1.0 + FAMILY_REGRESSION_TOLERANCE
        )

        passed = candidate_family_loss <= limit

        if not passed:
            all_families_within_tolerance = False

        if baseline_family_loss == 0.0:
            if candidate_family_loss == 0.0:
                regression_percent = 0.0
            else:
                regression_percent = None
        else:
            regression_percent = (
                (
                    candidate_family_loss
                    - baseline_family_loss
                )
                / baseline_family_loss
                * 100.0
            )

        family_comparison[family] = {
            "baselineResponseLoss":
                baseline_family_loss,
            "candidateResponseLoss":
                candidate_family_loss,
            "maximumAllowedResponseLoss":
                limit,
            "regressionPercent":
                regression_percent,
            "withinTolerance":
                passed,
        }

    formal_pass = (
        exact_strictly_better
        and at_least_one_exact
        and all_families_within_tolerance
        and aggregate_retention
    )

    return {
        "baselineExactMatches":
            baseline_exact,
        "candidateExactMatches":
            candidate_exact,
        "exactMatchStrictlyImproved":
            exact_strictly_better,
        "candidateHasAtLeastOneExactMatch":
            at_least_one_exact,
        "baselineAggregateResponseLoss":
            baseline_loss,
        "candidateAggregateResponseLoss":
            candidate_loss,
        "maximumAllowedAggregateResponseLoss":
            aggregate_limit,
        "aggregateRetentionPassed":
            aggregate_retention,
        "aggregateRegressionTolerancePercent":
            2.0,
        "familyRegressionTolerancePercent":
            5.0,
        "allFamiliesWithinTolerance":
            all_families_within_tolerance,
        "perFamilyComparison":
            family_comparison,
        "formalPass":
            formal_pass,
    }


def validate_dataset_structure(
    rows: list[dict[str, Any]],
) -> None:
    counts = {
        family: 0
        for family in EXPECTED_FAMILIES
    }

    for row in rows:
        family = row.get("family")

        if family not in EXPECTED_FAMILIES:
            raise ValueError(
                f"Unexpected capability family: {family}"
            )

        instruction = row.get("instruction")
        response = row.get("response")

        if not isinstance(instruction, str):
            raise ValueError(
                "instruction must be a string"
            )

        if not isinstance(response, str):
            raise ValueError(
                "response must be a string"
            )

        counts[family] += 1

    for family in EXPECTED_FAMILIES:
        if counts[family] != EXPECTED_PER_FAMILY:
            raise ValueError(
                f"{family} expected "
                f"{EXPECTED_PER_FAMILY} examples, "
                f"got {counts[family]}"
            )


def verify_checkpoint_invariants(
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    config = checkpoint.get("model_config")
    state = checkpoint.get("model_state_dict")

    if not isinstance(config, dict):
        raise ValueError(
            "checkpoint missing model_config"
        )

    if not isinstance(state, dict):
        raise ValueError(
            "checkpoint missing model_state_dict"
        )

    expected = {
        "vocab_size": EXPECTED_VOCAB_SIZE,
        "context_length":
            EXPECTED_CONTEXT_LENGTH,
        "hidden_size": EXPECTED_HIDDEN_SIZE,
        "layers": EXPECTED_LAYERS,
        "attention_heads":
            EXPECTED_ATTENTION_HEADS,
        "dropout": EXPECTED_DROPOUT,
    }

    for key, value in expected.items():
        if config.get(key) != value:
            raise ValueError(
                f"Architecture invariant failed: {key}"
            )

    model = D0Model(
        D0Config(**config)
    )

    model.load_state_dict(
        state,
        strict=True,
    )

    parameter_count = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    if parameter_count != EXPECTED_PARAMETER_COUNT:
        raise ValueError(
            "Parameter count changed: "
            f"{parameter_count}"
        )

    return {
        "parameterCount": parameter_count,
        "modelConfig": config,
    }


def load_checkpoint_read_only(
    path: str | Path,
) -> dict[str, Any]:
    checkpoint = torch.load(
        Path(path),
        map_location="cpu",
        weights_only=False,
    )

    if not isinstance(checkpoint, dict):
        raise ValueError(
            "Checkpoint payload must be a dictionary"
        )

    return checkpoint


def run_formal_evaluation(
    baseline_checkpoint: str | Path,
    candidate_checkpoint: str | Path,
    dataset: str | Path,
) -> dict[str, Any]:
    """
    Execution entry point.

    Formal model scoring is deliberately not implemented
    during the build/freeze stage. This prevents accidental
    formal exposure before the evaluator and execution
    protocol are separately authorized.
    """
    raise RuntimeError(
        "POST-004 formal model scoring is not authorized "
        "by the evaluator-build stage."
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--baseline",
        required=True,
    )
    parser.add_argument(
        "--candidate",
        required=True,
    )
    parser.add_argument(
        "--dataset",
        required=True,
    )

    args = parser.parse_args()

    result = run_formal_evaluation(
        args.baseline,
        args.candidate,
        args.dataset,
    )

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
