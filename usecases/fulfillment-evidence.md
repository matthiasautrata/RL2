# Use Case 51: Fulfillment Evidence

**Pattern:** Audit trail for norm satisfaction  
**Vocabulary Demonstrated:** `rl2p:fulfillmentEvidence`, `rl2p:Requirement`  
**Category:** Protocol, Compliance  
**Status:** DRAFT

---

## Business Context

When a duty is fulfilled or a promise kept, there must be evidence:

- **Audit:** Prove compliance occurred
- **Dispute resolution:** Demonstrate performance
- **Regulatory:** Show controls operated
- **Contractual:** Verify SLA met

The protocol must capture *what* was done, *when*, *by whom*, and *how* it satisfies the norm.

## Scenario

A data contract requires the provider to refresh data every 6 hours. When the provider performs a refresh:

1. System records the refresh event
2. Links event to the freshness duty
3. Captures timestamp, actor, evidence hash
4. Duty transitions to Fulfilled with evidence attached

Later, during an audit, the consumer can verify the provider met their obligations.

## Policy Intent

> "All duty fulfillments must be recorded with verifiable evidence."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| What | Action performed |
| When | Timestamp |
| Who | Performing agent |
| How | Evidence (hash, receipt, log) |
| Link | Reference to satisfied norm |

## Protocol Vocabulary

From RL2_Protocol.md:

```turtle
rl2p:Requirement a rdfs:Class ;
    rdfs:comment "Runtime tracking of normative requirements." .

rl2p:fulfillmentEvidence a rdf:Property ;
    rdfs:domain rl2p:Requirement ;
    rdfs:comment "Evidence that the requirement was satisfied." .

rl2p:requirementStatus a rdf:Property ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range rl2:ObligationState .

rl2p:satisfiedAt a rdf:Property ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range xsd:dateTime .

rl2p:satisfiedBy a rdf:Property ;
    rdfs:domain rl2p:Requirement ;
    rdfs:range rl2:Agent .
```

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Duty: Refresh Data                                  │
│  ─────────────────────────────────────────────────  │
│  Subject: Provider                                   │
│  Action: refreshData                                 │
│  Object: Dataset                                     │
│  Recurrence: Every 6 hours                           │
└─────────────────────────────────────────────────────┘
            │
            │ tracked by
            ▼
┌─────────────────────────────────────────────────────┐
│  Requirement (runtime instance)                      │
│  ─────────────────────────────────────────────────  │
│  sourceNorm: ex:refreshDuty                          │
│  status: Fulfilled                                   │
│  satisfiedAt: 2025-01-15T14:30:00Z                   │
│  satisfiedBy: ex:DataProvider                        │
│  fulfillmentEvidence: ex:refreshEvent123             │
└─────────────────────────────────────────────────────┘
            │
            │ points to
            ▼
┌─────────────────────────────────────────────────────┐
│  Evidence: Refresh Event                             │
│  ─────────────────────────────────────────────────  │
│  eventType: DataRefresh                              │
│  timestamp: 2025-01-15T14:30:00Z                     │
│  actor: ex:DataProvider                              │
│  asset: ex:CustomerDataset                           │
│  recordCount: 1,250,000                              │
│  checksum: sha256:a1b2c3...                          │
└─────────────────────────────────────────────────────┘
```

## Evidence Types

| Type | Use Case | Content |
|------|----------|---------|
| Event record | Action performed | Timestamp, actor, details |
| Hash/checksum | Data integrity | SHA-256 of delivered data |
| Receipt | Acknowledgment | Signed confirmation |
| Log entry | System action | Structured log record |
| Attestation | Third-party | Auditor certification |

## Evaluation Logic

```
Duty fulfillment flow:

1. Agent performs action (refreshData)
2. System captures evidence:
   - Create Evidence record
   - Record timestamp, actor, details
3. System updates Requirement:
   - Set status = Fulfilled
   - Set satisfiedAt = now
   - Set satisfiedBy = actor
   - Set fulfillmentEvidence = evidence IRI
4. Evidence available for audit queries
```

## Audit Queries

With fulfillment evidence, auditors can query:

```sparql
# Find all fulfillments for a duty in date range
SELECT ?req ?satisfiedAt ?evidence
WHERE {
    ?req rl2p:sourceNorm ex:refreshDuty ;
         rl2p:requirementStatus rl2:Fulfilled ;
         rl2p:satisfiedAt ?satisfiedAt ;
         rl2p:fulfillmentEvidence ?evidence .
    FILTER (?satisfiedAt >= "2025-01-01"^^xsd:date)
}

# Find unfulfilled duties
SELECT ?req ?norm
WHERE {
    ?req rl2p:sourceNorm ?norm ;
         rl2p:requirementStatus rl2:Active .
}
```

## Tamper Evidence

For high-assurance scenarios:

```turtle
ex:refreshEvidence123 a rl2p:FulfillmentEvidence ;
    rl2p:evidenceHash "sha256:a1b2c3d4..."^^xsd:string ;
    rl2p:signedBy ex:DataProvider ;
    rl2p:signature "base64:..."^^xsd:string ;
    rl2p:witnessedBy ex:AuditService .
```

## Comparison with Related Use Cases

| Use Case | Focus |
|----------|-------|
| runtime-evaluation (50) | Requirement creation and tracking |
| **fulfillment-evidence** | Proof of satisfaction |
| audit-trail (10) | Prerequisite pattern |
| data-freshness-promise (11) | Promise with violation |

## Profile Requirements

```turtle
@prefix audit: <https://example.org/profile/audit#> .

audit:FulfillmentEvidence a rdfs:Class ;
    rdfs:subClassOf rl2p:Evidence .

audit:evidenceHash a rdf:Property ;
    rdfs:domain audit:FulfillmentEvidence ;
    rdfs:range xsd:string .

audit:signedBy a rdf:Property ;
    rdfs:domain audit:FulfillmentEvidence ;
    rdfs:range rl2:Agent .
```

---

## RL2 Model

This model demonstrates a Duty tracked at runtime by a
`rl2p:Requirement`, transitioning to `rl2:Fulfilled` once a refresh
occurs, with `rl2p:fulfillmentEvidence` pointing at the log entry
that substantiates the fulfillment.

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rl2p: <https://rl2.example/protocol#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ── Duty: refresh the dataset every 6 hours ──────────────────────
ex:refreshDuty a rl2:Duty ;
    rl2:subject ex:DataProvider ;
    rl2:action ex:refreshData ;
    rl2:object ex:CustomerDataset ;
    rl2:counterparty ex:Consumer .

ex:refreshData a rl2:Action ;
    rdfs:label "Refresh Data" .

ex:dataContract a rl2:Agreement ;
    rl2:grantor ex:DataProvider ;
    rl2:grantee ex:Consumer ;
    rl2:clause ex:refreshDuty .

# ── Runtime record: the duty was fulfilled, with evidence ────────
# ex:refreshEvent123 is the log entry IRI (1,250,000 records, sha256:a1b2c3...);
# fulfillmentEvidence is domain/range-unrestricted, so it is referenced directly.
ex:refreshRequirement a rl2p:Requirement ;
    rl2p:sourceNorm ex:refreshDuty ;
    rl2p:sourcePolicy ex:dataContract ;
    rl2p:requirementStatus rl2:Fulfilled ;
    rl2p:imposedTime "2025-01-15T08:30:00Z"^^xsd:dateTime ;
    rl2p:fulfillmentEvidence ex:refreshEvent123 .
```

---

## References

- RL2_Protocol.md — Protocol vocabulary
- SOX Section 404 — Audit trail requirements
- GDPR Article 5(2) — Accountability principle
- ISO 27001 — Information security audit trails
