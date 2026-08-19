"""
D0-POST-007 controlled one-time formal execution bridge.

This module connects the external one-time arming capability to the
already-frozen formal activation lifecycle.

It does not modify the frozen activation source.

Formal execution requires:

1. exact frozen activation identity
2. exact authorization identity
3. FORMAL_EXECUTION_ARMED capability
4. no FORMAL_EXECUTION_CONSUMED marker
5. no prior POST-007 formal exposure
6. valid arming capability contents

The frozen activation flag is enabled in memory only for this process.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import NoReturn

from evaluation import d0_post007_formal_activation as activation


STAGE = "D0-POST-007"

ACTIVATION_PATH = Path(
    "ml/evaluation/d0_post007_formal_activation.py"
)

AUTHORIZATION_PATH = Path(
    "local-evidence/"
    "d0-post007-formal-execution-authorization/"
    "FORMAL_EXECUTION_AUTHORIZATION.json"
)

ARM_DIR = Path(
    "local-evidence/d0-post007-formal-arming"
)

ARMED_MARKER = ARM_DIR / "FORMAL_EXECUTION_ARMED"
CONSUMED_MARKER = ARM_DIR / "FORMAL_EXECUTION_CONSUMED"

EXPOSURE_MARKER = Path(
    "local-evidence/"
    "d0-post007-formal-execution/"
    "FORMAL_EXPOSURE_STARTED"
)

EXPECTED_ACTIVATION_SHA256 = (
    "cdb7820ebd03146a2821d5026796f15c"
    "4613c694a0b5e053b005427ae40f310a"
)

EXPECTED_AUTHORIZATION_SHA256 = (
    "e82b72665ea753ff59810b924b47a91e"
    "9c20aef85acf0809815286e881324bdf"
)


class BridgeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def verify_identity(
    path: Path,
    expected: str,
    label: str,
) -> None:
    if not path.is_file():
        raise BridgeError(
            f"missing {label}: {path}"
        )

    actual = sha256_file(path)

    if actual != expected:
        raise BridgeError(
            f"{label} identity mismatch"
        )


def parse_capability(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise BridgeError(
            "one-time formal execution is not armed"
        )

    result: dict[str, str] = {}

    for raw_line in path.read_text(
        encoding="utf-8"
    ).splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if "=" not in line:
            raise BridgeError(
                "invalid arming capability format"
            )

        key, value = line.split("=", 1)

        if not key or key in result:
            raise BridgeError(
                "invalid arming capability"
            )

        result[key] = value

    return result


def validate_capability(
    capability: dict[str, str],
) -> None:
    required = {
        "stage": STAGE,
        "authorization_sha256":
            EXPECTED_AUTHORIZATION_SHA256,
        "activation_sha256":
            EXPECTED_ACTIVATION_SHA256,
        "execution_count": "1",
        "training_authorized": "false",
        "retraining_authorized": "false",
        "formal_execution_armed": "true",
    }

    if capability != required:
        raise BridgeError(
            "arming capability contract mismatch"
        )


def create_consumed_marker() -> None:
    try:
        with CONSUMED_MARKER.open(
            "x",
            encoding="utf-8",
        ) as f:
            f.write(
                "stage=D0-POST-007\n"
                "formal_execution_consumed=true\n"
                "execution_count=1\n"
            )
    except FileExistsError as exc:
        raise BridgeError(
            "one-time formal execution already consumed"
        ) from exc


def fail(message: str) -> NoReturn:
    raise BridgeError(message)


def execute() -> dict:
    # Verify immutable inputs before trusting the arm.
    verify_identity(
        ACTIVATION_PATH,
        EXPECTED_ACTIVATION_SHA256,
        "frozen activation module",
    )

    verify_identity(
        AUTHORIZATION_PATH,
        EXPECTED_AUTHORIZATION_SHA256,
        "one-time authorization",
    )

    # Fail closed on any evidence of prior execution.
    if CONSUMED_MARKER.exists():
        fail(
            "one-time formal execution already consumed"
        )

    if EXPOSURE_MARKER.exists():
        fail(
            "POST-007 formal exposure already started"
        )

    capability = parse_capability(
        ARMED_MARKER
    )

    validate_capability(
        capability
    )

    # The source file remains frozen and untouched.
    #
    # Enable its construction lock only inside this Python
    # process after the external one-time capability has
    # been authenticated.
    activation.FORMAL_ACTIVATION_ARMED = True

    try:
        result = (
            activation.execute_one_time_formal_comparison()
        )

    finally:
        # Never leave the imported module armed inside a
        # surviving process.
        activation.FORMAL_ACTIVATION_ARMED = False

        # If exposure started, the one-time capability has
        # irreversibly been consumed whether scoring
        # succeeded or failed.
        if (
            EXPOSURE_MARKER.exists()
            and not CONSUMED_MARKER.exists()
        ):
            create_consumed_marker()

    if not EXPOSURE_MARKER.exists():
        raise BridgeError(
            "formal lifecycle returned without exposure marker"
        )

    if not CONSUMED_MARKER.exists():
        raise BridgeError(
            "formal lifecycle completed without consumed marker"
        )

    return dict(result)


def main() -> int:
    result = execute()

    # Do not print dataset rows, expected responses,
    # checkpoint contents, or detailed formal examples.
    print(
        json.dumps(
            {
                "stage": result.get("stage"),
                "status": result.get("status"),
                "mode": result.get("mode"),
                "formalExposureStarted":
                    EXPOSURE_MARKER.exists(),
                "oneTimeCapabilityConsumed":
                    CONSUMED_MARKER.exists(),
            },
            indent=2,
            sort_keys=True,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
