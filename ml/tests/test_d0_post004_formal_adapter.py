from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER_PATH = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post004_formal_adapter.py"
)

spec = importlib.util.spec_from_file_location(
    "d0_post004_formal_adapter",
    ADAPTER_PATH,
)

assert spec is not None
assert spec.loader is not None

adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

adapt_scoring_result = adapter.adapt_scoring_result


FAMILIES = [
    "echo",
    "binary",
    "transform",
    "qa",
    "semantic",
]


def build_fixture():
    rows = []
    results = []

    index = 0

    for family_number, family in enumerate(
        FAMILIES,
        start=1,
    ):
        for example_number in range(2):
            index += 1

            rows.append(
                {
                    "family": family,
                    "instruction":
                        f"{family} instruction {example_number}",
                    "response": "true",
                }
            )

            tokens = example_number + 1
            loss = float(family_number)

            results.append(
                {
                    "index": index,
                    "family": None,
                    "instruction":
                        f"{family} instruction {example_number}",
                    "expected": "true",
                    "generated":
                        "true" if example_number == 0 else "false",
                    "exactMatch":
                        example_number == 0,
                    "responseLoss": loss,
                    "responseTokens": tokens,
                }
            )

    raw = {
        "checkpoint": "synthetic.pt",
        "checkpointSha256": "synthetic",
        "modelName": "synthetic",
        "dataset": "synthetic.jsonl",
        "datasetSha256": "synthetic",
        "examples": len(results),
        "responseTokens":
            sum(r["responseTokens"] for r in results),
        "responseLoss": 0.0,
        "exactMatches": 5,
        "results": results,
    }

    return raw, rows


def test_schema_conversion():
    raw, rows = build_fixture()

    result = adapt_scoring_result(raw, rows)

    assert "aggregateResponseLoss" in result
    assert "perFamily" in result
    assert result["exactMatches"] == 5
    assert set(result["perFamily"]) == set(FAMILIES)


def test_family_labels_come_from_dataset():
    raw, rows = build_fixture()

    result = adapt_scoring_result(raw, rows)

    for scored, row in zip(
        result["results"],
        rows,
    ):
        assert scored["family"] == row["family"]


def test_token_weighted_aggregate():
    raw, rows = build_fixture()

    result = adapt_scoring_result(raw, rows)

    expected_sum = sum(
        r["responseLoss"] * r["responseTokens"]
        for r in raw["results"]
    )

    expected_tokens = sum(
        r["responseTokens"]
        for r in raw["results"]
    )

    expected = expected_sum / expected_tokens

    assert abs(
        result["aggregateResponseLoss"] - expected
    ) < 1e-12


def test_family_loss_is_token_weighted():
    raw, rows = build_fixture()

    result = adapt_scoring_result(raw, rows)

    for family_number, family in enumerate(
        FAMILIES,
        start=1,
    ):
        assert abs(
            result["perFamily"][family]["responseLoss"]
            - float(family_number)
        ) < 1e-12


def test_family_exact_counts():
    raw, rows = build_fixture()

    result = adapt_scoring_result(raw, rows)

    for family in FAMILIES:
        assert (
            result["perFamily"][family]["exactMatches"]
            == 1
        )


def test_missing_family_rejected():
    raw, rows = build_fixture()

    rows = [
        row
        for row in rows
        if row["family"] != "semantic"
    ]

    raw = dict(raw)
    raw["results"] = raw["results"][:len(rows)]

    try:
        adapt_scoring_result(raw, rows)
    except ValueError:
        return

    raise AssertionError(
        "Expected missing family rejection"
    )


def test_length_mismatch_rejected():
    raw, rows = build_fixture()

    try:
        adapt_scoring_result(
            raw,
            rows[:-1],
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected result/dataset mismatch rejection"
    )


def test_zero_tokens_rejected():
    raw, rows = build_fixture()

    raw["results"][0]["responseTokens"] = 0

    try:
        adapt_scoring_result(raw, rows)
    except ValueError:
        return

    raise AssertionError(
        "Expected zero-token rejection"
    )


def test_adapter_contains_no_model_scoring():
    import inspect

    source = inspect.getsource(adapter)

    forbidden = (
        "D0Model(",
        "torch.load(",
        "evaluate_checkpoint(",
        "greedy_generate(",
        "response_loss_for_example(",
    )

    for token in forbidden:
        assert token not in source


if __name__ == "__main__":
    tests = [
        test_schema_conversion,
        test_family_labels_come_from_dataset,
        test_token_weighted_aggregate,
        test_family_loss_is_token_weighted,
        test_family_exact_counts,
        test_missing_family_rejected,
        test_length_mismatch_rejected,
        test_zero_tokens_rejected,
        test_adapter_contains_no_model_scoring,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All POST-004 formal adapter synthetic tests passed."
    )
