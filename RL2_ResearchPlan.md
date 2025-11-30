# RL2 Research Plan: Toward Mechanized Semantics

*Consolidated roadmap for formal verification of RL2*

---

## Executive Summary

RL2's semantics are explicitly designed for mechanization. This document consolidates the research plan for:

1. **Mechanizing RL2 semantics** in Why3, K, or Lean 4
2. **Proving soundness and completeness** of the ontology-semantics correspondence
3. **Establishing expressive completeness** relative to ODRL

The goal: Transform RL2 from *well-specified* to *formally verified*, making it the first rights/policy language with mechanically checked semantics.

---

## Current State

### What RL2 Already Provides

The RL2 specification suite provides a near-executable semantics:

| Component | Document | Mechanization Fit |
|-----------|----------|-------------------|
| Abstract syntax (algebraic grammar) | RL2_Semantics.md | Maps directly to inductive datatypes |
| Typed ontology with SHACL shapes | RL2_Core.md | Well-formedness preconditions |
| Denotational semantics | RL2_Semantics.md | Pure functions `⟦e⟧ : Env → Value` |
| Operational semantics | RL2_Semantics.md | Small-step transitions, inductive predicates |
| Runtime protocol | RL2_Protocol.md | State Σ, request/response lifecycle |

The semantics are written in a style that anticipates mechanization:

> "The specification is designed for both human comprehension and mechanization (e.g., Why3/Lean), providing the foundation for verifiable policy-evaluation kernels."

---

## Prior Art in ODRL Formalization

RL2 builds on significant prior work formalizing ODRL:

| Work | Contribution | Limitation |
|------|--------------|------------|
| [Pucella-Weissman 2006] | First formal semantics; decidability (NP-hard) | No operational semantics |
| [Steyskal-Polleres 2015] | Action dependencies, rule-based reasoning | Limited to static analysis |
| [Fornara-Colombetti 2017] | Operational semantics for obligations | Apache Jena-specific |
| [W3C ODRL Formal Semantics] | Evaluator behavior, state of the world | Still draft; gaps remain |
| [Cicala-Fornara-Harth 2025] | Identifies specification gaps | Analysis only |

**Key gap RL2 addresses**: None of the above provides a *complete* operational semantics with explicit duty lifecycle state machines suitable for verified implementation.

---

## Tool Selection

### Primary: Why3

**Rationale**: Best match for RL2's design style.

| RL2 Feature | Why3 Capability |
|-------------|-----------------|
| Algebraic data types | Native support |
| Pure evaluation functions | First-class |
| Small-step operational rules | Inductive predicates |
| SHACL constraints | Expressible as preconditions |
| Determinism proofs | Standard technique |

**Ecosystem**: Backend provers (Alt-Ergo, Z3, CVC5) for automation; Coq/Isabelle for complex lemmas.

**Estimated effort**: 2-4 weeks for polished semantics + basic metatheory.

### Alternative: K Framework

**Rationale**: Executable semantics directly from formal definition.

- Rewrite-based: small-step rules map naturally
- Produces interpreter automatically
- Used for production languages (JavaScript, C)
- Better for *testing* semantics against examples

**Trade-off**: Less mature proof infrastructure than Why3/Coq.

### Alternative: Lean 4

**Rationale**: Modern, active community, code extraction.

- Strong type system, dependent types
- Tactic framework for proof automation
- Extract executable code
- AI integration (AlphaProof)

**Trade-off**: Steeper learning curve; younger ecosystem.

### Recommendation

**Start with Why3** for the formal companion. Use **K Framework** in parallel to create an executable reference implementation for validation. Consider **Lean 4** for future work or if AI-assisted proving becomes valuable.

---

## Proof Obligations

The following properties must be proved to establish RL2 as fully verified:

### Safety Properties (S1-S6)

**(S1) Determinism of Evaluation**
```
∀ Σ, R, Ctx, e:
  (Σ, R, Ctx, e) → (Σ₁, e₁) ∧ (Σ, R, Ctx, e) → (Σ₂, e₂)
  ⇒ Σ₁ = Σ₂ ∧ e₁ = e₂
```

**(S2) Progress**
Every closed, well-typed expression either:
- Is a value (Fulfilled, Violated, Permit, Deny, ...), or
- Can take a step

**(S3) Type Preservation**
```
Γ ⊢ e : τ ∧ (Σ, R, Ctx, e) → (Σ', e')
⇒ Γ ⊢ e' : τ ∧ Σ' is well-typed
```

**(S4) Duty-State Consistency**
`ObligationState(d)` can never be both `Fulfilled` and `Violated` in the same Σ.

**(S5) Timeout Correctness**
```
timeout(c, Σ) = true
⇒ after clock advances past deadline, duty is eventually Violated
```

**(S6) Policy-Evaluation Totality**
`Eval(P, R, Σ, Ctx)` terminates and returns a decision in:
`{Permit, Deny, PermitWithObligations, NotApplicable, Indeterminate}`

### Soundness/Completeness Properties

**(B1) Syntax Soundness**
SHACL-valid RDF ⇒ well-formed abstract syntax term

**(B2) Semantic Soundness**
SHACL-valid + well-typed ⇒ all semantic functions defined (no ⊥)

**(B3) Semantic Completeness**
Every abstract syntax object has a corresponding SHACL-valid RDF representation

### ODRL Coverage Properties

**(C1) Compilation Correctness**
```
∀ ODRL policy P, request R:
  ODRL_eval(P, R) = RL2_eval(C(P), R)
```

**(C2) Expressive Completeness**
Every ODRL construct has an RL2 equivalent; RL2 is a strict superset.

---

## Phased Implementation Plan

### Phase 1: Mechanization Setup (Weeks 1-2)

1. **Translate abstract syntax to Why3 datatypes**
   ```why3
   type norm =
     | Privilege agent action asset condition
     | Duty agent action asset condition
     | Prohibition agent action asset condition
     | Claim agent agent right
     | Power agent norm
     | Liability agent norm
     | Immunity agent norm
   ```

2. **Implement denotational functions**
   - `eval_condition : condition → env → bool`
   - `eval_norm : norm → request → env → norm_result`

3. **Implement operational predicates**
   - `predicate step (σ: state) (e: expr) (σ': state) (e': expr)`

4. **Import SHACL grammar as preconditions**

### Phase 2: Core Metatheory Proofs (Weeks 3-4)

1. Prove (S1) Determinism
2. Prove (S2) Progress
3. Prove (S3) Preservation
4. Prove (S4) Duty-state consistency
5. Prove (B1) Syntax soundness
6. Prove (B3) Syntax completeness

### Phase 3: ODRL Compilation Correctness (Weeks 5-6)

1. Define formal compiler `C : ODRL → RL2`
2. Prove (C1) semantic preservation
3. Prove (C2) expressive completeness
4. Document corner cases (inheritance, conflicts)

### Phase 4: Documentation & Validation (Week 7+)

1. Produce "RL2 Mechanized Semantics v1.0" companion document
2. Create test suite with ODRL examples compiled to RL2
3. Validate against K Framework executable semantics
4. Release reference evaluator kernel

---

## Deliverables

### Deliverable A: Why3 Semantics Companion

```
RL2_Semantics_Why3/
├── Syntax.mlw           # Abstract syntax datatypes
├── Types.mlw            # Type system
├── Environment.mlw      # State and environment
├── ConditionEval.mlw    # Condition evaluation
├── NormEval.mlw         # Norm evaluation
├── DutyLifecycle.mlw    # Duty state machine
├── EventSemantics.mlw   # Event processing
├── PolicyEval.mlw       # Policy evaluation
└── Proofs/
    ├── Determinism.mlw
    ├── Preservation.mlw
    ├── StateInvariants.mlw
    └── ConstraintAlgebra.mlw
```

### Deliverable B: Semantic IR Specification

Standalone document defining:
- Canonical AST for RL2
- Normal form for Conditions
- Canonical form for Policies (flattened, desugared)
- Translation: RDF/SHACL → AST → IR

### Deliverable C: ODRL→RL2 Compilation Semantics

Formal specification of compiler `C`:
- Mapping table (ODRL construct → RL2 construct)
- Translation rules
- Semantic preservation proof outline
- Corner cases documentation

### Deliverable D: Reference Evaluator

Extracted/implemented evaluator kernel:
- Pure, side-effect-free
- Verified against Why3 proofs (or K semantics)
- Test suite coverage

---

## Open Questions

### Not Yet Addressed

1. **Concurrency**: Semantics is single-threaded; real deployments may need concurrent duty tracking

2. **Asset Collection Materialization**: `dynamicQuery` termination/finiteness must be proved per profile

3. **External Context**: `lookupExternal` is parameterized; each deployment must instantiate and verify

4. **Cryptographic Evidence**: If events are signed, crypto layer must guarantee integrity (RL2 assumes tamper-evident Σ)

### Design Decisions Needed

1. **Tool choice**: Why3 vs Lean 4 for primary mechanization
2. **Executable semantics**: K Framework for validation?
3. **Extraction target**: OCaml, Rust, or verified C?

---

## Success Criteria

RL2 mechanization is complete when:

- [ ] All proof obligations (S1-S6, B1-B3, C1-C2) discharged in proof assistant
- [ ] Reference evaluator extracted and tested
- [ ] K Framework executable semantics validates same examples
- [ ] Companion document published
- [ ] Test suite covers all ODRL 2.2 constructs

**Outcome**: RL2 becomes the first rights/policy language with:
- Fully mechanized semantics
- Deterministic, verifiable duty lifecycle
- Formally defined strict superset of ODRL
- Verified evaluator kernel

---

## References

See **RL2_References.md** for complete citations.

Key sources for this plan:
- [Why3] Filliâtre & Paskevich, 2013
- [K Framework] Roșu, 2017
- [Lean 4] de Moura et al., 2021
- [Pucella-Weissman 2006] First ODRL formalization
- [Fornara-Colombetti 2017] ODRL operational semantics
