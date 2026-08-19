# D0.5 POST-003 Runtime Compatibility Evidence

## Decision

**COMPATIBLE**

The frozen accepted D0-POST-003 inference artifact successfully
executed exactly one bounded deterministic greedy inference using:

- Python: 3.10.0
- PyTorch: 2.2.2
- Platform: macOS arm64
- Checkpoint: `local-checkpoints/d0-post003-capability-seed42.pt`

## Frozen checkpoint identity

SHA-256:

`3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06`

The checkpoint identity was verified immediately before and immediately
after inference and remained unchanged.

## Acceptance identity

`local-evidence/d0-post003-acceptance/ACCEPTANCE.json`

SHA-256:

`90c500fa86448cc59e756712b62c3a485af7861b674a1302781589b27695c3b3`

The acceptance artifact remained unchanged.

## Authorized compatibility inference

Prompt:

`hello`

Maximum generated tokens:

`8`

Decoding:

`greedy`

Result status:

`complete`

Process exit code:

`0`

Generated token IDs:

`[0, 35, 20, 0, 35, 20, 0, 35]`

Generated text:

Escaped representation:

`\\nte\\nte\\nt`

This represents the generated continuation as three newline-separated fragments: `te`, `te`, and `t`, with an initial newline.

Reported runtime characteristics:

- prompt tokens: 5
- generated tokens: 8
- context length: 32
- parameter count: 102784
- latency: approximately 49.284 ms
- generation latency: approximately 24.518 ms
- measured throughput: approximately 326.286 tokens/second
- temperature argument ignored as required by deterministic greedy decoding

## Scope of decision

This decision establishes **runtime compatibility only**.

It does not claim that the generated output demonstrates sufficient
language quality, exact-match capability, or production readiness.

Generation quality remains governed by the existing D0 capability and
evaluation milestones.

## Safety / mutation result

During the compatibility operation:

- exactly one inference invocation occurred
- training was not executed
- evaluation was not executed
- no Python packages were installed
- no Python environment was created
- source was not modified by the inference operation
- the checkpoint was not modified
- `ACCEPTANCE.json` was not modified
- POST-005 was not promoted
- protected formal datasets were not intentionally opened

## Serving consequence

The existing API inference route already supports the `PYTHON_BIN`
environment variable.

Therefore the compatible Python 3.10 runtime can be selected without
modifying the frozen inference route and without creating `.pythonlibs`.

No additional inference is authorized by this evidence record.
