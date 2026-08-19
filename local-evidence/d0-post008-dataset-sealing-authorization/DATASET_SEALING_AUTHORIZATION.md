# DENARIXX D0-POST-008
## Dataset Sealing Authorization

Stage: D0-POST-008

Status: DATASET-SEALING-AUTHORIZED

This authorization permits exactly one subsequent creation of:

ml/data/d0_post008_formal.jsonl

from the frozen source:

local-evidence/d0-post008-reconstructed-proposed-formal-dataset/d0_post008_reconstructed_proposed_formal.jsonl

Frozen source SHA-256:

78ff74ea7103c52cee382cd87879a30bc1f9b65c16a800249c322303fa63d95b

Authorization scope:

- exactly one dataset-sealing operation
- source and destination must be byte-identical
- source modification is prohibited
- destination must not already exist
- destination SHA-256 must equal the frozen source SHA-256
- authorization is consumed only by the later sealing operation

This authorization does NOT authorize:

- checkpoint loading
- model instantiation
- inference
- scoring
- training
- candidate selection
- formal exposure
- formal evaluation
- formal execution

The sealed formal dataset is NOT created by this authorization step.
