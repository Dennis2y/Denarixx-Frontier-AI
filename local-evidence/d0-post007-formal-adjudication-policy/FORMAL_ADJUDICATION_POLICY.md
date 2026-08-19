# D0-POST-007 Formal Adjudication Policy

## Status

FROZEN BEFORE FORMAL EXPOSURE.

This policy defines the formal comparison rule for D0-POST-007.

It does not authorize formal execution.
It does not authorize dataset parsing.
It does not authorize checkpoint loading.
It does not authorize inference or scoring.

## Policy provenance

D0-POST-006 established a frozen formal acceptance and evaluator
contract before its formal execution attempt.

POST-006 did not reach formal adjudication because its execution
pipeline failed before a valid comparison could be completed.

That failure was classified as an evaluation-pipeline compatibility
failure rather than a candidate capability failure.

D0-POST-007 therefore carries forward the already frozen POST-006
formal acceptance semantics without threshold tuning, weakening,
strengthening, or candidate-specific adaptation.

The fresh POST-007 dataset changes the formal evidence set.

It does not change the previously frozen capability acceptance
standard.

## Compared systems

The formal comparison is between:

1. the accepted baseline checkpoint; and
2. the retained candidate checkpoint.

Both systems must be scored against the exact same sealed POST-007
formal rows using the same frozen scoring and normalization path.

## Required candidate conditions

A D0-POST-007 formal PASS requires ALL of the following.

### 1. Minimum exact generation

The candidate must produce at least one exact match.

candidateExactMatches >= 1

### 2. Strict exact-match improvement

The candidate must produce strictly more exact matches than the
accepted baseline.

candidateExactMatches > baselineExactMatches

### 3. Strict aggregate response-loss improvement

The candidate aggregate response loss must be strictly lower than
the accepted baseline aggregate response loss.

candidateAggregateResponseLoss <
baselineAggregateResponseLoss

### 4. Five-family retention

For each frozen family:

- echo
- boolean
- plural
- opposite
- world_fact

candidate family response loss must be no greater than 105% of the
accepted baseline family response loss.

For a non-zero baseline family loss:

candidateFamilyLoss <= baselineFamilyLoss * 1.05

If the accepted baseline family response loss is exactly zero, the
candidate family response loss must also be exactly zero.

Every one of the five families must pass this retention rule.

## Formal pass equation

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

## Frozen normalization symmetry

The exact same response normalization and exact-match procedure must
be used for baseline and candidate.

Candidate-specific normalization is forbidden.

Baseline-specific normalization is forbidden.

## Forbidden adaptations

After formal exposure begins, the following are forbidden:

- changing any threshold;
- changing the minimum exact-match requirement;
- changing the strict exact-match improvement rule;
- changing the aggregate response-loss rule;
- changing the 5% family-regression tolerance;
- changing the zero-baseline family rule;
- removing a family;
- changing normalization;
- candidate-specific preprocessing;
- baseline-specific preprocessing;
- modifying expected responses;
- repairing formal rows;
- selecting a new candidate based on POST-007 results.

## Failure interpretation

If formalPass is true, the retained candidate satisfies the frozen
D0-POST-007 capability acceptance standard.

If formalPass is false, the retained candidate does not satisfy that
standard on the sealed POST-007 evidence.

The formal result must be preserved regardless of outcome.

## Current authorization boundary

This policy freeze does NOT authorize:

- parsing ml/data/d0_post007_formal.jsonl;
- loading the accepted baseline for scoring;
- loading the retained candidate;
- model inference;
- response-loss computation;
- exact-match scoring;
- formal comparison;
- creation of FORMAL_EXPOSURE_STARTED.

A separate frozen dependency adapter, execution harness, and
single-use formal execution authorization are required before formal
exposure may begin.
