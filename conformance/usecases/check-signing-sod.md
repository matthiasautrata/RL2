# Check-Signing Separation of Duty

## Scenario

Bob may sign a particular check only if Alice prepared that check.

## Why it matters

The policy is instance-specific: the Duty subject, Privilege subject, and check are explicit. A
generator may create analogous policies for other authorized pairs and checks. The gate is ordinary
pre-duty gating — `signPrivilege` requires `preparationDuty` to be met and is canonically expressed
with `rl2:prerequisiteDuty`, not a status-condition equality test.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .

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
    rl2:prerequisiteDuty ex:preparationDuty .

ex:checkPolicy a rl2:Set ;
    rl2:clause ex:preparationDuty, ex:signPrivilege .
```

## Request and snapshot

Request: `(agent = Bob, action = sign, asset = Check123)`.

World snapshot: qualifying evidence records `Alice` performing `prepare` on `Check123`.

## Expected result

The request is `Permit`. Alice is not the subject of the signing Privilege, and Bob's preparation
does not fulfill Alice's Duty.
