# D0-EVAL-001 Research Decision

## Decision

**ACCEPT WITH LIMITATIONS**

## Scope

D0-EVAL-001 compares the accepted D0 pretrained checkpoint
against the accepted POST-001 SFT checkpoint using identical
frozen evaluation datasets.

No training was performed during formal evaluation.

## Language-model evaluation

Pretrained:

- average loss: 2.9376953414723843
- perplexity: 18.872301942469658

SFT:

- average loss: 3.1659788397294055
- perplexity: 23.711942868748995

SFT versus pretrained:

- LM average loss worsened by 7.7708363775599905%
- LM perplexity worsened by 25.64414739141257%

The SFT checkpoint therefore shows a measurable held-out
language-model regression on D0-EVAL-001.

## Instruction evaluation

Pretrained:

- response loss: 3.2275429145962584
- response perplexity: 25.217618942386874
- exact match: 0 / 6

SFT:

- response loss: 3.014594321157418
- response perplexity: 20.380821195278916
- exact match: 0 / 6

SFT versus pretrained:

- instruction response loss improved by 6.597854748136742%
- instruction response perplexity improved by 19.18023171877682%
- exact-match rate did not improve

POST-001 therefore shifted the model toward the intended
instruction-response distribution, but did not demonstrate
successful greedy exact-match instruction execution.

## Reproducibility

The two formal pretrained evaluations are byte-identical.

The two formal SFT evaluations are byte-identical.

The comparison is deterministic under the canonical
D0-EVAL-001 procedure.

## Limitations

The evaluation contains only:

- 395 language-model prediction tokens
- 6 instruction examples
- 51 instruction-response prediction tokens
- one pretrained checkpoint
- one SFT checkpoint
- one current experimental seed lineage

These results do not establish broad instruction-following
ability, production readiness, frontier capability, or
statistical superiority.

## Decision rationale

D0-EVAL-001 is accepted because:

1. the evaluation pipeline is reproducible;
2. frozen evaluation data is separated from optimization data;
3. measurable instruction-response improvement was detected;
4. measurable LM regression was also detected;
5. the evaluation successfully exposes the tradeoff created by
   POST-001.

The decision carries limitations because the SFT checkpoint is
not generally superior to the pretrained checkpoint under the
measured criteria.

## Final decision

**D0-EVAL-001: ACCEPT WITH LIMITATIONS**

## Prior experimental status

- ARCH-002 remains accepted.
- POST-001 remains accepted as the completed SFT experiment.
- INF-001 remains accepted.
- EVAL-001 qualifies the interpretation of POST-001.

The next post-training experiment should investigate whether
instruction-response improvement can be retained while reducing
or eliminating the observed language-model regression.

No training was performed as part of this decision.
