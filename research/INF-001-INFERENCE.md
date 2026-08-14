# D0-INF-001 — Post-Trained Inference Validation

## Research Question

Can the accepted Denarixx D0 pretrained and supervised
fine-tuned checkpoints be independently reconstructed and used
through one canonical deterministic inference path while preserving
the accepted tokenizer, architecture, context length, and parameter
count?

## Accepted Starting State

D0-INF-001 begins after:

- D0-ARCH-002 accepted LayerNorm + RoPE;
- D0-POST-001 accepted supervised fine-tuning as a pipeline stage.

Accepted D0 configuration:

- character tokenizer vocabulary size: 42
- context length: 32
- hidden size: 64
- transformer layers: 2
- attention heads: 4
- normalization: LayerNorm
- positional encoding: RoPE
- trainable parameters: 102,784

The accepted pretrained checkpoint is:

`local-checkpoints/d0-arch002-rope-seed42.pt`

The controlled SFT checkpoints are:

- `d0-post001-sft-seed42.pt`
- `d0-post001-sft-seed1337.pt`
- `d0-post001-sft-seed2026.pt`

## Purpose

INF-001 validates the post-training inference lifecycle.

It tests whether Denarixx can:

1. load accepted checkpoints independently;
2. reconstruct tokenizer and architecture from checkpoint metadata;
3. validate checkpoint invariants;
4. perform deterministic greedy autoregressive generation;
5. enforce the D0 rolling context window;
6. measure inference latency;
7. measure generated-token throughput;
8. compare pretrained and SFT inference behavior through the same path;
9. regression-test the inference implementation.

This experiment does not evaluate frontier capability.

## Canonical Inference Path

INF-001 introduces a canonical D0 inference implementation used by
the command-line runner and the regression tests.

Generation uses deterministic greedy decoding.

For prompts longer than the configured context length, only the
latest 32 tokens are supplied to the model while the returned output
preserves the complete original prompt.

Unknown tokenizer characters are rejected explicitly.

Empty prompts and invalid generation lengths are rejected.

## Controlled Evidence Design

The controlled comparison used:

- 1 accepted pretrained checkpoint;
- 3 controlled SFT checkpoints;
- 10 prompts;
- 3 held-out POST-001 prompts;
- 7 POST-001 training prompts;
- 8 generated tokens per prompt;
- 3 repeated greedy generations per checkpoint/prompt.

Held-out prompts:

- `say true`
- `say false`
- `say token`

The comparison used the same canonical inference path for pretrained
and SFT checkpoints.

## Determinism

All repeated greedy inference runs were deterministic.

**Result: PASS**

## Numerical Validity

All recorded inference latency and throughput measurements were
finite.

**Result: PASS**

## Checkpoint Invariants

Across pretrained and SFT inference:

- tokenizer remained identical;
- architecture remained identical;
- parameter count remained 102,784;
- context length remained 32;
- LayerNorm remained selected;
- RoPE remained selected.

**Result: PASS**

## Pretrained-vs-SFT Behavior

SFT-generated token sequences differed from the pretrained sequence
in:

**30 / 30 checkpoint-prompt comparisons**

For the held-out POST-001 prompts, SFT-generated token sequences
differed from pretrained generation in:

**9 / 9 comparisons**

The pretrained checkpoint commonly generated:

`Dererere`

The SFT checkpoints commonly generated a repeated sequence resembling:

`e\n`

This establishes that POST-001 weight updates materially changed
greedy autoregressive behavior through the canonical inference path.

It does not establish useful instruction-following capability.

## Exact Response Match

Pretrained exact expected responses:

**0 / 10**

SFT exact expected responses:

**0 / 30**

Exact response match is descriptive only and was not an INF-001
acceptance criterion.

POST-001 previously established improvement through held-out
response loss, not exact-match generation.

Therefore, zero exact generation matches do not invalidate INF-001
inference infrastructure.

They do demonstrate that D0 remains far below useful natural-language
instruction-following capability.

## Performance Measurements

Observed local mean generated-token throughput:

- pretrained: approximately 1,961 tokens/second
- SFT: approximately 2,136 tokens/second

Observed local mean generation latency:

- pretrained: approximately 4.22 ms
- SFT: approximately 3.92 ms

These measurements are descriptive only.

The generations are extremely small and local execution timing is
subject to runtime, hardware, cache, scheduling, and measurement
noise.

No performance superiority claim is made.

## Regression Coverage

INF-001 regression coverage verifies:

- pretrained checkpoint loading;
- SFT checkpoint loading;
- pretrained/SFT invariant equality;
- deterministic greedy generation;
- full-prompt output preservation;
- rolling context-window behavior;
- short-prompt behavior;
- tokenizer coverage rejection;
- empty-prompt rejection;
- invalid generation-length rejection;
- generation metadata;
- evaluation mode;
- SFT/pretrained weight difference.

ARCH-002 and POST-001 focused regression suites also remain passing.

## Acceptance Criteria

INF-001 is accepted if:

1. accepted checkpoints load successfully;
2. tokenizer and architecture reconstruct from checkpoint metadata;
3. tokenizer/configuration invariants remain unchanged;
4. parameter count remains 102,784;
5. greedy inference is deterministic;
6. context-length behavior is enforced;
7. latency and throughput measurements are finite;
8. pretrained and SFT checkpoints can be compared through the same
   canonical inference path;
9. accepted architecture and POST-001 training implementation remain
   unchanged;
10. all focused regression tests pass.

Exact natural-language response match is not an acceptance criterion.

Throughput superiority is not an acceptance criterion.

## Decision

**ACCEPT_INF_001**

D0-INF-001 satisfies the predefined engineering requirements for
post-trained inference validation.

Denarixx D0 now has a tested canonical inference path capable of
loading accepted checkpoints, reconstructing the model/tokenizer,
performing deterministic greedy generation, enforcing context
behavior, measuring local inference characteristics, and comparing
pretrained and post-trained checkpoints.

This decision accepts the inference mechanism and lifecycle.

It does not claim useful general instruction-following capability,
production readiness, or frontier-model capability.

## Limitations

D0 contains only 102,784 parameters.

Its tokenizer contains only 42 characters.

Its context length is only 32 tokens.

POST-001 used only 12 tiny instruction-response examples.

INF-001 used only 10 prompts.

All controlled SFT runs originate from the same accepted pretrained
checkpoint.

Generated text remains qualitatively poor.

Latency and throughput measurements are local engineering
measurements rather than production benchmarks.

The experiment validates infrastructure, determinism, invariants,
and inference lifecycle behavior only.

## Pipeline Status

With INF-001 accepted, the demonstrated D0 lifecycle now includes:

Dataset
→ Tokenizer
→ Architecture
→ Pretraining
→ Checkpoint
→ Supervised Fine-Tuning
→ Held-Out Evaluation
→ Canonical Inference
→ Deterministic Generation
→ Inference Measurement

Remaining D0 work should focus on stronger evaluation and expanding
the model-building lifecycle rather than interpreting tiny D0 outputs
as capability evidence.
