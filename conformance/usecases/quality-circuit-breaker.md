# Data-Quality Circuit Breaker

## Scenario

Users may access a market-data feed while its reported error rate is at most five percent. Access is prohibited above that threshold.

## Why it matters

The evaluator makes a deterministic decision from a quality measurement in the snapshot. It does not maintain a circuit-breaker state or repair the feed.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Subscriber a rl2:Agent .
ex:DataTeam a rl2:Agent .
ex:MarketDataFeed a rl2:Asset .
ex:QualityIncident a rl2:Asset .
ex:read a rl2:Action .
ex:report a rl2:Action .

ex:errorRate a rl2:LeftOperand ;
    rdfs:range xsd:decimal ;
    rl2:resolutionPath "asset.quality.errorRate" .

ex:readFeedPrivilege a rl2:Privilege ;
    rl2:subject ex:Subscriber ;
    rl2:action ex:read ;
    rl2:object ex:MarketDataFeed ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:errorRate ;
        rl2:constraintOperator rl2:lte ;
        rl2:rightOperand "0.05"^^xsd:decimal
    ] .

ex:poorQualityProhibition a rl2:Prohibition ;
    rl2:subject ex:Subscriber ;
    rl2:prohibitedAction ex:read ;
    rl2:object ex:MarketDataFeed ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:errorRate ;
        rl2:constraintOperator rl2:gt ;
        rl2:rightOperand "0.05"^^xsd:decimal
    ] .

ex:reportIncidentDuty a rl2:Duty ;
    rl2:subject ex:DataTeam ;
    rl2:action ex:report ;
    rl2:object ex:QualityIncident ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:errorRate ;
        rl2:constraintOperator rl2:gt ;
        rl2:rightOperand "0.05"^^xsd:decimal
    ] .

ex:qualityPolicy a rl2:Set ;
    rl2:clause ex:readFeedPrivilege, ex:poorQualityProhibition, ex:reportIncidentDuty .
```

## Request and snapshot

Request: `(agent = Subscriber, action = read, asset = MarketDataFeed)`.

World snapshot: `asset.quality.errorRate` is `0.02` or `0.08`.

## Expected result

At `0.02`, the request is `Permit`. At `0.08`, it is `Deny` and the incident-reporting Duty is active.
