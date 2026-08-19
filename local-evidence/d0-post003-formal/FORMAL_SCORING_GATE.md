# D0-POST-003 Final Formal-Scoring Gate

Status:

READY FOR ONE-TIME FORMAL SCORING

No formal candidate scoring had occurred when this gate
record was written.

## Fixed baseline

Path:

`local-checkpoints/d0-post002-accepted.pt`

SHA-256:

`31038f7801ae64f99aad4ec88e7aaa276917be9dec84ef0944b121578a36ca97`

## Fixed candidate

Path:

`local-checkpoints/d0-post003-capability-seed42.pt`

SHA-256:

`3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06`

## Frozen formal dataset

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

## Frozen evaluator

Path:

`ml/evaluation/d0_post003_formal.py`

SHA-256:

`df9a2a98162e384971b9609173b593475391306e761b93cef151d919df3099fc`

## Frozen synthetic tests

Path:

`ml/tests/test_d0_post003_formal.py`

SHA-256:

`a065abae466029584f445b505a64927b7a60fef4e6c1920a1c6f953d8cc6a672`

## Formal acceptance rule

Candidate formally passes only if all are true:

1. POST-003 aggregate response loss is strictly lower
   than POST-002 aggregate response loss.

2. POST-003 exact-match count is greater than or equal
   to POST-002 exact-match count.

3. At least four of five capability families have
   POST-003 response loss less than or equal to POST-002.

4. Candidate SHA-256 remains unchanged.

5. Architecture remains unchanged.

6. Parameter count remains 102784.

## Scientific interpretation

Even a formal PASS establishes only a controlled
probabilistic capability-acquisition milestone for the
tiny D0 model under this specific evaluation.

If exact-match performance remains zero, the result must
not be described as successful deterministic instruction
following.

It does not establish frontier-model capability,
general intelligence, production readiness, or
competitiveness with modern large language models.

## Prohibited after exposure

After formal scoring begins:

- no dataset edits,
- no evaluator edits,
- no retraining,
- no hyperparameter changes,
- no candidate replacement,
- no seed search,
- no checkpoint selection,
- no acceptance-rule changes.

The formal result is accepted as observed, whether PASS
or FAIL.
