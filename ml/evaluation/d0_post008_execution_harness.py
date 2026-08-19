"""
D0-POST-008 execution lifecycle harness.

PRE-FORMAL IMPLEMENTATION.

This module establishes the corrected filesystem lifecycle discovered
after the consumed D0-POST-007 execution.

Importing this module does NOT:

- open any formal dataset;
- load any real checkpoint;
- execute model inference;
- execute model scoring;
- authorize formal execution;
- create a real formal exposure marker.

Real POST-008 execution is mechanically disabled.

Only caller-supplied synthetic artifacts may be exercised through
run_synthetic_lifecycle().
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


STAGE = "D0-POST-008"

REAL_FORMAL_EXECUTION_ENABLED = False

REAL_RESULT_DIR = Path(
    "local-evidence/d0-post008-formal-execution"
)

REAL_EXPOSURE_MARKER = (
    REAL_RESULT_DIR / "FORMAL_EXPOSURE_STARTED"
)

# These are reserved future real paths. The formal dataset intentionally
# does not need to exist at this stage.
REAL_FORMAL_DATASET = Path(
    "ml/data/d0_post008_formal.jsonl"
)

REAL_BASELINE = Path(
    "local-checkpoints/d0-post003-capability-seed42.pt"
)

REAL_CANDIDATE = Path(
    "local-checkpoints/"
    "d0-post005-development-seed42-step120.pt"
)


class HarnessError(RuntimeError):
    """Base fail-closed harness error."""


class RerunError(HarnessError):
    """Raised when execution evidence already exists."""


class TopologyError(HarnessError):
    """Raised when exposure/result topology is incorrect."""


class IdentityError(HarnessError):
    """Raised when a supplied artifact identity changes."""


class EvidenceExistsError(HarnessError):
    """Raised when create-once evidence already exists."""


class RealPathCollisionError(HarnessError):
    """Raised when synthetic execution reaches reserved real paths."""


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


class Dependencies(Protocol):
    def load_rows(
        self,
        dataset: Path,
    ) -> Sequence[Mapping[str, Any]]:
        ...

    def score_checkpoint(
        self,
        checkpoint: Path,
        rows: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        ...

    def compare_results(
        self,
        baseline: Mapping[str, Any],
        candidate: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        ...


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def verify_identity(
    path: Path,
    expected_sha256: str,
) -> None:
    actual = sha256_file(path)

    if actual != expected_sha256:
        raise IdentityError(
            "artifact identity mismatch: "
            f"{path}; expected={expected_sha256}; "
            f"actual={actual}"
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


def persist_json_create_once(
    path: Path,
    value: Mapping[str, Any],
) -> None:
    create_once_text(
        path,
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def read_json(
    path: Path,
) -> Mapping[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(value, dict):
        raise HarnessError(
            f"expected JSON object: {path}"
        )

    return value


def assert_exact_topology(
    paths: HarnessPaths,
) -> None:
    if (
        paths.exposure_marker.parent.resolve()
        != paths.result_dir.resolve()
    ):
        raise TopologyError(
            "POST-008 requires exposure_marker.parent "
            "== result_dir"
        )


def assert_no_real_path_collision(
    paths: HarnessPaths,
) -> None:
    forbidden = {
        REAL_FORMAL_DATASET.resolve(),
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
        rendered = ", ".join(
            sorted(str(path) for path in collision)
        )

        raise RealPathCollisionError(
            "synthetic lifecycle collided with "
            f"reserved real path(s): {rendered}"
        )


def assert_pre_exposure_state(
    paths: HarnessPaths,
) -> None:
    if paths.exposure_marker.exists():
        raise RerunError(
            "synthetic exposure marker already exists"
        )

    if paths.result_dir.exists():
        raise RerunError(
            "synthetic result directory already exists"
        )


def run_synthetic_lifecycle(
    *,
    paths: HarnessPaths,
    dependencies: Dependencies,
    expected_identities: HarnessIdentities | None = None,
) -> Mapping[str, Any]:
    """
    Execute the corrected POST-008 lifecycle using synthetic artifacts.

    The exact topology is mandatory:

        exposure_marker.parent == result_dir

    Exposure-marker persistence creates result_dir as a side effect.
    There is intentionally NO subsequent result_dir.mkdir(
    exist_ok=False
    ) operation.
    """

    assert_exact_topology(paths)
    assert_no_real_path_collision(paths)
    assert_pre_exposure_state(paths)

    if expected_identities is not None:
        verify_identity(
            paths.dataset,
            expected_identities.dataset_sha256,
        )
        verify_identity(
            paths.baseline,
            expected_identities.baseline_sha256,
        )
        verify_identity(
            paths.candidate,
            expected_identities.candidate_sha256,
        )

    # IMPORTANT:
    # create_once_text creates the parent result directory.
    #
    # DO NOT add:
    #
    #     paths.result_dir.mkdir(exist_ok=False)
    #
    # anywhere after this point.
    create_once_text(
        paths.exposure_marker,
        f"{STAGE} SYNTHETIC_EXPOSURE_STARTED\n",
    )

    try:
        rows = dependencies.load_rows(
            paths.dataset
        )

        if not rows:
            raise HarnessError(
                "synthetic dataset contains no rows"
            )

        baseline_result = dict(
            dependencies.score_checkpoint(
                paths.baseline,
                rows,
            )
        )

        baseline_path = (
            paths.result_dir /
            "BASELINE_RESULT.json"
        )

        persist_json_create_once(
            baseline_path,
            baseline_result,
        )

        candidate_result = dict(
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

        persisted_baseline = read_json(
            baseline_path
        )

        persisted_candidate = read_json(
            candidate_path
        )

        adjudication = dict(
            dependencies.compare_results(
                persisted_baseline,
                persisted_candidate,
            )
        )

        final_path = (
            paths.result_dir /
            "FINAL_ADJUDICATION.json"
        )

        persist_json_create_once(
            final_path,
            adjudication,
        )

        return {
            "stage": STAGE,
            "status": "completed",
            "mode": "synthetic-only",
            "exposureMarkerCreated": True,
            "exactTopology": True,
        }

    except Exception as exc:
        failure = {
            "stage": STAGE,
            "status":
                "failed-after-synthetic-exposure",
            "errorType": type(exc).__name__,
            "error": str(exc),
        }

        # Parent may already exist because exposure marker was created.
        # exist_ok=True is permitted only for failure-evidence handling.
        paths.result_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        failure_path = (
            paths.result_dir / "FAILURE.json"
        )

        if not failure_path.exists():
            persist_json_create_once(
                failure_path,
                failure,
            )

        raise


def run_real_formal_execution() -> None:
    """
    Real POST-008 execution remains mechanically disabled.
    """

    if not REAL_FORMAL_EXECUTION_ENABLED:
        raise HarnessError(
            "D0-POST-008 real formal execution "
            "is not authorized"
        )

    raise HarnessError(
        "D0-POST-008 real formal execution "
        "implementation is intentionally absent"
    )
