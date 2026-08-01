# Display versus Non-display Use

## Scenario

A market-data subscriber may display quotations to named users but may not use the quotations for automated trading.

## Why it matters

Actions, rather than ambiguous labels on a general “use” action, preserve the distinction between human display and machine use.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Vendor a rl2:Agent .
ex:Subscriber a rl2:Agent .
ex:QuotationFeed a rl2:Asset .
ex:display a rl2:Action .
ex:automatedTrade a rl2:Action .

ex:displayQuotation a rl2:Privilege ;
    rl2:subject ex:Subscriber ; rl2:action ex:display ; rl2:object ex:QuotationFeed .
ex:noAutomatedTrading a rl2:Prohibition ;
    rl2:subject ex:Subscriber ; rl2:prohibitedAction ex:automatedTrade ; rl2:object ex:QuotationFeed .

ex:displayLicence a rl2:Agreement ;
    rl2:grantor ex:Vendor ; rl2:grantee ex:Subscriber ;
    rl2:clause ex:displayQuotation, ex:noAutomatedTrading .
```

## Request and snapshot

Request: `(Subscriber, display, QuotationFeed)`; world snapshot: no additional facts are required.

## Expected result

Expected decision: `Permit`. For `(Subscriber, automatedTrade, QuotationFeed)`, the expected decision is `Deny`.
