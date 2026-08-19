# D0-POST-002 Predeclared Acceptance Policy

Status: PREDECLARED BEFORE EVAL-002 MODEL COMPARISON

The purpose of D0-POST-002 is to determine whether mixed
response-only SFT plus language-model retention improves the
instruction/retention tradeoff relative to D0-POST-001.

## Required invariants

A candidate is invalid if:

1. Model architecture changes unexpectedly.
2. Tokenizer identity changes.
3. Parameter count changes unexpectedly.
4. Frozen evaluation data changes.
5. Training/evaluation contamination is detected.
6. Evaluation is nondeterministic under the established evaluator.

## Primary comparison

POST-002 is compared against POST-001.

A candidate must:

- improve instruction response loss relative to POST-001, and
- improve language-model loss relative to POST-001.

Neither metric may be traded away for the other at this stage.

## Baseline retention constraint

Relative to the ARCH-002 pretrained baseline:

- language-model degradation must remain below 7 percent.

## Secondary evaluation requirement

The same directional improvement over POST-001 must be observed
on both EVAL-001 and EVAL-002 before canonical promotion.

## Exact match

Exact-match rate is recorded but is not currently a hard gate
because D0 is a tiny research model and the evaluation suite is
primarily intended to measure controlled loss changes.

## Promotion rule

Passing numerical thresholds does not automatically promote a
checkpoint.

Before promotion:

- regression tests must pass,
- evidence hashes must be recorded,
- model identity must be verified,
- results must be reviewed,
- and no later experiment may be selected solely by repeatedly
  tuning against frozen evaluation results.
