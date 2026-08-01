# Use Case 11: Data Freshness Promise

**Pattern:** Promised state crystallized into a Maintenance Duty

**Scope:** RL2 core transformation and normative reporting

**Status:** SCOPE-2 migrated

## Business rule

> A provider offers to keep a dataset no more than six hours old. After acceptance, stale data
> violates the Maintenance Duty and makes a sibling incident-reporting Duty applicable.

RL2 does not monitor a clock, transition stored Promise state, or create a ticket. The evaluator
reads one immutable snapshot. A companion system may act on the returned obligation, but that
action is outside core semantics.

## Source Offer

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:DataProvider a rl2:Agent .
ex:DataConsumer a rl2:Agent .
ex:CustomerDataset a rl2:Asset .
ex:SLAViolationReport a rl2:Asset .
ex:createIncidentTicket a rl2:Action .

ex:datasetAgeOperand a rl2:LeftOperand ;
    rdfs:range xsd:duration ;
    rl2:resolutionPath "asset.metadata.datasetAge" .

ex:datasetIsFresh a rl2:AtomicConstraint ;
    rl2:leftOperand ex:datasetAgeOperand ;
    rl2:constraintOperator rl2:lte ;
    rl2:rightOperand "PT6H"^^xsd:duration .

ex:freshnessPromise a rl2:Promise ;
    rl2:promisor ex:DataProvider ;
    rl2:promisee ex:DataConsumer ;
    rl2:promisedState ex:datasetIsFresh ;
    rl2:object ex:CustomerDataset .

ex:incidentDuty a rl2:Duty ;
    rl2:subject ex:DataProvider ;
    rl2:counterparty ex:DataConsumer ;
    rl2:action ex:createIncidentTicket ;
    rl2:object ex:SLAViolationReport ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:freshnessPromise ;
        rl2:leftOperand rl2:promiseStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:freshnessOffer a rl2:Offer ;
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:DataConsumer ;
    rl2:clause ex:freshnessPromise, ex:incidentDuty .
```

## Acceptance value

```text
Acceptance(
  agreementId = ex:freshnessAgreement,
  grantor      = ex:DataProvider,
  grantee      = ex:DataConsumer,
  primaryIds   = {
    ex:freshnessPromise -> ex:freshnessDuty,
    ex:incidentDuty     -> ex:incidentDuty_A1
  },
  claimIds       = { ex:freshnessPromise -> ex:freshnessClaim },
  objectBindings = {},
  dutyWindows    = {}
)
```

No `dutyWindow` is supplied because the business rule is ongoing. The resulting Maintenance Duty
can be `Active` or `Violated`; it is not declared `Fulfilled` merely because one snapshot is fresh.

## Materialized Agreement

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

ex:DataProvider a rl2:Agent .
ex:DataConsumer a rl2:Agent .
ex:CustomerDataset a rl2:Asset .
ex:SLAViolationReport a rl2:Asset .
ex:createIncidentTicket a rl2:Action .

ex:datasetAgeOperand a rl2:LeftOperand ;
    rdfs:range xsd:duration ;
    rl2:resolutionPath "asset.metadata.datasetAge" .

ex:datasetIsFresh a rl2:AtomicConstraint ;
    rl2:leftOperand ex:datasetAgeOperand ;
    rl2:constraintOperator rl2:lte ;
    rl2:rightOperand "PT6H"^^xsd:duration .

ex:freshnessDuty a rl2:Duty ;
    rl2:subject ex:DataProvider ;
    rl2:counterparty ex:DataConsumer ;
    rl2:object ex:CustomerDataset ;
    rl2:invariant ex:datasetIsFresh .

ex:freshnessClaim a rl2:Claim ;
    rl2:subject ex:DataConsumer ;
    rl2:counterparty ex:DataProvider ;
    rl2:correlativeTo ex:freshnessDuty .

ex:incidentDuty_A1 a rl2:Duty ;
    rl2:subject ex:DataProvider ;
    rl2:counterparty ex:DataConsumer ;
    rl2:action ex:createIncidentTicket ;
    rl2:object ex:SLAViolationReport ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:freshnessDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:freshnessAgreement a rl2:Agreement ;
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:DataConsumer ;
    rl2:clause ex:freshnessDuty, ex:freshnessClaim, ex:incidentDuty_A1 ;
    prov:wasDerivedFrom ex:freshnessOffer .
```

## Expected evaluation

For a request matching `(DataProvider, createIncidentTicket, SLAViolationReport)`:

| Snapshot fact `asset.metadata.datasetAge` | Freshness Duty | Incident Duty atom |
|---|---|---|
| `PT2H` | `Active` | absent |
| `PT7H` | `Violated` | `obligate(ex:incidentDuty_A1, ex:freshnessAgreement)` |
| missing or invalid | `IndeterminateStatus` | attributed `indeterminate` |

Resolution ignores independent Duty atoms when choosing an access decision. The envelope exposes
the applicable incident-reporting Duty; it does not execute it.

## Migration note

The previous state machine, periodic reset, mutable `state.Promises` operand, and automatic ticket
creation are removed. Repeated six-hour periods would require separately identified bounded Duty
occurrences or a companion scheduling profile; this case expresses the ongoing freshness rule.
