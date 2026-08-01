# Role-Constrained Access

## Scenario

A document service permits any agent to read an internal document when the snapshot records that
the agent holds a role that is an instance of `Analyst`. The policy names no specific agent; role
membership is an explicit, profile-defined fact evaluated per requester. RL2 does not expand a
norm's `subject` through an ambient role hierarchy — the role class hierarchy gates the condition,
not the subject match.

## Why it matters

Role semantics remain explicit policy data rather than an implementation-specific subject match.
`rl2:subject rl2:anyAgent` matches every requesting agent; the `agent.role` condition, checked
with `isA` against the role class hierarchy, delimits the population to analysts. The policy graph
declares only reusable role vocabulary — the class hierarchy and a shared, agent-agnostic role
instance — never a fact naming Alice specifically; *which* agent holds *which* role instance is
world-snapshot data (`isA`'s `rdf:type` lookup is defined over the canonical policy universe, so
the instance's declared type must stay in the policy/profile graph — only its assignment to a
particular agent is snapshot data).

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix role: <https://example.org/profile/role#> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:InternalReport a rl2:Asset .
ex:read a rl2:Action .

role:currentRole a rl2:LeftOperand ;
    rdfs:range role:Role ;
    rl2:resolutionPath "agent.role" .
role:Role a rdfs:Class .
role:Analyst a rdfs:Class ; rdfs:subClassOf role:Role .
role:SeniorAnalyst a rdfs:Class ; rdfs:subClassOf role:Analyst .
role:SeniorAnalystInstance a role:SeniorAnalyst .

ex:analystRead a rl2:Privilege ;
    rl2:subject rl2:anyAgent ;
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

Request: `(Alice, read, InternalReport)`.

World snapshot: the agent-scoped fact `agent.role = role:SeniorAnalystInstance` for Alice. The
role instance and its type are reusable profile vocabulary, declared once in the policy/profile
graph; only the binding of that instance to Alice is snapshot data.

## Expected result

The decision is `Permit` — `rl2:anyAgent` matches Alice as subject, and her scoped `agent.role`
fact resolves to `role:SeniorAnalystInstance`, whose declared type `role:SeniorAnalyst` follows the
class hierarchy's `isA role:Analyst` check. One canonical clause now covers every analyst; an
evaluator does not substitute a role for the requesting agent during request matching, and a
missing `agent.role` fact produces `Indeterminate`, not `Permit` or `NotApplicable`.
