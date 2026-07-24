# Use Case 13: Quality Circuit Breaker

**Pattern:** State Transition on metric threshold
**Identity Check:** N/A (system-level enforcement)
**Category:** Data Contracts, Quality Gates

## Scenario

If `null_count > 5%` in the daily data batch, read access to downstream dashboards is immediately revoked to prevent bad reporting. Access is restored when a clean batch is received.

## Policy Intent

> "Suspend access automatically when data quality degrades. Restore when quality recovers."

## Key Characteristics

- **State Transition** based on quality metrics
- Automatic suspension (not human-initiated)
- Automatic restoration (not human-initiated)
- Prevents bad data from propagating

## Why RL2?

This requires **State Transitions**. A `QualityMetricEvent` triggers the transition of a `Privilege` from `Active` to `Suspended`. ODRL does not natively model:
- Dynamic suspension of rules
- Metric-based evaluation
- Automatic restoration

RL2's `NormState` model explicitly supports `Active`/`Suspended` transitions triggered by events or conditions.

## Profile-Declared Operands

```turtle
@prefix dataquality: <https://example.org/profile/dataquality#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Operands
dataquality:nullRateOperand a rl2:LeftOperand ;
    rdfs:label "Null Rate" ;
    rdfs:comment "Percentage of null values in the current batch." ;
    rl2:resolutionPath "asset.qualityMetrics.nullRate" ;
    rdfs:range xsd:decimal .

dataquality:qualityScoreOperand a rl2:LeftOperand ;
    rdfs:label "Quality Score" ;
    rdfs:comment "Composite quality score (0-100)." ;
    rl2:resolutionPath "asset.qualityMetrics.score" ;
    rdfs:range xsd:integer .

dataquality:batchStatusOperand a rl2:LeftOperand ;
    rdfs:label "Batch Status" ;
    rdfs:comment "Quality status of current batch." ;
    rl2:resolutionPath "asset.currentBatch.qualityStatus" ;
    rdfs:range dataquality:BatchStatus .

# Actions
dataquality:read a rl2:Action ;
    rdfs:label "Read" ;
    rdfs:comment "Read access to data asset." .

dataquality:notifyQualityTeam a rl2:Action ;
    rdfs:label "Notify Quality Team" ;
    rdfs:comment "Send quality degradation alert to data quality team." .
```

## RL2 Model

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix dataquality: <https://example.org/profile/dataquality#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Base privilege for dashboard access
ex:dashboardAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Analyst ;
    rl2:action dataquality:read ;
    rl2:object ex:SalesDashboard ;
    rl2:condition [
        # Only active when data quality is acceptable
        a rl2:AtomicConstraint ;
        rl2:leftOperand dataquality:nullRateOperand ;
        rl2:constraintOperator rl2:lte ;
        rl2:rightOperand "0.05"^^xsd:decimal  # 5% threshold
    ] .

# Prohibition when quality degrades (circuit breaker OPEN)
# Note: No priority needed - conditions are mutually exclusive (≤5% vs >5%)
ex:qualityCircuitBreaker a rl2:Prohibition ;
    rl2:subject ex:Analyst ;
    rl2:prohibitedAction dataquality:read ;
    rl2:object ex:SalesDashboard ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand dataquality:nullRateOperand ;
        rl2:constraintOperator rl2:gt ;
        rl2:rightOperand "0.05"^^xsd:decimal
    ] .

# Duty: Notify data team when circuit breaker trips
ex:notifyDataTeamDuty a rl2:Duty ;
    rl2:subject ex:DataPlatform ;
    rl2:action dataquality:notifyQualityTeam ;
    rl2:object ex:DataQualityTeam ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand dataquality:nullRateOperand ;
        rl2:constraintOperator rl2:gt ;
        rl2:rightOperand "0.05"^^xsd:decimal
    ] .
```

## State Machine

```
Circuit Breaker States:

                  nullRate > 5%
    ┌──────────┐ ─────────────▶ ┌──────────┐
    │  CLOSED  │                │   OPEN   │
    │ (Access  │ ◀───────────── │  (Access │
    │ Granted) │   nullRate     │  Denied) │
    └──────────┘     ≤ 5%       └──────────┘
         │                           │
         │                           │
         └─────── Normal flow ───────┘
                 (each batch
                  re-evaluated)
```

## Evaluation

| Scenario | Null Rate | Circuit State | Access Result |
|----------|-----------|---------------|---------------|
| Clean batch | 2% | CLOSED | PERMIT |
| Borderline | 5% | CLOSED | PERMIT |
| Degraded batch | 8% | OPEN | DENY + Alert |
| Recovery batch | 3% | CLOSED | PERMIT |

## Implementation Notes

### Mutually Exclusive Conditions

The circuit breaker pattern uses mutually exclusive conditions:
- `nullRate ≤ 5%` → Privilege applies (access granted)
- `nullRate > 5%` → Prohibition applies (access denied)

Since these conditions cannot both be true simultaneously, no priority mechanism is needed. The evaluator will find exactly one applicable norm for any given null rate.

### Metric Freshness

The quality metrics must be refreshed with each batch. The `resolutionPath` points to live metrics, not cached values.

### Cascading Effects

In a data mesh, this pattern can cascade:
1. Source dataset trips circuit breaker
2. Downstream datasets inherit the suspension
3. All dependent dashboards become inaccessible

This requires hierarchy traversal (transitive closure over `dependsOn`).

## Comparison

| Aspect | Manual Process | ODRL | RL2 |
|--------|----------------|------|-----|
| Trigger | Human review | Not supported | Automatic on metric |
| Suspension | Manual revocation | Not supported | Condition-based prohibition |
| Restoration | Manual grant | Not supported | Condition re-evaluation |
| Notification | Separate system | Not supported | Triggered duty |

## PNF Considerations

This use case is straightforward for PNF:

- Single numeric comparison (`nullRate > 0.05`)
- No transitive closure needed (unless cascading)
- Propositional logic only

The "circuit breaker" is a prohibition with a metric condition using mutually exclusive constraints — well within the semantic class.
