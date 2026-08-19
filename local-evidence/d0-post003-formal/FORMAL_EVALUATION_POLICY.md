# D0-POST-003 Formal Evaluation Policy

## Status

FROZEN BEFORE FORMAL CANDIDATE SCORING

## Candidate

The candidate is the already-fixed D0-POST-003
step-20 checkpoint.

No retraining, checkpoint selection, seed search,
learning-rate search, retention-weight search or
development-set reuse is permitted.

## Purpose

The formal evaluation determines whether POST-003
produced evidence of controlled multi-family
capability acquisition beyond the accepted POST-002
baseline.

Development PASS alone is insufficient for formal
acceptance.

## Required evaluation families

The untouched formal dataset must cover:

- echo
- binary
- transform
- qa
- semantic

The formal examples must not duplicate:

- POST-003 training examples;
- POST-003 development examples;
- EVAL-001 examples;
- EVAL-002 V4 examples.

## Formal metrics

For baseline and candidate measure:

- token-weighted response loss;
- response perplexity;
- greedy generation;
- exact match;
- exact-match rate;
- per-example response loss;
- per-family response loss;
- per-family exact match.

## Formal acceptance rule

Formal acceptance requires ALL of the following:

1. POST-003 aggregate response loss is strictly
   lower than POST-002 aggregate response loss.

2. At least four of the five capability families
   have candidate response loss no worse than the
   POST-002 baseline.

3. POST-003 exact-match count is not lower than
   POST-002 exact-match count.

4. If both baseline and candidate obtain zero exact
   matches, the result MUST NOT be described as
   demonstrated instruction-following capability.

5. Architecture, tokenizer and parameter-count
   invariants remain unchanged.

6. The candidate evaluated is byte-identical to
   the fixed POST-003 candidate.

## Interpretation rule

A formal PASS with zero exact matches may establish
only a controlled probabilistic-learning milestone.

It must not be described as:

- successful general instruction following;
- general reasoning;
- broad semantic competence;
- frontier capability;
- production readiness;
- competitiveness with modern LLMs.

Actual generated-task success requires non-zero
held-out generation performance in a future stage.

## Evaluation discipline

The formal dataset becomes immutable before scoring.

Once formal scoring begins:

- the dataset may not be edited;
- the candidate may not be retrained;
- the acceptance rule may not be changed;
- failed examples may not be replaced;
- no second formal dataset may silently replace it.

Historical EVAL-001 and EVAL-002 V4 remain frozen and
are not selection mechanisms for POST-003.
