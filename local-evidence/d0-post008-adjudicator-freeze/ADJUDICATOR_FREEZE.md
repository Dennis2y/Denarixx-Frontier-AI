# D0-POST-008 Adjudicator Freeze

## Status

PASS — dedicated adjudicator frozen after synthetic policy testing.

## Frozen adjudicator

- Path: `ml/evaluation/d0_post008_adjudicator.py`
- SHA256: `92d2d803be8d481caccf7cbf5a7758738094459d5ba8095ca95662e0cd427c0c`

## Frozen synthetic test suite

- Path: `ml/tests/test_d0_post008_adjudicator.py`
- SHA256: `645058be5145597fa48ad1d51e5d24094eb186e1d8d93024bfbca7fa3a3dec2e`
- Tests collected: 14
- Tests passed: 14
- Tests failed: 0

## Bound frozen artifacts

- Dependency adapter:
  `ml/evaluation/d0_post008_dependencies.py`
  `50fd911f8e29286999d65af6e390be049e5729c31f808b298d3809373b21d128`

- Execution harness:
  `ml/evaluation/d0_post008_execution_harness.py`
  `f5268a25b034b4c69d980ae372ed5c632546b50725723feea73f0eeab572ea59`

- Formal adjudication policy:
  `local-evidence/d0-post008-formal-adjudication-policy/FORMAL_ADJUDICATION_POLICY.md`
  `28e149660f93ded0e782f875f307eb79b1dd7bdccf5ba6d6fb4d29a09b3e8435`

## Verified adjudication semantics

The synthetic test suite verifies:

- all frozen conditions are required for formal PASS;
- candidate exact matches must be at least 1;
- candidate exact matches must strictly exceed baseline;
- candidate aggregate response loss must strictly improve;
- exactly 5% family loss regression is permitted;
- regression greater than 5% fails;
- zero baseline family loss requires zero candidate family loss;
- all five frozen families must satisfy retention;
- one failed family causes formal failure;
- wrong-stage comparison evidence is rejected;
- family-set mismatch is rejected;
- missing required comparison fields are rejected;
- negative family loss is rejected;
- adjudication does not mutate its input.

## Execution boundary

This freeze did not:

- construct or open the POST-008 formal dataset;
- open historical formal datasets;
- load a real checkpoint;
- execute model inference;
- execute model scoring;
- execute training or retraining;
- create formal exposure evidence;
- enable real formal execution;
- authorize real formal execution.

## Governance

The adjudicator is now frozen.

It must not be modified merely to accommodate future formal rows
or observed checkpoint behavior.

Any identity change invalidates this freeze and requires a new
explicit governance stage before formal execution.

Created: `2026-08-15T17:45:23.426753+00:00`
