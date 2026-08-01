# Information Barrier

## Scenario

An investment-banking employee must not read an unpublished research report. The restriction no longer applies after publication evidence is present.

## Why it matters

The example expresses a publication-dependent prohibition using a snapshot fact, without modelling document lifecycle transitions.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:InvestmentBanker a rl2:Agent .
ex:ResearchAnalyst a rl2:Agent .
ex:ResearchReport a rl2:Asset .
ex:read a rl2:Action .

ex:reportPublished a rl2:LeftOperand ;
    rl2:valueType xsd:boolean ;
    rl2:resolutionPath "asset.publication.published" .

ex:unpublishedReportProhibition a rl2:Prohibition ;
    rl2:subject ex:InvestmentBanker ;
    rl2:action ex:read ;
    rl2:object ex:ResearchReport ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:reportPublished ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand false
    ] .

ex:publishedReportPrivilege a rl2:Privilege ;
    rl2:subject ex:InvestmentBanker ;
    rl2:action ex:read ;
    rl2:object ex:ResearchReport ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:reportPublished ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperand true
    ] .

ex:analystReadPrivilege a rl2:Privilege ;
    rl2:subject ex:ResearchAnalyst ;
    rl2:action ex:read ;
    rl2:object ex:ResearchReport .

ex:informationBarrierPolicy a rl2:Set ;
    rl2:clause ex:unpublishedReportProhibition, ex:publishedReportPrivilege,
        ex:analystReadPrivilege .
```

## Request and snapshot

Request: `(agent = InvestmentBanker, action = read, asset = ResearchReport)`.

World snapshot: `asset.publication.published` is `false` before publication and `true` afterwards.

## Expected result

Before publication the request is `Deny`; afterwards it is `Permit`. The analyst’s separate privilege is unaffected.
