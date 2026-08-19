# D0-POST-003 Aborted Manual Formal-Evaluator Invocation

After formal evaluator implementation, the evaluator was
manually invoked without any required CLI arguments:

`python3 ml/evaluation/d0_post003_formal.py`

The invocation terminated during argparse CLI validation.

Observed error:

`the following arguments are required:
--baseline, --candidate, --dataset, --output`

Classification:

- CLI-validation abort
- no baseline path supplied
- no candidate path supplied
- no formal dataset path supplied
- no output path supplied
- run_formal_evaluation was not entered
- no checkpoint scoring occurred
- no formal dataset scoring occurred
- no formal result was produced
- no formal exposure occurred

This invocation does not count as formal candidate scoring.

The event is preserved for research/audit transparency.
