# SLA Credit Clause

## Scenario

A provider offers a monthly uptime commitment. On acceptance, the promised state becomes a
windowed Maintenance Duty. A sibling Duty to issue a service credit becomes applicable when that
Duty is violated.

## Why it matters

Materialization is pure: it creates an Agreement value and reads no snapshot. The Promise is
structurally a proposed Duty, so crystallization unwraps and rebinds it rather than re-deriving a
Duty from separate fields. Status-dependent terms use `obligationStateOperand` both before and
after acceptance; only the `targetNorm` rebinds, from the Promise to the generated Duty.

## Source Offer

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:Service a rl2:Asset .
ex:issueCredit a rl2:Action .

ex:monthlyUptime a rl2:LeftOperand ;
    rl2:valueType xsd:decimal ;
    rl2:resolutionPath "asset.metadata.monthlyUptime" .

ex:uptimeMeetsTarget a rl2:AtomicConstraint ;
    rl2:leftOperand ex:monthlyUptime ;
    rl2:constraintOperator rl2:gte ;
    rl2:rightOperand "99.9"^^xsd:decimal .

ex:uptimePromise a rl2:Promise ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Customer ;
    rl2:invariant ex:uptimeMeetsTarget ;
    rl2:object ex:Service .

ex:creditDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Customer ;
    rl2:action ex:issueCredit ;
    rl2:object ex:Service ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:uptimePromise ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:uptimeOffer a rl2:Offer ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:uptimePromise, ex:creditDuty .
```

## Acceptance

```text
Acceptance(
  agreementId = ex:uptimeAgreement,
  grantor = ex:Provider,
  grantee = ex:Customer,
  primaryIds = {
    ex:uptimePromise -> ex:uptimeDuty,
    ex:creditDuty -> ex:creditDuty_A1
  },
  objectBindings = {},
  dutyWindows = {
    ex:uptimePromise -> [2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z)
  }
)
```

## Materialized Agreement

```turtle
@prefix ex: <https://example.org/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:Service a rl2:Asset .
ex:issueCredit a rl2:Action .

ex:monthlyUptime a rl2:LeftOperand ;
    rl2:valueType xsd:decimal ;
    rl2:resolutionPath "asset.metadata.monthlyUptime" .

ex:uptimeMeetsTarget a rl2:AtomicConstraint ;
    rl2:leftOperand ex:monthlyUptime ;
    rl2:constraintOperator rl2:gte ;
    rl2:rightOperand "99.9"^^xsd:decimal .

ex:uptimeDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Customer ;
    rl2:object ex:Service ;
    rl2:invariant ex:uptimeMeetsTarget ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2026-07-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2026-08-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:creditDuty_A1 a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Customer ;
    rl2:action ex:issueCredit ;
    rl2:object ex:Service ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:uptimeDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:uptimeAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:uptimeDuty, ex:creditDuty_A1 ;
    prov:wasDerivedFrom ex:uptimeOffer .
```

## Request and snapshot

Request: `(Provider, issueCredit, Service)`. The snapshot establishes that `uptimeDuty` is
`Violated` and contains no qualifying credit evidence.

## Expected result

The Agreement contains the two materialized Duties. Evaluation derives an obligation atom for
`creditDuty_A1`, whose status is `Active`; the access decision is `NotApplicable` because Duties
do not grant or prohibit access.
