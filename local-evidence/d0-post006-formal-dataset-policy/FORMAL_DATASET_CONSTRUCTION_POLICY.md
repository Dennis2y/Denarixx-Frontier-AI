# D0-POST-006 Formal Dataset Construction Policy

## Status

FROZEN BEFORE FORMAL DATASET CREATION.

This document defines how a future fresh D0-POST-006 formal
acceptance dataset must be constructed.

This policy does NOT create that dataset.

This policy does NOT authorize model scoring.

This policy does NOT authorize training.

## Independence requirement

The D0-POST-006 formal dataset must be newly authored for POST-006.

It must not copy, paraphrase, transform, translate, mutate, or
programmatically derive examples from:

- ml/data/d0_post003_formal.jsonl
- POST-004 formal evidence
- POST-005 development examples
- POST-006 training examples
- POST-006 development examples

The historical formal dataset must remain unopened during
construction of the new formal dataset.

## Model-blind construction

Formal examples must be authored without querying or scoring:

- the accepted POST-003 baseline
- the retained POST-005 development checkpoint
- any POST-006 training checkpoint
- any POST-006 candidate checkpoint

Formal examples must not be selected because a candidate succeeds
or fails on them.

No model output may be used to edit, filter, replace, simplify,
strengthen, or otherwise tune a formal example.

## Frozen capability families

Exactly five families will be used:

1. echo
2. boolean
3. plural
4. opposite
5. world_fact

No additional family is permitted.

No family may be removed.

## Dataset size

Exactly 25 examples.

Exactly 5 examples per capability family.

The final dataset therefore has the fixed distribution:

echo: 5
boolean: 5
plural: 5
opposite: 5
world_fact: 5

## Record schema

Each JSONL row must contain exactly these semantic fields:

{
  "family": "...",
  "instruction": "...",
  "response": "..."
}

Additional metadata must not be required by the evaluator.

family must be one of the five frozen family names.

instruction must be a non-empty string.

response must be a non-empty string.

## Response form

Each expected response must be short and objectively determined.

Expected responses must not require:

- subjective judgment
- explanation
- multiple acceptable phrasings
- current events
- web access
- private information
- specialized external databases

The expected answer must be deterministically gradeable by the
frozen normalization/exact-match procedure.

## Family construction rules

### echo

Five instructions requiring reproduction of a supplied ordinary
word.

Each target word must be different.

Targets must not be copied from historical formal or development
datasets.

### boolean

Five simple binary propositions.

Expected response must be exactly:

true

or:

false

The set must contain at least two true and at least two false
responses.

### plural

Five simple regular English singular-to-plural transformations.

Only unambiguous regular +s forms are allowed.

Avoid irregular plurals.

Avoid words requiring +es, spelling replacement, or disputed forms.

### opposite

Five simple common-word antonym tasks.

Each must have one intended short answer in the context of this
benchmark.

Avoid words with several equally plausible antonyms.

### world_fact

Five simple, stable, timeless propositions about ordinary physical
or human-world facts.

Expected response must be exactly:

true

or:

false

The set must contain at least two true and at least two false
responses.

No current affairs or time-sensitive facts are allowed.

## Lexical independence

The target responses for echo, plural, and opposite families must
not duplicate target responses used in POST-006 training or
development data.

The construction process may inspect POST-006 training and
development DATA TEXT solely for duplicate prevention.

It must not inspect model outputs or evaluation results.

Historical formal data must not be opened even for duplicate
checking.

## Duplicate prohibition

Within the new formal dataset:

- no instruction may repeat
- no complete row may repeat
- echo target words must be unique
- plural source words must be unique
- opposite source words must be unique

## Difficulty policy

Examples should test the declared capability directly.

They must not deliberately introduce:

- trick questions
- adversarial formatting
- obscure vocabulary
- ambiguous grammar
- hidden multi-step reasoning

POST-006 formal acceptance is intended to measure retained/basic
capability under fresh examples, not adversarial robustness.

## Ordering

The 25 examples must be placed in a deterministic interleaved
family order.

For rounds 1 through 5:

1. echo
2. boolean
3. plural
4. opposite
5. world_fact

This produces exactly 25 rows.

No model performance may influence ordering.

## Construction seed

The dataset construction procedure must use the fixed governance
seed:

6006

If deterministic programmatic selection from an independently
authored candidate pool is used, seed 6006 must control selection.

The candidate pool itself must be authored without model feedback.

## Dataset identity

After construction, the complete JSONL file must be sealed by
SHA-256 before any model is scored against it.

The SHA-256 identity must be persisted in a construction manifest.

Once sealed:

- examples may not be edited
- ordering may not change
- expected responses may not change
- family labels may not change

Any required modification invalidates that dataset and requires a
new governance stage or a new explicitly authorized construction
before exposure.

## Pre-exposure validation

Before any model scoring, a validator must establish:

1. exactly 25 rows
2. exactly five families
3. exactly five rows per family
4. valid schema
5. non-empty instructions
6. non-empty responses
7. no duplicate instructions
8. valid boolean/world_fact responses
9. deterministic interleaved ordering
10. lexical duplicate checks against permitted training/development
    text
11. sealed SHA-256 identity

Validation must not execute a model forward pass.

## Exposure boundary

Dataset construction and structural validation do NOT constitute
formal model exposure.

Formal exposure begins only when an authorized evaluator first
loads the sealed formal rows for model scoring.

Before that event:

FORMAL_EXPOSURE_STARTED must not exist.

## Separation from training

The new formal dataset must never become:

- training input
- retention input
- development input
- candidate-selection input
- hyperparameter-selection input
- prompt-tuning input
- threshold-tuning input

## Authorization boundary

Freezing this policy does NOT authorize creation of the dataset.

A separate construction authorization is required.

That authorization must reference the SHA-256 identity of this
policy and must still prohibit model scoring.

## Next operation

After this policy is frozen:

create a synthetic structural validator and test the construction
pipeline without creating or reading real POST-006 formal examples.

Only after that rehearsal passes may a separate formal-dataset
construction authorization be considered.
