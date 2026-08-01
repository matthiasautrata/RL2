# RL2 Information Model

## Status

This document is the SCOPE-2 normative information-model scaffold. Detailed denotations and
algorithms are defined in `RL2_Semantics.md`. Sections marked **Open** identify semantic decisions
that must be closed before publication; they are not delegated to implementations.

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
    kind        : EventKind,
    occurredAt  : Time,
    actor       : Agent?,
    action      : Action?,
    object      : Resource?,
    payload     : finite map of canonical field name -> Value,
    attribution : Attribution
)
```

An `AttributedFact` binds one canonical path, in one explicit scope, to a typed value. `Evidence`
records an occurrence or observation used by event conditions and, through the status functions,
by Duties and Promises. `id` identifies an assertion or evidence item, not the real-world entity
described by it.

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

Arrival order, RDF statement order, Case membership, database version, and storage sequence are
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

`state.Clock` denotes `evaluationTime`, and `state.Events...` denotes an evidence query; neither
is an `AttributedFact`. A profile may define other `state`, `context`, or `global` paths, but every
such path still resolves through the fact algorithm below.

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
    in if candidates = empty then Err(Missing(k))
       else if any f in candidates is not admissible(p, f.attribution, C)
            then Err(Invalid(k))
       else if any f.value is not of type τ
            then Err(Invalid(k))
       else let values = distinctSemanticValues(candidates)
            in if |values| = 1 then Ok(the element of values)
               else Err(Conflict(k))
```

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
    kinds       : finite non-empty set of EventKind,
    actor       : Agent?,
    action      : Action?,
    object      : Resource?,
    during      : Interval?,
    payloadTest : finite map of field name -> ValuePattern,
    profile     : Profile?
)
```

Selector construction expands each requested kind to the finite set of included kinds using the
canonical PolicyUniverse. An evidence item matches when its kind belongs to that expanded set,
every present actor/action/object field equals the selector field, its occurrence is no later than
`evaluationTime` and within `during` when supplied, its payload passes every declared pattern,
and its attribution is admissible. Selector fields are conjunctive. There is no ambient Case
scope.

The query functions make the error boundary explicit:

```text
selectEvidence(selector, W, C) =
    let raw = {
        e in W.evidence |
        kindScopeTimeAndPayloadMatch(e, selector, W.evaluationTime)
    }
    in if any e in raw is not admissible(selector.profile, e.attribution, C)
       then Err(Invalid(selector))
       else Ok(raw)

existsEvidence(selector, W, C) =
    case selectEvidence(selector, W, C) of
        Err(e)  -> Err(e)
        Ok(es)  -> Ok(es != empty)

projectLatestEvidence(selector, field, expectedType, W, C) =
    case selectEvidence(selector, W, C) of
        Err(e) -> Err(e)
        Ok(empty) -> Err(Missing(selector))
        Ok(es) ->
            let latest = { e in es | e.occurredAt = maxOccurredAt(es) }
            in if any e in latest lacks field or field has the wrong type
               then Err(Invalid(selector))
               else let values = distinct projected semantic values from latest
                    in if |values| = 1 then Ok(the element of values)
                       else Err(Conflict(selector))
```

Duty evidence selectors must include the Duty subject and object, and include its action when the
Duty has one. S2-C2 defines their temporal interval. Other constructs that require request or
asset isolation must put those bindings into the selector; an omitted field is intentionally
unconstrained, not implicitly copied from the current Request.

Existential event conditions use `existsEvidence` and are true when at least one matching item
exists. A path that projects a field from the most recent matching evidence uses the maximum
`occurredAt`. When several matching items share that time, equal projected values collapse to one
value; unequal projected values produce `Conflict`. Evidence identifiers never break a semantic
tie.

Missing a matching evidence item makes an existential event condition `False`. Missing a required
projected field, inadmissible attribution, or an ill-typed projected value yields `Invalid`; a tied
unequal projection yields `Conflict`. Each error becomes `Unknown` when a condition depends on it.

### 4.4 Profile provenance and trust

Core RL2 does not declare an issuer trustworthy merely because an assertion is present. A profile
may define a total `admissible(profile, attribution, configuration)` predicate and may require
issuer, source, profile version, observation time, or other finite attribution fields. The
configuration supplies any permitted trust anchors or finite interpretation parameters.

For an operand or evidence selector with no profile attribution requirement,
`admissible(None, attribution, configuration) = true`. A referenced profile must define its
predicate and be supported by the configuration; otherwise snapshot use fails with `Invalid`.

`admissible` is evaluated only over the supplied snapshot, profile declarations, and evaluation
configuration. It performs no network access, credential refresh, or opaque callback. Missing or
unaccepted required attribution on a relevant fact or evidence item is `Invalid`; the evaluator
must not silently fall back to another candidate. Credential verification and construction of the
attribution fields occur before `Eval`.

### 4.5 Closed-world boundary

The snapshot is complete only for the facts and evidence the caller chose to supply. Absence does
not assert the logical negation of a fact. Fact absence is `Missing` and becomes `Unknown` when a
condition depends on it. Event existence is the deliberate exception: within the finite supplied
evidence set and selector interval, no matching event means `False`. This is a scoped evaluation
rule, not an RDF closed-world entailment regime.

## 5. Evaluation Configuration

`EvaluationConfiguration` contains choices that may legitimately vary between conforming
deployments and therefore must be explicit inputs, including:

- the conflict-resolution strategy;
- the supported profile identifiers and versions;
- declared conformance bounds, including maximum policy-universe size, condition/path depth,
  collection size, fact count, evidence count, and evidence-payload size;
- profile-defined interpretation parameters, where the profile permits them.

A policy must not silently select an evaluator-wide conflict strategy. Unsupported or conflicting
configuration produces a specified diagnostic.

```text
Strategy ::= ProhibitOverrides
           | PermitOverrides
           | SpecificOverridesGeneral
           | Invalid

validateConfiguration(U, C) : finite set of EvalError =
    { Invalid(ConfigurationSite(field)) |
        field contains an unsupported Strategy,
        a profile/version required by a policy in U but unsupported by C,
        a profile required by U without a total admissibility predicate,
        a self-reference or cycle in the finite targetNorm status-dependency graph,
        or an absent/non-positive conformance bound }
```

The set is empty exactly when configuration is valid. There is no default strategy. Configuration
validation happens before policy derivation and uses canonical `Invalid(ConfigurationSite(field))`
diagnostics.

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
Duty status participates in access derivation only through an owning Privilege's
`prerequisiteDuty` relation; independent Duties never change the access decision. `diagnostics`
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
individual. It records that the semantic input does not determine one state. An implementation
may serialize or cache a `Known` status, provided the observable result remains equal to the
derived value; an asserted `rl2:obligationState` or `rl2:promiseState` is never authoritative input
to core `Eval`.

### 7.1 Canonical Duty forms

A Duty node denotes one obligation occurrence and has exactly one of two content forms:

```text
AchievementDuty(subject, action, object, condition?, postCondition?, dutyWindow?)
MaintenanceDuty(subject, invariant, object, condition?, dutyWindow?)
```

`condition` is always an applicability guard. It is never reused as satisfaction content or as a
deadline. An Achievement Duty is satisfied by qualifying evidence that its `action` occurred;
when `postCondition` is present, that condition must also hold at the witness occurrence time. A
Maintenance Duty has no action: its `invariant` must hold throughout the elapsed part of its
window. Without a window it is an ongoing requirement assessed at the current snapshot. The
content form determines the interpretation; canonical RDF has no separate mode field.

A `DutyWindow` is one finite half-open interval:

```text
DutyWindow = [startInclusive, endExclusive)
```

At the start instant the Duty is active. Evidence at the end instant is outside the window, and
at that instant the window is closed. A Duty with no window is unbounded: an Achievement Duty can
be fulfilled but does not become violated merely because time passes; a Maintenance Duty is an
ongoing snapshot requirement that can be active or violated but cannot be declared fulfilled.

There is no implicit reset or recurrence. A later period or repeated access requires another
canonical Duty occurrence.

### 7.2 Duty ownership and access interaction

A Duty has one of two structural roles:

- **prerequisite** — it is the object of one or more Privileges' `rl2:prerequisiteDuty` and is not
  also a Policy clause; or
- **independent** — it is a Policy clause and is not the object of `rl2:prerequisiteDuty`.

Multiple prerequisites on one Privilege are conjunctive. For each prerequisite, a false
applicability `condition` means that the Duty is not required for this evaluation. When applicable,
only `Known(Fulfilled)` satisfies the prerequisite. `Known(Pending)`, `Known(Active)`, and
`Known(Violated)` prevent that Privilege from contributing a permit; an outcome-sensitive
`IndeterminateStatus` makes the Privilege indeterminate. These effects are local to the owning
Privilege. They do not create a global Deny and do not affect a different Privilege that can grant
the same request.

One prerequisite Duty may be shared by several Privileges. It still denotes one Duty occurrence:
the same derived status is read by every owner, so one qualifying fulfillment can satisfy all of
them. This is distinct from separate Duty nodes, which denote separate occurrences even when
their content is otherwise equal.

An independent Duty contributes normative and status information but never changes an access
decision. Core has no concurrent or post-use attachment mode and no `PermitWithObligations`
decision. A companion protocol may turn `Permit` plus selected Duty results into requirements,
scheduling, or an enforcement-specific response without changing core semantics.

### 7.3 Status meaning

- Before a declared window starts, either Duty form is `Pending`.
- An Achievement Duty is `Fulfilled` when at least one qualifying action witness occurs within
  its window and satisfies its optional postcondition. If no such witness exists, it is
  `Violated` when a finite window closes and otherwise `Active`.
- A Maintenance Duty is `Violated` when its invariant is conclusively false at any instant in the
  elapsed window. It is `Fulfilled` only after a finite window closes and the snapshot provides
  complete coverage establishing that the invariant held throughout. Without a window, it is
  `Active` when the invariant is true at the current snapshot and `Violated` when false.
- A missing, invalid, inadmissible, ill-typed, or conflicting value that can change the status
  yields `IndeterminateStatus` with its causal errors. Missing qualifying action evidence alone
  means “not yet fulfilled,” not an error.

Promise status follows its content. A promised action is fulfilled by qualifying action evidence
and otherwise remains pending because a Promise has no `dutyWindow`. A promised state is assessed
from its condition at the evaluation snapshot; a promised Duty projects the referenced Duty's
status, mapping `Pending` and `Active` to Promise `Pending`. Acceptance may crystallize a Promise
into a bounded Duty; that pure transformation is specified separately by S2-C4. Promise status
is re-derived for every snapshot and is not a persistent terminal state. Only a crystallized
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

Promises of actions crystallize into Achievement Duties. Promises of states crystallize into
Maintenance Duties. Each generated Duty names the promisor as subject and promisee as
counterparty and receives one canonical correlative Claim in the opposite orientation. A general
`promisedDuty` suretyship cannot be represented by the current Duty algebra without inventing an
action or changing Maintenance semantics, so core materialization rejects it with
`UnsupportedPromiseContent`; the Promise itself retains snapshot-derived status semantics.

All policy-local Norms receive Agreement-local identifiers while retaining top-level or attached
placement. Policy-local Norms are exactly top-level Norm clauses plus prerequisite Duties attached
to top-level Privileges; other Norm-valued properties are references rather than ownership.
References to local terms are rewritten through the source map; external Norm references are
unchanged. A Promise-valued target must name a sibling Promise clause in the same Offer. A
Promise-state query is rewritten to the crystallized Duty's
status query; other Promise-valued queries are rejected because no Promise survives in an
Agreement. A supplied Duty window must be a valid finite half-open interval.

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

Wire formats, storage models, evaluator architecture, enforcement, and future Case workflows are
separate conformance claims.
