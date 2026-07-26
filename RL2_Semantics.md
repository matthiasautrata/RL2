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
* **⊥** = bottom/undefined; represents absence of value or evaluation failure

We define RL2 expressions as:

#### Norms

```
Norm ::= 
    Privilege(Agent, Action, Asset, Condition)
  | Duty(Agent, Action, Asset, Condition)
  | Prohibition(Agent, Action, Asset, Condition)
  | Claim(Agent subject, Agent counterparty, Right)   -- subject = right-holder, counterparty = duty-bearer
  | Power(Agent, Norm)
  | Liability(Agent, Norm)
  | Immunity(Agent, Norm)
```

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
      AtomicConstraint(leftOperand, operator, rightOperand)
    | And(Condition+)
    | Or(Condition+)
    | Xone(Condition+)
    | Not(Condition)
    | EventConstraint(expectsEvent: Event)
```

Notes:
- `And`, `Or`, and `Xone` take one or more conditions
- `EventConstraint` models approval requirements; holds when the expected event is present in Σ.Events
- `leftOperand` is drawn from profile-defined operands (RL2 Core defines `rl2:LeftOperand` class plus `currentDateTime`, `obligationStateOperand`, `dutyPerformerOperand`, `promiseStateOperand`, `promisorOperand` instances)
- Time-based conditions use `AtomicConstraint` with `leftOperand = currentDateTime` (e.g., `currentDateTime lte deadline`)
- Dynamic value resolution on the left side uses `LeftOperand` with `resolutionPath`
- Dynamic value resolution on the right side uses `RuntimeReference` (e.g., `currentAgent`)

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
  clauses   : Clause*,
  meta      : Metadata
}
```

When a policy condition is present, the effective condition for a norm is the conjunction of the policy condition and the norm condition: `n.effectiveCondition = And(P.condition, n.condition)`, consistent with the `PolicyApplicable` and `NormActive` definitions below.

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
```

**`Performed` and `DutyPerformer` are DERIVED, not stored (S6).** They are *views* over the
append-only `Σ.Events`, never an independent Boolean/agent truth source that could drift from the
witness log — see *Witness Derivation* below. The earlier "record a Boolean on performance"
model is withdrawn.

Notes:
- `PromiseState(p, Σ)` is the derived promise state (see Promise State Derivation). For standalone promises, it coincides with the stored `Σ.Promises[p].state`.
- `RequirementRecord` carries lifecycle `status` using the same `rl2:ObligationState` individuals (`Pending`, `Active`, `Fulfilled`, `Violated`) defined in the Vocabulary.
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
wrong-typed, multi-valued, or fail to resolve. RL2 makes this total with two typed carriers
used uniformly across the denotational semantics, the IR (`RL2_IR.md`), the protocol
(`RL2_Protocol.md`), and the Go API:

```
EvalValue<T> = Ok(T)              -- a single well-typed value
             | Missing(Key)        -- operand resolved to ⊥ / absent (e.g. no targetNorm)
             | Invalid(Error)      -- malformed lexical value or incompatible datatype
             | Conflict(Values)    -- resolution produced more than one value

Truth        = True
             | False
             | Unknown(Error)      -- a condition whose truth cannot be determined
```

`resolve : LeftOperand × Env × Norm? → EvalValue<Value>` (the `Value ∪ {⊥}` form below is the
`Ok`/`Missing` projection of this). **Comparison lifts errors to `Unknown`:** `apply(operator, l, r)`
returns `True`/`False` only when both sides are `Ok` and type-compatible; any `Missing`, `Invalid`,
or `Conflict` on either side yields `Unknown(e)`.

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
reports `Indeterminate` so the ambiguity is visible and auditable. `rl2p:Indeterminate` is the
protocol carrier for this value.

We write, for the two kinds of denotation:

```
⟦ e ⟧      : Env → Value    -- terms (operands, right-values)
⟦ c ⟧      : Env → Truth    -- conditions
```

### Conditions

Atomic constraints (result is a `Truth`, lifting operand errors to `Unknown`):

```
⟦ AtomicConstraint(op, operator, value, targetNorm?) ⟧(Env) : Truth =
     let leftVal  = resolve(op, Env, targetNorm)          -- : EvalValue<Value>
     let rightVal = case value of
         RuntimeRef(r) → resolveRuntime(r, Env)           -- : EvalValue<Value>
         Literal(v)    → Ok(v)
     in apply(operator, leftVal, rightVal)                -- Ok∧Ok → True|False; else Unknown(e)
```

The optional `targetNorm` parameter specifies which norm's state to query when using `obligationStateOperand` or `dutyPerformerOperand`. The right operand may be a literal value or a runtime reference (e.g., `currentAgent`). If either operand is `Missing`/`Invalid`/`Conflict`, `apply` returns `Unknown` carrying that error — the constraint never silently reads as `False`.

Logical conditions (Kleene strong three-valued — see Result and Truth Algebra):

```
⟦ And(c1, c2)  ⟧(Env) = ⟦c1⟧(Env) ∧ᴷ ⟦c2⟧(Env)
⟦ Or(c1, c2)   ⟧(Env) = ⟦c1⟧(Env) ∨ᴷ ⟦c2⟧(Env)
⟦ Not(c)       ⟧(Env) = ¬ᴷ⟦c⟧(Env)
⟦ Xone(c1..cn) ⟧(Env) = Unknown  if any ⟦cᵢ⟧(Env) = Unknown
                        True      iff exactly one ⟦cᵢ⟧(Env) = True (and none Unknown)
                        False     otherwise
```

Event constraint (approval requirement) — a total Σ query, so `True`/`False` only (absence is `False`, not `Unknown`):

```
⟦ EventConstraint(expectsEvent) ⟧(Env) =
    True  if ∃e ∈ Env.Σ.Events : matches(e, expectsEvent)
    False otherwise
```

---

### Helper Function Specifications

The condition semantics rely on several helper functions. For a verified kernel, these must be precisely specified.

#### resolve : LeftOperand × Env × Norm? → Value

The function `resolve(leftOperand, Env, targetNorm?)` maps a left operand to a value. The optional `targetNorm` parameter is required for norm state operands.

**Resolution Precedence**: Operands are resolved in the following order:

1. **Core operands** (obligationStateOperand, dutyPerformerOperand, promiseStateOperand, promisorOperand) — handled specially
2. **Path-based resolution** — if `op.resolutionPath` is defined, use `deref()`
3. **Function-based resolution** — if `op.resolutionFunction` is defined, invoke it
4. **External lookup** — fallback to context-based resolution

```
resolve : LeftOperand × Env × Norm? → Value ∪ {⊥}

resolve(op, Env, targetNorm) =
    case op of
        -- Core operands (norm state queries)
        obligationStateOperand →
            if targetNorm ≠ ⊥ then Env.Σ.ObligationState(targetNorm)
            else ⊥
        dutyPerformerOperand →
            if targetNorm ≠ ⊥ then DutyPerformer(targetNorm, Env.Σ)   -- derived from the witness log (S6)
            else ⊥
        promiseStateOperand →
            if targetNorm ≠ ⊥ then PromiseState(targetNorm, Env.Σ)
            else ⊥
        promisorOperand →
            if targetNorm ≠ ⊥ then Env.Σ.Promises[targetNorm].promisor
            else ⊥

        -- Profile-declared operands with explicit resolution
        _ | op.resolutionPath ≠ ⊥ →
            deref(op.resolutionPath, Env)

        _ | op.resolutionFunction ≠ ⊥ →
            invokeFunction(op.resolutionFunction, Env)

        -- Legacy/fallback resolution
        _  → lookupExternal(op, Env.Context)
```

Where:
* `obligationStateOperand` queries `Σ.ObligationState(targetNorm)` — returns Pending, Active, Fulfilled, or Violated
* `dutyPerformerOperand` queries `DutyPerformer(targetNorm, Σ)` — derived from the witness event; returns the Agent who fulfilled the duty, or ⊥
* `promiseStateOperand` queries `PromiseState(targetNorm, Σ)` — returns Pending, Fulfilled, or Violated (Promise-valued counterpart of `obligationStateOperand`; `targetNorm` must be a Promise)
* `promisorOperand` queries `Σ.Promises[targetNorm].promisor` — returns the Agent bound by the promise, or ⊥ (Promise-valued counterpart of `dutyPerformerOperand`)
* `op.resolutionPath` — path expression declared on the operand via `rl2:resolutionPath`
* `op.resolutionFunction` — function name declared on the operand via `rl2:resolutionFunction`
* `invokeFunction(name, Env)` — implementation-specific function invocation
* `lookupExternal(op, Ctx)` — resolves operands from external context (HR systems, directories, etc.)
* `⊥` indicates undefined (evaluation fails if encountered)

**Architectural Principle**: All runtime and contextual data access SHOULD go through declared `rl2:LeftOperand` instances with explicit `rl2:resolutionPath` or `rl2:resolutionFunction`. This ensures:
- Type safety (operands can declare expected ranges)
- Validation (SHACL can verify operand usage)
- Mechanization (clear mapping to formal verification targets)
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
resolveRuntime : RuntimeReference × Env → Value ∪ {⊥}

resolveRuntime(ref, Env) =
    case ref of
        currentAgent → Env.Agent
        _            → ⊥  -- Unknown runtime reference
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

#### deref : Path × Env → Value

The function `deref(path, Env)` traverses a path expression to retrieve a value. This is the **primary mechanism for resolving profile-declared operands** via `rl2:resolutionPath`.

**Path Grammar** (normative):

All path expressions MUST conform to the following grammar:

```
Path       ::= Root ('.' Segment)*
Root       ::= 'agent' | 'asset' | 'context' | 'state' | 'request'
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
2. References roots other than the canonical set (`agent`, `asset`, `context`, `state`, `request`)
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

```
deref : Path × Env → Value ∪ {⊥}

deref(path, Env) =
    let segments = split(path, '.')
    let root = case head(segments) of
        "agent"   → Env.Agent
        "asset"   → Env.Asset
        "context" → Env.Context
        "state"   → Env.Σ
        "request" → Env.Request
        _         → ⊥
    in foldl(navigate, root, tail(segments))

navigate(obj, segment) =
    case obj of
        ⊥       → ⊥
        Record  → obj.segment if segment ∈ fields(obj) else ⊥
        Map     → obj[segment] if segment ∈ keys(obj) else ⊥
        _       → ⊥
```

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

1. **Root validation**: Reject paths not starting with a canonical root (`agent`, `asset`, `context`, `state`, `request`)
2. **Grammar validation**: Reject paths containing `..`, `/`, `%`, or other traversal/encoding patterns
3. **Wildcard restriction**: Reject `*` in any position other than immediately after `state.Events`
4. **Depth limiting**: **MUST** reject paths exceeding `MaxPathDepth` (conformance parameter, default 10). The bound is mandatory; only its value is implementation/profile-declared (S8a).
5. **Fail-closed**: Return `⊥` (not an error message) for invalid paths to prevent information leakage

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
        PromisedState(c)      → ⟦c⟧(mkEnv(nullRequest, Σ, emptyContext))
        PromisedDuty(d)       → Σ.ObligationState(d) = Fulfilled
```

#### timeout : Condition → Boolean

The function `timeout(c)` checks if a temporal deadline has passed. Since time-based conditions use `AtomicConstraint` with `currentDateTime`, we extract deadline values from constraints using `lte` or `lt` operators:

```
timeout : Condition × State → Boolean

timeout(c, Σ) =
    case extractDeadline(c) of
        None      → false
        Some(t)   → Σ.Clock > t

extractDeadline(c) =
    case c of
        AtomicConstraint(currentDateTime, lte, t)  → Some(t)
        AtomicConstraint(currentDateTime, lt, t)   → Some(t)
        And(c1, c2)                                → min(extractDeadline(c1), extractDeadline(c2))
        Or(c1, c2)                                 → max(extractDeadline(c1), extractDeadline(c2))
        _                                          → None
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

`TimeBound` values are obtained from temporal comparisons in conditions (e.g., `currentDateTime lte t`) or profile-specific temporal properties that reduce to the same structure.

For evaluation, deadline expiry is checked via:

```
deadlinePassed(content, Σ) =
    case deadline(content, Σ) of
        None    → false
        Some(t) → Σ.Clock > t
```

This predicate is used in the Promise Violation rule to determine when a pending promise has exceeded its temporal bounds without fulfillment.

#### apply : Operator × Value × Value → Boolean

The function `apply(op, left, right)` applies a comparison operator:

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
        isAnyOf  → left ∈ right
        isAllOf  → ∀v ∈ right : v ∈ left
        isNoneOf → ∀v ∈ right : v ∉ left
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
    Permit         if matches(Privilege(a,x,s,c), R) ∧ ⟦c⟧(Env) = True
    Indeterminate  if matches(Privilege(a,x,s,c), R) ∧ ⟦c⟧(Env) = Unknown(_)
    Inactive       otherwise   -- no match, or ⟦c⟧(Env) = False
```

Prohibition activation:

```
⟦Prohibition(a,x,s,c)⟧(R, Env) =
    Deny           if matches(Prohibition(a,x,s,c), R) ∧ ⟦c⟧(Env) = True
    Indeterminate  if matches(Prohibition(a,x,s,c), R) ∧ ⟦c⟧(Env) = Unknown(_)
    Inactive       otherwise
```

Duty activation:

```
⟦Duty(a,x,s,c)⟧(R, Env) =
    Obligation(a,x,s)  if matches(Duty(a,x,s,c), R) ∧ ⟦c⟧(Env) = True
    Indeterminate      if matches(Duty(a,x,s,c), R) ∧ ⟦c⟧(Env) = Unknown(_)
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
∀ Prohibition(s, x, o, c) : ∃ Claim(h, s, ¬x@o) where
    h = counterparty(Prohibition) if present, else grantor(policyOf(Prohibition)) ∧
    correlatesTo(Claim, Prohibition)
```

The correlative Claim is **derived**, not authored: policy authors write only the
`Prohibition`. Violation of a prohibition uses the subsumption-aware `performed()`
helper (so performing a narrower action `x′ ⊑ x` violates a prohibition on `x`).

### Claim Denotation and Content Derivation (C6b)

A Claim is the Hohfeldian correlative of **exactly one** Duty, reached by its required
`rl2:correlativeTo` link (enforced by `ClaimShape`). A Claim does **not** author its own content;
its action, object, and condition are **derived** from that Duty:

```
ClaimContent(Claim) =
    let D = correlativeTo(Claim)                     -- exactly one, and D : Duty (ClaimShape)
    in (action, object, condition) := (D.action, D.object, D.condition)   -- DERIVED, not authored
```

with the party roles required to mirror the Duty (validated by `ClaimShape`):

```
D.subject = Claim.counterparty   (the duty-bearer)   ∧
D.counterparty = Claim.subject   (the right-holder)
```

A Claim is *held* exactly when its correlative Duty's condition holds; the Claim inherits the
Duty's `Truth` (S2), so an `Unknown` Duty condition yields an `Indeterminate` claim rather than a
silently-inactive one:

```
⟦Claim(h, a)⟧(Env) =                                 -- h = subject (right-holder), a = counterparty (duty-bearer)
    let D = correlativeTo(Claim)
    in ClaimHeld(h, a, ClaimContent(Claim))  if ⟦D.condition⟧(Env) = True
       Indeterminate                          if ⟦D.condition⟧(Env) = Unknown(_)
       ClaimInactive                          otherwise
```

Because content and correlation are derived from the single authored Duty, two claims about
different actions or objects are always distinguishable (via their distinct Duties), the
Claim↔Duty pairing is one-to-one, and there is no dual-source encoding where a Claim and its
Duty could disagree.

### Power Denotation

A Power is the ability of an agent to alter normative relations:

```
⟦Power(a, n)⟧(Env) =
    PowerActive(a, n)   if powerCondition(a, n, Env) = true
    PowerInactive       otherwise
```

Where `n` is the norm that the agent has power to create, modify, or extinguish.

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

### Liability Denotation

A Liability is the correlative of a Power — the susceptibility to have one's normative position altered:

```
⟦Liability(a, n)⟧(Env) =
    LiabilityActive(a, n)   if ∃ Power(h, n) where subject(n) = a
    LiabilityInactive       otherwise
```

When a Power is exercised, the Liability-holder's position changes accordingly.

### Immunity Denotation

An Immunity protects an agent from having their normative position altered:

```
⟦Immunity(a, n)⟧(Env) =
    ImmunityActive(a, n)    if immunityCondition(a, n, Env) = true
    ImmunityInactive        otherwise
```

Immunity blocks Power exercise:

```
∀ Power(h, n), Immunity(a, n):
    ImmunityActive(a, n) → ¬canExercise(Power(h, n))
```

### Sanctions and Remedies

Violations trigger remedial norms via Power/Liability relations:

```
DutyViolated(a, x, s) ∧ Power(h, sanction) ∧ Liability(a, sanction)
─────────────────────────────────────────────────────────────────────
    h may exercise Power(h, sanction) against a
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
    P.condition = ⊥  ∨  ⟦P.condition⟧(Env) = True
```

Where `⊥` denotes the absence of a condition (unconditionally applicable).

## Applicable Policy Set

Given a universe of policies U and environment Env:

```
ApplicablePolicies(U, Env) = { P ∈ U | PolicyApplicable(P, Env) }
```

**PolicyUniverse determination**: The universe U is the set of all policies in the active *generation*. When evaluation begins, the evaluator resolves the generation identifier (from `rl2p:policyGeneration` on the Case) to obtain U. This is an evaluator responsibility, not a semantic operation — the semantics assume U is provided. See §Policy Generations for the generation model.

## Effective Norm Activation

A norm n within policy P is active when both the policy and norm conditions hold:

```
NormActive(n, P, Env) = PolicyApplicable(P, Env) ∧ ⟦n.condition⟧(Env) = True
```

`NormActive` (and the firm `Out` envelope below) admits a norm only on `True`. A norm whose
condition is `Unknown` is **neither** active **nor** silently discarded: it is collected into
the `indeterminate` set (see Evaluation Algorithm, S2) and promotes the decision to
`Indeterminate` when it could affect the outcome.

This is semantically equivalent to:

```
n.effectiveCondition = And(P.condition, n.condition)
```

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
- `rl2p:requirementStatus` is the protocol/runtime projection:
  - A pending promise that is **effective now** may be represented as an `Active` requirement (monitored/in-force) while the semantic promise state remains `Pending`.
  - If the promise is not yet effective, the requirement remains `Pending`.
  - Terminal promise states map to terminal requirement states.

### Duty Activation

A pending duty becomes active when its activation condition holds:

```
Env = mkEnv(R, Σ, Ctx)
⟦ c ⟧(Env) = True
Σ.ObligationState(Duty(a,x,s,c)) = Pending
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Duty(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Active], DutyActive(a,x,s,c))
```

### Duty Fulfillment

An active duty is fulfilled when the required action (or a narrower action subsumed by it) is performed. The performing agent is recorded in `DutyPerformer`:

```
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

### Duty Violation

An active duty is violated when its deadline passes without fulfillment:

```
Env = mkEnv(R, Σ, Ctx)
Σ.ObligationState(Duty(a,x,s,c)) = Active
performed(a,x,s,Σ) = false
timeout(c, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Violated], DutyViolated(a,x,s,c))
```

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

**Crystallization function** (total over the three content forms):

```
crystallize(Promise(p, q, κ)) = (D, C)
    where C = Claim(subject = q, counterparty = p, correlativeTo = D)
```

| Promise content `κ` | Crystallized Duty `D` | Fulfillment criterion (inherited from the Promise) | Behavioral wiring |
|---|---|---|---|
| `PromisedAction(x)` on `o` | `Duty(subject=p, action=x, object=o)` | `D` Fulfilled when `p` has performed `x` (`performed()`, subsumption-aware) | none — standard action-performance duty. **Fully closed.** |
| `PromisedState(c)` on `o` | state-maintenance `Duty(subject=p, object=o)` whose fulfillment is `c` | Fulfilled while `c` holds; Violated when `c` fails or its deadline passes | ObligationState transitions for a condition-fulfilled ("maintenance") duty + `restoreAction` on breach → **SEM-1** |
| `PromisedDuty(d)` | second-order (suretyship) `Duty(subject=p)` over `d` | Fulfilled when `d`'s ObligationState reaches `Fulfilled` | the remedy/liability the surety `p` incurs when `d` is Violated (guarantee vs indemnity) → **PROM-5** |

Each Duty's fulfillment criterion is inherited directly from the promise content's
*already-defined* semantics (`rl2.ttl`: `promisedAction` / `promisedState` /
`promisedDuty` all specify fulfillment/violation). Crystallization therefore
introduces **no new fulfillment semantics** — it re-homes an existing criterion
onto a Duty and adds the correlative Claim. The two behavioral wirings flagged
above (how a maintenance duty's ObligationState machine advances; what obligation a
surety incurs on breach) are residual specification tasks owned by SEM-1 and
PROM-5; the crystallization *targets* fixed here hold regardless of how those
resolve, so the Offer→Agreement transition is well-defined for every promise now.

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
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, PromiseViolated(p, q, content)) →
    (Σ[ObligationState(d) ↦ Active,
       Requirements ↦ Σ.Requirements ∪ {Requirement(d, Promise(p,q,content), q)}],
     RemedialDutyGenerated(d))
```

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
- The generated `Requirement` tracks `sourceNorm = Promise(p,q,content)` and `counterparty = q` (the promisee).
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
    let e⁺ = e with eventSequence = nextSeq(Σ.Events)   -- assign the total-order sequence on append
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

### Privilege Activation

Privileges become active when their condition holds:

```
Env = mkEnv(R, Σ, Ctx)
matches(Privilege(a,x,s,c), R) = true
⟦ c ⟧(Env) = True
──────────────────────────────────────────────────────────────────
PrivilegeActive(a, x, s, c)
```

Privileges become inactive when their condition no longer holds or the request doesn't match:

```
Env = mkEnv(R, Σ, Ctx)
matches(Privilege(a,x,s,c), R) = false ∨ ⟦ c ⟧(Env) = false
──────────────────────────────────────────────────────────────────
PrivilegeInactive(a, x, s, c)
```

### Prohibition Activation

Prohibitions are active when their condition holds and the request matches:

```
Env = mkEnv(R, Σ, Ctx)
matches(Prohibition(a,x,s,c), R) = true
⟦ c ⟧(Env) = True
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

The function `Out` computes the **unresolved set** of normative atoms from a policy universe and environment (atoms are deduplicated by canonical identity — the `∪` below is set union, not multiset sum):

```
Out : (PolicyUniverse U, Env) → ℘(NormativeAtoms)

Out(U, Env) =
    let applicablePolicies = ApplicablePolicies(U, Env)
    in ⋃ { deriveNorms(P, Env) | P ∈ applicablePolicies }

deriveNorms(P, Env) =
    { permit(a,x,s)    | Privilege(a,x,s,c) ∈ P.clauses, matches(_, R), ⟦c⟧(Env) = True } ∪
    { forbid(a,x,s)    | Prohibition(a,x,s,c) ∈ P.clauses, matches(_, R), ⟦c⟧(Env) = True } ∪
    { obligate(d)      | Duty d ∈ P.clauses, matches(d, R), ⟦d.condition⟧(Env) = True } ∪
    { violated(d)      | Duty d ∈ P.clauses, Σ.ObligationState(d) = Violated }
```

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
Eval(U, R, Σ, Ctx) =
    let Env = mkEnv(R, Σ, Ctx)
    let envelope = Out(U, Env)                    -- ① Derivation (monotone)
    let Σ' = updateDutyStates(envelope, Env, Σ)   -- ② State transitions
    let decision = resolveDecision(envelope, Σ', strategy)  -- ③ Resolution (non-monotone)
    in (decision, Σ', duties(envelope))
```

The **normative envelope** `Out(U, Env)` is the first-class intermediate result — visible before resolution, available for audit, and monotone in the policy universe (for a fixed environment).

Resolution may eliminate norms via priority or strategy, breaking monotonicity. This is by design: `permit(a,x,s) ∧ forbid(a,x,s)` is not a logical contradiction but a **conflict to be resolved procedurally**.
`resolveDecision` is a parameterized algorithm (strategy + priorities); if these inputs cannot break ties, the evaluator must surface an explicit ambiguity/error rather than applying an implicit specificity heuristic.

For architectural context on the full evaluation pipeline, see **RL2_Architecture.md** §Evaluation Pipeline.

---

## Big-Step Semantics (Policy Evaluation)

### Evaluation Function Signature

The total decision function takes a policy universe and Request as first-class parameters:

```
Eval : (PolicyUniverse U, Request R, State Σ, Context Ctx) → (Decision, State, DutySet)
```

Where:
* `U` is the universe of policies (the current generation)
* `R = (a_req, x_req, s_req)` is the request (agent, action, asset)
* `Σ` is the current system state
* `Ctx` is the external context (assertions from Protocol's ContextAssertion)
* `Decision ∈ {Permit, Deny, PermitWithObligations, NotApplicable, Indeterminate}`
* The returned `State` reflects any state updates from evaluation
* `DutySet` contains duties in Pending or Active state requiring fulfillment

### Evaluation Algorithm

```
Eval(U, R, Σ, Ctx) =
    let Env = mkEnv(R, Σ, Ctx)

    -- Step 0: Determine applicable policies
    let applicablePolicies = ApplicablePolicies(U, Env)

    -- Step 1: Find matching norms within applicable policies
    let matchingPrivileges = { p ∈ P.clauses | P ∈ applicablePolicies ∧ p : Privilege ∧ matches(p, R) }
    let matchingProhibitions = { p ∈ P.clauses | P ∈ applicablePolicies ∧ p : Prohibition ∧ matches(p, R) }
    let matchingDuties = { d ∈ P.clauses | P ∈ applicablePolicies ∧ d : Duty ∧ matches(d, R) }

    -- Step 2: Evaluate conditions three-valued (S2). A matched norm whose condition
    -- is Unknown is Indeterminate — collected, never silently dropped.
    let activePrivileges = { p ∈ matchingPrivileges | ⟦p.condition⟧(Env) = True }
    let activeProhibitions = { p ∈ matchingProhibitions | ⟦p.condition⟧(Env) = True }
    let indeterminate = { n ∈ matchingPrivileges ∪ matchingProhibitions ∪ matchingDuties
                          | ⟦n.condition⟧(Env) = Unknown(_) }

    -- Step 3: Update duty states (only True-conditioned duties transition)
    let Σ' = updateDutyStates({ d ∈ matchingDuties | ⟦d.condition⟧(Env) = True }, Env, Σ)
    let activeDuties = { d | Σ'.ObligationState(d) ∈ {Pending, Active} }
    let violatedDuties = { d | Σ'.ObligationState(d) = Violated }

    -- Step 4: Apply conflict resolution and compute decision
    let decision = resolveDecision(activePrivileges, activeProhibitions,
                                    activeDuties, violatedDuties, indeterminate,
                                    P.conflictStrategy)

    in (decision, Σ', activeDuties)
```

**Indeterminate handling (S2).** `resolveDecision` takes the `indeterminate` set as an
explicit argument. Its policy is fixed and deterministic: if a *conclusive* verdict is
reached without relying on the indeterminate norms — a `Deny` under prohibit-overrides, or a
`Permit` with no competing prohibition/indeterminate prohibition — that verdict stands.
Otherwise, if `indeterminate ≠ ∅` and it could have changed the outcome, the result is
`Indeterminate`. Mapping `Indeterminate → Deny` is an **enforcement-adapter** decision (a
fail-closed PEP), **not** the semantic verdict: `Eval` returns `Indeterminate` so the
ambiguity is auditable.

### Conflict Resolution

When multiple norms apply, conflicts must be resolved. RL2 provides two complementary mechanisms:

1. **Policy-level priority** (`rl2:priority`): Norms may declare an integer priority; higher values override lower. This is vocabulary defined in the ontology.

2. **Evaluator-level strategy**: The evaluator is configured with a conflict resolution strategy (e.g., prohibit-overrides, permit-overrides). This is **evaluator configuration**, not policy vocabulary—analogous to XACML combining algorithms.

The `strategy` parameter in `resolveDecision` below represents evaluator configuration. Policies express norms and priorities; evaluators decide how to combine conflicting results when priorities are equal.

More sophisticated defeasibility mechanisms—such as exclusionary rules—are available in frameworks like LegalRuleML [LegalRuleML] and may be incorporated in future RL2 profiles.

```
resolveDecision(privileges, prohibitions, activeDuties, violatedDuties, indeterminate, strategy) =
    let base = case strategy of
        ProhibitOverrides →
            if prohibitions ≠ ∅ then Deny
            else baseDecision(privileges, activeDuties, violatedDuties)

        PermitOverrides →
            if privileges ≠ ∅ ∧ activeDuties = ∅ then Permit
            else if prohibitions ≠ ∅ then Deny
            else baseDecision(privileges, activeDuties, violatedDuties)

        SpecificOverridesGeneral →
            let winner = mostSpecific(privileges ∪ prohibitions)
            in case winner of
                Privilege(_) → baseDecision({winner}, activeDuties, violatedDuties)
                Prohibition(_) → Deny

        _ → -- Default: prohibit-overrides
            if prohibitions ≠ ∅ then Deny
            else baseDecision(privileges, activeDuties, violatedDuties)
    in
    -- S2: an unresolved (Unknown-conditioned) norm only matters if it could flip the
    -- verdict. A firm Deny is conclusive regardless; otherwise a non-empty indeterminate
    -- set makes the result Indeterminate rather than a possibly-wrong Permit/NotApplicable.
    if base = Deny then Deny
    else if indeterminate ≠ ∅ then Indeterminate
    else base

baseDecision(privileges, activeDuties, violatedDuties) =
    if privileges = ∅ then NotApplicable
    else if violatedDuties ≠ ∅ then Deny  -- Violations block access
    else if activeDuties ≠ ∅ then PermitWithObligations
    else Permit
```

`Indeterminate` here is the same value produced per-norm in the denotations above and carried
by `rl2p:Indeterminate` at the protocol layer; a fail-closed PEP maps it to `Deny`, but that
mapping lives in the enforcement adapter, not in `resolveDecision`.

Note: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

### Duty State Updates

The duty lifecycle is governed by three inference rules:

**Rule D-ACTIVATE** (Pending → Active):
```
Σ.ObligationState(d) = Pending
⟦d.condition⟧(Env) = True
─────────────────────────────────────────────────────────
Σ' = Σ[ObligationState(d) ↦ Active]
```

Activation is **condition-driven**: when the duty's condition first evaluates to true, the duty becomes active. This typically occurs when temporal preconditions are met (e.g., "after contract signing").

**Rule D-FULFILL** (Active → Fulfilled):
```
Σ.ObligationState(d) = Active
performed(d.subject, d.action, d.object, Σ) = true
─────────────────────────────────────────────────────────
Σ' = Σ[ObligationState(d) ↦ Fulfilled]
```

Fulfillment is **event-driven**: when a performed action matches the duty's required action (including narrower actions via `rl2:includedIn` subsumption), the duty is fulfilled. The transition records **only** the state change — the performing agent is **not** stored, because `DutyPerformer(d, Σ)` is derived on demand from the witnessing event (S6), so identity binding reads the witness rather than a duplicated field that could drift.

**Rule D-VIOLATE** (Active → Violated):
```
Σ.ObligationState(d) = Active
performed(d.subject, d.action, d.object, Σ) = false
timeout(d.condition, Σ) = true
─────────────────────────────────────────────────────────
Σ' = Σ[ObligationState(d) ↦ Violated]
```

Violation is **time-driven**: when the deadline passes without fulfillment (no exact or subsumed action performed), the duty is violated.

**Algorithmic form** (for implementation):

```
updateDutyStates(duties, Env, Σ) =
    foldl(updateOneDuty(Env), Σ, duties)

updateOneDuty(Env)(Σ, d) =
    case Σ.ObligationState(d) of
        Pending → if ⟦d.condition⟧(Env) then Σ[ObligationState(d) ↦ Active] else Σ
        Active  → if performed(d.subject, d.action, d.object, Σ)
                  then Σ[ObligationState(d) ↦ Fulfilled]   -- DutyPerformer derived from witness (S6)
                  else if timeout(d.condition, Σ)
                  then Σ[ObligationState(d) ↦ Violated]
                  else Σ
        _       → Σ  -- Fulfilled/Violated are terminal
```

### PermitWithObligations Semantics

When `Eval` returns `PermitWithObligations`:
* Access is conditionally granted
* The returned `DutySet` contains duties that must be fulfilled
* Duties may be in `Pending` (activation condition not yet met) or `Active` (must be performed)
* The Protocol's Requirement class captures these for tracking

This allows pre-access duties (must fulfill before action) and post-access duties (must fulfill after action) to be distinguished by their conditions.

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
| `MaxConditionDepth` | 20 | condition tree nesting (fuel is linear in tree size) |
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
8. **No iteration**: `resolutionFunction` must be O(1) or O(log n) per invocation — **and is outside the verified core** (S8a); an opaque function voids the kernel's guarantees unless the profile documents its bounds
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

**Extension warning (S8a)**: `resolutionFunction` and `lookupExternal` are **outside the verified core**. The kernel's totality/complexity guarantees cover only `resolutionPath`-based resolution and the bounded operations above. Implementations using unbounded external queries via `resolutionFunction` or `lookupExternal` may exhibit non-polynomial or non-terminating behavior; such extensions MUST document their determinism and complexity characteristics and are not covered by the core proof obligations.

---

## Proof scope and normative artifact

RL2's formal guarantees are established by proving properties of the **reference evaluator written in Dafny and extracted to Go**. The extracted evaluator is the **normative realization** of RL2 semantics for implementation purposes. Proof obligations (S1–S6 and successors) apply to this evaluator and its extracted code, not to an open class of independent implementations.

---

## Mechanization

*This section is non-normative.*

RL2's semantics are explicitly designed for mechanization in Dafny, with the extracted Go evaluator as the endorsed runtime artifact. The abstract syntax maps cleanly to algebraic datatypes, and the operational rules are syntax-directed.

## Target Platforms

| Platform | Strengths | Status |
|----------|-----------|--------|
| **Dafny + Go extraction** | Algebraic types, Z3 backend, compiles to Go/Java/C#, cloud-native ecosystem | Primary (normative) |
| **K Framework** | Executable semantics, automatic interpreter generation | Optional independent validation |
| **Lean 4** | Dependent types, code extraction, AI-assisted proofs | Optional independent validation |
| **Coq** | Mature ecosystem, CompCert precedent | Optional independent validation |

## Dafny Example

```dafny
datatype Condition =
  | AtomicConstraint(op: Operand, cmp: Operator, val: Value)
  | And(left: Condition, right: Condition)
  | Or(left: Condition, right: Condition)
  | Not(inner: Condition)
  | Xone(operands: seq<Condition>)

function EvalCondition(c: Condition, env: Env): bool
  requires ValidEnv(env)
  ensures EvalCondition(c, env) ==> ConditionSatisfied(c, env)
{
  match c
    case AtomicConstraint(op, cmp, val) => Apply(cmp, Resolve(op, env), val)
    case And(l, r) => EvalCondition(l, env) && EvalCondition(r, env)
    case Or(l, r) => EvalCondition(l, env) || EvalCondition(r, env)
    case Not(inner) => !EvalCondition(inner, env)
    case Xone(cs) =>
      |set i | 0 <= i < |cs| && EvalCondition(cs[i], env)| == 1
}
```

Transition rules are expressed as Dafny lemmas with pre/post-conditions verified by Z3.

## Proof Obligations

The following properties should be proved for a verified implementation:

1. **(S1) Determinism**: Given Σ, R, Ctx, evaluation produces a unique result
2. **(S2) Progress**: Every well-typed expression either is a value or can step
3. **(S3) Preservation**: Types are preserved under transitions
4. **(S4) Duty-state consistency**: No duty can be both Fulfilled and Violated
5. **(S5) Timeout correctness**: Deadlines are eventually enforced
6. **(S6) Totality**: `Eval` terminates for all well-formed inputs

See **`RL2_IR.md`** for the compilation target these properties are proved against, and **`issues.md`** (Band 4 — Implementation) for the phased Dafny/Go implementation plan and deliverable specifications.

For expressive characterization and comparison with other formalisms, see **RL2_Architecture.md**.

---

## References

See **RL2_References.md** for complete citations and glossary.

Related RL2 specifications:
- rl2.ttl — Core ontology (OWL)
- rl2-shacl.ttl — SHACL validation shapes
- RL2_Protocol.md — Runtime evaluation protocol
