from __future__ import annotations

from collections import defaultdict
from typing import Any


EXPECTED_FAMILIES = {
    "echo",
    "binary",
    "transform",
    "qa",
    "semantic",
}


def adapt_scoring_result(
    raw_result: dict[str, Any],
    dataset_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Convert the frozen POST-003 scoring backend result into
    the schema required by the frozen POST-004 comparison policy.

    This function performs aggregation only.

    It does not load a model.
    It does not perform inference.
    It does not read the formal dataset itself.
    """

    results = raw_result.get("results")

    if not isinstance(results, list):
        raise ValueError("raw result missing results")

    if len(results) != len(dataset_rows):
        raise ValueError(
            "scoring result count does not match dataset"
        )

    total_loss_sum = 0.0
    total_tokens = 0
    exact_matches = 0

    family_loss_sum: dict[str, float] = defaultdict(float)
    family_tokens: dict[str, int] = defaultdict(int)
    family_exact: dict[str, int] = defaultdict(int)
    family_examples: dict[str, int] = defaultdict(int)

    adapted_results = []

    for scored, row in zip(results, dataset_rows):
        family = row.get("family")

        if family not in EXPECTED_FAMILIES:
            raise ValueError(
                f"unexpected capability family: {family}"
            )

        response_loss = float(scored["responseLoss"])
        response_tokens = int(scored["responseTokens"])
        exact = bool(scored["exactMatch"])

        if response_tokens <= 0:
            raise ValueError(
                "responseTokens must be positive"
            )

        # The backend exposes mean response loss for each
        # example. Recover its token-weighted loss sum so
        # aggregate/family means preserve backend semantics.
        loss_sum = response_loss * response_tokens

        total_loss_sum += loss_sum
        total_tokens += response_tokens
        exact_matches += int(exact)

        family_loss_sum[family] += loss_sum
        family_tokens[family] += response_tokens
        family_exact[family] += int(exact)
        family_examples[family] += 1

        adapted = dict(scored)
        adapted["family"] = family
        adapted_results.append(adapted)

    missing = EXPECTED_FAMILIES - set(family_examples)

    if missing:
        raise ValueError(
            f"missing capability families: {sorted(missing)}"
        )

    if total_tokens <= 0:
        raise ValueError("no response tokens")

    aggregate_loss = total_loss_sum / total_tokens

    per_family: dict[str, Any] = {}

    for family in sorted(EXPECTED_FAMILIES):
        tokens = family_tokens[family]

        if tokens <= 0:
            raise ValueError(
                f"family has no response tokens: {family}"
            )

        per_family[family] = {
            "examples": family_examples[family],
            "responseTokens": tokens,
            "responseLoss":
                family_loss_sum[family] / tokens,
            "exactMatches": family_exact[family],
        }

    return {
        "checkpoint": raw_result.get("checkpoint"),
        "checkpointSha256":
            raw_result.get("checkpointSha256"),
        "modelName": raw_result.get("modelName"),
        "dataset": raw_result.get("dataset"),
        "datasetSha256":
            raw_result.get("datasetSha256"),
        "examples": len(results),
        "responseTokens": total_tokens,
        "aggregateResponseLoss": aggregate_loss,
        "exactMatches": exact_matches,
        "exactMatchRate":
            exact_matches / len(results)
            if results else 0.0,
        "perFamily": per_family,
        "results": adapted_results,
    }
