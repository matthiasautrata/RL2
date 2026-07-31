# WorldSnapshot Resolution Vectors

**Status:** Normative component vectors for S2-C1

These vectors test snapshot normalization and lookup independently of policy derivation. Times are
semantic instants. `C` supports the declared profile and accepts the shown attributions.

## S1 — Equal fact assertions agree

```text
evaluationTime = 2026-08-01T12:00:00Z
key = (AgentScope(ex:alice), "agent.department")
facts = {
  (ex:f1, key, "Research", [2026-01-01, ∞), source=ex:hr),
  (ex:f2, key, "Research", [2026-06-01, ∞), source=ex:directory)
}

resolveFact(key, String, profile, W, C) = Ok("Research")
```

Different assertion identifiers and sources do not conflict when the semantic values agree.

## S2 — Distinct single-valued facts conflict

Use S1 but change `ex:f2`'s value to `"Finance"`.

```text
resolveFact(key, String, profile, W, C) = Err(Conflict(key))
```

Source order, assertion identifiers, and observation time do not choose a winner.

## S3 — Validity and scope are exact

```text
evaluationTime = 2026-08-01T12:00:00Z
facts = {
  (ex:f1, (AgentScope(ex:alice), "agent.department"), "Research",
          [2025-01-01, 2026-01-01), source=ex:hr),
  (ex:f2, (AgentScope(ex:bob), "agent.department"), "Finance",
          [2026-01-01, ∞), source=ex:hr)
}
```

Resolution for Alice returns `Err(Missing(key))`: her assertion is expired, and Bob's currently
valid assertion is in another scope.

## S4 — Conflicting identifier reuse invalidates the snapshot

```text
facts = {
  (ex:f1, key, "Research", [2026-01-01, ∞), source=ex:hr),
  (ex:f1, key, "Finance",  [2026-01-01, ∞), source=ex:hr)
}

validateSnapshot(W, C) = { Invalid(SnapshotSite(facts)) }
Eval(U, R, W, C).decision = Indeterminate
Eval(U, R, W, C).normativeEnvelope = empty
Eval(U, R, W, C).dutyStatuses = empty
Eval(U, R, W, C).promiseStatuses = empty
```

If both records were normalized-field equal, normalization would collapse them instead.

## S5 — Equal latest evidence projections agree

```text
evaluationTime = 2026-08-01T12:00:00Z
selector = (kinds={ex:Approval}, actor=ex:alice, object=ex:dataset, ...)
evidence = {
  (ex:e1, ex:Approval, 2026-08-01T10:00:00Z, ex:alice, ex:approve,
          ex:dataset, {level: 2}, source=ex:workflowA),
  (ex:e2, ex:Approval, 2026-08-01T10:00:00Z, ex:alice, ex:approve,
          ex:dataset, {level: 2}, source=ex:workflowB)
}

projectLatestEvidence(selector, "level", Integer, W, C) = Ok(2)
```

## S6 — Unequal latest evidence projections conflict

Use S5 but set `ex:e2.payload.level = 3`.

```text
projectLatestEvidence(selector, "level", Integer, W, C) = Err(Conflict(selector))
```

Neither evidence identifier is a tie-breaker.

## S7 — Future evidence is ineligible

With `evaluationTime = 2026-08-01T12:00:00Z`, evidence occurring at
`2026-08-01T12:00:01Z` is excluded. If it is the only otherwise matching item:

```text
existsEvidence(selector, W, C) = Ok(false)
projectLatestEvidence(selector, field, expectedType, W, C) = Err(Missing(selector))
```

## S8 — Relevant inadmissible evidence is invalid, not absent

If an otherwise matching evidence item lacks attribution required by the selector's profile:

```text
existsEvidence(selector, W, C) = Err(Invalid(selector))
```

The evaluator does not reinterpret untrusted evidence as proof that the event did not occur.

## S9 — A latest item missing the projected field is invalid

Use two equally latest matching evidence items. Let `ex:e1.payload.level = 2` and omit `level`
from `ex:e2.payload`:

```text
projectLatestEvidence(selector, "level", Integer, W, C) = Err(Invalid(selector))
```

The same result applies when `ex:e2.payload.level` exists with the wrong type. `Missing` is
reserved for the case where no eligible evidence item exists.
