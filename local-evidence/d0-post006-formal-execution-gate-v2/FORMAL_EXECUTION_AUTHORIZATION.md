# D0-POST-006 Revised One-Time Formal Execution Authorization

Status: AUTHORIZED

Authorization version: 2

This authorization permits exactly one formal comparison execution
using the exact frozen resources listed below.

## Sealed formal dataset

ml/data/d0_post006_formal.jsonl

SHA-256:

202e63aee4f3a24c0746dc1a6a6136a6b33cf7ebfb3395f3e068d016985d189f

## Accepted baseline

local-checkpoints/d0-post003-capability-seed42.pt

SHA-256:

3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06

## Candidate

local-checkpoints/d0-post005-development-seed42-step120.pt

SHA-256:

4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9

## Formal evaluator

ml/evaluation/d0_post006_formal.py

SHA-256:

37f54a6ec2725d8df34c0331780c723f841a1d471364091406159b3915121e89

## Revised execution harness

ml/evaluation/d0_post006_execution_harness.py

SHA-256:

2fc3fe2a6b2d2247fd37aa2c47633f1e7fa68703473ca90b507c7c8b94cdf9e5

The authorization is bound specifically to this revised harness
identity.

The prior one-time authorization bound to the old harness must not
be used for this revised implementation.

Exactly one formal execution is authorized.

Before the first sealed formal row is loaded, the formal exposure
marker must be created.

The accepted baseline must be scored first and persisted before
candidate scoring.

The candidate result must be persisted before comparison.

Comparison must consume persisted results.

Reruns after formal exposure begins are forbidden.

Evidence overwrite is forbidden.

Failure evidence must preserve any evidence already persisted.

The historical POST-003 formal dataset must not be opened or scored.

The POST-006 formal dataset must not be used for training,
development, candidate selection, or threshold tuning.

This authorization gate itself performs no model loading, no model
scoring, no formal-row parsing, and no formal exposure.

The next operation is an authorization-integrity audit before any
separately controlled launcher is permitted to execute the formal
lifecycle.
