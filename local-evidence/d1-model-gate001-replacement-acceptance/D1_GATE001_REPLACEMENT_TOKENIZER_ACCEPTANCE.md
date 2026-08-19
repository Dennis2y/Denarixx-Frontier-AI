# D1-GATE-001 Replacement Tokenizer Acceptance

Status: **ACCEPTED**

The contract-conforming replacement tokenizer has independently passed
D1-GATE-001 acceptance.

Accepted tokenizer:

`/Volumes/DenarixxSSD/Denarixx-Frontier-AI/D1/tokenizers/d1-bpe-8192-contract-replacement-v1`

Acceptance establishes:

- vocabulary size exactly 8192;
- `<|pad|>` ID 0;
- `<|bos|>` ID 1;
- `<|eos|>` ID 2;
- `<|unk|>` ID 3;
- exactly four tokenizer special tokens;
- `<DENARIXX_DOCUMENT_BOUNDARY>` is not special;
- UTF-8 round-trip behavior verified;
- deterministic encoding verified;
- representative inputs avoid unknown fallback;
- tokenizer, vocabulary, held-out evidence and manifest are hash-bound;
- merge-rule identity is hash-bound;
- D0 remains preserved;
- rejected historical tokenizer remains preserved.

The original rejected tokenizer remains historical evidence and is not
accepted as production authority.

This acceptance does **not** authorize D1 model training or checkpoint
creation. Those actions require a separate determination of the
remaining D1 pre-training gates.
