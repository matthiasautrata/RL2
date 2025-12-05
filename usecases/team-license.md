# Use Case 2: Team License

**Pattern:** Sein-sollen (Ought-to-be)
**Identity Check:** None (anyone may fulfill)
**Category:** Organizational licensing

## Scenario

An administrator pays for a team license. All team members gain access regardless of who paid.

## Policy Intent

> "If the fee IS PAID, members may access."

## Key Characteristics

- Impersonal/state obligation
- Payment by one enables access for many
- Decoupled actor from beneficiary
- Common in SaaS B2B licensing

## RL2 Model (Unified State Approach)

```turtle
ex:teamPaymentDuty a rl2:Duty ;
    rl2:subject ex:TeamAdmin ;
    rl2:action ex:pay ;
    rl2:object ex:TeamLicense .

ex:teamAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:TeamMember ;
    rl2:action ex:access ;
    rl2:object ex:PremiumFeatures ;
    rl2:condition [
        # Sein-sollen: Only check state, not who fulfilled
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:teamPaymentDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand rl2:Fulfilled
    ] .
```

## Evaluation

| Scenario | Payment By | Request By | Result |
|----------|------------|------------|--------|
| Admin accesses | Alice (admin) | Alice | PERMIT |
| Member accesses | Alice (admin) | Bob (member) | PERMIT |
| Non-member | Alice (admin) | Eve (external) | DENY (subject mismatch) |

## Comparison

- **ODRL:** Cannot express directly; requires separate policy per member
- **XACML:** Check `team.license-status == paid` attribute
- **RL2:** Sein-sollen (no `dutyPerformerOperand` check) cleanly decouples payer from accessor
