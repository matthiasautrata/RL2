# Collection Access

## Scenario

A data catalog grants a researcher access to every dataset directly listed in a clinical-outcomes
collection. A collection is an asset, so it may be the object of a Privilege. Request matching
uses direct `member` links in the supplied policy universe.

## Why it matters

Direct collection membership gives finite, inspectable matching without implicit recursive
expansion.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .

ex:Researcher a rl2:Agent .
ex:access a rl2:Action .
ex:Demographics a rl2:Asset .
ex:Outcomes a rl2:Asset .

ex:ClinicalOutcomes a rl2:AssetCollection ;
    rl2:member ex:Demographics, ex:Outcomes .

ex:collectionAccess a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:ClinicalOutcomes .

ex:catalogTerms a rl2:Set ; rl2:clause ex:collectionAccess .
```

## Request and snapshot

Request: `(Researcher, access, Demographics)`. No snapshot facts are required.

## Expected result

The decision is `Permit`; the same holds for `Outcomes`. Nested collections are not transitively
expanded, so broader coverage requires explicit membership or distinct clauses.
