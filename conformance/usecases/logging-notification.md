# Use Case 35: Logging and Notification

**Pattern:** Mandatory audit trail  
**Vocabulary Demonstrated:** `Duty` triggered by access  
**Category:** EU Data Spaces, Compliance  
**Status:** DRAFT

---

## Business Context

Data providers often require consumers to:

- **Log access:** Record who accessed what and when
- **Notify provider:** Inform provider of significant usage
- **Report periodically:** Submit usage reports

This supports audit, compliance, and billing.

## Scenario

A data exchange agreement requires:

> "Consumer shall maintain complete access logs and provide monthly usage reports to Provider. Consumer shall notify Provider within 24 hours of any security incident."

## Policy Intent

> "Access is PERMITTED but creates DUTY to log and notify."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Trigger | Each data access |
| Obligation | Log the access event |
| Notification | For specific conditions (incidents, thresholds) |
| Reporting | Periodic aggregate reports |

## Real-World Examples

### IDS Policy Patterns

"Logging" and "Notification" are documented IDS policy patterns.

### Market Data Licenses

Most require monthly usage reporting to vendors.

### GDPR Article 30

Requires records of processing activities.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Data                              │
│  ─────────────────────────────────────────────────  │
│  Subject: Consumer                                   │
│  Action: access                                      │
│  Object: Shared Data                                 │
└─────────────────────────────────────────────────────┘
            │
            │ triggers
            ▼
┌─────────────────────────────────────────────────────┐
│  Duty: Log Access                                    │
│  ─────────────────────────────────────────────────  │
│  Subject: Consumer                                   │
│  Action: logAccess                                   │
│  Object: Access Event                                │
│  Timing: Immediate (synchronous)                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Duty: Notify on Incident                            │
│  ─────────────────────────────────────────────────  │
│  Subject: Consumer                                   │
│  Action: notify                                      │
│  Counterparty: Provider                              │
│  Condition: securityIncident = true                  │
│  Deadline: 24 hours                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Duty: Submit Monthly Report                         │
│  ─────────────────────────────────────────────────  │
│  Subject: Consumer                                   │
│  Action: submitReport                                │
│  Counterparty: Provider                              │
│  Frequency: Monthly (by 5th of following month)      │
└─────────────────────────────────────────────────────┘
```

## Types of Logging/Notification

| Type | Trigger | Timing |
|------|---------|--------|
| **Access log** | Every access | Synchronous |
| **Anomaly alert** | Unusual pattern | Near-real-time |
| **Incident notification** | Security event | Within SLA |
| **Usage report** | End of period | Periodic |
| **Threshold alert** | Volume exceeded | When crossed |

## Log Content Requirements

| Field | Description |
|-------|-------------|
| Timestamp | When access occurred |
| Subject | Who accessed |
| Action | What was done |
| Object | What data |
| Outcome | Success/failure |
| Context | Purpose, application |

## Evaluation Logic

```
Action: Consumer accesses data

1. Evaluate access privilege → PERMIT/DENY
2. If PERMIT:
   - Create logging duty instance
   - Logging duty must be fulfilled (sync or async)
3. Check incident conditions:
   - If incident detected → Activate notification duty
4. Check reporting period:
   - If period ended → Activate reporting duty
```

## Profile Requirements

```turtle
@prefix audit: <https://example.org/profile/audit#> .

audit:logAccess a rl2:Action ;
    rdfs:label "Log Access Event" .

audit:notify a rl2:Action ;
    rdfs:label "Notify Provider" .

audit:submitReport a rl2:Action ;
    rdfs:label "Submit Usage Report" .

audit:isSecurityIncidentOperand a rl2:LeftOperand ;
    rl2:resolutionPath "context.securityIncident" ;
    rdfs:range xsd:boolean .

audit:reportingPeriodEndOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.reportingPeriod.end" .
```

---

## RL2 Model

This model demonstrates three Duties accompanying the access
Privilege: an unconditional logging Duty, an incident-triggered
notification Duty, and a period-end reporting Duty.

```turtle
@prefix ex: <https://example.org/> .
@prefix audit: <https://example.org/profile/audit#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ── Privilege: access the shared data ────────────────────────────
ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:Consumer ;
    rl2:action ex:access ;
    rl2:object ex:SharedData .

ex:access a rl2:Action ;
    rdfs:label "Access" .

# ── Duty: log every access, unconditionally ──────────────────────
ex:logAccessDuty a rl2:Duty ;
    rl2:subject ex:Consumer ;
    rl2:action audit:logAccess ;
    rl2:object ex:AccessEvent ;
    rl2:counterparty ex:Provider .

# ── Duty: notify the provider within 24h of a security incident ──
ex:notifyIncidentDuty a rl2:Duty ;
    rl2:subject ex:Consumer ;
    rl2:action audit:notify ;
    rl2:object ex:SecurityIncident ;
    rl2:counterparty ex:Provider ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand audit:isSecurityIncidentOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand "true"^^xsd:boolean
    ] .

# ── Duty: submit a usage report once the reporting period ends ──
ex:reportingDuty a rl2:Duty ;
    rl2:subject ex:Consumer ;
    rl2:action audit:submitReport ;
    rl2:object ex:UsageReport ;
    rl2:counterparty ex:Provider ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:currentDateOperand ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperandRef audit:reportingPeriodEndOperand
    ] .

ex:currentDateOperand a rl2:LeftOperand ;
    rdfs:label "Current Date" ;
    rl2:resolutionPath "context.now" .

ex:dataExchangeAgreement a rl2:Agreement ;
    rl2:grantor ex:Provider ;
    rl2:grantee ex:Consumer ;
    rl2:clause ex:accessPrivilege, ex:logAccessDuty, ex:notifyIncidentDuty, ex:reportingDuty .
```

---

## References

- IDS Policy Patterns — Logging, Notification
- GDPR Article 30 — Records of processing
- SOC 2 — Logging requirements
- Market data vendor reporting requirements
