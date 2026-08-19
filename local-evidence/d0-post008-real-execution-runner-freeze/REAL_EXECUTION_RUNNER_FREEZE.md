# D0-POST-008 Real Execution Runner Freeze

## Status

FROZEN PRE-AUTHORIZATION.

Runner:

    ml/evaluation/d0_post008_real_execution_runner.py

SHA256:

    af80d687e215897206d295655559ca9a69a3407a6d2e54c9316378fa7291faad

The runner has been statically inspected without opening the sealed
formal dataset for scoring, deserializing either checkpoint, executing
model inference, or starting formal exposure.

## Frozen lifecycle

The runner is frozen to the following lifecycle:

1. require replacement-authorization verification;
2. assert pristine real-result topology;
3. verify frozen dataset/checkpoint identities;
4. create the formal exposure marker;
5. load the sealed formal rows exactly once;
6. score and persist the accepted baseline first;
7. score and persist the retained candidate second;
8. reload persisted baseline and candidate results;
9. compare persisted results;
10. persist the comparison;
11. reload the persisted comparison;
12. apply the separately frozen adjudicator;
13. persist the final adjudication.

## Safety boundary

At freeze time:

- formal exposure has not started;
- the sealed dataset has not been opened for scoring by this stage;
- neither checkpoint has been deserialized;
- no model has been instantiated;
- no inference has occurred;
- no scoring has occurred;
- no training has occurred;
- no replacement authorization exists yet.

The next permitted stage is replacement pre-authorization readiness
against this exact runner identity.
