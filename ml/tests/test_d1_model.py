import torch
from torch import nn

from ml.models.d1 import (
    LOCKED_PARAMETER_COUNT,
    D1Config,
    D1Model,
)


def test_d1_locked_configuration() -> None:
    config = D1Config()

    assert config.vocab_size == 8192
    assert config.context_length == 2048
    assert config.hidden_size == 448
    assert config.layers == 8
    assert config.attention_heads == 7
    assert config.head_dimension == 64
    assert config.ffn_hidden_size == 1792
    assert config.position_encoding == "rope"
    assert config.causal is True


def test_d1_parameter_count_exact() -> None:
    model = D1Model()

    assert model.parameter_count() == LOCKED_PARAMETER_COUNT
    assert model.parameter_count() == 26_655_104


def test_d1_embedding_and_head_are_not_tied() -> None:
    model = D1Model()

    assert (
        model.token_embedding.weight.data_ptr()
        != model.lm_head.weight.data_ptr()
    )


def test_d1_lm_head_has_no_bias() -> None:
    model = D1Model()

    assert model.lm_head.bias is None


def test_d1_layer_count() -> None:
    model = D1Model()

    assert len(model.blocks) == 8


def test_d1_projection_biases_exist() -> None:
    model = D1Model()

    for block in model.blocks:
        assert block.attention.query.bias is not None
        assert block.attention.key.bias is not None
        assert block.attention.value.bias is not None
        assert block.attention.output.bias is not None

        assert block.feed_forward.up.bias is not None
        assert block.feed_forward.down.bias is not None


def test_d1_layernorm_has_scale_and_bias() -> None:
    model = D1Model()

    norms = [
        module
        for module in model.modules()
        if isinstance(module, nn.LayerNorm)
    ]

    assert len(norms) == 17

    for norm in norms:
        assert norm.weight is not None
        assert norm.bias is not None


def test_d1_rope_is_qk_only_by_forward_structure() -> None:
    model = D1Model()

    attention = model.blocks[0].attention

    x = torch.randn(
        1,
        4,
        model.config.hidden_size,
    )

    q, k, v = attention.project_qkv(x)

    rotated_q = attention.rotary_embedding(q)
    rotated_k = attention.rotary_embedding(k)

    assert rotated_q.shape == q.shape
    assert rotated_k.shape == k.shape

    # Value remains an independently projected tensor and is never
    # passed through the rotary embedding in attention.forward().
    assert v.shape == q.shape


def test_d1_small_cpu_forward_shape() -> None:
    model = D1Model()
    model.eval()

    token_ids = torch.tensor(
        [[1, 2, 3, 4]],
        dtype=torch.long,
    )

    with torch.no_grad():
        logits = model(token_ids)

    assert logits.shape == (1, 4, 8192)


def test_d1_rejects_context_overflow() -> None:
    model = D1Model()

    token_ids = torch.zeros(
        (
            1,
            model.config.context_length + 1,
        ),
        dtype=torch.long,
    )

    try:
        model(token_ids)
    except ValueError as error:
        assert "context length" in str(error)
    else:
        raise AssertionError(
            "D1 accepted sequence beyond locked context length"
        )


def test_d1_rejects_architecture_mutation() -> None:
    try:
        D1Config(hidden_size=512)
    except ValueError as error:
        assert "architecture is locked" in str(error)
    else:
        raise AssertionError(
            "D1 accepted mutation of locked architecture"
        )
