# Team Licence

## Scenario

An administrator must pay for a team licence before a named team member may access the service.

## Why it matters

The access condition depends on fulfilment of an organizational obligation, not on the identity of the payer.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:TeamAdministrator a rl2:Agent .
ex:Alice a rl2:Agent .
ex:TeamLicence a rl2:Asset .
ex:PremiumService a rl2:Asset .
ex:pay a rl2:Action .
ex:access a rl2:Action .

ex:teamPaymentDuty a rl2:Duty ;
    rl2:subject ex:TeamAdministrator ;
    rl2:action ex:pay ;
    rl2:object ex:TeamLicence .

ex:memberAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Alice ;
    rl2:action ex:access ;
    rl2:object ex:PremiumService ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:teamPaymentDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:teamPolicy a rl2:Set ;
    rl2:clause ex:teamPaymentDuty, ex:memberAccessPrivilege .
```

## Request and snapshot

Request: `(agent = Alice, action = access, asset = PremiumService)`.

World snapshot: qualifying evidence records the TeamAdministrator performing `pay` on `TeamLicence`.

## Expected result

`teamPaymentDuty` is `Fulfilled`; Alice’s request is `Permit`. The same payment does not itself grant access to an agent not named by a matching privilege.
