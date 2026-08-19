# D0-POST-008 Compatibility Validator Freeze

## Status

PASS — compatibility validator frozen after synthetic testing.

## Frozen validator

- Path: `ml/evaluation/d0_post008_compatibility.py`
- SHA256: `63408b13e1cc832b74d68c7feffae6035194d68adc43978bb6061fd23b19cac7`

## Frozen synthetic test suite

- Path: `ml/tests/test_d0_post008_compatibility.py`
- SHA256: `c55dd2033621dbcd0dc2638133f583a3ff8757804f4003ea42fb2de3058c4bb8`
- Tests collected: 13
- Tests passed: 13
- Tests failed: 0

## Bound formal dataset specification

- Path: `local-evidence/d0-post008-formal-dataset-specification/FORMAL_DATASET_SPECIFICATION.md`
- SHA256: `33747eda7c3da0a1d74ac351cc14d60aad8e76df374fe4617416ba5451a75161`

## Verified properties

- Exact 40-row structure is enforced.
- Exact family allocation is enforced.
- Unknown families are rejected.
- Extra fields are rejected.
- Blank required values are rejected.
- Duplicate instructions are rejected.
- Tokenizer coverage is validated.
- Context compatibility is validated.
- Unsupported characters are rejected.
- Validation does not modify supplied rows.
- No formal dataset path is embedded.
- No checkpoint path is embedded.
- No checkpoint loading operation is performed.
- Synthetic test fixture conforms to the tokenizer interface.

## Execution boundary

This freeze did not:

- construct POST-008 formal rows;
- open a POST-008 formal dataset;
- open historical formal datasets;
- load a real checkpoint;
- execute model inference;
- execute model scoring;
- execute training;
- start formal exposure;
- enable formal execution;
- authorize formal execution.

Created: `2026-08-15T17:48:09.067120+00:00`
