# No Machine-learning Training

## Scenario

A publisher licenses a text corpus for search and display but forbids using it to train a machine-learning model.

## Why it matters

AI training is a distinct action with distinct commercial and governance consequences. A dedicated prohibition avoids treating it as an unspecified form of “use.”

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Publisher a rl2:Agent .
ex:Licensee a rl2:Agent .
ex:TextCorpus a rl2:Asset .
ex:search a rl2:Action .
ex:trainModel a rl2:Action .

ex:searchCorpus a rl2:Privilege ;
    rl2:subject ex:Licensee ; rl2:action ex:search ; rl2:object ex:TextCorpus .
ex:noTraining a rl2:Prohibition ;
    rl2:subject ex:Licensee ; rl2:action ex:trainModel ; rl2:object ex:TextCorpus .

ex:corpusLicence a rl2:Agreement ;
    rl2:grantor ex:Publisher ; rl2:grantee ex:Licensee ;
    rl2:clause ex:searchCorpus, ex:noTraining .
```

## Request and snapshot

Request: `(Licensee, trainModel, TextCorpus)`; world snapshot: no additional facts are required.

## Expected result

Expected decision: `Deny`. A request to search the corpus is `Permit`.
