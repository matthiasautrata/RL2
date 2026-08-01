# Offer Materialization Vectors

**Status:** Normative component vectors for S2-C4

These vectors test the pure helper
`materialize(Offer, Acceptance) → MaterializationResult`. They do not invoke `Eval`, read a
WorldSnapshot, or create protocol effects. The complete positive graph is Use Case 52,
`../usecases/sla-credit-clause.md`.

## Positive mappings

| ID | Source | Acceptance parameters | Expected result |
|---|---|---|---|
| M1 | `PromisedAction(x)` with object `s` | Distinct Duty/Claim IDs; no window | Achievement Duty `(promisor, promisee, x, s, True, None, None)` plus correlative Claim |
| M2 | `PromisedAction(x)` with object `s` | Distinct IDs; finite window `w` | As M1 with `dutyWindow=w` |
| M3 | `PromisedState(i)` with object `s` | Distinct IDs; no window | Ongoing Maintenance Duty `(promisor, promisee, s, True, i, None)` plus Claim |
| M4 | `PromisedAction(x)` with no authored object | Acceptance binds object `s` | Achievement Duty with `action=x` and `object=s` |
| M5 | `PromisedState(i)` with no authored object | Acceptance binds object `s` and finite window `w` | Windowed Maintenance Duty with `object=s` and `invariant=i` |
| M6 | Offer Privilege owns an attached prerequisite Duty | Both have distinct primary IDs | Privilege is an Agreement clause; copied Duty remains attached and is not promoted to a clause |
| M7 | Copied condition uses `promiseStateOperand` targeting sibling Promise `p` | `primaryIds[p]=d` | `obligationStateOperand` targeting Duty `d` |
| M8 | Offer declares the same parties as Acceptance | Complete injective identity maps | Agreement copies the Offer applicability condition/metadata, records `prov:wasDerivedFrom`, and contains no Promise |
| M9 | Unaccepted Offer contains a matching Privilege | Any Request and snapshot | `Out` receives no atom from the Offer |

For M1–M8, `Materialized(agreement,sourceMap)` is returned. The Duty is authored with
`subject=promisor` and `counterparty=promisee`; its Claim has the reverse roles and only one
authored content link, `correlativeTo=duty`.

### M6 worked locality graph

The incoming `affectsNorm` reference from another policy does not change ownership. The Duty is
local to the Offer because it is attached through `prerequisiteDuty`; materialization copies that
attachment. The external Set remains unchanged and continues to reference the source Duty.

```turtle
@prefix ex:  <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:Owner a rl2:Agent .
ex:User a rl2:Agent .
ex:Administrator a rl2:Agent .
ex:Dataset a rl2:Asset .
ex:access a rl2:Action .
ex:signTerms a rl2:Action .

ex:termsDuty a rl2:Duty ;
    rl2:subject ex:User ;
    rl2:counterparty ex:Owner ;
    rl2:action ex:signTerms ;
    rl2:object ex:Dataset .

ex:accessPrivilege a rl2:Privilege ;
    rl2:subject ex:User ;
    rl2:action ex:access ;
    rl2:object ex:Dataset ;
    rl2:prerequisiteDuty ex:termsDuty .

ex:offer a rl2:Offer ;
    rl2:grantor ex:Owner ;
    rl2:grantee ex:User ;
    rl2:clause ex:accessPrivilege .

ex:administrativePower a rl2:Power ;
    rl2:subject ex:Administrator ;
    rl2:affectsNorm ex:termsDuty .

ex:administrativePolicy a rl2:Set ;
    rl2:clause ex:administrativePower .
```

With `primaryIds[accessPrivilege]=accessPrivilege_A1` and
`primaryIds[termsDuty]=termsDuty_A1`, the Agreement contains
`accessPrivilege_A1 prerequisiteDuty termsDuty_A1`; only `accessPrivilege_A1` is an Agreement
clause. `administrativePower affectsNorm termsDuty` is not rewritten because that Power is outside
the Offer.

## Rejections

| ID | Defect | Expected error |
|---|---|---|
| R1 | `PromisedDuty(d)` | `UnsupportedPromiseContent(p,PromisedDuty)` |
| R2 | Promised action/state has no authored or accepted object | `MissingPromiseObject(p)` |
| R3 | Authored object and a different accepted binding both exist | `InvalidOffer(site,ConflictingObjectBinding)` |
| R4 | Promise parties are not the accepted grantor/grantee pair | `PartyMismatch(p)` |
| R5 | Agreement, primary, or Claim identifiers collide or reuse any IRI occurring in the source Offer projection | `InvalidIdentityAllocation(id)` |
| R6 | A source-clause reference has no primary-ID entry | `DanglingInternalReference(site,target)` |
| R7 | `promisorOperand` targets a Promise in materialized content | `UnsupportedPromiseReference(site,p,promisorOperand)` |
| R8 | A profile-defined operand targets a Promise without a profile transformation | `UnsupportedPromiseReference(site,p,operand)` |
| R9 | The Offer's status-dependency graph contains a cycle | `InvalidOffer(site,StatusDependencyCycle)` |
| R10 | Rewriting otherwise produces a structurally invalid Agreement | `InvalidOffer(site,InvalidOutputShape)` |
| R11 | An identity/object/window map has a key outside its required source domain | `InvalidOffer(site,InvalidAcceptanceDomain)` |
| R12 | A supplied Duty window has `startInclusive >= endExclusive` | `InvalidDutyWindow(p)` |
| R13 | A Promise-valued target is outside the containing Offer | `InvalidOffer(site,NonLocalPromiseTarget)` |
| R14 | Promise `p` has a primary error and its absent output would cause only derivative dangling/output-shape errors | The primary error is returned; those derivative errors are suppressed |

Every rejection returns the complete canonical error set and no partial Agreement. Errors that
would arise only because a primarily invalid Promise generated no Duty are suppressed; unrelated
errors remain in the set.

## Determinism and locality

| ID | Property | Required observation |
|---|---|---|
| P1 | Repeatability | Equal Offer and Acceptance values produce structurally equal results |
| P2 | Acceptance isolation | Two Acceptances with disjoint identifier allocations produce Agreements with no shared clause IDs |
| P3 | Source immutability | Materialization does not modify the Offer |
| P4 | Snapshot independence | Changing a WorldSnapshot cannot change materialization because no snapshot is an input |
| P5 | Bounded execution | Traversal is linear in normalized Offer nodes and references with indexed maps |
| P6 | Reference locality | `correlativeTo`, `affectsNorm`, `exposedTo`, `immuneFrom`, and `targetNorm` targets are rewritten exactly when independently local; external targets retain their source identity |
