# Classification-Based Targeting

## Scenario

A data-governance policy permits any agent to read any asset classified as home-loan data, and
independently requires logging of that access. The policy names neither an agent nor an asset: the
classification tag stated as an asset-scoped fact selects the population on both sides of the norm.

## Why it matters

This is tag/classifier-driven targeting, not enumerated membership: `rl2:subject rl2:anyAgent` and
`rl2:object rl2:anyAsset` match unconditionally, and the shared `asset.classification eq
ex:HomeLoan` condition delimits which requests the policy actually reaches. The same condition
gates both an independent Privilege and an independent Duty, so a matching request is both
permitted and obligated.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:read a rl2:Action .
ex:logAccess a rl2:Action .

ex:dataClassification a rl2:LeftOperand ;
    rdfs:range ex:Classification ;
    rl2:resolutionPath "asset.classification" .

ex:Classification a rdfs:Class .
ex:HomeLoan a ex:Classification .

ex:homeLoanReadPrivilege a rl2:Privilege ;
    rl2:subject rl2:anyAgent ;
    rl2:action ex:read ;
    rl2:object rl2:anyAsset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:dataClassification ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef ex:HomeLoan
    ] .

ex:homeLoanAccessLogDuty a rl2:Duty ;
    rl2:subject rl2:anyAgent ;
    rl2:object rl2:anyAsset ;
    rl2:action ex:logAccess ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand ex:dataClassification ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef ex:HomeLoan
    ] .

ex:homeLoanPolicy a rl2:Set ;
    rl2:clause ex:homeLoanReadPrivilege, ex:homeLoanAccessLogDuty .
```

## Request and snapshot

Request: some agent reads asset `ex:LoanBook2026`.

World snapshot: `asset.classification = ex:HomeLoan` for `LoanBook2026`.

## Expected result

The decision for the `read` request is `Permit` — the Privilege matches on subject and object via
the sentinels, and the classification condition holds. The independent logging Duty matches the
same population, but an independent Duty contributes its `obligate` atom only to a request for its
own action: a request for `ex:logAccess` on `LoanBook2026` yields that atom, and the Duty's
derived status is queryable for any request. The `read` envelope therefore carries the Permit
alone (see `attestation-gating.md` for the same locality in the gating direction). A request for
an asset classified other than `ex:HomeLoan` makes the condition false on both clauses, so the
decision is `NotApplicable`. A missing `asset.classification` fact makes the condition `Unknown`,
so the result is `Indeterminate`, not `Permit` or `NotApplicable`.
