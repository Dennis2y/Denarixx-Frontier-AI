# D0-POST-008 Formal Adjudication Policy Binding

## Status

FORMAL ADJUDICATION POLICY BOUND TO CURRENT FROZEN POST-008 ARTIFACTS.

This evidence does not replace, modify, delete, or recreate the
historical pre-dataset formal adjudication policy.

Historical policy:

- `local-evidence/d0-post008-formal-adjudication-policy/FORMAL_ADJUDICATION_POLICY.md`
- SHA256 `28e149660f93ded0e782f875f307eb79b1dd7bdccf5ba6d6fb4d29a09b3e8435`

Historical policy state:

- `local-evidence/d0-post008-formal-adjudication-policy/FORMAL_ADJUDICATION_POLICY_STATE.json`
- SHA256 `5e5e4a946158318c7caa2d1711e95f529ecc0885abe376f1c00fc01342c84ac9`

## Current bindings

Sealed formal dataset:

- `ml/data/d0_post008_formal.jsonl`
- SHA256 `78ff74ea7103c52cee382cd87879a30bc1f9b65c16a800249c322303fa63d95b`

Accepted baseline:

- `local-checkpoints/d0-post003-capability-seed42.pt`
- SHA256 `3b409092c120242fe4ed75113758390dee3e8e627507afdf7bcbc1bb5b3ccc06`

Retained candidate:

- `local-checkpoints/d0-post005-development-seed42-step120.pt`
- SHA256 `4877d292fdd8e5428db250359dc9c57ebc4f4d1ccb2a329b94bdafd2c61569d9`

Frozen adjudicator:

- `ml/evaluation/d0_post008_adjudicator.py`
- SHA256 `92d2d803be8d481caccf7cbf5a7758738094459d5ba8095ca95662e0cd427c0c`

Frozen dependency adapter:

- `ml/evaluation/d0_post008_dependencies.py`
- SHA256 `50fd911f8e29286999d65af6e390be049e5729c31f808b298d3809373b21d128`

Frozen compatibility validator:

- `ml/evaluation/d0_post008_compatibility.py`
- SHA256 `63408b13e1cc832b74d68c7feffae6035194d68adc43978bb6061fd23b19cac7`

Frozen execution harness:

- `ml/evaluation/d0_post008_execution_harness.py`
- SHA256 `f5268a25b034b4c69d980ae372ed5c632546b50725723feea73f0eeab572ea59`

## Bound decision policy

Formal PASS requires all of the following:

1. candidateExactMatches >= 1
2. candidateExactMatches > baselineExactMatches
3. candidateAggregateResponseLoss <
   baselineAggregateResponseLoss
4. every frozen family satisfies the 5% maximum response-loss
   regression rule
5. a zero-loss baseline family requires candidate family loss == 0

Frozen families:

- echo
- boolean
- plural
- opposite
- world_fact

## Governance result

The historical policy is preserved unchanged.

The current frozen adjudicator implements the established policy
interfaces.

No threshold was changed after dataset sealing.

No candidate-specific rule was introduced.

No checkpoint was deserialized.

No model inference or scoring occurred.

Formal exposure has not started.

Formal execution remains unauthorized.
