# D0-POST-004 Development Selection Decision

## Status

DEVELOPMENT SELECTION PASS

This decision freezes the result of the authorized
POST-004 development recovery execution.

Development evaluation must not be rerun.

POST-004 must not be retrained based on this result.

Formal evaluation is NOT authorized by this document.

## Selected candidate

Candidate step:

120

Checkpoint:

local-checkpoints/d0-post004-capability-seed42-step120.pt

SHA-256:

ae927ca3e779a0eda7c8fff025fc7cfd3a41568cb236148f444c75507ef35441

## Development result

Step 40:
- exact matches: 0 / 15
- aggregate response loss: 2.8331576688790028

Step 80:
- exact matches: 0 / 15
- aggregate response loss: 2.68759533211037

Step 120:
- exact matches: 3 / 15
- exact-match rate: 0.20
- aggregate response loss: 2.5687373008257075

The frozen minimum condition required non-zero exact
generation.

Step 120 satisfies that condition.

Step 120 also strictly exceeds steps 40 and 80 on the
primary exact-match metric.

Therefore step 120 is fixed as the sole candidate
eligible for subsequent POST-004 formal evaluation.

## Evaluator observation — family labels

The development evaluator reported all 15 examples with:

family = "unknown"

Therefore the reported familyCoverage value of 1 must
NOT be interpreted as evidence of coverage across the
intended capability families.

This observation does not alter candidate selection
because step 120 uniquely wins the primary metric:

3 exact matches versus 0 for both other candidates.

The exposed development result must not be rescored
after changing family classification.

## Evaluator observation — policy metadata

The result payload contains a metadata inconsistency.

The implemented ranking reports:

1. higher exactMatchCount
2. higher familyCoverage
3. lower aggregateResponseLoss
4. earlier candidateStep

while the metric labels in the same payload describe
aggregateResponseLoss as secondary and familyCoverage
as tertiary.

The pre-exposure adjudication froze the implemented
ranking.

This inconsistency does not affect the observed
selection because step 120 uniquely wins the primary
exact-match metric.

No post-exposure selector modification or development
rerun is permitted.

## Formal state

The protected POST-003 formal dataset remains unchanged.

No POST-004 formal evaluation has been authorized or
executed by this decision.

The next operation must be a separate formal-evaluation
readiness audit and freeze.

Only the fixed step-120 candidate may become eligible
for the single POST-004 formal evaluation.
