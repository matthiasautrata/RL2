# Time-window Access

## Scenario

A researcher may access a health dataset during a defined study period.

## Why it matters

A half-open temporal interval has an unambiguous boundary: the start is included and the end is excluded.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Researcher a rl2:Agent .
ex:HealthDataset a rl2:Asset .
ex:access a rl2:Action .

ex:studyAccess a rl2:Privilege ;
    rl2:subject ex:Researcher ; rl2:action ex:access ; rl2:object ex:HealthDataset ;
    rl2:condition [ a rl2:LogicalConstraint ; rl2:constraintOperator rl2:and ;
        rl2:operand [ a rl2:AtomicConstraint ; rl2:leftOperand rl2:currentDateTime ;
            rl2:constraintOperator rl2:gte ; rl2:rightOperand "2026-01-01T00:00:00Z"^^xsd:dateTimeStamp ] ;
        rl2:operand [ a rl2:AtomicConstraint ; rl2:leftOperand rl2:currentDateTime ;
            rl2:constraintOperator rl2:lt ; rl2:rightOperand "2027-01-01T00:00:00Z"^^xsd:dateTimeStamp ]
    ] .

ex:studyAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Researcher ; rl2:clause ex:studyAccess .
```

## Request and snapshot

Request: `(Researcher, access, HealthDataset)`.

World snapshot time: `2026-06-15T10:00:00Z`.

## Expected result

Expected decision: `Permit`. At exactly `2027-01-01T00:00:00Z`, the privilege is no longer applicable.
