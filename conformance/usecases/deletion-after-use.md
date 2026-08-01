# Deletion after Use

## Scenario

A logistics recipient may process shipment data for route optimization. Once the supplied snapshot establishes completion, the recipient must delete the data within the stated window.

## Why it matters

Completion evidence activates the deletion duty; deletion status is then derived from the same immutable snapshot. RL2 does not perform deletion or maintain a workflow state machine.

The deletion deadline is "within 24 hours of completion" — a relative deadline anchored to a
snapshot fact, not a calendar date fixed at authoring time. The duty window is expressed with
`rl2:startRelativeTo`/`rl2:endRelativeTo` anchored to the completion timestamp fact, each with a
`rl2:startOffset`/`rl2:endOffset`, rather than by precomputing an absolute expiry and baking it
into the policy RDF. Policy meaning therefore stays in the policy: replaying this Agreement
against a snapshot with a different completion time yields a different, correctly shifted window,
which a hardcoded absolute window could not do. Compare `data-retention-limit.md`, which keeps the
absolute-endpoint style for a fixed contractual date — both endpoint forms remain valid.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:LogisticsCompany a rl2:Agent .
ex:Recipient a rl2:Agent .
ex:ShipmentData a rl2:Asset .
ex:optimizeRoute a rl2:Action .
ex:delete a rl2:Action .
ex:processingComplete a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "global.routeOptimization.completed" .
ex:completedAt a rl2:LeftOperand ;
    rdfs:range xsd:dateTimeStamp ;
    rl2:resolutionPath "global.routeOptimization.completedAt" .

ex:routeOptimization a rl2:Privilege ;
    rl2:subject ex:Recipient ; rl2:action ex:optimizeRoute ; rl2:object ex:ShipmentData .
ex:deleteAfterCompletion a rl2:Duty ;
    rl2:subject ex:Recipient ; rl2:action ex:delete ; rl2:object ex:ShipmentData ;
    rl2:counterparty ex:LogisticsCompany ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:processingComplete ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] ;
    rl2:dutyWindow [ a rl2:DutyWindow ;
        rl2:startRelativeTo ex:completedAt ; rl2:startOffset "PT0S"^^xsd:dayTimeDuration ;
        rl2:endRelativeTo ex:completedAt ; rl2:endOffset "P1D"^^xsd:dayTimeDuration ] .

ex:shipmentAgreement a rl2:Agreement ;
    rl2:grantor ex:LogisticsCompany ; rl2:grantee ex:Recipient ;
    rl2:clause ex:routeOptimization, ex:deleteAfterCompletion .
```

## Request and snapshot

Request: `(Recipient, optimizeRoute, ShipmentData)`.

World snapshot: `global.routeOptimization.completed = true` and
`global.routeOptimization.completedAt = 2026-08-01T12:00:00Z`. `resolveWindow` resolves the duty
window to `[2026-08-01T12:00:00Z, 2026-08-02T12:00:00Z)` — the anchor plus each offset. Deletion
evidence is supplied separately.

## Expected result

Expected decision: `Permit` for the processing request. The deletion duty is applicable and is `Fulfilled`, `Active`, or `Violated` according to the snapshot time and qualifying deletion evidence.
