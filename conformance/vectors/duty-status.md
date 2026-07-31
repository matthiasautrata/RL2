# Duty and Promise Status Component Vectors

These vectors isolate S2-C2. Each row fixes one canonical clause, an immutable snapshot, and the
expected pure status result. Intervals are half-open. Unless stated otherwise, evidence and facts
are admissible, well typed, and attributable under the supplied configuration.

## Structural boundaries

The following authored forms are SHACL violations rather than evaluator inputs:

- a Duty with neither `action` nor `invariant`;
- a Duty with both `action` and `invariant`;
- a Maintenance Duty with `postCondition`;
- more than one `dutyWindow`;
- a DutyWindow missing either endpoint, using a non-`xsd:dateTimeStamp` endpoint, or satisfying
  `startInclusive >= endExclusive`.

## Achievement Duty

Let `D` require agent `A` to perform action `x` on asset `S` in
`[2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z)`.

| ID | Evaluation time and evidence | Expected result | Decisive rule |
|---|---|---|---|
| A1 | `2026-07-31T23:59:59Z`; none | `Known(Pending)` | Window has not started |
| A2 | `2026-08-15T12:00:00Z`; matching action at `2026-08-10T09:00:00Z` | `Known(Fulfilled)` | A qualifying witness is inside the window |
| A3 | `2026-09-01T00:00:00Z`; only matching action is exactly at that instant | `Known(Violated)` | End is exclusive; the closed window has no witness |
| A4 | `2026-08-20T00:00:00Z`; matching action whose `postCondition` is false | `Known(Active)` | The action is not a qualifying witness and the window remains open |
| A5 | `2026-09-01T00:00:00Z`; same evidence as A4 | `Known(Violated)` | No qualifying witness exists when the window closes |
| A6 | `2026-08-20T00:00:00Z`; matching action whose `postCondition` depends on a missing fact | `IndeterminateStatus({Missing(...)})` | The missing value can change whether the witness qualifies |
| A7 | `2026-10-01T00:00:00Z`; unbounded Duty, no matching evidence | `Known(Active)` | Passage of time cannot violate an unbounded Achievement |

No matching action is not itself a `Missing` error.

## Maintenance Duty

Let `M` require invariant `i` for asset `S` in
`[2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z)`.

| ID | Evaluation time and interval evidence | Expected result | Decisive rule |
|---|---|---|---|
| M1 | Before the start | `Known(Pending)` | Window has not started |
| M2 | Inside the window; complete elapsed coverage establishes `i=True` | `Known(Active)` | The invariant holds, but the period is incomplete |
| M3 | Inside or after the window; one covered cell establishes `i=False` | `Known(Violated)` | One counterexample is decisive even if later cells are true |
| M4 | At the end; complete coverage establishes `i=True` throughout | `Known(Fulfilled)` | The finite period closed cleanly |
| M5 | At the end; one elapsed cell has no value needed by `i` | `IndeterminateStatus({Missing(...)})` | Fulfillment requires complete coverage |
| M6 | Unbounded; `i=True` at the evaluation snapshot | `Known(Active)` | This is an ongoing snapshot requirement, not an interval with an unknown start |
| M7 | Unbounded; `i=False` at the evaluation snapshot | `Known(Violated)` | The current snapshot violates the ongoing requirement |

The evaluator partitions the elapsed interval at the finite boundaries in the snapshot; it does
not sample a continuous clock.

## Promise projection

| ID | Promise content and snapshot | Expected result |
|---|---|---|
| P1 | Promised action; no matching evidence | `Known(Pending)` |
| P2 | Promised action; qualifying evidence exists | `Known(Fulfilled)` |
| P3 | Promised state evaluates true at this snapshot | `Known(Fulfilled)` |
| P4 | The same promised state evaluates false at a later snapshot | `Known(Violated)` |
| P5 | Promised Duty has `Known(Active)` status | `Known(Pending)` |
| P6 | Promised Duty has `IndeterminateStatus(E)` | `IndeterminateStatus(E)` |

P3 and P4 are not a state transition. Promise status is re-derived per snapshot. Acceptance may
turn a promised state into a Maintenance Duty whose finite `dutyWindow` supports a completed
period assessment.

## Resolver sensitivity

Given a definite matching Privilege and a separate independent Duty with indeterminate status,
the decision is `Permit`. The Duty's error remains in `dutyStatuses` and diagnostics but does not
enter access resolution.

If that same Duty is instead attached to the Privilege with `rl2:prerequisiteDuty`, its status is
read during Privilege derivation. `Known(Fulfilled)` permits the Privilege to become a candidate;
`Known(Pending)`, `Known(Active)`, or `Known(Violated)` prevents it; and an outcome-sensitive
`IndeterminateStatus` produces an indeterminate Privilege atom.
