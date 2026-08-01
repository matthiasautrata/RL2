# RL2 Information Model

**Version:** 0.7

## Status

This document defines the normative inputs and outputs of RL2 evaluation. Detailed denotations
and algorithms are defined in `RL2_Semantics.md`.

## 1. Purpose

RL2 expresses policies and defines their observable evaluation meaning. A conforming evaluator
accepts a canonical policy universe, a request, an immutable world snapshot, and an evaluation
configuration. It returns an explained result without performing external I/O or prescribing how
inputs and outputs are stored.

```text
Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)
    -> EvaluationResult
```

Evaluation is pure: identical inputs produce identical outputs.

## 2. Policy Universe

A `PolicyUniverse` is a finite collection of validated RL2 policies evaluated together. The
universe supplied to one evaluation is immutable. Policy discovery, administration, publication,
version selection, and distribution are outside `Eval`; the caller supplies the universe to be
interpreted.

Canonical projection also computes the finite action-inclusion, collection-membership, and
`rdf:type`/`rdfs:subClassOf` indexes referenced by those policies and their required profiles.
Those indexes are part of PolicyUniverse identity; an evaluator does not consult an ambient graph.
Collection-membership indexes cover both `rl2:AssetCollection` (direct `rl2:member`) and
`rl2:AgentCollection` (direct `rl2:agentMember`); neither is transitively closed.

Canonical RDF ingestion maps the universe to the normalized abstract syntax defined by the
Semantics. Canonical projection, including defaults and supported ODRL translations, is part of
language conformance. An implementation-specific index or IR is not.

## 3. Request

A core request is the proposition being evaluated:

```text
Request = (
    requestingAgent : Agent,
    requestedAction : Action,
    requestedAsset  : Asset
)
```

`requestingAgent` and `requestedAsset` name a concrete Agent and Asset; the sentinel individuals
`rl2:anyAgent` and `rl2:anyAsset` (used only in norm `rl2:subject`/`rl2:object` to declare an
attribute-defined population; see `RL2_Semantics.md` §Request Matching) are never valid values
here. A Request naming a sentinel is invalid and rejected before evaluation.

Authentication credentials, transport metadata, request identifiers, submission times, and
delegation chains may be represented as snapshot facts or by an interchange profile when policy
meaning depends on them. They are not implicit fields with unspecified semantics.

## 4. World Snapshot

A `WorldSnapshot` is a finite, immutable semantic input:

```text
WorldSnapshot = (
    evaluationTime : Time,
    facts          : finite set of AttributedFact,
    evidence       : finite set of Evidence
)
```

`Time` is a totally ordered instant domain. Concrete interchange datatypes must map each accepted
lexical form to one instant before evaluation; lexical form is not part of instant equality.

The remaining snapshot types are:

```text
FactScope ::= AgentScope(Agent)
            | AssetScope(Asset)
            | EvaluationScope
            | StateScope
            | GlobalScope

FactKey = (
    scope : FactScope,
    path  : canonical Path
)

Interval = (
    startInclusive : Time?,
    endExclusive   : Time?
)

Attribution = (
    issuer     : IRI?,
    source     : IRI?,
    profile    : (IRI, Version)?,
    observedAt : Time?
)

AttributedFact = (
    id          : IRI,
    key         : FactKey,
    value       : Value,
    validDuring : Interval,
    attribution : Attribution
)

Evidence = (
    id          : IRI,
    occurredAt  : Time,
    actor       : Agent,
    action      : Action,
    object      : Resource,
    attribution : Attribution
)
```

An `AttributedFact` binds one canonical path, in one explicit scope, to a typed value. `Evidence`
records an observed action used by Duty and Promise status functions. `id` identifies an
assertion or evidence item, not the real-world entity described by it.

The snapshot is a coherent mathematical value. RL2 does not require that it be stored as one
record, produced by event sourcing, or shared across evaluations. Implementations may assemble it
from databases, credentials, logs, APIs, or application state before calling `Eval`.

The evaluator performs no live lookup while evaluating a snapshot. Missing, invalid, duplicate,
or conflicting values are handled by the result and truth algebra in `RL2_Semantics.md`; they are
not resolved through implementation-specific fallback behavior.

### 4.1 Canonicalization and identity

Before policy derivation, `validateSnapshot` performs the following normalization:

1. Paths, values, field names, IRIs, versions, and instants are converted to their canonical
   semantic values.
2. A repeated `AttributedFact.id` is collapsed only when every normalized field is equal. The
   same rule applies to a repeated `Evidence.id`.
3. Reuse of one identifier for unequal normalized records makes the snapshot structurally
   invalid. `Eval` returns `Indeterminate` with an `Invalid` snapshot diagnostic; it does not
   evaluate policies against an arbitrarily selected record.
4. An interval is valid exactly when its present endpoints satisfy `startInclusive <
   endExclusive`. Missing endpoints mean unbounded. An invalid interval makes the snapshot
   structurally invalid.
5. Evidence later than `evaluationTime` is not eligible for a query. It is not deleted from the
   value, because the same supplied collection may be normalized for another evaluation time.
6. Every Evidence actor, action, and object is present and has the declared type. A malformed
   record makes the snapshot structurally invalid.

Arrival order, RDF statement order, database version, and storage sequence are
not semantic identity or tie-breaking fields.

`validateSnapshot(W,C)` returns the finite set of canonical `Invalid(SnapshotSite(field))`
diagnostics found by these rules and the declared snapshot bounds. The set is empty exactly when
the normalized snapshot is structurally valid.

### 4.2 Fact resolution

The path root determines the fact scope; the root itself remains part of the canonical path:

| Path root | Scope |
|---|---|
| `agent` | `AgentScope(Request.requestingAgent)` |
| `asset` | `AssetScope(Request.requestedAsset)` |
| `context` | `EvaluationScope` |
| `state` | `StateScope` |
| `global` | `GlobalScope` |
| `request` | read directly from `Request`, not from `facts` |

`state.Clock` denotes `evaluationTime` and is not an `AttributedFact`. A profile may define other
`state`, `context`, or `global` paths, but every such path resolves through the fact algorithm
below.

The only core `request.*` paths are `request.requestingAgent`, `request.requestedAction`, and
`request.requestedAsset`. They resolve directly from Request. Other request metadata uses a
declared `context.*` fact or a separate interchange profile; arbitrary `request.*` fields are not
canonical core paths.

For a required key `k`, expected value type `τ`, profile `p`, snapshot `W`, and configuration `C`:

```text
resolveFact(k, τ, p, W, C) =
    let candidates = {
        f in W.facts |
        f.key = k and contains(f.validDuring, W.evaluationTime)
    }
    in if candidates = empty then Err(Missing({ site: SnapshotSite(k.path), target: None }))
       else if any f in candidates is not admissibleFact(p, f.attribution, C)
            then Err(Invalid({ site: SnapshotSite(k.path), target: None }))
       else if any f.value is not of type τ
            then Err(Invalid({ site: SnapshotSite(k.path), target: None }))
       else let values = distinctSemanticValues(candidates)
            in if |values| = 1 then Ok(the element of values)
               else Err(Conflict({ site: SnapshotSite(k.path), target: None }))
```

Each `Err` carries the canonical `ErrorKey` record defined in `RL2_Semantics.md` (§Result and
Truth Algebra): `site` identifies the failing snapshot path via `SnapshotSite(String)`, and
`target` is the `StateTarget?` of the Duty or Promise being evaluated, when the fact lookup is
part of status derivation, or `None` for an ordinary operand lookup.

Equal values asserted under different identifiers therefore agree; they do not create a
conflict. Distinct values for a single-valued key conflict. A profile that needs multiple values
declares a set-valued operand; its value is one canonical `VSet`, with semantic duplicate removal
and canonical member ordering. A profile cannot replace this algorithm with an implicit
first-value, newest-value, or source-priority rule.

Expired and not-yet-valid facts are outside the candidate set. Consequently, a key for which all
assertions are outside their validity intervals is `Missing`, not `False`.

### 4.3 Evidence selection

Evidence is selected by an explicit selector:

```text
EvidenceSelector = (
    actor       : Agent,
    actions     : finite non-empty set of Action,
    object      : Resource,
    during      : Interval?
)
```

An evidence item matches when its actor and object equal the selector values, its action belongs
to `actions`, and its occurrence is no later than `evaluationTime` and within `during` when
supplied. There is no ambient request scope.

The query functions make the error boundary explicit:

```text
selectEvidence(selector, W, C) =
    let raw = {
        e in W.evidence |
        actorActionObjectTimeMatch(e, selector, W.evaluationTime)
    }
    in if any e in raw is not admissibleEvidence(e, C)
       then Err(Invalid(selector))
       else Ok(raw)
```

Core Duty and Promise selectors use the subject, the required action plus its finite set of
included actions, the object, and the applicable temporal interval. These values come from the
clause; they are not implicitly copied from the current Request. `admissibleEvidence` is the total
finite rule supplied by the evaluation configuration; it may inspect the selected Evidence and
its attribution. No matching evidence is `Ok(empty)`, meaning performance has not been established.

### 4.4 Profile provenance and trust

Core RL2 does not declare an issuer trustworthy merely because an assertion is present. A profile
may define a total `admissibleFact(profile, attribution, configuration)` predicate and may require
issuer, source, profile version, observation time, or other finite attribution fields. The
configuration supplies any permitted trust anchors or finite interpretation parameters.

For an operand with no profile attribution requirement,
`admissibleFact(None, attribution, configuration) = true`. A referenced profile must define its
fact predicate and be supported by the configuration; otherwise snapshot use fails with `Invalid`.
The configuration likewise supplies one explicit `admissibleEvidence(Evidence, configuration)`
rule; `AllowAllEvidence` is a valid declared rule, not an implicit default.

The admissibility rules are evaluated only over the supplied snapshot, profile declarations, and
evaluation configuration. They perform no network access, credential refresh, or opaque callback.
Missing or unaccepted required attribution on a relevant fact or evidence item is `Invalid`; the evaluator
must not silently fall back to another candidate. Credential verification and construction of the
attribution fields occur before `Eval`.

### 4.5 Closed-world boundary

The snapshot is complete only for the facts and evidence the caller chose to supply. Absence does
not assert the logical negation of a fact. Fact absence is `Missing` and becomes `Unknown` when a
condition depends on it. Absence of qualifying performance evidence means that a Duty or Promise
has not been shown fulfilled; the status rules determine whether it remains Pending or Active, or
becomes Violated.

## 5. Evaluation Configuration

`EvaluationConfiguration` contains choices that may legitimately vary between conforming
deployments and therefore must be explicit inputs, including:

- the conflict-resolution strategy;
- the default decision (`defaultDecision : Permit | Deny | NotApplicable`, default `NotApplicable`),
  substituted for a resolved `NotApplicable` outcome only — never for `Indeterminate`;
- the supported profile identifiers and versions;
- one total finite evidence-admissibility rule, which may explicitly be `AllowAllEvidence`;
- declared conformance bounds, including maximum policy-universe size, condition/path depth,
  collection size, fact count, and evidence count;
- profile-defined interpretation parameters, where the profile permits them.

A policy must not silently select an evaluator-wide conflict strategy. Unsupported or conflicting
configuration produces a specified diagnostic.

```text
Strategy ::= ProhibitOverrides
           | PermitOverrides
           | Invalid

validateConfiguration(U, C) : finite set of EvalError =
    { Invalid(ConfigurationSite(field)) |
        field contains an unsupported Strategy,
        a profile/version required by a policy in U but unsupported by C,
        a profile required by U without a total fact-admissibility predicate,
        an absent or non-total evidence-admissibility rule,
        a self-reference or cycle in the finite targetNorm status-dependency graph,
        or an absent/non-positive conformance bound }
```

The set is empty exactly when configuration is valid. There is no default strategy — unlike
`strategy`, `defaultDecision` does have a stated default (`NotApplicable`), matching current
behavior for deployments that do not set it explicitly. Configuration validation happens before
policy derivation and uses canonical `Invalid(ConfigurationSite(field))` diagnostics.

## 6. Evaluation Result

An `EvaluationResult` is an immutable semantic value:

```text
EvaluationResult = (
    decision           : Decision,
    normativeEnvelope : finite set of AttributedNormativeAtom,
    dutyStatuses       : finite map Duty -> StatusResult<DutyStatus>,
    promiseStatuses    : finite map Promise -> StatusResult<PromiseStatus>,
    diagnostics        : finite set of EvalError
)
```

The current decision domain is:

```text
Decision ::= Permit
           | Deny
           | NotApplicable
           | Indeterminate
```

`normativeEnvelope` is the complete policy- and clause-attributed input to resolution, including
definite and indeterminate atoms. It is intentionally not claimed to be a minimal proof set.
The two status maps expose the declarative results for Duties and Promises in the supplied policy
universe: `dutyStatuses` covers every independent or attached Duty reachable from any supplied
policy, including an Offer, and `promiseStatuses` covers every Promise clause. A status reported
for an Offer is descriptive only; it does not make the Offer or any of its clauses operative. A
Duty status participates in access derivation only through a `prerequisiteDuty` relation — declared
on an owning Privilege or on its owning Policy; a Duty that is a Policy clause only, and never the
object of `prerequisiteDuty`, never changes the access decision. `diagnostics`
uses the causal error algebra defined by the Semantics. Explanatory labels, localized
messages, traces, timestamps, signatures, and persistence identifiers are optional interchange or
implementation metadata unless a profile gives them policy meaning.

If input validation finds invalid configuration, conflicting snapshot-identifier reuse, an
invalid interval, a non-canonical path or value, or a violated snapshot bound, `Eval` returns
`Indeterminate`, an empty normative envelope, empty status maps, and the corresponding `Invalid`
diagnostics. It does not partially evaluate policies against invalid inputs.

## 7. Duty and Promise Status

Duty fulfillment and violation are language semantics. They are pure derivations from canonical
policy content and the immutable snapshot; they are not transitions in stored evaluator state.

```text
DutyStatus    ::= Pending | Active | Fulfilled | Violated
PromiseStatus ::= Pending | Fulfilled | Violated

StatusResult<S> ::= Known(S) | IndeterminateStatus(finite non-empty set of EvalError)

dutyStatus(PolicyUniverse, Duty, WorldSnapshot, EvaluationConfiguration)
    -> StatusResult<DutyStatus>

promiseStatus(PolicyUniverse, Promise, WorldSnapshot, EvaluationConfiguration)
    -> StatusResult<PromiseStatus>
```

`IndeterminateStatus` is not a fifth Duty or Promise state and has no corresponding ontology
individual. It records that the semantic input does not determine one state. Policy RDF does not
assert status; an implementation may cache a derived result only when doing so preserves the
observable result for the complete evaluation input.

### 7.1 Canonical Duty forms

A Duty node denotes one obligation occurrence and has exactly one of two body forms:

```text
Duty(subject, counterparty?, object, condition?, dutyWindow?, body)
DutyBody ::= Achieve(action, postCondition?) | Maintain(invariant)
```

`condition` is always an applicability guard. It is never reused as satisfaction content or as a
deadline. Before the guard is true, the Duty is `Pending`; unknown guard data makes its status
indeterminate. An `Achieve` body is satisfied by qualifying evidence that its `action` occurred;
when `postCondition` is present, that condition must also hold at the witness occurrence time. A
`Maintain` body has no action: its `invariant` must hold throughout the elapsed part of the Duty's
window. Without a window it is an ongoing requirement assessed at the current snapshot. The body
form determines the interpretation; canonical RDF has no separate mode field — `rl2:action` and
`rl2:invariant` project one-to-one to `Achieve` and `Maintain`.

A `DutyWindow` is one finite half-open interval:

```text
DutyWindow = [startInclusive, endExclusive)
```

At the start instant the Duty becomes eligible for assessment when its applicability guard holds.
Evidence at the end instant is outside the window, and at that instant the window is closed. A Duty with no window is unbounded: an Achievement Duty can
be fulfilled but does not become violated merely because time passes; a Maintenance Duty is an
ongoing snapshot requirement that can be active or violated but cannot be declared fulfilled.

There is no implicit reset or recurrence. A later period or repeated access requires another
canonical Duty occurrence.

### 7.2 Duty ownership and access interaction

A Duty has one or both of two structural roles, and both may hold at once:

- **prerequisite** — it is the object of one or more Privileges' `rl2:prerequisiteDuty`, or of a
  Policy's `rl2:prerequisiteDuty` (gating every Privilege clause of that Policy); or
- **independent** — it is a Policy clause.

A Duty that is both a Policy clause and a prerequisite is a standing obligation that also gates
access: it contributes its own `obligate` atom as an independent clause, and independently gates
every Privilege that references it (directly, or through its owning Policy). These are two effects
of one Duty occurrence; the Duty still has exactly one derived status, read once and reported once
(§7.1). A Duty referenced only via `prerequisiteDuty` (never a Policy clause) gates without
contributing an independent obligation atom of its own.

Multiple prerequisites — on one Privilege, on one Policy, or on both at once — are conjunctive. For
each prerequisite, a false applicability `condition` means that the Duty is `Pending` and not
required for this evaluation. When applicable,
only `Known(Fulfilled)` satisfies the prerequisite. `Known(Pending)`, `Known(Active)`, and
`Known(Violated)` prevent that Privilege from contributing a permit; an outcome-sensitive
`IndeterminateStatus` makes the Privilege indeterminate. These effects are local to the owning
Privilege(s) — for a Policy-level prerequisite, every Privilege clause of that Policy. They do not
create a global Deny and do not affect a different Privilege that can grant the same request.

One prerequisite Duty may be shared by several Privileges, whether referenced individually or
through a shared owning Policy. It still denotes one Duty occurrence: the same derived status is
read by every owner, so one qualifying fulfillment can satisfy all of them. This is distinct from
separate Duty nodes, which denote separate occurrences even when their content is otherwise equal.

An independent Duty that is not also a prerequisite contributes normative and status information
but never changes an access decision. Core has no concurrent or post-use attachment mode and no
`PermitWithObligations` decision. Applications may use the returned decision and Duty information
for enforcement or
scheduling without changing core semantics.

### 7.3 Status meaning

- Before a declared window starts, or while its applicability condition is false, either Duty
  form is `Pending`.
- An Achievement Duty is `Fulfilled` when at least one qualifying action witness occurs within
  its window and satisfies its optional postcondition. If no such witness exists, it is
  `Violated` when a finite window closes and otherwise `Active`.
- A Maintenance Duty is `Violated` when its invariant is conclusively false at any instant in the
  elapsed window. It is `Fulfilled` only after a finite window closes and the snapshot provides
  complete coverage establishing that the invariant held throughout. Without a window, it is
  `Active` when the invariant is true at the current snapshot and `Violated` when false.
- An unknown applicability condition yields `IndeterminateStatus`. A missing, invalid,
  inadmissible, ill-typed, or conflicting value that can change the content status
  yields `IndeterminateStatus` with its causal errors. Missing qualifying action evidence alone
  means “not yet fulfilled,” not an error.

Promise status follows the proposed Duty's body. A promised action is fulfilled by qualifying
action evidence and otherwise remains pending, since a Promise's own `dutyWindow` (if authored) is
carried to the materialized Duty and is not consulted pre-acceptance. A promised state is assessed
from its condition at the evaluation snapshot. Acceptance may crystallize a Promise into a bounded
Duty; that pure transformation is specified in the next section. Promise status is re-derived for
every snapshot, never yields `Active`, and is not a persistent terminal state. Only a crystallized
Maintenance Duty with a finite window can represent a completed maintenance period.

## 8. Policy Transformation

Offer acceptance is the pure transformation:

```text
materialize(Offer, Acceptance) -> MaterializationResult
```

An Offer is not an operative access policy: its clauses contribute no atoms to `Out` before
acceptance. Status functions still report its Promise and reachable Duty statuses for inspection;
those descriptive values do not activate the proposed terms. Normative access and Duty effects
begin only after a successful transformation has produced an Agreement supplied to `Eval`.

`Acceptance` supplies the Agreement identifier, grantor and grantee, an injective output-identifier
allocation for every source Promise and policy-local Norm (including attached Duties), optional
missing Promise-object bindings, and optional per-Promise Duty windows.
Identity allocation is explicit input: `materialize` never calls an unspecified fresh-name
operation. `MaterializationResult` is either one complete Agreement plus its source-clause map or
a non-empty canonical set of attributed errors; no partial Agreement is returned.

A Promise is structurally a proposed Duty, so crystallization is an unwrap-and-rebind: the
generated Duty reuses the proposed Duty's subject, condition, and body directly, with the Promise's
required counterparty (the promisee) retained as the Duty's counterparty and the object bound from
the Promise's authored value or, when absent, from the Acceptance's object binding. No separate
Claim node is generated.

All policy-local Norms receive Agreement-local identifiers while retaining top-level or attached
placement. Policy-local Norms are exactly top-level Norm clauses plus prerequisite Duties attached
to top-level Privileges; other Norm-valued properties are references rather than ownership.
References to local terms are rewritten through the source map; external Norm references are
unchanged. A Promise-valued target must name a sibling Promise clause in the same Offer. Its
`obligationStateOperand` query is unchanged by materialization; only the `targetNorm` rebinds from
the Promise to its crystallized Duty. A supplied Duty window must be a valid finite half-open
interval.

An Offer-level `condition` is the proposed Agreement applicability guard, not an offer-validity or
acceptance-authorization test. The output copies that condition and semantic metadata and records
`prov:wasDerivedFrom` provenance.

The transformation reads no `WorldSnapshot`, emits no effect, and prescribes no acceptance
message, persistence, or workflow. The full validation and rewriting algorithm is normative in
`RL2_Semantics.md` §Pure Offer Acceptance.

## 9. ODRL Input

ODRL 2.2 is an accepted source language only through the translation rules in
`RL2_ODRL_Mapping.md`. Translation yields canonical RL2 or a specified diagnostic. Structural
acceptance alone does not establish behavioral preservation.

## 10. Conformance

Core conformance requires:

1. RDF and SHACL conformance for native RL2 input.
2. Correct canonical projection.
3. Evaluation results matching the normative semantic vectors.
4. Correct diagnostics for invalid, unsupported, ambiguous, or indeterminate input.
5. Correct ODRL translation for every claimed migration class.

Wire formats, storage models, evaluator architecture, and enforcement are outside core
conformance.
