# DENARIXX D0.5 — API Runtime Selection

## Status

FROZEN BEFORE CONTROLLED API STARTUP

## Selected Runtime

Python executable:

`/Library/Frameworks/Python.framework/Versions/3.10/bin/python3`

Validated runtime:

- Python 3.10.0
- PyTorch 2.2.2
- macOS arm64

## Basis

Exactly one bounded POST-003 compatibility inference completed
successfully under this runtime.

Compatibility evidence:

`local-evidence/d0-milestones/d0.5/POST003_RUNTIME_COMPATIBILITY.md`

SHA-256:

`ac49572b8805a829b9ab476e9b103ee0d7e17ca097952af0ba9a7b6fd7f5e8b2`

## Runtime Selection Mechanism

The API route already resolves its Python command using:

`process.env.PYTHON_BIN`

Therefore D0.5 will select the validated runtime using a process-scoped
environment variable.

The intended controlled launch form is:

`PYTHON_BIN=/Library/Frameworks/Python.framework/Versions/3.10/bin/python3 PORT=3000 pnpm --filter @workspace/api-server run start`

This command is recorded here as the intended launch mechanism only.

Creation of this document does not execute that command.

## Why Process-Scoped Selection Was Chosen

Process-scoped `PYTHON_BIN` is preferred because it:

- requires no inference-route modification;
- requires no package installation;
- requires no `.pythonlibs` environment;
- requires no `.env.local` mutation;
- requires no package.json mutation;
- is explicit;
- is immediately reversible when the API process exits;
- preserves the frozen serving-authority implementation.

## Serving Authority Boundary

Runtime selection does not select the checkpoint.

Checkpoint authority remains exclusively controlled by the frozen
serving-authority resolver and accepted POST-003 acceptance metadata.

Authorized serving checkpoint:

`local-checkpoints/d0-post003-capability-seed42.pt`

SHA-256:

`3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06`

POST-005 remains unpromoted.

## Next Operation

Inspect the current API listener state.

If an old API process is running without the selected `PYTHON_BIN`,
perform a separately bounded controlled restart.

If no API process is running, perform a separately bounded controlled
startup.

That next operation may establish API process readiness and health only.

It must not invoke the inference endpoint.

## Prohibited By This Decision

This decision does not authorize:

- model inference;
- additional compatibility inference;
- training;
- evaluation;
- checkpoint modification;
- acceptance-metadata modification;
- POST-005 promotion;
- protected formal dataset access;
- package installation;
- `.pythonlibs` creation;
- inference-route modification.
