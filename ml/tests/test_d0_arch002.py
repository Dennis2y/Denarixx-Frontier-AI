"""Focused verification for D0-ARCH-002."""

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
ML = ROOT / "ml"

if str(ML) not in sys.path:
    sys.path.insert(0, str(ML))

from models.d0 import (  # noqa: E402
    CausalSelfAttention,
    D0Config,
    D0Model,
)


def make_config(
    *,
    position_encoding: str = "absolute",
    normalization: str = "layernorm",
) -> D0Config:
    return D0Config(
        vocab_size=41,
        context_length=32,
        hidden_size=64,
        layers=2,
        attention_heads=4,
        dropout=0.0,
        normalization=normalization,
        position_encoding=position_encoding,
    )


def parameter_count(
    model: torch.nn.Module,
) -> int:
    return sum(
        parameter.numel()
        for parameter in model.parameters()
    )


def test_construction_and_shapes() -> None:
    tokens = torch.randint(
        0,
        41,
        (2, 12),
    )

    absolute = D0Model(
        make_config(
            position_encoding="absolute"
        )
    )

    rope = D0Model(
        make_config(
            position_encoding="rope"
        )
    )

    absolute_logits, _ = absolute(tokens)
    rope_logits, _ = rope(tokens)

    assert absolute_logits.shape == (
        2,
        12,
        41,
    )

    assert rope_logits.shape == (
        absolute_logits.shape
    )


def test_invalid_position_encoding() -> None:
    try:
        D0Model(
            make_config(
                position_encoding="invalid"
            )
        )
    except ValueError:
        return

    raise AssertionError(
        "invalid position encoding was accepted"
    )


def test_rope_qk_shapes_and_v_unchanged() -> None:
    config = make_config(
        position_encoding="rope"
    )

    attention = CausalSelfAttention(config)

    x = torch.randn(
        2,
        9,
        config.hidden_size,
    )

    q, k, v = attention.project_qkv(x)

    q_before = q.clone()
    k_before = k.clone()
    v_before = v.clone()

    q_after, k_after, v_after = (
        attention.apply_position_encoding(
            q,
            k,
            v,
        )
    )

    assert q_after.shape == q_before.shape
    assert k_after.shape == k_before.shape
    assert v_after.shape == v_before.shape

    assert torch.equal(
        v_after,
        v_before,
    )

    assert not torch.equal(
        q_after,
        q_before,
    )

    assert not torch.equal(
        k_after,
        k_before,
    )


def test_position_parameter_difference() -> None:
    torch.manual_seed(42)

    absolute = D0Model(
        make_config(
            position_encoding="absolute"
        )
    )

    torch.manual_seed(42)

    rope = D0Model(
        make_config(
            position_encoding="rope"
        )
    )

    difference = (
        parameter_count(absolute)
        - parameter_count(rope)
    )

    expected = (
        absolute.config.context_length
        * absolute.config.hidden_size
    )

    assert difference == expected

    assert absolute.position_embedding is not None
    assert rope.position_embedding is None


def model_output_for_seed(
    seed: int,
    position_encoding: str,
) -> torch.Tensor:
    torch.manual_seed(seed)

    model = D0Model(
        make_config(
            position_encoding=position_encoding
        )
    )

    tokens = torch.tensor(
        [
            [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
            ]
        ]
    )

    logits, _ = model(tokens)

    return logits.detach().clone()


def test_determinism() -> None:
    for mode in ("absolute", "rope"):
        first = model_output_for_seed(
            1234,
            mode,
        )

        second = model_output_for_seed(
            1234,
            mode,
        )

        assert torch.equal(
            first,
            second,
        )


def test_normalization_compatibility() -> None:
    tokens = torch.randint(
        0,
        41,
        (1, 8),
    )

    for normalization in (
        "layernorm",
        "rmsnorm",
    ):
        for position_encoding in (
            "absolute",
            "rope",
        ):
            model = D0Model(
                make_config(
                    position_encoding=position_encoding,
                    normalization=normalization,
                )
            )

            logits, _ = model(tokens)

            assert logits.shape == (
                1,
                8,
                41,
            )


def test_rope_dimension_validation() -> None:
    config = D0Config(
        vocab_size=41,
        context_length=32,
        hidden_size=60,
        layers=2,
        attention_heads=4,
        position_encoding="rope",
    )

    try:
        D0Model(config)
    except ValueError as error:
        assert "even" in str(error).lower()
        return

    raise AssertionError(
        "odd RoPE head dimension was accepted"
    )


def test_promoted_default_is_rope() -> None:
    config = D0Config(
        vocab_size=41,
    )

    assert config.position_encoding == "rope"

    model = D0Model(config)

    assert model.position_embedding is None



def main() -> None:
    tests = [
        test_construction_and_shapes,
        test_invalid_position_encoding,
        test_rope_qk_shapes_and_v_unchanged,
        test_position_parameter_difference,
        test_determinism,
        test_normalization_compatibility,
        test_rope_dimension_validation,
        test_promoted_default_is_rope,
    ]

    for test in tests:
        test()
        print(f"✓ {test.__name__}")

    print()
    print(
        "All D0-ARCH-002 focused tests passed."
    )


if __name__ == "__main__":
    main()
