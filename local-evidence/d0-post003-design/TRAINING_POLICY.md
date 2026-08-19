# D0-POST-003 Predeclared Training Policy

## Status

FROZEN BEFORE POST-003 OPTIMIZATION

No POST-003 development result had been observed when
this optimization configuration and candidate-selection
rule were frozen.

## Research purpose

POST-003 tests whether the accepted D0 model can acquire
a broader collection of controlled instruction mappings
while retaining useful language-model behavior.

This remains a tiny-model research experiment.

## Starting checkpoint

Training starts exactly from:

`local-checkpoints/d0-post002-accepted.pt`

SHA-256:

`31038f7801ae64f99aad4ec88e7aaa276917be9dec84ef0944b121578a36ca97`

The POST-002 optimizer state is NOT resumed.

POST-003 initializes a fresh AdamW optimizer around the
accepted POST-002 model weights.

This makes POST-003 a new optimization stage starting
from accepted POST-002 parameters rather than a literal
continuation of POST-002 optimizer moments.

## Supervised data

Frozen capability dataset:

`ml/data/d0_post003_capabilities.jsonl`

SHA-256:

`af597165dba3f3c76672004759aa2fcc899f32b0eccd7737bebdaa94651242fe`

Frozen training split:

`ml/data/d0_post003_train.jsonl`

SHA-256:

`0ccc376954deba3c013789cde803cf230ee894bb91a7d2afd5105f2d0ee481a2`

Examples:

25

Frozen development split:

`ml/data/d0_post003_dev.jsonl`

SHA-256:

`dc7beefa2615b664438c445f5b13f6a579ddd2fff55b91420e7fc29e9c47c45b`

Examples:

5

The development examples must never enter gradient
optimization.

The POST-003 training implementation must consume the
frozen training split directly.

It must NOT call the historical internal SFT splitting
procedure to create another train/validation partition.

## Capability families

Five capability families are represented:

1. echo
2. binary
3. transform
4. qa
5. semantic

Training contains exactly five examples per family.

Development contains exactly one example per family.

## Language-model retention data

POST-003 continues to use:

`ml/data/d0_research_corpus.txt`

as the language-model retention corpus.

The corpus identity must be verified before training.

POST-003 must not use EVAL-001 or EVAL-002 V4 as
retention-training data.

## Objective

The objective is fixed as:

`L = L_response + 0.25 * L_lm`

Retention weight:

`lambda = 0.25`

No new retention-weight search is permitted.

## Optimizer

Optimizer:

`AdamW`

Learning rate:

`1e-4`

Weight decay:

`0.01`

No learning-rate scheduler is used.

No warmup is used.

These values are inherited from the accepted POST-002
training configuration rather than selected using
POST-003 development performance.

## Gradient handling

Maximum gradient norm:

`1.0`

Gradient clipping is applied before every optimizer step.

## Batch configuration

Supervised batch size:

`4`

Language-model retention batch size:

`4`

Supervised examples are sampled from the frozen
25-example POST-003 training split.

Sampling uses the deterministic POST-002 mechanism:

`torch.randint`

with a dedicated generator seeded with:

`42`

Language-model batches use a separate generator seeded
with:

`43`

## Random seed

Global training seed:

`42`

POST-003 performs no seed search.

## Optimization duration

POST-003 performs exactly:

`20 optimizer steps`

There is:

- no epoch-based stopping,
- no early stopping,
- no adaptive extension,
- no shortening based on development results.

The 20-step duration is inherited from POST-002 before
POST-003 development performance is observed.

## Candidate checkpoint rule

Exactly one POST-003 training run is authorized under
this policy.

The model state immediately after optimizer step 20 is
the POST-003 candidate checkpoint.

There is no:

- best-development checkpoint selection,
- intermediate checkpoint competition,
- checkpoint averaging,
- seed competition,
- learning-rate competition,
- retention-weight competition,
- training-duration competition.

Development performance does not select which training
step becomes the candidate.

Step 20 is predeclared as the candidate before training.

## Development evaluation rule

After the step-20 candidate exists, it may be evaluated
once against the frozen POST-003 development set for the
predeclared development decision.

The development set must not be used to modify:

- training examples,
- dataset split,
- optimizer,
- learning rate,
- retention weight,
- batch sizes,
- random seed,
- training duration,
- architecture,
- tokenizer,
- or candidate checkpoint.

If POST-003 fails its development criterion, the run is
recorded as a failed experiment.

A changed configuration requires a separately declared
future experiment rather than silently rerunning
POST-003.

## Historical evaluation rule

D0-EVAL-001 and D0-EVAL-002 V4 remain immutable
historical confirmation evaluations.

They must not be used for POST-003 candidate selection
or hyperparameter tuning.

They must not determine:

- learning rate,
- optimizer,
- batch size,
- retention weight,
- seed,
- number of steps,
- dataset composition,
- candidate checkpoint.

## Formal acceptance rule

POST-003 development performance alone cannot establish
formal acceptance.

After the POST-003 candidate is fixed, a separate,
previously untouched POST-003 formal evaluation protocol
must be designed and frozen before formal candidate
scoring.

Formal evaluation data must not be generated or revised
after observing the POST-003 candidate's performance on
that formal evaluation.

## Architecture invariants

POST-003 preserves:

- vocab_size = 42
- context_length = 32
- hidden_size = 64
- layers = 2
- attention_heads = 4
- dropout = 0.0
- normalization = layernorm
- position encoding = rope
- parameter count = 102784

## Tokenizer invariant

The accepted 42-character tokenizer remains unchanged.

## Scientific scope

A successful POST-003 result would demonstrate only
controlled capability acquisition in the D0 research
model.

It would not establish:

- general reasoning,
- broad language understanding,
- frontier capability,
- production readiness,
- competitiveness with modern large language models.
