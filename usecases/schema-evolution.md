# Use Case 12: Schema Evolution Lock

**Pattern:** Event + Condition with temporal duty
**Identity Check:** N/A (provider-side enforcement)
**Category:** Data Contracts, Backward Compatibility

## Scenario

A data consumer allows the provider to change schema columns *only if* changes are backward compatible. Breaking changes require 30-day advance notice before taking effect.

## Policy Intent

> "Schema changes are permitted if backward compatible. Breaking changes require 30-day notice."

## Key Characteristics

- Event-triggered evaluation (`SchemaChangeEvent`)
- Conditional branching (compatible vs. breaking)
- Temporal duty (30-day notice period)
- Dynamic prohibition (breaking change blocked until notice period expires)

## Why RL2?

This requires **Event Semantics**. A `SchemaChangeEvent` must be evaluated against a condition (`isBackwardCompatible`). If false, it triggers:
1. A temporary `Prohibition` on the breaking change
2. A `Duty` to notify consumers
3. A temporal condition (via `currentDateTime`) that lifts the prohibition after 30 days

ODRL has no event model to evaluate changes as they occur.

## Profile-Declared Operands

```turtle
@prefix datacontract: <https://example.org/profile/datacontract#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

datacontract:isBackwardCompatibleOperand a rl2:LeftOperand ;
    rdfs:label "Is Backward Compatible" ;
    rdfs:comment "Whether a schema change is backward compatible." ;
    rl2:resolutionPath "event.schemaChange.isBackwardCompatible" ;
    rdfs:range xsd:boolean .

datacontract:noticeGivenDateOperand a rl2:LeftOperand ;
    rdfs:label "Notice Given Date" ;
    rdfs:comment "Date when breaking change notice was provided." ;
    rl2:resolutionPath "state.Notices.schemaChange.givenDate" ;
    rdfs:range xsd:dateTime .

datacontract:daysSinceNoticeOperand a rl2:LeftOperand ;
    rdfs:label "Days Since Notice" ;
    rdfs:comment "Number of days elapsed since breaking change notice was given." ;
    rl2:resolutionPath "state.Notices.schemaChange.daysSinceGiven" ;
    rdfs:range xsd:integer .

# Actions
datacontract:modifySchema a rl2:Action ;
    rdfs:label "Modify Schema" ;
    rdfs:comment "Modify the schema of a dataset." .

datacontract:notifyConsumers a rl2:Action ;
    rdfs:label "Notify Consumers" ;
    rdfs:comment "Send notification to data consumers about schema changes." .
```

## RL2 Model

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix datacontract: <https://example.org/profile/datacontract#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Event template for schema changes
ex:SchemaChangeEvent a rl2:Event ;
    rdfs:comment "Triggered when provider modifies dataset schema." .

# Privilege: Backward-compatible changes are always allowed
ex:compatibleChangePrivilege a rl2:Privilege ;
    rl2:subject ex:DataProvider ;
    rl2:action datacontract:modifySchema ;
    rl2:object ex:CustomerDataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:EventConstraint ;
            rl2:expectsEvent ex:SchemaChangeEvent
        ] ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand datacontract:isBackwardCompatibleOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand true
        ]
    ] .

# Privilege: Breaking changes allowed AFTER 30-day notice period
ex:breakingChangeAfterNoticePrivilege a rl2:Privilege ;
    rl2:subject ex:DataProvider ;
    rl2:action datacontract:modifySchema ;
    rl2:object ex:CustomerDataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand datacontract:isBackwardCompatibleOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand false
        ] ;
        rl2:operand [
            # Notice period HAS elapsed (30+ days)
            a rl2:AtomicConstraint ;
            rl2:leftOperand datacontract:daysSinceNoticeOperand ;
            rl2:constraintOperator rl2:gteq ;
            rl2:rightOperand 30
        ]
    ] .

# Prohibition: Breaking changes blocked if notice period not yet elapsed
# Note: No priority needed - conditions are mutually exclusive with privilege above
ex:breakingChangeProhibition a rl2:Prohibition ;
    rl2:subject ex:DataProvider ;
    rl2:action datacontract:modifySchema ;
    rl2:object ex:CustomerDataset ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand datacontract:isBackwardCompatibleOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand false
        ] ;
        rl2:operand [
            # Notice period has NOT elapsed (< 30 days)
            a rl2:AtomicConstraint ;
            rl2:leftOperand datacontract:daysSinceNoticeOperand ;
            rl2:constraintOperator rl2:lt ;
            rl2:rightOperand 30
        ]
    ] .

# Duty: Must notify consumers of breaking changes
ex:notifyBreakingChangeDuty a rl2:Duty ;
    rl2:subject ex:DataProvider ;
    rl2:action datacontract:notifyConsumers ;
    rl2:object ex:BreakingChangeNotice ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand datacontract:isBackwardCompatibleOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand false
    ] .
```

## Evaluation Flow

```
SchemaChangeEvent received
         │
         ▼
    ┌────────────────────────┐
    │ isBackwardCompatible?  │
    └───────────┬────────────┘
                │
       ┌────────┴────────┐
       ▼                 ▼
      true             false
       │                 │
       ▼                 ▼
    PERMIT         Notice given?
                         │
                ┌────────┴────────┐
                ▼                 ▼
            No notice        30 days elapsed?
                │                    │
                ▼               ┌────┴────┐
           DENY +               ▼         ▼
           Create Duty         yes        no
           (notify)             │          │
                               ▼          ▼
                            PERMIT      DENY
```

## Evaluation

| Scenario | Change Type | Notice | Elapsed | Result |
|----------|-------------|--------|---------|--------|
| Add column | Compatible | N/A | N/A | PERMIT |
| Rename column | Breaking | None | N/A | DENY + Notify duty |
| Rename column | Breaking | Given | 15 days | DENY (wait) |
| Rename column | Breaking | Given | 35 days | PERMIT |

## Key Insight

Schema evolution policies require:

1. **Event evaluation** at change time
2. **Conditional branching** based on change properties
3. **Temporal state** (notice given date, days since notice)
4. **Dynamic duty creation** for notification requirement

This is firmly in RL2 territory — ODRL's static permission model cannot express "allow this breaking change *after* 30 days from notice."

## Comparison

| Aspect | ODRL | RL2 |
|--------|------|-----|
| Event evaluation | Not supported | `EventConstraint` |
| Conditional branching | Limited | Full `LogicalConstraint` |
| Temporal delays | `dateTime` constraints only | Profile operand for days since notice |
| Dynamic duties | Not supported | Condition-triggered `Duty` |
