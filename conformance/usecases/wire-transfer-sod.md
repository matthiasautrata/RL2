# Wire-Transfer Separation of Duty

## Scenario

Alice may execute a wire transfer only after Bob has approved that transfer.

## Why it matters

The policy expresses an instance-specific four-eyes control. Role expansion may generate one such
policy instance for each authorized pair.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Alice a rl2:Agent .
ex:Bob a rl2:Agent .
ex:WireTransfer a rl2:Asset .
ex:approve a rl2:Action .
ex:execute a rl2:Action .

ex:approvalDuty a rl2:Duty ;
    rl2:subject ex:Bob ;
    rl2:action ex:approve ;
    rl2:object ex:WireTransfer .

ex:executePrivilege a rl2:Privilege ;
    rl2:subject ex:Alice ;
    rl2:action ex:execute ;
    rl2:object ex:WireTransfer ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:approvalDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:wirePolicy a rl2:Set ;
    rl2:clause ex:approvalDuty, ex:executePrivilege .
```

## Request and snapshot

Request: `(agent = Alice, action = execute, asset = WireTransfer)`.

World snapshot: qualifying evidence records `Bob` performing `approve` on this `WireTransfer`.

## Expected result

The approval Duty is `Fulfilled` and Alice's request is `Permit`. Evidence of Alice approving does
not fulfill Bob's Duty.
