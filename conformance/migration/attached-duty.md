# Attached Duty Fixture

**Disposition:** normalized

An ODRL Duty attached to a Permission becomes an RL2 prerequisite Duty rather than an independent
policy clause.

## ODRL 2.2 source

```turtle
@prefix ex: <https://example.org/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

ex:user a odrl:Party .
ex:dataset a odrl:Asset .
ex:read a odrl:Action .
ex:pay a odrl:Action .

ex:source a odrl:Set ;
    odrl:permission [
        odrl:assignee ex:user ;
        odrl:action ex:read ;
        odrl:target ex:dataset ;
        odrl:duty [ odrl:action ex:pay ; odrl:target ex:dataset ]
    ] .
```

## Expected RL2

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:user a rl2:Agent .
ex:dataset a rl2:Asset .
ex:read a rl2:Action .
ex:pay a rl2:Action .

ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:user ;
    rl2:action ex:pay ;
    rl2:object ex:dataset .

ex:readPrivilege a rl2:Privilege ;
    rl2:subject ex:user ;
    rl2:action ex:read ;
    rl2:object ex:dataset ;
    rl2:prerequisiteDuty ex:paymentDuty .

ex:translated a rl2:Set ; rl2:clause ex:readPrivilege .
```

**Preservation claim:** the read Privilege contributes a permit only when the applicable payment
Duty is fulfilled.
