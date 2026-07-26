# Use Case 36: Deletion After Use

**Pattern:** Post-processing deletion duty  
**Vocabulary Demonstrated:** Triggered `Duty`, event-based activation  
**Category:** EU Data Spaces, Data Contracts  
**Status:** DRAFT

---

## Business Context

Some data is provided for one-time or limited use:

- Process once, then delete
- Use for specific task, then delete
- Retain only for analysis duration

The data must not persist beyond its intended purpose.

## Scenario

A logistics company receives shipment data for route optimization:

> "Recipient may process Data for route optimization only. Upon completion of optimization, Recipient shall delete all copies of Data within 24 hours."

## Policy Intent

> "Data may be used for [specific purpose]. Upon completion, data MUST be deleted."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Trigger | Completion of permitted use |
| Obligation | Delete all copies |
| Deadline | Fixed period after trigger |
| Evidence | Deletion confirmation required |

## Real-World Examples

### IDS Policy Patterns

"Delete after use" is a documented IDS usage control pattern.

### GDPR Minimization

Data should be deleted when no longer necessary for original purpose.

### Clinical Trials

Analysis data often must be deleted post-study (unless retention required).

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Process Data                             │
│  ─────────────────────────────────────────────────  │
│  Subject: Recipient                                  │
│  Action: processForOptimization                      │
│  Object: Shipment Data                               │
└─────────────────────────────────────────────────────┘
            │
            │ upon completion
            ▼
┌─────────────────────────────────────────────────────┐
│  Event: Processing Complete                          │
│  ─────────────────────────────────────────────────  │
│  operationalAgent: Recipient                         │
│  eventTime: [when processing finished]               │
└─────────────────────────────────────────────────────┘
            │
            │ triggers
            ▼
┌─────────────────────────────────────────────────────┐
│  Duty: Delete Data                                   │
│  ─────────────────────────────────────────────────  │
│  Subject: Recipient                                  │
│  Action: delete                                      │
│  Object: All copies of Shipment Data                 │
│  Condition: processingComplete event exists          │
│  Deadline: 24 hours after processingComplete         │
│  State: Pending → Active → Fulfilled/Violated        │
└─────────────────────────────────────────────────────┘
```

## State Transitions

```
Data Received          Processing Done           24h Later
      │                       │                      │
      ▼                       ▼                      ▼
┌───────────┐           ┌──────────┐          ┌───────────┐
│ Can Use   │──process─▶│ Complete │──delete?─▶│ Fulfilled │
│ (no duty) │           │ (active) │          └───────────┘
└───────────┘           └────┬─────┘                │
                             │                      │
                             │ no delete            │
                             ▼                      ▼
                        ┌──────────┐          ┌──────────┐
                        │ Violated │          │ Violated │
                        └──────────┘          └──────────┘
```

## "Use" Definitions

What constitutes "completion of use"?

| Definition | Trigger |
|------------|---------|
| Single processing run | Process completes |
| Purpose fulfilled | Business goal achieved |
| Time window | Fixed period expires |
| Explicit declaration | User marks complete |

## Technical Enforcement

Deletion may be enforced technically:
- Encrypted data with key destruction
- Self-destructing containers
- Remote wipe capabilities
- Timed access tokens

## Profile Requirements

```turtle
@prefix lifecycle: <https://example.org/profile/lifecycle#> .

lifecycle:processingCompleteOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.processingStatus.complete" ;
    rdfs:range xsd:boolean .

lifecycle:processingCompleteTimeOperand a rl2:LeftOperand ;
    rl2:resolutionPath "state.processingStatus.completedAt" .

lifecycle:ProcessingComplete a rl2:Event .

lifecycle:delete a rl2:Action ;
    rdfs:label "Delete All Copies" .
```

---

## RL2 Model

This model demonstrates a Privilege to process data for a stated
purpose, and a downstream Duty to delete all copies once the
processing-complete Event has occurred.

```turtle
@prefix ex: <https://example.org/> .
@prefix lifecycle: <https://example.org/profile/lifecycle#> .
@prefix rl2: <https://rl2.example/ontology#> .

# ── Privilege: process for route optimization ────────────────────
ex:processPrivilege a rl2:Privilege ;
    rl2:subject ex:Recipient ;
    rl2:action ex:processForOptimization ;
    rl2:object ex:ShipmentData .

ex:processForOptimization a rl2:Action ;
    rdfs:label "Process for Route Optimization" .

# ── Duty: delete all copies once processing is complete ──────────
ex:deleteDataDuty a rl2:Duty ;
    rl2:subject ex:Recipient ;
    rl2:action lifecycle:delete ;
    rl2:object ex:ShipmentData ;
    rl2:counterparty ex:LogisticsCompany ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent lifecycle:ProcessingComplete
    ] .

ex:dataSharingAgreement a rl2:Agreement ;
    rl2:grantor ex:LogisticsCompany ;
    rl2:grantee ex:Recipient ;
    rl2:clause ex:processPrivilege, ex:deleteDataDuty .
```

---

## References

- IDS Policy Patterns — Delete after use
- GDPR Article 5(1)(e) — Storage limitation
- Secure data destruction standards
