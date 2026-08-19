# D0-POST-008 Checkpoint Identity Binding Freeze

## Status

Checkpoint identities frozen.

Formal execution is NOT authorized.

## Accepted baseline

Path:

`local-checkpoints/d0-post003-capability-seed42.pt`

SHA-256:

`3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06`

## Retained candidate

Path:

`local-checkpoints/d0-post005-development-seed42-step120.pt`

SHA-256:

`4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9`

## Identity injection architecture

The frozen POST-008 execution harness defines
`HarnessIdentities`.

Concrete dataset, baseline, and candidate SHA-256 identities
are supplied externally through `expected_identities`.

The frozen harness does not require concrete checkpoint SHA-256
constants to be embedded in its source.

## Execution state

- Checkpoint bytes hashed: YES
- Checkpoint deserialized: NO
- Checkpoint metadata inspected: NO
- Model instantiated: NO
- Model inference executed: NO
- Model scoring executed: NO
- Training executed: NO
- Proposed dataset modified: NO
- Sealed formal dataset created/opened: NO
- Formal exposure started: NO
- Formal execution enabled: NO
- Formal execution authorized: NO

## Governance consequence

A future POST-008 real activation/launcher layer may construct
`HarnessIdentities` using these frozen identities.

That future layer must be separately designed, verified, frozen,
and authorized before any formal exposure or model scoring.
