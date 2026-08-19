# Denarixx Frontier AI — D0.4 Independent Evaluation Protocol

## Status

FROZEN BEFORE DATASET CONSTRUCTION AND BEFORE MODEL SCORING.

This protocol is subordinate to the frozen D0.4 Independent
Evaluation Contract.

Freezing this protocol does NOT authorize D0.4 model evaluation.

## Evaluated checkpoint

Exactly one checkpoint is evaluated:

local-checkpoints/d0-post002-accepted.pt

Expected SHA-256:

31038f7801ae64f99aad4ec88e7aaa276917be9dec84ef0944b121578a36ca97

No checkpoint comparison or candidate selection occurs in D0.4.

## Evaluation objective

D0.4 independently measures the accepted D0 model's behavior on
fresh, previously unscored evaluation material.

The evaluation is intended to characterize the accepted research
checkpoint within its deliberately small architecture, tokenizer,
context length, and capability scope.

The evaluation is not intended to demonstrate frontier capability,
production readiness, general intelligence, or broad language
competence.

## Independence

D0.4 evaluation examples must be newly constructed for D0.4.

They must not be copied from:

- D0 training data;
- D0 SFT data;
- development-selection datasets;
- D0-EVAL-001;
- D0-EVAL-002 V4;
- POST-003 historical formal data;
- POST-006 formal data;
- POST-007 formal data.

Previously exposed formal datasets must not be transformed,
paraphrased, repaired, or recycled into D0.4.

Historical evaluation results may remain historical context but
must not determine D0.4 example content after this protocol freeze.

## Evaluation families

D0.4 uses five capability families:

1. literal_response
2. short_completion
3. simple_transformation
4. constrained_generation
5. basic_instruction_following

Each family must contain exactly 5 examples.

Total D0.4 examples:

25

Family membership must be recorded explicitly in each example.

## Dataset schema

The future D0.4 evaluation dataset must use JSON Lines.

Every row must contain exactly:

- instruction
- response
- family

All three values must be non-empty strings.

No additional scoring hints, expected losses, model outputs,
checkpoint-specific annotations, or hidden selection metadata may
be stored in the dataset.

## Dataset construction

Dataset construction occurs only after this protocol is frozen.

Construction must occur without scoring the canonical model.

The canonical model must not be queried to decide which examples
are retained.

Examples must not be replaced because the model is expected to
perform poorly on them.

Examples must not be selected because the model is expected to
perform well on them.

## Freshness audit

Before the dataset can be sealed, a deterministic audit must check
for prohibited exact overlap against available historical
training, development, and evaluation material.

At minimum, the audit must reject:

- exact normalized instruction overlap;
- exact normalized response overlap where inappropriate for the
  defined task;
- exact instruction-response pair overlap.

The audit must not open protected later formal datasets whose
governance prohibits reuse or inspection.

Those datasets are excluded by provenance and identity rather than
by reopening their contents.

## Tokenizer compatibility

Every proposed example must be validated using the exact tokenizer
metadata belonging to the canonical accepted checkpoint.

Compatibility validation is permitted before dataset sealing.

For every row:

1. the formatted instruction must encode successfully;
2. the expected response must encode successfully;
3. no unsupported character may be silently removed;
4. no unsupported character may be substituted;
5. tokenizer behavior must not be modified for evaluation.

Any incompatible proposed row must be rejected before sealing.

## Context compatibility

Every proposed example must fit the canonical model context length
through the exact evaluation formatting path.

No example may be truncated to force compatibility.

At least one supervised response token must remain.

Compatibility failure causes rejection of the proposed example
before sealing.

## Dataset sealing

After all 25 examples pass:

- structural validation;
- family-count validation;
- freshness validation;
- tokenizer validation;
- context validation;

the dataset may be frozen.

The frozen dataset must receive a SHA-256 identity.

After freezing, no row may be edited, replaced, reordered for
selection purposes, repaired, or tuned based on model results.

A changed dataset requires a new explicit governance decision and
must not silently inherit the previous dataset identity.

## Evaluation metrics

D0.4 records the following metrics:

1. aggregate response loss;
2. response perplexity;
3. exact-match count;
4. exact-match rate;
5. per-family response loss;
6. per-family exact-match count.

Response loss must be token-weighted across supervised response
tokens.

## Exact-match semantics

Exact match means the generated response equals the expected
response under one frozen normalization operation:

- preserve semantic characters;
- remove only terminal generation-control artifacts if the
  established generation implementation requires it;
- do not lowercase;
- do not strip meaningful punctuation;
- do not substitute unsupported characters;
- do not apply candidate-specific normalization.

The exact normalization implementation must be frozen before real
D0.4 scoring.

## Generation

Generation must be deterministic.

The evaluator must use the canonical model in evaluation mode.

No sampling-based checkpoint selection is permitted.

Generation parameters and stopping behavior must be frozen before
execution.

## Evaluator

A dedicated D0.4 evaluator or a specifically frozen compatible
evaluation backend must be identified by SHA-256 before execution.

The evaluator must:

- verify checkpoint identity;
- verify dataset identity;
- use the checkpoint's frozen tokenizer;
- preserve the model architecture;
- perform no training;
- perform no optimizer updates;
- perform no checkpoint writes;
- produce deterministic scoring evidence.

## Completion semantics

D0.4 is a measurement milestone, not a promotion contest.

Therefore completion does NOT require the model to beat another
checkpoint.

D0.4 may be marked complete only if:

1. this protocol remains unchanged;
2. the canonical checkpoint identity is verified;
3. a fresh D0.4 dataset is validly constructed and sealed;
4. compatibility validation passes before scoring;
5. evaluator identity is frozen;
6. evaluation executes successfully;
7. all required aggregate metrics are produced;
8. all five families produce metrics;
9. execution evidence is persisted;
10. no governance boundary is violated.

A poor model score does not by itself invalidate D0.4 completion.

A pipeline failure, compatibility failure after sealing, identity
mismatch, incomplete metrics, or governance violation prevents
successful D0.4 completion until handled by a separately documented
recovery decision.

## Result interpretation

The final D0.4 evidence must distinguish:

- successful evaluation execution;
- measured model capability;
- D0.4 lifecycle completion.

Completion means the independent evaluation was validly performed.

It does not mean the model achieved a particular external capability
standard.

## Evidence

The future D0.4 execution package must preserve at minimum:

- contract SHA-256;
- protocol SHA-256;
- checkpoint path and SHA-256;
- dataset path and SHA-256;
- evaluator path and SHA-256;
- compatibility-validation evidence;
- aggregate metrics;
- per-family metrics;
- execution status;
- completion adjudication.

Raw dataset rows and expected responses should not be printed in
ordinary terminal output during evaluation.

## Failure behavior

The future execution controller must fail closed on:

- checkpoint identity mismatch;
- dataset identity mismatch;
- evaluator identity mismatch;
- structural dataset failure;
- tokenizer incompatibility;
- context incompatibility;
- incomplete scoring result;
- nondeterministic evaluator configuration.

Failure evidence must not be silently rewritten as success.

## Historical isolation

D0-EVAL-001 and D0-EVAL-002 V4 must not be rerun for D0.4.

POST-006 must not be rerun.

POST-007 must not be rerun.

Their exposed formal datasets are not D0.4 data.

## Current authorization after protocol freeze

AUTHORIZED:

- D0.4 dataset-construction tooling;
- construction of proposed fresh D0.4 examples;
- pre-seal structural validation;
- pre-seal freshness validation;
- pre-seal tokenizer compatibility validation;
- pre-seal context compatibility validation;
- evaluator/controller implementation;
- synthetic evaluator testing.

NOT YET AUTHORIZED:

- scoring the canonical checkpoint on D0.4 data;
- final D0.4 evaluation execution;
- D0.4 completion;
- lifecycle transition to D0.5;
- training or retraining;
- checkpoint modification;
- tokenizer modification;
- historical evaluation reruns.

## Next required operation

Implement a D0.4 pre-seal compatibility and freshness gate.

That gate must be tested without performing D0.4 model scoring.

Only after the gate is validated may fresh D0.4 evaluation examples
be constructed and sealed under this protocol.
