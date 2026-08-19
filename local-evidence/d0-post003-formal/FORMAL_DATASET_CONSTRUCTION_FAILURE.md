# D0-POST-003 Formal Dataset Construction Failure

## Classification

PRE-SCORING DATASET-CONSTRUCTION FAILURE

## Candidate dataset

Path:

`ml/data/d0_post003_formal.jsonl`

SHA-256:

`47917c3418e20ca58dea908f5d05f923c9fe97324ee22e34fdba3dac80a08886`

## Failure

The proposed formal dataset collided with already-used
POST-003 training instructions.

The validation gate rejected the dataset before any
baseline or candidate model was scored.

Therefore this dataset is invalid for formal evaluation.

## Scientific consequence

No formal evaluation exposure occurred.

The fixed POST-003 candidate remains eligible for a
newly constructed untouched formal dataset because:

- no formal model score was observed;
- no formal response loss was observed;
- no formal generation was observed;
- no formal exact-match result was observed;
- the candidate was not retrained;
- the candidate was not modified;
- the formal acceptance rule was not changed.

The failed proposed dataset is preserved as evidence
and must never later be presented as the accepted
formal dataset.

## Required correction

Construct a replacement formal dataset under the
already-frozen formal evaluation policy.

The replacement must pass all overlap, tokenizer,
context, structure and balance gates BEFORE being
declared frozen.
