# Role-Constrained Access

## Scenario

A document service permits a named analyst to read an internal document when the snapshot records
that the analyst holds a role that is an instance of `Analyst`. Role membership is an explicit,
profile-defined fact. RL2 does not expand a norm’s `subject` through an ambient role hierarchy.

## Why it matters

Role semantics remain explicit policy data rather than an implementation-specific subject match.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix role: <https://example.org/profile/role#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Alice a rl2:Agent .
ex:InternalReport a rl2:Asset .
ex:read a rl2:Action .

role:currentRole a rl2:LeftOperand ;
    rdfs:range role:Role ;
    rl2:resolutionPath "agent.role" .
role:Role a rdfs:Class .
role:Analyst a rdfs:Class ; rdfs:subClassOf role:Role .
role:SeniorAnalyst a rdfs:Class ; rdfs:subClassOf role:Analyst .
ex:AliceRole a role:SeniorAnalyst .

ex:analystRead a rl2:Privilege ;
    rl2:subject ex:Alice ;
    rl2:action ex:read ;
    rl2:object ex:InternalReport ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand role:currentRole ;
        rl2:constraintOperator rl2:isA ;
        rl2:rightOperandRef role:Analyst
    ] .

ex:policy a rl2:Set ; rl2:clause ex:analystRead .
```

## Request and snapshot

Request: `(Alice, read, InternalReport)`. The snapshot contains
`agent.role = ex:AliceRole`.

## Expected result

The decision is `Permit`. A policy intended for several agents contains the relevant canonical
clauses; an evaluator does not substitute a role for the requesting agent during request matching.
