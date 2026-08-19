# D0-POST-006 Formal Dataset Construction Authorization

Status:

AUTHORIZED FOR ONE FRESH FORMAL DATASET CONSTRUCTION

## Scope

This authorization permits construction of exactly one fresh
D0-POST-006 formal dataset according to the already frozen:

- FORMAL_ACCEPTANCE_POLICY.md
- FORMAL_DATASET_CONSTRUCTION_POLICY.md

The dataset must contain exactly:

- 25 examples
- 5 capability families
- 5 examples per family

Families:

1. echo
2. boolean
3. plural
4. opposite
5. world_fact

Construction seed:

6006

Ordering:

interleaved-five-rounds

## Model blindness

Construction must remain model-blind.

No checkpoint may be loaded.

No model forward pass may occur.

No model output may be inspected or used to author, select,
filter, replace, simplify, or edit an example.

## Historical dataset isolation

The historical formal dataset:

ml/data/d0_post003_formal.jsonl

is NOT eligible as construction input.

Its contents must not be opened, parsed, copied, transformed,
sampled, paraphrased, or used as a source for POST-006 examples.

## Formal exposure

Dataset construction itself does not begin model formal exposure.

FORMAL_EXPOSURE_STARTED MUST NOT be created during construction.

Formal exposure begins only if a separately authorized model-scoring
stage later loads the fresh formal dataset for model evaluation.

## Authorized operation

Exactly one fresh formal dataset may be constructed at:

ml/data/d0_post006_formal.jsonl

The resulting file must be structurally validated and SHA-256 sealed
before any model-scoring authorization is considered.

## Explicitly not authorized

This authorization does NOT authorize:

- training
- retraining
- checkpoint modification
- development evaluation
- formal model evaluation
- baseline scoring
- candidate scoring
- model loading
- model forward passes
- creation of FORMAL_EXPOSURE_STARTED
- modification of either frozen POST-006 policy
- opening the historical formal dataset

## Failure semantics

If construction or validation fails:

- preserve failure evidence
- do not score any model
- do not create FORMAL_EXPOSURE_STARTED
- do not silently modify frozen policies
- do not silently substitute historical examples
- stop for adjudication

## Next stage after successful construction

Successful construction alone does not authorize formal evaluation.

The newly constructed dataset must first be frozen and its provenance,
schema, family counts, ordering, and identity verified.

A separate formal evaluator design/rehearsal/authorization sequence
is required before any checkpoint is scored.
