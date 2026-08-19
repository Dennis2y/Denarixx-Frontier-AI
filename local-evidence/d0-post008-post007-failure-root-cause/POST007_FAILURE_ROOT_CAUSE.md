# D0-POST-008 Recovery — POST-007 Failure Root-Cause Freeze

## Status

ROOT CAUSE ESTABLISHED.

D0-POST-007 is permanently consumed and MUST NOT be rerun.

## POST-007 failure

POST-007 entered formal exposure and subsequently terminated with
FileExistsError.

The failure was an evaluation-harness filesystem lifecycle defect.

It is NOT classified as a candidate capability rejection.

## Root cause

The POST-007 activation module places FORMAL_EXPOSURE_STARTED inside
FORMAL_RESULT_DIR.

create_once_text() creates the marker's parent directory with
parents=True and exist_ok=True.

Therefore creation of FORMAL_EXPOSURE_STARTED necessarily creates
FORMAL_RESULT_DIR.

Later in the same formal lifecycle, after entering baseline scoring,
the activation module attempts:

FORMAL_RESULT_DIR.mkdir(parents=True, exist_ok=False)

That operation necessarily raises FileExistsError because the result
directory already exists.

## Scoring boundary

The source sequence enters baseline score_checkpoint() before the
failing result-directory mkdir.

No BASELINE_RESULT.json survived.

Therefore the evidence does not establish a persisted baseline result.

POST-007 must not be interpreted as either formal candidate acceptance
or formal candidate rejection.

## Synthetic rehearsal gap

The synthetic harness contains the same relevant lifecycle pattern:
create_once_text() creates an exposure marker parent, followed later by
result_dir.mkdir(exist_ok=False).

The successful synthetic rehearsal therefore did not exercise the
critical real-path topology in which:

exposure_marker.parent == result_dir

POST-008 synthetic lifecycle testing MUST explicitly reproduce this
relationship.

## Mandatory POST-008 correction

POST-008 must use a filesystem lifecycle that cannot attempt to
create the result directory twice.

Before any POST-008 formal dataset is exposed, synthetic tests MUST
verify the exact parent/result-directory topology used by real
execution.

POST-007 source, dataset, checkpoints, markers, failure evidence, and
authorization artifacts remain immutable historical evidence.

## Governance

POST-007:
- formal exposure: YES
- execution consumed: YES
- rerun permitted: NO
- candidate formally accepted: NO
- candidate formally rejected: NO
- failure classification: evaluation-pipeline lifecycle failure

POST-008 formal execution is NOT authorized by this artifact.
