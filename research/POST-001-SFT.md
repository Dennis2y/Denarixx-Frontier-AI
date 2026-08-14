# D0-POST-001 — Supervised Fine-Tuning

## Research Question

Can the accepted Denarixx D0 pretrained model be supervised
fine-tuned on instruction-response examples and improve held-out
response prediction without changing the tokenizer, architecture,
or parameter count?

## Accepted Pretraining Baseline

D0-POST-001 begins from the accepted D0-ARCH-002 checkpoint:

`local-checkpoints/d0-arch002-rope-seed42.pt`

The accepted architecture uses:

- LayerNorm
- Rotary Positional Embeddings (RoPE)
- context length 32
- hidden size 64
- 2 transformer layers
- 4 attention heads
- 102,784 trainable parameters

The tokenizer is the character tokenizer embedded in the accepted
pretrained checkpoint.

POST-001 does not retrain or replace that tokenizer.

## Purpose

POST-001 is a pipeline-validation experiment.

Its purpose is to establish that Denarixx owns and controls the
transition:

Pretraining
→ pretrained checkpoint
→ supervised fine-tuning
→ held-out instruction evaluation
→ post-trained checkpoint

It is not intended to establish frontier instruction-following
capability.

## Instruction Dataset

The POST-001 dataset contains 12 tiny instruction-response examples.

A deterministic ordered-tail holdout is used:

- total examples: 12
- training examples: 9
- held-out validation examples: 3
- validation fraction: 25%

Training instructions:

- say yes
- say no
- say ai
- say data
- say safe
- say model
- say code
- say train
- say test

Held-out validation instructions:

- say true
- say false
- say token

The held-out examples are never sampled during SFT optimization.

## Supervision

POST-001 uses response-only supervision.

Prompt-token targets are masked from the loss.

Padding targets are also masked.

Only response tokens contribute to the SFT cross-entropy objective.

## Experimental Control

All controlled runs use:

- the same accepted pretrained checkpoint
- the same tokenizer
- the same model architecture
- the same parameter count
- the same instruction dataset
- the same deterministic 9/3 split
- 20 SFT optimization steps
- batch size 4
- learning rate 0.0001

SFT seeds:

- 42
- 1337
- 2026

The three runs begin from the same pretrained seed-42 checkpoint.

Therefore, the seed comparison measures SFT optimization variation,
not independent pretraining variation.

## Decision Rule

SFT is accepted for the D0 pipeline only if:

1. mean held-out response loss after SFT is lower than before SFT;
2. SFT improves held-out response loss in at least 2 of 3 runs;
3. the pretrained tokenizer remains identical;
4. the architecture/configuration remains identical;
5. the parameter count remains 102,784;
6. losses and gradients remain finite.

## Results

| SFT Seed | Initial Held-Out Loss | Final Held-Out Loss | Delta | Winner |
|---:|---:|---:|---:|---|
| 42 | 3.557425625 | 3.065526738 | -0.491898887 | SFT |
| 1337 | 3.557425625 | 3.066936914 | -0.490488712 | SFT |
| 2026 | 3.557425625 | 3.077597632 | -0.479827993 | SFT |

Mean initial held-out response loss:

3.557425625184003

Mean final held-out response loss:

3.0700204278908525

Mean loss delta:

-0.48740519729315074

Relative mean loss change:

-13.70106500168757%

SFT wins:

3 / 3 runs

Initial held-out perplexity:

35.07279031638806

Final held-out perplexities:

- seed 42: 21.445755304431007
- seed 1337: 21.476018922474733
- seed 2026: 21.706193446987665

All controlled losses and gradients remained finite.

## Invariants

Across all controlled SFT runs:

- tokenizer remained identical;
- model configuration remained identical;
- LayerNorm remained selected;
- RoPE remained selected;
- context length remained 32;
- parameter count remained 102,784;
- held-out examples remained excluded from optimization.

The accepted ARCH-002 pretrained checkpoint was not overwritten.

## Decision

**ACCEPT_SFT**

D0-POST-001 satisfies every predefined retention condition.

Supervised fine-tuning is therefore accepted as a validated stage in
the Denarixx D0 model-building pipeline.

This decision accepts the SFT mechanism and lifecycle.

It does not claim that this tiny SFT checkpoint is a production model
or that D0 has general instruction-following capability.

## Limitations

The dataset contains only 12 tiny examples.

The validation set contains only three instructions.

All three SFT runs start from the same pretrained seed-42 checkpoint.

The experiment therefore does not measure variation across
independently pretrained models.

D0 remains a tiny research model.

The observed improvement is evidence only for this controlled
POST-001 configuration and held-out set.

It is not evidence of frontier-model capability.

## Pipeline Status

With POST-001 accepted, the demonstrated D0 lifecycle now includes:

Dataset
→ tokenizer
→ model architecture
→ pretraining
→ checkpoint
→ supervised fine-tuning
→ held-out evaluation

Remaining D0 lifecycle work includes stronger evaluation,
post-training expansion, inference validation, model serving, and
Denarixx API integration before the D0 pipeline can be considered
complete.
