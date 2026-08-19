# D0-POST-006 Authorized Execution-Harness Revision

## Status

AUTHORIZED FOR IMPLEMENTATION REVISION ONLY.

This authorization exists because the currently frozen execution
harness remains intentionally fail-closed even though the separate
one-time formal-execution authorization has now been frozen.

The current harness identity is:

`ml/evaluation/d0_post006_execution_harness.py`

SHA-256:

`b58ebf1f71b676d056fa5f00a84ce567f10797dd3e6bccb50f54b0721b7d44e9`

## Permitted change

The implementation may be revised only to bind the frozen
one-time authorization to the already-frozen real execution
lifecycle.

The revision must preserve:

- one-time execution semantics
- exposure marker immediately before first formal-row load
- sealed dataset identity verification before exposure
- checkpoint identity verification before loading
- baseline scoring first
- baseline persistence before candidate scoring
- candidate persistence before comparison
- comparison from persisted evidence
- failure evidence preservation
- rerun prevention
- overwrite prevention
- prohibition on historical formal data

## This gate does not authorize execution

During implementation of the revision:

- no formal rows may be parsed
- no checkpoint may be loaded
- no model may be scored
- no exposure marker may be created
- no training may occur

The revised harness will have a new SHA-256 identity.

That revised implementation must undergo synthetic rehearsal and
audit before a new one-time formal-execution authorization can bind
to its new identity.
