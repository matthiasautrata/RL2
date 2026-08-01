# Fulfillment Evidence

## Scenario

A provider must deliver a report by the end of a stated interval. The evaluator derives the
Duty’s status from qualifying evidence in the supplied world snapshot; it does not maintain a
stored requirement record or mutate a fulfillment flag.

## Why it matters

The status is reproducible from explicit evidence and time boundaries.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:MonthlyReport a rl2:Asset .
ex:deliver a rl2:Action .

ex:deliverReport a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:counterparty ex:Customer ;
    rl2:action ex:deliver ;
    rl2:object ex:MonthlyReport ;
    rl2:dutyWindow [
        a rl2:DutyWindow ;
        rl2:startInclusive "2026-08-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2026-09-01T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:terms a rl2:Agreement ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Customer ;
    rl2:clause ex:deliverReport .
```

## Request and snapshot

The request is unrelated to Duty status. The snapshot contains evaluation time and, when delivery
occurred, Evidence with actor `Provider`, action `deliver`, object `MonthlyReport`, an occurrence
inside the window, and admissible attribution.

## Expected result

Qualifying evidence produces `Known(Fulfilled)`. Without it the Duty is `Known(Active)` while the
window is open and `Known(Violated)` once it closes.
