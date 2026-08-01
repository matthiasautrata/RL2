# Check-Signing Separation of Duty

## Scenario

Bob may sign a particular check only if Alice prepared that check.

## Why it matters

The policy is instance-specific: the Duty subject, Privilege subject, and check are explicit. A
generator may create analogous policies for other authorized pairs and checks.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Alice a rl2:Agent .
ex:Bob a rl2:Agent .
ex:Check123 a rl2:Asset .
ex:prepare a rl2:Action .
ex:sign a rl2:Action .

ex:preparationDuty a rl2:Duty ;
    rl2:subject ex:Alice ;
    rl2:action ex:prepare ;
    rl2:object ex:Check123 .

ex:signPrivilege a rl2:Privilege ;
    rl2:subject ex:Bob ;
    rl2:action ex:sign ;
    rl2:object ex:Check123 ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:preparationDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:checkPolicy a rl2:Set ;
    rl2:clause ex:preparationDuty, ex:signPrivilege .
```

## Request and snapshot

Request: `(agent = Bob, action = sign, asset = Check123)`.

World snapshot: qualifying evidence records `Alice` performing `prepare` on `Check123`.

## Expected result

The request is `Permit`. Alice is not the subject of the signing Privilege, and Bob's preparation
does not fulfill Alice's Duty.
