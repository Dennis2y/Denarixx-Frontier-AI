# D0-POST-008 Replacement Pre-Authorization Readiness

## Verdict

GO

This verdict means the prerequisites are ready for issuance of a new,
single-use POST-008 formal-execution authorization bound to the frozen
real execution runner.

It does not authorize formal execution.

## Frozen runner

    ml/evaluation/d0_post008_real_execution_runner.py

SHA256:

    af80d687e215897206d295655559ca9a69a3407a6d2e54c9316378fa7291faad

## Bound formal artifacts

Sealed dataset:

    ml/data/d0_post008_formal.jsonl

Accepted baseline:

    local-checkpoints/d0-post003-capability-seed42.pt

Retained candidate:

    local-checkpoints/d0-post005-development-seed42-step120.pt

Dependency adapter:

    ml/evaluation/d0_post008_dependencies.py

Adjudicator:

    ml/evaluation/d0_post008_adjudicator.py

## Governance state

The earlier authorization was superseded without being consumed.

The replacement runner was implemented and frozen before issuance of
any replacement authorization.

At this readiness boundary:

- formal exposure has not started;
- no checkpoint has been deserialized;
- no model inference has occurred;
- no scoring has occurred;
- no training has occurred;
- no replacement authorization has been created.

## Next permitted stage

Create exactly one replacement formal-execution authorization bound to
the frozen runner and the already frozen formal artifacts.

Do not execute the runner in the authorization stage.
