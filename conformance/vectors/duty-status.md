# Duty and Promise Status Vectors

Intervals are half-open. Every vector uses admissible, typed evidence unless it explicitly tests
an error.

## Achievement Duty

For a Duty requiring action `x` in `[2026-08-01, 2026-09-01)`:

| ID | Evaluation time and evidence | Expected status |
|---|---|---|
| A0 | The applicability condition is false. | `Known(Pending)` |
| A1 | Before the window; no witness. | `Known(Pending)` |
| A2 | During the window; a qualifying witness is inside it. | `Known(Fulfilled)` |
| A3 | At the end; the only witness is at the end instant. | `Known(Violated)` |
| A4 | During the window; a witness fails its postcondition. | `Known(Active)` |
| A5 | At the end; no qualifying witness exists. | `Known(Violated)` |
| A6 | A witness’s postcondition depends on missing data. | `IndeterminateStatus({Missing({site: SnapshotSite(...), target: None})})` |
| A7 | Unbounded Duty; no witness. | `Known(Active)` |

No matching action evidence is not a missing-data error.

## Maintenance Duty

For an invariant over `[2026-08-01, 2026-09-01)`:

| ID | Evaluation time and evidence | Expected status |
|---|---|---|
| M1 | Before the window. | `Known(Pending)` |
| M2 | During the window; the invariant holds over elapsed coverage. | `Known(Active)` |
| M3 | During or after the window; one covered instant establishes false. | `Known(Violated)` |
| M4 | At the end; complete coverage establishes true throughout. | `Known(Fulfilled)` |
| M5 | At the end; required elapsed coverage is missing. | `IndeterminateStatus({Missing({site: SnapshotSite(...), target: None})})` |
| M6 | Unbounded; true at the evaluation snapshot. | `Known(Active)` |
| M7 | Unbounded; false at the evaluation snapshot. | `Known(Violated)` |

## Promise Status

| ID | Content | Expected status |
|---|---|---|
| P1 | Promised action with no matching evidence. | `Known(Pending)` |
| P2 | Promised action with a qualifying witness. | `Known(Fulfilled)` |
| P3 | Promised state true at this snapshot. | `Known(Fulfilled)` |
| P4 | Promised state false at this snapshot. | `Known(Violated)` |
| P5 | Relevant status evaluation is indeterminate. | `IndeterminateStatus(errors)` |

Statuses are derived from the supplied snapshot on every evaluation; none is a stored transition.
