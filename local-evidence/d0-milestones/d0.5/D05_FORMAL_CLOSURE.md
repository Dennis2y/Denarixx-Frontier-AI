# DENARIXX D0.5 — Formal Closure

## Decision

**FORMAL PASS — D0.5 COMPLETE**

D0.5 successfully served the formally promoted D0 checkpoint through
the authenticated Denarixx inference API.

## Serving Checkpoint

`local-checkpoints/d0-post005-development-seed42-step120.pt`

SHA-256:

`4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9`

## Serving Authority

`local-evidence/d0-milestones/d0.5/SERVING_AUTHORITY.json`

Serving status remains:

`ACTIVE`

This is intentional. `ACTIVE` represents the checkpoint currently
authorized for inference serving. It is not the D0.5 milestone lifecycle
state.

## Milestone State

D0.5 milestone:

`COMPLETE`

The research control-plane milestone was transitioned from `active`
to `complete`.

## Live Closure Evidence

An authenticated operator session was observed through Clerk.

Observed authentication state:

- authenticated: true
- authStateAvailable: true

A measured inference result was successfully returned through the
Denarixx D0 Playground.

Observed runtime measurements:

- latency: 86.2 ms
- throughput: 775.9 tokens/second

No additional inference was executed during this formal closure
operation.

## Scientific Boundary

This closure does not claim that D0 has production-quality language
generation.

D0.5 establishes authenticated serving of the formally accepted D0
artifact through the Denarixx inference API.

## Mutation Boundary

During formal closure:

- no training was executed;
- no additional inference was executed;
- model weights were not modified;
- the POST-005 checkpoint was not modified;
- serving authority was not modified;
- promotion authority was not modified;
- the inference route was not modified;
- the serving resolver was not modified;
- D1 was not started.

The only governed source transition was the D0.5 milestone presentation
from `active` to `complete`.

## Machine-Readable Closure

`local-evidence/d0-milestones/d0.5/D05_FORMAL_CLOSURE.json`

SHA-256:

`6cc5c8901b5155134a5b87b82aeccdb5bbeecc22dd1c388704caef0a3ca13ad1`

## Result

**D0.5 COMPLETE**
