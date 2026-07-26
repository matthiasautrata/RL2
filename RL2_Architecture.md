---
title: "RL2 Architecture"
subtitle: "Functional Model, Evaluation Pipeline, and Design Rationale"
version: "0.6"
status: "Draft"
date: 2026-07-24
---

# RL2 Architecture

This document describes the architectural design of RL2 — the functional interfaces, evaluation pipeline, layer separation, and design rationale.

For formal semantics, see **RL2_Semantics.md**. For protocol details, see **RL2_Protocol.md**.

---

## Evaluation Pipeline

RL2 follows an **I/O Logic + Transformer + Post-hoc Conflict Resolution** architecture:

```
① Context Materialization
   Env = mkEnv(Request, Σ, ContextAssertions)
        │
        ▼
② Derivation (Transformer)
   T : (Policy × Env) → NormativeAtoms*
   Produces: {permit(x), forbid(y), obligate(z)}
        │
        ▼
③ Normative Envelope (unresolved)
   Multiset of matching norms, possibly conflicting
        │
        ▼
④ Conflict Resolution
   R : NormativeAtoms* → Decision
   Strategy: ProhibitOverrides | PermitOverrides | SpecificOverridesGeneral
        │
        ▼
⑤ Protocol Wrapping
   Duties → Requirements (adds tracking metadata)
```

This pipeline **separates derivation from resolution** — the key architectural invariant.

For a given Case, the policy universe **U** is the set of policies in the generation identified by the case's `rl2p:policyGeneration`.

**Definition (Policy Universe):**

> U = { p | p ∈ Policy ∧ p.generation = currentGeneration }
>
> The Policy Universe is the complete set of policies in force at a given generation.

---

## Layer Separation

| Layer | Artifact | Responsibility |
|-------|----------|----------------|
| **Vocabulary** | rl2.ttl, rl2p.ttl | Define what things ARE |
| **Semantics** | RL2_Semantics.md | Define what evaluation MEANS (derivation rules) |
| **Protocol** | RL2_Protocol.md | Define how to EXCHANGE inputs/outputs |
| **Evaluator** | Implementation | Execute the pipeline, wrap outputs |

### What Belongs Where

| Concern | Layer |
|---------|-------|
| Norm types (Duty, Promise, Privilege) | Vocabulary |
| State structure (Σ) | Semantics |
| Condition evaluation | Semantics |
| Conflict resolution **strategies** | Semantics (defines valid strategies) |
| Conflict resolution **choice** | Evaluator (configuration) |
| Request/Response format | Protocol |
| Requirement lifecycle tracking | Protocol |
| Event indexing, Case management | Evaluator |

**Note on conflict resolution**: RL2 Semantics defines the *space* of valid conflict-resolution strategies (ProhibitOverrides, PermitOverrides, etc.) and their required properties. Individual evaluators *choose* a strategy as configuration. The `resolveDecision` function is parameterized by strategy — policies express norms and priorities; evaluators decide how to combine conflicting results.

---

## Derivation vs Resolution

### Derivation (Stage ②)

The transformer is a **pure function** over closed context:

- **Monotone**: Adding facts never removes conclusions
- **Total**: Always produces a result
- **Deterministic**: Same inputs → same outputs
- **No conflict handling**: Contradiction is data, not failure
- **No priority logic**: All matching norms are returned

**Constraint**: **Path-based resolution** is the normative baseline. Values are accessed via `resolutionPath` (e.g., `agent.department`, `asset.owner.organization`). `resolutionFunction` and `lookupExternal` are **controlled escape hatches** that MUST obey the same complexity constraints:

- No unbounded graph traversal or SPARQL-style joins
- O(1) or O(log n) per invocation
- No iteration over external graphs
- Synchronous or fail-fast (no blocking on external services)

### Resolution (Stage ④)

Conflict resolution is **procedural**, not logical:

- **Non-monotonic**: Priority can exclude norms
- **Strategy-based**: Evaluator configuration, not policy content
- **Defeasible**: Higher-priority norms defeat lower
- **P vs F conflicts**: Resolved by strategy (ProhibitOverrides, PermitOverrides)

**Key insight**: `P(a) ∧ F(a)` is not a logical contradiction — it's a conflict to be resolved procedurally.
`resolveDecision` is a parameterized algorithm (strategy + priorities); if these inputs do not disambiguate, the evaluator must return an explicit ambiguity/error instead of applying an implicit specificity heuristic.

### Why Separation Matters

> "Derivation must be monotone and total. Resolution must be defeasible and ordered. Mixing them destroys both correctness and performance."

Benefits:
- Polynomial-time evaluation (derivation is bounded)
- Deterministic replay (no hidden state)
- Auditability (all matching norms visible before resolution)
- Verifiability (transformer can be formally verified)

**Scope of formal guarantees:** Formal proofs (S1–S6 in RL2_Semantics.md) apply to derivation and state transitions. Resolution strategies are constrained by stated invariants but are not themselves subject to semantic completeness proofs — they are procedural algorithms parameterized by configuration.

---

## Conflict Resolution Strategies

The `resolveDecision` function implements several strategies:

| Strategy | Behavior |
|----------|----------|
| **ProhibitOverrides** | Any active prohibition → Deny |
| **PermitOverrides** | Any active privilege with no duties → Permit |
| **SpecificOverridesGeneral** | Most specific norm wins |

**rl2:priority** is resolution-layer, not derivation-layer:
- Orders among same-type norms (which prohibition's message? which privilege's duties?)
- Does NOT allow privileges to override prohibitions cross-type
- Could be used as pre-filter within strategies

---

## Protocol Wrapping (Stage ⑤)

The evaluator transforms semantic output to Protocol format:

```
Semantic Output          Protocol Output
─────────────────        ─────────────────
Decision                 rl2p:decision
DutySet                  rl2p:activeRequirements (wrapped as Requirements)
Σ' (updated state)       Persisted in Case
```

`rl2p:Requirement` adds tracking metadata not present in semantics:
- `sourcePolicy` — which policy created it
- `imposedTime` — when it was created
- `fulfilledByAction`, `fulfillmentEvidence` — completion tracking

This wrapping is **evaluator responsibility**, not semantic concern.

---

## Correspondence: Semantics ↔ Protocol

| Semantics Concept | Protocol Artifact |
|-------------------|-------------------|
| Request R = (a, x, s) | rl2p:Request |
| Env (environment) | Request + ContextAssertions |
| Σ (state) | Case history (reconstructed from ContextAssertions) |
| Σ.ObligationState | rl2p:requirementStatus |
| Decision | rl2p:EvaluationResult.decision |
| DutySet | rl2p:activeRequirements |

### Hohfeldian Mapping

| Norm | Runtime Meaning | Protocol Artifact |
|------|-----------------|-------------------|
| Duty | "Must Do" | Requirement (sourceNorm → Duty) |
| Promise | "Must Do" (Voluntary) | Requirement (sourceNorm → Promise) |
| Claim | "Owed To" | Requirement (with counterparty) |
| Privilege | "Can Do" | Decision = Permit |
| Prohibition | "Cannot Do" | Decision = Deny |
| Power | "Can Change" | Decision = Permit (state change action) |
| Immunity | "Cannot Be Changed" | Decision = Deny (state change action) |

### State Ownership and Scope

The evaluation state Σ has specific ownership and lifecycle semantics:

- **Owned by the evaluator** — Σ is managed by the policy engine, not by external systems
- **Scoped per Case** — Each Case maintains its own state; there is no global shared state across Cases
- **Persisted across evaluations** — Within a Case, state persists across re-evaluations (e.g., duty fulfillment tracking)
- **Reconstructible from history** — Σ can be reconstructed from the Case's ContextAssertion history (event sourcing)
- **Not omniscient** — Σ contains only facts explicitly asserted; the evaluator does not have access to external state unless provided via ContextAssertions

This scoping ensures evaluations are reproducible and auditable without requiring global coordination.

---

## Functional Model

This section specifies the **functional interfaces** for RL2 policy compilation and evaluation — what functions exist, their signatures, and how they compose. Implementation is opaque; only contracts and data flows are specified.

### Overview

RL2 processing divides into two phases:

| Phase | Functions | Artifacts |
|-------|-----------|-----------|
| **Compile-time** | `compile` | IR, ContextManifest, TargetIndex |
| **Runtime** | `lookup`, `manifest`, `resolve`, `evaluate` | Decision, Requirements |

```
                    Compile-Time
                    ════════════
                         │
    Policy*              │
       │                 │
       ▼                 │
  ┌─────────┐            │
  │ compile │            │
  └─────────┘            │
       │                 │
       ├──────────────────┼──────────────────┐
       │                 │                   │
       ▼                 ▼                   ▼
      IR          ContextManifest       TargetIndex
       │                 │                   │
═══════╪═════════════════╪═══════════════════╪══════════
       │                 │                   │
       │            Runtime                  │
       │            ═══════                  │
       │                 │                   │
       │                 │         Request   │
       │                 │            │      │
       │                 │            ▼      │
       │                 │       ┌────────┐  │
       │                 │       │ lookup │◀─┘
       │                 │       └────────┘
       │                 │            │
       │                 │            ▼
       │                 │       PolicyRef*
       │                 │            │
       │                 ▼            │
       │            ┌──────────┐      │
       │            │ manifest │◀─────┘
       │            └──────────┘
       │                 │
       │                 ▼
       │            OperandSpec*
       │                 │
       │                 ▼
       │            ┌─────────┐
       │            │ resolve │◀──── Sources
       │            └─────────┘
       │                 │
       │                 ├─────────────┐
       │                 │             │
       │                 ▼             ▼
       │             Context       Missing*
       │                 │             │
       │                 │      (if non-empty:
       │                 │       return to requester)
       │                 │
       ▼                 ▼
  ┌──────────────────────────┐
  │        evaluate          │
  └──────────────────────────┘
             │
             ▼
    (Decision, Requirements)
```

---

## Compile-Time Functions

### compile

```
compile : Policy* → (IR, ContextManifest, TargetIndex)
```

**Input:**
- `Policy*` — Set of RL2 policies (RDF/Turtle)

**Output:**
- `IR` — Intermediate representation for evaluation
- `ContextManifest` — Operands required per policy/norm
- `TargetIndex` — Mapping from targets to applicable policies

**Contract:**
- Semantics-preserving: `evaluate(IR, ...) ≡ eval(Policy*, ...)`
- Total: Always produces output for valid policies
- Deterministic: Same policies → same artifacts

**Implementation:** Opaque.

---

## Canonical Form

RL2 enforces a **canonical-form invariant**: *for any normative proposition the
language can express, there is exactly one valid RDF shape that expresses it.*
Two graphs that differ structurally must differ semantically; where they would
not, one shape is canonical and the alternatives are rejected (by SHACL) or
rewritten (by compile-time normalization).

This is the property that makes RL2 suited to automated generation and
verification. A generator has one target shape per intent — no authoring-
convenience variation to learn or normalize. Semantic equivalence of two policies
reduces to graph comparison after normalization, with no bespoke normalizer (the
place ODRL-style flexibility hides bugs).

Instances in the current vocabulary:

- **Promise content** — exactly one of `rl2:promisedAction` / `rl2:promisedState`
  / `rl2:promisedDuty`, not a polymorphic union. Enforced by `rl2:PromiseShape`.
- **Promise vs Duty by container** — a voluntary commitment has one shape
  (`rl2:Promise`, in an Offer) and its accepted, enforceable form has one shape
  (`rl2:Duty` + correlative `rl2:Claim`, in an Agreement). Acceptance *crystallizes*
  the former into the latter; the two never coexist for one commitment, so there is
  no dual-source encoding. A Promise clause in an Agreement is rejected by SHACL
  (`AgreementShape`). See *Crystallization* in `RL2_Semantics.md`.
- **Claim roles** — the uniform `rl2:subject` / `rl2:counterparty`; there are no
  Claim-specific `claimHolder` / `claimAgainst` properties.
- **Negative duties** — expressed solely as `rl2:Prohibition`; there is no
  competing "Duty with a negated action" encoding.
- **Conditions** — authored at the narrowest scope they apply to (on the Norm
  when they gate a single norm). A policy-level condition conjoins with norm
  conditions and is pushed down during IR normalization, so the IR carries
  conditions only on norms.

Every new construct is checked against this invariant before it is added.

## Compile-Time Artifacts

### IR (Intermediate Representation)

Executable representation of compiled policies.

**Structure:** defined in **RL2_IR.md**. A two-lowering pipeline
`Turtle → normalized AST (outer IR) → condition bytecode (inner IR)`: only conditions become
a stack-machine executable, while the deontic layer stays a tree-walk over the AST. The AST
base element is `Clause` (Norm ⊔ Promise); the verified kernel is a pure
`evalIR : (CompiledPolicy, Request, Σ) → (Decision, DutySet, seq<Effect>)` (functional core +
effect shell). The semantics-preservation obligation is stated there as a normalization
theorem (outer) plus a VM-correctness lemma (inner) plus an effect-soundness lemma.

**Properties:**
- Closed-form: No external references requiring resolution at evaluation time
- Indexed: Efficient lookup by policy reference
- Semantics-preserving: Evaluation equivalence with source policies
- Canonical: policy-level conditions are pushed down into each norm's
  `effectiveCondition` = `And(P.condition, n.condition)`, so the IR holds
  conditions only on norms — one shape per proposition (see Canonical Form)

### ContextManifest

Declares which operands each policy/norm requires for evaluation.

```
ContextManifest : PolicyRef → NormRef → OperandSpec*
```

**OperandSpec:**

| Field | Description |
|-------|-------------|
| `operand` | The left operand (e.g., `ex:department`, `rl2:currentDateTime`) |
| `subject` | What it applies to: `agent`, `asset`, or `environment` |
| `required` | Whether evaluation can proceed without it |

**Purpose:** Enables pre-flight context discovery without parsing policies at runtime.

### TargetIndex

Maps targets to applicable policies.

```
TargetIndex : Target → PolicyRef*
```

**Target matching modes** (TBD — design must accommodate all):

| Mode | Request | Policy Target | Example |
|------|---------|---------------|---------|
| **Direct** | URI | Same URI | `ex:LoanPortfolio` → policy targets `ex:LoanPortfolio` |
| **Classification** | URI | Classification tag | `ex:dataset123` → policy targets `tag:sensitive` |
| **Sub-asset** | URI + attribute | Attribute classification | `ex:dataset123.ssn` → policy targets `tag:PII` |
| **Subsumption** | URI with class | Superclass policy | `tag:top-secret` asset → policy targets `tag:sensitive` (if sensitive ⊇ top-secret) |

**Subsumption reasoning:** decided — a **declared hierarchy** traversed by bounded graph
reachability over `rl2:includedIn*` (closed-world; no OWL inference), materialized as a static
subsumption index and matched at eval-time. See **RL2_IR.md** §Subsumption. The
target-matching *algorithm* that applies it across the four modes is SEM-5.

**Design constraint:** The `lookup` function must handle all modes; index structure is implementation-dependent.

---

## Runtime Functions

### lookup

```
lookup : (TargetIndex, Target) → PolicyRef*
```

**Input:**
- `TargetIndex` — Compiled target index
- `Target` — Requested target (URI, classification, or attribute path)

**Output:**
- `PolicyRef*` — References to applicable policies

**Contract:**
- **Complete**: Returns all policies that could apply to the target
- **Sound**: Only returns policies whose target constraints are satisfied
- **Mode-agnostic**: Handles direct, classification, sub-asset, and subsumption matching

**Implementation:** Opaque.

### manifest

```
manifest : (ContextManifest, PolicyRef*) → OperandSpec*
```

**Input:**
- `ContextManifest` — Compiled context requirements
- `PolicyRef*` — Applicable policies (from `lookup`)

**Output:**
- `OperandSpec*` — Union of operands required by all applicable policies

**Contract:**
- Returns minimal sufficient set (no duplicates)
- Aggregates across all norms in all applicable policies

**Implementation:** Opaque.

### resolve

```
resolve : (OperandSpec*, Request, Sources) → (Context, Missing*)
```

**Input:**
- `OperandSpec*` — Required operands (from `manifest`)
- `Request` — The evaluation request (agent, action, target, supplied context)
- `Sources` — External context sources (identity provider, asset catalog, etc.)

**Output:**
- `Context` — Resolved operand values
- `Missing*` — Operands that could not be resolved

**Contract:**
- **Best-effort**: Resolves what it can from available sources
- **Transparent**: Reports what's missing (not silent failure)
- **Idempotent**: Same inputs → same outputs

**Interaction modes** (TBD):

| Mode | Description |
|------|-------------|
| **In-band** | Evaluator calls external sources directly |
| **Out-of-band** | Requester supplies all context with request |
| **Hybrid** | Evaluator resolves some; requester supplies rest |

**Implementation:** Opaque.

### evaluate

```
evaluate : (IR, PolicyRef*, Context) → (Decision, Requirements)
```

**Input:**
- `IR` — Compiled policy representation
- `PolicyRef*` — Applicable policies (from `lookup`)
- `Context` — Resolved operand values (from `resolve`)

**Output:**
- `Decision` — One of: `Permit`, `PermitWithObligations`, `Deny`, `Indeterminate`, `NotApplicable`
- `Requirements` — Active duties/promises/claims (if decision permits with obligations)

**Contract:**
- **Deterministic**: Same inputs → same outputs
- **Total**: Always produces a decision
- **Semantics-preserving**: Equivalent to RL2_Semantics.md evaluation rules

**Precondition:** `Context` should cover all operands from `manifest`. If incomplete:
- Return `Indeterminate` with `Missing*` indicating what's needed, OR
- Evaluate with available context (some conditions may be indeterminate)

TBD: Specify normative behavior for incomplete context.

**Implementation:** Executes the evaluation pipeline (§Evaluation Pipeline). Opaque beyond that.

---

## Request Processing

### Interaction Sequence

```
Requester                              Evaluator
─────────                              ─────────
    │                                      │
    │  Request                             │
    │  (target, action, agent, context?)   │
    ├─────────────────────────────────────▶│
    │                                      │
    │                             lookup(target)
    │                                      │
    │                             manifest(policies)
    │                                      │
    │                             resolve(operands, request, sources)
    │                                      │
    │         ┌────────────────────────────┤
    │         │ if Missing* non-empty      │
    │         ▼                            │
    │  NeedContext(Missing*)               │
    │◀──────────────────────────────────────┤
    │                                      │
    │  SupplyContext(values)               │
    ├─────────────────────────────────────▶│
    │                                      │
    │                             evaluate(IR, policies, context)
    │                                      │
    │  Result(Decision, Requirements)      │
    │◀──────────────────────────────────────┤
    │                                      │
```

### Interaction Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Single-shot** | Requester supplies all context upfront; evaluator returns decision or `Indeterminate` | Batch processing, known context |
| **Iterative** | Evaluator returns `NeedContext`; requester supplies; repeat until decision | Interactive flows, progressive disclosure |
| **Pre-flight** | Requester calls `manifest` first to discover requirements before full request | UI pre-population, access previews |

TBD: Specify which modes are normative vs optional.

### Protocol Mapping

The functional model maps to Protocol artifacts:

| Function | Protocol Input | Protocol Output |
|----------|----------------|-----------------|
| `lookup` | `rl2p:Request.requestedAsset` | (internal) |
| `manifest` | (internal) | `rl2p:NeedContext` (TBD) |
| `resolve` | `rl2p:ContextAssertion*` | (internal) |
| `evaluate` | (internal) | `rl2p:EvaluationResult` |

---

## Composition Invariants

The functions compose with these guarantees:

**1. Lookup Completeness**

```
∀ target, policy ∈ Policy* :
  applies(policy, target) ⟹ policy ∈ lookup(TargetIndex, target)
```

All policies that could affect the target are returned.

**2. Manifest Sufficiency**

```
∀ policies, context :
  manifest(policies) ⊆ dom(context) ⟹ evaluate returns definite Decision
```

If all required operands are provided, evaluation does not return `Indeterminate` due to missing context.

**3. Evaluation Equivalence**

```
evaluate(compile(P).IR, lookup(...), resolve(...)) ≡ semanticEval(P, ...)
```

Compiled evaluation is equivalent to direct semantic evaluation per RL2_Semantics.md.

**4. Determinism**

```
identical normalized inputs and configuration (IR, request, Σ, resolved context)
  ⟹ identical result, effects, diagnostics, and next state
```

This is *same-input determinism*, not injectivity. Distinct contexts routinely yield the
same decision, so the converse `evaluate(…, ctx₁) = evaluate(…, ctx₂) ⟹ ctx₁ = ctx₂` does
**not** hold and is not claimed. The related **canonicalization** property —
`compile(P₁) = compile(P₂) ⟺ P₁ ≡ P₂` (up to blank-node renaming) — is a property of
*compilation* (the Band-0 canonical-form thesis), distinct from determinism; the source/IR
equivalence `evaluate(compile(P).IR, …) ≡ semanticEval(P, …)` is stated as item 3 above.

---

## Open Design Questions

| Topic | Status | Notes |
|-------|--------|-------|
| IR structure | **Defined** — RL2_IR.md | Two-lowering hybrid (normalized AST + condition bytecode); functional core + effect shell |
| Target matching algorithm | TBD (SEM-5) | Must handle direct, classification, sub-asset, subsumption; index shape fixed in RL2_IR.md |
| Subsumption reasoning | **Decided** — RL2_IR.md §Subsumption | Declared hierarchy via `includedIn*`, bounded reachability (no OWL inference), eval-time match; matching algorithm → SEM-5 |
| Attribute-level policies | TBD | How sub-asset targets are represented and matched |
| Context resolution mode | TBD | In-band vs out-of-band vs hybrid |
| Incomplete context behavior | TBD | `Indeterminate` vs partial evaluation |
| Pre-flight API | TBD | Whether `manifest` is exposed to requesters |
| NeedContext protocol | TBD | How missing context is communicated |

---

## Expressive Characterization

RL2's current expressive model is a **guarded finite-state transition system**: conditions are
guards evaluated over a state snapshot (comparison over resolved values plus a current-time
comparison), and duty/promise lifecycles are finite obligation automata. Full finite-trace
temporal logic is a **design aspiration, not an established equivalence** — the current syntax
defines no trace-satisfaction relation, so the characterization below is a design goal, not a
proved result:

```
RL2 ≈ LTL_F + Deontic(P, O, F) + Finite Obligation Automata      [design goal, not yet proved]
```

Where:
- `LTL_F` = Linear Temporal Logic with finite traces (target, once a trace semantics is specified)
- `Deontic(P, O, F)` = Permission, Obligation, Prohibition
- `Finite Obligation Automata` = Duty lifecycle (Pending → Active → Fulfilled/Violated)

### What RL2 Can Express

- Single-deadline obligations ✔
- Conditional activation ("duty activates when X") ✔
- Sequential dependencies ("A before B") ✔
- Dynamic policy applicability (events activate policies) ✔
- Compensatory obligations via Power/Liability ✔
- Contrary-to-duty ("if violated, then Y") — partial via sanctions

### Known Limitations

- Repeating/periodic obligations ("every month")
- Quorum approvals ("any 2 of 5")
- Nested temporal modalities ("eventually always X")

### Comparison

| Language | Logic | Temporal Model |
|----------|-------|----------------|
| Simple ACLs | Propositional | None |
| XACML | First-order attributes | Point-in-time |
| ODRL 2.2 | Deontic (O, P, F) | Implicit |
| **RL2** | **Guarded FSM + Deontic + State** (LTL is a design goal) | **Snapshot + current-time** |
| Full temporal deontic | CTL* + Deontic | Branching |

RL2 occupies a practical sweet spot: more expressive than ODRL, with explicit operational semantics, while avoiding CTL complexity.

---

## Relationship to Prior Work

RL2 builds on prior ODRL formalization:

| Work | Contribution | RL2 Extension |
|------|--------------|---------------|
| Pucella-Weissman 2006 | First formal semantics | Adds operational semantics |
| Steyskal-Polleres 2015 | Action dependencies | Integrated into conditions |
| Fornara-Colombetti 2017 | State machines for obligations | Generalized to full calculus |
| W3C ODRL Formal Semantics | Evaluator spec | More precise denotations |

Gaps addressed:
- Unified semantics (prior work separated P, F, O)
- Implementation-independent (not tied to Jena)
- Hohfeldian coverage (Claims, Powers, Immunities)
- Mechanization path (Dafny with Go extraction; other proof assistants for optional validation)

---

## Design Goals

RL2 semantics are designed to be:

1. **Precise** — Every construct has clear formal meaning
2. **Modular** — Norms, conditions, roles, events are independent but composable
3. **Mechanizable** — Maps directly to Dafny; other proof assistants are optional cross-checks
4. **Standalone** — Self-contained, no external standard dependencies
5. **Operational** — Policies evolve through events and actions
6. **Analytically useful** — Supports reasoning about compliance and violations

**Normative implementation:** The reference evaluator is implemented and verified in Dafny, with extracted Go constituting the normative execution model. Alternative implementations must produce equivalent results for all valid inputs.

---

## Enforcement Boundary

RL2 is a **decision layer**, not an **enforcement layer**.

```
┌──────────────────────────────────────────────────────────┐
│ RL2 Scope                                                │
│  • Policy authoring (RDF/Turtle)                         │
│  • Semantic evaluation (Permit/Deny/PermitWithDuties)    │
│  • Duty lifecycle tracking (Pending→Active→Fulfilled)    │
│  • Case lifecycle (Protocol)                             │
│  • Audit trail (ContextAssertions, fulfillment evidence) │
└──────────────────────────────────────────────────────────┘
                           │
                           │ Handoff: approved Case
                           ▼
┌──────────────────────────────────────────────────────────┐
│ Enforcement Layer (NOT RL2)                              │
│  • Rego: row-level filtering, attribute masking          │
│  • Cedar: fine-grained resource authorization            │
│  • Immuta: data platform policy execution                │
│  • Custom: application-specific enforcement              │
└──────────────────────────────────────────────────────────┘
```

### What RL2 Provides to Enforcement

When evaluation completes, the Protocol's `rl2p:Case` serves as the handoff artifact:

| Artifact | Purpose |
|----------|---------|
| `rl2p:decision` | What was decided (Permit, Deny, PermitWithDuties) |
| `rl2p:activeRequirements` | Duties to track (if any) |
| `rl2p:matchedPolicies` | Which policies applied |
| `rl2p:matchedNorms` | Which norms matched |
| `rl2p:evaluationHistory` | Audit trail of all evaluations |
| `rl2p:expirationTime` | When the grant expires |

### What RL2 Does NOT Prescribe

RL2 does not prescribe enforcement mechanisms:

* **Row-level security** — Enforcement systems translate `Permit` + asset scope into database predicates
* **Attribute masking** — Enforcement systems decide which fields to redact
* **Rate limiting** — Enforcement systems implement counters and throttling
* **Session management** — Enforcement systems manage tokens and credentials

Enforcement systems translate RL2 decisions into their native constructs. RL2 is responsible for *what* is decided and *why*, not *how* it is enforced.

### The Protocol as Interoperability Boundary

The `rl2p` Protocol is the interoperability contract:

* **Input**: `rl2p:Request` + `rl2p:ContextAssertion`
* **Output**: `rl2p:EvaluationResult` + `rl2p:Case`

Any system that can produce Requests and consume Cases can integrate with RL2 evaluators. The Protocol is serialization-flexible (RDF/Turtle, JSON-LD) and implementation-agnostic.

**One-way data flow:** Protocol artifacts (Requirements, Cases, EvaluationResults) are outputs only — they do not feed back into derivation. The evaluator reads policies and context; it writes protocol artifacts. This prevents circular dependencies and ensures derivation remains a pure function of policy and context.

### Compilation and IR

The Functional Model (§Functional Model) defines `compile` as producing an **Intermediate Representation (IR)** along with auxiliary artifacts (`ContextManifest`, `TargetIndex`). This separation enables:

* **Pre-computed policy indexing** — Target matching without runtime policy parsing
* **Pre-computed context requirements** — Know what's needed before evaluation
* **Optimized evaluation** — IR can be tuned for performance

IR structure is defined in **RL2_IR.md**. The Protocol remains the external interoperability boundary; IR is internal to evaluator implementations.

---

## References

See **RL2_References.md** for complete citations.

Related specifications:
- rl2.ttl — Core ontology
- rl2p.ttl — Protocol ontology
- RL2_Semantics.md — Formal evaluation rules
- RL2_Protocol.md — Request/response formats
