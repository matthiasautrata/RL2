# Ordered Constraint Fixture

**Disposition:** rejected

An ordered constraint relation has no deterministic core translation unless an identified profile
defines its ordering semantics.

## ODRL 2.2 source

```turtle
@prefix ex: <https://example.org/> .
@prefix odrl: <http://www.w3.org/ns/odrl/2/> .

ex:user a odrl:Party .
ex:dataset a odrl:Asset .
ex:read a odrl:Action .

ex:source a odrl:Set ;
    odrl:permission [
        odrl:assignee ex:user ;
        odrl:action ex:read ;
        odrl:target ex:dataset ;
        odrl:constraint [
            odrl:andSequence (
              [ odrl:leftOperand odrl:dateTime ;
                odrl:operator odrl:gteq ;
                odrl:rightOperand "2026-01-01T00:00:00Z"^^<http://www.w3.org/2001/XMLSchema#dateTime> ]
              [ odrl:leftOperand odrl:dateTime ;
                odrl:operator odrl:lt ;
                odrl:rightOperand "2026-02-01T00:00:00Z"^^<http://www.w3.org/2001/XMLSchema#dateTime> ]
            )
        ]
    ] .
```

## Expected result

```text
Rejected({UnsupportedOrderedConstraint})
```

**Preservation claim:** rejection is preferable to an importer choosing an unstated interpretation
of the ordering relation.
