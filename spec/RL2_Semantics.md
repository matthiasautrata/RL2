---
title: "RL2 Formal Semantics"
subtitle: "Deterministic Policy Meaning over Requests and World Snapshots"
version: "0.6"
status: "Draft"
date: 2026-07-24
abstract: |
  RL2 is a policy language designed as a rigorous successor to legacy rights languages. It integrates deontic logic, Promise Theory, and constraint algebra into deterministic evaluation semantics over a canonical policy universe, request, and immutable world snapshot.
---

## Introduction

Digital policy frameworks often lack formal normative foundations. ODRL 2.2 provides an expressive
information model and vocabulary but leaves important evaluator choices open, allowing independent
implementations to disagree about the result of the same policy.

RL2 (“Rights Language 2”) addresses these limitations by integrating ideas from:

* **Deontic Logic**
* **DPCL (normative meta-language)**
* **Promise Theory**
* **Temporal and evidence semantics**

RL2 is fully RDF-compatible, but its semantics are defined **at the abstract syntax level**, independent of serialization.

This document defines the formal semantics. `RL2_Model.md` defines the SCOPE-2 evaluation
interface; `../docs/RL2_Architecture.md` explains the design. Protocol and reference-evaluator
material under `../future/` is not part of core conformance.

> **SCOPE-2 transition notice.** The result/truth algebra, canonical syntax, condition semantics,
> norm derivation, and conflict resolution remain active core work. Sections that prescribe mutable
> state transitions, Cases, Requirements, event sourcing, effects, commit, or protocol projection
> are retained temporarily for extraction and historical traceability; they are not normative core
> requirements under `RL2_Scope.md`. Phase 4 of `../project/reorganization-plan.md` replaces the
> remaining transition-oriented duty and Promise rules with declarative status functions.

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
* **⊥** = legacy notation for an absent value; at an evaluator boundary it is
  `Err(Missing(ErrorKey), note)` in the Result and Truth Algebra below

We define RL2 expressions as:

#### Norms

```
Norm ::=
    Privilege(Agent, Action, Asset, Condition,
              prerequisiteDuties: finite set of Duty)
  | AchievementDuty(Agent subject, Agent? counterparty, Action, Asset, Condition,
                    postCondition: Condition?, dutyWindow: DutyWindow?)
  | MaintenanceDuty(Agent subject, Agent? counterparty, Asset, Condition,
                    invariant: Condition, dutyWindow: DutyWindow?)
  | Prohibition(Agent, Action, Asset, Condition)
  | Claim(Agent subject, Agent counterparty, Duty correlativeTo)
      -- subject = right-holder, counterparty = duty-bearer; required content, object,
      -- applicability condition, and window are DERIVED from correlativeTo (C6b), never
      -- authored — see Claim Denotation below.
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

`Condition` in both Duty forms is the ordinary applicability guard. Duty satisfaction is
structural: an Achievement Duty requires action evidence and may additionally require a
`postCondition`; a Maintenance Duty requires its `invariant` throughout its `dutyWindow` and has
no action. The two forms are mutually exclusive in canonical RDF; no separate mode field exists.

`Privilege.prerequisiteDuties` is projected from zero or more `rl2:prerequisiteDuty` values.
The set is conjunctive: every applicable member must be Fulfilled before the Privilege can
contribute a permit. An attached Duty is referenced by one or more Privileges and is not also a
top-level Policy clause. Sharing one Duty node shares its one status result across those
Privileges. A top-level Duty is independent and never gates an access decision.

```
DutyWindow = [startInclusive: Time, endExclusive: Time)
```

The window is finite when present. Absence means unbounded; it is not a second RDF spelling for an
interval with omitted endpoints.

#### Promises

```
Promise ::= Promise(Agent promisor, Agent promisee, Asset? object, PromiseContent)

PromiseContent ::=
    PromisedAction(Action)          -- Tun-sollen; object is Promise.object
  | PromisedState(Condition)        -- Sein-sollen; from rl2:promisedState
  | PromisedDuty(Duty)              -- suretyship status; core acceptance rejects this form
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
    | EventConstraint(expectsEvent: EventPattern)
```

Notes:
- `And`, `Or`, and `Xone` take at least two conditions, matching
  `AndOrXoneOperandCardinalityShape`
- `EventConstraint` models evidence-sensitive requirements; it uses an explicit selector over
  `W.evidence`
- `leftOperand` is drawn from profile-defined operands (RL2 Core defines `rl2:LeftOperand` class plus `currentDateTime`, `obligationStateOperand`, `dutyPerformerOperand`, `promiseStateOperand`, `promisorOperand` instances)
- Time-based conditions use `AtomicConstraint` with `leftOperand = currentDateTime` (e.g., `currentDateTime lte deadline`)
- Dynamic value resolution on the left side uses `LeftOperand` with `resolutionPath`
- Dynamic value resolution on the right side uses `RuntimeReference` (e.g., `currentAgent`)
- The stable RDF property `rl2:targetNorm` is interpreted as the tagged `StateTarget` defined
  below, preserving whether it references a Norm or a Promise

#### Evidence Patterns

```
EventPattern ::= eventPattern(eventKind, actor?, action?, object?, payloadPattern, interval?)
```

Persistent events and state transitions are not policy-language expressions. The immutable
`Evidence` records matched by this pattern are part of `WorldSnapshot` (`RL2_Model.md` §4).

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

The Duties reachable from a Policy are:

```
independentDuties(P) = { d : Duty | d ∈ P.clauses }
attachedDuties(P)    = ⋃ { n.prerequisiteDuties | n : Privilege ∈ P.clauses }
allDuties(P)         = independentDuties(P) ∪ attachedDuties(P)
```

SHACL rejects a Duty that occurs in both sets. An attached Duty's policy provenance is the set of
Policies containing Privileges that reference it; one `obligate(d,P)` atom is derived per such
Policy when at least one matching owner makes the Duty applicable.

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
τ ::= Agent | Action | Asset | Condition | Time | Boolean | Norm | Promise | DutyWindow
    | EventPattern | WorldSnapshot | EvaluationConfiguration | EvaluationResult
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
Γ ⊢ a : Agent     Γ ⊢ b : Agent?      Γ ⊢ x : Action     Γ ⊢ s : Asset
Γ ⊢ c : Condition Γ ⊢ pc : Condition? Γ ⊢ w : DutyWindow?
--------------------------------------------------------------------------------
        Γ ⊢ AchievementDuty(a, b, x, s, c, pc, w) : Norm

Γ ⊢ a : Agent     Γ ⊢ b : Agent?      Γ ⊢ s : Asset      Γ ⊢ c : Condition
Γ ⊢ i : Condition Γ ⊢ w : DutyWindow?
--------------------------------------------------------------------------
        Γ ⊢ MaintenanceDuty(a, b, s, c, i, w) : Norm
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
- evidence is selected by explicit kind, actor, action, object, payload, and interval fields;
- occurrence time, not arrival order or a storage sequence, determines temporal eligibility;
- tied latest projections with unequal values yield `Conflict` rather than an arbitrary winner;
- no Case, Requirement, append log, stored Duty state, or stored Promise state is part of `W`.

`state.Clock` is an authored path spelling for `W.evaluationTime`. `state.Events...` is an
authored path spelling for an evidence query. Other declared fact paths resolve through
`W.facts`. Duty and Promise statuses are derived from policy content and `W`; S2-C2 defines the
total status functions.

### Environments

```
Env = (Universe, Request, Agent, Asset, Snapshot, Configuration)
```

A named six-field record (not a bare product), used for evaluating matching and operand paths.
The fields correspond one-to-one with the canonical path roots (`request.*`,
`agent.*`, `asset.*`, `state.*`, `context.*`, `global.*`):

- `Universe` — the immutable canonical PolicyUniverse and its finite term-inclusion indexes
- `Request` — the core request being evaluated
- `Agent`   — the requesting agent (`Request.requestingAgent`; what `rl2:currentAgent` resolves to)
- `Asset`   — the requested asset
- `Snapshot` — the immutable `WorldSnapshot`
- `Configuration` — profiles, bounds, trust parameters, and conflict strategy

`context.*` and `global.*` are scoped fact paths within `Snapshot`; they are not separate live
objects. `Env` contains no callback, source adapter, or mutable record.

---

## Denotational Semantics

Denotational semantics gives timeless meaning to norms and conditions.

### Result and Truth Algebra (S2)

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

Event constraints use the snapshot evidence selector defined in `RL2_Model.md` §4.3. Absence of
matching evidence is `False`; malformed or inadmissible relevant evidence remains an attributed
error rather than being treated as absence:

```
⟦ EventConstraint(expectsEvent) ⟧(Env) : ConditionResult =
    case existsEvidence(selector(expectsEvent, Env.Universe),
                        Env.Snapshot, Env.Configuration) of
        Ok(true)  → { truth: True,    causes: ∅ }
        Ok(false) → { truth: False,   causes: ∅ }
        Err(e, _) → { truth: Unknown, causes: {e} }
```

`selector(expectsEvent)` contains the event kind and every actor, action, object, payload, and
interval restriction declared by the pattern. It adds no implicit Case or Request scope.

---

### Helper Function Specifications

The condition semantics rely on several helper functions. For a testable evaluator, these must be precisely specified.

#### resolve : LeftOperand × Env × StateTarget? → EvalValue\<Value\>

The function `resolve(leftOperand, Env, targetNorm?)` maps a left operand to an
`EvalValue<Value>` (S2): `Ok(v)` on success and `Err(error,note)` on failure. Although the RDF
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
        -- Core derived-status operands (completed by S2-C2)
        obligationStateOperand →
            case targetNorm of
                Some(NormTarget(d : Duty)) →
                    resolveDutyStatus(d, Env.Universe, Env.Snapshot, Env.Configuration)
                None → failure(Missing, op, None, "obligationStateOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "obligationStateOperand requires a Duty target")
        dutyPerformerOperand →
            case targetNorm of
                Some(NormTarget(d : Duty)) →
                    resolveDutyPerformer(d, Env.Universe, Env.Snapshot, Env.Configuration)
                None → failure(Missing, op, None, "dutyPerformerOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "dutyPerformerOperand requires a Duty target")
        promiseStateOperand →
            case targetNorm of
                Some(PromiseTarget(p)) →
                    resolvePromiseStatus(p, Env.Universe, Env.Snapshot, Env.Configuration)
                None → failure(Missing, op, None, "promiseStateOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "promiseStateOperand requires a Promise target")
        promisorOperand →
            case targetNorm of
                Some(PromiseTarget(p)) → Ok(p.promisor)
                None → failure(Missing, op, None, "promisorOperand requires a targetNorm")
                _    → failure(Invalid, op, targetNorm, "promisorOperand requires a Promise target")

        -- Profile-declared snapshot operands
        _ | op.resolutionPath ≠ ⊥ →
            deref(op.resolutionPath, op, Env)

        -- An opaque resolver may be used while assembling a snapshot, never by core Eval.
        _ | op.resolutionFunction ≠ ⊥ →
            failure(Invalid, op, targetNorm,
                    "resolutionFunction is outside core Eval; supply a snapshot binding")

        _ → failure(Missing, op, targetNorm, "operand has no core or snapshot binding")
```

Where:
* `obligationStateOperand` accepts `NormTarget(d : Duty)` and queries the derived Duty status
* `dutyPerformerOperand` accepts `NormTarget(d : Duty)` and projects the unambiguous fulfillment
  witness selected for that Duty
* `promiseStateOperand` accepts `PromiseTarget(p)` and queries the derived Promise status
* `promisorOperand` accepts `PromiseTarget(p)` and reads the Promise's immutable policy content
* `op.resolutionPath` — path expression declared on the operand via `rl2:resolutionPath`
* `op.resolutionFunction` — an optional snapshot-assembly hint outside core evaluation
* `Err(Missing(key),note)` indicates the operand could not be resolved (S2) — never fatal,
  always lifted to `Unknown` at the condition level; a present target of the wrong variant is
  `Err(Invalid(key),note)` instead

All policy-visible contextual data uses declared `rl2:LeftOperand` instances. Core operands have
the fixed branches above; profile operands use an explicit snapshot path. This provides:

- Type safety (operands can declare expected ranges)
- Validation (SHACL can verify operand usage)
- Specifiability (one finite lookup algorithm)
- Auditability (all data access points are declared)

RL2 Core defines the following left operand instances:

* `obligationStateOperand` → derived Duty status (requires a Duty-valued `targetNorm`)
* `dutyPerformerOperand` → derived fulfillment actor (requires a Duty-valued `targetNorm`)
* `promiseStateOperand` → derived Promise status (requires a Promise-valued `targetNorm`)
* `promisorOperand` → the promisor declared by the targeted Promise

Profiles define domain-specific left operands with resolution paths, such as:
* `purpose` → `rl2:resolutionPath "context.purpose"`
* `dataOwner` → `rl2:resolutionPath "asset.dataOwner"`
* `eventPerformer` → `rl2:resolutionPath "state.Events.*.operationalAgent"`
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

#### deref : Path × LeftOperand × Env → EvalValue\<Value\>

`deref` interprets a declared path as a key into the normalized snapshot. It never traverses a
host-language object or invokes a connector.

```text
Path       ::= Root ('.' Segment)*
Root       ::= 'agent' | 'asset' | 'context' | 'state' | 'request' | 'global'
Segment    ::= Identifier | Wildcard
Identifier ::= [a-zA-Z_][a-zA-Z0-9_]*
Wildcard   ::= '*'
```

The wildcard is permitted only immediately after `state.Events`. A path exceeding
`MaxPathDepth`, using another root, containing an empty segment, or containing `/`, `\\`, `%`,
`..`, or an escape sequence is rejected during canonical projection. Paths are data keys, not
filesystem or language-level member expressions.

The only canonical `request.*` paths are `request.requestingAgent`,
`request.requestedAction`, and `request.requestedAsset`. Any other `request.*` path is rejected
during canonical projection.

```text
deref(path, op, Env) =
    case path of
        "request.requestingAgent" → requestField(Env.Request, requestingAgent, path)
        "request.requestedAction" → requestField(Env.Request, requestedAction, path)
        "request.requestedAsset"  → requestField(Env.Request, requestedAsset, path)
        "request." + _            → failure(Invalid, path, None,
                                             "unsupported core Request field")
        "state.Clock"             → Ok(Env.Snapshot.evaluationTime)
        EventProjection(rawSelector, field) →
            let expanded = expandEventSelector(rawSelector, Env.Universe) in
            projectLatestEvidence(expanded, field, declaredType(op),
                                  Env.Snapshot, Env.Configuration)
        _ →
            case factKey(path, Env.Agent, Env.Asset) of
                Err(e,note) → Err(e,note)
                Ok(key) → resolveFact(key, declaredType(op), declaringProfile(op),
                                      Env.Snapshot, Env.Configuration)
```

`requestField(None,_,path)` returns `Invalid(OperandSite(path))`; a request path therefore cannot
silently read a Duty or Promise status environment. `factKey` is total over canonical non-event
paths when the required scope is present:

```text
factKey("agent."   + rest, a, _)       = Ok(AgentScope(a), canonicalPath)
factKey("asset."   + rest, _, Some(s)) = Ok(AssetScope(s), canonicalPath)
factKey("asset."   + rest, _, None)    = failure(Missing, canonicalPath, None,
                                                  "status content has no asset scope")
factKey("context." + rest, _, _)       = Ok(EvaluationScope, canonicalPath)
factKey("state."   + rest, _, _)       = Ok(StateScope, canonicalPath)
factKey("global."  + rest, _, _)       = Ok(GlobalScope, canonicalPath)
```

`request.*` has exactly the three fields in the core Request. Additional request metadata must be
a declared `context.*` fact or belong to an interchange profile; an evaluator cannot invent a
fourth implicit Request field.

For `state.Events.<kind>.<field>`, `<kind>` identifies an EventKind. For
`state.Events.*.<field>`, the containing `LogicalConstraint` must provide the sibling
`EventConstraint` used to form the selector. `expandEventSelector(rawSelector, Env.Universe)`
replaces every requested kind with its finite included-kind closure before either form calls
`projectLatestEvidence`:

1. select eligible evidence according to `RL2_Model.md` §4.3;
2. keep the evidence with maximal `occurredAt`;
3. project `<field>` from every item tied at that time;
4. return `Missing` if no eligible item exists; `Invalid` if any tied item lacks `<field>` or has
   the wrong declared type; `Ok(v)` if all projected semantic values equal; and `Conflict` if tied
   projections differ.

There is no storage-sequence or identifier tie-break. A wildcard without a sibling event pattern
is invalid at projection time. `state.Events.<kind>` without a projected field is not a scalar
operand value and is likewise invalid.

The `global` root contains caller-supplied aggregate facts in `GlobalScope`. Computing a seat
count, active-Agreement set, or other aggregate happens during snapshot assembly. `Eval` applies
the same fact-resolution rules as for any other root.

#### matchesEvidence : Evidence × EventPattern × PolicyUniverse → Boolean

`matchesEvidence` checks an evidence item against an event pattern using the finite event-kind
index in the canonical PolicyUniverse:

```
matchesEvidence : Evidence × EventPattern × PolicyUniverse → Boolean

matchesEvidence(e, pattern, U) =
    typeMatches(e.kind, pattern.kind, U) ∧
    optionalMatch(e.actor, pattern.actor) ∧
    optionalMatch(e.action, pattern.action) ∧
    optionalMatch(e.object, pattern.object) ∧
    payloadMatches(e.payload, pattern.payload)

optionalMatch(actual, None) = true
optionalMatch(actual, Some(expected)) = actual = Some(expected)

typeMatches(actual, expected, U) =
    actual = expected ∨ expected ∈ U.eventKindAncestors[actual]
    -- S6: individual-level event-kind subsumption (eventKindIncludedIn*), NOT rdfs:subClassOf.
    -- Same bounded-traversal shape as action subsumption; no OWL class reasoning.

payloadMatches(actual, expected) =
    ∀(k, v) ∈ expected : k ∈ actual ∧ valueMatches(actual[k], v)

valueMatches(actual, expected) =
    case expected of
        Literal(v)   → actual = v
        Pattern(p)   → payloadMatches(actual, p)
        Any          → true
```

The selector layer additionally checks occurrence time and profile admissibility.
`matchesEvidence` is a pure structural pattern match and never consults storage order or
provenance by itself.

#### Declarative Duty and Promise status (S2-C2)

Status is a result over immutable inputs, not a stored-state transition:

```
DutyStatus    ::= Pending | Active | Fulfilled | Violated
PromiseStatus ::= Pending | Fulfilled | Violated

StatusResult<S> ::= Known(S)
                  | IndeterminateStatus(causes : finite non-empty Set<EvalError>)
```

`IndeterminateStatus` is not an ontology state. It preserves errors that prevent the evaluator
from selecting one of the existing state individuals. The optional RDF properties
`obligationState` and `promiseState` may serialize only a `Known` result and are never read as
authoritative evaluator input.

One Duty node denotes one occurrence. A present `dutyWindow` is the finite half-open interval
`[startInclusive, endExclusive)`; absence is unbounded. The following predicates fix every
boundary:

```
before(d, now) = d.window ≠ None ∧ now < d.window.startInclusive
inside(d, t)   = d.window = None ∨
                 d.window.startInclusive ≤ t < d.window.endExclusive
closed(d, now) = d.window ≠ None ∧ now ≥ d.window.endExclusive
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

For an Achievement Duty, action evidence is selected by kind `ActionPerformed`, the Duty subject,
an action equal to or narrower than the required action, the Duty object, and the Duty window.
The selector adds no ambient Case or storage-order condition. If `postCondition` is absent, each
selected event is a qualifying witness. If present, it is evaluated at that event's occurrence
time; later unrelated state cannot retroactively make an action successful:

```
achievementCandidates(d, U, W, C) =
    selectEvidence(actionSelector(d.subject, d.action, d.object, d.window, U), W, C)

qualifies(d, e, U, W, C) =
    case d.postCondition of
        None     → { truth: True, causes: ∅ }
        Some(pc) → evalAt(pc, e.occurredAt, U, d.subject, Some(d.object), W, C)
```

`actionSelector(a,x,s,w,U)` selects `ActionPerformed` evidence whose actor is `a`, whose object is
`s`, whose action is equal to or included in `x` under `U.actionAncestors`, and whose occurrence
time is inside `w` (or unrestricted when `w=None`). `selectEvidence` then applies the snapshot's
trust, validity, and admissibility rules from `RL2_Model.md` §4.3. `projectLatestActor` keeps the
qualifying witnesses with maximal `occurredAt`: it returns their common actor, `Conflict` if tied
actors differ, and never uses storage order as a tie-break.

`achievementStatus` is total:

```
achievementStatus(d, U, W, C) =
    if before(d, W.evaluationTime) then Known(Pending)
    else case achievementCandidates(d, U, W, C) of
        Err(e) → IndeterminateStatus({e})
        Ok(es) →
            let qs = [ qualifies(d,e,U,W,C) | e ∈ es ] in
            if ∃q ∈ qs : q.truth = True then Known(Fulfilled)
            else if ∃q ∈ qs : q.truth = Unknown then
                IndeterminateStatus(⋃ { q.causes | q ∈ qs, q.truth = Unknown })
            else if closed(d, W.evaluationTime) then Known(Violated)
            else Known(Active)
```

No matching action evidence is `Ok(∅)`, not `Missing`: it means the Achievement has not yet been
fulfilled. Relevant malformed, inadmissible, or conflicting evidence remains an error.

For a windowed Maintenance Duty, `elapsed(d,now)` is the set of instants inside its window no
later than `now`. `throughout` applies the existing three-valued condition semantics to every
such instant:

```
throughout(i, d, U, W, C) =
    let rs = { evalAt(i,t,U,d.subject,Some(d.object),W,C) |
               t ∈ elapsed(d,W.evaluationTime) } in
    if ∃r ∈ rs : r.truth = False then { truth: False, causes: ∅ }
    else if ∀r ∈ rs : r.truth = True then { truth: True, causes: ∅ }
    else { truth: Unknown,
           causes: ⋃ { r.causes | r ∈ rs, r.truth = Unknown } }
```

This is not an instruction to sample a continuous clock. Over a finite snapshot and bounded
condition tree, truth changes only at the finite boundaries contributed by fact-validity
intervals, evidence occurrence times, the Duty window, and literal time comparisons. A conforming
implementation partitions the elapsed window into truth-invariant finite cells at those
boundaries, retaining singleton boundary cells when equality or inclusivity can change truth, and
evaluates one representative per cell. An uncovered cell resolves the relevant fact as `Missing`
and therefore yields `Unknown`.

```
maintenanceStatus(d, U, W, C) =
    if before(d, W.evaluationTime) then Known(Pending)
    else if d.window = None then
        case evalAt(d.invariant,W.evaluationTime,U,d.subject,Some(d.object),W,C) of
            { truth: True, _ }       → Known(Active)
            { truth: False, _ }      → Known(Violated)
            { truth: Unknown, causes } → IndeterminateStatus(causes)
    else let r = throughout(d.invariant, d, U, W, C) in
            if r.truth = False then Known(Violated)
            else if r.truth = Unknown then IndeterminateStatus(r.causes)
            else if closed(d, W.evaluationTime) then Known(Fulfilled)
            else Known(Active)

dutyStatus(d, U, W, C) =
    case d of
        AchievementDuty(_) → achievementStatus(d,U,W,C)
        MaintenanceDuty(_) → maintenanceStatus(d,U,W,C)
```

A Maintenance Duty without a finite window is an ongoing snapshot requirement: it is Active when
the invariant is true now, Violated when false now, and cannot be Fulfilled. It makes no claim
about an interval with an unspecified start. For a windowed Maintenance Duty, complete coverage
is required; merely observing the invariant as true at `evaluationTime` is insufficient.

Promise status is derived without a Promise state machine:

```
promiseStatus(Promise(p,q,s?,content), U, W, C) =
    case content of
        PromisedAction(x) →
            case s? of
                None → IndeterminateStatus({
                    Missing({ site: StatusSite(PromiseTarget(p)),
                              target: Some(PromiseTarget(p)) }) })
                Some(s) → case selectEvidence(actionSelector(p,x,s,None,U), W, C) of
                    Err(e)    → IndeterminateStatus({e})
                    Ok(∅)     → Known(Pending)
                    Ok(_)     → Known(Fulfilled)

        PromisedState(c) →
            case ⟦c⟧(mkStatusEnv(U,p,s?,W,C)) of
                { truth: True,  _ }      → Known(Fulfilled)
                { truth: False, _ }      → Known(Violated)
                { truth: Unknown, causes } → IndeterminateStatus(causes)

        PromisedDuty(d) →
            case dutyStatus(d,U,W,C) of
                Known(Pending | Active) → Known(Pending)
                Known(Fulfilled)        → Known(Fulfilled)
                Known(Violated)         → Known(Violated)
                IndeterminateStatus(es) → IndeterminateStatus(es)
```

`mkStatusEnv` admits `agent.*`, `asset.*`, `state.*`, `context.*`, and `global.*`, binding agent and
asset to the Promise content rather than an access Request. A status condition that uses
`request.*` is invalid because status derivation has no access Request.
`PromisedAction` has no Duty window: it may be fulfilled by evidence but does not become Violated
solely through elapsed time. Acceptance can crystallize it into a bounded Duty.

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

`dutyPerformerOperand` is defined only for an Achievement Duty. It selects among action witnesses
whose optional postcondition is conclusively true, keeps those with maximal `occurredAt`, and
projects their actors using the same equal-value-collapse/unequal-tie-conflict rule as
`projectLatestEvidence`. No witness is `Missing`; a Maintenance Duty target is `Invalid` because
Maintenance has no performer.

```
resolveDutyPerformer(d,U,W,C) =
    case d of
        MaintenanceDuty(_) →
            Err(Invalid({ site: StatusSite(NormTarget(d)),
                          target: Some(NormTarget(d)) }),
                Some("A Maintenance Duty has no action performer"))
        AchievementDuty(_) →
            case achievementCandidates(d,U,W,C) of
                Err(e) → Err(e,None)
                Ok(es) →
                    let qs = { e ∈ es | qualifies(d,e,U,W,C).truth = True } in
                    if qs = ∅ then
                        Err(Missing({ site: StatusSite(NormTarget(d)),
                                      target: Some(NormTarget(d)) }),
                            Some("No qualifying Duty witness"))
                    else projectLatestActor(qs, NormTarget(d))
```

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

Given a PolicyUniverse `U`, Request `R = (a_req, x_req, s_req)`, WorldSnapshot `W`, and
EvaluationConfiguration `C`:

```
mkEnv(U, R, W, C) = (U, R, a_req, s_req, W, C)
                    -- (Universe, Request, Agent, Asset, Snapshot, Configuration)
```

The environment retains the full Request so `request.*` paths resolve. All other dynamic values
come from `W`; `U` supplies canonical action/event-kind/collection indexes; `C` supplies profiles,
declared bounds, trust parameters, and the combining strategy.

### Request Matching

A norm applies to a request only if the norm's subject, action, and object match the request:

```
matchesRequest(n, Env) =
    let R = Env.Request in
    subjectMatches(n.subject, R.requestingAgent, Env) ∧
    objectMatches(n.object, R.requestedAsset, Env.Universe) ∧
    actionMatches(n, R.requestedAction, Env.Universe)

subjectMatches(a, requested, Env) =
    a = requested ∨ a ∈ roles(requested, Env)

objectMatches(s, requested, U) =
    s = requested ∨ requested ∈ members(s,U)

actionMatches(AchievementDuty(_,_,x,_,_,_,_), requested, U) =
    x = requested ∨ includedInAction(requested,x,U)
actionMatches(Privilege(_,x,_,_,_), requested, U) =
    x = requested ∨ includedInAction(requested,x,U)
actionMatches(Prohibition(_,x,_,_), requested, U) =
    x = requested ∨ includedInAction(requested,x,U)
actionMatches(MaintenanceDuty(_), _, _) = true
```

Where:
- `roles(a_req, Env)` returns role memberships of the agent (D3 remains the tracked definition gap)
- `includedInAction(x_req, x, U)` tests the finite canonical action-inclusion index
- `members(s, U)` returns the **direct** `rl2:member` individuals of `s` in the canonical policy
  universe when `s` is an `AssetCollection` (empty otherwise)

A Maintenance Duty has no requested action to match. The `true` action component above makes an
independent Maintenance Duty a candidate on its subject and object only. An attached Duty is
reached through its owning Privilege and therefore uses the Privilege's request match; its own
subject and object still determine performance evidence, not access matching.

> **C7 — collections are assets, membership is direct.** `AssetCollection ⊑ Asset`, so a norm may target a collection directly (`s = s_req` matches when the request is *for* the collection) and a collection may itself appear as an `rl2:member` of another collection. Core `members(s, U)` is **not** transitively closed: if `s_req` is a member of a sub-collection nested inside `s`, that does **not** match in core. Flattening nested collections is a profile/derived concern layered on top of this direct-membership base. Membership is read from the fixed canonical PolicyUniverse, so a norm's asset extension is stable for the duration of an evaluation.

Action subsumption is defined by the transitive closure of `rl2:includedIn`:

```
x' ⊑ᵁ x  :=  includedInAction(x', x, U)
```

Canonical projection computes the finite transitive closure of `rl2:includedIn` in `U`. Usage of
`rdfs:subClassOf` for action refinement is non-normative in RL2.

Action subsumption applies uniformly across request matching and Achievement evidence selection.
There is no stored `Performed` Boolean or `DutyPerformer` field. `achievementCandidates` and
`resolveDutyPerformer` derive both from the immutable evidence set and report unequal latest-actor
ties as `Conflict`.

**RDF grounding**: Actions are individuals of `rl2:Action`. Action subsumption (`x' ⊑ x`) follows the transitive closure of `rl2:includedIn`; `members(s)` is the set of **direct** `rl2:member` links when `s` is an `rl2:AssetCollection` (not transitively closed — nested-collection flattening is a profile/derived concern, C7); and `roles(a_req)` derives from the agent's RDF typing/role assignments as defined in the Agent and role classes in the Vocabulary.

### Norm Denotations

Each activation is three-way on its canonical `ConditionResult`: `True` activates the norm,
`False` leaves it `Inactive`, and **`Unknown` yields `Indeterminate`**. Matching itself is total
(`matchesRequest` is a structural equality/subsumption check that cannot error). The helper
results referenced here are defined once in **Pre-Resolution Normative Envelope**; these equations
are projections of that definition, not a second evaluation algorithm.

Privilege activation:

```
⟦n : Privilege⟧(P, Env) =
    Permit         if matchesRequest(n, Env) ∧ accessResult(P,n,Env).truth = True
    Indeterminate  if matchesRequest(n, Env) ∧ accessResult(P,n,Env).truth = Unknown
    Inactive       otherwise
```

Prohibition activation:

```
⟦n : Prohibition⟧(P, Env) =
    Deny           if matchesRequest(n, Env) ∧ accessResult(P,n,Env).truth = True
    Indeterminate  if matchesRequest(n, Env) ∧ accessResult(P,n,Env).truth = Unknown
    Inactive       otherwise
```

Duty activation:

```
⟦d : independent Duty⟧(P, Env) =
    Obligation(d)  if matchesRequest(d, Env) ∧ ⟦effectiveCondition(P,d)⟧(Env).truth = True
    Indeterminate  if matchesRequest(d, Env) ∧ ⟦effectiveCondition(P,d)⟧(Env).truth = Unknown
    Inactive       otherwise

⟦d : attached Duty⟧(P, Env) =
    Obligation(d)  if attachedDutyResult(P,d,Env).truth = True
    Indeterminate  if attachedDutyResult(P,d,Env).truth = Unknown
    Inactive       otherwise
```

The applicability condition does not participate in `dutyStatus`. It determines whether the Duty
contributes an obligation atom; `action`/`postCondition` or `invariant`, together with
`dutyWindow`, determine the status of that obligation occurrence.

Promise status:

```
⟦Promise(p,q,s?,content)⟧(Env) =
    promiseStatus(Promise(p,q,s?,content), Env.Universe,
                  Env.Snapshot, Env.Configuration)
```

This is the total S2-C2 status function; it does not read a stored Promise state.

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
∀ Prohibition(s, x, o, c) :
    ∃ Claim(h, s, AchievementDuty(s, Some(h), refrainFrom(x), o, c, None, None)) where
    h = counterparty(Prohibition) if present, else grantor(policyOf(Prohibition))
```

The correlative Claim is **derived**, not authored: policy authors write only the
`Prohibition`. Violation of a prohibition uses the subsumption-aware `performed()`
helper (so performing a narrower action `x′ ⊑ x` violates a prohibition on `x`).

### Claim Denotation and Content Derivation (C6b)

A Claim is the Hohfeldian correlative of **exactly one** Duty, carried directly as its third
constructor field `correlativeTo` (enforced by `ClaimShape`: exactly one, and it must be a
`rl2:Duty`). A Claim does **not** author its own content; its required content, object,
applicability condition, and window are
**derived** from that Duty:

```
ClaimContent(k: Claim) =
    let D = k.correlativeTo                          -- exactly one, and D : Duty (ClaimShape)
    in (content, object, condition, window) :=
           (requiredContent(D), D.object, D.condition, D.dutyWindow)
           -- requiredContent is action + optional postCondition, or invariant
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
different actions, invariants, or objects are always distinguishable (via their distinct Duties), the
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

The denotation establishes whether the Power exists and is active. Exercising it would produce a
new `PolicyUniverse`; that transformation, its authorization request, and persistence are not
silently performed by access-request `Eval`. A future language work item may standardize a pure
Power-exercise transformation without introducing mutable evaluator state.

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

Liability identifies who is exposed if `P` is exercised; access-request `Eval` does not exercise
the Power.

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

**PolicyUniverse determination:** `U` is supplied as an immutable input. Discovery, version
selection, publication, and any deployment notion of an active generation occur before `Eval`.

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

Applicability is fixed during one evaluation. A later call may supply a different snapshot and
therefore obtain a different result—for example, after new approval evidence exists or an
evaluation-time bound has passed. RL2 specifies the result for each input value; it does not
specify when a deployment constructs another snapshot or schedules reevaluation.

---

## Duty and Promise status

The former activation/fulfillment/violation transition rules are removed from the active
semantics. `dutyStatus` and `promiseStatus` in §Declarative Duty and Promise status are the sole
definitions. They read immutable evidence and fact intervals, return `StatusResult`, and neither
consume an event nor update a stored state. Scheduling a later evaluation with a different
snapshot is outside core `Eval`.

### Pure Offer Acceptance (Offer → Agreement)

An **Offer** may contain voluntary Promises together with Norms that are restated as terms of the
proposed Agreement. A Promise binds its promisor as a voluntary commitment but has no correlative
Claim before acceptance. Acceptance is a pure, one-time policy transformation; it is not an
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
    claimIds       : total map PromiseRef → IRI,
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
    | UnsupportedPromiseContent(promiseRef, PromisedDuty)
    | UnsupportedPromiseReference(site, promiseRef, operand)
    | DanglingInternalReference(site, targetId)

InvalidOfferReason ::=
      WrongPolicyKind | EmptyClauseSet | ConflictingObjectBinding
    | InvalidAcceptanceDomain | NonLocalPromiseTarget
    | InvalidOutputShape | StatusDependencyCycle
```

`primaryIds` assigns the output Norm identifier for every materialized source: the crystallized
Duty for a Promise and the copied Norm for a policy-local Norm. For S2-C4, locality is structural
and deliberately narrow:

```text
localNorms(O) =
    { n : Norm | n ∈ O.clauses }
    ∪ { d : Duty | ∃ n : Privilege ∈ O.clauses : d ∈ n.prerequisiteDuties }
```

The second set contains the non-clause Duties owned through `prerequisiteDuty`; their attachment
placement is preserved rather than promoted to Agreement clauses. `correlativeTo`, `affectsNorm`,
`exposedTo`, `immuneFrom`, and `targetNorm` are references, not ownership relations. Their targets
are rewritten only when independently present in `localNorms(O)` or among the Promise clauses of
`O`; otherwise they remain external and are not copied. S2-C5 must preserve this distinction in
the canonical RDF projection.

`claimIds` assigns the additional Claim identifier for every Promise. Define `sourceIris(O)` as
every IRI occurring as an RDF term in the canonical projection of `O`; blank nodes contribute no
IRI. `agreementId`, all `primaryIds` values, and all `claimIds` values MUST be pairwise distinct,
and the resulting set of allocated IRIs MUST be disjoint from `sourceIris(O)`. Identifier allocation is therefore
explicit input, not a nondeterministic `fresh IRI` operation. How a caller allocates globally
unique IRIs is outside the transformation; canonical RDF projection of these supplied identifiers
belongs to S2-C5. `ref(x)` denotes the `SourceRef` assigned to source Promise or local Norm `x` by
that normalized projection; S2-C4 depends only on its stable identity and equality, not on its
concrete encoding.

`objectBindings` may supply an object for either an action or state Promise when the Offer leaves
the catalogue target open. A conflicting authored and supplied object is `InvalidOffer`; an
identical binding is accepted but has no effect. `dutyWindows` supplies an optional finite
performance interval for the Duty created from a Promise. It does not alter a copied Norm clause.

An Offer-level `condition` denotes the applicability guard proposed for the resulting Agreement;
it does not determine whether or when an Acceptance may be issued. Offer validity, withdrawal,
and acceptance authorization are outside this pure transformation. Materialization therefore
rewrites and copies `O.condition` as the Agreement-level applicability guard.

#### Validation

`materialize(O,A)` collects all applicable errors and returns `Rejected(errors)` without a partial
Agreement when any error exists. A value is **structurally conforming** when it inhabits the typed
abstract syntax in this document and its RDF projection satisfies the applicable core SHACL
shapes. The input is valid only when:

1. `O` is a structurally conforming `Offer` with a non-empty finite clause set;
2. any `grantor` or `grantee` authored on `O` equals the corresponding value in `A`;
3. each Promise's `(promisor,promisee)` is either `(A.grantor,A.grantee)` or
   `(A.grantee,A.grantor)`—orientation may differ, but acceptance cannot bind an absent third
   party;
4. `primaryIds` has domain `PromiseClauses(O) ∪ localNorms(O)`, `claimIds` has domain
   `PromiseClauses(O)`, the optional maps have no other keys, and the identity maps satisfy the
   freshness and injectivity rule;
5. every promised action or state has exactly one object after applying `objectBindings`;
6. every `dutyWindows[p]` satisfies
   `dutyWindows[p].startInclusive < dutyWindows[p].endExclusive`;
7. every Promise-valued `targetNorm` occurring in the Offer's policy condition, clause conditions,
   Promise content, or attached prerequisite Duties targets a Promise clause of that same Offer;
8. every reference to a clause of `O` has a corresponding `primaryIds` entry; and
9. rewriting produces an acyclic, structurally conforming Agreement.

A failure of item 6 yields `InvalidDutyWindow(ref(p))`; a failure of item 7 yields
`InvalidOffer(site, NonLocalPromiseTarget)`. `StatusDependencyCycle` reports a cycle already
present in the Offer's status-dependency graph: injective renaming and the typed Promise-to-Duty
operand rewrite cannot create one.

Materialization-error identity is the constructor plus its typed fields; explanatory prose is not
part of identity. Errors are enumerated by constructor, site, and referenced identifier, so
validation order cannot change the result. A primary error on a Promise (unsupported content,
missing object, invalid Duty window, or party mismatch) suppresses derivative output-shape and
rewrite errors caused solely by the absence of that Promise's generated Duty; independent errors
are still collected.

#### Crystallization

For a Promise `p = Promise(promisor, promisee, object?, content)`, let `s` be its authored object
or accepted object binding, and let `w` be its accepted Duty window if one exists:

```text
crystallize(p,A) =
    case p.content of
        PromisedAction(x) →
            AchievementDuty(subject = p.promisor,
                            counterparty = Some(p.promisee),
                            action = x,
                            object = s,
                            condition = True,
                            postCondition = None,
                            dutyWindow = w)

        PromisedState(i) →
            MaintenanceDuty(subject = p.promisor,
                            counterparty = Some(p.promisee),
                            object = s,
                            condition = True,
                            invariant = i,
                            dutyWindow = w)

        PromisedDuty(_) →
            UnsupportedPromiseContent(ref(p), PromisedDuty)
```

The Duty identifier is `A.primaryIds[ref(p)]`. Its correlative Claim has identifier
`A.claimIds[ref(p)]`, `subject = p.promisee`, `counterparty = p.promisor`, and
`correlativeTo = A.primaryIds[ref(p)]`. Claim content is derived from that Duty as specified in
§Claim Denotation and Content Derivation; it is not copied onto the Claim.

`PromisedDuty` remains meaningful for snapshot-derived Promise status, but general suretyship
cannot be crystallized into either current Duty form without inventing an action or misusing a
Maintenance invariant. Core therefore rejects that content at acceptance. A profile may define a
separate, explicitly typed suretyship transformation; core never guesses one.

A `PromisedAction` without an accepted window creates an unbounded Achievement Duty, which can
remain Pending. A `PromisedState` without a window creates an ongoing Maintenance Duty, which can
be Active or Violated but cannot become Fulfilled. A finite accepted window gives the resulting
Duty the status boundaries defined in §Declarative Duty and Promise status.

#### Clause copying and reference rewriting

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
        if a.leftOperand = promiseStateOperand then
            a[targetNorm  ↦ NormTarget(sourceMap(p)),
              leftOperand ↦ obligationStateOperand]
        else UnsupportedPromiseReference(site(a),ref(p),a.leftOperand)
    else a[targetNorm ↦ rewriteRef(a.targetNorm)]
```

`rewriteRef` applies to `prerequisiteDuty`, `correlativeTo`, `affectsNorm`, `exposedTo`,
`immuneFrom`, and Norm-valued `targetNorm`. A Promise-valued `targetNorm` has only the core rewrite
shown above. In particular, `promisorOperand` and profile-defined Promise operands are rejected:
the Agreement contains no Promise for them to query, and silently assigning them Duty semantics
would be unsound. Conditions without `targetNorm` are copied structurally.

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
                              ∪ crystallizedDuties(O,A)
                              ∪ correlativeClaims(O,A),
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

### Remedial Generation Boundary

**Conceptual Foundation (Sein-Sollen vs Tun-Sollen)**:

- **Promise = Sein-Sollen (Ought-to-Be)**: A required state of the world (invariant)
- **Duty = Tun-Sollen (Ought-to-Do)**: An action to achieve or restore that state

Core `Eval` does not generate a remedial Duty or a protocol Requirement when
`promiseStatus(p,U,W,C)=Known(Violated)`. Whether remediation should be an authored relation or a
future protocol transformation remains SEM-1; no state-changing generation rule is normative here.

The former `rl2p:Requirement` runtime representation has moved to
`../future/protocol/RL2_Protocol.md`. Core work must decide whether remediation is an authored
policy relation or a pure derived normative relation; an evaluator does not create or persist a
Requirement as part of `Eval`.

### Event Processing

> **Non-core legacy section.** Event arrival, append order, idempotency, scalar mutation, late
> delivery, and committed-decision replay belong to future protocol or implementation work. The
> core replacement is a finite evidence set supplied in `WorldSnapshot`; evidence identity and
> deterministic selection remain open under S2-C1.

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

Privileges become active when the request matches and `accessResult` is true. `accessResult`,
defined normatively in the derivation section below, includes the policy/clause condition and
every attached prerequisite:

```
Env = mkEnv(U, R, W, C)
matchesRequest(n : Privilege, Env) = true
accessResult(P,n,Env).truth = True
──────────────────────────────────────────────────────────────────
PrivilegeActive(n,P)
```

Privileges are inactive when the request does not match or the combined result is false:

```
Env = mkEnv(U, R, W, C)
matchesRequest(n : Privilege, Env) = false ∨ accessResult(P,n,Env).truth = False
──────────────────────────────────────────────────────────────────
PrivilegeInactive(n,P)
```

### Prohibition Activation

Prohibitions are active when their condition holds and the request matches:

```
Env = mkEnv(U, R, W, C)
matchesRequest(n : Prohibition, Env) = true
accessResult(P,n,Env).truth = True
──────────────────────────────────────────────────────────────────
ProhibitionActive(n,P)
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
        Some(c) → ⟦c⟧(Env)

prerequisiteResult(d, Env) =
    foldK(kOr, [notResult(dutyConditionResult(d,Env)), fulfilledResult(d,Env)])
    -- not applicable OR fulfilled

notResult(r) = { truth: ¬ᴷ r.truth, causes: r.causes }

allResults(rs) =
    if rs = [] then { truth: True, causes: ∅ } else foldK(kAnd, rs)

anyResults(rs) =
    if rs = [] then { truth: False, causes: ∅ } else foldK(kOr, rs)

canonicalDutyOrder(ds) = sort ds by dutyId
canonicalPrivilegeOrder(ns) = sort ns by privilegeId

accessResult(P, n : Privilege, Env) =
    allResults([⟦effectiveCondition(P,n)⟧(Env)] ++
               [ prerequisiteResult(d,Env) |
                 d ∈ canonicalDutyOrder(n.prerequisiteDuties) ])

accessResult(P, n : Prohibition, Env) = ⟦effectiveCondition(P,n)⟧(Env)

ownerScopeResult(P, n, d, Env) =
    if ¬matchesRequest(n,Env) then { truth: False, causes: ∅ }
    else foldK(kAnd, [⟦effectiveCondition(P,n)⟧(Env), dutyConditionResult(d,Env)])

attachedDutyResult(P, d, Env) =
    anyResults([ ownerScopeResult(P,n,d,Env) |
                 n ∈ canonicalPrivilegeOrder({ n : Privilege ∈ P.clauses |
                                               d ∈ n.prerequisiteDuties }) ])
```

`allResults` gives an empty prerequisite set the identity value `True`; it does not construct an
authored zero-arity `And`. `prerequisiteResult` masks irrelevant errors in the usual Kleene way:
an inapplicable Duty is satisfied as a prerequisite regardless of its separately reported status,
and a conclusively Fulfilled Duty is sufficient even when its applicability guard is Unknown.
Pending, Active, and Violated all mean that an applicable prerequisite has not been met. They
make that Privilege inactive; they do not create a global Deny.

```
Out : (PolicyUniverse U, Env) → ℘(NormativeAtoms)

Out(U, Env) =
    ⋃ { deriveNorms(P, Env) | P ∈ U }

deriveNorms(P, Env) =
    if P : Offer then ∅
    else
        { permit(n, P)   | n : Privilege ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = True } ∪
        { forbid(n, P)   | n : Prohibition ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = True } ∪
        { obligate(d, P) | d ∈ independentDuties(P), matchesRequest(d, Env), ⟦effectiveCondition(P,d)⟧(Env).truth = True } ∪
        { obligate(d, P) | d ∈ attachedDuties(P), attachedDutyResult(P,d,Env).truth = True } ∪
        { indeterminate(n, P, accessResult(P,n,Env).causes)
                         | n : Privilege ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = Unknown } ∪
        { indeterminate(n, P, accessResult(P,n,Env).causes)
                         | n : Prohibition ∈ P.clauses, matchesRequest(n, Env), accessResult(P,n,Env).truth = Unknown } ∪
        { indeterminate(d, P, ⟦effectiveCondition(P,d)⟧(Env).causes)
                         | d ∈ independentDuties(P), matchesRequest(d, Env), ⟦effectiveCondition(P,d)⟧(Env).truth = Unknown } ∪
        { indeterminate(d, P, attachedDutyResult(P,d,Env).causes)
                         | d ∈ attachedDuties(P), attachedDutyResult(P,d,Env).truth = Unknown }
```

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

The type filters are normative. Claims, Powers, Liabilities, Immunities, and Promises have their
own denotations/lifecycles; they are not request-matched access candidates and therefore do not
produce access-decision `indeterminate` atoms.

**S7 (provenance).** A `NormativeAtom` wraps the full norm object (`n`/`d`, not a projected
`(a,x,s)` triple) together with its source policy `P` — every atom in the envelope carries the
norm and policy that produced it, for audit and for `mostSpecific` (below), which needs the
norm's action, priority, complete access guard, and source policy. Atom equality is structural: `(atom-kind,n,P)` for
definite atoms and `(indeterminate,n,P,causes)` for Unknown atoms. `causes` is itself a canonical
set, so its enumeration order cannot create a second atom. Two policies granting the same
`(a,x,s)` shape remain distinct atoms with independent provenance (WP-3/C6a's clause-identity
guarantee already makes `n` unique per policy, so this never accidentally merges two different
clauses). For an attached Duty, `P` contains at least one Privilege that references it; the Duty
itself is not in `P.clauses`. `resolveDecision(envelope, strategy)` is the sole public entry point for
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
        let envelope = Out(U, Env)                         -- ① Derivation
        let decision = resolveDecision(envelope, C.strategy) -- ② Resolution
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

The **normative envelope** `Out(U, Env)` is the first-class intermediate result — visible before resolution, available for audit, and monotone in the policy universe (for a fixed environment).

Resolution may eliminate norms via priority or strategy, breaking monotonicity. This is by design: `permit(a,x,s) ∧ forbid(a,x,s)` is not a logical contradiction but a **conflict to be resolved procedurally**.
`resolveDecision` is a parameterized algorithm (strategy + priorities); if these inputs cannot break ties, the evaluator must surface an explicit ambiguity/error rather than applying an implicit specificity heuristic.

For architectural context, see `../docs/RL2_Architecture.md` §4.

---

## Big-Step Semantics (Policy Evaluation)

This section is **not** a second, independent definition of policy evaluation. `Out` (above)
is the sole derivation rule; what follows unfolds `Eval` one level to name the intermediate
quantities an informal "validate → interpret statuses → derive → resolve" description would use.
Prerequisite status is interpreted before derivation and may be memoized;
each quantity below is read from `Out`'s envelope or the derived status maps, never recomputed independently of
`deriveNorms`.

### Evaluation Function Signature

The total decision function takes a policy universe and Request as first-class parameters:

```
Eval : (PolicyUniverse U, Request R, WorldSnapshot W, EvaluationConfiguration C)
       → EvaluationResult
```

Where:
* `U` is the universe of policies (the current generation)
* `R = (a_req, x_req, s_req)` is the request (agent, action, asset)
* `W` is the finite immutable snapshot defined in `RL2_Model.md` §4
* `C` is the evaluation configuration, including profiles, bounds, trust parameters, and the
  evaluator-supplied conflict-resolution strategy (S7: evaluator
  configuration, not policy vocabulary — no policy or clause carries its own strategy)
* `Decision ∈ {Permit, Deny, NotApplicable, Indeterminate}`
* `EvaluationResult` contains the Decision, complete normative envelope, Duty- and Promise-status
  maps, and diagnostics

### Evaluation Algorithm (Unfolded)

```
Eval(U, R, W, C) =
    let errors = validateConfiguration(U, C) ∪ validateSnapshot(W, C)
    in if errors ≠ ∅ then
        EvaluationResult(Indeterminate, ∅, ∅, ∅, errors)
    else
    -- Step 1: Derive all Duty and Promise statuses from policy content and the immutable
    -- snapshot. Privilege prerequisite evaluation reads the same pure Duty results.
    let statuses = deriveDutyStatuses(U, W, C)
    let promiseStatuses = derivePromiseStatuses(U, W, C)

    -- Step 2: Derive the envelope. Privilege accessResult folds its prerequisite results;
    -- independent and attached Duties remain attributed atoms for normative reporting.
    let Env = mkEnv(U, R, W, C)
    let envelope = Out(U, Env)

    -- Step 3: Resolve access atoms only. Duty status has already affected each owning
    -- Privilege through accessResult; no Duty has global decision effect.
    let decision = resolveDecision(envelope, C.strategy)

    in EvaluationResult(decision,
                        envelope,
                        statuses,
                        promiseStatuses,
                        diagnosticsOf(envelope, statuses, promiseStatuses))
```

**Indeterminate handling (S2).** `resolveDecision(envelope, strategy)` retains each complete
access-norm `indeterminate(norm,policy,causes)` atom. It computes the finite set of resolver
summaries reachable when each Unknown access candidate is independently inactive or active, then
maps those summaries through the same priority/strategy decision function. Duty
`indeterminate` atoms remain in the envelope and diagnostics but do not enter access resolution.
A single reachable decision is conclusive; more than one yields `Indeterminate`. The summary
space is polynomial and does not enumerate the `2^|I|` truth assignments. Mapping
`Indeterminate → Deny` is an **enforcement-adapter** decision (a fail-closed PEP), **not** the
semantic verdict: `Eval` returns `Indeterminate` so the ambiguity is auditable.

### Conflict Resolution

When multiple norms apply, conflicts must be resolved. RL2 provides two complementary mechanisms:

1. **Access-norm priority** (`rl2:priority`): Privileges and Prohibitions may declare an integer
   priority; higher access candidates override lower access candidates before strategy is applied.
   Duty priority is irrelevant to access resolution. A prerequisite is either satisfied or it
   prevents its owning Privilege from becoming a candidate.

2. **Evaluator-level strategy**: The evaluator is configured with a conflict resolution strategy (e.g., prohibit-overrides, permit-overrides). This is **evaluator configuration**, not policy vocabulary—analogous to XACML combining algorithms.

The `strategy` parameter in `resolveDecision` below represents evaluator configuration. Policies express norms and priorities; evaluators decide how to combine conflicting results when priorities are equal. Four strategies are defined: `ProhibitOverrides`, `PermitOverrides`, `SpecificOverridesGeneral`, and `Invalid`.

More sophisticated defeasibility mechanisms—such as exclusionary rules—are available in frameworks like LegalRuleML [LegalRuleML] and may be incorporated in future RL2 profiles.

#### Specificity key (SEM-9)

`SpecificOverridesGeneral` needs a total ordering over competing norms *after* the global
priority step. Specificity is therefore a lexicographic pair computed statically per attributed
access norm — action subsumption depth, then complete access-guard atom count. Declared priority is not repeated inside
this metric because all candidates reaching `mostSpecific` are already in one maximal-priority
stratum:

```
actionDepth(x) = |{ y : Action | x ⊑ y, y ≠ x }|   -- count of x's proper ancestors under ⊑
    -- Static: one bounded traversal of the fixed `rl2:includedIn` closure per action.

atomCount(oc: Condition?) = case oc of
    None    → 0
    Some(c) → atoms(c)

atoms(c) = case c of
    AtomicConstraint(_)         → 1
    EventConstraint(_)          → 1
    And(cs) | Or(cs) | Xone(cs) → Σ_{c' ∈ cs} atoms(c')
    Not(c')                     → atoms(c')

guardAtomCount(P, n : Prohibition) =
    atomCount(P.condition) + atomCount(n.condition)

guardAtomCount(P, n : Privilege) =
    atomCount(P.condition) + atomCount(n.condition) +
    Σ_{d ∈ n.prerequisiteDuties} (1 + atomCount(d.condition))
    -- 1 counts the required Fulfilled test; d.condition controls whether it is required

Specificity = ActionDepth × GuardAtomCount
specificity(n,P) = (actionDepth(n.action), guardAtomCount(P,n))  -- lexicographic
```

A single lexicographic metric applies uniformly across `Privilege` and `Prohibition` — the
design choice SEM-9 flagged as needed, not a theorem. This eliminates *incomparability* by
construction: every norm has a well-defined `specificity` pair under a fixed total order on
tuples. The resolver summary retains the maximal pair separately for Privileges and
Prohibitions; equality of those two maxima is an opposite-effect tie.

`resolveDecision(envelope, strategy)` is the **only public signature** for conflict
resolution: policy universe, Request, and WorldSnapshot never surface as separate resolution arguments.
It retains attributed Unknown Privilege and Prohibition atoms and projects definite/possible
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
    { topPriority       : Integer?,
      bestPrivilegeSpec : Specificity?,
      bestProhibitSpec  : Specificity? }

emptySummary = { None, None, None }
summarizeChoices(atoms) =
    fold(extendSummaries, {emptySummary}, canonicalOrder(atoms))

extendSummaries(summaries, atom) =
    { addAtom(s, atom) | s ∈ summaries }

canonicalOrder(atoms) = sort atoms by (sourcePolicyId, sourceClauseId, atomKind)
optionMax(None, x)    = Some(x)
optionMax(Some(y), x) = Some(max(y, x))

addAtom(s, permit(n, P)) =
    addAccess(s, Privilege, priority(n), specificity(n,P))
addAtom(s, forbid(n, P)) =
    addAccess(s, Prohibition, priority(n), specificity(n,P))

addAccess(s, kind, p, spec) =
    if s.topPriority = None ∨ p > s.topPriority then
        { topPriority: p,
          bestPrivilegeSpec: if kind = Privilege then Some(spec) else None,
          bestProhibitSpec:  if kind = Prohibition then Some(spec) else None }
    else if p < s.topPriority then s
    else if kind = Privilege then
        s[bestPrivilegeSpec ↦ optionMax(s.bestPrivilegeSpec, spec)]
    else
        s[bestProhibitSpec ↦ optionMax(s.bestProhibitSpec, spec)]

choiceFold([], summaries) = summaries
choiceFold(i :: rest, summaries) =
    let active = { addAtom(s, activate(i)) | s ∈ summaries }
    let next = summaries ∪ active
    in choiceFold(rest, next)
    -- retaining s chooses condition Unknown=False; active chooses Unknown=True

hasPrivilege(s)  = s.bestPrivilegeSpec ≠ None
hasProhibition(s) = s.bestProhibitSpec ≠ None

baseDecision(s) =
    if ¬hasPrivilege(s) then NotApplicable else Permit

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
```

The cases are exhaustive over the validated `Strategy` datatype. An unknown strategy is an
`Invalid(ConfigurationSite(strategy))` input error and never reaches `decisionOf`.

`addAtom` uses only `max` and finite set construction, so definite summarization is
order-independent. `choiceFold` is exact for all joint Unknown access activations but deduplicates
after every step by summary equality. For `n` access atoms there are at most `O(n³)` summaries:
`O(n)` possible top priorities, `O(n)` best Privilege specificities, and `O(n)` best Prohibition
specificities. A direct implementation that scans each candidate top-priority stratum and the two
reachable best-specificity sets computes the same summaries in `O(n³)` time and polynomial space;
it need not materialize the powerset. This bounded summary construction, not a solver or entailment
engine, is the conformance model.

Normative boundary consequences include:

- Under `PermitOverrides`, a definite Privilege plus an equal-priority Unknown Prohibition is
  `Permit`: either activation choice permits.
- Under `PermitOverrides`, a definite Prohibition plus an equal-priority Unknown Privilege is
  `Indeterminate`: the choices yield Deny and Permit.
- Under `Invalid`, a lower-priority definite Prohibition and two Unknown equal-higher-priority
  access atoms (one Privilege, one Prohibition) are `Indeterminate`.
  Activating either Unknown alone still yields Deny, but activating both creates a top-stratum
  conflict; retaining joint reachable summaries is therefore necessary.

`Indeterminate` here is the same value produced per-norm in the denotations above and carried
by `rl2p:Indeterminate` at the protocol layer; a fail-closed PEP maps it to `Deny`, but that
mapping lives in the enforcement adapter, not in `resolveDecision`.

Note: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

### Duty Status Derivation

`deriveDutyStatuses` computes an immutable result map; it does not apply transitions or return a
new snapshot. The former transition rules above are retained as design input only. S2-C2 replaces
them with total Achievement and Maintenance status functions, including status indeterminacy and
the evidence interval for each attached Duty.

### Duty Attachment Boundary

Core has two Duty relationships only:

- a Duty linked from one or more Privileges with `rl2:prerequisiteDuty` is blocking for each owner when applicable; and
- a Duty linked directly from a Policy with `rl2:clause` is independent.

Concurrent and post-use obligations are not additional core attachment modes. Their substantive
requirements can still be stated as Achievement or Maintenance Duties with applicability,
postconditions, invariants, and optional windows. Turning a permitted use plus such Duties into
scheduled Requirements, enforcement actions, or a `PermitWithObligations` protocol response is
future companion behavior. Core `Eval` returns `Permit` plus the complete Duty-status map; it does
not claim that an ongoing obligation was imposed by the act of evaluation.

### Note on Evaluation Complexity

One `Eval` call is a bounded computation over finite policy, fact, and evidence sets. It neither
waits for evidence nor processes an event stream. Multi-step workflows may call `Eval` again with
a later snapshot, but scheduling, persistence, and trace semantics are future companion work.

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

## Evidence Semantics

Evidence influences a result only through `existsEvidence`, projected evidence paths, and the
Duty/Promise status functions. `Eval` does not append, reorder, or transform evidence. Event-kind
inclusion uses the finite `rl2:eventKindIncludedIn` closure; matching and temporal selection are
defined in `RL2_Model.md` §4.3 and `matches` above.

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

**Note on Inheritance**: ODRL's `inheritFrom` mechanism is intentionally not supported in RL2. Policy inheritance introduces complexity (flattening, override semantics, auditability issues) without clear benefit over explicit composition. Its migration disposition remains tracked in `../project/issues.md` (S2-M1).

---

## State Scope, Identity, and Concurrency (S5)

> **Non-core legacy section.** Offer/Agreement identity needed by a pure policy transformation may
> be extracted. Shared counters, active-Agreement aggregation, snapshot versions, CAS, retries,
> commit validation, and deployment consistency move to future reference implementation/protocol.

Runtime state must be scoped correctly, or two evaluators can both observe the same count and both
permit a request that should have been refused. RL2 pins state to **two identity tiers and no
more**, mirroring the object-oriented distinction between *class variables* and *instance
variables*.

### The two tiers (class vs instance)

| OOP | RL2 | Holds |
|-----|-----|-------|
| **class** (template) | **Offer** — immutable, authored once, accepted many times | no operative atoms before acceptance |
| **instance** (object) | **Agreement** — one immutable result per acceptance | Agreement-local clause identity |
| `new` / constructor | **`materialize(Offer, Acceptance)`** (§Pure Offer Acceptance) | uses the identifiers supplied by Acceptance |

- **Immutable policy identity vs materialized identity.** An **Offer** and the resulting
  **Agreement** are both immutable policy values. They are linked by
  `Agreement prov:wasDerivedFrom Offer`; neither stores runtime state.
- **Agreement-local identity.** Acceptance supplies a distinct identifier for every resulting
  clause. This prevents two acceptances from denoting the same Duty or Claim without prescribing
  a persistence layout or mutable state map.
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

> **Non-core legacy section.** Protocol projection is retained under `../future/protocol/` and is
> not part of language conformance.

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
| `MaxCollectionSize` | implementation-declared | policy-declared sets and collections |
| `MaxSnapshotFacts` | implementation-declared | `|WorldSnapshot.facts|` |
| `MaxSnapshotEvidence` | implementation-declared | `|WorldSnapshot.evidence|` |
| `MaxEvidencePayloadFields` | implementation-declared | fields in one Evidence payload |
| `MaxPolicyUniverse` | implementation-declared | `|U|` |

### Structural Constraints

1. **Finite policy universe**: U is a finite set of policies (`≤ MaxPolicyUniverse`)
2. **Bounded condition nesting**: Conditions have bounded depth (`≤ MaxConditionDepth`, default 20)
3. **Acyclic conditions**: No self-referential condition definitions
4. **Finite snapshot**: facts, evidence, and evidence payloads satisfy their declared bounds
5. **No recursive policy references**: Policies cannot invoke evaluation of other policies

### Path Resolution Constraints

6. **Bounded path depth**: `≤ MaxPathDepth` (default 10), enforced by grammar
7. **No live traversal**: ordinary paths are exact fact-key lookups, not graph pattern matching
8. **No evaluator callback**: `resolutionFunction` and connector execution occur only during
   snapshot assembly
9. **Deterministic selection**: evidence projection uses occurrence time and reports unequal ties
   as `Conflict`

### Complexity Analysis

Given these constraints:

| Operation | Complexity |
|-----------|------------|
| Canonical fact resolution | O(F) without an optional key index |
| Evidence selection/projection | O(E × (h + q)), where h is bounded kind-closure work and q is bounded payload matching |
| Condition evaluation | O(n × (F + E × (h + q))) without optional indexes |
| Norm matching | O(\|U\| × m) where m = max clauses per policy |
| Conflict resolution | O(k³) for the exact finite-summary construction described above |
| **Total `Eval` before S2-C2 status cost** | **O(\|U\| × m × n × (F + E × (h + q)) + k³)** |

`F`, `E`, `h`, and `q` are bounded by the snapshot, hierarchy, and payload conformance
parameters. Indexes may reduce lookup cost without changing meaning. S2-C2 must add a polynomial
bound for declarative Duty/Promise status derivation before the final total-`Eval` bound is closed.

### Totality Guarantees

Under these constraints, `Eval` is **total**: it terminates for all well-formed inputs. The function never:

- Loops infinitely (no recursive evaluation)
- Blocks on external resources (`Eval` performs no I/O; missing snapshot values produce `EvalError`)
- Diverges due to condition structure (bounded, acyclic)

`resolutionFunction`, source fetching, credential verification, and connector execution are
outside `Eval`. A deployment completes them while constructing `WorldSnapshot`; their cost and
termination are not included in the evaluator bound.

---

## Proof scope and normative artifact

RL2's current scope is **language specification, ODRL migration, and conformance**, not a
mechanized proof or implementation (`RL2_Scope.md`, SCOPE-2). The normative artifact consists of
the core ontology and shapes, `RL2_Model.md`, this document, the completed portions of
`RL2_ODRL_Mapping.md`, and accepted conformance vectors. No IR or protocol document is normative.

Datatype and function definitions in this document use Dafny-like algebraic-datatype notation
purely as precise pseudocode. This is not a commitment to Dafny or any implementation language.

---

## Proof Obligations

The following are requirements on the completed SCOPE-2 semantics:

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

See `../docs/RL2_References.md` for complete citations and glossary.

Related RL2 specifications:
- `rl2.ttl` — Core ontology (OWL)
- `rl2-shacl.ttl` — SHACL validation shapes
- `RL2_Model.md` — Request, WorldSnapshot, configuration, and result
- `RL2_ODRL_Mapping.md` — ODRL 2.2 translation and compatibility
- `../conformance/` — Structural and semantic conformance artifacts
