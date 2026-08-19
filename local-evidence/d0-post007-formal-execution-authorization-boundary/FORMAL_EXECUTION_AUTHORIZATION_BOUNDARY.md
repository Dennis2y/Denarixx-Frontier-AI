# D0-POST-007 Formal Execution Authorization Boundary

Status: PREPARED — NOT AUTHORIZED

This evidence establishes the frozen boundary immediately before any
future one-time D0-POST-007 formal execution authorization.

It does NOT authorize:

- formal dataset parsing;
- checkpoint loading;
- baseline inference;
- candidate inference;
- model scoring;
- formal comparison;
- creation of FORMAL_EXPOSURE_STARTED;
- activation of real formal execution.

Frozen execution harness:

ml/evaluation/d0_post007_execution_harness.py
SHA-256: edabc74e41e3785f8a0b49c2ddace683ac0b4be3fa9b1e1a81b04f10d9fb27ad

Frozen dependency adapter:

ml/evaluation/d0_post007_dependencies.py
SHA-256: 5bdd066deb42e55976d3e3bc64eba5453f019ff554db87ea6031d17a35bb4629

Sealed formal dataset:

ml/data/d0_post007_formal.jsonl
SHA-256: f0f5c88524c4f0b78f4ebbd23548006103aa3e4116cc4a3df34493712b07fb0c

Accepted baseline:

local-checkpoints/d0-post003-capability-seed42.pt
SHA-256: 3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

Retained candidate:

local-checkpoints/d0-post005-development-seed42-step120.pt
SHA-256: 4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

Synthetic harness rehearsal state:

local-evidence/d0-post007-execution-harness-rehearsal/SYNTHETIC_HARNESS_REHEARSAL_STATE.json
SHA-256: d3d9f3fcebbe5406f940cbe8516af508834a3d63190bf899e00b2f9a844c7a6d

Formal adjudication policy:

local-evidence/d0-post007-formal-adjudication-policy/FORMAL_ADJUDICATION_POLICY.md
SHA-256: 3512500d87932411590b7c9014a10a4185e130b515b7e549baa9e6ef723535c4

Current execution state:

REAL_FORMAL_EXECUTION_ENABLED=False

POST-007 formal exposure:

ZERO

A future authorization must be a separate create-once artifact and
must bind exactly these frozen identities.

No existing frozen POST-007 artifact may be edited to create that
authorization.
