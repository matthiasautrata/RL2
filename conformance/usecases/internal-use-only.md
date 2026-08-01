# Internal Use Only

## Scenario

A data vendor licenses reference data to a company for use within that company. Use for an external recipient is not authorized.

## Why it matters

“Internal use only” is a common data-licence term. RL2 expresses the distinction as a request-context condition, rather than leaving the meaning of *internal* to an evaluator.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Vendor a rl2:Agent .
ex:Licensee a rl2:Agent .
ex:ReferenceData a rl2:Asset .
ex:use a rl2:Action .
ex:recipientClass a rl2:LeftOperand ;
    rdfs:range xsd:string ;
    rl2:resolutionPath "context.recipient.class" .

ex:internalUse a rl2:Privilege ;
    rl2:subject ex:Licensee ; rl2:action ex:use ; rl2:object ex:ReferenceData ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:recipientClass ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand "internal" ] .

ex:internalUsePolicy a rl2:Agreement ;
    rl2:grantor ex:Vendor ; rl2:grantee ex:Licensee ; rl2:clause ex:internalUse .
```

## Request and snapshot

Request: `(Licensee, use, ReferenceData)`.

World snapshot: `context.recipient.class = "internal"`.

## Expected result

Expected decision: `Permit`. With `"external"`, no privilege matches and the decision is `NotApplicable`.
