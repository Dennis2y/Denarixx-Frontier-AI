# D0-POST-003 Formal Dataset Freeze

## Status

FROZEN BEFORE MODEL SCORING

## Dataset

Path:

`ml/data/d0_post003_formal.jsonl`

SHA-256:

`28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115`

Examples:

25

Families:

- echo: 5
- binary: 5
- transform: 5
- qa: 5
- semantic: 5

## Construction history

An earlier proposed formal dataset failed the
pre-scoring overlap gate.

That failed dataset was never used to score any model
and is preserved as:

`local-evidence/d0-post003-formal/FAILED_FORMAL_DATASET.jsonl`

The replacement dataset was constructed only after the
complete exclusion registry was created.

Exclusion registry SHA-256:

`1b2ca084d12c3b3bdf0e554c31a7f816ec639d36d63ac006bf725752e25f519c`

The replacement passed:

- exact instruction exclusion,
- normalized instruction exclusion,
- instruction/response pair exclusion,
- direct source-file overlap checks,
- family-balance validation,
- tokenizer coverage validation,
- context-length validation.

## Scientific boundary

At the time this dataset was frozen:

- the POST-003 candidate had not been formally scored,
- the baseline had not been formally scored on this data,
- no formal result existed,
- no retraining occurred,
- no hyperparameter was changed,
- EVAL-001 was not used,
- EVAL-002 V4 was not used.

The next stage may implement and synthetic-test the
formal evaluator.

The formal dataset must not be scored yet.
