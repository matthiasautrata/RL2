# RL2 Backlog

**Updated:** 2025-12-16

---

## Open Design Decisions

### Namespace URI

**Current:** `https://rl2.example/ontology#`  
**Options:** `https://w3id.org/rl2/` (persistent) or institutional  
**Status:** Deferred until publication

### Recurrent Duties

**Problem:** No native periodic recurrence (`FREQ=QUARTERLY`)  
**Options:** RecurrentDuty subclass, profile extension, external scheduler  
**Status:** Open — may be profile-level

### ODRL owl:imports

Add `owl:imports <http://www.w3.org/ns/odrl/2/>` before publication  
**Status:** Deferred until namespace decision

---

## Use Cases

**51 use cases, 17 complete.** See [usecases/README.md](usecases/README.md) for details.

---

## Work Items

### Phase 1: Core Evaluator

- [ ] Why3/WhyML core modules
- [ ] Prove S1 (Determinism), S4 (Duty-state consistency), S6 (Totality)
- [ ] OCaml extraction
- [ ] CLI: `rl2-eval --policy p.ttl --request r.json`
- [ ] Property-based tests (qcheck)
- [ ] Validate against use cases 1–17

### Phase 2: Extended Features

- [ ] Promise lifecycle
- [ ] Violation → remedial duty chains
- [ ] Validate against use cases 18–37

### Future

- [ ] ODRL → RL2 transpiler
- [ ] Protocol/Case lifecycle
- [ ] Profiles: external-data-license, ids-dataspace, privacy

---

## Toolchain

**Primary:** Why3/WhyML → OCaml extraction

**Rationale:** WhyML ≈ OCaml (clean extraction), multiple provers, escape hatch to Isabelle/Coq

**Normative artifact:** Extracted OCaml evaluator is the reference implementation

---

## Success Criteria

- [ ] S1, S4, S6 discharged in Why3
- [ ] OCaml reference evaluator tested
- [ ] Test suite covers use cases 1–17
- [ ] Vocabulary 100% demonstrated
- [ ] One production implementation tested against reference

---

## Resolved

| Date | Decision |
|------|----------|
| 2025-12-08 | Protocol: Universal `rl2p:Requirement` for Duties, Promises, Claims |
| 2025-12-07 | Temporal: Removed TemporalConstraint/EffectiveInterval; use AtomicConstraint |
| 2025-01-06 | Spec fixes: RuntimeReference, identity-binding SHACL, path grammar |
