"""
D0-POST-007 formal execution harness.

IMPORTANT
=========

This revision constructs the POST-007 execution lifecycle while
keeping real formal execution mechanically disabled.

Importing this module:

- does not open the sealed formal dataset
- does not load a checkpoint
- does not create FORMAL_EXPOSURE_STARTED
- does not score a model
- does not perform formal comparison

Synthetic lifecycle rehearsal is supported with caller-supplied
synthetic artifacts and dependencies.

Real formal execution requires a later, separately frozen
authorization/activation revision.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


STAGE = "D0-POST-007"

REAL_FORMAL_EXECUTION_ENABLED = False

REAL_FORMAL_DATASET = Path(
    "ml/data/d0_post007_formal.jsonl"
)

HISTORICAL_FORMAL_DATASETS = (
    Path("ml/data/d0_post003_formal.jsonl"),
    Path("ml/data/d0_post006_formal.jsonl"),
)

REAL_BASELINE = Path(
    "local-checkpoints/d0-post003-capability-seed42.pt"
)

REAL_CANDIDATE = Path(
    "local-checkpoints/"
    "d0-post005-development-seed42-step120.pt"
)

REAL_DATASET_SHA256 = (
    "f0f5c88524c4f0b78f4ebbd23548006103aa3e4116cc4a3df34493712b07fb0c"
)

REAL_BASELINE_SHA256 = (
    "3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06"
)

REAL_CANDIDATE_SHA256 = (
    "4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9"
)

REAL_EXPOSURE_MARKER = Path(
    "local-evidence/"
    "d0-post007-formal-execution/"
    "FORMAL_EXPOSURE_STARTED"
)

REAL_RESULT_DIR = Path(
    "local-evidence/d0-post007-formal-execution"
)


class HarnessError(RuntimeError):
    """Fail-closed execution-harness error."""


class AuthorizationError(HarnessError):
    """Raised when real formal execution is not authorized."""


class ActivationError(HarnessError):
    """Raised while real formal execution is mechanically disabled."""


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
    load_rows: Callable[
        [Path],
        Sequence[Mapping[str, Any]],
    ]
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
        raise IdentityError(
            f"missing {label}: {path}"
        )

    actual = sha256_file(path)

    if actual != expected_sha256:
        raise IdentityError(
            f"{label} SHA-256 mismatch: "
            f"expected={expected_sha256} "
            f"actual={actual}"
        )


def assert_real_execution_authorized(
    authorization: Mapping[str, Any] | None,
) -> None:
    """
    Construction-revision authorization guard.

    Real POST-007 formal execution is mechanically disabled.

    This function intentionally rejects every request during this
    revision, including authorization-shaped metadata.

    A later separately audited activation revision must replace
    this construction lock only after an exact formal execution
    authorization has been frozen.
    """

    del authorization

    if REAL_FORMAL_EXECUTION_ENABLED is not False:
        raise ActivationError(
            "invalid construction state: real execution flag changed"
        )

    raise AuthorizationError(
        "D0-POST-007 real formal execution is mechanically disabled "
        "in this harness revision"
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
        raise EvidenceExistsError(
            f"create-once evidence already exists: {path}"
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
    text = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
    ) + "\n"

    create_once_text(
        path,
        text,
    )


def validate_synthetic_rows(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    if not rows:
        raise HarnessError(
            "synthetic row set is empty"
        )

    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise HarnessError(
                f"synthetic row {index} is not a mapping"
            )

        for key in (
            "family",
            "instruction",
            "response",
        ):
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
    Exercise the lifecycle using synthetic artifacts only.

    The caller must supply synthetic paths and dependencies.

    All known POST-007 real paths and historical formal dataset
    paths are forbidden.
    """

    forbidden = {
        REAL_FORMAL_DATASET.resolve(),
        REAL_BASELINE.resolve(),
        REAL_CANDIDATE.resolve(),
        REAL_EXPOSURE_MARKER.resolve(),
        REAL_RESULT_DIR.resolve(),
    }

    forbidden.update(
        path.resolve()
        for path in HISTORICAL_FORMAL_DATASETS
    )

    supplied = {
        paths.dataset.resolve(),
        paths.baseline.resolve(),
        paths.candidate.resolve(),
        paths.exposure_marker.resolve(),
        paths.result_dir.resolve(),
    }

    collision = forbidden.intersection(
        supplied
    )

    if collision:
        raise HarnessError(
            "synthetic rehearsal attempted to use a real or "
            "historical formal path: "
            f"{sorted(map(str, collision))}"
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

    create_once_text(
        paths.exposure_marker,
        "SYNTHETIC_EXPOSURE_STARTED\n",
    )

    rows = dependencies.load_rows(
        paths.dataset
    )

    validate_synthetic_rows(rows)

    baseline_result = (
        dependencies.score_checkpoint(
            paths.baseline,
            rows,
        )
    )

    paths.result_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    baseline_path = (
        paths.result_dir /
        "BASELINE_RESULT.json"
    )

    persist_json_create_once(
        baseline_path,
        baseline_result,
    )

    candidate_result = (
        dependencies.score_checkpoint(
            paths.candidate,
            rows,
        )
    )

    candidate_path = (
        paths.result_dir /
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
        dependencies.compare_results(
            persisted_baseline,
            persisted_candidate,
        )
    )

    persist_json_create_once(
        paths.result_dir /
        "FINAL_ADJUDICATION.json",
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
    authorization: Mapping[str, Any] | None,
    dependencies: HarnessDependencies,
) -> Mapping[str, Any]:
    """
    Real POST-007 lifecycle placeholder.

    Real execution is mechanically disabled in this revision.

    No formal dataset path is opened and no dependency function is
    called because the construction lock is checked first.
    """

    del dependencies

    assert_real_execution_authorized(
        authorization
    )

    # Unreachable by construction.
    raise ActivationError(
        "unreachable real formal execution path"
    )


if __name__ == "__main__":
    raise SystemExit(
        "D0-POST-007 harness has no direct real-execution CLI. "
        "Real formal execution is mechanically disabled. "
        "Use only synthetic rehearsal until a separately frozen "
        "authorization and activation revision exists."
    )
