# D0-POST-008 Formal Adjudication Policy

## Status

FROZEN BEFORE POST-008 FORMAL DATASET CONSTRUCTION AND FORMAL EXPOSURE.

This policy defines the formal capability acceptance rule for
D0-POST-008.

It does not authorize formal dataset construction.
It does not authorize formal execution.
It does not authorize checkpoint loading.
It does not authorize inference, scoring, training, or retraining.

## Policy provenance

POST-006 established formal capability acceptance semantics before
formal exposure.

POST-007 carried those semantics forward without threshold tuning.

POST-007 did not produce a valid persisted formal adjudication because
its one-time execution was consumed by an evaluation-pipeline
filesystem lifecycle failure after formal exposure.

POST-008 therefore retains the established capability acceptance
standard rather than inventing candidate-specific or
POST-008-result-specific thresholds.

No POST-008 formal rows, checkpoint outputs, model scores, or formal
results were observed in freezing this policy.

## Compared systems

The formal comparison is between:

1. the separately frozen accepted baseline checkpoint; and
2. the separately frozen retained candidate checkpoint.

Both checkpoints must be evaluated against the exact same sealed
POST-008 formal rows using identical frozen scoring, tokenization,
normalization, decoding, and aggregation procedures.

## Frozen capability families

The formal evaluation families are:

- echo
- boolean
- plural
- opposite
- world_fact

The formal dataset specification must preserve these families unless a
separate pre-dataset governance revision is explicitly created before
formal rows are constructed.

Once the dataset is constructed or exposed, family definitions must
not change.

## Required candidate conditions

A POST-008 formal PASS requires ALL of the following conditions.

### 1. Minimum exact generation

The candidate must produce at least one exact match.

    candidateExactMatches >= 1

### 2. Strict exact-match improvement

The candidate must produce strictly more exact matches than the
accepted baseline.

    candidateExactMatches > baselineExactMatches

Equality is insufficient.

### 3. Strict aggregate response-loss improvement

The candidate aggregate response loss must be strictly lower than the
accepted baseline aggregate response loss.

    candidateAggregateResponseLoss
        < baselineAggregateResponseLoss

Equality is insufficient.

### 4. Per-family retention

For every frozen capability family, candidate response loss must be no
greater than 105% of baseline response loss.

For a non-zero baseline family loss:

    candidateFamilyLoss
        <= baselineFamilyLoss * 1.05

If baseline family response loss is exactly zero:

    candidateFamilyLoss == 0.0

The zero-baseline rule prevents a zero-loss baseline family from
acquiring an arbitrary regression allowance.

All five families must satisfy the retention condition.

## Formal pass equation

The final rule is:

    formalPass = (
        candidateExactMatches >= 1
        AND
        candidateExactMatches > baselineExactMatches
        AND
        candidateAggregateResponseLoss
            < baselineAggregateResponseLoss
        AND
        allFiveFamiliesRetentionPassed
    )

No partial PASS is permitted.

Failure of any required condition produces:

    formalPass = false

## Comparator input boundary

Formal adjudication must consume only the persisted baseline and
candidate scoring results.

The adjudication layer must not:

- reopen the formal dataset;
- load either checkpoint;
- perform inference;
- rescore examples;
- regenerate responses;
- change normalization;
- alter family allocation;
- tune thresholds.

## Frozen normalization symmetry

Baseline and candidate must use the exact same frozen normalization
procedure.

Candidate-specific normalization is forbidden.

Baseline-specific normalization is forbidden.

## Threshold immutability

The following values are frozen before POST-008 formal dataset
construction and formal exposure:

- minimum candidate exact matches: 1;
- strict exact-match improvement: required;
- strict aggregate response-loss improvement: required;
- maximum per-family response-loss regression: 5%;
- zero-baseline family rule: candidate must also equal zero;
- all five family-retention checks: required;
- all conditions required for formal PASS.

These values must not be tuned after formal rows are created, after
checkpoint scoring, or after formal exposure.

## Formal result interpretation

If `formalPass` is true, the retained candidate satisfies the frozen
POST-008 capability acceptance standard on the sealed POST-008
evidence.

If `formalPass` is false, the retained candidate does not satisfy that
standard on the sealed POST-008 evidence.

The result must be preserved regardless of outcome.

A formal failure does not authorize a retry, threshold change,
candidate replacement, dataset repair, or retraining within POST-008.

## Training boundary

This policy does not authorize:

- training;
- retraining;
- fine-tuning;
- candidate modification;
- new candidate selection.

Any later training activity requires a separately governed stage.

## Current execution boundary

At policy freeze time:

- POST-008 formal dataset does not exist;
- POST-008 formal dataset has not been opened;
- no POST-008 real checkpoint has been loaded;
- no POST-008 real model inference has occurred;
- no POST-008 real scoring has occurred;
- no POST-008 formal exposure has started;
- real POST-008 execution remains disabled;
- formal execution is not authorized.

## Next permitted activity

The next permitted stage is to bind the frozen adjudication policy to
a dedicated POST-008 adjudicator implementation and test that
implementation exclusively with synthetic/development-safe fixtures.

The real POST-008 formal dataset must remain unconstructed until the
remaining pre-dataset governance requirements are satisfied.
