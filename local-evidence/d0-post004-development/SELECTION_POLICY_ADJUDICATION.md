# D0-POST-004 Development Selection Policy Adjudication

Status: FROZEN BEFORE DEVELOPMENT MODEL SCORING

The POST-004 design specification contains both:

- primaryMetric = exactMatchCount
- secondaryMetric = aggregateResponseLoss
- tertiaryMetric = familyCoverage

and the more explicit tieBreak rule:

"Prefer more families with exact matches, then lower
aggregate response loss, then earlier training step."

These statements create an ordering ambiguity after the
primary exact-match metric.

Because the tieBreak statement explicitly specifies the
candidate ordering to apply after exact-match comparison,
the frozen operational interpretation is:

1. Candidate must achieve at least one exact match.
2. Higher exactMatchCount is preferred.
3. If exactMatchCount ties, higher familyCoverage is
   preferred.
4. If exactMatchCount and familyCoverage tie, lower
   aggregateResponseLoss is preferred.
5. If all above tie, earlier candidateStep is preferred.

This adjudication does not alter:

- training,
- checkpoints,
- development data,
- formal data,
- model architecture,
- optimizer state,
- decoding,
- metric definitions,
- or candidate set.

It only resolves contradictory ordering language before
any POST-004 development model result has been observed.

Exactly the predeclared step-40, step-80 and step-120
candidates are eligible.

The development dataset may be exposed only after this
adjudication is frozen.

Development selection may select at most one candidate
for subsequent formal evaluation.

Development selection does NOT authorize formal
evaluation.

The protected POST-003 formal dataset remains sealed.
