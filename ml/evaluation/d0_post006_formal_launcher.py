"""
D0-POST-006 separately controlled formal launcher.

CONSTRUCTION STATE ONLY.

This launcher binds the exact frozen authorization and revised
execution harness identities, but formal execution is deliberately
disabled in this construction revision.

This module:

- does not parse the formal dataset
- does not load either checkpoint
- does not score either checkpoint
- does not create FORMAL_EXPOSURE_STARTED
- does not invoke run_real_formal_execution
- does not perform training

A later launcher authorization / activation step is required after
static and synthetic auditing of this exact launcher identity.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


STAGE = "D0-POST-006"

AUTHORIZATION_STATE = Path(
    "local-evidence/"
    "d0-post006-formal-execution-gate-v2/"
    "FORMAL_EXECUTION_AUTHORIZATION_STATE.json"
)

HARNESS = Path(
    "ml/evaluation/d0_post006_execution_harness.py"
)

EVALUATOR = Path(
    "ml/evaluation/d0_post006_formal.py"
)

FORMAL_DATASET = Path(
    "ml/data/d0_post006_formal.jsonl"
)

BASELINE = Path(
    "local-checkpoints/"
    "d0-post003-capability-seed42.pt"
)

CANDIDATE = Path(
    "local-checkpoints/"
    "d0-post005-development-seed42-step120.pt"
)

EXPECTED_HARNESS_SHA256 = (
    "2fc3fe2a6b2d2247fd37aa2c47633f1e"
    "7fa68703473ca90b507c7c8b94cdf9e5"
)

EXPECTED_EVALUATOR_SHA256 = (
    "37f54a6ec2725d8df34c0331780c723f"
    "841a1d471364091406159b3915121e89"
)

EXPECTED_DATASET_SHA256 = (
    "202e63aee4f3a24c0746dc1a6a6136a"
    "6b33cf7ebfb3395f3e068d016985d189f"
)

EXPECTED_BASELINE_SHA256 = (
    "3b409092c120242fe4ed75113758390de"
    "e3e8e627507afdf7bcbc1bb5b3ccc06"
)

EXPECTED_CANDIDATE_SHA256 = (
    "4877d292fdd8e5428db250359dc9c57e"
    "bc4f4d1ccb2a329b94bdafd2c61569d9"
)


class LauncherError(RuntimeError):
    """Fail-closed D0-POST-006 launcher error."""


class LauncherLockedError(LauncherError):
    """Raised because launcher activation is not yet authorized."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def verify_identity(
    path: Path,
    expected_sha256: str,
    label: str,
) -> None:
    if not path.is_file():
        raise LauncherError(
            f"missing {label}: {path}"
        )

    actual = sha256_file(path)

    if actual != expected_sha256:
        raise LauncherError(
            f"{label} SHA-256 mismatch: "
            f"expected={expected_sha256} "
            f"actual={actual}"
        )


def load_authorization_metadata() -> Mapping[str, Any]:
    """
    Load authorization metadata only.

    This does not touch the formal dataset or checkpoints.
    """
    if not AUTHORIZATION_STATE.is_file():
        raise LauncherError(
            "missing frozen V2 authorization state"
        )

    with AUTHORIZATION_STATE.open(
        "r",
        encoding="utf-8",
    ) as stream:
        value = json.load(stream)

    if not isinstance(value, dict):
        raise LauncherError(
            "authorization state must be an object"
        )

    return value


def verify_static_binding() -> Mapping[str, Any]:
    """
    Verify launcher-to-frozen-resource identities.

    Dataset/checkpoint files are hashed as raw bytes only.
    They are not parsed or loaded as models.
    """
    verify_identity(
        HARNESS,
        EXPECTED_HARNESS_SHA256,
        "revised execution harness",
    )

    verify_identity(
        EVALUATOR,
        EXPECTED_EVALUATOR_SHA256,
        "formal evaluator",
    )

    verify_identity(
        FORMAL_DATASET,
        EXPECTED_DATASET_SHA256,
        "sealed POST-006 formal dataset",
    )

    verify_identity(
        BASELINE,
        EXPECTED_BASELINE_SHA256,
        "accepted POST-003 baseline",
    )

    verify_identity(
        CANDIDATE,
        EXPECTED_CANDIDATE_SHA256,
        "retained POST-005 candidate",
    )

    authorization = load_authorization_metadata()

    required = {
        "stage": STAGE,
        "status": "authorized",
        "authorizationVersion": 2,
        "authorizationType":
            "one-time-formal-execution",
        "authorizationScope":
            "exactly-one-formal-comparison-execution",
        "executionHarness": str(HARNESS),
        "executionHarnessSha256":
            EXPECTED_HARNESS_SHA256,
        "formalEvaluator": str(EVALUATOR),
        "formalEvaluatorSha256":
            EXPECTED_EVALUATOR_SHA256,
        "formalDataset": str(FORMAL_DATASET),
        "formalDatasetSha256":
            EXPECTED_DATASET_SHA256,
        "acceptedBaseline": str(BASELINE),
        "acceptedBaselineSha256":
            EXPECTED_BASELINE_SHA256,
        "candidate": str(CANDIDATE),
        "candidateSha256":
            EXPECTED_CANDIDATE_SHA256,
        "executionCountAuthorized": 1,
        "formalExecutionAuthorized": True,
        "modelScoringAuthorized": True,
        "formalExposureMarkerAuthorized": True,
        "trainingAuthorized": False,
        "retrainingAuthorized": False,
    }

    for key, expected in required.items():
        actual = authorization.get(key)

        if actual != expected:
            raise LauncherError(
                f"authorization binding mismatch for {key}: "
                f"expected={expected!r} "
                f"actual={actual!r}"
            )

    return authorization


def construct_execution_request() -> Mapping[str, Any]:
    """
    Construct metadata describing the authorized execution.

    This is data construction only.

    It deliberately does not invoke the harness real lifecycle.
    """
    authorization = verify_static_binding()

    return {
        "stage": STAGE,
        "launcherState": "constructed-not-activated",
        "authorizationVersion":
            authorization["authorizationVersion"],
        "executionCountAuthorized":
            authorization["executionCountAuthorized"],
        "executionHarness": str(HARNESS),
        "executionHarnessSha256":
            EXPECTED_HARNESS_SHA256,
        "formalEvaluator": str(EVALUATOR),
        "formalEvaluatorSha256":
            EXPECTED_EVALUATOR_SHA256,
        "formalDataset": str(FORMAL_DATASET),
        "formalDatasetSha256":
            EXPECTED_DATASET_SHA256,
        "acceptedBaseline": str(BASELINE),
        "acceptedBaselineSha256":
            EXPECTED_BASELINE_SHA256,
        "candidate": str(CANDIDATE),
        "candidateSha256":
            EXPECTED_CANDIDATE_SHA256,
        "formalExecutionInvoked": False,
        "formalRowsParsed": False,
        "checkpointLoaded": False,
        "modelScoringExecuted": False,
        "formalExposureStarted": False,
        "trainingExecuted": False,
    }


def execute() -> None:
    """
    Deliberately fail closed.

    Launcher activation has NOT been separately frozen.
    """
    raise LauncherLockedError(
        "D0-POST-006 formal launcher is constructed but "
        "NOT ACTIVATED. Formal execution remains unavailable "
        "through this launcher."
    )


if __name__ == "__main__":
    raise SystemExit(
        "D0-POST-006 formal launcher is CONSTRUCTED BUT LOCKED. "
        "Do not execute formal scoring."
    )
