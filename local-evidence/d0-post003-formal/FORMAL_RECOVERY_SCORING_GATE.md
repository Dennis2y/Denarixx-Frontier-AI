# D0-POST-003 Formal Recovery Scoring Gate

## State

The original formal exposure has been consumed.

The original evaluator terminated on an infrastructure
invariant before baseline or candidate scoring began.

No formal model metric was observed.

## Root cause

The original evaluator incorrectly summed every tensor
serialized in state_dict(), producing 107520.

Canonical D0 model parameter accounting uses
model.parameters(), producing 102784.

The 4736 difference is completely accounted for by:

- registered causal-mask buffers: 2048
- tied output-projection serialization: 2688

## Corrective evaluator

The defective evaluator remains preserved.

The corrected evaluator is:

ml/evaluation/d0_post003_formal_v2.py

The corrected implementation has been independently
frozen before recovery scoring.

## Recovery rules

Exactly one controlled recovery scoring attempt may be
made.

The recovery must use:

- the original frozen POST-002 baseline
- the original frozen POST-003 candidate
- the already-exposed but unchanged formal dataset
- the frozen V2 evaluator
- the original frozen acceptance policy

The following remain prohibited:

- POST-003 retraining
- checkpoint selection
- seed search
- hyperparameter search
- formal dataset revision
- acceptance-policy revision
- acceptance-threshold revision
- evaluator revision after this gate
- EVAL-001 selection
- EVAL-002 V4 selection

## Result handling

Once recovery exposure begins, its outcome must be
preserved whether:

- PASS
- FAIL
- evaluator/runtime error

There must be no second recovery attempt without a new
scientific adjudication.

## Current status

Recovery scoring has NOT been performed.

Formal acceptance remains undecided.
