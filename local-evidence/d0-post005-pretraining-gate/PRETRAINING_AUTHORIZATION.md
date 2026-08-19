# D0-POST-005 Pretraining Authorization Gate

Decision: AUTHORIZED FOR ONE FROZEN DEVELOPMENT TRAINING TRAJECTORY

Authorization scope:

- Accepted parent:
  local-checkpoints/d0-post003-capability-seed42.pt
  3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

- Frozen controller:
  ml/run_post005.py
  f19e01b43e7887bb7a65e30f2bd717942a39ef002d9081bb0ef9cf7ccf4dea59

- Frozen controller tests:
  ml/tests/test_d0_post005.py
  e54317a1b737d442585fcc6ea2615e8900e11c20c293612e93fc72951edafaf8

- Frozen training plan:
  local-evidence/d0-post005-training-plan/FROZEN_TRAINING_PLAN.md
  1629a882791cd4b12ea5d93322371b23e1c4ce1487b3589198d76cb969a10a42

- Training dataset:
  ml/data/d0_post004_train.jsonl
  93f60bf014810bc5a5592d1ad7f3c5bf7bef80011dea252ddb0455f006b9963f

- Development dataset:
  ml/data/d0_post004_dev.jsonl
  d54abaa83a4bbdcca313c557431fa5005e4490b7103f0f997ccd0c619f5c8a58

- Retention LM corpus:
  ml/data/d0_research_corpus.txt
  936b53855c5fa65cc408fb0b29108966445215a474ccfcce7ae7fe9f41fcc072

Optimization contract:

- max steps: 120
- candidate snapshots: 40, 80, 120
- SFT batch size: 4
- LM batch size: 4
- learning rate: 0.0001
- weight decay: 0.01
- gradient clip norm: 1.0
- retention weight: 0.25
- seed: 42
- SFT generator seed: 42
- LM generator seed: 43
- optimizer: fresh AdamW
- inherited optimizer state: prohibited
- internal dataset resplitting: prohibited

Protected formal dataset:

- identity:
  28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115
- training access: PROHIBITED
- development selection access: PROHIBITED
- formal scoring during training: PROHIBITED

POST-004 step-120:

- may serve as development reference only
- may not be loaded as POST-005 parent
- carries no inherited formal acceptance

Authorization:

POST-005 is authorized only for the single frozen
development training trajectory encoded by the controller
and training plan identified above.

This authorization does NOT authorize:

- development evaluation after training
- candidate selection after training
- formal evaluation
- modification of the frozen controller
- modification of frozen datasets
- modification of the accepted parent
- substitution of POST-004 as the parent

Any identity mismatch invalidates this authorization.
