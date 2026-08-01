# Ethics Approval

## Scenario

A researcher may access a sensitive dataset only when an ethics-board approval in the snapshot identifies that researcher and remains in force.

## Why it matters

Approval is external state, not a mutable property of a policy. Agent scoping binds the verified
approval to the requester.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Researcher a rl2:Agent .
ex:SensitiveDataset a rl2:Asset .
ex:access a rl2:Action .

ex:approvalValid a rl2:LeftOperand ;
    rdfs:range <http://www.w3.org/2001/XMLSchema#boolean> ;
    rl2:resolutionPath "agent.ethicsApprovalValid" .

ex:datasetAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveDataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:approvalValid ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] .

ex:researchPolicy a rl2:Set ;
    rl2:clause ex:datasetAccessPrivilege .
```

## Request and snapshot

Request: `(agent = Alice, action = access, asset = SensitiveDataset)`.

World snapshot: the agent-scoped fact `agent.ethicsApprovalValid` is `true` for Alice, with the
required board attribution and validity interval.

## Expected result

Alice’s request is `Permit`. Another researcher's facts occupy a different scope. Expired or
missing approval data produces `Indeterminate`.
