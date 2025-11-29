# **RL2: A Unified Normative, Operational, and Semantic Framework for Rights and Data Policies**

**Formal Semantics Specification (Draft v0.2)**

*This is a self-contained, publishable specification describing the full formal semantics of RL2, written in a hybrid style combining mathematical rigor with explanatory narrative.*

---

# **Abstract**

RL2 is a normative and operational policy language designed as a rigorous successor to legacy rights languages, integrating deontic logic, promise theory, constraint algebra, and small-step operational semantics into a single, unified, formally grounded framework. This paper presents the full formal semantics of RL2, including abstract syntax, typing rules, semantic domains, denotational semantics for normative structures, a complete operational semantics for duties, promises, and state transitions, and a big-step policy interpretation function. The specification is designed for both human comprehension and mechanization (e.g., Why3/Lean), providing the foundation for verifiable policy-evaluation kernels.

---

# **Introduction**

Digital policy frameworks often lack formal normative foundations and operational rigor. Legacy standards like ODRL 2.2 provide expressive vocabularies but leave semantics to interpretation, leading to inconsistent enforcement.

RL2 (“Rights Language 2”) addresses these limitations by integrating ideas from:

* **Deontic Logic**
* **DPCL (normative meta-language)**
* **Promise Theory**
* **ODRE (operational rights enforcement)**
* **Temporal Logic and Event Calculi**

RL2 is fully RDF-compatible, but its semantics are defined **at the abstract syntax level**, independent of serialization.

This document gives a full formal semantics for RL2.

---

# **Design Goals and Guiding Principles**

RL2 semantics are designed to be:

1. **Precise**: Every construct has a clear formal meaning.
2. **Modular**: Norms, conditions, roles, and events are independent but composable.
3. **Mechanizable**: Designed to map directly into Why3, Lean, or Coq.
4. **Standalone**: RL2 semantics are self-contained and do not depend on external standards for definition.
5. **Operational**: Policies evolve in time through events and actions.
6. **Analytically useful**: Supports reasoning about obligations, compliance, and violations.

---

# **Abstract Syntax**

We define RL2’s abstract syntax using a typed algebraic grammar, enriched with commentary explaining intuition and use.

## **Core Syntactic Categories**

Let:

* **A** = set of agents
* **X** = set of actions
* **S** = set of assets
* **V** = set of values
* **T** = time domain
* **Env** = evaluation environment
* **Σ** = system state

We define RL2 expressions as:

### **Norms**

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

### **Promises**

```
Promise ::= Promise(Agent promiser, Agent promisee, PromiseContent)
```

where `PromiseContent ∈ {Action, Duty, Condition}` (matching the `rl2:PromiseContent` union class in the ontology).

### **Conditions**

```
Condition ::=
      Atom(leftOperand, operator, rightOperand)
    | And(Condition+)
    | Or(Condition+)
    | Xone(Condition+)
    | Not(Condition)
    | TemporalInterval(t_start, t_end)
    | Contextual(path, operator, value)
    | DynamicOperand(path)
    | EventConstraint(expectsEvent: Event)
    | Composite(requires: Condition+)
```

Notes:
- `And`, `Or`, and `Xone` take one or more conditions
- `Composite` models conditions that require other conditions to hold (using `rl2:requires` property chains)
- `EventConstraint` models approval requirements; holds when the expected event is present in Σ.Events
- `leftOperand` is drawn from profile-defined operands (RL2 Core defines the class `rl2:LeftOperand` but not instances)

### **Events and Transitions**

```
Event ::= event(eventType, payload)

Transition ::=
    Activate(Norm)
  | Fulfill(Duty)
  | Violate(Duty)
  | FulfillPromise(Promise)
  | Trigger(Event)
```

### **Policies**

```
Policy ::= Policy { clauses: Norm*, meta: Metadata }
```

---

# **Type System**

The type system ensures well-formed policies.

### **Typing Judgements**

We use:

```
Γ ⊢ e : τ
```

### **Types**

```
τ ::= Agent | Action | Asset | Condition | Time | Boolean | Norm | Promise | Event | State
```

### **Key Typing Rules**

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

# **Semantic Domains**

We define semantic domains to interpret expressions.

### **Agents**

```
⟦Agent⟧ ⊆ A
```

### **Actions**

```
⟦Action⟧ ⊆ X
```

### **States**

A state Σ contains:

* asset metadata
* event log
* action log
* temporal clock
* promise statuses
* duty states

Formally:

```
Σ = (Clock : T,
     Events : E*,
     Performed : A × X × S → Boolean,
     Metadata : S → Map,
     PromiseState : Promise → {Pending, Fulfilled, Violated},
     ObligationState : Duty → {Pending, Active, Fulfilled, Violated})
```

Note: `ObligationState` is the canonical name (matching `rl2:ObligationState` in the ontology).

**Scope of Σ**: In practice, Σ represents the *evidence log* or *relevant history* for a given evaluation context—not a theoretically omniscient record of all actions ever performed. Implementations scope Σ to the Case being evaluated (see RL2_Protocol.md), tracking only events and actions relevant to that access request's lifecycle.

### **Environments**

```
Env = Agent × Asset × State × ExternalContext
```

Used for evaluating operand paths.

---

# **Denotational Semantics**

Denotational semantics gives timeless meaning to norms and conditions.

We write:

```
⟦ e ⟧ : Env → Value
```

## **Conditions**

Atomic constraints:

```
⟦ Atom(op, operator, value) ⟧(Env) =
     true  if apply(operator, resolve(op, Env), value)
     false otherwise
```

Logical conditions:

```
⟦ And(c1, c2)  ⟧(Env) = ⟦c1⟧(Env) ∧ ⟦c2⟧(Env)
⟦ Or(c1, c2)   ⟧(Env) = ⟦c1⟧(Env) ∨ ⟦c2⟧(Env)
⟦ Not(c)       ⟧(Env) = ¬⟦c⟧(Env)
⟦ Xone(c1..cn) ⟧(Env) = exactly one of ⟦c1⟧(Env)..⟦cn⟧(Env) is true
```

Temporal:

```
⟦ TemporalInterval(start,end) ⟧(Env) =
    true if start ≤ Env.Σ.Clock ≤ end
```

Contextual:

```
⟦ Contextual(path, op, v) ⟧(Env) =
    true if apply(op, deref(path, Env), v)
```

Dynamic operand:

```
⟦ DynamicOperand(path) ⟧(Env) = deref(path, Env)
```

Event constraint (approval requirement):

```
⟦ EventConstraint(expectsEvent) ⟧(Env) =
    true  if ∃e ∈ Env.Σ.Events : matches(e, expectsEvent)
    false otherwise
```

Composite condition (condition requiring other conditions):

```
⟦ Composite(requires: c1..cn) ⟧(Env) =
    true  if ∀i ∈ 1..n : ⟦ci⟧(Env) = true
    false otherwise
```

Composite conditions model transitive requirements where one condition depends on others (e.g., a promise condition requiring that subordinate conditions are met).

---

## **Helper Function Specifications**

The condition semantics rely on several helper functions. For a verified kernel, these must be precisely specified.

### **resolve : LeftOperand × Env → Value**

The function `resolve(leftOperand, Env)` maps a left operand to a value:

```
resolve : LeftOperand × Env → Value ∪ {⊥}

resolve(op, Env) =
    case op of
        dateTime    → Env.Σ.Clock
        agent       → Env.Agent
        asset       → Env.Asset
        profile(p)  → lookupProfile(p, op, Env)
        _           → lookupExternal(op, Env.Context)
```

Where:
* `lookupProfile(p, op, Env)` resolves operands defined by profile `p`
* `lookupExternal(op, Ctx)` resolves operands from external context (HR systems, directories, etc.)
* `⊥` indicates undefined (evaluation fails if encountered)

RL2 Core does not define specific left operands; these are provided by profiles. The resolution mechanism is intentionally delegated to implementations.

Profiles may define left operands such as:
* `purpose` → resolved from request context
* `dateTime` → resolved from Env.Σ.Clock
* `recipient` → resolved from agent metadata
* `department` → resolved via external lookup (e.g., HR system)

### **deref : Path × Env → Value**

The function `deref(path, Env)` traverses a path expression to retrieve a value:

```
deref : Path × Env → Value ∪ {⊥}

deref(path, Env) =
    let segments = split(path, '.')
    let root = case head(segments) of
        "agent"   → Env.Agent
        "asset"   → Env.Asset
        "context" → Env.Context
        "state"   → Env.Σ
        _         → ⊥
    in foldl(navigate, root, tail(segments))

navigate(obj, segment) =
    case obj of
        ⊥       → ⊥
        Record  → obj.segment if segment ∈ fields(obj) else ⊥
        Map     → obj[segment] if segment ∈ keys(obj) else ⊥
        _       → ⊥
```

Example paths:
* `agent.department` → the agent's department
* `asset.classification` → the asset's classification level
* `context.purpose` → the declared purpose from request context
* `state.Clock` → current system time

### **matches : Event × EventPattern → Boolean**

The function `matches(e, pattern)` checks if an event matches an expected pattern:

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

### **contentHolds : PromiseContent × State → Boolean**

The function `contentHolds(content, Σ)` checks if promise content is satisfied:

```
contentHolds : PromiseContent × State → Boolean

contentHolds(content, Σ) =
    case content of
        Action(a, x, s)  → Σ.Performed(a, x, s)
        Duty(d)          → Σ.ObligationState(d) = Fulfilled
        Condition(c)     → ⟦c⟧(mkEnv(nullRequest, Σ, emptyContext))
```

### **timeout : Condition → Boolean**

The function `timeout(c)` checks if a temporal deadline has passed:

```
timeout : Condition × State → Boolean

timeout(c, Σ) =
    case extractDeadline(c) of
        None      → false
        Some(t)   → Σ.Clock > t

extractDeadline(c) =
    case c of
        TemporalInterval(_, end)  → Some(end)
        And(c1, c2)               → min(extractDeadline(c1), extractDeadline(c2))
        Or(c1, c2)                → max(extractDeadline(c1), extractDeadline(c2))
        _                         → None
```

### **apply : Operator × Value × Value → Boolean**

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

# **Denotational Semantics for Norms**

Norms are evaluated in the context of a **Request** `R = (a_req, x_req, s_req)` specifying the requesting agent, requested action, and target asset. The denotation takes both the request and an environment constructed from it.

## **Environment Construction**

Given a Request `R = (a_req, x_req, s_req)`, state `Σ`, and external context `Ctx`:

```
mkEnv(R, Σ, Ctx) = (a_req, s_req, Σ, Ctx)
```

The environment `Env = (Agent, Asset, State, ExternalContext)` provides the evaluation context for conditions.

## **Request Matching**

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

## **Norm Denotations**

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

## **Hohfeldian Correlatives and Opposites**

RL2 supports the full Hohfeldian framework. The correlatives are:

| Right-holder has | Duty-bearer has |
|------------------|-----------------|
| Privilege | No-Claim |
| Claim | Duty |
| Power | Liability |
| Immunity | Disability |

## **Claim Denotation**

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

## **Power Denotation**

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

## **Liability Denotation**

A Liability is the correlative of a Power — the susceptibility to have one's normative position altered:

```
⟦Liability(a, n)⟧(Env) =
    LiabilityActive(a, n)   if ∃ Power(h, n) where subject(n) = a
    LiabilityInactive       otherwise
```

When a Power is exercised, the Liability-holder's position changes accordingly.

## **Immunity Denotation**

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

## **Sanctions and Remedies**

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

# **Operational Semantics (Small-Step)**

Operational semantics define **how states and obligations evolve over time**.

## **Judgement Form**

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

## **State Update Notation**

We use the notation `Σ[f ↦ v]` to denote state update:

```
Σ[ObligationState(d) ↦ Active] =
    (Σ.Clock, Σ.Events, Σ.Performed, Σ.Metadata,
     Σ.PromiseState, Σ.ObligationState[d ↦ Active])
```

## **Duty Activation**

A pending duty becomes active when its activation condition holds:

```
Env = mkEnv(R, Σ, Ctx)
⟦ c ⟧(Env) = true
Σ.ObligationState(Duty(a,x,s,c)) = Pending
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Duty(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Active], DutyActive(a,x,s,c))
```

## **Duty Fulfillment**

An active duty is fulfilled when the required action is performed:

```
Σ.ObligationState(Duty(a,x,s,c)) = Active
Σ.Performed(a,x,s) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Fulfilled], DutyFulfilled(a,x,s,c))
```

## **Duty Violation**

An active duty is violated when its deadline passes without fulfillment:

```
Env = mkEnv(R, Σ, Ctx)
Σ.ObligationState(Duty(a,x,s,c)) = Active
Σ.Performed(a,x,s) = false
timeout(c, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, DutyActive(a,x,s,c)) → (Σ[ObligationState(Duty(a,x,s,c)) ↦ Violated], DutyViolated(a,x,s,c))
```

## **Promise Fulfillment**

A pending promise is fulfilled when its content holds:

```
Σ.PromiseState(Promise(p,q,content)) = Pending
contentHolds(content, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Promise(p,q,content)) → (Σ[PromiseState(Promise(p,q,content)) ↦ Fulfilled], PromiseFulfilled(p,q,content))
```

## **Promise Violation**

A pending promise is violated when its deadline expires without fulfillment:

```
Σ.PromiseState(Promise(p,q,content)) = Pending
contentHolds(content, Σ) = false
deadline(content, Σ) = true
──────────────────────────────────────────────────────────────────
(Σ, R, Ctx, Promise(p,q,content)) → (Σ[PromiseState(Promise(p,q,content)) ↦ Violated], PromiseViolated(p,q,content))
```

Where `deadline(content, Σ)` extracts and checks temporal bounds from the promise content.

## **Event Processing**

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

## **Privilege Activation**

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

## **Prohibition Activation**

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

# **Big-Step Semantics (Policy Evaluation)**

## **Evaluation Function Signature**

The total decision function takes a Request as a first-class parameter:

```
Eval : (Policy P, Request R, State Σ, Context Ctx) → (Decision, State, DutySet)
```

Where:
* `P` is the policy being evaluated
* `R = (a_req, x_req, s_req)` is the request (agent, action, asset)
* `Σ` is the current system state
* `Ctx` is the external context (assertions from Protocol's ContextAssertion)
* `Decision ∈ {Permit, Deny, PermitWithObligations, NotApplicable, Indeterminate}`
* The returned `State` reflects any state updates from evaluation
* `DutySet` contains duties in Pending or Active state requiring fulfillment

## **Evaluation Algorithm**

```
Eval(P, R, Σ, Ctx) =
    let Env = mkEnv(R, Σ, Ctx)

    -- Step 1: Find matching norms
    let matchingPrivileges = { p ∈ P.clauses | p : Privilege ∧ matches(p, R) }
    let matchingProhibitions = { p ∈ P.clauses | p : Prohibition ∧ matches(p, R) }
    let matchingDuties = { d ∈ P.clauses | d : Duty ∧ matches(d, R) }

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

## **Conflict Resolution**

When multiple norms apply, conflicts must be resolved. RL2 supports configurable conflict strategies:

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

## **Duty State Updates**

```
updateDutyStates(duties, Env, Σ) =
    foldl(updateOneDuty(Env), Σ, duties)

updateOneDuty(Env)(Σ, d) =
    let currentState = Σ.ObligationState(d)
    in case currentState of
        Pending →
            if ⟦d.condition⟧(Env) then Σ[ObligationState(d) ↦ Active]
            else Σ
        Active →
            if Σ.Performed(d.subject, d.action, d.object) then
                Σ[ObligationState(d) ↦ Fulfilled]
            else if timeout(d.condition, Σ) then
                Σ[ObligationState(d) ↦ Violated]
            else Σ
        _ → Σ  -- Fulfilled/Violated are terminal states
```

## **PermitWithObligations Semantics**

When `Eval` returns `PermitWithObligations`:
* Access is conditionally granted
* The returned `DutySet` contains duties that must be fulfilled
* Duties may be in `Pending` (activation condition not yet met) or `Active` (must be performed)
* The Protocol's DutyRequirement captures these for tracking

This allows pre-access duties (must fulfill before action) and post-access duties (must fulfill after action) to be distinguished by their conditions.

## **Note on Evaluation Complexity**

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

# **Constraint Algebra Semantics**

Constraints form a Boolean algebra with additional temporal operators.

Properties:

* Associativity, commutativity, idempotence for And/Or
* De Morgan laws
* Temporal and contextual constraints orthogonal to logical structure
* Dynamic operands resolved at evaluation time
* Path-based evaluation is deterministic (fully resolved from Env)

This ensures determinism of constraint evaluation.

---

# **Event Semantics**

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

# **Role Resolution Semantics**

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

# **Policy Composition and Inheritance Semantics**

Policies can be composed:

```
P1 ⊔ P2 = union of clauses
```

Inheritance is resolved via SHACL rules and override semantics.

Conflict resolution reduces to condition calculus:

* if two norms conflict, policy-level or clause-level precedence applies
* RL2 supports ODRL conflict semantics via condition ordering

---

# **Interoperability and Compilation**

While RL2 is a standalone language, it is designed to be a valid target for compilation from other policy languages.

We define a compilation function `C` such that for a legacy policy `P_legacy`:

```
C(P_legacy) → P_RL2
```

Where `P_RL2` is a semantically precise RL2 representation of the intent of `P_legacy`. This allows RL2 kernels to execute policies authored in ambiguous standards by first compiling them into RL2's rigorous operational structures.

---

# **Relationship to RL2 Protocol**

The RL2 Protocol (RL2_Protocol.md) defines runtime artifacts for policy evaluation:

- **Request** → corresponds to initiating evaluation with a specific action, asset, and agent
- **ContextAssertion** → provides values for left operand resolution during evaluation
- **EvaluationResult** → the output of `Eval(Policy, Σ, E)`
- **DutyRequirement** → duties in `Active` or `Pending` state after evaluation
- **Case** → tracks the evolution of Σ over multiple evaluation cycles

The formal semantics define *what* evaluation means; the Protocol defines *how* to exchange evaluation inputs and outputs between systems.

Key correspondence:

| Semantics Concept | Protocol Artifact |
|-------------------|-------------------|
| Request R = (a, x, s) | rl2p:Request (requestingAgent, requestedAction, requestedAsset) |
| Env (environment) | Request + ContextAssertions |
| Σ (state) | Case history |
| Σ.ObligationState | rl2p:DutyStatus (Pending, Active, Fulfilled, Violated) |
| Σ.PromiseState | (Future: rl2p:PromiseStatus) |
| Decision | EvaluationResult.decision |
| Active duties | EvaluationResult.activeDuties |
| Events | ContextAssertions (including fulfillment) |
| mkEnv(R, Σ, Ctx) | Evaluator constructs from Request + Context |

---

# **Discussion**

The RL2 semantics unify normative logic, temporal logic, event calculus, and promise theory in a way that:

* remains RDF-compatible
* supports mechanization
* covers ODRL 3.0’s anticipated scope
* can be implemented in a verified kernel
* is expressive enough for enterprise data-governance policies

RL2 provides, for the first time, a rigorous semantic foundation capable of supporting large-scale, automated reasoning over data policies and contracts.

---

# **Future Mechanization in Why3**

The abstract syntax maps cleanly to Why3 datatypes.

Example:

```why3
type agent
type action
type asset

type condition =
  | Atom operand operator value
  | And condition condition
  | Or  condition condition
  | Not condition
  | Temporal time time
  | Context path operator value
  | Dynamic path
```

Evaluation becomes:

```why3
function eval_condition (c: condition) (env: env) : bool = ...
```

Transition rules expressed as inductive predicates.

This allows proofs of:

* determinism
* termination (modulo time progression)
* preservation
* monotonicity of constraints

---

# **Conclusion**

This document provides the first complete formal semantics for RL2, defining abstract syntax, types, semantic domains, denotational and operational semantics, event and temporal semantics, role resolution, constraint algebra, and policy evaluation.

---

# **References**

See **RL2_References.md** for complete citations and glossary.

Related RL2 specifications:
- RL2_Core.md — Ontology and SHACL shapes
- RL2_Protocol.md — Runtime evaluation protocol
