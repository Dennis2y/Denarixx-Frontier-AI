from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ML_ROOT = ROOT / "ml"

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from evaluation import d0_post006_dependencies as dependencies
from evaluation import d0_post006_execution_harness as harness
from evaluation import d0_post006_formal as formal


STAGE = "D0-POST-006"

ADAPTER_PATH = (
    ROOT / "ml/evaluation/d0_post006_dependencies.py"
)
HARNESS_PATH = (
    ROOT / "ml/evaluation/d0_post006_execution_harness.py"
)
COMPARATOR_PATH = (
    ROOT / "ml/evaluation/d0_post006_formal.py"
)

EXPECTED_ADAPTER_SHA256 = (
    "d3e34b57fcc48dc8c3f31b37195ca5c89d69bd7b2bcf67a44466c8b5e5631dce"
)

EXPECTED_HARNESS_SHA256 = (
    "2fc3fe2a6b2d2247fd37aa2c47633f1e7fa68703473ca90b507c7c8b94cdf9e5"
)

EXPECTED_COMPARATOR_SHA256 = (
    "37f54a6ec2725d8df34c0331780c723f841a1d471364091406159b3915121e89"
)

EXPECTED_DATASET_SHA256 = (
    "202e63aee4f3a24c0746dc1a6a6136a6b33cf7ebfb3395f3e068d016985d189f"
)

EXPECTED_BASELINE_SHA256 = (
    "3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06"
)

EXPECTED_CANDIDATE_SHA256 = (
    "4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9"
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


def require_identity(
    path: Path,
    expected: str,
    label: str,
) -> None:
    actual = sha256_file(path)

    if actual != expected:
        raise RuntimeError(
            f"{label} identity mismatch: "
            f"expected {expected}, got {actual}"
        )


def verify_source_identities() -> None:
    require_identity(
        ADAPTER_PATH,
        EXPECTED_ADAPTER_SHA256,
        "POST-006 dependency adapter",
    )

    require_identity(
        HARNESS_PATH,
        EXPECTED_HARNESS_SHA256,
        "POST-006 execution harness",
    )

    require_identity(
        COMPARATOR_PATH,
        EXPECTED_COMPARATOR_SHA256,
        "POST-006 comparator",
    )


def verify_real_artifact_identities_without_parsing() -> None:
    require_identity(
        ROOT / harness.REAL_FORMAL_DATASET,
        EXPECTED_DATASET_SHA256,
        "sealed POST-006 formal dataset",
    )

    require_identity(
        ROOT / harness.REAL_BASELINE,
        EXPECTED_BASELINE_SHA256,
        "accepted POST-003 baseline",
    )

    require_identity(
        ROOT / harness.REAL_CANDIDATE,
        EXPECTED_CANDIDATE_SHA256,
        "retained POST-005 candidate",
    )


def verify_dependency_contract() -> None:
    load_sig = inspect.signature(
        dependencies.load_rows
    )

    score_sig = inspect.signature(
        dependencies.score_checkpoint
    )

    compare_sig = inspect.signature(
        dependencies.compare_results
    )

    if len(load_sig.parameters) != 1:
        raise RuntimeError(
            "load_rows dependency contract changed"
        )

    if len(score_sig.parameters) != 2:
        raise RuntimeError(
            "score_checkpoint dependency contract changed"
        )

    if len(compare_sig.parameters) != 2:
        raise RuntimeError(
            "compare_results dependency contract changed"
        )

    if set(formal.EXPECTED_FAMILIES) != {
        "echo",
        "boolean",
        "plural",
        "opposite",
        "world_fact",
    }:
        raise RuntimeError(
            "POST-006 family contract changed"
        )


def verify_zero_exposure() -> None:
    exposure = ROOT / harness.REAL_EXPOSURE_MARKER
    result_dir = ROOT / harness.REAL_RESULT_DIR

    if exposure.exists():
        raise RuntimeError(
            "POST-006 formal exposure has already started"
        )

    if result_dir.exists():
        raise RuntimeError(
            "POST-006 formal result directory already exists"
        )


def dry_validate() -> dict[str, Any]:
    """
    Pre-execution validation only.

    IMPORTANT:
    - hashes sealed dataset bytes without parsing rows
    - hashes checkpoint bytes without loading models
    - does not call load_rows
    - does not call score_checkpoint
    - does not call run_real_formal_execution
    - does not create the exposure marker
    """

    verify_zero_exposure()
    verify_source_identities()
    verify_dependency_contract()
    verify_real_artifact_identities_without_parsing()
    verify_zero_exposure()

    return {
        "stage": STAGE,
        "status": "ready-for-separate-one-time-execution",
        "formalExposureStarted": False,
        "formalRowsParsed": False,
        "checkpointLoaded": False,
        "modelScoringExecuted": False,
        "sourceIdentitiesVerified": True,
        "sealedArtifactIdentitiesVerifiedByHashOnly": True,
        "dependencyContractVerified": True,
        "realExecutionInvoked": False,
    }


def build_dependencies() -> harness.HarnessDependencies:
    return harness.HarnessDependencies(
        load_rows=dependencies.load_rows,
        score_checkpoint=dependencies.score_checkpoint,
        compare_results=dependencies.compare_results,
    )


def execute_once(
    authorization: dict[str, Any],
) -> dict[str, Any]:
    """
    REAL ONE-TIME EXECUTION ENTRYPOINT.

    This function exists for the separately authorized execution
    step. It MUST NOT be called by --dry-validate.
    """

    verify_zero_exposure()
    verify_source_identities()
    verify_dependency_contract()
    verify_real_artifact_identities_without_parsing()

    bound = build_dependencies()

    return dict(
        harness.run_real_formal_execution(
            authorization=authorization,
            dependencies=bound,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-validate",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.dry_validate:
        raise RuntimeError(
            "Real POST-006 formal execution is locked. "
            "This launcher currently permits only "
            "--dry-validate from the command line."
        )

    result = dry_validate()

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
