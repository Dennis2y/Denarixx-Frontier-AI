# D0-POST-003 Formal Evaluator V2 Correction

## Classification

Infrastructure defect correction after formal exposure,
but before any formal model metric was produced.

## Original failure

The original evaluator calculated model size by summing
all tensors serialized in `state_dict()`.

Observed serialized tensor-element count:

107520

Canonical D0 model parameter count:

102784

Difference:

4736

## Root cause

The 4736 difference is exactly:

- two registered causal-mask buffers:
  2048 elements total

- tied output projection serialized under a second
  state-dict key:
  2688 elements

2048 + 2688 = 4736

The canonical D0 parameter-count definition has
consistently been:

sum(parameter.numel() for parameter in model.parameters())

This equals:

102784

## Scientific status

The original formal exposure failed before either the
POST-002 baseline or POST-003 candidate was scored.

No formal response loss, perplexity, exact match, or
family result was observed.

Therefore the model, candidate, formal dataset,
acceptance policy, and evaluation thresholds remain
uninformed by formal model performance.

## Corrective action

The original evaluator remains preserved.

A new evaluator version was created:

ml/evaluation/d0_post003_formal_v2.py

Only the incorrect parameter-count invariant was
replaced.

The corrected evaluator reconstructs D0 from the frozen
checkpoint model configuration, loads the frozen state
dictionary with strict=True, and counts actual
model.parameters().

No formal model scoring was performed while validating
this correction.

## Prohibited changes

This correction does NOT authorize:

- retraining POST-003
- modifying the formal dataset
- modifying acceptance thresholds
- changing the candidate checkpoint
- changing the baseline checkpoint
- changing architecture
- changing tokenizer
- changing hyperparameters
- using EVAL-001 or EVAL-002 V4 for selection

## Recovery status

A controlled recovery scoring attempt may only occur
after the corrected evaluator identity is frozen and
reviewed.

The original failure and exposure records must remain
preserved permanently.
