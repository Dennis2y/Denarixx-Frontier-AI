# D0-POST-007 Formal Dataset Construction Policy

## Status

FROZEN BEFORE POST-007 FORMAL DATASET CREATION.

This document defines construction and compatibility requirements
only.

It does not create a formal dataset.

It does not authorize model scoring.

It does not authorize formal exposure.

## Recovery binding

POST-007 exists as a fresh recovery stage after the exposed
D0-POST-006 formal execution failed before adjudication.

The POST-006 formal dataset is permanently ineligible for reuse,
repair, editing, rescoring, or transformation into POST-007 formal
evidence.

The last formally accepted baseline remains the accepted POST-003
checkpoint.

## Frozen capability families

POST-007 uses exactly five capability families:

- echo
- boolean
- plural
- opposite
- world_fact

No additional family may be added after this policy is frozen.

No family may be removed after this policy is frozen.

## Dataset size

The future POST-007 formal dataset must contain exactly 25 rows.

It must contain exactly 5 rows from each frozen family.

The final distribution is therefore:

- echo: 5
- boolean: 5
- plural: 5
- opposite: 5
- world_fact: 5

## Required semantic fields

Every future row must contain exactly these semantic fields:

- instruction
- response
- family

instruction must be a non-empty string.

response must be a non-empty string.

family must be one of the five frozen POST-007 families.

## Freshness requirement

Every POST-007 formal example must be newly constructed.

POST-007 examples must not be copied or programmatically derived
from:

- the exposed POST-006 formal dataset;
- the historical POST-003 formal dataset;
- training examples;
- development examples;
- candidate-selection examples.

The exposed POST-006 formal dataset must not be opened for the
purpose of authoring, filtering, deduplicating, or validating
POST-007 examples.

## No model-feedback construction

Formal examples must be authored without querying, scoring, or
testing either:

- the accepted baseline checkpoint; or
- the retained candidate checkpoint

for capability performance.

Compatibility validation is permitted only for structural
tokenizer/context compatibility as defined below.

Compatibility validation must not inspect model predictions,
losses, logits, exact matches, or candidate behavior.

## Mandatory tokenizer compatibility gate

Before any proposed POST-007 dataset may be sealed, every proposed
row must pass the exact frozen instruction-encoding path used by
formal scoring.

Compatibility must be checked against the tokenizer and context
contract of the accepted baseline.

For every proposed row:

1. instruction must be non-empty;
2. response must be non-empty;
3. family must be valid;
4. format_instruction() must succeed;
5. every formatted prompt character must exist in the accepted
   baseline tokenizer;
6. every formatted response character must exist in the accepted
   baseline tokenizer;
7. encode_instruction() must succeed;
8. the encoded sequence must fit the accepted baseline context
   length;
9. at least one supervised response token must remain.

All 25 rows must pass.

A single compatibility failure invalidates the proposed dataset
before sealing.

## Compatibility validation is not capability evaluation

The compatibility validator may:

- load the accepted baseline checkpoint only to obtain its frozen
  tokenizer/configuration identity if required;
- inspect tokenizer alphabet;
- inspect context length;
- call formatting and encoding utilities;
- report structural compatibility failures.

The compatibility validator must NOT:

- execute model forward inference;
- generate responses;
- compute loss;
- inspect logits;
- compute exact matches;
- compare baseline and candidate capability;
- load the candidate checkpoint;
- use compatibility outcomes for candidate selection.

## No evaluator weakening

Dataset compatibility must be achieved by authoring compatible
examples.

Recovery must not:

- extend or alter the tokenizer;
- replace unsupported characters during scoring;
- strip punctuation during scoring;
- silently normalize incompatible text;
- truncate examples to force them into context;
- change encode_instruction() to accommodate formal rows;
- weaken validation;
- introduce candidate-specific preprocessing.

## Family intent

### echo

Tests literal reproduction of a short tokenizer-compatible target.

The expected response must be objectively determined by the
instruction.

### boolean

Tests a simple binary yes/no capability.

Expected responses must be short, deterministic, and
tokenizer-compatible.

### plural

Tests a simple deterministic singular-to-plural transformation.

Only transformations with one objectively specified expected
response are permitted.

### opposite

Tests a simple deterministic opposite relation.

Only pairs with one unambiguous expected response are permitted.

### world_fact

Tests a short elementary world fact with one objectively
determined expected response.

The answer must not depend on current events, opinion, regional
convention, or changing external information.

## Deterministic grading

Every expected response must be short and objectively gradeable.

The same frozen normalization and exact-match procedure must apply
to baseline and candidate.

No candidate-specific normalization is permitted.

## Internal uniqueness

Within the future POST-007 formal dataset:

- no complete row may repeat;
- no instruction may repeat;
- each example must independently test its declared family.

## Ordering

The final 25 rows must use deterministic interleaving across the
five frozen families.

Five complete cycles must be used, with one row from each family
per cycle.

The ordering rule must be fixed before sealing.

## Pre-seal validator requirement

A dedicated POST-007 compatibility validator must be implemented
and tested before real formal dataset construction is finalized.

The validator must establish at minimum:

1. exactly 25 rows;
2. exactly five frozen families;
3. exactly five rows per family;
4. required semantic fields only;
5. non-empty instruction and response;
6. tokenizer coverage for formatted prompt;
7. tokenizer coverage for formatted response;
8. successful frozen instruction encoding;
9. accepted-baseline context compatibility;
10. at least one supervised response token per row;
11. deterministic family distribution/order checks.

The validator must be tested first on synthetic, non-formal rows.

## Sealing

Only after all 25 proposed rows pass the frozen compatibility
validator may the POST-007 dataset be sealed.

At sealing:

- the exact dataset bytes become immutable;
- SHA-256 must be recorded;
- examples may not be edited;
- expected responses may not change;
- family labels may not change;
- ordering may not change.

Any required change after sealing invalidates that dataset and
requires a fresh dataset identity before exposure.

## Exposure boundary

Construction and compatibility validation occur before formal
exposure.

Formal exposure begins only when a separately authorized execution
loads the sealed POST-007 formal rows for scoring.

Dataset construction does not itself constitute formal exposure.

## Prohibitions

This policy does not authorize:

- training;
- retraining;
- candidate selection;
- checkpoint modification;
- formal model scoring;
- formal comparison;
- formal exposure;
- creation of FORMAL_EXPOSURE_STARTED;
- reuse of POST-006 authorization.

## Required future sequence

After this policy is frozen:

1. build the compatibility validator;
2. test it using synthetic rows only;
3. freeze validator identity;
4. construct fresh POST-007 proposed examples;
5. validate all proposed rows before sealing;
6. seal the compatible dataset;
7. record dataset SHA-256;
8. freeze evaluator/dependency identities;
9. issue a fresh one-time POST-007 execution authorization;
10. perform a separate one-time formal execution.

