# D0-POST-006 Formal Acceptance Policy

## Status

FROZEN BEFORE:

- POST-006 training
- POST-006 development evaluation
- POST-006 candidate selection
- POST-006 formal dataset construction
- POST-006 formal model scoring

This document defines comparison semantics only.

It does NOT authorize any of those operations.

## Accepted baseline

The formal baseline is the last formally accepted checkpoint:

local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

No development-selected checkpoint may replace this baseline
without passing this frozen formal policy.

## Candidate eligibility

Exactly one POST-006 candidate may eventually enter formal
evaluation.

That candidate must:

1. originate from a separately authorized POST-006 training
   trajectory;
2. be selected using development data only;
3. have its checkpoint identity frozen before formal exposure;
4. have no access to POST-006 formal examples during training,
   development selection, or evaluator tuning.

The retained POST-005 step-120 checkpoint is NOT automatically the
POST-006 formal candidate.

## Formal dataset freshness

POST-006 formal acceptance must use a NEW formal dataset created
under a separately frozen construction policy.

The historical dataset:

ml/data/d0_post003_formal.jsonl

is INELIGIBLE for POST-006 formal scoring.

Its contents MUST NOT be used to construct, tune, filter, select,
or validate POST-006 formal examples.

## Capability families

POST-006 formal evaluation will use exactly five capability
families.

The exact family names and dataset distribution must be frozen
before formal dataset construction.

No family may be added or removed after formal examples exist.

## Scoring unit

Both baseline and candidate must be scored against exactly the
same frozen POST-006 formal examples.

Each example produces:

- response-token cross-entropy loss
- deterministic greedy generated response
- exact-match boolean
- capability family

## Exact-match definition

Generated response and expected response are compared after the
same deterministic normalization procedure for both baseline and
candidate.

The normalization procedure must be implemented and frozen before
formal scoring.

No candidate-specific normalization is permitted.

## Aggregate response loss

Aggregate response loss is token-weighted supervised
response-token cross-entropy across the complete formal dataset.

The baseline and candidate must use exactly the same tokenization,
masking, model architecture interface, and loss implementation.

## Per-family response loss

For each of the five frozen capability families, compute
token-weighted supervised response-token cross-entropy over only
the examples belonging to that family.

## Formal acceptance conditions

ALL conditions are conjunctive.

The POST-006 candidate passes formal acceptance if and only if
ALL of the following are true.

### Condition A — non-zero capability

candidateExactMatches >= 1

### Condition B — strict exact-match improvement

candidateExactMatches > baselineExactMatches

There is no exact-match regression tolerance.

### Condition C — aggregate loss improvement

candidateAggregateResponseLoss <
baselineAggregateResponseLoss

The improvement must be strict.

Equality is not sufficient.

### Condition D — per-family retention

For every one of the five capability families:

candidateFamilyResponseLoss <=
baselineFamilyResponseLoss * 1.05

Therefore the maximum permitted response-loss regression for any
individual family is 5 percent.

Every family must satisfy this condition.

There is no "four out of five" exception.

### Condition E — zero-baseline handling

If:

baselineFamilyResponseLoss == 0

then that family passes only if:

candidateFamilyResponseLoss == 0

No percentage tolerance is applied to a zero baseline.

## Formal pass equation

formalPass = (
    candidateExactMatches >= 1
    AND
    candidateExactMatches > baselineExactMatches
    AND
    candidateAggregateResponseLoss
        < baselineAggregateResponseLoss
    AND
    everyFamilyRetentionPassed
)

No weighted voting is permitted.

No discretionary override is permitted.

No development metric may compensate for a failed formal
condition.

## Determinism

Formal scoring must use deterministic evaluation settings.

At minimum:

- model evaluation mode
- no optimizer
- no gradient update
- deterministic greedy generation
- frozen tokenizer
- frozen maximum generation length
- frozen response normalization
- same evaluator for baseline and candidate

Any stochastic sampling invalidates the formal run.

## Persistence ordering

Formal execution must persist:

1. exposure marker
2. baseline raw scoring result
3. baseline adapted result
4. candidate raw scoring result
5. candidate adapted result
6. comparison result
7. final adjudication

The baseline adapted result MUST be durably persisted before
candidate scoring begins.

The candidate adapted result MUST be durably persisted before
formal comparison begins.

## Failure semantics

After the formal exposure marker exists, any execution failure is
treated as a consumed formal exposure.

The same formal dataset MUST NOT be silently rescored.

No exposure marker may be deleted or rewritten to enable a rerun.

Failure evidence must preserve:

- stage
- timestamp
- exception type
- exception message
- last completed lifecycle operation
- persisted artifacts available at failure

## One-time exposure

Exactly one authorized formal execution may consume a sealed
POST-006 formal dataset.

A second scoring execution requires a new stage and a fresh formal
dataset.

## Promotion semantics

If formalPass is true:

the POST-006 candidate becomes the new formally accepted baseline.

If formalPass is false:

the existing POST-003 accepted baseline remains accepted.

If formal execution is invalid or incomplete:

no acceptance decision is made and the POST-003 baseline remains
the last valid accepted baseline.

## Threshold immutability

The following thresholds are now frozen:

minimum candidate exact matches:
1

exact-match requirement:
strictly greater than baseline

aggregate response-loss requirement:
strictly lower than baseline

maximum per-family response-loss regression:
5 percent

required family retention:
5 of 5 families

zero-baseline tolerance:
zero

logical combination:
ALL CONDITIONS CONJUNCTIVE

These thresholds MUST NOT be changed using future POST-006
training, development, or formal results.

Any future change requires a new governance stage rather than
rewriting this policy.
