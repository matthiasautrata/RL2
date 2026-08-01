# Step-Up Authentication

## Scenario

An employee may access a high-risk document only with multi-factor authentication. If the snapshot reports a lower authentication level, the employee has a duty to authenticate.

## Why it matters

Authentication assurance is attributed external evidence. The policy specifies its required level but does not perform authentication.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Employee a rl2:Agent .
ex:HighRiskDocument a rl2:Asset .
ex:AuthenticationService a rl2:Asset .
ex:read a rl2:Action .
ex:authenticate a rl2:Action .

ex:authenticationLevel a rl2:LeftOperand ;
    rl2:valueType xsd:integer ;
    rl2:resolutionPath "agent.authentication.level" .

ex:highRiskReadPrivilege a rl2:Privilege ;
    rl2:subject ex:Employee ;
    rl2:action ex:read ;
    rl2:object ex:HighRiskDocument ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:authenticationLevel ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand 2
    ] .

ex:stepUpDuty a rl2:Duty ;
    rl2:subject ex:Employee ;
    rl2:action ex:authenticate ;
    rl2:object ex:AuthenticationService ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:authenticationLevel ;
        rl2:constraintOperator rl2:lt ;
        rl2:rightOperand 2
    ] .

ex:authenticationPolicy a rl2:Set ;
    rl2:clause ex:highRiskReadPrivilege, ex:stepUpDuty .
```

## Request and snapshot

Request: `(agent = Employee, action = read, asset = HighRiskDocument)`.

World snapshot: `agent.authentication.level` is `1` for password-only authentication or `2` for multi-factor authentication.

## Expected result

At level `2`, the request is `Permit`. At level `1`, the access privilege is inactive and the step-up Duty's derived status is `Active` — a status-map entry for the independent Duty, not an `obligate` atom for the `read` request; the Duty's own action and object (`authenticate`, `AuthenticationService`) do not match it.
