from __future__ import annotations

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post006_formal.py"
)

spec = importlib.util.spec_from_file_location(
    "d0_post006_formal",
    MODULE_PATH,
)

assert spec is not None
assert spec.loader is not None

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

compare = module.compare_formal_results


FAMILIES = (
    "echo",
    "boolean",
    "plural",
    "opposite",
    "world_fact",
)


def result(
    aggregate: float,
    exact: int,
    family_loss: float = 1.0,
):
    return {
        "aggregateResponseLoss": aggregate,
        "exactMatches": exact,
        "perFamily": {
            family: {
                "responseLoss": family_loss,
            }
            for family in FAMILIES
        },
    }


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def run_tests():
    count = 0

    # 1 — PASS
    baseline = result(1.0, 2, 1.0)
    candidate = result(0.9, 3, 1.02)

    out = compare(baseline, candidate)

    require(out["formalPass"] is True, "PASS case failed")
    print("✓ PASS case")
    count += 1

    # 2 — minimum candidate exact failure
    baseline = result(1.0, 0, 1.0)
    candidate = result(0.9, 0, 1.0)

    out = compare(baseline, candidate)

    require(
        out["formalPass"] is False,
        "minimum exact failure not detected",
    )
    require(
        out["minimumCandidateExactMatchesPassed"] is False,
        "minimum exact condition incorrect",
    )

    print("✓ minimum-exact failure")
    count += 1

    # 3 — strict exact improvement failure
    baseline = result(1.0, 3, 1.0)
    candidate = result(0.9, 3, 1.0)

    out = compare(baseline, candidate)

    require(
        out["strictExactMatchImprovementPassed"] is False,
        "strict exact rule failure not detected",
    )

    require(out["formalPass"] is False, "unexpected PASS")

    print("✓ strict-exact-improvement failure")
    count += 1

    # 4 — aggregate loss failure
    baseline = result(1.0, 2, 1.0)
    candidate = result(1.0, 3, 1.0)

    out = compare(baseline, candidate)

    require(
        out["aggregateResponseLossImprovementPassed"]
        is False,
        "aggregate strict-improvement failure not detected",
    )

    require(out["formalPass"] is False, "unexpected PASS")

    print("✓ aggregate-loss failure")
    count += 1

    # 5 — one-family >5% regression
    baseline = result(1.0, 2, 1.0)
    candidate = result(0.9, 3, 1.0)

    candidate["perFamily"]["plural"][
        "responseLoss"
    ] = 1.051

    out = compare(baseline, candidate)

    require(
        out["allFiveFamiliesRetentionPassed"]
        is False,
        "family regression failure not detected",
    )

    require(
        out["perFamilyComparison"]["plural"]["passed"]
        is False,
        "plural family should fail",
    )

    require(out["formalPass"] is False, "unexpected PASS")

    print("✓ individual-family retention failure")
    count += 1

    # 6 — exact 5% boundary passes
    baseline = result(1.0, 2, 1.0)
    candidate = result(0.9, 3, 1.0)

    candidate["perFamily"]["opposite"][
        "responseLoss"
    ] = 1.05

    out = compare(baseline, candidate)

    require(
        out["perFamilyComparison"]["opposite"]["passed"]
        is True,
        "exact 5% boundary should pass",
    )

    require(out["formalPass"] is True, "boundary PASS failed")

    print("✓ exact 5-percent boundary")
    count += 1

    # 7 — zero-baseline family passes at zero
    baseline = result(1.0, 2, 1.0)
    candidate = result(0.9, 3, 1.0)

    baseline["perFamily"]["echo"]["responseLoss"] = 0.0
    candidate["perFamily"]["echo"]["responseLoss"] = 0.0

    out = compare(baseline, candidate)

    require(
        out["perFamilyComparison"]["echo"]["passed"]
        is True,
        "zero baseline with zero candidate must pass",
    )

    print("✓ zero-baseline pass")
    count += 1

    # 8 — zero-baseline family fails above zero
    baseline = result(1.0, 2, 1.0)
    candidate = result(0.9, 3, 1.0)

    baseline["perFamily"]["echo"]["responseLoss"] = 0.0
    candidate["perFamily"]["echo"]["responseLoss"] = 0.000001

    out = compare(baseline, candidate)

    require(
        out["perFamilyComparison"]["echo"]["passed"]
        is False,
        "zero-baseline failure not detected",
    )

    require(out["formalPass"] is False, "unexpected PASS")

    print("✓ zero-baseline failure")
    count += 1

    # 9 — all conditions conjunctive
    baseline = result(1.0, 2, 1.0)
    candidate = result(0.9, 3, 1.0)

    candidate["perFamily"]["world_fact"][
        "responseLoss"
    ] = 1.06

    out = compare(baseline, candidate)

    require(
        out["minimumCandidateExactMatchesPassed"]
        is True,
        "minimum exact should pass",
    )

    require(
        out["strictExactMatchImprovementPassed"]
        is True,
        "exact improvement should pass",
    )

    require(
        out["aggregateResponseLossImprovementPassed"]
        is True,
        "aggregate improvement should pass",
    )

    require(
        out["allFiveFamiliesRetentionPassed"]
        is False,
        "family conjunction should fail",
    )

    require(
        out["formalPass"] is False,
        "all conditions must be conjunctive",
    )

    print("✓ all-five-family conjunction")
    count += 1

    # 10 — malformed family set rejected
    baseline = result(1.0, 2, 1.0)
    candidate = result(0.9, 3, 1.0)

    del candidate["perFamily"]["echo"]

    try:
        compare(baseline, candidate)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "malformed family set was accepted"
        )

    print("✓ malformed family set rejected")
    count += 1

    print()
    print(f"PURE_COMPARISON_TESTS_PASSED={count}")


if __name__ == "__main__":
    run_tests()
