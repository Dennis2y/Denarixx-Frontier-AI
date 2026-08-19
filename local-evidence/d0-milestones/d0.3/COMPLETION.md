# Denarixx Frontier AI — D0.3 Completion Record

## Milestone

D0.3 — Custom Tokenizer

## Status

COMPLETE

## Objective

Train and independently validate a Denarixx-controlled custom tokenizer.

## Tokenizer

- Name: denarixx-d0-bpe
- Type: BPE
- Requested vocabulary size: 64
- Actual vocabulary size: 64
- Pretrained vocabulary used: No
- Special tokens:
  - `<pad>`
  - `<unk>`
  - `<bos>`
  - `<eos>`

## Authorized Corpus

Path:

`ml/data/d0_research_corpus.txt`

SHA-256:

`936b53855c5fa65cc408fb0b29108966445215a474ccfcce7ae7fe9f41fcc072`

Corpus size:

- Characters: 66,416
- UTF-8 bytes: 66,416
- Lines: 867
- Words: 8,957

Formal evaluation data was not used.

## Measured Result

Character-tokenizer baseline:

- Tokens: 66,416

Denarixx D0 BPE tokenizer:

- Tokens: 52,236

Reduction:

- Tokens removed: 14,180
- Reduction fraction: 0.21350277041676705
- Reduction percentage: approximately 21.35%

## Validation

The controlled tokenizer training completed successfully.

Independent post-training validation confirmed:

- Required artifacts exist and are nonempty.
- 25/25 structural and manifest checks passed.
- Vocabulary contains exactly 64 entries.
- Required special tokens are present.
- Authorized corpus path and SHA-256 match.
- Manifest artifact hashes match independently calculated hashes.
- Saved tokenizer reloads successfully.
- Reloaded vocabulary size is 64.
- Reloaded tokenizer encodes the corpus to 52,236 tokens.
- Exact encode/decode round trip succeeds.
- Targeted D0.3 tokenizer tests pass: 5/5.

## Compatibility Boundary

The D0.3 tokenizer is intentionally not integrated into the existing
D0 model.

Existing D0 checkpoints retain their original character-tokenizer
vocabulary and are not compatible with the new D0.3 BPE vocabulary.

No existing checkpoint was modified.

## Execution Boundary

During D0.3 completion:

- D0 model training: NOT EXECUTED
- D0.2 rerun: NOT EXECUTED
- Formal evaluation: NOT PERFORMED
- Formal dataset: NOT OPENED
- POST-007: NOT RERUN
- D0.4: NOT STARTED

## Acceptance Decision

D0.3 acceptance criterion is satisfied.

The custom tokenizer was trained from the authorized local
Denarixx-controlled corpus and independently validated for artifact
integrity, deterministic functionality, serialization/reload behavior,
round-trip correctness, vocabulary size, and token-count reduction.

D0.3 is therefore recorded as COMPLETE.
