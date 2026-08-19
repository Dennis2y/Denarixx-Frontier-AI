"""D0-POST-004 development candidate selector.

This evaluator is intentionally development-only.

It evaluates exactly the three predeclared POST-004
candidate checkpoints against the frozen POST-004
development dataset.

It MUST NOT load or reference the protected formal
dataset.

Selection policy:

1. Candidate must have at least one exact match.
2. Higher exact-match count wins.
3. Higher exact-match family coverage wins.
4. Lower aggregate response loss wins.
5. Earlier candidate step wins.

Development selection does NOT constitute formal
acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import torch
from torch import nn

from models.d0 import D0Config, D0Model
from post_training.sft_data import (
    IGNORE_INDEX,
    encode_instruction,
    format_instruction,
    load_instruction_jsonl,
)
from tokenizers.char import CharacterTokenizer


EXPECTED_PARAMETER_COUNT = 102784

EXPECTED_CANDIDATES = {
    40: (
        "7525f75bc85c455251d59a54483a433dd5f093b42"
        "a0927c890a565afacdfdee5"
    ),
    80: (
        "64c2229162f18bb86d66c5f0bd390fc7c1bf8ec61"
        "fc82bdc77bc1547f313109b"
    ),
    120: (
        "ae927ca3e779a0eda7c8fff025fc7cfd3a41568cb"
        "236148f444c75507ef35441"
    ),
}

EXPECTED_DEV_SHA256 = (
    "d54abaa83a4bbdcca313c557431fa5005e4490b710"
    "3f0f997ccd0c619f5c8a58"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def parameter_count(model: nn.Module) -> int:
    return sum(
        parameter.numel()
        for parameter in model.parameters()
    )


def load_model(
    checkpoint_path: Path,
    expected_step: int,
) -> tuple[D0Model, CharacterTokenizer, dict]:

    actual_sha = sha256_file(checkpoint_path)
    expected_sha = EXPECTED_CANDIDATES[expected_step]

    if actual_sha != expected_sha:
        raise ValueError(
            "POST-004 candidate identity mismatch "
            f"for step {expected_step}"
        )

    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    candidate_step = checkpoint.get(
        "candidate_step",
        checkpoint.get("candidateStep"),
    )

    if candidate_step is None:
        training = checkpoint.get("training", {})
        candidate_step = training.get("candidateStep")

    if candidate_step != expected_step:
        raise ValueError(
            "candidate-step metadata mismatch"
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

    model.eval()

    if parameter_count(model) != EXPECTED_PARAMETER_COUNT:
        raise ValueError(
            "unexpected D0 parameter count"
        )

    return model, tokenizer, checkpoint


def response_loss_for_example(
    model: D0Model,
    tokenizer: CharacterTokenizer,
    example,
) -> tuple[float, int]:

    encoded = encode_instruction(
        tokenizer=tokenizer,
        example=example,
        context_length=model.config.context_length,
    )

    inputs = torch.tensor(
        [encoded.input_ids],
        dtype=torch.long,
    )

    targets = torch.tensor(
        [encoded.target_ids],
        dtype=torch.long,
    )

    with torch.no_grad():
        logits, _ = model(inputs)

    flat_logits = logits.reshape(
        -1,
        logits.size(-1),
    )

    flat_targets = targets.reshape(-1)

    mask = flat_targets.ne(IGNORE_INDEX)

    token_count = int(mask.sum().item())

    if token_count < 1:
        raise ValueError(
            "development example has no supervised tokens"
        )

    loss_sum = nn.functional.cross_entropy(
        flat_logits[mask],
        flat_targets[mask],
        reduction="sum",
    )

    return float(loss_sum.item()), token_count


def greedy_generate(
    model: D0Model,
    tokenizer: CharacterTokenizer,
    example,
) -> str:

    prompt, _ = format_instruction(example)

    ids = tokenizer.encode(prompt)

    if len(ids) >= model.config.context_length:
        raise ValueError(
            "prompt leaves no generation capacity"
        )

    generated: list[int] = []

    with torch.no_grad():

        while (
            len(ids) + len(generated)
            < model.config.context_length
        ):

            sequence = ids + generated

            inputs = torch.tensor(
                [sequence],
                dtype=torch.long,
            )

            logits, _ = model(inputs)

            next_id = int(
                torch.argmax(
                    logits[0, -1],
                    dim=-1,
                ).item()
            )

            generated.append(next_id)

            token = tokenizer.decode([next_id])

            if token == "\n":
                break

    text = tokenizer.decode(generated)

    if text.endswith("\n"):
        text = text[:-1]

    return text


def family_for_example(example) -> str:

    family = getattr(example, "family", None)

    if family:
        return str(family)

    raw = getattr(example, "raw", None)

    if isinstance(raw, dict):
        value = raw.get("family")

        if value:
            return str(value)

    return "unknown"


def evaluate_checkpoint(
    checkpoint_path: Path,
    candidate_step: int,
    dataset_path: Path,
) -> dict:

    model, tokenizer, checkpoint = load_model(
        checkpoint_path,
        candidate_step,
    )

    examples = load_instruction_jsonl(
        dataset_path
    )

    total_loss = 0.0
    total_tokens = 0
    exact_matches = 0

    exact_families: set[str] = set()

    results = []

    for index, example in enumerate(
        examples,
        start=1,
    ):

        loss_sum, token_count = (
            response_loss_for_example(
                model,
                tokenizer,
                example,
            )
        )

        generated = greedy_generate(
            model,
            tokenizer,
            example,
        )

        exact = generated == example.response

        family = family_for_example(example)

        total_loss += loss_sum
        total_tokens += token_count

        if exact:
            exact_matches += 1
            exact_families.add(family)

        results.append(
            {
                "index": index,
                "family": family,
                "instruction": example.instruction,
                "expected": example.response,
                "generated": generated,
                "exactMatch": exact,
                "responseLoss": (
                    loss_sum / token_count
                ),
                "responseTokens": token_count,
            }
        )

    if total_tokens < 1:
        raise ValueError(
            "development dataset has no response tokens"
        )

    average_loss = total_loss / total_tokens

    return {
        "candidateStep": candidate_step,
        "checkpoint": str(checkpoint_path),
        "checkpointSha256": sha256_file(
            checkpoint_path
        ),
        "modelName": checkpoint.get("model_name"),
        "dataset": str(dataset_path),
        "datasetSha256": sha256_file(
            dataset_path
        ),
        "examples": len(examples),
        "responseTokens": total_tokens,
        "aggregateResponseLoss": average_loss,
        "responsePerplexity": math.exp(
            average_loss
        ),
        "exactMatchCount": exact_matches,
        "exactMatchRate": (
            exact_matches / len(examples)
        ),
        "exactMatchFamilies": sorted(
            exact_families
        ),
        "familyCoverage": len(
            exact_families
        ),
        "results": results,
    }


def selection_key(result: dict) -> tuple:

    return (
        -result["exactMatchCount"],
        -result["familyCoverage"],
        result["aggregateResponseLoss"],
        result["candidateStep"],
    )


def select_candidate(
    results: list[dict],
) -> dict:

    eligible = [
        result
        for result in results
        if result["exactMatchCount"] > 0
    ]

    if not eligible:
        return {
            "developmentSelectionPass": False,
            "selectedCandidate": None,
            "reason": (
                "No candidate achieved non-zero exact "
                "generation on the development set."
            ),
        }

    ranked = sorted(
        eligible,
        key=selection_key,
    )

    selected = ranked[0]

    return {
        "developmentSelectionPass": True,
        "selectedCandidate": {
            "candidateStep": (
                selected["candidateStep"]
            ),
            "checkpoint": selected["checkpoint"],
            "checkpointSha256": (
                selected["checkpointSha256"]
            ),
            "exactMatchCount": (
                selected["exactMatchCount"]
            ),
            "familyCoverage": (
                selected["familyCoverage"]
            ),
            "aggregateResponseLoss": (
                selected["aggregateResponseLoss"]
            ),
        },
        "reason": (
            "Selected by frozen POST-004 development "
            "policy."
        ),
    }


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--step40",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--step80",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--step120",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    dataset_sha = sha256_file(args.dataset)

    if dataset_sha != EXPECTED_DEV_SHA256:
        raise ValueError(
            "POST-004 development dataset identity mismatch"
        )

    candidates = [
        (40, args.step40),
        (80, args.step80),
        (120, args.step120),
    ]

    results = []

    for step, path in candidates:
        results.append(
            evaluate_checkpoint(
                checkpoint_path=path,
                candidate_step=step,
                dataset_path=args.dataset,
            )
        )

    decision = select_candidate(results)

    payload = {
        "status": "complete",
        "stage": "D0-POST-004-development",
        "policy": {
            "primaryMetric": "exactMatchCount",
            "secondaryMetric": (
                "aggregateResponseLoss"
            ),
            "tertiaryMetric": "familyCoverage",
            "minimumCondition": (
                "non-zero exact generation"
            ),
            "implementedRanking": [
                "higher exactMatchCount",
                "higher familyCoverage",
                "lower aggregateResponseLoss",
                "earlier candidateStep",
            ],
        },
        "candidates": results,
        "decision": decision,
        "formalEvaluationAuthorized": False,
    }

    print(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
