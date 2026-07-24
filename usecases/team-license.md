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

## Profile-Declared Actions

```turtle
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

licensing:pay a rl2:Action ;
    rdfs:label "Pay" ;
    rdfs:comment "Make payment for a license." .

licensing:access a rl2:Action ;
    rdfs:label "Access" ;
    rdfs:comment "Access premium features." .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix licensing: <https://example.org/profile/licensing#> .

ex:teamPaymentDuty a rl2:Duty ;
    rl2:subject ex:TeamAdmin ;
    rl2:action licensing:pay ;
    rl2:object ex:TeamLicense .

ex:teamAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:TeamMember ;
    rl2:action licensing:access ;
    rl2:object ex:PremiumFeatures ;
    rl2:condition [
        # Sein-sollen: Only check state, not who fulfilled
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:teamPaymentDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
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
