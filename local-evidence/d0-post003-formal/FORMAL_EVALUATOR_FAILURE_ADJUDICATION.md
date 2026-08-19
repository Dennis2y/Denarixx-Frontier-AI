# D0-POST-003 Formal Evaluator Failure Adjudication

## Event

The one-time formal exposure was initiated.

The evaluator terminated with:

`RuntimeError: Parameter count changed: 107520`

## Important boundary

The formal exposure marker must remain preserved.

The formal dataset must now be treated as exposed.

No second formal scoring attempt is authorized at this
stage.

## Result status

No valid `FORMAL_RESULT.json` was produced.

Therefore:

- no aggregate formal response loss was recorded,
- no formal response perplexity was recorded,
- no formal exact-match count was recorded,
- no per-family formal comparison was recorded,
- no formal PASS/FAIL decision was produced.

## Classification pending

The discrepancy between the previously frozen parameter
count of 102784 and the evaluator-observed count of
107520 must be investigated before deciding whether the
failure represents:

1. a formal-evaluator implementation defect,
2. an inconsistent historical parameter-count method,
3. a model-construction/configuration mismatch,
4. or a genuine architecture invariant violation.

The expected parameter count must NOT simply be changed
to 107520 to force evaluation to proceed.

## Prohibited actions

Until adjudication is complete:

- do not rerun formal scoring,
- do not modify the formal dataset,
- do not retrain POST-003,
- do not replace the candidate,
- do not change hyperparameters,
- do not use EVAL-001 or EVAL-002 V4 for selection,
- do not declare POST-003 accepted,
- do not commit the experiment as accepted.
