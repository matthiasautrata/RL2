# Legal Review Gate

## Scenario

A vendor may access customer data under an agreement only while the world snapshot establishes that legal review is approved.

## Why it matters

RL2 evaluates the approval fact; it does not standardize the review workflow, signatures, or the creation of the agreement.

## Canonical policy

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://w3id.org/rl2#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Customer a rl2:Agent .
ex:Vendor a rl2:Agent .
ex:CustomerData a rl2:Asset .
ex:access a rl2:Action .
ex:legalReviewApproved a rl2:LeftOperand ;
    rl2:valueType xsd:boolean ;
    rl2:resolutionPath "global.legalReview.approved" .

ex:approvedVendorAccess a rl2:Privilege ;
    rl2:subject ex:Vendor ; rl2:action ex:access ; rl2:object ex:CustomerData ;
    rl2:condition [ a rl2:AtomicConstraint ; rl2:leftOperand ex:legalReviewApproved ;
        rl2:constraintOperator rl2:eq ; rl2:rightOperand true ] .

ex:customerDataAgreement a rl2:Agreement ;
    rl2:grantor ex:Customer ; rl2:grantee ex:Vendor ; rl2:clause ex:approvedVendorAccess .
```

## Request and snapshot

Request: `(Vendor, access, CustomerData)`.

World snapshot: `global.legalReview.approved = true`, attributed to the legal-review system.

## Expected result

Expected decision: `Permit`. A false fact makes the privilege inapplicable; missing, invalid, or conflicting evidence is reported as attributed indeterminacy where evaluation needs that fact.
