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
# The policy under evaluation and the duties it imposes
ex:dataUsePolicy a rl2:Policy ;
    rl2:clause ex:loggingDuty, ex:deletionDuty, ex:reportingDuty .

ex:loggingDuty a rl2:Duty ;
    rl2:subject ex:Researcher ; rl2:action ex:logAccess ; rl2:object ex:Dataset ;
    rl2:obligationState rl2:Active .
ex:deletionDuty a rl2:Duty ;
    rl2:subject ex:Researcher ; rl2:action ex:delete ; rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending .
ex:reportingDuty a rl2:Duty ;
    rl2:subject ex:Researcher ; rl2:action ex:submitReport ; rl2:object ex:Dataset ;
    rl2:obligationState rl2:Pending .

# Runtime requirements derived from those duties
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

ex:reportingRequirement a rl2p:Requirement ;
    rl2p:sourceNorm ex:reportingDuty ;
    rl2p:sourcePolicy ex:dataUsePolicy ;
    rl2p:requirementStatus rl2:Pending ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    rl2p:requirementLabel "Submit usage report" .
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
ex:someDuty a rl2:Duty ;
    rl2:subject ex:Researcher ; rl2:action ex:access ; rl2:object ex:Dataset .

# ex:dataUsePolicy also carries these two clauses (sourceNorm must be a clause of
# sourcePolicy — P3); ex:somePromise is declared below.
ex:dataUsePolicy rl2:clause ex:someDuty, ex:somePromise .

ex:dutyReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:someDuty ;
    rl2p:sourcePolicy ex:dataUsePolicy ;
    rl2p:requirementStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime .

# Promise-sourced requirement (with counterparty = claim holder)
ex:somePromise a rl2:Promise ;
    rl2:promisor ex:Provider ; rl2:promisee ex:Consumer ;
    rl2:promisedAction ex:maintainFreshness ; rl2:object ex:Dataset .

ex:promiseReq a rl2p:Requirement ;
    rl2p:sourceNorm ex:somePromise ;
    rl2p:sourcePolicy ex:dataUsePolicy ;
    rl2p:requirementStatus rl2:Active ;
    rl2p:imposedTime "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    rl2p:counterparty ex:Consumer .

# Runtime linkage: the Case whose evaluation surfaced these two Requirements (P3).
ex:universalRequest a rl2p:Request ;
    rl2p:requestedAction ex:access ;
    rl2p:requestedAsset ex:Dataset ;
    rl2p:requestingAgent ex:Researcher ;
    rl2p:requestTime "2025-01-15T10:00:00Z"^^xsd:dateTime .

ex:universalEvaluation a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:universalRequest ;
    rl2p:decision rl2p:PermitWithObligations ;
    rl2p:evaluationTime "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    rl2p:activeRequirements ex:dutyReq, ex:promiseReq .

ex:universalCase a rl2p:Case ;
    rl2p:initialRequest ex:universalRequest ;
    rl2p:caseStatus rl2p:CasePending ;
    rl2p:caseCreated "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    rl2p:evaluationHistory ex:universalEvaluation .
```

## Evaluation Response Format

A complete evaluation response includes:

```turtle
ex:accessRequest a rl2p:Request ;
    rl2p:requestedAction ex:access ;
    rl2p:requestedAsset ex:Dataset ;
    rl2p:requestingAgent ex:Researcher ;
    rl2p:requestTime "2025-01-15T10:00:00Z"^^xsd:dateTime .

ex:evaluationResult a rl2p:EvaluationResult ;
    rl2p:evaluatedRequest ex:accessRequest ;
    rl2p:decision rl2p:PermitWithObligations ;
    rl2p:evaluationTime "2025-01-15T10:00:05Z"^^xsd:dateTime ;
    rl2p:activeRequirements ex:loggingRequirement,
                            ex:deletionRequirement,
                            ex:reportingRequirement .
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

The `rl2p:Case` is the append-only record that ties the request to its evaluation
result and the generation under which it was decided.

```turtle
ex:accessCase a rl2p:Case ;
    rl2p:initialRequest ex:accessRequest ;
    rl2p:caseStatus rl2p:Approved ;
    rl2p:caseCreated "2025-01-15T10:00:00Z"^^xsd:dateTime ;
    rl2p:policyGeneration "https://example.org/policy/gen/2025-Q4"^^xsd:anyURI ;
    rl2p:evaluationHistory ex:evaluationResult .
```

---

## References

- RL2_Protocol.md — Protocol specification
- RL2_Vocabulary.md § 14 — Protocol vocabulary
- XACML — Obligations in response
