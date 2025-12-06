# Use Case 6: Check Signing (Dynamic SoD)

**Pattern:** Dynamic Separation of Duty
**Identity Check:** `dutyPerformer ≠ currentAgent`
**Category:** Financial controls

## Scenario

A check can only be signed by someone who did not prepare it. Unlike static SoD (role-based), this is instance-specific: the same person could prepare check A and sign check B.

## Policy Intent

> "The signer of THIS check must not be the preparer of THIS check."

## Key Characteristics

- Instance-level constraint (not role-level)
- Same person can hold both roles on different instances
- Runtime enforcement required
- More flexible than static SoD

## RL2 Core Operands

This use case uses operands declared in RL2 Core for querying norm state. Unlike profile-declared operands (see break-glass.md), these are part of the RL2 ontology itself:

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Query the obligation state (Pending, Active, Fulfilled, Violated) of a target norm
rl2:obligationStateOperand a rl2:LeftOperand ;
    rdfs:label "Obligation State Operand" ;
    rdfs:comment """Queries the ObligationState of the target norm from Σ.
    Returns Pending, Active, Fulfilled, or Violated.
    Requires rl2:targetNorm to specify which norm to query.""" .

# Query the agent who fulfilled a target duty
rl2:dutyPerformerOperand a rl2:LeftOperand ;
    rdfs:label "Duty Performer Operand" ;
    rdfs:comment """Queries the agent who fulfilled the target duty from Σ.
    Returns an Agent IRI or ⊥ if not yet fulfilled.
    Requires rl2:targetNorm to specify which duty to query.
    Used with rl2:currentAgent to check identity binding (Tun-sollen vs Sein-sollen).""" .
```

## RL2 Model (Unified State Approach)

```turtle
ex:checkPreparation a rl2:Duty ;
    rl2:subject ex:FinanceStaff ;
    rl2:action ex:prepare ;
    rl2:object ex:Check .

ex:signCheckPrivilege a rl2:Privilege ;
    rl2:subject ex:FinanceStaff ;
    rl2:action ex:sign ;
    rl2:object ex:Check ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Is the preparation duty fulfilled?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:checkPreparation ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Check 2: Was it fulfilled by someone ELSE (not me)?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:checkPreparation ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:neq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

## Evaluation

| Scenario | Check | Prepared By | Sign Request By | Result |
|----------|-------|-------------|-----------------|--------|
| Proper DSD | #123 | Alice | Bob | PERMIT |
| Self-sign | #123 | Alice | Alice | DENY |
| Cross-check | #124 | Bob | Alice | PERMIT |

## Static vs. Dynamic SoD

| Aspect | Static SoD | Dynamic SoD |
|--------|------------|-------------|
| Constraint level | Role assignment | Instance execution |
| Flexibility | Low (role-locked) | High (per-instance) |
| Example | "No one can be both Preparer AND Approver" | "Cannot approve what you prepared" |
| RL2 model | Role constraints | `dutyPerformer ≠ currentAgent` per-instance |

## Comparison

- **RBAC Static SoD:** Mutually exclusive role assignment
- **RBAC Dynamic SoD:** Complex history-based constraints
- **RL2:** `DutyPerformer` tracking + `neq` constraint handles both naturally
