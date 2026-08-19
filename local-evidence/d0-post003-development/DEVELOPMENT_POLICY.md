# D0-POST-003 Development Evaluation Policy

## Status

FROZEN BEFORE DEVELOPMENT SCORING

## Candidate

The only candidate eligible for this development
evaluation is:

local-checkpoints/d0-post003-capability-seed42.pt

Candidate SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

No alternative checkpoint may be substituted.

## Development dataset

The frozen development dataset is:

ml/data/d0_post003_dev.jsonl

SHA-256:

dc7beefa2615b664438c445f5b13f6a579ddd2fff55b91420e7fc29e9c47c45b

It contains exactly five examples, one from each
POST-003 capability family:

- echo
- binary
- transform
- qa
- semantic

## Evaluation purpose

This evaluation asks whether the fixed POST-003
candidate shows evidence of generalizing the controlled
instruction mappings to the held-out development
examples.

This is a development decision only.

It is NOT formal POST-003 acceptance.

## Metrics

The evaluator must record:

1. response-only cross-entropy loss for every example
2. aggregate token-weighted response loss
3. response perplexity
4. deterministic greedy generated response
5. exact match for every example
6. aggregate exact-match count and rate
7. per-family result

Generation must use deterministic greedy decoding.

No sampling is permitted.

## Comparison baseline

The accepted POST-002 checkpoint must also be scored on
the exact same frozen POST-003 development set.

This baseline comparison is permitted because POST-002
was fixed before POST-003 development data existed and
is not a POST-003 candidate selected using this set.

## Development PASS rule

POST-003 passes the development gate only if BOTH of
the following are true:

1. POST-003 aggregate response loss is lower than the
   accepted POST-002 checkpoint on the frozen POST-003
   development set.

2. POST-003 exact-match count is not lower than the
   accepted POST-002 checkpoint.

If either condition fails:

DEVELOPMENT FAIL

If both conditions pass:

DEVELOPMENT PASS

## Interpretation

A DEVELOPMENT PASS means only that the fixed POST-003
candidate improved held-out behavior relative to its
POST-002 starting checkpoint under this small
development protocol.

It does not establish formal acceptance.

## Prohibited actions after scoring

Development results must NOT be used to:

- retrain POST-003
- replace the candidate
- change the candidate step
- change the learning rate
- change lambda
- change batch sizes
- change the seed
- modify POST-003 training data
- modify the development set

A failed result remains a failed POST-003 experiment.

## Historical evaluations

D0-EVAL-001 and D0-EVAL-002 V4 must NOT be evaluated
during this development stage.

## Formal evaluation

If the development gate passes, a new untouched
POST-003 formal evaluation protocol must be designed
and frozen before formal scoring.

The formal evaluation must test capability acquisition
and retention without using this development set as
formal acceptance evidence.
