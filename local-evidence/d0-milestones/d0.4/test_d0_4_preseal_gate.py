"""
Synthetic tests for the D0.4 pre-seal gate.

No real D0.4 dataset is present in this file.
No real checkpoint is loaded.
No model scoring occurs.
"""

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE = HERE / "d0_4_preseal_gate.py"

spec = importlib.util.spec_from_file_location(
    "d0_4_preseal_gate",
    MODULE,
)

gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None

# Register the dynamically loaded module before execution.
# Python dataclasses resolve class-module metadata through
# sys.modules during decoration.
sys.modules[spec.name] = gate

spec.loader.exec_module(gate)


class SyntheticTokenizer:
    """
    Tiny synthetic tokenizer used only to test gate mechanics.
    """

    alphabet = set("abcdefghijklmnopqrstuvwxyz ")

    def encode(self, text):
        ids = []

        for char in text:
            if char not in self.alphabet:
                raise ValueError(
                    f"unsupported synthetic character: {char!r}"
                )
            ids.append(ord(char))

        return ids


def contract():
    return gate.CompatibilityContract(
        tokenizer=SyntheticTokenizer(),
        context_length=32,
    )


def test_partial_valid_rows_pass():
    rows = [
        {
            "instruction": "say cat",
            "response": "cat",
            "family": "literal_response",
        },
        {
            "instruction": "say dog",
            "response": "dog",
            "family": "short_completion",
        },
    ]

    result = gate.validate_preseal_candidate(
        rows,
        historical_rows=[],
        response_reuse_classes=[
            "forced"
            for _ in rows
        ],
        contract=contract(),
        require_final_counts=False,
    )

    assert result["status"] == "pass"
    assert result["modelScored"] is False


def test_bad_character_fails():
    rows = [
        {
            "instruction": "say cat?",
            "response": "cat",
            "family": "literal_response",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=[],
            response_reuse_classes=[
                "forced"
                for _ in rows
            ],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "unsupported tokenizer character was not rejected"
    )


def test_context_overflow_fails():
    rows = [
        {
            "instruction": "abcdefghijklmnopqrstuvwxy",
            "response": "abcdefghij",
            "family": "literal_response",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=[],
            response_reuse_classes=[
                "forced"
                for _ in rows
            ],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "context overflow was not rejected"
    )


def test_historical_instruction_overlap_fails():
    rows = [
        {
            "instruction": "say cat",
            "response": "cat",
            "family": "literal_response",
        }
    ]

    historical = [
        {
            "instruction": "say cat",
            "response": "other",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=historical,
            response_reuse_classes=["forced"],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "historical instruction overlap was not rejected"
    )


def test_duplicate_instruction_fails():
    rows = [
        {
            "instruction": "say cat",
            "response": "cat",
            "family": "literal_response",
        },
        {
            "instruction": "say  cat",
            "response": "dog",
            "family": "short_completion",
        },
    ]

    try:
        gate.validate_structure(
            rows,
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "normalized duplicate instruction was not rejected"
    )


def test_final_family_counts_fail_when_incomplete():
    rows = [
        {
            "instruction": "say cat",
            "response": "cat",
            "family": "literal_response",
        }
    ]

    try:
        gate.validate_structure(
            rows,
            require_final_counts=True,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "incomplete final dataset was not rejected"
    )




# D0.4 response-overlap clarification synthetic tests

def test_missing_response_reuse_class_fails():
    rows = [
        {
            "instruction": "echo amber",
            "response": "amber",
            "family": "literal_response",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=[],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "missing response reuse class must fail"
    )


def test_invalid_response_reuse_class_fails():
    rows = [
        {
            "instruction": "echo amber",
            "response": "amber",
            "family": "literal_response",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=[],
            response_reuse_classes=["unknown"],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "invalid response reuse class must fail"
    )


def test_response_reuse_class_length_mismatch_fails():
    rows = [
        {
            "instruction": "echo amber",
            "response": "amber",
            "family": "literal_response",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=[],
            response_reuse_classes=[],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "response reuse class length mismatch must fail"
    )


def test_forced_response_only_overlap_passes():
    rows = [
        {
            "instruction": "is amber a color",
            "response": "true",
            "family": "basic_instruction_following",
        }
    ]

    historical = [
        {
            "instruction": "is blue a color",
            "response": "true",
        }
    ]

    result = gate.validate_preseal_candidate(
        rows,
        historical_rows=historical,
        response_reuse_classes=["forced"],
        contract=contract(),
        require_final_counts=False,
    )

    assert result["status"] == "pass"
    assert result["freshnessValid"] is True
    assert result["modelScored"] is False


def test_discretionary_response_overlap_fails():
    rows = [
        {
            "instruction": "give a short label for a trial",
            "response": "experiment",
            "family": "short_completion",
        }
    ]

    historical = [
        {
            "instruction": "name a controlled test",
            "response": "experiment",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=historical,
            response_reuse_classes=["discretionary"],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "discretionary historical response overlap must fail"
    )


def test_instruction_overlap_still_fails_when_forced():
    rows = [
        {
            "instruction": "is amber a color",
            "response": "true",
            "family": "basic_instruction_following",
        }
    ]

    historical = [
        {
            "instruction": "is amber a color",
            "response": "false",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=historical,
            response_reuse_classes=["forced"],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "historical instruction overlap must remain prohibited"
    )


def test_pair_overlap_still_fails_when_forced():
    rows = [
        {
            "instruction": "is amber a color",
            "response": "true",
            "family": "basic_instruction_following",
        }
    ]

    historical = [
        {
            "instruction": "is amber a color",
            "response": "true",
        }
    ]

    try:
        gate.validate_preseal_candidate(
            rows,
            historical_rows=historical,
            response_reuse_classes=["forced"],
            contract=contract(),
            require_final_counts=False,
        )
    except gate.PresealValidationError:
        return

    raise AssertionError(
        "historical pair overlap must remain prohibited"
    )


def run_all():
    tests = [
        test_partial_valid_rows_pass,
        test_bad_character_fails,
        test_context_overflow_fails,
        test_historical_instruction_overlap_fails,
        test_duplicate_instruction_fails,
        test_final_family_counts_fail_when_incomplete,
        test_missing_response_reuse_class_fails,
        test_invalid_response_reuse_class_fails,
        test_response_reuse_class_length_mismatch_fails,
        test_forced_response_only_overlap_passes,
        test_discretionary_response_overlap_fails,
        test_instruction_overlap_still_fails_when_forced,
        test_pair_overlap_still_fails_when_forced,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print()
    print(f"Synthetic tests passed: {len(tests)}/{len(tests)}")


if __name__ == "__main__":
    run_all()
