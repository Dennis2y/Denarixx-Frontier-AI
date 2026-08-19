# D0-POST-006 Formal Evaluator Contract

## Status

FROZEN BEFORE FORMAL MODEL EXPOSURE.

This contract defines the required POST-006 formal evaluator
behavior.

It does NOT authorize formal evaluation.

It does NOT authorize model loading.

It does NOT authorize model scoring.

It does NOT authorize creation of FORMAL_EXPOSURE_STARTED.

It does NOT authorize training or retraining.

## Evaluation subjects

The future evaluator must compare exactly:

1. the last formally accepted POST-003 baseline
2. the retained POST-005 step-120 development candidate

No other checkpoint may be substituted.

## Formal dataset

The future evaluator must use exactly the sealed fresh POST-006
formal dataset whose identity was frozen before evaluator execution.

The historical POST-003 formal dataset is ineligible.

## Required scoring outputs

For both baseline and candidate, the evaluator must persist:

- aggregate response-token loss
- exact-match count
- per-family response-token loss
- per-family example count
- dataset identity
- checkpoint identity

The baseline scoring result must be persisted successfully before
candidate scoring begins.

The candidate scoring result must be persisted successfully before
formal comparison begins.

## Frozen acceptance rule

Formal PASS requires every condition below.

### A. Minimum candidate exact capability

candidateExactMatches >= 1

### B. Strict exact-match improvement

candidateExactMatches > baselineExactMatches

### C. Strict aggregate response-loss improvement

candidateAggregateResponseLoss <
baselineAggregateResponseLoss

### D. All-five-family retention

For every capability family with baseline loss greater than zero:

candidateFamilyLoss <= baselineFamilyLoss * 1.05

All five capability families must satisfy the rule.

### E. Zero-baseline handling

If baselineFamilyLoss == 0:

candidateFamilyLoss must equal 0.

### Conjunction

All acceptance conditions are conjunctive.

Failure of any condition means formal FAIL.

No threshold may be changed after formal exposure.

## Exact-match behavior

Generated model response must be evaluated using the already-frozen
normalization/exact-match behavior.

No manual judgment may change an exact-match result.

## Evidence ordering

The future formal execution must enforce:

1. authorization verification
2. identity verification
3. rerun-prevention check
4. exposure marker creation
5. sealed formal-row loading
6. baseline scoring
7. baseline-result persistence
8. candidate scoring
9. candidate-result persistence
10. formal comparison
11. final-result persistence

If execution fails after exposure begins, the exposure marker must
remain permanently preserved.

Formal execution must never silently restart.

## Failure semantics

Any execution-harness failure after exposure begins must:

- return non-zero status
- preserve the exposure marker
- preserve already-written scoring evidence
- persist failure evidence
- prohibit automatic rerun
- make no PASS or FAIL claim unless the complete comparison was
  successfully produced

## Synthetic rehearsal

Before real formal authorization, the evaluator implementation must
be tested using synthetic rows and/or synthetic scoring results.

Synthetic rehearsal must test at least:

- PASS case
- minimum-exact failure
- strict-exact-improvement failure
- aggregate-loss failure
- individual-family retention failure
- zero-baseline failure
- all-five-family conjunction
- baseline persistence before candidate execution
- candidate persistence before comparison
- injected failure after baseline persistence
- rerun prevention
- evidence overwrite prevention

Synthetic rehearsal must not load either real checkpoint.

Synthetic rehearsal must not parse the sealed POST-006 formal rows.

## Authorization boundary

Freezing this evaluator contract does not authorize formal model
exposure.

After implementation and successful synthetic rehearsal, a separate
formal-execution authorization gate is required.

Until that gate exists:

FORMAL_EXPOSURE_STARTED must remain absent.
