# D0-POST-007 One-Time Formal Execution Authorization

Status: AUTHORIZED — NOT EXECUTED

This artifact authorizes exactly one POST-007 formal comparison
execution using only the frozen identities bound by the accompanying
authorization JSON.

Creating this authorization does NOT:

- parse the sealed formal dataset;
- load either real checkpoint;
- execute model scoring;
- execute the formal comparison;
- create FORMAL_EXPOSURE_STARTED;
- arm the activation module automatically.

Training, retraining, development use, candidate selection,
threshold tuning, historical-formal-data reuse, and formal expected
response disclosure remain prohibited.

The activation package remains separately gated.

Formal exposure begins only if a later verified execution step creates
the exposure marker immediately before the first formal-row load.
