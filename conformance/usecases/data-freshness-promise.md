# Data Freshness Commitment

## Scenario

A provider offers to keep a customer dataset no more than six hours old. Acceptance produces a Maintenance Duty.

## Why it matters

The example expresses an ongoing quality commitment as a snapshot-derived invariant, without a clock-driven state machine.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Consumer a rl2:Agent .
ex:CustomerDataset a rl2:Asset .
ex:inspect a rl2:Action .

ex:datasetAge a rl2:LeftOperand ;
    rdfs:range xsd:dayTimeDuration ;
    rl2:resolutionPath "asset.metadata.datasetAge" .

ex:isFresh a rl2:AtomicConstraint ;
    rl2:leftOperand ex:datasetAge ;
    rl2:constraintOperator rl2:lte ;
    rl2:rightOperand "PT6H"^^xsd:dayTimeDuration .

ex:freshnessPromise a rl2:Promise ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:invariant ex:isFresh ;
    rl2:object ex:CustomerDataset .

ex:freshnessOffer a rl2:Offer ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Consumer ;
    rl2:clause ex:freshnessPromise .

ex:freshnessDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Consumer ;
    rl2:object ex:CustomerDataset ;
    rl2:invariant ex:isFresh .

ex:freshnessAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Consumer ;
    rl2:clause ex:freshnessDuty .
```

## Request and snapshot

Request: `(agent = Provider, action = inspect, asset = CustomerDataset)`.

World snapshot: `asset.metadata.datasetAge` is either `PT2H` or `PT7H`.

## Expected result

At `PT2H`, `freshnessDuty` is `Active`. At `PT7H`, it is `Violated`. The evaluator classifies the Duty; remediation is outside the policy decision. No clause in `freshnessAgreement` grants, denies, or attaches a prerequisite to the `inspect` action, so the request's decision is `NotApplicable`; the `inspect` action illustrates status inspection only and is not itself governed by this Agreement.
