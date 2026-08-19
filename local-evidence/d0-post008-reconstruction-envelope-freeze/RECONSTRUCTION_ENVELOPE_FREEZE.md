# D0-POST-008 Reconstruction Envelope Freeze

## Status

Frozen before controlled reconstruction.

No formal row has been reconstructed by this stage.

No model inference or scoring is authorized by this artifact.

## Reason for reconstruction

The original 40 proposed POST-008 rows were tested against
the accepted baseline and retained candidate tokenizer/config
metadata.

The real checkpoint interface has:

- character tokenizer alphabet size: 42
- context length: 32

The original proposal has:

- 40 / 40 rows containing unsupported characters
- 40 / 40 rows exceeding the real context
- 0 / 40 fully compatible rows

Therefore the original proposed dataset MUST NOT be sealed.

## Frozen formatting rule

The existing formatter remains unchanged.

The formatter performs:

prompt = instruction plus newline

response text = expected response plus newline

combined = prompt plus response text

input ids = combined without the final character

Therefore:

encoded input length =
len(instruction) + len(response) + 1

The frozen checkpoint context length is:

32

Therefore every reconstructed row MUST satisfy:

len(instruction) + len(response) <= 31

This is the exact raw-string compatibility envelope.

## Frozen tokenizer rule

Every character appearing in the instruction and expected
response MUST belong to the accepted checkpoint tokenizer
alphabet.

The formatter-added newline MUST remain supported.

No tokenizer expansion is permitted.

No normalization or silent character substitution is permitted
during compatibility validation.

## Frozen dataset structure

The reconstructed proposal MUST contain exactly:

- 40 rows
- 5 families
- 8 rows per family

Families:

- echo
- boolean
- plural
- opposite
- world_fact

Each row MUST contain exactly three fields:

- family
- instruction
- response

No additional fields are permitted.

## Frozen semantic requirements

Reconstruction MUST preserve the intended capability represented
by each family.

echo:

Request exact reproduction of a short supported string.
The expected response is that exact string.

boolean:

Contain a simple unambiguous proposition.
The expected response is a short truth-value answer.
The proposition must not depend on checkpoint behavior.

plural:

Request the plural of a simple English noun.
The expected response is the correct plural.

opposite:

Request a conventional opposite of a simple English word.
The expected response is the conventional opposite.

world_fact:

Ask a stable elementary world-fact question.
The expected response must be short and unambiguous.
No current, changing, political, subjective, or disputed fact
is permitted.

## Frozen isolation requirements

Reconstruction MUST NOT use:

- baseline model outputs
- candidate model outputs
- model logits
- model losses
- exact-match results
- previous formal evaluation outcomes
- historical formal dataset contents

Reconstruction may use only:

- this frozen envelope
- already-frozen family definitions
- stable human-authored knowledge
- frozen tokenizer alphabet
- frozen context length
- frozen formatter semantics

## Frozen compatibility requirement

Before any reconstructed proposal can be sealed:

1. Exactly 40 rows must exist.
2. Allocation must be exactly 8 rows per family.
3. Every row must use only supported tokenizer characters.
4. Every row must satisfy the 31-character raw-pair limit.
5. The frozen POST-008 compatibility validator must pass.
6. Validation must not rewrite any row.
7. Dataset identity must be frozen after successful validation.

## Prohibited actions

This freeze does NOT authorize:

- sealing the dataset
- formal exposure
- baseline inference
- candidate inference
- model scoring
- adjudication
- training
- candidate selection
- tokenizer modification
- context-length modification
- formatter modification
- compatibility-validator modification
