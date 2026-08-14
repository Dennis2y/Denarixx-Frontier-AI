"""Denarixx D0: a small, configurable causal language model."""

from dataclasses import asdict, dataclass

import torch
from torch import nn


@dataclass(frozen=True)
class D0Config:
    vocab_size: int
    context_length: int = 32
    hidden_size: int = 64
    layers: int = 2
    attention_heads: int = 4
    dropout: float = 0.0
    normalization: str = "layernorm"
    position_encoding: str = "rope"


class RotaryEmbedding(nn.Module):
    """Standard rotary positional embeddings for attention Q/K."""

    def __init__(
        self,
        head_dim: int,
        context_length: int,
        base: float = 10000.0,
    ) -> None:
        super().__init__()

        if head_dim % 2 != 0:
            raise ValueError(
                "RoPE requires an even attention head dimension"
            )

        if context_length < 1:
            raise ValueError(
                "RoPE requires context_length >= 1"
            )

        inverse_frequency = 1.0 / (
            base
            ** (
                torch.arange(
                    0,
                    head_dim,
                    2,
                    dtype=torch.float32,
                )
                / head_dim
            )
        )

        positions = torch.arange(
            context_length,
            dtype=torch.float32,
        )

        frequencies = torch.outer(
            positions,
            inverse_frequency,
        )

        self.register_buffer(
            "cos_cached",
            frequencies.cos(),
            persistent=False,
        )

        self.register_buffer(
            "sin_cached",
            frequencies.sin(),
            persistent=False,
        )

    def forward(
        self,
        tensor: torch.Tensor,
    ) -> torch.Tensor:
        sequence = tensor.size(-2)

        if sequence > self.cos_cached.size(0):
            raise ValueError(
                "RoPE sequence exceeds configured context_length"
            )

        cos = self.cos_cached[:sequence].to(
            device=tensor.device,
            dtype=tensor.dtype,
        )[None, None, :, :]

        sin = self.sin_cached[:sequence].to(
            device=tensor.device,
            dtype=tensor.dtype,
        )[None, None, :, :]

        even = tensor[..., 0::2]
        odd = tensor[..., 1::2]

        rotated_even = even * cos - odd * sin
        rotated_odd = even * sin + odd * cos

        return torch.stack(
            (rotated_even, rotated_odd),
            dim=-1,
        ).flatten(-2)


class CausalSelfAttention(nn.Module):
    def __init__(self, config: D0Config) -> None:
        super().__init__()

        self.query = nn.Linear(
            config.hidden_size,
            config.hidden_size,
        )
        self.key = nn.Linear(
            config.hidden_size,
            config.hidden_size,
        )
        self.value = nn.Linear(
            config.hidden_size,
            config.hidden_size,
        )
        self.output = nn.Linear(
            config.hidden_size,
            config.hidden_size,
        )
        self.dropout = nn.Dropout(config.dropout)

        self.heads = config.attention_heads
        self.head_dim = (
            config.hidden_size
            // config.attention_heads
        )

        self.position_encoding = config.position_encoding

        if self.position_encoding == "rope":
            self.rotary_embedding = RotaryEmbedding(
                head_dim=self.head_dim,
                context_length=config.context_length,
            )
        else:
            self.rotary_embedding = None

        mask = torch.tril(
            torch.ones(
                config.context_length,
                config.context_length,
            )
        )

        self.register_buffer(
            "causal_mask",
            mask.view(
                1,
                1,
                config.context_length,
                config.context_length,
            ),
        )

    def project_qkv(
        self,
        x: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
    ]:
        batch, sequence, _ = x.shape

        q = (
            self.query(x)
            .view(
                batch,
                sequence,
                self.heads,
                self.head_dim,
            )
            .transpose(1, 2)
        )

        k = (
            self.key(x)
            .view(
                batch,
                sequence,
                self.heads,
                self.head_dim,
            )
            .transpose(1, 2)
        )

        v = (
            self.value(x)
            .view(
                batch,
                sequence,
                self.heads,
                self.head_dim,
            )
            .transpose(1, 2)
        )

        return q, k, v

    def apply_position_encoding(
        self,
        q: torch.Tensor,
        k: torch.Tensor,
        v: torch.Tensor,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
    ]:
        if self.position_encoding == "rope":
            if self.rotary_embedding is None:
                raise RuntimeError(
                    "RoPE selected without rotary embedding"
                )

            q = self.rotary_embedding(q)
            k = self.rotary_embedding(k)

        return q, k, v

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        batch, sequence, channels = x.shape

        q, k, v = self.project_qkv(x)

        q, k, v = self.apply_position_encoding(
            q,
            k,
            v,
        )

        scores = (
            q @ k.transpose(-2, -1)
        ) / (self.head_dim**0.5)

        scores = scores.masked_fill(
            self.causal_mask[
                :,
                :,
                :sequence,
                :sequence,
            ]
            == 0,
            float("-inf"),
        )

        weights = torch.softmax(
            scores,
            dim=-1,
        )

        weights = self.dropout(weights)

        attended = (
            (weights @ v)
            .transpose(1, 2)
            .contiguous()
            .view(
                batch,
                sequence,
                channels,
            )
        )

        return self.output(attended)


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization.

    This implementation intentionally contains only a learned scale.
    It does not subtract the mean and does not use a learned bias.
    """

    def __init__(
        self,
        hidden_size: int,
        eps: float = 1e-6,
    ) -> None:
        super().__init__()

        self.weight = nn.Parameter(
            torch.ones(hidden_size)
        )
        self.eps = eps

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        input_dtype = x.dtype

        value = x.float()

        variance = value.pow(2).mean(
            dim=-1,
            keepdim=True,
        )

        normalized = value * torch.rsqrt(
            variance + self.eps
        )

        return (
            normalized.to(input_dtype)
            * self.weight
        )


def build_normalization(
    config: D0Config,
) -> nn.Module:
    if config.normalization == "layernorm":
        return nn.LayerNorm(
            config.hidden_size
        )

    if config.normalization == "rmsnorm":
        return RMSNorm(
            config.hidden_size
        )

    raise ValueError(
        "normalization must be "
        "'layernorm' or 'rmsnorm', "
        f"got {config.normalization!r}"
    )


class TransformerBlock(nn.Module):
    def __init__(
        self,
        config: D0Config,
    ) -> None:
        super().__init__()

        self.normalization_one = build_normalization(
            config
        )

        self.attention = CausalSelfAttention(
            config
        )

        self.normalization_two = build_normalization(
            config
        )

        self.feed_forward = nn.Sequential(
            nn.Linear(
                config.hidden_size,
                config.hidden_size * 4,
            ),
            nn.GELU(),
            nn.Linear(
                config.hidden_size * 4,
                config.hidden_size,
            ),
            nn.Dropout(config.dropout),
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        x = x + self.attention(
            self.normalization_one(x)
        )

        return x + self.feed_forward(
            self.normalization_two(x)
        )


class D0Model(nn.Module):
    def __init__(
        self,
        config: D0Config,
    ) -> None:
        super().__init__()

        if (
            config.hidden_size
            % config.attention_heads
            != 0
        ):
            raise ValueError(
                "hidden_size must be divisible by attention_heads"
            )

        if config.position_encoding not in {
            "absolute",
            "rope",
        }:
            raise ValueError(
                "position_encoding must be "
                "'absolute' or 'rope', "
                f"got {config.position_encoding!r}"
            )

        head_dim = (
            config.hidden_size
            // config.attention_heads
        )

        if (
            config.position_encoding == "rope"
            and head_dim % 2 != 0
        ):
            raise ValueError(
                "RoPE requires an even attention head dimension"
            )

        self.config = config

        self.token_embedding = nn.Embedding(
            config.vocab_size,
            config.hidden_size,
        )

        if config.position_encoding == "absolute":
            self.position_embedding = nn.Embedding(
                config.context_length,
                config.hidden_size,
            )
        else:
            self.position_embedding = None

        self.blocks = nn.ModuleList(
            [
                TransformerBlock(config)
                for _ in range(config.layers)
            ]
        )

        self.normalization = build_normalization(
            config
        )

        self.output_projection = nn.Linear(
            config.hidden_size,
            config.vocab_size,
            bias=False,
        )

        self.output_projection.weight = (
            self.token_embedding.weight
        )

        self.apply(self._initialize_weights)

    @staticmethod
    def _initialize_weights(
        module: nn.Module,
    ) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=0.02,
            )

            if module.bias is not None:
                nn.init.zeros_(module.bias)

        elif isinstance(module, nn.Embedding):
            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=0.02,
            )

    def forward(
        self,
        tokens: torch.Tensor,
        targets: torch.Tensor | None = None,
    ) -> tuple[
        torch.Tensor,
        torch.Tensor | None,
    ]:
        _, sequence = tokens.shape

        if sequence > self.config.context_length:
            raise ValueError(
                "sequence exceeds D0 context_length"
            )

        hidden = self.token_embedding(tokens)

        if self.config.position_encoding == "absolute":
            if self.position_embedding is None:
                raise RuntimeError(
                    "absolute position encoding selected "
                    "without position embedding"
                )

            positions = torch.arange(
                sequence,
                device=tokens.device,
            )

            hidden = (
                hidden
                + self.position_embedding(positions)
            )

        for block in self.blocks:
            hidden = block(hidden)

        logits = self.output_projection(
            self.normalization(hidden)
        )

        loss = None

        if targets is not None:
            loss = nn.functional.cross_entropy(
                logits.reshape(
                    -1,
                    logits.size(-1),
                ),
                targets.reshape(-1),
            )

        return logits, loss

    def config_dict(
        self,
    ) -> dict[str, int | float | str]:
        return asdict(self.config)
