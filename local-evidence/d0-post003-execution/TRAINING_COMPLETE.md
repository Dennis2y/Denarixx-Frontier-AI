# D0-POST-003 Training Complete

## Status

CANDIDATE FIXED

## Launch history

Initial controlled launch:

FAILED BEFORE TRAINING

Reason:

Missing required CLI arguments.

Optimizer steps from initial launch:

0

Corrected controlled launch:

SUCCESS

## Actual optimization runs

1

## Candidate

local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

## Candidate rule

The candidate is the model state immediately after
optimizer step 20.

## Frozen optimization configuration

- optimizer: AdamW
- learning rate: 1e-4
- weight decay: 0.01
- gradient clip norm: 1.0
- retention lambda: 0.25
- SFT batch size: 4
- LM batch size: 4
- seed: 42
- SFT generator seed: 42
- LM generator seed: 43
- optimizer steps: 20
- candidate step: 20

## Development status

NOT EVALUATED

## Formal evaluation status

NOT EVALUATED

## Historical evaluations

EVAL-001 and EVAL-002 V4 were not used for POST-003
candidate selection.

## Next scientific step

Evaluate this fixed candidate once against the frozen
POST-003 development split using a separate read-only
evaluation procedure.

No retraining or candidate replacement is permitted
within POST-003.
