# RL2 Scope and Conformance Boundary

**RL2 version:** 0.7 · **Status:** Draft proposal for review · **Date:** 2026-08-01

## Purpose

RL2 is an AI-generatable, deterministically evaluable policy language and a deterministic target
for the supported ODRL 2.2 fragment (`RL2_ODRL_Mapping.md`). It retains the familiar policy
concepts of ODRL 2.2 and addresses semantic choices that can cause independent evaluators to
assign different meanings to the same policy. Translation from ODRL 2.2 is deliberately partial
and fail-closed: a construct outside the supported fragment is rejected or profile-gated, never
silently weakened into a different meaning.

For the same canonical policy universe, request, world snapshot, and evaluation configuration,
conforming RL2 evaluators produce the same evaluation result.

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

RL2 defines:

- canonical policy syntax and RDF-to-AST projection;
- Privilege, Prohibition, Duty, and Promise clauses;
- policy, party, action, asset, and condition meaning;
- request structure and request-to-norm matching;
- immutable world snapshots and attributed evidence;
- missing, invalid, conflicting, and indeterminate information;
- Duty applicability, fulfillment, violation, and indeterminacy;
- policy composition, priority, and conflict resolution;
- pure Offer-to-Agreement materialization;
- evaluation results and their determining norms and diagnostics;
- explicit ODRL 2.2 translation rules; and
- conformance parameters required for independent evaluators to agree.

The evaluation contract may consume histories or externally derived values as finite snapshot
data. It does not prescribe how those inputs are collected or stored.

**Authoring forms compile down; `Eval`'s kernel never grows.** Between validated RDF and `Eval`
sits one normative compilation contract (`RL2_Compilation.md`): SHACL structural validation,
followed by a total, deterministic `compile` step that produces a closed `CompiledPolicyModule` or
a reproducible diagnostic set. Ergonomics — refinements, recurrence windows, profile vocabulary,
ODRL conveniences — live in that compile-down expansion; semantics and proof obligations live on
the evaluation kernel alone, so every authoring convenience is correct by construction of its
expansion into the kernel `compile` produces.

## Normative Positions

RL2 standardizes conduct norms with observable evaluator behavior:

- a Privilege may contribute a permit;
- a Prohibition may contribute a denial;
- a Duty contributes an obligation and a derived status; and
- a Promise records a proposed commitment in an Offer and may materialize into a Duty.

A Duty's optional `counterparty` identifies the beneficiary or other party to whom the Duty is
owed. RL2 does not require an additional Claim node to repeat that relationship.

Assignment, delegation, amendment, revocation, termination, and the legal effectiveness of such
acts require a separate normative-instrument transformation. RL2 does not standardize that
transformation and therefore does not expose Power, Liability, or Immunity as core norm classes.

## Out of Scope

The following are not requirements on a conforming RL2 evaluator:

- policy administration and discovery;
- request transport and authentication protocols;
- persistent workflow or case management;
- event-log storage, scheduling, and re-evaluation triggers;
- database layout, indexing, caching, or an optimized *internal* intermediate representation
  (distinct from the normative `CompiledPolicyModule` interchange form of `RL2_Compilation.md`,
  which fixes an interchange and conformance shape, not an execution strategy);
- locking, retry, transaction, replica-consistency, consensus, or distributed-commit protocols;
- audit-log storage and retention;
- enforcement, provisioning, masking, throttling, or resource reservation;
- assignment, delegation, amendment, revocation, or termination of normative positions; and
- a required implementation language, proof assistant, or verification toolchain.

## Duties and Evidence

Duty fulfillment and violation are language semantics. RL2 derives Duty status from canonical
Duty content, evaluation time, attributed facts, and action evidence in the supplied world
snapshot. It does not require a persistent Duty state machine or an evaluation cadence.

## External Data

A world snapshot binds every external value used during evaluation. RL2 defines how provenance,
missing values, invalid values, and conflicts affect evaluation. Fetching, refreshing, trusting,
storing, and distributing source data are deployment or profile concerns.

## ODRL 2.2 Migration

A conforming importer translates supported ODRL 2.2 structures into canonical RL2 or returns a
specified diagnostic. Each mapping is classified as `exact`, `normalized`, `clarified`,
`profile-dependent`, `rejected`, or `metadata-only`. A clarified mapping states its additional
interpretation explicitly; an importer does not silently choose among materially different
meanings.

## Deliverables

The RL2 proposal consists of:

1. the information model, ontology, SHACL shapes, and profiles;
2. the compilation contract from validated RDF to a `CompiledPolicyModule`, with its diagnostics
   and interchange schemas;
3. formal evaluation semantics;
4. ODRL 2.2 migration rules; and
5. structural and semantic conformance material.

The Primer, architecture overview, external-data guidance, vocabulary reference, and bibliography
are informative. `RL2_Primer.md` §13 gives a short, factual comparison of what RL2 improves on and
what it deliberately leaves to ODRL 2.2, OPA/Rego, Cedar, and Immuta — RL2 is narrower and more
auditable for its finite-snapshot decision problem, not a general replacement for those systems'
own execution or enforcement domains.
