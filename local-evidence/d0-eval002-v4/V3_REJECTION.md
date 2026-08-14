# D0-EVAL-002 v3 Candidate Rejection

Status: REJECTED BEFORE MODEL SCORING

EVAL-002 v3 successfully satisfied:

- tokenizer compatibility
- accepted architectural context limit of 32 tokens

However, the v3 construction procedure predeclared a stricter
design ceiling of 26 prediction tokens per instruction example.

The context audit found prediction lengths:

27, 26, 23, 25, 23, 28, 26, 26, 27, 30,
32, 25, 29, 30, 30, 29, 25, 26, 27, 29

Therefore v3 failed its own predeclared construction criterion.

No model checkpoint was evaluated on v3.

No model-selection information was obtained from v3.

V3 must not be used for POST-002 acceptance.
