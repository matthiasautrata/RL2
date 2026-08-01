# Concurrent Seats

## Scenario

A licensed user may start a session while a snapshot reports fewer than fifty active seats. At capacity, starting a session is prohibited.

## Why it matters

The policy makes a capacity decision from an attributed snapshot. It does not reserve a seat, update a counter, or resolve concurrent admissions; those effects require an implementation-level coordination mechanism.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:LicensedUser a rl2:Agent .
ex:Application a rl2:Asset .
ex:startSession a rl2:Action .

ex:activeSeatCount a rl2:LeftOperand ;
    rdfs:range xsd:integer ;
    rl2:resolutionPath "state.licence.activeSeatCount" .

ex:seatAvailablePrivilege a rl2:Privilege ;
    rl2:subject ex:LicensedUser ;
    rl2:action ex:startSession ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:activeSeatCount ;
        rl2:constraintOperator rl2:lt ;
        rl2:rightOperand 50
    ] .

ex:capacityProhibition a rl2:Prohibition ;
    rl2:subject ex:LicensedUser ;
    rl2:prohibitedAction ex:startSession ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:activeSeatCount ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand 50
    ] .

ex:seatPolicy a rl2:Set ;
    rl2:clause ex:seatAvailablePrivilege, ex:capacityProhibition .
```

## Request and snapshot

Request: `(agent = LicensedUser, action = startSession, asset = Application)`.

World snapshot: `state.licence.activeSeatCount` is `49` or `50`, supplied by the licence service with its evidence provenance.

## Expected result

At `49`, the request is `Permit`; at `50`, it is `Deny`. A `Permit` is a policy decision, not a reservation or a guarantee that a later admission will succeed.
