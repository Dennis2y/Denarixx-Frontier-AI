"""
D0-POST-007 formal execution activation boundary.

This module is intentionally DISARMED.

It defines the future one-time formal execution lifecycle but cannot
execute it while FORMAL_ACTIVATION_ARMED remains False.

Importing this module does not:

- parse the sealed formal dataset
- load a checkpoint
- score a model
- compare formal results
- create FORMAL_EXPOSURE_STARTED
- persist formal execution evidence
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from evaluation import d0_post007_dependencies as frozen_dependencies


STAGE = "D0-POST-007"

FORMAL_ACTIVATION_ARMED = False

FORMAL_DATASET = Path(
    "ml/data/d0_post007_formal.jsonl"
)

BASELINE = Path(
    "local-checkpoints/d0-post003-capability-seed42.pt"
)

CANDIDATE = Path(
    "local-checkpoints/"
    "d0-post005-development-seed42-step120.pt"
)

FORMAL_RESULT_DIR = Path(
    "local-evidence/d0-post007-formal-execution"
)

EXPOSURE_MARKER = (
    FORMAL_RESULT_DIR / "FORMAL_EXPOSURE_STARTED"
)

AUTHORIZATION_FILE = Path(
    "local-evidence/"
    "d0-post007-formal-execution-authorization/"
    "FORMAL_EXECUTION_AUTHORIZATION.json"
)

EXPECTED_DATASET_SHA256 = (
    "f0f5c88524c4f0b78f4ebbd235480061"
    "03aa3e4116cc4a3df34493712b07fb0c"
)

EXPECTED_BASELINE_SHA256 = (
    "3b409092c120242fe4ed75113758390de"
    "e3e8e627507afdf7bcbc1bb5b3ccc06"
)

EXPECTED_CANDIDATE_SHA256 = (
    "4877d292fdd8e5428db250359dc9c57e"
    "bc4f4d1ccb2a329b94bdafd2c61569d9"
)


class ActivationError(RuntimeError):
    """Fail-closed activation error."""


class AuthorizationError(ActivationError):
    """Invalid or missing one-time authorization."""


class IdentityError(ActivationError):
    """Frozen artifact identity mismatch."""


class RerunError(ActivationError):
    """Formal execution has already started."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            block = f.read(1024 * 1024)
            if not block:
                break
            h.update(block)

    return h.hexdigest()


def verify_identity(
    path: Path,
    expected: str,
    label: str,
) -> None:
    if not path.is_file():
        raise IdentityError(
            f"missing {label}: {path}"
        )

    actual = sha256_file(path)

    if actual != expected:
        raise IdentityError(
            f"{label} SHA-256 mismatch: "
            f"expected={expected} actual={actual}"
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
        raise RerunError(
            f"create-once path already exists: {path}"
        ) from exc

    with os.fdopen(
        fd,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())


def persist_json_create_once(
    path: Path,
    payload: Mapping[str, Any],
) -> None:
    create_once_text(
        path,
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n",
    )


def load_authorization() -> Mapping[str, Any]:
    if not AUTHORIZATION_FILE.is_file():
        raise AuthorizationError(
            "one-time POST-007 formal authorization "
            "does not exist"
        )

    with AUTHORIZATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as f:
        authorization = json.load(f)

    if not isinstance(authorization, Mapping):
        raise AuthorizationError(
            "formal authorization is not a mapping"
        )

    return authorization


def validate_authorization(
    authorization: Mapping[str, Any],
) -> None:
    required = {
        "stage": STAGE,
        "status": "authorized",
        "authorizationType":
            "one-time-formal-execution",
        "authorizationScope":
            "exactly-one-post007-formal-comparison",
        "formalExecutionAuthorized": True,
        "modelScoringAuthorized": True,
        "executionCountAuthorized": 1,
        "trainingAuthorized": False,
        "retrainingAuthorized": False,
        "formalDatasetSha256":
            EXPECTED_DATASET_SHA256,
        "acceptedBaselineSha256":
            EXPECTED_BASELINE_SHA256,
        "candidateSha256":
            EXPECTED_CANDIDATE_SHA256,
    }

    for key, expected in required.items():
        if authorization.get(key) != expected:
            raise AuthorizationError(
                f"authorization mismatch: {key}"
            )


def assert_activation_ready() -> Mapping[str, Any]:
    # This is the first and decisive construction lock.
    #
    # Nothing below this point can be reached in the current
    # revision because FORMAL_ACTIVATION_ARMED is frozen False.
    if FORMAL_ACTIVATION_ARMED is not True:
        raise ActivationError(
            "D0-POST-007 formal activation is DISARMED"
        )

    if EXPOSURE_MARKER.exists():
        raise RerunError(
            "POST-007 formal exposure already started"
        )

    if FORMAL_RESULT_DIR.exists():
        raise RerunError(
            "POST-007 formal result directory already exists"
        )

    authorization = load_authorization()
    validate_authorization(authorization)

    verify_identity(
        FORMAL_DATASET,
        EXPECTED_DATASET_SHA256,
        "sealed POST-007 formal dataset",
    )

    verify_identity(
        BASELINE,
        EXPECTED_BASELINE_SHA256,
        "accepted baseline",
    )

    verify_identity(
        CANDIDATE,
        EXPECTED_CANDIDATE_SHA256,
        "retained candidate",
    )

    return authorization


def execute_one_time_formal_comparison() -> Mapping[str, Any]:
    """
    Future one-time formal lifecycle.

    In this frozen revision the first call to
    assert_activation_ready() always fails closed because
    FORMAL_ACTIVATION_ARMED=False.

    Therefore none of the formal operations below are reachable.
    """

    authorization = assert_activation_ready()

    del authorization

    create_once_text(
        EXPOSURE_MARKER,
        "D0-POST-007 FORMAL_EXPOSURE_STARTED\n",
    )

    try:
        rows = frozen_dependencies.load_rows(
            FORMAL_DATASET
        )

        if not rows:
            raise ActivationError(
                "sealed formal dataset loaded zero rows"
            )

        baseline_result = (
            frozen_dependencies.score_checkpoint(
                BASELINE,
                rows,
            )
        )

        FORMAL_RESULT_DIR.mkdir(
            parents=True,
            exist_ok=False,
        )

        baseline_path = (
            FORMAL_RESULT_DIR /
            "BASELINE_RESULT.json"
        )

        persist_json_create_once(
            baseline_path,
            baseline_result,
        )

        candidate_result = (
            frozen_dependencies.score_checkpoint(
                CANDIDATE,
                rows,
            )
        )

        candidate_path = (
            FORMAL_RESULT_DIR /
            "CANDIDATE_RESULT.json"
        )

        persist_json_create_once(
            candidate_path,
            candidate_result,
        )

        with baseline_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            persisted_baseline = json.load(f)

        with candidate_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            persisted_candidate = json.load(f)

        adjudication = (
            frozen_dependencies.compare_results(
                persisted_baseline,
                persisted_candidate,
            )
        )

        persist_json_create_once(
            FORMAL_RESULT_DIR /
            "FINAL_ADJUDICATION.json",
            adjudication,
        )

        return {
            "stage": STAGE,
            "status": "completed",
            "mode": "one-time-formal-execution",
        }

    except Exception as exc:
        failure = {
            "stage": STAGE,
            "status": "failed-after-formal-exposure",
            "errorType": type(exc).__name__,
            "error": str(exc),
        }

        try:
            FORMAL_RESULT_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            persist_json_create_once(
                FORMAL_RESULT_DIR / "FAILURE.json",
                failure,
            )
        except Exception:
            pass

        raise


if __name__ == "__main__":
    raise SystemExit(
        "D0-POST-007 formal activation package is DISARMED. "
        "Direct execution is forbidden."
    )
