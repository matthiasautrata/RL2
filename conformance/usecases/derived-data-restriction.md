# Derived Data Restriction

## Scenario

A bank may distribute a market indicator derived from licensed data only where the indicator cannot reconstruct or substitute for the source data.

## Why it matters

Whether a derivative is externally distributable is often determined by a documented assessment. RL2 makes that assessment an attributed snapshot fact rather than embedding an undefined test in policy prose.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Vendor a rl2:Agent .
ex:Bank a rl2:Agent .
ex:MarketIndicator a rl2:Asset .
ex:distribute a rl2:Action .
ex:nonReconstructing a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "asset.assessment.nonReconstructing" .

ex:distributeSafeDerivative a rl2:Privilege ;
    rl2:subject ex:Bank ; rl2:action ex:distribute ; rl2:object ex:MarketIndicator ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:nonReconstructing ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:derivativeAgreement a rl2:Agreement ;
    rl2:grantor ex:Vendor ; rl2:grantee ex:Bank ; rl2:clause ex:distributeSafeDerivative .
```

## Request and snapshot

Request: `(Bank, distribute, MarketIndicator)`.

World snapshot: `asset.assessment.nonReconstructing = true`, attributed to the vendor-approved assessment process.

## Expected result

Expected decision: `Permit`. A false, missing, invalid, or conflicting assessment does not establish this privilege; the latter three yield an attributed indeterminate result where applicable.
