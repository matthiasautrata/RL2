# Pay-to-Play

## Scenario

A customer may view premium content only after that customer has paid for the licence.

## Why it matters

The Duty and Privilege name the same customer, so another customer's payment cannot satisfy this
policy instance. The gate is ordinary pre-duty gating — `viewPrivilege` requires `paymentDuty` to be
met and is canonically expressed with `rl2:prerequisiteDuty`, not a status-condition equality test.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Alice a rl2:Agent .
ex:PremiumPhoto a rl2:Asset .
ex:PhotoLicence a rl2:Asset .
ex:pay a rl2:Action .
ex:view a rl2:Action .

ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:Alice ;
    rl2:action ex:pay ;
    rl2:object ex:PhotoLicence .

ex:viewPrivilege a rl2:Privilege ;
    rl2:subject ex:Alice ;
    rl2:action ex:view ;
    rl2:object ex:PremiumPhoto ;
    rl2:prerequisiteDuty ex:paymentDuty .

ex:photoPolicy a rl2:Set ;
    rl2:clause ex:paymentDuty, ex:viewPrivilege .
```

## Request and snapshot

Request: `(agent = Alice, action = view, asset = PremiumPhoto)`.

World snapshot: qualifying evidence records `Alice` performing `pay` on `PhotoLicence`.

## Expected result

`paymentDuty` is `Fulfilled` and the request is `Permit`. A request by another agent is not matched by `viewPrivilege`.
