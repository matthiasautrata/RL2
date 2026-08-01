# Data Sovereignty

## Scenario

An automotive manufacturer shares production data with a supplier under agreed purpose, retention, and audit terms.

## Why it matters

The core meaning of data sovereignty is that use is governed by explicit, inspectable terms. RL2 evaluates those terms; external systems negotiate agreements, collect evidence, and enforce outcomes.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Manufacturer a rl2:Agent .
ex:Supplier a rl2:Agent .
ex:ProductionData a rl2:Asset .
ex:access a rl2:Action .
ex:submitUsageRecord a rl2:Action .
ex:purpose a rl2:LeftOperand ; rl2:valueType xsd:string ; rl2:resolutionPath "context.purpose" .

ex:productionSupportAccess a rl2:Privilege ;
    rl2:subject ex:Supplier ; rl2:action ex:access ; rl2:object ex:ProductionData ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:purpose ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand "production-support" ] .
ex:usageRecordDuty a rl2:Duty ;
    rl2:subject ex:Supplier ; rl2:action ex:submitUsageRecord ; rl2:object ex:ProductionData ;
    rl2:counterparty ex:Manufacturer .

ex:productionDataAgreement a rl2:Agreement ;
    rl2:grantor ex:Manufacturer ; rl2:grantee ex:Supplier ;
    rl2:clause ex:productionSupportAccess, ex:usageRecordDuty .
```

## Request and snapshot

Request: `(Supplier, access, ProductionData)`.

World snapshot: `context.purpose = "production-support"`.

## Expected result

Expected decision: `Permit`. The status output separately classifies the usage-record Duty;
amendment and revocation of the Agreement are outside the core evaluation contract.
