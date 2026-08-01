# RL2 Information Model

**RL2 version:** 0.7 · **Status:** Draft proposal for review · **Date:** 2026-08-01

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
    requestedAsset  : Asset,
    parameters      : finite map Name -> Value,
    id              : (IRI | String)?
)
```

`requestingAgent` and `requestedAsset` name a concrete Agent and Asset; the sentinel individuals
`rl2:anyAgent` and `rl2:anyAsset` (used only in norm `rl2:subject`/`rl2:object` to declare an
attribute-defined population; see `RL2_Semantics.md` §Request Matching) are never valid values
here. A Request naming a sentinel is invalid and rejected before evaluation.

`id` is an OPTIONAL caller-supplied stable identifier for this request/decision — an IRI or a
string, at the caller's discretion. Identifier allocation is explicit caller input, exactly like
`materialize`'s `Acceptance`-supplied identifiers (§8): `Eval` never mints a fresh identifier of
its own. `id` has no meaning to matching, conditions, or resolution; its sole normative role is as
the per-grant occurrence-identity input to `occurrenceOf` (`RL2_Semantics.md` §Duty Template
Binding). A Request omitting `id` is ordinary and fully valid — the fallback per-member occurrence
identity (§7.2) applies.

`parameters` carries request-specific input that the requester itself supplies — a record count,
a target format, a stated purpose — resolved through `request.parameters.<name>` (see
`RL2_Semantics.md` §`deref`). It is a finite typed map using the same `Value` universe as every
other operand; it is immutable input to `Eval`, so purity is unaffected. It is distinct from
`context.*`/`global.*` snapshot facts, which the assembler supplies rather than the requester, and
from `agent.*`/`asset.*` facts, which describe the agent or asset rather than this request.

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
    id           : IRI,
    occurredAt   : Time,
    actor        : Agent,
    action       : Action,
    object       : Resource,
    attribution  : Attribution,
    dischargeOf  : (IRI, IRI | String)?
)
```

An `AttributedFact` binds one canonical path, in one explicit scope, to a typed value. `Evidence`
records an observed action used by Duty and Promise status functions. `id` identifies an
assertion or evidence item, not the real-world entity described by it. `Attribution.observedAt`
is the assembler-recorded assertion time (distinct from `validDuring`, which bounds applicability,
not observation); a profile may expose it as an ordinary resolvable operand for a freshness check
(see `RL2_ExternalData.md` §5). `dischargeOf` is optional and, when present, names the PER-GRANT
`occurrenceId` — `(sourceIdentity, Request.id)`, the identifier `occurrenceOf` assigns at grant
time (§7.2) — of the specific bound occurrence this evidence claims to discharge. Only PER-GRANT
occurrences are discharge-correlated: PER-MEMBER occurrences, gated bound prerequisites, and
authored concrete Duties all use ordinary evidence selection, so an assembler that cannot
correlate evidence to a specific grant leaves the field absent, and absence never disqualifies
evidence from any Duty without a PER-GRANT occurrence to discharge (§4.3).

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

The core `request.*` paths are `request.requestingAgent`, `request.requestedAction`,
`request.requestedAsset`, and `request.parameters.<name>`. The first three resolve directly from
the matching Request field. `request.parameters.<name>` resolves directly from `Request.parameters`:
present under `name` yields `Ok(value)`; absent yields `Missing({site: Path(path), target: None})`.
Both cases attribute the value to the Request itself, not to a snapshot fact — there is no
`AttributedFact` or `validDuring` interval for a Request parameter, since it is not part of
`WorldSnapshot`. Other request metadata uses a declared `context.*` fact or a separate interchange
profile; no other `request.*` field is a canonical core path.

For a required key `k`, expected value type `τ` (`declaredType(op)`, read from the operand's
`rl2:valueType`), profile `p`, snapshot `W`, and configuration `C`:

```text
resolveFact(k, τ, p, W, C) =
    let candidates = {
        f in W.facts |
        f.key = k and contains(f.validDuring, W.evaluationTime)
        and admitsFact(k, f, C)
    }
    in if candidates = empty then Err(Missing({ site: SnapshotSite(k.path), target: None }))
       else if any f.value is not of type τ
            then Err(Invalid({ site: SnapshotSite(k.path), target: None }))
       else let values = distinctSemanticValues(candidates)
            in if |values| = 1 then Ok(the element of values)
               else Err(Conflict({ site: SnapshotSite(k.path), target: None }))
```

`admitsFact` is the finite admissibility filter defined in §4.4; a candidate that fails it is
excluded before the empty/type/conflict rules run, so a key for which every candidate fails the
filter is `Missing` exactly like a key with no candidates at all — never a separate error kind.
The profile `p` no longer participates in this filter (§4.4); it is retained in the signature for
`τ`/`declaredType(op)` context and for the deferred per-operand data contract (`backlog.md` §6).

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
selectEvidence(d, selector, W, C) =
    let raw = {
        e in W.evidence |
        actorActionObjectTimeMatch(e, selector, W.evaluationTime)
        and admitsEvidence(d, e, C)
    }
    in Ok(raw)
```

Core Duty and Promise selectors use the subject, the required action plus its finite set of
included actions, the object, and the applicable temporal interval. These values come from the
clause; they are not implicitly copied from the current Request. `d` is the Duty (or, for a
Promise, its proposed Duty, `RL2_Semantics.md` §Denotational Semantics for Norms) whose evidence is
being selected — carried alongside `selector` because `admitsEvidence`'s key is the Duty's own
identity, not the selector's shape (below). `admitsEvidence` is the evidence-side admissibility
filter defined in §4.4, over the `evidenceSigners` entry (if any) for `d`. An evidence item that
fails the filter is excluded from `raw`
exactly as if it had never matched; `selectEvidence` is therefore total. No matching evidence —
whether because none was ever asserted or because every match was filtered out — is `Ok(empty)`,
meaning performance has not been established, never a distinct error.

**Per-grant discharge correlation.** When the Duty being evaluated is a PER-GRANT bound occurrence
(§7.2 — its `occurrenceId` is `(sourceIdentity, Request.id)`, because the originating Request
carried an `id`), an evidence item matching `actorActionObjectTimeMatch` additionally discharges it
only when `e.dischargeOf` equals that same `occurrenceId`; uncorrelated evidence — `dischargeOf`
absent or naming a different occurrence — matches the selector's actor/action/object/time shape
but does not discharge this specific grant, so it is excluded from `achievementCandidates` for that
occurrence's status even though it may remain visible for another query. A PER-MEMBER bound
occurrence and an authored concrete Duty (one with no `occurrenceId` at all) are unaffected by
`dischargeOf`: matching is `actorActionObjectTimeMatch` and `admitsEvidence` alone, exactly as
before this field existed.

### 4.4 Admissibility and trust

**Trust verification is pre-`Eval` (normative).** Signature checking, provenance-chain validation,
trust-anchor evaluation, and connector authentication happen in the trusted assembler, before
`WorldSnapshot` exists. `WorldSnapshot` contains only already-admitted facts and evidence; each item
carries its attribution metadata (`source`, `observedAt`, `issuer` — the `Attribution` fields
defined in §4) as ordinary immutable fields. `Eval` never performs cryptographic or chain-of-trust
verification of its own; `admitsFact`/`admitsEvidence` below only compare attribution fields already
present on the snapshot against the finite record `C` supplies.

**The admissibility record.** What `EvaluationConfiguration` carries for admissibility is not a
predicate a profile authors. It is a finite declarative record, `Admissibility`, with exactly three
optional per-scope constraint kinds. This set is closed — a profile may not extend it — which is
what makes two conforming evaluators byte-identical over equal configuration:

| Constraint | Keyed by | Present: a candidate fails when | Absent |
|---|---|---|---|
| `allowedSources` | a left-operand's resolution path (`FactKey.path`) | `attribution.source` is outside the declared finite set of source IRIs, or absent | unrestricted — every source admitted |
| `maxAge` | a left-operand's resolution path | `attribution.observedAt` is older than `evaluationTime - maxAge` (a `Duration`), or absent | unrestricted — no freshness bound |
| `evidenceSigners` | **the owning Duty's own stable identity** — `sourceIdentity(d)`, its compiled-module IRI/`SourceRef` (`RL2_Semantics.md` §Duty Template Binding) — not the clause's `EvidenceSelector` shape | `attribution.issuer` is outside the declared finite set of attestor/signer IRIs, or absent | unrestricted — every signer admitted |

A scope absent from the record is unrestricted, not an error — there is no more "a profile required
to declare a fact-admissibility predicate" obligation; admissibility is configuration-only data.
Keying `evidenceSigners` by `sourceIdentity(d)` rather than by selector shape means a bound
occurrence — whether a per-grant or per-member `occurrenceId`, or a `BoundIdentity` from
prerequisite gating (§7.2) — inherits its originating template's entry unchanged: binding varies the
agent, asset, and (for `occurrenceOf`) the window and identity, but never the Duty's own
`sourceIdentity`, so one authored `evidenceSigners` entry governs every occurrence of that Duty
regardless of who requested it.
`Admissibility` has a canonical JSON representation using the same conventions as the §5.1 canonical
serialization (sorted keys). It is carried inside `EvaluationConfiguration` and therefore covered by
the configuration echo/digest in `EvaluationResult` (`RL2_Compilation.md` §7): two evaluators given
byte-equal configuration apply byte-equal admissibility.

```text
admitsFact(k, f, C)       = (k not in dom(C.admissibility.allowedSources)
                                 or (f.attribution.source is present
                                     and f.attribution.source in C.admissibility.allowedSources(k)))
                            and (k not in dom(C.admissibility.maxAge)
                                 or (f.attribution.observedAt is present
                                     and f.attribution.observedAt >= W.evaluationTime - C.admissibility.maxAge(k)))

admitsEvidence(d, e, C)   = sourceIdentity(d) not in dom(C.admissibility.evidenceSigners)
                                 or (e.attribution.issuer is present
                                     and e.attribution.issuer in C.admissibility.evidenceSigners(sourceIdentity(d)))
```

**Absent-attribution rule.** When a constraint is configured for a key or Duty but the specific
candidate's corresponding attribution field is itself absent — no `source`, no `observedAt`, or no
`issuer` — the candidate fails that filter; an absent field is never treated as vacuously
admissible in either direction: a configured constraint with an absent field always fails
(conservative), and an unconfigured scope never inspects the field at all, present or absent
(deterministic — `admitsFact`/`admitsEvidence` are total, pure functions of `C` and the candidate's
own fields).

**Filter semantics.** An item failing the filter is treated by resolution exactly as if absent —
never a silent fallback to another candidate and never a distinct error kind. `resolveFact` (§4.2)
filters `candidates` by `admitsFact` before the empty/type/conflict rules run: a key for which every
candidate fails the filter is `Missing`, the ordinary attributed error for that operand, exactly like
a key with no candidates at all. `selectEvidence` (§4.3) filters `raw` by `admitsEvidence` the same
way: evidence filtered to empty is `Ok(empty)`, the same "not yet established" outcome as a selector
that matched nothing. This keeps the filter inside the existing three-valued discipline, but the
visibility claim needs to be read precisely, not as a blanket "always visible in causes":
a fact candidate filtered by `allowedSources`/`maxAge` surfaces as an ordinary attributed `Missing`
cause, because `resolveFact` has an empty-candidates branch that already produces one. Evidence
filtered by `evidenceSigners` has no analogous branch: `selectEvidence` filtering `raw` to empty is
`Ok(empty)`, a definite status (typically `Pending`, or `Known(Fulfilled)` failing to hold) with
**no distinct cause of its own** — indistinguishable, from inside one evaluation, from no evidence
having been asserted at all. An `evidenceSigners` entry that is simply too narrow (excluding a
signer that should have been trusted) is therefore visible only by comparing two evaluations'
`Admissibility` configuration digests (`RL2_Compilation.md` §7) side by side, never by inspecting
one evaluation's `diagnostics` or causes.

**Threat model (normative).** `WorldSnapshot` is the output of a single trusted assembler — the
component, external to `Eval`, that gathers facts and evidence from underlying sources, performs the
verification of the paragraph above, and constructs `W` before evaluation runs. `admitsFact` and
`admitsEvidence` apply only the finite, configuration-declared filter above; they do not perform
source-level trust arbitration or credential verification of their own. A deployment that must
combine facts from sources of differing trust levels performs that combination — or excludes, per
key, facts from sources the deployment does not trust for that key — in the assembler, before `Eval`
sees the snapshot, not by relying on `resolveFact`/`selectEvidence` to arbitrate between trusted and
untrusted candidates for the same key or scope at evaluation time.

**Deferred.** The full per-operand data contract (value schema, cardinality, owner, provenance
fields beyond `Attribution`, freshness semantics beyond `maxAge`, a trust-policy digest, and
completeness scope) and a normative `RequiredInputs` companion are out of scope here; this section
fixes only the admissibility record's shape and filter semantics (`backlog.md` §6).

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
- the finite `Admissibility` record (§4.4): `allowedSources` and `maxAge` per left-operand
  resolution path, and `evidenceSigners` per Duty-evidence scope, each optional and unrestricted
  when absent;
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
        a scope key in `C.admissibility` naming a constraint kind outside the closed
            `allowedSources`/`maxAge`/`evidenceSigners` set (§4.4),
        a self-reference or cycle in the finite targetNorm status-dependency graph,
        or an absent/non-positive conformance bound }
```

There is no longer a "profile declares a fact-admissibility predicate" or "absent/non-total
evidence-admissibility rule" diagnostic: admissibility is optional, per-scope, configuration-only
data (§4.4), and an absent scope is unrestricted, not a validation failure.

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
    dutyStatuses       : finite map (Duty | OccurrenceId | BoundIdentity) -> StatusResult<DutyStatus>,
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
universe. `dutyStatuses` has two disjoint kinds of entry, by construction never colliding: a
**concrete-Duty entry**, keyed by Duty identity, covers every concrete (sentinel-free) Duty
reachable from any supplied policy, including an Offer — a template contributes no entry under its
own identity, since `dutyStatus` is never applied to one (§7.2); and a **bound-occurrence entry**,
present only when this evaluation's Request actually produced one, keyed by the `occurrenceId`
`occurrenceOf` assigned at a consequent-duty or independent-clause site, or by the `(sourceIdentity,
agent, asset)` `BoundIdentity` a template resolved to at a prerequisite-gating site (§7.2,
`RL2_Semantics.md`'s `boundOccurrenceStatuses`). A bound-occurrence entry lets a later query
re-identify that occurrence's status from the recorded key without re-deriving the binding.
`promiseStatuses` covers every Promise clause. A status reported for an Offer is descriptive only;
it does not make the Offer or any of its clauses operative. A Duty status participates in access
derivation only through a `prerequisiteDuty` relation — declared on an owning Privilege or on its
owning Policy; a Duty that is a Policy clause only, and never the object of `prerequisiteDuty`,
never changes the access decision. Every Duty named by an `obligate` atom in `normativeEnvelope` —
whether from an independent clause or from a firing `consequentDuty` (§7.2) — is a concrete,
sentinel-free occurrence: a sentinel-carrying Duty template is bound to the request's agent and
asset before it is ever placed in the envelope (`RL2_Semantics.md` §Duty Template Binding).
`diagnostics`
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

A `DutyWindow` is one finite half-open interval, and each endpoint is independently `Absolute` (a
literal instant) or `Relative` (an anchor operand plus a duration offset):

```text
WindowEndpoint ::= Absolute(Time) | Relative(LeftOperand, Duration)
DutyWindow = [start: WindowEndpoint, end: WindowEndpoint)
```

`Absolute` is the literal form (`rl2:startInclusive`/`rl2:endExclusive`). `Relative` (
`rl2:startRelativeTo`+`rl2:startOffset` / `rl2:endRelativeTo`+`rl2:endOffset`) names an anchor fact
plus an offset — e.g. "two weeks after receipt" as an anchor of `receivedAt` and an offset of
`P14D` — resolved once per evaluation via the same fact-resolution discipline as any other
operand (`RL2_Semantics.md`, `resolveWindow`). A missing or non-`DateTime` anchor, or a resolved
interval that is not `start < end`, leaves the window unresolved and the Duty's or Promise's
status is `IndeterminateStatus`. This removes the need to precompute an absolute expiry into a
snapshot fact purely to express a relative deadline; both styles remain valid.

At the start instant the Duty becomes eligible for assessment when its applicability guard holds.
Evidence at the end instant is outside the window, and at that instant the window is closed. A Duty with no window is unbounded: an Achievement Duty can
be fulfilled but does not become violated merely because time passes; a Maintenance Duty is an
ongoing snapshot requirement that can be active or violated but cannot be declared fulfilled.

There is no implicit reset or recurrence. A later period or repeated access requires another
canonical Duty occurrence. A `DutyWindow` denotes exactly one such occurrence; recurring
commitments (e.g. a weekly delivery) are out of scope for 0.7 — the deployment pattern is a
snapshot assembler that instantiates the current period's window, or a profile-defined operand
that carries the schedule. A fixed period-and-count form, expanded at compile time into finitely
many `DutyWindow` occurrences, is the candidate future extension.

### 7.2 Duty ownership and access interaction

A Duty has one or more of three structural roles, and any combination may hold at once:

- **prerequisite** — it is the object of one or more Privileges' `rl2:prerequisiteDuty`, or of a
  Policy's `rl2:prerequisiteDuty` (gating every Privilege clause of that Policy);
- **independent** — it is a Policy clause; or
- **consequent** — it is the object of a Privilege's `rl2:consequentDuty`: it fires alongside that
  Privilege's grant (contributing its `obligate` atom to the envelope) but never gates it, the
  post-use or companion counterpart to a prerequisite. Unlike `prerequisiteDuty`, `consequentDuty`
  is declared only on a Privilege, never folded in from an owning Policy.

A Duty's `rl2:subject` or `rl2:object` may be the sentinel `rl2:anyAgent` / `rl2:anyAsset` (§3);
such a Duty is a **template** naming an attribute-defined population, not a concrete occurrence,
and has no standalone status of its own; it never receives an entry in `dutyStatuses` as itself
(§6). In every request-context place a template Duty is consulted or emitted, it is first bound to
the request's concrete agent and asset (`RL2_Semantics.md` §Duty Template Binding), by one of two
mechanisms depending on the site:

- **prerequisite gating and attached-duty reporting** use unchanged, pure substitution —
  `bind(d,agent,asset)` — with no request-scoped transformation; a `request.*` path read in these
  request-free contexts yields an attributed `Missing`, not a value.
- **consequent-duty firing and independent-clause atom emission** use `occurrenceOf(d, Env)`,
  which additionally (a) consumes the Duty's `condition` — evaluated once, in the request
  environment, and dropped from the emitted occurrence; (b) resolves `window` to an `Absolute`
  window or `None` at grant time via `resolveWindow`, never an unresolved `Relative` window (a
  `resolveWindow` failure yields an indeterminate atom carrying that failure's causes instead of an
  occurrence); and (c) assigns an `occurrenceId` — `(sourceIdentity(d), Request.id)` when the
  request carries an `id` (PER-GRANT), else `(sourceIdentity(d), agent, asset)` (PER-MEMBER
  fallback, coalescing repeated grants by the same agent/asset pair).

No sentinel ever appears in an emitted `obligate` atom or in a `dutyStatus` query. A **bound
occurrence** produced by either mechanism, once recorded in an `EvaluationResult`, is an ordinary
concrete Duty value and may be status-evaluated again against a later snapshot; an occurrence
produced by `occurrenceOf` is additionally re-identifiable by its recorded `occurrenceId`
(`RL2_Semantics.md`'s `boundOccurrenceStatuses`, §6 below).

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
but never changes an access decision; the same is true of a consequent Duty, whose firing follows
its Privilege's grant and cannot feed back into it. Core has no concurrent attachment mode and no
`PermitWithObligations` decision — a genuinely ongoing requirement is a Maintenance Duty with an
optional window, not a distinct attachment mode. `consequentDuty` is core's one-shot post-use
attachment mode (attribution, logging, and similar companion duties triggered by a grant).
Applications may use the returned decision and Duty information for enforcement or
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
- An unknown applicability condition yields `IndeterminateStatus`. A missing, invalid, ill-typed,
  or conflicting value that can change the content status yields `IndeterminateStatus` with its
  causal errors — an admissibility-filtered value (§4.4) surfaces here as `Missing`, not as a
  distinct kind. Missing qualifying action evidence alone means "not yet fulfilled," not an error.

Promise status follows the proposed Duty's body. A promised action is fulfilled by qualifying
action evidence and otherwise remains pending, since a Promise's own `dutyWindow` (if authored) is
carried to the materialized Duty and is not consulted pre-acceptance; an action-form Promise's
optional `postCondition` is likewise not consulted pre-acceptance, for the same reason. A promised
state is assessed from its condition at the evaluation snapshot. Acceptance may crystallize a
Promise into a bounded Duty; that pure transformation is specified in the next section. Promise
status is re-derived for every snapshot, never yields `Active`, and is not a persistent terminal
state. Only a crystallized Maintenance Duty with a finite window can represent a completed
maintenance period.

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
the Promise's authored value or, when absent, from the Acceptance's object binding. Because the
body is reused directly, an action-form Promise's optional `postCondition` (the `Achieve` body's
optional slot) is carried into the crystallized Achievement Duty's body unevaluated, exactly like
`condition` and `dutyWindow`, and is assessed thereafter only by that Duty's status derivation; a
state-form Promise has no such slot and crystallizes to a Maintenance Duty without one. No separate
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
