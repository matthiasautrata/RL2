# Erasure Request

## Scenario

A controller must erase a data subject’s personal data when a valid erasure request is present in the evaluation snapshot.

## Why it matters

The policy makes the requested action and beneficiary explicit while leaving identity
verification and request intake to the snapshot assembler.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Controller a rl2:Agent .
ex:DataSubject a rl2:Agent .
ex:PersonalData a rl2:Asset .
ex:erase a rl2:Action .

ex:erasureRequestValid a rl2:LeftOperand ;
    rdfs:range <http://www.w3.org/2001/XMLSchema#boolean> ;
    rl2:resolutionPath "asset.erasureRequestValid" .

ex:erasePersonalDataDuty a rl2:Duty ;
    rl2:subject ex:Controller ;
    rl2:counterparty ex:DataSubject ;
    rl2:action ex:erase ;
    rl2:object ex:PersonalData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:erasureRequestValid ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] .

ex:privacyPolicy a rl2:Agreement ;
    rl2:grantor ex:Controller ;
    rl2:grantee ex:DataSubject ;
    rl2:clause ex:erasePersonalDataDuty .
```

## Request and snapshot

Request: `(agent = Controller, action = erase, asset = PersonalData)`.

World snapshot: the asset-scoped fact `asset.erasureRequestValid` is `true`, attributed to the
system that verified DataSubject's request.

## Expected result

The Duty is `Active` and the envelope contains an obligation to erase. The evaluator reports the obligation; it does not erase data.
