# Use Case 26: Legal Review Gate

**Pattern:** Pure Offer acceptance with an Agreement applicability guard

**Scope:** RL2 core transformation

**Status:** SCOPE-2 migrated

## Business rule

> A vendor may access customer data only under accepted terms and while the supplied world
> snapshot establishes legal approval.

Legal review workflow and authorization to issue an Acceptance are outside core RL2. If continuing
approval evidence must gate access, it is an ordinary policy applicability condition. On the
Offer that condition means “this is the guard proposed for the Agreement”; it does not make the
Offer operative and does not control the `materialize` call.

## Source Offer

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:DataOwner a rl2:Agent .
ex:Vendor a rl2:Agent .
ex:CustomerData a rl2:Asset .
ex:access a rl2:Action .

ex:legalApprovalOperand a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "global.legalReview.approved" .

ex:legalApprovalRequired a rl2:AtomicConstraint ;
    rl2:leftOperand ex:legalApprovalOperand ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand true .

ex:vendorAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Vendor ;
    rl2:action ex:access ;
    rl2:object ex:CustomerData .

ex:vendorAccessOffer a rl2:Offer ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Vendor ;
    rl2:condition ex:legalApprovalRequired ;
    rl2:clause ex:vendorAccessPrivilege .
```

Passing this Offer to `Out` produces no atom, even when the approval fact is true.

## Acceptance value

```text
Acceptance(
  agreementId = ex:vendorAccessAgreement,
  grantor      = ex:DataOwner,
  grantee      = ex:Vendor,
  primaryIds   = {
    ex:vendorAccessPrivilege -> ex:vendorAccessPrivilege_A1
  },
  claimIds       = {},
  objectBindings = {},
  dutyWindows    = {}
)
```

Legal review completion is a precondition for the external party deciding to issue this value. It
is not an event consumed by `materialize` and is not encoded as Agreement-formation state.

## Materialized Agreement

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

ex:DataOwner a rl2:Agent .
ex:Vendor a rl2:Agent .
ex:CustomerData a rl2:Asset .
ex:access a rl2:Action .

ex:legalApprovalOperand a rl2:LeftOperand ;
    rdfs:range xsd:boolean ;
    rl2:resolutionPath "global.legalReview.approved" .

ex:legalApprovalRequired a rl2:AtomicConstraint ;
    rl2:leftOperand ex:legalApprovalOperand ;
    rl2:constraintOperator rl2:eq ;
    rl2:rightOperand true .

ex:vendorAccessPrivilege_A1 a rl2:Privilege ;
    rl2:subject ex:Vendor ;
    rl2:action ex:access ;
    rl2:object ex:CustomerData .

ex:vendorAccessAgreement a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Vendor ;
    rl2:condition ex:legalApprovalRequired ;
    rl2:clause ex:vendorAccessPrivilege_A1 ;
    prov:wasDerivedFrom ex:vendorAccessOffer .
```

## Expected evaluation

For request `(Vendor, access, CustomerData)`:

| Snapshot fact `global.legalReview.approved` | Decision |
|---|---|
| `true` | `Permit` |
| `false` | `NotApplicable` |
| missing, invalid, or conflicting | `Indeterminate` with attributed causes |

The source and result use different Privilege identifiers. Reusing
`ex:vendorAccessPrivilege` in the Agreement would violate materialization freshness.

## Workflow boundary

Submission, negotiation, review assignment, rejection, modification, signature, persistence, and
audit-log workflow belong to the non-core protocol work in `../../future/protocol/`. Core RL2
standardizes the Offer value, explicit Acceptance input, resulting Agreement, and evaluation of
the supplied approval fact.
