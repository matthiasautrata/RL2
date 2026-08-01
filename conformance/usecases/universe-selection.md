# Policy Selection Provenance

## Scenario

A publisher may retain several policy editions, but RL2 evaluation interprets only the immutable
policy universe supplied by the caller. Selection of an edition, its publication status, and its
identifier are application provenance, not policy semantics.

## Why it matters

Explicit universe selection makes evaluation reproducible without embedding lifecycle state in
the policy language.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Subscriber a rl2:Agent .
ex:Dataset a rl2:Asset .
ex:read a rl2:Action .

ex:readDataset a rl2:Privilege ;
    rl2:subject ex:Subscriber ;
    rl2:action ex:read ;
    rl2:object ex:Dataset .

ex:terms a rl2:Set ; rl2:clause ex:readDataset .
```

## Request and snapshot

Request: `(Subscriber, read, Dataset)`. The caller supplies `ex:terms` in the policy universe; no
snapshot facts are required.

## Expected result

The decision is `Permit`. The application may record the selected universe's identifier or digest.
Selecting another universe is a different evaluation input.
