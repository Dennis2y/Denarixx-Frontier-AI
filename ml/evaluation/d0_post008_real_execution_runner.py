"""
D0-POST-008 governed real formal execution runner.

IMPORTANT:

This module defines the real execution lifecycle but does not execute
it merely by being imported.

Execution requires a separately created replacement authorization.

Frozen lifecycle:

    verify identities
    -> create formal exposure marker
    -> load sealed rows exactly once
    -> score baseline
    -> persist baseline
    -> score candidate
    -> persist candidate
    -> reload persisted results
    -> compare persisted results
    -> adjudicate comparison
    -> persist comparison
    -> persist final adjudication

No training or adaptation is performed.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from evaluation import d0_post008_adjudicator
from evaluation import d0_post008_dependencies


STAGE = "D0-POST-008"

ROOT = Path.cwd()

FORMAL_DATASET = Path(
    "ml/data/d0_post008_formal.jsonl"
)

BASELINE_CHECKPOINT = Path(
    "local-checkpoints/d0-post003-capability-seed42.pt"
)

CANDIDATE_CHECKPOINT = Path(
    "local-checkpoints/"
    "d0-post005-development-seed42-step120.pt"
)

RESULT_DIR = Path(
    "local-evidence/d0-post008-formal-execution"
)

EXPOSURE_MARKER = (
    RESULT_DIR / "FORMAL_EXPOSURE_STARTED"
)

BASELINE_RESULT = (
    RESULT_DIR / "BASELINE_RESULT.json"
)

CANDIDATE_RESULT = (
    RESULT_DIR / "CANDIDATE_RESULT.json"
)

COMPARISON_RESULT = (
    RESULT_DIR / "COMPARISON_RESULT.json"
)

FINAL_ADJUDICATION = (
    RESULT_DIR / "FINAL_ADJUDICATION.json"
)

FAILURE_RESULT = (
    RESULT_DIR / "FAILURE.json"
)

EXPECTED_DATASET_SHA256 = (
    "78ff74ea7103c52cee382cd87879a30bc"
    "1f9b65c16a800249c322303fa63d95b"
)

EXPECTED_BASELINE_SHA256 = (
    "3b409092c120242fe4ed75113758390de"
    "e3e8e627507afdf7bcbc1bb5b3ccc06"
)

EXPECTED_CANDIDATE_SHA256 = (
    "4877d292fdd8e5428db250359dc9c57e"
    "bc4f4d1ccb2a329b94bdafd2c61569d9"
)


class FormalExecutionError(RuntimeError):
    pass


class FormalExecutionRerunError(FormalExecutionError):
    pass


class IdentityError(FormalExecutionError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def verify_identity(
    path: Path,
    expected: str,
) -> None:
    actual = sha256_file(path)

    if actual != expected:
        raise IdentityError(
            "artifact identity mismatch: "
            f"{path}; expected={expected}; actual={actual}"
        )


def create_once_text(
    path: Path,
    text: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        fd = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o444,
        )
    except FileExistsError as exc:
        raise FormalExecutionRerunError(
            f"create-once artifact already exists: {path}"
        ) from exc

    with os.fdopen(
        fd,
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(text)


def persist_json_create_once(
    path: Path,
    value: Mapping[str, Any],
) -> None:
    create_once_text(
        path,
        json.dumps(
            dict(value),
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def read_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise FormalExecutionError(
            f"expected JSON object: {path}"
        )

    return value


def assert_pre_exposure_state() -> None:
    if RESULT_DIR.exists():
        raise FormalExecutionRerunError(
            "formal result directory already exists; "
            "POST-008 real execution is one-shot"
        )

    if EXPOSURE_MARKER.exists():
        raise FormalExecutionRerunError(
            "formal exposure marker already exists"
        )


def verify_frozen_inputs() -> None:
    verify_identity(
        FORMAL_DATASET,
        EXPECTED_DATASET_SHA256,
    )

    verify_identity(
        BASELINE_CHECKPOINT,
        EXPECTED_BASELINE_SHA256,
    )

    verify_identity(
        CANDIDATE_CHECKPOINT,
        EXPECTED_CANDIDATE_SHA256,
    )


def run_governed_formal_execution(
    *,
    authorization_verified: bool = False,
) -> dict[str, Any]:
    """
    Execute the single real POST-008 formal evaluation.

    The caller must verify the replacement authorization before
    invoking this function.

    Passing authorization_verified=True is an explicit mechanical
    boundary. The replacement authorization must bind this runner's
    exact frozen SHA256.
    """

    if authorization_verified is not True:
        raise FormalExecutionError(
            "replacement formal execution authorization "
            "has not been verified"
        )

    assert_pre_exposure_state()

    # Identity verification occurs before exposure.
    verify_frozen_inputs()

    # This is the irreversible formal-exposure boundary.
    create_once_text(
        EXPOSURE_MARKER,
        f"{STAGE} FORMAL_EXPOSURE_STARTED\n",
    )

    try:
        # Dataset is opened exactly once by the runner.
        rows = d0_post008_dependencies.load_rows(
            FORMAL_DATASET
        )

        if len(rows) != 40:
            raise FormalExecutionError(
                "sealed formal dataset must contain exactly 40 rows"
            )

        # Same in-memory rows object is supplied to both scorings.
        baseline = dict(
            d0_post008_dependencies.score_checkpoint(
                BASELINE_CHECKPOINT,
                rows,
            )
        )

        persist_json_create_once(
            BASELINE_RESULT,
            baseline,
        )

        candidate = dict(
            d0_post008_dependencies.score_checkpoint(
                CANDIDATE_CHECKPOINT,
                rows,
            )
        )

        persist_json_create_once(
            CANDIDATE_RESULT,
            candidate,
        )

        persisted_baseline = read_json(
            BASELINE_RESULT
        )

        persisted_candidate = read_json(
            CANDIDATE_RESULT
        )

        comparison = dict(
            d0_post008_dependencies.compare_results(
                persisted_baseline,
                persisted_candidate,
            )
        )

        persist_json_create_once(
            COMPARISON_RESULT,
            comparison,
        )

        persisted_comparison = read_json(
            COMPARISON_RESULT
        )

        adjudication = dict(
            d0_post008_adjudicator.adjudicate(
                persisted_comparison
            )
        )

        persist_json_create_once(
            FINAL_ADJUDICATION,
            adjudication,
        )

        return {
            "stage": STAGE,
            "status": "formal-execution-completed",
            "formalExposureStarted": True,
            "baselinePersistedBeforeCandidateScoring": True,
            "candidatePersistedBeforeComparison": True,
            "comparisonUsedPersistedResults": True,
            "adjudicationUsedPersistedComparison": True,
            "sameInMemoryRowsUsedForBothCheckpoints": True,
            "trainingExecuted": False,
            "formalPass":
                bool(adjudication["formalPass"]),
        }

    except Exception as exc:
        failure = {
            "stage": STAGE,
            "status": "failed-after-formal-exposure",
            "errorType": type(exc).__name__,
            "error": str(exc),
            "formalExposureStarted": True,
        }

        RESULT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not FAILURE_RESULT.exists():
            persist_json_create_once(
                FAILURE_RESULT,
                failure,
            )

        raise


if __name__ == "__main__":
    raise SystemExit(
        "Direct execution is disabled. "
        "Use the separately governed replacement-authorization runner."
    )
