# D0-ARCH-002 — Rotary Positional Embeddings

## Research Question

Does replacing D0's learned absolute positional embeddings with
Rotary Positional Embeddings (RoPE) improve held-out validation
performance while keeping the rest of the architecture and training
configuration fixed?

## Historical Baseline

The D0 Baseline V2 used:

- LayerNorm
- learned absolute positional embeddings
- context length 32
- hidden size 64
- 2 transformer layers
- 4 attention heads
- GELU feed-forward activation
- batch size 8
- learning rate 0.0003
- 100 training steps

The historical baseline reports predate the explicit
`normalization` and `position_encoding` configuration fields.

At that commit, LayerNorm and learned absolute positional embeddings
were hard-coded by the model implementation.

## Experimental Control

Only the positional representation changed.

Baseline:

- learned absolute positional embeddings

Variant:

- Rotary Positional Embeddings (RoPE)

Fixed:

- corpus
- corpus hash
- tokenizer
- normalization
- hidden size
- transformer layers
- attention heads
- feed-forward architecture
- activation
- optimizer
- learning rate
- batch size
- context length
- training steps
- evaluation procedure
- paired seeds

Corpus SHA-256:

936b53855c5fa65cc408fb0b29108966445215a474ccfcce7ae7fe9f41fcc072

Seeds:

- 42
- 1337
- 2026

## Implementation

The baseline model adds learned absolute positional embeddings to
token embeddings before the transformer stack.

The RoPE variant:

- does not create the learned absolute position embedding table
- applies rotary transformations to attention queries
- applies rotary transformations to attention keys
- does not rotate attention values
- preserves causal masking
- preserves attention tensor shapes
- introduces no trainable positional parameters

## Results

| Seed | Absolute Loss | RoPE Loss | Delta | Winner |
|---:|---:|---:|---:|---|
| 42 | 2.920356050133705 | 2.9277550280094147 | +0.007398977875709534 | Absolute |
| 1337 | 2.988580495119095 | 2.9213857203722 | -0.06719477474689484 | RoPE |
| 2026 | 2.9556596279144287 | 2.9254560321569443 | -0.030203595757484436 | RoPE |

Mean absolute validation loss:

2.9548653910557428

Mean RoPE validation loss:

2.924865593512853

Mean validation loss delta:

-0.029999797542889617

Relative validation loss change:

-1.0152678234919865%

Mean absolute perplexity:

19.206585949000864

Mean RoPE perplexity:

18.631786250564232

RoPE wins:

2 / 3 paired seeds

## Parameter Impact

Learned absolute positional baseline:

104,832 parameters

RoPE:

102,784 parameters

Reduction:

2,048 trainable parameters

Relative reduction:

1.9536019536019535%

The reduction corresponds exactly to the removed learned positional
embedding table:

32 context positions × 64 hidden dimensions = 2,048 parameters.

## Decision Rule

RoPE is retained only if:

1. mean held-out validation loss is lower than the learned absolute
   positional baseline, AND
2. RoPE wins at least 2 of 3 paired seeds.

## Decision

**ACCEPT_ROPE**

RoPE satisfies both predefined conditions:

- lower mean held-out validation loss
- wins 2 of 3 paired seeds

RoPE therefore becomes the positional encoding baseline for the next
D0 architecture experiment.

Learned absolute positional embeddings remain implemented and
selectable for reproducibility and future comparisons.

## Limitation

This result does not establish that RoPE is universally superior to
learned absolute positional embeddings.

It establishes only that RoPE performed better under the current
small D0 configuration, corpus, evaluation procedure, and paired-seed
experiment.

D0 remains a tiny research model and these results are not frontier
model benchmarks.
