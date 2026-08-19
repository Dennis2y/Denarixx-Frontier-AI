# D0-POST-003 Capability Expansion

## Status

PREDECLARED BEFORE TRAINING

## Starting checkpoint

D0-POST-002 accepted checkpoint.

POST-003 must preserve:

- architecture,
- tokenizer identity,
- parameter count,
- context length.

## Research question

Can D0 learn several controlled instruction mappings
instead of only the original trivial `say X` mapping,
while preserving useful language-model behavior?

## Capability families

POST-003 initially studies:

1. echo
2. binary classification
3. lexical transformation
4. short question-answer mappings
5. controlled semantic mappings

This remains a tiny-model experiment.

POST-003 does not claim general reasoning.

## Primary hypothesis

A capability-diverse response-only SFT dataset combined
with the already accepted language-model retention
objective can improve held-out instruction behavior
without unacceptable retention regression.

## Architecture policy

POST-003 does NOT change:

- vocab size
- tokenizer
- context length
- hidden size
- layer count
- attention-head count
- positional encoding

Architecture expansion belongs to a separate stage.

## Evaluation discipline

D0-EVAL-001 and D0-EVAL-002 V4 are historical frozen
confirmation datasets.

They MUST NOT be used:

- to select POST-003 hyperparameters,
- to select training duration,
- to choose among POST-003 candidates,
- or to repeatedly tune POST-003.

A new evaluation protocol must be established before
formal POST-003 acceptance testing.

## Training discipline

No POST-003 training may begin until:

1. candidate training data passes tokenizer coverage,
2. every supervised sequence fits context,
3. duplicates are rejected,
4. capability-family counts are recorded,
5. held-out development examples are separated,
6. training configuration is predeclared.

## Scientific scope

Success at POST-003 would establish only that this
small D0 model can acquire a broader set of controlled
instruction behaviors.

It would not establish frontier capability,
general reasoning, broad knowledge, production
readiness, or competitive performance against
large language models.
