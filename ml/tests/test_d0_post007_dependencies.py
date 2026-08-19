"""
Synthetic-only tests for D0-POST-007 dependency structure.

No formal dataset.
No real checkpoint.
No model inference.
No scoring.
"""

from __future__ import annotations

import inspect

from evaluation import d0_post007_dependencies as deps


def make_rows():
    rows = []

    families = list(deps.EXPECTED_FAMILIES)

    for cycle in range(5):
        for family in families:
            rows.append(
                {
                    "family": family,
                    "instruction":
                        f"synthetic {family} {cycle}",
                    "response": f"answer {cycle}",
                }
            )

    return rows


rows = make_rows()

assert len(rows) == 25

deps.validate_rows(rows)

print("✓ valid synthetic 25-row structure accepted")


bad = rows[:-1]

try:
    deps.validate_rows(bad)
except ValueError:
    print("✓ rejected: wrong row count")
else:
    raise AssertionError(
        "wrong row count was accepted"
    )


bad = [dict(row) for row in rows]
bad[0]["family"] = "invalid"

try:
    deps.validate_rows(bad)
except ValueError:
    print("✓ rejected: invalid family")
else:
    raise AssertionError(
        "invalid family was accepted"
    )


bad = [dict(row) for row in rows]
bad[0]["instruction"] = bad[5]["instruction"]

try:
    deps.validate_rows(bad)
except ValueError:
    print("✓ rejected: duplicate instruction")
else:
    raise AssertionError(
        "duplicate instruction was accepted"
    )


bad = [dict(row) for row in rows]
bad[0]["extra"] = "forbidden"

try:
    deps.validate_rows(bad)
except ValueError:
    print("✓ rejected: extra semantic field")
else:
    raise AssertionError(
        "extra semantic field was accepted"
    )


bad = [dict(row) for row in rows]
bad[0], bad[1] = bad[1], bad[0]

try:
    deps.validate_rows(bad)
except ValueError:
    print("✓ rejected: wrong family interleaving")
else:
    raise AssertionError(
        "wrong family interleaving was accepted"
    )


signature = inspect.signature(
    deps.score_checkpoint
)

parameters = list(signature.parameters)

assert parameters == [
    "checkpoint_path",
    "rows",
], parameters

print(
    "✓ score_checkpoint accepts checkpoint + rows only"
)


source = inspect.getsource(
    deps.score_checkpoint
)

assert "load_rows(" not in source
assert "d0_post007_formal.jsonl" not in source
assert "FORMAL_EXPOSURE_STARTED" not in source

print(
    "✓ scorer cannot independently reopen formal dataset"
)


module_source = inspect.getsource(deps)

assert "d0_post007_formal.jsonl" not in module_source
assert "FORMAL_EXPOSURE_STARTED" not in module_source

print(
    "✓ dependency module embeds no formal resource path"
)

print()
print("SYNTHETIC_DEPENDENCY_TESTS_PASSED=8")
print("REAL_CHECKPOINT_LOADED=NO")
print("MODEL_INFERENCE_EXECUTED=NO")
print("MODEL_SCORING_EXECUTED=NO")
print("FORMAL_DATASET_PARSED=NO")
