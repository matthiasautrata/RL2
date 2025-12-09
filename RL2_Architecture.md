# RL2 Architecture

This document describes the architectural design of RL2 — the evaluation pipeline, layer separation, and design rationale.

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

### Why Separation Matters

> "Derivation must be monotone and total. Resolution must be defeasible and ordered. Mixing them destroys both correctness and performance."

Benefits:
- Polynomial-time evaluation (derivation is bounded)
- Deterministic replay (no hidden state)
- Auditability (all matching norms visible before resolution)
- Verifiability (transformer can be formally verified)

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

---

## Expressive Characterization

RL2's expressive power:

```
RL2 ≈ LTL_F + Deontic(P, O, F) + Finite Obligation Automata
```

Where:
- `LTL_F` = Linear Temporal Logic with finite traces
- `Deontic(P, O, F)` = Permission, Obligation, Prohibition
- `Finite Obligation Automata` = Duty lifecycle (Pending → Active → Fulfilled/Violated)

### What RL2 Can Express

- Single-deadline obligations ✓
- Conditional activation ("duty activates when X") ✓
- Sequential dependencies ("A before B") ✓
- Dynamic policy applicability (events activate policies) ✓
- Compensatory obligations via Power/Liability ✓
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
| **RL2** | **LTL + Deontic + State** | **Linear time** |
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
- Mechanization path (ready for Why3/Lean/Coq)

---

## Design Goals

RL2 semantics are designed to be:

1. **Precise** — Every construct has clear formal meaning
2. **Modular** — Norms, conditions, roles, events are independent but composable
3. **Mechanizable** — Maps directly to Why3, Lean, Coq
4. **Standalone** — Self-contained, no external standard dependencies
5. **Operational** — Policies evolve through events and actions
6. **Analytically useful** — Supports reasoning about compliance and violations

---

## References

See **RL2_References.md** for complete citations.

Related specifications:
- rl2.ttl — Core ontology
- rl2p.ttl — Protocol ontology
- RL2_Semantics.md — Formal evaluation rules
- RL2_Protocol.md — Request/response formats
