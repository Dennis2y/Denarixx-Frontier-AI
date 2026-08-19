# D0-EVAL-002 v1 Retirement Record

Status: INVALID BEFORE SCORING

D0-EVAL-002 v1 was frozen as a candidate secondary evaluation
dataset but was discovered to be incompatible with the accepted
D0 tokenizer before any checkpoint produced evaluation metrics.

Frozen v1 identities:

LM:
352b349b675456bc24953be8dbc02f3d5d8f798c706bf12c20c01b8997c3a723

Instructions:
56e2038aa976c82b5f06ae55446a8cf8eae86dfb481329d415fd6b7a4e5064d0

Observed unsupported characters:

LM:
G H L M P V

Instructions:
? K M O P

All 20 instruction examples contained at least one unsupported
character because the question mark is absent from the accepted
42-character tokenizer.

The first attempted formal evaluation stopped during tokenizer
coverage validation before the pretrained checkpoint produced
metrics.

The resulting zero-byte pretrained.raw.json is not evaluation
evidence and must never be interpreted as a model result.

No POST-002 performance information was obtained from v1.

EVAL-002 v1 is permanently retired and must not be repaired in
place, scored, or used for checkpoint selection.
