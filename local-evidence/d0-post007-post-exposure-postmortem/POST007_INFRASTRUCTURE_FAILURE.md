# D0-POST-007 Formal Evaluation Incident

## Classification

POST-007 formal execution was invalidated by an evaluation-lifecycle
infrastructure defect after formal exposure began.

This incident is NOT a candidate-model adjudication failure.

## Irreversible state

- formal exposure started: YES
- one-time authorization consumed: YES
- POST-007 rerun permitted: NO

## Execution progress established by control flow

The formal lifecycle:

1. passed activation readiness
2. created FORMAL_EXPOSURE_STARTED
3. loaded the sealed formal rows
4. invoked baseline checkpoint scoring
5. baseline scoring returned control to the activation lifecycle
6. attempted to create FORMAL_RESULT_DIR with exist_ok=False
7. failed with FileExistsError

The exposure marker itself resides inside FORMAL_RESULT_DIR.
Creating the exposure marker necessarily creates that parent directory.

Therefore the later mkdir(exist_ok=False) operation was structurally
incompatible with the earlier exposure-marker creation.

## Formal evaluation outcome

Baseline scoring invocation: COMPLETED RETURN TO CALLER
Baseline result persisted: NO

Candidate scoring invocation: NO
Candidate result persisted: NO

Formal comparison: NO
Final adjudication: NONE

Candidate PASS: NOT ESTABLISHED
Candidate FAIL: NOT ESTABLISHED

## Integrity decision

POST-007 will not be rerun.

Existing exposure, consumed-state, and failure evidence must remain
preserved byte-for-byte.

The infrastructure defect must be corrected for a future evaluation
stage using a fresh formal-evaluation boundary. The exposed POST-007
dataset must not be reused for candidate selection, development,
threshold tuning, retraining, or a replacement adjudication.
