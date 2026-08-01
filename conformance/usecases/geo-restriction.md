# Geographic Restriction

## Scenario

A provider permits a customer to access a dataset only from approved jurisdictions.

## Why it matters

Jurisdiction is a fact supplied in the evaluation snapshot, not an implicit property of a network address. The profile defines how the deployment establishes that fact.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Customer a rl2:Agent .
ex:Dataset a rl2:Asset .
ex:access a rl2:Action .
ex:jurisdiction a rl2:LeftOperand ;
    rdfs:range xsd:string ;
    rl2:resolutionPath "context.requestJurisdiction" .

ex:euAccess a rl2:Privilege ;
    rl2:subject ex:Customer ; rl2:action ex:access ; rl2:object ex:Dataset ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:jurisdiction ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand "EU" ] .

ex:regionalAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Customer ; rl2:clause ex:euAccess .
```

## Request and snapshot

Request: `(Customer, access, Dataset)`.

World snapshot: `context.requestJurisdiction = "EU"`, attributed to the deployment’s jurisdiction determination service.

## Expected result

Expected decision: `Permit`. A non-EU value does not establish this privilege.
