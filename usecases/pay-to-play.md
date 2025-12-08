# Use Case 1: Pay-to-Play

**Pattern:** Tun-sollen (Ought-to-do)
**Identity Check:** `dutyPerformer = currentAgent`
**Category:** Individual licensing

## Scenario

A user must pay before accessing premium content. The same user who pays gets access.

## Policy Intent

> "If YOU pay, YOU may view."

## Key Characteristics

- Personal obligation binding
- Payment creates individual entitlement
- No transferability of access rights
- Audit trail links payment to accessor

## Profile-Declared Actions

```turtle
@prefix licensing: <https://example.org/profile/licensing#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

licensing:pay a rl2:Action ;
    rdfs:label "Pay" ;
    rdfs:comment "Make payment for a license." .

licensing:view a rl2:Action ;
    rdfs:label "View" ;
    rdfs:comment "View licensed content." .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix licensing: <https://example.org/profile/licensing#> .

ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:User ;
    rl2:action licensing:pay ;
    rl2:object ex:PhotoLicense .

ex:viewPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action licensing:view ;
    rl2:object ex:PremiumPhoto ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Is the duty fulfilled?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:obligationStateOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand rl2:Fulfilled
        ] ;
        rl2:operand [
            # Check 2: Did I (current agent) fulfill it?
            a rl2:AtomicConstraint ;
            rl2:targetNorm ex:paymentDuty ;
            rl2:leftOperand rl2:dutyPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

## Evaluation

| Scenario | Payment By | Request By | Result |
|----------|------------|------------|--------|
| Normal | Alice | Alice | PERMIT |
| Sharing attempt | Alice | Bob | DENY |

## Comparison

- **ODRL:** Nested duty implies same assignee (implicit)
- **XACML:** Requires `subject-id == payment.payer-id` condition
- **RL2:** Explicit `dutyPerformer = currentAgent` makes intent explicit
