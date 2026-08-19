from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ML_ROOT = ROOT / "ml"

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from evaluation.d0_post007_compatibility import (
    CompatibilityContract,
    CompatibilityError,
    EXPECTED_FAMILIES,
    load_compatibility_contract,
    validate_compatibility,
)


BASELINE = ROOT / (
    "local-checkpoints/"
    "d0-post003-capability-seed42.pt"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def make_rows(
    contract: CompatibilityContract,
):
    alphabet = set(contract.tokenizer.alphabet)

    candidates = [
        "a", "b", "c", "d", "e",
        "f", "g", "h", "i", "j",
        "k", "l", "m", "n", "o",
        "p", "q", "r", "s", "t",
        "u", "v", "w", "x", "y",
        "z", "0", "1", "2", "3",
        "yes", "no", "cat", "cats",
        "hot", "cold", "sky", "blue",
    ]

    safe = [
        text
        for text in candidates
        if set(text + "\n").issubset(alphabet)
    ]

    if len(safe) < 26:
        raise AssertionError(
            "not enough tokenizer-compatible synthetic strings"
        )

    rows = []
    position = 0

    for cycle in range(5):
        for family in EXPECTED_FAMILIES:
            instruction = safe[position]
            response = safe[position + 1]
            position += 1

            rows.append(
                {
                    "instruction": instruction,
                    "response": response,
                    "family": family,
                }
            )

    return rows


def expect_failure(rows, contract, label):
    try:
        validate_compatibility(
            rows,
            contract=contract,
        )
    except CompatibilityError:
        print(f"✓ rejected: {label}")
        return

    raise AssertionError(
        f"validator failed to reject: {label}"
    )


def main():
    contract = load_compatibility_contract(BASELINE)

    print(
        "accepted baseline context length:",
        contract.context_length,
    )

    rows = make_rows(contract)

    result = validate_compatibility(
        rows,
        contract=contract,
    )

    require(result["compatible"] is True, "valid rows rejected")
    require(result["rowsValidated"] == 25, "wrong row count")
    require(
        result["modelInferenceExecuted"] is False,
        "validator reported inference",
    )

    print("✓ valid synthetic 25-row dataset accepted")

    bad = [dict(row) for row in rows]
    bad.pop()
    expect_failure(bad, contract, "24 rows")

    bad = [dict(row) for row in rows]
    bad[0]["family"] = "invalid"
    expect_failure(bad, contract, "invalid family")

    bad = [dict(row) for row in rows]
    bad[1]["instruction"] = bad[0]["instruction"]
    expect_failure(bad, contract, "duplicate instruction")

    bad = [dict(row) for row in rows]
    bad[0]["extra"] = "x"
    expect_failure(bad, contract, "extra semantic field")

    bad = [dict(row) for row in rows]
    bad[0]["instruction"] = ""
    expect_failure(bad, contract, "empty instruction")

    bad = [dict(row) for row in rows]
    bad[0]["response"] = ""
    expect_failure(bad, contract, "empty response")

    bad = [dict(row) for row in rows]
    bad[0], bad[1] = bad[1], bad[0]
    expect_failure(bad, contract, "wrong family interleaving")

    unsupported = None

    for candidate in [":", "€", "§", "@", "#", "~"]:
        if candidate not in set(contract.tokenizer.alphabet):
            unsupported = candidate
            break

    if unsupported is None:
        raise AssertionError(
            "could not find synthetic unsupported character"
        )

    bad = [dict(row) for row in rows]
    bad[0]["instruction"] = (
        bad[0]["instruction"] + unsupported
    )

    expect_failure(
        bad,
        contract,
        "unsupported tokenizer character",
    )

    long_safe = next(
        char
        for char in contract.tokenizer.alphabet
        if char != "\n"
    )

    bad = [dict(row) for row in rows]
    bad[0]["instruction"] = (
        long_safe * contract.context_length
    )

    expect_failure(
        bad,
        contract,
        "context-length overflow",
    )

    print()
    print("SYNTHETIC_COMPATIBILITY_TESTS_PASSED=9")
    print("MODEL_INFERENCE_EXECUTED=NO")
    print("MODEL_LOSS_COMPUTED=NO")
    print("CANDIDATE_CHECKPOINT_LOADED=NO")


if __name__ == "__main__":
    main()
