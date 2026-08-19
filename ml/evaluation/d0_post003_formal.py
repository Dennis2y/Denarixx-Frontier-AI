from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch


EXPECTED_BASELINE_SHA256 = (
    "31038f7801ae64f99aad4ec88e7aaa276917be9dec84ef0944b121578a36ca97"
)

EXPECTED_CANDIDATE_SHA256 = (
    "3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06"
)

EXPECTED_FORMAL_DATA_SHA256 = (
    "28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115"
)

EXPECTED_FAMILIES = {
    "echo",
    "binary",
    "transform",
    "qa",
    "semantic",
}

EXPECTED_EXAMPLES = 25
EXPECTED_PER_FAMILY = 5

EXPECTED_VOCAB_SIZE = 42
EXPECTED_CONTEXT_LENGTH = 32
EXPECTED_HIDDEN_SIZE = 64
EXPECTED_LAYERS = 2
EXPECTED_ATTENTION_HEADS = 4
EXPECTED_DROPOUT = 0.0
EXPECTED_PARAMETER_COUNT = 102784


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()

    with Path(path).open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def require_sha256(
    path: str | Path,
    expected: str,
) -> None:
    actual = sha256_file(path)

    if actual != expected:
        raise RuntimeError(
            f"SHA-256 mismatch for {path}: "
            f"expected {expected}, got {actual}"
        )


def load_dataset(path: str | Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    with Path(path).open("r", encoding="utf-8") as f:
        for line_number, raw in enumerate(f, start=1):
            line = raw.strip()

            if not line:
                continue

            item = json.loads(line)

            family = item.get("family")
            instruction = item.get("instruction")
            response = item.get("response")

            if not isinstance(family, str):
                raise ValueError(
                    f"Invalid family on line {line_number}"
                )

            if not isinstance(instruction, str):
                raise ValueError(
                    f"Invalid instruction on line {line_number}"
                )

            if not isinstance(response, str):
                raise ValueError(
                    f"Invalid response on line {line_number}"
                )

            rows.append(
                {
                    "family": family,
                    "instruction": instruction,
                    "response": response,
                }
            )

    return rows


def validate_dataset_structure(
    rows: list[dict[str, str]],
) -> None:
    if len(rows) != EXPECTED_EXAMPLES:
        raise ValueError(
            f"Expected {EXPECTED_EXAMPLES} formal examples, "
            f"got {len(rows)}"
        )

    counts: dict[str, int] = defaultdict(int)
    instructions: set[str] = set()

    for row in rows:
        family = row["family"]

        if family not in EXPECTED_FAMILIES:
            raise ValueError(
                f"Unexpected capability family: {family}"
            )

        counts[family] += 1

        normalized_instruction = (
            " ".join(row["instruction"].strip().lower().split())
        )

        if normalized_instruction in instructions:
            raise ValueError(
                "Duplicate normalized formal instruction: "
                f"{normalized_instruction}"
            )

        instructions.add(normalized_instruction)

    if set(counts) != EXPECTED_FAMILIES:
        raise ValueError(
            f"Formal families mismatch: {dict(counts)}"
        )

    for family in EXPECTED_FAMILIES:
        if counts[family] != EXPECTED_PER_FAMILY:
            raise ValueError(
                f"{family} expected {EXPECTED_PER_FAMILY} examples, "
                f"got {counts[family]}"
            )


def compare_results(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    baseline_loss = float(baseline["aggregateResponseLoss"])
    candidate_loss = float(candidate["aggregateResponseLoss"])

    baseline_exact = int(baseline["exactMatches"])
    candidate_exact = int(candidate["exactMatches"])

    baseline_family = baseline["perFamily"]
    candidate_family = candidate["perFamily"]

    family_results: dict[str, dict[str, Any]] = {}
    no_worse_count = 0

    for family in sorted(EXPECTED_FAMILIES):
        base_loss = float(
            baseline_family[family]["responseLoss"]
        )
        cand_loss = float(
            candidate_family[family]["responseLoss"]
        )

        no_worse = cand_loss <= base_loss

        if no_worse:
            no_worse_count += 1

        family_results[family] = {
            "baselineResponseLoss": base_loss,
            "candidateResponseLoss": cand_loss,
            "candidateNoWorse": no_worse,
        }

    aggregate_improved = candidate_loss < baseline_loss
    exact_not_worse = candidate_exact >= baseline_exact
    family_requirement = no_worse_count >= 4

    passed = (
        aggregate_improved
        and exact_not_worse
        and family_requirement
    )

    return {
        "aggregateResponseLossImproved": aggregate_improved,
        "exactMatchNotWorse": exact_not_worse,
        "familiesNoWorse": no_worse_count,
        "familyRequirementPassed": family_requirement,
        "perFamilyComparison": family_results,
        "formalPass": passed,
    }


def _extract_model_state(
    checkpoint: dict[str, Any],
) -> dict[str, torch.Tensor]:
    for key in (
        "modelStateDict",
        "model_state_dict",
        "model",
        "state_dict",
    ):
        value = checkpoint.get(key)

        if isinstance(value, dict):
            return value

    raise RuntimeError(
        "Could not locate model state dictionary in checkpoint"
    )


def _extract_config(
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    for key in (
        "modelConfig",
        "model_config",
        "config",
        "architecture",
    ):
        value = checkpoint.get(key)

        if isinstance(value, dict):
            return value

    raise RuntimeError(
        "Could not locate model configuration in checkpoint"
    )


def _get_config_value(
    config: dict[str, Any],
    *keys: str,
) -> Any:
    for key in keys:
        if key in config:
            return config[key]

    raise RuntimeError(
        f"Missing required model config value: {keys}"
    )


def verify_checkpoint_invariants(
    checkpoint: dict[str, Any],
) -> dict[str, Any]:
    state = _extract_model_state(checkpoint)
    config = _extract_config(checkpoint)

    parameter_count = sum(
        int(tensor.numel())
        for tensor in state.values()
        if torch.is_tensor(tensor)
    )

    if parameter_count != EXPECTED_PARAMETER_COUNT:
        raise RuntimeError(
            f"Parameter count changed: {parameter_count}"
        )

    vocab_size = int(
        _get_config_value(
            config,
            "vocabSize",
            "vocab_size",
        )
    )

    context_length = int(
        _get_config_value(
            config,
            "contextLength",
            "context_length",
            "block_size",
        )
    )

    hidden_size = int(
        _get_config_value(
            config,
            "hiddenSize",
            "hidden_size",
            "n_embd",
        )
    )

    layers = int(
        _get_config_value(
            config,
            "layers",
            "numLayers",
            "num_layers",
            "n_layer",
        )
    )

    heads = int(
        _get_config_value(
            config,
            "attentionHeads",
            "attention_heads",
            "numHeads",
            "num_heads",
            "n_head",
        )
    )

    dropout = float(
        _get_config_value(
            config,
            "dropout",
        )
    )

    expected = {
        "vocabSize": EXPECTED_VOCAB_SIZE,
        "contextLength": EXPECTED_CONTEXT_LENGTH,
        "hiddenSize": EXPECTED_HIDDEN_SIZE,
        "layers": EXPECTED_LAYERS,
        "attentionHeads": EXPECTED_ATTENTION_HEADS,
        "dropout": EXPECTED_DROPOUT,
        "parameterCount": EXPECTED_PARAMETER_COUNT,
    }

    actual = {
        "vocabSize": vocab_size,
        "contextLength": context_length,
        "hiddenSize": hidden_size,
        "layers": layers,
        "attentionHeads": heads,
        "dropout": dropout,
        "parameterCount": parameter_count,
    }

    if actual != expected:
        raise RuntimeError(
            f"Architecture invariant mismatch: {actual}"
        )

    return actual


def load_checkpoint_read_only(
    path: str | Path,
) -> dict[str, Any]:
    checkpoint = torch.load(
        path,
        map_location="cpu",
        weights_only=False,
    )

    if not isinstance(checkpoint, dict):
        raise RuntimeError(
            "Checkpoint must deserialize to a dictionary"
        )

    return checkpoint


def assert_model_identity_invariants(
    baseline_checkpoint: dict[str, Any],
    candidate_checkpoint: dict[str, Any],
) -> dict[str, Any]:
    baseline = verify_checkpoint_invariants(
        baseline_checkpoint
    )
    candidate = verify_checkpoint_invariants(
        candidate_checkpoint
    )

    if baseline != candidate:
        raise RuntimeError(
            "Baseline/candidate architecture mismatch"
        )

    return candidate


def evaluate_checkpoint(
    checkpoint_path: str | Path,
    dataset_path: str | Path,
) -> dict[str, Any]:
    """
    Formal scoring implementation intentionally delegates to the
    already-validated POST-003 development evaluator machinery.

    This function is not exercised against the frozen formal dataset
    during implementation tests.

    Import is delayed so synthetic tests cannot accidentally trigger
    formal evaluation merely by importing this module.
    """

    from ml.evaluation import d0_post003_dev as dev_eval

    if hasattr(dev_eval, "evaluate_checkpoint"):
        return dev_eval.evaluate_checkpoint(
            checkpoint_path,
            dataset_path,
        )

    raise RuntimeError(
        "Validated development evaluator does not expose "
        "evaluate_checkpoint(). Inspect its public API before "
        "formal scoring. Do not improvise scoring behavior."
    )


def run_formal_evaluation(
    baseline_path: str | Path,
    candidate_path: str | Path,
    dataset_path: str | Path,
) -> dict[str, Any]:
    require_sha256(
        baseline_path,
        EXPECTED_BASELINE_SHA256,
    )

    require_sha256(
        candidate_path,
        EXPECTED_CANDIDATE_SHA256,
    )

    require_sha256(
        dataset_path,
        EXPECTED_FORMAL_DATA_SHA256,
    )

    rows = load_dataset(dataset_path)
    validate_dataset_structure(rows)

    baseline_checkpoint = load_checkpoint_read_only(
        baseline_path
    )

    candidate_checkpoint = load_checkpoint_read_only(
        candidate_path
    )

    architecture = assert_model_identity_invariants(
        baseline_checkpoint,
        candidate_checkpoint,
    )

    baseline_result = evaluate_checkpoint(
        baseline_path,
        dataset_path,
    )

    candidate_result = evaluate_checkpoint(
        candidate_path,
        dataset_path,
    )

    comparison = compare_results(
        baseline_result,
        candidate_result,
    )

    return {
        "stage": "D0-POST-003-formal",
        "datasetSha256": sha256_file(dataset_path),
        "baselineSha256": sha256_file(baseline_path),
        "candidateSha256": sha256_file(candidate_path),
        "architecture": architecture,
        "baseline": baseline_result,
        "candidate": candidate_result,
        "comparison": comparison,
    }


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

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    result = run_formal_evaluation(
        baseline_path=args.baseline,
        candidate_path=args.candidate,
        dataset_path=args.dataset,
    )

    output_path = Path(args.output)

    if output_path.exists():
        raise RuntimeError(
            f"Refusing to overwrite existing result: {output_path}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "complete",
                "formalPass": result[
                    "comparison"
                ]["formalPass"],
                "output": str(output_path),
            }
        )
    )


if __name__ == "__main__":
    main()
