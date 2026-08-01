# Permission Fixture

**Disposition:** normalized

An ODRL Permission becomes one canonical RL2 Privilege.

## ODRL 2.2 source

```turtle
@prefix ex: <https://example.org/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

ex:subscriber a odrl:Party .
ex:dataset a odrl:Asset .
ex:read a odrl:Action .

ex:source a odrl:Set ;
    odrl:permission [
        a odrl:Permission ;
        odrl:assignee ex:subscriber ;
        odrl:action ex:read ;
        odrl:target ex:dataset
    ] .
```

## Expected RL2

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:subscriber a rl2:Agent .
ex:dataset a rl2:Asset .
ex:read a rl2:Action .

ex:permission_1 a rl2:Privilege ;
    rl2:subject ex:subscriber ;
    rl2:action ex:read ;
    rl2:object ex:dataset .

ex:translated a rl2:Set ; rl2:clause ex:permission_1 .
```

**Preservation claim:** a matching request can receive a permit when no higher-priority applicable
prohibition determines another result.
