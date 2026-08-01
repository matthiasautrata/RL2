# Owner Access

## Scenario

Any agent may read a personal file only while the snapshot identifies that same agent as the
file's owner. The policy names no specific agent; ownership is decided per request.

## Why it matters

`rl2:subject rl2:anyAgent` matches every requesting agent; the condition compares the
asset-scoped `asset.dataOwner` fact against `rl2:currentAgent` (the requester), so ownership does
the real gating work instead of a subject match against one hardcoded agent.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:PersonalFile a rl2:Asset .
ex:read a rl2:Action .

ex:dataOwner a rl2:LeftOperand ;
    rdfs:range rl2:Agent ;
    rl2:resolutionPath "asset.dataOwner" .

ex:ownerPrivilege a rl2:Privilege ;
    rl2:subject rl2:anyAgent ;
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
than Alice makes the condition false and the request `NotApplicable`.
