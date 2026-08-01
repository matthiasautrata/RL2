# Audit Trail Prerequisite

## Scenario

A trader may execute an order only after an audit record for that order has been created.

## Why it matters

The policy treats audit evidence as a prerequisite Duty and exposes the distinction between a required record and an external logging implementation.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Trader a rl2:Agent .
ex:Order a rl2:Asset .
ex:AuditRecord a rl2:Asset .
ex:record a rl2:Action .
ex:execute a rl2:Action .

ex:recordOrderDuty a rl2:Duty ;
    rl2:subject ex:Trader ;
    rl2:action ex:record ;
    rl2:object ex:AuditRecord .

ex:executeOrderPrivilege a rl2:Privilege ;
    rl2:subject ex:Trader ;
    rl2:action ex:execute ;
    rl2:object ex:Order ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:recordOrderDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:tradingPolicy a rl2:Set ;
    rl2:clause ex:recordOrderDuty, ex:executeOrderPrivilege .
```

## Request and snapshot

Request: `(agent = Trader, action = execute, asset = Order)`.

World snapshot: qualifying evidence records the Trader performing `record` on `AuditRecord` for this order.

## Expected result

When the record Duty is `Fulfilled`, the request is `Permit`; otherwise the execution privilege is inactive.
