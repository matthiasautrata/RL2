# RL2 and ODRL 2.2: Comparison and Migration

**Version:** 1.1  
**Date:** 2026-07-29
**Status:** Draft migration specification; comparison content under SCOPE-2 review

> **SCOPE-2 status.** ODRL migration is a primary normative deliverable. The existing comparison
> remains useful background, but it is not yet the required term-by-term translation contract.
> State-machine, event-log, protocol, and prescribed-IR comparisons below describe the former
> scope until rewritten. The migration matrix defined in this document will replace those claims.

> **Maintenance note (2026-07-26, DOC-4 superseded).** This document is a
> deliberately **standalone** comparative analysis — it is not slated for
> merging into the Primer. The motivation, use-case walkthrough, and
> ODRL→RL2 justification this document exists to provide need room the Primer
> doesn't have. The stale claims previously flagged here (2026-07-25) have been
> corrected: §1.1 no longer cites a nonexistent media profile, §2.2's Event Log
> claim was confirmed against the former SCOPE-1 semantics, and §2.1 reflects
> the current crystallization model. §3.2's mechanization-toolchain framing
> (2026-07-26) was later superseded by SCOPE-1 and then SCOPE-2
> (`RL2_Scope.md`):
> RL2 dropped the Dafny→Go mechanization plan in favor of a single-lowering,
> directly interpreted AST design. Conformance testing is planned but no
> implementation or differential test suite currently exists; see §3.2.

## Executive Summary

RL2 is designed as a rigorous successor to the Open Digital Rights Language (ODRL). ODRL provides
a flexible information model and vocabulary, but important evaluator choices remain implicit or
descriptive. RL2 retains and extends the policy model while defining a canonical translation and a
pure evaluation function over an explicit request and world snapshot.

This document details the coverage gaps (what RL2 lacks compared to ODRL), the functional improvements (what RL2 solves that ODRL does not), and the formal soundness of the RL2 approach.

## Migration Contract — in progress

Every ODRL 2.2 term and structural form will receive one disposition:

| Disposition | Meaning |
|---|---|
| `exact` | Direct mapping with the same behavioral meaning |
| `normalized` | Deterministic structural rewrite to canonical RL2 |
| `clarified` | Accepted only with an explicit RL2 interpretation |
| `profile-dependent` | Requires an identified profile and its semantics |
| `rejected` | No safe deterministic core interpretation; importer returns a diagnostic |
| `metadata-only` | Preserved or reported but ignored by evaluation |

Each completed row must provide the ODRL source shape, canonical RL2 AST mapping, semantic
assumption, preservation rule, diagnostic, and positive/negative fixture. Quantitative or
feature-level comparison does not substitute for this mapping.

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
| **RL2 core** | 883 | 40 | 35 | 44 | 10 | 20 | 1 | 4 enum |
| **RL2 suite²** | 2,536 | 107 | 43 | 70 | 22 | 21 | 1 | 6 enum |

¹ ODRL 2.2 uses SKOS Concepts for vocabulary organization — `rdfs:domain` lines proxy for property count. It has 216 `skos:member` entries covering the full vocabulary.
² RL2 suite line/size totals include `rl2.ttl`, `rl2p.ttl`, `rl2-shacl.ttl`, and
`rl2p-shacl.ttl`; ontology-term counts combine the two ontology files. Measurements are from
the repository state dated 2026-07-31.

### Complexity: what's inside each ontology

| Dimension | ODRL 2.2 | RL2 |
|-----------|----------|-----|
| **Class hierarchy depth** | 3 levels (Policy→Set/Offer/Agreement; Rule→Permission/Prohibition/Duty) | 4 levels (Clause→Norm→Duty/Privilege/Claim/Power/...; Condition→Atomic/Logical/Event) |
| **Normative framework** | Deontic triple (Permission, Prohibition, Obligation) | Seven modeled positions: six positive Hohfeldian positions (Privilege, Duty, Claim, Power, Liability, Immunity) + Prohibition. The two absence positions (No-Right, Disability) are derived, not reified as classes. |
| **Promise Theory** | None | Promise, promisor/promisee, three exclusive content forms, and snapshot-derived status; the complete acceptance transformation remains S2-C4 |
| **Axiom type count** | Standard RDFS domain/range + skos:member organization + disjoint classes | RDFS domain/range + `owl:oneOf` enumerations + transitive `includedIn` + inverse properties + compound domain unions |
| **Constraint language** | No SHACL in ODRL spec (ODRL Profiles handle this externally) | Separate core and protocol SHACL shape files with mandatory/optional shape distinction |
| **Evaluation semantics** | Processing behavior described in the Information Model; Duty fulfillment remains application-dependent | Pure `Eval` over an explicit Request and immutable WorldSnapshot, including declarative Duty/Promise status and causal indeterminacy |
| **Policy container types** | 5 (Set, Offer, Agreement, Assertion, Privacy) + Ticket, Request | 5 (Set, Offer, Agreement, Assertion, Privacy) — matches ODRL subset |
| **Namespace purity** | Uses skos:, foaf:, vcard:, schema:, cc: — 14 external prefixes | 7 prefixes — minimal external dependency |

### Understandability

**ODRL 2.2** is easier for a *first read* because it follows a vocabulary-catalog pattern:
SKOS collections group terms by topic, and the Information Model supplies the processing
semantics. Correct evaluation therefore requires the ontology and the prose specification,
not the TTL alone.

**RL2** is harder on first read because the class hierarchy is deeper and the Hohfeldian positions
are unfamiliar to most practitioners. Its advantage is that the formal semantics
(`RL2_Semantics.md`) are aligned with canonical ontology and SHACL forms: applicability,
Achievement evidence, Maintenance invariants, intervals, missing data, and conflicts have explicit
interpretations. Future protocol terms such as `StateTransition` do not define core evaluation.

The RL2 approach trades *first-read simplicity* for *operational clarity* — you pay a steeper learning curve but get less ambiguity.

### Utility comparison

| Use case | ODRL 2.2 | RL2 |
|----------|----------|-----|
| **Express a simple license** (Creative Commons-style) | ✓ Best — flat vocabulary, one Permission with constraints | Overengineered for this |
| **Express a bilateral contract** with reciprocal obligations | Awkward — no Claim, correlative relations implicit | ✓ Native — Duty↔Claim, Power↔Liability via `correlativeTo` |
| **Model GDPR/consent** | Partial — Privacy subclass exists but no subject-rights vocabulary | ✓ Privacy profile (427 lines) + data subject rights as Claims |
| **Multi-party supply chain** with promises → crystallized duties | No explicit promise/acceptance model | Action/state Promise acceptance is a pure total transformation; unsupported suretyship is rejected |
| **Policy orchestration** (escalation, delegation, approval workflows) | Requires application logic beyond the core model | Future companion protocol; not part of core language conformance |
| **Automated compliance/audit** | Requires external logic | Partial — SHACL checks canonical structure and core semantics return an attributed envelope, derived statuses, and diagnostics; persistence and replay are outside core |
| **Cross-domain profiles** | In-practice fragmentation (Mpeg21, LDR, IDS each fork) | Designed for profile extensibility via `LeftOperand` resolution paths |

### The key structural difference

Both languages use RDF/OWL vocabularies plus prose specifications. ODRL prioritizes an
interoperable Information Model, vocabulary, and profile mechanism. RL2 adds separate SHACL,
formal-semantics, IR, and protocol layers, at the price of a deeper model and additional
Hohfeldian and Promise concepts. RL2 evaluation correctness still depends on the complete
file set; TTL+SHACL alone are structural, not operational.

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

### 2.1 Duty role and fulfillment

ODRL 2.2 already distinguishes two structural uses of `odrl:Duty`: `odrl:duty` on a Permission is
a precondition that must be fulfilled before the Permission is granted, while `odrl:obligation`
on a Policy is independent. The underspecified part is how fulfillment is established and how
evidence, time, and an evaluation request affect that result. RL2 preserves the structural
distinction and supplies deterministic status semantics.

**RL2 mapping and clarification:**

*   **`prerequisiteDuty`:** The exact structural counterpart of `odrl:duty` on a Permission. The
    attached Duty is referenced by that Privilege, and every applicable prerequisite must be
    Fulfilled before the Privilege can contribute a permit. As in ODRL 2.2, one Duty node may be
    shared by several Privileges and need be fulfilled only once.
*   **Independent Duty clause:** The counterpart of `odrl:obligation` on a Policy. Its status is
    reported but never changes an unrelated access decision.
*   **`condition`:** Applicability only; it does not establish fulfillment.
*   **Achievement Duty:** Requires an `action` and may declare a `postCondition` that qualifies an action witness.
*   **Maintenance Duty:** Requires an `invariant` and has no action.
*   **`dutyWindow`:** Optional finite half-open interval for one Duty occurrence; it is not inferred from a general condition.
*   **`Promise`:** Used pre-contract, in an `Offer`, for voluntary commitments (action or state) that bind their promisor in the Promise-Theory sense but create no correlative Claim yet.
*   **Crystallization:** Acceptance-to-Agreement mapping is a pure, total policy transformation,
    not a runtime transition. Acceptance supplies parties, output identifiers, optional object
    bindings, and optional Duty windows. Action and state Promises become Duties plus Claims;
    unsupported suretyship or Promise-specific references produce attributed diagnostics.

ODRL `Offer` and `Agreement` identify policy purposes but ODRL 2.2 does not define an equivalent
normative acceptance transformation. An importer therefore maps an already accepted ODRL
Agreement directly; it MUST NOT infer that an ODRL Offer was accepted or invoke RL2
`materialize` without explicit acceptance parameters.

For ODRL import, a Duty action maps to an RL2 Achievement Duty. A Permission's `odrl:duty` edge
maps to `rl2:prerequisiteDuty`; a Policy's `odrl:obligation` edge maps to `rl2:clause`. An ODRL constraint maps to
`condition` only when it gates applicability. A deadline or action-refinement constraint requires
an explicit translation interpretation into `dutyWindow` or `postCondition`; an importer must not
guess from the constraint's syntax. ODRL duties intended to maintain a state require a declared
translation to `invariant` and therefore are `clarified`, not exact, mappings. ODRL
`consequence` and `remedy` chains are not attachment phases and remain separately dispositioned;
an importer must not silently reinterpret them as independent Duties.

### 2.2 Evaluation Determinism
**Problem:** ODRL leaves request data, state-of-world input, and Duty satisfaction sufficiently
open that independent evaluators can reasonably disagree.

**RL2 Solution:** Pure evaluation and declarative status.
*   `Eval(PolicyUniverse, Request, WorldSnapshot, EvaluationConfiguration)` is total and immutable.
*   Duty and Promise statuses are derived from canonical content plus finite fact/evidence input;
    they are not read from a required persistent state machine.
*   Missing, invalid, and conflicting semantic inputs remain attributed and can yield
    `Indeterminate` rather than being silently treated as false.

### 2.3 The "Power" Norm (Deontic Completeness)
**Problem:** ODRL focuses on Permissions (access control). It struggles to model **administrative rights**, such as "The Data Protection Officer has the right to *revoke* this policy."

**RL2 Solution:** Full Hohfeldian Logic.
*   RL2 implements **Power** (ability to change norms) and **Liability** (susceptibility to change).
*   This allows modeling complex governance workflows (revocation, delegation, override) as first-class citizens.

### 2.4 Promise Theory & Remediation
**Problem:** ODRL does not distinguish between "I will do X" (Promise) and "I am required to do X" (Duty). It also lacks a formal mechanism for what happens when a rule is broken (other than a generic `remedy` property).

**RL2 Solution:** Promise content and explicit status.
*   RL2 distinguishes promised actions, states, and Duties and derives their status from the snapshot.
*   Core `Eval` does not invent a remedial action or mutate policy state. Authored remediation is an open language decision; workflow generation belongs to a future protocol.

---

## 3. Semantic Soundness

RL2 is built on a formal foundation designed to be precise and testable.

### 3.1 I/O Logic (Input/Output Logic)
RL2 utilizes **Makinson & van der Torre’s I/O Logic** for its derivation engine.
*   **Derivation (Monotone):** For a fixed environment, adding policy clauses or policies
    does not remove previously derived normative atoms. This claim does not say that changing
    runtime facts preserves derivations: negated and otherwise non-monotone conditions can
    change truth value when the environment changes.
*   **Resolution (Non-Monotone):** A separate strategy phase applies evaluator-configured priorities to resolve conflicts (e.g., a `prohibit-overrides` strategy, analogous to XACML combining algorithms) — priority is evaluator configuration, not fixed policy vocabulary.
*   This separation ensures that the core reasoning is logically sound and precisely specified.

### 3.2 Formal Specification, Not Mechanized Proof

RL2's current scope is a thoroughly specified policy model, pure evaluation semantics, ODRL
migration rules, and conformance suite (`RL2_Scope.md`). The normative artifacts must be precise
enough to implement and verify independently, but RL2 does not prescribe an IR, implementation
language, proof assistant, or extraction toolchain. Historical toolchain analysis is retained in
`../future/research/verification-toolchain-comparison.md`.

### 3.3 Explicit World Snapshot

ODRL policies frequently refer to request attributes and state-of-the-world values without a
single normative account of how those values enter evaluation. RL2 makes them an explicit,
immutable `WorldSnapshot` input. Conditions and duty evidence read only that snapshot during one
evaluation. RL2 specifies missing, invalid, conflicting, and indeterminate values; it does not
require an event log or prescribe how a deployment assembles the snapshot.

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

1.  **ODRL Information Model 2.2**, W3C Recommendation. [https://www.w3.org/TR/odrl-model/](https://www.w3.org/TR/odrl-model/)
2.  **ODRL Formal Semantics**, W3C Community Group. [https://w3c.github.io/odrl/formal-semantics/](https://w3c.github.io/odrl/formal-semantics/)
3.  **Steyskal, S., & Polleres, A. (2015).** *Towards a Formal Semantics for ODRL Policies.* Defines core ambiguity problems in ODRL action dependencies.
4.  **Makinson, D., & van der Torre, L. (2000).** *Input/Output Logics.* Journal of Philosophical Logic. The foundation for RL2’s derivation model.
5.  **Hohfeld, W. N. (1913).** *Some Fundamental Legal Conceptions as Applied in Judicial Reasoning.* The basis for RL2’s Rights/Powers distinction.
6.  **Burgess, M. (2005).** *An Approach to Understanding Policy based on Promise Theory.*
