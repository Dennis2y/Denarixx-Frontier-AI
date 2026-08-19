# D0-POST-003 Corrected Execution Authorization

## Status

AUTHORIZED

## Reason

The first controlled invocation terminated in Python
argparse before the POST-003 training function was
entered.

Optimizer steps executed during failed launch:

0

POST-003 checkpoint created during failed launch:

NONE

Development result observed:

NO

## Correction scope

The corrected execution changes only the shell-level
invocation by supplying the five command-line arguments
already required by the frozen POST-003 runner:

- --checkpoint
- --train-dataset
- --lm-dataset
- --output
- --run-id

No training implementation is modified.

No frozen research input is modified.

No optimization configuration is modified.

## Frozen experiment

Base:

local-checkpoints/d0-post002-accepted.pt

Training split:

ml/data/d0_post003_train.jsonl

LM retention corpus:

ml/data/d0_research_corpus.txt

Run ID:

d0-post003-capability-seed42

Candidate output:

local-checkpoints/d0-post003-capability-seed42.pt

Candidate rule:

model state immediately after optimizer step 20

## Scientific status

This corrected invocation is authorized as the actual
single POST-003 optimization run because the preceding
launch performed zero optimizer steps and produced no
candidate or development result.

The original failed-launch evidence remains preserved.
