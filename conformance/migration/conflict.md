# Conflict Fixture

**Disposition:** clarified

ODRL’s conflict indication is translated to the declared RL2 evaluation strategy. The policy graph
does not silently choose a winner.

## ODRL 2.2 source

```turtle
@prefix ex: <https://example.org/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

ex:user a odrl:Party .
ex:dataset a odrl:Asset .
ex:read a odrl:Action .

ex:source a odrl:Set ;
    odrl:conflict odrl:perm ;
    odrl:permission [ odrl:assignee ex:user ; odrl:action ex:read ; odrl:target ex:dataset ] ;
    odrl:prohibition [ odrl:assignee ex:user ; odrl:action ex:read ; odrl:target ex:dataset ] .
```

## Expected RL2

The importer emits one `rl2:Privilege` and one `rl2:Prohibition` with equal priority. The
translation configuration declares `PermitOverrides` for `odrl:perm`; under that configuration a
matching request evaluates to `Permit`.

**Preservation claim:** the source conflict directive is made explicit in the evaluation
configuration, so independent evaluators apply the same strategy.
