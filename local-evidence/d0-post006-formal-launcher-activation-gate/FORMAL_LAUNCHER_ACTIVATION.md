# D0-POST-006 Formal Launcher Activation Authorization

Status: AUTHORIZED

This governance gate authorizes activation of exactly one frozen
D0-POST-006 formal launcher identity:

- Launcher:
  `ml/evaluation/d0_post006_formal_launcher.py`
- SHA-256:
  `cc8a276f5bced9e4de8c69f5a12cd5d31e7ea9a44342253271b551ed7cde5a17`

The launcher is bound to the already authorized revised harness:

- Harness SHA-256:
  `2fc3fe2a6b2d2247fd37aa2c47633f1e7fa68703473ca90b507c7c8b94cdf9e5`

This gate does NOT execute formal evaluation.

This gate does NOT:

- train or retrain a model;
- load either real checkpoint;
- score either real checkpoint;
- parse the sealed POST-006 formal JSONL rows;
- access the historical POST-003 formal dataset;
- create FORMAL_EXPOSURE_STARTED;
- modify the launcher, harness, evaluator, dataset, or checkpoints.

Before the one-time formal execution, this activation authorization
must receive a separate read-only binding/integrity audit.

Authorized execution count: 1
