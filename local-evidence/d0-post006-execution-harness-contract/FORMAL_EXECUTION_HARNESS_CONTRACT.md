# D0-POST-006 Formal Execution Harness Contract

## Status

FROZEN BEFORE REAL FORMAL EXPOSURE.

This contract specifies the execution lifecycle for a future
D0-POST-006 formal evaluation.

Freezing this contract does NOT authorize formal execution.

It does NOT authorize model scoring.

It does NOT authorize parsing the sealed formal dataset.

It does NOT authorize creation of FORMAL_EXPOSURE_STARTED.

It does NOT authorize training.

## Fixed formal inputs

The formal evaluation will compare exactly two checkpoints:

1. the last formally accepted POST-003 baseline
2. the retained POST-005 step-120 development candidate

against exactly one sealed fresh POST-006 formal dataset.

No other checkpoint may be substituted.

No other formal dataset may be substituted.

## Historical formal isolation

ml/data/d0_post003_formal.jsonl remains permanently outside
POST-006 formal scoring.

It must not be opened, parsed, scored, copied, transformed,
or used to influence the POST-006 result.

## Pre-exposure checks

Before formal exposure begins, the future execution harness must:

1. verify all frozen governance manifests
2. verify the sealed POST-006 dataset SHA-256 without parsing rows
3. verify baseline checkpoint SHA-256 without loading the model
4. verify candidate checkpoint SHA-256 without loading the model
5. verify no prior POST-006 FORMAL_EXPOSURE_STARTED exists
6. verify no prior formal result/evidence path exists
7. fail closed on any mismatch

These checks are pre-exposure operations.

## Exposure boundary

FORMAL_EXPOSURE_STARTED must be created immediately before the
first operation that loads/parses the sealed POST-006 formal rows
for model scoring.

Once that marker exists, the exposure is irreversible.

The marker must never be deleted, rewritten, bypassed, or reset.

A failed execution after exposure starts must remain recorded as
an exposed formal attempt.

## Formal row handling

The sealed dataset may be loaded only by the separately authorized
formal execution.

Rows must not be printed to terminal output.

Expected responses must not be printed.

Formal examples must not be copied into ordinary logs.

Structural validation after loading must not modify the dataset.

## Baseline-first execution

The accepted baseline must be scored before the candidate.

The complete baseline scoring result must be persisted before
candidate scoring begins.

If baseline scoring fails, candidate scoring must not begin.

If baseline persistence fails, candidate scoring must not begin.

## Candidate execution

Candidate scoring may begin only after baseline result persistence
has succeeded.

The complete candidate scoring result must be persisted before
formal comparison begins.

If candidate scoring fails, all already-created evidence must be
preserved.

## Formal comparison

Formal comparison must consume the persisted baseline and
candidate results.

It must use the frozen POST-006 formal acceptance semantics.

No threshold, metric, tolerance, normalization rule, or family
requirement may be changed after exposure.

## Failure behavior

Any failure must:

1. return non-zero status
2. preserve stderr
3. preserve exit status
4. preserve the exposure marker
5. preserve already-created baseline evidence
6. preserve already-created candidate evidence
7. write failure evidence when possible
8. prevent silent restart
9. prevent overwrite
10. never reopen the historical formal dataset

A failure after exposure begins does not restore an unexposed
state.

## One-time execution

Formal exposure is one-time.

Once FORMAL_EXPOSURE_STARTED exists, rerunning the formal
execution is forbidden unless a future governance stage explicitly
defines a new independent formal evaluation.

The POST-006 harness must fail closed if invoked again.

## Evidence immutability

Formal execution evidence must be create-once.

Existing baseline results must not be overwritten.

Existing candidate results must not be overwritten.

Existing final adjudication must not be overwritten.

Existing failure evidence must not be silently replaced.

## No training feedback

The POST-006 formal dataset and all formal results must never be
used for:

- training
- retraining
- development evaluation
- checkpoint selection
- hyperparameter selection
- threshold tuning
- prompt tuning
- benchmark editing

## Synthetic rehearsal requirement

Before real formal execution may be authorized, the complete
execution harness must be implemented and exercised end-to-end
using synthetic rows and synthetic scoring results only.

That rehearsal must verify at minimum:

1. pre-exposure identity checks
2. exposure-marker timing
3. row loading lifecycle
4. baseline-first execution
5. baseline persistence
6. candidate execution
7. candidate persistence
8. persisted-result comparison
9. final adjudication persistence
10. baseline failure behavior
11. failure after baseline persistence
12. failure after candidate persistence
13. rerun prevention
14. overwrite prevention
15. evidence preservation
16. non-zero failure status
17. historical-formal isolation

The rehearsal must not parse the sealed real POST-006 formal rows.

The rehearsal must not load either real checkpoint.

## Authorization boundary

This contract does not authorize formal execution.

After implementation and successful synthetic rehearsal, a
separate formal-execution authorization gate is required.

Only that future gate may authorize:

- real checkpoint loading
- sealed POST-006 formal row parsing
- FORMAL_EXPOSURE_STARTED creation
- one-time real formal scoring

Until then, formal execution remains locked.
