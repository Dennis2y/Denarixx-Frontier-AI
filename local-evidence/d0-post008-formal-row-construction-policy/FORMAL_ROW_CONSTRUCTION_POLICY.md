# D0-POST-008 Formal Row Construction Policy

## Status

FROZEN BEFORE FORMAL ROW CONSTRUCTION.

This policy governs the future construction of the fresh
D0-POST-008 formal evaluation dataset.

No formal rows are created by this step.

## Frozen dataset size

The future formal dataset contains exactly:

- 40 total rows;
- 5 capability families;
- 8 rows per family.

The frozen families are:

1. echo
2. boolean
3. plural
4. opposite
5. world_fact

## Exact schema

Every row must contain exactly:

- family
- instruction
- response

No additional field is permitted.

## Construction independence

Rows must be authored without:

- loading the accepted baseline;
- loading the retained candidate;
- querying either checkpoint;
- observing model generations;
- observing response losses;
- observing exact-match behavior;
- filtering based on model performance;
- changing thresholds based on proposed rows.

## Historical isolation

Historical formal datasets must not be opened.

No POST-006 or POST-007 formal row may be copied,
rewritten, paraphrased, translated, or deliberately reproduced.

Construction must begin from the frozen capability specification,
not historical formal examples.

## Family construction requirements

### echo

Eight independent instructions requiring deterministic reproduction
of clearly specified text.

Rows must vary the requested content while remaining unambiguous.

### boolean

Eight independent deterministic boolean tasks.

Each expected response must have one objectively correct canonical
answer under the instruction.

### plural

Eight independent singular/plural transformation tasks.

Expected responses must be deterministic and linguistically
unambiguous.

### opposite

Eight independent opposite/antonym tasks.

Only terms with a clear intended opposite under the instruction
may be used.

### world_fact

Eight stable, elementary world-fact questions.

Facts must not depend on current events, changing office holders,
live prices, temporary statistics, or time-sensitive information.

## Difficulty and diversity

Rows within a family must not be trivial textual duplicates.

The dataset must include reasonable lexical and structural diversity.

Difficulty must be selected independently of known baseline or
candidate behavior.

## Expected-response independence

Reference responses must be established during row construction,
before any formal scoring.

Expected responses must not be derived from baseline or candidate
outputs.

## Compatibility boundary

After the 40 proposed rows are constructed, they must pass the
already-frozen POST-008 compatibility validator unchanged.

The validator must not be weakened, patched, or adapted merely to
make a proposed formal row pass.

A row that fails compatibility must be rejected before sealing.

Any replacement must be constructed under this same policy without
querying either checkpoint.

## No model exposure during construction

Formal-row construction does not authorize:

- checkpoint loading;
- inference;
- scoring;
- candidate inspection;
- formal comparison;
- training;
- retraining.

## Construction and sealing separation

Creating proposed rows does not seal them.

The future sequence is:

1. construct exactly 40 proposed rows;
2. structurally inspect them;
3. run the frozen compatibility validator;
4. verify exact family allocation;
5. verify freshness and isolation attestations;
6. compute the proposed dataset SHA-256;
7. separately seal the dataset identity.

No model scoring may occur during these steps.

## Formal exposure boundary

Dataset construction and compatibility validation are pre-exposure
activities.

FORMAL_EXPOSURE_STARTED must NOT be created during construction,
validation, or sealing.

Formal exposure begins only in the later separately authorized
one-time execution lifecycle.

## Modification boundary

Before sealing, a structurally or compatibility-invalid proposed row
may be replaced under this frozen construction policy.

After sealing, no row may be modified, repaired, reordered,
reweighted, or replaced.

## Training prohibition

Neither proposed nor sealed POST-008 formal rows may be used for:

- training;
- fine-tuning;
- retraining;
- candidate selection;
- checkpoint selection;
- prompt tuning;
- threshold tuning.

## Current boundary

At policy freeze time:

- formal rows created: 0;
- formal dataset exists: NO;
- historical formal datasets opened: NO;
- baseline loaded: NO;
- candidate loaded: NO;
- inference executed: NO;
- scoring executed: NO;
- training executed: NO;
- formal exposure started: NO;
- formal execution enabled: NO;
- formal execution authorized: NO.

Created: 2026-08-15T17:48:54.641201+00:00
