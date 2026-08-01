# Ethics Approval

## Scenario

Any agent may access a sensitive dataset only when an ethics-board approval in the snapshot
identifies that agent and remains in force. The policy names no specific researcher; the
population is delimited entirely by the approval fact.

## Why it matters

Approval is external state, not a mutable property of a policy. `rl2:subject rl2:anyAgent`
matches every requesting agent; the `agent.ethicsApprovalValid` condition, scoped to the
requester, correctly delimits the population to approved agents only.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:SensitiveDataset a rl2:Asset .
ex:access a rl2:Action .

ex:approvalValid a rl2:LeftOperand ;
    rdfs:range <http://www.w3.org/2001/XMLSchema#boolean> ;
    rl2:resolutionPath "agent.ethicsApprovalValid" .

ex:datasetAccessPrivilege a rl2:Privilege ;
    rl2:subject rl2:anyAgent ;
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

Alice’s request is `Permit` — `rl2:anyAgent` matches her as subject, and her scoped approval fact
satisfies the condition. An agent whose scoped `agent.ethicsApprovalValid` fact is `false` or
absent-but-defaulted does not satisfy the condition, so the Privilege does not grant and the
request is `NotApplicable` (no other clause applies). Were the approval fact missing from the
snapshot entirely, the condition would be `Unknown`, and the result would be `Indeterminate`, not
`Permit` or `NotApplicable`.
