# Use Case 5: Wire Transfer (Two-Man Rule)

**Pattern:** Separation of Duty (Static SoD)
**Identity Check:** `dutyPerformer ≠ currentAgent`
**Category:** Financial controls, NIST compliance

## Scenario

A wire transfer requires approval before execution. The person who prepared the transfer cannot approve it (Two-Man Rule / Four-Eyes Principle).

## Policy Intent

> "If SOMEONE ELSE approved, you may execute."

## Key Characteristics

- Fraud prevention
- Collusion resistance
- NIST AC-5 (Separation of Duties)
- Banking regulation compliance

## Profile-Declared Actions

```turtle
@prefix finance: <https://example.org/profile/finance#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

finance:approve a rl2:Action ;
    rdfs:label "Approve" ;
    rdfs:comment "Approve a financial transaction." .

finance:execute a rl2:Action ;
    rdfs:label "Execute" ;
    rdfs:comment "Execute an approved transaction." .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix finance: <https://example.org/profile/finance#> .

ex:wireTransferApproval a rl2:Duty ;
    rl2:subject ex:Approver ;
    rl2:action finance:approve ;
    rl2:object ex:WireTransfer .

ex:executeTransferPrivilege a rl2:Privilege ;
    rl2:subject ex:Preparer ;
    rl2:action finance:execute ;
    rl2:object ex:WireTransfer ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Is the approval duty fulfilled?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:wireTransferApproval ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Check 2: Was it fulfilled by someone ELSE (not me)?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:wireTransferApproval ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:neq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

## Evaluation

| Scenario | Prepared By | Approved By | Execute Request By | Result |
|----------|-------------|-------------|-------------------|--------|
| Proper SoD | Alice | Bob | Alice | PERMIT |
| Self-approval | Alice | Alice | Alice | DENY |
| Third party | Alice | Bob | Carol | PERMIT |

## NIST Mapping

- **AC-5:** Separation of Duties
- **AC-5(a):** Define duties requiring separation
- **AC-5(b):** Document separation mechanisms

RL2's `dutyPerformer ≠ currentAgent` provides auditable, declarative SoD enforcement.

## Comparison

- **RBAC:** Role constraints (Preparer ≠ Approver roles)
- **XACML:** `not(subject-id == approval.approver-id)` condition
- **RL2:** Explicit `neq` constraint captures SoD intent directly
