# Duty Attachment Decision Vectors

**Status:** Normative component vectors for S2-C3

These vectors isolate the interaction between Duty status and access decisions. Unless stated
otherwise, the request matches the shown Privilege, all ordinary conditions are `True`, there is
no matching Prohibition, and the configured strategy is valid.

## Structural boundaries

The following forms are SHACL violations:

- a `prerequisiteDuty` value that is not a Duty;
- a prerequisite Duty that is also a Policy `clause`; and
- a prerequisite Duty referenced by a Privilege that is not a clause of any Policy.

Multiple `prerequisiteDuty` values on one Privilege are conjunctive.
One Duty may be shared by several Privileges; its one derived status is used by every owner.

Canonical positive shape:

```turtle
@prefix ex:  <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:alice a rl2:Agent .
ex:document a rl2:Asset .
ex:read a rl2:Action .
ex:pay a rl2:Action .

ex:policy a rl2:Set ;
    rl2:clause ex:readPrivilege .

ex:readPrivilege a rl2:Privilege ;
    rl2:subject ex:alice ;
    rl2:action ex:read ;
    rl2:object ex:document ;
    rl2:prerequisiteDuty ex:paymentDuty .

ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:alice ;
    rl2:action ex:pay ;
    rl2:object ex:document .
```

## Decision interaction

| ID | Duty relationship and result | Expected access result | Decisive rule |
|---|---|---|---|
| D1 | No Duty | `Permit` | The matching Privilege is active |
| D2 | Independent Duty is `Known(Violated)` | `Permit` | Independent status does not enter access resolution |
| D3 | Independent Duty is indeterminate | `Permit`; error retained in status map and diagnostics | Independent status does not enter access resolution |
| D4 | Prerequisite is applicable and `Known(Fulfilled)` | `Permit` | The prerequisite is satisfied |
| D5 | Prerequisite is applicable and `Known(Pending)` | `NotApplicable` | Its owning Privilege does not become a permit candidate |
| D6 | Prerequisite is applicable and `Known(Active)` | `NotApplicable` | Active is not Fulfilled |
| D7 | Prerequisite is applicable and `Known(Violated)` | `NotApplicable` | Violation does not become a global Deny |
| D8 | Prerequisite status is outcome-sensitive indeterminate | `Indeterminate` | The owning Privilege may or may not become active |
| D9 | Prerequisite applicability is `False`, status is not Fulfilled | `Permit` | An inapplicable prerequisite is not required |
| D10 | Two prerequisites: one Fulfilled, one Active | `NotApplicable` | All applicable prerequisites are required |

## Locality and conflict

| ID | Policy set | Expected access result |
|---|---|---|
| L1 | Privilege A has a Violated prerequisite; Privilege B independently grants the same request | `Permit` from B |
| L2 | Privilege A has an indeterminate prerequisite; Privilege B definitely grants at the same priority under `PermitOverrides` | `Permit` |
| L3 | A matching Prohibition wins under `ProhibitOverrides`; a prerequisite is indeterminate | `Deny`; the prerequisite error remains diagnostic |
| L4 | Privileges A and B share one prerequisite Duty, which is Fulfilled once | Both Privileges may contribute permits for their respective matching requests |

The result is never `PermitWithObligations`: core returns the access verdict and the Duty-status
map separately. Requirement creation and enforcement phases belong to a companion protocol.
