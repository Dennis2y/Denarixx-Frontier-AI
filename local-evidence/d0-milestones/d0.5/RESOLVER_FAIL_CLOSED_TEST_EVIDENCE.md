# DENARIXX D0.5 — Serving Authority Resolver Fail-Closed Test Evidence

## Status

PASS — 12 / 12 controlled resolver tests passed.

## Scope

The serving-authority resolver was exercised independently using isolated
temporary fixtures.

No model inference, model evaluation, or training was executed.

The real accepted checkpoint and real acceptance metadata were not modified.

The protected formal datasets were not opened.

## Frozen Inputs

Serving Authority Contract:

`local-evidence/d0-milestones/d0.5/SERVING_AUTHORITY_CONTRACT.md`

SHA-256:

`1ab805a5880d41520be81a38a0102529cd7b409cb2b2a8cc1e65addce7051214`

Resolver:

`artifacts/api-server/src/lib/servingAuthority.ts`

SHA-256:

`13f1628418fc44f76039141147ce9e6161e06392b57f60ab9da71f2b84c33437`

Acceptance metadata:

`local-evidence/d0-post003-acceptance/ACCEPTANCE.json`

SHA-256:

`90c500fa86448cc59e756712b62c3a485af7861b674a1302781589b27695c3b3`

Canonical accepted checkpoint:

`local-checkpoints/d0-post003-capability-seed42.pt`

SHA-256:

`3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06`

## Controlled Test Results

1. PASS — valid accepted authority resolves.
2. PASS — missing acceptance artifact fails closed.
3. PASS — invalid acceptance JSON fails closed.
4. PASS — malformed acceptance metadata fails closed.
5. PASS — non-ACCEPTED status fails closed.
6. PASS — non-FORMAL_PASS decision fails closed.
7. PASS — absolute checkpoint path fails closed.
8. PASS — checkpoint traversal outside local-checkpoints fails closed.
9. PASS — missing checkpoint fails closed.
10. PASS — checkpoint SHA-256 mismatch fails closed.
11. PASS — tampered checkpoint fails closed.
12. PASS — absolute acceptance path fails closed.

## Post-Test Integrity

After resolver testing:

- Serving Authority Contract identity remained unchanged.
- servingAuthority.ts identity remained unchanged.
- ACCEPTANCE.json identity remained unchanged.
- canonical POST-003 checkpoint identity remained unchanged.
- inference.ts remained unintegrated.
- API server TypeScript typecheck passed.

## Scientific Boundary

These tests validate serving-authority resolution behavior only.

They do not constitute:

- model inference;
- model evaluation;
- training;
- checkpoint promotion;
- POST-005 adjudication;
- formal-dataset access;
- formal capability evidence.

## Result

The fail-closed serving-authority resolver is eligible for a separately
reviewed minimal integration into the D0.5 inference route.

No integration is authorized merely by this evidence artifact.
