# D0-POST-003 Parameter Count Root Cause

## Observed discrepancy

Formal evaluator observed:

107520 state-dict tensor elements

Frozen model parameter count:

102784 parameters

Difference:

4736 tensor elements

## Decomposition

The discrepancy decomposes exactly into:

- causal-mask buffers:
  2 × 1024 = 2048 elements

- serialized output-projection tensor:
  42 × 64 = 2688 elements

Total:

2048 + 2688 = 4736

Therefore:

107520 - 4736 = 102784

## Scientific interpretation

The formal evaluator used a state-dictionary tensor-element
count as though it were a model parameter count.

These quantities are not equivalent.

A state dictionary may contain:

1. registered non-parameter buffers, and
2. multiple serialized names referring to/shared with a
   single model parameter.

The training-time parameter count was based on model
parameters, yielding 102784.

The failed formal evaluator counted all state-dictionary
tensors, yielding 107520.

## Consequence

There is currently no evidence of a baseline/candidate
architecture change.

Baseline and candidate:

- have identical state-dictionary keys,
- have identical tensor shapes,
- have identical model configuration,
- preserve their frozen checkpoint hashes.

The failure occurred in the evaluator's invariant
implementation before formal model scoring.

## Boundary

This document does NOT authorize a second formal scoring
attempt.

The formal dataset remains exposed.

No evaluator modification or recovery execution is
authorized until this root-cause evidence is reviewed.
