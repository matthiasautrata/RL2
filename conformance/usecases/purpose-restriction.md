# Purpose Restriction

## Scenario

A research institution may process a health dataset for epidemiological research, but not for unrelated purposes.

## Why it matters

Purpose is a policy-visible input. Declaring its resolution path makes two evaluators test the same supplied request context.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Institution a rl2:Agent .
ex:HealthDataset a rl2:Asset .
ex:process a rl2:Action .
ex:purpose a rl2:LeftOperand ; rl2:valueType xsd:string ; rl2:resolutionPath "context.purpose" .

ex:researchProcessing a rl2:Privilege ;
    rl2:subject ex:Institution ; rl2:action ex:process ; rl2:object ex:HealthDataset ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:purpose ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand "epidemiological-research" ] .

ex:researchAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Institution ; rl2:clause ex:researchProcessing .
```

## Request and snapshot

Request: `(Institution, process, HealthDataset)`.

World snapshot: `context.purpose = "epidemiological-research"`, supplied by the requesting application.

## Expected result

Expected decision: `Permit`. A request with another declared purpose is `NotApplicable` unless another norm applies.
