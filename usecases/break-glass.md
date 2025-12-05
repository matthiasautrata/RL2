# Use Case 3: Break Glass (Personal Liability)

**Pattern:** Event + Identity binding (Tun-sollen)
**Identity Check:** `operationalAgent = currentAgent`
**Category:** Emergency access with accountability

## Scenario

Emergency access to fire suppression controls requires breaking a glass panel. Only the person who breaks the glass accepts liability and gains access.

## Policy Intent

> "If YOU break the glass, YOU accept responsibility and gain access."

## Key Characteristics

- Emergency override mechanism
- Personal liability binding
- Audit trail critical
- Cannot "draft off" someone else's emergency action

## RL2 Model (Unified State Approach)

```turtle
ex:breakGlassEvent a rl2:Event ;
    rdfs:comment "Template for glass-breaking events" .

ex:emergencyAccessPrivilege a rl2:Privilege ;
    rl2:priority 500 ;  # High priority override
    rl2:subject ex:Employee ;
    rl2:action ex:accessEmergencySystem ;
    rl2:object ex:FireSuppressionControls ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            # Check 1: Has the event occurred?
            a rl2:EventConstraint ;
            rl2:expectsEvent ex:breakGlassEvent
        ] ;
        rl2:operand [
            # Check 2: Did I perform it?
            a rl2:AtomicConstraint ;
            rl2:leftOperand rl2:eventPerformer ;  # Event performer from context
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

Note: For event-based identity binding, the event's `operationalAgent` is compared against the requester. This uses contextual event tracking rather than duty state querying.

## Evaluation

| Scenario | Glass Broken By | Request By | Result |
|----------|-----------------|------------|--------|
| Normal emergency | Alice | Alice | PERMIT + audit |
| Piggyback attempt | Alice | Bob | DENY |

## Key Insight

The precondition is an **Event** (physical action), not a **Duty** (normative obligation). The identity binding ensures the person who performed the irreversible action is the one who benefits/bears responsibility.

## Comparison

- **ODRL:** Cannot model event-based preconditions with identity binding
- **UCON:** Would require user-attribute check
- **RL2:** `EventConstraint` + identity binding via context
