# Duty State Constraint Implementation Plan

**Date:** 2025-01-05
**Feature:** Norm State Querying via Atomic Constraints
**Approach:** Alternative 1 - Unified State (No New Constraint Class)

---

## Overview

This plan implements duty state checking using RL2's existing `AtomicConstraint` machinery rather than introducing a new `DutyConstraint` class. This approach:

1. **Reuses existing constructs** - `AtomicConstraint`, `LogicalConstraint`
2. **Makes logic explicit** - Identity binding is expressed as `eq`/`neq` constraints
3. **Is more expressive** - Supports SameSubject, AnySubject, DifferentSubject, AND specific agents
4. **Maintains semantic rigor** - No hidden "magic" in the evaluator

### Key Additions

| Addition | Type | Purpose |
|----------|------|---------|
| `rl2:targetNorm` | Property | Specifies which norm to query in a constraint |
| `rl2:obligationState` | LeftOperand | Queries `Σ.ObligationState(n)` |
| `rl2:dutyPerformer` | LeftOperand | Queries `Σ.DutyPerformer(n)` |
| `rl2:currentAgent` | DynamicReference | Resolves to `Env.Agent` at evaluation time |
| `DutyPerformer` | Σ Component | Tracks who fulfilled each duty |
| `rl2p:performer` | Protocol Property | Records performer in ContextAssertion |

### What We Are NOT Adding

- ~~`rl2:DutyConstraint` class~~
- ~~`rl2:SubjectScope` enumeration~~
- ~~`rl2:SameSubject`, `rl2:AnySubject`, `rl2:DifferentSubject`~~
- ~~`rl2:subjectScope` property~~
- ~~`rl2:requiresDuty`, `rl2:requiredState` properties~~

---

## Semantic Patterns

### Pattern 1: Sein-sollen (AnySubject equivalent)

"The duty must be fulfilled, by anyone."

```turtle
[ a rl2:AtomicConstraint ;
  rl2:targetNorm ex:paymentDuty ;
  rl2:leftOperand rl2:obligationState ;
  rl2:constraintOperator rl2:eq ;
  rl2:rightOperand rl2:Fulfilled ] .
```

### Pattern 2: Tun-sollen (SameSubject equivalent)

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

### Pattern 3: Separation of Duty (DifferentSubject equivalent)

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

### Pattern 4: Specific Agent

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

---

## Implementation Checklist

### Phase 1: Ontology (rl2.ttl)

- [ ] Add `rl2:targetNorm` property (domain: AtomicConstraint, range: Norm)
- [ ] Add `rl2:obligationState` as LeftOperand instance
- [ ] Add `rl2:dutyPerformer` as LeftOperand instance
- [ ] Add `rl2:currentAgent` as DynamicReference instance
- [ ] Add `rl2:priority` property on Norm (for conflict resolution)
- [ ] Update ontology version to 0.4

**Location in file:** Section 4 (Conditions), add to LeftOperand definitions

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

**Dependencies:** None

### Phase 2: SHACL (rl2-shacl.ttl)

- [ ] Update `AtomicConstraintShape` to allow `rl2:targetNorm`
- [ ] Add validation: when `leftOperand` is `obligationState` or `dutyPerformer`, `targetNorm` is required

```turtle
# Conditional requirement: targetNorm needed for norm state operands
rl2:NormStateConstraintShape a sh:NodeShape ;
    sh:target [
        a sh:SPARQLTarget ;
        sh:select """
            PREFIX rl2: <https://rl2.example/ontology#>
            SELECT ?this WHERE {
                ?this a rl2:AtomicConstraint ;
                      rl2:leftOperand ?op .
                FILTER(?op IN (rl2:obligationState, rl2:dutyPerformer))
            }
        """
    ] ;
    sh:property [
        sh:path rl2:targetNorm ;
        sh:minCount 1 ;
        sh:class rl2:Norm ;
        sh:message "AtomicConstraint with obligationState or dutyPerformer operand must specify targetNorm"
    ] .
```

**Dependencies:** Phase 1 complete

### Phase 3: Formal Semantics (RL2_Semantics.md) - CRITICAL

#### Phase 3a: State Memory (Σ Definition Update)

- [ ] Update Σ definition (~line 235) to add `DutyPerformer` map:

```text
Σ = (Clock : T,
     Events : E*,
     Performed : A × X × S → Boolean,
     Metadata : S → Map,
     PromiseState : Promise → {Pending, Fulfilled, Violated},
     ObligationState : Duty → {Pending, Active, Fulfilled, Violated},
     DutyPerformer : Duty → Agent ∪ {⊥})  -- NEW: tracks WHO fulfilled
```

- [ ] Update Duty Fulfillment transition rule to record performer:

```text
(Σ, R, Ctx, DutyActive(a,x,s,c)) →
    (Σ[ObligationState(d) ↦ Fulfilled, DutyPerformer(d) ↦ R.agent], DutyFulfilled(...))
```

#### Phase 3b: resolve() Function Update

- [ ] Extend the `resolve` function to handle norm-targeted operands:

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

#### Phase 3c: AtomicConstraint Evaluation Update

- [ ] Update AtomicConstraint semantics to pass targetNorm:

```text
⟦ Atom(op, operator, value, targetNorm?) ⟧(Env) =
    let leftVal = resolve(op, Env, targetNorm)
    in apply(operator, leftVal, value)
```

#### Phase 3d: DynamicReference Resolution

- [ ] Add resolution for `currentAgent`:

```text
⟦ currentAgent ⟧(Env) = Env.Agent
```

- [ ] Update version to 0.4

**Dependencies:** Phase 1 complete

### Phase 4: Protocol Ontology (rl2p.ttl)

- [ ] Add `rl2p:performer` property to ContextAssertion:

```turtle
rl2p:performer a owl:ObjectProperty ;
    rdfs:domain rl2p:ContextAssertion ;
    rdfs:range rl2:Agent ;
    rdfs:comment """The agent who performed the action that this assertion records.
    Distinct from rl2p:assertedBy (the system reporting it).
    Used to populate Σ.DutyPerformer for identity checks.""" .
```

- [ ] Update ontology version to 0.4

**Location in file:** Section 5 (Context Assertions), after existing properties (~line 209)

**Dependencies:** Phase 1 complete

### Phase 5: Protocol SHACL (rl2p-shacl.ttl)

- [ ] Update `ContextAssertionShape` to validate `performer` property
- [ ] Add: when `contextProperty = rl2p:dutyFulfilled`, `performer` should be present

**Dependencies:** Phase 4 complete

### Phase 6: Vocabulary Reference (RL2_Vocabulary.md)

- [ ] Add `rl2:targetNorm` property to Property Reference
- [ ] Add `rl2:obligationState` to LeftOperand instances (Section 7)
- [ ] Add `rl2:dutyPerformer` to LeftOperand instances
- [ ] Add `rl2:currentAgent` to DynamicReference section
- [ ] Add `rl2:priority` to Property Reference
- [ ] Update Condition description to cover norm state queries
- [ ] Update version to 0.4

**Dependencies:** Phases 1-5 complete

### Phase 7: Core Specification (RL2_Core.md)

- [ ] Update Condition description in Conceptual Model
- [ ] Add example showing duty state as precondition
- [ ] Update version to 0.4

**Dependencies:** Phases 1-6 complete

### Phase 8: ODRL Coverage (RL2_ODRL_Coverage.md)

- [ ] Update duty mapping in Full Mapping Table
- [ ] Add transformation rules for nested duties:

```markdown
ODRL Transformation Rules:
IF duty is nested in odrl:permission:
    1. Create rl2:Duty as standalone clause (with URI for referenceability)
    2. Add LogicalConstraint to permission's rl2:condition:
       - AtomicConstraint checking obligationState = Fulfilled
       - AtomicConstraint checking dutyPerformer = currentAgent (for SameSubject)
    3. Combine with rl2:and
```

- [ ] Update Canonical Worked Example
- [ ] Update version to 0.4

**Dependencies:** Phases 1-6 complete

### Phase 9: Primer (RL2_Primer.md)

- [ ] Add subsection on duty state preconditions in Conditions section
- [ ] Add examples for each pattern (Sein-sollen, Tun-sollen, SoD)
- [ ] Explain the verbosity trade-off (explicit logic vs. magic enums)
- [ ] Update version to 0.4

**Dependencies:** Phases 1-8 complete

### Phase 10: Use Cases Update

- [ ] Update all use case files in `usecases/` to use new pattern
- [ ] Update README.md to explain the explicit constraint approach

**Dependencies:** Phase 9 complete

### Phase 11: Version Bump

- [ ] Update rl2.ttl version to 0.4
- [ ] Update rl2p.ttl version to 0.4
- [ ] Update all documentation frontmatter to 0.4

**Dependencies:** All phases complete

---

## File Change Summary

| File | Changes |
|------|---------|
| `rl2.ttl` | Add targetNorm property, obligationState/dutyPerformer LeftOperands, currentAgent reference, priority property |
| `rl2-shacl.ttl` | Add conditional shape for norm state constraints |
| `rl2p.ttl` | Add performer property to ContextAssertion |
| `rl2p-shacl.ttl` | Update ContextAssertionShape |
| `RL2_Semantics.md` | **CRITICAL:** Add DutyPerformer to Σ, update resolve() function, update AtomicConstraint evaluation |
| `RL2_Vocabulary.md` | Add new properties and LeftOperand instances |
| `RL2_Core.md` | Update condition description, add example |
| `RL2_ODRL_Coverage.md` | Update mapping table, add transformation rules |
| `RL2_Primer.md` | Add duty state section with patterns |
| `RL2_Protocol.md` | Document performer semantics |
| `usecases/*.md` | Update all examples to explicit constraint pattern |

---

## Theoretical Foundation

### Deontic Logic Mapping

| Concept | German | RL2 Implementation |
|---------|--------|-------------------|
| Ought-to-do (personal) | Tun-sollen | `obligationState = Fulfilled` AND `dutyPerformer = currentAgent` |
| Ought-to-be (impersonal) | Sein-sollen | `obligationState = Fulfilled` (only) |
| Separation of Duty | - | `obligationState = Fulfilled` AND `dutyPerformer ≠ currentAgent` |

### Why This Is Superior

1. **De-Magicing:** Identity binding is an explicit logical proposition, not a hidden enum interpretation
2. **Regularity:** Norm state is just another queryable property of the world
3. **Parsimony:** No new classes or enumerations
4. **Expressiveness:** Supports patterns impossible with SubjectScope (e.g., specific agent)
5. **Decidability:** All logic is explicit in the policy graph, enabling static analysis

### The Verbosity Trade-off

More verbose (3 objects vs. 1), but:
- Every piece of logic is explicit
- No hidden evaluator semantics
- Formally decidable
- This is the correct trade-off for a rigorous normative language

---

## Testing Considerations

After implementation, validate:

1. **SHACL validation** - Run rl2-shacl.ttl against example policies
2. **Semantic consistency** - Verify all patterns produce correct results
3. **ODRL transformation** - Verify nested duty transformation produces valid RL2
4. **Edge cases:**
   - Duty not yet fulfilled (DutyPerformer = ⊥)
   - Duty fulfilled by system vs. agent
   - Multiple fulfillment events
