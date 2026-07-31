# RL2 Scope and Conformance Boundary

## Status

This document records the governing SCOPE-2 project decision. It supersedes SCOPE-1 where that
decision included a runtime protocol, persistent Case model, or implementation-oriented IR in
the core specification deliverable.

## Purpose

RL2 is an AI-generatable, deterministically evaluable policy language that extends and clarifies
ODRL 2.2. Its primary purpose is to remove semantic choices that allow reasonable independent
ODRL evaluators to disagree about the meaning of the same policy.

For the same canonical policy universe, request, world snapshot, and evaluation configuration,
conforming RL2 evaluators produce the same observable evaluation result.

## Normative Evaluation Contract

The semantic center of RL2 is the pure function:

```text
Eval(
    PolicyUniverse,
    Request,
    WorldSnapshot,
    EvaluationConfiguration
) -> EvaluationResult
```

The normative specification defines:

- canonical policy syntax and RDF-to-AST projection;
- policy, rule, norm, party, action, asset, and condition meaning;
- request structure and request-to-rule matching;
- the contents and interpretation of an immutable world snapshot;
- missing, invalid, conflicting, and indeterminate information;
- duty applicability, attachment, fulfillment, violation, and indeterminacy;
- policy composition, priority, and conflict resolution;
- Promise and Hohfeldian constructs included in the RL2 language;
- the semantic Offer-to-Agreement transformation;
- evaluation results and the evidence needed to explain them;
- conformance parameters required for two evaluators to agree.

The specification may use abstract state or evidence histories as semantic input. Such input is a
mathematical value supplied to `Eval`; it does not prescribe a storage or messaging architecture.

## Out of Core Scope

The following are not requirements on a conforming RL2 language evaluator:

- persistent Case management;
- event-sourced storage;
- scheduling and re-evaluation triggers;
- clocks as active event producers;
- database layout, indexing, caching, or optimized IR design;
- compare-and-swap, locking, retry, or transaction protocols;
- replica consistency, consensus, or distributed commit;
- audit-log storage and retention;
- enforcement, provisioning, masking, throttling, or session management;
- a required implementation language, proof assistant, or verification toolchain.

These topics may appear in informative reference designs or future companion specifications, but
they do not affect core language conformance.

## State and Duties

Duty fulfillment is language meaning and therefore remains in scope. RL2 defines duty status as a
function of the duty, its attachment and temporal semantics, and evidence contained in the world
snapshot. Implementations may persist or reconstruct that evidence in any way that preserves the
normative input and result.

The core must not require evaluation cadence to determine duty status. Observing the same evidence
later must not produce a different result merely because an implementation skipped an intermediate
state-machine transition.

## External Data

RL2 defines how a world snapshot binds values required by conditions and how provenance, missing
values, invalid values, and conflicts affect evaluation. Fetching, refreshing, trusting, storing,
and distributing source data are deployment concerns unless a future profile standardizes them.

## ODRL 2.2 Migration

RL2 does not require arbitrary ODRL 2.2 RDF graphs to be native canonical RL2. A conforming importer
translates supported ODRL structures into canonical RL2 or returns a specified diagnostic.

Each ODRL construct is classified as `exact`, `normalized`, `clarified`, `profile-dependent`,
`rejected`, or `metadata-only`. A `clarified` mapping makes its added interpretation explicit; no
importer may silently choose among materially different meanings.

## Implementation and Verification

The language and semantics must be precise enough to implement and verify an evaluator. A reference
implementation, optimized IR, mechanized proof, and distributed deployment architecture are
follow-on work. Their absence does not weaken the requirement that the normative algorithms be
total, deterministic, bounded under declared conformance parameters, and testable against the
conformance suite.

## Deliverables

The SCOPE-2 project deliverables are:

1. RL2 information model, ontology, SHACL shapes, and profiles.
2. Formal evaluation semantics.
3. ODRL 2.2 compatibility and migration specification.
4. Structural and semantic conformance suite.

The Primer, vocabulary reference, and architecture overview are informative explanations of those
deliverables. Protocol and reference-implementation documents are retained separately as future
work.
