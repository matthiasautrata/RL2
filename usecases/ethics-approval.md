# Use Case 7: Ethics Board Approval

**Pattern:** Multi-party workflow with identity binding
**Identity Check:** `operationalAgent = currentAgent`
**Category:** Research governance, IRB compliance

## Scenario

A researcher must obtain ethics board approval before accessing sensitive research data. The approval is granted to a specific researcher, not transferable.

## Policy Intent

> "If the ethics board approved YOUR request, YOU may access."

## Key Characteristics

- Named individual approval
- Non-transferable grant
- Audit trail for compliance
- Common in IRB/ethics workflows

## RL2 Model (Unified State Approach)

```turtle
ex:ethicsApprovalEvent a rl2:Event ;
    rdfs:comment "Approval from ethics board for specific researcher" .

ex:sensitiveDataAccess a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveDataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Has approval event occurred?
            a rl2:EventConstraint ;
            rl2:expectsEvent [
                a rl2:Event ;
                rl2:approver ex:EthicsBoard
            ]
        ] ;
        rl2:operand [
            # Check 2: Was approval for me (current agent)?
            # This uses event participant matching
            a rl2:AtomicConstraint ;
            rl2:leftOperand rl2:eventBeneficiary ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ] ;
        rl2:operand [
            # Check 3: Is approval still valid?
            a rl2:TemporalConstraint ;
            rl2:interval [ rl2:end "2025-12-31T23:59:59Z"^^xsd:dateTime ]
        ]
    ] .
```

## Evaluation

| Scenario | Approval For | Request By | Result |
|----------|--------------|------------|--------|
| Approved researcher | Alice | Alice | PERMIT |
| Colleague sharing | Alice | Bob | DENY |
| Expired approval | Alice (2024) | Alice | DENY |

## Multi-Approval Variant

For N-of-M approval (e.g., 2 of 3 committee members):

```turtle
rl2:condition [
    a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand [
        # At least 2 approvals from any committee members
        # (Implementation would use counting constraint)
    ]
] .
```

## Comparison

- **Paper-based:** Manual verification, error-prone
- **XACML:** Complex attribute matching
- **RL2:** `EventConstraint` + identity binding via context + temporal bounds
