# D0-POST-006 Formal Execution Authorization

## Status

AUTHORIZED FOR EXACTLY ONE FORMAL EXECUTION.

This authorization is governance evidence only.

This authorization does not itself execute model scoring.

This authorization does not itself parse the sealed formal dataset.

This authorization does not itself load either checkpoint.

This authorization does not itself create the formal exposure
marker.

## Authorized sealed formal dataset

Path:

ml/data/d0_post006_formal.jsonl

SHA-256:

202e63aee4f3a24c0746dc1a6a6136a6b33cf7ebfb3395f3e068d016985d189f

No other formal dataset is authorized.

The historical formal dataset:

ml/data/d0_post003_formal.jsonl

remains ineligible and must not be opened or scored.

## Authorized accepted baseline

Path:

local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

## Authorized candidate

Path:

local-checkpoints/d0-post005-development-seed42-step120.pt

SHA-256:

4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

## Authorized formal evaluator

Path:

ml/evaluation/d0_post006_formal.py

SHA-256:

37f54a6ec2725d8df34c0331780c723f841a1d471364091406159b3915121e89

## Authorized execution harness

Path:

ml/evaluation/d0_post006_execution_harness.py

SHA-256:

b58ebf1f71b676d056fa5f00a84ce567f10797dd3e6bccb50f54b0721b7d44e9

## Execution cardinality

Exactly one formal execution is authorized.

No second execution is authorized after formal exposure begins.

If execution fails after exposure begins, the failure must be
preserved and the formal evaluation must not be silently rerun.

## Exposure semantics

The execution must create:

FORMAL_EXPOSURE_STARTED

immediately before the first authorized load of the sealed formal
rows.

Once that marker exists:

- rerun is forbidden
- overwrite is forbidden
- the dataset remains permanently exposed for this stage
- failure evidence must be preserved

## Required execution order

1. verify frozen governance
2. verify sealed dataset identity without parsing
3. verify checkpoint identities without loading
4. verify no prior exposure
5. create FORMAL_EXPOSURE_STARTED
6. load sealed formal rows exactly once
7. validate loaded rows against frozen structure
8. score accepted baseline
9. persist baseline result
10. score candidate
11. persist candidate result
12. compare persisted results
13. persist final adjudication
14. freeze execution evidence

## Forbidden operations

This authorization does not permit:

- training
- retraining
- threshold tuning
- candidate selection
- development evaluation
- use of formal rows as training data
- use of formal rows as development data
- opening the historical formal dataset
- scoring the historical formal dataset
- printing formal expected responses
- changing the sealed formal dataset
- changing the frozen acceptance policy
- changing either authorized checkpoint
- changing the frozen evaluator after authorization
- changing the frozen execution harness after authorization

## Failure semantics

Any failure after formal exposure starts must:

1. return non-zero
2. preserve stderr
3. preserve exit status
4. preserve already-created evidence
5. preserve the exposure marker
6. prohibit rerun
7. prohibit evidence overwrite
8. produce no fabricated pass/fail result

## Authorization boundary

This gate authorizes a future separate formal execution.

The formal execution MUST NOT occur inside this authorization step.

## Next operation

Execute the separately controlled one-time formal evaluation using
only the exact identities frozen by this authorization.
