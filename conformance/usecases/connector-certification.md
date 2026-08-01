# Connector Certification

## Scenario

A data provider permits a consumer connector to receive data only while the connector’s required certification is valid.

## Why it matters

RL2 evaluates a certification fact supplied by a trusted registry; it does not prescribe certificate issuance or network attestation.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:ConsumerConnector a rl2:Agent .
ex:ProductionData a rl2:Asset .
ex:receive a rl2:Action .
ex:certificationValid a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "agent.connectorCertification.valid" .

ex:certifiedConnectorAccess a rl2:Privilege ;
    rl2:subject ex:ConsumerConnector ; rl2:action ex:receive ; rl2:object ex:ProductionData ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:certificationValid ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:connectorAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ; rl2:grantee ex:ConsumerConnector ;
    rl2:clause ex:certifiedConnectorAccess .
```

## Request and snapshot

Request: `(ConsumerConnector, receive, ProductionData)`.

World snapshot: `agent.connectorCertification.valid = true`, attributed to the certification registry for the requesting connector at the evaluation time.

## Expected result

Expected decision: `Permit`. An expired or absent certification does not establish the privilege.
