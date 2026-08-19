# DENARIXX D0.5 — Serving Authority Contract

## Status

FROZEN BEFORE INFERENCE ROUTE MODIFICATION

## Purpose

D0.5 serves the currently formally accepted D0 checkpoint through the
Denarixx inference API.

Serving authority is distinct from training-run history.

The `training_runs` table records API training execution history and must
not be treated as the authoritative registry of scientifically accepted
checkpoints.

## Current Serving Authority

Checkpoint:

`local-checkpoints/d0-post003-capability-seed42.pt`

SHA-256:

`3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06`

Acceptance authority:

`local-evidence/d0-post003-acceptance/ACCEPTANCE.json`

Acceptance state:

- status: ACCEPTED
- decision: FORMAL_PASS

## POST-005 Boundary

The retained POST-005 development checkpoint is:

`local-checkpoints/d0-post005-development-seed42-step120.pt`

It is not the current serving authority because its formal acceptance
status remains unadjudicated.

D0.5 must not silently promote POST-005.

## Training-Run Boundary

D0.5 must not:

- insert a synthetic or fake completed training run;
- rewrite historical training-run records;
- infer serving authority from the newest completed training run;
- claim that POST-003 was produced by the API training subsystem.

Training provenance and serving authority are separate concerns.

## Required Serving Resolution

The inference API must eventually resolve the checkpoint from an explicit
serving-authority mechanism.

That mechanism must fail closed.

Before model loading, it must establish at minimum:

1. the authorized checkpoint path;
2. the expected SHA-256;
3. that the checkpoint exists;
4. that the actual SHA-256 equals the expected SHA-256.

A missing, malformed, unauthorized, or hash-mismatched serving authority
must prevent inference.

## Current D0.5 Modification Boundary

This contract does not authorize:

- model inference;
- model evaluation;
- training;
- checkpoint modification;
- database mutation;
- POST-005 promotion;
- protected formal dataset access;
- protected formal dataset parsing;
- protected formal dataset hashing.

Modification of `inference.ts` requires a separate bounded implementation
step after this contract is verified.

## Protected Historical Material

The following protected formal datasets must not be opened as part of
D0.5 serving integration:

- `ml/data/d0_post003_formal.jsonl`
- `ml/data/d0_post006_formal.jsonl`

D0.5 serving requires checkpoint identity and acceptance metadata only.

## Next Operation

Verify this frozen contract and inspect the minimal implementation surface
needed for a fail-closed serving-authority resolver without running model
inference.
