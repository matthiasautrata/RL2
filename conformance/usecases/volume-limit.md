# Use Case 34: Volume Limit

**Pattern:** Data amount restriction  
**Vocabulary Demonstrated:** Numeric comparison, profile operand  
**Category:** EU Data Spaces, Data Contracts  
**Status:** DRAFT

---

## Business Context

Data access may be limited by volume:

- **Row limits:** Max N records per query
- **Size limits:** Max X GB per month
- **API limits:** Max requests per time period
- **Batch limits:** Max records per export

This protects against bulk extraction and manages infrastructure costs.

## Scenario

A data marketplace offers demographic data. The standard license limits:

> "Subscriber may access up to 100,000 records per calendar month. Excess access requires upgraded licensing."

## Policy Intent

> "Access is PERMITTED if cumulative volume is below threshold."

## Key Characteristics

| Aspect | Description |
|--------|-------------|
| Metric | Records, bytes, API calls |
| Period | Per-query, daily, monthly |
| Threshold | Hard cap or soft limit |
| Enforcement | Block or charge overage |

## Real-World Examples

### IDS Policy Patterns

"Amount of data" is a documented IDS policy pattern for limiting data volume in transfers.

### API Rate Limits

Most data APIs impose request volume limits (e.g., 1000 requests/day).

### Database Licensing

Some databases license by data volume (e.g., per-TB pricing).

## Normative Structure

```
┌─────────────────────────────────────────────────────┐
│  Privilege: Query Data                               │
│  ─────────────────────────────────────────────────  │
│  Subject: Subscriber                                 │
│  Action: query                                       │
│  Object: Demographic Data                            │
│  Condition:                                          │
│    monthlyRecordCount + requestedRecords ≤ 100000   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  Duty: Track Volume (post-action)                   │
│  ─────────────────────────────────────────────────  │
│  Subject: System                                     │
│  Action: incrementVolumeCounter                      │
│  Triggered by: Each successful query                 │
└─────────────────────────────────────────────────────┘
```

## Evaluation Logic

```
Request: Query for N records

1. Retrieve current period volume from Σ
2. Calculate: currentVolume + N
3. Compare against limit:
   - If within limit → PERMIT, update counter
   - If exceeds limit → Check policy:
     - Hard cap → DENY
     - Soft cap → PERMIT with overage flag
     - Partial → Return only (limit - current) records
```

## Volume Metrics

| Metric | Unit | Use Case |
|--------|------|----------|
| Record count | Integer | Row-based data |
| Byte size | GB/MB | File downloads |
| API calls | Integer | Service access |
| Query count | Integer | Database access |
| Time duration | Seconds | Streaming data |

## Period Types

| Period | Reset | Use Case |
|--------|-------|----------|
| Per-request | Each request | Single query limits |
| Daily | Midnight | API rate limits |
| Monthly | 1st of month | Subscription tiers |
| Rolling | Sliding window | Burst protection |
| Lifetime | Never | One-time allocations |

## Profile Requirements

```turtle
@prefix volume: <https://example.org/profile/volume#> .

volume:currentVolumeOperand a rl2:LeftOperand ;
    rdfs:label "Current Period Volume" ;
    rl2:resolutionPath "state.volumeCounters.currentPeriod.value" .

volume:requestedVolumeOperand a rl2:LeftOperand ;
    rdfs:label "Requested Volume" ;
    rl2:resolutionPath "request.recordCount" .

volume:volumeLimitOperand a rl2:LeftOperand ;
    rdfs:label "Volume Limit" ;
    rl2:resolutionPath "state.License.volumeLimit" .

volume:incrementVolume a rl2:Action ;
    rdfs:label "Increment Volume Counter" .
```

---

## RL2 Model

This model demonstrates a numeric comparison against a profile-defined
threshold operand, plus a triggered Duty to increment the volume
counter after each successful query.

```turtle
@prefix ex: <https://example.org/> .
@prefix volume: <https://example.org/profile/volume#> .
@prefix rl2: <https://rl2.example/ontology#> .

# ── Privilege: query, while cumulative volume stays under the limit ──
ex:queryPrivilege a rl2:Privilege ;
    rl2:subject ex:Subscriber ;
    rl2:action ex:query ;
    rl2:object ex:DemographicData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand volume:currentVolumeOperand ;
        rl2:constraintOperator rl2:lt ;
        rl2:rightOperandRef volume:volumeLimitOperand
    ] .

ex:query a rl2:Action ;
    rdfs:label "Query" .

ex:queryPerformedEvent a rl2:Event ;
    rdfs:label "Query Performed" .

# ── Duty: increment the volume counter after every successful query ──
ex:incrementVolumeDuty a rl2:Duty ;
    rl2:subject ex:System ;
    rl2:action volume:incrementVolume ;
    rl2:object ex:VolumeCounter ;
    rl2:counterparty ex:Subscriber ;
    rl2:condition [
        a rl2:EventConstraint ;
        rl2:expectsEvent ex:queryPerformedEvent
    ] .

ex:dataAccessLicense a rl2:Agreement ;
    rl2:grantor ex:DataMarketplace ;
    rl2:grantee ex:Subscriber ;
    rl2:clause ex:queryPrivilege, ex:incrementVolumeDuty .
```

---

## References

- IDS Policy Patterns — Amount of data
- API rate limiting best practices
- Cloud storage pricing models
