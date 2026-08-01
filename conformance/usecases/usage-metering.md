# Usage Metering

## Scenario

A subscriber may run analytics queries while the requested query count plus the trusted count already used in the billing period does not exceed its allowance.

## Why it matters

Metered rights require an unambiguous admission test. RL2 evaluates a supplied immutable quota observation; it does not update the counter. This use case keeps the fully precomputed-fact style throughout; compare `volume-limit.md`, which additionally checks a fixed per-request ceiling directly against `request.parameters.requestedRecords` — both styles remain valid in RL2 0.7.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Subscriber a rl2:Agent .
ex:AnalyticsService a rl2:Asset .
ex:query a rl2:Action .
ex:quotaAdmitsRequest a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "global.quota.requestedPlusUsedWithinLimit" .

ex:meteredQuery a rl2:Privilege ;
    rl2:subject ex:Subscriber ; rl2:action ex:query ; rl2:object ex:AnalyticsService ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:quotaAdmitsRequest ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:subscription a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Subscriber ; rl2:clause ex:meteredQuery .
```

## Request and snapshot

Request: `(Subscriber, query, AnalyticsService)` with `requestedQueries = 25`.

World snapshot: `global.quota.requestedPlusUsedWithinLimit = true`, computed by the trusted metering service from `usedQueries + requestedQueries <= 10,000`.

## Expected result

Expected decision: `Permit`. The evaluator does not update `usedQueries`; a later request is evaluated against a new snapshot.
