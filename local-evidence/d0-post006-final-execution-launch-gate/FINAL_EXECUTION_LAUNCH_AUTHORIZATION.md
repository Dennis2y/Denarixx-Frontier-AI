# D0-POST-006 Final One-Time Execution-Launch Authorization

Status: AUTHORIZED

This governance gate authorizes exactly one later formal-comparison
launch using the exact frozen launcher, revised harness, evaluator,
sealed POST-006 dataset, accepted POST-003 baseline, and retained
POST-005 candidate identities recorded in the machine authorization.

This gate itself performs no formal evaluation.

It does not:

- parse the sealed POST-006 formal rows;
- open the historical POST-003 formal dataset;
- load either real checkpoint;
- score either model;
- create FORMAL_EXPOSURE_STARTED;
- train or retrain any model.

The later formal execution remains one-time only.

Once FORMAL_EXPOSURE_STARTED exists, rerun is forbidden.

The baseline must be scored and persisted before candidate scoring.
The candidate must be persisted before comparison.
The final comparison must consume persisted results.

No protected artifact may be modified between this gate and execution.
