# D0-POST-008 Scoring Interface Specification

Status: FROZEN DESIGN CONTRACT

This document defines the required interface and invariants for the
future D0-POST-008 scoring dependency adapter.

It does NOT implement scoring.
It does NOT authorize formal execution.
It does NOT construct or open the formal dataset.
It does NOT load a checkpoint.
It does NOT perform inference or training.

## 1. Frozen Harness Interface

The dependency implementation MUST satisfy exactly the semantic
interface required by the frozen POST-008 harness:

    load_rows(dataset)
    score_checkpoint(checkpoint, rows)
    compare_results(baseline, candidate)

The adapter MUST NOT change the frozen harness contract merely to fit
an implementation.

## 2. Dataset Loading Boundary

`load_rows(dataset)` is the only scoring-interface operation permitted
to receive the formal dataset path.

The future real execution lifecycle MUST load the sealed POST-008
formal dataset exactly once after formal exposure has started.

`score_checkpoint()` MUST NOT accept, derive, reopen, search for, or
otherwise access the formal dataset path.

The same already-loaded in-memory row collection MUST be supplied to
both baseline and candidate scoring.

## 3. Row Validation

The future dependency adapter MUST validate the exact frozen POST-008
row schema before model scoring.

Schema validation MUST be deterministic and fail closed.

Malformed rows, unknown fields, missing required fields, invalid
families, empty required strings, duplicate identifiers if identifiers
are part of the final schema, or other violations defined by the later
dataset specification MUST cause rejection.

Validation rules MUST be frozen before the formal dataset is
constructed.

## 4. Baseline-First Ordering

The baseline checkpoint MUST be scored before candidate scoring.

The complete baseline aggregate result MUST be persisted using
create-once semantics before candidate model scoring begins.

Candidate scoring MUST NOT influence baseline scoring.

## 5. Candidate Ordering

Candidate scoring may begin only after successful baseline-result
persistence.

The candidate aggregate result MUST be persisted using create-once
semantics before formal comparison begins.

## 6. Persisted-Result Comparison

`compare_results(baseline, candidate)` MUST consume the persisted
baseline and persisted candidate results re-read from evidence storage.

The comparator MUST NOT:

- open the formal dataset;
- load either checkpoint;
- execute inference;
- rescore examples;
- regenerate model responses;
- adapt thresholds;
- modify normalization rules;
- modify family definitions;
- modify scoring weights.

## 7. Scoring Determinism

The future scoring implementation MUST use a frozen deterministic
evaluation configuration appropriate to the model architecture.

Any generation used for exact-match evaluation MUST use a frozen
deterministic decoding configuration.

No sampling-based candidate advantage is permitted.

Baseline and candidate MUST use identical evaluation code,
tokenization rules, normalization rules, decoding configuration, and
row ordering.

## 8. Checkpoint Identity

Before scoring, the real execution system MUST verify the frozen
cryptographic identity of both baseline and candidate checkpoints.

The scoring result MUST record the checkpoint path or immutable
identifier and its SHA-256 identity.

A checkpoint identity mismatch MUST fail closed before that checkpoint
is scored.

## 9. Result Structure

The future scoring result MUST contain enough information to support
the separately frozen adjudication policy without reopening the formal
dataset or checkpoint.

At minimum, the final result schema must support:

- stage identity;
- checkpoint identity;
- number of examples;
- response-token accounting where applicable;
- aggregate scoring metric(s);
- exact-match count/rate if retained by the final scoring policy;
- per-family aggregates;
- deterministic per-example result records required for audit.

The exact result schema and metric definitions MUST be frozen before
formal execution authorization.

## 10. Expected Responses and Generated Responses

Formal expected responses and model-generated formal responses are
evaluation evidence.

They MUST NOT be printed to interactive terminal output during formal
execution unless a later governance artifact explicitly authorizes
such disclosure.

They MUST NOT be used for development, training, candidate selection,
prompt tuning, threshold tuning, or retry decisions.

## 11. Failure Semantics

Any exception after formal exposure starts MUST produce create-once
failure evidence where mechanically possible.

Previously persisted evidence MUST never be overwritten.

A failed formal execution MUST NOT become permission to rerun the same
formal evaluation.

## 12. Training Boundary

The dependency adapter MUST contain no training operation.

Formal evaluation MUST NOT:

- update model weights;
- update optimizer state;
- update tokenizer state;
- fine-tune either checkpoint;
- retrain after observing formal results.

## 13. Development Isolation

POST-007 formal rows and historical formal datasets MUST NOT be opened
or reused to construct POST-008 formal rows.

POST-008 formal content MUST remain isolated from model development and
candidate selection.

## 14. Dependency Freeze Requirement

Before POST-008 formal dataset construction, the concrete dependency
adapter must be:

1. implemented;
2. tested exclusively with synthetic/development-safe data;
3. reviewed for dataset reopening;
4. reviewed for checkpoint identity handling;
5. reviewed for deterministic scoring;
6. regression-tested against the POST-007 lifecycle failure;
7. cryptographically frozen.

No formal rows may be constructed merely to debug the dependency
adapter.

## 15. Real Execution Remains Disabled

Freezing this specification does NOT:

- create the dependency adapter;
- construct the formal dataset;
- create formal exposure;
- enable real execution;
- authorize formal execution.

A later, separately reviewed sequence is required.
