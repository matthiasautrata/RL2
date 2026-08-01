# RL2 Architecture

## Status

This document is informative. The normative definitions are in `../spec/`.

## 1. Evaluation Boundary

RL2 is a policy language, not an authorization-service or distributed-protocol architecture. Its
observable contract is:

```text
validated RDF --canonical projection--> policy AST

Eval(policy universe, request, world snapshot, configuration)
    -> explained evaluation result
```

`Eval` is pure: it performs no external I/O, persistence, scheduling, state transition, or
enforcement. Given equal canonical inputs, conforming evaluators return equal results.

## 2. Specification Layers

| Layer | Artifact | Responsibility |
|---|---|---|
| Scope | `../spec/RL2_Scope.md` | Language and conformance boundary |
| Information model | `../spec/RL2_Model.md` | Inputs, outputs, snapshot, and transformation values |
| Vocabulary | `../spec/rl2.ttl` | RDF terms and relationships |
| Validation | `../spec/rl2-shacl.ttl` | Canonical authored structures |
| Semantics | `../spec/RL2_Semantics.md` | Conditions, status, derivation, and resolution |
| Migration | `../spec/RL2_ODRL_Mapping.md` | Deterministic ODRL 2.2 translation |
| Conformance | `../conformance/` | Examples and expected observable behavior |

Reader documentation is informative. Follow-on ideas in `../future/` do not affect conformance.

## 3. Semantic Pipeline

### 3.1 Validate and project

SHACL rejects non-canonical or structurally incomplete authored RDF. Canonical projection maps the
validated graph to one normalized AST, resolves defaults, and checks supported profiles. An
implementation may use any internal representation after this boundary.

### 3.2 Match and evaluate conditions

The evaluator identifies policies and norms relevant to the Request. Conditions read only typed
facts in the immutable WorldSnapshot. Their result is `True`, `False`, or `Unknown`
with causal errors.

### 3.3 Interpret duties and promises

Duty and Promise statuses are derived from canonical content, evidence, evaluation time, and
optional Duty windows. They are not stored state-machine transitions. A prerequisite Duty gates
only the Privilege that refers to it; an independent Duty does not silently become an access
precondition.

### 3.4 Derive and resolve

Derivation produces attributed permit, prohibit, obligate, and indeterminate atoms. Resolution
then applies priorities and the configured conflict strategy. Keeping these stages separate makes
the determining clauses and causal errors observable.

## 4. External Data

An implementation assembles the WorldSnapshot before calling `Eval`. It may use databases,
credentials, APIs, caches, or logs, but those mechanisms do not change the meaning of an already
constructed snapshot. Profiles declare operand paths, types, and fact provenance rules; the
configuration supplies a finite evidence-admissibility rule. Neither may introduce hidden live
callbacks into evaluation.

This boundary gives deployments freedom over freshness, trust establishment, consistency, and
storage while preserving replayable policy meaning. See [External Data](RL2_ExternalData.md).

## 5. Offer Materialization

Offer acceptance is a separate pure transformation:

```text
materialize(Offer, Acceptance)
    -> Materialized(Agreement, sourceMap) | Rejected(errors)
```

It uses caller-supplied identifiers and bindings, rewrites local references, copies proposed
Norms, and converts action and state Promises into beneficiary-bearing Duties. It does
not infer acceptance, allocate identifiers nondeterministically, or create a runtime record.

## 6. ODRL Input

ODRL 2.2 is accepted through an explicit translation step. Translation expands compact syntax,
flattens supported inheritance, atomizes rules, and either produces canonical RL2 or reports a
stable diagnostic. It does not preserve multiple equivalent RDF spellings inside the core
language.

## 7. Implementation Freedom

A conforming evaluator may use direct interpretation, compiled bytecode, generated code,
relational plans, graph indexes, caching, or incremental recomputation. The implementation must
remain observationally equivalent to the normative contract and conformance vectors.

API design, source connectors, enforcement, audit storage, retries, transactions, distributed
coordination, and formal-verification toolchains are outside the language specification. A future
companion specification may address them without changing core policy meaning.
