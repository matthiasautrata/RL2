# Trial Period

## Scenario

A trial user may execute an application until a specified expiry instant and may read data throughout the trial and after expiry.

## Why it matters

Temporal feature limits are ordinary conditions over the evaluation time. No policy state transition is needed to express the change in available actions.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:TrialUser a rl2:Agent .
ex:Application a rl2:Asset .
ex:execute a rl2:Action .
ex:read a rl2:Action .

ex:trialExecutePrivilege a rl2:Privilege ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:execute ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand rl2:currentDateTime ;
        rl2:constraintOperator rl2:lt ;
        rl2:rightOperand "2026-08-15T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:expiredTrialProhibition a rl2:Prohibition ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:execute ;
    rl2:object ex:Application ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand rl2:currentDateTime ;
        rl2:constraintOperator rl2:gte ;
        rl2:rightOperand "2026-08-15T00:00:00Z"^^xsd:dateTimeStamp
    ] .

ex:readPrivilege a rl2:Privilege ;
    rl2:subject ex:TrialUser ;
    rl2:action ex:read ;
    rl2:object ex:Application .

ex:trialPolicy a rl2:Set ;
    rl2:clause ex:trialExecutePrivilege, ex:expiredTrialProhibition, ex:readPrivilege .
```

## Request and snapshot

Request: `(agent = TrialUser, action = execute, asset = Application)`.

World snapshot: `evaluationTime` is before or at/after `2026-08-15T00:00:00Z`.

## Expected result

Before expiry, execution is `Permit`. At and after expiry, execution is `Deny`; requests to `read` remain `Permit`.
