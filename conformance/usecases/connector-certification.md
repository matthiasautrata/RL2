# Use Case 32: Connector Certification

**Pattern:** Access via certified component  
**Vocabulary Demonstrated:** Profile operand for certification status  
**Category:** EU Data Spaces, IDS  
**Status:** DRAFT

---

## Business Context

In federated data spaces (IDS, Gaia-X), data exchange occurs through certified **connectors** — software components that enforce policies. Access is only permitted through connectors with valid certification.

This ensures:
- Technical security standards are met
- Policy enforcement is reliable
- Audit capabilities are present
- Interoperability is guaranteed

## Scenario

A data provider in the Mobility Data Space will only share traffic data with consumers whose IDS Connector has valid certification:

> "Data exchange is permitted only through connectors with current IDS certification at level 'Trust' or higher."

## Policy Intent

> "Access is PERMITTED only if the requesting connector holds valid certification."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Certified component | IDS Connector, Gaia-X node |
| Certification levels | Base, Trust, Trust+ |
| Validity | Time-limited, must be current |
| Issuer | Recognized certification body |

## IDS Reference Architecture

The IDS-RAM defines:
- **Connector:** Component for data exchange
- **Certification:** Attestation of security/compliance
- **Certification Authority:** Issues certifications
- **DAPS:** Dynamic Attribute Provisioning Service (validates tokens)

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Exchange Data                            │
│  ─────────────────────────────────────────────────  │
│  Subject: Data Consumer (via Connector)              │
│  Action: retrieve                                    │
│  Object: Traffic Data                                │
│  Condition:                                          │
│    connector.certification.level ∈ {Trust, Trust+}   │
│    AND connector.certification.validUntil > now      │
└─────────────────────────────────────────────────────┘
```

## Certification Levels

| Level | Requirements | Typical Use |
|-------|--------------|-------------|
| **Base** | Self-declaration | Development, testing |
| **Trust** | Third-party audit | Production (standard) |
| **Trust+** | Enhanced audit + continuous monitoring | High-sensitivity data |

## Evaluation Logic

```
Request: Consumer C via Connector K wants data D

1. Extract K's certification from request/token
2. Verify certification:
   - Issued by recognized authority?
   - Level meets minimum requirement?
   - Not expired?
   - Not revoked?
3. If all verified → Continue with other policy checks
   If any fail → DENY with certification error
```

## DAPS Integration

In IDS, certification is typically verified via DAPS tokens:

```json
{
  "iss": "https://daps.mobility-dataspace.eu",
  "sub": "connector-12345",
  "certificationLevel": "idsc:TRUST",
  "validUntil": "2025-12-31T23:59:59Z"
}
```

The policy checks claims in the token.

## Profile Requirements

```turtle
@prefix ids: <https://example.org/profile/ids#> .

ids:connectorCertLevelOperand a rl2:LeftOperand ;
    rdfs:label "Connector Certification Level" ;
    rl2:resolutionPath "context.connector.certification.level" .

ids:connectorCertValidUntilOperand a rl2:LeftOperand ;
    rdfs:label "Certification Valid Until" ;
    rl2:resolutionPath "context.connector.certification.validUntil" .

ids:connectorIdOperand a rl2:LeftOperand ;
    rdfs:label "Connector ID" ;
    rl2:resolutionPath "context.connector.id" .

# Certification levels
ids:Base a ids:CertificationLevel .
ids:Trust a ids:CertificationLevel .
ids:TrustPlus a ids:CertificationLevel .
```

---

## RL2 Model

This model demonstrates a Privilege gated on the requesting
connector's certification level (whitelist via `isAnyOf`) and its
certification not yet having expired (`gt` against the current
request time).

```turtle
@prefix ex: <https://example.org/> .
@prefix ids: <https://example.org/profile/ids#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ── Acceptable certification levels (whitelist) ──────────────────
ids:AcceptedCertificationLevels a rl2:AssetCollection ;
    rdfs:label "Accepted Certification Levels" ;
    rl2:member ids:Trust, ids:TrustPlus .

ex:requestTimeOperand a rl2:LeftOperand ;
    rdfs:label "Request Time" ;
    rl2:resolutionPath "context.request.time" ;
    rdfs:range xsd:dateTime .

# ── Privilege: exchange data via a certified, current connector ──
ex:exchangeDataPrivilege a rl2:Privilege ;
    rl2:subject ex:DataConsumer ;
    rl2:action ex:retrieve ;
    rl2:object ex:TrafficData ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand ids:connectorCertLevelOperand ;
            rl2:constraintOperator rl2:isAnyOf ;
            rl2:rightOperandRef ids:AcceptedCertificationLevels
        ] ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand ids:connectorCertValidUntilOperand ;
            rl2:constraintOperator rl2:gt ;
            rl2:rightOperandRef ex:requestTimeOperand
        ]
    ] .

ex:retrieve a rl2:Action ;
    rdfs:label "Retrieve" .

ex:mobilityDataSpacePolicy a rl2:Set ;
    rl2:grantor ex:DataProvider ;
    rl2:clause ex:exchangeDataPrivilege .
```

---

## References

- IDS Reference Architecture Model 4.0
- IDS Certification Scheme
- Gaia-X Trust Framework
- Eclipse Dataspace Connector documentation
