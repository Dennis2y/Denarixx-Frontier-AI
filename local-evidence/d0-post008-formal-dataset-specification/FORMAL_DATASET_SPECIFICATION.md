# D0-POST-008 Formal Dataset Specification

## Status

FROZEN BEFORE FORMAL DATASET CONSTRUCTION.

This document defines the exact structural specification for the
future D0-POST-008 formal evaluation dataset.

It contains NO formal evaluation rows.

It does NOT authorize dataset construction, checkpoint loading,
model inference, scoring, formal exposure, or formal execution.

---

## 1. Target Artifact

The future sealed formal dataset path is:

`ml/data/d0_post008_formal.jsonl`

Format:

JSON Lines (JSONL).

Each non-empty line represents exactly one formal example.

---

## 2. Exact Row Schema

Every row MUST contain exactly these three keys:

- `family`
- `instruction`
- `response`

No additional keys are permitted.

All three values MUST be non-empty strings.

The expected response is scoring evidence only.

It MUST NOT be inserted into the model-visible instruction.

---

## 3. Frozen Capability Families

Exactly five capability families are permitted:

1. `echo`
2. `boolean`
3. `plural`
4. `opposite`
5. `world_fact`

No sixth family may be introduced after this specification freeze.

No family may be removed or renamed.

---

## 4. Frozen Allocation

Each family MUST contain exactly:

8 examples.

Total formal examples MUST therefore equal:

40 examples.

Required distribution:

- echo: 8
- boolean: 8
- plural: 8
- opposite: 8
- world_fact: 8

The allocation is uniform.

No family weighting may be changed after construction begins.

---

## 5. Freshness Requirement

Every POST-008 formal example MUST be newly constructed.

POST-006 and POST-007 formal datasets MUST NOT be opened during
construction.

No historical formal row may be copied, paraphrased, transformed,
or intentionally reconstructed.

POST-008 examples must be independently authored from the frozen
capability definitions.

---

## 6. Checkpoint Independence

Neither the accepted baseline nor retained candidate may be queried
during formal-row construction.

Rows MUST NOT be:

- selected according to checkpoint success;
- rejected according to checkpoint failure;
- rewritten after observing checkpoint behavior;
- ranked according to checkpoint behavior;
- filtered according to checkpoint behavior.

No model preview is permitted.

---

## 7. Family Semantics

### echo

The instruction requests deterministic reproduction of a supplied
short textual payload.

The expected response is the required reproduced payload.

Examples must vary lexical content.

### boolean

The instruction asks a deterministic binary/boolean reasoning
question whose expected answer is unambiguous under the frozen task
format.

Examples must not depend on subjective interpretation.

### plural

The instruction requests the plural transformation of a supplied
singular form.

Examples must include a deliberate mixture of regular and
development-compatible irregular transformations.

Every expected form must be unambiguous.

### opposite

The instruction requests the conventional opposite of a supplied
term under an explicit short-answer format.

Pairs must be semantically unambiguous.

### world_fact

The instruction asks a stable, non-time-sensitive factual question.

Facts must not depend on:

- current office holders;
- current prices;
- current population;
- live events;
- recent news;
- mutable rankings;
- current company status.

Expected answers must be short and independently verifiable.

---

## 8. Difficulty Distribution

Within each family, the eight examples should not be eight superficial
copies of one template.

Each family must contain controlled variation in wording and content.

Difficulty must be established from task structure, not from observed
model behavior.

No row may be made easier or harder after either checkpoint has been
evaluated.

---

## 9. Uniqueness

Exact duplicate instructions are forbidden.

Exact duplicate `(instruction, response)` pairs are forbidden.

A row must not be a trivial textual duplicate of another row with only
punctuation changed.

Cross-family accidental duplication must be rejected.

---

## 10. Response Requirements

Expected responses must:

- be deterministic;
- be non-empty;
- be independently established;
- follow the frozen task semantics;
- remain unchanged after sealing;
- remain hidden from model-visible prompt content.

Expected responses must not be obtained by querying either checkpoint.

---

## 11. Compatibility Requirement

Before sealing, every proposed row MUST pass the separately governed
POST-008 compatibility-validation path.

The evaluator MUST NOT be weakened to make an incompatible row pass.

If a proposed row is incompatible before sealing, that row may be
rejected and independently replaced before formal exposure.

Replacement must occur without querying baseline or candidate.

---

## 12. Construction Ordering

The permitted future sequence is:

1. freeze this specification;
2. freeze the compatibility validator;
3. construct fresh proposed rows;
4. validate schema and family allocation;
5. validate uniqueness;
6. validate tokenizer/context compatibility;
7. independently review expected responses;
8. seal the completed dataset;
9. compute and freeze SHA-256;
10. prohibit further modification.

Formal scoring is forbidden during steps 1–10.

---

## 13. Sealing Conditions

The dataset may be sealed only if:

- exactly 40 valid rows exist;
- exactly 8 rows exist per family;
- all rows contain exactly the frozen keys;
- all required strings are non-empty;
- no forbidden duplicate exists;
- all rows pass compatibility validation;
- freshness/isolation attestations pass;
- no checkpoint has been queried using proposed formal rows.

After sealing, content modification is forbidden.

---

## 14. Exposure Boundary

Dataset construction and sealing are NOT formal exposure.

Formal exposure begins only when the separately authorized execution
path creates `FORMAL_EXPOSURE_STARTED` immediately before loading the
sealed formal rows for real scoring.

After exposure begins, the dataset cannot be repaired or replaced.

---

## 15. Adjudication Independence

Dataset content must not be designed around the frozen acceptance
thresholds.

The adjudication policy remains separate from example construction.

Rows must measure the frozen capabilities rather than engineer a
desired PASS or FAIL.

---

## 16. Current Boundary

At this specification freeze:

- formal rows created: 0
- formal dataset exists: NO
- formal dataset opened: NO
- historical formal datasets opened: NO
- real checkpoint loaded: NO
- model inference executed: NO
- model scoring executed: NO
- training executed: NO
- formal exposure started: NO
- real execution enabled: NO
- real execution authorized: NO

The next permitted stage is compatibility-validator design/freeze.

It is still NOT formal dataset construction.

Created: `2026-08-15T17:46:17.338360+00:00`
