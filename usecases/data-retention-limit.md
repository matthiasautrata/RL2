# Use Case 28: Data Retention Limit

**Pattern:** Time-bound deletion obligation  
**Vocabulary Demonstrated:** Temporal `Duty`, deadline constraint  
**Category:** Data Contracts, Compliance  
**Status:** DRAFT

---

## Business Context

Data cannot be kept forever. Retention limits arise from:

- **License terms:** "Delete within 30 days of contract termination"
- **Privacy law:** GDPR storage limitation principle
- **Contractual:** Data sharing agreements with expiry
- **Security:** Minimize data exposure window

## Scenario

A research institution receives a dataset for a specific study. The data use agreement states:

> "Recipient shall delete all copies of the Data within 30 days of study completion or agreement termination, whichever occurs first."

## Policy Intent

> "Data MUST be deleted by the retention deadline. After deadline, possession is a violation."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Trigger | Contract end, study completion, or fixed date |
| Obligation | Delete all copies |
| Deadline | Fixed period after trigger |
| Evidence | Deletion certificate often required |

## Real-World Terms

### GDPR Article 5(1)(e)

> "Personal data shall be kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for which the personal data are processed."

### Research Data Agreements

Typical clause: "Upon expiration or termination, Recipient shall destroy or return all Data and certify destruction in writing."

### Market Data Licenses

Bloomberg/LSEG often specify retention limits for historical data snapshots.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Retain Data (during valid period)       │
│  ─────────────────────────────────────────────────  │
│  Subject: Recipient                                  │
│  Action: retain                                      │
│  Object: Dataset                                     │
│  Condition: currentDateTime ≤ retentionDeadline     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Duty: Delete Data (by deadline)                    │
│  ─────────────────────────────────────────────────  │
│  Subject: Recipient                                  │
│  Action: delete                                      │
│  Object: Dataset (all copies)                        │
│  Deadline: retentionDeadline                         │
│  State: Pending → Active (at deadline) → Fulfilled/Violated │
└─────────────────────────────────────────────────────┘
```

## State Transitions

```
Contract Start                    Deadline                Post-Deadline
     │                               │                         │
     ▼                               ▼                         ▼
┌─────────┐                   ┌─────────┐               ┌───────────┐
│ Pending │ ──deadline───────▶│ Active  │──deleted?────▶│ Fulfilled │
└─────────┘                   └────┬────┘               └───────────┘
                                   │
                                   │ not deleted
                                   ▼
                              ┌──────────┐
                              │ Violated │
                              └──────────┘
```

## Evaluation Logic

```
Given:
  - Current time T
  - Retention deadline D
  - Deletion status S

1. If T < D:
   - Retention privilege: ACTIVE
   - Deletion duty: PENDING
   
2. If T ≥ D:
   - Retention privilege: EXPIRED
   - Deletion duty: ACTIVE
   - If S = deleted → Duty FULFILLED
   - If S = not deleted → Duty VIOLATED
```

## Evidence Requirements

Deletion duties often require proof:

| Evidence Type | Description |
|---------------|-------------|
| Deletion certificate | Signed attestation |
| System logs | Automated deletion records |
| Audit trail | Third-party verification |
| Secure destruction | For physical media |

## Profile Requirements

```turtle
@prefix retention: <https://example.org/profile/retention#> .

retention:retentionDeadlineOperand a rl2:LeftOperand ;
    rdfs:label "Retention Deadline" ;
    rl2:resolutionPath "context.agreement.retentionDeadline" .

retention:deletionStatusOperand a rl2:LeftOperand ;
    rdfs:label "Deletion Status" ;
    rl2:resolutionPath "state.deletionRecord.status" .

retention:delete a rl2:Action ;
    rdfs:label "Delete" ;
    rdfs:comment "Permanently remove all copies of data." .

retention:certifyDeletion a rl2:Action ;
    rdfs:label "Certify Deletion" .
```

---

## RL2 Model

This model demonstrates the retention/deletion pair: a Privilege to
retain the data while the current time is still before the deadline,
and a Duty to delete it once that deadline has passed.

```turtle
@prefix ex: <https://example.org/> .
@prefix retention: <https://example.org/profile/retention#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:currentDateTimeOperand a rl2:LeftOperand ;
    rdfs:label "Current Date/Time" ;
    rl2:resolutionPath "context.now" ;
    rdfs:range xsd:dateTime .

# ── Privilege: retain data while before the deadline ─────────────
ex:retainPrivilege a rl2:Privilege ;
    rl2:subject ex:Recipient ;
    rl2:action ex:retain ;
    rl2:object ex:StudyDataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:currentDateTimeOperand ;
        rl2:constraintOperator rl2:lt ;
        rl2:rightOperandRef retention:retentionDeadlineOperand
    ] .

ex:retain a rl2:Action ;
    rdfs:label "Retain" .

# ── Duty: delete all copies once the deadline has passed ─────────
ex:deleteDataDuty a rl2:Duty ;
    rl2:subject ex:Recipient ;
    rl2:action retention:delete ;
    rl2:object ex:StudyDataset ;
    rl2:counterparty ex:ResearchInstitution ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:currentDateTimeOperand ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperandRef retention:retentionDeadlineOperand
    ] .

ex:dataUseAgreement a rl2:Agreement ;
    rl2:grantor ex:ResearchInstitution ;
    rl2:grantee ex:Recipient ;
    rl2:clause ex:retainPrivilege, ex:deleteDataDuty .
```

---

## References

- GDPR Article 5(1)(e) — Storage limitation
- NIST SP 800-88 — Media sanitization guidelines
- Standard research data use agreements
