# RL2 Formal Semantics

**RL2 version:** 0.7 · **Status:** Draft proposal for review · **Date:** 2026-08-01

*Deterministic Policy Meaning over Requests and World Snapshots.* RL2 combines conduct norms,
promises, and constraint algebra in deterministic evaluation semantics over a canonical policy
universe, request, and immutable world snapshot.

## Introduction

Digital policy frameworks often lack formal normative foundations. ODRL 2.2 provides an expressive
information model and vocabulary but leaves important evaluator choices open, allowing independent
implementations to disagree about the result of the same policy.

RL2 (“Rights Language 2”) addresses these limitations with explicit conduct norms, typed
conditions, temporal Duty semantics, and evidence-derived status. RDF is the interchange
representation; evaluation is defined over the canonical abstract syntax produced during
ingestion.

This document defines the formal semantics. `RL2_Model.md` defines the evaluation interface;
`../docs/RL2_Architecture.md` provides an informative overview.

---

## Abstract Syntax

We define RL2’s abstract syntax using a typed algebraic grammar, enriched with commentary explaining intuition and use.

### Core Syntactic Categories

Let:

* **A** = set of agents
* **X** = set of actions
* **S** = set of assets
* **V** = set of values
* **T** = time domain
* **Env** = evaluation environment
* **W** = immutable WorldSnapshot
* **⊥** = an absent optional syntax field; missing evaluated data is represented by
  `Err(Missing(ErrorKey), note)` in the Result and Truth Algebra below

We define RL2 expressions as:

#### Norms

```
Norm ::=
    Privilege(Agent, Action, Asset, Condition,
              prerequisiteDuties: finite set of Duty,
              consequentDuties: finite set of Duty)
  | Duty(Agent subject, Agent? counterparty, Asset, Condition,
         dutyWindow: DutyWindow?, body: DutyBody)
  | Prohibition(Agent, Action, Asset, Condition)

DutyBody ::=
    Achieve(Action, postCondition: Condition?)
  | Maintain(invariant: Condition)
```

`Condition` on a `Duty` is the ordinary applicability guard. Duty satisfaction is structural and
determined by which `DutyBody` form is present: `Achieve` requires action evidence and may
additionally require a `postCondition`; `Maintain` requires its `invariant` throughout the Duty's
`dutyWindow` and admits no action. The canonical RDF projection maps `rl2:action` to `Achieve` and
`rl2:invariant` to `Maintain`; the two forms are mutually exclusive in canonical RDF, and no
separate mode field exists — `Duty.body` is the single formal locus of that structural dispatch.

`Privilege.prerequisiteDuties` is projected from zero or more `rl2:prerequisiteDuty` values
declared on the Privilege itself or on its owning Policy (§Policies). The set is conjunctive:
every applicable member must be Fulfilled before the Privilege can contribute a permit. An
attached Duty is referenced by one or more Privileges or Policies. It may also independently be a
top-level Policy clause — a Duty is not restricted to one structural role. Sharing one Duty node
shares its one status result across those owners. A Duty referenced only as a top-level clause
(never via `prerequisiteDuty`) is independent and never gates an access decision by itself.

When a Duty is both a top-level clause and a prerequisite, it contributes its independent
`obligate` atom (from being a clause) **and** gates its referencing Privilege(s) (from being a
prerequisite); these are two effects of one Duty occurrence, not two Duties. The Duty still has
exactly one derived status (§Duty Status Derivation), which is read once and reported once,
regardless of how many roles or owners consult it.

`Privilege.consequentDuties` is projected from zero or more `rl2:consequentDuty` values declared
on the Privilege itself (there is no Policy-level fold for `consequentDuty`, unlike
`prerequisiteDuties`). A consequent Duty fires alongside its Privilege: when the Privilege
matches the request and its `accessResult` is `True`, the referenced Duty's obligate atom is
emitted into the normative envelope (§Normative Derivation), bound to the request's concrete
agent and asset via `bind` (§Duty Template Binding below). Unlike a prerequisite Duty, a
consequent Duty never gates the decision — it is read-only with respect to `accessResult` and
contributes no `prerequisiteResult` term. `rl2:prerequisiteDuty` and `rl2:consequentDuty` are the
pre- and post-condition halves of the same authoring pattern: one gates the grant, the other rides
along with it.

```
WindowEndpoint ::= Absolute(DateTime) | Relative(LeftOperand, Duration)
DutyWindow = [start: WindowEndpoint, end: WindowEndpoint)
```

The window is finite when present. Absence means unbounded; it is not a second RDF spelling for an
interval with omitted endpoints. Each endpoint is independently `Absolute` (the existing literal
instant, `rl2:startInclusive`/`rl2:endExclusive`) or `Relative` (an anchor `LeftOperand` plus a
`Duration` offset, `rl2:startRelativeTo`+`rl2:startOffset` / `rl2:endRelativeTo`+`rl2:endOffset`);
see `resolveWindow` below for how a `Relative` endpoint becomes a concrete instant. A `DutyWindow`
denotes exactly one half-open interval. Recurring obligations ("ready at 8am every Monday") are
out of scope for 0.7: a Maintenance or Achievement Duty materialized from a recurring commitment
covers only its current occurrence. The deployment pattern is either a snapshot assembler that
instantiates the current period's window, or a profile-defined operand that carries the schedule.
A bounded recurrence form — a fixed period and count, expanded at compile time into finitely many
`DutyWindow` occurrences — is the candidate future extension; compile-time expansion keeps `Eval`
and the cell-partition argument (§Maintenance status, boundary completeness) unchanged.

#### Promises

```
Promise ::= Promise(proposed : Duty)
```

A Promise is structurally a proposed Duty: `promisor(p) ≡ p.proposed.subject` and
`promisee(p) ≡ p.proposed.counterparty`. Unlike on a Duty, a Promise's `counterparty` is
required — a Promise always names its promisee. A Promise's `object` may be absent, left for
Acceptance to bind when the Offer is materialized; its `condition` and `dutyWindow`, if present,
are carried unevaluated to the materialized Duty (see Materialization below). Because `proposed`
is a full `Duty`, an action-form Promise (`body = Achieve(action, postCondition?)`) may likewise
carry the optional `postCondition` of that `Achieve` slot; a state-form Promise (`body =
Maintain(invariant)`) has no such slot and so cannot. Like `condition` and `dutyWindow`, a present
`postCondition` is carried unevaluated to the materialized Duty and is consulted only by
`dutyStatus` there, never by `promiseStatus` pre-acceptance.

#### Conditions

```
Condition ::=
      AtomicConstraint(leftOperand, operator,
                       rightOperand : Literal | IRI | RuntimeReference | ValueSet,
                       targetNorm : StateTarget?)
    | And(Condition{2,})
    | Or(Condition{2,})
    | Xone(Condition{2,})
    | Not(Condition)
```

Notes:
- `And`, `Or`, and `Xone` take at least two conditions, matching
  `AndOrXoneOperandCardinalityShape`
- `leftOperand` is drawn from profile-defined operands; core defines `currentDateTime` and
  `obligationStateOperand`
- Time-based conditions use `AtomicConstraint` with `leftOperand = currentDateTime` (e.g., `currentDateTime lte deadline`)
- Dynamic value resolution on the left side uses `LeftOperand` with `resolutionPath`
- Dynamic value resolution on the right side uses `RuntimeReference` (e.g., `currentAgent`)
- Set comparisons use one inline `ValueSet`; asset collections are not value sets
- The stable RDF property `rl2:targetNorm` is interpreted as the tagged `StateTarget` defined
  below, preserving whether it references a Duty or a Promise. It is required for
  `obligationStateOperand` and forbidden for every other left operand.

#### Policies

```
Clause ::= Norm | Promise      -- mirrors rl2:Clause; only an Offer admits a Promise clause
PolicyKind ::= Set | Offer | Agreement

Policy ::= Policy {
  kind             : PolicyKind,
  grantor          : Agent?,       -- required for Agreement; optional for Offer; absent for Set
  grantee          : Agent?,       -- required for Agreement; optional for Offer; absent for Set
  condition        : Condition?,   -- optional policy-level activation condition
  prerequisiteDuty : finite set of Duty,  -- optional policy-level prerequisite set, folded into
                                           -- every Privilege clause like `condition` below
  clauses          : Clause+,      -- non-empty, matching PolicyShape
  meta             : Metadata
}
```

Set, Offer, and Agreement are pairwise disjoint concrete policy kinds. A Set contains only Norms
and has no grantor or grantee. An Offer may identify the proposed parties and is the only kind that
admits Promises. An Agreement identifies exactly one grantor and grantee and contains only Norms.

Conditions on Policies and clauses are optional in RDF. Normalization maps an
absent condition to the constant `True` and avoids manufacturing a unary `And`:

```
effectiveCondition(P, clause) =
    case (P.condition, clause.condition) of
        (None, None)       → True
        (Some(p), None)    → p
        (None, Some(c))    → c
        (Some(p), Some(c)) → And(p, c)
```

The canonical AST therefore contains a total condition for every clause while
preserving the logical-operator arities enforced by SHACL.

A Policy's `prerequisiteDuty` set is folded into every Privilege clause's own prerequisite set the
same way `P.condition` is folded into every clause's effective condition — one assertion at the
Policy gates every Privilege clause, instead of repeating it per Privilege. Because prerequisites
are already conjunctive (§Denotational Semantics for Norms), the fold is set union, not an `And`
node:

```
effectivePrerequisites(P, n : Privilege) = n.prerequisiteDuties ∪ P.prerequisiteDuty
```

Both the Privilege-declared and the Policy-declared members of this set are read by the same
`prerequisiteResult` machinery (§Pre-Resolution Normative Envelope below) — a Policy-level
prerequisite has no separate evaluation rule.

The Duties reachable from a Policy are:

```
independentDuties(P) = { d : Duty | d ∈ P.clauses }
attachedDuties(P)    = ⋃ { effectivePrerequisites(P,n) | n : Privilege ∈ P.clauses }
allDuties(P)         = independentDuties(P) ∪ attachedDuties(P)
```

A Duty may occur in both sets: it may be an independent clause of a Policy while also being
referenced — directly on a Privilege or via that Privilege's owning Policy's `prerequisiteDuty` —
as a prerequisite of one or more Privileges, in the same or a different Policy. The independent
obligation and the prerequisite-gating role are two effects of one Duty occurrence, not two
Duties: atom identity is `(obligate,d,P)` regardless of which route derives it (§Provenance
below), so `Out`'s set union deduplicates automatically and the Duty's one derived status is
reported once. An attached Duty's gating provenance is the set of Policies whose Privilege clauses
reference it (through either mechanism); one `obligate(d,P)` atom is derived per such Policy when
at least one matching owner makes the Duty applicable.

---

## Type System

The type system ensures well-formed policies.

### Typing Judgements

We use:

```
Γ ⊢ e : τ
```

### Types

```
τ ::= Agent | Action | Asset | Condition | Time | Boolean | Norm | Promise | DutyWindow | DutyBody
    | WorldSnapshot | EvaluationConfiguration | EvaluationResult
```

### Key Typing Rules

Privilege:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset     Γ ⊢ c : Condition
Γ ⊢ ds : finite set of Duty
--------------------------------------------------------------------------------
       Γ ⊢ Privilege(a, x, s, c, ds) : Norm
```

Duty:

```
Γ ⊢ a : Agent     Γ ⊢ b : Agent?     Γ ⊢ s : Asset
Γ ⊢ c : Condition Γ ⊢ w : DutyWindow?  Γ ⊢ body : DutyBody
--------------------------------------------------------------------------------
        Γ ⊢ Duty(a, b, s, c, w, body) : Norm
```

DutyBody formation:

```
Γ ⊢ x : Action     Γ ⊢ pc : Condition?
--------------------------------------------------------------------------------
        Γ ⊢ Achieve(x, pc) : DutyBody

Γ ⊢ i : Condition
--------------------------------------------------------------------------------
        Γ ⊢ Maintain(i) : DutyBody
```

Prohibition:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset
Γ ⊢ c : Condition
--------------------------------------------------------------------------
   Γ ⊢ Prohibition(a, x, s, c) : Norm
```

Promise:

```
Γ ⊢ d : Duty
--------------------------------------------------------------------------------
       Γ ⊢ Promise(d) : Promise
```

A Promise's `proposed` Duty carries a required `counterparty` and an optional `object`, the
reverse of the Duty typing rule's own cardinalities; this is the one documented exception, noted
here rather than by introducing a separate proposed-Duty type.

Condition types follow typical logical typing rules.

---

## Semantic Domains

We define semantic domains to interpret expressions.

### Agents

```
⟦Agent⟧ ⊆ A
```

### Actions

```
⟦Action⟧ ⊆ X
```

### Values

`Value` includes typed scalar values, `VURI(IRI)`, and finite `VSet(Value)` values. `Numeric` is
the sole numeric scalar type: `xsd:integer` and `xsd:decimal` literals both denote `Numeric`, with
exact decimal arithmetic and comparison — no floating-point representation. `xsd:float` and
`xsd:double` are not RL2 value types: a policy literal so typed is rejected at compile time, and a
float- or double-typed snapshot fact value resolves `Invalid`. A bare `xsd:duration` literal is
classified at canonicalization into one of two disjoint scalar types, `DayTimeDuration` (pure
day/time components) or `YearMonthDuration` (pure year/month components); mixed components are
rejected. A `ValueSet` projects to `VSet` after semantic duplicate removal and canonical member
ordering. Its members must be homogeneous when used by a comparison operator.

### World Snapshot

The evaluator reads one finite, immutable `WorldSnapshot W`; it has no mutable semantic state:

```text
W = (evaluationTime : Time,
     facts          : Set<AttributedFact>,
     evidence       : Set<Evidence>)
```

`AttributedFact`, `Evidence`, their scopes, identity rules, intervals, attribution, conflict
handling, and selection rules are defined normatively in `RL2_Model.md` §4. In summary:

- fact lookup is by canonical `(FactScope, Path)` and evaluation-time validity;
- equal asserted values agree, while distinct values for a single-valued key yield `Conflict`;
- action evidence is selected by explicit actor, action, object, and interval fields;
- occurrence time, not arrival order or a storage sequence, determines temporal eligibility;
- no event log or stored Duty or Promise state is part of `W`.

`state.Clock` is an authored path spelling for `W.evaluationTime`. Other declared paths resolve
through `W.facts`. Duty and Promise statuses are derived from policy content and `W.evidence`.

### Environments

```
Env = (Universe, Request?, Agent, Asset, Snapshot, Configuration)
```

A named six-field record (not a bare product), used for evaluating matching and operand paths.

- `Universe` — the immutable canonical PolicyUniverse and its finite term-inclusion indexes
- `Request?` — the core request being evaluated, when one exists; absent when `Env` is built for
  status derivation (`mkStatusEnv`, §Declarative Duty and Promise status), which has no access
  Request
- `Agent`   — the requesting agent (`Request.requestingAgent`; what `rl2:currentAgent` resolves to)
- `Asset`   — the requested asset
- `Snapshot` — the immutable `WorldSnapshot`
- `Configuration` — profiles, bounds, trust parameters, conflict strategy, and default decision

When `Request` is absent, every `request.*` path resolves to
`Invalid({ site: Path(path), target: None })` (§`requestField`), consistent with the status
environment's rule that `request.*` is invalid outside an access Request.

The fields do not correspond one-to-one with the canonical path roots (`request.*`, `agent.*`,
`asset.*`, `state.*`, `context.*`, `global.*`); several roots are backed by `Snapshot`, and two
fields back no root at all:

| Path root  | Backing `Env` field(s) |
|------------|-------------------------|
| `request.*` | `Request` — the three core scalar fields plus `request.parameters.<name>` (§`deref`) |
| `agent.*`   | `Snapshot` — facts under `AgentScope(Agent)`; `Agent` supplies the scope identity, not the data |
| `asset.*`   | `Snapshot` — facts under `AssetScope(Asset)`; `Asset` supplies the scope identity, not the data |
| `state.*`   | `Snapshot` — `state.Clock` is `Snapshot.evaluationTime`; other `state.*` paths are `StateScope` facts |
| `context.*` | `Snapshot` — `EvaluationScope` facts |
| `global.*`  | `Snapshot` — `GlobalScope` facts |

`Universe` backs no path root: it supplies the policy graph and term-inclusion indexes used by
matching, action-ancestor lookups, and status derivation. `Configuration` backs no path root: it
supplies the profile, bound, trust, and conflict-strategy parameters consulted during resolution.

`context.*` and `global.*` are scoped fact paths within `Snapshot`; they are not separate live
objects. `Env` contains no callback, source adapter, or mutable record.

---

## Denotational Semantics

Denotational semantics gives timeless meaning to norms and conditions.

### Result and Truth Algebra

Operand resolution and condition evaluation are **partial** — an operand may be missing,
wrong-typed, multi-valued, or fail to resolve. RL2 makes this total with typed carriers shared
throughout the normative semantics. Serialization of structured causes is an interchange-profile
question; the semantic value is defined here.

```
StateTarget  = NormTarget(Norm) | PromiseTarget(Promise)

ErrorSite    = LeftOperand | RuntimeReference | Path
             | SnapshotSite(String) | ConfigurationSite(String) | EvidenceSelector
             | StatusSite(StateTarget)
             | ComparisonSite(Operator, ValueType, ValueType)
ErrorKey     = { site : ErrorSite, target : StateTarget? }

EvalError    = Missing(ErrorKey) | Invalid(ErrorKey) | Conflict(ErrorKey)
             -- the canonical, comparable cause carried by ConditionResult

EvalValue<T> = Ok(T) | Err(EvalError, String?)
             -- the optional String is diagnostic text, not part of EvalError identity

Truth        = True | False | Unknown   -- no payload: causal attribution lives in ConditionResult
```

**Canonical error identity.** `EvalError` is the identity-bearing value: equality is structural
on `(constructor, ErrorKey)`. Diagnostic text lives only on `EvalValue.Err` and therefore cannot
change set membership. `ComparisonSite` includes both operand types, so two distinct mismatch
classes do not collapse merely because they use the same operator. This makes union over
`causes` commutative, associative, and idempotent without implementation-specific hashing.

`resolve : LeftOperand × Env × StateTarget? → EvalValue<Value>`. **Comparison lifts errors to
`Unknown`:** `apply(operator, l, r, Env)` is called, and its `True`/`False` result trusted, only when
both sides are `Ok` and type-compatible; any `Err` on either side — or a type mismatch between
two `Ok` values — yields `Unknown`, carrying the canonical `EvalError` as its cause.

**Condition evaluation carries causal attribution, not every error observed.** A condition
denotes a pair of its Kleene truth value and the *finite set of errors that actually
determined that truth value* — never the set of every error encountered anywhere in its
subtree:

```
ConditionResult = { truth : Truth, causes : Set<EvalError> }
```

Rules (instantiated by And/Or/Xone/Not below):
- An atomic resolution or comparison error produces `{ truth: Unknown, causes: {error} }`.
- `Not` preserves `causes` unchanged; only `truth` is negated.
- `And`, `Or`, and `Xone` first compute their Kleene truth value from the children's `truth`
  fields alone.
- If that truth value is `Unknown`, `causes` is the union of the `causes` of every child whose
  `truth` is `Unknown`.
- If the truth value is conclusively `True` or `False`, `causes` is **empty**: an error masked
  by a conclusive branch elsewhere in the same connective did not cause the result and must
  not be reported as if it did — there is no "winning error" to arbitrate.
- `causes` is a finite set under canonical error identity; ordering matters only when
  serializing diagnostics. An implementation MAY additionally keep every error encountered,
  causal or not, in a separate `observedErrors` side-channel for debugging — that channel is
  never attached to an `indeterminate` atom's payload (below), whose `causes` must explain
  *why that verdict* is unknown, nothing broader.

**Logical connectives are Kleene strong three-valued logic** — an error is *unobservable* when it
cannot change the outcome (short-circuit is therefore **specified**, not left implicit):

```
And:  True∧x = x ;  False∧x = False ;  Unknown∧False = False ;  Unknown∧(True|Unknown) = Unknown
Or:   False∨x = x ;  True∨x = True ;   Unknown∨True  = True  ;  Unknown∨(False|Unknown) = Unknown
Not:  ¬True = False ; ¬False = True ;  ¬Unknown = Unknown
Xone(c₁..cₙ): if any cᵢ = Unknown → Unknown; else True iff exactly one is True, else False
```

**Normative promotion.** A norm whose condition denotes `Unknown` is **not** silently inactive:
it contributes **`Indeterminate`** to the normative envelope. Mapping `Indeterminate → Deny` is an
**enforcement-adapter** policy (fail-closed at the PEP), *not* the semantic result — the evaluator
reports `Indeterminate` rather than silently choosing. The result retains the causal diagnostics.

We write, for the two kinds of denotation:

```
⟦ e ⟧      : Env → Value            -- terms (operands, right-values)
⟦ c ⟧      : Env → ConditionResult  -- conditions: truth plus the causal error set
```

Where only the truth value is needed (norm/policy activation checks, operational-semantics
guards), we read `⟦c⟧(Env).truth`; the full pair is consumed where causal attribution matters
(`deriveNorms`'s `indeterminate` atom, §Normative Derivation).

### Conditions

Atomic constraints (result is a `ConditionResult`, lifting operand and type errors to
`Unknown` with the responsible error attached as `causes`):

```
⟦ AtomicConstraint(op, operator, value, targetNorm?) ⟧(Env) : ConditionResult =
     let leftEV  = resolve(op, Env, targetNorm)          -- : EvalValue<Value>
     let rightEV = case value of
         RuntimeRef(r) → resolveRuntime(r, Env)           -- : EvalValue<Value>
         IRIRef(u)     → Ok(VURI(u))
         Literal(v)    → Ok(v)
         ValueSet(vs)  → Ok(VSet(canonicalMembers(vs)))
     in case (leftEV, rightEV) of
         (Ok(l), Ok(r)) | typeCompatible(operator, l, r) →
             { truth: apply(operator, l, r, Env), causes: ∅ }
         (Ok(l), Ok(r)) →
             { truth: Unknown, causes: { mkTypeMismatch(operator, targetNorm, l, r) } }
         _ →
             { truth: Unknown, causes: nonOk(leftEV) ∪ nonOk(rightEV) }

nonOk(Ok(_)) = ∅
nonOk(Err(e, _)) = { e }

typeCompatible(operator, l, r) =
    case operator of
        eq | neq            → sameDomain(l, r)
        lt | lte | gt | gte → ordered(l) ∧ ordered(r) ∧ sameDomain(l, r)
        isA                  → isURI(l) ∧ isURI(r)
        isAnyOf              → isSet(r) ∧ compatibleValueSet(l, r)
        isAllOf              → isSet(l) ∧ isSet(r) ∧ compatibleSets(l, r)
        isNoneOf             → isSet(r) ∧ compatibleValueSet(l, r)

sameDomain(l, r) = valueType(l) = valueType(r)
ordered(v)       = valueType(v) ∈ {Numeric, DateTime, DayTimeDuration, YearMonthDuration}
isURI(VURI(_))   = true;   isURI(_) = false
isSet(VSet(_))   = true;   isSet(_) = false

homogeneous(VSet(xs)) = ∀x,y ∈ xs : sameDomain(x,y)
compatibleSets(VSet(xs), VSet(ys)) =
    homogeneous(VSet(xs)) ∧ homogeneous(VSet(ys)) ∧
    (xs = [] ∨ ys = [] ∨ sameDomain(head(xs), head(ys)))
compatibleValueSet(VSet(xs), s : VSet) = compatibleSets(VSet(xs), s)
compatibleValueSet(v, VSet(ys)) = ¬isSet(v) ∧ homogeneous(VSet(ys)) ∧
                                  (ys = [] ∨ sameDomain(v, head(ys)))

    -- A profile may extend `ordered` only by declaring a total comparator for the new domain.
    -- No case admitted here can make `apply` get stuck. The `isA` right URI is verified as a
    -- class/subsumption-index key during compilation; `typeCompatible` checks its value shape.

mkTypeMismatch(operator, targetNorm, l, r) =
    Invalid({ site: ComparisonSite(operator, valueType(l), valueType(r)),
              target: targetNorm })
```

The RDF property remains named `rl2:targetNorm`, but its semantic value is the tagged
`StateTarget`: `NormTarget` for Duty-state queries and `PromiseTarget` for Promise-state queries.
The right operand may be a literal value or a runtime reference (e.g.,
`currentAgent`). If either operand is `Missing`/`Invalid`/`Conflict`, or the two resolved values
are not type-compatible for `operator`, the result is `Unknown` carrying that error as its
cause — the constraint never silently reads as `False`.

Logical conditions (Kleene strong three-valued, with `causes` masked whenever the connective
reaches a conclusive verdict — see Result and Truth Algebra):

```
foldK(kleeneOp, rs) =
    let t = kleeneOp([ r.truth | r ← rs ])
    in { truth: t,
         causes: if t ∈ {True, False} then ∅
                 else ⋃ { r.causes | r ∈ rs, r.truth = Unknown } }

⟦ And(cs)  ⟧(Env) = foldK(kAnd,  [ ⟦cᵢ⟧(Env) | cᵢ ← cs ])
⟦ Or(cs)   ⟧(Env) = foldK(kOr,   [ ⟦cᵢ⟧(Env) | cᵢ ← cs ])
⟦ Xone(cs) ⟧(Env) = foldK(kXone, [ ⟦cᵢ⟧(Env) | cᵢ ← cs ])
⟦ Not(c)   ⟧(Env) = let r = ⟦c⟧(Env) in { truth: ¬ᴷ r.truth, causes: r.causes }
```

`cs` is the `Condition{2,}` operand sequence (§Abstract Syntax, at least two conditions per
`AndOrXoneOperandCardinalityShape`); `kAnd`/`kOr`/`kXone` are the Kleene truth tables above,
applied to the full list of child truths at once — `kXone` in particular is "exactly one
`True`, else `Unknown` if any child is `Unknown`," not a chained binary XOR (chaining would
compute parity past two operands, the wrong answer).

---

### Helper Function Specifications

The condition semantics rely on several helper functions. For a testable evaluator, these must be precisely specified.

#### resolve : LeftOperand × Env × StateTarget? → EvalValue\<Value\>

The function `resolve(leftOperand, Env, targetNorm?)` maps a left operand to an
`EvalValue<Value>`: `Ok(v)` on success and `Err(error,note)` on failure. Although the RDF
property keeps its stable name `rl2:targetNorm`, the semantic parameter is a `StateTarget?` and
therefore preserves whether the referenced clause is a Norm or a Promise.

Resolution is closed over the policy, Request, snapshot, and configuration. There is no
function-based or external-lookup fallback inside `Eval`.

```
resolve : LeftOperand × Env × StateTarget? → EvalValue<Value>

failure(kind, site, target, note) =
    Err(kind({ site: site, target: target }), Some(note))

resolve(op, Env, targetNorm) =
    case op of
        -- Core derived-status operand
        obligationStateOperand →
            case targetNorm of
                Some(NormTarget(d : Duty)) →
                    resolveDutyStatus(d, Env.Universe, Env.Snapshot, Env.Configuration)
                Some(PromiseTarget(p)) →
                    resolvePromiseStatus(p, Env.Universe, Env.Snapshot, Env.Configuration)
                None → failure(Missing, op, None, "obligationStateOperand requires a targetNorm")
        -- Profile-declared snapshot operands
        _ | op.resolutionPath ≠ ⊥ →
            deref(op.resolutionPath, op, Env)

        _ → failure(Missing, op, targetNorm, "operand has no core or snapshot binding")
```

Where:
* `obligationStateOperand` accepts either `NormTarget(d : Duty)`, querying the derived Duty
  status, or `PromiseTarget(p)`, querying the derived status of an Offer-local Promise
* `op.resolutionPath` — path expression declared on the operand via `rl2:resolutionPath`
* `declaredType(op)` — the operand's expected value type, read from `rl2:valueType` (a
  datatype IRI or profile value class); `rdfs:range` on an operand individual is tolerated
  documentation only and is not consulted by the compile pass
* `Err(Missing(key),note)` indicates the operand could not be resolved — never fatal,
  always lifted to `Unknown` at the condition level

All policy-visible contextual data uses declared `rl2:LeftOperand` instances. Core status
operands use the fixed branches above, `currentDateTime` uses its fixed `state.Clock` path, and
profile operands use explicit snapshot paths. This provides:

- Type safety (operands declare an expected value type via `rl2:valueType`)
- Validation (SHACL can verify operand usage)
- Specifiability (one finite lookup algorithm)
- Auditability (all data access points are declared)

RL2 Core defines the following left operand instances:

* `currentDateTime` → `WorldSnapshot.evaluationTime`
* `obligationStateOperand` → derived Duty status, or the derived status of an Offer-local
  Promise, depending on whether `targetNorm` is `NormTarget` or `PromiseTarget`

Profiles define domain-specific left operands with resolution paths, such as:
* `purpose` → `rl2:resolutionPath "context.purpose"`
* `dataOwner` → `rl2:resolutionPath "asset.dataOwner"`
* `department` → `rl2:resolutionPath "agent.department"`

#### Runtime References

Runtime references resolve to values at evaluation time. These are used in `rightOperandRef` for dynamic comparisons.

```
resolveRuntime : RuntimeReference × Env → EvalValue<Value>

resolveRuntime(ref, Env) =
    case ref of
        currentAgent → Ok(Env.Agent)
        _            → failure(Missing, ref, None, "unrecognized runtime reference")
```

The `currentAgent` reference resolves to `Env.Agent`, the requesting agent. Other IRI-valued
right operands are ordinary `VURI` constants and do not invoke `resolveRuntime`.

#### Profile Resolution

A policy may declare vocabulary dependencies with `rl2:requiresProfile` (each value an `rl2:Profile` carrying an `rl2:profileVersion`). Before evaluation, the loader runs profile resolution against the evaluator's **supported-profile registry** — a set of `(profileIRI, supportedVersion)` pairs that is evaluator state, not part of the policy graph.

**Unknown-profile rule (fail-closed).** For each `requiresProfile P`, the loader MUST find a supported entry whose IRI equals `P`'s IRI and whose version is *compatible*. If any required profile is unsupported or only supported at an incompatible version, the policy is **rejected at load time** — never evaluated with a partially-understood vocabulary, and never silently accepted by ignoring the requirement:

```
loadOK(Policy, Registry) =
    ∀ P ∈ requiredProfiles(Policy) :
        ∃ (iri, supV) ∈ Registry :
            iri = P.iri ∧ compatible(supV, P.profileVersion)
    -- otherwise: reject(Policy) at ingestion (a load error, not ⊥ at eval time)
```

**Version negotiation (SemVer, same-major).** The referenced Profile's declared version is the **minimum required**:

```
compatible(supV, reqV) =
    supV.MAJOR = reqV.MAJOR ∧ (supV.MINOR, supV.PATCH) ≥ (reqV.MINOR, reqV.PATCH)
```

A major-version mismatch is always incompatible (breaking changes); a higher supported minor/patch is compatible (additive changes). This mirrors the SHACL `ProfileShape`/`RequiresProfileShape` structural checks, which only verify the declarations are well-formed — the compatibility decision itself is a runtime check because the registry is not in the graph.

#### deref : Path × LeftOperand × Env → EvalValue\<Value\>

`deref` interprets a declared path as a key into the normalized snapshot. It never traverses a
host-language object or invokes a connector.

```text
Path       ::= Root '.' Segment ('.' Segment)*
Root       ::= 'agent' | 'asset' | 'context' | 'state' | 'request' | 'global'
Segment    ::= Identifier
Identifier ::= [a-zA-Z_][a-zA-Z0-9_]*
```

A path exceeding `MaxPathDepth`, using another root, containing an empty segment, or containing
`*`, `/`, `\\`, `%`, `..`, or an escape sequence is rejected during canonical projection. Paths
are data keys, not filesystem or language-level member expressions.

The canonical `request.*` paths are `request.requestingAgent`, `request.requestedAction`,
`request.requestedAsset`, and `request.parameters.<name>` for a declared parameter name. Any other
`request.*` path is rejected during canonical projection.

```text
deref(path, op, Env) =
    case path of
        "request.requestingAgent" → requestField(Env.Request, requestingAgent, path)
        "request.requestedAction" → requestField(Env.Request, requestedAction, path)
        "request.requestedAsset"  → requestField(Env.Request, requestedAsset, path)
        "request.parameters." + name → requestParameter(Env.Request, name, path)
        "request." + _            → failure(Invalid, path, None,
                                             "unsupported core Request field")
        "state.Clock"             → Ok(Env.Snapshot.evaluationTime)
        _ →
            case factKey(path, Env.Agent, Env.Asset) of
                Err(e,note) → Err(e,note)
                Ok(key) → resolveFact(key, declaredType(op), declaringProfile(op),
                                      Env.Snapshot, Env.Configuration)
```

`resolveFact` and its `admitsFact` admissibility filter are defined in `RL2_Model.md` §4.2/§4.4,
along with the normative threat model they operate under: `WorldSnapshot` is the output of a single
trusted assembler, and mixed-trust filtering across sources is the assembler's responsibility
before the snapshot is constructed — `Eval` performs no source-level trust arbitration of its own.
Filtering happens during `resolveFact`'s candidate-set construction, not as a separate poisoning
step: a fact whose attribution fails the configuration's finite `Admissibility` record (§4.4) is
excluded from the candidate set exactly as if it were absent, so a key for which every candidate is
filtered out yields the same attributed `Missing` as a key with no candidates at all — never a
distinct error kind and never a silent fallback to another candidate.

`requestField(None,_,path)` returns `Invalid({ site: Path(path), target: None })`; a request path therefore cannot
silently read a Duty or Promise status environment.

```text
requestParameter(None, _, path)    = failure(Invalid, path, None,
                                             "request.parameters used outside an access Request")
requestParameter(Some(R), name, path) =
    case R.parameters[name] of
        Some(v) → Ok(v)
        None    → failure(Missing, path, None, "request parameter not supplied")
```

`request.parameters.<name>` resolves through the same discipline as any other operand: present
under `name` is `Ok(value)`, using the same `Value` universe as every other operand (values are
typed per the profile's declared operand range); absent is `Missing`, never a silent default.
Attribution for either outcome is the Request itself, not a snapshot `AttributedFact` — the
parameters map is immutable input to `Eval`, so this adds no impurity. `factKey` is total over
canonical fact paths when the required scope is present:

```text
factKey("agent."   + rest, a, _)       = Ok(AgentScope(a), canonicalPath)
factKey("asset."   + rest, _, Some(s)) = Ok(AssetScope(s), canonicalPath)
factKey("asset."   + rest, _, None)    = failure(Missing, canonicalPath, None,
                                                  "status content has no asset scope")
factKey("context." + rest, _, _)       = Ok(EvaluationScope, canonicalPath)
factKey("state."   + rest, _, _)       = Ok(StateScope, canonicalPath)
factKey("global."  + rest, _, _)       = Ok(GlobalScope, canonicalPath)
```

`request.*` has exactly the three scalar fields in the core Request plus the `parameters` map.
Additional request metadata must be a declared `context.*` fact or belong to an interchange
profile; an evaluator cannot invent an implicit Request field beyond these four.

The `global` root contains caller-supplied aggregate facts in `GlobalScope`. Computing a seat
count, active-Agreement set, or other aggregate happens during snapshot assembly. `Eval` applies
the same fact-resolution rules as for any other root.

#### Declarative Duty and Promise status

Status is a result over immutable inputs, not a stored-state transition:

```
DutyStatus    ::= Pending | Active | Fulfilled | Violated
PromiseStatus ::= Pending | Fulfilled | Violated

StatusResult<S> ::= Known(S)
                  | IndeterminateStatus(causes : finite non-empty Set<EvalError>)
```

`IndeterminateStatus` is not an ontology state. It preserves errors that prevent the evaluator
from selecting one of the existing state individuals. Policy RDF contains no asserted Duty or
Promise status; every status is derived from the evaluation inputs.

One Duty node denotes one occurrence. A present `dutyWindow` is the finite half-open interval
`[start, end)`; absence is unbounded. When either endpoint is `Relative`,
`resolveWindow` resolves it to a concrete interval once per evaluation, before `before`/`inside`/
`closed` are applied:

```
resolveEndpoint(Absolute(t), d, U, W, C) = Ok(t)
resolveEndpoint(Relative(op, dur), d, U, W, C) =
    case resolve(op, mkStatusEnv(U, d.subject, Some(d.object), W, C), None) of
        Ok(t : DateTime) → Ok(t + dur)
        Ok(_)            → failure(Invalid, op, None, "window anchor did not resolve to a DateTime")
        Err(e)           → Err(e)

resolveWindow(None, d, U, W, C)  = Ok(None)
resolveWindow(w, d, U, W, C) =
    case (resolveEndpoint(w.start,d,U,W,C), resolveEndpoint(w.end,d,U,W,C)) of
        (Ok(s), Ok(e)) | s < e → Ok(Some([s, e)))
        (Ok(s), Ok(e))         → failure(Invalid, w, None, "resolved window is not start < end")
        (rs, re)               → Err({ c | Err(c) ∈ {rs, re} })
```

The anchor resolves through the same `resolveFact`/`resolve` discipline as any other operand:
`Missing` (the anchor fact is absent) or `Invalid` (it resolves to a non-`DateTime`) both make the
endpoint — and therefore the whole window — unresolved; a resolved-but-degenerate interval
(`start ≥ end`, only reachable when at least one endpoint is `Relative`, since materialization
already excludes it for two `Absolute` endpoints) is likewise `Invalid` and unresolved. `before`,
`inside`, and `closed` below operate on the window returned by `resolveWindow(d.window, d, U, W,
C)`, computed once per evaluation and reused for every boundary check on that Duty or Promise
occurrence. `dutyStatus` and `promiseStatus` (below) check `resolveWindow` first: a window
resolution failure short-circuits to `IndeterminateStatus` carrying the resolution causes, before
the `before`/`closed` gates or any body evaluation are attempted. The following predicates then fix
every boundary over the resolved window `rw`:

```
before(rw, now) = rw ≠ None ∧ now < rw.start
inside(rw, t)   = rw = None ∨ rw.start ≤ t < rw.end
closed(rw, now) = rw ≠ None ∧ now ≥ rw.end
```

At the start instant the Duty is assessable. Evidence at the end instant is outside the window;
at that same instant a still-unsatisfied Achievement Duty is Violated. There is no implicit
recurrence or terminal-state reset. A repeated period requires another canonical Duty node.

`at(W,t)` is `W` with `evaluationTime = t`. It does not mutate the supplied snapshot. Status
conditions use a request-free environment whose agent and asset scopes are fixed by the Duty or
Promise content; `request.*` is invalid in a postcondition, invariant, or promised state. The
normal fact-validity and evidence-eligibility rules therefore define a historical slice from the
same finite semantic input:

```
mkStatusEnv(U, a, s?, W, C) = (U, None, a, s?, W, C)
evalAt(c, t, U, a, s?, W, C) = ⟦c⟧(mkStatusEnv(U,a,s?,at(W,t),C))
```

For an Achievement Duty, evidence is selected by the Duty subject, an action equal to or narrower
than the required action, the Duty object, and the Duty window.
The selector adds no ambient storage-order condition. If `postCondition` is absent, each
selected evidence item is a qualifying witness. If present, it is evaluated at that item's occurrence
time; later unrelated state cannot retroactively make an action successful:

```
achievementCandidates(d, rw, U, W, C) =
    selectEvidence(actionSelector(d.subject, d.body.action, d.object, rw, U), W, C)

qualifies(d, e, U, W, C) =
    case d.body.postCondition of
        None     → { truth: True, causes: ∅ }
        Some(pc) → evalAt(pc, e.occurredAt, U, d.subject, Some(d.object), W, C)
```

`actionSelector(a,x,s,w,U)` selects evidence whose actor is `a`, whose object is `s`, whose action
is equal to or included in `x` under `U.actionAncestors`, and whose occurrence time is inside `w`
(or unrestricted when `w=None`). `w` here is the *resolved* window (see `resolveWindow` above),
never an unresolved `Relative` endpoint. `selectEvidence` then applies the snapshot's attribution
rules from `RL2_Model.md` §4.3.

`achievementStatus` is total; it takes the already-resolved window `rw` from its caller
(`dutyStatus`), which performs `resolveWindow` once:

```
achievementStatus(d, rw, U, W, C) =
    if before(rw, W.evaluationTime) then Known(Pending)
    else case achievementCandidates(d, rw, U, W, C) of
        Err(e) → IndeterminateStatus({e})
        Ok(es) →
            let qs = [ qualifies(d,e,U,W,C) | e ∈ es ] in
            if ∃q ∈ qs : q.truth = True then Known(Fulfilled)
            else if ∃q ∈ qs : q.truth = Unknown then
                IndeterminateStatus(⋃ { q.causes | q ∈ qs, q.truth = Unknown })
            else if closed(rw, W.evaluationTime) then Known(Violated)
            else Known(Active)
```

No matching action evidence is `Ok(∅)`, not `Missing`: it means the Achievement has not yet been
fulfilled. Evidence excluded by the configuration's admissibility record (`RL2_Model.md` §4.4) is
absent from the candidate set in exactly the same way — a definite status, never an error. In core,
`selectEvidence` never returns `Err`: the snapshot interchange schema excludes malformed evidence
before `Eval`, and the admissibility record filters rather than errors. The `Err` branch here (and
in `promiseStatus`) is retained for `EvalValue` type totality and for any future evidence-side
error source a revision may introduce, not for present reachability.

For a windowed Maintenance Duty, `elapsed(rw,now)` is the set of instants inside its resolved
window no later than `now`:

```
elapsed(rw, now) = { t | inside(rw, t) ∧ t ≤ now }
```

`throughout` applies the existing three-valued condition semantics to every such instant:

```
throughout(i, rw, d, U, W, C) =
    let rs = { evalAt(i,t,U,d.subject,Some(d.object),W,C) |
               t ∈ elapsed(rw,W.evaluationTime) } in
    if ∃r ∈ rs : r.truth = False then { truth: False, causes: ∅ }
    else if ∀r ∈ rs : r.truth = True then { truth: True, causes: ∅ }
    else { truth: Unknown,
           causes: ⋃ { r.causes | r ∈ rs, r.truth = Unknown } }
```

This is not an instruction to sample a continuous clock. Over a finite snapshot and bounded
condition tree, truth changes only at the finite boundaries contributed by fact-validity
intervals, the Duty window, and literal time comparisons. A conforming
implementation partitions the elapsed window into truth-invariant finite cells at those
boundaries, retaining singleton boundary cells when equality or inclusivity can change truth, and
evaluates one representative per cell. An uncovered cell resolves the relevant fact as `Missing`
and therefore yields `Unknown`.

In RL2 0.7, a Maintenance Duty's or Promise's `rl2:invariant` admits only fact-resolving operands
and clock comparisons (`currentDateTime`); `obligationStateOperand` inside an invariant is
rejected at canonical projection. This restriction does not reach `rl2:condition`: status
operands remain permitted in applicability conditions (`sla-credit-clause` relies on exactly
this), and that placement is unaffected. The boundaries enumerated above — fact-validity
endpoints, the Duty window, and literal time comparisons — are complete exactly for this operand
class; an invariant referencing another norm's derived status would also change truth at that
norm's own evidence and window boundaries, recursively, which the listed boundaries do not cover.
Lifting the restriction requires the recursive boundary-collection extension over the compiled
condition/status-dependency DAG, deliberately deferred beyond 0.7.

```
maintenanceStatus(d, rw, U, W, C) =
    if before(rw, W.evaluationTime) then Known(Pending)
    else if rw = None then
        case evalAt(d.body.invariant,W.evaluationTime,U,d.subject,Some(d.object),W,C) of
            { truth: True, _ }       → Known(Active)
            { truth: False, _ }      → Known(Violated)
            { truth: Unknown, causes } → IndeterminateStatus(causes)
    else let r = throughout(d.body.invariant, rw, d, U, W, C) in
            if r.truth = False then Known(Violated)
            else if r.truth = Unknown then IndeterminateStatus(r.causes)
            else if closed(rw, W.evaluationTime) then Known(Fulfilled)
            else Known(Active)

dutyApplicabilityResult(d, U, W, C) =
    case d.condition of
        None    → { truth: True, causes: ∅ }
        Some(c) → ⟦c⟧(mkStatusEnv(U,d.subject,Some(d.object),W,C))

dutyStatus(d, U, W, C) =
    case resolveWindow(d.window, d, U, W, C) of
        Err(causes) → IndeterminateStatus(causes)
        Ok(rw) →
            if before(rw, W.evaluationTime) then Known(Pending)
            else case dutyApplicabilityResult(d,U,W,C) of
                { truth: False, _ }          → Known(Pending)
                { truth: Unknown, causes }   → IndeterminateStatus(causes)
                { truth: True, _ } → case d.body of
                    Achieve(_) → achievementStatus(d,rw,U,W,C)
                    Maintain(_) → maintenanceStatus(d,rw,U,W,C)
```

`dutyStatus` is defined on concrete duties only: `d.subject` and `d.object` are read directly
throughout (`mkStatusEnv`, `achievementCandidates`, `dutyApplicabilityResult`) with no sentinel
handling. A Duty carrying `rl2:anyAgent` or `rl2:anyAsset` is a template with no standalone
status — calling `dutyStatus` on it directly is meaningless, since no evidence is ever attributed
to a sentinel. A caller in a request context resolves this first, via `bind` (§Duty Template
Binding): a *bound occurrence* — the concrete duty produced by `bind(d, a, o)` for a specific
request's agent and asset — is an ordinary concrete duty. Once such a bound occurrence is recorded
in an `EvaluationResult` (as the target of a `permit`/`obligate` atom), it is a fully concrete Duty
and its status is well-defined and may be evaluated again — `dutyStatus` against a later
`WorldSnapshot` — for later audit or status inquiry, exactly like any authored Duty.

Window resolution happens once, before applicability or body evaluation, so an unresolved
`Relative` endpoint (a `Missing` or `Invalid` anchor) makes the whole Duty `IndeterminateStatus`
rather than silently falling through to `Pending` or a body-specific status.

A false applicability guard therefore denotes a Duty that is not currently required and remains
`Pending`; it is not a fulfilled Duty. A profile that needs a one-way trigger must provide a
snapshot fact whose validity records that the trigger remains established. Missing or conflicting
applicability data produces `IndeterminateStatus`.

A Maintenance Duty without a finite window is an ongoing snapshot requirement: it is Active when
the invariant is true now, Violated when false now, and cannot be Fulfilled. It makes no claim
about an interval with an unspecified start. For a windowed Maintenance Duty, complete coverage
is required; merely observing the invariant as true at `evaluationTime` is insufficient.

Promise status is derived without a Promise state machine, evaluated over `pr.proposed`, the
Promise's proposed Duty:

```
promiseStatus(pr, U, W, C) =
    let d = pr.proposed in
    let p = d.subject in
    let s? = d.object in
    case d.body of
        Achieve(x, _) →
            case s? of
                None → IndeterminateStatus({
                    Missing({ site: StatusSite(PromiseTarget(pr)),
                              target: Some(PromiseTarget(pr)) }) })
                Some(s) → case selectEvidence(actionSelector(p,x,s,None,U), W, C) of
                    Err(e)    → IndeterminateStatus({e})
                    Ok(∅)     → Known(Pending)
                    Ok(_)     → Known(Fulfilled)

        Maintain(c) →
            case ⟦c⟧(mkStatusEnv(U,p,s?,W,C)) of
                { truth: True,  _ }      → Known(Fulfilled)
                { truth: False, _ }      → Known(Violated)
                { truth: Unknown, causes } → IndeterminateStatus(causes)

```

`mkStatusEnv` admits `agent.*`, `asset.*`, `state.*`, `context.*`, and `global.*`, binding agent and
asset to the proposed Duty's content rather than an access Request. A status condition that uses
`request.*` is invalid because status derivation has no access Request.
An `Achieve` Promise body has no Duty window applied pre-acceptance: it may be fulfilled by
evidence but does not become Violated solely through elapsed time. Acceptance can crystallize it
into a bounded Duty. `promiseStatus` never yields `Active` — that status distinguishes Duties in
force from Promises, which are not yet operative. The proposed Duty's own `condition` and
`dutyWindow`, if present, are carried unevaluated to the materialized Duty and are not consulted by
`promiseStatus` prior to acceptance; on an action-form Promise the same is true of `postCondition`
(matched and discarded above as `Achieve(x, _)`) — it is consulted only by `dutyStatus` after
crystallization.

Status dependencies induced by `targetNorm` must be acyclic. Canonical projection rejects a
self-reference or cycle with `Invalid(ConfigurationSite("statusDependency"))`; memoized structural
evaluation then terminates and gives each referenced Duty or Promise one result.

```
statusDiagnostics(statuses) =
    ⋃ { es | IndeterminateStatus(es) ∈ range(statuses) }
```

The core status operands expose a `Known` state as an ordinary value. When status is
indeterminate, the atomic operand reports one stable status-site error; the complete underlying
causes remain in `EvaluationResult.diagnostics` through `statusDiagnostics`.

```
resolveDutyStatus(d,U,W,C) =
    case dutyStatus(d,U,W,C) of
        Known(s) → Ok(s)
        IndeterminateStatus(_) →
            Err(Invalid({ site: StatusSite(NormTarget(d)),
                          target: Some(NormTarget(d)) }),
                Some("Duty status is indeterminate"))

resolvePromiseStatus(p,U,W,C) =
    case promiseStatus(p,U,W,C) of
        Known(s) → Ok(s)
        IndeterminateStatus(_) →
            Err(Invalid({ site: StatusSite(PromiseTarget(p)),
                          target: Some(PromiseTarget(p)) }),
                Some("Promise status is indeterminate"))
```

#### apply : Operator × Value × Value × Env → Boolean

The function `apply(op, left, right, Env)` applies a comparison operator to two **already-resolved,
already type-compatible** values — the `AtomicConstraint` denotation (§Conditions) is the only
caller, and it calls `apply` only after `typeCompatible(operator, left, right)` holds; a
domain mismatch is caught there and surfaced as `Invalid`, never passed into `apply`:

```
apply : Operator × Value × Value × Env → Boolean

apply(op, left, right, Env) =
    case op of
        eq       → left = right
        neq      → left ≠ right
        lt       → left < right
        lte      → left ≤ right
        gt       → left > right
        gte      → left ≥ right
        isA      → instanceOf(left, right, Env.Universe)
        isAnyOf  → valuesOf(left) ∩ elements(right) ≠ ∅
        isAllOf  → elements(right) ⊆ elements(left)
        isNoneOf → valuesOf(left) ∩ elements(right) = ∅

valuesOf(VSet(xs)) = set(xs)
valuesOf(v)         = {v}       -- admitted only for scalar v by typeCompatible
elements(VSet(xs))  = set(xs)   -- called only after typeCompatible established VSet

instanceOf(VURI(u), VURI(c), U) =
    ∃t : (u rdf:type t) ∈ U ∧ (t = c ∨ t rdfs:subClassOf+ c in U)
```

Canonical projection computes the finite `rdf:type`/`rdfs:subClassOf` closure used by `isA`.
Profiles that use `isA` must supply the relevant classes and hierarchy in the policy universe.

A profile may extend the operator set beyond these ten via a declared `rl2:ProfileOperator` (see
`RL2_Compilation.md` §9.1). Such a declaration is conforming only when the profile's own normative
document supplies a denotation that extends `apply` as a pure **total** function over the operator's
declared `leftParamType`/`rightParamType` pair — every input pair maps to `True`, `False`, or a typed
`EvalError`, with no partiality and no host discretion, exactly as `apply` is defined above for the
core operators. Core conformance claims quantify over the ten core comparison operators enumerated
here only; implementing a profile's operators is that profile's own, separate conformance claim.

---

## Denotational Semantics for Norms

Norms are evaluated in the context of a **Request** `R = (a_req, x_req, s_req)` specifying the requesting agent, requested action, and target asset. The denotation takes both the request and an environment constructed from it.

### Environment Construction

Given a PolicyUniverse `U`, Request `R = (a_req, x_req, s_req)`, WorldSnapshot `W`, and
EvaluationConfiguration `C`:

```
mkEnv(U, R, W, C) = (U, R, a_req, s_req, W, C)
                    -- (Universe, Request, Agent, Asset, Snapshot, Configuration)
```

The environment retains the full Request so `request.*` paths resolve. All other dynamic values
come from `W`; `U` supplies canonical action and collection indexes; `C` supplies profiles,
declared bounds, trust parameters, the combining strategy, and the default decision.

`EvaluationConfiguration` also declares
`defaultDecision : Permit | Deny | NotApplicable` (default `NotApplicable`). It is applied only to
substitute for what `resolveDecision` would otherwise report as `NotApplicable` (§Conflict
Resolution, §Composition); it never substitutes for `Indeterminate`, which is a distinct outcome
reporting genuine ambiguity, not the absence of a matching rule.

### Request Matching

A norm applies to a request only if the norm's subject, action, and object match the request. A
Request whose `requestingAgent` or `requestedAsset` is a sentinel individual (`rl2:anyAgent` or
`rl2:anyAsset`) is invalid and is rejected before evaluation — a sentinel names a population, not
a requester.

All three request axes share one parameterized matching rule with a per-axis declared preorder:

```
matchesComponent(declared, requested, ⊑, U) =
    declared = requested ∨ ⊑(requested, declared, U)
```

| axis | sentinel | preorder `⊑` | transitive? |
|---|---|---|---|
| subject | `rl2:anyAgent` matches every requesting agent | `requested ∈ agentMembers(declared, U)` (direct `rl2:agentMember`) | no |
| object | `rl2:anyAsset` matches every requested asset | `requested ∈ members(declared, U)` (direct `rl2:member`) | no |
| action | none (deliberate: no `rl2:anyAction` sentinel in 0.7) | `includedInAction(requested, declared, U)` | yes |

The asymmetry is deliberate, not an oversight. Action vocabularies are curated, profile-declared
DAGs (§5's `rl2:includedIn`) — finite, precomputed, and safe to close transitively: a Prohibition
on a broad action correctly catches an unanticipated narrower one. Collection membership is
bounded and author-controlled — a collection lists exactly the agents or assets its author
enumerated, and closing it transitively would let an author's grant silently reach members of a
member's member they never enumerated. Attribute-defined populations (any agent, any asset)
therefore use the sentinel + condition mechanism instead of a third membership relation.

```
subjectMatches(a, requested, U) =
    a = rl2:anyAgent ∨ matchesComponent(a, requested, agentPreorder, U)
  where agentPreorder(requested, declared, U) = requested ∈ agentMembers(declared, U)

objectMatches(s, requested, U) =
    s = rl2:anyAsset ∨ matchesComponent(s, requested, assetPreorder, U)
  where assetPreorder(requested, declared, U) = requested ∈ members(declared, U)

actionMatches(Duty(_,_,_,_,_,Achieve(x,_)), requested, U) =
    matchesComponent(x, requested, actionPreorder, U)
actionMatches(Privilege(_,x,_,_,_), requested, U) =
    matchesComponent(x, requested, actionPreorder, U)
actionMatches(Prohibition(_,x,_,_), requested, U) =
    matchesComponent(x, requested, actionPreorder, U)
actionMatches(Duty(_,_,_,_,_,Maintain(_)), _, _) = true
  where actionPreorder(requested, declared, U) = includedInAction(requested, declared, U)

matchesRequest(n, Env) =
    let R = Env.Request in
    subjectMatches(n.subject, R.requestingAgent, Env.Universe) ∧
    objectMatches(n.object, R.requestedAsset, Env.Universe) ∧
    actionMatches(n, R.requestedAction, Env.Universe)
```

Where:
- `includedInAction(x_req, x, U)` tests the finite canonical action-inclusion index
- `members(s, U)` returns the **direct** `rl2:member` individuals of `s` in the canonical policy
  universe when `s` is an `AssetCollection` (empty otherwise)
- `agentMembers(c, U)` returns the **direct** `rl2:agentMember` individuals of `c` in the canonical
  policy universe when `c` is an `AgentCollection` (empty otherwise); parallel to `members(s, U)`
  and, like it, not transitively closed — membership in a nested sub-collection does not match the
  outer collection

A Maintenance Duty has no requested action to match. The `true` action component above makes an
independent Maintenance Duty a candidate on its subject and object only. An attached Duty is
reached through its owning Privilege and therefore uses the Privilege's request match; its own
subject and object still determine performance evidence, not access matching.

`AssetCollection ⊑ Asset` and `AgentCollection ⊑ Agent`, so a norm may target a collection
directly and a collection may itself be a member of another collection. Neither `members(s,U)` nor
`agentMembers(c,U)` is transitively closed: membership in a nested sub-collection does not match
the outer collection. Membership is read from the fixed canonical PolicyUniverse.

`rl2:anyAgent` and `rl2:anyAsset` are the sole unbound-population mechanism: matching against them
is unconditionally true on that axis, and the actual population is defined entirely by conditions
over `agent.*` / `asset.*` facts (§Conditions). SHACL's `sh:minCount 1` on `rl2:subject` and
`rl2:object` is unaffected — a sentinel value still satisfies that cardinality, so an unbound norm
is always an explicit authoring act, never a forgotten property silently becoming a universal
grant. A sentinel-subject or sentinel-object norm whose population-delimiting condition cannot be
evaluated (a `Missing` fact) yields `Unknown` and therefore an attributed `indeterminate` atom
through the ordinary truth algebra — an unknown population member is never silently permitted or
denied.

#### Duty Template Binding

A Duty carrying `rl2:anyAgent` as its subject or `rl2:anyAsset` as its object is a **template**:
it names an attribute-defined population, not a concrete instance, and by itself supplies no
instance for evidence selection, window anchoring, or condition evaluation to scope against
(§Declarative Duty and Promise status builds exactly such a scope from `d.subject`/`d.object`).
`bind` produces the concrete duty a request-context computation actually needs:

```
bind(d, a, o) = d with
    subject := a  iff d.subject = rl2:anyAgent, else d.subject
    object  := o  iff d.object  = rl2:anyAsset,  else d.object
    -- all other fields (condition, dutyWindow, body, counterparty) unchanged
```

`bind` is the identity on a Duty that carries no sentinel. It is applied in exactly four
request-context places, each tied to a Privilege or Duty that has already matched the current
Request `R = Env.Request`, so the substitution values are always `R.requestingAgent` and
`R.requestedAsset`:

1. **Prerequisite gating** (§Pre-Resolution Normative Envelope) — `prerequisiteResult` consults
   the bound duty, not the raw (possibly sentinel-bearing) template.
2. **Attached-duty reporting** (§Normative Derivation) — `ownerScopeResult` evaluates the bound
   duty's applicability, and the `obligate`/`indeterminate` atoms emitted for `attachedDuties(P)`
   target the bound duty.
3. **`rl2:consequentDuty` derivation** (§Normative Derivation) — the obligate atom emitted when a
   Privilege fires is that of the bound duty.
4. **Independent Duty clause atom emission** (§Normative Derivation, the existing
   `independentDuties(P)` rule) — the emitted `obligate` atom is bound likewise.

**Invariant.** No sentinel individual (`rl2:anyAgent`, `rl2:anyAsset`) ever appears as the subject
or object of a Duty inside an emitted `NormativeAtom`, nor as the `d.subject`/`d.object` supplied
to a `dutyStatus` query. Every duty reaching `dutyStatus` or an envelope atom in a request context
has already passed through `bind`. `dutyStatus` itself is unchanged and continues to assume a
concrete, sentinel-free duty (§Declarative Duty and Promise status) — templates are made concrete
by their caller, not by `dutyStatus`.

Action subsumption is defined by the transitive closure of `rl2:includedIn`:

```
x' ⊑ᵁ x  :=  includedInAction(x', x, U)
```

Canonical projection computes the finite transitive closure of `rl2:includedIn` in `U`. Usage of
`rdfs:subClassOf` for action refinement is non-normative in RL2.

Action subsumption applies uniformly across request matching and Achievement evidence selection.
There is no stored `Performed` Boolean; `achievementCandidates` derives performance from the
immutable evidence set.

**RDF grounding**: Actions are individuals of `rl2:Action`. Action subsumption (`x' ⊑ x`)
follows the transitive closure of `rl2:includedIn`; `members(s)` is the set of direct `rl2:member`
links when `s` is an `rl2:AssetCollection`; `agentMembers(c)` is the set of direct
`rl2:agentMember` links when `c` is an `rl2:AgentCollection`. A conduct norm's subject matches the
requesting Agent exactly, matches a declared `AgentCollection`'s direct members, or — when the
subject is `rl2:anyAgent` — matches unconditionally with the population left to a condition.
Role-based authorization not expressed via a collection or a sentinel uses an explicit condition
over a profile-defined agent fact.

Policy and clause conditions are combined by `effectiveCondition`. During derivation, `True`
activates a matching clause, `False` leaves it inactive, and `Unknown` produces an attributed
`indeterminate` atom. A Duty's own applicability guard also gates its derived status as specified
above; its action and optional postcondition, or its invariant, determine status once that guard
is true. The policy universe is an immutable caller-supplied input; discovery and version selection
occur before `Eval`.

---

## Pure Offer Acceptance (Offer → Agreement)

An **Offer** may contain voluntary Promises together with Norms that are restated as terms of the
proposed Agreement. A Promise is not an operative Norm before acceptance. Acceptance is a pure,
one-time policy transformation; it is not an
event consumed by `Eval`, a state transition, or an instruction to persist anything.

The transformation operates on the validated normalized Offer and explicit acceptance
parameters:

```text
SourceRef  = stable canonical identity of one Promise clause or policy-local Norm
PromiseRef = SourceRef restricted to Promise clauses

Acceptance = (
    agreementId   : IRI,
    grantor        : Agent,
    grantee        : Agent,
    primaryIds     : total map SourceRef  → IRI,
    objectBindings : partial map PromiseRef → Asset,
    dutyWindows    : partial map PromiseRef → DutyWindow
)

MaterializationResult =
      Materialized(agreement : Agreement, sourceMap : map SourceRef → IRI)
    | Rejected(errors : non-empty finite set of MaterializationError)

MaterializationError ::=
      InvalidOffer(site, reason : InvalidOfferReason)
    | PartyMismatch(promiseRef)
    | InvalidIdentityAllocation(id)
    | MissingPromiseObject(promiseRef)
    | InvalidDutyWindow(promiseRef)
    | DanglingInternalReference(site, targetId)

InvalidOfferReason ::=
      WrongPolicyKind | EmptyClauseSet | ConflictingObjectBinding
    | InvalidAcceptanceDomain | NonLocalPromiseTarget
    | InvalidOutputShape | StatusDependencyCycle
```

`primaryIds` assigns the output Norm identifier for every materialized source: the crystallized
Duty for a Promise and the copied Norm for a policy-local Norm. Locality is structural and narrow:

```text
localNorms(O) =
    { n : Norm | n ∈ O.clauses }
    ∪ { d : Duty | ∃ n : Privilege ∈ O.clauses : d ∈ n.prerequisiteDuties ∪ n.consequentDuties }
```

The second set contains the non-clause Duties owned through `prerequisiteDuty` or
`consequentDuty`; their attachment placement is preserved rather than promoted to Agreement
clauses. `targetNorm` is a reference,
not an ownership relation. Its target is rewritten only when independently present in
`localNorms(O)` or among the Promise clauses of `O`; otherwise it remains external and is not
copied. Canonical RDF projection preserves this distinction.

Define `sourceIris(O)` as every IRI occurring as an RDF term in the canonical projection of `O`;
blank nodes contribute no IRI. `agreementId` and all `primaryIds` values MUST be pairwise distinct,
and the resulting set of allocated IRIs MUST be disjoint from `sourceIris(O)`. Identifier allocation is therefore
explicit input, not a nondeterministic `fresh IRI` operation. How a caller allocates globally
unique IRIs is outside the transformation. `ref(x)` denotes the `SourceRef` assigned to source
Promise or local Norm `x` by the normalized projection; materialization depends only on its stable
identity and equality, not on its concrete encoding.

`objectBindings` may supply an object for either an action or state Promise when the Offer leaves
the catalogue target open. A conflicting authored and supplied object is `InvalidOffer`; an
identical binding is accepted but has no effect. `dutyWindows` supplies an optional finite
performance interval for the Duty created from a Promise. It does not alter a copied Norm clause.

An Offer-level `condition` denotes the applicability guard proposed for the resulting Agreement;
it does not determine whether or when an Acceptance may be issued. Offer validity, withdrawal,
and acceptance authorization are outside this pure transformation. Materialization therefore
rewrites and copies `O.condition` as the Agreement-level applicability guard.

### Validation

`materialize(O,A)` collects all applicable errors and returns `Rejected(errors)` without a partial
Agreement when any error exists. A value is **structurally conforming** when it inhabits the typed
abstract syntax in this document and its RDF projection satisfies the applicable core SHACL
shapes. The input is valid only when:

1. `O` is a structurally conforming `Offer` with a non-empty finite clause set;
2. any `grantor` or `grantee` authored on `O` equals the corresponding value in `A`;
3. each Promise's `(promisor,promisee)` is either `(A.grantor,A.grantee)` or
   `(A.grantee,A.grantor)`—orientation may differ, but acceptance cannot bind an absent third
   party;
4. `primaryIds` has domain `PromiseClauses(O) ∪ localNorms(O)`, the optional maps have no other
   keys, and the identity map satisfies the freshness and injectivity rule;
5. every promised action or state has exactly one object after applying `objectBindings`;
6. every `dutyWindows[p]` whose `start` and `end` are both `Absolute` satisfies
   `dutyWindows[p].start < dutyWindows[p].end`; a `dutyWindows[p]` with a `Relative` endpoint is
   structurally valid here regardless of ordering, since `materialize` reads no snapshot and
   cannot resolve an anchor — ordering for a `Relative` endpoint is checked at Eval time by
   `resolveWindow` (§Declarative Duty and Promise status), which yields `IndeterminateStatus` if
   the resolved interval is degenerate or the anchor fails to resolve;
7. every Promise-valued `targetNorm` occurring in the Offer's policy condition, clause conditions,
   Promise content, or attached prerequisite Duties targets a Promise clause of that same Offer;
8. every reference to a clause of `O` has a corresponding `primaryIds` entry; and
9. rewriting produces an acyclic, structurally conforming Agreement.

A failure of item 6 yields `InvalidDutyWindow(ref(p))`; a failure of item 7 yields
`InvalidOffer(site, NonLocalPromiseTarget)`. `StatusDependencyCycle` reports a cycle already
present in the Offer's status-dependency graph: injective renaming and the typed Promise-to-Duty
target rebinding cannot create one.

Materialization-error identity is the constructor plus its typed fields; explanatory prose is not
part of identity. Errors are enumerated by constructor, site, and referenced identifier, so
validation order cannot change the result. A primary error on a Promise (missing object, invalid
Duty window, or party mismatch) suppresses derivative output-shape and
rewrite errors caused solely by the absence of that Promise's generated Duty; independent errors
are still collected.

### Crystallization

Crystallization is an unwrap-and-rebind of the Promise's proposed Duty, not a re-derivation from
separate promisor/promisee/content fields. For a Promise `p = Promise(d)`, let `s` be `d`'s
authored object or accepted object binding, and let `w` be `d`'s authored or accepted Duty window,
if one exists:

```text
crystallize(p,A) =
    let d = p.proposed in
    Duty(subject      = d.subject,
         counterparty = Some(d.counterparty),
         object       = s,
         condition    = d.condition,
         dutyWindow   = w,
         body         = d.body)
```

The Duty identifier is `A.primaryIds[ref(p)]`. The proposed Duty's `counterparty` (the Promise's
promisee) is retained on the materialized Duty; no additional norm is generated. The proposed
Duty's `condition` and `dutyWindow`, authored on the Promise and not evaluated pre-acceptance, are
carried through unchanged unless `A.dutyWindows` supplies a window binding. `body = d.body` copies
the whole `DutyBody` verbatim, so on an action-form Promise this includes its optional
`postCondition` (`Achieve(action, postCondition?)`): the created Achievement Duty's body is
`Achieve(p.action, p.postCondition?)`, carried unevaluated exactly like `condition` and
`dutyWindow` — it is consulted only by `dutyStatus` on the materialized Duty, never here.

An `Achieve` body without an accepted window creates an unbounded Achievement Duty, which can
remain Pending. A `Maintain` body without a window creates an ongoing Maintenance Duty, which can
be Active or Violated but cannot become Fulfilled. A finite accepted window gives the resulting
Duty the status boundaries defined in §Declarative Duty and Promise status.

### Clause copying and reference rewriting

Let `sourceMap(x) = A.primaryIds[ref(x)]`. Each policy-local Norm is structurally copied under
`sourceMap(n)`. Immutable value expressions may be shared; Norm identity is never shared across
the Offer and Agreement. Only mapped top-level Norms become Agreement clauses; copied attached
Duties remain attached. All Norm-valued references inside the copied policy condition and
clauses are traversed recursively:

```text
rewriteRef(r) =
    if r is a Promise clause or policy-local Norm of O then sourceMap(r) else r

rewriteAtomic(a) =
    if a.targetNorm = PromiseTarget(p) then
        a[targetNorm ↦ NormTarget(sourceMap(p))]
    else a[targetNorm ↦ rewriteRef(a.targetNorm)]
```

`rewriteRef` applies to `prerequisiteDuty` and Norm-valued `targetNorm`. A Promise-valued
`targetNorm` already uses `obligationStateOperand` — the same operand as a Duty-valued
`targetNorm` — so crystallization only rebinds the target from `PromiseTarget(p)` to
`NormTarget(sourceMap(p))`; the `leftOperand` is unchanged. Conditions without `targetNorm` are
copied structurally.

The result is:

```text
materialize(O,A) =
    if validateMaterialization(O,A) = errors ≠ ∅ then Rejected(errors)
    else Materialized(
        Agreement(id        = A.agreementId,
                  grantor   = A.grantor,
                  grantee   = A.grantee,
                  condition = rewrite(O.condition),
                  clauses   = copiedTopLevelNorms(O,A)
                              ∪ crystallizedDuties(O,A),
                  metadata  = copyMetadata(O)
                              ∪ { prov:wasDerivedFrom ↦ O.id }),
        sourceMap)
```

No Promise survives in the Agreement. `materialize` neither reads a `WorldSnapshot` nor emits an
effect; identical Offer and Acceptance values produce the same result. With indexed maps it is
linear in the size of the normalized Offer, including its condition trees and references.
`copyMetadata` preserves non-structural annotations and profile/version requirements; it excludes
the source identifier, policy kind, parties, condition, clauses, and any prior materialization
provenance because those fields are constructed explicitly above.

`Eval` derives statuses and normative atoms but does not create remedial norms, consume events,
or mutate policy or world state.

## Normative Derivation (I/O-Logic Foundation)

RL2's evaluation follows an **I/O logic** pattern (Makinson & van der Torre): derivation produces a normative envelope, then conflict resolution yields a final decision.

### Pre-Resolution Normative Envelope

The function `Out` computes the **unresolved set** of normative atoms from a policy universe and
environment (atoms are deduplicated by canonical identity — the `∪` below is set union, not
multiset sum). Access clauses use `accessResult`: it folds the policy and clause conditions and,
for a Privilege, its prerequisite Duties. Independent Duties use `effectiveCondition` directly.
Attached Duties use `attachedDutyResult`, which makes the Duty applicable only within the scope of
its owning Privilege. An `Unknown` result is attributed to the affected norm rather than silently
treated as inapplicable.

For a Duty `d`, convert its derived status into a condition-shaped result:

```
fulfilledResult(d, Env) =
    case dutyStatus(d, Env.Universe, Env.Snapshot, Env.Configuration) of
        Known(Fulfilled)       → { truth: True,    causes: ∅ }
        Known(Pending)         → { truth: False,   causes: ∅ }
        Known(Active)          → { truth: False,   causes: ∅ }
        Known(Violated)        → { truth: False,   causes: ∅ }
        IndeterminateStatus(E) → { truth: Unknown, causes: E }

dutyConditionResult(d, Env) =
    case d.condition of
        None    → { truth: True, causes: ∅ }
        Some(c) → ⟦c⟧(mkStatusEnv(Env.Universe,
                                      d.subject,
                                      Some(d.object),
                                      Env.Snapshot,
                                      Env.Configuration))

prerequisiteResult(d, Env) =
    let bd = bind(d, Env.Request.requestingAgent, Env.Request.requestedAsset) in
    foldK(kOr, [notResult(dutyConditionResult(bd,Env)), fulfilledResult(bd,Env)])
    -- not applicable OR fulfilled, against the concrete (bound) duty — a sentinel-bearing
    -- prerequisite template is never itself passed to dutyConditionResult or dutyStatus
    -- (§Duty Template Binding)

notResult(r) = { truth: ¬ᴷ r.truth, causes: r.causes }
```

**Divergence from the status-condition encoding.** `prerequisiteResult` gives an inapplicable Duty
a vacuous pass: `dutyConditionResult(d,Env).truth = False` makes `notResult(...) = True`, and the
`kOr` fold short-circuits to `True` regardless of `fulfilledResult`. The alternative encoding —
an explicit condition testing `obligationStateOperand eq Fulfilled` against the same Duty via
`targetNorm` — does not get this vacuous pass: on an inapplicable Duty its status is `Pending`
(§Duty Status Derivation), so the equality test yields `False`, not `True`. The two encodings
therefore diverge exactly on an inapplicable prerequisite: `prerequisiteDuty` reads "not applicable
or fulfilled" (vacuously satisfied when inapplicable), while a status-condition equality test reads
"conclusively fulfilled" (false when inapplicable, regardless of applicability). This is why
`prerequisiteDuty` is the canonical form for ordinary gating: it expresses the intended reading —
an inapplicable prerequisite does not block. A status-condition equality test remains appropriate
only when a policy genuinely means to observe another norm's status as cross-norm data — e.g.
distinguishing "fulfilled" from "not yet fulfilled for any reason including inapplicability" — not
as a substitute for gating.

```
allResults(rs) =
    if rs = [] then { truth: True, causes: ∅ } else foldK(kAnd, rs)

anyResults(rs) =
    if rs = [] then { truth: False, causes: ∅ } else foldK(kOr, rs)

canonicalDutyOrder(ds) = sort ds by dutyId
canonicalPrivilegeOrder(ns) = sort ns by privilegeId

accessResult(P, n : Privilege, Env) =
    allResults([⟦effectiveCondition(P,n)⟧(Env)] ++
               [ prerequisiteResult(d,Env) |
                 d ∈ canonicalDutyOrder(effectivePrerequisites(P,n)) ])

accessResult(P, n : Prohibition, Env) = ⟦effectiveCondition(P,n)⟧(Env)

ownerScopeResult(P, n, d, Env) =
    if ¬matchesRequest(n,Env) then { truth: False, causes: ∅ }
    else foldK(kAnd, [⟦effectiveCondition(P,n)⟧(Env), dutyConditionResult(bindReq(d,Env),Env)])

attachedDutyResult(P, d, Env) =
    anyResults([ ownerScopeResult(P,n,d,Env) |
                 n ∈ canonicalPrivilegeOrder({ n : Privilege ∈ P.clauses |
                                               d ∈ effectivePrerequisites(P,n) }) ])
```

A Policy-level prerequisite therefore reaches `accessResult` and `attachedDutyResult` through
`effectivePrerequisites(P,n)` exactly like a Privilege-level one: every Privilege clause `n` of `P`
picks up `P.prerequisiteDuty` as if it had been declared on `n` directly, so `d ∈ P.prerequisiteDuty`
makes every `n : Privilege ∈ P.clauses` a qualifying owner in `attachedDutyResult`, i.e. `d` gates
every Privilege clause of `P`.

`allResults` gives an empty prerequisite set the identity value `True`; it does not construct an
authored zero-arity `And`. `prerequisiteResult` masks irrelevant errors in the usual Kleene way:
an inapplicable Duty is satisfied as a prerequisite regardless of its separately reported status,
and a conclusively Fulfilled Duty is sufficient even when its applicability guard is Unknown.
Pending, Active, and Violated all mean that an applicable prerequisite has not been met. They
make that Privilege inactive; they do not create a global Deny.

```
Out : (PolicySet S, Env) → ℘(NormativeAtoms), where S ⊆ Env.Universe

Out(S, Env) =
    ⋃ { deriveNorms(P, Env) | P ∈ S }

bindReq(d, Env) = bind(d, Env.Request.requestingAgent, Env.Request.requestedAsset)
    -- (§Duty Template Binding): the concrete duty for atoms and status queries raised in this
    -- request's own evaluation

deriveNorms(P, Env) =
    if P : Offer then ∅
    else
        { permit(n, P)   | n : Privilege ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = True } ∪
        { forbid(n, P)   | n : Prohibition ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = True } ∪
        { obligate(bindReq(d,Env), P) | d ∈ independentDuties(P), matchesRequest(d, Env), ⟦effectiveCondition(P,d)⟧(Env).truth = True } ∪
        { obligate(bindReq(d,Env), P) | d ∈ attachedDuties(P), attachedDutyResult(P,d,Env).truth = True } ∪
        { obligate(bindReq(d,Env), P)
                         | n : Privilege ∈ P.clauses, d ∈ n.consequentDuties,
                           matchesRequest(n, Env), accessResult(P,n,Env).truth = True,
                           ⟦effectiveCondition(P,d)⟧(Env).truth = True } ∪
        { indeterminate(n, P, accessResult(P,n,Env).causes)
                         | n : Privilege ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = Unknown } ∪
        { indeterminate(n, P, accessResult(P,n,Env).causes)
                         | n : Prohibition ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = Unknown } ∪
        { indeterminate(bindReq(d,Env), P, ⟦effectiveCondition(P,d)⟧(Env).causes)
                         | d ∈ independentDuties(P), matchesRequest(d, Env), ⟦effectiveCondition(P,d)⟧(Env).truth = Unknown } ∪
        { indeterminate(bindReq(d,Env), P, attachedDutyResult(P,d,Env).causes)
                         | d ∈ attachedDuties(P), attachedDutyResult(P,d,Env).truth = Unknown } ∪
        { indeterminate(bindReq(d,Env), P, ⟦effectiveCondition(P,d)⟧(Env).causes)
                         | n : Privilege ∈ P.clauses, d ∈ n.consequentDuties,
                           matchesRequest(n, Env), accessResult(P,n,Env).truth = True,
                           ⟦effectiveCondition(P,d)⟧(Env).truth = Unknown }
```

The `rl2:consequentDuty` clause above fires only alongside its own Privilege's grant
(`accessResult(P,n,Env).truth = True`); it contributes no term to `accessResult` itself and so
cannot affect whether that Privilege — or any other norm — resolves to `Permit`. Its own
`effectiveCondition(P,d)` (present only when the Duty declares one) is evaluated under the
existing independent-Duty condition discipline, the same rule `independentDuties(P)` uses just
above, not the status-scoped `mkStatusEnv` discipline used for prerequisite gating: a
`consequentDuty` is a request-context obligation like an independent clause, not a status
observation. Both the independent-clause and consequent-duty atoms are emitted for the *bound*
duty (`bindReq`, §Duty Template Binding); a sentinel-carrying template Duty never itself becomes
the target of an `obligate` or `indeterminate` atom.

`deriveNorms` reads the Request, snapshot, and configuration only through `Env`; there is no free
mutable state or external-context argument.

An Offer is transformation input, not an operative access policy. Its clauses contribute no
normative atoms before acceptance, so proposed Privileges cannot grant access and proposed Duties
cannot affect an access decision. `derivePromiseStatuses` and `deriveDutyStatuses` may still
report the snapshot-derived status of clauses reachable from an Offer for inspection and
diagnostics. Normative effect begins only in the materialized Agreement.

`violated(d, P)` is **not** an `Out`/`deriveNorms` atom. Duty status is a separate derived value.
It is read while deriving a Privilege with prerequisites and is also returned for every Duty
reachable from the supplied policy universe. An implementation may memoize the pure status
function; evaluation performs no status transition. Duty atoms remain in the envelope for
normative reporting but resolution ignores them. In particular, an unrelated violated Duty can
never deny a request.

The type filters are normative. Promises are not request-matched access candidates and therefore
do not produce access-decision `indeterminate` atoms.

**Provenance.** A `NormativeAtom` wraps the full norm object (`n`/`d`, not a projected
`(a,x,s)` triple) together with its source policy `P`. Every atom therefore identifies the norm
and policy that produced it. Atom equality is structural: `(atom-kind,n,P)` for
definite atoms and `(indeterminate,n,P,causes)` for Unknown atoms. `causes` is itself a canonical
set, so its enumeration order cannot create a second atom. Two policies granting the same
`(a,x,s)` shape remain distinct atoms with independent provenance because atom equality includes
`P`: even the same Norm `n` — SHACL permits one Norm to be a clause of multiple Policies — still
yields one distinct atom per owning Policy. For an attached Duty that is not also an independent
clause, `P` contains at least one Privilege that references it (directly or through `P`'s own
`prerequisiteDuty`) while the Duty itself is not in `P.clauses`. A Duty that IS also an independent
clause of `P` keeps that clause's `obligate(d,P)` atom — attachment adds a gating effect on its
referencing Privilege(s), not a second atom or a second provenance. Resolution consumes this
attributed envelope.

### Canonicalization rules

Every primitive RL2 relation has one admitted structural encoding. Canonical projection removes
RDF-level, lexical, ordering, and enumerated local syntactic alternatives; it does not attempt
general logical normalization of arbitrary semantically equivalent Boolean policies, which is
exponential in policy size. The following are the complete set of admitted local normalizations
and authoring preferences:

**(a) `prerequisiteDuty` is the canonical form for ordinary pre-duty gating.** As shown above
("Divergence from the status-condition encoding"), `prerequisiteResult` and an
`obligationStateOperand eq Fulfilled` condition targeting the same Duty diverge exactly on an
inapplicable Duty: `prerequisiteResult` gives it a vacuous pass, while the status-condition
equality test yields `False` (an inapplicable Duty's status is `Pending`, never `Fulfilled`). A
Privilege gated on a Duty's completion is authored with `prerequisiteDuty`, not with a
status-condition equality test, whenever the intent is ordinary gating — "this Privilege requires
that Duty to be met, and does not block on an inapplicable Duty." An `obligationStateOperand`
condition remains appropriate only when a policy genuinely means to observe another norm's derived
status as cross-norm data — e.g. a Duty or Privilege reporting on a *different* norm's fulfillment
for informational, auditing, or cross-policy purposes — not as a substitute for gating its own
applicability. Because this is a distinction of authorial intent (is the observation about *this*
Privilege's own gate, or about another norm's status as data?), it is not one canonical projection
can decide mechanically from RDF shape alone; it is a normative authoring rule, not an automatic
rewrite.

**(b) Atomic complement operators are the preferred authoring form — not a projection-time
rewrite.** `neq` and `isNoneOf` read more directly than `Not(eq(...))` and `Not(isAnyOf(...))`.
Their `Truth` values coincide in every case: `apply` computes `left ≠ right` for `neq` exactly
where `Not(eq(...))` flips `left = right`, and `valuesOf(left) ∩ elements(right) = ∅` for
`isNoneOf` exactly where `Not(isAnyOf(...))` flips `valuesOf(left) ∩ elements(right) ≠ ∅` (see
`apply`, §Helper Function Specifications). However, the two spellings are **not** identical once
`causes` is considered, so projection does **not** rewrite one into the other as a
semantics-preserving normalization. `mkTypeMismatch(operator, targetNorm, l, r)` embeds the
operator itself in `ComparisonSite(operator, ValueType, ValueType)` (§Result and Truth Algebra,
"Canonical error identity"); a type mismatch under `Not(eq(...))` therefore produces a cause
tagged `ComparisonSite(eq, ...)`, while the same mismatch under `neq` produces
`ComparisonSite(neq, ...)` — distinct `EvalError` values under RL2's structural error identity,
even though both resolve to `Unknown`. The divergence is confined to the type-mismatch path: a
missing or invalid operand produces `causes = nonOk(leftEV) ∪ nonOk(rightEV)`, which does not
depend on the operator at all, so `Not(eq(...))` and `neq` (and likewise `Not(isAnyOf(...))` and
`isNoneOf`) produce identical causes when the divergence is a missing fact rather than a type
mismatch. Because a difference exists in at least one case, `neq`/`isNoneOf` are stated only as
the preferred authoring spelling for new policies, not as a required canonical rewrite of
`Not(eq(...))`/`Not(isAnyOf(...))`.

**(c) A policy-level condition is shared factoring, not a distinct proposition.**
`effectiveCondition(P, clause)` (§Abstract Syntax, Policies) conjoins `P.condition` into every
clause's own condition; asserting a condition at the policy level denotes the same set of
effective conditions as asserting `And(P.condition, clause.condition)` on every clause of `P` — it
is not a separate expressible proposition with independent meaning. `P.prerequisiteDuty` is folded
the same way, via `effectivePrerequisites`. Canonical projection does not rewrite one spelling into
the other: the policy-level spelling is retained as authored because it states a condition shared
by every clause exactly once, instead of repeating it per clause.

### Monotonicity of Derivation

For one fixed immutable environment, `Out` is monotone in the selected subset of that
environment's policy universe:

```
For fixed Env and S ⊆ S' ⊆ Env.Universe,
Out(S, Env) ⊆ Out(S', Env)
```

Since `Out` is a union of per-clause contributions evaluated independently against the same
`Env`, selecting another policy can only add atoms. The result is independent of
clause-processing order.

This does not claim monotonicity when `Env.Universe` itself changes. A different universe may
change shared action hierarchies, collection membership, or status dependencies and is therefore
a different semantic input.

`Out` is not monotone in the environment: `not`, `neq`, `isNoneOf`, and upper bounds can change
from true to false when facts change, removing a derived atom. The environment is therefore one
immutable snapshot per evaluation. No optimization may assume that atoms survive a change of
snapshot.

Derivation does not use negation-as-failure over derived atoms. Conditions may still use
data-level negation and comparison over the fixed environment.

### Derivation vs Resolution

| Property | Out (Derivation) | Eval (Full) |
|----------|------------------|-------------|
| Monotone in selected policy set `S` (fixed `Env`) | Yes | No |
| Monotone in environment `Env` | No (conditions may be anti-monotone) | No |
| Deterministic | Yes | Yes |
| Conflict-handling | None (contradiction is data) | Strategy-based |
| Output | Set of atoms (dedup by canonical identity) | Single decision |

`Eval`'s policy-universe input `U` is a `CompiledPolicyModule` — the closed, typed output of the
compilation contract in `RL2_Compilation.md`, not raw policy RDF. This document defines what `Eval`
does with that module; `RL2_Compilation.md` defines how a validated RDF dataset becomes one, the
diagnostics that process can produce, and the soundness guarantee relating the two phases.

The `Eval` function composes snapshot validation, declarative status derivation, `Out`, and
access-conflict resolution. Status derivation precedes `Out` because Privilege prerequisites read
Duty status; it remains a pure interpretation of the same immutable inputs:

```
Eval(U, R, W, C) =
    let errors = validateConfiguration(U, C) ∪ validateSnapshot(W, C)
    in if errors ≠ ∅ then
        EvaluationResult(Indeterminate, ∅, ∅, ∅, errors)
    else
        let dutyStatuses = deriveDutyStatuses(U, W, C)     -- pure, memoizable support
        let promiseStatuses = derivePromiseStatuses(U, W, C)
        let Env = mkEnv(U, R, W, C)
        let envelope = Out(U, Env)
        let resolved = resolveDecision(envelope, C.strategy)
        let decision = if resolved = NotApplicable then C.defaultDecision else resolved
        in EvaluationResult(decision,
                            envelope,
                            dutyStatuses,
                            promiseStatuses,
                            diagnosticsOf(envelope, dutyStatuses, promiseStatuses))
```

`deriveDutyStatuses` is total over every independent or attached Duty reachable from the policy
universe and returns an immutable map. This makes every prerequisite result defined even when
the Duty does not itself produce an envelope atom:

```text
deriveDutyStatuses(U, W, C) =
    { d ↦ dutyStatus(d,U,W,C) | P ∈ U, d ∈ allDuties(P) }

derivePromiseStatuses(U, W, C) =
    { p ↦ promiseStatus(p,U,W,C) | p is a Promise clause in U }
```

Input errors short-circuit policy derivation because no condition may read an invalid semantic
input.

```text
diagnosticsOf(envelope, dutyStatuses, promiseStatuses) =
    ⋃ { causes | indeterminate(_, _, causes) ∈ envelope }
    ∪ statusDiagnostics(dutyStatuses)
    ∪ statusDiagnostics(promiseStatuses)
```

`statusDiagnostics` is defined by the declarative status algebra above.

The **normative envelope** `Out(U, Env)` is the first-class intermediate result: it is visible
before resolution and retains policy and clause attribution for audit.

Resolution may eliminate norms via priority or strategy, breaking monotonicity. This is by design:
`permit(a,x,s) ∧ forbid(a,x,s)` is an explicit conflict, not an inconsistency in the derivation.
`resolveDecision` applies norm priorities and the configured strategy. It never applies an
unstated specificity heuristic.

For architectural context, see `../docs/RL2_Architecture.md` §3.

---

## Conflict Resolution

`resolveDecision(envelope, strategy)` retains each complete
access-norm `indeterminate(norm,policy,causes)` atom. It computes the finite set of resolver
summaries reachable when each Unknown access candidate is independently inactive or active, then
maps those summaries through the same priority/strategy decision function. Duty
`indeterminate` atoms remain in the envelope and diagnostics but do not enter access resolution.
A single reachable decision is conclusive; more than one yields `Indeterminate`. The summary
space is polynomial and does not enumerate the `2^|I|` truth assignments. Mapping
`Indeterminate → Deny` is an **enforcement-adapter** decision (a fail-closed PEP), **not** the
semantic verdict: `Eval` returns `Indeterminate` so the ambiguity is auditable.

When multiple access norms apply, RL2 uses two explicit mechanisms:

1. **Access-norm priority** (`rl2:priority`): Privileges and Prohibitions may declare an integer
   priority; higher access candidates override lower access candidates before strategy is applied.
   Duty priority is irrelevant to access resolution. A prerequisite is either satisfied or it
   prevents its owning Privilege from becoming a candidate.

2. **Evaluator-level strategy**: The evaluator is configured with a conflict resolution strategy (e.g., prohibit-overrides, permit-overrides). This is **evaluator configuration**, not policy vocabulary—analogous to XACML combining algorithms.

The `strategy` parameter is evaluator configuration. Policies express norms and priorities;
the strategy combines opposite effects at the same maximal priority. The three strategies are
`ProhibitOverrides`, `PermitOverrides`, and `Invalid`, corresponding to ODRL's `prohibit`, `perm`,
and `invalid` values.

`resolveDecision(envelope, strategy)` retains attributed Unknown Privilege and Prohibition atoms
and projects definite and possible
activations into the compact `ResolverSummary` consumed by `decisionOf`. Duty atoms are not
access candidates.

```
resolveDecision(envelope, strategy) =
    let known    = { a ∈ envelope | kind(a) ∈ {permit, forbid} }
    let unknowns = { indeterminate(n,P,E) ∈ envelope |
                     n : Privilege ∨ n : Prohibition }
    let initial  = summarizeChoices(known)
    let summaries = choiceFold(canonicalOrder(unknowns), initial)
    let decisions = { decisionOf(s, strategy) | s ∈ summaries }
    in if |decisions| = 1 then the element of decisions else Indeterminate

activate(indeterminate(n : Privilege,   P, _)) = permit(n, P)
activate(indeterminate(n : Prohibition, P, _)) = forbid(n, P)

priority(n) = n.priority if declared, otherwise 0

ResolverSummary =
    { topPriority    : Integer?,
      hasPrivilege  : Boolean,
      hasProhibition : Boolean }

emptySummary = { None, false, false }
summarizeChoices(atoms) =
    fold(extendSummaries, {emptySummary}, canonicalOrder(atoms))

extendSummaries(summaries, atom) =
    { addAtom(s, atom) | s ∈ summaries }

canonicalOrder(atoms) = sort atoms by (sourcePolicyId, sourceClauseId, atomKind)
addAtom(s, permit(n, P)) =
    addAccess(s, Privilege, priority(n))
addAtom(s, forbid(n, P)) =
    addAccess(s, Prohibition, priority(n))

addAccess(s, kind, p) =
    if s.topPriority = None ∨ p > s.topPriority then
        { topPriority: p,
          hasPrivilege: kind = Privilege,
          hasProhibition: kind = Prohibition }
    else if p < s.topPriority then s
    else if kind = Privilege then
        s[hasPrivilege ↦ true]
    else
        s[hasProhibition ↦ true]

choiceFold([], summaries) = summaries
choiceFold(i :: rest, summaries) =
    let active = { addAtom(s, activate(i)) | s ∈ summaries }
    let next = summaries ∪ active
    in choiceFold(rest, next)
    -- retaining s chooses condition Unknown=False; active chooses Unknown=True

baseDecision(s) =
    if ¬s.hasPrivilege then NotApplicable else Permit

decisionOf(s, strategy) =
    case strategy of
        ProhibitOverrides →
            if s.hasProhibition then Deny else baseDecision(s)

        PermitOverrides →
            if s.hasPrivilege then Permit
            else if s.hasProhibition then Deny
            else NotApplicable

        Invalid →  -- ODRL "invalid": a conflict in the maximal-priority stratum is surfaced
            if s.hasPrivilege ∧ s.hasProhibition then Indeterminate
            else if s.hasProhibition then Deny
            else baseDecision(s)
```

The cases are exhaustive over the validated `Strategy` datatype. An unknown strategy is an
`Invalid(ConfigurationSite(strategy))` input error and never reaches `decisionOf`.

`addAtom` uses only priority comparison and Boolean accumulation, so definite summarization is
order-independent. `choiceFold` is exact for all joint Unknown access activations but deduplicates
after every step by summary equality. For `n` access atoms there are at most `4(n+1)` summaries:
one of four effect pairs for each possible top priority. The construction is polynomial and does
not enumerate the powerset of Unknown clauses.

Normative boundary consequences include:

- Under `PermitOverrides`, a definite Privilege plus an equal-priority Unknown Prohibition is
  `Permit`: either activation choice permits.
- Under `PermitOverrides`, a definite Prohibition plus an equal-priority Unknown Privilege is
  `Indeterminate`: the choices yield Deny and Permit.
- Under `Invalid`, a lower-priority definite Prohibition and two Unknown equal-higher-priority
  access atoms (one Privilege, one Prohibition) are `Indeterminate`.
  Activating either Unknown alone still yields Deny, but activating both creates a top-stratum
  conflict; retaining joint reachable summaries is therefore necessary.

`Indeterminate` here is the same value produced per norm in the denotations above. A fail-closed
enforcement adapter may map it to `Deny`, but that mapping is not part of `resolveDecision`.

Note: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

`resolveDecision` itself never returns anything but the three values above; substituting
`EvaluationConfiguration.defaultDecision` for a `NotApplicable` outcome is a separate step performed
by `Eval` (§Composition), not by `resolveDecision`. `defaultDecision` is an explicit,
evaluator-level open/closed-system parameter, analogous in kind to `strategy`: `Deny` encodes a
closed (deny-unless-permitted) system, `Permit` encodes an open (permit-unless-denied) system, and
`NotApplicable` (the default) leaves the no-matching-rule outcome unresolved and delegates the
choice to the PEP as pure reporting.

### Exception patterns

"Everywhere except X" is not one construct in RL2; it is a family of encodings with two distinct
*meanings* — "no permit at X" (the request is simply unmatched, `NotApplicable`) versus "an
explicit prohibition at X" (the request is affirmatively denied, `Deny`) — and the encodings are
not interchangeable once an operand is missing. The four forms below are derived directly from
`accessResult`, `resolveDecision`, and `choiceFold` above; none is guessed.

**(1) Single Privilege with a `neq`/`not`-condition.** One Privilege whose condition reads
`location neq ExcludedPlace` (or `Not(location eq ExcludedPlace)`, equivalent per rule 8b above)
matches broadly and denies itself at the excluded place by the condition going `False`, never by a
Prohibition. At the excluded place the condition is `False`, so `accessResult` is `False` and
`deriveNorms` contributes no atom at all — not even `indeterminate` — for that Privilege.

| Case | `accessResult` | Envelope contribution | `resolveDecision` | `Eval` decision (`defaultDecision = NotApplicable`) |
|---|---|---|---|---|
| At the excluded place | `False` | none | `NotApplicable` (empty envelope) | `NotApplicable` |
| Missing `location` fact | `Unknown` | one `indeterminate(Privilege)` atom | `Indeterminate` (only reachable summaries are `NotApplicable` or `Permit`, `\|decisions\|=2`) | `Indeterminate` |
| Elsewhere | `True` | `permit(Privilege)` | `Permit` | `Permit` |

A single indeterminate atom and no competing norm makes the missing-fact outcome `Indeterminate`
under every strategy — there is nothing for a Prohibition to contest.

**(2) Broad Privilege plus a scoped Prohibition, under a conflict-resolution strategy.** An
unconditional Privilege (matches everywhere) is joined by a Prohibition scoped to `location eq
ExcludedPlace`, both at the default priority `0`. Unlike (1), the excluded place now produces an
affirmative `forbid` atom, not merely the absence of a `permit` — "explicit prohibition there,"
not "no permit there." Outcomes are strategy-dependent because both norms occupy the same
priority stratum (`addAccess` keeps both flags set when priorities tie):

| Case | Envelope | `ProhibitOverrides` | `PermitOverrides` | `Invalid` |
|---|---|---|---|---|
| At the excluded place | `{permit(Privilege), forbid(Prohibition)}` | `Deny` | `Permit` | `Indeterminate` |
| Missing `location` fact | `{permit(Privilege), indeterminate(Prohibition)}` | `Indeterminate` | `Permit` | `Indeterminate` |
| Elsewhere | `{permit(Privilege)}` | `Permit` | `Permit` | `Permit` |

Derivation for the missing-fact row (`resolveDecision`, `choiceFold`, lines under "Conflict
Resolution" above): `known = {permit(Privilege, priority 0)}` gives `initial =
{{topPriority:0, hasPrivilege:true, hasProhibition:false}}`. Folding the one Unknown
(`indeterminate(Prohibition)`, priority 0) adds the "activated" summary
`{topPriority:0, hasPrivilege:true, hasProhibition:true}`, so `summaries` holds both. Under
`ProhibitOverrides`, `decisionOf` yields `Permit` for the retained summary and `Deny` for the
activated one — two decisions, hence `Indeterminate`. Under `PermitOverrides`, `hasPrivilege` is
`true` in both summaries, so both yield `Permit` — one decision, hence deterministic `Permit`
despite the missing fact: the broad Privilege dominates regardless of whether the Unknown
Prohibition would have activated. Under `Invalid`, the retained summary has `hasProhibition =
false` (`baseDecision → Permit`) and the activated summary has both flags `true` (`→
Indeterminate`) — again two decisions, hence `Indeterminate`.

**(3) Priority-based break-glass.** A broad, unconditional Prohibition at priority `0` ("no access,
ever") is overridden by a narrow, conditional Privilege at priority `10` (the break-glass
condition, e.g. `emergencyDeclared eq true`). Because `addAccess` discards atoms strictly below the
current top priority, the lower-priority Prohibition never reaches the summary once the
higher-priority Privilege is present, and the outcome does not depend on `strategy`:

| Case | Envelope | Decision (all three strategies) |
|---|---|---|
| Break-glass condition `True` | `{permit(Privilege,10), forbid(Prohibition,0)}` — Prohibition dropped, `topPriority = 10` | `Permit` |
| Break-glass condition `False` | `{forbid(Prohibition,0)}` only | `Deny` |
| Break-glass condition `Unknown` | `{indeterminate(Privilege,10), forbid(Prohibition,0)}` | `Indeterminate` (retained summary at priority 0 is `Deny`; activated summary at priority 10 is `Permit`) |

This survives changes to the evaluator's configured `strategy` because priority elimination in
`addAccess` happens before `decisionOf` ever branches on `strategy` — the two mechanisms are
independent, and (3) never reaches the tie-breaking case that (2) depends on.

**(4) `defaultDecision`-based ("never, except C").** A single Privilege carries the exception
condition `C`; no Prohibition is authored at all. `EvaluationConfiguration.defaultDecision = Deny`
supplies the closed-world default for every request the Privilege does not affirmatively match.

| Case | `resolveDecision` | `Eval` decision |
|---|---|---|
| Condition `C` holds | `Permit` | `Permit` |
| No matching norm (`C` false / request out of scope) | `NotApplicable` (empty envelope) | `Deny` (`defaultDecision` substituted) |
| Operand for `C` missing | `Indeterminate` (one `indeterminate(Privilege)` atom; reachable summaries are `NotApplicable` and `Permit`) | `Indeterminate` — **not** `Deny` |

The last row is the sharp edge of this pattern: `defaultDecision` substitutes only for a resolved
`NotApplicable`, never for `Indeterminate` (§Derivation vs Resolution, `Eval`'s composition). A
missing fact does not fall back to the closed-world default; it still surfaces as `Indeterminate`
for the PEP or a fail-closed adapter to handle explicitly.

**Which form is canonical.** For a plain exception with no need for its own explanation or
attached duties, (1) — single Privilege with `neq`/`not` — is canonical: it is the smallest
encoding and its missing-fact behavior does not depend on `strategy`. When the exception must
carry its own priority, condition, and independent provenance distinguishable from "no permit
here" — for example when the exception needs to be independently attributable in the resolved
envelope, or reported to audit as its own denied norm rather than an absent permit — (2), the
Privilege/Prohibition pair, is canonical, with the same-priority default reserved for cases where
the deployment accepts strategy-dependent resolution of the missing-fact case. For break-glass —
an exception meant to survive whatever `strategy` the evaluator is configured with — (3), the
priority-separated pair, is canonical. For closed-world deployments where every unmatched request
should default to `Deny` (or `Permit`) rather than reporting `NotApplicable`, (4),
`defaultDecision`, is canonical, with the caveat above that it does not paper over a missing-fact
`Indeterminate`.

### Duty Status Derivation

`deriveDutyStatuses` computes an immutable result map; it does not apply transitions or return a
new snapshot. The Achievement and Maintenance status functions include status indeterminacy and
the evidence interval for each attached Duty.

### Duty Attachment Boundary

Core has three Duty relationships only:

- a Duty linked from one or more Privileges (or their owning Policy) with `rl2:prerequisiteDuty` is blocking for each owner when applicable;
- a Duty linked directly from a Policy with `rl2:clause` is independent; and
- a Duty linked from a Privilege with `rl2:consequentDuty` fires alongside that Privilege's grant (§Normative Derivation) but never blocks it — the post-use or companion counterpart to `rl2:prerequisiteDuty`.

Concurrent obligations are not an additional core attachment mode; a genuinely ongoing requirement
is stated as a Maintenance Duty with an optional `dutyWindow`, independent or prerequisite as
appropriate. A one-shot post-use obligation triggered by a grant — attribution, logging, and
similar companion duties — is exactly what `rl2:consequentDuty` is for. Core `Eval` returns
`Permit` plus the complete Duty-status map; it does not schedule, enforce, or claim that an
ongoing obligation was imposed by the act of evaluation.

### Note on Evaluation Complexity

One `Eval` call is a bounded computation over finite policy, fact, and evidence sets. It neither
waits for evidence nor processes an event stream. Multi-step workflows may call `Eval` again with
a later snapshot, but scheduling, persistence, and trace semantics are future companion work.

---

## Constraint Algebra Semantics

Conditions form a compositional three-valued algebra. Time values use the same comparison
operators as other ordered values.

Properties:

* Associativity, commutativity, idempotence for And/Or
* De Morgan laws
* Temporal and contextual comparisons are orthogonal to logical structure
* Dynamic operands resolved at evaluation time
* Path-based evaluation is deterministic (fully resolved from Env)

This ensures determinism of constraint evaluation.

---

## Evidence Semantics

Evidence influences a result only through the Duty and Promise status functions. `Eval` does not
append, reorder, or transform evidence. Matching and temporal selection are defined in
`RL2_Model.md` §4.3.

---

## Policy Composition Semantics

Policy universes compose by set union:

```
U1 ⊔ U2 = U1 ∪ U2
```

Each policy retains its own applicability conditions, parties, profile declarations, and clause
provenance. The combined envelope is `Out(U1 ∪ U2, Env)`; `resolveDecision` then applies maximal
clause priority and the configured ODRL-compatible strategy to conflicting access atoms.

ODRL `inheritFrom` input is normalized by a translator before evaluation; native RL2 policy
composition is explicit clause union. The supported translation cases and diagnostics are defined
in `RL2_ODRL_Mapping.md`.

---

## Interoperability

RL2 is a canonical target for supported ODRL 2.2 input. Translation is a partial, deterministic
function:

```text
translate(ODRLPolicy, TranslationConfiguration)
    -> CanonicalRL2Policy | Rejected(diagnostics)
```

`RL2_ODRL_Mapping.md` defines the supported structures, required interpretation parameters,
preservation guarantees, and rejection diagnostics. Translation does not guess among materially
different meanings.

## Concurrency Boundary

`Eval` reads one immutable `WorldSnapshot`; it neither reserves resources nor commits an action.
A decision based on a shared quota or capacity fact is therefore a decision about that snapshot,
not an atomic admission guarantee. Systems that require check-and-reserve behavior must ensure
snapshot freshness and atomic enforcement outside RL2. **PEP guidance:** a PEP enforcing a quota
must serialize its own decrements (e.g. an atomic counter or a database transaction outside RL2);
`Eval` only reports the snapshot-time state and never itself reserves or decrements anything.

## Complexity and Constraints

*This section is non-normative.*

RL2 evaluation is designed to be **polynomial-time** and **total** under the following constraints.

### Conformance Parameters

The core's termination and polynomial-time guarantees depend on a small set of **conformance parameters** — named finite bounds a conforming implementation **MUST** enforce. Only the *values* are implementation- or profile-declared; the existence of each bound is mandatory, not a `MAY`. An implementation that omits any of these bounds is out of core conformance.

| Parameter | Default | Bounds |
|-----------|---------|--------|
| `MaxPathDepth` | 10 segments | `deref` path length |
| `MaxConditionDepth` | 20 | condition tree nesting; evaluation work is linear in tree size |
| `MaxCollectionSize` | implementation-declared | policy-declared sets and collections |
| `MaxSnapshotFacts` | implementation-declared | `|WorldSnapshot.facts|` |
| `MaxSnapshotEvidence` | implementation-declared | `|WorldSnapshot.evidence|` |
| `MaxPolicyUniverse` | implementation-declared | `|U|` |

### Structural Constraints

1. **Finite policy universe**: U is a finite set of policies (`≤ MaxPolicyUniverse`)
2. **Bounded condition nesting**: Conditions have bounded depth (`≤ MaxConditionDepth`, default 20)
3. **Acyclic conditions**: No self-referential condition definitions
4. **Finite snapshot**: facts and evidence satisfy their declared bounds
5. **No recursive policy references**: Policies cannot invoke evaluation of other policies

### Path Resolution Constraints

6. **Bounded path depth**: `≤ MaxPathDepth` (default 10), enforced by grammar
7. **No live traversal**: ordinary paths are exact fact-key lookups, not graph pattern matching
8. **No evaluator callback**: source access and derived-value computation occur before snapshot
   assembly
9. **Deterministic selection**: action evidence is selected by explicit clause-derived fields

### Complexity Analysis

*This subsection is non-normative accounting, not a new semantic claim.* It replaces a single
polynomial total with parameterized bounds so that the terms which dominate a realistic deployment
— windowed Maintenance Duties, shared-Duty status recomputation, hierarchy closures, profile
operators, and snapshot assembly — are named rather than folded into one opaque product.

**Parameters** (each bounded by a conformance parameter above, or declared by the compiled module):

| Parameter | Meaning |
|-----------|---------|
| `n_clauses` | Number of clauses (Privilege, Prohibition, Duty, Promise) in the policy universe (`≤ MaxPolicyUniverse × m`) |
| `n_cond` | Number of condition nodes (AtomicConstraint/LogicalConstraint) reachable from those clauses (`≤ MaxConditionDepth`-bounded per clause) |
| `n_facts` | Number of `WorldSnapshot.facts` referenced during one evaluation (`≤ MaxSnapshotFacts`) |
| `n_ev` | Number of `WorldSnapshot.evidence` items considered (`≤ MaxSnapshotEvidence`) |
| `n_hier` | Number of action/type hierarchy edges (`rl2:includedIn`, `rdfs:subClassOf`) in the compiled closure |
| `n_dep` | Number of edges in the finite `targetNorm`/`obligationStateOperand` status-dependency graph (acyclic by `StatusDependencyCycle`, `RL2_Compilation.md` §2.2) |
| `n_cells` | Number of temporal cells constructed for a windowed Maintenance Duty's invariant evaluation |

**(a) Direct evaluation is polynomial in these parameters.** The dominant terms:

| Operation | Complexity |
|-----------|------------|
| Per-clause condition evaluation | O(`n_cond` × fact-lookup-cost) — O(1) per lookup with a fact index, O(`n_facts`) without one |
| Evidence selection | O(`n_ev` × h), h a bounded action-hierarchy lookup (`h ≤ n_hier`) |
| Windowed Maintenance Duty evaluation | O(`n_cells` × `n_cond`) — the invariant condition is evaluated once per temporal cell, not once total |
| Status-dependency traversal | O(`n_dep`) to visit the acyclic `targetNorm` graph in dependency order |
| Norm matching | O(`n_clauses`) — `n_clauses` already totals clauses across the universe |
| Conflict resolution | O(k²) for `k` access atoms |

Shared-Duty and Promise status is computed **once per `(Duty, snapshot, configuration)`**, not once
per referencing clause: a conforming implementation memoizes status by the cache key `(Duty id,
module digest, snapshot digest, configuration digest)`, so a Duty gating ten Privileges or targeted
by ten `obligationStateOperand` conditions costs one status computation, not ten. The bounds above
state the **memoized** cost; naive per-reference recomputation is not the intended cost and is not
what these bounds describe.

**(b) Compile-time closure construction.** Action-inclusion and type/subclass closures
(`RL2_Compilation.md` §5, "Materialized closures") are computed once, at compile time, in O(`n_hier`)
space. Their size feeds evaluation only as a constant-time index lookup per condition or evidence
match; the closure-construction cost itself is amortized across every evaluation of the compiled
module, not paid per `Eval` call.

**(c) Profile-operator cost is outside core bounds.** A `rl2:ProfileOperator` (`RL2_Compilation.md`
§9.1) is required to be pure and total, but its cost is declared and accounted by the profile that
defines it, not by this section's parameters; core conformance makes no claim about a profile
operator's running time.

**(d) Snapshot assembly and universe selection are external and unbounded by core.** Constructing
`WorldSnapshot` and selecting the `PolicyUniverse` supplied to `Eval` are assembler responsibilities
(`RL2_Scope.md`, External Data) that occur before `Eval` is called; their cost — source fetching,
credential verification, connector execution, catalog/selection logic — is the assembler's, not
`Eval`'s, and is not bounded by any parameter in this section.

**(e) Total, for reference.** Folding (a) into one expression: `O(n_clauses × (n_cond ×
factLookup + n_ev × h + n_cells × n_cond) + n_dep + n_hier + k²)`, where the memoized status cost is
already counted once per distinct Duty rather than per reference. Indexes may reduce lookup cost
without changing meaning. Implementations may hash-index candidate norms by `(subject, action,
object)` for the fast bound-norm path; `rl2:anyAgent`/`rl2:anyAsset` sentinel-subject or
sentinel-object norms cannot key into that index and form a separate, always-scanned bucket.

### Totality Guarantees

Under these constraints, `Eval` is **total**: it terminates for all well-formed inputs. The function never:

- Loops infinitely (no recursive evaluation)
- Blocks on external resources (`Eval` performs no I/O; missing snapshot values produce `EvalError`)
- Diverges due to condition structure (bounded, acyclic)

Source fetching, credential verification, and connector execution are outside `Eval`. A deployment
completes them while constructing `WorldSnapshot`; their cost and termination are not included in
the evaluator bound.

---

## Proof scope and normative artifact

RL2 specifies the language, ODRL migration, and conformance, not an implementation or mechanized
proof. The normative artifacts are the core ontology and shapes, `RL2_Model.md`, this document,
`RL2_ODRL_Mapping.md`, and accepted conformance vectors.

Datatype and function definitions in this document use Dafny-like algebraic-datatype notation
purely as precise pseudocode. This is not a commitment to Dafny or any implementation language.

---

## Proof Obligations

The following are requirements on RL2 semantics:

1. **Determinism:** equal PolicyUniverse, Request, WorldSnapshot, and EvaluationConfiguration
   values produce equal EvaluationResults.
2. **Condition totality:** every well-formed condition produces `True`, `False`, or attributed
   `Unknown`; it neither throws nor silently drops an error.
3. **Projection determinism:** supported RDF input maps to one canonical AST; unsupported or
   ambiguous input produces a specified diagnostic.
4. **Status consistency:** a Duty or Promise receives one status for one semantic input; terminal
   outcomes cannot be simultaneously Fulfilled and Violated.
5. **Resolution completeness:** every finite attributed envelope, total Duty-status map, and
   supported configuration produces one Decision.
6. **Bounded totality:** `Eval` terminates for every well-formed input satisfying declared
   conformance bounds.

The semantic conformance vectors test these observable properties. A future reference evaluator
may add differential tests or mechanized proofs without changing the language contract.

For architecture and boundaries, see `../docs/RL2_Architecture.md`.

---

## References

See `../docs/RL2_References.md` for complete citations.

Related RL2 specifications:
- `rl2.ttl` — Core ontology (OWL)
- `rl2-shacl.ttl` — SHACL validation shapes
- `RL2_Model.md` — Request, WorldSnapshot, configuration, and result
- `RL2_ODRL_Mapping.md` — ODRL 2.2 translation and compatibility
- `../conformance/` — Structural and semantic conformance artifacts
