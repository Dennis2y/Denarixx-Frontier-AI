# D0-POST-004 Formal Execution Authorization

## Status

FORMAL EXECUTION AUTHORIZED

This authorization was created only after verification of:

- the frozen POST-004 development decision,
- the selected step-120 checkpoint,
- the accepted POST-003 baseline,
- the protected formal dataset,
- the frozen POST-004 design specification,
- the POST-004 formal evaluator,
- the synthetic formal policy tests,
- and absence of prior POST-004 formal exposure.

## Candidate

Only:

local-checkpoints/d0-post004-capability-seed42-step120.pt

is authorized as the POST-004 candidate.

Candidate SHA-256:

ae927ca3e779a0eda7c8fff025fc7cfd3a41568cb236148f444c75507ef35441

## Baseline

Accepted POST-003 baseline:

local-checkpoints/d0-post003-capability-seed42.pt

Baseline SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

## Formal dataset

Protected formal dataset:

ml/data/d0_post003_formal.jsonl

Dataset SHA-256:

28d95ae79d92fe767cf1fb16b984ccb3c33e79616d7cf20666bd6763ec2b7115

## Formal acceptance policy

PASS requires all frozen conditions:

1. Candidate exact-match count is strictly greater than baseline.
2. Candidate achieves at least one formal exact match.
3. Every capability family remains within the 5% loss-regression tolerance.
4. Aggregate response loss remains within the 2% retention tolerance.

## Exposure rule

This document authorizes exactly one controlled POST-004
formal evaluation of the fixed step-120 candidate against
the accepted POST-003 baseline.

No alternate POST-004 candidate may be substituted.

No retraining or candidate modification may occur after
formal exposure based on the protected formal result.

This authorization document itself performs no model scoring.
