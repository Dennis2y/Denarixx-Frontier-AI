# D0-POST-005 Frozen Development / Training Plan

Status: FROZEN BEFORE TRAINING

## Accepted parent checkpoint

Path:
local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:
3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

POST-003 is the only accepted starting checkpoint.

POST-004 step-120 is NOT an accepted parent and MUST NOT be
used to inherit formal acceptance.

## Development reference artifact

Path:
local-checkpoints/d0-post004-capability-seed42-step120.pt

SHA-256:
ae927ca3e779a0eda7c8fff025fc7cfd3a41568cb236148f444c75507ef35441

This artifact may be used only as a development reference.

## Training dataset

Path:
ml/data/d0_post004_train.jsonl

SHA-256:
93f60bf014810bc5a5592d1ad7f3c5bf7bef80011dea252ddb0455f006b9963f

## Development dataset

Path:
ml/data/d0_post004_dev.jsonl

SHA-256:
d54abaa83a4bbdcca313c557431fa5005e4490b7103f0f997ccd0c619f5c8a58

The development dataset may be used for POST-005 development
candidate selection only.

It MUST NOT be used as training input.

## Retention LM corpus

Path:
ml/data/d0_research_corpus.txt

SHA-256:
936b53855c5fa65cc408fb0b29108966445215a474ccfcce7ae7fe9f41fcc072

This is the historically verified retention corpus used by
the inherited POST-003 / POST-004 training lineage.

ml/data/d0_sft_tiny.jsonl is NOT the retention LM input for
this POST-005 contract.

## Protected formal dataset

Path:
ml/data/d0_post003_formal.jsonl

SHA-256:
28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115

The protected formal dataset:

- MUST NOT be training input
- MUST NOT be development input
- MUST NOT be used for hyperparameter selection
- MUST NOT be used for candidate selection
- MUST NOT be reopened for POST-004 scoring

Its identity may be checked without opening its contents.

## Starting policy

POST-005 MUST start from the accepted POST-003 checkpoint.

POST-004 step-120 MUST NOT be used as the parent checkpoint.

## Training-controller implementation policy

A dedicated POST-005 controller MUST be created.

Existing POST-003 / POST-004 training files are implementation
references only and MUST NOT be silently repurposed as POST-005.

The POST-005 controller MUST verify frozen input hashes before
training.

## Frozen optimization policy

Optimizer:
AdamW

Optimizer state:
FRESH — MUST NOT resume inherited optimizer state

Learning rate:
0.0001

Weight decay:
0.01

Gradient clip norm:
1.0

Retention weight:
0.25

SFT batch size:
4

LM batch size:
4

Warmup steps:
0

Global seed:
42

SFT generator seed:
42

LM generator seed:
43

## Frozen trajectory

Maximum training steps:
120

Candidate checkpoint steps:
40
80
120

No additional candidate checkpoint may be introduced after
training begins.

## Development candidate-selection rule

All candidate checkpoints MUST be evaluated on the frozen
development dataset only.

Primary metric:
higher exact-match count

Secondary metric:
lower aggregate response loss

Tertiary metric:
higher exact-match family coverage

A candidate with zero exact matches MUST NOT be selected.

Tie-breaking MUST be deterministic and implemented before
real candidate evaluation.

Development selection does NOT constitute formal acceptance.

## Failure behavior

Training-controller failure MUST:

1. return non-zero status
2. preserve stderr
3. preserve exit status
4. preserve already-created immutable evidence
5. never silently restart a partially executed formal process
6. never alter POST-004 sealed evidence
7. never alter protected formal data

## Formal-evaluation state

POST-005 formal evaluation remains LOCKED.

Training authorization does NOT authorize formal evaluation.

A separate formal-evaluation contract must be frozen after
development candidate selection.

## Required next operation

BUILD POST-005 TRAINING CONTROLLER + TESTS

Training remains locked until the controller and its synthetic
tests pass.
