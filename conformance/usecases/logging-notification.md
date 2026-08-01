# Logging and Incident Notification

## Scenario

A consumer may access shared data and owes the provider a usage record. If the supplied snapshot establishes a security incident, the consumer must notify the provider.

## Why it matters

RL2 can express the duties and classify them from snapshot evidence. It does not prescribe log transport, alert delivery, or incident-management workflow.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Consumer a rl2:Agent .
ex:SharedData a rl2:Asset .
ex:access a rl2:Action .
ex:recordUsage a rl2:Action .
ex:notifyIncident a rl2:Action .
ex:securityIncident a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "global.securityIncident.confirmed" .

ex:accessSharedData a rl2:Privilege ;
    rl2:subject ex:Consumer ; rl2:action ex:access ; rl2:object ex:SharedData .
ex:recordUsageDuty a rl2:Duty ;
    rl2:subject ex:Consumer ; rl2:action ex:recordUsage ; rl2:object ex:SharedData ;
    rl2:counterparty ex:Provider .
ex:notifyIncidentDuty a rl2:Duty ;
    rl2:subject ex:Consumer ; rl2:action ex:notifyIncident ; rl2:object ex:SharedData ;
    rl2:counterparty ex:Provider ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:securityIncident ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:dataSharingAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:Consumer ;
    rl2:clause ex:accessSharedData, ex:recordUsageDuty, ex:notifyIncidentDuty .
```

## Request and snapshot

Request: `(Consumer, access, SharedData)`.

World snapshot: `global.securityIncident.confirmed = true`, attributed to the incident authority; supplied usage-record and notification evidence determine the duty statuses.

## Expected result

Expected decision: `Permit`; the incident-notification duty is applicable and its status is reported separately.
