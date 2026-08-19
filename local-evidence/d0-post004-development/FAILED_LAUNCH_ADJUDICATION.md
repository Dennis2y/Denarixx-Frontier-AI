# D0-POST-004 Development Failed-Launch Adjudication

The first attempted POST-004 development-selector
invocation terminated during Python module import with:

ModuleNotFoundError: No module named 'models'

The failure occurred before evaluator execution could
proceed into model or dataset scoring.

Observed result state:

- process exit status = 1
- development result file = empty
- no development metric payload was produced
- no candidate-selection decision was produced

The original DEVELOPMENT_EXPOSURE_STARTED marker is
preserved and must not be deleted or rewritten.

This failure is treated as an evaluator invocation /
Python module-path infrastructure defect.

Any recovery must:

- preserve all three candidate checkpoints,
- preserve the frozen development dataset,
- preserve the selector implementation,
- preserve the selection policy,
- preserve the failed-launch evidence,
- make no training changes,
- and make no formal-evaluation changes.

A corrected invocation may be authorized only after
confirming the required modules import successfully
without changing the frozen selector.

Formal evaluation remains unauthorized.
