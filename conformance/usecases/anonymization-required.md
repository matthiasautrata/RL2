# Anonymization Required

## Scenario

A research institution may process a patient dataset only after the dataset has been anonymized to the agreed standard.

## Why it matters

Anonymization is not inferred from a policy label. RL2 evaluates an attributed assessment in the immutable snapshot.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Hospital a rl2:Agent .
ex:ResearchInstitution a rl2:Agent .
ex:PatientDataset a rl2:Asset .
ex:process a rl2:Action .
ex:anonymized a rl2:LeftOperand ;
    rl2:valueType xsd:boolean ;
    rl2:resolutionPath "asset.anonymization.approved" .

ex:processAnonymizedData a rl2:Privilege ;
    rl2:subject ex:ResearchInstitution ; rl2:action ex:process ; rl2:object ex:PatientDataset ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:anonymized ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:researchAgreement a rl2:Agreement ;
    rl2:grantor ex:Hospital ; rl2:grantee ex:ResearchInstitution ;
    rl2:clause ex:processAnonymizedData .
```

## Request and snapshot

Request: `(ResearchInstitution, process, PatientDataset)`.

World snapshot: `asset.anonymization.approved = true`, with evidence from the designated anonymization assessment.

## Expected result

Expected decision: `Permit`. A missing or disputed assessment is not silently treated as anonymization.
