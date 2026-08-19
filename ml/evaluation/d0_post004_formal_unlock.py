from __future__ import annotations

import hashlib
from pathlib import Path


EXPECTED = {
    "wrapper": (
        "ml/evaluation/d0_post004_formal_execute.py",
        "91070c482ec8ccddb6c008b9d45fc9c18a6fd0fc930d258b34eb5cd65fd8418f",
    ),
    "formal": (
        "ml/evaluation/d0_post004_formal.py",
        "29e891946b13be32b94cb1abe46e2a969989a39b76e65a126d3798a18e6184d9",
    ),
    "adapter": (
        "ml/evaluation/d0_post004_formal_adapter.py",
        "6eb73c231750125a13d151d75fd02a091afea6cce28ad8990d171641df744f41",
    ),
    "backend": (
        "ml/evaluation/d0_post003_dev.py",
        "a6a0018596a7de18bec74145c761cec79cbb88146d57b4366acce4c2e567530b",
    ),
    "dataset": (
        "ml/data/d0_post003_formal.jsonl",
        "28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115",
    ),
    "baseline": (
        "local-checkpoints/d0-post003-capability-seed42.pt",
        "3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06",
    ),
    "candidate": (
        "local-checkpoints/d0-post004-capability-seed42-step120.pt",
        "ae927ca3e779a0eda7c8fff025fc7cfd3a41568cb236148f444c75507ef35441",
    ),
    "authorization": (
        "local-evidence/d0-post004-formal/FORMAL_EXECUTION_AUTHORIZATION.md",
        "19d5c1f267030f68c26ebec778d5a552c4234479eac911dd58a77667c31d2f7e",
    ),
}

EXPOSURE_MARKER = Path(
    "local-evidence/d0-post004-formal/"
    "FORMAL_EXPOSURE_STARTED"
)

RESULT_PATH = Path(
    "local-evidence/d0-post004-formal/"
    "formal-result.json"
)

EXIT_STATUS_PATH = Path(
    "local-evidence/d0-post004-formal/"
    "formal.exit-status.txt"
)

STDERR_PATH = Path(
    "local-evidence/d0-post004-formal/"
    "formal.stderr.txt"
)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def verify_frozen_package() -> None:
    for name, (path, expected) in EXPECTED.items():
        actual = sha256_file(path)

        if actual != expected:
            raise RuntimeError(
                f"Frozen identity mismatch for {name}: "
                f"{path}"
            )


def verify_unexposed() -> None:
    artifacts = (
        EXPOSURE_MARKER,
        RESULT_PATH,
        EXIT_STATUS_PATH,
        STDERR_PATH,
    )

    existing = [
        str(path)
        for path in artifacts
        if path.exists()
    ]

    if existing:
        raise RuntimeError(
            "POST-004 formal execution is no longer "
            "unexposed: "
            + ", ".join(existing)
        )


def preflight() -> dict[str, object]:
    verify_frozen_package()
    verify_unexposed()

    return {
        "status": "READY_FOR_ONE_TIME_FORMAL_EXECUTION",
        "formalScoringExecuted": False,
        "exposureMarkerExists": False,
        "frozenInputsVerified": True,
    }


def begin_exposure() -> None:
    """
    This function is intentionally NOT called during
    build or synthetic validation.

    The final execution launcher may call it exactly once,
    immediately before the first formal model evaluation.
    """

    verify_frozen_package()
    verify_unexposed()

    EXPOSURE_MARKER.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Exclusive creation prevents a second execution.
    with EXPOSURE_MARKER.open(
        "x",
        encoding="utf-8",
    ) as handle:
        handle.write(
            "D0-POST-004 FORMAL EXPOSURE STARTED\n"
        )
        handle.write(
            "This marker permanently closes the "
            "pre-exposure state.\n"
        )
