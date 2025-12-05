# Use Case 3: Break Glass (Personal Liability)

**Pattern:** Event + Identity binding (Tun-sollen)
**Identity Check:** `eventPerformerOperand = currentAgent`
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

## Profile-Declared Operands

This use case requires a profile that declares the operand for accessing event performer information. The operand is resolved via the canonical path mechanism defined in RL2_Semantics.

```turtle
@prefix emergency: <https://example.org/profile/emergency#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Profile-declared operand for accessing the performer of an event
emergency:eventPerformerOperand a rl2:LeftOperand ;
    rdfs:label "Event Performer" ;
    rdfs:comment "Resolves to the agent who performed the triggering event." ;
    rl2:resolutionPath "state.Events.BreakGlassEvent.operationalAgent" ;
    rdfs:range rl2:Agent .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix emergency: <https://example.org/profile/emergency#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:BreakGlassEvent a rl2:Event ;
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
            rl2:expectsEvent ex:BreakGlassEvent
        ] ;
        rl2:operand [
            # Check 2: Did I perform it?
            # Uses profile-declared operand with explicit resolution path
            a rl2:AtomicConstraint ;
            rl2:leftOperand emergency:eventPerformerOperand ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperandRef rl2:currentAgent
        ]
    ] .
```

## Resolution Semantics

When evaluating the identity binding condition:

1. `emergency:eventPerformerOperand` is resolved via its declared `rl2:resolutionPath`
2. `deref("state.Events.BreakGlassEvent.operationalAgent", Env)` retrieves the agent who performed the event (most recent BreakGlassEvent instance)
3. `rl2:currentAgent` resolves to `Env.Agent` (the requesting agent)
4. The constraint holds if these are equal (Tun-sollen identity binding)

This aligns with the formal semantics in RL2_Semantics.md:
```
resolve(op, Env, targetNorm) =
    _ | op.resolutionPath ≠ ⊥ → deref(op.resolutionPath, Env)
```

## Evaluation

| Scenario | Glass Broken By | Request By | Result |
|----------|-----------------|------------|--------|
| Normal emergency | Alice | Alice | PERMIT + audit |
| Piggyback attempt | Alice | Bob | DENY |

## Key Insight

The precondition is an **Event** (physical action), not a **Duty** (normative obligation). The identity binding ensures the person who performed the irreversible action is the one who benefits/bears responsibility.

## Why Profile-Declared Operands?

Previous versions of this use case introduced ad-hoc properties like `rl2:eventPerformer`. This bypassed RL2's formal evaluation calculus and created semantic orphans—properties that work intuitively but have no grounding in the `resolve`/`deref` machinery.

By using profile-declared operands with explicit resolution paths:
- **No ontology pollution**: RL2 Core doesn't grow
- **Type safety**: The operand declares `rdfs:range rl2:Agent`
- **Validation**: SHACL can verify the operand is used correctly
- **Mechanization**: Clear mapping to Why3/Lean verification targets
- **Auditability**: All data access points are explicit and declared

## Comparison

- **ODRL:** Cannot model event-based preconditions with identity binding
- **UCON:** Would require user-attribute check
- **RL2:** `EventConstraint` + profile-declared operand with resolution path
