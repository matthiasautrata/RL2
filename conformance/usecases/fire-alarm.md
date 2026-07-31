# Use Case 4: Fire Alarm Evacuation

**Pattern:** Sein-sollen (state-triggered, event-based)
**Identity Check:** None (anyone may trigger)
**Category:** Safety systems

## Scenario

When a fire alarm is triggered (by anyone), all building occupants gain permission to use emergency exits.

## Policy Intent

> "If the alarm IS TRIGGERED, everyone may evacuate."

## Key Characteristics

- One trigger enables many beneficiaries
- Identity of trigger irrelevant (Sein-sollen)
- Safety takes precedence
- Broadcast permission grant

## Profile-Declared Actions

```turtle
@prefix safety: <https://example.org/profile/safety#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

safety:useEmergencyExit a rl2:Action ;
    rdfs:label "Use Emergency Exit" ;
    rdfs:comment "Use emergency exit doors for evacuation." .
```

## RL2 Model (Unified State Approach)

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix safety: <https://example.org/profile/safety#> .

ex:fireAlarmEvent a rl2:Event .

ex:emergencyEvacuationPrivilege a rl2:Privilege ;
    rl2:subject ex:BuildingOccupant ;
    rl2:action safety:useEmergencyExit ;
    rl2:object ex:EmergencyDoors ;
    rl2:condition [
        # Sein-sollen: Only check event occurred, not who triggered
        a rl2:EventConstraint ;
        rl2:expectsEvent ex:fireAlarmEvent
        # NO identity check - anyone's trigger enables everyone
    ] .
```

## Evaluation

| Scenario | Alarm Triggered By | Request By | Result |
|----------|-------------------|------------|--------|
| Sensor trigger | Smoke detector | Alice | PERMIT |
| Manual trigger | Bob | Alice | PERMIT |
| No alarm | - | Alice | DENY |

## Contrast with Break Glass

| Aspect | Break Glass | Fire Alarm |
|--------|-------------|------------|
| Identity Check | `performer = currentAgent` | None |
| Pattern | Tun-sollen | Sein-sollen |
| Rationale | Personal liability | Collective safety |
| Beneficiaries | Trigger only | Everyone |

## Comparison

- **IoT Systems:** Often model as state change without access control
- **RL2:** Treats safety triggers as first-class normative events with explicit identity semantics
