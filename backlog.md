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

**Inventory:** See [usecases/README.md](usecases/README.md)

| Category | Count | Status |
|----------|-------|--------|
| Core Patterns (1-17) | 17 | ✅ Complete |
| External Data Licenses (18-23) | 6 | 📝 Draft |
| Data Contract Patterns (24-31) | 8 | 📝 Draft |
| EU Data Spaces (32-37) | 6 | 📝 Draft |
| Hohfeldian (38-42) | 5 | 📝 Draft |
| Vocabulary (43-49) | 7 | 📝 Draft |
| Protocol (50-51) | 2 | 📝 Draft |
| **Total** | **51** | **17 complete, 34 draft** |

### Priority: Vocabulary Gaps

These demonstrate vocabulary not yet shown in any use case:

| # | Use Case | Demonstrates |
|---|----------|--------------|
| 24 | purpose-restriction | `isAnyOf` |
| 25 | geo-restriction | `isNoneOf` |
| 43 | exclusive-license | `xone` |
| 44 | multi-certification | `isAllOf` |
| 45 | negated-condition | `not` |
| 46 | role-hierarchy | `isA` |
| 38 | claim-counterclaim | `Claim` |
| 27, 40 | approval-revocation, power-to-grant | `Power` |
| 39 | immunity-from-termination | `Immunity` |
| 26 | legal-review-gate | `Offer`/`Agreement` |
| 47 | asset-collection-access | `AssetCollection` |
| 48 | compliance-attestation | `Assertion` |
| 49 | policy-versioning | `policyGeneration` |
| 50 | runtime-evaluation | `rl2p:Requirement` |

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
