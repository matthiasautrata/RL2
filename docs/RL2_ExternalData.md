---
title: "RL2 External Data"
subtitle: "World Snapshot Input and Implementation Boundary"
version: "0.2-draft"
status: "Informative"
date: 2026-07-31
---

# RL2 External Data

## 1. Purpose

RL2 policies may depend on facts not contained in the policy graph: organizational roles,
credential status, asset classifications, measurements, counts, prior actions, or evaluation
time. The normative evaluator receives those facts in an immutable `WorldSnapshot`.

This document explains that boundary. It does not standardize connectors or live data access.

## 2. Core Rule

The evaluator performs no external I/O during `Eval`:

```text
Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)
    -> EvaluationResult
```

All values and evidence read by conditions must already be present in the snapshot. Missing,
invalid, duplicate, and conflicting data is handled by the formal result/truth algebra rather than
by hidden fallback behavior.

## 3. Snapshot Contents

The information model separates:

- `evaluationTime` — the time at which temporal expressions are interpreted;
- `facts` — typed values bound to declared operands or canonical fact keys;
- `evidence` — attributed observations or occurrences used by duties, Promises, and event-sensitive
  conditions.

An implementation may assemble these values from any suitable source before evaluation. The
source system is not part of the policy semantics unless a profile makes source identity,
provenance, or freshness a policy-relevant field.

Normatively, each fact has a stable assertion identifier, canonical scoped path, typed value,
half-open validity interval, and attribution. Each evidence item has a stable identifier, kind,
occurrence time, optional actor/action/object, payload, and attribution. See
`../spec/RL2_Model.md` §4.

## 4. Profile-Declared Operands

A profile may define:

- operand identity and value type;
- cardinality;
- the canonical snapshot key or path;
- allowed operators;
- required provenance, issuer, or freshness information;
- a finite attribution-admissibility predicate over explicit configuration parameters.

A resolution path describes how a value is addressed within the semantic snapshot. It does not
authorize the evaluator to query an arbitrary live object graph or execute an unrestricted
function.

An unsupported profile or operand produces a specified diagnostic. Implementations must not
silently ignore an unknown policy term.

Profiles do not choose arbitrary conflict algorithms. Equal single-valued assertions agree;
distinct values conflict. A genuinely multi-valued operand uses one canonical set value.

## 5. Snapshot Assembly

Snapshot assembly is an implementation concern. A deployment might use:

- request attributes or identity tokens;
- database reads under a transaction or coherent read view;
- credential verification;
- an application event store;
- signed assertions;
- a cached source adapter.

These mechanisms may have their own timeout, retry, trust, and consistency requirements. They
complete before `Eval` begins and are outside the core totality and complexity claims.

## 6. Coherence

One evaluation must not combine values as though they represented one world state when the
applicable profile declares them inconsistent or stale. Snapshot validation rejects conflicting
reuse of one fact/evidence identifier and invalid time intervals. For one fact key, equal values
collapse and unequal values produce `Conflict`.

Fact scope is explicit: requesting-agent and requested-asset attributes are keyed by their
identities; context, state, and global facts occupy separate scopes. Evidence selectors state
their actor, action, object, payload, and interval constraints. Duty witnesses must include the
Duty subject and object. Evidence arrival order, Case membership, and storage version have no
semantic effect.

Most-recent evidence means greatest occurrence time. If equally recent evidence projects unequal
values, resolution returns `Conflict`; an identifier is never used as a semantic tie-breaker. If
any equally recent selected item lacks the projected field or supplies the wrong type, resolution
returns `Invalid`. `Missing` means that no eligible item exists.

Profiles may require attribution fields and define admissibility over declared trust parameters.
Credential verification and trust discovery occur before `Eval`; the predicate itself performs no
I/O or opaque callback.

## 7. Interaction Patterns

Applications may offer single-shot, iterative, or preflight APIs, but those are API designs rather
than policy semantics. For example, an API may report missing snapshot fields and accept a later
retry. The eventual `Eval` call is still made with one complete semantic input, and the returned
diagnostics must match the normative algebra.

## 8. Testing

Conformance vectors supply snapshots directly. The component vectors in
`../conformance/vectors/snapshot-resolution.md` cover scope, validity, duplicate identity,
conflicts, future evidence, attribution, and tied projections. They do not require live source
adapters. A future reference evaluator may test adapters separately with mock sources, but adapter
behavior cannot change the expected semantic result for a given snapshot.

The former SourceBinding, ContextManifest, live-resolution, and interaction-mode design is retained
at `../future/reference-implementation/RL2_ExternalData_Scope1.md`.
