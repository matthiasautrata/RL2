# Multi-level Approval

## Scenario

A bank employee may access customer transaction data for a new analytics project only after manager, data-owner, compliance, and security approvals are valid for that request.

## Why it matters

Approval workflow is outside core RL2. The policy consumes a verified, attributed fact that identifies the applicable approvals and their validity, enabling independent evaluators to reach the same result.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Bank a rl2:Agent .
ex:Employee a rl2:Agent .
ex:CustomerTransactions a rl2:Asset .
ex:access a rl2:Action .
ex:allApprovalsValid a rl2:LeftOperand ;
    rl2:valueType xsd:boolean ;
    rl2:resolutionPath "global.approvals.requiredSetValid" .

ex:approvedAccess a rl2:Privilege ;
    rl2:subject ex:Employee ; rl2:action ex:access ; rl2:object ex:CustomerTransactions ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:allApprovalsValid ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:analyticsAgreement a rl2:Agreement ;
    rl2:grantor ex:Bank ; rl2:grantee ex:Employee ; rl2:clause ex:approvedAccess .
```

## Request and snapshot

Request: `(Employee, access, CustomerTransactions)` for project `P`.

World snapshot: `global.approvals.requiredSetValid = true`, attributed to an approval service that verifies the four named approvers, their request binding, order where required, and expiry.

## Expected result

Expected decision: `Permit`. Missing, expired, or conflicting approval evidence does not establish the privilege.
