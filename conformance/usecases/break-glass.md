# Break-Glass Access

## Scenario

An employee may access emergency controls after activating a break-glass procedure.

## Why it matters

The authorization is scoped to the requesting agent. Verification and expiry of the activation
record remain external-data responsibilities.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Employee a rl2:Agent .
ex:FireControls a rl2:Asset .
ex:accessEmergencyControls a rl2:Action .

ex:breakGlassActive a rl2:LeftOperand ;
    rl2:valueType <http://www.w3.org/2001/XMLSchema#boolean> ;
    rl2:resolutionPath "agent.breakGlassActive" .

ex:emergencyAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Employee ;
    rl2:action ex:accessEmergencyControls ;
    rl2:object ex:FireControls ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:breakGlassActive ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] .

ex:emergencyPolicy a rl2:Set ;
    rl2:clause ex:emergencyAccessPrivilege .
```

## Request and snapshot

Request: `(agent = Employee, action = accessEmergencyControls, asset = FireControls)`.

World snapshot: the agent-scoped fact `agent.breakGlassActive` is `true` for Employee.

## Expected result

The request is `Permit`. A record scoped to another agent does not satisfy this operand.
