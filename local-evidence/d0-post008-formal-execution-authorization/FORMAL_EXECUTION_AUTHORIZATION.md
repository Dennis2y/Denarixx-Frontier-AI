# D0-POST-008 Formal Execution Authorization

## Status

FORMAL EXECUTION AUTHORIZED.

This artifact authorizes exactly one governed POST-008
formal execution against the already sealed dataset and
the already frozen baseline/candidate checkpoints.

This authorization does not itself execute inference,
scoring, adjudication, training, or retraining.

## Bound artifacts

Sealed dataset:

    ml/data/d0_post008_formal.jsonl

SHA256:

    78ff74ea7103c52cee382cd87879a30bc1f9b65c16a800249c322303fa63d95b

Accepted baseline:

    local-checkpoints/d0-post003-capability-seed42.pt

SHA256:

    3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

Retained candidate:

    local-checkpoints/d0-post005-development-seed42-step120.pt

SHA256:

    4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

Execution harness:

    ml/evaluation/d0_post008_execution_harness.py

SHA256:

    f5268a25b034b4c69d980ae372ed5c632546b50725723feea73f0eeab572ea59

Adjudicator:

    ml/evaluation/d0_post008_adjudicator.py

SHA256:

    92d2d803be8d481caccf7cbf5a7758738094459d5ba8095ca95662e0cd427c0c

## Authorization scope

Exactly one formal execution is authorized.

The governed execution must:

1. verify all frozen identities;
2. open the sealed dataset;
3. mark formal exposure;
4. load and score the accepted baseline first;
5. persist the baseline result;
6. load and score the retained candidate second;
7. persist the candidate result;
8. compare only the persisted results;
9. run the frozen adjudicator;
10. persist the final adjudication regardless of PASS or FAIL;
11. record the authorization as consumed.

No retry is authorized after the execution is consumed.

## Frozen execution restrictions

The execution must not:

- alter the sealed dataset;
- alter either checkpoint;
- alter tokenization;
- alter normalization;
- alter scoring;
- alter the adjudicator;
- alter thresholds;
- train;
- retrain;
- replace the candidate;
- repair results after exposure.

## Current lifecycle state

Formal execution enabled: YES

Formal execution authorized: YES

Authorization consumed: NO

Formal exposure started: NO

Checkpoint deserialized: NO

Model inference executed: NO

Model scoring executed: NO

Training executed: NO

## Next stage

The next stage is the single governed POST-008 formal
execution boundary.

No scoring has been performed by this authorization stage.
