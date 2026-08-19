# D0-POST-006 Synthetic Execution-Harness Rehearsal

## Decision

PASS.

The frozen D0-POST-006 execution harness was exercised using
synthetic-only artifacts.

No real formal dataset rows were parsed.

No historical formal dataset was opened.

No real checkpoint was loaded.

No real model scoring occurred.

No real POST-006 formal exposure marker was created.

## Verified lifecycle properties

The rehearsal verified:

- synthetic exposure marker before first synthetic row load
- baseline scoring before candidate scoring
- baseline persistence before candidate scoring
- candidate persistence before comparison
- comparison from persisted results
- final adjudication persistence
- prior-evidence preservation after injected failure
- rerun prevention
- create-once evidence / overwrite prevention
- identity failure before exposure
- rejection of the real formal-dataset path in synthetic mode
- rejection of the real baseline path in synthetic mode
- rejection of the real candidate path in synthetic mode
- rejection of the real exposure-marker path in synthetic mode
- rejection of the real result directory in synthetic mode
- continued fail-closed behavior of the real execution entry point

## Governance meaning

This rehearsal is engineering validation only.

It does not authorize formal execution.

It does not authorize model scoring.

It does not authorize creation of the real
FORMAL_EXPOSURE_STARTED marker.

A separate formal-execution authorization gate is required before
the sealed POST-006 formal dataset may be parsed for model scoring.
