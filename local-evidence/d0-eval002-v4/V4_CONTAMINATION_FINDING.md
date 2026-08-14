# D0-EVAL-002 V4 Pre-Freeze Contamination Finding

Status: DETECTED BEFORE FREEZE AND BEFORE MODEL SCORING

Candidate instruction SHA-256:
332a8bbd76c687e70aa4f240abaa1e684d14d340263ef74f3042276aee6442e5

Candidate LM SHA-256:
add74fe6a0402708d0263e804f9c2f063411b16e6a12906cc64c5620950c0b3b

The forensic audit identified exact instruction-field
overlap with D0 SFT data:

V4 example 4:
  instruction: say test
  matched SFT example 9 instruction.

V4 example 5:
  instruction: say train
  matched SFT example 8 instruction.

The complete instruction-response pairs did not overlap,
but the exact instruction reuse was conservatively treated
as evaluation contamination.

No checkpoint was evaluated on this candidate.

Only examples 4 and 5 were subsequently replaced before
formal freezing.
