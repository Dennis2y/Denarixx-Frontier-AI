"""Read-only D0-POST-003 development evaluator."""

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
) -> tuple[D0Model, CharacterTokenizer, dict]:
    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
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

    return (
        float(loss_sum.item()),
        token_count,
    )


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


def evaluate_checkpoint(
    checkpoint_path: Path,
    dataset_path: Path,
) -> dict:
    model, tokenizer, checkpoint = load_model(
        checkpoint_path
    )

    examples = load_instruction_jsonl(
        dataset_path
    )

    total_loss = 0.0
    total_tokens = 0
    exact_matches = 0
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

        total_loss += loss_sum
        total_tokens += token_count
        exact_matches += int(exact)

        family = None

        # POST-003 frozen dev ordering:
        # echo, binary, transform, qa, semantic.
        frozen_families = [
            "echo",
            "binary",
            "transform",
            "qa",
            "semantic",
        ]

        if len(examples) == 5:
            family = frozen_families[index - 1]

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

    average_loss = total_loss / total_tokens

    return {
        "checkpoint": str(checkpoint_path),
        "checkpointSha256": sha256_file(
            checkpoint_path
        ),
        "modelName": checkpoint.get(
            "model_name"
        ),
        "dataset": str(dataset_path),
        "datasetSha256": sha256_file(
            dataset_path
        ),
        "examples": len(examples),
        "responseTokens": total_tokens,
        "responseLoss": average_loss,
        "responsePerplexity": math.exp(
            average_loss
        ),
        "exactMatches": exact_matches,
        "exactMatchRate": (
            exact_matches / len(examples)
        ),
        "results": results,
    }


def compare(
    baseline: dict,
    candidate: dict,
) -> dict:
    loss_pass = (
        candidate["responseLoss"]
        < baseline["responseLoss"]
    )

    exact_pass = (
        candidate["exactMatches"]
        >= baseline["exactMatches"]
    )

    return {
        "responseLossImproved": loss_pass,
        "exactMatchNotWorse": exact_pass,
        "developmentPass": (
            loss_pass and exact_pass
        ),
        "responseLossDelta": (
            candidate["responseLoss"]
            - baseline["responseLoss"]
        ),
        "exactMatchDelta": (
            candidate["exactMatches"]
            - baseline["exactMatches"]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--candidate",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    baseline = evaluate_checkpoint(
        args.baseline,
        args.dataset,
    )

    candidate = evaluate_checkpoint(
        args.candidate,
        args.dataset,
    )

    payload = {
        "status": "complete",
        "baseline": baseline,
        "candidate": candidate,
        "decision": compare(
            baseline,
            candidate,
        ),
    }

    print(
        json.dumps(
            payload,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
