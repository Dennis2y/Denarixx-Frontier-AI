"""Canonical checkpoint inference utilities for Denarixx D0.

D0-INF-001 validates inference mechanics for accepted pretrained and
post-trained checkpoints.

This module does not claim production or frontier-model capability.
"""

from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import torch

from models.d0 import D0Config, D0Model
from tokenizers.char import CharacterTokenizer


@dataclass(frozen=True)
class LoadedD0Checkpoint:
    path: Path
    checkpoint: dict
    config: D0Config
    tokenizer: CharacterTokenizer
    model: D0Model


@dataclass(frozen=True)
class InferenceResult:
    status: str
    checkpoint: str
    model_name: str
    post_training_stage: str | None
    prompt: str
    prompt_tokens: int
    prompt_tokens_used: int
    prompt_truncated: bool
    generated_text: str
    output: str
    generated_token_ids: list[int]
    tokens_generated: int
    max_tokens_requested: int
    decoding: str
    latency_ms: float
    generation_latency_ms: float
    tokens_per_second: float
    context_length: int
    parameter_count: int

    def to_dict(self) -> dict:
        payload = asdict(self)

        # Preserve existing API-style camelCase fields.
        return {
            "status": payload["status"],
            "checkpoint": payload["checkpoint"],
            "modelName": payload["model_name"],
            "postTrainingStage": payload["post_training_stage"],
            "prompt": payload["prompt"],
            "promptTokens": payload["prompt_tokens"],
            "promptTokensUsed": payload["prompt_tokens_used"],
            "promptTruncated": payload["prompt_truncated"],
            "generatedText": payload["generated_text"],
            "output": payload["output"],
            "generatedTokenIds": payload["generated_token_ids"],
            "tokensGenerated": payload["tokens_generated"],
            "maxTokensRequested": payload["max_tokens_requested"],
            "decoding": payload["decoding"],
            "latencyMs": payload["latency_ms"],
            "generationLatencyMs": payload["generation_latency_ms"],
            "tokensPerSecond": payload["tokens_per_second"],
            "contextLength": payload["context_length"],
            "parameterCount": payload["parameter_count"],
        }


def parameter_count(model: torch.nn.Module) -> int:
    return sum(
        parameter.numel()
        for parameter in model.parameters()
    )


def validate_prompt_coverage(
    tokenizer: CharacterTokenizer,
    prompt: str,
) -> None:
    if not prompt:
        raise ValueError(
            "prompt must not be empty"
        )

    alphabet = set(tokenizer.alphabet)

    missing = sorted(
        set(prompt).difference(alphabet)
    )

    if missing:
        rendered = "".join(missing)

        raise ValueError(
            "prompt contains characters absent from "
            f"checkpoint tokenizer: {rendered!r}"
        )


def load_checkpoint(
    checkpoint_path: Path,
) -> LoadedD0Checkpoint:
    path = checkpoint_path.resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"checkpoint not found: {path}"
        )

    checkpoint = torch.load(
        path,
        map_location="cpu",
        weights_only=False,
    )

    required = {
        "model_config",
        "model_state_dict",
        "tokenizer",
    }

    missing = sorted(
        required.difference(checkpoint)
    )

    if missing:
        raise ValueError(
            "checkpoint missing required fields: "
            + ", ".join(missing)
        )

    config = D0Config(
        **checkpoint["model_config"]
    )

    tokenizer = CharacterTokenizer.from_dict(
        checkpoint["tokenizer"]
    )

    if tokenizer.vocab_size != config.vocab_size:
        raise ValueError(
            "checkpoint tokenizer vocabulary does not "
            "match model vocab_size"
        )

    model = D0Model(config)

    model.load_state_dict(
        checkpoint["model_state_dict"],
        strict=True,
    )

    model.eval()

    actual_parameters = parameter_count(model)

    stored_counts = checkpoint.get(
        "parameter_counts"
    )

    if stored_counts is not None:
        expected_parameters = stored_counts.get(
            "totalParameters"
        )

        if (
            expected_parameters is not None
            and expected_parameters
            != actual_parameters
        ):
            raise ValueError(
                "checkpoint parameter count does not "
                "match reconstructed model"
            )

    return LoadedD0Checkpoint(
        path=path,
        checkpoint=checkpoint,
        config=config,
        tokenizer=tokenizer,
        model=model,
    )


def run_greedy_inference(
    checkpoint_path: Path,
    prompt: str,
    max_tokens: int = 24,
) -> InferenceResult:
    if max_tokens < 1:
        raise ValueError(
            "max_tokens must be >= 1"
        )

    total_started = time.perf_counter()

    loaded = load_checkpoint(
        checkpoint_path
    )

    validate_prompt_coverage(
        loaded.tokenizer,
        prompt,
    )

    prompt_ids = loaded.tokenizer.encode(
        prompt
    )

    context_ids = prompt_ids[
        -loaded.config.context_length :
    ]

    prompt_truncated = (
        len(prompt_ids)
        > loaded.config.context_length
    )

    context = torch.tensor(
        [context_ids],
        dtype=torch.long,
    )

    generated_ids: list[int] = []

    generation_started = time.perf_counter()

    with torch.inference_mode():
        for _ in range(max_tokens):
            model_input = context[
                :,
                -loaded.config.context_length :
            ]

            logits, _ = loaded.model(
                model_input
            )

            next_token = torch.argmax(
                logits[:, -1, :],
                dim=-1,
                keepdim=True,
            )

            token_id = int(
                next_token.item()
            )

            generated_ids.append(
                token_id
            )

            context = torch.cat(
                (
                    context,
                    next_token,
                ),
                dim=1,
            )

    generation_latency_ms = (
        time.perf_counter()
        - generation_started
    ) * 1000.0

    latency_ms = (
        time.perf_counter()
        - total_started
    ) * 1000.0

    generated_text = (
        loaded.tokenizer.decode(
            generated_ids
        )
    )

    output = (
        prompt
        + generated_text
    )

    tokens_per_second = (
        len(generated_ids)
        / max(
            generation_latency_ms / 1000.0,
            1e-9,
        )
    )

    if not math.isfinite(
        tokens_per_second
    ):
        raise RuntimeError(
            "non-finite inference throughput"
        )

    checkpoint_payload = (
        loaded.checkpoint
    )

    return InferenceResult(
        status="complete",
        checkpoint=str(
            loaded.path
        ),
        model_name=str(
            checkpoint_payload.get(
                "model_name",
                "denarixx-d0",
            )
        ),
        post_training_stage=(
            checkpoint_payload.get(
                "post_training_stage"
            )
        ),
        prompt=prompt,
        prompt_tokens=len(
            prompt_ids
        ),
        prompt_tokens_used=len(
            context_ids
        ),
        prompt_truncated=prompt_truncated,
        generated_text=generated_text,
        output=output,
        generated_token_ids=generated_ids,
        tokens_generated=len(
            generated_ids
        ),
        max_tokens_requested=max_tokens,
        decoding="greedy",
        latency_ms=latency_ms,
        generation_latency_ms=(
            generation_latency_ms
        ),
        tokens_per_second=(
            tokens_per_second
        ),
        context_length=(
            loaded.config.context_length
        ),
        parameter_count=parameter_count(
            loaded.model
        ),
    )
