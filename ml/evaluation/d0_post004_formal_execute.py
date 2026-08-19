from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


EXPECTED_AUTH_SHA256 = (
    "19d5c1f267030f68c26ebec778d5a552c"
    "4234479eac911dd58a77667c31d2f7e"
)

EXPECTED_FORMAL_SHA256 = (
    "29e891946b13be32b94cb1abe46e2a969"
    "989a39b76e65a126d3798a18e6184d9"
)

EXPECTED_ADAPTER_SHA256 = (
    "6eb73c231750125a13d151d75fd02a091"
    "afea6cce28ad8990d171641df744f41"
)

EXPECTED_BACKEND_SHA256 = (
    "a6a0018596a7de18bec74145c761cec79"
    "cbb88146d57b4366acce4c2e567530b"
)

EXPECTED_DATA_SHA256 = (
    "28d95ae79d92fe767cf1fb16b984ccb3"
    "c33e79616d7cf20666bd6763ec2b7115"
)

EXPECTED_BASELINE_SHA256 = (
    "3b409092c120242fe4ed75113758390de"
    "e3e8e627507afdf7bcbc1bb5b3ccc06"
)

EXPECTED_CANDIDATE_SHA256 = (
    "ae927ca3e779a0eda7c8fff025fc7cfd"
    "3a41568cb236148f444c75507ef35441"
)


ROOT = Path(__file__).resolve().parents[2]

AUTH = (
    ROOT
    / "local-evidence"
    / "d0-post004-formal"
    / "FORMAL_EXECUTION_AUTHORIZATION.md"
)

FORMAL = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post004_formal.py"
)

ADAPTER = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post004_formal_adapter.py"
)

BACKEND = (
    ROOT
    / "ml"
    / "evaluation"
    / "d0_post003_dev.py"
)

DATA = (
    ROOT
    / "ml"
    / "data"
    / "d0_post003_formal.jsonl"
)

BASELINE = (
    ROOT
    / "local-checkpoints"
    / "d0-post003-capability-seed42.pt"
)

CANDIDATE = (
    ROOT
    / "local-checkpoints"
    / "d0-post004-capability-seed42-step120.pt"
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


def require_sha256(
    path: Path,
    expected: str,
) -> None:
    actual = sha256_file(path)

    if actual != expected:
        raise RuntimeError(
            f"Identity mismatch for {path}: "
            f"{actual}"
        )


def load_module(
    name: str,
    path: Path,
):
    spec = importlib.util.spec_from_file_location(
        name,
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"Unable to load module: {path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def verify_frozen_inputs() -> None:
    require_sha256(
        AUTH,
        EXPECTED_AUTH_SHA256,
    )
    require_sha256(
        FORMAL,
        EXPECTED_FORMAL_SHA256,
    )
    require_sha256(
        ADAPTER,
        EXPECTED_ADAPTER_SHA256,
    )
    require_sha256(
        BACKEND,
        EXPECTED_BACKEND_SHA256,
    )
    require_sha256(
        DATA,
        EXPECTED_DATA_SHA256,
    )
    require_sha256(
        BASELINE,
        EXPECTED_BASELINE_SHA256,
    )
    require_sha256(
        CANDIDATE,
        EXPECTED_CANDIDATE_SHA256,
    )


def dry_validate() -> dict[str, Any]:
    verify_frozen_inputs()

    formal = load_module(
        "d0_post004_formal_controlled",
        FORMAL,
    )

    adapter = load_module(
        "d0_post004_formal_adapter_controlled",
        ADAPTER,
    )

    if not callable(
        getattr(formal, "compare_results", None)
    ):
        raise RuntimeError(
            "Formal compare_results unavailable."
        )

    if not callable(
        getattr(
            formal,
            "validate_dataset_structure",
            None,
        )
    ):
        raise RuntimeError(
            "Formal dataset validator unavailable."
        )

    if not callable(
        getattr(adapter, "adapt_scoring_result", None)
    ):
        raise RuntimeError(
            "Formal adapter unavailable."
        )

    return {
        "status": "ready",
        "formalScoringExecuted": False,
        "authorizationSha256":
            sha256_file(AUTH),
        "formalEvaluatorSha256":
            sha256_file(FORMAL),
        "adapterSha256":
            sha256_file(ADAPTER),
        "backendSha256":
            sha256_file(BACKEND),
        "datasetSha256":
            sha256_file(DATA),
        "baselineSha256":
            sha256_file(BASELINE),
        "candidateSha256":
            sha256_file(CANDIDATE),
    }


def execute() -> dict[str, Any]:
    raise RuntimeError(
        "Controlled POST-004 formal execution "
        "is not unlocked in this wrapper build."
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
            "Only --dry-validate is permitted "
            "before the one-time execution unlock."
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
