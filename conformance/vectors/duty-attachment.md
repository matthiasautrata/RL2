# Duty Attachment Vectors

A prerequisite Duty is structurally attached to a Privilege and is not also a policy clause.
Multiple prerequisites are conjunctive. One prerequisite may be shared by multiple Privileges and
has one derived status.

```turtle
@prefix ex: <https://example.org/> .
@prefix rl2: <https://rl2.example/ontology#> .

ex:alice a rl2:Agent .
ex:document a rl2:Asset .
ex:read a rl2:Action .
ex:pay a rl2:Action .

ex:paymentDuty a rl2:Duty ;
    rl2:subject ex:alice ;
    rl2:action ex:pay ;
    rl2:object ex:document .

ex:readPrivilege a rl2:Privilege ;
    rl2:subject ex:alice ;
    rl2:action ex:read ;
    rl2:object ex:document ;
    rl2:prerequisiteDuty ex:paymentDuty .

ex:policy a rl2:Set ; rl2:clause ex:readPrivilege .
```

| ID | Prerequisite status | Expected access result |
|---|---|---|
| D1 | `Known(Fulfilled)` | `Permit` |
| D2 | `Known(Pending)`, `Known(Active)`, or `Known(Violated)` | `NotApplicable` |
| D3 | applicable prerequisite has outcome-sensitive indeterminacy | `Indeterminate` |
| D4 | prerequisite condition is false | `Permit` |
| D5 | two prerequisites, one fulfilled and one active | `NotApplicable` |

An independent Duty never changes an access decision. A different Privilege can therefore permit
the same request even if another Privilege has an unfulfilled or indeterminate prerequisite.
