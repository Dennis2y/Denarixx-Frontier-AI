from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

import torch
from torch import nn

from models.d0 import D0Model
from post_training.sft_data import (
    IGNORE_INDEX,
    InstructionExample,
    encode_instruction,
    format_instruction,
)
from tokenizers.char import CharacterTokenizer


EXPECTED_FAMILIES = frozenset(
    {
        "basic_instruction_following",
        "constrained_generation",
        "literal_response",
        "short_completion",
        "simple_transformation",
    }
)


@dataclass(frozen=True)
class D04ExampleResult:
    index: int
    family: str
    instruction: str
    expected_response: str
    generated_response: str
    response_loss: float
    response_tokens: int
    exact_match: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class D04FamilyResult:
    family: str
    examples: int
    response_tokens: int
    response_loss: float
    response_perplexity: float
    exact_matches: int

    @property
    def exact_match_rate(self) -> float:
        return self.exact_matches / self.examples

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["exact_match_rate"] = self.exact_match_rate
        return payload


@dataclass(frozen=True)
class D04EvaluationResult:
    examples_evaluated: int
    response_tokens_evaluated: int
    response_loss: float
    response_perplexity: float
    exact_matches: int
    per_family: dict[str, D04FamilyResult]
    results: list[D04ExampleResult]

    @property
    def exact_match_rate(self) -> float:
        return self.exact_matches / self.examples_evaluated

    def to_dict(self) -> dict[str, Any]:
        return {
            "examplesEvaluated": self.examples_evaluated,
            "responseTokensEvaluated": (
                self.response_tokens_evaluated
            ),
            "responseLoss": self.response_loss,
            "responsePerplexity": self.response_perplexity,
            "exactMatches": self.exact_matches,
            "exactMatchRate": self.exact_match_rate,
            "perFamily": {
                family: result.to_dict()
                for family, result in self.per_family.items()
            },
            "results": [
                result.to_dict()
                for result in self.results
            ],
        }


def safe_perplexity(loss: float) -> float:
    try:
        return math.exp(loss)
    except OverflowError:
        return math.inf


def validate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    if not rows:
        raise ValueError(
            "D0.4 evaluation requires examples"
        )

    families: set[str] = set()

    for index, row in enumerate(rows, start=1):
        for field in (
            "instruction",
            "response",
            "family",
        ):
            if field not in row:
                raise ValueError(
                    f"row {index} missing field: {field}"
                )

        instruction = row["instruction"]
        response = row["response"]
        family = row["family"]

        if not isinstance(instruction, str):
            raise TypeError(
                f"row {index} instruction must be str"
            )

        if not isinstance(response, str):
            raise TypeError(
                f"row {index} response must be str"
            )

        if not isinstance(family, str):
            raise TypeError(
                f"row {index} family must be str"
            )

        if not instruction:
            raise ValueError(
                f"row {index} instruction is empty"
            )

        if not response:
            raise ValueError(
                f"row {index} response is empty"
            )

        if family not in EXPECTED_FAMILIES:
            raise ValueError(
                f"row {index} unexpected family: {family}"
            )

        families.add(family)

    missing = EXPECTED_FAMILIES - families

    if missing:
        raise ValueError(
            "D0.4 dataset missing capability families: "
            + ", ".join(sorted(missing))
        )


def response_loss_for_example(
    model: D0Model,
    tokenizer: CharacterTokenizer,
    example: InstructionExample,
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

    device = next(model.parameters()).device

    inputs = inputs.to(device)
    targets = targets.to(device)

    with torch.inference_mode():
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
            "D0.4 example contains no supervised "
            "response tokens"
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
    example: InstructionExample,
) -> str:
    prompt, response = format_instruction(
        example
    )

    prompt_ids = tokenizer.encode(prompt)

    if len(prompt_ids) >= model.config.context_length:
        raise ValueError(
            "D0.4 prompt leaves no generation capacity"
        )

    response_ids = tokenizer.encode(response)

    if not response_ids:
        raise ValueError(
            "D0.4 response contains no tokens"
        )

    context = torch.tensor(
        [prompt_ids],
        dtype=torch.long,
        device=next(model.parameters()).device,
    )

    generated_ids: list[int] = []

    was_training = model.training
    model.eval()

    try:
        with torch.inference_mode():
            for _ in range(len(response_ids)):
                model_input = context[
                    :,
                    -model.config.context_length:
                ]

                logits, _ = model(model_input)

                next_token = torch.argmax(
                    logits[:, -1, :],
                    dim=-1,
                    keepdim=True,
                )

                generated_ids.append(
                    int(next_token.item())
                )

                context = torch.cat(
                    (context, next_token),
                    dim=1,
                )
    finally:
        if was_training:
            model.train()

    return tokenizer.decode(generated_ids)


def evaluate_rows(
    *,
    model: D0Model,
    tokenizer: CharacterTokenizer,
    rows: Sequence[Mapping[str, Any]],
) -> D04EvaluationResult:
    validate_rows(rows)

    was_training = model.training
    model.eval()

    total_loss_sum = 0.0
    total_tokens = 0
    exact_matches = 0

    family_loss_sum: dict[str, float] = defaultdict(
        float
    )
    family_tokens: dict[str, int] = defaultdict(int)
    family_examples: dict[str, int] = defaultdict(int)
    family_exact: dict[str, int] = defaultdict(int)

    results: list[D04ExampleResult] = []

    try:
        for index, row in enumerate(rows, start=1):
            family = str(row["family"])

            example = InstructionExample(
                instruction=str(row["instruction"]),
                response=str(row["response"]),
            )

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

            expected = example.response

            exact = generated == expected

            mean_loss = loss_sum / token_count

            total_loss_sum += loss_sum
            total_tokens += token_count
            exact_matches += int(exact)

            family_loss_sum[family] += loss_sum
            family_tokens[family] += token_count
            family_examples[family] += 1
            family_exact[family] += int(exact)

            results.append(
                D04ExampleResult(
                    index=index,
                    family=family,
                    instruction=example.instruction,
                    expected_response=expected,
                    generated_response=generated,
                    response_loss=mean_loss,
                    response_tokens=token_count,
                    exact_match=exact,
                )
            )
    finally:
        if was_training:
            model.train()

    if total_tokens < 1:
        raise RuntimeError(
            "D0.4 evaluation produced no response tokens"
        )

    aggregate_loss = (
        total_loss_sum / total_tokens
    )

    per_family: dict[str, D04FamilyResult] = {}

    for family in sorted(EXPECTED_FAMILIES):
        tokens = family_tokens[family]
        examples = family_examples[family]

        if tokens < 1 or examples < 1:
            raise RuntimeError(
                f"family {family} has no scored examples"
            )

        family_loss = (
            family_loss_sum[family] / tokens
        )

        per_family[family] = D04FamilyResult(
            family=family,
            examples=examples,
            response_tokens=tokens,
            response_loss=family_loss,
            response_perplexity=safe_perplexity(
                family_loss
            ),
            exact_matches=family_exact[family],
        )

    return D04EvaluationResult(
        examples_evaluated=len(rows),
        response_tokens_evaluated=total_tokens,
        response_loss=aggregate_loss,
        response_perplexity=safe_perplexity(
            aggregate_loss
        ),
        exact_matches=exact_matches,
        per_family=per_family,
        results=results,
    )
