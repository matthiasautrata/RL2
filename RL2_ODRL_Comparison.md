# RL2 vs. ODRL: A Comparative Analysis

**Version:** 1.1  
**Date:** 2026-07-26  
**Status:** Draft

> **Maintenance note (2026-07-26, DOC-4 superseded).** This document is a
> deliberately **standalone** comparative analysis — it is not slated for
> merging into `RL2_Primer.md`. The motivation, use-case walkthrough, and
> ODRL→RL2 justification this document exists to provide need room the Primer
> doesn't have. The stale claims previously flagged here (2026-07-25) have been
> corrected: §1.1 no longer cites a nonexistent media profile, §2.2's Event Log
> claim is now confirmed accurate against `RL2_Semantics.md`, and §2.1 reflects
> the current crystallization model. §3.2's mechanization-toolchain framing
> (2026-07-26) was later superseded by **SCOPE-1** (2026-07-29, `issues.md`):
> RL2 dropped the Dafny→Go mechanization plan in favor of a specified,
> differential-tested design — see the updated §3.2 below.

## Executive Summary

RL2 is designed as a **rigorous successor** to the Open Digital Rights Language (ODRL). While ODRL provides a flexible vocabulary for expressing rights and policies, its normative Information Model specifies policy processing descriptively in prose rather than as a formal operational calculus — a W3C Community Group *Formal Semantics* draft exists (see References) but is non-normative and not part of the core IM — which leaves ambiguity in automated enforcement. RL2 retains the conceptual information model of ODRL (Subject-Action-Object rules) but replaces its descriptive processing model with a **formal operational calculus** (state machines, transition rules, type systems).

This document details the coverage gaps (what RL2 lacks compared to ODRL), the functional improvements (what RL2 solves that ODRL does not), and the formal soundness of the RL2 approach.

---

## Quantitative Comparison

RL2's ontology suite measured against four major W3C ontologies — ODRL 2.2 (the baseline), PROV-O, DCAT 3, and the Organization Ontology — plus FOAF for scale reference.

### Raw metrics

| Ontology | Lines | Size (KB) | Classes | ObjProps | DataProps | subClass | subProp | Disj/Enums |
|----------|------:|----------:|--------:|---------:|----------:|---------:|--------:|-----------:|
| **FOAF** | 415 | 21 | 13 | 46 | 12 | 2 | 0 | 0 |
| **ORG** | 1,059 | 84 | 12 | 31 | 2 | 7 | 0 | 0 |
| **PROV-O** | 1,321 | 69 | 39 | 42 | 6 | 23 | 50 | 0 |
| **DCAT 3** | 1,840 | 200 | 10 | 30 | 9 | 8 | 18 | 0 |
| **ODRL 2.2** | 2,274 | 91 | 19 | ~37¹ | ~37¹ | 14 | 24 | 10 disj |
| **RL2 core** | 679 | 28 | 33 | 36 | 6 | 20 | 1 | 4 enum |
| **RL2 full²** | 2,018 | 79 | 40 | 62 | 18 | 20 | 1 | 6 enum |

¹ ODRL 2.2 uses SKOS Concepts for vocabulary organization — `rdfs:domain` lines proxy for property count. It has 216 `skos:member` entries covering the full vocabulary.
² RL2 full = `rl2.ttl` + `rl2p.ttl` + `rl2-shacl.ttl` + `rl2p-shacl.ttl`

### Complexity: what's inside each ontology

| Dimension | ODRL 2.2 | RL2 |
|-----------|----------|-----|
| **Class hierarchy depth** | 3 levels (Policy→Set/Offer/Agreement; Rule→Permission/Prohibition/Duty) | 4 levels (Clause→Norm→Duty/Privilege/Claim/Power/...; Condition→Atomic/Logical/Event) |
| **Normative framework** | Deontic triple (Permission, Prohibition, Obligation) | Seven modeled positions: six positive Hohfeldian positions (Privilege, Duty, Claim, Power, Liability, Immunity) + Prohibition. The two absence positions (No-Right, Disability) are derived, not reified as classes. |
| **Promise Theory** | None | Full layer: Promise, promisor/promisee, 3 disjoint promise types (action/state/duty), crystallization to Duty+Claim |
| **Axiom type count** | Standard RDFS domain/range + skos:member organization + disjoint classes | RDFS domain/range + `owl:oneOf` enumerations + transitive `includedIn` + inverse properties + compound domain unions |
| **Constraint language** | No SHACL in ODRL spec (ODRL Profiles handle this externally) | 628-line SHACL shapesheet with mandatory/optional shape distinction |
| **Operational semantics** | Implicit — described in prose IM spec, not in ontology | Explicit: ObligationState enum, Event class, StateTransition, temporal `after` property |
| **Policy container types** | 5 (Set, Offer, Agreement, Assertion, Privacy) + Ticket, Request | 5 (Set, Offer, Agreement, Assertion, Privacy) — matches ODRL subset |
| **Namespace purity** | Uses skos:, foaf:, vcard:, schema:, cc: — 14 external prefixes | 7 prefixes — minimal external dependency |

### Understandability

**ODRL 2.2** is easier for a *first read* because it follows a flat, vocabulary-catalog pattern — SKOS collections group terms by topic, each term gets a label and a short comment. The ontology is a reference dictionary. The harder lift comes from the *implicit semantics* — what "duty implies obligation" actually means in evaluation terms lives in a separate 40-page prose spec. You can't reason about correctness from the TTL alone.

**RL2** is harder on first read because the class hierarchy is deeper and the Hohfeldian positions are unfamiliar to most practitioners. But it's *more understandable once you get past that* — because the formal semantics (`RL2_Semantics.md`) are aligned with the ontology vocabulary. `rl2:ObligationState` is an explicit `owl:oneOf` enumeration, not prose. `rl2:triggeredBy` → `rl2:StateTransition` is in the ontology, not an implicit convention. The SHACL shapesheet gives you machine-checkable answers to "is this a valid X?" without hunting through prose.

The RL2 approach trades *first-read simplicity* for *operational clarity* — you pay a steeper learning curve but get less ambiguity.

### Utility comparison

| Use case | ODRL 2.2 | RL2 |
|----------|----------|-----|
| **Express a simple license** (Creative Commons-style) | ✓ Best — flat vocabulary, one Permission with constraints | Overengineered for this |
| **Express a bilateral contract** with reciprocal obligations | Awkward — no Claim, correlative relations implicit | ✓ Native — Duty↔Claim, Power↔Liability via `correlativeTo` |
| **Model GDPR/consent** | Partial — Privacy subclass exists but no subject-rights vocabulary | ✓ Privacy profile (427 lines) + data subject rights as Claims |
| **Multi-party supply chain** with promises → crystallized duties | Not expressible — no promise/acceptance model | ✓ Full Promise Theory layer with `promisedAction/State/Duty` |
| **Policy orchestration** (escalation, delegation, approval workflows) | No event model, no state machine | ✓ Event + StateTransition + obligation states |
| **Automated compliance/audit** | Requires external logic | Partial — SHACL checks structural validity and `ObligationState` is a deterministic state enum; full audit (evidence semantics, trusted inputs, event ordering, replay) is not yet implemented |
| **Cross-domain profiles** | In-practice fragmentation (Mpeg21, LDR, IDS each fork) | Designed for profile extensibility via `LeftOperand` resolution paths |

### The key structural difference

ODRL 2.2 is a **vocabulary** — a SKOS-organized dictionary of terms with RDFS domain/range constraints. Its 216 `skos:member` entries cover exhaustively what you can *say*, but the *what-it-means* lives in a separate prose document.

RL2 is an **ontology** in the stronger sense — it encodes not just vocabulary but also the operational types (enumerations, state machines, transition triggers) that let you reason about correctness from the TTL+SHACL alone. The price: deeper hierarchy, the unfamiliar Hohfeldian positions, and a Promise Theory layer that ODRL simply doesn't have.

If ODRL 2.2 is a dictionary, RL2 is a dictionary + grammar + a formal semantics appendix — all in the same file set.

---

## 1. RL2 Coverage: Deviations and Strategies

RL2 is a "strict core" language. It intentionally omits certain flexible features of ODRL to ensure decidability, determinism, and security.

### 1.1 Vocabulary Richness
**Gap:** ODRL defines a massive standard vocabulary of actions (`print`, `play`, `stream`, `move`) and constraints (`meteredTime`, `count`, `resolution`). RL2 defines only abstract concepts (`Action`, `Constraint`) in its core.
**RL2 Strategy:** **Profiles**.
*   RL2 delegates domain-specific vocabulary to **Profiles** (e.g., `rl2-privacy-profile.ttl`; additional profiles are added as domains require them).
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

**RL2 Solution:** Distinct semantic types, reconciled at contract formation.
*   **`Condition`:** Used for pre-requisites (e.g., payment).
*   **`Duty`:** Used strictly for "Ought-to-Do" (and, for state-maintenance, "Ought-to-Be") obligations — always enforceable, always paired with a correlative Claim.
*   **`Promise`:** Used pre-contract, in an `Offer`, for voluntary commitments (action or state) that bind their promisor in the Promise-Theory sense but create no correlative Claim yet.
*   **Crystallization:** On acceptance (Offer → Agreement), every Promise *crystallizes* into a Duty plus its correlative Claim — acceptance is precisely what supplies the claim-holder the bare Promise lacked. No Promise survives in an Agreement; only Duties (and their Claims) are enforceable there.

### 2.2 Operational Determinism
**Problem:** ODRL describes *what* an engine should decide (e.g., "If constraint is satisfied, then Permit") but not *how* state transitions occur over time. It relies on a "bag of facts" state model that struggles with sequence (e.g., "Did the payment happen *before* the access?").

**RL2 Solution:** Small-Step Operational Semantics.
*   RL2 defines transitions as $ (\Sigma, e) \to (\Sigma', e') $.
*   It explicitly models the lifecycle of a Duty: `Pending` $\to$ `Active` $\to$ `Fulfilled` (or `Violated`).
*   State ($\Sigma$) includes `Σ.Events`, a **typed, temporally-ordered index** (a map from event type to a time-ordered sequence of events of that type), allowing precise queries like "the most recent approval event of this type".

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

RL2 is built on a formal foundation designed to be precise and testable.

### 3.1 I/O Logic (Input/Output Logic)
RL2 utilizes **Makinson & van der Torre’s I/O Logic** for its derivation engine.
*   **Derivation (Monotone):** The engine first derives *all* potential norms (candidates) from the policy and state. This phase is monotonic (adding facts never removes derived norms).
*   **Resolution (Non-Monotone):** A separate strategy phase applies evaluator-configured priorities to resolve conflicts (e.g., a `prohibit-overrides` strategy, analogous to XACML combining algorithms) — priority is evaluator configuration, not fixed policy vocabulary.
*   This separation ensures that the core reasoning is logically sound and precisely specified.

### 3.2 Formal Specification, Not Mechanized Proof
RL2's current scope is a thoroughly specified semantics and IR (`RL2_Semantics.md`,
`RL2_IR.md`), not a mechanized proof or a reference implementation (**SCOPE-1**, `issues.md`,
2026-07-29). Safety properties such as "a specific prohibition can never be bypassed" are
stated as documented design properties (RL2_Semantics.md §Proof Obligations) precise enough to
test an implementation against by differential testing, rather than proof obligations
discharged in a proof assistant. An earlier plan to mechanize the evaluator in Dafny with Go
extraction was considered and dropped; `research/verification-toolchain-comparison.md` records
that comparison for historical reference only.

### 3.3 Event-Indexed State
Unlike ODRL's static snapshot of the world, RL2 makes state a function of accumulated events.
*   State is a function of the initial state and the sequence of applied events: $\Sigma_{t} = Apply(Events_{0..t}, \Sigma_0)$.
*   Concretely, `Σ.Events` is a typed, temporally-ordered index (event type → time-ordered sequence), not a single flat log — but the same auditability property holds: the current decision can always be reconstructed by replaying the recorded events.

---

## 4. Prior Art and Related ODRL Work

RL2 overlaps a substantial body of existing ODRL formalization and tooling. It does **not** subsume this work — the table records, for each effort, where RL2 currently stands and the remaining gap. Before introducing a new core term, record whether it comes from, refines, or intentionally differs from these efforts.

| Work | RL2 relationship | Gap |
|------|------------------|-----|
| [ODRL Formal Semantics](https://w3c.github.io/odrl/formal-semantics/) / Compliance Report Model | Has request, state, Result, active requirements. | No per-policy/rule/action/constraint compliance report; no requested-vs-attempted-action distinction; open/closed evaluator behavior not separated from rule conflicts. |
| ODRL atomization | Canonical singular AST (Band 0) is the same direction. | RDF shapes still allow some plural fields; no normative atomization algorithm or equivalence tests yet. |
| FORCE / ODRL 3 experiments | Similar evaluator/protocol concepts. | No term-by-term comparison or import/export mapping; treat FORCE as prior art, not independent coverage. |
| [ODRL evaluator test suite](https://w3c.github.io/odrl/landscape/) | 52 narrative use cases. | Not yet standard policy + request + state-of-world + expected-report vectors (golden-test conversion is open work). |
| [ODRL-PAP → Rego](https://github.com/SEAMWARE/odrl-pap) | Both translate RDF policy into a non-RDF evaluator target. | RL2's IR not yet compared against an ODRL-to-Rego translator (bundles, input mappings, enforcement-point integration). |
| Deontic consistency checking | Carries conflicts into a resolution stage. | No static consistency analysis, unreachable-clause diagnostics, or intentional-vs-authoring-error conflict explanation. |
| [ODRL Temporal Profile](https://w3c.github.io/odrl/profile-temporal/) | Current-time comparison + event references. | No interval/trace algebra, recurrence, or temporal composition; no compatible import mapping. |
| [ODRL Data-space](https://w3c.github.io/odrl/profile-dataspaces/) & VC profiles | ContextAssertion could carry policy-relevant claims. | No credential-verification/trust semantics, negotiation protocol, or data-space profile mapping. |

**Landscape / registry references** (review before minting overlapping constructs): [ODRL Landscape](https://w3c.github.io/odrl/landscape/), [ODRL Profile registry](https://www.w3.org/community/odrl/wiki/ODRL_Profiles), [Profile Best-Practices report](https://www.w3.org/community/reports/odrl/CG-FINAL-profile-bp-20240808.html).

---

## 5. References

1.  **ODRL Formal Semantics**, W3C Community Group. [https://w3c.github.io/odrl/formal-semantics/](https://w3c.github.io/odrl/formal-semantics/)
2.  **Steyskal, S., & Polleres, A. (2015).** *Towards a Formal Semantics for ODRL Policies.* Defines core ambiguity problems in ODRL action dependencies.
3.  **Makinson, D., & van der Torre, L. (2000).** *Input/Output Logics.* Journal of Philosophical Logic. The foundation for RL2’s derivation model.
4.  **Hohfeld, W. N. (1913).** *Some Fundamental Legal Conceptions as Applied in Judicial Reasoning.* The basis for RL2’s Rights/Powers distinction.
5.  **Burgess, M. (2005).** *An Approach to Understanding Policy based on Promise Theory.*
