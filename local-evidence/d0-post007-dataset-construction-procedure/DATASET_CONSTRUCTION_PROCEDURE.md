# D0-POST-007 Fresh Formal Dataset Construction Procedure

## Status

PRE-FORMAL PROCEDURE FREEZE.

This document defines how proposed D0-POST-007 examples may be
constructed and validated.

It does NOT create the formal dataset.
It does NOT authorize model scoring.
It does NOT begin formal exposure.

## Governing principles

POST-007 exists as a fresh recovery stage after the POST-006
evaluation-pipeline compatibility failure.

The exposed POST-006 formal dataset must not be reused, repaired,
edited into POST-007, or used as a source of POST-007 examples.

No model output, response loss, candidate behavior, candidate
checkpoint, or formal scoring result may influence construction.

## Dataset contract

The future dataset must contain exactly 25 rows.

The frozen families are:

1. echo
2. boolean
3. plural
4. opposite
5. world_fact

There must be exactly five rows per family.

Rows must use the deterministic family interleaving required by
the frozen construction policy and compatibility validator.

Every row must contain only the frozen semantic fields accepted by
the validator.

## Construction sequence

Construction must proceed in the following order:

1. Create proposed examples outside the formal dataset path.

2. Construct examples from the frozen family definitions and
   objective task rules only.

3. Do not inspect candidate model behavior.

4. Do not run candidate inference.

5. Do not calculate candidate response loss.

6. Do not use the POST-006 exposed formal rows as examples.

7. Assemble exactly 25 proposed rows with five rows per family.

8. Run the exact frozen POST-007 compatibility validator against
   the complete proposed 25-row set.

9. If validation fails, the proposed dataset MUST NOT be sealed.

10. Correct or replace incompatible proposed rows using only the
    frozen task rules and compatibility requirements.

11. Rerun the exact same frozen validator.

12. Continue until one complete proposed 25-row dataset passes
    without modifying or weakening the validator.

13. Once the complete proposed dataset passes, freeze the proposed
    dataset content and record its SHA-256.

14. Only after that successful pre-seal validation may the exact
    validated bytes be moved/copied to the designated POST-007
    formal dataset path.

15. Hash the sealed formal dataset and verify that its SHA-256 is
    identical to the successfully validated proposed dataset.

16. After sealing, no row, instruction, response, family, order,
    punctuation, whitespace, or byte may be modified.

## Compatibility requirements

Every proposed row must pass the exact frozen encoding path using
the accepted baseline tokenizer and context contract.

Required checks include:

- non-empty instruction;
- non-empty response;
- valid frozen family;
- exact row count;
- exact family distribution;
- deterministic interleaving;
- no duplicate instruction;
- no unsupported semantic fields;
- complete formatted-prompt tokenizer coverage;
- complete response tokenizer coverage;
- successful encode_instruction();
- context-length compliance;
- at least one supervised response token.

No compatibility failure may be ignored.

## Forbidden adaptations

The following are forbidden:

- modifying the accepted tokenizer;
- adding tokenizer characters;
- weakening tokenizer coverage checks;
- silently replacing unsupported characters;
- stripping unsupported punctuation during evaluation;
- automatic truncation to force context fit;
- candidate-specific normalization;
- candidate-specific preprocessing;
- changing expected responses after model inspection;
- selecting examples based on model performance;
- threshold tuning from formal examples;
- modifying the frozen compatibility validator.

The examples must conform to the evaluator.

The evaluator must not be changed to conform to the examples.

## Freshness requirement

POST-007 examples must be freshly constructed.

The POST-006 exposed formal dataset may be preserved as historical
failure evidence only.

Its rows must not be copied, paraphrased, transformed, reordered,
or repaired into the POST-007 dataset.

## Model isolation

During construction and compatibility validation:

- accepted baseline inference is forbidden;
- candidate inference is forbidden;
- response-loss computation is forbidden;
- exact-match model scoring is forbidden;
- checkpoint comparison is forbidden.

Loading only the accepted baseline tokenizer/configuration metadata
required by the frozen structural compatibility validator is
permitted.

## Sealing boundary

Compatibility validation occurs BEFORE sealing.

Formal exposure does not begin merely because proposed rows are
being constructed and structurally validated.

After the validated dataset is sealed:

- its identity must be frozen;
- evaluator/dependency identities must be frozen;
- a new one-time POST-007 execution authorization must be created;
- formal execution must occur only through the separately frozen
  execution harness.

## Failure rule

If a proposed dataset fails compatibility before sealing, it is
not formal evidence and must not be sealed.

If a sealed POST-007 dataset later fails after formal exposure
begins, it must not be repaired or rerun under the same
authorization.

## Current prohibition

This procedure-freeze step does NOT authorize creation of the real
POST-007 formal dataset.

The next step may prepare a non-formal proposed-row workspace and
construction tooling only.
