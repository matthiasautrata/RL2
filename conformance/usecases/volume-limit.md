# Volume Limit

## Scenario

A subscriber may retrieve records from a data service only when the requested volume fits within its trusted remaining monthly quota.

## Why it matters

The policy tests an admission fact, not a mutable counter. This avoids implying that evaluation itself reserves or updates quota.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Subscriber a rl2:Agent .
ex:DataService a rl2:Asset .
ex:retrieve a rl2:Action .
ex:requestFitsRemainingQuota a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "global.quota.requestedWithinRemaining" .

ex:limitedRetrieval a rl2:Privilege ;
    rl2:subject ex:Subscriber ; rl2:action ex:retrieve ; rl2:object ex:DataService ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:requestFitsRemainingQuota ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:volumeSubscription a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Subscriber ; rl2:clause ex:limitedRetrieval .
```

## Request and snapshot

Request: `(Subscriber, retrieve, DataService)` with `requestedRecords = 12,000`.

World snapshot: `global.quota.requestedWithinRemaining = true`, attributed to the quota service after comparing `requestedRecords <= remainingRecords` for the relevant period.

## Expected result

Expected decision: `Permit`. The evaluator neither reserves records nor changes the remaining quota.
