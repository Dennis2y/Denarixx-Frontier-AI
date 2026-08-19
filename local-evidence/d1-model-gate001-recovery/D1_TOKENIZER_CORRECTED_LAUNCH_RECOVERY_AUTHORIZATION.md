# D1 Tokenizer Corrected Launch Recovery Authorization

Authorization ID: `D1-TOK-REPLACEMENT-RECOVERY-AUTH-001`

Status: `authorized-not-executed`

## Purpose

Authorize exactly one corrected replacement-tokenizer construction launch
after D1-MODEL-041 created the authorized destination but failed before
tokenizer construction because the Python stdin script marker (`-`) was
omitted.

## Forensic basis

D1-MODEL-042 established that the replacement destination exists but has
zero descendants and zero regular files.

Tokenizer construction, training and serialization were not reached.

## Authorized recovery

Exactly one corrected construction launch may use the existing empty
destination:

`/Volumes/DenarixxSSD/Denarixx-Frontier-AI/D1/tokenizers/d1-bpe-8192-contract-replacement-v1`

The Python invocation must explicitly use stdin program source:

`python - <arguments...>`

## Token semantics

The replacement remains bound to:

- `<|pad|>` = ID 0
- `<|bos|>` = ID 1
- `<|eos|>` = ID 2
- `<|unk|>` = ID 3

No additional special token is authorized.

`<DENARIXX_DOCUMENT_BOUNDARY>` remains ordinary corpus text and MUST NOT
be assigned tokenizer special-token status.

## Prohibitions

This authorization does not permit deletion/recreation/renaming of the
replacement destination, mutation of D1-TOK-001, mutation of the original
replacement authorization, mutation of the rejected tokenizer, mutation
of D0, D1 model training, checkpoint creation, or formal evaluation
dataset access.

Successful tokenizer construction does not automatically accept
D1-GATE-001. A separate acceptance/sealing gate is required.
