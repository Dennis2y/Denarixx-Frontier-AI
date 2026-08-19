# D0-POST-006 Stage Initialization

## Stage status

D0-POST-006 is initialized for GOVERNANCE DESIGN ONLY.

Training:
LOCKED

Development evaluation:
LOCKED

Formal evaluation:
LOCKED

Model scoring:
NOT AUTHORIZED

Formal dataset construction:
NOT AUTHORIZED BY THIS INITIALIZATION

## Last formally accepted baseline

Checkpoint:

local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

This remains the last formally accepted baseline.

No later development-selected checkpoint may inherit formal
acceptance automatically.

## POST-005 retained research candidate

Checkpoint:

local-checkpoints/d0-post005-development-seed42-step120.pt

SHA-256:

4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

POST-005 disposition:

DEVELOPMENT-SELECTED / FORMALLY UNADJUDICATED

This checkpoint may be considered as a starting candidate or parent
only under a separately frozen POST-006 design decision.

This initialization does NOT authorize training from it.

This initialization does NOT promote it to the accepted baseline.

## Historical protected formal dataset

Path:

ml/data/d0_post003_formal.jsonl

SHA-256:

28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115

Historical state:

EXPOSED DURING POST-004

POST-005 rescoring:

ZERO

This historical dataset MUST NOT be treated as a fresh unseen
POST-006 formal dataset.

It MUST NOT be used for:

- POST-006 training
- POST-006 development selection
- POST-006 hyperparameter tuning
- POST-006 formal acceptance scoring

Its identity may be verified without reading its contents.

## POST-006 formal-policy requirement

Before any POST-006 formal dataset is created, inspected by a model,
or used for scoring, POST-006 must freeze an explicit formal
acceptance contract.

The contract must determine, before formal results exist:

1. accepted baseline checkpoint identity
2. candidate checkpoint eligibility
3. capability families
4. formal dataset construction policy
5. formal dataset size and family distribution
6. exact-match metric definition
7. aggregate response-loss metric definition
8. per-family response-loss metric definition
9. exact-match pass threshold
10. aggregate-loss pass threshold
11. per-family retention threshold
12. zero-baseline handling
13. conjunction/disjunction semantics
14. deterministic comparison behavior
15. scoring-result schema
16. baseline/candidate persistence ordering
17. failure evidence behavior
18. one-time exposure semantics
19. rerun prevention
20. promotion semantics

No acceptance threshold may be chosen or modified after observing
results from the POST-006 formal dataset.

## Separation requirement

POST-006 must maintain strict separation between:

- training data
- development data
- formal acceptance data

Formal acceptance data MUST NOT participate in:

- training
- candidate selection
- hyperparameter selection
- prompt/template tuning
- evaluator threshold tuning

## Required engineering order

The permitted governance sequence is:

1. initialize POST-006
2. design and freeze formal acceptance semantics
3. design formal dataset construction policy
4. design training/development trajectory
5. synthetically test controllers/evaluators
6. authorize training separately
7. execute exactly the authorized training trajectory
8. freeze training
9. authorize development evaluation separately
10. select candidate using development data only
11. freeze selected candidate
12. construct/seal fresh formal dataset under frozen policy
13. verify formal evaluator without formal-data exposure
14. create separate formal execution authorization
15. perform one-time formal comparison

Steps may remain locked until their prerequisites are satisfied.

## Current authorization

AUTHORIZED:

POST-006 governance design.

NOT AUTHORIZED:

- training
- model scoring
- development evaluation
- formal evaluation
- formal dataset exposure
- formal dataset scoring
- checkpoint promotion

## Next authorized operation

Freeze the D0-POST-006 formal acceptance semantics before creating
or scoring any new formal dataset.
