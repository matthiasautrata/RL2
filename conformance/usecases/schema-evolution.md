# Schema-Evolution Notice

## Scenario

A provider may deploy a breaking schema change only after required notice evidence shows that the notice period has elapsed. Compatible changes need no notice.

## Why it matters

The policy separates the business classification of a proposed change from the deterministic decision over supplied evidence.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Provider a rl2:Agent .
ex:Schema a rl2:Asset .
ex:deployChange a rl2:Action .
ex:notifyConsumers a rl2:Action .

ex:changeIsBreaking a rl2:LeftOperand ;
    rl2:valueType xsd:boolean ;
    rl2:resolutionPath "state.schemaChange.breaking" .
ex:noticePeriodElapsed a rl2:LeftOperand ;
    rl2:valueType xsd:boolean ;
    rl2:resolutionPath "state.schemaChange.noticePeriodElapsed" .

ex:compatibleChangePrivilege a rl2:Privilege ;
    rl2:subject ex:Provider ;
    rl2:action ex:deployChange ;
    rl2:object ex:Schema ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:changeIsBreaking ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand false
    ] .

ex:breakingChangePrivilege a rl2:Privilege ;
    rl2:subject ex:Provider ;
    rl2:action ex:deployChange ;
    rl2:object ex:Schema ;
    rl2:condition [
        a rl2:LogicalConstraint ;
        rl2:constraintOperator rl2:and ;
        rl2:operand [
            a rl2:AtomicConstraint ;
            rl2:leftOperand ex:changeIsBreaking ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand true
        ], [
            a rl2:AtomicConstraint ;
            rl2:leftOperand ex:noticePeriodElapsed ;
            rl2:constraintOperator rl2:eq ;
            rl2:rightOperand true
        ]
    ] .

ex:notifyDuty a rl2:Duty ;
    rl2:subject ex:Provider ;
    rl2:action ex:notifyConsumers ;
    rl2:object ex:Schema ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:changeIsBreaking ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] .

ex:schemaPolicy a rl2:Set ;
    rl2:clause ex:compatibleChangePrivilege, ex:breakingChangePrivilege, ex:notifyDuty .
```

## Request and snapshot

Request: `(agent = Provider, action = deployChange, asset = Schema)`.

World snapshot: classified change evidence provides `breaking` and `noticePeriodElapsed` booleans.

## Expected result

A compatible change is `Permit`. A breaking change is `Permit` only when the notice period has elapsed; otherwise neither privilege applies. The notification Duty's derived status is `Active` for a breaking change — a status-map entry for the independent Duty, not an `obligate` atom for the `deployChange` request; the Duty's own action, `notifyConsumers`, does not match it.
