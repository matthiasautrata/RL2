# RL2 Critical Fixes

**Date:** 2025-01-05
**Target:** RL2 Core Ontology and Semantics

---

## Permission-Bound Duties (CRITICAL - ODRL Compatibility)

### Problem

ODRL duties can have actions different from the permitted action (e.g., permit `display` if duty `pay` is fulfilled). RL2 semantics currently only activate duties whose `action` matches the request, so duties with different actions never apply.

**Technical Analysis:**
* `matches(Norm(a,x,s,c), R)` at RL2_Semantics.md:505-512 requires action equality: `(x = x_req ∨ x_req ⊑ x)`
* Duty denotation at RL2_Semantics.md:540-542 uses `matches(Duty(a,x,s,c), R)` to determine activation
* Evaluation algorithm at RL2_Semantics.md:888 filters: `matchingDuties = { d ∈ P.clauses | ... ∧ matches(d, R) }`
* Result: A duty with `action=pay` attached to privilege with `action=display` is dropped on a `display` request

**ODRL Example That Fails:**
```turtle
:offer1 a odrl:Offer ;
    odrl:permission [
        odrl:action odrl:display ;
        odrl:target :photo123 ;
        odrl:duty [
            odrl:action odrl:pay ;
            odrl:constraint [ odrl:payAmount 5.00 ]
        ]
    ] .
```

Expected: `PermitWithObligations` with payment duty
Actual (RL2): `Permit` (duty not surfaced because `pay ≠ display`)

### Approved Solution: Unified State Approach (Alternative 1)

**Rationale:**

Rather than introducing a new `DutyConstraint` class with a "magic" `SubjectScope` enum, we leverage RL2's existing `AtomicConstraint` machinery. Duty state becomes just another queryable property of the world, like `dateTime` or `fileSize`.

**Key Insight:** Identity binding should be an **explicit logical proposition** (`performer = currentAgent`), not a configuration flag hidden in an enum.

**Architectural Principle:**
```
ObligationState and DutyPerformer are properties of Σ (world state)
    ↓
AtomicConstraint can query any property of Σ via LeftOperands
    ↓
Therefore: Duty state checks are just AtomicConstraints with norm-targeted operands
```

**What We Add:**

| Addition | Type | Purpose |
|----------|------|---------|
| `rl2:targetNorm` | Property | Specifies which norm to query in a constraint |
| `rl2:obligationState` | LeftOperand | Queries `Σ.ObligationState(n)` |
| `rl2:dutyPerformer` | LeftOperand | Queries `Σ.DutyPerformer(n)` |
| `rl2:currentAgent` | DynamicReference | Resolves to `Env.Agent` at evaluation time |
| `DutyPerformer` | Σ Component | Tracks who fulfilled each duty |

**What We Do NOT Add:**
- ~~`rl2:DutyConstraint` class~~
- ~~`rl2:SubjectScope` enumeration~~
- ~~`rl2:SameSubject`, `rl2:AnySubject`, `rl2:DifferentSubject`~~
- ~~`rl2:subjectScope` property~~
- ~~`rl2:requiresDuty`, `rl2:requiredState` properties~~

**Benefits of This Approach:**

1. **De-Magicing:** Identity binding is an explicit `eq`/`neq` constraint, not hidden enum interpretation
2. **Regularity:** Norm state is just another queryable property of the world
3. **Parsimony:** No new classes or enumerations
4. **Expressiveness:** Supports patterns impossible with SubjectScope:
   - SameSubject → `dutyPerformer = currentAgent`
   - AnySubject → (no performer check)
   - DifferentSubject → `dutyPerformer ≠ currentAgent`
   - SpecificAgent → `dutyPerformer = ex:Bob`
5. **Decidability:** All logic is explicit in the policy graph, enabling static analysis

### Deontic Logic Foundation

This approach operationalizes the classical distinction from normative philosophy:

| German | English | RL2 Implementation |
|--------|---------|-------------------|
| *Tun-sollen* | Ought-to-do (personal) | `obligationState = Fulfilled` AND `dutyPerformer = currentAgent` |
| *Sein-sollen* | Ought-to-be (impersonal) | `obligationState = Fulfilled` (only) |

### Semantic Patterns

#### Pattern 1: Sein-sollen (Team License / AnySubject equivalent)

"The duty must be fulfilled, by anyone."

```turtle
[ a rl2:AtomicConstraint ;
  rl2:targetNorm ex:paymentDuty ;
  rl2:leftOperand rl2:obligationState ;
  rl2:constraintOperator rl2:eq ;
  rl2:rightOperand rl2:Fulfilled ] .
```

#### Pattern 2: Tun-sollen (Pay-to-Play / SameSubject equivalent)

"The duty must be fulfilled, by me."

```turtle
[ a rl2:LogicalConstraint ;
  rl2:constraintOperator rl2:and ;
  rl2:operand [
      a rl2:AtomicConstraint ;
      rl2:targetNorm ex:paymentDuty ;
      rl2:leftOperand rl2:obligationState ;
      rl2:constraintOperator rl2:eq ;
      rl2:rightOperand rl2:Fulfilled
  ] ;
  rl2:operand [
      a rl2:AtomicConstraint ;
      rl2:targetNorm ex:paymentDuty ;
      rl2:leftOperand rl2:dutyPerformer ;
      rl2:constraintOperator rl2:eq ;
      rl2:rightOperandRef rl2:currentAgent
  ] ] .
```

#### Pattern 3: Separation of Duty (Two-Man Rule / DifferentSubject equivalent)

"The duty must be fulfilled, by someone other than me."

```turtle
[ a rl2:LogicalConstraint ;
  rl2:constraintOperator rl2:and ;
  rl2:operand [
      a rl2:AtomicConstraint ;
      rl2:targetNorm ex:preparationDuty ;
      rl2:leftOperand rl2:obligationState ;
      rl2:constraintOperator rl2:eq ;
      rl2:rightOperand rl2:Fulfilled
  ] ;
  rl2:operand [
      a rl2:AtomicConstraint ;
      rl2:targetNorm ex:preparationDuty ;
      rl2:leftOperand rl2:dutyPerformer ;
      rl2:constraintOperator rl2:neq ;          # NOT EQUAL
      rl2:rightOperandRef rl2:currentAgent
  ] ] .
```

#### Pattern 4: Specific Agent

"The duty must be fulfilled by Bob specifically."

```turtle
[ a rl2:LogicalConstraint ;
  rl2:constraintOperator rl2:and ;
  rl2:operand [
      a rl2:AtomicConstraint ;
      rl2:targetNorm ex:approvalDuty ;
      rl2:leftOperand rl2:obligationState ;
      rl2:constraintOperator rl2:eq ;
      rl2:rightOperand rl2:Fulfilled
  ] ;
  rl2:operand [
      a rl2:AtomicConstraint ;
      rl2:targetNorm ex:approvalDuty ;
      rl2:leftOperand rl2:dutyPerformer ;
      rl2:constraintOperator rl2:eq ;
      rl2:rightOperandRef ex:Bob               # Specific agent
  ] ] .
```

### The Verbosity Trade-off

The explicit approach is more verbose (3 objects vs. 1 hypothetical DutyConstraint), but:

- Every piece of logic is explicit in the graph
- No hidden evaluator semantics interpreting "what SameSubject means"
- Formally decidable by static analysis
- This is the correct trade-off for a rigorous normative language

### Required Changes

#### 1. Ontology (rl2.ttl)

Add to Section 4 (Conditions):

```turtle
# Norm-targeting for state queries
rl2:targetNorm a owl:ObjectProperty ;
    rdfs:domain rl2:AtomicConstraint ;
    rdfs:range rl2:Norm ;
    rdfs:label "Target Norm" ;
    rdfs:comment "Specifies the norm whose state is being queried. Used with obligationState or dutyPerformer left operands." .

# Left operands for norm state queries
rl2:obligationState a rl2:LeftOperand ;
    rdfs:label "Obligation State" ;
    rdfs:comment "Queries the ObligationState of the target norm from Σ. Returns Pending, Active, Fulfilled, or Violated." .

rl2:dutyPerformer a rl2:LeftOperand ;
    rdfs:label "Duty Performer" ;
    rdfs:comment "Queries the agent who fulfilled the target duty from Σ. Returns an Agent or ⊥ if not fulfilled." .

# Dynamic reference for current agent
rl2:currentAgent a rl2:DynamicOperandReference ;
    rdfs:label "Current Agent" ;
    rdfs:comment "Resolves to Env.Agent (the agent making the current request) at evaluation time." .

# Priority for conflict resolution
rl2:priority a owl:DatatypeProperty ;
    rdfs:domain rl2:Norm ;
    rdfs:range xsd:integer ;
    rdfs:comment "Numeric priority for conflict resolution; higher values override lower values." .
```

#### 2. Semantic Domain (RL2_Semantics.md)

Update Σ definition to track duty performers:

```text
Σ = (Clock : T,
     Events : E*,
     Performed : A × X × S → Boolean,
     Metadata : S → Map,
     PromiseState : Promise → {Pending, Fulfilled, Violated},
     ObligationState : Duty → {Pending, Active, Fulfilled, Violated},
     DutyPerformer : Duty → Agent ∪ {⊥})  -- NEW
```

#### 3. resolve() Function (RL2_Semantics.md)

Extend to handle norm-targeted operands:

```text
resolve : LeftOperand × Env × Norm? → Value ∪ {⊥}

resolve(op, Env, targetNorm) =
    case op of
        obligationState →
            if targetNorm ≠ ⊥ then Env.Σ.ObligationState(targetNorm)
            else ⊥
        dutyPerformer →
            if targetNorm ≠ ⊥ then Env.Σ.DutyPerformer(targetNorm)
            else ⊥
        dateTime → Env.Σ.Clock
        agent → Env.Agent
        ...
```

#### 4. AtomicConstraint Semantics (RL2_Semantics.md)

Update to pass targetNorm:

```text
⟦ Atom(op, operator, value, targetNorm?) ⟧(Env) =
    let leftVal = resolve(op, Env, targetNorm)
    in apply(operator, leftVal, value)
```

#### 5. Duty Fulfillment Transition (RL2_Semantics.md)

Record performer on fulfillment:

```text
(Σ, R, Ctx, DutyActive(a,x,s,c)) →
    (Σ[ObligationState(d) ↦ Fulfilled, DutyPerformer(d) ↦ R.agent], DutyFulfilled(...))
```

#### 6. Protocol (rl2p.ttl)

Add performer tracking to ContextAssertion:

```turtle
rl2p:performer a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:range rl2:Agent ;
    rdfs:comment """The agent who performed the action that this assertion records.
    Distinct from rl2p:assertedBy (the system reporting it).
    Used to populate Σ.DutyPerformer for identity checks.""" .
```

#### 7. ODRL Transformation Rules

```text
IF duty is nested in odrl:permission:
    1. Create rl2:Duty as standalone clause (with URI for referenceability)
    2. Add LogicalConstraint to permission's rl2:condition:
       - AtomicConstraint checking obligationState = Fulfilled
       - AtomicConstraint checking dutyPerformer = currentAgent (ODRL implies SameSubject)
    3. Combine with rl2:and
```

---

## Other ODRL Compatibility Issues

### Inheritance (`odrl:inheritFrom`)

RL2 explicitly excludes runtime inheritance, requiring a pre-processing/flattening step. While semantically equivalent results can be achieved, it is not a syntactic superset.

**Recommendation:** Explicitly document the transformation required for `inheritFrom` in ODRL mapping documentation.

### Conflict Strategies (`odrl:conflict`)

ODRL allows policies to specify their conflict resolution strategy (e.g., `perm:perm`, `prohibit:perm`). RL2 relies on numeric priorities and compilation-time resolution.

**Recommendation:** Document how ODRL conflict strategies map to RL2 priority-based resolution in ODRL coverage documentation.

### Policy Request Type

ODRL defines `odrl:Request` as a policy class. `rl2.ttl` lacks a policy-level Request; `rl2p.ttl` introduces a runtime `rl2p:Request` (evaluation artifact, not a policy container).

**Recommendation:** Add `rl2:Request` policy subclass or document mapping for `odrl:Request` policies.

---

## Documentation Claim Refinement

The claim in `RL2_ODRL_Coverage.md` that "RL2 is a strict superset of ODRL" should be softened to **"Semantic Superset"** or **"Expressive Superset"** to acknowledge that transformation/compilation is required for certain ODRL features (inheritance, permission-bound duties with different actions).

---

## Documentation Synchronization Required

After implementing the ontology and semantics changes above, the following documentation must be updated:

* **RL2_Vocabulary.md** - Add `rl2:targetNorm`, `rl2:obligationState`, `rl2:dutyPerformer`, `rl2:currentAgent`, `rl2:priority` with full descriptions and examples
* **RL2_Core.md** - Update examples to show duty state constraints
* **RL2_ODRL_Coverage.md** - Update duty mapping table; add ODRL→RL2 transformation rules for nested duties
* **RL2_Primer.md** - Add section on duty state preconditions with patterns
* **RL2_Protocol.md** - Document `rl2p:performer` semantics
* **usecases/*.md** - Update all examples to use explicit constraint patterns
