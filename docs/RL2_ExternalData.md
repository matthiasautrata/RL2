# RL2 External Data

## Status

This document is informative. The normative snapshot model is in `../spec/RL2_Model.md`.

## 1. Rule

Policy evaluation performs no external I/O:

```text
Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)
    -> EvaluationResult
```

Every fact and item of evidence read by a policy is already present in the immutable
WorldSnapshot. Missing, invalid, and conflicting data is handled by the formal result algebra,
not by implementation-specific fallback behavior.

## 2. Snapshot Contents

The snapshot contains:

- `evaluationTime`, the instant used by temporal expressions;
- attributed facts, each with a canonical scoped key, typed value, and validity interval; and
- attributed evidence of an action, with its occurrence time, actor, action, and object.

Facts are scoped to the requesting agent, requested asset, evaluation context, state, or a global
namespace. Request identity fields are read directly from the Request. Performance evidence is
selected by explicit actor, action, object, interval, and profile criteria.

## 3. Profile-Declared Operands

A profile defines an operand's identity, value type, cardinality, allowed operators, and canonical
`rl2:resolutionPath`. It may also require explicit issuer, source, profile version, or freshness
metadata.

A resolution path is a key in the semantic snapshot. It is not a host-language property path and
does not authorize a live lookup. Unknown operands and unsupported profile versions are errors.

For a single-valued fact key, equal eligible assertions agree and unequal values conflict. A
multi-valued operand uses one canonical set value. Profiles cannot replace these rules with an
implicit first, newest, or preferred-source choice.

## 4. Assembly Boundary

A deployment may assemble a snapshot using request attributes, database reads, verified
credentials, signed assertions, APIs, caches, or event stores. Credentials, connection failures,
timeouts, retries, and trust discovery are resolved before evaluation.

The assembler is responsible for producing a coherent snapshot. Snapshot validation rejects
invalid intervals and reuse of one identifier for unequal normalized records. Evidence after the
evaluation time is ineligible. Storage order and arrival order have no semantic effect.

## 5. Provenance and Trust

A required profile may declare a finite, pure fact-admissibility predicate. Evaluation
configuration separately supplies one total evidence-admissibility rule, which may explicitly
accept all Evidence. Cryptographic verification or source authentication happens before `Eval`;
the evaluator consumes their attributed result.

## 6. Re-evaluation

An application may request missing inputs, refresh a snapshot, and evaluate again. Each call is a
separate evaluation over one immutable input. RL2 does not standardize subscription, polling,
retry, or event-delivery protocols.

Conformance vectors supply snapshots directly, making resolution behavior replayable without
requiring any particular external system.
