# D0-ARCH-001 — RMSNorm Experiment

## Hypothesis

Replacing LayerNorm with RMSNorm may improve held-out validation
performance while reducing normalization parameters.

## Experimental Control

Only normalization changes.

Fixed:

- corpus
- tokenizer
- model dimensions
- optimizer
- learning-rate schedule
- batch size
- max steps
- evaluation procedure
- seeds

Seeds:

- 42
- 1337
- 2026

## Results

| Seed | LayerNorm Loss | RMSNorm Loss | Delta | Winner |
|---:|---:|---:|---:|---|
| 42 | 2.920356050133705 | 2.9258273988962173 | +0.005471348762512207 | LayerNorm |
| 1337 | 2.988580495119095 | 2.988915741443634 | +0.00033524632453918457 | LayerNorm |
| 2026 | 2.9556596279144287 | 2.958572432398796 | +0.0029128044843673706 | LayerNorm |

Mean LayerNorm validation loss:

2.9548653910557428

Mean RMSNorm validation loss:

2.9577718575795493

Mean LayerNorm perplexity:

19.206585949000864

Mean RMSNorm perplexity:

19.261408524693937

RMSNorm won:

0 / 3 seeds.

Mean RMSNorm loss delta:

+0.002906466523806254

Relative mean loss change:

+0.09836206185919703%

## Parameter Impact

LayerNorm:

104,832

RMSNorm:

104,512

Reduction:

320 parameters

0.3053%

## Decision

**REJECT_RMSNORM**

The predefined retention rule requires RMSNorm to:

1. achieve lower mean held-out validation loss, AND
2. win at least 2 of 3 paired seeds.

It achieved neither.

LayerNorm therefore remains the D0 baseline.

RMSNorm remains implemented as an explicit experimental option for
future architecture research.

This experiment does NOT establish that LayerNorm is universally
better than RMSNorm. It only establishes that RMSNorm did not improve
the current D0 configuration under this experiment.
