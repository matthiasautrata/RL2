# No Redistribution

## Scenario

A bank may use licensed market data but must not provide the raw data to a third party. A legally required disclosure is outside the prohibition.

## Why it matters

Redistribution is distinct from ordinary use. An explicit prohibition makes the negative result deterministic even when another policy permits use of the same data.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Vendor a rl2:Agent .
ex:Bank a rl2:Agent .
ex:MarketData a rl2:Asset .
ex:redistribute a rl2:Action .
ex:requiredDisclosure a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "context.requiredDisclosure" .

ex:noRedistribution a rl2:Prohibition ;
    rl2:subject ex:Bank ; rl2:action ex:redistribute ; rl2:object ex:MarketData ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:requiredDisclosure ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand false ] .

ex:marketDataAgreement a rl2:Agreement ;
    rl2:grantor ex:Vendor ; rl2:grantee ex:Bank ; rl2:clause ex:noRedistribution .
```

## Request and snapshot

Request: `(Bank, redistribute, MarketData)`.

World snapshot: `context.requiredDisclosure = false`, supplied by the bank’s compliance service.

## Expected result

Expected decision: `Deny`. With a verified required disclosure (`true`), this prohibition does not match; any permission for that disclosure must be supplied separately.
