# Use Case 37: Time Window Access

**Pattern:** Temporal validity restriction  
**Vocabulary Demonstrated:** `effectiveFrom`/`effectiveTo` pattern, `currentDateTime`  
**Category:** EU Data Spaces, Data Contracts  
**Status:** DRAFT

---

## Business Context

Access rights are often time-bounded:

- **Project duration:** Access during project only
- **Contract term:** Valid from signing to termination
- **Market hours:** Access during trading hours only
- **Subscription period:** Monthly/annual subscriptions

## Scenario

A research project has access to healthcare data for the study period:

> "Access is permitted from January 1, 2025 through December 31, 2026. Upon expiration, all access privileges terminate automatically."

## Policy Intent

> "Access is PERMITTED only during the defined time window."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Start | Effective from date/time |
| End | Effective to date/time |
| Automatic | No manual intervention needed |
| Inclusive | May include start, exclude end |

## Real-World Examples

### Clinical Trial Data

Access tied to study duration.

### Software Subscriptions

Annual licenses with renewal.

### Market Data

Real-time access during market hours only.

### ODRL Temporal Profile

Defines `effectiveFrom` and `effectiveTo` for time-bounded policies.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Access Research Data                     │
│  ─────────────────────────────────────────────────  │
│  Subject: Researcher                                 │
│  Action: access                                      │
│  Object: Healthcare Dataset                          │
│  Condition:                                          │
│    currentDateTime >= 2025-01-01T00:00:00Z           │
│    AND currentDateTime < 2027-01-01T00:00:00Z        │
└─────────────────────────────────────────────────────┘
```

## Time Window Patterns

| Pattern | Effective From | Effective To |
|---------|---------------|--------------|
| Fixed period | Specific date | Specific date |
| Rolling | Now | Now + duration |
| Open start | (unbounded) | Specific date |
| Open end | Specific date | (unbounded) |
| Recurring | Daily/weekly schedule | Daily/weekly schedule |

## Evaluation Logic

```
Request: User wants to access data at time T

1. Resolve current time T (from Σ.Clock or request)
2. Check start condition:
   - If effectiveFrom defined: T >= effectiveFrom?
   - If not defined: always true
3. Check end condition:
   - If effectiveTo defined: T < effectiveTo?
   - If not defined: always true
4. Both true → time window is valid → continue
   Either false → DENY with "outside valid period"
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Clock skew | Use authoritative time source |
| Timezone | Store as UTC, convert for display |
| Leap seconds | Typically ignored |
| Daylight saving | UTC avoids ambiguity |
| "End of day" | Specify exact time (23:59:59 vs 00:00:00) |

## Pre-expiry Notification

Good practice includes warning before expiration:

```turtle
ex:expiryWarningDuty a rl2:Duty ;
    rl2:subject ex:System ;
    rl2:action ex:notifyExpiry ;
    rl2:counterparty ex:Researcher ;
    rl2:condition [
        # 30 days before expiry
        a rl2:AtomicConstraint ;
        rl2:leftOperand rl2:currentDateTime ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand "2026-12-01T00:00:00Z"^^xsd:dateTime
    ] .
```

## Profile Requirements

```turtle
@prefix temporal: <https://example.org/profile/temporal#> .

temporal:effectiveFromOperand a rl2:LeftOperand ;
    rl2:resolutionPath "policy.effectiveFrom" .

temporal:effectiveToOperand a rl2:LeftOperand ;
    rl2:resolutionPath "policy.effectiveTo" .

# rl2:currentDateTime is a core LeftOperand
```

---

## RL2 Model

*To be added after pattern documentation is approved.*

```turtle
# Placeholder - will demonstrate currentDateTime with gte/lt operators
```

---

## References

- ODRL Temporal Profile
- ISO 8601 — Date and time format
- Contract law — Term and termination
- Software licensing — Subscription models
