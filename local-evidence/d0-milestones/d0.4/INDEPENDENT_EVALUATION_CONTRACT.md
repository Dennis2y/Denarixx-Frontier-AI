# Denarixx Frontier AI — D0.4 Independent Evaluation Contract

## Stage

D0.4 — Complete independent evaluation.

## Status

CONTRACT FROZEN BEFORE D0.4 EVALUATION EXECUTION.

This document defines the D0.4 evaluation boundary.

Creating this contract does NOT execute an evaluation and does NOT
constitute D0.4 completion.

## Canonical D0 checkpoint

D0.4 evaluates the already accepted canonical D0 checkpoint:

local-checkpoints/d0-post002-accepted.pt

Expected SHA-256:

31038f7801ae64f99aad4ec88e7aaa276917be9dec84ef0944b121578a36ca97

D0.4 MUST NOT retrain, modify, replace, or promote another checkpoint.

## Purpose

D0.4 is an independent evaluation milestone for the already accepted
D0 model.

Its purpose is evaluation and evidence generation, not model selection.

D0.4 MUST NOT:

- train or retrain D0;
- tune hyperparameters;
- select among candidate checkpoints;
- modify the tokenizer;
- modify model architecture;
- change the canonical checkpoint;
- use evaluation results to improve the evaluated checkpoint;
- reopen a completed post-training selection stage.

## Historical evaluations

D0-EVAL-001 and D0-EVAL-002 V4 are historical frozen evaluations.

Their identities are:

D0-EVAL-001 language-model data:

7ebff5e6dd3ef0d22fc4424296ec0ad8806bf304068328c0c74d2d5b1235b6e4

D0-EVAL-001 instruction data:

78896135affacc51fd22d5cf8e0e68798d69f32b415220b9c137f2855be21bd5

D0-EVAL-002 V4 language-model data:

add74fe6a0402708d0263e804f9c2f063411b16e6a12906cc64c5620950c0b3b

D0-EVAL-002 V4 instruction data:

f4016c10c1b493a8ba5e2bc71d9435436e703aec64f4bd1890e262d1865c1f2e

These historical evaluations MUST remain immutable.

D0.4 MUST NOT rerun them merely to manufacture new independent
evaluation evidence.

Their previously recorded results may be cited as historical evidence.

## Independence requirement

D0.4 requires evaluation evidence that is independent of the
post-training selection process that accepted POST-002.

Therefore historical EVAL-001 and EVAL-002 V4 results alone are not
sufficient to complete D0.4.

A separate D0.4 evaluation protocol must be frozen before any new
D0.4 model scoring occurs.

## Later POST stages

POST-006 and POST-007 belong to later experimental governance and
formal-evaluation work.

Their exposed formal datasets and failed execution attempts MUST NOT
be repurposed as D0.4 evaluation data.

POST-006 MUST NOT be rerun.

POST-007 MUST NOT be rerun as part of D0.4.

Their formal datasets MUST NOT be opened, copied, transformed,
repaired, or used as D0.4 evaluation data.

## D0.4 evaluation-data requirement

Any new D0.4 evaluation data must be governed by a separately frozen
D0.4 protocol before model scoring.

That protocol must define, before results exist:

1. evaluation objective;
2. evaluation families or capabilities;
3. dataset construction rules;
4. tokenizer compatibility requirements;
5. context-length compatibility requirements;
6. dataset size;
7. dataset identity and SHA-256;
8. scoring metrics;
9. deterministic generation/scoring behavior;
10. evidence persistence;
11. failure behavior;
12. one-time or repeatability semantics;
13. completion criteria.

No completion criterion may be selected after observing D0.4 results.

## Compatibility requirement

Before any D0.4 dataset is frozen for scoring, it must be demonstrated
to be compatible with the canonical checkpoint tokenizer and context
length.

Compatibility validation must occur before evaluation exposure.

The tokenizer MUST NOT be changed to accommodate evaluation data.

Evaluation examples MUST NOT be silently normalized, repaired, or
truncated merely to force compatibility.

## Evaluation semantics

D0.4 evaluates exactly the canonical accepted D0 checkpoint.

D0.4 is not a checkpoint comparison or candidate-selection stage.

Results must therefore be reported as measurements of the accepted
D0 model rather than evidence for selecting a replacement model.

## Scope of claims

D0.4 completion, when eventually established, may support only claims
demonstrated by its frozen evaluation protocol and recorded evidence.

It must not automatically claim:

- frontier-model capability;
- production readiness;
- broad language competence;
- general intelligence;
- safety certification;
- robustness outside the tested scope.

## Evidence discipline

D0.4 evidence must preserve:

- canonical checkpoint identity;
- evaluation protocol identity;
- evaluation-data identity;
- evaluator identity;
- raw result identity;
- execution status;
- completion/adjudication result.

Evidence should be create-once where practical.

Existing evidence must not be silently overwritten.

## Current authorization

AUTHORIZED BY THIS CONTRACT:

- creation of D0.4 governance evidence;
- read-only identity verification;
- design of the D0.4 evaluation protocol;
- design of compatibility validation;
- synthetic testing that does not score the canonical checkpoint
  against future D0.4 evaluation data.

NOT AUTHORIZED BY THIS CONTRACT:

- D0.4 model scoring;
- formal dataset exposure;
- training;
- retraining;
- checkpoint modification;
- tokenizer modification;
- EVAL-001 rerun;
- EVAL-002 V4 rerun;
- POST-006 rerun;
- POST-007 rerun;
- lifecycle completion of D0.4.

## Next required stage

Freeze the detailed D0.4 evaluation protocol before constructing or
executing the independent evaluation.

