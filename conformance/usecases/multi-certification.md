# Multiple Required Certifications

## Scenario

A classified-data service permits a named contractor to access a dataset only when the contractor
holds every required certification. Certification issuance, validity, and trust are represented by
admissible snapshot data under the governing profile.

## Why it matters

`isAllOf` tests whether the right-hand set is a subset of the left-hand set.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix certification: <https://example.org/profile/certification#> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Contractor a rl2:Agent .
ex:ClassifiedDataset a rl2:Asset .
ex:access a rl2:Action .

certification:held a rl2:LeftOperand ;
    rl2:valueType rl2:ValueSet ;
    rl2:resolutionPath "agent.certifications" .

certification:Clearance a certification:Type .
certification:ProjectAccess a certification:Type .
certification:EthicsTraining a certification:Type .

ex:certifiedAccess a rl2:Privilege ;
    rl2:subject ex:Contractor ;
    rl2:action ex:access ;
    rl2:object ex:ClassifiedDataset ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:leftOperand certification:held ;
        rl2:constraintOperator rl2:isAllOf ;
        rl2:rightOperandSet [
            a rl2:ValueSet ;
            rl2:valueMember certification:Clearance,
                certification:ProjectAccess,
                certification:EthicsTraining
        ]
    ] .

ex:policy a rl2:Set ; rl2:clause ex:certifiedAccess .
```

## Request and snapshot

Request: `(Contractor, access, ClassifiedDataset)`. The snapshot fact `agent.certifications` is
the set `{Clearance, ProjectAccess, EthicsTraining}`.

## Expected result

The decision is `Permit`. Omitting any required member makes the rule inapplicable. A profile may
derive the set from credentials, but credential processing is outside the evaluator.
