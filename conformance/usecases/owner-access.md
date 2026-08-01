# Owner Access

## Scenario

Alice may read a personal file only while the snapshot identifies Alice as its owner.

## Why it matters

The example compares an asset-scoped profile fact with the requesting agent without copying the
request identity into the policy as a condition value.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Alice a rl2:Agent .
ex:PersonalFile a rl2:Asset .
ex:read a rl2:Action .

ex:dataOwner a rl2:LeftOperand ;
    rdfs:range rl2:Agent ;
    rl2:resolutionPath "asset.dataOwner" .

ex:ownerPrivilege a rl2:Privilege ;
    rl2:subject ex:Alice ;
    rl2:action ex:read ;
    rl2:object ex:PersonalFile ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:dataOwner ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:currentAgent
    ] .

ex:ownerPolicy a rl2:Set ;
    rl2:clause ex:ownerPrivilege .
```

## Request and snapshot

Request: `(agent = Alice, action = read, asset = PersonalFile)`.

World snapshot: `asset.dataOwner = Alice` for PersonalFile.

## Expected result

The request is `Permit`. A conflicting owner assertion produces `Indeterminate`; an owner other
than Alice makes the condition false.
