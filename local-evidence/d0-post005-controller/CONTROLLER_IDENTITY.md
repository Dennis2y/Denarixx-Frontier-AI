# D0-POST-005 Frozen Training Controller Identity

Status: FROZEN

Controller:
- path: ml/run_post005.py
- sha256: f19e01b43e7887bb7a65e30f2bd717942a39ef002d9081bb0ef9cf7ccf4dea59

Controller tests:
- path: ml/tests/test_d0_post005.py
- sha256: e54317a1b737d442585fcc6ea2615e8900e11c20c293612e93fc72951edafaf8

Frozen training plan:
- path: local-evidence/d0-post005-training-plan/FROZEN_TRAINING_PLAN.md
- sha256: 1629a882791cd4b12ea5d93322371b23e1c4ce1487b3589198d76cb969a10a42

Accepted starting checkpoint:
- path: local-checkpoints/d0-post003-capability-seed42.pt
- sha256: 3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

Training dataset:
- path: ml/data/d0_post004_train.jsonl
- sha256: 93f60bf014810bc5a5592d1ad7f3c5bf7bef80011dea252ddb0455f006b9963f

Development dataset:
- path: ml/data/d0_post004_dev.jsonl
- sha256: d54abaa83a4bbdcca313c557431fa5005e4490b7103f0f997ccd0c619f5c8a58

Retention LM corpus:
- path: ml/data/d0_research_corpus.txt
- sha256: 936b53855c5fa65cc408fb0b29108966445215a474ccfcce7ae7fe9f41fcc072

Protected formal dataset:
- path: ml/data/d0_post003_formal.jsonl
- sha256: 28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115
- use during training: PROHIBITED
- use during development selection: PROHIBITED

POST-004 step-120 checkpoint:
- status: DEVELOPMENT REFERENCE ONLY
- POST-005 parent: NO
- inherited formal acceptance: NONE

Training authorization:
- status: NOT YET GRANTED

This identity record freezes the POST-005 controller and
its static test suite before any POST-005 optimization.
