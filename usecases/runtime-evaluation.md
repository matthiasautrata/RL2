# Use Case 50: Runtime Evaluation

**Pattern:** Evaluation trace and requirements  
**Vocabulary Demonstrated:** `rl2p:Requirement`, `rl2p:sourceNorm`, `rl2p:requirementStatus`  
**Category:** Protocol Demonstration  
**Status:** DRAFT

---

## Business Context

When a policy is evaluated at runtime, the result includes:

- **Decision:** Permit, Deny, or NotApplicable
- **Active requirements:** Duties/promises that must be fulfilled
- **Evidence needed:** What must be proven for fulfillment

The RL2 Protocol vocabulary (`rl2p:`) captures these runtime artifacts.

## Scenario

A user requests access to a dataset. The evaluation produces:

1. **Decision:** PermitWithObligations
2. **Requirements:**
   - Log the access (immediate)
   - Delete data within 30 days (deadline)
   - Submit usage report monthly (recurring)

## Policy Intent

> "Track runtime obligations and their fulfillment status."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Artifact | `rl2p:Requirement` |
| Source | Links to originating Duty/Promise |
| Status | Tracks lifecycle (Pending→Fulfilled/Violated) |
| Evidence | Records fulfillment proof |

## Protocol Structure

```
┌─────────────────────────────────────────────────────┐
│  Evaluation Request                                  │
│  ─────────────────────────────────────────────────  │
│  Agent: Researcher                                   │
│  Action: access                                      │
│  Object: Dataset                                     │
│  Time: 2025-01-15T10:00:00Z                         │
└─────────────────────────────────────────────────────┘
            │
            │ produces
            ▼
┌─────────────────────────────────────────────────────┐
│  Evaluation Result                                   │
│  ─────────────────────────────────────────────────  │
│  Decision: PermitWithObligations                     │
│  Active Requirements:                                │
│    - req:logging (Active, immediate)                 │
│    - req:deletion (Pending, 30-day deadline)         │
│    - req:reporting (Pending, monthly)                │
└─────────────────────────────────────────────────────┘
```

## Requirement Structure

```turtle
ex:loggingRequirement a rl2p:Requirement ;
    rl2p:sourceNorm ex:loggingDuty ;
    rl2p:sourcePolicy ex:dataUsePolicy ;
    rl2p:requirementStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    rl2p:requirementLabel "Log access event" .

ex:deletionRequirement a rl2p:Requirement ;
    rl2p:sourceNorm ex:deletionDuty ;
    rl2p:sourcePolicy ex:dataUsePolicy ;
    rl2p:requirementStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    rl2p:requirementLabel "Delete data" ;
    ex:deadline "2025-02-14T10:00:00Z"^^xsd:dateTime .
```

## Requirement Lifecycle

```
           ┌─────────┐
           │ Pending │ ← Created but not yet active
           └────┬────┘
                │ activation condition met
                ▼
           ┌─────────┐
           │ Active  │ ← Must be fulfilled
           └────┬────┘
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
  ┌───────────┐    ┌──────────┐
  │ Fulfilled │    │ Violated │
  └───────────┘    └──────────┘
```

## Universal Requirement

`rl2p:Requirement` tracks:
- **Duties:** Obligations from policy
- **Promises:** Voluntary commitments
- **Claims:** From the counterparty perspective

```turtle
# Duty-sourced requirement
ex:dutyReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:someDuty .

# Promise-sourced requirement (with counterparty = claim holder)
ex:promiseReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:somePromise ;
    rl2p:counterparty ex:Consumer .
```

## Evaluation Response Format

A complete evaluation response includes:

```turtle
ex:evaluationResult a rl2p:EvaluationResult ;
    rl2p:request ex:accessRequest ;
    rl2p:decision rl2p:PermitWithObligations ;
    rl2p:evaluatedAt "2025-01-15T10:00:05Z"^^xsd:dateTime ;
    rl2p:policyGeneration <https://example.org/policy/v4> ;
    rl2p:activeRequirements (
        ex:loggingRequirement
        ex:deletionRequirement
        ex:reportingRequirement
    ) .
```

## Profile Requirements

The protocol vocabulary is defined in `rl2p:` namespace. No additional profile needed.

```turtle
@prefix rl2p: <https://rl2.example/protocol#> .

# Core protocol classes and properties used:
# - rl2p:Requirement
# - rl2p:sourceNorm
# - rl2p:sourcePolicy
# - rl2p:requirementStatus
# - rl2p:imposedTime
# - rl2p:counterparty
# - rl2p:activeRequirements
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate rl2p:Requirement and related properties
```

---

## References

- RL2_Protocol.md — Protocol specification
- RL2_Vocabulary.md § 14 — Protocol vocabulary
- XACML — Obligations in response
