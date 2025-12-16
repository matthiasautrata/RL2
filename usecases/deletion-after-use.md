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

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate event-triggered deletion Duty
```

---

## References

- IDS Policy Patterns — Delete after use
- GDPR Article 5(1)(e) — Storage limitation
- Secure data destruction standards
