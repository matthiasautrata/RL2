# Snapshot Resolution Vectors

These vectors isolate world-snapshot normalization and lookup. `C` supports the declared profile
and accepts the stated attributions. Rows F5–F7 and E3–E5 additionally configure `C.admissibility`
(`RL2_Model.md` §4.4) with the stated `allowedSources`/`maxAge`/`evidenceSigners` entry for the
key or Duty in question; a row that does not mention `C.admissibility` leaves it absent for that
path or Duty, so every candidate is admitted regardless of attribution.

| ID | Input | Expected result |
|---|---|---|
| F1 | Two valid facts for one key have equal semantic values. | `Ok(value)` |
| F2 | Two valid facts for one single-valued key have distinct semantic values. | `Err(Conflict({site: SnapshotSite(key.path), target: None}))` |
| F3 | No valid fact exists for the requested key and evaluation time. | `Err(Missing({site: SnapshotSite(key.path), target: None}))` |
| F4 | The only candidate fact for a key has an unsupported (wrong-typed) value. `C.admissibility` is absent for this path. | `Err(Invalid({site: SnapshotSite(key.path), target: None}))` |
| F5 | The only candidate fact for a key is well-typed but its `attribution.source` is outside the configured `allowedSources` entry for this path. | filtered before the empty/type/conflict rules run; `Err(Missing({site: SnapshotSite(key.path), target: None}))`, since no candidate survives — the same outcome as F3, not `Invalid` |
| F6 | A `maxAge` entry is configured for this path, but the only candidate fact has no `attribution.observedAt` at all. | the absent-attribution rule (`RL2_Model.md` §4.4) fails the filter deterministically; `Err(Missing({site: SnapshotSite(key.path), target: None}))` |
| F7 | Two candidate facts for one key have equal semantic values; one's `attribution.source` is outside the configured `allowedSources` entry, the other's is inside. | the inadmissible candidate is filtered before matching begins; the admissible candidate alone resolves the key: `Ok(value)` |
| F8 | One fact identifier denotes unequal normalized records. | snapshot invalid; `Eval` returns `Indeterminate` with an empty envelope |
| E1 | A matching, admissible action record is inside the selector interval. | included in `Ok(evidence)` |
| E2 | The only otherwise matching action record occurs after evaluation time. | excluded from `Ok(evidence)` |
| E3 | A matching action record's `attribution.issuer` is outside the `evidenceSigners` entry configured for this Duty (`RL2_Model.md` §4.4 — keyed by `sourceIdentity(d)`, not by selector shape). | excluded from `Ok(evidence)`, exactly as if it had never matched; no error, no distinct cause — if it was the only match, `Ok(empty)` |
| E4 | An `evidenceSigners` entry is configured for this Duty, but the only matching action record has no `attribution.issuer` at all. | the absent-attribution rule fails the filter deterministically; excluded from `Ok(evidence)`, no error |
| E5 | Every action record matching the selector is filtered out by `evidenceSigners` (none has an admitted issuer). | `Ok(empty)` — the same "not yet established" outcome as no match at all, never a distinct error |
| E6 | One evidence identifier denotes unequal normalized records. | snapshot invalid; `Eval` returns `Indeterminate` with an empty envelope |

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
