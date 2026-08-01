# Snapshot Resolution Vectors

These vectors isolate world-snapshot normalization and lookup. `C` supports the declared profile
and accepts the stated attributions.

| ID | Input | Expected result |
|---|---|---|
| F1 | Two valid facts for one key have equal semantic values. | `Ok(value)` |
| F2 | Two valid facts for one single-valued key have distinct semantic values. | `Err(Conflict({site: SnapshotSite(key.path), target: None}))` |
| F3 | No valid fact exists for the requested key and evaluation time. | `Err(Missing({site: SnapshotSite(key.path), target: None}))` |
| F4 | A fact has an unsupported type or inadmissible attribution. | `Err(Invalid({site: SnapshotSite(key.path), target: None}))` |
| F5 | One fact identifier denotes unequal normalized records. | snapshot invalid; `Eval` returns `Indeterminate` with an empty envelope |
| E1 | A matching, admissible action record is inside the selector interval. | included in `Ok(evidence)` |
| E2 | The only otherwise matching action record occurs after evaluation time. | excluded from `Ok(evidence)` |
| E3 | A matching action record has inadmissible attribution. | `Err(Invalid({site: EvidenceSelector, target: None}))` |
| E4 | One evidence identifier denotes unequal normalized records. | snapshot invalid; `Eval` returns `Indeterminate` with an empty envelope |

For example, equal facts from two sources agree:

```text
evaluationTime = 2026-08-01T12:00:00Z
key = (AgentScope(ex:alice), "agent.department")
facts = {
  (ex:f1, key, "Research", [2026-01-01, infinity), source=ex:hr),
  (ex:f2, key, "Research", [2026-06-01, infinity), source=ex:directory)
}
resolveFact(key, String, profile, W, C) = Ok("Research")
```

Order, source identifiers, and observation times never select one of two unequal values.
