---
title: "RL2 Intermediate Representation"
subtitle: "Compilation Target, Construct Correspondence, and Equivalence Obligation"
version: "0.6"
status: "Draft"
date: 2026-07-25
---

# RL2 Intermediate Representation

This document defines the RL2 **intermediate representation (IR)** — the target of
`compile : Policy* → IR` — and the equivalence obligation that ties IR evaluation back to
the denotational semantics. It closes the "IR = TBD" gap in **RL2_Architecture.md** and
supplies the object every downstream verification step reasons about.

This is a **design specification**: it fixes the datatypes, the opcode set, the construct
correspondence, and the theorem statements. It deliberately contains **no Dafny proofs** —
those belong to the implementation band (IMPL-1/2). For the formal semantics this IR refines,
see **RL2_Semantics.md**; for the architectural pipeline, **RL2_Architecture.md**; the
stack-VM design rationale is **design-forth-ir.md** (refined and narrowed by this document).

---

## 1. Purpose and Scope

`compile : Policy* → IR` was left undefined, which blocked the evaluator implementation and
the compile-time-canonicalization story (SEM-4). This document defines the IR so that:

- **SEM-5** (target matching) has a concrete `targetIndex` to specify an algorithm over;
- **IMPL-1/2** (Dafny→Go) have a concrete compilation target and proof obligations;
- the "one canonical RDF shape per proposition" invariant (Band 0, CANON) has a place to be
  *enforced* — normalization is the compiler's job, not a runtime guess.

**In scope:** the IR datatypes (outer AST + inner condition bytecode), the eval-time
interaction model, the state/effect model, the construct correspondence table, and the
equivalence obligation split into named lemmas.

**Out of scope:** Dafny proofs; bytecode wire format, dictionary layout, and debugger design
(IMPL — see §11); the target-matching *algorithm* itself (SEM-5, which consumes the
`targetIndex` defined here).

---

## 2. Pipeline

RL2 compilation is a standard two-lowering pipeline, named in ordinary compiler terms:

```
  Turtle (surface syntax)
        │  compile — normalize + index      (Band 0 canonical form makes this near-mechanical)
        ▼
  Normalized AST  ── the "outer IR"          (norms + promises as structured data)
        │  lower — conditions only
        ▼
  Condition bytecode ── the "inner IR"       (the only part that becomes an "executable")
```

Only **conditions** are lowered to an executable (a stack machine). The **deontic layer**
— which clauses match, which win, what the decision is — stays a tree-walk over the AST.
This is the central design decision of the RL2 IR, and everything below follows from it.

Two orthogonal structural commitments frame the rest of this document:

- **Derive-then-resolve (I/O logic).** Evaluation is two phases: a *monotone* derivation that
  collects a normative envelope, then a *non-monotone* resolution that applies conflict
  strategy and priority (§7, §9; RL2_Semantics.md §Normative Derivation).
- **Functional core + effect shell.** The verified kernel is a pure total function that
  returns a decision plus a list of *effect descriptions*; an unverified shell applies them
  to state (§7).

```
   ┌──────────────────────────── verified kernel (pure) ────────────────────────────┐
   │  evalIR : (CompiledPolicy, Request, Σ) → (Decision, DutySet, seq<Effect>)       │
   │      ① derive  →  ② resolve  →  emit (Decision, DutySet) + effect descriptions  │
   └────────────────────────────────────────────────────────────────────────────────┘
                                        │ seq<Effect>
                                        ▼
                    shell (trivial):  Σ' = applyEffects(Σ, effects)
```

---

## 3. Construct Correspondence Table

The equivalence obligation (§9) is proven by **structural induction over the language
constructs**, and this table *is* the induction skeleton. Every construct lines up across
three columns — **syntax** (canonical RDF), **semantics** (`RL2_Semantics.md` denotation),
**outer-AST constructor** — plus, for conditions only, a **bytecode lowering**. One row is
one case of the induction. A construct present in one column but missing from another is a
proof hole: this is exactly the shape of the PROM-1 defect (a `Norm`-only clause range with
no `Promise` correspondent), which is why building this table is also a corpus audit.

**Clause is the base element — not Norm.** An Offer exists for its promises, so the base
cases include both `Norm` leaves *and* `Promise` leaves.

### 3.1 Clauses (norms and promises)

| Syntax (canonical RDF) | Semantics (§ref) | Outer-AST ctor |
|---|---|---|
| `rl2:Privilege [subject; action; object; condition?]` | Norm Denotations §684; `permit(a,x,s)` §1227 | `NormEntry(Privilege(a,x,s), effCond)` |
| `rl2:Duty [subject; action; object; condition?]` | §684; Duty SM §960–§1004; `obligate(d)` §1229 | `NormEntry(Duty(a,x,s), effCond)` |
| `rl2:Prohibition [subject; prohibitedAction; object; condition?]` | §684; `forbid(a,x,s)` §1228 | `NormEntry(Prohibition(a,x,s), effCond)` |
| `rl2:Claim [subject; counterparty; correlativeTo]` | Claim Denotation §748 | `NormEntry(Claim(subj,cpty,corr), …)` |
| `rl2:Power / Liability / Immunity [subject; affectsNorm/exposedTo/immuneFrom]` | §767 / §793 / §805 | `NormEntry(Power/Liability/Immunity(a,n), …)` |
| `rl2:Promise [promisor; promisee; promisedAction ∘ object]` | Promise SM §923–§1035; Crystallization §1036 | `PromiseEntry(p, q, PromisedAction(x,o), effCond)` |
| `rl2:Promise [promisor; promisee; promisedState]` | §923–§1035; §1036 | `PromiseEntry(p, q, PromisedState(c), effCond)` |
| `rl2:Promise [promisor; promisee; promisedDuty]` | §923–§1035; §1036 | `PromiseEntry(p, q, PromisedDuty(d), effCond)` |

> **Correspondence gap flagged (PROM-1 residue).** The semantics abstract syntax still
> declares `Policy ::= { clauses : Norm* }` (RL2_Semantics.md §Policies), predating the
> ontology's `rl2:Clause` (Norm ⊔ Promise) added in PROM-1. This IR takes the *ontology* as
> authoritative: a clause is a `Clause`. The one-line `Norm* → Clause*` alignment of the
> abstract syntax is a small PROM-1 follow-up (see issues.md), not a change of meaning.

### 3.2 Conditions (base and inductive cases, with bytecode lowering)

| Syntax (canonical RDF) | Semantics (§ref) | Outer-AST ctor | Condition lowering (inner IR) |
|---|---|---|---|
| `rl2:AtomicConstraint [leftOperand; operator; rightOperand \| rightOperandRef; targetNorm?]` | ⟦AtomicConstraint⟧ §288 | `Atomic(left, op, right, targetNorm?)` | `RESOLVE left; PUSH right; ⟨op⟩` |
| `rl2:LogicalConstraint [and (…operands)]` | ⟦And⟧ §301 | `And(seq<Cond>)` | lower each; fold `AND` |
| `rl2:LogicalConstraint [or (…operands)]` | ⟦Or⟧ §302 | `Or(seq<Cond>)` | lower each; fold `OR` |
| `rl2:LogicalConstraint [xone (…operands)]` | ⟦Xone⟧ §304 | `Xone(seq<Cond>)` | lower each; `XONE` reducer |
| `rl2:LogicalConstraint [not operand]` | ⟦Not⟧ §303 | `Not(Cond)` | lower; `NOT` |
| `rl2:EventConstraint [expectsEvent]` | ⟦EventConstraint⟧ §311 | `EventCond(ev)` | **AST-layer** (queries Σ.Events, not pure env) — no bytecode |

`AtomicConstraint` and each leaf clause are the **base cases**; `LogicalConstraint` and
conditional/nested clauses are the **inductive cases**. `EventConstraint` and any
`targetNorm`-parameterized state query read Σ, so they are evaluated in the AST tree-walk via
the subsumption-aware `performed(...)` helper (§320), never inside the pure condition VM.

### 3.3 Reading the table backwards

Right-to-left, the table is the **IR → source inverse map**: every AST node and every emitted
bytecode carries the identity of the RDF construct it came from. Error reporting ("policy X,
clause Y") is therefore a table lookup, not a separate mechanism — this answers Open Question
#3 of design-forth-ir.md (mapping VM errors back to source) for free.

---

## 4. Outer AST (the normalized policy)

The outer IR is structured data, mirroring the ontology's `rl2:Clause` split. It is **not**
bytecode: `resolveDecision` and clause matching pattern-match directly on these datatypes.

```dafny
datatype CompiledPolicy = CompiledPolicy(
  clauses          : seq<Clause>,
  targetIndex      : map<Target, set<int>>,      // Target → indices into clauses (SEM-5 consumes)
  subsumptionIndex : map<Action, set<Action>>,   // includedIn* downward closure — STATIC (§8)
  conflictStrategy : Strategy,                    // evaluator config (RL2_Semantics.md §Conflict Resolution)
  kind             : PolicyKind )                 // Offer | Agreement | Set | Privacy | Assertion

datatype Clause = NormEntry(norm: Norm, effCond: Condition)
                | PromiseEntry(promisor: Agent, promisee: Agent,
                               content: PromiseContent, effCond: Condition)

datatype PromiseContent = PromisedAction(action: Action, object: Asset)
                        | PromisedState(cond: Condition)
                        | PromisedDuty(duty: Norm)      // the referenced Duty (suretyship)
```

Notes:

- **`effCond` carries the CANON-1 push-down.** The compiler computes
  `effCond = And(policyCondition, clauseCondition)` (RL2_Semantics.md §Policies) so the
  evaluator never re-derives policy-level activation. This is a *normalization*, and its
  decision-preservation is part of the equivalence obligation (§9a).
- **No `matchesAction` field.** Action/purpose matching is *eval-time* (§8): the request's
  chosen value is unknown at compile time. The compiler precomputes the `subsumptionIndex`;
  the match is a membership test at eval-time.
- **`kind` encodes the Offer/Agreement well-formedness split.** Only `kind = Offer` admits a
  `PromiseEntry` clause; `Agreement`, `Set`, `Privacy`, `Assertion` reject it. This mirrors
  the SHACL constraints added in PROM-1 (`AgreementShape` etc. carry `sh:not [ sh:class
  rl2:Promise ]`). The compiler rejects a Promise in a non-Offer at compile time — the IR
  cannot represent an ill-formed policy.

---

## 5. Inner IR (condition bytecode)

Conditions compile to a small stack machine — the verifiable subset of Forth from
design-forth-ir.md, **scoped to pure boolean evaluation**. The `EMIT-PERMIT/FORBID/
OBLIGATION` opcodes of the original sketch are **removed**: emission is derivation (§7), a set
operation over the envelope, not a stack effect. What remains is ~30 opcodes with no side
effects and no external writes.

```dafny
datatype Value = VBool(bool) | VInt(int) | VString(string)
               | VDate(int)  | VURI(string) | VBottom          // ⊥ = absent / eval failure

datatype Instr =
  // stack
  | IDup | IDrop | ISwap | IOver | IRot
  // logic
  | IAnd | IOr | INot | IXor
  // compare (mono + typed)
  | IEq | INeq | ILt | ILte | IGt | IGte
  | ISEq | IDateLte | IURIEq
  // literals
  | ILitBool(bool) | ILitInt(int) | ILitString(string) | ILitDate(int) | ILitURI(string)
  // control
  | IIf(thn: seq<Instr>, els: seq<Instr>)
  // the single external-read opcode (§6)
  | IResolve(path: string)

datatype VM = VM(stack: seq<Value>, env: Env, fuel: nat)     // no output channel — pure boolean result
```

The intended invariants (proof obligations for IMPL, not proven here):

- **Termination:** `fuel` strictly decreases each `Step`; conditions are finite acyclic trees,
  so a `fuel` bound linear in tree size suffices.
- **Determinism:** `Step` is a function, not a relation.
- **Type/memory safety:** the stack never underflows on well-typed bytecode; `Xone` and typed
  comparators reject ill-typed operands to `VBottom` rather than getting stuck.

The single exported meaning is `EvalBytecode(prog, env) : Value` returning a `VBool` (or
`VBottom`). Its correctness statement is §9b.

---

## 6. Eval-time Interaction (reads)

All interaction with the outside world is **front-loaded and read-only**, so the kernel stays
pure.

- **`IResolve` is the sole external-read opcode.** It reads from a fully-populated `Env`; it
  never blocks on I/O. Its precondition is the `deref` grammar and sandbox of
  RL2_Semantics.md §Path Resolution Constraints (valid path, allowed root); the helper
  contract is §Helper Function Specifications.

```dafny
datatype Env = Env(request: Request, agent: AgentView, asset: AssetView,
                   state: StateView, context: ContextView)   // all pre-materialized values
```

- **ContextManifest.** The compiler statically extracts, from every condition tree, the exact
  set of paths the policy will `RESOLVE`. That set is the policy's *ContextManifest*. At
  runtime the host pre-materializes precisely those paths into `Env` before evaluation; a
  `RESOLVE` of an un-manifested path is a hard reject. Interaction is thus **bounded and
  declared** — no surprise fetch mid-evaluation.
- **Σ / event queries are AST-layer, not bytecode.** `EventConstraint` and
  `targetNorm`-parameterized state operands interrogate Σ/history and are evaluated in the
  tree-walk via `performed(...)`, keeping the VM's `Env` purely value-typed.

**Snapshot-consistency invariant.** Every read in a single evaluation observes Σ as of entry;
all effects (§7) apply atomically afterward. There is no intra-evaluation read-after-write.
This invariant is what permits effects to live *outside* the semantics of the language. It
holds for RL2 today: a decision evaluates against a fixed Σ snapshot, `Out` is a set-builder
over that snapshot, and `resolveDecision` is set-based rather than a stateful fold. A future
construct that had to observe another clause's effect *within the same evaluation* would
violate it and force a revisit — so it is stated, not assumed.

---

## 7. State and Effects (writes)

The denotational `Eval` already returns state as a *value* — `(Decision, State, DutySet)`
(RL2_Semantics.md §Evaluation Function Signature). The IR keeps that shape and only refactors
the returned `State` into a list of **effect descriptions**:

```dafny
evalIR : (CompiledPolicy, Request, Σ) → (Decision, DutySet, seq<Effect>)     // PURE, total
```

- **`(Decision, DutySet)` is the outward result: a verdict plus possible future duties.** The
  verdict is yes/no/indeterminate (`Permit | Deny | PermitWithObligations | NotApplicable |
  Indeterminate`); `DutySet` is the duties the request will owe. `PermitWithObligations` is
  the "yes, and you will owe these" case. For an **Offer**, the future duties simply *are* the
  crystallized duties (below).
- **`seq<Effect>` replaces the returned `State`.** Effects are *data*, not actions. Σ,
  Cases, and history are immutable values threaded through the kernel (the same way
  evm-dafny threads EVM storage). "Mutation" is a shell computing `Σ' = applyEffects(Σ, fx)`.

```dafny
datatype Effect =
  | TransitionDuty(duty: Norm, from: DutyState, to: DutyState)   // Duty SM; SEM-1 restoreAction wiring
  | CrystallizePromise(promisor: Agent, promisee: Agent,         // PROM-1 §1036 — orientation-carrying
                       content: PromiseContent)
  | GenerateRemedialDuty(source: Clause, remedy: Norm)           // PROM-6 §1082 (Remedial Generation)
  | CreateCase(case: CaseRef, generation: GenId)                 // Protocol; SEM-6 generation binding
  | ExercisePower(power: Norm, target: Norm)                     // Power exercise; SEM-8
  | AppendHistory(event: Event)
```

**Effects unify a large part of Bands 1–2.** Crystallization (PROM-1), remedial generation
(PROM-6), duty-state transitions and `restoreAction` (SEM-1), Case/generation binding
(SEM-6), and Power exercise (SEM-8) are all *effect kinds* in one closed algebra. The verified
kernel enumerates the legal effect vocabulary; the Duty/Promise state machines define which
transitions are legal; the shell just applies them.

### 7.1 Derive-then-resolve

Inside `evalIR`, the deontic computation is the I/O-logic two-phase (RL2_Semantics.md
§Normative Derivation):

```
evalIR(CP, R, Σ) =
    let env      = mkEnv(R, Σ)
    -- ① DERIVATION (monotone): collect the pre-resolution envelope
    let envelope = ⋃ { derive(c, env) | c ∈ CP.clauses, matches(c, R) }     -- Out, §1222
    -- ② effect collection (still monotone): duty transitions, crystallization on acceptance, …
    let effects  = deriveEffects(envelope, CP, env)
    -- ③ RESOLUTION (non-monotone): strategy + priority over the collected envelope
    let decision = resolveDecision(envelope, applyEffects(Σ, effects), CP.conflictStrategy)
    in (decision, duties(envelope), effects)
```

`derive` is a monotone per-clause fold; `resolveDecision` is where conflict/priority act, and
only there. Duties and crystallization pass through derivation into the output; resolution
decides only the verdict. Because derivation is monotone and order-independent, the outer
normalization theorem (§9a) inherits order-independence for free.

### 7.2 Crystallization carries orientation

**Acceptance of an Offer is the event that emits the crystallization effect set.** Each
`PromiseEntry` yields a `CrystallizePromise` effect; `applyEffects` realizes PROM-1's function

```
crystallize(Promise(p, q, κ)) = (D, C),   C = Claim(subject = q, counterparty = p, correlativeTo = D)
```

A promise **made** (promisor = offerer) and a promise **demanded** (promisor = acceptor) both
crystallize on acceptance but bind **opposite** parties. Carrying `promisor`/`promisee` on the
effect is what keeps the resulting `Duty` + correlative `Claim` correctly oriented — the
made-vs-demanded orientation is a named effect-soundness sub-lemma (§9c). The three content
forms map exactly as in RL2_Semantics.md §Crystallization (`PromisedAction` fully closed;
`PromisedState` maintenance-duty wiring → SEM-1; `PromisedDuty` suretyship remedy → PROM-5).

### 7.3 Effect coherence

`applyEffects` operates on the effect **set**, and must resolve or reject conflicting
transitions (e.g. one clause emits `TransitionDuty(d, _, Fulfilled)` while another emits
`TransitionDuty(d, _, Violated)`). This is the `resolveDecision` analogue for the write side —
a genuine proof obligation, not mechanical application (§9c). Snapshot-consistency (§6) makes
it well-posed: all effects derive from the same Σ snapshot, so the conflict set is fixed.

---

## 8. Subsumption (compile-time index, eval-time match)

Action/purpose subsumption is **eval-time**, because the chosen action/purpose is a
request-time value. The compiler precomputes only the *static* structure:

- **Compile-time:** build `subsumptionIndex : map<Action, set<Action>>` as the `includedIn*`
  downward closure of the hierarchy — for each norm-action `y`, the set `{ x | x includedIn* y
  }`. The hierarchy is fixed within a generation (SEM-6), so the closure is static. Cycles are
  a compile-time reject.
- **Eval-time:** `matches(c, R) := R.action ∈ subsumptionIndex[c.action]` — a membership test
  against the request. The same index mechanism serves any subsumable dimension (action,
  purpose, target asset); each gets its own closure map.

**Well-defined limitations** carry over verbatim from the resolved action-hierarchy decisions
(ACT-1/ACT-2) and EXPR-2: subsumption is *bounded graph reachability* over `includedIn*` — no
OWL reasoning, no counting/aggregation quantifier. The `subsumptionIndex` is a materialized
cache of the reachability relation, so eval-time match `≡ ∃ path in includedIn*`; this is a
caching-correctness lemma inside §9a, not a new semantic gap.

---

## 9. Equivalence Obligation

The IR is correct iff it reproduces the denotational semantics. Top-level statement (with Σ
threaded functionally and refactored into effects):

```
For all policy universes U, requests R, states Σ, contexts Ctx:

  Eval(U, R, Σ, Ctx) = (dec, Σ', duties)
    ≡
  let (dec', duties', fx) = evalIR(compile(U), R, Σ)
  in  dec = dec'  ∧  duties = duties'  ∧  Σ' = applyEffects(Σ, fx)
```

The proof is structural induction over the correspondence table (§3). It decomposes into three
named lemmas:

**(9a) Normalization theorem (outer IR).** `compile` is decision-preserving: pushing policy
conditions into `effCond`, precomputing `targetIndex`, and materializing `subsumptionIndex`
change *how* the answer is stored, not *what* is computed. Formally, `Out(U, Env)` (§1222)
equals the envelope collected by the AST tree-walk over `compile(U)`. Derivation's monotonicity
and order-independence (§7.1) make this a fold-equivalence; the subsumption-index caching
lemma (§8) is a sub-case.

**(9b) VM-correctness lemma (inner IR).** For every condition `c`,
`EvalBytecode(lower(c), env) = ⟦c⟧(env)` (RL2_Semantics.md §Conditions), together with the VM
invariants of §5 (termination, determinism, type/memory safety). Base case: `Atomic`.
Inductive cases: `And`/`Or`/`Xone`/`Not` by the fold in §3.2. (`EventConstraint` is discharged
in 9a, not here — it is AST-layer.)

**(9c) Effect-soundness lemma.** `applyEffects(Σ, fx)` reproduces the `Σ'` that `Eval` computes
via `updateDutyStates` (§1259) and the operational rules (§Duty Activation/Fulfillment/
Violation, §Crystallization, §Remedial Generation). Two sub-lemmas:
- **Made-vs-demanded orientation:** for either promise orientation, `CrystallizePromise`
  yields a `Duty` bound to the promisor and a correlative `Claim` bound to the promisee
  (§7.2).
- **Effect coherence:** `applyEffects` is well-defined on the emitted effect *set*, resolving
  or rejecting conflicting transitions (§7.3).

The split localizes the hard verification to 9b (the pure VM, where evm-dafny is direct
precedent) and keeps 9a/9c as structural refinements close to the denotational spec.

---

## 10. Compiler Trust Model

The **kernel** (`evalIR`, the VM, `applyEffects`) is the verified trusted base. The
**compiler** (`Turtle → AST`, `lower : Condition → bytecode`, index construction) starts
**tested, not verified**:

- **Differential testing** against the denotational reference on the 51-use-case corpus *and*
  on generated policies (the canonical-form thesis makes machine-generated policies the
  primary case, so they must be in the test set). This is the Cedar-spec model — reference
  semantics kept separate from the executable, reconciled by differential testing
  (`research/verification-toolchain-comparison.md` §Lean/Cedar).
- **CANON shrinks the trusted surface.** Because the RDF is already canonical (Band 0), `Turtle
  → AST` is a near-mechanical transliteration rather than an optimizing compiler; canonical
  form is also what makes syntax → AST a *function* (one shape → one node), which is the
  precondition that makes §9's base cases well-formed.
- **Stretch goal:** the `lower : Condition → bytecode` compiler is a syntax-directed recursion
  over a bounded acyclic datatype — small enough to *verify* in Dafny later. With the hybrid
  split it is far smaller than a full-pipeline compiler, so verifying it is a realistic
  follow-on, not a fantasy.

**Precedents** (`research/verification-toolchain-comparison.md`): Consensys **evm-dafny**
(verified stack VM in Dafny→Go, ~140 opcodes, runtime-error-freedom) is direct precedent for
the inner VM (9b) — RL2 needs fewer opcodes and no gas. **Cedar-spec** (policy language in
Lean, differential-tested) is precedent for the compiler-testing strategy.

---

## 11. Handoffs and Deferred Items

- **SEM-5 (target matching).** Consumes `CompiledPolicy.targetIndex`. This document fixes the
  index *shape* (`map<Target, set<int>>`); SEM-5 owns the *algorithm* and precedence (direct,
  classification, sub-asset, subsumption) and closed-world defaults.
- **SEM-1 / PROM-5.** `PromisedState` maintenance-duty ObligationState wiring (SEM-1) and
  `PromisedDuty` suretyship remedy (PROM-5) are the two behavioral wirings the crystallization
  *targets* (§7.2) hand off; the IR is well-defined regardless of how they resolve.
- **PROM-1 residue.** Align RL2_Semantics.md abstract syntax `clauses : Norm* → Clause*` (§3.1
  note) — a one-line follow-up.
- **IMPL (Band 4), out of scope here:** bytecode serialization format, dictionary/word
  indexing, error-report surfacing, and step/debug tooling (design-forth-ir.md §Open
  Questions). The de-risking spike (a handful of opcodes Dafny→Go) precedes committing to the
  full VM.

---

## References

- **RL2_Semantics.md** — denotational and operational semantics this IR refines (§Conditions,
  §Norm Denotations, §Crystallization, §Normative Derivation, §Big-Step Semantics).
- **RL2_Architecture.md** — evaluation pipeline and layer separation.
- **design-forth-ir.md** — stack-VM design rationale (refined here: VM scoped to conditions;
  `EMIT-*` removed).
- **research/verification-toolchain-comparison.md** — Dafny→Go decision; evm-dafny and
  Cedar-spec precedents.
- Makinson & van der Torre, *Input/Output Logics* — the derive-then-resolve foundation.
