# D0-POST-008 Recovery Policy and Execution Lifecycle Contract

## Status

PRE-FORMAL RECOVERY DESIGN FROZEN.

This stage follows the consumed D0-POST-007 execution.

D0-POST-007 MUST NOT be rerun.

D0-POST-007 did not formally accept or formally reject the retained
candidate.

Its failure is classified as an evaluation-pipeline filesystem
lifecycle failure after formal exposure.

## Historical immutability

The following POST-007 artifacts are historical evidence and MUST NOT
be repaired, deleted, rewritten, or reset:

- POST-007 formal dataset;
- POST-007 activation module;
- POST-007 execution harness;
- POST-007 authorization artifacts;
- POST-007 arming and consumed markers;
- FORMAL_EXPOSURE_STARTED;
- FAILURE.json;
- POST-007 checkpoint identities.

POST-008 recovery MUST be implemented through new POST-008 artifacts.

## Candidate status

The retained candidate remains:

local-checkpoints/d0-post005-development-seed42-step120.pt

POST-007 produced no persisted formal adjudication.

Therefore POST-007 provides no capability evidence sufficient to
accept or reject that candidate.

Any future POST-008 comparison must separately bind the accepted
baseline and retained candidate identities before formal execution.

## Fresh formal dataset requirement

POST-008 requires a fresh formal dataset.

Neither exposed POST-006 formal rows nor exposed POST-007 formal rows
may be reused as POST-008 formal examples.

Historical formal datasets MUST NOT be opened for construction,
development, candidate selection, threshold tuning, or training.

## Corrected filesystem lifecycle

POST-008 real execution MUST satisfy:

    exposure_marker.parent == result_dir

Creation of FORMAL_EXPOSURE_STARTED is allowed to establish the result
directory through create-once marker persistence.

After the exposure marker has been created, real execution MUST NOT
attempt to create result_dir again with mkdir(exist_ok=False).

All subsequent evidence artifacts inside result_dir MUST use
create-once file semantics.

The required lifecycle is:

1. verify authorization and frozen identities;
2. verify result_dir and exposure marker are absent;
3. create FORMAL_EXPOSURE_STARTED using create-once persistence;
4. confirm exposure_marker.parent == result_dir;
5. load the sealed formal rows exactly once;
6. score the accepted baseline first;
7. persist BASELINE_RESULT.json create-once;
8. score the retained candidate;
9. persist CANDIDATE_RESULT.json create-once;
10. reload persisted aggregate results;
11. compare persisted aggregate results only;
12. persist FINAL_ADJUDICATION.json create-once.

There MUST NOT be an independent result_dir.mkdir(exist_ok=False)
between steps 3 and 12.

## Failure lifecycle

After formal exposure begins, any exception consumes the execution.

Failure handling may ensure result_dir exists with exist_ok=True only
for failure-evidence persistence.

FAILURE.json MUST be create-once.

Existing successful evidence MUST NOT be overwritten during failure
handling.

A failure after exposure MUST NOT authorize a rerun.

## Synthetic topology requirement

Before POST-008 formal execution can be authorized, the synthetic
execution rehearsal MUST reproduce the exact real topology:

    synthetic_exposure_marker.parent == synthetic_result_dir

The rehearsal MUST demonstrate that:

- exposure-marker creation establishes the result directory;
- no duplicate result-directory creation occurs;
- baseline scoring occurs before candidate scoring;
- baseline result is persisted before candidate scoring;
- candidate result is persisted before comparison;
- comparison consumes persisted aggregate results;
- final adjudication is create-once;
- rerun protection rejects a second lifecycle;
- pre-existing exposure marker rejects execution;
- pre-existing result directory rejects execution;
- injected failure after exposure persists failure evidence;
- injected failure cannot overwrite prior evidence;
- real formal paths are unreachable from synthetic execution.

A synthetic rehearsal using a different parent/result-directory
relationship is insufficient.

## Pre-exposure tests

POST-008 MUST include automated synthetic tests specifically capable
of detecting the POST-007 defect.

At minimum, a test MUST fail if implementation contains the semantic
equivalent of:

    create_once_text(exposure_marker, ...)
    result_dir.mkdir(exist_ok=False)

when exposure_marker.parent == result_dir.

## Dataset compatibility

The POST-007 compatibility lesson remains binding.

Before a POST-008 formal dataset is sealed, every proposed row MUST
pass the exact frozen tokenizer/context compatibility path required by
the future POST-008 scorer.

The evaluator MUST NOT be weakened to accommodate proposed rows.

## Separation of stages

The following must remain separate, deliberate stages:

1. recovery/lifecycle policy;
2. corrected harness implementation;
3. synthetic lifecycle tests;
4. synthetic end-to-end rehearsal;
5. POST-008 capability-family freeze;
6. formal dataset construction policy;
7. compatibility validator freeze;
8. fresh proposed dataset construction;
9. compatibility validation;
10. formal dataset sealing;
11. scoring dependency freeze;
12. adjudication policy freeze;
13. GO/NO-GO readiness;
14. one-time formal authorization;
15. one-time arming;
16. one-time formal execution.

Passing an earlier stage does not authorize a later stage.

## Training prohibition

This recovery stage does NOT authorize:

- training;
- retraining;
- candidate modification;
- candidate selection;
- threshold tuning;
- formal dataset creation;
- formal dataset exposure;
- checkpoint loading;
- model inference;
- model scoring;
- formal comparison.

## Governance decision

D0-POST-008 is currently PRE-FORMAL.

POST-008 formal execution is NOT authorized.

The immediate next permitted activity is implementation and synthetic
testing of a new POST-008 execution harness under this frozen
lifecycle contract.
