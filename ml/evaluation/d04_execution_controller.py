from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

from evaluation.d04_final_evaluator import (
    EXPECTED_FAMILIES,
    evaluate_rows,
)
from inference.d0_inference import (
    load_checkpoint,
)


ROOT = Path(__file__).resolve().parents[2]

D04_DIR = (
    ROOT
    / "local-evidence"
    / "d0-milestones"
    / "d0.4"
)

DATASET = (
    D04_DIR
    / "D04_PROPOSED_DATASET.jsonl"
)

SEAL = (
    D04_DIR
    / "D04_DATASET_SEAL.json"
)

MANIFEST = (
    D04_DIR
    / "D04_SEALED_DATASET_MANIFEST.json"
)

PROTOCOL = (
    D04_DIR
    / "EVALUATION_PROTOCOL.md"
)

CONTRACT = (
    D04_DIR
    / "INDEPENDENT_EVALUATION_CONTRACT.md"
)

CHECKPOINT = (
    ROOT
    / "local-checkpoints"
    / "d0-post002-accepted.pt"
)

EVALUATOR = (
    ROOT
    / "ml"
    / "evaluation"
    / "d04_final_evaluator.py"
)

EVALUATOR_TESTS = (
    ROOT
    / "ml"
    / "tests"
    / "test_d04_final_evaluator.py"
)

IMPLEMENTATION_FREEZE = (
    D04_DIR
    / "D04_EVALUATOR_IMPLEMENTATION_FREEZE.json"
)

PRE_EXECUTION_SEAL = (
    D04_DIR
    / "D04_PRE_EXECUTION_SEAL.json"
)

EXPECTED_EXECUTION_IDENTITIES = {
    EVALUATOR: (
        "d654d108762e216702da64584b8de5494"
        "b8a88139b39ed8cd4316f78a125153a"
    ),
    EVALUATOR_TESTS: (
        "70d7d4f02c7bee9fb9f952a155e6288b"
        "8e8b34c2ef960068571d1217ecbd440a"
    ),
}

OUTPUT = (
    D04_DIR
    / "D04_FORMAL_EVALUATION_RESULT.json"
)


EXPECTED_IDENTITIES = {
    DATASET: (
        "ae97701e409d3836a4097b64e0548f30"
        "bdab46c80a0db763c650fc4c8c77b8af"
    ),
    SEAL: (
        "c9958d9b14840e7f9cb6e53f278da2f6"
        "cd244722a3f23661e6866095a81d3478"
    ),
    MANIFEST: (
        "707db5498820462db1a2885fc086be85"
        "d93ad01ed27716dbf8fb520fb19ab6f9"
    ),
    PROTOCOL: (
        "d16170455693e05d414a01e455286362"
        "c5df7670c66141551786afaed5c670a5"
    ),
    CONTRACT: (
        "8da2d419065ee6b482087207dda7cc7f"
        "901b5d143395f669f2d04b215380adb0"
    ),
}


AUTHORIZATION_PHRASE = (
    "AUTHORIZE_D04_CANONICAL_EVALUATION"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    identities: dict[str, str] = {}

    for path, expected in EXPECTED_IDENTITIES.items():
        if not path.exists():
            raise RuntimeError(
                f"FAIL-CLOSED: missing frozen input: {path}"
            )

        actual = sha256_file(path)

        if actual != expected:
            raise RuntimeError(
                "FAIL-CLOSED: frozen identity mismatch: "
                f"{path}\n"
                f"expected={expected}\n"
                f"actual={actual}"
            )

        identities[str(path.relative_to(ROOT))] = (
            actual
        )

    return identities


def verify_execution_identities() -> None:
    # Directly frozen executable identities.
    for path, expected in (
        EXPECTED_EXECUTION_IDENTITIES.items()
    ):
        if not path.exists():
            raise RuntimeError(
                "FAIL-CLOSED: missing execution identity: "
                f"{path}"
            )

        actual = sha256_file(path)

        if actual != expected:
            raise RuntimeError(
                "FAIL-CLOSED: execution identity mismatch: "
                f"{path}\n"
                f"expected={expected}\n"
                f"actual={actual}"
            )

    # The evidence files attest to this controller. Their own
    # file hashes must therefore not be embedded back into this
    # controller, which would create a self-referential cycle.
    for evidence_path in (
        IMPLEMENTATION_FREEZE,
        PRE_EXECUTION_SEAL,
    ):
        if not evidence_path.exists():
            raise RuntimeError(
                "FAIL-CLOSED: missing execution evidence: "
                f"{evidence_path}"
            )

    try:
        freeze = json.loads(
            IMPLEMENTATION_FREEZE.read_text(
                encoding="utf-8"
            )
        )
        preseal = json.loads(
            PRE_EXECUTION_SEAL.read_text(
                encoding="utf-8"
            )
        )
    except Exception as exc:
        raise RuntimeError(
            "FAIL-CLOSED: invalid execution evidence JSON"
        ) from exc

    controller_sha = sha256_file(
        Path(__file__).resolve()
    )
    evaluator_sha = sha256_file(EVALUATOR)
    tests_sha = sha256_file(EVALUATOR_TESTS)
    freeze_sha = sha256_file(IMPLEMENTATION_FREEZE)

    required_freeze = {
        "ml/evaluation/d04_execution_controller.py":
            controller_sha,
        "ml/evaluation/d04_final_evaluator.py":
            evaluator_sha,
        "ml/tests/test_d04_final_evaluator.py":
            tests_sha,
    }

    freeze_files = freeze.get("files")

    if not isinstance(freeze_files, dict):
        raise RuntimeError(
            "FAIL-CLOSED: invalid implementation freeze"
        )

    for rel_path, expected_sha in (
        required_freeze.items()
    ):
        entry = freeze_files.get(rel_path)

        if not isinstance(entry, dict):
            raise RuntimeError(
                "FAIL-CLOSED: implementation freeze "
                f"missing identity: {rel_path}"
            )

        if entry.get("sha256") != expected_sha:
            raise RuntimeError(
                "FAIL-CLOSED: implementation freeze "
                f"identity mismatch: {rel_path}"
            )

    if freeze.get("milestone") != "D0.4":
        raise RuntimeError(
            "FAIL-CLOSED: wrong implementation "
            "freeze milestone"
        )

    if freeze.get("status") != "implementation-frozen":
        raise RuntimeError(
            "FAIL-CLOSED: invalid implementation "
            "freeze status"
        )

    if freeze.get("formalExecutionAuthorized") is not False:
        raise RuntimeError(
            "FAIL-CLOSED: implementation freeze "
            "authorization state invalid"
        )

    frozen = preseal.get("frozenIdentities")

    if not isinstance(frozen, dict):
        raise RuntimeError(
            "FAIL-CLOSED: invalid pre-execution seal"
        )

    required_preseal = {
        "executionController": controller_sha,
        "evaluator": evaluator_sha,
        "evaluatorTests": tests_sha,
        "implementationFreeze": freeze_sha,
    }

    for name, expected_sha in (
        required_preseal.items()
    ):
        entry = frozen.get(name)

        if not isinstance(entry, dict):
            raise RuntimeError(
                "FAIL-CLOSED: pre-execution seal "
                f"missing identity: {name}"
            )

        if entry.get("sha256") != expected_sha:
            raise RuntimeError(
                "FAIL-CLOSED: pre-execution seal "
                f"identity mismatch: {name}"
            )

    if preseal.get("milestone") != "D0.4":
        raise RuntimeError(
            "FAIL-CLOSED: wrong pre-execution "
            "seal milestone"
        )

    if preseal.get("status") != "pre-execution-sealed":
        raise RuntimeError(
            "FAIL-CLOSED: invalid pre-execution "
            "seal status"
        )

    if preseal.get("formalExecutionAuthorized") is not False:
        raise RuntimeError(
            "FAIL-CLOSED: pre-execution seal "
            "authorization state invalid"
        )

    if preseal.get("formalEvaluationExecuted") is not False:
        raise RuntimeError(
            "FAIL-CLOSED: pre-execution seal "
            "execution state invalid"
        )

    checkpoint_state = preseal.get(
        "canonicalCheckpoint"
    )

    if not isinstance(checkpoint_state, dict):
        raise RuntimeError(
            "FAIL-CLOSED: invalid checkpoint "
            "pre-execution state"
        )

    for key in (
        "opened",
        "hashed",
        "loaded",
        "scored",
    ):
        if checkpoint_state.get(key) is not False:
            raise RuntimeError(
                "FAIL-CLOSED: checkpoint state "
                f"invalid before execution: {key}"
            )


def load_dataset() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for line_number, raw in enumerate(
        DATASET.read_text(
            encoding="utf-8"
        ).splitlines(),
        start=1,
    ):
        line = raw.strip()

        if not line:
            continue

        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"invalid JSONL at line {line_number}"
            ) from exc

        if not isinstance(row, dict):
            raise RuntimeError(
                f"row {line_number} is not an object"
            )

        rows.append(row)

    if len(rows) != 25:
        raise RuntimeError(
            "FAIL-CLOSED: D0.4 dataset must contain "
            f"exactly 25 examples; found {len(rows)}"
        )

    families = {
        str(row.get("family"))
        for row in rows
    }

    if families != EXPECTED_FAMILIES:
        raise RuntimeError(
            "FAIL-CLOSED: unexpected D0.4 family set: "
            f"{sorted(families)}"
        )

    return rows


def require_authorization(
    supplied: str | None,
) -> None:
    env_value = os.environ.get(
        "DENARIXX_D04_AUTHORIZATION"
    )

    if supplied != AUTHORIZATION_PHRASE:
        raise RuntimeError(
            "CANONICAL EXECUTION REFUSED: explicit "
            "authorization phrase not supplied"
        )

    if env_value != AUTHORIZATION_PHRASE:
        raise RuntimeError(
            "CANONICAL EXECUTION REFUSED: "
            "DENARIXX_D04_AUTHORIZATION environment "
            "variable not supplied"
        )


def execute(
    authorization: str | None,
) -> None:
    print("=" * 78)
    print(" DENARIXX FRONTIER AI")
    print(" D0.4 — CANONICAL FORMAL EVALUATION CONTROLLER")
    print("=" * 78)
    print()

    print("1. Verifying frozen D0.4 identities...")
    identities = verify_frozen_inputs()
    print("   PASS")
    print()

    print("2. Verifying pre-execution identities...")
    verify_execution_identities()
    print("   PASS")
    print()

    print("3. Loading sealed D0.4 dataset...")
    rows = load_dataset()
    print(f"   PASS: {len(rows)} examples")
    print()

    print("4. Checking explicit execution authorization...")

    require_authorization(
        authorization
    )

    print("   PASS")
    print()

    if OUTPUT.exists():
        raise RuntimeError(
            "FAIL-CLOSED: canonical D0.4 result already "
            f"exists: {OUTPUT}"
        )

    print("5. Loading canonical checkpoint...")
    loaded = load_checkpoint(CHECKPOINT)
    print("   PASS")
    print()

    print("6. Executing frozen D0.4 evaluation...")
    result = evaluate_rows(
        model=loaded.model,
        tokenizer=loaded.tokenizer,
        rows=rows,
    )
    print("   COMPLETE")
    print()

    payload = {
        "status": "complete",
        "milestone": "D0.4",
        "evaluationType": "canonical-formal",
        "dataset": str(
            DATASET.relative_to(ROOT)
        ),
        "checkpoint": str(
            CHECKPOINT.relative_to(ROOT)
        ),
        "frozenInputIdentities": identities,
        "checkpointSha256": sha256_file(
            CHECKPOINT
        ),
        "modelConfig": loaded.config.__dict__,
        "evaluation": result.to_dict(),
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Result: {OUTPUT}")
    print(
        f"Result SHA256: {sha256_file(OUTPUT)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--authorization",
        default=None,
    )

    args = parser.parse_args()

    execute(
        authorization=args.authorization
    )


if __name__ == "__main__":
    main()
