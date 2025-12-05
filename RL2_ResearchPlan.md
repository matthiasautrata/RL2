# RL2 Research Plan: Toward Mechanized Semantics

*Consolidated roadmap for formal verification of RL2*

---

## Executive Summary

RL2's semantics are explicitly designed for mechanization. This document consolidates the research plan for:

1. **Mechanizing RL2 semantics** with proofs of correctness
2. **Producing an executable reference implementation** that cannot drift from the specification
3. **Establishing expressive completeness** relative to ODRL

The goal: Transform RL2 from *well-specified* to *formally verified*, making it the first rights/policy language with mechanically checked semantics — while remaining **practical enough for enterprise adoption**.

---

## Guiding Principles

### The Balance We Must Strike

Any mechanization approach must satisfy multiple stakeholders:

| Stakeholder | Requirement |
|-------------|-------------|
| **Regulators** | Credible formal foundation; machine-checked proofs exist |
| **Academics** | Rigorous semantics; soundness/completeness established |
| **Engineers** | Readable spec; can implement without learning type theory |
| **Enterprise leadership** | No "black magic"; no single-point-of-failure expertise |
| **Auditors** | Implementation provably matches specification |

**The critical constraint**: If the formal artifacts require exotic expertise that only one engineer possesses, the approach fails regardless of mathematical soundness. Leadership will (rightly) reject betting the firm on one person's Coq/Agda/K knowledge.

### What We Can Defensibly Claim

The toolchain must support these statements to regulators and auditors:

> "RL2's semantics are fully specified and machine-checked using formal methods. The production evaluator is tested against a verified reference implementation extracted from the formal specification."

This is comparable to AWS Cedar, Google Zanzibar, and DAML — without requiring exotic expertise.

---

## Toolchain Decision

### Primary Path: Why3 → OCaml

After evaluating alternatives, **Why3 with OCaml extraction** is the recommended approach:

| Criterion | Why3 + OCaml | Coq/Lean/Agda | K Framework |
|-----------|--------------|---------------|-------------|
| Readable by engineers | ✓ WhyML ≈ ML | ✗ Dependent types | ~ Rewrite rules |
| Proof automation | ✓ SMT backends | ~ Manual tactics | ✗ Limited |
| Executable output | ✓ OCaml extraction | ✓ Extraction | ✓ Interpreter |
| Enterprise credibility | ✓ Jane Street uses OCaml | ✗ "Academic" | ✗ Obscure |
| Bus factor | ✓ Multiple engineers can learn | ✗ Specialist required | ✗ Specialist required |
| Fallback to JVM | ✓ Scala is ML-family | ~ Possible | ✗ Difficult |

**Why Why3?**

1. **RL2's pseudo-code is already 80% WhyML.** The translation is nearly mechanical.

2. **OCaml is a real production language.** Jane Street runs a trading firm on it. That's credibility no dependent-type language has in enterprise finance.

3. **Proofs exist but don't block development.** Engineers work with the OCaml reference; formal proofs are checked but not maintained daily.

4. **Multiple backend provers.** Alt-Ergo, Z3, CVC5 for automation; Coq/Isabelle escalation path for difficult lemmas.

5. **No single wizard required.** Why3/OCaml can be learned by competent engineers. It's not homotopy type theory.

### Alternatives Considered

**Coq / Lean 4 / Agda**

Strong proof assistants with dependent types. Rejected because:
- Steep learning curve creates single-point-of-failure risk
- "Academic" perception undermines enterprise buy-in
- No regulator will read or understand the proofs anyway

**K Framework**

Powerful for executable semantics and symbolic execution. Considered as enhancement but not primary because:
- Smaller community; harder to hire expertise
- Why3's OCaml extraction already provides executable reference
- Can be added later if symbolic execution becomes valuable

**TLA+**

Excellent for distributed systems, but RL2 is a language semantics problem, not a distributed protocol problem.

### Fallback Strategy

If organizational pressure requires JVM deployment:
- OCaml semantics remain the verified reference
- Scala implementation tested against OCaml reference (property-based testing)
- Scala and OCaml are both ML-family; translation is straightforward

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

### Industry Precedents

RL2's approach is comparable to other formally-backed policy systems:

| System | Formal Approach | Production Language |
|--------|-----------------|---------------------|
| AWS Cedar | Lean proofs + Dafny | Rust |
| Google Zanzibar | Internal verification | Go |
| DAML | Formally specified | Haskell/Scala |
| Tezos Michelson | Mi-Cho-Coq | OCaml |

RL2 follows the same pattern: formal proofs backing a practical implementation.

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
Every ODRL concept has an RL2 representation; RL2 is a semantic superset (see RL2_ODRL_Coverage.md). Some ODRL constructs (e.g., `odrl:inheritFrom`) require compilation/transformation.

---

## Phased Implementation Plan

### Phase 1: Why3 Mechanization (Weeks 1-3)

**Goal**: Translate RL2 semantics to Why3; prove core safety properties.

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

4. **Prove safety properties**
   - (S1) Determinism
   - (S4) Duty-state consistency
   - (S6) Totality

### Phase 2: OCaml Reference Extraction (Weeks 4-5)

**Goal**: Produce executable reference evaluator from Why3.

1. **Extract OCaml code** from verified Why3 modules
2. **Build reference evaluator CLI** that takes RL2 policies and requests
3. **Create test suite** covering all RL2 constructs
4. **Validate** against hand-worked examples from RL2_White_Paper.md

### Phase 3: Metatheory Completion (Weeks 6-8)

**Goal**: Complete remaining proofs.

1. Prove (S2) Progress
2. Prove (S3) Preservation
3. Prove (S5) Timeout correctness
4. Prove (B1-B3) Syntax soundness/completeness
5. Document any lemmas requiring Coq/Isabelle escalation

### Phase 4: ODRL Compilation Correctness (Weeks 9-10)

**Goal**: Formal ODRL→RL2 compiler with semantic preservation.

1. Define formal compiler `C : ODRL → RL2`
2. Prove (C1) semantic preservation
3. Prove (C2) expressive completeness
4. Document corner cases (inheritance, conflicts)

### Phase 5: Documentation & Release (Weeks 11-12)

**Goal**: Publishable artifacts.

1. "RL2 Mechanized Semantics v1.0" companion document
2. Release OCaml reference evaluator
3. Test suite with ODRL examples compiled to RL2
4. Integration guidance for production implementations

---

## Deliverables

### Deliverable A: Why3 Semantics Module

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

### Deliverable B: OCaml Reference Evaluator

Extracted from Why3:
- Pure, side-effect-free evaluator kernel
- CLI for testing: `rl2-eval --policy p.ttl --request r.json`
- Property-based test suite (QuickCheck/qcheck)

### Deliverable C: Semantic IR Specification

Standalone document defining:
- Canonical AST for RL2
- Normal form for Conditions
- Canonical form for Policies (flattened, desugared)
- Translation: RDF/SHACL → AST → IR

### Deliverable D: ODRL→RL2 Compiler Specification

Formal specification of compiler `C`:
- Mapping table (ODRL construct → RL2 construct)
- Translation rules
- Semantic preservation proof outline
- Corner cases documentation

---

## What We Explicitly Do NOT Do

To maintain focus and avoid over-engineering:

1. **No Coq/Lean/Agda as primary tools.** Why3 with Coq escalation path is sufficient.

2. **No K Framework (initially).** OCaml extraction provides executable semantics. K can be added later if symbolic execution is needed.

3. **No verified C/Rust extraction.** OCaml reference is the verified artifact; production implementations are tested against it.

4. **No concurrent semantics (yet).** Single-threaded semantics first; concurrency is future work.

These decisions can be revisited based on actual needs, but the default is pragmatic minimalism.

---

## Open Questions

### Not Yet Addressed

1. **Concurrency**: Semantics is single-threaded; real deployments may need concurrent duty tracking

2. **Asset Collection Materialization**: `dynamicQuery` termination/finiteness must be proved per profile

3. **External Context**: `lookupExternal` is parameterized; each deployment must instantiate and verify

4. **Cryptographic Evidence**: If events are signed, crypto layer must guarantee integrity (RL2 assumes tamper-evident Σ)

### Future Enhancements (Not in Scope)

1. **K Framework executable semantics** for symbolic execution and model checking
2. **Verified Rust/C extraction** for performance-critical deployments
3. **Lean 4 port** if AI-assisted proving becomes valuable

---

## Success Criteria

RL2 mechanization is complete when:

- [ ] Safety properties (S1, S4, S6) discharged in Why3
- [ ] OCaml reference evaluator extracted and tested
- [ ] Test suite covers all RL2 constructs
- [ ] Companion document published
- [ ] At least one production implementation tested against OCaml reference

**Outcome**: RL2 becomes the first rights/policy language with:
- Mechanized semantics (Why3)
- Verified reference evaluator (OCaml)
- Formal ODRL superset proof
- Practical enterprise adoption path

---

## What We Can Tell Stakeholders

### For Regulators

> "RL2's semantics are fully specified and machine-checked using formal methods (SMT solvers, interactive proof). The production evaluator is continuously tested against a verified reference implementation."

### For Academics

> "RL2 is defined by a canonical small-step operational semantics with mechanized proofs of determinism, type preservation, and duty-state consistency."

### For Engineers

> "You only need the pseudo-code specification to implement RL2. The Why3 proofs and OCaml reference ensure we don't accidentally break the semantics."

### For Enterprise Leadership

> "This approach is comparable to AWS Cedar and Google Zanzibar. It provides material risk reduction without requiring exotic expertise. Multiple engineers can maintain the formal artifacts."

---

## References

See **RL2_References.md** for complete citations.

Key sources for this plan:
- [Why3] Filliâtre & Paskevich, 2013
- [K Framework] Roșu, 2017
- [Lean 4] de Moura et al., 2021
- [Pucella-Weissman 2006] First ODRL formalization
- [Fornara-Colombetti 2017] ODRL operational semantics
- [AWS Cedar] Bozic et al., 2023 — Formal verification of authorization policies
