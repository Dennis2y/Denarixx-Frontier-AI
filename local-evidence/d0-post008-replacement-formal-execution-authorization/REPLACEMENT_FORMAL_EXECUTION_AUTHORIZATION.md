# D0-POST-008 Replacement Formal Execution Authorization

## Status

AUTHORIZED FOR EXACTLY ONE GOVERNED FORMAL EXECUTION.

This authorization replaces the earlier unused authorization that was
formally superseded before exposure.

## Authorized runner

    ml/evaluation/d0_post008_real_execution_runner.py

SHA256:

    af80d687e215897206d295655559ca9a69a3407a6d2e54c9316378fa7291faad

## Authorized formal inputs

Sealed dataset:

    ml/data/d0_post008_formal.jsonl

Accepted baseline:

    local-checkpoints/d0-post003-capability-seed42.pt

Retained candidate:

    local-checkpoints/d0-post005-development-seed42-step120.pt

Frozen dependency adapter:

    ml/evaluation/d0_post008_dependencies.py

Frozen adjudicator:

    ml/evaluation/d0_post008_adjudicator.py

## Execution count

Exactly one formal execution is authorized.

No retry is authorized after the execution is consumed.

## Immutability

After this authorization:

- the sealed dataset must not change;
- either checkpoint must not change;
- the dependency adapter must not change;
- the adjudicator must not change;
- the real execution runner must not change;
- the frozen policy must not change.

## Training boundary

Training, retraining, adaptation, and candidate modification are not
authorized during formal execution.

## Current state

At authorization creation:

- formal exposure has not started;
- neither checkpoint has been deserialized;
- no model has been instantiated;
- no inference has occurred;
- no scoring has occurred;
- no training has occurred.

## Next permitted action

Invoke exactly one governed POST-008 formal execution through the
frozen real execution runner.

No alternative evaluator is authorized.
No manual scoring is authorized.
