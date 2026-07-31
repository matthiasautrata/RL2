---
title: "RL2 Formal Semantics"
subtitle: "A Unified Normative, Operational, and Semantic Framework for Rights and Data Policies"
version: "0.6"
status: "Draft"
date: 2026-07-24
abstract: |
  RL2 is a normative and operational policy language designed as a rigorous successor to legacy rights languages, integrating deontic logic, promise theory, constraint algebra, and small-step operational semantics into a single, unified, formally grounded framework.
---

## Introduction

Digital policy frameworks often lack formal normative foundations and operational rigor. Legacy standards like ODRL 2.2 provide expressive vocabularies but leave semantics to interpretation, leading to inconsistent enforcement.

RL2 (“Rights Language 2”) addresses these limitations by integrating ideas from:

* **Deontic Logic**
* **DPCL (normative meta-language)**
* **Promise Theory**
* **ODRE (operational rights enforcement)**
* **Temporal Logic and Event Calculi**

RL2 is fully RDF-compatible, but its semantics are defined **at the abstract syntax level**, independent of serialization.

This document defines the formal semantics. For architectural design and rationale, see **RL2_Architecture.md**. For protocol details, see **RL2_Protocol.md**.

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
* **Σ** = system state
* **⊥** = legacy notation for an absent value; at an evaluator boundary it is
  `Err(Missing(ErrorKey), note)` in the Result and Truth Algebra below

We define RL2 expressions as:

#### Norms

```
Norm ::= 
    Privilege(Agent, Action, Asset, Condition)
  | Duty(Agent, Action, Asset, Condition; dutyMode: DutyMode?)
  | Prohibition(Agent, Action, Asset, Condition)
  | Claim(Agent subject, Agent counterparty, Duty correlativeTo)
      -- subject = right-holder, counterparty = duty-bearer; action/object/condition are
      -- DERIVED from correlativeTo (C6b), never authored — see Claim Denotation below.
      -- (F2/SEM-10: replaces a former `Right` field that was undefined anywhere in this
      -- document, absent from `ClaimShape`, and superseded by this one.)
  | Power(Agent, Norm affectsNorm, Condition?)
      -- optional Condition gates the Power's OWN activation (independent of affectsNorm's)
  | Liability(Agent, Power exposedTo)
      -- no own Condition: structurally derived from exposedTo's activation (F2/SEM-10;
      -- mirrors the Claim/Duty derivation pattern of C6b)
  | Immunity(Agent, Power immuneFrom, Condition?)
      -- optional Condition gates the Immunity's OWN activation, independent of immuneFrom's
```

The semicolon separates the Duty's optional normalized `dutyMode` field from its
normative action content. Equations that write `Duty(a,x,s,c)` omit this field when
it is irrelevant; `dutyMode(d)` below reads it and supplies the default.

#### Promises

```
Promise ::= Promise(Agent promisor, Agent promisee, PromiseContent)

PromiseContent ::=
    PromisedAction(Action, Asset)   -- Tun-sollen; from rl2:promisedAction + rl2:object
  | PromisedState(Condition)        -- Sein-sollen; from rl2:promisedState
  | PromisedDuty(Duty)              -- suretyship;  from rl2:promisedDuty
```

`PromiseContent` is a metalanguage tagged union mapping 1:1 to the three disjoint
ontology properties (`rl2:promisedAction`, `rl2:promisedState`, `rl2:promisedDuty`).
A well-formed Promise carries exactly one. (This replaces the former polymorphic
`rl2:promiseContent`/`rl2:PromiseContent` union, which allowed one intent to be
encoded several ways — see the canonical-form invariant.)

#### Conditions

```
Condition ::=
      AtomicConstraint(leftOperand, operator,
                       rightOperand : Literal | RuntimeReference,
                       targetNorm : StateTarget?)
    | And(Condition{2,})
    | Or(Condition{2,})
    | Xone(Condition{2,})
    | Not(Condition)
    | EventConstraint(expectsEvent: Event)
```

Notes:
- `And`, `Or`, and `Xone` take at least two conditions, matching
  `AndOrXoneOperandCardinalityShape`
- `EventConstraint` models approval requirements; holds when the expected event is present in Σ.Events
- `leftOperand` is drawn from profile-defined operands (RL2 Core defines `rl2:LeftOperand` class plus `currentDateTime`, `obligationStateOperand`, `dutyPerformerOperand`, `promiseStateOperand`, `promisorOperand` instances)
- Time-based conditions use `AtomicConstraint` with `leftOperand = currentDateTime` (e.g., `currentDateTime lte deadline`)
- Dynamic value resolution on the left side uses `LeftOperand` with `resolutionPath`
- Dynamic value resolution on the right side uses `RuntimeReference` (e.g., `currentAgent`)
- The stable RDF property `rl2:targetNorm` is interpreted as the tagged `StateTarget` defined
  below, preserving whether it references a Norm or a Promise

#### Events and Transitions

```
Event ::= event(eventType, payload)

StateTransition ::=
    Activate(Norm)
  | Fulfill(Duty)
  | Violate(Duty)
  | FulfillPromise(Promise)
  | Trigger(Event)
```

#### Policies

```
Clause ::= Norm | Promise      -- mirrors rl2:Clause; only an Offer admits a Promise clause

Policy ::= Policy {
  condition : Condition?,   -- optional policy-level activation condition
  clauses   : Clause+,      -- non-empty, matching PolicyShape
  meta      : Metadata
}
```

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
τ ::= Agent | Action | Asset | Condition | Time | Boolean | Norm | Promise | Event | State
```

### Key Typing Rules

Privilege:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset     Γ ⊢ c : Condition
---------------------------------------------------------------------------
       Γ ⊢ Privilege(a, x, s, c) : Norm
```

Duty:

```
Γ ⊢ a : Agent     Γ ⊢ x : Action     Γ ⊢ s : Asset
Γ ⊢ c : Condition
--------------------------------------------------------------------------
        Γ ⊢ Duty(a, x, s, c) : Norm
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
Γ ⊢ p : Agent   Γ ⊢ q : Agent   Γ ⊢ content : PromiseContent
-------------------------------------------------------------
       Γ ⊢ Promise(p, q, content)
```

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

### States

A state Σ contains:

* asset metadata
* event log
* action log
* temporal clock
* promise records (including status, promisor/promisee, content)
* duty states

Formally:

```
Σ = (Clock : T,
     Events : EventLog,                          -- APPEND-ONLY authoritative witness log (S6)
     Metadata : S → Map,
     Promises : Promise → PromiseRecord,
     ObligationState : Duty → {Pending, Active, Fulfilled, Violated},
     Requirements : RequirementID → RequirementRecord)

EventLog = E*  indexed by kind (Events : EventType → E*), append-only, every e carrying a
               unique total-order e.eventSequence

EventRecord = (id        : IRI,        -- the event's IRI, its stable identifier
               eventSequence : ℕ,       -- total order, assigned on append; the tie-breaker
               eventTime : T,           -- coarse temporal order
               kind      : EventKind,   -- an individual of rl2:Event; subsumption via eventKindIncludedIn*
               operationalAgent : Agent,-- the performer
               eventAction : Action?,   -- for ActionPerformed events
               eventObject : Resource?, -- for ActionPerformed events
               case      : Case?,       -- rl2p:affectsCase scope
               provenance : IRI?)       -- prov:wasDerivedFrom

PromiseRecord = (promisor : Agent,
                 promisee : Agent,
                 content : PromiseContent,
                 state : PromiseState)

RequirementRecord = (sourceNorm   : Duty | Promise,  -- rl2p:sourceNorm; provenance
                     trackedDuty  : Duty?,            -- the Duty whose ObligationState drives
                                                       -- status (see Requirement Status Derivation)
                     sourcePolicy : Policy,
                     counterparty : Agent?,
                     imposedTime  : T)
```

**`Performed` and `DutyPerformer` are DERIVED, not stored (S6).** They are *views* over the
append-only `Σ.Events`, never an independent Boolean/agent truth source that could drift from the
witness log — see *Witness Derivation* below. The earlier "record a Boolean on performance"
model is withdrawn.

Notes:
- `PromiseState(p, Σ)` is the derived promise state (see Promise State Derivation). For standalone promises, it coincides with the stored `Σ.Promises[p].state`.
- `RequirementRecord` does **not** carry a stored `status` field. `rl2p:requirementStatus` (protocol/RDF surface) is the projection `requirementStatus(req, Σ, Env)` — see *Requirement Status Derivation* — computed from `Σ.ObligationState`/`PromiseState`, using the same `rl2:ObligationState` individuals (`Pending`, `Active`, `Fulfilled`, `Violated`) defined in the Vocabulary. This mirrors S6's treatment of `Performed`/`DutyPerformer`: no independent store that could drift from the authoritative model (F3).
- `ObligationState` is the canonical name (matching `rl2:ObligationState` in the ontology).
- PromiseState values (`Pending`, `Fulfilled`, `Violated`) reuse the shared state individuals defined in the Vocabulary (promises do not use `Active`).
- `DutyPerformer(d, Σ)` — **derived** (S6) from the witnessing event, returns `⊥` if the duty has not been fulfilled. Enables identity binding patterns:
  - *Tun-sollen* (ought-to-do): `DutyPerformer(d) = currentAgent` — the same agent must fulfill
  - *Sein-sollen* (ought-to-be): Check only `ObligationState(d) = Fulfilled` — anyone may fulfill
  - *Separation of Duty*: `DutyPerformer(d) ≠ currentAgent` — a different agent must fulfill

**Event Log Structure** (normative):

`Σ.Events` is an **append-only witness log** presented as a typed index: a map from event kind
to the events of that kind. Each event carries a unique total-order `eventSequence` assigned when
it is appended. Selection orders **lexicographically by `(eventTime, eventSequence)`** — `eventTime`
is the coarse temporal order and `eventSequence` is the **total tie-breaker**, so selection is
deterministic even when timestamps tie.

```
Events : EventType → E*
Events[kind] = [e₁, e₂, ..., eₙ]  ordered by (eventTime, eventSequence)
```

Path access semantics (normative) — `maxByⁱ` = the maximum under the `(eventTime, eventSequence)`
lexicographic order (S6):

```
state.Events.<kind>           ≡  maxByⁱ(Events[kind])  or ⊥ if empty
state.Events.<kind>.<prop>    ≡  (maxByⁱ(Events[kind])).<prop>
state.Events.*                ≡  maxByⁱ(⋃ Events[k] for all k)
```

Because `eventSequence` is a **total** order, this "most-recent-wins" selection is a total
function with no residual nondeterminism (the earlier `maxBy(eventTime)` could tie; S6 fixes it).

This model supports both:
- **Named event access**: `state.Events.breakGlassEvent.operationalAgent`
- **Pattern-based selection**: via EventConstraint + wildcard paths

**Scope of Σ**: In practice, Σ represents the *evidence log* or *relevant history* for a given evaluation context—not a theoretically omniscient record of all actions ever performed. Implementations scope Σ to the Case being evaluated (see RL2_Protocol.md), tracking only events and actions relevant to that access request's lifecycle.

### Environments

```
Env = (Request, Agent, Asset, Σ, Context)
```

A named five-field record (not a bare product), used for evaluating operand paths.
The fields correspond one-to-one with the canonical path roots (`request.*`,
`agent.*`, `asset.*`, `state.*`, `context.*`):

- `Request` — the `rl2p:Request` being evaluated
- `Agent`   — the requesting agent (`Request.requestingAgent`; what `rl2:currentAgent` resolves to)
- `Asset`   — the requested asset
- `Σ`       — system state (the `state.*` root)
- `Context` — external request context

Including `Request` resolves the prior inconsistency where `deref` dereferenced
`Env.Request` while `Env` was declared without it.

---

## Denotational Semantics

Denotational semantics gives timeless meaning to norms and conditions.

### Result and Truth Algebra (S2)

Operand resolution and condition evaluation are **partial** — an operand may be missing,
wrong-typed, multi-valued, or fail to resolve. RL2 makes this total with typed carriers shared
by the denotational semantics and the IR (`RL2_IR.md`). Projection of structured causes into
the protocol is the separate C3-6/D10 work item; the current protocol carries the
`rl2p:Indeterminate` decision but not its causal detail.

```
StateTarget  = NormTarget(Norm) | PromiseTarget(Promise)

ErrorSite    = LeftOperand | RuntimeReference | Path
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
`Unknown`:** `apply(operator, l, r)` is called, and its `True`/`False` result trusted, only when
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
reports `Indeterminate` rather than silently choosing. `rl2p:Indeterminate` carries that decision;
the structured causal projection remains C3-6/D10.

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
         Literal(v)    → Ok(v)
     in case (leftEV, rightEV) of
         (Ok(l), Ok(r)) | typeCompatible(operator, l, r) →
             { truth: apply(operator, l, r), causes: ∅ }
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
ordered(v)       = valueType(v) ∈ {Int, Decimal, DateTime, Duration}
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
`StateTarget`: `NormTarget` for Duty state/performer queries and `PromiseTarget` for Promise
state/promisor queries. The right operand may be a literal value or a runtime reference (e.g.,
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

Event constraint (approval requirement) — a total Σ query, so `True`/`False` only (absence is `False`, not `Unknown`, and therefore never contributes a cause):

```
⟦ EventConstraint(expectsEvent) ⟧(Env) : ConditionResult =
    { truth: True,  causes: ∅ }  if ∃e ∈ Env.Σ.Events : matches(e, expectsEvent)
    { truth: False, causes: ∅ }  otherwise
```

---

### Helper Function Specifications

The condition semantics rely on several helper functions. For a testable evaluator, these must be precisely specified.

#### resolve : LeftOperand × Env × StateTarget? → EvalValue\<Value\>

The function `resolve(leftOperand, Env, targetNorm?)` maps a left operand to an
`EvalValue<Value>` (S2): `Ok(v)` on success and `Err(error,note)` on failure. Although the RDF
property keeps its stable name `rl2:targetNorm`, the semantic parameter is a `StateTarget?` and
therefore preserves whether the referenced clause is a Norm or a Promise.

**Resolution Precedence**: Operands are resolved in the following order:

1. **Core operands** (obligationStateOperand, dutyPerformerOperand, promiseStateOperand, promisorOperand) — handled specially
2. **Path-based resolution** — if `op.resolutionPath` is defined, use `deref()`
3. **Function-based resolution** — if `op.resolutionFunction` is defined, invoke it
4. **External lookup** — fallback to context-based resolution

```
resolve : LeftOperand × Env × StateTarget? → EvalValue<Value>

failure(kind, site, target, note) =
    Err(kind({ site: site, target: target }), Some(note))

resolve(op, Env, targetNorm) =
    case op of
        -- Core operands (norm state queries)
        obligationStateOperand →
            case targetNorm of
                Some(NormTarget(d : Duty)) → Ok(Env.Σ.ObligationState(d))
                None → failure(Missing, op, None, "obligationStateOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "obligationStateOperand requires a Duty target")
        dutyPerformerOperand →
            case targetNorm of
                Some(NormTarget(d : Duty)) →
                    let performer = DutyPerformer(d, Env.Σ) in   -- derived from witness log (S6)
                    if performer ≠ ⊥ then Ok(performer)
                    else failure(Missing, op, targetNorm, "no witnessing event yet")
                None → failure(Missing, op, None, "dutyPerformerOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "dutyPerformerOperand requires a Duty target")
        promiseStateOperand →
            case targetNorm of
                Some(PromiseTarget(p)) → Ok(PromiseState(p, Env.Σ))
                None → failure(Missing, op, None, "promiseStateOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "promiseStateOperand requires a Promise target")
        promisorOperand →
            case targetNorm of
                Some(PromiseTarget(p)) →
                    let promisor = Env.Σ.Promises[p].promisor in
                    if promisor ≠ ⊥ then Ok(promisor)
                    else failure(Missing, op, targetNorm, "no promisor bound")
                None → failure(Missing, op, None, "promisorOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "promisorOperand requires a Promise target")

        -- Profile-declared operands with explicit resolution
        _ | op.resolutionPath ≠ ⊥ →
            deref(op.resolutionPath, Env)               -- : EvalValue<Value>

        _ | op.resolutionFunction ≠ ⊥ →
            invokeFunction(op.resolutionFunction, Env)   -- : EvalValue<Value>, implementation-specific

        -- Legacy/fallback resolution
        _  → lookupExternal(op, Env.Context)             -- : EvalValue<Value>
```

Where:
* `obligationStateOperand` accepts `NormTarget(d : Duty)` and queries `Σ.ObligationState(d)`
* `dutyPerformerOperand` accepts `NormTarget(d : Duty)` and returns `DutyPerformer(d,Σ)`
* `promiseStateOperand` accepts `PromiseTarget(p)` and returns `PromiseState(p,Σ)`
* `promisorOperand` accepts `PromiseTarget(p)` and returns `Σ.Promises[p].promisor`
* `op.resolutionPath` — path expression declared on the operand via `rl2:resolutionPath`
* `op.resolutionFunction` — function name declared on the operand via `rl2:resolutionFunction`
* `invokeFunction(name, Env)` — implementation-specific function invocation; MUST return `EvalValue<Value>`
* `lookupExternal(op, Ctx)` — resolves operands from external context (HR systems, directories, etc.); MUST return `EvalValue<Value>`
* `Err(Missing(key),note)` indicates the operand could not be resolved (S2) — never fatal,
  always lifted to `Unknown` at the condition level; a present target of the wrong variant is
  `Err(Invalid(key),note)` instead

**Architectural Principle**: All runtime and contextual data access SHOULD go through declared `rl2:LeftOperand` instances with explicit `rl2:resolutionPath` or `rl2:resolutionFunction`. This ensures:
- Type safety (operands can declare expected ranges)
- Validation (SHACL can verify operand usage)
- Specifiability (clear mapping to a precise, testable evaluator design)
- Auditability (all data access points are declared)

RL2 Core defines the following left operand instances:
* `obligationStateOperand` → queries duty state from Σ (requires `targetNorm`)
* `dutyPerformerOperand` → queries who fulfilled a duty from Σ (requires `targetNorm`)
* `promiseStateOperand` → queries promise state from Σ (requires a Promise-valued `targetNorm`)
* `promisorOperand` → queries who is bound by a promise from Σ (requires a Promise-valued `targetNorm`)

Profiles define domain-specific left operands with resolution paths, such as:
* `purpose` → `rl2:resolutionPath "context.purpose"`
* `dataOwner` → `rl2:resolutionPath "asset.dataOwner"`
* `eventPerformer` → `rl2:resolutionPath "state.Events.*.operationalAgent"`
* `department` → `rl2:resolutionFunction "lookupDepartment"`

#### Runtime References

Runtime references resolve to values at evaluation time. These are used in `rightOperandRef` for dynamic comparisons.

```
resolveRuntime : RuntimeReference × Env → EvalValue<Value>

resolveRuntime(ref, Env) =
    case ref of
        currentAgent → Ok(Env.Agent)
        _            → failure(Missing, ref, None, "unrecognized runtime reference")
```

The `currentAgent` reference resolves to `Env.Agent` — the agent making the current request. This is used in `rightOperandRef` to compare against `dutyPerformerOperand` for identity binding.

**Security Note**: When `leftOperand` is a dynamic operand like `dutyPerformerOperand`, `rightOperandRef` SHOULD be a `RuntimeReference` (e.g., `currentAgent`), not a static IRI. Hardcoded comparisons like `dutyPerformerOperand eq ex:Bob` bypass dynamic binding semantics and create security vulnerabilities. SHACL validation flags such patterns as warnings.

#### Profile Resolution (O3)

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

#### deref : Path × Env → EvalValue\<Value\>

The function `deref(path, Env)` traverses a path expression to retrieve a value, returning
`Ok(v)` or `Err(Missing(key),note)` (S2). This is the **primary mechanism for resolving
profile-declared operands** via `rl2:resolutionPath`.

**Path Grammar** (normative):

All path expressions MUST conform to the following grammar:

```
Path       ::= Root ('.' Segment)*
Root       ::= 'agent' | 'asset' | 'context' | 'state' | 'request' | 'global'
Segment    ::= Identifier | Wildcard
Identifier ::= [a-zA-Z_][a-zA-Z0-9_]*
Wildcard   ::= '*'
```

Constraints:
- Paths MUST begin with a valid Root
- The Wildcard `*` is ONLY valid immediately after `Events` (i.e., `state.Events.*`)
- Identifiers MUST NOT contain `.`, `/`, `..`, or URL-encoded characters
- Maximum path depth: conformance parameter `MaxPathDepth` (default 10 segments). A conforming implementation **MUST** enforce a finite bound; only the value is implementation/profile-declared (S8a — the bound is mandatory, not `MAY`).

Paths not conforming to this grammar MUST be rejected at parse time, not at evaluation time. This ensures that malformed paths cannot be used to probe for valid segments.

**Security Requirement: Path Sandboxing**

Implementations MUST enforce a strict sandbox for `deref` operations. The evaluator MUST reject any path that:

1. Contains directory traversal sequences (e.g., `..`, `/`, `\`)
2. References roots other than the canonical set (`agent`, `asset`, `context`,
   `state`, `request`, `global`)
3. Contains URL-encoded characters or escape sequences
4. Attempts to access host system variables or environment settings not explicitly mapped to the `Env` object

Rationale: Without these constraints, a malicious path like `state.Events.../../private/key` could escape the policy evaluation sandbox and access host system resources. Path validation MUST occur at parse time to prevent timing-based probing attacks.

**Canonical Path Roots** (normatively defined):

| Root | Meaning | Example Paths |
|------|---------|---------------|
| `agent` | Env.Agent (requesting agent) | `agent.department`, `agent.clearanceLevel` |
| `asset` | Env.Asset (requested asset) | `asset.classification`, `asset.dataOwner` |
| `state` | Σ (system state) | `state.Clock`, `state.Events.BreakGlassEvent.operationalAgent` |
| `context` | External request context | `context.purpose`, `context.jurisdiction` |
| `request` | rl2p:Request fields | `request.requestTime`, `request.requestingAgent` |
| `global` | Offer-tier resolved snapshot (shared across acceptances of one Offer; S5) | `global.activeSessions.count` |

```
deref : Path × Env → EvalValue<Value>

deref(path, Env) =
    let segments = split(path, '.')
    let root = case head(segments) of
        "agent"   → Env.Agent
        "asset"   → Env.Asset
        "context" → Env.Context
        "state"   → Env.Σ
        "request" → Env.Request
        "global"  → Env.Context.global   -- S5: Offer-tier snapshot, injected by the resolver (see below)
        _         → ⊥
    let result = foldl(navigate, root, tail(segments))
    in if result ≠ ⊥ then Ok(result)
       else failure(Missing, path, None, "path root or segment not present")

navigate(obj, segment) =              -- internal traversal stays ⊥-based; deref lifts the boundary result
    case obj of
        ⊥       → ⊥
        Record  → obj.segment if segment ∈ fields(obj) else ⊥
        Map     → obj[segment] if segment ∈ keys(obj) else ⊥
        _       → ⊥
```

**The `global` root (S5).** `global.*` reads the **Offer tier** — state shared across every
Agreement materialized from one Offer (the "class variable" of §State Scope, Identity, and
Concurrency). Its values are **resolved into a reserved `global` subtree of the immutable
`ResolvedContext`** by the evaluator's resolution phase *before* evaluation (the same
E1/SEM-13 contract that resolves external context), which is why the pure core simply derefs it
like any other context value — it does not itself walk the Agreement graph. Global reads are
**read-only aggregates** over the Offer's active Agreements (e.g. a live-seat count); computing
them is a resolver responsibility **outside the specified evaluator core**, on the same footing as an
aggregating `rl2:resolutionFunction` (S8a). Profiles declare `global.*` operands as
`rl2p:GlobalLeftOperand` individuals.

`Σ.Events` is indexed **by event type** (keyed by the event type IRI), each mapping to a time-ordered sequence of event instances of that type. The path segment immediately after `Events` MUST be that type key (e.g., `BreakGlassEvent`). Using an instance identifier there will yield `⊥` under these rules. To distinguish multiple events of the same type, add distinguishing properties in the `EventConstraint`; the selection rule then picks the most recent event of that type that matches those properties.

**Event Access Pattern**: To access properties of events in Σ.Events, use paths like:
- `state.Events.BreakGlassEvent.operationalAgent` — specific event type key
- `state.Events.*.operationalAgent` — wildcard (see selection rules below)

**Wildcard Selection Rules** (normative):

The wildcard `*` is permitted ONLY in the pattern `state.Events.*` and MUST be accompanied by an `EventConstraint` in the same `LogicalConstraint`. This ensures deterministic, auditable event selection.

When a path contains `state.Events.*`, the following selection rules apply:

1. **EventConstraint requirement**: The `LogicalConstraint` containing the wildcard path MUST include an `EventConstraint` specifying the expected event type. Wildcards without a sibling `EventConstraint` SHOULD be flagged as a validation warning (implementations MAY treat as error).

2. **Selection is singular**: Wildcards always resolve to a single value, not a set. This ensures `deref` remains a total function over allowed paths.

3. **Precedence**: Among events matching the `EventConstraint`:
   - The most recent under the `(eventTime, eventSequence)` lexicographic order is selected — `eventSequence` breaks `eventTime` ties (S6)
   - If no events match, returns ⊥

Formally:
```
navigate(Events, "*", constraintInScope) =
    require constraintInScope ≠ ⊥  -- EventConstraint must be present
    let candidates = { e ∈ Events | matches(e, constraintInScope.expectsEvent) }
    in if candidates = ∅ then ⊥
       else maxByⁱ(candidates)      -- max under (eventTime, eventSequence); total, deterministic
```

**Rationale**: Requiring an `EventConstraint` sibling eliminates ambiguity about which event the wildcard selects. Without this constraint, `state.Events.*.operationalAgent` could return the performer of *any* recent event, creating security vulnerabilities in identity-binding patterns.

This rule ensures that identity binding patterns like:
```
rl2:leftOperand emergency:eventPerformerOperand ;  # resolutionPath "state.Events.*.operationalAgent"
```
correctly resolve to the performer of the **triggering event** specified by the accompanying `EventConstraint`.

**Security Requirements** (normative):

Implementations MUST enforce the following security constraints:

1. **Root validation**: Reject paths not starting with a canonical root (`agent`,
   `asset`, `context`, `state`, `request`, `global`)
2. **Grammar validation**: Reject paths containing `..`, `/`, `%`, or other traversal/encoding patterns
3. **Wildcard restriction**: Reject `*` in any position other than immediately after `state.Events`
4. **Depth limiting**: **MUST** reject paths exceeding `MaxPathDepth` (conformance parameter, default 10). The bound is mandatory; only its value is implementation/profile-declared (S8a).
5. **Fail-closed**: Reject syntactically invalid paths at policy load. For a
   syntactically valid path whose selected field or value is absent at evaluation,
   return `Err(Missing(key),note)` without exposing host details.

These constraints prevent path traversal attacks and unauthorized data access via malformed resolution paths.

Example paths:
* `agent.department` → the agent's department
* `asset.classification` → the asset's classification level
* `context.purpose` → the declared purpose from request context
* `state.Clock` → current system time
* `state.Events.BreakGlassEvent.operationalAgent` → performer of the most recent break-glass event

#### matches : Event × EventPattern → Boolean

The function `matches(e, pattern)` checks if an event matches an expected pattern. An `EventPattern` is simply an `Event` instance used as a template—the actual event must have the same type (or subtype) and all properties specified in the pattern (e.g., `rl2:approver`):

```
matches : Event × EventPattern → Boolean

matches(e, pattern) =
    typeMatches(e.kind, pattern.kind) ∧
    payloadMatches(e.payload, pattern.payload)

typeMatches(actual, expected) =
    actual = expected ∨ reachable(actual, rl2:eventKindIncludedIn, expected)
    -- S6: individual-level event-kind subsumption (eventKindIncludedIn*), NOT rdfs:subClassOf.
    -- Same bounded-traversal shape as action subsumption; no OWL class reasoning.

payloadMatches(actual, expected) =
    ∀(k, v) ∈ expected : k ∈ actual ∧ valueMatches(actual[k], v)

valueMatches(actual, expected) =
    case expected of
        Literal(v)   → actual = v
        Pattern(p)   → actual matches p
        Any          → true
```

#### contentHolds : Agent × PromiseContent × State → Boolean

The function `contentHolds(promisor, content, Σ)` checks if promise content is
satisfied. The action case is evaluated against the promisor (the committed
actor) and reuses the subsumption-aware `performed()` helper:

```
contentHolds : Agent × PromiseContent × State → Boolean

contentHolds(promisor, content, Σ) =
    case content of
        PromisedAction(x, s)  → performed(promisor, x, s, Σ)
        PromisedState(c)      → ⟦c⟧(mkEnv(nullRequest, Σ, emptyContext)).truth = True
                                 -- Unknown reads as not-yet-holding here (SEM-11 open scope governs
                                 -- nullRequest itself; this is only the mechanical ConditionResult
                                 -- projection needed to keep contentHolds Boolean)
        PromisedDuty(d)       → Σ.ObligationState(d) = Fulfilled
```

#### dutyMode : Duty → DutyMode

The function `dutyMode(d)` selects which ObligationState transition discipline
governs duty `d` (S4) — **Achievement** (fulfilled once by a single qualifying witness
before a deadline; violated only when that deadline expires unfulfilled) or
**Maintenance** (violated on the first witnessed counterexample while active; fulfilled
only when a finite monitoring period closes with no counterexample). It is total: a
crystallized duty carries the mode `crystallize` derived from its source Promise's
content shape (below); a directly authored duty may state `rl2:dutyMode` explicitly;
absent either, the duty defaults to Achievement — the discipline every Duty followed
before this distinction existed, so pre-existing Duties with no `rl2:dutyMode` triple
are unaffected:

```
dutyMode : Duty → DutyMode

dutyMode(d) =
    case d.dutyMode of
        Some(m) → m
        None    → Achievement
```

#### TimeBound and expiry

A `TimeBound` pairs an instant with the strictness of the comparison that produced it,
so an `lt` bound and an `lte` bound at the same instant expire at different clock
readings — the distinction the former `Σ.Clock > t` check collapsed:

```
TimeBound ::= Bound(t: T, inclusive: Boolean)   -- inclusive = true for `lte`, false for `lt`

expired : TimeBound × T → Boolean

expired(Bound(t, inclusive), now) =
    if inclusive then now > t     -- `currentDateTime lte t`: still satisfiable at now = t
    else          now ≥ t         -- `currentDateTime lt t`:  already false at now = t
```

#### extractDeadline : Condition → TimeBound?

`extractDeadline(c)` is **deliberately partial**. It recognizes exactly one canonical
upper-bound leaf — `AtomicConstraint(currentDateTime, lte, t)` or
`AtomicConstraint(currentDateTime, lt, t)` with a static (literal, not
`RuntimeReference`-valued) `t` — reachable through a top-level conjunction, and returns
`None` for anything it cannot prove is a single, unambiguous upper bound: `Or`, `Not`,
`Xone`, more than one recognized bound within an `And`, non-`currentDateTime`
comparisons, or a dynamic `t`. This replaces the former `min`/`max` synthesis over `And`
and `Or`, which guessed a bound for arbitrary boolean structure rather than proving one
exists. A temporal comparison inside a general `Condition` is not automatically a
temporal window: the raw condition language remains fully usable for activation and
guards (`⟦c⟧`), but `deadlinePassed` may only consume this deliberately narrow,
proven-safe fragment. `rl2:currentDateTime rdfs:range xsd:dateTimeStamp` (rl2.ttl)
guarantees a recognized `t`, once extracted, carries a timezone-qualified total order —
a bare `xsd:dateTime` without a timezone offset does not, and `rl2:OperandRangeTypeShape`
warns if a compared literal's datatype does not match.

```
extractDeadline : Condition → TimeBound?

extractDeadline(c) = case recognizedBounds(c) of
    {b} → Some(b)    -- exactly one recognized upper-bound leaf
    _   → None        -- zero, or more than one (ambiguous) — no synthesis

recognizedBounds(c) = case c of
    AtomicConstraint(currentDateTime, lte, t) where static(t)  → { Bound(t, true) }
    AtomicConstraint(currentDateTime, lt, t)  where static(t)  → { Bound(t, false) }
    And(cs)                                                    → ⋃_{c' ∈ cs} recognizedBounds(c')
    _  -- other AtomicConstraint, Or, Not, Xone, EventConstraint → {}
```

#### timeout : Condition × State → Boolean

```
timeout : Condition × State → Boolean

timeout(c, Σ) =
    case extractDeadline(c) of
        None    → false
        Some(b) → expired(b, Σ.Clock)
```

#### deadline : PromiseContent × State → TimeBound?

The function `deadline(content, Σ)` extracts any temporal bound on promise content:

```
deadline : PromiseContent × State → TimeBound?

deadline(content, Σ) =
    case content of
        PromisedAction(x, s)  → None                        -- Raw actions have no inherent deadline
        PromisedDuty(d)       → extractDeadline(d.condition)
        PromisedState(c)      → extractDeadline(c)
```

For evaluation, deadline expiry is checked via:

```
deadlinePassed(content, Σ) =
    case deadline(content, Σ) of
        None    → false
        Some(b) → expired(b, Σ.Clock)
```

This predicate is used in the Promise Violation rule to determine when a pending promise has exceeded its temporal bounds without fulfillment.

#### apply : Operator × Value × Value → Boolean

The function `apply(op, left, right)` applies a comparison operator to two **already-resolved,
already type-compatible** values — the `AtomicConstraint` denotation (§Conditions) is the only
caller, and it calls `apply` only after `typeCompatible(operator, left, right)` holds; a
domain mismatch is caught there and surfaced as `Invalid`, never passed into `apply`:

```
apply : Operator × Value × Value → Boolean

apply(op, left, right) =
    case op of
        eq       → left = right
        neq      → left ≠ right
        lt       → left < right
        lte      → left ≤ right
        gt       → left > right
        gte      → left ≥ right
        isA      → left ∈ instancesOf(right)
        isAnyOf  → valuesOf(left) ∩ elements(right) ≠ ∅
        isAllOf  → elements(right) ⊆ elements(left)
        isNoneOf → valuesOf(left) ∩ elements(right) = ∅

valuesOf(VSet(xs)) = set(xs)
valuesOf(v)         = {v}       -- admitted only for scalar v by typeCompatible
elements(VSet(xs))  = set(xs)   -- called only after typeCompatible established VSet
```

---

## Denotational Semantics for Norms

Norms are evaluated in the context of a **Request** `R = (a_req, x_req, s_req)` specifying the requesting agent, requested action, and target asset. The denotation takes both the request and an environment constructed from it.

### Environment Construction

Given a Request `R = (a_req, x_req, s_req)`, state `Σ`, and external context `Ctx`:

```
mkEnv(R, Σ, Ctx) = (R, a_req, s_req, Σ, Ctx)   -- (Request, Agent, Asset, Σ, Context)
```

The environment `Env = (Request, Agent, Asset, Σ, Context)` (see *Environments* above)
provides the evaluation context for conditions; `mkEnv` retains the full `Request` so
`request.*` paths resolve.

### Request Matching

A norm applies to a request only if the norm's subject, action, and object match the request:

```
matches(Norm(a, x, s, c), R) =
    (a = a_req ∨ a ∈ roles(a_req)) ∧
    (x = x_req ∨ x_req ⊑ x) ∧
    (s = s_req ∨ s_req ∈ members(s))
```

Where:
- `roles(a_req)` returns role memberships of the agent
- `x_req ⊑ x` indicates action subsumption (e.g., `read ⊑ access`)
- `members(s)` returns the **direct** `rl2:member` individuals of `s` when `s` is an `AssetCollection` (empty otherwise), evaluated against the evaluation snapshot

> **C7 — collections are assets, membership is direct.** `AssetCollection ⊑ Asset`, so a norm may target a collection directly (`s = s_req` matches when the request is *for* the collection) and a collection may itself appear as an `rl2:member` of another collection. Core `members(s)` is **not** transitively closed: if `s_req` is a member of a sub-collection nested inside `s`, that does **not** match in core. Flattening nested collections is a profile/derived concern layered on top of this direct-membership base. Membership is read from the fixed evaluation snapshot, so a norm's asset extension is stable for the duration of an evaluation.

Action subsumption is defined by the transitive closure of `rl2:includedIn`:

```
x' ⊑ x  :=  reachable(x', rl2:includedIn, x)
```

Evaluators MUST support transitive traversal of `rl2:includedIn`. In SPARQL, this is `ASK { ?x' rl2:includedIn* ?x }`. Usage of `rdfs:subClassOf` for action refinement is non-normative in RL2.

Action subsumption applies uniformly across all norm types: request matching, duty fulfillment, and prohibition violation checks. The subsumption-aware performed check is **derived from the witness log** (S6):

```
performed(a, x, s, Σ) :=
    ∃ e ∈ Σ.Events : kind(e) ⊑ₑ ActionPerformed
                     ∧ e.operationalAgent = a
                     ∧ e.eventObject = s
                     ∧ (e.eventAction = x ∨ e.eventAction ⊑ x)
    where ⊑ₑ is eventKindIncludedIn* and ⊑ is action includedIn*
```

`performed()` is thus a query over the append-only `Σ.Events` — there is no separate
`Σ.Performed` Boolean to keep in sync (S6). It is the same bounded graph traversal as request
matching — no additional reasoning complexity.

#### Witness Derivation (S6)

`Performed` and `DutyPerformer` are **derived views** over `Σ.Events`; the witnessing event is the
single source of truth for who did what, and (crucially) `DutyPerformer` reads its agent from that
witness rather than from a separately-recorded value:

```
witness(d, Σ) =
    let cand = { e ∈ Σ.Events | kind(e) ⊑ₑ ActionPerformed
                                ∧ e.eventAction ⊑ d.action ∧ e.eventObject = d.object }
    in if cand = ∅ then ⊥ else maxByⁱ(cand)     -- latest by (eventTime, eventSequence): total, deterministic

DutyPerformer(d, Σ) =
    let w = witness(d, Σ) in if w = ⊥ then ⊥ else w.operationalAgent
```

Because `maxByⁱ` uses the total `eventSequence` tie-breaker, `witness` (and hence `DutyPerformer`)
is deterministic even when two candidate events share an `eventTime`.

**RDF grounding**: Actions are individuals of `rl2:Action`. Action subsumption (`x' ⊑ x`) follows the transitive closure of `rl2:includedIn`; `members(s)` is the set of **direct** `rl2:member` links when `s` is an `rl2:AssetCollection` (not transitively closed — nested-collection flattening is a profile/derived concern, C7); and `roles(a_req)` derives from the agent's RDF typing/role assignments as defined in the Agent and role classes in the Vocabulary.

### Norm Denotations

Each activation is now three-way on the condition's `Truth` (S2): `True` activates the norm,
`False` leaves it `Inactive`, and **`Unknown` yields `Indeterminate`** — a matched norm whose
condition could not be evaluated is surfaced, never silently dropped. Matching itself is total
(`matches` is a structural equality/subsumption check that cannot error).

Privilege activation:

```
⟦Privilege(a,x,s,c)⟧(R, Env) =
    Permit         if matches(Privilege(a,x,s,c), R) ∧ ⟦c⟧(Env).truth = True
    Indeterminate  if matches(Privilege(a,x,s,c), R) ∧ ⟦c⟧(Env).truth = Unknown
    Inactive       otherwise   -- no match, or ⟦c⟧(Env).truth = False
```

Prohibition activation:

```
⟦Prohibition(a,x,s,c)⟧(R, Env) =
    Deny           if matches(Prohibition(a,x,s,c), R) ∧ ⟦c⟧(Env).truth = True
    Indeterminate  if matches(Prohibition(a,x,s,c), R) ∧ ⟦c⟧(Env).truth = Unknown
    Inactive       otherwise
```

Duty activation:

```
⟦Duty(a,x,s,c)⟧(R, Env) =
    Obligation(a,x,s)  if matches(Duty(a,x,s,c), R) ∧ ⟦c⟧(Env).truth = True
    Indeterminate      if matches(Duty(a,x,s,c), R) ∧ ⟦c⟧(Env).truth = Unknown
    Inactive           otherwise
```

Promise status:

```
⟦Promise(p,q,content)⟧(Env) =
    Fulfilled if contentHolds(p, content, Env.Σ)
    Pending   otherwise
```

where `contentHolds` is defined below.

### Hohfeldian Correlatives and Opposites

RL2 reifies **six positive Hohfeldian positions** (Privilege, Duty, Claim, Power,
Liability, Immunity) plus **Prohibition** as authoring classes. The two *absence*
positions — **No-Claim** and **Disability** — are **not** modeled as classes; they are
derived (inferred from the absence of the correlative Claim/Power) and never reified.
The correlatives are (italicized entries are the derived, non-reified absences):

| Right-holder has | Duty-bearer has |
|------------------|-----------------|
| Privilege | *No-Claim* (derived) |
| Claim | Duty |
| Power | Liability |
| Immunity | *Disability* (derived) |

**Prohibition in the Hohfeldian square.** RL2 keeps `Prohibition` as a distinct
class for authoring ergonomics, but semantically a `Prohibition(s, x, o, c)` **is a
duty to refrain** — a Duty whose action is the omission of `x`. Its Hohfeldian
correlative is therefore a **Claim**: the `counterparty` of the prohibition holds a
claim that `s` not perform `x` on `o`. When no `rl2:counterparty` is asserted on the
prohibition, the correlative claim is held by the policy grantor.

```
∀ Prohibition(s, x, o, c) : ∃ Claim(h, s, Duty(s, ¬x, o, c)) where
    h = counterparty(Prohibition) if present, else grantor(policyOf(Prohibition))
```

The correlative Claim is **derived**, not authored: policy authors write only the
`Prohibition`. Violation of a prohibition uses the subsumption-aware `performed()`
helper (so performing a narrower action `x′ ⊑ x` violates a prohibition on `x`).

### Claim Denotation and Content Derivation (C6b)

A Claim is the Hohfeldian correlative of **exactly one** Duty, carried directly as its third
constructor field `correlativeTo` (enforced by `ClaimShape`: exactly one, and it must be a
`rl2:Duty`). A Claim does **not** author its own content; its action, object, and condition are
**derived** from that Duty:

```
ClaimContent(k: Claim) =
    let D = k.correlativeTo                          -- exactly one, and D : Duty (ClaimShape)
    in (action, object, condition) := (D.action, D.object, D.condition)   -- DERIVED, not authored
```

with the party roles required to mirror the Duty (validated by `ClaimShape`):

```
D.subject = k.counterparty   (the duty-bearer)   ∧
D.counterparty = k.subject   (the right-holder)
```

A Claim is *held* exactly when its correlative Duty's condition holds; the Claim inherits the
Duty's `Truth` (S2), so an `Unknown` Duty condition yields an `Indeterminate` claim rather than a
silently-inactive one:

```
⟦Claim(h, a, D)⟧(Env) =                     -- h = subject (right-holder), a = counterparty (duty-bearer), D = correlativeTo
    ClaimHeld(h, a, ClaimContent(Claim(h, a, D)))  if ⟦D.condition⟧(Env).truth = True
    Indeterminate                                   if ⟦D.condition⟧(Env).truth = Unknown
    ClaimInactive                                    otherwise
```

Because content and correlation are derived from the single authored Duty, two claims about
different actions or objects are always distinguishable (via their distinct Duties), the
Claim↔Duty pairing is one-to-one, and there is no dual-source encoding where a Claim and its
Duty could disagree.

### Power Denotation (F2 / SEM-10)

A Power is the ability of an agent to alter normative relations, gated by its own optional
`Condition` — the third constructor field `c` — using the same three-way `Truth` pattern (S2)
as Privilege/Duty/Prohibition, not a separately-named `powerCondition` predicate (CANON-5: one
canonical condition-evaluation shape). `c` gates the Power itself, independent of `affectsNorm`'s
own condition, which separately governs whether *that* norm is active once the power is exercised:

```
⟦Power(a, n, c)⟧(Env) =
    PowerActive(a, n)   if c = ⊥ ∨ ⟦c⟧(Env).truth = True
    Indeterminate       if c ≠ ⊥ ∧ ⟦c⟧(Env).truth = Unknown
    PowerInactive       otherwise
```

Where `n` is the norm that the agent has power to create, modify, or extinguish (`affectsNorm`).

Powers enable:
* Creating new Privileges, Duties, or Prohibitions
* Modifying existing norms (e.g., extending deadlines)
* Extinguishing norms (e.g., waiving a Claim)

Power exercise is modeled as a state transition:

```
ExercisePower(a, n):
    Σ ⊢ Power(a, n) active
    ────────────────────────
    Σ → Σ' where n ∈ Σ'.ActiveNorms
```

### Liability Denotation (F2 / SEM-10)

A Liability is the correlative of a Power — the susceptibility to have one's normative position
altered. Like Claim/Duty (C6b), a Liability does not author its own condition: it is a
**structurally derived** view of a *specific* Power, carried directly as its second constructor
field `exposedTo` (required, exactly one; enforced by `LiabilityShape`) — not an unlinked
existential over every Power sharing the same `subject`, which could bind a Liability to an
unrelated Power:

```
⟦Liability(a, P)⟧(Env) =
    LiabilityActive(a, P)   if ⟦P⟧(Env) = PowerActive(_, _)
    Indeterminate            if ⟦P⟧(Env) = Indeterminate
    LiabilityInactive        otherwise
```

When `P` is exercised (`ExercisePower`), the Liability-holder's position changes accordingly.

### Immunity Denotation (F2 / SEM-10)

An Immunity protects an agent from having their normative position altered by a *specific* named
Power, carried directly as its second constructor field `immuneFrom` (required, exactly one;
enforced by `ImmunityShape`). Unlike Liability, an Immunity's activation is **independently
condition-gated** — e.g. "immune from the termination Power during the first 90 days" holds on
its own schedule, regardless of whether the termination Power's own condition currently holds —
so, like Power, it uses the direct condition-evaluation pattern rather than a Power-derived
`Truth`:

```
⟦Immunity(a, P, c)⟧(Env) =
    ImmunityActive(a, P)   if c = ⊥ ∨ ⟦c⟧(Env).truth = True
    Indeterminate           if c ≠ ⊥ ∧ ⟦c⟧(Env).truth = Unknown
    ImmunityInactive        otherwise
```

Immunity blocks Power exercise:

```
∀ P : Power, Immunity(a, P):
    ImmunityActive(a, P) → ¬canExercise(P)
```

### Sanctions and Remedies

Violations trigger remedial norms via Power/Liability relations. `P` must be the *same* Power
instance on both sides of the rule — `Liability(a, P)`'s `exposedTo` link (F2/SEM-10) is what
ties the exposed party to this particular sanction, not merely to some other power sharing its
target:

```
DutyViolated(a, x, s) ∧ P = Power(h, sanction, _) ∧ Liability(a, P)
─────────────────────────────────────────────────────────────────────
    h may exercise P against a
```

Typical sanctions include:
* Creation of compensatory Duties
* Activation of Prohibitions (e.g., access revocation)
* Triggering of escalation workflows

---

## Policy-Level Activation

Policies may have an optional activation condition. A policy is *applicable* when its condition holds (or if no condition is specified, it is always applicable).

## Policy Applicability

```
PolicyApplicable(P, Env) =
    P.condition = ⊥  ∨  ⟦P.condition⟧(Env).truth = True
```

Where `⊥` denotes the absence of a condition (unconditionally applicable).

## Applicable Policy Set

Given a universe of policies U and environment Env:

```
ApplicablePolicies(U, Env) = { P ∈ U | PolicyApplicable(P, Env) }
```

**PolicyUniverse determination**: The universe U is the set of all policies in the active *generation*. When evaluation begins, the evaluator resolves the generation identifier (from `rl2p:policyGeneration` on the Case) to obtain U. This is an evaluator responsibility, not a semantic operation — the semantics assume U is provided. See §Policy Generations for the generation model.

## Effective Norm Activation

A norm n within policy P is active when its effective condition (S2's `effectiveCondition`,
folding the policy-level and clause-level conditions together) holds:

```
NormActive(n, P, Env) = ⟦effectiveCondition(P,n)⟧(Env).truth = True
```

`NormActive` is defined directly over `effectiveCondition`, not via `PolicyApplicable` — this
is the fix for the collapse bug `PolicyApplicable` has on its own: because `PolicyApplicable`
is Boolean-valued, gating a clause through `PolicyApplicable(P,Env) ∧ ...` would silently treat
an `Unknown` policy-level condition as if the policy were inapplicable, discarding the clause
instead of surfacing it as indeterminate. Going through `effectiveCondition` first means the
policy- and clause-level conditions are combined *before* the three-way `Truth` is read, so an
`Unknown` at either level correctly yields `Unknown` for the whole clause. (`PolicyApplicable`
itself is retained, unchanged, for the few call sites — `promiseEffective` — that need a
Boolean applicability check with no norm-level condition to combine.)

`NormActive` (and `deriveNorms` below) admits a norm only on `True`. A norm whose effective
condition is `Unknown` is **neither** active **nor** silently discarded: it is collected into
the `indeterminate` set (see Evaluation Algorithm, S2) and carries the causing errors forward.

## Dynamic Policy Applicability

As the state Σ evolves (events arrive, duties fulfill/violate, time advances), the applicable policy set changes accordingly. This models workflows where:

* An event activates a new policy (e.g., committee acceptance triggers full review)
* A condition becoming false deactivates a policy
* Multiple policies may apply simultaneously

No branching or non-determinism is introduced. Policies activate/deactivate based on the current state Σ; the evaluation remains deterministic at each point in time.

---

## Operational Semantics (Small-Step)

Operational semantics define **how states and obligations evolve over time**.

### Judgement Form

```
(Σ, R, Ctx, e) → (Σ', e')
```

Where:
* `Σ` is the current state
* `R = (a_req, x_req, s_req)` is the request (agent, action, asset)
* `Ctx` is the external context (assertions, environment facts)
* `e` is the expression being evaluated
* `Σ'` is the resulting state
* `e'` is the resulting expression

The environment is constructed as: `Env = mkEnv(R, Σ, Ctx)`

### State Update Notation

We use the notation `Σ[f ↦ v]` to denote state update:

```
Σ[ObligationState(d) ↦ Active] =
    (Σ.Clock, Σ.Events, Σ.Metadata,
     Σ.Promises, Σ.ObligationState[d ↦ Active], Σ.Requirements)

Σ[PromiseState(p) ↦ Fulfilled] =
    (Σ.Clock, Σ.Events, Σ.Metadata,
     Σ.Promises[p ↦ Σ.Promises[p] with state = Fulfilled],
     Σ.ObligationState, Σ.Requirements)
```

(No `Σ.Performed`/`Σ.DutyPerformer` fields to carry — they are derived from `Σ.Events`, S6.)

### Promise State Derivation

Let `linkedDuty(p)` be `d` when `p` has `rl2:promisedDuty = d` (i.e. `content = PromisedDuty(d)`); otherwise `⊥`. Promise state is derived (not guessed) from Σ as:

```
PromiseState(p, Σ) =
    if linkedDuty(p) ≠ ⊥ then projectObligationState(ObligationState(linkedDuty(p), Σ))
    else evidencePromiseState(p, Σ)

projectObligationState(s) =
    Pending    if s = Pending
    Pending    if s = Active     -- Promises never expose Active; it collapses to Pending
    Fulfilled  if s = Fulfilled
    Violated   if s = Violated

evidencePromiseState(p, Σ) =
    if fulfilledEvidence(p, Σ) then Fulfilled
    else if violatedEvidence(p, Σ) then Violated
    else Pending
```

Where:
- `fulfilledEvidence(p, Σ)` holds when Σ contains an event or assertion establishing the promise content holds (e.g., `contentHolds(promisor(p), content, Σ)`).
- `violatedEvidence(p, Σ)` holds when Σ contains an event or assertion establishing the promise content is violated, including deadline/timeout (`deadlinePassed(content, Σ)` with unmet content).
- Default is `Pending` until evidence moves it to a terminal value.

The projection keeps PromiseState deterministic and monotone: adding evidence or advancing a linked duty's lifecycle cannot revert a promise from `Fulfilled`/`Violated` to `Pending`.

### Promise and duty states vs protocol requirement status

- `PromiseState ∈ {Pending, Fulfilled, Violated}` (no `Active`).
- `Obligation/DutyState ∈ {Pending, Active, Fulfilled, Violated}`.
- `rl2p:requirementStatus` is the protocol/runtime projection (formalized below as `requirementStatus`):
  - A pending promise that is **effective now** may be represented as an `Active` requirement (monitored/in-force) while the semantic promise state remains `Pending`.
  - If the promise is not yet effective, the requirement remains `Pending`.
  - Terminal promise states map to terminal requirement states.

#### Requirement Status Derivation (F3 / P3)

`requirementStatus` closes the duplication F3 flags: `RequirementRecord` stores no independent
`status` — every `rl2p:requirementStatus` triple is this projection over `Σ.ObligationState` /
`PromiseState`, never a second source of truth. `req.trackedDuty` (see the `Σ` record above) names
the Duty whose `ObligationState` this requirement mirrors: the source Duty itself for a Duty-sourced
requirement, or the remedial Duty generated by the Promise→Duty Generation Rule below for a
remediated Promise-sourced requirement; `⊥` for a Promise-sourced requirement with neither.

```
requirementStatus(req, Σ, Env) =
    if req.trackedDuty ≠ ⊥ then ObligationState(req.trackedDuty, Σ)
    else projectRequirementFromPromise(req.sourceNorm, Σ, Env)

projectRequirementFromPromise(p, Σ, Env) =
    let s = PromiseState(p, Σ) in
    if s ≠ Pending then s                                     -- terminal states map directly
    else if promiseEffective(p, Σ, Env) then Active else Pending

promiseEffective(p, Σ, Env) =
    if linkedDuty(p) ≠ ⊥ then ObligationState(linkedDuty(p), Σ) = Active
    else PolicyApplicable(clauseOf(p), Env)
```

`clauseOf(p)` is the Policy containing `p` (`rl2p:clauseOf`, inverse of `rl2:clause`). Two worked
cases from RL2_Protocol.md §Universal Requirement: `ex:req1` (`sourceNorm = trackedDuty =
ex:managerApprovalDuty`) reads `ObligationState` directly and is `Active` exactly when the duty is;
`ex:req2` (`sourceNorm = ex:dataQualityPromise`, `trackedDuty = ⊥`, no linked duty, not yet effective)
projects to `Pending`. The remedial Requirement of §Promise→Duty Generation Rule sets `trackedDuty =
d` — the freshly-generated remedial Duty, itself entered into `Σ.ObligationState` — while `sourceNorm`
keeps pointing at the originating (by-then-`Violated`) Promise for audit provenance; `requirementStatus`
therefore tracks `d`'s lifecycle (`Active` on generation, per the worked example there), not the stale
terminal `PromiseState` of the Promise it superseded.

The projection is deterministic and monotone for the same reason `PromiseState` is (§Promise State
Derivation above): it only reads `ObligationState`/`PromiseState`/a live condition evaluation, never an
independent store that could drift from them.

#### Case Status Derivation (duty-fulfillment component)

`rl2p:caseStatus`'s `CasePending ↔ {Approved, Denied}` transitions (RL2_Protocol.md §Case Lifecycle)
are the derivable slice of case status — a projection over the case's Requirements, closing the same
gap for the piece that genuinely follows from requirement state. `Expired`/`Revoked` stay explicit,
exogenous, one-way transitions (time advancing past `expirationTime`; an administrative revocation
event) — they are not functions of Requirement state and are not part of this projection, exactly as
RL2_Protocol.md's Case State Transitions diagram already documents.

```
Requirements(c, Σ) = latestEvaluation(c, Σ).activeRequirements
latestEvaluation(c, Σ) = argmax_{ev ∈ evaluationHistory(c)} ev.evaluationTime

allFulfilled(c, Σ, Env) = ∀ req ∈ Requirements(c, Σ). requirementStatus(req, Σ, Env) = Fulfilled
anyViolated(c, Σ, Env)  = ∃ req ∈ Requirements(c, Σ). requirementStatus(req, Σ, Env) = Violated

pendingOutcome(c, Σ, Env) =
    if latestEvaluation(c, Σ).decision = Deny then Denied
    else if anyViolated(c, Σ, Env) then Denied
    else if allFulfilled(c, Σ, Env) then Approved       -- vacuously true when Requirements(c,Σ) = ∅
    else CasePending
```

`caseStatus(c, Σ, Env)` equals `pendingOutcome(c, Σ, Env)` while `c` has not been explicitly revoked
and its `expirationTime` has not passed; `Expired`/`Revoked` are stored overrides applied on top of
`pendingOutcome`, matching the diagram (`Approved → Expired`, `Approved → Revoked`). Re-certification
(`Expired → Pending`) is not a special case: it is a fresh `evaluationHistory` entry, which
`latestEvaluation` picks up, re-entering `pendingOutcome` on the new Requirements.

### Duty Activation

A pending duty becomes active when its activation condition holds:

```
Env = mkEnv(R, Σ, Ctx)
⟦ c ⟧(Env).truth = True
Σ.ObligationState(Duty(a,x,s,c)) = Pending
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Duty(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Active], DutyActive(a,x,s,c))
```

### Duty Fulfillment (Achievement)

An active Achievement-mode duty (S4; `dutyMode(Duty(a,x,s,c)) = Achievement`,
including the default when `rl2:dutyMode` is absent) is fulfilled by a single
qualifying witness — the required action (or a narrower action subsumed by it)
performed while the duty is still active. The performing agent is recorded in
`DutyPerformer`:

```
dutyMode(Duty(a,x,s,c)) = Achievement
Σ.ObligationState(Duty(a,x,s,c)) = Active
performed(a,x,s,Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) →
    (Σ[ObligationState(Duty(a,x,s,c)) ↦ Fulfilled],
     DutyFulfilled(a,x,s,c))
```

The transition records only the state change; the performer is **not** stored (S6). Identity
binding reads `DutyPerformer(d, Σ)` — derived from the witnessing `ActionPerformed` event:
- **Tun-sollen check**: `DutyPerformer(d, Σ) = currentAgent` (same agent must benefit)
- **Sein-sollen check**: Only check `ObligationState(d) = Fulfilled` (anyone may fulfill)
- **Separation of Duty**: `DutyPerformer(d, Σ) ≠ currentAgent` (different agent must benefit)

### Duty Violation (Achievement)

An active Achievement-mode duty is violated only when its deadline expires while still
unfulfilled — never merely because the condition is momentarily false:

```
Env = mkEnv(R, Σ, Ctx)
dutyMode(Duty(a,x,s,c)) = Achievement
Σ.ObligationState(Duty(a,x,s,c)) = Active
performed(a,x,s,Σ) = false
timeout(c, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Violated], DutyViolated(a,x,s,c))
```

### Duty Fulfillment (Maintenance)

A Maintenance-mode duty (S4; `dutyMode(Duty(a,x,s,c)) = Maintenance` — crystallized
from a `PromisedState`, see Crystallization) holds a condition `c` as a state-invariant
rather than requiring a witnessed action; `x`/`s` remain structurally present (the Duty
grammar always carries an Action slot) but this rule does not consult them. It is
fulfilled only when its monitoring period **closes** — `c`'s extracted deadline expires
— with `c` still holding and with no prior counterexample (Violation, below, would
already have moved the duty out of `Active`). With no recognized end bound
(`extractDeadline(c) = None`), the duty has no closing event and stays Active — it is
never declared fulfilled by omission:

```
Env = mkEnv(R, Σ, Ctx)
dutyMode(Duty(a,x,s,c)) = Maintenance
Σ.ObligationState(Duty(a,x,s,c)) = Active
extractDeadline(c) = Some(b)
expired(b, Σ.Clock) = true
⟦c⟧(Env).truth = True
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) →
    (Σ[ObligationState(Duty(a,x,s,c)) ↦ Fulfilled],
     DutyFulfilled(a,x,s,c))
```

### Duty Violation (Maintenance)

A Maintenance-mode duty is violated on the first witnessed counterexample while
active — it does not wait for any deadline:

```
Env = mkEnv(R, Σ, Ctx)
dutyMode(Duty(a,x,s,c)) = Maintenance
Σ.ObligationState(Duty(a,x,s,c)) = Active
⟦c⟧(Env).truth = False
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Violated], DutyViolated(a,x,s,c))
```

`⟦c⟧(Env).truth = Unknown` (S2's three-valued `Truth`) advances neither Maintenance rule —
an indeterminate condition is neither a closing witness nor a counterexample, matching
the S2 discipline that `Unknown` never silently resolves to a decision.

### Promise Fulfillment

For promises without a linked duty (`linkedDuty(Promise(p,q,content)) = ⊥`), evidence that the content holds fulfills the promise. This is the operational realization of `fulfilledEvidence`:

```
PromiseState(Promise(p,q,content), Σ) = Pending
linkedDuty(Promise(p,q,content)) = ⊥
contentHolds(p, content, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Promise(p,q,content)) →
    (Σ[PromiseState(Promise(p,q,content)) ↦ Fulfilled],
     PromiseFulfilled(p,q,content))
```

### Promise Violation

For promises without a linked duty, evidence of non-fulfillment (including timeouts) violates the promise. This is the operational realization of `violatedEvidence`:

```
PromiseState(Promise(p,q,content), Σ) = Pending
linkedDuty(Promise(p,q,content)) = ⊥
contentHolds(p, content, Σ) = false
deadlinePassed(content, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Promise(p,q,content)) →
    (Σ[PromiseState(Promise(p,q,content)) ↦ Violated],
     PromiseViolated(p,q,content))
```

Where `deadlinePassed(content, Σ)` checks for expiry of any temporal bound extracted from the promise content.

### Crystallization (Offer → Agreement)

An **Offer** is a bundle of voluntary Promises (made or demanded) together with any
restated externally-imposed Duties — e.g. a data provider offers "complete, timely
data" (a Promise) *and* restates the statutory GDPR erasure obligation (a Duty that
holds regardless of the contract). Nothing in an Offer is yet enforceable *as a
contract*: a Promise binds its promisor in the Promise-Theory sense but creates no
correlative Claim, and there is no accepted counterparty who can demand performance.

**Acceptance** transforms the Offer into an **Agreement**. Each Promise
*crystallizes* into a Duty plus its correlative Claim — acceptance is precisely what
supplies the claim-holder the bare Promise lacked. Restated external Duties carry
through unchanged. The result is enforceable on both sides, and **no Promise
survives in the Agreement**: a residual Promise creates no correlative and is
therefore inert — a construct the totality proof would have to carry with no
evaluation semantics — so it is rejected by SHACL (`AgreementShape`). Non-binding
recitals, if wanted, belong in an `rl2:Assertion`, not a clause.

This is distinct from the **Remedial Generation Rule** below: crystallization is
*acceptance-triggered*, total, and structural (every Promise yields a Duty at
contract formation); remedial generation is *violation-triggered* and produces a
restorative Duty only when a live Promise's invariant is breached.

**Crystallization function** (total over the three content forms). `D.dutyMode` is
**derived** from `κ`'s shape (S4) — never redundantly authored on the source Promise:

```
crystallize(Promise(p, q, κ)) = (D, C)
    where D.dutyMode = case κ of
                            PromisedState(_) → Maintenance
                            _                → Achievement   -- PromisedAction, PromisedDuty
          C = Claim(subject = q, counterparty = p, correlativeTo = D)
```

| Promise content `κ` | Crystallized Duty `D` | Fulfillment criterion (inherited from the Promise) | Behavioral wiring |
|---|---|---|---|
| `PromisedAction(x)` on `o` | Achievement-mode `Duty(subject=p, action=x, object=o)` | `D` Fulfilled when `p` has performed `x` (`performed()`, subsumption-aware) | none — standard action-performance duty. **Fully closed.** |
| `PromisedState(c)` on `o` | Maintenance-mode `Duty(subject=p, object=o, condition=c)` | Fulfilled when `c`'s monitoring period closes with `c` still true (Duty Fulfillment (Maintenance)); Violated on the first witnessed counterexample (Duty Violation (Maintenance)) | ObligationState transitions **specified (S4)**; `restoreAction` on breach remains open → **SEM-1** (narrowed) |
| `PromisedDuty(d)` | Achievement-mode second-order (suretyship) `Duty(subject=p)` over `d` | Fulfilled when `d`'s ObligationState reaches `Fulfilled` | the remedy/liability the surety `p` incurs when `d` is Violated (guarantee vs indemnity) → **PROM-5** |

Each Duty's fulfillment criterion is inherited directly from the promise content's
*already-defined* semantics (`rl2.ttl`: `promisedAction` / `promisedState` /
`promisedDuty` all specify fulfillment/violation). Crystallization therefore
introduces **no new fulfillment semantics** — it re-homes an existing criterion
onto a Duty and adds the correlative Claim. Both crystallized modes' ObligationState
transitions are now fully specified (S4, above — Duty Fulfillment/Violation
(Achievement) and (Maintenance)); the one remaining behavioral wiring from the
`PromisedState` row is what remedial action a breach should trigger
(`restoreAction`/`remedialActionOf`, SEM-1, narrowed to just this), alongside the
independent surety-obligation question for `PromisedDuty` (PROM-5). Neither remaining
item affects the crystallization *targets* fixed here, so the Offer→Agreement
transition is well-defined for every promise now.

### Materialization (Offer → Agreement, document level)

Crystallization above defines *what a Promise becomes*; it does not by itself say how an
Agreement's clauses come to reference the crystallized Duty instead of the vanished Promise, or
how a restated Norm clause avoids colliding across multiple Agreements formed from the same
Offer. **Materialization** is the one-time, document-level step that acceptance performs to
produce a self-contained Agreement:

```
materialize(Offer, Acceptance) = Agreement
    where Agreement = fresh IRI
```

An Offer is catalog-like: it is authored once, published, and may be accepted many times (e.g.
an SLA offered to many customers). Because `Σ`'s state maps are keyed by bare IRI with no
Case/Agreement dimension —

```
ObligationState : Duty → {Pending, Active, Fulfilled, Violated}
DutyPerformer   : Duty → Agent ∪ {⊥}
```

(§Σ, above) — two Agreements that shared a clause IRI would share one entry in these maps, and
one customer's fulfillment would silently become another's. `materialize` therefore mints a
**fresh IRI for every clause it places in the Agreement**, crystallized or not:

1. Mint a fresh IRI for the Agreement itself.
2. For each Promise clause in the Offer, `crystallize` it (as above) into a **freshly-minted**
   Duty `D` and correlative Claim `C` — scoped to this Agreement, not shared with any other
   acceptance of the same Offer.
3. For each restated Norm clause in the Offer, copy it into the Agreement under a **freshly-minted**
   IRI — for the same Σ-collision reason as step 2, not merely for symmetry.
4. Let `map` be the resulting Promise/Norm ⟶ crystallized-or-copied-clause correspondence built by
   steps 2–3. Rewrite every `rl2:targetNorm` reference inside the Agreement's clauses through
   `map`, so a condition that targeted an Offer-stage Promise now targets its crystallized Duty.
   After this rewrite, `targetNorm` is always Norm-valued inside an executed Agreement — no
   Promise survives materialization (PROM-1) and none is ever queried by IRI after acceptance.
5. Record provenance: `Agreement prov:wasDerivedFrom Offer` (`http://www.w3.org/ns/prov#`,
   borrowed by term as `rl2.ttl` already borrows `dc:` — no `owl:imports` of PROV-O itself).
   This is the first use of an external vocabulary term on RL2 individuals rather than on the
   ontology document header; it is deliberate, not an invitation to import further vocabularies
   without the same discussion.

`materialize` is **not** an IR effect. It runs once, before compilation, over the fixed Offer
document and the Acceptance event — analogous to the ODRL-inheritance flattening pass in
`RL2_ODRL_Comparison.md`. `evalIR`/`applyEffects` (RL2_IR.md §7) operate on an already-compiled,
immutable `CompiledPolicy` and only ever mutate Σ; they have no mechanism for rewriting a
policy's own AST, which is exactly what step 4 requires. `CrystallizePromise` (RL2_IR.md's
`Effect` datatype) remains unchanged: it is the *runtime* bookkeeping Σ-effect fired each time a
`PromiseEntry` is evaluated within an already-materialized Agreement, distinct from this one-time
document construction.

### Promise→Duty Generation (Remedial Generation Rule)

**Conceptual Foundation (Sein-Sollen vs Tun-Sollen)**:

- **Promise = Sein-Sollen (Ought-to-Be)**: A required state of the world (invariant)
- **Duty = Tun-Sollen (Ought-to-Do)**: An action to achieve or restore that state

When the world deviates from a Promise's invariant, the evaluator generates a remedial Duty (tracked as a `rl2p:Requirement`) to restore compliance.

**Generation Rule**:

When a Promise enters the `Violated` state, a remedial Requirement is generated:

```
PromiseState(Promise(p, q, content), Σ) = Violated
d = RemedialDuty(p, restoreAction(content), objectOf(content))
req = RequirementRecord(sourceNorm = Promise(p,q,content), trackedDuty = d,
                         sourcePolicy = clauseOf(Promise(p,q,content)), counterparty = q,
                         imposedTime = Σ.Clock)
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, PromiseViolated(p, q, content)) →
    (Σ[ObligationState(d) ↦ Active,
       Requirements ↦ Σ.Requirements ∪ {req}],
     RemedialDutyGenerated(d))
```

`req.trackedDuty = d`, so `requirementStatus(req, Σ') = ObligationState(d, Σ') = Active`
immediately — `req.sourceNorm` stays the original Promise for provenance, never queried for status
while `trackedDuty ≠ ⊥` (§Requirement Status Derivation).

Where `restoreAction` and `objectOf` are total over the three content forms:

```
restoreAction(content) =                      objectOf(content) =
    case content of                               case content of
        PromisedAction(x, s) → x                      PromisedAction(x, s) → s
        PromisedDuty(d)      → d.action               PromisedDuty(d)      → d.object
        PromisedState(c)     → remedialActionOf(c)    PromisedState(c)     → objectOf(c)
```

- `PromisedAction`: retry the promised action `x`. `PromisedDuty`: perform the promised duty's action. These are canonical — no annotation needed.
- `PromisedState`: restoring an arbitrary state is not a single canonical action; `remedialActionOf(c)` resolves to an explicit `rl2:remedialAction` annotation on the promise (see issue SEM-1). Absent that annotation the remedial Duty is generated with an undefined action and the case is surfaced as an ambiguity, not silently guessed.
- The generated `Requirement` tracks `sourceNorm = Promise(p,q,content)`, `trackedDuty = d`, and `counterparty = q` (the promisee).
- The promisee `q` holds the correlative Claim.

**Runtime Representation**:

The Protocol's `rl2p:Requirement` structure captures this:

```turtle
ex:dataQualityPromise a rl2:Promise ;
    rl2:promisor ex:DataProvider ;
    rl2:promisee ex:DataConsumer ;
    rl2:promisedState ex:qualityThresholdMet .

ex:dataOffer a rl2:Offer ;                    # Promises live in Offers
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:DataConsumer ;
    rl2:clause ex:dataQualityPromise .

ex:remedialReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:dataQualityPromise ;  # The violated Promise
    rl2p:sourcePolicy ex:dataOffer ;
    rl2p:counterparty ex:DataConsumer ;       # The promisee/Claim holder
    rl2p:requirementStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime .
```

This unified structure enables:
- Audit trails linking requirements to their normative source
- Uniform lifecycle tracking regardless of whether source is Duty or Promise
- Claim holder identification for multi-party obligations

### Event Processing

Events update state and may trigger norm transitions:

```
e ∈ E (incoming events)
Σ' = processEvent(e, Σ)
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, EventSet(E)) → (Σ', EventSet(E \ {e}))

processEvent(e, Σ) =
    if e.id ∈ ids(Σ.Events) then Σ                      -- S5: idempotent — a duplicate id is a no-op
    else let e⁺ = e with eventSequence = nextSeq(Σ.Events)   -- assign the total-order sequence on append
    in case kind(e) of
        TimeAdvanced(t)        → Σ[Clock ↦ t]
        MetadataChanged(s,k,v) → Σ[Metadata(s)[k] ↦ v]
        _                      → Σ[Events ↦ append(Σ.Events, e⁺)]   -- append-only; ActionPerformed included
```

**S6:** every witness event — including `ActionPerformed` — is **appended** to the log with a
freshly assigned `eventSequence`; nothing sets a separate `Performed` Boolean. `nextSeq` returns a
value strictly greater than every existing `eventSequence`, giving the total order that makes
`performed()`/`witness()`/`DutyPerformer()` deterministic. `TimeAdvanced`/`MetadataChanged` update
scalar state and are not witness events. Appends are monotonic: the log never rewrites or drops a
prior event.

**S5 — duplicate and late-arrival events (normative).** Because events carry a stable `id` (S6)
and `processEvent` is idempotent on it, **re-delivering the same event is a no-op** — an
at-least-once transport does not double-count. A **late-arriving** event (one whose `eventTime` is
earlier than events already in the log, but which reaches the evaluator later) is appended
normally: it receives the *next* `eventSequence`, so it sorts into position by `eventTime` under
the `(eventTime, eventSequence)` order while its higher sequence records the true arrival order for
audit. A late arrival therefore affects only evaluations performed *after* it lands; it **never
retroactively changes a decision already committed against an earlier snapshot** (see *State Scope,
Identity, and Concurrency* below — decisions are computed against a versioned snapshot and are
replay-stable for that version). `ids(Σ.Events)` is the set of event ids already logged.

### Privilege Activation

Privileges become active when their condition holds:

```
Env = mkEnv(R, Σ, Ctx)
matches(Privilege(a,x,s,c), R) = true
⟦ c ⟧(Env).truth = True
──────────────────────────────────────────────────────────────────
PrivilegeActive(a, x, s, c)
```

Privileges become inactive when their condition no longer holds or the request doesn't match:

```
Env = mkEnv(R, Σ, Ctx)
matches(Privilege(a,x,s,c), R) = false ∨ ⟦ c ⟧(Env).truth = False
──────────────────────────────────────────────────────────────────
PrivilegeInactive(a, x, s, c)
```

### Prohibition Activation

Prohibitions are active when their condition holds and the request matches:

```
Env = mkEnv(R, Σ, Ctx)
matches(Prohibition(a,x,s,c), R) = true
⟦ c ⟧(Env).truth = True
──────────────────────────────────────────────────────────────────
ProhibitionActive(a, x, s, c)
```

A prohibition is violated when the prohibited action (or a narrower action subsumed by it) is performed while active:

```
ProhibitionActive(a, x, s, c)
performed(a, x, s, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Prohibition(a,x,s,c)) → (Σ, ProhibitionViolated(a, x, s, c))
```

---

## Normative Derivation (I/O-Logic Foundation)

RL2's evaluation follows an **I/O logic** pattern (Makinson & van der Torre): derivation produces a normative envelope, then conflict resolution yields a final decision.

### Pre-Resolution Normative Envelope

The function `Out` computes the **unresolved set** of normative atoms from a policy universe and environment (atoms are deduplicated by canonical identity — the `∪` below is set union, not multiset sum). Every clause is read through `effectiveCondition(P, n)` (S2's policy/clause condition fold, defined above) rather than through `ApplicablePolicies`/`PolicyApplicable`: those two functions stay Boolean-valued (kept only for the few call sites that need a plain applicability check with no clause to fold in) and would silently collapse an `Unknown` policy-level condition into "inapplicable," discarding every clause it should instead mark indeterminate. Folding first and reading `Truth` second means an `Unknown` at either level is attributed to the clause, never lost:

```
Out : (PolicyUniverse U, Env) → ℘(NormativeAtoms)

Out(U, Env) =
    ⋃ { deriveNorms(P, Env) | P ∈ U }

deriveNorms(P, Env) =
    let R = Env.Request in
    { permit(n, P)   | n : Privilege   ∈ P.clauses, matches(n, R), ⟦effectiveCondition(P,n)⟧(Env).truth = True } ∪
    { forbid(n, P)   | n : Prohibition ∈ P.clauses, matches(n, R), ⟦effectiveCondition(P,n)⟧(Env).truth = True } ∪
    { obligate(d, P) | d : Duty        ∈ P.clauses, matches(d, R), ⟦effectiveCondition(P,d)⟧(Env).truth = True } ∪
    { indeterminate(n, P, causes(n, P, Env))
                     | n : Privilege   ∈ P.clauses, matches(n, R), ⟦effectiveCondition(P,n)⟧(Env).truth = Unknown } ∪
    { indeterminate(n, P, causes(n, P, Env))
                     | n : Prohibition ∈ P.clauses, matches(n, R), ⟦effectiveCondition(P,n)⟧(Env).truth = Unknown } ∪
    { indeterminate(d, P, causes(d, P, Env))
                     | d : Duty        ∈ P.clauses, matches(d, R), ⟦effectiveCondition(P,d)⟧(Env).truth = Unknown }

causes(n, P, Env) = ⟦effectiveCondition(P,n)⟧(Env).causes
```

`deriveNorms` reads `R` and `Σ` only through `Env` (`Env.Request`, `Env.Σ`) — there is no free
reference to either — matching S2's `⟦·⟧(Env)` discipline throughout this document.

`violated(d, P)` is **not** an `Out`/`deriveNorms` atom. `Out` runs at the derivation stage (①):
monotone, total, and evaluated against the immutable pre-transition `Env`/`Σ` — it has no way to
observe which matched duties `updateDutyStates` (stage ②) will later drive to `Violated`, so an
atom minted here would go stale the instant that transition happens. Instead, duty
Active/Violated classification is done by `resolveDecision`'s internal partition helper (below),
which reads the *post*-transition `Σ'` for exactly the duties `Out` attributed via `obligate(d,P)`.

The type filters are normative. Claims, Powers, Liabilities, Immunities, and Promises have their
own denotations/lifecycles; they are not request-matched access candidates and therefore do not
produce access-decision `indeterminate` atoms.

**S7 (provenance).** A `NormativeAtom` wraps the full norm object (`n`/`d`, not a projected
`(a,x,s)` triple) together with its source policy `P` — every atom in the envelope carries the
clause and policy that produced it, for audit and for `mostSpecific` (below), which needs
`n.priority`/`n.action`/`n.condition`. Atom equality is structural: `(atom-kind,n,P)` for
definite atoms and `(indeterminate,n,P,causes)` for Unknown atoms. `causes` is itself a canonical
set, so its enumeration order cannot create a second atom. Two policies granting the same
`(a,x,s)` shape remain distinct atoms with independent provenance (WP-3/C6a's clause-identity
guarantee already makes `n` unique per policy, so this never accidentally merges two different
clauses). `resolveDecision(envelope, Σ', strategy)` is the sole public entry point for
resolution; its internal definite/Unknown partition retains the complete attributed atoms and
is not itself a second public interface (see **Conflict Resolution** below).

### Monotonicity of Derivation

The derivation function `Out` is **monotone in the policy universe** for a **fixed immutable environment**:

```
For a fixed Env, if U ⊆ U' then Out(U, Env) ⊆ Out(U', Env)
```

Since `Out` is a union of per-clause contributions evaluated independently against the *same* `Env`, adding clauses can only add atoms, and the result is **independent of the order** in which clauses are processed (order-independence of derivation). This is the property Phase ① actually relies on and the one the resolution/audit layer builds upon.

> **`Out` is *not* monotone in the environment.** The earlier form `Env ⊆ Env' ⇒ Out(U, Env) ⊆ Out(U, Env')` is **false**: several conditions are anti-monotone in the facts — `Not(EventConstraint)`, `neq`, `isNoneOf`, and upper time bounds can flip from `true` to `false` as facts are added, *removing* a derived atom. The environment is therefore treated as a single immutable snapshot per evaluation, and no proof, optimization, or caching step may assume atoms survive the enlargement of `Env`.

Phase ① avoids negation-as-failure and rule-level negation over *derived* facts (derivation never negates an atom another clause might still produce); condition evaluation still allows data-level boolean/comparator predicates such as `rl2:neq` and `rl2:isNoneOf` as ground terms over the fixed `Env`.

### Derivation vs Resolution

| Property | Out (Derivation) | Eval (Full) |
|----------|------------------|-------------|
| Monotone in policy universe `U` (fixed `Env`) | Yes | No |
| Monotone in environment `Env` | No (conditions may be anti-monotone) | No |
| Deterministic | Yes | Yes |
| Conflict-handling | None (contradiction is data) | Strategy-based |
| Output | Set of atoms (dedup by canonical identity) | Single decision |

The `Eval` function composes `Out` with state updates and conflict resolution:

```
Eval(U, R, Σ, Ctx, strategy) =
    let Env = mkEnv(R, Σ, Ctx)
    let envelope = Out(U, Env)                    -- ① Derivation (monotone)
    let Σ' = updateDutyStates(envelope, Env, Σ)   -- ② State transitions
    let decision = resolveDecision(envelope, Σ', strategy)  -- ③ Resolution (non-monotone)
    in (decision, Σ', duties(envelope, Σ'))

duties(envelope, Σ') = { d | obligate(d, P) ∈ envelope, Σ'.ObligationState(d) ∈ {Pending, Active} }
```

`duties(envelope, Σ')` is the returned `DutySet` (Pending/Active duties still requiring
fulfillment, per **PermitWithObligations Semantics** below) — it is read against `Σ'`, not
`envelope` alone, for the same reason `violated(d,P)` is not an `Out` atom: `obligate(d,P)`
only records that `d` matched and its effective condition held *before* stage ②; whether `d` is
now `Pending`, `Active`, `Fulfilled`, or `Violated` is a `Σ'` fact.

The **normative envelope** `Out(U, Env)` is the first-class intermediate result — visible before resolution, available for audit, and monotone in the policy universe (for a fixed environment).

Resolution may eliminate norms via priority or strategy, breaking monotonicity. This is by design: `permit(a,x,s) ∧ forbid(a,x,s)` is not a logical contradiction but a **conflict to be resolved procedurally**.
`resolveDecision` is a parameterized algorithm (strategy + priorities); if these inputs cannot break ties, the evaluator must surface an explicit ambiguity/error rather than applying an implicit specificity heuristic.

For architectural context on the full evaluation pipeline, see **RL2_Architecture.md** §Evaluation Pipeline.

---

## Big-Step Semantics (Policy Evaluation)

This section is **not** a second, independent definition of policy evaluation. `Out` (above)
is the sole derivation rule; what follows unfolds `Eval` one level to name the intermediate
quantities an informal "match → evaluate condition → update duties → resolve" description
would use — each one is read off `Out`'s envelope or `Σ'`, never recomputed independently of
`deriveNorms`.

### Evaluation Function Signature

The total decision function takes a policy universe and Request as first-class parameters:

```
Eval : (PolicyUniverse U, Request R, State Σ, Context Ctx, Strategy strategy) → (Decision, State, DutySet)
```

Where:
* `U` is the universe of policies (the current generation)
* `R = (a_req, x_req, s_req)` is the request (agent, action, asset)
* `Σ` is the current system state
* `Ctx` is the external context (assertions from Protocol's ContextAssertion)
* `strategy` is the evaluator-supplied conflict-resolution strategy (S7: evaluator
  configuration, not policy vocabulary — no policy or clause carries its own strategy)
* `Decision ∈ {Permit, Deny, PermitWithObligations, NotApplicable, Indeterminate}`
* The returned `State` reflects any state updates from evaluation
* `DutySet` contains duties in Pending or Active state requiring fulfillment

### Evaluation Algorithm (Unfolded)

```
Eval(U, R, Σ, Ctx, strategy) =
    let Env = mkEnv(R, Σ, Ctx)

    -- Step 1: Derive the envelope. deriveNorms already folds effectiveCondition(P,n) per
    -- clause for every P ∈ U — there is no separate ApplicablePolicies pre-filter (see
    -- Pre-Resolution Normative Envelope).
    let envelope = Out(U, Env)

    -- Step 2: Name the envelope's atoms by kind (S2: a matched norm whose effective
    -- condition is Unknown is `indeterminate` — collected, never silently dropped).
    let activePrivileges   = { n | permit(n, P) ∈ envelope }
    let activeProhibitions = { n | forbid(n, P) ∈ envelope }
    let obligated           = { d | obligate(d, P) ∈ envelope }
    let indeterminateAtoms  = { i ∈ envelope | i = indeterminate(n, P, causes) }

    -- Step 3: Update duty states (Duty Activation/Fulfillment/Violation rules above).
    -- Active/Violated classification reads the post-transition Σ', not the pre-transition
    -- envelope: obligate(d,P) only records that d matched and was True *before* this step.
    let Σ' = updateDutyStates(envelope, Env, Σ)
    let activeDuties   = { d ∈ obligated | Σ'.ObligationState(d) ∈ {Pending, Active} }
    let violatedDuties = { d ∈ obligated | Σ'.ObligationState(d) = Violated }

    -- Step 4: Resolve. resolveDecision(envelope, Σ', strategy) is the sole public
    -- signature — it derives the definite categories above and retains complete attributed
    -- Unknown atoms for the priority/strategy outcome test (see Conflict Resolution below).
    let decision = resolveDecision(envelope, Σ', strategy)

    in (decision, Σ', duties(envelope, Σ'))
```

**Indeterminate handling (S2).** `resolveDecision(envelope, Σ', strategy)` retains each complete
`indeterminate(norm,policy,causes)` atom. It computes the finite set of resolver summaries
reachable when each Unknown is independently inactive or active, then maps those summaries
through the same priority/strategy decision function. A single reachable decision is conclusive;
more than one yields `Indeterminate`. The summary space is polynomial and does not enumerate the
`2^|I|` truth assignments. Mapping
`Indeterminate → Deny` is an **enforcement-adapter** decision (a fail-closed PEP), **not** the
semantic verdict: `Eval` returns `Indeterminate` so the ambiguity is auditable.

### Conflict Resolution

When multiple norms apply, conflicts must be resolved. RL2 provides two complementary mechanisms:

1. **Policy-level priority** (`rl2:priority`): Norms may declare an integer priority; higher values override lower. This is vocabulary defined in the ontology.

2. **Evaluator-level strategy**: The evaluator is configured with a conflict resolution strategy (e.g., prohibit-overrides, permit-overrides). This is **evaluator configuration**, not policy vocabulary—analogous to XACML combining algorithms.

The `strategy` parameter in `resolveDecision` below represents evaluator configuration. Policies express norms and priorities; evaluators decide how to combine conflicting results when priorities are equal. Four strategies are defined: `ProhibitOverrides`, `PermitOverrides`, `SpecificOverridesGeneral`, and `Invalid`.

More sophisticated defeasibility mechanisms—such as exclusionary rules—are available in frameworks like LegalRuleML [LegalRuleML] and may be incorporated in future RL2 profiles.

#### Specificity key (SEM-9)

`SpecificOverridesGeneral` needs a total ordering over competing norms *after* the global
priority step. Specificity is therefore a lexicographic pair computed statically per norm —
action subsumption depth, then condition atom count. Declared priority is not repeated inside
this metric because all candidates reaching `mostSpecific` are already in one maximal-priority
stratum:

```
actionDepth(x) = |{ y : Action | x ⊑ y, y ≠ x }|   -- count of x's proper ancestors under ⊑
    -- Static: one traversal of the fixed `rl2:includedIn` closure per action, the same cost
    -- and direction-dual of the compiler's descendant-oriented `subsumptionIndex` (RL2_IR.md
    -- §4, `map<Action, set<Action>>`, used for eval-time match membership). NOT the EXPR-2
    -- runtime quorum counting that is out of scope for the specified core — this is a
    -- compile-time property of the fixed action hierarchy, bounded per ACT-1/2.

atomCount(oc: Condition?) = case oc of        -- oc is n.condition (optional, per grammar)
    None    → 0
    Some(c) → atoms(c)

atoms(c) = case c of
    AtomicConstraint(_)         → 1
    EventConstraint(_)          → 1
    And(cs) | Or(cs) | Xone(cs) → Σ_{c' ∈ cs} atoms(c')
    Not(c')                     → atoms(c')

Specificity = ActionDepth × AtomCount
specificity(n) = (actionDepth(n.action), atomCount(n.condition))  -- lexicographic
```

A single lexicographic metric applies uniformly across `Privilege` and `Prohibition` — the
design choice SEM-9 flagged as needed, not a theorem. This eliminates *incomparability* by
construction: every norm has a well-defined `specificity` pair under a fixed total order on
tuples. The resolver summary retains the maximal pair separately for Privileges and
Prohibitions; equality of those two maxima is an opposite-effect tie.

`resolveDecision(envelope, Σ', strategy)` is the **only public signature** for conflict
resolution: policy universe, Request, and Σ never surface as separate resolution arguments.
It retains attributed Unknown atoms and projects definite/possible activations into the compact
`ResolverSummary` consumed by `decisionOf`.

```
resolveDecision(envelope, Σ', strategy) =
    let known    = { a ∈ envelope | kind(a) ≠ indeterminate }
    let unknowns = { a ∈ envelope | kind(a) = indeterminate }
    let initial  = summarize(known, Σ')
    let summaries = choiceFold(canonicalOrder(unknowns), {initial}, Σ')
    let decisions = { decisionOf(s, strategy) | s ∈ summaries }
    in if |decisions| = 1 then the element of decisions else Indeterminate

activate(indeterminate(n : Privilege,   P, _)) = permit(n, P)
activate(indeterminate(n : Prohibition, P, _)) = forbid(n, P)
activate(indeterminate(d : Duty,        P, _)) = obligate(d, P)

priority(n) = n.priority if declared, otherwise 0

ResolverSummary =
    { topPriority       : Integer?,
      bestPrivilegeSpec : Specificity?,
      bestProhibitSpec  : Specificity?,
      hasActiveDuty     : Boolean,
      hasViolatedDuty   : Boolean }

emptySummary = { None, None, None, false, false }
summarize(atoms, Σ') = fold(addAtom(_, _, Σ'), emptySummary, canonicalOrder(atoms))

canonicalOrder(atoms) = sort atoms by (sourcePolicyId, sourceClauseId, atomKind)
optionMax(None, x)    = Some(x)
optionMax(Some(y), x) = Some(max(y, x))

addAtom(s, permit(n, P), Σ')   = addAccess(s, Privilege, priority(n), specificity(n))
addAtom(s, forbid(n, P), Σ')   = addAccess(s, Prohibition, priority(n), specificity(n))
addAtom(s, obligate(d, P), Σ') =
    case Σ'.ObligationState(d) of
        Pending | Active → s[hasActiveDuty ↦ true]
        Violated         → s[hasViolatedDuty ↦ true]
        _                → s

addAccess(s, kind, p, spec) =
    if s.topPriority = None ∨ p > s.topPriority then
        { topPriority: p,
          bestPrivilegeSpec: if kind = Privilege then Some(spec) else None,
          bestProhibitSpec:  if kind = Prohibition then Some(spec) else None,
          hasActiveDuty: s.hasActiveDuty,
          hasViolatedDuty: s.hasViolatedDuty }
    else if p < s.topPriority then s
    else if kind = Privilege then
        s[bestPrivilegeSpec ↦ optionMax(s.bestPrivilegeSpec, spec)]
    else
        s[bestProhibitSpec ↦ optionMax(s.bestProhibitSpec, spec)]

choiceFold([], summaries, Σ') = summaries
choiceFold(i :: rest, summaries, Σ') =
    let next = summaries ∪ { addAtom(s, activate(i), Σ') | s ∈ summaries }
    in choiceFold(rest, next, Σ')
    -- retaining s chooses Unknown=False; addAtom chooses Unknown=True

hasPrivilege(s)  = s.bestPrivilegeSpec ≠ None
hasProhibition(s) = s.bestProhibitSpec ≠ None

baseDecision(s) =
    if ¬hasPrivilege(s) then NotApplicable
    else if s.hasViolatedDuty then Deny
    else if s.hasActiveDuty then PermitWithObligations
    else Permit

decisionOf(s, strategy) =
    case strategy of
        ProhibitOverrides →
            if hasProhibition(s) then Deny else baseDecision(s)

        PermitOverrides →
            if hasPrivilege(s) then baseDecision(s)
            else if hasProhibition(s) then Deny
            else NotApplicable

        SpecificOverridesGeneral →
            case (s.bestPrivilegeSpec, s.bestProhibitSpec) of
                (None, None)       → NotApplicable
                (Some(_), None)    → baseDecision(s)
                (None, Some(_))    → Deny
                (Some(p), Some(f)) → if p > f then baseDecision(s)
                                      else if f > p then Deny
                                      else Indeterminate

        Invalid →  -- ODRL "invalid": a conflict in the maximal-priority stratum is surfaced
            if hasPrivilege(s) ∧ hasProhibition(s) then Indeterminate
            else if hasProhibition(s) then Deny
            else baseDecision(s)

        _ → -- Default: prohibit-overrides
            if hasProhibition(s) then Deny else baseDecision(s)
```

`addAtom` uses only `max` and Boolean disjunction, so definite summarization is order-independent.
`choiceFold` is exact for all joint Unknown activations but deduplicates after every step by
summary equality. For `n` access atoms there are at most `O(n³)` summaries: `O(n)` possible top
priorities, `O(n)` best Privilege specificities, `O(n)` best Prohibition specificities, and four
duty-flag pairs. A direct implementation that scans each candidate top-priority stratum and the
two reachable best-specificity sets computes the same summaries in `O(n³)` time and polynomial
space; it need not materialize the powerset. This bounded summary construction, not a solver or
entailment engine, is the conformance model.

Normative boundary consequences include:

- Under `PermitOverrides`, a definite Privilege plus an equal-priority Unknown Prohibition is
  `Permit`: either activation choice permits.
- Under `PermitOverrides`, a definite Prohibition plus an equal-priority Unknown Privilege is
  `Indeterminate`: the choices yield Deny and Permit.
- Under `Invalid`, a lower-priority definite Prohibition, a violated Duty, and two Unknown
  equal-higher-priority access atoms (one Privilege, one Prohibition) are `Indeterminate`.
  Activating either Unknown alone still yields Deny, but activating both creates a top-stratum
  conflict; retaining joint reachable summaries is therefore necessary.

`Indeterminate` here is the same value produced per-norm in the denotations above and carried
by `rl2p:Indeterminate` at the protocol layer; a fail-closed PEP maps it to `Deny`, but that
mapping lives in the enforcement adapter, not in `resolveDecision`.

Note: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

### Duty State Updates

`updateDutyStates` in the Evaluation Function is the batch application of the
single-duty rules in **Duty Activation**, **Duty Fulfillment (Achievement)**,
**Duty Violation (Achievement)**, **Duty Fulfillment (Maintenance)**, and
**Duty Violation (Maintenance)** above. Those rules are the sole normative
definition; this section does not define a second lifecycle algorithm.

For every selected Duty, at most one legal transition is emitted from the input
snapshot. `Fulfilled` and `Violated` are terminal, and an `Unknown` condition
emits no transition. Updates to distinct Duties are combined as disjoint
`ObligationState` map updates.

### PermitWithObligations Semantics

When `Eval` returns `PermitWithObligations`:
* The semantic decision is `PermitWithObligations`
* The returned `DutySet` contains duties that must be fulfilled
* Duties may be in `Pending` (activation condition not yet met) or `Active` (must be performed)
* The Protocol's Requirement class captures these for tracking

The current core does not yet distinguish blocking, concurrent, and post-use
Duties. Conditions determine activation, but do not by themselves define an
enforcement phase; that association remains part of C3-4/P4.

### Note on Evaluation Complexity

Policy evaluation in RL2 is inherently **stateful** and may span **multiple events over time**. Unlike simple access-control decisions, RL2 evaluation must track:

* The lifecycle of duties (Pending → Active → Fulfilled/Violated)
* Promise states across temporal boundaries
* Event sequences that trigger state transitions
* Dynamic operand resolution at each evaluation point

A complete formal treatment of multi-event evaluation—including evaluation contexts, event ordering, and cumulative state—is deferred to a future specification. The current semantics define:

1. **Point-in-time evaluation**: Given a request, state, and context, compute a decision
2. **State transition rules**: How individual events modify Σ
3. **Conflict resolution**: How to decide when multiple norms apply

The composition of these into a full **evaluation trace** semantics (handling event streams, concurrent duties, and long-running workflows) requires additional machinery and is noted as future work.

---

## Constraint Algebra Semantics

Constraints form a Boolean algebra with additional temporal operators.

Properties:

* Associativity, commutativity, idempotence for And/Or
* De Morgan laws
* Temporal and contextual constraints orthogonal to logical structure
* Dynamic operands resolved at evaluation time
* Path-based evaluation is deterministic (fully resolved from Env)

This ensures determinism of constraint evaluation.

---

## Event Semantics

Events influence evaluation by causing transitions.

```
Σ ⊢ e ≫ Σ'
```

Event types:

* ActionPerformed
* ApprovalGranted
* TimeAdvanced
* MetadataChanged
* ExternalSignal

Transitions update:

* PromiseState
* DutyState
* Clock
* AssetCollection materializations

---

## Role Resolution Semantics

Roles are evaluated as:

* **Normative roles**:

  ```
  subject = agent bearing normative burden
  counterparty = agent holding corresponding right
  ```
* **Functional roles**:

  ```
  grantor = agent who issues policy
  grantee = agent who receives privilege
  approver = agent whose approval is required
  operator = agent performing duties
  ```

Role resolution rules ensure that every role reference is type-correct and semantically consistent.

---

## Policy Composition Semantics

Policies can be composed via clause union:

```
P1 ⊔ P2 = Policy { clauses: P1.clauses ∪ P2.clauses }
```

Conflict resolution reduces to condition calculus:
- If two norms conflict, policy-level or clause-level precedence applies
- RL2 supports ODRL conflict semantics via the `resolveDecision` function

**Note on Inheritance**: ODRL's `inheritFrom` mechanism is intentionally not supported in RL2. Policy inheritance introduces complexity (flattening, override semantics, auditability issues) without clear benefit over explicit composition. See **issues.md** § Open Decisions (OPEN-3).

---

## State Scope, Identity, and Concurrency (S5)

Runtime state must be scoped correctly, or two evaluators can both observe the same count and both
permit a request that should have been refused. RL2 pins state to **two identity tiers and no
more**, mirroring the object-oriented distinction between *class variables* and *instance
variables*.

### The two tiers (class vs instance)

| OOP | RL2 | Holds |
|-----|-----|-------|
| **class** (template) | **Offer** — immutable, authored once, accepted many times | class variables: state **shared** across all its acceptances |
| **instance** (object) | **Agreement** — one per acceptance | instance variables: state **isolated** per acceptance |
| `new` / constructor | **`materialize(Offer, Acceptance)`** (§Materialization) | mints the instance and its fresh instance-variable cells |

- **Immutable policy identity vs materialized identity.** An **Offer** is a stateless catalog
  document: it holds no runtime state and is never mutated by evaluation. An **Agreement** is the
  stateful instance. The two are linked by `Agreement prov:wasDerivedFrom Offer` (recorded by
  `materialize`, §Materialization). A directly-authored `Set` policy that is never materialized is
  its own single instance (class and instance coincide).
- **Instance variables (the default, ~all cases).** `materialize` already mints a **fresh IRI for
  every clause** it places in an Agreement, so each Agreement's `ObligationState`, counters, and
  duty state are keyed by IRIs unique to that Agreement. Σ stays keyed by bare IRI; isolation
  between acceptances is automatic and needs **no new machinery**. This is how the entire existing
  corpus already behaves.
- **Class variables (the rare, explicit exception).** Some limits are enforced *across* all live
  Agreements of one Offer — a pool of *N* concurrent seats, a shared quota. That state belongs to
  the **Offer tier** and is read through the `global.*` root (above) / `rl2p:GlobalLeftOperand`.
  It is **never coerced onto the common path**: an operand is Offer-tier only when it explicitly
  says so.

**The Offer is the ceiling.** There is deliberately no tier above the Offer — no tenant-wide or
global-across-Offers state. Cross-Offer coupling is out of scope for the core; a deployment that
needs it layers it outside the specified core.

### Active-Agreement set and derived shared limits

Most shared limits are **derived, not stored** — they need no mutable shared cell at all:

```
activeAgreements(Offer, Σ) = { A | A prov:wasDerivedFrom Offer ∧ active(A, Σ) }
```

where `active(A, Σ)` holds while Agreement `A` is in force. The predicate's transitions
(commencement, expiry, termination) are the **temporal lifecycle of WP-4**; this step fixes only
the *set* it feeds. A concurrent-seat limit is then the read-only aggregate

```
seatsUsed(Offer, Σ) = |activeAgreements(Offer, Σ)|          -- resolved into global.*, read-only
```

and admission is the ordinary condition `global.…count < N`. Because nothing is written, there is
no shared-counter race for the derived case. A genuinely **accumulating** shared counter (a pooled
quota drawn down and written back across parties) is *not* expressible in the read-only core; a
profile MAY back a `global.*` operand with an external, resolver-maintained counter, but — like any
`rl2:resolutionFunction` aggregation (S8a) — it is **outside the specified core** and gets no
totality/determinism guarantee.

### Versioned snapshot and commit (concurrency)

Even a derived limit has a check-then-act race: two evaluators both read `seatsUsed = N−1` and both
admit. RL2 makes evaluation a **pure function over a versioned snapshot**, and pushes the race into
a single commit rule:

```
Snapshot = (Σ, version : ℕ)          -- version is monotone; each committed transition increments it
evalIR / Out are pure over a fixed Snapshot (they never mutate Σ; effects are returned, RL2_IR.md §7)
commit(Snapshot_v, effects):
    succeeds and yields Snapshot_{v+1} = (applyEffects(effects, Σ), v+1)   iff current version = v
    otherwise FAILS (conflict) → the caller re-resolves and re-evaluates against the new snapshot
```

This is compare-and-swap on `version`. A policy that reads Offer-tier (shared) state — i.e. any
admission against `global.*` — **MUST** commit under this CAS / a serializable transaction, so a
concurrent admitter cannot slip in between the read and the commit. A purely **case-local** policy
(only instance-variable state, the common path) MAY commit under snapshot isolation, since its
writes touch IRIs no other case shares. The *mechanism* — locks, transactions, storage, retry — is
a deployment concern **outside the specified evaluator core** (I4): the evaluator's obligation is only that the
pure transition and effect set it computed for version `v` are exactly what gets applied when `v`
is still current. Duplicate and late-arriving events are handled by the idempotent, append-only
`processEvent` rule (§State Update / operational semantics): a committed decision is replay-stable
for its snapshot version and is never rewritten by a later-arriving earlier-time event.

**Commit validity is re-derivation, not trust (I4, RL2_IR.md §7.3).** The version check alone
guarantees no *other* transition landed between read and write; it does not by itself guarantee
the `effects` being committed are the ones the pure evaluator computed for `v` (a retried or
memoized request could carry a stale `fx` alongside a `v` that happens to still be current).
`commit` therefore obtains `(CU, _) = compile(U)` and recomputes `fx` from
`evalIR(CU, R, Snapshot_v.Σ, Ctx, strategy)` at commit time rather than accepting a
caller-supplied effect set on trust — `RL2_IR.md §7.3`'s
`validateCommit`. This makes retries free to leave outside the proof: an unchanged-`v` retry
recomputes the same `fx` (determinism, RL2_IR.md §9) and commits as a no-op; a retry after `v`
has advanced fails CAS and forces the caller back to re-evaluation against the new snapshot.
Effect-set conflicts within a single `fx` (e.g. two clauses disputing one duty's next state) are
precluded at derivation time, not resolved at commit time — `RL2_IR.md §7.1`'s `deriveEffects`
keys each `TransitionDuty` by the duty it transitions, not by the clause that mentioned it, so
`Σ.ObligationState(d)` and `Env` alone determine the (at most one) effect for `d`.

### Shared-strong-state vs case-local (deployment consequence)

This tier split is exactly the shared-vs-local distinction the S5 review finding (issues.md,
WP-3) asks for, and it drives deployment cost:

- **Case-local** (default, instance variables only): evaluable from a snapshot scoped to the one
  Case/Agreement; no cross-request coordination; horizontally scalable.
- **Shared-strong-state** (reads `global.*`): needs a consistent view of the Offer's active-Agreement
  set and serializable commit; this is the only class of policy that requires strong coordination,
  and authors opt into it visibly by declaring a `GlobalLeftOperand`.

## Policy Generations

A **generation** is the complete set of policies in force at a point in time — the "law of the land."

## Three-Level Model

```
Level 0: State (Σ)           - current facts, events, duty states
Level 1: Active policies     - policies whose conditions hold NOW
Level 2: Policy generation   - all policies that COULD apply (fixed)
```

## Key Properties

* **Events at Level 0 change Level 1**, not Level 2. An event may activate or deactivate a policy, but cannot modify the generation.
* **Generation changes occur outside normal state transitions**. Writing new policy, amending existing policy, or repealing policy creates a new generation — this is legislation, not execution.
* **Cases carry their generation identifier** for auditability. A case is evaluated under the generation in effect when it was created.
* **The state machine does not modify itself**. This ensures tractable semantics and reproducible evaluation.

## Why Generations Matter

* **Reproducibility**: Given a case and its generation, evaluation is deterministic
* **Auditability**: You can always identify which policy universe was in effect
* **Tractability**: State transitions are well-defined within a fixed policy set
* **Versioning**: Supports policy lifecycle management and grandfather clauses

## Analogy

A court case proceeds under the laws in effect when filed (one generation). If the legislature passes new law, that creates a new generation. The case may continue under the old generation (grandfather clause) or transition to the new generation, depending on the rules — but the case's progression doesn't modify the laws themselves.

---

## Interoperability and Compilation

While RL2 is a standalone language, it is designed to be a valid target for compilation from other policy languages.

We define a compilation function `C` such that for a legacy policy `P_legacy`:

```
C(P_legacy) → P_RL2
```

Where `P_RL2` is a semantically precise RL2 representation of the intent of `P_legacy`. This allows RL2 kernels to execute policies authored in ambiguous standards by first compiling them into RL2's rigorous operational structures.

---

## Protocol Correspondence

For the mapping between semantic concepts and Protocol artifacts, see **RL2_Architecture.md** §Correspondence.

---

## Complexity and Constraints

*This section is non-normative.*

RL2 evaluation is designed to be **polynomial-time** and **total** under the following constraints.

### Conformance Parameters (S8a)

The core's termination and polynomial-time guarantees depend on a small set of **conformance parameters** — named finite bounds a conforming implementation **MUST** enforce. Only the *values* are implementation- or profile-declared; the existence of each bound is mandatory, not a `MAY`. An implementation that omits any of these bounds is out of core conformance.

| Parameter | Default | Bounds |
|-----------|---------|--------|
| `MaxPathDepth` | 10 segments | `deref` path length |
| `MaxConditionDepth` | 20 | condition tree nesting; evaluation work is linear in tree size |
| `MaxCollectionSize` | implementation-declared | `members(s)` / event sequence length |
| `MaxPolicyUniverse` | implementation-declared | `|U|` |

### Structural Constraints

1. **Finite policy universe**: U is a finite set of policies (`≤ MaxPolicyUniverse`)
2. **Bounded condition nesting**: Conditions have bounded depth (`≤ MaxConditionDepth`, default 20)
3. **Acyclic conditions**: No self-referential condition definitions
4. **Finite Σ**: State contains finite sets (Events, Performed, ObligationState)
5. **No recursive policy references**: Policies cannot invoke evaluation of other policies

### Path Resolution Constraints

6. **Bounded path depth**: `≤ MaxPathDepth` (default 10), enforced by grammar
7. **No joins**: Path resolution is single-threaded navigation, not graph pattern matching
8. **No iteration**: `resolutionFunction` must be O(1) or O(log n) per invocation — **and is outside the specified core** (S8a); an opaque function falls outside the core guarantees unless the profile documents its bounds
9. **Deterministic selection**: Wildcards resolve to single values via most-recent-wins

### Complexity Analysis

Given these constraints:

| Operation | Complexity |
|-----------|------------|
| Path resolution (`deref`) | O(d) where d = path depth |
| Condition evaluation | O(n × d) where n = condition tree size |
| Norm matching | O(\|U\| × m) where m = max clauses per policy |
| Conflict resolution | O(k) where k = matched norms |
| **Total `Eval`** | **O(\|U\| × m × n × d)** — polynomial |

### Totality Guarantees

Under these constraints, `Eval` is **total**: it terminates for all well-formed inputs. The function never:

- Loops infinitely (no recursive evaluation)
- Blocks on external resources (resolution is synchronous or fails to ⊥)
- Diverges due to condition structure (bounded, acyclic)

**Extension warning (S8a)**: `resolutionFunction` and `lookupExternal` are **outside the specified core**. The totality/complexity guarantees stated for `evalCondition`/`evalIR` (RL2_IR.md §5, §9) cover only `resolutionPath`-based resolution and the bounded operations above. Implementations using unbounded external queries via `resolutionFunction` or `lookupExternal` may exhibit non-polynomial or non-terminating behavior; such extensions MUST document their determinism and complexity characteristics and are not covered by the core proof obligations.

---

## Proof scope and normative artifact

RL2's current scope is **specification, not mechanized proof or implementation** (SCOPE-1,
`issues.md`, 2026-07-29). The normative artifact is this document together with
**RL2_IR.md** (the AST, `evalCondition`, and `evalIR` design) and the SHACL-validated ontology
— not a verified evaluator in any particular language. Proof obligations (S1–S6 and
successors) are documented design properties of the specified evaluator (RL2_IR.md §5, §9),
stated precisely enough that a future implementation can be tested against them by
differential testing (RL2_IR.md §10), not properties discharged by a mechanized proof
assistant.

Datatype and function definitions in this document use Dafny-like algebraic-datatype notation
purely as precise pseudocode, consistent with RL2_IR.md's notational convention — this is not
a commitment to Dafny, or to any implementation language.

---

## Proof Obligations

The following are documented design properties of the specified evaluator (RL2_IR.md §5, §9),
stated precisely enough to test an implementation against, not properties discharged by a
mechanized proof assistant:

1. **(S1) Determinism**: Given Σ, R, Ctx, evaluation produces a unique result
2. **(S2) Progress**: Every well-typed expression either is a value or can step
3. **(S3) Preservation**: Types are preserved under transitions
4. **(S4) Duty-state consistency**: No duty can be both Fulfilled and Violated
5. **(S5) Timeout correctness**: Deadlines are eventually enforced
6. **(S6) Totality**: `Eval` terminates for all well-formed inputs

See **`RL2_IR.md`** §5 and §9 for the interpreter these properties are stated against
(`evalCondition`/`evalIR`), and its §10 for the differential-testing strategy that stands in
for mechanized proof.

For expressive characterization and comparison with other formalisms, see **RL2_Architecture.md**.

---

## References

See **RL2_References.md** for complete citations and glossary.

Related RL2 specifications:
- rl2.ttl — Core ontology (OWL)
- rl2-shacl.ttl — SHACL validation shapes
- RL2_Protocol.md — Runtime evaluation protocol
