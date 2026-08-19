# D0.4 Response-Overlap Governance Clarification

## Status

This artifact clarifies the meaning of the existing D0.4
EVALUATION_PROTOCOL.md freshness requirement:

> exact normalized response overlap where inappropriate for the
> defined task

It does not replace, weaken, or modify the frozen D0.4 evaluation
contract or evaluation protocol.

It does not authorize model scoring.

It does not contain D0.4 evaluation examples.

## Purpose

The frozen protocol requires deterministic rejection of historical
response overlap where such overlap is inappropriate, but it does not
define a mechanical criterion for determining when response reuse is
inappropriate.

This clarification freezes that criterion before construction of the
real D0.4 evaluation dataset.

## Response-overlap rule

Historical normalized response overlap is not prohibited merely
because the same response text occurred historically.

A proposed response may repeat historical response text when the
response is objectively forced, canonical, or naturally reusable for
the independently constructed instruction.

Examples of response classes that may legitimately recur include
boolean answers, literal labels, single-token categorical answers,
and deterministic transformation outputs when the proposed
instruction independently determines that response.

Historical normalized response overlap is inappropriate and must be
rejected when the proposed example uses historical response text as
content that is not objectively forced by its independently
constructed instruction.

The freshness audit must therefore distinguish between:

1. response text that is independently required by the semantics of
   the proposed instruction; and

2. response text whose reuse is discretionary and could be replaced
   without violating the proposed instruction.

Case 1 is permitted with respect to response-only overlap.

Case 2 is prohibited when the normalized response exactly overlaps
historical material.

## Requirements that remain unconditional

This clarification does not change the unconditional prohibition on:

- exact normalized historical instruction overlap;
- exact historical instruction-response pair overlap;
- duplicate normalized instructions within D0.4;
- duplicate normalized instruction-response pairs within D0.4.

## Deterministic pre-seal representation

Because the distinction above cannot safely be inferred from model
behavior, every proposed D0.4 row must be classified during pre-seal
construction as either:

- response_reuse_class = "forced"
- response_reuse_class = "discretionary"

This classification is construction metadata used by the freshness
audit.

It is not a model input.

It is not a scoring target.

It must not be selected or changed after observing model behavior.

For a row classified as "forced", exact historical response-only
overlap is permitted, while historical instruction and pair overlap
remain prohibited.

For a row classified as "discretionary", exact normalized historical
response overlap is prohibited.

## Fail-closed behavior

The pre-seal validator must reject a proposed row if:

- response_reuse_class is missing;
- response_reuse_class has an unsupported value;
- a discretionary response exactly overlaps a historical normalized
  response;
- the row violates any other frozen D0.4 freshness requirement.

The validator must not silently infer or repair a missing
response_reuse_class.

## Historical isolation

This clarification does not authorize reopening any protected later
formal dataset.

Historical material whose governance prohibits inspection remains
excluded by provenance and frozen identity.

## Evaluation independence

The response-reuse classification must be established before model
scoring.

No classification may be changed because the canonical checkpoint is
expected to succeed or fail on an example.

## Authorization state

AUTHORIZED after this clarification:

- revision of D0.4 pre-seal tooling to implement this clarification;
- synthetic testing of the revised gate;
- freezing a replacement pre-seal package identity after validation.

NOT AUTHORIZED by this clarification:

- canonical checkpoint scoring;
- D0.4 final evaluation execution;
- training or retraining;
- checkpoint modification;
- tokenizer modification;
- historical evaluation reruns;
- D0.4 completion;
- lifecycle transition to D0.5.
