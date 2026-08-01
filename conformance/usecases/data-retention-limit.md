# Data Retention Limit

## Scenario

A customer may retain a supplied dataset until a specified expiry and must delete it afterwards.

## Why it matters

The access restriction and the deletion obligation are separate norms. A condition on the access privilege does not itself establish that deletion occurred.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:Dataset a rl2:Asset .
ex:retain a rl2:Action .
ex:delete a rl2:Action .

ex:retentionUntil2027 a rl2:Privilege ;
    rl2:subject ex:Customer ; rl2:action ex:retain ; rl2:object ex:Dataset ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand rl2:currentDateTime ;
        rl2:constraintOperator rl2:lt ; rl2:rightOperand "2027-01-01T00:00:00Z"^^xsd:dateTimeStamp ] .
ex:deleteAfterRetention a rl2:Duty ;
    rl2:subject ex:Customer ; rl2:action ex:delete ; rl2:object ex:Dataset ;
    rl2:counterparty ex:Provider ;
    rl2:dutyWindow [ a rl2:DutyWindow ;
        rl2:startInclusive "2027-01-01T00:00:00Z"^^xsd:dateTimeStamp ;
        rl2:endExclusive "2027-01-02T00:00:00Z"^^xsd:dateTimeStamp ] .

ex:retentionAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Customer ;
    rl2:clause ex:retentionUntil2027, ex:deleteAfterRetention .
```

## Request and snapshot

Request: `(Customer, retain, Dataset)`.

World snapshot time: `2026-12-31T12:00:00Z`.

## Expected result

Expected decision: `Permit`. At `2027-01-01T00:00:00Z`, the retention privilege is inapplicable and the deletion duty enters its assessment window. Its status depends on supplied deletion evidence.
