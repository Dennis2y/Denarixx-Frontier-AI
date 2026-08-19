# D0-POST-007 Recovery Policy

## Status

PRE-FORMAL RECOVERY STAGE.

This stage exists because D0-POST-006 formal execution failed
after formal exposure began.

D0-POST-006 MUST NOT be rerun.

The D0-POST-006 formal dataset MUST NOT be repaired, edited,
rescored, or reused as a POST-007 formal dataset.

## Existing accepted baseline

The last formally accepted checkpoint remains:

local-checkpoints/d0-post003-capability-seed42.pt

The retained POST-005 candidate was neither formally accepted nor
formally rejected by POST-006 because adjudication was never
reached.

## POST-006 failure classification

D0-POST-006 failed because at least one sealed formal instruction
contained a character absent from the accepted checkpoint
tokenizer.

The observed execution error was a tokenizer-coverage failure.

This is classified as an evaluation-pipeline compatibility failure,
not a candidate capability failure.

## Mandatory POST-007 compatibility gate

Before ANY POST-007 formal dataset may be sealed, every proposed
formal example MUST pass the exact instruction encoding path used
for scoring.

For every proposed row:

1. instruction must be a non-empty string;
2. response must be a non-empty string;
3. family must belong to the frozen POST-007 family set;
4. formatted prompt must have complete tokenizer coverage;
5. formatted response must have complete tokenizer coverage;
6. encode_instruction() must succeed using the accepted baseline
   tokenizer;
7. the formatted instruction + response sequence must fit the
   accepted baseline context length;
8. at least one supervised response token must remain;
9. no compatibility failure may be ignored or normalized away.

A dataset that fails any compatibility check MUST NOT be sealed.

## No evaluator weakening

Recovery MUST NOT:

- add missing characters to the accepted tokenizer;
- silently replace unsupported characters;
- strip unsupported punctuation during scoring;
- truncate formal examples to force context compatibility;
- change encode_instruction() merely to accommodate formal data;
- use candidate-specific preprocessing;
- weaken tokenizer validation.

The formal dataset must be compatible with the frozen evaluator,
not the reverse.

## Freshness

POST-007 requires a fresh formal dataset.

The exposed POST-006 formal rows must not be reused as POST-007
formal examples.

The POST-006 dataset must not be edited into a supposedly new
dataset.

POST-007 formal examples must be newly constructed under the
POST-007 policy.

## Pre-seal validation

Tokenizer coverage and context compatibility MUST be established
before the new formal dataset is sealed and before formal execution
authorization is issued.

The compatibility validator itself may inspect proposed POST-007
rows during dataset construction because those rows are not yet
sealed formal evidence.

After sealing, examples may not be changed.

## Formal execution

This recovery-policy stage does NOT authorize:

- training;
- retraining;
- candidate selection;
- formal dataset creation;
- formal model scoring;
- formal comparison;
- modification of POST-006 evidence.

A later step must separately freeze:

1. POST-007 capability families;
2. POST-007 construction policy;
3. compatibility validator;
4. fresh dataset;
5. dataset SHA-256;
6. evaluator identities;
7. one-time execution authorization.

## Governance principle

Formal dataset compatibility is a precondition of formal exposure.

A compatibility defect discovered after exposure consumes that
execution and requires a fresh stage and fresh formal dataset.
