"""
Denarixx D1 locked decoder-only causal transformer.

Authoritative architecture:
    research/d1/d1_architecture_contract.json

Authoritative semantic freeze:
    research/d1/d1_model_semantic_freeze.json

D1 is initialized from scratch.

No D0 parameters, D0 tokenizer state, pretrained third-party model
weights, or pretrained third-party tokenizer artifacts are inherited.
"""

from dataclasses import asdict, dataclass

import torch
from torch import nn
from torch.nn import functional as F


LOCKED_PARAMETER_COUNT = 26_655_104


@dataclass(frozen=True)
class D1Config:
    vocab_size: int = 8192
    context_length: int = 2048
    hidden_size: int = 448
    layers: int = 8
    attention_heads: int = 7
    head_dimension: int = 64
    ffn_hidden_size: int = 1792
    position_encoding: str = "rope"
    causal: bool = True

    def __post_init__(self) -> None:
        expected = {
            "vocab_size": 8192,
            "context_length": 2048,
            "hidden_size": 448,
            "layers": 8,
            "attention_heads": 7,
            "head_dimension": 64,
            "ffn_hidden_size": 1792,
            "position_encoding": "rope",
            "causal": True,
        }

        actual = asdict(self)

        for key, expected_value in expected.items():
            actual_value = actual[key]

            if actual_value != expected_value:
                raise ValueError(
                    "D1 architecture is locked: "
                    f"{key} must be {expected_value!r}, "
                    f"got {actual_value!r}"
                )

        if self.hidden_size != (
            self.attention_heads * self.head_dimension
        ):
            raise ValueError(
                "D1 hidden_size must equal "
                "attention_heads * head_dimension"
            )

        if self.ffn_hidden_size != self.hidden_size * 4:
            raise ValueError(
                "D1 FFN hidden size must be exactly 4x hidden size"
            )

        if self.head_dimension % 2 != 0:
            raise ValueError(
                "D1 RoPE requires an even head dimension"
            )


class D1RotaryEmbedding(nn.Module):
    """Rotary positional embedding applied to query and key only."""

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


class D1CausalSelfAttention(nn.Module):
    """Biased Q/K/V/O causal multi-head self-attention."""

    def __init__(self, config: D1Config) -> None:
        super().__init__()

        self.heads = config.attention_heads
        self.head_dim = config.head_dimension
        self.hidden_size = config.hidden_size

        self.query = nn.Linear(
            config.hidden_size,
            config.hidden_size,
            bias=True,
        )

        self.key = nn.Linear(
            config.hidden_size,
            config.hidden_size,
            bias=True,
        )

        self.value = nn.Linear(
            config.hidden_size,
            config.hidden_size,
            bias=True,
        )

        self.output = nn.Linear(
            config.hidden_size,
            config.hidden_size,
            bias=True,
        )

        self.rotary_embedding = D1RotaryEmbedding(
            head_dim=config.head_dimension,
            context_length=config.context_length,
        )

        mask = torch.tril(
            torch.ones(
                config.context_length,
                config.context_length,
                dtype=torch.bool,
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
            persistent=False,
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

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        batch, sequence, channels = x.shape

        if channels != self.hidden_size:
            raise ValueError(
                "D1 attention input hidden dimension mismatch"
            )

        q, k, v = self.project_qkv(x)

        q = self.rotary_embedding(q)
        k = self.rotary_embedding(k)

        scores = torch.matmul(
            q,
            k.transpose(-2, -1),
        ) / (self.head_dim ** 0.5)

        scores = scores.masked_fill(
            ~self.causal_mask[
                :,
                :,
                :sequence,
                :sequence,
            ],
            float("-inf"),
        )

        weights = torch.softmax(
            scores,
            dim=-1,
        )

        attended = torch.matmul(
            weights,
            v,
        )

        attended = (
            attended
            .transpose(1, 2)
            .contiguous()
            .view(
                batch,
                sequence,
                channels,
            )
        )

        return self.output(attended)


class D1FeedForward(nn.Module):
    """Locked dense 448 -> 1792 -> 448 GELU feed-forward network."""

    def __init__(self, config: D1Config) -> None:
        super().__init__()

        self.up = nn.Linear(
            config.hidden_size,
            config.ffn_hidden_size,
            bias=True,
        )

        self.down = nn.Linear(
            config.ffn_hidden_size,
            config.hidden_size,
            bias=True,
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        return self.down(
            F.gelu(
                self.up(x)
            )
        )


class D1TransformerBlock(nn.Module):
    """Pre-norm residual D1 transformer block."""

    def __init__(self, config: D1Config) -> None:
        super().__init__()

        self.attention_norm = nn.LayerNorm(
            config.hidden_size,
            elementwise_affine=True,
            bias=True,
        )

        self.attention = D1CausalSelfAttention(config)

        self.feed_forward_norm = nn.LayerNorm(
            config.hidden_size,
            elementwise_affine=True,
            bias=True,
        )

        self.feed_forward = D1FeedForward(config)

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:
        x = x + self.attention(
            self.attention_norm(x)
        )

        x = x + self.feed_forward(
            self.feed_forward_norm(x)
        )

        return x


class D1Model(nn.Module):
    """
    Denarixx D1 decoder-only causal language model.

    Locked architecture:
        vocab:          8192
        context:        2048
        hidden:         448
        layers:         8
        heads:          7
        head dimension: 64
        FFN:            1792
        position:       RoPE
        LM-head tying:  false
        parameters:     26,655,104
    """

    def __init__(
        self,
        config: D1Config | None = None,
    ) -> None:
        super().__init__()

        self.config = config or D1Config()

        self.token_embedding = nn.Embedding(
            self.config.vocab_size,
            self.config.hidden_size,
        )

        self.blocks = nn.ModuleList(
            [
                D1TransformerBlock(self.config)
                for _ in range(self.config.layers)
            ]
        )

        self.final_norm = nn.LayerNorm(
            self.config.hidden_size,
            elementwise_affine=True,
            bias=True,
        )

        self.lm_head = nn.Linear(
            self.config.hidden_size,
            self.config.vocab_size,
            bias=False,
        )

        self._verify_locked_parameter_count()

    def parameter_count(self) -> int:
        return sum(
            parameter.numel()
            for parameter in self.parameters()
        )

    def _verify_locked_parameter_count(self) -> None:
        actual = self.parameter_count()

        if actual != LOCKED_PARAMETER_COUNT:
            raise RuntimeError(
                "D1 parameter-count contract violation: "
                f"expected {LOCKED_PARAMETER_COUNT}, got {actual}"
            )

    def forward(
        self,
        token_ids: torch.Tensor,
    ) -> torch.Tensor:
        if token_ids.ndim != 2:
            raise ValueError(
                "D1 token_ids must have shape [batch, sequence]"
            )

        sequence = token_ids.size(1)

        if sequence < 1:
            raise ValueError(
                "D1 requires sequence length >= 1"
            )

        if sequence > self.config.context_length:
            raise ValueError(
                "D1 sequence exceeds locked context length "
                f"{self.config.context_length}"
            )

        x = self.token_embedding(token_ids)

        for block in self.blocks:
            x = block(x)

        x = self.final_norm(x)

        return self.lm_head(x)


def build_d1_model() -> D1Model:
    """Construct a fresh locked D1 model with no inherited weights."""

    return D1Model(D1Config())
