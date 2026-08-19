# D0-POST-008 Dependency Adapter Freeze

## Status

PASS — dependency adapter frozen after synthetic interface testing.

## Frozen adapter

- Path: `ml/evaluation/d0_post008_dependencies.py`
- SHA256: `50fd911f8e29286999d65af6e390be049e5729c31f808b298d3809373b21d128`

## Frozen synthetic test suite

- Path: `ml/tests/test_d0_post008_dependencies.py`
- SHA256: `6736d2c404420cd024d8a0013e2d7742f22d485e6bb17e0946dac28dfd66790c`
- Tests collected: 9
- Tests passed: 9
- Tests failed: 0

## Verified properties

- POST-008 dependency interface is implemented.
- `score_checkpoint(checkpoint_path, rows)` consumes rows supplied in memory.
- Dataset selection remains outside the dependency adapter.
- Checkpoint selection remains outside the dependency adapter.
- Formal exposure evidence remains outside the dependency adapter.
- Aggregate scoring behavior is covered by synthetic mocks.
- Comparison consumes aggregate scoring results.
- Family mismatch is rejected.
- Wrong-stage scoring results are rejected.
- Final POST-008 adjudication policy is NOT frozen here.
- `formalPass` remains unresolved.
- No real formal execution is authorized by this freeze.

## Execution boundary

This freeze did not:

- construct or open the POST-008 formal dataset;
- open historical formal datasets;
- load a real checkpoint;
- execute real model inference;
- execute real model scoring;
- execute training or retraining;
- create formal exposure evidence;
- enable real POST-008 execution;
- authorize real POST-008 execution.

Created: `2026-08-15T17:38:05.791973+00:00`
