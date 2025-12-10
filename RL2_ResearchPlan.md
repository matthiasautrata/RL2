---
title: "RL2 Research Plan"
subtitle: "Modular, ODRL-Aligned Verification Roadmap"
version: "0.5"
status: "Draft"
date: 2025-12-09
---

# RL2 Research Plan (Modular, ODRL‑Aligned)

This plan reorganizes the original RL2 research program around **ODRL‑derived modules**, with a **common mechanics layer first**, followed by **module‑specific semantics, proofs, and implementation phases**, and a final **integration and transpiler strategy**. The objective is to establish **expressive completeness of RL2‑Core‑ODRL relative to ODRL 2.2**, with additional RL2 capabilities layered incrementally.

---

## Part I — Common Mechanics (Module‑Independent)

### I.1 Objectives

* Provide a **mechanizable semantic core** for rights, duties, and prohibitions.
* Enable a **diagnostic ODRL → RL2 transpiler** that explicitly reports required clarifications.
* Separate **derivation (transformer)** from **conflict & priority resolution** and from **protocol/case tracking**.

### I.2 Layers and Separation of Concerns

1. **Core Semantics Layer**

   * Denotational + small‑step operational semantics
   * Explicit state Σ (events, duties, promises, requirements when enabled)

2. **Resolution Layer**

   * Post‑derivation conflict and priority handling
   * Evaluator‑level, not policy‑embedded

3. **Protocol Layer** (optional module)

   * Cases, requests, requirements, context assertions, traceability

4. **Transpilation Layer**

   * ODRL 2.2 (+ profile) → RL2 modules
   * Emits **clarification reports** for all non‑derivable assumptions

### I.3 Toolchain

* **Why3** as the primary mechanization and proof environment
* **OCaml** as the reference executable evaluator extracted from Why3
* Scala/JVM as a compatible secondary target if required

Guiding principle: proofs must **not block early executability**.

### I.4 Proof Methodology (Staged)

Proof obligations are discharged incrementally by layer. Each obligation is tagged with its target module(s).

#### Stage A — RL2‑Core Safety

**(S1) Determinism of Evaluation** [Modules A–F]
```
∀ Σ, R, Ctx, e:
  (Σ, R, Ctx, e) → (Σ₁, e₁) ∧ (Σ, R, Ctx, e) → (Σ₂, e₂)
  ⇒ Σ₁ = Σ₂ ∧ e₁ = e₂
```

**(S2) Progress** [Modules A–F]
Every closed, well-typed expression either:
- Is a value (Fulfilled, Violated, Permit, Deny, ...), or
- Can take a step

**(S3) Type Preservation** [Modules A–F]
```
Γ ⊢ e : τ ∧ (Σ, R, Ctx, e) → (Σ', e')
⇒ Γ ⊢ e' : τ ∧ Σ' is well-typed
```

**(S4) Duty-State Consistency** [Modules B, C, D]
`DutyState(d)` can never be both `Fulfilled` and `Violated` in the same Σ.

**(S5) Timeout Correctness** [Module B]
```
timeout(c, Σ) = true
⇒ after clock advances past deadline, duty is eventually Violated
```

**(S6) Policy-Evaluation Totality** [Modules A–F]
`Eval(P, R, Σ, Ctx)` terminates and returns a decision in:
`{Permit, Deny, PermitWithDuties, NotApplicable, Indeterminate}`

#### Stage B — RDF Correspondence

**(B1) Syntax Soundness** [All Modules]
SHACL-valid RDF ⇒ well-formed abstract syntax term

**(B2) Semantic Soundness** [All Modules]
SHACL-valid + well-typed ⇒ all semantic functions defined (no ⊥)

**(B3) Semantic Completeness** [All Modules]
Every abstract syntax object has a corresponding SHACL-valid RDF representation

#### Stage C — ODRL Compilation

**(C1) Compilation Correctness** [Modules A–C]
```
∀ ODRL policy P, request R:
  ODRL_eval(P, R) = RL2_eval(C(P), R)
```
modulo clarifications emitted by the transpiler.

**(C2) Expressive Completeness** [Modules A–C]
Every ODRL 2.2 concept has an RL2‑Core‑ODRL representation; RL2 is a semantic superset. Some ODRL constructs (e.g., `odrl:inheritFrom`) require compilation/transformation.

### I.5 Clarification Reports (First‑Class Artifact)

The transpiler output is a triple:

```
( RL2_Policy , Clarifications[] , ProfileAssumptions[] )
```

Clarifications explicitly document:

* Implicit party bindings
* Conflict strategy assumptions
* Collection materialization choices
* Temporal bound extraction
* Identity and subject unification

These reports are **normative** and part of audit output.

---

## Part II — ODRL‑Derived RL2 Modules

Each module has:

* **Scope**
* **ODRL mapping**
* **Semantics & proof obligations**
* **Implementation phase**

### Module A — Privileges & Prohibitions (RL2‑Core‑ODRL)

**Scope**

* Permission, Prohibition
* Targets, Actions, Constraints
* Logical combinations of constraints

**ODRL Mapping**

* odrl:permission → rl2:Privilege
* odrl:prohibition → rl2:Prohibition
* odrl:constraint → rl2:Condition (Atomic, Logical, Temporal)

**Semantics**

* Pure state‑read evaluation
* No protocol or promises required

**Proof Obligations**

* (S1) Determinism — for privilege/prohibition evaluation
* (S6) Totality — constraint evaluation terminates
* (B1–B3) RDF correspondence for rl2:Privilege, rl2:Prohibition, rl2:Condition

**Phase**

* Phase 1

---

### Module B — Duties

**Scope**

* Duties with lifecycle: Pending, Active, Fulfilled, Violated
* Duty performer binding
* Conditional activation

**ODRL Mapping**

* odrl:duty → rl2:Duty
* Permission‑scoped duties become gated privileges

**Semantics**

* Duty activation as state transition
* Fulfillment as external evidence

**Proof Obligations**

* (S4) Duty-state consistency — Fulfilled ⊗ Violated mutual exclusion
* (S5) Timeout correctness — deadline violation
* (S1) Determinism — duty activation/evaluation
* (S2) Progress — duty state machine advances

**Phase**

* Phase 1

---

### Module C — Consequences & Remedies

**Scope**

* Violations
* Remedial duties

**ODRL Mapping**

* odrl:consequence → violation‑triggered duty
* odrl:remedy → remedial duty

**Semantics**

* State‑triggered duty creation

**Proof Obligations**

* (S4) Duty-state consistency — extends to remedial duties
* No orphan remedies — every remedy has a traceable violation
* Violation trace preservation — state Σ records causal chain

**Phase**

* Phase 2

---

### Module D — Promises (Future RL2 Extension)

**Scope**

* Promises and promise state
* Promise → violation → remedial duty chain

**ODRL Status**

* Not native in ODRL 2.2
* Derived from delayed‑commitment patterns

**Proof Obligations**

* Promise-state consistency — analogous to (S4)
* Promise→Duty derivation soundness
* (S1) Determinism — promise evaluation

**Phase**

* Phase 3

---

### Module E — Hohfeldian Correlatives (Future)

**Scope**

* Rights, Claims, Powers, Liabilities
* Explicit correlatives beyond subject/counterparty

**ODRL Status**

* Not present
* Pure RL2 expressive enrichment

**Proof Obligations**

* Correlative consistency — Claim(A,B) ↔ Duty(B,A)
* Power-Liability duality preservation
* (S1) Determinism — correlative derivation
* (B1–B3) RDF correspondence for Hohfeldian types

**Phase**

* Phase 4

---

### Module F — Protocol & Case Lifecycle

**Scope**

* Requests, Cases, Requirements
* ContextAssertions
* Evidence tracking

**ODRL Status**

* Execution and audit layer only

**Proof Obligations**

* Case-state consistency — well-formed lifecycle transitions
* Requirement fulfillment soundness
* (S6) Totality — protocol-level evaluation terminates
* Evidence integrity assumptions (parameterized)

**Phase**

* Phase 3–4

---

## Part III — Integration and Roadmap

### III.1 RL2‑Core‑ODRL Definition

RL2‑Core‑ODRL consists of:

* Privileges
* Prohibitions
* Duties
* Consequences & remedies
* Atomic + logical + temporal conditions

This is the **minimum target** for full ODRL 2.2 coverage.

### III.2 Transpiler Strategy

1. Normalize ODRL input to atomic form
2. Compile to RL2‑Core‑ODRL
3. Emit clarification report
4. Optionally lift to Promises, Protocol, or Hohfeld modules

### III.3 Conflict Strategy Placement

* ODRL conflict strategies are compiled into the **evaluator configuration**
* They are **not embedded as RL2 policy semantics**

### III.4 Phased Deliverables

**Phase 1 — RL2‑Core Skeleton**

* Why3 core modules
* OCaml evaluator for Modules A–B

**Phase 2 — Consequences & Violations**

* Module C
* Violation proofs

**Phase 3 — Protocol & Promises**

* Modules D and F

**Phase 4 — Hohfeld & Advanced Correlatives**

* Module E

### III.5 Deliverables

**Deliverable A: Why3 Semantics Modules**

```
RL2_Semantics_Why3/
├── Syntax.mlw           # Abstract syntax datatypes
├── Types.mlw            # Type system
├── Environment.mlw      # State and environment
├── ConditionEval.mlw    # Condition evaluation
├── NormEval.mlw         # Norm evaluation
├── DutyLifecycle.mlw    # Duty state machine
├── PolicyEval.mlw       # Policy evaluation
└── Proofs/
    ├── Determinism.mlw
    ├── Preservation.mlw
    ├── StateInvariants.mlw
    └── ConstraintAlgebra.mlw
```

**Deliverable B: OCaml Reference Evaluator**

Extracted from Why3:
* Pure, side-effect-free evaluator kernel
* CLI for testing: `rl2-eval --policy p.ttl --request r.json`
* Property-based test suite (qcheck)

**Deliverable C: ODRL→RL2 Transpiler**

* Formal compiler `C : ODRL → RL2`
* Clarification report generator
* Semantic preservation proof outline

### III.6 Success Criteria

RL2 mechanization is complete when:

- [ ] (S1, S4, S6) discharged in Why3 for Phase 1 modules
- [ ] OCaml reference evaluator extracted and tested
- [ ] Test suite covers all RL2‑Core‑ODRL constructs
- [ ] (C1, C2) established for Modules A–C
- [ ] Clarification reports normatively documented
- [ ] At least one production implementation tested against OCaml reference

### III.7 What This Is NOT

* Not a new syntax standard
* Not a UI or enforcement engine
* Not a conformance test suite (yet)

---

## Open Research Questions

* Formal semantics of clarification reports
* External lookup instantiation
* Dynamic asset collection materialization
* Cryptographic evidence anchoring
* Controlled concurrency and event races

---

## Strategic Positioning

* RL2 acts as:

  * A **semantic profile** of ODRL 2.2
  * A **candidate semantic foundation** for a future ODRL 3.x
* The ODRL → RL2 transpiler serves as:

  * A compiler
  * A semantic debugger
  * A standards negotiation instrument

---

*End of Modular RL2 Research Plan*
