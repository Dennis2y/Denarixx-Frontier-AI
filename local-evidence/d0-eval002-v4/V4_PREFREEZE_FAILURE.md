# D0-EVAL-002 V4 Pre-Freeze Failure

Status: FAILED BEFORE FREEZE AND BEFORE MODEL SCORING

Instruction candidate SHA-256:
e90060bee0376967d0cad987354265700d1b0c4c63b0ffdd98ce3744a38dc707

LM candidate SHA-256:
add74fe6a0402708d0263e804f9c2f063411b16e6a12906cc64c5620950c0b3b

The first V4 candidate failed the predeclared
22-token instruction prediction ceiling.

Failing examples:

1: 23 tokens
6: 23 tokens
16: 24 tokens
17: 23 tokens
18: 23 tokens
19: 25 tokens

No checkpoint was evaluated against this candidate.

This candidate was never frozen and must not be
treated as formal evaluation data.
