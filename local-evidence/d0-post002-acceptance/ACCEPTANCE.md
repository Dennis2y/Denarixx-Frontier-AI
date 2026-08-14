# D0-POST-002 Formal Acceptance

## Decision

ACCEPTED

Candidate:

`d0-post002-mixed-l025-seed42`

Retention weight:

`lambda = 0.25`

## Objective

D0-POST-002 tested mixed response-only supervised
fine-tuning plus next-token language-model retention:

`L = L_sft + lambda * L_lm`

The purpose was to improve instruction adaptation while
reducing language-model retention regression relative to
D0-POST-001.

## EVAL-001

POST-002 versus POST-001:

- instruction loss improvement: 1.0099496320988508%
- language-model loss improvement: 2.414214333524967%

POST-002 versus ARCH-002 pretrained:

- language-model degradation: 5.169017398373198%

Result:

PASS

## EVAL-002 V4

POST-002 versus POST-001:

- instruction loss improvement: 0.710553%
- language-model loss improvement: 2.063525%

POST-002 versus ARCH-002 pretrained:

- language-model degradation: 2.897396%

Result:

PASS

## Acceptance-policy result

The candidate:

- improved instruction response loss versus POST-001
  on EVAL-001 and EVAL-002 V4,
- improved language-model loss versus POST-001
  on EVAL-001 and EVAL-002 V4,
- remained below the predeclared 7% language-model
  degradation ceiling versus ARCH-002 pretrained,
- preserved architecture,
- preserved tokenizer identity,
- preserved parameter count,
- passed regression gates,
- and was evaluated against frozen secondary data.

Therefore D0-POST-002 lambda=0.25 satisfies the
predeclared acceptance criteria.

## Scope

This acceptance establishes a D0 research milestone.

It does not claim frontier-model capability,
production readiness, broad language competence,
or meaningful absolute instruction-following ability.

Exact-match generation remains zero on the current
evaluation suites.

## Experimental discipline

EVAL-002 V4 must remain immutable.

No further lambda value should be selected using
EVAL-001 or EVAL-002 V4 as a tuning target.

Future post-training experiments require a new
predeclared experimental stage and appropriate
evaluation discipline.
