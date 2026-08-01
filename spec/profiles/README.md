# RL2 Profiles

Profiles define domain actions, assets, value classes, evidence interpretations, and typed operands without
changing core evaluation semantics.

A profile-defined operand used by `Eval` declares:

- one semantic value type with `rdfs:range`; and
- one `rl2:resolutionPath` into the immutable `WorldSnapshot`.

```turtle
@prefix ex:   <https://example.org/profile#> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

ex:department a rl2:LeftOperand ;
    rdfs:label "Department" ;
    rdfs:range xsd:string ;
    rl2:resolutionPath "agent.department" .
```

Allowed roots are `agent`, `asset`, `context`, `state`, `global`, and the three core `request`
fields. A path is a canonical snapshot key, not a live object traversal or callback.

A policy declares each required profile and minimum compatible version:

```turtle
ex:profile a rl2:Profile ;
    rl2:profileVersion "1.2.0" .

ex:agent a rl2:Agent .
ex:asset a rl2:Asset .
ex:read a rl2:Action .
ex:rule a rl2:Privilege ;
    rl2:subject ex:agent ;
    rl2:action ex:read ;
    rl2:object ex:asset .

ex:policy a rl2:Set ;
    rl2:requiresProfile ex:profile ;
    rl2:clause ex:rule .
```

An evaluator rejects an unsupported required profile before policy derivation. A supported version
is compatible when it has the same major version and is not older than the required version.

The included [privacy profile](rl2-privacy-profile.ttl) is an illustrative vocabulary. It does not
by itself establish compliance with any law.
