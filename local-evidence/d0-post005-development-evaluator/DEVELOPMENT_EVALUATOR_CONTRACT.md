# D0-POST-005 Development Evaluator Contract

Status: FROZEN

## Authorized scope

This evaluator may score only the three predeclared
D0-POST-005 development candidates:

- step 40
- step 80
- step 120

against exactly:

- ml/data/d0_post004_dev.jsonl
- SHA-256: d54abaa83a4bbdcca313c557431fa5005e4490b7103f0f997ccd0c619f5c8a58

Formal evaluation is NOT authorized.

Training is CLOSED and MUST NOT be resumed.

## Frozen candidate identities

step 40:
1ea05d991a28381adc65c5af06fb1caf95ee52484d714c1ec4101275ee439796

step 80:
92a8f742c9f7a37170d908f39db0dd01f26b4d9bc370218bc435df16ef029b7f

step 120:
4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

## Frozen scoring

For each development example:

1. Compute supervised response-token cross-entropy loss.
2. Generate greedily.
3. Compare generated response with expected response by exact string equality.
4. Record exact-match family coverage.

## Frozen candidate eligibility

A candidate is eligible only if:

exactMatchCount > 0

## Frozen selection order

Among eligible candidates:

1. Higher exactMatchCount wins.
2. Higher familyCoverage wins.
3. Lower aggregateResponseLoss wins.
4. Earlier candidateStep wins.

Development selection does NOT constitute formal acceptance.

## Frozen evaluator identity

ml/evaluation/d0_post005_dev.py
SHA-256: 76376df4bc74575f151192a866267e3632cb35a6cdcd712f17f7b8a7b48bb10a

ml/tests/test_d0_post005_dev.py
SHA-256: 3ab93b00e17a49b605f83affca0df02c6ae21b806f241dcd173340343bdbf74a

## Governance

Development evaluation:
AUTHORIZED

Formal evaluation:
LOCKED

Retraining:
FORBIDDEN
