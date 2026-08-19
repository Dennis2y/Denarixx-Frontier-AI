# D0-POST-008 Unused Formal Authorization Supersession

## Status

SUPERSEDED BEFORE FORMAL EXPOSURE AND BEFORE AUTHORIZATION CONSUMPTION.

The previously issued POST-008 formal-execution authorization is
preserved unchanged as historical evidence.

It is not deleted, rewritten, or marked consumed in place.

A separate supersession record establishes that the old authorization
must not be executed or reactivated.

## Reason

The authorization bound the frozen POST-008 execution harness.

Subsequent read-only inspection established that the exact authorized
harness:

- has `REAL_FORMAL_EXECUTION_ENABLED = False`; and
- intentionally contains no real formal-execution implementation.

The authorization simultaneously forbids changing the scoring/execution
implementation after authorization.

Therefore modifying that harness and then executing under the old
authorization would violate the authorization's own frozen identity
boundary.

## Exposure state

At supersession time:

- the authorization is unconsumed;
- zero authorized executions have occurred;
- the real result directory does not exist;
- the sealed formal dataset has not been opened for formal scoring;
- neither real checkpoint has been deserialized for POST-008;
- no real POST-008 inference has occurred;
- no real POST-008 scoring has occurred;
- formal exposure has not started;
- no training or retraining has occurred.

## Governance consequence

The old authorization is superseded without consumption.

It must never be used for execution.

The frozen dataset, checkpoints, adjudication policy, dependency
semantics, and existing historical evidence remain unchanged.

## Required next stages

Before any replacement formal authorization can exist:

1. implement the missing real execution lifecycle;
2. freeze the completed execution implementation;
3. verify that dataset/checkpoint/policy/scoring semantics remain
   unchanged;
4. synthetically rehearse the completed lifecycle;
5. perform a new pre-authorization GO/NO-GO readiness check;
6. only after a GO verdict issue a new one-shot authorization.

No formal execution is authorized by this supersession artifact.
