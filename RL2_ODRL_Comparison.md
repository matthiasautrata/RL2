# RL2 vs. ODRL: A Comparative Analysis

**Version:** 1.0  
**Date:** 2025-12-16  
**Status:** Draft

> **Staleness notice (2026-07-25, DOC-4).** This document predates the v0.6
> canonical-form pass and the Dafny→Go toolchain decision, and contains several
> claims no longer accurate:
> - References **Why3/WhyML** and **Coq/Lean** as verification targets (§3.2) —
>   the decided toolchain is **Dafny → Go** exclusively (`de473f5`).
> - Cites `rl2-media-profile.ttl` (§1.1) — this file does not exist in `profiles/`.
> - Claims Σ includes a "time-ordered Event Log" (§2.2) — `Σ.Events` is a set, not
>   an ordered log.
> - Its Duty-ambiguity discussion (§2.1) predates **PROM-1**'s crystallization
>   resolution (Promise-in-Agreement content crystallizes into Duty + correlative
>   Claim on acceptance).
>
> See `issues.md` **DOC-4** for the full list and the plan to merge this document
> into `RL2_Primer.md` as a comparison section. Treat the sections below as
> historical unless corroborated by the current spec suite.

## Executive Summary

RL2 is designed as a **rigorous successor** to the Open Digital Rights Language (ODRL). While ODRL provides a flexible vocabulary for expressing rights and policies, it lacks a strictly defined formal semantics, leading to ambiguity in automated enforcement. RL2 retains the conceptual information model of ODRL (Subject-Action-Object rules) but replaces its descriptive processing model with a **formal operational calculus** (state machines, transition rules, type systems).

This document details the coverage gaps (what RL2 lacks compared to ODRL), the functional improvements (what RL2 solves that ODRL does not), and the formal soundness of the RL2 approach.

---

## 1. RL2 Coverage: Deviations and Strategies

RL2 is a "strict core" language. It intentionally omits certain flexible features of ODRL to ensure decidability, determinism, and security.

### 1.1 Vocabulary Richness
**Gap:** ODRL defines a massive standard vocabulary of actions (`print`, `play`, `stream`, `move`) and constraints (`meteredTime`, `count`, `resolution`). RL2 defines only abstract concepts (`Action`, `Constraint`) in its core.
**RL2 Strategy:** **Profiles**.
*   RL2 delegates domain-specific vocabulary to **Profiles** (e.g., `rl2-privacy-profile.ttl`, `rl2-media-profile.ttl`).
*   This ensures the *Core* logic remains small and verifiable, while extensibility is handled in a modular, validatable way (via SHACL).

### 1.2 Policy Inheritance
**Gap:** ODRL supports `inheritFrom`, allowing a policy to inherit rules from a parent policy. This creates complex resolution chains that can be difficult to audit (e.g., "Why is this permitted? Because of a parent policy 3 levels up.").
**RL2 Strategy:** **Explicit Composition**.
*   RL2 removes inheritance in favor of set-theoretic composition (`Policy A ⊔ Policy B`).
*   **Compilation:** Legacy ODRL policies using inheritance must be "flattened" by a compiler into explicit RL2 rules before execution. This ensures that the *runtime* artifact is always self-contained and auditable.

### 1.3 "Undefined" States
**Gap:** ODRL semantics allow for "Undefined" or "Not-Set" states when information is missing.
**RL2 Strategy:** **Totality**.
*   RL2 functions are total; they must resolve to a value or a distinct `Bottom` ($\perp$) failure state.
*   This prevents "fail-open" or ambiguous behaviors in autonomous agents.

---

## 2. Problems RL2 Solves (That ODRL Does Not)

Academic literature has identified several "gray areas" in ODRL which RL2 explicitly resolves.

### 2.1 The "Duty" Ambiguity
**Problem:** ODRL uses `odrl:Duty` for two distinct concepts:
1.  **Pre-conditions:** "You must pay $5 to see the movie" (Condition for Permission).
2.  **Post-obligations:** "You must delete the file after 30 days" (Standalone Obligation).
This leads to confusion in processing engines about whether a duty must be done *before* or *after* access.

**RL2 Solution:** Distinct semantic types.
*   **`Condition`:** Used for pre-requisites (e.g., payment).
*   **`Duty`:** Used strictly for "Ought-to-Do" obligations (stateful tasks).
*   **`Promise`:** Used for "Ought-to-Be" invariants (guarantees of state).

### 2.2 Operational Determinism
**Problem:** ODRL describes *what* an engine should decide (e.g., "If constraint is satisfied, then Permit") but not *how* state transitions occur over time. It relies on a "bag of facts" state model that struggles with sequence (e.g., "Did the payment happen *before* the access?").

**RL2 Solution:** Small-Step Operational Semantics.
*   RL2 defines transitions as $ (\Sigma, e) \to (\Sigma', e') $.
*   It explicitly models the lifecycle of a Duty: `Pending` $\to$ `Active` $\to$ `Fulfilled` (or `Violated`).
*   State ($\Sigma$) includes a time-ordered **Event Log**, allowing precise queries like "the most recent approval event".

### 2.3 The "Power" Norm (Deontic Completeness)
**Problem:** ODRL focuses on Permissions (access control). It struggles to model **administrative rights**, such as "The Data Protection Officer has the right to *revoke* this policy."

**RL2 Solution:** Full Hohfeldian Logic.
*   RL2 implements **Power** (ability to change norms) and **Liability** (susceptibility to change).
*   This allows modeling complex governance workflows (revocation, delegation, override) as first-class citizens.

### 2.4 Promise Theory & Remediation
**Problem:** ODRL does not distinguish between "I will do X" (Promise) and "I am required to do X" (Duty). It also lacks a formal mechanism for what happens when a rule is broken (other than a generic `remedy` property).

**RL2 Solution:** Remedial Generation.
*   RL2 implements **Promise Theory**: A violated Promise (invariant) automatically generates a remedial **Duty** (action) to restore the state.
*   This enables "self-healing" policy systems.

---

## 3. Semantic Soundness

RL2 is built on a formal foundation designed for mechanization (formal verification).

### 3.1 I/O Logic (Input/Output Logic)
RL2 utilizes **Makinson & van der Torre’s I/O Logic** for its derivation engine.
*   **Derivation (Monotone):** The engine first derives *all* potential norms (candidates) from the policy and state. This phase is monotonic (adding facts never removes derived norms).
*   **Resolution (Non-Monotone):** A separate strategy phase applies priorities to resolve conflicts (e.g., `Prohibition` overrides `Privilege`).
*   This separation ensures that the core reasoning is logically sound and mathematically provable.

### 3.2 Formal Verification Targets
The RL2 semantics are written to be mechanizable in:
*   **Why3/WhyML:** For extracting correct-by-construction OCaml evaluators.
*   **Coq/Lean:** For independent proofs of safety properties (e.g., "A specific prohibition can never be bypassed").

### 3.3 Event Calculus
Unlike ODRL’s static snapshot of the world, RL2 uses a simplified **Event Calculus**.
*   State is a function of the initial state and the sequence of applied events: $\Sigma_{t} = Apply(Events_{0..t}, \Sigma_0)$.
*   This ensures auditability: The current decision can always be reconstructed by replaying the event log.

---

## 4. References

1.  **ODRL Formal Semantics**, W3C Community Group. [https://w3c.github.io/odrl/formal-semantics/](https://w3c.github.io/odrl/formal-semantics/)
2.  **Steyskal, S., & Polleres, A. (2015).** *Towards a Formal Semantics for ODRL Policies.* Defines core ambiguity problems in ODRL action dependencies.
3.  **Makinson, D., & van der Torre, L. (2000).** *Input/Output Logics.* Journal of Philosophical Logic. The foundation for RL2’s derivation model.
4.  **Hohfeld, W. N. (1913).** *Some Fundamental Legal Conceptions as Applied in Judicial Reasoning.* The basis for RL2’s Rights/Powers distinction.
5.  **Burgess, M. (2005).** *An Approach to Understanding Policy based on Promise Theory.*
