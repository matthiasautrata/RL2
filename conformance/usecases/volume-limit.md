# Volume Limit

## Scenario

A subscriber may retrieve records from a data service only when the requested volume fits within
its plan's per-request ceiling and within its trusted remaining monthly quota.

## Why it matters

The requested volume is a real, typed input carried by the Request itself — `request.parameters`
(RL2 0.7) resolves it the same way any other operand resolves, instead of leaving it as prose that
names a Request field the formal model does not define. The per-request ceiling is a fixed plan
term, so it is checked directly against `request.parameters.requestedRecords`. The remaining
monthly quota is not: it is a mutable running total the subscriber does not control the shape of,
so — as before — the policy still tests a supplied admission fact rather than a mutable counter.
This avoids implying that evaluation itself reserves or updates quota. (RL2's `AtomicConstraint`
compares one resolved operand against an authored literal, IRI constant, or runtime reference — not
against a second, independently dynamic fact — so a "requested volume fits remaining quota"
comparison is necessarily expressed as a precomputed admission fact, not as a direct two-fact
condition.) Compare `usage-metering.md`, which keeps the fully precomputed-fact style throughout;
both styles remain valid in RL2 0.7.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Subscriber a rl2:Agent .
ex:DataService a rl2:Asset .
ex:retrieve a rl2:Action .
ex:requestedRecords a rl2:LeftOperand ;
    rl2:valueType xsd:integer ;
    rl2:resolutionPath "request.parameters.requestedRecords" .
ex:requestFitsRemainingQuota a rl2:LeftOperand ;
    rl2:valueType xsd:boolean ;
    rl2:resolutionPath "global.quota.requestedWithinRemaining" .

ex:limitedRetrieval a rl2:Privilege ;
    rl2:subject ex:Subscriber ; rl2:action ex:retrieve ; rl2:object ex:DataService ;
    rl2:condition [ a rl2:LogicalConstraint ; rl2:constraintOperator rl2:and ;
        rl2:operand [ a rl2:AtomicConstraint ; rl2:leftOperand ex:requestedRecords ;
            rl2:constraintOperator rl2:lte ; rl2:rightOperand "20000"^^xsd:integer ] ;
        rl2:operand [ a rl2:AtomicConstraint ; rl2:leftOperand ex:requestFitsRemainingQuota ;
            rl2:constraintOperator rl2:eq ; rl2:rightOperand true ]
    ] .

ex:volumeSubscription a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Subscriber ; rl2:clause ex:limitedRetrieval .
```

## Request and snapshot

Request: `(Subscriber, retrieve, DataService)` with `parameters = { requestedRecords: 12000 }`,
resolved via `request.parameters.requestedRecords`.

World snapshot: `global.quota.requestedWithinRemaining = true`, attributed to the quota service
after comparing `requestedRecords <= remainingRecords` for the relevant period.

## Expected result

Expected decision: `Permit`. `12000 <= 20000` (the plan's per-request ceiling) and the remaining-quota
admission fact both hold. The evaluator neither reserves records nor changes the remaining quota.
