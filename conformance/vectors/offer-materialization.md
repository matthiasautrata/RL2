# Offer Materialization Vectors

`materialize(Offer, Acceptance)` is pure. It reads neither a world snapshot nor external state and
returns either one complete Agreement and a source map, or a canonical non-empty error set.

## Positive mappings

| ID | Source content | Expected Agreement content |
|---|---|---|
| M1 | Promise with `Achieve(x)` body and object `s` | Achievement Duty with promisor as subject, promisee as counterparty, action `x`, object `s` |
| M2 | M1 with a supplied finite window | The same Duty with that `dutyWindow` |
| M3 | Promise with `Maintain(i)` body and object `s` | Maintenance Duty with invariant `i` and object `s` |
| M4 | Promise has no object; Acceptance supplies `s` | Duty uses `s` |
| M5 | An `obligationStateOperand` condition targets a sibling Promise | `targetNorm` rebinds to the corresponding Duty; the operand is unchanged |
| M6 | Offer Privilege has an attached prerequisite Duty | Both receive Agreement-local identifiers; the Duty remains attached |
| M7 | Offer has an applicability condition and parties agree | Agreement copies the condition and records derivation provenance |
| M8 | Unaccepted Offer supplied to `Out` | No normative atom is derived |

Materialization generates one Duty for every Promise.

## Rejections

| ID | Defect | Expected diagnostic |
|---|---|---|
| R1 | A Promise lacks both content properties | rejected by canonical projection |
| R2 | No authored or accepted object | `MissingPromiseObject` |
| R3 | Authored and accepted objects conflict | `InvalidOffer(..., ConflictingObjectBinding)` |
| R4 | Promise parties differ from the accepted pair | `PartyMismatch` |
| R5 | Output identifiers collide or reuse a source IRI | `InvalidIdentityAllocation` |
| R6 | A local reference has no primary identifier | `DanglingInternalReference` |
| R7 | The Offer has a status-dependency cycle | `InvalidOffer(..., StatusDependencyCycle)` |
| R8 | A supplied window is not a finite increasing interval | `InvalidDutyWindow` |

Equal Offer and Acceptance values produce structurally equal results. The source Offer remains
unchanged, output identifiers are isolated between Acceptances, and local references are rewritten
only through the source map.
