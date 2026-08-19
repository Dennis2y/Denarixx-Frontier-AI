# D1 Tokenizer Replacement Authorization

Authorization ID: D1-TOK-REPLACEMENT-AUTH-001

Status: AUTHORIZED — NOT EXECUTED

This artifact authorizes one future construction attempt for a replacement
D1 tokenizer under the unchanged locked D1-TOK-001 authority.

It does not modify or supersede D1-TOK-001.

## Required special-token mapping

- 0 = `<|pad|>`
- 1 = `<|bos|>`
- 2 = `<|eos|>`
- 3 = `<|unk|>`

This numeric mapping is a prospective remediation binding. It is not a
claim that D1-TOK-001 historically contained numeric IDs.

## Document boundary

`<DENARIXX_DOCUMENT_BOUNDARY>` is ordinary corpus text and is not
authorized as a tokenizer special token.

## Historical artifact

The existing tokenizer at:

`/Volumes/DenarixxSSD/Denarixx-Frontier-AI/D1/tokenizers/d1-bpe-8192`

must remain byte-identical and must never be overwritten by the replacement.

## Replacement destination

`/Volumes/DenarixxSSD/Denarixx-Frontier-AI/D1/tokenizers/d1-bpe-8192-contract-replacement-v1`

The destination must be absent before the authorized construction attempt.

## Training boundary

This authorization permits tokenizer replacement construction only.

It does NOT authorize:

- D1 model training
- D1 checkpoint creation
- formal evaluation dataset access
- mutation of D1-TOK-001
- mutation of D0
- mutation of the rejected tokenizer

A separate acceptance gate is required after replacement construction.
