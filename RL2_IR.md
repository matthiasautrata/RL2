---
title: "RL2 Intermediate Representation"
subtitle: "Compilation Target, Construct Correspondence, and Equivalence Obligation"
version: "0.7"
status: "Draft"
date: 2026-07-29
---

# RL2 Intermediate Representation

This document defines the RL2 **intermediate representation (IR)** — the target of
`compile : PolicyUniverse → CompiledUniverse` — and the equivalence obligation that ties IR evaluation back to
the denotational semantics. It closes the "IR = TBD" gap in **RL2_Architecture.md** and
supplies the object every downstream verification step reasons about.

This is a **design specification**: it fixes the datatypes, the opcode set, the construct
correspondence, and the theorem statements. It deliberately contains **no Dafny proofs** —
those belong to the implementation band (IMPL-1/2). For the formal semantics this IR refines,
see **RL2_Semantics.md**; for the architectural pipeline, **RL2_Architecture.md**; the
stack-VM design rationale is **research/design-forth-ir.md** (refined and narrowed by this document).

---

## 1. Purpose and Scope

`compile : PolicyUniverse → CompiledUniverse` was left undefined, which blocked the evaluator
implementation and the compile-time-canonicalization story (SEM-4). This document defines the
IR so that:

- **SEM-5** (target matching) has a concrete `targetIndex` to specify an algorithm over;
- **IMPL-1/2** (Dafny→Go) have a concrete compilation target and proof obligations;
- the "one canonical RDF shape per proposition" invariant (Band 0, CANON) has a place to be
  *enforced* — normalization is the compiler's job, not a runtime guess.

**I1/SEM-4 (WP-5).** `targetIndex` and conflict strategy are lifted to **universe scope**
(§4): a request may match clauses drawn from several policies at once, and RL2_Semantics.md's
`Out`/`Eval` already operate over a `PolicyUniverse`, not a single `Policy` — so the compiled
form must mirror that shape. `conflictStrategy` is not stored in compiled data at all; it is
supplied to `evalIR` at evaluation time, per S7's "evaluator configuration, not policy
vocabulary" ruling (RL2_Semantics.md §Normative Derivation, §Big-Step Semantics).

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

Two ratified implementation stances follow from these (recorded here so downstream work does
not relitigate them):

- **I2 — typed-AST evaluator first; bytecode is conditional.** The normative meaning is the
  tree-walk over the outer AST (§4). The inner condition **bytecode** (§5) is an
  *optimization/portability* path, not a prerequisite: implement and verify the typed-AST
  evaluator first, and adopt the stack-VM lowering only once a concrete benchmark or a
  cross-language portability requirement justifies the extra proof surface. Absent that
  evidence, a conforming implementation MAY evaluate conditions directly over the AST.
- **I3 — runtime stays solver-free; entailment/closure happen at ingestion.** No OWL reasoner,
  SAT/SMT solver, or fixpoint search runs during evaluation. All entailment and bounded
  closure — subsumption/`includedIn*` (§8), materialization (§6), hierarchy expansion — are
  computed **once at ingestion/compile time** and frozen into static indices; `evalIR` only
  reads pre-materialized values. This is what keeps the kernel a pure total function.

**AST↔bytecode boundary and evaluation order (I1/SEM-4 closure).** These are not open
questions; I2 already fixes the boundary (typed-AST evaluator is the normative one; bytecode
is an optional lowering of conditions only, never of the deontic layer), and §5's Kleene logic
already fixes evaluation order: short-circuit and error-observability are determined by the
three-valued algebra (`VBool(false) IAnd VBottom = VBool(false)`, etc.), not by the order a
compiler or VM happens to visit operands in. Both properties hold identically whether a
condition is evaluated as a tree-walk over the AST or as compiled bytecode — that equivalence
is exactly what the VM-correctness lemma (§9b) proves. Nothing further needs defining here.

```
   ┌────────────────────────────── verified kernel (pure) ───────────────────────────────┐
   │  evalIR : (CompiledUniverse, Request, Σ, Ctx, Strategy) → (Decision, DutySet, seq<Effect>) │
   │      ① derive  →  ② resolve  →  emit (Decision, DutySet) + effect descriptions        │
   └───────────────────────────────────────────────────────────────────────────────────────┘
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

> **Correspondence note (PROM-1 residue, now aligned).** The semantics abstract syntax
> previously declared `Policy ::= { clauses : Norm* }`, predating the ontology's `rl2:Clause`
> (Norm ⊔ Promise) added in PROM-1. It has been aligned to `clauses : Clause*` with a
> `Clause ::= Norm | Promise` production (RL2_Semantics.md §Policies), matching this IR and the
> ontology — no change of meaning (the type-filtered comprehensions in `Out`/`Eval` already
> exclude Promise clauses from norm matching; promises participate only via crystallization).

### 3.2 Conditions (base and inductive cases, with bytecode lowering)

| Syntax (canonical RDF) | Semantics (§ref) | Outer-AST ctor | Condition lowering (inner IR) |
|---|---|---|---|
| `rl2:AtomicConstraint [leftOperand; operator ∈ {eq,neq,lt,lte,gt,gte}; rightOperand \| rightOperandRef; targetNorm?]` | ⟦AtomicConstraint⟧ §288 | `Atomic(left, op, right, targetNorm?)` | `RESOLVE left; PUSH right; ⟨op⟩` |
| `rl2:AtomicConstraint [leftOperand; operator ∈ {isA,isAnyOf,isAllOf,isNoneOf}; rightOperand \| rightOperandRef; targetNorm?]` | ⟦AtomicConstraint⟧ §288 | `Atomic(left, op, right, targetNorm?)` | `RESOLVE left; PUSH right; ⟨IIsA\|IIsAnyOf\|IIsAllOf\|IIsNoneOf⟩` |
| `rl2:LogicalConstraint [and (…operands)]` | ⟦And⟧ §301 | `And(seq<Cond>)` | lower each; fold `IAnd` |
| `rl2:LogicalConstraint [or (…operands)]` | ⟦Or⟧ §302 | `Or(seq<Cond>)` | lower each; fold `IOr` |
| `rl2:LogicalConstraint [xone (…operands)]` | ⟦Xone⟧ §304 | `Xone(seq<Cond>)` | lower each; `IXone(n)` — **not** a chained binary XOR (see §5) |
| `rl2:LogicalConstraint [not operand]` | ⟦Not⟧ §303 | `Not(Cond)` | lower; `INot` |
| `rl2:EventConstraint [expectsEvent]` | ⟦EventConstraint⟧ §311 | `EventCond(ev)` | **AST-layer** (queries Σ.Events, not pure env) — no bytecode |

`AtomicConstraint` and each leaf clause are the **base cases**; `LogicalConstraint` and
conditional/nested clauses are the **inductive cases**. `EventConstraint` and any
`targetNorm`-parameterized state query read Σ, so they are evaluated in the AST tree-walk via
the subsumption-aware `performed(...)` helper (§320), never inside the pure condition VM.

**`rightOperandRef` (I1/SEM-4).** When an `AtomicConstraint` carries `rightOperandRef` (a
`RuntimeReference`, e.g. `currentAgent` — RL2_Semantics.md §Conditions) rather than a literal
`rightOperand`, the right side is dynamic and must be read from `Env` like the left side.
`IResolve` (§6) is not left-side-only: the lowering emits `RESOLVE left; RESOLVE right; ⟨op⟩`
in that case, in place of `RESOLVE left; PUSH right; ⟨op⟩`. Which form applies is a static,
compile-time choice (`rightOperand` vs `rightOperandRef` are mutually exclusive per
`AtomicConstraintShape`), so it adds no branching to the VM itself — only to the compiler's
lowering rule.

### 3.3 Reading the table backwards

Right-to-left, the table is the **IR → source inverse map**: every AST node and every emitted
bytecode carries the identity of the RDF construct it came from. Error reporting ("policy X,
clause Y") is therefore a table lookup, not a separate mechanism — this answers
research/design-forth-ir.md Open Question 3 (mapping VM errors back to source) for free.

---

## 4. Outer AST (the normalized policy)

The outer IR is structured data, mirroring the ontology's `rl2:Clause` split. It is **not**
bytecode: `resolveDecision` and clause matching pattern-match directly on these datatypes.

Compilation targets a `CompiledUniverse`, not a single compiled policy, mirroring
RL2_Semantics.md's `Out`/`Eval`, which already take a `PolicyUniverse U` (I1/SEM-4 — a request
can match clauses drawn from several policies at once, so `targetIndex` and
`subsumptionIndex` must span the whole compiled universe, not one policy's clauses):

```dafny
datatype CompiledUniverse = CompiledUniverse(
  policies         : seq<CompiledPolicy>,
  targetIndex      : map<Target, set<ClauseRef>>,   // Target → clause refs, ACROSS policies (SEM-5 consumes)
  subsumptionIndex : map<Action, set<Action>> )      // includedIn* downward closure — STATIC (§8), one
                                                       // hierarchy per generation (SEM-6), so it is shared
                                                       // by every policy in the universe, not per-policy

datatype ClauseRef = ClauseRef(policy: nat, clause: nat)  // indices into policies[policy].clauses[clause]

datatype CompiledPolicy = CompiledPolicy(
  policyId : IRI,                                  // source rl2:Policy — provenance (mirrors S7's
                                                     // per-atom provenance requirement on the Out side)
  clauses  : seq<Clause>,
  kind     : PolicyKind )                           // Offer | Agreement | Set | Privacy | Assertion

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
- **No `conflictStrategy` field anywhere in compiled data (I1/SEM-4).** S7 established that
  conflict-resolution strategy is evaluator configuration, not something a policy or the
  universe authors — so it is not compiled at all. It is supplied directly to `evalIR` as a
  parameter (§7), exactly mirroring `Eval`'s `strategy` parameter in RL2_Semantics.md
  §Big-Step Semantics.
- **`policyId` restores per-clause provenance.** `Out`'s atoms carry `(atom-kind, n, P)` — the
  producing policy `P` (RL2_Semantics.md S7) — so the compiled form must be able to answer
  "which policy did this clause come from" too; `ClauseRef.policy` indexes into
  `CompiledUniverse.policies`, and `CompiledPolicy.policyId` is that policy's source IRI.

---

## 5. Inner IR (condition bytecode)

Conditions compile to a small stack machine — the verifiable subset of Forth from
research/design-forth-ir.md, **scoped to pure three-valued evaluation**. The `EMIT-PERMIT/FORBID/
OBLIGATION` opcodes of the original sketch are **removed**: emission is derivation (§7), a set
operation over the envelope, not a stack effect. What remains is ~30 opcodes with no side
effects and no external writes.

The VM result carrier realizes the semantics' **Truth = True | False | Unknown** algebra (S2,
RL2_Semantics.md §Result and Truth Algebra): `VBottom` **is** `Unknown` — the propagated error
value, not a silent false. A resolve that is Missing/Invalid/Conflict pushes `VBottom`, and the
logic opcodes are **Kleene** (see below), so a comparison or connective yields `VBottom`
whenever the outcome genuinely cannot be determined. The tree-walk that consumes a condition
result (§7 derivation) treats `VBottom` as `Indeterminate` at the norm level — never as inactive.

```dafny
datatype Value =
    VBool(bool)
  | VInt(int)
  | VDecimal(unscaled: int, scale: nat)              // exact fixed-point (no float rounding)
  | VString(string)
  | VLangString(string, lang: string)                // rdf:langString
  | VDateTime(epochSeconds: int, tzOffsetMinutes: int) // xsd:dateTimeStamp — tz offset MANDATORY (S4)
  | VDuration(seconds: int)                          // xsd:duration, normalized to seconds
  | VURI(string)
  | VSet(seq<Value>)                                 // collections — operand of isAnyOf/isAllOf/isNoneOf
  | VBottom                                          // ⊥ = Unknown (propagated error; S2)

datatype Instr =
  // stack
  | IDup | IDrop | ISwap | IOver | IRot
  // logic
  | IAnd | IOr | INot
  | IXone(n: nat)                                    // N-ary "exactly one true" (see below — replaces IXor)
  // compare (mono + typed)
  | IEq | INeq | ILt | ILte | IGt | IGte
  | ISEq | IDateTimeLte | IURIEq
  | IIsA | IIsAnyOf | IIsAllOf | IIsNoneOf            // rl2:isA / isAnyOf / isAllOf / isNoneOf (I1/SEM-4)
  // literals
  | ILitBool(bool) | ILitInt(int) | ILitDecimal(unscaled: int, scale: nat)
  | ILitString(string) | ILitLangString(string, lang: string)
  | ILitDateTime(epochSeconds: int, tzOffsetMinutes: int) | ILitDuration(seconds: int)
  | ILitURI(string) | ILitSet(seq<Value>)
  // control
  | IIf(thn: seq<Instr>, els: seq<Instr>)
  // the single external-read opcode (§6) — usable for either operand position (§3.2)
  | IResolve(path: string)

datatype VM = VM(stack: seq<Value>, env: Env, fuel: nat)     // no output channel — pure boolean result
```

**`IXone(n)` replaces `IXor` (I1/SEM-4).** The old logic group folded a chain of binary
`IXor`, which computes *parity* (an odd number of true operands) once folded across three or
more operands — not "exactly one true," which is what `Xone` means (§3.2's row already
described an "`XONE` reducer" the `Instr` type never actually backed). `IXone(n)` pops `n`
operands and reduces them directly per the Kleene rule already stated in §5's invariants
(`Xone` is `VBottom` if any operand is `VBottom`) — a type-level fix, not a re-derivation of
the semantic rule itself, which is unchanged.

**`VDateTime` replaces `VDate` (I1/SEM-4, consistent with S4).** `VDate(int)` was an untyped
epoch value with no timezone, which is inconsistent with S4's `xsd:dateTimeStamp` decision
(WP-4) mandating a **mandatory** tz offset for `currentDateTime` comparisons. `VDateTime`
carries `tzOffsetMinutes` explicitly so a comparison can never silently assume UTC.
`IDateLte` is renamed `IDateTimeLte` to match.

**`VSet` is the operand type for `isAnyOf`/`isAllOf`/`isNoneOf`.** These operators are already
ontology-defined (`rl2:ComparisonOperator` individuals in `rl2.ttl`: `isA` = "Type/class
membership check," `isAnyOf` = "Value is any of a specified set," `isAllOf` = "Value satisfies
all of a specified set," `isNoneOf` = "Value is none of a specified set") — the ontology
already permits authoring these conditions; this IR previously had no opcode to lower them to,
which was the actual gap. `IIsA` reuses the same static subsumption-index mechanism already
generalized in §8 ("the same index mechanism serves any subsumable dimension") for
hierarchical `leftOperand` domains, falling back to equality for flat ones; `IIsAnyOf` tests
`left ∩ rightSet ≠ ∅` (or scalar `left ∈ rightSet`); `IIsAllOf` tests `rightSet ⊆ left`'s
value-set; `IIsNoneOf` tests `left ∩ rightSet = ∅`. All four are Kleene: `VBottom` on either
side yields `VBottom`, consistent with §5's invariants.

The intended invariants (proof obligations for IMPL, not proven here):

- **Termination:** `fuel` strictly decreases each `Step`; conditions are finite acyclic trees,
  so a `fuel` bound linear in tree size suffices.
- **Determinism:** `Step` is a function, not a relation.
- **Type/memory safety:** the stack never underflows on well-typed bytecode; `Xone` and typed
  comparators reject ill-typed operands to `VBottom` (= `Unknown`) rather than getting stuck.
- **Kleene logic (S2):** `IAnd`/`IOr`/`INot`/`Xone` implement strong three-valued logic —
  `VBool(false) IAnd VBottom = VBool(false)`, `VBool(true) IOr VBottom = VBool(true)`,
  `INot VBottom = VBottom`, and `Xone` is `VBottom` if any operand is `VBottom`. Short-circuit
  is therefore fixed by the algebra, not by evaluation order, so which errors are observable is
  determined, not incidental.

The single exported meaning is `EvalBytecode(prog, env) : Value` returning a `VBool` (or
`VBottom` = `Unknown`). Its correctness statement is §9b.

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

- **`context: ContextView` is populated from `Ctx`.** `Env` is built by
  `mkEnv(R, Σ, Ctx) : Env` (RL2_Semantics.md §839), matching the denotational `mkEnv` exactly
  — `evalIR` threads `Ctx` through the same way it threads `R` and `Σ` (§7.1; I1/SEM-4 fixes a
  prior mismatch where `evalIR`'s signature and its internal `mkEnv` call omitted `Ctx` even
  though §9's equivalence obligation already stated it as a top-level parameter).

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
evalIR : (CompiledUniverse, Request, Σ, Ctx, Strategy) → (Decision, DutySet, seq<Effect>)   // PURE, total
```

`CompiledUniverse` (§4) replaces the earlier single-policy `CompiledPolicy` as `evalIR`'s
input (I1/SEM-4 — a request evaluates against the whole compiled universe, not one policy).
`Ctx` and `Strategy` are explicit parameters, matching the denotational `Eval`'s signature
(RL2_Semantics.md §Big-Step Semantics) exactly: `Ctx` was previously dropped between §9's
equivalence obligation and this signature; `Strategy` was previously smuggled in as a
`CompiledPolicy` field, which S7 already rejected as policy vocabulary.

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
                       content: PromiseContent, source: Clause)  // CONS-3 — audit trail to originating Promise
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
evalIR(CU, R, Σ, Ctx, strategy) =
    let env      = mkEnv(R, Σ, Ctx)
    -- ① DERIVATION (monotone): collect the pre-resolution envelope, across ALL policies
    let envelope = ⋃ { derive(c, env) | P ∈ CU.policies, c ∈ P.clauses, matches(c, R) }     -- Out, §1222
    -- ② effect collection (still monotone): duty transitions, crystallization on acceptance, …
    let effects  = deriveEffects(envelope, CU, Σ, env)
    -- ③ RESOLUTION (non-monotone): strategy + priority over the collected envelope
    let decision = resolveDecision(envelope, applyEffects(Σ, effects), strategy)
    in (decision, duties(envelope), effects)
```

`derive` is a monotone per-clause fold; `resolveDecision` is where conflict/priority act, and
only there. Duties and crystallization pass through derivation into the output; resolution
decides only the verdict. Because derivation is monotone and order-independent, the outer
normalization theorem (§9a) inherits order-independence for free.

**`deriveEffects` (I4).** Each effect kind is produced by a function keyed on the entity it
transitions, not on the clause that happened to mention it — this is what makes effect
conflicts unrepresentable rather than something `applyEffects` must arbitrate:

```dafny
deriveEffects(envelope, CU, Σ, env) : seq<Effect> =
    dutyFx(envelope, Σ, env) ++ promiseFx(envelope) ++ remedialFx(envelope)
      ++ caseFx(envelope) ++ powerFx(envelope) ++ historyFx(envelope)
    -- each sub-sequence canonically ordered by ClauseRef (policy index, then clause index) —
    -- derivation's Decision is order-independent (§7.1 above) regardless, but AppendHistory's
    -- literal order feeds the replay/audit log (WP-3 witness events), so evalIR fixes one

dutyFx(envelope, Σ, env) =
    [ e | d ∈ duties(envelope), e = transitionEffect(d, Σ, env), e ≠ None ]

transitionEffect(d, Σ, env) : Effect? =
    case Σ.ObligationState(d) of
        Pending → if ⟦d.condition⟧(env) = True then Some(TransitionDuty(d, Pending, Active)) else None
        Active  → if performed(d.subject, d.action, d.object, Σ)
                  then Some(TransitionDuty(d, Active, Fulfilled))
                  else if timeout(d.condition, Σ) then Some(TransitionDuty(d, Active, Violated))
                  else None
        _       → None   -- Fulfilled/Violated terminal (D-FULFILL/D-VIOLATE, RL2_Semantics.md §Duty
                          -- Activation/Fulfillment/Violation)
```

`transitionEffect` is `updateOneDuty`'s case dispatch (RL2_Semantics.md `updateDutyStates`,
§1259) restated to *return* an effect instead of mutating Σ in place. It is a total function of
`(Σ.ObligationState(d), env)` alone — **not** of which clause matched — and `duties(envelope)`
is a set, so at most one `TransitionDuty` effect is ever produced per duty per round. A
same-round `Fulfilled`-vs-`Violated` conflict on one duty (§7.3's original framing) is
therefore not a case `applyEffects` resolves at commit time; it is precluded at derivation time
by construction, the same way S7 eliminated per-clause `conflictStrategy` by making resolution
a single evaluator-supplied parameter rather than something clauses vote on. `promiseFx`,
`remedialFx`, `caseFx` similarly key each effect by its originating clause (`source: Clause`,
§7.2) — distinct clauses can never collide because they produce distinct `Effect` values, so
folding them into Σ is append, not arbitration. `powerFx` (`ExercisePower`) is the one
remaining open case: SEM-8's state-update verification for `ExercisePower` is explicitly
deferred (see issues.md), so this document does not claim its conflict-freedom — only that the
other five kinds are conflict-free by the argument above.

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

**`CrystallizePromise` is not the whole of Offer→Agreement (PROM-7).** This effect is
*runtime* bookkeeping inside an already-materialized Agreement's evaluation. The document-level
step that turns an Offer into that Agreement — minting fresh clause IRIs and rewriting
`targetNorm` references from Offer-stage Promises to their crystallized Duties — is
`materialize` (RL2_Semantics.md §Materialization), which runs once, before compilation. It
cannot be an `Effect`/`applyEffects` case: `CompiledUniverse` is immutable during `evalIR`, and
`applyEffects` only ever produces a new Σ, never a rewritten policy AST — exactly what
`targetNorm` rewriting requires.

### 7.3 Effect coherence

`applyEffects` folds `deriveEffects`'s output into Σ. Given §7.1's `transitionEffect`
construction, the fold has no conflicts left to arbitrate: each `TransitionDuty` is keyed by a
distinct duty, each `CrystallizePromise`/`GenerateRemedialDuty`/`CreateCase` by a distinct
source clause, so `applyEffects` is a commutative, idempotent merge into Σ, well-posed by
snapshot-consistency (§6 — all effects derive from the same Σ, so the update set is fixed).
`applyEffects`'s remaining proof obligation (§9c) is therefore reproduction, not arbitration:
that this merge yields exactly the Σ' the denotational `updateDutyStates`/operational rules
compute — not that it picks a winner among effects that were never actually in tension.

**Commit-time validation (I4).** `applyEffects` is pure and total over a fixed `(Σ, fx)`; the
part of "committing a transition" that is *not* pure — persistence, network delivery, retries —
sits entirely in the deployment shell (RL2_Semantics.md §Versioned snapshot and commit) and is
out of this document's proof surface. What the kernel *does* obligate the shell to do is
re-derive, not merely re-apply: a commit against snapshot version `v` is valid only if the
`fx` being applied is the `fx` that `evalIR` computes fresh against `Snapshot_v`, not an `fx`
carried over from a possibly-stale prior evaluation:

```
validateCommit(Snapshot_v, R, Ctx, strategy, fx_claimed) : bool =
    let (_, _, fx_expected) = evalIR(compile(U), R, Snapshot_v.Σ, Ctx, strategy)
    in fx_claimed = fx_expected
```

This closes the gap the CAS check alone does not: version-matching guarantees no *other*
committed transition slipped in between read and write, but does not by itself guarantee the
shell is committing the effect set the pure kernel actually computed for that version (e.g. a
retried request whose `fx` was memoized against an earlier, since-superseded evaluation attempt
could still carry a matching `v` by coincidence). Recomputing `fx_expected` at commit time —
rather than trusting a caller-supplied `fx` — makes `commit` idempotent under retry for free:
a retried commit at unchanged `v` recomputes the same `fx` (§9's determinism) and is a no-op;
a retry after `v` has moved fails the CAS check and forces re-evaluation against the new
snapshot, exactly as already specified.

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
For all policy universes U, requests R, states Σ, contexts Ctx, strategies strategy:

  Eval(U, R, Σ, Ctx, strategy) = (dec, Σ', duties)
    ≡
  let (dec', duties', fx) = evalIR(compile(U), R, Σ, Ctx, strategy)
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
`EvalBytecode(lower(c), env) = ⟦c⟧(env)` under the `Truth`↔`Value` correspondence
`True↔VBool(true)`, `False↔VBool(false)`, `Unknown↔VBottom` (RL2_Semantics.md §Conditions and
§Result and Truth Algebra), together with the VM invariants of §5 (termination, determinism,
type/memory safety). Base case: `Atomic` (including the `Missing/Invalid/Conflict → Unknown`
lifting). Inductive cases: `And`/`Or`/`Xone`/`Not` by the Kleene fold in §3.2 — the lemma
therefore also pins the short-circuit behavior. (`EventConstraint` is discharged in 9a, not
here — it is AST-layer and total two-valued.)

**(9c) Effect-soundness lemma.** `applyEffects(Σ, fx)` reproduces the `Σ'` that `Eval` computes
via `updateDutyStates` (§1259) and the operational rules (§Duty Activation/Fulfillment/
Violation, §Crystallization, §Remedial Generation). Three sub-lemmas:

- **Made-vs-demanded orientation:** for either promise orientation, `CrystallizePromise`
  yields a `Duty` bound to the promisor and a correlative `Claim` bound to the promisee
  (§7.2).
- **Effect coherence (I4):** `deriveEffects` keys `TransitionDuty` by duty (not by clause), so
  distinct duties/sources never produce colliding effects within one round — `applyEffects` is
  a commutative, idempotent merge, not an arbitration (§7.3). This is a determinism argument,
  not a runtime resolution strategy, mirroring how S7 removed per-clause `conflictStrategy`
  rather than adjudicating between clauses that declared different ones.
- **Commit validity (I4):** for a shell built on the versioned-snapshot/CAS protocol
  (RL2_Semantics.md §Versioned snapshot and commit), a committed transition at version `v` is
  sound only if its applied `fx` equals `evalIR`'s fresh recomputation against `Snapshot_v`
  (§7.3's `validateCommit`) — persistence, network, and retries stay outside this proof; only
  the equality obligation on `fx` is in scope.

The split localizes the hard verification to 9b (the pure VM, where evm-dafny is direct
precedent) and keeps 9a/9c as structural refinements close to the denotational spec.

---

## 10. Compiler Trust Model

The **kernel** (`evalIR`, the VM, `applyEffects`) is the verified trusted base. The
**compiler** (`Turtle → AST`, `lower : Condition → bytecode`, index construction) starts
**tested, not verified**:

- **Differential testing** against the denotational reference on the 52-use-case corpus *and*
  on generated policies (the canonical-form thesis makes machine-generated policies the
  primary case, so they must be in the test set). This is the Cedar-spec model — reference
  semantics kept separate from the executable, reconciled by differential testing
  (`research/verification-toolchain-comparison.md` §Lean/Cedar).
- **CANON shrinks the trusted surface.** The canonical-form invariant is scoped to the
  **AST the projection produces**, not to raw RDF (C5, RL2_Architecture.md §Canonical Form):
  the RDF authoring layer admits exactly one authored shape per proposition (SHACL-enforced),
  and the projection `π : RDF → AST` normalizes entailment, defaults, blank nodes, operand
  ordering/dedup, annotations, and unsupported-extension rejection. Because that authored input
  is already SHACL-canonical, `π` is a **near-mechanical normalizer** — small and total — rather
  than an optimizing compiler, and it is `π` (not raw graph structure) that makes syntax → AST a
  *function* (one canonical AST per proposition), the precondition that makes §9's base cases
  well-formed. Semantic equivalence is decided over the AST, never by raw-graph isomorphism.
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

- **SEM-5 (target matching).** Consumes `CompiledUniverse.targetIndex`. This document fixes the
  index *shape* (`map<Target, set<ClauseRef>>`); SEM-5 owns the *algorithm* and precedence
  (direct, classification, sub-asset, subsumption) and closed-world defaults.
- **SEM-1 / PROM-5.** `PromisedState` maintenance-duty ObligationState wiring (SEM-1) and
  `PromisedDuty` suretyship remedy (PROM-5) are the two behavioral wirings the crystallization
  *targets* (§7.2) hand off; the IR is well-defined regardless of how they resolve.
- **PROM-1 residue.** Align RL2_Semantics.md abstract syntax `clauses : Norm* → Clause*` (§3.1
  note) — a one-line follow-up.
- **IMPL (Band 4), out of scope here:** bytecode serialization format, dictionary/word
  indexing, error-report surfacing, and step/debug tooling (research/design-forth-ir.md §Open
  Questions). The de-risking spike (a handful of opcodes Dafny→Go) precedes committing to the
  full VM.

---

## References

- **RL2_Semantics.md** — denotational and operational semantics this IR refines (§Conditions,
  §Norm Denotations, §Crystallization, §Normative Derivation, §Big-Step Semantics).
- **RL2_Architecture.md** — evaluation pipeline and layer separation.
- **research/design-forth-ir.md** — stack-VM design rationale (refined here: VM scoped to conditions;
  `EMIT-*` removed).
- **research/verification-toolchain-comparison.md** — Dafny→Go decision; evm-dafny and
  Cedar-spec precedents.
- Makinson & van der Torre, *Input/Output Logics* — the derive-then-resolve foundation.
