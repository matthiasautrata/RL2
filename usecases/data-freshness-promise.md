# Use Case 11: Data Freshness Promise

**Pattern:** Promise with violation detection
**Identity Check:** `promisor = provider`
**Category:** Data Contracts, SLA Enforcement

## Scenario

A data provider promises that a dataset will be refreshed every 6 hours. If the refresh is missed, the promise transitions to `Violated` and an incident ticket is automatically created.

## Policy Intent

> "Provider promises data will be updated every 6 hours. Violation triggers escalation."

## Key Characteristics

- **Promise**, not a Duty (obligation on provider, not consumer)
- Temporal monitoring (6-hour window)
- Automated violation detection
- Side-effect on violation (ticket creation)

## Why RL2?

ODRL struggles to model obligations *on the Provider*. Its permission/prohibition model assumes a unilateral grant from licensor to licensee. Data contracts are bilateral: the provider has obligations too.

RL2 explicitly models:
- `Promise` states (`Pending` → `Fulfilled` / `Violated`)
- `promisedState` (Sein-sollen) with a temporal freshness bound
- State transitions on deadline expiry
- Triggered duties on violation

## Profile-Declared Operands

```turtle
@prefix datacontract: <https://example.org/profile/datacontract#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

datacontract:lastRefreshTimeOperand a rl2:LeftOperand ;
    rdfs:label "Last Refresh Time" ;
    rdfs:comment "Timestamp of most recent data refresh." ;
    rl2:resolutionPath "asset.metadata.lastRefreshTime" ;
    rdfs:range xsd:dateTime .

datacontract:refreshIntervalOperand a rl2:LeftOperand ;
    rdfs:label "Refresh Interval" ;
    rdfs:comment "Maximum allowed time between refreshes." ;
    rl2:resolutionPath "context.sla.refreshInterval" ;
    rdfs:range xsd:duration .

datacontract:datasetAgeOperand a rl2:LeftOperand ;
    rdfs:label "Dataset Age" ;
    rdfs:comment "Elapsed time since the dataset was last refreshed." ;
    rl2:resolutionPath "asset.metadata.datasetAge" ;
    rdfs:range xsd:duration .

datacontract:promiseStateOperand a rl2:LeftOperand ;
    rdfs:label "Promise State Operand" ;
    rdfs:comment "Queries the PromiseState of the target promise." ;
    rl2:resolutionPath "state.Promises.<target>.state" ;
    rdfs:range rl2:PromiseState .

# Actions
datacontract:refreshData a rl2:Action ;
    rdfs:label "Refresh Data" ;
    rdfs:comment "Refresh a dataset with new data." .

datacontract:createIncidentTicket a rl2:Action ;
    rdfs:label "Create Incident Ticket" ;
    rdfs:comment "Create an incident ticket for SLA violation." .
```

## RL2 Model

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix datacontract: <https://example.org/profile/datacontract#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# The Promise: Provider commits to a freshness SLA.
# Sein-sollen (ought-to-be): the promised *state* is that the dataset stays fresh
# (age ≤ 6h). The refresh action is merely the means; the commitment is the state.
# On violation, ex:escalationDuty below is the remedial response.
ex:freshnessPromise a rl2:Promise ;
    rl2:promisor ex:DataProvider ;
    rl2:promisee ex:DataConsumer ;
    rl2:promisedState ex:datasetIsFresh ;
    rl2:object ex:CustomerDataset .

ex:datasetIsFresh a rl2:AtomicConstraint ;
    rl2:leftOperand datacontract:datasetAgeOperand ;
    rl2:constraintOperator rl2:lte ;
    rl2:rightOperand "PT6H"^^xsd:duration .

# Duty triggered on violation: create incident ticket
ex:escalationDuty a rl2:Duty ;
    rl2:subject ex:DataProvider ;
    rl2:action datacontract:createIncidentTicket ;
    rl2:object ex:SLAViolationReport ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:freshnessPromise ;
        rl2:leftOperand datacontract:promiseStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Violated   # state enum is an IRI → rightOperandRef
    ] .
```

## State Transitions

```
Promise State Machine:

  ┌─────────────┐   refresh event    ┌───────────────┐
  │  Pending    │──────────────────▶│   Fulfilled    │
  └─────┬───────┘                    └────────┬──────┘
        │                                    │
        │ deadline expires                   │ next interval starts
        ▼                                    ▼
  ┌─────────────┐                   ┌─────────────┐
  │  Violated   │◀──────────────────│  Pending    │
  └─────────────┘  deadline expires └─────────────┘
```

## Evaluation

| Scenario | Last Refresh | Current Time | Promise State | Result |
|----------|--------------|--------------|---------------|--------|
| On time | 2h ago | now | Fulfilled | OK |
| Due soon | 5h ago | now | Pending | Warning |
| Overdue | 7h ago | now | Violated | Ticket created |

## Comparison with ODRL

| Aspect | ODRL | RL2 |
|--------|------|-----|
| Provider obligations | Awkward (permission with duty?) | Native Promise type |
| Temporal monitoring | Not built-in | `currentDateTime` constraints + state machine |
| Violation detection | No standard mechanism | `promiseStateOperand = Violated` |
| Escalation triggers | Not expressible | Duty conditioned on Promise state |

## PNF Considerations

This use case requires:
- **Temporal reasoning**: checking `now - lastRefresh > interval`
- **Promise state tracking**: part of `Σ` (system state)
- **Triggered duties**: condition on Promise state

All within the "propositional + bounded transitive closure" semantic class. The temporal check is a simple comparison, not quantification.
