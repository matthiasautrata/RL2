# Fire-Alarm Evacuation

## Scenario

When a fire alarm is active, a building occupant may use an emergency exit.

## Why it matters

This is a global state condition whose effect is independent of the agent or device that reported
the alarm.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Occupant a rl2:Agent .
ex:EmergencyExit a rl2:Asset .
ex:useEmergencyExit a rl2:Action .
ex:fireAlarmActive a rl2:LeftOperand ;
    rl2:valueType <http://www.w3.org/2001/XMLSchema#boolean> ;
    rl2:resolutionPath "state.fireAlarmActive" .

ex:evacuatePrivilege a rl2:Privilege ;
    rl2:subject ex:Occupant ;
    rl2:action ex:useEmergencyExit ;
    rl2:object ex:EmergencyExit ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:fireAlarmActive ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] .

ex:safetyPolicy a rl2:Set ;
    rl2:clause ex:evacuatePrivilege .
```

## Request and snapshot

Request: `(agent = Occupant, action = useEmergencyExit, asset = EmergencyExit)`.

World snapshot: `state.fireAlarmActive = true` from an admissible alarm source.

## Expected result

The request is `Permit`. A false alarm state makes the Privilege inactive; missing or invalid
state produces an attributed `Indeterminate` result.
