# D0-POST-005 Stage Initialization

## Status

POST-005 INITIALIZED

This artifact establishes the starting state for D0-POST-005.

No training was executed by initialization.

No model evaluation was executed by initialization.

No model forward pass was executed by initialization.

No formal example was scored or rescored by initialization.

## Inherited accepted baseline

The last accepted formal baseline remains:

local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

POST-004 did not produce a valid formal acceptance decision.

Therefore the POST-004 step-120 candidate MUST NOT replace the
accepted POST-003 baseline.

## POST-004 closure state

POST-004 formal execution is permanently recorded as:

INVALID / INCOMPLETE

Model acceptance status:

NO PASS DETERMINATION

NO FAIL DETERMINATION

The POST-004 formal exposure boundary was crossed.

The accepted POST-003 baseline was scored once during the failed
POST-004 execution.

That transient baseline result was not persisted.

The POST-004 candidate was not formally scored.

The failure occurred in the execution harness while adapting the
baseline scoring result.

The sealed failure was an adapter interface mismatch:

TypeError: object of type 'PosixPath' has no len()

POST-004 formal scoring MUST NOT be rerun.

The POST-004 exposure marker MUST NOT be deleted, replaced,
rewritten, or bypassed.

## POST-004 development candidate disposition

The checkpoint:

local-checkpoints/d0-post004-capability-seed42-step120.pt

SHA-256:

ae927ca3e779a0eda7c8fff025fc7cfd3a41568cb236148f444c75507ef35441

is retained only as an unadjudicated POST-004 development artifact.

It is NOT an accepted formal baseline.

It MUST NOT be represented as formally accepted.

Its development-selection result does not substitute for a formal
acceptance decision.

## Exposed formal data

The dataset:

ml/data/d0_post003_formal.jsonl

SHA-256:

28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115

has crossed a formal exposure boundary during POST-004.

POST-005 development decisions MUST NOT use results obtained by
rescoring this exposed formal dataset.

POST-005 initialization does not authorize any model scoring against
this dataset.

## POST-005 execution-harness requirement

Before any future formal exposure is authorized, POST-005 requires a
complete synthetic end-to-end rehearsal of the execution pipeline.

The rehearsal must validate, at minimum:

1. dataset-row loading
2. scoring-result schema
3. adapter invocation using actual row objects rather than a path
4. baseline-result persistence
5. candidate-result persistence
6. per-family aggregation
7. formal comparison
8. result evidence writing
9. failure evidence writing
10. one-time exposure semantics
11. rerun prevention
12. clean import-path behavior

Synthetic rehearsal MUST NOT use the protected formal dataset.

Synthetic rehearsal MUST NOT score the accepted baseline checkpoint.

Synthetic rehearsal MUST NOT score the POST-004 candidate checkpoint.

## Training state

POST-005 training is NOT authorized by this initialization.

POST-005 development evaluation is NOT authorized by this
initialization.

POST-005 formal evaluation is NOT authorized by this initialization.

A separate design, rehearsal, and authorization sequence is required.

## Frozen inherited evidence

POST-004 authorization SHA-256:

19d5c1f267030f68c26ebec778d5a552c4234479eac911dd58a77667c31d2f7e

POST-004 exposure marker SHA-256:

2d55a5181c72444ca12fb39f455c91a1672cffb8ce8ce61b9cfe6d2c273151a9

POST-004 stderr SHA-256:

877a86b287bbaad6bc0ea2045fb4402621c325bad4973d0ad36a8bfae1615f96

POST-004 exit-status SHA-256:

4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865

POST-004 adjudication SHA-256:

b2721a9c18555cc5b5c237b8ca5c6f2e339c3bc4960f89dbb7fad2827d8f3f40

## Initial POST-005 state

Accepted baseline:

POST-003

POST-004 formal status:

INVALID / INCOMPLETE

POST-004 candidate:

UNADJUDICATED DEVELOPMENT ARTIFACT

POST-005 training:

LOCKED

POST-005 model evaluation:

LOCKED

POST-005 formal evaluation:

LOCKED

Next authorized engineering operation:

SYNTHETIC END-TO-END EXECUTION-HARNESS REHEARSAL
