# D0-EVAL-002 v2 Retirement

Status: INVALID BEFORE SCORING

EVAL-002 v2 corrected the tokenizer incompatibility found
in EVAL-002 v1.

However, a mandatory context-length audit subsequently found
that all 20 instruction examples exceeded the accepted D0
context length of 32 tokens.

Results:

- instruction examples audited: 20
- examples fitting context: 0
- examples exceeding context: 20
- maximum prediction length: 57
- accepted context length: 32

No valid checkpoint evaluation was completed on EVAL-002 v2.

EVAL-002 v2 is therefore retired and must not be used for
acceptance decisions.

EVAL-002 v3 is a separately constructed evaluation candidate.
