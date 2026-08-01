# Prohibition Fixture

**Disposition:** normalized

An ODRL Prohibition becomes one canonical RL2 Prohibition.

## ODRL 2.2 source

```turtle
@prefix ex: <https://example.org/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

ex:subscriber a odrl:Party .
ex:dataset a odrl:Asset .
ex:redistribute a odrl:Action .

ex:source a odrl:Set ;
    odrl:prohibition [
        a odrl:Prohibition ;
        odrl:assignee ex:subscriber ;
        odrl:action ex:redistribute ;
        odrl:target ex:dataset
    ] .
```

## Expected RL2

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:subscriber a rl2:Agent .
ex:dataset a rl2:Asset .
ex:redistribute a rl2:Action .

ex:prohibition_1 a rl2:Prohibition ;
    rl2:subject ex:subscriber ;
    rl2:prohibitedAction ex:redistribute ;
    rl2:object ex:dataset .

ex:translated a rl2:Set ; rl2:clause ex:prohibition_1 .
```

**Preservation claim:** a matching request contributes a denial candidate.
