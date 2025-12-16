# RL2 Backlog

**Updated:** 2025-12-16

---

## Open Design Decisions

### Namespace URI

**Files:** All TTL files
**Current:**

```turtle
@prefix rl2: <https://rl2.example/ontology#> .
@prefix rl2p: <https://rl2.example/protocol#> .
```

**Options:**
- `https://w3id.org/rl2/` (persistent, recommended for publication)
- Institutional namespace (if internal)

**Status:** Deferred until publication decision

---

### Recurrent Duties

**Problem:** No native periodic recurrence (`FREQ=QUARTERLY`).

**Options:**
- RecurrentDuty subclass with iCal-style rules
- Profile-level extension using owl:time or schema:schedule
- External scheduler generates discrete duty instances

**Complexity:** Each instance needs own obligation state tracking.

**Status:** Open. May be addressable via profiles without core changes.

---

### ODRL owl:imports

**File:** `rl2.ttl`

**Recommendation:** Before publication, add:

```turtle
<https://rl2.example/ontology>
    owl:imports <http://www.w3.org/ns/odrl/2/> .
```

**Status:** Deferred until namespace decision

---

## Work Items

### Phase 1: Core Evaluator

- [ ] Why3/WhyML core modules (Syntax, Environment, ConditionEval, NormEval, PolicyEval)
- [ ] Prove S1 (Determinism), S4 (Duty-state consistency), S6 (Totality)
- [ ] OCaml extraction from Why3
- [ ] CLI for testing: `rl2-eval --policy p.ttl --request r.json`
- [ ] Property-based test suite (qcheck)
- [ ] Validate against use cases 1–10 (Core Patterns)

### Phase 2: Extended Features

- [ ] Promise lifecycle support
- [ ] Violation → remedial duty chains
- [ ] Validate against use cases 11–13 (Data Contracts)

### Future

- [ ] ODRL → RL2 transpiler with clarification reports
- [ ] Protocol/Case lifecycle implementation
- [ ] Hohfeldian correlative validation

---

## Toolchain

**Primary:** Why3/WhyML → OCaml extraction

**Rationale:** 
- WhyML ≈ OCaml (clean extraction)
- Multiple backend provers (Alt-Ergo, Z3, CVC4)
- Escape hatch to Isabelle/Coq for hard lemmas

**Normative artifact:** The extracted OCaml evaluator is the reference implementation. Other implementations conform by matching its behavior.

---

## Success Criteria

RL2 Core is complete when:

- [ ] S1, S4, S6 discharged in Why3
- [ ] OCaml reference evaluator extracted and tested
- [ ] Test suite covers use cases 1–10
- [ ] At least one production implementation tested against reference

---

## Resolved

### Protocol Completeness (2025-12-08)

Implemented universal `rl2p:Requirement` to track Duties, Promises, and Claims uniformly. See RL2_Protocol.md.

### Temporal Classes Simplification (2025-12-07)

Removed `rl2:TemporalConstraint` and `rl2:EffectiveInterval`. All temporal logic now uses `rl2:AtomicConstraint` with `rl2:currentDateTime`.

### Spec Fixes (2025-01-06)

- Created `rl2:RuntimeReference` class
- Added identity-binding SHACL warning
- Hardened path grammar with security requirements
- Clarified Promise vs Duty distinction
