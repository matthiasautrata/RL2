# Pass-through Terms

## Scenario

A data aggregator may redistribute licensed data to a customer only when the customer is already bound by the required downstream terms. The aggregator must maintain that binding.

## Why it matters

This pattern separates the admission question from the continuing obligation. It does not claim that RL2 creates the downstream contract or transfers rights.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Vendor a rl2:Agent .
ex:Aggregator a rl2:Agent .
ex:Customer a rl2:Agent .
ex:LicensedData a rl2:Asset .
ex:redistribute a rl2:Action .
ex:maintainTerms a rl2:Action .
ex:downstreamTermsBound a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "context.downstreamTerms.bound" .

ex:redistributeUnderTerms a rl2:Privilege ;
    rl2:subject ex:Aggregator ; rl2:action ex:redistribute ; rl2:object ex:LicensedData ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:downstreamTermsBound ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .
ex:maintainPassThroughTerms a rl2:Duty ;
    rl2:subject ex:Aggregator ; rl2:action ex:maintainTerms ; rl2:object ex:Customer ;
    rl2:counterparty ex:Vendor .

ex:distributionAgreement a rl2:Agreement ;
    rl2:grantor ex:Vendor ; rl2:grantee ex:Aggregator ;
    rl2:clause ex:redistributeUnderTerms, ex:maintainPassThroughTerms .
```

## Request and snapshot

Request: `(Aggregator, redistribute, LicensedData)` for `Customer`.

World snapshot: `context.downstreamTerms.bound = true`, attributed to the agreement registry.

## Expected result

Expected decision: `Permit`; the maintenance duty is assessed independently from evidence concerning the continuing binding. If the registry says `false`, the redistribution privilege does not match.
