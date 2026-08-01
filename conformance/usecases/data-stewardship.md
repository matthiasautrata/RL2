# Data Stewardship Commitment

## Scenario

A data owner offers access to a researcher who promises to perform a stewardship action. After acceptance, access applies only once the resulting Duty is fulfilled.

## Why it matters

The example demonstrates the core Offer-to-Agreement transformation without prescribing a workflow or a persistent case model.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:DataOwner a rl2:Agent .
ex:Researcher a rl2:Agent .
ex:SensitiveData a rl2:Asset .
ex:steward a rl2:Action .
ex:access a rl2:Action .

ex:stewardshipPromise a rl2:Promise ;
    rl2:subject ex:Researcher ;
    rl2:counterparty ex:DataOwner ;
    rl2:action ex:steward ;
    rl2:object ex:SensitiveData .

ex:offeredAccess a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:stewardshipPromise ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:stewardshipOffer a rl2:Offer ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:stewardshipPromise, ex:offeredAccess .

ex:stewardshipDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:counterparty ex:DataOwner ;
    rl2:action ex:steward ;
    rl2:object ex:SensitiveData .

ex:acceptedAccess a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:stewardshipDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:stewardshipAgreement a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:stewardshipDuty, ex:acceptedAccess .
```

## Request and snapshot

Request: `(agent = Researcher, action = access, asset = SensitiveData)` against `stewardshipAgreement`.

World snapshot: qualifying evidence records the Researcher performing `steward` on `SensitiveData`.

## Expected result

The materialized `stewardshipDuty` is `Fulfilled` and the request is `Permit`. Before that evidence exists, the access privilege is inactive.
