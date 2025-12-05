# Use Case 10: Audit Trail Requirement

**Pattern:** Compliance prerequisite (Sein-sollen)
**Identity Check:** None (anyone may fulfill)
**Category:** Compliance, SOX, audit

## Scenario

Access to financial records is only permitted if an audit trail has been established. It doesn't matter who established it—the compliance state must exist.

## Policy Intent

> "If audit logging IS ENABLED, access is permitted."

## Key Characteristics

- System state prerequisite
- Identity-independent (Sein-sollen)
- Compliance-driven
- Enables defense-in-depth

## RL2 Model (Unified State Approach)

```turtle
ex:auditTrailSetup a rl2:Duty ;
    rl2:subject ex:SystemAdmin ;
    rl2:action ex:enableAuditLogging ;
    rl2:object ex:FinancialSystem .

ex:financialRecordAccess a rl2:Privilege ;
    rl2:subject ex:Auditor ;
    rl2:action ex:access ;
    rl2:object ex:FinancialRecords ;
    rl2:condition [
        # Sein-sollen: Only check state, not who fulfilled
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:auditTrailSetup ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand rl2:Fulfilled
    ] .
```

## Evaluation

| Scenario | Audit Enabled By | Access Request By | Result |
|----------|------------------|-------------------|--------|
| Admin setup | Alice (admin) | Bob (auditor) | PERMIT |
| Auto-setup | System | Bob (auditor) | PERMIT |
| Not enabled | - | Bob (auditor) | DENY |

## SOX Compliance Mapping

| SOX Requirement | RL2 Mechanism |
|-----------------|---------------|
| Section 302: Internal controls | Policy conditions |
| Section 404: Audit requirements | `obligationStateOperand` precondition |
| Audit trail | Sein-sollen (state-based, identity-independent) |

## Defense in Depth

The Sein-sollen pattern enables layered security:

1. **Layer 1:** Role-based access (Auditor role required)
2. **Layer 2:** System state (Audit logging enabled)
3. **Layer 3:** Temporal (Within audit period)

```turtle
rl2:condition [
    a rl2:LogicalConstraint ;
    rl2:constraintOperator rl2:and ;
    rl2:operand [ ... role check ... ] ;
    rl2:operand [
        # Sein-sollen: duty must be fulfilled (by anyone)
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:auditTrailSetup ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand rl2:Fulfilled
    ] ;
    rl2:operand [ ... temporal constraint ... ]
] .
```

## Comparison

- **Traditional RBAC:** Role check only
- **XACML:** System attribute check
- **RL2:** Duty state as queryable property via `obligationStateOperand`
