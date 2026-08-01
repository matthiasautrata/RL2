# Use Case 52: SLA Credit Clause

**Pattern:** Pure Offer acceptance with a promised state and a sibling remedial term

**Scope:** RL2 core transformation

**Status:** SCOPE-2 migrated

## Business rule

> A provider offers 99.9% uptime for a calendar month. After acceptance, the provider owes the
> customer a maintenance Duty for that interval and a service-credit Duty if the uptime Duty is
> violated.

The catalog Offer is not an operative access policy. Its Promise may be inspected, but `Out`
derives no atoms from the Offer. Acceptance materializes a separate Agreement with explicit,
Agreement-local identifiers.

## Source Offer

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:CloudProvider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:ProductionService a rl2:Asset .

ex:issueServiceCredit a rl2:Action .
ex:monthlyUptimeOperand a rl2:LeftOperand ;
    rdfs:range xsd:decimal ;
    rl2:resolutionPath "asset.metadata.monthlyUptime" .

ex:uptimeMeetsSLA a rl2:AtomicConstraint ;
    rl2:leftOperand ex:monthlyUptimeOperand ;
    rl2:constraintOperator rl2:gte ;
    rl2:rightOperand "99.9"^^xsd:decimal .

ex:uptimePromise a rl2:Promise ;
    rl2:promisor ex:CloudProvider ;
    rl2:promisee ex:Customer ;
    rl2:promisedState ex:uptimeMeetsSLA ;
    rl2:object ex:ProductionService .

ex:creditDuty a rl2:Duty ;
    rl2:subject ex:CloudProvider ;
    rl2:counterparty ex:Customer ;
    rl2:action ex:issueServiceCredit ;
    rl2:object ex:ProductionService ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:uptimePromise ;
        rl2:leftOperand rl2:promiseStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:uptimeOffer a rl2:Offer ;
    rl2:grantor ex:CloudProvider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:uptimePromise, ex:creditDuty .
```

## Acceptance value

```text
Acceptance(
  agreementId = ex:uptimeAgreement,
  grantor      = ex:CloudProvider,
  grantee      = ex:Customer,
  primaryIds   = {
    ex:uptimePromise -> ex:uptimeDuty,
    ex:creditDuty    -> ex:creditDuty_A1
  },
  claimIds     = { ex:uptimePromise -> ex:uptimeClaim },
  objectBindings = {},
  dutyWindows  = {
    ex:uptimePromise -> [2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z)
  }
)
```

## Materialized Agreement

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:CloudProvider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:ProductionService a rl2:Asset .
ex:issueServiceCredit a rl2:Action .

ex:monthlyUptimeOperand a rl2:LeftOperand ;
    rdfs:range xsd:decimal ;
    rl2:resolutionPath "asset.metadata.monthlyUptime" .

ex:uptimeMeetsSLA a rl2:AtomicConstraint ;
    rl2:leftOperand ex:monthlyUptimeOperand ;
    rl2:constraintOperator rl2:gte ;
    rl2:rightOperand "99.9"^^xsd:decimal .

ex:uptimeDuty a rl2:Duty ;
    rl2:subject ex:CloudProvider ;
    rl2:counterparty ex:Customer ;
    rl2:object ex:ProductionService ;
    rl2:invariant ex:uptimeMeetsSLA ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2026-07-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2026-08-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:uptimeClaim a rl2:Claim ;
    rl2:subject ex:Customer ;
    rl2:counterparty ex:CloudProvider ;
    rl2:correlativeTo ex:uptimeDuty .

ex:creditDuty_A1 a rl2:Duty ;
    rl2:subject ex:CloudProvider ;
    rl2:counterparty ex:Customer ;
    rl2:action ex:issueServiceCredit ;
    rl2:object ex:ProductionService ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:uptimeDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated
    ] .

ex:uptimeAgreement a rl2:Agreement ;
    rl2:grantor ex:CloudProvider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:uptimeDuty, ex:uptimeClaim, ex:creditDuty_A1 ;
    prov:wasDerivedFrom ex:uptimeOffer .
```

The transformation changes both parts of the Promise-status query: `targetNorm` now identifies
the crystallized Duty and `promiseStateOperand` becomes `obligationStateOperand`. It copies the
sibling Duty under a new identifier and preserves the Promise's state condition as the
Maintenance Duty's `invariant`; it does not invent a `maintainUptime` action.

## Expected transformation result

| Observation | Expected value |
|---|---|
| Source Offer passed directly to `Out` | Empty envelope |
| Transformation result | `Materialized(ex:uptimeAgreement, sourceMap)` |
| Source-map entry for `ex:uptimePromise` | `ex:uptimeDuty` |
| Source-map entry for `ex:creditDuty` | `ex:creditDuty_A1` |
| Promise clauses in Agreement | None |
| Snapshot or runtime effects read/emitted | None |

General `promisedDuty` suretyship, a missing promised-state object, conflicting parties, duplicate
output identifiers, or a Promise-targeted `promisorOperand` query yields `Rejected(errors)` and no
partial Agreement.
