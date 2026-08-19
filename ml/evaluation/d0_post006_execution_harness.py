"""
D0-POST-006 formal execution harness.

IMPORTANT
=========

This module defines the frozen execution lifecycle.

Real formal execution is intentionally disabled at implementation
time.

The harness may only operate in synthetic rehearsal mode until a
separate POST-006 formal-execution authorization has been frozen.

Importing this module:

- does not open the formal dataset
- does not load a checkpoint
- does not create an exposure marker
- does not score a model
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


STAGE = "D0-POST-006"

REAL_FORMAL_DATASET = Path("ml/data/d0_post006_formal.jsonl")

HISTORICAL_FORMAL_DATASET = Path(
    "ml/data/d0_post003_formal.jsonl"
)

REAL_BASELINE = Path(
    "local-checkpoints/d0-post003-capability-seed42.pt"
)

REAL_CANDIDATE = Path(
    "local-checkpoints/"
    "d0-post005-development-seed42-step120.pt"
)

REAL_DATASET_SHA256 = (
    "202e63aee4f3a24c0746dc1a6a6136a6b33cf7ebfb3395f3e068d016985d189f"
)

REAL_BASELINE_SHA256 = (
    "3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06"
)

REAL_CANDIDATE_SHA256 = (
    "4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9"
)

REAL_EXPOSURE_MARKER = Path(
    "local-evidence/"
    "d0-post006-formal-execution/"
    "FORMAL_EXPOSURE_STARTED"
)

REAL_RESULT_DIR = Path(
    "local-evidence/d0-post006-formal-execution"
)


class HarnessError(RuntimeError):
    """Fail-closed execution-harness error."""


class AuthorizationError(HarnessError):
    """Raised when real formal execution is not authorized."""


class RerunError(HarnessError):
    """Raised if a one-time execution is attempted again."""


class IdentityError(HarnessError):
    """Raised when a frozen artifact identity changes."""


class EvidenceExistsError(HarnessError):
    """Raised when create-once evidence already exists."""


@dataclass(frozen=True)
class HarnessPaths:
    dataset: Path
    baseline: Path
    candidate: Path
    exposure_marker: Path
    result_dir: Path


@dataclass(frozen=True)
class HarnessIdentities:
    dataset_sha256: str
    baseline_sha256: str
    candidate_sha256: str


@dataclass(frozen=True)
class HarnessDependencies:
    load_rows: Callable[[Path], Sequence[Mapping[str, Any]]]
    score_checkpoint: Callable[
        [Path, Sequence[Mapping[str, Any]]],
        Mapping[str, Any],
    ]
    compare_results: Callable[
        [Mapping[str, Any], Mapping[str, Any]],
        Mapping[str, Any],
    ]


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
    expected_sha256: str,
    label: str,
) -> None:
    if not path.is_file():
        raise IdentityError(f"missing {label}: {path}")

    actual = sha256_file(path)

    if actual != expected_sha256:
        raise IdentityError(
            f"{label} SHA-256 mismatch: "
            f"expected={expected_sha256} actual={actual}"
        )


def assert_real_execution_authorized(
    authorization: Mapping[str, Any] | None,
) -> None:
    """
    Validate a supplied frozen one-time execution authorization.

    This function validates authorization metadata only.

    It does not load the formal dataset, load checkpoints,
    create the exposure marker, or score a model.
    """
    if authorization is None:
        raise AuthorizationError(
            "missing frozen D0-POST-006 formal execution authorization"
        )

    required = {
        "stage": STAGE,
        "status": "authorized",
        "authorizationType": "one-time-formal-execution",
        "authorizationScope":
            "exactly-one-formal-comparison-execution",
        "formalDataset": str(REAL_FORMAL_DATASET),
        "formalDatasetSha256": REAL_DATASET_SHA256,
        "acceptedBaseline": str(REAL_BASELINE),
        "acceptedBaselineSha256": REAL_BASELINE_SHA256,
        "candidate": str(REAL_CANDIDATE),
        "candidateSha256": REAL_CANDIDATE_SHA256,
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
            raise AuthorizationError(
                f"authorization mismatch for {key}: "
                f"expected={expected!r} actual={actual!r}"
            )

    required_true = (
        "baselineMustBeScoredFirst",
        "baselineMustBePersistedBeforeCandidateScoring",
        "candidateMustBePersistedBeforeComparison",
        "comparisonMustUsePersistedResults",
        "exposureMarkerRequired",
        "exposureMarkerMustPrecedeFormalRowLoad",
        "rerunForbiddenAfterExposureStarts",
        "overwriteForbidden",
        "failureEvidenceRequired",
        "failureMustPreservePriorEvidence",
    )

    for key in required_true:
        if authorization.get(key) is not True:
            raise AuthorizationError(
                f"required authorization protection is not true: {key}"
            )

    required_false = (
        "historicalFormalDatasetMayBeOpened",
        "historicalFormalDatasetMayBeScored",
        "formalDatasetMayBePrinted",
        "formalExpectedResponsesMayBePrinted",
        "formalDatasetMayBeUsedForTraining",
        "formalDatasetMayBeUsedForDevelopment",
        "formalDatasetMayBeUsedForCandidateSelection",
        "formalDatasetMayBeUsedForThresholdTuning",
    )

    for key in required_false:
        if authorization.get(key) is not False:
            raise AuthorizationError(
                f"required prohibition is not false: {key}"
            )



def create_once_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        fd = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o444,
        )
    except FileExistsError as exc:
        raise EvidenceExistsError(
            f"create-once evidence already exists: {path}"
        ) from exc

    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())


def persist_json_create_once(
    path: Path,
    payload: Mapping[str, Any],
) -> None:
    text = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
    ) + "\n"

    create_once_text(path, text)


def validate_synthetic_rows(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    if not rows:
        raise HarnessError("synthetic row set is empty")

    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise HarnessError(
                f"synthetic row {index} is not a mapping"
            )

        for key in ("family", "instruction", "response"):
            value = row.get(key)

            if not isinstance(value, str) or not value:
                raise HarnessError(
                    f"synthetic row {index} invalid field: {key}"
                )


def run_synthetic_lifecycle(
    *,
    paths: HarnessPaths,
    dependencies: HarnessDependencies,
    expected_identities: HarnessIdentities | None = None,
) -> Mapping[str, Any]:
    """
    Exercise the execution lifecycle using synthetic artifacts only.

    The caller MUST supply synthetic paths and synthetic dependencies.

    This function refuses all known real POST-006 formal paths.
    """

    forbidden = {
        REAL_FORMAL_DATASET.resolve(),
        HISTORICAL_FORMAL_DATASET.resolve(),
        REAL_BASELINE.resolve(),
        REAL_CANDIDATE.resolve(),
        REAL_EXPOSURE_MARKER.resolve(),
        REAL_RESULT_DIR.resolve(),
    }

    supplied = {
        paths.dataset.resolve(),
        paths.baseline.resolve(),
        paths.candidate.resolve(),
        paths.exposure_marker.resolve(),
        paths.result_dir.resolve(),
    }

    collision = forbidden.intersection(supplied)

    if collision:
        raise HarnessError(
            "synthetic rehearsal attempted to use a real "
            f"POST-006 path: {sorted(map(str, collision))}"
        )

    if paths.exposure_marker.exists():
        raise RerunError(
            "synthetic exposure marker already exists"
        )

    if paths.result_dir.exists():
        raise RerunError(
            "synthetic result directory already exists"
        )

    if expected_identities is not None:
        verify_identity(
            paths.dataset,
            expected_identities.dataset_sha256,
            "synthetic dataset",
        )
        verify_identity(
            paths.baseline,
            expected_identities.baseline_sha256,
            "synthetic baseline",
        )
        verify_identity(
            paths.candidate,
            expected_identities.candidate_sha256,
            "synthetic candidate",
        )

    # Exposure begins immediately before first row load.
    create_once_text(
        paths.exposure_marker,
        "SYNTHETIC_EXPOSURE_STARTED\n",
    )

    rows = dependencies.load_rows(paths.dataset)

    validate_synthetic_rows(rows)

    baseline_result = dependencies.score_checkpoint(
        paths.baseline,
        rows,
    )

    paths.result_dir.mkdir(parents=True, exist_ok=False)

    baseline_path = paths.result_dir / "BASELINE_RESULT.json"

    persist_json_create_once(
        baseline_path,
        baseline_result,
    )

    candidate_result = dependencies.score_checkpoint(
        paths.candidate,
        rows,
    )

    candidate_path = paths.result_dir / "CANDIDATE_RESULT.json"

    persist_json_create_once(
        candidate_path,
        candidate_result,
    )

    # Comparison consumes persisted evidence.
    with baseline_path.open("r", encoding="utf-8") as f:
        persisted_baseline = json.load(f)

    with candidate_path.open("r", encoding="utf-8") as f:
        persisted_candidate = json.load(f)

    adjudication = dependencies.compare_results(
        persisted_baseline,
        persisted_candidate,
    )

    persist_json_create_once(
        paths.result_dir / "FINAL_ADJUDICATION.json",
        adjudication,
    )

    return {
        "stage": STAGE,
        "mode": "synthetic-only",
        "exposureMarkerCreated": True,
        "baselinePersistedBeforeCandidate": True,
        "candidatePersistedBeforeComparison": True,
        "comparisonUsedPersistedResults": True,
        "finalAdjudicationPersisted": True,
    }


def run_real_formal_execution(
    *,
    authorization: Mapping[str, Any],
    dependencies: HarnessDependencies,
) -> Mapping[str, Any]:
    """
    Authorization-bound real lifecycle.

    IMPORTANT:

    This function is intentionally not invoked by this revision
    step. A later separately authorized launcher must supply the
    real dependencies and call it exactly once.

    The exposure marker is created immediately before the first
    formal-row load.
    """
    assert_real_execution_authorized(authorization)

    paths = HarnessPaths(
        dataset=REAL_FORMAL_DATASET,
        baseline=REAL_BASELINE,
        candidate=REAL_CANDIDATE,
        exposure_marker=REAL_EXPOSURE_MARKER,
        result_dir=REAL_RESULT_DIR,
    )

    identities = HarnessIdentities(
        dataset_sha256=REAL_DATASET_SHA256,
        baseline_sha256=REAL_BASELINE_SHA256,
        candidate_sha256=REAL_CANDIDATE_SHA256,
    )

    if paths.exposure_marker.exists():
        raise RerunError(
            "POST-006 formal exposure has already started; "
            "rerun is forbidden"
        )

    if paths.result_dir.exists():
        raise RerunError(
            "POST-006 formal result directory already exists"
        )

    verify_identity(
        paths.dataset,
        identities.dataset_sha256,
        "sealed POST-006 formal dataset",
    )
    verify_identity(
        paths.baseline,
        identities.baseline_sha256,
        "accepted POST-003 baseline",
    )
    verify_identity(
        paths.candidate,
        identities.candidate_sha256,
        "retained POST-005 candidate",
    )

    if HISTORICAL_FORMAL_DATASET.resolve() == paths.dataset.resolve():
        raise HarnessError(
            "historical formal dataset cannot be used"
        )

    create_once_text(
        paths.exposure_marker,
        "D0-POST-006 FORMAL_EXPOSURE_STARTED\\n",
    )

    try:
        rows = dependencies.load_rows(paths.dataset)

        if not rows:
            raise HarnessError(
                "sealed POST-006 formal dataset loaded zero rows"
            )

        baseline_result = dependencies.score_checkpoint(
            paths.baseline,
            rows,
        )

        paths.result_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        baseline_path = (
            paths.result_dir / "BASELINE_RESULT.json"
        )
        persist_json_create_once(
            baseline_path,
            baseline_result,
        )

        candidate_result = dependencies.score_checkpoint(
            paths.candidate,
            rows,
        )

        candidate_path = (
            paths.result_dir / "CANDIDATE_RESULT.json"
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

        adjudication = dependencies.compare_results(
            persisted_baseline,
            persisted_candidate,
        )

        persist_json_create_once(
            paths.result_dir / "FINAL_ADJUDICATION.json",
            adjudication,
        )

        return {
            "stage": STAGE,
            "mode": "one-time-formal-execution",
            "exposureMarkerCreated": True,
            "baselinePersistedBeforeCandidate": True,
            "candidatePersistedBeforeComparison": True,
            "comparisonUsedPersistedResults": True,
            "finalAdjudicationPersisted": True,
        }

    except Exception as exc:
        failure_payload = {
            "stage": STAGE,
            "status": "failed-after-formal-exposure",
            "errorType": type(exc).__name__,
            "error": str(exc),
        }

        try:
            paths.result_dir.mkdir(
                parents=True,
                exist_ok=True,
            )
            persist_json_create_once(
                paths.result_dir / "FAILURE.json",
                failure_payload,
            )
        except Exception:
            pass

        raise



if __name__ == "__main__":
    raise SystemExit(
        "D0-POST-006 revised harness contains an authorization-bound "
        "real lifecycle but has no direct real-execution CLI. "
        "Use only a separately frozen and authorized launcher."
    )
