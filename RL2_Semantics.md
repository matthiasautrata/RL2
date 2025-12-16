---
title: "RL2 Formal Semantics"
subtitle: "A Unified Normative, Operational, and Semantic Framework for Rights and Data Policies"
version: "0.5"
status: "Draft"
date: 2025-12-08
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
  | Claim(AgentHolder, AgentAgainst, Right)
  | Power(Agent, Norm)
  | Liability(Agent, Norm)
  | Immunity(Agent, Norm)
```

#### Promises

```
Promise ::= Promise(Agent promisor, Agent promisee, PromiseContent)
```

where `PromiseContent ∈ {Action, Duty, Condition}` (matching the `rl2:PromiseContent` union class in the ontology).

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
- `leftOperand` is drawn from profile-defined operands (RL2 Core defines `rl2:LeftOperand` class plus `currentDateTime`, `obligationStateOperand`, `dutyPerformerOperand` instances)
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
Policy ::= Policy {
  condition : Condition?,   -- optional policy-level activation condition
  clauses   : Norm*,
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
     Events : EventType → E*,
     Performed : A × X × S → Boolean,
     Metadata : S → Map,
     Promises : Promise → PromiseRecord,
     ObligationState : Duty → {Pending, Active, Fulfilled, Violated},
     DutyPerformer : Duty → Agent ∪ {⊥},
     Requirements : RequirementID → RequirementRecord)

PromiseRecord = (promisor : Agent,
                 promisee : Agent,
                 content : PromiseContent,
                 state : PromiseState)
```

Notes:
- `PromiseState(p, Σ)` is the derived promise state (see Promise State Derivation). For standalone promises, it coincides with the stored `Σ.Promises[p].state`.
- `RequirementRecord` carries lifecycle `status` using the same `rl2:ObligationState` individuals (`Pending`, `Active`, `Fulfilled`, `Violated`) defined in the Vocabulary.
- `ObligationState` is the canonical name (matching `rl2:ObligationState` in the ontology).
- PromiseState values (`Pending`, `Fulfilled`, `Violated`) reuse the shared state individuals defined in the Vocabulary (promises do not use `Active`).
- `DutyPerformer` tracks which agent fulfilled a duty. Returns `⊥` if the duty has not been fulfilled. This enables identity binding patterns:
  - *Tun-sollen* (ought-to-do): `DutyPerformer(d) = currentAgent` — the same agent must fulfill
  - *Sein-sollen* (ought-to-be): Check only `ObligationState(d) = Fulfilled` — anyone may fulfill
  - *Separation of Duty*: `DutyPerformer(d) ≠ currentAgent` — a different agent must fulfill

**Event Log Structure** (normative):

`Σ.Events` is a **typed, temporally-ordered index**: a map from event type to a sequence of events of that type, ordered by `eventTime` (most recent last).

```
Events : EventType → E*
Events[type] = [e₁, e₂, ..., eₙ]  where eᵢ.eventTime ≤ eᵢ₊₁.eventTime
```

Path access semantics (normative):

```
state.Events.<type>           ≡  maxBy(eventTime, Events[type])  or ⊥ if empty
state.Events.<type>.<prop>    ≡  (maxBy(eventTime, Events[type])).<prop>
state.Events.*                ≡  maxBy(eventTime, ⋃ Events[t] for all t)
```

This "most-recent-wins" rule is provable and ensures deterministic event selection.

This model supports both:
- **Named event access**: `state.Events.breakGlassEvent.operationalAgent`
- **Pattern-based selection**: via EventConstraint + wildcard paths

**Scope of Σ**: In practice, Σ represents the *evidence log* or *relevant history* for a given evaluation context—not a theoretically omniscient record of all actions ever performed. Implementations scope Σ to the Case being evaluated (see RL2_Protocol.md), tracking only events and actions relevant to that access request's lifecycle.

### Environments

```
Env = Agent × Asset × State × ExternalContext
```

Used for evaluating operand paths.

---

## Denotational Semantics

Denotational semantics gives timeless meaning to norms and conditions.

We write:

```
⟦ e ⟧ : Env → Value
```

### Conditions

Atomic constraints:

```
⟦ AtomicConstraint(op, operator, value, targetNorm?) ⟧(Env) =
     let leftVal = resolve(op, Env, targetNorm)
     let rightVal = case value of
         RuntimeRef(r) → resolveRuntime(r, Env)
         Literal(v)    → v
     in apply(operator, leftVal, rightVal)
```

The optional `targetNorm` parameter specifies which norm's state to query when using `obligationStateOperand` or `dutyPerformerOperand`. The right operand may be a literal value or a runtime reference (e.g., `currentAgent`).

Logical conditions:

```
⟦ And(c1, c2)  ⟧(Env) = ⟦c1⟧(Env) ∧ ⟦c2⟧(Env)
⟦ Or(c1, c2)   ⟧(Env) = ⟦c1⟧(Env) ∨ ⟦c2⟧(Env)
⟦ Not(c)       ⟧(Env) = ¬⟦c⟧(Env)
⟦ Xone(c1..cn) ⟧(Env) = true iff exactly one of ⟦c1⟧(Env)..⟦cn⟧(Env) is true
                        (false when zero or more than one)
```

Event constraint (approval requirement):

```
⟦ EventConstraint(expectsEvent) ⟧(Env) =
    true  if ∃e ∈ Env.Σ.Events : matches(e, expectsEvent)
    false otherwise
```

**rl2:requires semantics**: Conditions (and events) may declare dependencies via `rl2:requires`. A dependency `c1 requires c2` means that whenever `c1` is considered, `c2` must also hold. This is expressed in the RDF graph through `rl2:requires` links between `ConditionOrEvent` instances rather than via a distinct Composite constructor in the abstract syntax.

---

### Helper Function Specifications

The condition semantics rely on several helper functions. For a verified kernel, these must be precisely specified.

#### resolve : LeftOperand × Env × Norm? → Value

The function `resolve(leftOperand, Env, targetNorm?)` maps a left operand to a value. The optional `targetNorm` parameter is required for norm state operands.

**Resolution Precedence**: Operands are resolved in the following order:

1. **Core operands** (obligationStateOperand, dutyPerformerOperand) — handled specially
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
            if targetNorm ≠ ⊥ then Env.Σ.DutyPerformer(targetNorm)
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
* `dutyPerformerOperand` queries `Σ.DutyPerformer(targetNorm)` — returns the Agent who fulfilled the duty, or ⊥
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
- Maximum path depth: 10 segments (implementation MAY enforce)

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
   - The most recent (by `rl2:eventTime`) is selected
   - If no events match, returns ⊥

Formally:
```
navigate(Events, "*", constraintInScope) =
    require constraintInScope ≠ ⊥  -- EventConstraint must be present
    let candidates = { e ∈ Events | matches(e, constraintInScope.expectsEvent) }
    in if candidates = ∅ then ⊥
       else maxBy(eventTime, candidates)
```

**Rationale**: Requiring an `EventConstraint` sibling eliminates ambiguity about which event the wildcard selects. Without this constraint, `state.Events.*.operationalAgent` could return the performer of *any* recent event, creating security vulnerabilities in identity-binding patterns.

This rule ensures that identity binding patterns like:
```turtle
rl2:leftOperand emergency:eventPerformerOperand ;  # resolutionPath "state.Events.*.operationalAgent"
```
correctly resolve to the performer of the **triggering event** specified by the accompanying `EventConstraint`.

**Security Requirements** (normative):

Implementations MUST enforce the following security constraints:

1. **Root validation**: Reject paths not starting with a canonical root (`agent`, `asset`, `context`, `state`, `request`)
2. **Grammar validation**: Reject paths containing `..`, `/`, `%`, or other traversal/encoding patterns
3. **Wildcard restriction**: Reject `*` in any position other than immediately after `state.Events`
4. **Depth limiting**: MAY reject paths exceeding implementation-defined maximum depth
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
    typeMatches(e.eventType, pattern.eventType) ∧
    payloadMatches(e.payload, pattern.payload)

typeMatches(actual, expected) =
    actual = expected ∨ actual ⊑ expected  -- subtype relation

payloadMatches(actual, expected) =
    ∀(k, v) ∈ expected : k ∈ actual ∧ valueMatches(actual[k], v)

valueMatches(actual, expected) =
    case expected of
        Literal(v)   → actual = v
        Pattern(p)   → actual matches p
        Any          → true
```

#### contentHolds : PromiseContent × State → Boolean

The function `contentHolds(content, Σ)` checks if promise content is satisfied:

```
contentHolds : PromiseContent × State → Boolean

contentHolds(content, Σ) =
    case content of
        Action(a, x, s)  → Σ.Performed(a, x, s)
        Duty(d)          → Σ.ObligationState(d) = Fulfilled
        Condition(c)     → ⟦c⟧(mkEnv(nullRequest, Σ, emptyContext))
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
        Action(a, x, s)  → None                        -- Raw actions have no inherent deadline
        Duty(d)          → extractDeadline(d.condition)
        Condition(c)     → extractDeadline(c)
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
mkEnv(R, Σ, Ctx) = (a_req, s_req, Σ, Ctx)
```

The environment `Env = (Agent, Asset, State, ExternalContext)` provides the evaluation context for conditions.

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
- `members(s)` returns collection members if `s` is an AssetCollection

**RDF grounding**: In RDF/OWL, `x_req ⊑ x` follows subclass (or SKOS broader/narrower) relations on `rl2:Action` individuals; `members(s)` is the closure over `rl2:member` when `s` is an `rl2:AssetCollection`; and `roles(a_req)` derives from the agent's RDF typing/role assignments as defined in the Agent and role classes in the Vocabulary.

### Norm Denotations

Privilege activation:

```
⟦Privilege(a,x,s,c)⟧(R, Env) =
    Permit    if matches(Privilege(a,x,s,c), R) ∧ ⟦c⟧(Env) = true
    Inactive  otherwise
```

Prohibition activation:

```
⟦Prohibition(a,x,s,c)⟧(R, Env) =
    Deny      if matches(Prohibition(a,x,s,c), R) ∧ ⟦c⟧(Env) = true
    Inactive  otherwise
```

Duty activation:

```
⟦Duty(a,x,s,c)⟧(R, Env) =
    Obligation(a,x,s)  if matches(Duty(a,x,s,c), R) ∧ ⟦c⟧(Env) = true
    Inactive           otherwise
```

Promise status:

```
⟦Promise(p,q,content)⟧(Env) =
    Fulfilled if contentHolds(content, Env.Σ)
    Pending   otherwise
```

where `contentHolds` is defined below.

### Hohfeldian Correlatives and Opposites

RL2 supports the full Hohfeldian framework. The correlatives are:

| Right-holder has | Duty-bearer has |
|------------------|-----------------|
| Privilege | No-Claim |
| Claim | Duty |
| Power | Liability |
| Immunity | Disability |

### Claim Denotation

A Claim expresses that one agent holds a right against another agent for some content:

```
⟦Claim(holder, against, right)⟧(Env) =
    ClaimActive(holder, against, right)  if claimCondition(right, Env) = true
    ClaimInactive                        otherwise
```

A Claim correlates with a Duty: if agent H has a Claim against agent A for X, then A has a Duty to H regarding X.

```
∀ Claim(h, a, x) : ∃ Duty(a, x_action, x_asset, c) where
    subject(Duty) = a ∧
    correlatesTo(Claim, Duty)
```

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
    P.condition = ⊥  ∨  ⟦P.condition⟧(Env) = true
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
NormActive(n, P, Env) = PolicyApplicable(P, Env) ∧ ⟦n.condition⟧(Env) = true
```

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
    (Σ.Clock, Σ.Events, Σ.Performed, Σ.Metadata,
     Σ.Promises, Σ.ObligationState[d ↦ Active])

Σ[PromiseState(p) ↦ Fulfilled] =
    (Σ.Clock, Σ.Events, Σ.Performed, Σ.Metadata,
     Σ.Promises[p ↦ Σ.Promises[p] with state = Fulfilled],
     Σ.ObligationState)
```

### Promise State Derivation

Let `linkedDuty(p)` be `d` when `rl2:promiseContent(p) = d` and `d` is a `Duty`; otherwise `⊥`. Promise state is derived (not guessed) from Σ as:

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
- `fulfilledEvidence(p, Σ)` holds when Σ contains an event or assertion establishing the promise content holds (e.g., `contentHolds(content, Σ)`).
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
⟦ c ⟧(Env) = true
Σ.ObligationState(Duty(a,x,s,c)) = Pending
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Duty(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Active], DutyActive(a,x,s,c))
```

### Duty Fulfillment

An active duty is fulfilled when the required action is performed. The performing agent is recorded in `DutyPerformer`:

```
Σ.ObligationState(Duty(a,x,s,c)) = Active
Σ.Performed(a,x,s) = true
performer = R.agent  -- Agent who performed the action
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) →
    (Σ[ObligationState(Duty(a,x,s,c)) ↦ Fulfilled,
       DutyPerformer(Duty(a,x,s,c)) ↦ performer],
     DutyFulfilled(a,x,s,c))
```

Recording the performer enables identity binding patterns:
- **Tun-sollen check**: `DutyPerformer(d) = currentAgent` (same agent must benefit)
- **Sein-sollen check**: Only check `ObligationState(d) = Fulfilled` (anyone may fulfill)
- **Separation of Duty**: `DutyPerformer(d) ≠ currentAgent` (different agent must benefit)

### Duty Violation

An active duty is violated when its deadline passes without fulfillment:

```
Env = mkEnv(R, Σ, Ctx)
Σ.ObligationState(Duty(a,x,s,c)) = Active
Σ.Performed(a,x,s) = false
timeout(c, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Violated], DutyViolated(a,x,s,c))
```

### Promise Fulfillment

For promises without a linked duty (`linkedDuty(Promise(p,q,content)) = ⊥`), evidence that the content holds fulfills the promise. This is the operational realization of `fulfilledEvidence`:

```
PromiseState(Promise(p,q,content), Σ) = Pending
linkedDuty(Promise(p,q,content)) = ⊥
contentHolds(content, Σ) = true
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
contentHolds(content, Σ) = false
deadlinePassed(content, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Promise(p,q,content)) →
    (Σ[PromiseState(Promise(p,q,content)) ↦ Violated],
     PromiseViolated(p,q,content))
```

Where `deadlinePassed(content, Σ)` checks for expiry of any temporal bound extracted from the promise content.

### Promise→Duty Generation (Remedial Generation Rule)

**Conceptual Foundation (Sein-Sollen vs Tun-Sollen)**:

- **Promise = Sein-Sollen (Ought-to-Be)**: A required state of the world (invariant)
- **Duty = Tun-Sollen (Ought-to-Do)**: An action to achieve or restore that state

When the world deviates from a Promise's invariant, the evaluator generates a remedial Duty (tracked as a `rl2p:Requirement`) to restore compliance.

**Generation Rule**:

When a Promise enters the `Violated` state, a remedial Requirement is generated:

```
PromiseState(Promise(p, q, content), Σ) = Violated
d = RemedialDuty(p, restoreAction(content), content.object)
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, PromiseViolated(p, q, content)) →
    (Σ[ObligationState(d) ↦ Active,
       Requirements ↦ Σ.Requirements ∪ {Requirement(d, Promise(p,q,content), q)}],
     RemedialDutyGenerated(d))
```

Where:
- `restoreAction(content)` is an abstract, implementation-defined function that maps the violated content to a remedial Action. (Note: The core semantics do not prescribe *how* this mapping occurs; implementations may use lookup tables, policy metadata, or manual intervention).
- The generated `Requirement` tracks `sourceNorm = Promise(p,q,content)` and `counterparty = q` (the promisee)
- The promisee `q` holds the correlative Claim

**Runtime Representation**:

The Protocol's `rl2p:Requirement` structure captures this:

```turtle
ex:remedialReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:dataQualityPromise ;  # The violated Promise
    rl2p:sourcePolicy ex:dataContract ;
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
    case e.eventType of
        ActionPerformed(a,x,s) → Σ[Performed(a,x,s) ↦ true]
        TimeAdvanced(t)        → Σ[Clock ↦ t]
        ApprovalGranted(...)   → Σ[Events ↦ Σ.Events ∪ {e}]
        MetadataChanged(s,k,v) → Σ[Metadata(s)[k] ↦ v]
        _                      → Σ[Events ↦ Σ.Events ∪ {e}]
```

### Privilege Activation

Privileges become active when their condition holds:

```
Env = mkEnv(R, Σ, Ctx)
matches(Privilege(a,x,s,c), R) = true
⟦ c ⟧(Env) = true
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
⟦ c ⟧(Env) = true
──────────────────────────────────────────────────────────────────
ProhibitionActive(a, x, s, c)
```

A prohibition is violated when the prohibited action is performed while active:

```
ProhibitionActive(a, x, s, c)
Σ.Performed(a, x, s) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Prohibition(a,x,s,c)) → (Σ, ProhibitionViolated(a, x, s, c))
```

---

## Normative Derivation (I/O-Logic Foundation)

RL2's evaluation follows an **I/O logic** pattern (Makinson & van der Torre): derivation produces a normative envelope, then conflict resolution yields a final decision.

### Pre-Resolution Normative Envelope

The function `Out` computes the **unresolved multiset** of normative atoms from a policy universe and environment:

```
Out : (PolicyUniverse U, Env) → NormativeAtoms*

Out(U, Env) =
    let applicablePolicies = ApplicablePolicies(U, Env)
    in ⋃ { deriveNorms(P, Env) | P ∈ applicablePolicies }

deriveNorms(P, Env) =
    { permit(a,x,s)    | Privilege(a,x,s,c) ∈ P.clauses, matches(_, R), ⟦c⟧(Env) = true } ∪
    { forbid(a,x,s)    | Prohibition(a,x,s,c) ∈ P.clauses, matches(_, R), ⟦c⟧(Env) = true } ∪
    { obligate(d)      | Duty d ∈ P.clauses, matches(d, R), ⟦d.condition⟧(Env) = true } ∪
    { violated(d)      | Duty d ∈ P.clauses, Σ.ObligationState(d) = Violated }
```

### Monotonicity of Derivation

The derivation function `Out` is **monotone** with respect to facts:

```
If Env ⊆ Env' (additional facts only), then Out(U, Env) ⊆ Out(U, Env')
```

Adding facts to the environment can only add normative conclusions, never remove them. This is the key I/O-logic property: **derivation is monotone; resolution is not**.
Phase ① avoids negation-as-failure and rule-level negation over derived facts; condition evaluation still allows data-level boolean/comparator predicates such as `rl2:neq` as ground terms.

### Derivation vs Resolution

| Property | Out (Derivation) | Eval (Full) |
|----------|------------------|-------------|
| Monotone | Yes | No |
| Deterministic | Yes | Yes |
| Conflict-handling | None (contradiction is data) | Strategy-based |
| Output | Multiset of atoms | Single decision |

The `Eval` function composes `Out` with state updates and conflict resolution:

```
Eval(U, R, Σ, Ctx) =
    let Env = mkEnv(R, Σ, Ctx)
    let envelope = Out(U, Env)                    -- ① Derivation (monotone)
    let Σ' = updateDutyStates(envelope, Env, Σ)   -- ② State transitions
    let decision = resolveDecision(envelope, Σ', strategy)  -- ③ Resolution (non-monotone)
    in (decision, Σ', duties(envelope))
```

The **normative envelope** `Out(U, Env)` is the first-class intermediate result — visible before resolution, available for audit, and formally monotone.

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

    -- Step 2: Evaluate conditions and determine active norms
    let activePrivileges = { p ∈ matchingPrivileges | ⟦p.condition⟧(Env) = true }
    let activeProhibitions = { p ∈ matchingProhibitions | ⟦p.condition⟧(Env) = true }

    -- Step 3: Update duty states
    let Σ' = updateDutyStates(matchingDuties, Env, Σ)
    let activeDuties = { d | Σ'.ObligationState(d) ∈ {Pending, Active} }
    let violatedDuties = { d | Σ'.ObligationState(d) = Violated }

    -- Step 4: Apply conflict resolution and compute decision
    let decision = resolveDecision(activePrivileges, activeProhibitions,
                                    activeDuties, violatedDuties, P.conflictStrategy)

    in (decision, Σ', activeDuties)
```

### Conflict Resolution

When multiple norms apply, conflicts must be resolved. RL2 provides two complementary mechanisms:

1. **Policy-level priority** (`rl2:priority`): Norms may declare an integer priority; higher values override lower. This is vocabulary defined in the ontology.

2. **Evaluator-level strategy**: The evaluator is configured with a conflict resolution strategy (e.g., prohibit-overrides, permit-overrides). This is **evaluator configuration**, not policy vocabulary—analogous to XACML combining algorithms.

The `strategy` parameter in `resolveDecision` below represents evaluator configuration. Policies express norms and priorities; evaluators decide how to combine conflicting results when priorities are equal.

More sophisticated defeasibility mechanisms—such as exclusionary rules—are available in frameworks like LegalRuleML [LegalRuleML] and may be incorporated in future RL2 profiles.

```
resolveDecision(privileges, prohibitions, activeDuties, violatedDuties, strategy) =
    case strategy of
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

baseDecision(privileges, activeDuties, violatedDuties) =
    if privileges = ∅ then NotApplicable
    else if violatedDuties ≠ ∅ then Deny  -- Violations block access
    else if activeDuties ≠ ∅ then PermitWithObligations
    else Permit
```

Note: `NotApplicable` (no matching rule) is distinct from `Deny` (explicit prohibition). This allows policy composition where a higher-level policy can provide defaults.

### Duty State Updates

The duty lifecycle is governed by three inference rules:

**Rule D-ACTIVATE** (Pending → Active):
```
Σ.ObligationState(d) = Pending
⟦d.condition⟧(Env) = true
─────────────────────────────────────────────────────────
Σ' = Σ[ObligationState(d) ↦ Active]
```

Activation is **condition-driven**: when the duty's condition first evaluates to true, the duty becomes active. This typically occurs when temporal preconditions are met (e.g., "after contract signing").

**Rule D-FULFILL** (Active → Fulfilled):
```
Σ.ObligationState(d) = Active
Σ.Performed(d.subject, d.action, d.object) = true
─────────────────────────────────────────────────────────
Σ' = Σ[ObligationState(d) ↦ Fulfilled,
       DutyPerformer(d) ↦ performer]
```

Fulfillment is **event-driven**: when `Performed` records show the required action was done, the duty is fulfilled. The performing agent is recorded for identity binding.

**Rule D-VIOLATE** (Active → Violated):
```
Σ.ObligationState(d) = Active
Σ.Performed(d.subject, d.action, d.object) = false
timeout(d.condition, Σ) = true
─────────────────────────────────────────────────────────
Σ' = Σ[ObligationState(d) ↦ Violated]
```

Violation is **time-driven**: when the deadline passes without fulfillment, the duty is violated.

**Algorithmic form** (for implementation):

```
updateDutyStates(duties, Env, Σ) =
    foldl(updateOneDuty(Env), Σ, duties)

updateOneDuty(Env)(Σ, d) =
    case Σ.ObligationState(d) of
        Pending → if ⟦d.condition⟧(Env) then Σ[ObligationState(d) ↦ Active] else Σ
        Active  → if Σ.Performed(d.subject, d.action, d.object)
                  then Σ[ObligationState(d) ↦ Fulfilled, DutyPerformer(d) ↦ performer]
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

**Note on Inheritance**: ODRL's `inheritFrom` mechanism is intentionally not supported in RL2. Policy inheritance introduces complexity (flattening, override semantics, auditability issues) without clear benefit over explicit composition. See **backlog.md** §Policy Inheritance.

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

### Structural Constraints

1. **Finite policy universe**: U is a finite set of policies
2. **Bounded condition nesting**: Conditions have bounded depth (recommended ≤ 20)
3. **Acyclic conditions**: No self-referential condition definitions
4. **Finite Σ**: State contains finite sets (Events, Performed, ObligationState)
5. **No recursive policy references**: Policies cannot invoke evaluation of other policies

### Path Resolution Constraints

6. **Bounded path depth**: Maximum 10 segments (enforced by grammar)
7. **No joins**: Path resolution is single-threaded navigation, not graph pattern matching
8. **No iteration**: `resolutionFunction` must be O(1) or O(log n) per invocation
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

**Extension warning**: Implementations using unbounded external queries via `resolutionFunction` or `lookupExternal` may exhibit non-polynomial or non-terminating behavior. Such extensions must document their complexity characteristics.

---

## Proof scope and normative artifact

RL2's formal guarantees are established by proving properties of the **reference evaluator written in WhyML and extracted to OCaml**. The extracted evaluator is the **normative realization** of RL2 semantics for implementation purposes. Proof obligations (S1–S6 and successors) apply to this evaluator and its extracted code, not to an open class of independent implementations.

---

## Mechanization

*This section is non-normative.*

RL2's semantics are explicitly designed for mechanization in Why3/WhyML, with the extracted OCaml evaluator as the endorsed runtime artifact. The abstract syntax maps cleanly to inductive datatypes, and the operational rules are syntax-directed.

## Target Platforms

| Platform | Strengths | Status |
|----------|-----------|--------|
| **Why3/WhyML + OCaml extraction** | Algebraic types, multiple backend provers (Alt-Ergo, Z3), extracted reference evaluator | Primary (normative) |
| **K Framework** | Executable semantics, automatic interpreter generation | Optional independent validation |
| **Lean 4** | Dependent types, code extraction, AI-assisted proofs | Optional independent validation |
| **Coq** | Mature ecosystem, CompCert precedent | Optional independent validation |

## Why3 Example

```why3
type agent
type action
type asset

type condition =
  | AtomicConstraint operand operator value
  | And condition condition
  | Or  condition condition
  | Not condition
  | Temporal time time
  | Context path operator value
  | Dynamic path

function eval_condition (c: condition) (env: env) : bool = ...
```

Transition rules are expressed as inductive predicates.

## Proof Obligations

The following properties should be proved for a verified implementation:

1. **(S1) Determinism**: Given Σ, R, Ctx, evaluation produces a unique result
2. **(S2) Progress**: Every well-typed expression either is a value or can step
3. **(S3) Preservation**: Types are preserved under transitions
4. **(S4) Duty-state consistency**: No duty can be both Fulfilled and Violated
5. **(S5) Timeout correctness**: Deadlines are eventually enforced
6. **(S6) Totality**: `Eval` terminates for all well-formed inputs

See **RL2_ResearchPlan.md** for the complete mechanization roadmap, phased implementation plan, and deliverable specifications.

For expressive characterization and comparison with other formalisms, see **RL2_Architecture.md**.

---

## References

See **RL2_References.md** for complete citations and glossary.

Related RL2 specifications:
- rl2.ttl — Core ontology (OWL)
- rl2-shacl.ttl — SHACL validation shapes
- RL2_Protocol.md — Runtime evaluation protocol
