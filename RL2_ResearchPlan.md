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

Proof obligations are discharged incrementally by layer:

**Stage A — RL2‑Core Safety**

* Determinism of evaluation
* Duty lifecycle consistency
* Termination and totality of the transformer

**Stage B — RDF Correspondence**

* AST ↔ TTL/SHACL soundness
* Well‑typedness preservation

**Stage C — ODRL Compilation**

* Conditional semantic preservation (modulo clarifications)
* Expressive coverage modulo explicit assumptions

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

**Proof Focus**

* Determinism
* Constraint soundness

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

**Proof Focus**

* Lifecycle consistency
* Performer uniqueness

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

**Proof Focus**

* No orphan remedies
* Guaranteed violation trace

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

### III.5 What This Is NOT

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
