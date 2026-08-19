from __future__ import annotations

from copy import deepcopy

import pytest

from evaluation import d0_post008_compatibility as compat


class SyntheticTokenizer:
    """
    Development-safe character tokenizer stand-in.

    It deliberately implements only the interface needed by the
    frozen SFT formatting/encoding path.
    """

    def __init__(self) -> None:
        chars = (
            "\n"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
            " .,?!:;'-_/()"
        )

        self.alphabet = chars

        self._to_id = {
            ch: index + 1
            for index, ch in enumerate(chars)
        }

    def encode(self, text: str) -> list[int]:
        result = []

        for ch in text:
            if ch not in self._to_id:
                raise ValueError(
                    f"unsupported character: {ch!r}"
                )

            result.append(self._to_id[ch])

        return result


def synthetic_rows():
    rows = []

    for family in compat.EXPECTED_FAMILIES:
        for index in range(
            compat.EXPECTED_ROWS_PER_FAMILY
        ):
            rows.append(
                {
                    "family": family,
                    "instruction":
                        f"{family} synthetic instruction {index}",
                    "response":
                        f"synthetic response {family} {index}",
                }
            )

    return rows


def test_valid_structure_passes():
    compat.validate_structure(
        synthetic_rows()
    )


def test_requires_exactly_40_rows():
    rows = synthetic_rows()[:-1]

    with pytest.raises(
        compat.CompatibilityError,
        match="exactly 40",
    ):
        compat.validate_structure(rows)


def test_requires_exact_family_allocation():
    rows = synthetic_rows()

    rows[-1] = {
        **rows[-1],
        "family": "echo",
    }

    with pytest.raises(
        compat.CompatibilityError,
    ):
        compat.validate_structure(rows)


def test_unknown_family_rejected():
    rows = synthetic_rows()

    rows[0] = {
        **rows[0],
        "family": "unknown",
    }

    with pytest.raises(
        compat.CompatibilityError,
        match="unknown family",
    ):
        compat.validate_structure(rows)


def test_extra_field_rejected():
    rows = synthetic_rows()

    rows[0] = {
        **rows[0],
        "extra": "forbidden",
    }

    with pytest.raises(
        compat.CompatibilityError,
        match="exactly family, instruction, response",
    ):
        compat.validate_structure(rows)


def test_blank_instruction_rejected():
    rows = synthetic_rows()

    rows[0] = {
        **rows[0],
        "instruction": "   ",
    }

    with pytest.raises(
        compat.CompatibilityError,
        match="invalid instruction",
    ):
        compat.validate_structure(rows)


def test_blank_response_rejected():
    rows = synthetic_rows()

    rows[0] = {
        **rows[0],
        "response": "",
    }

    with pytest.raises(
        compat.CompatibilityError,
        match="invalid response",
    ):
        compat.validate_structure(rows)


def test_duplicate_instruction_rejected():
    rows = synthetic_rows()

    rows[1] = {
        **rows[1],
        "instruction": rows[0]["instruction"],
    }

    with pytest.raises(
        compat.CompatibilityError,
        match="duplicate instruction",
    ):
        compat.validate_structure(rows)


def test_valid_encoding_passes():
    tokenizer = SyntheticTokenizer()

    result = compat.validate_row_encoding(
        row=synthetic_rows()[0],
        tokenizer=tokenizer,
        context_length=512,
    )

    assert result["inputTokens"] > 0
    assert result["supervisedResponseTokens"] > 0


def test_unsupported_character_rejected():
    tokenizer = SyntheticTokenizer()

    row = synthetic_rows()[0].copy()
    row["instruction"] += " €"

    with pytest.raises(
        compat.CompatibilityError,
        match="not tokenizer/context compatible",
    ):
        compat.validate_row_encoding(
            row=row,
            tokenizer=tokenizer,
            context_length=512,
        )


def test_too_small_context_rejected():
    tokenizer = SyntheticTokenizer()

    with pytest.raises(
        compat.CompatibilityError,
        match="not tokenizer/context compatible",
    ):
        compat.validate_row_encoding(
            row=synthetic_rows()[0],
            tokenizer=tokenizer,
            context_length=8,
        )


def test_full_synthetic_dataset_compatible():
    tokenizer = SyntheticTokenizer()

    result = compat.validate_compatibility(
        rows=synthetic_rows(),
        tokenizer=tokenizer,
        context_length=512,
    )

    assert result["stage"] == "D0-POST-008"
    assert result["status"] == "compatible"
    assert result["examples"] == 40
    assert result["rowsPerFamily"] == 8
    assert len(result["rows"]) == 40


def test_validation_does_not_modify_rows():
    tokenizer = SyntheticTokenizer()

    rows = synthetic_rows()
    original = deepcopy(rows)

    compat.validate_compatibility(
        rows=rows,
        tokenizer=tokenizer,
        context_length=512,
    )

    assert rows == original
