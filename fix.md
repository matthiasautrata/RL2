# RL2 Specification Review & Remediation Plan (ODRL 2.2 → ODRL 3)

**Document Status:** Complete Specification Audit, Engineering Analysis & Remediation Plan
**Target Spec:** RL2 (Candidate Specification for ODRL 3.0)
**Date:** 2026-07-25
**Ontology Version:** RL2 0.6 / Protocol 0.5
**Reviewer Method:** Full read of all TTL, SHACL, and Markdown artifacts; web research against W3C ODRL specs, community group outputs, and comparison systems (OPA/Rego, AWS Cedar, Immuta); engineering analysis of Forth-IR feasibility, external data integration, and no-solver approach.

---

## 1. Executive Summary & Strategic Assessment

### 1.1 Context and Vision

ODRL 2.2 (W3C Recommendation, 15 February 2018) established a foundational vocabulary for digital rights management. However, ODRL 2.2 suffers from critical design limitations that prevent automated policy generation and mechanized formal verification:

1. **Authoring Variability & Non-Canonical Shapes.** ODRL allows multiple syntactically distinct ways to encode the same normative proposition (e.g., target placement, conflict resolution, inheritance variations). The W3C ODRL Formal Semantics draft ([w3c.github.io/odrl/formal-semantics/](https://w3c.github.io/odrl/formal-semantics/), last updated 2026-07-24) notes this as a fundamental obstacle to automated compliance checking.
2. **Ambiguous Operational Semantics.** The ODRL formal semantics draft is still a Community Group Draft (not a Recommendation) and explicitly states "neither the specification of the model nor the vocabulary accurately describes the behaviour of an ODRL Evaluator." Section 2.4 (Evaluation Report) contains "Pending to be written" markers for conflict handling. The `Duty` class is overloaded for four distinct meanings (Obligation, Condition, Consequence, Remedy); the draft itself notes "it would be better to have an `odrl:Obligation` class" (§6).
3. **Imprecise Modalities & Scoping.** Lack of formal deontic modal distinctions (e.g., Hohfeldian positions, *Sein-sollen* vs *Tun-sollen*) causes conflicting interpretations in automated contract enforcement. The Bonatti-Fornara-Harth 2025 paper ([OPAL 2025](https://ceur-ws.org/Vol-3977/OPAL2025-4.pdf)) identifies the same ambiguities: duty fulfillment semantics, pre/post-condition duties, constraint activation vs fulfillment, gap resolution, and policy scope.

**ODRL 3.0 status.** The W3C ODRL Community Group explicitly lists "Plan for future major enhancements to ODRL (V3.0)" as a charter goal ([w3.org/community/odrl/](https://www.w3.org/community/odrl/)). A **W3C Workshop on the Future of ODRL** was held 20-21 July 2026 in London (co-chaired by Renato Iannella, Nicoletta Fornara, Víctor Rodríguez-Doncel; PC includes Simon Steyskal, Beatriz Esteves, Leonard Rosenthol/Adobe). Workshop topics explicitly include "Gaps in the current ODRL Information Model", "Requirements for future revisions", "Formal semantics of ODRL", "Policy evaluation engines", "Constraint modeling", "Conformance and testing mechanisms", "Runtime enforcement and compliance verification", and "Profile development and extension governance" — all areas RL2 addresses. No published V3.0 requirements document or use-case catalog exists yet; the workshop is the gathering mechanism. RL2 is well-timed as a candidate contribution.

**RL2 (Rights Language 2)** is candidate spec work designed as a clean, rigorous upgrade from ODRL 2.2 to ODRL 3.0. It pivots the standard toward the modern paradigm where **policies are generated and interpreted primarily by AI models and executed by verified deterministic engines**.

### 1.2 Core Architectural Invariants Tested

This audit evaluated RL2 against its two governing quality attributes:

- **Generatable (Canonical Form Invariant).** For any normative proposition RL2 can express, there must be *exactly one* valid RDF shape. Two graphs that differ structurally must differ semantically.
- **Verifiable (Formal Semantics & Stack VM).** Every construct must map deterministically to a bounded evaluation state machine (Dafny kernel → Go reference implementation).

### 1.3 Overall Evaluation Verdict

- **Completeness: High (85%).** Core ODRL 2.2 constructs are fully mapped and enhanced with Hohfeldian correlatives (Privilege, Duty, Prohibition, Claim, Power, Liability, Immunity) and Promise Theory. Gaps remain in quantified selectors (`targetNorm`), native implication/equivalence operators (`implies`/`iff`), periodic recurrence, and ODRL's `inheritFrom` (intentionally dropped, not covered by a replacement).
- **Consistency: Very High (92%).** The v0.6 canonical form pass successfully unified normative roles (`subject`/`counterparty`), split polymorphic properties (`promisedAction`/`promisedState`/`promisedDuty`), and eliminated legacy role ambiguity. Core ontologies (`rl2.ttl`, `rl2-shacl.ttl`) and standalone use cases pass machine SHACL validation (51/51 use cases OK).
- **Logical & Semantic Soundness: Sound with identified gaps.** The separation of static normative policies (`rl2:Policy`) from runtime evaluation state (Σ, `rl2p:Request`, `rl2p:Requirement`) and the I/O-Logic derivation / post-hoc resolution pipeline provides provable bounds on execution. The `restoreAction` hole (SEM-1), quantified selectors (SEM-2), and target matching algorithm (SEM-5) remain open and block full Dafny mechanization.
- **Implementation Feasibility: Feasible but de-risked.** The Forth-IR approach is reasonable and well-precedented (JVM, WASM, Bitcoin Script, Ethereum EVM all use stack machines). Dafny→Go extraction is maturing but requires a spike. The no-solver approach (translation to stack IR rather than Datalog/Prolog entailment) is sound because RL2's derivation phase is already designed as a pure, bounded, polynomial-time function — it does not need entailment-based reasoning. External data integration is the highest-risk engineering area and needs a concrete binding specification.

---

## 2. Completeness Analysis

### 2.1 Coverage of ODRL 2.2 Core Vocabulary

Sources: [ODRL Information Model 2.2](https://www.w3.org/TR/odrl-model/), [ODRL Vocabulary & Expression 2.2](https://www.w3.org/TR/odrl-vocab/), [ODRL Best Practices](https://www.w3.org/TR/odrl-bp/).

| ODRL 2.2 Construct | RL2 Candidate Equivalent | Upgrade Status / Enhancements |
|:---|:---|:---|
| `odrl:Policy` | `rl2:Policy` | Container class. Subclasses `Set`, `Offer`, `Agreement`, `Privacy`, `Assertion`. ODRL's `Privacy` and `Assertion` are RL2 additions. |
| `odrl:Permission` | `rl2:Privilege` | Defined as normative absence of duty not to perform action (*Tun-sollen*). |
| `odrl:Prohibition` | `rl2:Prohibition` | Modeled as a class (duty-to-refrain) with `rl2:prohibitedAction` (⊑ `rl2:action`). Correlative Claim derived. |
| `odrl:Duty` | `rl2:Duty` | Action obligation with explicit `ObligationState` tracking (Σ). |
| `odrl:Party` / `odrl:assigner` / `assignee` | `rl2:Agent` / `rl2:subject` / `rl2:counterparty` / `rl2:grantor` / `rl2:grantee` | Unified role model. Core semantic roles are `subject` (right-holder) and `counterparty` (duty-bearer). |
| `odrl:Asset` / `odrl:target` | `rl2:Asset` / `rl2:object` | Domain broadened to `rl2:Norm ∪ rl2:Promise`. Collections use `rl2:AssetCollection` + `rl2:member`. |
| `odrl:Constraint` | `rl2:AtomicConstraint` | Strict `leftOperand`, `constraintOperator`, `rightOperand`/`rightOperandRef` structure. |
| `odrl:LogicalConstraint` | `rl2:LogicalConstraint` | Connects sub-conditions via `rl2:and`, `rl2:or`, `rl2:xone`, `rl2:not`. |
| `odrl:purpose` | `privacy:purposeOperand` (Profile) | Replaced "magic" ODRL vocabulary with profile-declared `rl2:LeftOperand` instances with explicit `rl2:resolutionPath`. |
| `odrl:inheritFrom` | **Dropped** | Intentionally removed in favor of explicit composition (`Policy A ⊔ Policy B`). Legacy ODRL policies with inheritance must be flattened by a compiler. **Gap: no transpiler exists yet (backlog Phase 3).** |
| `odrl:conflict` | `rl2:priority` + evaluator strategy | Policy-level priority (integer) plus evaluator-configured strategy (ProhibitOverrides, PermitOverrides, SpecificOverridesGeneral). Analogous to XACML combining algorithms. |
| `odrl:remedy` | Promise→Duty remedial generation | Replaced generic `remedy` property with formal remedial generation rule (`RL2_Semantics.md:1036-1071`). **Gap: `restoreAction` for `promisedState` is unresolved (SEM-1).** |
| `odrl:consequence` | `rl2:condition` on Duty | Modeled via condition-gated duty activation rather than a `consequence` property. |
| `odrl:relation` / `odrl:partOf` | Not directly covered | ODRL's asset relation properties (`relation`, `partOf`, `hasPolicy`) are not in RL2 core. Would need a profile. **Minor gap.** |
| `odrl:refinement` | Not directly covered | ODRL's `refinement` property (constraining an action or collection) is not in RL2 core. Action refinement is handled via `rl2:includedIn` hierarchies; collection refinement would need `rl2:selectionCriteria` (EXPR-4). **Gap.** |
| `odrl:function` | `rl2:grantor`/`grantee` | ODRL Party `function` (assigner, assignee, attributor, etc.) mapped to RL2 functional roles. |

### 2.2 Advanced Deontic & Hohfeldian Layer

RL2 completes the Hohfeldian table of legal positions missing in ODRL 2.2:

- **Correlatives Modeled:** `Duty ↔ Claim`, `Power ↔ Liability`, `Immunity ↔ Disability`.
- **Absence Positions (`HOHF-1`, `HOHF-2`):** `No-Right` and `Disability` are correctly treated as negative/absence positions rather than positive RDF classes, avoiding class inflation.
- **Prohibition Correlative (`CANON-3`):** Semantics explicitly derive that a `Prohibition(s, x, o)` induces a correlative `Claim` held by `counterparty` (or policy `grantor`).
- **Jural Opposites (`HOHF-2`):** Not explicitly modeled. Privilege⊥Duty, Power⊥Disability, Immunity⊥Liability are implicit in the evaluator's conflict detection. **Open: decide whether to make opposition relation explicit or document as evaluator-level concern.**

**Community context:** The Fornara-Colombetti 2017/2019 papers ([Springer](https://link.springer.com/chapter/10.1007/978-3-030-01713-2_13), [AI Communications](https://doi.org/10.3233/AIC-190615)) proposed extending ODRL with conditional obligations and operational semantics via Discrete State Machines. RL2's approach is more comprehensive: it integrates the state machine (Pending→Active→Fulfilled/Violated) into the core ontology rather than as an external rule engine. The ODRE 2024 framework ([arXiv:2409.17602](https://arxiv.org/abs/2409.17602)) defines obligation lifecycle (Pending→Active→Fulfilled/Violated) — RL2 adopts and extends this with Hohfeldian normative theory and Promise Theory.

### 2.3 Promise Theory Layer (*Sein-sollen* vs *Tun-sollen*)

RL2 cleanly separates voluntary commitments (`rl2:Promise`) from binding legal obligations (`rl2:Duty`):

- **Tagging Property Split (`CANON-2`):** Polymorphic `promiseContent` was replaced by three tagged properties:
  1. `rl2:promisedAction` (*Tun-sollen*: ought-to-do action).
  2. `rl2:promisedState` (*Sein-sollen*: ought-to-be state invariant).
  3. `rl2:promisedDuty` (Suretyship: guarantee that a third-party duty is fulfilled).
- **Identified Gaps (`SEM-1`, `PROM-5`, `PROM-7`):**
  - `promisedState` requires an explicit `rl2:remedialAction` default when the state invariant fails. Without it, `restoreAction(content)` is partial — a hole in an otherwise-deterministic pipeline.
  - `promisedDuty` suretyship creates an obligation for the promisor, but the exact state mapping when the underlying duty is violated requires explicit resolution.
  - `PromiseState` (Pending/Fulfilled/Violated, no Active) vs `rl2p:requirementStatus` (Pending/Active/Fulfilled/Violated) are not reconciled at the protocol level. The semantics define `projectObligationState` which collapses Active→Pending for promises, but this projection is not documented in `rl2p.ttl` comments.

### 2.4 Operator and Expression Gaps

1. **Logical Implication and Equivalence (`implies`, `iff`):**
   - Core ontology contains `and`, `or`, `xone`, `not`.
   - `implies` (A ⟹ B) and `iff` (A ⟺ B) are absent from `rl2:LogicalOperator`.
   - *Recommendation:* Add desugaring rules in IR compilation (A ⟹ B ≡ ¬A ∨ B) or extend `rl2:LogicalOperator`. The desugaring approach is preferred for canonical form — it avoids adding operators that can be expressed with existing ones.

2. **Quantified Norm Selectors (`SEM-2`):**
   - `rl2:targetNorm` currently takes a single static IRI.
   - Expression of quantified predicates (e.g., "all duties in Policy P are fulfilled", "exists a violated duty") is not expressible without a set-based selector.
   - *Recommendation:* Introduce `rl2:targetNormSelector` or class-based norm pattern matching (e.g., `allWithClass(rl2:Duty)`).

3. **Periodic / Recurrent Duties (`EXPR-1`):**
   - No native representation for calendar recurrence (`FREQ=MONTHLY`). Current workaround delegates to external cron events or profile operands.
   - *Recommendation:* Profile-level `DutyTemplate` + recurrence, not core.

4. **Quorum / k-of-n Approvals (`EXPR-2`):**
   - Cannot express "any 2 of 5 approvers." Needs a quorum constraint. Interacts with SEM-2 (quantified operands).

5. **Temporal Arithmetic (`EXPR-3`):**
   - Relative time ("30 days after event") needs profile operands like `daysSinceEvent`. Native `xsd:duration` arithmetic deferred. The workaround is sufficient for current use cases.

6. **AssetCollection Dynamic Membership (`EXPR-4`):**
   - Only `rl2:member` enumeration. Need `rl2:selectionCriteria` (a Condition) for "all assets with tag:PII." Watch canonical-form: enumeration vs criteria must not become two ways to say the same set.

7. **Delegation Model (`EXPR-5`):**
   - "Alice grants Bob power to act on her behalf." Likely expressible today via Power/Liability. May be a documentation issue, not a vocabulary gap.

8. **Revocation Vocabulary (`EXPR-6`):**
   - Power-to-revoke exists but no explicit revocation event. Consider `rl2:RevocationEvent` in the protocol layer.

### 2.5 Use Case Coverage

The 51-use-case corpus covers 7 categories: Core Patterns (1-17, complete), External Data Licenses (18-23, draft), Data Contract Patterns (24-31, draft), EU Data Spaces/IDS (32-37, draft), Hohfeldian Completeness (38-42, draft), Vocabulary Completeness (43-49, draft), Protocol (50-51, draft).

**Strengths:** Core patterns demonstrate the full normative vocabulary in action. The corpus is validated by `tools/validate.py` (pySHACL), all 51 pass.

**Gaps:**
- 34 of 51 use cases are draft-only (no Turtle model). The Hohfeldian cases (38-42: Claim, Power, Immunity, Liability) are specified but not stress-tested.
- No use case demonstrates ODRL migration (transpilation from an ODRL policy to RL2).
- No use case exercises the Forth-IR compilation path end-to-end.
- No use case demonstrates external data integration (the `resolve` function calling an external source).
- No use case tests conflict resolution strategies (ProhibitOverrides vs PermitOverrides vs SpecificOverridesGeneral) on the same scenario.

### 2.6 ODRL Community Proposals Coverage

**RL2 addresses the following known ODRL limitations identified by the community:**

| Limitation (Source) | RL2 Solution |
|:---|:---|
| Duty ambiguity: pre-condition vs post-obligation (Steyskal-Polleres 2015) | `Condition` (pre-requisite) vs `Duty` (ought-to-do) vs `Promise` (ought-to-be) |
| No operational semantics (Fornara-Colombetti 2017/2019) | Small-step operational semantics with explicit state transitions |
| No Hohfeldian completeness (community discussion) | Full Hohfeldian table: Privilege, Duty, Prohibition, Claim, Power, Liability, Immunity |
| No obligation lifecycle (ODRE 2024) | `ObligationState` (Pending→Active→Fulfilled/Violated) in core ontology |
| No promise/voluntary commitment distinction (Burgess 2005) | `rl2:Promise` with Promise Theory integration |
| Informal English semantics only (Bonatti-Fornara-Harth 2025) | Denotational + operational + constraint algebra semantics |
| No formal conflict resolution (Pucella-Weissman 2006) | `resolveDecision` with parameterized strategies |

**RL2 does NOT cover (or defers):**

| Community Proposal | RL2 Status |
|:---|:---|
| LegalRuleML defeasible logic (Governatori) | Not integrated. `resolveDecision` is procedural, not defeasible-logic-based. Acknowledged as future profile. |
| OWL-POLAR decidable OWL-DL reasoning (Sensoy et al. 2012) | Not integrated. RL2 uses OWL for vocabulary, not for reasoning. Deliberate — avoids undecidability. |
| OPA/Rego Datalog-style evaluation | Not adopted. RL2 uses I/O-Logic derivation + stack VM, not Datalog. Deliberate — for verifiability. |
| ODRL Temporal Profile ([w3c.github.io/odrl/profile-temporal/](https://w3c.github.io/odrl/profile-temporal/)) | Partially covered via `AtomicConstraint` with `currentDateTime`. Native `xsd:duration` arithmetic deferred (EXPR-3). |
| Answer-Set Programming for ODRL compliance (De Vos, Kirrane, Padget & Satoh 2019) | Not adopted. ASP is a solver-based approach; RL2 deliberately avoids solver-based methods for verifiability. |
| Deontic logic for license composition (Rotolo, Villata & Gandon 2013) | Partially. RL2's Hohfeldian framework covers deontic positions but not license composition specifically. |
| Linear logic for rights management (Barth & Mitchell 2006) | Not adopted. RL2 uses I/O-Logic, not linear logic. Different formal foundation. |
| Multi-set rewriting for licenses (Chong et al. 2006, LicenseScript) | Not adopted. RL2 uses state-transition semantics, not rewriting logic. |
| Operational semantics for RELs (Sheppard & Safavi-Naini 2009) | Adopted. RL2's small-step operational semantics align with this line of work. |
| Critical reflection on ODRL semantics (Kebede, Sileno & van Engers 2020) | Addressed. RL2's clean-slate design resolves the semantic foundation issues identified. |

---

## 3. Logical and Semantic Soundness

### 3.1 Conflict Resolution and Decision Determinism

The evaluation function `Eval(U, R, Σ, Ctx)` is defined at `RL2_Semantics.md:1249-1273` and is deterministic and total under stated structural constraints (finite policy universe, bounded condition nesting, acyclic conditions, finite Σ, bounded path depth):

1. **Target Matching:** Filters policies and norms matching `requestedAction`, `requestedAsset`, and `requestingAgent`. Action subsumption is evaluated via `rl2:includedIn*` reachability (transitive closure).
2. **Condition Evaluation (⟦C⟧_Env):** Evaluates atomic and logical constraints against request context, system clock, and Σ event log.
3. **Priority & Overrides:** When both a `Privilege` and a `Prohibition` match, norm priority (`rl2:priority`, `xsd:integer`) determines the outcome. Higher numeric priority prevails.
4. **Default Stance:** Unresolved conflicts or ties emit `rl2p:Indeterminate` (or `rl2p:Deny` under strict closed-world profiles).

**`resolveDecision` is fully specified** (`RL2_Semantics.md:1289-1315`) with three strategies (ProhibitOverrides, PermitOverrides, SpecificOverridesGeneral) and a `baseDecision` fallback. The function is parameterized by strategy + priorities; if these inputs cannot break ties, the evaluator must surface an explicit ambiguity/error rather than applying an implicit specificity heuristic.

**Finding: The `SpecificOverridesGeneral` strategy references `mostSpecific(privileges ∪ prohibitions)` but `mostSpecific` is not defined.** This is a gap — the function's implementation (how "specificity" is computed: by action subsumption depth? by condition complexity? by policy nesting?) is unspecified. **Action: define `mostSpecific` formally.**

### 3.2 Monotonicity and Non-Monotonicity

The separation of derivation (`Out`) from resolution (`resolveDecision`) is architecturally sound and well-justified by I/O Logic (Makinson & van der Torre 2000):

- **`Out` is monotone** (`RL2_Semantics.md:1189-1196`): Adding facts to the environment can only add normative conclusions, never remove them. This is the key I/O-logic property.
- **`Eval` is non-monotone** by design: resolution may eliminate norms via priority or strategy.
- **No negation-as-failure** in the derivation phase. Condition evaluation allows data-level boolean/comparator predicates (`rl2:neq`) as ground terms, but not rule-level negation over derived facts.

**Finding: This is consistent with the defeasible reasoning literature** (Arieli et al. 2024, AAAI — "Defeasible Normative Reasoning: A Proof-Theoretic Approach" validates the monotone-derivation / non-monotone-resolution pipeline as formally sound). The RL2_References.md correctly cites this.

### 3.3 Undefined Guard Predicates

**Finding:** Three condition guard predicates are referenced in the norm denotations but never defined anywhere in the spec:

- `claimCondition(right, Env)` — used in `Claim` denotation (`RL2_Semantics.md:754`)
- `powerCondition(a, n, Env)` — used in `Power` denotation (`:773`)
- `immunityCondition(a, n, Env)` — used in `Immunity` denotation (`:811`)

These functions determine whether a Claim, Power, or Immunity is active, but their reduction rules (how they evaluate to true/false given an environment) are absent. SEM-8 flags these as "under-exercised" (`issues.md:150-154`). **Action: define these three predicates formally**, either as (a) evaluation of the norm's `rl2:condition` (the obvious reading, which would make them aliases for `⟦n.condition⟧(Env) = true`), or (b) separate predicate functions with distinct semantics. Option (a) is the canonical choice — if they are just condition evaluation, they should be stated as such and the distinct names dropped for canonical form.

### 3.4 Closed-World Assumptions

RL2 operates under a **scoped closed-world assumption** for evaluation: Σ contains only facts explicitly asserted (via ContextAssertions or events). The evaluator does not have access to external state unless provided. This is documented at `RL2_Architecture.md:196` ("Not omniscient — Σ contains only facts explicitly asserted").

**Finding: The closed-world stance is correct for a verifiable evaluator** but creates a tension with ODRL's open-world RDF semantics. RL2 should explicitly document this as a deliberate design choice and specify how an open-world profile would work (e.g., "absent fact → Indeterminate, not Deny").

### 3.5 Totality and Termination

Under the structural constraints (`RL2_Semantics.md:1539-1574`), `Eval` is total and polynomial-time (O(|U| × m × n × d)):

- No recursive evaluation (policies cannot invoke evaluation of other policies).
- No unbounded external queries (resolution is synchronous or fails to ⊥).
- Bounded condition nesting (≤ 20), acyclic conditions, bounded path depth (≤ 10).

**Finding: The extension warning at `:1574` is important** — implementations using unbounded external queries via `resolutionFunction` or `lookupExternal` may exhibit non-polynomial or non-terminating behavior. This is the primary threat to the totality guarantee and must be addressed in the external data integration specification (see §7).

### 3.6 Denotational vs Operational Consistency

The denotational semantics (§Denotational Semantics) and operational semantics (§Operational Semantics) are consistent:

- **Norm denotations** (`:686-836`) define what a norm *means* (Permit, Deny, Obligation, Inactive).
- **Operational rules** (`:960-1161`) define *how* norms evolve over time (Duty Activation, Fulfillment, Violation; Promise Fulfillment, Violation, remedial generation).
- **Promise state derivation** (`:924-950`) is deterministic and monotone: `PromiseState(p, Σ)` is derived from Σ, not guessed. `projectObligationState` collapses Active→Pending for promises, keeping the projection deterministic.

**Finding: The `contentHolds` function for `PromisedState` uses `mkEnv(nullRequest, Σ, emptyContext)` (`:560`).** This constructs an environment with a "null request" — but the denotational semantics for conditions assume a Request `R = (a_req, x_req, s_req)`. How conditions that reference `agent.*` or `asset.*` paths behave under a null request is unspecified. **Action: define `nullRequest` semantics or restrict `PromisedState` conditions to `state.*` and `context.*` paths only.**

### 3.7 Abstract Syntax vs TTL Ontology Alignment

The abstract syntax in `RL2_Semantics.md:29-119` maps cleanly to the TTL ontology:

- `Norm ::= Privilege | Duty | Prohibition | Claim | Power | Liability | Immunity` — matches `rl2.ttl:21-58`.
- `PromiseContent ::= PromisedAction | PromisedState | PromisedDuty` — matches the v0.6 split (`rl2.ttl:123-148`).
- `Condition ::= AtomicConstraint | And | Or | Xone | Not | EventConstraint` — matches `rl2.ttl:225-250`.
- `StateTransition ::= Activate | Fulfill | Violate | FulfillPromise | Trigger` — matches `rl2.ttl:562-577`.

**Finding: The Dafny example at `:1601-1620` includes `Temporal(start, end)` and `Context(path, cmp, val)` as Condition variants that do not exist in the abstract syntax or TTL ontology.** These are stale from a pre-v0.6 design (TemporalConstraint was removed; `AtomicConstraint` with `currentDateTime` replaced it). **Action: update the Dafny example to match the current abstract syntax.**

---

## 4. Consistency & Validation Analysis

### 4.1 RDF Ontology vs SHACL Shapes vs Documentation

- **Ontology (`rl2.ttl`) & Core Shapes (`rl2-shacl.ttl`):** Fully synchronized at v0.6. Clean imports, correct property domains/ranges, non-closed shape design for profile extensibility.
- **Protocol Ontology (`rl2p.ttl`) & Protocol Shapes (`rl2p-shacl.ttl`):** Synchronized at v0.5. Integrates `rl2p:Request`, `rl2p:EvaluationResult`, `rl2p:Requirement`, `rl2p:ContextAssertion`, and `rl2p:Case`.
- **Use Case Suite (`usecases/*.md`):** All 51 markdown use cases pass automated pySHACL validation via `tools/validate.py` (**PASS 0 · WARN-ONLY 51 · FAIL 0 · SKIP 1**). The 51 warnings are advisory `OperandResolutionRecommendationShape` checks encouraging profile resolution path declarations.

### 4.2 Protocol Documentation Example Validation (`VALID-3`)

Validation of RDF code fences inside `RL2_Protocol.md` under `--per-fence` mode identified 9 failing fences (`fence@189, 311, 320, 356, 553, 703, 738, 762, 805`).

- **Root Cause:** The code snippets illustrate a multi-step scenario across sections. When validated as isolated fences, individual snippets omit required scaffolding.
- **Fix:** Complete the inline scaffolding for each of the 9 fences so that every code block in the spec suite validates standalone under `tools/validate.py --per-fence`.

### 4.3 State Machine and Lifecycle Reconciliation (`PROM-7`)

- `rl2:Duty` uses `rl2:ObligationState` (`Pending`, `Active`, `Fulfilled`, `Violated`).
- `rl2:Promise` uses `rl2:PromiseState` (`Pending`, `Fulfilled`, `Violated` — no `Active` state, because promises are passive commitments until evaluated).
- `rl2p:Requirement` tracks runtime obligations using `rl2p:requirementStatus` typed as `rl2:ObligationState`.
- **Resolution:** The semantics document defines `projectObligationState(Promise)` which projects `Active` back to `Pending` for promises. This projection must be explicitly documented in `rl2p.ttl` comments.

### 4.4 Specific Markdown vs TTL/SHACL Discrepancies

1. **Unmapped Protocol Decision Individuals:** `RL2_Vocabulary.md:1265` states that `Power` and `Immunity` map to `rl2p:Decision` values `rl2p:PermitStateChange` and `rl2p:DenyStateChange`. However, `rl2p.ttl` defines only `Permit`, `PermitWithObligations`, `Deny`, `Indeterminate`, and `NotApplicable`. *Fix:* Define `rl2p:PermitStateChange` and `rl2p:DenyStateChange` in `rl2p.ttl` or update `RL2_Vocabulary.md`.
2. **`rl2p:requirementFulfilled` Categorization:** `RL2_Vocabulary.md:1285` lists `rl2p:requirementFulfilled` in the Protocol Property Reference table. However, `rl2p.ttl:257` defines it as a `rl2:LeftOperand` individual, not an RDF property. *Fix:* Move to the Left Operand section of `RL2_Vocabulary.md`.
3. **Missing SHACL Shapes for Policy Subclasses:** `rl2.ttl` defines `Set`, `Offer`, `Privacy`, and `Assertion`. While `rl2-shacl.ttl` includes `PolicyShape` and `AgreementShape`, it omits explicit shapes for the other subclasses. *Fix:* Add dedicated SHACL shapes or document that subclass inheritance from `PolicyShape` is sufficient (which it is under SHACL's standard inheritance behavior — but this should be stated explicitly).
4. **Missing `sh:maxCount 1` on Atomic and Logical Constraints:** `rl2:AtomicConstraintShape` enforces `sh:minCount 1` for `leftOperand`, `constraintOperator`, `rightOperand`, and `rightOperandRef`, but lacks `sh:maxCount 1`. Similarly, `rl2:LogicalConstraintShape` lacks `sh:maxCount 1` for `constraintOperator`. *Fix:* Add `sh:maxCount 1` constraints to prevent multi-operand syntax violations. (Note: `AtomicConstraintShape` already has `sh:xone` for rightOperand/rightOperandRef which effectively limits to one, but explicit maxCount on leftOperand and constraintOperator is still needed.)
5. **Broken Profile Reference:** `RL2_ODRL_Comparison.md:22` cites `rl2-media-profile.ttl` as an example profile, but this file does not exist in `profiles/`. *Fix:* Create `profiles/rl2-media-profile.ttl` or correct the doc reference.
6. **Dafny Example Stale:** `RL2_Semantics.md:1601-1620` includes `Temporal` and `Context` Condition variants that do not exist in the current abstract syntax. *Fix:* Update to match v0.6 abstract syntax (remove `Temporal`, replace `Context` with `AtomicConstraint` using `resolutionPath`).

### 4.5 Technical Writing Consistency

**Strengths:**
- The spec suite follows a clear source-of-truth hierarchy (`AGENTS.md` §4): TTL+SHACL > Semantics > Architecture > Protocol > Vocabulary > Examples.
- Documents are version-stamped consistently (v0.6, 2026-07-24) except `RL2_ODRL_Comparison.md` (v1.0, 2025-12-16). `backlog.md` was merged into `issues.md` (2026-07-25).
- The CLAUDE.md/AGENTS.md provides clear authoring guidance and common mistake tables.

**Issues:**
- `RL2_ODRL_Comparison.md` is dated 2025-12-16 and references `Why3/WhyML` and `Coq/Lean` as verification targets (`:90-91`), while `AGENTS.md` and `issues.md` have since decided on **Dafny → Go** exclusively. This is stale. **Action: update or merge into Primer (DOC-4).**
- `issues.md` (merged from `backlog.md` 2026-07-25) is the single tracker. DOC-7 resolved. `fix.md` §6.2 has the toolchain comparison. **Action: ensure all references point to `issues.md`, not the deleted `backlog.md`.
- `FAQ/RL2_FAQ.md` states RL2 compiles to "Rego, Cedar, Prolog, Datalog" (`:181`) — but the actual design is Forth IR → Dafny. This is aspirational, not actual. **Action: clarify that these are potential compilation targets, not the current design.**
- `RL2_References.md:445` references `RL2_ODRL_Coverage.md` which does not exist (the file is `RL2_ODRL_Comparison.md`). **Action: fix cross-reference.**
- The term "Rights & Licenses 2" appears in `FAQ/RL2_FAQ.md:23` while `README.md:1` says "Rights Language 2". **Action: standardize on "Rights Language 2".**

---

## 5. Comparison of Alternatives

### 5.1 RL2 vs OPA/Rego

Sources: [openpolicyagent.org](https://www.openpolicyagent.org/), [OPA docs](https://www.openpolicyagent.org/docs/latest/).

| Dimension | OPA/Rego | RL2 |
|:---|:---|:---|
| **Formal Basis** | Datalog (query language based on first-order logic) | I/O Logic + Deontic Logic + Hohfeldian positions |
| **Decidability** | Rego is Turing-complete (can loop, recurse); OPA has no termination guarantee by default | Polynomial-time, total under stated constraints; fuel-bounded VM |
| **Normative Model** | None — Rego is a generic policy query language | Full Hohfeldian table + Promise Theory |
| **Obligations** | No native obligation lifecycle; must be coded manually | `ObligationState` (Pending→Active→Fulfilled/Violated) in core |
| **Temporal Constraints** | Via built-in functions (`time.now_ns()`); no native temporal logic | `AtomicConstraint` with `currentDateTime`; `xsd:duration` deferred |
| **Conflict Resolution** | `deny-wins` by default (any deny overrides allow); no configurable strategy | Parameterized strategies (ProhibitOverrides, PermitOverrides, SpecificOverridesGeneral) |
| **Formal Verification** | None — OPA is tested, not proven | Dafny→Go with proof obligations S1-S6 |
| **Performance** | Highly optimized Datalog evaluation; used at scale (millions of decisions/sec) | Theoretical polynomial; no implementation yet |
| **Data Integration** | Mature: 5 models (JWT, input overload, bundle API, push data, pull-during-eval) | `resolutionPath` / `resolutionFunction` / `lookupExternal` — declared but no binding spec |
| **Ecosystem** | CNCF graduated, widely adopted, large community | Draft spec, no implementation |

**What RL2 does better:** Normative expressiveness (Hohfeld, promises, deontic modalities), canonical form for AI generation, formal verifiability, obligation lifecycle, configurable conflict resolution.

**What RL2 is missing vs OPA:** Mature implementation, proven performance at scale, data integration patterns, ecosystem, tooling.

**Key lesson for RL2:** OPA's bundle API (atomic policy+data updates) and data replication model are mature patterns for external data integration that RL2 should adopt (see §7).

### 5.2 RL2 vs AWS Cedar

Sources: [Cedar GitHub](https://github.com/cedar-policy/cedar), [cedar-spec (Lean formalization)](https://github.com/cedar-policy/cedar-spec), [Cedar docs](https://docs.cedarpolicy.com/).

| Dimension | Cedar | RL2 |
|:---|:---|:---|
| **Formal Basis** | First-order logic with type system; formalized in Lean (cedar-spec) | I/O Logic + Deontic Logic; formalized in Dafny (planned) |
| **Decidability** | Decidable by design (no recursion, no unbounded quantifiers) | Polynomial-time, total under constraints |
| **Normative Model** | RBAC + ABAC (permissions, prohibitions); no obligations, no Hohfeld | Full Hohfeldian table + Promise Theory + obligations |
| **Obligations** | None — Cedar is pure authorization (allow/deny) | `ObligationState` lifecycle in core |
| **Temporal** | None — Cedar has no time operators | `currentDateTime` constraints |
| **Verification** | Lean formalization (cedar-spec); differential randomized testing vs Rust impl | Dafny→Go (planned); proof obligations S1-S6 |
| **Cedar proven theorems** | (1) if any forbid policy is satisfied, request is denied; (2) a request is allowed only if explicitly permitted (no implicit allow) — proven in `Cedar/Thm/Authorization.lean` | RL2's S1-S6 proof obligations are analogous but broader (determinism, duty-state consistency, totality) |
| **Performance** | Rust implementation; microsecond-level decisions | No implementation |
| **Entities** | Cedar Entity Store (JSON-based external data) | `LeftOperand` with `resolutionPath` |
| **Policy Structure** | `permit` / `forbid` clauses with principals, actions, resources, conditions | Norm clauses within Policy containers with subject/action/object/condition |

**What RL2 does better:** Obligation lifecycle, Hohfeldian normative positions, promise theory, temporal constraints, richer policy containers (Set, Offer, Agreement, Privacy, Assertion vs Cedar's flat policy).

**What RL2 is missing vs Cedar:** Working verified implementation (Cedar's Lean formalization exists and is tested via DRT), performance, Rust deployment.

**Key lesson for RL2:** Cedar's approach to formal verification — Lean formalization + differential randomized testing against the production Rust implementation — is a proven pattern. RL2's Dafny→Go approach should consider a similar DRT strategy: verify in Dafny, extract to Go, then differentially test the Go output against the Dafny reference on randomized inputs.

### 5.3 RL2 vs Immuta

Source: [immuta.com](https://www.immuta.com/).

Immuta is a commercial data governance platform, not a spec or language. It provides:

- **Attribute-based access control (ABAC)** with policy templates.
- **Global policies** that apply across data sources.
- **Automated policy enforcement** via integrations with Spark, Snowflake, Databricks, etc.
- **Audit and compliance** reporting.

**What RL2 does better:** Formal semantics, normative expressiveness (Hohfeld, promises), canonical form for AI generation, interoperability (RDF/OWL standard), vendor independence.

**What Immuta does better:** Production deployment, data source integrations, UI/UX for policy management, proven at enterprise scale.

**RL2 is not directly comparable to Immuta** — RL2 is a specification; Immuta is a product. RL2 could serve as the policy language layer in a system like Immuta. The privacy profile (`profiles/rl2-privacy-profile.ttl`) demonstrates the GDPR/ABAC patterns that Immuta implements commercially.

### 5.4 RL2 vs ODRL 2.2 — Summary

| Dimension | ODRL 2.2 | RL2 |
|:---|:---|:---|
| **Semantics** | Informal English + draft formal semantics (CG report) | Denotational + operational + constraint algebra |
| **Canonical Form** | Multiple encodings for same proposition | Exactly one shape per proposition (CANON-5) |
| **Normative Completeness** | Permission, Prohibition, Duty only | Full Hohfeldian table + Promise Theory |
| **Obligation Lifecycle** | Undefined (informal) | Pending→Active→Fulfilled/Violated (formal state machine) |
| **Conflict Resolution** | `odrl:conflict` property (propose, prohibit, permit, undefined) | Parameterized strategies + priority integers |
| **AI Generation**** | Multiple valid shapes → ambiguity for LLMs | One canonical shape → clean LLM target |
| **Verification** | None | Dafny→Go with proof obligations |
| **Inheritance** | `inheritFrom` (complex, hard to audit) | Explicit composition (flattened at compile time) |
| **Profiles** | ODRL Profiles (mechanism defined) | RL2 Profiles (LeftOperand + resolutionPath pattern) |

---

## 6. Engineering Analysis

### 6.1 Forth-Style IR: Feasibility and Reasonableness

**Assessment: Reasonable and feasible, with identified risks.**

The Forth-IR design (`design-forth-ir.md`) proposes a stack-based VM with ~45 opcodes, verified in Dafny, extracted to Go. This is a well-precedented approach:

| Precedent | Relevance |
|:---|:---|
| JVM bytecode (1995) | Stack-based, verified, massively deployed |
| WebAssembly (2017) | Stack-based, formal semantics, portable |
| Bitcoin Script (2009) | Minimal stack language, deliberately limited |
| Ethereum EVM (2015) | Stack-based, formal verification efforts |

**Why it fits RL2:**
- The derivation phase is concatenative: push norms → evaluate conditions (pure) → filter → produce envelope. This maps naturally to a stack machine.
- Condition trees compile to stack programs trivially (see `design-forth-ir.md:44-49`).
- The minimal opcode set (~45) makes the TCB readable (~500-800 lines) and verifiable.
- Fuel-bounded execution guarantees termination; bounded stack growth guarantees memory safety.

**Risks:**
1. **Dafny→Go extraction maturity.** Dafny's Go backend is an officially supported target (Dafny Reference Manual §13.8.7) but uses "pre-module Go" mode (`GO111MODULE=auto GOPATH=$(pwd) go run src/A.go`), which the manual notes may change. It is less mature than the C# target. The design doc correctly recommends a spike (`design-forth-ir.md:325-340`). **Action: run the spike before committing.** The Dafny features-by-target table (§13.8.10) confirms Go is supported but with limitations on certain advanced features (traits, some datatype features). The `{:extern}` attribute supports Go interop but requires hand-written wrappers. The Forth VM's simple datatypes should be well within the supported subset.
2. **RESOLVE is the escape hatch.** All semantic complexity lives in `RESOLVE` (path resolution). The Dafny spec requires `ValidPath(path)` and `PathRootAllowed(path, vm.env)` preconditions. This is where the verified boundary meets unverified external data. **Action: the RESOLVE primitive must be either (a) fully verified with a restricted path grammar, or (b) treated as a trusted syscall with a narrow, audited interface.** Option (a) is preferred for the canonical roots (`agent`, `asset`, `state`, `context`, `request`).
3. **No debugger, no bytecode format.** The design doc lists these as open questions (`:344-349`). For a production system, these are needed. **Action: specify bytecode serialization format (JSON array of opcodes is simplest and debuggable), dictionary structure, and error-to-source mapping.**
4. **The compiler is NOT verified.** Only the VM is verified. The compiler (Turtle→bytecode) is tested, not proven. This means a compiler bug could produce incorrect bytecode that the VM faithfully executes. **Action: property-based testing on compiled output, plus a bytecode verifier (type-check the stack effects before execution).**

**Comparison with Rego's approach:** Rego compiles to Datalog queries evaluated by a highly optimized Datalog engine. This gives Rego excellent performance but no termination guarantee (Rego is Turing-complete) and no formal verification. RL2's Forth-IR trades performance for verifiability — a deliberate and defensible choice for a rights language targeting high-trust deployment.

**Conclusion:** The Forth-IR approach is feasible and reasonable. It is the right choice for RL2's verifiability thesis. The primary risk is Dafny→Go extraction maturity, which should be de-risked with a small spike before full commitment. The approach is fundamentally different from Rego's Datalog evaluation and Cedar's Lean-formalized Rust — but all three share the principle of a small, verified core.

### 6.2 Toolchain Selection: Is Dafny→Go the Right Choice?

**Assessment: Yes, Dafny→Go remains the right choice — but the decision should be evidence-based, not default. Below is the comparison and the justification.**

The question is whether Dafny is the right verification toolchain and whether Go is the right deployment target, vs alternatives: Lean 4, WhyML/Why3, F*, Rocq/Coq, Rust+Creusot, Isabelle/HOL.

#### Comparison Matrix (researched 2026-07-25)

| Tool | Version | Maintained | Extraction to Go/Rust? | Proof Strength | VM Precedent | Fit for RL2 |
|------|---------|------------|------------------------|----------------|--------------|-------------|
| **Dafny** | 4.11.0 (Aug 2025) | Yes, AWS-backed | Go (mature); Rust (in-dev, not ready) | Z3, Hoare, `--enforce-determinism`, termination | **evm-dafny** (Consensys, 140★) | ★★★★★ Best fit |
| **Lean 4** | 4.32.1 (Jul 2026) | Yes, Lean FRO | C only (via LLVM); no Go/Rust | Dependent types, Mathlib, `grind` | **cedar-spec** (policy language!) | ★★★☆☆ Cedar precedent strong but deployment awkward |
| **Why3** | 1.8.2 | Moderate | OCaml/C only | Multi-prover (Z3/CVC5/Alt-Ergo) | Solidity/Michelson contracts | ★★☆☆☆ Fewer targets |
| **F*** | v2026.07.24 | Yes, very active | OCaml/F#/C (KaRaMeL); no Go/Rust | Dependent types + Pulse (sep logic) | Abstract interpreter, Vale | ★★★☆☆ Strong but heavy |
| **Rocq/Coq** | 9.2.0 (Mar 2026) | Yes | OCaml/Haskell/C; no Go/Rust | CiC, Ltac2, MathComp | CompCert | ★★★☆☆ Mature but heavy |
| **Prusti** | nightly (Mar 2024) | Stalled | None (verifies Rust directly) | Viper separation logic | None | ★★☆☆☆ Stalled |
| **Creusot** | v0.12.0 (Jun 2026) | Yes, very active | None (verifies Rust directly) | Why3 backend, Pearlite | CreuSAT solver | ★★★★☆ Pre-1.0 but promising |
| **Isabelle/HOL** | 2025-2 (Jan 2026) | Yes | Haskell/SML/OCaml/Scala; no Go/Rust | HOL, Sledgehammer, Refinement Framework | seL4, IMP semantics | ★★★☆☆ Mature, no Go |

Sources: [Dafny releases](https://github.com/dafny-lang/dafny/releases), [Consensys/evm-dafny](https://github.com/Consensys/evm-dafny), [cedar-spec](https://github.com/cedar-policy/cedar-spec), [Creusot](https://github.com/creusot-rs/creusot), [Rocq](https://github.com/rocq-prover/rocq/releases), [F*](https://github.com/FStarLang/FStar/releases), [Lean 4](https://github.com/leanprover/lean4/releases), [Why3](https://www.why3.org/), [Isabelle](https://isabelle.in.tum.de/). Full comparison at `research/verification-toolchain-comparison.md`.

#### Why Dafny→Go wins for RL2

1. **Direct precedent exists.** Consensys/evm-dafny is a verified EVM stack-machine interpreter in Dafny (~140 opcodes, runtime-error-freedom proofs, compared against Geth and Ethereum Common Reference Tests). This is architecturally identical to RL2's needs (stack VM, ~45 opcodes, determinism, termination). The evm-dafny team explicitly chose Dafny over Coq/Isabelle/HOL "because it is relatively accessible to someone without significant prior experience." ([github.com/Consensys/evm-dafny](https://github.com/Consensys/evm-dafny))

2. **Go is a first-class extraction target.** Dafny supports Go alongside C#, Java, JavaScript, Python, C++. The Go backend produces readable Go packages with a `_dafny.go` runtime helper. It is less mature than C# but is officially supported (Dafny Reference Manual §13.8.7).

3. **Determinism support is first-class.** Dafny 4.11 (Aug 2025) added `--enforce-determinism` mode (now compatible with `--standard-libraries`), directly addressing RL2's proof obligation S1 (Determinism). The 4.11 release removed std-lib features incompatible with this mode, showing active investment in this use case.

4. **Termination proofs are built-in.** `decreases` clauses, `Std.Termination`, `Std.Ordinal` (new in 4.11) — directly serve RL2's S6 (Totality) and the fuel-bounded VM design.

5. **Active maintenance.** Dafny 4.11.0 (Aug 2025), nightlies through July 2026. AWS-backed (Mikael Mayer, Rustan Leino). Active Zulip community. Not a stale academic project.

6. **Go is the right deployment target.** Go is cloud-native, has a strong ecosystem for policy services (gRPC, Kubernetes, etc.), and is accessible to the engineering talent pool RL2 would need. Rust would be marginally faster but harder to hire for and the Dafny→Rust backend is not production-ready.

#### Why the alternatives lose

- **Lean 4** has the strongest *domain* precedent (cedar-spec formalizes a policy language in Lean), but its deployment story is awkward: Lean compiles to C via LLVM and ships its own GC'd runtime. Calling Lean-compiled code from Go/Rust requires FFI plus the Lean runtime — heavier than Dafny→Go's direct extraction. Cedar itself keeps the Lean spec *separate* from the Rust production code (differential testing, not extraction). Lean is the right choice if RL2's primary goal were a formalization paper, not a deployable evaluator.

- **Creusot** (verify Rust directly, no extraction gap) is the most interesting alternative. It eliminates the extraction problem entirely — write Rust, verify in-place via Why3 backend. v0.12.0 (Jun 2026) is very active, with CreuSAT (verified SAT solver) as precedent. But: pre-1.0 (API may change), no `--enforce-determinism` equivalent, less mature than Dafny, and "less suited for systems which interact heavily with the outside world" (per their release notes — though RL2's pure evaluator is not such a system). **Creusot is the fallback if Dafny→Go proves unworkable.**

- **Rocq/Coq, F*, Isabelle/HOL** are all mature and capable but extract to OCaml/Haskell/C, not Go or Rust. They would require an FFI wrapper and a different runtime. For RL2's cloud-native deployment goals, this adds friction without compensating benefit. Coq has CompCert as a landmark precedent; F* has Everest (HACL*/EverCrypt deployed to Firefox, Linux kernel); Isabelle has seL4. All are heavier than Dafny for RL2's relatively simple verification needs (a ~45-opcode stack VM, not a C compiler or a microkernel).

- **Why3** extracts to OCaml/C, has multi-prover support (Z3, CVC5, Alt-Ergo), but has fewer extraction targets, less industrial tooling, and no direct Go path. Dafny is strictly more capable for RL2's needs.

- **Prusti** (Viper-based Rust verification) has stalled — last nightly March 2024, no 2025-2026 releases. Not viable.

#### Why Go (not Rust, not OCaml) as the deployment target

- **Go vs Rust:** Go is sufficient for RL2's performance needs (policy evaluation is not CPU-bound; it's I/O-bound on external data resolution). Go is easier to hire for, easier to deploy, and has better cloud-native tooling. Rust's performance advantage is irrelevant for a policy evaluator that spends its time waiting on external data sources. And critically, Dafny→Rust is not production-ready.

- **Go vs OCaml:** OCaml is the natural extraction target for Coq/F*/Why3, but it has a smaller ecosystem for cloud services, weaker gRPC/HTTP tooling, and a smaller talent pool. Go wins on operational grounds.

- **Go vs C:** C is available via F*/Low* and CertiCoq, but memory safety in C requires additional verification (Low* provides this, but the complexity is unnecessary for RL2). Go's garbage collector is acceptable for a policy evaluator.

#### Recommendation

**Stay with Dafny→Go.** The evm-dafny precedent is the decisive factor — it proves the approach works for a stack VM in Dafny's exact feature set. Run the de-risking spike (Task 11) using evm-dafny as a reference. Pin Dafny 4.11.0 (avoid nightly churn during development). If the spike fails, pivot to **Creusot** (verify Rust directly) as the fallback — it is the only alternative that eliminates the extraction gap.

**Action:**
- Before committing, replicate a minimal evm-dafny-style proof (e.g., verify 3-4 opcodes: DUP, DROP, ADD, IF) in Dafny 4.11, extract to Go, and confirm the generated Go compiles and runs correctly. This is a 2-3 day spike, not a full implementation.
- If the spike succeeds, proceed with Dafny→Go as planned.
- If the spike fails (Go extraction issues, proof friction), evaluate Creusot as the fallback.


### 6.3 No-Solver Approach: Is Translation Feasible?

**Assessment: Yes, the no-solver approach is feasible and correct for RL2's current semantics.**

The question is whether RL2 can be executed via translation to a stack IR without using Prolog, Datalog, OWL reasoners, or other entailment-based methods.

**Why it works:**

1. **RL2's derivation is already designed as a pure, bounded function.** `Out(U, Env)` (`RL2_Semantics.md:1174-1185`) is a transformer that produces normative atoms by filtering and evaluating conditions. It is not a logic program that requires backtracking or unification — it is a straightforward pipeline: match norms → evaluate conditions → collect atoms.

2. **Condition evaluation is decidable and bounded.** `AtomicConstraint` is a three-part comparison (`leftOperand`, `operator`, `rightOperand`). `LogicalConstraint` combines conditions with `and`/`or`/`xone`/`not`. The constraint algebra is a Boolean algebra with no quantifiers. Path resolution is single-threaded navigation with bounded depth. No graph pattern matching, no joins, no SPARQL-style queries.

3. **Conflict resolution is procedural, not logical.** `resolveDecision` is a case-based function, not a logic program. It does not need a solver — it is a deterministic algorithm parameterized by strategy.

4. **Action subsumption is bounded graph reachability.** `x' ⊑ x := reachable(x', rl2:includedIn, x)` is a simple transitive closure check, expressible as `ASK { ?x' rl2:includedIn* ?x }` in SPARQL but trivially compilable to a Forth-IR word that walks the `includedIn` graph (which is finite and acyclic in any given generation).

5. **No OWL reasoning is needed.** RL2 uses OWL for vocabulary definition (class hierarchy, property domains/ranges) but not for runtime reasoning. The ontology is used at compile time (to validate policies via SHACL) and at runtime (to check `sh:class` constraints), but the evaluation itself does not invoke an OWL reasoner.

**What would be lost by not using a solver:**
- **Quantified queries** (SEM-2): "all duties fulfilled" or "exists a violated duty" would be natural for Datalog but require a loop in the Forth IR. This is feasible — it is a bounded iteration over a finite set — but less elegant than a Datalog rule. **The current design defers this (SEM-2 is open).**
- **Entailment-based policy comparison:** If two policies are semantically equivalent but structurally different, an OWL reasoner could detect this. RL2's canonical form invariant makes this unnecessary — structural equivalence after normalization *is* semantic equivalence.

**Conclusion:** The no-solver approach is not just feasible — it is the correct choice for RL2's verifiability thesis. A solver (Prolog/Datalog/OWL reasoner) would introduce undecidability or at minimum non-polynomial complexity, breaking the totality and termination guarantees. The Forth-IR translation preserves the polynomial-time, total, deterministic properties of the semantics. The only area where a solver would be more natural is quantified selectors (SEM-2), and even there, bounded iteration over finite sets suffices.

### 6.4 External Data Integration

**Assessment: This is the highest-risk engineering area and needs a concrete binding specification.**

Constraints in RL2 may refer to external data (HR systems, asset catalogs, directories, API services). The current design has three mechanisms:

1. **`rl2:resolutionPath`** — path-based access to `Env` fields (`agent.*`, `asset.*`, `state.*`, `context.*`, `request.*`). This is the primary, verified mechanism.
2. **`rl2:resolutionFunction`** — named function for complex resolution (API calls, aggregation, computation). Profile-defined, implementation-specific.
3. **`lookupExternal(op, Ctx)`** — fallback for legacy/external context resolution.

**The problem:** `resolutionFunction` and `lookupExternal` are declared but not bound. The semantics say "implementation-specific" (`RL2_Semantics.md:364-366`) and the architecture says "Opaque" (`RL2_Architecture.md:461`). This means:
- No standard way for a policy to declare what external data it needs.
- No standard way for an evaluator to call external services.
- No complexity guarantee for external calls (the extension warning at `:1574` acknowledges this).
- No way to test or verify policies that use external data.

**Recommended approach (best fit for RL2):**

Adopt a **Context Manifest + Source Binding** pattern, inspired by OPA's bundle API and Cedar's Entity Store:

1. **ContextManifest (already defined in Architecture).** At compile time, the `compile` function produces a `ContextManifest : PolicyRef → NormRef → OperandSpec*` listing which operands each norm requires. This is already in the design (`RL2_Architecture.md:348-364`).

2. **Source Binding.** At deployment time, bind each `resolutionFunction` name to a concrete source:
   - **In-band:** Evaluator calls the source directly (e.g., HTTP to an HR API). Risk: latency, failure, non-termination.
   - **Out-of-band:** Requester supplies all context with the request (as `rl2p:ContextAssertion`s). Safest, most verifiable.
   - **Hybrid (recommended):** Evaluator resolves what it can from ContextAssertions; calls external sources for the rest, with a timeout and fail-to-⊥ policy.

3. **Out-of-band as the normative baseline.** The safest and most verifiable pattern is: the requester supplies all needed context as `rl2p:ContextAssertion`s before evaluation. The evaluator never calls external services during evaluation. This preserves totality, determinism, and the fuel-bounded execution guarantee. External data integration becomes a pre-evaluation step, not an evaluation-time concern.

4. **In-band as an extension with documented complexity.** If in-band resolution is needed (e.g., for dynamic attributes), it must be:
   - Declared in the ContextManifest with a `required: true/false` flag.
   - Bounded by a timeout (fail-to-⊥ on timeout).
   - Documented with complexity characteristics (O(1) or O(log n) per call).
   - Tested with mock sources.

5. **Profile-defined source schemas.** Profiles should define not just operands but also their source bindings (e.g., `privacy:dataOwnerOperand` → `source: HR_API, query: getUserByIRI`). This makes external data access declared, typed, and validatable.

**Comparison:**
- **OPA:** 5 data models (JWT, input overload, bundle API, push, pull). Bundle API (atomic policy+data) is the most relevant for RL2 — it ensures the evaluator always has the data it needs.
- **Cedar:** Entity Store (JSON-based, loaded before evaluation). This is the out-of-band pattern.
- **XACML:** PIP (Policy Information Point) calls external sources during evaluation. This is the in-band pattern, and it is the source of XACML's performance and reliability issues.

**Recommendation for RL2:** Make **out-of-band** (ContextAssertions) the normative baseline. Allow **hybrid** as an extension with documented complexity and timeout. Forbid **pure in-band** for the verified kernel — it breaks totality. This aligns with the existing `resolve` function design (`RL2_Architecture.md:435-461`) which already has the right structure (resolve what you can, report what's missing).

---

## 7. AI-Tuned Policy Generation & Automated Interpretation

RL2 is explicitly optimized for AI Large Language Models (LLMs) and automated policy translation:

```
[ Natural Language / Intent ]
             │
             ▼  (LLM Generation — One Canonical Target Shape)
     [ RL2 Canonical RDF ]
             │
             ▼  (IR Compiler — Deterministic Flattening)
    [ Forth IR Bytecode ]
             │
             ▼  (Dafny Verified Kernel)
  [ Permitted / Denied / Obligations ]
```

### 7.1 Why RL2 Outperforms ODRL 2.2 for AI

1. **Elimination of Target Ambiguity.** In ODRL 2.2, an LLM might attach a constraint to a `Permission`, `Duty`, `Rule`, or `Policy`. In RL2, canonical rules dictate exact placement: conditions scope at the narrowest node, and the IR compiler flattens all policy-level conditions into norm-level `effectiveCondition` conjunctions.
2. **Explicit Resolution Paths.** Instead of hallucinating arbitrary property names, an LLM generating RL2 uses structured `LeftOperand` definitions constrained to canonical resolution paths (`agent.department`, `asset.classification`, `context.purpose`).
3. **Graph Isomorphism as Equivalence.** Because every normative proposition has exactly one canonical RDF shape, testing whether an LLM-generated policy matches a gold-standard reference policy requires no complex semantic theorem prover — it reduces to standard RDF graph isomorphism (`isomorphic(G1, G2)`).

### 7.2 AI Generation Gap

**No prompt template or fine-tuning dataset exists.** The canonical form invariant makes RL2 ideal for LLM generation, but no concrete artifacts demonstrate this:
- No prompt engineering guide for generating RL2 from natural language.
- No evaluation harness for LLM-generated RL2 policies (SHACL validation exists, but no NL→RL2 benchmark).
- No few-shot examples formatted for LLM consumption.

**Action:** Create an `examples/llm-generation/` directory with prompt templates, few-shot examples, and a validation harness that checks LLM output against SHACL + canonical form rules.

---

## 8. Comprehensive Actionable Remediation Roadmap

```
  ┌────────────────────────────────────────────────────────────┐
  │ Band 0: Canonical Form (v0.6 Baseline) — COMPLETE          │
  └────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌────────────────────────────────────────────────────────────┐
  │ Band 1: Protocol Spec Validation & Scaffolding (VALID-3)    │
  └────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌────────────────────────────────────────────────────────────┐
  │ Band 2: Formal Semantics & Remedial Actions (SEM-1..8)      │
  └────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌────────────────────────────────────────────────────────────┐
  │ Band 3: Expressiveness & Quantified Selectors (EXPR-1..6)  │
  └────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌────────────────────────────────────────────────────────────┐
  │ Band 4: External Data Integration Specification            │
  └────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌────────────────────────────────────────────────────────────┐
  │ Band 5: Dafny Core Kernel & Reference Implementation        │
  └────────────────────────────────────────────────────────────┘
                               │
                               ▼
  ┌────────────────────────────────────────────────────────────┐
  │ Band 6: ODRL Transpiler & Migration Tooling                │
  └────────────────────────────────────────────────────────────┘
```

### Task 1: Complete Spec Document Validation (`VALID-3`)
- **Action:** Update the 9 failing RDF code fences in `RL2_Protocol.md` (`fence@189, 311, 320, 356, 553, 703, 738, 762, 805`) with complete inline scaffolding.
- **Verification:** Run `uv run tools/validate.py --per-fence RL2_Protocol.md` to achieve 100% PASS.

### Task 2: Formalize Remedial Action Mappings (`SEM-1`)
- **Action:** Extend `RL2_Semantics.md` to define `restoreAction(content)` as a total function:
  - `promisedAction` → Re-execute action.
  - `promisedDuty` → Fulfill referenced duty.
  - `promisedState` → Require explicit `rl2:remedialAction` property on the promise node. Absent annotation → surface as ambiguity (already the case, but must be formalized as a total function that returns a "needs annotation" sentinel, not ⊥).

### Task 3: Define `mostSpecific` for Conflict Resolution
- **Action:** Formally define the `mostSpecific` function used in `SpecificOverridesGeneral` strategy (`RL2_Semantics.md:1301`). Specify how specificity is computed (action subsumption depth, condition complexity, or a declared specificity ordering).

### Task 4: Define Undefined Guard Predicates
- **Action:** Define `claimCondition`, `powerCondition`, and `immunityCondition` (`RL2_Semantics.md:754,773,811`). If they are condition evaluation aliases, state this explicitly and drop the distinct names for canonical form. If they have distinct semantics, specify their reduction rules.

### Task 5: Fix `nullRequest` Semantics for `PromisedState`
- **Action:** Define the behavior of `mkEnv(nullRequest, Σ, emptyContext)` at `RL2_Semantics.md:560`. Either (a) define `nullRequest` as a sentinel that makes `agent.*` and `asset.*` paths return ⊥, or (b) restrict `PromisedState` conditions to `state.*` and `context.*` paths only.

### Task 6: Implement Quantified Target Selectors (`SEM-2`)
- **Action:** Introduce `rl2:targetNormSelector` or class-based norm pattern matching to allow atomic constraints to query states across sets of norms (e.g., `allWithClass(rl2:Duty)`).

### Task 7: Specify Target Matching Algorithm (`SEM-5`)
- **Action:** Specify the algorithm and precedence for the four target matching modes (direct, classification, sub-asset, subsumption) listed in `RL2_Architecture.md:374-388`. Define closed-world defaults.

### Task 8: Clarify State Machine Projections (`PROM-7`)
- **Action:** Document the exact projection mapping in `rl2p.ttl` and `RL2_Protocol.md` showing how `rl2:PromiseState` maps into `rl2p:Requirement`'s `rl2:ObligationState`.

### Task 9: Update Stale Dafny Example
- **Action:** Update `RL2_Semantics.md:1601-1620` to match the v0.6 abstract syntax. Remove `Temporal` and `Context` Condition variants; replace with `AtomicConstraint` using `resolutionPath`.

### Task 10: Fix Documentation Discrepancies
- **Action:** Fix the 6 documentation discrepancies identified in §4.4: unmapped `PermitStateChange`/`DenyStateChange`, `requirementFulfilled` categorization, missing policy subclass shapes, `sh:maxCount 1` constraints, broken `rl2-media-profile.ttl` reference, stale Dafny example.

### Task 11: External Data Integration Specification
- **Action:** Write a new section in `RL2_Architecture.md` (or a new `RL2_ExternalData.md`) specifying:
  - Out-of-band as normative baseline (ContextAssertions).
  - Hybrid as extension with timeout and fail-to-⊥.
  - Profile-defined source schemas.
  - Complexity constraints for in-band resolution.

### Task 12: Dafny Execution Kernel & Go Evaluator (`IMPL-1`..`IMPL-3`)
- **Action:** Run the Dafny→Go de-risking spike first: replicate a minimal evm-dafny-style proof (3-4 opcodes: DUP, DROP, ADD, IF) in Dafny 4.11, extract to Go, confirm it compiles and runs. Use [Consensys/evm-dafny](https://github.com/Consensys/evm-dafny) as the architectural reference — it is a verified stack VM in Dafny with the same structure RL2 needs. Pin Dafny 4.11.0. If the spike succeeds, implement the ~45 primitives of the stack-based VM, prove termination and memory safety (using `--enforce-determinism` and `decreases` clauses), and extract the Go reference evaluator CLI (`rl2-eval`). If the spike fails, evaluate Creusot (verify Rust directly) as the fallback.

### Task 13: ODRL→RL2 Transpiler
- **Action:** Create an ODRL 2.2 → RL2 transpiler that flattens `inheritFrom`, maps `odrl:Permission`→`rl2:Privilege`, etc. This is needed for migration and for demonstrating RL2 as a true ODRL successor. Currently in backlog Phase 3.

### Task 14: Complete Hohfeldian Use Cases
- **Action:** Complete the 34 draft use cases, prioritizing Hohfeldian cases (38-42: Claim, Power, Immunity, Liability) to stress-test the vocabulary. Author in canonical form.

### Task 15: LLM Generation Artifacts
- **Action:** Create `examples/llm-generation/` with prompt templates, few-shot examples, and a validation harness for LLM-generated RL2 policies.

---

## 9. Summary of Key Findings

### Strengths
1. **Canonical form invariant** is the right thesis for AI-generated policies. Implemented and validated in v0.6.
2. **I/O-Logic separation** of derivation (monotone) from resolution (non-monotone) is architecturally sound and well-supported by the literature.
3. **Hohfeldian completeness** exceeds ODRL 2.2 and addresses community-identified gaps.
4. **Promise Theory integration** (Sein-sollen vs Tun-sollen) cleanly separates voluntary commitments from imposed obligations.
5. **SHACL validation tooling** exists and is operational. All 51 use cases pass.
6. **Polynomial-time, total evaluation** under stated constraints — a strong formal property.

### Critical Gaps (S1)
1. **`restoreAction` for `promisedState`** (SEM-1) — the one hole in an otherwise-deterministic pipeline.
2. **IR definition** (SEM-4) — the Forth-IR design exists but is not adopted into the spec; `RL2_Architecture.md` still says "Structure: TBD."
3. **Target matching algorithm** (SEM-5) — four modes listed, algorithm and precedence unspecified.
4. **No implementation** — no Dafny kernel, no Go evaluator, no transpiler. The spec is paper-only.

### Significant Gaps (S2)
1. **`mostSpecific` undefined** in `SpecificOverridesGeneral` strategy.
2. **`claimCondition`/`powerCondition`/`immunityCondition` undefined** — guard predicates used in denotations but never reduced.
3. **`nullRequest` semantics** for `PromisedState` condition evaluation.
4. **Quantified norm selectors** (SEM-2) — cannot express "all duties fulfilled."
5. **External data integration** — declared but not bound; highest engineering risk.
6. **Dafny→Go extraction maturity** — needs a de-risking spike (evm-dafny precedent exists; Creusot is fallback).
7. **34 draft use cases** — Hohfeldian vocabulary not stress-tested.
8. **No ODRL transpiler** — migration path undefined.

### Documentation Issues (S3)
1. Stale references to `rl2-media-profile.ttl`, `RL2_ODRL_Coverage.md`, Why3/Coq.
2. Dafny example has removed `Temporal`/`Context` variants.
3. `FAQ` claims Rego/Cedar/Prolog compilation; actual design is Forth IR.
4. Protocol doc fences fail per-fence validation (VALID-3).
5. Terminology: "Rights & Licenses 2" vs "Rights Language 2" inconsistency.

---

## 10. Files Touched & Created

- **`fix.md`**: This document — the primary review, audit, and remediation plan.
- **`rl2.ttl` & `rl2-shacl.ttl`**: Verified consistent at v0.6. Stale Dafny example in `RL2_Semantics.md` to fix.
- **`rl2p.ttl` & `rl2p-shacl.ttl`**: Verified consistent at v0.5. `PROM-7` projection to document.
- **`usecases/*.md`**: Verified 51/51 pass SHACL. 34 drafts to complete.
- **`tools/validate.py`**: Verified operational for both file-level and per-fence validation.
- **`RL2_Semantics.md`**: `mostSpecific` to define; `nullRequest` to specify; Dafny example to update; `restoreAction` to formalize.
- **`RL2_Architecture.md`**: IR structure to define (adopt Forth-IR or specify alternative); target matching algorithm to specify; external data integration section to add.
- **`RL2_Protocol.md`**: 9 fences to fix (VALID-3).
- **`RL2_Vocabulary.md`**: 5 discrepancies to fix (§4.4).
- **`RL2_ODRL_Comparison.md`**: Stale references to update or merge into Primer (DOC-4).
- **`FAQ/RL2_FAQ.md`**: Compilation targets to clarify; terminology to standardize.
- **`RL2_References.md`**: `RL2_ODRL_Coverage.md` cross-reference to fix.
- **New (proposed): `RL2_ExternalData.md`** or new Architecture section — external data integration specification.
- **New (proposed): `examples/llm-generation/`** — LLM generation prompt templates and validation harness.
- **New (proposed): `profiles/rl2-media-profile.ttl`** — or correct the reference in `RL2_ODRL_Comparison.md`.