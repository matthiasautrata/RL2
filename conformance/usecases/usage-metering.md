# Use Case 21: Usage Metering

**Pattern:** Count-based constraint  
**Vocabulary Demonstrated:** Counter operand (profile-declared)  
**Category:** External Data Licenses  
**Status:** DRAFT

---

## Business Context

Data vendors often license data with usage limits:
- N queries per month
- N downloads per day
- N API calls per hour

Exceeding limits requires additional licensing or triggers overage fees.

## Scenario

A bank licenses real-time market data with a limit of 10,000 queries per month. The system must:
1. Track query count
2. Permit queries within limit
3. Deny or flag queries exceeding limit

## Policy Intent

> "Licensee may query data up to N times per period. Excess queries require additional authorization."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Constraint type | Numeric threshold |
| State required | Persistent counter |
| Reset | Periodic (daily, monthly, annually) |
| Enforcement | Hard limit or soft (overage billing) |

## Real-World Terms

### CME Group

> "Fees apply to any unauthorized use or redistribution of Information... A full month's Fee is due for each month in which the Unit of Count has access to Information."

### IDS Policy Pattern

The IDS "restricted number of usages" pattern uses ODRL COUNT constraint with post-duty to increment counter.

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Query Data (within limit)                │
│  ─────────────────────────────────────────────────  │
│  Subject: Licensee                                   │
│  Action: query                                       │
│  Object: Market Data                                 │
│  Condition: usageCount ≤ 10000                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Duty: Increment Counter (post-use)                  │
│  ─────────────────────────────────────────────────  │
│  Subject: System                                     │
│  Action: incrementCounter                            │
│  Triggered by: Each query                            │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Request: User wants to query data

1. Resolve current usage count from Σ
2. Compare against limit (≤ 10000)
3. If within limit → PERMIT, then increment counter
   If exceeds limit → DENY or escalate
```

## Counter State Management

| Aspect | Options |
|--------|---------|
| Storage | External system, policy state |
| Granularity | Per-user, per-org, per-API-key |
| Reset | Calendar period, rolling window |
| Overflow | Hard block, soft warning, auto-upgrade |

## Profile Requirements

```turtle
@prefix license: <https://example.org/profile/license#> .

license:usageCountOperand a rl2:LeftOperand ;
    rdfs:label "Usage Count" ;
    rl2:resolutionPath "state.counters.queryCount" .

license:usageLimitOperand a rl2:LeftOperand ;
    rdfs:label "Usage Limit" ;
    rl2:resolutionPath "state.License.queryLimit" .

license:incrementCounter a rl2:Action ;
    rdfs:label "Increment Counter" .
```

## Comparison with Related Use Cases

| Use Case | Focus |
|----------|-------|
| **usage-metering** | Query/access counting |
| concurrent-seats (16) | Simultaneous user limit |
| volume-limit (34) | Data amount (bytes/rows) |

---

## RL2 Model

This model demonstrates the counter-operand pattern: a Privilege
gated on a persistent usage count staying at or below the licensed
limit, plus a triggered Duty to increment that counter after each
query.

```turtle
@prefix ex: <https://example.org/> .
@prefix license: <https://example.org/profile/license#> .
@prefix rl2: <https://rl2.example/ontology#> .

# ── Privilege: query, while usage count stays within the limit ──────
ex:queryPrivilege a rl2:Privilege ;
    rl2:subject ex:Licensee ;
    rl2:action ex:query ;
    rl2:object ex:MarketData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand license:usageCountOperand ;
        rl2:constraintOperator rl2:lte ;
        rl2:rightOperandRef license:usageLimitOperand
    ] .

ex:query a rl2:Action ;
    rdfs:label "Query" .

ex:queryPerformedEvent a rl2:Event ;
    rdfs:label "Query Performed" .

# ── Duty: increment the usage counter after every query ──────────────
ex:incrementCounterDuty a rl2:Duty ;
    rl2:subject ex:System ;
    rl2:action license:incrementCounter ;
    rl2:object ex:UsageCounter ;
    rl2:counterparty ex:Licensee ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent ex:queryPerformedEvent
    ] .

ex:marketDataLicense a rl2:Agreement ;
    rl2:grantor ex:Bank ;
    rl2:grantee ex:Licensee ;
    rl2:clause ex:queryPrivilege, ex:incrementCounterDuty .
```

---

## References

- CME Market Data License Agreement
- IDS Policy Patterns — COUNT constraint
- API rate limiting best practices
