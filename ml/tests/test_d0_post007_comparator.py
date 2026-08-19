from __future__ import annotations

from copy import deepcopy

from evaluation import d0_post007_dependencies as deps


FAMILIES = list(deps.EXPECTED_FAMILIES)


def result(
    *,
    aggregate: float,
    exact: int,
    family_loss: float = 1.0,
) -> dict:
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


# ---------------------------------------------------------
# 1. Canonical PASS
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=0.90,
    exact=2,
)

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is True
assert (
    decision[
        "minimumCandidateExactMatchesPassed"
    ]
    is True
)
assert (
    decision[
        "strictExactMatchImprovementPassed"
    ]
    is True
)
assert (
    decision[
        "aggregateResponseLossImprovementPassed"
    ]
    is True
)
assert (
    decision[
        "allFiveFamiliesRetentionPassed"
    ]
    is True
)

print("✓ canonical synthetic PASS accepted")


# ---------------------------------------------------------
# 2. Zero candidate exact matches must fail
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=0,
)

candidate = result(
    aggregate=0.90,
    exact=0,
)

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is False
assert (
    decision[
        "minimumCandidateExactMatchesPassed"
    ]
    is False
)

print("✓ zero candidate exact matches rejected")


# ---------------------------------------------------------
# 3. Equal exact count must fail strict improvement
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=0.90,
    exact=1,
)

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is False
assert (
    decision[
        "strictExactMatchImprovementPassed"
    ]
    is False
)

print("✓ equal exact-match count rejected")


# ---------------------------------------------------------
# 4. Equal aggregate loss must fail strict improvement
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=1.00,
    exact=2,
)

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is False
assert (
    decision[
        "aggregateResponseLossImprovementPassed"
    ]
    is False
)

print("✓ equal aggregate loss rejected")


# ---------------------------------------------------------
# 5. Exactly 5% family regression is allowed
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
    family_loss=1.00,
)

candidate = result(
    aggregate=0.90,
    exact=2,
    family_loss=1.05,
)

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is True

for family in FAMILIES:
    assert (
        decision["perFamilyComparison"][
            family
        ]["passed"]
        is True
    )

print("✓ exact 5% family regression accepted")


# ---------------------------------------------------------
# 6. Greater than 5% family regression must fail
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
    family_loss=1.00,
)

candidate = result(
    aggregate=0.90,
    exact=2,
    family_loss=1.00,
)

bad_family = FAMILIES[0]

candidate["perFamily"][bad_family][
    "responseLoss"
] = 1.050001

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is False
assert (
    decision[
        "allFiveFamiliesRetentionPassed"
    ]
    is False
)

assert (
    decision["perFamilyComparison"][
        bad_family
    ]["passed"]
    is False
)

print("✓ >5% family regression rejected")


# ---------------------------------------------------------
# 7. Zero-baseline family requires candidate zero
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=0.90,
    exact=2,
)

zero_family = FAMILIES[0]

baseline["perFamily"][zero_family][
    "responseLoss"
] = 0.0

candidate["perFamily"][zero_family][
    "responseLoss"
] = 0.000001

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is False

family_decision = (
    decision["perFamilyComparison"][
        zero_family
    ]
)

assert (
    family_decision[
        "zeroBaselineRuleApplied"
    ]
    is True
)

assert family_decision["passed"] is False

print("✓ zero-baseline nonzero candidate loss rejected")


# ---------------------------------------------------------
# 8. Zero-baseline / zero-candidate family passes
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=0.90,
    exact=2,
)

zero_family = FAMILIES[0]

baseline["perFamily"][zero_family][
    "responseLoss"
] = 0.0

candidate["perFamily"][zero_family][
    "responseLoss"
] = 0.0

decision = deps.compare_results(
    baseline,
    candidate,
)

assert decision["formalPass"] is True

assert (
    decision["perFamilyComparison"][
        zero_family
    ]["passed"]
    is True
)

print("✓ zero-baseline / zero-candidate family accepted")


# ---------------------------------------------------------
# 9. Missing family must be rejected
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=0.90,
    exact=2,
)

del candidate["perFamily"][
    FAMILIES[-1]
]

try:
    deps.compare_results(
        baseline,
        candidate,
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "missing family was not rejected"
    )

print("✓ missing family rejected")


# ---------------------------------------------------------
# 10. Extra family must be rejected
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=0.90,
    exact=2,
)

candidate["perFamily"]["unexpected"] = {
    "responseLoss": 1.0,
}

try:
    deps.compare_results(
        baseline,
        candidate,
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "extra family was not rejected"
    )

print("✓ extra family rejected")


# ---------------------------------------------------------
# 11. Negative aggregate loss rejected
# ---------------------------------------------------------

bad = result(
    aggregate=-0.01,
    exact=2,
)

good = result(
    aggregate=1.00,
    exact=1,
)

try:
    deps.compare_results(
        good,
        bad,
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "negative aggregate loss was not rejected"
    )

print("✓ negative aggregate loss rejected")


# ---------------------------------------------------------
# 12. Negative family loss rejected
# ---------------------------------------------------------

baseline = result(
    aggregate=1.00,
    exact=1,
)

candidate = result(
    aggregate=0.90,
    exact=2,
)

candidate["perFamily"][
    FAMILIES[0]
]["responseLoss"] = -0.01

try:
    deps.compare_results(
        baseline,
        candidate,
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "negative family loss was not rejected"
    )

print("✓ negative family loss rejected")


print()
print("SYNTHETIC_COMPARATOR_TESTS_PASSED=12")
print("FORMAL_DATASET_PARSED=NO")
print("REAL_CHECKPOINT_LOADED=NO")
print("MODEL_INFERENCE_EXECUTED=NO")
print("MODEL_SCORING_EXECUTED=NO")
