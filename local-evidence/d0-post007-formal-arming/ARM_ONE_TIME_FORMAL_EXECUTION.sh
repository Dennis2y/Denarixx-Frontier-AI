#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo " DENARIXX FRONTIER AI — D0-POST-007"
echo " ONE-TIME FORMAL EXECUTION ARMING GATE"
echo " THIS STEP ARMS ONLY — IT DOES NOT SCORE THE DATASET"
echo "============================================================"
echo

AUTH="local-evidence/d0-post007-formal-execution-authorization/FORMAL_EXECUTION_AUTHORIZATION.json"
ACTIVATION="ml/evaluation/d0_post007_formal_activation.py"

ARMED_MARKER="local-evidence/d0-post007-formal-arming/FORMAL_EXECUTION_ARMED"
CONSUMED_MARKER="local-evidence/d0-post007-formal-arming/FORMAL_EXECUTION_CONSUMED"
EXPOSURE="local-evidence/d0-post007-formal-execution/FORMAL_EXPOSURE_STARTED"

EXPECTED_AUTH="65b1ede08e0709b4ab3cc9a0067cddbe5e64a9013c8d9cbc3437936060eb8dbc"
EXPECTED_ACTIVATION="cdb7820ebd03146a2821d5026796f15c4613c694a0b5e053b005427ae40f310a"

sha256_file() {
    shasum -a 256 "$1" | awk '{print $1}'
}

[[ "$(sha256_file "$AUTH")" == "$EXPECTED_AUTH" ]] || {
    echo "ERROR: authorization identity mismatch."
    exit 1
}

[[ "$(sha256_file "$ACTIVATION")" == "$EXPECTED_ACTIVATION" ]] || {
    echo "ERROR: activation module identity mismatch."
    exit 1
}

if [[ -e "$CONSUMED_MARKER" ]]; then
    echo "ERROR: one-time authorization has already been consumed."
    exit 1
fi

if [[ -e "$EXPOSURE" ]]; then
    echo "ERROR: formal exposure has already started."
    exit 1
fi

if [[ -e "$ARMED_MARKER" ]]; then
    echo "ERROR: formal execution is already armed."
    exit 1
fi

AUTH="$AUTH" python3 - <<'PY'
import json
import os
from pathlib import Path

auth = json.loads(
    Path(os.environ["AUTH"]).read_text(encoding="utf-8")
)

checks = {
    "status": "authorized",
    "executionCountAuthorized": 1,
    "formalExecutionAuthorized": True,
    "modelScoringAuthorized": True,
    "trainingAuthorized": False,
    "retrainingAuthorized": False,
}

for key, expected in checks.items():
    if auth.get(key) != expected:
        raise SystemExit(
            f"ERROR: authorization failed readiness check: {key}"
        )

print("✓ One-time authorization readiness verified.")
PY

# IMPORTANT:
# This marker is an external one-time arming capability.
# It does NOT edit frozen Python source.
# It does NOT create FORMAL_EXPOSURE_STARTED.
# It does NOT open the formal dataset.
# It does NOT load either checkpoint.
# It does NOT perform inference.

(
    umask 077
    printf '%s\n' \
        "stage=D0-POST-007" \
        "authorization_sha256=$EXPECTED_AUTH" \
        "activation_sha256=$EXPECTED_ACTIVATION" \
        "execution_count=1" \
        "training_authorized=false" \
        "retraining_authorized=false" \
        "formal_execution_armed=true" \
        > "$ARMED_MARKER"
)

echo
echo "✓ One-time external arming capability created."
echo
echo "Formal dataset opened: NO"
echo "Checkpoint loaded: NO"
echo "Model scoring executed: NO"
echo "Formal exposure started: NO"
echo
echo "NEXT:"
echo "  STOP."
echo "  Return the complete Terminal output before formal execution."
echo
echo "============================================================"
echo " D0-POST-007 ONE-TIME ARMING COMPLETE"
echo "============================================================"
