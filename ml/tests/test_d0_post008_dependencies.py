from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation import d0_post008_dependencies as deps


class FakeCheckpoint:
    pass


class FakeTokenizer:
    pass


class FakeModel:
    pass


def test_load_rows_valid_synthetic_fixture(
    tmp_path: Path,
):
    dataset = tmp_path / "synthetic.jsonl"

    rows = [
        {
            "family": "alpha",
            "instruction": "Synthetic instruction A",
            "response": "Synthetic response A",
        },
        {
            "family": "beta",
            "instruction": "Synthetic instruction B",
            "response": "Synthetic response B",
        },
    ]

    dataset.write_text(
        "\n".join(
            json.dumps(row)
            for row in rows
        )
        + "\n",
        encoding="utf-8",
    )

    loaded = deps.load_rows(dataset)

    assert loaded == rows


def test_load_rows_rejects_extra_field(
    tmp_path: Path,
):
    dataset = tmp_path / "synthetic.jsonl"

    dataset.write_text(
        json.dumps(
            {
                "family": "alpha",
                "instruction": "A",
                "response": "B",
                "unexpected": "forbidden",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        deps.load_rows(dataset)


def test_validate_rows_rejects_empty_rows():
    with pytest.raises(
        ValueError,
        match="contains no rows",
    ):
        deps.validate_rows([])


def test_validate_rows_rejects_blank_values():
    rows = [
        {
            "family": "alpha",
            "instruction": "",
            "response": "response",
        }
    ]

    with pytest.raises(
        ValueError,
        match="invalid instruction",
    ):
        deps.validate_rows(rows)


def test_normalize_response_is_deterministic():
    assert (
        deps.normalize_response("  hello  ")
        == "hello"
    )

    assert (
        deps.normalize_response("\nhello\n")
        == "hello"
    )


def test_score_checkpoint_uses_in_memory_rows(
    tmp_path: Path,
    monkeypatch,
):
    checkpoint = (
        tmp_path / "synthetic-checkpoint.pt"
    )

    checkpoint.write_bytes(
        b"synthetic checkpoint stand-in"
    )

    rows = [
        {
            "family": "alpha",
            "instruction": "Instruction A",
            "response": "Expected A",
        },
        {
            "family": "beta",
            "instruction": "Instruction B",
            "response": "Expected B",
        },
    ]

    calls = {
        "load_model": 0,
        "loss": 0,
        "generate": 0,
        "sha256": 0,
    }

    def fake_load_model(path):
        calls["load_model"] += 1

        assert Path(path) == checkpoint

        return (
            FakeModel(),
            FakeTokenizer(),
            {
                "model_name":
                    "synthetic-model",
            },
        )

    def fake_loss(
        model,
        tokenizer,
        example,
    ):
        calls["loss"] += 1

        if example.instruction == "Instruction A":
            return 2.0, 2

        if example.instruction == "Instruction B":
            return 3.0, 3

        raise AssertionError(
            "unexpected synthetic example"
        )

    def fake_generate(
        model,
        tokenizer,
        example,
    ):
        calls["generate"] += 1

        if example.instruction == "Instruction A":
            return "Expected A"

        return "Different B"

    def fake_sha256(path):
        calls["sha256"] += 1
        assert Path(path) == checkpoint
        return "a" * 64

    monkeypatch.setattr(
        deps.dev_eval,
        "load_model",
        fake_load_model,
    )

    monkeypatch.setattr(
        deps.dev_eval,
        "response_loss_for_example",
        fake_loss,
    )

    monkeypatch.setattr(
        deps.dev_eval,
        "greedy_generate",
        fake_generate,
    )

    monkeypatch.setattr(
        deps.dev_eval,
        "sha256_file",
        fake_sha256,
    )

    result = deps.score_checkpoint(
        checkpoint,
        rows,
    )

    assert calls == {
        "load_model": 1,
        "loss": 2,
        "generate": 2,
        "sha256": 1,
    }

    assert result["stage"] == "D0-POST-008"

    assert (
        result["checkpointSha256"]
        == "a" * 64
    )

    assert (
        result["modelName"]
        == "synthetic-model"
    )

    assert result["examples"] == 2
    assert result["responseTokens"] == 5

    assert (
        result["aggregateResponseLoss"]
        == pytest.approx(1.0)
    )

    assert result["exactMatches"] == 1

    assert (
        result["exactMatchRate"]
        == pytest.approx(0.5)
    )

    assert result["families"] == [
        "alpha",
        "beta",
    ]

    assert (
        result["perFamily"]["alpha"][
            "responseLoss"
        ]
        == pytest.approx(1.0)
    )

    assert (
        result["perFamily"]["beta"][
            "responseLoss"
        ]
        == pytest.approx(1.0)
    )


def synthetic_result(
    *,
    checkpoint_sha: str,
    loss: float,
    exact: int,
):
    return {
        "stage": "D0-POST-008",
        "checkpoint": "synthetic.pt",
        "checkpointSha256":
            checkpoint_sha,
        "examples": 2,
        "responseTokens": 4,
        "aggregateResponseLoss":
            loss,
        "exactMatches":
            exact,
        "exactMatchRate":
            exact / 2,
        "families": [
            "alpha",
            "beta",
        ],
        "perFamily": {
            "alpha": {
                "examples": 1,
                "responseTokens": 2,
                "responseLoss": 1.0,
                "exactMatches": 1,
            },
            "beta": {
                "examples": 1,
                "responseTokens": 2,
                "responseLoss": 2.0,
                "exactMatches": 0,
            },
        },
        "results": [],
    }


def test_compare_results_is_policy_neutral():
    baseline = synthetic_result(
        checkpoint_sha="b" * 64,
        loss=2.0,
        exact=1,
    )

    candidate = synthetic_result(
        checkpoint_sha="c" * 64,
        loss=1.5,
        exact=2,
    )

    result = deps.compare_results(
        baseline,
        candidate,
    )

    assert result["stage"] == "D0-POST-008"

    assert (
        result["status"]
        == "comparison-complete-"
        "adjudication-not-frozen"
    )

    assert result["formalPass"] is None

    assert (
        result[
            "aggregateResponseLossDelta"
        ]
        == pytest.approx(-0.5)
    )

    assert result["exactMatchDelta"] == 1


def test_compare_results_rejects_family_mismatch():
    baseline = synthetic_result(
        checkpoint_sha="b" * 64,
        loss=2.0,
        exact=1,
    )

    candidate = synthetic_result(
        checkpoint_sha="c" * 64,
        loss=1.5,
        exact=2,
    )

    candidate["families"] = [
        "alpha",
    ]

    candidate["perFamily"] = {
        "alpha":
            candidate["perFamily"]["alpha"]
    }

    with pytest.raises(
        ValueError,
        match="family sets differ",
    ):
        deps.compare_results(
            baseline,
            candidate,
        )


def test_validate_scoring_result_rejects_wrong_stage():
    result = synthetic_result(
        checkpoint_sha="b" * 64,
        loss=2.0,
        exact=1,
    )

    result["stage"] = "WRONG-STAGE"

    with pytest.raises(
        ValueError,
        match="wrong stage",
    ):
        deps._validate_scoring_result(
            result,
            "synthetic",
        )
