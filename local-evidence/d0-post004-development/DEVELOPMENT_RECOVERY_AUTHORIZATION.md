# D0-POST-004 Development Recovery Authorization

The original development-selector invocation failed
during Python module import before model scoring.

Failure:

ModuleNotFoundError: No module named 'models'

The failure produced:

- no development metric payload,
- no model score,
- no candidate-selection decision.

The original failure evidence and exposure marker remain
preserved.

Root cause:

The repository's ml directory was not present on the
Python module search path.

Recovery correction:

PYTHONPATH=ml

This correction changes only the process import
environment.

It does NOT modify:

- candidate checkpoints,
- model parameters,
- development data,
- protected formal data,
- selector source,
- selection metrics,
- selection ordering,
- training configuration,
- or formal acceptance policy.

The frozen POST-004 selector may therefore receive one
recovery execution using the same three frozen
candidates and the same frozen development dataset.

The protected formal dataset remains sealed.

Formal evaluation remains unauthorized until the
development recovery result is observed and adjudicated.
