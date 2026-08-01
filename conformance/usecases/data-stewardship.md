# Use Case 8: Data Stewardship Promise

**Pattern:** Offer-local Promise dependency rewritten on acceptance

**Scope:** RL2 core transformation and evaluation

**Status:** SCOPE-2 migrated

## Business rule

> A data owner offers access to a researcher who undertakes to perform a stewardship action.
> Access applies only after the accepted stewardship Duty has been fulfilled.

The Promise and dependent Privilege are siblings in one Offer. The Offer is non-operative: its
Privilege cannot grant access. Acceptance crystallizes the Promise into an Achievement Duty and
rewrites the Privilege's Promise-status query into a Duty-status query.

The researcher identity is structural rather than a second condition: the Promise names the
researcher as `promisor`, and the Privilege names the same agent as `subject`. Materialization
allows the Promise parties only in the accepted grantor/grantee pair.

## Source Offer

```turtle
@prefix ex:  <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:DataOwner a rl2:Agent .
ex:Researcher a rl2:Agent .
ex:SensitiveData a rl2:Asset .
ex:steward a rl2:Action .
ex:access a rl2:Action .

ex:stewardshipPromise a rl2:Promise ;
    rl2:promisor ex:Researcher ;
    rl2:promisee ex:DataOwner ;
    rl2:promisedAction ex:steward ;
    rl2:object ex:SensitiveData .

ex:dataAccessPrivilege a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:stewardshipPromise ;
        rl2:leftOperand rl2:promiseStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:stewardshipOffer a rl2:Offer ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:stewardshipPromise, ex:dataAccessPrivilege .
```

## Acceptance value

```text
Acceptance(
  agreementId = ex:stewardshipAgreement,
  grantor      = ex:DataOwner,
  grantee      = ex:Researcher,
  primaryIds   = {
    ex:stewardshipPromise -> ex:stewardshipDuty,
    ex:dataAccessPrivilege -> ex:dataAccessPrivilege_A1
  },
  claimIds       = { ex:stewardshipPromise -> ex:stewardshipClaim },
  objectBindings = {},
  dutyWindows    = {}
)
```

## Materialized Agreement

```turtle
@prefix ex:   <https://example.org/> .
@prefix rl2:  <https://rl2.example/ontology#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

ex:DataOwner a rl2:Agent .
ex:Researcher a rl2:Agent .
ex:SensitiveData a rl2:Asset .
ex:steward a rl2:Action .
ex:access a rl2:Action .

ex:stewardshipDuty a rl2:Duty ;
    rl2:subject ex:Researcher ;
    rl2:counterparty ex:DataOwner ;
    rl2:action ex:steward ;
    rl2:object ex:SensitiveData .

ex:stewardshipClaim a rl2:Claim ;
    rl2:subject ex:DataOwner ;
    rl2:counterparty ex:Researcher ;
    rl2:correlativeTo ex:stewardshipDuty .

ex:dataAccessPrivilege_A1 a rl2:Privilege ;
    rl2:subject ex:Researcher ;
    rl2:action ex:access ;
    rl2:object ex:SensitiveData ;
    rl2:condition [
        a rl2:AtomicConstraint ;
        rl2:targetNorm ex:stewardshipDuty ;
        rl2:leftOperand rl2:obligationStateOperand ;
        rl2:constraintOperator rl2:eq ;
        rl2:rightOperandRef rl2:Fulfilled
    ] .

ex:stewardshipAgreement a rl2:Agreement ;
    rl2:grantor ex:DataOwner ;
    rl2:grantee ex:Researcher ;
    rl2:clause ex:stewardshipDuty, ex:stewardshipClaim,
               ex:dataAccessPrivilege_A1 ;
    prov:wasDerivedFrom ex:stewardshipOffer .
```

## Expected evaluation

For request `(Researcher, access, SensitiveData)`:

| Snapshot evidence | Duty status | Decision |
|---|---|---|
| A qualifying `steward` action by Researcher on SensitiveData | `Fulfilled` | `Permit` |
| No qualifying stewardship evidence | `Active` | `NotApplicable` |
| The same evidence, but a request by another agent | `Fulfilled` | `NotApplicable` |

Passing the source Offer directly to `Out` always contributes no atom. `NotApplicable` is not a
global denial: another operative policy may independently permit the request.

## Migration note

The earlier encoding used profile operands over mutable `state.Promises` fields and asserted
`rl2:promiseState`. Those forms are removed. Promise status is derived from evidence, and the
accepted Agreement queries the crystallized Duty.
