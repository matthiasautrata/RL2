---
title: "RL2 Architecture"
subtitle: "Language Boundaries and Pure Evaluation"
version: "0.7-draft"
status: "Informative"
date: 2026-07-31
---

# RL2 Architecture

## 1. Purpose

RL2 is a policy language, not an authorization service architecture. This document explains how
the normative language artifacts fit together and where implementation freedom begins. Formal
definitions live in `../spec/`; this document does not define a second evaluator.

The architectural objective is reproducible meaning:

> Given the same canonical policy universe, request, world snapshot, and evaluation configuration,
> conforming evaluators return the same evaluation result.

## 2. Evaluation Boundary

```text
┌──────────────────────┐
│ Validated policy RDF │
└──────────┬───────────┘
           │ canonical projection
           ▼
┌──────────────────────┐     ┌─────────┐
│ Canonical policy AST │◀────│ Request │
└──────────┬───────────┘     └─────────┘
           │                 ┌────────────────┐
           │ Eval ◀──────────│ WorldSnapshot  │
           │                 └────────────────┘
           │                 ┌─────────────────────────┐
           │◀────────────────│ EvaluationConfiguration │
           ▼                 └─────────────────────────┘
┌──────────────────────┐
│ EvaluationResult     │
│ • decision           │
│ • normative envelope │
│ • duty statuses      │
│ • promise statuses   │
│ • diagnostics        │
└──────────────────────┘
```

`Eval` is pure. It neither fetches external data nor commits effects. A deployment may persist
inputs and outputs, but persistence is not part of the language semantics.

## 3. Language Layers

| Layer | Normative artifact | Responsibility |
|---|---|---|
| Scope | `../spec/RL2_Scope.md` | Core boundary and conformance classes |
| Information model | `../spec/RL2_Model.md` | Policy universe, request, snapshot, configuration, result |
| Vocabulary | `../spec/rl2.ttl` | Classes, properties, and named terms |
| Structural validation | `../spec/rl2-shacl.ttl` | Canonical authored shapes and diagnostics |
| Semantics | `../spec/RL2_Semantics.md` | Conditions, derivation, status, resolution |
| Migration | `../spec/RL2_ODRL_Mapping.md` | ODRL 2.2 translation and preservation rules |
| Conformance | `../conformance/` | Structural fixtures and expected semantic results |

Reader documentation under `docs/` is informative. Protocol and reference implementation ideas
under `future/` do not affect core conformance.

## 4. Semantic Pipeline

### 4.1 Validate and project

Input RDF is validated and mapped to one canonical AST. The projection resolves authoring
defaults and structural variation before evaluation. Unsupported terms and ambiguous ODRL input
produce diagnostics rather than being silently ignored.

Canonical projection is normative because two evaluators cannot agree if they interpret the same
RDF structure differently. Materializing indexes, bytecode, or another internal IR is optional.

### 4.2 Derive

The derivation stage evaluates request matching and effective conditions against one immutable
environment. It produces attributed normative atoms such as permits, prohibitions, obligations,
and indeterminate clauses.

Derivation is separate from conflict resolution. For a fixed environment, adding policies or
clauses can add atoms without making derivation depend on input order. Derivation is not claimed
to be monotone in world facts: negation and upper bounds can change a condition from true to false.

### 4.3 Interpret duties and Promises

Duty and Promise status is derived from canonical content, temporal scope, and evidence in the
world snapshot. Achievement Duties use action evidence plus an optional postcondition;
Maintenance Duties use an invariant over an optional finite half-open window. Evaluation does not
depend on whether an implementation previously executed an intermediate state-machine transition.

A Duty is either an independent Policy clause or a prerequisite referenced by one or more Privileges.
An applicable prerequisite must be Fulfilled before its owner can contribute a permit; an
independent Duty never changes the access decision. Concurrent and post-use scheduling belongs to
the future protocol, not to core evaluation. S2-C4 separately completes the pure Promise-to-Duty
acceptance transformation.

### 4.4 Resolve

Resolution applies the explicit evaluation configuration to the access atoms in the attributed
envelope. Priorities and the selected strategy determine one decision. Prerequisite status has
already affected its owning Privilege during derivation; other Duty atoms are not access
candidates. Causal errors remain
attributed so an `Indeterminate` result can explain which clauses and inputs prevented a definite
answer.

## 5. Request and World Snapshot

The Request contains the agent, action, and asset whose normative status is being evaluated.

The WorldSnapshot contains evaluation time, facts, and evidence. It is a semantic value, not a
storage prescription. A deployment may assemble it from request attributes, credentials,
databases, event logs, or APIs before evaluation.

Facts are addressed by a canonical path plus an explicit agent, asset, evaluation, state, or
global scope. Evidence is selected by declared kind, actor, action, object, payload, and interval
constraints. Equal assertions agree; distinct single-valued assertions conflict. Equally recent
evidence with unequal projected values also conflicts—arrival order and record identifiers do not
choose a winner.

RL2 specifies:

- which values and evidence a construct reads;
- typing and cardinality;
- identity and scoping needed for matching;
- behavior for missing, invalid, duplicate, conflicting, or indeterminate input.

RL2 does not specify:

- when facts are refreshed;
- how sources are queried;
- how evidence is persisted;
- how replicas synchronize;
- when reevaluation is scheduled.

## 6. External Data Boundary

Policy evaluation performs no live I/O. An implementation resolves external sources before
calling `Eval` and supplies the resulting values in the snapshot. This keeps the language
semantics total and replayable without standardizing connectors, credentials, timeouts, or source
registries.

Profiles may define operands, types, and provenance requirements. They may not replace missing
core semantics with an opaque implementation callback.

## 7. ODRL Migration

ODRL 2.2 is a source language for a conforming translation step, not a second native shape for
each RL2 proposition. Translation produces canonical RL2 or a specified diagnostic.

This separation allows RL2 to accept existing ODRL practice without weakening its canonical form.
It also exposes assumptions that ODRL leaves to evaluators, such as request matching, conflict
behavior, duty attachment, fulfillment evidence, and state-of-the-world interpretation.

## 8. Conformance Strategy

Structural conformance establishes that an RDF graph uses a valid authored shape. Semantic
conformance establishes that evaluation produces the specified result.

Each semantic vector contains:

- policy graph and canonical projection expectation;
- request;
- world snapshot;
- evaluation configuration;
- expected decision;
- normative envelope;
- duty/Promise statuses;
- diagnostics.

ODRL migration fixtures additionally identify the translation disposition and preservation claim.

## 9. Implementation Freedom

A conforming evaluator may use:

- direct AST interpretation;
- a compiled IR or bytecode;
- generated code;
- relational or graph indexes;
- caching and incremental recomputation;
- any implementation language or verification toolchain.

Those choices are conforming when their observable results match the normative evaluation
contract and conformance suite.

Enforcement is also outside RL2. A policy enforcement point may translate `Permit`, `Deny`, or
obligation information into application behavior, but it must not rewrite the semantic result and
present the rewritten value as RL2's decision.

## 10. Future Companion Work

The former architecture also explored:

- RDF request/result exchange;
- Requirements and Cases;
- event-sourced audit history;
- re-evaluation workflows;
- policy-generation binding;
- state effects, retries, and commits;
- a normalized-AST evaluator implementation.

That material is preserved under `../future/`. A future companion may standardize some of it with
its own conformance claims. It is not required to implement the RL2 language.

The full former Architecture is retained at
`../future/reference-implementation/RL2_Architecture_Scope1.md` for traceability.
