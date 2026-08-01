# Suspension Exception

## Scenario

A platform permits a user to access an asset unless the user’s account status is suspended. `not`
has exactly one operand and preserves indeterminacy: a missing or conflicting account-status fact
does not become a permit.

## Why it matters

Negation must preserve missing-data semantics instead of treating an unknown fact as false.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix account: <https://example.org/profile/account#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:User a rl2:Agent .
ex:Platform a rl2:Asset .
ex:access a rl2:Action .

account:status a rl2:LeftOperand ;
    rdfs:range account:Status ;
    rl2:resolutionPath "agent.accountStatus" .
account:Suspended a account:Status .

ex:platformAccess a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Platform ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:not ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand account:status ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef account:Suspended
        ]
    ] .

ex:policy a rl2:Set ; rl2:clause ex:platformAccess .
```

## Request and snapshot

Request: `(User, access, Platform)`. The snapshot provides `agent.accountStatus`.

## Expected result

`Suspended` makes the rule inapplicable; another resolved status produces `Permit`. A missing or
conflicting status produces `Indeterminate`.
